#!/usr/bin/env python3
"""Apply verified corrections to 05_V19_DEPLOYMENT_PLAN.md (Task 83)."""
import io, sys

P = "/home/z/my-project/kaggle-research/05_V19_DEPLOYMENT_PLAN.md"
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

# §0 portfolio breadth
rep("(−$10,926 ΔEGG cho ymg_aq), 9 dòng revenue của ymg_aq áp 5 dòng của Majkel.",
    "(−$10,926 ΔEGG cho ymg_aq), 9 dòng revenue của ymg_aq so 8 dòng của Majkel (Majkel chỉ thiếu đúng EGG).")

# §2.1 lifecycle
rep("| Spend-down | d0-2 | Chi $3,000 xuống ~$5-180: seeds + 5-6 động vật đầu + feed + hire |",
    "| Spend-down | d0-2 | Chi $3,000 xuống ~$3-180: seeds + 5-6 động vật đầu + feed + hire |")
rep("| Harvest | d25-28 | Dừng mua (buys → $0 từ d28), dừng feed (d28), cắt hiring d27 |",
    "| Harvest | d25-28 | Dừng mua (buys → $0 từ d28), dừng feed (d28), cắt bớt hiring từ d28 (11→10 hands) |")

# §2.2 evidence table
rep("| Revenue ngày 29 (match2) | **$13,575** | DSM $6,943 | endgame dump = 96% margin trận |",
    "| Revenue ngày 29 (match2) | **$13,575** | DSM $6,943 | dump s719 = 96% revenue bước cuối của Majkel; step 719 mang 81% margin trận |")
rep("| Trough throttle (match2) | +$4,757 (giữ 65u chờ 84→186) | DSM " + M + "$4,474 (bán đáy @102) | price-gated sell rate |",
    "| Trough throttle (match2) | +$4,757 (tích shed 65-68u chờ 84→186, giữ 42u cho s719) | DSM " + M + "$4,474 (bán đáy @102) | price-gated sell rate |")

# §2.3 #5 fertilizer
rep("từ 179 units bán + 162 bón ×2-yield cho STRA", "từ 179 units bán + 152 bón ×2-yield cho STRA")

# §3.1 A1
rep("- Từ step 712 (h 20 d29): tắt mọi BUY (kể cả feed/seed), chỉ còn SELL.",
    "- Từ step 712 (h 16 d29): tắt mọi BUY (kể cả feed/seed), chỉ còn SELL.")
rep("(recovery = town_đơn_vị/ngày × giá hiện tại; WHEAT/FERT/MILK/WOOL/TOMATO/CARROT trước),",
    "(recovery = town_đơn_vị/ngày × giá hiện tại — bán tăng dần recovery: FERT/MILK/WOOL trước, rồi WHEAT/CARROT/TOMATO),")

# §3.1 A2
rep("$6-7K vì dump 120u STRA @44.8 trung bình.", "$6-7K vì dump 120u STRA @45 trung bình.")

# §3.2 B1 heading typo
rep("#### B1 · GOOSE/EGG MONOPOLY DETECTOR ★ breadh lớn nhất", "#### B1 · GOOSE/EGG MONOPOLY DETECTOR ★ breadth lớn nhất")

# §3.2 B2 unsupported number
rep("thêm COW (Majkel vẫn mua = sai lệnh −$2K).", "thêm COW (Majkel vẫn thêm 5 COW ở d6 — MILK bão hòa từ d16, thiếu dòng EGG).")

# §3.2 B3 wrong shop day
rep("PET_CAFE d21 + base 35 + cycle 2 ngày → CARROT factory", "PET_CAFE d9 + base 35 + cycle 2 ngày → CARROT factory")

# §3.2 B4 auto-drop semantics
rep("\"trên cây\" là kho thứ hai, 23h auto-drop vào shed rồi d29 bán.",
    "\"trên cây\" là kho thứ hai — auto-drop 23h chỉ gom hàng TRÊN TAY units; yields trên cây phải HARVEST trong ngày cuối.")

# §3.3 C2
rep("(match2 Majkel = 0 stranded; destbreso benchmark cho thấy agent xấu kẹt $442).",
    "(shed match2 Majkel = 0 stranded; destbreso benchmark cho thấy agent xấu kẹt $442).")

# §3.3 C3 SE fib sum
rep("**SE KHÔNG BAO GIỜ** (âm EV: +25 ô cần +$377-665/ngày fib-hands).",
    "**SE KHÔNG BAO GIỜ** (âm EV: +25 ô cần +$377-1,364/ngày fib-hands).")

# §1 engine line refs + parser note
rep("`_end_of_day` auto-drop L860-882,", "`_end_of_day` auto-drop L860-893 (call L878),")
rep("→ **0 sai lệch tiền trên 720×2 bước của cả 2 trận**. Mọi con số",
    "→ **0 sai lệch tiền trên 720×2 bước của cả 2 trận** (bug off-by-one của `profit_day` trong daily.json\n  đã được phát hiện và sửa trong review ngày 16-09 — cột Δ trong 04A/04B giờ là money-delta chuẩn). Mọi con số")

# §4 Phase 3 G4 clarification
rep("Cổng G2 (sparring) + G4 (official runner, **single-file packaged — KHÔNG wrapper**; audit\n   bằng packaged main.py, giải phóng sys.modules giữa games).",
    "Cổng G2 (sparring) + G4 (official runner, **single-file packaged — inline toàn bộ source vào 1 file**;\n   audit bằng packaged main.py chứ KHÔNG qua wrapper-file, giải phóng sys.modules giữa games).")

# §6 file map
rep("""kagriculture/agents/v19.py     ← (tương lai) wrapper REAPER trên v18
kagriculture/agents/v18.py     ← nền byte-exact, KHÔNG đụng
kagriculture/arena/run_battle.py  ← T1 battery (CLI --a v19 --b v18 --seed N)
mini-services/arena-service/   ← UI arena (đã chạy, giữ nguyên)
bench/                         ← 64-worlds + bootstrap CI (tái dụng hạ tầng task 80)""",
    """kagriculture/v19.py            ← (tương lai) wrapper REAPER trên v18
kagriculture/v18.py            ← nền byte-exact, KHÔNG đụng
kagriculture/arena/run_battle.py  ← T1 battery (CLI --a v19 --b v18 --seed N)
mini-services/arena-service/   ← UI arena (đã chạy, giữ nguyên)
kagriculture/battles/          ← JSONL battle log (run_battle tự ghi)
bench/64worlds/                ← (tái tạo khi triển khai) bootstrap CI — bench/ cũ đã dọn trong cleanup""")

if fails:
    print("FAILED MATCHES:")
    for f in fails: print("  " + f)
    sys.exit(1)
io.open(P, "w", encoding="utf-8").write(s)
print(f"OK — {n_ok} replacements applied.")
