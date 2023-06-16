import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget,QVBoxLayout,QHBoxLayout,QTextEdit
from PyQt5.QtGui import QPalette, QColor

class Color(QTextEdit):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("My App")
        mywidget=Color(RED)
        layout1 = QHBoxLayout()
        layout1.setContentsMargins(0,0,0,0)
        layout1.setSpacing(24)
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        layout2.addWidget(mywidget)
        layout2.addWidget(Color('yello'))
        layout2.addWidget(Color('purple'))
        layout1.addLayout(layout2)

        layout1.addWidget(Color('green'))
        layout3.addWidget(Color('red'))
        layout3.addWidget(Color('purple'))
        layout1.addLayout(layout3)

        widget=QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)

RED='red'
def main():
    app = QApplication(sys.argv)

    
    window = MainWindow()
    window.show()

    app.exec()

if __name__=='__main__':
    main()