#!/usr/bin/env python3
"""Query 7: PLANT schedule by crop, FERTILIZE usage, shed pressure, final waste."""
import json
from collections import Counter, defaultdict

def unit_cmds(rec):
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

for fname, label in [('/home/z/my-project/upload/107559251.json', 'MATCH 1 (SpaTaro vs Unknown Mother-Goose)'),
                     ('/home/z/my-project/upload/107573831.json', 'MATCH 2 (SpaTaro vs Otter Vibe)')]:
    with open(fname) as f:
        data = json.load(f)
    names = data['info']['TeamNames']
    print('=' * 95)
    print(label)

    for p in (0, 1):
        plant_by_day = defaultdict(Counter)
        fert_by_day = Counter()
        for rec in data['steps']:
            day = rec[0]['observation']['day']
            i = 0
            cmds = unit_cmds(rec[p])
            while i < len(cmds):
                c = cmds[i]
                if c == 'PLANT' and i + 1 < len(cmds):
                    plant_by_day[day][cmds[i + 1]] += 1
                    i += 2
                    continue
                if c == 'FERTILIZE':
                    fert_by_day[day] += 1
                i += 1
        print(f'\n--- {names[p]} PLANT schedule by day (crop: count):')
        for day in range(30):
            c = plant_by_day.get(day, Counter())
            if c:
                print(f'  d{day:>2}: ' + ', '.join(f'{k}x{v}' for k, v in sorted(c.items())))
        print(f'    FERTILIZE total: {sum(fert_by_day.values())} (by day: {dict(sorted(fert_by_day.items()))})')

        # final waste: what's left in shed at end + on tiles
        last = data['steps'][-1][p]
        priv = data['steps'][-1][0]['observation'] if p == 0 else None
        # use own private from last obs of that player
        obs_p = data['steps'][719][p]['observation']
        # private only valid for p0 in stored obs? check both
        shed = obs_p.get('private', {}).get('shed', {})
        seeds_left = obs_p.get('private', {}).get('seeds', {})
        # tiles yield units unharvested
        waste_tiles = Counter()
        waste_units = Counter()
        for row in obs_p['farms'][p]['tiles']:
            for t in row:
                if isinstance(t, dict):
                    if t.get('kind') == 'PLANT' and t.get('yield_units', 0) > 0:
                        waste_tiles[t['crop']] += 1
                        waste_units[t['crop']] += t['yield_units']
                    elif 'animal' in t and t.get('yield_units', 0) > 0:
                        waste_tiles[t['animal']] += 1
                        waste_units[t['animal']] += t['yield_units']
                    elif t.get('fertilizer_available'):
                        waste_tiles['FERT_on_tile'] += 1
        print(f'    END-GAME waste (p{p}): shed={shed} | seeds={seeds_left} | tile yields unharvested={dict(waste_units)}')
