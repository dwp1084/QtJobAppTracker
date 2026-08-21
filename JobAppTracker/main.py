import faulthandler
import sys
import traceback

from PyQt6.QtWidgets import QApplication

from QtGUI.JobAppTrackerMainWindow import JobAppTrackerMainWindow
from SQLite.Initializer import init_autocomplete_file
from errorDialog import showErrorMessage


def qt_excepthook(exc_type, value, tb):
    """
    Custom exception hook. Initially written to print out uncaught exceptions
    to the terminal, even when QT hides the traceback. Now, it also shows an
    error dialog with the traceback on it as well.
    :param exc_type: Exception type
    :param value: Exception value
    :param tb: Exception traceback
    :return:
    """
    traceback.print_exception(exc_type, value, tb)

    tb_str = "".join(traceback.format_exception(exc_type, value, tb))

    showErrorMessage(f"An uncaught exception occurred:\n{tb_str}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = JobAppTrackerMainWindow()

    try:
        init_autocomplete_file()
    except IOError as ioe:
        showErrorMessage(str(ioe))
        sys.exit(-1)

    sys.excepthook = qt_excepthook

    faulthandler.enable()

    window.show()

    sys.exit(app.exec())
