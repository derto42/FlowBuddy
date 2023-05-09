from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFontMetrics
)

from utils import get_font

class CustomButton(QPushButton):
    def __init__(self, text, padding=22):
        super().__init__(text)
        self.setFont(get_font(size=16))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #DADADA;")
        self.padding = padding
        self.setCursor(Qt.PointingHandCursor)


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.underMouse():
            painter.setBrush(QColor(self.property("hover_color")))
        else:
            painter.setBrush(self.palette().button())

        painter.drawRoundedRect(self.rect(), 14, 14)
        painter.setPen(self.palette().buttonText().color())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self.text())
        button_width = text_width + self.padding * 2  # Adding padding to both sides
        # Setting fixed height including top and bottom padding
        return QSize(button_width, 44)