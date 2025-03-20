import sqlite3
import os
from contextlib import closing

def init_db(db_path="candidate.db"):
    """Initialize the database with the schema"""
    # Delete existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Existing database deleted: {db_path}")

    # Create new empty database
    with closing(sqlite3.connect(db_path)) as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        print(f"Database initialized: {db_path}")

if __name__ == "__main__":
    init_db()
