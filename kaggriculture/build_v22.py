#!/usr/bin/env python3
"""Assemble v22.py — flat single-namespace build of the v19.4 chain + v22
MILK-BANKER layer (host = the v20 chain's entry point).

    v20.py chain (v18 + v19 + v191 + v192 + v193 + v194, verified flat build)
    + v22_layer (milk recovery banker)                   — host: agent (v20)

Isolation choice: v22 chains on v20 (NOT v21) so probe deltas vs the v20
baseline measure the milk layer alone (v21's wool banker was ~+$9 noise).

Run from the project root:  python3 build_v22.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as f:
        return f.read()


v20_src = read("v20.py")
v22_layer = read("v22_layer.py")

v22_layer = v22_layer.replace(
    "_V22_HOST = agent  # noqa: F821  (flat chain: v19.4's entry point)",
    "_V22_HOST = agent  # noqa: F821  (flat chain: v20 = v19.4's entry point)")

MARKER = "# ---- kaggle_environments entry-point fix (Task 88) ----"
cut = v20_src.find(MARKER)
assert cut > 0, "entry-fix marker not found in v20.py"
base_chain = v20_src[:cut].rstrip() + "\n"

header = '''# v22 "MILK-BANKER" — flat build of the v19.4 chain + v22 layer.
# Chain (identical logic to v20.py + v22_layer.py, single namespace):
#   v18 (V43 parent + jaxa micro-edges, byte-exact)
#   + v19  REAPER (A1 endgame liquidation + A4 debt invariant)
#   + v19.1 first-turn microstructure (v46 EXP284/293 mechanism port)
#   + v19.2 hour-21/22 shed-overflow preguard (seyit-L1 adapted)
#   + v19.3 sale-advance window 2 -> 3 (v46 _ADV_LOOK)
#   + v19.4 clone-gated lockstep SELL reorder (seyit-L2 port)
#   + v22   milk recovery banker (2-milk-shop seed endgame banking,
#           walk-aware chunked re-entry into price recoveries)
# Evidence: Task-90 8-seed milk market probe (reconstruction milk_sim /
# milk_reconstruct2) + battery t90_*.
'''

tail = '''

# ---- kaggle_environments entry-point fix (Task 88 pattern) ----
# del + re-def re-inserts `agent` at the END of the namespace so
# get_last_callable() (kaggle_environments/agent.py L64) picks the REAL agent
# entry, not a helper defined later in the file.
_V22_ENTRY = agent
del agent


def agent(observation, configuration=None):
    return _V22_ENTRY(observation, configuration)


agent.telemetry = _V22_TELEMETRY
'''

src = header + base_chain + "\n\n" + v22_layer + tail

out_path = os.path.join(ROOT, "v22.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(src)

size = os.path.getsize(out_path)
print(f"v22.py written: {size:,} bytes")

# Task 88: verify the kaggle_environments harness picks the REAL agent entry.
from kaggle_environments.agent import get_last_callable

fn = get_last_callable(src, path=out_path)
assert fn is not None and getattr(fn, "__name__", "") == "agent", (
    f"entry-point check FAILED: get_last_callable -> {fn!r}")
print("entry-point check OK: get_last_callable -> agent")
