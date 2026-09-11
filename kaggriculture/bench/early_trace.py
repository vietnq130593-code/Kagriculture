#!/usr/bin/env python3
"""Debug d0-9: in orders + money + shed cua agent A moi gio."""
import sys, os
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make

a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
env = make("kaggriculture", debug=False, configuration={"seed": seed})
env.run([a, b])

for si, step in enumerate(env.steps):
    if si % 24 != 0 and si % 24 != 23:
        continue
    # obs cua player 0
    try:
        obs = step[0]['observation']
    except Exception:
        continue
    day = si // 24
    hour = si % 24
    if day > 9:
        break
    money = obs['farms'][0]['money']
    tiles = obs['farms'][0]['tiles']
    nq = len(obs['farms'][0].get('unlocked_quadrants', ['NW']))
    empty = sum(1 for row in tiles for t in row if t is None)
    shed = obs['private']['shed'] if 'private' in obs else {}
    print(f"d{day}h{hour:02d} nq={nq} money=${money:7.0f} empty={empty:2d} shed={ {k:v for k,v in shed.items() if v} }")
# in orders dau tien moi ngay tu replay? khong co — in actions tu steps
print('--- actions (market orders) d3-8 ---')
for si, step in enumerate(env.steps):
    day = si // 24
    if not (3 <= day <= 8):
        continue
    acts = step[0].get('action')
    if isinstance(acts, dict):
        m = acts.get('market', [])
        if m:
            print(f"d{day}h{si%24:02d}: {m}")
