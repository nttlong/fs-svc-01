import pathlib
import shutil

from cyx.common.base import config
import subprocess
import uuid
import os

class LibreOfficeService:
    def __init__(self):
        self.config = config
        self.libre_office_path = self.config.libre_office_path
        self.working_dir = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.temp_dir = os.path.join(self.working_dir,"tmp","libre-office")
        if not os.path.isdir(self.temp_dir):
            os.makedirs(self.temp_dir,exist_ok=True)
        self.user_profile_dir = os.path.join(self.temp_dir,"users-profiles")
        if not os.path.isdir(self.user_profile_dir):
            os.makedirs(self.user_profile_dir,exist_ok=True)
        self.output_dir = os.path.join(self.temp_dir,"out-put")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir,exist_ok=True)

    def get_image(self, file_path)->str:
        filename_only = pathlib.Path(file_path).stem
        ret_file = os.path.join(self.output_dir, f"{filename_only}.png")
        if os.path.isfile(ret_file):
            return ret_file

        uno = f"Negotiate=0,ForceSynchronous=1;"
        # from subprocess import CREATE_NEW_CONSOLE

        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(self.user_profile_dir, user_profile_id)

        pid = subprocess.Popen(
            [
                self.libre_office_path,
                '--headless',
                '--convert-to', 'png',
                f"--accept={uno}",
                f"-env:UserInstallation=file://{full_user_profile_path.replace(os.sep, '/')}",
                '--outdir',
                self.output_dir, file_path
            ],
            shell=False,
            start_new_session=True
            # creationflags=16
        )
        ret = pid.wait()  # Đợi


        return ret_file
