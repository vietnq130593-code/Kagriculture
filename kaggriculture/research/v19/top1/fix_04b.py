#!/usr/bin/env python3
"""Apply verified corrections to 04B_MATCH1_MAJKEL_LOSS_ANALYSIS.md (Task 83)."""
import io, sys

P = "/home/z/my-project/kaggle-research/top1/04B_MATCH1_MAJKEL_LOSS_ANALYSIS.md"
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

# --- §1 Δ/profit column fixes (16 cells) ---
rep("| 6 | 2,222 (+1,401) | 20 (" + M + "485) | ymg | +2,202 |",
    "| 6 | 2,222 (+1,490) | 20 (" + M + "485) | ymg | +2,202 |")
rep("| 8 | 2,560 (+441) | 2,275 (+2,256) | ymg | +285 |",
    "| 8 | 2,560 (+609) | 2,275 (+2,256) | ymg | +285 |")
rep("| 9 | 3,388 (+793) | 374 (" + M + "1,901) | ymg | +3,014 |",
    "| 9 | 3,388 (+828) | 374 (" + M + "1,901) | ymg | +3,014 |")
rep("| 10 | 5,748 (+2,066) | 6,487 (+6,113) | **MAJ** | " + M + "739 |",
    "| 10 | 5,748 (+2,360) | 6,487 (+6,113) | **MAJ** | " + M + "739 |")
rep("| 12 | 5,841 (" + M + "140) | 13,532 (+1,656) | MAJ | " + M + "7,691 |",
    "| 12 | 5,841 (+206) | 13,532 (+1,656) | MAJ | " + M + "7,691 |")
rep("| 13 | 9,250 (+3,279) | 13,837 (+305) | MAJ | " + M + "4,587 |",
    "| 13 | 9,250 (+3,409) | 13,837 (+305) | MAJ | " + M + "4,587 |")
rep("| 14 | 13,739 (+4,365) | 25,612 (+7,167) | MAJ | **" + M + "11,873 (đỉnh)** |",
    "| 14 | 13,739 (+4,489) | 25,612 (+11,775) | MAJ | **" + M + "11,873 (đỉnh)** |")
rep("| 20 | 51,374 (+1,461) | 54,367 (+3,119) | MAJ | " + M + "2,993 |",
    "| 20 | 51,374 (+1,555) | 54,367 (+3,119) | MAJ | " + M + "2,993 |")
rep("| 23 | 58,931 (+902) | 59,918 (+1,318) | MAJ | " + M + "987 |",
    "| 23 | 58,931 (+902) | 59,918 (+1,320) | MAJ | " + M + "987 |")
rep("| 24 | 61,268 (+2,337) | 62,786 (+2,326) | MAJ | " + M + "1,518 |",
    "| 24 | 61,268 (+2,337) | 62,786 (+2,868) | MAJ | " + M + "1,518 |")
rep("| 25 | 65,174 (+3,856) | 65,998 (+3,210) | MAJ | " + M + "824 |",
    "| 25 | 65,174 (+3,906) | 65,998 (+3,212) | MAJ | " + M + "824 |")
rep("| 26 | 68,110 (+2,936) | 69,047 (+3,035) | MAJ | " + M + "937 |",
    "| 26 | 68,110 (+2,936) | 69,047 (+3,049) | MAJ | " + M + "937 |")
rep("| 27 | 71,469 (+3,323) | 73,091 (+4,044) | MAJ | " + M + "1,622 |",
    "| 27 | 71,469 (+3,359) | 73,091 (+4,044) | MAJ | " + M + "1,622 |")
rep("| 28 | 76,145 (+4,676) | 79,264 (+6,162) | MAJ | " + M + "3,119 |",
    "| 28 | 76,145 (+4,676) | 79,264 (+6,173) | MAJ | " + M + "3,119 |")

# --- §1 narrative ---
rep("(+6,113 ngày 10, +5,389 ngày 11, +7,167 ngày 14)", "(+6,113 ngày 10, +5,389 ngày 11, +11,775 ngày 14)")
rep("11 ngày liên tiếp ymg_aq out-earn Majkel (trừ d20/d23 nhỏ)",
    "ymg_aq out-earn Majkel 8/11 ngày (trừ d20/d23/d24)")
rep("d26-28:** Majkel lại tăng speed (+3,035/+4,044/+6,162)", "d26-28:** Majkel lại tăng speed (+3,049/+4,044/+6,173)")

# --- §2 opening ---
rep("**2 COW (−800) + 3 SHEEP (−1,500)** = 5 animals", "**1 COW (−400) + 3 SHEEP (−1,500)** → cộng COW s1 = 5 animals (2 COW + 3 SHEEP)")
rep("| s16-19 | 4 lệnh BUY_SEED **exec=0 (hết tiền)**", "| s16-19 | 5 lệnh BUY_SEED **exec=0 (hết tiền)**")
rep("Bán FERT 4-5/ngày (~$475-495/ngày)", "Bán FERT 5/ngày (~$476-496/ngày)")
rep("d4 HARVEST 18 WHEAT → d5 bán 68u/$2,614", "d4 HARVEST 18 WHEAT → d5 bán 68u/$2,614 (58 WHEAT + 10 FERT)")

# --- §3 hands ---
rep("ymg_aq: 7 (d0) → 8 (d7) → **11-12 (d9-28)** → 11 (d29). Avg 10.4-11.3.",
    "ymg_aq: 7 (d0) → 8 (d7) → **10-12 (d9-28)** → 11 (d29). Avg 10.4-11.3.")
rep("Majkel: 4 (d0) → 8 (d6) → 10-11 (d9-26) → **chỉ 9-10 (d27-29)**.",
    "Majkel: 4 (d0) → 8 (d6) → 10-11 (d9-26) → **chỉ 10 (d27-29)**.")
rep("Majkel giảm về 9-10 ở đúng 3 ngày cuối → ít unit", "Majkel giảm về 10 ở đúng 3 ngày cuối → ít unit")

# --- §4 weeds / water / land ---
rep("- Tổng weeds: ymg_aq 16 (chủ yếu d28-29: 3+8 khi rút unit đi harvest/bán), Majkel 26 (1 weed\n  suốt d5-13, d25-29 tăng 2→7).",
    "- Weeds trên board (cuối ngày): ymg_aq gần sạch suốt game (0-2 tới d27) rồi 3 (d28) → 8 (d29)\n  khi rút unit đi harvest/bán; Majkel giữ 1 weed dai dẳng d5-13, d25-29 tăng dần 2→7. Final 8 vs 7.")
rep("- WATER verbs: Majkel nhiều hơn tổng thể (1,181 vs 942)", "- WATER verbs: Majkel nhiều hơn tổng thể (1,397 vs 1,028)")
rep("Spam retry khi broke: s101/d4, s122-129/d5 (6 lệnh cash=0), s220/d9", "Spam retry khi broke: s101/d4, s122-129/d5 (5 lệnh cash=0), s220/d9")

# --- §5 feed/fertilize totals ---
rep("| FEED verbs tổng | 354 (đỉnh 18/ngày) | 244 (đỉnh 14/ngày) |", "| FEED verbs tổng | 353 (đỉnh 18/ngày) | 267 (đỉnh 14/ngày) |")
rep("| FERTILIZE verbs tổng (bón cây) | **208** (d28 vẫn bón 24) | 100 |", "| FERTILIZE verbs tổng (bón cây) | **216** (d28 vẫn bón 24) | 134 |")
rep("động vật nhả FERT, 1 phần bón lại cây (**208 lượt bón vs 100**,", "động vật nhả FERT, 1 phần bón lại cây (**216 lượt bón vs 134**,")

# --- §6.2 timing ---
rep("d14: 24u @230 → hết hàng d14**", "d14: 24u @223 → hết hàng d14**")
rep("rồi **dump d15-18: 60u @190→95** ✘", "rồi **dump d15-18: 66u @~181→102** ✘")

# --- §6.3 endgame ---
rep("| 697-714 | +6,306 | +5,391 | MAJ (gap cực đại +1,574 @s710) |", "| 697-714 | +6,306 | +3,378 | MAJ (gap cực đại +1,574 @s710) |")
rep("| Hands ngày | 11 | 9-10 |", "| Hands ngày | 11 | 10 |")
rep("| MILK | 16u $294 @18 | 13u $295 @23 |", "| MILK | 16u $294 @18 | 13u $295 @23 |\n| WOOL | — | 1u $5 @5 |")
rep("2. Engine **tự harvest yields đã chín vào shed lúc 0h d29** (shed 0→94 units chỉ sau 1 step) → không\n   tốn hands cho việc đưa hàng vào kho sáng cuối.",
    "2. Hàng nằm **trên tay units lúc 23h** được `_end_of_day` auto-drop vào shed (ymg 0→94 units ngay\n   đầu d29) — KHÔNG phải engine tự harvest cây (yields chín vẫn nằm trên cây chờ HARVEST tay).")

# --- §8 key moments ---
rep("MILK @167-196, +6,113/+5,389/+7,167 profit 3 ngày", "MILK @167-196, +6,113/+5,389/+11,775 profit 3 ngày")
rep("ymg **dump 156u (120u @44.8 ở đáy)**", "ymg **dump 120u @45 ở đáy d19-24 (13u @$1 ngày d23)**")
rep("248 seed\npackets, 208 lượt bón phân, 11-12 hands mỗi ngày", "248 seed\npackets, 216 lượt bón phân, 11-12 hands mỗi ngày")

# --- §9 ---
rep("vs Majkel cắt về 9-10 ở d27-29 → throughput d29: 39 vs 33 HARVEST", "vs Majkel cắt về 10 ở d27-29 → throughput d29: 39 vs 33 HARVEST")

# --- typos & footer ---
rep("### 6.1 Sells tổng hợp theo item (beguồn Mục 5)", "### 6.1 Sells tổng hợp theo item (từ Mục 5)")
rep("không反应 (0 GOOSE cả match)", "không phản ứng (0 GOOSE cả match)")
rep("Hai agent bán cùng lúc加速 sập giá", "Hai agent bán cùng lúc thúc đẩy sập giá")
rep("bổ sung động物 mix + shop\n    counter", "bổ sung động vật mix + shop\n    counter")
rep("*(Phân tích: match1/{orders,timeline,daily,market,town}.json; engine kaggressurE.py `_end_of_day`\nL~740: `_drop_inventories_to_shed`, `farm[\"hands\"]=[]`, `hires_today=0`;",
    "*(Phân tích: match1/{orders,timeline,daily,market,town}.json; engine kaggriculture.py `_end_of_day`\nL860-893: `_drop_inventories_to_shed` L878, `farm[\"hands\"]=[]`, `hires_today=0`;")

if fails:
    print("FAILED MATCHES:")
    for f in fails: print("  " + f)
    sys.exit(1)
io.open(P, "w", encoding="utf-8").write(s)
print(f"OK — {n_ok} replacements applied.")
