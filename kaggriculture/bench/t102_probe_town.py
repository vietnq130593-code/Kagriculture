#!/usr/bin/env python3
"""T102 probe3: tomato book state (price + shops) across seeds 100-104."""
import json
from kaggle_environments import make

A = "/home/z/my-project/kaggriculture/v26c.py"
B = "/home/z/my-project/kaggriculture/thomast2945.py"

for seed in (100, 101, 102, 103, 104):
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run([A, B])
    rows = []
    for day in (10, 14, 18, 22, 26, 29):
        step = min(day * 24, 719)
        obs = env.steps[step][1]["observation"]
        town = obs["town"]["unlocked_shops"]
        tom_shops = sum(1 for s in town if s in ("PIZZA_SHOP", "FARMERS_MARKET"))
        prices = obs["market"]["prices"]
        rows.append((day, tom_shops, prices["TOMATO"], prices["WHEAT"], len(town)))
    print("seed", seed, "| (day, tomShops, $TOM, $WHEAT, nShops):", rows)
