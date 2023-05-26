import pathlib
import sys
import os

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_kit
from cyx.common.share_storage import ShareStorageService
import cyx.document_layout_analysis.system
shared_storage_service=cy_kit.singleton(ShareStorageService)
cyx.document_layout_analysis.system.set_dataset_path(
            os.path.abspath(
                os.path.join(shared_storage_service.get_root(), "dataset")
            )
        )
from cyx.common.msg import MSG_FILE_DOC_LAYOUT_ANALYSIS, broker, MessageService


from cyx.common.msg import MessageInfo
from cyx.common.audio_utils import AudioService
from cyx.common.temp_file import TempFiles
from cyx.document_layout_analysis.table_ocr_service import TableOCRService



@broker(message=MSG_FILE_DOC_LAYOUT_ANALYSIS)
class Process:
    def __init__(self,
                 shared_storage_service=shared_storage_service,
                 audio_service=cy_kit.singleton(AudioService),
                 temp_file=cy_kit.singleton(TempFiles),
                 table_ocr_service=cy_kit.singleton(TableOCRService)
                 ):
        print("consumer init")
        self.shared_storage_service = shared_storage_service
        self.audio_service = audio_service
        self.temp_file = temp_file


        self.output_dir = self.shared_storage_service.get_temp_dir(self.__class__)
        self.table_ocr_service = table_ocr_service

    def on_receive_msg(self, msg_info: MessageInfo, msg_broker: MessageService):
        full_file = self.temp_file.get_path(
            app_name=msg_info.AppName,
            file_ext=msg_info.Data["FileExt"],
            upload_id=msg_info.Data["_id"]

        )
        if full_file is None:
            msg_broker.delete(msg_info)
        output_file_path = os.path.join(self.output_dir,f'{msg_info.Data["_id"]}.{msg_info.Data["FileExt"]}')
        ret = self.table_ocr_service.analyze_image_by_file_path(
            input_file_path=full_file,
            ouput_file_path=output_file_path
        )
        print(ret.result_image_path)
        print(ret.msg_1)
        print(ret.msg_2)
        print(ret.data)
        print(ret)
