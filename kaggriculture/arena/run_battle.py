#!/usr/bin/env python3
"""
ARENA BATTLE RUNNER — kaggriculture v4 vs v5 observation infrastructure.

Runs a full kaggriculture battle on the REAL kaggle-environments engine and
streams every turn as one JSON line on stdout (JSONL). The arena-service (bun +
socket.io) forwards these lines to the Observer UI at /.

Protocol (stdout, one JSON object per line):
  {"t":"hello","runner":1,"a":"v5","b":"v4","seed":101,"episodeSteps":720}
  {"t":"turn","step":0,"day":0,"hour":0,
   "farms":[farm0,farm1],                       # public, pre-action state of the step
   "market":{"inventory":{...},"prices":{...}},
   "town":{"unlocked_shops":[...]},
   "priv":[privA,privB],                        # omniscient observer: both sheds
   "acts":[actA,actB],                          # actions returned this turn
   "diag":[diagA,diagB],                        # agent internal state (mode/posterior/H...)
   "times":[msA,msB]}                           # agent compute time per turn
  {"t":"end","rewards":[r0,r1],"winner":0|1|-1,"wallS":38.2,"turns":718}

Usage:
  python3 run_battle.py --a v4 --b v5 --seed 101
  python3 run_battle.py --a v5 --b v4 --seed 102          # swapped seats
  python3 run_battle.py --a v4 --b v5 --seed 7 --max-steps 48   # 2-day smoke test
"""
import argparse
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # kaggriculture/
BENCH = os.path.join(ROOT, "bench")

sys.path.insert(0, ROOT)
sys.path.insert(0, BENCH)

# name -> (file, entry function)
# Task 81 (2026-09-16): RESET TOÀN BỘ registry — user xóa sạch dòng dõi cũ (v13→v17, kme3 family,
# aurax, kawashigi, indark, thomast, ahmedv41) để dựng v18 trên nền mới.
# v18 = jaxa623/sdy623 "Beyond 48-0" K0006 (V43 + 4 market micro-edges) — Kaggle pull 2026-09-16,
#        main.py sha256 4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e (byte-exact).
# Sparring: ahmedv43/v44/v45 = Ahmed Berat Özer lineage (nền của v18).
AGENTS = {
    "v18": (os.path.join(ROOT, "v18.py"), "agent"),
    "v19": (os.path.join(ROOT, "v19.py"), "agent"),
    "ahmedv43": (os.path.join(ROOT, "ahmedv43.py"), "agent"),
    "ahmedv44": (os.path.join(ROOT, "ahmedv44.py"), "agent"),
    "ahmedv45": (os.path.join(ROOT, "ahmedv45.py"), "agent"),
    # Task 87: đối thủ meta mới (extracted từ notebook Kaggle 17-09, sha256-verified)
    # seyit4 = seyitkaangunes "V44+4 layers" (live 56280605, ~2801 rank ~188)
    # ahmedv46 = ahmedberatozer "First-Turn Microstructure" (EXP293)
    "seyit4": (os.path.join(ROOT, "seyit4.py"), "agent"),
    "ahmedv46": (os.path.join(ROOT, "ahmedv46.py"), "agent"),
    # v19.1 = v19 + first-turn microstructure (v46-mechanism port)
    "v191": (os.path.join(ROOT, "v191.py"), "agent"),
    # v19.2 = + h21/22 preguard (seyit-L1 adapted); v19.3 = + LOOKAHEAD 3;
    # v19.4 = + clone-gated lockstep SELL reorder (seyit-L2 port)
    "v192": (os.path.join(ROOT, "v192.py"), "agent"),
    "v193": (os.path.join(ROOT, "v193.py"), "agent"),
    "v194": (os.path.join(ROOT, "v194.py"), "agent"),
    # v20 = FLAT single-namespace build of the v19.4 chain (submission format, 410KB)
    "v20": (os.path.join(ROOT, "v20.py"), "agent"),
    # Task 89: v21 = v19.4 chain + v21 trough-banker layer (WOOL/STRAWBERRY/MELON
    # crash-window banking, recovery liquidation). Flat build, 419KB.
    "v21": (os.path.join(ROOT, "v21.py"), "agent"),
    # Task 90: v22 = v20 chain + milk recovery banker layer (2-shop seeds)
    "v22": (os.path.join(ROOT, "v22.py"), "agent"),
    # Task 90b: v22b = tuned milk banker (floor 50, enter on shop count,
    # h0-h5 emission window, chunk cap 8) — H1 variant #2
    "v22b": (os.path.join(ROOT, "v22b.py"), "agent"),
    # Task 90c: v22c = evidence-gated milk banker (inv-fall enter + win-guard)
    # — H1 variant #3
    "v22c": (os.path.join(ROOT, "v22c.py"), "agent"),
    # Task 90d: v22d = evidence-only one-shot milk banker — H1 variant #4
    "v22d": (os.path.join(ROOT, "v22d.py"), "agent"),
    # Task 88: aurax7 "Farmers Is All You Need" (rank 299, 2723.3) — V45 chassis
    # + V44 race escalator + _r60 survival guard + 2842 overlay (frontload +
    # advance_sales LOOK=2 + HORIZON 24). Extracted byte-exact 17-09.
    "aurax7": (os.path.join(ROOT, "aurax7.py"), "agent"),
    # Task 92: v24 = v20 flat chain + GARBAGE-THROTTLE layer (H2 peak-pricing:
    # strip SELL < $15, hold <= 24u, release chunked >= $18; 48-0 vs v46
    # +$1,699, direct vs v20 +$113 t=2.68 CI[$30,$196]). Flat build 419KB,
    # entry-point verified (Task 88 pattern).
    "v24": (os.path.join(ROOT, "v24.py"), "agent"),
    # Task 93 (18-09): ahmedv48 = Ahmed Berat Özer "V48 — Clear the Queue"
    # (kaggle.com/code/ahmedberatozer/kaggriculture-v48-clear-the-queue,
    # version 1, pulled 18-09 via Kaggle API). V47 + market-slot cleanup:
    # remove sale slots that cannot sell, merge repeated same-product SELLs,
    # move executable cash-product sales into freed slots. Byte-exact
    # extraction, sha256 4b5402888feeb4170dce38f34bebe56788b62ca287139fce
    # 7db72df8eb89bb96 (pinned digest asserted inside the notebook). Author's
    # held-out: 36/0/0 vs 6 opponents, mean margin +1471. Entry point
    # _e335_agent = last top-level function (Kaggle last-callable convention,
    # asserted by notebook cell 3).
    "ahmedv48": (os.path.join(ROOT, "ahmedv48.py"), "_e335_agent"),
    # Task 95 (18-09): v25 "THE LAST DAY GENERAL" = v24 chain + stealth
    # opening [BUY 7, SELL 5] (breaks ahmedv48's EXP288 money-mirror at
    # step 1) + COMPACT-FROM-0 outermost layer (V48 Clear-the-Queue
    # mechanism port: merge same-item SELL runs, dead SELL -> [] keeping
    # indices, quantities clamped by the engine-exact projected post-unit
    # shed; gate from step 0). Design: kaggle-research/v25-blueprint.md.
    # Task 96 (19-09): v25 = ahmedv48 byte-exact + two-band drain-eta
    # throttle + compact (44W-2L-2T vs ahmedv48, backup: bench/
    # t96_v25_task96_champion.py.bak).
    # Task 97 (19-09): v25 += _ADV_LOOK=14 module-end rebind — sale-advance
    # horizon race: round 1 look=8 (parity alperen1) nhưng vẫn thua tetsutani
    # v65 (V48 + look 14 + guards, public notebook). Final look=14 (không port
    # guards — đo guards làm yếu trong shared-tape race). v25 = 48W-0L (100%)
    # +$723 vs alperen1; 46W-2L (95.8%) +$494 vs ahmedv48; 44W-4L (91.7%)
    # +$370 vs tetsutani_v65; 10-0 +$785 vs v24. Backups: t96_v25_task96_
    # champion.py.bak, t97_v25f_interim.py.bak.
    "v25": (os.path.join(ROOT, "v25.py"), "agent"),
    # Task 96 (19-09): quiet-seed autopsy upgrades (s119 forensics).
    # v25b = v25 + FERT-never-strip (R40: no town drain -> monotonic decay)
    #         + endgame flush (day>=27 hoard unwinds at any price).
    # v25c = v25b + gate 15->5 (only strip true-bottom sells; avoids the
    #         d16 cliff-delay: strip@$5 -> re-sold@$1 one turn later).
    "v25b": (os.path.join(ROOT, "v25b.py"), "agent"),
    "v25c": (os.path.join(ROOT, "v25c.py"), "agent"),
    # v25d = v25b + drain-eta oracle: hold only shop-backed items whose
    # pure-drain recovery ETA fits before the flush (s106/s119/s121 forensics).
    "v25d": (os.path.join(ROOT, "v25d.py"), "agent"),
    # v25e = v25d + two-band gate: p<5 hoards unconditionally (v25c micro-wins),
    # $5..14 band hoards only drain-backed (v25 crash wins).
    "v25e": (os.path.join(ROOT, "v25e.py"), "agent"),
    # Task 97 (19-09): alperen1 = alperen5252525 "First in Line — Stock Into
    # Income" (kaggle.com/code/alperen5252525/kaggriculture-first-in-line-
    # stock-into-income, pulled 19-09 via Kaggle API). = ahmedv48 byte-exact
    # + module-level _ADV_LOOK=8 override (EXP293 sale-advance: nhìn trước
    # tape 8 turn thay 3, bán sớm cash-product trước đối thủ cùng tape).
    # sha256 53dc224a75301affb6ba6ea549b6d9842110b6b9913f001510d36991c8d
    # fe07a (pinned digest asserted inside the notebook). Author claim:
    # 136W-8L-0T / 144 local games vs 6 public opponents. Entry
    # _e335_agent (giống ahmedv48, Kaggle last-callable convention).
    "alperen1": (os.path.join(ROOT, "alperen1.py"), "_e335_agent"),
    # Task 97 (19-09): v25f = v25 + _ADV_LOOK=8 (match public param change
    # của alperen1 — EXP293 sale-advance lookahead 8). Biến thể nghiên cứu
    # (đã bị v25g vượt: interim backup bench/t97_v25f_interim.py.bak).
    "v25f": (os.path.join(ROOT, "v25f.py"), "agent"),
    # v25g = v25 + _ADV_LOOK=14 — CHAMPION Task 97, đã thăng cấp vào v25.py
    # (giữ file cho bench đối chứng).
    "v25g": (os.path.join(ROOT, "v25g.py"), "agent"),
    # tetsutani_v65 = tetsutani "Demand-Preserving Fourteen-Turn Sale
    # Timing" (kaggle.com/code/tetsutani/demand-preserving-turn-sale-timing,
    # pull 19-09, byte-exact sha256 95b02b9b…) = V48 + _ADV_LOOK=14 +
    # bakery guard (>=2 BAKERY -> look 3) + WOOL/YARN hold guard +
    # canonical 'agent' entry. Sparring partner nghiên cứu (không đăng ký UI).
    "tetsutani_v65": (os.path.join(ROOT, "tetsutani_v65.py"), "agent"),
    # Task 98 (19-09): v251 "DEMAND-PRESERVING RACE GENERAL" (v25.1) =
    # v25 (Task 97 champion) + (1) FIX-A slot hygiene: _v25_compact sắp
    # dòng SELL ghép theo doanh thu giảm dần, CHỈ trong cửa sổ endgame
    # h21/h22 + day>=27 (mổ xẻ s100: MILK $3 ở slot 1 đẩy STRAW 17u ra
    # sau đợt dump của đối thủ -> -$530/turn; fix lật s100 từ thua thành
    # thắng, 48W-0L vs ahmedv48) và (2) port nghiên cứu tetsutani v65
    # "Demand-Preserving Fourteen-Turn Sale Timing" dạng RACE-CONDITIONAL:
    # guards demand-preserving (>=2 BAKERY -> look 3; WOOL offset 5-14
    # hoãn khi YARN_STORE mở) chỉ kích hoạt khi KHÔNG phát hiện race
    # (mirror step-1 / clone-lock / escalation) — tắt khi race để giữ
    # đỉnh look=14. Battery: vs ahmedv48 48W-0L (100%!) +$640 CI95
    # [$521,$759]; vs alperen1 10-0 +$1.192; vs tetsutani_v65 10-0
    # +$689; vs v25 cũ 8W-2L +$330; vs thomast (guard-path) 10-0
    # +$10.072. Audit 4 lĩnh vực (thực vật/động vật/nhân công/kho): CLEAN.
    "v251": (os.path.join(ROOT, "v251.py"), "agent"),
    # Task 99 (19-09): thomast2945 = "The 2945 Farm v9/4" của
    # thomastschinkel (kaggle.com/code/thomastschinkel/
    # the-2945-farm-96-vs-the-top-10-public-bots, pull 19-09) —
    # byte-exact main.py sha256 bfee70e9… = đúng submission 56269928
    # ladder 2944.7. Kiến trúc: route replayer (yhay81/Ahmed V39-V40)
    # + 12 lớp reflex (RACE/RACEPX, PREDICT 451k-event, COURIER, CARROT,
    # HERD, CAPHARV, SL2/VE1/VT1…). H2H của tác giả: tetsutani 55-5,
    # alperen 54-6, V48 55-5. Loader-verified entry 'agent' (last-callable
    # rule). Sparring partner nghiên cứu.
    "thomast2945": (os.path.join(ROOT, "thomast2945.py"), "agent"),
    # Task 100 (19-09): v26 "HERD-ADAPTIVE ANSWER GENERAL" (chính thức, file
    # v26c.py, submission Kaggle 56359569) = v25.1 + port ĐÚNG verdict COW
    # của 2945-farm V9 herd (gate chính xác V9_HERD_*: egg_shops==0 AND YARN
    # chưa mở AND milk_shops>=3 AND MILK>=$150 -> SHEEP/GOOSE mua window
    # (8,11) đổi thành COW — profile "bò chuyên sâu" s110). Đối chứng:
    # ahmedv48 48W-0L mean +1204 (v25.1: +640, s110: +186 -> +13.728!);
    # alperen1 10-0 +1192 & tetsutani_v65 10-0 +689 (đều khớp byte-exact
    # v25.1 trên seed không verdict); thomast2945 48 trận 6W-42L mean -1361
    # (v25.1: 4W-44L -1922; s110 lật -9845 -> +3638). Bản port rộng đầu
    # (4 lớp: herd-mở-rộng + RACEGATE glut + horizon-40 + ORDERPRI2 +
    # CAPHARV) đã LOẠI sau ablation A0/A3: herd sớm đoán-sai YARN muộn tốn
    # -8.7k/ghế s102-104, các lớp runtime khác neutral-đến-hại (-2.3k s122)
    # — xem bench/t100_v26_* và v26.py (lưu bản thí nghiệm thất bại).
    "v26": (os.path.join(ROOT, "v26c.py"), "agent"),
    # Task 110 (19-09): v27 program = chassis thomast2945 byte-exact + các lớp
    # outermost patch (wrapper an toàn kiểu production-loader). v27a = lớp
    # CRASH-DUMP ACCELERATOR: sản phẩm pure-output (MILK/STRAW/MELON/WOOL/
    # EGG/CARROT/TOMATO) đang sập giá cấu trúc (yest <= 88% peak 4 ngày,
    # không hồi) -> bán sạch shed ngay (extend order của tape nếu có, không
    # append vượt MAX 10). WHEAT/FERTILIZER loại trừ (input nội bộ máy móc).
    # v27b = crash-dump NHẤT MỘT LẦN/product/game (tránh bắn đáy dao động);
    # v27c = gate sụt kéo dài 2 ngày (yest & yest2 đều <= 88% peak).
    "v27x_noMILK": (os.path.join(ROOT, "v27x_noMILK.py"), "agent"),
    "v27x_noWOOL": (os.path.join(ROOT, "v27x_noWOOL.py"), "agent"),
    "v27x_noSTRAW": (os.path.join(ROOT, "v27x_noSTRAW.py"), "agent"),
    "v27x_noCARROT": (os.path.join(ROOT, "v27x_noCARROT.py"), "agent"),
    "v27x_noEGG": (os.path.join(ROOT, "v27x_noEGG.py"), "agent"),
    "v27x_onlyMILK": (os.path.join(ROOT, "v27x_onlyMILK.py"), "agent"),
    "v27x_onlySTRAW": (os.path.join(ROOT, "v27x_onlySTRAW.py"), "agent"),
    "v27x_onlyWOOL": (os.path.join(ROOT, "v27x_onlyWOOL.py"), "agent"),
    # v27d = ablation-final: chỉ STRAWBERRY + WOOL (MILK trap dao động đã loại)
    # v27e = v27a + PREPEND (dump order lên đầu queue); v27f = noMILK + prepend
    # v27g = milk gate p>=60; v27h = milk gate day<20
    # v27i = milk gate (day<20 OR p>=60)
    # v27j = dump chỉ từ d26+; v27k = dump chỉ từ d20+
    "v27gs_ALL_none_r88": (os.path.join(ROOT, "v27gs_ALL_none_r88.py"), "agent"),
    "v27gs_ALL_none_r95": (os.path.join(ROOT, "v27gs_ALL_none_r95.py"), "agent"),
    "v27gs_ALL_p60_r88": (os.path.join(ROOT, "v27gs_ALL_p60_r88.py"), "agent"),
    "v27gs_ALL_p60_r95": (os.path.join(ROOT, "v27gs_ALL_p60_r95.py"), "agent"),
    "v27gs_ALL_d20_r88": (os.path.join(ROOT, "v27gs_ALL_d20_r88.py"), "agent"),
    "v27gs_ALL_d20_r95": (os.path.join(ROOT, "v27gs_ALL_d20_r95.py"), "agent"),
    "v27gs_SMW_none_r88": (os.path.join(ROOT, "v27gs_SMW_none_r88.py"), "agent"),
    "v27gs_SMW_none_r95": (os.path.join(ROOT, "v27gs_SMW_none_r95.py"), "agent"),
    "v27gs_SMW_p60_r88": (os.path.join(ROOT, "v27gs_SMW_p60_r88.py"), "agent"),
    "v27gs_SMW_p60_r95": (os.path.join(ROOT, "v27gs_SMW_p60_r95.py"), "agent"),
    "v27gs_SMW_d20_r88": (os.path.join(ROOT, "v27gs_SMW_d20_r88.py"), "agent"),
    "v27gs_SMW_d20_r95": (os.path.join(ROOT, "v27gs_SMW_d20_r95.py"), "agent"),
    "v27gs_SM_none_r88": (os.path.join(ROOT, "v27gs_SM_none_r88.py"), "agent"),
    "v27gs_SM_none_r95": (os.path.join(ROOT, "v27gs_SM_none_r95.py"), "agent"),
    "v27gs_SM_p60_r88": (os.path.join(ROOT, "v27gs_SM_p60_r88.py"), "agent"),
    "v27gs_SM_p60_r95": (os.path.join(ROOT, "v27gs_SM_p60_r95.py"), "agent"),
    "v27gs_SM_d20_r88": (os.path.join(ROOT, "v27gs_SM_d20_r88.py"), "agent"),
    "v27gs_SM_d20_r95": (os.path.join(ROOT, "v27gs_SM_d20_r95.py"), "agent"),
    "v27gs_SW_none_r88": (os.path.join(ROOT, "v27gs_SW_none_r88.py"), "agent"),
    "v27gs_SW_none_r95": (os.path.join(ROOT, "v27gs_SW_none_r95.py"), "agent"),
    "v27gs_SW_p60_r88": (os.path.join(ROOT, "v27gs_SW_p60_r88.py"), "agent"),
    "v27gs_SW_p60_r95": (os.path.join(ROOT, "v27gs_SW_p60_r95.py"), "agent"),
    "v27gs_SW_d20_r88": (os.path.join(ROOT, "v27gs_SW_d20_r88.py"), "agent"),
    "v27gs_SW_d20_r95": (os.path.join(ROOT, "v27gs_SW_d20_r95.py"), "agent"),
    "v27gs_MSM_none_r88": (os.path.join(ROOT, "v27gs_MSM_none_r88.py"), "agent"),
    "v27gs_MSM_none_r95": (os.path.join(ROOT, "v27gs_MSM_none_r95.py"), "agent"),
    "v27gs_MSM_p60_r88": (os.path.join(ROOT, "v27gs_MSM_p60_r88.py"), "agent"),
    "v27gs_MSM_p60_r95": (os.path.join(ROOT, "v27gs_MSM_p60_r95.py"), "agent"),
    "v27gs_MSM_d20_r88": (os.path.join(ROOT, "v27gs_MSM_d20_r88.py"), "agent"),
    "v27gs_MSM_d20_r95": (os.path.join(ROOT, "v27gs_MSM_d20_r95.py"), "agent"),
    "v27gs_MS_none_r88": (os.path.join(ROOT, "v27gs_MS_none_r88.py"), "agent"),
    "v27gs_MS_none_r95": (os.path.join(ROOT, "v27gs_MS_none_r95.py"), "agent"),
    "v27gs_MS_p60_r88": (os.path.join(ROOT, "v27gs_MS_p60_r88.py"), "agent"),
    "v27gs_MS_p60_r95": (os.path.join(ROOT, "v27gs_MS_p60_r95.py"), "agent"),
    "v27gs_MS_d20_r88": (os.path.join(ROOT, "v27gs_MS_d20_r88.py"), "agent"),
    "v27gs_MS_d20_r95": (os.path.join(ROOT, "v27gs_MS_d20_r95.py"), "agent"),
    "v27gs_MW_none_r88": (os.path.join(ROOT, "v27gs_MW_none_r88.py"), "agent"),
    "v27gs_MW_none_r95": (os.path.join(ROOT, "v27gs_MW_none_r95.py"), "agent"),
    "v27gs_MW_p60_r88": (os.path.join(ROOT, "v27gs_MW_p60_r88.py"), "agent"),
    "v27gs_MW_p60_r95": (os.path.join(ROOT, "v27gs_MW_p60_r95.py"), "agent"),
    "v27gs_MW_d20_r88": (os.path.join(ROOT, "v27gs_MW_d20_r88.py"), "agent"),
    "v27gs_MW_d20_r95": (os.path.join(ROOT, "v27gs_MW_d20_r95.py"), "agent"),
    "v27gs_MM_none_r88": (os.path.join(ROOT, "v27gs_MM_none_r88.py"), "agent"),
    "v27gs_MM_none_r95": (os.path.join(ROOT, "v27gs_MM_none_r95.py"), "agent"),
    "v27gs_MM_p60_r88": (os.path.join(ROOT, "v27gs_MM_p60_r88.py"), "agent"),
    "v27gs_MM_p60_r95": (os.path.join(ROOT, "v27gs_MM_p60_r95.py"), "agent"),
    "v27gs_MM_d20_r88": (os.path.join(ROOT, "v27gs_MM_d20_r88.py"), "agent"),
    "v27gs_MM_d20_r95": (os.path.join(ROOT, "v27gs_MM_d20_r95.py"), "agent"),
    "v27gs_MWL_none_r88": (os.path.join(ROOT, "v27gs_MWL_none_r88.py"), "agent"),
    "v27gs_MWL_none_r95": (os.path.join(ROOT, "v27gs_MWL_none_r95.py"), "agent"),
    "v27gs_MWL_p60_r88": (os.path.join(ROOT, "v27gs_MWL_p60_r88.py"), "agent"),
    "v27gs_MWL_p60_r95": (os.path.join(ROOT, "v27gs_MWL_p60_r95.py"), "agent"),
    "v27gs_MWL_d20_r88": (os.path.join(ROOT, "v27gs_MWL_d20_r88.py"), "agent"),
    "v27gs_MWL_d20_r95": (os.path.join(ROOT, "v27gs_MWL_d20_r95.py"), "agent"),
    "v27gs_SMWC_none_r88": (os.path.join(ROOT, "v27gs_SMWC_none_r88.py"), "agent"),
    "v27gs_SMWC_none_r95": (os.path.join(ROOT, "v27gs_SMWC_none_r95.py"), "agent"),
    "v27gs_SMWC_p60_r88": (os.path.join(ROOT, "v27gs_SMWC_p60_r88.py"), "agent"),
    "v27gs_SMWC_p60_r95": (os.path.join(ROOT, "v27gs_SMWC_p60_r95.py"), "agent"),
    "v27gs_SMWC_d20_r88": (os.path.join(ROOT, "v27gs_SMWC_d20_r88.py"), "agent"),
    "v27gs_SMWC_d20_r95": (os.path.join(ROOT, "v27gs_SMWC_d20_r95.py"), "agent"),
    "v27gs_MWMS_none_r88": (os.path.join(ROOT, "v27gs_MWMS_none_r88.py"), "agent"),
    "v27gs_MWMS_none_r95": (os.path.join(ROOT, "v27gs_MWMS_none_r95.py"), "agent"),
    "v27gs_MWMS_p60_r88": (os.path.join(ROOT, "v27gs_MWMS_p60_r88.py"), "agent"),
    "v27gs_MWMS_p60_r95": (os.path.join(ROOT, "v27gs_MWMS_p60_r95.py"), "agent"),
    "v27gs_MWMS_d20_r88": (os.path.join(ROOT, "v27gs_MWMS_d20_r88.py"), "agent"),
    "v27gs_MWMS_d20_r95": (os.path.join(ROOT, "v27gs_MWMS_d20_r95.py"), "agent"),
    "v27gs_S_none_r88": (os.path.join(ROOT, "v27gs_S_none_r88.py"), "agent"),
    "v27gs_S_none_r95": (os.path.join(ROOT, "v27gs_S_none_r95.py"), "agent"),
    "v27gs_S_p60_r88": (os.path.join(ROOT, "v27gs_S_p60_r88.py"), "agent"),
    "v27gs_S_p60_r95": (os.path.join(ROOT, "v27gs_S_p60_r95.py"), "agent"),
    "v27gs_S_d20_r88": (os.path.join(ROOT, "v27gs_S_d20_r88.py"), "agent"),
    "v27gs_S_d20_r95": (os.path.join(ROOT, "v27gs_S_d20_r95.py"), "agent"),
    # Task 110 fine-tune: ratio sweep quanh ALL_none (r90/r92/r93, r95+min_day)
    # Task 110 FINAL: v27 "SECOND-HALF PRICE-CURVE GENERAL" = chassis 2945
    # byte-exact + DUAL-MODE crash-dump (clone-detector d4-8: 2945-family
    # r92 full-dump / V48-class race-mode no-milk d12+ r95). Protocol
    # 100-104 vs thomast2945: 10W-0L (paired +358/+1446/+184/+2706/+1094).
    # 20-seed: 26W-14L mean +201 worst -274. Vs 11 đối thủ khác: V48 10-0,
    # tetsutani 10-0, v18/43/44/45 10-0, alperen1/v24 8-2, v25/251/26 6-4.
    "v27": (os.path.join(ROOT, "v27.py"), "agent"),
    # v27n = v27 + clone-detector dual-mode (clone=2945-family r92 full;
    # non-clone=V48-class race-mode: no MILK, d12+, r95)
}


# kaggle_environments wraps every agent call with redirect_stdout(StringIO)
# (core.py L645-648) to capture agent logs — so anything written to sys.stdout
# *from inside an agent wrapper* is swallowed. Hold the REAL stdout from
# import time and write events through it directly.
_REAL_OUT = sys.stdout


def out(obj):
    _REAL_OUT.write(json.dumps(obj, separators=(",", ":"), default=str) + "\n")
    _REAL_OUT.flush()


def load_agent(name, tag):
    if name in AGENTS:
        path, entry = AGENTS[name]
    elif os.path.isfile(name):
        path, entry = name, "agent"
    else:
        raise SystemExit(f"unknown agent: {name}")
    modname = f"arena_{tag}_{os.path.splitext(os.path.basename(path))[0]}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    fn = getattr(mod, entry, None)
    if not callable(fn):
        raise SystemExit(f"agent {name} has no callable '{entry}'")
    return mod, fn


def _jsonable(x):
    try:
        json.dumps(x)
        return x
    except Exception:
        return str(x)


def extract_diag(mod, obs):
    """Pull the agent's internal brain state for the observer UI.

    v5 exposes `_arena_diag(obs)` explicitly. Older v4-family modules are mined
    generically from their `_STATE` dict (tm mode/pm + today's plan).
    """
    try:
        fn = getattr(mod, "_arena_diag", None)
        if callable(fn):
            return _jsonable(fn(obs))
        st = getattr(mod, "_STATE", None)
        if not isinstance(st, dict):
            return {}
        tm = st.get("tm") or {}
        d = {"mode": tm.get("mode")}
        if "pm" in tm:
            try:
                d["pm"] = round(float(tm["pm"]), 3)
            except Exception:
                pass
        od = tm.get("opp_day") or {}
        if od:
            d["opp_flows"] = {k: round(float(v), 1) for k, v in od.items()}
        try:
            day = obs.get("day")
        except Exception:
            day = None
        plan = st.get(("plan", day)) if day is not None else None
        if isinstance(plan, dict):
            d["herd"] = {k: plan.get(k) for k in
                         ("goose_target", "cow_target", "sheep_target")}
            d["crop_plan"] = plan.get("crop_tiles")
            d["feed_demand"] = plan.get("feed_demand")
        return d
    except Exception:
        return {}


class TurnBuffer:
    """Collects one turn record from the two agent calls of the same step."""

    def __init__(self, emit):
        self.emit = emit
        self.cur = None

    def start_step(self, step, day, hour, farms, market, town):
        self.flush()
        self.cur = {
            "t": "turn", "step": step, "day": day, "hour": hour,
            "farms": farms, "market": market, "town": town,
            "priv": [None, None], "acts": [None, None],
            "diag": [{}, {}], "times": [0.0, 0.0],
        }

    def record(self, side, obs, action, diag, ms):
        if self.cur is None or self.cur.get("step") != _step_of(obs):
            # first call of a new step
            try:
                day = obs.get("day") or 0
                hour = obs.get("hour") or 0
            except Exception:
                day, hour = 0, 0
            self.start_step(_step_of(obs), day, hour,
                            _farms(obs), _market(obs), _town(obs))
        self.cur["priv"][side] = _private(obs)
        self.cur["acts"][side] = _jsonable(action)
        self.cur["diag"][side] = diag
        self.cur["times"][side] = round(ms, 2)
        if side == 1:
            self.flush()

    def flush(self):
        if self.cur is not None:
            self.emit(self.cur)
            self.cur = None


def _step_of(obs):
    try:
        return (obs.get("day") or 0) * 24 + (obs.get("hour") or 0)
    except Exception:
        return -1


def _farms(obs):
    try:
        return _jsonable(obs.get("farms"))
    except Exception:
        return None


def _market(obs):
    try:
        return _jsonable(obs.get("market"))
    except Exception:
        return None


def _town(obs):
    try:
        return _jsonable(obs.get("town"))
    except Exception:
        return None


def _private(obs):
    try:
        return _jsonable(obs.get("private"))
    except Exception:
        return None


def wrap_agent(mod, fn, side, buf):
    def agent_fn(obs, config=None):
        t0 = time.perf_counter()
        action = fn(obs)
        ms = (time.perf_counter() - t0) * 1000.0
        buf.record(side, obs, action, extract_diag(mod, obs), ms)
        return action
    return agent_fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="agent name or file path (seat 0)")
    ap.add_argument("--b", required=True, help="agent name or file path (seat 1)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--max-steps", type=int, default=None,
                    help="override episodeSteps (smoke tests)")
    args = ap.parse_args()

    from kaggle_environments import make

    modA, fnA = load_agent(args.a, "A")
    modB, fnB = load_agent(args.b, "B")

    cfg = {}
    if args.seed is not None:
        cfg["seed"] = args.seed
    if args.max_steps is not None:
        cfg["episodeSteps"] = args.max_steps
    episode_steps = cfg.get("episodeSteps", 720)

    out({"t": "hello", "runner": 1, "a": args.a, "b": args.b,
         "seed": args.seed, "episodeSteps": episode_steps})

    buf = TurnBuffer(out)
    wrapA = wrap_agent(modA, fnA, 0, buf)
    wrapB = wrap_agent(modB, fnB, 1, buf)

    wall0 = time.time()
    env = make("kaggriculture", debug=False, configuration=cfg or None)
    try:
        env.run([wrapA, wrapB])
    finally:
        buf.flush()

    try:
        final = env.steps[-1]
        r0 = final[0].reward
        r1 = final[1].reward
        r0 = float(r0) if r0 is not None else 0.0
        r1 = float(r1) if r1 is not None else 0.0
    except Exception:
        r0 = r1 = 0.0
    winner = 0 if r0 > r1 else (1 if r1 > r0 else -1)

    out({"t": "end", "rewards": [r0, r1], "winner": winner,
         "wallS": round(time.time() - wall0, 1),
         "turns": len(env.steps)})


if __name__ == "__main__":
    main()
