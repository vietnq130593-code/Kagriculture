#!/usr/bin/env python3
"""Final batch of verification queries (Task 83)."""
import json
from collections import defaultdict

BASE = "/home/z/my-project/kaggle-research/top1"
def load(m, f): return json.load(open(f"{BASE}/{m}/{f}"))
D = {m: {(r["day"], r["player"]): r for r in load(m, "daily.json")} for m in ("match1", "match2")}
O = {m: load(m, "orders.json") for m in ("match1", "match2")}
T = {m: {(r["step"], r["player"]): r for r in load(m, "timeline.json")} for m in ("match1", "match2")}
MK = {m: load(m, "market.json") for m in ("match1", "match2")}

print("== M1: maj (p1) d0 ALL orders ==")
for o in O["match1"]:
    if o["day"] == 0 and o["player"] == 1:
        print(f"  s{o['step']} {o['op']} {o['item']} asked={o['asked']} units={o['units']} cash={o['cash']:.0f}")

print("== M1: ymg WHEAT sells by day d3-6 ==")
mm = defaultdict(lambda: [0, 0.0])
for o in O["match1"]:
    if o["op"] == "SELL" and o["item"] == "WHEAT" and o["player"] == 0 and o["units"] > 0 and o["day"] <= 6:
        mm[o["day"]][0] += o["units"]; mm[o["day"]][1] += o["cash"]
print("  " + " ".join(f"d{d}:{v[0]}u/${v[1]:.0f}@{v[1]/v[0]:.1f}" for d, v in sorted(mm.items())))

print("== M1: FERT sells d0-3 by player ==")
for p, nm in [(0, "ymg"), (1, "maj")]:
    mm = defaultdict(lambda: [0, 0.0])
    for o in O["match1"]:
        if o["op"] == "SELL" and o["item"] == "FERTILIZER" and o["player"] == p and o["units"] > 0 and o["day"] <= 3:
            mm[o["day"]][0] += o["units"]; mm[o["day"]][1] += o["cash"]
    print(f"  {nm}: " + " ".join(f"d{d}:{v[0]}u/${v[1]:.0f}" for d, v in sorted(mm.items())))

print("== M1: ymg shed_total END of day (s=d*24+23) d24-28 ==")
for d in range(24, 29):
    print(f"  d{d} end: ymg={T['match1'][(d*24+23,0)]['shed_total']} maj={T['match1'][(d*24+23,1)]['shed_total']}")
print(f"  maj s695 shed_total = {T['match1'][(695,1)]['shed_total']} (claim 12)")
print(f"  ymg s695 shed_total = {T['match1'][(695,0)]['shed_total']}")

print("== M2: Majkel dead orders by op (19 breakdown) ==")
dd = defaultdict(int)
for o in O["match2"]:
    if o["player"] == 0 and o["units"] == 0 and o["cash"] == 0:
        dd[o["op"]] += 1
print(f"  {dict(dd)}")
dead = [o for o in O["match2"] if o["player"] == 0 and o["units"] == 0 and o["cash"] == 0]
print("  details: " + "; ".join(f"s{o['step']} {o['op']} {o['item']}" for o in dead))

print("== M2: M hire_spend by day + hands ==")
for d in range(10):
    print(f"  d{d}: hire=${D['match2'][(d,0)]['hire_spend']:.0f} hands_max={D['match2'][(d,0)]['hands_max']}")

print("== M2: M FERTILIZE verbs total (162 claim) ==")
print(f"  M FERTILIZE={sum(D['match2'][(d,0)]['verbs'].get('FERTILIZE',0) for d in range(30))} D={sum(D['match2'][(d,1)]['verbs'].get('FERTILIZE',0) for d in range(30))}")

print("== M2: M money min during d6 ==")
print(f"  min d6 = {min(T['match2'][(s,0)]['money'] for s in range(144,168)):.0f}")

print("== M2: s695 shed_total (claims: M 50, D 28) ==")
print(f"  M s695 = {T['match2'][(695,0)]['shed_total']} D s695 = {T['match2'][(695,1)]['shed_total']}")
print(f"  M s695 shed: " + ", ".join(f"{k}={v}" for k, v in T['match2'][(695,0)]['shed'].items() if v))
print(f"  D s695 shed: " + ", ".join(f"{k}={v}" for k, v in T['match2'][(695,1)]['shed'].items() if v))

print("== M2: MELON price d10 (270→226 claim) ==")
ps = [(s, MK['match2'][s]['prices']['MELON']) for s in range(240, 264)]
print(f"  {ps[:6]} ... {ps[-3:]}")

print("== M2: Majkel STRA sell rows d13-17 (§6.2 table) ==")
for o in O["match2"]:
    if o["op"] == "SELL" and o["item"] == "STRAWBERRY" and o["player"] == 0 and o["units"] > 0 and 13 <= o["day"] <= 17:
        print(f"  d{o['day']} s{o['step']} {o['units']}u ${o['cash']:.0f} @{o['cash']/o['units']:.0f}")

print("== M2: DSM STRA d19-24 sells (72u @102.3 claim) ==")
du = sum(o["units"] for o in O["match2"] if o["op"]=="SELL" and o["item"]=="STRAWBERRY" and o["player"]==1 and 19<=o["day"]<=24 and o["units"]>0)
dc = sum(o["cash"] for o in O["match2"] if o["op"]=="SELL" and o["item"]=="STRAWBERRY" and o["player"]==1 and 19<=o["day"]<=24 and o["units"]>0)
print(f"  DSM d19-24: {du}u ${dc:.0f} @{dc/du:.1f}")

print("== M1: ymg d5 revenue events (68u/$2,614 claim) ==")
mm = defaultdict(lambda: [0, 0.0])
for o in O["match1"]:
    if o["op"] == "SELL" and o["player"] == 0 and o["units"] > 0 and o["day"] in (4, 5):
        mm[(o["day"], o["item"])][0] += o["units"]; mm[(o["day"], o["item"])][1] += o["cash"]
print("  " + "; ".join(f"{k}:{v[0]}u/${v[1]:.0f}" for k, v in sorted(mm.items())))

print("== M1: FERTILIZE đỉnh/ngày + d28 (claim: ymg 208 tổng, d28 bón 24) ==")
for p, nm in [(0, "ymg"), (1, "maj")]:
    fz = [(d, D['match1'][(d,p)]["verbs"].get("FERTILIZE",0)) for d in range(30) if D['match1'][(d,p)]["verbs"].get("FERTILIZE",0)]
    print(f"  {nm}: max={max(v for _,v in fz)} d28={dict(fz).get(28,0)}")
    ff = [(d, D['match1'][(d,p)]["verbs"].get("FEED",0)) for d in range(30) if D['match1'][(d,p)]["verbs"].get("FEED",0)]
    print(f"  {nm} FEED max/day={max(v for _,v in ff)}")
