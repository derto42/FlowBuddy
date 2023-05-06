from __future__ import annotations

import json
from typing import Any, List, Dict, Literal, Optional, Union

import FileSystem as FS


FILE_PATH = FS.SAVE_FILE


class Task:
    def __init__(self, group_name: str, task_name: str):
        self._group_name = group_name
        self._task_name = task_name
        
        if group_name not in _data.keys():
            raise ValueError("Group '%s' not found" % group_name)
        
        if task_name not in _data[group_name].keys():
            new_task(self._group_name, task_name)
        else:
            task: dict = _data[group_name][task_name]

        self._name = task["name"]
        self._text = task["text"]
        self._button_text = task["button_text"]
        self._url = task["url"]
        self._file = task["file"]
        
        self.update_json()
        
    def __repr__(self) -> str:
        return json.dumps(self._json)

    def group_name(self, group_name: Optional[str] = None) -> Optional[str]:
        if group_name is not None:
            edit_task(self._group_name, self._task_name,
                  new_task_name=self.task_name())
            self._group_name = group_name
        else:
            return self._group_name
        
    def task_name(self, task_name: Optional[str] = None) -> Optional[str]:
        if task_name is not None:
            edit_task(self._group_name, self._task_name,
                  new_task_name=task_name)
            self._task_name = task_name
        else:
            return self._task_name

    def name(self, name: Optional[str] = None) -> Optional[str]:
        if name is not None:
            self._name = name
            self.update()
        else:
            return self._name
        
    def text(self, text: Optional[str] = None) -> Optional[str]:
        if text is not None:
            self._text = text
            self.update()
        else:
            return self._text
        
    def button_text(self, button_text: Optional[str] = None) -> Optional[str]:
        if button_text is not None:
            self._button_text = button_text
            self.update()
        else:
            return self._button_text

    def url(self, url: Optional[str] = None) -> Optional[str]:
        if url is not None:
            self._url = url
            self.update()
        else:
            return self._url
        
    def file(self, file_path: Optional[str] = None) -> Optional[str]:
        if file_path is not None:
            self._file = file_path
            self.update()
        else:
            return self._file
        
    def update_json(self) -> None:
        self._json = {"name": self._name,
                 "text": self._text,
                 "button_text": self._button_text,
                 "url": self._url,
                 "file": self._file}

    def update(self) -> None:
        self.update_json()
        self.save()
        
    def save(self) -> None:
        edit_task(self._group_name, self._task_name,
                  new_task_name=self._task_name,
                  new_task_content=self.get_json())
        
    def get_json(self) -> Dict[str, str]:
        return self._json

    def group(self) -> Group:
        """Returns a the group of this task as a Group object."""
        return Group(self._group_name)

    def delete(self) -> None:
        """Do not use this object after deletion."""
        _data[self._group_name].pop(self._task_name)
        _save_contents()

class Group:
    def __init__(self, group_name: str):
        self._group_name = group_name
        
        self._tasks = _data[group_name]

    def __len__(self):
        return len(self._tasks)

    def group_name(self, group_name: Optional[str] = None) -> Optional[str]:
        if group_name is not None:
            edit_group(self._group_name, new_group_name=group_name)
            self._group_name = group_name
        else:
            return self._group_name
        
    def get_task(self, task_name: str) -> Task:
        if task_name not in self._tasks.keys():
            raise KeyError("Task '%s' not found" % task_name)
        return Task(self._group_name, task_name)
    
    def get_tasks(self) -> List[Task]:
        return [Task(self._group_name, task_name) for task_name in self._tasks.keys()]
    
    def add_task(self, task_name: str, task_content: Optional[Union[Task, dict[str, str]]] = None) -> Task:
        if isinstance(task_content, Task):
            content = task_content.get_json()
        elif isinstance(task_content, dict):
            content = task_content
        else:
            content = None
        new_task(self._group_name, task_name)
        edit_task(self._group_name, task_name, new_task_content=content)
        return self.get_task(task_name)

    def del_task(self, task_name: str) -> None:
        if task_name not in self._tasks.keys():
            raise ValueError("Task '%s' not found" % task_name)
        self._tasks.pop(task_name)
        self.update()

    def get_json(self,) -> Dict[str, Dict[str, str]]:
        return self._tasks
    
    def save(self) -> None:
        edit_group(self._group_name, new_group_content=self._tasks)
        
    def update(self) -> None:
        self.save()

    def delete(self) -> None:
        """Do not use this object after deletion."""
        _data.pop(self._group_name)
        _save_contents()

def _get_contents() -> Dict[Literal["settings", "data"], Dict[str, Dict]]:
    try:
        if not FS.exists(FILE_PATH):
            raise FileNotFoundError
        with open(FILE_PATH, 'r') as f:
            contents = json.load(f)
            if not ("settings" in contents and "data" in contents):
                raise KeyError
            return contents
    except (json.JSONDecodeError, FileNotFoundError, KeyError):
        FS.create_save_file()
        return _get_contents()
    
def _save_contents() -> None:
    _contents["settings"] = _settings
    _contents["data"] = _data
    with open(FILE_PATH, 'w') as f:
        json.dump(_contents, f, indent=4)


_contents = _get_contents()
_settings = _contents["settings"]

# data -> groups -> tasks -> properties
_data: Dict[str, Dict[str, Dict[str, str]]] = _contents["data"]


def get_setting(name: str) -> Union[Any, Literal["None"]]:
    """Returns 'None' if no setting is defined."""
    if name in _settings.keys():
        return _settings[name]
    else:
        return 'None'

def set_setting(name: str, value: Any) -> None:
    global _settings
    _settings[name] = value
    _save_contents()


def get_group(group_name: str) -> Group:
    if group_name not in _data.keys():
        raise KeyError("Group '%s' not found" % group_name)
    return Group(group_name)

def get_groups() -> list[Group]:
    return [Group(group_name) for group_name in _data.keys()]

def new_group(group_name: str) -> Group:
    global _data
    if group_name in _data:
        raise ValueError("Group name already exists.")
    _data[group_name] = {}
    _save_contents()
    return Group(group_name)

def edit_group(group_name: str, *,
               new_group_name: Optional[str] = None,
               new_group_content: Optional[Dict] = None) -> None:
    
    if new_group_name == new_group_content == None:
        return
    
    # iterating over the tasks in the group to maintain the order.
    # if there is a better way to do this(changin the key without changing the order) feel free to change this.
    global _data
    old_data_items = _data.items()
    _data = {}
    
    for _group_name, _group_content in old_data_items:
        
        if group_name == _group_name:
            name = new_group_name if new_group_name is not None else _group_name
            content = new_group_content if new_group_content is not None else _group_content
            _data[name] = content
        else:
            _data[_group_name] = _group_content

    _save_contents()


def get_task(group_name: str, task_name: str) -> Task:
    return Task(group_name, task_name)

def get_tasks(group_name: str) -> List[Task]:
    if group_name not in _data.keys():
        raise ValueError("Group '%s' does not exist." % group_name)
    group: dict = _data[group_name]
    tasks = [Task(group_name, task_name) for task_name in group.keys()]
    return tasks

def new_task(group_name: str, task_name: str) -> None:
    global _data
    if not group_name in _data.keys():
        raise KeyError("Group '%s' not found" % group_name)
    _data[group_name][task_name] = {"name": "", "text": "", "button_text": "", "url": "", "file": ""}
    _save_contents()

def edit_task(group_name: str, task_name: str, *,
                   new_task_name: Optional[str] = None,
                   new_task_content: Optional[dict] = None) -> None:
    
    if new_task_name == new_task_content == None:
        return
    
    # iterating over the tasks in the group to maintain the order.
    # if there is a better way to do this(changin the key without changing the order) feel free to change this.
    global _data
    old_data_group_itmes = _data[group_name].items()
    _data[group_name] = {}
    for _task_name, _task_content in old_data_group_itmes:
        if _task_name == task_name:
            name = new_task_name if new_task_name is not None else _task_name
            content = new_task_content if new_task_content is not None else _task_content
            _data[group_name][name] = content
        else:
            _data[group_name][_task_name] = _task_content
    _save_contents()




# for testing purposes
if __name__ == '__main__':
    group1 = new_group("Text + Button")
    task: Task = group1.add_task("Task 1")
    task.name("Text + Button1683068687")
    task.text("Text")
    
    task2: Task = group1.add_task("Task 2")
    task2.name("Text + Button1683068705")
    task2.text("Text +")
    task2.button_text("Button")
    task2.url("e")

    task3: Task = group1.add_task("Task 3")
    task3.name("Text + Button1683068724")
    task3.button_text("Just Button")
    task3.url("e")
    
    group2 = new_group("URL + Files")
    task1: Task = group2.add_task("Task 1")
    task1.name("URL + Files1683072251")
    task1.button_text("URL")
    task1.url("youtube.com")

    task2: Task = group2.add_task("Task 2")
    task2.name("URL + Files1683072257")
    task2.button_text("File")
    task2.file("C:/Program Files/Imagine/Imagine.exe")
    
    group1.delete()
    group2.delete()