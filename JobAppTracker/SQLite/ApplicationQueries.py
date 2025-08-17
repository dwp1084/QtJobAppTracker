import datetime
from typing import cast

from Data.Application import Application, JobTypes, Status
from Data.InterviewDate import InterviewDate
from SQLite.Utils import DataFileSQLRunner


def add_application(data_db: str,
                    applied_date: datetime.date,
                    company: str,
                    title: str,
                    applied_at: str,
                    location: str,
                    materials_sent: str,
                    comments: str,
                    salary: str,
                    contact: str,
                    status: int,
                    job_type: int,
                    follow_up: datetime.date | str = ""
                    ) -> None:
    """
    Inserts a new job application into the database.
    :param data_db: Database file
    :param applied_date: Application date
    :param company: Company name
    :param title: Job title
    :param applied_at: Website or place where I applied
    :param location: Job location if not remote
    :param materials_sent: Materials sent to the company
    :param comments: Comments about the job position
    :param salary: Posted salary information
    :param contact: Contact info
    :param status: Application status
    :param job_type: Job type (remote, in-person, hybrid)
    :param follow_up: Latest follow-up date
    :return:
    """
    add_app_sql = """
    INSERT INTO applications (company, title, applied_at, latest_follow_up, 
    location, materials_sent, comments, salary,  contact, status, type, 
    application_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    db = DataFileSQLRunner(data_db)

    params = (company, title, applied_at, follow_up, location, materials_sent,
              comments, salary, contact, status, job_type, applied_date)
    db.run(add_app_sql, params)


def update_application(data_db: str,
                       app_id: int,
                       company: str,
                       title: str,
                       applied_at: str,
                       location: str,
                       materials_sent: str,
                       comments: str,
                       salary: str,
                       contact: str,
                       status: int,
                       job_type: int,
                       follow_up: datetime.date | str = ""
                       ) -> None:
    """
    Updates the main fields of an application in the database.
    :param data_db: Database file
    :param app_id: Job application ID from database
    :param company: Company name
    :param title: Job title
    :param applied_at: Website or place where I applied
    :param location: Job location if not remote
    :param materials_sent: Materials sent to the company
    :param comments: Comments about the job position
    :param salary: Posted salary information
    :param contact: Contact info
    :param status: Application status
    :param job_type: Job type (remote, in-person, hybrid)
    :param follow_up: Latest follow-up date
    :return:
    """
    update_app_sql = """
    UPDATE applications 
    SET company = ?,
        title = ?,
        applied_at = ?,
        latest_follow_up = ?,
        location = ?,
        materials_sent = ?,
        comments = ?,
        salary = ?,
        contact = ?,
        status = ?,
        type = ?
    WHERE app_id = ?;
    """
    db = DataFileSQLRunner(data_db)
    params = (company, title, applied_at, follow_up, location, materials_sent,
              comments, salary, contact, status, job_type, app_id)
    db.run(update_app_sql, params)


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


def get_applications(data_db: str) -> list[Application]:
    """
    Grab a list of all job application data.
    :param data_db: Database file
    :return: Applications data
    """
    retrieve_apps_sql = """
    SELECT app_id, company, title, applied_at, application_date, 
    latest_follow_up, location, materials_sent, comments, salary, contact, 
    status, type FROM applications ORDER BY date(application_date) DESC;
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
                               data_dict["applied_at"],
                               data_dict["contact"],
                               data_dict["materials_sent"],
                               data_dict["salary"],
                               Status(data_dict["status"]),
                               data_dict["comments"])

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
