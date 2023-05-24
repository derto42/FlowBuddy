import sys
from typing import Callable

from pynput import keyboard
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon

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

    if any(x.lower() == "-showui" for x in app.arguments()):
        QApplication.instance().processEvents()
        window.update()
        window.show()

    show_tray_icon(app, window.window_toggle_signal.emit)

    def on_hotkey_press():
        window.window_toggle_signal.emit()

    hotkey_listener = keyboard.GlobalHotKeys({'<ctrl>+`': on_hotkey_press})
    hotkey_listener.start()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
