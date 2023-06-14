import cy_docs
import cy_es
from elasticsearch.client import Elasticsearch
from  pymongo.mongo_client import  MongoClient
import cy_kit
from cy_xdoc.services.apps import AppServices
from cy_xdoc.models.apps import App
from cy_xdoc.models.files import DocUploadRegister
from cyx.base import DbConnect

source_client = Elasticsearch(
    "http://192.168.18.36:9200"
)
dest_client = Elasticsearch(
    "http://172.16.0.242:9200"
)
info = cy_es.get_info(source_client)
dest_client.create(
    index = "lv-codx_lv-docs",
    doc_type = "_doc",
    id="1223",
    body = dict(xx="OK")
)
mongodb_source_client = MongoClient(
    host="192.168.18.36",
    port=27018,
    authSource='lv-docs',
    username='admin-doc',
    password='123456'
)

# mongodb_dest_client = MongoClient(
#     host= "192.168.18.36",
#     port= 27017,
#     authSource= 'lv - docs',
#     username = 'admin-doc',
#     password = '123456'
# )
source_app_docs = cy_docs.queryable_doc(mongodb_source_client,"lv-docs",App)

list_of_apps = source_app_docs.context.aggregate().project(
    source_app_docs.fields.Name
)
app_names  = [x.Name for x in list_of_apps]
print(app_names)
print(f"Connect... to {'http://192.168.18.36:9200'} ")
if not source_client.ping():
    print(f"Connection to {'http://192.168.18.36:9200'} failed")
else:
    print(f"Connection to {'http://192.168.18.36:9200'} is ok")
print(f"Connect... to {'http://172.16.0.242:9200'} ")
if not dest_client.ping():
    print(f"Connection to {'http://172.16.0.242:9200'} failed")
else:
    print(f"Connection to {'http://172.16.0.242:9200'} is ok")
for x in app_names:
    index_name = f"lv-codx_{x}"
    if not cy_es.cy_es_x.is_index_exist(client =dest_client,index=index_name):
        # print(f"delete index {index_name} ...")
        # cy_es.delete_index(client=dest_client, index=index_name)
        # print(f"Delete index {index_name} is ok")
        print(f"Create index {index_name} ...")
        cy_es.create_index(client =dest_client,index=index_name)
        print(f"Created index {index_name} is ok")
@cy_kit.loop_process(app_names)
def run(app_name:str):
    source_file_docs = cy_docs.queryable_doc(mongodb_source_client, app_name, DocUploadRegister)
    upload_agg = source_file_docs.context.aggregate().project(
        cy_docs.fields._id
    )
    lst = list(upload_agg)
    for x in lst:
        print(f"{app_name} \t\t\t {x._id}")

    return {
        app_name: [x._id for x in lst]
    }

upload_apps = run()

@cy_kit.loop_process(upload_apps)
def move_dat(upload_app:dict):
    app_name = list(upload_app.keys())[0]
    index_name = f"lv-codx_{app_name}"
    for x in upload_app[app_name]:
        es_doc =cy_es.get_doc(source_client,index_name,x)
        print(es_doc.doc_type)
        if es_doc:
            if not dest_client.exists(index=index_name, id=es_doc.id,doc_type="_doc"):
                cy_es.create_doc(dest_client,index_name,id = es_doc.id,body=es_doc.source.to_dict())
                print(f"{index_name} \t\t\t {es_doc.id} was create")
            else:
                print(f"{index_name} \t\t\t {es_doc.id} is already")
        cy_kit.clean_up()
move_dat()

"""
curl -X POST -H "Content-Type: application/json" -H "Cache-Control: no-cache" -d '{
"user" : "Arun Thundyill Saseendran",
"post_date" : "2009-03-23T12:30:00",
"message" : "trying out Elasticsearch"
}' "http://172.16.0.242:9200/lv-codx_lv-docs/sampletype/"


"""
"""
curl -X PUT -H "Content-Type: application/json" -H "Cache-Control: no-cache" -d '{
"user" : "Arun Thundyill Saseendran",
"post_date" : "2009-03-23T12:30:00",
"message" : "trying out Elasticsearch"
}' "http://172.16.0.242:9200/lv-codx_lv-docs/_doc/xxxx/_create"


"""
#curl -H "Content-Type: application/json" -XPOST "http://localhost:9200/indexname/typename/optionalUniqueId" -d "{ \"field\" : \"value\"}"