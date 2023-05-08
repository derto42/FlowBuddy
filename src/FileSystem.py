from __future__ import annotations
import os

SAVE_FILE_NAME = "save.json"
ICONS_FOLDER_NAME = "icons"
FONTS_FOLDER_NAME = "fonts"

PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

SAVE_FILE = os.path.join(PROGRAM_DIR, SAVE_FILE_NAME)
ICONS_FOLDER = os.path.join(PROGRAM_DIR, ICONS_FOLDER_NAME)
FONTS_FOLDER = os.path.join(PROGRAM_DIR, FONTS_FOLDER_NAME)


def create_save_file() -> None:
    """Creates an empty save file."""
    with open(SAVE_FILE, 'w') as f:
        f.write('{"settings": {}, "data": {}}')


def abspath(path: str) -> str:
    """Returns the absolute path. Returns None if the path does not exist."""
    _path = os.path.join(PROGRAM_DIR, path)
    return os.path.abspath(_path) if os.path.exists(_path) else None


def exists(path: str):
    """Returns True if the path exists. Returns False otherwise"""
    return os.path.exists(path)


def icon(icon_name: str) -> str | None:
    """Returns the absolute path of given icon. Returns None if the icon does not exist."""
    path = os.path.join(ICONS_FOLDER, icon_name)
    return os.path.abspath(path) if os.path.exists(path) else None


def font(font_name: str) -> str | None:
    """Returns the absolute path of given font. Returns None if the font does not exist."""
    path = os.path.join(FONTS_FOLDER, font_name)
    return os.path.abspath(path) if os.path.exists(path) else None


# for testing purposes
if __name__ == "__main__":
    print(os.path.exists(abspath("icons/icon.png")))
    print(os.path.exists(icon("toggle.png")))
