
import asyncio
import os
import sys

# Добавляем корневую директорию nba в sys.path
sys.path.append(r'c:\Users\Владелец\Desktop\nba')
os.environ["PYTHONPATH"] = r'c:\Users\Владелец\Desktop\nba'

from data.odds import get_nba_odds
from datetime import datetime

async def main():
    # Настройка кодировки для Windows
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print(f"Current time (UTC): {datetime.utcnow()}")
    try:
        games = await get_nba_odds()
        print(f"Total games received: {len(games)}")
        
        for g in games:
            home = g.get('home_team')
            away = g.get('away_team')
            commence = g.get('commence_time')
            print(f"- {away} @ {home} (Time: {commence})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
