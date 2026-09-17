#!/usr/bin/env python3
"""
MILK MINI-SIMULATOR — calibrated to engine + observed v46 behavior (seed 5).
Purpose: screen H1 policy candidates cheaply before real-game testing.

Engine facts (verified from kaggriculture.py):
  price(inv) = 160 - 2.0984*(inv-I0) if inv>=I0   [linear, floor $1]
             = 160 + 8.688*sqrt(I0-inv) if inv<I0  [sqrt]
  Sell 1 unit at price>1: money += p, inv += 1. Sell at $1: money += 1, inv unchanged.
  Drain: town center 1/day every day; milk shops (each 1 unit per 4 steps = 6/day)
         unlock from d18 (seed5: 1 shop) or earlier (2-shop seeds).
  Cow production with full care+feed: first harvest on day placed+8 = 6 units
         (care-bonus accumulated), then ~1.5/day steady (2-3 per 2-day event),
         tile cap 6, needs HARVEST->shed->SELL.
  Lockstep: unit i of A and unit i of B in same order slot quote at the SAME
         pre-commit inventory -> identical price per unit-pair.
v46 observed policy (seed 5 replay): dump everything daily at any price;
         d8 h4 burst 12; REAPER d27+ sell-1000s.
"""
import math

I0 = 10000
BASE = 160.0
SLOPE = 1.60 * 160.0 / 122.0   # 2.0984 per unit above I0
AMP_B = 0.60 * 160.0 / math.sqrt(122.0)  # 8.688

def milk_price(inv):
    if inv >= I0:
        return max(1, int(round(BASE - SLOPE * (inv - I0))))
    return max(1, int(round(BASE + AMP_B * math.sqrt(I0 - inv))))

def lockstep_pair(inv, nA, nB):
    """Engine-exact: for each unit-index, quote A and B at the same pre-commit
    inventory; commit A first (its sale bumps inv), then commit B (already
    quoted). B's NEXT unit sees the bumped inv."""
    revA = revB = 0
    for _ in range(max(nA, nB)):
        pA = milk_price(inv) if nA > 0 else None
        pB = milk_price(inv) if nB > 0 else None
        if nA > 0:
            revA += pA
            if pA > 1: inv += 1
            nA -= 1
        if nB > 0:
            revB += pB
            if pB > 1: inv += 1
            nB -= 1
    return revA, revB, inv


# ---------------- market sim over 30 days ----------------
def run(policy_me, cows_me=6, extra_cows_d0=0, shops="late1",
        verbose=False):
    """
    policy_me: callable(day, price, my_shed, inv) -> units to sell today.
    v46: 6 cows, dump-all-daily (observed), burst d8.
    cows_me: baseline 6 cows; extra_cows_d0: extra cows bought d0 (burst d8 too).
    shops: "late1" (seed5: 1 shop from d18), "early2" (2 shops from d6),
           "mid2" (2 shops from d12) etc.
    Returns (rev_me, rev_v46, margin_after_costs).
    """
    inv = I0 + 0
    rev_me = rev_v46 = 0.0

    def production(cows, day):
        if day < 8: return 0
        if day == 8: return 6 * cows
        return int(1.5 * cows)  # steady with care

    def drain(day):
        base = 1  # town center
        n_shops = 0
        if shops == "late1":    n_shops = 1 if day >= 18 else 0
        elif shops == "early2": n_shops = 2 if day >= 6 else (1 if day >= 3 else 0)
        elif shops == "mid2":   n_shops = 2 if day >= 12 else (1 if day >= 9 else 0)
        return base + 6 * n_shops

    shed_me = 0
    shed_v46 = 0
    daily_log = []
    for day in range(30):
        shed_me += production(cows_me + extra_cows_d0, day)
        shed_v46 += production(6, day)
        nA = policy_me(day, milk_price(inv), shed_me, inv) if shed_me > 0 else 0
        nA = min(nA, shed_me)
        nB = shed_v46  # v46 dumps everything daily
        rA, rB, inv = lockstep_pair(inv, nA, nB)
        rev_me += rA; rev_v46 += rB
        shed_me -= nA; shed_v46 -= nB
        inv = max(0, inv - drain(day))
        daily_log.append((day, inv, milk_price(inv), nA, nB))
    # REAPER d29: dump leftovers
    if shed_me or shed_v46:
        rA, rB, inv = lockstep_pair(inv, shed_me, shed_v46)
        rev_me += rA; rev_v46 += rB
    cow_cost = 400 * extra_cows_d0
    feed_cost = 30 * 20 * extra_cows_d0  # 30 days wheat @$20 marginal
    if verbose:
        for row in daily_log:
            print(f"d{row[0]:02d} inv={row[1]:6d} p=${row[2]:4d} soldA={row[3]:3d} soldB={row[4]:3d}")
    return rev_me, rev_v46, rev_me - rev_v46 - cow_cost - feed_cost


if __name__ == "__main__":
    print("=== BASELINE (both dump daily, 6 cows, late1 shop) vs observed seed5 ===")
    rA, rB, m = run(lambda d, p, s, i: s, verbose=True)
    print(f"rev_me={rA:.0f} rev_v46={rB:.0f} margin={m:.0f}")
    print("observed seed5: d08 inv=10015, d13 inv=10070, d15 inv=10076 flat floor")
