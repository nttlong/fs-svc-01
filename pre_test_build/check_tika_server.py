print("Check tika server")
try:
    import pathlib
    working_path = pathlib.Path(__file__).parent.parent.__str__()
    import sys
    import os
    sys.path.append(working_path)
    ext_lib_folder =os.path.abspath(os.path.join(working_path, "cyx","ext_libs"))
    path_to_java = os.path.join(ext_lib_folder, "tika-server.jar")
    path_to_java_md5 = os.path.join(ext_lib_folder, "tika-server.jar.md5")
    if not os.path.isfile(path_to_java):
        raise Exception(f"f{path_to_java} was not found")
    if not os.path.isfile(path_to_java_md5):
        raise Exception(f"f{path_to_java_md5} was not found")
    if not os.path.isdir(ext_lib_folder):
        raise Exception(f"f{ext_lib_folder} was not found")
    os.environ['TIKA_SERVER_JAR'] = path_to_java
    os.environ['TIKA_PATH'] = ext_lib_folder
    if sys.modules.get("tika") is not None:
        import importlib
        importlib.reload(sys.modules["tika"])

    import tika
    tika.initVM()
    from tika import parser
    headers = {

    }
    ret = parser.from_file(__file__)#,  requestOptions={'headers': headers, 'timeout': 3000000})
    print(ret)
    print("Check tika server is ok")
except Exception as e:
    raise e