import os.path
import pathlib
import clr
_wrking_dir_ = pathlib.Path(__file__).parent.__str__()
dll_file = "Accent.Utils.dll"
import subprocess
#check mono
mono_path_bin =subprocess.check_output(f"which mono".split(' '))
mono_path =mono_path_bin.decode('utf8')
if not os.path.isfile(mono_path):
    raise Exception("mono was not found")
ret = subprocess.check_output(f"find / -name {dll_file}".split(' '))
ret_ttx = ret.decode('utf8')
dll_path=ret_ttx.lstrip('\n').rstrip('\n')
dll_paths = dll_path.split('\n')
publish_paths = [x for x in dll_paths if '/publish/' in x]
if publish_paths.__len__()==0:
    raise Exception("Can not find publish/Accent.Utils.dll")
dll_path="/py3_dotnet/python_dot_net_core/Accent.Utils/bin/Debug/net5.0/publish/Accent.Utils.dll"
clr.AddReference(dll_path)
import Accent.Utils
instance = Accent.Utils.AccentPredictor(
                gram1Path=f"{_wrking_dir_}/news1gram.bin",
                gram2Path=f"{_wrking_dir_}/news2grams.bin",
                statisticPath=f"{_wrking_dir_}/_1Statistic.dat",
                replaceSpecialPath=f"{_wrking_dir_}/ReplaceSpecial.txt"
            )
contents = [
    "noi dung nay dung de kiem tra tinh dung dan cua he thong du doan van ban tieng viet",
    "tien viet so voi tien my re hon. hom nay minh tra tien my bang tien viet",
    "Hom truoc minh vay tien My bang tien My. Hom nay minh tra tien My bang tien Viet",
    "Moi lan an my minh tra tien Viet. Hom nay, minh tra bang tien My",
    "Tien hoc le hau hoc van. Nhung tien hoc le mac hon tien hoc van"

]
for content in contents:
    ret_content = instance.get_text(content)
    print(content)
    print(ret_content.replace('\n',' '))
print("OK")