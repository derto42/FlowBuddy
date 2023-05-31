from typing import Callable
from importlib import import_module
from glob import glob
from os.path import split

from FileSystem import exists, ADD_ONS_FOLDER, ADD_ONS_NAME
from utils import HotKeys


class AddOnBase:
    def set_shortcut(self, shortcut: str, function: Callable) -> None:
        HotKeys.add_global_shortcut(shortcut, function)
    


def load_add_ons() -> None:
    """Loads all the modules from the add_ons folder."""
    if exists(ADD_ONS_FOLDER):
        for file_path in glob(f"{ADD_ONS_FOLDER}\\*.py"):
            import_module(f'{ADD_ONS_NAME}.{split(file_path)[1][:-3]}')
            