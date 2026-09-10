#!/usr/bin/env python3
"""Query 3: Price curves, shops, sell timing, seed/animal purchase timeline."""
import json
from collections import Counter, defaultdict

with open('/home/z/my-project/tool-results/replay_extract.json') as f:
    data = json.load(f)

ITEMS = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']

for fn, r in data.items():
    print('=' * 100)
    print('MATCH:', fn.split('/')[-1], '|', r['names'], '|', r['rewards'])

    # shops over time
    shops_seen = []
    for rec in r['shops']:
        if rec['step'] % 24 == 23:  # day end snapshot
            shops_seen = rec['shops']
        if rec['step'] == 719:
            shops_seen = rec['shops']
    print('\nFinal town shops:', Counter(shops_seen))

    # daily avg prices for key items
    print('\nDaily price table (h23):')
    hdr = 'day ' + ' '.join(f'{i[:5]:>6}' for i in ITEMS)
    print(hdr)
    day_px = {}
    for rec in r['prices']:
        day_px.setdefault(rec['day'], []).append(rec['prices'])
    for day in range(30):
        if day not in day_px:
            continue
        pxs = day_px[day]
        avg = {it: sum(p[it] for p in pxs) / len(pxs) for it in ITEMS}
        print(f'{day:>3} ' + ' '.join(f'{avg[it]:>6.0f}' for it in ITEMS))

    # sell timing: hour-of-day histogram of SELL orders + tranche sizes
    for p in (0, 1):
        sells = defaultdict(list)
        for ev in r['market_events'][str(p)]:
            if ev['cmd'] == 'SELL' and ev.get('item'):
                sells[ev['item']].append(ev)
        print(f'\n--- {r["names"][p]} SELL pattern:')
        for item in sorted(sells, key=lambda x: -sum(e['qty'] or 0 for e in sells[x])):
            evs = sells[item]
            total = sum(e['qty'] or 0 for e in evs)
            hours = Counter(e['hour'] for e in evs)
            qts = [e['qty'] or 0 for e in evs]
            days = sorted(set(e['day'] for e in evs))
            print(f'  {item:<12} {total:>4}u in {len(evs):>3} orders (avg {sum(qts)/max(1,len(qts)):.1f}u) '
                  f'days {days[0]}-{days[-1]} | top hours: {hours.most_common(4)}')
    print()
