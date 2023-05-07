import os
import json

import keyboard
from PyQt5.QtWidgets import QApplication, QTextEdit, QVBoxLayout, QWidget, QShortcut, QTabWidget, QSizePolicy, QInputDialog, QToolButton, QTabBar, QMessageBox
from PyQt5.QtCore import Qt, QPoint, QEvent, pyqtSignal
from PyQt5.QtGui import QFont, QFontDatabase, QTextCursor, QPainter, QPen, QColor, QKeySequence

import FileSystem

def get_custom_font(size=16, font_name="Montserrat-Medium.ttf"):
    font_path = FileSystem.font(font_name)
    font_id = QFontDatabase.addApplicationFont(font_path)
    font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
    return QFont(font_family, size)

class NoteTab(QTextEdit):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.load_text_from_file()
        self.setFont(get_custom_font(size=16, font_name="Montserrat-Medium.ttf"))
        self.textChanged.connect(self.save_text_to_file)
        self.setStyleSheet("""
            QTextEdit {
                padding: 24px;
                border: none;
            }
        """)

    def load_text_from_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.setPlainText(file.read())
            self.moveCursor(QTextCursor.End)

    def save_text_to_file(self):
        with open(self.file_path, "w") as file:
            file.write(self.toPlainText())

class CustomTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.addTabButton = QToolButton(self)
        self.addTabButton.setText('+')
        self.addTabButton.clicked.connect(parent.add_new_tab)
        self.setCornerWidget(self.addTabButton, Qt.TopRightCorner)

class JottingDownWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.notes_folder = "notes"
        if not os.path.exists(self.notes_folder):
            os.makedirs(self.notes_folder)

        self.config_file = os.path.join(self.notes_folder, "config.json")
        self.tab_widget = CustomTabWidget(self)
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        layout.addWidget(self.tab_widget)

        self.load_tabs()

        new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        new_tab_shortcut.activated.connect(self.add_new_tab)

        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #DADADA;
                border-radius: 12px;
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

    def load_tabs(self):
        # Load existing .txt files in the notes folder as tabs
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as file:
                config = json.load(file)

            # Load tabs based on the order in config["files"]
            for file_path in config["files"]:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    self.tab_widget.addTab(NoteTab(file_path), file_name)

            self.tab_widget.setCurrentIndex(config["last_active"])
        else:
            # If config file doesn't exist, load tabs by iterating over files in the notes folder
            for file_name in os.listdir(self.notes_folder):
                if file_name.endswith('.txt'):
                    file_path = os.path.join(self.notes_folder, file_name)
                    self.tab_widget.addTab(NoteTab(file_path), file_name)

            # If no tabs are found after loading existing .txt files, add the default "notes" file
            if self.tab_widget.count() == 0:
                self.add_new_tab("notes")



    def save_tabs(self):
        config = {
            "files": [self.notes_folder + "/" + self.tab_widget.tabText(i) for i in range(self.tab_widget.count())],
            "last_active": self.tab_widget.currentIndex()
        }
        with open(self.config_file, "w") as file:
            json.dump(config, file)

    def add_new_tab(self, file_name=''):
        if not file_name:
            file_name, ok = QInputDialog.getText(self, "New Note", "Enter the note name:")
            if not ok or not file_name:
                return
        file_name = f"{file_name}.txt"

        file_path = os.path.join(self.notes_folder, file_name)
        if not os.path.exists(file_path):
            self.tab_widget.addTab(NoteTab(file_path), file_name)
        else:
            QMessageBox.warning(self, "File Exists", f"A file with the name {file_name} already exists.")


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

    def closeEvent(self, event):
        self.save_tabs()

if __name__ == "__main__":
    app = QApplication([])
    window = JottingDownWindow()
    window.show()
    window.hide()

    def toggle_window():
        if window.isHidden():
            window.show()
            window.activateWindow()  # Add this line to activate the window
            current_widget = window.tab_widget.currentWidget()
            if current_widget:
                current_widget.setFocus()  # Set focus on the text box
        else:
            window.hide()

    keyboard.add_hotkey("ctrl+`", toggle_window)
    app.exec_()
