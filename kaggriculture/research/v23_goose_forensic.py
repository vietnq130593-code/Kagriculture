#!/usr/bin/env python3
"""v23 goose-lifecycle forensic — trace every goose-related event per turn."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from kaggle_environments import make

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 3

env = make("kaggriculture", debug=False, configuration={"seed": SEED})
env.run([os.path.join(ROOT, "v23.py"), os.path.join(ROOT, "ahmedv46.py")])

print(f"final: v23 {float(env.steps[-1][0].reward or 0):,.0f} "
      f"vs v46 {float(env.steps[-1][1].reward or 0):,.0f}")

prev = {"money": None, "shed_goose": 0, "geese_tiles": set(), "coops": 0}
for step, states in enumerate(env.steps):
    if step == 0:
        continue
    st = states[0]
    obs = st["observation"] if isinstance(st, dict) else st.observation
    act = st.get("action") if isinstance(st, dict) else None
    farm = obs["farms"][0]
    private = obs["private"]
    money = round(farm["money"])
    shed = private["shed"]
    shed_goose = shed.get("GOOSE", 0)
    shed_wheat = shed.get("WHEAT", 0)
    shed_eggs = shed.get("EGG", 0)
    geese_tiles = set()
    coops = 0
    for y in range(10):
        for x in range(10):
            t = farm["tiles"][y][x]
            if isinstance(t, dict):
                if t.get("animal") == "GOOSE":
                    geese_tiles.add((x, y, t.get("consecutive_unfed", 0),
                                     t.get("fed_today"), t.get("yield_units", 0)))
                elif t.get("kind") == "COOP" and "animal" not in t:
                    coops += 1
    events = []
    if money != prev["money"]:
        events.append(f"money {prev['money']}->{money}")
    if shed_goose != prev["shed_goose"]:
        events.append(f"shedGOOSE {prev['shed_goose']}->{shed_goose}")
    if geese_tiles != prev["geese_tiles"]:
        old = prev["geese_tiles"]
        new = geese_tiles
        gone = old - new
        came = new - old
        if gone:
            events.append(f"GEESE GONE: {sorted(gone)}")
        if came:
            events.append(f"GEESE NEW: {sorted(came)}")
    if coops != prev["coops"]:
        events.append(f"coops {prev['coops']}->{coops}")
    # my market orders this turn (goose/wheat/land/egg/egg related)
    if isinstance(act, dict):
        mk = act.get("market") or []
        interesting = [o for o in mk if isinstance(o, list) and o and
                       o[0] in ("BUY_ANIMAL", "BUY_LAND", "HIRE", "BUY_PRODUCT")
                       or (o and o[0] == "SELL" and o[1] == "EGG")]
        if interesting:
            events.append(f"mkt {interesting}")
    if events and step < 720:
        day, hour = step // 24, step % 24
        print(f"d{day:02d}h{hour:02d} w{shed_wheat} e{shed_eggs} "
              f"m{money} | " + " ; ".join(events))
    prev = {"money": money, "shed_goose": shed_goose,
            "geese_tiles": geese_tiles, "coops": coops}
