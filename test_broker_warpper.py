from cyx.common.msg import MSG_FILE_DOC_LAYOUT_ANALYSIS, broker, MessageService
import cy_kit
from cyx.common.share_storage import ShareStorageService
from cyx.common.msg import MessageInfo
from cyx.common.audio_utils import AudioService
from cyx.common.temp_file import TempFiles

@broker(message=MSG_FILE_DOC_LAYOUT_ANALYSIS)
class Process:
    def __init__(self,
                 share_storage_service=cy_kit.singleton(ShareStorageService),
                 audio_service = cy_kit.singleton(AudioService),
                 temp_file=cy_kit.singleton(TempFiles),

                 ):
        self.share_storage_service = share_storage_service
        self.audio_service = audio_service
        self.temp_file = temp_file

    def on_receive_msg(self, msg_info:MessageInfo, msg_broker:MessageService):
        full_file = self.temp_file.get_path(
            app_name=msg_info.AppName,
            file_ext=msg_info.Data["FileExt"],
            upload_id=msg_info.Data["_id"]

        )
        if full_file is None:
            msg_broker.delete(msg_info)
        print(self)
