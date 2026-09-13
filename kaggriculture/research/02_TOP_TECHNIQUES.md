# 02 — DANH MỤC KỸ THUẬT ĐẮT GIÁ NHẤT TỪ PUBLIC META (mức code)

> Tổng hợp từ 5 báo cáo ANALYSIS_*.md (Task 74-a→e). Mỗi kỹ thuật ghi: nguồn notebook cụ thể,
> mô tả code-level, độ tin cậy (bao nhiêu nguồn độc lập xác nhận), trạng thái so với v15 ta.

## A. TẦNG THỊ TRƯỜNG (market execution) — trái tim của meta hiện tại

### A1. Clone preemption có sổ nợ (debt-ledger) ⭐⭐⭐⭐⭐
- **Nguồn**: boatlee 84/84 · Kaito v44/v48 · tetsutani · prvsiyan — **4 nguồn độc lập**
- **Code** (boatlee): `_signature(farm) = (hands, quadrants, counts 11 loại ô)`; `clone_distance = |Δhands| + 3×|Δquadrants| + Σ|Δcounts|`, gate ≤6.
  Khi phát hiện near-clone ở 120 ≤ step < 680: lấy SELL premium của `ACTIONS[step+1]`, bán `target = min(shed_dự_phóng, future, 30)` ngay,
  ghi `state["due"][item] = target`, **turn sau khấu đúng lượng khỏi SELL gốc** → bất biến 2-turn bảo toàn lượng (chỉ đổi thời điểm).
- **Sai khác v15 ta**: front_run của ta dựa `opponent_plan` giả định lineage; họ **đo từ public state** (bất kỳ near-clone nào).
- SELL fail → chuyển nợ sang turn sau (Kaito).

### A2. Town-demand gate cho front-run ⭐⭐⭐⭐⭐
- **Nguồn**: salemali7 · boatlee V16-RC5 · andrew munib_FR — **3 nguồn**
- **Code**: chỉ pull-forward khi turn hiện tại KHÔNG có shop cầu item đó (`step%4≠0 and step%24≠0` — giờ 0/12 có tick demand kép).
  Mapping `_SHOP_PRODUCTS` (shop → item nó hút) = R41 ta đã có.
- **Sai khác v15**: ta chỉ gate `step%4==0`. Đây là **1-dòng fix**.

### A3. Price-impact ranking phi tuyến ⭐⭐⭐⭐
- **Nguồn**: boatlee V14/V23 (mô hình hard-code khớp engine: milk/straw linear-1.6, wool/melon sq-3.2/3.6) · Kaito v43 MARKET_PARAMS
- **Code** (Kaito v43): bảng giá 9 item (base, equilibrium 10.000, shape riêng dưới/trên: WHEAT sqrt/log, MELON log/sq, WOOL log/sq...)
  + demand model (shop %4 ×2 nếu 1-product, center %12 ×1/2/4) → mô phỏng impact **không cần engine**.
  Xếp SELL cùng turn theo `qty × (giá_hiện − giá_sau_khi_tự_đổ)`; thêm urgency khi gần trần kho.
- **Sai khác v15**: sorts theo giá hiện tại, không model giá sau dump.

### A4. Contested-value SELL ranking ⭐⭐⭐⭐
- **Nguồn**: indarkarhana E749 (duy nhất nhưng rất hợp lý)
- **Code**: xếp slot SELL theo `Σ giá block bán ngay − Σ giá block displaced` = đo trực tiếp tổn thất gây cho người bán kế tiếp.
  Order-only ~25 dòng.

### A5. Exposure×glut scoring khi gặp clone ⭐⭐⭐
- **Nguồn**: romantamrazov Hamburger
- **Code**: đếm tiles đối thủ → map COW→MILK, SHEEP→WOOL...; `score = price×min(q,12) + 0.075×price×min(q,8)×exposure×glut + 0.10×price×q×glut`
  với glut per-item (WHEAT 0.2 → MELON 3.6, WOOL 3.2). Không cần biết tape đối thủ.
- Clone-detect của hamburger = 5 điều kiện tile cứng (WHEAT≥5 ∧ STRAW≥26 ∧ MELON==6 ∧ COW≥8 ∧ SHEEP==6) — **không khớp profile v15** (ta đổi herd theo route).

### A6. Cluster bán giờ 0 ⭐⭐⭐
- **Nguồn**: Kaito v21.1 (63 lệnh SELL giờ 0; 199u STRAW đúng giờ 0)
- **Lý do**: day-boundary trùng tick demand kép (shop %4 + center %12) → giá đỉnh cục bộ.

### A7. Sequential funding ledger ⭐⭐⭐
- **Nguồn**: indarkarhana `_fund_market` — trong list 10 đơn: SELL cộng tiền ngay trong lượt, HIRE/BUY phía sau slice đúng tiền còn
  → chống reject cả cụm. (Cần verify engine xử lý đơn theo thứ tự list.)

### A8. Wheat round-trip quy mô lớn ⭐⭐
- **Nguồn**: Kaito v21.1 (mua 980 / bán 820, net −160 = feed)
- Vừa dự trữ feed vừa đi quanh dao động giá town demand. Rủi ro cao — chỉ tham khảo.

## B. TẦNG NHẬN THỨC (opponent modeling) — đỉnh cao kỹ thuật public

### B1. 1-NN Conditional Memory ⭐⭐⭐⭐⭐ (kỹ thuật đắt nhất toàn meta)
- **Nguồn**: Kaito v21.1 — claim **177/180 vs top-30**
- **Code**: 30 prototype = 719 bước chữ ký farm public + tập item từng bán ở mỗi step. Mỗi turn: tìm prototype gần nhất
  (distance ≤48; weight 12×workers / 7×quadrant / 3×counts) → đoán item đối thủ **sắp bán ngay turn này** → kéo SELL trùng
  của mình lên đầu queue. **Chỉ đổi thứ tự, không tạo SELL mới** (682 reorder/53 game, abstain 2.4% khi không chắc).
- **Sai khác v15**: ta không có opponent-item prediction từ public state.

### B2. Public-state router + steering surface ⭐⭐⭐⭐⭐ (mới về khái niệm tấn công)
- **Nguồn**: thomastschinkel v5 (93.8%, 44.096 game)
- **Code**: 5 tape; mỗi 144 turn chạy decision tree trên 100 feature public (money 2 bên, 9 giá, 9 inventory−10k, 8 shop, 9 demand,
  farm counts + Σyield_units + weeds + quadrants, shed, seeds). Ví dụ: day-6 `YARN mở → tape sheep-heavy`; day-24 `px_CARROT ≤ 54 → tape3 late-liquidation`.
- **Đòn "steering" (phát hiện của Task 74-b)**: ta **đổ CARROT trước step 576** → ép px_CARROT ≤54 → đẩy router vào tape3 thấp giá trị.
  Lớp tấn công mới: thao túng *state mà router đối thủ đọc*. Không vi phạm luật đối xứng (ta đổi state, không đổi engine).

### B3. Mirror logistic 7-feature ⭐⭐⭐
- **Nguồn**: Kaito v20 (threshold 0.8065, 95% precision, latch step 48, release sau 8 turn lệch) — nền tảng nghiên cứu: board 2 bên khớp 24 turn → market intent trùng 99.11%.
- **boatlee V29-R1 mirror latch**: composition distance ≤2 + hands/quadrants bằng + |Δmoney| ≤250 → **max_extra=0, tắt hẳn layer adaptive**
  → xác nhận độc lập luật **L38 mirror knife-edge** của ta: gặp mirror thì can thiệp = xúc xắc, im lặng tối ưu.

### B4. Spend-detector tie-break ⭐⭐⭐⭐
- **Nguồn**: andrewsokolovsky "Breaking the Tie"
- **Code**: theo dõi `opponent_money`; nếu tại **step 217** (cửa sổ cattle-switch) đối thủ tiêu ≥$100 so với lượt trước → bật **vĩnh viễn**
  overlay = action gốc + Δ(base→front-run) trên 4 món WOOL/MILK/MELON/STRAW. Elo tính W/L/T → bẻ tie 1 lần là đủ.
- **Sai khác v15**: ta có front_run-sync nhưng thiếu trigger spend-detector.

### B5. Legacy-layout fingerprint fallback ⭐⭐
- **Nguồn**: tetsutani — fingerprint tile đối thủ (WHEAT5/MELON5/COW1/SHEEP4 + money≤12) ở step 24-72 → đổi cả bộ tape sang layout khác (chống bị copy).

## C. TẦNG VẬN HÀNH (execution robustness)

### C1. WEED-slip recovery (chỉ repair action bị chặn) ⭐⭐⭐⭐
- **Nguồn**: raykkretzschmar C92 (22-6-72, BT 1973) · Kaito v20 (159/160) — 2 nguồn
- **Code**: PLANT/BUILD gặp ô WEED → DIG ngay → retry ý định t+1 → replay **chỉ actor đó** ≤8 turn, resync tại PASS kế tiếp.
  Ablation paired: 8 loss→win, 0 win→loss. Đổi 1 trận -7.288 → +3.455.

### C2. Terminal relay 716-718 + mega-SELL ⭐⭐⭐⭐
- **Nguồn**: hamburger (walk-to-shed khi `distance ≤ 718-step` + guaranteed-noop, DROP nếu room, PLACE item tốt) · boatlee (SELL qty **1.000.000** — engine tự kẹp bằng shed; "bán tất" 0 dòng runtime)
- **Sai khác v15**: terminal_liquidation + dead_stock đang OFF — **2 A/B rẻ nhất chưa làm** (74-b gọi "19/−0 ở thomast 968 game").

### C3. R88 horizon-check feed ⭐⭐⭐⭐
- **Nguồn**: guruprasaathas V39 (EXP219)
- **Code**: `care/feed = 0` nếu dawn sản xuất kế tiếp > ngày 29; pending_care_bonus chỉ tính vào dawn sản xuất — **~15 dòng**, chống feed vô ích cuối mùa.

### C4. Hour-23 + dedicated hire (không displace native plans) ⭐⭐⭐⭐
- Xác nhận độc lập từ Kaito/boatlee với luật **L39** của ta (Task 73: displacement -$8.6k cho 2 CARE):
  chỉ hire riêng ($3-13 spawn ô shed-access) hoặc dùng giờ 23 (không có lượt kế). R90 của v15 đúng hướng.

### C5. Invariant "đúng 1 child call/turn" ⭐⭐⭐⭐ (bài học máu)
- **Nguồn**: Kaito v47→v48 — v47 gọi 4 child stateful trước decision point → exception nuốt action → **PASS 719 turn, thua 11/11 đúng $3.000**.
  v48 fix: invariant 1 call/turn + smoke test "first action non-PASS" (đúng đầu tiên không phải PASS).

## D. TẦNG KINH TẾ (planning)

### D1. Scenario-admission gate đầu tư ⭐⭐⭐
- **Nguồn**: pilkwang — cổng V233 sheep paddock: 2 kịch bản stress (rival adopts 6 cừu/feed ×1.25; delivery haircut 25%), chi phí $7000 + fib labor; ALLOW iff worst-case surplus ≥ 0.

### D2. Adaptive market hysteresis (EMA áp lực đối thủ) ⭐⭐⭐
- **Nguồn**: boatlee V29-R1 — `0.72×old + clip(Δinv + town_demand − own_sold)`; reserve 12→8→6→3→2→0 theo mùa; price gate 0.66; **budget 18 unit/item cả mùa**.

### D3. E773 pressure formula herd-gate ⭐⭐
- **Nguồn**: indarkarhana — `wool = 2·YARN + price/200` vs `dairy = 3-shop + price/160`, gap ±1, cap 3:1, relabel COW↔SHEEP giữ geometry (pasture service-sẵn).

### D4. Kenjo1209 medoid 9C/5S/HIRE290 ⭐⭐⭐
- **Nguồn**: indarkarhana E776 — tape top-10 thật ngoài registry ta. E775 "latent pasture" (+1 animal step 313-317 nhét vào pasture service-sẵn).

## E. NHỮNG THỨ ĐÃ BỊ LOẠI (negative results — đừng lặp lại)

| Ý tưởng | Kết quả | Nguồn |
|---|---|---|
| Quadrant-4 (SE $4k) mọi biến thể | 0-40 vs C92, -3.885 trung bình; cả Seb route thua 14-37k | raykkretzschmar C93 |
| Fixed horizon dài (H=25) | 0-6 vs C45 | raykkretzschmar |
| Threshold banking 500/1000 | 0-8 (chỉ ≥$2000 + ≤1 move sống) | raykkretzschmar C72 |
| Budget-guard 72-turn (kiểu lynnsakurai) | 0/8 -$17.8k (Task 69 của TA tự đo) + cross-check | bench của ta |
| Buy 6 wheat đầu | 0-4 regression | raykkretzschmar C94 screen |
| Buy 14-19 wheat exploit + resell | Mạnh nhưng brittle vs Kaito route | raykkretzschmar C94 |
| Seat router (chọn route theo ghế) | 1/3 real losses solved vs 3/3 fixed route | Kaito v27 |
| Displace worker giữa ngày (2 CARE) | -$8.602 (luật L39 của ta) | Task 73 |
| pool-age grace cho placement | race 2 ngày V233 (luật L40 của ta) | Task 73 |

## F. SỐ LIỆU CHỐT CHO PLANNER (georgymarin 1.32.7)

- Profit/tile-day: MELON $142 ≫ CARROT 28.3 > STRAW 23.8 > WHEAT 22.5 > TOMATO 17.3
- CARE cuối mùa: SHEEP +$5.575 · COW +$4.635 · GOOSE +$1.675 (fed-only chỉ $300-600)
- Crash depth: WOOL 59u · STRAW 62u · MILK 76u · MELON 158u · WHEAT/EGG không chạm
- 100 melon 1 lượt = 87% giá trị; modal meta 8/11: 9c+4s+1w+10h
