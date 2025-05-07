from PyQt6.QtWidgets import QMessageBox


def showErrorMessage(message, title, icon):
    msg = QMessageBox()
    msg.setIcon(icon)
    msg.setText(message)
    msg.setWindowTitle(title)
    msg.exec()