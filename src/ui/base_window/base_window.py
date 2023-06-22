from __future__ import annotations
from typing import Literal
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QGraphicsEffect,
    QWidget,
    QVBoxLayout,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QIcon,
)

from settings import CORNER_RADIUS, apply_ui_scale as scaled
from ui.custom_button import RedButton

from .title_bar_layer import TabButton, TitleBarLayer
from .tab_widget import TabWidget


def add_base_window(widget: QWidget | TabWidget, title_bar: Literal["title", "tab", "hidden"],
                    parent: QWidget | None = None) -> None:
    
    if title_bar not in ["title", "tab", "hidden"]:
        raise ValueError(f"Invalid title_bar option: '{title_bar}'. title_bar should be 'title' or 'tab'")

    shadow_layer = QWidget(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    shadow_layer.setAttribute(Qt.WA_TranslucentBackground)
    
    shadow_layer.setLayout(shadow_layer_layout := QVBoxLayout(shadow_layer))
    shadow_layer_layout.setContentsMargins(x := scaled(50), x, x, x)
    shadow_layer_layout.setSpacing(0)

    # create widget for show title bar.
    shadow_layer_layout.addWidget(title_bar_layer := TitleBarLayer(title_bar, shadow_layer)) 
    title_bar_layer.setLayout(title_bar_layer_layout := QVBoxLayout(title_bar_layer))
    title_bar_layer_layout.setContentsMargins(0, 0, 0, 0)
    if title_bar == "tab": spacing = scaled(50)
    elif title_bar == "title": spacing = scaled(34)
    else: spacing = 0
    title_bar_layer_layout.addSpacing(scaled(spacing))

    widget.setParent(title_bar_layer)
    title_bar_layer_layout.addWidget(widget)
    
    # adding shadow that shows behind the main window.
    main_window_shadow = QGraphicsDropShadowEffect(title_bar_layer)
    main_window_shadow.setColor(QColor(118, 118, 118, 70))
    main_window_shadow.setOffset(0, scaled(10))
    main_window_shadow.setBlurRadius(60)
    title_bar_layer.setGraphicsEffect(main_window_shadow)
    
    # adding shadow that shows in the title bar
    title_bar_shadow = QGraphicsDropShadowEffect()
    title_bar_shadow.setColor(QColor(118, 118, 118, 25))
    title_bar_shadow.setOffset(0, scaled(-4.33))
    title_bar_shadow.setBlurRadius(scaled(27))
    # the shadow doesn't apply to the title bar if the title_bar is "hidden"
    if title_bar != "hidden":
        widget.setGraphicsEffect(title_bar_shadow)
    
    # redirecting some functions to shadow_layer.
    widget.show = shadow_layer.show
    widget.hide = shadow_layer.hide
    widget.isHidden = shadow_layer.isHidden
    widget.parent = shadow_layer.parent
    widget.setParent = shadow_layer.setParent
    
    widget.shadow_layer = shadow_layer
    widget.title_bar_layer = title_bar_layer
    widget.shadow_effect = title_bar_shadow


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
    def __init__(self, hide_title_bar: bool = False, parent: QWidget | None = None) -> None:
        super().__init__()
        
        # fot linting
        self.shadow_layer: QWidget
        self.title_bar_layer: TitleBarLayer
        self.shadow_effect: QGraphicsDropShadowEffect
        
        add_base_window(self, "hidden" if hide_title_bar else "title", parent)


    def set_title(self, title: str) -> None:
        self.title_bar_layer.set_title(title)

    def title(self) -> str:
        return self.title_bar_layer.title()


    def setGraphicsEffect(self, effect: QGraphicsEffect) -> None:
        """NOTE: Shadow effect is already applied to this window.\n
        for access the shadow effect, self.shadow_layer."""
        # this function defined here just for add the docstring
        return super().setGraphicsEffect(effect)
    
    
class TabsWindow(TabWidget, Buttons):
    class TabIndex(int):
        """This class created for access the tab_button and tab_button.red_button from the index of the tab."""
        def __new__(cls, index: int, tab_button: TabButton):
            cls.tab_button = tab_button
            return super().__new__(cls, index)

        @property
        def red_button(self) -> RedButton:
            (button := self.tab_button.red_button).show()
            return button
        
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__()

        # fot linting
        self.shadow_layer: QWidget
        self.title_bar_layer: TitleBarLayer
        self.shadow_effect: QGraphicsDropShadowEffect

        add_base_window(self, "tab", parent)

    
    @property
    def add_button(self):
        (button := self.title_bar_layer.add_button).show()
        self.title_bar_layer._reset_tab_positions()
        return button


    def setGraphicsEffect(self, effect: QGraphicsEffect) -> None:
        """NOTE: Shadow effect is already applied to this window.\n
        for access the shadow effect, self.shadow_layer."""
        # this function defined here just for add the docstring
        return super().setGraphicsEffect(effect)
        
    
    def addTab(self, widget: QWidget, label: str, icon: QIcon | None = None) -> TabsWindow.TabIndex:
        # NOTE: index of QTabWidget is tab_id here
        tab_id = super().addTab(widget, label)
        tab_button = self.title_bar_layer.add_tab_button(label, tab_id)
        tab_button.clicked.connect(self.setCurrentIndex)
        self.title_bar_layer.set_tab_focus(self.currentIndex())
        return TabsWindow.TabIndex(tab_id, tab_button)

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
