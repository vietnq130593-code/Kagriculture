#!/usr/bin/env python3
"""Follow-up queries for Task 83 review."""
import json
from collections import defaultdict

BASE = "/home/z/my-project/kaggle-research/top1"
def load(m, f): return json.load(open(f"{BASE}/{m}/{f}"))
D = {m: {(r["day"], r["player"]): r for r in load(m, "daily.json")} for m in ("match1", "match2")}
O = {m: load(m, "orders.json") for m in ("match1", "match2")}
T = {m: {(r["step"], r["player"]): r for r in load(m, "timeline.json")} for m in ("match1", "match2")}
MK = {m: load(m, "market.json") for m in ("match1", "match2")}

print("== M2: animals trajectory d16-29 (both) ==")
for p, nm in [(0, "M"), (1, "D")]:
    for d in range(16, 30):
        print(f"  {nm} d{d}: {D['match2'][(d,p)]['animals']} FEED={D['match2'][(d,p)]['verbs'].get('FEED',0)}")

print("== M2: Majkel money s148-151 + land ==")
for s in range(148, 152):
    print(f"  s{s}: money={T['match2'][(s,0)]['money']:.0f}")

print("== M2: Majkel shed STRA by day (max in day) ==")
for d in range(16, 30):
    mx = max(T['match2'][(s,0)]["shed"]["STRAWBERRY"] for s in range(d*24, d*24+24))
    print(f"  d{d}: shedSTRA_max={mx}")

print("== M2: STRA price min/max + inv by day (d13-29) ==")
mk = MK["match2"]
for d in range(13, 30):
    ps = [mk[s]["prices"]["STRAWBERRY"] for s in range(d*24, d*24+24)]
    iv = [mk[s]["inventory"]["STRAWBERRY"] for s in range(d*24, d*24+24)]
    print(f"  d{d}: price {min(ps):.0f}..{max(ps):.0f} inv {min(iv)}..{max(iv)}")

print("== M2: hands_max by day (both, d0-29) ==")
for p, nm in [(0, "M"), (1, "D")]:
    hs = [D['match2'][(d,p)]["hands_max"] for d in range(30)]
    print(f"  {nm}: {hs}")

print("== M2: MILK sells Majkel by day ==")
mm = defaultdict(lambda: [0, 0.0])
for o in O["match2"]:
    if o["op"] == "SELL" and o["item"] == "MILK" and o["player"] == 0 and o["units"] > 0:
        mm[o["day"]][0] += o["units"]; mm[o["day"]][1] += o["cash"]
print("  " + " ".join(f"d{d}:{v[0]}u@{v[1]/v[0]:.0f}" for d, v in sorted(mm.items())))

print("== M2: WHEAT price range by day (feed-lift claim 25→42 d12) ==")
for d in [0, 3, 6, 9, 12, 15]:
    ps = [mk[s]["prices"]["WHEAT"] for s in range(d*24, d*24+24)]
    print(f"  d{d}: {min(ps):.0f}..{max(ps):.0f}")

print("== M2: s408 Majkel orders (boundary-step profit check) ==")
net = sum(o["cash"] for o in O["match2"] if o["step"] == 408 and o["player"] == 0)
print(f"  net cash s408 p0 = {net:.0f} (expect +1160)")

print("== M1: land orders ==")
for o in O["match1"]:
    if o["op"] == "BUY_LAND":
        print(f"  p{o['player']} s{o['step']} d{o['day']} units={o['units']} cash={o['cash']:.0f}")

print("== M1: weeds end-of-day trajectory (both) ==")
for p, nm in [(0, "ymg"), (1, "maj")]:
    wz = [(d, D['match1'][(d,p)]["weeds"]) for d in range(30) if D['match1'][(d,p)]["weeds"] > 0]
    print(f"  {nm}: {wz} | final s719: {T['match1'][(719,p)]['weeds']}")

print("== M1: ymg hands_max all days ==")
print("  ymg:", [D['match1'][(d,0)]["hands_max"] for d in range(30)])
print("  maj:", [D['match1'][(d,1)]["hands_max"] for d in range(30)])

print("== M1: maj shed STRA d22-25 (giữ 29 STRA claim) ==")
for d in range(21, 26):
    mx = max(T['match1'][(s,1)]["shed"]["STRAWBERRY"] for s in range(d*24, d*24+24))
    print(f"  d{d}: maj shedSTRA_max={mx}")

print("== M1: s705-712 gap trace ==")
for s in range(705, 713):
    y = T['match1'][(s,0)]["money"]; m = T['match1'][(s,1)]["money"]
    print(f"  s{s}: ymg={y:.0f} maj={m:.0f} gap(maj-ymg)={m-y:.0f}")

print("== M1: MELON sells by day (both) ==")
for p, nm in [(0, "ymg"), (1, "maj")]:
    mm = defaultdict(lambda: [0, 0.0])
    for o in O["match1"]:
        if o["op"] == "SELL" and o["item"] == "MELON" and o["player"] == p and o["units"] > 0:
            mm[o["day"]][0] += o["units"]; mm[o["day"]][1] += o["cash"]
    print(f"  {nm}: " + " ".join(f"d{d}:{v[0]}u@{v[1]/v[0]:.0f}" for d, v in sorted(mm.items())))

print("== M1: MILK/WOOL sells by day (both) ==")
for p, nm in [(0, "ymg"), (1, "maj")]:
    for item in ("MILK", "WOOL"):
        mm = defaultdict(lambda: [0, 0.0])
        for o in O["match1"]:
            if o["op"] == "SELL" and o["item"] == item and o["player"] == p and o["units"] > 0:
                mm[o["day"]][0] += o["units"]; mm[o["day"]][1] += o["cash"]
        print(f"  {nm} {item}: " + " ".join(f"d{d}:{v[0]}u@{v[1]/v[0]:.0f}" for d, v in sorted(mm.items())))

print("== M1: FEED/FERTILIZE verbs totals + BUY_PRODUCT/BUY_FERTILIZER ==")
for p, nm in [(0, "ymg"), (1, "maj")]:
    feed = sum(D['match1'][(d,p)]["verbs"].get("FEED", 0) for d in range(30))
    fert = sum(D['match1'][(d,p)]["verbs"].get("FERTILIZE", 0) for d in range(30))
    bp = defaultdict(lambda: [0, 0.0])
    for o in O["match1"]:
        if o["op"] == "BUY_PRODUCT" and o["player"] == p and o["units"] > 0:
            bp[o["item"]][0] += o["units"]; bp[o["item"]][1] += o["cash"]
    print(f"  {nm}: FEED={feed} FERTILIZE={fert} BUY_PRODUCT={dict((k, v[0]) for k, v in bp.items())}")

print("== M2: FERTILIZER sell prices over time (99→29 claim) ==")
fs = [o for o in O["match2"] if o["op"] == "SELL" and o["item"] == "FERTILIZER" and o["player"] == 0 and o["units"] > 0]
print(f"  first: d{fs[0]['day']} @{fs[0]['prices'][0]:.0f}; last: d{fs[-1]['day']} @{fs[-1]['prices'][-1]:.0f}; n={len(fs)}")

print("== M2: CARROT price range d12-29 (41→55 claim) ==")
for d in [12, 16, 20, 24, 28, 29]:
    ps = [mk[s]["prices"]["CARROT"] for s in range(d*24, d*24+24)]
    print(f"  d{d}: {min(ps):.0f}..{max(ps):.0f}")

print("== M1: EGG price range d9-29 (flat ~base claim) ==")
mk1 = MK["match1"]
for d in [9, 12, 15, 18, 21, 24, 27, 29]:
    ps = [mk1[s]["prices"]["EGG"] for s in range(d*24, d*24+24)]
    print(f"  d{d}: {min(ps):.0f}..{max(ps):.0f}")

print("== M2: crop mix spot check d28-29 plants (§4.3) ==")
for d in [28, 29]:
    print(f"  d{d}: M={D['match2'][(d,0)]['plants']} D={D['match2'][(d,1)]['plants']}")

print("== M1: crop mix spot check d28-29 (§4) ==")
for d in [28, 29]:
    print(f"  d{d}: ymg={D['match1'][(d,0)]['plants']} maj={D['match1'][(d,1)]['plants']}")

print("== M2: Majkel d29 full order log (verify §10) ==")
for o in O["match2"]:
    if o["day"] == 29 and o["player"] == 0 and o["units"] > 0 and o["op"] == "SELL":
        print(f"  s{o['step']} {o['item']} {o['units']}u ${o['cash']:.0f}")

print("== M2: WOOL d6 s148 DSM context (§8 #2 says M 18u; D also sold) ==")
w6 = [o for o in O["match2"] if o["op"] == "SELL" and o["item"] == "WOOL" and o["day"] == 6 and o["units"] > 0]
for o in w6:
    print(f"  p{o['player']} s{o['step']} {o['units']}u ${o['cash']:.0f} first@{o['prices'][0]:.0f} last@{o['prices'][-1]:.0f}")
