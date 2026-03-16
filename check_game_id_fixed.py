import sqlite3
import os

db_path = r"c:\Users\Владелец\Desktop\nba\nba_bot.db"

def check_game_id():
    game_id = "b2cf48e20e7ea3f4ee141bf67f8229d1"
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"--- All entries for game_id {game_id} ---")
        cursor.execute("""
            SELECT id, away_team, home_team, pick, bet_type, line, odds, is_premium, status, is_published, created_at 
            FROM predictions 
            WHERE game_id = ?
            ORDER BY created_at DESC
        """, (game_id,))
        rows = cursor.fetchall()
        
        for r in rows:
            # id:0, away:1, home:2, pick:3, bet_type:4, line:5, odds:6, premium:7, status:8, published:9, created:10
            print(f"ID: {r[0]}, {r[1]}@{r[2]}, Pick: {r[3]}, Type: {r[4]}, Line: {r[5]}, Odds: {r[6]}, Premium: {r[7]}, Status: {r[8]}, Published: {r[9]}, Created: {r[10]}")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_game_id()
