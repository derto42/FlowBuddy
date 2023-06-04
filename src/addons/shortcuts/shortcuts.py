from __future__ import annotations
import webbrowser
from typing import Optional
import contextlib


from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QLayout,
    QApplication,
    QSystemTrayIcon,
)

from . import shortcuts_save as Data
from FileSystem import open_file
from utils import HotKeys
from addon import AddOnBase
import SaveFile

from ui import (
    BaseWindow,
    RedButton,
    GrnButton,
    YelButton,
    TextButton,
    TaskDialog,
    GroupDialog,
    ConfirmationDialog,
    ACCEPTED,
    REJECTED,
)

from ui.settings import UI_SCALE
from ui.utils import get_font


NAME_TO_INT = {
    "group_layout": 0,
}


class BaseNode(QWidget):
    def __init__(self, parent: MainWindow) -> None:
        super().__init__(parent)

        self._parent = parent

        self._layout = QHBoxLayout(self)
        self.setLayout(self._layout)
        self._layout.setSpacing(0)


class GroupNode(BaseNode):
    def __init__(self, parent: QWidget, group_class: Data.GroupClass) -> None:
        super().__init__(parent)

        self._group_class = group_class

        self._layout.setContentsMargins(0, 0, 0, 0)

        self._name_label = QLabel(group_class.group_name, self)
        self._name_label.setFont(get_font(size=int(24 * UI_SCALE), weight="semibold"))
        self._name_label.setStyleSheet("color: #282828")

        new_task_button = GrnButton(self, "radial")
        edit_group_button = YelButton(self, "radial")
        delete_group_button = RedButton(self, "radial")
        new_task_button.clicked.connect(self.on_new_task)
        edit_group_button.clicked.connect(self.on_edit_group)
        delete_group_button.clicked.connect(self.on_delete_group)
        new_task_button.setToolTip("Add Task")
        edit_group_button.setToolTip("Edit Group")
        delete_group_button.setToolTip("Delete Group")

        self._parent.add_to_editors(new_task_button, edit_group_button, delete_group_button)

        self._layout.addWidget(self._name_label)
        self._layout.addSpacing(int(13 * UI_SCALE))
        self._layout.addWidget(new_task_button)
        self._layout.addSpacing(int(9 * UI_SCALE))
        self._layout.addWidget(edit_group_button)
        self._layout.addSpacing(int(9 * UI_SCALE))
        self._layout.addWidget(delete_group_button)
        self._layout.addStretch()

    def on_new_task(self, event) -> None:
        self._parent.add_task(self)

    def on_edit_group(self, event) -> None:
        dialog = GroupDialog(self)
        dialog.for_edit(self._group_class.group_name)
        dialog.setTitle("Edit Group")
        if dialog.exec() != REJECTED:
            self._group_class.group_name = dialog.result()
            self._name_label.setText(self._group_class.group_name)
            self._parent._nodes[self._group_class.group_id] = self._parent._nodes.pop(self._group_class.group_id)
            self.update()
            self.adjustSize()
            self._parent.update()
            QApplication.instance().processEvents()
            QApplication.instance().processEvents()
            self._parent.adjustSize()

    def on_delete_group(self, event) -> None:
        dialog = ConfirmationDialog(f"Delete '{self._group_class.group_name}'?", self)
        if dialog.exec() == ACCEPTED:
            self._group_class.delete_group_and_tasks()
            self.delete()

    def delete(self):
        group_layout = self._parent._nodes[self._group_class.group_id].pop(NAME_TO_INT["group_layout"])
        del self._parent._nodes[self._group_class.group_id]
        self._parent.clearLayout(group_layout)
        self.hide()
        self.deleteLater()
        self._parent.adjust_group_layouts()
        QApplication.instance().processEvents()
        QApplication.instance().processEvents()
        self._parent.update()
        self._parent.adjustSize()


class TaskNode(BaseNode):
    def __init__(self, parent: MainWindow, group_node: GroupNode, task: Data.TaskClass):
        super().__init__(parent)

        self._group_node = group_node
        self._task = task

        self._text_button = None

        self._layout.setContentsMargins(0, int(16 * UI_SCALE), 0, 0)

        self._name_label = QWidget()
        self._name_label.setLayout(layout := QHBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        name_label = QLabel(task.task_name, self)
        name_label.setFont(get_font(size=int(16 * UI_SCALE)))
        name_label.setStyleSheet("color: #282828")
        layout.addWidget(name_label)
        layout.addSpacing(int(13 * UI_SCALE))
        # making setText and text of name_label accessible from self._name_label
        self._name_label.setText = name_label.setText
        self._name_label.text = name_label.text
        self._layout.addWidget(self._name_label)
        if not task.task_name:
            self._name_label.hide()

        self._text_button = QWidget()
        self._text_button.setLayout(text_button_layout := QHBoxLayout())
        text_button_layout.setContentsMargins(0, 0, int(13 * UI_SCALE), 0)
        text_button_layout.setSpacing(0)

        text_button = TextButton(self, task.button_text)
        text_button.setFont(get_font(size=int(16 * UI_SCALE)))
        text_button.clicked.connect(self.on_text_button)
        self._text_button.setText = text_button.setText
        text_button_layout.addWidget(text_button)
        self._layout.addWidget(self._text_button)
        if task.button_text is None:
            self._text_button.hide()

        edit_task_button = YelButton(self, "radial")
        delete_task_button = RedButton(self, "radial")

        edit_task_button.clicked.connect(self.on_edit_task)
        delete_task_button.clicked.connect(self.on_delete_task)

        edit_task_button.setToolTip("Edit Task")
        delete_task_button.setToolTip("Delete Task")

        self._parent.add_to_editors(edit_task_button, delete_task_button)

        self._layout.addWidget(edit_task_button)
        self._layout.addSpacing(int(9 * UI_SCALE))
        self._layout.addWidget(delete_task_button)
        self._layout.addStretch()

    def on_edit_task(self, event) -> None:
        dialog = TaskDialog(self)
        dialog.for_edit(
            self._task.task_name,
            self._task.button_text,
            self._task.url,
            self._task.file_path,
        )
        dialog.setTitle("Edit Task")
        if dialog.exec() != REJECTED:
            self._edit_data(dialog)

            # i don't know why pyqt5 needs 10 lines of codes just for update the ui.
            self.update()
            self.adjustSize()
            self._parent.update()
            QApplication.instance().processEvents()
            QApplication.instance().processEvents()
            self._parent.adjustSize()
            self._parent.update()
            QApplication.instance().processEvents()
            QApplication.instance().processEvents()
            self._parent.adjustSize()

    def on_delete_task(self) -> None:
        dialog = ConfirmationDialog(
            f"Delete '{self._task.task_name}' from '{self._group_node._group_class.group_name}'?",
            self,
        )
        if dialog.exec() == ACCEPTED:
            self._group_node._group_class.delete_task(self._task.task_id)
            self.delete()

    def on_text_button(self) -> None:
        [webbrowser.open(_url) for _url in self._task.url]
        open_file(self._task.file_path)

    def _edit_data(self, dialog: TaskDialog) -> None:
        task_name, button_text, url, file_path = dialog.result()
        self._task.edit_task(task_name=task_name, button_text=button_text, url=url, file_path=file_path)

        self._name_label.setText(task_name)

        if button_text is not None:
            if self._text_button.isHidden():
                self._text_button.show()
            self._text_button.setText(button_text)

        elif not self._text_button.isHidden():
            self._text_button.hide()

        if task_name:
            if self._name_label.isHidden():
                self._name_label.show()
        elif not self._name_label.isHidden():
            self._name_label.hide()

        QApplication.instance().processEvents()
        self.update()
        self.adjustSize()
        self._parent.update()
        self._parent.adjustSize()

    def delete(self) -> None:
        self.hide()
        self.deleteLater()
        del self._parent._nodes[self._group_node._group_class.group_id][self._task.task_id]
        QApplication.instance().processEvents()
        QApplication.instance().processEvents()
        self._parent.update()
        self._parent.adjustSize()


class MainWindow(BaseWindow):
    window_toggle_signal = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(True, parent)

        self._edit_mode = False
        self._editors: list[QWidget] = []
        self._nodes = {}

        self.window_toggle_signal.connect(self.toggle_window)

        self.setLayout(layout := QVBoxLayout())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        for group_id in Data.load_groups():
            group_class = Data.get_group_by_id(group_id)
            group_node = self.create_group(group_class)

            for task in group_class.get_tasks():
                self.create_task(group_node, task)

        layout.addStretch()
        layout.addSpacing(0)

        layout.addWidget(add_group_widget := QWidget(self))
        add_group_widget.setContentsMargins(0, int(29 * UI_SCALE), 0, 0)

        add_group_widget.setLayout(add_group_layout := QHBoxLayout())
        add_group_layout.setContentsMargins(0, 0, 0, 0)
        add_group_layout.setSpacing(0)

        add_group_label = QLabel("Add New Group", self)
        add_group_label.setFont(get_font(size=int(24 * UI_SCALE), weight="semibold"))
        add_group_label.setStyleSheet("color: #ABABAB")

        add_group_button = GrnButton(self, "radial")
        add_group_button.clicked.connect(self.add_group)
        add_group_button.setToolTip("Add Group")

        add_group_layout.addWidget(add_group_label)
        add_group_layout.addSpacing(int(13 * UI_SCALE))
        add_group_layout.addWidget(add_group_button)
        add_group_layout.addStretch()

        self.add_to_editors(add_group_widget)

        try:
            position = SaveFile.get_setting("position")
        except SaveFile.NotFound:
            pass
        else:
            self.move(position[0], position[1])
        self.toggle_edit_mode(False)
        self.animate = True
        QApplication.instance().processEvents()
        self.adjustSize()

    def toggle_window(self) -> None:
        if self.isHidden():
            self.setFixedSize(1, 1)
            self.show()
            self.adjustSize()
        else:
            self.hide()

    def add_group(self) -> None:
        dialog = GroupDialog(self)
        if dialog.exec() != REJECTED:
            new_group = Data.GroupClass(dialog.result())
            self.create_group(new_group)

    def create_group(self, group_class: Data.GroupClass) -> GroupNode:
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(0)
        group_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.layout().insertLayout(len(self._nodes), group_layout)
        group_layout.addWidget(group_node := GroupNode(self, group_class))
        group_node.on_new_task = self.add_task
        self._nodes[group_class.group_id] = {0: group_layout}

        self.adjust_group_layouts()

        QApplication.instance().processEvents()
        self.update()
        self.adjustSize()
        return group_node

    def add_task(self, group_node: GroupNode) -> None:
        dialog = TaskDialog(self)
        if dialog.exec() != REJECTED:
            task_name, button_text, url, file_path = dialog.result()

            new_task = group_node._group_class.create_task(
                task_name=task_name,
                button_text=button_text,
                url=url,
                file_path=file_path,
            )

            self.create_task(group_node, new_task)

    def create_task(self, group_node: GroupNode, task: Data.TaskClass) -> None:
        task_node = TaskNode(self, group_node, task)
        self._nodes[group_node._group_class.group_id][NAME_TO_INT["group_layout"]].addWidget(task_node)
        self._nodes[group_node._group_class.group_id][task.task_id] = task_node
        QApplication.instance().processEvents()
        self.update()
        self.adjustSize()

    def clearLayout(self, layout: QLayout) -> None:
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.hide()
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
            layout.deleteLater()
        QApplication.instance().processEvents()

    def adjust_group_layouts(self) -> None:
        # adding ContentsMargins to layout of groups.
        for index, (_, _group_node) in enumerate(self._nodes.items()):
            if index == len(self._nodes) - 1:
                _group_node[NAME_TO_INT["group_layout"]].setContentsMargins(0, 0, 0, 0)
            else:
                _group_node[NAME_TO_INT["group_layout"]].setContentsMargins(0, 0, 0, int(29 * UI_SCALE))

    def add_to_editors(self, *widgets: QWidget) -> None:
        self._editors += [*widgets]

    def on_edit_button_clicked(self, event) -> None:
        self.toggle_edit_mode()
        QApplication.instance().processEvents()
        self.adjustSize()
        return super().on_edit_button_clicked(event)

    def toggle_edit_mode(self, mode: Optional[bool] = None) -> None:
        self._edit_mode = not self._edit_mode if mode is None else mode
        for widget in self._editors:
            try:
                widget.setHidden(not self._edit_mode)
            except Exception:
                self._editors.remove(widget)

        QApplication.instance().processEvents()

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        SaveFile.apply_settings("position", [self.pos().x(), self.pos().y()])
        return super().mouseReleaseEvent(a0)
    
    def show(self) -> None:
        SaveFile.apply_settings("hidden", False)
        return super().show()
    
    def hide(self) -> None:
        SaveFile.apply_settings("hidden", True)
        return super().hide()
    
    def setHidden(self, hidden: bool) -> None:
        SaveFile.apply_settings("hidden", hidden)
        return super().setHidden(hidden)


window = MainWindow()

with contextlib.suppress(SaveFile.NotFound):
    if not SaveFile.get_setting("hidden"):
        QApplication.instance().processEvents()
        window.update()
        window.show()
        
HotKeys.add_global_shortcut("<ctrl>+`", window.window_toggle_signal.emit)

AddOnBase.system_tray_icon.activated.connect(
    lambda reason: window.window_toggle_signal.emit()
    if reason != QSystemTrayIcon.ActivationReason.Context
    else None
)