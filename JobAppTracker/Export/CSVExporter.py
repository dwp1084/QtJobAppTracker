import csv
from typing import Callable

import constants as c
from Data.Application import Application
from Export.BaseExporter import BaseExporter
from QtGUI.AppTableModel import AppTableModel
from SQLite.ApplicationQueries import (get_interview_count_for_application,
                                       ghost_prediction)


class CSVExporter(BaseExporter):
    """
    Exporter that creates a limited report of the table data in CSV format.
    """
    currentFile = ""

    def __init__(self):
        self.columns: list[tuple[str, Callable[[Application], str]]] = [
            (c.H_COMPANY, lambda app: app.company),
            (c.H_TITLE, lambda app: app.title),
            (c.H_APP_DATE, lambda app: app.applied_on.isoformat()),
            (c.H_FOLLOW_UP, lambda app: app.followed_up.isoformat() \
                if app.followed_up is not None else ""),
            (c.H_INTERVIEWS, lambda app: str(
                get_interview_count_for_application(self.currentFile,
                                                    app.app_id)
            )),
            (c.H_JOB_TYPE, lambda app: str(app.job_type)),
            (c.H_LOCATION, lambda app: app.location),
            (c.H_EXPERIENCE, lambda app: app.experience),
            (c.H_APP_SRC, lambda app: app.found_at),
            (c.H_APP_WEBSITE, lambda app: app.website),
            (c.H_CONTACT, lambda app: app.contact),
            (c.H_MATERIALS, lambda app: app.materials),
            (c.H_SALARY, lambda app: app.salary),
            (c.H_STATUS, lambda app: str(
                ghost_prediction(self.currentFile, app)
            )),
            (c.H_TTR, lambda app: app.time_to_rejection),
            (c.H_LINK, lambda app: app.link),
            (c.H_COMMENT, lambda app: app.comments),
            (c.H_PENDING, lambda app: str(app.days_pending))
        ]

    @property
    def window_title(self) -> str:
        return "CSV Export"

    @property
    def filter(self) -> str:
        return "CSV File (*.csv)"

    @property
    def save_dialog_title(self) -> str:
        return "Export as CSV"

    @property
    def ext(self) -> str:
        return "csv"

    def _export(self, db_file: str, save_path: str, data: AppTableModel) -> None:
        self.currentFile = db_file

        with open(save_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            current_row = []

            for (header, _) in self.columns:
                current_row.append(header)
            writer.writerow(current_row)
            current_row.clear()

            for app in data:
                for (_, expr) in self.columns:
                    current_row.append(expr(app))
                writer.writerow(current_row)
                current_row.clear()