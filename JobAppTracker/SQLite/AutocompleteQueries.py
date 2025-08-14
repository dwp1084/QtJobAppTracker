import os.path
from enum import StrEnum

from SQLite.Initializer import AUTOCOMPLETE_FILE, APP_FILES_DIR
from SQLite.Utils import SQLiteRunner


class AutocompleteTables(StrEnum):
    """
    A simple string enum mapping a data type to a database name.
    """
    COMPANIES = "companies",
    LOCATIONS = "locations",
    APP_SOURCES = "app_sources"


def autocomplete_companies():
    """
    Autocomplete wrapper function for companies.
    :return: Autocomplete data
    """
    return _autocomplete(AutocompleteTables.COMPANIES)


def autocomplete_locations():
    """
        Autocomplete wrapper function for locations.
        :return: Autocomplete data
        """
    return _autocomplete(AutocompleteTables.LOCATIONS)


def autocomplete_app_sources():
    """
        Autocomplete wrapper function for application websites.
        :return: Autocomplete data
        """
    return _autocomplete(AutocompleteTables.APP_SOURCES)


def _autocomplete(table_name):
    """
    Internally used autocomplete function that gets a list from an autocomplete
    table and returns it.
    :param table_name: Table name to get data from
    :return: Autocomplete data
    """
    get_ac_sql = f"SELECT name FROM {table_name.value};"
    ac_runner = SQLiteRunner(os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE))
    results = ac_runner.fetch(get_ac_sql)

    # Return results as a list
    ac_list = []
    for result in results:
        ac_list.append(dict(result)["name"])

    return ac_list


def insert_companies(value):
    """
    Wrapper function for adding autocomplete data into the companies table.
    :param value: New data. If the data already exists, it will be ignored.
    :return:
    """
    _insert_ac(AutocompleteTables.COMPANIES, value)


def insert_locations(value):
    """
        Wrapper function for adding autocomplete data into the locations table.
        :param value: New data. If the data already exists, it will be ignored.
        :return:
        """
    _insert_ac(AutocompleteTables.LOCATIONS, value)


def insert_app_sources(value):
    """
        Wrapper function for adding autocomplete data into the application
        websites table.
        :param value: New data. If the data already exists, it will be ignored.
        :return:
        """
    _insert_ac(AutocompleteTables.APP_SOURCES, value)


def _insert_ac(table_name, value):
    """
    Internally used function for inserting data into autocomplete tables. This
    will insert the value into the table if it's not already in there.
    Otherwise, the data will be ignored.
    :param table_name: Table to insert data into
    :param value: New data. If the data already exists, it will be ignored.
    :return:
    """
    insert_ac_sql = f"INSERT OR IGNORE INTO {table_name.value} ( name ) VALUES (?);"
    ac_runner = SQLiteRunner(os.path.join(APP_FILES_DIR, AUTOCOMPLETE_FILE))
    ac_runner.run(insert_ac_sql, (value,))

