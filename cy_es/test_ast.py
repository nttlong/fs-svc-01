import ast
import json









filter = "day(data_item.RegisterOn)=10 "
filter ="(content^1) search 'test'  and privileges['1'] like ['DEV']"
filter ="privileges['1'] like ['dev']"
filter = "(data_item.FileName^1) search 'Unknown'"
filter = "data_item.Privileges['1'] like ['dev']"
import cy_es

fx = cy_es.natural_logic_parse(filter)
vx = cy_es.create_filter_from_dict(fx)

from cy_xdoc.services.search_engine import SearchEngine
import cy_kit
se = cy_kit.singleton(SearchEngine)
lst =se.full_text_search(
    app_name="default",
    page_size=10,
    page_index=0,
    logic_filter=None,
    privileges=None,
    highlight=False,
    content=None
)
print(lst.hits.total)
print(json.dumps(fx))
