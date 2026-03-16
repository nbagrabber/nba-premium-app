import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def check_db():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- Checking tables in {db_path} ---")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        if ('predictions',) in tables:
            print("\n--- Columns in 'predictions' table ---")
            cursor.execute("PRAGMA table_info(predictions);")
            cols = cursor.fetchall()
            for col in cols:
                print(f"ID: {col[0]}, Name: {col[1]}, Type: {col[2]}")
        else:
            print("\nError: 'predictions' table not found!")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db()
