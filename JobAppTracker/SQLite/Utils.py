import sqlite3


class SQLiteRunner:
    """
    Provides utility functions for executing SQLite queries on db files.
    On creation, this class verifies that the file passed in is a valid
    SQLite database, otherwise throws an IOError.
    """
    def __init__(self, db_file):
        self.db_file = db_file

        try:
            self.fetch("PRAGMA schema_version;")
        except sqlite3.DatabaseError:
            raise IOError(f"{self.db_file} corrupted.")

    def run(self, query, params=()):
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

    def fetchone(self, query, params=()):
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

    def fetch(self, query, params=()):
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

    def run_script(self, script):
        """
        Runs a SQLite script without parameters, typically for creating
        database files.
        :param script: The SQLite script to run.
        :return:
        """
        with sqlite3.connect(self.db_file) as conn:
            conn.executescript(script)
            conn.commit()
