#!/usr/bin/env python3
"""T102 diff probe: my farm's daily money+census in mirror vs v26d battles."""
import sys
from kaggle_environments import make

SEED = 100
T29 = "/home/z/my-project/kaggriculture/thomast2945.py"
V26D = "/home/z/my-project/kaggriculture/v26d.py"

def probe(paths, myidx):
    env = make("kaggriculture", debug=False, configuration={"seed": SEED})
    env.run(paths)
    out = {}
    sells = {}
    for t in range(720):
        e = env.steps[t][myidx]
        obs = e.get("observation", {})
        act = e.get("action") or {}
        farm = obs.get("farms", [None, None])[myidx]
        if farm is None: continue
        day = t // 24
        for o in (act.get("market") or []):
            if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                sells[o[1]] = sells.get(o[1], 0) + int(o[2])
        if t % 24 == 0:
            c = {}
            for row in farm["tiles"]:
                for tl in row:
                    if isinstance(tl, dict):
                        k = tl.get("kind")
                        if k == "PLANT": c["P:" + tl["crop"]] = c.get("P:" + tl["crop"], 0) + 1
                        elif "animal" in tl: c["A:" + tl["animal"]] = c.get("A:" + tl["animal"], 0) + 1
            out[day] = (float(farm["money"]), c)
    return out, sells, float(env.steps[-1][myidx]["reward"])

print("=== MIRROR (2945 vs 2945, my seat 0)")
m, ms, mr = probe([T29, T29], 0)
print("final", mr)
print("=== V26D (v26d vs 2945, my seat 0)")
v, vs, vr = probe([V26D, T29], 0)
print("final", vr)
print()
for d in sorted(m):
    mm, mc = m[d]; vv, vc = v.get(d, (0, {}))
    diffc = {k: mc.get(k, 0) - vc.get(k, 0) for k in set(mc) | set(vc) if mc.get(k, 0) != vc.get(k, 0)}
    print(f"d{d:02d} mirror={mm:7.0f} v26d={vv:7.0f} diff={vv-mm:+8.0f}  censusDiff={diffc}")
print("sells mirror:", {k: v for k, v in sorted(ms.items())})
print("sells v26d  :", {k: v for k, v in sorted(vs.items())})
