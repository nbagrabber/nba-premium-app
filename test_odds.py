import asyncio
import os
import sys
from datetime import datetime

# Add the 'nba' directory to sys.path
sys.path.append(r'c:\Users\Владелец\Desktop\nba')

from data.odds import get_nba_odds

async def test():
    print("Fetching NBA Odds...")
    games = await get_nba_odds()
    print(f"Total games found: {len(games)}")
    
    now = datetime.utcnow()
    print(f"UTC Now: {now}")
    
    future_count = 0
    for g in games:
        commence_time = datetime.fromisoformat(g["commence_time"].replace('Z', ''))
        is_future = commence_time > now
        print(f"Game: {g.get('away_team')} @ {g.get('home_team')} | Start: {commence_time} | Future: {is_future}")
        if is_future:
            future_count += 1
            
    print(f"\nSummary: {future_count} future games found.")

if __name__ == "__main__":
    asyncio.run(test())
