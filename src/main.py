import sys
from typing import Callable


import keyboard
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon


import FileSystem as FS
from ui import MainWindow


"""It displays the title of the application"""

TITLE = "FlowBuddy"



def show_tray_icon(parent: QApplication, activate_action: Callable):

    """Here in the code below  Displays the tray icon along with tooltip of the 
        application
    Args:
        parent (QApplication): The parent application to which the tray icon belongs.
        activate_action (Callable): A callable function to be triggered when the tray 
        icon is activated.

    Returns:
        None
"""
    tray_icon = QSystemTrayIcon(QIcon(FS.icon("icon.png")), parent=parent)
    tray_icon.setToolTip(TITLE)
    tray_icon.activated.connect(
        lambda reason: activate_action()
        if reason != QSystemTrayIcon.ActivationReason.Context
        else None
    )
    tray_icon.show()

    menu = QMenu()
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(parent.quit)
    tray_icon.setContextMenu(menu)


"""This trigggers the main function of the application
    Args:
        None
        After the main function is executed, it runs  a series of events like 
            updating , showing and hiding the tray icon. adding a hotkey shortcut to 
            window"""


def main():

    """This trigggers the main function of the application
    Args:
        None
        After the main function is executed, it runs  a series of events like 
            updating , showing and hiding the tray icon. adding a hotkey shortcut to 
            window"""


    app = QApplication(sys.argv)

    window = MainWindow()

    if any(x.lower() == "-showui" for x in app.arguments()):
        QApplication.instance().processEvents()
        window.update()
        window.show()

        # QTimer.singleShot(10, window.window_toggle_signal.emit)

    show_tray_icon(app, window.window_toggle_signal.emit)
    keyboard.add_hotkey("ctrl+`", window.window_toggle_signal.emit)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
