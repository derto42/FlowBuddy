from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QFileDialog
)
from PyQt5.QtGui import (
    QColor,
    QPen,
    QPainter,
    QPainterPath,
    QKeyEvent
)

from .get_font import get_font
from .custom_button import CustomButton

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