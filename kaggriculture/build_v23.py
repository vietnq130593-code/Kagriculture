#!/usr/bin/env python3
"""Assemble v23.py — the v20 flat chain + v23 GOOSE ENGINE layer.

    v20.py chain (v18 + v19 + v191 + v192 + v193 + v194, verified flat build)
    + v23_layer (EGG/GOOSE production planner)      — host: agent (v20)

Build strategy: read the verified v20.py, cut it at the Task-88 entry-point-fix
marker, append the v23 layer (host alias rewired to the flat-chain `agent`),
and re-apply the same entry-point fix pattern (del + re-def so
get_last_callable() picks the REAL agent).

Run from the project root:  python3 build_v23.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as f:
        return f.read()


v20_src = read("v20.py")
v23_layer = read("v23_layer.py")

# rewire the layer host to the flat chain's current agent (v20)
v23_layer = v23_layer.replace(
    "_V23_HOST = agent  # noqa: F821  (flat chain: v20's entry point)",
    "_V23_HOST = agent  # noqa: F821  (flat chain: v20's entry point)")

MARKER = "# ---- kaggle_environments entry-point fix (Task 88) ----"
cut = v20_src.find(MARKER)
assert cut > 0, "entry-fix marker not found in v20.py"
base_chain = v20_src[:cut].rstrip() + "\n"

header = '''# v23 "GOOSE ENGINE" — flat build of the v19.4 chain + v23 EGG/GOOSE planner.
# Chain (identical logic to v20.py + v23_layer.py, single namespace):
#   v18 (V43 parent + jaxa micro-edges, byte-exact)
#   + v19  REAPER (A1 endgame liquidation + A4 debt invariant)
#   + v19.1 first-turn microstructure (v46 EXP284/293 mechanism port)
#   + v19.2 hour-21/22 shed-overflow preguard (seyit-L1 adapted)
#   + v19.3 sale-advance window 2 -> 3 (v46 _ADV_LOOK)
#   + v19.4 clone-gated lockstep SELL reorder (seyit-L2 port)
#   + v23   GOOSE ENGINE: EGG/GOOSE production planner (own architecture:
#           NE coop zone, receipt-claimed hands, wheat feed contract, greedy
#           stateless sweep; fail-open to the pure v20 core)
# Evidence: doc 10 EGG discovery + v23_resource_probe (seed-3 calibration).
'''

tail = '''

# ---- kaggle_environments entry-point fix (Task 88 pattern) ----
# del + re-def re-inserts `agent` at the END of the namespace so
# get_last_callable() (kaggle_environments/agent.py L64) picks the REAL agent
# entry, not a helper defined later in the file.
_V23_ENTRY = agent
del agent


def agent(observation, configuration=None):
    return _V23_ENTRY(observation, configuration)


agent.telemetry = _V23_TEL
'''

src = header + base_chain + "\n\n" + v23_layer + tail

out_path = os.path.join(ROOT, "v23.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(src)

# land-only variant for the A/B: same SE buy, no goose engine
src_land = src.replace('_V23_MODE = "goose"', '_V23_MODE = "land"')
out_land = os.path.join(ROOT, "v23l.py")
with open(out_land, "w", encoding="utf-8") as f:
    f.write(src_land)

size = os.path.getsize(out_path)
print(f"v23.py written: {size:,} bytes")
print(f"v23l.py written: {os.path.getsize(out_land):,} bytes (land-only A/B)")

# Task 88: verify the kaggle_environments harness picks the REAL agent entry.
from kaggle_environments.agent import get_last_callable

fn = get_last_callable(src, path=out_path)
assert fn is not None and getattr(fn, "__name__", "") == "agent", (
    f"entry-point check FAILED: get_last_callable -> {fn!r}")
fnl = get_last_callable(src_land, path=out_land)
assert fnl is not None and getattr(fnl, "__name__", "") == "agent", (
    f"entry-point check FAILED (land): get_last_callable -> {fnl!r}")
print("entry-point check OK: get_last_callable -> agent (both)")
