#!/usr/bin/env python3
"""t76_fit_protos.py — fit LOCAL prototype bank for H5 (Task 76).

Records the opponent's public farm signature + ACTUAL sells (from their
returned actions) for every step of fresh v16-vs-opponent battles, and stores
them in the exact compact format used by the H5 blob (flat int signatures +
sparse sale pairs). These local prototypes are merged with Kaito's 30 top-30
prototypes at build time by t76_build.py.

Fit seeds are DISJOINT from battery seeds (fit: 90-95, battery: 340-344).
Usage: python3 bench/t76_fit_protos.py            # records + writes bank
       python3 bench/t76_fit_protos.py --report   # summarizes existing bank
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import importlib.util  # noqa: E402
spec = importlib.util.spec_from_file_location('v16h5_mod', os.path.join(ROOT, 'v16h5.py'))
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

BANK = os.path.join(HERE, 't76_local_bank.json')
ITEMS = ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER')
IDX = {it: k for k, it in enumerate(ITEMS)}

# (opponent, seeds) — 2 games each, 3 for kawashigi (5-tape router by town shops)
PLAN = [
    ('kme3', (90, 91)),
    ('kme3v10', (90, 91)),
    ('kme3v39', (90, 91)),
    ('aurax', (90, 91)),
    ('kawashigi', (90, 91, 92)),
    ('indark_e776', (90, 91)),
    ('v13', (90, 91)),
    ('v14', (90, 91)),
    ('v15', (90, 91)),
    ('v16', (90, 91)),
]


def enc_sig(s):
    return ([int(s['workers']), int(s['unlocks'])]
            + [int(x) for x in s['positions']]
            + [int(x) for x in s['counts']]
            + [int(x) for x in s['yields']])


def enc_sales(d):
    out = []
    for it, q in (d or {}).items():
        if it in IDX and int(q) > 0:
            out += [IDX[it], int(q)]
    return out


def record(opponent, seed, opp_seat=1):
    out = f'/tmp/t76_fit_v16_vs_{opponent}_{seed}.jsonl'
    cmd = [sys.executable, os.path.join(ROOT, 'arena', 'run_battle.py'),
           '--a', 'v16', '--b', opponent, '--seed', str(seed)]
    with open(out, 'w') as fh:
        subprocess.run(cmd, stdout=fh, stderr=subprocess.DEVNULL, check=True)
    lines = [json.loads(l) for l in open(out)]
    turns = [l for l in lines if l.get('t') == 'turn']
    assert turns and turns[-1]['step'] == 718, f'incomplete battle {opponent} {seed}'
    sigs = []
    sales = []
    for t in turns:
        farm = t['farms'][opp_seat]
        act = t['acts'][opp_seat] or {}
        sold = {}
        for o in (act.get('market') or []):
            if isinstance(o, list) and len(o) >= 3 and o and o[0] == 'SELL' and o[1] in IDX:
                sold[o[1]] = sold.get(o[1], 0) + max(1, int(o[2]))
        sigs.append(enc_sig(M._h5_signature(farm)))
        sales.append(enc_sales(sold))
    return {'name': f'{opponent}@{seed}', 'sigs': sigs, 'sales': sales}


def main():
    if '--report' in sys.argv:
        bank = json.load(open(BANK))
        print(f'bank protos: {len(bank)}')
        for p in bank:
            n = sum(1 for s in p['sales'] if s)
            print(f'  {p["name"]:24s} sigs={len(p["sigs"])} sell-steps={n}')
        return
    bank = []
    for opponent, seeds in PLAN:
        for seed in seeds:
            proto = record(opponent, seed)
            bank.append(proto)
            print(f'recorded {proto["name"]}: {len(proto["sigs"])} steps, '
                  f'{sum(1 for s in proto["sales"] if s)} sell-steps', flush=True)
    json.dump(bank, open(BANK, 'w'))
    print(f'wrote {BANK}: {len(bank)} local prototypes')


if __name__ == '__main__':
    main()
