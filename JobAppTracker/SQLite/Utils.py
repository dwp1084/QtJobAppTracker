import sqlite3
from abc import ABC, abstractmethod
from enum import StrEnum
from os import PathLike
from typing import LiteralString


class SQLiteRunner(ABC):
    """
    Provides utility functions for executing SQLite queries on db files.
    On creation, this class verifies that the file passed in is a valid
    SQLite database, otherwise throws an IOError.
    """
    def __init__(self, db_file: str | PathLike | LiteralString | bytes) -> None:
        self.db_file = db_file

        if not self.is_valid_sql:
            raise IOError(f"{self.db_file} corrupted.")

    @property
    def is_valid_sql(self) -> bool:
        """
        Runs a simple check to make sure the file that was opened is a SQLite
        format file.
        :return: True if valid SQLite, False if not
        """
        valid = True
        try:
            self.fetchone("PRAGMA schema_version;")
        except sqlite3.DatabaseError:
            valid = False

        return valid

    @property
    @abstractmethod
    def is_valid_format(self) -> bool: ...

    def _is_valid_format(self, *required_tables: str) -> bool:
        """
        Internal implementation for the valid format functions. Checks if the
        SQLite file contains all the tables it needs.
        :param required_tables: All required table names as strings
        :return: True if all required tables are present, false otherwise
        """
        try:
            tables = self.fetch(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
            table_set = {row[0] for row in tables}
            valid = set(required_tables).issubset(table_set)
        except sqlite3.DatabaseError:
            valid = False

        return valid

    def run(self, query: str, params: tuple = ()) -> None:
        """
        Runs a single modifying SQLite query, then commits the changes.
        :param query: A single modifying SQLite query
        :param params: A tuple consisting of any parameters to be inserted into
            the query in the order that they appear.
        :return:
        """
        with (sqlite3.connect(self.db_file,
                              detect_types=
                              sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
              as conn):
            conn.execute(query, params)
            conn.commit()

    def fetchone(self, query: str, params: tuple = ()) -> sqlite3.Row:
        """
        Runs a single SELECT SQLite query, then fetches only one returned
        result using the built-in row factory, useful for aggregate functions.
        :param query: A single SELECT SQLite query that only needs to return one
            result.
        :param params: A tuple consisting of any parameters to be inserted into
            the query in the order that they appear.
        :return: Results in a SQLite row object
        """
        with (sqlite3.connect(self.db_file,
                              detect_types=
                              sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
              as conn):
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch(self, query: str, params: tuple = ()) -> list[sqlite3.Row]:
        """
        Runs a single SELECT SQLite query, then fetches all returned
        results using the built-in row factory.
        :param query: A single SELECT SQLite query
        :param params: A tuple consisting of any parameters to be inserted into
            the query in the order that they appear.
        :return: Results in a SQLite row object
        """
        with (sqlite3.connect(self.db_file,
                              detect_types=
                              sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
              as conn):
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def run_script(self, script: str) -> None:
        """
        Runs a SQLite script without parameters, typically for creating
        database files.
        :param script: The SQLite script to run.
        :return:
        """
        with sqlite3.connect(self.db_file) as conn:
            conn.executescript(script)
            conn.commit()


class DataFileSQLRunner(SQLiteRunner):
    """
    SQLite runner for the data files of the application.
    """
    @property
    def is_valid_format(self) -> bool:
        """
        Checks if the data file contains all the tables it needs.
        :return: True if it contains the required tables, false otherwise
        """
        return super()._is_valid_format("applications", "interview_dates")


class AutocompleteTables(StrEnum):
    """
    A simple string enum mapping a data type to a database name.
    """
    COMPANIES = "companies",
    LOCATIONS = "locations",
    APP_SOURCES = "app_sources"


class ACFileSQLRunner(SQLiteRunner):
    """
    SQLite runner for the autocomplete file of the application.
    """
    @property
    def is_valid_format(self) -> bool:
        """
        Checks if the autocomplete file contains all the tables it needs.
        :return: True if it contains the required tables, false otherwise
        """
        return super()._is_valid_format(
            str(AutocompleteTables.COMPANIES),
            str(AutocompleteTables.LOCATIONS),
            str(AutocompleteTables.APP_SOURCES)
        )
