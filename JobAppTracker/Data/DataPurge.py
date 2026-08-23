import datetime

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

from Data.Application import Status
from QtGUI.AppTableModel import AppTableModel
from SQLite.ApplicationQueries import ghost_prediction, update_application, vacuum_db


class DataPurge(QObject):
    tableUpdated = pyqtSignal()

    def __init__(self, dataModel: AppTableModel, currentFile: str):
        super().__init__()
        self.dataModel = dataModel
        self.currentFile = currentFile

    def set_current_file(self, newOpenFile: str):
        self.currentFile = newOpenFile

    @pyqtSlot(datetime.date, set)
    def purge_job_descriptions(self, before_date: datetime.date, whitelist: set[Status]):
        for app in self.dataModel:
            if (app.applied_on <= before_date
                and ghost_prediction(self.currentFile, app) not in whitelist):
                app.description = ""
                update_application(self.currentFile, app)

        vacuum_db(self.currentFile)

        self.tableUpdated.emit()