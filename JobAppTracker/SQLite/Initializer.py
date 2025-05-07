import os.path
import sqlite3 as sql3

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


def init_autocomplete_file():
    if not os.path.exists(APP_FILES_DIR):
        os.mkdir(APP_FILES_DIR)

    ac_file = os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE)

    if not verify_sqlite(ac_file):
        raise IOError(f"Autocomplete file {ac_file} corrupted. Restore or delete the file to fix.")

    conn = sql3.connect(ac_file)

    try:
        cursor = conn.cursor()
        cursor.executescript(CREATE_AUTOCOMPLETE_SQL)
        conn.commit()
    finally:
        conn.close()
