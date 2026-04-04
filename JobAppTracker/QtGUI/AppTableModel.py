from typing import Callable

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from Data.Application import Application
from SQLite.ApplicationQueries import (get_interview_count_for_application,
                                       ghost_prediction)
import constants as h


class AppTableModel(QAbstractTableModel):
    """
    Table model for the main application table. Defines columns and mapping of
    data from the application dataclass to the table view.
    """

    def __init__(self, data: list[Application], currentFile: str):
        super().__init__()
        self._data = data
        self.currentFile = currentFile
        self.privacyFilter = False

        self._columns: list[tuple[str, Callable[[Application], str]]] = [
            (h.H_COMPANY, lambda app: self.add_privacy_filter(app.company)),
            (h.H_TITLE, lambda app: app.title),
            (h.H_APP_DATE, lambda app: app.applied_on.strftime("%b %d, %Y")),
            (h.H_FOLLOW_UP, lambda app: app.followed_up.strftime("%b %d, %Y") \
                if app.followed_up is not None else ""),
            (h.H_INTERVIEWS, lambda app: str(
                    get_interview_count_for_application(self.currentFile,
                                                        app.app_id)
                )),
            (h.H_JOB_TYPE, lambda app: str(app.job_type)),
            (h.H_LOCATION, lambda app: self.add_privacy_filter(app.location)),
            (h.H_EXPERIENCE, lambda app: app.experience),
            (h.H_APP_SRC, lambda app: app.found_at),
            (h.H_APP_WEBSITE, lambda app: app.website),
            (h.H_CONTACT, lambda app: self.add_privacy_filter(app.contact)),
            (h.H_MATERIALS, lambda app: app.materials),
            (h.H_SALARY, lambda app: app.salary),
            (h.H_STATUS, lambda app: str(ghost_prediction(self.currentFile, app))),
            (h.H_TTR, lambda app: app.time_to_rejection),
            (h.H_COMMENT, lambda app: self.add_privacy_filter(app.comments)),
            (h.H_PENDING, lambda app: str(app.days_pending))
        ]

    def add_privacy_filter(self, content: str):
        if self.privacyFilter:
            return "*****"
        else:
            return content

    def enable_privacy_filter(self, setting: bool):
        self.privacyFilter = setting

    def searchColIdx(self, name: str) -> int:
        """
        Searches for a column by its header name.
        :param name: Header name to search for
        :return: Column index if found, -1 if not found.
        """
        for i, (header, _) in enumerate(self._columns):
            if header == name:
                return i
        return -1

    def setCurrentFile(self, currentFile: str) -> None:
        """
        Changes the current open file path to reference.
        :param currentFile: Open file path
        :return:
        """
        self.currentFile = currentFile

    def setModelData(self, data: list[Application]) -> None:
        """
        Changes the data list to be displayed on the table.
        :param data: Data list
        :return:
        """
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        """
        Reimplementation of function for data model. Returns the row count for
        the table (number of entries in the data)
        :param parent:
        :return:
        """
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        """
        Reimplementation of function for data model. Returns the column count
        for the table (number of internally defined columns)
        :param parent:
        :return:
        """
        return len(self._columns)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        """
        Reimplementation of function for data model. Returns the data for a
        specific cell in the table.
        :param index:
        :param role:
        :return:
        """
        if role == Qt.ItemDataRole.DisplayRole:
            app = self._data[index.row()]
            _, expr = self._columns[index.column()]
            return expr(app)
        return None

    def headerData(self,
                   section: int,
                   orientation: Qt.Orientation,
                   role: Qt.ItemDataRole = ...):
        """
        Reimplementation of function for data model. Returns the header data for
        a specific column in the table.
        :param section:
        :param orientation:
        :param role:
        :return:
        """
        if (role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal):
            return self._columns[section][0]
        return None
