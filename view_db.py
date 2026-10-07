import sqlite3
import pandas as pd
from pathlib import Path

# Path to SQLite database file
DB_FILE = Path(__file__).parent / "github_analytics.db"

def inspect_database():
    if not DB_FILE.exists():
        print(f"[ERROR] Database file '{DB_FILE}' does not exist yet! Run 'python src/database.py' first.")
        return

    print("==================================================")
    print("        SQLITE DATABASE INSPECTOR TOOL            ")
    print("==================================================")
    print(f"Database File: {DB_FILE.resolve()}\n")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if row[0] != "sqlite_sequence"]

    if not tables:
        print("[INFO] No tables found in database.")
        conn.close()
        return

    print(f"[INFO] Found {len(tables)} tables: {', '.join(tables)}\n")

    for tbl in sorted(tables):
        print(f"--------------------------------------------------")
        print(f"TABLE: {tbl}")
        print(f"--------------------------------------------------")
        
        # Count rows
        cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
        row_count = cursor.fetchone()[0]
        print(f"Total Rows: {row_count}")

        # Show first 5 rows using pandas dataframe formatting
        if row_count > 0:
            df = pd.read_sql_query(f"SELECT * FROM {tbl} LIMIT 5;", conn)
            print("\nPreview (First 5 Rows):")
            print(df.to_string(index=False))
        else:
            # Show schema column names if table is empty
            cursor.execute(f"PRAGMA table_info({tbl});")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns (Table Currently Empty): {', '.join(columns)}")
        print("\n")

    conn.close()
    print("==================================================")
    print("SUCCESS: Database inspection complete!")

if __name__ == "__main__":
    inspect_database()
