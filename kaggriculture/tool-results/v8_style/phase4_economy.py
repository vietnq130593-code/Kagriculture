#!/usr/bin/env python3
"""Phase 4 — v8 wheat economy (feed supply) + sell channels + worst dead-land window."""
import json, glob
from collections import defaultdict

UNIT_DIRS = ("NORTH", "SOUTH", "EAST", "WEST")


def load_kaggle(path):
    d = json.load(open(path))
    steps = []
    for t, row in enumerate(d["steps"]):
        obs = row[0]["observation"]
        steps.append({"t": t, "day": obs["day"], "hour": obs["hour"],
                      "farms": obs["farms"],
                      "acts": [row[i].get("action") for i in range(2)]})
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
    steps = [{"t": d["step"], "day": d["day"], "hour": d["hour"], "farms": d["farms"],
              "acts": d.get("acts")} for d in raw]
    return steps, names


def channels(steps, pidx):
    sell = defaultdict(int)
    buy_p = defaultdict(int)
    buy_seed = defaultdict(int)
    for s in steps:
        act = (s["acts"] or [None, None])[pidx]
        if not act:
            continue
        for g in (act.get("market") or []):
            if not g:
                continue
            if g[0] == "SELL":
                sell[g[1]] += g[2] if len(g) > 2 else 1
            elif g[0] == "BUY_PRODUCT":
                buy_p[g[1]] += g[2] if len(g) > 2 else 1
            elif g[0] == "BUY_SEED":
                buy_seed[g[1]] += g[2] if len(g) > 2 else 1
    return sell, buy_p, buy_seed


def daily_wheat_plants(steps, pidx):
    per_day = {}
    for s in steps:
        per_day.setdefault(s["day"], None)
        if s["hour"] >= 22:
            per_day[s["day"]] = s["farms"][pidx]
    out = {}
    for d, farm in per_day.items():
        if farm is None:
            continue
        w = sum(1 for row in farm["tiles"] for t in row
                if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT")
        st = sum(1 for row in farm["tiles"] for t in row
                 if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "STRAWBERRY")
        out[d] = (w, st)
    return out


def dead_series(steps, pidx):
    per_day = {}
    for s in steps:
        per_day.setdefault(s["day"], None)
        if s["hour"] >= 22:
            per_day[s["day"]] = s["farms"][pidx]
    out = {}
    for d, farm in per_day.items():
        if farm is None:
            continue
        dead = 0
        for row in farm["tiles"]:
            for t in row:
                if t is None:
                    dead += 1
                elif isinstance(t, dict) and (t.get("kind") == "WEED" or
                        (t.get("kind") in ("COOP", "PASTURE") and "animal" not in t)):
                    dead += 1
        out[d] = dead
    return out


def worst_window(series):
    days = sorted(series)
    best = None
    for i in range(len(days)):
        for j in range(i + 3, len(days) + 1):
            seg = days[i:j]
            avg = sum(series[d] for d in seg) / len(seg)
            if best is None or avg > best[3]:
                best = (seg[0], seg[-1], len(seg), avg)
    return best


sources = []
for p in ("/home/z/my-project/upload/107559251.json", "/home/z/my-project/upload/107573831.json"):
    steps, names = load_kaggle(p)
    sources.append((p.split("/")[-1][:11], steps, names))
for p in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/v8_seatA_*.jsonl")):
    steps, names = load_arena(p)
    sources.append((p.split("/")[-1].replace(".jsonl", ""), steps, names))

print("=" * 104)
print("A) KÊNH BÁN (units) + MUA WHEAT + MUA HẠT — toàn mùa")
print("=" * 104)
groups = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for tag, steps, names in sources:
    for pidx in (0, 1):
        sell, buy_p, buy_seed = channels(steps, pidx)
        g = "TOP3" if names[pidx] not in ("v8", "v7") else names[pidx]
        for k, v in sell.items():
            groups[g]["sell"][k] += v
        for k, v in buy_p.items():
            groups[g]["buyP"][k] += v
        for k, v in buy_seed.items():
            groups[g]["seed"][k] += v
        print(f"{tag:<21} {names[pidx][:8]:<9} SELL: " +
              " ".join(f"{k[:4]}={v}" for k, v in sorted(sell.items(), key=lambda x: -x[1])))
        if buy_p:
            print(f"{'':<31} BUY_PROD: " + " ".join(f"{k[:4]}={v}" for k, v in sorted(buy_p.items())))
n = {"TOP3": 4, "v8": 3, "v7": 3}
print("\nTB MỘT TRẬN THEO NHÓM:")
for g in ("TOP3", "v8", "v7"):
    s = groups[g]
    print(f"  {g}: sell " + " ".join(f"{k[:4]}={v/n[g]:.0f}" for k, v in sorted(s['sell'].items(), key=lambda x: -x[1])))
    print(f"        buyP " + " ".join(f"{k[:4]}={v/n[g]:.0f}" for k, v in sorted(s['buyP'].items())))
    print(f"        seed " + " ".join(f"{k[:4]}={v/n[g]:.0f}" for k, v in sorted(s['seed'].items())))

print()
print("=" * 104)
print("B) WHEAT/STRAWBERRY ĐỨNG THEO NGÀY (trung bình nhóm)")
print("=" * 104)
series = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for tag, steps, names in sources:
    for pidx in (0, 1):
        g = "TOP3" if names[pidx] not in ("v8", "v7") else names[pidx]
        dw = daily_wheat_plants(steps, pidx)
        for d, (w, st) in dw.items():
            series[g][d][0] += w
            series[g][d][1] += st
print(f"{'d':>3} | {'TOP3 W':>6} {'TOP3 S':>6} | {'v8 W':>5} {'v8 S':>5} | {'v7 W':>5} {'v7 S':>5}")
for d in range(30):
    row = [series[g].get(d, [0, 0]) for g in ("TOP3", "v8", "v7")]
    cnt = {"TOP3": 4, "v8": 3, "v7": 3}
    print(f"{d:>3} | " + " | ".join(
        f"{row[i][0]/cnt[g]:>6.1f} {row[i][1]/cnt[g]:>6.1f}" if i == 0 else
        f"{row[i][0]/cnt[g]:>5.1f} {row[i][1]/cnt[g]:>5.1f}"
        for i, g in enumerate(("TOP3", "v8", "v7"))))

print()
print("=" * 104)
print("C) CỬA SỔ ĐẤT CHẾT (empty+weed+structure rỗng) TỆ NHẤT — trung bình nhóm")
print("=" * 104)
dser = defaultdict(lambda: defaultdict(list))
for tag, steps, names in sources:
    for pidx in (0, 1):
        g = "TOP3" if names[pidx] not in ("v8", "v7") else names[pidx]
        for d, v in dead_series(steps, pidx).items():
            dser[g][d].append(v)
for g in ("TOP3", "v8", "v7"):
    avg = {d: sum(v)/len(v) for d, v in dser[g].items()}
    w = worst_window(avg)
    peak = max(avg.items(), key=lambda kv: kv[1])
    print(f"  {g}: tệ nhất d{w[0]}-d{w[1]} ({w[2]} ngày, TB {w[3]:.1f} ô chết) | đỉnh d{peak[0]} = {peak[1]:.1f} ô")
    print(f"      chuỗi: " + " ".join(f"{d}:{avg[d]:.0f}" for d in sorted(avg)))
