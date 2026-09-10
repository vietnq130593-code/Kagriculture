#!/usr/bin/env python3
"""Extract per-tile occupancy ranking from an original replay (for CF placement)."""
import json, sys


def occupancy(path, player, out_path):
    d = json.load(open(path))
    steps = d["steps"]
    board = len(steps[1][player]["observation"]["farms"][player]["tiles"])
    occ = [[0] * board for _ in range(board)]
    n_days = 0
    last_day = -1
    for t in range(1, 720):
        obs = steps[t][player]["observation"]
        day = (t - 1) // 24
        if day == last_day:
            continue
        last_day = day
        n_days += 1
        for y in range(board):
            for x in range(board):
                if obs["farms"][player]["tiles"][y][x] is not None:
                    occ[y][x] += 1
    json.dump({"board": board, "n_days": n_days, "occ": occ}, open(out_path, "w"))
    flat = sorted(((occ[y][x], x, y) for y in range(board) for x in range(board)))
    print(f"{path.split('/')[-1]} p{player}: {n_days} days; least-occupied 25 tiles:")
    print("  " + " ".join(f"({x},{y}):{o}" for o, x, y in flat[:25]))


if __name__ == "__main__":
    occupancy("/home/z/my-project/upload/107559251.json", 0, "/home/z/my-project/tool-results/cf_occ_M1_p0.json")
    occupancy("/home/z/my-project/upload/107573831.json", 0, "/home/z/my-project/tool-results/cf_occ_M2_p0.json")
