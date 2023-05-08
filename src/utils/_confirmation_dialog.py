from __future__ import annotations
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QDialog,
    )
from PyQt5.QtGui import (
    QFont,
    QFontDatabase,
    QPainter,
    QColor,
    QFontMetrics,
    QPaintEvent,
    QPainterPath,
    QPen,
    QMouseEvent,
    QKeyEvent,
)


import FileSystem



class CustomButton(QPushButton): 
    def __init__(self, text, padding=22):
        super().__init__(text)
        self.setFont(get_custom_font("Montserrat-Medium.ttf", size=16))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #DADADA;")
        self.padding = padding
        self.setCursor(QtCore.Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QtCore.Qt.NoPen)

        if self.underMouse():
            painter.setBrush(QColor(self.property("hover_color")))
        else:
            painter.setBrush(self.palette().button())

        painter.drawRoundedRect(self.rect(), 14, 14)
        painter.setPen(self.palette().buttonText().color())
        painter.drawText(self.rect(), QtCore.Qt.AlignCenter, self.text())

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self.text())
        button_width = text_width + self.padding * 2  # Adding padding to both sides
        return QtCore.QSize(button_width, 44)


def get_custom_font(font_name: str, size: int) -> QFont:
    font_file = FileSystem.font(font_name)
    font_id = QFontDatabase.addApplicationFont(font_file)
    if font_families := QFontDatabase.applicationFontFamilies(font_id):
        font = QFont(font_families[0], size)
        if "Bold" in font_name:
            font.setWeight(QFont.Bold)
        elif "Medium" in font_name:
            font.setWeight(QFont.Medium)
        return font
    else:
        print(f"Error: Failed to load font '{font_file}'")
        return QFont("Helvetica", size)


class ConfirmationDialog(QDialog):
    def __init__(self, parent: QWidget | None = None,
                 text: str = "Confirmation",
                 flags: QtCore.Qt.WindowFlags | QtCore.Qt.WindowType = 
                            QtCore.Qt.Dialog |
                            QtCore.Qt.WindowCloseButtonHint |
                            QtCore.Qt.FramelessWindowHint) -> None:
        super().__init__(parent, flags)
        
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        
        self.setLayout(layout := QVBoxLayout())
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)

        layout.addWidget(title_label := QLabel(), alignment=QtCore.Qt.AlignCenter)
        title_label.setFont(get_custom_font("Montserrat-Bold.ttf", 12))
        title_label.setText(text)

        layout.addLayout(button_layout := QHBoxLayout())
        
        button_layout.addStretch(1)
        button_layout.addWidget(cancel_button := CustomButton(""))
        button_layout.addSpacing(10)
        button_layout.addWidget(ok_button := CustomButton(""))
        button_layout.addStretch(1)
        
        cancel_button.setProperty("hover_color", "#FFA0A0")
        cancel_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        cancel_button.setFixedSize(75, 24)
        cancel_button.setDefault(False)
        cancel_button.clicked.connect(self.reject)

        ok_button.setProperty("hover_color", "#ACFFBE")
        ok_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        ok_button.setFixedSize(75, 24)
        ok_button.setDefault(True)
        ok_button.clicked.connect(self.accept)
        
        
    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QtCore.QRectF(self.rect().adjusted(0, 0, -1, -1)), 12, 12)
        painter.fillPath(path, QColor(QtCore.Qt.white))

        # Adding the stroke around the window
        stroke_color = QColor("#DADADA")
        painter.setPen(QPen(stroke_color, 2))
        painter.drawPath(path)
        return super().paintEvent(a0)
    
    
    def mousePressEvent(self, a0: QMouseEvent):
        if a0.button() == QtCore.Qt.LeftButton:
            self.moving = True
            self.offset = a0.pos()
        return super().mousePressEvent(a0)

    def mouseMoveEvent(self, a0: QMouseEvent):
        if self.moving:
            self.move(a0.globalPos() - self.offset)
        return super().mouseMoveEvent(a0)
    
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() in [QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return]:
            self.accept()
        elif a0.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()
        return super().keyPressEvent(a0)