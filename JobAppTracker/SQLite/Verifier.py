import sqlite3 as sql3

def verify_sqlite(filename):
    """
    Helper function that verifies a file is a SQLite format file by issuing a simple pre-check query.
    :param filename:
    :return:
    """
    valid = True
    conn = sql3.connect(filename)
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA schema_version;")
    except sql3.DatabaseError:
        valid = False
    finally:
        conn.close()

    return valid


def check_job_app_sqlite(filename):
    REQUIRED_TABLES = {"applications", "interview_dates"}

    conn = sql3.connect(filename)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = {row[0] for row in cursor.fetchall()}
        valid = REQUIRED_TABLES.issubset(existing_tables)
    except sql3.DatabaseError:
        valid = False
    finally:
        conn.close()

    return valid
