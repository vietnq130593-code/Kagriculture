#!/usr/bin/env python3
"""KOPS11 — autopsy phân bổ unit-hour của v10: TẠI SAO WATER CHỈ 629?

Đọc 1 replay JSONL (v10 vs X), với ghế v10 cho trước, và in ra:
  1. Bảng ngày: units | PASS | MOVE | WATER | HARVEST | FEED/CARE/COLLECT | PLANT | mkts(BUY/SELL/HIRE)
  2. Bảng cơ hội nước: mỗi ngày, số ô PLANT sống (theo crop) vs số ô ĐƯỢC TƯỚI
     → "thirsty tiles" = ô sống trong window nước mà KHÔNG được tưới hôm đó
  3. Phân bố PASS theo giờ (giờ nào unit ngồi không)

Cách dùng:
  python3 kops11.py <replay.jsonl> <seat> [--day 10]
"""
import json
import sys
from collections import defaultdict

CROPS = {
    "WHEAT":      {"first_yield_day": 2, "max_yield_day": 4, "interval": 0, "ongoing": False},
    "CARROT":     {"first_yield_day": 2, "max_yield_day": 3, "interval": 0, "ongoing": False},
    "TOMATO":     {"first_yield_day": 8, "max_yield_day": 8, "interval": 1, "ongoing": True},
    "STRAWBERRY": {"first_yield_day": 10, "max_yield_day": 10, "interval": 2, "ongoing": True},
    "MELON":      {"first_yield_day": 10, "max_yield_day": 12, "interval": 0, "ongoing": False},
}

def in_water_window(crop, age):
    cd = CROPS[crop]
    if cd["ongoing"]:
        return True  # ongoing cần nước liên tục (sống + ngày produce)
    ws = (cd["max_yield_day"] + 1) // 2
    return ws <= age <= cd["max_yield_day"]

def main():
    path = sys.argv[1]
    seat = int(sys.argv[2])
    day_filter = None
    if "--day" in sys.argv:
        day_filter = int(sys.argv[sys.argv.index("--day") + 1])

    per_day = defaultdict(lambda: defaultdict(int))
    pass_by_hour = defaultdict(int)
    # mỗi ngày: {crop: [được tưới, sống-trong-window, sống-ngoài-window]}
    water_opp = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
    last_tiles = {}
    units_per_day = defaultdict(int)

    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("t") != "turn":
            continue
        step, day, hour = ev["step"], ev["day"], ev["hour"]
        farm = ev["farms"][seat]
        acts = ev["acts"][seat] if ev.get("acts") else None

        # hành động — farmer + MỖI hand đều 1 op/turn
        if acts:
            if isinstance(acts, dict):
                units = ([acts.get("farmer") or ["PASS"]]
                         + [u or ["PASS"] for u in (acts.get("hands") or [])])
                mk = acts.get("market") or []
            else:
                units, mk = [acts], []
            for mv in units:
                op = mv[0] if isinstance(mv, list) and mv else (mv if isinstance(mv, str) else "PASS")
                per_day[day][op or "PASS"] += 1
                if (op or "PASS") == "PASS":
                    pass_by_hour[hour] += 1
            for o in mk:
                if o and o[0]:
                    per_day[day]["mk_" + o[0]] += 1

        # nước: đếm MỖI ô 1 lần/ngày — lấy snapshot cuối ngày (h23) tránh đếm kép
        n_units = 1 + len(farm.get("hands") or [])
        units_per_day[day] = max(units_per_day[day], n_units)
        if hour >= 23:
            for row in farm["tiles"]:
                for t in row:
                    if isinstance(t, dict) and t.get("kind") == "PLANT":
                        crop = t.get("crop")
                        age = day - t.get("planted_day", day)
                        slot = water_opp[day][crop]
                        if t.get("watered_today"):
                            slot[0] += 1
                        if in_water_window(crop, age):
                            slot[1] += 1
                        else:
                            slot[2] += 1

    days = sorted(set(list(per_day.keys()) + list(water_opp.keys())))
    print(f"{'day':>3} {'unt':>3} {'PASS':>4} {'MOVE':>4} {'WATER':>5} {'HARV':>4} {'FEED':>4} {'CARE':>4} {'COLL':>4} {'PLANT':>5} {'FERT':>4} {'DIG':>4} {'mkTS':>4} | thirsty-window (được tưới/sống-window)")
    tot = defaultdict(int)
    for d in days:
        if day_filter is not None and d != day_filter:
            continue
        p = per_day.get(d, {})
        row = [p.get("PASS", 0), p.get("NORTH", 0) + p.get("SOUTH", 0) + p.get("EAST", 0) + p.get("WEST", 0),
               p.get("WATER", 0), p.get("HARVEST", 0), p.get("FEED", 0), p.get("CARE", 0),
               p.get("COLLECT_FERTILIZER", 0), p.get("PLANT", 0), p.get("FERTILIZE", 0), p.get("DIG", 0),
               p.get("mk_BUY_SEED", 0) + p.get("mk_BUY_PRODUCT", 0) + p.get("mk_BUY_ANIMAL", 0)
               + p.get("mk_SELL", 0) + p.get("mk_HIRE", 0) + p.get("mk_BUY_LAND", 0)]
        for k in ("PASS", "WATER", "HARVEST", "FEED", "CARE", "COLLECT_FERTILIZER", "PLANT", "FERTILIZE", "DIG"):
            tot[k] += p.get(k, 0)
        tot["MOVE"] += row[1]
        w = water_opp.get(d, {})
        wtxt = " ".join(f"{c[:4]}:{v[0]}/{v[1]}" for c, v in sorted(w.items()) if v[1] + v[2] > 0)
        print(f"{d:>3} {units_per_day.get(d,0):>3} {row[0]:>4} {row[1]:>4} {row[2]:>5} {row[3]:>4} {row[4]:>4} {row[5]:>4} {row[6]:>4} {row[7]:>5} {row[8]:>4} {row[9]:>4} {row[10]:>4} | {wtxt}")
    print("\nTỔNG:", dict(tot))
    print("PASS theo giờ:", dict(sorted(pass_by_hour.items())))

if __name__ == "__main__":
    main()
