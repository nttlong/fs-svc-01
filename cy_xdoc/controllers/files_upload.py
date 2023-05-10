import mimetypes

import humanize

import cy_docs
import cy_web
import cyx.common.msg
from cy_xdoc.auths import Authenticate
from fastapi import Depends, UploadFile
from cy_xdoc.controllers.models.file_upload import UploadFilesChunkInfoResult
import cy_kit
from cy_xdoc.services.files import FileServices
from cyx.common.file_storage import FileStorageService
from cyx.common.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.temp_file import TempFiles
from cyx.common.brokers import Broker

@cy_web.hanlder("post", "{app_name}/files/upload")
def files_upload(app_name: str, UploadId: str, Index: int, FilePart: UploadFile,
                 token=Depends(Authenticate)) -> UploadFilesChunkInfoResult:
    # from cy_xdoc.controllers.apps import check_app
    # check_app(app_name)
    content_part = FilePart.file.read()
    file_service: FileServices = cy_kit.singleton(FileServices)
    file_storage_service: FileStorageService = cy_kit.singleton(FileStorageService)
    msg_service: MessageService = cy_kit.singleton(MessageService)
    broker:Broker = cy_kit.singleton(Broker)
    temp_files = cy_kit.singleton(TempFiles)

    upload_item = file_service.get_upload_register(app_name, upload_id=UploadId)
    if upload_item is None:
        del FilePart
        del content_part
        return cy_docs.DocumentObject(
            Error=dict(
                Message="Upload was not found or has been remove",
                Code="ItemWasNotFound"

            )
        ).to_pydantic()
    upload_register_doc = file_service.db_connect.db(app_name).doc(DocUploadRegister)
    file_size = upload_item.SizeInBytes
    # path_to_broker_share = os.path.join(path_to_broker_share,f"{UploadId}.{upload_item.get(docs.Files.FileExt.__name__)}")
    size_uploaded = upload_item.SizeUploaded or 0
    num_of_chunks_complete = upload_item.NumOfChunksCompleted or 0
    nun_of_chunks = upload_item.NumOfChunks or 0
    main_file_id = upload_item.MainFileId
    chunk_size_in_bytes = upload_item.ChunkSizeInBytes or 0
    server_file_name = upload_item.FullFileNameLower
    content_type, _ = mimetypes.guess_type(server_file_name)

    if num_of_chunks_complete == 0:
        fs = file_storage_service.create(
            app_name=app_name,
            rel_file_path=server_file_name,
            chunk_size=chunk_size_in_bytes,
            content_type=content_type,
            size=file_size)
        fs.push(content_part, Index)
        upload_item.MainFileId = fs.get_id()
        if not temp_files.is_use:
            msg_service.emit(
                app_name=app_name,
                message_type="files.upload",
                data=upload_item
            )
        else:
            temp_files.push(
                app_name=app_name,
                content=content_part,
                upload_id=UploadId,
                file_ext=upload_item[upload_register_doc.fields.FileExt]
            )
    else:
        fs = file_storage_service.get_file_by_name(
            app_name=app_name,
            rel_file_path=server_file_name
        )
        fs.push(content_part, Index)
        if temp_files.is_use:
            temp_files.push(
                app_name=app_name,
                content=content_part,
                upload_id=UploadId,
                file_ext=upload_item[upload_register_doc.fields.FileExt]
            )
    if num_of_chunks_complete == nun_of_chunks - 1 and temp_files.is_use:
        try:
            upload_item["Status"] = 1
            file_service.search_engine.update_content(
                app_name = app_name,
                id = UploadId,
                content= "",
                data_item= upload_item


            )
            try:
                broker.emit(
                    app_name=app_name,
                    message_type=cyx.common.msg.MSG_FILE_UPLOAD,
                    data=upload_item
                )
                print(f"rais msg {cyx.common.msg.MSG_FILE_UPLOAD}")
            except Exception as e:
                print(e)

        except Exception as e:
            raise e
            print(e)

    size_uploaded += len(content_part)
    ret = cy_docs.DocumentObject()
    ret.Data = cy_docs.DocumentObject()
    ret.Data.Percent = round((size_uploaded * 100) / file_size, 2)
    ret.Data.SizeUploadedInHumanReadable = humanize.filesize.naturalsize(size_uploaded)
    num_of_chunks_complete += 1
    ret.Data.NumOfChunksCompleted = num_of_chunks_complete
    ret.Data.SizeInHumanReadable = humanize.filesize.naturalsize(file_size)
    status = 0
    if num_of_chunks_complete == nun_of_chunks:
        status = 1

    file_controller_type = cy_kit.get_runtime_type(file_storage_service)
    file_controller = None
    if file_controller_type:
        file_controller = f"{file_controller_type.__module__}:{file_controller_type.__name__}"
    upload_register_doc.context.update(
        upload_register_doc.fields.Id == UploadId,
        upload_register_doc.fields.SizeUploaded << size_uploaded,
        upload_register_doc.fields.NumOfChunksCompleted << num_of_chunks_complete,
        upload_register_doc.fields.Status << status,
        upload_register_doc.fields.MainFileId << fs.get_id(),
        upload_register_doc.fields.FileModuleController << file_controller

    )


    del FilePart
    return ret.to_pydantic()
