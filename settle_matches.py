import sqlite3
db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

ids = ['6420f72c1e96bb40f11548af8dbb2950', 'ee20dd8148c700589a380b7f5b5c1010']
cursor.execute('SELECT game_id, home_team, away_team, pick, bet_type, line, status, odds FROM predictions WHERE game_id IN (?, ?)', ids)
rows = cursor.fetchall()

print("--- Current Match Data ---")
for row in rows:
    print(dict(row))

# PHI 109 - 103 POR
# TOR 119 - 108 DET
# Update based on scores
# Note: In our DB Toronto @ Detroit or Detroit @ Toronto? 
# Row 1: {'home_team': 'Toronto Raptors', 'away_team': 'Detroit Pistons', 'pick': 'Toronto Raptors', ...}
# Row 2: {'home_team': 'Philadelphia 76ers', 'away_team': 'Portland Trail Blazers', 'pick': 'Philadelphia 76ers', ...}

updates = [
    # (status, result_score, game_id)
    ('WIN', '119:108', 'ee20dd8148c700589a380b7f5b5c1010'), 
    ('WIN', '109:103', '6420f72c1e96bb40f11548af8dbb2950')
]

for status, score, gid in updates:
    cursor.execute('UPDATE predictions SET status = ?, result_score = ? WHERE game_id = ?', (status, score, gid))

conn.commit()
print("\n--- Matches Updated ---")
conn.close()
