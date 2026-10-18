import sqlite3
import json

con = sqlite3.connect('data/dictionary.db')
con.execute("PRAGMA journal_mode=WAL;")
con.execute("PRAGMA busy_timeout=60000;")

con.execute("""
    UPDATE entries
    SET japanese_kanji = 'パワーウィンドウ',
        japanese_kana = 'パワーウィンドウ',
        japanese_romaji = 'pawā windō',
        urdu_script = 'پاور ونڈو / برقی کھڑکی',
        urdu_roman = 'power window / barqi khirki'
    WHERE LOWER(english) = 'power window'
""")
con.commit()

con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute("SELECT * FROM entries ORDER BY id").fetchall()]
con.close()

with open('app/assets/dictionary.json', 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(f"Cleaned 'power window' and synced {len(rows)} entries to dictionary.json")
