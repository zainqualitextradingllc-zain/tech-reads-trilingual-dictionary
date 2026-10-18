"""
Detailed Audio Audit & Linguistic Quality Breakdown
Scans dictionary.db and outputs a breakdown categorized by audio impact.
"""
import sqlite3
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DB_PATH = Path(__file__).resolve().parent.parent / "data" / "dictionary.db"

con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
con.row_factory = sqlite3.Row
rows = [dict(r) for r in con.execute("SELECT * FROM entries ORDER BY id ASC")]

# Categories of Audio Issues
audio_issues = {
    "slashes_read_aloud": [],      # Contains "/" which TTS reads as "slash" or "スラッシュ"
    "parentheses_read": [],        # Contains "(" which TTS reads aloud or alters pacing
    "latin_in_urdu": [],           # English words in Urdu causing voice engine to mispronounce
    "cyrillic_corrupted": [],      # Accidental Russian/Cyrillic characters in Urdu
    "wrong_kana_pronunciation": [],# Kana reading contains Kanji or invalid syllables
    "hallucinated_gibberish": []   # Obvious gibberish or non-Urdu translations
}

CYRILLIC = re.compile(r"[\u0400-\u04FF]")
LATIN = re.compile(r"[A-Za-z]")
KANJI = re.compile(r"[\u4E00-\u9FFF]")

for r in rows:
    eng = r["english"]
    kana = r["japanese_kana"] or ""
    ur = r["urdu_script"] or ""
    
    # 1. Japanese Audio (reads japanese_kana)
    if "/" in kana:
        audio_issues["slashes_read_aloud"].append({
            "id": r["id"], "term": eng, "field": "japanese_kana", "val": kana,
            "impact": "TTS reads 'スラッシュ' (surasshu) between the synonyms instead of pausing"
        })
    if KANJI.search(kana):
        audio_issues["wrong_kana_pronunciation"].append({
            "id": r["id"], "term": eng, "field": "japanese_kana", "val": kana,
            "impact": "Kanji in kana field causes TTS engine reading misinterpretations"
        })
        
    # 2. Urdu Audio (reads urdu_script)
    if "/" in ur:
        audio_issues["slashes_read_aloud"].append({
            "id": r["id"], "term": eng, "field": "urdu_script", "val": ur,
            "impact": "Urdu TTS reads 'slash' aloud between both translations"
        })
    if "(" in ur or "（" in ur:
        audio_issues["parentheses_read"].append({
            "id": r["id"], "term": eng, "field": "urdu_script", "val": ur,
            "impact": "TTS reads parenthetical abbreviations or English acronyms awkwardly"
        })
    if CYRILLIC.search(ur):
        audio_issues["cyrillic_corrupted"].append({
            "id": r["id"], "term": eng, "field": "urdu_script", "val": ur,
            "impact": "Cyrillic characters trigger pronunciation crashes or silence"
        })
    elif LATIN.search(ur):
        audio_issues["latin_in_urdu"].append({
            "id": r["id"], "term": eng, "field": "urdu_script", "val": ur,
            "impact": "Urdu voice switches to robotic English spelling"
        })

print(f"Total Entries Audited: {len(rows)}")
for issue_type, items in audio_issues.items():
    print(f"• {issue_type}: {len(items)} entries affected")
