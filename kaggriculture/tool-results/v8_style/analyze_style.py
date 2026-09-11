#!/usr/bin/env python3
"""V8 vs TOP-3 STYLE COMPARISON (Task 43).

Unified extractor for both replay formats + per-day/per-hour metrics:
  - animal allocation: buy timeline, placement positions (quadrant, distance
    from shed), herd size, service intensity, product sales
  - labor: actions/day, MOVE fraction, walking distance per unit/day,
    distance-from-shed of service work locations
  - empty land: hourly series, per-day averages, worst window + duration

Sources:
  Kaggle replay: /home/z/my-project/upload/{107559251,107573831}.json
  Arena JSONL:   /home/z/my-project/tool-results/v8_style/v8_seat{A,B}_s*.jsonl

Convention (god-replay verified, Task 39):
  Kaggle row t  = state AFTER action t  (service loc at t = unit pos row t-1)
  Arena turn s  = state BEFORE action s (service loc at s = unit pos turn s;
                  post-action-s state = turn s+1 farms)
"""
import json, gzip, glob, math, sys
from collections import defaultdict

BOARD = 10
HALF = BOARD // 2
SPAWN = (4, 4)  # farmer default spawn (first shed-access NW tile)
CENTERS = {"NW": (2, 2), "NE": (7, 2), "SW": (2, 7), "SE": (7, 7)}


def quadrant_of(x, y):
    return ("N" if y < HALF else "S") + ("W" if x < HALF else "E")


def man(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ---------------------------------------------------------------- parsing --
def load_kaggle(path):
    """-> list of steps: {t, day, hour, farms:[...], acts:[a0,a1]}
    farms[t] = post-action-t state."""
    d = json.load(open(path))
    steps = []
    for t, row in enumerate(d["steps"]):
        obs = row[0]["observation"]
        steps.append({
            "t": t, "day": obs["day"], "hour": obs["hour"],
            "farms": obs["farms"],
            "acts": [row[i].get("action") for i in range(2)],
        })
    return steps, d["info"].get("TeamNames") if isinstance(d.get("info"), dict) else None


def load_arena(path):
    """-> same shape; farms at index t+1 = post-action-t state."""
    opener = gzip.open if path.endswith(".gz") else open
    raw = []
    names = None
    with opener(path, "rt") as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") == "hello":
                names = [d.get("a"), d.get("b")]
            elif d.get("t") == "turn":
                raw.append({"t": "turn", **d})
            elif d.get("t") == "end":
                raw.append({"t": "end", **d})
    steps = []
    n = len(raw)
    for i, d in enumerate(raw):
        if d.get("t") != "turn":
            continue
        # turn i = pre-action state of step i, plus acts at step i.
        # post-action-i state = turn i+1 farms (if exists)
        nxt = raw[i + 1] if i + 1 < n else None
        farms = nxt["farms"] if nxt and nxt.get("t") == "turn" else d["farms"]
        steps.append({
            "t": d["step"], "day": d["day"], "hour": d["hour"],
            "farms": farms, "acts": d.get("acts"),
        })
    return steps, names


# ------------------------------------------------------------- extraction --
def farm_scan(farm):
    """Scan one farm -> dict of tile aggregates + positions."""
    out = {
        "locked": 0, "empty": 0, "weeds": 0,
        "plants": defaultdict(int), "animals": defaultdict(int),
        "animal_tiles": [], "plant_tiles": [], "empty_tiles": [],
        "unlocked": len(farm.get("unlocked_quadrants") or ["NW"]),
    }
    tiles = farm["tiles"]
    for y in range(BOARD):
        for x in range(BOARD):
            t = tiles[y][x]
            if t == "LOCKED":
                out["locked"] += 1
            elif t is None:
                out["empty"] += 1
                out["empty_tiles"].append((x, y))
            elif t.get("kind") == "WEED":
                out["weeds"] += 1
            elif t.get("kind") == "PLANT":
                out["plants"][t.get("crop")] += 1
                out["plant_tiles"].append((x, y, t.get("crop")))
            elif t.get("kind") in ("COOP", "PASTURE"):
                out["animals"][t.get("animal")] += 1
                out["animal_tiles"].append((x, y, t.get("kind"), t.get("animal")))
    return out


def unit_positions(farm):
    ps = [tuple(farm["farmer"])] + [tuple(h) for h in (farm.get("hands") or [])]
    return ps


UNIT_DIRS = ("NORTH", "SOUTH", "EAST", "WEST")
SERVICE_OPS = {"FEED", "CARE", "COLLECT_FERTILIZER"}
FIELD_OPS = {"WATER", "HARVEST", "PLANT", "FERTILIZE", "REMOVE_WEED"}


def analyze(steps, pidx, name):
    """One player trace -> dict of everything."""
    R = {
        "name": name, "seat": pidx,
        "money_final": steps[-1]["farms"][pidx].get("money"),
        "daily": {}, "events": [],
        "ops_season": defaultdict(int),
        "walk_dist_day": defaultdict(float),
        "service_loc_dist": defaultdict(list),   # op -> [dist from SPAWN]
        "field_loc_dist": defaultdict(list),
        "empty_hourly": [],                      # (day, hour, empty, weeds, unlocked)
    }
    prev_pos = None
    for s in steps:
        day, hour, act = s["day"], s["hour"], (s["acts"] or [None, None])[pidx]
        farm = s["farms"][pidx]
        pre_farm = farm  # arena: farms at this row = post-action; we need POS
        # positions BEFORE action: kaggle row t-1 has them; we approximate with
        # the dedicated second pass below. Here: use this row's positions for
        # arena service-loc (turn s pre-action) handled at load time.
        pos = unit_positions(farm)

        # walk distance (between consecutive post-action states)
        if prev_pos is not None and len(pos) == len(prev_pos):
            wd = sum(man(a, b) for a, b in zip(pos, prev_pos))
            R["walk_dist_day"][day] += wd
        prev_pos = pos

        # ops + service locations: service executed at PRE-action position.
        # For arena steps (already loaded as post-action at row t), the
        # pre-action pos was at row t-1 -- handled in pass 2.
        if act:
            for u in ([act.get("farmer")] + list(act.get("hands") or [])):
                if not u:
                    continue
                op = u[0]
                R["ops_season"][op if op not in UNIT_DIRS else "MOVE"] += 1
            for grp in (act.get("market") or []):
                if grp and grp[0] in ("BUY_ANIMAL", "BUILD_COOP", "BUILD_PASTURE",
                                      "BUY_LAND", "HIRE", "SELL"):
                    R["events"].append({"day": day, "hour": hour, "op": grp})

        scan = farm_scan(farm)
        # end-of-day snapshot (post-action state at hour 23)
        if hour == 23 or s["t"] >= len(steps) - 1:
            R["daily"][day] = {
                "empty": scan["empty"], "weeds": scan["weeds"],
                "locked": scan["locked"], "unlocked": scan["unlocked"],
                "plants": dict(scan["plants"]), "animals": dict(scan["animals"]),
                "animal_tiles": scan["animal_tiles"],
                "plant_tiles_n": len(scan["plant_tiles"]),
                "hands": len(farm.get("hands") or []),
                "money": farm.get("money"),
                "walk": R["walk_dist_day"][day],
            }
        R["empty_hourly"].append((day, hour, scan["empty"], scan["weeds"], scan["unlocked"]))

    # pass 2: service locations using PRE-action positions.
    for i, s in enumerate(steps):
        act = (s["acts"] or [None, None])[pidx]
        if not act:
            continue
        pre = steps[i - 1]["farms"][pidx] if i > 0 else None
        if pre is None:
            continue
        # count of units might change mid-day; use farmer+hands zip
        units_then = unit_positions(pre)
        allu = ([act.get("farmer")] + list(act.get("hands") or []))
        for j, u in enumerate(allu):
            if not u or u[0] not in SERVICE_OPS | FIELD_OPS:
                continue
            if j < len(units_then):
                dist = man(units_then[j], SPAWN)
                if u[0] in SERVICE_OPS:
                    R["service_loc_dist"][u[0]].append(dist)
                else:
                    R["field_loc_dist"][u[0]].append(dist)
    return R


def load_any(path):
    if path.endswith(".jsonl.gz") or path.endswith(".jsonl"):
        return load_arena(path)
    return load_kaggle(path)


# -------------------------------------------------------------- reporting --
def agg_animals(R):
    """buy timeline + placement stats."""
    buys = defaultdict(lambda: defaultdict(int))
    builds = defaultdict(int)
    land = []
    sells = defaultdict(float)
    for e in R["events"]:
        if e["op"][0] == "BUY_ANIMAL":
            buys[e["day"]][e["op"][1]] += e["op"][2] if len(e["op"]) > 2 else 1
        elif e["op"][0] in ("BUILD_COOP", "BUILD_PASTURE"):
            builds[e["op"][0]] += 1
        elif e["op"][0] == "BUY_LAND":
            land.append(e["day"])
        elif e["op"][0] == "SELL" and e["op"][1] in ("MILK", "WOOL", "EGG"):
            sells[e["op"][1]] += e["op"][2] if len(e["op"]) > 2 else 1
    return buys, builds, land, sells


def placement_stats(R):
    """per-day animal tile geometry."""
    out = {}
    for day, snap in R["daily"].items():
        at = snap["animal_tiles"]
        if not at:
            out[day] = None
            continue
        dists = [man((x, y), SPAWN) for (x, y, k, a) in at]
        quads = defaultdict(int)
        for (x, y, k, a) in at:
            quads[quadrant_of(x, y)] += 1
        # spread: max pairwise manhattan within herd (approx via bbox diag)
        xs = [t[0] for t in at]; ys = [t[1] for t in at]
        out[day] = {
            "n": len(at),
            "d_shed_avg": sum(dists) / len(dists),
            "d_shed_max": max(dists),
            "bbox": (max(xs) - min(xs)) + (max(ys) - min(ys)),
            "quads": dict(quads),
            "by_type": defaultdict(int),
        }
        for (x, y, k, a) in at:
            out[day]["by_type"][a] += 1
        out[day]["by_type"] = dict(out[day]["by_type"])
    return out


def empty_report(R):
    """daily empty + worst window."""
    days = sorted(R["daily"])
    e9_27 = [R["daily"][d]["empty"] for d in days if 9 <= d <= 27]
    w9_27 = [R["daily"][d]["weeds"] for d in days if 9 <= d <= 27]
    # hourly max empty per day + longest streak of empty >= 10
    per_day_max = defaultdict(int)
    for (d, h, e, w, u) in R["empty_hourly"]:
        per_day_max[d] = max(per_day_max[d], e)
    # worst consecutive window (avg empty), any length >= 3
    series = [(d, R["daily"][d]["empty"]) for d in days]
    best = None
    for i in range(len(series)):
        for j in range(i + 3, len(series) + 1):
            seg = series[i:j]
            avg = sum(v for _, v in seg) / len(seg)
            if best is None or avg > best[3]:
                best = (series[i][0], series[j - 1][0], j - i, avg)
    return {
        "empty_avg_d9_27": sum(e9_27) / len(e9_27) if e9_27 else 0,
        "weeds_avg_d9_27": sum(w9_27) / len(w9_27) if w9_27 else 0,
        "worst_window": best,
        "max_empty_day": max(per_day_max.items(), key=lambda kv: kv[1]) if per_day_max else None,
        "per_day": {d: R["daily"][d]["empty"] for d in days},
        "per_day_max": dict(per_day_max),
    }


def labor_report(R):
    ops = R["ops_season"]
    total = sum(ops.values())
    walk = sum(R["walk_dist_day"].values())
    ndays = len(R["daily"])
    svc = {op: (sum(v) / len(v), len(v)) for op, v in R["service_loc_dist"].items()}
    fld = {op: (sum(v) / len(v), len(v)) for op, v in R["field_loc_dist"].items()}
    return {
        "ops": dict(ops), "total": total,
        "per_day": total / max(1, ndays),
        "move_frac": ops.get("MOVE", 0) / max(1, total),
        "walk_total": walk, "walk_per_day": walk / max(1, ndays),
        "svc_loc": svc, "field_loc": fld,
    }


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", help="write aggregated JSON here")
    args = ap.parse_args()

    sources = []
    for p in ("/home/z/my-project/upload/107559251.json",
              "/home/z/my-project/upload/107573831.json"):
        sources.append((p, None))
    for p in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/*.jsonl")):
        sources.append((p, None))

    out = {}
    for path, _ in sources:
        steps, names = load_any(path)
        if names is None:
            names = ["P0", "P1"]
        tag = path.split("/")[-1].replace(".json", "").replace(".jsonl", "")
        for pidx in (0, 1):
            pname = names[pidx]
            R = analyze(steps, pidx, pname)
            buys, builds, land, sells = agg_animals(R)
            out[f"{tag}#{pidx}:{pname}"] = {
                "final_money": R["money_final"],
                "buys": {str(d): dict(v) for d, v in buys.items()},
                "builds": dict(builds), "land_days": land,
                "animal_sells": dict(sells),
                "placement": {str(d): v for d, v in placement_stats(R).items()},
                "empty": empty_report(R),
                "labor": labor_report(R),
                "daily_animals": {str(d): R["daily"][d]["animals"] for d in sorted(R["daily"])},
                "daily_plants": {str(d): R["daily"][d]["plants"] for d in sorted(R["daily"])},
                "daily_hands": {str(d): R["daily"][d]["hands"] for d in sorted(R["daily"])},
                "daily_walk": {str(d): R["daily"][d]["walk"] for d in sorted(R["daily"])},
            }
        print(f"parsed {tag}: {names}")

    if args.dump:
        json.dump(out, open(args.dump, "w"), default=str)
        print(f"wrote {args.dump} ({len(out)} player-traces)")
