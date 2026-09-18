#!/usr/bin/env python3
"""H2 ENDGAME PROBE — fill-exact economics of the synchronized REAPER crash.

Uses the instrumented env kaggriculture_h2 (commits + drains logged per unit).
For each seed (v20 vs ahmedv46, seat 0):
  - per (player, item, day): units sold + revenue (true fills)
  - reconstructed market inventory per item per day-end (I0 + sells - buys - drains)
  - avg fill price per item per day
  - endgame revenue split (d27-29) per player
  - FRONT-RUN VALUE: my d27-29 units x (price at day D - endgame avg price),
    D in {20..26} — first-order estimate, feedback ignored
"""
import json
import os
import subprocess
import sys

ROOT = "/home/z/my-project/kaggressurE"  # placeholder, fixed below
ROOT = "/home/z/my-project/kaggriculture"
TRACE = "/tmp/h2_endgame_trace.json"
OUT = os.path.join(ROOT, "research", "h2_endgame_probe.json")

SEEDS = [3, 5, 8, 11, 17, 21]

RUNNER = r'''
import json, os
from kaggle_environments import make
seed = int(os.environ["H2_SEED"])
env = make("kaggriculture_h2", debug=False, configuration={"seed": seed})
env.run(["v20.py", "ahmedv46.py"])
r = [s.reward for s in env.steps[-1]]
print(json.dumps({"rewards": r}))
'''


def run_seed(seed):
    env = dict(os.environ, H2_TRACE=TRACE, H2_SEED=str(seed))
    p = subprocess.run([sys.executable, "-c", RUNNER], capture_output=True,
                       text=True, timeout=400, cwd=ROOT, env=env)
    rewards = None
    for line in (p.stdout or "").splitlines():
        try:
            o = json.loads(line)
            if "rewards" in o:
                rewards = o["rewards"]
        except Exception:
            pass
    d = json.load(open(TRACE))
    d["rewards"] = rewards
    return d


def analyze(d):
    commits = d["commits"]
    drains = d["drains"]
    # per (player,item,day) units/revenue
    per = {}
    for c in commits:
        if c["op"] != "SELL":
            continue
        day = c["s"] // 24
        k = (c["p"], c["it"], day)
        u, rev = per.get(k, (0, 0))
        per[k] = (u + 1, rev + c["pr"])
    # inventory reconstruction (per item, per day-end)
    inv = {it: 10000 for it in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY",
                                "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")}
    inv_by_day = {}   # day -> {item: inv at day end}
    drain_map = {}
    for dr in drains:
        drain_map.setdefault(dr["s"] // 24, 0)
    for dr in drains:
        s = dr["s"]
        for it, n in dr["d"].items():
            inv[it] -= n
        # commits processed before drain within same step? engine: market first,
        # then drain. Apply in step order below instead.
    # redo properly: build event list by step
    evs = []
    for c in commits:
        evs.append((c["s"], "c", c))
    for dr in drains:
        evs.append((dr["s"], "d", dr))
    evs.sort(key=lambda x: (x[0], 0 if x[1] == "c" else 1))
    inv = {it: 10000 for it in inv}
    for s, kind, o in evs:
        if kind == "c":
            if o["op"] == "SELL":
                if o["pr"] > 1:
                    inv[o["it"]] = inv.get(o["it"], 10000) + 1
            elif o["op"] == "BUY_PRODUCT":
                inv[o["it"]] = inv.get(o["it"], 10000) - 1
        else:
            for it, n in o["d"].items():
                inv[it] -= n
        if s % 24 == 23:
            inv_by_day[s // 24] = dict(inv)
    inv_by_day[29] = dict(inv)
    return per, inv_by_day


def main():
    all_out = {"games": []}
    agg = {}
    for seed in SEEDS:
        d = run_seed(seed)
        per, inv_by_day = analyze(d)
        rewards = d["rewards"]
        game = {"seed": seed, "rewards": rewards, "per": {}, "inv_by_day":
                {str(day): iv for day, iv in inv_by_day.items()}}
        print(f"=== seed {seed}: {rewards[0]:.0f} vs {rewards[1]:.0f} "
              f"(gap {rewards[0]-rewards[1]:+.0f})")
        # endgame per player
        for pid, name in ((0, "me"), (1, "v46")):
            eg_rev = {}
            for (p, it, day), (u, rev) in per.items():
                if p != pid or day < 27:
                    continue
                cu, cr = eg_rev.get(it, (0, 0))
                eg_rev[it] = (cu + u, cr + rev)
            print(f"  {name} endgame(d27+) revenue: " + " ".join(
                f"{it}:{u}u/${rev:.0f}" for it, (u, rev) in sorted(eg_rev.items())))
        # avg fill price per item per day (both players)
        pr_day = {}
        for (p, it, day), (u, rev) in per.items():
            a, b = pr_day.get(it, ({}, {}))
            a[day] = a.get(day, 0) + u
            b[day] = b.get(day, 0) + rev
            pr_day[it] = (a, b)
        # front-run value: my d27+ units x (price(D) - price_end)
        for it, (u_day, r_day) in sorted(pr_day.items()):
            eg_u = sum(u for day, u in u_day.items() if day >= 27)
            eg_rev = sum(r for day, r in r_day.items() if day >= 27)
            if eg_u == 0:
                continue
            p_end = eg_rev / eg_u
            best = None
            for D in range(18, 27):
                if u_day.get(D, 0) == 0:
                    # use reconstructed price? use fill price from opponent too
                    pass
                pD = (r_day.get(D, 0) / u_day[D]) if u_day.get(D, 0) else None
                if pD is None:
                    continue
                gain = eg_u * (pD - p_end)
                if best is None or gain > best[1]:
                    best = (D, gain)
            if best and best[1] > 1:
                print(f"    [{it}] endgame {eg_u}u @ ${p_end:.1f} avg; "
                      f"front-run best day d{best[0]} -> +${best[1]:.0f}")
                agg[it] = agg.get(it, 0) + best[1]
                game["per"][it] = {"eg_units": eg_u, "eg_avg_price": p_end,
                                   "best_day": best[0], "gain": best[1]}
        # price path by day (fill avg, any volume)
        for it in ("WHEAT", "CARROT", "STRAWBERRY", "MELON", "WOOL", "MILK", "EGG", "FERTILIZER", "TOMATO"):
            u_day, r_day = pr_day.get(it, ({}, {}))
            path = " ".join(
                f"d{day}:${r_day[day]/u_day[day]:.0f}" for day in sorted(u_day)
                if day >= 18 and u_day[day] > 0)
            if path:
                print(f"    price[{it}] {path}")
        all_out["games"].append(game)
    print("\n=== AGG front-run value (6 seeds): " + " ".join(
        f"{it}:{v:+.0f}" for it, v in sorted(agg.items())))
    print(f"TOTAL: {sum(agg.values()):+.0f} (~{sum(agg.values())/len(SEEDS):+.0f}/game)")
    with open(OUT, "w") as f:
        json.dump(all_out, f, indent=1)
    print("saved", OUT)


if __name__ == "__main__":
    main()
