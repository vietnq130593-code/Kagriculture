#!/usr/bin/env python3
"""BAT11 - battery A vs B, N seed, thread-pool."""
import json, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

def run_one(args):
    a, b, seed = args
    try:
        out = subprocess.run(
            ["python3", "arena/run_battle.py", "--a", a, "--b", b, "--seed", str(seed)],
            capture_output=True, text=True, timeout=300, cwd="/home/z/my-project/kaggriculture")
        last = None
        for line in out.stdout.strip().split("\n"):
            if line.strip():
                try: ev = json.loads(line)
                except Exception: continue
                if ev.get("t") == "end": last = ev
        if last is None: return (seed, None, None, None)
        return (seed, last["rewards"][0], last["rewards"][1],
                1 if last["rewards"][0] > last["rewards"][1] else (0 if last["rewards"][0] < last["rewards"][1] else 0.5))
    except Exception:
        return (seed, None, None, None)

def main():
    a, b = sys.argv[1], sys.argv[2]
    s0, n = int(sys.argv[3]), int(sys.argv[4])
    seeds = list(range(s0, s0 + n))
    with ThreadPoolExecutor(max_workers=4) as ex:
        results = list(ex.map(run_one, [(a, b, s) for s in seeds]))
    wins = tot_a = tot_b = n_ok = 0
    print(f"{'seed':>5} {'A':>9} {'B':>9} win")
    for seed, ra, rb, w in sorted(results):
        if ra is None:
            print(f"{seed:>5}  ERROR"); continue
        n_ok += 1
        if w == 1: wins += 1
        tot_a += ra; tot_b += rb
        print(f"{seed:>5} {ra:>9.0f} {rb:>9.0f} {'A' if w==1 else ('B' if w==0 else 'T')}")
    if n_ok:
        print(f"\n{a}: {wins}/{n_ok} ({100*wins/n_ok:.0f}%) TB ${tot_a/n_ok:,.0f} | {b} TB ${tot_b/n_ok:,.0f}")

if __name__ == "__main__":
    main()
