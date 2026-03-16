import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def list_last_50():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- Last 50 predictions in {db_path} ---")
        cursor.execute("""
            SELECT id, game_id, away_team, home_team, pick, line, odds, is_published, is_premium, status, created_at 
            FROM predictions 
            ORDER BY created_at DESC
            LIMIT 50
        """)
        matches = cursor.fetchall()
        
        for m in matches:
            print(f"ID: {m[0]}, Game: {m[2]}@{m[3]}, Pick: {m[4]}, Line: {m[5]}, Odds: {m[6]}, Published: {m[7]}, Premium: {m[8]}, Status: {m[9]}, Date: {m[10]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_last_50()
