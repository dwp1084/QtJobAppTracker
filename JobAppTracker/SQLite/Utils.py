import sqlite3


class SQLiteRunner:
    def __init__(self, db_file):
        self.db_file = db_file

        try:
            self.fetch("PRAGMA schema_version;")
        except sqlite3.DatabaseError:
            raise IOError(f"{self.db_file} corrupted.")

    def run(self, query, params=()):
        with sqlite3.connect(self.db_file) as conn:
            conn.execute(query, params)
            conn.commit()

    def fetch(self, query, params=()):
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def run_script(self, script):
        with sqlite3.connect(self.db_file) as conn:
            conn.executescript(script)
            conn.commit()