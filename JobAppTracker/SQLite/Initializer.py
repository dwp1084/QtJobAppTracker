import os.path
import sqlite3 as s3

APP_FILES_DIR = "internal"
AUTOCOMPLETE_FILE = "autocomplete.sqlite"

CREATE_AUTOCOMPLETE_SQL = """
CREATE TABLE IF NOT EXISTS company (
    company_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS location (
    location_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS app_source (
    app_source_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
"""


def init_autocomplete_file():
    if not os.path.exists(APP_FILES_DIR):
        os.mkdir(APP_FILES_DIR)

    ac_file = os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE)
    conn = s3.connect(ac_file)

    try:
        cursor = conn.cursor()
        cursor.executescript(CREATE_AUTOCOMPLETE_SQL)
        conn.commit()
        print("Initialized autocomplete db")
    finally:
        conn.close()
