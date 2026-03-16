import sqlite3
from datetime import datetime, timedelta

db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'

history = [
    ("Lakers", "Warriors", "Lakers", 1.95, "WIN", "112:108"),
    ("Suns", "Clippers", "Clippers", 2.10, "LOSS", "105:115"),
    ("Celtics", "Heat", "Celtics", 1.85, "WIN", "121:110"),
    ("Nuggets", "Mavericks", "Nuggets", 1.70, "WIN", "108:102"),
    ("Bucks", "Knicks", "Bucks", 1.90, "LOSS", "110:122"),
    ("76ers", "Bulls", "76ers", 1.65, "WIN", "115:100"),
    ("Kings", "Rockets", "Kings", 2.05, "WIN", "130:120"),
]

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

for i, (home, away, pick, odds, status, score) in enumerate(history):
    created_at = (datetime.now() - timedelta(days=7-i)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO predictions (
            game_id, commence_time, home_team, away_team, pick, odds, 
            status, is_premium, result_score, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
    """, (f"hist_{i}", created_at, home, away, pick, odds, status, score, created_at))

conn.commit()
print(f"Added {len(history)} historical games for stats display.")
conn.close()
