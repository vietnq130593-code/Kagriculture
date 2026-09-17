#!/usr/bin/env python3
"""Tạo 3 biến thể GT-LAND từ v5.py (v5.4) — Task 21, trả lời 2 câu hỏi đất.

vL1 — FILL LAND: lấp đất trống bằng wheat + mở biên thợ (trả lời Q2:
      ràng buộc là LAO ĐỘNG chứ không phải thị trường → thuê thêm lấp đất)
vL2 — SKIP SE: không mua quadrant 4 ($4k) (trả lời Q1: mua đất có lãng phí?)
vL3 — COMBO: skip SE + lấp 75 tiles bằng wheat + 15 thợ
"""
import re, sys

SRC = "/home/z/my-project/kaggriculture/v5.py"
src = open(SRC, encoding="utf-8").read()

# ---------- Patch 1: FILL LAND — wheat quota khi ruộng trống ----------
FILL_QUOTA_ANCHOR = """    if rg and int(rg.get("F2", 0) or 0) >= 2:  # v5: F2 L2+ — tăng quota wheat tự trồng
        quotas["WHEAT"] = min(28, quotas.get("WHEAT", 20) + 2)
"""
FILL_QUOTA_NEW = FILL_QUOTA_ANCHOR + """    # vL1 GT-LAND (Task 21): lấp đất trống bằng wheat. Đo thực 36 trận: SW+SE
    # ($6k) chạy 60-75% trống suốt d13-24; ô trống = tài sản chết. Wheat có
    # 3 lối ra (feed thú / bán ở giá pump R37 / tồn kho chờ giá) nên không
    # glut kiểu melon. Gate: ruộng THẬT trống >=20 ô (tính cả ô chờ thu hôm nay).
    try:
        _empty_now = sum(1 for row in tiles for t in row if t is None)
    except Exception:
        _empty_now = 0
    if 13 <= day <= 24 and _empty_now >= 20 and money >= 1200:
        _fill = min(14, (_empty_now - 16) // 2)
        quotas["WHEAT"] = max(quotas.get("WHEAT", 20),
                              min(34, quotas.get("WHEAT", 20) + _fill))
        try:
            tm["gt_fill"] = _fill
        except Exception:
            pass
"""

# ---------- Patch 2: FILL LAND — mở biên thợ 15 ----------
HIRE_ANCHOR = """            cap = 13 if ((day >= 9 and money >= 1800) or (day >= 18 and money >= 2500)) else 12
"""
HIRE_NEW = HIRE_ANCHOR + """            # vL1 GT-LAND: LAO ĐỘNG là ràng buộc chặt (đo d15-25: 91% slot dùng,
            # PASS 3%) → khi ruộng còn >=15 ô trống, nâng biên 15: chi fib biên
            # ~$377+$610/ngày đổi ~10-20 turn hiệu dụng/tile $50+ = lời.
            try:
                _empty_h = sum(1 for row in tiles for t in row if t is None)
            except Exception:
                _empty_h = 0
            if 12 <= day <= 25 and _empty_h >= 15 and money >= 3200:
                cap = 15
"""

# ---------- Patch 3: SKIP SE ----------
SKIPSE_ANCHOR = """    nq = len(unlocked)
    lp = LAND_PRICES[nq - 1] if nq < 4 else None
"""
SKIPSE_NEW = """    nq = len(unlocked)
    # vL2 GT-LAND: bỏ quadrant 4 (SE $4k) — đo thực: SE chạy 76% trống,
    # ROI âm khi lao động bão hòa; $4k giữ lại nuôi thợ/thú/hạt.
    if nq >= 3:
        nq = 4  # khóa: lp=None → không bao giờ mua tiếp
    lp = LAND_PRICES[nq - 1] if nq < 4 else None
"""


def apply(name, patches):
    out = src
    for label, anchor, new in patches:
        if anchor not in out:
            print(f"[{name}] LỖI: không tìm thấy anchor '{label}'")
            sys.exit(1)
        if out.count(anchor) != 1:
            print(f"[{name}] LỖI: anchor '{label}' xuất hiện {out.count(anchor)} lần")
            sys.exit(1)
        out = out.replace(anchor, new)
    path = f"/home/z/my-project/kaggriculture/bench/{name}.py"
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    # syntax check
    import ast
    ast.parse(out)
    print(f"[{name}] OK → {path} ({len(out.splitlines())} dòng)")


apply("vL1", [("quota", FILL_QUOTA_ANCHOR, FILL_QUOTA_NEW),
              ("hire", HIRE_ANCHOR, HIRE_NEW)])
apply("vL2", [("skipSE", SKIPSE_ANCHOR, SKIPSE_NEW)])
apply("vL3", [("quota", FILL_QUOTA_ANCHOR, FILL_QUOTA_NEW),
              ("hire", HIRE_ANCHOR, HIRE_NEW),
              ("skipSE", SKIPSE_ANCHOR, SKIPSE_NEW)])
