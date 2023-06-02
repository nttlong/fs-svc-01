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
mb = (1024 * 1024)
gb = mb * 1024
for app in list_of_apps:
    print(f"Stat app = {app[apps_context.fields.Name]}")
    print(f"\t grand total calculating")
    files_context = connector.db(app[apps_context.fields.Name]).doc(DocUploadRegister)
    total_files = files_context.context.count({})
    print(f"\t grand total {total_files}")
    t = datetime.datetime.utcnow()
    agg_get_size_of_uploaded = files_context.context.aggregate().match(
        cy_docs.EXPR(
            (files_context.fields.SizeUploaded == files_context.fields.SizeInBytes) & \
            (files_context.fields.Status == 1)
        )
    ).project(
        cy_docs.fields.total_size_mb >> cy_docs.FUNCS.sum(files_context.fields.SizeInBytes / mb),
        cy_docs.fields.total_size_gb >> cy_docs.FUNCS.sum(files_context.fields.SizeInBytes / gb),
        cy_docs.fields.count_of_files >> cy_docs.FUNCS.count(files_context.fields.id),
        cy_docs.fields.start >> cy_docs.FUNCS.min(files_context.fields.RegisterOn),
        cy_docs.fields.end >> cy_docs.FUNCS.max(files_context.fields.RegisterOn),
        cy_docs.fields.first >> cy_docs.FUNCS.first(files_context.fields.RegisterOn),
        cy_docs.fields.last >> cy_docs.FUNCS.last(files_context.fields.RegisterOn),
    )
    compiler_time = (datetime.datetime.utcnow()-t).total_seconds()*1000
    print(f"\t Expression compiler {compiler_time}")
    t = datetime.datetime.utcnow()
    fx = list(agg_get_size_of_uploaded)
    exec_time = (datetime.datetime.utcnow() - t).total_seconds() * 1000
    print(f"\t Mongodb exec time {exec_time}")
    print(fx)
