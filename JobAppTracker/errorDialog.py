from PyQt6.QtWidgets import QMessageBox


def _showMessage(message, title, icon, accepted=None, default_button=None, buttons=None):
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


def showErrorMessage(message):
    _showMessage(message, "Error", QMessageBox.Icon.Critical)


def showWarningMessage(message):
    _showMessage(message, "Warning", QMessageBox.Icon.Warning)


def showQuestionMessage(message, title, accepted):
    _showMessage(message,
                 title,
                 QMessageBox.Icon.Question,
                 accepted,
                 QMessageBox.StandardButton.No,
                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                 )
