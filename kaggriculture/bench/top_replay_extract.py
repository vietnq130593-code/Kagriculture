#!/usr/bin/env python3
"""Extract per-day stats from top-rank Kaggle replay JSONs (upload/107559251.json, 107573831.json).

Outputs:
  - bench/top_replay_analysis.json  (compact distilled stats, git-tracked)
  - stdout summary for reading

Per replay, per day (hour 23 = end of day, before EOD refresh):
  money, #quadrants, tile census (crops/animals/empty/locked/weed), empty% of unlocked
  market prices, shops unlocked, hires (from actions at h0-h23)
Aggregates: land buy timing (first quadrant appearance), sell orders by product,
  buy orders (animals/seeds/land), final tile composition, final money.
"""
import json, sys, gc
from collections import defaultdict

FILES = [
    ("/home/z/my-project/upload/107559251.json", "R1_107559251"),
    ("/home/z/my-project/upload/107573831.json", "R2_107573831"),
]

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("GOOSE", "COW", "SHEEP")


def tile_census(farm):
    """Count tiles by category for one farm dict."""
    c = defaultdict(int)
    unlocked = 0
    for row in farm["tiles"]:
        for t in row:
            if t == "LOCKED":
                c["locked"] += 1
                continue
            unlocked += 1
            if t is None:
                c["empty"] += 1
            elif t.get("kind") == "WEED":
                c["weed"] += 1
            elif t.get("kind") == "PLANT":
                c["plant_" + t["crop"]] += 1
            elif t.get("kind") in ("COOP", "PASTURE"):
                a = t.get("animal")
                if a:
                    c["animal_" + a] += 1
                else:
                    c["struct_empty_" + t["kind"].lower()] += 1
    c["unlocked"] = unlocked
    return c


def analyze(path, tag):
    with open(path) as f:
        d = json.load(f)
    steps = d["steps"]
    info = d["info"]
    out = {
        "episode_id": info.get("EpisodeId"),
        "teams": info.get("TeamNames"),
        "seed": info.get("seed"),
        "rewards": d["rewards"],
        "n_steps": len(steps),
        "daily": [],           # per-day snapshots
        "sells": [defaultdict(int), defaultdict(int)],     # units sold by product
        "buys_animal": [defaultdict(int), defaultdict(int)],
        "buys_seed": [defaultdict(int), defaultdict(int)],
        "buys_product": [defaultdict(int), defaultdict(int)],
        "hires": [0, 0],
        "land_buy_turn": {},  # quadrant -> (turn, day, player)
        "final_tiles": {},
    }

    # --- daily snapshots at each day boundary (step = day*24 + 23 approx; use last step of day) ---
    n_days = len(steps) // 24
    quad_seen = set()
    for day in range(n_days):
        hi = min(day * 24 + 23, len(steps) - 1)
        # find the last step of the day with hour==23 to be safe
        step_idx = None
        for si in range(hi, day * 24 - 1, -1):
            obs = steps[si][0]["observation"]
            if obs.get("hour") == 23 or si == len(steps) - 1:
                step_idx = si
                break
        if step_idx is None:
            step_idx = hi
        obs = steps[step_idx][0]["observation"]
        rec = {"day": day, "t": step_idx, "players": []}
        for p in (0, 1):
            farm = obs["farms"][p]
            c = tile_census(farm)
            empty_pct = 100.0 * c["empty"] / max(1, c["unlocked"])
            # structures occupy land too; also compute "productive %" = non-empty non-weed / unlocked
            prod = c["unlocked"] - c["empty"] - c["weed"]
            rec["players"].append({
                "money": round(farm["money"]),
                "nq": len(farm["unlocked_quadrants"]),
                "n_hands": len(farm["hands"]),
                "empty": c["empty"],
                "unlocked": c["unlocked"],
                "empty_pct": round(empty_pct, 1),
                "prod_tiles": prod,
                "crops": {k[6:]: v for k, v in c.items() if k.startswith("plant_")},
                "animals": {k[7:]: v for k, v in c.items() if k.startswith("animal_")},
                "struct_empty": sum(v for k, v in c.items() if k.startswith("struct_")),
                "weed": c["weed"],
            })
            # land purchase timing (first time quadrant appears)
            for q in farm["unlocked_quadrants"]:
                key = (p, q)
                if key not in quad_seen:
                    quad_seen.add(key)
                    out["land_buy_turn"][f"p{p}_{q}"] = {"turn": step_idx, "day": day}
        rec["prices"] = dict(obs["market"]["prices"])
        rec["inv"] = {k: v for k, v in obs["market"]["inventory"].items() if abs(v - 10000) > 50}
        rec["shops"] = obs["town"]["unlocked_shops"]
        out["daily"].append(rec)

    # --- aggregate actions ---
    for t, step in enumerate(steps):
        for p in (0, 1):
            act = step[p]["action"] or {}
            for mo in act.get("market", []) or []:
                if not mo:
                    continue
                op = mo[0]
                if op == "SELL" and len(mo) >= 3:
                    out["sells"][p][mo[1]] += int(mo[2])
                elif op == "BUY_ANIMAL" and len(mo) >= 3:
                    out["buys_animal"][p][mo[1]] += int(mo[2])
                elif op == "BUY_SEED" and len(mo) >= 3:
                    out["buys_seed"][p][mo[1]] += int(mo[2])
                elif op == "BUY_PRODUCT" and len(mo) >= 3:
                    out["buys_product"][p][mo[1]] += int(mo[2])
                elif op == "HIRE":
                    out["hires"][p] += 1

    # final tiles
    last = steps[-1][0]["observation"]
    for p in (0, 1):
        c = tile_census(last["farms"][p])
        out["final_tiles"][f"p{p}"] = {
            "money": round(last["farms"][p]["money"]),
            "crops": {k[6:]: v for k, v in c.items() if k.startswith("plant_")},
            "animals": {k[7:]: v for k, v in c.items() if k.startswith("animal_")},
            "empty": c["empty"], "unlocked": c["unlocked"],
            "struct_empty": sum(v for k, v in c.items() if k.startswith("struct_")),
            "weed": c["weed"],
        }
    # convert defaultdicts
    out["sells"] = [dict(x) for x in out["sells"]]
    out["buys_animal"] = [dict(x) for x in out["buys_animal"]]
    out["buys_seed"] = [dict(x) for x in out["buys_seed"]]
    out["buys_product"] = [dict(x) for x in out["buys_product"]]
    del d, steps
    gc.collect()
    return out


def main():
    results = {}
    for path, tag in FILES:
        print(f"=== analyzing {tag}: {path}", flush=True)
        results[tag] = analyze(path, tag)

    with open("/home/z/my-project/kaggriculture/bench/top_replay_analysis.json", "w") as f:
        json.dump(results, f, indent=1)
    print("saved -> kaggriculture/bench/top_replay_analysis.json")

    # --- printable summary ---
    for tag, r in results.items():
        print("\n" + "=" * 78)
        print(f"{tag}: episode {r['episode_id']}  teams={r['teams']}  seed={r['seed']}")
        print(f"rewards: p0={r['rewards'][0]:,.0f}  p1={r['rewards'][1]:,.0f}")
        print(f"land buys: " + ", ".join(f"{k}@d{v['day']}" for k, v in sorted(r["land_buy_turn"].items(), key=lambda kv: kv[1]['turn'])))
        print(f"hires: p0={r['hires'][0]} p1={r['hires'][1]}")
        for p in (0, 1):
            print(f" p{p} sells: {r['sells'][p]}")
            print(f" p{p} buys_animal: {r['buys_animal'][p]}  buys_seed: {r['buys_seed'][p]}  buys_product: {r['buys_product'][p]}")
        # empty% trajectory
        print(" day | p0: money nq empty% crops | p1: money nq empty% crops")
        for rec in r["daily"]:
            if rec["day"] % 3 and rec["day"] != 29:
                continue
            for i in (0, 1):
                pass
            p0, p1 = rec["players"]
            print(f" d{rec['day']:02d} | p0 ${p0['money']:>7,} nq{p0['nq']} emp{p0['empty_pct']:>5.1f}% {p0['crops']} anim{p['animals'] if False else ''}"
                  f" | p1 ${p1['money']:>7,} nq{p1['nq']} emp{p1['empty_pct']:>5.1f}% {p1['crops']}")
        print(" final:", json.dumps(r["final_tiles"]))


if __name__ == "__main__":
    main()
