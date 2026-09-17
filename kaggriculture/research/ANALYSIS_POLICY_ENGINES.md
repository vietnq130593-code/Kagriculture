# ANALYSIS: POLICY AGENTS + ECONOMIC ENGINES (Task 74-e)

> Phân tích 8 notebook Kaggle (kaggriculture) — policy/scheduler, labor, feed, tie-break, route, economics.
> Ngày: 2026-09-13 · Agent: research-subagent (Task 74-e) · Engine pin: kaggle-environments 1.32.7

---

## 0. PHÁT HIỆN LỚN NHẤT: TOÀN BỘ TOP-META LÀ MỘT GIA ĐÌNH — CHUỖI PHIÊN BẢN V36→V39

Tất cả các agent lớn trong 8 notebook (kèm aurax local) **dùng CHUNG một bộ tape 719 turn × 12 route patches**
(payload giải nén md5 `63dfed8689c2`, base_len=719, patches=12 — kiểm chứng trực tiếp). Khác biệt chỉ nằm ở
**lớp engine overlay** chồng lên tape. Chuỗi phiên bản xác định được bằng diff byte-identical:

| Phiên bản | Notebook công khai | File local trùng khớp | Dòng |
|---|---|---|---|
| **V36** "Guarded Four Turn Sales" | upstream của pilkwang | `unpacked/pilkwang__upstream.py` | 2090 |
| **V37** "More Yield, Smarter Labor" | ahmedberatozer (103v) | **= `kme3.py`** (main.py byte-identical, MD5 55579a72) | 2355 |
| **V38** "Smarter Feed, Stronger Margins" | ahmedberatozer (88v) | **= `kme3v10.py`** = reyhanksatria "Dynamic Route" (MD5 4593a884) | 2625 |
| **V39** (mới) | guruprasaathas111 "Master Engine V3" (317KB, 72v) | **KHÔNG trùng** ai trong registry — = kme3v10 + 3 layer mới | 2963 |
| v31-branch "shop-router-reactive-v4" | aurax7 | `aurax.py` (MD5 8230b5a9) — nhánh song song | 2766 |

**TRẢ LỜI CÂU HỎI GURUPRASAATHAS**: notebook "kaggriculture-master-engine-v3" 317KB vừa tải = **V39** —
tức kme3v10 (V38) + 3 lớp mới **R88 + R95 + R97** (chi tiết mục 8). Notebook slug "V3" nhưng md tự gọi là
"Master Engine V5 — Unified Winning System" (claim 95.1% win rate, +17.5M net margin trên test field riêng).
Task 56 (285KB) hồi đó chứa V37; Task 66 (299KB) chứa V38 → notebook này được **tác giả update liên tục**,
chứ không phải file mới lạ họ khác.

---

## 1. BẢNG SO SÁNH TỔNG QUAN 8 NOTEBOOK

| Notebook (votes) | Loại | Kiến trúc | Cơ chế riêng nổi bật | Transfer → v15 |
|---|---|---|---|---|
| pilkwang structured-economic-policy (106) | Agent (wrapper) | V36 frozen upstream + monkey-patch `_v233_eligible` | **Scenario-admission gate** cho dự án 6 cừu SE (day-12), 2 kịch bản stress, worst-case surplus ≥ 0 mới cho phép | MED-HIGH |
| ahmedberatozer more-yield (103) | Agent | = **kme3** (V37) | Finite crop fertilization projects (R51 input planner EXP182), guarded warehouse sales, shared tomato-worker assignment (R53) | ĐÃ CÓ |
| ahmedberatozer v38 smarter-feed (88) | Agent | = **kme3v10** (V38) | Feed-skip theo giá trị biên, fertilizer-sale có reserve, R51 beam-search w8×d8, R62 spawn, R68 joint, R70/R79 fert adaptive | ĐÃ CÓ |
| reyhanksatria dynamic-route (78) | Agent | **= kme3v10 byte-identical** (re-post) | Không có gì mới — cùng file MD5 | NONE |
| georgymamarin visualized (98) | Economics | Visualization + starter bot | Bảng số liệu kinh tế crop/animal/market đầy đủ (mục 7) | DATA |
| andrewsokolovsky breaking-the-tie (73) | Pipeline + Agent | **5-expert multiplexer** + imitation learning (BC + DAgger) | **Tie-break**: detect đối thủ tiêu ≥$100 tại step 217 → bật overlay front-run; anti-mirror switch ở step 1; MLP router học từ counterfactual W/L/T | HIGH |
| lynnsakurai farming-score-v3 (72) | Agent | 2-route tape thuần + budget guard | Route 1 iff BAKERY+FERT≤10232 / PET_CAFE+rival≤64 tiles; **budget guard 72-turn** emergency-sell | LOW (đã A/B fail) |
| guruprasaathas master-engine-v3 (72) | Agent | = **V39** = kme3v10 + 3 layer | **R88** feed-bonus-cost horizon, **R95** wheat grain reserve 49-turn, **R97** supply guard chặn bán lúa phá kế hoạch pickup | HIGH |

---

## 2. pilkwang — "Structured Economic Policy" (106 votes)

**Cấu trúc**: submission tar.gz có 4 file: `main.py` (wrapper 114 dòng) + `market_primitives.py` (383 dòng, thư
viện market thuần) + `sheep_admission.py` (277 dòng, cổng đầu tư) + `upstream.py` (V36 frozen, SHA-checked).
Wrapper monkey-patch `_v233_eligible` (quyết định xây paddock 6 cừu SE của lineage) bằng cổng `evaluate_admission`;
arm "A" = bỏ qua gate, arm "B" (notebook này) = gate hoạt động. Dọn slot rỗng `[]` → `['SELL','WHEAT',0]`.

**Cổng admission (chạy đúng step 288/289 = day 12)**:
- 2 **kịch bản stress khai báo** (không phải prediction): (1) `visible_herds_frozen_shops` — đối thủ không
  nhận nuôi cừu, feed ×1.0; (2) `six_sheep_adoption_expensive_feed` — đối thủ nhận nuôi 6 cừu sau 3 ngày,
  feed ×1.25.
- Forward projection đầy đủ tới step 719: mô phỏng dawn-transition theo engine (SHEEP: first d6, mỗi 3 ngày,
  cap yield 6, `consecutive_unfed ≥ 2` = chết; care banks pending_care_bonus), depth market WOOL/WHEAT theo
  curve thật, rival bán trước (h18), project bán h20 với **delivery_fraction 0.75** (haircut 25%).
- Chi phí: land+sheep **$7000** cố định + **labor = Σ_{d=12..29} [fib(hires_d) + fib(hires_d+1)]** (chi phí
  Fibonacci HIRE đọc từ kế hoạch native của chính agent).
- Quyết định: `surplus = Δrevenue − Δfeed_cost − 7000 − labor`; **ALLOW iff min(surplus 2 kịch bản) ≥ 0**,
  ngoài ra DECLINE; lỗi/UNKNOWN → fallback parent (an toàn).

**market_primitives.py — thư viện "reserve-aware control"** (đáng chú ý nhất về kỹ thuật):
- `price_at()`: tái tạo **chính xác** công thức giá engine 1.32.7 (base, I0, T, below/above target, shapes
  linear/sq/sqrt/log/log10/**hinge** = `u + 8·max(0,u−1)²`), rounding + floor $1.
- `evaluate_sales()`: mô phỏng chuỗi SELL tuần tự — **quan trọng**: đơn bán ở giá floor $1 KHÔNG tăng
  market inventory ("engine burns price-floor sales") — chỉ quote > 1 mới +1 inventory.
- `prioritize_sales()`: xếp hạng thứ tự bán theo **explicit rival lead sale stress** (đối thủ bán trước X
  đơn vị thì mình mất bao nhiêu) — awareness front-run.
- `SaleLedger` + `reserve_advance`/`confirm_advance`/`repay_due_sales`: **sổ nợ đa lượt cho cửa sổ bán** —
  reserve đơn bán tương lai → confirm theo fill receipt thật → repay đúng lượt; unpaid debt không tự mất.

**Đánh giá**: đây là "policy" đúng nghĩa decision-theory (declared scenarios, worst-case gate) — pattern
**admission control cho đầu tư vốn** (V233 sheep paddock). Không phải agent mạnh hơn về chiến thuật.

---

## 3. ahmedberatozer "More Yield, Smarter Labor" (103 votes) — V37 = kme3

**Xác nhận**: main.py byte-identical với `kme3.py` (Task 56). Không cần đăng ký đối thủ mới.

**Cơ chế của V37 so với V36** (theo md + code):
- **Finite crop fertilization projects** (R51 input planner, EXP182): quy hoạch finite-harvest wheat/carrot —
  dự báo target theo tape continuation (WATER/HARVEST timeline từng ô), tính `gain` (yield cap − baseline),
  path tối ưu theo `gain×price/(arrival−now+1)`, max 2 workers.
- **Guarded warehouse sales**: bán khi có guard.
- **Shared tomato-worker assignments** (R53 labor assignment): gán worker dùng chung cho vụ cà chua.

**Số liệu công bố (md)**: vs V36 — field "old 512": 70.1% vs 53.1% (+87 win, 0 loss thêm); field độc lập
136 trận (17 team ≥2900): **81/55 cả hai bản — 0 net win, chỉ +865 mean margin** (gate qualification
FAILED — tác giả trung thực ghi nhận); field reacting 1856 trận: 96.23% vs 93.64%, +1180 margin.
→ Khớp luật L-của-chúng-ta: mirror-class cùng họ → ceiling là margin, không phải win-rate.

---

## 4. ahmedberatozer "V38 Smarter Feed, Stronger Margins" (88 votes) — V38 = kme3v10

**Xác nhận**: main.py byte-identical với `kme3v10.py` (Task 66) — và cũng là agent của reyhanksatria.
So với V37 (kme3), V38 thêm (đã ghi trong worklog Task 68): R51 greedy→**beam search w8×d8** (phạt
1.5×giáFERT×path), R62 deterministic HIRE spawn, R68 joint 3-mode plans, R70/R79 fert adaptive, R85/R86
economic overlay.

**Feed-skip rule (V38, phần "Smarter Feed")** — code `_r85_feed`:
- Window: day 10-28, giờ ≤ 21; chỉ xét thú `consecutive_unfed == 0` (an toàn đói ngay) VÀ ngày mai trong
  route có cơ hội feed khác (`_r86_next_feed`).
- Điều kiện GIỮ feed: `bonus × (giá_sản_phẩm + 5) × 1.25 ≥ giá WHEAT`; ngược lại → thay FEED bằng PASS.
- Với V38: `bonus = 1 + pending_care_bonus` (V39 sửa thành `_r88_feed_bonus_cost` — xem mục 8).

**Fertilizer-sale có bảo vệ** (`_r85_reserve`): reserve FERTILIZER backward-recurrence theo tape —
bảo toàn pickup + purchase kế hoạch + nhu cầu worker chuyên canh (needs_fertilizer), phần thừa mới bán.

**Số liệu công bố (md)**: vs V37 — 648 recorded: 73.61% vs 67.90%; 97 live cohort V37: **82.47% vs 64.95%**
(+17 win, 0 tie còn lại); 704 reacting: 86.51% points vs 88.49% (V38 hơn).

---

## 5. andrewsokolovsky "Breaking the Tie" (73 votes)

**Kiến trúc 2 tầng:**

**(a) Teacher V21-R1 = multiplexer 5 expert** (main.py 238 dòng, payload giải nén được):
- **_MOON** = "BL-MDgogo-10C4S-R0" / `Codex-Moon-V56-TomatoEgg-Adaptive` (166KB): consensus route tái
  tạo từ 12 public trace (8 Cow 6 Sheep? — "10C4S"), kèm: **clone-detection** (`_public_signature`,
  `_clone_distance`, ngưỡng ≤ 6), **preempt front-run** (bán trước đối thủ clone: PREEMPT_START=120 →
  STOP=680, fraction 1.0, batch ≤ 12, min future qty 4, premium items STRAWBERRY/MELON/MILK/WOOL),
  **adaptive horizon** (đo sale pattern đối thủ, max 6 lượt, evidence 1.50, decay 0.999), sale-shift debt
  ledger (`_repay_shift`), weed repair (replay 8 bước), impact-scoring xếp slot bán, terminal liquidation,
  counter riêng cho họ "R5" (fraction 0.5) và họ "MD" (fraction 2.0 + room guard + feed rescue + room evac),
  tomato pairing (target 3), egg late-pair khi đối thủ không có goose.
- **_MUTOY** = tape "ScoreBand-2200-2299-Rank368" (247 dòng) + weed repair + front-run đơn giản.
- **_MUNIB** = tape "ScoreBand-2600-2699-Rank58" (247 dòng), nạp 2 lần: BASE (FR items = ()) và
  **FR variant** (FR_ITEMS = WOOL/MILK/MELON/STRAWBERRY — bán sớm 1 lượt khi town demand active, có
  pickup-reserve + repay).

**Router (heuristic)**:
- Step 0: gọi tất cả (khởi tạo state), trả moon.
- **Step 1, anti-mirror detector**: đối thủ `hires_today ≥ 4` VÀ `money ≤ 20` (vết mở màn của cả họ
  KaggressurE — HIRE×5 + mua lúa) → khóa route "mutoy" (có thể defer tới step 144 rồi quyết theo 2 shop
  đầu + money gate).
- Route lock khi **first_action_divergence** (moon ≠ munib): step < 200 → "munib"; regime shop đặc biệt
  (BAKERY×3, PET_CAFE+ICE_CREAM×2) → munib; còn lại → "moon".
- **TIE-BREAK CHÍNH (câu trả lời câu hỏi 2)**: theo dõi `opponent_money` mỗi lượt; **nếu tại đúng step 217
  (day 9, giờ 5 — ngay cửa sổ cattle-switch V231 216-227) đối thủ tiêu ≥ $100 so với lượt trước** (dấu hiệu
  mua thú/đầu tư lớn — match với mirror đang copy nhau) → bật `_MARKET_OVERLAY` **vĩnh viễn**. Từ đó hành
  động = `moon_action + Δ(munib_base → munib_FR)` — tức **áp delta front-run 4 món premium lên agent chính**:
  bán sớm hơn những gì base định giá, giật giá trước khi supply đối thủ đổ vào. Vì Elo chỉ tính W/L/T,
  một trận mirror khác version sẽ hòa → overlay này "bẻ tie" về phía mình đúng lúc đối thủ commit vốn.
- `_apply_market_delta`: chỉ cộng/trừ đúng SELL theo item lên action gốc, giữ ≤ 10 slot — surgical.

**(b) Notebook = ML pipeline "V4 Real Imitation + DAgger"**:
- BC (behavioral cloning) router quyết định từ teacher V21-R1 trên trajectory đầy đủ.
- **Counterfactual oracle**: tại mỗi checkpoint, cặp thế giới giống hệt nhau cho chạy tiếp bởi 5 expert
  (V21/Moon/Mutoy/Munib-base/Munib-front) → nhãn theo **final W/L/T** (đúng objective Elo!).
- DAgger: policy tự sinh state distribution → gán nhãn lại bởi oracle; **recovery imitation**: nửa số
  state oracle sinh sau khi cố tình bỏ 1 action (missed farmer/hand/market) trước checkpoint.
- RouterNet = MLP 3 tầng (Linear d→h1→h2→5) CPU, AdamW, class-weight, clip norm 5.
- Calibration ngưỡng + **paired holdout** trên seed rời; **promotion gate**: chỉ viết `submission.tar.gz`
  nếu policy học thực sự rời route V21 trên game mới VÀ không thua trên paired holdout — nếu fail thì
  KHÔNG tạo submission (chống nộp nhầm teacher).

**Đánh giá**: kỹ thuật "break the tie" = (i) detector spend-step-217 + front-run delta overlay (rẻ, surgical,
dễ port); (ii) học router bằng counterfactual W/L/T oracle (đắt — hàng nghìn rollout). Notebook chỉ chứa
teacher; bản học chỉ tồn tại khi promotion pass.

---

## 6. reyhanksatria "Dynamic Route Agent" (78 votes)

**Kết luận 1 dòng**: file main.py giải nén ra **MD5 4593a884... = kme3v10.py byte-identical** — notebook này
chỉ là re-post/copy của V38 "Smarter Feed Stronger Margins" (đóng gói khác: Base85 đơn thuần). "Dynamic
route" = chính là chassis 12-route theo shop tại step 144 (+ route 2 endgame từ step 648) mà ta đã biết.
**Không có cơ chế mới, không cần đăng ký đối thủ.**

---

## 7. georgymamarin "Visualized: What Every Crop Pays" (98 votes)

Notebook phân tích/visual (agent kèm theo chỉ là "Carrot Crew" starter: 6 ô carrot quanh shed). **Tất cả số
liệu dưới đây tính lại trực tiếp từ engine 1.32.7** (khớp notebook):

**Bảng giá trị cây trồng (giá base, tưới hàng ngày, không fertilize):**

| Crop | Seed | Tile-days | Units | Giá base | Doanh thu | Lợi nhuận | **$/tile-day** |
|---|---|---|---|---|---|---|---|
| MELON | $80 | 10 | 6 | $250 | $1500 | $1420 | **142.0** |
| CARROT | $20 | 3 | 3 | $35 | $105 | $85 | **28.3** |
| STRAWBERRY | $100 | 16 | 4 | $120 | $480 | $380 | **23.8** |
| WHEAT | $10 | 4 | 4 | $25 | $100 | $90 | **22.5** |
| TOMATO | $50 | 11 | 4 | $60 | $240 | $190 | **17.3** |

- Yield caps: WHEAT 6 (d2-4, cần FERT mới chạm max), CARROT 4 (d2-3), TOMATO ongoing 4 (first d8, mỗi 1d),
  STRAWBERRY ongoing 4 (first d10, mỗi 2d), MELON 6 (d10-12 — max chỉ cần nước).
- 1 cửa sổ bonus nước = nửa sau `max_yield_day` → +1/ngày (+2 nếu fert), cap bó trước max_yield_day
  (melon xong ngày 10, không phải 12).

**Vật nuôi (mua d0, giá base, feed = giá base WHEAT $25):**

| Con | Cost | Sản phẩm | First/interval/cap | Cuối mùa CARED | Fed-only | Breakeven |
|---|---|---|---|---|---|---|
| SHEEP | $500 | WOOL | d6 / 3d / 6 | **+$5,575** | +$375 | d6 |
| COW | $400 | MILK | d8 / 2d / 6 | **+$4,635** | +$635 | d8 |
| GOOSE | $300 | EGG | d4 / 1d / 4 | **+$1,675** | +$275 | d7 |

→ **CARE đáng giá 5-15×** (care làm pending_care_bonus cộng vào lần sản xuất kế tiếp).

**Độ sâu crash ($1 floor) — bao nhiêu unit net-sold thì chạm đáy:**

| Item | $1 floor sau | Giá +50u | +100u | +400u |
|---|---|---|---|---|
| WOOL | **59u** | $55 | $1 | $1 |
| STRAWBERRY | **62u** | $24 | $1 | $1 |
| MILK | **76u** | $55 | $1 | $1 |
| MELON | **158u** | $225 | $150 | $1 |
| FERTILIZER | 493u | $90 | $80 | $20 |
| TOMATO | 529u | $42 | $35 | $9 |
| CARROT | 842u | $27 | $23 | $12 |
| WHEAT | không chạm | $22 | $21 | $20 |
| EGG | không chạm | $43 | $42 | $40 |

- 100 melon bán một lượt = **87%** giá trị quote đầu ($21,721/$25,000).
- MARKET_PARAMS đầy đủ: base WHEAT 25/CARROT 35/TOMATO 60/STRAW 120/MELON 250/EGG 50/MILK 160/WOOL 200/FERT
  100; I0=10000; T: WHEAT 400, CARROT 450, TOMATO 200, STRAW 100, MELON 300, EGG 332, MILK 122, WOOL 105,
  FERT 200; above_func: WHEAT/EGG log 0.2, CARROT sqrt 0.7, TOMATO sqrt 0.6, STRAW **linear 1.6**, MILK
  **linear 1.6**, MELON sq 3.6, WOOL **sq 3.2**, FERT linear 0.4.
- HIRE Fibonacci: 1,1,2,3,5,8,13,21,34,55 → 5 tay $12/ngày, 10 tay $143/ngày; C(12)=376, C(13)=609.
- LAND: NE $1000, SW $2000, SE $4000.
- **Town demand**: town centre 1 unit/sản phẩm (trừ FERT)/ngày = 30/mùa; shop k mở ngày 3(k+1), mỗi shop
  mua 2/tick nếu 1 sản phẩm, 1/tick nếu nhiều (tick mỗi 4h = 6 lần/ngày), shop draw **with replacement**.
- Cảnh báo hire: 3 tay hire cùng lúc rồi về HOME đi trên land LOCKED mất 69 worker-turn đầu ngày.

**Ý nghĩa cho v15**: WOOL/STRAW/MILK crash sau ~60-76 unit → luật Cournot route-0 (L32) có số lượng cụ thể;
WHEAT/EGG gần như không crash (log) → an toàn để dump/big-sell; C(13)−C(12)=$233 → tay thứ 13 chỉ đáng
từ day 20+ khi đủ việc (đúng logic V39 md).

---

## 8. guruprasaathas111 "Master Engine V3" 317KB (72 votes) — **V39 = kme3v10 + R88/R95/R97**

**Xác định phiên bản (trả lời câu hỏi 8)**: KHÔNG trùng MD5 kme3/kme3v10/aurax. Sau khi strip payload
(giải nén ra **cùng tape** 63dfed...), diff cho thấy main agent = **V38 (kme3v10) + chính xác 3 layer mới +
1 edit 1 dòng**. Notebook packaging in `V39 started`, manifest `v39`, archive `submission_competitive_v39.tar.gz`.

**3 layer mới (mọi thứ còn lại giữ nguyên):**

1. **R88 — feed-bonus-cost đúng (EXP219)** — sửa dòng `_r85_feed`: `bonus = 1+max(0,pending)` →
   `bonus = _r88_feed_bonus_cost(tile, day)`:
   - `pending_care_bonus` chỉ tính vào ngày mai **là dawn sản xuất** (`tomorrow ≥ first` và
     `(tomorrow−first) % interval == 0`) — ngoài dawn sản xuất thì bonus "cất kho" không mất (banked).
   - Charge bảo thủ 1 CARE cho feed hôm nay; **nhưng care = 0 nếu dawn sản xuất kế tiếp > ngày 29**
     (hết game) → không feed vô ích cuối mùa.
   - Animal days: GOOSE (4,1), COW (8,2), SHEEP (6,3).
2. **R95 — grain reserve hai ngày (EXP226)**: chỉ chạy day 10-11; nếu action có BUY_PRODUCT WHEAT thuần
   (không kèm SELL WHEAT cùng lượt): reserve = **6 (buffer) + mọi PICKUP WHEAT + SELL WHEAT trong 49 turn
   tới theo tape** + nếu ≥ 2 YARN_STORE: **+6 cừu/ngày cho mọi ngày ≥ 12 trong cửa sổ** (cam kết feed
   paddock SE). Trim lượng mua vượt reserve; telemetry đếm trim turns/units.
3. **R97 — supply guard (EXP231)**: chặn/khuếch đại để **bảo vệ input vật lý cho kế hoạch pickup 2 lượt
   tới**: mô phỏng stock shed + overnight overflow (đêm h23 chỉ farmer ở (4,4)), nếu SELL WHEAT làm thiếu
   WHEAT cho PICKUP kế tiếp → giảm bán đúng chỗ thiếu / tăng BUY đè lên / thêm slot mua; chỉ khi budget
   pass (`_r97_budget` — giá mua mô phỏng market impact `_r37_market_price(inventory−2000)`, HIRE theo
   fib `_v219_fib`, không tính tiền bán trong lượt); mọi thay đổi phải "safe" (không phá buy đã có, không
   tăng overflow). Chỉ chạy 144 ≤ step < 695.

**Nhận định**: cả 3 layer đều là **hoàn thiện kinh tế lúa/feed** — hướng trực tiếp cạnh tranh R85/feed-skip
và front_run grain của v14/v15. V39 là đối thủ mạnh nhất họ lineage đã công khai → **nên đăng ký benchmark**.
Lưu ý R97 guard chỉ active 144-695 (sau phase mở màn) và R95 chỉ 2 ngày — behavior khác v15 chủ yếu giữa game.

---

## 9. lynnsakurai "Farming Score V3 Replay Revised" (72 votes)

- Agent "three-day shop router" thuần Python: 2 route tape (chỉ khác nhau step 360-431), chọn ở **step 360**:
  route 1 ⟺ (shop đầu = BAKERY VÀ FERT inventory ≤ 10232.5) HOẶC (shop đầu = PET_CAFE VÀ rival ≤ 64.5 ô trồng).
- **Budget guard mỗi 72 turn** (đầu mỗi khối 3 ngày): forward-simulate 72 turn của tape → purchase budget
  (HIRE fib + LAND 1000/2000/4000 + seed + BUY WHEAT/FERT theo giá hiện tại + animal 300/400/500) + starting
  requirement (FEED/FERTILIZE/PLACE balances); nếu cash (money + planned sales) thiếu → **emergency-sell
  surplus** theo giá giảm dần, bảo vệ đúng lượng "starting requirement − đang mang tay".
- Nhận xét: đây chính là dạng "budget_guard" mà Task 69 A/B trên v14: **0/8, −$17.834 — thảm họa** (với
  agent của ta). Lynnsakurai dùng nó ở mức phòng thủ cho tape cứng — hợp lý cho tape thuần, không phải cho ta.

---

## 10. TRANSFER VALUE CHO v15/v16 (xếp hạng)

| # | Cơ chế | Nguồn | Rank | Ghi chú triển khai |
|---|---|---|---|---|
| 1 | **Đăng ký đối thủ kme3v39** (kme3v10 + R88/R95/R97) | guruprasaathas V39 | **HIGH** | Copy file vào arena, chạy battery 10 trận × seeds mới vs v15 — kiểm tra gap còn ≥ +$3k không |
| 2 | **R88 horizon-check cho feed**: care/feed = 0 khi dawn sản xuất kế tiếp > ngày 29 | V39 EXP219 | **HIGH** | Surgical 1 hàm (~15 dòng) đè lên `_r85_feed`-style của v15: tiết kiệm lúa cuối mùa, zero-risk theo cơ chế |
| 3 | **Tie-break overlay kiểu andrew**: theo dõi opponent_money; nếu tại step ~217 đối thủ tiêu ≥ $100 → bật permanently overlay delta front-run (bán sớm WOOL/MILK/MELON/STRAW khi town demand active, có repay ledger) | andrew V21-R1 | **HIGH** | v15 đã có front_run-sync nhưng KHÔNG có trigger spend-detector; test A/B riêng layer trigger |
| 4 | **Scenario-admission cho quyết định vốn** (pattern pilkwang): worst-case surplus gate ≥ 0 cho V233 sheep paddock bằng 2 kịch bản (rival adopts 6 sheep, feed ×1.25; delivery haircut 25%) | pilkwang | MED-HIGH | Chỉ áp nếu muốn nâng chất lượng quyết định V233; cần fib labor + $7000 cost model |
| 5 | **SaleLedger reserve/confirm/repay** (sổ nợ cửa sổ bán đa lượt, confirm theo fill thật) | pilkwang market_primitives | MEDIUM | Nâng độ chính xác cho front_run + clamp_sells của v14/v15 |
| 6 | **price_at() chuẩn + floor-burn semantics** (đơn floor $1 không tăng inventory) + hinge curve | pilkwang + engine | MEDIUM | Cải gap_waterfall/oracle probe: mô phỏng impact chính xác hơn |
| 7 | **Số liệu crash-depth** (WOOL 59u, STRAW 62, MILK 76, MELON 158; WHEAT/EGG ~không floor) | georgymamarin | MEDIUM (data) | Dùng cho cap sells/định lượng front-run; kiểm chứng clamp_sells hiện có |
| 8 | **R95 grain-reserve 49-turn** cho BUY WHEAT trim | V39 EXP226 | MEDIUM | Cẩn trọng: đã có budget_guard FAIL ở ta (L33) — nhưng R95 chỉ trim mua thừa, không bán; A/B bắt buộc |
| 9 | Anti-mirror switch step-1 (detect KaggressurE opening hires≥4+money≤20 → đổi route) | andrew | LOW-MED | Chỉ có ý nghĩa nếu ta có route thay thế tốt hơn — L32 cho thấy route đổi tự hại |
| 10 | ML router counterfactual W/L/T + DAgger | andrew | LOW | Đắt (hàng nghìn rollout), lợi thế không rõ vs rule-based của ta |
| 11 | Budget guard 72-turn | lynnsakurai | **LOW** | ĐÃ TEST Task 69: 0/8 −$17.8k với v14 — loại |
| 12 | Route 1 iff BAKERY/FERT≤10232 (step 360) | lynnsakurai | LOW | Tape của họ, không applicable |

**Kết luận guruprasaathas version** (câu 8 chính): 317KB = **V39** — một thế hệ SAU kme3v10 (=V38), thêm
đúng 3 layer (R88 feed-bonus horizon, R95 grain reserve, R97 supply guard) trên cùng bộ tape 63dfed...
→ hành vi giống kme3v10 ở mở màn/endgame, khác ở giữa game (day 10-11 + step 144-695). **Đề xuất main-agent:
đăng ký làm đối thủ thứ 5 ("kme3v39") và battery vs v15 trước khi quyết định v16.**

---

## Phụ lục: file giải nén để lại (nếu main-agent cần benchmark)

- `research/kaggle_dl/unpacked/guruprasaathas111_payload0.json` — tape (trùng kme3)
- `research/kaggle_dl/unpacked/pilkwang__{main,market_primitives,sheep_admission,upstream}.py`
- `research/kaggle_dl/unpacked/andrew__main.py` + `andrew__moon.py` + `andrew___mutoy.py` + `andrew___munib.py`
- `research/kaggle_dl/unpacked/reyhank__main.py` (= kme3v10), `lynnsakurai__main.py`
- (Xây V39 agent = copy kme3v10.py + 3 khối R88/R95/R97 từ file nguồn 317KB — đoạn code thuần, payload chung)
