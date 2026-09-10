#!/usr/bin/env python3
"""Query 2: Daily empty rate, tile composition, herd, hands, money."""
import json

with open('/home/z/my-project/tool-results/replay_extract.json') as f:
    data = json.load(f)

for fn, r in data.items():
    print('=' * 100)
    print('MATCH:', fn.split('/')[-1])
    for p in (0, 1):
        print(f'\n--- Player {p} ({r["names"][p]}) daily profile (h23):')
        print(f'{"day":>3} {"money":>8} {"nq":>3} {"empty":>5} {"rate%":>5} {"wheat":>5} {"carrot":>6} {"melon":>5} {"tomato":>6} {"straw":>5} {"G":>3} {"C":>3} {"S":>3} {"hands":>5} {"weeds":>5}')
        for day in range(30):
            h23 = r['days'].get(str(day), {}).get(str(p), {}).get('23')
            if h23 is None:
                continue
            n = h23['n_unlocked']
            em = h23['empty_unlocked']
            rate = 100.0 * em / n if n else 0
            cr = h23['crops']
            an = h23['animals']
            print(f'{day:>3} {h23["money"]:>8.0f} {n//25:>3} {em:>5} {rate:>5.0f} '
                  f'{cr.get("WHEAT",0):>5} {cr.get("CARROT",0):>6} {cr.get("MELON",0):>5} '
                  f'{cr.get("TOMATO",0):>6} {cr.get("STRAWBERRY",0):>5} '
                  f'{an.get("GOOSE",0):>3} {an.get("COW",0):>3} {an.get("SHEEP",0):>3} '
                  f'{h23["hands"]:>5} {h23["tiles"].get("WEED",0):>5}')
    print()
