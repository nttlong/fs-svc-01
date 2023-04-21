import pathlib
import os
import sys

working_path = pathlib.Path(__file__).parent.__str__()
sys.path.append(working_path)
bin_path = os.path.join(working_path,"Accent.Utils","bin")
sourcepath = None
for root, dirs, files in os.walk(bin_path):
    for file in files:
        if file=="Accent.Utils.dll":
            print(file)
            sourcepath =os.path.join(root, file)
            break
    if sourcepath: break
data_set_dir=os.path.join(working_path,"Datasets_Training_Accent")
from pythonnet import load
load("coreclr")
import clr

dll_path="/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Accent.API/bin/Debug/net5.0/publish/Accent.Utils.dll"
clr.AddReference(sourcepath)
import Accent.Utils
#public AccentPredictor(string gram1Path, string gram2Path, string statisticPath, string replaceSpecialPath)
ins = Accent.Utils.AccentPredictor(
    gram1Path=f"{data_set_dir}/news1gram.bin",
    gram2Path =f"{data_set_dir}/news2grams.bin",
    statisticPath=f"{data_set_dir}/_1Statistic.dat",
    replaceSpecialPath=f"{data_set_dir}/ReplaceSpecial.txt"
)
print("kiem tra du lieu")
print(ins.PredictAccents("kiem tra du lieu"))
print("OK")