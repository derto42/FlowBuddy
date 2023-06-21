import os
import json

from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import (
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QMessageBox,
)
from PyQt5.QtGui import (
    QTextCursor,
    QKeySequence,
)

from addon import AddOnBase

from ui import ConfirmationDialog
from settings import UI_SCALE
from ui.utils import get_font
from ui.base_window import TabsWindow
from addons.notes.save_notes import exists




class NoteTab(QWidget):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.text_edit = QTextEdit()
        self.text_edit.setFont(get_font(size=16))
        self.text_edit.textChanged.connect(self.save_text_to_file)
        self.text_edit.setAcceptRichText(False)
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

    def load_text_from_file(self):
        if exists(self.file_path):
            with open(self.file_path, "r") as file:
                self.text_edit.setPlainText(file.read())
            self.text_edit.moveCursor(QTextCursor.End)

    def save_text_to_file(self):
        with open(self.file_path, "w") as file:
            file.write(self.text_edit.toPlainText())

    def create_new_file(self):
        with open(self.file_path, "w") as file:
            file.write("")




class JottingDownWindow(TabsWindow):
    window_toggle_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.window_toggle_signal.connect(self.toggle_window)

        self.notes_folder = "src/addons/notes/data"
        if not exists(self.notes_folder):
            os.makedirs(self.notes_folder)

        self.config_file = os.path.join(self.notes_folder, "config.json")



        self.load_tabs()
        self.old_pos = None
        self.red_button.clicked.connect(self.closeEvent)
        self.grn_button.clicked.connect(self.add_new_tab)
    

    def load_tabs(self):
        if exists(self.config_file):
            self.load_tabs_from_config()
        else:
            self.Load_tabs_from_text_files()

        if self.count() == 0:
            self.add_new_tab("notes")

    def Load_tabs_from_text_files(self):
        for tabno, file_name in enumerate(os.listdir(self.notes_folder)):
            if file_name.endswith(".txt"):
                file_path = os.path.join(self.notes_folder, file_name)
                note_tab = NoteTab(file_path)
                self.addTab(note_tab, file_name)


    def load_tabs_from_config(self):
        with open(self.config_file, "r") as file:
            config = json.load(file)

        for tabno, file_path in enumerate(config["files"]):
            if exists(file_path):
                file_name = os.path.basename(file_path)
                note_tab = NoteTab(file_name)
                self.addTab(note_tab, file_name)

        self.setCurrentIndex(config["last_active"])


    def save_tabs(self):
        config = {
            "files": [
                self.notes_folder + "/" + self.tabText(i)
                for i in range(self.count())
            ],
            "last_active": self.currentIndex(),
        }
        with open(self.config_file, "w") as file:
            json.dump(config, file)

    def delete_tab_text_file(self, file_name):
        file_path = os.path.join(self.notes_folder, file_name)
        if exists(file_path):
            os.remove(file_path)
        else:
            QMessageBox.warning(self, "File Exists", f"{file_path} does not exist.")

    def delete_tab(self, tab_text):
        tabid = self.get_tab_number_from_text(tab_text)
        file_name = self.tabText(tabid)
        dialog = ConfirmationDialog(f"Delete tab {file_name}?")
        res = dialog.exec()
        if not res:
            return
        self.removeTab(tabid)
        self.delete_tab_text_file(file_name)
        # self.movePlusButton()
        self.save_tabs()

    def get_tab_number_from_text(self, tab_text):
        for i in range(self.count()):
            if self.tabText(i) == tab_text:
                return i
        return -1

    def add_new_tab(self, file_name=""):
        if not file_name:
            file_name, ok = QInputDialog.getText(
                self, "New Note", "Enter the note name:"
            )
            if not ok or not file_name:
                return
        file_name = f"{file_name}.txt"

        file_path = os.path.join(self.notes_folder, file_name)
        if not exists(file_path):
            note_tab = NoteTab(file_path)  # create an instance of NoteTab
            note_tab.create_new_file()
            self.addTab(
                note_tab, file_name
            )  # add the NoteTab instance, not the QTextEdit
            self.save_tabs()
            self.setCurrentIndex(len(self) - 1)

        else:
            QMessageBox.warning(
                self, "File Exists", f"A file with the name {file_name} already exists."
            )

    def toggle_window(self) -> None:
        if self.isHidden():
            window.show()
            window.activateWindow()
            if current_widget := self.currentWidget():
                current_widget.setFocus()
        else:
            window.hide()

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
        self.hide()

window = JottingDownWindow()

AddOnBase().activate = window.window_toggle_signal.emit
AddOnBase().set_activate_shortcut(QKeySequence("Ctrl+`"))
