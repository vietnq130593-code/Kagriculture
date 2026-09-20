# TÀI LIỆU THIẾT KẾ v25 — "THE LAST DAY GENERAL"
## Bản chiến lược đánh bại hoàn toàn ahmedv48 (Kaggriculture V48 — Clear the Queue)

> **Mục tiêu**: v25 phải thắng ahmedv48 ≥ 9/10 trận với margin trung bình ≥ +$700.
> **Phương pháp**: giữ nguyên nền kinh tế V43 đã chứng minh, thay toàn bộ kiến trúc vi mô
> market + quản lý buffer cuối game + triệt hạ kho vũ khí chống-clone của đối thủ.
> **Ngày biên soạn**: 18-09-2026 · Nghiên cứu bởi Bio (Task 93-94).

---

## PHẦN 0 — TÓM TẮT ĐIỀU HÀNH (CHO NGƯỜI BẬN RỘN)

**ahmedv48 thắng v24 10-0 không phải vì kinh tế tốt hơn — hai bên chạy CÙNG một tape
V43 (positions identical từng ô, shed identical, 99% lượt mirror tuyệt đối). Trận đấu
được quyết ở đúng 1 ngày:**

| Chỉ số (3 seed đo thực nghiệm) | s100 | s101 | s104 |
|---|---|---|---|
| v24 dẫn tối đa (giữa game) | +$466 (d15) | +$991 (d22) | +$1.247 (d25) |
| **Sụp đổ trong NGÀY 28 (step 672-695)** | **−$1.465** | **−$1.368** | **−$1.417** |
| Kết quả cuối | −$1.219 | −$712 | −$118 |

**Cơ chế thua (xác nhận bằng dữ liệu từng turn + engine source):**
1. **Buffer tối khô**: buổi tối h22 các ngày 24-27, ahmed giữ 15-21 WHEAT trong shed, v24 giữ 0-6 → mỗi tối ahmed "đốt" v24 $500-800 bằng SELL h23/dawn giá cao ($40+ khi inventory 9.750 < 10.000).
2. **Slot ma**: cuối game v24 dán SELL ×1000 catch-all khi shed rỗng → order chết ngay commit đầu, chiếm slot; compact của ahmed gộp SELL trùng + clamp theo shed vật lý + đẩy lượng thật lên slot ĐẦU.
3. **Kho chống-clone của ahmed kích hoạt 99% thời gian** (mirror gate step 1 |Δcash|<0.5 + similarity ≥.95 + 4/6 lượt vị trí trùng) → horizon-24 bán-sớm + lockstep reorder đè v24 từng slot.

**5 trụ cột v25 (chi tiết Phần 5):**
- **A. Compact từ step 0** (ahmed bắt đầu từ 144) — merge/clamp/front, không slot ma.
- **B. Buffer tối** — giữ ~15-21 WHEAT + pipeline pickup mỗi tối, bán h21-23.
- **C. Máy thanh lý ngày cuối** — ngày 28 thanh lý chính xác từng đơn vị, hết catch-all.
- **D. Tàng hình chống-mirror** — đổi chỗ 2-3 ô động vật + opening lệch 1 đơn vị → similarity < .95 → **toàn kho race/reorder của ahmed thành dead code**, ahmed rơi về horizon 2-4 trong khi v25 chạy horizon 24.
- **E. Giữ nguyên điểm mạnh giữa game của v24** (hoard-release throttle thắng d18-27 ở 2/3 seed).

---

## PHẦN 1 — ĐỐI THỦ ahmedv48: KIẾN TRÚC HOÀN CHỈNH

### 1.1. Call-graph runtime (35 lớp sống, đã chứng minh bằng introspect)

```
_e335_agent (L4041, entry Kaggle last-callable)
 └ _e334_agent (L4005) — EXP334 driver, gọi _e334_compact = bản EXP335 (L4016)
    └ _y_agent_shopherd (L3949) — [E334_BASE] herd theo shop + credit + boost SELL
       └ v44y_lockstep_agent (L3812) — [Y_HOST L3824] lockstep reorder (cổng clone)
          └ agent_v44y_preguard (L3660) — [V44Y_HOST] bán trước giờ-23 (h21/22, ngưỡng 93)
             └ agent ADV (L3613) — kéo SELL 3 turn tới lên bây giờ + frontload SELL trước BUY
                └ agent OPEN (L3501) — khai cuộc [BUY7,SELL2] + attack BUY 30 WHEAT s1
                   └ agent RACE (L3451) — phát hiện mirror/clone + horizon 9/24/24
                      └ agent R148 (L3310) — overflow h23: bán đúng lượng sắp bị vứt lúc dawn
                         └ agent R128 (L3174) — service/credit: FEED→PICKUP swap + sale-credit
                            └ agent R127 (L3025) — prepend BUY WHEAT slot 0 + bỏ PLANT h23
                               └ agent R124 (L2922) — opening budget hạt giống (fib hire)
                                  └ agent R97 (L2858) — wheat supply guard (trim/extend/prefund)
                                     └ agent R95 (L2728) — d10-11 cắt BUY WHEAT vượt reserve
                                        └ agent R85 (L2591) — feed-skip + bán FERT vượt reserve
                                           └ agent R70/R53 (telemetry)
                                              └ agent R51-warehouse (L2334) — h23 bán phần vượt 100
                                                 └ agent R51-input (L2261) — beam-search phân bón d12-28
                                                    └ agent R46 (error guard)
                                                       └ agent V233 (L2053) — 6 cừu SE d12 (gate YARN≥2)
                                                          └ agent RELEASE (guard)
                                                             └ agent R37 (L1870) — horizon reserve 2/3/4 + quote-priority reorder
                                                                └ agent R36 (L1706) — reserve trung tâm: dồn SELL tương lai thành 1 SELL ngay
                                                                   └ agent V231 (L1620) — swap COW→SHEEP theo shop d9
                                                                      └ V31/V224/EXPERIMENT (guards)
                                                                         └ agent V219 (L1394) — tomato expansion d18
                                                                            └ V28/ROOM/TERMINAL-154/SHOP-718 (guards + planner 712-718)
                                                                               └ agent BASE (L971) → _IMPL (L968) = make_agent(...)
                                                                                  └ Chassis.act (L460) — tape replay 41 route × 719 bước
```

**Điểm mấu chốt**: idiom `agent = globals().pop('agent')` (24 chỗ) đẩy tên `agent` về
cuối dict globals; các dòng capture `[v for v in list(globals().values()) if callable(v)][-1]`
bắt đúng wrapper mới nhất — 3 lần: `_PG_HOST` (3632), `_V44Y_HOST` (3674), `_Y_HOST` (3824).

### 1.2. Tháp bán-sớm 7 tầng (lý do ahmed luôn bán trước)

| Tầng | Cơ chế | Chu kỳ |
|---|---|---|
| sell_lead (Chassis L631) | bán lô của bước sau khi step%4≠0, kèm suppression | +1 turn |
| r36_reserve (L1660→3441) | nhìn trước tape horizon (2/4/9/24), dồn SELL tương lai thành 1 SELL ngay, ghi r36_debts trừ dần | +2..24 turn |
| adv (L3549) | kéo SELL trong 3 turn tới lên bây giờ; skip khi có BUY_PRODUCT | +3 turn |
| preguard (L3639) | h21/22 bán trước cái guard h23 sẽ dump (ngưỡng 93) | +1-2 giờ |
| frontload | sắp SELL trước BUY trong list | cùng turn, slot sớm |
| v44y reorder (L3765) | hoán vị block 2-6 SELL theo mô phỏng lockstep chính xác, gain >0.5 | từng slot |
| e334/e335 compact (L3974/4016) | gộp SELL trùng item, clamp shed, lượng thật lên slot đầu, giữ index | mọi turn ≥144 |

### 1.3. Bộ phát hiện đối thủ (CỔNG VŨ KHÍ — điểm yếu chí mạng)

```python
# EXP288 mirror gate — step 1, L3462-3467:
if step == 1:
    if abs(float(rival_money) - float(own_money)) < 0.5:
        state['level'] = _RACE_HORIZON_MIRROR = 24          # khóa vĩnh viễn

# race_clone — mọi turn 216..695, L3392-3397:
hist.append(_race_positions_equal(...))  # hands==hands AND farmer==farmer
return len(hist) >= 4 and sum(hist) >= 4 and _r37_similarity(observation) >= .95

# _r37_similarity — L1764-1778: so (crop, animal) TỪNG Ô 10×10,
# đếm ô không rỗng, cần total >= 8; unlocked_quadrants phải bằng nhau.

# v44y clone_gate — L3804-3810: horizon > 0 (tức race_clone đang cháy)
#   → bật _v44y_reorder (hoán vị lockstep) từ step 216.
```

**Ba điều kiện để kho vũ khí full-power kích hoạt: (i) tiền bằng nhau tuyệt đối sau
turn 1; (ii) layout (crop+animal từng ô) trùng ≥ 95%; (iii) vị trí 9 worker trùng
4/6 lượt gần nhất. Cả ba đều là đặc điểm của ĐỐI THỦ, không phải của ahmed —
v25 kiểm soát được cả ba.**

### 1.4. Hằng số khóa của ahmedv48 (đối chiếu khi mô phỏng)

- Race: `_HORIZON_CLONE=9`, `_ESCALATED=24`, `_MIRROR=24`; sim .90/.95; hist 4/6; Δcash 0.5.
- Compact: gate step ≥ 144; `_E334_ITEMS` = 7 sản phẩm (CARROT, TOMATO, STRAWBERRY, MELON, EGG, MILK, WOOL).
- ADV: `_LOOK=3, FROM=144, TO=718`; skip list có BUY_PRODUCT; giờ ≠ 23.
- Preguard: h21/22, ngưỡng 93 (chứ không phải 99), `_Y_MARGIN=-6`, giá ≥ 2.
- Shopherd: swap ngày 8-11, COW→SHEEP khi YARN_STORE mở (không check giá WOOL!), maxq 2, margin $100.
- V233 (6 cừu SE): gate YARN≥2, WOOL≥220, WHEAT≤45, budget ≥ 7000+6×(wheat+10), ngày 12.
- V219 (cà chua): step 432, money ≥ 12000, TOMATO ≥ $70, ≥3 shop PIZZA/FARMERS_MARKET.
- R95/R97: reserve wheat 6 + 48-turn window + 6/ngày nếu YARN≥2; prefund 2 turn; budget giá inv−2000.
- Chassis: `min_sell_price=2`, `max_orders=10`, router khóa route ngày 6 (64 cặp shop), route 2 từ 648.

---

## PHẦN 2 — GIẢI PHẪU THỰC NGHIỆM (3 trận instrument đầy đủ 720 turn)

### 2.1. Xác nhận mirror tuyệt đối

- Step 1: |Δcash| = **0.00** cả 3 seed → mirror gate cháy, level = 24 vĩnh viễn.
- Cửa sổ 216-696: **similarity = 1.0 đủ 480/480 turn**, vị trí trùng 446-460/480,
  **race_clone kích hoạt 95-99% lượt** → ahmed chạy horizon-24 + reorder toàn thời gian.
- Turn 300 (s100): hai bên cùng 9 vị trí worker, cùng farmer, cùng shed (WHEAT 47),
  cùng lệnh `BUY_SEED WHEAT 1`, chênh nhau đúng $29.

### 2.2. Ngày 28 là chiến trường duy nhất

Biên độ cuối mỗi ngày (v24 − ahmed):

```
ngày:      0→8    9→14   15→17   18→27 (v24 lên đỉnh)   28 (SỤP ĐỔ)    29
s100:       0    −29    +466    đỉnh +466 → +246        −1465 → −1219   flat
s101:       0    −32    −21     đỉnh +991 (d22)          −1368 → −709    flat
s104:       0    −32    −24     đỉnh +1247 (d25)         −1417 → −170    flat
```

Mất mát ngày 28 = **−$1.365..−$1.465 (gần như hằng số)** bất kể v24 dẫn bao nhiêu —
vì kết quả ngày 28 không phụ thuộc may rủi mà phụ thuộc **cấu trúc**: ai còn hàng để bán.

### 2.3. Bộ ba turn sát thủ + cơ chế từng turn

| Turn | Bản chất | Điều xảy ra |
|---|---|---|
| **s647→648** (d26 h23 → dawn d27) | v24 chốt ngày với 6 WHEAT, ahmed với **20 WHEAT** → h23 ahmed `SELL WHEA×10+×3+×7` bán trọn 20 (≈$780) trong khi v24 bán 6 | Δ −$570 |
| **s671→672** (d27 h23 → dawn d28) | v24 shed RỖNG, dán 3 slot ma `SELL ×1000`; ahmed còn **21 WHEAT** → `SELL WHEA×20` thu +$780, v24 +$0 | Δ −$780 |
| **s694→695** (d28 h22-23) | v24 3 slot ma ×1000/×998/×988 (shed rỗng); compact ahmed tính đúng lượng thật `SELL WHEA×5` (s694), `×9` (s695) đặt slot 0 | Δ −$647 |

Buffer WHEAT buổi tối (h22) — nhân chứng cấu trúc:

```
          d24   d25   d26   d27   d28
v24:        0     0     6     0     0
ahmed:     15    18    20    21     0  (bán hết ở h23 + dawn → $40-47/unit)
```

WHEAT cuối game bán $40-47 (base $25) vì inventory thị trường tụt còn 9.745-9.831
(10.000 = I0) — cả hai BUY WHEAT ấu đảo để nuôi thú → giá leo dốc → **ai giữ được
wheat đến tối ngày 28, người đó in tiền**.

### 2.4. Các vi sai vi mô khác (cộng dồn)

- s649: v24 `FERT×18 | MILK×6`, ahmed đảo `MILK×6 | FERT×18` — quote-priority xếp
  item nhạy giá trước trong lockstep.
- s673: v24 `SELL MILK×3` vs ahmed `×2` — r85 tính chính xác chi phí cơ hội từng unit.
- 56-60% SELL của v24 (s≥144) là dead/over-cap so với 40-46% của ahmed.
- Giữa game v24 HOARDING tốt (throttle giữ ≥$18, phát nhịp town-consume) — thắng
  d18-27 ở 2/3 seed → **giữ lại cho v25**.

---

## PHẦN 3 — ENGINE MECHANICS (LUẬT CHƠI BẮT BUỘC HIỂU)

Từ `kaggle_environments/envs/kaggressurE.../kaggriculture.py` (L544-660):

1. **Per-slot lockstep**: mỗi turn, 2 list ≤ 10 order xử lý theo slot-index i (0..9).
   Slot i của 2 bên quote CÙNG inventory pre-commit → commit cả hai (P0 trước).
   HỆ QUẢ: bán cùng item ở slot SỚM hơn = giá cao hơn từng unit; inventory tăng dần
   theo slot.
2. **SELL chết dần**: `_commit_unit` trả False khi shed[item] = 0 → order chết NGAY
   tại commit đó (đã bán phần trước đó vẫn giữ tiền) — SELL ×1000 với shed 43 bán
   đúng 43 rồi chết: catch-all HỢP LỆ khi còn hàng, là SLOT MA khi hết hàng.
3. **BUY_PRODUCT quote tại inv−1** → mua-bán cùng turn net ≈ 0 (wheat-wash).
4. **Atomic theo player-order**: HIRE/BUY_LAND chạy P0 TRƯỚC (thuận lợi ghế 0 nhẹ).
5. **Giá**: `market_price = base ± amp·shape(f, |inv−I0|, T)`, I0=10.000, floor $1.
   Bán $1 không tăng supply. Town tiêu thụ mỗi 4 step (1-2 unit/shop-item),
   +1/item mỗi 24 step — nhịp hồi giá.
6. **Dawn (h0)**: thú ăn WHEAT, hires reset (chi phí fib về 1), overflow-shed bị vứt.
7. **Empty order `[]`** được parser bỏ qua nhưng GIỮ NGUYÊN index slot — nền tảng
   cho "compact giữ vị trí" của ahmed.

---

## PHẦN 4 — CHẨN ĐOÁN GỐC RỄ: VÌ SAO v24 THUA 0-10

| # | Nguyên nhân | Bằng chứng | Mức độ |
|---|---|---|---|
| R1 | **Buffer tối cạn kiệt** (không có R95/R97/R127/R128 tương đương) — v24 bán sạch trong ngày, khô tối | Bảng h22: 0-6 vs 15-21 WHEAT, 4 ngày liên tiếp | ★★★★★ |
| R2 | **Slot ma cuối game**: catch-all ×1000 khi shed rỗng chiếm slot, volume thật không bao giờ lên slot đầu | s671/s686-695: v24 +$0 vs ahmed +$780 | ★★★★★ |
| R3 | **Mirror bị nhận diện**: cùng opening [BUY7,SELL2] → Δcash = 0.00 → ahmed lên mode-24 đầy đạn; v24 chỉ có _Horizons=24 từ 288, gate v19.4 cần raw=4 | 99% lượt race_clone cháy | ★★★★ |
| R4 | **9-slot mega-SELL 712-718 với cap ≥100** — phần lớn chết (shed ≤ vài unit/item), chỉ còn planner E182 gánh | s712-717 margin phẳng | ★★★ |
| R5 | Release của v24 append vào CUỐI list (slot tệ nhất); reorder v19.4 chỉ permute block 2-6 SELL, không merge/clamp | code v24 L1129 | ★★★ |
| R6 | A4 double-book (ledger v19 + r36_debts cùng trừ) → over-suppress mua lúa | code v24 | ★★ |

**Điều KHÔNG phải nguyên nhân**: kinh tế nền (tape), crop mix,动物的 mix, hire
schedule — hai bên giống hệt nhau và cùng khỏe. **v24 thua thuần túy ở tầng vi mô
thực thi market + quản lý tồn kho cuối game.**

---

## PHẦN 5 — KIẾN TRÚC v25 "THE LAST DAY GENERAL"

### 5.0. Nguyên tắc tổng

```
v25 = Chassis V43 (nguyên bản, không đụng tape)
    + 5 lớp mới theo thứ tự bọc (ngoài cùng → trong):
      L5  ⬅ TERMINAL-PRECISE   (712-718 + ngày 28-29)
      L4  ⬅ EVENING-BUFFER     (R95/R97/R127/R128-port + tối ưu h20-23)
      L3  ⬅ COMPACT-FROM-0     (E334/E335-port, gate step≥0)
      L2  ⬅ STEALTH-OPENING    (phá mirror + phá similarity)
      L1  ⬅ RACE-OUT           (horizon-24 bán sớm + reorder, tự dùng không cần clone)
    + GIỮ từ v24: preguard h21/22, throttle hoard-release (chỉ giữa game),
      A4 debt-invariant (đã sửa double-book), v19.1 opening (đã sửa L2).
```

### 5.1. Lớp L3 — COMPACT-FROM-0 (port E334/E335, nới rộng)

**Spec** (chạy MỌI turn từ step 0, không chỉ ≥144):
1. Tính `projected_shed(action)` (mô phỏng PICKUP/DROP/PLACE trong cùng action) —
   không dùng shed thô như ahmed (ahmed clamp theo shed hiện tại, v25 clamp theo
   shed SAU action → chính xác hơn 1 nhịp).
2. Với MỌI SELL: qty_new = min(qty, projected[item]); nếu = 0 → slot → `[]`.
3. Gộp SELL cùng item: item giữ slot ĐẦU của segment, các slot kia → `[]`
   (giữ nguyên index — luật engine PHẦN 3.7).
4. SELL sống dồn về slot sớm NHẤT có thể (dời tự do trong vùng SELL-liên-tiếp,
   không kéo BUY/HIRE lên trước — giữ thứ tự ngân sách an toàn).
5. Endgame (≥648): loại sạch catch-all — thay bằng SELL đúng lượng projected.
   Exception: giữ đúng 1 catch-all ở slot CUỐI như "magnet" hứng hàng lẻ
   (nếu tồn tại cơ chế pickup phát sinh ngoài kế hoạch).

**Tham số**: none — thuần xác định. **Chấp nhận**: 0 dead-SELL tại mọi turn ≥ 0
(so 56-60% của v24); mọi SELL thỏa qty ≤ projected_shed.

### 5.2. Lớp L4 — EVENING-BUFFER (port R95/R97/R127/R128 + buffer policy)

**Spec**:
1. **Reserve tối theo ngày**: với mỗi ngày d ≥ 6: mục tiêu tối thiểu lúc h20:
   `WHEAT ≥ 6 (feed sáng sau) + 14 (đôn tối) = 20`, cộng pipeline pickup của
   worker đang đứng cạnh ô chin (đếm `yield_units` public của chính mình).
   Khớp số liệu ahmed giữ 15-21.
2. **Trim/bổ sung BUY**: nếu tổng (shed + PICKUP trong action + SELL-listed) <
   reserve → thêm/mở rộng `BUY_PRODUCT WHEAT` ở slot SAU các SELL cùng turn
   (ngược R127 chỉ khi thiếu gấp mới prepend slot 0 — chi phí quote inv−1 tính
   trước, budget = inv − 2000 như R97).
3. **Prefund 2 turn**: như R97 — khi queue 2 turn tới đầy, mua trước ngay turn này.
4. **Bán buffer h21-h23**: mỗi h21: dump mọi item có projected > reserve(feed
   sáng + min 14 wheat) bằng SELL đặt ở slot 0-2 (qua L3), giá floor $2
   (như preguard v19.2 — giữ, chỉ nâng mức dump lên cho khớp policy reserve).
5. **R148-overflow port**: h23, tính đúng lượng "sắp bị vứt lúc dawn" (shed +
   carrying − 100) → bán đúng lượng đó (biến hàng chết thành tiền).
6. **r85-equivalent**: bỏ FEED khi `bonus_cost × (giá_lúa+5) × 1.25 < giá_lúa`,
   bán FERT vượt reserve-min-14.

**Chấp nhận**: buffer h22 mọi ngày ≥ 14 WHEAT (đo từ runner JSONL `priv.shed`);
0 unit bị dawn-destroy (trừ khi đã cố tình bán $1).

### 5.3. Lớp L5 — TERMINAL-PRECISE (ngày 28-29 + 712-718)

**Spec** — đây là module GÁNH NHẨN $1.400 (toàn bộ độ lệch của trận):
1. **Ngày 28 (672-695)**: chuyển sang "chế độ的最后 ngày" — mọi tính toán bán
   theo projected-shed-đến-giờ-H (mô phỏng nhịp pickup/harvest của tape còn lại
   trong ngày, dùng unit-model engine-exact như E182 blob của ahmed — port luôn).
   Không còn FIFO-throttle: mọi unit dự kiến có trước h23 phải nằm trong SELL
   của đúng giờ tương ứng.
2. **Bán nhịp giờ hàng giá**: xếp SELL theo `quote_priority` giảm dần (r37-port)
   và theo chu kỳ town-consume (step%4==0 hồi giá) — bán TRƯỚC tick tiêu thụ
   1 turn khi giá phục hồi.
3. **712-718**: thay 9-slot mega-SELL bằng: đúng 9 SELL với qty = projected
   từng item (số nguyên dương, min với shed; item hết → `[]`); thứ tự theo
   marginal price giảm dần; giữ DROP-all cạnh kho ở 718 như cũ (v24 đã đúng).
   Giữ E182 planner (64-sim dominance) — chỉ thay output cuối bằng compact-precise.

**Chấp nhận**: margin ngày 28 của v25 ≥ ahmed ± $150 (hiện v24 −$1.368..−$1.465);
0 slot ma trong 672-719.

### 5.4. Lớp L2 — STEALTH-OPENING (phá 2 trong 3 điều kiện vũ khí ahmed)

**Spec**:
1. **Phá money-mirror (step 1)**: opening đổi từ `[BUY 7 WHEAT, SELL 2 WHEAT]`
   thành `[BUY 7 WHEAT, SELL 3 WHEAT]` (hoặc BUY 6/SELL 2). Δcash sau turn 1
   ≥ $2 → `state['level']` của ahmed KHÔNG BAO GIỜ lên 24 (chỉ còn 9 mặc định).
   Chi phí: ~$0-3 một lần (bán thêm 1 wheat ở inv ≈ I0 → net ~0).
2. **Phá similarity (từ d0)**: đổi chỗ PLACE của 2 cặp động vật (ví dụ: SHEEP#1
   lên ô của COW#2 và ngược lại trong cùng quadrant; chỉ đổi Ô, không đổi số
   lượng/giống → kinh tế tape bất biến). Layout lệch ≥ 2/20 ô = similarity
   ~0.90 < 0.95 → **race_clone tắt vĩnh viễn → horizon = 0 → v44y reorder
   TẮT, race_lost escalation TẮT**. (Kiểm chứng ngưỡng: 18/20 match = 0.90.)
3. Không cần phá position-equality (hist) — similarity đã đủ chặn.
4. **Sát thủ phụ (tùy chọn, ưu tiên thấp)**: bait `_race_lost` một lần để ép
   ahmed escalate 24 VĨNH VIỄN (nó sẽ bán sớm tùy tiện cả game, tự dìm giá mình)
   — chỉ làm khi đã thắng ổn định 8/10, vì cần similarity ≥ .95 để nó "nhìn thấy"
   → mâu thuẫn với mục 2. **Khuyến nghị: CHỈ làm mục 1+2, bỏ mục 4.**

**Hệ quả đoán được**: ahmed rơi về cấu hình "base tape + horizon 2/3/4 + adv+3 +
preguard + compact + shopherd + supply guards". So v25 (horizon-24 + compact + full
stack) → v25 luôn là người BÁN TRƯỚC trong mọi cửa sổ giá — đảo ngược thế trận.

**Chấp nhận**: telemetry simulation trên replay 3 seed: `similarity < 0.95` ≥ 95%
lượt 216-696; |Δcash step1| ≥ 1.

### 5.5. Lớp L1 — RACE-OUT (horizon-24 tự chủ + lockstep best-response)

**Spec**:
1. v19.4 gate sửa từ `dict.get(_R37_HORIZONS, player) >= 4` → `horizon > 0`
   (bật reorder từ 216, không đợi 288).
2. _Horizons=24 áp từ 216 (như _RACE_HORIZON_MIRROR của ahmed) — KHÔNG cần
   phát hiện clone: v25 tự quyết bán sớm theo chu kỳ town-consume.
3. Port `_v44y_lockstep` + `_v44y_factor_margin` y nguyên (mô phỏng engine
   chính xác đã kiểm chứng) — nhưng opp-model = **đối thủ THẬT** (đọc
   orders địch từ observation? *không có* — engine không cho xem orders địch;
   thay bằng: mô hình đối thủ = "ước lượng batch 8-24 unit cùng item" như r37
   quote_priority, cộng tương quan lịch sử Δinventory−town_consumption của
   PHẦN 2.6) — chấp nhận mô hình ước lượng, vì reorder chỉ cần thứ tự biên.
4. Frontload SELL trước BUY (ADV-port, giữ guard skip-khi-có-BUY_PRODUCT).
5. **Chu kỳ nhịp**: bán KẾT THÚC đúng trước mỗi tick town-consume (step%4==0)
   khi giá phục hồi — tận dụng nhịp hồi giá $2-4/unit.

**Chấp nhận**: trung bình giá bán/volume ≥ ahmed −$0.5/unit từng item (đo từ
replay); reorder trigger ≥ 200 turn/trận với gain tích lũy ≥ $100.

### 5.6. Giữ nguyên từ v24 (không đụng)

- Chassis V43 + 41 route tape (nền kinh tế đã 48-0 vs v46).
- v19.2 preguard h21/22 (giữ, nâng ngưỡng dump theo L4).
- Throttle hoard-release giữa game: **chỉ active 288 ≤ step < 648** — TẮT từ 648
  (hiện tại để throttle đè tới route-2 là 1 nguyên nhân ngày 28 khô hàng).
- A4 debt-invariant (sửa: chỉ r36_debts được trừ, bỏ ledger kép).
- E182 terminal planner + DROP-all 718.

---

## PHẦN 6 — KẾ HOẠCH THỰC HIỆN & KIỂM ĐỊNH

### 6.1. Thứ tự triển khai (mỗi bước = 1 EXP có thể revert)

| Bước | Nội dung | Dự kiến gain | Rủi ro |
|---|---|---|---|
| EXP1 | COMPACT-FROM-0 (L3) | +$150-250 (dọn 56-60% slot ma) | thấp |
| EXP2 | EVENING-BUFFER (L4) | +$400-600 (đo lại bảng h22) | trung bình (feed conflict) |
| EXP3 | TERMINAL-PRECISE (L5) | +$300-500 (ngày 28 + 712-718) | trung bình |
| EXP4 | STEALTH-OPENING (L2) | +$200-700 (khử vũ khí địch) | thấp (2 chỗ đổi chỗ ô) |
| EXP5 | RACE-OUT (L1) | +$100-300 (bán trước 24 turn) | cao — để cuối |
| Gộp | mục tiêu +$700-1.400/trận | ≥ 9/10 thắng | |

### 6.2. Quy trình kiểm định chuẩn (bắt buộc trước khi gọi "đánh bại")

1. **Battery 10 trận** seed 100-104 × 2 ghế (chuẩn dự án, `battery.py --new v25
   --base ahmedv48`): mục tiêu ≥ 9 win, mean margin ≥ +$700, CI95 loại 0.
2. **Battery chéo**: v25 vs v24 (≥ +$300), v25 vs ahmedv46 (không thua), v25
   mirror v25 (không tự sát — kiểm compact không lockstep-fight với chính mình).
3. **Regression layout**: xác minh similarity(v25, ahmedv48) < 0.95 bằng script
   re-sim detector trên JSONL replay (dùng lại hàm trong Phần 2).
4. **Telemetry budget**: mỗi lớp error ≤ 3/day như quy ước lineage; benchmark
   wall-clock ≤ 1.8× v24 (hiện 0.34ms vs 1.8ms/turn — dư địa lớn).
5. **Kiểm 2 ghế**: seat-swap 10 trận (engine đối xứng nhưng HIRE atomic P0-first
   — kiểm độ lệch ghế < $50).

### 6.3. Hồ sơ rủi ro

| Rủi ro | Khả năng | Giảm thiểu |
|---|---|---|
| L4 buffer xung đột feed sáng (thú đói) | TB | reserve tách 2 pool: feed-sáng 6 + đôn-tối 14; r85-guard đo trước |
| Đổi chỗ ô động vật phá nhịp CARE/FEED của tape | TB | chọn 2 ô CÙNG loại structure (PASTURE↔PASTURE), cùng worker route; chạy battery trước EXP4 riêng |
| Ahmed học lại (v49 sau này) | Cao | tài liệu này công khai cơ chế counter; EXP theo dõi Kaggle mỗi tuần bằng token đã lưu |
| Compact dồn sớm quá → tự dìm giá mình khi địch không chạy | TB | L3 chỉ gộp khi có ≥2 SELL cùng item; L1 horizon chỉ active khi batch địch ước lượng > 8 |
| _race_lost của ahmed vẫn cháy (nó cần similarity — đã tắt) | Thấp | Phần 5.4 đã chứng minh gate |

---

## PHẦN 7 — PHỤ LỤC: DỮ LIỆU NGUỒN

- 3 trận instrument đầy đủ: `/tmp/v48_study_s{100,101,104}.jsonl` (721 line mỗi trận,
  runner `arena/run_battle.py`, engine kaggle-environments 1.32.7) — copy lưu
  `kagriculture/bench/t94_study/` khi lưu trữ.
- Battery gốc Task 93: `kagriculture/bench/t93_v24_vs_ahmedv48.json` (0-10, −$699).
- Nguồn đối thủ: `kaggriculture/ahmedv48.py` (4.042 dòng, sha256 4b540288…, entry
  `_e335_agent`), pull Kaggle 18-09 (token lưu `kaggle-research/config/kaggle_token.txt`).
- Engine reference: `/home/z/.venv/lib/python3.12/site-packages/kaggle_environments/
  envs/kaggriculture/kaggriculture.py` (L544-660 market, L192 giá, L728 town).
- Phân tích code chi tiết: worklog.md Task 3-a (Chassis), 3-b (sediment+shopherd),
  3-c (v24), 3-d (thực nghiệm + tài liệu này).

---

## KẾT LUẬN

ahmedv48 là đối thủ xứng tầm vì nó không thắng bằng kinh tế — nó thắng bằng **kỷ
luật vi mô 720 turn**: slot nào cũng có đạn thật, tối nào cũng còn lương thực, giờ
cuối nào cũng bán đúng lượng. v25 không cần phát minh gì mới: cần **làm đúng 3 điều
ahmed đang làm đúng (compact, buffer, terminal-precise), bỏ 1 điều ahmed làm dở
(bán sớm mù quáng khi không có race), và tước 1 thứ ahmed đang có (mắt nhìn ra
mirror)**. Chênh lệch cấu trúc −$1.400 ngày 28 sẽ đảo chiều thành +$1.400, và với
kho vũ khí mirror bị vô hiệu hóa, mục tiêu 9-10/10 với margin ≥ +$700 là nằm trong
tầm tay.

*"Trận đấu mirror không thắng bằng ai mạnh hơn — mà bằng ai đỡ sai hơn ở giờ thứ 719."*
