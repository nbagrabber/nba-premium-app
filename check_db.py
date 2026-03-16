import sqlite3
db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT home_team, away_team, edge, is_premium FROM predictions ORDER BY created_at DESC LIMIT 20")
rows = cursor.fetchall()
for r in rows:
    print(r)
conn.close()
