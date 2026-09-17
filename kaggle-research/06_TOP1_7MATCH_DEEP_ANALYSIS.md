# 06 — TOP-1 DEEP ANALYSIS: 7 TRẬN MAJKEL1337 (5 trận mới + 2 trận cũ)
## Nguyên lý mua/bán · ép giá & tấn công · chọn cây/vật theo lượt · dòng tiền ra/vào

> Task 84 · 2026-09-16 · Bio (tiếp quản Ari)
> Mẫu: 7 episode public của Majkel1337 (teamId 16718819, #1 LB 3,191.7) — parse 0-mismatch
> bằng `top1/parse_replay.py` (re-simulate lockstep engine, verify money từng bước).
> Scripts: `top1/an5_overview.py` (stage 1), `an5_selltiming.py` (2), `an5_attack.py` (3),
> `an5_buyportfolio.py` (4), `an5_stra.py` (5) — outputs `an5_*.json`.

---

## 0. TÓM TẮT — 12 PHÁT HIỆN MỚI (chưa có trong 04A/04B/05)

| # | Phát hiện | Số liệu | Giá trị cho v19 |
|---|---|---|---|
| 1 | **MARKET_PARAMS sensitivity table** (above/below func từng item) | WOOL sq3.20, MELON sq3.60, MILK/STRA linear1.60, EGG log0.20, WHEAT log0.20, FERT linear0.40 | Chunk-policy CHÍNH XÁC theo engine, không phải heuristic |
| 2 | **Mỗi con vật sống = 1 FERT miễn phí/ngày** (`fertilizer_available=True` L831, không cần feed) | Majkel bán 142-217 FERT/match = $9.4-12.2K, KHÔNG BAO GIỜ mua FERT | Động vật = "máy in FERT" — dòng thu #4 của top-1 |
| 3 | **MELON opening là template cố định**: 12 cây (6 d0 + 6 d1-2), bón phân, tưới đủ cửa sổ d6-12 | 72.6u/match @ 218.7 = $15.9K; bán 24-30u d10 @ ~250, phần còn lại d11-12; KHÔNG bao giờ trồng lại | Module B6 mới — $15K/ trận gần như deterministic |
| 4 | **STRA campaign 2 cohort**: trồng d2-6 + d6-12 (peak 23-39 cây); mỗi cây 4 lần đẻ (interval 2 ngày) rồi CHẾT ~d20/d26 | Cohort 1 chết d18-20 → giá crash d19-23 (m1: 204→7); cohort 2 chết ~d26 → giá hồi d24-29 | Chiến lược "tránh crash window + đón recovery" cho anchor |
| 5 | **Anchor correlation 7/7**: 5 trận thắng đều còn đạn anchor s715-719 — 3 lệnh mega-dump STRA $4.8-8.0K (m2/m4/m6) + WOO $2.6K (m7) + nhỏ (m5); 2 trận thua KHÔNG còn hàng | m2 s719 STR×42@173=$7,258; m6 s719 STR×46@174=$7,975; m4 s718 STR×30@161 + s715 WOO×13@171 | Xác nhận A1 là module #1; anchor nhiều tầng: WOOL s715-716 → STRA s718-719 |
| 6 | **Trough discipline ở quy mô lớn**: sau dump ≥10u của đối thủ, Majkel chờ 4-23 bước (65%) rồi bán tại −2.9 dưới giá dump; đối thủ phản ứng ngược (41% bán lại trong 3 bước, −7.8) | 340 instances Majkel vs 244 đối thủ | Bằng chứng thống kê cho A2 (trước đây chỉ 2 trận) |
| 7 | **Cửa sổ bán h22-23 + h0-1** = 39% doanh thu Majkel (đối thủ 61.7%) — auto-drop 23h + consumption-bump h0 (shops step%4==0 + center step%24==0) | h23: 250 lệnh/$118.8K; h1: 221/$98.1K | Module A7 mới: morning scheduler |
| 8 | **Majkel phân tán hơn đối thủ**: top-5 lệnh chỉ 11-16% revenue (n=318-452 lệnh); M&M&P&Q top-5 = 15-20% (n=203-239) | 2,508 lệnh bán / 7 trận | Micro-chunking là edge thống kê, không phải style |
| 9 | **WHEAT là item khối lượng**: 454.7u/match @ 36 (144% base) — log0.20 above-func cho phép dump thoải mái | chunk TB 6.2u, percentile bán 72.4 | Filler crop + feed tự sản |
| 10 | **Idle cash d0-9 ≈ 0** (min $3-7, avg $244-616) — mọi đồng tái đầu tư tức thì; hire ladder cứng 3.7→10.4 units đến d10, giữ nguyên, $4.9K/match | 7/7 trận giống hệt | Money-lifecycle là invariant, không phải tình huống |
| 11 | **Mua feed quanh mặt bằng, không đuổi đỉnh**: WHEAT feed mua đều d0-27, avg $33-36.6, ở percentile 32-58% phân phối giá trận (5/7 trận ≤ 38%) | 127-216u/match | A5 cập nhật: price-gated feed buying quanh-under mặt bằng |
| 12 | **Đối thủ mới M&M&P&Q** (4/5 trận mới): 4-quadrant ($7K land), 10-12 GOOSE, 15 con vật, dump d29 khổng lồ — beaten 3/4 bởi Majkel nhưng +12.7K revenue trong trận thắng (m3) | Điểm 102-112K | Meta đã lên mức 100K+; v19 phải nhắm chuẩn này |

---

## 1. OVERVIEW 7 TRẬN

| key | episode | đối thủ | seed | KQ | Majkel | đối thủ | margin |
|---|---|---|---|---|---|---|---|
| m1 | 109776263 | ymg_aq (#4) | 223111085 | **THUA** | 86,262 | 86,713 | −451 |
| m2 | 109770002 | DSM (#3) | 771335573 | thắng | 91,845 | 84,129 | +7,716 |
| m3 | 109763505 | M&M&P&Q | 1839702094 | **THUA** | 95,090 | 104,058 | −8,968 |
| m4 | 109756255 | M&M&P&Q | 302635704 | thắng | 119,480 | 112,152 | +7,328 |
| m5 | 109748819 | M&M&P&Q | 1054156924 | thắng | 107,051 | 105,494 | +1,557 |
| m6 | 109741171 | SpaTaro | 1330453307 | thắng | 108,597 | 96,273 | +12,324 |
| m7 | 109732826 | M&M&P&Q | 1889174384 | thắng | 110,903 | 102,007 | +8,896 |

**5W/2L.** Điểm trung bình Majkel 102,747 — meta mới đã lên mức **100K+** (2 trận cũ 84-92K).
5 trận mới: đối thủ "M & M & P & Q" chiếm 4 trận (102-112K — có lẽ đội top mới; đã từng
thắng Majkel 8,968 ở m3). SpaTaro 96K.

### 1.1 Revenue mix 7 trận (Majkel $894K vs đối thủ $889K)

| item | Majkel | % | Đối thủ | % |
|---|---|---|---|---|
| STRAWBERRY | 282,080 | **31.5%** | 223,457 | 25.1% |
| MILK | 118,635 | 13.3% | 104,893 | 11.8% |
| WHEAT | 114,708 | 12.8% | 108,625 | 12.2% |
| MELON | 111,120 | 12.4% | 103,190 | 11.6% |
| WOOL | 96,888 | 10.8% | 79,447 | 8.9% |
| FERTILIZER | 76,840 | 8.6% | 94,181 | 10.6% |
| CARROT | 47,366 | 5.3% | 54,915 | 6.2% |
| TOMATO | 33,657 | 3.8% | 53,376 | 6.0% |
| EGG | 12,831 | 1.4% | 66,795 | 7.5% |

→ Majkel = **STRA-heavy (31.5%) + COW/MILK (13.3%) + bỏ EGG** (chỉ mua GOOSE ở m5/m7 khi
thử nghiệm). Đối thủ (đặc biệt M&M&P&Q) = EGG engine (7.5%).

### 1.2 Spend 7 trận (TB trận thắng / trận thua)

| Hạng mục | Majkel (5W) | Đối thủ (5W) | Majkel (2L) | Đối thủ (2L) |
|---|---|---|---|---|
| hire | 4,928 | 4,469 | 4,900 | 5,146 |
| land | **3,000** | 4,600 | **3,000** | 5,000 |
| animal | 6,840 | 7,720 | 5,750 | 7,250 |
| seed | 7,354 | 7,918 | 7,590 | 7,775 |
| product (feed+fert) | 6,486 | 6,586 | 5,190 | 6,124 |
| **revenue** | **133,183** | 128,303 | 114,106 | **123,681** |
| d29 revenue | 12,489 | 12,443 | **9,902** | **15,314** |
| d27-29 revenue | 23,883 | 21,832 | 22,020 | **26,826** |

→ Thua = (a) revenue thấp hơn 9.6K, (b) **thua hẳn 3 ngày cuối** (d29: −5.4K; d27-29: −4.8K),
(c) mua ít động vật hơn (5,750 vs 7,250). Thắng = revenue +4.9K với chi phí thấp hơn.

---

## 2. ENGINE FACTS MỚI (verify trực tiếp source 1.32.7 — bổ sung README)

### 2.1 MARKET_PARAMS — bảng độ nhạy giá từng item (L36-52)

| item | base | T | below_func (thiếu hàng → giá LÊN) | above_func (thừa hàng → giá XUỐNG) |
|---|---|---|---|---|
| WHEAT | 25 | 400 | sqrt ×0.80 | **log ×0.20** (crash rất mềm) |
| CARROT | 35 | 450 | hinge ×1.00 | sqrt ×0.70 |
| TOMATO | 60 | 200 | hinge ×0.40 | sqrt ×0.60 |
| STRAWBERRY | 120 | 100 | sqrt ×0.70 (đỉnh ~204-240) | linear ×1.60 |
| MELON | 250 | 300 | log ×0.20 (hồi rất chậm) | **sq ×3.60** (crash tàn khốc) |
| EGG | 50 | 332 | hinge ×0.40 | **log ×0.20** (gần như KHÔNG crash) |
| MILK | 160 | 122 | sqrt ×0.60 | linear ×1.60 |
| WOOL | 200 | 105 | log ×0.20 (hồi chậm) | **sq ×3.20** |
| FERTILIZER | 100 | 200 | linear ×0.40 | linear ×0.40 (đối xứng) |

Hệ quả sell-policy (đối chiếu chunk TB thực tế của Majkel 7 trận — khớp hoàn toàn):
- **EGG/WHEAT**: chunk lớn an toàn (log) — WHEAT 6.2u/chunk, CARROT 9.6 (hinge/sqrt vừa)
- **MILK/STRA**: linear 1.60 — chunk 3.0/4.9, bán theo trough
- **WOOL/MELON**: sq — chunk 2.8/6.4 chỉ bán ở đỉnh, MUỐN dump phải chia nhỏ + chờ
- **EGG flat**: bán 20-30 EGG s718-719 giá vẫn 51-53 (m3/m4/m5 đối thủ dump 19-30 EGG cùng lúc)

### 2.2 FERTILIZER miễn phí từ động vật (L815-831)
`_daily_refresh_animals`: mọi con vật sống qua ngày (chưa escape) đều được
`fertilizer_available = True` — **không điều kiện feed**. `COLLECT_FERTILIZER` (1 verb) nhặt
1 FERT/con/ngày. Majkel: 295-396 lệnh COLLECT/match → 142-217 FERT bán ($9.4-12.2K) + ~150
bón cho cây. **Không bao giờ mua FERT (buy_n = 0 ở cả 7 trận).**

### 2.3 Cơ chế cây trồng (L215-227 _new_plant, L431-443 WATER, L755-768 decay)
- Non-ongoing (WHEAT/CARROT/MELON): sinh ra `yield_units=1`; **WATER trong cửa sổ
  `[(max_yield_day+1)//2, max_yield_day]`** mỗi lần +1 (+2 nếu fertilized), cap max_yield.
  - WHEAT: cửa sổ tuổi 2-4, cap 6 → 3 lần tưới = 4u (fert: 6u)
  - CARROT: cửa sổ 2-3, cap 4 → 2 tưới = 3u (fert: 4u)
  - MELON: cửa sổ 6-12, cap 6 → 6 tưới = 6u (fert: 3 tưới = 6u — tiết kiệm verb)
- Ongoing (TOMATO interval 1 / STRA interval 2): từ `first_yield_day`, mỗi chu kỳ +1 (+2 nếu
  watered+fertilized), giữ tối đa 4u trên cây, **đẻ đúng 4 lần rồi set max_lifespan → chết**.
- `max_lifespan_step` non-ongoing = (planted_day + max_yield_day + 1)×24: WHEAT d0 chết d5,
  MELON d0 chết d13. Sau lifespan: mỗi 2 step `yield_units -= 1` → mục thành WEED.
- HARVEST lấy toàn bộ yield_units; non-ongoing xóa ô (phải trồng lại), ongoing để cây đẻ tiếp.
- FERTILIZE: 1 FERT = 3 ngày hiệu lực (day..day+2).

### 2.4 Shed & market micro (L345-358, L665-687, L544-628)
- **DROP/auto-drop khi shed đầy → phần tràn bị PHÁ HỦY** (del inv[item] sau khi chỉ lấy `room`).
  Majkel chạm shed=100 ở khung h0-6 mỗi trận (8-21 step ≥95) nhưng bán sáng xuống ngay.
- **BUY_ANIMAL / BUY_PRODUCT FAIL khi shed đầy** (return False, mất lượt).
- Lockstep market: cùng order-index → quote cùng giá pre-commit, commit chẵn kịp p0-p1 mỗi
  unit (p0 không được giá tốt hơn). **Index thấp chạy HẾT trước index cao** (vòng lặp ngoài
  theo index). Majkel đặt index thấp hơn trong 154/586 collision, đối thủ 66, còn lại bằng nhau
  (54% cả hai cùng index 0; 62% cùng index).

### 2.5 Town consumption (L728-749)
- Shops: **step % 4 == 0** (giờ 0, 4, 8, 12, 16, 20) — mỗi shop-instance mua: single-product
  shop (YARN_STORE=WOOL, PET_CAFE=CARROT) ×2u, multi ×1u mỗi sản phẩm.
- Town center: **step % 24 == 0** (giờ 0) — mọi product trừ FERTILIZER −1u.
- → Giờ 0 là cú hích giá lớn nhất trong ngày (shops + center trùng nhau).

---

## 3. NGUYÊN LÝ BÁN (2,508 lệnh của Majkel vs 2,056 của đối thủ)

### 3.1 Percentile giá khi bán (0=đáy trận, 100=đỉnh)

| item | Majkel pct($-weighted) | Đối thủ | Majkel %base | Đối thủ |
|---|---|---|---|---|
| WHEAT | 73.6 | 62.1 | 144% | 137% |
| CARROT | 68.7 | 59.9 | 130% | 120% |
| TOMATO | 68.5 | 58.5 | 134% | 124% |
| STRAWBERRY | **64.5** | 55.7 | **146%** | 133% |
| MELON | **67.2** | 42.2 | 87% | 69% |
| FERTILIZER | 48.8 | 45.6 | 62% | 60% |
| MILK | 32.8 | 39.7 | 52% | 60% |
| WOOL | 45.1 | 43.6 | 62% | 58% |
| EGG | 32.6 | 39.5 | 95% | 102% |

→ Majkel bán **cao hơn 8-23 điểm percentile ở MỌI item crop** (đặc biệt MELON +25, STRA +9).
MILK/EGG/FERT thấp là "trickle liên tục" (vốn không chờ đợi). Đơn giá TB đạt được: STRA 175.8
(146% base!), WHEAT 36.0 (144%), MELON 218.7 (87% — sq-curve giới hạn).

### 3.2 Khung giờ bán (39% doanh thu ở biên ngày)

| Khung | Majkel | Đối thủ |
|---|---|---|
| h22-23 + h0-1 | **39.0%** | **61.7%** |
| h2-7 | 20.1% | 21.0% |
| h8-15 | 25.7% | 11.1% |
| h16-21 | 15.2% | 6.2% |

Cả hai bên đều dồn về "biên ngày" (auto-drop 23h làm hàng mới bán được + h0 có cú hích giá
consumption). Khác biệt: Majkel còn bán LƯỚT ban ngày (25.7% h8-15) — FERT/MILK trickle.
Giờ mạnh nhất: h23 (250 lệnh/$118.8K), h1 (221/$98.1K), h22 (214/$79.8K), h0 (107/$52.2K).

### 3.3 Chunk size & tác động mỗi lệnh

| chunk | Majkel %lệnh | Majkel %$ | Đối thủ %lệnh | Đối thủ %$ |
|---|---|---|---|---|
| 1-2u | 48.3% | 13.5% | 38.2% | 8.3% |
| 3-5u | 25.1% | 23.2% | 28.2% | 18.6% |
| 6-10u | 19.0% | 36.5% | 20.0% | 30.5% |
| 11-20u | 6.5% | 19.0% | 9.4% | 23.3% |
| 21u+ | 1.1% | 7.9% | 4.2% | 19.3% |

Impact mỗi unit (giá pre→post quanh lệnh, Majkel): WOOL 4.62, MILK 2.62, MELON 1.78, STRA
1.19, TOMATO 0.35, FERT 0.34, CARROT 0.12, WHEAT 0.07, EGG 0.07 — **đúng thứ tự nguy hiểm
của above_func** (sq > linear > sqrt/hinge > log).

### 3.4 Doanh thu theo pha

| pha | Majkel | Đối thủ |
|---|---|---|
| d0-9 | $91,131 | $95,413 |
| **d10-19** | **$426,069 (47.7%)** | $367,946 |
| d20-26 | $213,472 | $262,710 |
| d27-29 | $163,453 | $162,810 |

→ **Midgame blitz d10-19 là nơi Majkel thắng +$58K** (MELON xả + STRA peak + FRT/MILK đều
đường). Cuối game d20-26 đối thủ ngược dòng +$49K (họ giữ hàng nhiều hơn) nhưng d27-29 hòa.

### 3.5 Concentration & endgame anchor
- Top-5 lệnh: Majkel 11-16% revenue; M&M&P&Q 15-20% (ít lệnh hơn, lệnh to hơn).
- **Anchor 5 trận thắng**: m2 s719 STR×42@173 ($7,258) · m4 s715 WOO×13@171 ($2,224) + s718
  STR×30@161 ($4,827) · m5 s719 STR×5@95 (nhỏ — nhưng vẫn thắng nhờ trước đó bán @113-109)
  · m6 s719 STR×46@174 ($7,975) + WOO×6@131 · m7 s716 WOO×19@135 ($2,568).
- **2 trận thua: KHÔNG anchor** — m1 5s cuối chỉ $3,620 (đối thủ $4,262); m3 $2,397 (đối thủ
  $9,989). Cùng failure mode: **hết đạn trước chuông cuối**.
- Mẫu hình stagger: **WOOL anchor bán trước (s715-716), STRA anchor giữ đến s718-719** — đúng
  lý thuyết recovery (WOOL log0.20 hồi chậm nên bán sớm vào đỉnh; STRA được town hút mạnh nên
  giá cuối ngày d29 vẫn cao 142-207). Ngoại lệ m6: WOO×6 xả cùng s719 (giá đã đủ cao).

---

## 4. NGUYÊN LÝ MUA & DÒNG TIỀN

### 4.1 Thời điểm mua (7 trận gộp)
- **Động vật**: COW 64 con — ngày {0, 6-10}; SHEEP 36 con — {0, 6-12, 16}; GOOSE 7 con — {6}
  (chỉ m5/m7). → Mua dập đầu game (d0) + đợt 2 sau khi có tiền (d6-10), dừng hẳn sau d10.
- **Đất**: NE+SW ở ngày {3-9}, **KHÔNG BAO GIỜ SE** (0/7 trận). Đối thủ M&M&P&Q mua SE ở
  m3/m4/m5 (4 quadrant, $7K) — thắng lớn nhất của họ (m3) có 4-quadrant.
- **Seed MELON: CHỈ d0-3** (42+28+14+1 gói) — không bao giờ trồng lại.
- **Seed STRA: d2-20** (bulk d2-10: 12+25+20+4+75+30+6+3+14 gói) — 2 cohort.
- **Seed WHEAT: liên tục d9-27** (40-109 gói/ngày) — filler + feed.
- **Seed CARROT: d11-27** (bulk d16+: 33+18+30+30+54+43+37+55+60+24) — late filler theo shop.
- **Seed TOMATO: d9-19** (nhỏ, 2-11 gói/ngày).
- **Feed WHEAT mua đều tay d0-27** (127-216u/match, avg $33-36.6) — mức mua nằm ở percentile
  32-58% phân phối giá trận (5/7 ≤ 38%): mua quanh-under mặt bằng, không đuổi đỉnh spike;
  phần còn lại tự trồng.

### 4.2 Crop mix template (7/7 trận gần giống hệt)

| mốc | cây trồng (cuối ngày) |
|---|---|
| d0 | WHEAT×10 + MELON×6 |
| d2-5 | +MELON×12 (tổng) + STRA×2→8 |
| d8 | **STRA×21-27 + MELON×12** (peak cohort 1) |
| d10 | STRA×21-32 + MELON×6 (vừa xả) + WHEAT×17-27 |
| d14 | **STRA×23-37** (peak cohort 2) + WHEAT×20-27 |
| d18 | STRA giảm + TOMATO×2-9 mọc + WHEAT |
| d22-25 | CARROT×6-29 + WHEAT×15-41 + TOM×2-10 + STRA×2-22 (cohort chết dần) |
| d29 | TOM×2-5 + STRA×0-6 + WHEAT×0-6 (gần trống — đã thanh lý) |

### 4.3 Idle cash & hire ladder (invariant 7/7)
- **d0-9: tiền mặt gần 0** (min $3-7; TB $244-616/ngày cuối ngày) — mua ngay khi có tiền.
- d10-19 TB $22-30K (doanh thu big-phase để dành seed/filler), d20-26 $57-80K tích lũy, d27-29
  giữ (không gì để mua nữa — mọi thứ đã hạ cánh).
- **Hire ladder cứng**: d0 3.7 → d2-3 5.8 → d6 7.7 → d8 8.6 → d9 9.5 → d10-27 **10.4** →
  d28-29 9.5. Tổng $4.9K/match — fib-cost tối ưu (mua sớm ngày rẻ, giữ nguyên tối đa units).

### 4.4 MELON opening — mổ xẻ (5 mục)
1. d0: 6 MELON + 10 WHEAT; d1-2: +6 MELON → **12 cây MELON** ($960 seed).
2. Bón FERT (hiệu lực 3 ngày/lần) + tưới trong cửa sổ d6-12 → mỗi cây 6u (cap).
3. d10: **bán 24-30u @ 240-255**; d11: 6-24u @ 177-244; d12-19: rải nốt @ 106-244.
4. TB 72.6u @ 218.7 = **$15,874/match** — ROI 14.6-18x trên seed $960-1,040 (TB 16.4x), không
   tính verb.
5. Không trồng lại (sq3.60 crash + log0.20 hồi chậm = giữ MELON là leak; m2 d12: 12u@136 sau
   khi xả 54u — đường sq rõ ràng).

### 4.5 Chiến dịch STRAWBERRY (31.5% revenue) — vòng đời giá ROUND-TRIP
Nhịp điển hình (m4, sạch nhất): d15 1u@232 → d16 16u@239 → d17 **39u@234** → d18 24u@221 →
d19 32u@212 → d20 19u@190 → d21 33u@177 → d22 12u@152 (crash window bắt đầu) → d23-26
throttle 5-14u@147-158 → d27-28 13-26u@167-168 (hồi) → **d29 30u@161 (anchor)**.
- Cohort 1 (trồng d2-6): đẻ d12-16-18-20, chết ~d20-22 → **giá crash d19-23** (m1: 204→7;
  m6: 173→39) vì 2 bên cùng xả + cây chết.
- Cohort 2 (trồng d6-12): đẻ đến d24-26, chết ~d26-28 → giá hồi d24-29 khi supply cạn.
- Majkel phản ứng: **giảm mạnh nhịp bán trong crash window** (m1 d21-23: chỉ 2-5u/ngày @45-8;
  d26-28 bật lại 11-13u@104) và giữ anchor d29 13-52u.
- THUA vì STRA: m1 — bán 38u vào crash d19-23 (@132→8, mất ~$3-4K so với giữ) + hết anchor.

---

## 5. TẤN CÔNG & ÉP GIÁ

### 5.1 Va chạm cùng bước (586 lần / 7 trận)
FERTILIZER 147 · MILK 110 · WOOL 94 · WHEAT 84 · STRA 63 · CARROT 33 · TOMATO 28 · MELON 22 ·
EGG 5. 54% cả hai cùng đặt index 0 (62% cùng index — giá quote như nhau). Không có evidence "đặt index thấp
để ăn giá" mang lại chênh lệch đáng kể (48.2 vs 50.2 trung bình — lẫn item-mix). **Kết luận:
order-index không phải vũ khí lớn; THỜI ĐIỂM BÁN (step) mới là vũ khí.**

### 5.2 Trough response (điểm phân biệt thắng/thua rõ nhất)
| | Majkel phản ứng | Đối thủ phản ứng |
|---|---|---|
| Sau dump ≥10u của bên kia | 20% bán lại ≤3 step; **65% chờ 4-23 step** | **41% bán lại ≤3 step** (chase xuống) |
| Giá bán lại so với giá dump | **−2.9** (gần hồi) | −7.8 (đáy) |

→ "Ép giá" của Majkel không phải chủ động slam: nó là **kỷ luật không theo đối thủ xuống
đáy**. Đối thủ tự dẫm lẫn nhau (−7.8) còn Majkel đứng ngoài chờ hồi (−2.9). Trên 244 lần bị
dump: chỉ 5 lần "không bao giờ bán lại" (đối thủ đó đã hết item).

### 5.3 Không có price-war chủ động
Không tìm thấy mẫu "dump để phá giá trước khi đối thủ bán" có hệ thống (attack pre-sale).
Nguyên lý top-1: **để town-consumulation + cohort-death tạo đáy, mình chỉ điều nhịp bán**.

---

## 6. ĐỐI THỦ MỚI: "M & M & P & Q" (4 trận: 102-112K)

- 4-quadrant ($7K land) khi thắng/thua lớn; 10-12 GOOSE + 2-4 COW + 0-2 SHEEP (15 con vật m3).
- EGG engine: 8.9-18.6K EGG + 12.6-14.8K FERT (nhiều con vật = nhiều FERT).
- Dump d29 khổng lồ: m3 s718-719 bán $9,989 (EGG×19+28, STR×12+6, MEL×12, WHEAT×26+30, CAR×11+17);
  m5 $6,395; m4 $7,147; m7 $9,414 (WHEAT×67@31 một lệnh s718!).
- Điểm yếu bị Majkel khai thác: bán QUÁ nhiều units ở giá thấp hơn (TB 7 trận d29: 249u đối
  thủ vs 176u Majkel — họ thu thêm ~$1.5K ở đúng ngày cuối nhưng trả giá bằng đơn giá thấp suốt
  d10-26; riêng m7: 318u vs 157u), top-heavy concentration (top-5 = 17-20% revenue),
  crash-dump WHEAT @22-31 (m4/m7 — còn Majkel bán @33-40).

---

## 7. ĐÓNG GÓP CHO V19 (delta so với 05 hiện tại)

1. **A1 (Liquidation)**: bổ sung stagger 2 tầng — WOOL/fert-đỉnh xả s715-716, STRA giữ đến
   s718-719; anchor = argmax recovery (STRA 5/7, WOOL secondary). Evidence +2 trận (m4, m6).
2. **A2 (Throttle)**: nâng cấp từ 2-trận anecdote → 340-instance thống kê (−2.9 vs −7.8);
   thêm "crash window cohort-1 d19-23" là trigger giảm nhịp STRA.
3. **A6 → CHUNK TABLE chính xác** theo MARKET_PARAMS: WOOL/MELON sq (2-3u/lệnh, chỉ đỉnh),
   MILK/STRA linear (3-5u), CARROT/TOM sqrt (5-10u), WHEAT/EGG log (6-10u+, dump tự do),
   FERT linear (2-8u).
4. **A7 MỚI (Morning scheduler)**: bán lô 23h-auto-drop ở h0-1 (39% revenue window) sau cú
   hích consumption h0; đừng bán h4-7 (trước consumption kế tiếp) nếu không cần shed-room.
5. **B1 (EGG)**: cơ chế flat = log0.20 above + T=332 rộng — detector "net supply flow vs band"
   (sản lượng 2 bên − town drain), không chỉ "price flat".
6. **B2 (Animal mix)**: reframing **động vật = FERT printer** (1 FERT/con/ngày miễn phí) —
   animal count là biến chính; net/ngày: GOOSE ~$74, COW ~$68, SHEEP ~$67 (đã trừ feed $30-35);
   m3 thua vì đối thủ 15 con vs 9 (ΔFERT +$5.4K). FEED INVARIANT giữ nguyên + COLLECT_FERTILIZER
   mỗi ngày cho mọi con.
7. **B3 (Crop)**: STRA 2-cohort model — cohort chết d20/d26; stop-plant d14; crash window
   d19-23 throttle; replant-strategy cho cohort 2 nếu shop STRA ≥ 2.
8. **B6 MỚI (MELON opening lock)**: 12 cây d0-2 + FERT + tưới d6-12 → 72u; sell 24-30 d10 +
   rải d11-12; cấm trồng lại; $15.9K/match gần deterministic.
9. **B5 (Fert allocation)**: MELON 3-tưới-đủ-6u (fert tiết kiệm verb); STRA bón để ×2 production
   (4→8u/cây); CARROT/WHEAT không bón.
10. **Rủi ro mới**: shed-full PHÁ HỦY hàng lúc auto-drop 23h (giữ shed < 100 trước 23h khi còn
    harvest pending); BUY_ANIMAL fail khi shed đầy; cây non-ongoing chết nhanh sau lifespan
    (WHEAT d+5, MELON d+13) — không trồng muộn.
11. **Chuẩn đối thủ mới**: 100K+ points (M&M&P&Q 102-112K) — dominance gate nên thêm benchmark
    "v19 ≥ 100K trung bình trên 64 worlds" hoặc tối thiểu không thua gap > $3K vs mô phỏng
    M&M&P&Q-style (4-quadrant + EGG engine + d29 dump).
12. **Không làm**: order-index sniping (5.1 — không có edge); price-war slam chủ động (5.3).
