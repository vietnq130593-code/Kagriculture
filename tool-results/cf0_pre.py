#!/usr/bin/env python3
"""CF-0 pre-analysis: SpaTaro M2 straw timing, junk orders, shed stock."""
import json
from collections import defaultdict

d = json.load(open('/home/z/my-project/tool-results/r2_god_M2.json'))
cl = d['commit_log']
sp = 0 if d['rewards'][0] == 107329 else 1
print('names:', d['names'], '| SpaTaro is player', sp)

straw_sells = defaultdict(lambda: [0, 0.0])
junk = defaultdict(int)
eggs = defaultdict(lambda: [0, 0.0])
for t, p, op, item, price in cl:
    if p != sp:
        continue
    day = (t - 1) // 24
    if op == 'SELL' and item == 'STRAWBERRY':
        straw_sells[day][0] += 1
        straw_sells[day][1] += price
    if op == 'BUY_PRODUCT' and item not in ('WHEAT', 'FERTILIZER'):
        junk[day] += 1

print('SpaTaro straw sells by day (n, avg price):')
for day in sorted(straw_sells):
    n, tot = straw_sells[day]
    print(f'  d{day}: n={n} avg=${tot/n:.0f}')
print('SpaTaro junk BUY orders by day:', dict(sorted(junk.items())))

snaps = d['snapshots']
print()
print('End-of-day shed STRAW + market price + inv:')
for day in range(16, 29):
    s = None
    for ss in snaps:
        if ss['day'] == day and ss['hour'] == 23:
            s = ss
            break
    if s:
        print(f"  d{day}: shed={s[f'p{sp}']['shed'].get('STRAWBERRY', 0)} "
              f"price=${s['prices']['STRAWBERRY']:.0f} inv={s['inv']['STRAWBERRY']}")

# straw unit_log harvests (units picked up) timing
ul = d['unit_log']
harv = defaultdict(int)
for e in ul:
    if e.get('p') != sp or 'harvest' not in e:
        continue
    crop, n = e['harvest']
    if crop == 'STRAWBERRY':
        harv[e['t']] += n
print()
print('SpaTaro straw HARVEST events (t: units):')
cum = 0
for t in sorted(harv):
    cum += harv[t]
    if (t - 1) // 24 >= 17:
        print(f'  t={t} (d{(t-1)//24} h{(t-1)%24}): +{harv[t]} (cum {cum})')
