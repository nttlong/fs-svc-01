MSG_FILE_UPLOAD = "files.upload"
MSG_FILE_GENERATE_IMAGE_FROM_VIDEO = "files.upload.generate.image.from.video"
MSG_FILE_EXTRACT_TEXT_FROM_VIDEO = "files.extract.text.from.video"
MSG_FILE_GENERATE_IMAGE_FROM_OFFICE = "files.upload.generate.image.from.office"
MSG_FILE_GENERATE_IMAGE_FROM_PDF = "files.upload.generate.image.from.pdf"
MSG_FILE_GENERATE_PDF_FROM_IMAGE = "files.upload.generate.pdf"
MSG_FILE_GENERATE_THUMBS = "files.upload.generate.thumbs"
MSG_FILE_OCR_CONTENT = "files.upload.ocr.content"
MSG_FILE_SAVE_DEFAULT_THUMB = "files.upload.save.default.thumb"
MSG_FILE_SAVE_CUSTOM_THUMB = "files.upload.save.custom.thumb"
MSG_FILE_SAVE_OCR_PDF = "files.upload.save.ocr.pdf"
MSG_FILE_UPDATE_SEARCH_ENGINE_FROM_FILE = "files.upload.update.search.from.file"
MSG_FILE_EXTRACT_TEXT_FROM_IMAGE = "files.upload.extract.text.from.file"
MSG_FILE_MOVE_TENANT = "files.move.tenant"
import datetime
from typing import List


class MessageInfo:
    def __init__(self):
        self.MsgType: str = None
        self.Data: dict = None
        self.CreatedOn: datetime.datetime = None
        self.AppName: str = None
        self.Id: str = None
        self.tags = None


class MessageService:
    def emit(cls, app_name: str, message_type: str, data: dict):
        pass

    def re_emit(cls, msg: MessageInfo):
        pass

    def get_message(self, message_type: str, max_items: int = 1000) -> List[MessageInfo]:
        pass

    def get_type(self) -> str:
        return "unknown"

    def consume(self, handler, msg_type: str):
        pass

    def delete(self, item: MessageInfo):
        pass

    def reset_status(self, message_type: str):
        """
        Reset status
        :param message_type:
        :return:
        """
        raise NotImplemented

    def lock(self, item: MessageInfo):
        pass

    def unlock(self, item: MessageInfo):
        pass

    def is_lock(self, item: MessageInfo):
        pass

    def consume(self, handler, msg_type: str):
        pass

    def close(self):
        pass
