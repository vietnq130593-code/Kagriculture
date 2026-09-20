#!/usr/bin/env python3
"""T102 probe2: full grid dump of B's farm at chosen days + worker positions."""
import sys
from kaggle_environments import make

SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 101
DAYS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [12, 15, 17, 19, 22, 23]
A = "/home/z/my-project/kaggriculture/v26c.py"
B = "/home/z/my-project/kaggriculture/thomast2945.py"

env = make("kaggriculture", debug=False, configuration={"seed": SEED})
env.run([A, B])

for day in DAYS:
    step = day * 24
    e = env.steps[step][1]
    obs = e["observation"]
    farm = obs["farms"][1]
    grid = farm["tiles"]
    n = len(grid)
    print(f"=== day {day} (board {n}x{len(grid[0])}) money={farm['money']}")
    sym = {None: ".", "WEED": "w"}
    rows = []
    for y in range(n):
        row = []
        for x in range(len(grid[y])):
            t = grid[y][x]
            if t is None: row.append(".")
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "PLANT":
                    row.append({"WHEAT": "W", "CARROT": "C", "TOMATO": "T", "STRAWBERRY": "S", "MELON": "M"}[t["crop"]] + str(t.get("planted_day", "?") % 10))
                elif "animal" in t:
                    row.append({"COW": "c", "SHEEP": "s", "GOOSE": "g"}[t["animal"]])
                elif k == "WEED": row.append("w")
                else: row.append(k[0])
            else: row.append("?")
        rows.append("".join(row))
    pos = [farm["farmer"]] + list(farm["hands"])
    for i, p in enumerate(pos):
        x, y = int(p[0]), int(p[1])
        r = list(rows[y]); r[x] = "@" if i == 0 else str(i)
        rows[y] = "".join(r)
    print("\n".join(rows))
    # also count empties
    empt = sum(1 for row in grid for t in row if t is None)
    print("empty tiles:", empt)
