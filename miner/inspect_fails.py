import json
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

with open('data/audit_report.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fails = [e for e in data if e['grade'] == 'FAIL']
print(f"Total fails: {len(fails)}")

reasons = {}
for e in fails:
    for iss in e['issues']:
        if iss['severity'] in ('CRITICAL', 'HIGH'):
            k = f"{iss['field']}: {iss['msg'][:60]}"
            reasons[k] = reasons.get(k, 0) + 1

for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
    print(f"{v:3d} | {k}")

print("\n--- SAMPLE FAILS ---")
for e in fails[:10]:
    high_issues = [f"[{i['severity']}] {i['field']}: {i['msg']}" for i in e['issues'] if i['severity'] in ('CRITICAL', 'HIGH')]
    print(f"ID {e['id']:3d} | EN: {e['english']:<25} | Issues: {high_issues}")
