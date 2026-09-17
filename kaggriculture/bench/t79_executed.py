#!/usr/bin/env python3
"""T79b — executed-sells autopsy (shed-delta + money attribution) from JSONL replay."""
import json
import sys
from collections import defaultdict

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def load(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        if d.get("t") == "turn":
            recs.append(d)
    return recs


def executed(recs):
    """Per-seat: executed sell units (via shed delta + order), revenue (money attribution)."""
    out = {}
    prev_shed = [{}, {}]
    prev_money = [None, None]
    for r in recs:
        step = r["step"]
        for seat in (0, 1):
            shed = dict(r["priv"][seat]["shed"])
            money = r["farms"][seat]["money"]
            act = r["acts"][seat]
            if r["step"] > 0 and prev_money[seat] is not None:
                dm = money - prev_money[seat]
                for item in PRODUCTS:
                    delta = shed.get(item, 0) - prev_shed[seat].get(item, 0)
                    if delta < 0:
                        out.setdefault(seat, {}).setdefault(item, []).append(
                            {"step": step, "hour": step % 24, "day": step // 24,
                             "units": -delta, "dmoney": None, "px": r["market"]["prices"][item]})
            prev_shed[seat] = shed
            prev_money[seat] = money
    return out


def main(path):
    recs = load(path)
    ex = executed(recs)
    print(f"=== {path} ===")
    for seat in (0, 1):
        who = "v16" if seat == 0 else "ahmedv41"
        tot_u = 0
        rows = []
        for item, evs in sorted(ex.get(seat, {}).items(), key=lambda x: -sum(e["units"] for e in x[1])):
            u = sum(e["units"] for e in evs)
            tot_u += u
            last_day = max(e["day"] for e in evs)
            first_day = min(e["day"] for e in evs)
            big = max(evs, key=lambda e: e["units"])
            rows.append(f"  {item:10s} {u:6d}u exec ({len(evs):3d} turns) days {first_day}-{last_day} | biggest {big['units']}u @day{big['day']}h{big['hour']} px{big['px']}")
        print(f"-- {who}: total executed {tot_u}u")
        print("\n".join(rows))
    # money gap by day-end
    money = {r["step"]: (r["farms"][0]["money"], r["farms"][1]["money"]) for r in recs}
    print("\nday-end: step, v16$, ahmedv41$, gap(v41-v16):")
    for step in sorted(money):
        if step % 24 == 23:
            a, b = money[step]
            print(f"  d{step//24:2d} s{step:3d}: {a:>9,.0f} {b:>9,.0f}  {b-a:>+9,.0f}")


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)
