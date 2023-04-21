import pathlib
import sys
import time

wk = pathlib.Path(__file__).parent.parent.__str__()
sys.path.append(wk)
import cy_kit
from  cy_xdoc.services.files import FileServices
from cyx.common.msg import MessageService
from cyx.common.rabitmq_message import RabitmqMsg
fs = cy_kit.singleton(FileServices)
docs =fs.get_queryable_doc(
    app_name="hps-file-test"
)
ls = docs.context.aggregate().sort(
    docs.fields.RegisterOn.desc()
).limit(100000)
cy_kit.config_provider(
    from_class=MessageService,
    implement_class=RabitmqMsg
)
msg_service = cy_kit.singleton(RabitmqMsg)
count =0
for x in ls:

    try:
        msg_service.emit(
            app_name="hps-file-test",
            message_type="files.upload",
            data=x
        )
        count+=1
        print(count)
        time.sleep(3)
    except Exception as e:
        print(e)
        time.sleep(3*60)
