import sqlite3
import json
import re

conn = sqlite3.connect('data/dictionary.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

rows = cur.execute('SELECT id, category, english, japanese_kanji, japanese_kana, japanese_romaji, urdu_script, urdu_roman FROM entries ORDER BY id').fetchall()

kana_issues = []
urdu_issues = []

for r in rows:
    row_dict = dict(r)
    kana = r['japanese_kana'] or ''
    has_ascii = bool(re.search(r'[a-zA-Z]', kana))
    has_kanji = bool(re.search(r'[\u4e00-\u9faf]', kana))
    has_non_kana = bool(re.search(r'[^\u3040-\u309F\u30A0-\u30FF\u3000-\u303F\s/・ー]', kana))
    if has_ascii or has_kanji or has_non_kana:
        row_dict['issues'] = {
            'has_ascii': has_ascii,
            'has_kanji': has_kanji,
            'has_non_kana': has_non_kana
        }
        kana_issues.append(row_dict)
        
    urdu = r['urdu_script'] or ''
    has_cyrillic = bool(re.search(r'[\u0400-\u04FF]', urdu))
    has_latin = bool(re.search(r'[a-zA-Z]', urdu))
    if has_cyrillic or has_latin:
        row_dict_u = dict(r)
        row_dict_u['issues'] = {
            'has_cyrillic': has_cyrillic,
            'has_latin': has_latin
        }
        urdu_issues.append(row_dict_u)

print(f"Total Kana issues: {len(kana_issues)}")
print(f"Total Urdu issues: {len(urdu_issues)}")

with open('data/audit_glitches_detail.json', 'w', encoding='utf-8') as f:
    json.dump({'kana_issues': kana_issues, 'urdu_issues': urdu_issues}, f, ensure_ascii=False, indent=2)

print("Saved detailed glitch report to data/audit_glitches_detail.json")
