"""
Database connection — CareerIQ (SQLite version, Plan 2)
--------------------------------------------------------
Uses SQLite: a zero-install, single-file database built into Python.
No Docker, no Postgres server, nothing to start or maintain.

The whole database lives in one file: database/careeriq.db
That file is created automatically the first time you run init_db().

Row access works like a dict: row["title"], row["id"], etc. —
so the rest of the codebase doesn't need to change.
"""

import os
import sqlite3

# The database is a single file next to this script.
DB_PATH = os.path.join(os.path.dirname(__file__), "careeriq.db")


def get_connection():
    """Open a connection. Rows behave like dictionaries (row['column'])."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # lets us do row["title"]
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create all tables from schema.sql. Safe to run repeatedly."""
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        sql = f.read()
    conn = get_connection()
    try:
        conn.executescript(sql)     # executescript runs multiple statements
        conn.commit()
    finally:
        conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()
