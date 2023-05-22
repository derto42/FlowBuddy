from typing import Optional, Literal
from PyQt5.QtCore import Qt, QSize, QVariantAnimation, QEasingCurve, QEvent
from PyQt5.QtWidgets import QPushButton, QWidget
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QFontMetrics,
    QPaintEvent,
    QShowEvent,
)


from FileSystem import icon as icon_path
from .utils import get_font
from .settings import CORNER_RADIUS, UI_SCALE


BUTTON_SIZE = {
    "radial": QSize(int(28 * UI_SCALE), int(28 * UI_SCALE)),
    "long": QSize(int(104 * UI_SCALE), int(28 * UI_SCALE)),
}


class Button(QPushButton):
    def __init__(self, parent: Optional[QWidget] = None,
                 button_type: Literal["long", "radial"] = "radial",
                 custom_size: QSize = None):
        super().__init__(parent=parent)
        
        self._size = custom_size if custom_size is not None else BUTTON_SIZE[button_type]
        self._button_type = button_type
        self.animate = False
        
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self._size)
        self.setIconSize(self._size)
        
        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self.set_size)
        self.easing_curve = QEasingCurve.OutBack
        self.duration = 500

    def set_icons(self, icon_name: str) -> None:
        suffix = ("_long" if self._button_type == "long" else "") + ".png"
        self.setStyleSheet(
            (
                """
            QPushButton {
                border: none;
                icon: url(%s);
                margin: 0px;
                padding: 0px;
            }
            QPushButton:hover {
                icon: url(%s);
                margin: 0px;
                padding: 0px;
            }
        """
                % (
                    icon_path(f"{icon_name}{suffix}"),
                    icon_path(f"{icon_name}_hover{suffix}"),
                )
            )
        )
    
    def animate_resize(self, hidden: bool):
        if not self.animate:
            return
        zeero = QSize(1, 1)
        target_size = self._size
        if hidden:
            zeero, target_size = target_size, zeero
        self.animation.setStartValue(zeero)
        self.animation.setEndValue(target_size)

        self.animation.setEasingCurve(self.easing_curve)
        self.animation.setDuration(self.duration)

        self.animation.start()

    def set_size(self, size):
        self.setIconSize(size)
        
    def showEvent(self, a0: QShowEvent) -> None:
        self.animate_resize(hidden=False)
        return super().showEvent(a0)
    
    def setHidden(self, hidden: bool) -> None:
        self.animate_resize(hidden)
        return super().setHidden(hidden)


class RedButton(Button):
    def __init__(self, parent: Optional[QWidget] = None,
                 button_type: Literal["long", "radial"] = "radial"):
        super().__init__(parent = parent, button_type = button_type)
        self.set_icons("red_button")


class YelButton(Button):
    def __init__(self, parent: Optional[QWidget] = None,
                 button_type: Literal["long", "radial"] = "radial"):
        super().__init__(parent = parent, button_type = button_type)
        self.set_icons("yellow_button")


class GrnButton(Button):
    def __init__(self, parent: Optional[QWidget] = None,
                 button_type: Literal["long", "radial"] = "radial"):
        super().__init__(parent = parent, button_type = button_type)
        self.set_icons("green_button")


class TextButton(QPushButton):
    def __init__(self, parent: Optional[QWidget] = None,
                 text: str = "Text Button"):
        super().__init__(parent, text=text)
        self.setCursor(Qt.PointingHandCursor)
        self._x_padding = int(35 * UI_SCALE)
        self._y_padding = int(7 * UI_SCALE)
        self.setFont(get_font(size=int(16 * UI_SCALE)))
        self.setStyleSheet("color: #282828")
        
    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self.text())
        text_height = font_metrics.height()
        button_width = text_width + self._x_padding * 2  # *2 for Adding padding to both sides
        button_height = text_height + self._y_padding * 2
        return QSize(button_width, button_height)
        
    def paintEvent(self, a0: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#DADADA" if self.underMouse() else "#ECECEC"))
        painter.drawRoundedRect(self.rect(), CORNER_RADIUS * UI_SCALE, CORNER_RADIUS * UI_SCALE)
        painter.setPen(self.palette().buttonText().color())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())
