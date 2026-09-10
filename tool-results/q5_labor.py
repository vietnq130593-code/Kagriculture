#!/usr/bin/env python3
"""Query 5: Labor commands per day, liquidation detail, animal/seed purchase timeline."""
import json
from collections import Counter, defaultdict

CROPS = {"WHEAT", "CARROT", "MELON", "TOMATO", "STRAWBERRY"}

def unit_cmds(rec):
    """Yield all unit commands (farmer + hands) with position in list."""
    a = rec.get('action') or {}
    fc = a.get('farmer', [])
    if isinstance(fc, str):
        fc = [fc]
    cmds = list(fc)
    for hc in a.get('hands', []) or []:
        if isinstance(hc, list):
            cmds.extend(hc)
        elif isinstance(hc, str):
            cmds.append(hc)
    return cmds


with open('/home/z/my-project/upload/107559251.json') as f:
    m1 = json.load(f)
with open('/home/z/my-project/upload/107573831.json') as f:
    m2 = json.load(f)

for label, data in [('MATCH 1: SpaTaro LOST vs Unknown Mother-Goose', m1),
                    ('MATCH 2: SpaTaro LOST vs Otter Vibe', m2)]:
    print('=' * 95)
    print(label, '| rewards:', data['rewards'])
    names = data['info']['TeamNames']

    for p in (0, 1):
        # labor commands per day
        daily_labor = defaultdict(Counter)
        feed_wheat = 0
        for rec in data['steps']:
            day = rec[0]['observation']['day']
            for c in unit_cmds(rec[p]):
                if c in ('WATER', 'FEED', 'CARE', 'HARVEST', 'DIG', 'PASS',
                         'COLLECT_FERTILIZER', 'FERTILIZE', 'PICKUP', 'DROP'):
                    daily_labor[day][c] += 1
                elif c in ('NORTH', 'SOUTH', 'EAST', 'WEST'):
                    daily_labor[day]['MOVE'] += 1
                elif c == 'PLANT':
                    daily_labor[day]['PLANT'] += 1
            if c == 'FEED':
                pass

        print(f'\n--- {names[p]} (p{p}) labor per day (top: WATER/FEED/CARE/HARVEST/MOVE/PLANT/COLL):')
        print(f'{"day":>3} {"WATER":>5} {"FEED":>4} {"CARE":>4} {"HARV":>4} {"MOVE":>5} {"PLANT":>5} {"COLL":>4} {"DIG":>3} {"PASS":>4} {"total":>5}')
        for day in range(30):
            c = daily_labor.get(day, Counter())
            tot = sum(v for k, v in c.items() if k != 'PASS')
            print(f'{day:>3} {c["WATER"]:>5} {c["FEED"]:>4} {c["CARE"]:>4} {c["HARVEST"]:>4} '
                  f'{c["MOVE"]:>5} {c["PLANT"]:>5} {c["COLLECT_FERTILIZER"]:>4} {c["DIG"]:>3} {c["PASS"]:>4} {tot:>5}')

        # animal purchase timeline
        print(f'\n    Animal/seed purchases:')
        evs = []
        for t, rec in enumerate(data['steps']):
            a = rec[p].get('action') or {}
            for mo in (a.get('market') or []):
                if isinstance(mo, list) and len(mo) >= 3 and mo[0] in ('BUY_ANIMAL', 'BUY_SEED'):
                    obs_day = rec[0]['observation']['day']
                    evs.append((obs_day, mo[0], mo[1], mo[2]))
        agg = defaultdict(int)
        for d, op, item, q in evs:
            agg[(d, op, item)] += q
        for (d, op, item) in sorted(agg):
            print(f'      d{d:>2} {op:<12} {item:<12} x{agg[(d,op,item)]}')
    print()
