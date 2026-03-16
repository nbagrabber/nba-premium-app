import sqlite3
import os
from datetime import datetime

db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("Current Predictions in DB:")
cursor.execute("SELECT game_id, away_team, home_team, commence_time, status, is_premium, is_published, created_at FROM predictions ORDER BY commence_time DESC LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    print(dict(row))

print("\nUTC Now:", datetime.utcnow().isoformat())
conn.close()
