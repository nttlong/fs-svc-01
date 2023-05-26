from cyx.common.msg import MSG_FILE_DOC_LAYOUT_ANALYSIS, broker, MessageService
import cy_kit
from cyx.common.share_storage import ShareStorageService
from cyx.common.msg import MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg


@broker(message=MSG_FILE_DOC_LAYOUT_ANALYSIS)
class Process:
    def __init__(self,
                 share_storage_service=cy_kit.singleton(ShareStorageService)):
        self.share_storage_service = share_storage_service

    def on_receive_msg(self, msg_info:MessageInfo, msg_broker:MessageService):
        print(self)
