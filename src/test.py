from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
)


from utils import ConfirmationDialog
from utils import create_button

if __name__ == "__main__":
    app = QApplication([])
    window = QWidget()
    window.setLayout(layout := QVBoxLayout())
    txt = "abcdefghijklmnopqrstuvwxyz"
    confirmation = ConfirmationDialog(text=txt)
    confirmation.exec_()
    print(confirmation.accepted)

    style_sheet = """
            QPushButton {
                border: none;
                icon: url(icons/toggle.png);
                background-color: ffffff;
            }
        """

    # button = create_button("toggle.png",
    #                        [58, 22],
    #                        [0, 0],
    #                        style_sheet,
    #                        lambda x: print("pressed"),
    #                        [58, 22])
    # layout.addWidget(button)

    window.show()
    app.exec_()