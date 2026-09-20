#!/usr/bin/env python3
"""Task 110 grid search: crash-dump layer parameter combos on protocol seeds.

Runs each combo on seeds 100-104 (seat 0 only — seat symmetry verified
byte-exact in t102 data), reports per-seed margins and win counts.
Combos: DUMPABLE subsets x milk gates x crash ratio.
"""
import itertools
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = open(os.path.join(ROOT, "v27a.py")).read()

SUBSETS = [
    ("ALL", '("MILK", "STRAWBERRY", "MELON", "WOOL", "EGG", "CARROT", "TOMATO")'),
    ("SMW", '("STRAWBERRY", "MELON", "WOOL")'),
    ("SM", '("STRAWBERRY", "MELON")'),
    ("SW", '("STRAWBERRY", "WOOL")'),
    ("MSM", '("MILK", "STRAWBERRY", "MELON")'),
    ("MS", '("MILK", "STRAWBERRY")'),
    ("MW", '("MILK", "WOOL")'),
    ("MM", '("MILK", "MELON")'),
    ("MWL", '("MILK", "MELON", "WOOL")'),
    ("SMWC", '("STRAWBERRY", "MELON", "WOOL", "CARROT")'),
    ("MWMS", '("MILK", "WOOL", "MELON", "STRAWBERRY", "CARROT")'),
    ("S", '("STRAWBERRY",)'),
]
MILK_GATES = [
    ("none", None),
    ("p60", 'if item == "MILK" and prices.get("MILK", 0) < 60:\n                continue'),
    ("d20", 'if item == "MILK" and day >= 20:\n                continue'),
]
RATIOS = [0.88, 0.95]

OLD_DUMP = '_V27_DUMPABLE = ("MILK", "STRAWBERRY", "MELON", "WOOL", "EGG", "CARROT", "TOMATO")'
OLD_LOOP = '''        for item in sorted(crashing):
            have = _v27_int(shed.get(item))
            if have <= 0:
                continue'''


def build(name, subset_expr, milk_gate, ratio):
    src = BASE.replace(OLD_DUMP, "_V27_DUMPABLE = %s" % subset_expr)
    src = src.replace("_V27_CRASH_RATIO = 0.88", "_V27_CRASH_RATIO = %s" % ratio)
    if milk_gate:
        src = src.replace(OLD_LOOP, OLD_LOOP.replace("continue", milk_gate + "\n            have placeholder"))
        # simpler: insert gate line after the for
        src = src.replace(OLD_LOOP, OLD_LOOP.replace(
            '            have = _v27_int(shed.get(item))',
            '            ' + milk_gate + '\n            have = _v27_int(shed.get(item))'))
    path = os.path.join(ROOT, "v27gs_%s.py" % name)
    open(path, "w").write(src)
    return path


def run_one(args):
    agent_path, seed, reg_name = args
    cmd = [sys.executable, os.path.join(ROOT, "arena", "run_battle.py"),
           "--a", reg_name, "--b", "thomast2945", "--seed", str(seed)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=ROOT)
        for line in reversed((p.stdout or "").strip().splitlines()):
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("t") == "end":
                r0, r1 = obj["rewards"]
                return {"seed": seed, "margin": r0 - r1, "winner": obj.get("winner")}
    except Exception:
        pass
    return {"seed": seed, "margin": None, "winner": None}


def main():
    import sys as _sys
    batch = int(_sys.argv[1]) if len(_sys.argv) > 1 else None
    all_combos = []
    for (sname, sexpr), (gname, gate), ratio in itertools.product(SUBSETS, MILK_GATES, RATIOS):
        cname = "%s_%s_r%d" % (sname, gname, int(ratio * 100))
        path = build(cname, sexpr, gate, ratio)
        all_combos.append((cname, path))
    combos = all_combos if batch is None else all_combos[batch * 9:(batch + 1) * 9]

    # register all
    reg = open(os.path.join(ROOT, "arena", "run_battle.py")).read()
    marker = '''    "v27k": (os.path.join(ROOT, "v27k.py"), "agent"),
}'''
    lines = ["    \"v27gs_%s\": (os.path.join(ROOT, \"v27gs_%s.py\"), \"agent\")," % (c, c) for c, _ in combos]
    reg = reg.replace(marker, marker[:-2] + "\n" + "\n".join(lines) + "\n}")
    open(os.path.join(ROOT, "arena", "run_battle.py"), "w").write(reg)

    t0 = time.time()
    results = {}
    # run combos sequentially; 5 matches each, 2 parallel threads
    with ThreadPoolExecutor(max_workers=2) as ex:
        for cname, path in combos:
            jobs = [(path, s, "v27gs_%s" % cname) for s in (100, 101, 102, 103, 104)]
            outs = list(ex.map(run_one, jobs))
            results[cname] = outs
            wins = sum(1 for o in outs if (o["margin"] or 0) > 0)
            margins = [o["margin"] for o in outs]
            print("%-18s wins=%d/5 margins=%s mean=%s  [%.0fs]" % (
                cname, wins, [None if m is None else round(m) for m in margins],
                round(sum(m for m in margins if m is not None) / 5) if all(m is not None for m in margins) else "ERR",
                time.time() - t0), flush=True)

    # summary sorted by wins then mean
    print("\n=== TOP COMBOS ===")
    scored = []
    for cname, outs in results.items():
        margins = [o["margin"] for o in outs if o["margin"] is not None]
        if len(margins) == 5:
            wins = sum(1 for m in margins if m > 0)
            mean = sum(margins) / 5
            scored.append((wins, mean, cname, margins))
    scored.sort(key=lambda x: (-x[0], -x[1]))
    for wins, mean, cname, margins in scored[:15]:
        print("%-18s wins=%d/5 mean=%+d margins=%s" % (cname, wins, round(mean), [round(m) for m in margins]))

    outf = os.path.join(ROOT, "bench", "t110_gridsearch_b%s.json" % (batch if batch is not None else "all"))
    json.dump({c: r for c, r in results.items()}, open(outf, "w"), indent=1)
    print("saved", outf)


if __name__ == "__main__":
    main()
