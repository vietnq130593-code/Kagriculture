#!/usr/bin/env python3
"""Apply remaining corrections to 04A (Task 83) — idempotent-safe."""
import io, sys

P = "/home/z/my-project/kaggle-research/top1/04A_MATCH2_MAJKEL_WIN_ANALYSIS.md"
s = io.open(P, encoding="utf-8").read()
n_ok, fails = 0, []

def rep(old, new, count=1):
    global s, n_ok
    c = s.count(old)
    if c != count:
        fails.append(f"[{c}x] {old[:70]}")
        return
    s = s.replace(old, new)
    n_ok += 1

M = "\u2212"

# §1.1 Δ cells (rows 20-29 still pending)
rep(f"| 20 | 49,564 | +1,723 | 50,528 | +3,167 | {M}964 |",
    f"| 20 | 49,564 | +1,723 | 50,528 | +3,274 | {M}964 |")
rep(f"| 21 | 51,151 | +1,585 | 52,335 | +1,807 | {M}1,184 |",
    f"| 21 | 51,151 | +1,587 | 52,335 | +1,807 | {M}1,184 |")
rep(f"| 22 | 54,155 | +2,711 | 54,234 | +1,899 | {M}79 |",
    f"| 22 | 54,155 | +3,004 | 54,234 | +1,899 | {M}79 |")
rep(f"| 23 | 56,612 | +2,457 | 56,927 | +2,639 | {M}315 |",
    f"| 23 | 56,612 | +2,457 | 56,927 | +2,693 | {M}315 |")
rep(f"| 24 | 59,164 | +2,200 | 59,692 | +2,765 | {M}528 |",
    f"| 24 | 59,164 | +2,552 | 59,692 | +2,765 | {M}528 |")
rep(f"| 25 | 62,928 | +3,116 | 62,679 | +2,933 | +249 |",
    f"| 25 | 62,928 | +3,764 | 62,679 | +2,987 | +249 |")
rep(f"| 26 | 67,572 | +3,598 | 66,327 | +3,648 | **+1,245** |",
    f"| 26 | 67,572 | +4,644 | 66,327 | +3,648 | **+1,245** |")
rep(f"| 27 | 71,227 | +3,030 | 71,417 | +5,090 | {M}190 |",
    f"| 27 | 71,227 | +3,655 | 71,417 | +5,090 | {M}190 |")
rep(f"| 28 | 78,413 | +5,788 | 77,329 | +5,907 | **+1,084** |",
    f"| 28 | 78,413 | +7,186 | 77,329 | +5,912 | **+1,084** |")
rep(f"| 29 | **91,845** | **+13,431** | **84,129** | **+6,325** | **+7,716** |",
    f"| 29 | **91,845** | **+13,432** | **84,129** | **+6,800** | **+7,716** |")

# Prose
rep("MELON dump d10 (30 units @246 = $7,380)", "MELON dump d10 (30 units @245.6 = $7,367)")
rep("- Trên board: **17 plants trên 25 ô NW** (6 MELON + 10 WHEAT + 2 ô trống), 5 ô PASTURE cho 5 con vật\n  (verbs: 5 BUILD_PASTURE + 5 PLACE). WATER 17 lần ngay d0 (tưới đủ 16 cây + 1 thừa).",
    "- Trên board: **16 plants trên 25 ô NW** (6 MELON + 10 WHEAT), 5 ô PASTURE cho 5 con vật\n  (verbs: 5 BUILD_PASTURE + 5 PLACE), 4 ô trống. PLANT/WATER 17 lần ngay d0 (tưới đủ 16 cây + 1 thừa).")
rep("Cả hai thuê thêm hands: d1 +3 ($4), d2 +6 ($20) → 6 hands.", "Cả hai thuê thêm hands: d1 giữ 4 ($7), d2 +6 ($20) → 6 hands.")
rep("### 3.1 Tổng chi theo loại (begge 30 ngày)", "### 3.1 Tổng chi theo loại (cả hai, 30 ngày)")
rep("d0-1: 4 hands ($7) → d2-5: 6 ($20)", "d0-1: 4 hands ($7) → d2-5: 5-6 ($12-20)")
rep("2 lượt hire FAIL của Majkel (s25 d1) vì tiền < giá fib — vô hại.",
    "3 lượt hire FAIL của Majkel (s25×2 d1, s73 d3) vì tiền < giá fib — vô hại.")
rep("**NE OK** (−1,000, sau khi bán WOOL 12 units)", "**NE OK** (−1,000, sau đợt WOOL đầu 6 units ở s149)")
rep("144+233+377+610 ≈ **+$665/ngày**", "144+233+377+610 ≈ **+$1,364/ngày**")
rep("- Bảng专项 strawberry:", "- Bảng chuyên sâu strawberry:")
rep("6 WOOL/con** (care-bonus tích lũy 6) = 18 units @194-199 = $3,492 ngay d6.",
    "6 WOOL/con** (care-bonus tích lũy 6) = 18 units @167-218 = $3,483 ngay d6.")
rep("- **FERTILIZER (byproduct miễn phí): 179 units bán $11,514 + ~162 units tự bón** → đám vật nuôi\n  \"trả tiền\" chủ yếu qua phân: $11.5K tiền + giá trị bón (~162 × ~$40 hiệu ứng ×2 yield) ≈ $18K.",
    "- **FERTILIZER (byproduct miễn phí): 179 units bán $11,514 + ~152 units tự bón** → đám vật nuôi\n  \"trả tiền\" chủ yếu qua phân: $11.5K tiền + giá trị bón (~152 × ~$40 hiệu ứng ×2 yield) ≈ $18K.")
rep("**d28-29 FEED=0** — chủ động bỏ đói (1 COW + 4 SHEEP escape, vô hại ngày cuối) để bán sạch wheat.",
    "**d28-29 FEED=0** — bỏ đói cuối game (3 SHEEP escape d28, 1 COW + 1 SHEEP d29 — vô hại ngày cuối)\n  để bán sạch wheat; trước đó đã mất lẻ 1 SHEEP (~d20) + 1 COW + 1 SHEEP (~d22) vì feed không đều\n  (đàn 15 → 12 → 9 → 7 từ d19 tới d29).")
rep("Fertilizer bán giá giảm dần 99 → 29", "Fertilizer bán giá giảm dần 100 → 29")
rep("**shed STRA tích lũy 0 → 20 → 30 → 46 → 54 → 65 units (d19-24)**",
    "**shed STRA tích lũy 0 → 20 → 33 → 51 → 57 → 68 → 65 units (d19-24, đỉnh 68 ở d23)**")
rep("giá 270 → 226 cùng ngày; Majkel vẫn đạt avg 246 cho 24 units đầu, cú 12 units cuối\n  @235.",
    "giá 272 → 226 cùng ngày; Majkel đạt avg ~252 cho 18 units đầu (s251-253), cú 12 units cuối\n  @235 (s254).")
rep("- **WOOL d12:** cả 2 bán 10@216 + 6@226/227 ở s292-294 khi giá còn 226-228",
    "- **WOOL d12:** Majkel 6@226 (s292) + 10@216 (s294), DSM 5@227 + 10@216, giá còn 226-228")
rep("Majkel dump 12@153 (d8), 12@138 (d10), 17@59 (d14) rồi bán rác.",
    "Majkel dump 12@153 (d8), 6@119 (d10), 3@108 (d12), 3@99 (d13), 17@59 (d14) rồi bán rác.")
rep("Majkel: ~0 (d0-15) → 15-50 (d16-21) → **57-100 (d22-27, chạm cap 100 ở d22/d28/d29)** → 0.\nDSM: tối đa 79-92 (d21-27), thường 17-35.",
    "Majkel: ~0-20 (d0-15) → 50-95 (d16-21) → **94-100 (d22-29, chạm cap 100 ở d22/d28/d29)** → 0.\nDSM: max 60-92 (d21-29), thường 17-35.")
rep("(2,709 là SELL vô hàng: TOMATO 594, EGG 492, MELON 400, CARROT 389, STRA 311, WOOL 270, MILK 252)",
    "(2,709 là SELL vô hàng: TOMATO 594, EGG 492, MELON 400, CARROT 389, STRA 311, WOOL 270, MILK 252, WHEAT 1)")
rep("### 7.1 Town consumption (engine: shop 每4 step, single-product ×2; center 每24 step mỗi product)",
    "### 7.1 Town consumption (engine: mỗi shop 4 step một lần, shop 1 sản phẩm ×2; center mỗi 24 step mỗi product)")
rep("đợt WOOL đầu 18 units @194-199.", "đợt WOOL đầu 18 units @167-218.")
rep("WOOL 18 units @194-208 (6/con nhờ care-bonus) rồi mua NE + 4 SHEEP + 2 COW | cú tái đầu tư đầu tiên, ep về $69-130 |",
    "WOOL 18 units @167-218 (6/con nhờ care-bonus) rồi mua NE + 4 SHEEP + 2 COW | cú tái đầu tư đầu tiên, money về đáy $49 |")
rep("MELON dump 30 units @235-262 (+$7,380 trong 4 step)", "MELON dump 30 units @243-270 (+$7,367 trong 4 step)")
rep("| 7 | d22-24 | shed STRA 54→65; giá hồi 114→132 |", "| 7 | d22-24 | shed STRA 57→68→65; giá hồi 114→132 |")
rep("| 8 | s292-294 (d12) | WOOL 10@216 bán đúng trước ngưỡng I0 | (cả 2) — kiểu \"sell into strength\" |",
    "| 8 | s292-294 (d12) | WOOL 15-16 units mỗi bên @216-227 bán đúng trước ngưỡng I0 | (cả 2) — kiểu \"sell into strength\" |")
rep("rolling-14d HOặc < base", "rolling-14d hoặc < base")
rep("bị両 bên bão hòa", "bị cả hai bên bão hòa")
rep("phân\": 179 bán + ~162 bón = ~$18K giá trị từ 15 con.",
    "phân\": 179 bán + ~152 bón = ~$18K giá trị từ 15 con.")
rep("+ hire 9 (79,788)", "+ hire 8 (79,788)")
rep("WHEA 8@35 + hire 9 (78,948)", "WHEA 8@35 + hire 8 (78,948)")
rep("MILK nên bán sạch trước ~d14 ( Majkel còn giữ", "MILK nên bán sạch trước ~d14 (Majkel còn giữ")

if fails:
    print("FAILED MATCHES:")
    for f in fails: print("  " + f)
    sys.exit(1)
io.open(P, "w", encoding="utf-8").write(s)
print(f"OK — {n_ok} replacements applied.")
