#!/usr/bin/env python3
"""t76_matrix.py — Task 76 evaluation battery driver.

Runs every (variant, opponent) pairing through bench/battery.py (seeds 340-344,
both seats = 10 games each) plus the 3 direct variant pairings, then writes a
combined summary. Designed to run as a double-fork daemon (survives tool calls).

Pairings: v16h5/v16h7/v16h57 x 10 opponents + 3 direct = 33 x 10 games = 330.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

VARIANTS = ['v16h5', 'v16h7', 'v16h57']
OPPONENTS = ['v16', 'v15', 'v14', 'v13', 'kme3', 'kme3v10', 'aurax',
             'kme3v39', 'kawashigi', 'indark_e776']
DIRECT = [('v16h57', 'v16h5'), ('v16h57', 'v16h7'), ('v16h5', 'v16h7')]
SEEDS = '340-344'

PAIRS = [(v, o) for v in VARIANTS for o in OPPONENTS] + DIRECT


def out_path(a, b):
    return os.path.join(HERE, f't76_{a}_vs_{b}.json')


def summarize():
    rows = []
    for a, b in PAIRS:
        p = out_path(a, b)
        if not os.path.exists(p):
            continue
        r = json.load(open(p))
        rows.append(r)
    rows.sort(key=lambda r: (r['a'], r['b']))
    out = {'seeds': SEEDS, 'rows': rows}
    json.dump(out, open(os.path.join(HERE, 't76_summary.json'), 'w'), indent=1)
    print('\n==== SUMMARY ====')
    for r in rows:
        print(f"{r['a']:8s} vs {r['b']:12s} {r['wins']:2d}/{r['games']:2d} "
              f"gap {r['gap']:+9,.0f} worst {r['worst_ratio']:.3f}")
    return out


def main():
    t0 = time.time()
    done = 0
    for a, b in PAIRS:
        p = out_path(a, b)
        if os.path.exists(p):
            try:
                old = json.load(open(p))
                if old.get('seeds') == SEEDS and not old.get('fails'):
                    done += 1
                    continue
            except Exception:
                pass
        cmd = [sys.executable, os.path.join(HERE, 'battery.py'), a, b,
               '--seeds', SEEDS, '--out', os.path.basename(p), '--jobs', '2',
               '--tag', 't76']
        print(f'[{done + 1}/{len(PAIRS)}] {" ".join(cmd[:4])} ...', flush=True)
        subprocess.run(cmd, cwd=ROOT)
        done += 1
    print(f'matrix complete: {done} pairings, {time.time() - t0:.0f}s', flush=True)
    summarize()


if __name__ == '__main__':
    main()
