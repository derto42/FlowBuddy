from __future__ import annotations
import json
from types import ModuleType
from typing import Callable, Optional
from importlib import import_module
import os
import inspect

from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QKeySequence

from FileSystem import exists, ADDONS_FOLDER, ADDONS_NAME
from SaveFile import JsonType, NotFoundException, apply_setting, get_setting, remove_setting, NotFoundException
from utils import HotKeys


add_ons: dict[str, ModuleType] = {}
add_on_paths: dict[str, ModuleType] = {}

currently_loading_module = None


def load_addons() -> None:
    """Loads all the modules from the ADDONs folder."""
    global add_ons, add_on_paths, currently_loading_module
    
    def apply_order(modules_and_paths: dict[str, str]) -> dict[str, str]:
        order_file = f"{ADDONS_FOLDER}/order.json"
        if not exists(order_file):
            default_order_data = {
                    "_comment": [
                        "High priority addons. These addons will be loaded first.",
                        "Those addons which not specified will be considered as 'medium_priority' and will be loaded after loading hight_priority addons.",
                        "Low priority addons. These addons will be loaded after loading all the addons.",
                        "Names are case insensitive."
                    ],


                    "high_priority": [
                        "shortcuts",
                        "notes",
                        "youtube_downloader"
                    ],

                    "medium_priority": [],

                    "low_priority": [
                        "settings"
                    ]
                }
            with open(order_file, "w") as f:
                json.dump(default_order_data, f, indent=4)

        else:
            try:
                # apply sorting if possible.
                if exists(order_file):
                    with open(order_file, "r") as f:
                        order_data = json.load(f)
                        
                    high_priorities   = [x.lower() for x in order_data["high_priority"]]
                    medium_priorities = [x.lower() for x in order_data["medium_priority"]]
                    low_priorities    = [x.lower() for x in order_data["low_priority"]]
                    
                    modules_name_in_lower = {x.split(".")[-1].lower(): x for x in modules_and_paths}
                    
                    priority_addons = []
                    for priority in [high_priorities, medium_priorities, low_priorities]:
                        addons = {}
                        for module in priority:
                            if module in modules_name_in_lower:
                                module_name = modules_name_in_lower[module]
                                addons[module_name] = modules_and_paths.pop(module_name)
                        priority_addons.append(addons)
                        
                    high_priority_addons, medium_priority_addons, low_priority_addons = priority_addons

                    rest_addons = modules_and_paths

                    return {**high_priority_addons,
                            **medium_priority_addons,
                            **rest_addons,
                            **low_priority_addons}

            except Exception as e:
                print(f"Error occurred while applying order for addons.\n{e}")
            
        return modules_and_paths
    
    
    if exists(ADDONS_FOLDER):
        # traverse root directory, and list directories as dirs and files as files
        modules_and_paths = {}
        
        for root, dirs, files in os.walk(ADDONS_FOLDER):
            for name in dirs:
                dir_path = os.path.join(root, name)
                file_path = os.path.join(dir_path, f"{name}.py")
                if os.path.isfile(file_path):  # If the .py file with same name as directory exists
                    module_name = f'{ADDONS_NAME}.{name}.{name}'
                    modules_and_paths[module_name] = file_path
        
        modules_and_paths = apply_order(modules_and_paths)
        
        for module_name in modules_and_paths:
            # Import the module
            add_on_paths[module_name] = modules_and_paths[module_name]
            currently_loading_module = module_name
            module = import_module(module_name)
            currently_loading_module = None
            add_ons[module_name] = module



class AddOnBase:
    system_tray_icon: QSystemTrayIcon = None # instance of QSystemTrayIcon will be assigned after initializing it
    instances: dict[str, AddOnBase] = {}
    
    def __new__(cls, name: Optional[str] = None):
        # returns the instance of currently loading or calling addon module if available.
        # if not, returns the AddOnBase instance of module of given addon name.
        
        if (addon_module:=currently_loading_module) is not None or \
            (addon_module:=AddOnBase._get_calling_module()) is not None:
            if name is not None:
                print("WARNING: name should not be specified when creating new instace from addon module.",
                      f"name of this instance is '{addon_module}'.")
                
            if addon_module in AddOnBase.instances:
                return AddOnBase.instances[addon_module]
            new_instance = super().__new__(cls)
            new_instance._init()
            AddOnBase.instances[addon_module] = new_instance
            return new_instance
        
        if name in AddOnBase.instances:
            return AddOnBase.instances[name]
        else: raise ValueError(f"'{name}' AddOn instance not found.")
    
    def _init(self):
        self.name = currently_loading_module
        self.activate_shortcut = None
        
    @staticmethod
    def _get_calling_module() -> str | None:
        """Returns the calling module name if calling module is an addon. Otherwise returns None."""
        addon_file = inspect.currentframe().f_back.f_back.f_globals["__file__"]
        return next(
            (
                module_name
                for module_name, path in add_on_paths.items()
                if os.path.abspath(path) == os.path.abspath(addon_file)
            ),
            None,
        )
        
        
    def activate(self):
        """Override this method to call when desktop widget is activated."""
        pass
    
    def set_activate_shortcut(self, key: QKeySequence) -> None:
        """Adds a global shortcut key to call the activate method."""
        self.activate_shortcut: QKeySequence = key
        HotKeys.add_global_shortcut(HotKeys.format_shortcut_string(key.toString()), self.activate)


    def apply_setting(self, name: str, value: JsonType) -> None:
        save_file = os.path.join(os.path.dirname(add_on_paths[self.name]), "save.json")
        return apply_setting(name, value, save_file)
    
    def get_setting(self, name: str) -> JsonType:
        save_file = os.path.join(os.path.dirname(add_on_paths[self.name]), "save.json")
        return get_setting(name, save_file)
    
    def remove_setting(self, name: str) -> None:
        save_file = os.path.join(os.path.dirname(add_on_paths[self.name]), "save.json")
        return remove_setting(name, save_file)
    
    
    @staticmethod
    def set_shortcut(key: QKeySequence, function: Callable) -> None:
        """Adds a global shortcut"""
        HotKeys.add_global_shortcut(HotKeys.format_shortcut_string(key.toString()), function)
    
