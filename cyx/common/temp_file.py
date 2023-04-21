import os
import pathlib
import shutil

import gridfs.errors

import cy_kit
import cyx.common


class TempFiles:

    def __init__(self):
        from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
        from cy_xdoc.services.files import FileServices

        self.file_storage = cy_kit.singleton(MongoDbFileService)
        self.files_services = cy_kit.singleton(FileServices)
        self.config = cyx.common.config
        if self.config.get("temp_directory") is None or self.config.get("temp_directory") == '':
            self.__is_use__ = False
            print(f" warning temp_directory was not set")
            return
        self.__tem_path__: str = self.config.temp_directory
        if self.__tem_path__.startswith("./"):
            self.__tem_path__ = os.path.abspath(
                os.path.join(pathlib.Path(__file__).parent.parent.parent.__str__(), self.__tem_path__[2:]))
            if not os.path.isdir(self.__tem_path__):
                os.makedirs(self.__tem_path__, exist_ok=True)
        self.__is_use__ = True

    @property
    def is_use(self) -> bool:
        return self.__is_use__

    @property
    def path(self):
        return self.__tem_path__

    def push(self, upload_id: str, app_name: str, file_ext: str, content: bytes):
        full_path = self.get_path(app_name, upload_id, file_ext)
        if not os.path.isfile(full_path):
            with open(full_path, "wb") as f:
                f.write(content)
        else:
            with open(full_path, "ab") as f:
                f.write(content)
    def get_root_dir(self)->str:
        return self.__tem_path__
    def get_path(self, app_name, upload_id, file_ext) -> str:
        import gridfs.errors
        app_dir = os.path.join(self.__tem_path__, app_name)
        if not os.path.isdir(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        ret = os.path.join(app_dir, f"{upload_id}.{file_ext}")
        if not os.path.isfile(ret):
            try:
                fs = self.files_services.get_main_file_of_upload(
                    app_name=app_name,
                    upload_id=upload_id
                )
                if fs is not None:
                    with open(ret,'wb') as f:
                        data = fs.read(fs.get_size())
                        f.write(data)
            except gridfs.errors.CorruptGridFile as e:
                return None



        return ret

    def move_file(self, from_file: str, app_name: str, sub_dir: str):
        app_dir = os.path.join(self.__tem_path__, app_name)
        if not os.path.isdir(app_dir):
            os.makedirs(app_dir, exist_ok=True)
        full_sub_dir = os.path.join(app_dir, sub_dir)
        if not os.path.isdir(full_sub_dir):
            os.makedirs(full_sub_dir, exist_ok=True)
        file_name = pathlib.Path(from_file).name
        file_ext = os.path.splitext(file_name)[1]
        ret = os.path.join(full_sub_dir, f"{file_name}")
        shutil.move(
            src=from_file,
            dst=ret
        )
        return ret
