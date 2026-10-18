import json

with open('data/audit_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fails = [e for e in data if e['grade'] == 'FAIL']
print("Failing IDs count:", len(fails))
print("IDs:", [e['id'] for e in fails])

with open('data/failing_entries.json', 'w', encoding='utf-8') as f:
    json.dump(fails, f, ensure_ascii=False, indent=2)

print("Exported to data/failing_entries.json")
