import sys
import json
import webbrowser
import os
import time
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QDialog, QLineEdit, QFileDialog, QMessageBox
from PyQt5.QtGui import QFont, QColor, QPainter, QPainterPath, QPalette, QPen, QFontMetrics, QPixmap, QIcon
from PyQt5.QtCore import QRectF, QEvent, QSize




class CustomButton(QPushButton):
    def __init__(self, text, padding=15):
        super().__init__(text)
        self.setFont(QFont("Helvetica", 16))
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: #DADADA;")
        self.padding = padding

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



class CustomWindow(QWidget):

    def toggle_edit_window(self):
        if self.edit_window.isVisible():
            self.edit_window.hide()
        else:
            self.edit_window.show()

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
        edit_button.setStyleSheet("background-color: #FFCD83; border-radius: 12px;")
        edit_button.setFixedSize(24, 24)
        edit_button.enterEvent = lambda event: edit_button.setStyleSheet("background-color: #FFDAA3; border-radius: 12px;")
        edit_button.leaveEvent = lambda event: edit_button.setStyleSheet("background-color: #FFCD83; border-radius: 12px;")
        return edit_button

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.parent_layout = layout      


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

        self.render_groups()
        
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

                # Update the UI for the new task
                # self.update_ui_for_new_task(group_name, task_data)
                self.clearLayout(self.parent_layout)
                self.render_groups()

    def edit_group(self, group_name):
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
                for i in range(self.layout().count()):
                    widget = self.layout().itemAt(i).widget()
                    if isinstance(widget, QLabel) and widget.text() == group_name:
                        widget.setText(new_group_name)
                        break

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

            # Update the UI to reflect the new group
            group_label = QLabel(group_name)
            group_label.setFont(QFont("helvetica", 24, QFont.Bold))

            create_task_button = QPushButton()

            delete_group_button = self.create_delete_button()
            delete_group_button.clicked.connect(partial(self.delete_group, group_name))
            create_task_button = QPushButton()
            create_task_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
            create_task_button.setFixedSize(24, 24)
            create_task_button.clicked.connect(partial(self.create_new_task, group_name))
            create_task_button.enterEvent = partial(self.set_button_style, create_task_button, "background-color: #ACFFBE; border-radius: 12px;")
            create_task_button.leaveEvent = partial(self.set_button_style, create_task_button, "background-color: #71F38D; border-radius: 12px;")
            edit_group_button = self.create_edit_button()
            edit_group_button.clicked.connect(partial(self.edit_group, group_name))

            header_layout = QHBoxLayout()
            header_layout.addWidget(group_label)
            header_layout.addStretch(1)
            #header_layout.addWidget(create_task_button)
            #header_layout.addWidget(delete_group_button)
            #header_layout.addWidget(edit_group_button)

            group_layout = QVBoxLayout()
            group_layout.addLayout(header_layout)

            self.layout().addLayout(group_layout)
            self.update()

    def save_and_close(self):
        self.save_position()
        self.close()

    def create_delete_button(self):
        delete_button = QPushButton()
        delete_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        delete_button.setFixedSize(24, 24)
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
        
    def render_groups(self):
        with open("data.json") as f:
            data = json.load(f)

        for group in data:
            group_layout = QVBoxLayout()

            group_label = QLabel(group["name"])
            group_label.setFont(QFont("helvetica", 24, QFont.Bold))

            create_task_button = QPushButton()
            create_task_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
            create_task_button.setFixedSize(24, 24)
            create_task_button.clicked.connect(partial(self.create_new_task, group["name"]))
            create_task_button.enterEvent = partial(self.set_button_style, create_task_button, "background-color: #ACFFBE; border-radius: 12px;")
            create_task_button.leaveEvent = partial(self.set_button_style, create_task_button, "background-color: #71F38D; border-radius: 12px;")
            
            delete_group_button = self.create_delete_button()
            delete_group_button.clicked.connect(partial(self.delete_group, group["name"], group_layout=group_layout))

            edit_group_button = self.create_edit_button()
            edit_group_button.clicked.connect(partial(self.edit_group, group["name"]))

            header_layout = QHBoxLayout()
            header_layout.addWidget(group_label)
            #header_layout.addStretch(1)
            #header_layout.addWidget(create_task_button)
            #header_layout.addWidget(delete_group_button)
            #header_layout.addWidget(edit_group_button)

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
                


                if task["url"]:
                    urls = task["url"].split(',')
                    button.clicked.connect(lambda checked, urls=urls: [webbrowser.open(url.strip()) for url in urls])
                elif task["file"] and task["file"] != "file":
                    button.clicked.connect(partial(os.startfile, task["file"]))
                else:
                    button.setEnabled(False)

                task_layout.addWidget(button)
                #task_layout.addWidget(delete_task_button, alignment=Qt.AlignRight)
                #task_layout.addWidget(edit_task_button)                
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
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_start_position)
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CustomWindow()
    window.show()
    sys.exit(app.exec_())

