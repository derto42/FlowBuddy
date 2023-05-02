import os
import sys
import keyboard
import subprocess
from time import sleep
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QThread

class ProcessThread(QThread):
    def __init__(self):
        super(ProcessThread, self).__init__()
        self.process = None

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(current_dir, "GraphicView.pyw")


        while not self.isInterruptionRequested():
            # Wait for the '`' key to be pressed
            keyboard.wait("`")

            # Check if Ctrl is not being held down
            if not keyboard.is_pressed("ctrl"):

                # If the process is not running, start it
                if self.process is None or self.process.poll() is not None:
                    self.process = subprocess.Popen(["pythonw", script_path], creationflags=subprocess.CREATE_NO_WINDOW)


                # If the process is running, terminate it and set it to None
                else:
                    self.process.terminate()
                    self.process = None

            sleep(0.1)

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(current_dir, "icon.png")

    app = QApplication([])
    tray_icon = QSystemTrayIcon(QIcon(icon_path), parent=app)
    
    # Create a menu for the tray icon
    menu = QMenu()

    # Create a "Quit" action
    quit_action = QAction("Quit")
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    # Set the context menu and show the tray icon
    tray_icon.setContextMenu(menu)
    tray_icon.show()

    # Create and start the process thread
    process_thread = ProcessThread()
    app.aboutToQuit.connect(process_thread.requestInterruption)
    process_thread.start()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
