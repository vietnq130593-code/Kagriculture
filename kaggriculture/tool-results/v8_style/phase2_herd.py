#!/usr/bin/env python3
"""Task 43 phase 2 — escape timeline, early money, service intensity, herd curve."""
import json, gzip, glob
from collections import defaultdict

BOARD = 10
UNIT_DIRS = ("NORTH", "SOUTH", "EAST", "WEST")


def load_arena(path):
    raw = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") == "hello":
                names = [d.get("a"), d.get("b")]
            elif d.get("t") == "turn":
                raw.append(d)
    return raw, names


def load_kaggle(path):
    d = json.load(open(path))
    steps = []
    for t, row in enumerate(d["steps"]):
        obs = row[0]["observation"]
        steps.append({"t": t, "day": obs["day"], "hour": obs["hour"],
                      "farms": obs["farms"],
                      "acts": [row[i].get("action") for i in range(2)]})
    return steps, d["info"]["TeamNames"]


def null_animals(farm):
    n = 0
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and "animal" not in t:
                n += 1
    return n


def herd(farm):
    h = defaultdict(int)
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and "animal" in t:
                h[t["animal"]] += 1
    return dict(h)


def daily_profile(steps, pidx):
    """per-day: null structures, herd, plants n, market ops summary."""
    out = {}
    for s in steps:
        day = s["day"]
        farm = s["farms"][pidx]
        act = (s["acts"] or [None, None])[pidx]
        if day not in out:
            out[day] = {"null": 0, "herd": {}, "plants": 0, "buys": defaultdict(int),
                        "mkt_ops": [], "money": 0}
        if s["hour"] == 23:
            out[day]["null"] = null_animals(farm)
            out[day]["herd"] = herd(farm)
            out[day]["plants"] = sum(1 for row in farm["tiles"] for t in row
                                     if isinstance(t, dict) and t.get("kind") == "PLANT")
            out[day]["money"] = farm.get("money")
        if act:
            for g in (act.get("market") or []):
                if g and g[0] == "BUY_ANIMAL":
                    out[day]["buys"][g[1]] += g[2] if len(g) > 2 else 1
                elif g and g[0] in ("BUY_SEED", "BUY_LAND", "HIRE", "BUY_PRODUCT"):
                    out[day]["mkt_ops"].append((s["hour"], g))
    return out


def service_counts(steps, pidx):
    """FEED/CARE/COLLECT per day + count animals fed (via post-state fed flags is
    expensive; approximate via FEED op count)."""
    feed = defaultdict(int); care = defaultdict(int); coll = defaultdict(int)
    for s in steps:
        act = (s["acts"] or [None, None])[pidx]
        if not act:
            continue
        for u in ([act.get("farmer")] + list(act.get("hands") or [])):
            if not u:
                continue
            if u[0] == "FEED":
                feed[s["day"]] += 1
            elif u[0] == "CARE":
                care[s["day"]] += 1
            elif u[0] == "COLLECT_FERTILIZER":
                coll[s["day"]] += 1
    return feed, care, coll


print("=" * 108)
print("A) TIMELINE ĐÀN + STRUCTURE RỖNG (escape) — theo ngày")
print("=" * 108)
sources = []
for p in ("/home/z/my-project/upload/107559251.json", "/home/z/my-project/upload/107573831.json"):
    steps, names = load_kaggle(p)
    tag = p.split("/")[-1].replace(".json", "")
    sources.append((tag, steps, names))
for p in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/v8_seatA_*.jsonl")):
    raw, names = load_arena(p)
    steps = [{"t": d["step"], "day": d["day"], "hour": d["hour"], "farms": d["farms"],
              "acts": d.get("acts")} for d in raw]
    sources.append((p.split("/")[-1].replace(".jsonl", ""), steps, names))

for tag, steps, names in sources:
    for pidx in (0, 1):
        prof = daily_profile(steps, pidx)
        feed, care, coll = service_counts(steps, pidx)
        print(f"\n### {tag} seat{pidx} = {names[pidx]}")
        print(f"{'d':>3} {'đàn sống':<26} {'mua':<16} {'rỗng':>4} {'cây':>3} {'FEED':>4} {'CARE':>4} {'CFERT':>5} {'feed/đàn':>8} {'money':>8}")
        for d in sorted(prof):
            if d > 12 and d not in (15, 18, 20, 22, 24, 26, 28, 29):
                continue
            pr = prof[d]
            hd = pr["herd"]
            hd_s = " ".join(f"{k[:2]}×{v}" for k, v in sorted(hd.items()))
            bu = " ".join(f"{k[:2]}+{v}" for k, v in pr["buys"].items()) or "-"
            n_animals = sum(hd.values())
            f_ = feed.get(d, 0); c_ = care.get(d, 0); k_ = coll.get(d, 0)
            ratio = f"{f_/n_animals:.2f}" if n_animals else "-"
            print(f"{d:>3} {hd_s:<26} {bu:<16} {pr['null']:>4} {pr['plants']:>3} {f_:>4} {c_:>4} {k_:>5} {ratio:>8} {pr['money']:>8,.0f}")
