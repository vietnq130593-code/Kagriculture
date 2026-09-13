#!/usr/bin/env python3
"""GAP WATERFALL — per-item / per-day money-gap attribution between two agents.

Usage:
  python3 gap_waterfall.py <A> <B> <seed> [--out file.json]

Runs one battle on the REAL engine with `_process_market` replaced by a
transaction-logging copy (technique from bench-oracle/oracle_probe.py, verified
0-mismatch in Task 62-64). Every market unit traded is logged:
  (step, pid, op, item, price)   op in {SELL, BUY_PRODUCT, BUY_SEED, BUY_ANIMAL}
HIRE / BUY_LAND money effects are captured by snapshotting farm money around
those engine calls. Output: per-item and per-day revenue/spend for both players
plus the gap waterfall A−B and the top gap cells (day × item).
"""
import argparse
import importlib
import json
import os
import sys

BASE = '/home/z/my-project'
PROJ = os.path.join(BASE, 'kaggriculture')
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(PROJ, 'bench'))

from kaggle_environments import make
import kaggle_environments

ENV_NAME = 'kaggriculture'
eng_mod = importlib.import_module(f'.envs.{ENV_NAME}.{ENV_NAME}', 'kaggle_environments')
_get = eng_mod.get

TX = []
_CUR = {'step': -1}


def _process_market_logged(state, env):
    obs0 = state[0].observation
    _CUR['step'] = int(_get(obs0, 'step', 0) or 0)
    market = obs0.market
    farms = obs0.farms
    privates = [s.observation.private for s in state]
    cfg = env.configuration
    max_orders = max(1, int(_get(cfg, "maxMarketOrdersPerTurn", 10)))
    hire_mult = int(_get(cfg, "farmHandCostMult", eng_mod.FARM_HAND_COST_MULT))
    shed_capacity = int(_get(cfg, "shedCapacity", 100))
    queues = []
    for s in state:
        action = s.action if isinstance(s.action, dict) else {}
        m = action.get("market", []) if isinstance(action, dict) else []
        q = list(m) if isinstance(m, list) else []
        queues.append(q[:max_orders])
    max_len = max((len(q) for q in queues), default=0)
    for i in range(max_len):
        order_states = []
        for player_id, q in enumerate(queues):
            ostate = None
            if i < len(q):
                ostate = eng_mod._parse_order(q[i])
            order_states.append(ostate)
        for player_id, ostate in enumerate(order_states):
            if ostate is None:
                continue
            if ostate["type"] == "HIRE":
                m0 = farms[player_id].money
                eng_mod._do_hire(farms[player_id], privates[player_id],
                                 int(_get(cfg, "boardSize", 10)), hire_mult)
                TX.append({'step': _CUR['step'], 'pid': player_id, 'op': 'HIRE',
                           'item': None, 'price': m0 - farms[player_id].money})
                order_states[player_id] = None
            elif ostate["type"] == "BUY_LAND":
                m0 = farms[player_id].money
                eng_mod._do_buy_land(farms[player_id], int(_get(cfg, "boardSize", 10)))
                TX.append({'step': _CUR['step'], 'pid': player_id, 'op': 'BUY_LAND',
                           'item': None, 'price': m0 - farms[player_id].money})
                order_states[player_id] = None
        idx_esc = 0
        while True:
            idx_esc += 1
            if idx_esc >= 100_000:
                break
            quoted = [None, None]
            for player_id, ostate in enumerate(order_states):
                if ostate is None or ostate["remaining"] <= 0:
                    continue
                op = ostate["type"]
                item = ostate["item"]
                if op == "SELL" and item in eng_mod.PRODUCTS:
                    price = eng_mod.market_price(item, market["inventory"][item], market.get("params"))
                    quoted[player_id] = ("SELL", item, price, ostate)
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    price = eng_mod.market_price(item, market["inventory"][item] - 1, market.get("params"))
                    quoted[player_id] = ("BUY_PRODUCT", item, price, ostate)
                elif op == "BUY_SEED" and item in eng_mod.CROPS:
                    quoted[player_id] = ("BUY_SEED", item, eng_mod.CROPS[item]["seed"], ostate)
                elif op == "BUY_ANIMAL" and item in eng_mod.ANIMALS:
                    quoted[player_id] = ("BUY_ANIMAL", item, eng_mod.ANIMALS[item]["cost"], ostate)
                else:
                    order_states[player_id] = None
            if all(q is None for q in quoted):
                break
            committed_any = False
            for player_id, q in enumerate(quoted):
                if q is None:
                    continue
                op, item, price, ostate = q
                ok = eng_mod._commit_unit(op, item, price, farms[player_id],
                                          privates[player_id], market, shed_capacity)
                if ok:
                    TX.append({'step': _CUR['step'], 'pid': player_id, 'op': op,
                               'item': item, 'price': price})
                    ostate["remaining"] -= 1
                    committed_any = True
                else:
                    order_states[player_id] = None
            if not committed_any:
                break
        eng_mod._refresh_prices(market)


def load(path, tag):
    import importlib.util
    spec = importlib.util.spec_from_file_location(f'wf_{tag}_{os.path.basename(path)}', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.agent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("seed", type=int)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    def resolve(x):
        p = x if os.path.isfile(x) else os.path.join(PROJ, x)
        if os.path.isfile(p):
            return p
        import re
        src = open(os.path.join(PROJ, 'arena', 'run_battle.py')).read()
        m = re.search(r'"%s"\s*:\s*\(.*?"([^"]+)"' % re.escape(x), src)
        if m:
            return os.path.join(PROJ, m.group(1).split('/')[-1])
        raise SystemExit(f"unknown agent {x}")

    fnA = load(resolve(args.a), 'A')
    fnB = load(resolve(args.b), 'B')

    eng_mod._process_market = _process_market_logged
    env = make(ENV_NAME, debug=False, configuration={'seed': args.seed})
    env.run([fnA, fnB])

    r0 = float(env.steps[-1][0].reward or 0)
    r1 = float(env.steps[-1][1].reward or 0)

    # aggregate
    agg = {0: {}, 1: {}}     # pid -> item -> {sell, buy, units_sell, units_buy}
    daily = {0: {}, 1: {}}   # pid -> day -> {sell, buy}
    for t in TX:
        pid, op, item, price, step = t['pid'], t['op'], t['item'], t['price'], t['step']
        day = step // 24
        if item is None:
            key = op
        else:
            key = item
        d = agg[pid].setdefault(key, {'sell': 0.0, 'buy': 0.0, 'u_sell': 0, 'u_buy': 0})
        dd = daily[pid].setdefault(day, {'sell': 0.0, 'buy': 0.0})
        if op == 'SELL':
            d['sell'] += price; d['u_sell'] += 1; dd['sell'] += price
        else:
            d['buy'] += price; d['u_buy'] += 1; dd['buy'] += price

    items = sorted(set(agg[0]) | set(agg[1]))
    print(f"\n=== GAP WATERFALL: {args.a} vs {args.b} seed {args.seed} ===")
    print(f"final: A ${r0:,.0f} vs B ${r1:,.0f}  gap {r0 - r1:+,.0f}")
    print(f"\n{'item':<12} {'A sell':>10} {'B sell':>10} {'gap sell':>9} | {'A buy':>9} {'B buy':>9} {'gap buy':>9} | {'net gap':>9}")
    for it in items:
        a = agg[0].get(it, {'sell': 0, 'buy': 0})
        b = agg[1].get(it, {'sell': 0, 'buy': 0})
        gs, gb = a['sell'] - b['sell'], a['buy'] - b['buy']
        net = gs - gb
        if abs(net) < 1 and abs(gs) < 1 and abs(gb) < 1:
            continue
        print(f"{it:<12} {a['sell']:>10,.0f} {b['sell']:>10,.0f} {gs:>+9,.0f} | "
              f"{a['buy']:>9,.0f} {b['buy']:>9,.0f} {gb:>+9,.0f} | {net:>+9,.0f}")

    print(f"\n{'day':<5} {'A net':>9} {'B net':>9} {'gap':>8}")
    for day in sorted(set(daily[0]) | set(daily[1])):
        a = daily[0].get(day, {'sell': 0, 'buy': 0})
        b = daily[1].get(day, {'sell': 0, 'buy': 0})
        na, nb = a['sell'] - a['buy'], b['sell'] - b['buy']
        print(f"{day:<5} {na:>9,.0f} {nb:>9,.0f} {na - nb:>+8,.0f}")

    if args.out:
        outp = args.out if os.path.isabs(args.out) else os.path.join(PROJ, 'bench', args.out)
        json.dump({'a': args.a, 'b': args.b, 'seed': args.seed, 'rewards': [r0, r1],
                   'agg': {str(k): v for k, v in agg.items()},
                   'daily': {str(k): v for k, v in daily.items()},
                   'tx': TX}, open(outp, 'w'))
        print(f"\nsaved {outp} ({len(TX)} transactions)")


if __name__ == "__main__":
    main()
