import cy_kit
from cy_xdoc.services.files import FileServices
uploads = cy_kit.singleton(FileServices)

qr =uploads.get_queryable_doc(app_name="lv-docs")
items = qr.context.update(qr.fields.IsPublic==True,qr.fields.IsPublic<<False)
for x in items:
    print(x)
