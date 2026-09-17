#!/usr/bin/env python3
"""Stage 3: TẤN CÔNG & ÉP GIÁ — same-step collisions (kèm order index từ replay gốc),
phản ứng sau khi bị dump (trough wait), vòng tua FERTILIZER, và pre-sale attacks."""
import json
from collections import defaultdict

MATCHES = {
    "m1": ("match1", 1, 109776263), "m2": ("match2", 0, 109770002), "m3": ("match3", 1, 109763505),
    "m4": ("match4", 1, 109756255), "m5": ("match5", 1, 109748819), "m6": ("match6", 1, 109741171),
    "m7": ("match7", 1, 109732826),
}

def op_type(o):
    if isinstance(o, str): return "SELL" if o.startswith("SELL") else o.split()[0]
    return o.get("op", "?")

def op_item(o):
    if isinstance(o, str):
        parts = o.split()
        return parts[1] if len(parts) > 1 else None
    return o.get("item")

all_collisions = []
trough_waits = []       # (match, item, dumper, victim, dump_step, next_sell_step, wait, price_at_dump, price_at_next)
fert_rt = []            # fertilizer round-trip per match
attacks = []            # pre-sale attack candidates

for key, (mdir, midx, eid) in MATCHES.items():
    oidx = 1 - midx
    ords = json.load(open(f"{mdir}/orders.json"))
    mkt = json.load(open(f"{mdir}/market.json"))
    prices = {m["step"]: m["prices"] for m in mkt}

    # ---- extract action queues with order index from raw replay ----
    raw = json.load(open(f"episode-{eid}-replay.json"))
    steps = raw["steps"]
    queues = {}  # (step, player) -> list of (idx, op, item, asked)
    for t in range(len(steps)):
        for p in (0, 1):
            act = steps[t][p].get("action") or {}
            m = act.get("market", []) if isinstance(act, dict) else []
            qlist = []
            for i, o in enumerate(m if isinstance(m, list) else []):
                if isinstance(o, (list, tuple)) and len(o) >= 2:
                    op, item, asked = o[0], o[1], int(o[2]) if len(o) > 2 else 1
                elif isinstance(o, str):
                    parts = o.split()
                    op = parts[0] if parts else "?"
                    item = parts[1] if len(parts) > 1 else None
                    asked = int(parts[2]) if len(parts) > 2 else 1
                elif isinstance(o, dict):
                    op = o.get("op", "?"); item = o.get("item"); asked = int(o.get("units", o.get("asked", 1)))
                else:
                    continue
                qlist.append((i, op, item, asked))
            queues[(t, p)] = qlist
    del raw, steps

    # ---- 1. same-step same-item collisions with index info ----
    # gom sells theo (step, item, player) từ orders (đã execute)
    sells_by_si = defaultdict(lambda: {0: None, 1: None})
    for o in ords:
        if o["op"] != "SELL" or o["units"] <= 0: continue
        sells_by_si[(o["step"], o["item"])][o["player"]] = o
    for (t, it), pair in sells_by_si.items():
        if pair[0] is None or pair[1] is None: continue
        # index mỗi bên đặt sell này
        idx = {}
        for p in (0, 1):
            for (i, op, item, asked) in queues.get((t, p), []):
                if op == "SELL" and item == it:
                    idx[p] = i; break
        all_collisions.append({
            "match": key, "step": t, "day": t // 24, "item": it,
            "u0": pair[0]["units"], "p0_avg": pair[0]["cash"] / pair[0]["units"],
            "u1": pair[1]["units"], "p1_avg": pair[1]["cash"] / pair[1]["units"],
            "i0": idx.get(0), "i1": idx.get(1),
            "majkel": midx,
        })

    # ---- 2. trough wait: sau big-dump của đối thủ, chờ bao lâu Majkel mới bán lại item đó ----
    sells_m = sorted([o for o in ords if o["op"] == "SELL" and o["player"] == midx and o["units"] > 0], key=lambda o: o["step"])
    sells_o = sorted([o for o in ords if o["op"] == "SELL" and o["player"] == oidx and o["units"] > 0], key=lambda o: o["step"])
    dumps_o = [o for o in sells_o if o["units"] >= 10]
    for dmp in dumps_o:
        it = dmp["item"]; t0 = dmp["step"]
        nxt = next((s for s in sells_m if s["item"] == it and s["step"] > t0), None)
        wait = nxt["step"] - t0 if nxt else None
        trough_waits.append({
            "match": key, "item": it, "dump_step": t0, "dump_units": dmp["units"],
            "dump_price": dmp["cash"] / dmp["units"],
            "wait": wait,
            "price_at_next": prices[nxt["step"]][it] if nxt else None,
            "next_units": nxt["units"] if nxt else 0,
        })
    # và ngược lại: sau dump của MAJKEL, đối thủ chờ bao lâu
    dumps_m = [o for o in sells_m if o["units"] >= 10]
    for dmp in dumps_m:
        it = dmp["item"]; t0 = dmp["step"]
        nxt = next((s for s in sells_o if s["item"] == it and s["step"] > t0), None)
        wait = nxt["step"] - t0 if nxt else None
        trough_waits.append({
            "match": key, "item": it, "dump_step": t0, "dump_units": dmp["units"],
            "dump_price": dmp["cash"] / dmp["units"], "wait": wait, "who": "majkel_dump",
            "price_at_next": prices[nxt["step"]][it] if nxt else None,
            "next_units": nxt["units"] if nxt else 0,
        })

    # ---- 3. FERTILIZER round-trip ----
    fb = [o for o in ords if o["item"] == "FERTILIZER" and o["op"] == "BUY_PRODUCT" and o["units"] > 0]
    fs = [o for o in ords if o["item"] == "FERTILIZER" and o["op"] == "SELL" and o["units"] > 0]
    for p, tag in [(midx, "M"), (oidx, "O")]:
        b = [o for o in fb if o["player"] == p]; s = [o for o in fs if o["player"] == p]
        if not s: continue
        fert_rt.append({
            "match": key, "who": tag,
            "buy_n": sum(o["units"] for o in b), "buy_avg": (sum(-o["cash"] for o in b) / sum(o["units"] for o in b)) if b else 0,
            "sell_n": sum(o["units"] for o in s), "sell_avg": sum(o["cash"] for o in s) / sum(o["units"] for o in s),
            "pnl": sum(o["cash"] for o in s) + sum(o["cash"] for o in b),
        })

json.dump({"collisions": all_collisions, "trough": trough_waits, "fert": fert_rt},
          open("an5_attack.json", "w"), indent=1)

# ================= IN KẾT QUẢ =================
print("=" * 100)
print("1. SAME-STEP SAME-ITEM COLLISIONS (cả 7 trận)")
print("=" * 100)
print(f"tổng collisions: {len(all_collisions)}")
byitem = defaultdict(int)
for c in all_collisions: byitem[c["item"]] += 1
print("theo item:", dict(sorted(byitem.items(), key=lambda x: -x[1])))
# index battle: khi collision, ai đặt index thấp hơn?
maj_low = maj_high = tie = both_none = 0
for c in all_collisions:
    i0, i1 = c["i0"], c["i1"]
    if i0 is None or i1 is None: both_none += 1; continue
    m_i, o_i = (i0, i1) if c["majkel"] == 0 else (i1, i0)
    if m_i < o_i: maj_low += 1
    elif m_i > o_i: maj_high += 1
    else: tie += 1
print(f"Majkel index-thấp-hơn: {maj_low} | đối thủ thấp hơn: {maj_high} | bằng: {tie} | thiếu index: {both_none}")
# giá đạt được khi index thấp vs cao
low_p = []; high_p = []
for c in all_collisions:
    i0, i1 = c["i0"], c["i1"]
    if i0 is None or i1 is None or i0 == i1: continue
    p_m, p_o = (c["p0_avg"], c["p1_avg"]) if c["majkel"] == 0 else (c["p1_avg"], c["p0_avg"])
    i_m, i_o = (i0, i1) if c["majkel"] == 0 else (i1, i0)
    if i_m < i_o: low_p.append(p_m)
    else: high_p.append(p_o)
if low_p and high_p:
    print(f"giá TB khi index thấp hơn: {sum(low_p)/len(low_p):.1f} (n={len(low_p)}) | khi cao hơn: {sum(high_p)/len(high_p):.1f} (n={len(high_p)})")

print()
print("=" * 100)
print("2. TROUGH WAIT — sau big-dump (>=10u), bên kia chờ bao lâu mới bán lại item đó")
print("=" * 100)
for who in ["majkel_dump", "opp_dump"]:
    if who == "majkel_dump":
        grp = [t for t in trough_waits if t.get("who") == "majkel_dump"]
        label = "SAU DUMP CỦA MAJKEL → đối thủ bán lại sau:"
    else:
        grp = [t for t in trough_waits if "who" not in t]
        label = "SAU DUMP CỦA ĐỐI THỦ → Majkel bán lại sau:"
    waits = [t["wait"] for t in grp if t["wait"] is not None]
    never = sum(1 for t in grp if t["wait"] is None)
    if not grp: continue
    buckets = defaultdict(int)
    for w in waits:
        b = "0-3" if w <= 3 else "4-11" if w <= 11 else "12-23" if w <= 23 else "24-47" if w <= 47 else "48+"
        buckets[b] += 1
    print(f"\n{label} (n={len(grp)}, never={never})")
    for b in ["0-3", "4-11", "12-23", "24-47", "48+"]:
        print(f"  wait {b:>6} steps: {buckets.get(b,0):>3}")
    # giá khi bán lại so với giá dump
    rec = [t["price_at_next"] - t["dump_price"] for t in grp if t["wait"] is not None and t["price_at_next"]]
    if rec:
        print(f"  giá khi bán lại − giá lúc dump: avg {sum(rec)/len(rec):+.1f} (n={len(rec)})")

print()
print("=" * 100)
print("3. FERTILIZER ROUND-TRIP (mua thấp bán cao)")
print("=" * 100)
print(f"{'match':5} {'who':4} {'buy_n':>6} {'buy_avg':>8} {'sell_n':>7} {'sell_avg':>8} {'PnL':>8}")
for r in fert_rt:
    print(f"{r['match']:5} {r['who']:4} {r['buy_n']:>6} {r['buy_avg']:>8.1f} {r['sell_n']:>7} {r['sell_avg']:>8.1f} {r['pnl']:>8.0f}")
