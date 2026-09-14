#!/usr/bin/env python3
"""T80b — realized prices, op cadence, and land-use timeline for ahmedv41.

Computes from JSONL replays:
  - market price + inventory timeline per item (sampled daily)
  - realized avg sell price per item (units executed x turn price, approx)
  - FEED / PICKUP / PLANT / WATER / DIG / BUILD op counts by day
  - hire hours histogram (HIRE market orders)
  - shed occupancy timeline
  - animal placement timeline
  - money by day (idle windows)
"""
import json
import sys
from collections import defaultdict

CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]


def load(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d.get("t") == "turn":
            recs.append(d)
    return recs


def audit(path, seat, tag):
    recs = load(path)
    print(f"\n{'='*76}\n{path} seat {seat} = {tag}\n{'='*76}")

    price_tl = defaultdict(dict)     # item -> day -> price
    inv_tl = defaultdict(dict)       # item -> day -> inventory
    rev = defaultdict(float)
    sold_units = defaultdict(int)
    feed_ops = defaultdict(int)     # day -> count
    pickup_ops = defaultdict(int)
    plant_ops = defaultdict(lambda: defaultdict(int))  # day -> crop -> n
    water_ops = defaultdict(int)
    dig_ops = defaultdict(int)
    build_ops = defaultdict(int)
    hire_hours = defaultdict(int)
    shed_occ = []
    prev_shed = {}
    money_day = {}
    animal_first = {}
    dead_tiles_day = defaultdict(int)   # day -> count of WEED tiles
    empty_tiles_day = defaultdict(int)  # day -> count of None tiles

    for r in recs:
        step = r["step"]
        day = step // 24
        hour = step % 24
        farm = r["farms"][seat]
        priv = r["priv"][seat]
        act = r["acts"][seat]
        market = r["market"]

        if hour == 12:  # daily sample mid-day
            for item in market["prices"]:
                price_tl[item][day] = market["prices"][item]
                inv_tl[item][day] = market["inventory"][item]

        money_day[day] = farm["money"]

        # ops
        for a in [act.get("farmer")] + (act.get("hands") or []) if isinstance(act, dict) else []:
            if not isinstance(a, list) or not a:
                continue
            op = a[0]
            if op == "FEED":
                feed_ops[day] += 1
            elif op == "PICKUP":
                pickup_ops[day] += 1
            elif op == "PLANT":
                plant_ops[day][a[1] if len(a) > 1 else "?"] += 1
            elif op == "WATER":
                water_ops[day] += 1
            elif op == "DIG":
                dig_ops[day] += 1
            elif op in ("BUILD_COOP", "BUILD_PASTURE"):
                build_ops[day] += 1

        for o in (act.get("market") or []) if isinstance(act, dict) else []:
            if isinstance(o, list) and o and o[0] == "HIRE":
                hire_hours[hour] += 1

        # realized sells: shed decrease minus pickups
        # count pickups per item this turn
        picked = defaultdict(int)
        for a in [act.get("farmer")] + (act.get("hands") or []) if isinstance(act, dict) else []:
            if isinstance(a, list) and a and a[0] == "PICKUP" and len(a) >= 2:
                picked[a[1]] += a[2] if len(a) > 2 else 1
        placed = defaultdict(int)
        for a in [act.get("farmer")] + (act.get("hands") or []) if isinstance(act, dict) else []:
            if isinstance(a, list) and a and a[0] == "PLACE" and len(a) >= 2:
                placed[a[1]] += 1
        for item, v in priv["shed"].items():
            dec = prev_shed.get(item, 0) - v - picked.get(item, 0) - placed.get(item, 0)
            if dec > 0 and item in market["prices"]:
                sold_units[item] += dec
                rev[item] += dec * market["prices"][item]
        prev_shed = dict(priv["shed"])
        shed_occ.append((step, sum(priv["shed"].values())))

        # animal first appearance
        if hour == 23:
            for row in farm["tiles"]:
                for t in row:
                    if isinstance(t, dict) and t.get("animal"):
                        animal_first.setdefault(t["animal"], []).append(day)
            nw = sum(1 for row in farm["tiles"] for t in row
                     if isinstance(t, dict) and t.get("kind") == "WEED")
            ne = sum(1 for row in farm["tiles"] for t in row if t is None)
            dead_tiles_day[day] = nw
            empty_tiles_day[day] = ne

    print("\n-- realized sells (units, avg price, revenue):")
    for item in sorted(sold_units, key=lambda k: -rev[k]):
        u = sold_units[item]
        if u > 0:
            print(f"   {item:12s} {u:5d}u  avg ${rev[item]/u:7.2f}  total ${rev[item]:,}")

    print("\n-- price timeline (sampled h12) for key items:")
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]:
        tl = price_tl[item]
        days = sorted(tl)
        if not days:
            continue
        pts = " ".join(f"d{d}:{tl[d]}" for d in days if d % 4 == 0)
        print(f"   {item:12s} {pts}")

    print("\n-- inventory timeline (sampled h12, delta vs I0=10000):")
    for item in ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]:
        tl = inv_tl[item]
        days = sorted(tl)
        if not days:
            continue
        pts = " ".join(f"d{d}:{tl[d]-10000:+d}" for d in days if d % 4 == 0)
        print(f"   {item:12s} {pts}")

    print("\n-- ops per day:")
    print(f"   FEED by day:    {dict(sorted(feed_ops.items()))}")
    print(f"   WATER by day:  {dict(sorted(water_ops.items()))}")
    print(f"   DIG by day:    {dict(sorted(dig_ops.items()))}")
    print(f"   BUILD by day:  {dict(sorted(build_ops.items()))}")
    print(f"   PICKUP by day: {dict(sorted(pickup_ops.items()))}")
    print("   PLANT by day:")
    for d in sorted(plant_ops):
        if plant_ops[d]:
            print(f"      d{d:2d}: {dict(plant_ops[d])}")

    print(f"\n   HIRE hours histogram: {dict(sorted(hire_hours.items()))}")

    occ = [o for _, o in shed_occ]
    occ.sort()
    n = len(occ)
    print(f"\n   shed occupancy: peak {occ[-1]}, p99 {occ[int(n*0.99)]}, p90 {occ[int(n*0.90)]}, median {occ[n//2]}")

    print(f"\n   animal first-seen days: { {k: sorted(set(v))[:1] for k, v in animal_first.items()} }")
    print(f"   animals at end: { {k: len(set(v)) for k, v in animal_first.items()} }")

    print("\n   WEED tiles by day (h23):")
    print("      " + " ".join(f"d{d}:{dead_tiles_day[d]}" for d in sorted(dead_tiles_day) if d % 2 == 0))
    print("\n   EMPTY tiles by day (h23):")
    print("      " + " ".join(f"d{d}:{empty_tiles_day[d]}" for d in sorted(empty_tiles_day) if d % 2 == 0))

    print("\n   money by day (h23 of each day):")
    print("      " + " ".join(f"d{d}:${money_day.get(d,0):,}" for d in sorted(money_day)))


if __name__ == "__main__":
    base = "/home/z/my-project/kaggriculture/battles/"
    audit(base + "t79_replay_v16_ahmedv41_s365.jsonl", 1, "ahmedv41")
