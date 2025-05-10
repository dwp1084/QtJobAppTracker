from dataclasses import asdict
from datetime import date
from enum import Enum, auto

from PyQt6.QtCore import pyqtSlot, pyqtSignal
from PyQt6.QtWidgets import QDialog

from Data.Application import Application
from QtGUI.ui.ui_AppInfoScreen import Ui_AppInfoScreen
from SQLite.ApplicationQueries import add_application, update_application, delete_application
from errorDialog import showWarningMessage, showQuestionMessage


class AppInfoDialog(QDialog):
    currentApplication = None
    currentFile = None
    app_id = None
    table_updated = pyqtSignal()

    class AppInfoType(Enum):
        NEW = auto(),
        EXISTING = auto()

    app_info_type = AppInfoType.NEW

    def __init__(self, parent=None):
        super().__init__(parent)

        # Create an instance of your generated UI and set it up
        self.ui = Ui_AppInfoScreen()
        self.ui.setupUi(self)

        self.textFieldMap = {
            self.ui.companyField: "company",
            self.ui.jobTitleField: "title",
            self.ui.locationField: "location",
            self.ui.appSiteField: "website",
            self.ui.salaryField: "salary",
            self.ui.materialsSent: "materials",
            self.ui.contactField: "contact"
        }

        self.ui.followedUpCheckBox.stateChanged.connect(
            lambda: self.ui.followUpWidget.setVisible(self.ui.followedUpCheckBox.isChecked())
        )

        self.ui.appSubmitButton.clicked.connect(self.submit)
        self.ui.appCancelButton.clicked.connect(self.close)
        self.ui.appDeleteButton.clicked.connect(self.askDelete)

    def fill_data(self, **kwargs):
        self.app_id = kwargs.get("app_id", None)
        self.ui.jobTypeField.setCurrentIndex(int(kwargs.get("job_type", 0)))
        self.ui.statusField.setCurrentIndex(int(kwargs.get("status", 0)))

        self.ui.interviewDateField.setDate(date.today())

        self.ui.commentsField.setPlainText(kwargs.get("comments"))
        self.ui.daysSinceAppliedLabel.setText(str(kwargs.get("days_pending")))

        follow_up_date = kwargs.get("followed_up", None)
        followed_up = follow_up_date is not None
        self.ui.followedUpCheckBox.setChecked(followed_up)
        if followed_up:
            self.ui.followUpWidget.show()
            self.ui.followUpField.setDate(follow_up_date)
        else:
            self.ui.followUpWidget.hide()
            self.ui.followUpField.setDate(date.today())

        for textField, key in self.textFieldMap.items():
            textField.setText(kwargs.get(key, ""))

    def setCurrentFile(self, newFile):
        self.currentFile = newFile

    @pyqtSlot()
    def newApplication(self):
        self.ui.interviewDatesWidget.hide()
        self.ui.appDeleteButton.hide()
        self.ui.DaysSinceAppliedWidget.hide()
        self.fill_data()
        self.app_info_type = self.AppInfoType.NEW
        self.exec()

    @pyqtSlot(Application)
    def editApplication(self, app):
        self.ui.interviewDatesWidget.show()
        self.ui.appDeleteButton.show()
        self.ui.DaysSinceAppliedWidget.show()
        self.app_info_type = self.AppInfoType.EXISTING
        args = asdict(app)
        args["days_pending"] = app.days_pending
        try:
            self.fill_data(**args)
        except Exception as e:
            print(str(e))
        self.exec()

    @pyqtSlot()
    def submit(self):
        required_fields = [self.ui.companyField, self.ui.jobTitleField, self.ui.appSiteField]

        for field in required_fields:
            if field.text() == "":
                showWarningMessage("Company, Job title, and Application site must not be blank.")
                return

        follow_up = ""
        if self.ui.followedUpCheckBox.isChecked():
            follow_up = self.ui.followUpField.date().toPyDate()
        match self.app_info_type:
            case self.AppInfoType.NEW:
                add_application(
                    self.currentFile,
                    date.today(),
                    self.ui.companyField.text(),
                    self.ui.jobTitleField.text(),
                    self.ui.appSiteField.text(),
                    self.ui.locationField.text(),
                    self.ui.materialsSent.text(),
                    self.ui.commentsField.toPlainText(),
                    self.ui.salaryField.text(),
                    self.ui.contactField.text(),
                    self.ui.statusField.currentIndex(),
                    self.ui.jobTypeField.currentIndex(),
                    follow_up
                )
            case self.AppInfoType.EXISTING:
                update_application(
                    self.currentFile,
                    self.app_id,
                    self.ui.companyField.text(),
                    self.ui.jobTitleField.text(),
                    self.ui.appSiteField.text(),
                    self.ui.locationField.text(),
                    self.ui.materialsSent.text(),
                    self.ui.commentsField.toPlainText(),
                    self.ui.salaryField.text(),
                    self.ui.contactField.text(),
                    self.ui.statusField.currentIndex(),
                    self.ui.jobTypeField.currentIndex(),
                    follow_up
                )

        self.table_updated.emit()
        self.close()

    @pyqtSlot()
    def askDelete(self):
        showQuestionMessage("Do you wish to delete this application?", "Delete application?", self.delete)

    @pyqtSlot()
    def delete(self):
        delete_application(self.currentFile, self.app_id)
        self.table_updated.emit()
        self.close()

