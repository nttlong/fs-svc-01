import ast
import json









filter = "day(data_item.RegisterOn)=10 "
filter ="(content^1) search 'test'  and privileges['1'] like ['DEV']"
filter ="privileges['1'] like ['dev']"
filter = "(data_item.FileName^1) search 'Unknown'"
filter = "data_item.Privileges['7'] like [''] or data_item.Privileges['u'] like ['Guest']"
import cy_es

fx = cy_es.natural_logic_parse(filter)
vx = cy_es.create_filter_from_dict(fx)

from cy_xdoc.services.search_engine import SearchEngine
import cy_kit
se = cy_kit.singleton(SearchEngine)
lst =se.full_text_search(
    app_name="default",
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
