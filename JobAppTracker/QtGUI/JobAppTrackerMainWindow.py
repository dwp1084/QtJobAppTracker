import os.path

from PyQt6.QtCore import QSettings, QStandardPaths, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem

from Data.Application import Application
from JobAppTracker.QtGUI.ui.ui_JobAppTrackerMainWindow import \
    Ui_JobAppTrackerMainWindow
from QtGUI.AppInfoScreen import AppInfoDialog
from SQLite.ApplicationQueries import (get_interview_count_for_application,
                                       get_applications)
from SQLite.Initializer import init_data_file
from SQLite.Utils import DataFileSQLRunner
from errorDialog import showWarningMessage

# Base title for the main window
TITLE_BASE = "Job Application Tracker"

# When there is no file loaded, this will appear in place of a file name
NO_FILE_LOADED = "No file loaded"

# Name of the app settings file
CONFIG_FILE_NAME = "jobapptrackerconfig.ini"


class JobAppTrackerMainWindow(QMainWindow):
    """
    Main window for the job application tracker, which lets users open a data
    file into a table to view or modify.
    """

    currentFile: str | None = None
    """
    Path to the currently opened file
    """

    tableData: list[Application] = []
    """
    An internal list of applications displayed on the table
    """

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_JobAppTrackerMainWindow()
        self.ui.setupUi(self)

        # Create and load the settings config file
        app_data = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppDataLocation
        )
        self.settings = QSettings(os.path.join(app_data, CONFIG_FILE_NAME),
                                  QSettings.Format.IniFormat
                                  )

        # Create the application info screen
        self.appInfoScreen = AppInfoDialog()

        # Set window title and load the previously loaded file if possible
        titleStatus = NO_FILE_LOADED

        if self.settings.value("file/currentFile"):
            filename = self.settings.value("file/currentFile")
            if not os.path.exists(filename):
                showWarningMessage(f"Last open file {filename} is missing")
            else:
                titleStatus = os.path.basename(filename)
                self.changeOpenFile(filename)

        self.setTitleStatus(titleStatus)

        # Link application info screen to the application view
        self.ui.appTableWidget.cellDoubleClicked.connect(
            lambda row, _: self.appInfoScreen.editApplication(self.tableData[row])
        )
        self.ui.addAppButton.clicked.connect(self.appInfoScreen.newApplication)

        # Connect the menu actions to their functions
        self.ui.actionOpen.triggered.connect(self.openFileAction)
        self.ui.actionNew.triggered.connect(self.newFileAction)

        # Allow app info screen to trigger a data reload
        self.appInfoScreen.table_updated.connect(self.load_data)

    def changeOpenFile(self, new_file_path: str) -> None:
        """
        Change the data file that is currently open and load in the new data.
        :param new_file_path: Path to the new data file
        :return:
        """
        self.setTitleStatus(os.path.basename(new_file_path))
        self.currentFile = new_file_path
        self.appInfoScreen.setCurrentFile(new_file_path)
        self.settings.setValue("file/currentFile", self.currentFile)
        self.load_data()

    def setTitleStatus(self, title_status: str) -> None:
        """
        Set the window title based on what file is currently open.
        :param title_status: The name of the file that is opened, or a default
            message if no file is opened.
        :return:
        """
        self.setWindowTitle(f"{TITLE_BASE} - {title_status}")

    def handleStartLocationLoad(self) -> None:
        """
        If a custom starting data file location hasn't been defined, creates a
        folder in the Documents folder for the application and sets that to the
        starting data file location.
        :return:
        """
        if not self.settings.value("file/startLocation"):
            documentsFolder = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
            startFolder = os.path.join(documentsFolder, "JobAppTracker")
            if not os.path.exists(startFolder):
                os.mkdir(startFolder)
            self.settings.setValue("file/startLocation", startFolder)

    @pyqtSlot()
    def load_data(self) -> None:
        """
        Loads data from a data file into the main table and the data list.
        :return:
        """
        self.tableData = get_applications(self.currentFile)

        self.ui.appTableWidget.clearContents()
        self.ui.appTableWidget.setRowCount(len(self.tableData))
        for row, app in enumerate(self.tableData):
            followed_up = app.followed_up.strftime("%b %d, %Y") \
                if app.followed_up is not None else ""

            row_contents = [
                app.company,
                app.title,
                app.applied_on.strftime("%b %d, %Y"),
                followed_up,
                str(
                    get_interview_count_for_application(self.currentFile,
                                                        app.app_id)
                ),
                str(app.job_type),
                app.location,
                app.website,
                app.contact,
                app.materials,
                app.salary,
                str(app.status),
                app.comments,
                str(app.days_pending)
            ]

            for col, item in enumerate(row_contents):
                self.ui.appTableWidget.setItem(row, col, QTableWidgetItem(item))

        self.ui.appTableWidget.resizeColumnsToContents()
        for col_idx in range(self.ui.appTableWidget.columnCount()):
            if self.ui.appTableWidget.columnWidth(col_idx) < 100:
                self.ui.appTableWidget.setColumnWidth(col_idx, 100)

    @pyqtSlot()
    def openFileAction(self) -> None:
        """
        Triggers a file opening dialog. Then, if a valid file is selected, it
        loads the new file into the program.
        :return:
        """

        self.handleStartLocationLoad()

        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open Job App Tracker",
            self.settings.value("file/startLocation"),
            "SQLite database (*.sqlite *.sqlite3 *.db *.db3);;All Files (*)"
        )

        if fileName == '':
            return

        try:
            verify_file = DataFileSQLRunner(fileName)
        except IOError:
            showWarningMessage("Invalid file type")
            return

        if not verify_file.is_valid_format:
            showWarningMessage("SQLite file missing required tables")
            return

        self.changeOpenFile(fileName)

    @pyqtSlot()
    def newFileAction(self) -> None:
        """
        Triggers a new file creation dialog. If the user decides to create a
        file, and it doesn't already exist, it creates and initializes the file
        before opening it.
        :return:
        """
        self.handleStartLocationLoad()

        fileName, _ = QFileDialog.getSaveFileName(
            self,
            "Create new Job App Tracker",
            self.settings.value("file/startLocation"),
            "SQLite database (*.sqlite *.sqlite3 *.db *.db3)"
        )

        if fileName == '':
            return

        if os.path.exists(fileName):
            showWarningMessage(f"Cannot overwrite existing file {fileName}")
            return

        init_data_file(fileName)

        self.changeOpenFile(fileName)
