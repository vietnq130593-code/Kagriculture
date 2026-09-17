#!/usr/bin/env python3
"""Phân tích money-profile từ battles/*.jsonl: doanh thu theo kênh + đất + empty."""
import json, sys, statistics
from collections import defaultdict

def _J(x):
    return json.loads(x) if isinstance(x, str) else x

def analyze(path):
    lines = [json.loads(l) for l in open(path)]
    hello = lines[0]
    a_name, b_name = hello.get('a', 'A'), hello.get('b', 'B')
    rev = [defaultdict(float), defaultdict(float)]
    units = [defaultdict(int), defaultdict(int)]
    empty_daily = [[], []]
    land_buy = [[], []]
    end = None
    for ln in lines:
        t = ln.get('t')
        if t == 'end':
            end = ln
            continue
        if t != 'turn':
            continue
        farms = _J(ln.get('farms'))
        acts = _J(ln.get('acts'))
        market = _J(ln.get('market'))
        if not isinstance(farms, list) or not isinstance(acts, list) or market is None:
            continue
        day = int(ln.get('day', 0))
        prices = market.get('prices', {}) if isinstance(market, dict) else {}
        for pid in range(2):
            if pid >= len(acts) or pid >= len(farms):
                continue
            # doanh thu ước tính theo giá turn
            for o in acts[pid].get('market', []):
                if o and o[0] == 'SELL' and len(o) >= 3:
                    item, n = o[1], int(o[2])
                    px = prices.get(item, 0)
                    rev[pid][item] += n * float(px)
                    units[pid][item] += n
            # đất & empty: ghi 1 lần/ngày (h0)
            if day > 4 and int(ln.get('hour', 0)) == 0:
                tiles = farms[pid]['tiles']
                empty = sum(1 for row in tiles for tt in row if tt is None)
                owned = sum(1 for row in tiles for tt in row if tt != 'LOCKED')
                nq = len(farms[pid].get('unlocked_quadrants', ['NW']))
                empty_daily[pid].append((day, empty, owned, nq))
    print(f"=== {path.split('/')[-1]} | {a_name}(0) vs {b_name}(1) ===")
    if end:
        print(f"  rewards={end.get('rewards')} winner={end.get('winner')}")
    for pid, name in enumerate([a_name, b_name]):
        tot = sum(rev[pid].values())
        det = ", ".join(f"{it}:{units[pid][it]}u/${rev[pid][it]/1000:.1f}k" for it in sorted(rev[pid], key=lambda k: -rev[pid][k]))
        print(f"  [{name}] ~total ${tot/1000:.1f}k | {det}")
        after75 = [e for (d, e, o, nq) in empty_daily[pid] if nq >= 3 and d >= 14]
        if after75:
            em = statistics.mean(after75)
            print(f"    empty d14+ (sau đủ 3 quadrant): trung bình {em:.1f} ô")
        nq_last = empty_daily[pid][-1][3] if empty_daily[pid] else 0
        print(f"    quadrants cuối: {nq_last} ({nq_last*25} ô)")

if __name__ == '__main__':
    for p in sys.argv[1:]:
        try:
            analyze(p)
        except Exception as ex:
            print(f"!! {p}: {ex}")
