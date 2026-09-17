#!/usr/bin/env python3
"""Part 4: SELL chi tiết theo item, sell timing vs giá, rejected orders, shops, tương tác."""
import json, os
from collections import defaultdict

D = os.path.dirname(os.path.abspath(__file__))
M = os.path.join(D, 'match1')
orders = json.load(open(os.path.join(M, 'orders.json')))
daily  = json.load(open(os.path.join(M, 'daily.json')))
tl     = json.load(open(os.path.join(M, 'timeline.json')))
market = json.load(open(os.path.join(M, 'market.json')))
town   = json.load(open(os.path.join(M, 'town.json')))
P = {0: 'ymg_aq', 1: 'Majkel'}
mkt = {r['step']: r for r in market}

# ---------- 6a. SELL theo item ----------
print('=' * 100)
print('6a. SELL theo item: units, revenue, avg price')
items = set()
for r in orders:
    if r['op'] == 'SELL' and r['units'] > 0:
        items.add(r['item'])
print(f'{"item":<12} | {"ymg units":>9} {"ymg rev":>9} {"ymg avg":>8} | {"mk units":>9} {"mk rev":>9} {"mk avg":>8}')
for it in sorted(items):
    row = []
    for p in (0, 1):
        u = c = 0
        for r in orders:
            if r['player'] == p and r['op'] == 'SELL' and r['item'] == it and r['units'] > 0:
                u += r['units']; c += r['cash']
        row.append((u, c))
    (u0, c0), (u1, c1) = row
    a0 = c0 / u0 if u0 else 0; a1 = c1 / u1 if u1 else 0
    print(f'{it:<12} | {u0:>9} {c0:>9,.0f} {a0:>8,.1f} | {u1:>9} {c1:>9,.0f} {a1:>8,.1f}')

# ---------- 6b. SELL timing vs market price ----------
print('\n6b. SELL TIMING vs giá thị trường (mỗi item: bán ở phần trăm nào của biên độ giá)')
print('    % vị trí giá khi bán = (px - min) / (max - min) trên toàn trận; 100% = bán ở đỉnh')
for it in sorted(items):
    for p in (0, 1):
        pxs = []
        for r in orders:
            if r['player'] == p and r['op'] == 'SELL' and r['item'] == it and r['units'] > 0:
                for i, pr in enumerate(r['prices'][:r['units']]):
                    pxs.append(pr)
        if not pxs: continue
        allpx = [m['prices'][it] for m in market]
        lo, hi = min(allpx), max(allpx)
        avg = sum(pxs) / len(pxs)
        pos = (avg - lo) / (hi - lo) * 100 if hi > lo else 50
        print(f'  {it:<12} {P[p]:<8}: n_sell_px={len(pxs):>4} avg_sell_px={avg:>7,.1f} '
              f'market[{lo:.0f}..{hi:.0f}] avg_all={sum(allpx)/len(allpx):>7,.1f} vị-trí={pos:>5.1f}%')

# giá thị trường theo từng mốc ngày cho các item chính
print('\nGiá thị trường (step 0/120/240/360/480/600/696/719):')
hdr = ['step'] + [f'{it[:5]}' for it in ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']]
print('  ' + ' '.join(f'{h:>8}' for h in hdr))
for s in [0, 120, 240, 360, 480, 600, 696, 719]:
    row = [f'{s:>8}'] + [f"{mkt[s]['prices'][it]:>8}" for it in ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']]
    print('  ' + ' '.join(row))

# ---------- 6c. REJECTED ORDERS ----------
print('\n6c. ORDERS BỊ TỪ CHỐI (units=0)')
for p in (0, 1):
    rej = defaultdict(int); rej_detail = []
    for r in orders:
        if r['player'] == p and r['units'] == 0:
            rej[(r['op'], r['item'])] += 1
    print(f'--- {P[p]}: tổng {sum(rej.values())} order bị từ chối ---')
    for (op, it), n in sorted(rej.items(), key=lambda x: -x[1]):
        print(f'  {op:<12} {str(it):<12} × {n}')
    # tiền tại thời điểm bị từ chối (nếu biết)
tlp = {0: {}, 1: {}}
for r in tl: tlp[r['player']][r['step']] = r
print('\nChi tiết order BUY_SEED/BUY_PRODUCT bị từ chối + tiền lúc đó:')
for p in (0, 1):
    n_starved = 0
    for r in orders:
        if r['player'] == p and r['units'] == 0 and r['op'] in ('BUY_SEED', 'BUY_PRODUCT', 'BUY_ANIMAL'):
            money = tlp[p][r['step']-1]['money'] if r['step'] > 0 else 3000
            if money < (r['prices'][0] if r['prices'] else 0) + 5:
                n_starved += 1
    print(f'  {P[p]}: {n_starved}/... bị chặn vì hết tiền')

# ---------- 7. SHOPS ----------
print('\n' + '=' * 100)
print('7. SHOPS: unlock theo ngày')
seen = {}
for r in town:
    for s in r['shops']:
        nm = s if isinstance(s, str) else s.get('name')
        if nm not in seen:
            seen[nm] = (r['step'], r['step'] // 24)
for nm, (s, d) in seen.items():
    print(f'  MỞ: step {s} (d{d}): {nm}')
print(f'  Số shop instance cuối trận: {len(town[-1]["shops"])}')

# ---------- 7b. Cả 2 cùng bán 1 item trong cùng step ----------
print('\n7b. CẢ HAI BÁN CÙNG ITEM TRONG CÙNG STEP (đua giá trực tiếp)')
coll = 0
for r in orders:
    if r['op'] != 'SELL' or r['units'] == 0: continue
    for r2 in orders:
        if r2['step'] == r['step'] and r2['player'] != r['player'] and r2['op'] == 'SELL' and r2['item'] == r['item'] and r2['units'] > 0 and r['player'] == 0:
            print(f'  s{r["step"]:>3} d{r["day"]}: cả hai SELL {r["item"]}: ymg {r["units"]}u@{r["cash"]/r["units"]:.0f} vs Majkel {r2["units"]}u@{r2["cash"]/r2["units"]:.0f}')
            coll += 1
print(f'  Tổng {coll} cặp cùng-step cùng-item')

# ---------- 7c. Tổng SELL units mỗi ngày mỗi item (pivot quanh shop) ----------
print('\n7c. SELL units theo (ngày, item) — mỗi bên (chỉ ngày có bán)')
for p in (0, 1):
    print(f'--- {P[p]} ---')
    per = defaultdict(lambda: defaultdict(int))
    for r in orders:
        if r['player'] == p and r['op'] == 'SELL' and r['units'] > 0:
            per[r['day']][r['item']] += r['units']
    its = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']
    print('      ' + ''.join(f'{i[:5]:>7}' for i in its))
    for d in range(30):
        if per[d]:
            print(f'  d{d:>2} ' + ''.join(f'{per[d].get(i, 0):>7}' for i in its))
