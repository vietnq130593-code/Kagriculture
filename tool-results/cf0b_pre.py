#!/usr/bin/env python3
"""CF-0b: SpaTaro M2 raw action stream analysis (junk orders, d29 rhythm, leftovers)."""
import json
from collections import defaultdict

d = json.load(open('/home/z/my-project/upload/107573831.json'))
steps = d['steps']
sp = 0

# 1) Junk BUY_PRODUCT orders (raw, incl. dropped) by day
junk = defaultdict(int)
junk_items = defaultdict(int)
for t in range(1, 720):
    a = steps[t][sp].get('action') or {}
    for o in a.get('market', []):
        if o and o[0] == 'BUY_PRODUCT' and (len(o) < 2 or o[1] not in ('WHEAT', 'FERTILIZER')):
            junk[(t - 1) // 24] += 1
            junk_items[o[1] if len(o) > 1 else '?'] += 1
print('raw junk BUY orders by day:', dict(sorted(junk.items())))
print('by item:', dict(junk_items))

# 2) d28-29 per-hour: market orders of SpaTaro + shed stock snapshot
print()
print('=== SpaTaro M2 d28-29 hour-by-hour ===')
god = json.load(open('/home/z/my-project/tool-results/r2_god_M2.json'))
snaps = {s['t']: s for s in god['snapshots']}
for t in range(28 * 24 + 1, 720):
    a = steps[t][sp].get('action') or {}
    mkt = [tuple(o) for o in a.get('market', [])]
    s = snaps.get(t)
    shed = s[f'p{sp}']['shed'] if s else {}
    day, hour = (t - 1) // 24, (t - 1) % 24
    if mkt or hour % 6 == 0:
        print(f'd{day} h{hour}: mkt={mkt}')
        if hour % 6 == 0:
            print(f'         shed={ {k: v for k, v in shed.items() if v} } inv_carry={ {k: v for k, v in enumerate(s[f"p{sp}"]["inv_carry"]) if v} }')

# 3) final leftover: shed + on-tile yield at end
s = snaps[719]
shed = s[f'p{sp}']['shed']
tiles = s[f'p{sp}']['tiles']
print()
print('FINAL d29 h23 shed:', {k: v for k, v in shed.items() if v})
print('FINAL tiles crops:', tiles.get('crops'), 'crop_yield:', tiles.get('crop_yield'))
print('FINAL animals:', tiles.get('animals'), 'animal_yield:', tiles.get('animal_yield'))
print('FINAL money:', s['money'])
