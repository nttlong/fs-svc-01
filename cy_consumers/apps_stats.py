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
                        app_name=app.Name,
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



for app in list_of_apps:
    data = app_stat_service.get_stat_of_app(app.Name)
    print(data)


