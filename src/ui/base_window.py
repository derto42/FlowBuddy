from PyQt5.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve
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
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, -10)
        shadow.setBlurRadius(35)
        self.setGraphicsEffect(shadow)

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
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, 0)
        shadow.setBlurRadius(20)
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
            
            layout.addLayout(title_layout:=QHBoxLayout())
            title_layout.setContentsMargins(0, 7, 0, 7)
            title_layout.setSpacing(0)
            # title_layout.addWidget(self._title_label)
            title_layout.addStretch()
            title_layout.addSpacing(15)
            title_layout.addWidget(self.edit_button)
            title_layout.addSpacing(7)
            title_layout.addWidget(self.close_button)
            title_layout.addSpacing(15)
            
            
        layout.addWidget(self._main_layer)
        
        # for redirect layout settings to MainLayer
        self.setLayout = self._main_layer.setLayout
        self.layout = self._main_layer.layout


    def paintEvent(self, a0: QPaintEvent) -> None:
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), CORNER_RADIUS, CORNER_RADIUS)
        painter.fillPath(path, QColor("#FFFFFF"))

        return super().paintEvent(a0)


class BaseWindow(QWidget):
    def __init__(self,
                 add_tab: bool = False,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._offset = None
        
        self.setLayout(layout:=QVBoxLayout(self))
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


    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.LeftButton:
            self._offset = a0.pos()
        return super().mousePressEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._offset is not None and a0.buttons() == Qt.LeftButton:
            self.move(a0.globalPos() - self._offset)
        return super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self._offset = None
        return super().mouseReleaseEvent(a0)
    
    def adjustSize(self) -> None:
        self.animate_resize()
        return super().adjustSize()