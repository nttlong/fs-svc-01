import pathlib
import typing

import elasticsearch

import cy_docs
import cy_kit
import cy_es
import cyx.common
from cy_xdoc.services.text_procesors import TextProcessService
from cy_xdoc.services.file_content_extractors import FileContentExtractorService
from cyx.rdr_segmenter.segmenter_services import VnSegmenterService
import cyx.vn_predictor


class SearchEngine:
    def __init__(self,
                 text_process_service: TextProcessService = cy_kit.singleton(TextProcessService),
                 file_content_extractor_service: FileContentExtractorService = cy_kit.singleton(
                     FileContentExtractorService
                 ),
                 vn=cy_kit.singleton(VnSegmenterService),
                 vn_predictor=cy_kit.singleton(cyx.vn_predictor.VnPredictor)):
        self.config = cyx.common.config
        self.client = elasticsearch.Elasticsearch(
            cyx.common.config.elastic_search.server
        )
        self.prefix_index = cyx.common.config.elastic_search.prefix_index
        self.text_process_service = text_process_service
        self.file_content_extractor_service = file_content_extractor_service
        self.similarity_settings_cache = {}
        self.vn = vn
        self.vn_predictor = vn_predictor
        self.empty_privilege_value = 0

    def get_content_field_name(self):
        return self.config.elastic_search.field_content

    def delete_index(self, app_name):
        self.client.indices.delete(index=self.get_index(app_name))

    def get_index(self, app_name):
        if app_name == "admin":
            app_name = self.config.admin_db_name
        index_name = f"{self.prefix_index}_{app_name}"
        if self.similarity_settings_cache.get(app_name) is None:
            """
            Set ignore doc len when calculate search score 
            """
            cy_es.cy_es_x.similarity_settings(
                client=self.client,
                index=index_name,
                field_name=self.get_content_field_name(),
                algorithm_type="BM25", b_value=0, k1_value=10)
            self.similarity_settings_cache[app_name] = True
        return index_name

    def delete_doc(self, app_name, id: str):
        return cy_es.delete_doc(
            client=self.client,
            index=self.get_index(app_name),
            id=id
        )

    def mark_delete(self, app_name, id, mark_delete_value):
        ret = cy_es.update_doc_by_id(
            client=self.client,
            id=id,
            index=self.get_index(app_name),
            data=(
                cy_es.buiders.mark_delete << mark_delete_value,
            )
        )
        return ret

    def full_text_search(self,
                         app_name,
                         content,
                         page_size: int,
                         page_index: int,
                         highlight: bool,
                         privileges: dict,
                         sort: typing.List[str] = ["data_item.RegisterOn:desc"],
                         logic_filter=None):

        content = content or ""
        original_content = content

        privileges = self.fix_privilges_contains_error(privileges)
        if isinstance(privileges, dict):
            privileges = cy_es.text_lower(privileges)
        content = self.vn_predictor.get_text(content)
        content = original_content + " " + content
        content_boots = self.vn.parse_word_segment(content=content, boot=[3])

        search_expr = (cy_es.buiders.mark_delete == False) | (cy_es.buiders.mark_delete == None)
        if privileges is not None and privileges != {}:
            search_expr = search_expr & cy_es.create_filter_from_dict(
                filter=
                cy_es.nested(
                    field_name="privileges",
                    filter=privileges
                ),
                suggest_handler=self.vn_predictor.get_text
            )
        if content is not None and content != "" and content.lstrip().rstrip().strip() != "":
            content_search_match_phrase = cy_es.match_phrase(
                field=getattr(cy_es.buiders, "content"),
                content=content,
                boost=0.01,
                # slop=1,
                # analyzer="stop"

            )

            qr = cy_es.query_string(
                fields=[getattr(cy_es.buiders, f"{self.get_content_field_name()}_seg")],
                query=content_boots
                # slop=1

            )

            search_expr = search_expr & (content_search_match_phrase | qr)
            # search_expr.set_minimum_should_match(1)
        skip = page_index
        highlight_expr = None
        if highlight:
            """
            "highlight": {
    "require_field_match": "false",
    "fields": {
      "title": {},
      "email": {}
    }
  }
            """
            highlight_expr = [
                getattr(cy_es.buiders, f"content"),
                getattr(cy_es.buiders, f"{self.get_content_field_name()}_seg")
            ]
        if logic_filter is not None and isinstance(logic_filter, dict):
            _logic_filter = cy_es.create_filter_from_dict(
                logic_filter,
                suggest_handler=self.vn_predictor.get_text
            )
            if _logic_filter:
                search_expr = search_expr & _logic_filter
        highlight_expr = highlight_expr or []
        highlight_expr += search_expr.get_highlight_fields()
        print(f"------------{skip}--{page_size}-------------------------")
        ret = cy_es.search(
            client=self.client,
            limit=page_size,
            excludes=[
                cy_es.buiders.content,
                cy_es.buiders.meta_info,
                cy_es.buiders.vn_on_accent_content],
            index=self.get_index(app_name),
            highlight=highlight_expr,
            filter=search_expr,
            skip=skip,
            sort=sort

        )
        return ret

    def get_doc(self, app_name: str, id: str, doc_type: str = "_doc"):
        return cy_es.get_doc(client=self.client, id=id, doc_type=doc_type, index=self.get_index(app_name))

    def copy(self, app_name: str, from_id: str, to_id: str, attach_data, run_in_thread: bool = True):
        @cy_kit.thread_makeup()
        def copy_elastics_search(app_name: str, from_id: str, to_id: str, attach_data):
            es_doc = self.get_doc(id=from_id, app_name=app_name)
            if es_doc:
                es_doc.source.upload_id = to_id
                es_doc.source.data_item = attach_data
                es_doc.source["mark_delete"] = False
                ret = self.create_doc(app_name=app_name, id=to_id, body=es_doc.source)

        if run_in_thread:
            copy_elastics_search(app_name, from_id, to_id, attach_data).start()
        else:
            copy_elastics_search(app_name, from_id, to_id, attach_data).start().join()

    def create_doc(self, app_name, id: str, body):
        return cy_es.create_doc(
            client=self.client,
            index=self.get_index(app_name),
            id=id,
            body=body
        )

    def make_index_content(self, app_name: str,
                           upload_id: str,
                           data_item: dict,
                           privileges: dict,
                           path_to_file_content: str = None,
                           content: str = None,
                           meta_info=None,
                           mark_delete=False,
                           meta=None):
        file_name = None
        if path_to_file_content is not None:
            content, meta_info = self.file_content_extractor_service.get_text(path_to_file_content)
            file_name = pathlib.Path(path_to_file_content).name
        elif content is None:
            content, meta_info = None, None
            file_name = None
        index_name = self.get_index(app_name)

        vn_non_accent_content = self.text_process_service.vn_clear_accent_mark(content)
        body_dict = dict(
            app_name=app_name,
            upload_id=upload_id,
            file_name=file_name,
            mark_delete=mark_delete,
            content=content,
            vn_non_accent_content=vn_non_accent_content,
            meta_info=cy_es.convert_to_vn_predict_seg(
                meta_info,
                segment_handler=self.vn.parse_word_segment,
                handler=self.vn_predictor.get_text,
                clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
            ),
            data_item=cy_es.convert_to_vn_predict_seg(
                data_item,
                segment_handler=self.vn.parse_word_segment,
                handler=self.vn_predictor.get_text,
                clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
            ),
            privileges=privileges,
            meta_data=meta
        )

        # body_dict[f"{self.get_content_field_name()}_lower"] = self.vn.parse_word_segment(content=content.lower())
        cy_es.create_doc(
            client=self.client,
            index=index_name,
            id=upload_id,
            body=body_dict
        )

        del content
        del meta_info
        del vn_non_accent_content

    def create_or_update_privileges(self, app_name, upload_id, data_item: dict, privileges):
        is_exist = self.is_exist(app_name, id=upload_id)

        if is_exist:
            return cy_es.update_doc_by_id(
                client=self.client,
                index=self.get_index(app_name),
                id=upload_id,
                data=(
                        cy_es.buiders.privileges << privileges
                )
            )
        else:
            if data_item:
                self.make_index_content(
                    app_name=app_name,
                    privileges=privileges,
                    upload_id=upload_id,
                    data_item=cy_es.convert_to_vn_predict_seg(
                        data_item,
                        segment_handler=self.vn.parse_word_segment,
                        handler=self.vn_predictor.get_text,
                        clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
                    )
                )
            else:
                self.update_doc_by_id(
                    client=self.client,
                    index=self.get_index(app_name),
                    id=upload_id,
                    data=(
                            cy_es.buiders.privileges << privileges
                    )
                )

    def is_exist(self, app_name: str, id: str) -> bool:
        return cy_es.is_exist(
            client=self.client,
            index=self.get_index(app_name),
            id=id
        )

    def update_content_value_only(self, app_name: str, id: str, content: str, content_lower: str,
                                  content_field="content"):
        is_exist = self.is_exist(app_name, id=id)
        if is_exist:
            return cy_es.update_doc_by_id(
                client=self.client,
                index=self.get_index(app_name),
                id=id,
                data=(
                    getattr(cy_es.buiders, content_field) << content,
                    getattr(cy_es.buiders, f"{content_field}_lower") << content_lower,
                    getattr(cy_es.buiders, f"{content_field}_seg") << content,

                )
            )

    def update_content(self, app_name: str, id: str, content: str, data_item=None, meta: dict = None):

        original_content = content or ""
        content = self.vn_predictor.get_text(content)
        if data_item is None:
            return
        is_exist = self.is_exist(app_name, id=id)
        if isinstance(data_item, cy_docs.DocumentObject):
            json_data_item = data_item.to_json_convertable()
        elif isinstance(data_item, dict):
            json_data_item = cy_docs.to_json_convertable(data_item, predict_content_handler=self.vn_predictor.get_text)
        if is_exist:
            es_doc = self.get_doc(
                app_name=app_name,
                id=id

            )
            old_content = self.vn_predictor.get_text(es_doc.source.content or "")
            content = content + "\n" + old_content
            content = original_content + "\n" + content
            vn_non_accent_content = self.text_process_service.vn_clear_accent_mark(content)
            _Privileges = None
            if hasattr(data_item, "Privileges"):
                _Privileges = data_item.Privileges
            elif isinstance(data_item, dict):
                _Privileges = data_item.get("Privileges")
            seg_content = self.vn.parse_word_segment(
                content=content
            )
            return cy_es.update_doc_by_id(
                client=self.client,
                index=self.get_index(app_name),
                id=id,
                data=(
                    cy_es.buiders.privileges << _Privileges,
                    getattr(cy_es.buiders, f"{self.get_content_field_name()}_bm25_seg") << seg_content,
                    getattr(cy_es.buiders, f"{self.get_content_field_name()}_seg") << seg_content,
                    getattr(cy_es.buiders, f"{self.get_content_field_name()}_lower") << self.vn.parse_word_segment(
                        content=content.lower()),
                    cy_es.buiders.vn_non_accent_content << vn_non_accent_content,
                    cy_es.buiders.content << content,
                    cy_es.buiders.data_item << cy_es.convert_to_vn_predict_seg(
                        json_data_item,
                        handler=self.vn_predictor.get_text,
                        segment_handler=self.vn.parse_word_segment,
                        clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
                    ),
                    cy_es.buiders.meta_data << meta

                )
            )
        else:
            content = original_content + "\n" + content
            _Privileges = None
            if hasattr(data_item, "Privileges"):
                _Privileges = data_item.Privileges
            elif isinstance(data_item, dict):
                _Privileges = data_item.get("Privileges")
            _mark_delete = False
            if hasattr(data_item, "mark_delete"):
                _mark_delete = data_item.mark_delete
            self.make_index_content(
                app_name=app_name,
                privileges=_Privileges,
                upload_id=id,
                data_item=cy_es.convert_to_vn_predict_seg(
                    json_data_item,
                    handler=self.vn_predictor.get_text,
                    segment_handler=self.vn.parse_word_segment,
                    clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
                ),
                content=content,
                meta_info=None,
                meta=meta,
                mark_delete=_mark_delete,

            )

    def update_data_field(self, app_name, id, field_path, field_value):
        cy_es.update_data_fields(
            index=self.get_index(app_name),
            id=id,
            field_path=field_path,
            field_value=field_value,
            client=self.client

        )
        if cy_es.is_content_text(field_value):
            vn_predictor = self.vn_predictor.get_text(field_value)
            vn_seg = self.vn.parse_word_segment(vn_predictor)
            if vn_predictor != field_value:
                cy_es.update_data_fields(
                    index=self.get_index(app_name),
                    id=id,
                    field_path=f"{field_path}_vn_predict",
                    field_value=vn_predictor,
                    client=self.client

                )
            cy_es.update_data_fields(
                index=self.get_index(app_name),
                id=id,
                field_path=f"{field_path}_bm25_seg",
                field_value=vn_seg,
                client=self.client

            )

    def update_by_conditional(self, app_name, conditional, data):
        if isinstance(conditional, dict):
            conditional = cy_es.create_filter_from_dict(conditional)
        return cy_es.update_by_conditional(
            client=self.client,
            data_update=cy_es.convert_to_vn_predict_seg(
                data,
                handler=self.vn_predictor.get_text,
                segment_handler=self.vn.parse_word_segment,
                clear_accent_mark_handler=self.text_process_service.vn_clear_accent_mark
            ),
            index=self.get_index(app_name),
            conditional=conditional
        )

    def delete_by_conditional(self, app_name, conditional):
        if isinstance(conditional, dict):
            conditional = cy_es.create_filter_from_dict(conditional)
        return cy_es.delete_by_conditional(
            client=self.client,
            index=self.get_index(app_name),
            conditional=conditional
        )



    def fix_privilges_list_error(self, privileges):
        """
        Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
        :param privileges:
        :return:
        """
        if isinstance(privileges, list):
            ret = []
            for x in privileges:
                if x.Values == "":
                    x.Values = self.empty_privilege_value
                ret += [x]
            return ret
        return privileges

    def fix_privilges_contains_error(self, data_privileges):
        """
                    Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
                    :param data_privileges:
                    :return:
                    """
        if isinstance(data_privileges, dict):
            for k, v in data_privileges.items():
                if k == "$contains" and v == ['']:
                    data_privileges[k] = [self.empty_privilege_value]
                else:
                    data_privileges[k] = self.fix_privilges_contains_error(v)
        elif isinstance(data_privileges, list):
            return [self.fix_privilges_contains_error(x) for x in data_privileges]
        else:
            return data_privileges
        return data_privileges
