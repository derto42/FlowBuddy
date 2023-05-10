import sys
import time
from functools import partial

from PyQt5 import QtWidgets
from PyQt5.QtCore import QRectF, QSize, Qt
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt5.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import FileSystem as FS
import SaveFile as SF

from .get_font import get_font

from .custom_button import CustomButton
from .new_group_dialog import NewGroupDialog
from .new_task_dialog import NewTaskDialog
from .confirmation_dialog import ConfirmationDialog



class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.drag_start_position = None
        self.edit_widgets = []
        self.edit_mode = True

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        self.setLayout(layout)

        exit_button = QPushButton()
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        exit_button.setFixedSize(24, 24)
        exit_button.clicked.connect(self.save_and_close)
        exit_button.enterEvent = lambda event: exit_button.setStyleSheet(
            "background-color: #FFA0A0; border-radius: 12px;")
        exit_button.leaveEvent = lambda event: exit_button.setStyleSheet(
            "background-color: #FF7777; border-radius: 12px;")

        new_group_button = QPushButton()
        new_group_button.setCursor(Qt.PointingHandCursor)
        new_group_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        new_group_button.setFixedSize(24, 24)
        new_group_button.clicked.connect(self.create_group)
        new_group_button.enterEvent = lambda event: new_group_button.setStyleSheet(
            "background-color: #ACFFBE; border-radius: 12px;")
        new_group_button.leaveEvent = lambda event: new_group_button.setStyleSheet(
            "background-color: #71F38D; border-radius: 12px;")

        toggle_button = self.create_toggle_button()

        exit_new_group_layout = QHBoxLayout()
        exit_new_group_layout.addWidget(new_group_button)
        exit_new_group_layout.addWidget(exit_button)
        exit_new_group_layout.setContentsMargins(0, 0, 0, 0)
        exit_new_group_layout.setSpacing(10)

        top_buttons_widget = QWidget()
        top_buttons_layout = QVBoxLayout()
        top_buttons_layout.setContentsMargins(0, 0, 0, 0)
        top_buttons_layout.setSpacing(10)

        top_buttons_layout.addLayout(exit_new_group_layout)  # Add the exit and new group buttons layout
        top_buttons_layout.addWidget(toggle_button)

        top_buttons_widget.setLayout(top_buttons_layout)
        layout.addWidget(top_buttons_widget, alignment=Qt.AlignTop | Qt.AlignRight)

        if (position := SF.get_setting("position")) is not None:
            self.move(position[0], position[1])

        self.parent_layout = QVBoxLayout()

        self.render_groups()

        self.turn_edit_mode(False)  # edit mode is turned off in default

        layout.addLayout(self.parent_layout)


    def render_groups(self):
        groups = SF.get_groups()

        self.edit_widgets = []
        for group in groups:
            group_layout = QVBoxLayout()

            group_label = QLabel(group.group_name())
            group_label.setFont(get_font(size=24, weight="bold"))

            create_task_button = QPushButton()
            create_task_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
            create_task_button.setFixedSize(24, 24)
            create_task_button.clicked.connect(partial(self.create_task, group.group_name()))
            create_task_button.setCursor(Qt.PointingHandCursor)
            create_task_button.enterEvent = partial(self.set_button_style, create_task_button,
                                                    "background-color: #ACFFBE; border-radius: 12px;")
            create_task_button.leaveEvent = partial(self.set_button_style, create_task_button,
                                                    "background-color: #71F38D; border-radius: 12px;")

            size_policy = create_task_button.sizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            create_task_button.setSizePolicy(size_policy)

            delete_group_button = self.create_delete_button()
            delete_group_button.clicked.connect(
                partial(self.delete_group, group.group_name(), group_layout=group_layout))

            edit_group_button = self.create_edit_button()
            edit_group_button.clicked.connect(partial(self.edit_group, group.group_name(), group_label))

            header_layout = QHBoxLayout()
            header_layout.addWidget(group_label)
            header_layout.addSpacing(10)
            header_layout.addWidget(create_task_button)
            header_layout.addWidget(delete_group_button)
            header_layout.addWidget(edit_group_button)
            header_layout.addStretch(1)

            self.edit_widgets.append(create_task_button)
            self.edit_widgets.append(delete_group_button)
            self.edit_widgets.append(edit_group_button)

            self.parent_layout.addSpacing(24)
            group_layout.addLayout(header_layout)

            for task in group.get_tasks():
                task_layout = QHBoxLayout()
                task_layout.setSpacing(10)

                delete_task_button = self.create_delete_button()
                delete_task_button.clicked.connect(
                    partial(self.delete_task, group.group_name(), task.task_name(), task_layout=task_layout))

                edit_task_button = self.create_edit_button()
                edit_task_button.clicked.connect(partial(self.edit_task, group.group_name(), task.task_name()))

                if text := task.text():
                    task_text = QLabel(text)
                    task_text.setFont(get_font(size=16))
                    task_layout.addWidget(task_text)

                if button_text := task.button_text():
                    button = CustomButton(button_text)
                    button.setProperty("normal_color", "#DADADA")
                    button.setProperty("hover_color", "#EBEBEB")
                    button.setStyleSheet("background-color: #DADADA; border-radius: 12px;")
                    task_layout.addWidget(button)

                    commands = FS.open_task(task.url(), task.name(), task.file(), sys.platform)

                    button.setProperty("commands", commands)

                    button.clicked.connect(lambda x, btn=button: [command() for command in btn.property("commands")])
                    if not (task.url() or task.file()):
                        button.setEnabled(False)

                task_layout.addSpacing(10)
                task_layout.addWidget(delete_task_button)
                task_layout.addWidget(edit_task_button)
                task_layout.addStretch(1)

                self.edit_widgets.append(delete_task_button)
                self.edit_widgets.append(edit_task_button)

                group_layout.addSpacing(12)
                group_layout.addLayout(task_layout)

            self.parent_layout.addLayout(group_layout)

        self.adjustSize()

    def rerender_groups(self):
        self.clearLayout(self.parent_layout)
        self.render_groups()
        self.turn_edit_mode(self.edit_mode)


    @staticmethod
    def set_button_style(button, style, event):
        button.setStyleSheet(style)

    @staticmethod
    def create_edit_button():
        edit_button = QPushButton()
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.setStyleSheet("background-color: #FFCD83; border-radius: 12px;")
        edit_button.setFixedSize(24, 24)
        edit_button.enterEvent = lambda event: edit_button.setStyleSheet(
            "background-color: #FFDAA3; border-radius: 12px;")
        edit_button.leaveEvent = lambda event: edit_button.setStyleSheet(
            "background-color: #FFCD83; border-radius: 12px;")
        size_policy = edit_button.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        edit_button.setSizePolicy(size_policy)
        return edit_button

    @staticmethod
    def create_delete_button():
        delete_button = QPushButton()
        delete_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        delete_button.setFixedSize(24, 24)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.enterEvent = lambda event: delete_button.setStyleSheet(
            "background-color: #FFA0A0; border-radius: 12px;")
        delete_button.leaveEvent = lambda event: delete_button.setStyleSheet(
            "background-color: #FF7777; border-radius: 12px;")
        size_policy = delete_button.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        delete_button.setSizePolicy(size_policy)
        return delete_button

    def create_toggle_button(self):
        toggle_button = QPushButton()
        toggle_button.setIconSize(QSize(58, 22))
        toggle_button.setFixedSize(58, 22)
        toggle_button.setCursor(Qt.PointingHandCursor)
        
        toggle_icon = FS.icon("toggle.png").replace("\\","/")
        toggle_hover_icon = FS.icon("toggle_hover.png").replace("\\","/")
        
        toggle_button.setStyleSheet("""
            QPushButton {
                border: none;
                icon: url(%s);
            }
            QPushButton:hover {
                icon: url(%s);
            }
        """%(toggle_icon, toggle_hover_icon))

        toggle_button.clicked.connect(self.toggle_edit_window)
        return toggle_button


    def toggle_edit_window(self):
        self.turn_edit_mode(not self.edit_mode)

    def turn_edit_mode(self, mode: bool):
        for widget in self.edit_widgets:
            widget: QPushButton = widget
            widget.setHidden(not mode)
        self.edit_mode = mode


    def create_group(self):
        new_group_dialog = NewGroupDialog(self)
        new_group_dialog.setModal(True)
        result = new_group_dialog.exec()

        if result == QDialog.Accepted:
            if group_name := new_group_dialog.get_group_name():
                SF.new_group(group_name)
            self.rerender_groups()

    def edit_group(self, group_name, group_label_widget):
        edit_group_dialog = NewGroupDialog(self, group_name)
        edit_group_dialog.setModal(True)
        result = edit_group_dialog.exec()

        if result == QDialog.Accepted:
            if new_group_name := edit_group_dialog.get_group_name():
                SF.edit_group(group_name, new_group_name=new_group_name)
                self.rerender_groups()

    def delete_group(self, group_name, group_layout: QVBoxLayout):
        if ConfirmationDialog(self, f'Delete "{group_name}" group?').exec():
            SF.Group(group_name).delete()
            self.rerender_groups()


    def create_task(self, group_name):
        new_task_dialog = NewTaskDialog(self, group_name)
        new_task_dialog.setModal(True)
        result = new_task_dialog.exec()

        if result == QDialog.Accepted:
            if task_data := new_task_dialog.get_task_data():
                # Generate a unique task name based on the current timestamp
                unique_task_name = f"{group_name}{int(time.time())}"
                task_data["name"] = unique_task_name
                SF.new_task(group_name, unique_task_name)
                SF.edit_task(group_name, unique_task_name,
                             new_task_content=task_data)

                self.rerender_groups()

    def edit_task(self, group_name, task_name):
        if task_data := SF.get_task(group_name, task_name).get_json():
            edit_task_dialog = NewTaskDialog(self, group_name, task_data)
            edit_task_dialog.setModal(True)
            result = edit_task_dialog.exec()

            if result == QDialog.Accepted:
                if updated_task_data := edit_task_dialog.get_task_data():
                    # Generate a unique task name based on the current timestamp
                    unique_task_name = f"{group_name}{int(time.time())}"
                    updated_task_data["name"] = unique_task_name
                    SF.edit_task(group_name, task_name,
                                 new_task_name=unique_task_name,
                                 new_task_content=updated_task_data)

                self.rerender_groups()

    def delete_task(self, group_name, task, task_layout: QVBoxLayout):
        if ConfirmationDialog(self, f'Delete "{task}" task from "{group_name}" group?').exec():
            SF.Task(group_name, task).delete()
            self.rerender_groups()


    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
        QtWidgets.QApplication.instance().processEvents()

    def save_and_close(self):
        SF.set_setting("position", (self.pos().x(), self.pos().y()))
        self.hide()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect().adjusted(0, 0, -1, -1)), 12, 12)
        painter.fillPath(path, QColor(Qt.white))

        # Adding the stroke around the window
        stroke_color = QColor("#DADADA")
        painter.setPen(QPen(stroke_color, 2))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

