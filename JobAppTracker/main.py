import faulthandler
import logging.config
import sys
import traceback

import yaml
from PyQt6.QtWidgets import QApplication

from QtGUI.JobAppTrackerMainWindow import JobAppTrackerMainWindow
from SQLite.Initializer import init_autocomplete_file
from constants import CURRENT_APP_VERSION
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

    logging.getLogger(__name__).error(f"Exception occurred:\n{tb_str}")


if __name__ == '__main__':
    with open("log_config.yml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    logging.config.dictConfig(config)
    logging.getLogger(__name__).info(
        f"Logging initialized on JAT v{CURRENT_APP_VERSION}"
    )

    logging.info("Started")
    app = QApplication(sys.argv)
    app.setApplicationName("Job Application Tracker")
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
