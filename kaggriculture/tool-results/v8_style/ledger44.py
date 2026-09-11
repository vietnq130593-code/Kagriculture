#!/usr/bin/env python3
"""Ledger: doanh thu theo kênh + buys — NEW vs BASE trên 1 seed."""
import sys
sys.path.insert(0, '/home/z/my-project/kaggriculture')
from kaggle_environments import make

A = '/home/z/my-project/kaggriculture/v8.py'
B = '/tmp/v8_base.py'
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 203

env = make("kaggriculture", debug=False, configuration={"seed": SEED})
env.run([A, B])

# market orders live in step actions: [farmer, hands, market]
rev = {0: {}, 1: {}}
buys = {0: {}, 1: {}}
for si, step in enumerate(env.steps):
    day = step[0].observation.day
    if day < 20:
        continue
    for p in (0, 1):
        act = step[p].action
        if not isinstance(act, dict):
            continue
        for o in (act.get("market") or []):
            if o and o[0] == "SELL" and len(o) >= 3:
                it, n = o[1], o[2]
                rev[p][it] = rev[p].get(it, 0) + n
            if o and o[0] in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL", "HIRE", "BUY_LAND") :
                k = o[0] + ":" + (o[1] if len(o) > 1 else "")
                buys[p][k] = buys[p].get(k, 0) + 1

r0 = env.steps[-1][0].reward
r1 = env.steps[-1][1].reward
print(f"FINAL: NEW ${r0:,.0f} vs BASE ${r1:,.0f}")
print("d20+ SELL units  NEW:", rev[0])
print("d20+ SELL units BASE:", rev[1])
print("d20+ BUY orders NEW:", buys[0])
print("d20+ BUY orders BASE:", buys[1])
