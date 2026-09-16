# 04A · MATCH2 — Majkel1337 (p0) THẮNG DSM (p1): 91,845 vs 84,129 (+7,716)

**Episode 109770002 · seed 771335573 · 720 steps · parse_replay verified 0 money-mismatch.**
Majkel1337 = top-1 LB (3191.7); DSM = top-3 LB. Shops match2: d3 FARMERS_MARKET, d6 YARN_STORE,
d9 PET_CAFE, d12 BAKERY, d15 FARMERS_MARKET(2), d18 FARMERS_MARKET(3), d21 BAKERY(2), d24 ICE_CREAM_SHOP.

> **Tóm tắt 1 đoạn:** Hai agent gần như đồng nhất (cùng opening từng dollar đến d2, cùng mua land
> NE d6 / SW d9, cùng 5 COW + 10 SHEEP, cùng 11 hands $232/ngày). Majkel thắng bằng 3 quyết định:
> **(1)** crop-mix thiên về STRAWBERRY (25 vs 23 cây) + CARROT (125 vs 76 gói seed),
> **(2)** **throttle** bán strawberry trong vùng giá đáy d19-24 (bán 40 units thay vì 117, tích trữ
> shed 0→65 units), **(3)** **mega-dump 42 STRAWBERRY trong 1 order ở step 719 cuối cùng** (avg 173,
> unit đầu 186) — riêng step cuối Majkel thu $7,542 vs DSM $1,260. Chênh lệch +7,716 thì **$6,283
> sinh ra ở đúng step 719**, $1,084 còn lại là gap banked từ d28.

---

## Mục lục
1. [Diễn biến tổng thể](#1-diễn-biến-tổng-thể)
2. [Opening & cách triển khai (d0-3)](#2-opening--cách-triển-khai-d0-3)
3. [Quá trình dùng tiền (money flow)](#3-quá-trình-dùng-tiền-money-flow)
4. [Chiến thuật sử dụng đất](#4-chiến-thuật-sử-dụng-đất)
5. [Chiến thuật MUA](#5-chiến-thuật-mua)
6. [Chiến thuật BÁN — phần quan trọng nhất](#6-chiến-thuật-bán)
7. [Tương tác thị trường & shops](#7-tương-tác-thị-trường--shops)
8. [Điểm mấu chốt](#8-điểm-mấu-chốt)
9. [Bài học cho v19](#9-bài-học-cho-v19)
10. [Phụ lục: log ngày 29](#10-phụ-lục-log-ngày-29-full)

---

## 1. Diễn biến tổng thể

### 1.1 Money curve 30 ngày (số dư cuối ngày)

| Ngày | Majkel | Δ/ngày | DSM | Δ/ngày | Gap (M−D) |
|---:|---:|---:|---:|---:|---:|
| 0 | 5 | −2,995 | 5 | −2,995 | 0 |
| 1 | 59 | +54 | 59 | +54 | 0 |
| 2 | 16 | −43 | 16 | −43 | 0 |
| 3 | 180 | +164 | 102 | +86 | +78 |
| 4 | 357 | +177 | 410 | +308 | −53 |
| 5 | 724 | +367 | 746 | +336 | −22 |
| 6 | 49 | −675 | 10 | −736 | +39 |
| 7 | 11 | −38 | 72 | +62 | −61 |
| 8 | 700 | +689 | 1,139 | +1,067 | −439 |
| 9 | 341 | −359 | 635 | −504 | −294 |
| 10 | **6,950** | **+6,609** | 5,305 | +4,670 | **+1,645** |
| 11 | 12,026 | +5,076 | 11,626 | +6,321 | +400 |
| 12 | 20,619 | +8,593 | 20,766 | +9,140 | −147 |
| 13 | 23,139 | +2,520 | 23,553 | +2,787 | −414 |
| 14 | 28,070 | +4,931 | 29,945 | +6,392 | **−1,875** (đáy gap) |
| 15 | 32,969 | +4,899 | 34,097 | +4,152 | −1,128 |
| 16 | 36,180 | +3,211 | 37,738 | +3,641 | −1,558 |
| 17 | 40,655 | +4,475 | 41,053 | +3,315 | −398 |
| 18 | 46,070 | +5,415 | 45,223 | +4,170 | +847 |
| 19 | 47,841 | +1,771 | 47,254 | +2,031 | +587 |
| 20 | 49,564 | +1,723 | 50,528 | +3,274 | −964 |
| 21 | 51,151 | +1,587 | 52,335 | +1,807 | −1,184 |
| 22 | 54,155 | +3,004 | 54,234 | +1,899 | −79 |
| 23 | 56,612 | +2,457 | 56,927 | +2,693 | −315 |
| 24 | 59,164 | +2,552 | 59,692 | +2,765 | −528 |
| 25 | 62,928 | +3,764 | 62,679 | +2,987 | +249 |
| 26 | 67,572 | +4,644 | 66,327 | +3,648 | **+1,245** |
| 27 | 71,227 | +3,655 | 71,417 | +5,090 | −190 |
| 28 | 78,413 | +7,186 | 77,329 | +5,912 | **+1,084** |
| 29 | **91,845** | **+13,432** | **84,129** | **+6,800** | **+7,716** |

### 1.2 Tóm tắt dòng tiền theo pha (revenue / spend)

| Pha | Majkel rev | Majkel spend | Net | DSM rev | DSM spend | Net |
|---|---:|---:|---:|---:|---:|---:|
| Opening d0-2 | 1,094 | 4,078 | −2,984 | 1,122 | 4,106 | −2,984 |
| Build-up d3-9 | 12,190 | 11,865 | +325 | 12,474 | 11,855 | +619 |
| Mid d10-20 | 57,036 | 7,813 | +49,223 | 59,193 | 9,300 | +49,893 |
| Endgame d21-28 | 34,278 | 5,429 | +28,849 | 30,305 | 3,504 | +26,801 |
| Final d29 | **13,575** | 143 | **+13,432** | **6,943** | 143 | **+6,800** |
| **Tổng** | **118,173** | **29,328** | **+88,845** | **110,037** | **28,908** | **+81,129** |

### 1.3 Nhận định pha trận
- **Opening (d0-2):** hai agent chơi **GIỐNG HỆT nhau tới từng dollar** (cùng $5 cuối d0, cùng $59, $16).
  Cả hai đốt sạch $3,000 → $5.
- **Build-up (d3-9):** sống bằng tiền bán FERTILIZER (5/ngày @ ~95-97) + bán lại WHEAT wash.
  Cả hai mua NE (d6, s150) ngay sau đợt bán WOOL đầu tiên, SW (d9, s222/224) sau đợt WOOL lần 2.
- **Mid (d10-20):** MELON dump d10 (30 units @245.6 = $7,367) + STRAWBERRY đỉnh giá d13-17 (@160-192).
  **DSM dẫn tới −1,875 ở d14** vì bán WHEAT dồn dập (32-37 units/ngày) còn Majkel âm thầm chuyển
  tile sang CARROT/STRAWBERRY và **bắt đầu tích trữ** (bán ít đi).
- **Endgame (d21-28):** giá STRAWBERRY hồi (104 → 174) do town hút 25 units/ngày trong khi cây đã chết
  (hết vòng đời ~d26). Majkel bán dần vào đỉnh hồi phục + CARROT đều đặn 20-32 units/ngày → vượt lại.
- **Final (d29):** liquidation — xem mục 6.4.

---

## 2. Opening & cách triển khai (d0-3)

### 2.1 Build order từng step (Majkel; DSM hệt trừ các note)

| Step | Hành động | Tiền sau |
|---:|---|---:|
| s1 | **BUY_ANIMAL COW ×1** (−400) + **BUY_PRODUCT WHEAT ×5** feed @26-27 (−136) | 2,464 |
| s2 | SELL WHEAT ×1 @28 (+28) · **HIRE ×4** (fib 1+1+2+3 = −$7) · **BUY_ANIMAL COW ×1** (−400) · **BUY_ANIMAL SHEEP ×3** (−1,500) | 585 |
| s3 | SELL WHEAT ×1 @28 | 613 |
| s4 | **BUY_SEED MELON ×2** (−160) — *DSM mua ở s7* | 453 |
| s5-s7 | BUY_PRODUCT WHEAT feed ×1 @28 mỗi step (tổng 3) | 209 |
| s6 | BUY_SEED MELON ×2 (−160) + WHEAT feed ×1 | 237 |
| s12 | BUY_SEED MELON ×2 (−160) → **đủ 6 MELON** | 49 |
| s13 | BUY_SEED WHEAT ×2 @10 | 29 |
| s15-s22 | xen kẽ SELL WHEAT ×1 @28 và BUY_SEED WHEAT ×1 @10 → **đủ 10 WHEAT seeds** | 5 |
| **Cuối d0** | **$5** — đã có: 2 COW, 3 SHEEP, 6 MELON plants, 10 WHEAT plants, 4 hands | |

- Trên board: **16 plants trên 25 ô NW** (6 MELON + 10 WHEAT), 5 ô PASTURE cho 5 con vật
  (verbs: 5 BUILD_PASTURE + 5 PLACE), 4 ô trống. PLANT/WATER 17 lần ngay d0 (tưới đủ 16 cây + 1 thừa).
- **Trình tự PLANT:** MELON trước (s4-s12 trồng đủ 6), WHEAT sau (s13-s22 đủ 10). Ngày d1-d2 bổ sung
  4 MELON nữa (10) + 2 STRAWBERRY (d2) — đều tự tài trợ bằng tiền bán FERTILIZER.
- **Wash trade WHEAT:** mua feed 5 @26-27 đẩy giá 25→28, rồi bán lại 1-4 units @28. Cả 2 bên làm;
  DSM còn làm wash trắng trợn hơn (mua 1 + bán 1 cùng step s4-s7).
- **DSM d0 cũng về $5** nhưng phát **7 dead-SELL mỗi step** (SELL STRAWBERRY/MELON/MILK/WOOL/TOMATO/
  EGG/CARROT với units=0) — tổng 2,709 dead-sells cả trận so với **19 của Majkel** (xem 6.6).

### 2.2 Số dư từng ngày đầu: d0 $5 → d1 $59 → d2 $16 → d3 $180 (M) / $102 (D).
Nguồn sống d1-d5: **FERTILIZER ×5/ngày @ 99→91** (thu từ COLLECT_FERTILIZER của 5 con vật, miễn phí)
+ bán WHEAT @30-32. Cả hai thuê thêm hands: d1 giữ 4 ($7), d2 +6 ($20) → 6 hands.

---

## 3. Quá trình dùng tiền (money flow)

### 3.1 Tổng chi theo loại (cả hai, 30 ngày)

| Loại | Majkel | DSM | Chênh |
|---|---:|---:|---:|
| Seeds (tất cả) | 7,900 | 7,530 | +370 |
| — trong đó WHEAT seeds | 1,240 (124 gói) | 1,800 (180 gói) | −560 |
| — STRAWBERRY seeds | 2,500 (25 gói) | 2,300 (23 gói) | +200 |
| — CARROT seeds | 2,500 (125 gói) | 1,520 (76 gói) | +980 |
| — MELON / TOMATO seeds | 960 (12) / 700 (14) | 960 (12) / 950 (19) | 0 / −250 |
| Animals | 7,000 (5 COW + 10 SHEEP) | 7,000 (idem) | 0 |
| Products (WHEAT feed) | 6,507 (178 units, avg 36.6) | 6,449 (172 units, avg 37.5) | +58 |
| **FERTILIZER mua** | **0** | **0** | 0 |
| Hires | 4,921 (285 lượt) | 4,929 (286 lượt) | −8 |
| Land | 3,000 (NE+SW) | 3,000 (NE+SW) | 0 |
| **Tổng chi** | **29,328** | **28,908** | **+420** |

### 3.2 Idle cash
- Cả hai giữ pattern giống nhau: **avg $28,1K (M) / $28,3K (D)**, median ~$27,3K, min $1, max $78K.
  81 steps đầu game dưới $100; từ ~d12 tiền chất đống vì không còn gì đáng mua (seeds rẻ, land xong,
  animals xong) — thu $3-5K/ngày vs chi ~$500/ngày.
- **Tái đầu tư:** mọi cú tiền lớn (WOOL d6/d9, MELON d10) đều bị hút về ~$0 trong 1-2 ngày qua
  NE/SW/animals/seeds. Sau d12 thì "reinvest" = seeds lai rai + feed.

### 3.3 Hire strategy
- **Hands là thuê THEO NGÀY** (fib reset mỗi ngày): d0-1: 4 hands ($7) → d2-5: 5-6 ($12-20) → d6-8: 8-9
  ($54-88) → d9: 10 ($143) → **d10-27: 11 hands = $232/ngày** (fib 1..89) → d28-29: 10 ($143).
- Pattern hire: hires đặt **đầu giờ** (s = day×24+1) trước khi làm gì khác; hires ngày mới luôn nổ
  đúng 1-2 step sau nửa đêm. Tổng 285 lượt/$4,921 — chi phí "nhân sự" chỉ 4.2% revenue.
- 3 lượt hire FAIL của Majkel (s25×2 d1, s73 d3) vì tiền < giá fib — vô hại.

---

## 4. Chiến thuật sử dụng đất

### 4.1 Thời điểm mua land (kèm các cú FAIL — agent thử mua ngay khi có tiền)

| Bước | Bên | Kết quả | Tiền lúc order |
|---:|---|---|---:|
| s126 (d5) | M | **NE FAIL** (còn $460 < $1,000) | 460 |
| **s150 (d6)** | M | **NE OK** (−1,000, sau đợt WOOL đầu 6 units ở s149) | 2,017 → 1,017 |
| **s150 (d6)** | D | **NE OK** | 2,046 → 1,446 |
| s220 (d9) | M+D | SW FAIL (M $250, D $413) | — |
| s222 (d9) | M | SW FAIL ($1,115) — D **SW OK** ($2,148 → $148) | — |
| **s224 (d9)** | M | **SW OK** (−2,000, sau FERTILIZER sale) | 2,088 → $88 |

→ Mua land **ngay sau sự kiện doanh thu lớn** (đợt WOOL đầu tiên d6, đợt WOOL/MILK d9), ép số dư về
$88-148. Majkel mua SW **muộn hơn DSM 2 step** (thiếu tiền lúc s222) — thiệt hại ~0 (tile SW chỉ
cần kịp trồng trước d10-11).

### 4.2 Tại sao KHÔNG ai mua SE ($4,000)? — Phân tích opportunity cost
- 3 quadrant = 75 ô; trừ ~15 ô PASTURE/COOP + shed-path → **~57-61 ô trồng là capacity thực tế**
  (cả trận 2 bên giữ đúng 57-61 plants). Thêm SE = +25 ô nhưng:
  - Cần thêm ~4 hands/ngày: fib(12..15) = 144+233+377+610 ≈ **+$1,364/ngày** (hoặc tối thiểu +$377 nếu
    chỉ +2 hands) vs doanh thu carrot/tomato của 25 ô ≈ 25 × $21/ngày = **+$525/ngày** → **EV âm**.
  - Ô SE xa shed nhất (board 10×10, shed ở giữa) → unit tốn thêm bước di chuyển/harvest.
  - $4,000 ở d10-12 = 11-19% money — rủi ro cash-flow khi đang cần mua seeds/animals.
- Kết luận: bỏ SE là **đúng** trong meta này (khớp kết quả âm tính "SE" của meta-research 02).

### 4.3 Crop mix theo ngày (plants cuối ngày — M | D)

| Ngày | Majkel | DSM |
|---:|---|---|
| 0 | MELON 6, WHEAT 10 | idem |
| 2-5 | MELON 12, STRA 2→8, WHEAT 6→0 | idem (STRA 5-8) |
| 6-8 | STRA 15→22, WHEAT 2-3 (+4 COW, +4 SHEEP) | STRA 16→22 idem |
| 9-10 | STRA 22→25, WHEAT 17→25, MELON 12→6 | STRA 23, WHEAT 17→26 |
| 11-14 | **+CARROT 2→15, +TOMATO 1→3**, WHEAT 28→14 | WHEAT 31→33 (không carrot!), TOMATO 1 |
| 15-17 | CARR 13→11, TOMA 5→10, WHEA 14→11 | **WHEA 28→22**, TOMA 3→9, CARR 0→5 (mới bắt đầu d17!) |
| 18-21 | CARR 12→17, TOMA 14, WHEA 10-11, STRA 21→17 | CARR 7→15, TOMA 15→18, WHEA 16→11, STRA 21→15 |
| 22-27 | **CARR 23→30→31**, TOMA 9-13, WHEA 15-19, STRA 10→0 | CARR 16→23, TOMA 17, WHEA 20→25, STRA 8→0 |
| 28 | CARR 16 (thu hoạch dồn), TOMA 9, WHEA 17 | CARR 4, TOMA 11, WHEA 18 |
| 29 | TOMA 4, WHEA 6 (dọn sạch) | TOMA 10, WHEA 5 |

**Pivot theo giai đoạn:** MELON (d0-10) → STRAWBERRY backbone (d2-26) + WHEAT churn (d9-16) →
**CARROT factory (d11-28, Majkel sớm hơn DSM 6 ngày)** + TOMATO (d17-28). Majkel cắt WHEAT từ 26 (d12)
xuống 11-13 (d16-17); DSM giữ 33 cây WHEAT đến d16 rồi chuyển sang TOMATO nhiều hơn.

### 4.4 Kỷ luật tưới nước & weeds
- WATER ~54-71 lần/ngày trên 57-61 cây — phủ gần đủ. FERTILIZE 8-14 lần/ngày từ d15.
- **Weeds: Majkel 1 (d21), 0-2 rải rác; DSM 8 ở d28** — DSM rút bớt unit đi bán hàng → bỏ tưới 2 ngày
  liên tiếp → 8 ô thành weed đúng lúc cuối. d29: M 7, D 9 (hỗn loạn ngày cuối, ít ý nghĩa).
- Bảng chuyên sâu strawberry: Majkel giữ cây STRA sống tới d26 (25→10→5→3→0), DSM chết sạch từ d24
  (23→8→2→1) → Majkel thu thêm ~2 ngày production (~+10-15 units).

---

## 5. Chiến thuật MUA

### 5.1 Mua seed (chi tiết theo ngày — units gói)

| Ngày | Majkel | DSM |
|---:|---|---|
| 0 | MELON 6, WHEAT 10 | idem |
| 1-2 | MELON 4, MELON 2 + STRA 2 | idem |
| 3-5 | STRA 3+3+1 | STRA 4+2+1 |
| 6-8 | STRA 6+6+1, WHEAT 3+3 | STRA 7+5+1, WHEAT 3+3 |
| 9 | WHEAT 16 (SW vừa mở) | WHEAT 17 |
| 10 | STRA 3, TOMA 2, WHEAT 10 | STRA 1, WHEAT 9 |
| 11 | **CARR 6**, TOMA 2, WHEAT 11 | TOMA 1, WHEAT 11 |
| 12-14 | WHEAT 2; **CARR 7+8**; TOMA 1+3, WHEAT 12+6 | WHEAT 8+13+13; TOMA 2 |
| 15-16 | CARR 3+12, TOMA 1+1, WHEAT 6+5 | TOMA 2+6, WHEAT 12+10 |
| 17-19 | CARR 6; TOMA 3, WHEAT 5; CARR 6, WHEAT 7 | **CARR 12**, TOMA 3, WHEAT 9; CARR 6 TOMA 5 WHEAT 9; WHEAT 8 |
| 20-27 | CARR 11,18,12,6,11,13,6 (liên tục) + WHEAT 4-6/ngày | CARR 12,6,12,6,16,6 + WHEAT 6-8/ngày |
| **Tổng** | **STRA 25 · CARR 125 · WHEAT 124 · MELON 12 · TOMA 14** | **STRA 23 · CARR 76 · WHEAT 180 · MELON 12 · TOMA 19** |

### 5.2 Mua animal — giống hệt nhau, timing khớp shop
| Ngày | Mua | Ghi chú |
|---:|---|---|
| 0 | 2 COW (−800) + 3 SHEEP (−1,500) | SHEEP đẻ WOOL ngay d6 = đúng lúc YARN_STORE mở d6 |
| 6 | 2 COW + 4 SHEEP (−2,800) | sau đợt bán WOOL đầu |
| 8 | 2 SHEEP (−1,000) | |
| 9 | 1 COW + 1 SHEEP (−900) | cuối: **5 COW + 10 SHEEP = $7,000** |
| Sau d9 | 0 | không GOOSE nào — DSM spam 492 dead-SELL EGG suốt game |

**ROI động vật (Majkel):**
- SHEEP $5,000 → 196 WOOL @94.3 = $18,481 (**3.7x**). Chi tiết: 3 con đầu được CARE từ d0 → lượt
  cắt lông đầu d6 cho **6 WOOL/con** (care-bonus tích lũy 6) = 18 units @167-218 = $3,483 ngay d6.
- COW $2,000 → 107 MILK @41.5 = $4,440 (**2.2x**) — milk chết giá từ d16 (xem 6.3).
- **FERTILIZER (byproduct miễn phí): 179 units bán $11,514 + ~152 units tự bón** → đám vật nuôi
  "trả tiền" chủ yếu qua phân: $11.5K tiền + giá trị bón (~152 × ~$40 hiệu ứng ×2 yield) ≈ $18K.
- Feed: 178 units WHEAT mua ($6,507) + phần wheat tự trồng; FEED 4-16 lần/ngày ≈ đủ 15 con.
  **d28-29 FEED=0** — bỏ đói cuối game (3 SHEEP escape d28, 1 COW + 1 SHEEP d29 — vô hại ngày cuối)
  để bán sạch wheat; trước đó đã mất lẻ 1 SHEEP (~d20) + 1 COW + 1 SHEEP (~d22) vì feed không đều
  (đàn 15 → 12 → 9 → 7 từ d19 tới d29).

### 5.3 Mua WHEAT làm feed
- Majkel: 178 units $6,507 (avg 36.6) — tập trung d0-9 (26-37/unit) rồi giảm dần khi wheat tự trồng
  đủ (harvest wheat → PICKUP → FEED). Cả hai dùng feed-buy để **giá WHEAT thị trường đi lên**
  (25 → 42 ở d12) —Crop wheat của chính mình bán @37-42 (+49% vs base). Đáy đơn giá mua 26 (s1).
- COW ăn 1 WHEAT/ngày (engine L505-512: FEED = _inv_take WHEAT 1). MILK xuất hiện từ d8 (first_yield 8,
  interval 2): Majkel bán MILK 12@153 d8 — pattern mua feed d6-8 (4-17 units) khớp trước mỗi đợt MILK.

### 5.4 Mua FERTILIZER
- **KHÔNG ai mua fertilizer** (0 đơn). Nguồn duy nhất: COLLECT_FERTILIZER 1/con vật/ngày → bán 179
  units @64.3 = $11,514 + bón cây. Fertilizer bán giá giảm dần 100 → 29 (linear 0.40 hai chiều, T=200).

---

## 6. Chiến thuật BÁN

### 6.1 Doanh thu theo item — đơn giá đạt được vs base price ("premium")

| Item | M units | M avg | M premium | D units | D avg | D premium | Δ revenue (M−D) |
|---|---:|---:|---:|---:|---:|---:|---:|
| STRAWBERRY | **196** | **152.3** | +27% | 175 | 139.3 | +16% | **+5,475** |
| WOOL | 196 | 94.3 | −53% | 215 | 85.3 | −57% | +144 |
| CARROT | **310** | 51.8 | +48% | 170 | 52.2 | +49% | **+7,200** |
| WHEAT | 390 | 37.3 | +49% | 455 | 37.6 | +50% | −2,569 |
| MELON | 72 | 199.7 | −20% | 72 | 201.4 | −19% | −126 |
| FERTILIZER | 179 | 64.3 | −36% | 177 | 64.8 | −35% | +46 |
| TOMATO | 108 | 82.5 | +38% | 135 | 81.1 | +35% | −2,031 |
| MILK | 107 | 41.5 | −74% | 93 | 47.8 | −70% | −3 |
| **Tổng** | **1,558** | | | **1,492** | | | **+8,136** |

→ Chi +420 nhiều hơn → **margin đúng +7,716**. Premium dương = item có town hút (FM×3, PET_CAFE,
ICE_CREAM); premium âm = item bị cả 2 bên dump (WOOL sq-crash, MILK linear-crash, MELON không shop nào hút).

### 6.2 Timing bán strawberry — PHÂN TÍCH CHÍNH (throttle → hold → mega-dump)

Giá thị trường STRAWBERRY + sản lượng bán 2 bên theo ngày:

| Ngày | Giá (min..max) | Inv thị trường | M bán | D bán |
|---:|---|---:|---|---|
| 13 | 189..193 | 9,927 | 6@191 | 6@192 |
| 14-15 | 183..190 | ~9,935 | 2@190, 12@187 | 4@189, 10@186 |
| 16-17 | 157..185 | 9,959→9,979 | 16@181, 18@164 | 16@181, 15@164 |
| 18 | **105..158 (crash)** | 9,979→10,008 | 25@139 | 23@136 |
| 19 | 87..107 (đáy) | 10,008 | **2@104** | **16@94** |
| 20 | 84..112 | 10,019 | **5@105** | **26@100** |
| 21-23 | 84..114 | ~10,010 | **5, 11, 13 units @103-106** | 6, 7, 11 @102-108 |
| 24 | 84..132 | 10,000 | 4@88 | 6@119 |
| 25 | 114..148 (hồi) | 9,994 | 11@137 | 8@146 |
| 26-27 | 132..171 | 9,982→9,965 | 7@145, 4@154 | 6@155, 4@170 |
| 28 | 166..179 | 9,957 | 13@173 | 4@177 |
| 29 | 157..186 | 9,939 (trước dump) | **42@173 (s719!)** | 7@182 (rải 1-2/step) |

**Cơ chế:** d18 cả 2 dump 23-25 units → inventory vượt I0=10,000 → giá rơi 158→105. Từ d19:
- **Majkel THROTTLE**: chỉ bán 2-4 units/step (40 units trong 6 ngày @102.6 avg) trong khi cây vẫn
  ra ~10-12 units/ngày → **shed STRA tích lũy 0 → 20 → 33 → 51 → 57 → 68 → 65 units (d19-24, đỉnh 68 ở d23)**.
- **DSM tiếp tục dump**: 72 units @102.3 trong cùng kỳ (có cú 13@93 ngày d19, 10@95 ngày d20 —
  bán thẳng vào dao rơi), shed không bao giờ quá 7.
- Town (FM×3 + ICE_CREAM + center) hút **~25 units/ngày**; cây strawberry chết dần từ d22-26 →
  giá hồi 104 → 174. Majkel bán dần 8-13/ngày vào giá hồi + **giữ lại 42 units**.
- **Ngày 29: giá đi lên 175 → 186 trong ngày** (town hút, không ai bán) — Majkel bán hết
  carrot/wheat/tomato trong ngày nhưng **KHÔNG đụng strawberry** cho tới **step 719 (step cuối cùng
  của game)**: 1 order duy nhất 42 units, prices[0]=186, walk-down 186→158, avg 173, **+7,258**.

**Giá trị định lượng của chuỗi này:**
- Throttle d19-24: 117 units nếu bán ngay @102.6 = $12,004; thực tế Majkel thu $16,761
  (40@102.6 + 77@164.4) → **throttle gain ≈ +$4,757**.
- Phía DSM: 72 units bán @102.3 ở d19-24, nếu giữ bán @164.4 (như Majkel) → bỏ lỡ **≈ $4,474**.
- Chênh lệch đơn giá strawberry 152.3 vs 139.3 (13.0/unit) + volume 196 vs 175 → tổng **+$5,475**.

### 6.3 Timing các item khác
- **MELON d10:** cả 2 thu 12 cây × 6 units (bón đủ phân) rồi dump 30 units trong 4 order liên tiếp
  (s251-254) — giá 272 → 226 cùng ngày; Majkel đạt avg ~252 cho 18 units đầu (s251-253), cú 12 units cuối
  @235 (s254). Avg 199.7 (−20% base) vì nốt 12 units d11-12 bán @136-208. *Bài học: melon không có shop
  hút, dump sớm khi giá còn >240 thì tốt hơn giữ.*
- **WOOL d12:** Majkel 6@226 (s292) + 10@216 (s294), DSM 5@227 + 10@216, giá còn 226-228 (inv 9,976 < I0) —
  **đúng trước ngưỡng sụp**; d14-16 giá rơi 185 → 24 (hàm sq trên I0). Sau đó wool = rác $1-35,
  cả 2 vẫn bán từng unit (đúng — tiền nào cũng là tiền).
- **MILK:** không shop hút tới ICE_CREAM d24 → giá chết dần 185 (d8) → 110 (d12) → 19 (d16) → 1 (d18+).
  Majkel dump 12@153 (d8), 6@119 (d10), 3@108 (d12), 3@99 (d13), 17@59 (d14) rồi bán rác. Avg 41.5 — **thấp hơn DSM 47.8**
  vì Majkel chunk 12 units/lần (walk-down dốc) trong khi DSM chunk 3 units (@185/177/152/143).
  Bài học nhỏ: trên book dốc (linear 1.6), chunk nhỏ giá hơn.
- **CARROT:** giá rất ổn 41→55 (PET_CAFE d9 hút 12/ngày + FM×3 18/ngày) — Majkel bán 20-32 units/ngày
  d19-28 @51-55 không làm giá sụp. **310 units @51.8 = $16,068 — item doanh thu số 3.**

### 6.4 ENDGAME DAY 29 — mổ xẻ (xem log đầy đủ mục 10)

**Tồn kho trước d29 (s695, cuối d28):**

| | Majkel | DSM |
|---|---|---|
| Shed | **42 STRA** + 6 WOOL + 2 MILK = 50 | 7 STRA + 7 CARR + 6 MILK + 5 WHEA + 3 WOOL = 28 |
| Yield trên cây (sáng d29 gặt được) | 27 CARR + 28 WHEA + 2 TOMA = 57 | 26 WHEA + 4 TOMA + 4 CARR = 34 |
| Tiền đầu d29 | 78,413 | 77,329 |
| Tổng hàng bán d29 | 190 units | 136 units |

**Trình tự d29 của Majkel:** s696 shed đầy 100 (cap) → s697 **SELL CARROT 30@48** (order lớn nhất
giữa trận ngoài s719) + 8 hires ($54; đủ 10 hands cùng 2 hires s698) → bán nốt TOMA 11@77 (s709) → WHEAT rải 6-15/step @34-36 →
CARR rải 4-17/step @45-48 → **s719: STRAWBERRY 42@173 + WHEA 5@33 + CARR 2@45 + FERT 1@29 = +7,542**
→ hết sạch shed, kết thúc $91,845.
DSM bán rải đều mọi thứ (1-19 units/step, nhiều nhất 20), strawberry 7 units xé lẻ 1-2/step @180-183
(s702-712), s719 chỉ còn TOMA 11 + WHEA 9 + CARR 2 + FERT 2 = **+$1,260**.

**Phân giải margin cuối:**
| Thành phần | Giá trị |
|---|---:|
| Gap ngân sách cuối d28 (M−D) | +1,084 |
| Chênh lệch revenue ngày 29 (13,575 − 6,943) | +6,632 |
| Trong đó riêng step 719 (7,542 − 1,260) | **+6,283** |
| **= margin cuối** | **+7,716** |

**Tại sao tồn kho Majkel lớn hơn?** (a) throttle d19-24 giữ lại ~55 units; (b) nhiều cây STRA hơn
(25 vs 23) và sống lâu hơn (d26 vs d24); (c) carrot factory 125 gói seed; (d) DSM tiêu tốn hàng
vào vùng giá đáy.

### 6.5 Inventory accumulation (shed_total theo thời gian)
Majkel: ~0-20 (d0-15) → 50-95 (d16-21) → **94-100 (d22-29, chạm cap 100 ở d22/d28/d29)** → 0.
DSM: max 60-92 (d21-29), thường 17-35. → Majkel vận hành gần shed-cap 100 suốt cuối game,
vẫn không văng hàng (overflow discard = 0 mất mát quan sát được nhờ pipeline bán-hàng-ngày-cuối).

### 6.6 Dead orders ("rác")
| | Majkel | DSM |
|---|---|---|
| Tổng orders | 987 (968 exec) | 3,772 (1,043 exec) |
| Dead | **19** | **2,729** (2,709 là SELL vô hàng: TOMATO 594, EGG 492, MELON 400, CARROT 389, STRA 311, WOOL 270, MILK 252, WHEAT 1) |
| Lý do | hết tiền (BUY_SEED/land/hire fail) | standing-order spam — chiếm slot (cap 10 orders/turn) |

---

## 7. Tương tác thị trường & shops

### 7.1 Town consumption (engine: mỗi shop 4 step một lần, shop 1 sản phẩm ×2; center mỗi 24 step mỗi product)
Lượng town hút/ngày ở cuối game (sau d24): **CARROT ~31** (FM×3=18 + PET_CAFE×2=12 + center 1),
**STRAWBERRY ~25** (FM 18 + ICE 6 + 1), WHEAT ~37 (FM 18 + BAKERY×2 12 + ICE 6 + 1), TOMATO ~19,
WOOL 12 (YARN), EGG 12, MILK 6. → Giải thích: giá CARROT/STRA/WHEAT giữ trên base (+27..+49%)
còn WOOL/MILK/MELON chết giá.

### 7.2 Có pivot theo shop không?
- **YARN_STORE d6:** cả 2 đã có 3 SHEEP từ d0 (first yield đúng d6) và **+4 SHEEP ngay d6** —
  timing hoàn hảo với shop; đợt WOOL đầu 18 units @167-218.
- **PET_CAFE d9 (CARROT):** Majkel bắt đầu mua CARROT seed **d11** (6 gói) — phản ứng trong 2 ngày;
  DSM chậm tới **d17**. Đây là pivot tạo ra cả mảng $16K carrot revenue của Majkel.
- **FARMERS_MARKET d3/15/18:** hút 4 loại crop — đúng lúc Majkel mở rộng STRA+WHEAT (d9-10) và
  chuyển sang CARROT (d11+).
- **BAKERY d12/21 (EGG+WHEAT):** không ai nuôi GOOSE (EGG = 0) — chỉ WHEAT được hưởng; DSM vẫn
  spam SELL EGG 492 lần (chưa bao giờ có trứng).
- **ICE_CREAM d24 (STRA+MILK+WHEAT):** tăng tốc hồi giá strawberry cuối game (đỡ cho mega-dump).
- Ước tính tác động: town hút khoảng ~700-800 units các loại trong 30 ngày → giữ inventory dưới I0
  cho STRA/CARROT → premium +27-49% so với base; ngược lại chính 2 agent push WOOL/MILK trên I0.

---

## 8. Điểm mấu chốt (key moments)

| # | Step | Sự kiện | Ý nghĩa |
|---|---|---|---|
| 1 | s1-s2 (d0) | 2 COW + 3 SHEEP + wash WHEAT + 4 hires, còn $585 | opening chuẩn của cả family; CARE ngay từ d0 |
| 2 | **s149-152 (d6)** | WOOL 18 units @167-218 (6/con nhờ care-bonus) rồi mua NE + 4 SHEEP + 2 COW | cú tái đầu tư đầu tiên, money về đáy $49 |
| 3 | s251-254 (d10) | MELON dump 30 units @243-270 (+$7,367 trong 4 step) | ngày +6,609, nguồn tiền mở rộng |
| 4 | **s224 (d9)** | Mua SW muộn hơn DSM 2 step, còn $88 | mở 25 ô → STRA 25 + WHEAT 25 + CARR |
| 5 | d11 (s265-290) | Majkel bắt đầu CARROT (6 gói) — DSM không | +6 ngày carrot factory sớm hơn |
| 6 | **d18-19 (s448-474)** | STRA crash 158→105; Majkel cắt bán 25→2 units/ngày | điểm rẽ throttle — nơi trận đấu được thắng thầm lặng |
| 7 | d22-24 | shed STRA 57→68→65; giá hồi 114→132 | tích trữ đúng hướng town-drain |
| 8 | s292-294 (d12) | WOOL 15-16 units mỗi bên @216-227 bán đúng trước ngưỡng I0 | (cả 2) — kiểu "sell into strength" |
| 9 | d26-28 | Majkel bán STRA 4-13 units/ngày @145-177 + CARROT 25-32/ngày | gỡ gap −1,184 → +1,084 |
| 10 | **s719 (d29)** | **SELL STRAWBERRY ×42 @173 = $7,258** (96% revenue step cuối) | cú đánh quyết định, duy nhất 1 order |

---

## 9. Bài học cho v19 (nền v18/jaxa623)

v18 hiện có: HORIZON-24, OPEN-50, FRONT-LOAD (sells lên đầu), ADVANCE-2 (dời sale sớm 2 step khi
premium, skip dawn & step≥718); parent V43 có tape farm-plan + 41 routes + router theo shop.
Match2 gợi ý **các feature v18 CHƯA có**:

1. **ENDGAME LIQUIDATION SCHEDULER — "final-step mega-dump"** ★ lớn nhất: ngày 29, item có
   town-recovery cao nhất (điểm theo shop: STRA 25/ngày > CARROT 31 nhưng STRA đắt 3x) được GIỮ
   nguyên tới step 719 rồi bán 1 order duy nhất. Evidence: 42 STRA avg 173 (unit đầu 186) = $7,258;
   giá tăng 175→186 trong ngày chờ; +$6,283 của margin sinh ở step cuối. v18 hiện bỏ qua step≥718
   trong advance_sales — thay bằng module mới: nếu step == 719 → sell-all inventory theo thứ tự
   recovery giảm dần.
2. **TROUGH THROTTLE (price-gated sell rate):** khi giá < ~85% đỉnh rolling-14d hoặc < base, giới
   hạn bán 2-4 units/step (min impact), để shed hấp thụ (đến cap 100). Evidence: throttle gain
   +$4,757; DSM bỏ lỡ $4,474. Lưu ý mức giá hoạt động: d19-24 STRA ~84-114 vs đỉnh 193.
3. **CROP-MIX endgame: STRAWBERRY anchor + CARROT filler.** Evidence: 125 gói CARR ($2,500) →
   310 units $16,068 (ROI 6.4x); STRA 25 gói → 196 units $29,844 (ROI 11.9x). DSM dùng tile cho
   WHEAT (ROI ~11x nhưng giá thấp, bị cả hai bên bão hòa) + TOMATO. Tape-route của V43 nên có route
   STRA-heavy + CARR-filler khi shop có PET_CAFE/FM nhiều.
4. **STRAWBERRY PLANT-COUNT + keep-alive:** mỗi gói seed STRA dư = ~$1,500 revenue (8 units × ~150
   với fertilizer). Majkel 25 vs DSM 23 gói = +21 units = +$3,045. Tưới tuyệt đối để cây sống hết
   vòng đời (~d26); weeds = mất production (DSM 8 weeds d28).
5. **FERTILIZER ALLOCATION:** bón STRA/TOMA (ongoing, ×2 yield) ưu tiên — STRA 7.84 units/cây (≈8
   = max có phân), TOMA 7.7; CARROT 2.48 (thường không bón — đúng, seed rẻ). Động vật là "máy tạo
   phân": 179 bán + ~152 bón = ~$18K giá trị từ 15 con.
6. **SHED-CAP PIPELINE ngày cuối:** shed 100 là cap; phải xen kẽ sell→harvest→drop. Majkel đứng ở
   cap 3 lần mà vẫn xả sạch 190 units d29 (0 stranded). Thêm check "expected final-day throughput"
   vào terminal planner của V43.
7. **FEED-CUTOFF d28-29:** dừng FEED (FEED=0 từ d28) — bán nốt wheat @35 thay vì đổi thành milk
   $1-3; để động vật escape. Majkel bán 44 WHEAT d29 = $1,530.
8. **CHUNKING theo độ dốc book:** WOOL/MILK/MELON (sq/linear above-func) — chunk lớn khi giá còn
   TRÊN I0-threshold rồi dừng hẳn; MILK nên bán sạch trước ~d14 (Majkel còn giữ tới 17@59 d14,
   avg 41.5 < DSM 47.8 vì chunk 12). STRA/CARROT (sqrt/log, town hút) — chunk lớn an toàn.
9. **ORDER HYGIENE:** 0 dead-sell standing orders (DSM lãng phí 2,709 slot, từng bước chạm cap 10).
   v18 đã sạch (19 dead) — giữ nguyên; đảm bảo frontload không tạo rác.
10. **FEED-BUY sớm để nâng giá WHEAT cho crop mình:** 178 units mua d0-9 đẩy giá 25→37+; 390 units
    wheat self-crop bán @37.3 (+49% base). (Khớp ý tưởng #3 feed-buy index-0 trong roadmap MD3.)
11. **LAND: NE ngay sau revenue-event đầu (d6), SW sau đợt 2 (d9), SE KHÔNG BAO GIỜ** (toán:
    +25 ô cần +2-4 hands = +$377-1,364/ngày > $525/ngày carrot revenue; cộng khoảng cách xa shed).
    Agent nên retry-buy land mỗi step khi tiền thiếu (Majkel FAIL s126/s220/s222 rồi OK) — mô hình
    "order-đặt-hàng" này miễn phí.
12. **SELL-INTO-STRENGTH trước ngưỡng I0:** WOOL d12: inventory 9,976 (dưới I0 24 units) — cả 2
    bán 16-20 units @216-227 TRƯỚC khi vượt I0; ai chậm 2 ngày chỉ còn @85-114. Cần tracker
    "cumulative supply vs I0" per item (mình + đối thủ) — feature bám sát _simulate của v18.

**Anti-patterns quan sát được ở DSM (tránh):** dump 13-16 units STRA vào ngày giá đang rơi tự do
(d19-20 @93-100); giữ 33 WHEAT khi carrot/strawberry ROI cao hơn; 8 weeds d28 vì rút unit đi bán;
spam dead-sells.

---

## 10. Phụ lục: log ngày 29 full

| Step | Majkel (money sau) | DSM (money sau) |
|---:|---|---|
| 696 | SELL WOOL 1@1 — shed 100/100: CARR30, MILK6, **STRA42**, TOMA11, WHEA6, WOOL5 (78,414) | SELL CARR 6@50, WHEA 5@35 (77,804) |
| 697 | **SELL CARR 30@48 (+1,428)** + hire 8 (79,788) | SELL CARR 19@48, WHEA 8@35 + hire 8 (78,948) |
| 698-708 | WOOL/MILK lẻ @1-11; FERT 1@31; TOMA 11@77 (s709, 80,628); WHEA 6@36 (s710) | STRA 2@180 (s702), 2@182 (s706), 1@183 (s710); TOMA lẻ |
| 711-718 | WHEA 8+8+15, CARR 8+5+4+17, TOMA 2+3+2, FERT 4@30 — về $84,303; **shed còn STRA42 + lẻ** | STRA 1@182×3 (s711-712); TOMA/WHEA/CARR/FERT rải; về $82,869 |
| **719** | **SELL STRA 42@173 = +7,258** (prices 186→158) + WHEA 5@33 + CARR 2@45 + FERT 1@29 → **$91,845** | TOMA 11@74 + FERT 2@29 + CARR 2@45 + WHEA 9@33 → **$84,129** (+4 dead-sell STRA/MELON/MILK/WOOL/EGG) |

Giá STRAWBERRY trong ngày 29: 175 (open) → 186 (s718) → 157 (sau dump, không còn ai cần).
*(Nguồn: match2/orders.json, timeline.json, market.json, daily.json; engine kaggle_environments
1.32.7 kaggriculture.py: CROPS L11-17, ANIMALS L19-23, MARKET_PARAMS L41-51, WATER L431-443,
HARVEST L446-473, FERTILIZE L475-482, FEED L505-513, COLLECT_FERTILIZER L515-522, CARE L524-530,
_daily_refresh_plants/animals, _town_consume L728-749.)*
