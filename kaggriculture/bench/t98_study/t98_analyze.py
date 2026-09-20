#!/usr/bin/env python3
"""Task 98 instrument: per-item money flow + SELL timeline + price trajectory
for a battle JSONL. Answers: where did the loser lose, and what did the
sale-advance layer do around those events?"""
import json, sys
from collections import defaultdict

path = sys.argv[1]
lines = [json.loads(l) for l in open(path)]
end = lines[-1]
assert end['t'] == 'end'

turns = [l for l in lines if l.get('t') == 'turn']
A, B = 0, 1  # player indices

# ---- per-item money flow: replay SELL orders against price walk ----
# The engine processes orders slot-by-slot interleaved; exact per-unit prices
# are not in the JSONL, but per-turn realized revenue IS observable via money
# deltas per player. We attribute money deltas to items by matching our own
# SELL quantities (approx attribution; good enough to locate the leak).
money = {A: [0.0], B: [0.0]}
for t in turns:
    for p in (A, B):
        money[p].append(float(t['farms'][p]['money']) - money[p][-1])

sell_events = []  # (step, player, item, qty, price_at_turn)
buy_events = []
for t in turns:
    step = t['step']
    for p, who in ((A, 'A'), (B, 'B')):
        for o in (t['acts'][p].get('market') or []):
            if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL':
                sell_events.append((step, p, o[1], int(o[2]), t['market']['prices'].get(o[1], 0), who))
            elif isinstance(o, list) and len(o) >= 3 and o[0] == 'BUY_PRODUCT':
                buy_events.append((step, p, o[1], int(o[2]), who))

# realized revenue per item per player from money deltas on sell turns is
# messy (buys mixed); instead compute GROSS if sold at quoted price
# (pre-sell quote) — approximation flag kept in mind.
gross = defaultdict(float)
units = defaultdict(int)
for step, p, item, q, px, who in sell_events:
    gross[(p, item)] += q * px
    units[(p, item)] += q

print("=== FINAL money ===")
print(f"A: {end['rewards'][A]:.0f}  B: {end['rewards'][B]:.0f}  margin(A-B): {end['rewards'][A]-end['rewards'][B]:.0f}")

print("\n=== GROSS quoted-price revenue by item (units) ===")
items = sorted({it for (_, it) in gross})
print(f"{'item':<12}{'A_units':>8}{'A_$':>10}{'B_units':>8}{'B_$':>10}{'d_units':>8}{'d_$':>10}")
for it in items:
    au, aq = units[(A, it)], gross[(A, it)]
    bu, bq = units[(B, it)], gross[(B, it)]
    print(f"{it:<12}{au:>8}{aq:>10.0f}{bu:>8}{bq:>10.0f}{au-bu:>8}{aq-bq:>10.0f}")

# ---- price trajectory around key items ----
print("\n=== price trajectory (daily, h0) ===")
for it in ('EGG', 'WHEAT', 'WOOL', 'MILK', 'STRAWBERRY'):
    traj = []
    for t in turns:
        if t['step'] % 24 == 0:
            traj.append((t['step'] // 24, t['market']['prices'].get(it, 0)))
    print(f"{it:<12}", ' '.join(f"d{d}:{p}" for d, p in traj))

# ---- sell timeline diff for the top-gap items ----
print("\n=== SELL timeline (A=v25 seat0, B=ahmedv48 seat1) ===")
for it in ('EGG', 'WHEAT'):
    print(f"--- {it} ---")
    for p, who in ((A, 'A'), (B, 'B')):
        evs = [(s, q, px) for s, pp, i, q, px, w in sell_events if i == it and pp == p and q > 0]
        print(f"  {who}: " + ' '.join(f"s{s}x{q}@{px}" for s, q, px in evs[:60]))

# ---- day-level money delta comparison ----
print("\n=== daily money delta (A vs B), worst 6 days ===")
dayA = defaultdict(float)
dayB = defaultdict(float)
for t in turns:
    d = t['step'] // 24
    dayA[d] += money[A][t['step'] + 1]
    dayB[d] += money[B][t['step'] + 1]
worst = sorted(range(30), key=lambda d: dayA[d] - dayB[d])[:6]
for d in worst:
    print(f"  day {d:>2}: A {dayA[d]:>+9.0f}  B {dayB[d]:>+9.0f}  diff {dayA[d]-dayB[d]:>+9.0f}")

# ---- animal counts over time ----
print("\n=== animal tiles over time (every 2d) ===")
def count_animals(farm):
    n = 0
    for tl in (farm.get('tiles') or []):
        if isinstance(tl, dict) and tl.get('animal'):
            n += 1
    return n
for p, who in ((A, 'A'), (B, 'B')):
    series = []
    for t in turns:
        if t['step'] % 48 == 0:
            series.append((t['step'] // 24, count_animals(t['farms'][p])))
    print(f"  {who}: {series}")

# ---- shed usage + hires ----
print("\n=== shed totals (max per day) + hires (per day) ===")
for p, who in ((A, 'A'), (B, 'B')):
    shed_max = defaultdict(int)
    hires = defaultdict(int)
    for t in turns:
        d = t['step'] // 24
        sh = t['priv'][p].get('shed') or {}
        shed_max[d] = max(shed_max[d], sum(v for v in sh.values() if isinstance(v, (int, float))))
        hires[d] = t['farms'][p].get('hires_today', 0)
    print(f"  {who} shed max: {[(d,v) for d,v in sorted(shed_max.items()) if v>=90]}")
    print(f"  {who} hires tot: {sum(hires.values())}")
