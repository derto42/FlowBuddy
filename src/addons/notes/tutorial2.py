import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
    QAction,
    QToolBar,
)
class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.setWindowTitle("My Awesome App")

        label = QLabel("Hello!")
        label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(label)

        toolbar = QToolBar("My main toolbar")
        self.addToolBar(toolbar)

        button_action1 = QAction("Button 1", self)
        button_action1.setStatusTip("This is Button 1")
        button_action1.triggered.connect(self.onMyToolBarButtonClick1)
        button_action2 = QAction("Button 2", self)
        button_action2.setStatusTip("This is Button 2")
        button_action2.triggered.connect(self.onMyToolBarButtonClick2)
        toolbar.addAction(button_action1)
        toolbar.addAction(button_action2)

    def onMyToolBarButtonClick1(self, s):
        print("Button 1 click", s)
    def onMyToolBarButtonClick2(self, s):
        print("Button 2 click", s)

def main():
    app = QApplication(sys.argv)

    
    window = MainWindow()
    window.show()

    app.exec()

if __name__=='__main__':
    main()