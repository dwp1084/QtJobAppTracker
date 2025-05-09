from dataclasses import asdict
from datetime import date
from enum import Enum, auto

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog

from Data.Application import Application
from QtGUI.ui.ui_AppInfoScreen import Ui_AppInfoScreen


class AppInfoDialog(QDialog):
    currentApplication = None
    app_id = None

    class AppInfoType(Enum):
        NEW = auto(),
        EXISTING = auto()

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

    def fill_data(self, **kwargs):
        self.app_id = kwargs.get("app_id", None)
        # self.ui.companyField.setText(kwargs.get('company', ""))
        # self.ui.jobTitleField.setText(kwargs.get("title", ""))
        # self.ui.locationField.setText(kwargs.get("location", ""))
        self.ui.jobTypeField.setCurrentIndex(kwargs.get("job_type", 0))
        self.ui.statusField.setCurrentIndex(kwargs.get("status", 0))

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

    @pyqtSlot()
    def newApplication(self):
        self.ui.interviewDatesWidget.hide()
        self.ui.appDeleteButton.hide()
        self.ui.DaysSinceAppliedWidget.hide()
        try:
            self.fill_data()
        except Exception as e:
            print(str(e))
        self.exec()

    @pyqtSlot(Application)
    def editApplication(self, app):
        self.ui.interviewDatesWidget.show()
        self.ui.appDeleteButton.show()
        self.ui.DaysSinceAppliedWidget.show()
        args = asdict(app)
        print(args)
        args["days_pending"] = app.days_pending
        self.fill_data(**args)
        self.exec()
