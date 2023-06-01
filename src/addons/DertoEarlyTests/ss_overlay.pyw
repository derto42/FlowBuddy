import sys
import cv2
import numpy as np
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui

class Overlay(QtWidgets.QLabel):

    def __init__(self, parent=None):
        super(Overlay, self).__init__(parent)
        print("Overlay initialized")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.close_button = QtWidgets.QPushButton(self)
        self.close_button.setText("X")
        self.close_button.setStyleSheet("background-color: red")
        self.close_button.clicked.connect(self.close)
        self.close_button.hide()

        self.remove_bg_button = QtWidgets.QPushButton(self)
        self.remove_bg_button.setText("Remove BG")
        self.remove_bg_button.setStyleSheet("background-color: blue")
        self.remove_bg_button.clicked.connect(self.open_color_picker)
        self.remove_bg_button.hide()

        self.m_drag = False
        self.m_DragPosition = QtCore.QPoint()
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.hide_buttons)
        self.timer.setSingleShot(True)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = QMouseEvent.globalPos() - self.pos()
            QMouseEvent.accept()

    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.buttons() == QtCore.Qt.LeftButton:
            self.move(QMouseEvent.globalPos() - self.m_DragPosition)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_drag = False

    def close(self):
        super(Overlay, self).close()

    def show_close_button(self):
        self.close_button.move(self.width()-25, 5)
        self.close_button.show()
        print("Close button is visible: ", self.close_button.isVisible())

    def hide_close_button(self):
        self.close_button.hide()

    def show_remove_bg_button(self):
        self.remove_bg_button.move(self.width()-25, 50)
        self.remove_bg_button.show()

    def hide_remove_bg_button(self):
        self.remove_bg_button.hide()

    def enterEvent(self, event):
        self.show_close_button()
        self.show_remove_bg_button()
        self.timer.stop()

    def leaveEvent(self, event):
        self.timer.start(550)  # Start the timer for 1.5 seconds

    def hide_buttons(self):
        self.hide_close_button()
        self.hide_remove_bg_button()


    def open_color_picker(self):
        color = QtWidgets.QColorDialog.getColor()

        if color.isValid():
            # Convert QColor to RGB values
            color_rgb = color.getRgb()[:3]
            self.remove_background(color_rgb)

    def remove_background(self, color_rgb):
        screenshot = self.pixmap().toImage()
        width = screenshot.width()
        height = screenshot.height()
        ptr = screenshot.bits()
        ptr.setsize(height * width * 4)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))

        # Convert np array to PIL Image
        img = Image.fromarray(arr)

        # Use Pillow's convert function to set transparency
        img = img.convert("RGBA")

        datas = img.getdata()

        newData = []
        for item in datas:
            # change all (also shades of the color) white (also shades of grey) pixels to transparent
            if item[0] in list(range(color_rgb[0]-15, color_rgb[0]+15)):
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)

        img.putdata(newData)
        
        # Convert PIL Image back to np array
        arr = np.array(img)
        
        qimage = QtGui.QImage(arr.data, width, height, QtGui.QImage.Format_ARGB32)
        pixmap = QtGui.QPixmap.fromImage(qimage)

        self.setPixmap(pixmap)




class ScreenShotOverlay(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ScreenShotOverlay, self).__init__(parent)
        print("ScreenShotOverlay initialized")
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.screenshot_overlay = None


    def start(self):
        print("Starting ScreenShotOverlay")
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.FramelessWindowHint)
        self.setGeometry(QtWidgets.QApplication.desktop().availableGeometry())
        self.showFullScreen()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
        qp.setBrush(QtGui.QColor(128, 128, 255, 128))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        print("Mouse button pressed")
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        print("Mouse moved")
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        print("Mouse button released")
        QtWidgets.QApplication.restoreOverrideCursor()
        self.hide()

        QtCore.QTimer.singleShot(200, self.take_screenshot)

    def take_screenshot(self):
        screenshot = QtWidgets.QApplication.primaryScreen().grabWindow(
            QtWidgets.QApplication.desktop().winId(),
            min(self.begin.x(), self.end.x()),
            min(self.begin.y(), self.end.y()),
            abs(self.begin.x() - self.end.x()),
            abs(self.begin.y() - self.end.y())
        )
        print("Screenshot taken")

        self.screenshot_overlay = Overlay()
        self.screenshot_overlay.setPixmap(screenshot)
        self.screenshot_overlay.show()
        self.screenshot_overlay.show_close_button()

        print("Overlay is visible: ", self.screenshot_overlay.isVisible())

        self.close()


if __name__ == '__main__':
    print("Program started")
    app = QtWidgets.QApplication(sys.argv)
    overlay = ScreenShotOverlay()
    overlay.start()
    sys.exit(app.exec_())
