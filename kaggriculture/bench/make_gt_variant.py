#!/usr/bin/env python3
"""Tạo vG = vL5 (50 ô) + LỚP GT-COURNOT — kiến trúc 2 cấp nhân quả user yêu cầu.

MACRO CYCLE (mỗi 24 lượt, hour 0-1): đọc L1 mode + L2 Gamma-Poisson forecast
  dòng bán đối thủ → tính tín hiệu Cournot mỗi kênh:
    dump_sig: P75 ≥ 8u và P75 ≥ 1.5×E → đối thủ sắp dội lumpy
    calm_sig: dòng đối thủ êm → độc quyền nắm chờ
MICRO CYCLE (mỗi lượt): điều chế ngưỡng bán theo tín hiệu macro:
    dump_sig → ×0.96 (Stackelberg front-run: bán TRƯỚC cú dội)
    calm_sig + giá dự báo tăng → ×1.04 (monopoly restraint)
Ghi tm["gt"] vào diag — Arena BrainPanel hiển thị lớp GT.
"""
import sys

SRC = "/home/z/my-project/kaggriculture/bench/vL5.py"
src = open(SRC, encoding="utf-8").read()

# ---------- Patch GT-1: macro cycle đầu ngày ----------
MACRO_ANCHOR = """    cands = []
    if shed:
"""
MACRO_NEW = """    # ---- Task 21 GT-COURNOT: VÒNG TOÀN CỤC (mỗi 24 lượt, đầu ngày) ----
    # Bậc 1 (quan sát): L2 Gamma-Poisson E/P25/P75 dòng bán đối thủ mỗi kênh.
    # Bậc 2 (can thiệp): quy về tín hiệu Cournot điều chế ngưỡng bán hôm nay —
    #   dump_sig → front-run (bán trước cú dội, giá chưa bị dìm);
    #   calm_sig → monopoly restraint (nắm chờ drain hồi giá).
    # Micro (mỗi lượt) áp dụng trong _hold() bên dưới. Ghi tm["gt"] cho diag.
    try:
        if hour <= 1 and 6 <= day <= 25:
            l2p = (tmx.get("l2_pred") or {}) if isinstance(tmx, dict) else {}
            gt = {}
            for it in PRODUCTS:
                if it in ("FERTILIZER",):
                    continue
                q = l2p.get(it) or {}
                _e = float(q.get("e", 0) or 0)
                _p75 = float(q.get("p75", 0) or 0)
                dump_sig = (_p75 >= 8.0 and _p75 >= 1.5 * max(1.0, _e))
                calm_sig = (_p75 <= 3.0 or (_e > 0 and _p75 < _e * 1.15 + 2.0))
                gt[it] = {"e": round(_e, 1), "p75": round(_p75, 1),
                          "dump": bool(dump_sig), "calm": bool(calm_sig)}
            if isinstance(tmx, dict):
                tmx["gt"] = gt
    except Exception:
        pass

    cands = []
    if shed:
"""

# ---------- Patch GT-2: micro cycle trong _hold ----------
MICRO_ANCHOR = """        dliq = 1 if tier == "BEHIND" else 0  # v5-P1: BEHIND thanh lý sớm 1 ngày
"""
MICRO_NEW = """        # ---- Task 21 GT-COURNOT: VÒNG NHỎ (mỗi lượt) — điều chế theo macro ----
        try:
            _gtq = ((tmx.get("gt") or {}).get(it)) or {}
            if _gtq and 6 <= day <= 25:
                if _gtq.get("dump"):
                    # Stackelberg front-run: đối thủ sắp dội lumpy (L2 P75 cao
                    # vượt 1.5×E) → bán NGAY vào sức mua còn nguyên trước sóng
                    h = max(0.85, h * 0.96)
                elif _gtq.get("calm"):
                    _pxq = (tmx.get("px_pred") or {}).get(it) or {}
                    _now, _p3 = _pxq.get("now"), _pxq.get("p3")
                    if _now and _p3 and _p3 >= _now * 1.05:
                        # Monopoly restraint: ngày êm + giá leo → nắm chờ đỉnh
                        h = min(0.99, h * 1.04)
        except Exception:
            pass
        dliq = 1 if tier == "BEHIND" else 0  # v5-P1: BEHIND thanh lý sớm 1 ngày
"""


def apply(anchor, new):
    global src
    if anchor not in src:
        print(f"LỖI: không tìm thấy anchor [{anchor[:60]}...]")
        sys.exit(1)
    if src.count(anchor) != 1:
        print(f"LỖI: anchor xuất hiện {src.count(anchor)} lần")
        sys.exit(1)
    src = src.replace(anchor, new)


apply(MACRO_ANCHOR, MACRO_NEW)
apply(MICRO_ANCHOR, MICRO_NEW)

path = "/home/z/my-project/kaggriculture/bench/vG.py"
with open(path, "w", encoding="utf-8") as f:
    f.write(src)
import ast
ast.parse(src)
print(f"vG OK → {path} ({len(src.splitlines())} dòng)")
