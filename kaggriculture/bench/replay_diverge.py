#!/usr/bin/env python3
"""DIVERGENCE FINDER — find the first step where a god-replay of a recorded
Kaggle episode desyncs from the recorded observations.

Usage: python3 replay_diverge.py <replay.json> [--window 12]
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

ENV_NAME = 'kaggriculture'
eng_mod = importlib.import_module(f'.envs.{ENV_NAME}.{ENV_NAME}', 'kaggle_environments')


def snap(obs):
    """Comparable snapshot of an agent-visible observation (own seat view)."""
    own = int(obs.player) if hasattr(obs, 'player') else 0
    farms = obs.farms
    f = farms[own]
    tiles = {}
    for row in f.tiles:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            k = tile.get('kind')
            tiles[k] = tiles.get(k, 0) + 1
            if tile.get('animal'):
                tiles['A_' + tile['animal']] = tiles.get('A_' + tile['animal'], 0) + 1
    prices = dict(obs.market.prices)
    inv = dict(obs.market.inventory)
    shed = dict(obs.private.shed) if obs.private else {}
    hands = len(f.hands)
    return {'money': f.money, 'tiles': tiles, 'prices': prices, 'inv': inv,
            'shed': shed, 'hands': hands, 'day': obs.day, 'hour': obs.hour}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--window", type=int, default=12)
    args = ap.parse_args()

    d = json.load(open(args.replay))
    steps = d["steps"]
    cfg = dict(d["configuration"])
    seed = d.get("info", {}).get("seed")
    if seed is not None:
        cfg["seed"] = seed

    tapes = [[], []]
    rec_snaps = [[], []]
    for st in steps:
        for s in (0, 1):
            act = st[s].get("action")
            tapes[s].append(act)
            rec_snaps[s].append(st[s]["observation"])

    first_bad = [None, None]

    def make_tape(seat):
        state = {'i': 0}

        def agent(obs, config):
            i = state['i']
            state['i'] += 1
            try:
                cur = snap(obs)
                # replay convention: obs[t] is POST-action[t]; the local engine
                # shows PRE-action state at call i == replay obs[i-1].
                j = i - 1
                rec = rec_snaps[seat][j] if 0 <= j < len(rec_snaps[seat]) else None
                if rec is not None:
                    r_money = rec['farms'][seat]['money']
                    if abs(cur['money'] - r_money) > 0.01:
                        if first_bad[seat] is None:
                            first_bad[seat] = i
                            print(f" seat{seat} FIRST MONEY DIVERGENCE at t={i} "
                                  f"(d{rec['day']} h{rec['hour']}): local {cur['money']:,.0f} vs kaggle {r_money:,.0f}")
                            for t2 in range(max(0, i - args.window // 2), min(len(steps), i + args.window // 2)):
                                r2 = rec_snaps[seat][t2]['farms'][seat]['money']
                                print(f"   t{t2} kaggle {r2:>9,.0f}")
                    # prices
                    rp = rec['market']['prices']
                    for k in rp:
                        if abs(cur['prices'].get(k, 0) - rp[k]) > 0.01:
                            if first_bad[seat] is None:
                                first_bad[seat] = i
                                print(f" seat{seat} FIRST PRICE DIVERGENCE at t={i} item {k}: "
                                      f"local {cur['prices'].get(k)} vs kaggle {rp[k]}")
                            break
            except Exception as e:
                print(f" snap error seat{seat} t={i}: {e!r}")
            a = tapes[seat][i] if i < len(tapes[seat]) and tapes[seat][i] is not None else \
                {'farmer': ['PASS'], 'hands': [], 'market': []}
            return a
        return agent

    env = make(ENV_NAME, debug=False, configuration=cfg)
    env.run([make_tape(0), make_tape(1)])
    r0 = float(env.steps[-1][0].reward or 0)
    r1 = float(env.steps[-1][1].reward or 0)
    print(f"\nfinal local [{r0:,.0f}, {r1:,.0f}] vs kaggle {d.get('rewards')}")
    print(f"first divergence: {first_bad}")


if __name__ == "__main__":
    main()
