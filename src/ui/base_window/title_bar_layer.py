from __future__ import annotations
from typing import Optional, Literal
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QSize, QRect, QRectF, QVariantAnimation, QEasingCurve, QPoint, QObject, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QMouseEvent,
    QPen,
)

from settings import apply_ui_scale as scaled, CORNER_RADIUS
from ui.custom_button import RedButton, YelButton, GrnButton
from ui.utils import get_font


class Direction(int):
    Forward = 1
    Backward = -1
        

class TabButton(QWidget):
    tab_moved = pyqtSignal(int)
    clicked = pyqtSignal(int)
    
    def __init__(self, tab_id: int, title: str, parent: QWidget | None = None):
        super().__init__(parent)

        self._parent = parent
        self._offset = None
        self._last_postition = None
        self.tab_id: int = tab_id
        self.focused: bool = False
        self.title: str = title
        
        self.setFont(get_font(size=scaled(16)))

        red_button = RedButton(self, "radial")
        red_button.move(QPoint(self.size().width() - scaled(22 + 10), scaled(8)))
        red_button.setIconSize(size := scaled(QSize(22, 22)))
        red_button.setFixedSize(size)
        
        self.setFixedSize(self.size())
        
        
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setOffset(0, 4.3)
        self.shadow_effect.setBlurRadius(16)
        
        self.setGraphicsEffect(self.shadow_effect)
        
        self.set_focused(self.focused)  # updating the shadow color


    def set_focused(self, focused: bool) -> None:
        self.focused = focused
        self.shadow_effect.setColor(QColor(118, 118, 118, 63 if focused else 0))
        if focused: self.raise_()
        
    def set_title(self, title: str) -> None:
        self.title = title


    @staticmethod
    def get_tab_button_position(index: int) -> QPoint:
        return QPoint(scaled(20) + (TabButton.size().width() + scaled(16)) * scaled(index), scaled(6))


    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawRoundedRect(0, 0, self.size().width(), self.size().height(),
                                scaled(12), scaled(12))
        painter.setPen(QPen(self.palette().text().color()))
        painter.drawText(self.rect().adjusted(scaled(20), scaled(5), -scaled(52), 0),
                         Qt.AlignmentFlag.AlignLeft, self.title)


    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self._offset = a0.pos()
        self.clicked.emit(self.tab_id)
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._offset is not None and a0.buttons() == Qt.LeftButton:
            new_pos_x = self.mapToParent(a0.pos() - self._offset).x()

            # make sure the new position is within the self._parent widget
            if new_pos_x < 0:
                new_pos_x = 0
            elif new_pos_x + self.width() > self._parent.size().width():
                new_pos_x = self._parent.size().width() - self.width()

            self.tab_moved.emit(self.tab_id)
                
            self.move(new_pos_x, self.y())

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self._offset = None
        self.tab_moved.emit(self.tab_id)  # for update the positions of dragging TabButton
    

    @staticmethod
    def size() -> QSize:
        return scaled(QSize(175, 38))


class Buttons(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setLayout(QHBoxLayout(self))
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(scaled(9))
        self.red_button = RedButton(self, "radial")
        self.yel_button = YelButton(self, "radial")
        self.grn_button = GrnButton(self, "radial")
        self.layout().addWidget(self.grn_button)
        self.layout().addWidget(self.yel_button)
        self.layout().addWidget(self.red_button)
        self.red_button.hide()
        self.yel_button.hide()
        self.grn_button.hide()


class TitleBarLayer(QWidget):
    def __init__(self, title_bar: Optional[Literal["title", "tab"]] = None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        if title_bar not in ["title", "tab"]:
            raise ValueError(f"Invalid title_bar option: '{title_bar}'. title_bar should be 'title' or 'tab'")

        self._parent = parent
        self.mode = title_bar
        self._offset_for_drag = None
        
        self.buttons = Buttons(self)
        self._set_button_position()
        
        if self.mode == "title":
            self._init_for_title()
        else:
            self._init_for_tabs()
            
            
        # adding shadow
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setColor(QColor(118, 118, 118, 70))
        shadow_effect.setOffset(0, 10)
        shadow_effect.setBlurRadius(60)
        self.setGraphicsEffect(shadow_effect)  # XXX: should be removed
        
        self.setFixedSize(600, 300)  # XXX: should be removed
            

    def _init_for_title(self) -> None:
        """initialize title bar for title."""
        # XXX add stuff here for show title
        # XXX add close and edit buttons (should be accessible from instance of BaseWindow)
        self.add_tab_button = lambda widget, title, index: print(f"""WARNING: tab with {title=} {index=} not created. 
                                                                 this BaseWindow is not tabs implemented.""")

    def _init_for_tabs(self) -> None:
        """initialize title bar for tabs."""
        self.tabs: dict[int, TabButton] = {}
        self.tabs_order: list[int] = []

    def _tab_moving(self, tab_id: int):
        """Checks if the tab is moved more than a specified amount and changes the order of the tabs."""
        current_order = self.tabs_order.index(tab_id)
        changed = self.tabs[tab_id].x() - TabButton.get_tab_button_position(current_order).x()
        max_different = TabButton.size().width() * 0.6

        if changed >= max_different:
            # if the tab is moved forward more than 0.6 the size of the TabButton
            self.move_tab(current_order, current_order + 1)
            
        elif -changed >= max_different:
            # if the tab is moved backward more than 0.6 the size of the TabButton
            self.move_tab(current_order, current_order - 1)
            
        # check if the tab is still moving
        if self.tabs[tab_id]._offset is None:
            self._reset_tab_positions()

    def _reset_tab_positions(self) -> None:
        """Re sets the position of the tab buttons."""
        for index, tab_id in enumerate(self.tabs_order):
            tab: TabButton = self.tabs[tab_id]
            pos = tab.get_tab_button_position(index)
            if tab._offset is None and tab.pos() != pos:  # check if the tab is being dragged.
                tab.move(pos)

    def _set_button_position(self) -> None:
        self.buttons.adjustSize()
        self.buttons.move(self.width() - self.buttons.width() - scaled(20), scaled(50)//2 - self.buttons.height()//2)


    def add_tab_button(self, title: str, tab_id: int) -> TabButton:
        """Adds new tab button to the title bar."""

        tab_button = TabButton(tab_id, title, self)
        tab_button.move(TabButton.get_tab_button_position(tab_id))
        tab_button.show()
        self.tabs[tab_id] = tab_button
        self.tabs_order.append(tab_id)
        tab_button.tab_moved.connect(self._tab_moving)
        tab_button.clicked.connect(self.set_tab_focus)
        return tab_button
        
    def remove_tab_button(self, tab_id: int) -> None:
        """Removes the tab button from the title bar."""
        tab_button = self.tabs[tab_id]
        tab_button.hide()
        tab_button.deleteLater()
        del self.tabs[tab_id]
        del self.tabs_order[tab_id]
        self._reset_tab_positions()

    def move_tab(self, current_pos: int, move_to: int) -> None:
        """Moves the position of the tab button."""
        self.tabs_order.insert(move_to, self.tabs_order.pop(current_pos))
        self._reset_tab_positions()

    def set_tab_focus(self, tab_id: int) -> None:
        if self.tabs[tab_id].focused:
            return
        for _tab_id, _tab_button in self.tabs.items():
            if _tab_id == tab_id:
                _tab_button.set_focused(True)
            else:
                _tab_button.set_focused(False)


    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), x:=scaled(CORNER_RADIUS), x)

    
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self._offset_for_drag = a0.pos()
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._offset_for_drag is None: return
        content_margins = self._parent.layout().contentsMargins()
        self._parent.move(a0.globalPos() - self._offset_for_drag -
                          QPoint(content_margins.left(), content_margins.top()))
    
    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self._offset_for_drag = None

    def resizeEvent(self, QResizeEvent) -> None:
        self._set_button_position()
        return super().resizeEvent(QResizeEvent)
