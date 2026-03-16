import sqlite3
import re

db_path = r'c:\Users\Владелец\Desktop\nba\nba_bot.db'

def remove_emojis(text):
    if not text:
        return text
    # Remove emojis using regex
    # Common emojis and some specific ones mentioned in the prompt
    return re.sub(r'[\U00010000-\U0010ffff]|\u26bd|\u26be|\ud83c[\udf00-\udfff]|\ud83d[\udc00-\ude4f]|\ud83d[\ude80-\udeff]|\u26aa|\u26ab|\u2b1b|\u2b1c|\u2611|\u2705|\u274c|\u274e|\u2753|\u2754|\u2755|\u2757|\u27a1|\u2b05|\u2b06|\u2b07|\u2139|\u24c2|\u24bd|\u21a9|\u21aa|\u231a|\u231b|\u23f0|\u23f3|\u25fe|\u25fd|\u2648-\u2653|\u26ce|\u267b|\u267f|\u26a0|\u26a1|\u26aa|\u26ab|\u26bd|\u26be|\u26c4|\u26c5|\u26d4|\u26ea|\u26f2|\u26f3|\u26f5|\u26fa|\u26fd|\u2702|\u2705|\u2708|\u2709|\u270a-\u270d|\u270f|\u2712|\u2714|\u2716|\u2728|\u2733|\u2734|\u2744|\u2747|\u274c|\u274e|\u2753-\u2755|\u2757|\u2763|\u2764|\u2795-\u2797|\u27a1|\u27b0|\u27bf|\u2b05-\u2b07|\u2b1b|\u2b1c|\u2b50|\u2b55|\u3030|\u303d|\u3297|\u3299]', '', text)

# Also remove bullet dots if they look like emojis or if user wants more clean ones
def replace_bullets(text):
    if not text:
        return text
    # Replace • with - for consistency as per prompt update
    return text.replace('•', '-')

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, intel_summary FROM predictions WHERE is_premium = 1")
rows = cursor.fetchall()

updated_count = 0
for row in rows:
    summary = row['intel_summary']
    if summary:
        clean_summary = remove_emojis(summary)
        clean_summary = replace_bullets(clean_summary)
        if clean_summary != summary:
            cursor.execute("UPDATE predictions SET intel_summary = ? WHERE id = ?", (clean_summary.strip(), row['id']))
            updated_count += 1

conn.commit()
print(f"Cleaned emojis from {updated_count} predictions")
conn.close()
