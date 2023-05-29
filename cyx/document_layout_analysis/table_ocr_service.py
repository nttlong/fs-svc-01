import sys
import pathlib

working_path = pathlib.Path(__file__).parent.parent.parent.__str__()
sys.path.append(working_path)

import os
import cy_kit
import deepdoctection as dd

from cyx.document_layout_analysis.doctr_service import DoctrService

from deepdoctection.dataflow.serialize import DataFromList
import deepdoctection
import numpy

import deepdoctection.extern.tessocr

from deepdoctection import ModelCatalog


class AnalysisInfo:
    result_image_path:str
    text:str
    table:str
    data:dict



class TableOCRService:
    def __init__(
            self,
            doc_tr_service=cy_kit.singleton(DoctrService)

    ):
        import cyx.document_layout_analysis.system
        self.doc_tr_service = doc_tr_service
        # self.doc_tr_service_model = doc_tr_service.get_model()
        self.sub_app_dir = cyx.document_layout_analysis.system.get_dataset_path()  # pathlib.Path(__file__).parent.parent.__str__()
        self._DD_ONE = f"{self.sub_app_dir}/conf_dd_one.yaml"
        if not os.path.isfile(self._DD_ONE):
            raise Exception(f"{self._DD_ONE} was not found")
        self._DETECTIONS = ["table", "ocr"]
        self.lay_out_model_file = "model_final_inf_only.pt"
        self.model = dd.ModelProfile(
            name=f"layout/{self.lay_out_model_file}",
            description="Detectron2 layout detection model trained on private datasets",
            config="dd/d2/layout/CASCADE_RCNN_R_50_FPN_GN.yaml",
            size=[1024 * 1024 * 10],
            tp_model=True,  # False original
            # hf_repo_id=environ.get("HF_REPO"),
            # hf_model_name="model_final_inf_only.pt",
            hf_config_file=["Base-RCNN-FPN.yaml", "CASCADE_RCNN_R_50_FPN_GN.yaml"],
            categories={"1": dd.LayoutType.text,
                        "2": dd.LayoutType.title,
                        "3": dd.LayoutType.list,
                        "4": dd.LayoutType.table,
                        "5": dd.LayoutType.figure},
        )
        import huggingface_hub.file_download

        dd.ModelCatalog.register(f"layout/{self.lay_out_model_file}", self.model)

        self.cfg = dd.set_config_by_yaml(
            # os.path.join(working_path, self._DD_ONE)
            self._DD_ONE
        )

        self.cfg.freeze(freezed=False)
        self.cfg.DEVICE = "cpu"
        self.cfg.freeze()

        # layout detector
        self.layout_config_path = dd.ModelCatalog.get_full_path_configs(
            self.cfg.CONFIG.D2LAYOUT
        )
        self.layout_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(
            self.cfg.WEIGHTS.D2LAYOUT
        )
        self.categories_layout = dd.ModelCatalog.get_profile(
            self.cfg.WEIGHTS.D2LAYOUT
        ).categories
        assert self.categories_layout is not None
        assert self.layout_weights_path is not None
        self.d_layout = dd.D2FrcnnDetector(
            self.layout_config_path,
            self.layout_weights_path,
            self.categories_layout,
            device=self.cfg.DEVICE
        )
        dd.tesseract_available()
        # cell detector
        self.cell_config_path = dd.ModelCatalog.get_full_path_configs(self.cfg.CONFIG.D2CELL)
        self.cell_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(self.cfg.WEIGHTS.D2CELL)
        self.categories_cell = dd.ModelCatalog.get_profile(self.cfg.WEIGHTS.D2CELL).categories
        assert self.categories_cell is not None
        self.d_cell = dd.D2FrcnnDetector(
            self.cell_config_path,
            self.cell_weights_path,
            self.categories_cell,
            device=self.cfg.DEVICE
        )

        # row/column detector
        item_config_path = dd.ModelCatalog.get_full_path_configs(
            self.cfg.CONFIG.D2ITEM
        )
        item_weights_path = dd.ModelDownloadManager.maybe_download_weights_and_configs(
            self.cfg.WEIGHTS.D2ITEM
        )
        self.categories_item = dd.ModelCatalog.get_profile(
            self.cfg.WEIGHTS.D2ITEM
        ).categories
        assert self.categories_item is not None
        self.d_item = dd.D2FrcnnDetector(
            item_config_path,
            item_weights_path,
            self.categories_item,
            device=self.cfg.DEVICE
        )
        #/home/vmadmin/python/v6/file-service-02/share-storage/dataset/deepdoctection/weights/doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt
        architecture_name = "db_resnet50"
        profile_name = f"doctr/{architecture_name}/pt/db_resnet50-ac60cadc.pt"
        path_weights_tl = os.path.abspath(
            os.path.join(self.sub_app_dir,f"deepdoctection/weights/{profile_name}")
        )

        #path_weights_tl = dd.ModelDownloadManager.maybe_download_weights_and_configs(
        #"doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt")
        print("-----------------------------------------------")
        print(path_weights_tl)
        print("-----------------------------------------------")
        #categories = ModelCatalog.get_profile(path_weights_tl).categories
        print("-----------Profile info-----------------------------")
        profile = ModelCatalog.get_profile(profile_name)
        categories = profile.categories
        print(profile.name)
        print(profile.dl_library)
        print("-------------------------------------------------")
        # word detector

        self.det = dd.DoctrTextlineDetector(architecture_name, path_weights_tl, categories, "cpu")
        #self.det = dd.DoctrTextlineDetector("db_resnet50", "doctr/db_resnet50/pt/db_resnet50-ac60cadc.pt", categories, "cpu")
        # text recognizer rec = DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu")
        # #
        # path_weights_tr = dd.ModelDownloadManager.maybe_download_weights_and_configs(
        #     "doctr/crnn_vgg16_bn/pt/crnn_vgg16_bn-9762b0b0.pt")
        # self.rec = dd.DoctrTextRecognizer("crnn_vgg16_bn", path_weights_tr, "cpu")

    def build_analyzer_pipeline(self, table=True, table_ref=True, ocr=True):
        """Building the Detectron2/DocTr analyzer based on the given config"""
        return self.doc_tr_service.get_pipe()
        # self.cfg.freeze(freezed=False)
        # self.cfg.TAB = table
        # self.cfg.TAB_REF = table_ref
        # self.cfg.OCR = ocr
        #
        # self.cfg.freeze()
        #
        # pipe_component_list = []
        # layout = dd.ImageLayoutService(self.d_layout, to_image=True, crop_image=True)
        # pipe_component_list.append(layout)
        #
        # if self.cfg.TAB:
        #
        #     detect_result_generator = dd.DetectResultGenerator(self.categories_cell)
        #     cell = dd.SubImageLayoutService(
        #         self.d_cell, dd.LayoutType.table, {1: 6}, detect_result_generator
        #     )
        #     pipe_component_list.append(cell)
        #
        #     detect_result_generator = dd.DetectResultGenerator(
        #         self.categories_item
        #     )
        #     item = dd.SubImageLayoutService(
        #         self.d_item, dd.LayoutType.table,
        #         {1: 7, 2: 8},
        #         detect_result_generator
        #     )
        #     pipe_component_list.append(item)
        #
        #     table_segmentation = dd.TableSegmentationService(
        #         self.cfg.SEGMENTATION.ASSIGNMENT_RULE,
        #         self.cfg.SEGMENTATION.IOU_THRESHOLD_ROWS
        #         if self.cfg.SEGMENTATION.ASSIGNMENT_RULE in ["iou"]
        #         else self.cfg.SEGMENTATION.IOA_THRESHOLD_ROWS,
        #         self.cfg.SEGMENTATION.IOU_THRESHOLD_COLS
        #         if self.cfg.SEGMENTATION.ASSIGNMENT_RULE in ["iou"]
        #         else self.cfg.SEGMENTATION.IOA_THRESHOLD_COLS,
        #         self.cfg.SEGMENTATION.FULL_TABLE_TILING,
        #         self.cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_ROWS,
        #         self.cfg.SEGMENTATION.REMOVE_IOU_THRESHOLD_COLS,
        #     )
        #     pipe_component_list.append(table_segmentation)
        #
        #     if self.cfg.TAB_REF:
        #         table_segmentation_refinement = dd.TableSegmentationRefinementService()
        #         pipe_component_list.append(table_segmentation_refinement)
        #
        # if self.cfg.OCR:
        #     d_layout_text = dd.ImageLayoutService(self.det, to_image=True, crop_image=True)
        #     pipe_component_list.append(d_layout_text)
        #
        #     d_text = dd.TextExtractionService(self.rec,
        #                                       extract_from_roi="WORD")
        #     pipe_component_list.append(d_text)
        #
        #     match = dd.MatchingService(
        #         parent_categories=self.cfg.WORD_MATCHING.PARENTAL_CATEGORIES,
        #         child_categories=dd.LayoutType.word,
        #         matching_rule=self.cfg.WORD_MATCHING.RULE,
        #         threshold=self.cfg.WORD_MATCHING.IOU_THRESHOLD
        #         if self.cfg.WORD_MATCHING.RULE in ["iou"]
        #         else self.cfg.WORD_MATCHING.IOA_THRESHOLD,
        #     )
        #     pipe_component_list.append(match)
        #     order = dd.TextOrderService(
        #         text_container=dd.LayoutType.word,
        #         floating_text_block_names=[dd.LayoutType.title, dd.LayoutType.text, dd.LayoutType.list],
        #         text_block_names=[
        #             dd.LayoutType.title,
        #             dd.LayoutType.text,
        #             dd.LayoutType.list,
        #             dd.LayoutType.cell,
        #             dd.CellType.header,
        #             dd.CellType.body,
        #         ],
        #     )
        #     pipe_component_list.append(order)
        #
        # pipe = dd.DoctectionPipe(pipeline_component_list=pipe_component_list)
        #
        # return pipe

    def build_gradio_analyzer(self, table=True, table_ref=True, ocr=True):
        """Building the Detectron2/DocTr analyzer based on the given config"""

        self.cfg.freeze(freezed=False)
        self.cfg.TAB = table
        self.cfg.TAB_REF = table_ref
        self.cfg.OCR = ocr

        self.cfg.freeze()

        # pipe_component_list = []
        #
        # layout = dd.ImageLayoutService(self.d_layout, to_image=True, crop_image=True)
        deepdoctection_analyzer = self.doc_tr_service.get_analyzer()


        return deepdoctection_analyzer

    def prepare_output(self, dp: deepdoctection.datapoint.view.Page, add_table: bool, add_ocr: bool):
        out = dp.as_dict()
        out.pop("_image")

        layout_items = dp.layouts
        if add_ocr:
            layout_items.sort(key=lambda x: x.reading_order)
        layout_items_str = ""

        for item in layout_items:
            layout_items_str += f"\n {item.category_name}: {item.text}"

        if add_table:
            html_list = [table.html for table in dp.tables]
            if html_list:
                html = ("\n").join(html_list)
            else:
                html = None
        else:
            html = None

        return dp.viz(show_table_structure=True), layout_items_str, html, out

    def analyze_image(self, image_file_path: str):
        from doctr.io import DocumentFile
        # if not isinstance(image,dd_image):
        #     raise Exception(f"image must be {type(dd_image)}")
        img = DocumentFile.from_images(image_file_path)[0]
        ret = self.analyze_image_or_pdf(img)
        return ret
        # analyzer = self.build_gradio_analyzer()
        # df = DataFromList(lst=[img])
        # df = analyzer.analyze(dataset_dataflow=df)
        # df.reset_state()
        # df_iter = iter(df)
        # dp = next(df_iter)
        # return dp

    def analyze_image_or_pdf(self, img: numpy.ndarray, pdf=None, attributes=None):

        # creating an image object and passing to the analyzer by using dataflows
        add_table = True
        add_ocr = True
        if attributes is not None:
            add_table = self._DETECTIONS[0] in attributes
            add_ocr = self._DETECTIONS[1] in attributes

        analyzer = self.build_gradio_analyzer(
            add_table, add_table, add_ocr
        )

        if img is not None:
            image = dd.Image(file_name="input.png", location="")
            if isinstance(img, tuple):
                img = img[0]
            image.image = img[:, :, ::-1]

            df = DataFromList(lst=[image])
            df = analyzer.analyze(dataset_dataflow=df)
        elif pdf:
            df = analyzer.analyze(path=pdf.name, max_datapoints=3)
        else:
            raise ValueError

        df.reset_state()
        df_iter = iter(df)

        dp = next(df_iter)
        # if attributes is None:
        #     return dp
        return self.prepare_output(dp, add_table, add_ocr)

    def analyze_image_by_file_path(self, input_file_path: str, ouput_file_path: str)->AnalysisInfo:
        import html_to_json
        arr_image, text, table, data = self.analyze_image(
            image_file_path=input_file_path
        )
        import numpy as np
        from PIL import Image
        im = Image.fromarray(arr_image)
        im.save(ouput_file_path)
        del im
        del arr_image
        ret = AnalysisInfo()
        ret.result_image_path = ouput_file_path
        ret.text = text
        ret.table = dict()
        try:
            ret.table=html_to_json.convert(table)
        except Exception as e:
            pass


        return ret

    def load_deepdoctection_datapoint_image(self, file_path: str) -> deepdoctection.datapoint.Image:
        location = pathlib.Path(file_path).parent.__str__()
        file_name = pathlib.Path(file_path).name
        from numpy import asarray
        from PIL import Image
        img = Image.open(file_path)
        arr_image = asarray(img)

        ret = deepdoctection.datapoint.Image(
            file_name=file_name, location=location

        )
        ret.get_image()
        print("file data")
        print(ret.image)
        ret.image = arr_image[:, :, ::-1]
        img.close()
        del img
        return ret
