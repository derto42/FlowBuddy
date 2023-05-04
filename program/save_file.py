import json
from typing import Any, List, Dict, Literal, Optional, Union
import FileSystem as FS

FILE_PATH = FS.SAVE_FILE


class Task:
    def __init__(self, group_name: str, task_name: str):
        self._group_name = group_name
        self._task_name = task_name
        
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
                 "_button_text": self._button_text,
                 "url": self._url,
                 "file": self._file}

    def update(self) -> None:
        self.update_json()
        self.save()
        
    def save(self) -> None:
        edit_task(self._group_name, self._task_name,
                  new_task_name=self.task_name(),
                  new_task_content=self.get_json())
        
    def get_json(self) -> Dict[str, str]:
        return self._json


class Group:
    def __init__(self, group_name: str):
        self._group_name = group_name
        
        self._tasks = get_group(self._group_name)

    def group_name(self, group_name: Optional[str]) -> Optional[str]:
        if group_name is not None:
            edit_group(self._group_name, new_group_name=group_name)
            self._group_name = group_name
        else:
            return self._group_name
        
    def get_task(self, task_name: str) -> Task:
        if task_name not in self._tasks.keys():
            raise KeyError("Task '%s' not found" % task_name)
        return Task(self._group_name, task_name)
    
    def add_task(self, task_name: str, task_content: Union[Task, dict[str, str]]) -> Task:
        if isinstance(task_content, Task):
            content = task_content.get_json()
        elif isinstance(task, dict):
            content = task_content
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


def get_setting(name: str) -> Any:
    if name in _settings.keys():
        return _settings[name]
    else:
        return None

def set_setting(name: str, value: Any) -> None:
    global _settings
    _settings[name] = value
    _save_contents()


def get_group(group_name: str) -> dict[str, dict]:
    if group_name not in _data.keys():
        raise KeyError("Group '%s' not found" % group_name)
    return _data[group_name].items()

def get_groups() -> list[tuple[str, dict]]:
    return _data.items()

def new_group(group_name: str) -> None:
    global _data
    _data[group_name] = {}
    _save_contents()

def edit_group(group_name: str, *,
               new_group_name: Optional[str] = None,
               new_group_content: Optional[Union[Task, Dict]] = None) -> None:
    
    if new_group_name == new_group_content == None:
        return
    
    global _data
    content = _data.pop(group_name)
    
    if new_group_name is not None:
        group_name = new_group_name

    if new_group_content is not None:
        if isinstance(new_group_content, Task):
            content = {new_group_content.task_name(): new_group_content.get_json()}
        elif isinstance(new_group_content, dict):
            content = new_group_content
    
    _data[group_name] = content
    _save_contents()


def get_task(group_name: str, task_name: str) -> Task:
    return Task(group_name, task_name)

def get_tasks(group_name: str) -> List[Task]:
    group: dict = _data[group_name]
    tasks = [Task(group_name, task_name) for task_name in group.keys()]
    return tasks

def new_task(group_name: str, task_name: str) -> None:
    global _data
    if not group_name in _data.keys():
        raise KeyError("Group '%s' not found" % group_name)
    _data[group_name][task_name] = {}
    _save_contents()

def edit_task(group_name: str, task_name: str, *,
                   new_task_name: Optional[str],
                   new_task_content: Optional[dict]) -> None:
    
    if new_task_name == new_task_content == None:
        return

    global _data
    content = _data[group_name].pop(task_name)

    if new_task_name is not None:
        task_name = new_task_name

    if new_task_content is not None:
        content = new_task_content

    _data[group_name][task_name] = content
    _save_contents()




# for testing purposes
if __name__ == '__main__':
    for group_name, group in get_groups():
        for task_name, properties in group.items():
            print(group_name, properties["name"])
            
    for task in get_tasks("Group 1"):
        print(task.task_name())
        
    task = get_task("Group 1", "Task 1")
    task.name("Name of task 1")
    print(task.name())