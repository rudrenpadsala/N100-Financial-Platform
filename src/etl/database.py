import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

SCHEMA_PATH = BASE_DIR / "db" / "schema.sql"


def create_database():

    conn = sqlite3.connect(DB_PATH)

    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()


    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        schema = file.read()


    cursor.executescript(schema)


    conn.commit()

    conn.close()


    print("=" * 60)
    print("SQLite Database Created Successfully")
    print("=" * 60)
    print(f"Database : {DB_PATH}")
    print("Foreign Keys Enabled")
    print("10 Tables Created")


if __name__ == "__main__":
    create_database()