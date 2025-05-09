import os.path
import sqlite3 as sql3

from SQLite.Utils import SQLiteRunner
from SQLite.Verifier import verify_sqlite

APP_FILES_DIR = "internal"
AUTOCOMPLETE_FILE = "autocomplete.sqlite"

CREATE_AUTOCOMPLETE_SQL = """
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS locations (
    location_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS app_sources (
    app_source_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);
"""


CREATE_DATAFILE_SQL = """
CREATE TABLE IF NOT EXISTS applications (
    app_id INTEGER PRIMARY KEY,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    application_date DATE NOT NULL DEFAULT (date('now')),
    latest_follow_up DATE NOT NULL DEFAULT '',
    location TEXT NOT NULL DEFAULT 'N/A',
    materials_sent TEXT NOT NULL DEFAULT '',
    comments TEXT NOT NULL DEFAULT '',
    salary TEXT NOT NULL DEFAULT '',
    contact TEXT NOT NULL DEFAULT '',
    status INTEGER NOT NULL DEFAULT 0 CHECK(status > -1 AND status < 5),
    type INTEGER NOT NULL DEFAULT 0 CHECK(type > -1 AND type < 4)
);

CREATE TABLE IF NOT EXISTS interview_dates (
    date_id INTEGER PRIMARY KEY,
    app_id INTEGER REFERENCES applications(app_id) ON UPDATE CASCADE,
    interview_date TEXT NOT NULL DEFAULT (date('now'))
);
"""


def init_autocomplete_file():
    if not os.path.exists(APP_FILES_DIR):
        os.mkdir(APP_FILES_DIR)

    ac_file = os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE)

    ac_file_runner = SQLiteRunner(ac_file)
    ac_file_runner.run_script(CREATE_AUTOCOMPLETE_SQL)


def init_data_file(filePath):
    data_file_runner = SQLiteRunner(filePath)
    data_file_runner.run_script(CREATE_DATAFILE_SQL)
