import os
from notes import JottingDownWindow, NoteTab
from PyQt5.QtCore import Qt
from ui.dialog import ConfirmationDialog




def test_delete_tab(qtbot, tmpdir):
    # Create a temporary directory for testing
    temp_dir = tmpdir.mkdir("notes")

    # Create a test file in the temporary directory
    test_file = temp_dir.join("test.txt")
    test_file.write("Test content")

    # Create the JottingDownWindow instance
    window = JottingDownWindow()
    window.notes_folder = str(temp_dir)
    window.tab_widget.addTab(NoteTab(str(test_file)), "test.txt")

    # Add the window to the QtBot for interaction
    qtbot.addWidget(window)

    # Mock the QMessageBox.question method to always return QMessageBox.Yes
    def mock_question(_, __, ___, ____,  default_button):
        dialog = ConfirmationDialog("Delete tab test.txt?")
        return True

    ConfirmationDialog.question = mock_question

    # Simulate the delete_tab action
    with qtbot.waitSignal(window.tab_widget.tabCloseRequested):
        # Get the delete button of the tab
        delete_button = window.tab_widget.tabBar().tabButton(0, 2)
        qtbot.mouseClick(delete_button, Qt.LeftButton)

    # Verify that the tab is removed
    assert window.tab_widget.count() == 0

    # Verify that the file is deleted
    assert not os.path.exists(str(test_file))


