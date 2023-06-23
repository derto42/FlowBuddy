import test_components

import os
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QPainter, QColor, QPaintEvent, QMouseEvent, QTextCursor

from ui.base_window.title_bar_layer import TitleBarLayer
from ui import BaseWindow, TabsWindow
from ui.utils import get_font
from settings import UI_SCALE

class NoteTab(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

        # Create QTextEdit within the QWidget
        self.text_edit = QTextEdit()
        self.text_edit.setFont(get_font(size=16))
        self.text_edit.textChanged.connect(self.save_text_to_file)
        self.text_edit.setAcceptRichText(False)
        # This is for the tab itself
        # Add QTextEdit to layout with padding
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        #  Set the margins
        layout.setContentsMargins(
            int(24 * UI_SCALE),
            int(24 * UI_SCALE),
            int(22 * UI_SCALE),
            int(22 * UI_SCALE),
        )
        self.setLayout(layout)
        self.load_text_from_file()
        
        self.setStyleSheet("""QTextEdit{ 
                                background-color:lightgrey;
                                border-radius: 10;
                            } """)

    def load_text_from_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.text_edit.setPlainText(file.read())
            self.text_edit.moveCursor(QTextCursor.End)

    def save_text_to_file(self):
        with open(self.file_path, "w") as file:
            file.write(self.text_edit.toPlainText())

    def create_new_file(self):
        with open(self.file_path, "w") as file:
            file.write("")

app = QApplication([])

window = TabsWindow()
notes_1 = window.addTab(NoteTab("notes.txt"), "title1")
window.addTab(NoteTab("notes.txt"), "title2")
window.addTab(p := QPushButton("Button 1", window), "Button")
p.clicked.connect(lambda: window.removeTab(notes_1))
window.show()

window.setFixedSize(800, 400)

window.red_button.clicked.connect(lambda: print("Red button clicked"))
window.add_button.clicked.connect(lambda: print("Add button clicked"))

app.exec()