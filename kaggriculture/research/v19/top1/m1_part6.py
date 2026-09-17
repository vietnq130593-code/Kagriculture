#!/usr/bin/env python3
"""Part 6: giai đoạn hóa, giá theo ngày vs sell, d29 theo giờ, shed cap, land affordability."""
import json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(D, 'match1')
orders = json.load(open(os.path.join(M, 'orders.json')))
daily  = json.load(open(os.path.join(M, 'daily.json')))
tl     = json.load(open(os.path.join(M, 'timeline.json')))
market = json.load(open(os.path.join(M, 'market.json')))
P = {0: 'ymg_aq', 1: 'Majkel'}
daily_p = {0: {}, 1: {}}
for r in daily: daily_p[r['player']][r['day']] = r
tlp = {0: {}, 1: {}}
for r in tl: tlp[r['player']][r['step']] = r
mkts = {r['step']: r for r in market}

# ---------- 6A. REVENUE + SPEND THEO GIAI ĐOẠN ----------
print('=' * 100)
print('6A. REVENUE/SPEND THEO GIAI ĐOẠN 5 NGÀY')
phases = [(0, 4), (5, 9), (10, 14), (15, 19), (20, 24), (25, 29)]
for p in (0, 1):
    print(f'--- {P[p]} ---')
    for lo, hi in phases:
        rev = spend = 0
        for d in range(lo, hi + 1):
            r = daily_p[p][d]
            rev += sum(v['cash'] for v in r['sells'].values())
            spend += sum(v['cash'] for v in r['buys'].values()) + r['hire_spend'] + r['land_spend']
        print(f'  d{lo:>2}-{hi:<2}: revenue={rev:>8,.0f} spend={spend:>8,.0f} net={rev+spend:>+8,.0f}')

# revenue delta theo giai đoạn (ymg - maj)
print('\nDelta revenue (ymg − Majkel) theo giai đoạn:')
for lo, hi in phases:
    rv = []
    for p in (0, 1):
        rev = 0
        for d in range(lo, hi + 1):
            rev += sum(v['cash'] for v in daily_p[p][d]['sells'].values())
        rv.append(rev)
    print(f'  d{lo:>2}-{hi:<2}: ymg={rv[0]:>8,.0f} maj={rv[1]:>8,.0f} delta={rv[0]-rv[1]:>+8,.0f}')

# ---------- 6B. GIÁ THEO NGÀY (h0) vs AVG SELL PRICE THEO NGÀY ----------
print('\n' + '=' * 100)
print('6B. GIÁ THỊ TRƯỜNG ĐẦU NGÀY (h1) cho MELON/STRAWBERRY/TOMATO/CARROT/WHEAT/EGG/MILK')
print(f'{"day":>3} | ' + ' '.join(f'{i[:5]:>6}' for i in ['MELON','STRAW','TOMAT','CARRO','WHEAT','EGG','MILK','WOOL','FERT']))
for d in range(30):
    s = d * 24 + 1
    r = mkts.get(s, mkts.get(d*24))
    print(f'{d:>3} | ' + ' '.join(f"{r['prices'][i]:>6}" for i in ['MELON','STRAWBERRY','TOMATO','CARROT','WHEAT','EGG','MILK','WOOL','FERTILIZER']))

# avg sell price theo ngày cho MELON + STRAWBERRY
for it in ('MELON', 'STRAWBERRY', 'TOMATO'):
    print(f'\nAvg sell price {it} theo ngày (units):')
    for p in (0, 1):
        per = defaultdict(lambda: [0, 0.0])
        for r in orders:
            if r['player'] == p and r['op'] == 'SELL' and r['item'] == it and r['units'] > 0:
                per[r['day']][0] += r['units']; per[r['day']][1] += r['cash']
        s = ', '.join(f'd{d}:{u}u@{c/u:.0f}' for d, (u, c) in sorted(per.items()))
        print(f'  {P[p]:<8}: {s}')

# ---------- 6C. d29 THEO GIỜ ----------
print('\n' + '=' * 100)
print('6C. NGÀY 29 THEO GIỜ: revenue mỗi giờ + HARVEST verb + money')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    for s in range(696, 720):
        rev = sum(r['cash'] for r in orders if r['step'] == s and r['player'] == p and r['op'] == 'SELL' and r['units'] > 0)
        hv = tlp[p][s]['unit_verbs'].get('HARVEST', 0)
        sh = tlp[p][s]['shed_total']
        if rev or hv or sh:
            print(f'  h{s%24:>2}: sell=${rev:>6,.0f} harvest={hv} shed_total={sh} money={tlp[p][s]["money"]:>9,.0f}')

# ---------- 6D. SHED CAP ----------
print('\n' + '=' * 100)
print('6D. SHED: max shed_total từng bên (cap 100)')
for p in (0, 1):
    mx = max((tlp[p][s]['shed_total'], s) for s in range(720))
    over = [(s, tlp[p][s]['shed_total']) for s in range(720) if tlp[p][s]['shed_total'] >= 95]
    print(f'{P[p]}: max={mx[0]} tại s{mx[1]}; các step ≥95: {len(over)}')

# ---------- 6E. LAND AFFORDABILITY ----------
print('\n6E. TIỀN TẠI THỜI ĐIỂM MUA ĐẤT / THỬ MUA:')
for r in orders:
    if r['op'] == 'BUY_LAND':
        m_before = tlp[r['player']][r['step']-1]['money'] if r['step'] > 0 else 3000
        print(f'  s{r["step"]:>3} d{r["day"]} {P[r["player"]]:<8} money_trước={m_before:>8,.0f} → units={r["units"]} cash={r["cash"]:,.0f}')

# ---------- 6F. MAJKEL CASH-STARVED ORDERS ----------
print('\n6F. Orders bị từ chối của Majkel: tiền có được tại step đó (để xác định thiếu tiền)')
mkt_by_s = mkts
n_nocash = n_nostock = 0
rows = []
for r in orders:
    if r['player'] == 1 and r['units'] == 0 and r['op'] in ('BUY_SEED', 'BUY_ANIMAL'):
        s = r['step']
        money = tlp[1][s-1]['money'] if s > 0 else 3000
        # giá cần: seed giá cố định; animal cố định
        need = {'BUY_SEED': {'WHEAT': 10, 'CARROT': 20, 'TOMATO': 50, 'STRAWBERRY': 100, 'MELON': 80},
                'BUY_ANIMAL': {'COW': 400, 'SHEEP': 500, 'GOOSE': 300}}
        cost = need.get(r['op'], {}).get(r['item'], 0)
        if money < cost:
            n_nocash += 1
            rows.append((s, r['day'], r['op'], r['item'], money, cost))
        else:
            n_nostock += 1
print(f'  Bị chặn vì thiếu tiền: {n_nocash}; vì lý do khác (hết slot/vượt giá): {n_nostock}')
for s, d, op, it, money, cost in rows[:20]:
    print(f'    s{s:>3} d{d} {op:<11} {it:<12} money={money:>7,.0f} cần={cost}')
