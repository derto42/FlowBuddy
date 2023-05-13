from typing import Literal, Optional, Union

from PyQt5.QtGui import QFont, QFontDatabase

import FileSystem as File


DEFAULT_REGULAR = "Montserrat-Regular.ttf"
DEFAULT_MEDIUM = "Montserrat-Medium.ttf"
DEFAULT_SEMI_BOLD = "Montserrat-SemiBold.ttf"
DEFAULT_BOLD = "Montserrat-Bold.ttf"
DEFAULT_FONT_SIZE = 16

_loaded_fonts = {}
_default_fonts_loaded = False

MEDIUM = "medium"
SEMIBOLD = "semibold"
BOLD   = "bold"

# Note: Semi Bold is named DemiBold
SHORT_NAME_TO_WEIGHT = {
    "Thin": QFont.Thin,
    "Extralight": QFont.ExtraLight,
    "Light": QFont.Light,
    "Regular": QFont.Normal,
    "Medium": QFont.Medium,
    "Semibold": QFont.DemiBold,
    "Bold": QFont.Bold,
    "Extrabold": QFont.ExtraBold,
    "Black": QFont.Black,
}


def get_font(font_name: str = DEFAULT_REGULAR,
             size: int = DEFAULT_FONT_SIZE,
             weight: Literal["medium", "semibold", "bold", "regular"] = "regular") -> QFont:

    global _default_fonts_loaded
    
    _size = size
    _italic = False
    
    if font_name == DEFAULT_REGULAR:
        if not _default_fonts_loaded:
            _loaded_fonts[DEFAULT_MEDIUM] = QFontDatabase.addApplicationFont(File.font(DEFAULT_MEDIUM))
            _loaded_fonts[DEFAULT_BOLD] = QFontDatabase.addApplicationFont(File.font(DEFAULT_BOLD))
            _loaded_fonts[DEFAULT_SEMI_BOLD] = QFontDatabase.addApplicationFont(File.font(DEFAULT_SEMI_BOLD))
            _loaded_fonts[DEFAULT_REGULAR] = QFontDatabase.addApplicationFont(File.font(DEFAULT_REGULAR))
            _default_fonts_loaded = True
        if weight == "regular":
            font_name = DEFAULT_REGULAR
        elif weight == "medium":
            font_name = DEFAULT_MEDIUM
        elif weight == "semibold":
            font_name = DEFAULT_SEMI_BOLD
        elif weight == "bold":
            font_name = DEFAULT_BOLD
        _weight = SHORT_NAME_TO_WEIGHT["Regular"]
            
    elif font_name not in _loaded_fonts:
        # add font to application.
        _loaded_fonts[font_name] = QFontDatabase.addApplicationFont(File.font(font_name))
        if isinstance(weight, int):
            _weight = weight
        elif isinstance(weight,str):
            _weight = SHORT_NAME_TO_WEIGHT[weight.title()]
    else:
        _weight = SHORT_NAME_TO_WEIGHT[weight.title()]
        
    _family_name = QFontDatabase.applicationFontFamilies(_loaded_fonts[font_name])[0]

    system_fonts = QFontDatabase().families()
    if "Montserrat" in system_fonts:
        _family_name = "Montserrat"
        _weight = SHORT_NAME_TO_WEIGHT[weight.title()]
        
    return QFont(_family_name, _size, _weight, _italic)