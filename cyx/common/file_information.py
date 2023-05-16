import cy_kit
from cyx.media.libre_office import LibreOfficeService
from cyx.common.temp_file import TempFiles
class FileInformationService:
    def __init__(self,
                 libre_office_service=cy_kit.singleton(LibreOfficeService),
                 temp_file = cy_kit.singleton(TempFiles)):
        self.libre_office_service = libre_office_service
        self.temp_file = temp_file
    def get_one_page(self, file_path: str,page_number:int)->str:
        self.libre_office_service.extract_page(file_path,page_number)
    def get_total_pages(self, file_path: str) -> int:
        from tika import parser

        headers = {

        }
        ret = parser.from_file(file_path, requestOptions={'headers': headers, 'timeout': 30000})
        # import psutil
        # import signal
        # for x in psutil.process_iter():
        #     if x.status() == 'sleeping' and x.__name__() == 'java':
        #         os.kill(x.pid, signal.SIGKILL)
        if ret.get('metadata'):
            metadata = ret.get('metadata')
            if isinstance(metadata,dict):

                return int(metadata.get("xmpTPg:NPages") or 1)

            else:
                return 1
        return 1
