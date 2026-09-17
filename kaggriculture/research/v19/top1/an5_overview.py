#!/usr/bin/env python3
"""Stage 1: overview của 7 trận Majkel — spend/revenue/land/animals/hires/breadth."""
import json, os
from collections import defaultdict

MATCHES = {
    "m1": ("match1", 1), "m2": ("match2", 0), "m3": ("match3", 1),
    "m4": ("match4", 1), "m5": ("match5", 1), "m6": ("match6", 1), "m7": ("match7", 1),
}

rows = []
detail = {}
for key, (mdir, midx) in MATCHES.items():
    s = json.load(open(f"{mdir}/summary.json"))
    tl = json.load(open(f"{mdir}/timeline.json"))
    ords = json.load(open(f"{mdir}/orders.json"))
    daily = json.load(open(f"{mdir}/daily.json"))
    oidx = 1 - midx
    mname, oname = s["teams"][midx], s["teams"][oidx]

    def agg(p):
        rev = defaultdict(float); units = defaultdict(int)
        for o in ords:
            if o["player"] != p or o["op"] != "SELL" or o["units"] <= 0: continue
            rev[o["item"]] += o["cash"]; units[o["item"]] += o["units"]
        return rev, units

    mrev, munits = agg(midx); orev, ounits = agg(oidx)

    # animals bought & final
    an = defaultdict(int)
    for o in ords:
        if o["player"] == midx and o["op"] == "BUY_ANIMAL": an[o["item"]] += o["units"]
    # land buys
    land_m = [o for o in ords if o["player"] == midx and o["op"] == "BUY_LAND"]
    land_o = [o for o in ords if o["player"] == oidx and o["op"] == "BUY_LAND"]
    # final plants/animals from last timeline row
    lastm = [r for r in tl if r["player"] == midx][-1]
    lasto = [r for r in tl if r["player"] == oidx][-1]
    # endgame: sells step>=696 (d29)
    end_m = sum(o["cash"] for o in ords if o["player"]==midx and o["op"]=="SELL" and o["day"]>=29)
    end_o = sum(o["cash"] for o in ords if o["player"]==oidx and o["op"]=="SELL" and o["day"]>=29)
    # last-3-days revenue d27-29
    l3_m = sum(o["cash"] for o in ords if o["player"]==midx and o["op"]=="SELL" and o["day"]>=27)
    l3_o = sum(o["cash"] for o in ords if o["player"]==oidx and o["op"]=="SELL" and o["day"]>=27)
    p = s["p%d" % midx]; q = s["p%d" % oidx]
    rows.append({
        "key": key, "m": mname[:10], "o": oname[:10],
        "win": s["winner"] == midx, "margin": (s["final_money"][midx] - s["final_money"][oidx]),
        "M$": s["final_money"][midx], "O$": s["final_money"][oidx],
        "Mrev": p["revenue"], "Orev": q["revenue"],
        "Mhire": p["hire_spend"], "Ohire": q["hire_spend"],
        "Mland": p["land_spend"], "Oland": q["land_spend"],
        "Mseed": p["seed_spend"], "Oseed": q["seed_spend"],
        "Manimal": p["animal_spend"], "Oanimal": q["animal_spend"],
        "Mprod": p.get("product_spend", 0), "Oprod": q.get("product_spend", 0),
        "Mland_n": len(land_m), "Oland_n": len(land_o),
        "Mend29": end_m, "Oend29": end_o, "Ml3": l3_m, "Ol3": l3_o,
        "Mitems": len(mrev), "Oitems": len(orev),
    })
    detail[key] = {
        "mrev": dict(mrev), "orev": dict(orev), "munits": dict(munits), "ounits": dict(ounits),
        "animals_bought": dict(an),
        "m_final_animals": lastm["animals"], "o_final_animals": lasto["animals"],
        "m_final_plants": lastm["plants"], "o_final_plants": lasto["plants"],
        "seed": s["seed"], "midx": midx,
    }

# ---- print overview table ----
print("=" * 110)
print("OVERVIEW 7 TRẬN MAJKEL1337 (M=Majkel, O=đối thủ)")
print("=" * 110)
hdr = f"{'key':4} {'opp':11} {'KQ':3} {'margin':>8} {'M$':>7} {'O$':>7} {'Mrev':>7} {'Orev':>7} {'Mhire':>6} {'Ohire':>6} {'Mland':>6} {'Oland':>6} {'Manim':>6} {'Oanim':>6} {'Mseed':>6} {'Oseed':>6} {'Mend29':>7} {'Oend29':>7} {'Ml3':>7} {'Ol3':>7}"
print(hdr)
for r in rows:
    print(f"{r['key']:4} {r['o']:11} {'W' if r['win'] else 'L':3} {r['margin']:>8.0f} {r['M$']:>7.0f} {r['O$']:>7.0f} {r['Mrev']:>7.0f} {r['Orev']:>7.0f} {r['Mhire']:>6.0f} {r['Ohire']:>6.0f} {r['Mland']:>6.0f} {r['Oland']:>6.0f} {r['Manimal']:>6.0f} {r['Oanimal']:>6.0f} {r['Mseed']:>6.0f} {r['Oseed']:>6.0f} {r['Mend29']:>7.0f} {r['Oend29']:>7.0f} {r['Ml3']:>7.0f} {r['Ol3']:>7.0f}")

print()
print("--- Per-match detail ---")
for key, d in detail.items():
    print(f"\n### {key} (seed {d['seed']}, Majkel=p{d['midx']})")
    print("  Majkel revenue:", {k: round(v) for k, v in sorted(d["mrev"].items(), key=lambda x: -x[1])})
    print("  Opp    revenue:", {k: round(v) for k, v in sorted(d["orev"].items(), key=lambda x: -x[1])})
    print("  Majkel animals bought:", d["animals_bought"], "final:", d["m_final_animals"])
    print("  Opp    final animals:", d["o_final_animals"])
    print("  Majkel final plants:", d["m_final_plants"])
    print("  Opp    final plants:", d["o_final_plants"])

# ---- aggregates ----
wins = [r for r in rows if r["win"]]; losses = [r for r in rows if not r["win"]]
print("\n" + "=" * 110)
print(f"AGGREGATE: {len(wins)}W/{len(losses)}L")
for label, grp in [("WINS", wins), ("LOSSES", losses)]:
    if not grp: continue
    n = len(grp)
    print(f"\n{label} ({n} trận) — mean Majkel vs Opp:")
    for f in ["Mrev", "Orev", "Mhire", "Ohire", "Mland", "Oland", "Manimal", "Oanimal", "Mseed", "Oseed", "Mprod", "Oprod", "Mend29", "Oend29", "Ml3", "Ol3"]:
        print(f"  {f:>7}: {sum(r[f] for r in grp)/n:>8.0f}", end="")
    print()

# revenue share per item across 7 matches (Majkel vs all opponents)
mrev_tot = defaultdict(float); orev_tot = defaultdict(float)
for key, d in detail.items():
    for k, v in d["mrev"].items(): mrev_tot[k] += v
    for k, v in d["orev"].items(): orev_tot[k] += v
mt = sum(mrev_tot.values()); ot = sum(orev_tot.values())
print(f"\nRevenue mix (Majkel ${mt:.0f} vs Opp ${ot:.0f} — 7 trận):")
for k in sorted(set(mrev_tot) | set(orev_tot), key=lambda k: -(mrev_tot[k] + orev_tot[k])):
    print(f"  {k:11} M: {mrev_tot[k]:>8.0f} ({100*mrev_tot[k]/mt:>4.1f}%)   O: {orev_tot[k]:>8.0f} ({100*orev_tot[k]/ot:>4.1f}%)")

json.dump({"rows": rows, "detail": {k: {kk: vv for kk, vv in v.items()} for k, v in detail.items()}},
          open("an5_overview.json", "w"), indent=1, default=str)
print("\nsaved an5_overview.json")
