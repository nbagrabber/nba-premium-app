import os

log_path = r"c:\Users\Владелец\Desktop\nba\logs\bot.log"

def search_log(query):
    if not os.path.exists(log_path):
        print(f"Error: Log not found at {log_path}")
        return

    try:
        matches = []
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if query.lower() in line.lower():
                    matches.append(line.strip())
        
        print(f"--- Found {len(matches)} matches for '{query}' in log ---")
        for m in matches[-50:]:  # Print last 50 matches
            print(m)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    search_log("approve")
