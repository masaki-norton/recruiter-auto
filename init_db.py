import sqlite3
import os

def init_db(db_path="candidate.db"):
    """Initialize the database with the schema"""
    with sqlite3.connect(db_path) as conn:
        with open('schema.sql', 'r') as f:
            conn.executescript(f.read())
        print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    init_db()
