import sys
import os
from typing import Optional

from clipboard import copy

from pynput import mouse

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QFrame, QSizePolicy,
                             QSpacerItem, QPushButton)
from PyQt5.QtGui import QCursor, QPainter, QPixmap, QColor, QIcon
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtSvg import QSvgWidget
from PIL import ImageGrab


sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

sys.path.append(os.path.abspath(__file__))

from ui.custom_button import RedButton, GrnButton, YelButton, TextButton  # pylint: disable=import-error, unused-import
from ui.dialog import ConfirmationDialog, BaseDialog  # pylint: disable=import-error, unused-import
from ui.base_window import MainLayer  # pylint: disable=import-error, unused-import
from ui.base_window import InnerPart  # pylint: disable=import-error, unused-import
from ui.base_window import BaseWindow  # pylint: disable=import-error, unused-import
from ui.entry_box import Entry  # pylint: disable=import-error, unused-import
from ui.utils import DEFAULT_BOLD, DEFAULT_REGULAR  # pylint: disable=import-error, unused-import
from ui.utils import get_font  # pylint: disable=import-error, unused-import
from settings import UI_SCALE  # pylint: disable=import-error, unused-import

from vcolorpicker import ColorPicker


def get_pixel_from_position(position) -> str:
    """Get pixel color from mouse position

    Returns:
        str: Pixel color in hex format
    """
    pixel = ImageGrab.grab().load()[position.x(), position.y()]

    # convert pixel color to hex
    pixel = f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"

    return pixel


class SelectedColorWidget(QWidget):
    def __init__(self, color: str = '#000000'):
        super().__init__()
        self.color = color
        self.layout = QGridLayout()

        self.copy_svg_icon = QSvgWidget(os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "icons", "copy-icon.svg"))
        self.copy_svg_icon = self.copy_svg_icon.grab()

        self.setLayout(self.layout)

        self.delete_widget_btn = RedButton()
        self.delete_widget_btn.setToolTip("Remove selected color")

        # scale button size to 50% of default
        self.delete_widget_btn.setIconSize(
            self.delete_widget_btn.iconSize() * 0.5)

        self.delete_widget_btn.clicked.connect(self.delete_widget)

        self.color_label_hex = QLabel("Hex Color:")
        self.color_label_hex.setFont(get_font(DEFAULT_BOLD, 12))
        self.color_label_hex.setStyleSheet("color: #000000;")
        self.color_label_hex.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.color_value_hex = QLabel(self.color)
        self.color_value_hex.setFont(get_font(DEFAULT_REGULAR, 10))
        self.color_value_hex.setStyleSheet("color: #000000;")
        self.color_value_hex.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.copy_color_hex_btn = QPushButton()
        self.copy_color_hex_btn.setFixedWidth(25)
        self.copy_color_hex_btn.setIcon(QIcon(self.copy_svg_icon))
        self.copy_color_hex_btn.setStyleSheet('background: white;')
        self.copy_color_hex_btn.setStyleSheet(
            "QPushButton:hover { " + f"background-color: {self.color}; " + "}")
        self.copy_color_hex_btn.clicked.connect(lambda: copy(self.color))

        self.layout.addWidget(self.color_label_hex, 0, 0, 1, 3)
        self.layout.addWidget(self.color_value_hex, 0, 3, 1, 5)
        self.layout.addWidget(self.copy_color_hex_btn, 0, 8, 1, 1)
        self.layout.addWidget(self.delete_widget_btn, 0, 9, 1, 1)

        self.color_label_rgb = QLabel("RGB Color:")
        self.color_label_rgb.setFont(get_font(DEFAULT_BOLD, 12))
        self.color_label_rgb.setStyleSheet("color: #000000;")
        self.color_label_rgb.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.color_value_rgb = QLabel(str(QColor(self.color).getRgb()[0:3]))
        self.color_value_rgb.setFont(get_font(DEFAULT_REGULAR, 10))
        self.color_value_rgb.setStyleSheet("color: #000000;")
        self.color_value_rgb.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.copy_color_rgb_btn = QPushButton()
        self.copy_color_rgb_btn.setFixedWidth(25)
        self.copy_color_rgb_btn.setIcon(QIcon(self.copy_svg_icon))
        self.copy_color_rgb_btn.setStyleSheet('background: white;')

        # set color on hover to match color of selected color
        self.copy_color_rgb_btn.setStyleSheet(
            "QPushButton:hover { " + f"background-color: {self.color}; " + "}")
        self.copy_color_rgb_btn.clicked.connect(
            lambda: copy(str(QColor(self.color).getRgb()[0:3])))

        self.layout.addWidget(self.color_label_rgb, 1, 0, 1, 3)
        self.layout.addWidget(self.color_value_rgb, 1, 3, 1, 5)
        self.layout.addWidget(self.copy_color_rgb_btn, 1, 8, 1, 1)

        self.color_display_box = QFrame()
        self.color_display_box.setStyleSheet(
            f"background-color: {self.color};")
        self.color_display_box.setMaximumSize(280, 280)
        self.color_display_box.setMinimumSize(280, 25)
        self.color_display_box.setFrameShape(QFrame.Box)
        self.color_display_box.setFrameShape(QFrame.StyledPanel)

        self.color_display_box.setFrameShadow(QFrame.Raised)
        self.color_display_box.setLineWidth(2)

        self.layout.addWidget(self.color_display_box, 2, 0, 1, 10)

        # add a spacer to push the color display box to the top
        self.layout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding), 3, 0, 1, 10)

    def delete_widget(self):
        self.deleteLater()
        buddy_color_picker.resize_signal.emit()


class ColorPickerWidget(ColorPicker):
    def __init__(self) -> None:
        super().__init__(True)

    def exit_btn_clicked(self):
        self.hide()
        buddy_color_picker.add_selected_color_signal.emit(
            f"#{self.ui.hex.text()}")
        buddy_color_picker.show()


class BuddyColorPicker(BaseWindow):
    add_selected_color_signal = pyqtSignal(str)
    resize_signal = pyqtSignal()

    def __init__(self):
        super().__init__(True)
        self.layout = QVBoxLayout()
        self.selected_color_widget = None
        self.selected_color_widgets = 0
        self.setLayout(self.layout)
        self.setMaximumHeight(800)

        self.add_selected_color_signal.connect(self.add_selected_color)
        self.resize_signal.connect(self.resize_self)

        self.findChildren(InnerPart)[0].edit_button.hide()

        self.desktop_color_picker = TextButton(text=" Desktop Color Picker ")
        self.color_picker = TextButton(text=" Custom Color Picker ")

        self.desktop_color_picker.clicked.connect(
            self.start_desktop_color_picker)
        self.color_picker.clicked.connect(self.start_color_picker)

        self.layout.addWidget(self.desktop_color_picker)
        self.layout.addWidget(self.color_picker)

        self.vertical_spacer = QSpacerItem(
            0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addItem(self.vertical_spacer)

        self.animate = True
        self.adjustSize()

    def start_desktop_color_picker(self):
        self.hide()
        desktop_color_picker.show()
        desktop_color_picker.start_color_picker()

    def start_color_picker(self):
        self.hide()
        color_picker.show()

    def on_close_button_clicked(self):
        self.close()
        desktop_color_picker.close()
        color_picker.close()

    def add_selected_color(self, color: str):
        self.selected_color_widget = SelectedColorWidget(color=color)
        self.layout.insertWidget(
            self.layout.count() - 1, self.selected_color_widget)

        self.selected_color_widgets = len(
            self.findChildren(SelectedColorWidget))
        self.setMinimumHeight(300 + 100 * self.selected_color_widgets)
        if self.selected_color_widgets > 5:
            for ind, selected_color_widget in enumerate(self.findChildren(SelectedColorWidget)):
                if ind < self.selected_color_widgets - 5:
                    selected_color_widget.hide()

    def resize_self(self):
        self.setMinimumHeight(100 + 100 * self.selected_color_widgets)
        self.setMaximumHeight(200 + 100 * self.selected_color_widgets)
        self.adjustSize()


class DesktopColorPicker(BaseWindow):
    def __init__(self) -> None:
        super().__init__(True)
        self._edit_mode = False
        self.side = 'left'
        self.color = '#000000'
        self.track_color = False
        self.listener = None

        self.findChildren(InnerPart)[0].edit_button.hide()
        self.findChildren(InnerPart)[0].close_button.hide()

        self.move(50, 50)

        self.inner_part = self.findChild(InnerPart)
        self.title_layout = self.inner_part.findChild(QHBoxLayout)

        self.color_label = QLabel("")

        # insert the color label to the title layout at first position
        self.title_layout.insertWidget(0, self.color_label)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignTop)

        for main_layer in self.findChildren(MainLayer):
            main_layer.setContentsMargins(0, 0, 0, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1)  # Adjust the update interval as needed

        self.magnifier = MagnifierWidget(parent=self)
        self.layout.addWidget(self.magnifier)

    def update_position(self):
        if self.track_color:
            cursor_pos = QCursor.pos()
            color = get_pixel_from_position(cursor_pos)
            self.update_color(color)
            screen_width = QApplication.desktop().screenGeometry().width()
            if cursor_pos.x() < 550 and cursor_pos.y() < 600 and self.side == 'left':
                self.move(screen_width - 550, 50)
                self.side = 'right'
            elif cursor_pos.x() > screen_width - 550 and cursor_pos.y() < 600 and self.side == 'right':
                self.move(50, 50)
                self.side = 'left'

    def start_color_picker(self):
        self.listener = mouse.Listener(
            on_click=lambda x, y, button, pressed: self.mousePressEvent(pressed))
        self.listener.start()
        self.track_color = True
        self.move(50, 50)
        self.magnifier.set_track_color(True)
        self.title_layout.setContentsMargins(20, 10, 0, 10)

    def update_color(self, color: str) -> None:
        self.color = color
        self.color_label.setText(
            f"HEX: {color} RGB: {QColor(color).getRgb()[0:3]}")
        self.color_label.setStyleSheet(
            f"color: {color}; font-size: 15px; font-weight: bold;")

    def mousePressEvent(self, event):
        if event is True:
            self.magnifier.set_track_color(False)
            self.track_color = False
            self.listener.stop()
            copy(self.color)
            self.color_label.setText("")
            self.layout.removeWidget(self.color_label)
            self.title_layout.setContentsMargins(5, 5, 0, 5)
            self.setFixedSize(int(UI_SCALE * 230), int(UI_SCALE * 200))
            self.setFixedWidth(0)
            self.setFixedHeight(0)
            self.adjustSize()
            self.hide()
            buddy_color_picker.add_selected_color_signal.emit(self.color)
            buddy_color_picker.show()


class MagnifierWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__()
        self.parent = parent
        self.track_color = False
        self.set_track_color(False)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        # Adjust the size of the magnifier image as needed
        self.magnifier_pixmap = QPixmap(350, 350)
        self.update_magnifier()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1)  # Adjust the update interval as needed

    def update_magnifier(self):
        if self.track_color:
            self.magnifier_pixmap.fill(Qt.transparent)
            painter = QPainter(self.magnifier_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            magnifier_radius = self.magnifier_pixmap.width() // 2
            painter.setPen(Qt.black)
            painter.drawEllipse(self.magnifier_pixmap.rect(
            ).center(), magnifier_radius, magnifier_radius)
            cursor_pos = QCursor.pos()

            magnification = 16
            magnified_region = QApplication.primaryScreen().grabWindow(
                QApplication.desktop().winId(),
                cursor_pos.x() - magnifier_radius // magnification,
                cursor_pos.y() - magnifier_radius // magnification,
                self.magnifier_pixmap.width(),
                self.magnifier_pixmap.height()
            )
            painter.drawPixmap(0, 0, magnified_region.scaled(
                self.magnifier_pixmap.size() * magnification,
                Qt.KeepAspectRatioByExpanding))

            # Draw cursor position point
            crosshair_size = 10
            magnifier_center = self.rect().center()

            # if get_pixel_from_cposition() is red or a shade of red
            if not get_pixel_from_position(cursor_pos).startswith('#ff'):
                painter.setPen(Qt.red)
            else:
                painter.setPen(Qt.green)
            painter.drawLine(
                magnifier_center.x() - crosshair_size, magnifier_center.y(),
                magnifier_center.x() + crosshair_size, magnifier_center.y())
            painter.drawLine(
                magnifier_center.x(), magnifier_center.y() - crosshair_size,
                magnifier_center.x(), magnifier_center.y() + crosshair_size)

            painter.end()

            self.update()  # Update the widget to reflect the changes

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.magnifier_pixmap)
        painter.end()

    def update_position(self):
        self.update_magnifier()

    def mousePressEvent(self, event):
        self.close()

    def set_track_color(self, track_color: bool) -> None:
        self.track_color = track_color
        if track_color:
            self.setFixedSize(350, 350)
            self.parent.setFixedSize(450, 450)
        else:
            self.setFixedSize(0, 40)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    buddy_color_picker = BuddyColorPicker()
    buddy_color_picker.show()

    desktop_color_picker = DesktopColorPicker()
    desktop_color_picker.hide()

    color_picker = ColorPickerWidget()
    color_picker.hide()

    sys.exit(app.exec_())
