from __future__ import annotations

import contextlib
import json
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, overload

import FileSystem as FS

FILE_PATH = FS.SAVE_FILE

_save_dict = False

class NotFound(Exception):
    def __init__(self, name: str):
        super().__init__(f"'{name}' not found")

class Found(Exception):
    def __init__(self, name: str):
        super().__init__(f"'{name}' already exists")


class AutoSaveDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, item in self.items():
            if isinstance(item, dict):
                self[key] = AutoSaveDict(item)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        ret = super().__setitem__(__key, __value)
        self._save_contents()
        return ret

    def __delitem__(self, __key: Any) -> None:
        ret = super().__delitem__(__key)
        self._save_contents()
        return ret

    def _save_contents(self) -> None:
        if not _save_dict:
            return
        with contextlib.suppress(NameError):
            _contents["settings"] = _settings
            _contents["data"] = _groups
            with open(FILE_PATH, 'w') as f:
                json.dump(_contents, f, indent=4)


def _get_data() -> Dict[Literal["settings", "data"], Dict[str, Dict]]:
    try:
        if not FS.exists(FILE_PATH):
            raise FileNotFoundError
        with open(FILE_PATH, 'r') as f:
            contents = json.load(f)
            if "settings" not in contents or "data" not in contents:
                raise KeyError
            return contents
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        FS.create_save_file()
        return _get_data()


_contents = _get_data()
_settings = AutoSaveDict(_contents["settings"])
_groups: Dict[str, Dict[str, Dict[str, str]]] = AutoSaveDict(_contents["data"])
_save_dict = True


#  region overloades
@overload
def get_name_list() -> List[str]: ...
@overload
def get_name_list(group_name: str) -> List[str]: ...

@overload
def length() -> int: ...
@overload
def length(group_name: str) -> int: ...

@overload
def order_number(group_name: str) -> int: ...
@overload
def order_number(group_name: str, number: int) -> None: ...
@overload
def order_number(group_name: str, task_name: str) -> int: ...
@overload
def order_number(group_name: str, task_name: str, number: int) -> None: ...

@overload
def is_exist(group_name: str) -> bool: ...
@overload
def is_exist(group_name: str, task_name: str) -> bool: ...

@overload
def task_property(group_name: str, task_name: str, property: Literal["button_text", "url", "file_path"]) -> Any: ...
@overload
def task_property(group_name: str, task_name: str, property: Literal["button_text", "url", "file_path"], value: Any = None) -> None: ...

@overload
def setting(name: str) -> Any: ...
@overload
def setting(name: str, value: Any) -> None: ...
# endregion


def add_group(group_name: str) -> None:
    global _groups
    if group_name in _groups:
        raise Found(group_name)
    _groups[group_name] = AutoSaveDict()

def delete_group(group_name: str) -> None:
    global _groups
    if group_name not in _groups:
        raise NotFound(group_name)
    del _groups[group_name]

def edit_group(group_name: str, *,
               new_group_name: Optional[str] = None,
               new_group_data: Optional[dict] = None) -> None:
    global _groups
    if group_name not in _groups:
        raise NotFound(group_name)
    data = _groups[group_name]
    name = new_group_name if new_group_name is not None else group_name
    if new_group_data is not None:
        data = AutoSaveDict(new_group_data)
    old_groups: dict = _groups
    _groups = AutoSaveDict()
    for _group_name, _data in old_groups.items():
        if group_name == _group_name:
            _groups[name] = data
            continue
        _groups[_group_name] = _data

def add_task(group_name: str, task_name: str) -> None:
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_name not in _groups[group_name]:
        _groups[group_name][task_name] = AutoSaveDict()
    else:
        Found(task_name)

def delete_task(group_name: str, task_name: str) -> None:
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_name not in _groups[group_name]:
        raise NotFound(task_name)
    del _groups[group_name][task_name]

def edit_task(group_name: str, task_name: str, *,
              new_task_name: Optional[str] = None,
              new_task_data: Optional[dict] = None) -> None:
    global _groups
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_name not in _groups[group_name]:
        raise NotFound(task_name)
    data = _groups[group_name][task_name]
    name = new_task_name if new_task_name is not None else task_name
    if new_task_data is not None:
        data = AutoSaveDict(new_task_data)
    old_tasks: dict = _groups[group_name]
    tasks = AutoSaveDict()
    for _task, _data in old_tasks.items():
        if task_name == _task:
            tasks[name] = data
            continue
        tasks[_task] = _data
    _groups[group_name] = tasks

def task_property(group_name: str, task_name: str,
                  property: str, value: Optional[Any] = None) -> Optional[Any]:
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_name not in _groups[group_name]:
        raise NotFound(task_name)
    if value is not None:
        _groups[group_name][task_name][property] = value
    elif property in _groups[group_name][task_name]:
        return _groups[group_name][task_name][property]
    else:
        raise NotFound(property)

def get_name_list(group_name: Optional[str] = None) -> List[str]:
    if group_name is None:
        return list(_groups.keys())
    elif group_name not in _groups:
        raise NotFound(group_name)
    else:
        return list(_groups[group_name].keys())

def length(group_name: Optional[str] = None) -> int:
    if group_name is None:
        return len(_groups)
    elif group_name not in _groups:
        raise NotFound(group_name)
    else:
        return len(_groups[group_name])

def order_number(group_name: str, task_name: Optional[str] = None,
                 number: Optional[int] = None) -> Optional[int]:
    global _groups
    if group_name not in _groups:
        raise NotFound(group_name)
    if isinstance(task_name, str) and task_name not in _groups[group_name]:
        raise NotFound(task_name)
    
    match group_name, task_name, number:
        case str(), None, None:
            return list(_groups).index(group_name)
        case str(), str(), None:
            return list(_groups[group_name]).index(task_name)
        
        case str(), int() as number, None:
            old_groups: dict = dict(_groups)
            data = old_groups.pop(group_name)
            _groups = AutoSaveDict()
            for index, (_group_name, _data) in enumerate(old_groups.items()):
                if index == number:
                    _groups[group_name] = data
                _groups[_group_name] = _data
                
        case str(), str(), int():
            old_tasks: dict = dict(_groups[group_name])
            data = old_tasks.pop(task_name)
            tasks = AutoSaveDict()
            for index, (_task_name, _data) in enumerate(_groups[group_name].items()):
                if index == number:
                    tasks[task_name] = data
                tasks[_task_name] = _data
            _groups[group_name] = tasks

def is_exist(group_name: str, task_name: Optional[str] = None) -> bool:
    if task_name is None:
        return group_name in _groups
    elif group_name not in _groups:
        raise NotFound(group_name)
    else:
        return task_name in _groups[group_name]

def setting(name: str, value: Optional[Any] = None) -> Optional[Any]:
    if value is None:
        if name not in _settings:
            raise NotFound(name)
        return _settings[name]
    else:
        _settings[name] = value

def delete_setting(name: str) -> None:
    if name not in _settings:
        raise NotFound(name)
    del _settings[name]


# for testing purposes
if __name__ == '__main__':
    add_group("group 1")
    add_group("group 2")
    add_group("group 3")
    add_group("group 4")
    delete_group("group 1")
    edit_group("group 2", new_group_name="group 1")
    edit_group("group 3", new_group_name="group 5")
    edit_group("group 1", new_group_data={"None": "None"})

    try: add_task("group 3", "task 1")
    except NotFound as e: print(e)
    add_task("group 1", "task 1")
    add_task("group 1", "task 2")
    add_task("group 1", "task 3")
    delete_task("group 1", "task 1")
    edit_task("group 1", "task 2", new_task_name="task 1", new_task_data={"None": "None"})
    edit_task("group 1", "task 1", new_task_data={"Name": "Nothing"})

    task_property("group 1", "task 1", "text", "description")
    task_property("group 1", "task 1", "text")

    n = order_number("group 1")
    n = order_number("group 1", "task 1")
    order_number("group 5", 1)
    order_number("group 1", "task 3", 0)

    x = get_name_list()
    x = get_name_list("group 1")

    l = length()
    l = length("group 1")

    e = is_exist("group 1")
    e = is_exist("group 2")
    e = is_exist("group 1", "task 1")
    e = is_exist("group 1", "task 2")

    setting("position", [5, 5])
    s = setting("position")

    delete_group("group 1")
    delete_group("group 4")
    delete_group("group 5")
    delete_setting("position")