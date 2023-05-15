import sys
import time
import webbrowser
from functools import partial
from typing import Callable

import subprocess
import keyboard
from PyQt5.QtCore import QObject, QThread, QProcess, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QLabel,
    QDialog,
    QWidget,
    QApplication,
    QMenu,
    QSystemTrayIcon,
)

import FileSystem as FS
import SaveFile as Save
from ui import MainWindow


TITLE = "FlowBuddy"

class KeyBindRequest(QDialog):
    def __init__(self, key_listener):
        super().__init__()

        self._key_listener = key_listener

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.btn = QPushButton('Select Keybind', self)
        self.done_btn = QPushButton('Done', self)
        self.label = QLabel('Press the "Select Keybind" button and then any key', self)

        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.done_btn)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.process = QProcess()
        self.btn.clicked.connect(self.runNodeScript)
        self.done_btn.clicked.connect(self.on_done)
        self.is_keybind_selected = False

    def keyPressEvent(self, event):
        if self.is_keybind_selected:
            modifiers = QApplication.keyboardModifiers()
            keybind = []
            if modifiers & Qt.ShiftModifier:
                keybind.append('Shift')
            if modifiers & Qt.ControlModifier:
                keybind.append('Ctrl')
            if modifiers & Qt.AltModifier:
                keybind.append('Alt')
            if modifiers & Qt.MetaModifier:
                keybind.append('Meta')
            keybind.append(QKeySequence(event.key()).toString())
            # Only display key combination when at least 2 keys are pressed
            if len(keybind) > 1:
                self.label.setText(' + '.join(keybind))
                self.is_keybind_selected = False
                self.btn.setEnabled(True)
                while self._key_listener.keys is None:
                    time.sleep(0.5)
                self._current_keys = self._key_listener.keys

    def runNodeScript(self):
        self.btn.setEnabled(False)  # Disable the button while waiting for key input
        self.label.setText('Press any key...')
        self.is_keybind_selected = True

    def on_done(self, event=None):
        self.label.setText('Keybind captured.')
        self.btn.setEnabled(True)
        key1, key2 = self._current_keys
        Save.setting("key_bind", [key1, key2])
        self.accept()


class ListenKey(QThread):
    def __init__(self, callback: Callable = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.callback = callback
        self.keys = None
    
    def run(self):
        getKeyBind_path = FS.abspath("getKeybind.js")
        js_process = subprocess.Popen(['node', getKeyBind_path], stdout=subprocess.PIPE)
        
        while True:
            time.sleep(0.2)
            line = js_process.stdout.readline().decode('utf-8').strip()
            rawcode1, rawcode2 = map(int, line.split(','))
            if self.callback is not None:
                self.callback(rawcode1, rawcode2)
            self.keys = (rawcode1, rawcode2)


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

    if any(x.lower() == '-showui' for x in app.arguments()):
        QApplication.instance().processEvents()
        window.update()
        window.show()
    
    
    key_listener = ListenKey(parent=window)
    key_listener.start()

    try:
        saved_code1, saved_code2 = Save.setting("key_bind")
    except Save.NotFound:
        key_bind_request = KeyBindRequest(key_listener)
        key_bind_request.exec()


    def key_press(rawcode1, rawcode2):
        saved_code1, saved_code2 = Save.setting("key_bind")
        if rawcode1 == saved_code1 and rawcode2 == saved_code2:
            window.window_toggle_signal.emit()
    
    key_listener.callback = key_press
    
    
    show_tray_icon(app, window.window_toggle_signal.emit)
    
    
    # keyboard.add_hotkey("ctrl+`", window.window_toggle_signal.emit)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
