#!/usr/bin/env python3
"""t78_verify_h8.py — run one instrumented game v16h8 (imported module) vs v15,
then inspect _H8_STATE / _H8_REPORT to confirm detector + overlay behavior."""
import os
import sys

ROOT = "/home/z/my-project/kaggriculture"
sys.path.insert(0, ROOT)
import importlib.util

spec = importlib.util.spec_from_file_location("_v16h8_mod", f"{ROOT}/v16h8.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["_v16h8_mod"] = mod
spec.loader.exec_module(mod)

wrap = "/tmp/t78_h8_wrap.py"
open(wrap, "w").write(
    "import sys\n"
    "if '_v16h8_mod' not in sys.modules:\n"
    "    import importlib.util\n"
    "    _spec = importlib.util.spec_from_file_location('_v16h8_mod', '/home/z/my-project/kaggriculture/v16h8.py')\n"
    "    _m = importlib.util.module_from_spec(_spec)\n"
    "    sys.modules['_v16h8_mod'] = _m\n"
    "    _spec.loader.exec_module(_m)\n"
    "else:\n"
    "    _m = sys.modules['_v16h8_mod']\n"
    "def agent(obs, configuration=None):\n"
    "    return _m.agent(obs, configuration)\n"
)

from kaggle_environments import make

for seed in (350, 351):
    for arrangement in (0, 1):
        env = make("kaggriculture", debug=False, configuration={"seed": seed})
        agents = [wrap, f"{ROOT}/v15.py"] if arrangement == 0 else [f"{ROOT}/v15.py", wrap]
        mod._H8_STATE.update(prev={0: None, 1: None}, on={0: False, 1: False}, active=False)
        mod._H8_REPORT.update(triggered={0: 0, 1: 0}, extra_units=0)
        env.run(agents)
        r0 = float(env.steps[-1][0].reward or 0)
        r1 = float(env.steps[-1][1].reward or 0)
        h8_seat = 0 if arrangement == 0 else 1
        print(f"seed {seed} arr{arrangement}: rewards=({r0:.0f},{r1:.0f}) "
              f"h8seat={h8_seat} triggered={mod._H8_REPORT['triggered']} "
              f"on={mod._H8_STATE['on']} extra_units={mod._H8_REPORT['extra_units']}")
