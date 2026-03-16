import asyncio
import logging
import os
import sys
from dotenv import load_dotenv

# Добавляем путь к боту в sys.path
sys.path.append("c:/Users/Владелец/Desktop/nba")

# Настройка логов для консоли
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

async def run_test_analysis():
    # Загружаем .env из папки бота
    load_dotenv("c:/Users/Владелец/Desktop/nba/.env")
    
    from engine.vector_store import NBAVectorStore
    # Форсируем временную директорию для базы
    import shutil
    temp_db_path = "c:/Users/Владелец/Desktop/stitch/_1/temp_chroma"
    if os.path.exists(temp_db_path):
        shutil.rmtree(temp_db_path)
    os.makedirs(temp_db_path, exist_ok=True)
    
    from engine.odds_monitor import monitor
    from data.odds import parse_best_odds_all_markets
    from engine.intelligence import intel
    from engine.selector import selector
    from db.models import Prediction, BetType
    
    # Переопределяем путь к базе
    intel.vector_store = NBAVectorStore(persist_directory=temp_db_path)
    
    print("STARTING TEST ANALYSIS AUDIT...\n")
    
    # 1. Получаем реальные коэффициенты
    print("--- STEP 1: Fetching Odds (Odds API) ---")
    games = await monitor.update_all_odds()
    if not games:
        print("Error: No games from API.")
        return
        
    # Берем первый попавшийся матч
    game_raw = games[0]
    parsed = parse_best_odds_all_markets(game_raw)
    home, away = parsed["home_team"], parsed["away_team"]
    
    print(f"Match selected: {away} @ {home}")
    print(f"Consensus Line (Spread): {parsed['spreads']['home_point']}")
    print(f"Best H2H: Home {parsed['h2h']['home']} | Away {parsed['h2h']['away']}")
    print(f"Bookies: {parsed['h2h']['home_bookie']} vs {parsed['h2h']['away_bookie']}")
    print("-" * 50 + "\n")

    # 2. Собираем контекст (Reddit + RSS)
    print(f"--- STEP 2: Collecting Insights for {home} and {away} ---")
    context_data = await intel.analyze_match_sentiment(home, away, odds=parsed["h2h"])
    print(f"Insights found: {context_data.get('full_context', '0')}")
    print("-" * 50 + "\n")

    # 3. Генерируем финальное обоснование
    print("--- STEP 3: Generating Deep Analysis (Gemini) ---")
    mock_pred = Prediction(
        game_id=parsed["id"],
        home_team=home,
        away_team=away,
        pick=home if context_data["score"] >= 0 else away,
        odds=parsed["h2h"]["home"] if context_data["score"] >= 0 else parsed["h2h"]["away"],
        sentiment_score=context_data["score"],
        edge=abs(context_data["score"]) * 100,
        intel_summary=context_data["summary"],
        bet_type=BetType.H2H,
        confidence="High"
    )
    
    justification = await selector.generate_justification(mock_pred)
    
    print("\nFINAL RESULT (Text for Telegram):\n")
    print(justification)
    print("\n" + "=" * 50)
    print(f"Text length: {len(justification)} characters.")

if __name__ == "__main__":
    asyncio.run(run_test_analysis())
