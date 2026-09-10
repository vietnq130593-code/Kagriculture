#!/usr/bin/env python3
"""Query 4: Shop unlock timeline + inventory trajectories for key items."""
import json
from collections import Counter

with open('/home/z/my-project/tool-results/replay_extract.json') as f:
    data = json.load(f)

for fn, r in data.items():
    print('=' * 90)
    print('MATCH:', fn.split('/')[-1])

    # shop unlock timeline (new shops appearing)
    seen = Counter()
    prev_set = None
    print('\nShop unlock timeline:')
    for rec in r['shops']:
        cur = tuple(rec['shops'])
        if prev_set is not None and len(cur) > len(prev_set):
            c_prev = Counter(prev_set)
            c_cur = Counter(cur)
            added = []
            for s in c_cur:
                if c_cur[s] > c_prev.get(s, 0):
                    added.extend([s] * (c_cur[s] - c_prev.get(s, 0)))
            day = rec.get('day', rec['step'] // 24)
            hour = rec.get('hour', rec['step'] % 24)
            print(f'  d{day:>2} h{hour:>2} step {rec["step"]:>3}: +{added} -> total {dict(c_cur)}')
        prev_set = cur

    # inventory trajectory at day level for MILK, STRAW, EGG, WHEAT, MELON, WOOL
    print('\nMarket inventory (I0=10000; negative = below I0 = scarce):')
    items = ['WHEAT', 'MILK', 'STRAWBERRY', 'EGG', 'WOOL', 'MELON', 'CARROT', 'TOMATO', 'FERTILIZER']
    print('day ' + ' '.join(f'{i[:6]:>7}' for i in items))
    day_inv = {}
    for rec in r['prices']:
        if rec['hour'] == 23 or rec['step'] == 719:
            day_inv.setdefault(rec['day'], []).append(rec['inv'])
    for day in sorted(day_inv):
        invs = day_inv[day]
        avg = {it: sum(iv[it] for iv in invs) / len(invs) for it in items}
        print(f'{day:>3} ' + ' '.join(f'{avg[it]-10000:>+7.0f}' for it in items))
    print()
