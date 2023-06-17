from os import path
from math import ceil
from types import ModuleType
from typing import Callable, Optional

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRect,
    QSize,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QWidget,
    QHBoxLayout,
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

from settings import apply_ui_scale as scaled
from ui.utils import get_font

from FileSystem import icon as get_icon, abspath
from SaveFile import apply_setting, get_setting, remove_setting, NotFoundException
from utils import HotKeys

from addon import AddOnBase, add_on_paths


def check_setting(name: str) -> bool:
    try:
        get_setting(name)
    except NotFoundException:
        return False
    return True


class IconButton(QPushButton):
    def __init__(self, parent: QWidget, icon_path: str, hover_icon_path: str) -> None:
        super().__init__(parent)
        
        self._icon = icon_path
        self._hover_icon = hover_icon_path
        
        self.setFixedSize(QSize(scaled(100), scaled(100)))
        self.setIconSize(QSize(scaled(100), scaled(100)))
        
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
            
            self.setFont(get_font(size=scaled(11), weight="semibold"))
            self.setFixedSize(self.sizeHint())
            
        def sizeHint(self):
            font_metrics = QFontMetrics(self.font())
            text_width = font_metrics.width(self.text())
            text_height = font_metrics.height()
            button_width = text_width + 7 * 2  # *2 for Adding padding to both sides
            button_height = text_height + 1 * 2
            return QSize(scaled(button_width), scaled(button_height))
            
        def paintEvent(self, a0: QPaintEvent) -> None:
            back_color = QColor(0, 0, 0, 0) if self.is_plus else QColor("#ECECEC")
            text_color = QColor("#ECECEC") if self.is_plus else self.palette().buttonText().color()
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(back_color)  # default color #ECECEC
            painter.drawRoundedRect(self.rect(), scaled(5), scaled(5))
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
    animating: int = 0
    
    def __init__(self, parent: QWidget, index: int, title: str, icon_path: str, hover_icon_path: str,
                 shortcut: QKeySequence, activate_callback: Callable) -> None:
        super().__init__(parent)
        
        self.index = index
        self.setFixedWidth(scaled(100 + 40))  # 40 padding
        
        self.icon_button = IconButton(self, icon_path, hover_icon_path)
        self.icon_button.clicked.connect(activate_callback)
        self.icon_button.setGeometry(QRect(scaled(20), 0, self.icon_button.width(), self.icon_button.height()))
        
        self.title_label = QLabel(title, self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(get_font(size = scaled(12), weight="medium"))
        self.title_label.setStyleSheet("QLabel { color : #ECECEC }")
        self.title_label.setGeometry(QRect(0, scaled(85+11), self.width(), self.title_label.height() + scaled(10)))

        if shortcut is not None:
            self.hotkey_label = ShortcutLabel(self, shortcut)
            self.hotkey_label.setGeometry(QRect(0, scaled(90+17+17)+self.title_label.sizeHint().height(),
                                                self.width(),
                                                self.hotkey_label.height()))
        
        self.adjustSize()
        self.move(self.get_widget_position(self.index))
        

    @staticmethod
    def get_widget_position(index: int) -> QPoint:
        """Returns the position of the GroupWidget for main window according to the given index."""
        # 4 is the maximum number of widgets for each line
        x = (4 if (_x:=index % 4) == 0 else _x) - 1
        y = ceil(index / 4) - 1
        position = QPoint(GroupWidget.size().width() * x, (GroupWidget.size().height() + scaled(40)) * y)
        return position + QPoint(scaled(20), scaled(40))  # adding left and top padding
        
    
    # setting fixed size of GroupWidget
    @staticmethod
    def size() -> QSize:
        # Note: this widgets exact size is 85, 164. 20 is added to the margins.
        # this values don't effect the size of the GroupWidget
        return QSize(scaled(100+20+20), scaled(164))


class LowerWidget(QMainWindow):
    window_toggle_signal = pyqtSignal()
    
    def __init__(self, add_ons: dict[str, ModuleType]) -> None:
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        
        self._offset = None
        self._moved = False
        
        self.window_toggle_signal.connect(self.toggle_windows)
        
        self.lower_position = QPoint(get_setting("lower_position")[0], get_setting("lower_position")[1]) \
                              if check_setting("lower_position") else \
                              QPoint(QApplication.desktop().width() // 2 - self.size().width() // 2,
                                     QApplication.desktop().height() - self.size().height() - 200)


        self.icon: QPixmap = QPixmap(get_icon("icon.png")).scaled(scaled(35), scaled(35),
                                                                  Qt.AspectRatioMode.KeepAspectRatio,
                                                                  Qt.TransformationMode.SmoothTransformation)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(self.icon)
        self.icon_label.setGeometry(scaled(40), scaled(13), scaled(35), scaled(35))
        
        self.title_label = QLabel("FlowBuddy", self)
        self.title_label.setFont(get_font(size=scaled(16), weight="medium"))
        self.title_label.setStyleSheet("QLabel { color : #ECECEC }")
        self.title_label.move(scaled(53 + 40), scaled(5 + 13))
        self.title_label.adjustSize()

        self.setFixedSize(self.size())
        
        
        self.main_window = MainWindow(add_ons)
        
        hotkey = get_setting("hotkey") if check_setting("hotkey") else "<Ctrl>+`"
        HotKeys.add_global_shortcut(hotkey, self.window_toggle_signal.emit)

        self.move(self.lower_position)
        self.setHidden(get_setting("lower-hidden")) if check_setting("lower-hidden") else self.show()
        self.main_window.setHidden(get_setting("upper-hidden")) if check_setting("upper-hidden") else self.show()
        

    def toggle_windows(self) -> None:
        if self.isHidden():
            for window in self.active_windows:
                window.show()
        else:
            self.active_windows = [x for x in QApplication.allWindows() if x.isVisible()]
            for window in self.active_windows:
                window.hide()
                
    
    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 178)))
        painter.drawRoundedRect(self.rect(), scaled(32), scaled(32))
    
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
            self.lower_position = self.pos()
            apply_setting("lower_position", [self.lower_position.x(), self.lower_position.y()])
        else:
            self.main_window.setHidden(not self.main_window.isHidden())
        self._moved = False
        self._offset = None
        return super().mouseReleaseEvent(a0)
    
    
    def show(self) -> None:
        apply_setting("lower-hidden", False)
        return super().show()
    
    def hide(self) -> None:
        apply_setting("lower-hidden", True)
        return super().hide()
    
    def setHidden(self, hidden: bool) -> None:
        apply_setting("lower-hidden", hidden)
        return super().setHidden(hidden)

    
    # setting fixed size of LowerWidget
    @staticmethod
    def size() -> QSize:
        # Note: this widgets exact size is 177, 35. 40, 13 is added to the margins.
        # this values don't effect the size of the LowerWidget
        return QSize(scaled(177+40+40), scaled(35+13+13))


class MainWindow(QWidget):
    def __init__(self, add_ons: dict[str, ModuleType], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._offset = None
        self._moved = False
        self.maximized = False
        self.widgets: list[GroupWidget] = []
        self.active_windows = []
        
        for index, add_on_name in enumerate(add_ons, 1):
            self.add_widget(index, add_on_name)

        self.upper_position = QPoint(get_setting("upper_position")[0], get_setting("upper_position")[1]) \
                              if check_setting("upper_position") else \
                              QPoint(QApplication.desktop().width() // 2 - self.get_window_size().width() // 2,
                                     QApplication.desktop().height() - self.get_window_size().height() - 150)

        self.setGeometry(QRect(self.upper_position, self.get_window_size()))

        
    def get_window_size(self) -> QSize:
        """Returns the size of the window acording to the GroupWidgets created."""
        len_of_widgets = len(self.widgets)
        x = min(len_of_widgets, 4)
        y = ceil(len_of_widgets / 4)
        window_size = QSize(GroupWidget.size().width() * x, (GroupWidget.size().height() + scaled(40)) * y - scaled(40))
        return window_size + QSize(scaled(20+20), scaled(40+40))  # adding left, right, top and bottom padding
        
        
    def add_widget(self, index: int, add_on_name: str) -> None:
        """Adds a new GroupWidget to the main window."""
        
        title = add_on_name.split(".")[-1].replace("_", " ").title()

        add_on_path = path.dirname(add_on_paths[add_on_name])
        if icon_path := abspath(f"{add_on_path}/icon.png"):
            icon_path = icon_path.replace("\\", "/")
        else:
            icon_path = get_icon("default_launcher_icon.png")
        hover_icon_path = icon_path
        add_on_base_instance = AddOnBase(add_on_name)
        activate = add_on_base_instance.activate
        shortcut = add_on_base_instance.activate_shortcut

        widget = GroupWidget(self, index, title, icon_path, hover_icon_path, shortcut, activate)
        self.widgets.append(widget)
        
        
    def toggle_windows(self) -> None:
        if self.isHidden():
            for window in self.active_windows:
                window.show()
        else:
            self.active_windows = [x for x in QApplication.allWindows() if x.isVisible()]
            for window in self.active_windows:
                window.hide()
        
        
    def paintEvent(self, a0: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(0, 0, 0, 178)))
        painter.drawRoundedRect(self.rect(), scaled(32), scaled(32))

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
            self.upper_position = self.pos()
            apply_setting("upper_position", [self.upper_position.x(), self.upper_position.y()])
        self._moved = False
        self._offset = None
        return super().mouseReleaseEvent(a0)
    
    def show(self) -> None:
        apply_setting("upper-hidden", False)
        return super().show()
    
    def hide(self) -> None:
        apply_setting("upper-hidden", True)
        return super().hide()
    
    def setHidden(self, hidden: bool) -> None:
        apply_setting("upper-hidden", hidden)
        return super().setHidden(hidden)



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