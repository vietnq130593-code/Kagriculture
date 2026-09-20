#!/usr/bin/env python3
"""T102 autopsy: v26c vs thomast2945 — money curves + sell flow per product/day.

Usage: python3 t102_autopsy.py <seed> [aseat]
"""
import sys, json
from collections import defaultdict
from kaggle_environments import make

V26 = "/home/z/my-project/kaggriculture/v26c.py"
T29 = "/home/z/my-project/kaggriculture/thomast2945.py"

seed = int(sys.argv[1])
aseat = int(sys.argv[2]) if len(sys.argv) > 2 else 0
paths = [V26, T29] if aseat == 0 else [T29, V26]

env = make("kaggriculture", debug=False, configuration={"seed": seed})
env.run(paths)

# players: 0,1 -> names
names = {aseat: "v26c", 1 - aseat: "2945"}

money = {p: [] for p in (0, 1)}          # per day-end
sells = {p: defaultdict(lambda: defaultdict(int)) for p in (0, 1)}  # sells[p][item][day] = units
prices_log = []
weeds = {p: [] for p in (0, 1)}
census = {p: {} for p in (0, 1)}

prev_money = {0: None, 1: None}
for t in range(720):
    for p in (0, 1):
        e = env.steps[t][p]
        obs = e.get("observation", {})
        act = e.get("action") or {}
        farm = obs.get("farms", [None, None])[p]
        if farm is None:
            continue
        day = t // 24
        for o in (act.get("market") or []):
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                sells[p][o[1]][day] += int(o[2])
        if t % 24 == 23:
            money[p].append((day, float(farm["money"])))
        if t % 24 == 0:
            tiles = farm["tiles"]
            c = defaultdict(int)
            for row in tiles:
                for tl in row:
                    if isinstance(tl, dict):
                        if tl.get("kind") == "PLANT":
                            c["P:" + tl["crop"]] += 1
                        elif "animal" in tl:
                            c["A:" + tl["animal"]] += 1
            census[p][day] = dict(c)
    if t % 96 == 0:
        prices_log.append((t // 24, dict(env.steps[t][0]["observation"]["market"]["prices"])))

print(f"=== seed {seed} (v26c seat{aseat}) FINAL: v26c={env.steps[-1][aseat]['reward']} 2945={env.steps[-1][1-aseat]['reward']}")
for p in (0, 1):
    d = dict(money[p])
    print(names[p], "money:", " ".join(f"d{dd}:{dm:.0f}" for dd, dm in sorted(d.items())))
for p in (0, 1):
    print(names[p], "SELLS (units by day):")
    for item in sorted(sells[p]):
        row = sells[p][item]
        tot = sum(row.values())
        if tot:
            print(f"  {item:11s} tot={tot:5d} ", " ".join(f"d{k}:{v}" for k, v in sorted(row.items())))
print("PRICES (every 4d):", json.dumps(prices_log, default=str)[:1500])
for p in (0, 1):
    print(names[p], "census:", json.dumps(census[p], default=str)[:1200])
