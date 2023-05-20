from __future__ import annotations
from PyQt5.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, QPoint
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
)

from .settings import *
from .custom_button import *
from .utils import get_font



class MainLayer(QWidget):
    def __init__(self, parent: InnerPart) -> None:
        super().__init__(parent)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(118, 118, 118, 25))
        shadow.setOffset(0, -4.33)
        shadow.setBlurRadius(27)
        self.setGraphicsEffect(shadow)
        
        self.setContentsMargins(int(20 * UI_SCALE), int(12 * UI_SCALE), int(20 * UI_SCALE), int(20 * UI_SCALE))

    def paintEvent(self, a0: QPaintEvent) -> None:
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), CORNER_RADIUS, CORNER_RADIUS)
        painter.fillPath(path, QColor("#FFFFFF"))
        
        return super().paintEvent(a0)


class InnerPart(QWidget):
    def __init__(self,
                 add_tab: bool = False,
                 parent: BaseWindow = None) -> None:
        super().__init__(parent)

        self._parent = parent

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(118, 118, 118, 70))
        shadow.setOffset(0, 10)
        shadow.setBlurRadius(60)
        self.setGraphicsEffect(shadow)

        self.setLayout(layout:=QVBoxLayout(self))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._main_layer = MainLayer(self)
        
        if add_tab:
            self._title_label = QLabel(self, text="")
            self._title_label.setFont(get_font())
            
            self.edit_button = YelButton(self)
            self.close_button = RedButton(self)

            self.edit_button.setToolTip("Edit Window")
            self.close_button.setToolTip("Close Window")
            
            layout.addLayout(title_layout:=QHBoxLayout())
            title_layout.setContentsMargins(0, int(10 * UI_SCALE), 0, int(10 * UI_SCALE))
            title_layout.setSpacing(0)
            # title_layout.addWidget(self._title_label)
            title_layout.addStretch()
            title_layout.addSpacing(int(15 * UI_SCALE))
            title_layout.addWidget(self.edit_button)
            title_layout.addSpacing(int(9 * UI_SCALE))
            title_layout.addWidget(self.close_button)
            title_layout.addSpacing(int(20 * UI_SCALE))
            
            
        layout.addWidget(self._main_layer)
        
        # for redirect layout settings to MainLayer
        self.setLayout = self._main_layer.setLayout
        self.layout = self._main_layer.layout


    def paintEvent(self, a0: QPaintEvent) -> None:
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), CORNER_RADIUS * UI_SCALE, CORNER_RADIUS * UI_SCALE)
        painter.fillPath(path, QColor("#F6F6F6"))

        return super().paintEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self._parent._offset = a0.pos()
        return super().mousePressEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._parent._offset is not None and a0.buttons() == Qt.LeftButton:
            margin_offset = QPoint(self._parent._margin_for_shadow, self._parent._margin_for_shadow)
            self._parent.move(a0.globalPos() - self._parent._offset - margin_offset)
        return super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self._parent._offset = None
        return super().mouseReleaseEvent(a0)
    

class BaseWindow(QWidget):
    def __init__(self,
                 add_tab: bool = False,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._offset = None
        self._margin_for_shadow = mrgn = 25
        
        self.setLayout(layout:=QVBoxLayout(self))
        layout.setContentsMargins(mrgn, mrgn, mrgn, mrgn) # margin for shadow
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(inner:=InnerPart(add_tab, self))
        
        self.setLayout = inner._main_layer.setLayout
        self.layout = inner._main_layer.layout
        if add_tab:
            inner.edit_button.clicked.connect(self.on_edit_button_clicked)
            inner.close_button.clicked.connect(self.on_close_button_clicked)
        
        self._animation = QVariantAnimation()
        self._animation.valueChanged.connect(self.setFixedSize)
        self.easing_curve = QEasingCurve.OutBack
        self.duration = 500

        self.animate = False

        
    def on_edit_button_clicked(self, event) -> None:
        return
    
    def on_close_button_clicked(self, event) -> None:
        self.hide()
        
    def animate_resize(self):
        if not self.animate: return
        target_size = self.minimumSizeHint()
        old_size = self.size()

        self._animation.setStartValue(old_size)
        self._animation.setEndValue(target_size)

        self._animation.setEasingCurve(self.easing_curve)
        self._animation.setDuration(self.duration)

        self._animation.start()


    def adjustSize(self) -> None:
        self.animate_resize()
        return super().adjustSize()