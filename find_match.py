import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def find_match():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if table is Prediction or predictions
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='predictions' OR name='Prediction');")
        table_name = cursor.fetchone()[0]
        
        query = f"SELECT id, home_team, away_team, commence_time, status FROM {table_name} WHERE (home_team LIKE '%Dallas%' AND away_team LIKE '%Atlanta%') OR (home_team LIKE '%Atlanta%' AND away_team LIKE '%Dallas%') ORDER BY commence_time DESC LIMIT 5;"
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]} | {row[2]} @ {row[1]} | Time: {row[3]} | Status: {row[4]}")
            
        if not rows:
            print("Match not found in database.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_match()
