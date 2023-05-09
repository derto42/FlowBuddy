import sys
from typing import Callable

import keyboard
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication,
    QMenu,
    QSystemTrayIcon,
)

import FileSystem as FS
from ui import MainWindow


TITLE = "FlowBuddy"


def show_tray_icon(parent: QApplication, activate_action: Callable):
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


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    # showing the window for first time to construct the window
    # (Avoid cunstruct from the thread, which does crashes)
    window.show()
    if all(x.lower() != '-showui' for x in app.arguments()):
        window.hide()

    toggle_window = lambda: window.show() if window.isHidden() else window.hide()

    show_tray_icon(app, toggle_window)
    keyboard.add_hotkey("ctrl+`", toggle_window)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
