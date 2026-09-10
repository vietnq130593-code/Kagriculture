#!/usr/bin/env python3
"""Query 6: Daily units sold per channel per player + revenue estimate."""
import json

with open('/home/z/my-project/tool-results/replay_ledger.json') as f:
    out = json.load(f)

for match, r in out.items():
    print('=' * 100)
    print('MATCH:', match, '|', r['names'], '|', r['rewards'])
    for p in ('0', '1'):
        dr = r['daily_rev'][p]
        items = ['WHEAT', 'MILK', 'STRAWBERRY', 'EGG', 'MELON', 'CARROT', 'TOMATO', 'WOOL', 'FERTILIZER']
        print(f'\n--- {r["names"][int(p)]} daily units SOLD:')
        print('day ' + ' '.join(f'{i[:6]:>6}' for i in items) + '   $Δmoney')
        prev_money = None
        for day in range(30):
            d = dr.get(str(day), {})
            # money from ledger days: use extract money
            print(f'{day:>3} ' + ' '.join(f'{d.get(i, 0):>6}' for i in items))
    print()
