"""
This module contains settings values of our application.

Functions:
reload_values(): Reloads the Settings values from the SaveFile module if the setting found in SaveFile.
Otherwise loads the defaul values.

Note: The values can be adjusted using the reload_values() function,
which updates the values based on the latest settings.
"""

from typing import Any


# Function to retrieve settings from the SaveFile module.
def _get_setting(setting_name: str) -> tuple[Any, bool]:
    import SaveFile as Data
    try:
        return Data.get_setting(setting_name), True
    except Data.NotFound:
        return None, False



CORNER_RADIUS = 12
STROKE_WIDTH = 2

# Assign the retrieved value if it is found; otherwise, assign the default value.
UI_SCALE: float = _load[0] if (_load:=_get_setting("ui_scale"))[1] and isinstance(_load[0], (int, float)) else 1.0
