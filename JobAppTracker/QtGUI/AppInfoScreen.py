from PyQt6.QtWidgets import QDialog

from QtGUI.ui.ui_AppInfoScreen import Ui_AppInfoScreen


class AppInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create an instance of your generated UI and set it up
        self.ui = Ui_AppInfoScreen()
        self.ui.setupUi(self)