import sys
import json
import webbrowser
import os
import time
import keyboard
from typing import Callable
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QDialog, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QPalette, QPen, QFontMetrics, QPixmap, QIcon
from PyQt5.QtCore import QRectF, QEvent, QSize
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QThread

# local imports
import FileSystem as FS


# variables
TITLE = "FlowBuddy"


class CustomButton(QPushButton):
    def __init__(self, text, padding=15):
        super().__init__(text)
        self.setFont(QFont("Helvetica", 16))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #DADADA;")
        self.padding = padding
        self.setCursor(Qt.PointingHandCursor)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        if self.underMouse():
            # painter.setBrush(QColor("#FFA0A0"))
            painter.setBrush(QColor(self.property("hover_color")))
        else:
            painter.setBrush(self.palette().button())

        painter.drawRoundedRect(self.rect(), 12, 12)
        painter.setPen(self.palette().buttonText().color())
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())

    def sizeHint(self):
        font_metrics = QFontMetrics(self.font())
        text_width = font_metrics.width(self.text())
        button_width = text_width + self.padding * 2  # Adding padding to both sides
        size = QSize(button_width, 38)  # Setting fixed height including top and bottom padding
        return size


class NewGroupDialog(QDialog):
    def __init__(self, parent=None, group_name=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        title_label = QLabel()
        title_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        spacer = QSpacerItem(1, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        self.group_name_input = QLineEdit()
        self.group_name_input.setFixedHeight(38)
        self.group_name_input.setFixedWidth(200)
        self.group_name_input.setPlaceholderText("Group Name")
        self.group_name_input.setStyleSheet("background-color: #DADADA; border-radius: 12px; padding-left: 18px; padding-right: 18px;")
        self.group_name_input.setFont(QFont("Helvetica", 16))
        self.group_name_input.hover_state = False
        self.group_name_input.enterEvent = lambda event: self.set_group_name_input_hover(True)
        self.group_name_input.leaveEvent = lambda event: self.set_group_name_input_hover(False)
        layout.addWidget(self.group_name_input, alignment=Qt.AlignCenter)

        if group_name:
            title_label.setText("Edit Group")
            self.group_name_input.setText(group_name)
        else:
            title_label.setText("New Group")

        button_layout = QHBoxLayout()
        button_layout.setSpacing(2)

        cancel_button = CustomButton("")
        cancel_button.setProperty("hover_color", "#FFA0A0")
        cancel_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        cancel_button.setFixedSize(75, 24)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        create_button = CustomButton("")
        create_button.setProperty("hover_color", "#ACFFBE")
        create_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        create_button.setFixedSize(75, 24)
        create_button.clicked.connect(self.validate_and_accept)
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
            self.group_name_input.setStyleSheet("background-color: #EBEBEB; border-radius: 12px; padding-left: 18px; padding-right: 18px;")
        else:
            self.group_name_input.setStyleSheet("background-color: #DADADA; border-radius: 12px; padding-left: 18px; padding-right: 18px;")

    def generate_unique_name(self):
        with open("data.json", "r") as f:
            data = json.load(f)
            existing_group_names = [group["name"] for group in data]
            
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


class NewTaskDialog(QDialog):
    def __init__(self, parent, group_name, task_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.group_name = group_name
        self.file_input = None
        self.task_data = task_data

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        title_label = QLabel(f"New Task")
        title_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        input_style = "background-color: #DADADA; border-radius: 12px; padding-left: 18px; padding-right: 18px;"
        spacer = QSpacerItem(1, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Text")
        self.text_input.setFixedHeight(38)
        self.text_input.setFixedWidth(200)
        self.text_input.setStyleSheet(input_style)
        self.text_input.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.text_input, alignment=Qt.AlignCenter)

        self.button_text_input = QLineEdit()
        self.button_text_input.setPlaceholderText("Button Text")
        self.button_text_input.setFixedHeight(38)
        self.button_text_input.setFixedWidth(200)
        self.button_text_input.setStyleSheet(input_style)
        self.button_text_input.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.button_text_input, alignment=Qt.AlignCenter)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")
        self.url_input.setFixedHeight(38)
        self.url_input.setFixedWidth(200)
        self.url_input.setStyleSheet(input_style)
        self.url_input.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.url_input, alignment=Qt.AlignCenter)

        self.file_input = ""

        self.choose_file_button = CustomButton("Choose File")
        self.choose_file_button.setFixedSize(200, 38)
        self.choose_file_button.setProperty("hover_color", "#EBEBEB")
        layout.addWidget(self.choose_file_button, alignment=Qt.AlignCenter)
        self.choose_file_button.clicked.connect(self.choose_file)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setAlignment(Qt.AlignCenter)

        cancel_button = CustomButton("")
        cancel_button.setProperty("hover_color", "#FFA0A0")
        cancel_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        cancel_button.setFixedSize(75, 24)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        create_button = CustomButton("")
        create_button.setProperty("hover_color", "#ACFFBE")
        create_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        create_button.setFixedSize(75, 24)
        create_button.clicked.connect(self.validate_and_accept)
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
        task_data = self.get_task_data()
        if task_data:
            self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.moving:
            self.move(event.globalPos() - self.offset)


class CustomWindow(QWidget):

    def __init__(self):
        super().__init__()
        
        self.edit_widgets = []
        self.edit_mode = True

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        exit_button = QPushButton()
        exit_button.setCursor(Qt.PointingHandCursor)
        exit_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        exit_button.setFixedSize(24, 24)
        exit_button.clicked.connect(self.save_and_close)
        exit_button.enterEvent = lambda event: exit_button.setStyleSheet("background-color: #FFA0A0; border-radius: 12px;")
        exit_button.leaveEvent = lambda event: exit_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")

        new_group_button = QPushButton()
        new_group_button.setCursor(Qt.PointingHandCursor)
        new_group_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        new_group_button.setFixedSize(24, 24)
        new_group_button.clicked.connect(self.create_new_group)
        new_group_button.enterEvent = lambda event: new_group_button.setStyleSheet("background-color: #ACFFBE; border-radius: 12px;")
        new_group_button.leaveEvent = lambda event: new_group_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")

        toggle_button = self.create_toggle_button()

        exit_new_group_layout = QHBoxLayout()
        exit_new_group_layout.addWidget(new_group_button)
        exit_new_group_layout.addWidget(exit_button)
        exit_new_group_layout.setContentsMargins(0, 0, 0, 0)
        exit_new_group_layout.setSpacing(10)

        top_buttons_widget = QWidget()
        top_buttons_layout = QVBoxLayout()
        top_buttons_layout.setContentsMargins(0, 0, 0, 20)
        top_buttons_layout.setSpacing(10)

        top_buttons_layout.addLayout(exit_new_group_layout)  # Add the exit and new group buttons layout
        top_buttons_layout.addWidget(toggle_button)

        top_buttons_widget.setLayout(top_buttons_layout)
        layout.addWidget(top_buttons_widget, alignment=Qt.AlignTop | Qt.AlignRight)

        try:
            with open("position.txt", "r") as f:
                position = f.read().split(",")
                self.move(int(position[0]), int(position[1]))
        except (FileNotFoundError, IndexError, ValueError):
            pass  # If the file doesn't exist or has an incorrect format, ignore it

        self.parent_layout = QVBoxLayout()
        
        self.render_groups()
        
        self.turn_edit_mode(False)  # edit mode is turned off in default

        layout.addLayout(self.parent_layout)
        layout.addStretch(1)

    def toggle_edit_window(self):
        self.turn_edit_mode(not self.edit_mode)

    def turn_edit_mode(self, mode: bool):
        for widget in self.edit_widgets:
                widget: QPushButton = widget
                widget.setHidden(not mode)
        self.edit_mode = mode

    def create_toggle_button(self):
        toggle_button = QPushButton()
        toggle_button.setIcon(QIcon("icons/toggle.png"))
        toggle_button.setIconSize(QSize(58, 22))
        toggle_button.setFixedSize(58, 22)
        toggle_button.setCursor(Qt.PointingHandCursor)

        toggle_button.setStyleSheet("""
            QPushButton {
                border: none;
                icon: url(icons/toggle.png);
            }
            QPushButton:hover {
                icon: url(icons/toggle_hover.png);
            }
        """)

        toggle_button.clicked.connect(self.toggle_edit_window)
        return toggle_button

    def create_edit_button(self):
        edit_button = QPushButton()
        edit_button.setCursor(Qt.PointingHandCursor)
        edit_button.setStyleSheet("background-color: #FFCD83; border-radius: 12px;")
        edit_button.setFixedSize(24, 24)
        edit_button.enterEvent = lambda event: edit_button.setStyleSheet("background-color: #FFDAA3; border-radius: 12px;")
        edit_button.leaveEvent = lambda event: edit_button.setStyleSheet("background-color: #FFCD83; border-radius: 12px;")
        return edit_button

    def set_button_style(self, button, style, event):
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
                            task_text.setFont(QFont("helvetica", 16))
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
        # Find the existing task data
        task_data = None
        with open("data.json", "r") as f:
            data = json.load(f)
            for group in data:
                if group["name"] == group_name:
                    for task in group["tasks"]:
                        if task["name"] == task_name:
                            task_data = task
                            break
                    break

        if task_data:
            edit_task_dialog = NewTaskDialog(self, group_name, task_data)
            edit_task_dialog.setModal(True)
            result = edit_task_dialog.exec()

            if result == QDialog.Accepted:
                updated_task_data = edit_task_dialog.get_task_data()
                if updated_task_data:
                    # Generate a unique task name based on the current timestamp
                    unique_task_name = f"{group_name}{int(time.time())}"
                    updated_task_data["name"] = unique_task_name

                    # Update the task data in the JSON file
                    with open("data.json", "r+") as f:
                        data = json.load(f)
                        for group in data:
                            if group["name"] == group_name:
                                for i, task in enumerate(group["tasks"]):
                                    if task["name"] == task_name:
                                        group["tasks"][i] = updated_task_data
                                        break
                                break
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()

                self.rerender_groups()

    def create_new_task(self, group_name):
        new_task_dialog = NewTaskDialog(self, group_name)
        new_task_dialog.setModal(True)
        result = new_task_dialog.exec()

        if result == QDialog.Accepted:
            task_data = new_task_dialog.get_task_data()
            if task_data:
                # Generate a unique task name based on the current timestamp
                unique_task_name = f"{group_name}{int(time.time())}"
                task_data["name"] = unique_task_name

                with open("data.json", "r+") as f:
                    data = json.load(f)
                    for group in data:
                        if group["name"] == group_name:
                            group["tasks"].append(task_data)
                            break
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

                self.rerender_groups()

    def edit_group(self, group_name, group_label_widget):
        edit_group_dialog = NewGroupDialog(self, group_name)
        edit_group_dialog.setModal(True)
        result = edit_group_dialog.exec()

        if result == QDialog.Accepted:
            new_group_name = edit_group_dialog.get_group_name()
            if new_group_name:
                # Update the group data in the JSON file
                with open("data.json", "r+") as f:
                    data = json.load(f)
                    for group in data:
                        if group["name"] == group_name:
                            group["name"] = new_group_name
                            break
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

                # Update the UI to reflect the updated group name
                # for i in range(self.parent_layout.layout().count()):
                #     widget = self.layout().itemAt(i).widget()
                #     if isinstance(widget, QLabel) and widget.text() == group_name:
                #         widget.setText(new_group_name)
                #         break
                group_label_widget.setText(new_group_name)

    def create_new_group(self):
        new_group_dialog = NewGroupDialog(self)
        new_group_dialog.setModal(True)
        result = new_group_dialog.exec()

        if result == QDialog.Accepted:
            group_name = new_group_dialog.get_group_name()
            if group_name:
                with open("data.json", "r+") as f:
                    data = json.load(f)
                    new_group = {"name": group_name, "tasks": []}
                    data.append(new_group)
                    f.seek(0)
                    f.truncate()
                    json.dump(data, f, indent=4)

            self.rerender_groups()

    def create_delete_button(self):
        delete_button = QPushButton()
        delete_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        delete_button.setFixedSize(24, 24)
        delete_button.setCursor(Qt.PointingHandCursor)
        delete_button.enterEvent = lambda event: delete_button.setStyleSheet("background-color: #FFA0A0; border-radius: 12px;")
        delete_button.leaveEvent = lambda event: delete_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        return delete_button

    def delete_group(self, group_name, group_layout: QVBoxLayout):
        # Remove group from the data file
        with open("data.json", "r+") as f:
            data = json.load(f)
            data = [group for group in data if group["name"] != group_name]
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        self.clearLayout(group_layout)
        self.update()
        
    def delete_task(self, group_name, task, task_layout: QVBoxLayout):
        # Remove task from the data file
        with open("data.json", "r+") as f:
            data = json.load(f)
            for group_no in range(len(data)):
                if data[group_no]["name"] == group_name:
                    task_list = []
                    for t in data[group_no]["tasks"]:
                        if t["name"] == task:
                            continue
                        task_list.append(t)
                    data[group_no]["tasks"] = task_list
                    break
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        self.clearLayout(task_layout)
        self.update()
        
    def rerender_groups(self):
        self.clearLayout(self.parent_layout)
        self.render_groups()
        self.turn_edit_mode(self.edit_mode)
        
    def render_groups(self):
        with open("data.json") as f:
            data = json.load(f)

        self.edit_widgets = []
        for group in data:
            group_layout = QVBoxLayout()

            group_label = QLabel(group["name"])
            group_label.setFont(QFont("helvetica", 24, QFont.Bold))

            create_task_button = QPushButton()
            create_task_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
            create_task_button.setFixedSize(24, 24)
            create_task_button.clicked.connect(partial(self.create_new_task, group["name"]))
            create_task_button.setCursor(Qt.PointingHandCursor)
            create_task_button.enterEvent = partial(self.set_button_style, create_task_button, "background-color: #ACFFBE; border-radius: 12px;")
            create_task_button.leaveEvent = partial(self.set_button_style, create_task_button, "background-color: #71F38D; border-radius: 12px;")
            
            delete_group_button = self.create_delete_button()
            delete_group_button.clicked.connect(partial(self.delete_group, group["name"], group_layout=group_layout))

            edit_group_button = self.create_edit_button()
            edit_group_button.clicked.connect(partial(self.edit_group, group["name"], group_label))

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

            group_layout.addLayout(header_layout)


            for task in group["tasks"]:
                task_layout = QHBoxLayout()
                task_layout.setSpacing(10)

                delete_task_button = self.create_delete_button()
                delete_task_button.clicked.connect(partial(self.delete_task, group["name"], task["name"], task_layout=task_layout))

                edit_task_button = self.create_edit_button()
                edit_task_button.clicked.connect(partial(self.edit_task, group["name"], task["name"]))

                if task["text"]:
                    task_text = QLabel(task["text"])
                    task_text.setFont(QFont("helvetica", 16))
                    task_layout.addWidget(task_text)

                if task["button_text"]:
                    button = CustomButton(task["button_text"])
                    button.setProperty("normal_color", "#DADADA")
                    button.setProperty("hover_color", "#EBEBEB")
                    button.setStyleSheet("background-color: #DADADA; border-radius: 12px;")
                    task_layout.addWidget(button)

                    commands = []

                    if task["url"]:
                        urls = task["url"].split(',')
                        func_1 = lambda *x, urls=urls, name=task["name"]: [webbrowser.open(url.strip()) for url in urls]
                        commands.append(func_1)
                        
                    if "file" in task and task["file"]:
                        abs_file_path = os.path.abspath(task["file"])
                        func_2 = lambda *x, name=task["name"]: os.startfile(abs_file_path)
                        commands.append(func_2)

                        
                        
                    button.setProperty("commands", commands)
                        
                    button.clicked.connect(lambda x, btn=button: [command() for command in btn.property("commands")])
                    if not (task["url"] or task["file"]):
                        button.setEnabled(False)

                task_layout.addSpacing(10)
                task_layout.addWidget(delete_task_button)
                task_layout.addWidget(edit_task_button)
                task_layout.addStretch(1)
                
                self.edit_widgets.append(delete_task_button)
                self.edit_widgets.append(edit_task_button)
                
                group_layout.addLayout(task_layout)

            self.parent_layout.addLayout(group_layout)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

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
        with open("position.txt", "w") as f:
            f.write(f"{self.pos().x()},{self.pos().y()}")

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




class ListenKey(QThread):
    def __init__(self, key_press_action: Callable):
        super(ListenKey, self).__init__()
        self.key_press_action = key_press_action

    def run(self):
        while True:
            keyboard.wait("`")
            if self.isInterruptionRequested(): break
            if not keyboard.is_pressed("ctrl"):
                self.key_press_action()


def show_tray_icon(parent: QApplication, activate_action: Callable):
    tray_icon = QSystemTrayIcon(QIcon(FS.icon("icon.png")), parent=parent)
    tray_icon.setToolTip(TITLE)
    tray_icon.activated.connect(activate_action)
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
    if not any([x.lower() == '-showui' for x in app.arguments()]):
        window.hide()
    
    toggle_window = lambda: window.show() if window.isHidden() else window.hide()
    
    show_tray_icon(app, toggle_window)
    
    keyboard_listener = ListenKey(toggle_window)
    keyboard_listener.start()
    
    app.aboutToQuit.connect(keyboard_listener.requestInterruption)
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()