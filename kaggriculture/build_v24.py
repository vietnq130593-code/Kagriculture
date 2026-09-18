#!/usr/bin/env python3
"""Assemble v24.py — flat single-namespace build of the v19.4 chain + v24
GARBAGE-THROTTLE layer (host = the v20 chain's entry point).

    v20.py chain (v18 + v19 + v191 + v192 + v193 + v194, verified flat build)
    + v24_layer (garbage-price throttle: strip SELL < $10, hold <= 24u,
                 release chunk <= 12 at p >= $25, REAPER d27+ untouched)

Run from the project root:  python3 build_v24.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as f:
        return f.read()


v20_src = read("v20.py")
v24_layer = read("v24_layer.py")

MARKER = "# ---- kaggle_environments entry-point fix (Task 88) ----"
cut = v20_src.find(MARKER)
assert cut > 0, "entry-fix marker not found in v20.py"
base_chain = v20_src[:cut].rstrip() + "\n"

header = '''# v24 "GARBAGE-THROTTLE" — flat build of the v19.4 chain + v24 layer.
# Chain (identical logic to v20.py + v24_layer.py, single namespace):
#   v18 (V43 parent + jaxa micro-edges, byte-exact)
#   + v19  REAPER (A1 endgame liquidation + A4 debt invariant)
#   + v19.1 first-turn microstructure (v46 EXP284/293 mechanism port)
#   + v19.2 hour-21/22 shed-overflow preguard (seyit-L1 adapted)
#   + v19.3 sale-advance window 2 -> 3 (v46 _ADV_LOOK)
#   + v19.4 clone-gated lockstep SELL reorder (seyit-L2 port)
#   + v24   garbage-price throttle (Task 92 H2 peak pricing: re-time SELLs
#           of existing output; strip true-garbage (<$10) windows, capped
#           24-unit hoard, chunked release at >=$25; no input changes)
# Evidence: Task-92 probes (h2_timing_probe, h2_endgame_probe,
#           h2_hoard_forensic) + battery t92_*.
'''

tail = '''

# ---- kaggle_environments entry-point fix (Task 88 pattern) ----
# del + re-def re-inserts `agent` at the END of the namespace so
# get_last_callable() (kaggle_environments/agent.py L64) picks the REAL agent
# entry, not a helper defined later in the file.
_V24_ENTRY = agent
del agent


def agent(observation, configuration=None):
    return _V24_ENTRY(observation, configuration)


agent.telemetry = _V24_TELEMETRY
'''

src = header + base_chain + "\n\n" + v24_layer + tail

out_path = os.path.join(ROOT, "v24.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(src)
print("written", out_path, len(src), "bytes")

# ---- build-time verification (Task 88 lesson) ----
import importlib.util

spec = importlib.util.spec_from_file_location("v24_check", out_path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from kaggle_environments import agent as kagent

fn = kagent.get_last_callable(src)
assert fn is not None, "get_last_callable returned None"
assert fn.__name__ == "agent", f"entry point wrong: {fn.__name__}"
print("entry-point verify OK (get_last_callable -> agent)")
assert hasattr(mod, "agent") and hasattr(mod.agent, "telemetry")
print("telemetry attach OK:", sorted(mod.agent.telemetry.keys())[:6])
