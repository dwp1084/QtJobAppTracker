import os
import shutil
from typing import Protocol, Callable, Any

import packaging.version
from bs4 import BeautifulSoup

from constants import CURRENT_APP_VERSION

from PyQt6.QtCore import QSettings, QStandardPaths

# Name of the app settings file
CONFIG_FILE_NAME = "jobapptrackerconfig.ini"

CONFIG_DIR_NAME = f"Job Application Tracker"


class QtSignal(Protocol):
    """
    This class acts as a type hint fix for the "pyqtSignal has no attribute
    'emit'" warning that comes up, but doesn't have a straight-forward fix.

    It has no added function, it's meant to supress a warning for a non-issue.
    """
    def connect(self, slot: Callable[..., Any]) -> None: ...
    def disconnect(self, slot: Callable[..., Any]) -> None: ...
    def emit(self, *args: Any, **kwargs: Any) -> None: ...


def shorten_string(original_string: str, length: int) -> str:
    """
    Helper function to shorten a string down to a certain number of characters,
    with an additional ellipsis at the end
    :param original_string: Source string
    :param length: Maximum string length, not including ellipsis
    :return: Shortened string. If the resulting string is shorter, it will have
        an ellipsis appended to the end
    """
    if len(original_string) > length:
        substr = original_string[:length].strip()
        substr += "..."

        return substr

    return original_string


def add_privacy_filter(content: str, privacyFilter: bool):
    if privacyFilter:
        return "*****"
    else:
        return content


def readable_data_size(num_bytes: int):
    w_size = float(num_bytes)
    for unit in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if w_size < 1024.0:
            return f"{w_size:.2f} {unit}"
        w_size /= 1024.0

    raise NotImplementedError("Bytes count too large")


def strip_html(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    return soup.getText().strip()


def is_html(text: str) -> bool:
    return bool(BeautifulSoup(text, "html.parser").find())


def initializeSettings() -> QSettings:
    # Create and load the settings config file
    app_data = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )

    # Config file creation, checking and migration
    settings_dir = os.path.join(app_data, CONFIG_DIR_NAME)

    if not os.path.exists(settings_dir):
        os.mkdir(settings_dir)

    # Version directory and config file migration
    remove_open_file = False

    settings_version_dir = os.path.join(settings_dir, CURRENT_APP_VERSION)
    if not os.path.exists(settings_version_dir):
        os.mkdir(settings_version_dir)

        current_version = packaging.version.parse(CURRENT_APP_VERSION)

        # Do config file migration only if it's not a dev release
        if not current_version.is_devrelease:
            version_folders = os.listdir(settings_dir)
            previous_versions: list[packaging.version.Version] = []

            for version_str in version_folders:
                try:
                    version = packaging.version.parse(version_str)
                    if not version.is_devrelease and version < current_version:
                        previous_versions.append(version)

                except packaging.version.InvalidVersion:
                    pass  # Somehow, an invalid version folder got in there, just ignore it

            sorted_versions = sorted(previous_versions, reverse=True)
            if len(sorted_versions) > 0:
                most_recent_version = sorted_versions[0]
                shutil.copy2(
                    os.path.join(
                        os.path.join(settings_dir, str(most_recent_version)),
                        CONFIG_FILE_NAME
                    ),
                    os.path.join(settings_version_dir, CONFIG_FILE_NAME)
                )

                # If current version is of a different major version,
                # migrate the file, but don't automatically open the last
                # opened file.
                if current_version.major != most_recent_version.major:
                    remove_open_file = True

    settings = QSettings(os.path.join(settings_version_dir, CONFIG_FILE_NAME),
                              QSettings.Format.IniFormat
                              )

    if remove_open_file:
        settings.remove("file/currentFile")

    return settings
