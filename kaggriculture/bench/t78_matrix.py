#!/usr/bin/env python3
"""t78_matrix.py — H8 battery driver (Task 78).

7 pairings on fresh seeds 350-354 (both seats = 10 games each):
  v16h8 vs {v16, v15, v14, kme3v39}   (H8 effect + parent veto)
  v16   vs {v15, v14, kme3v39}        (same-seed baselines for tie comparison)
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

SEEDS = "350-354"
PAIRS = [
    ("v16h8", "v16"),
    ("v16h8", "v15"),
    ("v16h8", "v14"),
    ("v16h8", "kme3v39"),
    ("v16", "v15"),
    ("v16", "v14"),
    ("v16", "kme3v39"),
]


def out_path(a, b):
    return os.path.join(HERE, f"t78_{a}_vs_{b}.json")


def main():
    t0 = time.time()
    done = 0
    for a, b in PAIRS:
        p = out_path(a, b)
        if os.path.exists(p):
            try:
                old = json.load(open(p))
                if old.get("seeds") == SEEDS and not old.get("fails"):
                    done += 1
                    continue
            except Exception:
                pass
        cmd = [sys.executable, os.path.join(HERE, "battery.py"), a, b,
               "--seeds", SEEDS, "--out", os.path.basename(p), "--jobs", "2",
               "--tag", "t78"]
        print(f"[{done + 1}/{len(PAIRS)}] {' '.join(cmd[2:4])} ...", flush=True)
        subprocess.run(cmd, cwd=ROOT)
        done += 1
    print(f"matrix complete: {done} pairings, {time.time() - t0:.0f}s", flush=True)
    for a, b in PAIRS:
        p = out_path(a, b)
        if os.path.exists(p):
            r = json.load(open(p))
            ties = sum(1 for row in r["rows"]
                       if row["a_seat0"] == row["b_seat1"] and row["a_seat1"] == row["b_seat0"])
            half = sum(1 for row in r["rows"] if row["a_seat0"] == row["b_seat1"]) + \
                   sum(1 for row in r["rows"] if row["a_seat1"] == row["b_seat0"])
            print(f"{r['a']:6s} vs {r['b']:9s} {r['wins']:2d}/{r['games']:2d} "
                  f"gap {r['gap']:+9,.0f} worst {r['worst_ratio']:.4f} "
                  f"seat-ties {half} full-ties {ties}")


if __name__ == "__main__":
    main()
