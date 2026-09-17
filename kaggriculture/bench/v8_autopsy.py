#!/usr/bin/env python3
"""V7 AUTOPSY v2 — so sánh trực tiếp cơ cấu lao động + cây + đàn với top-3.

Chuẩn top-3 (mùa 30 ngày, từ TOP3_REPLAY_ANALYSIS.md V3.0 exact):
  WATER 982-1387 | HARVEST 410-615 | FEED 135-446 | CARE 136-387
  COLLECT_FERT 173-420 | FERTILIZE 91-186 | PLACE 15-20 | move ~2700-3100 (48-52%)
  Đàn: 15-22 con | cây đứng 45-60 ô | empty 0-7 ô d9-27
"""
import json, sys
from collections import defaultdict

UNIT_DIRS = ("NORTH", "SOUTH", "EAST", "WEST")

def tile_states(tiles):
    locked = empty = weeds = 0
    plants = defaultdict(int)
    animals = defaultdict(int)
    for row in tiles:
        for t in row:
            if t == "LOCKED":
                locked += 1
            elif t is None:
                empty += 1
            elif t.get("kind") == "WEED":
                weeds += 1
            elif t.get("kind") == "PLANT":
                plants[t.get("crop")] += 1
            elif t.get("kind") in ("COOP", "PASTURE"):
                animals[t.get("animal")] += 1
    return locked, empty, weeds, dict(plants), dict(animals)

def analyze(path):
    days = {}
    ops_season = defaultdict(int)          # op -> count (unit actions only)
    ops_daily = defaultdict(lambda: defaultdict(int))  # day -> op -> n
    landbuys = []
    mkt = defaultdict(int)
    a_name = b_name = None
    rewards = None
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            t = d.get("t")
            if t == "hello":
                a_name, b_name = d.get("a"), d.get("b")
            elif t == "turn":
                step, day = d["step"], d.get("day", d["step"] // 24)
                acts = (d.get("acts") or [None, None])[0]
                if acts:
                    for grp in (acts.get("market") or []):
                        if grp:
                            mkt[grp[0]] += 1
                            if grp[0] == "BUY_LAND":
                                landbuys.append(day)
                    for u in ([acts.get("farmer")] + list(acts.get("hands") or [])):
                        if not u: continue
                        op = u[0]
                        if op in UNIT_DIRS:
                            ops_season["MOVE"] += 1
                            ops_daily[day]["MOVE"] += 1
                        else:
                            ops_season[op] += 1
                            ops_daily[day][op] += 1
                if d.get("hour") == 23 or step >= 718:
                    snaps = []
                    for farm in d["farms"]:
                        locked, empty, weeds, plants, animals = tile_states(farm["tiles"])
                        snaps.append({
                            "locked": locked, "empty": empty, "weeds": weeds,
                            "unlocked": 100 - locked,
                            "plants": plants, "animals": animals,
                            "hands": len(farm.get("hands") or []),
                            "money": farm.get("money"),
                        })
                    days[day] = snaps
            elif t == "end":
                rewards = d.get("rewards")
    return a_name, b_name, days, landbuys, rewards, ops_season, ops_daily, mkt

def main():
    files = sys.argv[1:]
    agg = defaultdict(lambda: defaultdict(float))
    for path in files:
        a, b, days, landbuys, rewards, ops, ops_daily, mkt = analyze(path)
        print(f"\n{'='*80}\n{path.split('/')[-1]}: {a} vs {b}  rewards={rewards}  landbuys d={sorted(set(landbuys))}")
        print(f"{'d':>3} {'own':>3} {'emp':>3} {'wd':>3} | {'plants':<44} | animals | hands")
        for day in sorted(days):
            if day % 3 != 0 and day not in (1, 2, 9, 27, 28, 29): continue
            s = days[day][0]
            pl = " ".join(f"{k[:4]}:{v}" for k, v in sorted(s["plants"].items(), key=lambda x: -x[1]))
            an = " ".join(f"{(k or '?')[:2]}×{v}" for k, v in sorted(s["animals"].items(), key=lambda x: str(x[0])))
            print(f"{day:>3} {s['unlocked']:>3} {s['empty']:>3} {s['weeds']:>3} | {pl:<44} | {an:<14} | {s['hands']:>2}")
        print("\n  Cơ cấu lệnh unit (cả mùa) [top-3: WATER 982-1387 | HARV 410-615 | FEED 135-446 | CARE 136-387 | CFERT 173-420 | FERT 91-186 | MOVE ~48-52% raw]:")
        row = "   "
        for op, n in sorted(ops.items(), key=lambda x: -x[1]):
            row += f"{op}={n} "
        print(row)
        # wheat-quality: harvest/plant ratio
        print("\n  Lệnh/ngày theo loại (chọn d11-20):")
        for day in sorted(ops_daily):
            if day in (11, 13, 15, 17, 19, 20, 24, 28):
                od = ops_daily[day]
                print(f"   d{day}: " + " ".join(f"{k}={v}" for k, v in sorted(od.items(), key=lambda x: -x[1])))
        # empty stats
        emps, wds = [], []
        for day in sorted(days):
            if 9 <= day <= 27:
                s = days[day][0]
                emps.append(s["empty"]); wds.append(s["weeds"])
        print(f"  → empty TB d9-27: {sum(emps)/len(emps):.1f} ô | weed TB: {sum(wds)/len(wds):.1f} ô | tổng bỏ không: {(sum(emps)+sum(wds))/len(emps):.1f}/{days[15][0]['unlocked']} ô")
        for op, n in ops.items():
            agg[op]["sum"] += n / len(files)
    print(f"\n{'='*80}\nTB cơ cấu lệnh trên {len(files)} trận (mùa):")
    for op, v in sorted(agg.items(), key=lambda x: -x[1]["sum"]):
        print(f"  {op:<20} {v['sum']:.0f}")

if __name__ == "__main__":
    main()
