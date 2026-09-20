#!/usr/bin/env python3
"""T102 ledger: monkeypatch _commit_unit to log every executed market commit.

Runs v26d-less mirror (2945 vs 2945) seeds 100-104, reports per-product
executed revenue/units for each seat.
"""
import sys, json
from collections import defaultdict

import kaggle_environments.envs.kaggriculture.kaggriculture as K

LOG = []
_orig = K._commit_unit


def patched(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig(op, item, price, farm, private, market, shed_capacity)
    if ok:
        LOG.append((op, item, price))
    return ok


K._commit_unit = patched

from kaggle_environments import make

T29 = "/home/z/my-project/kaggriculture/thomast2945.py"

for seed in (100, 101, 102, 103, 104):
    LOG.clear()
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    # we need per-player attribution: patch again to catch player via farm id
    # simpler: wrap _commit_unit per-call order... engine passes farm object;
    # tag via id() mapping after init is complex. Instead: run and use money
    # deltas later. For now log global.
    env.run([T29, T29])
    # aggregate global executed
    agg = defaultdict(lambda: [0, 0.0])
    for op, item, price in LOG:
        k = op + ":" + item
        agg[k][0] += 1
        if op == "SELL":
            agg[k][1] += price
        else:
            agg[k][1] -= price
    print("seed", seed, "global executed (op:item, units, net$):")
    for k in sorted(agg):
        u, d = agg[k]
        print(f"   {k:22s} {u:6d} {d:+12.0f}")
