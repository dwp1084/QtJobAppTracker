from dataclasses import asdict
from datetime import date
from enum import Enum, auto

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QPoint
from PyQt6.QtWidgets import QDialog, QCompleter, QMenu

from Data.Application import Application
from QtGUI.ui.ui_AppInfoScreen import Ui_AppInfoScreen
from SQLite.ApplicationQueries import (add_application,
                                       update_application,
                                       delete_application,
                                       get_interviews_for_application,
                                       add_interview_date,
                                       delete_interview)
from SQLite.AutocompleteQueries import (autocomplete_companies,
                                        autocomplete_locations,
                                        autocomplete_app_sources,
                                        insert_companies,
                                        insert_locations,
                                        insert_app_sources)
from errorDialog import showWarningMessage, showQuestionMessage


class AppInfoDialog(QDialog):
    """
    Dialog screen that allows a user to have an extended view of a specific
    application and to create or modify applications.
    """

    currentFile = None
    """
    Path to the data file that's currently in use
    """

    app_id = None
    """
    The application ID for the currently loaded application
    """

    interview_dates = []
    """
    Internal list of interview dates shown in the interviews list
    """

    table_updated = pyqtSignal()
    """
    Emitted when an update to the main table data happens, triggering a data 
    reload
    """

    class AppInfoType(Enum):
        """
        States for the app info dialog
        """
        NEW = auto(),
        EXISTING = auto()

    app_info_type = AppInfoType.NEW

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AppInfoScreen()
        self.ui.setupUi(self)

        # Maps fields to dictionary keys for adding info to screen
        self.textFieldMap = {
            self.ui.companyField: "company",
            self.ui.jobTitleField: "title",
            self.ui.locationField: "location",
            self.ui.appSiteField: "website",
            self.ui.salaryField: "salary",
            self.ui.materialsSent: "materials",
            self.ui.contactField: "contact"
        }

        # Connecting signals to slots
        self.ui.followedUpCheckBox.stateChanged.connect(
            lambda: self.ui.followUpWidget.setVisible(
                self.ui.followedUpCheckBox.isChecked()
            )
        )

        self.ui.interviewDateSubmit.clicked.connect(self.interview_submit)

        self.ui.appSubmitButton.clicked.connect(self.app_submit)
        self.ui.appCancelButton.clicked.connect(self.close)
        self.ui.appDeleteButton.clicked.connect(self.askDelete)

        self.ui.interviewsList.customContextMenuRequested.connect(
            self.interview_list_ctx_menu
        )

    def fill_data(self, **kwargs):
        """
        Fills data into the data fields from various fields
        :param kwargs: Keyword arguments for the various field names
        :return:
        """
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
        """
        Adds autocomplete data to a text field so results can be autocompleted.
        :param fetch_func: Database function to fetch autocomplete data from the
            database.
        :param text_field: Text field where the autocomplete data should apply.
        :return:
        """
        word_list = fetch_func()
        completer = QCompleter(word_list, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        text_field.setCompleter(completer)

    def refresh_interview_dates(self):
        """
        Clears and reloads the list of interviews for this specific application
        when the data has changed.
        :return:
        """
        self.interview_dates.clear()
        for date_row in get_interviews_for_application(
                self.currentFile,
                self.app_id
        ):
            row = dict(date_row)
            self.interview_dates.append({
                "date_id": row["date_id"],
                "interview_date": date.fromisoformat(row["interview_date"])
            })

        self.ui.interviewsList.clear()
        for date_row in self.interview_dates:
            self.ui.interviewsList.addItem(
                date_row["interview_date"].strftime("%b %d, %Y")
            )

    def setCurrentFile(self, newFile):
        """
        Sets the current data file
        :param newFile: New data file
        :return:
        """
        self.currentFile = newFile

    @pyqtSlot()
    def newApplication(self):
        """
        Sets up and opens this dialog for entering a new application
        :return:
        """
        self.ui.interviewDatesWidget.hide()
        self.ui.appDeleteButton.hide()
        self.ui.DaysSinceAppliedWidget.hide()
        self.fill_data()
        self.app_info_type = self.AppInfoType.NEW
        self.exec()

    @pyqtSlot(Application)
    def editApplication(self, app):
        """
        Opens this dialog and fills it with application data to edit an existing
        application.
        :param app: Application data
        :return:
        """
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
        """
        Function called when the submit button for this dialog is clicked. If
        the application loaded in is a new one, it will create a new application
        with the given data. If it is instead an existing one, it will be
        modified.
        :return:
        """

        # Checks if the minimal required fields are filled, otherwise it returns
        required_fields = [self.ui.companyField,
                           self.ui.jobTitleField,
                           self.ui.appSiteField]

        for field in required_fields:
            if field.text() == "":
                showWarningMessage(
                    "Company, Job title, and Application site must not be blank."
                )
                return

        # Adds follow-up date only if the checkbox has been pressed.
        follow_up = ""
        if self.ui.followedUpCheckBox.isChecked():
            follow_up = self.ui.followUpField.date().toPyDate()

        # Chooses which function to call based on dialog state
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

        # Updates autocomplete data
        insert_companies(self.ui.companyField.text())
        insert_locations(self.ui.locationField.text())
        insert_app_sources(self.ui.appSiteField.text())

        # Notifies that the table data has changed and closes the dialog
        self.table_updated.emit()
        self.close()

    @pyqtSlot()
    def interview_submit(self):
        """
        Function called when the interview date submit button is pressed.
        Submits the new date and refreshes the data.
        :return:
        """
        interview_date = self.ui.interviewDateField.date().toPyDate()
        add_interview_date(self.currentFile, self.app_id, interview_date)

        self.refresh_interview_dates()
        self.table_updated.emit()

    @pyqtSlot()
    def askDelete(self):
        """
        Shows a question dialog asking if the application should be deleted.
        :return:
        """
        showQuestionMessage("Do you wish to delete this application?",
                            "Delete application?",
                            self.delete
                            )

    @pyqtSlot()
    def delete(self):
        """
        Deletes the loaded application and notifies that the table data has been
        updated.
        :return:
        """
        delete_application(self.currentFile, self.app_id)
        self.table_updated.emit()
        self.close()

    @pyqtSlot(QPoint)
    def interview_list_ctx_menu(self, pos):
        """
        Creates a context menu for right-clicking on an interview date, showing
        an option to delete the date. If that option is clicked, the date is
        deleted and observers are notified that the table data has changed.
        :param pos: Selected interview date position
        :return:
        """
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

