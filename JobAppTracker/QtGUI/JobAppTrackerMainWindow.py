import os.path

from PyQt6.QtCore import QSettings, QStandardPaths, pyqtSlot
from PyQt6.QtWidgets import (QMainWindow, QFileDialog, QTableWidgetItem,
                             QHeaderView)

from Data.Application import Application, JobTypes, Status
from JobAppTracker.QtGUI.ui.ui_JobAppTrackerMainWindow import \
    Ui_JobAppTrackerMainWindow
from QtGUI.AppInfoScreen import AppInfoDialog
from SQLite.ApplicationQueries import (get_applications,
                                       get_interview_count_for_application)
from SQLite.Initializer import init_data_file
from SQLite.Verifier import verify_sqlite, check_job_app_sqlite
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

    currentFile = None
    """
    Path to the currently opened file
    """

    tableData = []
    """
    An internal list of applications displayed on the table
    """

    def __init__(self):
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

        # Create the application info screen and link it to each application
        # and the new application button
        self.appInfoScreen = AppInfoDialog()

        self.ui.appTableWidget.cellDoubleClicked.connect(
            lambda row, _: self.appInfoScreen.editApplication(self.tableData[row])
        )
        self.ui.addAppButton.clicked.connect(self.appInfoScreen.newApplication)

        # Connect the menu actions to their functions
        self.ui.actionOpen.triggered.connect(self.openFileAction)
        self.ui.actionNew.triggered.connect(self.newFileAction)

        # Allow app info screen to trigger a data reload
        self.appInfoScreen.table_updated.connect(self.load_data)

    def changeOpenFile(self, new_file_path):
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

    def setTitleStatus(self, title_status):
        """
        Set the window title based on what file is currently open.
        :param title_status: The name of the file that is opened, or a default
            message if no file is opened.
        :return:
        """
        self.setWindowTitle(f"{TITLE_BASE} - {title_status}")

    def handleStartLocationLoad(self):
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
    def load_data(self):
        """
        Loads data from a data file into the main table and the data list.
        :return:
        """

        self.tableData.clear()
        for row in get_applications(self.currentFile):
            row_data = dict(row)
            app_data = Application(int(row_data["app_id"]),
                                   row_data["company"],
                                   row_data["title"],
                                   row_data["application_date"],
                                   row_data["latest_follow_up"],
                                   JobTypes(row_data["type"]),
                                   row_data["location"],
                                   row_data["applied_at"],
                                   row_data["contact"],
                                   row_data["materials_sent"],
                                   row_data["salary"],
                                   Status(row_data["status"]),
                                   row_data["comments"])
            self.tableData.append(app_data)

        self.ui.appTableWidget.clearContents()
        self.ui.appTableWidget.setRowCount(len(self.tableData))
        for row, app in enumerate(self.tableData):
            self.ui.appTableWidget.setItem(row, 0, QTableWidgetItem(app.company))
            self.ui.appTableWidget.setItem(row, 1, QTableWidgetItem(app.title))
            self.ui.appTableWidget.setItem(row, 2, QTableWidgetItem(app.applied_on.strftime("%b %d, %Y")))
            if app.followed_up is not None:
                self.ui.appTableWidget.setItem(row, 3, QTableWidgetItem(app.followed_up.strftime("%b %d, %Y")))
            self.ui.appTableWidget.setItem(row, 4, QTableWidgetItem(
                str(get_interview_count_for_application(self.currentFile, app.app_id))
            ))
            self.ui.appTableWidget.setItem(row, 5, QTableWidgetItem(str(app.job_type)))
            self.ui.appTableWidget.setItem(row, 6, QTableWidgetItem(app.location))
            self.ui.appTableWidget.setItem(row, 7, QTableWidgetItem(app.website))
            self.ui.appTableWidget.setItem(row, 8, QTableWidgetItem(app.contact))
            self.ui.appTableWidget.setItem(row, 9, QTableWidgetItem(app.materials))
            self.ui.appTableWidget.setItem(row, 10, QTableWidgetItem(app.salary))
            self.ui.appTableWidget.setItem(row, 11, QTableWidgetItem(str(app.status)))
            self.ui.appTableWidget.setItem(row, 12, QTableWidgetItem(app.comments))
            self.ui.appTableWidget.setItem(row, 13, QTableWidgetItem(str(app.days_pending)))

        self.ui.appTableWidget.resizeColumnsToContents()
        for col_idx in range(self.ui.appTableWidget.columnCount()):
            if self.ui.appTableWidget.columnWidth(col_idx) < 100:
                self.ui.appTableWidget.setColumnWidth(col_idx, 100)

    @pyqtSlot()
    def openFileAction(self):
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

        if not verify_sqlite(fileName):
            showWarningMessage("Invalid file type")
            return

        if not check_job_app_sqlite(fileName):
            showWarningMessage("SQLite file missing required tables")
            return

        self.changeOpenFile(fileName)

    @pyqtSlot()
    def newFileAction(self):
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
