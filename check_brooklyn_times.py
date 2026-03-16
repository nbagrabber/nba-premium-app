import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def check_times():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- Checking commence_time for Brooklyn matches ---")
        cursor.execute("""
            SELECT id, away_team, home_team, pick, line, is_premium, status, commence_time, created_at 
            FROM predictions 
            WHERE (home_team LIKE '%Brooklyn%' OR away_team LIKE '%Brooklyn%' OR home_team LIKE '%Nets%' OR away_team LIKE '%Nets%')
            ORDER BY created_at DESC
        """)
        matches = cursor.fetchall()
        
        for m in matches:
            print(f"ID: {m[0]}, Game: {m[1]}@{m[2]}, Pick: {m[3]}, Line: {m[4]}, Premium: {m[5]}, Status: {m[6]}, Start: {m[7]}, Created: {m[8]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_times()
