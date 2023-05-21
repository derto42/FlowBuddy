from PyQt5.QtWidgets import QWidget, QApplication

from ui.settings.ui import SettingsUI

app = QApplication([])
win = SettingsUI()
win.show()

app.exec()