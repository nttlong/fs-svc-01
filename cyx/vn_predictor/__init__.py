from pythonnet import load
import pathlib
__working_path__ = pathlib.Path(__file__).parent.parent.parent.__str__()
import sys
import os
sys.path.append(__working_path__)
load("coreclr")
import clr
__Accent_Utils_AccentPredictor__  = None
class VnPredictor:
    def __init__(self):
        self.working_path = __working_path__
        self.bin_path = os.path.join(self.working_path,"python_dot_net_core","Accent.Utils", "bin")
        self.data_set_dir = os.path.join(self.working_path, "python_dot_net_core", "Datasets_Training_Accent")
        if not os.path.isdir(self.bin_path):
            self.bin_path = os.path.join(pathlib.Path(self.working_path).parent.__str__(), "python_dot_net_core", "Accent.Utils", "bin")
            self.data_set_dir = os.path.join(pathlib.Path(self.working_path).parent.__str__(), "python_dot_net_core", "Datasets_Training_Accent")
        if not os.path.isdir(self.bin_path):
            raise Exception(f"{self.bin_path} was not found")
        self.source_path = None
        for root, dirs, files in os.walk(self.bin_path):
            for file in files:
                if file == "Accent.Utils.dll":
                    print(file)
                    self.source_path = os.path.join(root, file)
                    break

            if self.source_path: break

        if self.source_path is None:
            raise Exception(f"Can not find 'Accent.Utils.dll' in {self.bin_path}")
        self.instance = None

    def get_text(self,content:str)->str:
        global __Accent_Utils_AccentPredictor__
        if __Accent_Utils_AccentPredictor__ is None:

            clr.AddReference(self.source_path)
            import Accent.Utils
            __Accent_Utils_AccentPredictor__ = Accent.Utils.AccentPredictor(
                gram1Path=f"{self.data_set_dir}/news1gram.bin",
                gram2Path=f"{self.data_set_dir}/news2grams.bin",
                statisticPath=f"{self.data_set_dir}/_1Statistic.dat",
                replaceSpecialPath=f"{self.data_set_dir}/ReplaceSpecial.txt"
            )
        ret = __Accent_Utils_AccentPredictor__.PredictAccents(content)
        return ret.replace('\n',' ')