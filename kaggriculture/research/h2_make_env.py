#!/usr/bin/env python3
"""Create instrumented env copy `kaggriculture_h2` (Task 92).

Copies the registered kaggriculture engine (byte-identical md5 with
/home/z/engine.py) into envs/kaggriculture_h2/ and adds PURE-LOGGING hooks:
  - every successful market unit commit (op/item/price/player/step)
  - every town drain batch (step, per-item units)
  - dump to $H2_TRACE at episode DONE
NO game-logic changes (determinism preserved; same rewards expected).
"""
import json
import os
import shutil

ENVS = "/home/z/.venv/lib/python3.12/site-packages/kaggle_environments/envs"
SRC = os.path.join(ENVS, "kaggriculture")
DST = os.path.join(ENVS, "kaggriculture_h2")

os.makedirs(DST, exist_ok=True)
shutil.copy(os.path.join(SRC, "kaggriculture.json"),
            os.path.join(DST, "kaggriculture.json"))  # engine hardcodes this name

src = open(os.path.join(SRC, "kaggriculture.py"), encoding="utf-8").read()

# 1) step in _process_market
old = '''def _process_market(state, env):
    """Per-unit lockstep: at each step, quote both players' current-unit prices, then commit both."""
    obs0 = state[0].observation
'''
new = '''def _process_market(state, env):
    """Per-unit lockstep: at each step, quote both players' current-unit prices, then commit both."""
    obs0 = state[0].observation
    step = get(obs0, "step", 0)
'''
assert src.count(old) == 1
src = src.replace(old, new)

# 2) log commits
old = '''                if ok:
                    ostate["remaining"] -= 1
                    committed_any = True
'''
new = '''                if ok:
                    ostate["remaining"] -= 1
                    committed_any = True
                    _H2_COMMITS.append({"s": step, "p": player_id, "op": op,
                                        "it": item, "pr": price,
                                        "m": farms[player_id]["money"]})
'''
assert src.count(old) == 1
src = src.replace(old, new)

# 3) log drains
old = '''    if step % shop_interval == 0:
        # unlocked_shops may list the same shop more than once (shops are drawn
        # with replacement); each instance consumes independently.
        for shop_name in town.get("unlocked_shops", []):
            products = SHOPS[shop_name]
            multiplier = 2 if len(products) == 1 else 1
            for item in products:
                market["inventory"][item] -= multiplier

    if step % center_interval == 0:
        for item in TOWN_CENTER_PRODUCTS:
            market["inventory"][item] -= 1

    _refresh_prices(market)
'''
new = '''    _h2_drain_d = {}
    if step % shop_interval == 0:
        # unlocked_shops may list the same shop more than once (shops are drawn
        # with replacement); each instance consumes independently.
        for shop_name in town.get("unlocked_shops", []):
            products = SHOPS[shop_name]
            multiplier = 2 if len(products) == 1 else 1
            for item in products:
                market["inventory"][item] -= multiplier
                _h2_drain_d[item] = _h2_drain_d.get(item, 0) + multiplier

    if step % center_interval == 0:
        for item in TOWN_CENTER_PRODUCTS:
            market["inventory"][item] -= 1
            _h2_drain_d[item] = _h2_drain_d.get(item, 0) + 1

    if _h2_drain_d:
        _H2_DRAINS.append({"s": step, "d": _h2_drain_d})
    _refresh_prices(market)
'''
assert src.count(old) == 1
src = src.replace(old, new)

# 4) clear logs at episode init
old = '''def _initialize(state, env):
    configuration = env.configuration
'''
new = '''def _initialize(state, env):
    _H2_COMMITS.clear()
    _H2_DRAINS.clear()
    configuration = env.configuration
'''
assert src.count(old) == 1
src = src.replace(old, new)

# 5) dump at DONE
old = '''    if step >= cfg.episodeSteps - 2:
        for s in state:
            s.status = "DONE"
            s.reward = float(obs0.farms[s.observation.player]["money"])
'''
new = '''    if step >= cfg.episodeSteps - 2:
        for s in state:
            s.status = "DONE"
            s.reward = float(obs0.farms[s.observation.player]["money"])
        _h2_dump(env, obs0)
'''
assert src.count(old) == 1
src = src.replace(old, new)

# 6) append instrumentation globals + dump fn
src += '''

# ---- H2 instrumentation (Task 92) — pure logging, no logic change ----
_H2_COMMITS = []
_H2_DRAINS = []


def _h2_dump(env, obs0):
    try:
        out = os.environ.get("H2_TRACE")
        if not out:
            return
        try:
            seed = resolve_episode_seed(env)
        except Exception:
            seed = None
        payload = {"seed": seed,
                   "final_money": [f.get("money") for f in obs0.get("farms", [])],
                   "commits": _H2_COMMITS, "drains": _H2_DRAINS}
        with open(out, "w") as f:
            json.dump(payload, f)
    except Exception:
        pass
'''

out = os.path.join(DST, "kaggriculture_h2.py")
with open(out, "w", encoding="utf-8") as f:
    f.write(src)
print("written", out, len(src), "bytes")

# verify import + registration
import importlib
import kaggle_environments
importlib.reload(kaggle_environments)
env = kaggle_environments.make("kaggriculture_h2", configuration={"seed": 5})
print("env OK:", env.name, "episodeSteps", env.configuration.episodeSteps)
