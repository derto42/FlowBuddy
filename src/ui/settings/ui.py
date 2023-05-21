from typing import overload
from importlib import reload
import contextlib
from typing import Optional, Tuple, Any
from PyQt5 import QtCore, QtGui

from PyQt5.QtCore import Qt, pyqtSignal, QRectF
from PyQt5.QtGui import QMouseEvent, QPaintEvent, QPainter, QColor, QCursor, QWheelEvent
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLayout,
    QApplication,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
)


import SaveFile as Data
from ..base_window import BaseWindow
from ..entry_box import Entry
from . import UI_SCALE, CORNER_RADIUS
from .. import settings as GlobalSettings
from .structure import STRUCTURE, UPDATE, ENTRY, SPIN, KEY, SETTING_TYPE, TYPE, OPTIONS


class Button(QPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(text, parent)


class SpinBox(Entry):
    def __init__(self, current_value: int | float = 0, step: int | float = 1,
                 parent: QWidget = None) -> None:
        super().__init__(parent, "")
        
        self._value = current_value
        self._step = step
        
        self.setText(current_value)
        
        self.setLayout(layout := QVBoxLayout())
        layout.setContentsMargins(self.width() - self.width() // 3, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(but1 := QPushButton("↑"))
        layout.addWidget(but2 := QPushButton("↓"))
        but1.setFixedSize(self.width() // 3, self.height() // 2)
        but2.setFixedSize(self.width() // 3, self.height() // 2)
        but1.clicked.connect(lambda *_: self._value_add())
        but2.clicked.connect(lambda *_: self._value_substract())
        but1.setCursor(Qt.CursorShape.PointingHandCursor)
        but2.setCursor(Qt.CursorShape.PointingHandCursor)
        
        
        self.value = self.text
        self.setValue = self.setText
        self.valueChanged = self.textChanged
        self.valueEdited = self.textEdited
        
        
    @overload
    def value(self) -> int | float: ...
    @overload
    def setValue(self, value: int | float) -> None: ...


    def _value_add(self, step: int | float = None) -> None:
        if step is None: step = self._step
        self.setValue(self._value + step)

    def _value_substract(self, step: int | float = None) -> None:
        if step is None: step = self._step
        self.setValue(self._value - step)


    def text(self) -> int | float:
        return self._value
    
    def setText(self, value: int | float) -> None:
        self._value = value
        return super().setText(str(value))
    
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        return super().mousePressEvent(a0)
    
    def wheelEvent(self, a0: QWheelEvent) -> None:
        self._value_add((a0.angleDelta().y() // 120) * self._step)
        return super().wheelEvent(a0)
    

class SettingsUI(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self._layouts: dict[str, QVBoxLayout] = {}
        
        self.setLayout(layout:=QVBoxLayout())
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        self._layout = layout
        
        for group_name, settings in STRUCTURE.items():
            self._create_group(group_name)
            for setting_name, options in settings.items():
                self._create_setting(group_name, setting_name, options)
        
        
    def _create_group(self, group_name: str) -> None:
        self._layout.addLayout(group_layout := QVBoxLayout())
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)
        
        group_layout.addWidget((name := QLabel(group_name, self)))
        
        self._layouts[group_name] = group_layout

    
    def _create_setting(self, group_name: str, setting_name: str, options: dict[str, Any]) -> None:
        self._layouts[group_name].addLayout(setting_layout := QHBoxLayout())
        setting_layout.setContentsMargins(0, 0, 0, 0)
        setting_layout.setSpacing(0)

        setting_layout.addWidget(name := QLabel(setting_name))

        setting_key: str = options[KEY]
        setting_type: str = options[SETTING_TYPE]
        value_type: type = options[TYPE]
        setting_options: list = options[OPTIONS]

        def get_setting_value(*_, setting_name: str = setting_key) -> Any:
            with contextlib.suppress(Data.NotFound):
                return Data.get_setting(setting_name)

        def set_setting_value(*_, setting_name: str = setting_key, value: Any = None) -> None:
            with contextlib.suppress(Data.NotFound):
                Data.apply_settings(setting_name, value)
            reload(GlobalSettings)

        def reset_setting_value(*_, setting_name: str = setting_key, widget: QSpinBox = None) -> None:
            with contextlib.suppress(Data.NotFound):
                Data.remove_setting(setting_name)
            if widget is not None:
                reload(GlobalSettings)
                widget.setValue(UI_SCALE)

        if setting_type == ENTRY:
            setting_layout.addWidget(entry := QLineEdit())
            entry.setText(str(get_setting_value()))
            entry.textChanged.connect(lambda value: set_setting_value(value=value))
            
        elif setting_type == SPIN:
            if value_type == int:
                spinbox = QSpinBox()
            elif value_type == float:
                spinbox = QDoubleSpinBox()
                
            setting_layout.addWidget(spinbox)
            spinbox.setValue(value if (value:=get_setting_value()) is not None else UI_SCALE)
            spinbox.setRange(0, 10)
            spinbox.setSingleStep(0.1)
            spinbox.valueChanged.connect(lambda value: set_setting_value(value=value))

        setting_layout.addWidget(reset_button := QPushButton("Reset"))
        reset_button.clicked.connect(lambda _: reset_setting_value(widget=spinbox))
        