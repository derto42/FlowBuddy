import sys
import os
from typing import Optional

from pynput import mouse

from numpy import array

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QGridLayout, QFrame, QSizePolicy,
                             QSpacerItem, QPushButton)
from PyQt5.QtGui import QCursor, QPainter, QPixmap, QColor, QIcon, QPen, QPainterPath, QImage, QRadialGradient, QBrush
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt5.QtSvg import QSvgWidget
from PIL import ImageGrab, Image


sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

sys.path.append(os.path.abspath(__file__))

from settings import UI_SCALE  # pylint: disable=import-error, unused-import
from ui.utils import get_font  # pylint: disable=import-error, unused-import
from ui.utils import DEFAULT_BOLD, DEFAULT_REGULAR  # pylint: disable=import-error, unused-import
from ui.base_window import BaseWindow  # pylint: disable=import-error, unused-import
from ui.base_window import InnerPart  # pylint: disable=import-error, unused-import
from ui.custom_button import RedButton, TextButton  # pylint: disable=import-error, unused-import

if __name__ == "__main__":
    from vcolorpicker import ColorPicker
else:
    from .vcolorpicker import ColorPicker


def resize_image(image, target_width, target_height):
    qImg = QImage(image)
    qImg = qImg.scaled(target_width, target_height,
                       Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return qImg


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
        self.clipboard = QApplication.clipboard()
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
        self.copy_color_hex_btn.clicked.connect(
            lambda: self.clipboard.setText(self.color))

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
            lambda: self.clipboard.setText(str(QColor(self.color).getRgb()[0:3])))

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
        self.added_colors = []

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
        if color not in self.added_colors:
            self.added_colors.append(color)
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


class MagnifierWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__()
        self.parent = parent
        self.color = '#000000'
        self.track_color = False
        self.listener = None
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.resize(340, 340)

        self.layout.addWidget(self.label)

        screen_geometry = QApplication.desktop().screenGeometry()
        window_width = self.width()
        x_pos = screen_geometry.width() - window_width - -200
        y_pos = 50

        self.move(x_pos, y_pos)

        self.timer = QTimer()
        self.timer.timeout.connect(self.capture)
        self.timer.start(60)

    def paintEvent(self, event):
        # Override QWidget's paint event to draw a circular mask with smooth edges
        path = QPainterPath()
        # Adjust the rectangle dimensions
        path.addEllipse(QRectF(self.rect()).adjusted(7, 7, -7, -7))
        mask = QPainter(self)
        mask.setRenderHint(QPainter.Antialiasing)  # Enable anti-aliasing
        mask.setClipPath(path)
        mask.fillRect(self.rect(), Qt.black)

    def generatePixmapMask(self, diameter):
        # Create QPixmap with transparency
        mask = QPixmap(diameter, diameter)
        mask.fill(Qt.transparent)

        # Create QPainter to draw on the QPixmap
        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)

        # Create radial gradient
        gradient = QRadialGradient(
            diameter / 2, diameter / 2, diameter / 2, diameter / 2, diameter / 2)
        gradient.setColorAt(0, QColor(0, 0, 0, 255))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))

        # Set gradient as brush
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)

        # Draw ellipse
        painter.drawEllipse(0, 0, diameter, diameter)
        painter.end()

        return mask

    def start_color_picker(self):
        self.listener = mouse.Listener(
            on_click=lambda x, y, button, pressed: self.mousePressEvent(pressed))
        self.listener.start()
        self.track_color = True
        self.move(50, 50)
        self.set_track_color(True)
        # self.title_layout.setContentsMargins(20, 10, 0, 10)

    def capture(self):
        if self.track_color:
            cursor = QCursor.pos()
            self.color = get_pixel_from_position(cursor)
            x, y = cursor.x() - 8, cursor.y() - 8
            x, y = int(x), int(y)

            screen = ImageGrab.grab(bbox=(x, y, x + 17, y + 17))
            screen_resized = screen.resize((340, 340), resample=Image.NEAREST)

            screen_np = array(screen_resized)

            height, width, channel = screen_np.shape
            bytesPerLine = 3 * width
            qImg = QImage(screen_np.data, width, height,
                          bytesPerLine, QImage.Format_RGB888)

            pixmap = QPixmap.fromImage(qImg)

            painter = QPainter(pixmap)
            pen = QPen(QColor('gray'), 1, Qt.SolidLine)
            painter.setPen(pen)

            pixel_size = 340 // 17

            center = 340 // 2

            for i in range(center % pixel_size, 340, pixel_size):
                painter.drawLine(i - pixel_size // 2, 0,
                                 i - pixel_size // 2, 340)
                painter.drawLine(0, i - pixel_size // 2,
                                 340, i - pixel_size // 2)

            pen = QPen(QColor('white'), 1, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(center - pixel_size // 2 - 2, center -
                             pixel_size // 2 - 2, pixel_size + 3, pixel_size + 3)

            pen = QPen(QColor('black'), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(center - pixel_size // 2, center -
                             pixel_size // 2, pixel_size, pixel_size)

            painter.end()

            self.label.setPixmap(pixmap)

            # Apply mask to pixmap
            mask = self.generatePixmapMask(pixmap.width())
            pixmap.setMask(mask.mask())

            # Create QPainterPath
            path = QPainterPath()
            path.addEllipse(QRectF(0, 0, 0, 0))

            # Create mask QPainter
            mask_painter = QPainter(pixmap)
            mask_painter.setRenderHint(QPainter.Antialiasing)
            mask_painter.setClipPath(path)

            # Draw pixmap onto itself using the mask painter
            mask_painter.drawPixmap(0, 0, pixmap)
            mask_painter.end()

            self.label.setPixmap(pixmap)

    def mousePressEvent(self, event):
        self.set_track_color(False)
        self.listener.stop()
        self.hide()
        buddy_color_picker.add_selected_color_signal.emit(self.color)
        buddy_color_picker.show()

    def set_track_color(self, track_color: bool) -> None:
        self.track_color = track_color


if __name__ == '__main__':
    app = QApplication(sys.argv)
    buddy_color_picker = BuddyColorPicker()
    buddy_color_picker.show()

    desktop_color_picker = MagnifierWidget()
    desktop_color_picker.hide()

    color_picker = ColorPickerWidget()
    color_picker.hide()

    sys.exit(app.exec_())
