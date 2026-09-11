#!/usr/bin/env python3
"""Đếm action types theo giờ trong 1 ngày — nhìn lao động đi đâu."""
import sys, json
from collections import Counter
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make

a, b, seed, d_lo, d_hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
env = make("kaggriculture", debug=False, configuration={"seed": seed})
env.run([a, b])

for si, step in enumerate(env.steps):
    day = si // 24
    if not (d_lo <= day <= d_hi) or si % 24 != 0:
        continue
    # quét cả ngày
    cnt = Counter()
    for sj in range(si, min(si + 24, len(env.steps))):
        act = env.steps[sj][0].get('action')
        if isinstance(act, dict):
            ops = [act.get('farmer')] + [h for h in (act.get('hands') or [])]
            for op in ops:
                if isinstance(op, list) and op:
                    cnt[op[0]] += 1
    obs = env.steps[min(si + 23, len(env.steps) - 1)][0]['observation']
    money = obs['farms'][0]['money']
    tiles = obs['farms'][0]['tiles']
    empty = sum(1 for row in tiles for t in row if t is None)
    straw = sum(1 for row in tiles for t in row
                if isinstance(t, dict) and t.get('crop') == 'STRAWBERRY')
    print(f"d{day}: money=${money:6.0f} empty={empty:2d} straw={straw:2d} | {dict(cnt)}")
