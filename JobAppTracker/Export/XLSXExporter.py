from datetime import date
from typing import Callable, Any

from Data.Application import Application, Status, JobTypes
from Export.BaseExporter import BaseExporter

import xlsxwriter as xlw
import headers as h
from SQLite.ApplicationQueries import get_interview_count_for_application, ghost_prediction, \
    get_interviews_for_application


class XLSXExporter(BaseExporter):
    currentFile = ""

    def __init__(self):
        self.main_ws_columns: list[tuple[str, Callable[[Application], Any]]] = [
            (h.H_COMPANY, lambda app: app.company),
            (h.H_TITLE, lambda app: app.title),
            (h.H_APP_DATE, lambda app: app.applied_on),
            (h.H_FOLLOW_UP, lambda app: app.followed_up \
                if app.followed_up is not None else ""),
            (h.H_INTERVIEWS, lambda app:
                get_interview_count_for_application(self.currentFile,
                                                    app.app_id)
            ),
            (h.H_JOB_TYPE, lambda app: app.job_type),
            (h.H_LOCATION, lambda app: app.location),
            (h.H_APP_SRC, lambda app: app.found_at),
            (h.H_APP_WEBSITE, lambda app: app.website),
            (h.H_CONTACT, lambda app: app.contact),
            (h.H_MATERIALS, lambda app: app.materials),
            (h.H_SALARY, lambda app: app.salary),
            (h.H_STATUS, lambda app: ghost_prediction(self.currentFile, app)),
            (h.H_PENDING, lambda app: app.days_pending)
        ]

    @property
    def window_title(self) -> str:
        return "Excel Export"

    def setCurrentFile(self, currentFile):
        self.currentFile = currentFile

    def _export(self, data: list[Application]) -> str:
        with xlw.Workbook("Tempname.xlsx") as wb:

            # Create cell formats
            header_fmt = wb.add_format({"bold": True, "fg_color": "#bdbdbd"})
            bold = wb.add_format({"bold": "true"})
            italic = wb.add_format({"italic": True})
            date_format = wb.add_format(
                {"num_format": "d mmm yyyy"}
            )
            red_cell = wb.add_format({
                "fg_color": "red",
                "font_color": "white"})
            org_cell = wb.add_format({
                "fg_color": "orange",
                "font_color": "white"})
            mid_yel_cell = wb.add_format({"bg_color": "#ffd966"})
            mid_green_cell = wb.add_format({"fg_color": "#6aa84f"})
            mid_light_blue = wb.add_format({"fg_color": "#6d9eeb"})

            # Page 1 - Applications worksheet
            main_ws = wb.add_worksheet("Applications")

            note = f"""Exported from Job Application Tracker on {
                date.today().strftime('%B %d, %Y')
            }"""

            note_row = 0
            count_row = 1
            header_row = 3
            beginning_row = 4

            interviewed_apps: list[tuple[int, Application]] = []

            main_ws.write(note_row, 0, note, italic)
            main_ws.write(count_row, 0, f"Total applications sent: {len(data)}", bold)

            for col, (header, _) in enumerate(self.main_ws_columns):
                main_ws.write(header_row, col, header, header_fmt)

            # Fill in data and format
            for row, app in enumerate(data):
                currentStatus = Status.PENDING
                for col, (_, expr) in enumerate(self.main_ws_columns):
                    data = expr(app)
                    match data:
                        case date():
                            main_ws.write(row + beginning_row, col, data, date_format)
                        case Status.REJECTED:
                            main_ws.write(row + beginning_row, col, str(data), red_cell)
                            currentStatus = data
                        case Status.LIKELY_GHOSTED:
                            main_ws.write(row + beginning_row, col, str(data), org_cell)
                            currentStatus = data
                        case Status.INTERVIEW:
                            main_ws.write(row + beginning_row, col, str(data), mid_light_blue)
                            currentStatus = data
                        case Status():
                            main_ws.write(row + beginning_row, col, str(data))
                            currentStatus = data
                        case JobTypes.IN_PERSON:
                            main_ws.write(row + beginning_row, col, str(data), mid_green_cell)
                        case JobTypes.HYBRID:
                            main_ws.write(row + beginning_row, col, str(data), mid_yel_cell)
                        case JobTypes.REMOTE:
                            main_ws.write(row + beginning_row, col, str(data), mid_light_blue)
                        case _:
                            main_ws.write(row + beginning_row, col, data)

                # Get interview count and color in cell
                int_count = get_interview_count_for_application(self.currentFile,
                                                                app.app_id)
                if int_count > 0:
                    main_ws.write(row + beginning_row, 4, int_count, mid_green_cell)
                    interviewed_apps.append((row, app))

                # Match company cell color with app status color
                match currentStatus:
                    case Status.REJECTED:
                        fmt = red_cell if int_count < 1 else mid_yel_cell
                        main_ws.write(row + beginning_row,
                                             0,
                                             app.company,
                                             fmt)
                    case Status.LIKELY_GHOSTED:
                        fmt = org_cell if int_count < 1 else mid_yel_cell
                        main_ws.write(row + beginning_row,
                                             0,
                                             app.company,
                                             fmt)
                    case Status.INTERVIEW:
                        main_ws.write(row + beginning_row,
                                      0,
                                      app.company,
                                      mid_light_blue)
                    case _:
                        pass

            # Page 2 - Interviews worksheet
            ints_ws = wb.add_worksheet("Interviews")
            ints_ws_headers = ("Job Title", "Application Date", "Company", "Interviewed")
            for col, header in enumerate(ints_ws_headers):
                ints_ws.write(0, col, header, header_fmt)

            row = 1

            for (app_row, app) in interviewed_apps:
                int_dates = get_interviews_for_application(self.currentFile,
                                                           app.app_id)
                for int_date in int_dates:
                    ints_ws.write_url(row,
                                      0,
                                      f"internal:Applications!B{app_row + beginning_row + 1}",
                                      string=app.title
                                      )
                    ints_ws.write(row, 1, app.applied_on, date_format)
                    ints_ws.write(row, 2, app.company)
                    ints_ws.write(row, 3, int_date.interview_date, date_format)
                    row += 1


        # self.export_complete("Excel Export", "Tempname.xlsx")
        return "Tempname.xlsx"
