from typing import Callable
from importlib import import_module
from glob import glob
from os.path import split
import os

from FileSystem import exists, ADDONS_FOLDER, ADDONS_NAME
from utils import HotKeys


class AddOnBase:
    def set_shortcut(self, shortcut: str, function: Callable) -> None:
        HotKeys.add_global_shortcut(shortcut, function)
    


def load_addons() -> None:
    """Loads all the modules from the ADDONs folder."""
    if exists(ADDONS_FOLDER):
        # traverse root directory, and list directories as dirs and files as files
        for root, dirs, files in os.walk(ADDONS_FOLDER):
            for dir in dirs:
                dir_path = os.path.join(root, dir)
                file_path = os.path.join(dir_path, f"{dir}.py")
                if os.path.isfile(file_path):  # If the .py file with same name as directory exists
                    # Import the module
                    import_module(f'{ADDONS_NAME}.{dir}.{dir}')
            