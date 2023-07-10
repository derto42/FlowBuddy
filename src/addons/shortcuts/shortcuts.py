from __future__ import annotations
from typing import overload

from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt5.QtGui import QMouseEvent, QKeySequence

from addon import AddOnBase

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

from .nodes import GroupNode, TaskNode, NodeChangeEvent

from settings import apply_ui_scale as scaled


add_on_base = AddOnBase()
add_on_base.set_icon_path("icon.png")
add_on_base.set_name("Shortcuts")


class MainWindow(BaseWindow):
    def __init__(self) -> None:
        super().__init__(hide_title_bar = False)
        
        self._nodes: list[GroupNode | TaskNode] = []
        self._edit_mode: bool = False
        
        self.toggle_window = lambda: window.show() if window.isHidden() else window.hide()

        self.setContentsMargins(x := scaled(15), x, x, x)
        
        for group_id in Data.load_groups():
            group = Data.get_group_by_id(group_id)
            self._add_group_node(group)
            for task in group.get_tasks():
                self._add_task_node(task)
                
        self._update_size()

        self.yel_button.clicked.connect(self._toggle_edit_mode)
        self.red_button.clicked.connect(self.toggle_window)


    def _add_group_node(self, group_class: Data.GroupClass) -> None:
        if len(self._nodes) != 0:
            self._nodes.append(QSize(0, scaled(25)))
        group_node = GroupNode(group_class, self)
        self._setup_node(group_node)
        
    def _add_task_node(self, task_class: Data.TaskClass) -> None:
        if len(self._nodes) != 0:
            self._nodes.append(QSize(0, scaled(12)))
        task_node = TaskNode(task_class, self)
        self._setup_node(task_node)

    def _setup_node(self, node: TaskNode | GroupNode):
        node.move(self._get_next_position())
        node.set_edit_mode(self._edit_mode)
        node.changed.connect(self._on_node_changed)
        self._nodes.append(node)
        
    def _delete_node(self, node: TaskNode | GroupNode) -> None:
        node.hide()
        node.deleteLater()
        self._nodes.remove(node)
        self._update_size()
        
    def _on_node_changed(self, event: NodeChangeEvent) -> None:
        if event.event == NodeChangeEvent.Event.NODE_RESIZED:
            self._update_size()
        elif event.event == NodeChangeEvent.Event.NODE_DELETED:
            self._delete_node(event.node)
        
    def _get_next_position(self) -> QPoint:
        y = sum(node.height() for node in self._nodes)
        return self._add_paddings(0, y)
    
    def _position_of_node_by_index(self, node_index: int) -> QPoint:
        y = sum(node.height() for node in self._nodes[:node_index])  # XXX: should remove counting QSize
        return self._add_paddings(0, y)

    def _add_paddings(self, x, y):
        y += self.contentsMargins().top()
        x += self.contentsMargins().left()
        return QPoint(x, y)
    
    def _update_node_position(self) -> None:
        pass  # XXX: should be implemented.
    
    def _update_size(self) -> None:
        if self._nodes:
            width = max(node.width() for node in self._nodes)
            height = sum(node.height() for node in self._nodes)
            width += self.contentsMargins().left() + self.contentsMargins().right()  # adding the contentsMargins
            height += self.contentsMargins().top() + self.contentsMargins().bottom()  # adding the contentsMargins
            self.setFixedSize(width, height)
        
    def _toggle_edit_mode(self) -> None:
        self._edit_mode = not self._edit_mode
        [node.set_edit_mode(self._edit_mode) for node in self._nodes if not isinstance(node, QSize)]
        self._update_size()
        

window = MainWindow()
add_on_base.activate = window.toggle_window