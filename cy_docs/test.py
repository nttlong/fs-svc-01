import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_docs
f1 = cy_docs.fields.code
f2 = cy_docs.fields.name
fx= f2>f1
import cy_kit
from cyx.base import DbConnect
fs=  cy_kit.singleton(DbConnect)


print(fx)