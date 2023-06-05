"""Manages the save.json which is in the directory of the calling module."""

from __future__ import annotations

import json
import sys
from os import path
from typing import Any

from FileSystem import abspath


# This module uses `sys._getframe(1).f_globals["__name__"]` to get the name of the calling module.
# I don't think this is a good idea.


class NotFound(Exception):
    def __init__(self, name: str):
        super().__init__(f"'{name}' not found")


def _create_empty_save_file(file_path: str) -> None:
    """Creates an empty save file."""
    with open(f"{file_path}/save.json", "w") as f:
        json.dump({}, f)


def _prepare_save_file(module_path: str) -> str:
    """If the save_file exists, retruns the save_file path. Otherwise, creates a new save_file."""
    file_path = path.join((module_path.replace(".", "/")), "..")
    abs_file_path = abspath(file_path)

    if abs_file_path is None or not path.exists(f"{abs_file_path}/save.json"):
        _create_empty_save_file(abs_file_path)

    try:
        with open(f"{abs_file_path}/save.json", "r") as f:
            _ = json.load(f)
    except json.JSONDecodeError:
        _create_empty_save_file(abs_file_path)

    return f"{abs_file_path}/save.json"


def apply_settings(name: str, value: Any) -> None:
    save_file_path = _prepare_save_file(sys._getframe(1).f_globals["__name__"])
    
    with open(save_file_path, "r") as save_file:
        json_data = json.load(save_file)

    json_data[name] = value

    with open(save_file_path, "w") as save_file:
        json.dump(json_data, save_file, indent=4)


def get_setting(name: str) -> Any:
    save_file_path = _prepare_save_file(sys._getframe(1).f_globals["__name__"])
    
    with open(save_file_path, "r") as save_file:
        json_data = json.load(save_file)

    if name in json_data:
        return json_data[name]
    raise NotFound(name)


def remove_setting(name: str) -> None:
    save_file_path = _prepare_save_file(sys._getframe(1).f_globals["__name__"])
    
    with open(save_file_path, "r") as save_file:
        json_data = json.load(save_file)

    if name in json_data:
        del json_data[name]
        with open(save_file_path, "w") as save_file:
            json.dump(json_data, save_file, indent=4)

    raise NotFound(name)
