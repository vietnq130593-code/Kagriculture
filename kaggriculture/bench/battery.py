#!/usr/bin/env python3
"""BATTERY — universal two-sided battery runner (Task 69, ARI plan).

Usage:
  python3 battery.py <A> <B> [--seeds 100-115] [--out file.json] [--jobs 2] [--tag note]

A/B: agent name (resolved via arena/run_battle.py AGENTS registry) or a .py path
(relative to kaggressurE/ or absolute). Each seed runs BOTH seats; summary reports
wins/total, avg money, avg gap, worst ratio, per-seed rows (JSON).

Determinism: same pattern as battery_v5.py (env.run with file paths —
kaggle_environments exec's fresh agent namespaces per battle), verified
dollar-identical with the arena server runner in Tasks 60-67.
"""
import argparse
import json
import os
import sys
import time
from multiprocessing import get_context

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # kaggressurE/
sys.path.insert(0, ROOT)


def resolve(x):
    if os.path.isfile(x):
        return x
    p = os.path.join(ROOT, x)
    if os.path.isfile(p):
        return p
    return None


def load_registry():
    reg = {}
    try:
        import re
        src = open(os.path.join(ROOT, 'arena', 'run_battle.py')).read()
        m = re.search(r'AGENTS\s*=\s*\{(.*?)\}', src, re.S)
        for name, path in re.findall(r'"([^"]+)"\s*:\s*\(.*?"([^"]+)"', m.group(1)):
            reg[name] = path
    except Exception:
        pass
    return reg


REG = load_registry()


def resolve_agent(x):
    p = resolve(x)
    if p:
        return p
    if x in REG:
        return REG[x]
    p = resolve(x + ".py")  # bare name of a .py file in kaggressurE/
    if p:
        return p
    raise SystemExit(f"unknown agent: {x} (registry: {sorted(REG)})")


def one_match(a_path, b_path, seed):
    from kaggle_environments import make
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run([a_path, b_path])
    r0 = float(env.steps[-1][0].reward or 0)
    r1 = float(env.steps[-1][1].reward or 0)
    return r0, r1


def work(job):
    a_path, b_path, seed = job
    t0 = time.time()
    try:
        r0, r1 = one_match(a_path, b_path, seed)
        return {"ok": True, "seed": seed, "r0": r0, "r1": r1, "s": round(time.time() - t0, 1)}
    except Exception as e:
        return {"ok": False, "seed": seed, "err": repr(e)[:200]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a")
    ap.add_argument("b")
    ap.add_argument("--seeds", default="100-107")
    ap.add_argument("--out", default=None)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    a_path = resolve_agent(args.a)
    b_path = resolve_agent(args.b)

    if "-" in args.seeds:
        lo, hi = args.seeds.split("-")
        seeds = list(range(int(lo), int(hi) + 1))
    else:
        seeds = [int(x) for x in args.seeds.split(",")]

    # both seats upfront so the pool parallelizes everything
    jobs = []
    for s in seeds:
        jobs.append((a_path, b_path, s))   # seat A
        jobs.append((b_path, a_path, s))   # seat B (swapped)
    t0 = time.time()
    if args.jobs <= 1:
        results = [work(j) for j in jobs]
    else:
        ctx = get_context("fork")
        with ctx.Pool(args.jobs) as pool:
            results = pool.map(work, jobs)

    # results[i] = seat-A run for seed seeds[i/2], results[i+1] = swapped run
    fails = [r for r in results if not r["ok"]]
    out_rows = []
    for i, s in enumerate(seeds):
        rA = results[2 * i]      # a as seat0: r0=a, r1=b
        rB = results[2 * i + 1]  # b as seat0: r0=b, r1=a
        if not (rA["ok"] and rB["ok"]):
            continue
        ra = (rA["r0"] + rB["r1"]) / 2.0
        rb = (rA["r1"] + rB["r0"]) / 2.0
        out_rows.append({
            "seed": s,
            "a_seat0": rA["r0"], "b_seat1": rA["r1"], "b_seat0": rB["r0"], "a_seat1": rB["r1"],
            "a_avg": ra, "b_avg": rb, "gap": ra - rb, "ratio": ra / max(1, rb),
        })

    n = len(out_rows) * 2
    wins = sum(1 for r in out_rows if r["a_seat0"] > r["b_seat1"]) + \
           sum(1 for r in out_rows if r["a_seat1"] > r["b_seat0"])
    ma = sum(r["a_seat0"] + r["a_seat1"] for r in out_rows) / max(1, n)
    mb = sum(r["b_seat1"] + r["b_seat0"] for r in out_rows) / max(1, n)
    worst = min((min(r["a_seat0"] / max(1, r["b_seat1"]), r["a_seat1"] / max(1, r["b_seat0"]))
                 for r in out_rows), default=0)
    ratios = sorted(r["ratio"] for r in out_rows)
    med = ratios[len(ratios) // 2] if ratios else 0

    print(f"\n=== {args.a} vs {args.b} two-sided {n} games (seeds {seeds[0]}-{seeds[-1]}) ===")
    print(f"wins {wins}/{n} | avg ${ma:,.0f} vs ${mb:,.0f} | gap {ma - mb:+,.0f} | "
          f"ratio {ma / max(1, mb):.3f}x | median {med:.3f} | worst {worst:.3f}x | "
          f"{time.time() - t0:.0f}s")
    if args.tag:
        print(f"tag: {args.tag}")
    if fails:
        print(f"FAILS: {len(fails)} — {fails[:3]}")

    result = {
        "a": args.a, "b": args.b, "seeds": f"{seeds[0]}-{seeds[-1]}" if len(seeds) > 1 else str(seeds[0]),
        "wins": wins, "games": n, "avg_a": ma, "avg_b": mb, "gap": ma - mb,
        "median_ratio": med, "worst_ratio": worst, "tag": args.tag,
        "rows": out_rows, "fails": fails,
    }
    if args.out:
        outp = args.out if os.path.isabs(args.out) else os.path.join(ROOT, "bench", args.out)
        json.dump(result, open(outp, "w"), indent=1)
        print(f"saved {outp}")


if __name__ == "__main__":
    main()
