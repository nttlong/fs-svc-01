import datetime
import pathlib
import sys

import cy_es

sys.path.append(
    pathlib.Path(__file__).parent.__str__()
)
from elasticsearch import Elasticsearch
import typing
import cy_es_x

DocumentFields = cy_es_x.DocumentFields
buiders = cy_es_x.docs


def create_index(client: Elasticsearch, index: str, body=None):
    return cy_es_x.create_index(
        index=index,
        body=body,
        client=client
    )


def get_map_struct(client: Elasticsearch, index: str) -> dict:
    return cy_es_x.get_map_struct(client, index)


def select(client: Elasticsearch, index: str, doc_type: str = "_doc", fields=[], filter=None, sort=None, skip=0,
           limit=1000):
    return cy_es_x.select(
        client=client,
        index=index,
        doc_type=doc_type,
        filter=filter,
        fields=fields,
        sort=sort,
        skip=skip,
        limit=limit
    )

__cache__settings_max_result_window___ = {}
def search(client: Elasticsearch,
           index: str,
           filter,
           excludes: typing.List[DocumentFields] = [],
           skip: int = 0,
           limit: int = 50,
           highlight: DocumentFields = None,
           sort=None,
           doc_type="_doc",
           logic_filter=None):
    global __cache__settings_max_result_window___
    if __cache__settings_max_result_window___.get(index)== None:

        client.indices.put_settings(index=index,
                                body={"index": {
                                    "max_result_window": 50000000
                                }})
        __cache__settings_max_result_window___[index] = True
    return cy_es_x.search(
        client=client,
        index=index,
        excludes=excludes,
        skip=skip,
        limit=limit,
        highlight=highlight,
        filter=filter,
        sort=sort,
        logic_filter=logic_filter
    )


def get_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:
    return cy_es_x.get_doc(client, index, id, doc_type=doc_type)


def delete_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc"):
    return cy_es_x.delete_doc(client=client, index=index, id=id, doc_type=doc_type)


__check_mapping__ = {}


def __create_mapping_from_dict__(body):
    ret = {}
    for k, v in body.items():
        if v:
            if isinstance(v, int):
                ret[k] = {
                    "type": "long",
                    # "ignore_malformed": True
                }
            elif isinstance(v, float):
                ret[k] = {
                    "type": "float",
                    # "ignore_malformed": True
                }
            elif isinstance(v, datetime.datetime):
                ret[k] = {
                    "type": "date",
                    "ignore_malformed": True
                }
            elif isinstance(v, bool):
                ret[k] = {
                    "type": "boolean",
                    # "ignore_malformed": True
                }
            elif isinstance(v, str):
                ret[k] = {
                    "type": "text",
                    # "ignore_malformed": True
                }
            else:
                ret[k] = {
                    "type": "nested",
                    "dynamic": True
                }
    return {
        "properties": ret
    }


def create_doc(client: Elasticsearch, index: str, id: str, body,
               doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:
    # global __check_mapping__
    # if __check_mapping__.get(index) is None:
    #
    #     map = get_mapping(client,index)
    #
    #     if map:
    #         __check_mapping__[index] = map
    #     else:
    #         map = __create_mapping_from_dict__(body)
    #         """
    #             {
    #                   "settings": {
    #                 "index.mapping.ignore_malformed": true
    #               },
    #               "mappings": {
    #                 "_doc": {
    #                   "properties": {
    #                     "number_one": {
    #                       "type": "byte"
    #                     },
    #                     "number_two": {
    #                       "type": "integer",
    #                       "ignore_malformed": false
    #                     }
    #                   }
    #                 }
    #               }
    #         """
    #         create_index(client=client, index=index, body={
    #             "settings":{
    #                 # "index.mapping.ignore_malformed": True
    #             },
    #             "mappings": map
    #         })
    #         put_mapping(
    #             client, index,map
    #         )
    #         __check_mapping__[index] = map

    return cy_es_x.create_doc(
        client=client,
        index=index,
        doc_type=doc_type,
        body=body,
        id=id
    )


match_phrase = cy_es_x.match_phrase
match = cy_es_x.match
query_string = cy_es_x.query_string


def wildcard(field: DocumentFields, content: str):
    """
    :return:
    """
    """
    "query": {
          "bool": {
              "should": [
                {
                  "wildcard": { "Field1": "*" + term + "*" }
                },
                {
                  "wildcard": { "Field2": "*" + term + "*" }
                }
              ],
              "minimum_should_match": 1
          }
      }
    """
    ret = DocumentFields()
    __match_phrase__ = {
        "wildcard": {
            field.__name__: "*" + content + "*"
        }
    }

    ret.__es_expr__ = {
        "match_phrase": __match_phrase__
    }

    # ret.__es_expr__["boost"] = boost
    return ret


def update_doc_by_id(client: Elasticsearch, index: str, id: str, data, doc_type: str = "_doc"):
    return cy_es_x.update_doc_by_id(
        client=client,
        index=index,
        id=id,
        data=data,
        doc_type=doc_type
    )


def nested(field_name: str, filter: dict):
    return cy_es_x.nested(prefix=field_name, filter=filter)


def create_filter_from_dict(filter: dict,suggest_handler= None):
    if filter == {}:
        return None
    return cy_es_x.create_filter_from_dict(filter,suggest_handler=suggest_handler)


def is_exist(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> bool:
    return cy_es_x.is_exist(
        client=client,
        index=index,
        id=id,
        doc_type=doc_type
    )


def get_docs(client: Elasticsearch, index: str, doc_type: str = "_doc"):
    return cy_es_x.get_docs(
        client=client,
        index=index,
        doc_type=doc_type
    )


def create_mapping(fields: typing.List[cy_es_x.DocumentFields]):
    return cy_es_x.create_mapping(fields)


def set_norms(field: cy_es.buiders, field_type: str, enable: bool):
    return cy_es_x.set_norms(
        field=field,
        enable=enable,
        field_type=field_type
    )


def create_mapping_meta(client: Elasticsearch, index: str, body):
    ret = cy_es_x.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index=index)


def put_mapping(client: Elasticsearch, index: str, body):
    ret = cy_es_x.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index=index)


def get_mapping(client, index):
    return cy_es_x.get_mapping(
        client, index
    )


def text_lower(filter):
    return cy_es_x.text_lower(
        filter
    )


def create_dict_from_key_path_value(field_path: str, value):
    """
    Ex: field_path="a.b.c" value:1 =>{a:{b:{c:1}}
    :param field_path:
    :param value:
    :return:
    """
    return cy_es_x.create_dict_from_key_path_value(field_path, value)


def update_data_fields(client: Elasticsearch, index: str, id: str, field_path=None, field_value=None, keys_values=None):
    return cy_es_x.update_data_fields(
        client=client,
        index=index,
        id=id,
        field_path=field_path,
        field_value=field_value,
        keys_values=keys_values
    )


def update_by_conditional(
        client: Elasticsearch, index: str,
        data_update,
        conditional,
        doc_type="_doc"
):
    return cy_es_x.update_by_conditional(
        client=client,
        data_update=data_update,
        conditional=conditional,
        doc_type=doc_type,
        index=index
    )


def delete_by_conditional(client, index, conditional, doc_type="_doc"):
    return cy_es_x.delete_by_conditional(
        client=client,
        conditional=conditional,
        index=index,
        doc_type=doc_type
    )


import uuid


def is_content_text(text):
    return cy_es_x.is_content_text(text)


def convert_to_vn_predict_seg(data, handler, segment_handler,clear_accent_mark_handler):
    ret = cy_es_x.convert_to_vn_predict_seg(data, handler, segment_handler,clear_accent_mark_handler)
    return ret

def natural_logic_parse(expr):
    ret = cy_es_x.natural_logic_parse(expr)
    if not isinstance(ret,dict):
        raise  Exception(f"'{expr}' is incorrect syntax")
    return ret