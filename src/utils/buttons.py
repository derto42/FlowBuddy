from typing import Tuple, Callable

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton

from src.utils.colors import replace_color


def create_button(icon: str, size: Tuple[int, int], location: Tuple[int, int], style: str, action: Callable, icon_size: Tuple[int, int] = None) -> QPushButton:
    """Create a button."""
    button = QPushButton()
    button.setIcon(QIcon(f'../icons/{icon}'))
    button.setFixedSize(*size)
    button.setCursor(Qt.PointingHandCursor)
    button.setStyleSheet(style)
    button.move(*location)
    button.enterEvent = lambda event: button.setStyleSheet(replace_color(style, "light"))
    button.leaveEvent = lambda event: button.setStyleSheet(replace_color(style, "dark"))

    if icon_size:
        button.setIconSize(QSize(*icon_size))
    button.clicked.connect(action)

    return button
