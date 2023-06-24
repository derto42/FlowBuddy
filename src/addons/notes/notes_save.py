from __future__ import annotations
import os
import sys
import json


FILE_PATH = os.path.join(os.path.dirname(__file__))
DATA_NAME = "data"
DATA_FOLDER = os.path.join(FILE_PATH, DATA_NAME)
PLATFORM = sys.platform
CONFIG_FILE = os.path.join(DATA_FOLDER, "config.json")


def save_file_data(file_name: str, file_data: str = "") -> None:
    file_name+=".txt"
    SAVE_FILE = os.path.join(DATA_FOLDER, file_name)
    with open(SAVE_FILE, "w") as f:
        f.write(file_data)


def delete_file_data(file_name: str) -> None:
    file_name+=".txt"
    SAVE_FILE = os.path.join(DATA_FOLDER, file_name)
    if exists(SAVE_FILE):
        os.remove(SAVE_FILE)


def exists(file_name: str):
    """Returns True if the path exists. Returns False otherwise"""
    SAVE_FILE = os.path.join(DATA_FOLDER, file_name)
    return os.path.exists(SAVE_FILE)


def get_file_data(file_name):
    file_name+=".txt"
    SAVE_FILE = os.path.join(DATA_FOLDER, file_name)
    if exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return file.read()


if not exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


def open_file(file_path: str | None) -> None:
    if file_path is not None:
        if PLATFORM in ("win32",):
            os.startfile(file_path)
        elif PLATFORM in ("linux", "darwin"):
            os.system(f"xdg-open {file_path}")


def get_config():
    with open(CONFIG_FILE, "r") as file:
        config = json.load(file)
    return config


def create_config_from_text_files():
    config = {
        "files": [file_name for file_name in os.listdir(DATA_FOLDER)],
        "last_active": 0,
    }
    write_config(config)


def write_config(config):
    with open(CONFIG_FILE, "w") as f:
        f.write(json.dumps(config))


# If there are any exceptions related to JSON decoding, file not found, or missing keys,
# a save file is created using the FS module.
try:
    with open(CONFIG_FILE) as f:
        data = json.load(f)
    _, _ = data["files"], data["last_active"]
except (json.JSONDecodeError, FileNotFoundError, KeyError):
    create_config_from_text_files()
