#!/usr/bin/env python3
"""Diagnose CF runs: channel ledger diff + daily money divergence."""
import json, sys
from collections import defaultdict


def ledger_from(cl, p):
    led = {}
    for (t, pp, op, item, price) in cl:
        if pp != p or op != 'SELL':
            continue
        d = led.setdefault(item, [0, 0.0])
        d[0] += 1
        d[1] += price
    return led


def diag(cf_path, orig_god_path, player=0):
    cf = json.load(open(cf_path))
    og = json.load(open(orig_god_path))
    print(f"=== {cf['label']} ===")
    print(f"delta target {cf['delta']:+,.0f} | opp {cf['opp_delta']:+,.0f}")
    led_cf = cf['ledger_target']
    led_og = ledger_from(og['commit_log'], player)
    items = sorted(set(led_cf) | set(led_og))
    print(f"{'channel':<12} {'orig n/avg/$':>24} {'CF n/avg/$':>24}  diff$")
    for it in items:
        o = led_og.get(it, [0, 0.0])
        c = led_cf.get(it, [0, 0.0])
        print(f"{it:<12} {o[0]:>7}u ${o[1]/max(1,o[0]):>6.1f} ${o[1]:>8,.0f} "
              f"{c[0]:>7}u ${c[1]/max(1,c[0]):>6.1f} ${c[1]:>8,.0f}  {c[1]-o[1]:>+10,.0f}")
    # daily divergence
    print('money divergence by day (target):')
    osn = {s['day']: s['money'][player] for s in og['snapshots'] if s['hour'] == 23}
    prev_gap = 0
    for dd in cf['daily']:
        day = dd['day']
        om = osn.get(day, 0)
        gap = dd['money'][player] - om
        if abs(gap - prev_gap) > 800 or day % 5 == 0:
            print(f"  d{day}: CF ${dd['money'][player]:>9,.0f} orig ${om:>9,.0f} gap {gap:>+9,.0f}")
        prev_gap = gap


if __name__ == '__main__':
    diag(sys.argv[1], sys.argv[2])
