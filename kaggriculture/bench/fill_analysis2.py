#!/usr/bin/env python3
"""Phân tích ĐẤT TRỐNG tổng quát (Task 35 — nâng cấp từ fill_analysis.py).

Vào: các trận <agent> vs v6 (JSONL run_battle format) + tên agent mục tiêu.
Ra (cho farm agent và farm v6 đối chiếu):
  - Bảng theo ngày (h23): empty%, cap, planted, tiền, thợ
  - MAX empty% mỗi ngày (đường trên, mục tiêu <=15% trừ ngày cuối)
  - Empty% trung bình theo thời kỳ: d0-4 / d5-9 / d10-14 / d15-19 / d20-24 / d25-28
  - Fill-time sau mỗi lần BUY_LAND
"""
import json, glob, sys, os, argparse
from collections import defaultdict


def tile_stats(tiles):
    cap = planted = empty = 0
    for row in tiles:
        for t in row:
            if t == "LOCKED":
                continue
            cap += 1
            if t is None:
                empty += 1
            else:
                planted += 1
    return cap, planted, empty


def analyze(path):
    days = {}
    buys = []
    a_name = b_name = None
    rewards = None
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            t = d.get("t")
            if t == "hello":
                a_name, b_name = d.get("a"), d.get("b")
            elif t == "turn":
                day, hour = d.get("day", 0), d.get("hour", 0)
                for pid, acts in enumerate(d.get("acts") or []):
                    for grp in (acts.get("market") or []) if isinstance(acts, dict) else []:
                        if grp and grp[0] == "BUY_LAND":
                            buys.append((day, pid))
                if hour == 23:
                    days[day] = [
                        (tile_stats(fr["tiles"]),
                         len(fr.get("hands") or []),
                         fr.get("money"),
                         len(fr.get("unlocked_quadrants") or []))
                        for fr in d.get("farms") or []
                    ]
            elif t == "end":
                rewards = d.get("rewards")
    return a_name, b_name, days, buys, rewards


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="kain38")
    ap.add_argument("--paths", nargs="*", default=None)
    ap.add_argument("--skip-last", type=int, default=2, help="số ngày cuối được miễn <=15%")
    args = ap.parse_args()
    target = args.target

    paths = args.paths
    if not paths:
        paths = sorted(glob.glob("/home/z/my-project/kaggriculture/battles/battle_*.jsonl"))
    games = []
    for p in paths:
        a, b, days, buys, rewards = analyze(p)
        if not (a and b):
            continue
        if target in str(a):
            k_pid = 0
        elif target in str(b):
            k_pid = 1
        else:
            continue
        games.append({"path": os.path.basename(p), "a": a, "b": b, "days": days,
                      "buys": buys, "rewards": rewards, "k": k_pid, "v": 1 - k_pid})

    if not games:
        print(f"Không tìm thấy trận nào của {target}")
        return
    print(f"=== {len(games)} trận {target} vs v6 ===\n")
    agg = defaultdict(lambda: {"k": [], "v": [], "k_cap": [], "k_pl": [], "k_m": [], "k_u": []})
    for g in games:
        for d, snaps in g["days"].items():
            (kcap, kpl, kem), ku, km, kq = snaps[g["k"]]
            (vcap, vpl, vem), vu, vm, vq = snaps[g["v"]]
            agg[d]["k"].append(100.0 * kem / max(1, kcap))
            agg[d]["v"].append(100.0 * vem / max(1, vcap))
            agg[d]["k_cap"].append(kcap)
            agg[d]["k_pl"].append(kpl)
            agg[d]["k_m"].append(km)
            agg[d]["k_u"].append(ku)

    print(f"{'day':>4} {'mean%':>6} {'MAX%':>6} {'nG':>3} | {'k_cap':>6} {'k_plant':>8} {'k_money':>9} {'k_units':>8} {'v6_empty%':>10}")
    viol_days = 0
    for d in sorted(agg):
        a = agg[d]
        km = sum(x for x in a["k_m"] if x is not None) / max(1, len([x for x in a["k_m"] if x is not None]))
        mx = max(a["k"])
        flag = ""
        if d <= 28 - args.skip_last and mx > 15.0:
            flag = " <<<"
            viol_days += 1
        print(f"{d:>4} {sum(a['k'])/len(a['k']):>5.1f}% {mx:>5.1f}% {len(a['k']):>3} | "
              f"{sum(a['k_cap'])/len(a['k_cap']):>6.1f} {sum(a['k_pl'])/len(a['k_pl']):>8.1f} "
              f"{km:>9.0f} {sum(a['k_u'])/len(a['k_u']):>8.1f} {sum(a['v'])/len(a['v']):>9.1f}%{flag}")

    def phase_avg(dd, who):
        xs = [x for d in dd for x in agg[d][who]] if dd else []
        return sum(xs) / max(1, len(xs))
    phases = [("d0-4", range(0, 5)), ("d5-9", range(5, 10)), ("d10-14", range(10, 15)),
              ("d15-19", range(15, 20)), ("d20-24", range(20, 25)), ("d25-28", range(25, 29))]
    print(f"\n=== EMPTY% THEO THỜI KỲ ({target} / v6) ===")
    for name, dd in phases:
        print(f"  {name:7s}: {target} {phase_avg(dd,'k'):5.1f}%   v6 {phase_avg(dd,'v'):5.1f}%")
    print(f"\nNgày VI PHẠM >15% (trừ {args.skip_last} ngày cuối): {viol_days} ngày")

    print(f"\n=== BUY_LAND & FILL-TIME TỪNG TRẬN ({target}) ===")
    for g in games:
        kbuys = [d for d, p in g["buys"] if p == g["k"]]
        if not g["days"]:
            continue
        def empty_at(day):
            if day not in g["days"]:
                return None
            (cap, pl, em), u, m, q = g["days"][day][g["k"]]
            return 100.0 * em / max(1, cap)
        last = g["days"].get(max(g["days"]))
        if last:
            (kcap, kpl, kem), ku, km, kq = last[g["k"]]
            print(f"  {g['path'][:30]:32s} kbuy_d={kbuys} final: empty={kem}/{kcap} "
                  f"({100*kem/max(1,kcap):.0f}%) money=${km:,.0f} r={g['rewards']}")
        for bd in kbuys:
            ft = None
            for d2 in range(bd, 29):
                e = empty_at(d2)
                if e is not None and e <= 15.0:
                    ft = d2 - bd
                    break
            e_bd = empty_at(bd)
            e_2 = empty_at(min(28, bd + 2))
            print(f"      buy d{bd}: empty ngay sau={e_bd if e_bd is None else round(e_bd)}% "
                  f"-> +2d={e_2 if e_2 is None else round(e_2)}% -> ve <=15% sau {ft} ngay")


if __name__ == "__main__":
    main()
