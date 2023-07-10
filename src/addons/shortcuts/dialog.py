
from typing import Any, Tuple, Optional, Literal
from PyQt5.QtCore import QEvent, QVariantAnimation,QPropertyAnimation, QEasingCurve, QRect

from PyQt5.QtGui import QCursor, QResizeEvent
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFileDialog,
    QGraphicsOpacityEffect,
)
from .shortcuts_save import TaskClass

from ui import BaseDialog, ACCEPTED, REJECTED, TextButton, Entry


class FileChooseButton(TextButton):
    
    class InnerButton(TextButton):
        def __init__(self, parent: QWidget, text: str = "Text Button", side: str = Literal["left", "right"]):
            super().__init__(parent, text)
            
            self.side = side
            self._parent = parent
            
            self.exposed_geometry = None
            self.hidden_geometry = None
            
            self.opacity = QGraphicsOpacityEffect()
            self.opacity.setOpacity(0.0)
            self.opacity_anim = QPropertyAnimation(self.opacity, b"opacity")
            self.opacity_anim.setDuration(500)
            self.opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            self.setGraphicsEffect(self.opacity)
            
            self.animation = QVariantAnimation()
            self.animation.setDuration(500)
            self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.animation.valueChanged.connect(self.setGeometry)


        def spawn(self):
            self.animation.stop()
            self.opacity_anim.stop()
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.exposed_geometry)
            self.opacity_anim.setStartValue(self.opacity.opacity())
            self.opacity_anim.setEndValue(0.99)
            self.animation.start()
            self.opacity_anim.start()

        def kill(self):
            self.animation.stop()
            self.opacity_anim.stop()
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(self.hidden_geometry)
            self.opacity_anim.setStartValue(self.opacity.opacity())
            self.opacity_anim.setEndValue(0.0)
            self.animation.start()
            self.opacity_anim.start()
            
        def define_geometries(self):
            geo = self._parent.geometry()
            width = geo.width() // 2
            height = geo.height()
            self.exposed_geometry = QRect(width if self.side == "right" else 0, 0,
                                                 width, height)
            self.hidden_geometry = QRect(width // 2, 0, width, height)
            
            self.setGeometry(self.hidden_geometry)
            
        def resizeEvent(self, a0: QResizeEvent) -> None:
            if self.exposed_geometry is None:
                self.define_geometries()
            return super().resizeEvent(a0)

    
    def __init__(self, parent: QWidget | None = None, text: str = "Text Button"):
        super().__init__(parent, text)
        
        self.adjustSize()

        self.file_button = self.InnerButton(self, "File", "left")
        self.folder_button = self.InnerButton(self, "Folder", "right")
        
    def enterEvent(self, a0: QEvent) -> None:
        self.file_button.spawn()
        self.folder_button.spawn()
        return super().enterEvent(a0)
    
    def leaveEvent(self, a0: QEvent) -> None:
        self.file_button.kill()
        self.folder_button.kill()
        return super().leaveEvent(a0)


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
        file_choose_button = FileChooseButton(self, "Choose File")
        file_choose_button.file_button.clicked.connect(lambda: self._choose_file("file"))
        file_choose_button.folder_button.clicked.connect(lambda: self._choose_file("folder"))

        self._name_entry.setToolTip("Task Name")
        self._button_entry.setToolTip("Button Text")
        self._url_entry.setToolTip("URL")
        file_choose_button.setToolTip("Choose File")

        layout.addWidget(self._name_entry)
        layout.addWidget(self._button_entry)
        layout.addWidget(self._url_entry)
        layout.addWidget(file_choose_button)

        self._name_entry.setFocus()

    def _choose_file(self, type: Literal["file", "folder"]):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        if type == "file":
            self._file_path, _ = QFileDialog.getOpenFileName(self, "Choose File", "",
                                                            "All Files (*)", options=options)
        elif type == "folder":
            self._file_path = QFileDialog.getExistingDirectory(self, "Choose Folder", "", options=options)

    def for_edit(self, task_class: TaskClass) -> None:
        name, button_text, url, file_path, _ = task_class.get_task_data().values()
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

    def exec(self) -> tuple[str, str, str, str]:
        self.adjustSize()
        cursor_pos = QCursor.pos()
        geo = self.geometry()
        self.setGeometry(geo.adjusted(cursor_pos.x() - geo.width()//2, cursor_pos.y() - geo.height()//2, 0, 0))
        
        super().exec()
        return self.result()
    
    def exec_(self):
        return self.exec()
