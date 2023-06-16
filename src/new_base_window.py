from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QTextEdit, QVBoxLayout, QTabWidget
import sys
from pathlib import Path
from PyQt5.QtWidgets import QPushButton

from ui.custom_button import RedButton
from ui.base_window import BaseWindow


UI_SCALE = 1


class Window(BaseWindow):
    def __init__(self):
        super().__init__(add_tab=True)
        layout = QVBoxLayout()
        self.setLayout(layout)
        # label1 = QTextEdit("Widget in Tab 1.")
        # label2 = QTextEdit("Widget in Tab 2.")
        # button1 = RedButton()
        # button2 = RedButton()
        tabwidget = QTabWidget()
        # tabwidget.addTab(label1, "Tab 1")
        # self.right = tabwidget.tabBar().RightSide
        # tabwidget.tabBar().setTabButton(0, self.right, button1)
        # tabwidget.addTab(label2, "Tab 2")
        # tabwidget.tabBar().setTabButton(1, self.right, button2)
        layout.addWidget(tabwidget)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(int(650 * UI_SCALE), int(450 * UI_SCALE))
        # tabwidget.hide()


app = QApplication(sys.argv)
app.setStyleSheet(Path("src/addons/notes/notes.qss").read_text())
screen = Window()
screen.show()
sys.exit(app.exec_())
