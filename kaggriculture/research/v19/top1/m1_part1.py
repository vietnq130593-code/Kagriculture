#!/usr/bin/env python3
"""Phân tích match1: ymg_aq (p0) vs Majkel1337 (p1), episode 109776263."""
import json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(D, 'match1')

orders = json.load(open(os.path.join(M, 'orders.json')))
daily  = json.load(open(os.path.join(M, 'daily.json')))
tl     = json.load(open(os.path.join(M, 'timeline.json')))
market = json.load(open(os.path.join(M, 'market.json')))
town   = json.load(open(os.path.join(M, 'town.json')))
summ   = json.load(open(os.path.join(M, 'summary.json')))

P = {0: 'ymg_aq', 1: 'Majkel'}
CAT = {'SELL': 'sell', 'BUY_PRODUCT': 'product', 'BUY_SEED': 'seed',
       'BUY_ANIMAL': 'animal', 'HIRE': 'hire', 'BUY_LAND': 'land'}

# ---------- helpers ----------
def dd(): return defaultdict(float)

daily_p = {0: {}, 1: {}}
for r in daily:
    daily_p[r['player']][r['day']] = r

tl_p = {0: defaultdict(list), 1: defaultdict(list)}
for r in tl:
    tl_p[r['player']][r['step']] = r
tl_by_step = {}
for r in tl:
    tl_by_step.setdefault(r['step'], {})[r['player']] = r

mkt_by_step = {r['step']: r for r in market}

def money_at(p, step):
    return tl_p[p][step]['money']

# ---------- 1. MONEY CURVE ----------
print('=' * 100)
print('1. MONEY CURVE THEO NGÀY (money_end mỗi ngày)')
print(f"{'day':>3} | {'ymg_aq':>10} {'Majkel':>10} | {'diff(+ymg)':>10} | lead")
rows = []
for d in range(30):
    a = daily_p[0][d]['money_end']; b = daily_p[1][d]['money_end']
    diff = a - b
    rows.append((d, a, b, diff))
    print(f"{d:>3} | {a:>10,.0f} {b:>10,.0f} | {diff:>+10,.0f} | {'ymg_aq' if diff>0 else ('Majkel' if diff<0 else 'TIE')}")

# số ngày dẫn đầu
ymg_lead = sum(1 for r in rows if r[3] > 0)
maj_lead = sum(1 for r in rows if r[3] < 0)
print(f'\nNgày ymg_aq dẫn: {ymg_lead}, Majkel dẫn: {maj_lead}')

# tìm các bước giao nhau trong timeline (step-level crossover)
prev = None; crossovers = []
for s in range(720):
    a = money_at(0, s); b = money_at(1, s)
    sign = (a > b) - (a < b)
    if prev is not None and sign != prev[1] and sign != 0:
        crossovers.append((s, s // 24, s % 24, prev[0], a, b))
    prev = (s, sign)
print('\nCROSSOVER (step-level, đổi bên dẫn đầu):')
for c in crossovers:
    print(f'  step {c[0]} (d{c[1]} h{c[2]}): trước ymg-maj = {c[3]:,.0f} → sau = {c[4]-c[5]:,.0f}')

# min money mỗi bên (idle cash proxy)
for p in (0, 1):
    mns = [money_at(p, s) for s in range(720)]
    print(f'\n{P[p]}: min money = {min(mns):,.0f} tại step {mns.index(min(mns))}; '
          f'money trung bình = {sum(mns)/720:,.0f}; cuối = {mns[-1]:,.0f}')

# tiền "đang nằm" trung bình giai đoạn cuối
for p in (0, 1):
    mns = [money_at(p, s) for s in range(600, 720)]
    print(f'{P[p]}: avg money step 600-719 = {sum(mns)/120:,.0f}')
