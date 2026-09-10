#!/usr/bin/env python3
"""Query script 1: Land purchase timing + final money."""
import json

with open('/home/z/my-project/tool-results/replay_extract.json') as f:
    data = json.load(f)

for fn, r in data.items():
    print('=' * 80)
    print('MATCH:', fn.split('/')[-1])
    print('Players:', r['names'], '-> rewards:', r['rewards'])
    print()
    for p in (0, 1):
        print(f'--- Player {p} ({r["names"][p]}):')
        prev_q = None
        for day in range(30):
            d = r['days'].get(str(day), {}).get(str(p), {})
            h23 = d.get('23')
            if h23 is None:
                continue
            q = tuple(h23['quadrants'])
            if q != prev_q:
                print(f'  d{day} h23: quadrants={q} ({h23["n_unlocked"]} tiles) money=${h23["money"]:.0f}')
                prev_q = q
        for ev in r['market_events'][str(p)]:
            if ev['cmd'] == 'BUY_LAND':
                print(f'  BUY_LAND: d{ev["day"]} h{ev["hour"]}')
        h23 = r['days'].get('29', {}).get(str(p), {}).get('23')
        if h23:
            print(f'  final d29 h23: money=${h23["money"]:.0f}, empty={h23["empty_unlocked"]}')
    print()
