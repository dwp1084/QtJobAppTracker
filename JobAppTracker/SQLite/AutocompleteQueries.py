import os.path
from enum import StrEnum

from SQLite.Initializer import AUTOCOMPLETE_FILE, APP_FILES_DIR
from SQLite.Utils import SQLiteRunner


class AutocompleteTables(StrEnum):
    COMPANIES = "companies",
    LOCATIONS = "locations",
    APP_SOURCES = "app_sources"


def autocomplete_companies():
    return _autocomplete(AutocompleteTables.COMPANIES)


def autocomplete_locations():
    return _autocomplete(AutocompleteTables.LOCATIONS)


def autocomplete_app_sources():
    return _autocomplete(AutocompleteTables.APP_SOURCES)


def _autocomplete(table_name):
    get_ac_sql = f"SELECT name FROM {table_name.value};"
    ac_runner = SQLiteRunner(os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE))
    results = ac_runner.fetch(get_ac_sql)

    # Return results as a list
    ac_list = []
    for result in results:
        ac_list.append(dict(result)["name"])

    return ac_list


def insert_companies(value):
    _insert_ac(AutocompleteTables.COMPANIES, value)


def insert_locations(value):
    _insert_ac(AutocompleteTables.LOCATIONS, value)


def insert_app_sources(value):
    _insert_ac(AutocompleteTables.APP_SOURCES, value)


def _insert_ac(table_name, value):
    insert_ac_sql = f"INSERT OR IGNORE INTO {table_name.value} ( name ) VALUES (?);"
    ac_runner = SQLiteRunner(os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE))
    ac_runner.run(insert_ac_sql, (value,))

