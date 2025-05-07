from PyQt6.QtWidgets import QMainWindow

from JobAppTracker.QtGUI.ui.ui_JobAppTrackerMainWindow import Ui_JobAppTrackerMainWindow
from QtGUI.AppInfoScreen import AppInfoDialog


class JobAppTrackerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_JobAppTrackerMainWindow()
        self.ui.setupUi(self)

        self.appInfoScreen = AppInfoDialog()

        self.ui.appTableWidget.cellDoubleClicked.connect(lambda: print("Yeet"))
        self.ui.addAppButton.clicked.connect(self.appInfoScreen.exec)
