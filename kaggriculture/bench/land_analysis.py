#!/usr/bin/env python3
"""Phân tích định lượng ĐẤT TRỐNG (empty land) trên battles JSONL.

Trả lời 2 câu hỏi của user:
  Q1: Mua đất có lãng phí tài nguyên không?
  Q2: Chiến lược tối ưu đất + phân bổ tài nguyên là gì?

Phương pháp: với mỗi turn, đếm trạng thái ô (LOCKED / null-trống / cây),
đối chiếu với hành động BUY_LAND, tiền, số thợ, để tìm ràng buộc thật sự
khiến đất trống: thiếu thợ? thiếu nước? thiếu hạt? hay quota tự giới hạn?
"""
import json, glob, sys, os
from collections import defaultdict

def tile_states(tiles):
    """Trả về (locked, empty, crops, crop_mix) cho 10x10 grid."""
    locked = empty = crops = 0
    mix = defaultdict(int)
    for row in tiles:
        for t in row:
            if t == "LOCKED":
                locked += 1
            elif t is None:
                empty += 1
            else:
                crops += 1
                k = t.get("kind") if isinstance(t, dict) else "?"
                mix[k] += 1
    return locked, empty, crops, dict(mix)

def analyze(path):
    days = defaultdict(lambda: None)   # day -> snapshot at hour 23 (end of day)
    buys = []                          # (step, day, which_player)
    a_name = b_name = None
    rewards = None
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            t = d.get("t")
            if t == "hello":
                a_name, b_name = d.get("a"), d.get("b")
            elif t == "turn":
                step = d["step"]; day = d.get("day", step // 24)
                for pid, acts in enumerate(d.get("acts", [])):
                    flat = []
                    for grp in (acts.get("market") or []):
                        flat.append(grp[0] if grp else None)
                    if "BUY_LAND" in flat:
                        buys.append((step, day, pid))
                # snapshot cuối ngày (hour 23) — trạng thái ổn định sau auto-drop
                if d.get("hour") == 23:
                    snaps = []
                    for farm in d["farms"]:
                        locked, empty, crops, mix = tile_states(farm["tiles"])
                        snaps.append({
                            "locked": locked, "empty": empty, "crops": crops,
                            "hands": len(farm.get("hands") or []),
                            "money": farm.get("money"),
                            "q": len(farm.get("unlocked_quadrants") or []),
                            "mix": mix,
                        })
                    days[day] = snaps
            elif t == "end":
                rewards = d.get("rewards")
    return a_name, b_name, dict(days), buys, rewards

def main():
    files = sorted(glob.glob("/home/z/my-project/kaggriculture/battles/*.jsonl"))
    # chỉ lấy trận v5 vs v4 mới nhất (nhóm timestamp 17889xxx = battery Task 20)
    stats = []
    for path in files:
        a, b, days, buys, rewards = analyze(path)
        if not (a and b):
            continue
        pair = {a, b}
        if pair != {"v5", "v4"}:
            continue
        # vị trí v5
        v5_pid = 0 if a == "v5" else 1
        v4_pid = 1 - v5_pid
        last_day = max(days.keys()) if days else -1
        if last_day < 28:
            continue
        # empty trung bình d10..d28 (bỏ bootstrap sớm) và đỉnh
        empt_v5 = [days[d][v5_pid]["empty"] for d in sorted(days) if 10 <= d <= 28 and d in days]
        crops_v5 = [days[d][v5_pid]["crops"] for d in sorted(days) if 10 <= d <= 28 and d in days]
        empt_v4 = [days[d][v4_pid]["empty"] for d in sorted(days) if 10 <= d <= 28 and d in days]
        crops_v4 = [days[d][v4_pid]["crops"] for d in sorted(days) if 10 <= d <= 28 and d in days]
        stats.append({
            "file": os.path.basename(path), "seed": path.split("_")[-1].split(".")[0],
            "empty_v5_avg": sum(empt_v5)/max(1,len(empt_v5)),
            "empty_v5_max": max(empt_v5) if empt_v5 else 0,
            "crops_v5_avg": sum(crops_v5)/max(1,len(crops_v5)),
            "empty_v4_avg": sum(empt_v4)/max(1,len(empt_v4)),
            "crops_v4_avg": sum(crops_v4)/max(1,len(crops_v4)),
            "buys_v5": [(d, p) for (s, d, p) in buys if p == v5_pid],
            "buys_v4": [(d, p) for (s, d, p) in buys if p == v4_pid],
            "rewards": rewards,
            "days": days, "v5_pid": v5_pid,
        })

    print(f"Đã phân tích {len(stats)} trận v5 vs v4 (đủ 29 ngày)\n")
    print(f"{'file':<28}{'empty_v5':>10}{'crops_v5':>10}{'empty_v4':>10}{'crops_v4':>10}  buys_v5(d)  buys_v4(d)")
    for s in stats:
        print(f"{s['file']:<28}{s['empty_v5_avg']:>10.1f}{s['crops_v5_avg']:>10.1f}{s['empty_v4_avg']:>10.1f}{s['crops_v4_avg']:>10.1f}  {str([d for d,_ in s['buys_v5']]):<12} {[d for d,_ in s['buys_v4']]}")

    # Tổng hợp
    n = len(stats)
    if n:
        print(f"\n=== TỔNG HỢP ({n} trận, d10-28) ===")
        print(f"v5: đất trống TB {sum(s['empty_v5_avg'] for s in stats)/n:.1f} ô / cây TB {sum(s['crops_v5_avg'] for s in stats)/n:.1f} ô")
        print(f"v4: đất trống TB {sum(s['empty_v4_avg'] for s in stats)/n:.1f} ô / cây TB {sum(s['crops_v4_avg'] for s in stats)/n:.1f} ô")
        buydays_v5 = sorted(d for s in stats for d, _ in s["buys_v5"])
        buydays_v4 = sorted(d for s in stats for d, _ in s["buys_v4"])
        print(f"v5 BUY_LAND các ngày: {buydays_v5}")
        print(f"v4 BUY_LAND các ngày: {buydays_v4}")
        # Quan hệ empty vs mua đất
        core = stats[len(stats)//2] if n > 2 else stats[0]
        print(f"\n=== CHI TIẾT 1 TRẬN ĐẠI DIỆN: {core['file']} (v5 pid={core['v5_pid']}) ===")
        print(f"{'day':>4}{'v5.q':>6}{'v5.empty':>10}{'v5.crops':>10}{'v5.hands':>10}{'v5.money':>10}{'v4.empty':>10}{'v4.crops':>10}")
        for d in sorted(core["days"]):
            if d % 3 == 0 or d in (1, 2, 28):
                s5 = core["days"][d][core["v5_pid"]]; s4 = core["days"][d][1 - core["v5_pid"]]
                print(f"{d:>4}{s5['q']:>6}{s5['empty']:>10}{s5['crops']:>10}{s5['hands']:>10}{s5['money']:>10.0f}{s4['empty']:>10}{s4['crops']:>10}")

if __name__ == "__main__":
    main()
