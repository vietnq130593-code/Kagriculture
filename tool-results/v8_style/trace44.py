#!/usr/bin/env python3
"""Task 44 trace: v8-5trụ vs v8-base — day-by-day money/herd/tiles/feed."""
import sys, json
sys.path.insert(0, '/home/z/my-project/kaggriculture')
from kaggle_environments import make

A = '/home/z/my-project/kaggriculture/v8.py'
B = '/home/z/my-project/kaggriculture/v6.py'
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 115

env = make("kaggriculture", debug=False, configuration={"seed": SEED})
env.run([A, B])

last_day = -1
for step in env.steps:
    obs = step[0].observation
    d, h = obs.day, obs.hour
    if d != last_day and h == 23:
        last_day = d
        for p in (0, 1):
            f = obs.farms[p]
            priv = step[p].observation.private
            tiles = f.tiles
            nw = sum(1 for row in tiles for t in row if t == "LOCKED")
            empty = sum(1 for row in tiles for t in row if t is None)
            weeds = sum(1 for row in tiles for t in row
                        if isinstance(t, dict) and t.get("kind") == "WEED")
            plants = {}
            herd = {}
            hungry = 0
            for row in tiles:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT":
                        plants[t.get("crop")] = plants.get(t.get("crop"), 0) + 1
                    if isinstance(t, dict) and "animal" in t:
                        herd[t.get("animal")] = herd.get(t.get("animal"), 0) + 1
                        if (t.get("consecutive_unfed", 0) or 0) >= 1:
                            hungry += 1
            shed = dict(priv.shed)
            name = "NEW" if p == 0 else "BASE"
            print(f"d{d:02d} {name} ${f.money:>7,.0f} herd={herd} hungry={hungry} "
                  f"wheat_shed={shed.get('WHEAT',0)} empty={empty} weed={weeds} "
                  f"plants={plants}", flush=True)
        print()

r0 = env.steps[-1][0].reward
r1 = env.steps[-1][1].reward
print(f"FINAL seed {SEED}: NEW ${r0:,.0f} vs BASE ${r1:,.0f}")
