from __future__ import annotations
from types import ModuleType
from typing import Callable
from importlib import import_module
import os

from PyQt5.QtWidgets import QSystemTrayIcon

from FileSystem import exists, ADDONS_FOLDER, ADDONS_NAME
from utils import HotKeys


add_ons: dict[str, ModuleType] = {}

currently_loading_module = None


class AddOnBase:
    system_tray_icon: QSystemTrayIcon = None # instance of QSystemTrayIcon will be assigned after initializing it
    instences: dict[str, AddOnBase] = {}
    
    def __init__(self):
        AddOnBase.instences[currently_loading_module] = self
        self.name = currently_loading_module
        
    def activate(self):
        """Override this method to call when desktop widget is activated."""
        pass
    
    def set_shortcut(self, shortcut: str, function: Callable) -> None:
        """Adds a global shortcut"""
        HotKeys.add_global_shortcut(shortcut, function)
    


def load_addons() -> None:
    """Loads all the modules from the ADDONs folder."""
    global add_ons, currently_loading_module
    if exists(ADDONS_FOLDER):
        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(ADDONS_FOLDER):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                file_path = os.path.join(dir_path, f"{dir}.py")
                if os.path.isfile(file_path):  # If the .py file with same name as directory exists
                    # Import the module
                    module_name = f'{ADDONS_NAME}.{dir}.{dir}'
                    currently_loading_module = module_name
                    module = import_module(module_name)
                    currently_loading_module = None
                    add_ons[module_name] = module
