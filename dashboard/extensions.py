import re

from flask_htmx import HTMX
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

db = SQLAlchemy()
htmx = HTMX()
login_manager = LoginManager()


@event.listens_for(Engine, "connect")
def configure_sqlite(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    # Enable the SpatiaLite extension for SQLite
    dbapi_connection.enable_load_extension(True)
    cursor.execute("SELECT load_extension('mod_spatialite')")
    # Register a custom SQL function for regular expression matching
    dbapi_connection.create_function(
        "regexp", 2, lambda x, y: 1 if re.search(x, y) else 0
    )
    # Enables write-ahead log so that your reads do not block writes and vice-versa.
    cursor.execute("PRAGMA journal_mode = WAL")
    # Sqlite will wait 5 seconds to obtain a lock before returning SQLITE_BUSY errors, which will significantly reduce them.
    cursor.execute("PRAGMA busy_timeout = 5000")
    # Sqlite will sync less frequently and be more performant, still safe to use because of the enabled WAL mode.
    cursor.execute("PRAGMA synchronous = NORMAL")
    # Negative number means kilobytes, in this case 20MB of memory for cache.
    cursor.execute("PRAGMA cache_size = -20000")
    # Moves temporary tables from disk into RAM, speeds up performance a lot.
    cursor.execute("PRAGMA temp_store = memory")

    cursor.close()
