#!/usr/bin/env python3
"""Part 5: production engine — verbs, yields, animal economy, d29 production, market inventory."""
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

# ---------- VERBS tổng ----------
print('=' * 100)
print('5a. VERBS TỔNG CẢ TRẬN (đếm lệnh)')
for p in (0, 1):
    agg = defaultdict(int)
    for d in range(30):
        for k, v in daily_p[p][d]['verbs'].items():
            agg[k] += v
    print(f'--- {P[p]} ---')
    print('  ' + ', '.join(f'{k}={v}' for k, v in sorted(agg.items(), key=lambda x: -x[1])))

# FEED/CARE/FERTILIZE theo giai đoạn
print('\nFEED/CARE/FERTILIZE/PLANT/WATER/HARVEST theo giai đoạn 5 ngày:')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    for lo in range(0, 30, 5):
        hi = min(lo + 5, 30)
        f = c = fe = pl = wa = ha = 0
        for d in range(lo, hi):
            v = daily_p[p][d]['verbs']
            f += v.get('FEED', 0); c += v.get('CARE', 0); fe += v.get('FERTILIZE', 0)
            pl += v.get('PLANT', 0); wa += v.get('WATER', 0); ha += v.get('HARVEST', 0)
        print(f'  d{lo}-{hi-1}: PLANT={pl:>3} WATER={wa:>4} HARVEST={ha:>4} FEED={f:>4} CARE={c:>4} FERTILIZE={fe:>3}')

# ---------- 5b. Animal economy ----------
print('\n' + '=' * 100)
print('5b. KINH TẾ ĐỘNG VẬT: animal-days, sản phẩm, ROI')
for p in (0, 1):
    # animal-days
    ad = defaultdict(int)
    for r in tl:
        if r['player'] != p or r['hour'] != 23: continue
        for a, n in r['animals'].items():
            ad[a] += n
    print(f'--- {P[p]} --- animal-days: {dict(ad)} (tổng {sum(ad.values())})')
    # doanh thu sản phẩm động vật
    rev = defaultdict(lambda: [0, 0.0])
    for r in orders:
        if r['player'] == p and r['op'] == 'SELL' and r['item'] in ('EGG', 'MILK', 'WOOL', 'FERTILIZER') and r['units'] > 0:
            rev[r['item']][0] += r['units']; rev[r['item']][1] += r['cash']
    for k, (u, c) in sorted(rev.items()):
        print(f'    SELL {k:<11} {u:>4} units ${c:>8,.0f} (avg {c/u:>6,.1f})')
    animal_spend = sum(abs(r['cash']) for r in orders if r['player'] == p and r['op'] == 'BUY_ANIMAL' and r['units'] > 0)
    feedw = sum(r['units'] for r in orders if r['player'] == p and r['op'] == 'BUY_PRODUCT' and r['item'] == 'WHEAT' and r['units'] > 0)
    feedcost = sum(abs(r['cash']) for r in orders if r['player'] == p and r['op'] == 'BUY_PRODUCT' and r['item'] == 'WHEAT' and r['units'] > 0)
    tot_rev = sum(c for u, c in rev.values())
    print(f'    animal_spend=${animal_spend:,.0f}; feed mua {feedw} WHEAT ${feedcost:,.0f}; '
          f'tổng doanh thu EGG+MILK+WOOL+FERT=${tot_rev:,.0f}')
    print(f'    ROI vòng đời = (rev − animal − feed) / (animal + feed) = {(tot_rev - animal_spend - feedcost)/(animal_spend+feedcost)*100:.0f}%')

# ---------- 5c. d29 PRODUCTION ----------
print('\n' + '=' * 100)
print('5c. NGÀY 29 CHI TIẾT: sell theo item + profit ngày')
for p in (0, 1):
    r = daily_p[p][29]
    print(f'--- {P[p]} --- money {r["money_start"]:,.0f} → {r["money_end"]:,.0f} (profit {r["profit_day"]:+,.0f})')
    for it, v in sorted(r['sells'].items(), key=lambda x: -x[1]['cash']):
        print(f'    SELL {it:<11} {v["units"]:>3} units ${v["cash"]:>7,.0f} (avg {v["cash"]/v["units"]:>6,.1f})')
    print(f'    buys: { {k: (v["units"], v["cash"]) for k, v in r["buys"].items()} }')
    print(f'    hire=${r["hire_spend"]:,.0f} verbs.PLANT={r["verbs"].get("PLANT",0)} HARVEST={r["verbs"].get("HARVEST",0)} '
          f'WATER={r["verbs"].get("WATER",0)} FEED={r["verbs"].get("FEED",0)}')

# d27-29 sells từng bên (3 ngày cuối)
print('\nDoanh thu 3 ngày cuối (d27, d28, d29):')
for p in (0, 1):
    for d in (27, 28, 29):
        r = daily_p[p][d]
        tot = sum(v['cash'] for v in r['sells'].values())
        units = sum(v['units'] for v in r['sells'].values())
        print(f'  {P[p]:<8} d{d}: {units:>4} units ${tot:>8,.0f}')

# ---------- 5d. MARKET INVENTORY các item chính ----------
print('\n' + '=' * 100)
print('5d. MARKET INVENTORY theo mốc (độ lệch so với I0=10,000):')
mkts = {r['step']: r for r in market}
for s in [0, 48, 96, 144, 192, 240, 288, 360, 432, 480, 540, 600, 660, 719]:
    r = mkts[s]
    inv = {k: (v - 10000) for k, v in r['inventory'].items()}
    print(f'  s{s:>3} d{s//24:>2}: ' + ' '.join(f'{k[:4]}:{inv[k]:>+5}' for k in ['WHEAT','CARROT','TOMATO','STRAWBERRY','MELON','EGG','MILK','WOOL','FERTILIZER']))

# ---------- 5e. NGÀY CÓ SELL LỚN NHẤT ----------
print('\nTop 10 step có revenue lớn nhất mỗi bên:')
for p in (0, 1):
    per = defaultdict(float)
    for r in orders:
        if r['player'] == p and r['op'] == 'SELL' and r['units'] > 0:
            per[r['step']] += r['cash']
    top = sorted(per.items(), key=lambda x: -x[1])[:10]
    print(f'--- {P[p]} ---')
    for s, c in top:
        its = [f"{r['item']}x{r['units']}" for r in orders if r['step'] == s and r['player'] == p and r['op'] == 'SELL' and r['units'] > 0]
        print(f'  s{s:>3} d{s//24:>2} h{s%24:>2}: ${c:>7,.0f} | {", ".join(its)}')
