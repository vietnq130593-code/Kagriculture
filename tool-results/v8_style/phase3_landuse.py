#!/usr/bin/env python3
"""Task 43 phase 3 — land-use accounting: productive/weed/empty tile-days by phase."""
import json, glob
from collections import defaultdict

UNIT_DIRS = ("NORTH", "SOUTH", "EAST", "WEST")


def load_kaggle(path):
    d = json.load(open(path))
    steps = []
    for t, row in enumerate(d["steps"]):
        obs = row[0]["observation"]
        steps.append({"t": t, "day": obs["day"], "hour": obs["hour"], "farms": obs["farms"]})
    return steps, d["info"]["TeamNames"]


def load_arena(path):
    raw = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") == "hello":
                names = [d.get("a"), d.get("b")]
            elif d.get("t") == "turn":
                raw.append(d)
    steps = [{"t": d["step"], "day": d["day"], "hour": d["hour"], "farms": d["farms"]}
             for d in raw]
    return steps, names


def day_end_snapshot(steps, pidx):
    """best-effort end-of-day state per day (hour 23; fallback hour 22)."""
    per_day = {}
    for s in steps:
        per_day.setdefault(s["day"], None)
        if s["hour"] >= 22:
            per_day[s["day"]] = s["farms"][pidx]
    return per_day


def count_tiles(farm):
    empty = weeds = plants = animals = alive = nulls = 0
    for row in farm["tiles"]:
        for t in row:
            if t == "LOCKED" or t is None:
                empty += 1 if t is None else 0
            elif t.get("kind") == "WEED":
                weeds += 1
            elif t.get("kind") == "PLANT":
                plants += 1
            elif t.get("kind") in ("COOP", "PASTURE"):
                if "animal" in t:
                    animals += 1
                else:
                    nulls += 1
    return empty, weeds, plants, animals, nulls


def land_use(steps, pidx):
    per_day = day_end_snapshot(steps, pidx)
    R = {}
    for d in sorted(per_day):
        farm = per_day[d]
        if farm is None:
            continue
        e, w, p, a, n = count_tiles(farm)
        unlocked = len(farm.get("unlocked_quadrants") or ["NW"]) * 25
        R[d] = {"empty": e, "weeds": w, "plants": p, "animals": a, "nulls": n,
                "unlocked": unlocked,
                "productive": p + a,
                "dead": e + w + n}  # empty + weed + empty-structure
    return R


def phase_sums(R):
    """sum tile-days per phase; unlocked excludes pre-purchase days."""
    phases = [("mở đầu d1-7", 1, 7), ("giữa d8-20", 8, 20),
              ("cuối d21-28", 21, 28)]
    out = []
    for name, lo, hi in phases:
        prod = dead = unlok = an = pl = wd = 0
        ndays = 0
        for d in range(lo, hi + 1):
            if d not in R:
                continue
            r = R[d]
            ndays += 1
            prod += r["productive"]
            dead += r["dead"]
            unlok += r["unlocked"]
            an += r["animals"]
            pl += r["plants"]
            wd += r["weeds"]
        if ndays:
            out.append((name, ndays, unlok / ndays, prod / ndays, dead / ndays,
                        pl / ndays, an / ndays, wd / ndays))
    return out


sources = []
for p in ("/home/z/my-project/upload/107559251.json", "/home/z/my-project/upload/107573831.json"):
    steps, names = load_kaggle(p)
    sources.append((p.split("/")[-1][:11], steps, names))
for p in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/v8_seatA_*.jsonl")):
    steps, names = load_arena(p)
    sources.append((p.split("/")[-1].replace(".jsonl", ""), steps, names))

print(f"{'trace':<22} {'player':<8} {'giai đoạn':<14} {'ngày':>4} {'ô mở':>6} "
      f"{'sản xuất/ngày':>13} {'chết/ngày':>10} {'cây':>5} {'đàn':>5} {'weed':>5} {'%sd':>6}")
tot = defaultdict(list)
for tag, steps, names in sources:
    for pidx in (0, 1):
        R = land_use(steps, pidx)
        for (name, nd, ul, pr, dd, pl, an, wd) in phase_sums(R):
            print(f"{tag:<22} {names[pidx]:<8} {name:<14} {nd:>4} {ul:>6.1f} "
                  f"{pr:>13.1f} {dd:>10.1f} {pl:>5.1f} {an:>5.1f} {wd:>5.1f} "
                  f"{100*pr/ul:>5.1f}%")
            key = ("TOP3" if names[pidx] not in ("v8", "v7") else names[pidx], name)
            tot[key].append((ul, pr, dd, pl, an, wd))

print()
print("=" * 100)
print("TỔNG HỢP TRUNG BÌNH THEO NHÓM  (ô mở TB | sản xuất TB | chết TB | cây | đàn | weed)")
for key in sorted(tot):
    rows = tot[key]
    n = len(rows)
    ul = sum(r[0] for r in rows) / n
    pr = sum(r[1] for r in rows) / n
    dd = sum(r[2] for r in rows) / n
    pl = sum(r[3] for r in rows) / n
    an = sum(r[4] for r in rows) / n
    wd = sum(r[5] for r in rows) / n
    print(f"  {key[0]:<6} {key[1]:<14} ô mở={ul:5.1f} sản xuất={pr:5.1f} ({100*pr/ul:4.1f}%) "
          f"chết={dd:5.1f} cây={pl:5.1f} đàn={an:5.1f} weed={wd:5.1f}")
