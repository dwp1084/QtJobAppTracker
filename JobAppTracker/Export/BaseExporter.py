from abc import ABC, abstractmethod

from Data.Application import Application
from errorDialog import showInfoMessage


class BaseExporter(ABC):

    @property
    @abstractmethod
    def window_title(self) -> str: ...

    def _export_complete(self, filename):
        showInfoMessage(self.window_title, f"Data exported to {filename}.")

    @abstractmethod
    def _export(self, data: list[Application]) -> str: ...

    def export(self, data: list[Application]) -> None:
        filename = self._export(data)
        self._export_complete(filename)