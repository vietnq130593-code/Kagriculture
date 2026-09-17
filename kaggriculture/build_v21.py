#!/usr/bin/env python3
"""Assemble v21.py — the FLAT single-namespace build of the v19.4 chain + v21 layer.

    v20.py chain (v18 + v19 + v191 + v192 + v193 + v194, verified flat build)
    + v21_layer (trough-banker sell-gating)                — host: agent (v194)

Build strategy: read the verified v20.py, cut it at the Task-88 entry-point-fix
marker, append the v21 layer (host alias rewired to the flat-chain `agent`),
and re-apply the same entry-point fix pattern (del + re-def so
get_last_callable() picks the REAL agent).

Run from the project root:  python3 build_v21.py
"""
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as f:
        return f.read()


v20_src = read("v20.py")
v21_layer = read("v21_layer.py")

# rewire the layer host to the flat chain's current agent (v19.4)
v21_layer = v21_layer.replace(
    "_V21_HOST = _V194  # noqa: F821  (v19.4's entry point from the embedded namespace)",
    "_V21_HOST = agent  # noqa: F821  (flat chain: v19.4's entry point)")

MARKER = "# ---- kaggle_environments entry-point fix (Task 88) ----"
cut = v20_src.find(MARKER)
assert cut > 0, "entry-fix marker not found in v20.py"
base_chain = v20_src[:cut].rstrip() + "\n"

header = '''# v21 "TROUGH-BANKER" — flat build of the v19.4 chain + v21 layer.
# Chain (identical logic to v194.py + v21_layer.py, single namespace):
#   v18 (V43 parent + jaxa micro-edges, byte-exact)
#   + v19  REAPER (A1 endgame liquidation + A4 debt invariant)
#   + v19.1 first-turn microstructure (v46 EXP284/293 mechanism port)
#   + v19.2 hour-21/22 shed-overflow preguard (seyit-L1 adapted)
#   + v19.3 sale-advance window 2 -> 3 (v46 _ADV_LOOK)
#   + v19.4 clone-gated lockstep SELL reorder (seyit-L2 port)
#   + v21   trough-banker sell-gating (WOOL/STRAWBERRY/MELON crash banking)
# Evidence: Task-89 probes (8-seed price trajectories) + battery t89_*.
'''

tail = '''

# ---- kaggle_environments entry-point fix (Task 88 pattern) ----
# del + re-def re-inserts `agent` at the END of the namespace so
# get_last_callable() (kaggle_environments/agent.py L64) picks the REAL agent
# entry, not a helper defined later in the file.
_V21_ENTRY = agent
del agent


def agent(observation, configuration=None):
    return _V21_ENTRY(observation, configuration)


agent.telemetry = _V21_TELEMETRY
'''

src = header + base_chain + "\n\n" + v21_layer + tail

out_path = os.path.join(ROOT, "v21.py")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(src)

size = os.path.getsize(out_path)
print(f"v21.py written: {size:,} bytes")

# Task 88: verify the kaggle_environments harness picks the REAL agent entry.
from kaggle_environments.agent import get_last_callable

fn = get_last_callable(src, path=out_path)
assert fn is not None and getattr(fn, "__name__", "") == "agent", (
    f"entry-point check FAILED: get_last_callable -> {fn!r}")
print("entry-point check OK: get_last_callable -> agent")
