import sqlite3
import os

db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete records with game_id starting with 'hist_'
cursor.execute("DELETE FROM predictions WHERE game_id LIKE 'hist_%'")
deleted_count = cursor.rowcount

conn.commit()
conn.close()

print(f"Removed {deleted_count} test records from the database.")
