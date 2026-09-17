#!/usr/bin/env python3
"""Assemble v20.py — the FLAT single-namespace build of the v19.4 chain.

The iterative v19.x builds nest each layer inside the previous file's exec'd
blob (v194.py = 1.03 MB, growing quadratically). This flattener concatenates
the same chain into ONE namespace for submission:

    v18.py (V43 parent + jaxa wrappers, byte-exact)
    + v19_layer  (REAPER A1/A4)              — host: _V18
    + v191_layer (v46 opening port)          — host: _V19
    + v192_layer (preguard h21/22)           — host: _V191
    + v193_layer (LOOKAHEAD 3 override)      — host: _V192
    + v194_layer (lockstep reorder)          — host: _V193

Layer code is unchanged except (a) the nested build headers are dropped,
(b) host captures alias the previous block's `agent`, (c) the deep namespace
chains collapse to the flat `_V18_NS`. Behavior must match v194.py exactly
(verified by differential battles: identical final money on identical seeds).

Run from kaggressulture/:  python3 build_v20.py
"""
import hashlib
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def read(name):
    with open(os.path.join(ROOT, name), "r", encoding="utf-8") as f:
        return f.read()


with open(os.path.join(ROOT, "v18.py"), "rb") as f:
    v18_bytes = f.read()
v18_sha = hashlib.sha256(v18_bytes).hexdigest()

v19_layer = read("v19_layer.py")
v191_layer = read("v191_layer.py")

v192_layer = read("v192_layer.py")
v192_layer = v192_layer.replace(
    "_V192_HOST = _V191  # noqa: F821  (v19.1's entry point from the embedded namespace)",
    "_V192_HOST = _V191")
v192_layer = v192_layer.replace(
    '_V192_V43 = _V191_NS["_V19_NS"]["_V18_NS"]["_PARENT_NS"]  # noqa: F821',
    '_V192_V43 = _V18_NS["_PARENT_NS"]')

v193_layer = read("v193_layer.py")
v193_layer = v193_layer.replace(
    '_ns18 = _V192_NS["_V191_NS"]["_V19_NS"]["_V18_NS"]  # noqa: F821',
    "_ns18 = _V18_NS")

v194_layer = read("v194_layer.py")
v194_layer = v194_layer.replace(
    "_V194_HOST = _V193  # noqa: F821  (v19.3's entry point from the embedded namespace)",
    "_V194_HOST = _V193")
v194_layer = v194_layer.replace(
    '_V194_NS18 = _V193_NS["_V192_NS"]["_V191_NS"]["_V19_NS"]["_V18_NS"]  # noqa: F821',
    "_V194_NS18 = _V18_NS")

header = f'''# v20 "SPRINGBOARD" — flat build of the v19.4 chain (submission format).
# Chain (identical logic to v194.py, single namespace):
#   v18 (V43 parent + jaxa micro-edges, byte-exact, sha256 {v18_sha[:16]}…)
#   + v19  REAPER (A1 endgame liquidation + A4 debt invariant)
#   + v19.1 first-turn microstructure (v46 EXP284/293 mechanism port)
#   + v19.2 hour-21/22 shed-overflow preguard (seyit-L1 adapted)
#   + v19.3 sale-advance window 2 -> 3 (v46 _ADV_LOOK)
#   + v19.4 clone-gated lockstep SELL reorder (seyit-L2 port)
# Evidence: research/v19/05 + 06 + 07 + Task-87 batteries (bench/t87_*.json).
import math

_V18_SRC = {v18_bytes!r}

_V18_NS = {{"__name__": "kagg_parent_v18"}}
exec(compile(_V18_SRC.decode("utf-8"), "parent_v18.py", "exec"), _V18_NS)
_V18 = _V18_NS["agent"]
import hashlib as _hashlib
assert _hashlib.sha256(_V18_SRC).hexdigest() == "{v18_sha}", "v18 base corrupted"
del _V18_SRC

'''

parts = [
    header,
    v19_layer,
    "\n\n# ---- flat-chain host alias: v19 REAPER entry ----\n_V19 = agent\n",
    v191_layer,
    "\n\n# ---- flat-chain host alias: v19.1 opening entry ----\n_V191 = agent\n",
    v192_layer,
    "\n\n# ---- flat-chain host alias: v19.2 preguard entry ----\n_V192 = agent\n",
    v193_layer,
    "\n\n# ---- flat-chain host alias: v19.3 advance-widen entry ----\n_V193 = agent\n",
    v194_layer,
    "\n\n# final entry point: `agent` (the v19.4 layer's function, last defined)\n",
]

src = "\n".join(parts)
with open(os.path.join(ROOT, "v20.py"), "w", encoding="utf-8") as f:
    f.write(src)

size = os.path.getsize(os.path.join(ROOT, "v20.py"))
print(f"v20.py written: {size:,} bytes (v18 base sha256 {v18_sha[:16]}...)")
