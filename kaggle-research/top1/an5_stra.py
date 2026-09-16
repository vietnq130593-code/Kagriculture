#!/usr/bin/env python3
"""Stage 5: CHIẾN DỊCH STRAWBERRY + shed management + cadence bán theo ngày."""
import json
from collections import defaultdict

MATCHES = {
    "m1": ("match1", 1), "m2": ("match2", 0), "m3": ("match3", 1),
    "m4": ("match4", 1), "m5": ("match5", 1), "m6": ("match6", 1), "m7": ("match7", 1),
}

print("=" * 100)
print("1. STRAWBERRY — units bán theo ngày + đơn giá + giá thị trường TB ngày (Majkel)")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    mkt = json.load(open(f"{mdir}/market.json"))
    day_price = defaultdict(list)
    for m in mkt: day_price[m["step"] // 24].append(m["prices"]["STRAWBERRY"])
    byday = defaultdict(lambda: [0, 0.0])  # day -> [units, $]
    for o in ords:
        if o["player"] == midx and o["op"] == "SELL" and o["item"] == "STRAWBERRY" and o["units"] > 0:
            byday[o["day"]][0] += o["units"]; byday[o["day"]][1] += o["cash"]
    line = ""
    for d in sorted(byday):
        u, c = byday[d]
        avg = day_price[d] and sum(day_price[d]) / len(day_price[d])
        line += f"d{d}:{u}u@{c/u:.0f}(mkt{avg:.0f})  "
    print(f"  {key}: {line}")

print()
print("=" * 100)
print("2. SHED UTILIZATION — shed_total theo mốc giờ mỗi ngày (Majkel): min/avg/max")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    tl = json.load(open(f"{mdir}/timeline.json"))
    rows = [r for r in tl if r["player"] == midx]
    # shed_total theo pha giờ: sáng h0-6, trưa h7-15, tối h16-23
    ph = {"h0-6": [], "h7-15": [], "h16-23": []}
    for r in rows:
        h = r["hour"]
        k = "h0-6" if h <= 6 else "h7-15" if h <= 15 else "h16-23"
        ph[k].append(r["shed_total"])
    out = []
    for k, v in ph.items():
        if v: out.append(f"{k}:{min(v)}/{sum(v)/len(v):.0f}/{max(v)}")
    # số step shed >= 95 (nguy cơ overflow)
    nfull = sum(1 for r in rows if r["shed_total"] >= 95)
    print(f"  {key}: " + "  ".join(out) + f"  | steps shed>=95: {nfull}")

print()
print("=" * 100)
print("3. CADENCE BÁN THEO NGÀY — số lệnh SELL + units mỗi ngày (Majkel vs OPP, TB 7 trận)")
print("=" * 100)
cad = defaultdict(lambda: {"M": [0, 0], "O": [0, 0]})
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    for o in ords:
        if o["op"] != "SELL" or o["units"] <= 0: continue
        tag = "M" if o["player"] == midx else "O"
        cad[o["day"]][tag][0] += 1; cad[o["day"]][tag][1] += o["units"]
n = len(MATCHES)
print(f"{'day':>3} {'M_lệnh':>7} {'M_units':>8} {'O_lệnh':>7} {'O_units':>8}")
for d in sorted(cad):
    m, o = cad[d]["M"], cad[d]["O"]
    print(f"{d:>3} {m[0]/n:>7.1f} {m[1]/n:>8.1f} {o[0]/n:>7.1f} {o[1]/n:>8.1f}")

print()
print("=" * 100)
print("4. HARI/động tác mỗi ngày — hires_today TB (Majkel) và tổng verbs TB/ngày")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    tl = json.load(open(f"{mdir}/timeline.json"))
    rows = [r for r in tl if r["player"] == midx]
    byday_h = defaultdict(list); byday_v = defaultdict(int)
    for r in rows:
        byday_h[r["day"]].append(r.get("hires_today", 0))
        byday_v[r["day"]] += sum(r.get("unit_verbs", {}).values())
    hires = [sum(byday_h[d]) / max(1, len(byday_h[d])) for d in sorted(byday_h)]
    print(f"  {key}: hires TB/ngày: {' '.join(f'{h:.1f}' for h in hires)}")

print()
print("=" * 100)
print("5. MELON OPENING — units bán + giá theo ngày d9-15 (Majkel) và chứng cứ 'chỉ 1 đợt'")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    byday = defaultdict(lambda: [0, 0.0])
    for o in ords:
        if o["player"] == midx and o["op"] == "SELL" and o["item"] == "MELON" and o["units"] > 0:
            byday[o["day"]][0] += o["units"]; byday[o["day"]][1] += o["cash"]
    if byday:
        print(f"  {key}: " + "  ".join(f"d{d}:{u}u@{c/u:.0f}" for d, (u, c) in sorted(byday.items())))

print()
print("=" * 100)
print("6. TỔNG KẾT CHIẾN LƯỢC — tổng units từng item bán (Majkel TB/match)")
print("=" * 100)
item_stats = defaultdict(lambda: [0, 0.0, 0])
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    per = defaultdict(lambda: [0, 0.0])
    for o in ords:
        if o["player"] == midx and o["op"] == "SELL" and o["units"] > 0:
            per[o["item"]][0] += o["units"]; per[o["item"]][1] += o["cash"]
    for it, (u, c) in per.items():
        item_stats[it][0] += u; item_stats[it][1] += c; item_stats[it][2] += 1
n = len(MATCHES)
print(f"{'item':11} {'units/match':>11} {'$/match':>9} {'đơn giá':>7}")
for it, (u, c, cnt) in sorted(item_stats.items(), key=lambda x: -x[1][1]):
    print(f"{it:11} {u/n:>11.1f} {c/n:>9.0f} {c/u:>7.1f}")
