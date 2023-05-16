from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional, overload

import FileSystem as FS

FILE_PATH = FS.SAVE_FILE
GROUP_ID_DELIMITER = '#'

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
        self._save_data()
        return ret

    def __delitem__(self, __key: Any) -> None:
        ret = super().__delitem__(__key)
        self._save_data()
        return ret

    def _save_data(self) -> None:
        if not _save_dict:
            return
        _contents["settings"] = _settings
        _contents["data"] = _groups
        with open(FILE_PATH, 'w') as f:
            json.dump(_contents, f, indent=4)


def _load_data() -> Dict[Literal["settings", "data"], Dict[str, Dict]]:
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
        return _load_data()


_contents = _load_data()
_settings = AutoSaveDict(_contents["settings"])
_groups: Dict[str, Dict[str, Dict[str, str]]] = AutoSaveDict(_contents["data"])
_save_dict = True


#  region overloades
@overload
def get_list() -> List[str]: ...
@overload
def get_list(group_name: str) -> List[str]: ...

@overload
def length() -> int: ...
@overload
def length(group_name: str) -> int: ...

@overload
def order_number(group_name: str) -> int: ...
@overload
def order_number(group_name: str, number: int) -> None: ...
@overload
def order_number(group_name: str, task_id: str) -> int: ...
@overload
def order_number(group_name: str, task_id: str, number: int) -> None: ...

@overload
def is_exist(group_name: str) -> bool: ...
@overload
def is_exist(group_name: str, task_id: str) -> bool: ...

@overload
def task_property(group_name: str, task_id: str, property: Literal["button_text", "url", "file_path"]) -> Any: ...
@overload
def task_property(group_name: str, task_id: str, property: Literal["button_text", "url", "file_path"], value: Any = None) -> None: ...

@overload
def setting(name: str) -> Any: ...
@overload
def setting(name: str, value: Any) -> None: ...
# endregion

def _make_unique_id(group_name):
    ids = []
    for group in _groups:
        if remove_group_id(group) == group_name:
            # Get all group ids with the same name in `ids`
            ids.append(get_group_id(group))
    if ids:
        # If groups with same name exists, add 1 to the last's id
        return ids[-1] + 1
    # No groups with same name found so we give `0` for id
    return 0

def get_group_id(group_name: str, id_delimiter: str = GROUP_ID_DELIMITER) -> int:
    return int(group_name[group_name.rfind(id_delimiter) + 1])

def remove_group_id(group_name: str, id_delimiter: str = GROUP_ID_DELIMITER) -> str:
    if id_delimiter in group_name:
        return group_name[:group_name.rfind(id_delimiter)]
    return group_name

def give_group_id(group_name: str) -> str:
    found = 0
    for group in _groups:
        if group_name == remove_group_id(group):
            found += 1
    return f"{group_name}#{_make_unique_id(group_name)}"

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

def add_task(group_name: str, task_name: str) -> int:
    """Add a task to the group given. return the task id."""
    if group_name not in _groups:
        raise NotFound(group_name)
    # task_{len(_groups[group_name])}, where len(_groups[group_name]) retrieves the number of
    # tasks already stored in the group and increments it by 1 to assign a new number to the new task.
    add = 0
    while (task_id := f"task_{len(_groups[group_name]) + add}") in _groups[group_name]:
        add += 1
    _groups[group_name][task_id] = AutoSaveDict({"task_name": task_name})
    return task_id

def delete_task(group_name: str, task_id: str) -> None:
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_id not in _groups[group_name]:
        raise NotFound(task_id)
    del _groups[group_name][task_id]

def edit_task(group_name: str, task_id: str,
              new_task_data: dict) -> None:
    global _groups
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_id not in _groups[group_name]:
        raise NotFound(task_id)
    
    _groups[group_name][task_id] = AutoSaveDict(new_task_data)

def task_property(group_name: str, task_id: str,
                  property: str, value: Optional[Any] = None) -> Optional[Any]:
    if group_name not in _groups:
        raise NotFound(group_name)
    if task_id not in _groups[group_name]:
        raise NotFound(task_id)
    if value is not None:
        _groups[group_name][task_id][property] = value
    elif property in _groups[group_name][task_id]:
        return _groups[group_name][task_id][property]
    else:
        raise NotFound(property)

def get_list(group_name: Optional[str] = None) -> List[str]:
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

def order_number(group_name: str, task_id: Optional[str] = None,
                 number: Optional[int] = None) -> Optional[int]:
    global _groups
    if group_name not in _groups:
        raise NotFound(group_name)
    if isinstance(task_id, str) and task_id not in _groups[group_name]:
        raise NotFound(task_id)
    
    match group_name, task_id, number:
        case str(), None, None:
            return list(_groups).index(group_name)
        case str(), str(), None:
            return list(_groups[group_name]).index(task_id)
        
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
            data = old_tasks.pop(task_id)
            tasks = AutoSaveDict()
            for index, (_task_name, _data) in enumerate(_groups[group_name].items()):
                if index == number:
                    tasks[task_id] = data
                tasks[_task_name] = _data
            _groups[group_name] = tasks

def is_exist(group_name: str, task_id: Optional[str] = None) -> bool:
    if task_id is None:
        return group_name in _groups
    elif group_name not in _groups:
        raise NotFound(group_name)
    else:
        return task_id in _groups[group_name]

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
    task1_id = add_task("group 1", "task 1")
    task2_id = add_task("group 1", "task 2")
    task3_id = add_task("group 1", "task 3")
    delete_task("group 1", task1_id)
    edit_task("group 1", task2_id, new_task_data={"task_name": "task 1", "none": "empty"})
    edit_task("group 1", task3_id, new_task_data={"Name": "Nothing"})

    task_property("group 1", task2_id, "text", "description")
    p = task_property("group 1", task2_id, "text")

    n = order_number("group 1")
    n = order_number("group 1", task2_id)
    order_number("group 5", 1)
    order_number("group 1", task3_id, 0)

    x = get_list()
    x = get_list("group 1")

    l = length()
    l = length("group 1")

    e = is_exist("group 1")
    e = is_exist("group 2")
    e = is_exist("group 1", task2_id)
    e = is_exist("group 1", task3_id)

    setting("setting 1", [5, 5])
    s = setting("setting 1")

    delete_group("group 1")
    delete_group("group 4")
    delete_group("group 5")
    delete_setting("setting 1")
