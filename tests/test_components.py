from importlib import import_module
import os
import sys
from types import ModuleType
import inspect

from PyQt5.QtWidgets import QApplication


sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import addon

application = QApplication([])

def load_addon(name: str) -> ModuleType:
    module_name = f"addons.{name}.{name}"
    addon.add_on_paths[module_name] = f"addons/{name}/{name}"
    addon.currently_loading_module = module_name
    print(f"Addon name: {name}\nAddon path: {addon.add_on_paths[module_name]}\nModule: {module_name}")
    print(f"Importing '{module_name}' module.")
    module = import_module(f"addons.{name}.{name}")
    print("Import complete.")
    addon.currently_loading_module = None
    addon.add_ons[module_name] = module
    return module

def activate_addon(name: str) -> None:
    module_name = f"addons.{name}.{name}"
    func = addon.AddOnBase(module_name).activate
    print(f"Activating addon {name}.")
    func()