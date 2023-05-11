from typing import overload, Optional
from functools import singledispatchmethod


# class A:
#     def __init__(self):
#         self._group = 0
    
#     @singledispatchmethod
#     def group(self, group_name: str) -> str:
#         if group_name is not None:
#             self._group = group_name
#         return self._group
    
#     @singledispatchmethod.register
#     def group(self) -> str:
#         print("Getting group name")
        
#     @singledispatchmethod.register
#     def group(self, group_name: str = None) -> None:
#         print("Renaming group")


# @overload
# def func():
#     print('calling function')

# @overload
# def func(name: str):
#     print('getting function')
    
# def func(name: str = None):
#     print(name)


# if __name__ == "__main__":
#     func()
#     func("name")
    
#     a = A()
#     a.group("New name")
#     a.group()


class MyClass:
    def __init__(self):
        self._group_name = None
        self._task_name = None
        self._name = None
        self._text = None
        self._button_text = None
        self._url = None
        self._file = None
        

    @overload
    def group_name(self) -> str: pass
    @overload
    def group_name(self, group_name: str) -> None: pass
    
    @overload
    def task_name(self) -> str: pass
    @overload
    def task_name(self, task_name: str) -> None: pass
    
    @overload
    def name(self) -> str: pass
    @overload
    def name(self, name: str) -> None: pass
    
    @overload
    def text(self) -> str: pass
    @overload
    def text(self, text: str) -> None: pass
    
    @overload
    def button_text(self) -> str: pass
    @overload
    def button_text(self, button_text: str) -> None: pass
    
    @overload
    def url(self) -> str: pass
    @overload
    def url(self, url: str) -> None: pass
    
    @overload
    def file(self) -> str: pass
    @overload
    def file(self, file_path: str) -> None: pass
    
    
mc = MyClass()
mc.name()
mc.name("file")