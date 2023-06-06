
from typing import Any, Tuple, Optional

from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFileDialog,
)

from ui import BaseDialog, ACCEPTED, REJECTED, TextButton, Entry

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
        
        
    def result(self) -> str | BaseDialog.DialogCode:
        return self._name_entry.text() if super().result() == ACCEPTED else super().result()

    def exec(self) -> Any:
        self.adjustSize()
        cursor_pos = QCursor.pos()
        geo = self.geometry()
        self.setGeometry(geo.adjusted(cursor_pos.x() - geo.width()//2, cursor_pos.y() - geo.height()//2, 0, 0))

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
        self.adjustSize()
        cursor_pos = QCursor.pos()
        geo = self.geometry()
        self.setGeometry(geo.adjusted(cursor_pos.x() - geo.width()//2, cursor_pos.y() - geo.height()//2, 0, 0))
        
        super().exec()
        return self.result()
    
    def exec_(self) -> int:
        return self.exec()
