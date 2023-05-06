import os

import keyboard
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QFont, QFontDatabase, QTextCursor, QPainter, QPen, QColor

import FileSystem

def get_custom_font(size=16, font_name="Montserrat-Medium.ttf"):
    font_path = FileSystem.font(font_name)
    font_id = QFontDatabase.addApplicationFont(font_path)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    return QFont(font_family, size)


class JottingDownWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.notes_folder = "notes"
        # os used. so the notes folder and the notes.txt files will be
        # created in the working directory. not in the program directory.
        if not os.path.exists(self.notes_folder):
            os.makedirs(self.notes_folder)
        self.text_file_path = os.path.join(self.notes_folder, "notes.txt")

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(get_custom_font(size=16, font_name="Montserrat-Medium.ttf"))
        self.load_text_from_file()
        layout.addWidget(self.text_edit)

        self.text_edit.textChanged.connect(self.save_text_to_file)

        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #DADADA;
                border-radius: 12px;
            }
            QTextEdit {
                padding: 24px;
                border: none;
            }
        """)

        self.setFixedSize(500, 500)
        self.old_pos = None


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor("#DADADA"), 2))
        painter.setBrush(QColor("white"))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        
        
    def load_text_from_file(self):
        if os.path.exists(self.text_file_path):
            with open(self.text_file_path, "r") as file:
                self.text_edit.setPlainText(file.read())
            self.text_edit.moveCursor(QTextCursor.End)



    def save_text_to_file(self):
        with open(self.text_file_path, "w") as file:
            file.write(self.text_edit.toPlainText())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if not self.old_pos:
            return
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None

if __name__ == "__main__":
    app = QApplication([])
    window = JottingDownWindow()
    window.show()
    window.hide()
    toggle_window = lambda: window.show() if window.isHidden() else window.hide()
    keyboard.add_hotkey("ctrl+`", toggle_window)
    app.exec_()
