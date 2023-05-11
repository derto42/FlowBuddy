import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, QSize, QTimer, QPoint
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
    QShowEvent
)


from .custom_button import RedButton, GrnButton, Button
from .settings import CORNER_RADIUS


class Buddy(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setLayout(layout:=QVBoxLayout(self))
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(0)
        
        layout.addLayout(eye_layout:=QHBoxLayout())
        eye_layout.addWidget(l_button:=RedButton(self))
        eye_layout.addSpacing(12)
        eye_layout.addWidget(r_button:=GrnButton(self))

        layout.addSpacing(10)

        layout.addWidget(smile:=Button(self, custom_size=QSize(47, 18)), alignment=Qt.AlignCenter)
        smile.set_icons("edit_button")
        
        smile.clicked.connect(self.spawn)

        smile.animate = False
        l_button.animate = False
        r_button.animate = False
        
        self._spawner = QVariantAnimation()
        self._spawner.valueChanged.connect(self.move)
        self.easing_curve = QEasingCurve.OutCubic
        self.duration = 500
        
        
    def spawn(self) -> None:
        pos = self.pos()
        self._spawner.setStartValue(pos)
        pos.setY(pos.y()-100)
        self._spawner.setEndValue(pos)
        self._spawner.start()

        
    def paintEvent(self, a0: QPaintEvent) -> None:
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), CORNER_RADIUS, CORNER_RADIUS)
        painter.fillPath(path, QColor("#FFFFFF"))

        return super().paintEvent(a0)
    
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
    
    def showEvent(self, a0: QShowEvent) -> None:
        ret = super().showEvent(a0)
        self.spawn()
        return ret