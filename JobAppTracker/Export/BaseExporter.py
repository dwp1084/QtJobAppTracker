import os.path
from abc import ABC, abstractmethod

from Data.Application import Application
from errorDialog import showInfoMessage


class BaseExporter(ABC):

    @property
    @abstractmethod
    def window_title(self) -> str: ...

    @property
    @abstractmethod
    def filter(self) -> str: ...

    @property
    @abstractmethod
    def save_dialog_title(self) -> str: ...

    def _export_complete(self, filename):
        showInfoMessage(self.window_title, f"Data exported to {filename}.")

    @abstractmethod
    def _export(self, db_file: str, save_path: str, data: list[Application]) -> None: ...

    def export(self, db_file: str, save_path: str, data: list[Application]) -> None:
        self._export(db_file, save_path, data)
        self._export_complete(os.path.basename(save_path))