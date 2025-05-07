import sys

from PyQt6.QtWidgets import QApplication, QMessageBox

from JobAppTracker.QtGUI.JobAppTrackerMainWindow import JobAppTrackerMainWindow
from SQLite.Initializer import init_autocomplete_file
from errorDialog import showErrorMessage

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JobAppTrackerMainWindow()

    try:
        init_autocomplete_file()
    except IOError as ioe:
        showErrorMessage(str(ioe), "Error", QMessageBox.Icon.Critical)
        sys.exit(-1)

    window.show()

    sys.exit(app.exec())
