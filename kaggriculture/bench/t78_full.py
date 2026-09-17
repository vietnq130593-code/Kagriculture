#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SEEDS = "350-354"
PAIRS = [
    ("v16h8", "v13"),
    ("v16h8", "kme3"),
    ("v16h8", "kme3v10"),
    ("v16h8", "aurax"),
    ("v16h8", "kawashigi"),
    ("v16h8", "indark_e776"),
    ("v16h8", "v16h5"),
    ("v16h8", "v16h57"),
]


def out_path(a, b):
    return os.path.join(HERE, f"t78_{a}_vs_{b}.json")


def main():
    t0 = time.time()
    for a, b in PAIRS:
        p = out_path(a, b)
        if os.path.exists(p):
            try:
                old = json.load(open(p))
                if old.get("seeds") == SEEDS and not old.get("fails"):
                    continue
            except Exception:
                pass
        cmd = [sys.executable, os.path.join(HERE, "battery.py"), a, b,
               "--seeds", SEEDS, "--out", os.path.basename(p), "--jobs", "2",
               "--tag", "t78f"]
        subprocess.run(cmd, cwd=ROOT)
    print(f"full battery done in {time.time() - t0:.0f}s", flush=True)
    for a, b in PAIRS:
        p = out_path(a, b)
        if os.path.exists(p):
            r = json.load(open(p))
            print(f"{r['a']:6s} vs {r['b']:12s} {r['wins']:2d}/{r['games']:2d} "
                  f"gap {r['gap']:+9,.1f} worst {r['worst_ratio']:.4f}")


if __name__ == "__main__":
    main()
