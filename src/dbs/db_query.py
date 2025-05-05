# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
from typing import List, Dict, Any

# Setup path and logging
FILE_LOCATION = f"{os.path.dirname(__file__)}/pull_from_table.py"

try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)

    from logs import log_debug, log_error, log_info
except Exception as e:
    raise ImportError(f"Import Error in {FILE_LOCATION}: {e}")

def fetch_all_rows(
    conn: sqlite3.Connection,
    table_name: str,
    columns: List[str],
    rely_data: str = "text"
) -> List[Dict[str, Any]]:
    """
    Pulls data from a specified table in the SQLite database.

    Args:
        conn (sqlite3.Connection): SQLite connection.
        table_name (str): Target table to pull from.
        columns (List[str]): List of columns to select.
        rely_data (str): Label key for the first selected column.

    Returns:
        List[Dict[str, Any]]: List of records with 'id' and selected data.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT {', '.join(columns)} FROM {table_name}")
        rows = cursor.fetchall()

        log_info(f"Pulled {len(rows)} row(s) from table '{table_name}'.")

        result = [
            {"id": row[1], rely_data: row[0]} for row in rows
        ]

        return result

    except Exception as e:
        log_error(f"Failed to pull data from '{table_name}': {e}")
        return []
    finally:
        log_debug("Executed pull_from_table.")
