import sqlite3
import os
from datetime import datetime

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def check_upcoming():
    if not os.path.exists(db_path):
        # Try local path
        db_path_local = "nba_bot.db"
        if os.path.exists(db_path_local):
            path = db_path_local
        else:
            print(f"Error: DB not found at {db_path} or {db_path_local}")
            return
    else:
        path = db_path

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        print(f"--- Upcoming matches in {path} ---")
        # Check if Prediction table exists (case sensitive check might be needed)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='predictions' OR name='Prediction');")
        table_name = cursor.fetchone()
        if not table_name:
            print("Error: Prediction/predictions table not found!")
            return
        
        table_name = table_name[0]
        print(f"Current time: {datetime.utcnow()}")
        cursor.execute(f"SELECT home_team, away_team, commence_time, status FROM {table_name} WHERE commence_time > datetime('now', '-48 hours') ORDER BY commence_time ASC LIMIT 20;")
        rows = cursor.fetchall()
        for row in rows:
            print(f"{row[1]} @ {row[0]} | Time: {row[2]} | Status: {row[3]}")
            
        if not rows:
            print("No upcoming matches found in the next period.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_upcoming()
