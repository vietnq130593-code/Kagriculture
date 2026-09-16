#!/usr/bin/env python3
"""Part 3: money flow, hires, land, crop mix, weeds, watering."""
import json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(D, 'match1')
orders = json.load(open(os.path.join(M, 'orders.json')))
daily  = json.load(open(os.path.join(M, 'daily.json')))
tl     = json.load(open(os.path.join(M, 'timeline.json')))
P = {0: 'ymg_aq', 1: 'Majkel'}
daily_p = {0: {}, 1: {}}
for r in daily: daily_p[r['player']][r['day']] = r
tl_p = {0: {}, 1: {}}
for r in tl: tl_p[r['player']][r['step']] = r

# ---------- 3. MONEY FLOW ----------
print('=' * 100)
print('3. MONEY FLOW — tổng chi theo op (orders.json)')
for p in (0, 1):
    agg = defaultdict(lambda: [0, 0.0])  # units, cash
    for r in orders:
        if r['player'] == p and r['units'] > 0:
            k = r['op']
            agg[k][0] += r['units']; agg[k][1] += r['cash']
    print(f'\n--- {P[p]} ---')
    tot = 0
    for k in ['BUY_SEED', 'BUY_ANIMAL', 'BUY_PRODUCT', 'HIRE', 'BUY_LAND', 'SELL']:
        u, c = agg.get(k, [0, 0])
        tot += c
        print(f'  {k:<12} units={u:>6} cash={c:>10,.0f}')
    print(f'  NET (all ops) = {tot:,.0f}  (+3,000 start = {tot+3000:,.0f})')

print('\nChi tiết BUY theo item:')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    agg = defaultdict(lambda: [0, 0.0])
    for r in orders:
        if r['player'] == p and r['units'] > 0 and r['op'] != 'SELL':
            agg[(r['op'], r['item'])][0] += r['units']
            agg[(r['op'], r['item'])][1] += r['cash']
    for (op, it), (u, c) in sorted(agg.items()):
        it = it or '-'
        print(f'  {op:<12} {it:<12} units={u:>5} cash={c:>9,.0f} avg={abs(c/u):>7,.1f}')

# sells per day
print('\nSELL revenue theo ngày:')
for p in (0, 1):
    rev = defaultdict(float)
    for r in orders:
        if r['player'] == p and r['op'] == 'SELL' and r['units'] > 0:
            rev[r['day']] += r['cash']
    print(f'--- {P[p]} ---')
    for d in range(30):
        print(f'  d{d:>2}: {rev[d]:>8,.0f}', end='')
        if (d+1) % 5 == 0: print()
    print()

# ---------- HIRES ----------
print('=' * 100)
print('HIRES theo ngày: hands_max / hire_spend')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    tot = 0
    for d in range(30):
        r = daily_p[p][d]
        tot += r['hire_spend']
        print(f'  d{d:>2}: hands={r["hands_max"]:>2} hire=${r["hire_spend"]:>6,.0f}')
    print(f'  TỔNG hire = ${tot:,.0f}')

# hands timeline (max hands over game)
for p in (0, 1):
    hs = [tl_p[p][s]['hands'] for s in range(720)]
    print(f'{P[p]}: hands min/avg/max = {min(hs)}/{sum(hs)/720:.1f}/{max(hs)}')

# ---------- LAND ----------
print('=' * 100)
print('LAND: BUY_LAND orders')
for r in orders:
    if r['op'] == 'BUY_LAND':
        print(f'  s{r["step"]:>3} d{r["day"]} p{r["player"]} ({P[r["player"]]:<8}) units={r["units"]} cash={r["cash"]:,.0f}')

# quadrants over time
for p in (0, 1):
    qs = [tl_p[p][s]['quadrants'] for s in range(720)]
    ch = [(s // 24, q) for s, q in enumerate(qs) if s == 0 or qs[s-1] != q]
    print(f'{P[p]}: quadrants đổi tại (day, quad): {ch}')

# ---------- CROP MIX ----------
print('=' * 100)
print('CROP MIX (plants) theo ngày chọn + cuối trận:')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    for d in [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 29]:
        print(f'  d{d:>2}: {daily_p[p][d]["plants"]}')
    # tổng cây-trời (plant-days)
    pd = defaultdict(int)
    for d in range(30):
        for k, v in daily_p[p][d]['plants'].items():
            pd[k] += v
    print(f'  plant-days tổng: {dict(pd)}')

# ---------- WEEDS & WATERING ----------
print('=' * 100)
print('WEEDS theo ngày (timeline cuối ngày) + WATER verbs + tổng cây:')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    tot_weeds = 0; tot_water = 0; tot_plants = 0
    for d in range(30):
        r = daily_p[p][d]
        w = r['weeds']; wa = r['verbs'].get('WATER', 0)
        npl = sum(r['plants'].values())
        tot_weeds += w; tot_water += wa; tot_plants += npl
        if w > 0 or d in (0, 5, 10, 15, 20, 25, 29):
            print(f'  d{d:>2}: weeds={w:>2} water={wa:>3} plants={npl:>3}')
    print(f'  TỔNG: weeds={tot_weeds}, water={tot_water}, plant-days={tot_plants}, water/plant-day={tot_water/max(tot_plants,1):.2f}')
