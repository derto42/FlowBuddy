from __future__ import annotations
import os
import sys


ADDONS_NAME = "addons"

PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

ADDONS_FOLDER = os.path.join(PROGRAM_DIR, ADDONS_NAME)

PLATFORM = sys.platform


def save_file_data(file_name:str,file_data:str ="") -> None:
    SAVE_FILE = os.path.join(PROGRAM_DIR, file_name)
    
    with open(SAVE_FILE, "w") as f:
        f.write(file_data)


def abspath(path: str) -> str:
    """Returns the absolute path. Returns None if the path does not exist."""
    _path = os.path.join(PROGRAM_DIR, path)
    return os.path.abspath(_path) if os.path.exists(_path) else None


def exists(path: str):
    """Returns True if the path exists. Returns False otherwise"""
    return os.path.exists(path)

def get_file_data(file_name):
    SAVE_FILE = os.path.join(PROGRAM_DIR, file_name)
    if exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return file.read()
        


def open_file(file_path: str | None) -> None:
    if file_path is not None:
        if PLATFORM in ("win32",):
            os.startfile(file_path)
        elif PLATFORM in ("linux", "darwin"):
            os.system(f"xdg-open {file_path}")
