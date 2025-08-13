from dataclasses import asdict
from datetime import date
from enum import Enum, auto

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QPoint
from PyQt6.QtWidgets import QDialog, QCompleter, QMenu

from Data.Application import Application
from QtGUI.ui.ui_AppInfoScreen import Ui_AppInfoScreen
from SQLite.ApplicationQueries import add_application, update_application, delete_application, \
                                       get_interviews_for_application, add_interview_date, delete_interview
from SQLite.AutocompleteQueries import autocomplete_companies, autocomplete_locations, autocomplete_app_sources, \
    insert_companies, insert_locations, insert_app_sources
from errorDialog import showWarningMessage, showQuestionMessage


class AppInfoDialog(QDialog):
    currentApplication = None
    currentFile = None
    app_id = None
    table_updated = pyqtSignal()

    interview_dates = []

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

        self.ui.interviewDateSubmit.clicked.connect(self.interview_submit)

        self.ui.appSubmitButton.clicked.connect(self.app_submit)
        self.ui.appCancelButton.clicked.connect(self.close)
        self.ui.appDeleteButton.clicked.connect(self.askDelete)

        self.ui.interviewsList.customContextMenuRequested.connect(self.interview_list_ctx_menu)

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

        self.fill_autocomplete_data(autocomplete_companies, self.ui.companyField)
        self.fill_autocomplete_data(autocomplete_locations, self.ui.locationField)
        self.fill_autocomplete_data(autocomplete_app_sources, self.ui.appSiteField)

    def fill_autocomplete_data(self, fetch_func, text_field):
        word_list = fetch_func()
        completer = QCompleter(word_list, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        text_field.setCompleter(completer)

    def refresh_interview_dates(self):
        self.interview_dates.clear()
        for date_row in get_interviews_for_application(self.currentFile, self.app_id):
            row = dict(date_row)
            self.interview_dates.append({
                "date_id": row["date_id"],
                "interview_date": date.fromisoformat(row["interview_date"])
            })

        self.ui.interviewsList.clear()
        for date_row in self.interview_dates:
            self.ui.interviewsList.addItem(date_row["interview_date"].strftime("%b %d, %Y"))

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
        self.fill_data(**args)
        self.refresh_interview_dates()
        self.exec()

    @pyqtSlot()
    def app_submit(self):
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

        insert_companies(self.ui.companyField.text())
        insert_locations(self.ui.locationField.text())
        insert_app_sources(self.ui.appSiteField.text())

        self.table_updated.emit()
        self.close()

    @pyqtSlot()
    def interview_submit(self):
        interview_date = self.ui.interviewDateField.date().toPyDate()
        add_interview_date(self.currentFile, self.app_id, interview_date)

        self.refresh_interview_dates()
        self.table_updated.emit()

    @pyqtSlot()
    def askDelete(self):
        showQuestionMessage("Do you wish to delete this application?", "Delete application?", self.delete)

    @pyqtSlot()
    def delete(self):
        delete_application(self.currentFile, self.app_id)
        self.table_updated.emit()
        self.close()

    @pyqtSlot(QPoint)
    def interview_list_ctx_menu(self, pos):
        global_pos = self.ui.interviewsList.mapToGlobal(pos)

        item = self.ui.interviewsList.itemAt(pos)
        if item is None:
            return

        menu = QMenu()
        delete_action = menu.addAction("Delete")

        selected_action = menu.exec(global_pos)
        if selected_action == delete_action:
            row = self.ui.interviewsList.row(item)
            date_id = self.interview_dates[row]["date_id"]

            delete_interview(self.currentFile, date_id)
            self.refresh_interview_dates()
            self.table_updated.emit()

