import json
import sys
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')
data = [json.loads(line) for line in open(r'C:\Users\zain_\trilingual-dictionary\dictionary_master.jsonl', encoding='utf-8')]
print(f"Total entries: {len(data)}")

urdu_counts = Counter(d.get('urdu_script') for d in data)
print(f"Unique Urdu values: {len(urdu_counts)}")
print("Top 5 duplicated Urdu values:")
for u, c in urdu_counts.most_common(5):
    print(f"  [{c} times] {u}")

print("\nSample 10 items:")
for d in data[20:30]:
    print(f"[{d.get('category')}] EN: {d.get('english')} | JA: {d.get('japanese_kanji')} ({d.get('japanese_romaji')}) | UR: {d.get('urdu_script')} ({d.get('urdu_roman')})")
