# ANALYSIS: yhay81 "Shop Router" family + romantamrazov "Hamburger" + misc (Task 74-c)

> Research-only. 6 notebook: yhay81 shop-router-0909 (127 votes), yhay81 three-day-shop-router (121), yhay81 six-day-public-state-fieldbook (131), romantamrazov hamburger (129), salemali7 2900+ (77), jek1wantaufik building-a-kaggriculture-ai-agent (76). Ngày chạy cuối: 10/9/2026.

---

## 0. "SHOP ROUTER" LÀ GÌ — giải thích chính xác mức code

**KHÔNG phải** "route worker đến shop" và cũng **KHÔNG phải** router quyết định mua/bán tại shop. Nó là:

> **Một tape-router (bộ chọn plan): tại turn 144 (ngày 6), đọc `observation["town"]["unlocked_shops"]` — 2 shop đầu tiên được mở khóa — rồi chọn 1 trong 13 tape 719-turn đã tối ưu sẵn cho cặp shop đó.**

Cơ sở engine (đối chiếu RULES.md của ta):
- R38: shop unlock mỗi 3 ngày (d3, d6, d9…), bốc uniform CÓ hoàn lại từ 8 loại, cap 8 instances.
- R39/R41: mỗi instance shop tiêu 1 unit/mặt hàng nó cần mỗi 4 turn (6 unit/ngày; shop đơn sản phẩm ×2). Bảng demand: Bakery(egg+wheat) · Pizza(milk+tomato+wheat) · Brunch(egg+wheat+straw) · **Yarn(wool×2)** · IceCream(straw+milk+wheat) · PetCafe(carrot×2) · Smoothie(straw+milk) · FarmersMarket(wheat+carrot+tomato+straw).
- Shop draw là 1 trong 2 nguồn nhiễu thật của game (R45) → **shop mix quyết định mặt hàng nào "sống" cả mùa** → plan tối ưu phụ thuộc draw.

Code đích (yhay 0909, `main.py`):
```python
ROUTE_STEP = 144
SHOP_PLANS = { ("BAKERY","YARN_STORE"):3, ("BRUNCH_SPOT","YARN_STORE"):4, ...,
               ("YARN_STORE","YARN_STORE"):12 }   # 15 cặp → plan 1,3..12; còn lại → plan 0
if step == ROUTE_STEP:
    shops = observation["town"]["unlocked_shops"]
    state.plan = SHOP_PLANS.get(tuple(shops[:2]), 0)
if step == FINAL_PLAN_STEP:   # 648
    state.plan = 2            # mọi route dùng chung ending từ step 648
```
Lưu ý cặp key là **(shop d3, shop d6) theo thứ tự observed** — vì turn 144 là lúc shop thứ 2 vừa mở.

"Ba ngày / sáu ngày" = **độ granular của block quyết định + budget guard**, không phải chu kỳ nuôi:
- *Six-Day* (fieldbook): block 144 turn (6 ngày), router ở 4 mốc 144/288/432/576, decision-tree theo public state.
- *Three-Day* (3day router): budget guard chạy mỗi 72 turn (3 ngày) + 1 quyết định thay segment ở turn 360 (thay đúng block 360–431).
- *0909*: rút gọn — 1 quyết định duy nhất ở 144 + ending chung ở 648 + 3 lớp repair.

---

## 1. BẢNG TỔNG QUAN 6 NOTEBOOK

| # | Notebook | Loại | Architecture | Điểm mới so v15 của ta |
|---|---|---|---|---|
| 1 | yhay81 shop-router-0909 | Tape portfolio + router | 13 tape × 719 turn; chọn bằng cặp shop ở t144; + weed-repair, advance-sales, final-liquidate | **KHÔNG CÓ — đây là tổ tiên trực tiếp của ta** (kme3/kme3v10 kế thừa nguyên văn: `_V14_SHOP_ROUTE` trong v15 = `SHOP_PLANS` của yhay) |
| 2 | yhay81 three-day-shop-router | Như trên + 2 route | 2 tape; quyết định t360: BAKERY-first & fert-inv≤10232.5, hoặc PET_CAFE-first & rival plant≤64.5 → segment 360-431 khác; budget guard 72-turn | **(a) Guard 72-turn (ta 144), (b) feature "rival plant tiles" trong router, (c) threshold market fert 10232** |
| 3 | yhay81 six-day fieldbook | Mine-and-route | Tape block 6 ngày mining từ replay top (Bantam #3, Zenith Ye #8), decision-tree 16 test nhị phân/20 lá ở 4 mốc, 30 path; C++ runtime | Nguồn gốc các tape của ta; thêm tư duy "đo trên fresh seeds + 188 external histories" (24k game, 0.9485 point rate) |
| 4 | romantamrazov hamburger | Lab tối ưu trên tape "Tran H Hoang" | Tape cố định + 4 lớp repair/terminal + **clone-detection & collision-aware sell ordering** + terminal relay 716-718 | **(a) Clone-profile ở t300 (5 điều kiện trên tiles đối thủ) → reorder SELL theo exposure×glut, (b) Replay Shield = front-run 1-turn theo profile rival (hands/money ở t1), (c) terminal relay 716-718, (d) sell-front ordering** |
| 5 | salemali7 2900+ (= boatlee V16-RC5 biến thể) | Tape + repair | Tape cố định (8C/4S) + weed-repair realign 8 bước + **premium lead có gate theo town demand** | **Gate `_town_demand_now` cho front-run: bỏ qua khi có shop đang cầu mặt hàng đó; bảng _SHOP_PRODUCTS** |
| 6 | jek1wantaufik | Build script | Gộp 8 module (state/board/actions/economy/market/scheduler/search/planner) từ Kaggle Model dataset → 1 file; smoke test vs random | Không có (chỉ pattern đóng gói) |

**Quan hệ dòng dõi với ta:** yhay 0909/fieldbook → kme3 → kme3v10 → v13 → v14 → **v15**. Cơ chế của notebook 1-3 đã nằm nguyên trong v15 (xác minh: `_V14_SHOP_ROUTE` v15.py L2732 ≡ `SHOP_PLANS` yhay; `_sell_lead`/`_front_run`/`_budget_guard`/`_weed_repair`/`_terminal_liquidation` đều có trong chassis; `FRONT_RUN_ITEMS = MILK/WOOL/STRAWBERRY/MELON` ≡ salemali7 `_FR_ITEMS`). Notebook 4 (hamburger) là **họ tape khác** (Tran H Hoang, không phải KaggressurE) — toàn bộ cơ chế clone-aware của nó là MỚI so với v15.

---

## 2. CHI TIẾT TỪNG NOTEBOOK (theo 8 câu hỏi)

### 2.1 yhay81 — Shop Router 0909 (266 dòng, payload 226KB)

**ARCHITECTURE.** `Policy.act(obs)` mỗi turn: (1) t144 chọn plan theo cặp shop; (2) t648 → plan 2 (ending chung); (3) lấy `copy.deepcopy(tape[step])`; (4) `repair_weeds`; (5) `subtract_advanced_sales` (trừ lượng đã bán sớm ở turn trước); (6) `advance_sales`; (7) t718 → `liquidate()` thay thế hoàn toàn. Per-player state riêng (`DayState`), queue reset mỗi dawn.

**OPENING + FARM (từ actions.json giải mã, 13 tape).**
- t0: `BUY WHEAT 13 / SELL WHEAT 13 / BUY WHEAT 13` — churn giá wheat (đúng chữ ký họ KaggressurE ta từng mổ ở Task 72).
- t1: SELL 13 + BUY 5 wheat, 5 HIRE, BUY 2 COW + 2 SHEEP; t2-3 PICKUP + BUILD_PASTURE + PLACE.
- Tổng game: **260-277 HIRE** (~9-11 hands/ngày, max 11-12), **2 BUY_LAND** (3 quadrant), 14-18 BUILD_PASTURE + 1-5 BUILD_COOP.
- Herd theo plan: plan 0/2 = **8 COW + 6 SHEEP + 3 GOOSE**; plans 3-8,10,11 = **6 COW + 10-11 SHEEP** (17 pasture, 2 coop); plan 1 (FARMERS_MARKET sau YARN) = 6C+10S bán ít (yarn continuation, wool 9.580); plan 12 (YARN,YARN) = **4 COW + 14 SHEEP** — wool-heaviest.
- Crops: **163-165 PLANT WHEAT + 33 STRAWBERRY + 28-31 CARROT + 12 MELON**.
- Bán: plan lớn dumps WHEAT ~25.268, FERTILIZER ~18.351, WOOL ~12.7k, MILK 9.3k, EGG 9k, STRAW 13.3k, CARROT 19k, TOMATO 7k, MELON 7k. Plan nhỏ ~60-70% mức đó.
→ **Router shop-pair thực chất = đổi herd/mix bán hàng theo demand mùa**: draw YARN-heavy → thêm sheep bớt cow (wool ×2 demand), draw khác → 6C+10S và đấu wheat/fertilizer volume.

**MARKET.** Bán rải theo tape; histogram giờ bán tập trung **turn-of-day 1 (46 lần)** và **21 (38 lần)** — sau dawn (market refresh) và cuối ngày. Ngày 27 có dump lớn trong tape (FERTILIZER 2019, MILK 2014, CARROT 2000 — sẽ bị clamp bởi inventory thực). Cơ chế bán sớm: `advance_sales` kéo SELL của turn sau lên 1 turn (bỏ qua WHEAT/FERTILIZER làm feed, bỏ qua khi `next_step % 72 == 0` — ranh giới unlock shop — và `step % 4 == 0` — tick tiêu thụ town), rồi trừ lại turn sau (`subtract_advanced_sales`). Front-run đối thủ: KHÔNG có trong notebook này (ta mới là người thêm).

**WEED.** `repair_weeds`: queue theo-từng-worker trong ngày; nếu action kế tiếp là PLANT/BUILD_COOP/BUILD_PASTURE mà đứng trên WEED → phát DIG, action bị chặn được đẩy lùi (chỉ worker đó), queue clear lúc dawn ("Unfinished work never spills into tomorrow").

**ENDGAME.** `liquidate()` ở t718: mọi worker cạnh shed DROP hết; SELL toàn bộ shed dự báo (`projected_shed` mô phỏng PICKUP/DROP/PLACE quanh shed, cap 100), sort theo `price×qty` giảm dần, cap 10 orders.

**MỚI so với v15:** không có gì (v15 ⊃ notebook này, qua kme3v10 + layers). **ĐÁNH GIÁ: đã sở hữu.**

**ĐIỂM YẾU gặp v15:** chính là đối thủ trong battery — v15 thắng kme3/kme3v10 10/10 (+$3.2-3.6k). Tape tĩnh không biết đáp lại front-run/room_guard của ta; route choice thuần shop-draw (deterministic) → v14/v15 front-run layer đọc trọn tape đối thủ.

---

### 2.2 yhay81 — Three-Day Shop Router (979 dòng, C++)

**ARCHITECTURE.** C++ `.so` + ctypes bridge. `kSegmentTurns=72`, `kDecisionStep=360`, 2 route (`kRoutes=2`). Mỗi 72-turn boundary chạy `calculate_six_day_requirements` + `apply_six_day_budget_guard`:
- Requirement: quét 72 turn kế: chi phí HIRE (fib per-day, `hires_today` reset mỗi ngày), BUY_LAND (1000/2000/4000), seed (10/20/50/100/80), BUY_PRODUCT wheat/fert theo giá hiện tại, BUY_ANIMAL (300/400/500); reserve FEED wheat + FERTILIZE + PLACE.
- Guard: nếu cash + doanh thu SELL đã có < budget → bán tiếp **chỉ phần vượt reserve tiêu dùng tĩnh**, sort giá cao trước, `sales_first` (SELL đẩy lên đầu queue order).

**ROUTER (mấu chốt):**
```cpp
if (shops[0]==BAKERY && market.inventory[FERTILIZER] <= 10232.5) return 1;
if (shops[0]==PET_CAFE && plant_tiles(farms[1-seat]) <= 64.5) return 1;
```
→ Route 1 = thay nguyên block 360-431 bằng "segment72_b01_0091" (một block 72-turn khai thác từ replay mạnh — bán WOOL sớm+liên tục WOOL×1..×6, bỏ SELL MILK đầu block, ít mua hơn). Nghĩa: **state-keyed mid-game swap**: thị trường fertilizer ảo (≤10232 = ít oversupply? hoặc detect đường nào) và **quy mô ruộng đối thủ (≤64 ô planted)** là feature quyết định continuation. Đoạn 360-431 = day 15-17 — đúng giai đoạn premium-line.

**MARKET.** Guard bán theo nhu cầu vốn 72-turn (không phải 144) → phản ứng tiền mặt nhanh gấp đôi; SELL-first ordering.

**MỚI so với v15:** (a) interval budget guard 72 (ta để budget_guard=False toàn thời gian sau L33 — nhưng L33结 luận "budget_guard thảm họa" là của bản 144-turn; bản 72-turn chưa từng A/B); (b) **rival plant-tile count làm feature router** — v15 chưa dùng tiles đối thủ để đổi continuation (chỉ dùng ở các layer nhỏ như R90/mirror-counter); (c) market fert inventory threshold.

**YẾU gặp v15:** vẫn là tape tĩnh 2 route + 1 lượt swap; không có front-run; ending không đổi. **TRANSFER: MED** (ý tưởng feature rival-tiles cho router mid-game; guard 72 chỉ đáng thử nếu tái bật budget_guard).

---

### 2.3 yhay81 — Six-Day Public-State Fieldbook (53 dòng py + dataset ngoài)

**ARCHITECTURE.** Block 144-turn; 5 kỳ: d0-6 fixed (1 plan) → d6-12 tree (2) → d12-18 bridge (1) → d18-24 tree (3) → d24-30 tree (5). 16 test nhị phân/20 lá, 30 path mùa, chỉ lưu 8 tape gốc. Test = so sánh public state: "carrot có đắt?", "fertilizer rẻ?", "cash gap dương?" — KHÔNG key theo tên/rank/seed/replay-id/future shop (runtime_features_exclude ghi rõ). Build: sha256-verify 7 file nguồn C++ từ Dataset, compile, đóng tar.gz 2 file.

**NGUỒN TAPE (phần "How I built it" — quy trình đáng ăn cắp nhất):**
1. Download top-200 + replay cũ, dedup action-history theo SHA-256 chính xác.
2. Gom mọi episode public của **Bantam (rank 3) và Zenith Ye (rank 8)**, lấy block 6 ngày của họ làm ứng viên swap.
3. Test block tại đúng boundary, seed mới, cả 2 ghế (không so game không liên quan).
4. Giữ 8 route, fit decision-tree nhỏ bằng feature public.
5. Freeze policy rồi đo trên 188 external histories: 24.064 game → 22.795W/58D/1211L = **0.9485 point rate** (CI [0.9371, 0.9565]); subset 164 đối thủ thường 0.9948; **24 đối thủ khó 0.6322**.

**BUDGET GUARD.** Như 2.2 nhưng chu kỳ 144; bán "chỉ tồn dư trên reserve tĩnh", giá ≥ 2 mới bán, high-price-first.

**MỚI so với v15:** (a) phương pháp luận holdout 188 external histories + fresh seeds; (b) tree router đa-mốc (4 boundary) — v15 chỉ router 1 mốc t144 (+ fixed t648); (c) "hard tail 0.6322" là chỉ số thú vị: top public agent cũng có 24 kẻ ăn được nó.

**TRANSFER: MED-HIGH về methodology** (harness đo external histories — hiện ta chỉ battery 5 đối thủ local), LOW về code (chassis ta đã là con cháu của nó).

---

### 2.4 romantamrazov — Hamburger 🍔 (739 dòng) — TRỌNG TÂM

**ARCHITECTURE.** Notebook = phòng lab: `ANCHOR_BLOB` (agent gốc 150KB) + `OVERLAY_BLOB` (template 12.5KB, chèn `__CASHFLOW_MODE__/__TERMINAL_RELAY__/__TERMINAL_START__`) + 5 `CONTROL_BLOBS` (Soil V25, Kaito V21, Replay Shield V15, Scenario V14, Frontier V12) + 7 candidates. Đo bằng kaggle-environments==1.32.2, Stage A (2 seed, symmetric pair vs Anchor) → Stage B (broad gate) → promotion (strict higher broad mean money, không giảm wins/robust minimum, phạt leftover 0.01×). **Winner: "Collision Slots + Relay".**

**ANCHOR = tape "Tran H Hoang" episode 89674601 seat 0 — HỌ KHÁC KaggressurE:**
- Day-0: HIRE×2 + BUY COW 1 + BUY_SEED MELON 6 + WHEAT 6 + SELL WHEAT 1/3/… (bán lẻ để canh giá).
- Tổng: 306 HIRE, 2 land, **8 COW + 6 SHEEP** (không goose), PLANT 66 WHEAT + 44 STRAWBERRY + 21 MELON; BUY_PRODUCT 1033 wheat (feed), SELL WHEAT 1103 (wheat là feed-churn chứ không phải cột doanh thu), FERTILIZER 408, MILK 413, STRAW 390, WOOL 251, MELON 182.
- Lớp repair của anchor: terminal PLACE+SELL từ t716; weed-block BUILD_PASTURE → DIG + pending-next-step; late-day farmer shift giữ tape cũ đến cuối ngày; step 636 special-case PLANT WHEAT bị weed.

**"CLONE QUAD H1" / CLONE-AWARE TIMING — 3 tầng, xếp theo độ tinh:**

1. **Clone detection (anchor + overlay, step 300):** đếm tiles đối thủ theo `tile["animal"] or tile["crop"]`. Nếu `WHEAT≥5 ∧ STRAWBERRY≥26 ∧ MELON==6 ∧ COW≥8 ∧ SHEEP≥6` → đối thủ đang chạy tape Tran H Hoang (hoặc clone gần) → bật chế độ clone. Đây là "check 2 farm gần giống" — dấu vân tay 5 điều kiện đúng bằng config của chính tape (8C/6S/6 melon/44 straw/66 wheat).
2. **Collision-aware sell ordering (overlay, mỗi turn 300→714 khi clone):** score mỗi SELL order:
   `score = price×min(qty,12) + 0.075×price×min(qty,8)×exposure×glut + 0.10×price×qty×glut`
   trong đó `exposure` = số tile đối thủ sản mặt hàng đó (COW→MILK, SHEEP→WOOL, GOOSE→EGG, tổng thú→FERTILIZER…), `glut` = hệ số sập giá theo mặt hàng (WHEAT 0.2, MELON 3.6, WOOL 3.2, STRAW 1.6, MILK 1.6, CARROT 0.7, TOMATO 0.6, EGG 0.2, FERT 0.4). Mode: `collision_slots` (chỉ hoán vị trong các slot SELL đã có), `collision_front` (SELL dồn hết lên trước mọi order), `static_slots` (priority cứng WOOL>MELON>MILK>STRAW>CARROT>FERT>WHEAT>EGG>TOMATO). Hiệu ứng: 2 clone cùng dump cùng mặt hàng cùng turn → double price impact; kẻ sort theo collision-risk bán Premium đúng chỗ/trước.
3. **Replay Shield V15 (control blob — "bán trước 1 turn premium line" đúng nghĩa nhất):** ở step 1, profile đối thủ bằng public state thuần: `hands≤3 ∧ money≥900 → "tape"`; `hands==6 ∧ 600≤money≤700 → "v12parent"`; `hands==6 ∧ money>700 → "v14"`; `hands==6 ∧ money<600 → "m12"`. Nếu profile thuộc tập kích hoạt (`tape_v12parent_v14`) thì **mỗi turn**: nhìn SELL của chính tape mình ở t+1 với các PREMIUM items (WOOL, MILK, MELON, STRAWBERRY, EGG, TOMATO, CARROT, FERTILIZER — tất cả trừ WHEAT) → **bán ngay turn này lượng min(shed, lượng định bán)** sort theo notional, cap 10 orders, KHÔNG trừ lại turn sau (khác invariant của ta — Replay Shield bán thêm chứ không shift). Logic: cùng tape → cùng lịch dump → mình bán t trước khi dump của nó (và của mình theo tape) đè giá ở t+1.

**TERMINAL RELAY (716-718):** với mọi carrier đang giữ hàng: nếu cạnh shed-access tile và toàn bộ inventory là product thuần vừa room shed (cap 100) → DROP; nếu không → PLACE item tốt nhất (theo price×qty×(1+glut)); nếu đang xa thì đi từng bước về shed nếu `distance ≤ 718-step` và action gốc là no-op (PASS/PLACE/DROP). Cuối cùng SELL shed+projected sort theo `price×qty×(1+0.05×exposure×glut)`.

**LỖI TÍNH GIỜ CUỐI (đúng với L36/L64 của ta):** "interpreter xử lý action 718 rồi DONE; index 719 không chạy" — V27 dồn routing+liquidation vào 716-718.

**WEED:** DIG + pending-pasture retry; không có watchdog shed-animal như R90 của ta.

**MỚI so với v15:** (a) **collision/exposure scoring của SELL khi gặp clone** — v15 có front-run theo tape biết trước (mạnh hơn về thông tin: biết CHÍNH XÁC lịch đối thủ cùng lineage KaggressurE), nhưng KHÔNG có exposure-model khi bản thân không suy ra được tape (đối thủ lạ) và không có glut-weighted ordering; (b) profile-by-public-state (hands/money t1) để nhận diện family đối thủ — v15 mặc định cùng lineage, không nhận diện family khác; (c) terminal relay walk-to-shed có "guaranteed_noop + distance" check tinh hơn `_terminal_liquidation` của ta (ta đang off).

**YẾU gặp v15:** tape Tran 8C/6S không có front-run, không lead-sale, sells nhỏ; v15 front-run biết lịch KaggressurE nhưng với Tran-family thì chỉ cần out-economy — cùng nhánh 8C ~ ta từng thắng họ KaggressurE ở Task 72 (BorisV-type) trừ khi clone-detection giúp họ sort bán đẹp hơn. Rủi ro chính: **đối thủ hamburger gặp v15 sẽ không detect clone** (v15 ≠ Tran profile) → toàn bộ tầng clone của họ tắt → chỉ còn tape thuần.

**TRANSFER: HIGH** — (1) tư duy "glut hệ số sập giá từng mặt hàng" để sort SELL (dùng được cho clamp_sells/độ ưu tiên bán khi inventory thị trường cao); (2) exposure từ public tiles đối thủ như feature (v15 chỉ dùng trong mirror-counter nhỏ); (3) terminal relay an toàn (bảo hiểm rẻ kiểu R90); (4) cách đo Stage A/B có broad gate + phạt leftover.

---

### 2.5 salemali7 — "2900+" / HarvestForge-X (545 dòng)

**ARCHITECTURE.** Tape 719 turn nhúng base85 + 3 lớp: weed-repair, repay/front-run bookkeeping, align-hands. Claim 2900+ rating kèm chart 60/60 wins local 30 seeds. Thực chất = dòng boatlee V16-RC5 (ta có notebook boatlee__v16-rc5 trong research) — kể cả biểu đồ "One-turn premium market lead".

**OPENING/FARM (từ chart data):** **4 SHEEP ngay t0**, COW 1 → 2 (t120) → 4 (t161) → 6 (t168) → **8 (t192)** — "8C/4S production core reaches full livestock by step 192". 3 quadrant. Gần modal meta "9c+4s+1w+10h" của ta (ta 9C, họ 8C).

**MARKET — cơ chế đáng chú ý nhất: TOWN-DEMAND GATE cho front-run:**
```python
_SHOP_PRODUCTS = { "BAKERY":("EGG","WHEAT"), "PIZZA_SHOP":("MILK","TOMATO","WHEAT"),
 "BRUNCH_SPOT":("EGG","WHEAT","STRAWBERRY"), "YARN_STORE":("WOOL",),
 "ICE_CREAM_SHOP":("STRAWBERRY","MILK","WHEAT"), "PET_CAFE":("CARROT",),
 "SMOOTHIE_SHOP":("STRAWBERRY","MILK"), "FARMERS_MARKET":("WHEAT","CARROT","TOMATO","STRAWBERRY") }
def _town_demand_now(obs, item, step):
    d = 1 if (item != "FERTILIZER" and step % 24 == 0) else 0   # dawn baseline
    if step % 4 != 0: return d
    for shop in unlocked_shops:
        if item in _SHOP_PRODUCTS[shop]: d += 2 if len(prods)==1 else 1
    return d
```
Front-run MELON/MILK/STRAWBERRY/WOOL chỉ khi `_town_demand_now == 0` — i.e. **không kéo sớm khi có shop đang cầu mặt hàng đó** (bán vào demand thì đợi; không demand thì bán sớm tránh decay). Kèm `_repay`: trừ đúng lượng đã kéo ở turn sau (invariant 2-turn giữ nguyên tổng), reserve PICKUP đang thực hiện.
Weed-repair của họ: DIG hôm nay, mai làm intended, nếu còn lệch thì **replay theo trace của chính tape trong 8 bước** để re-sync (ta chỉ queue 1 ngày).

**MỚI so với v15:** (a) town-demand gate (v15 `_sell_lead` chỉ gate `step%4==0`; không kiểm "shop có đang cầu item này không"); (b) 8-step trace-realign; (c) pickup-reserve khi tính lượng bán được.

**YẾU gặp v15:** tape 8C/4S tĩnh, không router shop → gặp draw xấu vẫn chơi như cũ; v15 đã thắng các tape họ nhà boatlee trong roster cũ. **TRANSFER: MED** (gate shop-demand cho sell-lead là 1 dòng điều kiện rẻ, đúng tri thức R39 ta có sẵn).

---

### 2.6 jek1wantaufik — Building a Kaggriculture AI Agent (147 dòng)

Build script: gộp 8 module từ Kaggle Model `jek1wantaufik/buddy/scikitlearn/agric/2` → `submission.py` (dedup imports, strip internal imports), compile-check, smoke 1 game vs random. Không lộ chiến lược (nằm trong Model dataset ngoài). **TRANSFER: LOW** — chỉ là pattern đóng gói multi-file thành single-file (ta đã làm tốt hơn với payload b85+zlib).

---

## 3. TỔNG HỢP CƠ CHẾ ĐỘT PHÁ (xếp theo giá trị với v15)

| # | Cơ chế | Nguồn | Có trong v15? | Giá trị |
|---|---|---|---|---|
| 1 | **Exposure×glut sell-scoring khi gặp clone** (đếm tiles đối thủ → map COW→MILK, SHEEP→WOOL…; glut WHEAT .2/EGG .2/FERT .4/CARROT .7/TOMATO .6/MILK 1.6/STRAW 1.6/WOOL 3.2/MELON 3.6) | hamburger overlay | ❌ | HIGH — không cần biết tape đối thủ vẫn sort được SELL chống double-dump |
| 2 | **Town-demand gate cho sell-lead/front-run** (bỏ qua khi shop đang cầu item; baseline d=1 lúc dawn) | salemali7/boatlee | ❌ (chỉ step%4) | HIGH — 1 dòng, ăn khớp R39/R41 |
| 3 | **Terminal relay 716-718** (walk-to-shed khi distance≤remaining, DROP nếu product-thuần+vừa room, PLACE item tốt nhất; sell hết) | hamburger | ❌ (terminal_liquidation=False) | MED — bảo hiểm endgame kiểu R90, rẻ |
| 4 | **Profile rival bằng public state ở t1** (hands/money → phân loại family tape) | hamburger (Replay Shield) | ❌ (mặc định cùng lineage) | MED — mở front-run cho đối thủ không cùng lineage |
| 5 | **Rival plant-tiles + market-fert-inventory làm feature router mid-game** (t360 swap block 360-431) | yhay 3day | ❌ | MED — lần đầu thấy continuation đổi theo quy mô RUỘNG đối thủ |
| 6 | **Budget guard interval 72-turn** + sales-first ordering | yhay 3day | Guard đang OFF (L33) | LOW-MED — chú ý: L33 kết luận tệ là bản 144; bản 72 chưa A/B |
| 7 | Sell-front ordering (SELL đứng trước BUY trong 10-slot) | yhay 3day guard / hamburger | Một phần (guard off) | LOW |
| 8 | Weed-repair 8-step trace realign | salemali7 | ❌ (1-day queue) | LOW |
| 9 | Harness đo trên 188 external histories + hard-tail metric | yhay fieldbook | ❌ (5 đối thủ local) | MED (methodology) |
| 10 | Block-mining từ replay top theo boundary + fresh-seed A/B | yhay fieldbook | Nguồn gốc ta (đã có) | — |

**CẢNH BÁO termites:** cơ chế 1-2-3 đều là tầng "ngoài cùng" kiểu v12aa/v14 của ta (wrap `agent`, try/except, chỉ đổi `action["market"]`/t716+) → có thể cắm theo đúng pattern layer an toàn đã chứng minh (zero-regression khi no-op).

---

## 4. KHẢ NĂNG KHAI THÁC KHI GẶP v15 (đánh giá đối thủ)

- **yhay 3 notebook:** đã là con cháu của ta — battery chứng minh v15 thắng kme3v10/kme3 10/10. Bàn phím của họ không có gì v15 thiếu. Điểm duy nhất họ hơn: multi-boundary tree (fieldbook) — nhưng chính họ thừa nhận hard-tail 0.6322.
- **hamburger:** clone-detect KHÔNG khớp v15 (profile Tran 8C/6S/6M/26S ≠ v15 route-dependent herd; v15 đổi route theo shop draw) → tầng clone của họ likely tắt khi gặp ta → còn tape thuần + repair + terminal relay. Tape 8C/6S có cấu trúc kinh tế yếu hơn KaggressurE (sells nhỏ, không mass-wheat) → kỳ vọng v15 thắng rõ. Rủi ro duy nhất: `_TRAN_CASHFLOW_ACTIVE` sort notional giúp họ bán đẹp hơn tape gốc.
- **salemali7 (2900):** tape boatlee V16-RC5 + demand-gate front-run — dòng boatlee từng nằm trong roster nghiên cứu cũ của ta và thua v14; gate demand không cứu được việc tape tĩnh không thích ứng shop draw.
- **jek1wantaufik:** không đánh giá được (agent ở Model dataset ngoài) — ghi nhận để theo dõi nếu xuất hiện trên ladder.

## 5. HÀNH ĐỘNG TIẾP THEO (đề xuất cho main agent, KHÔNG thực hiện trong task này)

1. **v16-đề xuất #1 (rẻ nhất):** thêm gate town-demand vào `_sell_lead`/`_front_run`: nếu unlocked_shops cầu item (mapping R41) → bỏ pull-forward. A/B trên battery chuẩn 5×10 trận.
2. **v16-đề xuất #2:** exposure×glut ordering cho SELL khi đối thủ cùng-route phát hiện (đang có `_v14_opp_route` sẵn — dùng tiles đối thủ đếm exposure, glut theo bảng hamburger, chỉ reorder khi cùng lineage) — không đổi tổng lượng, chỉ đổi thứ tự → rủi ro thấp.
3. **v16-đề xuất #3:** bật `_terminal_liquidation` với relay version (716-718) — đo trên seed có tồn cuối.
4. Nếu bật lại budget_guard (sau L33) → thử interval 72 thay vì 144.
5. Cân nhắc mở battery thêm "hamburger-anchor" (tape Tran) làm đối thủ local thứ 7 để đo cơ chế 1-3 chống họ.
