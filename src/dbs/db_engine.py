import os
import sys
import sqlite3
from pathlib import Path  # Better path handling

# Debugging setup
FILE_LOCATION = Path(__file__).absolute()
log_header = f"[SQLite Engine] {FILE_LOCATION.name}:"

# Add root dir and handle potential import errors
try:
    MAIN_DIR = Path(__file__).parent.parent.absolute()
    sys.path.append(str(MAIN_DIR))

    from logs import log_debug, log_error, log_info
    from helpers import get_settings, Settings
except Exception as e:
    msg = f"{log_header} Import Error: {str(e)}"
    raise ImportError(msg)

app_setting: Settings = get_settings()


def get_sqlite_engine():
    """
    Creates a connection to an SQLite database.
    If the database does not exist, it will be created.
    """
    try:
        db_path = Path(app_setting.SQLITE_DB)
        parent_dir = db_path.parent

        # Debugging output
        log_debug(f"{log_header} Checking database path: {db_path}")
        log_debug(f"{log_header} Parent directory: {parent_dir}")
        log_debug(f"{log_header} Parent exists: {parent_dir.exists()}")
        log_debug(f"{log_header} Parent writable: {os.access(parent_dir, os.W_OK)}")

        # Ensure directory exists
        parent_dir.mkdir(parents=True, exist_ok=True)

        # Debug connection string
        conn_str = f"file:{db_path}?mode=rwc"
        log_debug(f"{log_header} Connection string: {conn_str}")

        # Create connection with URI for better handling
        conn = sqlite3.connect(conn_str, uri=True)

        # Test connection
        with conn:
            conn.execute("SELECT 1")

        log_info(f"{log_header} Successfully connected to: {db_path}")
        return conn

    except sqlite3.Error as e:
        error_msg = f"{log_header} Database connection failed to {db_path}: {str(e)}"
        log_error(error_msg)
        raise RuntimeError(error_msg) from e
    except Exception as e:
        error_msg = f"{log_header} Unexpected error: {str(e)}"
        log_error(error_msg)
        raise RuntimeError(error_msg) from e
