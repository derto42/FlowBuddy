from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import (
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QInputDialog,
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
from .notes_save import (
    get_file_data,
    save_file_data,
    write_config,
    get_config,
    delete_file_data,
)


class NoteTab(QWidget):
    def __init__(self, file_name):
        super().__init__()
        self.file_name = file_name
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
        file_data = get_file_data(self.file_name)
        self.text_edit.setPlainText(file_data)
        self.text_edit.moveCursor(QTextCursor.End)

    def save_text_to_file(self):
        save_file_data(self.file_name, self.text_edit.toPlainText())

    def create_new_file(self):
        with open(self.file_name, "w") as file:
            file.write("")


class JottingDownWindow(TabsWindow):
    window_toggle_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.window_toggle_signal.connect(self.toggle_window)

        self.load_tabs()
        self.old_pos = None
        self.red_button.clicked.connect(self.closeEvent)
        self.add_button.clicked.connect(self.add_new_tab)
        self.setFixedSize(840, 400)

    def load_tabs(self):
        for file_name in get_config()["files"]:
            note_tab = NoteTab(file_name)
            self.tab = self.addTab(note_tab, file_name)
            self.tab.red_button.clicked.connect(self.delete_tab)

        if self.count() == 0:
            self.add_new_tab("notes")

    def save_tabs(self):
        config = {
            "files": [self.tabText(i) for i in range(self.count())],
            "last_active": self.currentIndex(),
        }
        write_config(config)

    def delete_tab(self, tab_text):
        tabid = self.get_tab_number_from_text(tab_text)
        file_name = self.tabText(tabid)
        dialog = ConfirmationDialog(f"Delete tab {file_name}?")
        res = dialog.exec()
        if not res:
            return
        self.removeTab(tabid)
        delete_file_data(file_name)
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
        note_tab = NoteTab(file_name)
        note_tab.create_new_file()
        self.addTab(note_tab, file_name)
        save_file_data(file_name)
        self.save_tabs()
        self.setCurrentIndex(len(self) - 1)

    def toggle_window(self) -> None:
        if self.isHidden():
            window.show()
            window.activateWindow()
            if current_widget := self.currentWidget():
                current_widget.setFocus()
        else:
            window.hide()

    def closeEvent(self, event):
        self.save_tabs()
        self.hide()


window = JottingDownWindow()

AddOnBase().activate = window.window_toggle_signal.emit
AddOnBase().set_activate_shortcut(QKeySequence("Ctrl+`"))
