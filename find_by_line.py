import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def find_by_line():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- Searching for matches with line 10.5 or -10.5 ---")
        cursor.execute("""
            SELECT id, game_id, away_team, home_team, pick, line, odds, is_published, is_premium, status, created_at 
            FROM predictions 
            WHERE abs(line) = 10.5
            ORDER BY created_at DESC
        """)
        matches = cursor.fetchall()
        
        if not matches:
            print("No matches with line 10.5 found.")
        else:
            for m in matches:
                print(f"ID: {m[0]}, Game: {m[2]}@{m[3]}, Pick: {m[4]}, Line: {m[5]}, Odds: {m[6]}, Published: {m[7]}, Premium: {m[8]}, Status: {m[9]}, Date: {m[10]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_by_line()
