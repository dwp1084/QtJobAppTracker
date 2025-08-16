from typing import Callable

from PyQt6.QtWidgets import QMessageBox


def _showMessage(message: str,
                 title: str,
                 icon: QMessageBox.Icon,
                 accepted: Callable[[], None] | None = None,
                 default_button: QMessageBox.StandardButton | None = None,
                 buttons: QMessageBox.StandardButton | None = None
                 ) -> None:
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
    _showMessage(message, "Error", QMessageBox.Icon.Critical)


def showWarningMessage(message: str) -> None:
    _showMessage(message, "Warning", QMessageBox.Icon.Warning)


def showQuestionMessage(message: str,
                        title: str,
                        accepted: Callable[[], None]
                        ) -> None:
    _showMessage(message,
                 title,
                 QMessageBox.Icon.Question,
                 accepted,
                 QMessageBox.StandardButton.No,
                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                 )
