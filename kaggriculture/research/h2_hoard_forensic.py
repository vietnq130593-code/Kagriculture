#!/usr/bin/env python3
"""H2 HOARD-vs-FLOW forensic — for crash seeds, per-day:
  - my shed level at end-of-day (env.steps)
  - my SELL fill units + avg price that day (instrumented trace)
Separates HOARD (front-runnable) from FLOW (not front-runnable).
"""
import json
import os
import subprocess
import sys

ROOT = "/home/z/my-project/kaggriculture"
TRACE = "/tmp/h2_hoard_trace.json"

RUNNER = r'''
import json, os
from kaggle_environments import make
seed = int(os.environ["H2_SEED"])
env = make("kaggriculture_h2", debug=False, configuration={"seed": seed})
env.run(["v20.py", "ahmedv46.py"])
# dump per-day shed for both players from env.steps
shed = [{}, {}]
money = [{}, {}]
for t, states in enumerate(env.steps):
    day = t // 24
    for i in (0, 1):
        obs = states[i].observation
        priv = obs.get("private") or {}
        sh = priv.get("shed") or {}
        shed[i][day] = {k: v for k, v in sh.items() if v}
        money[i][day] = (obs.get("farms") or [{}]*2)[i].get("money", 0) if obs.get("farms") else money[i].get(day-1, 0)
out = {"seed": seed, "shed": shed, "rewards": [s.reward for s in env.steps[-1]]}
with open(os.environ["H2_SHED"], "w") as f:
    json.dump(out, f)
print(json.dumps({"rewards": out["rewards"]}))
'''

ITEMS = ["STRAWBERRY", "WOOL", "FERTILIZER", "EGG", "MILK", "WHEAT", "CARROT", "TOMATO", "MELON"]


def run_seed(seed):
    shed_path = f"/tmp/h2_shed_{seed}.json"
    env = dict(os.environ, H2_TRACE=TRACE, H2_SEED=str(seed), H2_SHED=shed_path)
    p = subprocess.run([sys.executable, "-c", RUNNER], capture_output=True,
                       text=True, timeout=400, cwd=ROOT, env=env)
    line = [l for l in (p.stdout or "").splitlines() if l.startswith("{")]
    tr = json.load(open(TRACE))
    sh = json.load(open(shed_path))
    # fills per (player, item, day)
    fills = {}
    for c in tr["commits"]:
        if c["op"] != "SELL":
            continue
        k = (c["p"], c["it"], c["s"] // 24)
        u, rev = fills.get(k, (0, 0))
        fills[k] = (u + 1, rev + c["pr"])
    return sh, fills


def main():
    for seed in [11, 17, 8, 21]:
        sh, fills = run_seed(seed)
        print(f"\n===== seed {seed}: rewards {sh['rewards']}")
        print("day | my shed [S W F E M WK] | my fills (u@$p) | v46 fills")
        for day in range(12, 30):
            my_shed = sh["shed"][0].get(str(day)) or sh["shed"][0].get(day) or {}
            cells = []
            for it in ITEMS:
                v = my_shed.get(it, 0)
                cells.append(f"{v}" if v else ".")
            my_f = []
            for it in ITEMS:
                k = (0, it, day)
                if k in fills:
                    u, rev = fills[k]
                    my_f.append(f"{it[:4]}:{u}@${rev/u:.0f}")
            v46_f = []
            for it in ITEMS:
                k = (1, it, day)
                if k in fills:
                    u, rev = fills[k]
                    v46_f.append(f"{it[:4]}:{u}@${rev/u:.0f}")
            print(f"d{day:02d} | {' '.join(cells):25s} | {' '.join(my_f):60s} | {' '.join(v46_f)}")


if __name__ == "__main__":
    main()
