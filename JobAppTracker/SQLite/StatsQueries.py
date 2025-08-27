from SQLite.Utils import DataFileSQLRunner


def get_total_ints(data_db: str) -> int:
    """
    Gets total number of interviews.
    :param data_db: Database file
    :return: Total interview count
    """

    get_interview_count_sql = """
    SELECT COUNT(*) FROM interview_dates;
    """

    db = DataFileSQLRunner(data_db)

    return db.fetchone(get_interview_count_sql)[0]


def get_avg_apps_per_month(data_db: str) -> float:
    """
    Gets the average number of applications sent per month.
    :param data_db: Database file
    :return: Average number of applications per month
    """
    get_avg_apps_sql = """
    SELECT AVG(app_count)
    FROM (
        SELECT strftime('%Y-%m', application_date) AS year_month,
        COUNT(*) AS app_count
        FROM applications
        GROUP BY year_month
    );
    """

    db = DataFileSQLRunner(data_db)

    return db.fetchone(get_avg_apps_sql)[0]


def get_avg_ints_and_count(data_db: str) -> tuple[int, float]:
    """
    Gets the total number of applications that have had interviews, as well as
    the average number of interviews that each application has had.
    :param data_db: Database file
    :return: Number of applications w/ interviews and avg. number of interviews
    """
    get_avg_ints_and_count_sql = """
    SELECT COUNT(*) AS jobs_interviewed, AVG(interview_count) AS avg_int_count
    FROM (
        SELECT app_id, COUNT(*) AS interview_count
        FROM interview_dates
        GROUP BY app_id
    );
    """

    db = DataFileSQLRunner(data_db)

    result = db.fetchone(get_avg_ints_and_count_sql)
    res_dict = dict(result)

    return res_dict["jobs_interviewed"], res_dict["avg_int_count"]
