import sys
import traceback

from PyQt6.QtWidgets import QApplication

from QtGUI.JobAppTrackerMainWindow import JobAppTrackerMainWindow
from SQLite.Initializer import init_autocomplete_file
from errorDialog import showErrorMessage

def qt_excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    sys.exit(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JobAppTrackerMainWindow()

    try:
        init_autocomplete_file()
    except IOError as ioe:
        showErrorMessage(str(ioe))
        sys.exit(-1)

    sys.excepthook = qt_excepthook

    window.show()

    sys.exit(app.exec())
