import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def check_odds_history():
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- Odds History for Brooklyn/Nets ---")
        cursor.execute("""
            SELECT h.game_id, h.timestamp, h.spread_home_line, h.spread_home_odds, p.home_team, p.away_team
            FROM odds_history h
            JOIN predictions p ON h.game_id = p.game_id
            WHERE (p.home_team LIKE '%Brooklyn%' OR p.away_team LIKE '%Brooklyn%' OR p.home_team LIKE '%Nets%' OR p.away_team LIKE '%Nets%')
            ORDER BY h.timestamp DESC
            LIMIT 20
        """)
        history = cursor.fetchall()
        
        for row in history:
            print(f"Game: {row[4]}@{row[5]}, ID: {row[0]}, Time: {row[1]}, Spread: {row[2]}, Odds: {row[3]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_odds_history()
