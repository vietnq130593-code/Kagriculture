#!/usr/bin/env python3
"""Extract per-day per-player metrics from Kaggle episode replay JSONs."""
import json
import sys
from collections import Counter, defaultdict

CROPS = {"WHEAT", "CARROT", "MELON", "TOMATO", "STRAWBERRY"}
ANIMALS = {"GOOSE", "COW", "SHEEP"}


def tile_stats(tiles):
    """Count tile kinds from a 10x10 tile grid."""
    c = Counter()
    crops = Counter()
    animals = Counter()
    weeds = 0
    for row in tiles:
        for t in row:
            if t is None:
                c["EMPTY"] += 1
            elif isinstance(t, str):
                c[t] += 1  # LOCKED
            else:
                kind = t.get("kind", "?")
                c[kind] += 1
                if "animal" in t:
                    animals[t.get("animal", "?")] += 1
                if kind == "PLANT":
                    crops[t.get("crop", "?")] += 1
                if t.get("weed"):
                    weeds += 1
    return c, crops, animals, weeds


def analyze(fn):
    with open(fn) as f:
        data = json.load(f)

    names = data["info"]["TeamNames"]
    rewards = data["rewards"]
    steps = data["steps"]
    n_steps = len(steps)

    result = {
        "file": fn,
        "names": names,
        "rewards": rewards,
        "days": {},  # day -> {p0: {...}, p1: {...}}
        "market_events": {0: [], 1: []},  # all market orders with step
        "prices": [],  # (step, day, hour, prices dict)
        "shops": [],  # (step, day, shops list)
    }

    for day in range(30):
        result["days"][day] = {}

    # walk steps; step t observation = state at time t (before action)
    for t in range(n_steps):
        obs = steps[t][0]["observation"]
        day = obs["day"]
        hour = obs["hour"]

        # record prices each step (from p0 obs)
        result["prices"].append({
            "step": t, "day": day, "hour": hour,
            "prices": dict(obs["market"]["prices"]),
            "inv": dict(obs["market"]["inventory"]),
        })
        shops = obs["town"]["unlocked_shops"]
        result["shops"].append({"step": t, "day": day, "shops": list(shops)})

        # record actions for both players
        for p in (0, 1):
            act = steps[t][p].get("action")
            if not act:
                continue
            for mo in act.get("market", []):
                if isinstance(mo, list) and len(mo) >= 2:
                    rec = {"step": t, "day": day, "hour": hour,
                           "cmd": mo[0]}
                    if len(mo) >= 3:
                        rec["item"] = mo[1] if isinstance(mo[1], str) else None
                        rec["qty"] = mo[2] if isinstance(mo[2], (int, float)) else None
                    result["market_events"][p].append(rec)

        # day snapshot at hour 23 (last hour of day) or last step of day
        # store state at every hour boundary h0 (day start) and h23 (day end)
        if hour in (0, 23):
            for p in (0, 1):
                farm = obs["farms"][p]
                c, crops, animals, weeds = tile_stats(farm["tiles"])
                unlocked = farm["unlocked_quadrants"]
                n_unlocked = len(unlocked) * 25
                empty_unowned = c.get("EMPTY", 0)  # empty among unlocked
                priv = steps[t][p]["observation"].get("private", {}) if p == 0 else None
                rec = {
                    "hour": hour,
                    "money": farm["money"],
                    "quadrants": list(unlocked),
                    "n_unlocked": n_unlocked,
                    "empty_unlocked": empty_unowned,
                    "tiles": dict(c),
                    "crops": dict(crops),
                    "animals": dict(animals),
                    "hands": len(farm["hands"]),
                    "hires_today": farm.get("hires_today", 0),
                    "farmer_pos": farm["farmer"],
                }
                if p == 0:
                    rec["seeds"] = dict(priv.get("seeds", {})) if priv else {}
                    rec["shed"] = dict(priv.get("shed", {})) if priv else {}
                result["days"][day].setdefault(p, {})[hour] = rec

    return result


def main():
    out = {}
    for fn in sys.argv[1:]:
        print(f"Analyzing {fn}...", file=sys.stderr)
        r = analyze(fn)
        # compress: keep only needed fields in market events
        out[fn] = r

    with open("/home/z/my-project/tool-results/replay_extract.json", "w") as f:
        json.dump(out, f)
    print("Saved to replay_extract.json", file=sys.stderr)


if __name__ == "__main__":
    main()
