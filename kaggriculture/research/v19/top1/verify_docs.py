#!/usr/bin/env python3
"""Verify numeric claims in 04A/04B/05/README against parsed match data (Task 83 review)."""
import json, sys
from collections import defaultdict

BASE = "/home/z/my-project/kaggle-research/top1"
OUT = []

def log(s=""):
    OUT.append(s)
    print(s)

def load(m, f):
    return json.load(open(f"{BASE}/{m}/{f}"))

def daily_map(m):
    """(day, player) -> record"""
    return {(r["day"], r["player"]): r for r in load(m, "daily.json")}

def orders(m):
    return load(m, "orders.json")

def timeline(m):
    """(step, player) -> record"""
    return {(r["step"], r["player"]): r for r in load(m, "timeline.json")}

def market(m):
    return load(m, "market.json")

def check(label, actual, expect, tol=1.0):
    ok = abs(actual - expect) <= tol
    log(f"{'PASS' if ok else 'FAIL'} | {label}: actual={actual} expect={expect}")
    return ok

def eq(label, actual, expect):
    ok = actual == expect
    log(f"{'PASS' if ok else 'FAIL'} | {label}: actual={actual} expect={expect}")
    return ok

# ============ MATCH2 (04A) ============
log("=" * 70)
log("MATCH2 — Majkel(p0) vs DSM(p1) — 04A claims")
log("=" * 70)
D2 = daily_map("match2")
O2 = orders("match2")
T2 = timeline("match2")

# --- 04A §1.1 money curve: money_end & delta ---
doc_money_m = {0:5,1:59,2:16,3:180,4:357,5:724,6:49,7:11,8:700,9:341,10:6950,11:12026,12:20619,13:23139,14:28070,15:32969,16:36180,17:40655,18:46070,19:47841,20:49564,21:51151,22:54155,23:56612,24:59164,25:62928,26:67572,27:71227,28:78413,29:91845}
doc_money_d = {0:5,1:59,2:16,3:102,4:410,5:746,6:10,7:72,8:1139,9:635,10:5305,11:11626,12:20766,13:23553,14:29945,15:34097,16:37738,17:41053,18:45223,19:47254,20:50528,21:52335,22:54234,23:56927,24:59692,25:62679,26:66327,27:71417,28:77329,29:84129}
doc_delta_m = {0:-2995,1:54,2:-43,3:164,4:177,5:367,6:-675,7:-38,8:689,9:-359,10:6609,11:5076,12:8593,13:2520,14:4931,15:4899,16:3211,17:3315,18:4753,19:1771,20:1723,21:1585,22:2711,23:2457,24:2200,25:3116,26:3598,27:3030,28:5788,29:13431}
doc_delta_d = {0:-2995,1:54,2:-43,3:86,4:308,5:336,6:-736,7:62,8:1067,9:-504,10:4670,11:5607,12:9140,13:2787,14:6392,15:4152,16:3641,17:3315,18:4170,19:2031,20:3167,21:1807,22:1899,23:2639,24:2765,25:2933,26:3648,27:5090,28:5907,29:6325}
log("\n-- §1.1 money_end (doc vs data) --")
bad = []
for d in range(30):
    for p, doc, name in [(0, doc_money_m, "M"), (1, doc_money_d, "D")]:
        act = D2[(d, p)]["money_end"]
        if abs(act - doc[d]) > 0.5:
            bad.append(f"d{d} {name}: doc={doc[d]} data={act}")
log(("MONEY_END MISMATCH: " + "; ".join(bad)) if bad else "PASS | all 60 money_end match")
log("\n-- §1.1 delta column (doc Δ vs money_end diff) --")
prev = {0: 3000.0, 1: 3000.0}
bad_doc, bad_data = [], []
for d in range(30):
    for p, docd, name in [(0, doc_delta_m, "M"), (1, doc_delta_d, "D")]:
        act = D2[(d, p)]["money_end"] - prev[p]
        if abs(act - docd[d]) > 0.5:
            bad_doc.append(f"d{d}{name}: docΔ={docd[d]} correctΔ={act:.0f}")
        pd_doc = D2[(d, p)]["profit_day"]
        if abs(pd_doc - act) > 0.5:
            bad_data.append(f"d{d}{name}: profit_day={pd_doc} moneyΔ={act:.0f}")
        prev[p] = D2[(d, p)]["money_end"]
log("DOC Δ ERRORS: " + "; ".join(bad_doc) if bad_doc else "PASS | doc Δ column all correct")
log("DAILY.JSON profit_day vs moneyΔ: " + ("; ".join(bad_data) if bad_data else "PASS | profit_day consistent"))

# --- 04A §1.2 phase revenue/spend ---
log("\n-- §1.2 phase table (rev/spend/net) --")
phases = [("d0-2", 0, 2, 1094, 4078, 1122, 4106), ("d3-9", 3, 9, 12190, 11865, 12474, 11855),
          ("d10-20", 10, 20, 57036, 7813, 59193, 9300), ("d21-28", 21, 28, 34278, 5429, 30305, 3504),
          ("d29", 29, 29, 13575, 143, 6943, 143)]
for name, d1, d2, mr, ms, dr, ds in phases:
    for p, erv, esp, nm in [(0, mr, ms, "M"), (1, dr, ds, "D")]:
        rv = sum(sum(v["cash"] for v in D2[(d, p)]["sells"].values()) for d in range(d1, d2 + 1))
        sp = -(sum(sum(v["cash"] for v in D2[(d, p)]["buys"].values()) for d in range(d1, d2 + 1))
               + sum(D2[(d, p)]["hire_spend"] + D2[(d, p)]["land_spend"] for d in range(d1, d2 + 1)))
        log(f"{'PASS' if abs(rv-erv)<2 and abs(sp-esp)<2 else 'FAIL'} | phase {name} {nm}: rev={rv:.0f} (doc {erv}) spend={sp:.0f} (doc {esp})")

# --- 04A §3.1 spend by category ---
log("\n-- §3.1 spend categories --")
seed_items = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
seed_spend = {0: defaultdict(float), 1: defaultdict(float)}
seed_units = {0: defaultdict(int), 1: defaultdict(int)}
animal_spend = {0: 0.0, 1: 0.0}
feed_spend = {0: 0.0, 1: 0.0}
feed_units = {0: 0, 1: 0}
for o in O2:
    if o["op"] == "BUY_SEED":
        seed_spend[o["player"]][o["item"]] += -o["cash"]
        seed_units[o["player"]][o["item"]] += o["units"]
    elif o["op"] == "BUY_ANIMAL":
        animal_spend[o["player"]] += -o["cash"]
    elif o["op"] == "BUY_PRODUCT":
        feed_spend[o["player"]] += -o["cash"]
        feed_units[o["player"]] += o["units"]
for p, nm in [(0, "M"), (1, "D")]:
    log(f"INFO | {nm} seeds: " + ", ".join(f"{k}={seed_units[p][k]}u/${seed_spend[p][k]:.0f}" for k in seed_items if seed_units[p][k]))
    check(f"{nm} animal_spend", animal_spend[p], 7000)
    check(f"{nm} product(feed) spend", feed_spend[p], 6507 if p == 0 else 6449)
    check(f"{nm} product(feed) units", feed_units[p], 178 if p == 0 else 172)

# --- 04A §6.1 revenue per item ---
log("\n-- §6.1 per-item revenue --")
rev = {0: defaultdict(lambda: [0, 0.0]), 1: defaultdict(lambda: [0, 0.0])}
for o in O2:
    if o["op"] == "SELL" and o["units"] > 0:
        rev[o["player"]][o["item"]][0] += o["units"]
        rev[o["player"]][o["item"]][1] += o["cash"]
doc612 = {("M", "STRAWBERRY"): (196, 152.3, 5475), ("M", "WOOL"): (196, 94.3, 144), ("M", "CARROT"): (310, 51.8, 7200),
          ("M", "WHEAT"): (390, 37.3, -2569), ("M", "MELON"): (72, 199.7, -126), ("M", "FERTILIZER"): (179, 64.3, 46),
          ("M", "TOMATO"): (108, 82.5, -2031), ("M", "MILK"): (107, 41.5, -3),
          ("D", "STRAWBERRY"): (175, 139.3, None), ("D", "WOOL"): (215, 85.3, None), ("D", "CARROT"): (170, 52.2, None),
          ("D", "WHEAT"): (455, 37.6, None), ("D", "MELON"): (72, 201.4, None), ("D", "FERTILIZER"): (177, 64.8, None),
          ("D", "TOMATO"): (135, 81.1, None), ("D", "MILK"): (93, 47.8, None)}
for (side, item), (u, avg, dd) in doc612.items():
    p = 0 if side == "M" else 1
    au, ac = rev[p][item]
    aavg = ac / au if au else 0
    log(f"{'PASS' if au == u and abs(aavg - avg) < 0.15 else 'FAIL'} | 6.1 {side} {item}: units={au} (doc {u}) avg={aavg:.1f} (doc {avg})")
dM = sum(rev[0][i][1] for i in rev[0]); dD = sum(rev[1][i][1] for i in rev[1])
log(f"INFO | Δrevenue M-D = {dM - dD:.0f} (doc +8,136)")
for item in rev[0]:
    dd = rev[0][item][1] - rev[1][item][1]
    docdd = dict(STRAWBERRY=5475, WOOL=144, CARROT=7200, WHEAT=-2569, MELON=-126, FERTILIZER=46, TOMATO=-2031, MILK=-3).get(item)
    if docdd is not None:
        log(f"{'PASS' if abs(dd - docdd) < 8 else 'FAIL'} | 6.1 Δ {item}: {dd:.0f} (doc {docdd})")

# --- 04A §6.2 throttle math ---
log("\n-- §6.2 STRA throttle math --")
stra = [o for o in O2 if o["op"] == "SELL" and o["item"] == "STRAWBERRY" and o["units"] > 0 and o["player"] == 0]
early = [o for o in stra if 19 <= o["day"] <= 24]
late = [o for o in stra if o["day"] >= 25]
eu = sum(o["units"] for o in early); ec = sum(o["cash"] for o in early)
lu = sum(o["units"] for o in late); lc = sum(o["cash"] for o in late)
log(f"INFO | M STRA d19-24: {eu}u ${ec:.0f} (doc 40 @102.6 → $4,104)")
log(f"INFO | M STRA d25-29: {lu}u ${lc:.0f} avg {lc/lu:.1f} (doc 77 @164.4)")
check("throttle total units (117)", eu + lu, 117)
alt = (eu + lu) * (ec / eu)
log(f"INFO | throttle gain = ({ec}+{lc:.0f}) - {eu + lu}u*{ec/eu:.1f} = {ec + lc - alt:.0f} (doc +4,757)")

# --- 04A §6.4 endgame d29 ---
log("\n-- §6.4 day29 --")
t696 = T2[(696, 0)]
log("INFO | M shed s696: " + ", ".join(f"{k}={v}" for k, v in t696["shed"].items() if v))
log("INFO | D shed s696: " + ", ".join(f"{k}={v}" for k, v in T2[(696, 1)]["shed"].items() if v))
s697 = [o for o in O2 if o["step"] == 697 and o["op"] == "SELL" and o["units"] > 0]
for o in s697:
    log(f"INFO | s697 SELL p{o['player']} {o['item']} {o['units']}u ${o['cash']:.0f} prices[:3]={o['prices'][:3]}")
s719 = [o for o in O2 if o["step"] == 719]
for o in s719:
    log(f"INFO | s719 p{o['player']} {o['op']} {o['item']} asked={o['asked']} units={o['units']} cash={o['cash']:.0f} prices[:3]={o['prices'][:3]}")
m719 = sum(o["cash"] for o in s719 if o["player"] == 0 and o["cash"] > 0)
d719 = sum(o["cash"] for o in s719 if o["player"] == 1 and o["cash"] > 0)
check("M s719 revenue", m719, 7542, 3)
check("D s719 revenue", d719, 1260, 3)
check("step719 margin", m719 - d719, 6283, 3)
d29u_m = sum(o["units"] for o in O2 if o["day"] == 29 and o["op"] == "SELL" and o["player"] == 0)
d29u_d = sum(o["units"] for o in O2 if o["day"] == 29 and o["op"] == "SELL" and o["player"] == 1)
check("M d29 sell units", d29u_m, 190)
check("D d29 sell units", d29u_d, 136)
d29r_m = sum(o["cash"] for o in O2 if o["day"] == 29 and o["op"] == "SELL" and o["player"] == 0)
d29r_d = sum(o["cash"] for o in O2 if o["day"] == 29 and o["op"] == "SELL" and o["player"] == 1)
check("M d29 revenue", d29r_m, 13575, 3)
check("D d29 revenue", d29r_d, 6943, 3)

# --- 04A §6.5 shed_total profile ---
log("\n-- §6.5 shed_total --")
for p, nm in [(0, "M"), (1, "D")]:
    st = {d: max(T2[(s, p)]["shed_total"] for s in range(d * 24, d * 24 + 24)) for d in range(30)}
    log(f"INFO | {nm} max shed_total per day: " + " ".join(f"{d}:{st[d]}" for d in [16, 18, 20, 21, 22, 24, 26, 27, 28, 29]))

# --- 04A §6.6 dead orders ---
log("\n-- §6.6 dead orders --")
for p, nm, td, te in [(0, "M", 987, 968), (1, "D", 3772, 1043)]:
    po = [o for o in O2 if o["player"] == p]
    dead = [o for o in po if o["units"] == 0 and o["cash"] == 0]
    eq(f"{nm} total orders", len(po), td)
    eq(f"{nm} executed", len(po) - len(dead), te)
    ds = defaultdict(int)
    for o in dead:
        if o["op"] == "SELL":
            ds[o["item"]] += 1
    log(f"INFO | {nm} dead-SELL by item: {dict(sorted(ds.items(), key=lambda x: -x[1]))}")

# --- 04A §8 key moments ---
log("\n-- §8 key moments --")
wool_d6 = [o for o in O2 if o["op"] == "SELL" and o["item"] == "WOOL" and o["day"] == 6 and o["units"] > 0]
log(f"INFO | d6 WOOL sells (both): " + "; ".join(f"p{o['player']} s{o['step']} {o['units']}u @{o['prices'][0]:.0f}-${o['prices'][-1]:.0f} ${o['cash']:.0f}" for o in wool_d6))
melon_d10 = [o for o in O2 if o["op"] == "SELL" and o["item"] == "MELON" and o["day"] == 10 and o["units"] > 0]
log(f"INFO | d10 MELON sells: " + "; ".join(f"p{o['player']} s{o['step']} {o['units']}u @{o['prices'][0]:.0f} ${o['cash']:.0f}" for o in melon_d10))
land = [o for o in O2 if o["op"] == "BUY_LAND"]
for o in land:
    log(f"INFO | LAND p{o['player']} s{o['step']} d{o['day']} units={o['units']} cash={o['cash']:.0f}")
wool_d12 = [o for o in O2 if o["op"] == "SELL" and o["item"] == "WOOL" and o["day"] == 12 and o["units"] > 0]
log(f"INFO | d12 WOOL sells: " + "; ".join(f"p{o['player']} s{o['step']} {o['units']}u @{o['prices'][0]:.0f} ${o['cash']:.0f}" for o in wool_d12))

# weeds per day
for p, nm in [(0, "M"), (1, "D")]:
    w = {d: D2[(d, p)]["weeds"] for d in range(30)}
    log(f"INFO | {nm} weeds by day (nonzero): " + ", ".join(f"d{d}:{v}" for d, v in w.items() if v))

# animals escape match2 endgame
for p, nm in [(0, "M"), (1, "D")]:
    an = {d: dict(D2[(d, p)]["animals"]) for d in range(26, 30)}
    log(f"INFO | {nm} animals d26-29: {an}")
    fd = {d: D2[(d, p)]["verbs"].get("FEED", 0) for d in range(26, 30)}
    log(f"INFO | {nm} FEED verbs d26-29: {fd}")

# PET_CAFE → carrot pivot timing
for p, nm in [(0, "M"), (1, "D")]:
    cd = [d for d in range(30) if D2[(d, p)]["buys"].get("CARROT", {}).get("units", 0) > 0]
    log(f"INFO | {nm} first CARROT seed-buy day: {cd[0] if cd else None}")

# ============ MATCH1 (04B) ============
log("\n" + "=" * 70)
log("MATCH1 — ymg_aq(p0) vs Majkel(p1) — 04B claims")
log("=" * 70)
D1 = daily_map("match1")
O1 = orders("match1")
T1 = timeline("match1")

# --- 04B §1 money curve ---
doc_ymg = {0:12,1:430,2:810,3:1150,4:82,5:732,6:2222,7:1951,8:2560,9:3388,10:5748,11:5635,12:5841,13:9250,14:13739,15:21785,16:29660,17:36122,18:45446,19:49819,20:51374,21:54347,22:58029,23:58931,24:61268,25:65174,26:68110,27:71469,28:76145,29:86713}
doc_maj = {0:7,1:3,2:43,3:73,4:149,5:505,6:20,7:19,8:2275,9:374,10:6487,11:11876,12:13532,13:13837,14:25612,15:29796,16:36684,17:41153,18:48207,19:51248,20:54367,21:56847,22:58598,23:59918,24:62786,25:65998,26:69047,27:73091,28:79264,29:86262}
doc_p_ymg = {0:-2988,1:418,2:380,3:340,4:-1068,5:650,6:1401,7:-271,8:441,9:793,10:2066,11:-113,12:-140,13:3279,14:4365,15:8046,16:7875,17:6462,18:9324,19:4373,20:1461,21:2973,22:3682,23:902,24:2337,25:3856,26:2936,27:3323,28:4676,29:10568}
doc_p_maj = {0:-2993,1:-4,2:40,3:30,4:76,5:356,6:-485,7:-1,8:2256,9:-1901,10:6113,11:5389,12:1656,13:305,14:7167,15:4184,16:6888,17:4469,18:7054,19:3041,20:3119,21:2480,22:1751,23:1318,24:2326,25:3210,26:3035,27:4044,28:6162,29:6998}
log("\n-- §1 money_end + profit --")
bad = []
for d in range(30):
    for p, doc, name in [(0, doc_ymg, "ymg"), (1, doc_maj, "maj")]:
        act = D1[(d, p)]["money_end"]
        if abs(act - doc[d]) > 0.5:
            bad.append(f"d{d} {name}: doc={doc[d]} data={act}")
log(("MONEY_END MISMATCH: " + "; ".join(bad)) if bad else "PASS | all 60 money_end match")
prev = {0: 3000.0, 1: 3000.0}
bad_doc = []
for d in range(30):
    for p, docp, name in [(0, doc_p_ymg, "ymg"), (1, doc_p_maj, "maj")]:
        act = D1[(d, p)]["money_end"] - prev[p]
        if abs(act - docp[d]) > 0.5:
            bad_doc.append(f"d{d}{name}: docΔ={docp[d]} correctΔ={act:.0f}")
        prev[p] = D1[(d, p)]["money_end"]
log("DOC Δ ERRORS: " + "; ".join(bad_doc) if bad_doc else "PASS | doc Δ column all correct")

# --- 04B §3 summary ---
log("\n-- §3 summary from summary.json --")
S = load("match1", "summary.json")
eq("ymg revenue", S["p0"]["revenue"], 116858)
eq("maj revenue", S["p1"]["revenue"], 110387)
eq("ymg hire", S["p0"]["hire_spend"], 6481)
eq("maj hire", S["p1"]["hire_spend"], 4824)

# --- 04B §5 revenue per item ---
log("\n-- §5 revenue per item --")
rev1 = {0: defaultdict(lambda: [0, 0.0]), 1: defaultdict(lambda: [0, 0.0])}
for o in O1:
    if o["op"] == "SELL" and o["units"] > 0:
        rev1[o["player"]][o["item"]][0] += o["units"]
        rev1[o["player"]][o["item"]][1] += o["cash"]
doc5 = {("ymg", "STRAWBERRY"): (211, 20326, 96.3), ("ymg", "MILK"): (219, 19507, 89.1), ("ymg", "WHEAT"): (482, 18464, 38.3),
        ("ymg", "FERTILIZER"): (251, 14707, 58.6), ("ymg", "MELON"): (84, 13099, 155.9), ("ymg", "EGG"): (208, 10926, 52.5),
        ("ymg", "TOMATO"): (91, 8359, 91.9), ("ymg", "CARROT"): (137, 6118, 44.7), ("ymg", "WOOL"): (70, 5352, 76.5),
        ("maj", "STRAWBERRY"): (150, 20598, 137.3), ("maj", "MILK"): (232, 20320, 87.6), ("maj", "WHEAT"): (478, 19564, 40.9),
        ("maj", "FERTILIZER"): (157, 10535, 67.1), ("maj", "MELON"): (72, 17298, 240.2), ("maj", "EGG"): (0, 0, 0),
        ("maj", "TOMATO"): (128, 11972, 93.5), ("maj", "CARROT"): (109, 5102, 46.8), ("maj", "WOOL"): (71, 4998, 70.4)}
for (side, item), (u, c, avg) in doc5.items():
    p = 0 if side == "ymg" else 1
    au, ac = rev1[p][item]
    aavg = ac / au if au else 0
    log(f"{'PASS' if au == u and abs(ac - c) < 3 and abs(aavg - avg) < 0.15 else 'FAIL'} | 5 {side} {item}: {au}u ${ac:.0f} @{aavg:.1f} (doc {u}u ${c} @{avg})")

# --- 04B §6.3 endgame ---
log("\n-- §6.3 endgame d29 --")
for p, nm in [(0, "ymg"), (1, "maj")]:
    t = T1[(696, p)]
    log(f"INFO | {nm} s696 shed: " + ", ".join(f"{k}={v}" for k, v in t["shed"].items() if v) + f" | total={t['shed_total']}")
    log(f"INFO | {nm} s696 yields on plants: {t['yields']} | animals: {t['animals']} | hands={t['hands']}")
s697 = [o for o in O1 if o["step"] == 697 and o["units"] > 0]
for o in s697:
    log(f"INFO | m1 s697 p{o['player']} {o['op']} {o['item']} {o['units']}u ${o['cash']:.0f}")
r697 = sum(o["cash"] for o in s697 if o["player"] == 0 and o["cash"] > 0)
check("ymg s697 revenue", r697, 2615, 3)
# d29 per-item
log("\n-- d29 per-item sells --")
d29 = {0: defaultdict(lambda: [0, 0.0]), 1: defaultdict(lambda: [0, 0.0])}
for o in O1:
    if o["day"] == 29 and o["op"] == "SELL" and o["units"] > 0:
        d29[o["player"]][o["item"]][0] += o["units"]
        d29[o["player"]][o["item"]][1] += o["cash"]
for p, nm in [(0, "ymg"), (1, "maj")]:
    tot_u = sum(v[0] for v in d29[p].values()); tot_c = sum(v[1] for v in d29[p].values())
    log(f"INFO | {nm} d29: " + ", ".join(f"{k}={v[0]}u/${v[1]:.0f}" for k, v in sorted(d29[p].items())) + f" | TOTAL {tot_u}u ${tot_c:.0f}")
# trace 715-719
log("\n-- trace s714-719 --")
for s in range(713, 720):
    log(f"INFO | s{s}: ymg={T1[(s,0)]['money']:.0f} maj={T1[(s,1)]['money']:.0f}")
s719 = [o for o in O1 if o["step"] == 719 and o["units"] > 0]
for o in s719:
    log(f"INFO | m1 s719 p{o['player']} {o['op']} {o['item']} {o['units']}u ${o['cash']:.0f}")
y719 = sum(o["cash"] for o in s719 if o["player"] == 0 and o["cash"] > 0)
m719 = sum(o["cash"] for o in s719 if o["player"] == 1 and o["cash"] > 0)
check("ymg s719 revenue", y719, 1405, 3)
check("maj s719 revenue", m719, 260, 3)

# --- 04B §6.4 dead orders ---
log("\n-- §6.4 dead orders --")
for p, nm, td in [(0, "ymg", 878), (1, "maj", 949)]:
    po = [o for o in O1 if o["player"] == p]
    dead = [o for o in po if o["units"] == 0 and o["cash"] == 0]
    eq(f"{nm} total orders", len(po), td)
    eq(f"{nm} dead", len(dead), 2 if p == 0 else 45)

# --- 04B opening ---
log("\n-- opening d0 --")
for o in O1:
    if o["day"] == 0 and o["step"] <= 3 and o["units"] > 0:
        log(f"INFO | m1 d0 s{o['step']} p{o['player']} {o['op']} {o['item']} {o['units']}u ${o['cash']:.0f} prices[:2]={o['prices'][:2]}")
d0a = {0: defaultdict(int), 1: defaultdict(int)}
for o in O1:
    if o["day"] == 0 and o["op"] == "BUY_ANIMAL" and o["units"] > 0:
        d0a[o["player"]][o["item"]] += o["units"]
log(f"INFO | d0 animals: ymg={dict(d0a[0])} maj={dict(d0a[1])}")

# --- 04B escapes, hands, weeds, verbs ---
log("\n-- animals by day (escapes) --")
for p, nm in [(0, "ymg"), (1, "maj")]:
    prev_a = None
    for d in range(18, 30):
        a = dict(D1[(d, p)]["animals"])
        if a != prev_a:
            log(f"INFO | {nm} animals end d{d}: {a}")
            prev_a = a
log("\n-- hands --")
for p, nm in [(0, "ymg"), (1, "maj")]:
    h = {d: D1[(d, p)]["hands_max"] for d in [8, 9, 20, 26, 27, 28, 29]}
    log(f"INFO | {nm} hands_max: {h}")
log("\n-- totals verbs --")
for p, nm in [(0, "ymg"), (1, "maj")]:
    w = sum(D1[(d, p)]["verbs"].get("WATER", 0) for d in range(30))
    wz = sum(D1[(d, p)]["weeds"] for d in range(30))
    h29 = D1[(29, p)]["verbs"].get("HARVEST", 0)
    dr29 = D1[(29, p)]["verbs"].get("DROP", 0)
    wa29 = D1[(29, p)]["verbs"].get("WATER", 0)
    cf = D1[(29, p)]["verbs"].get("COLLECT_FERTILIZER", 0)
    log(f"INFO | {nm}: WATER total={w} (doc 942/1181) weeds_total={wz} (doc 16/26) d29 HARVEST={h29} DROP={dr29} WATER={wa29} COLLECT_FERT={cf}")

# --- 04B goose buys / cow buys by day ---
log("\n-- animal purchases by day --")
for p, nm in [(0, "ymg"), (1, "maj")]:
    ab = defaultdict(lambda: defaultdict(int))
    for o in O1:
        if o["op"] == "BUY_ANIMAL" and o["units"] > 0 and o["player"] == p:
            ab[o["day"]][o["item"]] += o["units"]
    log(f"INFO | {nm}: " + "; ".join(f"d{d}:{dict(v)}" for d, v in sorted(ab.items())))

# --- 04B STRA timing: ymg dump d19-24 ---
log("\n-- STRA sells by day --")
for p, nm in [(0, "ymg"), (1, "maj")]:
    ss = defaultdict(lambda: [0, 0.0])
    for o in O1:
        if o["op"] == "SELL" and o["item"] == "STRAWBERRY" and o["units"] > 0 and o["player"] == p:
            ss[o["day"]][0] += o["units"]
            ss[o["day"]][1] += o["cash"]
    log(f"INFO | {nm} STRA: " + " ".join(f"d{d}:{v[0]}u@{v[1]/v[0]:.0f}" for d, v in sorted(ss.items())))
ymg_dump = [o for o in O1 if o["op"] == "SELL" and o["item"] == "STRAWBERRY" and 19 <= o["day"] <= 24 and o["player"] == 0 and o["units"] > 0]
du = sum(o["units"] for o in ymg_dump); dc = sum(o["cash"] for o in ymg_dump)
log(f"INFO | ymg STRA dump d19-24: {du}u ${dc:.0f} @{dc/du:.1f} (doc 120u @44.8)")
lo = [o for o in ymg_dump if o["cash"] / o["units"] < 10]
log(f"INFO | ymg STRA sub-$10 sells d19-24: " + "; ".join(f"d{o['day']} {o['units']}u@{o['cash']/o['units']:.0f}" for o in lo))

log("\nDONE. Full log saved.")
with open(f"{BASE}/verify_report_task83.txt", "w") as f:
    f.write("\n".join(OUT))
