from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel
)
from PyQt5.QtGui import QKeyEvent, QShowEvent


from settings import UI_SCALE
from .custom_button import RedButton, GrnButton
from .utils import get_font


ACCEPTED = QDialog.Accepted
REJECTED = QDialog.Rejected


class BaseDialog(QDialog):
    def __init__(self, title: str = "Title",
                 parent: QWidget | None = None,) -> None:
        super().__init__(parent = parent)
        
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._title = QLabel(title, self)
        self._layout.addWidget(self._title)
        self._title.setFont(get_font(size=int(24 * UI_SCALE), weight="semibold"))
        self._title.setStyleSheet("color: #282828")
        self._title.setAlignment(Qt.AlignCenter)
        
        self._main_layout = QWidget(self)
        self._layout.addWidget(self._main_layout)
        
        self._layout.insertLayout
        self._layout.addLayout(button_layout:=QHBoxLayout())
        
        button_layout.addStretch()
        button_layout.addWidget(reject_button:=RedButton(self, "long"))
        button_layout.addSpacing(int(7 * UI_SCALE))
        button_layout.addWidget(accept_button:=GrnButton(self, "long"))
        button_layout.addStretch()
        accept_button.clicked.connect(lambda : self.accept())
        reject_button.clicked.connect(lambda : self.reject())
        accept_button.setToolTip("Ok")
        reject_button.setToolTip("Cancel")
        accept_button.setDefault(True)
        
        self.setLayout = self._main_layout.setLayout
        self.layout = self._main_layout.layout
        
        self.setModal(True)
        
        # self.setFixedSize(100, 100)
        
        
    def setTitle(self, title: str) -> None:
        self._title.setText(title)
        
    
    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() in [Qt.Key.Key_Enter, Qt.Key.Key_Return]:
            self.accept()
        elif a0.key() is Qt.Key.Key_Escape:
            self.reject()
        return super().keyPressEvent(a0)
    
    def showEvent(self, a0: QShowEvent) -> None:
        self.adjustSize()
        return super().showEvent(a0)


class ConfirmationDialog(BaseDialog):
    def __init__(self, title: str = "Title", parent: QWidget | None = None) -> None:
        super().__init__(title, parent)
        
        self._title.setFont(get_font(size=int(16 * UI_SCALE)))
        self._title.setStyleSheet("color: #282828")
