#!/usr/bin/env python3
"""Stage 2: NGUYÊN LÝ BÁN — price percentile khi bán, hour-of-day, chunk size,
hold time từ harvest→sell, và bằng chứng trough-throttle."""
import json
from collections import defaultdict

MATCHES = {
    "m1": ("match1", 1), "m2": ("match2", 0), "m3": ("match3", 1),
    "m4": ("match4", 1), "m5": ("match5", 1), "m6": ("match6", 1), "m7": ("match7", 1),
}
BASE = {"WHEAT": 25, "CARROT": 35, "TOMATO": 60, "STRAWBERRY": 120, "MELON": 250,
        "EGG": 50, "MILK": 160, "WOOL": 200, "FERTILIZER": 100}

sell_rows = []       # từng order SELL của từng player
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    mkt = json.load(open(f"{mdir}/market.json"))
    tl = json.load(open(f"{mdir}/timeline.json"))
    prices = {m["step"]: m["prices"] for m in mkt}

    # min/max price toàn trận mỗi item (để tính percentile)
    pmin, pmax = {}, {}
    for m in mkt:
        for it, p in m["prices"].items():
            if it not in pmin or p < pmin[it]: pmin[it] = p
            if it not in pmax or p > pmax[it]: pmax[it] = p

    # lịch sử shed theo từng item từng player (để tính hold time)
    shed_hist = {0: defaultdict(list), 1: defaultdict(list)}  # player -> item -> [(step, delta)]
    for r in tl:
        pass  # timeline chỉ có shed cuối step; orders DROP/PICKUP không có trong orders.json
              # -> hold-time tính theo cách khác: khoảng cách từ khi units xuất hiện trong shed

    for o in ords:
        if o["op"] != "SELL" or o["units"] <= 0: continue
        p = o["player"]
        it = o["item"]
        cur = prices[o["step"]][it]
        span = pmax[it] - pmin[it]
        pct = 100 * (cur - pmin[it]) / span if span > 0 else 50.0
        vs_base = 100 * (o["cash"] / o["units"]) / BASE[it] if BASE[it] else 0
        sell_rows.append({
            "match": key, "player": p, "is_majkel": p == midx,
            "step": o["step"], "day": o["day"], "hour": o["step"] % 24,
            "item": it, "units": o["units"], "unit_price": o["cash"] / o["units"],
            "mkt_price": cur, "pct": pct, "vs_base": vs_base,
            "pre_price": prices[max(0, o["step"] - 1)][it],
            "post_price": prices[min(719, o["step"] + 1)][it],
        })

# ============ 1. Price percentile khi bán ============
print("=" * 100)
print("1. PERCENTILE GIÁ KHI BÁN (0 = đáy trận, 100 = đỉnh trận)")
print("=" * 100)
for label, filt in [("MAJKEL", True), ("OPP", False)]:
    rows = [r for r in sell_rows if r["is_majkel"] == filt]
    per_item = defaultdict(list)
    for r in rows: per_item[r["item"]].append(r)
    print(f"\n--- {label} ({len(rows)} sells) ---")
    print(f"{'item':11} {'n':>4} {'pct avg':>8} {'pct w$':>7} {'vs_base':>8} {'đơn giá TB':>10} {'chunk TB':>8}")
    for it in sorted(per_item, key=lambda i: -sum(r['units'] * r['unit_price'] for r in per_item[i])):
        rs = per_item[it]
        w = sum(r["units"] for r in rs)
        wpct = sum(r["pct"] * r["units"] for r in rs) / w
        apct = sum(r["pct"] for r in rs) / len(rs)
        vb = sum(r["vs_base"] * r["units"] for r in rs) / w
        up = sum(r["unit_price"] * r["units"] for r in rs) / w
        ch = sum(r["units"] for r in rs) / len(rs)
        print(f"{it:11} {len(rs):>4} {apct:>8.1f} {wpct:>7.1f} {vb:>7.0f}% {up:>10.1f} {ch:>8.1f}")

# ============ 2. Hour-of-day bán ============
print("\n" + "=" * 100)
print("2. HOUR-OF-DAY BÁN (tần suất + $ theo giờ, Majkel)")
print("=" * 100)
for label, filt in [("MAJKEL", True), ("OPP", False)]:
    rows = [r for r in sell_rows if r["is_majkel"] == filt]
    hourly = defaultdict(lambda: [0, 0.0])
    for r in rows:
        hourly[r["hour"]][0] += 1; hourly[r["hour"]][1] += r["units"] * r["unit_price"]
    print(f"\n--- {label} ---   (giờ: n_orders $revenue)")
    line1 = "h:   "; line2 = "n:   "; line3 = "$:   "
    for h in range(24):
        n, d = hourly.get(h, (0, 0.0))
        line1 += f"{h:>6}"; line2 += f"{n:>6}"; line3 += f"{int(d/100):>6}"
    print(line1); print(line2); print(line3 + "  ($/100)")

# ============ 3. Chunk size (đơn vị mỗi lệnh bán) ============
print("\n" + "=" * 100)
print("3. CHUNK SIZE — đơn vị mỗi lệnh SELL (phân bố %, Majkel vs OPP)")
print("=" * 100)
for label, filt in [("MAJKEL", True), ("OPP", False)]:
    rows = [r for r in sell_rows if r["is_majkel"] == filt]
    buckets = defaultdict(int); dollars = defaultdict(float)
    for r in rows:
        b = "1-2" if r["units"] <= 2 else "3-5" if r["units"] <= 5 else "6-10" if r["units"] <= 10 else "11-20" if r["units"] <= 20 else "21+"
        buckets[b] += 1; dollars[b] += r["units"] * r["unit_price"]
    tot = sum(buckets.values()); td = sum(dollars.values())
    print(f"\n{label}: n={tot}, $={td:.0f}")
    for b in ["1-2", "3-5", "6-10", "11-20", "21+"]:
        print(f"  chunk {b:>6}: {buckets.get(b,0):>4} ({100*buckets.get(b,0)/tot:>4.1f}%)  ${dollars.get(b,0):>8.0f} ({100*dollars.get(b,0)/td:>4.1f}%)")

# ============ 4. Tác động giá: pre → execution → post ============
print("\n" + "=" * 100)
print("4. GIÁ TRƯỚC/DƯỚI MỖI LỆNH BÁN (impact mỗi lệnh, avg theo item — MAJKEL)")
print("=" * 100)
for label, filt in [("MAJKEL", True), ("OPP", False)]:
    rows = [r for r in sell_rows if r["is_majkel"] == filt]
    per_item = defaultdict(list)
    for r in rows: per_item[r["item"]].append(r)
    print(f"\n--- {label} ---")
    print(f"{'item':11} {'n':>4} {'pre':>7} {'exec':>7} {'post':>7} {'drop/u':>7} (exec = đơn giá TB đạt được)")
    for it in sorted(per_item, key=lambda i: -len(per_item[i])):
        rs = per_item[it]
        n = len(rs)
        pre = sum(r["pre_price"] for r in rs) / n
        ex = sum(r["unit_price"] for r in rs) / n
        post = sum(r["post_price"] for r in rs) / n
        du = (pre - post) / max(1, sum(r["units"] for r in rs) / n)
        print(f"{it:11} {n:>4} {pre:>7.1f} {ex:>7.1f} {post:>7.1f} {du:>7.2f}")

# ============ 5. Bán theo pha trận ============
print("\n" + "=" * 100)
print("5. DOANH THU THEO PHA (d0-9 / d10-19 / d20-26 / d27-29) — Majkel vs OPP")
print("=" * 100)
def phase(d): return "d0-9" if d <= 9 else "d10-19" if d <= 19 else "d20-26" if d <= 26 else "d27-29"
for label, filt in [("MAJKEL", True), ("OPP", False)]:
    rows = [r for r in sell_rows if r["is_majkel"] == filt]
    ph = defaultdict(float); phn = defaultdict(int)
    for r in rows:
        ph[phase(r["day"])] += r["units"] * r["unit_price"]; phn[phase(r["day"])] += 1
    print(f"\n{label}: " + "  ".join(f"{k}: ${ph[k]:>7.0f} (n={phn[k]})" for k in ["d0-9", "d10-19", "d20-26", "d27-29"]))

json.dump(sell_rows, open("an5_sells.json", "w"))
print("\nsaved an5_sells.json")
