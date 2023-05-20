from typing import Any


CORNER_RADIUS = 12
STROKE_WIDTH = 2



# Temporary load function to retrieve settings from the SaveFile module.
def load(setting_name: str) -> Any:
    import SaveFile as Data
    try:
        return Data.get_setting(setting_name), True
    except Data.NotFound:
        return None, False

# loads the setting from save.json. if no setting found will assign default value.
UI_SCALE: float = _load[0] if (_load:=load("ui_scale"))[1] and isinstance(_load[0], (int, float)) else 1.0

# After retrieving the setting, the function is deleted to prevent unnecessary imports from other modules.
del load