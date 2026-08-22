from PyQt6.QtCore import QSettings, pyqtSlot
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from QtGUI.ui.ui_AppSettingsWindow import Ui_AppSettingsWindow


class AppSettingsWindow(QDialog):
    def __init__(self, settings: QSettings):
        super().__init__()
        self.ui = Ui_AppSettingsWindow()
        self.ui.setupUi(self)
        self.settings = settings

        appDateThreshold = self.settings.value(
            "opts/appDateThreshold", defaultValue=21, type=int
        )
        followUpThreshold = self.settings.value(
            "opts/followUpThreshold", defaultValue=7, type=int
        )
        interviewThreshold = self.settings.value(
            "opts/interviewThreshold", defaultValue=60, type=int
        )

        self.ui.appDateThresholdEdit.setValidator(QIntValidator(1, 999))
        self.ui.followUpThresholdEdit.setValidator(QIntValidator(1, 999))
        self.ui.interviewThresholdEdit.setValidator(QIntValidator(1, 999))

        self.ui.appDateThresholdEdit.setText(str(appDateThreshold))
        self.ui.followUpThresholdEdit.setText(str(followUpThreshold))
        self.ui.interviewThresholdEdit.setText(str(interviewThreshold))

        apply_btn = self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.clicked.connect(self.submit)

    @pyqtSlot()
    def submit(self):
        appDateThreshold = int(self.ui.appDateThresholdEdit.text())
        followUpThreshold = int(self.ui.followUpThresholdEdit.text())
        interviewThreshold = int(self.ui.interviewThresholdEdit.text())

        self.settings.setValue("opts/appDateThreshold", appDateThreshold)
        self.settings.setValue("opts/followUpThreshold", followUpThreshold)
        self.settings.setValue("opts/interviewThreshold", interviewThreshold)

        self.close()