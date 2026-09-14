#!/usr/bin/env python3
"""T80d — instrumented battle runner: exact trade ledger via engine monkeypatch.

Patches kaggle_environments' kaggriculture interpreter so every committed
market unit is logged with (player, op, item, price, step). Player identity
is resolved by farm object id, which _commit_unit receives directly.
Usage: python3 bench/t80_ledger.py A B SEED OUT.jsonl
"""
import io
import json
import os
import runpy
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "arena"))
sys.path.insert(0, os.path.join(ROOT, "bench"))

from kaggle_environments.envs.kaggriculture import kaggriculture as eng  # noqa: E402

LEDGER = []
_orig_commit = eng._commit_unit
_orig_pm = eng._process_market


def main():
    a, b, seed, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]

    def pm_wrapper(state, env):
        obs0 = state[0].observation
        step = obs0.get("step", 0) if hasattr(obs0, "get") else 0
        idmap = {id(f): i for i, f in enumerate(obs0.farms)}

        def commit2(op, item, price, farm, private, market, shed_capacity=100):
            ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
            if ok and op != "BUY_SEED":
                LEDGER.append({"p": idmap.get(id(farm), -1), "op": op,
                               "item": item, "price": price, "step": step})
            return ok

        eng._commit_unit = commit2
        try:
            return _orig_pm(state, env)
        finally:
            eng._commit_unit = _orig_commit

    eng._process_market = pm_wrapper

    sys.argv = ["run_battle.py", "--a", a, "--b", b, "--seed", str(seed)]
    buf = io.StringIO()
    real_stdout = sys.stdout
    sys.stdout = buf
    end = None
    try:
        runpy.run_module("run_battle", run_name="__main__", alter_sys=False)
    finally:
        sys.stdout = real_stdout

    lines = [l for l in buf.getvalue().strip().split("\n") if l.strip()]
    for ln in lines:
        d = json.loads(ln)
        if d.get("t") == "end":
            end = d
    with open(out, "w") as f:
        for e in LEDGER:
            f.write(json.dumps(e) + "\n")
        if end:
            f.write(json.dumps({"t": "end", "rewards": end["rewards"],
                                "winner": end["winner"]}) + "\n")
    if end:
        print(f"{a} vs {b} seed {seed}: rewards={end['rewards']} winner={end['winner']}")
    print(f"ledger: {len(LEDGER)} commits -> {out}")


if __name__ == "__main__":
    main()
