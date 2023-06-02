test_custom_buttons = False
base_window = False
base_dialog = False
group_node = False
main_window = False
logo = True


def _custom_buttons_():
    layout.addWidget(RedButton())
    layout.addWidget(YelButton())
    layout.addWidget(GrnButton())
    layout.addWidget(RedButton(button_type="long"))
    layout.addWidget(YelButton(button_type="long"))
    layout.addWidget(GrnButton(button_type="long"))
    layout.addWidget(TextButton())
    layout.addWidget(TextButton(text="Click Me!"))

def _base_window_():
    window = BaseWindow()
    window.setLayout(layout:=QVBoxLayout())
    layout.addWidget(RedButton())
    layout.addWidget(YelButton())
    layout.addWidget(GrnButton())
    layout.addWidget(RedButton(button_type="long"))
    layout.addWidget(YelButton(button_type="long"))
    layout.addWidget(GrnButton(button_type="long"))
    layout.addWidget(TextButton())
    layout.addWidget(TextButton(text="Click Me!"))
    window.show()
    app.exec()
    
def _base_dialog_():
    add_group = GroupDialog()
    add_group.exec()
    print(gres:=add_group.result())
    
    add_task = TaskDialog()
    print(tres:=add_task.exec())
    
    edit_group = GroupDialog()
    edit_group.for_edit(gres)
    print(edit_group.exec())
    
    edit_task = TaskDialog()
    edit_task.for_edit(*tres)
    print(edit_task.exec())
    
    app.exec()

def _group_node_():
    win.setStyleSheet("background : '#838383'")
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.addWidget(GroupNode("Group 1"))
    layout.addWidget(GroupNode("Group 2"))
    layout.addWidget(GroupNode("Group 3"))

def _main_window_():
    window = MainWindow()
    window.show()
    app.exec()
    
def _logo_():
    window = Buddy()
    window.show()
    app.exec()

from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
from ui.custom_button import *
from ui.base_window import *
from ui.dialog import *
from addons.shortcuts.shortcuts import *
from ui.logo import *

app = QApplication([])
win = QWidget()
win.setLayout(layout:=QVBoxLayout())

if test_custom_buttons: _custom_buttons_()
if base_window: _base_window_()
if base_dialog: _base_dialog_()
if group_node: _group_node_()
if main_window: _main_window_()
if logo: _logo_()

win.show()
app.exec()