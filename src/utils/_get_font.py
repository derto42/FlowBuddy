from typing import Literal, Optional, Union

from PyQt5.QtGui import QFont, QFontDatabase

import FileSystem as File


DEFAULT_FONT = "Montserrat-Medium.ttf"
DEFAULT_BOLD = "Montserrat-Bold.ttf"
DEFAULT_FONT_SIZE = 16

loaded_fonts = {
    # DEFAULT_FONT: QFontDatabase.addApplicationFont(File.font(DEFAULT_FONT)),
    # DEFAULT_BOLD: QFontDatabase.addApplicationFont(File.font(DEFAULT_BOLD))
}

MEDIUM = "medium"
BOLD   = "bold"

SHORT_NAME_TO_WEIGHT = {
    "Thin": QFont.Thin,
    "ExtraLight": QFont.ExtraLight,
    "Light": QFont.Light,
    "Normal": QFont.Normal,
    "Medium": QFont.Medium,
    "DemiBold": QFont.DemiBold,
    "Bold": QFont.Bold,
    "ExtraBold": QFont.ExtraBold,
    "Black": QFont.Black,
}


def get_font(font_name: str = DEFAULT_FONT,
             size: int = DEFAULT_FONT_SIZE,
             weight: Literal["medium", "bold"] = "medium") -> QFont:
    
    _size = size
    _italic = False
    
    if font_name == DEFAULT_FONT:
        if DEFAULT_FONT not in loaded_fonts or\
           DEFAULT_BOLD not in loaded_fonts:
               loaded_fonts[DEFAULT_FONT] = QFontDatabase.addApplicationFont(File.font(DEFAULT_FONT))
               loaded_fonts[DEFAULT_BOLD] = QFontDatabase.addApplicationFont(File.font(DEFAULT_BOLD))
        if weight == "medium":
            font_name = DEFAULT_FONT
        elif weight == "bold":
            font_name = DEFAULT_BOLD
        _weight = SHORT_NAME_TO_WEIGHT["Normal"]
            
    elif font_name not in loaded_fonts:
        # add font to application.
        loaded_fonts[font_name] = QFontDatabase.addApplicationFont(File.font(font_name))
        if isinstance(weight, int):
            _weight = weight
        elif isinstance(weight,str):
            _weight = SHORT_NAME_TO_WEIGHT[weight.title()]
    else:
        _weight = SHORT_NAME_TO_WEIGHT[weight.title()]
        
    _family_name = QFontDatabase.applicationFontFamilies(loaded_fonts[font_name])[0]

    system_fonts = QFontDatabase ().families ()
    if "Montserrat" in system_fonts:
        _family_name = "Montserrat"
        _weight = SHORT_NAME_TO_WEIGHT[weight.title()]
        
    return QFont(_family_name, _size, _weight, _italic)