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
for app in list_of_apps:
    fx = app_stat_service.auto_stats()
    print(fx)
