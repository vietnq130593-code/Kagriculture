# BÁO CÁO NGHIÊN CỨU META KAGGLE — Định hướng cải tiến v18 (K0006)

**Task ID:** 8-b · **Ngày:** 2026-09-16 · **Agent:** general-purpose (subagent)
**Đối tượng:** v18 = jaxa623 K0006 = Ahmed V43 + 4 market micro-edges (front-load SELL, advance-2, horizon-24, open-50 round trip)
**Kết luận 1 dòng:** Meta đã hội tụ về farm-plan (9c4s/8c4s, 3 quadrants, 10-12 hands) — **toàn bộ edge còn lại nằm ở market timing**, đúng hướng v18 đang đi; có ≥4 cơ chế mới giá trị cao chưa có trong v18 (preempt fertilizer, impact-aware ordering, feed-buy slot-0, town-demand gate).

---

## MỤC LỤC

1. [Phạm vi tư liệu & phương pháp](#1-phạm-vi-tư-liệu--phương-pháp)
2. [Meta snapshot hiện tại](#2-meta-snapshot-hiện-tại)
3. [Timeline tiến hóa c14→C95 của Rayk Kretzschmar](#3-timeline-tiến-hóa-c14c95-của-rayk-kretzschmar)
4. [Kỹ thuật mới chưa có trong v18](#4-kỹ-thuật-mới-chưa-có-trong-v18)
5. [Bẫy đo lường & thống kê sai](#5-bẫy-đo-lường--thống-kê-sai)
6. [Kết quả âm tính — danh sách KHÔNG làm lại](#6-kết-quả-âm-tính--danh-sách-không-làm-lại)
7. [So sánh với 4 edges của jaxa623: TRÙNG vs BỔ SUNG](#7-so-sánh-với-4-edges-của-jaxa623-trùng-vs-bổ-sung)
8. [Top 10 ý tưởng cải tiến v18 (xếp theo impact × tin cậy)](#8-top-10-ý-tưởng-cải-tiến-v18)
9. [Next actions](#9-next-actions)
10. [Phụ lục: thông số engine đã verify từ code](#10-phụ-lục-thông-số-engine-đã-verify-từ-code)

---

## 1. Phạm vi tư liệu & phương pháp

Đã đọc **toàn bộ 12 file markdown** trong `kaggle-research/extracted/` + `jaxa623_markdown.md`, và đối chiếu code khi cần kiểm chứng:

| Nguồn | Votes | Nội dung chính | Kiểm chứng code |
|---|---:|---|---|
| jaxa623 — Beyond 48-0 | ~10 (mới) | 4 edges = nền v18; 2 trap đo lường | ✅ decode K0006 wrapper (HORIZON=24, OPEN_UNITS=50, frontload A/B/C, advance LOOKAHEAD=2 PREMIUM-only) |
| raykkretzschmar — Findings zero→top meta | 192 | Nhật ký c14→C95, ~3.214+ game local | ✅ C94/C95 blob + BEST_LABEL `c94_feed_first_fert_split`, `c95_top20_wheat_counter` |
| georgymamarin — What 2600+ farms do | 43 | Dataset ladder + fingerprint, caveats thống kê | — |
| cjlcjlcjl — Live meta guide | 75 | Daily meta report 08-07→08-11, modal farm, sell rhythm | — |
| nathanjacob — Turn-1 clusters | 36 | 33 clusters, C9 opening, pipe-4, colosseum 200 game | — |
| nathanjacob — Pipe-7 microstructure | 49 | Round-trip Q=5 thay 70; 179-1 tournament | ✅ decode blob: `_OPEN_UNITS=5`, guard thay `[BUY 5, BUY 10, SELL 60]` → `[BUY 5, SELL 5]` |
| destbreso — X-ray your agent | 42 | Telemetry/forensic toolkit, shape của #1, ngôn ngữ agent | — |
| alperen — V62 MetaBalance | 3 | Chỉ là rebuild artifact (score 2763.2), không công bố cơ chế | — |
| kaitofukami — v43 sparse shop hybrid | 78 | 2 nhánh YARN, không classifier, 103/128 | blob nén, không decode (markdown đủ rõ) |
| boatlee — V16-RC5 8c4s | 313 | 8C/4S route + premium market lead (debt-tracked) | ✅ `_front_run`/`_repay`/`_town_demand_now` đầy đủ |
| ahmedberatozer — V43/V44/V45 | 88/32/85 | Evaluation chi tiết 3 version | — |
| raw/comp_kernels_recent.json | — | 50 notebook mới nhất (chạy 09-14→09-16) | ✅ phát hiện pipe-8, order-sequencing, open-78… (xem §9) |

---

## 2. META SNAPSHOT HIỆN TẠI

### 2.1 Bảng xếp hạng & người chơi top (mốc gần nhất trong tư liệu)

| Thời điểm | Top players | Ghi chú |
|---|---|---|
| LB 2026-08-12 (cjlcjlcjl) | **カワシギ 3179.7** · researchstudio.site 3174.3 · Kaito Fukami 3133.9 | Kaito = tác giả sparse hybrid (78v) |
| destbreso capture 2026-08-30 | "#1" (không tên) — hình dáng: Quadrant 2 **ngày 5**, **7 bò**, ~**280 CARE**, 13 tile fallow cuối mùa, **$442 stranded** | Đây là benchmark, không phải target |
| Local BT cuối của Rayk (18 agents) | **C94 fertilizer-only BT 1837** > live Huyimin 1798 > wheat+fert capped 1779 > live Kaito 1724 > five-wheat-first 1714; C90/91/92 chỉ 1380 | C-field đã bị các counter market vượt |
| jaxa623 K0006 lúc ghi notebook | Ladder **2.663 và đang leo** (128-0 vs V45 local) | = v18 của chúng ta |

**Điểm số chuẩn hoá:** ladder Elo chỉ tính W/L/T, margin tiền KHÔNG đổi rating (Rayk §2.4, §4.8: C70 đi 83-5 +14.196 mean margin nhưng kẹt dưới 3000 vì "rating rewards wins, not surplus coins"). → Mục tiêu tối ưu là **xác suất thắng match**, không phải margin.

### 2.2 Thành phần farm modal (diễn biến 08-07 → 08-11, cjlcjlcjl)

| Ngày | Modal farm | Share | Money median |
|---|---|---:|---:|
| 08-07 | 8c + 6s · 9 wheat · 10 hands · NE+NW+SW | 25% | 109.071 |
| 08-08 | 8c + 6s · 4 wheat · 11 hands | 54% | 78.020 |
| 08-09 | 8c + 6s · 4 wheat · 11 hands | 26% | 77.737 |
| 08-10 | **9c + 4s · 1 wheat · 10 hands** | 29% | 82.237 |
| 08-11 | **9c + 4s · 1 wheat · 10 hands** | 30% | 84.151 (tăng 3 ngày liên tiếp) |

- Trục phân hóa chính = **số cừu** (9c4s ×89 vs 9c5s ×73 vs 9c1s ×17); melon early-seeds hồi phục 4.9→6.3.
- Đến 08-08 (Rayk §4.7): 11/12 team top hội tụ 3-quadrant, 8 cows/6 sheep/23 strawberry/31 wheat. Refresh 09-08: **một field hash duy nhất xuất hiện trong 144/200 episode của 40 team**; rank 3-20 giống nhau 99-100% về field actions.
- **SE (quadrant 4) gần như không ai mua** (≈0% top); refresh C95: "leaders share almost the same public farm route — differences are **sale timing and private inventory**".

### 2.3 Sell rhythm & winner/loser (band Elo≥3100, 08-11, 296 players)

| Product | Ngày bán đầu | Batch TB |
|---|---:|---:|
| Fertilizer | day 4 | 4.9 |
| Wool | day 6 | 9.8 |
| Wheat | day 8 | 11.6 |
| Melon | day 10 | 7.7 |
| Milk | day 11 | 7.7 |
| Strawberry | day 15 | **15.4** (3 ngày trước: 9.9→14.1→15.4) |

- **Winner bán strawberry ngày 14, loser ngày 16** — khoảng cách 2 ngày, đang mở rộng (điểm nhấn "sell before their big harvest").
- Giá premium rơi vách đá sau ~60-80 units oversupply (wool/strawberry/milk); melon ~158; wheat/egg ~3000 (không bao giờ sập) → sell metered 4-8 units/order (cjlcjlcjl §4).
- Cash curve median: d5=545 → d10=2.172 → d15=11.782 → d20=36.414.

### 2.4 Phân loại agent trên ladder (destbreso X-ray)

| Lớp | Đặc hiệu | Ai thuộc lớp này |
|---|---|---|
| PURE_REPLAY | trace byte-identical mọi game | kakutei (~3136), venks (~3117), Wufang Hong (~3146, 5/6 game) |
| REPAIRING_SCRIPT | 1 plan + market channel phản ứng | **phần lớn field** ("most of the field looks like this") |
| SHOP ROUTER | fork plan tại turn 72/144 theo shop draw | V43-family (yhay81 route map), Kaito sparse |
| LIVE POLICY / ADAPTIVE | plan đổi trong cùng world | Seb (~3204, 35-66% identical), **カワシギ** (language 0.89/0.15/0.00 — brancher rồi compose) |

- Consensus staffing (490 seat-seasons): 4 hands đến day 4 → ramp 8→11 đến day 10 → **12 hands từ day 13**; IQR 0-2 hands mọi ngày.
- Leader đi bộ **53.8%** unit-turns (mid-table 42.9%, idle 3.8% vs 11.8%) — "PASS là thứ không có gì ở đầu kia".
- **81% top-50 = cluster C15 (v40 megacluster của Ahmed)** (nathanjacob); top-8 đều là singleton độc đáo. → Field = mirror soup; **edge gần-clone là quan trọng nhất**.

### 2.5 Hướng dịch chuyển meta (tổng hợp)

1. Farm composition đã bão hòa (9c4s/8c4s) → **cuộc chiến chuyển hoàn toàn sang market execution** (bằng chứng mạnh nhất: c18 chỉ đổi 20 field-turns nhưng 112 market-turns mà vẫn vượt hẳn; C95 refresh xác nhận).
2. Timing arms race đang leo thang theo trục **horizon/advance**: horizon 3 (field hiện tại) → 4 (C68 mặc định) → 8 (V44 khi gặp clone) → 24 (jaxa623 optimum) — mỗi bên cố quote sớm hơn.
3. Counter-meta xuất hiện: feed-denial + fertilizer preemption (Rayk C94), round-trip opening attack (V45/jaxa623, và **2 live rival đã dùng open-78 chống Ahmed**), mirror counter (leoprovorov).
4. Đỉnh cao ladder đang chuyển sang **adaptive/live policy** (カワシギ, Seb) — nhưng phần lớn field vẫn là script → dùng adaptive một cách hẹp, có gate (Kaito: "thêm classifier để giải thích 25 loss = lặp lại sai lầm v42").
5. Research frontier công khai 09-16 (từ comp_kernels_recent): `pipe-8-clean-opening`, `wheat-microstructure`, `beyond-48-order-sequencing` (fork notebook jaxa623!), `cloning-v45-open-78-experiment`, `capacity-release`, `terminal-logistics`, `hour-4-financing-allocator` — tất cả đều **market/timing microstructure**, xác nhận thêm hướng đi.

---

## 3. TIMELINE TIẾN HÓA c14→C95 CỦA RAYK KRETSZSCHMAR

| Gen | Ý tưởng | Kết quả đo được | Bài học chuyển giao |
|---|---|---|---|
| c14 | Chỉ nhận replay-tape lặp lại qua nhiều đối thủ (senkin13: 8c/6s/7 strawberry) + cleanup 8 turn cuối | 27-3 vs c11/12/13; ladder 2182.2 | Chọn tape theo **độ ổn định**, không theo score đơn lẻ |
| c15 | + clone-aware premium front-run 1 turn (từ Hamburger) | 14-2 vs base | Timing rule làm việc thật, không chỉ "trang trí" |
| c16 | Refresh base khi 5 leader hội tụ (VN-Orion tape ổn định) | c16 control 7-7-2 vs Superallen (cùng meta = cùng policy) | Hội tụ leader = tín hiệu refresh |
| c18 | Giữ farm, thay 112 market-turns (Ueddy premium liquidation) | 35-5 (+3.161) vs c16; 23-17 vs Anton | **Edge nằm ở inventory-sale timing, không phải herd** |
| c27 | Terminal controller 712→**717** (step 718 chạy được, index 719 KHÔNG) | 90-10 promotion gate | Chi tiết engine falsifiable đáng tiền |
| c45 | Debt-tracked 2-turn sale shift | 3085.4, rank 9 live | Advance bảo toàn tổng 2 turn |
| (rejected) | Fixed horizon 25 | Thắng finalist gate nhưng **0-6 vs C45** trên seed mới | "Aggregate wins vs weak agents giấu parent regression" |
| c68 | Field THUNDER + **online horizon inference** (fit 1-6, default 4) | 342-18 final block, 0 errors | Chỉ đua đúng khoảng cách đối thủ đua |
| C70/C71 | **Impact-first ordering** (GiovanniCR market trace + sort premium SELL theo price impact) | C71 31-9 vs C70; BT 1996 vs 1953 | MELON/STRAWBERRY/MILK/WOOL đi trước; WHEAT/FERTILIZER giữ timing an toàn |
| C72 | **One-step premium banking** (chỉ khi ≥$2.000 giá trị, ≤1 bước tới shed, chỉ thay PASS/move) | 109-11 vs 15 agents; +168.5 cash day-15; 29-11 vs C70 | Ngưỡng sắc: 500/1000/2-bước đều thua 0-8 |
| C90-C92 | Weed repair 3 tầng (idle→future-use→blocked-action) | C92: -7.288 → **+3.455** trên tape DePie; BT 1876 rank-1 (10 agents) | Chỉ sửa weed khi chặn hành động sản xuất NGAY |
| C93 | Quadrant 4 (SE $4.000) | **0-40 vs C92** (−3.885); Seb routes thua 14.608-36.980 | Broad negative — bỏ |
| C94 | **Feed-first slot-0 + fertilizer preempt cap 10** | Held-out 174-6 (96.7%); 18-agent rank 1 (88-14, BT 1837); thắng C90/91/92 6-0 | Bảo vệ feed trước, chỉ advance fertilizer |
| C95 | + wheat advance cap 10 (top-20 refresh) | 112-8 vs top-20 medoids (93.3%); +72-94 coins vs Kaito/Ueddy/JALKARNA/Efe | Response cho population hiện tại |

**Chuỗi sáng kiến của Rayk tổng cộng ~3.214 game local, 0 lỗi runtime.**

---

## 4. KỸ THUẬT MỚI CHƯA CÓ TRONG v18

> Đối chiếu trực tiếp với code wrapper của K0006 (đã decode): v18 hiện có (a) reorder [SELL không-wash] → [BUY_PRODUCT + wash-SELL] → [còn lại], có simulation guard 2 mức áp suất; (b) advance 2-turn lookahead, CHỈ premium (STRAWBERRY/WOOL/EGG/MILK/MELON/CARROT/TOMATO), protect first-sell (feed credit), skip dawn-turn & step≥718; (c) HORIZON=24 override `_R37_HORIZONS`; (d) turn-0 `[BUY 50, SELL 50]` thay `[BUY 5, BUY 10, SELL 60]`.

### 4.1 Fertilizer one-turn preemption (Rayk C94/C95) — **mạnh nhất**
- **Cơ chế:** khi tape sẽ BÁN fertilizer ở turn sau → bán ≤10 units ngay turn này, **trừ đúng lượng đã moved** khỏi lệnh bán turn sau (debt). C95 mở rộng sang wheat cap 10 (fertilizer hạ cap 5).
- **Bằng chứng:** 11 live-loss của C92 chung 1 cơ chế — "đối thủ bán fertilizer/wheat đúng 1 turn trước batch của C92, production không đổi, chỉ thứ tự đã lật match-up **5.300-5.700 coins**". C94 held-out 174-6 (96.7%); tournament 18 agents rank 1 (88-14, BT 1837), thắng C90/91/92 6-0; **fertilizer-only thắng wheat+fertilizer 6-0** (mean margin chỉ +27 — tối ưu win-prob chứ không phải margin).
- **Vì sao v18 chưa có:** `advance_sales` của jaxa623 **loại trừ tường minh WHEAT và FERTILIZER** (comment: "never WHEAT = animal feed, never FERTILIZER = field input").
- **Rủi ro:** V43 có finite fertilizer planner + sale-credit overlay (funding feed purchase từ SELL đầu tiên của turn) → phải giữ protect-first-sell, không advance dưới reserve fertilizer của planner.
- **Tích hợp:** thêm branch riêng cho FERTILIZER trong `advance_sales` với cap 10 + **debt-tracked subtract** (không dựa vào SELL-as-cap semantics vì V43 tiêu thụ fertilizer như input).

### 4.2 Impact-aware ordering: KHÔNG đưa SELL wheat/fertilizer lên đầu (Rayk C71)
- **Cơ chế:** sort premium SELL theo estimated self-induced price impact; MELON/STRAWBERRY/MILK/WOOL được phép vượt lên trước các dump khác; **WHEAT và FERTILIZER giữ timing an toàn vì đối thủ MUA chúng** — bán sớm = tự hạ giá nguồn input mà đối thủ cần mua.
- **Bằng chứng:** C71 thắng C70 **31-9**, Nikita 25-15, Ezz-alternative 27-13; broad holdout BT 1996 vs 1953.
- **Vì sao v18 chưa có:** frontload của jaxa623 đưa **mọi SELL không-wash** (kể cả wheat/fertilizer thuần) vào group A (đầu list).
- **Rủi ro:** chưa test trên chassis V43; cần A/B với stress clones.
- **Tích hợp:** tách group A thành A1 (premium) + A2 (wheat/fert → đẩy về sau, trước/trong group C). Giữ nguyên wash-pairing.

### 4.3 Feed-buy slot-0 (phòng thủ feed-denial) (Rayk C94 phần 1)
- **Cơ chế:** nâng lệnh BUY wheat-feed hiện có lên **index 0** của market list (không đổi số lượng) ở những turn funding eo hẹp. Đối thủ mua 14-19 wheat trước lệnh slot-8 của ta → giá đẩy lên → chỉ mua được 4/5 → 1 cừu chết ngày 2.
- **Bằng chứng:** 4 live-loss lớn của C92 trung bình **−13.606**; "moving exactly the existing five-unit order to slot zero **fixed every sampled feed-denial route**" (biến thể 5-wheat-first: 173-7, 96.1% trên 900 game). Mua 6 thay vì 5 thì **regress 0-4**; mua 14/19 rồi bán lại = exploit mạnh nhưng brittle vs Kaito.
- **Vì sao v18 chưa có:** frontload của jaxa623 đặt BUY_PRODUCT ở group B — sau mọi SELL không-wash. Trên turn có cả sell lẫn buy-feed, buy ngồi sau index-0 của đối thủ.
- **Rủi ro:** mua trước khi mình bán = giá đắt hơn nếu chính mình sell wheat (wash đã được xử lý); chỉ áp dụng early-game (jaxa623 đã chứng minh mid-season buys có cash slack — funding-attack mùa dài thua 0-16).
- **Tích hợp:** trong `frontload`, nếu list chứa BUY_PRODUCT WHEAT (feed) và day ≤ ~6 (hoặc cash < ngưỡng), hoist lên index 0; giữ simulation guard full-execution.

### 4.4 Town-demand gate cho advance (boatlee V16-RC5)
- **Cơ chế (verify từ code):** `_front_run` chỉ kéo lệnh bán premium (MELON/MILK/STRAWBERRY/WOOL) của turn sau lên **khi turn hiện tại KHÔNG có town demand** cho item đó. Demand = 1 baseline ở step%24==0 (trừ FERTILIZER) + với mỗi unlocked shop chứa item: +2 nếu shop 1-product, +1 nếu nhiều (chỉ tính ở step%4==0). Kèm reserve = pickup-đang-chờ + sell-hiện-tại; **debt `state["due"]` trừ đúng lượng ở turn sau** (`_repay`).
- **Bằng chứng:** 60/60 game (30 seeds × 2 seats) vs reconstructed 8C/4S core; notebook **313 votes** = route public được vote cao nhất; route 8C/4S khớp meta 9c4s hiện tại.
- **Vì sao v18 chưa có:** advance của jaxa623 không có khái niệm town demand — advance bất cứ khi nào hàng trong shed + tape dự kiến bán trong 2 turn.
- **Rủi ro:** chiều của gate (skip khi demand>0) cần verify trên engine 1.32.7 (thứ tự town-drain vs order settlement); bằng chứng 60/60 là vs chính core reconstruct của boatlee.
- **Tích hợp:** thêm `_town_demand_now` vào `advance_sales`; đo A/B qua telemetry.

### 4.5 Strict debt invariant cho advance (boatlee/C45/C94 vs jaxa623)
- **Cơ chế:** các tác giả trên đều **trừ đúng lượng đã bán sớm khỏi lệnh turn sau** ("two-turn intended quantity stays constant"). jaxa623 thay vào đó dựa vào semantics "SELL quantity = cap": lệnh turn sau tự bán ít hơn vì shed đã vơi. **Khác biệt:** nếu shed có nhiều hơn cap của tape (stock tích tụ), bản jaxa623 bán THÊM n units tổng cộng (early-n + full-q), bản debt thì giữ nguyên tổng.
- **Bằng chứng:** boatlee nêu tường minh invariant `s + (q−s) = q`; C45 "records a debt so the original later sale was reduced by exactly the shifted quantity"; C94/C95 same.
- **Rủi ro:** nếu V43 cố tình dùng cap lỏng để sell-all, debt có thể để lại hàng chưa bán cuối mùa → cần kèm endgame stranding audit (xem §8 ý tưởng 10).
- **Tích hợp:** thêm per-item debt state vào wrapper; giảm cap lệnh bán turn kế.

### 4.6 Online opponent-horizon inference (Rayk C68)
- **Cơ chế:** theo dõi delta market-inventory của premium products, trừ sale của mình + town drain xác định, fit "batch thêm" của đối thủ vào horizon 1-6, đua trước đúng 1 turn. Default horizon 4 khi chưa đủ evidence. Gate theo độ tương đồng farm (public).
- **Bằng chứng:** C68 342-18 (0 errors) trong final block; diagnostics nhận đúng horizon 2/3/4/5; refresh 09-08 cho thấy market của phần lớn field fit **horizon 3**.
- **Tích hợp:** nâng cấp độngLOOKAHEAD của advance (hiện fixed 2) + tần suất reservation; cần telemetry market-inventory. **Chi phí xây dựng cao nhất trong danh sách.**

### 4.7 Micro-calibration mở đầu (pipe-7) — xác nhận + tinh chỉnh
- **Cơ chế (verify từ code):** pipe-7 = chassis V43/V44-family, thay opening `[BUY 5, BUY 10, SELL 60]` bằng round trip `[BUY _OPEN_UNITS, SELL _OPEN_UNITS]` với **_OPEN_UNITS = 5**.
- **Bằng chứng:** sweep 0-80 vs Q=70 (50 game): **5/40/60/65 đều 50W-0L (100%)**; 75: 2W-48L; 80: 0W-50L. Tournament 10 agents: **179-1-0 (99.4%)**, thua duy nhất 1 game vs V44. 1.754-46 (97.4%) qua 9 opponents × 200 game. ~$250/game.
- **So với jaxa623:** sweep của jaxa623 (paired margin vs build-70 của chính họ): n=0 (giữ split opening) = **−1.300**; n=10 = +1.286; 25-50 plateau (+1.328…+1.367); 85+ tự hại. Hai sweep **đồng thuận về hướng** (<70 tốt hơn 70) nhưng khác nhau về "đáy an toàn": pipe-7 nói 5 là sweet spot, jaxa623 nói cliff dưới ~10 (n=0 là split opening, không phải round-trip nhỏ). v18 đang dùng 50 — đã trên plateau; việc đổi 50→5 chỉ đáng nếu re-sweep trên opponent pool HIỆN TẠI xác nhận.
- **Cảnh báo từ pipe-7 (danh sách mod THẤT BẠI trên V45 chassis):** clamp_sells (4%), dead_stock (42%), R37 horizon 4→5 (52%), terminal planner expansion (49%), V219/V233 unlock (38%), always-R108 routing (49.5%) — *"V45 has 30 reactive wrapper layers calibrated together like a Swiss watch. Change one gear and the whole thing breaks."* → Mọi thay đổi lên v18 phải qua stress-clone library, không patch đơn lẻ.

### 4.8 One-step premium banking (Rayk C72) — cần fork field
- **Cơ chế:** steps 120-679, chỉ thay PASS/movement (không bao giờ plant/water/harvest/feed/collect/care) khi worker đang mang ≥$2.000 giá trị melon/strawberry/milk/wool **và cách shed-access tile ≤1 bước**; deposit xong thì move sale lên trước trong queue.
- **Bằng chứng:** day-15 trung bình **+168.5 cash / +208.9 liquid**, positive 9/10 game; 109-11 vs 15 reconstructed agents; 29-11 vs C70, 27-13 vs C71. Ngưỡng sắc bén: 500/1000/2-bước đều thua 0-8.
- **Rủi ro:** đụng field actions → vi phạm ràng buộc "không phá farm plan"; chỉ 1.6 drop thêm/game.

### 4.9 Sparse shop branches + cell audit (Kaito)
- **Cơ chế:** đúng 2 nhánh quan sát được: `first_shop == YARN && step>=88 → yarn_first`; `second_shop == YARN && step>=153 → yarn_second`; không classifier, mọi child planner vẫn observe mỗi turn (giữ transaction state của weed-repair).
- **Bằng chứng:** 30/32 vs 20/32 fixed-default (thu hồi 10/12 loss ở YARN seed); 103/128 vs 8 public agents (79.7%, worst-opponent 50%); nhánh yếu nhất **PET_CAFE 16/26**. Branch thứ 2 được chính tác giả router định giá **+0.136 điểm rating/game** trên census 24.000 game (destbreso trích dẫn).
- **Với v18:** V43 đã có route map 13 routes + ordered shop-pair (yhay81 0913) → việc cần là **audit per-world win-rate** (64 worlds) xem cell YARN/PET_CAFE có đang yếu; nếu có thì graft continuation (fork farm plan).

### 4.10 Các mảnh nhỏ khác
- **c27 terminal window:** step 718 executes, action index 719 không — terminal controller nhảy vào 717 (không sớm hơn). v18 đã skip advance ở step≥718 nhưng route 2 của V43 chạy từ step 648 — đáng audit 1 lần.
- **S2.2 engine (Rayk):** SELL chỉ thấy shed (HARVEST vào unit inventory) — DROP kịp mới fund được lệnh cùng turn; fertilizer bán được qua SELL generic (sidecar income).
- **Melon window:** water ngày 6-10 (không phải 12); 16 tiles × 6 = 96 melons khi perfect; miss nước ngày 6-10 = leak ~70 units âm thầm.
- **V44's clone-gated escalation** (4→8→24 khi rival chạy tape của mình): đã bị supersede bởi fixed-24 của jaxa623 (K0006 thắng V45 — vốn chứa escalation — 128-0).

---

## 5. BẪY ĐO LƯỜNG & THỐNG KÊ SAI

| # | Bẫy | Triệu chứng | Phòng tránh |
|---|---|---|---|
| 1 | **Wrapper-file audit** (jaxa623 Trap 1) | Candidate "thắng" +167.366 — thực ra opponent PASS mọi turn vì `kaggle_environments` exec source (relative-path load fail) | Luôn audit với **single-file main.py đóng gói**; 3 số độc lập phải khớp (local harness / package / 64-worlds) |
| 2 | **sys.modules OOM** (jaxa623 Trap 2) | Sweep chết ở game ~200/256 tại 6GB; mỗi candidate để lại ~40MB; wrapper load parent dưới tên parent | Snapshot `_BASE_MODULES` lúc import, xoá mọi module không có trong đó + `gc.collect()` |
| 3 | **Engine version drift** (cjlcjlcjl) | Strawberry cliff 62 units (1.32.x) vs ~247 (build khác) → mọi figure sai âm thầm | Embed reference engine 1.32.x; check compatibility cuối notebook |
| 4 | **File-runner chọn callable CUỐI** (Rayk C92) | File chạy đúng khi import `module.agent` nhưng runner chạy nhầm helper | Packaged file kết thúc bằng binding agent mới; test qua file-path interface |
| 5 | **Downloader nhầm submission** (Rayk §4.3) | Merge 2 submission active → sample agent rating thấp hơn của team | `--leader-submission-only`, match `publicScore` với displayed score |
| 6 | **Rating instance noise** (Rayk §4.4) | 2 bản SHA-256 identical: 2182.2 vs 1210.1 → v9 tự nhảy 1210→1865 không đổi code | Đừng kết luận từ 1 con số LB đang di chuyển; chỉ 2 submission cuối mới nhận game |
| 7 | **"Nothing observable before turn 48"** (destbreso) | Early agreement giữa 2 agent = determinism của engine, không phải evidence copying | Đọc lineage ở prefix, không đọc ở đầu |
| 8 | **Bank 2 bên correlate +0.73** (georgymarin/destbreso) | So bank raw cross-episode mang phương sai shared-world | Dùng **within-episode margin** |
| 9 | **Serial correlation** (georgymarin) | Game liên tiếp của 1 submission chain theo matchmaking → CI win-rate hẹp hơn sự thật | "Know Your Noise"; coi n độc lập là thượng hạn |
| 10 | **16-0 trên 8 seeds không phải evidence** (jaxa623 §7) | Bị lừa 3 lần bởi landslide nhỏ | 4-tier: 24 fixed seeds cả 2 seat → stress-clone library → 64-worlds bootstrap CI (CI dưới chạm 0 = không phải edge) → official runner |
| 11 | **Aggregate giấu parent regression** (Rayk, horizon 25) | Thắng gate tổng nhưng 0-6 vs chính parent trên fresh seeds | Parent + incumbent là **veto opponents**; thua 1 game = veto |
| 12 | **First-turn change re-roll shop draws** (Ahmed V45) | Engine tiêu weed-randomness theo empty tile của CẢ HAI farm trước khi draw shop | So sánh bằng **paired differences + world-level intervals**, không per-game |
| 13 | **Turn convention** (destbreso) | Action quyết ở turn t lưu ở steps[t+1]; day = turn // 24 | Dùng raw index nhất quán |
| 14 | **Elo rate vs margin** (Rayk §2.4; nathanjacob) | 140k bank thua vẫn mất rating; h=+0.662 "medium" mà 80.8% | Tối ưu (wins + 0.5×ties)/total; báo kèm Cohen's h + binomial p |

---

## 6. KẾT QUẢ ÂM TÍNH — DANH SÁCH KHÔNG LÀM LẠI

| Ý tưởng | Ai đo | Kết quả | 
|---|---|---|
| Mua quadrant 4 (SE $4.000) — mọi biến thể | Rayk C93 + destbreso | 0-40 vs C92; Seb routes thua 14.608-36.980; top-30 agent mua SE 12% game mà bank không đổi |
| Season-long funding attack (26-28 lượt/t game) | jaxa623 | 0-16 (−594) và 2-14 (−1.091); mid-season có cash slack |
| Horizon 36/48 | jaxa623 | Thua mirror games vs plain V43 |
| Fixed horizon 25 | Rayk | 0-6 vs C45 trên fresh seeds dù thắng finalist gate |
| Buy 6 wheat đầu game | Rayk C94 | Regress 0-4 vs established agents |
| Buy 14/19 wheat rồi bán surplus | Rayk C94 | Exploit mạnh nhưng brittle vs Kaito |
| Graft toàn bộ market tape của rival | Rayk C94 | "Large generalization failure" |
| Split premium products | Rayk C94 | Không address counters |
| Predict 2 turns ahead (C94 era) | Rayk | 2-2 vs C92 |
| Clone-confidence gate | Rayk | Suppress move hữu ích, không thêm robustness |
| SHEEP↔COW substitution | jaxa623 | −6 wins |
| Feed sweeper / route re-selection / seed recovery | jaxa623 | Negative |
| **Pipe-4 C9 conditional opening** (minimal wheat + hire sớm) | **jaxa623 đã test trên chassis của họ** | **+$1/game — noise** (giá trị biến mất khi đã có frontload + round trip) |
| clamp_sells / dead_stock / R37 4→5 / terminal planner expansion / V219-V233 / always-R108 | pipe-7 (trên V45) | 4% / 42% / 52% / 49% / 38% / 49.5% — tất cả fail |
| EGG market maker (batch 5/10/20) | Kaito | 0 outcome differences — disabled |
| BAKERY branch | Kaito | 2/7 chronological holdout — từ chối |
| Open 85+ (jaxa623) / 75-80 (pipe-7) | cả hai | −1.318…−1.345 / 2-48, 0-50 — tự hại |

---

## 7. SO SÁNH VỚI 4 EDGES CỦA jaxa623: TRÙNG vs BỔ SUNG

### 7.1 TRÙNG / LỘP — không làm lại

| Kỹ thuật bên ngoài | Edge jaxa623 tương ứng | Ghi chú |
|---|---|---|
| Hamburger clone-aware 1-turn premium front-run (6-0, +1.865) | Edge 2 (advance-2) | Tổ tiên trực tiếp; v18 mạnh hơn (2-turn lookahead) |
| c45 debt-tracked 2-turn shift | Edge 2 + Edge 3 | v18 dùng fixed-24; đã beat V45 (chứa V44 escalation) 128-0 |
| V44 clone-gated escalation 4→8→24 | Edge 3 (fixed 24) | Superseded — K0006 > V45 |
| V45 open-70 round trip | Edge 4 (open-50) | jaxa623 re-size + sweep plateau; pipe-7 cross-check (§4.7) |
| boatlee premium market lead (1-turn) | Edge 2 | Trùng phần lớn; phần KHÔNG trùng = town-demand gate + debt (→ ý tưởng #4, #5) |
| C70 impact-first ordering (phần "sells trước buys") | Edge 1 (frontload) | Trùng phần sắp theo loại; phần KHÔNG trùng = wheat/fert giữ sau (→ ý tưởng #2) |
| **nathanjacob pipe-4 C9 opening (96.5% vs V43 raw)** | Edge 4 + Edge 1 | **jaxa623 đã tự test: +$1/game = noise trên chassis có sẵn 4 edges** — KHÔNG làm lại |
| Kaito/ship router shop-pair routing | V43 đã có sẵn (yhay81 0913, 13 routes) | Chỉ cần audit cell (→ ý tưởng #9) |
| Weed repair (C90-C92) | V43 đã có tầng weed-repair (credit tetsutani; Kaito mô tả "bounded weed repair" là feedback surface) | Chỉ C92-style blocked-action repair là có thể thiếu — cần audit, ưu tiên thấp |

### 7.2 BỔ SUNG — chưa có trong v18-base

| Kỹ thuật | Nguồn | Lý do chưa có trong v18 |
|---|---|---|
| Fertilizer/wheat sale preemption (cap + debt) | Rayk C94/C95 | advance_sales loại trừ tường明细 FERTILIZER/WHEAT |
| Impact-aware: wheat/fert sells KHÔNG lên đầu | Rayk C71 | frontload đưa mọi non-wash SELL vào group A |
| Feed-buy slot-0 (early game) | Rayk C94 | frontload đặt BUY sau group A |
| Town-demand gate | boatlee | Không có khái niệm town demand |
| Strict debt (two-turn invariant) | boatlee/C45/C94 | v18 dựa vào SELL-as-cap semantics |
| Online horizon inference 1-6 | Rayk C68 | LOOKAHEAD fixed = 2, horizon fixed = 24 |
| One-step premium banking | Rayk C72 | Cần field fork (thay PASS/move) |
| Sparse YARN/PET_CAFE continuation | Kaito | Cần fork farm plan |
| OPEN_UNITS=5 calibration | pipe-7 | v18 = 50 (đều trên plateau; cần re-sweep) |

---

## 8. TOP 10 Ý TƯỞNG CẢI TIẾN v18

Xếp theo **kỳ vọng impact × độ tin cậy bằng chứng**. Tất cả đều chỉ đụng market/timing trừ khi ghi chú rõ cần fork.

### #1 — Fertilizer-only one-turn preemption (cap 10, debt-tracked)
- **Cơ chế:** nhìn trước tape 1 turn; nếu tape bán FERTILIZER ở t+1 và shed có đủ → bán ≤10 units ở t; ghi debt trừ đúng lượng khỏi lệnh t+1. Bắt đầu fertilizer-only.
- **Bằng chứng:** Rayk C94: held-out 174-6 (96.7%, 900 game/6 seed mới); 18-agent final rank 1 (88-14, BT 1837) thắng C90/91/92 6-0; cơ chế isolated từ 11 live loss (swing 5.300-5.700/match); fertilizer-only thắng wheat+fert 6-0 head-to-head. C95 (+wheat cap 10): 112-8 vs refreshed top-20 medoids.
- **Rủi ro:** tương tác với finite fertilizer planner + sale-credit overlay của V43; phải protect first-sell, không đụng reserve.
- **Tích hợp:** thêm items-with-caps vào `advance_sales` (FERTILIZER, cap 10) + debt state; chạy 4-tier acceptance của jaxa623 (24 seeds → stress clones open78/fast24/open70_h24 → 64-worlds CI → official runner).

### #2 — Impact-aware ordering: wheat/fertilizer sells xuống cuối
- **Cơ chế:** trong frontload, tách group A: A1 = premium sells (đầu list), A2 = WHEAT/FERTILIZER sells (đẩy về cuối, trước group C chỉ khi an toàn). Lý do: bán sớm wheat/fert = tự hạ giá input đối thủ đang mua.
- **Bằng chứng:** Rayk C71 "Giovanni Impact": 31-9 vs C70, BT 1996 vs 1953 trên broad holdout; C70→C71 là đúng thay đổi này trên cùng route family.
- **Rủi ro:** chưa đo trên chassis V43; hiệu ứng nhỏ mỗi turn nhưng cộng dồn 30 ngày; phải giữ wash-pair và simulation guard.
- **Tích hợp:** ~15 dòng trong `frontload`; A/B với telemetry `frontload_declined` để chắc không phá full-execution.

### #3 — Feed-buy index-0 (early-game feed-denial defense)
- **Cơ chế:** khi market list có BUY_PRODUCT WHEAT (feed) và còn early game / cash eo hẹp → hoist lệnh đó lên index 0 (trước cả sells premium).
- **Bằng chứng:** Rayk §15.1: 4 live-loss trung bình −13.606 do cơ chế này; "5-wheat-first fixed every sampled feed-denial route"; biến thể held-out 173-7 (96.1%).
- **Rủi ro:** chỉ có giá trị khi funding thực sự eo hẹp (jaxa623: mid-season buys có slack); hoist sai chiều có thể tự đắt tiền mua — simulation guard bắt buộc.
- **Tích hợp:** branch trong `frontload` gate theo day ≤ 6 hoặc cash < qty × giá wheat + buffer; thêm stress clone "wheat-squeezer" (đối thủ mua 14-19 wheat turn có feed-buy của ta) vào library.

### #4 — Town-demand gate cho advance_sales
- **Cơ chế:** chỉ advance item X khi turn hiện tại KHÔNG có town demand cho X (demand = dawn baseline + shop products tại step%4==0); trừ thêm pickup-reserve.
- **Bằng chứng:** boatlee V16-RC5 60/60 (30 seeds × 2 seats) vs reconstructed 8C/4S core — đúng composition meta hiện tại; notebook 313 votes.
- **Rủi ro:** chiều gate cần verify engine 1.32.7 (thứ tự town drain vs settlement); 60/60 là vs core tự reconstruct.
- **Tích hợp:** port `_town_demand_now` (≈10 dòng, đã có code tham khảo); đo A/B telemetry.

### #5 — Strict debt invariant cho mọi advanced sale
- **Cơ chế:** mọi unit bán sớm đều được trừ khỏi lệnh turn sau (two-turn total constant) thay vì dựa SELL-as-cap.
- **Bằng chứng:** boatlee invariant tường minh; C45/C94/C95 đều debt-tracked; đây là thiết kế chung của 3 dòng độc lập — còn jaxa623 là ngoại lệ.
- **Rủi ro:** nếu tape caps cố tình lỏng (sell-all), debt để lại hàng cuối mùa → kèm ý tưởng #10 đo stranding trước/sau.
- **Tích hợp:** per-item debt dict trong wrapper; giảm cap lệnh t+1.

### #6 — OPEN_UNITS re-sweep + Two-Coins-opening stress clone
- **Cơ chế:** sweep OPEN_UNITS ∈ {5, 10, 25, 50} trên stress-clone library hiện tại; thêm clone "sell-wheat-before-buy" (Two Coins opening) — nhóm duy nhất V45 thua (−10.52, mirror_counter −1.153) và v18 kế thừa chỗ yếu này.
- **Bằng chứng:** pipe-7: Q=5 50W-0L vs Q=70; 179-1 tournament; jaxa623: plateau 25-50 (+1.328…+1.367), n=0 = −1.300. Ahmed V45 disclosed: Two-Coins-opening rivals "cost us the melon".
- **Rủi ro:** pool đang thử open-78 (notebook mới `cloning-v45-open-78-experiment`) — re-sweep định kỳ.
- **Tích hợp:** 1 parameter + 1 clone mới trong bench harness.

### #7 — Online opponent-horizon inference (C68-style)
- **Cơ chế:** tracker delta market inventory (net của own sales + town drain) → fit horizon đối thủ 1-6 → đặt LOOKAHEAD advance + khoảng reservation động, thay fixed 2/24.
- **Bằng chứng:** C68 342-18 (0 errors); diagnostics nhận đúng horizon 2-5; field hiện tại fit horizon 3 (refresh 200 episode/40 team).
- **Rủi ro:** phức tạp nhất trong danh sách; sai lệch fit có thể advance quá tay (như horizon 25 từng thua 0-6).
- **Tích hợp:** telemetry thị trường trong arena trước, model sau; gate theo farm-similarity như C68.

### #8 — One-step premium banking (C72) [cần field fork có kiểm soát]
- **Cơ chế:** steps 120-679, chỉ thay PASS/move khi worker mang ≥$2.000 premium và ≤1 bước tới shed-access; deposit xong kéo sale lên trước queue.
- **Bằng chứng:** 109-11 vs 15 agents; 29-11 vs C70; +168.5 cash/+208.9 liquid day-15 (9/10 positive); ngưỡng sắc (500/1000/2-bước = thua 0-8).
- **Rủi ro:** đụng tầng route executor của V43 (không phải tape replay thuần) — phải hook chỗ phát action, giữ nguyên mọi hành động sản xuất.
- **Tích hợp:** chỉ sau khi #1-#5 xong; fork riêng có cờ bật/tắt + đo bằng 64-worlds.

### #9 — Per-world route-cell audit (YARN-first/YARN-second/PET_CAFE)
- **Cơ chế:** chạy v18 qua 64 worlds (phương pháp jaxa623 tier-3) chia theo shop-pair; tìm world có win-rate < 50%.
- **Bằng chứng:** Kaito: YARN branch thu hồi 10/12 loss (30/32 vs 20/32); nhánh yếu PET_CAFE 16/26; branch 2 đáng +0.136 rating/game theo census 24k game.
- **Rủi ro:** nếu cell yếu, việc graft continuation là fork farm plan (vi phạm ràng buộc market-only) — nhưng audit thuần túy thì rẻ và cần làm.
- **Tích hợp:** thuần đo lường trong arena hiện có; chỉ fork nếu tìm thấy lỗ hổng lớn.

### #10 — Endgame hygiene audit (stranded cash / fallow / liquidation cuối)
- **Cơ chế:** đo giá trị còn kẹt (shed + unit inventory) ở step 719 và số tile fallow cuối mùa của v18; benchmark #1 của destbreso = $442 stranded / 13 fallow tiles.
- **Bằng chứng:** destbreso tìm thấy agent của chính mình "stranding **60×** less money at the bell than the leader tolerates"; leader shape = tham chiếu thời điểm 08-30.
- **Rủi ro:** V43 có route proposal planner + V43 dawn warehouse contract nên có thể đã tốt — cần số liệu trước khi đụng.
- **Tích hợp:** metric thuần telemetry trong run_battle.py; nếu stranded > ~$500 → tăng cường sell-off 3-5 turn cuối (thuộc market domain, an toàn).

---

## 9. NEXT ACTIONS

1. **Tải thêm notebook mới xuất hiện** (từ `comp_kernels_recent.json`, chạy 2026-09-16 — chưa có trong kho):
   - `nathanjacob/kaggriculture-pipe-8-clean-opening` (pipe-8!)
   - `sunil123kumar/kaggriculture-wheat-microstructure`
   - `uninhibitedscholar/kaggriculture-beyond-48-order-sequencing` (fork chính notebook jaxa623 — xem họ mở rộng gì)
   - `ayodejiibrahimlateef/kaggriculture-cloning-v45-open-78-experiment` (counter open-78)
   - `xuanzhang001/kaggriculture-pipe7-public-top1` (claim "pipe7 public top1")
   - `xuantianfengwu/kaggriculture-capacity-release` + `terminal-logistics` + `hour-4-financing-allocator`
   - `aurax7/kaggriculture-shop-router-reactive-v6`, `destbreso/agent-telemetry-catch-what-you-lose`, `alperen5252525/turn-one-market-advantage-kaggriculture` (11v)
2. **Verify engine 1.32.7:** thứ tự town-drain vs market settlement (cho ý tưởng #4); xác nhận cliff strawberry 62 units.
3. **Implement #1 + #2 + #3** (gói "market-defence-v19") — 3 thay đổi đều nằm trong `frontload`/`advance_sales` của wrapper, không đụng farm plan; chạy 4-tier acceptance.
4. **Mở rộng stress-clone library:** wheat-squeezer (mua 14-19 wheat), Two-Coins opener (sell trước buy), open-78.
5. **Bật telemetry per-world + stranding metric** trong arena để phục vụ #9, #10.

---

## 10. PHỤ LỤC: THÔNG SỐ ENGINE ĐÃ VERIFY TỪ CODE

Từ `_MARKET_PARAMS`/`CROPS`/`ANIMALS` nhúng trong k0006_jaxa623.py và pipe-7 (khớp engine 1.32.7, SHA `bc8a54879ef02c7...`):

- **Giá base:** WHEAT 25 · CARROT 35 · TOMATO 60 · STRAWBERRY 120 · MELON 250 · EGG 50 · MILK 160 · WOOL 200 · FERTILIZER 100; I0 = 10.000; floor $1.
- **CROPS:** WHEAT (seed 10, yield 2-4, max 6, one-shot) · CARROT (20, 2-3, 4) · TOMATO (50, first 8, interval 1, max 4, ongoing) · STRAWBERRY (100, first 10, interval 2, max 4, ongoing) · MELON (80, 10-12, max 6).
- **ANIMALS:** GOOSE $300/COOP (first 4, interval 1, EGG) · COW $400/PASTURE (first 8, interval 2, MILK) · SHEEP $500/PASTURE (first 6, interval 3, WOOL).
- **Cơ học:** hire = fib(n); shed 100 items (overflow destroy); ≤10 market orders/turn; start $3.000; land NE $1k / SW $2k / SE $4k; FERTILIZE active 3 ngày (day..day+2); nước trong window [ceil(max_yield_day/2), max_yield_day] +1 (+2 nếu fertilized); one-shot crop decay −1/2 step sau max_lifespan; movement cho phép qua LOCKED tile nhưng tile-op thì không; DROP/PICKUP chỉ ở 4 shed-access tile.
- **Shop unlock:** turn 72 và 144 (ngày 3, 6) → "world" = cặp shop có thứ tự đầu tiên = 64 worlds (destbreso, khớp tier-3 của jaxa623).

---

*Tài liệu này là research-only; không thay đổi code. Nguồn: 12 notebook Kaggle đã extract + verify code tại chỗ (pipe-7 blob, K0006 wrapper, boatlee front-run, C94/C95 labels, engine constants).*
