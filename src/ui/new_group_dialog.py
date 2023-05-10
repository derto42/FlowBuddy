from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QLineEdit,
    QSizePolicy
)
from PyQt5.QtGui import (
    QPainter,
    QPainterPath,
    QKeyEvent,
    QColor,
    QPen
)

import SaveFile as SF
from .get_font import get_font
from .custom_button import CustomButton


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