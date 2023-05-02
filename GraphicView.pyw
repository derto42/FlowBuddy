import sys
import json
import webbrowser
import os
from functools import partial
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect, QDialog, QLineEdit, QFileDialog, QMessageBox
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
            painter.setBrush(QColor("#FFA0A0"))
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
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        


        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        title_label = QLabel("New Group")
        title_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

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

class NewTaskDialog(QDialog):
    def __init__(self, group_name, parent=None):
        super().__init__(parent)
        self.group_name = group_name

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel(f"New Task")
        title_label.setFont(QFont("Helvetica", 24, QFont.Bold))
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        input_style = "background-color: #DADADA; border-radius: 12px; padding-left: 18px; padding-right: 18px;"
        spacer = QSpacerItem(1, 15, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)

        self.text_input = QLineEdit(self)
        self.text_input.setPlaceholderText("Text")
        self.text_input.setFixedHeight(38)
        self.text_input.setFixedWidth(200)
        self.text_input.setStyleSheet(input_style)
        self.text_input.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.text_input, alignment=Qt.AlignCenter)

        self.button_text_input = QLineEdit(self)
        self.button_text_input.setPlaceholderText("Button Text")
        self.button_text_input.setFixedHeight(38)
        self.button_text_input.setFixedWidth(200)
        self.button_text_input.setStyleSheet(input_style)
        self.button_text_input.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.button_text_input, alignment=Qt.AlignCenter)

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("URL")
        self.url_input.setFixedHeight(38)
        self.url_input.setFixedWidth(200)
        self.url_input.setStyleSheet(input_style)
        self.url_input.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.url_input, alignment=Qt.AlignCenter)

        self.file_input = "file"

        self.choose_file_button = CustomButton("Choose File")
        self.choose_file_button.setFixedSize(200, 38)
        layout.addWidget(self.choose_file_button, alignment=Qt.AlignCenter)
        self.choose_file_button.clicked.connect(self.choose_file)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
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

        layout.addItem(QSpacerItem(1, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addLayout(button_layout)

        self.setStyleSheet("background-color: #FFFFFF;")  # set white background color
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0)
        self.setGraphicsEffect(shadow)  # set shadow effect on dialog



       


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



class CustomWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.setLayout(layout)

        exit_button = QPushButton()
        exit_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        exit_button.setFixedSize(24, 24)
        exit_button.clicked.connect(self.save_and_close)
        exit_button.enterEvent = lambda event: exit_button.setStyleSheet("background-color: #FFA0A0; border-radius: 12px;")
        exit_button.leaveEvent = lambda event: exit_button.setStyleSheet("background-color: #FF7777; border-radius: 12px;")
        new_group_button = QPushButton()
        new_group_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        new_group_button.setFixedSize(24, 24)
        new_group_button.clicked.connect(self.create_new_group)
        new_group_button.enterEvent = lambda event: new_group_button.setStyleSheet("background-color: #ACFFBE; border-radius: 12px;")
        new_group_button.leaveEvent = lambda event: new_group_button.setStyleSheet("background-color: #71F38D; border-radius: 12px;")
        top_buttons_layout = QHBoxLayout()
        top_buttons_layout.addWidget(new_group_button)
        top_buttons_layout.addWidget(exit_button)
        top_buttons_widget = QWidget()
        top_buttons_widget.setLayout(top_buttons_layout)
        layout.addWidget(top_buttons_widget, alignment=Qt.AlignTop | Qt.AlignRight)



        try:
            with open("position.txt", "r") as f:
                position = f.read().split(",")
                self.move(int(position[0]), int(position[1]))
        except (FileNotFoundError, IndexError, ValueError):
            pass  # If the file doesn't exist or has an incorrect format, ignore it

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
            header_layout = QHBoxLayout()
            header_layout.addWidget(group_label)
            header_layout.addWidget(create_task_button, alignment=Qt.AlignRight)

            group_layout.addLayout(header_layout)

            for task in group["tasks"]:
                task_layout = QHBoxLayout()
                task_layout.setSpacing(16)

                if task["text"]:
                    task_text = QLabel(task["text"])
                    task_text.setFont(QFont("helvetica", 16))
                    task_layout.addWidget(task_text)

                button = CustomButton(task["button_text"])
                button.setProperty("normal_color", "#DADADA")
                button.setProperty("hover_color", "#EBEBEB")
                button.setStyleSheet("background-color: #DADADA; border-radius: 12px;")

                if task["url"]:
                    button.clicked.connect(partial(webbrowser.open, task["url"]))
                elif task["file"] and task["file"] != "file":
                    button.clicked.connect(partial(os.startfile, task["file"]))
                else:
                    button.setEnabled(False)

                task_layout.addWidget(button)
                group_layout.addLayout(task_layout)

            layout.addLayout(group_layout)

    def set_button_style(self, button, style, event):
        button.setStyleSheet(style)

    def update_ui_for_new_task(self, group_name, task_data):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() == group_name:
                task_label = QLabel(task_data["text"])
                task_label.setFont(QFont("helvetica", 18))
                self.layout.insertWidget(i + 1, task_label)
                break

    def create_new_task(self, group_name):
        new_task_dialog = NewTaskDialog(group_name, self)
        new_task_dialog.setModal(True)
        result = new_task_dialog.exec()

        if result == QDialog.Accepted:
            task_data = new_task_dialog.get_task_data()
            if task_data:
                with open("data.json", "r+") as f:
                    data = json.load(f)
                    for group in data:
                        if group["name"] == group_name:
                            group["tasks"].append(task_data)
                            break
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()




    def create_new_group(self):
        new_group_dialog = NewGroupDialog(self)
        new_group_dialog.setModal(True)  # Make the dialog modal
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
                self.layout().addWidget(group_label)
                self.update()

    def save_and_close(self):
        self.save_position()
        self.close()


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

