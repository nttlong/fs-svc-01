import py_vncorenlp
import cy_es
import elasticsearch
client = elasticsearch.Elasticsearch(
    hosts=["172.16.7.91:30920"]
)
app_name="lv-docs"
index =f"lv-codx_{app_name}"
id='f7f26d59-6303-412c-a1f1-26407f508a10'
doc =cy_es.get_doc(
    client=client,
    index=index,
    id=id

)

# Automatically download VnCoreNLP components from the original repository
# and save them in some local machine folder
path_to_vn_core_lp = f"/cyx/rdr_segmenter/vncorenlp/components"
rdrsegmenter = py_vncorenlp.VnCoreNLP(annotators=["wseg"], save_dir=path_to_vn_core_lp)
text = "Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây."
text = "cách khắc phục lỗi phông chữ trong phần mềm soạn thảo văn bản"
text = "Sau khi giao việc cho user ùi Văn Đắc. , Thông tin của user thực hiện khồn được hiển thị trong chỉ tiết cv (account người giao việc) "
text = doc.source.content.lower()
output = rdrsegmenter.word_segment(text)
print(output)
print("xong")
# py_vncorenlp.download_model(save_dir=path_to_vn_core_lp)
#
#
#
# # Load VnCoreNLP
# model = py_vncorenlp.VnCoreNLP(save_dir=path_to_vn_core_lp)
# # Equivalent to: model = py_vncorenlp.VnCoreNLP(annotators=["wseg", "pos", "ner", "parse"], save_dir='/absolute/path/to/vncorenlp')
#
# # Annotate a raw corpus
# # model.annotate_file(input_file="/absolute/path/to/input/file", output_file="/absolute/path/to/output/file")
#
# # Annotate a raw text
# fx= model.annotate_text("Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây.")
# model.print_out(model.annotate_text("Ông Nguyễn Khắc Chúc  đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây."))