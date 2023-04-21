from pythonnet import load
load("coreclr")
import clr
dll_path ="/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Accent.Utils/bin/Release/net5.0/Accent.Utils.dll"
dll_path="/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Accent.API/bin/Debug/net5.0/publish/Accent.Utils.dll"
clr.AddReference(dll_path)
import Accent.Utils
#public AccentPredictor(string gram1Path, string gram2Path, string statisticPath, string replaceSpecialPath)
ins = Accent.Utils.AccentPredictor(
    gram1Path=f"/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Datasets_Training_Accent/news1gram.bin",
    gram2Path ="/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Datasets_Training_Accent/news2grams.bin",
    statisticPath="/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Datasets_Training_Accent/_1Statistic.dat",
    replaceSpecialPath="/home/vmadmin/python/v6/file-service-02/dotnet_core/VietnameseAccent/Datasets_Training_Accent/ReplaceSpecial.txt"
)
print("OK")