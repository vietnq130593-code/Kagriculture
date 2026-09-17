#!/usr/bin/env python3
"""Assemble v191.py ("v19.1" opening microstructure) from v19.py + v191_layer.py.

v191 = v19 byte-exact (embedded verbatim, sha256-verified at exec time)
       + first-turn microstructure layer (v46-mechanism port):
         step-0 [BUY 7, SELL 2] feed-at-index-0 opening,
         step-1 strip + BUY 30 index-0 attack (cash-gated),
         step-2 sellback into the lifted quotes.

Run from kaggressulture/:  python3 build_v191.py
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "v19.py"), "rb") as f:
    v19_bytes = f.read()
v19_sha = hashlib.sha256(v19_bytes).hexdigest()

with open(os.path.join(ROOT, "v191_layer.py"), "r", encoding="utf-8") as f:
    layer = f.read()

header = f'''# v19.1 — first-turn microstructure layer on the v19 "REAPER" core.
# Base: v19.py (v18 K0006 micro-timing + REAPER A1/A4) embedded verbatim below —
# sha256 {v19_sha} — executed unmodified in a private namespace.
# Layer (original work, 2026-09-17): v46-mechanism opening port (EXP284/EXP293
# published by ahmedberatozer, Apache-2.0; re-implemented, no source copied).
# Evidence: research/v19/07_COMPETITOR_INTEL_V46_SEYIT4.md + Task-87 batteries
# (v19 vs ahmedv46 2W/46L -$396 -> this layer; v19 vs seyit4 46W/2L +$1225 held).
import math

_V19_SRC = {v19_bytes!r}

_V19_NS = {{"__name__": "kagg_parent_v19"}}
exec(compile(_V19_SRC.decode("utf-8"), "parent_v19.py", "exec"), _V19_NS)
_V19 = _V19_NS["agent"]
import hashlib as _hashlib
assert _hashlib.sha256(_V19_SRC).hexdigest() == "{v19_sha}", "v19 base corrupted"
del _V19_SRC

'''

with open(os.path.join(ROOT, "v191.py"), "w", encoding="utf-8") as f:
    f.write(header + layer)

size = os.path.getsize(os.path.join(ROOT, "v191.py"))
print(f"v191.py written: {size} bytes (v19 base sha256 {v19_sha[:16]}...)")
