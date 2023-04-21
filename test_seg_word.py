import cy_kit
import cyx.rdr_segmenter.segmenter_services
se = cy_kit.singleton(cyx.rdr_segmenter.segmenter_services.VnSegmenterService)
fx = se.parse_word_segment("Công ty Cổ phần Tin Học Lạc Việt thông báo nghỉ tết dương lịch và nghỉ tết Nguyên Đán như sau:",boot=[100])
print(fx)
fx = se.parse_word_segment("Chờ xét duyệt ".lower(),boot=[100])
print(fx)
