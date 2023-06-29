import pathlib
_wrking_dir_ = pathlib.Path(__file__).parent.parent.__str__()
import sys
sys.path.append(_wrking_dir_)
from cyx.media.pdf import PDFService
import cy_kit
instance =cy_kit.singleton(PDFService)
print(sys.modules[ instance.get_image.__module__])
