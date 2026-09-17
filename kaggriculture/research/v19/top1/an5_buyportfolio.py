#!/usr/bin/env python3
"""Stage 4: NGUYÊN LÝ MUA & PORTFOLIO — seed/animal/land timing, crop mix theo ngày,
idle cash theo pha, concentration doanh thu, endgame anchor ở 5 trận mới."""
import json
from collections import defaultdict

MATCHES = {
    "m1": ("match1", 1), "m2": ("match2", 0), "m3": ("match3", 1),
    "m4": ("match4", 1), "m5": ("match5", 1), "m6": ("match6", 1), "m7": ("match7", 1),
}

print("=" * 100)
print("1. THỜI ĐIỂM MUA (Majkel) — animal / land / seed-theo-loại, theo ngày")
print("=" * 100)
all_animal_days = defaultdict(list)  # item -> [days]
all_land_days = []
all_seed_days = defaultdict(list)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    for o in ords:
        if o["player"] != midx: continue
        if o["op"] == "BUY_ANIMAL" and o["units"] > 0:
            all_animal_days[o["item"]].append((key, o["day"], o["units"]))
        elif o["op"] == "BUY_LAND":
            all_land_days.append((key, o["day"]))
        elif o["op"] == "BUY_SEED" and o["units"] > 0:
            all_seed_days[o["item"]].append((key, o["day"], o["units"]))

for it, lst in sorted(all_animal_days.items()):
    days = [d for _, d, _ in lst]
    units = sum(u for _, _, u in lst)
    print(f"  {it:6}: {len(lst)} lần mua, {units} con, ngày: {sorted(set(days))}")
print(f"  LAND: {len(all_land_days)} lần — ngày: {sorted(set(d for _, d in all_land_days))}")
for it, lst in sorted(all_seed_days.items()):
    byday = defaultdict(int)
    for _, d, u in lst: byday[d] += u
    print(f"  seed {it:11}: packets theo ngày: {dict(sorted(byday.items()))}")

print()
print("=" * 100)
print("2. CROP MIX THEO NGÀY (plants cuối ngày, Majkel) — đọc từ daily.json")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    daily = json.load(open(f"{mdir}/daily.json"))
    rows = [r for r in daily if r["player"] == midx]
    marks = {}
    for r in rows:
        if r["day"] in (0, 2, 5, 8, 10, 14, 18, 22, 25, 28, 29):
            pl = r.get("plants", {})
            marks[r["day"]] = "+".join(f"{k[:3]}{v}" for k, v in pl.items()) or "-"
    print(f"  {key}: " + " | ".join(f"d{d}:{marks[d]}" for d in sorted(marks)))

print()
print("=" * 100)
print("3. IDLE CASH THEO PHA (money cuối ngày — Majkel; min/avg/max theo pha)")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    daily = json.load(open(f"{mdir}/daily.json"))
    rows = [r for r in daily if r["player"] == midx]
    phases = {"d0-9": [], "d10-19": [], "d20-26": [], "d27-29": []}
    for r in rows:
        ph = "d0-9" if r["day"] <= 9 else "d10-19" if r["day"] <= 19 else "d20-26" if r["day"] <= 26 else "d27-29"
        phases[ph].append(r["money_end"])
    out = []
    for ph, v in phases.items():
        if v: out.append(f"{ph}:{min(v):.0f}/{sum(v)/len(v):.0f}/{max(v):.0f}")
    print(f"  {key}: " + "  ".join(out))

print()
print("=" * 100)
print("4. CONCENTRATION DOANH THU — top-5 lệnh bán chiếm bao nhiêu % revenue (Majkel vs OPP)")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    for p, tag in [(midx, "M"), (1 - midx, "O")]:
        sells = sorted([o for o in ords if o["player"] == p and o["op"] == "SELL" and o["units"] > 0],
                       key=lambda o: -o["cash"])
        tot = sum(s["cash"] for s in sells)
        top5 = sum(s["cash"] for s in sells[:5])
        top10 = sum(s["cash"] for s in sells[:10])
        print(f"  {key} {tag}: revenue ${tot:.0f}, top5 {100*top5/tot:.1f}%, top10 {100*top10/tot:.1f}%, n={len(sells)}")

print()
print("=" * 100)
print("5. ENDGAME ANCHOR — bán ở 5 step cuối (s715-719), Majkel vs OPP (5 trận mới)")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    for p, tag in [(midx, "M"), (1 - midx, "O")]:
        tail = [o for o in ords if o["player"] == p and o["op"] == "SELL" and o["step"] >= 715 and o["units"] > 0]
        if tail:
            s = " + ".join(f"s{o['step']}:{o['item'][:3]}×{o['units']}@{o['cash']/o['units']:.0f}=${o['cash']:.0f}" for o in tail)
            tot = sum(o["cash"] for o in tail)
            print(f"  {key} {tag} (5s cuối ${tot:.0f}): {s}")
        else:
            print(f"  {key} {tag}: (không bán ở 5s cuối)")

print()
print("=" * 100)
print("6. MUA WHEAT LÀM FEED — giá khi mua vs giá TB (Majkel)")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    ords = json.load(open(f"{mdir}/orders.json"))
    wb = [o for o in ords if o["player"] == midx and o["op"] == "BUY_PRODUCT" and o["item"] == "WHEAT" and o["units"] > 0]
    mkt = json.load(open(f"{mdir}/market.json"))
    wp = [m["prices"]["WHEAT"] for m in mkt]
    if wb:
        n = sum(o["units"] for o in wb)
        avg = sum(-o["cash"] for o in wb) / n
        pct = 100 * sum(1 for m in mkt if m["prices"]["WHEAT"] <= avg) / len(mkt)
        days = sorted(set(o["day"] for o in wb))
        print(f"  {key}: {n}u @ avg {avg:.1f} (percentile giá trận {pct:.0f}%), ngày {days[0]}-{days[-1]}")
    else:
        print(f"  {key}: không mua WHEAT")

print()
print("=" * 100)
print("7. FEED/CARE kỷ luật — số lệnh FEED & CARE từng bên (đếm từ timeline unit_verbs)")
print("=" * 100)
for key, (mdir, midx) in MATCHES.items():
    tl = json.load(open(f"{mdir}/timeline.json"))
    tot = {0: defaultdict(int), 1: defaultdict(int)}
    for r in tl:
        for v, n in r.get("unit_verbs", {}).items():
            tot[r["player"]][v] += n
    m, o = tot[midx], tot[1 - midx]
    print(f"  {key}: M FEED={m.get('FEED',0)} CARE={m.get('CARE',0)} COLLECT_FERT={m.get('COLLECT_FERTILIZER',0)} | O FEED={o.get('FEED',0)} CARE={o.get('CARE',0)} COLLECT_FERT={o.get('COLLECT_FERTILIZER',0)}")
