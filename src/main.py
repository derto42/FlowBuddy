import os
import sys
import time
from functools import partial
from typing import Callable

import keyboard
from PyQt5 import QtWidgets
from PyQt5.QtCore import QRectF, QSize, Qt
from PyQt5.QtGui import (
    QColor,
    QFontMetrics,
    QIcon,
    QKeyEvent,
    QPainter,
    QPainterPath,
    QPen,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

# local imports
import FileSystem as FS
import SaveFile as SF
from utils import ConfirmationDialog
from utils import get_font

# variables
TITLE = "FlowBuddy"


class CustomButton(QPushButton):
    def __init__(self, text, padding=22):
        super().__init__(text)
        self.setFont(get_font(size=16))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #DADADA;")
        self.padding = padding
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.underMouse():
            painter.setBrush(QColor(self.property("hover_color")))
        else:
            painter.setBrush(self.palette().button())

        painter.drawRoundedRect(self.rect(), 14, 14)
        painter.setPen(self.palette().buttonText().color())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self.text())
        button_width = text_width + self.padding * 2  # Adding padding to both sides
        # Setting fixed height including top and bottom padding
        return QSize(button_width, 44)


class NewGroupDialog(QDialog):
    def __init__(self, parent=None, group_name=None):
        super().__init__(parent)

        self.moving = None
        self.offset = None
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        title_label = QLabel()
        title_label.setFont(get_font(size=24, weight="bold"))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        spacer = QSpacerItem(1, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        self.group_name_input = QLineEdit()
        self.group_name_input.setFixedSize(220, 44)
        self.group_name_input.setPlaceholderText("Group Name")
        self.group_name_input.setStyleSheet(
            "background-color: #DADADA; border-radius: 14px; padding-left: 18px; padding-right: 18px;")
        self.group_name_input.setFont(get_font(size=16))

        self.group_name_input.hover_state = False
        self.group_name_input.enterEvent = lambda event: self.set_group_name_input_hover(True)
        self.group_name_input.leaveEvent = lambda event: self.set_group_name_input_hover(False)
        layout.addWidget(self.group_name_input, alignment=Qt.AlignCenter)

        create_button = CustomButton("")
        cancel_button = CustomButton("")

        if group_name:
            title_label.setText("Edit Group")
            self.group_name_input.setText(group_name)
            create_button.setText("Edit")
        else:
            title_label.setText("New Group")
            create_button.setText("Create")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        cancel_button.setProperty("hover_color", "#FFA0A0")
        cancel_button.setStyleSheet("background-color: #FF7777; border-radius: 12px; text-align: center;")
        cancel_button.setText("Cancel")
        cancel_button.setFixedSize(110, 50)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFont(get_font(size=15))
        button_layout.addWidget(cancel_button)

        create_button.setProperty("hover_color", "#ACFFBE")
        create_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        create_button.setFixedSize(110, 50)
        create_button.setDefault(True)
        create_button.clicked.connect(self.validate_and_accept)
        create_button.setFont(get_font(size=15))
        button_layout.addWidget(create_button)

        layout.addItem(QSpacerItem(1, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addLayout(button_layout)

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

    def get_group_name(self):
        return self.group_name_input.text()

    def set_group_name_input_hover(self, state):
        self.group_name_input.hover_state = state
        if state:
            self.group_name_input.setStyleSheet(
                "background-color: #EBEBEB; border-radius: 12px; padding-left: 18px; padding-right: 18px;")
        else:
            self.group_name_input.setStyleSheet(
                "background-color: #DADADA; border-radius: 12px; padding-left: 18px; padding-right: 18px;")

    @staticmethod
    def generate_unique_name():
        existing_group_names = [group.group_name() for group in SF.get_groups()]

        base_name = "Untitled"
        counter = 1
        unique_name = base_name

        while unique_name in existing_group_names:
            unique_name = f"{base_name}{counter}"
            counter += 1

        return unique_name

    def validate_and_accept(self):
        group_name = self.group_name_input.text().strip()
        if not group_name:
            group_name = self.generate_unique_name()
            self.group_name_input.setText(group_name)

        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
            self.validate_and_accept()
        elif a0.key() == Qt.Key.Key_Escape:
            self.reject()
        return super().keyPressEvent(a0)


class NewTaskDialog(QDialog):
    def __init__(self, parent, group_name, task_data=None):
        super().__init__(parent)
        self.moving = None
        self.offset = None
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.group_name = group_name
        self.file_input = None
        self.task_data = task_data

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        title_label = QLabel("New Task")
        title_label.setFont(get_font(size=24))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        input_style = "background-color: #DADADA; border-radius: 14px; padding-left: 18px; padding-right: 18px;"
        spacer = QSpacerItem(1, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Text")
        self.text_input.setFixedSize(220, 44)
        self.text_input.setStyleSheet(input_style)
        self.text_input.setFont(get_font(size=16))
        layout.addWidget(self.text_input, alignment=Qt.AlignCenter)

        self.button_text_input = QLineEdit()
        self.button_text_input.setPlaceholderText("Button Text")
        self.button_text_input.setFixedSize(220, 44)
        self.button_text_input.setStyleSheet(input_style)
        self.button_text_input.setFont(get_font(size=16))
        layout.addWidget(self.button_text_input, alignment=Qt.AlignCenter)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")
        self.url_input.setFixedSize(220, 44)
        self.url_input.setStyleSheet(input_style)
        self.url_input.setFont(get_font(size=16))
        layout.addWidget(self.url_input, alignment=Qt.AlignCenter)

        self.file_input = ""

        self.choose_file_button = CustomButton("Choose File")
        self.choose_file_button.setFixedSize(220, 44)
        self.choose_file_button.setProperty("hover_color", "#EBEBEB")
        layout.addWidget(self.choose_file_button, alignment=Qt.AlignCenter)
        self.choose_file_button.clicked.connect(self.choose_file)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setAlignment(Qt.AlignCenter)

        cancel_button = CustomButton("")
        cancel_button.setProperty("hover_color", "#FFA0A0")
        cancel_button.setStyleSheet("background-color: #FF7777; border-radius: 12px; text-align: center;")
        cancel_button.setText("Cancel")
        cancel_button.setFixedSize(110, 50)
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFont(get_font(size=15))
        button_layout.addWidget(cancel_button)

        create_button = CustomButton("")
        create_button.setProperty("hover_color", "#ACFFBE")
        create_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        create_button.setText("Create")
        create_button.setFixedSize(110, 50)
        create_button.setDefault(True)
        create_button.clicked.connect(self.validate_and_accept)
        create_button.setFont(get_font(size=15))
        button_layout.addWidget(create_button)

        layout.addItem(QSpacerItem(1, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addLayout(button_layout)

        self.setStyleSheet("background-color: #FFFFFF;")  # set white background color
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0)
        self.setGraphicsEffect(shadow)  # set shadow effect on dialog

        if self.task_data:
            self.text_input.setText(self.task_data["text"])
            self.button_text_input.setText(self.task_data["button_text"])
            self.url_input.setText(self.task_data["url"])
            if "file" in self.task_data and self.task_data["file"]:
                self.file_input = self.task_data["file"]

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

    def choose_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose File", "", "All Files (*)", options=options)
        if file_name:
            self.file_input = file_name

    def get_task_data(self):
        text = self.text_input.text().strip()
        button_text = self.button_text_input.text().strip()
        url = self.url_input.text().strip()
        task_id = f"{self.group_name.replace(' ', '').lower()}1"
        return {
            "name": task_id,
            "text": text,
            "button_text": button_text,
            "url": url,
            "file": self.file_input
        }

    def validate_and_accept(self):
        if self.get_task_data():
            self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
            self.validate_and_accept()
        elif a0.key() == Qt.Key.Key_Escape:
            self.reject()
        return super().keyPressEvent(a0)


class CustomWindow(QWidget):

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
        exit_button.setToolTip("Exit")
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        exit_button.setFixedSize(24, 24)
        exit_button.clicked.connect(self.save_and_close)
        exit_button.enterEvent = lambda event: exit_button.setStyleSheet(
            "background-color: #FFA0A0; border-radius: 12px;")
        exit_button.leaveEvent = lambda event: exit_button.setStyleSheet(
            "background-color: #FF7777; border-radius: 12px;")

        new_group_button = QPushButton()
        new_group_button.setToolTip("New Group")
        new_group_button.setCursor(Qt.PointingHandCursor)
        new_group_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        new_group_button.setFixedSize(24, 24)
        new_group_button.clicked.connect(self.create_new_group)
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

    def toggle_edit_window(self):
        self.turn_edit_mode(not self.edit_mode)

    def turn_edit_mode(self, mode: bool):
        for widget in self.edit_widgets:
            widget: QPushButton = widget
            widget.setHidden(not mode)
        self.edit_mode = mode

    def create_toggle_button(self):
        toggle_button = QPushButton()
        toggle_button.setToolTip("Edit Mode")
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

    @staticmethod
    def create_edit_button():
        edit_button = QPushButton()
        edit_button.setToolTip("Edit Task")
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
    def set_button_style(button, style, event):
        button.setStyleSheet(style)

    def update_ui_for_new_task(self, group_name, task_data):
        for i in range(self.layout().count()):
            group_layout = self.layout().itemAt(i)
            if isinstance(group_layout, QVBoxLayout):
                header_layout = group_layout.itemAt(0)
                if isinstance(header_layout, QHBoxLayout):
                    group_label = header_layout.itemAt(0).widget()
                    if isinstance(group_label, QLabel) and group_label.text() == group_name:
                        # Create and add the new task layout
                        task_layout = QHBoxLayout()
                        task_layout.setSpacing(10)

                        delete_task_button = self.create_delete_button()
                        delete_task_button.clicked.connect(partial(self.delete_task, task_data["name"], group_name))

                        edit_task_button = self.create_edit_button()
                        edit_task_button.clicked.connect(partial(self.edit_task, task_data["name"], group_name))

                        if task_data["text"]:
                            task_text = QLabel(task_data["text"])
                            task_text.setFont(get_font(size=16))
                            task_layout.addWidget(task_text)

                        if task_data["button_text"]:
                            button = CustomButton(task_data["button_text"])
                            button.setProperty("normal_color", "#DADADA")
                            button.setProperty("hover_color", "#EBEBEB")
                            button.setStyleSheet("background-color: #DADADA; border-radius: 12px;")

                            urls = task_data["url"] if "url" in task_data else None
                            file = task_data["file"] if "file" in task_data and task_data["file"] != "file" else None
                            if urls or file:
                                button.clicked.connect(partial(self.open_url_and_file, urls, file))
                            else:
                                button.setEnabled(False)

                            task_layout.addWidget(button)

                        task_layout.addWidget(delete_task_button, alignment=Qt.AlignRight)
                        task_layout.addWidget(edit_task_button)
                        group_layout.addLayout(task_layout)
                        break

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

    def create_new_task(self, group_name):
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

    def edit_group(self, group_name, group_label_widget):
        edit_group_dialog = NewGroupDialog(self, group_name)
        edit_group_dialog.setModal(True)
        result = edit_group_dialog.exec()

        if result == QDialog.Accepted:
            if new_group_name := edit_group_dialog.get_group_name():
                SF.edit_group(group_name, new_group_name=new_group_name)
                self.rerender_groups()

    def create_new_group(self):
        new_group_dialog = NewGroupDialog(self)
        new_group_dialog.setModal(True)
        result = new_group_dialog.exec()

        if result == QDialog.Accepted:
            if group_name := new_group_dialog.get_group_name():
                SF.new_group(group_name)
            self.rerender_groups()

    @staticmethod
    def create_delete_button():
        delete_button = QPushButton()
        delete_button.setToolTip("Delete Task")
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

    def delete_group(self, group_name, group_layout: QVBoxLayout):
        if ConfirmationDialog(self, f'Delete "{group_name}" group?').exec():
            SF.Group(group_name).delete()
            self.rerender_groups()

    def delete_task(self, group_name, task, task_layout: QVBoxLayout):
        if ConfirmationDialog(self, f'Delete "{task}" task from "{group_name}" group?').exec():
            SF.Task(group_name, task).delete()
            self.rerender_groups()

    def rerender_groups(self):
        self.clearLayout(self.parent_layout)
        self.render_groups()
        self.turn_edit_mode(self.edit_mode)

    def render_groups(self):
        groups = SF.get_groups()

        self.edit_widgets = []
        for group in groups:
            group_layout = QVBoxLayout()

            group_label = QLabel(group.group_name())
            group_label.setFont(get_font(size=24, weight="bold"))

            create_task_button = QPushButton()
            create_task_button.setToolTip("Create Task")
            create_task_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
            create_task_button.setFixedSize(24, 24)
            create_task_button.clicked.connect(partial(self.create_new_task, group.group_name()))
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

    def save_position(self):

        SF.set_setting("position", (self.pos().x(), self.pos().y()))

    def save_and_close(self):
        self.save_position()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()


def show_tray_icon(parent: QApplication, activate_action: Callable):
    tray_icon = QSystemTrayIcon(QIcon(FS.icon("icon.png")), parent=parent)
    tray_icon.setToolTip(TITLE)
    tray_icon.activated.connect(
        lambda reason: activate_action()
        if reason != QSystemTrayIcon.ActivationReason.Context
        else None
    )
    tray_icon.show()

    menu = QMenu()
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(parent.quit)
    tray_icon.setContextMenu(menu)


def main():
    app = QApplication(sys.argv)

    window = CustomWindow()
    # showing the window for first time to construct the window
    # (Avoid cunstruct from the thread, which does crashes)
    window.show()
    if all(x.lower() != '-showui' for x in app.arguments()):
        window.hide()

    toggle_window = lambda: window.show() if window.isHidden() else window.hide()

    show_tray_icon(app, toggle_window)
    keyboard.add_hotkey("ctrl+`", toggle_window)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
