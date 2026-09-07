import datetime
import os.path

from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot

from Data.Application import Status
from QtGUI.AppTableModel import AppTableModel
from QtGUI.QtUtils import readable_data_size, strip_html
from SQLite.ApplicationQueries import ghost_prediction, update_application, vacuum_db
from errorDialog import showInfoMessage


class DataPurge(QObject):
    tableUpdated = pyqtSignal()

    def __init__(self, dataModel: AppTableModel, currentFile: str):
        super().__init__()
        self.dataModel = dataModel
        self.currentFile = currentFile

    def set_current_file(self, newOpenFile: str):
        self.currentFile = newOpenFile

    @staticmethod
    def purge_success_msg(data_type: str,
                          count: int,
                          bytes_saved: int) -> None:
        readable_bytes_saved = readable_data_size(bytes_saved)
        showInfoMessage("Success",
                        f"Successfully purged {count} {data_type}.\n" +
                        f"Data freed: {readable_bytes_saved}"
                        )

    @pyqtSlot(datetime.date, set)
    def purge_job_descriptions(self, before_date: datetime.date, whitelist: set[Status]):
        purge_count = 0
        for app in self.dataModel:
            if (app.applied_on <= before_date
                and ghost_prediction(self.currentFile, app) not in whitelist):
                app.description = ""
                update_application(self.currentFile, app)
                purge_count += 1

        original_size = os.path.getsize(self.currentFile)
        vacuum_db(self.currentFile)
        end_size = os.path.getsize(self.currentFile)

        bytes_saved = original_size - end_size

        self.purge_success_msg("job descriptions", purge_count, bytes_saved)
        self.tableUpdated.emit()

    @pyqtSlot(datetime.date, set)
    def purge_job_desc_formats(self, before_date: datetime.date, whitelist: set[Status]):
        purge_count = 0
        for app in self.dataModel:
            if (app.applied_on <= before_date
                    and ghost_prediction(self.currentFile, app) not in whitelist):
                app.description = strip_html(app.description)
                update_application(self.currentFile, app)
                purge_count += 1

        original_size = os.path.getsize(self.currentFile)
        vacuum_db(self.currentFile)
        end_size = os.path.getsize(self.currentFile)

        bytes_saved = original_size - end_size

        self.purge_success_msg("job description formats", purge_count, bytes_saved)
        self.tableUpdated.emit()
