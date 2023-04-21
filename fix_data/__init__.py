from cyx.common import config
import cy_docs
import cy_kit
from  cy_xdoc.services.files import FileServices
fs = cy_kit.singleton(FileServices)
fs.get_list(
    app_name="hps-file-test"
)