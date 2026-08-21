import os.path
from abc import ABC, abstractmethod

from QtGUI.AppTableModel import AppTableModel
from errorDialog import showInfoMessage


class BaseExporter(ABC):
    """
    Abstract exporter class that defines methods and properties for an exporter
    class.
    """

    @property
    @abstractmethod
    def window_title(self) -> str:
        """
        Title that should be displayed on the exported status message.
        """
        ...

    @property
    @abstractmethod
    def filter(self) -> str:
        """
        File extension filter for choosing a save file.
        """
        ...

    @property
    @abstractmethod
    def save_dialog_title(self) -> str:
        """
        Title for the save dialog window.
        """
        ...

    @property
    @abstractmethod
    def ext(self) -> str:
        """
        File extension without the dot.
        """
        ...

    def _export_complete(self, filename):
        """
        Displays a message telling the user that the data has been exported.
        :param filename: File name that it was exported to, without the path.
        :return:
        """
        showInfoMessage(self.window_title, f"Data exported to {filename}.")

    @abstractmethod
    def _export(self, db_file: str, save_path: str, data: AppTableModel) -> None:
        """
        Internal export function that is implemented by each exporter for a
        specific format.
        :param db_file: SQLite database file path.
        :param save_path: Save file path
        :param data: Data to be exported.
        :return:
        """
        ...

    def export(self, db_file: str, save_path: str, data: AppTableModel) -> None:
        """
        Exports the data to a file of a type defined by the exporter.
        :param db_file: SQLite database file path.
        :param save_path: Save file path
        :param data: Data to be exported.
        :return:
        """
        self._export(db_file, save_path, data)
        self._export_complete(os.path.basename(save_path))