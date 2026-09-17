#!/usr/bin/env python3
"""Assemble v192.py ("v19.2" preguard) from v191.py + v192_layer.py.

v192 = v191 byte-exact (embedded verbatim, sha256-verified at exec time)
       + hour-21/22 shed-overflow preguard (seyit-L1 mechanism, adapted):
         project end-of-day shed+carried with the V43 chassis helpers and
         sell the excess from shed stock (price-desc, gated item list) so
         the carried feed wheat survives the hour-23 deposit and the sale
         front-runs the V44-family's hour-23 guard dumps.

Run from kaggressulture/:  python3 build_v192.py
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "v191.py"), "rb") as f:
    v191_bytes = f.read()
v191_sha = hashlib.sha256(v191_bytes).hexdigest()

with open(os.path.join(ROOT, "v192_layer.py"), "r", encoding="utf-8") as f:
    layer = f.read()

header = f'''# v19.2 — hour-21/22 shed-overflow preguard on the v19.1 opening core.
# Base: v191.py (v19 + first-turn microstructure) embedded verbatim below —
# sha256 {v191_sha} — executed unmodified in a private namespace.
# Layer (original work, 2026-09-17): seyit-L1 mechanism port, item list adapted
# to the V43 shed mix (WHEAT 69% + EGG 16% at h21/22; CARROT/FERTILIZER excluded).
# Evidence: research/v19/07_COMPETITOR_INTEL_V46_SEYIT4.md + Task-87 battle
# forensics (~90-116 units/player-game destroyed at hour-23 overflow, 96% WHEAT,
# $22-42/unit — ~$3-7K/game vaporized; no V43 guard exists, V44 added EXP-154).
import math

_V191_SRC = {v191_bytes!r}

_V191_NS = {{"__name__": "kagg_parent_v191"}}
exec(compile(_V191_SRC.decode("utf-8"), "parent_v191.py", "exec"), _V191_NS)
_V191 = _V191_NS["agent"]
import hashlib as _hashlib
assert _hashlib.sha256(_V191_SRC).hexdigest() == "{v191_sha}", "v191 base corrupted"
del _V191_SRC

'''

with open(os.path.join(ROOT, "v192.py"), "w", encoding="utf-8") as f:
    f.write(header + layer)

size = os.path.getsize(os.path.join(ROOT, "v192.py"))
print(f"v192.py written: {size} bytes (v191 base sha256 {v191_sha[:16]}...)")
