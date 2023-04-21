import datetime
import time

from setuptools.command.rotate import rotate
from cy_xdoc.models.files import DocUploadRegister
import cy_es
import elasticsearch
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.files import FileServices
from cyx.rdr_segmenter.segmenter_services import VnSegmenterService
import cy_es

se = cy_kit.singleton(SearchEngine)
fs = cy_kit.singleton(FileServices)
vn = cy_kit.singleton(VnSegmenterService)
client = elasticsearch.Elasticsearch(
    hosts=["192.168.18.36:9200"]
)
index = f"lv-codx_test-2023"
fx = cy_es.DocumentFields("data_item")
emp = cy_es.DocumentFields("Employee")
vx = (fx._id @ "f25609d2-7365-4c49-a0f3-a17aa229ec51") | (fx._id @ "3c2b3749-b0a4-4c3e-9723-aeb5da97eb19")
map = cy_es.get_map_struct(client,index)

filter1 = {
    "data_item.MyNameIs": {
        "$contains" :"hello"
    }
}
filter_month = {
     "$gte":{
         "$$month":"data_item.RegisterOn",
         "$value":4
     }

}
filter_day = {
     "$gt":{
         "$$day":"data_item.RegisterOn",
         "$value":3
     }

}
filter_year = {
     "$eq":{
         "$$year":"data_item.RegisterOn",
         "$value":2023
     }

}
filter_first = {
    "$$first":"data_item.MyNameIs",
    "$value":"hello"

}
filter_last = {
    "$$last":"data_item.MyNameIs",
    "$value":"hello"

}
fx= {
    "content":"404",
    "page_size":20,"page_index":0,
    "highlight":True,
    "privileges":{"$or":[{"1":{"$contains":["ADMIN"]}},{"U":{"$contains":["ADMIN"]}},{"9":{"$contains":[""]}},{"7":{"$contains":[""]}}]}}

# fa = cy_es.create_filter_from_dict(filter_year)
data_item_filter = cy_es.DocumentFields("data_item")
filter_by_code = data_item_filter.Code=="0001"
f_year = cy_es.create_filter_from_dict(filter_year)
f_day = cy_es.create_filter_from_dict(filter_day)


f_month = cy_es.create_filter_from_dict(filter_month)

full = f_day | f_year & f_month
fa= cy_es.create_filter_from_dict(filter_last)

#fa= fx.MyNameIs.endswith("hello")
items = cy_es.select(
    client=client,
    index=index,
    filter=full,


)
print(items.hits.total)
for x in items.hits.hits:
    print(x)
cy_es.update_doc_by_id(
    client=client,
    index=index,
    id="35240062-c180-4b29-b918-cddda0a30ea6",
    data=dict(
        data_item=dict(
            Code="001",
            RegisterOn=datetime.datetime.utcnow(),
            HasThumb=True,
            Depts=[1,2,4],
            MyNameIs= "$*hello.^"
        )
    )
)
print(fx)
