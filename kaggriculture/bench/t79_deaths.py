#!/usr/bin/env python3
"""T79d — pinpoint animal escape events + what the owner was doing."""
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
        prev = {}
        events = []
        for r in recs:
            step = r["step"]
            cur = {}
            for y, row in enumerate(r["farms"][seat]["tiles"]):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and t.get("animal"):
                        cur[(x, y)] = (t["animal"], t.get("fed_today"), t.get("consecutive_unfed"), t.get("placed_day"))
            for k, v in prev.items():
                if k not in cur:
                    events.append((step, k, v))
            prev = cur
        print(f"-- {who}: {len(events)} escape events")
        for step, (x, y), (animal, fed, un, placed) in events:
            day, hour = step // 24, step % 24
            # look back at previous 2 days of that tile + owner actions
            print(f"   ESCAPE at s{step} (d{day} h{hour}): {animal} @({x},{y}) placed_day={placed}")
            for r2 in recs:
                s2 = r2["step"]
                if s2 < step - 55 or s2 > step:
                    continue
                t2 = r2["farms"][seat]["tiles"][y][x]
                if isinstance(t2, dict) and t2.get("animal"):
                    shed_w = r2["priv"][seat]["shed"].get("WHEAT", 0)
                    inv_w = sum(inv.get("WHEAT", 0) for inv in r2["priv"][seat]["inventories"])
                    act = r2["acts"][seat]
                    feeds = [h for h in [act.get("farmer")] + list(act.get("hands", [])) if h and h[0] == "FEED"]
                    if s2 % 24 in (19, 20, 21, 22, 23) or feeds:
                        print(f"      s{s2:3d} d{s2//24:2d}h{s2%24:02d}: fed={t2['fed_today']} cun={t2['consecutive_unfed']} yld={t2['yield_units']} shedW={shed_w} invW={inv_w} FEEDs={len(feeds)}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
