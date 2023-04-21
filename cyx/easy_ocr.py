import os.path
import pathlib
import typing

import easyocr
import cy_kit
from cyx.vn_predictor import VnPredictor
from  cyx.common.temp_file import TempFiles
__model_storage_directory__ = os.path.abspath(
    os.path.join(
        pathlib.Path(__file__).parent.parent.__str__(),
        "dataset",
        "easyocr"
    )

)
class DouTextInfo:
    content:typing.List[str]

    suggest_content:str
class EasyOCRService:
    def __init__(
            self,
            vn_predict = cy_kit.singleton(VnPredictor),
            tmp_file = cy_kit.singleton(TempFiles)
    ):
        self.use_gpu = False
        self.reader = easyocr.Reader(
            ['vi', 'en'], gpu=self.use_gpu,
            model_storage_directory=__model_storage_directory__
        )
        self.vn_predict = vn_predict
        self.tmp_file = tmp_file
    def get_duo_text(self, image_file: str) -> dict:
        ret = {}
        if os.path.isfile(image_file):
            lst_text = self.reader.readtext(image_file, detail=0)

            for x in lst_text:
                ret[x]=self.vn_predict.get_text(x)


            # ret_1 = "\n".join(results)
            # _r =[]
            # for x in results:
            #     _r+=[self.vn_predict.get_text(x)]
            #
            # ret = " ".join(_r)
            # return ret+"\n"+ret_1
            return ret

    def get_text(self, image_file: str) -> str:
        if os.path.isfile(image_file):
            results = self.reader.readtext(image_file, detail=0)
            ret_1 = "\n".join(results)
            _r =[]
            for x in results:
                _r+=[self.vn_predict.get_text(x)]

            ret = " ".join(_r)
            return ret+"\n"+ret_1
