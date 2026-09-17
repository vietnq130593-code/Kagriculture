#!/usr/bin/env python3
"""Assemble v19.py ("REAPER" Phase-1) from v18.py + v19_layer.py.

v19 = v18 byte-exact (embedded verbatim, sha256-verified at exec time)
      + A1 endgame liquidation scheduler + A2 trough throttle
      + A4 strict debt invariant + C1 per-episode state reset.

Run from kaggriculture/:  python3 build_v19.py
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "v18.py"), "rb") as f:
    v18_bytes = f.read()
v18_sha = hashlib.sha256(v18_bytes).hexdigest()

with open(os.path.join(ROOT, "v19_layer.py"), "r", encoding="utf-8") as f:
    layer = f.read()

header = f'''# v19 "REAPER" — Phase 1 (market-timing layer) on the v18 micro-timing core.
# Base: v18.py (K0006, sdy623/jaxa623: V43 parent + 4 market micro-edges) embedded
# verbatim below — sha256 {v18_sha} — executed unmodified in a private namespace.
# Layer (original work, 2026-09-16): A1 endgame liquidation scheduler, A2 trough
# throttle, A4 strict debt invariant, C1 per-episode state reset.
# Evidence base: research/v19/05_V19_DEPLOYMENT_PLAN.md + 06_TOP1_7MATCH_DEEP_ANALYSIS.md
# (7 public episodes of #1 Majkel1337, 5W/2L, parsed 0-mismatch).
import math

_V18_SRC = {v18_bytes!r}

_V18_NS = {{"__name__": "kagg_parent_v18"}}
exec(compile(_V18_SRC.decode("utf-8"), "parent_v18.py", "exec"), _V18_NS)
_V18 = _V18_NS["agent"]
import hashlib as _hashlib
assert _hashlib.sha256(_V18_SRC).hexdigest() == "{v18_sha}", "v18 base corrupted"
del _V18_SRC

'''

with open(os.path.join(ROOT, "v19.py"), "w", encoding="utf-8") as f:
    f.write(header + layer)

size = os.path.getsize(os.path.join(ROOT, "v19.py"))
print(f"v19.py written: {size} bytes (v18 base sha256 {v18_sha[:16]}...)")
