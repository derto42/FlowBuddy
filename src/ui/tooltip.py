from __future__ import annotations
from typing import Literal
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QRectF, QVariantAnimation, QEasingCurve, QPoint, QSize, QAnimationGroup, QRect, QMetaObject
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
    QDialog,
    QApplication,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPaintEvent,
    QMouseEvent,
    QFontMetrics,
    QCursor,
)


from .utils import get_font
from .settings import *


class ToolTip(QWidget):
    def __init__(self, text: str, parent: QWidget = None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        self.text = text
        
        self.setFont(get_font(size=8))
        
        self.setContentsMargins(20, 20, 20, 20)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setColor(QColor(118, 118, 118, 25))
        shadow.setOffset(0, 4)
        shadow.setBlurRadius(14)
        self.setGraphicsEffect(shadow)
        
        self._x_padding = 10
        self._y_padding = 8
        self._width_animation = QVariantAnimation()
        self._width_animation.valueChanged.connect(self.setFixedWidth)
        self._width_animation.setDuration(200)
        self._width_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self._pos_animation = QVariantAnimation()
        self._pos_animation.valueChanged.connect(self.move)
        self._pos_animation.setDuration(200)
        self._pos_animation.setEasingCurve(QEasingCurve.OutCubic)

        self._alpha_animation = QVariantAnimation()
        self._alpha_animation.valueChanged.connect(self._set_alpha)
        self._alpha_animation.setDuration(200)
        
        self._hide_connection = None
        self._alpha: int = 0
        
        # self.show()
        # self.hide()
        
        
    def _set_alpha(self, alpha: int) -> None:
        self._alpha = alpha
    
    def _animate(self, mode: Literal["show", "hide"]) -> None:
        if mode == "show":
            self._setup_show_animation()
        elif mode == "hide":
            self._setup_hide_animation()
        self._width_animation.start()
        self._pos_animation.start()
        self._alpha_animation.start()

    def _setup_show_animation(self):
        self._width_animation.setStartValue(self.width())
        self._width_animation.setEndValue(self.sizeHint().width())
        self._pos_animation.setStartValue(self.pos())
        self._pos_animation.setEndValue(self._position - QPoint(self.sizeHint().width() // 2, 0))
        self._alpha_animation.setStartValue(0)
        self._alpha_animation.setEndValue(255)

        if self._hide_connection is not None:
            self._width_animation.finished.disconnect(self._hide_connection)
            self._hide_connection = None
        
    def _setup_hide_animation(self):
        self._width_animation.setStartValue(self.width())
        self._width_animation.setEndValue(1)
        self._pos_animation.setStartValue(self.pos())
        self._pos_animation.setEndValue(self._position)
        self._alpha_animation.setStartValue(255)
        self._alpha_animation.setEndValue(0)

        self._hide_connection: QMetaObject.Connection = self._width_animation.finished.connect(self.hide)

        
    def setText(self, text: str) -> None:
        self.text = text
        
    def sizeHint(self) -> QSize:
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self.text)
        text_height = font_metrics.height()
        button_width = text_width + self._x_padding * 2  # *2 for Adding padding to both sides
        button_height = text_height + self._y_padding * 2
        return QSize(button_width, button_height)
        
    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(218, 218, 218, self._alpha))  # rgb(218, 218, 218)
        painter.drawRoundedRect(self.rect(), CORNER_RADIUS, CORNER_RADIUS)
        text_color = self.palette().buttonText().color()
        text_color.setAlpha(self._alpha)
        painter.setPen(text_color)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)
        return super().paintEvent(a0)
        
    def _show(self) -> None:
        self._position: QPoint = QCursor.pos() + QPoint(0, 15)
        self.move(self._position)
        self._animate("show")
        self.show()
    
    def _hide(self) -> None:
        self._animate("hide")