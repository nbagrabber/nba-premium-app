import asyncio
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, r"c:\Users\Владелец\Desktop\nba")

from engine.intelligence import intel
from engine.selector import selector
from dotenv import load_dotenv

async def analyze_match():
    load_dotenv(r"c:\Users\Владелец\Desktop\nba\.env")
    
    home = "Atlanta Hawks"
    away = "Dallas Mavericks"
    
    print(f"Starting analysis for {away} @ {home} (User odds: 1.27)...")
    
    # Optional: Try to get real odds from monitor
    from engine.odds_monitor import monitor
    # games = await monitor.update_all_odds() # Skip live update to save time/credits if possible, or use try-except
    try:
        # games = await monitor.update_all_odds()
        games = [] # Use user odds as priority
    except Exception as e:
        print(f"Error fetching live odds: {e}")
        games = []
    
    odds = {"home": 1.27, "away": 3.80} # Updated mock based on user input
    found = False
    for g in games:
        if (home.lower() in g['home_team'].lower() and away.lower() in g['away_team'].lower()) or \
           (away.lower() in g['home_team'].lower() and home.lower() in g['away_team'].lower()):
            from data.odds import parse_best_odds_all_markets
            parsed = parse_best_odds_all_markets(g)
            odds = parsed["h2h"]
            home = parsed["home_team"]
            away = parsed["away_team"]
            found = True
            print(f"Found real-time odds: {odds}")
            break
            
    if not found:
        print(f"Match not found in live feed. Using estimated odds: {odds}")

    # Run AI Sentiment Analysis (Phase 1)
    print("Fetching injuries, stats and context...")
    analysis, extra = await intel.analyze_match_sentiment(home, away, odds=odds)
    
    print("\n--- AI SENTIMENT RESULT ---")
    print(f"Probabilities: {analysis.get('home_win_probability', 'N/A')}")
    print(f"Score: {analysis.get('score', 0)}")
    print(f"Summary: {analysis.get('summary', 'No summary')}")
    print(f"Key Factor: {analysis.get('key_factor', 'N/A')}")
    print("---------------------------\n")

    # Generate Professional Justification (Phase 2)
    print("Generating professional justification...")
    # We need a Prediction object for the justification generator
    from db.models import Prediction, BetType
    mock_pred = Prediction(
        home_team=home,
        away_team=away,
        pick=home if analysis.get('score', 0) > 0 else away,
        odds=odds['home'] if analysis.get('score', 0) > 0 else odds['away'],
        bet_type=BetType.H2H,
        edge=0.0, # Will be set below
        sentiment_score=analysis.get('score', 0),
        intel_summary=analysis.get('summary', ''),
        game_id="manual_run"
    )
    
    # Calculate edge for visualization
    prob = analysis.get('home_win_probability', 0.5)
    if mock_pred.pick == home:
        mock_pred.edge = (prob * odds['home'] - 1) * 100
    else:
        mock_pred.edge = ((1-prob) * odds['away'] - 1) * 100
        
    justification = await selector.generate_justification(mock_pred, is_vip=(abs(mock_pred.sentiment_score) > 0.4))
    
    print("\n--- FINAL JUSTIFICATION ---")
    print(justification)
    print("----------------------------")
    
    # Write result to a file for the user to see easily
    with open("analysis_result.txt", "w", encoding="utf-8") as f:
        f.write(f"MATC: {away} @ {home}\n")
        f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n\n")
        f.write(f"SENTIMENT: {analysis.get('score', 0)}\n")
        f.write(f"PROBABILITY: {analysis.get('home_win_probability', 'N/A')}\n")
        f.write(f"SUMMARY: {analysis.get('summary', '')}\n\n")
        f.write("JUSTIFICATION:\n")
        f.write(justification)

if __name__ == "__main__":
    asyncio.run(analyze_match())
