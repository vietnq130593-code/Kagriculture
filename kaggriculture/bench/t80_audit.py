#!/usr/bin/env python3
"""T80a — leak audit of ahmedv41 from full JSONL replays.

Goal: find every dollar v41 leaves on the table. Measures:
  P1  CARE coverage per animal-day (care bonus = +1 unit/production cycle)
  P2  FERTILIZE usage per crop (doubles watering yield)
  P3  End-state: money, shed contents, unharvested yields, seeds, standing plants
  P4  SELL hour histogram (town-tick timing)
  P5  EGG economy (geese produce every day)
  P6  Realized avg sell price per product (money delta / units)
  P7  Shed occupancy peak (room to defer sells)
  P8  Harvest saturation: animal tiles at max_held
  P9  Weed / unwatered plant incidents
  P10 Water coverage of plants
  P11 Hire cadence + hands per day
  P12 Idle money windows
"""
import json
import sys
from collections import defaultdict

MAX_HELD = {"GOOSE": 4, "COW": 6, "SHEEP": 6}


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


def unit_actions(act):
    if not isinstance(act, dict):
        return []
    out = []
    f = act.get("farmer")
    if isinstance(f, list):
        out.append(f)
    for h in act.get("hands", []) or []:
        if isinstance(h, list):
            out.append(h)
    return out


def market_orders(act):
    if not isinstance(act, dict):
        return []
    m = act.get("market")
    return m if isinstance(m, list) else []


def audit(path, focus_seat, focus_name):
    recs = load(path)
    print(f"\n{'='*72}\n{path} — {len(recs)} turns — FOCUS seat {focus_seat} = {focus_name}\n{'='*72}")

    for seat in (0, 1):
        tag = focus_name if seat == focus_seat else f"opp{seat}"
        care_ops = defaultdict(int)          # day -> CARE count
        fert_ops = defaultdict(int)          # crop -> count
        collectfert_ops = 0
        harvest_ops = 0
        sell_hours = defaultdict(int)         # hour -> SELL order count
        sell_by_item_hour = defaultdict(lambda: defaultdict(int))
        buys = defaultdict(int)
        money_traj = []
        prev_money = None
        rev_by_item = defaultdict(float)
        shed_sell_units = defaultdict(int)
        shed_peak = 0
        shed_end = {}
        saturation_events = defaultdict(int)  # animal -> count of tiles at max_held
        weeds = 0
        unwatered_now = 0
        seeds_end = {}
        animal_yields_end = defaultdict(int)
        plant_yields_end = defaultdict(int)
        standing_plants = defaultdict(int)
        hires_per_day = defaultdict(int)
        hands_hist = []
        eggs_shed_peak = 0
        pass_count = 0
        act_count = 0

        prev_shed = {}
        for r in recs:
            step = r["step"]
            day = step // 24
            hour = step % 24
            farm = r["farms"][seat]
            priv = r["priv"][seat]
            act = r["acts"][seat]

            money_traj.append((step, farm["money"]))
            hands_hist.append((step, len(farm.get("hands", []))))

            for a in unit_actions(act):
                act_count += 1
                if not a:
                    continue
                op = a[0]
                if op == "CARE":
                    care_ops[day] += 1
                elif op == "FERTILIZE":
                    fert_ops[a[1] if len(a) > 1 else "?"] += 1
                elif op == "COLLECT_FERTILIZER":
                    collectfert_ops += 1
                elif op == "HARVEST":
                    harvest_ops += 1
                elif op == "PASS":
                    pass_count += 1

            for o in market_orders(act):
                if isinstance(o, list) and o and o[0] == "SELL" and len(o) >= 3:
                    item = o[1]
                    n = o[2]
                    sell_hours[hour] += 1
                    sell_by_item_hour[item][hour] += n

            # money delta attribution -> sells revenue
            if prev_money is not None:
                dm = farm["money"] - prev_money
                if dm > 0:
                    # approximate split per item by shed decrease
                    for item, v in priv["shed"].items():
                        d = prev_shed.get(item, 0) - v
                        if d > 0 and item in rev_by_item.__class__():
                            pass
                # simpler: revenue only tracked via executed analysis below
            prev_money = farm["money"]

            # shed delta -> executed sell units
            for item, v in priv["shed"].items():
                d = prev_shed.get(item, 0) - v
                if d > 0:
                    shed_sell_units[item] += d
                if item == "EGG" and v > eggs_shed_peak:
                    eggs_shed_peak = v
            prev_shed = dict(priv["shed"])

            occ = sum(priv["shed"].values())
            if occ > shed_peak:
                shed_peak = occ

            for row in farm["tiles"]:
                for t in row:
                    if isinstance(t, dict):
                        if t.get("animal"):
                            if t.get("yield_units", 0) >= MAX_HELD.get(t["animal"], 0):
                                saturation_events[t["animal"]] += 1
                        elif t.get("kind") == "PLANT":
                            pass
                        elif t.get("kind") == "WEED":
                            weeds += 1

        # end state from last turn
        last = recs[-1]
        farm = last["farms"][seat]
        priv = last["priv"][seat]
        shed_end = dict(priv["shed"])
        seeds_end = dict(priv.get("seeds", {}))
        for row in farm["tiles"]:
            for t in row:
                if isinstance(t, dict):
                    if t.get("animal"):
                        animal_yields_end[t["animal"]] += t.get("yield_units", 0)
                        standing_plants["ANIMAL:" + t["animal"]] += 1
                    elif t.get("kind") == "PLANT":
                        plant_yields_end[t["crop"]] += t.get("yield_units", 0)
                        standing_plants["PLANT:" + t["crop"]] += 1

        total_animal_days = sum(
            standing_plants.get("ANIMAL:" + k, 0) for k in MAX_HELD
        ) * 30  # rough
        print(f"\n-- {tag}: final money ${last['farms'][seat]['money']:,}")
        print(f"   CARE ops by day: {dict(sorted(care_ops.items()))}")
        print(f"   CARE total: {sum(care_ops.values())}  (animal-days ~{total_animal_days})")
        print(f"   FERTILIZE ops by crop: {dict(fert_ops)}  | COLLECT_FERTILIZER: {collectfert_ops}")
        print(f"   HARVEST ops: {harvest_ops} | PASS among unit-actions: {pass_count}/{act_count}")
        print(f"   SELL hour histogram: {dict(sorted(sell_hours.items()))}")
        print(f"   shed sell units (executed, approx): {dict(shed_sell_units)}")
        print(f"   shed peak occupancy: {shed_peak}/100 | EGG shed peak: {eggs_shed_peak}")
        print(f"   END shed: {shed_end}")
        print(f"   END seeds: {seeds_end}")
        print(f"   END animal yields unharvested: {dict(animal_yields_end)}")
        print(f"   END plant yields unharvested: {dict(plant_yields_end)}")
        print(f"   END standing: {dict(standing_plants)}")
        print(f"   saturation (tile-events at max_held): {dict(saturation_events)}")
        print(f"   weeds seen: {weeds}")
        print(f"   money min/max: ${min(m for _, m in money_traj):,} / ${max(m for _, m in money_traj):,}")
        print(f"   hands peak: {max(h for _, h in hands_hist)}")


if __name__ == "__main__":
    base = "/home/z/my-project/kaggriculture/battles/"
    audit(base + "t79_replay_v16_ahmedv41_s364.jsonl", 1, "ahmedv41")
    audit(base + "t79_replay_v16_ahmedv41_s365.jsonl", 1, "ahmedv41")
    audit(base + "t79_replay_kme3v39_ahmedv41_s362.jsonl", 1, "ahmedv41")
