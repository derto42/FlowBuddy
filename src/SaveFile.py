"""Manages the save.json files. (if save file not provided, will use default save file.)\n
NOTE: If you want to save settings of addons,
please use apply_setting, get_setting, remove_setting
methods from AddOnBase class instead."""

from __future__ import annotations

import json
from os import path
from typing import Optional, Union

from FileSystem import abspath, SAVE_FILE


JsonType = Union[dict, list, tuple, str, int, float, bool, None]


class NotFoundException(Exception):
    def __init__(self, name: str):
        super().__init__(f"'{name}' not found")


def _create_empty_save_file(file_path: str) -> None:
    """Creates an empty save file in the file_path directory."""
    with open(f"{file_path}", "w") as f:
        json.dump({}, f)


def _prepare_save_file(save_file: Optional[str] = None) -> str:
    """If the save_file exists, retruns the save_file path. Otherwise, creates a new save_file."""

    abs_file_path = SAVE_FILE if save_file is None else abspath(save_file)

    if not path.exists(abs_file_path):
        _create_empty_save_file(abs_file_path)

    try:
        with open(abs_file_path, "r") as f:
            _ = json.load(f)
    except json.JSONDecodeError:
        _create_empty_save_file(abs_file_path)

    return abs_file_path


def apply_setting(name: str, value: JsonType, save_file: Optional[str] = None) -> None:
    save_file_path = _prepare_save_file(save_file)
    
    with open(save_file_path, "r") as save_file:
        json_data = json.load(save_file)

    json_data[name] = value

    with open(save_file_path, "w") as save_file:
        json.dump(json_data, save_file, indent=4)


def get_setting(name: str, save_file: Optional[str] = None) -> JsonType:
    save_file_path = _prepare_save_file(save_file)
    
    with open(save_file_path, "r") as save_file:
        json_data = json.load(save_file)

    if name in json_data:
        return json_data[name]
    raise NotFoundException(name)


def remove_setting(name: str, save_file: Optional[str] = None) -> None:
    save_file_path = _prepare_save_file(save_file)
    
    with open(save_file_path, "r") as save_file:
        json_data = json.load(save_file)

    if name in json_data:
        del json_data[name]
        with open(save_file_path, "w") as save_file:
            json.dump(json_data, save_file, indent=4)

    raise NotFoundException(name)
