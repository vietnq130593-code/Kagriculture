#!/usr/bin/env python3
"""MILK market reconstruction v2 — actual sold units derived from observed
inventory deltas (engine-exact by construction), split 50/50 between sides
(validated: both tapes submit symmetric order streams in seed 5).

actual_added(step) = inv(step+1) - inv(step) + drain(step)
where inv are PRE-ACTION observed inventories and drain is known from the
shop/center schedule. Units sold at p=$1 add no supply (engine rule).
Revenue per unit = price walk in engine lockstep order.
"""
import json, sys, math

I0 = 10000
SLOPE = 1.60 * 160.0 / 122.0
AMP_B = 0.60 * 160.0 / math.sqrt(122.0)

def milk_price(inv):
    if inv >= I0:
        return max(1, int(round(160.0 - SLOPE * (inv - I0))))
    return max(1, int(round(160.0 + AMP_B * math.sqrt(I0 - inv))))

MILK_SHOPS = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}

def drain_for_step(step, town):
    shops = sum(1 for sh in town.get('unlocked_shops', []) if sh in MILK_SHOPS)
    d = 0
    if step % 4 == 0:
        d += shops
    if step % 24 == 0:
        d += 1
    return d

def reconstruct(path):
    with open(path) as f:
        lines = [json.loads(l) for l in f if l.strip()]
    turns = [l for l in lines if l.get('t') == 'turn']
    by_step = {t['step']: t for t in turns}
    steps = sorted(by_step)
    # actual units sold per step: from inv deltas
    inv_series = [(s, by_step[s]['market']['inventory']['MILK']) for s in steps]
    actual = {}
    for k in range(len(steps) - 1):
        s, inv = inv_series[k]
        s2, inv2 = inv_series[k + 1]
        drain = drain_for_step(s, by_step[s]['town'])
        added = inv2 - inv + drain
        if added > 0:
            actual[s] = added
    # last step (no next obs): use orders at final steps (REAPER) — approximate 0
    # walk the price: process steps in order; at each step with sales,
    # interleave A/B unit-by-unit (A first, both quote same pre-commit inv)
    inv = inv_series[0][1]
    rev = [0.0, 0.0]
    units = [0, 0]
    daily = {}
    for s in steps:
        n = actual.get(s, 0)
        if n > 0:
            nA = (n + 1) // 2
            nB = n - nA
            for _ in range(max(nA, nB)):
                p = milk_price(inv)
                if nA > 0:
                    rev[0] += p; units[0] += 1
                    if p > 1: inv += 1
                    nA -= 1
                if nB > 0:
                    rev[1] += p; units[1] += 1
                    if p > 1: inv += 1
                    nB -= 1
        inv = max(0, inv - drain_for_step(s, by_step[s]['town']))
        d = s // 24
        dd = daily.setdefault(d, {'units': 0, 'revA': 0.0, 'inv': inv,
                                  'price': milk_price(inv), 'revB': 0.0})
        if n:
            dd['units'] += n
        dd['revA'] = rev[0]; dd['revB'] = rev[1]
        dd['inv'] = inv; dd['price'] = milk_price(inv)
    return rev, units, daily

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/milk_probe_s5.jsonl'
    rev, units, daily = reconstruct(path)
    print(f"MILK baseline seed5: A=${rev[0]:.0f} ({units[0]}u)  B=${rev[1]:.0f} ({units[1]}u)")
    print("day: units sold(both) | inv@h23 price | cumulative revA/revB")
    for d in sorted(daily):
        x = daily[d]
        if x['units']:
            print(f"  d{d:02d} n={x['units']:3d} inv={x['inv']:6d} p=${x['price']:4d} revA={x['revA']:7.0f} revB={x['revB']:7.0f}")
