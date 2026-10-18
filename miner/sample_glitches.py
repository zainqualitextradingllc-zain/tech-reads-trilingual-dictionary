import sqlite3
import sys
import re
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "dictionary.db"
con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute('SELECT * FROM entries')]

print("=== 1. CYRILLIC IN URDU (Breaks ur-PK voice) ===")
for r in rows:
    ur = r['urdu_script'] or ''
    if re.search(r'[\u0400-\u04FF]', ur):
        print(f"ID {r['id']:<3} | EN: {r['english']:<25} | UR: {ur}")

print("\n=== 2. ENGLISH TEXT IN URDU (Causes robotic letter spelling) ===")
for r in rows:
    ur = r['urdu_script'] or ''
    if re.search(r'[A-Za-z]', ur) and len(re.findall(r'[A-Za-z]', ur)) >= 3:
        print(f"ID {r['id']:<3} | EN: {r['english']:<25} | UR: {ur}")

print("\n=== 3. KANA FIELD MISPRONUNCIATION / KANJI IN KANA ===")
for r in rows:
    kana = r['japanese_kana'] or ''
    if re.search(r'[\u4E00-\u9FFF]', kana) or re.search(r'[A-Za-z]', kana):
        print(f"ID {r['id']:<3} | EN: {r['english']:<25} | KANA: {kana}")

print("\n=== 4. SLASHES READ AS 'SLASH' IN BOTH VOICES ===")
slash_samples = [r for r in rows if '/' in (r['japanese_kana'] or '') or '/' in (r['urdu_script'] or '')][:6]
for r in slash_samples:
    print(f"ID {r['id']:<3} | EN: {r['english']:<25} | JA_KANA: {r['japanese_kana']} | UR: {r['urdu_script']}")
