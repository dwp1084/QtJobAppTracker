import os.path

from PyQt6.QtCore import QSettings, QStandardPaths, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem

from Data.Application import Application, Status
from JobAppTracker.QtGUI.ui.ui_JobAppTrackerMainWindow import \
    Ui_JobAppTrackerMainWindow
from QtGUI.AppInfoScreen import AppInfoDialog
from SQLite.ApplicationQueries import (get_interview_count_for_application,
                                       get_applications, ghost_prediction)
from SQLite.Initializer import init_data_file
from SQLite.Utils import DataFileSQLRunner
from errorDialog import showWarningMessage

# Base title for the main window
TITLE_BASE = "Job Application Tracker"

# When there is no file loaded, this will appear in place of a file name
NO_FILE_LOADED = "No file loaded"

# Name of the app settings file
CONFIG_FILE_NAME = "jobapptrackerconfig.ini"

# Column indices - careful if these change
STATUS_COL = 11
DAYS_PASSED_COL = 13


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

    hiddenCount: int = 0

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

        # Setup show inactive
        show_inactive = self.settings.value(
            "opts/showInactiveApplications", defaultValue=True, type=bool
        )

        self.ui.actionInactive_Applications.toggled.connect(self.toggle_inactive)
        self.ui.actionInactive_Applications.setChecked(show_inactive)

        if self.settings.value("file/currentFile") is not None:
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

        # Hide days passed column option
        show_days_passed = self.settings.value(
            "opts/showDaysPassed", defaultValue=True, type=bool
        )

        self.ui.actionDays_Since_Application.toggled.connect(
            lambda checked: self.toggleDaysPassedColumn(DAYS_PASSED_COL, checked)
        )

        self.ui.actionDays_Since_Application.setChecked(show_days_passed)

    def toggleDaysPassedColumn(self, col_idx: int, show_col: bool) -> None:
        """
        Hides or shows a column in the table based on its index.
        :param col_idx: Column's index
        :param show_col: True if column should be shown, False if hidden
        :return:
        """
        if show_col:
            self.ui.appTableWidget.showColumn(col_idx)
        else:
            self.ui.appTableWidget.hideColumn(col_idx)

        self.settings.setValue("opts/showDaysPassed", show_col)

    @pyqtSlot(bool)
    def toggle_inactive(self, show_inactive: bool) -> None:
        """
        Hides or shows applications in the table that are inactive (rejected or
        likely ghosted)
        :param show_inactive: True if inactive application should be shown, False
            if hidden
        :return:
        """
        self.hiddenCount = 0

        if show_inactive:
            for row in range(self.ui.appTableWidget.rowCount()):
                self.ui.appTableWidget.setRowHidden(row, False)
        else:
            for row, app in enumerate(self.tableData):
                app_status = ghost_prediction(
                    self.currentFile,
                    self.tableData[row]
                )

                if app_status in {Status.LIKELY_GHOSTED, Status.REJECTED}:
                    self.ui.appTableWidget.setRowHidden(row, True)
                    self.hiddenCount += 1
                else:
                    self.ui.appTableWidget.setRowHidden(row, False)

        self.settings.setValue("opts/showInactiveApplications", show_inactive)

        self.update_app_count()

    def update_app_count(self) -> None:
        """
        Updates the application count label on the screen based on the number
        of applications loaded and the number of rows hidden.
        :return:
        """
        match self.hiddenCount:
            case 0:
                label_text = str(len(self.tableData))
            case 1:
                label_text = f"{len(self.tableData)} (1 application hidden)"
            case _:
                label_text = f"{len(self.tableData)} ({self.hiddenCount} applications hidden)"

        self.ui.appCountLabel.setText(label_text)

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
        if self.settings.value("file/startLocation") is None:
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
                str(ghost_prediction(self.currentFile, app)),
                app.comments,
                str(app.days_pending)
            ]

            for col, item in enumerate(row_contents):
                self.ui.appTableWidget.setItem(row, col, QTableWidgetItem(item))

        self.ui.appTableWidget.resizeColumnsToContents()
        for col_idx in range(self.ui.appTableWidget.columnCount()):
            if self.ui.appTableWidget.columnWidth(col_idx) < 100:
                self.ui.appTableWidget.setColumnWidth(col_idx, 100)
            elif self.ui.appTableWidget.columnWidth(col_idx) > 600:
                self.ui.appTableWidget.setColumnWidth(col_idx, 600)

        self.toggle_inactive(self.ui.actionInactive_Applications.isChecked())

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
