from os import path
from types import ModuleType
from typing import Callable, Optional

from PyQt5.QtCore import Qt, QPoint, QRect, QSize, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QEvent
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QGraphicsOpacityEffect,
)
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QBrush,
    QKeySequence,
    QPaintEvent,
    QMouseEvent,
    QFontMetrics,
    QPixmap,
)

from ui.settings import UI_SCALE
from ui.utils import get_font

from FileSystem import icon as get_icon, abspath
from SaveFile import apply_settings, get_setting, remove_setting, NotFound

from addon import AddOnBase, add_on_paths


# Constants
SAVE_JSON = 'launcher.json'
BUTTON_WIDTH = 110
BUTTON_HEIGHT = 30
BUTTON_OFFSET = 120
GRID_OFFSET = 30


def check_setting(name: str) -> bool:
    try:
        get_setting(name)
    except NotFound:
        return False
    return True


class IconButton(QPushButton):
    def __init__(self, parent: QWidget, icon_path: str, hover_icon_path: str) -> None:
        super().__init__(parent)
        
        self._icon = icon_path
        self._hover_icon = hover_icon_path
        
        self.setFixedSize(QSize(85, 85))
        self.setIconSize(QSize(85, 85))
        
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
                    self._icon,
                    self._hover_icon,
                )
            )
        )


class ShortcutLabel(QWidget):
    
    class Label(QLabel):
        def __init__(self, text: str, parent: Optional[QWidget] = None):
            super().__init__(text, parent)
            
            self.is_plus = text == "+"
            
            self.setFont(get_font(size=11, weight="semibold"))
            self.setFixedSize(self.sizeHint())
            
        def sizeHint(self):
            font_metrics = QFontMetrics(self.font())
            text_width = font_metrics.width(self.text())
            text_height = font_metrics.height()
            button_width = text_width + 7 * 2  # *2 for Adding padding to both sides
            button_height = text_height + 1 * 2
            return QSize(button_width, button_height)
            
        def paintEvent(self, a0: QPaintEvent) -> None:
            back_color = QColor(0, 0, 0, 0) if self.is_plus else QColor("#ECECEC")
            text_color = QColor("#ECECEC") if self.is_plus else self.palette().buttonText().color()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(back_color)  # default color #ECECEC
            painter.drawRoundedRect(self.rect(), 5 * UI_SCALE, 5 * UI_SCALE)
            painter.setPen(text_color)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
            
            
    def __init__(self, parent: QWidget, shortcut: QKeySequence):
        super().__init__(parent)
        
        keys = QKeySequence(shortcut[0]).toString().split("+")
        self.shortcut_keys = [x.upper() for y in keys for x in (y, "+")][:-1]
        
        self.setLayout(layout := QHBoxLayout(self))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        layout.addStretch()

        for key in self.shortcut_keys:
            label = self.Label(key)
            layout.addWidget(label)

        layout.addStretch()
        
        self.adjustSize()


class GroupWidget(QWidget):
    def __init__(self, parent: QWidget, title: str, icon_path: str, hover_icon_path: str,
                 shortcut: QKeySequence, activate_callback: Callable) -> None:
        super().__init__(parent)
        
        self.setFixedWidth(85 + 40)
        
        self.icon_button = IconButton(self, icon_path, hover_icon_path)
        self.icon_button.clicked.connect(activate_callback)
        self.icon_button.setGeometry(QRect(20, 0, self.icon_button.width(), self.icon_button.height()))
        
        self.title_label = QLabel(title, self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(get_font(size = int(12 * UI_SCALE), weight="medium"))
        self.title_label.setStyleSheet("QLabel { color : #ECECEC }")
        self.title_label.setGeometry(QRect(0, 85+11, self.width(), self.title_label.height()))

        self.hotkey_label = ShortcutLabel(self, shortcut)
        self.hotkey_label.setGeometry(QRect(0, 85+17+17+self.title_label.sizeHint().height(),
                                            self.width(),
                                            self.hotkey_label.height()))
        
        self.adjustSize()
        
        self.move(QPoint(self.x(), 80))
        self.hide()
        
        self.finished_callback = None
        
        self.opacity = QGraphicsOpacityEffect()
        self.opacity.setOpacity(0.0)
        self.setGraphicsEffect(self.opacity)

        self.opacity_animation = QPropertyAnimation(self.opacity, b"opacity")
        self.opacity_animation.setDuration(500)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(500)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.animation = QParallelAnimationGroup()
        self.animation.addAnimation(self.pos_animation)
        self.animation.addAnimation(self.opacity_animation)
        self.animation.finished.connect(lambda: self.finished_callback())

    def spawn(self) -> None:
        self.animation.stop()
        self.show()
        self.finished_callback = self.after_spawn
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(self.x(), 40))
        self.opacity_animation.setStartValue(self.opacity.opacity())
        self.opacity_animation.setEndValue(1.0)
        self.animation.start()
        
        
    def kill(self) -> None:
        self.animation.stop()
        self.finished_callback = self.after_kill
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(self.x(), 80))
        self.opacity_animation.setStartValue(self.opacity.opacity())
        self.opacity_animation.setEndValue(0.0)
        self.animation.start()
        
        
    def after_spawn(self) -> None:
        pass
    
    def after_kill(self) -> None:
        self.hide()


class LowerWidget(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.icon: QPixmap = QPixmap(get_icon("icon.png")).scaled(45, 45,
                                                                  Qt.AspectRatioMode.KeepAspectRatio,
                                                                  Qt.TransformationMode.SmoothTransformation)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(self.icon)
        
        self.title_label = QLabel("FlowBuddy", self)
        self.title_label.setFont(get_font(size=16, weight="semibold"))
        self.title_label.setStyleSheet("QLabel { color : #ECECEC }")
        self.title_label.move(53, 5)

        self.setFixedSize(177, 45)
        
        self.pos_animation = QPropertyAnimation(self, b"pos")
        self.pos_animation.setDuration(500)
        self.pos_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.opacity = QGraphicsOpacityEffect()
        self.opacity.setOpacity(1.0)
        self.setGraphicsEffect(self.opacity)
        self.opacity_animation = QPropertyAnimation(self.opacity, b"opacity")
        self.opacity_animation.setDuration(500)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.animation = QParallelAnimationGroup()
        self.animation.addAnimation(self.pos_animation)
        self.animation.addAnimation(self.opacity_animation)
        
        
    def spawn(self) -> None:
        self.animation.stop()
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(self.x(), 13))
        self.opacity_animation.setStartValue(self.opacity.opacity())
        self.opacity_animation.setEndValue(1.0)
        self.animation.start()
    
    def kill(self) -> None:
        self.animation.stop()
        self.pos_animation.setStartValue(self.pos())
        self.pos_animation.setEndValue(QPoint(self.x(), 26))
        self.opacity_animation.setStartValue(self.opacity.opacity())
        self.opacity_animation.setEndValue(0.0)
        self.animation.start()


class MainWindow(QMainWindow):
    def __init__(self, add_ons: dict[str, ModuleType]) -> None:
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._offset = None
        self._moved = False
        self.maximized = False
        self.widgets: list[GroupWidget] = []

        self.lower_position = QPoint(get_setting("lower_position")[0], get_setting("lower_position")[1]) \
                                  if check_setting("lower_position") else \
                                  QPoint(QApplication.desktop().width() // 2 - (40+40+177) // 2, QApplication.desktop().height() - 100 - (13+13+45) // 2)

        self.upper_position = QPoint(get_setting("upper_position")[0], get_setting("upper_position")[1]) \
                                  if check_setting("upper_position") else \
                                  self.pos()

        for add_on_name in add_ons:
            title = add_on_name.split(".")[-1]

            add_on_path = path.dirname(add_on_paths[add_on_name])
            if icon_path:=abspath(f"{add_on_path}/icon.png"):
                icon_path = icon_path.replace("\\", "/")
            else:
                icon_path = get_icon("default_launcher_icon.png")
            hover_icon_path = icon_path
            add_on_base_instance = AddOnBase.instances[add_on_name]
            activate = add_on_base_instance.activate
            shortcut = add_on_base_instance.activate_shortcut

            self.add_widget(title, hover_icon_path, hover_icon_path, shortcut, activate)
        self.lower_widget = LowerWidget(self)
        self.lower_widget.move(40, 13)

        self.setGeometry(QRect(self.lower_position, QPoint(40+40+177, 13+13+45) + self.lower_position))


        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        
    def get_window_size(self) -> QSize:
        return QSize(((85+20+20) * len(self.widgets)) + 20+20, 164+40+40)
    
    def get_next_widget_position(self) -> QPoint:
        return QPoint(((85+20+20) * len(self.widgets)) + 20, 40)
        
    def add_widget(self, title: str, icon_path: str, hover_icon_path: str,
                   shortcut: QKeySequence, activate_callback: Callable) -> None:
        widget = GroupWidget(self, title, icon_path, hover_icon_path, shortcut, activate_callback)
        widget.move(self.get_next_widget_position())
        self.widgets.append(widget)
        
    def maximize(self) -> None:
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.upper_position,
                                         QPoint(self.get_window_size().width(),
                                                self.get_window_size().height()) + self.upper_position))
        self.animation.start()
        self.lower_widget.kill()
        for widget in self.widgets:
            widget.spawn()
        self.maximized = True

    def minimize(self) -> None:
        self.animation.stop()
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(self.lower_position, QPoint(40+40+177, 13+13+45) + self.lower_position))
        self.animation.start()
        self.lower_widget.spawn()
        for widget in self.widgets:
            widget.kill()
        self.maximized = False
        
        
    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 178)))
        painter.drawRoundedRect(self.rect(), 32 * UI_SCALE, 32 * UI_SCALE)

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        if a0.button() == Qt.MouseButton.LeftButton:
            self._offset = a0.pos()
        return super().mousePressEvent(a0)
    
    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._offset is not None and a0.buttons() == Qt.MouseButton.LeftButton:
            self.move(a0.globalPos() - self._offset)
            self._moved = True
        return super().mouseMoveEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if self._moved:
            if self.maximized:
                self.upper_position = self.pos()
                apply_settings("upper_position", [self.upper_position.x(), self.upper_position.y()])
            else:
                self.lower_position = self.pos()
                apply_settings("lower_position", [self.lower_position.x(), self.lower_position.y()])
        else:
            if self.maximized:
                self.minimize()
            else:
                self.maximize()
        self._moved = False
        self._offset = None
        return super().mouseReleaseEvent(a0)



if __name__ == '__main__':
    import sys
    
    app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    
    # widget2 = ShortcutLabel(parent = None, shortcut=QKeySequence(Qt.CTRL | Qt.Key.Key_S))
    # widget2.show()
    
    # widget = GroupWidget(None)
    # widget.show()

    # window = MainWindow({"Name 1": None, "Name 2": None, "Name 3": None, "Name 4": None})
    # widget2 = GroupWidget(window, "Title", "src/addons/shortcuts/icon.png", "src/addons/shortcuts/icon.png")
    # widget2.move(20, 40)
    # window.show()
    
    # wid = LowerWidget(None)
    # wid.show()

    sys.exit(app.exec_())