import datetime

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QDialog, QDialogButtonBox

from Data.Application import Status
from QtGUI.ui.ui_PurgeDataWindow import Ui_PurgeDataWindow


class PurgeDataWindow(QDialog):
    purgeJD = pyqtSignal(datetime.date, set)
    purgeJDFormat = pyqtSignal(datetime.date, set)
    purgeDocs = pyqtSignal(datetime.date, set)

    def __init__(self):
        super().__init__()
        self.ui = Ui_PurgeDataWindow()
        self.ui.setupUi(self)
        # self.settings = settings

        apply_btn = self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Apply)
        apply_btn.clicked.connect(self.purge)

        self.ui.purgeDataTypeGroup.setId(self.ui.jobDescRadioButton, 1)
        self.ui.purgeDataTypeGroup.setId(self.ui.jobDescFormatRadioButton, 2)
        self.ui.purgeDataTypeGroup.setId(self.ui.docRadioButton, 3)

    @pyqtSlot()
    def purge(self):
        before_date = self.ui.dateEdit.date().toPyDate()

        whitelisted_statuses = set()
        if self.ui.offeredCheckbox.isChecked():
            whitelisted_statuses.add(Status.OFFER)
        if self.ui.pendingCheckbox.isChecked():
            whitelisted_statuses.add(Status.PENDING)
        if self.ui.interviewingCheckbox.isChecked():
            whitelisted_statuses.add(Status.INTERVIEW)
        if self.ui.ghostedCheckbox.isChecked():
            whitelisted_statuses.add(Status.LIKELY_GHOSTED)
        if self.ui.rejectedCheckbox.isChecked():
            whitelisted_statuses.add(Status.REJECTED)
        if self.ui.declinedCheckbox.isChecked():
            whitelisted_statuses.add(Status.DECLINED)
        if self.ui.cancelledCheckbox.isChecked():
            whitelisted_statuses.add(Status.CANCELLED)

        match self.ui.purgeDataTypeGroup.checkedId():
            case 1:
                self.purgeJD.emit(before_date, whitelisted_statuses)
            case 2:
                pass
            case 3:
                pass
            case _:
                raise NotImplementedError("Invalid button ID")

        self.close()