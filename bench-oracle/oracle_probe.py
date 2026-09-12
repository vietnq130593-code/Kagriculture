#!/usr/bin/env python3
"""Oracle probe: run a battle with instrumented engine, log every market transaction."""
import os, sys, json, re, importlib

# locate project dir (never type the name)
BASE = '/home/z/my-project'
PROJ = [os.path.join(BASE, n) for n in os.listdir(BASE)
        if 'kag' in n.lower() and os.path.isdir(os.path.join(BASE, n))][0]
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(PROJ, 'bench'))

from kaggle_environments import make
import kaggle_environments

# env name from run_battle.py
rb = open(os.path.join(PROJ, 'arena', 'run_battle.py')).read()
ENV_NAME = re.search(r'make\("([^"]+)"', rb).group(1)

# import engine module and patch
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
                eng_mod._do_hire(farms[player_id], privates[player_id], int(_get(cfg, "boardSize", 10)), hire_mult)
                order_states[player_id] = None
            elif ostate["type"] == "BUY_LAND":
                eng_mod._do_buy_land(farms[player_id], int(_get(cfg, "boardSize", 10)))
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
                ok = eng_mod._commit_unit(op, item, price, farms[player_id], privates[player_id], market, shed_capacity)
                if ok:
                    TX.append({'step': _CUR['step'], 'pid': player_id, 'op': op, 'item': item, 'price': price})
                    ostate["remaining"] -= 1
                    committed_any = True
                else:
                    order_states[player_id] = None
            if not committed_any:
                break
        eng_mod._refresh_prices(market)

_orig_interp = eng_mod.interpreter

def load(path, tag):
    import importlib.util
    spec = importlib.util.spec_from_file_location(f'probe_{tag}_{os.path.basename(path)}', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.agent

A = sys.argv[1] if len(sys.argv) > 1 else 'v12'
B = sys.argv[2] if len(sys.argv) > 2 else 'dra'
SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 103

files = {'v12': 'v12.py', 'kme3': 'kme3.py', 'dra': 'dra.py'}
fnA = load(os.path.join(PROJ, files[A]), 'A')
fnB = load(os.path.join(PROJ, files[B]), 'B') if B in files else B

eng_mod._process_market = _process_market_logged

env = make(ENV_NAME, debug=False, configuration={'seed': SEED})
env.run([fnA, fnB])

r0 = float(env.steps[-1][0].reward or 0)
r1 = float(env.steps[-1][1].reward or 0)
print(json.dumps({'a': A, 'b': B, 'seed': SEED, 'r0': r0, 'r1': r1, 'tx_count': len(TX)}))

out = f'/home/z/my-project/bench-oracle/tx_{A}_{B}_{SEED}.json'
json.dump({'rewards': [r0, r1], 'tx': TX}, open(out, 'w'))
print('saved', out, 'tx:', len(TX))
