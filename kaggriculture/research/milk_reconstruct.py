#!/usr/bin/env python3
"""Exact step-level MILK market reconstruction from battle JSONL.
Per engine: each step -> _process_market (sells add +1 inv per unit at p>1),
then _town_consume (milk shops: -1 per instance each step%4==0; center: -1 each step%24==0).
We replay both sides' SELL MILK order streams in engine lockstep order and
validate the reconstructed inventory against the observed one every step.
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
    inv = None
    rev = [0.0, 0.0]
    sold = [0, 0]
    mismatch = 0
    daily = {}
    for s in sorted(by_step):
        t = by_step[s]
        obs = t['market']['inventory']['MILK']
        if inv is None:
            inv = obs
        elif inv != obs:
            mismatch += 1
            if mismatch <= 6:
                print(f"  mismatch step {s}: sim={inv} obs={obs}", file=sys.stderr)
            inv = obs
        qA, qB = [], []
        shedA = shedB = 0
        for i, target in ((0, qA), (1, qB)):
            a = t['acts'][i]
            priv = t['priv'][i]
            if a:
                for m in (a.get('market') or []):
                    if len(m) >= 3 and m[0] == 'SELL' and m[1] == 'MILK':
                        target.append(int(m[2]))
        # actual sellable stock: shed milk pre-action (engine no-ops beyond stock)
        try:
            shedA = (t['priv'][0] or {}).get('shed', {}).get('MILK', 0)
            shedB = (t['priv'][1] or {}).get('shed', {}).get('MILK', 0)
        except Exception:
            shedA = shedB = 10**9
        # engine lockstep: order slots processed in order; within slot,
        # unit-pair loop: both quote at same pre-commit inv, A commits then B.
        for slot in range(max(len(qA), len(qB))):
            nA = qA[slot] if slot < len(qA) else 0
            nB = qB[slot] if slot < len(qB) else 0
            # cap by remaining shed stock this step
            nA = min(nA, shedA); nB = min(nB, shedB)
            for _ in range(max(nA, nB)):
                p = milk_price(inv)
                if nA > 0:
                    rev[0] += p; sold[0] += 1
                    if p > 1: inv += 1
                    nA -= 1; shedA -= 1
                if nB > 0:
                    rev[1] += p; sold[1] += 1
                    if p > 1: inv += 1
                    nB -= 1; shedB -= 1
        inv = max(0, inv - drain_for_step(s, t['town']))
        d = s // 24
        dd = daily.setdefault(d, {'soldA': 0, 'soldB': 0, 'revA': 0.0, 'revB': 0.0,
                                  'inv': inv, 'price': milk_price(inv)})
        # accumulate per-day sales (sales happened before drain this step)
        dd['inv'] = inv; dd['price'] = milk_price(inv)
    return rev, sold, mismatch, by_step, daily

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/milk_probe_s5.jsonl'
    rev, sold, mismatch, by_step, daily = reconstruct(path)
    print(f"MILK revenue: A=${rev[0]:.0f} ({sold[0]} units)  B=${rev[1]:.0f} ({sold[1]} units)")
    print(f"inventory mismatches: {mismatch}")
    final = by_step[max(by_step)]
    print(f"final milk inv: {final['market']['inventory']['MILK']}, price ${final['market']['prices']['MILK']}")
    print("\nper-day (soldA soldB revA revB inv@h23 price@h23):")
    for d in sorted(daily):
        x = daily[d]
        if x['soldA'] or x['soldB']:
            print(f"  d{d:02d} A={x['soldA']:3d}/${x['revA']:7.0f} B={x['soldB']:3d}/${x['revB']:7.0f} inv={x['inv']:6d} p=${x['price']:4d}")
