#!/usr/bin/env python3
"""Assemble v193.py ("v19.3" advance-widen) from v192.py + v193_layer.py.

v193 = v192 byte-exact (embedded verbatim, sha256-verified at exec time)
       + sale-advance window widened 2 -> 3 turns (v46's _ADV_LOOK=3) via a
         one-time namespace override of the embedded v18's LOOKAHEAD.

Run from kaggressulture/:  python3 build_v193.py
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(ROOT, "v192.py"), "rb") as f:
    v192_bytes = f.read()
v192_sha = hashlib.sha256(v192_bytes).hexdigest()

with open(os.path.join(ROOT, "v193_layer.py"), "r", encoding="utf-8") as f:
    layer = f.read()

header = f'''# v19.3 — sale-advance window 2 -> 3 turns on the v19.2 preguard core.
# Base: v192.py embedded verbatim below — sha256 {v192_sha} — executed
# unmodified in a private namespace. Layer (2026-09-17): LOOKAHEAD override.
import math

_V192_SRC = {v192_bytes!r}

_V192_NS = {{"__name__": "kagg_parent_v192"}}
exec(compile(_V192_SRC.decode("utf-8"), "parent_v192.py", "exec"), _V192_NS)
_V192 = _V192_NS["agent"]
import hashlib as _hashlib
assert _hashlib.sha256(_V192_SRC).hexdigest() == "{v192_sha}", "v192 base corrupted"
del _V192_SRC

'''

with open(os.path.join(ROOT, "v193.py"), "w", encoding="utf-8") as f:
    f.write(header + layer)

size = os.path.getsize(os.path.join(ROOT, "v193.py"))
print(f"v193.py written: {size} bytes (v192 base sha256 {v192_sha[:16]}...)")
