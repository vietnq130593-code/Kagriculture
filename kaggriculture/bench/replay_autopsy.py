#!/usr/bin/env python3
"""REPLAY AUTOPSY — phân tích Kaggle episode replay JSON (Task 71).

Usage: python3 replay_autopsy.py <replay.json> [--json out.json]

Outputs:
  1. Summary: teams, seed, rewards, final money
  2. Per-day money curve both seats (end-of-day money)
  3. Per-seat item ledger: executed SELLs (price_t × shed delta) and buys
  4. Tile class timeline: crops planted (count by type per day) + animals
  5. HIRE timeline (hands count per day) + ops mix per day
Ledger method: at step t engine executes market orders at obs(t) prices;
shed deltas between t and t+1 with a SELL request for that item at t = sold.
"""
import argparse
import json
import sys
from collections import defaultdict

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
PRODUCTS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER")
ANIMALS = ("COW", "SHEEP", "GOOSE")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("replay")
    ap.add_argument("--json", default=None)
    ap.add_argument("--seat", type=int, default=None, help="focus seat for ops detail")
    args = ap.parse_args()

    d = json.load(open(args.replay))
    info = d.get("info", {})
    steps = d["steps"]
    names = [a.get("Name", "?") for a in info.get("Agents", [])]
    print(f"=== {args.replay} ===")
    print(f"Episode {info.get('EpisodeId')} | seed {info.get('seed')} | {len(steps)} steps")
    print(f"Teams: {names}")
    print(f"Rewards: {d.get('rewards')}")

    n_days = steps[-1][0]["observation"]["day"] + 1
    seats = (0, 1)

    money_day = {s: [None] * n_days for s in seats}
    hands_day = {s: [0] * n_days for s in seats}
    sells = {s: defaultdict(float) for s in seats}          # item -> $
    units = {s: defaultdict(int) for s in seats}            # item -> units sold
    buys = {s: defaultdict(float) for s in seats}           # item -> $ spent
    buy_units = {s: defaultdict(int) for s in seats}
    crops_day = {s: {c: [0] * n_days for c in CROPS} for s in seats}
    animals_day = {s: {a: [0] * n_days for a in ANIMALS} for s in seats}
    ops_day = {s: defaultdict(lambda: [0] * n_days) for s in seats}
    mkts_day = {s: defaultdict(lambda: [0] * n_days) for s in seats}
    animal_buys = {s: defaultdict(int) for s in seats}

    pend_req = {s: None for s in seats}
    pend_shed = {s: {} for s in seats}
    pend_prices = {s: {} for s in seats}
    for t, st in enumerate(steps):
        for s in seats:
            obs = st[s]["observation"]
            day = obs["day"]
            farm = obs["farms"][s]
            money_day[s][day] = farm["money"]
            hands_day[s][day] = len(farm.get("hands", []))
            # tiles: crops + animals
            cc = defaultdict(int)
            ac = defaultdict(int)
            for row in farm["tiles"]:
                for tile in row:
                    if not isinstance(tile, dict):
                        continue
                    if tile.get("kind") == "PLANT":
                        cc[tile.get("crop")] += 1
                    if tile.get("animal"):
                        ac[tile["animal"]] += 1
            for c in CROPS:
                crops_day[s][c][day] = cc.get(c, 0)
            for a in ANIMALS:
                animals_day[s][a][day] = ac.get(a, 0)
            # ops mix
            act = st[s].get("action") or {}
            cmds = [act.get("farmer")] + list(act.get("hands") or [])
            for mv in cmds:
                op = mv[0] if isinstance(mv, list) and mv else "PASS"
                ops_day[s][op][day] += 1
            # market orders (parse first, then ledger pairing t-1 → t)
            prices = obs["market"]["prices"]
            shed = obs["private"]["shed"] if obs.get("private") else {}
            req_sell = defaultdict(int)
            for o in (act.get("market") or []):
                if not o or len(o) < 3:
                    if o and o[0]:
                        mkts_day[s][o[0]][day] += 1  # HIRE: 1-element order
                    continue
                kind, item, qty = o[0], o[1], o[2]
                mkts_day[s][kind][day] += 1
                if kind == "SELL":
                    req_sell[item] += qty
                elif kind == "BUY_ANIMAL":
                    animal_buys[s][item] += qty
                    buys[s][item] += prices.get(item, 0) * qty
                    buy_units[s][item] += qty
                elif kind in ("BUY_SEED", "BUY_PRODUCT"):
                    buys[s][item] += prices.get(item, 0) * qty
                    buy_units[s][item] += qty
            # ledger: action at step t executes against prices[t]/shed[t];
            # its effect appears in shed[t+1]. Pair pending (from t-1) with
            # the delta computed at t (shed[t-1]-shed[t]).
            if pend_req[s] is not None:
                for item, qty_req in pend_req[s].items():
                    delta = pend_shed[s].get(item, 0) - shed.get(item, 0)
                    if delta > 0:
                        sells[s][item] += pend_prices[s].get(item, 0) * delta
                        units[s][item] += delta
            pend_req[s] = dict(req_sell)
            pend_shed[s] = dict(shed)
            pend_prices[s] = dict(prices)

    for s in seats:
        print(f"\n--- SEAT {s}: {names[s]} ---")
        print("  item ledger ($ in / units sold $ out):")
        tot_in = sum(buys[s].values())
        tot_out = sum(sells[s].values())
        for item in sorted(set(sells[s]) | set(buys[s])):
            print(f"    {item:12s} sold {units[s][item]:>5d}u ${sells[s][item]:>9,.0f} | bought {buy_units[s][item]:>4d}u ${buys[s][item]:>8,.0f}")
        print(f"    TOTAL: sold ${tot_out:,.0f} | spent ${tot_in:,.0f} | final ${money_day[s][-1]:,.0f}")
        print(f"  animals bought: {dict(animal_buys[s])}")
        print(f"  hires: max hands {max(hands_day[s])} | end-of-day hands d1,d5,d10,d15,d20,d25,d29: "
              f"{[hands_day[s][min(i, n_days-1)] for i in (1,5,10,15,20,25,29)]}")
        # crop mix milestones
        for day in (6, 12, 18, 24, 29):
            if day < n_days:
                mix = {c: crops_day[s][c][day] for c in CROPS if crops_day[s][c][day]}
                ans = {a: animals_day[s][a][day] for a in ANIMALS if animals_day[s][a][day]}
                print(f"  d{day:02d} tiles: {mix} | animals: {ans}")

    # money curve with gap
    print("\n  day | money seat0 | money seat1 | gap(0-1)")
    for day in range(n_days):
        m0, m1 = money_day[0][day], money_day[1][day]
        if m0 is not None and m1 is not None and day % 2 == 0:
            print(f"  {day:3d} | {m0:>10,.0f} | {m1:>10,.0f} | {m0-m1:>+9,.0f}")

    if args.seat is not None:
        s = args.seat
        print(f"\n  ops mix seat {s} (totals): " + dict(sorted(((k, sum(v)) for k, v in ops_day[s].items()), key=lambda kv: -kv[1])))

    if args.json:
        out = {
            "episode": info.get("EpisodeId"), "seed": info.get("seed"), "names": names,
            "rewards": d.get("rewards"),
            "money_day": money_day, "hands_day": hands_day,
            "sells": {s: dict(sells[s]) for s in seats},
            "units": {s: dict(units[s]) for s in seats},
            "buys": {s: dict(buys[s]) for s in seats},
            "crops_day": {s: {c: crops_day[s][c] for c in CROPS} for s in seats},
            "animals_day": {s: {a: animals_day[s][a] for a in ANIMALS} for s in seats},
            "animal_buys": {s: dict(animal_buys[s]) for s in seats},
            "ops_day": {s: {k: v for k, v in ops_day[s].items()} for s in seats},
            "mkts_day": {s: {k: v for k, v in mkts_day[s].items()} for s in seats},
        }
        json.dump(out, open(args.json, "w"), indent=1)
        print(f"\nsaved {args.json}")


if __name__ == "__main__":
    main()
