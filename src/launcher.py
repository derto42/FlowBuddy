import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt, QPoint, QRect, QEvent
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QPalette
import webbrowser

# Constants
SAVE_JSON = 'launcher.json'
BUTTON_WIDTH = 110
BUTTON_HEIGHT = 30
BUTTON_OFFSET = 120
GRID_OFFSET = 30

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.grid_size = 64
        self.gutter_size = GRID_OFFSET

        # setup window
        self.setGeometry(0, 0, QApplication.desktop().width(), QApplication.desktop().height())
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Load squares
        self.squares = [DraggableSquare(self, QPoint(i*(self.grid_size+self.gutter_size) + self.gutter_size, self.gutter_size), self.grid_size, 'gray', folder, f'https://www.google.com/search?q={folder}') 
                        for i, folder in enumerate(os.listdir('add_ons'))]
        
        self.load_positions()

    def save_positions(self):
        return {square.label.text(): (square.x(), square.y()) for square in self.squares}

    def load_positions(self):
        try:
            with open(SAVE_JSON, 'r') as f:
                positions = json.load(f)
            for square in self.squares:
                if square.label.text() in positions:
                    square.move(QPoint(*positions[square.label.text()]))
        except FileNotFoundError:
            pass  # No saved positions to load

    def mousePressEvent(self, event):
        for square in self.squares:
            if square.geometry().contains(event.pos()):
                square.mousePressEvent(event)
                return

    def closeEvent(self, event):
        with open("launcher.json", "w") as f:
            json.dump({"squares": self.save_positions()}, f)


class DraggableSquare(QLabel):
    def __init__(self, parent, pos, size, color, label, url):
        super().__init__(parent)
        self.size = size
        self.setFixedSize(size, size)
        self.move(pos)
        self.grabOffset = None
        self.url = url
        self.label = QLabel(label, self)
        self.label.setGeometry(QRect(0, 0, size, 20))
        self.label.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f'background-color: {color}; border-radius: 9px;')
        self.highlighted = False
        self.show()

    def mousePressEvent(self, event):
        self.raise_()
        self.grabOffset = event.pos()
        self.highlighted = True
        self.update()
        


    def mouseReleaseEvent(self, event):
        self.grabOffset = None
        self.highlighted = False
        self.update()
        self.parent().save_positions()

    def mouseMoveEvent(self, event):
        if self.grabOffset is not None:
            new_pos = self.mapToParent(event.pos() - self.grabOffset)

            # Snap to grid
            grid_size = self.parent().grid_size + self.parent().gutter_size
            new_pos.setX(round((new_pos.x() - self.parent().gutter_size) / grid_size) * grid_size + self.parent().gutter_size)
            new_pos.setY(round((new_pos.y() - self.parent().gutter_size) / grid_size) * grid_size + self.parent().gutter_size)

            # Check for collisions
            for square in self.parent().squares:
                if square is not self and square.geometry().contains(new_pos, True):
                    return  # Don't move if a collision is detected

            # Check for screen boundaries
            if new_pos.x() < 0 or new_pos.y() < 0 or new_pos.x() + self.width() > QApplication.desktop().width() or new_pos.y() + self.height() > QApplication.desktop().height():
                return  # Don't move if it would go off-screen

            self.move(new_pos)


    def mouseDoubleClickEvent(self, event):
        webbrowser.open(self.url)

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.highlighted:
            painter.fillRect(self.rect(), QBrush(QColor(100, 100, 100, 50)))


app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())