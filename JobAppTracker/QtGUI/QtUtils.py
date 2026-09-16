import logging
import os
import sys
import shutil
from typing import Protocol, Callable, Any

import packaging.version
from bs4 import BeautifulSoup

from constants import CURRENT_APP_VERSION

from PyQt6.QtCore import QSettings, QStandardPaths

# Name of the app settings file
CONFIG_FILE_NAME = "jobapptrackerconfig.ini"

CONFIG_DIR_NAME = f"Job Application Tracker"

logger = logging.getLogger(__name__)

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


def get_version_dir(current_version, version_dir, settings_dir):
    """
    Helper function for copying the config file, considering the need for the
    linux support fix

    :param current_version:
    :param version_dir:
    :param settings_dir:
    :return:
    """
    remove_open_file = False
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
        logger.debug(
            f"Found suitable version. Migrating config v{most_recent_version} -> v{CURRENT_APP_VERSION}."
        )
        shutil.copy2(
            os.path.join(
                os.path.join(settings_dir, str(most_recent_version)),
                CONFIG_FILE_NAME
            ),
            os.path.join(version_dir, CONFIG_FILE_NAME)
        )

        # If current version is of a different major version,
        # migrate the file, but don't automatically open the last
        # opened file.
        if current_version.major != most_recent_version.major:
            remove_open_file = True

    return len(sorted_versions), remove_open_file


def initializeSettings() -> QSettings:
    # Create and load the settings config file
    app_data = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )

    settings_dir = app_data
    win_legacy_settings_dir = os.path.join(
        os.path.dirname(settings_dir),
        f"Python\\{CONFIG_DIR_NAME}"
    )
    # Config file creation, checking and migration
    # settings_dir = os.path.join(app_data, CONFIG_DIR_NAME)

    if not os.path.exists(settings_dir):
        os.mkdir(settings_dir)

    # Version directory and config file migration
    remove_open_file = False

    settings_version_dir = os.path.join(settings_dir, CURRENT_APP_VERSION)
    if not os.path.exists(settings_version_dir):
        logger.debug(
            f"No config location found for v{CURRENT_APP_VERSION}."
        )
        os.mkdir(settings_version_dir)

        current_version = packaging.version.parse(CURRENT_APP_VERSION)

        # Do config file migration only if it's not a dev release
        if not current_version.is_devrelease:
            logger.debug("Not a dev release. Searching for migrations.")
            num_versions, remove_open_file = get_version_dir(current_version, settings_version_dir, settings_dir)

            # Due to an error discovered in developing 2.1 that prevented the software
            # from running on Linux, the main config path needed to be changed.
            # As such, Windows should do an extra check for file migrations in
            # the old path.
            if num_versions == 0 and sys.platform == "win32":
                logger.debug("No migrations found on a Windows system. Checking legacy folder.")
                # If the path doesn't exist, ignore it. Nothing to see here.
                try:
                    _, remove_open_file = get_version_dir(current_version,
                                                          settings_version_dir,
                                                          win_legacy_settings_dir
                                                          )
                except FileNotFoundError:
                    logger.debug("Legacy folder not found. No files to migrate.")
                    remove_open_file = False

    settings = QSettings(os.path.join(settings_version_dir, CONFIG_FILE_NAME),
                              QSettings.Format.IniFormat
                              )

    if remove_open_file:
        settings.remove("file/currentFile")

    return settings
