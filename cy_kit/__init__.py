"""
The library support real useful the way one Class create an instance.\n
The methods list:\n
-----------------------------------------------------------------------------------------------------------\n
| method                    |   description  \n
|__________________________________________________________________________________________________________ \n
| single                    |   Create single instance of Class \n
|                           |   Examaple: ClassA()==ClassA() // is always True \n
|                           |   That means. If thou called thousand time Initialize of Class just only one \n
|                           |     instance create \n
|__________________________________________________________________________________________________________ \n
| instance                  | Create instance of Class \n
|                           | instance: ClassA() == ClassB() // is always false. \n
|                           | That mean everytime thou call Initialize of Class, \n
|                           |     the new instance will create \n
|_____________________________________________________________________________________________________________ \n

The most importance method in the library is "config_provider"
Thou could make several Class with the same in the both method name and args, but difference Implementation of Method.
Then thou can  one of those Class in runtime.
Example:
    class A:
        def hello():
            print ('Hello my name is "A"')
    class B:
        def hello():
            print ('Hello my name is "B"')
    the first code bellow:
        a = cy_kit.single(A)
        a.hello() // thou will see Hello my name is "A"
    the second code bellow
        cy_kit.config_provider(
            from_class=A,
            implement_class = A

        )
        a = cy_kit.single(A)
        a.hello() // thou will see Hello my name is "B"


The purpose of config_provider is help thou needn't re-modify thou's source code, just define a new class and
implement all methods by another way


Thư viện hỗ trợ thực sự hữu ích theo cách mà một Lớp tạo một thể hiện.\n
Danh sách phương pháp:\n
-------------------------------------------------- -------------------------------------------------- -------\N
| phương pháp | mô tả \n
|_____________________________________________________________________________________________________________________________ \n
| độc thân | Tạo một phiên bản duy nhất của Lớp \n
| | Ví dụ: ClassA()==ClassA() // luôn đúng \n
| | Điều đó có nghĩa là. Nếu bạn đã gọi hàng nghìn lần Khởi tạo lớp chỉ một \n
| | tạo ví dụ \n
|_____________________________________________________________________________________________________________________________ \n
| ví dụ | Tạo phiên bản của Lớp \n
| | ví dụ: ClassA() == ClassB() // luôn sai. \N
| | Điều đó có nghĩa là mỗi khi bạn gọi Khởi tạo lớp, \n
| | phiên bản mới sẽ tạo \n
|________________________________________________________________________________________________________________________________ \n

Phương pháp quan trọng nhất trong thư viện là "config_provider"
Bạn có thể tạo một số Lớp giống nhau ở cả tên phương thức và đối số, nhưng sự khác biệt về Thực hiện Phương thức.
Sau đó, bạn có thể sử dụng một trong những Lớp đó trong thời gian chạy.
Ví dụ:
    hạng A:
        chắc chắn xin chào():
            print('Xin chào, tên tôi là "A"')
    lớp B:
        chắc chắn xin chào():
            print('Xin chào, tên tôi là "B"')
    mã đầu tiên dưới đây:
        a = cy_kit.single(A)
        a.hello() // bạn sẽ thấy Xin chào tên tôi là "A"
    mã thứ hai dưới đây
        cy_kit.config_provider(
            from_class=A,
            thực hiện_class = A

        )
        a = cy_kit.single(A)
        a.hello() // bạn sẽ thấy Xin chào tên tôi là "B"


Mục đích của config_provider là giúp bạn không cần sửa đổi lại mã nguồn của mình, chỉ cần định nghĩa một lớp mới và
thực hiện tất cả các phương pháp bằng cách khác

"""
import os.path
import pathlib
import sys
from typing import TypeVar

__working_dir__ = pathlib.Path(__file__).parent.__str__()

import cy_kit

sys.path.append(__working_dir__)

import cy_kit_x

container = cy_kit_x.container

T = TypeVar('T')


def single(cls: T) -> T:
    return cy_kit_x.resolve_singleton(cls)


def instance(cls: T) -> T:
    return cy_kit_x.resolve_scope(cls)


def config_provider(from_class: type, implement_class: type):
    cy_kit_x.config_provider(from_class, implement_class)

from typing import Generic

# class Provider(Generic[T]):
#     def __init__(self,__cls__:type):
#         self.__cls__=__cls__
#         self.__ins__ =None
#     @property
#     def instance(self)->T:
#         if self.__ins__  is None:
#             self.__ins__ = cy_kit_x.provider(self.__cls__)
#         return self.__ins__




def provider(cls: T) -> T:
    return cy_kit_x.provider(cls)


def check_implement(from_class: type, implement_class: T) -> T:
    cy_kit_x.check_implement(from_class, implement_class)
    return implement_class


def must_imlement(interface_class: type):
    return cy_kit_x.must_implement(interface_class)

def trip_content(data):
    if isinstance(data,dict):
        for k,v in data.items():
            if isinstance(v,str):
                data[k]=v.rstrip(' ').lstrip(' ')
            elif isinstance(v,dict):
                data[k] = trip_content(v)
    return data
def yaml_config(path: str, apply_sys_args: bool = True):
    ret = cy_kit_x.yaml_config(path, apply_sys_args)
    if hasattr(cy_kit_x,"trip_content"):
        ret = cy_kit_x.trip_content(ret)
    else:
        ret = trip_content(ret)
    return ret


def combine_agruments(data):
    ret = cy_kit_x.combine_agruments(data)
    if hasattr(cy_kit_x,"trip_content"):
        ret = cy_kit_x.trip_content(ret)
    else:
        ret = trip_content(ret)
    return ret



def inject(cls:T)->T:
    return cy_kit_x.inject(cls)
def singleton(cls:T)->T:
    return cy_kit_x.singleton(cls)
def scope(cls:T)->T:
    return cy_kit_x.scope(cls)


def thread_makeup():
    return cy_kit_x.thread_makeup()
def get_local_host_ip():
    return cy_kit_x.get_local_host_ip()


def create_logs(log_dir:str, name:str):
    return cy_kit_x.create_logs(log_dir,name)


def get_runtime_type(injector_instance):
    return cy_kit_x.get_runtime_type(injector_instance)


def singleton_from_path(injector_path:str):
    """

    :param injector_path: <module>:<class name>
    :return:
    """
    return cy_kit_x.singleton_from_path(injector_path)


def to_json(data):
    return cy_kit_x.to_json(data)
def clean_up():
    try:
        cy_kit_x.clean_up()
    except Exception as e:
        pass
Graceful_Application = cy_kit_x.Graceful_Application