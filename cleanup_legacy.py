import os
files_to_del = [
    r'c:\Users\Владелец\Desktop\nba\test_g4f_fix.py',
    r'c:\Users\Владелец\Desktop\nba\test_g4f_providers.py',
    r'c:\Users\Владелец\Desktop\nba\test_g4f_providers_v2.py',
    r'c:\Users\Владелец\Desktop\nba\debug_ai.py'
]
for f in files_to_del:
    if os.path.exists(f):
        try:
            os.remove(f)
            print(f"Deleted {f}")
        except Exception as e:
            print(f"Failed to delete {f}: {e}")
    else:
        print(f"File not found: {f}")
