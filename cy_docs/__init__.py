import os.path
import pathlib
import typing

import bson
import pymongo.mongo_client
import ctypes
import sys
__release_mode__ = True
__working_dir__ = pathlib.Path(__file__).parent.__str__()




sys.path.append(__working_dir__)
import cy_docs_x

from typing import TypeVar, Generic, List

T = TypeVar('T')


def expr(cls: T) -> T:
    """
    Create mongodb build expression base on __cls__
    :param cls:
    :return:
    """
    ret = cy_docs_x.fields[cls]

    return ret
def get_doc(collection_name: str, client: pymongo.mongo_client.MongoClient, indexes: List[str] = [],
            unique_keys: List[str] = []):

    return getattr(cy_docs_x,"Document")(collection_name, client,indexes=indexes,unique_keys=unique_keys)
def define(name:str,indexes:List[str]=[],uniques:List[str]=[]):
    return getattr(cy_docs_x,"document_define")(name,indexes,uniques)
fields=cy_docs_x.fields
"""
For any expression
"""
def context(client, cls):
    return cy_docs_x.context(client,cls)

def concat(*args): return cy_docs_x.Funcs.concat(*args)
def exists(field):return cy_docs_x.Funcs.exists(field)
def is_null(field):return cy_docs_x.Funcs.is_null(field)
def is_not_null(field):return cy_docs_x.Funcs.is_not_null(field)
def not_exists(field):return cy_docs_x.Funcs.not_exists(field)

DocumentObject=cy_docs_x.DocumentObject


def file_get(client:pymongo.MongoClient, db_name:str, file_id):
    return cy_docs_x.file_get(client, db_name, file_id)


async def get_file_async(client, db_name, file_id):
    return await cy_docs_x.get_file_async(client,db_name,file_id)


def create_file(client:pymongo.MongoClient,db_name, file_name,content_type:str, chunk_size, file_size):
    return cy_docs_x.create_file(
        client=client,
        file_size=file_size,
        chunk_size=chunk_size,
        file_name=file_name,
        db_name=db_name,
        content_type=content_type
    )

def file_chunk_count(client :pymongo.MongoClient, db_name: str, file_id: bson.ObjectId)->int:
    return cy_docs_x.file_chunk_count(
        client=client,
        db_name=db_name,
        file_id=file_id
    )
def file_add_chunk(client :pymongo.MongoClient, db_name: str, file_id: bson.ObjectId,chunk_index:int, chunk_data: bytes):
    return cy_docs_x.file_add_chunk(
        client=client,
        db_name=db_name,
        file_id=file_id,
        chunk_index=chunk_index,
        chunk_data=chunk_data
    )
def file_add_chunks(client :pymongo.MongoClient, db_name: str, file_id: bson.ObjectId, data: bytes):
    return cy_docs_x.file_add_chunks(
        client=client,
        db_name=db_name,
        file_id=file_id,
        data=data
    )

def to_json_convertable(data,predict_content_handler=None):
    return cy_docs_x.to_json_convertable(data,predict_content_handler)


def file_get_iter_contents(client:pymongo.MongoClient, db_name:str, files_id:bson.ObjectId, from_chunk_index:int, num_of_chunks:int):
    return cy_docs_x.file_get_iter_contents(
        client=client,
        db_name=db_name,
        files_id=files_id,
        from_chunk_index_index= from_chunk_index,
        num_of_chunks=num_of_chunks
    )


def get_file_info_by_id(client, db_name, files_id):
    return cy_docs_x.get_file_info_by_id(
        client=client,
        db_name=db_name,
        files_id = files_id
    )
DocumentObject = cy_docs_x.DocumentObject


def create_empty_pydantic(_type):
    import pydantic

    ret = pydantic.BaseModel()
    for k,v in _type.__annotations__.items():
        if hasattr(v,"__args__") and isinstance(v.__args__,tuple) and len(v.__args__)==2 and v.__args__[1]== type(None):
            ret.__dict__[k] = None
        else:
            ret.__dict__[k] = v()
    return ret