from __future__ import annotations
from typing import Optional, Literal
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QRect, QRectF, QVariantAnimation, QEasingCurve, QPoint
from PyQt5.QtWidgets import (
    QGraphicsEffect,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QTabWidget
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QMouseEvent,
    QPen,
    QIcon,
)

from settings import CORNER_RADIUS, apply_ui_scale as scaled
from ui.custom_button import RedButton, YelButton
from ui.utils import get_font

from .title_bar_layer import TitleBarLayer
from .tab_widget import TabWidget


def add_base_window(widget: QWidget | TabWidget, title_bar: Literal["title", "tab"],
                    parent: QWidget | None = None) -> None:
    shadow_layer = QWidget(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    shadow_layer.setAttribute(Qt.WA_TranslucentBackground)
    
    shadow_layer.setLayout(shadow_layer_layout := QVBoxLayout(shadow_layer))
    shadow_layer_layout.setContentsMargins(50, 50, 50, 50)
    shadow_layer_layout.setSpacing(0)

    # create widget for show title bar.
    shadow_layer_layout.addWidget(title_bar_layer := TitleBarLayer(title_bar, shadow_layer)) 
    title_bar_layer.setLayout(title_bar_layer_layout := QVBoxLayout(title_bar_layer))
    title_bar_layer_layout.setContentsMargins(0, 0, 0, 0)
    title_bar_layer_layout.addSpacing(50)

    widget.setParent(title_bar_layer)
    title_bar_layer_layout.addWidget(widget)
    
    # adding shadow that shows in the title bar
    shadow = QGraphicsDropShadowEffect()
    shadow.setColor(QColor(118, 118, 118, 25))
    shadow.setOffset(0, -4.33)
    shadow.setBlurRadius(27)
    widget.setGraphicsEffect(shadow)
    
    # redirecting some functions to shadow_layer.
    widget.show = shadow_layer.show
    widget.hide = shadow_layer.hide
    widget.isHidden = shadow_layer.isHidden
    widget.parent = shadow_layer.parent
    widget.setParent = shadow_layer.setParent
    
    widget.shadow_layer = shadow_layer
    widget.title_bar_layer = title_bar_layer
    widget.shadow_effect = shadow


class Buttons:
    def __init__(self):
        # for linting purposes
        self.title_bar_layer: TitleBarLayer
        
    @property
    def red_button(self):
        (button := self.title_bar_layer.buttons.red_button).show()
        self.title_bar_layer._set_button_position()
        return button

    @property
    def yel_button(self):
        (button := self.title_bar_layer.buttons.yel_button).show()
        self.title_bar_layer._set_button_position()
        return button

    @property
    def grn_button(self):
        (button := self.title_bar_layer.buttons.grn_button).show()
        self.title_bar_layer._set_button_position()
        return button
    
    
class BaseWindow(QWidget, Buttons):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__()
        
        # fot linting
        self.shadow_layer: QWidget
        self.title_bar_layer: TitleBarLayer
        self.shadow_effect: QGraphicsDropShadowEffect
        
        add_base_window(self, "title", parent)


    def setGraphicsEffect(self, effect: QGraphicsEffect) -> None:
        """NOTE: Shadow effect is already applied to this window.\n
        for access the shadow effect, self.shadow_layer."""
        return super().setGraphicsEffect(effect)
    
    
class TabsWindow(TabWidget, Buttons):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__()

        # fot linting
        self.shadow_layer: QWidget
        self.title_bar_layer: TitleBarLayer
        self.shadow_effect: QGraphicsDropShadowEffect

        add_base_window(self, "tab", parent)

    
    @property
    def add_button(self):
        (button := self.title_bar_layer.green_button).show()
        self.title_bar_layer._reset_tab_positions()
        return button


    def setGraphicsEffect(self, effect: QGraphicsEffect) -> None:
        """NOTE: Shadow effect is already applied to this window.\n
        for access the shadow effect, self.shadow_layer."""
        # this function defined here just for add the docstring
        return super().setGraphicsEffect(effect)
        
    
    def addTab(self, widget: QWidget, label: str, icon: QIcon | None = None) -> int:
        # NOTE: index of QTabWidget is tab_id here
        tab_id = super().addTab(widget, label)
        tab_button = self.title_bar_layer.add_tab_button(label, tab_id)
        tab_button.clicked.connect(self.setCurrentIndex)
        self.title_bar_layer.set_tab_focus(self.currentIndex())
        return tab_id

    def removeTab(self, index: int) -> None:
        super().removeTab(index)
        self.title_bar_layer.remove_tab_button(index)
        self.title_bar_layer.set_tab_focus(self.currentIndex())
        
    def setCurrentIndex(self, index: int) -> None:
        self.title_bar_layer.set_tab_focus(index)
        return super().setCurrentIndex(index)

    
    def paintEvent(self, paint_event) -> None:
        painter = QPainter(self)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), x := scaled(CORNER_RADIUS), x)
        painter.end()
