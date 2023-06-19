from __future__ import annotations
import typing
from PyQt5 import QtGui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QWidget


class TabWidget(QTabWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        
        self.tabBar().setVisible(False)  # hiding the tabs bar
        
        
    # making the Tab Widget hidden
    def paintEvent(self, paint_event) -> None:
        return
