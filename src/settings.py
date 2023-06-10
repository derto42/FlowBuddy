"""
This module contains settings values of our application.
"""

from typing import Any
from importlib import reload

import SaveFile as Data


# Function to retrieve settings from the SaveFile module.
def _get_setting(setting_name: str) -> tuple[Any, bool]:
    try:
        return Data.get_setting(setting_name), True
    except Data.NotFoundException:
        return None, False



CORNER_RADIUS = 12
STROKE_WIDTH = 2

# Assign the retrieved value if it is found; otherwise, assign the default value.
UI_SCALE: float = _load[0] if (_load:=_get_setting("ui_scale"))[1] and isinstance(_load[0], (int, float)) else 1.0




def apply_ui_scale(value: int | float) -> int | float:
    scaled_value = value * UI_SCALE
    return type(value)(scaled_value)