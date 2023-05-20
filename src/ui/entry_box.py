from PyQt5.QtWidgets import QLineEdit, QWidget
from .settings import CORNER_RADIUS, UI_SCALE
from .utils import get_font


ENTRY_BOX_STYLE = f"""
    background-color: #DADADA;
    border-radius: {CORNER_RADIUS * UI_SCALE}px;
    padding-left: {int((27 - 4) * UI_SCALE)}px;
    padding-right: {int((27 - 4) * UI_SCALE)}px;
    """


class Entry(QLineEdit):
    def __init__(self, parent: QWidget = None, place_holder: str = "Text") -> None:
        super().__init__(parent)
        self.setPlaceholderText(place_holder)
        self.setFixedSize(int(200 * UI_SCALE), int(40 * UI_SCALE))
        self.setFont(get_font(size=int(16 * UI_SCALE)))
        self.setStyleSheet(ENTRY_BOX_STYLE)
