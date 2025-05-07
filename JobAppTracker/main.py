import sys

from PyQt6.QtWidgets import QApplication

from JobAppTracker.QtGUI.JobAppTrackerMainWindow import JobAppTrackerMainWindow
from SQLite.Initializer import init_autocomplete_file

if __name__ == '__main__':

    init_autocomplete_file()

    app = QApplication(sys.argv)
    window = JobAppTrackerMainWindow()
    window.show()

    sys.exit(app.exec())
