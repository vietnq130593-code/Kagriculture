# PHÂN TÍCH: prvsiyan + tetsutani + flexonafft + indarkarhana (Task 74-d)

> Scope gọn, retry sau timeout lần 1. Nguồn: `research/kaggle_dl/`. Đối chiếu champion hiện tại: **v15** (= v14 kme3v10+price-timing + R90 watchdog; tape 63dfed lineage KaggressurE).
> Agent giải nén thêm: `research/kaggle_dl/unpacked/tetsutani_adaptive__main.py` (148KB, 1009 dòng).

---

## 0. prvsiyan — "The Soil Remembers Rain" (581KB, 103 votes) — lab **V235Combined**

### 0.1 ARCHITECTURE — TAPE YHAY + CHUỖI 8 LAYER V216→V233
- Runtime agent = **AGENT_SOURCE** (99KB, giải nén → `unpacked/prvsiyan_soil__main.py`, 1328 dòng): policy **yhay81 Shop Router 0909 NGUYÊN VẸN** (13 tape × 719, tapes md5 `ae810e80…`; SHOP_PLANS 15 cặp shop đầu tiên → plan 0-12; ROUTE_STEP=144; FINAL_PLAN_STEP=648 → ép về plan 2; repair_weeds queue theo-worker trong ngày; advance_sales kéo SELL sớm 1 turn; liquidate t718 sort theo price×qty) + chuỗi wrapper:
  - **V216**: step 23 — nếu tiền không đủ hire hôm sau (fib 1,1,2,3,5) và shed WHEAT≥3 và giá WHEAT lấp khoảng thiếu → SELL WHEAT×1 (cứu vốn hire day-1).
  - **V217**: idle-farmer starvation rescue — farmer rảnh (PASS) giờ 16-21, ≤2 lần/game, động vật consecutive_unfed≥1 chưa feed → đi PICKUP WHEAT + FEED + quay về; hủy nếu tape còn FEED trong ngày hoặc có queue.
  - **V218**: thu fertilizer cuối mùa bằng ≤3 worker rảnh (TSP bitmask route).
  - **V219**: tomato investment cuối mùa (day 24-29, worker thuê riêng, fertilize day 24/27 chỉ khi giá FERT≤30, bán TOMATO = stock).
  - **V224**: **sales-first reorder** (step≥144): bubble SELL lên trên HIRE/BUY trong list 10 đơn (không đổi thứ tự SELL-SELL, không vượt qua BUY cùng item).
  - **V226**: wheat top-up giới hạn (shortage so với PICKUP WHEAT lượt sau, ≤4 đơn, ≤8/ngày, budget giá+10, 24≤step<696).
  - **V231** ("Moon's later cattle switch"): bước 216-227, điều kiện hẹp (≥3 shop, ≥2 milk-shop, KHÔNG có YARN, giá MILK≥WOOL, farm có COW≥4 & SHEEP≥2, tape có đúng 1 đơn BUY SHEEP 1-2 con) → **đổi nhãn SHEEP→COW trong đơn mua + PICKUP + PLACE**, theo dõi placement bằng pending_places/milk_credit, bán thêm MILK = đúng lượng thu được thêm, chỉ append vào slot SELL MILK sẵn có. Cap 4 con.
  - **V233/V234** ("financed sheep paddock"): day 12 giờ ≤2, eligibility (đúng 10 tile, quadrant {NW,NE,SW}, **2+ YARN_STORE, WOOL≥220, WHEAT≤45**, dải SE y5-6×x5-7 toàn LOCKED, không sót SHEEP) → commit **BUY_LAND(SE) + BUY_ANIMAL SHEEP×6 + BUY WHEAT×6 + 2 HIRE**, budget $7000 + fib hire + reserve 3000/1000 + giá+10/feed; 2 worker chuyên trách mỗi đứa 3 cừu (thang ưu tiên BUILD_PASTURE→DIG→PLACE→FEED→CARE→HARVEST→COLLECT_FERTILIZER); V234 rescue mua thêm ≤6 wheat/ngày; wool/fert "credit" chỉ bán khi có stock thừa.
- **"Soil remembers rain" = thuần văn chương** — KHÔNG có memory về water/fertilize/soil. Memory thực: DayState queue + advanced_sales ledger + telemetry counters từng layer (fail-closed, đếm đủ).
- Notebook = lab paired-experiment: 58 cell discovery → 18 cell confirmation 3 seed; kết luận công khai của chính tác giả: V228/V229 50W-8L; sheep paddock **cả 2 phiên bản vẫn THUA** (cash −15.8k/−17.6k dù cừu khỏe, wool 81→108); panel fresh 72 cell: branch active 0/72 → "không có bằng chứng active-effect mới".

### 0.2 OPENING + FARM
- t0: `BUY WHEAT 13 / SELL WHEAT 13 / BUY WHEAT 13` → t1: 5×HIRE + 2 COW + 2 SHEEP (chữ ký KaggressurE — TRÙNG yhay81 shop-router-0909 đã decode ở Task 74-c).
- Herd theo plan: plan0/2 = 8C6S+3 GOOSE; plan 3-11 = 6C10-11S; plan12 = 4C14S; HIRE 260-277; LAND=2. Sells khủng: plan3-8: WHEAT ~25k, FERT ~18k, STRAWBERRY 13k, WOOL 12.6k.

### 0.3 MARKET
- yhay advance_sales (pull-forward 1 turn, bỏ WHEAT/FERT, tránh bước %72==0 và step<144 %4==0) + V224 sales-first + V231 append MILK + V233 append WOOL/FERT credit + liquidate cuối.

### 0.4 CƠ CHẾ MỚI so với v15
| # | Cơ chế | v15 có chưa | Ghi chú |
|---|---|---|---|
| 1 | **V224 sales-first reorder** (SELL nổi trên HIRE/BUY trong list order) | KHÔNG rõ (v15 _sell_lead đổi timing, không đổi thứ tự trong list) | RẺ (~15 dòng) — nếu engine xử lý order theo thứ tự list thì bán trước mua cùng turn = giảm rủi ro hụt tiền/đủ slot |
| 2 | **V216 day-0 cash rescue hire** | CHƯA | Micro, chỉ đúng khi fib-hire thiếu đúng vài coin |
| 3 | **V217 farmer feed-respect-tape** (rescue đói nhưng kiểm tra tape còn FEED không, queue, ≤2 lần) | GẦN (kme3v10 có feed layer; cách gates khác) | Gate "tape còn FEED hôm nay" đáng học |
| 4 | **V231 relabel SHEEP→COW theo demand** (đổi herd trong tape không đổi geometry) | CHƯA (v15 đổi route portfolio, không relabel) | Ý tưởng "conserved substitution" — cùng hướng indarkarhana §3 |
| 5 | V226 wheat top-up (shortage vs PICKUP kế) | GẦN (V39 R95) | Nguồn độc lập thứ 2 cùng cơ chế → hội tụ |
| 6 | Lab methodology (hash nguồn, freeze seed, đếm activation, cả failure để lại) | = quy trình ta đang làm | — |

### 0.5 TRANSFER VALUE: **MED**
- V224 sales-first + V216 rescue + V217 gates là 3 layer rẻ, dễ port, fail-closed. V231/V233 = thử nghiệm CHƯA thắng (tác giả tự nói thua; activation 0/72 fresh) → không port.
- Base yhay đã thua v15 10/10 (battery Task 74-c) → đối thủ này nguy hiểm thấp; nhưng chuỗi V2xx của họ (Moon/Codex lineage) là nguồn layer-guard dày đang tiến hóa — nên theo dõi.

---

## 1. tetsutani — "Adaptive Farming Strategy" (195KB, 142 votes) — `BL-Kawashigi-Adaptive-R1-V19Core-L3F50-P100B12-LayoutFallback`

### 1.1 ARCHITECTURE — TAPE 5-ROUTE + 10 LAYER GUARD
- **Không phải planner.** 5 tape full-game 719 action (b85+zlib nhúng): `10C4S_3Q` (milk-support), `8C6S_3Q` (generalist, default), `6C8S_3Q` (yarn thứ 3), `6C12S_4Q_FIRST_YARN`, `6C12S_4Q_SECOND_YARN` + **5 bản `_LEGACY_` từng route** (layout cũ để chống 1 agent cụ thể — xem 1.4).
- **Router 1 quyết định, đọc 1 lần**: `_kawa_route_label(obs)` — vị trí YARN_STORE trong 3 shop unlock đầu + milk-support shop (PIZZA/ICE_CREAM/SMOOTHIE) → chọn tape. Sau đó KHÔNG đổi route toàn trận (giống v15 về mặt 1-lần-chọn, khác ở tín hiệu: v15 dùng 2 shop đầu + portfolio 13 tape yhay).
- **Memory theo seat** (dict key 0/1): `_WEED_STATE` (repair), `_SHIFT_STATE` (due-ledger preempt), `_V17_R5_STATE`/`_V17_MD_STATE` (latch đối thủ), `_KAWA_LAYOUT_FALLBACK` (latch layout). Đó là toàn bộ "state" — không có model soil/market.
- **Pipeline agent()** (thứ tự cố định): weed_repair → feed_guard (TẮT) → room_evac → repay_shift → rank_sell_slots → preempt_shift → r5_counter → md_counter → room_guard → terminal_liquidation → align_hands.

### 1.2 OPENING + FARM (đo từ tape giải nén)
- **Chữ ký t0 cả 10 tape giống hệt**: farmer=BUILD_PASTURE; market = 5×HIRE + BUY_ANIMAL COW×2 + SHEEP×2 + BUY_SEED WHEAT×7 + MELON×12 + BUY_PRODUCT WHEAT×6 → t1: PICKUP SHEEP + 5 hand đi WEST/NORTH + SELL WHEAT×3. = **chữ ký KaggressurE 5-HIRE/2C/2S** (họ hàng yhay81, Task 74-c).
- Herd: theo route như tên (10C4S / 8C6S / 6C8S / 6C12S ×2), GOOSE=0, LAND=2 (yarn routes LAND=3).
- Plant tổng mùa (8C6S): WHEAT 125, STRAWBERRY 42, MELON 12, CARROT 5. Không plant TOMATO.
- SELL tổng mùa (8C6S): **FERTILIZER 2932** (nòng cốt doanh thu!), WHEAT 856, MILK 279, STRAWBERRY 274, WOOL 120, MELON 72, CARROT 11. Tape 6C12S_SECOND_YARN: WHEAT 1641 + WOOL 270.

### 1.3 MARKET — bán theo tape + 4 lớp can thiệp
1. **`_rank_sell_slots`**: xếp lại THỨ TỰ SELL trong 10 slot market theo `_order_score` = impact × (1 + 0.25×urgency); impact = q×(quote_hi − quote_sau_khi_bán) dùng `_MARKET_PARAMS` (bảng giá engine chính xác, trùng georgymarin/salemali7); urgency = (excess/demand_per_day)/10 — demand tính từ unlocked_shops qua `_SHOP_PRODUCTS` (shop 1 món ×2) + Town Center 1 lần/ngày.
2. **`_preempt_shift` (clone preempt)**: `_clone_distance` = |Δhands| + 3|Δquadrants| + Σ|Δcounts| trên 11 loại tile (WEED tính luôn!) ≤ 6 → kéo SELL premium (STRAWBERRY/MELON/MILK/WOOL) từ step+1 lên now, batch ≤12, fraction 1.0, chỉ khi step 120–680, market <10 đơn, có `_projected_shed` (mô phỏng DROP/PLACE vào 4 ô shed) đủ hàng. **`_repay_shift`: ledger due[step+1] trừ đúng lượng đã kéo** — chống double-sell (giống Kaito v48 debt).
3. **`_v17_r5_counter`**: LATCH step≥24, đối thủ SHEEP≥4 & COW≤3 → dùng **`_V17_R5_MARKETS` (băng market 719 turn ĐÓNG BĂNG của 1 họ agent công khai)**: nếu step+3 họ định SELL premium → mình bán trước 50% lượng (chỉ khi town demand KHÔNG refill item ở step hoặc step+1 — gate chống tự phá giá; trừ pickup reserve).
4. **`_v17_md_counter`**: LATCH step≥160, (quadrants≥2 & COW≥4 & SHEEP≤2) hoặc COW≥9 → dùng `_V17_MD_MARKETS` băng khác, bán trước **200%** lượng step+1. (R5/MD = 2 họ public agent mà tác giả freeze replay.)
5. **`_terminal_liquidation`** step≥716: bán sạch shed theo `_LIQUIDATION_ORDER` (CARROT→…→WOOL), step 718 bán all.
6. **`_v17_room_guard`/`_room_evac`** (step≥648, hour 21-23): tính shed 100 + carried + produced − consumed + buys − sells → nếu tràn thì SELL theo priority WOOL→MILK→EGG→…; evac 1 worker về shed DROP + bán hour 23.

### 1.4 CƠ CHẾ MỚI so với v15 (mức code)
| # | Cơ chế | v15 có chưa | Ghi chú |
|---|---|---|---|
| 1 | **Legacy-layout fallback**: bước 24–72 đọc tile đối thủ, nếu đúng fingerprint WHEAT=5,MELON=5,COW=1,SHEEP=4,PASTURE=0 + money≤12 → đổi cả 5 tape sang bản `_LEGACY_` (layout khác) | CHƯA | Chống 1 agent "layout-clone" — phát hiện ai đó copy layout mình thì đổi layout toàn trận. Rất rẻ (~25 dòng), chống chính v15? Không: fingerprint quá hẹp (1C/4S) |
| 2 | **R5/MD family counters bằng băng đối thủ đóng băng** + gate town-demand refill | CHƯA (v15 có _sell_lead nhưng theo giá, không theo băng đối thủ) | Chỉ ăn 2 họ agent cụ thể; v15 (sheep 6-11, cow 6-8) KHÔNG khớp latch R5 (sheep≥4&cow≤3) lẫn MD (cow≥9 hoặc cow≥4&sheep≤2) → **tự tắt khi gặp v15** |
| 3 | **Sell-slot ranking impact×urgency** (xếp thứ tự SELL trong 10 slot theo impact ước lượng + overload so với demand/ngày) | GẦN (v15 _sell_lead/front_run theo timing; KHÔNG rank thứ tự) | Order-only, an toàn kiểu v12aa; khác hamburger exposure (không cần tape đối thủ) |
| 4 | `_repay_shift` debt ledger horizon=1 | v15 front_run có guard riêng; debt ledger tương tự SaleLedger pilkwang (74-e) | Ăn khớp đề xuất 74-c/74-e |
| 5 | `_projected_shed` mô phỏng DROP/PLACE 4 ô shed access + capacity 100 | CHƯA ở tầng này | Dùng cho preempt + room guard |
| 6 | Fingerprint 11-loại-tile gồm WEED/quadrant cho clone_distance | v15 dùng route-label; Kaito 1-NN dùng 12-feature | Tương đương |

### 1.5 TRANSFER VALUE: **MED-HIGH**
- **Rank sell slots theo impact×urgency** (~40 dòng, order-only, dùng bảng giá đã có sẵn trong v14) — khả thi cao, không đổi production.
- **Debt-ledger repay cho _front_run/_sell_lead của v15** — 3 nguồn độc lập (Kaito v48, pilkwang SaleLedger, tetsutani _repay_shift) cùng làm → mạnh.
- R5/MD counters KHÔNG transfer trực tiếp (đối tượng là 2 họ agent khác; băng đóng băng không có trong tay); nhưng **ý tưởng**: freeze băng market của kme3/kme3v10 (registry có sẵn) làm counter tương tự nếu gặp họ.
- Legacy-layout fallback: LOW-MED (phòng bị copy-layout).
- Đối đầu với v15: counters tự tắt; preempt chỉ kích hoạt khi clone_distance≤6 (v15 herd 8C6S/6C10S + hands 10 → distance thường >6).

---

## 2. flexonafft — "Multi-Route Farming Agent" (117KB, 93 votes) — **DUPLICATE CỦA tetsutani adaptive**

### 2.1 Phát hiện chính
- Notebook chỉ 28 dòng: giải nén `SOURCE_B85` (b85+zlib) → `unpacked/flexonafft__main.py` (148KB, 1013 dòng).
- **Diff với `unpacked/tetsutani_adaptive__main.py` = CHỈ 4 dòng docstring** (1009 vs 1013 dòng, phần code + tapes + `__version__='BL-Kawashigi-Adaptive-R1-V19Core-L3F50-P100B12-LayoutFallback'` GIỐNG HỆT).
- Docstring flexonafft: *"BL-MDgogo-10C4S-R0: public-replay consensus route with generic execution guards. This is a behavioral reconstruction from twelve public traces... Clone preemption is disabled in this experiment."* — nhưng code thật vẫn có `_PREEMPT_ENABLED = True` (docstring NÓI DỐI/lạc hậu).
- Như vậy "multi-route" = đúng 5 route của tetsutani (yarn-first/second/third, milk-support, generalist); "switch theo điều kiện gì" = vị trí YARN trong 3 shop unlock đầu (xem §1.1). Không có gì mới.

### 2.2 Ý nghĩa meta
- Đây là họ **"BL-" (behavioral reconstruction)**: 1 codebase gốc được re-post/nhãn lại nhiều lần (BL-Kawashigi, BL-MDgogo) — vote 142 + 93 = cùng 1 agent trên leaderboard ⇒ **nhiều "đối thủ" meta thật ra là 1 agent**. Khi đếm độ phủ meta/top-ladder phải dedupe theo fingerprint code, không đếm theo tên notebook.
- "Reconstruction from 12 public traces" của team MDgogo/Kawashigi → tape V19Core là consensus tổng hợp, không phải source riêng.

### 2.3 TRANSFER VALUE: **LOW** (0 delta so với tetsutani) — chỉ giá trị trừ lg ưu tiên phân tích tetsutani (§1).

---

## 3. indarkarhana — "Shape the Shop, Work the Pasture (TOP 10)" (50KB, 94 votes) — chuỗi E749→E776

### 3.1 ARCHITECTURE — TAPE KENJO MEDOID + MẠNG GUARD 6 LAYER + 2 CAN THIỆP CẤU TRÚC
- Archive 13 file (giải nén → `unpacked/indarkarhana/`). Chuỗi wrapper:
  - **E749A** "niklita consensus network": tape replay **NIklitaCheporev ep101408728 seat1** + guard: weed_repair (DIG+replay 8 bước, gồm BUILD_COOP), `_cap_sales` (shed projection + pickup_reserve), `_assign_sell_slots` (xếp SELL theo **contested_value**), `_fund_market` (**sổ cái tuần tự theo thứ tự list đơn**: SELL cộng tiền ngay trong lượt → HIRE fib / BUY_LAND theo unlocked / BUY_ANIMAL cần shed room / BUY_PRODUCT mua theo giá biên inventory−1; đơn không đủ tiền bị cắt bớt SLICE, không bỏ cả đơn).
  - **E750A**: sửa `_project_shed` tính cả PLACE (đặt vật xuống shed-aware).
  - **E766A**: **đổi tape** sang Kenjo1209 ep102192548 seat1 (medoid 6 route Hamming từ E754; khớp boundary 72/86) — 9C+5S, HIRE 290, LAND 2.
  - **E773A** "demand-aligned conserved pasture": **5 bundle COW/SHEEP** ở step cố định (88/150/169/176/313) — mỗi bundle = chuỗi BUY+PICKUP+PLACE cùng 1 con vật; áp lực = `wool: 2×YARN_STORE + WOOL_price/200` vs `dairy: PIZZA+ICE_CREAM+SMOOTHIE + MILK_price/160`; gap ≥ +1.0 → đổi nhãn COW→SHEEP (cap 3), gap ≤ −1.0 → SHEEP→COW (cap 1); **bán MILK/WOOL ở slot cũ được tái phân bổ** theo revenue-walk + demand_score (chọn item bán mỗi slot bằng mô phỏng giá engine).
  - **E774A**: terminal frontier — step 718 append SELL mọi item trong shed (rank theo revenue walk, chừa 10 slot).
  - **E775A** "latent pasture activation": step 313, nếu geometry khớp (8 unit quanh shed cross, hires_today=7, đúng 1 đơn BUY_ANIMAL 1 con + 3 HIRE, tiền ≥ animal+hire+1000, shed ≤90) → **mua 2 con thay 1 + thêm 1 HIRE (hand thứ 11)**, hand mới delivery con vật vào pasture trống (5,3) đã được service sẵn trong 4 bước 314-317.
  - **E776A**: engine-exact delivery repair — sửa lại 3 bước delivery (314 PICKUP @ (5,4), 315 NORTH, 316 PLACE @ (5,3)) nếu vị trí/inventory khớp expected, sai 1 chi tiết nào là CANCEL cả bundle (fail-closed).
- Memory: `_STATE`/`_LAST_DIAGNOSTIC` theo seat — chỉ state activation + weed transactions + đếm guard.

### 3.2 OPENING + FARM (Kenjo medoid tape)
- t0: farmer PASS, market rỗng; t1: BUY_PRODUCT WHEAT 5 + BUY_SEED WHEAT 7 + MELON 12 + 5×HIRE + 2 COW + 2 SHEEP (biến thể chữ ký KaggressurE — mua gạo trước, hire 5).
- Herd 9C+5S, LAND 2, HIRE 290; +E775 → 10C6S/9C6S + 11 hands. Không GOOSE.

### 3.3 MARKET
- **PARAMS giá engine chính xác** (khớp georgymarin/salemali7/Kaito + thêm **shape "hinge"** = `ratio + 8·max(0,ratio−1)²` cho CARROT/TOMATO/EGG below-equilibrium — công thức trùng pilkwang market_primitives; 3 nguồn độc lập giờ cùng 1 bảng).
- `_contested_value(item, inv, q)` = Σ giá block đầu (bán ngay) − Σ giá block sau vị trí q (đối thủ bán ngay sau) → **thước đo adversarial trực tiếp**: xếp slot SELL cao nhất cho đơn gây tổn thất lớn nhất cho người bán kế tiếp (cap 60 đơn).
- `_fund_market` = ledger tuần tự: bán trước mua trong CÙNG list 10 đơn (hiệu ứng: tiền từ SELL financing HIRE/BUY ngay lượt đó).
- E773 realloc SELL MILK↔WOOL theo revenue-walk; E774 terminal liquidation tất cả item.

### 3.4 CƠ CHẾ MỚI so với v15
| # | Cơ chế | v15 có chưa | Ghi chú |
|---|---|---|---|
| 1 | **Contested-value slot ranking** (bán thứ tự gây hại tối đa cho người bán sau) | KHÔNG (v15 rank theo price-timing/waterfall riêng) | Ngắn (~25 dòng), cần bảng giá sẵn có; khác impact-score (tự thân) ở chỗ này đo **tổn thất đối thủ** |
| 2 | **Sequential funding ledger** (SELL cộng tiền trong-lượt cho HIRE/BUY sau nó trong list) | GẦN (v15 _budget_guard?) nhưng không slice đơn theo sổ tuần tự | Rẻ, chống đơn bị reject cả cụm |
| 3 | **E773 pressure formula** wool=2·YARN+price/200, dairy=3-shop+price/160, gap ±1.0, cap đối xứng 3:1 | KHÔNG | Công thức demand scoring đầu tiên thấy normalize giá về base — dùng được cho mọi quyết định herd |
| 4 | **Latent pasture activation** (mua thêm 1 con + 1 hand vào pasture đã service sẵn) | KHÔNG | Hard-code step 313/314-317 cho tape Kenjo — KHÔNG port trực tiếp cho v15 (tape khác), nhưng ý tưởng "pasture thừa + service sẵn thì nhét thêm con" đáng A/B |
| 5 | Terminal MILK/WOOL frontier (bán hết ở 718) | CÓ (_terminal_liquidation v14) | Trùng khớp |
| 6 | Hinge shape cho 3 item (CARROT/TOMATO/EGG) | v15 dùng MARKET_PARAMS như Kaito (linear/log) | Kiểm chứng chéo: pilkwang + indarkarhana cùng hinge → có thể chính xác hơn cho vùng under-equilibrium |

### 3.5 TRANSFER VALUE: **MED-HIGH**
- Contested-value ranking + sequential funding ledger: 2 layer ~50 dòng, order-only, dùng bảng giá có sẵn.
- Pressure formula E773: 5 dòng, dùng ngay cho router herd hoặc relabel gate.
- E775 latent pasture: cần đo trên tape v15 trước (không hard-code step được).
- Đối đầu: đây là bản top-10 thật (md: diagnostic 136-14 vs current top-10, .907) — **không được xem nhẹ như yhay-family**; base tape Kenjo medoid (9C5S + 290 hire) là production race mạnh, v15 CHƯA gặp trong battery.

---

## 4. (Phụ) prvsiyan "The Moon Counts Melons" (1MB) — grep nhanh
- Lab đồng hành của soil-remembers: **V232Late** = cattle substitution "chờ shop thứ 3 visible rồi đổi sheep→cow" trên feed baseline; default agent có **V226A feed repair** (mua đúng shortage wheat ≤4/lượt, ≤8/ngày, skip dawn/route-boundary/ngày cuối).
- Số liệu public của chính tác giả: Soil 33 rating 1828.4 (27W-2L), Soil 32 = 2282.2; Moon 37 inactive sau 3 wins, 872.7 → **cả họ Soil/Moon lab hiện nằm dưới mốc 2300**, không phải mối đe dọa ngắn hạn.
- Cùng chuỗi V2xx như §0 → không phân tích sâu thêm.

---

## 5. TỔNG KẾT — 6 CƠ CHẾ ĐÁNG CHÚ Ý NHẤT (đề xuất cho v16)

1. **Contested-value SELL ranking (indarkarhana E749)** — `first_block − displaced_block` theo giá engine; adversarial trực tiếp, order-only, ~25 dòng. [HIGH]
2. **Sequential funding ledger (indarkarhana E749 `_fund_market`)** — trong list 10 đơn: SELL cộng tiền trước, HIRE/BUY sau được slice đúng số tiền; chống reject cụm. [HIGH — cần xác nhận engine xử lý đơn theo thứ tự list]
3. **Debt-ledger repay cho pull-forward sells** — lần 3 (Kaito v48 → pilkwang SaleLedger → tetsutani `_repay_shift`/prvsiyan `subtract_advanced_sales`); mọi họ lớn đều có (kể cả prvsiyan V1 `subtract_advanced_sales`) → v15 nên thêm nếu thiếu. [HIGH]
4. **Legacy-layout fallback (tetsutani)** — fingerprint tile đối thủ bước 24-72 → đổi cả bộ tape sang layout khác; v15 herd 8C6S/6C10S không khớp fingerprint hẹp (1C/4S) nhưng cơ chế "đổi layout khi bị copy" đáng có ở tầng anti-clone. [MED]
5. **E773 pressure formula** (wool 2·YARN+price/200 vs dairy 3-shop+price/160, gap ±1, cap 3:1) + **E775 latent-pasture** (nhét 1 con + 1 hand vào pasture service-sẵn) — 2 đòn cấu trúc mới ở tầng production. [MED — cần A/B]
6. **Dedupe meta theo fingerprint** — flexonafft ≡ tetsutani adaptive (chỉ khác docstring), cùng __version__ BL-Kawashigi; + Soil/Moon là 1 gia đình V2xx trên tape yhay. ⇒ registry đối thủ nên thêm: `kawashigi_adaptive` (tetsutani+flexonafft), `indark_e776` (Kenjo medoid 9C5S), và NHẮC LẠI rằng prvsiyan soil/moon = yhay-family (đã thua v15 10/10). [MED]

**Lưu ý đối đầu:**
- tetsutani/flexonafft (Kawashigi V19Core): counters R5/MD **tự tắt vs v15** (latch sheep≥4&cow≤3 hoặc cow≥9 không khớp herd v15); preempt chỉ kích hoạt khi clone_distance ≤6 (11 loại tile, gồm WEED + quadrants) — v15 hands 10 + herd 8C6S thường >6.
- indarkarhana E776: tape Kenjo **mới ngoài registry** (9C5S, HIRE 290, t0 PASS/t1 mua hạt) + guard dày + 2 can thiệp cấu trúc → nên build proxy `indark_e776` cho battery (source đã có sẵn 13 file trong `unpacked/indarkarhana/`).
- prvsiyan soil/moon: yhay-family + layer V2xx mỏng, self-report thua; rating public 1828-2282 → ưu tiên thấp.
