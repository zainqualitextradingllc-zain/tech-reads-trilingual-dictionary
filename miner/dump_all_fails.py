import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/audit_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fails = [e for e in data if e['grade'] == 'FAIL']
print(f"Total fails: {len(fails)}")

for e in fails:
    high_issues = [f"[{i['severity']}] {i['field']}: {i['msg']}" for i in e['issues'] if i['severity'] in ('CRITICAL', 'HIGH')]
    print("="*60)
    print(f"ID {e['id']} | Category: {e['category']} | English: {e['english']}")
    print(f"JA Kanji : {e['japanese_kanji']}")
    print(f"JA Kana  : {e['japanese_kana']}")
    print(f"JA Romaji: {e['japanese_romaji']}")
    print(f"UR Script: {e['urdu_script']}")
    print(f"UR Roman : {e['urdu_roman']}")
    print(f"Issues   : {high_issues}")
