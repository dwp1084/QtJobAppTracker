from typing import Callable, Optional

from PyQt6.QtWidgets import QMessageBox


def _showMessage(message: str,
                 title: str,
                 icon: QMessageBox.Icon,
                 accepted: Callable[[], None] | None = None,
                 default_button: Optional[QMessageBox.StandardButton] = None,
                 buttons: Optional[QMessageBox.StandardButton] = None
                 ) -> None:
    """
    Internally used helper function to show a message box
    :param message: The message to be displayed.
    :param title: The title of the message box
    :param icon: The icon used on the message box
    :param accepted: Optional argument for a function to be called if the
        box action is accepted.
    :param default_button: Optional argument for the default button to focus on
    :param buttons: Optional argument for which buttons to use
    :return:
    """
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setText(message)
    msg.setWindowTitle(title)
    if buttons is not None:
        msg.accepted.connect(accepted)
        msg.accepted.connect(msg.close)
        msg.setStandardButtons(buttons)
        msg.setDefaultButton(default_button)
    msg.exec()


def showErrorMessage(message: str) -> None:
    """
    Shows a popup error message.
    :param message: The message to be displayed.
    :return:
    """
    _showMessage(message, "Error", QMessageBox.Icon.Critical)


def showWarningMessage(message: str) -> None:
    """
    Shows a popup warning message.
    :param message: The message to be displayed.
    :return:
    """
    _showMessage(message, "Warning", QMessageBox.Icon.Warning)


def showInfoMessage(title: str, message: str) -> None:
    """
    Shows a popup information message.
    :param title: Title of the message box.
    :param message: The message to be displayed.
    :return:
    """
    _showMessage(message, title, QMessageBox.Icon.Information)


def showQuestionMessage(message: str,
                        title: str,
                        accepted: Callable[[], None]
                        ) -> None:
    """
    Shows a popup question message. If the user responds "Yes", then it will
    call the provided callback function.
    :param message: The message to be displayed.
    :param title: Title of the message box.
    :param accepted: Callback function, which should be a pyqt slot that takes
        no arguments.
    :return:
    """
    _showMessage(message,
                 title,
                 QMessageBox.Icon.Question,
                 accepted,
                 QMessageBox.StandardButton.No,
                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                 )
