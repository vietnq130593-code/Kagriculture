#!/usr/bin/env python3
"""v23 design probe — v20 vs ahmedv46, dump v20's daily resource profile.

Answers (empirically, for the v23 goose planner design):
  1. How many hands/day does v20 hire? Ops histogram per day?
  2. How many PASS slots (idle labor) per day?
  3. Wheat flow: produced / sold / shed stock — how much can feed 20 geese?
  4. Shed headroom (capacity 100) — room for eggs + transient geese?
  5. Tile usage in NW — what would geese displace?
  6. EGG market state: price, inventory, drain cadence.
  7. Market order slots used/turn.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from kaggle_environments import make

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 3
A = os.path.join(ROOT, sys.argv[2] if len(sys.argv) > 2 else "v20.py")
B = os.path.join(ROOT, "ahmedv46.py")

env = make("kaggriculture", debug=False, configuration={"seed": SEED})
env.run([A, B])

# Re-walk steps to build the daily profile for seat 0 (v20).
days = {}
for step, states in enumerate(env.steps):
    if step == 0:
        continue
    obs = states[0]["observation"] if isinstance(states[0], dict) else states[0].observation
    day = step // 24
    d = days.setdefault(day, {"ops": {}, "market": [], "hands": 0, "pass": 0, "acts": 0})

    farm = obs["farms"][0]
    private = obs["private"]
    d["hands"] = max(d["hands"], len(farm["hands"]))
    d["money"] = farm["money"]

    # action actually submitted this step: kaggle stores it in the previous
    # state's action field; env.steps[step][0]["action"] is what seat0 played.
    act = states[0].get("action") if isinstance(states[0], dict) else None
    if isinstance(act, dict):
        units = [act.get("farmer", ["PASS"])] + act.get("hands", [])
        for u in units:
            op = u[0] if isinstance(u, list) and u else "?"
            d["ops"][op] = d["ops"].get(op, 0) + 1
            d["acts"] += 1
            if op == "PASS":
                d["pass"] += 1
        mk = act.get("market", [])
        if mk:
            d["market"].extend([list(o) for o in mk])

    if step % 24 == 23:  # end of day snapshot
        d["shed"] = {k: v for k, v in private["shed"].items() if v}
        tiles = {}
        for row in farm["tiles"]:
            for t in row:
                if t is None:
                    tiles["empty"] = tiles.get("empty", 0) + 1
                elif t == "LOCKED":
                    tiles["locked"] = tiles.get("locked", 0) + 1
                elif isinstance(t, dict):
                    k = t.get("kind", "?")
                    if k == "PLANT":
                        k = "PLANT_" + t.get("crop", "?")
                    elif "animal" in t:
                        k = "ANIMAL_" + t["animal"]
                    tiles[k] = tiles.get(k, 0) + 1
        d["tiles"] = tiles
        d["unlocked"] = farm["unlocked_quadrants"]
        mkt = obs["market"]
        d["prices"] = {k: mkt["prices"][k] for k in ("WHEAT", "EGG", "MILK", "WOOL", "TOMATO", "STRAWBERRY")}
        d["inv"] = {k: mkt["inventory"][k] for k in ("WHEAT", "EGG", "MILK", "WOOL")}
        d["shops"] = obs["town"]["unlocked_shops"]

out = {
    "seed": SEED,
    "final_money_v20": float(env.steps[-1][0].reward or 0),
    "final_money_v46": float(env.steps[-1][1].reward or 0),
    "days": days,
}
path = os.path.join(ROOT, "bench", f"v23_probe_seed{SEED}.json")
json.dump(out, open(path, "w"), indent=1)

# Console digest
print(f"seed {SEED}: v20 ${out['final_money_v20']:,.0f} vs v46 ${out['final_money_v46']:,.0f}")
for day in sorted(days):
    d = days[day]
    ops = d.get("ops", {})
    tot = d.get("acts", 0)
    pas = d.get("pass", 0)
    ops = d.get("ops", {})
    tot = d.get("acts", 0)
    pas = d.get("pass", 0)
    wheat_sold = sum(o[2] for o in d.get("market", []) if len(o) >= 3 and o[0] == "SELL" and o[1] == "WHEAT")
    egg_sold = sum(o[2] for o in d.get("market", []) if len(o) >= 3 and o[0] == "SELL" and o[1] == "EGG")
    mkt_orders = [o for o in d.get("market", []) if isinstance(o, list) and len(o) >= 1 and o[0] != "HIRE"]
    print(f"d{day:02d} hands={d.get('hands',0)} acts={tot:3d} pass={pas:3d} wSold={wheat_sold} eSold={egg_sold} "
          f"ops={ {k:v for k,v in sorted(ops.items()) if k not in ('PASS',)} } "
          f"mkt={mkt_orders[:5] }")
    if day % 4 == 0 and "shed" in d:
        print(f"     shed={d['shed']} tiles={d['tiles']} wheatP=${d['prices']['WHEAT']:.0f} eggP=${d['prices']['EGG']:.0f} eggInv={d['inv']['EGG']}")
print(f"saved {path}")
