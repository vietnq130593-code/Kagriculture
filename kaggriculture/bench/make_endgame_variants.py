#!/usr/bin/env python3
"""E-PACK v2 (sau khi E-pack v1: E2 NameError-inert, E3 forecast-bullish-inert).

Chẩn đoán autopsy: v5 thua endgame vì VOLUME (đàn 11 vs 15, strawberry trồng
ít) + nắm giữ khi dự báo px_pred thiên lệch tăng (L2 trễ cú ramp của v4).

  vE2 = v5.5 + LATE-HERD (FIXED: đặt SAU water_debt): d13-17 tiền ≥ $8k,
        nợ nước ≤2 → animal_cap +4, bò +2, cừu +2 (milk/wool/fert cuối mùa).
  vE3 = v5.5 + REALIZED-MOMENTUM FRONT-RUN (FIXED: dùng giá THỰC TẾ, bỏ dự
        báo): px_hist mỗi sáng; d19-26 nếu giá kênh rơi ≥2% trong 2 ngày và
        không phải WHEAT/FERT → hạ ngưỡng bán 0.55 (xả trước cú dội thật).
  vE1b = v5.5 + LATE-LAND STRAWBERRY-ONLY: SW d14-16 khi tiền ≥ $8k, ≥12
        thợ, nợ nước ≤2 → chỉ dâu muộn (room-gated, KHÔNG wheat — giữ pump
        R37/R75), tối đa 15 cây.
"""
import sys

SRC = "/home/z/my-project/kaggriculture/v5.py"
src = open(SRC, encoding="utf-8").read()

# ---------- E2 (fixed): late-herd — SAU khối siết cap theo nợ nước ----------
H_ANCHOR = """    if water_debt >= 3:
        animal_cap = max(4, animal_cap - 2)  # siết cap khi nợ nước cao
"""
H_NEW = H_ANCHOR + """    # ---- vE2 LATE-HERD: d13-17 vốn nhàn ≥ $8k → engine thú cuối mùa ----
    try:
        if 13 <= day <= 17 and money >= 8000 and water_debt <= 2:
            animal_cap = min(ANIMAL_CAP, animal_cap + 4)
            cow_target = min(12, int(cow_target) + 2)
            sheep_target = min(10, int(sheep_target) + 2)
            if isinstance(tm, dict):
                tm["knobs_late_herd"] = True
    except Exception:
        pass
"""

# ---------- E3 (fixed): ghi px_hist + momentum front-run ----------
PH_ANCHOR = """    if hour <= 5 and day < 29:
        planted_today = _STATE.get(("planted", day)) or {}
"""
PH_NEW = """    try:
        if hour <= 1:
            _ph = tmx.setdefault("px_hist", {})
            _ph[day] = {p: float(prices.get(p, 0) or 0) for p in PRODUCTS}
    except Exception:
        pass
""" + PH_ANCHOR

F_ANCHOR = """        dliq = 1 if tier == "BEHIND" else 0  # v5-P1: BEHIND thanh lý sớm 1 ngày
"""
F_NEW = """        # ---- vE3 REALIZED-MOMENTUM FRONT-RUN: giá THỰC TẾ rơi 2 ngày → xả ----
        try:
            if 19 <= day <= 26 and it not in ("WHEAT", "FERTILIZER"):
                _ph = (tmx.get("px_hist") or {})
                _p2 = (_ph.get(day - 2) or {}).get(it) or 0
                _p0 = (_ph.get(day) or {}).get(it) or 0
                if _p2 and _p0 and _p0 <= _p2 * 0.98:
                    h = min(h, 0.55)
        except Exception:
            pass
""" + F_ANCHOR

# ---------- E1b: late-land strawberry-only (KHÔNG wheat) ----------
LAND_ANCHOR = """    if land_ready:
        orders.append(["BUY_LAND"])
        bought["LAND"] = 1
        money -= lp
"""
LAND_NEW = LAND_ANCHOR + """    # ---- vE1b LATE-LAND STRAWBERRY-ONLY: SW d14-16, chỉ dâu muộn ----
    try:
        if not _STATE.get("late_land_done") and 14 <= day <= 16 \\
                and len(unlocked) == 2 and bought.get("LAND", 0) < 1 \\
                and not (rg and int(rg.get("F1", 0) or 0) >= 2):
            _wd = int((_STATE.get(("risk", day - 1)) or {}).get("water_crit_late", 0) or 0)
            if money >= 8000 and len(hands) >= 12 and _wd <= 2:
                orders.append(["BUY_LAND"])
                bought["LAND"] = bought.get("LAND", 0) + 1
                money -= 2000
                _STATE["late_land_done"] = True
                tmx["knobs_late_land"] = True
    except Exception:
        pass
"""

Q_ANCHOR = """    if day <= 23:
        if day <= 2:
            quotas["CARROT"] = 12
"""
Q_NEW = """    # ---- vE1b: ô mới chỉ trồng DÂU MUỘN (giữ nguyên pump wheat R37/R75) ----
    try:
        if (tm or {}).get("late_land_done") and 14 <= day <= 20:
            _pl = len(plantable)
            if _pl > 0:
                _sr = room("STRAWBERRY")
                straw_late = min(_pl, 15, max(0, int(_sr // 4)))
                if straw_late > 0:
                    quotas["STRAWBERRY"] = quotas.get("STRAWBERRY", 0) + straw_late
    except Exception:
        pass
""" + Q_ANCHOR


def patch(s, anchor, new, name):
    if s.count(anchor) != 1:
        sys.exit(f"{name}: anchor xuat hien {s.count(anchor)} lan")
    return s.replace(anchor, new)


def build(path, patches):
    s = src
    for name, anchor, new in patches:
        s = patch(s, anchor, new, name)
    open(path, "w", encoding="utf-8").write(s)
    print(f"wrote {path}")


base_dir = "/home/z/my-project/kaggressulture/bench/"
base_dir = "/home/z/my-project/kaggriculture/bench/"
build(base_dir + "vE2.py", [("E2", H_ANCHOR, H_NEW)])
build(base_dir + "vE3.py", [("E3a", PH_ANCHOR, PH_NEW), ("E3b", F_ANCHOR, F_NEW)])
build(base_dir + "vE1b.py", [("E1b-A", LAND_ANCHOR, LAND_NEW), ("E1b-B", Q_ANCHOR, Q_NEW)])
