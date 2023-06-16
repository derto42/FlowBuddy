import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
)

from tutorial import Color
from PyQt5.QtWidgets import QGridLayout


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        # self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.setMovable(True)
        layout = QGridLayout()
        self.setLayout(layout)
        layout.addWidget(tabs)

        for n, color in enumerate(["red", "green", "blue", "yellow"]):
            tabs.addTab(Color(color), color)

        


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
