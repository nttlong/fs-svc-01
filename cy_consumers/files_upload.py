# python /home/vmadmin/python/v6/file-service-02/cy_consumers/files_upload.py temp_directory=./brokers/tmp rabbitmq.server=172.16.7.91 rabbitmq.port=31672
import os
import pathlib
import sys
import threading
import time

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cy_kit
import cyx.common.msg
from cyx.common.msg import MessageService, MessageInfo
from cyx.common.rabitmq_message import RabitmqMsg
from cyx.common.brokers import Broker
from cyx.common import config
import json

log_dir = os.path.join(
    pathlib.Path(__file__).parent.__str__(),
    "logs"

)
print(f"logs to {log_dir}")
logs = cy_kit.create_logs(
    log_dir=log_dir,
    name=pathlib.Path(__file__).stem
)
if isinstance(config.get('rabbitmq'), dict):
    cy_kit.config_provider(
        from_class=MessageService,
        implement_class=RabitmqMsg
    )
else:
    cy_kit.config_provider(
        from_class=MessageService,
        implement_class=Broker
    )
msg = cy_kit.singleton(MessageService)
from cyx.common.temp_file import TempFiles

temp_file = cy_kit.singleton(TempFiles)


def on_receive_msg(msg_info: MessageInfo):
    full_file_path = temp_file.get_path(
        app_name=msg_info.AppName,
        file_ext=msg_info.Data["FileExt"],
        upload_id=msg_info.Data["_id"]
    )
    if full_file_path  is None:
        msg.delete(msg_info)
        return

    print(f"{full_file_path} was receive")

    if not os.path.isfile(full_file_path) :
        msg.delete(msg_info)
        print(f"{full_file_path} was not found")
        logs.info(f"{full_file_path} was not found")
        return

    print(f"Receive file {full_file_path}")
    logs.info(f"Receive file {full_file_path}")
    try:

        if not isinstance(msg_info, MessageInfo):
            raise Exception(f"msg param must be MessageInfo")
        file_ext = msg_info.Data.get("FileExt")
        import mimetypes
        mime_type, _ = mimetypes.guess_type(msg_info.Data['FullFileName'])
        if file_ext.lower() == "pdf":
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_PDF}\n{full_file_path}")
            msg_info.Data["processing_file"]=full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_OCR_CONTENT,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_OCR_CONTENT}\n{full_file_path}")
        if file_ext.lower() in config.ext_office_file and file_ext.lower() != "pdf":
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE}\n{full_file_path}")
            logs.info(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_OFFICE}\n{full_file_path}")

            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE,
                data=msg_info.Data
            )
            logs.info(f"{cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE}\n{full_file_path}")
            print(f"{cyx.common.msg.MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE}\n{full_file_path}")
        if mime_type.startswith('video/'):
            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO}\n{full_file_path}")
            msg_info.Data["processing_file"] = full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_VIDEO,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_IMAGE_FROM_VIDEO}\n{full_file_path}")
        if mime_type.startswith('image/'):
            msg_info.Data["processing_file"]=full_file_path
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_THUMBS,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n{full_file_path}")
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_GENERATE_PDF_FROM_IMAGE,
                data=msg_info.Data
            )
            msg.emit(
                app_name=msg_info.AppName,
                message_type=cyx.common.msg.MSG_FILE_EXTRACT_TEXT_FROM_IMAGE,
                data=msg_info.Data
            )
            print(f"{cyx.common.msg.MSG_FILE_GENERATE_THUMBS}\n{full_file_path}")

        msg.delete(msg_info)
        print(f"{full_file_path}\n is ok")
    except Exception as e:
        msg.delete(msg_info)
        logs.exception(e)
        print(e)


msg.consume(
    msg_type=cyx.common.msg.MSG_FILE_UPLOAD,
    handler=on_receive_msg
)
