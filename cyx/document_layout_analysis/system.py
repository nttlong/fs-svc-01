"""
Document layout analysis require a lot of settings at Operating System before it started
This package provides some functions to run at the end-point of thou's application.

Note!!!!!!:All functions in this package must be called at the most top of thou's application
Lưu ý!!!!!!: Tất cả các chức năng trong gói này phải được gọi ở đầu ứng dụng của bạn
-----------------------
Document layout analysis yêu cầu nhiều cài đặt tại Hệ điều hành trước khi bắt đầu
Gói này cung cấp một số chức năng để chạy ở end-point của ứng dụng của bạn.
Example :
import docment_layout_analysis
docment_layout_analysis.set_offline_dataset(true) # the dataset of AI is already in thou's OS
                                                  # OS needn't dowlnoad it from dataset hub
... any thou's source code star from here
if __name__=="__main__":
.....
"""
import os
import pathlib
import sys

__working_path__ = pathlib.Path(__file__).parent.parent.parent.__str__()
"""
The path to root directory of applcation
"""


def set_offline_dataset(is_offline: bool):
    """
    Set offline mode or online mode \n
    For offline mode: The system assume that: all necessary dataset is in thou's OS \n
    For online mode: Dataset synchronize  is always start whenever thou's application start \n
    --------------------------------------------------------------\n
    Đặt chế độ ngoại tuyến hoặc chế độ trực tuyến \n
    Đối với chế độ ngoại tuyến: Hệ thống giả định rằng: tất cả tập dữ liệu cần thiết đều có trong hệ điều hành của bạn \n
    Đối với chế độ trực tuyến: Đồng bộ hóa tập dữ liệu luôn bắt đầu bất cứ khi nào ứng dụng của bạn bắt đầu \n
    -------------------------------------- \n
    Note: this method was always called at the most-top of thou's application \n
    Lưu ý: Method này luôn được gọi ở đầu ứng dụng của bạn

    :param is_offline:
    :return:
    """
    if is_offline:
        os.environ["TRANSFORMERS_OFFLINE"] = "true"
        os.environ["HF_HUB_OFFLINE"] = "true"

    else:
        os.environ["TRANSFORMERS_OFFLINE"] = "false"
        os.environ["HF_HUB_OFFLINE"] = "false"


def set_dataset_path(abs_or_relative_path: str):
    """
    AI or deep-learning framework required dataset in thou's application. \n
    In the most case, the dataset will get from somewhere in dataset-hub on Internet and reuse on the next time. \n
    The method will tell Document layout analysis that dataset locates at "abs_or_relative_path" \n
    if "abs_or_relative_path" start with "./" . That means "abs_or_relative_path" is relative path from "__working_path__" \n
    The other case is always absolute path in thou's OS \n
    ----------------------------------------------------- \n
    Bộ dữ liệu yêu cầu AI hoặc khung học sâu trong ứng dụng của bạn. \n
    Trong hầu hết các trường hợp, tập dữ liệu sẽ lấy từ một nơi nào đó trong trung tâm tập dữ liệu trên Internet và sử dụng lại vào lần tiếp theo.\n
    Phương pháp này sẽ báo cáo phân tích bố cục Tài liệu rằng tập dữ liệu nằm ở "abs_or_relative_path" \n
    nếu "abs_or_relative_path" bắt đầu bằng "./" . Điều đó có nghĩa là "abs_or_relative_path" là đường dẫn tương đối từ "__working_path__" \n
    Trường hợp khác luôn là đường dẫn tuyệt đối trong hệ điều hành của bạn \n
    :param abs_or_relative_path:
    :return:
    """
    global __working_path__
    full_path_to_data_set = abs_or_relative_path
    if abs_or_relative_path[0:2] =="./":
        """
        if start with "./" -> relative path
        """
        full_path_to_data_set = os.path.abspath(
            os.path.join(__working_path__,abs_or_relative_path[2:])
        )
    doctr_path = os.path.abspath(
        os.path.join(full_path_to_data_set,"doctr")
    )
    if not os.path.isdir(doctr_path):
        """
        if not exist "doctr_path" create it
        """
        os.makedirs(doctr_path,exist_ok=True)
    os.environ["XDG_CACHE_HOME"] = full_path_to_data_set
    os.environ["DOCTR_CACHE_DIR"] = doctr_path
