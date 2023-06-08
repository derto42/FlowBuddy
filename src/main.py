import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QSystemTrayIcon

import FileSystem as FS
from addon import AddOnBase, load_addons, add_ons
from launcher import MainWindow


def main():
    app = QApplication(sys.argv)

    tray_icon = AddOnBase.system_tray_icon = QSystemTrayIcon(QIcon(FS.icon("icon.png")))
    tray_icon.setToolTip("FlowBuddy")
    tray_icon.show()
    
    menu = QMenu()
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(app.quit)
    tray_icon.setContextMenu(menu)
    
    load_addons()
    
    widgets = MainWindow(add_ons)
    widgets.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
