import os.path
import sys
import pathlib

skip_check_python_version = False
if len([x for x in sys.argv if x=="--skip"])>0:
    skip_check_python_version = True

sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
if not skip_check_python_version:
    if sys.version_info.major ==3 and sys.version_info.minor ==9 and sys.version_info.micro==5:
        print(sys.version)
    else:
        raise Exception(f"incorect version. Current version is {sys.version}. Path to {sys.executable}")
    import cython
    if cython.__version__!="3.0.0b1":
        raise Exception(f"incorect cython version. Current version is {cython.__version__}")
class stages:
    def py39_core(self):
        from pymongo.mongo_client import MongoClient
        from elasticsearch.transport import Transport
        from bson.objectid import ObjectId
        from gridfs.grid_file import GridIn
        return [MongoClient,Transport,ObjectId,GridIn]
    def core_framework(self):
        from cy_kit.cy_kit_x import singleton
        from cy_docs.cy_docs_x import AggregateDocument
        from cy_es.cy_es_x import get_version
        return [singleton,AggregateDocument,get_version]
    def app_framework(self):
        from cyx.common.base import DbCollection
        from cy_xdoc.services.files import FileServices
        from cy_web.cy_web_x import WebApp
        return [DbCollection,FileServices,WebApp]
    def check(self):
        return []
    def office(self):
        import subprocess
        libre_office_path = "/usr/bin/soffice"
        if os.path.isfile(libre_office_path):
            print(f"{libre_office_path} is ok")
        else:
            ret = subprocess.check_output(['which', 'soffice'])
            ret_ttx = ret.decode('utf8')
            raise Exception(f"{libre_office_path} was not found. Libre Office path is in '{ret_ttx}'")
        return []
    @staticmethod
    def component(name:str):
        import subprocess
        ret = subprocess.check_output(['which', name])
        ret_ttx = ret.decode('utf8').lstrip('\n').rstrip('\n')
        if ret_ttx =="":
            raise Exception(f"{name} was not found. Path is in '{ret_ttx}'")
        else:
            print(f"{name} was found. Path is in '{ret_ttx}'")
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
        elif callable(args[0]):
            fx= stages()
            lst =args[0](fx)
            for x in lst:
                verify(x)
        else:
            for k, v in args[0].__dict__.items():
                if k[0:2] != "__" and k[-2:] != "__":
                    verify(v)
    else:
        for k,v in args.__dict__.items():
            if k[0:2]!="__" and k[-2:]!="__":
                verify(v)

def verfy_full_stage():
    obj = stages()
    for k,v in stages.__dict__.items():
        if k[0:2]!="__" and k[-2:]!="__":
            val = getattr(obj,k)(obj)
            verify_stage(val)

check_component = [x for x in sys.argv if x.startswith("--check")]
if len(check_component)>0:
    components = [x for x in sys.argv if x[0:2]!="__" and x[-2:]!="__" and x!="--check" and os.sep not in x and not x.startswith("--")]
    print(f"Verify components {' '.join(components)}")
    for x in components:
        if os.sep not in x:
            stages.component(x)
else:
    lst = [stages.__dict__.get(x) for x in sys.argv if stages.__dict__.get(x)]
    if len(lst)>0:
        verify_stage(lst)
    else:
        verfy_full_stage()
