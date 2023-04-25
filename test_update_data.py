import cy_kit
from cy_xdoc.services.files import FileServices
uploads = cy_kit.singleton(FileServices)

qr =uploads.get_queryable_doc(app_name="hps-file-test")

items = qr.context.update(qr.fields.IsPublic==False,qr.fields.IsPublic<<True)
for x in items:
    print(x)
