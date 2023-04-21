import datetime

from  cyx.media.video import VideoServices
import cy_kit
import cy_docs
file=f"/home/vmadmin/python/v6/file-service-02/temp-data/ok.mp4"
scv:VideoServices = cy_kit.singleton(VideoServices)
pdf_file = scv.get_pdf(file,num_of_segment =10)
print(pdf_file)