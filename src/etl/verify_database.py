import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "db" / "nifty100.db"

conn = sqlite3.connect(DB_PATH)

tables = pd.read_sql(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn
)

print("=" * 60)
print("TABLE ROW COUNTS")
print("=" * 60)

for table in tables["name"]:

    count = pd.read_sql(
        f"SELECT COUNT(*) AS rows FROM {table}",
        conn
    )

    print(f"{table:20} {count.iloc[0,0]}")

print("\n")

print("=" * 60)
print("FOREIGN KEY CHECK")
print("=" * 60)

fk = pd.read_sql(
    "PRAGMA foreign_key_check;",
    conn
)

if fk.empty:
    print("✔ No Foreign Key Violations")
else:
    print(fk)

conn.close()