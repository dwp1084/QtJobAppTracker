from SQLite.Utils import SQLiteRunner


def add_application(data_db,
                    company,
                    title,
                    applied_at,
                    location,
                    materials_sent,
                    comments,
                    salary,
                    contact,
                    status,
                    job_type,
                    follow_up=""):
    """
    Inserts a new application into the database
    :param data_db:
    :param company:
    :param title:
    :param applied_at:
    :param location:
    :param materials_sent:
    :param comments:
    :param salary:
    :param contact:
    :param status:
    :param job_type:
    :param follow_up:
    :return:
    """
    add_app_sql = """
    INSERT INTO applications (company, title, applied_at, latest_follow_up, location, materials_sent, comments, salary, 
    contact, status, type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """

    db = SQLiteRunner(data_db)

    params = (company, title, applied_at, follow_up, location, materials_sent, comments, salary, contact, status,
              job_type)
    db.run(add_app_sql, params)


def update_application(data_db,
                       app_id,
                       company,
                       title,
                       applied_at,
                       location,
                       materials_sent,
                       comments,
                       salary,
                       contact,
                       status,
                       job_type,
                       follow_up=""):
    """
    Updates the main fields of an application in the database
    :param data_db:
    :param app_id:
    :param company:
    :param title:
    :param applied_at:
    :param location:
    :param materials_sent:
    :param comments:
    :param salary:
    :param contact:
    :param status:
    :param job_type:
    :param follow_up:
    :return:
    """
    update_app_sql = """
    UPDATE applications 
    SET company = ?,
        title = ?,
        applied_at = ?,
        follow_up = ?,
        location = ?,
        materials_sent = ?,
        comments = ?,
        salary = ?,
        contact = ?,
        status = ?,
        type = ?
    WHERE app_id = ?;
    """
    db = SQLiteRunner(data_db)
    params = (company, title, applied_at, follow_up, location, materials_sent, comments, salary, contact, status,
              job_type, app_id)
    db.run(update_app_sql, params)


def add_interview_date(data_db, app_id, date):
    add_interview_sql = """
    INSERT INTO interview_dates (app_id, interview_date) VALUES (?, ?);
    """

    db = SQLiteRunner(data_db)
    params = (app_id, date)
    db.run(add_interview_sql, params)


def get_applications(data_db):
    retrieve_apps_sql = """
    SELECT app_id, company, title, applied_at, application_date, latest_follow_up, location, materials_sent, comments, salary, 
    contact, status, type FROM applications ORDER BY date(application_date) DESC;
    """
    db = SQLiteRunner(data_db)

    return db.fetch(retrieve_apps_sql)
