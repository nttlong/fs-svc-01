import sys
import pathlib

working_path = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_path)

import os
os.environ["TRANSFORMERS_OFFLINE"] = "true"
os.environ["HF_HUB_OFFLINE"]="true"
from huggingface_hub import constants
print(constants.__dict__)
import cy_kit
import gradio as gr
from  cyx.table_ocr_service import TableOCRService
f=f"/home/vmadmin/python/v6/file-service-02/temp-data/Screenshot_3.png"
table_ocr_service = cy_kit.singleton(TableOCRService)
ret=table_ocr_service.analyze_image_by_file_path(
    file_path=f
)
print(ret)