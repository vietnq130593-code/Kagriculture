#!/usr/bin/env python3
"""t76_h5_hitrate.py — offline gate for H5 (plan: memory guesses >=60% of
opponent sell-turns).

Runs one battle v16h5 vs <opponent> via arena/run_battle.py (JSONL), then
replays the exact H5 decision logic (imported from v16h5.py) on the public
farm states and scores the 1-NN prediction against the opponent's ACTUAL SELL
items (read directly from the recorded actions).

Usage: python3 bench/t76_h5_hitrate.py <opponent> [seed] [--seat b]
"""
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

spec = importlib.util.spec_from_file_location('v16h5_mod', os.path.join(ROOT, 'v16h5.py'))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


def battle(opponent, seed, a='v16h5'):
    out = f'/tmp/t76_hit_{a}_vs_{opponent}_{seed}.jsonl'
    cmd = [sys.executable, os.path.join(ROOT, 'arena', 'run_battle.py'),
           '--a', a, '--b', opponent, '--seed', str(seed)]
    with open(out, 'w') as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.DEVNULL, check=True)
    return [json.loads(l) for l in open(out)]


def analyse(lines, opp_seat=1):
    turns = [l for l in lines if l.get('t') == 'turn']
    fired = 0
    abstained = 0
    sell_turns = 0
    hit_turns = 0
    pred_items = 0
    hit_items = 0
    actual_items = 0
    dists = []
    for t in turns:
        step = t['step']
        farms = t['farms']
        acts = t['acts']
        opp_farm = farms[opp_seat]
        opp_act = acts[opp_seat] or {}
        actual = {o[1] for o in (opp_act.get('market') or [])
                  if isinstance(o, list) and len(o) >= 3 and o and o[0] == 'SELL'}
        sig = M._h5_signature(opp_farm)
        best = None
        bi = -1
        for i, p in enumerate(M._H5_PROTOTYPES):
            s = p['signatures']
            if step >= len(s):
                continue
            d = M._h5_distance(sig, s[step])
            if best is None or d < best:
                best = d
                bi = i
        if best is not None and best <= M._H5_MAX_DISTANCE:
            fired += 1
            dists.append(best)
            sales = M._H5_PROTOTYPES[bi]['sales']
            pred = set((sales[step] if step < len(sales) else {}).keys())
            pred_items += len(pred)
            hit_items += len(pred & actual)
            if actual:
                sell_turns += 1
                if pred & actual:
                    hit_turns += 1
        else:
            abstained += 1
            if actual:
                sell_turns += 1
    return {
        'turns': len(turns), 'fired': fired, 'abstained': abstained,
        'opp_sell_turns': sell_turns, 'hit_turns': hit_turns,
        'turn_hit_rate': round(hit_turns / max(1, sell_turns), 3),
        'item_precision': round(hit_items / max(1, pred_items), 3),
        'item_recall': round(hit_items / max(1, actual_items), 3),
        'avg_best_distance': round(sum(dists) / max(1, len(dists)), 1),
    }


def main():
    opponents = sys.argv[1:] or ['kawashigi', 'indark_e776', 'kme3v39', 'kme3', 'kme3v10', 'aurax', 'v15']
    print(f'{"opp":14s} {"turns":>5s} {"fired":>5s} {"abst":>5s} {"sellT":>5s} {"hitT":>5s} '
          f'{"turnHR":>7s} {"itemP":>6s} {"itemR":>6s} {"avgD":>6s}')
    for opp in opponents:
        lines = battle(opp, 338)
        r = analyse(lines)
        print(f'{opp:14s} {r["turns"]:5d} {r["fired"]:5d} {r["abstained"]:5d} {r["opp_sell_turns"]:5d} '
              f'{r["hit_turns"]:5d} {r["turn_hit_rate"]:7.1%} {r["item_precision"]:6.1%} '
              f'{r["item_recall"]:6.1%} {r["avg_best_distance"]:6.1f}')


if __name__ == '__main__':
    main()
