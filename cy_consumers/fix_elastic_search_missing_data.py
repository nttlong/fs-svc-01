"""
Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
"""
import datetime
import os
import pathlib
import sys
import threading
import time
from datetime import timezone

working_dir = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(working_dir)
import cy_es
import cy_kit
from cy_xdoc.services.search_engine import SearchEngine
from cy_xdoc.services.apps import AppServices

apps_service = cy_kit.singleton(AppServices)
search_engine = cy_kit.singleton(SearchEngine)


def fix_error(data_privileges):
    """
    Lỗi này là do mấy cha nội Codx đưa dữ liệu vào sai nên phải fix trước khi tìm
    :param data_privileges:
    :return:
    """
    if isinstance(data_privileges, dict):
        for k, v in data_privileges.items():
            if isinstance(v, list):
                t = []
                for x in v:
                    if x == "":
                        t += ["."]
                    else:
                        t += ["x"]
                data_privileges[k] = t

    elif isinstance(data_privileges, list):
        return [fix_error(x) for x in data_privileges]
    else:
        return data_privileges
    return data_privileges


def fix_app(app_name: str):
    utc_date = datetime.datetime(
        datetime.datetime.now().year,
        datetime.datetime.now().month,
        datetime.datetime.now().day, 23, 59, 59, 999, tzinfo=timezone.utc)

    page_index = 0
    page_size = 20
    filter = (cy_es.DocumentFields("data_item") != None)
    filter = filter & (cy_es.DocumentFields("data_item").RegisterOn != None)
    lst = search_engine.full_text_search(
        app_name=app_name,
        content=None,
        page_size=page_size,
        page_index=page_index,
        logic_filter= filter & (cy_es.DocumentFields("data_item").RegisterOn <= utc_date),
        highlight=False,
        privileges=None,
        sort=["data_item.RegisterOn:desc"]
    )
    print(f'Process app {app_name} total rows {lst.hits.hits.__len__()}')
    while lst.hits.hits.__len__() > 0:
        for x in lst.hits.hits:
            if isinstance(x.get("_source"), dict) and isinstance(x["_source"].get("privileges"), dict):
                p = x["_source"]["privileges"]
                p = fix_error(p)
                print(f'{app_name} fix error data of {x["_id"]}, from {page_index*page_size} to {(page_index+1) * page_size}')
                try:
                    search_engine.create_or_update_privileges(
                        app_name=app_name,
                        privileges=p,
                        data_item=None,
                        upload_id=x["_id"]
                    )
                    print(f'fix error data of {x["_id"]} ok')
                except  Exception as e:
                    print(f'fix error data of {x["_id"]} error')
                    print(e)
        page_index += 1
        utc_date = datetime.datetime(
            datetime.datetime.now().year,
            datetime.datetime.now().month,
            datetime.datetime.now().day, 23, 59, 59, 999, tzinfo=timezone.utc)

        lst = search_engine.full_text_search(
            app_name=app_name,
            content=None,
            page_size=page_size,
            page_index=page_index,
            logic_filter=filter & (cy_es.DocumentFields("data_item").RegisterOn <= utc_date),
            highlight=False,
            privileges=None
        )

import elasticsearch
if __name__ == "__main__":
    apps = apps_service.get_list(app_name='admin')
    ths = []
    for x in apps:
        print(f"Process {x['Name']}")
        try:
            fix_app(x["Name"])
        except Exception  as e:
            print(e)

