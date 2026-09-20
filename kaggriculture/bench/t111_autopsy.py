#!/usr/bin/env python3
"""Task 111 autopsy: daily money divergence between two agents on given seeds.

Runs run_battle.py, parses the JSONL turn stream, and prints per-day money
for both seats + the running gap, so we can see WHERE the losing margin
accumulates (which day window).
"""
import json
import subprocess
import sys

ROOT = "/home/z/my-project/kaggriculture"


def run(a, b, seed):
    cmd = [sys.executable, f"{ROOT}/arena/run_battle.py", "--a", a, "--b", b,
           "--seed", str(seed)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
    days = {}
    for line in (p.stdout or "").splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("t") == "turn":
            day = obj["day"]
            m0 = obj["farms"][0]["money"]
            m1 = obj["farms"][1]["money"]
            # record the last turn seen for each day
            days[day] = (m0, m1)
        elif obj.get("t") == "end":
            end = obj["rewards"]
    return days, end


def main():
    a, b = sys.argv[1], sys.argv[2]
    seeds = [int(s) for s in sys.argv[3:]]
    for seed in seeds:
        days, end = run(a, b, seed)
        print(f"=== {a} vs {b} seed {seed}  final {end} (a-b = {end[0]-end[1]:.0f})")
        prev_gap = 0.0
        for d in sorted(days):
            m0, m1 = days[d]
            gap = m0 - m1
            dgap = gap - prev_gap
            mark = " <<<<" if abs(dgap) > 150 else ""
            print(f"  day {d:2d}: a={m0:9.0f} b={m1:9.0f} gap={gap:8.0f} dGap={dgap:+8.0f}{mark}")
            prev_gap = gap


if __name__ == "__main__":
    main()
