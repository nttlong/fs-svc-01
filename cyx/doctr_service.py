import pathlib
import shutil

working_dir = pathlib.Path(__file__).parent.parent.__str__()
lib_path  = pathlib.Path(__file__).parent.__str__()
import os
os.environ["XDG_CACHE_HOME"]=f"{working_dir}/dataset"
os.environ["DOCTR_CACHE_DIR"]=f"{working_dir}/dataset/doctr"

# os.environ["DOCTR_CACHE_DIR"]= f"{working_dir}/dataset"
from doctr.io import DocumentFile

from doctr.models import ocr_predictor
from doctr.datasets import CORD
deepdoctection_analyzer = None


class DoctrService:
    def __init__(self):
        global working_dir
        global lib_path
        self.dataset_model_path = os.path.abspath(
            os.path.join(lib_path,"dataset-model","model_final_inf_only.pt")
        )

        self.dataset_dir = os.path.join(working_dir,"dataset")
        self.deepdoctection_weights_layout_finale_model_dir = os.path.abspath(
            os.path.join(
                self.dataset_dir,
                "deepdoctection",
                "weights",
                "layout"
            )
        )

        self.model = ocr_predictor(
            pretrained=True,
            detect_language=True,
            export_as_straight_boxes=True,
            detect_orientation=True
            )
        import deepdoctection as dd

        global deepdoctection_analyzer
        if deepdoctection_analyzer is None:
            deepdoctection_analyzer = dd.get_dd_analyzer(
                language="vie"

            )
        self.deepdoctection_analyzer=deepdoctection_analyzer

        dest_model = os.path.join(self.deepdoctection_weights_layout_finale_model_dir, "model_final_inf_only.pt")
        if not os.path.isfile(self.dataset_model_path):
            fake_model_path = os.path.join(
                working_dir,
                "dataset",
                "deepdoctection",
                "weights",
                "layout",
                "d2_model_0829999_layout_inf_only.pt"
            )
            if os.path.isfile(fake_model_path):
                if not os.path.isfile(dest_model):
                    shutil.copy(
                        src=fake_model_path,
                        dst=dest_model
                    )
            # raise FileNotFoundError(f"{self.dataset_model_path} was not found")
        if not  os.path.isfile(dest_model):
            print(f"Copy model file form {self.dataset_model_path}\n\tto{dest_model}")

            os.makedirs(self.deepdoctection_weights_layout_finale_model_dir,exist_ok=True )
            shutil.copy(
                src=self.dataset_model_path,
                dst=dest_model
            )
        else:
            print(f"{dest_model} is already")



    def get_result_from_image(self,img_src:str):
        doc = DocumentFile.from_images(img_src)
        ret = self.model (doc)
        return ret
