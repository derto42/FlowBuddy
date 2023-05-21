from typing import Optional, Tuple, Any
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox
)
from PyQt5.QtGui import QKeyEvent, QShowEvent


from .settings import CORNER_RADIUS, UI_SCALE
from .custom_button import TextButton, RedButton, GrnButton
from .utils import get_font
from .base_window import BaseWindow
from .entry_box import Entry


ACCEPTED = QDialog.Accepted
REJECTED = QDialog.Rejected


class BaseDialog(QDialog, BaseWindow):
    def __init__(self, title: str = "Title",
                 parent: QWidget | None = None,) -> None:
        super().__init__(add_tab = False, parent = parent)
        
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._title = QLabel(title, self)
        self._layout.addWidget(self._title)
        self._title.setFont(get_font(size=int(24 * UI_SCALE), weight="semibold"))
        self._title.setAlignment(Qt.AlignCenter)
        
        self._main_layout = QWidget(self)
        self._layout.addWidget(self._main_layout)
        
        self._layout.insertLayout
        self._layout.addLayout(button_layout:=QHBoxLayout())
        
        button_layout.addStretch()
        button_layout.addWidget(reject_button:=RedButton(self, "long"))
        button_layout.addSpacing(int(7 * UI_SCALE))
        button_layout.addWidget(accept_button:=GrnButton(self, "long"))
        button_layout.addStretch()
        accept_button.clicked.connect(lambda : self.accept())
        reject_button.clicked.connect(lambda : self.reject())
        accept_button.setToolTip("Ok")
        reject_button.setToolTip("Cancel")
        accept_button.setDefault(True)
        
        self.setLayout = self._main_layout.setLayout
        self.layout = self._main_layout.layout
        
        self.setModal(True)
        
        # self.setFixedSize(100, 100)
        
        
    def setTitle(self, title: str) -> None:
        self._title.setText(title)
        
    
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
            self.accept()
        elif a0.key() is Qt.Key.Key_Escape:
            self.reject()
        return super().keyPressEvent(a0)
    
    def showEvent(self, a0: QShowEvent) -> None:
        self.adjustSize()
        return super().showEvent(a0)


class GroupDialog(BaseDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("New Group", parent)

        self.setLayout(layout:=QVBoxLayout())
        
        self._name_entry = Entry(self, "Group Name")
        layout.addWidget(self._name_entry)
        self._name_entry.setFocus()
        
    def for_edit(self, name: str):
        self.setTitle("Edit Group")
        self._name_entry.setText(name)
        self._name_entry.setToolTip("Group Name")
        
        
    def result(self) -> str | QDialog.DialogCode:
        return self._name_entry.text() if super().result() == ACCEPTED else super().result()

    def exec(self) -> Any:
        super().exec()
        return self.result()
    
    def exec_(self) -> int:
        return self.exec()


class TaskDialog(BaseDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("New Task", parent)
        
        self._file_path = None
        
        self.setLayout(layout:=QVBoxLayout())

        self._name_entry = Entry(self, "Task Name")
        self._button_entry = Entry(self, "Button Text")
        self._url_entry = Entry(self, "URL")
        file_choose_button = TextButton(self, "Choose File")
        file_choose_button.clicked.connect(self._choose_file)

        self._name_entry.setToolTip("Task Name")
        self._button_entry.setToolTip("Button Text")
        self._url_entry.setToolTip("URL")
        file_choose_button.setToolTip("Choose File")

        layout.addWidget(self._name_entry)
        layout.addWidget(self._button_entry)
        layout.addWidget(self._url_entry)
        layout.addWidget(file_choose_button)

        self._name_entry.setFocus()

    def _choose_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        self._file_path, _ = QFileDialog.getOpenFileName(self, "Choose File", "",
                                                         "All Files (*)", options=options)

    def for_edit(self, name: str, button_text: str, url: str, file_path: str) -> None:
        self.setTitle("Edit Task")
        self._name_entry.setText(name)
        self._button_entry.setText(button_text if button_text is not None else "")
        self._url_entry.setText(', '.join(url) if url is not None else "")
        self._file_path = file_path if file_path is not None else ""

    def result(self) -> Tuple[Optional[str]]:
        if (ret:=super().result()) != ACCEPTED:
            return ret
        namet, buttont = self._name_entry.text(), self._button_entry.text()
        urlt, filet = self._url_entry.text(), self._file_path
        name = namet
        button_text = buttont if buttont else None
        url = urlt if urlt else None
        file_path = filet if filet else None
        return name, button_text, url, file_path

    def exec(self) -> Any:
        super().exec()
        return self.result()
    
    def exec_(self) -> int:
        return self.exec()


class ConfirmationDialog(BaseDialog):
    def __init__(self, title: str = "Title", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        
        self._title.setFont(get_font(size=int(16 * UI_SCALE)))


