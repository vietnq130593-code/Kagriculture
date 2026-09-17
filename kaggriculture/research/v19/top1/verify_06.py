#!/usr/bin/env python3
"""Verify các con số còn nghi vấn trong 06_TOP1_7MATCH_DEEP_ANALYSIS.md."""
import json
from collections import defaultdict

MATCHES = {
    "m1": ("match1", 1), "m2": ("match2", 0), "m3": ("match3", 1),
    "m4": ("match4", 1), "m5": ("match5", 1), "m6": ("match6", 1), "m7": ("match7", 1),
}

sells = json.load(open("an5_sells.json"))
print("=" * 90)
print("V1. KHUNG GIỜ BÁN chính xác từ an5_sells.json (% doanh thu)")
print("=" * 90)
for label, filt in [("MAJKEL", True), ("OPP", False)]:
    rows = [r for r in sells if r["is_majkel"] == filt]
    tot = sum(r["units"] * r["unit_price"] for r in rows)
    groups = {"h22-23+h0-1": [22, 23, 0, 1], "h2-7": list(range(2, 8)),
              "h8-15": list(range(8, 16)), "h16-21": list(range(16, 22))}
    out = []
    for g, hours in groups.items():
        d = sum(r["units"] * r["unit_price"] for r in rows if r["hour"] in hours)
        out.append(f"{g}: {100*d/tot:.1f}%")
    print(f"  {label}: " + "  ".join(out))

print()
print("=" * 90)
print("V2. MELON seed spend + ROI (seed price từ orders BUY_SEED MELON)")
print("=" * 90)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    n_pkts, spend, mel_rev, mel_units = 0, 0.0, 0.0, 0
    for o in ords:
        if o["player"] != midx: continue
        if o["op"] == "BUY_SEED" and o["item"] == "MELON" and o["units"] > 0:
            n_pkts += o["units"]; spend += o["cash"]
        elif o["op"] == "SELL" and o["item"] == "MELON" and o["units"] > 0:
            mel_rev += o["cash"]; mel_units += o["units"]
    roi = mel_rev / spend if spend else 0
    print(f"  {key}: {n_pkts} gói ${spend:.0f} (unit ${spend/max(1,n_pkts):.0f}) → bán {mel_units}u ${mel_rev:.0f}  ROI {roi:.1f}x")

print()
print("=" * 90)
print("V3. UNITS BÁN NGÀY 29 từng trận (Majkel vs OPP) — kiểm tra claim 'm7: 249 vs 176'")
print("=" * 90)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    mu = sum(o["units"] for o in ords if o["player"] == midx and o["op"] == "SELL" and o["day"] == 29 and o["units"] > 0)
    ou = sum(o["units"] for o in ords if o["player"] != midx and o["op"] == "SELL" and o["day"] == 29 and o["units"] > 0)
    print(f"  {key}: Majkel {mu}u vs OPP {ou}u")

print()
print("=" * 90)
print("V4. FEED WHEAT percentile khi mua (Majkel) — range thực")
print("=" * 90)
pcts = []
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    mkt = json.load(open(f"{mdir}/market.json"))
    prices = {m["step"]: m["prices"] for m in mkt}
    pmin, pmax = {}, {}
    for m in mkt:
        for it, p in m["prices"].items():
            if it not in pmin or p < pmin[it]: pmin[it] = p
            if it not in pmax or p > pmax[it]: pmax[it] = p
    # feed = BUY_PRODUCT WHEAT
    buys = [(o["step"], o["units"], o["cash"]) for o in ords
            if o["player"] == midx and o["op"] == "BUY_PRODUCT" and o["item"] == "WHEAT" and o["units"] > 0]
    if not buys: continue
    wpct = 0.0; wu = 0
    for st, u, c in buys:
        cur = prices[st]["WHEAT"]
        span = pmax["WHEAT"] - pmin["WHEAT"]
        pct = 100 * (cur - pmin["WHEAT"]) / span if span > 0 else 50
        wpct += pct * u; wu += u
    pcts.append(wpct / wu)
    print(f"  {key}: {sum(u for _,u,_ in buys)}u feed-WHEAT, percentile $-weighted {wpct/wu:.0f}%")
print(f"  → RANGE percentile: {min(pcts):.0f}-{max(pcts):.0f}%")

print()
print("=" * 90)
print("V5. CROP MIX ranges chính xác (plants cuối ngày d8/d10/d14/d29, Majkel)")
print("=" * 90)
for day in (8, 10, 14, 18, 29):
    vals = {}
    for key, (mdir, midx) in MATCHES.items():
        daily = json.load(open(f"{mdir}/daily.json"))
        for r in daily:
            if r["player"] == midx and r["day"] == day:
                for it, n in r.get("plants", {}).items():
                    vals.setdefault(it, []).append(n)
    s = "  d%d: " % day + "  ".join(f"{it} {min(v)}-{max(v)}" for it, v in sorted(vals.items()))
    print(s)

print()
print("=" * 90)
print("V6. MELON giá bán range d11-19 (đơn giá từng lệnh, Majkel)")
print("=" * 90)
allp = []
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    for o in ords:
        if o["player"] == midx and o["op"] == "SELL" and o["item"] == "MELON" and o["units"] > 0 and 11 <= o["day"] <= 19:
            allp.append(o["cash"] / o["units"])
print(f"  MELON d11-19: đơn giá min {min(allp):.0f} max {max(allp):.0f} (n={len(allp)})")

print()
print("=" * 90)
print("V7. 5-STEP-END revenue từng trận + lệnh anchor lớn nhất (Majkel)")
print("=" * 90)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    last = [(o["cash"], o["step"], o["item"], o["units"]) for o in ords
            if o["player"] == midx and o["op"] == "SELL" and o["units"] > 0 and o["step"] >= 715]
    tot = sum(c for c, *_ in last)
    big = max(last) if last else (0, 0, "-", 0)
    print(f"  {key}: 5s cuối ${tot:.0f}; lệnh lớn nhất s{big[1]} {big[2]}x{big[3]} ${big[0]:.0f}")

print()
print("=" * 90)
print("V8. Collision index — 'bằng' có phải index-0? (đọc logic an5_attack.py)")
print("=" * 90)
src = open("an5_attack.py").read()
i = src.find("bằng")
# tìm đoạn code xử lý index
for ln in src.splitlines():
    if "index" in ln.lower() or "i0" in ln or "i1" in ln:
        print("   |", ln.rstrip())
