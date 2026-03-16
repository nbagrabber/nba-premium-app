import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def find_all_premium():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- All Premium Predictions ---")
        cursor.execute("""
            SELECT id, game_id, away_team, home_team, pick, line, is_premium, status, commence_time, is_published 
            FROM predictions 
            WHERE is_premium = 1
            ORDER BY created_at DESC
        """)
        matches = cursor.fetchall()
        
        for m in matches:
            print(f"ID: {m[0]}, Game: {m[2]}@{m[3]}, Pick: {m[4]}, Line: {m[5]}, Premium: {m[6]}, Status: {m[7]}, Start: {m[8]}, Published: {m[9]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_all_premium()
