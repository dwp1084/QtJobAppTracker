import datetime
import os.path

from PyQt6.QtCore import QSettings, QStandardPaths, pyqtSlot, QTimer
from PyQt6.QtGui import QAction, QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QFileDialog

import headers as h
from Data.Application import Application, Status
from Data.StatsData import StatsData
from Export.BaseExporter import BaseExporter
from Export.XLSXExporter import XLSXExporter
from QtGUI.AppInfoScreen import AppInfoDialog
from QtGUI.AppTableModel import AppTableModel
from QtGUI.StatsWindow import StatsWindow
from QtGUI.ui.ui_JobAppTrackerMainWindow import Ui_JobAppTrackerMainWindow
from SQLite.ApplicationQueries import (get_applications,
                                       ghost_prediction)
from SQLite.Initializer import init_data_file
from SQLite.StatsQueries import (get_total_ints,
                                 get_avg_apps_per_month,
                                 get_avg_ints_and_count)
from SQLite.Utils import DataFileSQLRunner
from errorDialog import showWarningMessage, showQuestionMessage

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

        # Create additional windows
        self.appInfoScreen = AppInfoDialog()
        self.statisticsWindow = StatsWindow()

        # Set window title and load the previously loaded file if possible
        titleStatus = NO_FILE_LOADED

        # Setup show inactive
        show_inactive = self.settings.value(
            "opts/showInactiveApplications", defaultValue=True, type=bool
        )

        self.ui.actionInactive_Applications.toggled.connect(self.toggle_inactive)
        self.ui.actionInactive_Applications.setChecked(show_inactive)

        self.tableModel = AppTableModel(self.tableData, self.currentFile)
        self.tableModel.modelReset.connect(self.scheduleAdjust)

        self.xlsxExporter = XLSXExporter()

        if self.settings.value("file/currentFile") is not None:
            filename = self.settings.value("file/currentFile")
            if not os.path.exists(filename):
                showWarningMessage(f"Last open file {filename} is missing")
            else:
                titleStatus = os.path.basename(filename)
                self.changeOpenFile(filename)

        self.setTitleStatus(titleStatus)

        # Set up table view
        self.ui.appTableView.setModel(self.tableModel)

        self.ui.appTableView.verticalHeader().hide()

        self.ui.appTableView.doubleClicked.connect(
            lambda index: self.appInfoScreen.editApplication(
                self.tableData[index.row()]
            )
        )

        self.ui.addAppButton.clicked.connect(self.appInfoScreen.newApplication)

        # Connect the menu actions to their functions
        self.ui.actionOpen.triggered.connect(self.openFileAction)
        self.ui.actionNew.triggered.connect(self.newFileAction)

        # Allow app info screen to trigger a data reload
        self.appInfoScreen.table_updated.connect(self.load_data)

        # Map columns with their respective config keys and UI action elements
        toggleable_columns: dict[str, tuple[QAction, str]] = {
            "opts/showDaysPassed": (
                self.ui.actionDays_Since_Application,
                h.H_PENDING
            ),
            "opts/showComments": (
                self.ui.actionComments,
                h.H_COMMENT
            ),
            "opts/showMaterialsSent": (
                self.ui.actionMaterials_Sent,
                h.H_MATERIALS
            ),
            "opts/showContactInfo": (
                self.ui.actionContact_Info,
                h.H_CONTACT
            )
        }

        # Load in settings and hide columns if necessary
        for key, (action, header) in toggleable_columns.items():
            self.load_hide_column_setting(key, action, header)

        self.ui.actionStatistics.triggered.connect(self.show_stats)

        self.ui.actionXLSXExport.triggered.connect(
            lambda: self.export_data(self.xlsxExporter)
        )

    def export_data(self, exporter: BaseExporter):
        current_date_str = datetime.date.today().isoformat()
        default_file_name = f"{current_date_str} Job Application Tracker Export.xlsx"
        default_save_location = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )

        default_path = os.path.join(default_save_location, default_file_name)

        fileName, _ = QFileDialog.getSaveFileName(
            self,
            exporter.save_dialog_title,
            default_path,
            exporter.filter
        )

        if fileName == "":
            return

        exporter.export(self.currentFile, fileName, self.tableData)

    @pyqtSlot()
    def show_stats(self) -> None:
        """
        Gathers statistics and shows the statistics window.
        :return:
        """

        # Do nothing if the window is already open
        if self.statisticsWindow.isVisible():
            return

        total_apps = len(self.tableData)
        total_num_interviews = get_total_ints(self.currentFile)
        jobs_given_ints, avg_ints_per_job = get_avg_ints_and_count(
            self.currentFile
        )
        avg_apps_per_month = get_avg_apps_per_month(self.currentFile)

        stats_data = StatsData(total_apps,
                               total_num_interviews,
                               avg_ints_per_job,
                               avg_apps_per_month,
                               jobs_given_ints)

        for app in self.tableData:
            match ghost_prediction(self.currentFile, app):
                case Status.PENDING | Status.INTERVIEW:
                    stats_data.pending += 1
                case Status.REJECTED:
                    stats_data.rejected += 1
                case Status.LIKELY_GHOSTED:
                    stats_data.ghosted += 1
                case _:
                    pass

        self.statisticsWindow.load_stats_and_show(stats_data)

    def load_hide_column_setting(self, key: str, action: QAction, header: str) -> None:
        """
        Loads a setting for a toggleable column and connects its associated
        action.
        :param key: Setting key
        :param action: Action UI element
        :param header: Associated column header
        :return:
        """
        show_col = self.settings.value(key, defaultValue=True, type=bool)
        action.toggled.connect(  # type: ignore
            lambda checked: self.toggleCol(header, key, checked)
        )

        action.setChecked(show_col)

    def toggleCol(self, header: str, key: str, show_col: bool) -> None:
        """
        Hides or shows a column in the table based on its index.
        :param header: Column's header
        :param key: Settings key
        :param show_col: True if column should be shown, False if hidden
        :return:
        """
        col_idx = self.tableModel.searchColIdx(header)
        if col_idx < 0:
            raise ValueError("Invalid column name provided.")

        if show_col:
            self.ui.appTableView.showColumn(col_idx)
        else:
            self.ui.appTableView.hideColumn(col_idx)

        self.scheduleAdjust()

        self.settings.setValue(key, show_col)

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
            for row in range(self.tableModel.rowCount()):
                self.ui.appTableView.setRowHidden(row, False)

        else:
            for row, app in enumerate(self.tableData):
                app_status = ghost_prediction(
                    self.currentFile,
                    self.tableData[row]
                )

                if app_status in {Status.LIKELY_GHOSTED, Status.REJECTED}:
                    self.ui.appTableView.setRowHidden(row, True)
                    self.hiddenCount += 1
                else:
                    self.ui.appTableView.setRowHidden(row, False)

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

        # Disable updates during the changing data process to remove flickering
        self.ui.appTableView.setUpdatesEnabled(False)
        self.tableModel.setCurrentFile(self.currentFile)
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

        self.tableModel.setModelData(self.tableData)

    @pyqtSlot()
    def scheduleAdjust(self) -> None:
        """
        Schedules an adjustment to the column size with a singleShot timer.
        :return:
        """
        QTimer.singleShot(0, self.adjustColumnSize)

    @pyqtSlot()
    def adjustColumnSize(self) -> None:
        """
        Adjusts column size to resize to content within minimum and maximum
        bounds. This shouldn't be called directly, rather have it called at the
        end of the event loop (using a singleShot timer)
        :return:
        """
        for col in range(self.tableModel.columnCount()):
            self.ui.appTableView.resizeColumnToContents(col)
            w = self.ui.appTableView.columnWidth(col)
            self.ui.appTableView.setColumnWidth(col, max(100, min(w, 400)))

        self.toggle_inactive(self.ui.actionInactive_Applications.isChecked())

        # Re-enable updates, triggering a repaint of the table all at once.
        self.ui.appTableView.setUpdatesEnabled(True)

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

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Overrides the close event for the main window to ensure all other
        windows are closed when the user wants to exit the application.
        :param event: Close event
        :return:
        """
        self.statisticsWindow.close()
        self.appInfoScreen.close()
        event.accept()
