import os
if not os.path.isfile("/usr/bin/tesseract"):
    raise Exception(f"'/usr/bin/tesseract' was not found")
import doctr
if doctr.__version__!="v0.6.0":
    raise Exception(f"doctr version require is v0.6.0. But found {doctr.__version__}")
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
from doctr.datasets import CORD
import deepdoctection
if str(deepdoctection.__version__)!="0.23":
    raise Exception(f"deepdoctection version require is 0.23. But found {deepdoctection.__version__}")
from deepdoctection.dataflow.serialize import DataFromList

import gradio as gr
import datasets
if datasets.__version__!="2.10.2.dev0":
    raise Exception(f"datasets version require is 2.10.2.dev0. But found {datasets.__version__}")
import transformers
if transformers.__version__!="4.28.0.dev0":
    raise Exception(f"transformers version require is 4.28.0.dev0. But found {transformers.__version__}")
import detectron2
if detectron2.__version__!="0.6":
    raise Exception(f"detectron2 version require is 0.6. But found {detectron2.__version__}")
import gradio
if gradio.__version__!="3.32.0":
    raise Exception(f"gradio version require 3.32.0. But found {gradio.__version__}")
import packaging
if packaging.__version__!="20.9":
    raise Exception(f"packaging version require 20.9. But found {packaging.__version__}")