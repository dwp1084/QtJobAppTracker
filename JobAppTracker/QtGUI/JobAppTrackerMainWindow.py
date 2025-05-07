import os.path

from PyQt6.QtCore import QSettings, QStandardPaths, pyqtSlot
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog

from JobAppTracker.QtGUI.ui.ui_JobAppTrackerMainWindow import Ui_JobAppTrackerMainWindow
from QtGUI.AppInfoScreen import AppInfoDialog
from SQLite.Verifier import verify_sqlite, check_job_app_sqlite
from errorDialog import showErrorMessage

TITLE_BASE = "Job Application Tracker"
NO_FILE_LOADED = "No file loaded"
CONFIG_FILE_NAME = "jobapptrackerconfig.ini"


class JobAppTrackerMainWindow(QMainWindow):
    currentFile = None

    def __init__(self):
        super().__init__()
        self.ui = Ui_JobAppTrackerMainWindow()
        self.ui.setupUi(self)

        app_data = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        self.settings = QSettings(os.path.join(app_data, CONFIG_FILE_NAME), QSettings.Format.IniFormat)

        titleStatus = NO_FILE_LOADED

        if self.settings.value("file/currentFile"):
            filename = self.settings.value("file/currentFile")
            if not os.path.exists("file/currentFile"):
                showErrorMessage(f"Last open file {filename} is missing", "Warning", QMessageBox.Icon.Warning)
            else:
                titleStatus = os.path.basename(filename)
                self.currentFile = filename

        self.setTitleStatus(titleStatus)

        self.appInfoScreen = AppInfoDialog()

        self.ui.appTableWidget.cellDoubleClicked.connect(lambda: print("Yeet"))
        self.ui.addAppButton.clicked.connect(self.appInfoScreen.exec)

        self.ui.actionOpen.triggered.connect(self.openFileAction)

    def setTitleStatus(self, title_status):
        self.setWindowTitle(f"{TITLE_BASE} - {title_status}")

    @pyqtSlot()
    def openFileAction(self):
        if not self.settings.value("file/startLocation"):
            documentsFolder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            startFolder = os.path.join(documentsFolder, "JobAppTracker")
            if not os.path.exists(startFolder):
                os.mkdir(startFolder)
            self.settings.setValue("file/startLocation", startFolder)

        fileName = QFileDialog.getOpenFileName(self, "Open Job App Tracker",
                                               self.settings.value("file/startLocation"),
                                               "SQLite database (*.sqlite *.sqlite3 *.db *.db3);;All Files (*)")

        if fileName[0] == '':
            return

        if not verify_sqlite(fileName[0]):
            showErrorMessage("Invalid file type", "Warning", QMessageBox.Icon.Warning)
            return

        if not check_job_app_sqlite(fileName[0]):
            showErrorMessage("SQLite file missing required tables", "Warning", QMessageBox.Icon.Warning)
            return

        self.currentFile = fileName[0]
        self.setTitleStatus(os.path.basename(self.currentFile))
        self.settings.setValue("file/currentFile", self.currentFile)

