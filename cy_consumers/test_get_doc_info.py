import cy_kit
from cyx.common.file_information import FileInformationService
fx = cy_kit.singleton(FileInformationService)
fx1=f"/home/vmadmin/python/v6/file-service-02/temp-data/LV - ThuThongBao _002_.docx"
fx2=f"/home/vmadmin/python/v6/file-service-02/temp-data/lancape.docx"

a = fx.get_total_pages(fx2)
print(a)