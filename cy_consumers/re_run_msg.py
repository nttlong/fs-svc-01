from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cy_xdoc.services.files import FileServices
import cy_kit
broker:MessageService = cy_kit.singleton(MessageService)
files = cy_kit.singleton(FileServices)
items = files.find_file_async()