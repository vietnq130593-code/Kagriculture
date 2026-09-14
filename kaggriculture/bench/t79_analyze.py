#!/usr/bin/env python3
"""T79 — autopsy of ahmedv41 vs v16 battles from full JSONL replays."""
import json
import sys
from collections import defaultdict

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def load(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d.get("t") == "turn":
            recs.append(d)
    return recs


def sell_price(prices, item, qty):
    """Engine price after selling qty at current inventory."""
    p = prices[item]
    inv = prices["_inv"][item]
    total = 0
    for _ in range(qty):
        if inv > 10000:
            break
        total += p
        inv += 1
        p = max(1, p - 1) if inv % 200 == 0 else p
    return total


def autopsy(path):
    recs = load(path)
    print(f"=== {path} — {len(recs)} turns ===")
    stats = []
    for seat in (0, 1):
        money = []
        sells = defaultdict(lambda: {"units": 0, "n": 0, "rev": 0.0, "hours": defaultdict(int), "days": set()})
        buys = defaultdict(lambda: {"units": 0, "n": 0, "cost": 0.0})
        plants = defaultdict(int)
        hires = defaultdict(int)
        hands_hist = []
        maxtime = 0.0
        quadrants = set()
        animals = defaultdict(int)
        opening_market = None
        first_sells = []
        for r in recs:
            step = r["step"]
            farm = r["farms"][seat]
            priv = r["priv"][seat]
            act = r["acts"][seat]
            money.append((step, farm["money"]))
            hands_hist.append((step, len(farm.get("hands", []))))
            for q in farm.get("unlocked_quadrants", []):
                quadrants.add(q)
            for row in farm["tiles"]:
                for t in row:
                    if isinstance(t, dict) and t.get("animal"):
                        animals[t["animal"]] += 1
            hires[step // 24] += farm.get("hires_today", 0) if step % 24 == 23 else 0
            if opening_market is None and act.get("market"):
                opening_market = act["market"]
            for o in act.get("market", []):
                if not o or len(o) < 3:
                    continue
                kind, item, qty = o[0], o[1], int(o[2])
                if kind == "SELL":
                    px = r["market"]["prices"][item]
                    d = sells[item]
                    d["units"] += qty
                    d["n"] += 1
                    d["rev"] += px * qty
                    d["hours"][step % 24] += qty
                    d["days"].add(step // 24)
                    if len(first_sells) < 6:
                        first_sells.append((step, item, qty, px))
                elif kind.startswith("BUY"):
                    px = r["market"]["prices"].get(item, 0)
                    buys[item]["units"] += qty
                    buys[item]["n"] += 1
                    buys[item]["cost"] += px * qty
            for h in [act.get("farmer")] + list(act.get("hands", [])):
                if h and h[0] == "PLANT":
                    plants[h[1]] += 1
            if r.get("times") and len(r["times"]) > seat:
                maxtime = max(maxtime, r["times"][seat])
        final_money = money[-1][1]
        stats.append(dict(seat=seat, final=final_money, money=money, sells=sells, buys=buys,
                         plants=plants, hires=sum(hires.values()), hands=hands_hist,
                         maxtime=maxtime, quadrants=quadrants, animals=animals,
                         opening=opening_market, first_sells=first_sells))
    for s in stats:
        who = "v16" if s["seat"] == 0 else "ahmedv41"
        print(f"\n--- seat {s['seat']} ({who}) — final ${s['final']:,.0f} | max callback {s['maxtime']:.2f}s")
        print(f"    quadrants: {sorted(s['quadrants'])} | hires: {s['hires']} | peak hands: {max(h for _, h in s['hands'])}")
        print(f"    animals placed (cum tiles): {dict(s['animals'])}")
        print(f"    plants: {dict(s['plants'])}")
        print(f"    opening market: {s['opening']}")
        print(f"    first sells: {s['first_sells']}")
        tot_units = 0
        tot_rev = 0.0
        for item in PRODUCTS:
            d = s["sells"][item]
            if d["units"]:
                tot_units += d["units"]
                tot_rev += d["rev"]
                hrs = sorted(d["hours"].items(), key=lambda x: -x[1])[:3]
                print(f"    SELL {item:10s} {d['units']:6d}u in {d['n']:4d} orders ${d['rev']:>10,.0f} | top-hours {hrs} | days {min(d['days'])}-{max(d['days'])}")
        bstr = ", ".join(f"{i}:{d['units']}u/${d['cost']:,.0f}" for i, d in s["buys"].items() if d["units"])
        print(f"    BUYs: {bstr}")
        print(f"    TOTAL sold: {tot_units}u, revenue ${tot_rev:,.0f}")
    # money crossing points
    m0 = dict(stats[0]["money"])
    m1 = dict(stats[1]["money"])
    lead_switches = 0
    last_lead = None
    gaps = []
    for step in sorted(m0):
        lead = 0 if m0[step] > m1[step] else 1
        if last_lead is not None and lead != last_lead:
            lead_switches += 1
        last_lead = lead
        if step % 24 == 23:
            gaps.append((step // 24, m1[step] - m0[step]))
    print(f"\nlead switches: {lead_switches} | day-end gap (v16 −? sign: seat1−seat0): first 5 {gaps[:5]} last 5 {gaps[-5:]}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        autopsy(p)
