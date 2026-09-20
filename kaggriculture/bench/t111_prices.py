#!/usr/bin/env python3
"""Task 111: dump daily EGG/other prices + our sell revenue from a battle."""
import json
import subprocess
import sys

ROOT = "/home/z/my-project/kaggriculture"


def main():
    a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    items = sys.argv[4].split(",") if len(sys.argv) > 4 else ["EGG"]
    cmd = [sys.executable, f"{ROOT}/arena/run_battle.py", "--a", a, "--b", b,
           "--seed", str(seed)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
    prev_money = [0.0, 0.0]
    sold = [dict(), dict()]
    print(f"=== {a} vs {b} seed {seed}")
    hdr = "day " + " ".join(f"{it:>10s}" for it in items) + "   revA   revB  gapA-B  shops"
    print(hdr)
    for line in (p.stdout or "").splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("t") != "turn":
            continue
        step, day = obj["step"], obj["day"]
        if step % 24 == 23:  # last turn of day
            prices = obj["market"]["prices"]
            m = [f["money"] for f in obj["farms"]]
            rev = [m[i] - prev_money[i] for i in (0, 1)]
            shops = obj["town"]["unlocked_shops"]
            row = f"{day:3d} " + " ".join(f"{prices.get(it, 0):10.1f}" for it in items)
            print(f"{row} {rev[0]:7.0f} {rev[1]:7.0f} {m[0]-m[1]:7.0f}  {','.join(shops[-2:])}")
            prev_money = m
        # count sells per item per seat
        for i, act in enumerate(obj.get("acts") or []):
            for o in (act.get("market") or []):
                if o and o[0] == "SELL" and len(o) >= 3 and o[1] in items:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    sold[i][o[1]] = sold[i].get(o[1], 0) + q
    print("total SELL qty caps:", "A:", sold[0], "B:", sold[1])


if __name__ == "__main__":
    main()
