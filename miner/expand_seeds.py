import json

with open('miner/seeds.json', 'r', encoding='utf-8') as f:
    seeds = json.load(f)

new_seeds = {
    'Automotive': [
        'windshield wiper', 'serpentine belt', 'sunroof', 'muffler', 'anti-freeze',
        'brake fluid', 'power window', 'cruise control', 'blind spot monitor', 'rearview mirror'
    ],
    'Software': [
        'zero-trust security', 'event-driven architecture', 'garbage collection', 'thread pool', 'memory leak',
        'web assembly', 'continuous monitoring', 'blue-green deployment', 'canary release', 'rate limiter'
    ],
    'Banking': [
        'overdraft protection', 'yield curve', 'hedge fund', 'credit rating agency', 'sovereign debt',
        'anti-money laundering', 'kyc compliance', 'peer-to-peer lending', 'merchant account', 'forex trading'
    ],
    'Business': [
        'venture capital', 'due diligence', 'scalability', 'cross-functional team', 'competitive advantage',
        'quarterly earnings', 'value proposition', 'supply shortage', 'freight charge', 'procurement strategy'
    ],
    'Workplace': [
        'onboarding process', 'employee retention', 'exit interview', 'talent acquisition', 'workplace wellness',
        'hybrid work model', 'core working hours', 'maternity benefits', 'occupational health', 'performance incentive'
    ],
    'Logistics': [
        'less than container load', 'full container load', 'customs declaration', 'air waybill', 'reefer container',
        'last-mile delivery', 'cross-docking', 'freight rate', 'stevedoring', 'cargo insurance'
    ],
    'Medical': [
        'electronic health record', 'general anesthesia', 'local anesthesia', 'clinical trial', 'radiology',
        'ultrasound scan', 'intensive care unit', 'medical prescription', 'allergy test', 'preventive medicine'
    ],
    'Legal': [
        'statute of limitations', 'power of representation', 'cease and desist letter', 'injunction', 'appellate court',
        'breach of contract', 'indemnity clause', 'force majeure', 'jurisdiction clause', 'non-compete agreement'
    ]
}

total_added = 0
for cat, terms in new_seeds.items():
    existing_lower = {t.lower() for t in seeds.get(cat, [])}
    for t in terms:
        if t.lower() not in existing_lower:
            seeds.setdefault(cat, []).append(t)
            total_added += 1

with open('miner/seeds.json', 'w', encoding='utf-8') as f:
    json.dump(seeds, f, ensure_ascii=False, indent=2)

print(f"Added {total_added} new seed terms to miner/seeds.json")
