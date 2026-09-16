# 05 — V19 DEPLOYMENT PLAN: "REAPER"
## Nền v18 (jaxa623 K0006) + Intel Top-1 Majkel1337 — mục tiêu ĐÁNH BẠI TẤT CẢ với BIÊN ĐỘ LỚN

> Task 82 · 2026-09-16 · Ari (AI engineer / system architect)
> Nguồn tổng hợp: `top1/README.md` (dữ liệu 2 trận top-1, parse 0-mismatch) +
> `top1/04A_MATCH2_MAJKEL_WIN_ANALYSIS.md` (Majkel thắng DSM +7,716) +
> `top1/04B_MATCH1_MAJKEL_LOSS_ANALYSIS.md` (ymg_aq thắng Majkel +451) +
> `01_V18_BASE_ANALYSIS.md` (kiến trúc v18) + `03_V18_ROADMAP.md` (hàng đợi MD + negative results).

---

## 0. TÓM TẮT ĐIỀU HÀNH

**Luận đề của v19**: `Timing của Majkel + Breadth của ymg_aq, đặt trên khung v18 đã được kiểm chứng.`

Phân tích 2 trận gần nhất của #1 Majkel1337 cho thấy meta top-1 không phải "farm plan hay hơn" mà
là **3 tầng quyết định kết quả ở 4 ngày cuối**:

1. **ENDGAME LIQUIDATION** — người giữ được item có town-recovery cao nhất (STRAWBERRY) đến
   step 719 rồi mega-dump sẽ ăn $6,000-7,500 gọn trong 1 step. Cả 2 trận đều quyết định ở
   step 715-719, không phải ở mid-game.
2. **TROUGH THROTTLE** — cắt bán khi giá đáy, tích shed 65 units, chờ giá hồi +100% rồi mới bán:
   +$4,757 cho người làm, −$4,474 cho người không làm.
3. **PORTFOLIO BREADTH** — match1 Majkel (top-1!) thua vì portfolio hẹp: không GOOSE/EGG
   (−$10,926 ΔEGG cho ymg_aq), 9 dòng revenue của ymg_aq áp 5 dòng của Majkel. Người bán giá
   TỆ hơn (STRA @96 vs @137) vẫn thắng nếu có thêm 2-3 dòng "không đối thủ".

v18 hiện tại (4 edges: HORIZON-24 / OPEN-50 / FRONT-LOAD / ADVANCE-2) là **market micro-layer**,
hoàn toàn KHÔNG có 3 tầng trên. Đó là khoảng trống $8,000-15,000/game mà v19 sẽ chiếm.

**Mục tiêu định lượng (định nghĩa "thắng cách xa")**:
| Cổng | Điều kiện |
|---|---|
| G1 — vs v18 | 64 worlds × 2 ghế: mean margin ≥ **+$2,500**, bootstrap CI-95% lower bound > +$1,000, worst world ≥ −$1,500 |
| G2 — vs sparring | vs ahmedv43/44/45: mean margin ≥ +$1,500 mỗi đối thủ |
| G3 — stress-clone | chống được counter tự xây (early-dump-vs-holder, EGG-race, throttle-copy): ≥ +$500 |
| G4 — runner audit | official `kaggle_environments` runner, single-file packaged, 0 lỗi, 0 slow-turn |
| G5 — không thoái hóa | 24 dev-seed battery: winrate ≥ winrate của v18 − 2 trận |

---

## 1. DỮ LIỆU & PHƯƠNG PHÁP

- Kaggle API (token đã lưu): leaderboard → Majkel1337 = teamId 16718819, hạng 1 (3,191.7).
- Submission đang chạy: 56216119 (13-09, public 3,179.0). 2 episode mới nhất:
  - **match1** = 109776263 (16-09 19:27): ymg_aq (hạng 4) vs Majkel1337 → 86,713 vs 86,262. **Majkel thua 451.**
  - **match2** = 109770002 (16-09 19:03): Majkel1337 vs DSM (hạng 3) → 91,845 vs 84,129. **Majkel thắng 7,716.**
- Parser `top1/parse_replay.py` re-simulate lockstep engine từng bước (kể cả shed-impact của
  DROP/PICKUP/PLACE trước market) → **0 sai lệch tiền trên 720×2 bước của cả 2 trận**. Mọi con số
  trong tài liệu này đều truy vết được về orders/timeline/daily/market/town JSON.
- Engine facts đã verify từ source 1.32.7 (định vị dòng): `_end_of_day` auto-drop L860-882,
  animal escape khi `consecutive_unfed ≥ 2` L817-819, care-bonus L829-830, town consume L728-749,
  lockstep market L544-628, hire fib L696-703, land NE/SW/SE = 1000/2000/4000 L95-97.

---

## 2. CHÂN DUNG CHIẾN THUẬT TOP-1 MAJKEL1337 (tổng hợp 2 trận)

### 2.1 Vòng đời tiền (money lifecycle) — giống nhau ở cả top-1, top-3, top-4

| Pha | Ngày | Hành vi |
|---|---|---|
| Spend-down | d0-2 | Chi $3,000 xuống ~$5-180: seeds + 5-6 động vật đầu + feed + hire |
| Re-invest | d3-9 | Mua NE ($1,000) ngay revenue-event đầu (d5-6), SW ($2,000) d8-9; tiền rơi về $11-148 |
| Compound | d10-24 | Bán liên tục nhưng giữ ≤ ~$3,000 idle; tiền quay ngay thành seed/animal |
| Harvest | d25-28 | Dừng mua (buys → $0 từ d28), dừng feed (d28), cắt hiring d27 |
| **Liquidate** | **d29** | **Xả toàn bộ tồn kho; đặc biệt giữ item đắt nhất cho step 719** |

### 2.2 Bảng chứng cứ gốc (trích 04A/04B)

| Chỉ số | Majkel (2 trận) | Đối thủ | Δ ý nghĩa |
|---|---|---|---|
| Revenue ngày 29 (match2) | **$13,575** | DSM $6,943 | endgame dump = 96% margin trận |
| Cú dump step 719 (match2) | 42 STRA @173 avg = **+$7,258** | DSM +$1,260 | giữ hàng chờ giá cuối |
| Trough throttle (match2) | +$4,757 (giữ 65u chờ 84→186) | DSM −$4,474 (bán đáy @102) | price-gated sell rate |
| ΔEGG (match1) | $0 (không có GOOSE) | ymg_aq **+$10,926** (6 GOOSE $1,800 → 208 EGG) | breadth monopoly |
| Avg sell STRA | match2 152.3 / match1 137.3 | DSM 139.3 / ymg 96.3 | timing nhạy giá |
| Carrot factory | 125 gói seed từ d11 (match2) | DSM 76 gói từ d17 | +$7,200 carrot rev |
| Đất | NE d6 + SW d9, SE KHÔNG MUA | giống cả 3 top | SE âm EV (mục 4.2 04A) |
| Dead orders | 19 / 45 | DSM 2,709 / ymg ít | order hygiene |

### 2.3 Điểm mấu chốt rút ra (key moments → nguyên lý)

1. **Step 719 là "cái chuông"**: ai còn hàng ở step 719 và bán được = ăn tiền miễn phí (giá đã
   được town consumption đẩy lên hết ngày). Majkel thắng match2 bằng 1 order; Majkel thua match1
   vì hết hàng (chỉ còn 6 WHEAT + 1 FERT = +$260 vs +$1,405 của ymg).
2. **Giữ hay bán phụ thuộc town-recovery**: item có nhiều shop hút (STRA 25 units/ngày recovery)
   → giữ càng lâu giá càng cao; item không shop (MELON chỉ town center) → phải bán hết ở cửa sổ
   đỉnh đầu (d10-14 @240), giữ là leak.
3. **Sản lượng cuối trận = hàm của (a) cây đang đẻ, (b) shed, (c) hands**: ymg thắng d29 vì
   39 HARVEST vs 33 (không cắt hire) + cây 2-ngày chín đúng d28-29 + auto-drop 23h cho shed đầy.
4. **I0 = 10,000 là vạch bán trước hay chết sau**: trước khi tổng supply 2 bên vượt I0, giá còn
   trên base (premium); sau khi vượt, WOOL/MILK/MELON rơi kiểu sq/linear rất đau (match2: MILK
   −74% base). Bán vào strength TRƯỚC ngưỡng, giữ qua ngưỡng chỉ dành cho item town hút mạnh.
5. **Động vật = máy 2 tầng**: sản phẩm (EGG/MILK/WOOL) + FERTILIZER byproduct ($11,514 match2
   từ 179 units bán + 162 bón ×2-yield cho STRA). CARE từ ngày 0 để tích care-bonus (+1 yield
   mỗi ngày fed+cared).

---

## 3. KIẾN TRÚC V19 "REAPER"

```
v19.py  (single-file packaged khi nộp Kaggle — trap #1)
  └── exec v18.py nguyên văn (byte-string, sha256-verify)   ← nền không sửa
        └── exec V43 nguyên văn (parent, farm plan + tape)   ← không sửa
  + LỚP A: MARKET TIMING LAYER  (chỉ đụng market list — rủi ro thấp nhất)
  + LỚP B: BREADTH LAYER        (đụng route/animal qua hook có kiểm soát)
  + LỚP C: TELEMETRY & AUDIT    (đo lường per-game)
```

Nguyên tắc bảo toàn (kế thừa v18): **mọi can thiệp phải "provably-inert" khi điều kiện không
khớp** (fingerprint / mô phỏng lockstep solo+pair / fallback nguyên trạng). Farm plan V43 đã
chứng 128-0 — chỉ được can thiệp qua 3 cửa: (1) market list post-processing, (2) monkey-patch
biến/hàm trong `_PARENT_NS` theo pattern HORIZON-24 đã chứng minh, (3) **route-router bias**
(dùng chính máy móc route của parent, không tiêm action trực tiếp).

### 3.1 Lớp A — Market Timing Layer (6 module, ~150 dòng trong wrapper)

#### A1 · ENDGAME LIQUIDATION SCHEDULER ★ impact lớn nhất (+$5,000-8,000/game kỳ vọng)
- **Cơ chế**:
  - Từ step 712 (h 20 d29): tắt mọi BUY (kể cả feed/seed), chỉ còn SELL.
  - Steps 712-718: xả TỪNG PHẦN các item theo thứ tự **recovery-score tăng dần**
    (recovery = town_đơn_vị/ngày × giá hiện tại; WHEAT/FERT/MILK/WOOL/TOMATO/CARROT trước),
    giữ lại **đúng 1 anchor item** = argmax(recovery) (gần như luôn là STRAWBERRY).
  - Step 719: **1 order duy nhất** `["SELL", anchor, all_remaining]` + các order lẻ của item
    khác còn kẹt. Chunking: max 10 order/turn, mỗi order 1 item.
  - Shed-cap pipeline d29: xen kẽ sell → (auto-drop 23h đã đổ sẵn) → không cần DROP; nếu
    tồn kho > 100 + yields-trên-cây → bắt đầu xả sớm hơn (tính `expected_final_throughput`).
- **Override trên v18**: `advance_sales` hiện skip `step ≥ 718` — v19 thay bằng scheduler này.
- **Evidence**: match2 +$7,258 (42 STRA @173, giá đi 175→186 trong ngày chờ); match1 ymg +$2,615
  ngay s697 nhờ shed đầy từ auto-drop 23h; Majkel match1 thua vì hết hàng s719.
- **Rủi ro & gate**: giá anchor có thể bị đối thủ dump trước (xem G3 stress-clone early-dumper);
  mô phỏng lockstep như frontload trước khi phát hành order thật.

#### A2 · TROUGH THROTTLE (price-gated sell rate)
- **Cơ chế**: mỗi item track đỉnh giá rolling-14-ngày. Nếu `price < 0.85 × peak` hoặc `price <
  base` → giới hạn SELL item đó còn 2-4 units/step (chỉ đủ giữ shed ≤ 100 và không để yields
  tràn); chờ giá hồi ≥ 0.85×peak → mở full. Shed là bể chứa, không phải kho vĩnh viễn.
- **Evidence**: Majkel match2 +$4,757 (giữ 65 STRA qua đáy 84 → bán 104-186); ymg match1 thua
  $6-7K vì dump 120u STRA @44.8 trung bình.
- **Tương tác**: active cùng A1 — trong d29 throttle TẮT (cái chuông đã đánh thì xả hết).

#### A3 · IMPACT-AWARE ORDERING (nâng cấp frontload — merge MD1)
- Tách group "non-wash SELL" của frontload thành `premium-first` (MELON/STRA/MILK/WOOL/EGG/
  CARROT/TOMATO) và `wheat-fert-cuối-cùng`. Không front-run chính input của đối thủ bằng giá
  WHEAT/FERT rẻ (bằng chứng Rayk C71 31-9).

#### A4 · STRICT DEBT INVARIANT (merge MD3)
- `advance_sales` + A1/A2 chỉ được **di chuyển doanh thu trong thời gian**, không tạo thêm:
  per-item ledger `sold_early[item]`; lệnh tape gốc của item trừ đúng lượng đã bán sớm. Chống
  oversell khi shed dư (cap-semantics của jaxa623 có thể bán THÊM thay vì chỉ dời).

#### A5 · FEED-BUY INDEX-0 + EARLY PRICE LIFT (merge MD4 + match2 #10)
- Day ≤ 6: nếu tape có BUY WHEAT (feed) → hoist lên slot 0 (bằng chứng 173-7). Song song đó,
  việc mua 178 units feed d0-9 tự nâng giá WHEAT 25→37 — crop WHEAT của mình sau đó bán +49%
  base. Giữ mô phỏng lockstep.

#### A6 · I0 SUPPLY TRACKER + SLOPE-AWARE CHUNKING
- Track `cumulative_supply[item]` (mình + đối thủ, từ market inventory delta trừ town-drain).
- Item `above_func ∈ {sq, linear}` (WOOL/MILK/MELON/STRAWBERRY... MELON sq, WOOL sq, MILK linear,
  STRA linear-above nhưng town hút mạnh): **bán hết trước khi tổng supply chạm I0** (sell-into-
  strength). Item `sqrt/log` + town hút (CARROT/WHEAT/EGG): chunk lớn an toàn.
- MELON special: không shop nào hút (chỉ town center) → 100% bán cửa sổ đỉnh d10-14, cấm giữ.

### 3.2 Lớp B — Breadth Layer (5 module — can thiệp có kiểm soát)

#### B1 · GOOSE/EGG MONOPOLY DETECTOR ★ breadh lớn nhất (Δ +$10,926 trong 1 trận)
- **Detector** (rẻ, market-only): EGG price flat trong [base × 1.0, base × 1.08] liên tục ≥ 5
  ngày + không thấy SELL EGG của đối thủ (inventory EGG không tăng khi mình theo dõi) + ≥ 1 shop
  EGG (BAKERY/BRUNCH) đã mở hoặc sắp mở → **mua 4-6 GOOSE trải d0-9**.
- **Cơ chế can thiệp**: GOOSE mua qua market list (wrapper append `BUY_ANIMAL` — thuần market
  order). Vấn đề PLACE/CARE/FEED: dùng **route-router bias** — patch router chọn route có nhánh
  EGG/COOP khi detector cháy (parent V43 đã có hạ tầng route + 64 cặp shop + unit plan đầy đủ
  cho mọi route — tận dụng thay vì tiêm action). Nếu route EGG không tồn tại trong tape cho cặp
  shop hiện tại → fallback: chỉ mua khi self-sim xác nhận kế hoạch PLACE khả thi từ unit rảnh.
- **Feed**: GOOSE ăn WHEAT (feed overhead đã tính trong pricing T −30%); đảm bảo A5 mua đủ.

#### B2 · SHOP-DRIVEN ANIMAL MIX + FEED INVARIANT
- Công thức mix: `n_target[animal] ∝ (shop_instances[product] − opponent_supply_estimate) ×
  price_margin`. Match1: EGG 3 shop 0 đối thủ → GOOSE; MILK 3 shop nhưng đối thủ 10 COW → không
  thêm COW (Majkel vẫn mua = sai lệnh −$2K).
- **FEED INVARIANT**: mọi con phải được feed mỗi ngày đến d27 (`consecutive_unfed ≥ 2` = escape;
  match1 Majkel mất 7 con = −$1-1.5K). **FEED-CUTOFF d28**: dừng feed, bán nốt WHEAT @35 thay vì
  đổi thành milk $1-3, chấp nhận escape (động vật không thể hiện tiền ở d29).

#### B3 · CROP-MIX: STRA-ANCHOR + SHOP-COUNT FILLER
- Anchor: STRAWBERRY max cây sống (~25 gói, mỗi gói ~$1,500 revenue với fertilizer, ROI 11.9x).
- Filler theo công thức: `argmax(shops × price_margin / (seed_cost × cycle_days))` — match2 có
  PET_CAFE d21 + base 35 + cycle 2 ngày → CARROT factory (125 gói từ d11 → $16,068, ROI 6.4x);
  match1 có 7 WHEAT-shops → WHEAT-filler đúng.
- Giữ-alive: tưới tuyệt đối để ongoing cây sống hết vòng đời (~d26); 8 weeds d28 của DSM =
  mất production cuối. Kỷ luật: WATER count ≥ plants count mỗi ngày.

#### B4 · CROP-MATURITY SCHEDULING d26-27
- Plant WHEAT/CARROT (first-yield 2 ngày) vào d26-27 để max-yield chín đúng d28-29 — inventory
  "trên cây" là kho thứ hai, 23h auto-drop vào shed rồi d29 bán. TOMATO ongoing + fertilizer
  tiếp tục đẻ trong d29 (ymg bán 18 TOMA ngày cuối match1).

#### B5 · FERTILIZER ALLOCATION + ANIMALS-AS-FERT-MACHINES
- Ưu tiên bón STRA/TOMA (ongoing, ×2 yield khi tưới): match2 STRA đạt 7.84 units/cây ≈ max 8.
  CARROT không bón (đúng — seed rẻ). Động vật là nguồn phân kép: CARE từ d0 (care-bonus +1
  yield/ngày fed+cared), COLLECT_FERTILIZER đều đặn.

### 3.3 Lớp C — Telemetry, Audit, Ops

- **C1**: reset TELEMETRY mỗi game (hiện cộng dồn cross-episode — bug của v18 wrapper); thêm
  counter per-module (a1_dump_value, a2_throttle_saved, b1_egg_rev...).
- **C2**: endgame stranding audit — shed + yields-trên-cây còn kẹt tại step 719 phải < $300
  (match2 Majkel = 0 stranded; destbreso benchmark cho thấy agent xấu kẹt $442).
- **C3**: hands endgame — **không cắt hire d27-29** (cuộc chiến d29 là cuộc chiến đơn vị hành
  động: ymg 39 vs 33 HARVEST). Land threshold-trigger: mua khi `cash ≥ price + $150` buffer,
  không spam dead-order; **SE KHÔNG BAO GIỜ** (âm EV: +25 ô cần +$377-665/ngày fib-hands).

---

## 4. THỨ TỰ TRIỂN KHAI & ACCEPTANCE

### Phase 1 — "v19-alpha" (chỉ Lớp A: A1, A2, A4) — 2-3 ngày
1. Fork v18.py → v19.py giữ nguyên wrapper pattern (exec + sha256). A1/A2/A4 nằm trong
   post-processing market list, mở rộng `advance_sales` (xóa skip ≥718, thêm scheduler).
2. T1: 24 dev-seed × 2 ghế vs {v18, ahmedv45} (runner ~6-8s/trận).
3. T3 sớm: 64 worlds bootstrap paired margins vs v18 — cổng G1.
4. Kỳ vọng: A1 +$2,000-5,000, A2 +$800-1,500. Nếu CI chạm 0 → gỡ module lỗi, giữ phần còn lại.

### Phase 2 — "v19-beta" (+ A3, A5, A6, B3-route bias) 
5. A3/A5/A6 vào frontload/advance (mô phỏng lockstep bắt buộc). B3 làm qua router-bias trước.
6. Stress-clone library mở rộng: `early-dumper` (counter A1 — dump anchor sớm ép ta giữ đồ vô
   giá trị), `egg-racer` (counter B1 — đua GOOSE), `throttle-copy` (counter A2).
7. 64 worlds lại + cổng G3.

### Phase 3 — "v19-rc" (+ B1, B2, B4, B5 khi route-bias không đủ)
8. Nếu B1 cần vượt ra ngoài route sẵn có: fork có kiểm soát kế hoạch động vật (đo riêng từng
   module bằng ablation: base / +B1 / +B1+B2...).
9. Cổng G2 (sparring) + G4 (official runner, **single-file packaged — KHÔNG wrapper**; audit
   bằng packaged main.py, giải phóng sys.modules giữa games).

### Bảng module — impact × rủi ro
| Module | Kỳ vọng $/game | Rủi ro | Nơi can thiệp |
|---|---|---|---|
| A1 Liquidation | +5,000-8,000 | thấp | market list + advance_sales |
| A2 Throttle | +800-1,500 | thấp | market list |
| A3 Ordering | +300-800 | thấp | frontload |
| A4 Debt invariant | chống −500-1,000 oversell | thấp | advance_sales state |
| A5 Feed index-0 | +300-600 | thấp | market list index 0 |
| A6 I0 tracker | +500-1,500 | trung bình | market list + tracker |
| B1 EGG monopoly | +1,500-4,000 (matchup-dependent) | trung bình-cao | market order + router bias |
| B2 Animal mix | +500-1,500 | trung bình | router bias + feed plan |
| B3 Crop filler | +700-2,000 | trung bình | router bias |
| B4 Maturity sched | +300-800 | trung bình | plan d26-27 |
| B5 Fert allocation | +300-800 | thấp | plan bón phân |

---

## 5. RỦI RO & ÂM TÍNH TUYỆT ĐỐI TRÁNH (kế thừa + bổ sung)

1. KHÔNG sửa trực tiếp v18/V43 source — chỉ wrapper/hook (mọi biến thể phải package single-file).
2. KHÔNG dùng wrapper khi nộp Kaggle (trap #1 đã mất +$167 giả); sys.modules cleanup (trap #2).
3. KHÔNG mua SE quadrant (âm EV — đối chiếu C93 0-40 trong meta research).
4. KHÔNG crash-dump vào dao rơi (DSM match2: −$4,474; ymg match1: −$6-7K).
5. KHÔNG cắt hire 3 ngày cuối; KHÔNG để động vật escape trước d28.
6. KHÔNG giữ MELON/WOOL/MILK qua ngưỡng I0 (sq/linear above-func).
7. KHÔNG spam dead-order (làm đầy 10 slot, DSM mất 2,709 slot).
8. Giữ nguyên mọi âm tính đã ghi trong `03_V18_ROADMAP.md` §4 (season funding attack, horizon
   36/48, EGG market-maker thuần (B1 khác: có động vật thật + shop hút), V44 escalation...).

---

## 6. FILE MAP & HẠ TẦNG

```
kaggle-research/top1/           ← toàn bộ intel trận đấu (README + 04A + 04B + match1/ match2/)
kagriculture/agents/v19.py     ← (tương lai) wrapper REAPER trên v18
kagriculture/agents/v18.py     ← nền byte-exact, KHÔNG đụng
kagriculture/arena/run_battle.py  ← T1 battery (CLI --a v19 --b v18 --seed N)
mini-services/arena-service/   ← UI arena (đã chạy, giữ nguyên)
bench/                         ← 64-worlds + bootstrap CI (tái dụng hạ tầng task 80)
```

Quy trình đo: T1 battery (24 seed) → stress-clone → 64 worlds bootstrap paired → official runner
audit packaged. Mọi gate phải đạt trước khi gọi v19 là "xong".

---

## 7. KẾT LUẬN

Hai trận của top-1 cho thấy meta đã dịch từ "farm plan tốt" sang **"kiểm soát 4 ngày cuối +
đa dạng nguồn thu"**. v18 là nền micro-timing hoàn hảo nhưng trắng tay ở đúng 2 chiều đó.
v19 REAPER = v18 + 11 module (6 market-timing + 5 breadth) với mục tiêu định lượng G1-G5:
**mean margin ≥ +$2,500 vs v18 trên 64 worlds, CI-95% > +$1,000, worst world ≥ −$1,500** —
đó là "thắng cách xa" bằng tiền, không phải bằng cảm giác.
