from __future__ import annotations
import os
import sys
from pathlib import Path



FILE_PATH = os.path.join(os.path.dirname(__file__))
ADDONS_NAME = "data"
ADDONS_FOLDER=os.path.join(FILE_PATH,ADDONS_NAME)
PLATFORM = sys.platform


def save_file_data(file_name:str,file_data:str ="") -> None:
    SAVE_FILE = os.path.join(ADDONS_FOLDER, file_name)
    with open(SAVE_FILE, "w") as f:
        f.write(file_data)



def exists(file_name: str):
    """Returns True if the path exists. Returns False otherwise"""
    SAVE_FILE = os.path.join(ADDONS_FOLDER, file_name)
    return os.path.exists(SAVE_FILE)

def get_file_data(file_name):
    SAVE_FILE = os.path.join(ADDONS_FOLDER, file_name)
    if exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return file.read()
        

if not exists(ADDONS_FOLDER):
    os.makedirs(ADDONS_FOLDER)

def open_file(file_path: str | None) -> None:
    if file_path is not None:
        if PLATFORM in ("win32",):
            os.startfile(file_path)
        elif PLATFORM in ("linux", "darwin"):
            os.system(f"xdg-open {file_path}")
