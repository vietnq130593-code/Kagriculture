#!/usr/bin/env python3
"""GOD REPLAY SYNC — replay a recorded Kaggle episode on the local engine with
per-step STATE SYNC + transaction logging (Task 71).

Usage: python3 god_replay_sync.py <replay.json> [--out tx.json]

The Kaggle server engine differs from the pip engine by ~$1 rounding on rare
market units, which cascades (order-feasibility flips) and derails a pure tape
replay. Fix: before each step t, force the local state to the RECORDED
post-step-(t-1) state (farms, market, town, both privates). Intra-step
processing then runs on exact inputs, so the TX ledger is exact-volume and
money-accurate to ~$1/step noise that never accumulates.
"""
import argparse
import importlib
import json
import os
import sys
from collections import defaultdict

BASE = '/home/z/my-project'
PROJ = os.path.join(BASE, 'kaggriculture')
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(PROJ, 'bench'))

import kaggle_environments
from kaggle_environments.utils import structify

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


def _sync_state(state, rec, rec_priv):
    """Force engine state to the recorded post-step-(t-1) snapshot (structs)."""
    obs0 = state[0].observation
    for i, rf in enumerate(rec["farms"]):
        obs0.farms[i] = structify(rf)
    params = obs0.market.get("params") if hasattr(obs0.market, "get") else None
    new_market = {"inventory": dict(rec["market"]["inventory"]),
                  "prices": dict(rec["market"]["prices"])}
    if params is not None:
        new_market["params"] = params
    obs0.market = structify(new_market)
    obs0.town = structify(rec["town"])
    for i in range(len(state)):
        state[i].observation.private = structify(rec_priv[i])
        if i:
            state[i].observation.farms = obs0.farms
            state[i].observation.market = obs0.market
            state[i].observation.town = obs0.town


_ORIG_INTERP = eng_mod.interpreter


def _synced_interpreter(state, env):
    obs0 = state[0].observation
    if hasattr(obs0, "farms") and obs0.farms:
        t = int(_get(obs0, "step", 0) or 0)
        if 1 <= t < len(REC):
            _sync_state(state, REC[t - 1], [REC_PRIV[i][t - 1] for i in range(len(state))])
    return _ORIG_INTERP(state, env)


def make_tape(actions):
    state = {'i': 0}

    def agent(obs, config):
        i = state['i']
        state['i'] += 1
        if i < len(actions) and actions[i] is not None:
            return actions[i]
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    return agent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    d = json.load(open(args.replay))
    steps = d["steps"]
    names = [a.get("Name", "?") for a in d.get("info", {}).get("Agents", [])]
    cfg = dict(d["configuration"])
    seed = d.get("info", {}).get("seed")
    if seed is not None:
        cfg["seed"] = seed  # kaggle keeps the seed in info, not configuration

    tapes = [[], []]
    for st in steps:
        for s in (0, 1):
            act = st[s].get("action")
            tapes[s].append(act)
    global REC, REC_PRIV
    REC = [st[0]["observation"] for st in steps]
    REC_PRIV = [[st[s]["observation"]["private"] for st in steps] for s in (0, 1)]

    eng_mod._process_market = _process_market_logged
    # interpreter must be swapped in the REGISTRY (make() reads the dict entry,
    # not the module attribute — captured at package import time)
    import kaggle_environments as _ke
    _ke.environments[ENV_NAME]["interpreter"] = _synced_interpreter
    env = kaggle_environments.make(ENV_NAME, debug=False, configuration=cfg)
    env.run([make_tape(tapes[0]), make_tape(tapes[1])])

    r0 = float(env.steps[-1][0].reward or 0)
    r1 = float(env.steps[-1][1].reward or 0)
    exp = d.get("rewards")
    match = (exp is not None and abs(r0 - exp[0]) < 1 and abs(r1 - exp[1]) < 1)
    near = (exp is not None and abs(r0 - exp[0]) < 50 and abs(r1 - exp[1]) < 50)
    print(f"Episode {d.get('info', {}).get('EpisodeId')} | seed {cfg.get('seed')}")
    print(f"Teams: {names}")
    print(f"GOD-REPLAY-SYNC verify: local [{r0:,.0f}, {r1:,.0f}] vs kaggle {exp} -> "
          f"{'EXACT' if match else ('NEAR (drift <$50 — ledger trustworthy)' if near else 'MISMATCH — check sync!')}")

    agg = {0: defaultdict(lambda: {'sell': 0.0, 'buy': 0.0, 'u_sell': 0, 'u_buy': 0}),
           1: defaultdict(lambda: {'sell': 0.0, 'buy': 0.0, 'u_sell': 0, 'u_buy': 0})}
    day_rev = {0: defaultdict(float), 1: defaultdict(float)}
    for tx in TX:
        pid = tx['pid']
        day = tx['step'] // 24
        item = tx['item'] or tx['op']
        dd = agg[pid][item]
        if tx['op'] == 'SELL':
            dd['sell'] += tx['price']
            dd['u_sell'] += 1
            day_rev[pid][day] += tx['price']
        else:
            dd['buy'] += tx['price']
            dd['u_buy'] += 1
            day_rev[pid][day] -= tx['price']

    for pid in (0, 1):
        print(f"\n--- SEAT {pid}: {names[pid]} ---")
        tot_s = tot_b = 0
        items = sorted(agg[pid], key=lambda k: -(agg[pid][k]['sell'] - agg[pid][k]['buy']))
        for it in items:
            v = agg[pid][it]
            net = v['sell'] - v['buy']
            tot_s += v['sell']
            tot_b += v['buy']
            print(f"  {str(it):12s} sold {v['u_sell']:>5d}u ${v['sell']:>9,.0f} | "
                  f"bought {v['u_buy']:>4d}u ${v['buy']:>8,.0f} | net {net:>+9,.0f}")
        print(f"  TOTAL: sold ${tot_s:,.0f} | spent ${tot_b:,.0f} | net {tot_s - tot_b:+,.0f}")

    print("\nper-day net (rev - spend):")
    for day in range(30):
        a = day_rev[0].get(day, 0.0)
        b = day_rev[1].get(day, 0.0)
        print(f"  d{day:02d} | seat0 {a:>+9,.0f} | seat1 {b:>+9,.0f} | diff {a - b:>+9,.0f}")

    if args.out:
        out = {
            "episode": d.get("info", {}).get("EpisodeId"), "seed": cfg.get("seed"),
            "names": names, "rewards_local": [r0, r1], "rewards_kaggle": exp,
            "dollar_exact": match,
            "ledger": {str(pid): {k: dict(v) for k, v in agg[pid].items()} for pid in (0, 1)},
            "day_net": {str(pid): {str(d): v for d, v in day_rev[pid].items()} for pid in (0, 1)},
            "tx_count": len(TX),
        }
        json.dump(out, open(args.out, "w"), indent=1)
        print(f"\nsaved {args.out}")


if __name__ == "__main__":
    main()
