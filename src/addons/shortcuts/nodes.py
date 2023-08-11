from __future__ import annotations
from typing import NewType

from PyQt5.QtCore import pyqtSignal, QEvent, QTimer
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLayout,
)

from utils import Signal

from . import shortcuts_save as Data

from ui import (
    RedButton,
    GrnButton,
    YelButton,
    TextButton,
    ConfirmationDialog,
    ACCEPTED,
    REJECTED,
)

from .dialog import TaskDialog, GroupDialog, ACCEPTED, REJECTED

from settings import apply_ui_scale as scaled
from ui.utils import get_font


NodeChangeEventType = NewType("NodeChangeEventType", int)

class NodeChangeEvent(QEvent):
    class Type:
        NODE_RESIZED: NodeChangeEventType = NodeChangeEventType(0)
        NODE_DELETED: NodeChangeEventType = NodeChangeEventType(1)
        NODE_MOVING: NodeChangeEventType = NodeChangeEventType(2)
        NODE_MOVED: NodeChangeEventType = NodeChangeEventType(3)
        
    def __init__(self, event: NodeChangeEventType, node: GroupNode | TaskNode, mouse_event: QMouseEvent = None):
        super().__init__(QEvent.Type.User)
        self.event = event
        self.node = node
        self.node_type = type(node)
        self.data_class = node.data_class
        self.mouse_event: QMouseEvent | None = mouse_event


NODE_RESIZED = NodeChangeEvent.Type.NODE_RESIZED
NODE_DELETED = NodeChangeEvent.Type.NODE_DELETED
NODE_MOVING = NodeChangeEvent.Type.NODE_MOVING
NODE_MOVED = NodeChangeEvent.Type.NODE_MOVED


class SubNodeManager:
    def __init__(self, layout: QLayout, parent: QWidget):
        self._nodes_container: QVBoxLayout = layout
        self._parent = parent
        
        self.departed_signal = Signal(GroupNode | TaskNode)
        
        self._current_changes = None
        
        
    def add_node(self, node: GroupNode | TaskNode) -> None:
        self._nodes_container.addWidget(node)
        node.changed.connect(self._on_node_change)
        self._update_nodes_contents_margins()
        QTimer.singleShot(0, self._parent.adjustSize)
        
    def remove_node(self, node: GroupNode | TaskNode) -> None:
        self._nodes_container.removeWidget(node)
        node.hide()
        node.deleteLater()
        self._update_nodes_contents_margins()
        QTimer.singleShot(0, self._parent.adjustSize)
        
    def _on_node_change(self, event: NodeChangeEvent) -> None:
        if event.event == NODE_DELETED:
            self.remove_node(event.node)
        elif event.event == NODE_MOVING:
            self._on_node_moving(event)
        elif event.event == NODE_MOVED:
            self._on_node_moved()
        
    def _on_node_moving(self, event: NodeChangeEvent) -> None:
        # check if the mouse hovering over any other GroupNode.
        # if so, check if the mouse is hovering top half or bottom half of the GroupNode.
        mouse_position = event.node.mapTo(self._parent, event.mouse_event.pos())  # mapped to parent widget.
        mouse_position.setX(1)  # x canceled

        for i in range(self._nodes_container.count()):
            node = self._nodes_container.itemAt(i).widget()
            if node is event.node:
                continue

            node_rect = node.geometry().adjusted(-node.geometry().x(), 0, 2, 0)  # x is set to 0 (canceled).
            top_half_rect = node_rect.adjusted(0, 0, 0, -(node.height() // 2))
            bottom_half_rect = node_rect.adjusted(0, (node.height() // 2), 0, 0)

            if top_half_rect.contains(mouse_position):
                self._current_changes: list = [event.node, i]
                break
            elif bottom_half_rect.contains(mouse_position):
                self._current_changes: list = [event.node, i +1]
                break
            
        if not self._nodes_container.geometry().contains(mouse_position):
            self.departed_signal.emit(event.node)

    def _on_node_moved(self):
        if self._current_changes is not None:
            self.change_node_index(self._current_changes[0], self._current_changes[1])
            self._current_changes = None
        self._nodes_container.update()
        
    def _update_nodes_contents_margins(self):
        # currently GroupNode contents margins are only updated.
        for i in range(self._nodes_container.count()):
            node: GroupNode | TaskNode = self._nodes_container.itemAt(i).widget()
            if isinstance(node, GroupNode):
                node.update_content_margins()

    def change_node_index(self, node: GroupNode | TaskNode, index: int) -> None:
        for i in range(self._nodes_container.count()):
            _node: GroupNode | TaskNode = self._nodes_container.itemAt(i).widget()
            if node is _node:
                index -= (1 if i < index else 0)  # for avoid index shifting when removing the widget.
                self._nodes_container.insertItem(index, self._nodes_container.takeAt(i))
                break

        if isinstance(node, GroupNode):
            group_ids = [
                self._nodes_container.itemAt(i).widget().group_class.group_id
                for i in range(self._nodes_container.count())
            ]
            Data.reorder_groups(group_ids)
            
        else:
            task_ids = [
                self._nodes_container.itemAt(i).widget().task_class.task_id
                for i in range(self._nodes_container.count())
            ]
            Data.get_group_by_id(node.task_class.group_id).reorder_tasks(task_ids)

        self._update_nodes_contents_margins()

    def set_edit_mode(self, on: bool) -> None:
        for i in range(self._nodes_container.count()):
            node: GroupNode | TaskNode = self._nodes_container.itemAt(i).widget()
            node.set_edit_mode(on)
        

class BaseNode(QWidget):
    class Buttons(QWidget):
        def __init__(self, add_grn_button: bool, parent: QWidget | None = None) -> None:
            super().__init__(parent)
            
            self.setLayout(layout := QHBoxLayout(self))
            layout.setContentsMargins(scaled(10), 0, 0, 0)
            layout.setSpacing(scaled(7))
            
            if add_grn_button:
                self.grn_button = GrnButton(self, "radial")
                layout.addWidget(self.grn_button)

            self.yel_button = YelButton(self, "radial")
            self.red_button = RedButton(self, "radial")

            layout.addWidget(self.yel_button)
            layout.addWidget(self.red_button)
    
    task_class: Data.TaskClass
    group_class: Data.GroupClass
    buttons: BaseNode.Buttons
    changed = pyqtSignal(NodeChangeEvent)
    """This signal is emitted with an event when any changes are made to this node."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._parent = parent
        self._mouse_click_offset = None
        
        
    def set_edit_mode(self, on: bool) -> None:
        self.buttons.setHidden(not on)
        self.adjustSize()

    def delete_node(self) -> None:
        self.hide()
        self.deleteLater()
        self.changed.emit(NodeChangeEvent(NODE_DELETED, self))
        
    def adjustSize(self) -> None:
        super().adjustSize()
        self.changed.emit(NodeChangeEvent(NODE_RESIZED, self))
    
    def is_first_node(self) -> bool:
        return self is self._parent.get_first_node()

    @property
    def data_class(self):
        return self.task_class if "task_class" in self.__dict__ else self.group_class
    
    
    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self._mouse_click_offset = a0.pos()
        self.raise_()

    def mouseMoveEvent(self, a0: QMouseEvent) -> None:
        if self._mouse_click_offset is not None:
            y = self.mapToParent(a0.pos() - self._mouse_click_offset).y()
            self.move(self.x(), y)
            self.changed.emit(NodeChangeEvent(NODE_MOVING, self, a0))
    
    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        self._mouse_click_offset = None
        self.changed.emit(NodeChangeEvent(NODE_MOVED, self, a0))


class TaskNode(BaseNode):
    nodes: dict[str, TaskNode] = {}
    
    def __init__(self, task_class: Data.TaskClass, parent: QWidget) -> None:
        super().__init__(parent)
        TaskNode.nodes[task_class.task_id] = self
        
        self.task_class: Data.TaskClass = task_class
        
        self.setLayout(layout := QHBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(scaled(10))
        
        layout.addWidget(buttons := BaseNode.Buttons(False, self))
        
        layout.addStretch()

        self.red_button = buttons.red_button
        self.yel_button = buttons.yel_button
        self.buttons = buttons

        self.label = QLabel(self)
        self.label.setFont(get_font(size=scaled(16)))
        self.label.hide()
        
        self.button = TextButton(self)
        self.button.clicked.connect(self._text_button_action)
        self.button.hide()
        
        layout: QHBoxLayout = self.layout()
        layout.insertWidget(0, self.label)
        layout.insertWidget(1, self.button)
        layout.setContentsMargins(0, scaled(15), 0, 0)
        
        self.setFixedHeight(self.button.sizeHint().height())
        
        self.update_contents()
        
        self.yel_button.clicked.connect(self._edit_task)
        self.red_button.clicked.connect(self._delete_task)
        
    def __repr__(self):
        return f"TaskNode: {self.task_class.task_name}"
        
        
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

    def _text_button_action(self) -> None:
        print("Button action")
        # XXX: button action should be implemented.
        
    def _edit_task(self) -> None:
        dialog = TaskDialog(self)
        dialog.for_edit(self.task_class)
        if (result := dialog.exec()) != REJECTED:
            self.task_class.edit_task(*result)
            self.update_contents()

    def _delete_task(self) -> None:
        dialog = ConfirmationDialog(f"Delete '{self.task_class.task_name}' from\
                '{Data.get_group_by_id(self.task_class.group_id).group_name}'?")
        if dialog.exec() == ACCEPTED:
            self.task_class.delete_task()
            self.changed.emit(NodeChangeEvent(NODE_DELETED, self))

    def update_contents(self) -> None:
        self._set_label(self.task_class.task_name)
        self._set_button(text if (text := self.task_class.button_text) is not None else "")
        

class GroupNode(BaseNode):
    task_node_departed_signal = pyqtSignal(TaskNode)
    """This signal will be emitted when a TaskNode is departed from the GroupNode."""
    nodes: dict[str, GroupNode] = {}
    
    def __init__(self, group_class: Data.GroupClass, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        GroupNode.nodes[group_class.group_id] = self
        
        self.group_class: Data.GroupClass = group_class
        self._id = group_class.group_id
        
        self.setLayout(main_layout := QVBoxLayout())
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        main_layout.addLayout(layout := QHBoxLayout())
        main_layout.addLayout(nodes_layout := QVBoxLayout())
        self._nodes_layout = nodes_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        nodes_layout.setContentsMargins(0, 0, 0, 0)
        nodes_layout.setSpacing(0)
        
        layout.addWidget(buttons := BaseNode.Buttons(True, self))
        
        layout.addStretch()

        self.red_button = buttons.red_button
        self.yel_button = buttons.yel_button
        self.grn_button = buttons.grn_button
        self.buttons = buttons
        
        self.label = QLabel(self)
        self.label.setFont(get_font(size=scaled(24), weight="semibold"))
        self.label.hide()
        
        layout.insertWidget(0, self.label)
        
        self._task_nodes_manager = SubNodeManager(nodes_layout, self)
        self._task_nodes_manager.departed_signal.connect(self.task_node_departed_signal.emit)

        self._update_contents()

        self.grn_button.clicked.connect(self._new_task)
        self.yel_button.clicked.connect(self._edit_group)
        self.red_button.clicked.connect(self._delete_group)
        
        # spawn TaskNodes
        for task_class in self.group_class.get_tasks():
            self._add_task_node(task_class)

    def __repr__(self):
        return f"GroupNode: {self.group_class.group_name}"


    def _update_contents(self) -> None:
        self._set_label(self.group_class.group_name)

    def _set_label(self, label: str) -> None:
        self.label.setText(label)
        if label:
            self.label.show()
        else:
            self.label.hide()
        self.adjustSize()

    def _new_task(self) -> None:
        dialog = TaskDialog(self)
        if (result := dialog.exec()) != REJECTED:
            name, button_text, url, file_path = result
            task_class = self.group_class.create_task(name, None, button_text, url, file_path)
            self._add_task_node(task_class)

    def _edit_group(self) -> None:
        dialog = GroupDialog(self)
        dialog.for_edit(self.group_class.group_name)
        if (result := dialog.exec()) != REJECTED:
            self.group_class.group_name = result
            self._update_contents()

    def _delete_group(self) -> None:
        dialog = ConfirmationDialog(f"Delete '{self.group_class.group_name}'")
        if dialog.exec() == ACCEPTED:
            while self._nodes_layout.count():
                node = self._nodes_layout.takeAt(0).widget()
                node.hide()
                node.deleteLater()
            self.group_class.delete_group()
            self.changed.emit(NodeChangeEvent(NODE_DELETED, self))

    def _add_task_node(self, task_class: Data.TaskClass) -> None:
        task_node = TaskNode(task_class, self)
        self._task_nodes_manager.add_node(task_node)

    def update_content_margins(self):
        if self.is_first_node():
            self.layout().setContentsMargins(0, 0, 0, 0)
        else:
            self.layout().setContentsMargins(0, scaled(25), 0, 0)

    def set_edit_mode(self, on: bool) -> None:
        self._task_nodes_manager.set_edit_mode(on)
        return super().set_edit_mode(on)

    def method_to_add_task(self, task_node: TaskNode) -> int:
        """Adds task_node to this group and set it's order according to the position of task_node.
        returns new id of task."""
        position = task_node.pos()
        # add the task of task_node to group of this group.
        task_node.task_class.change_group(self.group_class.group_id)
        # check if task_node position is hovering over top half or bottom half of any task_nodes.
        middle_of_task_node = position + task_node.height() // 2
        for i in range(self._nodes_layout.count()):
            _node = self._nodes_layout.itemAt(i).widget()
            if _node.rect().adjusted(0, 0, 0, -_node.height()//2).contains(middle_of_task_node):
                # task_node in top half of _node
                print("task_node in top half of node")
            elif _node.rect().adjusted(0, _node.height()//2, 0, 0).contains(middle_of_task_node):
                # task_node in bottom half of _node
                print("task_node in bottom half of node")
        # XXX: delete task_node and add new task_node with new task data.
        # if yes, put the 

    def adjustSize(self) -> None:
        super().adjustSize()
        QTimer.singleShot(0, self._parent.adjustSize)


    # uncomment this to show every individual groups.
    # def paintEvent(self, a0: QtGui.QPaintEvent) -> None:
    #     # this is created for test purposes.
    #     painter = QtGui.QPainter(self)
    #     painter.setBrush(QtGui.QColor(100, 100, 100, 100))
    #     painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
    #     painter.drawLine(0, self.height()//2, self.width(), self.height()//2)
    #     return super().paintEvent(a0)