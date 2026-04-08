from collections.abc import Callable

from SQLite.ApplicationQueries import set_app_file_version
from SQLite.Utils import DataFileSQLRunner
from constants import CURRENT_DATA_FILE_VERSION

MigrationFunc = Callable[[str], None]


class SchemaMigrationException(Exception):
    """Exception wrapper for exceptions that occur during schema migration."""
    pass


# Automatically register migration functions going from one version
# to the next
MIGRATIONS: dict[int, MigrationFunc] = {}


def migration_from(from_version: int):
    """
    Registers a function as a schema migration function
    :param from_version: Version that the function migrates the data file from
    :return:
    """
    def decorator(fn: MigrationFunc):
        MIGRATIONS[from_version] = fn
        return fn
    return decorator


@migration_from(0)
def v0_to_v1(db_name: str):
    update_sql_file_sql = """
    ALTER TABLE applications ADD COLUMN link TEXT NOT NULL DEFAULT '';
    ALTER TABLE applications ADD COLUMN description TEXT NOT NULL DEFAULT '';
    ALTER TABLE applications ADD COLUMN rej_date DATE;
    ALTER TABLE applications ADD COLUMN exp_low INTEGER;
    ALTER TABLE applications ADD COLUMN exp_upp INTEGER;
    
    CREATE TABLE documents (
        doc_id INTEGER PRIMARY KEY,
        app_id INTEGER REFERENCES applications(app_id) ON UPDATE CASCADE,
        doc_name TEXT NOT NULL,
        doc BLOB NOT NULL
    );
    """
    db = DataFileSQLRunner(db_name)
    db.run_script(update_sql_file_sql)


def migrate_file(db_file_path: str, file_version: int):
    """
    Attempts to migrate a data file from whatever version it currently is up to
    the current version.
    :param db_file_path: Path to the database file to migrate
    :param file_version: Database file's current version
    :return:
    """
    while file_version < CURRENT_DATA_FILE_VERSION:
        if file_version not in MIGRATIONS:
            raise SchemaMigrationException(
                f"No migration found for version {file_version}."
            )
        migration_func = MIGRATIONS[file_version]
        try:
            migration_func(db_file_path)
            set_app_file_version(db_file_path, file_version+1)
        except Exception as e:
            raise SchemaMigrationException(
                f"Migration from {file_version} to {file_version+1} failed: {e}"
            ) from e

        file_version += 1