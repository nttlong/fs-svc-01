import pathlib
w = pathlib.Path(__file__).parent.__str__()
import sys
sys.path.append(w)
import os
import py_vncorenlp
data_path = os.path.join(w,"components")
if not os.path.isdir(data_path):
    raise Exception(f"{data_path} was not found")
rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"],
                                                   save_dir=data_path)
txt = "Công ty Cổ phần Tin Học Lạc Việt thông báo nghỉ tết dương lịch và nghỉ tết Nguyên Đán như sau:"
fx =rdrsegmenter.word_segment(txt)
print(txt)
print(fx)

