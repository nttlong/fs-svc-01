import os.path
import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
class stages:
    class py39_core:
        from pymongo.mongo_client import MongoClient
        from elasticsearch.transport import Transport
        from bson.objectid import ObjectId
        from gridfs.grid_file import GridIn
    class framework_core:

        from cy_kit.cy_kit_x import singleton
        from cy_docs.cy_docs_x import AggregateDocument
        from cy_es.cy_es_x import get_version
    class framework:
        from cyx.common.base import DbCollection
        from cy_xdoc.services.files import FileServices
        from cy_web.cy_web_x import WebApp
def verify(obj):
    print(f"verify {obj}...")
    file_name = sys.modules[obj.__module__].__file__
    if os.path.splitext(file_name)[1] !=".so":
        raise Exception(f"{obj.__name__} is not compile. Lib file is \n{file_name}")
    else:
        print(f"verify {obj} is ok, lib file {file_name}")

def verify_stage(*args,**kwargs):
    if isinstance(args,list):
        for x in list(args):
            verify(x)
    if isinstance(args,tuple):
        if len(args)>1:
            for x in list(args):
                verify_stage(x)
        elif isinstance(args[0],list):
            for x in args[0]:
                verify_stage(x)
        else:
            for k, v in args[0].__dict__.items():
                if k[0:2] != "__" and k[-2:] != "__":
                    verify(v)
    else:
        for k,v in args.__dict__.items():
            if k[0:2]!="__" and k[-2:]!="__":
                verify(v)

def verfy_full_stage():
    for k,v in stages.__dict__.items():
        if k[0:2]!="__" and k[-2:]!="__":
            verify_stage(v)
lst = [stages.__dict__.get(x) for x in sys.argv if stages.__dict__.get(x)]
if len(lst)>0:
    verify_stage(lst)
else:
    verfy_full_stage()
