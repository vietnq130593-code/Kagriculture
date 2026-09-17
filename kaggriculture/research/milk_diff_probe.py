#!/usr/bin/env python3
"""Daily MILK dynamics diff: v22 vs v20 on a given seed (seat A vs ahmedv46).
Shows when the layer engaged, what it banked, and the price/inventory paths
that separate good seeds from bad ones."""
import json, subprocess, sys

ROOT = "/home/z/my-project/kaggriculture"
MILK_SHOPS = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}


def run(agent, seed):
    cmd = [sys.executable, f"{ROOT}/arena/run_battle.py", "--a", agent,
           "--b", "ahmedv46", "--seed", str(seed)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                       cwd=ROOT)
    daily = {}
    end = None
    for line in (p.stdout or "").splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("t") == "end":
            end = o
            continue
        if o.get("t") != "turn":
            continue
        d = o["step"] // 24
        inv = o["market"]["inventory"]["MILK"]
        pr = o["market"]["prices"]["MILK"]
        shops = sum(1 for s in o["town"]["unlocked_shops"] if s in MILK_SHOPS)
        act = o["acts"][0].get("market") or []
        sells = sum(int(x[2]) for x in act
                    if isinstance(x, (list, tuple)) and len(x) >= 3
                    and x[0] == "SELL" and x[1] == "MILK")
        shed = (o["priv"][0].get("shed") or {}).get("MILK", 0)
        money = o["farms"][0]["money"]
        # keep last hour of the day
        daily[d] = (inv, pr, shops, sells, shed, money)
    return daily, end


def main(seed):
    d20, e20 = run("v20", seed)
    d22, e22 = run("v22", seed)
    print(f"=== seed {seed}: v20 margin {e20['rewards'][0]-e20['rewards'][1]:+.0f}"
          f" | v22 margin {e22['rewards'][0]-e22['rewards'][1]:+.0f}"
          f" | layer delta {e22['rewards'][0]-e20['rewards'][0]:+.0f} (my money),"
          f" v46 delta {e22['rewards'][1]-e20['rewards'][1]:+.0f}")
    print("day | inv20 inv22 | p20   p22 | sh | sel20 sel22 | shed20 shed22 | money20 money22")
    for d in sorted(set(d20) | set(d22)):
        a = d20.get(d, (0, 0, 0, 0, 0, 0))
        b = d22.get(d, (0, 0, 0, 0, 0, 0))
        mark = " <<<" if a[3] != b[3] or a[4] != b[4] else ""
        print(f"d{d:02d} | {a[0]:5d} {b[0]:5d} | {a[1]:4d} {b[1]:4d} |"
              f" {b[2]:1d} | {a[3]:5d} {b[3]:5d} | {a[4]:6d} {b[4]:6d} |"
              f" {a[5]:8.0f} {b[5]:8.0f}{mark}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
