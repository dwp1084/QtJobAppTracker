import csv
from typing import Callable

from Data.Application import Application
from Export.BaseExporter import BaseExporter

import headers as h
from SQLite.ApplicationQueries import (get_interview_count_for_application,
                                       ghost_prediction)


class CSVExporter(BaseExporter):
    """
    Exporter that creates a limited report of the table data in CSV format.
    """
    currentFile = ""

    def __init__(self):
        self.columns: list[tuple[str, Callable[[Application], str]]] = [
            (h.H_COMPANY, lambda app: app.company),
            (h.H_TITLE, lambda app: app.title),
            (h.H_APP_DATE, lambda app: app.applied_on.isoformat()),
            (h.H_FOLLOW_UP, lambda app: app.followed_up.isoformat() \
                if app.followed_up is not None else ""),
            (h.H_INTERVIEWS, lambda app: str(
                get_interview_count_for_application(self.currentFile,
                                                    app.app_id)
            )),
            (h.H_JOB_TYPE, lambda app: str(app.job_type)),
            (h.H_LOCATION, lambda app: app.location),
            (h.H_APP_SRC, lambda app: app.found_at),
            (h.H_APP_WEBSITE, lambda app: app.website),
            (h.H_CONTACT, lambda app: app.contact),
            (h.H_MATERIALS, lambda app: app.materials),
            (h.H_SALARY, lambda app: app.salary),
            (h.H_STATUS, lambda app: str(
                ghost_prediction(self.currentFile, app)
            )),
            (h.H_COMMENT, lambda app: app.comments),
            (h.H_PENDING, lambda app: str(app.days_pending))
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

    def _export(self, db_file: str, save_path: str, data: list[Application]) -> None:
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