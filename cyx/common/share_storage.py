
class ShareStorageService:
    def __init__(self):
        from cyx.common import config
        import pathlib
        import os
        self.config = config
        self.__shared_storage__ = None
        self.__app_dir__ = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.__shared_storage__ = self.config.shared_storage
        if self.__shared_storage__[0:2]=="./":
            self.__shared_storage__ = os.path.abspath(
                os.path.join(self.__app_dir__,self.__shared_storage__[2:])
            )


    def get_root(self)->str:
        import os
        return self.__shared_storage__