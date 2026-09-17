#!/usr/bin/env python3
"""T79c — herd survival & feed audit per day."""
import json
import sys


def main(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if line:
            d = json.loads(line)
            if d.get("t") == "turn":
                recs.append(d)
    print(f"=== {path} ===")
    for seat in (0, 1):
        who = "v16" if seat == 0 else "ahmedv41"
        print(f"-- {who}: herd per day-end (h23) + unfed incidents")
        prev = {}
        deaths = 0
        for r in recs:
            step = r["step"]
            if step % 24 != 23:
                continue
            counts = {}
            for row in r["farms"][seat]["tiles"]:
                for t in row:
                    if isinstance(t, dict) and t.get("animal"):
                        counts[t["animal"]] = counts.get(t["animal"], 0) + 1
            day = step // 24
            # deaths: animals present yesterday, missing today (same day boundary rough)
            for k, v in prev.items():
                if counts.get(k, 0) < v:
                    deaths += v - counts.get(k, 0)
            prev = counts
            if day % 3 == 0 or day > 25:
                print(f"   d{day:2d}: {counts}")
        # unfed scan: count tiles with consecutive_unfed >= 1 at any hour >= 20
        unfed = 0
        for r in recs:
            if r["step"] % 24 < 20:
                continue
            for row in r["farms"][seat]["tiles"]:
                for t in row:
                    if isinstance(t, dict) and t.get("animal") and t.get("consecutive_unfed", 0) >= 1 and not t.get("fed_today"):
                        unfed += 1
        print(f"   animal losses (day-over-day count drops): ~{deaths} | unfed-at-h20+ incidents: {unfed}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
