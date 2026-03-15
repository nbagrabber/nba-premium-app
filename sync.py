import sqlite3
import json
import os
import subprocess
from datetime import datetime

# Конфигурация
DB_PATH = "c:/Users/Владелец/Desktop/nba/nba_bot.db"
OUTPUT_DIR = "c:/Users/Владелец/Desktop/stitch/_1/data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "matches.json")
REPO_DIR = "c:/Users/Владелец/Desktop/stitch/_1"

def sync():
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных не найдена: {DB_PATH}")
        # Попробуем найти копию если мы в песочнице
        DB_PATH_ALT = "c:/Users/Владелец/Desktop/stitch/_1/nba_bot_copy.db"
        if os.path.exists(DB_PATH_ALT):
            print(f"⚠️ Использую копию базы: {DB_PATH_ALT}")
            conn = sqlite3.connect(DB_PATH_ALT)
        else:
            return
    else:
        conn = sqlite3.connect(DB_PATH)
    
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Проверяем наличие таблицы
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='predictions'")
    if not cursor.fetchone():
        print("❌ Таблица 'predictions' не найдена в БД")
        return

    # Выбираем только актуальные премиум прогнозы (без дублей)
    cursor.execute("""
        SELECT * FROM (
            SELECT 
                id, game_id, commence_time, home_team, away_team, 
                bet_type, pick, odds, line, our_prob, edge, 
                status, sentiment_score, intel_summary, confidence
            FROM predictions 
            WHERE is_premium = 1 
            AND commence_time >= datetime('now', '-6 hours')
            ORDER BY created_at DESC
        ) GROUP BY game_id
        ORDER BY commence_time ASC
        LIMIT 10
    """)
    
    rows = cursor.fetchall()
    matches = []
    
    for row in rows:
        match = dict(row)
        # Форматируем дату для JS
        if match['commence_time']:
            try:
                # Обработка разных форматов дат
                date_str = match['commence_time'].replace('Z', '').split('.')[0]
                dt = datetime.fromisoformat(date_str)
                match['commence_time_display'] = dt.strftime('%d.%m %H:%M')
            except Exception as e:
                match['commence_time_display'] = match['commence_time']
        
        matches.append(match)

    # Сохраняем JSON
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=2)
    
    print(f"DONE: Data exported to {OUTPUT_FILE} ({len(matches)} matches)")

    # Пушим в GitHub
    try:
        os.chdir(REPO_DIR)
        subprocess.run(["git", "add", "data/matches.json"], check=True)
        # Проверяем есть ли изменения
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if status.stdout:
            subprocess.run(["git", "commit", "-m", "Update match data from bot DB"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            print("SUCCESS: Data synced with GitHub Pages")
        else:
            print("INFO: No changes in data, skip push")
    except Exception as e:
        print(f"ERROR: Git push failed: {e}")

if __name__ == "__main__":
    sync()
