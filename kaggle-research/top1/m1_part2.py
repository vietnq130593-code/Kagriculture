#!/usr/bin/env python3
"""Part 2: Opening day 0-3 + endgame d27-29 chi tiết."""
import json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(D, 'match1')
orders = json.load(open(os.path.join(M, 'orders.json')))
daily  = json.load(open(os.path.join(M, 'daily.json')))
tl     = json.load(open(os.path.join(M, 'timeline.json')))
market = json.load(open(os.path.join(M, 'market.json')))
summ   = json.load(open(os.path.join(M, 'summary.json')))
P = {0: 'ymg_aq', 1: 'Majkel'}
daily_p = {0: {}, 1: {}}
for r in daily: daily_p[r['player']][r['day']] = r
tl_p = {0: {}, 1: {}}
for r in tl: tl_p[r['player']][r['step']] = r
mkt = {r['step']: r for r in market}

# ---------- 2. OPENING (day 0-3) — mọi order ----------
print('=' * 100)
print('2. OPENING DAY 0-3: mọi order theo thứ tự (step)')
for p in (0, 1):
    print(f'\n--- {P[p]} (p{p}) ---')
    for r in orders:
        if r['player'] == p and r['day'] <= 3:
            pr = r['prices']
            prs = ','.join(str(x) for x in pr[:3]) + ('...' if len(pr) > 3 else '')
            print(f"  s{r['step']:>3} d{r['day']} {r['op']:<12} {str(r['item']):<12} asked={r['asked']:>4} units={r['units']:>4} cash={r['cash']:>8,.0f} px=[{prs}]")

# plants/animals/hands theo ngày 0-3
print('\nTrạng thái cuối mỗi ngày d0-d3:')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    for d in range(4):
        r = daily_p[p][d]
        print(f"  d{d}: hands={r['hands_max']} quad={r['quadrants']} plants={r['plants']} animals={r['animals']} "
              f"hire=${r['hire_spend']} land=${r['land_spend']} money_end={r['money_end']:,.0f}")

# ---------- ENDGAME: d26-29 step-level money + sells ----------
print('\n' + '=' * 100)
print('ENDGAME d26-29: mỗi step có SELL hoặc đổi tiền lớn')
for s in range(26 * 24, 720):
    a, b = tl_p[0][s], tl_p[1][s]
    sells = [r for r in orders if r['step'] == s and r['op'] == 'SELL']
    buys = [r for r in orders if r['step'] == s and r['op'] in ('BUY_PRODUCT', 'BUY_SEED', 'BUY_ANIMAL', 'BUY_LAND', 'HIRE') and r['units'] > 0]
    if sells or buys:
        print(f"s{s:>3} d{s//24:>2} h{s%24:>2} | money ymg={a['money']:>8,.0f} maj={b['money']:>8,.0f} diff={a['money']-b['money']:>+7,.0f}")
        for r in sells:
            who = P[r['player']]
            avg = (r['cash'] / r['units']) if r['units'] else 0
            print(f"        SELL {who:<8} {r['item']:<11} units={r['units']:>3} cash={r['cash']:>7,.0f} avg={avg:>6,.1f}")
        for r in buys:
            who = P[r['player']]
            avg = (abs(r['cash']) / r['units']) if r['units'] else 0
            print(f"        {r['op']:<11} {who:<8} {str(r['item']):<11} units={r['units']:>3} cash={r['cash']:>7,.0f} avg={avg:>6,.1f}")

# shed inventory theo ngày cuối (d26-d29 cuối ngày)
print('\nShed inventory cuối mỗi ngày d24-29:')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    for d in range(24, 30):
        r = daily_p[p][d]
        sh = {k: v for k, v in r['shed'].items() if v > 0}
        print(f"  d{d}: shed={sh} total={sum(sh.values())}")
