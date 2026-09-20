#!/usr/bin/env python3
"""T113 — AUDIT 4 NHÓM của v27.2 (cây / động vật / lao động / kho) + thị trường.

Input : battles/*.jsonl (tape run_battle.py)
Output: stdout báo cáo tổng hợp + bench/t113_audit_<tag>.json

Phân tích:
  1. CÂY TRỒNG     — empty% đất mở, weed, crop mix, cây sẵn-sàng-chưa-thu,
                     cây unwatered chết, yield chờ trên cây
  2. ĐỘNG VẬT      — coop/pasture TRỐNG (lãng phí cơ hội), nuôi gì,
                     sản lượng EGG/MILK/WOOL thu về, chi phí feed
  3. LAO ĐỘNG      — số hands mỗi ngày, PASS/idle %, cơ cấu ops,
                     tiền hire (ước lượng qua BUY/HIRE ops), capacity dùng
  4. KHO           — shed tồn cuối ngày, hàng chết cuối game, seeds dư,
                     vật mang theo (inventories) đọng
  5. THỊ TRƯỜNG    — mọi SELL (item, qty, giá, ngày), mọi BUY (loại),
                     curve giá trung bình theo ngày
"""
import json, sys, glob
from collections import defaultdict

CROPS = ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON")
ANIMALS = ("GOOSE", "COW", "SHEEP")
ITEMS = CROPS + ("EGG", "MILK", "WOOL")

def tiles_census(farm):
    c = defaultdict(int)
    for row in farm["tiles"]:
        for t in row:
            if t == "LOCKED":
                c["locked"] += 1
            elif t is None:
                c["empty"] += 1
            else:
                k = t.get("kind")
                if k == "WEED":
                    c["weed"] += 1
                elif k == "PLANT":
                    c["plant_" + t["crop"]] += 1
                    if t.get("yield_units", 0) >= 2:
                        c["ready_unharvested"] += 1
                    if t.get("consecutive_unwatered", 0) >= 1:
                        c["unwatered"] += 1
                elif k in ("COOP", "PASTURE"):
                    if t.get("animal"):
                        c[f"{k.lower()}_{t['animal'].lower()}"] += 1
                    else:
                        c[f"{k.lower()}_EMPTY"] += 1
                else:
                    c["other_" + str(k)] += 1
    c["unlocked"] = 100 - c["locked"]
    return c

def analyze(path, tag):
    days = {}            # day -> per-seat snapshot hour 23
    sells = []           # (day, pid, item, qty, price)
    buys = defaultdict(list)  # pid -> (day, op, item, qty, price)
    hands_count = defaultdict(lambda: [0, 0])
    ops_day = defaultdict(lambda: defaultdict(int))  # day -> op -> count (both seats)
    pass_day = defaultdict(lambda: [0, 0])
    rewards = None
    seed = None
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            t = d.get("t")
            if t == "hello":
                seed = d.get("seed")
                continue
            if t == "end":
                rewards = d.get("rewards")
                continue
            if t != "turn":
                continue
            day, step = d.get("day"), d.get("step")
            prices = d["market"]["prices"]
            inv = d["market"]["inventory"]
            for pid, acts in enumerate(d["acts"]):
                # hands
                hs = acts.get("hands") or []
                if hs:
                    hands_count[day][pid] = max(hands_count[day][pid], len(hs))
                # unit ops
                fr = acts.get("farmer")
                all_units = ([fr] if fr else []) + list(hs)
                for u in all_units:
                    if not u:
                        pass_day[day][pid] += 1
                        ops_day[day]["PASS"] += 1
                        continue
                    op = u[0] if isinstance(u, list) else str(u)
                    ops_day[day][op] += 1
                # market ops
                for m in (acts.get("market") or []):
                    if not m:
                        continue
                    op = m[0]
                    if op == "SELL" and len(m) >= 3:
                        sells.append((day, pid, m[1], m[2], prices.get(m[1])))
                    else:
                        item = m[1] if len(m) > 1 else "?"
                        qty = m[2] if len(m) > 2 else 0
                        buys[pid].append((day, op, item, qty, prices.get(item)))
            # snapshot end-of-day (hour 23)
            if d.get("hour") == 23:
                for pid, farm in enumerate(d["farms"]):
                    priv = d["priv"][pid]
                    c = tiles_census(farm)
                    snap = {
                        "money": farm["money"],
                        "hands": len(farm.get("hands") or []),
                        "hires_today": farm.get("hires_today", 0),
                        "quadrants": farm.get("unlocked_quadrants", 0),
                        "census": dict(c),
                        "shed": dict(priv.get("shed") or {}),
                        "seeds": dict(priv.get("seeds") or {}),
                        "inv_carry": {k: v for k, v in (priv.get("inventories") or [{}])[0].items()} if priv.get("inventories") else {},
                    }
                    days.setdefault(day, {})[pid] = snap

    # ---- aggregate report ----
    R = {"tag": tag, "seed": seed, "rewards": rewards, "path": path}
    n_days = max(days) + 1 if days else 0

    # 1. CÂY TRỒNG — trung bình các ngày
    empty_pct = []
    ready_unh = []
    unwatered = []
    weed_l = []
    crop_mix = defaultdict(int)
    for day in range(10, n_days):  # bỏ 10 ngày đầu (mở đất)
        for pid in (0, 1):
            s = days.get(day, {}).get(pid)
            if not s:
                continue
            c = s["census"]
            empty = c.get("empty", 0)
            unlocked = c.get("unlocked", 0) or (100 - c.get("locked", 100))
            if unlocked > 0:
                empty_pct.append(100.0 * empty / unlocked)
                ready_unh.append(c.get("ready_unharvested", 0))
                unwatered.append(c.get("unwatered", 0))
                weed_l.append(c.get("weed", 0))
            for cr in CROPS:
                crop_mix[cr] += c.get("plant_" + cr, 0)
    R["crops"] = {
        "empty_pct_after_d10": {
            "mean": round(sum(empty_pct) / len(empty_pct), 2) if empty_pct else None,
            "max": round(max(empty_pct), 2) if empty_pct else None,
            "last10_mean": round(sum(empty_pct[-20:]) / max(1, len(empty_pct[-20:])), 2),
        },
        "ready_unharvested_mean": round(sum(ready_unh) / max(1, len(ready_unh)), 2),
        "unwatered_mean": round(sum(unwatered) / max(1, len(unwatered)), 2),
        "weed_mean": round(sum(weed_l) / max(1, len(weed_l)), 2),
        "crop_mix_total": dict(crop_mix),
    }

    # 2. ĐỘNG VẬT
    struct_empty = defaultdict(int)
    animal_counts = defaultdict(int)
    animal_shed = defaultdict(int)
    for day in range(10, n_days):
        for pid in (0, 1):
            s = days.get(day, {}).get(pid)
            if not s:
                continue
            c = s["census"]
            for k in ("coop_empty", "pasture_empty"):
                struct_empty[k] += c.get(k, 0)
            for a in ANIMALS:
                animal_counts[a] += c.get("pasture_" + a.lower(), 0) + c.get("coop_" + a.lower(), 0)
            sh = s["shed"]
            for it in ("EGG", "MILK", "WOOL"):
                animal_shed[it] += sh.get(it, 0)
    R["animals"] = {
        "coop_empty_dayavg": round(struct_empty["coop_empty"] / max(1, 2 * (n_days - 10)), 2),
        "pasture_empty_dayavg": round(struct_empty["pasture_empty"] / max(1, 2 * (n_days - 10)), 2),
        "animal_dayavg": {a: round(animal_counts[a] / max(1, 2 * (n_days - 10)), 2) for a in ANIMALS},
        "shed_deadstock_endgame": dict(animal_shed),
    }

    # 3. LAO ĐỘNG
    hands_by_day = []
    pass_by_day = []
    for day in range(10, n_days):
        hs = [hands_count[day][p] for p in (0, 1)]
        hands_by_day.append(sum(hs))
        ps = [pass_day[day][p] for p in (0, 1)]
        pass_by_day.append(sum(ps))
    total_hands_days = sum(hands_by_day)
    R["labor"] = {
        "hands_mean_per_seat_day": round(total_hands_days / max(1, 2 * (n_days - 10)), 2),
        "hands_last10_per_seat_day": round(sum(hands_by_day[-10:]) / max(1, 20), 2),
        "pass_unit_turns_total": sum(pass_by_day),
        "pass_pct_of_unit_turns": round(100.0 * sum(pass_by_day) / max(1, sum(hands_by_day) * 24 + 2 * 24 * (n_days - 10)), 2),
        "hire_ops": sum(1 for pid in buys for b in buys[pid] if b[1] == "HIRE"),
    }

    # 4. KHO
    end_shed = {}
    end_seeds = {}
    for pid in (0, 1):
        s = days.get(n_days - 1, {}).get(pid) or days.get(max(days), {}).get(pid)
        if s:
            for k, v in s["shed"].items():
                end_shed[k] = end_shed.get(k, 0) + v
            for k, v in s["seeds"].items():
                end_seeds[k] = end_seeds.get(k, 0) + v
    # shed tồn trung bình các ngày cuối (d20+)
    shed_late = defaultdict(int)
    n_late = 0
    for day in range(20, n_days):
        for pid in (0, 1):
            s = days.get(day, {}).get(pid)
            if s:
                n_late += 1
                for k, v in s["shed"].items():
                    shed_late[k] += v
    R["storage"] = {
        "end_shed_both_seats": dict(end_shed),
        "end_seeds_both_seats": dict(end_seeds),
        "shed_late_mean_per_seat": {k: round(v / max(1, n_late), 2) for k, v in shed_late.items()},
    }

    # 5. THỊ TRƯỜNG
    sell_by_item = defaultdict(lambda: {"qty": 0, "rev": 0.0, "n": 0, "price_sum": 0.0})
    for day, pid, item, qty, price in sells:
        b = sell_by_item[item]
        b["qty"] += qty
        b["rev"] += qty * (price or 0)
        b["n"] += 1
        b["price_sum"] += price or 0
    R["market"] = {
        "sells_by_item": {
            it: {
                "qty": b["qty"],
                "revenue": round(b["rev"], 0),
                "avg_price": round(b["price_sum"] / max(1, b["n"]), 1),
                "orders": b["n"],
            } for it, b in sell_by_item.items()
        },
        "buys_summary": {},
    }
    buyagg = defaultdict(lambda: {"qty": 0, "n": 0, "cost": 0.0})
    for pid in buys:
        for day, op, item, qty, price in buys[pid]:
            k = f"{op}:{item}"
            buyagg[k]["qty"] += qty if isinstance(qty, (int, float)) else 0
            buyagg[k]["n"] += 1
            buyagg[k]["cost"] += (qty if isinstance(qty, (int, float)) else 0) * (price if isinstance(price, (int, float)) else 0)
    R["market"]["buys_summary"] = {k: {"qty": v["qty"], "orders": v["n"]} for k, v in sorted(buyagg.items())}

    # price curve (day-mean, market is shared)
    price_curve = defaultdict(lambda: defaultdict(list))
    # re-scan tape for prices
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") != "turn":
                continue
            day = d.get("day")
            if d.get("hour") == 23:
                for it, p in d["market"]["prices"].items():
                    price_curve[it][day].append(p)
    R["price_curve_end_day"] = {
        it: [round(sum(vs) / len(vs), 1) for day, vs in sorted(dc.items())]
        for it, dc in price_curve.items()
    }
    return R

if __name__ == "__main__":
    tag = sys.argv[1] if len(sys.argv) > 1 else "audit"
    paths = sys.argv[2:] or glob.glob("/home/z/my-project/kaggriculture/battles/t113_*.jsonl")
    allR = []
    for p in paths:
        R = analyze(p, tag + ":" + p.split("/")[-1])
        allR.append(R)
        print(json.dumps({k: v for k, v in R.items() if k != "price_curve_end_day"}, indent=1))
    out = f"/home/z/my-project/kaggriculture/bench/t113_audit_{tag}.json"
    json.dump(allR, open(out, "w"), indent=1)
    print("saved:", out)
