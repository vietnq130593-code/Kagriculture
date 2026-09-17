#!/usr/bin/env python3
"""Paired battery runner — T1/T3 gates for v19 acceptance (05 §4).

Runs N seeds × both seats of `--new` vs `--base` through the official engine
(run_battle.py), aggregates per-seed PAIRED margins (sum of both seats) and
single-seat margins, and reports mean / median / worst / winrate plus a
bootstrap 95% CI of the mean.

Usage:
  python3 arena/battery.py --new v19 --base v18 --seeds 24 --tag t85_p1_t1
  python3 arena/battery.py --new v19 --base v18 --seeds 64 --tag t85_p1_g1
"""
import argparse
import json
import os
import random
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "arena", "run_battle.py")
OUTDIR = os.path.join(ROOT, "bench")
os.makedirs(OUTDIR, exist_ok=True)


def run_one(args):
    new, base, seed, seat = args
    # seat 0: new plays player 0; seat 1: new plays player 1 (swapped)
    a, b = (new, base) if seat == 0 else (base, new)
    cmd = [sys.executable, RUNNER, "--a", a, "--b", b, "--seed", str(seed)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                           cwd=ROOT)
        end = None
        for line in reversed((p.stdout or "").strip().splitlines()):
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("t") == "end":
                end = obj
                break
        if end is None:
            return {"seed": seed, "seat": seat, "error": p.stderr[-400:] if p.stderr else "no end line"}
        r0, r1 = end["rewards"]
        new_reward = r0 if seat == 0 else r1
        base_reward = r1 if seat == 0 else r0
        return {"seed": seed, "seat": seat, "new": new_reward, "base": base_reward,
                "margin": round(new_reward - base_reward, 2),
                "wallS": end.get("wallS")}
    except subprocess.TimeoutExpired:
        return {"seed": seed, "seat": seat, "error": "timeout"}


def bootstrap_ci(margins, n=10000, alpha=0.05, seed=13):
    if not margins:
        return None
    rng = random.Random(seed)
    means = []
    m = margins
    k = len(m)
    for _ in range(n):
        s = sum(m[rng.randrange(k)] for _ in range(k))
        means.append(s / k)
    means.sort()
    lo = means[int((alpha / 2) * n)]
    hi = means[int((1 - alpha / 2) * n)]
    return round(lo, 1), round(hi, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--seeds", type=int, default=24, help="number of seeds (1..N)")
    ap.add_argument("--seed-start", type=int, default=1)
    ap.add_argument("--tag", default="battery")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4) - 1))
    args = ap.parse_args()

    jobs = [(args.new, args.base, s, seat)
            for s in range(args.seed_start, args.seed_start + args.seeds)
            for seat in (0, 1)]
    results = []
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(run_one, j): j for j in jobs}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            done += 1
            if done % 8 == 0 or done == len(jobs):
                print(f"  {done}/{len(jobs)} battles done ({time.time()-t0:.0f}s)", flush=True)

    errs = [r for r in results if "error" in r]
    ok = [r for r in results if "error" not in r]
    margins = [r["margin"] for r in ok]
    # paired per-seed margin: sum of both seats
    per_seed = {}
    for r in ok:
        per_seed.setdefault(r["seed"], []).append(r)
    paired = {s: round(sum(x["margin"] for x in rs), 2) for s, rs in per_seed.items()}
    paired_vals = list(paired.values())

    wins = sum(1 for m in margins if m > 0)
    losses = sum(1 for m in margins if m < 0)
    summary = {
        "tag": args.tag, "new": args.new, "base": args.base,
        "battles": len(ok), "errors": len(errs),
        "mean_margin": round(sum(margins) / len(margins), 1) if margins else None,
        "median_margin": round(sorted(margins)[len(margins) // 2], 1) if margins else None,
        "worst_margin": min(margins) if margins else None,
        "best_margin": max(margins) if margins else None,
        "wins": wins, "losses": losses, "ties": len(margins) - wins - losses,
        "mean_paired_margin": round(sum(paired_vals) / len(paired_vals), 1) if paired_vals else None,
        "bootstrap95_ci_mean": bootstrap_ci(margins),
        "elapsed_s": round(time.time() - t0, 1),
    }
    out_path = os.path.join(OUTDIR, f"{args.tag}.json")
    with open(out_path, "w") as f:
        json.dump({"summary": summary, "results": sorted(ok, key=lambda r: (r["seed"], r["seat"])),
                   "errors": errs, "paired": paired}, f, indent=1)

    print(json.dumps(summary, indent=1))
    print(f"per-seed paired margins: {json.dumps(paired, sort_keys=True)}")
    print(f"saved: {out_path}")
    if errs:
        print(f"ERRORS ({len(errs)}):")
        for e in errs[:5]:
            print(" ", e)


if __name__ == "__main__":
    main()
