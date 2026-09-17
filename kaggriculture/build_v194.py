#!/usr/bin/env python3
"""Assemble v194.py ("v19.4" lockstep reorder) from v193.py + v194_layer.py.

v194 = v193 byte-exact (embedded verbatim, sha256-verified at exec time)
       + clone-gated best-response SELL ordering (seyit-L2 mechanism):
         permute contiguous SELL runs of 2-6 orders and keep the permutation
         that maximizes own-minus-clone revenue in an exact 2-player lockstep
         replay (engine-exact price model, projected shed, positive-edge-only).

Run from kaggressulture/:  python3 build_v194.py
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "v193.py"), "rb") as f:
    v193_bytes = f.read()
v193_sha = hashlib.sha256(v193_bytes).hexdigest()

with open(os.path.join(ROOT, "v194_layer.py"), "r", encoding="utf-8") as f:
    layer = f.read()

header = f'''# v19.4 — clone-gated lockstep SELL reorder on the v19.3 advance-widen core.
# Base: v193.py embedded verbatim below — sha256 {v193_sha} — executed
# unmodified in a private namespace. Layer (2026-09-17): seyit-L2 port.
import math

_V193_SRC = {v193_bytes!r}

_V193_NS = {{"__name__": "kagg_parent_v193"}}
exec(compile(_V193_SRC.decode("utf-8"), "parent_v193.py", "exec"), _V193_NS)
_V193 = _V193_NS["agent"]
import hashlib as _hashlib
assert _hashlib.sha256(_V193_SRC).hexdigest() == "{v193_sha}", "v193 base corrupted"
del _V193_SRC

'''

with open(os.path.join(ROOT, "v194.py"), "w", encoding="utf-8") as f:
    f.write(header + layer)

size = os.path.getsize(os.path.join(ROOT, "v194.py"))
print(f"v194.py written: {size} bytes (v193 base sha256 {v193_sha[:16]}...)")
