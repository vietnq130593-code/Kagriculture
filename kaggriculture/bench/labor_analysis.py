#!/usr/bin/env python3
"""Tìm RÀNG BUỘC THẬT SỰ khiến đất trống: đếm hành động mỗi ngày của mỗi unit.

Mỗi unit mỗi turn: hoặc MOVE hoặc 1 action (PLANT/WATER/HARVEST/...).
Capacity/ngày = hands × 24 turn. Đo mức dùng + cơ cấu action.
"""
import json, sys
from collections import defaultdict

def flat_actions(acts):
    """Trả về list (unit_idx, op) từ cấu trúc acts."""
    out = []
    for grp in (acts.get("market") or []):
        if grp:
            out.append(("mkt", grp[0] if isinstance(grp, list) else "?"))
    f = acts.get("farmer") or []
    if f:
        out.append(("farmer", f[0] if isinstance(f, list) else f))
    for i, h in enumerate(acts.get("hands") or []):
        if h:
            out.append((f"h{i}", h[0] if isinstance(h, list) else h))
    return out

def main(path):
    day_stats = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))  # day -> pid -> op -> count
    day_hands = defaultdict(lambda: [0, 0])
    day_idle = defaultdict(lambda: [0, 0])
    day_moves = defaultdict(lambda: [0, 0])
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") != "turn":
                continue
            day = d.get("day", d["step"] // 24)
            for pid, acts in enumerate(d.get("acts", [])):
                n_units = 1 + len(acts.get("hands") or [])
                day_hands[day][pid] = max(day_hands[day][pid], len(acts.get("hands") or []))
                ops = flat_actions(acts)
                n_act = 0
                for who, op in ops:
                    day_stats[day][pid][op] += 1
                    if op == "MOVE":
                        day_moves[day][pid] += 1
                    elif op not in ("PASS",):
                        n_act += 1
                    elif op == "PASS":
                        day_idle[day][pid] += 1
                # PASS đếm như rảnh
    print(f"{'day':>4} | {'v5: hands':>10} {'PLANT':>7} {'WATER':>7} {'HARV':>7} {'SELL':>6} {'BUY*':>6} {'MOVE':>6} {'PASS':>6} {'FW':>5} {'SERV':>6} | v4 hands PASS")
    for day in sorted(day_stats):
        if day % 3 != 0 and day not in (1, 2, 27, 28):
            continue
        s5 = day_stats[day][0]; s4 = day_stats[day][1]
        tot5 = sum(s5.values())
        def g(s, k): return s.get(k, 0)
        buys = g(s5, "BUY_SEED") + g(s5, "BUY_ANIMAL") + g(s5, "BUY_PRODUCT") + g(s5, "BUY_LAND")
        fw = g(s5, "FEED") + g(s5, "WATER_CROP")  # có thể không tồn tại
        serv = g(s5, "COLLECT") + g(s5, "CARE") + g(s5, "FEED")
        print(f"{day:>4} | {day_hands[day][0]:>10} {g(s5,'PLANT'):>7} {g(s5,'WATER'):>7} {g(s5,'HARVEST'):>7} {g(s5,'SELL'):>6} {buys:>6} {g(s5,'MOVE'):>6} {g(s5,'PASS'):>6} {g(s5,'FEED'):>5} {g(s5,'CARE')+g(s5,'COLLECT'):>6} | {day_hands[day][1]:>5} {g(s4,'PASS'):>4}")
        _ = tot5
    # Tổng capacity d15-25
    print("\n=== NĂNG SUẤT LAO ĐỘNG d15-25 (v5) ===")
    used = idle = moves = hands_days = 0
    for day in range(15, 26):
        if day not in day_stats:
            continue
        s5 = day_stats[day][0]
        h = day_hands[day][0] + 1  # +farmer
        hands_days += h
        idle += day_idle[day][0]
        moves += day_moves[day][0]
        used += sum(v for k, v in s5.items() if k != "MOVE")
    cap = hands_days * 24
    print(f"Capacity: {hands_days} unit-days × 24 = {cap} action-slots")
    print(f"Đã dùng (không tính MOVE): {used}  |  MOVE: {moves}  |  PASS: {idle}")
    print(f"→ Mức dùng thực (MOVE+action)/capacity = {(used+moves)/cap*100:.0f}%  (nếu MOVE tính là việc)")
    print(f"→ Action hiệu dụng/capacity = {used/cap*100:.0f}%")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/kaggriculture/battles/battle_1788934268119.jsonl")
