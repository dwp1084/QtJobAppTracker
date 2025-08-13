import os.path

from PyQt6.QtCore import QSettings, QStandardPaths, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QTableWidgetItem, QHeaderView

from Data.Application import Application, JobTypes, Status
from JobAppTracker.QtGUI.ui.ui_JobAppTrackerMainWindow import Ui_JobAppTrackerMainWindow
from QtGUI.AppInfoScreen import AppInfoDialog
from SQLite.ApplicationQueries import get_applications, get_interview_count_for_application
from SQLite.Initializer import init_data_file
from SQLite.Verifier import verify_sqlite, check_job_app_sqlite
from errorDialog import showWarningMessage

TITLE_BASE = "Job Application Tracker"
NO_FILE_LOADED = "No file loaded"
CONFIG_FILE_NAME = "jobapptrackerconfig.ini"


class JobAppTrackerMainWindow(QMainWindow):
    currentFile = None
    tableData = []

    def __init__(self):
        super().__init__()
        self.ui = Ui_JobAppTrackerMainWindow()
        self.ui.setupUi(self)

        app_data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.settings = QSettings(os.path.join(app_data, CONFIG_FILE_NAME), QSettings.Format.IniFormat)

        titleStatus = NO_FILE_LOADED

        self.appInfoScreen = AppInfoDialog()

        if self.settings.value("file/currentFile"):
            filename = self.settings.value("file/currentFile")
            if not os.path.exists(filename):
                showWarningMessage(f"Last open file {filename} is missing")
            else:
                titleStatus = os.path.basename(filename)
                self.changeOpenFile(filename)

        self.setTitleStatus(titleStatus)

        self.ui.appTableWidget.cellDoubleClicked.connect(
            lambda row, _: self.appInfoScreen.editApplication(self.tableData[row])
        )
        self.ui.addAppButton.clicked.connect(self.appInfoScreen.newApplication)

        self.ui.actionOpen.triggered.connect(self.openFileAction)
        self.ui.actionNew.triggered.connect(self.newFileAction)

        self.appInfoScreen.table_updated.connect(self.load_data)

    def changeOpenFile(self, new_file_path):
        self.setTitleStatus(os.path.basename(new_file_path))
        self.currentFile = new_file_path
        self.appInfoScreen.setCurrentFile(new_file_path)
        self.settings.setValue("file/currentFile", self.currentFile)
        self.load_data()

    def setTitleStatus(self, title_status):
        self.setWindowTitle(f"{TITLE_BASE} - {title_status}")

    def handleStartLocationLoad(self):
        if not self.settings.value("file/startLocation"):
            documentsFolder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            startFolder = os.path.join(documentsFolder, "JobAppTracker")
            if not os.path.exists(startFolder):
                os.mkdir(startFolder)
            self.settings.setValue("file/startLocation", startFolder)

    @pyqtSlot()
    def load_data(self):
        # print(*(dict(row) for row in get_applications(self.currentFile)))

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
        self.handleStartLocationLoad()

        fileName, _ = QFileDialog.getOpenFileName(self, "Open Job App Tracker",
                                                  self.settings.value("file/startLocation"),
                                                  "SQLite database (*.sqlite *.sqlite3 *.db *.db3);;All Files (*)")

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
        self.handleStartLocationLoad()

        fileName, _ = QFileDialog.getSaveFileName(self, "Create new Job App Tracker",
                                                  self.settings.value("file/startLocation"),
                                                  "SQLite database (*.sqlite *.sqlite3 *.db *.db3)")

        if fileName == '':
            return

        if os.path.exists(fileName):
            showWarningMessage(f"Cannot overwrite existing file {fileName}")
            return

        init_data_file(fileName)

        self.changeOpenFile(fileName)
