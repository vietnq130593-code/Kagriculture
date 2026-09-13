#!/usr/bin/env python3
"""SHED WATCH — Task 73 pathology scanner for orphaned shed animals.

Scans a run_battle.py JSONL stream (or a saved JSONL file) and reports every
"orphan event": an animal (COW/SHEEP/GOOSE) sitting in a farm's shed for
>= GRACE steps (default 24 = 1 day) — i.e. the native planner bought it but
never placed it on a matching structure tile (root cause of the -$5,973
Kaggle loss to Dmitriy Ulylin, see Task 72 autopsy).

Usage (from kaggriculture/):
  python3 bench/shed_watch.py --a v14 --b kme3v10 --seed 661817856
  python3 bench/shed_watch.py --a v14 --b kme3v10 --seeds 100-115 --seat 0
  python3 bench/shed_watch.py --replay t73_game.jsonl --seat 0
"""
import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(ROOT, "arena", "run_battle.py")

ANIMALS = ("COW", "SHEEP", "GOOSE")
STRUCT = {"COW": "PASTURE", "SHEEP": "PASTURE", "GOOSE": "COOP"}


def board_counts(farm):
    """Count animals on the board + empty matching structures."""
    on_board = {a: 0 for a in ANIMALS}
    empty = {"PASTURE": 0, "COOP": 0}
    for line in farm.get("tiles", []):
        for tile in line:
            if not isinstance(tile, dict):
                continue
            animal = tile.get("animal")
            if animal in on_board:
                on_board[animal] += 1
            elif tile.get("kind") in empty and "animal" not in tile:
                empty[tile["kind"]] += 1
    return on_board, empty


def scan_stream(stream, seat, grace):
    """Yield orphan event dicts from a JSONL stream of turn records."""
    first_seen = {}   # animal -> step when it first appeared in shed
    last_count = {}
    events = []
    shed_end = None
    for line in stream:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        if rec.get("t") == "end":
            shed_end = rec
            continue
        if rec.get("t") != "turn":
            continue
        step = int(rec["step"])
        priv = rec.get("priv") or [None, None]
        if seat >= len(priv) or not priv[seat]:
            continue
        farm = (rec.get("farms") or [None, None])[seat]
        if not farm:
            continue
        shed = (priv[seat].get("shed")) or {}
        invs = priv[seat].get("inventories") or []
        carried = {a: sum(int(inv.get(a, 0)) for inv in invs) for a in ANIMALS}
        on_board, empty = board_counts(farm)
        for a in ANIMALS:
            n = int(shed.get(a, 0))
            if n > 0:
                if last_count.get(a, 0) == 0:
                    first_seen[a] = step
                last_count[a] = n
                age = step - first_seen.get(a, step)
                if age >= grace and empty[STRUCT[a]] > 0:
                    events.append({
                        "step": step, "day": rec.get("day"), "hour": rec.get("hour"),
                        "animal": a, "shed": n, "carried": carried[a],
                        "board": on_board[a], "empty_tiles": empty[STRUCT[a]],
                        "age": age,
                    })
            else:
                if last_count.get(a, 0) > 0 and carried[a] == 0:
                    # animal left the shed without anyone carrying -> placed
                    events.append({"step": step, "animal": a, "resolved": True,
                                   "board": on_board[a]})
                elif last_count.get(a, 0) > 0:
                    events.append({"step": step, "animal": a, "resolved": True,
                                   "carried": carried[a], "board": on_board[a]})
                last_count[a] = 0
    return events, shed_end


def dedupe(events):
    """One line per (animal, contiguous stuck window) instead of per-turn spam."""
    out, cur = [], None
    for e in events:
        if e.get("resolved"):
            if cur:
                out.append(cur)
                cur = None
            out.append(e)
            continue
        key = (e["animal"], e["shed"])
        if cur and (cur["animal"], cur["shed"]) == key and e["step"] - cur["last_step"] <= 24:
            cur["last_step"] = e["step"]
            cur["max_empty"] = max(cur["max_empty"], e["empty_tiles"])
        else:
            if cur:
                out.append(cur)
            cur = {"animal": e["animal"], "shed": e["shed"], "first_step": e["step"],
                   "last_step": e["step"], "day": e["day"], "max_empty": e["empty_tiles"]}
    if cur:
        out.append(cur)
    return out


def run_game(a, b, seed):
    proc = subprocess.run(
        [sys.executable, RUNNER, "--a", a, "--b", b, "--seed", str(seed)],
        capture_output=True, text=True, cwd=ROOT,
    )
    if proc.returncode != 0:
        print(f"runner failed seed {seed}:\n{proc.stderr[-2000:]}", file=sys.stderr)
        return None
    return proc.stdout.splitlines()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="v14")
    ap.add_argument("--b", default="kme3v10")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--seeds", help="N-M inclusive")
    ap.add_argument("--seat", type=int, default=0)
    ap.add_argument("--grace", type=int, default=24)
    ap.add_argument("--replay", help="scan a saved JSONL instead of running")
    ap.add_argument("--tag", default="")
    args = ap.parse_args()

    seeds = []
    if args.seed is not None:
        seeds = [args.seed]
    elif args.seeds:
        lo, _, hi = args.seeds.partition("-")
        seeds = list(range(int(lo), int(hi) + 1))
    elif not args.replay:
        ap.error("need --seed, --seeds or --replay")

    total_events = 0
    if args.replay:
        with open(args.replay) as f:
            events, end = scan_stream(f, args.seat, args.grace)
        for e in dedupe(events):
            print(json.dumps(e))
        return

    for seed in seeds:
        lines = run_game(args.a, args.b, seed)
        if lines is None:
            continue
        events, end = scan_stream(iter(lines), args.seat, args.grace)
        if events:
            total_events += len([e for e in events if not e.get("resolved")])
        endr = (end or {}).get("rewards")
        print(f"seed {seed} seat{args.seat} rewards={endr} "
              f"orphan_events={len([e for e in events if not e.get('resolved')])}")
        for e in dedupe(events):
            print("  " + json.dumps(e))
    print(f"TOTAL orphan animal-windows: {total_events}")


if __name__ == "__main__":
    main()
