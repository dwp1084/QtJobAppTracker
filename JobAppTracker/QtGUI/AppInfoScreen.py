from datetime import date
from enum import Enum, auto
from typing import Callable

from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QPoint
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QDialog, QCompleter, QMenu, QLineEdit, QCheckBox, QStyle, QWhatsThis

from Data.Application import Application, Status
from Data.InterviewDate import InterviewDate
from QtGUI.QtUtils import QtSignal, shorten_string
from QtGUI.ui.ui_AppInfoScreen import Ui_AppInfoScreen
from SQLite.ApplicationQueries import (add_application,
                                       update_application,
                                       delete_application,
                                       add_interview_date,
                                       delete_interview,
                                       get_interviews_for_application,
                                       set_interview_status,
                                       ghost_prediction)
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

    currentFile: str | None = None
    """
    Path to the data file that's currently in use
    """

    app_id: int | None = None
    """
    The application ID for the currently loaded application
    """

    interview_dates: list[InterviewDate] = []
    """
    Internal list of interview dates shown in the interviews list
    """

    table_updated: QtSignal = pyqtSignal()
    """
    Emitted when an update to the main table data happens, triggering a data 
    reload
    """

    privacy_filter: bool = False

    class AppInfoType(Enum):
        """
        States for the app info dialog
        """
        NEW = auto(),
        EXISTING = auto()

    app_info_type: AppInfoType = AppInfoType.NEW

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.ui = Ui_AppInfoScreen()
        self.ui.setupUi(self)

        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)

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

        self.ui.minExpField.setValidator(QIntValidator(0, 50))
        self.ui.maxExpField.setValidator(QIntValidator(0, 50))

        self.ui.storeRejectionDateCheckbox.checkStateChanged.connect(self.enable_rej_date_edit)

        self.ui.modifyButton.clicked.connect(
            lambda: self.edit_job_link(True)
        )

        self.ui.interviewsList.customContextMenuRequested.connect(
            self.interview_list_ctx_menu
        )

        self.ui.statusHelpButton.clicked.connect(self.whats_this_status_field)

    def enable_privacy_filter(self, setting: bool):
        self.privacy_filter = setting

    def fill_data(self, app: Application = Application()) -> None:
        """
        Fills data into the data fields from an application.
        :param app: Application to fill. If left blank, a placeholder application
        will be used in order to clear data for a new application
        :return:
        """
        self.ui.interviewDateField.setDate(date.today())

        # Disconnect signal from status field while data is being filled out
        # We only care about it when the user changes the status
        try:
            self.ui.statusField.currentIndexChanged.disconnect()
        except TypeError:
            pass    # Error when no signals are connected, but in this case that's fine

        # If the placeholder application is used, no application is loaded
        self.app_id = app.app_id if app.app_id > -1 else None

        app_date_box_date = date.today() if self.app_id is None else app.applied_on
        self.ui.appDateEdit.setDate(app_date_box_date)

        status = ghost_prediction(self.currentFile, app)
        self.ui.statusField.setPlaceholderText(str(status))

        # Statuses that can be selected in combobox. If a different one applies,
        # placeholder text is shown
        selectableStatuses = {Status.PENDING, Status.OFFER, Status.REJECTED, Status.DECLINED, Status.CANCELLED}

        status_idx = int(status) if status in selectableStatuses else -1

        self.ui.jobTypeField.setCurrentIndex(int(app.job_type))
        self.ui.statusField.setCurrentIndex(status_idx)
        self.ui.commentsField.setPlainText(app.comments)
        self.ui.daysSinceAppliedLabel.setText(str(app.days_pending))

        followed_up = app.followed_up is not None
        self.ui.followedUpCheckBox.setChecked(followed_up)
        if followed_up:
            self.ui.followUpWidget.show()
            self.ui.followUpField.setDate(app.followed_up)
        else:
            self.ui.followUpWidget.hide()
            self.ui.followUpField.setDate(date.today())

        exp_low = "" if app.exp_low is None else f"{app.exp_low}"
        exp_upp = "" if app.exp_upp is None else f"{app.exp_upp}"

        plainTextFields: dict[QLineEdit, str] = {
            self.ui.companyField: app.company,
            self.ui.jobTitleField: app.title,
            self.ui.locationField: app.location,
            self.ui.appSiteField: app.website,
            self.ui.salaryField: app.salary,
            self.ui.materialsSent: app.materials,
            self.ui.contactField: app.contact,
            self.ui.appFoundOnField: app.found_at,
            self.ui.hyperlinkField: app.link,
            self.ui.minExpField: exp_low,
            self.ui.maxExpField: exp_upp
        }

        for field, data in plainTextFields.items():
            field.setText(data)

        hyperlink = ""
        if app.link != "":
            hyperlink = f"<a href={app.link}>{app.link}</a>"

        self.ui.hyperlinkLabel.setText(hyperlink)

        self.ui.jobDescriptionEdit.setHtml(app.description)

        # Hyperlink logic
        link_filled = app.link == ""

        self.edit_job_link(link_filled)

        self.ui.storeRejectionDateCheckbox.setChecked(app.rej_date is None)
        self.ui.rejectionDateEdit.setDisabled(app.rej_date is None)

        if app.rej_date is not None:
            self.ui.rejectionDateEdit.setDate(app.rej_date)
        else:
            self.ui.rejectionDateEdit.setDate(date.today())

        showRejDateField = status == Status.REJECTED or status == Status.DECLINED
        self.ui.rejectionDateWidget.setVisible(showRejDateField)

        self.fill_autocomplete_data(autocomplete_companies, self.ui.companyField)
        self.fill_autocomplete_data(autocomplete_locations, self.ui.locationField)
        self.fill_autocomplete_data(autocomplete_app_sources, self.ui.appSiteField)
        self.fill_autocomplete_data(autocomplete_app_sources, self.ui.appFoundOnField)

        # Re-instate the signal
        self.ui.statusField.currentIndexChanged.connect(
            lambda idx: self.check_and_set_reject_date(Status(idx))
        )

    def check_and_set_reject_date(self, app_status: Status):
        if app_status == Status.REJECTED or app_status == Status.DECLINED:
            self.ui.rejectionDateWidget.setVisible(True)

            if self.ui.storeRejectionDateCheckbox.checkState() == Qt.CheckState.Checked:
                self.ui.storeRejectionDateCheckbox.setChecked(False)
                self.ui.rejectionDateEdit.setDate(date.today())
        else:
            self.ui.rejectionDateWidget.setVisible(False)
            self.ui.storeRejectionDateCheckbox.setChecked(True)

    @pyqtSlot()
    def whats_this_status_field(self):
        sf = self.ui.statusField
        pos = sf.mapToGlobal(QPoint(sf.width() // 2, sf.height() // 2))
        QWhatsThis.showText(pos, sf.whatsThis(), sf)

    @pyqtSlot(Qt.CheckState)
    def enable_rej_date_edit(self, checked: Qt.CheckState):
        disableEdit = checked == Qt.CheckState.Checked
        self.ui.rejectionDateEdit.setDisabled(disableEdit)

    def edit_job_link(self, isEditable: bool):
        self.ui.modifyButton.setVisible(not isEditable)
        self.ui.hyperlinkLabel.setVisible(not isEditable)
        self.ui.hyperlinkField.setVisible(isEditable)

    def fill_autocomplete_data(self,
                               fetch_func: Callable[[], list[str]],
                               text_field: QLineEdit
                               ) -> None:
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

    def refresh_interview_dates(self) -> None:
        """
        Clears and reloads the list of interviews for this specific application
        when the data has changed.
        :return:
        """
        self.interview_dates = get_interviews_for_application(self.currentFile,
                                                              self.app_id)

        self.ui.interviewsList.clear()
        for interview_date in self.interview_dates:
            self.ui.interviewsList.addItem(interview_date.date_str)

    def setCurrentFile(self, newFile: str) -> None:
        """
        Sets the current data file
        :param newFile: New data file
        :return:
        """
        self.currentFile = newFile

    @pyqtSlot()
    def newApplication(self) -> None:
        """
        Sets up and opens this dialog for entering a new application
        :return:
        """
        if self.privacy_filter:
            showWarningMessage(
                "Cannot add applications when the Privacy Filter is enabled.\n" +
                "Please disable the Privacy Filter to continue."
            )
            return
        self.ui.appDateWidget.hide()
        self.ui.interviewDatesWidget.hide()
        self.ui.appDeleteButton.hide()
        self.ui.DaysSinceAppliedWidget.hide()
        self.fill_data()
        self.app_info_type = self.AppInfoType.NEW
        self.setWindowTitle("New Application")
        self.exec()

    @pyqtSlot(Application)
    def editApplication(self, app: Application) -> None:
        """
        Opens this dialog and fills it with application data to edit an existing
        application.
        :param app: Application data
        :return:
        """
        if self.privacy_filter:
            showWarningMessage(
                "Cannot view individual applications or edit when the Privacy Filter is enabled.\n" +
                "Please disable the Privacy Filter to continue."
            )
            return
        self.ui.appDateWidget.show()
        self.ui.interviewDatesWidget.show()
        self.ui.appDeleteButton.show()
        self.ui.DaysSinceAppliedWidget.show()
        self.app_info_type = self.AppInfoType.EXISTING
        self.fill_data(app)
        self.refresh_interview_dates()
        job_title = shorten_string(app.title, 30)
        company = shorten_string(app.company, 30)
        self.setWindowTitle(f"Application Info - {job_title} at {company}")
        self.exec()

    @pyqtSlot()
    def app_submit(self) -> None:
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

        # Experience range input validation
        min_exp = None
        min_exp_input = self.ui.minExpField.text().strip()
        if min_exp_input != "":
            state, _, _ = self.ui.minExpField.validator().validate(min_exp_input, 0)

            if state != QIntValidator.State.Acceptable:
                showWarningMessage("Invalid input for minimum experience (Blank or between 0 and 50)")
                return

            min_exp = int(min_exp_input)

        max_exp = None
        max_exp_input = self.ui.maxExpField.text().strip()
        if max_exp_input != "":
            state, _, _ = self.ui.maxExpField.validator().validate(max_exp_input, 0)

            if state != QIntValidator.State.Acceptable:
                showWarningMessage("Invalid input for maximum experience (Blank or between 0 and 50)")
                return

            max_exp = int(max_exp_input)

        if min_exp is not None and max_exp is not None and min_exp >= max_exp:
            showWarningMessage("Minimum experience must be less than maximum experience.")
            return

        # Adds follow-up date only if the checkbox has been pressed.
        follow_up = ""
        if self.ui.followedUpCheckBox.isChecked():
            follow_up = self.ui.followUpField.date().toPyDate()

        rej_date = None
        if not self.ui.storeRejectionDateCheckbox.isChecked():
            rej_date = self.ui.rejectionDateEdit.date().toPyDate()

        # Chooses which function to call based on dialog state
        match self.app_info_type:

            case self.AppInfoType.NEW:
                add_application(
                    self.currentFile,
                    date.today(),
                    self.ui.companyField.text(),
                    self.ui.jobTitleField.text(),
                    self.ui.appFoundOnField.text(),
                    self.ui.appSiteField.text(),
                    self.ui.locationField.text(),
                    self.ui.materialsSent.text(),
                    self.ui.commentsField.toPlainText(),
                    self.ui.salaryField.text(),
                    self.ui.contactField.text(),
                    self.ui.statusField.currentIndex(),
                    self.ui.jobTypeField.currentIndex(),
                    self.ui.hyperlinkField.text(),
                    self.ui.jobDescriptionEdit.toHtml(),
                    min_exp,
                    max_exp,
                    rej_date,
                    follow_up
                )

            case self.AppInfoType.EXISTING:
                update_application(
                    self.currentFile,
                    self.app_id,
                    self.ui.companyField.text(),
                    self.ui.jobTitleField.text(),
                    self.ui.appFoundOnField.text(),
                    self.ui.appSiteField.text(),
                    self.ui.locationField.text(),
                    self.ui.materialsSent.text(),
                    self.ui.commentsField.toPlainText(),
                    self.ui.salaryField.text(),
                    self.ui.contactField.text(),
                    self.ui.statusField.currentIndex(),
                    self.ui.jobTypeField.currentIndex(),
                    self.ui.hyperlinkField.text(),
                    self.ui.jobDescriptionEdit.toHtml(),
                    min_exp,
                    max_exp,
                    rej_date,
                    self.ui.appDateEdit.date().toPyDate(),
                    follow_up
                )

        # Updates autocomplete data
        insert_companies(self.ui.companyField.text())
        insert_locations(self.ui.locationField.text())
        insert_app_sources(self.ui.appSiteField.text())
        insert_app_sources(self.ui.appFoundOnField.text())

        # Notifies that the table data has changed and closes the dialog
        self.table_updated.emit()
        self.close()

    @pyqtSlot()
    def interview_submit(self) -> None:
        """
        Function called when the interview date submit button is pressed.
        Submits the new date and refreshes the data.
        :return:
        """
        interview_date = self.ui.interviewDateField.date().toPyDate()
        add_interview_date(self.currentFile, self.app_id, interview_date)
        set_interview_status(self.currentFile, self.app_id)

        # Change placeholder text and index to show the interview status
        self.ui.statusField.setPlaceholderText(str(Status.INTERVIEW))
        self.ui.statusField.setCurrentIndex(-1)

        self.refresh_interview_dates()
        self.table_updated.emit()

    @pyqtSlot()
    def askDelete(self) -> None:
        """
        Shows a question dialog asking if the application should be deleted.
        :return:
        """
        showQuestionMessage("Do you wish to delete this application?",
                            "Delete application?",
                            self.delete
                            )

    @pyqtSlot()
    def delete(self) -> None:
        """
        Deletes the loaded application and notifies that the table data has been
        updated.
        :return:
        """
        delete_application(self.currentFile, self.app_id)
        self.table_updated.emit()
        self.close()

    @pyqtSlot(QPoint)
    def interview_list_ctx_menu(self, pos: QPoint) -> None:
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
            date_id = self.interview_dates[row].date_id

            delete_interview(self.currentFile, date_id)
            self.refresh_interview_dates()
            self.table_updated.emit()

