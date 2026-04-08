import datetime
from typing import cast

from Data.Application import Application, JobTypes, Status
from Data.InterviewDate import InterviewDate
from SQLite.Utils import DataFileSQLRunner

APP_DAT_THRESHOLD = 21
"""
Threshold, in days after application date, for ghosting prediction.
"""

FOLLOW_UP_THRESHOLD = 7
"""
Threshold, in days after follow-up date, for ghosting prediction.
"""

INTERVIEW_THRESHOLD = 90
"""
Threshold, in days after latest interview date, for ghosting prediction.
"""

def add_application(data_db: str,
                    applied_date: datetime.date,
                    company: str,
                    title: str,
                    app_found_at: str,
                    applied_at: str,
                    location: str,
                    materials_sent: str,
                    comments: str,
                    salary: str,
                    contact: str,
                    status: int,
                    job_type: int,
                    link: str,
                    description: str,
                    exp_low: int | None,
                    exp_upp: int | None,
                    rej_date: datetime.date | None,
                    follow_up: datetime.date | str = "",
                    ) -> None:
    """
    Inserts a new job application into the database.
    :param data_db: Database file
    :param applied_date: Application date
    :param company: Company name
    :param title: Job title
    :param app_found_at: Website or place where I found the application
    :param applied_at: Website or place where I applied
    :param location: Job location if not remote
    :param materials_sent: Materials sent to the company
    :param comments: Comments about the job position
    :param salary: Posted salary information
    :param contact: Contact info
    :param status: Application status
    :param job_type: Job type (remote, in-person, hybrid)
    :param link: Link to the application
    :param description: Rich-text job description
    :param exp_low: Lower bound for years of experience
    :param exp_upp: Upper bound for years of experience
    :param rej_date: Rejection date
    :param follow_up: Latest follow-up date
    :return:
    """
    add_app_sql = """
    INSERT INTO applications (company, title, app_found_at, applied_at, 
    latest_follow_up, location, materials_sent, comments, salary,  contact, 
    status, type, application_date, link, description, exp_low, exp_upp, rej_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    db = DataFileSQLRunner(data_db)

    params = (company, title, app_found_at, applied_at, follow_up, location,
              materials_sent, comments, salary, contact, status, job_type,
              applied_date, link, description, exp_low, exp_upp, rej_date)
    db.run(add_app_sql, params)


def update_application(data_db: str,
                       app_id: int,
                       company: str,
                       title: str,
                       app_found_at: str,
                       applied_at: str,
                       location: str,
                       materials_sent: str,
                       comments: str,
                       salary: str,
                       contact: str,
                       status: int,
                       job_type: int,
                       link: str,
                       description: str,
                       exp_low: int | None,
                       exp_upp: int | None,
                       rej_date: datetime.date | None,
                       app_date: datetime.date,
                       follow_up: datetime.date | str = ""
                       ) -> None:
    """
    Updates the main fields of an application in the database. If an invalid
    index is used for status, then it will not be updated in the database.
    :param data_db: Database file
    :param app_id: Job application ID from database
    :param company: Company name
    :param title: Job title
    :param app_found_at: Website or place where I found the application
    :param applied_at: Website or place where I applied
    :param location: Job location if not remote
    :param materials_sent: Materials sent to the company
    :param comments: Comments about the job position
    :param salary: Posted salary information
    :param contact: Contact info
    :param status: Application status
    :param job_type: Job type (remote, in-person, hybrid)
    :param link: Link to the application
    :param description: Rich-text job description
    :param exp_low: Lower bound for years of experience
    :param exp_upp: Upper bound for years of experience
    :param rej_date: Rejection date
    :param app_date: Application date
    :param follow_up: Latest follow-up date
    :return:
    """
    update_without_status_sql = """
    UPDATE applications 
    SET company = ?,
        title = ?,
        app_found_at = ?,
        applied_at = ?,
        latest_follow_up = ?,
        location = ?,
        materials_sent = ?,
        comments = ?,
        salary = ?,
        contact = ?,
        type = ?,
        link = ?,
        description = ?,
        exp_low = ?,
        exp_upp = ?,
        rej_date = ?,
        application_date = ?
    WHERE app_id = ?;
    """

    update_full_app_sql = """
    UPDATE applications 
    SET company = ?,
        title = ?,
        app_found_at = ?,
        applied_at = ?,
        latest_follow_up = ?,
        location = ?,
        materials_sent = ?,
        comments = ?,
        salary = ?,
        contact = ?,
        status = ?,
        type = ?,
        link = ?,
        description = ?,
        exp_low = ?,
        exp_upp = ?,
        rej_date = ?,
        application_date = ?
    WHERE app_id = ?;
    """

    if status < 0:
        sql_query = update_without_status_sql
        params = (company, title, app_found_at, applied_at, follow_up, location,
                  materials_sent, comments, salary, contact, job_type, link,
                  description, exp_low, exp_upp,  rej_date, app_date, app_id)
    else:
        sql_query = update_full_app_sql
        params = (company, title, app_found_at, applied_at, follow_up, location,
                  materials_sent, comments, salary, contact, status, job_type,
                  link, description, exp_low, exp_upp, rej_date, app_date,
                  app_id)

    db = DataFileSQLRunner(data_db)
    db.run(sql_query, params)


def add_interview_date(data_db: str, app_id: int, date: datetime.date) -> None:
    """
    Add an interview date into the database.
    :param data_db: Database file
    :param app_id: Application ID
    :param date: Interview date
    :return:
    """
    add_interview_sql = """
    INSERT INTO interview_dates (app_id, interview_date) VALUES (?, ?);
    """

    db = DataFileSQLRunner(data_db)
    params = (app_id, date)
    db.run(add_interview_sql, params)


def set_interview_status(data_db: str, app_id: int) -> None:
    """
    Sets an application status to "interview" in the database.
    :param data_db: Database file
    :param app_id: Application ID
    :return:
    """
    set_status_sql = """
    UPDATE applications SET status = ? WHERE app_id = ?;
    """

    db = DataFileSQLRunner(data_db)
    params = (int(Status.INTERVIEW), app_id)
    db.run(set_status_sql, params)


def get_applications(data_db: str) -> list[Application]:
    """
    Grab a list of all job application data.
    :param data_db: Database file
    :return: Applications data
    """
    retrieve_apps_sql = """
    SELECT app_id, company, title, app_found_at, applied_at, application_date, 
    latest_follow_up, location, materials_sent, comments, salary, contact, 
    status, type, link, description, rej_date, exp_low, exp_upp FROM 
    applications ORDER BY date(application_date) DESC;
    """
    db = DataFileSQLRunner(data_db)

    data = db.fetch(retrieve_apps_sql)

    apps_list = []

    for row in data:
        data_dict = dict(row)

        # Purely for type checking purposes, the data coming from SQL is
        # already the date type.
        app_date = cast(datetime.date, data_dict["application_date"])
        follow_up = cast(datetime.date, data_dict["latest_follow_up"])

        app_data = Application(int(data_dict["app_id"]),
                               data_dict["company"],
                               data_dict["title"],
                               app_date,
                               follow_up,
                               JobTypes(data_dict["type"]),
                               data_dict["location"],
                               data_dict["app_found_at"],
                               data_dict["applied_at"],
                               data_dict["contact"],
                               data_dict["materials_sent"],
                               data_dict["salary"],
                               Status(data_dict["status"]),
                               data_dict["comments"],
                               data_dict["link"],
                               data_dict["description"],
                               data_dict["rej_date"],
                               data_dict["exp_low"],
                               data_dict["exp_upp"])

        apps_list.append(app_data)

    return apps_list


def get_interviews_for_application(data_db: str,
                                   app_id: int
                                   ) -> list[InterviewDate]:
    """
    Grab a list of all interview dates for a specific application.
    :param data_db: Database file
    :param app_id: Application ID
    :return: List of interview dates
    """
    get_interviews_sql = """
    SELECT date_id, interview_date FROM interview_dates WHERE app_id = ? 
    ORDER BY interview_date DESC;
    """
    db = DataFileSQLRunner(data_db)

    data = db.fetch(get_interviews_sql, (app_id,))

    interviews_list = []

    for row in data:
        data_dict = dict(row)

        interviews_list.append(InterviewDate(
            data_dict["date_id"],
            datetime.date.fromisoformat(data_dict["interview_date"])
        ))

    return interviews_list


def days_since_last_interview(data_db: str,
                              app_id: int
                              ) -> int:
    """
    Gets the number of days that has passed since the last interview
    :param data_db: Database file
    :param app_id: Application ID
    :return: Number of days, or -1 if no interview dates were found
    """
    get_interviews_sql = """
    SELECT interview_date FROM interview_dates WHERE app_id = ? 
    ORDER BY interview_date DESC;
    """
    db = DataFileSQLRunner(data_db)

    data = db.fetchone(get_interviews_sql, (app_id,))

    if data is not None:
        latest_interview = datetime.date.fromisoformat(data[0])
        return (datetime.date.today() - latest_interview).days

    return -1  # If there is no date available, return arbitrary number


def ghost_prediction(data_db: str, app: Application) -> Status:
    """
    Predicts if an application is likely to have been ghosted using set
    thresholds from the application date, latest follow-up, and latest interview
    :param data_db: Database file
    :param app: Application
    :return: Updated status, including if the application has been likely ghosted
    """
    past_follow_up_threshold = True if app.followed_up is None \
        else ((datetime.date.today() - app.followed_up).days
              > FOLLOW_UP_THRESHOLD)

    match app.status:
        case Status.PENDING:
            past_app_threshold = ((datetime.date.today() - app.applied_on).days
                                  > APP_DAT_THRESHOLD)

            return Status.LIKELY_GHOSTED if (past_app_threshold and
                                             past_follow_up_threshold) \
                else app.status
        case Status.INTERVIEW:
            last_int = days_since_last_interview(data_db, app.app_id)

            return Status.LIKELY_GHOSTED if (last_int > INTERVIEW_THRESHOLD and
                                             past_follow_up_threshold) \
                else app.status
        case _:
            return app.status


def get_interview_count_for_application(data_db: str, app_id: int) -> int:
    """
    Gets the number of interviews tied to a specific application.
    :param data_db: Database file
    :param app_id: Application ID
    :return: Number of interviews
    """
    get_interviews_count_sql = """
    SELECT COUNT(*) FROM interview_dates WHERE app_id = ?;
    """
    db = DataFileSQLRunner(data_db)

    return db.fetchone(get_interviews_count_sql, (app_id,))[0]


def delete_interview(data_db: str, date_id: int) -> None:
    """
    Delete an interview from the database.
    :param data_db: Database file
    :param date_id: Interview date ID
    :return:
    """
    delete_interview_sql = """
    DELETE FROM interview_dates WHERE date_id = ?;
    """
    db = DataFileSQLRunner(data_db)
    db.run(delete_interview_sql, (date_id,))


def delete_application(data_db: str, app_id: int) -> None:
    """
    Delete an application from the database.
    :param data_db: Database file
    :param app_id: Application ID
    :return:
    """
    delete_app_sql = """
    DELETE FROM applications WHERE app_id = ?;
    """
    db = DataFileSQLRunner(data_db)
    db.run(delete_app_sql, (app_id,))

def get_app_file_version(data_db: str) -> int:
    """
    Gets the version number of the database.
    :param data_db: Database file
    :return: Version number
    """

    get_version_num_sql = "PRAGMA user_version;"
    db = DataFileSQLRunner(data_db)
    return db.fetchone(get_version_num_sql, ())[0]

def set_app_file_version(data_db: str, version: int) -> None:
    """
    Gets the version number of the database.
    :param data_db: Database file
    :param version: New app version
    :return:
    """

    get_version_num_sql = f"PRAGMA user_version = {version};"
    db = DataFileSQLRunner(data_db)
    db.run(get_version_num_sql)