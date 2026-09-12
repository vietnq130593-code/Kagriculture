# v9 "STACK-SWEEP" (Task 54) — TÁI CẤU TRÚC KERNEL LAO ĐỘNG (người dùng duyệt).
# Nền = v8 VÒNG 50 (R188-R192) nguyên vẹn; chỉ thay kernel + gắn lại bộ FERT
# 53c (đã chứng minh +$1,6k trên 20 seed nhưng bị kernel bão hòa làm sụp
# ext-seed — xem TOP3_REPLAY_ANALYSIS.md §11.16).
#
# KERNEL-AUTOPSY (Task 54, kautopsy9.py + kgap.py + ktop3.py — new52/53r50):
#   v8: MOVE 63%, walk-per-useful 2,49, chuỗi TB 3,1 bước, 64 op hữu ích/ngày
#   top-3: MOVE 37%, walk-per-op 1,02-1,52, gap-0 (đứng nguyên chỗ) 35-45%
#          + gap-1 (ô kề) 25-30%, 92-123 op/ngày
#   → Top-3 KHÔNG đi xa hơn — họ LẶP NHIỀU OP TRÊN CÙNG Ô (stack) và sweep
#     ô kề nhau. Khoảng cách còn lại = morning-commute hands (spawn shed).
#
#   K1 CONTINUATION CLAIMS (phase-0 assignment): unit free ở vị trí hiện tại
#      được claim NGAY task trong bán kính 1 (tier ≤ 2) hoặc đúng ô đứng
#      (tier 3, gap-0) TRƯỚC khi phase-1 tier-first chạy → serpentine sweep
#      (WATER dâu ô-kề-ô) + op-stacking (WATER→FERTILIZE / FEED→CARE→COLLECT
#      / HARVEST→PLANT cùng ô, 0 bước đi).
#   K2 MORNING CASCADE (h ≤ 2): phase-1 sort theo (tier, d_shed) — hands
#      spawn ở shed làm đàn (gần shed) TRƯỚC rồi quét ra ngoài, commute
#      buổi sáng thành lao động có ích.
#   K3 FERT-KEEP 8 (R194-53c): giữ 8 FERT trong shed từ d4 (cũ 2) — nuôi
#      chuỗi FERTILIZE gap-0; kernel cũ hấp thụ 2,7 lệnh/ngày vì MỖI lệnh
#      tốn 1 chuyến đi; stack gap-0 chỉ tốn 1 unit-hour.
#   K4 CARROT-FLOOR 6 (R195-53c): carrot không chết — chỉ thiếu FERT (2
#      nước trên ô fertilized = 4u thay 2u). Floor standing 6 + nhánh
#      FERTILIZE carrot tier 2.
#   K5 MELON-FERT ws-1 (R196-53c): bón melon 1 ngày TRƯỚC window (3 nước
#      chạm 6u, dư lao động cho dâu) + mở _task_still_valid tương ứng.
#   K6 DÂU-EVENT FERT cap 6/h (53c): tier 2 giữ nguyên, dàn đều giờ.
#
# V9.1 SUPPLY-BUMP (sau khi kernel đồng bộ — đo trên chính battery v9):
#   Kernel PASS 920 unit-hour/game (30,7/ngày) = lao động rảnh → nạp thêm
#   cây trồng để tiêu hóa:
#   • DÂU standing 24 → 28 (d5-13) / 20 (d14-15) / 16-14 (d16-19) /
#     16-12 (d20-26) — mũ cũ 24 là giới hạn của kernel 62%-MOVE (R151
#     s306); top-3 đứng 24,8 FLAT cả mùa và bán 254u.
#   • CARROT floor 6 → 8.
#   KẾT QUẢ v9.1 (battery 50 seed 100-149 vs v6): 50/50 (100%), TB $75.238,
#   max $96.972 (s127); v9.0: $73.044/20 + $72.532/30; vòng-50 v8: 43/50
#   (86%) $67.2k. Đầu-trực: v9.1 vs v8 15/20 ($68.133 vs $62.730), vs v7
#   10/10 ($59.749 vs $44.614).
#
# v8 "REGION-FLOW" (Task 42) — kernel lao động lai theo mô hình top-3
# (TOP3_REPLAY_ANALYSIS.md V3.0 + R151): v7 + 8 delta chọn lọc bằng differential.
# VÒNG 50 (R188-R191 — fix tỷ số thua v6; god-ledger 4 trận thua đậm
#   s118/s114/s108/s111, battery 20 seed 15/20):
#   GAP#1 MELON WAVE-1 (−$8.5-16.4k/trận): v6 d0 mua 14 hạt melon + 0
#     thú, thu $11.8-18.5k ngay d11; v8 chỉ 8 hạt (starter thú $1.600 ăn
#     vốn) → $1.6-6.7k. R188: starter 2 bò+1 cừu+1 ngỗng → 1 cừu+1 ngỗng
#     ($800, giữ sheep-AD d0 của R179), quota d0 wheat 14→12 + carrot
#     8→4 + MELON 8→14 (đủ 32 ô; luật 45% không còn cắt mất 1 hạt).
#     Bò vào lại d2+ qua trajectory R180 (v6 mở 0 thú vẫn đạt 13 con d15).
#   R189 WHEAT HOLD SỚM d≤11: 1.50 → 0.90 — bán ngay vụ d4-6 để có vốn
#     mua hạt dâu từ d5 (v6 trồng dâu d5, v8 d7 → mất 1 chu kỳ thu;
#     cửa sổ an toàn: đàn v6 0-4 con chưa hút feed — R162 chỉbinding d12+).
#   R190 WHEAT CUTOFF d26 → d21: hạt/task wheat d22+ chỉ còn 1 mứ chín,
#     cướp đúng lao động tưới/thu dâu (s118: P10 wheat d24 → 22 ô dâu
#     chết trắng $8-12k). Áp cho cả seed-buy refill + fill-law plan.
#   R191 CỪU-6: trajectory 1+day//4 → 1+day//3 + cắt cap ngỗng→bò→cừu
#     (cũ cừu trước) — v6 6 cừu WOOL $19.7-24.7k vs v8 4 con $5.6-18.3k.
#   R192 MELON SURVIVAL: ô melon cu>=1 trong cửa sổ chín (age 6-12) mà
#     trượt nước HÔM NAY = chết trắng — lên tier-0 budget riêng cap 4/h.
#     Root-cause các trận $39-46k: 12 ô melon d0-9 chết sạch d9-10 (s132/
#     146/123) → melon rev $4-6.4k vs v6 $20-23.6k (gap #1, −$14-18k).
# VÒNG 48 (11.13 — lượt fix thứ 2, R178/R179/R180 + R184/R185):
#   R178 d29 = NGÀY LÀM VIỆC ĐẦY: bỏ gate `day < 29` hire (0 hands d29 cũ =
#     $2.288 vs $7.484 top-3); d29 drop từ h8 + MỞ lại bán wheat d29 (R175
#     chỉ chặn d27-28; game kết h22 không EOD = feed tồn shed là giá trị chết).
#   R179 CỪU TỪ D0: starter 2 bò + 1 cừu + 1 ngỗng $1.600 (giữ $1.400 hạt;
#     melon floor 300 d0) + sheep window w0 2→0 + buy_per_day d0 = 4.
#     Sheep-AD 29 → 57,5 (top-3: 71); WOOL $4,1k → $8-13,7k.
#   R180 RAMP = TỐC TOP-3: cap money (1+money//900) → trajectory bò 2+day//2
#     / cừu 1+day//4 — AD d0-10 41 → 62 (top-3: 77).
#   R180b/c VAN HẠT SÓNG DÂU: thú chờ (cash_floor +700) khi dâu đứng <14
#     d5-14; dâu TRƯỚC carrot trong _seed_order d5-13 (chặn thú/wheat/carrot
#     ăn vốn hạt — s100-r1: dâu d7 = 5 ô).
#   R180d MILK VETO: floor-6 bò chỉ khi inv MILK ≤ I0+5 & opp bò ≤ 6 (s100:
#     shop-draw 2 milk-shop — v8+7 bò tràn cả nhau, giá $297→$61).
#   R184 TẮT carrot floor 8 (0-6u bán cả mùa = hạt + 8-10 task nước lãng
#     phí, trả phase-2 cho melon; marg-ladder giữ nguyên).
#   R185 MELON SALVAGE: thu age ≥ max_yield_day−1 bất kể yu (chết tuổi 13
#     = 0u; 6u → 19,7u TB).
#   R183 [bài học âm]: 2 lần nâng tier tưới carrot/melon (0/1/2) đều giết
#     seedling/service — PHA-1 BÃO HÒA, kernel 62% MOVE không có dư địa.
#   R186: shop-draw path-dependent (weed-spawn ăn RNG theo ô trống) → battery
#     phải ≥10 seed. KẾT QUẢ: vs v7 10/10 thắng, $51,3k → $61,5k (+19,9%);
#     vs v6 8/10, $65,8k. Gap còn lại = kernel (R151/R164).
# VÒNG 44 (11.10) — 5 TRỤ CỘT FIX TẠI CHỖ (mục tiêu: đạt chỉ số 3 hạng đầu):
#   Trụ 1 (R156) ĐÀN D0: starter 2 bò + 1 ngỗng ($1.100) ngay d0-h2 — mô phỏng
#     SpaTaro/Otter; d1-4 ramp bằng dòng FERT ($95-100/con/ngày vô điều kiện);
#     bỏ cổng day<2/day<5/day<6=0 của _daily_plan.
#   Trụ 2 (R157) ĐÀN ÔM SHED: reserved sort theo khoảng cách shed thật
#     ((4,4)-(5,5)) từ d0-h0 TRƯỚC khi planting claim ô trung tâm; BUILD
#     tier-urg d0-3; _struct_reserve bỏ money-gate (BUILD miễn phí engine).
#   Trụ 3 (R160) ĐẤT CHẾT ≤6: T_DIG 5→3; wheat-refill TRONG NGÀY (standing<18
#     → PLANT tier 1-2, không chờ plan h0 — plan không thấy ô vừa harvest).
#   Trụ 4 (R158) FEED TỚI d28: wheat_reserve giữ tới d28 (base bán sạch từ d26
#     → 7-8 con trốn); mua feed mở gate d≤3 (pw≤45) + d≥20 (pw≤70, need 14).
#   Trụ 5 (R159) MÁY WHEAT CẢ MÙA: refill floor 18 + plan quota 24-standing
#     giữ nguyên; không còn phụ thuộc BUY_PRODUCT wheat 814u.
# VÒNG 45 (11.11 — god-ledger exact 4 trace top-3 + 6 game v8, 0-mismatch):
#   Khoảng cách $46.096 = dâu −$29.8k (53u vs 254u) + wheat NET −$18k (mua
#   610u $31k vs top-3 net +$10k) + melon −$8.5k + carrot −$5.8k; bù milk/egg
#   /fert +$16k. Đàn v8 5.67 cụm (big_share 0.62) vs top-3 MỘT khối (0.79-0.91).
#   5 TRỤ MỚI:
#   Trụ A (R167) ĐÀN LIỀN KHỐI: reserved mọc BFS-liên-thông từ khối sẵn có
#     (không sort từng ô quanh vòng shed) — ncomp≤2, adj ≥90%, cây bao quanh.
#   Trụ B (R168) ĐÀN 13 = top-3 parity: floors cừu2/bò5/ngỗng5 cho phép cap
#     13 hạ thật (floor cũ 4+6+7=17 → đàn phình 19 → mua 610u wheat).
#   Trụ C (R169/R170) MÁY WHEAT 3 LAYER: quota floor max(16, đàn+3) + bỏ
#     shift wheat→dâu + seed-buy nhìn standing SỐNG (16−live) + refill
#     floor 20 tier1 khi <16.
#   Trụ D (R169) KHỐI LƯỢNG KÊNH: carrot floor 8 khi đứng <6 (bán 135u@$44.8
#     của top-3 vs 8u của v8) + melon wave-2 nới marg 0.78→0.66/0.70→0.58
#     mở tới d21 + PLANT tier 3 khi >6 ô trống (R171 hố sau mua đất).
#   Trụ E (R168) FEED-BUY ACUTE-ONLY: bỏ cổng dairy-deep $52 — đàn 13 + máy
#     20 = tự cấp (top-3 mua 248u $9.9k, v8 cũ mua 610u $30.9k).
# ĐÍCH ĐO: final $90-110k | đất chết d7-26 ≤6 | cây đứng ≥55 | dâu bán ≥200u
#   | đàn 1 khối ncomp≤2 | wheat đứng 16-20 cả mùa.
# VẤN ĐỀ v7 (đo bằng autopsy 3 trận + god-replay chuẩn top-3):
#   empty d9-27 = 25-37 ô (top-3: 0-5) | MOVE 4.962/mùa (top-3 2.700-3.100)
#   wheat chết d15 (1-6 ô đứng vs top-3 17-29) | FERTILIZE = 0 (top-3 91-186)
#   PLANT 3,9/ngày (top-3 10-15) | không kênh đứng cuối mùa (carrot/tomato)
# 8 DELTA (giữ NGUYÊN chassis v6.6 + 4 luật đất cứng + mọi delta kain38/40/41):
#   Δ1 EVENT-WATER: dâu chỉ tưới NGÀY EVENT (interval 2 = tự sống, +2u khi
#      nước+fert) + CAP-6 tier-0/giờ (v8b lesson: 14 task tier-0 chồng nhau
#      d20 làm 9 thú bỏ đói) — cắt nửa số task tưới tier-0
#   Δ2 HYBRID ASSIGNMENT (bài học 4 biến thể a/b/c/d): pha 1 = tier-first
#      tier 0-2 (money-ops: SERVICE/HARVEST — phủ bảo đảm như v7); pha 2 =
#      geo + aging (fill-ops: PLANT/T_WATER_YIELD/DIG — task gần unit trước,
#      task chờ lâu cộng điểm đói). Geo toàn phần pha loãng money-ops (v8a/c:
#      MILK −$8k); tier-first toàn phần làm PLANT tier-2 cướp service (v8d
#      −$18k). Lai là đúng.
#   Δ3 HARVEST 5 -> 2: tiền không ngồi trên ô (autopsy: 183/mùa vs 410-615)
#   Δ4 PLANT tier 4 khi trống>6 + WHEAT STANDING-TARGET quota 24 ô
#      (sập <14 -> tier 1 + trồng lại 10/ngày; đủ -> 2-4 duy trì) + carrot
#      d24+ tier 1 (cửa sổ 2 ngày)
#   Δ5 FERTILIZE 7 -> 3: bón dâu/tomato NGÀY EVENT (nước+fert = +2u) +
#      wheat window + melon — nguồn: đàn nhả 16-22 FERT/ngày
#   Δ6 GOOSE-SERVICE tier 1 (trứng+fert $82-114/ngỗng-ngày R145)
#   Δ7 QUOTA: carrot late 12/10/8 (top-3 đứng 10-15 ô d24-29 = $4-7k);
#      straw wave-2 d14-15 12/10 (CF-validated +$3-4k trên ô trống)
#   Δ8 BỎ T_WATER_MAINT parity (tưới chẵn-lẻ = 0 yield)
# FIX-BOM (tồn tại NGẦM từ v7): _task_still_valid nhánh FERTILIZE tham chiếu
#   `day` ngoài scope -> NameError -> agent() trả hands=[] (CẢ ĐỘI ĐỨNG IM
#   HẾT NGÀY). v7 hiếm nổ (fert melon hiếm); v8 nổ liên tục cho tới khi fix.
# KẾT QUẢ (Task 42 hoàn chỉnh):
#   • vs v7 (đầu trực tiếp, 60 game / 30 seed 100-129): 57/60 THẮNG,
#     ratio 1.434x/1.285x theo lô — ÁP ĐẢO
#   • vs v6 (battery 100 game 2 ghế): 94/100, ratio 1.284x, avg $58.081
#     (v7: 96/100, 1.278x, $57.972 — ngang thống kê, thua hoàn toàn đầu-trực)
#   • empty d9-27: 6.6 ô (v7: 25.3; top-3: 0-5) | máy wheat đứng cả mùa
#     9-20 ô (v7 chết 1-6 từ d15) | PLANT 165 (v7: 116) | FERTILIZE 16-21
#     (v7: 0) | wave-2 dâu + carrot d24-26 + tomato kênh chạy thật
#   • v8f-fix (seedling-survival tier 4): lật 3 seed thua nặng nhất
#     s115 28.9k->62.4k, s130 32.0k->61.6k, s105 45.7k->64.5k
# Chưa đạt top-3 (bàn giao v9): WATER 580 (target 982-1387) | HARVEST 196
#   (410-615) | weeds 11.5 ô | FERTILIZE 16-21 (91-186) | đàn theo shop-draw
#   còn thua v6 ở seed wool/milk-deep (s129).
# Giữ NGUYÊN v6.6-chassis + 4 luật đất cứng + mọi delta kain38/40 + R147
# (land reserve), R148 (tranche-8 + sell theo giờ), E8-lite, hire tiers.
# ---- lịch sử kain38-41 (Task 34-40) ----
# Chẩn đoán fill_analysis2 (4 trận browser, kbuy [5,10]/[10,11]):
#   d5-9 trống 29-58% (valley vốn), d10-11 vọt 45-78% (mở 25-50 ô mới),
#   d15-28 MẠN TÍNH 30-41% trống với $10-55k tiền nằm chết — quota design
#   chỉ nhắm ~50/75 ô (wheat 21-24 + straw 30 chết d21 + carrot 0-4).
#   Giá cuối game: WHEAT $49-51 (v6 hút 150-240u/ngày d11-25 + endgame dump
#   $8k/ngày đã có sẵn), CARROT $42-72, TOMATO $60→$155 KHÔNG AI TRỒNG.
# ΔA SMART-RESERVE (valley d5-13): hạt RẺ (carrot $20, wheat $10) bỏ
#   land_reserve khi money < 800 (SW $2150 còn xa — carrot hoàn vốn 3-4 ngày
#   tự bơm vốn về; straw/melon GIỮ reserve nguyên vẹn). Carrot fill cap
#   14 -> 20.
# ΔB FILL-LAW (lõi): mọi ô trống còn lại SAU quota phải đi làm:
#   d4-13 carrot-20 -> wheat hết phần còn lại; d14-26 WHEAT TOÀN BỘ còn lại
#   (giá $33-51 tăng đều; v6 feed-demand + endgame E8-lite hút sạch).
#   Thay _late_cap 8/16 cứng.
# ΔC TOMATO-CHANNEL (d17-19): quota 10/8/6 — kênh 0 đối thủ (giá d26-29
#   $113-155; 4 event d26-29 = 4u × ~$130 = $520/ô từ hạt $50). Trước đó
#   TOMATO quota 0 suốt game.
# ΔD CARROT-LATE + WHEAT-LATE: cửa sổ d≤24 -> d≤26 (trồng d26 chín d28-29:
#   carrot 3u×$66, wheat 3u×$51); ngưỡng marg carrot mềm 0.88/0.76/0.62.
# ΔE MELON-LATE-2: mở cửa sổ d17-18 quota 6 marg≥0.70 (giá $110-122 vẫn
#   lãi $610/ô: 6u×$115 - $80).
# ΔF HIRE-14: cap 14 khi d10-26, money≥6000, trống >10 (đơn #14 fib $377/
#   ngày — lấp nhanh hơn đi bộ; lao động tier bảo vệ feed/care/water-crit).
# Giữ NGUYÊN v6.6-chassis + 4 luật đất cứng + mọi delta kain38.
# ---- kain34 "FILL-EVERYTHING" gốc (Task 34/Phase-1):
# Autopsy kain33 (fill_analysis + internal trace, 15 trận): 3 lỗ hổng lấp đất:
#   Δ1 FILL-AFFORD d4-14: plan giao 30 ô cho dâu nhưng floor $900 chặn mua
#      hạt khi money $400-600 (d5-9) -> 30 ô TRỐNG 5 NGÀY LIỀN, không fallback
#      sang wheat $10. Fix: ô của cây đắt quá khả năng -> rút sang wheat;
#      filler 8 -> TOÀN BỘ remaining khi feed_demand cao; wheat fill mua
#      hạt không giữ land_reserve (quay vòng 5 ngày trả lời nhanh hơn).
#   Δ2 PLANT-PRIORITY d12+: PLANT tier 5 thua SERVICE/WATER (tier 2-3) triệt
#      để — d15-24 tạo n_plant=16 task/ngày nhưng 0 hành động trồng (13 units
#      dành 65% thời gian đi bộ). Fix: PLANT tier 4 khi empties>10.
#   Δ3 HIRE-BOOST: d4-25 khi trống >12 ô -> target 10 units (10 hands =
#      fib $143/ngày — rẻ; lấp sớm trả lời nhiều hơn).
#   Δ4 CARROT d24: trồng d24 chín d27-28 (+$140/ô cuối game).
# ---- kain35 "FILL-SMART" (Task 34/Phase-1 v2) — đo lại sau kain34 (2/6,
#   v6 +$17.6k: wheat-flood = SUBSIDY feed cho engine bò v6, R113):
#   Δ1' REVERT wheat-flood. Valley fill = straw-partial (mua tối đa 4 hạt
#       dâu/ngày giữ buffer $200 — dâu ROI ~19x: 4 event × 4u × $150-250)
#       + redirect phần hạt không nổi sang CARROT (không phải feed — v6
#       không arbitrage được; cap 8 ô).
#   Δ5 LATE-STRAW d16-19: engine dâu 2 bên chết tuổi 17 -> d21-28 kênh dâu
#       THIẾU CUNG, giá $180-303 (autopsy 15 trận). Trồng d16-17 quota 8
#       (2 event d26-28), d18-19 quota 5 (1 event) khi marg ≥ 0.82.
# ---- kain36 (v3): bỏ cap 4 hạt dâu/ngày của kain35 (bug: chặn cả ngày
#   giàu d11 — $3415 vẫn mua 4 → engine dâu không đạt 30 cây đứng, d20-28
#   empty 37%). Seedable = buffer thuần (money-200)//100. Thêm Δ1'' fill
#   carrot cap 14 ô cho valley (không wheat — không feed v6).
# ---- kain37 (v4): 2 cửa còn lại:
#   Δ6 LAND-BUFFER: NE mua khi money >= 1350 (d5-7, fallback 8-9), SW >= 2400
#       — autopsy kain36t: mua NE d5 lúc $1102 -> còn $102 -> 5 ngày không
#       doanh thu (melon d12+, dâu d15+) -> tiền rơi $16, KHÔNG MUA ĐƯỢC
#       hạt nào -> death spiral 25 ô. Buffer $350 sống qua thung lũng.
#   Δ7 CHEAP-SEED-ALWAYS: wheat/carrot floor bỏ land_reserve (hạt $10-20
#       không bao giờ endanger SW $2150 — max $300; straw/melon giữ reserve).
#   Δ8 LATE-WHEAT: d17-22 filler 8 -> 16 ô (wheat cuối game $40-49 —
#       seed 103: v6 out-earn ta d22-26 +$5.5k nhờ engine wheat 100 ô).
# ---- kain38 (v5): sửa 2 bug kain37 (s100: NE KHÔNG BAO GIỜ được mua —
#   LOCKED 75 đến d12; straw-partial tự ăn vốn d5h0 $300 -> money không
#   chạm $1350; fallback có khoảng hở: lỡ NE thì nhánh SW không bao giờ
#   chạy -> farm kẹt 25 ô vĩnh viễn):
#   Δ6' NE gate về 1000+150 (buffer nhỏ), cửa sổ liền mạch d5-9 + escape
#       hatch d10+ (money >= 1150 vẫn mua NE — muộn còn hơn không).
#   Δ9 SPEND-DISCIPLINE: straw-partial + carrot-fill + wheat/carrot floor
#       phẳng CHỈ chạy khi nq >= 2 (sau NE). Trước khi mua đất: giữ vốn.
# Giữ: Δ5 late-straw, Δ8 late-wheat, Δ2/Δ3/Δ4, 4 luật đất cứng.
# (kain32 đã thử cả wheat-machine + watchdog 85%: kernel lao động v6 không
# chịu nổi 85% util — chết đàn d20-21; kain33 = thử nghiệm SẠCH luật đất)
# ---- gốc kain31 "SOLVER-2" (Task 31) — autopsy 146: fix 2 leak của kain30:
#   ΔA BỎ NOON-REPLAN (autopsy seed 146: plan h12 trồng wheat 2 LẦN/ngày
#      cướp đất dâu — 15 vs 22 tiles của v6 = -$8k; quota dâu chưa bao giờ
#      bị cắt, chết vì hết ĐẤT). Trở lại single-plan h0 như v6.
#   ΔB MILK-COMMIT: cow floor 6 khi 4<=d<=19 & sữa >= 0.95xbase — v6 commit
#      9 bò d8-11 khi ta băm vốn vào ngỗng -> milk_room ta âm -> nhượng kênh
#      sâu nhất (-$16.7k trên 146; kênh hút 163u giá vẫn $312 = CHƯA bão hòa).
#      Đàn: ngỗng floor 7/cap 9, cut order cừu(>=4) -> bò(>=6) -> ngỗng(>=7),
#      herd cap 16; buy order COW trước (GOOSE sau).
#   ΔC FERT hold 0.40 -> 0.50 (146: 224u @ $60 = dưới đường cầu).
# Giữ kain30: P3 graded-quota (_marg), S3 straw anti-yield, S4 late windows,
# S1 egg-fortress (floor 7), melon-14 idol, tranche-8, E8-lite, care tiers.
# ---- kain30 gốc:
# KERNEL MỚI (bước ra idol constants, thay bằng giá-trị-biên):
#   ΔP3 GRADED-QUOTA: mọi quota premium (MELON/CARROT/STRAW) định giá bằng
#      _marg() — giá biên TRUNG BÌNH của các unit sắp bán vào kênh chiếu
#      theo (inv hiện tại + pipeline 2 bên − drain tương lai) thay vì
#      constant 14/30/8 (đây là hạt nhân P3: $/unit biên → quyết định).
#   ΔR NOON-REPLAN: plan key (day, noon) — tính lại toàn cục lúc h12
#      (v6 cache 24h không thích ứng giữa ngày).
# SEAM (khai thác điểm yếu v6 — xem RESEARCH_V7.md):
#   S1 EGG-FORTRESS: v6 hard-cap ngỗng 6 → floor 8/cap 9 khi opp_geese≤7
#      (R102: kênh không-đối-chiếu-được); cắt BÒ TRƯỚC khi vượt herd-cap.
#   S3 STRAW-COMMIT: _marg ≥ 0.98 → không nhượng kênh dâu (R101/R105:
#      cắt quota = hiến phần chia; giá-biên quyết định, không pipeline).
#   S3b LATE-STRAW d14-15: quota 8 (v6 dừng 6) khi giá biên còn ≥ 1.0.
#   S4 LATE-MELON d15-16: quota 6 khi marg ≥ 0.78 (đất trống endgame).
# Giữ nguyên v6.6: melon-14 d0-7 (idol K13), tranche-8 (R90), feed-gate $52
# (R92), E8-lite (drain-aware endgame), hire/land/task tiers, care discipline.

import math

CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}
ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
MARKET_I0 = 10000
MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "I0": MARKET_I0, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "I0": MARKET_I0, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "I0": MARKET_I0, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": MARKET_I0, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": MARKET_I0, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "I0": MARKET_I0, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": MARKET_I0, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": MARKET_I0, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}
SHOPS = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != "FERTILIZER"]

TURN_PER_DAY = 24
EPISODE_STEPS = 720
MAX_ORDERS = 10
SHED_CAP = 100
LAND_PRICES = [1000, 2000, 4000]
MAX_SHOP_INSTANCES = 8

CYCLE_LEN = {"WHEAT": 5, "CARROT": 4, "TOMATO": 12, "STRAWBERRY": 17, "MELON": 13}
YIELD_PER_CYCLE = {"WHEAT": 5, "CARROT": 3, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}

T_WATER_CRIT = 0
T_SERVICE_URG = 0
T_HARVEST_URG = 2
T_DELIVER = 2
T_BUILD_URG = 2
T_SERVICE = 2
T_WATER_YIELD = 3
T_BUILD = 4
T_HARVEST_ANIMAL = 2
# v8 Δ3: HARVEST 5 -> 2 (autopsy: 183/mùa vs top-3 410-615 — tier 5 bị
# SERVICE/WATER hút sạch, thành tiền ngồi trên ô)
T_HARVEST = 2
# v8e: PLANT 5 -> 4 (phase-2 geo; phase-1 không đụng money-ops)
T_PLANT = 4
T_DIG = 4  # Trụ 3-fix: 3 bị DIG-backlog át PLANT tier-4 (probe s130: 29 DIG
            # nuốt tomato cả ngày — tomato 0 ô dù seed đã mua); 4 = ngang
            # PLANT, phase-2 geo tự phân giải theo khoảng cách + age
T_WATER_MAINT = 3
# v8 Δ5: FERTILIZE 7 -> 3 (phase-2 geo; bón dâu/tomato NGÀY EVENT
# +1u ≈ $130-190; top-3 bón 91-186/mùa, v7 = 0)
T_FERTILIZE = 3

FERT_SELL = True
FERT_FLOOR = 38
ANIMAL_CAP = 14
TOM_QUOTA = 6
HOLD = {"MILK": 0.98, "WOOL": 0.94, "STRAWBERRY": 0.80, "EGG": 0.86,
        "CARROT": 0.70, "WHEAT": 1.50, "MELON": 0.52, "TOMATO": 0.82, "FERTILIZER": 0.50}

_STATE = {}
_ARCHES = ("CONTEST", "MIRROR", "COOP", "PASSIVE")


def _gauss(x, c, s):
    s = max(1e-6, float(s))
    return math.exp(-0.5 * ((float(x) - float(c)) / s) ** 2)


def _tm_step(tm, step, inv, shops):
    try:
        prev = tm.get("prev_inv")
        if prev is not None and tm.get("prev_step") == step - 1:
            drain = _drain_at(step - 1, tm.get("shops") or [])
            ms = tm.get("my_sells") or {}
            mb = tm.get("my_buys") or {}
            od = tm.setdefault("opp_day", {})
            for p in PRODUCTS:
                delta = inv.get(p, MARKET_I0) - prev.get(p, MARKET_I0)
                od[p] = od.get(p, 0.0) + delta + drain.get(p, 0.0) - ms.get(p, 0.0) + mb.get(p, 0.0)
        if step % 24 == 0 and step > 0:
            tm.setdefault("opp_daily", {})[step // 24 - 1] = dict(tm.get("opp_day") or {})
            tm["opp_day"] = {}
        tm["prev_inv"] = {p: inv.get(p, MARKET_I0) for p in PRODUCTS}
        tm["prev_step"] = step
        tm["my_sells"] = {}
        tm["my_buys"] = {}
    except Exception:
        pass


def _tm_orders(tm, orders):
    try:
        ms = tm.setdefault("my_sells", {})
        mb = tm.setdefault("my_buys", {})
        for o in orders or []:
            if not isinstance(o, (list, tuple)) or len(o) < 3:
                continue
            op, item, n = o[0], o[1], o[2]
            if op == "SELL" and item in PRODUCTS and _is_num(n):
                ms[item] = ms.get(item, 0.0) + int(n)
            elif op == "BUY_PRODUCT" and item in PRODUCTS and _is_num(n):
                mb[item] = mb.get(item, 0.0) + int(n)
    except Exception:
        pass


def _bayes_step(tm, day, opp_farm, my_herd, my_money):
    try:
        tm["mode"] = tm.get("mode", "CONTEST")
        if day < 8:
            tm["mode"] = "CONTEST"
            return
        oc = og = osp = 0
        opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
        if opp_tiles:
            for row in opp_tiles:
                for t in row:
                    if isinstance(t, dict) and "animal" in t:
                        a = t.get("animal")
                        if a == "COW":
                            oc += 1
                        elif a == "GOOSE":
                            og += 1
                        elif a == "SHEEP":
                            osp += 1
        opp_money = float(_g(opp_farm, "money", 0) or 0) if opp_farm else 0.0
        mc, mg, msp = my_herd
        money_ratio = (opp_money / my_money) if my_money > 300.0 else 1.0

        # tight bit-identical twin signature (true self-play only)
        sig = (_gauss(oc - mc, 0.0, 0.8)
               * _gauss(og - mg, 0.0, 1.0)
               * _gauss(osp - msp, 0.0, 0.8)
               * _gauss(money_ratio, 1.0, 0.07)
               * _gauss(len(opp_tiles or []) and 1.0 or 0.0, 1.0, 0.05))
        like_m = max(0.005, min(0.98, sig))
        like_c = max(0.05, 1.0 - 0.75 * like_m)

        pm = tm.get("pm", 0.08)
        pm = (pm ** 0.8) * (like_m / (like_m + like_c))
        pm = min(0.99, max(0.005, pm))
        tm["pm"] = pm

        cur = tm.get("mode", "CONTEST")
        if cur == "MIRROR":
            if pm < 0.35:
                tm["mode"] = "CONTEST"
        else:
            if pm > 0.70:
                tm["mode"] = "MIRROR"
    except Exception:
        pass


def _g(o, k, d=None):
    try:
        if isinstance(o, dict):
            return o.get(k, d)
        return getattr(o, k, d)
    except Exception:
        return d


def _mk(tier, x, y, op, **kw):
    d = {"tier": tier, "x": x, "y": y, "op": op}
    d.update(kw)
    return d


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _step_toward(fx, fy, tx, ty):
    if fx < tx:
        return "EAST"
    if fx > tx:
        return "WEST"
    if fy < ty:
        return "SOUTH"
    if fy > ty:
        return "NORTH"
    return None


def _shed_tiles(board):
    h = board // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]


def _nearest_shed_tile(x, y, board):
    return min(_shed_tiles(board), key=lambda t: abs(t[0] - x) + abs(t[1] - y))


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _shape(func, x, T=None):
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "log10":
        return math.log10(1.0 + x)
    if func == "hinge":
        if not T or T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _price(item, inventory):
    p = MARKET_PARAMS[item]
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        pr = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        pr = base - amp * _shape(f, inventory - I0, T)
    return max(1, int(round(pr)))


def _sell_count(item, n_avail, inv, thresh):
    k = 0
    while k < n_avail:
        if _price(item, inv + k) < thresh:
            break
        k += 1
    return k


_ABOVE_CACHE = {}


def _above_headroom(item, frac):
    key = (item, frac)
    if key not in _ABOVE_CACHE:
        thresh = frac * MARKET_PARAMS[item]["base"]
        k = 0
        while k < 20000 and _price(item, MARKET_I0 + k) >= thresh:
            k += 1
        _ABOVE_CACHE[key] = k
    return _ABOVE_CACHE[key]


def _shop_vector(shops):
    v = {it: 0.0 for it in PRODUCTS}
    for s in shops:
        prods = SHOPS.get(s, [])
        m = 2 if len(prods) == 1 else 1
        for it in prods:
            v[it] += m
    return v


def _avg_shop_vector():
    v = {it: 0.0 for it in PRODUCTS}
    ks = list(SHOPS)
    for s in ks:
        sv = _shop_vector([s])
        for it in PRODUCTS:
            v[it] += sv[it] / len(ks)
    return v


AVG_SHOP_VEC = _avg_shop_vector()


def _drain_at(step, shops):
    d = {p: 0.0 for p in PRODUCTS}
    if step % 4 == 0 and shops:
        sv = _shop_vector(shops)
        for p in PRODUCTS:
            d[p] += sv[p]
    if step % 24 == 0:
        for p in TOWN_CENTER_PRODUCTS:
            d[p] += 1.0
    return d


def _forward_absorb(day, hour, shops):
    step = day * TURN_PER_DAY + hour
    cur = _shop_vector(shops)
    n = len(shops)
    unlock_steps = []
    for d in range(day + 1, 30):
        if d % 3 == 0 and n < MAX_SHOP_INSTANCES:
            unlock_steps.append(d * TURN_PER_DAY)
            n += 1
    tot = {it: 0.0 for it in PRODUCTS}
    for t in range(step, EPISODE_STEPS):
        if t % 4 == 0:
            k = 0
            for u in unlock_steps:
                if t >= u:
                    k += 1
            for it in PRODUCTS:
                tot[it] += cur[it] + AVG_SHOP_VEC[it] * k
        if t % 24 == 0:
            for it in TOWN_CENTER_PRODUCTS:
                tot[it] += 1
    return tot


def _pipeline(tiles, shed):
    pipe = {it: 0.0 for it in PRODUCTS}
    if not tiles:
        return pipe
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT":
                crop = t.get("crop")
                if crop in YIELD_PER_CYCLE:
                    pipe[crop] += YIELD_PER_CYCLE[crop]
            elif "animal" in t:
                an = t.get("animal")
                if an in ANIMALS:
                    pipe[ANIMALS[an]["product"]] += 28.0
    if shed:
        for it in PRODUCTS:
            v = shed.get(it, 0)
            if _is_num(v):
                pipe[it] += v
    return pipe


def _struct_reserve(need, unit_cost, money):
    # Trụ 2 (R157): BUILD_COOP/BUILD_PASTURE MIỄN PHÍ trong engine (chỉ tốn
    # labor) — money-gate 300/500 cũ là tự đặt, chặn vòng đàn sát shed d0.
    # Cap theo need thuần; chỉ giữ floor mềm 1 để không đùng khi phá sản.
    if need <= 0:
        return 0
    return min(need, 3 if money >= 500 else (2 if money >= 250 else 1))



# ---- v6 ΔF: E8-lite port (v5's drain-aware endgame hold) ----

def _pipe_rest(tiles, day):
    """v6 ΔF (port nguyên văn v5._pipe_rest — RULES R71): nguồn cung CHỜ THU
    còn lại trước hết mùa theo item — gate thanh lý d22-27."""
    out = {it: 0.0 for it in PRODUCTS}
    try:
        if not tiles:
            return out
        for row in tiles:
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get("kind") == "PLANT":
                    crop = t.get("crop")
                    cd = CROPS.get(crop)
                    if not cd:
                        continue
                    age = day - t.get("planted_day", day)
                    yu = float(t.get("yield_units", 0) or 0)
                    if cd["ongoing"]:
                        mls = t.get("max_lifespan_step", -1)
                        days_left = max(0, (mls - day * 24) // 24 + 1) if mls >= 0 else 0
                        out[crop] += yu + 1.3 * max(0, days_left)
                    else:
                        out[crop] += yu if age > cd["max_yield_day"] else max(yu, 2.0)
                elif "animal" in t:
                    ad = ANIMALS.get(t.get("animal"))
                    if not ad:
                        continue
                    yu = float(t.get("yield_units", 0) or 0)
                    first = ad["first_yield_day"]
                    itv = max(1, ad["interval"])
                    age = day - t.get("placed_day", day)
                    n_prod = 0
                    a = max(age, first)
                    while a <= 28:
                        if (a - first) % itv == 0:
                            n_prod += 1
                        a += 1
                    out[ad["product"]] += yu + min(2.0 * ad["max_held"], 1.3 * n_prod)
    except Exception:
        pass
    return out


def _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp_farm, money, tm=None):
    absorb = _forward_absorb(day, 0, shops)
    my_pipe = _pipeline(tiles, shed)
    opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
    opp_pipe = _pipeline(opp_tiles, None)

    def room(it):
        deficit = max(0.0, MARKET_I0 - inv.get(it, MARKET_I0))
        r = deficit + absorb.get(it, 0) + _above_headroom(it, 0.78)
        return r - my_pipe.get(it, 0) - 0.85 * opp_pipe.get(it, 0)

    # ΔP3: giá-biên trung bình của `units` unit sắp đổ vào kênh `it`, quy về
    # lần base. proj = tồn kho chiếu theo mid-window (inv + pipeline 2 bên −
    # phần drain tới anchor). Đây là kernel P3: quyết định theo đường cầu
    # (Cournot exact), KHÔNG theo constant/idol.
    def _marg(it, units, anchor_day):
        try:
            cur = float(inv.get(it, MARKET_I0) or MARKET_I0)
            total_abs = float(absorb.get(it, 0.0) or 0.0)
            horizon = max(1, 29 - day)
            days_to = max(1, min(28, anchor_day) - day)
            fut_drain = total_abs * min(1.0, days_to / float(horizon))
            proj = (cur + float(my_pipe.get(it, 0.0) or 0.0)
                    + 0.85 * float(opp_pipe.get(it, 0.0) or 0.0) - fut_drain)
            s = 0.0
            for k in range(1, int(units) + 1):
                s += _price(it, max(0.0, proj + k))
            return (s / max(1, int(units))) / float(MARKET_PARAMS[it]["base"])
        except Exception:
            return 1.0

    coops = pastures = wheat_standing = 0
    animals_now = 0
    standing = {c: 0 for c in CROPS}
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                k = t.get("kind")
                if k == "COOP":
                    coops += 1
                elif k == "PASTURE":
                    pastures += 1
                if "animal" in t:
                    animals_now += 1
                if k == "PLANT":
                    cc = t.get("crop")
                    if cc in standing:
                        standing[cc] += 1
                    if cc == "WHEAT":
                        wheat_standing += 1
    shed_geese = shed.get("GOOSE", 0) if shed and _is_num(shed.get("GOOSE", 0)) else 0
    shed_cows = shed.get("COW", 0) if shed and _is_num(shed.get("COW", 0)) else 0
    shed_sheep = shed.get("SHEEP", 0) if shed and _is_num(shed.get("SHEEP", 0)) else 0

    opp_counts = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    if opp_tiles:
        for row in opp_tiles:
            for t in row:
                if isinstance(t, dict) and "animal" in t:
                    a = t.get("animal")
                    if a in opp_counts:
                        opp_counts[a] += 1

    mode = (tm or {}).get("mode", "CONTEST")
    milk_room = (absorb.get("MILK", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("MILK", MARKET_I0))
                 - 30.0 * opp_counts["COW"] - 40.0)
    wool_room = (absorb.get("WOOL", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("WOOL", MARKET_I0))
                 - 28.0 * opp_counts["SHEEP"] - 20.0)
    egg_room = (absorb.get("EGG", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("EGG", MARKET_I0))
                - 46.0 * opp_counts["GOOSE"] - 20.0)
    # KAIN-8: herd = v5's adaptive formula + shop floors, capital-capped
    # early, labor-safe total (13), delivery 2/day to d14 + price windows.
    # (v6 v5: BỎ geese-4-early — va chạm ngỗng-sớm với ngỗng-sớm của v5 trên
    # 129/131/138 (cả hai phóng 7 → kênh trứng sập, v6 −$10.6k). Giữ công thức
    # kain16; floor-7 ΔB chỉ bật SAU tiền dưa — lệch pha với đàn ngỗng v5)
    goose_target = max(3, min(8, int(egg_room // 46)))
    # S1 EGG-FORTRESS (R102): floor hạ 7→5 (R168: đàn 13 + máy 20 = tự cấp;
    # ngỗng 7 + bò 6 + cừu 4 = floor 17 chặn cap — đàn thực tế phình 19)
    if opp_counts["GOOSE"] <= 6 and day >= 4:
        goose_target = max(goose_target, 5)
    cow_target = max(2, min(8, int(milk_room // 30)))
    # ΔB MILK-COMMIT: kênh sữa sâu nhất game — KHÔNG nhượng (first-mover:
    # v6 commit 9 bò trước thì ta mất $16.7k; floor 6 khi giá còn khỏe)
    # R180d (Vòng 48): floor-6 chỉ khi đối thủ ≤6 bò — đo s100: trajectory
    # đưa v8 tới 6 bò từ d10 trong lúc v7 đang giữ 9 → CẢ HAI tràn sữa,
    # giá $297→$85 (v7 milk −$23k, v8 −$18k). Cap money cũ (1+money//900)
    # vô tình giữ v8 ngoài chiến — trajectory bỏ được valve đó thì valve
    # phải đến từ opp_counts.
    if 4 <= day <= 19:
        try:
            if float(prices.get("MILK", 0) or 0) >= 0.95 * MARKET_PARAMS["MILK"]["base"] \
                    and opp_counts.get("COW", 0) <= 6 \
                    and float(inv.get("MILK", MARKET_I0) or 0) <= MARKET_I0 + 5:
                # R180d phụ: inv > I0+n = thị trường sữa ĐÃ TRÀN (đo s100:
                # shop-draw chỉ còn 2 milk-shop — inventory +53 trên I0, giá
                # $297→$61; v8 vẫn giữ 6 bò = đốt vốn vào kênh chết)
                cow_target = max(cow_target, 6)
        except Exception:
            pass
    sheep_target = max(3, min(6, int(wool_room // 30)))
    try:
        if mode != "MIRROR":
            milk_shops = sum(1 for s in (shops or [])
                             if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
            yarn_n = sum(1 for s in (shops or []) if s == "YARN_STORE")
            if milk_shops >= 2 and 4 <= day <= 19 and opp_counts.get("COW", 0) <= 6 \
                    and float(inv.get("MILK", MARKET_I0) or 0) <= MARKET_I0 + 5:
                _dm = float(prices.get("MILK", 0) or 0) >= 0.95 * MARKET_PARAMS["MILK"]["base"]
                cow_target = max(cow_target,
                                 min(6 if _dm else 5, (2 if _dm else 2) + milk_shops))
            if yarn_n >= 1 and 4 <= day <= 18:
                _dw = float(prices.get("WOOL", 0) or 0) >= 0.95 * MARKET_PARAMS["WOOL"]["base"]
                sheep_target = max(sheep_target,
                                   min(5 if _dw else 4, (2 if _dw else 1) + yarn_n))
    except Exception:
        pass
    if day <= 10:
        # R180 (Vòng 48): ramp theo TRAJECTORY — cap cũ theo money
        # (1 + money//900) đóng băng bò ở 1-2 suốt d1-7 khi vốn mỏng → toàn bộ
        # đàn dồn burst d8-18. Top-3 drip 0.5-1 con/2 ngày d4-18 (AD d0-10 =
        # 77 vs 41 của v8): bò d0 = 22 ngày sản xuất, bò d14 = 8. Trajectory
        # cap theo NGÀY — budget vẫn do cash_floor (250+land_reserve) kìm.
        # R191 (Vòng 50): cừu 1+day//4 → 1+day//3 — god-ledger 4 trận thua:
        # v6 giữ 6 cừu (WOOL $19.7-24.7k) vs v8 đứng 4 (WOOL $5.6-18.3k);
        # sheep-AD top-3 = 71. Trajectory d15 = 6 (trước: 4).
        cow_target = min(cow_target, 2 + day // 2)
        sheep_target = min(sheep_target, 1 + day // 3)
    _herd_cap = 13 if day >= 3 else 15  # R168: đàn 13 = top-3 parity (đàn 19 + máy chết = mua 610u wheat $31k net -$8k; top-3: đàn 13 + máy 20 = net +$10k + lao động dư tưới)
    tot = cow_target + sheep_target + goose_target
    if tot > _herd_cap:
        # autopsy 146 + R168: floors 2/5/5 — cho phép cap 13 hạ THẬT (floor cũ
        # 4+6+7=17 chặn cap 14 → đàn thực 19)
        # R191 (Vòng 50): đổi thứ tự cắt ngỗng→bò→cừu (cũ cừu→bò→ngỗng):
        # WOOL $200/u là kênh động vật đắt nhất — v6 giữ 6 cừu thắng
        # $6.4-6.8k WOOL ở 2 trận thua đậm; slot 13-14 phải về cừu trước.
        over = tot - _herd_cap
        goose_target = max(4, goose_target - over)
        tot = cow_target + sheep_target + goose_target
        if tot > _herd_cap:
            cow_target = max(4, cow_target - (tot - _herd_cap))
            tot = cow_target + sheep_target + goose_target
            if tot > _herd_cap:
                sheep_target = max(3, sheep_target - (tot - _herd_cap))
    # Trụ 1 (R156): ĐÀN TỪ D0 — top-3 mua $1.700-2.400 ngay d0 (SpaTaro
    # 2C+2S, UMG 5C+1S, Otter 2S+2G+1C). Starter $1.100 = 2 bò + 1 ngỗng
    # giữ ≥$1.6k cho hạt melon-wave + wheat/carrot (R147 domino: không
    # được hút vốn hạt). d1-4 ramp bằng dòng FERT (~$285/ngày từ 3 con).
    # Cấu trúc đích giữ nguyên room-based + shop-draw phía trên.
    # R188 (Vòng 50): MELON-14 là kênh #1 gap vs v6 (god-ledger 4 trận thua:
    # v6 d0 mua 14 hạt melon + 0 thú, bán $11.8-18.5k ngay d11; v8 8 hạt
    # + $1.600 thú → chỉ $1.6-6.7k). Starter còn đúng 1 cừu + 1 ngỗng
    # ($800) — giữ sheep-AD d0 (R179) nhưng trả $800 = 10 hạt melon;
    # bò vào lại từ d2 qua trajectory R180 (v6: thú đầu d7 vẫn đạt 13 con
    # d15 bằng tiền melon).
    if day == 0:
        # R188b (Vòng 50b): 1 bò + 1 cừu + 1 ngỗng ($1.200, 3 ô) — giữ
        # milk-AD (battery 50a: cắt sạch bò d0 mất MILK −$22k ở game
        # 5-milk-shop s100) + sheep-AD d0 (R179); 3 ô trả cho 5 hạt melon.
        cow_target = min(cow_target, 1 if money >= 1600 else 0)
        goose_target = min(goose_target, 1)
        sheep_target = min(sheep_target, 1 if money >= 800 else 0)
    elif day <= 2:
        cow_target = min(cow_target, 3)
        goose_target = min(goose_target, 3)
        sheep_target = min(sheep_target, 2 if money >= 2200 else (1 if money >= 1600 else 0))
    elif day <= 4:
        cow_target = min(cow_target, 4)
        goose_target = min(goose_target, 4)
        sheep_target = min(sheep_target, 2 if money >= 1200 else 1)
    owned_total = animals_now + shed_geese + shed_cows + shed_sheep
    if owned_total >= ANIMAL_CAP:
        goose_target = min(goose_target, animals_now + shed_geese)
        cow_target = min(cow_target, sum(1 for row in tiles for t in row
                                         if isinstance(t, dict) and t.get("animal") == "COW") + shed_cows)
        sheep_target = min(sheep_target, sum(1 for row in tiles for t in row
                                             if isinstance(t, dict) and t.get("animal") == "SHEEP") + shed_sheep)

    coop_need = _struct_reserve(goose_target + shed_geese - coops, 300, money)
    past_need = _struct_reserve(cow_target + shed_cows + sheep_target + shed_sheep - pastures, 500, money)
    if day <= 2:
        coop_need = min(coop_need, 3)
        past_need = min(past_need, 3)

    board = len(tiles)
    # Trụ A (R167): ĐÀN MỘT KHỐI LIỀN KỀ — top-3 đặt coop/pasture thành khối
    # 4-liên-thông ôm shed (big_share 0.79-0.91, adj 91%); v8 cũ sort từng ô
    # theo khoảng cách shed → đàn rải 5.67 cụm (big_share 0.62, d̄shed 3.19).
    # Fix: mọc khối BFS — mỗi ô reserved MỚI phải kề ≥1 ô đàn sẵn có (hoặc
    # hạt = ô trống gần shed nhất nếu chưa có đàn). Thực vật bao quanh khối.
    _shed_xy = _shed_tiles(board)
    empties = []
    structs = set()
    for y in range(board):
        for x in range(board):
            t = tiles[y][x]
            if t is None:
                empties.append((x, y))
            elif isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"):
                structs.add((x, y))

    def _dshed(c):
        return min(abs(c[0] - sx) + abs(c[1] - sy) for sx, sy in _shed_xy)

    n_struct_want = coop_need + past_need
    block = []
    if structs:
        grown = set(structs)
    else:
        if not empties:
            grown = set()
        else:
            seed = min(empties, key=lambda c: (_dshed(c), c))
            block.append(seed)
            grown = {seed}
    while len(block) < n_struct_want:
        frontier = set()
        for (x, y) in grown:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy)
                if (0 <= q[0] < board and 0 <= q[1] < board
                        and tiles[q[1]][q[0]] is None and q not in grown
                        and q not in block):
                    frontier.add(q)
        if not frontier:
            break
        pick = min(frontier, key=lambda c: (_dshed(c), c))
        block.append(pick)
        grown.add(pick)
    reserved = []
    for i, (x, y) in enumerate(block):
        op = "BUILD_COOP" if i < coop_need else "BUILD_PASTURE"
        reserved.append((x, y, op))
    block_xy = {(x, y) for (x, y, _) in reserved}
    plantable = [c for c in empties if c not in block_xy]

    feed_demand = (animals_now + shed_geese + shed_cows + shed_sheep
                   + goose_target + cow_target + sheep_target) * max(0, 29 - day)

    quotas = {}
    # KAIN-2 "WAVE COLLIDER": bigger + earlier melon (cycle 11: d2 plants
    # harvest d13 — a full 6 days before v5's Wave-E d19 wave) to bank the
    # premium BEFORE the collision, while the visible pipeline pressures
    # v5's room() into yielding.
    if day <= 1:
        quotas["MELON"] = 8
    elif 2 <= day <= 7:
        quotas["MELON"] = 14
    elif 8 <= day <= 14:
        # ΔP3: thang giá-bên thay binary room-gate — 14/10/7 theo marg
        m_m = _marg("MELON", 60, day + 13)
        if room("MELON") > -50 and m_m >= 0.58:
            quotas["MELON"] = 14
        elif m_m >= 0.55:
            quotas["MELON"] = 10
        else:
            quotas["MELON"] = 7
        # Trụ-fix (R144): melon kênh 0-drain — top-3 CẢ HAI cùng bán
        # 66-90u; không nhượng vì pipeline đối thủ khi mình đứng < 10
        if standing.get("MELON", 0) < 10 and m_m >= 0.52:
            quotas["MELON"] = max(quotas["MELON"], 12)
    elif 15 <= day <= 16:
        # S4 LATE-MELON + R169: top-3 trồng lại melon d16-21 (đứng 4.5 ô TB
        # mùa, bán 82u@$186) — nới marg 0.78→0.66, quota 6→8
        if _marg("MELON", 36, day + 13) >= 0.66:
            quotas["MELON"] = 8
    elif 17 <= day <= 21:
        # ΔE MELON-LATE-2 + R169: giá melon $110-122 (sau dump v6) vẫn lãi
        # ~$610/ô (6u×$115 − $80 hạt − nước) — chín d27-30, thu d27-29;
        # nới 0.70→0.58 + mở cửa sổ tới d21 (top-3 wave-2 kéo dài)
        if _marg("MELON", 36, day + 13) >= 0.58:
            quotas["MELON"] = 6
    if 2 <= day <= 16:
        quotas["TOMATO"] = 0
    elif 17 <= day <= 19:
        # ΔC TOMATO-CHANNEL: kênh 0 đối thủ — giá d26-29 $113-155.
        # Trồng d17: 4 event d26-29 = 4u×~$130 = $520/ô từ hạt $50;
        # d18: 3 event; d19: 3 event (event cuối end-d29 không thu được).
        # Nước MỖI NGÀY (interval 1, bỏ 2 ngày = chết) — tier water-crit giữ.
        # v2: hạ quota 10/8/6 -> 8/6/4 (132: tomato 10 hạt mua mà 0 trồng —
        # lao động bão hòa; số lượng nhỏ vẫn bắt kênh giá)
        quotas["TOMATO"] = 8 if day == 17 else (6 if day == 18 else 4)
    if 5 <= day <= 13:
        s_room = room("STRAWBERRY")
        # (v6 v4: REVERT ΔA straw-ramp — battery v3 33/40 vs kain16 38/40:
        # pipeline dâu 30-từ-d5 là ÁP LỰC làm v5 room() nhượng kênh (R94/R96
        # market-share yield); ramp theo v5 = v5 lấy lại $1.9k. Vốn đàn d5-12
        # giờ đến từ ngỗng-4-sớm ΔB (egg+$fert từ d4) thay vì cắt dâu)
        # v9.1: kernel STACK-SWEEP đã đồng bộ walk/op 1,3 (top-3 mức 1,0-1,5)
        # → dư địa nâng standing; 24 là mũ của kernel cũ 62%-MOVE (s306)
        want_straw = 28
        # KAIN-10: v5's minimax + scarcity straw escalation — don't subtract
        # the opponent pipeline when the market is deep enough for both.
        try:
            spx = float(prices.get("STRAWBERRY", 0) or 0)
            sinv = float(inv.get("STRAWBERRY", MARKET_I0) or MARKET_I0)
            straw_shops_n = sum(1 for s in (shops or [])
                                if "STRAWBERRY" in SHOPS.get(s, ()))
        except Exception:
            spx, sinv, straw_shops_n = 0.0, MARKET_I0, 0
        if (spx >= 1.05 * MARKET_PARAMS["STRAWBERRY"]["base"] and straw_shops_n >= 2
                and mode != "MIRROR" and day <= 13):
            s_room = max(s_room, absorb.get("STRAWBERRY", 0.0)
                         - my_pipe.get("STRAWBERRY", 0.0))
        if spx >= 1.25 * MARKET_PARAMS["STRAWBERRY"]["base"] and sinv <= MARKET_I0:
            s_room = max(s_room, want_straw * 4 + 40)
        # S3 STRAW-COMMIT (R101/R105): giá-bên còn khỏe → KHÔNG hiến kênh
        # dù pipeline đối thủ lớn (chỉnh theo đường cầu, không theo pipeline)
        if _marg("STRAWBERRY", 110, min(28, day + 14)) >= 0.98:
            s_room = max(s_room, 120)
        # Trụ 3-fix (R36-mở-rộng): kênh dâu SÂU — trong cửa sổ sóng chính,
        # khi mình đứng < 14 ô thì KHÔNG nhượng kênh vì pipeline đối thủ
        # (trace s105: base trồng dâu 25 trước → room() tự đầu hàng → NEW
        # đứng 10-12 ô cả d14-19 → thua kênh $12-20k).
        # (thử cap 16 khi đối thủ dâu 24: 11/50 vs v6 — rút lui làm v6 độc
        # quyền premium → TỆ HƠN; reverted)
        if day <= 13 and standing.get("STRAWBERRY", 0) < 14:
            s_room = max(s_room, want_straw * 4 + 40)
        quotas["STRAWBERRY"] = want_straw if s_room > 100 else max(0, min(want_straw, int(s_room // 4)))
    elif 14 <= day <= 15:
        # S3b LATE-STRAW + R163-fix: standing-target TUYỆT ĐỐI 18 (cũ
        # max(12, 18−st) bị trừ đôi: st=16 → quota 12 → need 0 — dâu trượt
        # mục tiêu replant sau mỗi đợt chết)
        quotas["STRAWBERRY"] = 20
    elif 16 <= day <= 19:
        # Δ5 LATE-STRAW-2 + R163-fix: đứng đích 14 (d16-17) / 12 (d18-19)
        quotas["STRAWBERRY"] = 16 if day <= 17 else 14
    elif 20 <= day <= 26:
        # R176 LATE-STRAW-3: top-3 replant dâu tới d26 (đứng 24.8 phẳng cả mùa,
        # bán 254u); v8 cũ không có quota d20+ → đứng rơi 18→12 cuối mùa.
        # Standing-target tuyệt đối: 14 (d20-23) / 10 (d24-26) — need =
        # target − standing tự replant mỗi lần cây chết.
        quotas["STRAWBERRY"] = 16 if day <= 23 else 12
    if day <= 26:
        if day <= 4:
            quotas["WHEAT"] = 17
        else:
            # Trụ 5-fix (R159) + R169/R170: WHEAT STANDING-TARGET THẬT nhìn từ
            # đủ mọi layer. Đứng đích = max(16, đàn×1.0+3) cap 20 — máy là
            # NHÀ MÁY THỨC ĂN (v8 cũ đứng 1 ô d15 → mua 610u $31k; top-3 đứng
            # 20 ô cả mùa = feed tự cấp + bán dư 574u net +$10k).
            wt_stand = standing.get("WHEAT", 0)
            _wt_target = max(16, int((animals_now + shed_geese + shed_cows + shed_sheep
                                      + goose_target + cow_target + sheep_target) * 1.0) + 3)
            quotas["WHEAT"] = min(20, _wt_target)
    if day <= 26:
        if day <= 2:
            quotas["CARROT"] = 12
        else:
            # ΔP3+ΔD: thang giá-bên carrot (v6: binary room-gate 8/6/4/0);
            # ngưỡng mềm 0.88/0.76/0.62 + cửa sổ mở tới d26 (trồng d26
            # chín d28-29: 3u×$56-66) — giá carrot tăng dần $35→$72 endgame
            c_m = _marg("CARROT", 24, min(28, day + 5))
            # v8 Δ7: 8/6/4 -> 12/10/8 — top-3 đứng 10-15 ô carrot d24-29
            # (UMG $4.074, Otter $7.121 doanh thu cuối mùa — R139 danh mục
            # đứng cuối là thứ phân định 2 trận top)
            if c_m >= 0.88:
                quotas["CARROT"] = 12
            elif c_m >= 0.76:
                quotas["CARROT"] = 10
            elif c_m >= 0.62:
                quotas["CARROT"] = 8
            else:
                quotas["CARROT"] = 0
            # R169 (khối lượng > giá): carrot kênh đứng rẻ — top-3 đứng 5.3 ô
            # TB, bán 135u@$44.8; v8 chỉ 11u cả mùa. Standing < 8 → floor 8
            # KHÔNG CỔNG MARG (đo lại: marg≥0.45 chặn gần cả mùa — hạt $20,
            # 3 yield/4 ngày, giá luôn ≥ base khi thị trường không tự dump)
            # R184 (Vòng 48): TẮT floor — đo bat48 (10 seed): carrot bán 0-6u
            # cả mùa dù đứng 7-11 ô (window 2 ngày tier-3 thua_phase-2 →
            # chết lặp) = hạt + 8-10 task nước/ngày lãng phí HOÀN TOÀN,
            # còn cướp phase-2 của melon (6u vs 42-48u baseline). Trả lao
            # động cho melon; carrot chỉ trồng khi marg thật sự đẹp.
            # (floor 8 đã TẮT — không còn dòng quotas["CARROT"] = max(..., 8))
            # v9-K4 (R195-53c, hồi sinh có điều kiện): floor standing 6 —
            # với kernel stack-gap-0, 1 FERTILIZE (gap-0) + 2 nước window
            # = 4u/ô × $45-70; giữ NHỎ (6) để không tái phát R184 (cũ 8).
            if 3 <= day <= 26:
                quotas["CARROT"] = max(quotas.get("CARROT", 0), 8)

    if day <= 1:
        # Trụ 1 + R188b: d0-1 = máy wheat 10 + carrot 2 (đúng opening v6:
        # 10 wheat + 2 carrot + 14 melon) + MELON 14. Tiền: $1.200 thú +
        # $1.120 melon + $100 wheat + $40 carrot = $2.460, buffer $540.
        # 45%-fast-crop CUT đã TẮT ở d0-1 (R188b) — melon-14 giờ CHÍNH là
        # kế hoạch vốn (d11 = $12-18k) và 3 thú cho dòng FERT $285/ngày,
        # không cần 45% wheat như v6 thuần cây.
        quotas["WHEAT"] = 10
        quotas["CARROT"] = 2
        quotas["MELON"] = 14
        quotas.pop("STRAWBERRY", None)

    if day <= 2:
        order = ["WHEAT", "MELON", "TOMATO", "CARROT", "STRAWBERRY"]
    elif 17 <= day <= 19:
        # ΔC: TOMATO đứng đầu — kênh 0 đối thủ, ROI/ô cao nhất endgame
        order = ["TOMATO", "STRAWBERRY", "MELON", "WHEAT", "CARROT"]
    elif feed_demand > 300:
        order = ["WHEAT", "STRAWBERRY", "TOMATO", "MELON", "CARROT"]
    else:
        order = ["MELON", "STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]
    crop_tiles = {}
    remaining = len(plantable)
    for crop in order:
        want = quotas.get(crop, 0)
        if want <= 0:
            continue
        have = standing.get(crop, 0)
        need = max(0, want - have)
        take = min(remaining, need)
        if take > 0:
            crop_tiles[crop] = take
            remaining -= take
        if remaining <= 0:
            break
    # Δ1' FILL-SMART affordability (kain35, tái cấu trúc kain40): d4-13,
    # nq>=2 — hạt dâu/melon không nổi floor thì CẮT BỚT, ô giải phóng
    # TRẢ VỀ `remaining` để fill-law phía dưới chọn cây lấp (không còn
    # redirect mù +8 carrot). Δ9: CHỈ khi nq>=2 (sau NE) — trước khi mua
    # đất phải giữ vốn (kain37 s100: straw-partial $300 d5h0 -> NE không
    # bao giờ mua được -> farm kẹt 25 ô).
    _nq_plan = (len(tiles) * len(tiles) - sum(
        1 for row in tiles for t in row if t == "LOCKED")) // max(1, len(tiles) * len(tiles) // 4)
    if 4 <= day <= 13 and _nq_plan >= 2:
        try:
            _sk = crop_tiles.get("STRAWBERRY", 0)
            _seedable = max(0, int((money - 200) // CROPS["STRAWBERRY"]["seed"]))
            if _sk > _seedable:
                crop_tiles["STRAWBERRY"] = _seedable
                remaining += _sk - _seedable
            _mk = crop_tiles.get("MELON", 0)
            _mseed = max(0, int((money - 300) // CROPS["MELON"]["seed"]))
            if _mk > _mseed:
                crop_tiles["MELON"] = _mseed
                remaining += _mk - _mseed
        except Exception:
            pass
    if remaining > 0 and day <= 21:
        # R190 (Vòng 50): 26 → 21 — fill wheat endgame cướp lao động tưới/
        # thu dâu (xem R190 ở seed-buy); d22+ đất trống để trống còn hơn
        # trồng wheat không kịp chín (đo s118: P10 wheat d24 vô nghĩa,
        # dâu chết d24-27) — ΔB FILL-LAW: mọi ô trống còn lại PHẢI đi làm
        # cứng của kain38. Thứ tự theo thời kỳ:
        #   d4-13 : CARROT tới cap 20 (hạt $20; không phải feed — v6
        #           không arbitrage được) -> WHEAT hết phần còn lại
        #   d14-26: WHEAT TOÀN BỘ còn lại (giá $33-51 tăng đều; v6 hút
        #           150-240u/ngày d11-25 + E8-lite endgame dump $8k/ngày)
        # Valley d6-9: tiền còn $100-260 → wheat $10/ô là cây duy nhất mua
        # nổi (floor $30 flat sau NE; carrot floor $220 chặn) — 12 ô ×
        # $120 → +$1.1k d9-10 tự bơm vốn.
        # Cổng giá carrot: giá-biên 20 unit còn ≥0.62×base mới lấp carrot
        # (tránh tự crash kênh mình — hinge T=450; nghèo < $400 → wheat).
        # ΔG FIX-3+4 (bài học 102 vs 146 — 2 lớp seed muốn carrot ĐỐI NGHỊCH):
        #   102 (engine giàu: dâu đứng 20+ sẵn) — carrot fill 12 ô = $20/act
        #     ROI lao động tệ, hạt cơm giành harvest/care của dâu+sữa → LOSS.
        #   146/103 (engine nghèo: dâu đứng ~0 lúc d10-13) — carrot 20 = mồi
        #     vốn không-subsidy (v6 không mua carrot; wheat fill = nuôi bò v6
        #     R113) → WIN lớn.
        # Giải pháp: cap carrot THEO standing dâu lúc dựng plan — dâu yếu
        # (<12 ô) → carrot 20 (bootstrap); dâu khỏe (≥12) → carrot 8 (né máy).
        _straw_standing = standing.get("STRAWBERRY", 0)
        if _straw_standing < 12:
            _car_cap = 20 if day <= 13 else 12
        else:
            _car_cap = 8 if day <= 19 else 6
        if money < 400:
            _car_cap = 0
        else:
            try:
                if _marg("CARROT", 20, min(28, day + 5)) < 0.62:
                    _car_cap = min(_car_cap, 8)
            except Exception:
                pass
        _c_now = crop_tiles.get("CARROT", 0)
        _c_room = max(0, _car_cap - _c_now)
        if _c_room > 0:
            _fill = min(remaining, _c_room)
            crop_tiles["CARROT"] = _c_now + _fill
            remaining -= _fill
        if remaining > 0:
            crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + remaining
            remaining = 0

    if day <= 1 and plantable:
        # R188b (Vòng 50b): TẮT nhánh CUT của luật 45% fast-crop ở d0-1 —
        # nó sinh ra để bảo đảm dòng tiền cây non, nhưng melon-14 + 3 thú
        # FERT $285/ngày đã là kế hoạch vốn (đo 50a: đứng 11-13 thay vì 14
        # vì 1-2 hạt bị cắt). Chỉ GIỮ nhánh fill-up wheat khi còn ô trống.
        fast = sum(v for c, v in crop_tiles.items() if c in ("WHEAT", "CARROT"))
        if fast < 0.45 * len(plantable):
            need = int(0.45 * len(plantable)) - fast
            if need > 0:
                crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + need

    return {
        "crop_tiles": crop_tiles,
        "reserved": reserved,
        "goose_target": goose_target,
        "cow_target": cow_target,
        "sheep_target": sheep_target,
        "feed_demand": feed_demand,
        "standing": standing,
        "mode": mode,
    }


def _build_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, n_units):
    tasks = []
    stats = {"water_crit": 0, "total": 0}
    board = len(tiles)
    if not board:
        return tasks, stats

    fert_available = (shed.get("FERTILIZER", 0) if shed else 0) + sum(
        (u.get("FERTILIZER", 0) or 0) for u in inventories if isinstance(u, dict))
    wheat_available = (shed.get("WHEAT", 0) if shed else 0) + sum(
        (u.get("WHEAT", 0) or 0) for u in inventories if isinstance(u, dict))
    # v8 Δ4: đếm wheat standing cho PLANT-URG (máy sữa không được chết)
    wheat_standing_n = 0
    standing_carrot_n = 0
    weeds_n = 0
    animals_n = 0
    hungry_n = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "WHEAT":
                wheat_standing_n += 1
            elif isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "CARROT":
                standing_carrot_n += 1
            elif isinstance(t, dict) and t.get("kind") == "WEED":
                weeds_n += 1
            if isinstance(t, dict) and "animal" in t:
                animals_n += 1
                if (t.get("consecutive_unfed", 0) or 0) >= 1 and not t.get("fed_today", False):
                    hungry_n += 1
    feed_crunch = hungry_n > 0 or (animals_n > 0 and wheat_available < animals_n + 3)

    fert_usable = 0
    for row in tiles:
        for t in row:
            if not isinstance(t, dict) or t.get("kind") != "PLANT":
                continue
            crop = t.get("crop")
            if crop not in ("WHEAT", "CARROT"):
                continue
            cd = CROPS[crop]
            age = day - t.get("planted_day", day)
            ws = (cd["max_yield_day"] + 1) // 2
            if ws <= age <= cd["max_yield_day"] and t.get("fertilized_until_day", -1) < day:
                fert_usable += 1
    fert_usable = max(0, fert_usable - fert_available)
    fert_made = 0

    for y in range(board):
        row = tiles[y]
        for x in range(board):
            t = row[x]
            if t is None or t == "LOCKED" or not isinstance(t, dict):
                continue
            kind = t.get("kind")
            if kind == "PLANT":
                crop = t.get("crop")
                cd = CROPS.get(crop)
                if cd is None:
                    continue
                age = day - t.get("planted_day", day)
                yu = t.get("yield_units", 0) or 0
                mls = t.get("max_lifespan_step", -1)
                watered = bool(t.get("watered_today", False))
                if not watered:
                    cu = t.get("consecutive_unwatered", 0) or 0
                    ws = (cd["max_yield_day"] + 1) // 2
                    in_win = (not cd["ongoing"]) and (ws <= age <= cd["max_yield_day"])
                    # v8 Δ1 EVENT-WATER (R151-fix): cây ongoing (dâu interval 2,
                    # tomato interval 1) chỉ cộng yield NGÀY EVENT và chỉ cần
                    # nước mỗi `interval` ngày để sống — tưới ngày thường là
                    # lãng phí tier-0 (autopsy: v7 tưới dâu hằng ngày 18-23 ô,
                    # top-3 chỉ tưới event). Event credit cuối ngày D khi
                    # (D+1-P-first) % interval == 0.
                    # Δ1b CAP-6: chỉ 6 task tưới event tier-0 mỗi giờ (credit
                    # cuối ngày — dàn đều cả ngày), phần còn lại tier 1 —
                    # không để tưới chiếm sạch units đúng buổi SERVICE (v8a
                    # d20: 9 thú bỏ đói vì 14 task tưới tier-0 chồng nhau)
                    if cd["ongoing"]:
                        dsf = (day + 1) - t.get("planted_day", day) - cd["first_yield_day"]
                        prod_n = dsf // cd["interval"] + 1 if dsf >= 0 else 0
                        is_event = dsf >= 0 and dsf % cd["interval"] == 0 \
                            and prod_n <= cd["max_yield"]
                        if is_event:
                            # nước+fert ngày event = +2u thay +1u
                            # R174: cap 6→8/giờ — đàn khối shed (d̄ 1.89) cắt
                            # nửa chuyến service, phase-1 dư sức tưới event đủ
                            if stats.get("water_crit", 0) < 8:
                                tasks.append(_mk(T_WATER_CRIT, x, y, "WATER"))
                                stats["water_crit"] += 1
                            else:
                                tasks.append(_mk(1, x, y, "WATER"))
                        elif cu >= 1 and prod_n <= cd["max_yield"]:
                            # survival mỗi 2 ngày (chưa tới event / lỡ event)
                            # — dâu/tomato non tier 1: 1 task tier-2 trượt =
                            # chết dây chuyền (s306: dâu 24→9→7, mất kênh
                            # $30k cho v6 độc quyền premium d21-28)
                            if crop in ("STRAWBERRY", "TOMATO"):
                                tasks.append(_mk(1, x, y, "WATER"))
                            else:
                                tasks.append(_mk(T_SERVICE, x, y, "WATER"))
                        # sau vách (prod_n > max_yield): không tưới — chỉ thu
                    elif in_win:
                        # Trụ F (Vòng 48 — R183 KẾT LUẬN): 2 lần thử nâng ưu
                        # tiên tưới carrot/melon (tier-0/1/2) đều PHẠM LUẬT
                        # PHA-1 BÃO HÒA: tier-0 ăn cap-8 giết seedling (R172
                        # tái phát, 39 weed); tier-1/2 giết service (milk
                        # −$8k, wool −$5k một mùa). Kernel lao động 62% MOVE
                        # không có dư địa — carrot/melon phải sống bằng tier-3
                        # như cũ; gap −$5.7k carrot / −$6.2k melon belongs
                        # vòng kernel (R151/R164), KHÔNG fix được tại chỗ.
                        # R192 (Vòng 50) — MELON SURVIVAL carve-out: R183 đúng
                        # cho tưới THƯỜNG, nhưng ô melon cu>=1 trong cửa sổ
                        # chín mà trượt thêm HÔM NAY = chết trắng $900-1.500/ô
                        # (god-ledger s132/146/123: 12 ô đứng d0-9 → d10 = 4-5,
                        # melon rev $4-6.4k vs v6 $20-23.6k = gap #1 của các
                        # trận 40-46k). Budget RIÊNG cap 4/h (không giành chỗ
                        # seedling của R172); service không bị đẩy vì số task
                        # = đúng số ô đang chết (0-12, không hằng ngày).
                        if cu >= 1 and crop == "MELON" and stats.get("melon_crit", 0) < 4:
                            tasks.append(_mk(T_WATER_CRIT, x, y, "WATER"))
                            stats["melon_crit"] = stats.get("melon_crit", 0) + 1
                        else:
                            tasks.append(_mk(T_WATER_YIELD, x, y, "WATER"))
                            stats["water_yield"] = stats.get("water_yield", 0) + 1
                    elif cu >= 1:
                        # R172 [E] — CÂY NON CHẾT NGAY EOD ĐẦU TIÊN: engine
                        # _new_plant sinh consecutive_unwatered=1 (ngày trồng
                        # tính là chưa tưới) → không tưới NGÀY TRỒNG = chết
                        # ngay lần refresh đầu (s115: 19 PLANT d11 + 26 WATER
                        # đi nơi khác → 23 weed sáng d12). Hạt non (age 0) =
                        # tier 0 cap 6/h; cây lớn bỏ lỡ hôm qua = tier 2 (cũ 4
                        # — đói → weed 22-47 ô mạn tính).
                        if age <= 0 and stats.get("water_crit", 0) < 6:
                            tasks.append(_mk(T_WATER_CRIT, x, y, "WATER"))
                            stats["water_crit"] = stats.get("water_crit", 0) + 1
                        else:
                            tasks.append(_mk(T_WATER_MAINT, x, y, "WATER"))  # tier 3 — không ngập phase-1
                    # v8 Δ8: BỎ T_WATER_MAINT parity (tưới chẵn lẻ ngày thường
                    # = 0 giá trị yield cho mọi cây — chỉ nuôi cỏ dại khỏi
                    # mọc; survival đã có nhánh cu>=1 ở trên)
                if yu > 0 and age >= cd["first_yield_day"]:
                    urgent = (mls >= 0 and mls - step <= 36) or (crop == "WHEAT" and feed_crunch) \
                        or (crop == "WHEAT" and yu >= 4) \
                        or (cd["ongoing"] and yu >= 3 and day >= 26)
                    if cd["ongoing"]:
                        # ΔG FIX-1 (bài học 102: 22 ô dâu chỉ bán 22u/88u —
                        # thu ở yu>=4 quá muộn, yield ngồi trên ô tới hết game;
                        # yu>=3 harvest sớm hơn 2 ngày/ô, dàn trải đều lao động)
                        ready = yu >= 3 or (mls >= 0 and mls - step <= 6) or day >= 27
                        if not ready and yu >= 3 and mls >= 0 and mls - step <= 12:
                            ready = True
                    else:
                        ready = yu >= cd["max_yield"] or age >= cd["max_yield_day"] + 1 or (
                            age >= cd["max_yield_day"] and watered)
                        # R185 (Vòng 48) — MELON SALVAGE: đo bat48, melon
                        # tưới cách nhật (phase-2 đói) → yu 4-5 lúc hết
                        # window, cây chết tuổi 13-14 = 0u (6u cả mùa vs 42-48u
                        # baseline). Thu TẠI age 11 bất kể yu: 4-5u×$150-190
                        # cứu được thay vì chết trắng thành weed.
                        # [R193 THỬ VÀ LOẠI ở Vòng 50: age 10 + cargo-rush
                        # battery 15/20 $64.9k < R192 15/20 $66.5k — thu sớm
                        # mất unit cuối của ô fertilized, rush giữa ngày
                        # tốn lao động; s117 −$16.6k. Giữ age 11.]
                        if crop == "MELON" and age >= cd["max_yield_day"] - 1:
                            ready = True
                    if ready:
                        tasks.append(_mk(T_HARVEST_URG if urgent else T_HARVEST, x, y, "HARVEST"))
            elif "animal" in t:
                ad = ANIMALS.get(t.get("animal"))
                if ad is None:
                    continue
                starve = (t.get("consecutive_unfed", 0) or 0) >= 1
                need_feed = (not t.get("fed_today", False)) and wheat_available > 0
                need_care = not t.get("cared_today", False)
                need_fert = bool(t.get("fertilizer_available", False))
                if day <= 28 and (need_feed or need_care or need_fert):
                    # v8 Δ6 GOOSE-PRIORITY (revert Δ6b service-all-tier-1:
                    # 19 task tier-1 nuốt hết phase-1, harvest/PLANT chết đói —
                    # v8b straw chỉ bán 23u): ngỗng tier 1, bò/cừu tier 2
                    _sv_tier = T_SERVICE_URG if starve else (
                        1 if t.get("animal") == "GOOSE" else T_SERVICE)
                    # Trụ 4 (R143): con đang có sản lượng chờ (event sắp
                    # tính) → tier 1 — care-bonus +1 chỉ ăn khi feed+care
                    # đúng hôm đó; bò/cừu tier 2 trượt feed = mất 50% milk/
                    # wool (s203: NEW milk 54u vs base 95u cùng cỡ đàn)
                    if (_sv_tier == T_SERVICE
                            and (t.get("yield_units", 0) or 0) >= 1):
                        _sv_tier = 1
                    tasks.append(_mk(_sv_tier, x, y, "SERVICE",
                                     want_wheat=need_feed, feed=need_feed))
                yu = t.get("yield_units", 0) or 0
                if yu >= ad["max_held"] - 1:
                    tasks.append(_mk(T_HARVEST_URG, x, y, "HARVEST"))
                elif yu >= 2 or (yu > 0 and day >= 27):
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, "HARVEST"))
            elif kind == "WEED":
                # R173 [E] — WEED > 6 = XOẮN ỐC ĐẤT CHẾT: cây chết thành weed,
                # refill chỉ trồng được trên ô None (weed phải DIG) → máy
                # wheat chết dây chuyền khi weed phình (s115: 30-47 ô d21+).
                # DIG tier 3 khi weed > 6 (cũ 4 — đói; tier 2 = ngập phase-1
                # starving service — đo lùi $8.6k)
                tasks.append(_mk(3 if weeds_n > 6 else T_DIG, x, y, "DIG"))
            elif kind in ("COOP", "PASTURE"):
                pass

    if hour <= 20:
        built = 0
        for (x, y, bop) in plan.get("reserved", []):
            if built >= 2:
                break
            if 0 <= y < board and 0 <= x < board and tiles[y][x] is None:
                animal_waiting = ((shed.get("GOOSE", 0) or 0) + (shed.get("COW", 0) or 0)
                                  + (shed.get("SHEEP", 0) or 0)) > 0
                # Trụ 2: d0-3 BUILD luôn urg — vòng đàn phải đứng trước
                # planting claim ô trung tâm (top-3 BUILD d0-1)
                _urg2 = animal_waiting or day <= 3
                tasks.append(_mk(T_BUILD_URG if _urg2 else T_BUILD, x, y, bop))
                built += 1

    if shed:
        for animal in ("GOOSE", "COW", "SHEEP"):
            n_pending = shed.get(animal, 0) or 0
            if n_pending <= 0:
                continue
            struct_kind = ANIMALS[animal]["structure"]
            placed = 0
            limit = min(n_pending, 3)
            for y in range(board):
                for x in range(board):
                    if placed >= limit:
                        break
                    t = tiles[y][x]
                    if isinstance(t, dict) and t.get("kind") == struct_kind and "animal" not in t:
                        tasks.append(_mk(T_DELIVER, x, y, "DELIVER", item=animal))
                        placed += 1
                if placed >= limit:
                    break

    planted = _STATE.get(("planted", day)) or {}
    budget = []
    for crop, cap in plan.get("crop_tiles", {}).items():
        remain = cap - planted.get(crop, 0)
        have = (seeds.get(crop, 0) or 0) if seeds else 0
        if remain > 0 and have > 0:
            budget.append((crop, min(remain, have)))
    reserved_xy = {(x, y) for (x, y, _) in plan.get("reserved", [])}
    if budget and hour <= 19:
        empties = []
        for y in range(board):
            for x in range(board):
                if tiles[y][x] is None and (x, y) not in reserved_xy:
                    empties.append((x, y))
        empties.sort(key=lambda c: abs(c[0] - board // 2) + abs(c[1] - board // 2))
        flat = []
        wfirst = (plan.get("feed_demand", 0) or 0) > 0
        for crop, n in budget:
            if wfirst and crop == "WHEAT":
                flat.extend(["WHEAT"] * n)
        for crop, n in budget:
            if wfirst and crop == "WHEAT":
                continue
            flat.extend([crop] * n)
        turn_budget = n_units * max(1, 23 - hour)
        water_load = stats.get("water_crit", 0) + stats.get("water_yield", 0)
        safe_plant = int((turn_budget - water_load * 2.0) / 4)
        n_plant = min(len(flat), len(empties), max(0, safe_plant))
        _pt = 3 if len(empties) > 6 else T_PLANT  # R171: hố sau mua đất — PLANT
        # tier 3 khi còn >6 ô trống (cũ 4 = T_PLANT — no-op; v8 chết 25-33 ô
        # d10-13 vì PLANT đói dịch chuyển)
        for i in range(n_plant):
            x, y = empties[i]
            c = flat[i]
            _tier = _pt
            if _tier > 1 and (
                    (c == "WHEAT" and wheat_standing_n < 16)
                    or (c == "CARROT" and day >= 24)
                    or (c == "CARROT" and standing_carrot_n < 4 and 5 <= day <= 22)
                    or (c == "STRAWBERRY" and day <= 16
                        and (plan.get("standing", {}).get("STRAWBERRY", 0) or 0) < 14)
                    or (c == "TOMATO" and 17 <= day <= 19)):
                # TOMATO tier-1 (probe s130 d17): cửa sổ 3 ngày + hạt đã mua
                # mà task tier-4 thua 29 DIG — kênh $2-3k mất trắng
                _tier = 1
            tasks.append(_mk(_tier, x, y, "PLANT", crop=c))

    # Trụ 5 (R159) WHEAT-REFILL: máy feed không được chết — plan h0 không
    # thấy ô vừa harvest giữa ngày (v8-base đứng 0-9 ô từ d14 vì quota
    # only-morning). Refill độc lập: standing < 18 → trồng thêm ngay trong
    # giờ, tier 1 khi < 14 (top-3 giữ 13-32 ô cả mùa bằng 4-8 lần trồng/ngày).
    try:
        if 2 <= day <= 26 and hour <= 20 and seeds and wheat_standing_n < 20:
            _wt_planted = (planted.get("WHEAT", 0) or 0)
            _want = min(10, 20 - wheat_standing_n - _wt_planted)
            _have = seeds.get("WHEAT", 0) or 0
            if _want > 0 and _have > 0:
                _pl_xy = {(tk["x"], tk["y"]) for tk in tasks if tk["op"] == "PLANT"}
                _re = []
                for y2 in range(board):
                    for x2 in range(board):
                        if (tiles[y2][x2] is None and (x2, y2) not in reserved_xy
                                and (x2, y2) not in _pl_xy):
                            _re.append((x2, y2))
                _re.sort(key=lambda c: min(abs(c[0] - sx) + abs(c[1] - sy)
                                           for sx, sy in _shed_tiles(board)))
                _tr = 1 if wheat_standing_n < 16 else 2
                for (x2, y2) in _re[:_want]:
                    if _have <= 0:
                        break
                    tasks.append(_mk(_tr, x2, y2, "PLANT", crop="WHEAT"))
                    _have -= 1
    except Exception:
        pass

    if fert_available > 0 and day < 27:
        # v8 Δ5 FERT-EVENT: bón dâu/tomato NGÀY EVENT (nước+fert = +2u thay
        # +1u — giá trị $130-190/ô/event) + wheat trong window (2u/ lần tưới),
        # cap 22 — nguồn: đàn nhả 16-22 FERT/ngày (v7 thu 43%, top-3 71-81%)
        # v9 K3-K6: carrot + melon ws-1 vào stack; dâu cap 6/h dàn đều giờ
        # (kernel gap-0 hấp thụ theo giờ, không dồn 1 buổi)
        made = 0
        capf = min(int(fert_available), 22)
        for y in range(board):
            for x in range(board):
                if made >= capf:
                    break
                t = tiles[y][x]
                if not isinstance(t, dict) or t.get("kind") != "PLANT":
                    continue
                if t.get("fertilized_until_day", -1) >= day:
                    continue  # còn hiệu lực (3 ngày)
                crop = t.get("crop")
                cd = CROPS[crop]
                age = day - t.get("planted_day", day)
                if crop in ("STRAWBERRY", "TOMATO") and cd["ongoing"]:
                    dsf = (day + 1) - t.get("planted_day", day) - cd["first_yield_day"]
                    if dsf < 0 or dsf % cd["interval"] != 0:
                        continue  # chỉ ngày event
                    if dsf // cd["interval"] + 1 > cd["max_yield"]:
                        continue  # sau vách
                    # R177: dâu event +2u cần NƯỚC+FERT cùng ngày — giá trị
                    # $150-250/lệnh (cao hơn hầu hết tier-2) nhưng cũ đứng
                    # tier 3 thua geo-queue → chỉ 50 lệnh/mùa (top-3 91-186)
                    # v9-K6: cap 6/giờ dàn đều (53c) — stack gap-0 hút dần
                    if stats.get("sfert9", 0) < 6:
                        tasks.append(_mk(2, x, y, "FERTILIZE"))
                        made += 1
                        stats["sfert9"] = stats.get("sfert9", 0) + 1
                elif crop == "MELON":
                    ws = (cd["max_yield_day"] + 1) // 2
                    # v9-K5 (R196-53c): bón từ ws-1 (1 ngày TRƯỚC window) —
                    # 3 nước chạm 6u thay 6 nước, thu sớm d8, giải phóng
                    # lao động cho dâu; tier 2 (gap-0 sau khi WATER cùng ô)
                    if ws - 1 <= age <= cd["max_yield_day"]:
                        tasks.append(_mk(2, x, y, "FERTILIZE"))
                        made += 1
                elif crop == "CARROT":
                    # v9-K4 (R195-53c): carrot không chết — chỉ thiếu FERT.
                    # 2 nước trên ô fertilized = 4u (R184 đúng cho kernel
                    # không-FERT); window 2 ngày nên bón ngay đầu window.
                    ws = (cd["max_yield_day"] + 1) // 2
                    if ws <= age <= cd["max_yield_day"]:
                        tasks.append(_mk(2, x, y, "FERTILIZE"))
                        made += 1
                elif crop == "WHEAT":
                    ws = (cd["max_yield_day"] + 1) // 2
                    if ws <= age <= cd["max_yield_day"]:
                        tasks.append(_mk(T_FERTILIZE, x, y, "FERTILIZE"))
                        made += 1

    stats["total"] = len(tasks)
    # v8 Δ2b TASK-AGE: ghi giờ đầu tiên task xuất hiện trong ngày — task xa
    # chờ lâu sẽ được cộng "đói" trong phase-2 geo-assign (không bao giờ
    # bỏ đói vĩnh viễn — v8a: wheat yu 17-20 ngồi trên ô tới h23)
    tage = _STATE.setdefault(("taskage", day), {})
    for tk in tasks:
        k = (tk["op"], tk["x"], tk["y"])
        if k not in tage:
            tage[k] = hour
        tk["age"] = hour - tage[k]
    return tasks, stats


def _drop_action(ux, uy, board):
    st = _nearest_shed_tile(ux, uy, board)
    if (ux, uy) == st:
        return ["DROP"]
    mv = _step_toward(ux, uy, st[0], st[1])
    return [mv] if mv else ["PASS"]


def _task_action(tk, ux, uy, uinv, tiles, shed, board):
    op = tk["op"]
    tx, ty = tk["x"], tk["y"]

    if op == "SERVICE":
        t = tiles[ty][tx] if 0 <= tx < board and 0 <= ty < board else None
        an = t if (isinstance(t, dict) and "animal" in t) else None
        if an is None:
            return ["PASS"]
        w = uinv.get("WHEAT", 0) or 0
        unfed = not an.get("fed_today", False)
        shed_w = (shed.get("WHEAT", 0) or 0) if shed else 0
        if unfed and w > 0:
            if (ux, uy) == (tx, ty):
                return ["FEED"]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        if unfed and w <= 0 and shed_w > 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, shed_w)
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
            else:
                mv = _step_toward(ux, uy, st[0], st[1])
                if mv:
                    return [mv]
        if (ux, uy) == (tx, ty):
            # v7 Δ-A (R149): collect fert TRƯỚC care — flag không tích lũy
            # qua ngày; care chờ 1 giờ không mất gì (bonus tính cuối ngày).
            if an.get("fertilizer_available", False):
                return ["COLLECT_FERTILIZER"]
            if not an.get("cared_today", False):
                return ["CARE"]
            return ["PASS"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "FEED":
        w = uinv.get("WHEAT", 0) or 0
        if w <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, (shed.get("WHEAT", 0) or 0) if shed else 0)
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
                return ["PASS"]
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ["PASS"]
        if (ux, uy) == (tx, ty):
            return ["FEED"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "DELIVER":
        item = tk.get("item")
        if uinv.get(item, 0):
            if (ux, uy) == (tx, ty):
                return ["PLACE", item]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        st = _nearest_shed_tile(ux, uy, board)
        if (ux, uy) == st:
            if shed and (shed.get(item, 0) or 0) > 0:
                return ["PICKUP", item, 1]
            return ["PASS"]
        mv = _step_toward(ux, uy, st[0], st[1])
        return [mv] if mv else ["PASS"]

    if op == "FERTILIZE":
        f = uinv.get("FERTILIZER", 0) or 0
        if f <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(6, (shed.get("FERTILIZER", 0) or 0) if shed else 0)
                if n > 0:
                    return ["PICKUP", "FERTILIZER", n]
                return ["PASS"]
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ["PASS"]
        if (ux, uy) == (tx, ty):
            return ["FERTILIZE"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if (ux, uy) == (tx, ty):
        if op == "PLANT":
            return ["PLANT", tk.get("crop")]
        return [op]

    mv = _step_toward(ux, uy, tx, ty)
    return [mv] if mv else ["PASS"]


def _task_still_valid(tk, tiles, board, shed, uinv, day=0):
    x, y = tk["x"], tk["y"]
    if not (0 <= x < board and 0 <= y < board):
        return False
    t = tiles[y][x]
    op = tk["op"]
    if op == "PLANT":
        return t is None
    if op == "WATER":
        return isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today", False)
    if op == "HARVEST":
        return isinstance(t, dict) and (t.get("yield_units", 0) or 0) > 0
    if op == "SERVICE":
        if not (isinstance(t, dict) and "animal" in t):
            return False
        if not t.get("fed_today", False):
            if (uinv.get("WHEAT", 0) or 0) > 0 or (shed.get("WHEAT", 0) or 0) > 0:
                return True
        return (not t.get("cared_today", False)) or bool(t.get("fertilizer_available", False))
    if op in ("FEED", "CARE"):
        return isinstance(t, dict) and "animal" in t and not t.get(
            "fed_today" if op == "FEED" else "cared_today", False)
    if op == "DIG":
        return isinstance(t, dict) and t.get("kind") == "WEED"
    if op in ("BUILD_COOP", "BUILD_PASTURE"):
        return t is None
    if op == "COLLECT_FERTILIZER":
        return isinstance(t, dict) and "animal" in t and t.get("fertilizer_available", False)
    if op == "FERTILIZE":
        # v8 FIX-BOM: nhánh cũ tham chiếu `day` ngoài scope -> NameError ->
        # agent() trả hands=[] (CẢ ĐỘI ĐỨNG IM HẾT NGÀY) mỗi khi task FERTILIZE
        # dính sticky qua giờ. v7 hiếm nổ (fert melon hiếm); v8 fert dâu/tomato
        # liên tục -> nổ hàng loạt (v8b −$20k). Đối chiếu logic tạo task Δ5.
        if not (isinstance(t, dict) and t.get("kind") == "PLANT"):
            return False
        if t.get("fertilized_until_day", -1) >= day:
            return False
        crop = t.get("crop")
        cd = CROPS.get(crop)
        if cd is None:
            return False
        if cd["ongoing"]:
            dsf = (day + 1) - t.get("planted_day", day) - cd["first_yield_day"]
            return dsf >= 0 and dsf % cd["interval"] == 0 \
                and dsf // cd["interval"] + 1 <= cd["max_yield"]
        age = day - t.get("planted_day", day)
        ws = (cd["max_yield_day"] + 1) // 2
        # v9-K5: melon mở ws-1 (bón trước window 1 ngày — khớp nhánh
        # tạo task K5); carrot/wheat giữ window chuẩn
        if crop == "MELON":
            ws -= 1
        return ws <= age <= cd["max_yield_day"]
    if op == "DELIVER":
        return (uinv.get(tk.get("item"), 0) or 0) > 0 or (shed.get(tk.get("item"), 0) or 0) > 0
    return True


def _assign_and_act(units, tasks, tiles, shed, inventories, day, hour, board, seeds):
    uinv_cache = {}
    for i in range(len(units)):
        u = inventories[i] if i < len(inventories) and isinstance(inventories[i], dict) else {}
        uinv_cache[i] = u

    sticky = _STATE.setdefault(("sticky", day), {})
    feed_pending = 0
    for tk2 in tasks:
        if tk2["op"] == "SERVICE" and tk2.get("feed"):
            feed_pending += 1
    for i in list(sticky.keys()):
        if i >= len(units):
            del sticky[i]
            continue
        tk = sticky[i]
        if not _task_still_valid(tk, tiles, board, shed, uinv_cache[i], day):
            del sticky[i]
            continue
        if feed_pending > 0 and tk["tier"] >= 2 and tk["op"] not in ("SERVICE", "FEED", "DELIVER") \
                and (uinv_cache[i].get("WHEAT", 0) or 0) > 0:
            del sticky[i]
    claimed = set()
    for i, tk in sticky.items():
        claimed.add((tk["op"], tk["x"], tk["y"]))

    free = [i for i in range(len(units)) if i not in sticky]
    plant_sticky = {}
    for i, tk in sticky.items():
        if tk["op"] == "PLANT":
            plant_sticky[tk.get("crop")] = plant_sticky.get(tk.get("crop"), 0) + 1

    def dist(i, tk):
        u = uinv_cache[i]
        if tk["op"] == "DELIVER" and (u.get(tk.get("item"), 0) or 0) > 0:
            return 0
        if tk["op"] in ("FEED", "SERVICE") and (u.get("WHEAT", 0) or 0) > 0:
            return 0
        d = abs(units[i][1] - tk["x"]) + abs(units[i][2] - tk["y"])
        if (u.get("WHEAT", 0) or 0) > 0 and tk["tier"] >= 1 and tk["op"] not in ("SERVICE", "FEED"):
            d += 6
        return d

    def skey(tk):
        md = min((dist(i, tk) for i in free), default=99)
        # K2 MORNING CASCADE (v9): h≤2 — task gần shed được claim trước;
        # hands vừa spawn ở shed quét ĐÀN (gần shed) trên đường ra ruộng,
        # commute sáng thành lao động (top-3: walk-per-op 1,0-1,5). Chỉ đổi
        # THỨ TỰ trong cùng tier — không đụng ưu tiên tier.
        if hour <= 2:
            h2 = len(tiles) // 2
            # khoảng cách thật tới 4 ô shed-access (tâm bàn)
            dsh = min(abs(tk["x"] - sx) + abs(tk["y"] - sy)
                      for sx in (h2 - 1, h2) for sy in (h2 - 1, h2))
            return (tk["tier"], dsh, md)
        return (tk["tier"], md)

    def try_claim(tk):
        if (tk["op"], tk["x"], tk["y"]) in claimed:
            return False
        if tk["op"] == "PLANT":
            c = tk.get("crop")
            if plant_sticky.get(c, 0) + 1 > (seeds.get(c, 0) if seeds else 0):
                return False
            plant_sticky[c] = plant_sticky.get(c, 0) + 1
        best = min(free, key=lambda i: dist(i, tk))
        sticky[best] = tk
        claimed.add((tk["op"], tk["x"], tk["y"]))
        free.remove(best)
        return True

    # ═══ K1 CONTINUATION CLAIMS (v9 kernel) ═══
    # Unit free tại vị trí hiện tại (vừa xong op / vừa spawn) claim NGAY
    # task gần trước khi phase-1 tier-first chạy:
    #   • d ≤ 1 (ô kề) với tier ≤ 2 → serpentine sweep + giữ money-priority
    #   • d = 0 (đúng chỗ đứng) với tier 3 → op-stacking gap-0
    #     (WATER→FERTILIZE, HARVEST→PLANT, FEED→CARE→COLLECT)
    # Kernel-autopsy: v8 mất 2,49 bước/op vì task scatter; top-3 1,0-1,5
    # nhờ 35-45% op tại gap-0 + sweep gap-1.
    for i in list(free):
        if not free:
            break
        ux, uy = units[i][1], units[i][2]
        best_tk = None
        best_key = None
        for tk in tasks:
            if (tk["op"], tk["x"], tk["y"]) in claimed:
                continue
            tr = tk["tier"]
            if tr > 3:
                continue
            d = abs(ux - tk["x"]) + abs(uy - tk["y"])
            if d > 1 or (d > 0 and tr > 2):
                continue
            key = (tr, d)
            if best_key is None or key < best_key:
                best_key = key
                best_tk = tk
        if best_tk is not None:
            if best_tk["op"] == "PLANT":
                c = best_tk.get("crop")
                if plant_sticky.get(c, 0) + 1 > (seeds.get(c, 0) if seeds else 0):
                    continue
                plant_sticky[c] = plant_sticky.get(c, 0) + 1
            sticky[i] = best_tk
            claimed.add((best_tk["op"], best_tk["x"], best_tk["y"]))
            free.remove(i)

    # v8e HYBRID ASSIGNMENT: pha 1 = tier-first CHO TIER 0-2 (money-ops:
    # water-crit/service/harvest — bảo đảm phủ như v7); pha 2 = geo + aging
    # CHO TIER 3+ (fill-ops: tưới-yield/trồng/dig — dùng phần dư lao động
    # sau money-ops, chọn việc GẦN unit). Bài học 4 biến thể: geo toàn phần
    # (v8a/c) pha loãng money-ops (−$8k MILK); tier-first toàn phần với
    # task-set mới (v8d) làm PLANT tier-2 cướp service (−$18k). Lai là đúng.
    # (v9: pha 0 continuation-claims đã chạy phía trên — TRƯỚC pha 1.)
    for tk in sorted((t for t in tasks if t["tier"] <= 2), key=skey):
        if not free:
            break
        try_claim(tk)

    rest = [t for t in tasks if t["tier"] > 2]
    while free and rest:
        best_i = best_tk = None
        best_sc = None
        for i in free:
            for tk in rest:
                if (tk["op"], tk["x"], tk["y"]) in claimed:
                    continue
                # task chờ lâu được cộng "đói" — không bỏ đói task xa vĩnh viễn
                sc = tk["tier"] * 1.0 + dist(i, tk) - min(6.0, 1.5 * tk.get("age", 0))
                if best_sc is None or sc < best_sc:
                    best_i, best_tk, best_sc = i, tk, sc
        if best_tk is None:
            break
        if best_tk["op"] == "PLANT":
            c = best_tk.get("crop")
            if plant_sticky.get(c, 0) + 1 > (seeds.get(c, 0) if seeds else 0):
                rest.remove(best_tk)
                continue
            plant_sticky[c] = plant_sticky.get(c, 0) + 1
        sticky[best_i] = best_tk
        claimed.add((best_tk["op"], best_tk["x"], best_tk["y"]))
        free.remove(best_i)
        rest.remove(best_tk)

    planted = _STATE.setdefault(("planted", day), {})
    actions = []
    for idx in range(len(units)):
        ux, uy = units[idx][1], units[idx][2]
        uinv = uinv_cache[idx]
        carried = sum(v for v in uinv.values() if _is_num(v))
        sellable = carried - (uinv.get("WHEAT", 0) or 0)
        act = ["PASS"]
        tk = sticky.get(idx)

        need_drop = sellable >= 18 or (hour >= 20 and sellable >= 3) \
            or (day >= 28 and hour >= 14 and sellable >= 1) \
            or (day >= 29 and hour >= 8 and sellable >= 1)  # R178b: d29 rửa sớm từ h8
        # [R193b THỬ VÀ LOẠI ở Vòng 50 — xem ghi chú R193 ở nhánh salvage;
        # cargo-rush melon làm s117 −$16.6k, battery avg −$1.6k. Bỏ.]
        if need_drop:
            act = _drop_action(ux, uy, board)
        elif tk is not None:
            act = _task_action(tk, ux, uy, uinv, tiles, shed, board)
        if isinstance(act, list) and act and act[0] == "PLANT":
            crop = act[1]
            planted[crop] = planted.get(crop, 0) + 1
        actions.append(act)
    return actions


def _wheat_all(shed, inventories):
    w = (shed.get("WHEAT", 0) or 0) if shed else 0
    for u in inventories or []:
        if isinstance(u, dict):
            w += u.get("WHEAT", 0) or 0
    return w


def _build_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan,
                  stats, tiles, shops):
    orders = []
    money = float(_g(me, "money", 0) or 0)
    hands = _g(me, "hands", None) or []
    unlocked = _g(me, "unlocked_quadrants", None) or ["NW"]
    board = len(tiles) if tiles else 10
    shed_total = sum(v for v in (shed or {}).values() if _is_num(v))

    # R178 [E] (Vòng 48): D29 LÀ NGÀY LÀM VIỆC ĐẦY — top-3 thuê 9-12 hands
    # xuyên d29 (h0-h4, $88-143) thu $7.484 ngày cuối; gate `day < 29` cũ để
    # 0 hands → d29 chết ($2.288 vs 7.484 = −$3-5k/trận). Bỏ gate: hire tới
    # khi workload cạn, cap 13 giữ nguyên, fib reset h0 như mọi ngày.
    if hour <= 5:
        planted_today = _STATE.get(("planted", day)) or {}
        plant_budget = sum(max(0, n - planted_today.get(c, 0))
                           for c, n in plan.get("crop_tiles", {}).items())
        workload = stats.get("total", 0) + plant_budget
        if day >= 6:
            cap = 13 if ((day >= 9 and money >= 1800) or (day >= 18 and money >= 2500)) else 12
            # ΔF HIRE-14: lấp nhanh 25 ô mới d10-13 + fill mạn tính d17-26
            # khi giàu (đơn #14 fib $377/ngày — giá 1 action wheat $45-51,
            # tomato $120; tier bảo vệ feed/care/water-crit như cũ)
            try:
                _n_empty_h = sum(1 for row in tiles for t in row if t is None)
                if 10 <= day <= 26 and money >= 6000 and _n_empty_h > 10:
                    cap = 14
            except Exception:
                pass
            target_units = min(cap, max(8, 6 + money // 500))
        elif day >= 1:
            target_units = 8
        else:
            target_units = 7
        # Δ3 HIRE-BOOST: đang có >12 ô trống d4-25 -> 10 units (10 hands =
        # fib $143/ngày; lấp sớm trả lời nhanh hơn tiền công)
        try:
            if 4 <= day <= 25 and money >= 150:
                _n_empty_now = sum(1 for row in tiles for t in row if t is None)
                if _n_empty_now > 12:
                    target_units = max(target_units, 10)
        except Exception:
            pass
        target_units = max(target_units, min(11, 1 + int(math.ceil(workload * 2.6 / max(5, 23 - hour)))))
        want = target_units - (1 + len(hands))
        n_hired = _g(me, "hires_today", 0) or 0
        cost = 0
        k = 0
        hire_floor = 60 if day <= 5 else 150
        if money > hire_floor + 88:
            hire_budget = min(money - hire_floor, max(88, money * 0.25))
        else:
            hire_budget = max(0, money - 10)
        while k < want and k < 5:
            c = _fib(n_hired + k)
            if cost + c > hire_budget:
                break
            cost += c
            orders.append(["HIRE"])
            k += 1

    bought = _STATE.setdefault(("bought", day), {"GOOSE": 0, "COW": 0, "SHEEP": 0, "LAND": 0})
    pending_animal_cost = 0

    # ==== 4 LUẬT CỨNG (top Kaggle) — LAND-FIRST ====
    # HARD-1 NE ($1k) d5-7 · HARD-2 SW ($2k) d10-12 · HARD-3 KHÔNG mua SE
    # (fallback muộn chống khoá 25 ô: NE d8-9, SW d13-14)
    nq = len(unlocked)
    if nq < 3 and bought.get("LAND", 0) < 1:
        if nq == 1:
            if ((5 <= day <= 9 and money >= 1000 + 150) or (day >= 10 and money >= 1150)):
                orders.append(["BUY_LAND"])
                bought["LAND"] = 1
                money -= 1000
                # plan d5 được dựng lúc h0 TRƯỚC khi mua đất -> 25 ô NE
                # không tồn tại trong plan; d6+ cửa sổ tưới melon [6,12]
                # ăn hết lao động -> NE trống tới d11. Hủy cache để plan
                # dựng lại trong chiều d5 (nông trại đang rảnh — 0 thú,
                # melon chưa vào window)
                _STATE.pop(("plan", day), None)
        elif nq == 2:
            if 10 <= day <= 16 and money >= 2000 + 250:
                orders.append(["BUY_LAND"])
                bought["LAND"] = 1
                money -= 2000
                _STATE.pop(("plan", day), None)
    land_reserve = 0
    if nq == 1 and 3 <= day <= 9 and bought.get("LAND", 0) < 1:
        land_reserve = 1150
    elif nq == 2 and 8 <= day <= 14 and bought.get("LAND", 0) < 1:
        land_reserve = 2150
    if hour <= 8 and 0 <= day <= 22:
        struct_free = {"COOP": 0, "PASTURE": 0}
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k in struct_free and "animal" not in t:
                        struct_free[k] += 1
        animals_total = sum(1 for row in tiles for t in row
                            if isinstance(t, dict) and "animal" in t)
        wt = _wheat_all(shed, inventories)
        wheat_ripe = sum(1 for row in tiles for t in row
                         if isinstance(t, dict) and t.get("kind") == "PLANT"
                         and t.get("crop") == "WHEAT"
                         and (day - t.get("planted_day", day)) >= 3)
        wt_supply = wt + 0.8 * wheat_ripe
        pxg = float(prices.get("EGG", 0) or 0)
        pxw = float(prices.get("WOOL", 0) or 0)
        pxm = float(prices.get("MILK", 0) or 0)
        milk_shops_n = sum(1 for s in (shops or [])
                           if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
        yarn_n = sum(1 for s in (shops or []) if s == "YARN_STORE")
        for animal, target, w0, w1 in (("COW", plan.get("cow_target", 0), 0,
                                        16 + (2 if pxm >= 200 else 0) + (2 if milk_shops_n >= 2 else 0)),
                                       ("GOOSE", plan.get("goose_target", 0), 0,
                                        14 + (2 if pxg >= 62 else 0)),
                                       ("SHEEP", plan.get("sheep_target", 0), 0,
                                        15 + (2 if pxw >= 250 else 0) + (2 if yarn_n >= 1 else 0))):
            owned = sum(1 for row in tiles for t in row
                        if isinstance(t, dict) and t.get("animal") == animal)
            owned += (shed.get(animal, 0) or 0) if shed else 0
            ad = ANIMALS[animal]
            cash_floor = 250 + land_reserve
            # R180b (Vòng 48): VAN HẠT SÓNG DÂU — trajectory thú (R180) sẽ
            # ăn sạch dòng tiền d9-13 (thú mua TRƯỚC hạt trong giờ) → sóng
            # refill dâu d11 ×14 hạt của vòng 45 biến mất (đo new48: S d7=5,
            # d14=12 vs 24). Khi dâu chưa đủ 14 ô trong cửa sóng: thú chờ,
            # hạt đi trước (máy wheat/carrot rẻ vẫn mua được qua floor riêng).
            if 5 <= day <= 14:
                try:
                    _st_st = (plan.get("standing", {}).get("STRAWBERRY", 0) or 0)
                    if _st_st < 14 and (plan.get("crop_tiles", {}).get("STRAWBERRY", 0) or 0) > 0:
                        cash_floor += 700
                except Exception:
                    pass
            # Trụ 1: d0-2 mua nhanh 3 con/ngày (top-3 mua 3-5 con d0);
            # ngược lại ramp d1-4 bị buy_per_day=2 kìm hãm. R179: d0 = 4
            # (2 bò + 1 cừu + 1 ngỗng starter mới)
            buy_per_day = 4 if day <= 0 else (3 if day <= 2 else (2 if day <= 14 else 1))
            # Trụ 1-fix (D): cap TỔNG 3 con/ngày từ d3 — top-3 mua rải 1-4
            # con/ngày d0-d10 (không splurge); trace s105: NEW rút $2.800 mua
            # 7 con d11-12 đúng lúc cần $2.000 SW + $1.400 hạt dâu → sóng dâu
            # chết đói vốn
            _tot_today = bought.get("GOOSE", 0) + bought.get("COW", 0) + bought.get("SHEEP", 0)
            if day >= 3 and _tot_today >= 3:
                continue
            if (owned < target and w0 <= day <= w1
                    and bought.get(animal, 0) < buy_per_day
                    and (day <= 2 or struct_free[ad["structure"]] > 0)
                    and money >= ad["cost"] + cash_floor and shed_total < 92
                    and (wt_supply >= (animals_total + 1) * 1.3 or animals_total == 0)):
                orders.append(["BUY_ANIMAL", animal, 1])
                bought[animal] = bought.get(animal, 0) + 1
                money -= ad["cost"]
        if 0 <= day <= 15:
            try:
                for animal, tgt in (("COW", plan.get("cow_target", 0)),
                                    ("SHEEP", plan.get("sheep_target", 0)),
                                    ("GOOSE", plan.get("goose_target", 0))):
                    own_n = sum(1 for row in tiles for t in row
                                if isinstance(t, dict) and t.get("animal") == animal)
                    own_n += (shed.get(animal, 0) or 0) if shed else 0
                    pending_animal_cost += max(0, int(tgt) - own_n) * ANIMALS[animal]["cost"]
            except Exception:
                pending_animal_cost = 0
    pending_animal_cost = min(pending_animal_cost, 1400)

    seed_spent = 0
    if hour <= 17 and seeds is not None:
        # Trụ 5-fix: melon lên TRƯỚC dâu trong cửa sổ wave-2 (8-14) khi
        # đứng < 8 — s311: melon 35u vs v6 78u, seed-buy thua queue
        # dâu/đàn cả mùa (BUY_SEED:MELON chỉ 3 lệnh) = mất kênh $8-10k
        _seed_order = ["WHEAT", "CARROT", "STRAWBERRY", "MELON", "TOMATO"]
        # R180c (Vòng 48): sóng dâu-1 d5-13 — dâu TRƯỚC carrot trong pass
        # mua hạt (đo new48: d5 wheat×13+carrot×7 ăn $270 trước → dâu chỉ
        # còn ×5 hạt; dâu là kênh $42.7k của top-3, carrot chỉ fill rẻ)
        if 5 <= day <= 13:
            _seed_order = ["WHEAT", "STRAWBERRY", "CARROT", "MELON", "TOMATO"]
        _mel_stand_now = sum(1 for row in tiles for t in row
                             if isinstance(t, dict) and t.get("kind") == "PLANT"
                             and t.get("crop") == "MELON")
        if 8 <= day <= 14 and _mel_stand_now < 8:
            _seed_order = ["WHEAT", "MELON", "STRAWBERRY", "CARROT", "TOMATO"]
        for crop in _seed_order:
            n_tiles = plan.get("crop_tiles", {}).get(crop, 0)
            if not n_tiles and crop != "WHEAT":
                continue
            # R170 (máy wheat chết từ layer hạt): plan h0 thấy standing 19 →
            # need 1 → không mua hạt; giữa ngày wheat chết/harvest → refill
            # không có hạt. Seed-buy wheat nhìn standing SỐNG hiện tại:
            # floor 16 − live (đúng 3 layer: plan/refill/seed-buy).
            # R190 (Vòng 50): 24 → 21 — hạt wheat trồng d22+ chỉ kịp 1 mứ
            # chín d26-28 (4-6u × $30-40 = $150-240/ô cho 7 task) trong
            # khi dâu d22-26 cần đúng task đó cho $120-180/harvest (s118:
            # P10 wheat d24 cướp nước → 22 ô dâu chết trắng $8-12k).
            if crop == "WHEAT" and 2 <= day <= 21:
                _wt_live = sum(1 for row in tiles for t in row
                               if isinstance(t, dict) and t.get("kind") == "PLANT"
                               and t.get("crop") == "WHEAT")
                n_tiles = max(n_tiles, 16 - _wt_live)
            if crop == "MELON" and day > 7 and day > 2 and False:
                continue
            if crop == "STRAWBERRY" and day < 5:
                continue
            if crop == "TOMATO" and (day < 2 or day > 19):
                continue
            have = seeds.get(crop, 0) or 0
            if have < n_tiles:
                need = n_tiles - have
                unit = CROPS[crop]["seed"]
                _bought_land = len(unlocked) >= 2
                floor = ((30 if _bought_land else 30 + land_reserve) if crop == "WHEAT" else
                         (150 + land_reserve) if crop == "STRAWBERRY" else
                         ((220 if _bought_land else 220 + land_reserve) if crop == "CARROT" else 220 + land_reserve))
                if crop == "TOMATO":
                    # ΔC: hạt tomato $50 — kênh 0 đối thủ, floor phẳng
                    floor = 400
                if crop == "WHEAT" and _bought_land and 5 <= day <= 13:
                    # ΔB-fix1 (bài học 146/132): valley sau NE tiền $100-250 —
                    # fill wheat KHÔNG được hút sạch tiền vì hands bị sa thải
                    # cuối ngày rồi thuê lại buổi sáng (fib 8 hands = $54);
                    # hút hết → $16 → 0-2 hands → farm chết d6-9 (146: -27k).
                    # Floor $120 = đủ thuê 9-10 hands + mua hạt feed.
                    floor = 120
                if crop == "STRAWBERRY":
                    floor = 900
                    # Δ1' partial-buy: d5-13 mua dâu từng phần giữ buffer $200
                    if 5 <= day <= 13:
                        floor = 200
                        # ΔB-fix2 (bài học 146: straw $300 d5h6 ăn vốn NE —
                        # khi CHƯA có NE, buffer phải là đủ mua NE $1150:
                        # kain37 R "straw-partial tự ăn vốn")
                        if nq == 1:
                            floor = 1350
                    try:
                        _spx = float(prices.get("STRAWBERRY", 0) or 0)
                        _sinv = float(inv.get("STRAWBERRY", MARKET_I0) or MARKET_I0)
                        # low floor only when treasury can survive the batch
                        if (_spx >= 1.25 * MARKET_PARAMS["STRAWBERRY"]["base"]
                                and _sinv <= MARKET_I0
                                and (money >= 1500 or day >= 12)):
                            floor = 200
                    except Exception:
                        pass
                if crop == "MELON":
                    floor = 700
                    # R179b (Vòng 48): d0 starter 2C+1S+1G ($1.600) để lại
                    # $1.400 — wheat+carrot ăn $300, melon 8 ô cần $640:
                    # floor 700 chặn mất nửa wave → floor 300 như wave-2
                    if day == 0:
                        floor = 300
                if crop == "MELON" and pending_animal_cost > 0:
                    floor = max(floor, min(pending_animal_cost, 1100))
                # Trụ 5-fix: wave-2 đứng < 8 → floor phẳng 300 (pending-animal
                # bump $1.1-1.4k bóp chết seed-buy melon cả mùa vs v6)
                if crop == "MELON" and 8 <= day <= 14 and _mel_stand_now < 8:
                    floor = 300
                max_afford = max(0, int((money - floor) // unit)) if unit > 0 else 0
                buy = min(need, max_afford)
                if buy > 0:
                    orders.append(["BUY_SEED", crop, buy])
                    money -= buy * unit
                    seed_spent += buy * unit
            if len(orders) >= 9:
                break



    animals = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and "animal" in t)
    plan_animals = plan.get("goose_target", 0) + plan.get("cow_target", 0) + plan.get("sheep_target", 0)
    if animals > 0 or plan_animals > 0:
        shed_wheat = (shed.get("WHEAT", 0) or 0) if shed else 0
        wheat_want = int(animals * 1.5) + 4
        try:
            if float(prices.get("MILK", 0) or 0) >= 200:
                wheat_want = int(animals * 2.0) + 6
        except Exception:
            pass
        # Trụ 4 (R158) + churn-fix: mua feed 3 pha. BÀI HỌC s203: gate _late
        # pw≤70 + buffer 2-ngày = chu kỳ mua-cao-bán-thấp (tối mua $45-70,
        # sáng sau bán $19-40 → rút $4-7k + nâng giá cho đối thủ). Sửa:
        # (a) trừ đi dòng máy wheat ĐANG ĐỨNG (~0.9u/ô/ngày) trước khi mua;
        # (b) d20+ chỉ mua KHẨN CẤP (shed<6); (c) đàn non d0-3 mua ≤$45.
        _early = day <= 3
        _late = day >= 20
        _acute2 = shed_wheat < 6
        _wheat_standing_now = sum(1 for row in tiles for t in row
                                  if isinstance(t, dict) and t.get("kind") == "PLANT"
                                  and t.get("crop") == "WHEAT"
                                  and (day - t.get("planted_day", day)) >= 1)
        _machine_inflow = 0.8 * _wheat_standing_now * 0.9
        # Trụ 4-fix (v6 lesson) + churn-stop: máy wheat là dòng TƯƠNG LAI
        # nhiều ngày — x2 dòng hôm nay; muốn mua thật = 2 ngày feed còn thiếu
        # sau khi trừ máy. s311: ta vẫn churn 85 lệnh (mua $35-45 tuần đầu,
        # sáng sau bán $19-25 — từng unit −$10-15)
        _eff_want = max(3, int(wheat_want - _machine_inflow * 2.0))
        _floor_money = 250 if (_early or (_late and _acute2)) else 400
        if shed_wheat < _eff_want and money >= _floor_money:
            need = min(14 if (_late and _acute2) else 10, _eff_want - shed_wheat)
            pw = _price("WHEAT", inv.get("WHEAT", MARKET_I0) - 1)
            afford = int((money * 0.35) // pw) if pw > 0 else 0
            n = min(need, afford)
            acute = shed_wheat < 6
        # Trụ E (R168) + R175: đàn 13 + máy 16-20 = tự cấp — feed-buy chỉ 4
            # cổng: rẻ (≤$38), khẩn cấp (≤$62), đàn non d0-3 (≤$45), cuối mùa
            # sập đàn (≤$70). BỎ dairy-deep $52. R175: KHÔNG MUA d27+ — đo
            # god-ledger: d28-29 v8 mua ~318u rồi bán ~350u cùng giá (round-trip
            # net $0 nhưng ngập 10 slot/giờ → milk/egg thanh lý không lên được)
            if n >= 1 and day <= 26 and (pw <= 38 or (acute and pw <= 62)
                                         or (_early and pw <= 45)
                                         or (_late and _acute2 and pw <= 70)):
                orders.append(["BUY_PRODUCT", "WHEAT", n])
                money -= n * pw

    absorb_key = ("absorb", day)
    if absorb_key not in _STATE:
        _STATE[absorb_key] = _forward_absorb(day, 0, shops)
    absorb = _STATE[absorb_key]
    glutted = set()
    for it in PRODUCTS:
        if it in ("FERTILIZER", "MELON"):
            continue
        over = inv.get(it, MARKET_I0) - MARKET_I0
        pr_now = prices.get(it, 0) or 0
        if over > absorb.get(it, 0) * 0.8 and pr_now < 0.75 * MARKET_PARAMS[it]["base"]:
            glutted.add(it)

    # KAIN-15 + Trụ 4 (R158): reserve feed — giữ TỚI d28 VÀ muộn mùa = phủ
    # toàn bộ nhu cầu còn lại của đàn (đàn×số ngày còn) — không bao giờ bán
    # thức ăn khi máy không đủ tự cấp (s203: bán 810u d20+ trong khi đàn đói
    # care-bonus → thua kênh milk/egg $14k cho base)
    _wheat_feed_need_late = animals * max(0, (29 - day)) if day >= 18 else 0
    wheat_reserve = min(max(animals * 3 + 6, _wheat_feed_need_late),
                        shed.get("WHEAT", 0) or 0) if day < 28 and shed else 0

    # v6 ΔF (E8-lite): drain-aware endgame — d22-27 nếu drain còn đủ hút
    # TOÀN BỘ nguồn chờ bán thì KHÔNG hạ ngưỡng (bán dần vào drain giá đẹp)
    absorb_rest = {}
    pipe_rest = {}
    try:
        if 22 <= day <= 27:
            absorb_rest = _forward_absorb(day, 0, shops)
            pipe_rest = _pipe_rest(tiles, day)
    except Exception:
        absorb_rest, pipe_rest = {}, {}

    def _hold(it):
        h = HOLD.get(it, 0.90)
        if it in glutted:
            return min(h, 0.40)
        # R189 (Vòng 50) — VAN HẠT SÓNG DÂU: wheat HOLD 1.50 ($37.5) chỉ bán
        # được d7/d10 rải rác (s118: shed 39u ngồi im d5-6) — v6 bán d5
        # $1.035 ngay → có vốn trồng dâu d5 vs v8 d7 (mất 1 chu kỳ thu
        # $2-4k). Cửa sổ d≤11 = đàn v6 còn 0-4 con (buyW chỉ từ d10) →
        # bán $22.5 không nuôi đối thủ (R162 chỉ áp dụng d12+ khi v6 hút
        # 30-40u/ngày).
        if it == "WHEAT" and day <= 11:
            return 0.90
        if 22 <= day <= 27:
            try:
                _np_ = float(shed.get(it, 0) or 0) + float(pipe_rest.get(it, 0.0) or 0.0)
                if _np_ > 0 and absorb_rest.get(it, 0.0) >= _np_ * 1.1:
                    return h
            except Exception:
                pass
        if day >= 28:
            return 0.004
        if day >= 27:
            return min(h, 0.20)
        if day >= 26:
            return min(h, 0.45)
        if day >= 22:
            return min(h, 0.70)
        if it == "MELON" and day >= 24:
            return min(h, 0.30)
        if it == "MELON" and day >= 21:
            return min(h, 0.42)
        if shed_total >= 80:
            return min(h, 0.72)
        if money < 250:
            return min(h, 0.65)
        return h

    cands = []
    if shed:
        for it in PRODUCTS:
            if it == "FERTILIZER" and day < 26:
                nf = shed.get("FERTILIZER", 0) or 0
                # K3 FERT-KEEP 8 (v9, cấu hình 53c): giữ 8 FERT trong shed từ
                # d4 (cũ 2). Vòng 53 đã chứng minh FERT bón +$1,6k/20-seed
                # NHƯNG kernel cũ chỉ hấp thụ 2,7 FERTILIZE/ngày (mỗi lệnh
                # = 1 chuyến đi riêng) — v9 stack gap-0 (bón đúng ô đang đứng
                # sau khi WATER) làm chi phí biên rơi về 1 unit-hour.
                if nf > 0 and day >= 1:
                    keep = 8 if day >= 4 else 0
                    k = _sell_count("FERTILIZER", nf - keep, inv.get("FERTILIZER", MARKET_I0), FERT_FLOOR)
                    if k > 0:
                        cands.append((k * 60, ["SELL", "FERTILIZER", k]))
                continue
            n = shed.get(it, 0) or 0
            if it == "WHEAT":
                n = max(0, n - wheat_reserve)
                if 27 <= day <= 28:
                    n = 0  # R175: không bán wheat d27-28 (churn vòng tròn); R178b:
                    # d29 MỞ LẠI — game kết thúc h22 không có EOD, feed tồn
                    # shed = giá trị chết, thanh lý nốt (top-3 shed cuối ~rỗng)
            if n <= 0:
                continue
            thresh = _hold(it) * MARKET_PARAMS[it]["base"]
            k = _sell_count(it, n, inv.get(it, MARKET_I0), thresh)
            # KAIN-16: deep-drain channels (MILK/WOOL/EGG) recover price
            # between hours as the town drains inventory — tranche at 8/hour
            # instead of dumping 19 at once down the curve (v5 sells 3-9 per
            # order and banks the recovery premium).
            if k > 8 and it in ("MILK", "WOOL", "EGG") and day < 26:
                k = 8
            if k > 0:
                cands.append((k * (prices.get(it, 0) or 0), ["SELL", it, k]))
    cands.sort(key=lambda c: -c[0])
    for _, o in cands:
        if len(orders) >= MAX_ORDERS:
            break
        orders.append(o)

    return orders[:MAX_ORDERS]


def _agent(obs):
    player = _g(obs, "player", 0)
    farms = _g(obs, "farms", None) or []
    if not farms or player is None or not (0 <= player < len(farms)):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    me = farms[player]
    day = _g(obs, "day", 0) or 0
    hour = _g(obs, "hour", 0) or 0
    step = day * TURN_PER_DAY + hour
    if day == 0 and hour == 0:
        _STATE.clear()

    tiles = _g(me, "tiles", None) or []
    board = len(tiles)
    if board == 0:
        return {"farmer": ["PASS"], "hands": [], "market": []}

    private = _g(obs, "private", None) or {}
    market = _g(obs, "market", None) or {}
    town = _g(obs, "town", None) or {}
    shed = _g(private, "shed", None) or {}
    seeds = _g(private, "seeds", None) or {}
    inventories = _g(private, "inventories", None) or []
    prices = _g(market, "prices", None) or {}
    inv = _g(market, "inventory", None) or {}
    shops = _g(town, "unlocked_shops", None) or []
    opp = farms[1 - player] if len(farms) > 1 else None

    tm = _STATE.setdefault("tm", {})
    _tm_step(tm, step, inv, shops)

    pkey = ("plan", day)
    if pkey not in _STATE:
        mc = sum(1 for row in tiles for t in row
                 if isinstance(t, dict) and t.get("animal") == "COW")
        mg = sum(1 for row in tiles for t in row
                 if isinstance(t, dict) and t.get("animal") == "GOOSE")
        msp = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and t.get("animal") == "SHEEP")
        _bayes_step(tm, day, opp, (mc, mg, msp), float(_g(me, "money", 0) or 0))
        _STATE[pkey] = _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp,
                                   float(_g(me, "money", 0) or 0), tm)
    plan = _STATE[pkey]

    fpos = _g(me, "farmer", None) or [board // 2 - 1, board // 2 - 1]
    units = [(0, int(fpos[0]), int(fpos[1]))]
    for i, h in enumerate(_g(me, "hands", None) or []):
        units.append((i + 1, int(h[0]), int(h[1])))

    tasks, stats = _build_tasks(tiles, shed, seeds, plan, day, hour, step,
                                inventories, len(units))

    orders = _build_orders(me, shed, seeds, inventories, inv, prices, day,
                           hour, plan, stats, tiles, shops)
    _tm_orders(tm, orders)

    actions = _assign_and_act(units, tasks, tiles, shed, inventories, day,
                              hour, board, seeds)

    return {"farmer": actions[0], "hands": actions[1:], "market": orders}


def agent(obs):
    try:
        return _agent(obs)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
