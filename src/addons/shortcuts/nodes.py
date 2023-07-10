from __future__ import annotations
from typing import Union
from PyQt5 import QtGui

from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize, QEvent
from PyQt5.QtGui import QMouseEvent, QKeySequence
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLayout,
    QApplication,
    QSystemTrayIcon,
    QPushButton,
)

from . import shortcuts_save as Data
from FileSystem import open_file

from ui import (
    BaseWindow,
    RedButton,
    GrnButton,
    YelButton,
    TextButton,
    ConfirmationDialog,
    ACCEPTED,
    REJECTED,
)

from .dialog import TaskDialog, GroupDialog, ACCEPTED, REJECTED

from settings import UI_SCALE, apply_ui_scale as scaled
from ui.utils import get_font


class NodeChangeEvent(QEvent):
    class Event:
        NODE_RESIZED: int = 0
        NODE_DELETED: int = 1
        
    def __init__(self, event: int, node: GroupNode | TaskNode,
                 data_class: Data.TaskClass | Data.GroupClass):
        super().__init__(QEvent.Type.User)
        self.event = event
        self.node = node
        self.node_type = type(node)
        self.data_class = data_class


class BaseNode(QWidget):
    class Buttons(QWidget):
        def __init__(self, add_grn_button: bool, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            
            self.setLayout(layout := QHBoxLayout(self))
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(scaled(7))
            
            if add_grn_button:
                self.grn_button = GrnButton(self, "radial")
                layout.addWidget(self.grn_button)

            self.yel_button = YelButton(self, "radial")
            self.red_button = RedButton(self, "radial")

            layout.addWidget(self.yel_button)
            layout.addWidget(self.red_button)

    changed = pyqtSignal(NodeChangeEvent)
    """This signal is emitted with an event when any changes are made to this node."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.task: Data.TaskClass
        self.group: Data.GroupClass
        
        self._parent = parent
        self._mouse_click_offset = None
        
        self.setLayout(layout := QHBoxLayout(self))
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(scaled(10))
        
        layout.addWidget(buttons := BaseNode.Buttons(isinstance(self, GroupNode), self))

        self.red_button = buttons.red_button
        self.yel_button = buttons.yel_button
        self.grn_button = buttons.grn_button if "grn_button" in buttons.__dict__ else None
        self.buttons = buttons
        
    def set_edit_mode(self, on: bool) -> None:
        self.buttons.setHidden(not on)
        self.adjustSize()

    def delete_node(self) -> None:
        self.hide()
        self.deleteLater()
        self.changed.emit(NodeChangeEvent(NodeChangeEvent.Event.NODE_DELETED, self, self.data_class))
        
    def adjustSize(self) -> None:
        super().adjustSize()
        self.changed.emit(NodeChangeEvent(NodeChangeEvent.Event.NODE_RESIZED, self, self.data_class))

    @property
    def data_class(self):
        return self.task if "task" in self.__dict__ else self.group


class TaskNode(BaseNode):
    def __init__(self, task: Data.TaskClass, parent: QWidget) -> None:
        super().__init__(parent)
        
        self.task: Data.TaskClass = task

        self.label = QLabel(self)
        self.label.setFont(get_font(size=scaled(16)))
        self.label.hide()
        
        self.button = TextButton(self)
        self.button.clicked.connect(self._text_button_action)
        self.button.hide()
        
        layout: QHBoxLayout = self.layout()
        layout.insertWidget(0, self.label)
        layout.insertWidget(1, self.button)
        
        # XXX: fixed height should be set.
        
        self.update_contents()
        
        self.yel_button.clicked.connect(self._edit_task)
        self.red_button.clicked.connect(self._delete_task)
        
    def _set_label(self, label: str) -> None:
        self.label.setText(label)
        if label:
            self.label.show()
        else:
            self.label.hide()
        self.adjustSize()

    def _set_button(self, label: str) -> None:
        self.button.setText(label)
        if label:
            self.button.show()
        else:
            self.button.hide()
        self.adjustSize()

    def update_contents(self) -> None:
        self._set_label(self.task.task_name)
        self._set_button(text if (text := self.task.button_text) is not None else "")
        
    def _text_button_action(self) -> None:
        print("Button action")
        # XXX: button action should be implemented.
        
    def _edit_task(self) -> None:
        dialog = TaskDialog(self)
        dialog.for_edit(self.task)
        if (result := dialog.exec()) != REJECTED:
            self.task.edit_task(*result)
            self.update_contents()

    def _delete_task(self) -> None:
        dialog = ConfirmationDialog(f"Delete '{self.task.task_name}' from\
                '{Data.get_group_by_id(self.task.group_id).group_name}'?")
        if dialog.exec() == ACCEPTED:
            self.task.delete_task()
            self.changed.emit(NodeChangeEvent(NodeChangeEvent.Event.NODE_DELETED, self, self.data_class))


class GroupNode(BaseNode):
    def __init__(self, group: Data.GroupClass, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self.group = group
        self._id = group.group_id
        
        self.label = QLabel(self)
        self.label.setFont(get_font(size=scaled(24), weight="semibold"))
        self.label.hide()
        
        self.tasks_layer = QWidget(self)
        self.tasks_layer.move(0, 12)
        
        layout: QHBoxLayout = self.layout() # type: ignore
        layout.insertWidget(0, self.label)

        self._update_contents()

        self.grn_button.clicked.connect(self._new_task)
        self.yel_button.clicked.connect(self._edit_group)
        self.red_button.clicked.connect(self._delete_group)
        
    def _set_label(self, label: str) -> None:
        self.label.setText(label)
        if label:
            self.label.show()
        else:
            self.label.hide()
        self.adjustSize()
        
    def _update_contents(self) -> None:
        self._set_label(self.group.group_name)
        
    def _new_task(self) -> None:
        dialog = TaskDialog(self)
        if (result := dialog.exec()) != REJECTED:
            name, button_text, url, file_path = result
            self.group.create_task(name, None, button_text, url, file_path)

    def _edit_group(self) -> None:
        dialog = GroupDialog(self)
        dialog.for_edit(self.group.group_name)
        if (result := dialog.exec()) != REJECTED:
            self.group.group_name = result
            self._update_contents()
            
    def _delete_group(self) -> None:
        dialog = ConfirmationDialog(f"Delete '{self.group.group_name}'")
        if dialog.exec() == ACCEPTED:
            self.group.delete_group()
            self.changed.emit(NodeChangeEvent(NodeChangeEvent.Event.NODE_DELETED, self, self.data_class))
