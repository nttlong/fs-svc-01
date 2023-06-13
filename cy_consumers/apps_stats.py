import datetime
import sys
import os
import pathlib

sys.path.append(
    pathlib.Path(__file__).parent.parent.__str__()
)
import cy_kit
from cy_xdoc.services.apps import App
from cyx.base import DbConnect
import cy_docs

connector = cy_kit.singleton(DbConnect)
from cy_xdoc.models.files import DocUploadRegister
from cyx.models import FsFile
from cy_xdoc.models.apps import App

apps_context = connector.db("admin").doc(App)
list_of_apps = list(apps_context.context.aggregate().project(
    apps_context.fields.Name,
    apps_context.fields._id
))
from cy_xdoc.services.apps_stat import AppStatServices

app_stat_service = cy_kit.singleton(AppStatServices)

from cy_xdoc.models.apps import App


def run(app_name: str):
    from_year, to_year = app_stat_service.get_year_range(app_name)
    if to_year:
        for year in range(from_year, to_year + 1):
            from_month, to_month = app_stat_service.get_month_range(app_name, year)

            if to_month:
                for month in range(from_month, to_month + 1):
                    stat_data = app_stat_service.stat_by_month(
                        app_name=app_name,
                        year=year,
                        month=month

                    )
                    from_day, to_day = app_stat_service.get_day_range(app_name, year, month)
                    if to_day:
                        for day in range(from_day, to_day + 1):
                            stat_data = app_stat_service.stat_by_day(
                                app_name=app_name,
                                year=year,
                                month=month,
                                day=day

                            )


app_stat_service.get_stat_of_app("default")
app_names = [app.Name for app in list_of_apps]


@cy_kit.loop_process([app.Name for app in list_of_apps])
def get_data(app_name: str):
    ret = app_stat_service.get_stat_of_app(app_name)
    return {app_name: ret}


@cy_kit.watch_forever(sleep_time=1)
def my_run(seconds: int):
    start_time = datetime.datetime.now()
    data = dict(count=0)
    print(f"Start at ={start_time}")
    print(f"This is the demonstrated how to print 'Hello!' in every 5 second")

    def check(data):
        return datetime.datetime.now().second % seconds == 0

    def run(data):
        global count
        count = data["count"]
        count+=1
        data["count"]=count
        print(f"Hello. This is {count} is say")

    return data, check, run


my_run(5)
# data_list = get_data()
# default_app = [x for x in data_list if x.get('default') is not None][0]
# print(default_app)
# for app in list_of_apps:
#     data = app_stat_service.get_stat_of_app(app.Name)
#     print(data)
