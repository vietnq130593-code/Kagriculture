#!/usr/bin/env python3
"""MOVE-ANATOMY — đo CÁC UNIT di chuyển thế nào, giữa task nào, dài bao nhiêu.

Cho 1 replay + seat: với mỗi unit (farmer + hands), trích chuỗi hành động
đơn giản hóa: [U=useful op, M=move, P=pass, K=market]. Thống kê:
  1. MOVE/unit/ngày — ai đi nhiều nhất
  2. Run-length: chuỗi M liên tiếp trước mỗi U (0,1,2,3,...)
  3. Khoảng cách Manhattan giữa 2 task LIÊN TIẾP của cùng unit (0=stack!)
  4. Phân bố nước đi theo giờ (commute sáng?)

Cách dùng: python3 moveana.py <replay.jsonl> <seat>
"""
import json
import sys
from collections import defaultdict

def main():
    path = sys.argv[1]
    seat = int(sys.argv[2])
    mv_per_unit_day = defaultdict(int)
    run_before_useful = defaultdict(int)
    dist_between_tasks = defaultdict(int)
    useful_ops = defaultdict(int)
    last_task_pos = {}
    cur_run = defaultdict(int)

    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        if ev.get("t") != "turn":
            continue
        day, step = ev["day"], ev["step"]
        acts = (ev.get("acts") or [None, None])[seat]
        if not isinstance(acts, dict):
            continue
        farm = ev["farms"][seat]
        units = [tuple(farm.get("farmer") or (-1, -1))] + [tuple(p) for p in (farm.get("hands") or [])]
        seqs = [acts.get("farmer") or ["PASS"]] + [u or ["PASS"] for u in (acts.get("hands") or [])]
        for ui, mv in enumerate(seqs):
            op = mv[0] if isinstance(mv, list) and mv else (mv if isinstance(mv, str) else "PASS")
            if op in ("NORTH", "SOUTH", "EAST", "WEST"):
                mv_per_unit_day[(ui, day)] += 1
                cur_run[ui] += 1
            else:
                if op in ("WATER", "HARVEST", "FEED", "CARE", "COLLECT_FERTILIZER",
                          "PLANT", "FERTILIZE", "DIG", "BUILD_COOP", "BUILD_PASTURE"):
                    useful_ops[ui] += 1
                    run_before_useful[cur_run[ui]] += 1
                    cur_run[ui] = 0
                    pos = units[ui] if ui < len(units) else None
                    prev = last_task_pos.get(ui)
                    if pos and prev:
                        d = abs(pos[0] - prev[0]) + abs(pos[1] - prev[1])
                        dist_between_tasks[d] += 1
                    if pos:
                        last_task_pos[ui] = pos
                else:
                    cur_run[ui] = 0  # PASS/market reset chain
        # market orders count per unit index via lockstep — bỏ qua chi tiết

    n_units = max(u for u, _ in mv_per_unit_day) + 1 if mv_per_unit_day else 0
    print("== MOVE/unit/ngày (trung bình) ==")
    for ui in range(n_units):
        tot = sum(v for (u, d), v in mv_per_unit_day.items() if u == ui)
        nd = len({d for (u, d) in mv_per_unit_day if u == ui})
        print(f"  unit{ui:>2}: {tot/max(1,nd):6.1f} move/ngày | useful cả mùa {useful_ops.get(ui,0):4d}")
    print("\n== Chuỗi MOVE trước mỗi useful op ==")
    tot_runs = sum(run_before_useful.values())
    for r in sorted(run_before_useful):
        print(f"  run {r}: {run_before_useful[r]:5d} ({100*run_before_useful[r]/max(1,tot_runs):4.1f}%)")
    print("\n== Khoảng cách giữa 2 task liên tiếp cùng unit ==")
    tot_d = sum(dist_between_tasks.values())
    for d in sorted(dist_between_tasks):
        if dist_between_tasks[d] >= 20:
            print(f"  dist {d}: {dist_between_tasks[d]:5d} ({100*dist_between_tasks[d]/max(1,tot_d):4.1f}%)")
    gap0 = dist_between_tasks.get(0, 0)
    gap1 = dist_between_tasks.get(1, 0)
    print(f"\n  gap-0: {100*gap0/max(1,tot_d):.1f}% | gap-1: {100*gap1/max(1,tot_d):.1f}% | tổng task-pairs {tot_d}")

if __name__ == "__main__":
    main()
