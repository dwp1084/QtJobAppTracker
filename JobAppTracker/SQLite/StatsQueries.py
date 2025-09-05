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
        -- Builds a list of each month starting from the first one found in the
        -- data to the last one found
        WITH RECURSIVE months_list(month) AS (
            SELECT date(MIN(application_date), 'start of month')
            FROM applications
            UNION ALL
            SELECT date(month, '+1 month')
            FROM months_list
            WHERE month < (SELECT date(MAX(application_date), 
            'start of month') FROM applications)
        )
        -- Joins the list of months with the months found in the application
        -- table, then counts entries per each month
        SELECT strftime('%Y-%m', m.month) AS year_month,
        COUNT(a.application_date) AS app_count 
        FROM months_list AS m
        LEFT JOIN applications AS a
        ON strftime('%Y-%m', a.application_date) = year_month
        GROUP BY m.month
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
