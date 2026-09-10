#!/usr/bin/env python3
"""Autopsy kain41 vs kain40 on seed 142 (k41 -$17k): daily money, crops, labor."""
import sys
sys.path.insert(0, '/home/z/my-project/kaggriculture')
from kaggle_environments import make


def daily_trace(agent_file, seed):
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run([agent_file, "v6.py"])
    rows = []
    for t, stepstates in enumerate(env.steps):
        if t == 0:
            continue
        obs = stepstates[0].observation
        day, hour = (t - 1) // 24, (t - 1) % 24
        if hour != 23:
            continue
        f = obs.farms[0]
        crops = {}
        animals = {}
        for row in f["tiles"]:
            for tl in row:
                if isinstance(tl, dict):
                    if tl.get("kind") == "PLANT":
                        crops[tl.get("crop")] = crops.get(tl.get("crop"), 0) + 1
                    if "animal" in tl:
                        animals[tl["animal"]] = animals.get(tl["animal"], 0) + 1
        rows.append({
            "day": day, "money": f["money"], "crops": crops, "animals": animals,
            "shed": dict(obs.private["shed"]) if hasattr(obs, "private") else {},
        })
    return rows, env.steps[-1][0].reward


if __name__ == "__main__":
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 142
    r40, f40 = daily_trace("kain40.py", seed)
    r41, f41 = daily_trace("kain41.py", seed)
    print(f"seed {seed}: kain40 final {f40:,.0f} | kain41 final {f41:,.0f}")
    print("day | k40 money/crops | k41 money/crops | gap")
    d41 = {r["day"]: r for r in r41}
    for r in r40:
        d = r["day"]
        o = d41.get(d)
        if not o or d % 2:
            continue
        gap = o["money"] - r["money"]
        print(f"d{d:2}: k40 ${r['money']:>8,.0f} {r['crops']} | "
              f"k41 ${o['money']:>8,.0f} {o['crops']} | gap {gap:>+8,.0f}")
