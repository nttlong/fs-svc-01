import ast
import json









filter = "day(data_item.RegisterOn)=10 "
filter ="(content^1) search 'test'  and privileges['1'] like ['DEV']"
filter ="privileges['1'] like ['dev']"
filter = "(data_item.FileName^1) search 'Unknown'"
filter = "privileges['7'] like [0,'admin']"
filter = "data_item.FileNameLower search 'sample.pdf'"
import cy_es

fx = cy_es.natural_logic_parse(filter)
vx = cy_es.create_filter_from_dict(fx)

from cy_xdoc.services.search_engine import SearchEngine
import cy_kit
se = cy_kit.singleton(SearchEngine)
lst =se.full_text_search(
    app_name="0604230816",
    page_size=400,
    page_index=0,
    logic_filter=fx,
    privileges=None,
    highlight=False,
    content=None
)
for x in lst.hits.hits:
    if len(x["_source"]["data_item"]["Privileges"].keys())>1:
        print(x["_source"]["data_item"]["Privileges"])
print(lst.hits.total)
print(json.dumps(fx))
