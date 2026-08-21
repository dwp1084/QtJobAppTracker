from typing import cast

from PyQt6.QtCore import QSortFilterProxyModel, pyqtSlot

from Data.Application import Application, Status
from QtGUI.AppTableModel import AppTableModel
from SQLite.ApplicationQueries import ghost_prediction


class TableFilterProxy(QSortFilterProxyModel):
    def __init__(self, currentFile):
        super().__init__()
        self.showInactive = True
        self.searchText = ""
        self.currentFile = currentFile
        self.inverted = False

    def sourceModel(self) -> AppTableModel:
        return cast(AppTableModel, super().sourceModel())

    def setSourceModel(self, sourceModel: AppTableModel) -> None:
        super().setSourceModel(sourceModel)

    def set_show_inactive(self, inactive: bool) -> None:
        self.showInactive = inactive
        self.invalidateFilter()

    def set_search_text(self, searchText: str) -> None:
        self.searchText = searchText.lower()
        self.invalidateFilter()

    def set_current_file(self, filePath: str) -> None:
        self.currentFile = filePath
        self.invalidateFilter()

    @pyqtSlot(bool)
    def toggle_inverted(self, inverted: bool) -> None:
        self.inverted = inverted
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        app = self.sourceModel()[source_row]

        if not self.showInactive:
            if self.is_inactive(app):
                return False

        if self.searchText:
            if not self.match_search(app):
                return False

        return True

    def num_hidden(self) -> int:
        if self.sourceModel() is None:
            return 0

        return self.sourceModel().rowCount() - self.rowCount()

    def is_inactive(self, application: Application) -> bool:
        app_status = ghost_prediction(self.currentFile, application)

        return app_status in {Status.LIKELY_GHOSTED,
                              Status.REJECTED,
                              Status.DECLINED,
                              Status.CANCELLED
                              }

    def match_search(self, application: Application) -> bool:
        matches = (
            self.searchText in application.company.lower()
            or self.searchText in application.title.lower()
            or self.searchText in str(application.job_type).lower()
            or self.searchText in application.location.lower()
            or self.searchText in application.found_at.lower()
            or self.searchText in application.website.lower()
            or self.searchText in application.contact.lower()
            or self.searchText in application.materials.lower()
            or self.searchText in application.salary.lower()
            or self.searchText in str(ghost_prediction(self.currentFile, application)).lower()
            or self.searchText in application.experience.lower()
        )

        return matches if not self.inverted else not matches
