#!/usr/bin/env python3
"""Build v24 knob variants (b/c/d/e) for the 6-seed sweep.
    v24b: HOARD_CAP 40            (shed-risk variant)
    v24c: RELEASE_P 18            (softer release)
    v24d: HOARD_CAP 40 + REL 18
    v24e: GATE_P 15               (wider garbage net, still deep-garbage)
"""
import os

ROOT = "/home/z/my-project/kag Agriculture"
ROOT = "/home/z/my-project/kaggriculture"


def build(name, patches):
    v20 = open(f"{ROOT}/v20.py", encoding="utf-8").read()
    layer = open(f"{ROOT}/v24_layer.py", encoding="utf-8").read()
    for old, new in patches:
        assert layer.count(old) == 1, (name, old, layer.count(old))
        layer = layer.replace(old, new)
    MARKER = "# ---- kaggle_environments entry-point fix (Task 88) ----"
    cut = v20.find(MARKER)
    base = v20[:cut].rstrip() + "\n"
    header = f"# v24 variant {name} (knob sweep, Task 92)\n"
    tail = f'''

# ---- kaggle_environments entry-point fix (Task 88 pattern) ----
_V24X_ENTRY = agent
del agent


def agent(observation, configuration=None):
    return _V24X_ENTRY(observation, configuration)


agent.telemetry = _V24_TELEMETRY
'''
    src = header + base + "\n\n" + layer + tail
    out = f"{ROOT}/{name}.py"
    with open(out, "w", encoding="utf-8") as f:
        f.write(src)
    print("built", out, len(src))


build("v24b", [("_V24_HOARD_CAP = 24", "_V24_HOARD_CAP = 40")])
build("v24c", [("_V24_RELEASE_P = 25", "_V24_RELEASE_P = 18")])
build("v24d", [("_V24_HOARD_CAP = 24", "_V24_HOARD_CAP = 40"),
               ("_V24_RELEASE_P = 25", "_V24_RELEASE_P = 18")])
build("v24e", [("_V24_GATE_P = 10", "_V24_GATE_P = 15")])
