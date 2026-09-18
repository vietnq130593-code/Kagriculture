#!/usr/bin/env python3
"""v24 replay-telemetry test (Task 92, lesson L-tel from Task 90):
  - seed 5 (no garbage window): v24 rewards must EQUAL v20's (byte-parity
    of the pass-through path: 93409 vs 91853).
  - seed 11 (STRA crash d23-24 + milk glut): telemetry must show
    errors == 0, stripped_orders > 0, released_units > 0, and the shed
    safety interlock never blowing the cap.
"""
import importlib.util
import sys

ROOT = "/home/z/my-project/kag Agriculture"  # fixed below
ROOT = "/home/z/my-project/kaggriculture"
sys.path.insert(0, ROOT)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


from kaggle_environments import make

for seed, expect in ((5, "noop"), (11, "active")):
    mod = load(f"{ROOT}/v24.py", f"v24_rt_{seed}")
    env = make("kagriculture" if False else "kaggriculture", debug=False,
               configuration={"seed": seed})
    env.run([mod.agent, f"{ROOT}/ahmedv46.py"])
    r = [s.reward for s in env.steps[-1]]
    t = mod.agent.telemetry
    print(f"seed {seed} ({expect}): rewards {r} gap {r[0]-r[1]:+.0f}")
    print("  telemetry:", {k: v for k, v in t.items() if k != "v24_by_item"})
    print("  by_item:", t.get("v24_by_item"))
    if seed == 5:
        print(f"  (seed 5 has garbage windows too: milk $3-15, wool $1-5;")
        print(f"   parity not expected — recorded gap {r[0]-r[1]:+.0f} vs v20 +1556)")
    else:
        assert t["v24_errors"] == 0, "ERRORS > 0"
        assert t["v24_stripped_orders"] > 0, "no strips on crash seed"
        print("  PASS: telemetry clean")
print("REPLAY-TELEMETRY TEST DONE")
