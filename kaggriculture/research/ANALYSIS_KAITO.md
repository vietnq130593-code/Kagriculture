# PHÂN TÍCH HỌ KAITO FUKAMI (v20 / v21.1 / v27 / v43 / v48)

> Task 74-a — research-only. Ngày 13/9. Nguồn: 4 notebook `kaitofukami__*.py` trong
> `research/kaggle_dl/` (file `.py` = notebook đã convert; agent thật được nhúng base85+zlib
> bên trong, đã giải nén vào `research/kaito_extracted/` để đọc).
>
> **Kaito Fukami = #3 leaderboard 3133.9** (sau カワシギ 3179.7). Là tác giả có hệ
> validation nghiêm ngặt nhất trong mọi public notebook ta đã tải: chronological
> split, both-seat, medoid selection, strict-future holdout, artifact hash, self-play
> tie check. Điểm mấu chốt: **mọi con số trong title (159/160, 177/180, 103/128,
> 40/40, 39/46) đều là counterfactual replay vs đối thủ ĐÓNG BĂNG (open-loop)**,
> không phải live score — chính tác giả ghi rõ "policy-screening evidence, not a
> claim of exact live-LB reproduction".

---

## 0. TÓM TẮT ĐIỀU HÀNH (1 đoạn)

Cả họ Kaito = **tape 719 action lấy từ replay người chơi top (medoid) + các lớp
closed-loop MỎNG chêm lên**: WEED-slip repair (DIG→retry→replay ≤8 turn),
reorder/vét SELL theo impact, mirror-latch/clone-preempt (front-run 2 turn, max
10 unit, có sổ nợ "debt"), 1-NN "conditional memory" 30 prototype để đoán item
đối thủ sắp bán rồi kéo SELL trùng lên trước, terminal liquidation rọi cả shed
ở step 718. **Không có planner thật sự** — sản xuất (herd/crop/labor) 100% đi
lại băng; toàn bộ "thông minh" nằm ở (a) chọn route tốt từ meta hiện tại và
(b) micro-timing thị trường. Edge thật của họ = **route quality + kỷ luật
intervention tối thiểu** (đổi thứ tự, không thêm bớt SELL — trừ clone-preempt có
debt đảm bảo "chỉ dời thời gian, không thêm sản lượng").

---

## 1. BẢNG SO SÁNH 4 VERSION CHÍNH

| | **v20** (159/160) | **v21.1** (177/180) | **v43** (103/128) | **v48** (40/40 + 39/46) |
|---|---|---|---|---|
| **Size main.py** | 26.894 B | 428.598 B | 63.309 B | 107.008 B |
| **Route gốc** | medoid họ `sash` (ep 90049120), CŨ | medoid "Konstantin" hiện tại + 30 memory | ActiveMusyoku ep 96815867 | = v43 default + 5 nhánh |
| **Số route runtime** | 1 | 1 | 3 (default/yarn1/yarn2) | 6 (+yarn_fast/farm_fast/yarn_third/bakery_capital) |
| **Herd tape** | 8C/6S/0G | 8C/6S/0G | 11C/4S/0G | 11C/4S (yarn_fast: 6C/10S) |
| **Day-0** | BUILD_PASTURE + 3C/1S + hire2 | HIRE×5 + 2C/2S | 4S + HIRE2 + wheat4/melon7 seed | = v43 |
| **Crop mix tape** | MELON26/WHEAT68/STRAW41 seed | WHEAT92/MELON24/STRAW42 seed | WHEAT140/MELON11/STRAW41/CARROT20 | = v43 |
| **BUY_PRODUCT WHEAT** | 275 u | **980 u** | 105 u | 105 u |
| **HIRE** | 284 (~9,5/ngày, h0-2) | 277 (h0-2) | 282 (h0) | 282 (h0) |
| **Lớp market** | front-run reorder khi mirror-latch + terminal | **1-NN 30-mem reorder** + clamp shed + terminal | impact_score reorder + (EGG MM tắt) | clone-preempt debt h=2 + exposure_preempt FERT + terminal |
| **Mirror/anti-clone** | logistic 7-feature, threshold 0.8065, latch 48, release 8 turn lệch | 1-NN distance ≤48 (không identity) | Không (v44 mới thêm) | clone_distance ≤2 × 24 turn streak → latch từ step 48, active 160-700 |
| **WEED repair** | DIG→retry→replay 8 turn (actor-local) | idem | idem | idem (chấp nhận gọi muộn) |
| **Endgame** | step 718 bán sạch theo collision-score | idem | terminal_liquidation theo quote×qty | terminal rule="collision" |
| **Điểm mạnh đo được** | 8 loss→win, 0 win→loss (160 game Frontier) | 177/180 outer; margin 3.560→13.049 | worst-opponent 12,5%→50% | 40/40 floor + 39/46 top-10 |
| **Điểm yếu công khai** | route cũ (19/46 vs top-30 mới) | 46/51 post-cutoff = decay nhanh | PET_CAFE 16/26 | worst -26.535 trên top-10 |

**Điểm chung absolutely nhất quán qua 4 version:** (1) ordinary turn KHÔNG BAO GIỜ
tạo/xoá/đổi số lượng SELL — chỉ đổi thứ tự (invariant "change order, never
inventory"); (2) WEED repair actor-localbounded; (3) terminal step-718 liquidation;
(4) runtime không đọc identity/seed/episode/future action; (5) HIRE dồn giờ 0-2 đầu
ngày (workers bị sa thải cuối ngày — L36 của ta khớp).

---

## 2. EVOLUTION TIMELINE v18 → v48

```text
v18  40/53 Top-10 future holdout ......... cả 2 seat, complete-route control
v19  41/49 replication-to-control ........ medoid train-only + terminal control
v20  159/160 vs Frontier ................. + WEED-slip recovery (8L→0W)
                                            + mirror logistic latch (7 feature)
v21  65/67 live recorded ................. + order-only memory (public v21)
v21.1 177/180 fresh top-30 ............... + route refresh (Konstantin medoid)
                                            + 30 fit-only prototypes 1-NN reorder
     [route cũ rơi 19/46 → refresh 40-41/46: ROUTE là effect lớn nhất]
v22  market impact study ................. impact_score = q×(quote_now − quote_after)
v23  simulator/state encoder .............. route-switching + quantity MPC: BỊ LOẠI
                                            (seed-grouped holdout không tăng win)
v24  market maker (EGG round-trip) ........ 0 khác biệt → TẮT trong production
v26  87/90 live, 20/20 gần nhất .......... đường cong rating ≠ decay thật
v27  25/27 midgame meta reset ............ giữ nguyên HIRE4 opening, thay
                                            continuation từ step 161 (Ezzzzzekki)
     [26/30 top-30 cùng opening 1C/4S — edge nằm ở continuation]
v42  5-expert router + direct-value ...... router LUÔN abstain → fallback → LOẠI
v43  103/128 sparse shop hybrid .......... 3 route, 2 nhánh shop observable
                                            (first-YARN@88, second-YARN@153)
v44  gold floor 40/40 ................... + CloneSellPreemption (debt h=2, ≤10u)
v47  0/11 — THẢM HỌA .................... bug: 4 child stateful chạy trước
                                            decision point mỗi turn → exception
                                            → comprehension sụp → PASS 719 turn
                                            → mọi game kết thúc đúng 3.000
v48  40/40 + 39/46 + 97/140 top-30 ....... fix "đúng 1 child call/turn" + thêm
                                            yarn_fast (Kaileh57), farm_fast
                                            (taiseiu), bakery_capital (Cary Jin)
```

3 bài học hệ thống lớn của cả dòng họ:
- **Route refresh > thêm controller** (v21.1: route cũ 19/46 → route mới 40/46, trong khi mọi ablation market chỉ ±2-3 win).
- **Thêm nhánh phải rất hiếm và có observable event công khai** (v43: chỉ 2 shop event; v48: +3, mỗi cái có gate hẹp).
- **Sự phức tạp stateful + hosted timing = PASS-only disaster** (v47). v48 đưa "719 policy calls = 719 child calls" thành build invariant + smoke "first action non-PASS".

---

## 3. PHÂN TÍCH TỪNG NOTEBOOK (10 câu hỏi)

### 3.1 v20 — "159/160 vs Frontier | WEED-Slip Recovery" (26.894 B)

1. **ARCHITECTURE**: Tape thuần 719 action (`_ACTIONS`, base85+zlib) + 3 lớp mỏng:
   `_weed_repair_action` → `_hybrid_action` (mirror latch step-48 + front-run) →
   `_terminal_market` (step 718). Không planner.
2. **OPENING**: step 0 = `BUILD_PASTURE` + BUY 3 COW/1 SHEEP + 7 MELON seed + 10
   WHEAT seed + **BUY_PRODUCT WHEAT 17** + HIRE×2 → **KHÔNG** theo meta 1C/4S/HIRE4
   (route `sash` cũ). Mua thú tiếp d5-d11 → 8C/6S.
3. **FARM**: 8 COW + 6 SHEEP + 0 GOOSE; MELON 26 + WHEAT 68 + STRAW 41 seed; 275
   wheat mua thêm; 284 HIRE (~9,5/ngày, 195 lệnh ở giờ 0); 2 BUY_LAND; ≤13 hands.
4. **MARKET**: bán đầu ngày 2 (FERTILIZER); 1-3 SELL/turn; giờ bán rải h19-23 + h1;
   front-run = reorder SELL hiện có theo score
   `(1+opp_exposure)×glut_weight×price×log1p(qty)`, clamp bằng `_projected_shed`
   (cap 100, xét cả DROP/PLACE đang phát sinh).
5. **ANTI-CLONE/MIRROR**: logistic 7 feature (`log1p_board_distance −0.945`,
   `log1p_money_gap −1.462`, `near_equal_money +0.599`, `board_streak_96 −0.155`,
   `step_fraction +0.442`, `late_phase −0.026`, `exact_board −0.468`; intercept
   1.2457; threshold **0.8065** chọn cho 95% precision — holdout 94.90% @ 32.52%
   coverage). Latch 1 lần tại step≥48; mirror regime front-run khi latch còn
   hiệu lực, release sau 8 turn board lệch >2; open regime thì front-run liên tục.
   **Nghiên cứu nền tảng**: trong gate 24-turn near-equal-board, action trùng đối
   thủ tới 90.53%, market intent trùng 99.11% — tức "đối thủ giống hệt mình thì
   cùng định bán cùng lúc" → đẩy SELL lên trước là đúng.
6. **WEED**: transaction 3 pha actor-local: **DIG ngay** (khi PLANT/BUILD_PASTURE
   rơi vào ô WEED thấy được) → **retry ý định ở t+1** → replay MÀ CHỈ actor đó
   route action ≤8 turn (`_WEED_REPLAY_STEPS=8`) — market + actor khác không
   đụng. Ablation: 205-case panel 188→202, 108-case 102→108, fresh 160:
   151→159 (8 loss→win, 0 win→loss, 1 thua còn lại -945).
7. **ENDGAME**: `_terminal_market` step 718 — thay market bằng toàn bộ projected
   shed, xếp theo collision-score, cap 10 order.
8. **CƠ CHẾ MỚI vs v15**: bảng `_GLUT_WEIGHT` (MELON 3.6, WOOL 3.2, STRAW 2.0,
   MILK 2.0, EGG 1.5, TOMATO 1.3, còn lại 1.0); `_opponent_exposure` đọc tile
   công khai của đối thủ (crop yield_units + 1+yield của animal + fert flag);
   mô hình mirror logistic.
9. **KHAI THÁC**: route cũ decay 19/46 — nếu v15 gặp v20 trên Kaggle thì ưu tiên sản
   lượng + timing động là thắng; v20 không đổi số lượng bán, không biết plan lại
   khi bị disrupt.
10. **TRANSFER**: WEED repair vô nghĩa với planner như v15 (tự chữa mỗi turn) —
    rank LOW. Glut weight MED (prior xếp thứ tự bán khi va chạm). Mirror model
    LOW (ta có luật L38 knife-edge — và Kaito cũng tự thừa nhận mirror không
    exploit được deterministic copy).

### 3.2 v21.1 — "177/180 Fresh Top-30 | Conditional Memory" (428.598 B)

1. **ARCHITECTURE**: Tape route "Konstantin medoid" hiện tại + **30 prototype**
   fit-only (mỗi cái = 719 signature + 719 sales-set). "Conditional Memory" ở
   mức code = **1-nearest-neighbor mỗi turn**: tính
   `_signature_distance(opponent_farm, prototype.signatures[step])`, chọn min;
   nếu distance ≤ **48** → lấy `sales[step]` = tập item prototype đó bán ở step
   này → **kéo SELL trùng item của CHÍNH route ta lên đầu queue** (chỉ đổi thứ
   tự). Signature gồm: workers, quadrant bitmask, ≤13 vị trí actor, counts
   (crops/animals/structures/WEED), yields — weight: **12×workers, 7×quadrant
   bit, 0.8 (farmer)/0.25 (hand) × |Δposition|, 3.0×counts (WEED chỉ 0.25),
   0.15×yields**. Tổng 682 lần đổi thứ tự / 53 game; abstain 301/12.614 query.
   Ngoài ra `_safe_market` clamp mọi SELL vào projected shed (bán đủ — không
   order ảo), cap 10 order.
2. **OPENING**: step 0 = **HIRE×5** + BUY 2 SHEEP + 2 COW + WHEAT 7 seed + MELON
   12 seed → thuộc **basin HIRE5 (họ v25)**, rất gần meta 1C/4S/HIRE4 nhưng
   không đúng chữ ký. Herd cuối 8C/6S (mua thêm d3-d11).
3. **FARM**: 8C/6S/0G; WHEAT 92/MELON 24/STRAW 42 seed; **980 wheat mua ngoài**;
   277 HIRE (giờ 0-2); 2 land; max 14 hands.
4. **MARKET**: đây là phần thú vị nhất — **wheat round-trip quy mô lớn**: mua
   980, bán 820, net −160 = feed. 417 event wheat, SELL+BUY CÙNG turn (vd
   step 54: SELL 2 + BUY 2), SELL wheat dồn giờ 7-12, cluster **63 lệnh SELL ở
   giờ 0** (199 STRAW + 152 WHEAT + 96 FERT + 96 MILK units bán ngay mở ngày —
   giờ 0 trùng tick demand shop%4==0 + center%12==0 → giá cục bộ cao nhất chu kỳ).
   Tổng bán: WHEAT 820, STRAW 313, MILK 237, FERT 168, WOOL 164, MELON 144.
   1-5 SELL/turn, size phổ biến 1-6.
5. **ANTI-CLONE/MIRROR**: chính là conditional memory — "không phải username
   lookup": route mới lạ → không prototype nào gần (distance >48) → abstain
   (2.4% query). Nghiên cứu kèm: Dennis route cũ cách Richard/Konstantin >
   1.200 channel-moment, còn Richard↔Konstantin chỉ 110 — họ hành xử như
   "họ route" chứ không phải "họ người".
6. **WEED**: y hệt v20.
7. **ENDGAME**: y hệt v20 (step 718, collision-score, ≤10 order).
8. **CƠ CHẾ MỚI vs v15**: (a) bộ 30 prototype công khai-state → predicted collision;
   (b) invariant order-only (không sinh SELL mới — an toàn closed-loop);
   (c) `_safe_market` clamp-to-shed chống SELL ảo; (d) cluster bán giờ 0.
9. **KHAI THÁC**: 46/51 post-cutoff (tụt so với 177/180) = memory + route decay
   nhanh với meta di chuyển; order-only nghĩa là bị đối thủ CÓ KHẢ NĂNG đổi
   quantity (như v15) đè timing; distance-48 có thể match nhầm policy mới.
   Thua cụ thể: Seb family (3/3 outer), Ben Hamilton −245, OceanMix ×2.
10. **TRANSFER**: **1-NN collision prediction = HIGH** (bản "front_run premium"
    của ta hiện chỉ react giá; thêm nhánh "đoán item đối thủ sắp bán từ farm
    signature của nó" là nâng cấp có kiểm chứng); **cluster bán giờ 0 = HIGH**
    (kiểm tra v15 đã bán đúng giờ 0 sau day-boundary chưa — cadence race H=8
    của ta phải thắng được cái này); **wheat round-trip = MED-HIGH** (cần battery).

### 3.3 v43 — "103/128 Fresh Public | Sparse Shop Hybrid" (63.309 B)

1. **ARCHITECTURE**: module hóa `sys.modules` fake-package; **3 route tape**
   (default + yarn_first + yarn_second — chung prefix tuyệt đối tới step 87
   full-action, step 158 farmer/hand) + **router 2 sự kiện observable duy nhất**:
   shop đầu tiên == YARN_STORE (step ≥88) → yarn_first; shop thứ 2 == YARN_STORE
   (step ≥153) → yarn_second. "Sparse Shop Hybrid" = mỗi child là
   `build_sparse_planner` (tape + weed repair + `reorder_sell_slots`) và **CẢ 3
   child được gọi MỖI turn** (đồng bộ state weed-repair) nhưng chỉ 1 action emit.
2. **OPENING** (default = ActiveMusyoku ep 96815867): step 0 =
   `BUY_PRODUCT WHEAT 4` + HIRE×2 + MELON 7 seed + WHEAT 5 seed + **BUY 4 SHEEP**
   → đúng lõi meta "4-SHEEP" (không COW ngày 0; COW bắt đầu d4).
3. **FARM** (default): 11 COW + 4 SHEEP + 0 GOOSE; WHEAT 140/MELON 11/STRAW 41/
   CARROT 20 seed; 105 wheat mua; 282 HIRE (237 lệnh ở giờ 0); 2 land; ≤15 hands.
   yarn_first branch: 6C/10S (nặng WOOL khi YARN mở đầu).
4. **MARKET**: tổng bán FERT 400, STRAW 432, MILK 335, WHEAT 326, WOOL 179,
   MELON 72, CARROT 57; giờ bán trải dài, đỉnh buổi tối h17-23 (55 lệnh h23);
   reorder theo `impact_score = q×(quote_now − quote_after_q)` dùng **bảng giá
   chính xác engine 1.32.7** `MARKET_PARAMS` (base, equilibrium=10000, scale,
   shape dưới/trên: WHEAT sqrt/log, MELON log/sq, WOOL log/sq, MILK sqrt/linear,
   STRAW sqrt/linear, EGG hinge/log, TOMATO hinge/sqrt, CARROT hinge/sqrt, FERT
   linear/linear) — transcription stdlib thuần.
5. **ANTI-CLONE**: không có trong v43 (clone preemption là v44). Router chỉ đọc
   `town.unlocked_shops` công khai.
6. **WEED**: `wrap_weed_repair` y hệt v20 (replay_steps=8).
7. **ENDGAME**: `terminal_liquidation` — step 718, mọi item trong shed, xếp theo
   `quote×qty`, ≤10 order. Có thêm `plan_sell_quantities` (MPC đổi quantity)
   nhưng **CHỈ chạy ở regime "rebalance"** (configuration
   `townCenterSellInterval ≥ 24` — PR #1394) và bị loại ở legacy.
8. **CƠ CHẾ MỚI vs v15**: (a) **MARKET_PARAMS chính xác** — mô phỏng giá nội bộ
   không cần engine; (b) **demand model**: shop mỗi 4 turn ×(2 nếu 1-product),
   center mỗi 12 turn ×(1→d10, 2→d20, 4→d20+) — dùng cho urgency bán;
   (c) EGG market-maker expert đầy reserve accounting (cash floor, feed-days
   reserve, investment horizon 2 turn, shed headroom) — nhưng **0 khác biệt đo
   được → tắt**; (d) dual-regime planner (đổi route theo configuration engine).
9. **KHAI THÁC**: cell yếu nhất PET_CAFE 16/26; nhánh shop không đổi sản xuất —
   dính shop lạ thì vẫn default tape; tape mua/feed cố định.
10. **TRANSFER**: **MARKET_PARAMS + demand model = HIGH** (nếu v15 chưa có bảng
    giá chính xác — đây là món ăn cắp giá trị nhất, cho phép oracle timing hoàn
    chỉnh); **shop-pair continuation = MED** (chuyển thành: nếu YARN đầu → giữ
    WOOL dài hơn / metter bán WOOL khác); EGG MM = LOW (đã đo = 0).

### 3.4 v48 — "40/40 Early Floor | 39/46 Top-10 | Fast Routes" (107.008 B)

1. **ARCHITECTURE**: **6 route tape** + `FastRouteConfig` router theo shop event
   (yarn_fast@88 nếu shop1=YARN; farm_fast@120 nếu shop1=FARMERS_MARKET;
   yarn_second@153; yarn_third@216 với prefix-allowlist
   (BRUNCH,PET_CAFE)/(PET_CAFE,FARMERS); bakery_capital@160) + `CloneSellPreemption`
   + terminal collision. **"Fast Routes"** = 2 continuation lấy từ 2 đội leo nhanh
   nhất (Kaileh57 YARN ep 98720726 nhánh sau step-87; taiseiu FARMERS ep 98706979
   nhánh sau step-119). **Đúng 1 child được gọi mỗi turn** (fix thảm họa v47:
   v47 gọi 4 child stateful trước decision point → exception → PASS fallback →
   11/11 game đúng 3.000 coin).
2. **OPENING**: = v43 default (4 SHEEP + HIRE2 + wheat 4 + melon 7).
3. **FARM**: default 11C/4S; yarn_fast 6C/10S; bakery_capital giữ nguyên farm
   default (chỉ đổi market/capital).
4. **MARKET** — **CloneSellPreemption (đây là cơ chế đắt giá nhất của v48)**:
   - latch: từ step 48, nếu `clone_distance ≤ 2.0` (public signature: hands,
     quadrants, exposure counts) liên tục **24 turn** → latched;
   - active window 160-700; mỗi turneligible: nhìn **route[step+2]** — SELL nào
     dự kiến 2 turn tới → append `["SELL", item, min(planned−đã_có, shed_còn, 10)]`
     vào market hôm nay (front-run 2 turn, batch ≤10 unit);
   - **debt ledger**: số unit bán sớm được ghi `due[step+2][item]`; đến hạn thì
     TRỪ đúng số đó khỏi SELL route (repay); nếu route SELL fail/short →
     **chuyển nợ sang turn sau** (không "tặng" thêm sản lượng);
   - veto: state BAKERY-first + opponent sheep≥4, cow≤1, wheat≥8, melon≥7 →
     TẮT preemption (chỗ từng gây 2 regression);
   - sau preempt thì vẫn `reorder_sell_slots` (impact) — 2 lớp chồng nhau;
   - riêng FERTILIZER: `exposure_preempt` (đối thủ ≥8 thú + price_ratio ≥0.80)
     front-run lookahead 24 turn — nhưng bị disable khi latched.
   - terminal rule="collision" step 718.
5. **ANTI-CLONE/MIRROR**: chính là clone preemption (mục 4) — chỉ kích hoạt khi
   đối thủ GẦN NHƯ COPY mình (distance ≤2 trong 24 turn) → bán trước mặt nó 2
   turn. Đối thủ không phải clone (như v15) → latch không bao giờ fire → mọi
   layer can thiệp về cơ bản tắt, chỉ còn tape + reorder + terminal.
6. **WEED**: y hệt, nhưng code note "explicitly supports a first call at a late
   continuation decision point" (state an toàn khi gọi muộn).
7. **ENDGAME**: terminal_market rule="collision".
8. **CƠ CHẾ MỚI vs v15**: (a) debt-tracked pull-forward; (b) bakery_capital gate
   đọc **public asset counts của ĐỐI THỦ** (≥3 cow, ≥2 sheep, ≥10 melon, 0 goose)
   → nhánh vốn; (c) one-child-per-turn invariant + build smoke "first action
   non-PASS"; (d) route theo shop của THỊ TRẤN (không phải của mình).
9. **KHAI THÁC**: clone preemption mù với đối thủ lạ (v15 không giống public tape
   → hưởng 0); worst margin top-10 −26.535 = vẫn có matchup thua nặng; route
   cố định 11C/4S không adapt giá.
10. **TRANSFER**: debt ledger = MED (v15 front_run có nguy cơ double-sell — kiểm
    tra và ensure "vốn bán sớm phải trừ khỏi kế hoạch sau"); bakery gate = LOW-MED;
    build invariant = LOW nhưng RẺ VÀ NGĂN THẢM HỌA (v47 mất 11 trận vì PASS-only).

---

## 4. TOP 10 ĐỘT PHÁ ĐÁNG CHUYỂN VÀO v16 (xếp hạng transfer value)

| # | Cơ chế | Nguồn | Rank | Vì sao / cách chuyển |
|---|---|---|---|---|
| 1 | **Bảng giá chính xác `MARKET_PARAMS`** (9 item × shape dưới/trên equilibrium, stdlib thuần) | v22/v43 `scripts.v22_market_impact` | **HIGH** | Cho phép v16 mô phỏng chính xác quote sau mỗi unit bán → chọn batch/timing tối ưu KHÔNG cần engine; kết hợp demand model (shop%4, center%12 ×1/2/4) = oracle timing trọn vẹn. Kiểm tra v15 đang xấp xỉ thế nào; nếu v15 chỉ dùng giá quan sát + slope giả định thì đây là leap trực tiếp. |
| 2 | **1-NN conditional collision memory** (30 prototype: signature 719-step + sales-set; distance ≤48; chỉ đổi thứ tự SELL) | v21.1 `_conditional_reorder` | **HIGH** | Nâng cấp `front_run premium` của v15: thay vì chỉ react giá hiện tại, đoán **item đối thủ sẽ bán TURN NÀY** từ farm-signature của nó (workers/quadrant/positions/counts/yields) rồi kéo SELL trùng lên trước. Invariant order-only = an toàn closed-loop (không sinh order mới → không feedback loop). Data: có sẵn từ replay Kaggle ta đã tải (2 file 32MB) — build 20-30 prototype từ đó. |
| 3 | **Cluster bán giờ 0 (day-boundary + demand tick kép)** | route v21.1 (63 lệnh SELL giờ 0; 199 STRAW unit) | **HIGH** | Giờ 0 trùng shop-tick %4==0 VÀ center-tick %12==0 → inventory vừa drain → giá đỉnh cục bộ. v15 có cadence race H=8 — verify rằng mọi SELL lớn của v15 rơi giờ 0 (hoặc giờ 12), không bị trôi giờ 1-2. Audit rẻ bằng replay đã có. |
| 4 | **WHEAT round-trip quy mô lớn** (980 mua / 820 bán; SELL+BUY cùng turn) | route v21.1 | **MED-HIGH** | Bằng chứng route mạnh nhất public dùng wheat vừa feed vừa "cất trữ-bán" quanh dao động giá do town demand. v15 có sẵn BUY_PRODUCT — thử nhánh: khi wheat inventory cao (giá ≤ base) mua gộp, bán lại khi inventory về dưới equilibrium sau các tick. Cần battery A/B vì v43 đã thử EGG-MM = 0 (wheat khác EGG: cũng là feed + base thấp + dao động đều). |
| 5 | **Debt-tracked pull-forward** (bán sớm horizon=2, ≤10 unit, ghi nợ `due[step+h]`, repay bằng cách trừ khỏi SELL route; fail → chuyển nợ sang turn sau) | v44/v48 `CloneSellPreemption` | **MED** | Nguyên lý "dời thời gian, không thêm sản lượng" chống double-sell. Nếu front_run của v15 thêm SELL mới mà không trừ khỏi plan → có thể bán 2 lần cùng đơn vị (hoặc để tồn đọng). Đối chiếu mechanism + telemetry. |
| 6 | **Glut-weight sell-priority table** (MELON 3.6, WOOL 3.2, STRAW 2.0, MILK 2.0, EGG 1.5, TOM 1.3) nhân `(1+opp_exposure)×price×log1p(q)` | v20/v21.1 `_GLUT_WEIGHT` | **MED** | Prior hóa item "đối thủ sắp làm glut" khi xếp hàng bán / terminal. Rẻ, dễ A/B trong battery: đổi thứ tự ưu tiên terminal liquidation của v15 sang công thức này. |
| 7 | **Terminal liquidation "collision"** (step 718: rọi toàn bộ projected shed, xếp theo score, cap 10 order) | cả 4 version | **MED** | v15 đã có `_shadow_terminal/_parent_liquidate` — đối chiánh: (a) có tính `_projected_shed` gồm DROP/PLACE đang bay không; (b) xếp theo (1+exposure)×glut×price×log1p; (c) cap 10 đúng luật. Khác biệt nhỏ nhưng cuối game là tiền thật. |
| 8 | **Shop-conditional continuation** (YARN đầu → suffix nặng WOOL; FARMERS đầu; BAKERY+PIZZA + đối thủ 3C/2S/10M → nhánh vốn) | v43/v48 router | **MED** | Bản dịch cho v15: herd/market target nên điều biến theo `town.unlocked_shops` (giá trị WOOL giữ cao khi YARN mở). v15 hiện router theo state riêng — thêm feature shop vào router là surgical. |
| 9 | **Mirror/clone latch hysteresis + nghiên cứu 99.11% market-intent match** | v20 §3 | **LOW-MED** | Kiến thức quan trọng hơn cơ chế: khi board hai bên gần nhau 24+ turn thì intent bán TRÙNG 99% — front-run chỉ cần reorder. Với v15: nếu detect near-mirror (farm signature khớp), chuyển sang chế độ "giờ 0 + batch nhỏ + item trùng" thay vì đánh lớn. (Cẩn thận L38 knife-edge: Kaito chỉ đổi THỨ TỰ — không tạo nhiễu mới.) |
| 10 | **Build invariant "719 policy calls = 719 child calls" + smoke first-action-non-PASS** | v48 (sau thảm họa v47 PASS-only 0/11) | **LOW (rẻ)** | Bảo hiểm nâng submission: 1 test tự chạy 2 seat assert action[0] ≠ PASS + đếm child call. Ngăn nguyên cả thế hệ trận thua 3.000-3.000 do crash nuốt action. |

---

## 5. V15 ĐÁNH HỌ KAITO BẰNG CÁCH NÀO — ĐIỂM YẾU CỦA HỌ

1. **Họ là open-loop 95%** — sản xuất cố định (11C/4S hoặc 8C/6S tuỳ route), mua
   feed theo lịch (105-980 wheat). v15 là planner reactive: điều chỉnh theo giá/thị
   trường thật → thắng mọi game mà đúng quyết định phụ thuộc state (feed-vs-sell
   như trận thua -$553 của TA chính là thứ Kaito làm tốt bằng tape và ta làm tốt
   bằng planner — nhưng Kaito KHÔNG thể điều chỉnh route giữa game).
2. **Clone-preemption của họ mù với v15**: latch cần clone_distance ≤2 trong 24
   turn — v15 khác biệt hành vi so với mọi public tape → layer can thiệp mạnh nhất
   của v48 không bao giờ kích hoạt khi gặp ta.
3. **Tape mua BUY_PRODUCT theo lịch cố định** (v21.1 mua 980 wheat) — v15 có thể
   đón đầu: hút inventory wheat (BUY) ngay trước các bước mua lớn của tape đó →
   đẩy giá mua của họ lên, sau đó bán lại quanh equilibrium. Đây là đòn "đvý
   market" đối đầu open-loop duy nhất có hiệu quả đo được.
4. **Order-only interventions** — khi meta đổi (đối thủ mạnh như Seb/OceanMix),
   họ thua vì không đổi được quantity/route (đích thân failure audit v21.1 ghi:
   "consistent with a stronger production/market route family").
5. **Route decay nhanh**: 46/51 post-cutoff so với 177/180 outer — họ phải refresh
   route liên tục; v15 không phụ thuộc route snapshot.
6. **Điểm yếu cân nhắc**: route của họ (ActiveMusyoku/Konstantin medoid) là băng
   của người THẬT top — sản lượng nền rất mạnh (STRAW 432 + MILK 335 + WOOL 179
   + MELON 72 với 15 hands). Nếu v15 sai timing màroute đúng → vẫn thua production
   race. Không được chủ quan: v15 phải giữ nguyên chuẩn H=8 + room_guard hiện tại.

**Khả năng gặp trên Kaggle**: Kaito Fukami #3 — xác suất gặp rất cao khi v15 lên
điểm. Nhận diện: opening 4-SHEEP/HIRE2 (v43/v48 basin) hoặc HIRE5/2C/2S (v21.1
basin) + hành vi bán giờ 0-1 + mua wheat đều đặn. Counter: giữ cadence race,
không bắt chước opening của họ (latch của họ sẽ tắt — tốt), hút wheat trước giờ
mua của họ nếu nhận diện được nhịp.

---

## 6. GHI CHÚ PHƯƠNG PHÁP

- 4 file `.py` là notebook convert; agent nhúng base85+zlib. Đã giải nén:
  `research/kaito_extracted/{v20_main.py, v211_main.py, v43_main.py+mods/,
  v48_main.py+mods/, *_actions.json, v48_routes.json, v43_routes.json}`.
- Số liệu route (herd/seed/hire/sell/hour-histogram) tính trực tiếp từ tape JSON.
- Con số win-rate trong title = **counterfactual replay holdout** (đối thủ đóng
  băng, không phản ứng) — không so sánh trực tiếp với battery closed-loop của ta;
  dùng để đánh giá cơ chế, không phải sức mạnh live tuyệt đối. Live record duy
  nhất được ghi: v21 cũ 65/67, v26 87/90 (20/20 cuối).
- Engine assumption của họ: 1.32.7 default params (khớp pip của ta), shed
  capacity 100, max 10 market order/turn, hire Fibonacci theo ngày, land
  (1000/2000/4000), animal cost (GOOSE 300/COW 400/SHEEP 500), seed cost
  (WHEAT 10/CARROT 20/TOMATO 50/STRAW 100/MELON 80) — khớp bảng giá ta biết.
- v27 (25/27) đọc để bổ sung timeline: cùng opening HIRE4, thay continuation từ
  step 161 — bằng chứng "26/30 top dùng cùng opening; edge ở continuation"
  trùng khớp meta live 8/11 của ta (modal 9C/4S/1W/10 hands, 26/30 cùng
  1C/4S).
