#!/usr/bin/env python3
"""Phân tích ĐẤT TRỐNG kain33 theo thời kỳ (Task 34 — Phase 1).

Vào: các trận kain33 vs v6 (JSONL run_battle format).
Ra (cho farm kain33 và farm v6 đối chiếu):
  - Bảng theo ngày (h23): sức chứa (ô mở khoá), cây đứng, trống, trống%,
    tiền, thợ (farmer+hands)
  - Fill-time: số ngày sau BUY_LAND để trống% rơi xuống <=15%
  - Empty% trung bình theo thời kỳ: d0-4 / d5-9 / d10-14 / d15-19 / d20-28
"""
import json, glob, sys, os
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
    buys = []          # (day, pid)
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
                step, day, hour = d.get("step", 0), d.get("day", 0), d.get("hour", 0)
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


def pick_seat(a_name, b_name, target):
    """target = 'kain' hoặc 'v6' -> pid trong farms."""
    if target in (a_name or ""):
        return 0
    if target in (b_name or ""):
        return 1
    # file path chứa tên
    return None


def main():
    paths = sys.argv[1:]
    if not paths:
        paths = sorted(glob.glob("/home/z/my-project/kaggriculture/battles/battle_178904[3-4]*.jsonl"))
    games = []
    for p in paths:
        a, b, days, buys, rewards = analyze(p)
        if not (a and b):
            continue
        k_pid = None
        if "kain33" in str(a) or "kain33" in str(b):
            k_pid = 0 if "kain33" in str(a) else 1
        if k_pid is None:
            continue
        games.append({"path": os.path.basename(p), "a": a, "b": b, "days": days,
                      "buys": buys, "rewards": rewards, "k": k_pid, "v": 1 - k_pid})

    print(f"=== {len(games)} trận kain33 vs v6 ===\n")
    # gom theo ngày: mean empty% cho kain33 và v6
    agg = defaultdict(lambda: {"k": [], "v": [], "k_cap": [], "v_cap": [], "k_m": [], "k_u": []})
    for g in games:
        for d, snaps in g["days"].items():
            (kcap, kpl, kem), ku, km, kq = snaps[g["k"]]
            (vcap, vpl, vem), vu, vm, vq = snaps[g["v"]]
            agg[d]["k"].append(100.0 * kem / max(1, kcap))
            agg[d]["v"].append(100.0 * vem / max(1, vcap))
            agg[d]["k_cap"].append(kcap)
            agg[d]["v_cap"].append(vcap)
            agg[d]["k_m"].append(km)
            agg[d]["k_u"].append(ku)

    print(f"{'day':>4} {'k_empty%':>9} {'v_empty%':>9} {'k_cap':>7} {'v_cap':>7} {'k_money':>9} {'k_units':>8}")
    for d in sorted(agg):
        a = agg[d]
        km = sum(x for x in a["k_m"] if x is not None) / max(1, len([x for x in a["k_m"] if x is not None]))
        print(f"{d:>4} {sum(a['k'])/len(a['k']):>8.1f}% {sum(a['v'])/len(a['v']):>8.1f}% "
              f"{sum(a['k_cap'])/len(a['k_cap']):>7.1f} {sum(a['v_cap'])/len(a['v_cap']):>7.1f} "
              f"{km:>9.0f} {sum(a['k_u'])/len(a['k_u']):>8.1f}")

    # giai đoạn
    def phase_avg(dd, who):
        xs = [x for d in dd for x in agg[d][who]] if dd else []
        return sum(xs) / max(1, len(xs))
    phases = [("d0-4", range(0, 5)), ("d5-9", range(5, 10)), ("d10-14", range(10, 15)),
              ("d15-19", range(15, 20)), ("d20-28", range(20, 29))]
    print("\n=== EMPTY% THEO THỜI KỲ (kain33 / v6) ===")
    for name, dd in phases:
        print(f"  {name:7s}: kain33 {phase_avg(dd,'k'):5.1f}%   v6 {phase_avg(dd,'v'):5.1f}%")

    # BUY_LAND + fill-time từng trận
    print("\n=== BUY_LAND & FILL-TIME TỪNG TRẬN (kain33) ===")
    for g in games:
        kbuys = [d for d, p in g["buys"] if p == g["k"]]
        vbuys = [d for d, p in g["buys"] if p == g["v"]]
        if not g["days"]:
            continue
        def empty_at(day):
            if day not in g["days"]:
                return None
            (cap, pl, em), u, m, q = g["days"][day][g["k"]]
            return 100.0 * em / max(1, cap)
        fills = []
        for bd in kbuys:
            ft = None
            for d2 in range(bd, 29):
                e = empty_at(d2)
                if e is not None and e <= 15.0:
                    ft = d2 - bd
                    break
            e_bd = empty_at(bd)
            e_3 = empty_at(min(28, bd + 3))
            fills.append((bd, e_bd, e_3, ft))
        last = g["days"].get(max(g["days"]))
        if last:
            (kcap, kpl, kem), ku, km, kq = last[g["k"]]
            r = g["rewards"] or [0, 0]
            print(f"  {g['path'][:34]:36s} kbuy_d={kbuys} vbuy_d={vbuys} "
                  f"final: empty={kem}/{kcap} ({100*kem/max(1,kcap):.0f}%) money=${km:,.0f} r={g['rewards']}")
            for bd, e_bd, e_3, ft in fills:
                print(f"      buy d{bd}: empty ngay sau={e_bd if e_bd is None else round(e_bd)}% "
                      f"-> +3d={e_3 if e_3 is None else round(e_3)}% -> ve <=15% sau {ft} ngay")


if __name__ == "__main__":
    main()
