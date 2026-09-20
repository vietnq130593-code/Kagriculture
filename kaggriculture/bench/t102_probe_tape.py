#!/usr/bin/env python3
"""T102 probe: dump thomast2945 (seat B) behaviour days 15-29 vs v26c, seed 101.

Goal: find free labour + dead-straw tiles for a TOMATO channel layer.
"""
import json, sys
from kaggle_environments import make

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 101
A = "/home/z/my-project/kaggriculture/v26c.py"
B = "/home/z/my-project/kaggriculture/thomast2945.py"

env = make("kaggriculture", debug=False, configuration={"seed": SEED})
env.run([A, B])

# per-day census of B's farm + B's commands
def cmdstat(cmds):
    from collections import Counter
    c = Counter()
    for u in cmds:
        op = u[0] if u else "PASS"
        if op in ("PLANT", "WATER", "HARVEST", "FERTILIZE"):
            c[op + ":" + (u[1] if len(u) > 1 else "?")] += 1
        else:
            c[op] += 1
    return dict(c)

def tile_census(farm):
    from collections import Counter
    c = Counter()
    straw_age = Counter()
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    c["P:" + t["crop"]] += 1
                    if t["crop"] == "STRAWBERRY":
                        straw_age[t.get("planted_day", -9)] += 1
                elif "animal" in t:
                    c["A:" + t["animal"]] += 1
                elif t.get("kind") == "WEED":
                    c["WEED"] += 1
                else:
                    c[t.get("kind", "?")] += 1
            elif t is None:
                c["EMPTY"] += 1
    return c, straw_age

out = []
for step in range(0, 720, 24):
    day = step // 24
    obsB = env.steps[step][1]
    obsA = env.steps[step][0]
    actB = env.steps[step][1]["action"] or {}
    farmB = obsB["observation"]["farms"][1] if "farms" in obsB.get("observation", {}) else None
    # actions recorded on state entries
    cmds = [actB.get("farmer")] + list(actB.get("hands") or [])
    cen, straw = tile_census(farmB) if farmB else ({}, {})
    out.append({"day": day, "Bcmds": cmdstat(cmds), "Btiles": cen,
                "straw_planted_days": dict(straw),
                "Bmoney": farmB["money"] if farmB else 0,
                "Btom_sold": 0})

# market: count tomato sells by B over the game
tomA = tomB = 0
for step in range(720):
    for seat in (0, 1):
        e = env.steps[step][seat]
        a = e.get("action") or {}
        for o in (a.get("market") or []):
            if o and o[0] == "SELL" and o[1] == "TOMATO":
                if seat == 0: tomA += int(o[2])
                else: tomB += int(o[2])
print("TOMATO sell orders: A(v26c)=", tomA, " B(2945)=", tomB)
r0 = env.steps[-1][0]["reward"]
r1 = env.steps[-1][1]["reward"]
print("FINAL A=", r0, "B=", r1, "gap=", (r0 - r1))
for row in out:
    print(json.dumps(row))
