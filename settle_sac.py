import sqlite3
db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Settle Sacramento vs Utah
cursor.execute('UPDATE predictions SET status = "WIN", result_score = "116:111" WHERE game_id = "ae243acf61e3bbc8a0fef18df12adf30"')
conn.commit()
print(f"Settled Sacramento: {conn.total_changes}")
conn.close()
