#!/usr/bin/env python3
"""Chi phí theo danh mục từ battles/*.jsonl."""
import json, sys
from collections import defaultdict

SEED_PX = {'WHEAT': 10, 'CARROT': 20, 'TOMATO': 50, 'STRAWBERRY': 100, 'MELON': 80}
ANIM_PX = {'GOOSE': 300, 'COW': 400, 'SHEEP': 500}

def _J(x):
    return json.loads(x) if isinstance(x, str) else x

def analyze(path):
    lines = [json.loads(l) for l in open(path)]
    hello = lines[0]
    names = [hello.get('a'), hello.get('b')]
    spend = [defaultdict(float), defaultdict(float)]
    seed_cnt = [defaultdict(int), defaultdict(int)]
    hire_cost = [0.0, 0.0]
    FIB = [1, 1]
    for ln in lines:
        if ln.get('t') != 'turn':
            continue
        acts = _J(ln.get('acts'))
        market = _J(ln.get('market'))
        if not isinstance(acts, list):
            continue
        prices = market.get('prices', {}) if isinstance(market, dict) else {}
        for pid in range(2):
            if pid >= len(acts):
                continue
            for o in acts[pid].get('market', []):
                if not o:
                    continue
                op = o[0]
                if op == 'BUY_SEED' and len(o) >= 3:
                    n = int(o[2])
                    spend[pid]['seed_' + o[1]] += n * SEED_PX.get(o[1], 0)
                    seed_cnt[pid][o[1]] += n
                elif op == 'BUY_ANIMAL' and len(o) >= 3:
                    n = int(o[2])
                    spend[pid]['animal_' + o[1]] += n * ANIM_PX.get(o[1], 0)
                elif op == 'BUY_PRODUCT' and len(o) >= 3:
                    n = int(o[2])
                    spend[pid]['buyprod_' + o[1]] += n * float(prices.get(o[1], 0))
                elif op == 'HIRE':
                    spend[pid]['hire'] += 0  # tính riêng dưới
                elif op == 'BUY_LAND':
                    spend[pid]['land'] += 0
    # land + hire: tính từ farms money khi đơn atomic
    land_px = [1000, 2000, 4000]
    prev_money = [None, None]
    prev_nq = [1, 1]
    hire_today = [0, 0]
    prev_day = -1
    def fib(n):
        a, b = 1, 1
        for _ in range(n):
            a, b = b, a + b
        return a
    for ln in lines:
        if ln.get('t') != 'turn':
            continue
        farms = _J(ln.get('farms'))
        acts = _J(ln.get('acts'))
        if not isinstance(farms, list) or not isinstance(acts, list) or len(farms) < 2:
            continue
        day = int(ln.get('day', 0))
        if day != prev_day:
            hire_today = [0, 0]
            prev_day = day
        for pid in range(2):
            if pid >= len(acts):
                continue
            orders = acts[pid].get('market', [])
            nq = len(farms[pid].get('unlocked_quadrants', ['NW']))
            if nq > prev_nq[pid]:
                spend[pid]['land'] += land_px[prev_nq[pid] - 1]
                prev_nq[pid] = nq
            nh = sum(1 for o in orders if o and o[0] == 'HIRE')
            if nh:
                for k in range(nh):
                    hire_today[pid] += 1
                    spend[pid]['hire'] += fib(hire_today[pid] - 1)
    end = lines[-1]
    print('==', path.split('/')[-1], '->', names)
    for pid in range(2):
        tot = sum(spend[pid].values())
        det = ', '.join(f"{k.replace('seed_','').replace('animal_','')}:{v/1000:.1f}k" for k, v in sorted(spend[pid].items(), key=lambda kv: -kv[1]))
        print(f"  [{names[pid]}] final={end['rewards'][pid]:.0f}  TỔNG CHI ${tot:.0f} | {det}")
        print(f"      hạt: {dict(seed_cnt[pid])}")

if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            analyze(p)
        except Exception as ex:
            print('!!', p, ex)
