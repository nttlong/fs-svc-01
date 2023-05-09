import sys
import pathlib
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_es

if cy_es.cy_es_x.version()!='0.0.2.so':
    raise Exception("Incorrect version of cy_es.cy_es_x")
else:
    print(cy_es.cy_es_x.version())