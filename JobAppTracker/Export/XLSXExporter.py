from datetime import date
from typing import Callable, Any

from Data.Application import Application, Status
from Export.BaseExporter import BaseExporter

import xlsxwriter as xlw
import headers as h
from SQLite.ApplicationQueries import get_interview_count_for_application, ghost_prediction


class XLSXExporter(BaseExporter):
    currentFile = ""

    def __init__(self):
        self._columns: list[tuple[str, Callable[[Application], Any]]] = [
            (h.H_COMPANY, lambda app: app.company),
            (h.H_TITLE, lambda app: app.title),
            (h.H_APP_DATE, lambda app: app.applied_on),
            (h.H_FOLLOW_UP, lambda app: app.followed_up \
                if app.followed_up is not None else ""),
            (h.H_INTERVIEWS, lambda app:
                get_interview_count_for_application(self.currentFile,
                                                    app.app_id)
            ),
            (h.H_JOB_TYPE, lambda app: str(app.job_type)),
            (h.H_LOCATION, lambda app: app.location),
            (h.H_APP_SRC, lambda app: app.found_at),
            (h.H_APP_WEBSITE, lambda app: app.website),
            (h.H_CONTACT, lambda app: app.contact),
            (h.H_MATERIALS, lambda app: app.materials),
            (h.H_SALARY, lambda app: app.salary),
            (h.H_STATUS, lambda app: ghost_prediction(self.currentFile, app)),
            (h.H_COMMENT, lambda app: app.comments),
            (h.H_PENDING, lambda app: str(app.days_pending))
        ]

    @property
    def window_title(self) -> str:
        return "Excel Export"

    def setCurrentFile(self, currentFile):
        self.currentFile = currentFile

    def _export(self, data: list[Application]) -> str:
        with xlw.Workbook("Tempname.xlsx") as workbook:

            # Create cell formats
            bold = workbook.add_format({"bold": True})
            italic = workbook.add_format({"italic": True})
            date_format = workbook.add_format(
                {"num_format": "d mmm yyyy"}
            )
            red_cell = workbook.add_format({
                "fg_color": "red",
                "font_color": "white"})
            org_cell = workbook.add_format({
                "fg_color": "orange",
                "font_color": "white"})
            # yel_cell = workbook.add_format({"bg_color": "yellow"})
            mid_green_cell = workbook.add_format({"fg_color": "#93c47d"})

            main_worksheet = workbook.add_worksheet("Applications")

            note = f"""Exported from Job Application Tracker on {
                date.today().strftime('%B %d, %Y')
            }"""

            note_row = 0
            header_row = 2
            beginning_row = 3

            main_worksheet.write(note_row, 0, note, italic)

            for col, (header, _) in enumerate(self._columns):
                main_worksheet.write(header_row, col, header, bold)

            # Fill in data and format
            for row, app in enumerate(data):
                currentStatus = Status.PENDING
                for col, (_, expr) in enumerate(self._columns):
                    data = expr(app)
                    match data:
                        case date():
                            main_worksheet.write(row + beginning_row, col, data, date_format)
                        case Status.REJECTED:
                            main_worksheet.write(row + beginning_row, col, str(data), red_cell)
                            currentStatus = data
                        case Status.LIKELY_GHOSTED:
                            main_worksheet.write(row + beginning_row, col, str(data), org_cell)
                            currentStatus = data
                        case Status():
                            main_worksheet.write(row + beginning_row, col, str(data))
                            currentStatus = data
                        case _:
                            main_worksheet.write(row + beginning_row, col, data)

                # Match company cell color with app status color
                match currentStatus:
                    case Status.REJECTED:
                        main_worksheet.write(row + beginning_row,
                                             0,
                                             app.company,
                                             red_cell)
                    case Status.LIKELY_GHOSTED:
                        main_worksheet.write(row + beginning_row,
                                             0,
                                             app.company,
                                             org_cell)
                    case _:
                        pass

                # Color in other cells
                int_count = get_interview_count_for_application(self.currentFile,
                                                    app.app_id)
                if int_count > 0:
                    main_worksheet.write(row + beginning_row, 4, int_count, mid_green_cell)



        # self.export_complete("Excel Export", "Tempname.xlsx")
        return "Tempname.xlsx"
