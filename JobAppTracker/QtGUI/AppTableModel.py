from typing import Callable

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from Data.Application import Application
from SQLite.ApplicationQueries import get_interview_count_for_application, ghost_prediction


class AppTableModel(QAbstractTableModel):
    def __init__(self, data: list[Application], currentFile: str):
        super().__init__()
        self._data = data
        self.currentFile = currentFile

        self._columns: list[tuple[str, Callable[[Application], str]]] = [
            ("Company", lambda app: app.company),
            ("Job Title", lambda app: app.title),
            ("Applied On", lambda app: app.applied_on.strftime("%b %d, %Y")),
            ("Followed Up", lambda app: app.followed_up.strftime("%b %d, %Y") \
                if app.followed_up is not None else ""),
            ("Interviews", lambda app: str(
                    get_interview_count_for_application(self.currentFile,
                                                        app.app_id)
                )),
            ("Type", lambda app: str(app.job_type)),
            ("Location", lambda app: app.location),
            ("App Found On", lambda app: app.found_at),
            ("App Website", lambda app: app.website),
            ("Contact", lambda app: app.contact),
            ("Materials Sent", lambda app: app.materials),
            ("Salary", lambda app: app.salary),
            ("Status", lambda app: str(ghost_prediction(self.currentFile, app))),
            ("Comments", lambda app: app.comments),
            ("Days Pending", lambda app: str(app.days_pending))
        ]

    def searchColIdx(self, name: str) -> int:
        for i, (header, _) in enumerate(self._columns):
            if header == name:
                return i
        return -1

    def setCurrentFile(self, currentFile: str) -> None:
        self.currentFile = currentFile

    def setModelData(self, data: list[Application]) -> None:
        self.beginResetModel()
        self._data = data
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._columns)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...):
        if role == Qt.ItemDataRole.DisplayRole:
            app = self._data[index.row()]
            _, expr = self._columns[index.column()]
            return expr(app)
        return None

    def headerData(self,
                   section: int,
                   orientation: Qt.Orientation,
                   role: Qt.ItemDataRole = ...):
        if (role == Qt.ItemDataRole.DisplayRole
                and orientation == Qt.Orientation.Horizontal):
            return self._columns[section][0]
        return None
