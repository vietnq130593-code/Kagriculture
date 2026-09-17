#!/usr/bin/env python3
"""T80c — verify melon mystery, market-order headroom, v41 sell timing by day."""
import json
from collections import defaultdict


def load(path):
    recs = []
    for line in open(path):
        line = line.strip()
        if line:
            d = json.loads(line)
            if d.get("t") == "turn":
                recs.append(d)
    return recs


def main(path, seat):
    recs = load(path)
    print(f"=== {path} seat {seat} ===")

    # 1. melon tile trajectory: track every tile that ever becomes MELON
    melon_tiles = {}   # (x,y) -> list of (day, yield, watered)
    melon_water = defaultdict(int)  # day -> water ops ON melon tiles
    fert_sell_day = defaultdict(int)
    milk_sell_day = defaultdict(int)
    straw_sell_day = defaultdict(int)
    melon_sell_day = defaultdict(int)
    wool_sell_day = defaultdict(int)
    egg_sell_day = defaultdict(int)
    wheat_sell_day = defaultdict(int)
    mkt_order_count = defaultdict(int)
    sell_q_by_day_item = defaultdict(lambda: defaultdict(int))

    prev_shed = {}
    for r in recs:
        step = r["step"]
        day = step // 24
        hour = step % 24
        farm = r["farms"][seat]
        priv = r["priv"][seat]
        act = r["acts"][seat]

        # water ops on melon tiles: find unit pos -> tile
        for a in [act.get("farmer")] + (act.get("hands") or []) if isinstance(act, dict) else []:
            if isinstance(a, list) and a and a[0] == "WATER":
                pass  # position unknown here; use tile watered_today transitions instead

        if hour == 23:
            for y, row in enumerate(farm["tiles"]):
                for x, t in enumerate(row):
                    if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON":
                        melon_tiles.setdefault((x, y), []).append(
                            (day, t.get("yield_units"), t.get("planted_day")))

        mkt = act.get("market") or []
        mkt_order_count[len(mkt)] += 1
        for o in mkt:
            if isinstance(o, list) and o and o[0] == "SELL" and len(o) >= 3:
                item, q = o[1], o[2]
                sell_q_by_day_item[day][item] += q

        # executed sells by shed delta minus pickups/placements
        picked = defaultdict(int)
        placed = defaultdict(int)
        for a in [act.get("farmer")] + (act.get("hands") or []) if isinstance(act, dict) else []:
            if isinstance(a, list) and a:
                if a[0] == "PICKUP" and len(a) >= 2:
                    picked[a[1]] += a[2] if len(a) > 2 else 1
                elif a[0] == "PLACE" and len(a) >= 2:
                    placed[a[1]] += 1
        for item, v in priv["shed"].items():
            dec = prev_shed.get(item, 0) - v - picked.get(item, 0) - placed.get(item, 0)
            if dec > 0:
                if item == "FERTILIZER":
                    fert_sell_day[day] += dec
                elif item == "MILK":
                    milk_sell_day[day] += dec
                elif item == "STRAWBERRY":
                    straw_sell_day[day] += dec
                elif item == "MELON":
                    melon_sell_day[day] += dec
                elif item == "WOOL":
                    wool_sell_day[day] += dec
                elif item == "EGG":
                    egg_sell_day[day] += dec
                elif item == "WHEAT":
                    wheat_sell_day[day] += dec
        prev_shed = dict(priv["shed"])

    print("\n-- melon tiles (day23 snapshot): tile -> [(day, yield, planted_day)]")
    for k in sorted(melon_tiles)[:16]:
        print(f"   {k}: {melon_tiles[k][:12]}")
    print(f"   total melon tiles seen: {len(melon_tiles)}")

    print("\n-- v41 executed sells by day:")
    for name, d in [("FERT", fert_sell_day), ("MILK", milk_sell_day),
                    ("STRAW", straw_sell_day), ("MELON", melon_sell_day),
                    ("WOOL", wool_sell_day), ("EGG", egg_sell_day),
                    ("WHEAT", wheat_sell_day)]:
        if d:
            print(f"   {name:6s}: " + " ".join(f"d{k}:{v}" for k, v in sorted(d.items())))

    print("\n-- market order count per turn (histogram):")
    print("   " + " ".join(f"{k}orders:{v}" for k, v in sorted(mkt_order_count.items())))

    print("\n-- max 10-budget: turns with >=10 orders:",
          sum(v for k, v in mkt_order_count.items() if k >= 10))
    print("   turns total:", len(recs))


if __name__ == "__main__":
    base = "/home/z/my-project/kaggressurE".replace("kaggressurE", "kaggriculture") + "/battles/"
    main(base + "t79_replay_v16_ahmedv41_s365.jsonl", 1)
    main(base + "t79_replay_kme3v39_ahmedv41_s362.jsonl", 1)
