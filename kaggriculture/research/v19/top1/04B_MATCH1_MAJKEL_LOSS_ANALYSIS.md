# 04B — MATCH1: ymg_aq (p0) THẮNG Majkel1337 (p1) 86,713 vs 86,262 (+451)

Episode 109776263, seed 223111085. Majkel (hạng 1 LB) dẫn suốt từ d10 → d28, bị lật đúng ngày
cuối d29. ymg_aq hiện hạng 4 LB. Dữ liệu parse + verify 0-mismatch (`match1/`).

---

## 1. Money curve & diễn biến

| Day | ymg_aq money_end (profit_day) | Majkel money_end (profit_day) | Leader | Gap (ymg−Maj) |
|---:|---:|---:|:---:|---:|
| 0 | 12 (−2,988) | 7 (−2,993) | ymg | +5 |
| 1 | 430 (+418) | 3 (−4) | ymg | +427 |
| 2 | 810 (+380) | 43 (+40) | ymg | +767 |
| 3 | 1,150 (+340) | 73 (+30) | ymg | +1,077 |
| 4 | 82 (−1,068) | 149 (+76) | **MAJ** | −67 |
| 5 | 732 (+650) | 505 (+356) | ymg | +227 |
| 6 | 2,222 (+1,490) | 20 (−485) | ymg | +2,202 |
| 7 | 1,951 (−271) | 19 (−1) | ymg | +1,932 |
| 8 | 2,560 (+609) | 2,275 (+2,256) | ymg | +285 |
| 9 | 3,388 (+828) | 374 (−1,901) | ymg | +3,014 |
| 10 | 5,748 (+2,360) | 6,487 (+6,113) | **MAJ** | −739 |
| 11 | 5,635 (−113) | 11,876 (+5,389) | MAJ | −6,241 |
| 12 | 5,841 (+206) | 13,532 (+1,656) | MAJ | −7,691 |
| 13 | 9,250 (+3,409) | 13,837 (+305) | MAJ | −4,587 |
| 14 | 13,739 (+4,489) | 25,612 (+11,775) | MAJ | **−11,873 (đỉnh)** |
| 15 | 21,785 (+8,046) | 29,796 (+4,184) | MAJ | −8,011 |
| 16 | 29,660 (+7,875) | 36,684 (+6,888) | MAJ | −7,024 |
| 17 | 36,122 (+6,462) | 41,153 (+4,469) | MAJ | −5,031 |
| 18 | 45,446 (+9,324) | 48,207 (+7,054) | MAJ | −2,761 |
| 19 | 49,819 (+4,373) | 51,248 (+3,041) | MAJ | −1,429 |
| 20 | 51,374 (+1,555) | 54,367 (+3,119) | MAJ | −2,993 |
| 21 | 54,347 (+2,973) | 56,847 (+2,480) | MAJ | −2,500 |
| 22 | 58,029 (+3,682) | 58,598 (+1,751) | MAJ | −569 |
| 23 | 58,931 (+902) | 59,918 (+1,320) | MAJ | −987 |
| 24 | 61,268 (+2,337) | 62,786 (+2,868) | MAJ | −1,518 |
| 25 | 65,174 (+3,906) | 65,998 (+3,212) | MAJ | −824 |
| 26 | 68,110 (+2,936) | 69,047 (+3,049) | MAJ | −937 |
| 27 | 71,469 (+3,359) | 73,091 (+4,044) | MAJ | −1,622 |
| 28 | 76,145 (+4,676) | 79,264 (+6,173) | MAJ | −3,119 |
| **29** | **86,713 (+10,568)** | **86,262 (+6,998)** | **YMG** | **+451** |

**Diễn biến chính:**
- **d0-9:** ymg_aq dẫn nhỏ — cả 2 mở màn HEAVY (chi gần hết $3,000). Majkel giữ tiền hơn (d1-3
  profit ~0, còn $3/node), ymg_aq bán WHEAT sớm để có cash-flow (60 WHEAT d0 +$1,844).
- **d10-14 — "Majkel blitz":** Majkel bùng nổ (+6,113 ngày 10, +5,389 ngày 11, +11,775 ngày 14),
  mở gap tới **−11,873 (d14)**. Đây là phase Majkel dồn toàn lực (mua animals + STRA) trong khi
  ymg_aq lãi đều.
- **d15-25 — ymg_aq grind-back:** ymg_aq out-earn Majkel 8/11 ngày (trừ d20/d23/d24),
  gap co từ −11,873 → −824. Không phải một cú strike mà là compound: +8,046 (d15), +7,875 (d16),
  +9,324 (d18).
- **d26-28:** Majkel lại tăng speed (+3,049/+4,044/+6,173) → gap nới lại −3,119. Majkel dường như
  vẫn tin mình đang kiểm soát endgame như match2.
- **d29 — THE FLIP:** ymg_aq profit **+10,568** vs Majkel +6,998 = chênh **+3,570 trong 1 ngày**,
  đủ lật từ −3,119 thành **+451**. Toàn bộ kết quả nằm ở ngày cuối → xem kỹ Mục 6.

*(Số liệu: daily.json, match1.)*

---
## 2. Opening d0-3 từng bên

### ymg_aq (p0) — "arb + livestock + wheat-cashflow"
| Step | Hành động |
|---:|---|
| s1 | **BUY_PRODUCT WHEAT 60u @30.2 (−1,812)** rồi **SELL 60u @30.7 (+1,844)** — market probe/arb nhỏ, đồng thời đẩy giá WHEAT 26→33 |
| s1 | HIRE ×6 (fib: 1+1+2+3+5+8 = −20); s2 hire thứ 7 (−13) → **7 hands ngay d0** |
| s1 | **BUY_ANIMAL 3 COW (−1,200) + 3 SHEEP (−1,500)** |
| s2 | BUY_SEED 18 WHEAT (−180) + 1 MELON (−80) → plant 18 WHEAT + 1 MELON |
| d1-3 | FEED/CARE 6 animals/ngày → **bán 6 FERTILIZER/ngày @94-100 (~$570-590/ngày)** — máy in tiền đầu game; mua thêm 6 WHEAT/ngày làm feed |
| d3 | s73: hire ×6 (−20) + BUY_SEED 1 CARROT |
| d4-5 | Pivot: mua STRA (11 plants), +MELON (8), +1 COW; d4 HARVEST 18 WHEAT → d5 bán 68u/$2,614 (58 WHEAT + 10 FERT) |

→ Kết thúc d0 với **$12** (all-in). Cash-flow d1-5 từ FERT (~$580/ngày) + WHEAT harvest d4-5 (~$2,600).

### Majkel (p1) — "melon-first, chặt tiền"
| Step | Hành động |
|---:|---|
| s1 | BUY_ANIMAL 1 COW (−400) + BUY_PRODUCT 5 WHEAT @33 (feed) |
| s2 | HIRE ×4 (−7); **1 COW (−400) + 3 SHEEP (−1,500)** → cộng COW s1 = 5 animals (2 COW + 3 SHEEP) |
| s2-12 | BUY_SEED MELON ×2 ba lần = **6 MELON seeds (−480)**; WHEAT seeds 1+3 |
| s16-19 | 5 lệnh BUY_SEED **exec=0 (hết tiền)** — spam order khi broke |
| d1 | +4 MELON seeds (−320), tiếp tục dead-orders MELON khi hết tiền (s36-42) |
| d2-3 | **STRA seeds bắt đầu d2** (1), d3 mua 4 (−400, 1 dead) → 4 STRA plants d3 |
| d1-3 | Bán FERT 5/ngày (~$476-496/ngày), mua 2-6 WHEAT product/ngày làm feed |

→ Kết thúc d0 với **$7**. d1-4 money đáy **$3-73** (không hề có cash dự trữ) — nhưng plants d3 đã là
**MELON 12 + STRA 4 + WHEAT 3** (đầu tư thu hoạch d10+).

### Khác biệt opening then chốt
1. **ymg_aq 18 WHEAT d0** = cash-flow d4-5 ($2,600) để mua NE đất d5; Majkel bỏ WHEAT, chọn MELON
   12 cây (thu hoạch d10-12) → d1-4 gần như không có tiền lãi ($3-73) nhưng đón shop FARMERS_MARKET
   d3 bằng STRA 4 cây.
2. **ymg_aq 7 hands d0 vs Majkel 4** — lao động sớm để tưới/harvest 18 WHEAT + 6 pasture.
3. **Động vật ngang nhau (6 vs 5)** — cả 2 đều hiểu FERT là nguồn thu d1-9; ymg_aq bán FERT đều hơn
   (6/ngày vs 4-5/ngày) nhờ nhiều hands.
4. **ymg_aq làm WHEAT-arb s1** (buy 60 → sell 60, +$32) — tác dụng phụ: đẩy giá WHEAT lên 33 khiến
   Majkel mua feed đắt hơn ngay step sau.

*(orders.json step<96, daily.json d0-5.)*

---
## 3. Money flow so sánh

### Tổng hợp cả match (từ summary.json)
| Hạng mục | ymg_aq (p0) | Majkel (p1) | Δ |
|---|---:|---:|---:|
| **Revenue (SELL)** | **116,858** | 110,387 | **+6,471** |
| Sell units | 1,753 | 1,397 | +356 |
| HIRE spend | 6,481 | 4,824 | +1,657 |
| BUY_SEED spend | 7,430 | 7,140 | +290 |
| BUY_ANIMAL spend | 6,900 | 6,000 | +900 |
| BUY_PRODUCT spend | 9,334 | 6,161 | +3,173 |
| BUY_LAND spend | 3,000 | 3,000 | 0 |
| **Tổng chi** | 33,145 | 27,125 | +6,020 |
| Orders (executed) | 878 (876) | 949 (904) | |
| **Final** | **86,713** | **86,262** | **+451** |

→ ymg_aq chi nhiều hơn $6,020 nhưng thu nhiều hơn $6,471. Cùng mua 2 quadrant (NE+SW, $3,000).
ymg_aq **đầu tư manpower nhiều hơn hẳn** (hire +$1,657 ≈ +1-2 hands thường trực) và mua product
(feed/fertilizer) +$3,173 — hai khoản này sinh ra phần chênh revenue.

### Idle cash & hands theo giai đoạn
| Giai đoạn | ymg_aq min/avg money | Majkel min/avg money | Nhận xét |
|---|---|---|---|
| d0-9 | $8-1,902 / $154-3,025 | **$0-320** / $35-1,655 | Majkel chạy broke liên tục (min $0 d1, $4 d10) — đầu tư tối đa vào plants/animals |
| d10-18 | $2,424-9,374 / $3,669-11,258 | $4-18,445 / $3,152-13,761 | Majkel giữ idle cash lớn hơn (d11: 10,276 vs 5,375) — tiền nằm chờ |
| d19-28 | $49,885-71,469 | $53,758-73,102 | Cân bằng, Majkel nhỉnh hơn ~2-4K |
| d29 | 76,145→86,713 | 79,264→86,262 | ymg_aq bán khỏe hơn ở ngày cuối |

**Hands (lao động):**
- ymg_aq: 7 (d0) → 8 (d7) → **10-12 (d9-28)** → 11 (d29). Avg 10.4-11.3.
- Majkel: 4 (d0) → 8 (d6) → 10-11 (d9-26) → **chỉ 10 (d27-29)**.
- ymg_aq giữ 11-12 hands suốt 20 ngày cuối; Majkel giảm về 10 ở đúng 3 ngày cuối → ít unit
  harvest/drop hơn trong endgame (thấy rõ ở Mục 6).

**Shed trung bình/ngày (inventory nằm trong kho):**
- Majkel: d10 41 → d21 **82.5** → d28 42.7 (nuôi kho lớn, bán rải).
- ymg_aq: chỉ 15-26 suốt d14-28 — **kho luôn gần rỗng, hàng vào là bán**.
- Nghịch lý: Majkel giữ kho lớn NHƯNG thua ở ngày cuối; ymg_aq "kho rỗng" nhưng d29 vẫn xả được
  $10,568 → hàng của ymg_aq nằm **trên cây (yields chưa harvest)** chứ không phải trong shed —
  xem truy vấn Mục 6.

*(timeline.json: money/hands/shed_total từng step; summary.json.)*

---
## 4. Đất & crop mix

### Mua đất (orders BUY_LAND)
| Player | NE ($1,000) | SW ($2,000) | SE | Ghi chú |
|---|---|---|---|---|
| ymg_aq | **s121/d5** | **s204/d8** | — | Mua ngay khi đủ tiền, 0 lần fail |
| Majkel | s150/d6 | s220 FAIL → **s222/d9** | — | Spam retry khi broke: s101/d4, s122-129/d5 (5 lệnh cash=0), s220/d9 |

→ ymg_aq có đất sớm hơn đúng **1 ngày mỗi lần** (NE d5 vs d6, SW d8 vs d9) — 25 ô mới sớm 1 ngày
= 1 ngày production sớm hơn ở đúng giai đoạn giá còn cao (trước khi market bị bơm hàng).

### Crop mix theo mốc (plants cuối ngày)
| Day | ymg_aq (tổng) | Majkel (tổng) |
|---:|---|---|
| d8 | MELON 13, **STRA 24**, WHEAT 6, CARR 1, TOMA 1 (45) | **STRA 21**, MELON 12, WHEAT 4 (37) |
| d12 | STRA 25, WHEAT 18, MELON 12, CARR 1, TOMA 1 (57) | WHEAT 31, STRA 22, TOMA 5, MELON 1 (59) |
| d16 | STRA 29, TOMA 8, WHEAT 15, MELON 3 (55) | STRA 23, TOMA 15, WHEAT 21 (59) |
| d20 | STRA 28, TOMA 13, WHEAT 13, MELON 1 (55) | WHEAT 25, TOMA 21, STRA 14 (60) |
| d24 | WHEAT 23, **CARR 15**, TOMA 13, STRA 6, MELON 1 (58) | WHEAT 23, CARR 21, TOMA 15, STRA 2 (61) |
| d27 | **CARR 22, WHEAT 21**, TOMA 9, STRA 4, MELON 1 (57) | **WHEAT 31**, CARR 17, TOMA 7, STRA 2 (57) |
| d28 | CARR 15, WHEAT 9, TOMA 7, STRA 4, MELON 1 (36) | WHEAT 23, CARR 7, TOMA 6, STRA 1 (37) |
| d29 | TOMA 4, STRA 3, CARR 1 (8) | WHEAT 4, TOMA 5, STRA 1 (10) |

- **Cả 2 cùng kịch bản lớn:** STRA-charged giai đoạn giữa (d8-20, 21-29 cây), rồi chuyển sang
  WHEAT+CARROT filler giai đoạn cuối (seed rẻ, thu hoạch 2 ngày, nuôi shop BAKERY/PIZZA).
- **Khác biệt cuối trận:** ymg_aq giữ **TOMA 7-9 + STRA 4 + MELON 1** (đa dạng, chờ giá tốt cho từng
  item); Majkel dồn hết vào **WHEAT 23-31** (từ d20) — WHEAT là item giá thấp nhất (base 25) và đã
  bị cả 2 bên bơm inventory → d29 Majkel phải bán WHEAT giá rẻ, ymg_aq thì còn TOMA/STRA/MELON
  đắt tiền để xả.
- MELON: ymg_aq 13 cây d8 → thu hoạch d10-12, giữ 1 cây tới cuối; Majkel 12 cây nhưng bỏ hẳn MELON
  từ d13 (replant bằng WHEAT).

### Weeds & nước tưới
- Weeds trên board (cuối ngày): ymg_aq gần sạch suốt game (0-2 tới d27) rồi 3 (d28) → 8 (d29)
  khi rút unit đi harvest/bán; Majkel giữ 1 weed dai dẳng d5-13, d25-29 tăng dần 2→7. Final 8 vs 7.
- WATER verbs: Majkel nhiều hơn tổng thể (1,397 vs 1,028) — chăm tưới hơn nhưng vẫn để weeds d28-29
  như ymg_aq; khác biệt không quyết định.
- Điểm chung: **cả 2 đều chấp nhận để cây thành weed ở 2 ngày cuối** để tối ưu hands cho
  harvest/drop/sell — đúng chân dung endgame.

*(orders.json BUY_LAND, daily.json plants/weeds/verbs.)*

---
## 5. Mua: seed/animal/feed/fertilizer + ROI động vật

### Seed packets mua cả match
| Seed | ymg_aq (packets/$) | Majkel (packets/$) |
|---|---|---|
| WHEAT | 142 (~$1,420) | **180** (~$1,800) |
| CARROT | 43 (~$860) | 49 (~$980) |
| STRAWBERRY | **31** ($3,100) | 23 ($2,300) |
| TOMATO | 17 ($850) | 22 ($1,100) |
| MELON | **15** ($1,200) | 12 ($960) |
| **Tổng** | 248 pkt / $7,430 | 286 pkt / $7,140 |

→ Majkel mua **nhiều packet hơn nhưng rẻ hơn** (WHEAT-heavy); ymg_aq đắt hơn nhờ **STRA 31 + MELON 15**
(cây revenue cao).

### Động vật
| | ymg_aq | Majkel |
|---|---|---|
| Mua | **9 COW + 3 SHEEP + 6 GOOSE** = $6,900 | 10 COW + 4 SHEEP = $6,000 |
| Đặc biệt | **6 GOOSE ($1,800) → nguồn EGG riêng** | **0 GOOSE** |

### Feed & fertilizer
| | ymg_aq | Majkel |
|---|---|---|
| FEED verbs tổng | 353 (đỉnh 18/ngày) | 267 (đỉnh 14/ngày) |
| BUY WHEAT (feed) | 193u | 169u |
| BUY FERTILIZER từ market | **66u** (bón thêm cho cây) | 0u |
| FERTILIZE verbs tổng (bón cây) | **216** (d28 vẫn bón 24) | 134 |
| SELL FERTILIZER | 251u / $14,707 @58.6 | 157u / $10,535 @67.1 |

→ ymg_aq vận hành "FERT twin-engine": động vật nhả FERT, 1 phần bón lại cây (**216 lượt bón vs 134**,
chưa kể 66u mua thêm) để nhân ×2 yield cho STRA/TOMA/MELON, phần dư bán ra ($14.7K). Majkel bán FERT
đắt hơn từng unit (67.1 vs 58.6 — bớt bón cây hơn) nhưng tổng FERT-revenue thấp hơn $4,172.

### Revenue & ROI động vật
| Item | ymg_aq units/rev/avg | Majkel units/rev/avg | Δ rev |
|---|---|---|---:|
| MILK (COW) | 219u / $19,507 / 89.1 | 232u / $20,320 / 87.6 | −813 |
| EGG (GOOSE) | **208u / $10,926 / 52.5** | 0 / 0 / — | **+10,926** |
| WOOL (SHEEP) | 70u / $5,352 / 76.5 | 71u / $4,998 / 70.4 | +354 |
| **Tổng animal-product** | **$35,785** | **$25,318** | **+10,467** |

ROI theo loài (ymg_aq): GOOSE $1,800 → $10,926 = **6.1x** (EGG daily, không cần wheat ngon);
COW $3,600 → $19,507 = 5.4x; SHEEP $1,500 → $5,352 = 3.6x. Majkel: COW 5.1x, SHEEP 2.5x.
→ **GOOSE là con bài ymg_aq có mà Majkel không** — đúng $10,926 ≈ 2.3× toàn bộ margin trận này.

### Toàn bộ revenue theo item (để thấy bức tranh "portfolio")
| Item | ymg_aq | Majkel | Δ (ymg−Maj) |
|---|---|---|---:|
| STRAWBERRY | 211u $20,326 @96.3 | 150u $20,598 @137.3 | −272 |
| MILK | 219u $19,507 @89.1 | 232u $20,320 @87.6 | −813 |
| WHEAT | 482u $18,464 @38.3 | 478u $19,564 @40.9 | −1,100 |
| FERTILIZER | 251u $14,707 @58.6 | 157u $10,535 @67.1 | +4,172 |
| MELON | 84u $13,099 @155.9 | 72u $17,298 @240.2 | **−4,199** |
| **EGG** | **208u $10,926 @52.5** | — | **+10,926** |
| TOMATO | 91u $8,359 @91.9 | 128u $11,972 @93.5 | −3,613 |
| CARROT | 137u $6,118 @44.7 | 109u $5,102 @46.8 | +1,016 |
| WOOL | 70u $5,352 @76.5 | 71u $4,998 @70.4 | +354 |

**Phân rã margin +451 = Δrevenue +6,471 − Δchi +6,020.** Trong Δrevenue: EGG +10,926 và FERT +4,172
bù cho MELON −4,199, TOMA −3,613 (Majkel bán đắt/nhiều hơn ở 2 item này), WHEAT −1,100, MILK −813.
→ ymg_aq = chiến lược **volume + đa dạng** (9 nguồn thu, chấp nhận giá avg thấp hơn); Majkel =
**price-sniper** (đơn giá STRA 137 vs 96, MELON 240 vs 156) nhưng tập trung nên thiếu nguồn EGG/FERT.

*(orders.json, daily.json verbs.)*

---
## 6. BÁN — nơi trận đấu được quyết định

### 6.1 Sells tổng hợp theo item (từ Mục 5) — ai tối ưu hơn?
| Item | ymg_aq | Majkel | Tối ưu hơn |
|---|---|---|---|
| STRAWBERRY | 211u $20,326 @96.3 | 150u $20,598 **@137.3** | **Majkel** (đơn giá +42%, revenue ngang) |
| MELON | 84u $13,099 @155.9 | 72u $17,298 **@240.2** | **Majkel** (bán đúng đỉnh d10-14) |
| TOMATO | 91u $8,359 @91.9 | 128u $11,972 @93.5 | **Majkel** (nhiều unit hơn) |
| MILK/WHEAT/WOOL | ~ngang nhau | ~ngang nhau | hòa |
| EGG | **208u $10,926 @52.5** | 0 | **ymg_aq độc quyền** |
| FERTILIZER | **251u $14,707** | 157u $10,535 | **ymg_aq** (đàn vật lớn hơn) |
| CARROT | 137u $6,118 | 109u $5,102 | ymg_aq |

→ Majkel thắng thế "đơn giá" ở đúng 3 item mình tập trung (STRA/MELON/TOMA, cộng +$8K), nhưng
**thua thế "portfolio"**: ymg_aq có 1 nguồn revenue Majkel hoàn toàn không có (EGG +$10.9K)
và 1 nguồn áp đảo (FERT +$4.2K — đàn 18 con vs 14 con), cộng nhiều unit hơn ở CARROT. Tổng: ymg +$6,471 revenue.

### 6.2 Timing bán vs giá thị trường
| Item | Đỉnh giá | Majkel bán | ymg_aq bán |
|---|---|---|---|
| WOOL | 218 @d6 | d6 18u@184, d9 12u@119 rồi ngừng | d6 16u@202, d9 12u@130 — cả 2 sát đỉnh ✓ |
| MILK | 201 @d8 | d8 12@196, d12 4@193, d14 30@167 | d8 12@184, d13 15@186 — cả 2 tốt; cả 2 tiếp tục bán @58-88 d17-22 (crash) |
| MELON | 272 @d10 | **d10-11: 48u @248-264, d14: 24u @223 → hết hàng d14** ✓ chuẩn | d10 6@250, rồi **dump d15-18: 66u @~181→102** ✘, giữ 6u bán d29 @100 |
| STRAWBERRY | 206 @d14-15 | d15 12@204 ✓; d19-21 bán 34u @132→45 rồi **THROTTLE d22-25**; d26-29 bán 39u @86-104 (đón sóng hồi) | d15-16 30u @198-203 ✓; **d19-24 dump 120u @111→6** ✘✘ (26u @6 ngày 23!); d26-29 chỉ còn 18u @88-102 |
| CARROT | 51 @d25 | d25-29: 109u @43-50 | d27-29: 137u @42-48 (nhiều cây hơn) |
| WHEAT | 44 @d24 | đều 39-43 | d0 60@31 (arb), d5 58@29 ✘, còn lại 40-44 |

**Điểm nhấn:**
- **MELON:** Majkel thể hiện đúng "chunking theo độ dốc" — 72 units xả sạch trong 4 ngày đỉnh
  (272→215), bỏ ngỏ khi giá rơi. ymg_aq giữ 13 cây melon rồi bán rải d15-18 khi giá rơi tự do →
  mất ~$4-5K so với kịch bản của Majkel.
- **STRA:** ngược lại — ymg_aq dump 120u vào đáy (d19-24, avg **44.8**, có ngày @6) vì cần throughput;
  Majkel throttle từ d22 (giữ **29 STRA trong shed ở d25** khi giá 22) rồi bán d26-29 @86-104 →
  cứu ~$2.9K. **Đây là replay ngược của match2** — lần này Majkel là người giữ hàng đúng.
- **Cả 2 cùng bơm làm sập giá:** 64 step cả 2 bán cùng item (FERT 24, MILK 13, STRA 13, WHEAT 11)
  — d15-24 hai bên xả STRA đồng thời khiến giá 206→1.

### 6.3 ENDGAME LẬT KÈO — truy từng bước d26-29

**Tồn kho sáng d29 (step 696, sau daily-refresh tự harvest vào shed):**
| | ymg_aq | Majkel |
|---|---|---|
| Shed (94u) | WHEA 43, CARR 16, TOMA 10, STRA 6, EGG 7, MILK 8, FERT 4 | WHEA 14, CARR 21, STRA 11, TOMA 6, MILK 8, FERT 1, WOOL 1 (62u) |
| Yields trên cây | CARR 32, TOMA 8, WHEA 11, STRA 2, MELON 5 (58u) | WHEA 37, CARR 13, TOMA 9, STRA 2 (61u) |
| Đàn vật | 9 COW + 6 GOOSE (sẽ nhả EGG/MILK/FERT trong ngày) | 6 COW + 1 SHEEP |
| Hands ngày | 11 | 10 |

→ ymg_aq bắt đầu ngày cuối với **~152 units bán được + động vật daily-yield**; Majkel ~123 units,
không có EGG, không có MELON.

**Kết quả ngày 29:**
| | ymg_aq (229u) | Majkel (150u) |
|---|---|---|
| WHEAT | 72u $2,889 @40 | 68u $2,681 @39 |
| CARROT | **64u $2,681** @42 | 34u $1,476 @43 |
| TOMATO | 18u $1,560 @87 | 13u $1,119 @86 |
| **EGG** | **27u $1,453 @54** | — |
| STRAWBERRY | 8u $800 @100 | 13u $1,296 @100 |
| FERTILIZER | **18u $623** | 8u $269 |
| MELON | **6u $600** @100 | — |
| MILK | 16u $294 @18 | 13u $295 @23 |
| WOOL | — | 1u $5 @5 |
| **Tổng d29** | **$10,900** | **$7,141** |

**Cơ chế "giữ hàng chờ cuối" của ymg_aq (tái hiện):**
1. **Không phải giữ trong shed** (shed luôn rỗng cuối ngày d25-28) — hàng nằm ở 3 chỗ: (a) yields
   chín trên cây (CARROT 31-34, WHEAT 11→47, MELON 2→5 mỗi tối d26-28), (b) trứng/phân tích lũy trên
   pasture chờ PICKUP, (c) 1 cây MELON "gác" với 5-6 yield chín đúng d29.
2. Hàng nằm **trên tay units lúc 23h** được `_end_of_day` auto-drop vào shed (ymg 0→94 units ngay
   đầu d29) — KHÔNG phải engine tự harvest cây (yields chín vẫn nằm trên cây chờ HARVEST tay).
3. Ngày 29: **bán ngay từ s697** (43 WHEAT + 10 TOMA — 2 order đầu ngày), song song 39 HARVEST +
   13 DROP + 24 WATER (tưới ongoing TOMA/CARR để chúng đẻ thêm yield trong ngày), nhặt EGG/FERT
   (COLLECT_FERTILIZER ×14), bán liên tục 4-6 order/step.
4. **Chunk nhỏ 2-8u/order, trải cả ngày** — EGG bán 7+8+2+8+2 = 27u mà giá không rơi (54→53) nhờ
   town hút (3 shop EGG) + mình là người bán duy nhất.
5. **Bước 719 (cuối cùng) vẫn còn đạn:** 16 CARR + 6 WHEA + 2 STRA + 2 TOMA + 2 EGG + 2 FERT
   = +$1,405 ở step cuối; Majkel chỉ còn 6 WHEA + 1 FERT (+$260).

**Trace money từng bước d29 — trận lật đúng step cuối:**
| Step | ymg | Majkel | Lead |
|---:|---:|---:|---|
| 696 | 76,145 | 79,264 | MAJ (−3,119) |
| 697-714 | +6,306 | +3,378 | MAJ (gap cực đại +1,574 @s710) |
| 715 | 83,114 | 82,742 | **YMG dẫn lần đầu trong ngày** |
| 718 | 85,308 | 86,002 | MAJ giành lại (dump 13 WHEAT) |
| **719** | **86,713** | **86,262** | **YMG +451 — trận kết thúc** |

→ Majkel **hết hàng bán ở step 718** (sáng chỉ có ~123u, không có nguồn EGG/MELON bù); ymg_aq vẫn
xả được $1,405 ở step 719. Toàn bộ margin 451 nằm trong 5 step cuối (s715-719).

### 6.4 Dead orders
- ymg_aq: **2** (BUY_PRODUCT WHEAT d0 khi hết tiền $12).
- Majkel: **45** (13 BUY_SEED STRA, 8 MELON, 6 HIRE, 6 BUY_LAND NE, 4 WHEAT product, 4 WHEAT seed,
  3 BUY_ANIMAL COW, 1 BUY_LAND SW) — spam order khi broke, chủ yếu d0-9. Không tốn slot sell nhưng
  bộc lộ logic "đặt rồi quên".

*(orders.json, market.json, timeline.json step 696-719, daily.json d29.)*

---
## 7. Shops & tương tác

### Shops match1 (seed 223111085) và sản phẩm mỗi shop tiêu thụ
| Unlock | Shop | Sản phẩm |
|---:|---|---|
| d3 | FARMERS_MARKET | WHEAT, CARROT, TOMATO, STRAWBERRY |
| d6 | PIZZA_SHOP | MILK, TOMATO, WHEAT |
| d9 | BAKERY | **EGG**, WHEAT |
| d12 | ICE_CREAM_SHOP | STRAWBERRY, MILK, WHEAT |
| d15 | PIZZA_SHOP (2) | MILK, TOMATO, WHEAT |
| d18 | BAKERY (2) | **EGG**, WHEAT |
| d21 | PET_CAFE | CARROT |
| d24 | BRUNCH_SPOT | **EGG**, WHEAT, STRAWBERRY |

**Cường độ cầu theo product (số shop-instance):** WHEAT **7** | MILK 3 | TOMATO 3 | STRA 3 |
EGG 3 | CARROT 2 | WOOL **0** (không có YARN_STORE) | MELON **0** (chỉ town center).

→ Match1 là "WHEAT world" (7 shop) — giải thích vì sao cả 2 bán WHEAT @39-44 (+56-76% base) suốt
endgame; WOOL chết sau d12, MELON không có hồi sức (chỉ dump đỉnh là đúng).

### Phản ứng của từng agent với shop unlock
| Sự kiện | ymg_aq | Majkel |
|---|---|---|
| d6 PIZZA (MILK) | mua GOOSE đầu tiên (thăm dò) | **+5 COW ngay d6** (2→7) phản ứng MILK |
| d9 BAKERY (EGG) | **+3 GOOSE d9, +2 GOOSE d10** → độc quyền EGG | không phản ứng (0 GOOSE cả match) |
| d9-13 (WHEAT shops chồng) | WHEAT đều đặn 3-8 pkt/ngày | **WHEAT-monoculture**: 16,10,10,10,12,10 pkt d9-14 |
| d21 PET_CAFE (CARROT) | CARROT wave d23-28: 36 pkt → 22 cây d27 | CARROT wave d21-26: 32 pkt → 27 cây d26 |
| d24 BRUNCH (EGG+STRA) | EGG giá lên 54 (max); STRA hồi 22→101 | bán STRA hồi @104 d27-28 |

→ Cả 2 đều shop-reactive ở CARROT; **khác biệt lớn nhất: ymg_aq biến shop EGG thành mỏ tiền
(GOOSE), Majkel biến shop WHEAT/MILK thành sản lượng (COW/WHEAT)** — cùng logic nhưng EGG là thị
trường trống (không ai cạnh tranh + 3 shop hút) còn MILK/WHEAT bị cả hai bơm.

### Price war (cùng step bán cùng item): 64 step
| Item | Steps va chạm | Hậu quả |
|---|---|---|
| FERTILIZER | 24 (rải suốt game) | giá FERT 100→32-37 |
| MILK | 13 (d14-18) | MILK 201→1 (d26 đáy) |
| STRAWBERRY | 13 (d15-21) | STRA 206→1 (d23 đáy) |
| WHEAT | 11 | giữ 39-44 nhờ 7 shop hút |
| TOMATO 7, CARROT 3, WOOL 4, MELON 1 | | |

→ Hai agent bán cùng lúc thúc đẩy sập giá ở MILK/STRA/FERT; không có cơ chế nhường lượt — đây là
"prisoner's dilemma" bán hàng: ai dump trước giữ đơn giá tốt hơn, ai giữ thì nhận giá hồi.

*(town.json, orders.json, engine SHOPS mapping.)*

---

## 8. Key moments — vì sao ymg_aq thắng

| # | Step/Day | Sự kiện | Tác động |
|---|---|---|---|
| 1 | **s1 d0** | ymg arb WHEAT 60u: mua @26-30 bán @33 (+$32) | Nhỏ về tiền, nhưng đẩy giá WHEAT lên 33 → Majkel mua feed đắt hơn ngay d0 |
| 2 | d0 | Build order: ymg 18 WHEAT + **7 hands** + 6 animals vs Majkel 6 MELON + 5 animals + 4 hands | ymg có cash-flow d4-5 ($2,614) để mua đất sớm; Majkel broke đến d8 ($3-73 suốt 4 ngày) |
| 3 | **s121 d5 / s204 d8** | ymg mua NE (d5), SW (d8) — mỗi lần sớm hơn Majkel đúng 1 ngày (Majkel cần 6 retry hụt d4-5) | +25 ô × 1 ngày production ở giai đoạn giá cao |
| 4 | d6 | PIZZA unlock → Majkel +5 COW; ymg +1 GOOSE | Majkel all-in MILK (sẽ bão hòa d16+); ymg thăm dò EGG |
| 5 | **d9-10** | BAKERY (EGG) unlock → ymg **+5 GOOSE (tổng 6)** | **Nguồn lợi thế lớn nhất trận**: 208 EGG @52.5 = $10,926, giá không bao giờ xuống dưới base 50 |
| 6 | d10-14 | Majkel blitz: MELON 72u @240 (đỉnh 272), MILK @167-196, +6,113/+5,389/+11,775 profit 3 ngày | Gap lên **−11,873 (d14)** — Majkel tưởng đã thắng thế |
| 7 | d15-24 | STRA crash 206→1: ymg **dump 120u @45 ở đáy d19-24 (13u @$1 ngày d23)**; Majkel throttle từ d22, giữ 29 STRA trong shed @d25 | ymg đốt ~$6K so với kịch bản giữ; Majkel bán lại @100-104 d27-29 — Majkel thắng thế sell-timing |
| 8 | **d18-22** | Majkel under-feed (8-12 FEED cho 14 con) → **d22: 5 con escape (2 COW + 3 SHEEP)**, thêm 2 COW d27-28 | Mất ~30% sản lượng MILK/FERT 8 ngày cuối; đàn cuối: 15 vs 7 con |
| 9 | d21-28 | PET_CAFE → cả 2 plant CARROT wave; ymg nhiều hơn (36 pkt, 22 cây d27) + giữ 4 STRA + 1 MELON + 9 TOMA | Tồn kho cuối trận đa dạng: d29 ymg bán 8 loại hàng (Majkel 7), tới s719 vẫn còn 6 loại đạn (CARR/WHEA/STRA/TOMA/EGG/FERT) vs 2 của Majkel (WHEA/FERT) |
| 10 | **d28 23h → d29 0h** | Engine `_end_of_day`: auto-drop toàn bộ hàng trên tay vào shed (ymg shed 0→**94 units**, Majkel 12→62); hands bị giải tán, thuê lại theo ngày | ymg mở ngày cuối với 94u sẵn sàng bán + 58u yield trên cây + EGG/FERT theo đàn |
| 11 | **d29 s697→719** | ymg bán 229u/$10,900 (chunk 2-8u, liên tục tới s719 +$1,405); Majkel cạn hàng ở s718, s719 chỉ +$260 | Trận lật ở **đúng step cuối 719**: 86,713 vs 86,262 |

**Công thức thắng của ymg_aq:** không phải bán giỏi hơn (đơn giá STRA/MELON/TOMA đều thua
Majkel), mà là **"đủ hàng để bán"** — 9 dòng revenue, đàn vật 18 con (có EGG monopoly), 248 seed
packets, 216 lượt bón phân, 11-12 hands mỗi ngày, tồn kho trên cây chín đúng d29.

---

## 9. Bài học cho v19 (bổ sung độc nhất từ match1, trên nền 04A)

04A (match2) đã nêu: endgame-liquidation scheduler, trough-throttle, STRA-anchor + CARR-filler,
fertilizer allocation, shed-cap pipeline, feed-cutoff d28-29, chunking theo độ dốc, order hygiene,
feed-buy sớm, land timing, sell-into-strength. Match1 bổ sung:

1. **GOOSE/EGG-MONOPOLY PLAY** ★ lớn nhất: khi ≥2 shop EGG (BAKERY/BRUNCH) unlock sớm (d9) và
   đối thủ không bán EGG (giá EGG dính 50-54 = không ai cung) → mua 4-6 GOOSE ngay. Evidence:
   6 GOOSE $1,800 → $10,926 (6.1x), giá không một lần xuống dưới base vì sole-supplier + 3 shop
   hút. Detector rẻ: EGG price flat ≈ base×(1..1.08) suốt ≥5 ngày. Majkel (top-1!) bỏ trống thị
   trường này cả match — v19 có thể exploit mọi đối thủ tương tự.
2. **SHOP-DRIVEN ANIMAL MIX:** số con mỗi loại ∝ số shop-instance của product đó TRỪ phần đối thủ
   đã cung. Match1: EGG 3 shop & 0 đối thủ → GOOSE; MILK 3 shop nhưng đối thủ 10 COW → bão hòa d16
   (Majkel vẫn mua 5 COW thêm d6 = sai lệnh thứ hai). FERT là byproduct của mọi con → đàn lớn =
   nguồn revenue kép (MILK/EGG/WOOL + $14.7K FERT của ymg).
3. **FEED INVARIANT — không để con nào escape trước d28:** `consecutive_unfed ≥ 2` → escape.
   Majkel mất 5 con d22 + 2 con d27-28 (đàn 14→7) = mất ~$1-1.5K sản lượng cuối + FERT. v19: hard
   rule FEED đủ mọi con mỗi ngày (đã có feed-cutoff d28-29 của 04A #7 — thêm chốt trên).
4. **END-OF-DAY AUTO-DROP (engine fact):** `_end_of_day` tự đổ toàn bộ inventory trên tay vào shed
   lúc 23h → **không cần action DROP cuối ngày**. Chiến thuật d28: dành actions cho
   WATER/FERTILIZE/HARVEST, gánh hàng về 23h; sang 0h d29 shed đã đầy (ymg 0→94u) → SELL ngay s697
   trước khi di chuyển (ymg +$2,615 ở s697). v18 nên bỏ DROP khỏi plan 3 step cuối mỗi ngày.
5. **HANDS LÀ CHI PHÍ HẰNG NGÀY (dismissed 23h, thuê lại 0h):** ymg duy trì 11-12 hands × 20 ngày
   ($6,481 tổng) vs Majkel cắt về 10 ở d27-29 → throughput d29: 39 vs 33 HARVEST. Cuộc chiến
   endgame là cuộc chiến đơn vị hành động/ ngày — **đừng tiết kiệm hire ở 3 ngày cuối**.
6. **CROP-MATURITY SCHEDULING cho d29:** plant WHEAT/CARROT (first-yield 2 ngày) vào d26-27 để
   max-yield chín đúng d28-29; TOMATO ongoing + fertilizer tiếp tục đẻ NGAY trong d29 (ymg bán 18
   TOMA ngày cuối). Inventory "trên cây" (yields field) là kho thứ hai — sang 0h tự vào shed.
7. **MELON = item không-shop (chỉ town center):** bán 100% ở cửa sổ đỉnh đầu (d10-14 @240); giữ
   melon qua d15 chỉ còn @78-155. (Bổ sung 04A #8: không chỉ chunking — mà KHÔNG GIỮ vì recovery
   chậm.) MELON 6u giữ tới d29 của ymg @100 = chấp nhận được vì 1 cây/1 tile, nhưng dump 60u d15-18
   của ymg là leak ~$4-5K.
8. **FILLER CROP THEO SHOP-COUNT:** match1 có 7 WHEAT-shops → WHEAT-filler giữ 39-44 (tốt); match2
   ít hơn → DSM giữ WHEAT là sai. v19: đếm shop-instance per product từ observation → chọn filler
   = argmax(shops × price_margin / (seed_cost × cycle_days)). CARROT chỉ có 2 shop nhưng PET_CAFE
   d21 + giá base 35 + cycle 2 ngày → vẫn ăn (137u $6.1K của ymg).
9. **MONOPOLY MICRO-CHUNKING:** item mình là người bán duy nhất (EGG) → chunk 2-8u/order, giá
   không suy chuyển (54 suốt); item hai bên cùng bán (STRA d15-21) → chunk lớn = tự sát chung.
   v19: chunk-size ∝ (I0 − inventory − town-drain-rate×steps) của riêng item đó.
10. **TROUGH-THROTTLE xác nhận từ phía thua:** ymg dump 120u STRA @45 trung bình ở đáy (26u @6
    ngày d23!) trong khi Majkel giữ 29u bán lại @104 — chênh ~$6-7K. ymg vẫn thắng nhờ portfolio,
    nhưng v19 (đấu với Majkel-style throttle) KHÔNG được áp đặt crash-dumping; giữ nguyên
    04A #2 và cộng thêm nguồn thu breadth.
11. **BREADTH vs EFFICIENCY:** Majkel hiệu quả hơn từng dollar (revenue/spend 4.07x vs 3.53x) nhưng
    thua tổng tuyệt đối. Khi margin mỏng (±0.5%), người có thêm 2-3 dòng revenue "không đối thủ"
    (EGG, FERT, MELON-endgame) thắng. v19: giữ core hiệu suất của v18 + bổ sung động vật mix + shop
    counter (bài 1-2).
12. **LAND THRESHOLD-TRIGGER:** mua đất đúng lúc cash vượt giá (ymg d5/d8, 0 retry) thay vì spam
    order khi broke (Majkel 9 dead-orders đất). Land sớm 1 ngày = 1 ngày giá cao hơn của quadrant
    mới. Kiểm "cash ≥ price + buffer hire" mỗi step.

*(Phân tích: match1/{orders,timeline,daily,market,town}.json; engine kaggriculture.py `_end_of_day`
L860-893: `_drop_inventories_to_shed` L878, `farm["hands"]=[]`, `hires_today=0`; `_daily_refresh_animals`:
escape khi consecutive_unfed≥2, care-bonus +1 yield khi fed+cared.)*

---
## 10. Kết luận

Match1 là **hình ảnh phản chiếu của match2**: ở match2 Majkel thắng bằng final-step mega-dump
(42 STRA @173); ở match1 chính Majkel là người **hết đạn trước step cuối** (150u bán được ngày 29
vs 229u của ymg_aq) — không phải vì bán dởm, mà vì cấu trúc sản xuất hẹp hơn: không GOOSE/EGG
(−$10.9K), đàn vật bị escape 7 con, ít CARROT/MELON cuối trận, ít hands hơn. ymg_aq bán giá tệ
hơn ở mọi item chủ lực (STRA 96 vs 137, MELON 156 vs 240) nhưng bù bằng 9 dòng doanh thu và
throughput cuối trận. **Bài học tổng hợp cho v19: timing của Majkel + breadth của ymg_aq.**
