# NGHIÊN CỨU REPLAY TOP-3 KAGGLE — VÒNG PHÂN TÍCH 1 (Task 38)

**Ngày:** 10 Sep (sau Task 37) · **Tác giả:** KAIN
**Nguồn:** 2 file replay Kaggle chính thức do user tải lên: `upload/107559251.json` (32.4MB) + `upload/107573831.json` (33MB) — episode đầy đủ 720 turn, engine `kaggle_environments 1.32.7` (khớp 100% engine local đã audit Task 21 mục Q.1).
**Phạm vi:** Chỉ phân tích học tập — CHƯA triển khai v7/kain41 (theo chỉ thị của user).

---

## PHẦN 0 — NGUỒN DỮ LIỆU & PHƯƠNG PHÁP

- Trích xuất toàn bộ 720 step × 2 player × 2 match: tiles 10×10, money, quadrants, herd, hands, market orders, prices, inventory, shops.
- **Quy ước replay đã xác minh bằng trace từng đô-la** (step 144-156 M1): `steps[t].observation` = trạng thái SAU khi `steps[t].action` được thực thi. Mọi phép đo trong file này dùng quy ước đó.
- Doanh thu theo kênh: tái dựng giá từng unit theo công thức giá engine (MARKET_PARAMS gốc) + điều hòa bằng sổ cái tiền (final = 3000 + revenue − costs). Doanh thu absolute có sai số ±20% do SELL fail khi shed rỗng (đơn vị "requested" ≠ "executed"); TỶ TRỌNG theo kênh là tín hiệu đáng tin.
- Bộ tool phân tích: `tool-results/replay_analyze.py` (extract), `replay_ledger.py` (sổ cái), `q1_land.py`→`q7_plant.py` (query).

**4 người chơi (top-3 bảng xếp hạng Kaggle):**

| Trận | Đối thủ | Kết quả | Chênh |
|---|---|---|---|
| M1 (107559251) | **SpaTaro** vs **Unknown Mother-Goose** (UMG) | $93,281 vs **$99,793** | −$6,512 |
| M2 (107573831) | **SpaTaro** vs **Otter Vibe** | $107,329 vs **$109,084** | −$1,755 |

**SpaTaro thua cả 2 trận nhưng vẫn ở mức $93-107k** — cả 4 performance đều gấp ~2x mức tốt nhất của chúng ta (kain40 $58k, v6.6 $45-55k). Tổng tiền 2 bên mỗi trận: **$193k (M1) / $216k (M2)** — trận đấu top-3 gần như ĐỐI XỨNG (0.98-1.07x), không phải trận đè bẹp.

---

## PHẦN 1 — BỨC TRANH CHIẾN LƯỢC TỔNG QUÁT (điểm chung của cả 4 lượt chơi)

### 1.1 Timeline chuẩn 30 ngày (tổng hợp từ cả 4 lượt)

| Giai đoạn | Hành động | Chi tiết |
|---|---|---|
| **d0** | Mở màn "vườn ươm + chuồng" | Trồng melon 6-16 ô + wheat 3-18 ô + carrot 2 ô. **Mua 3-5 con vật NGAY d0** (bò 1-5, cừu 1-2, ngỗng 2). Hire 5-7. Tiền về ~$0-230 cuối ngày d0. |
| **d1-3** | Thu hoạch fertilizer = **máy in tiền khởi động** | Mỗi con vật nhả 1 FERT/ngày → 3-6 FERT/ngày × $95-100 = **$300-600/ngày từ d1**. Đây là nguồn vốn mua đất sớm. UMG giàu nhất giai đoạn này ($619 d1, $890 d2). |
| **d3-6** | **Mua NE ($1k)** — đúng vào lúc vốn tích đủ | UMG d3 (sớm nhất), Otter d5, SpaTaro d6 (cả 2 trận). Trống 20-78% 1-2 ngày ngay sau mua rồi lấp lại. |
| **d4-7** | **Sóng dâu đợt 1: 14-17 ô** | Mua 20-40 hạt dâu ($100/hạt), trồng dọc d5-7. Được bón phân + tưới đủ → chờ event d10-16. |
| **d5-10** | **Mua SW ($2k)** — sớm hơn cửa sổ 10-12 | UMG d8, SpaTaro d8 (cả 2 trận), Otter d10. Sau mua: lấp đầy trong **1-2 ngày** (0-16 ô trống thoáng qua). |
| **d8-9** | Bò bắt đầu cho sữa (first_yield_day 8) | Sữa chảy từ d8: 2-6 u/ngày mỗi bên. Wheat machine (24-41 ô) vận hành để FEED. |
| **d10-12** | **QUẢ BOM MELON chín** | 76-90 quả × $143-271 = **$13-22k trong 2-3 ngày**. Đây là cú vốn giữa game. |
| **d10-16** | Sóng dâu đợt 2 (5-9 ô) + **TOMATO** (chỉ 2 người thắng) | Dâu event mỗi 2 ngày (4 lần × 1-2u/ô); cà chua event mỗi ngày d8-11. |
| **d12-20** | **Mở rộng đàn theo shop draw** | Xem Phần 6 — đây là điểm quyết định thắng thua. |
| **d13-27** | **Chạy ổn định 75/75 ô, empty 0-2%** | Dâu 20-34 đứng + wheat 15-31 + đàn 14-22 con + carrot/straw thay phiên. **FERTILIZE dâu 92-186 lần** (×2 yield). |
| **d21-26** | Dâu chết tuổi → **CARROT lấp chỗ** (7-12 ô/ngày) | Carrot $35-56 (PET_CAFE d18/d21+ hút mạnh ở M2). Wheat tăng 22-41 ô. |
| **d27-29** | **THANH LÝ TOÀN BỘ** | Ngừng trồng, thu tất cả, bán dồn. Ngày 29 bán 348u (UMG) / 97u wheat (SpaTaro M2). Shed cuối game: **0-16u tồn** (~$0-300 lãng phí trên $100k+). |

### 1.2 Bảng đối chiếu mua đất (kiểm chứng 4 luật cứng)

| Người chơi | NE (50 ô) | SW (75 ô) | SE (100 ô) | Empty d7-26 (duy trì) | Empty max sau khi mua |
|---|---|---|---|---|---|
| SpaTaro M1 | d6 | **d8** | KHÔNG | 0-7% (đa số 0-1%) | 5 ô (1 ngày) |
| UMG (thắng M1) | **d3** | **d8** | KHÔNG | **0-7%** (d9-27 hầu như 0) | 39 ô (d4, sau NE sớm — thung lũng 2 ngày) |
| SpaTaro M2 | d6 | **d8** | KHÔNG | 0-5% | 8 ô |
| Otter Vibe (thắng M2) | d5 | **d10** | KHÔNG | **0% tuyệt đối d11-27** (chỉ 16 ô 1 ngày sau SW d10) | 16 ô (1 ngày) |

**Phán quyết 4 luật cứng của user (từ quan sát top-Kaggle):**
1. ✅ **NE d5-7** — đúng khung (biến thể: d3-6; sớm hơn nếu vốn cho phép — UMG d3 vẫn thắng)
2. ✅ **SW d10-12** — đúng khung (biến thể: **d8-10 — cả 3 người còn lại mua SỚM HƠN** cửa sổ 1-2 ngày)
3. ✅✅ **KHÔNG BAO GIỜ 100 ô** — 4/4 lượt chơi, không ai mua SE dù cuối game có $30-90k nhàn rỗi
4. ✅✅ **Empty 0-15%** — thực tế còn gắt hơn: **0-7% duy trì d7-26**; spike duy nhất = 16-39 ô trong **đúng 1 ngày** sau khi mua đất, lấp lại trong 24h

**Điểm mới quan trọng nhất: lấp NE/SW mất 1-2 NGÀY** (không phải 5-9 ngày như kain33-40 của ta). Họ có sẵn hạt + lao động dự trữ TRƯỚC khi mua đất.

---

## PHẦN 2 — KINH TẾ KÊNH: SỔ CÁI DOANH THU

### 2.1 Doanh thu theo kênh (điều hòa theo sổ cái tiền, ±20%)

**M1 (SpaTaro thua vì chọn sai kênh):**

| Kênh | SpaTaro ($93.3k) | UMG ($99.8k) | Ghi chú |
|---|---|---|---|
| STRAWBERRY | **$65.5k** (413u) | $43.9k (313u) | Kênh #1 cả hai bên |
| WHEAT | $22.7k (904u) | $10.6k (509u) | SpaTaro là máy xay wheat |
| MELON | $17.9k (90u) | $15.7k (150u) | Bom d10-12 |
| FERTILIZER | $7.3k (123u) | **$19.7k (406u)** | UMG thu FERT tử tế |
| WOOL | $5.3k | $4.8k | Bằng nhau |
| CARROT | $3.9k | $6.1k (210u, chủ yếu d26-29) | |
| MILK | $3.4k (87u @ avg $48) | $5.3k (152u) | **Kênh CHẾT ở M1** — giá sữa sập $8 |
| EGG | $0 (0 ngỗng) | **$11.1k (228u)** | UMG độc quyền 6 ngỗng |
| TOMATO | $0 | $3.6k (78u) | |
| **TỔNG revenue** | ~$126k | ~$121k | SpaTaro gross CAO HƠN |

**M2 (đối xứng — cả hai đều $107k+):**

| Kênh | SpaTaro ($107.3k) | Otter Vibe ($109.1k) | Ghi chú |
|---|---|---|---|
| MILK | **$36.7k (254u)** | **$38.4k (231u)** | Kênh #1 M2 — 9 vs 11 bò |
| STRAWBERRY | $36.4k (313u) | $32k (224u) | |
| WHEAT | $29.6k (863u) | $13.3k (351u) | SpaTaro bán wheat 2.5× |
| MELON | $18.8k (98u) | $12.6k (90u) | |
| FERTILIZER | $9.1k (178u) | **$16.1k (280u)** | |
| EGG | $0 | **$13.9k (322u)** | 8 ngỗng của Otter |
| CARROT | $7.6k | $7.1k | |
| TOMATO | $0 | $6.1k (100u) | |
| WOOL | $5.3k | $5.3k | Bằng nhau tuyệt đối |
| **TỔNG revenue** | ~$143.5k | ~$144.8k | Gần như hoàn hảo đối xứng |

### 2.2 Chi phí (theo sổ cái tái dựng)

| Hạng mục | SpaTaro M1 | UMG | SpaTaro M2 | Otter Vibe |
|---|---|---|---|---|
| Hạt giống | $9.4k (176 wheat + 55 straw + 33 carrot + 18 melon) | $7.3k | $9.4k | $6.5k |
| Con vật | $7.3k (7 bò + 9 cừu) | $5.7k (6 bò + 3 cừu + 6 ngỗng) | $8.7k (12 bò + 6 cừu + 3 ngỗng) | $8.3k (11 bò + 3 cừu + 8 ngỗng) |
| Mua wheat feed | $14.0k (449u) | $4.5k (134u) | $16.7k (446u) | $9.0k (244u) |
| **HIRE (272-293 lần)** | $3.4k | $5.4k | $4.1k | **$12.8k** ⚠ |
| Đất (NE+SW) | $3k | $3k | $3k | $3k |
| Mua FERT | $1.6k | $1.0k | $0.2k | $2.1k |

⚠ **Otter Vibe đốt $12.8k tiền hire** (13-15 thợ/ngày cuối game, fib $89-377/thợ) và VẪN THẮNG — lao động cuối game có ROI $100-200/action khi dâu+sữa ở đỉnh giá.

### 2.3 Cấu trúc đàn — điểm khác biệt thắng/thua lớn nhất

| | SpaTaro M1 | UMG ✅ | SpaTaro M2 | Otter ✅ |
|---|---|---|---|---|
| Ngỗng (EGG+FERT) | **0** | **6** (mua d8-10) | 3 (chết sớm) | **8** (d4-7) |
| Bò (MILK) | 4 | 5-6 | 9 | 11 (mua d15-18) |
| Cừu (WOOL) | 3 | 3 | 2 | 3 |
| Tổng đàn | **7** | **14** | 11-13 | **22** |

**Cả 2 người thắng đều có ngỗng; cả 2 lần SpaTaro thua đều không có/không giữ ngỗng.** Ngỗng = EGG ($11-14k) + FERT (1/con/ngày) + chăm nhẹ.

---

## PHẦN 3 — CƠ CHẾ ĐỌC SHOP DRAW (game theory quyết định thắng thua M1)

### 3.1 Shop là số phận kênh

Shop unlock mỗi 3 ngày (d3, d6, d9, ..., d24; tối đa 8 instance, bốc CÓ hoàn lại):

| Trận | Shop draw | Hệ quả giá |
|---|---|---|
| M1 | BRUNCH×3 + BAKERY + SMOOTHIE×2 + PET_CAFE + FARMERS (d24) | **EGG demand 4 instance** (BAKERY d6 + BRUNCH d3/d9/d12) → trứng khan hiếm −360u → $73. **MILK demand gần bằng 0 đến d15** (chỉ SMOOTHIE d15/d24 + town center) → sữa +73 above-I0 → **sập $8**. WHEAT demand 7 instance → khan −181 → $38. |
| M2 | PET_CAFE×3 + ICE_CREAM×2 + BRUNCH + PIZZA + SMOOTHIE | **MILK demand 4 instance từ d9-15** (ICE d9/d12, PIZZA d15) → sữa khan −25 → **$122-200 cả mùa**. CARROT demand 3 PET_CAFE ×2u = mạnh → $35→56. EGG chỉ 1 BRUNCH → $42. STRAW 4 instance → $211 đỉnh nhưng **2 bên bán 537u → sập $37 d23-25** (tự hủy chung). |

### 3.2 Phản ứng của người thắng (ADAPTIVE herd scaling)

- **UMG (M1)**: d0 mua 5 bò (trước khi biết gì) → thấy BAKERY d6 + BRUNCH d3/d9 = trứng mạnh → **mua 6 ngỗng d8-10, KHÔNG mở rộng bò** (sữa đang chết). Kết quả: $11.1k trứng + $19.7k FERT mà không đổ thêm tiền vào kênh sữa chết.
- **Otter (M2)**: thấy ICE_CREAM d9/d12 + PIZZA d15 = sữa mạnh → **tăng bò 6→9→11 theo từng mốc shop d15/d18**. Đồng thời giữ 8 ngỗng từ d4-7 (trứng $44 vẫn dương + FERT machine).
- **SpaTaro (M1, thua)**: profile cứng 4 bò 0 ngỗng — bán sữa avg $48 vào kênh $8-40, không có kênh trứng dù demand mạnh nhất mùa.

→ **Bài học lớn nhất M1: herd composition phải đọc shop draw d3-d12, không phải theo profile tĩnh.** Đây là biến thể của R50 (tín hiệu thị trường > tín hiệu đối thủ) nhưng ở tầng cấu trúc đàn.

### 3.3 Cung-cầu 9 kênh (kiểm chứng inventory I0=10000)

- Kênh có SHOP hút (wheat/egg/milk/straw theo draw): giá giữ trên base khi 2 bên bán đúng nhịp drain (M2 milk −25u → $122-200; M1 wheat −181 → $38).
- **Kênh KHÔNG có shop nào hút: MELON (0 shop), FERTILIZER (0 shop + bị loại khỏi town center)** → mọi unit bán vào là cộng dồn inventory vĩnh viễn, giá chỉ đi xuống (melon $270→$74; FERT $100→$26-51). Vẫn bán được lớn ($12-27k) nhưng phải bán SỚM + NHỎ.
- **FERT dùng nội bộ (FERTILIZE) là "drain" duy nhất của kênh FERT**: Otter FERTILIZE 186 lần = tiêu 186u tự sản, giữ giá FERT thị trường. Vòng lặp: thú nhả FERT → bón dâu → dâu ×2 yield.

---

## PHẦN 4 — HỆ THỐNG LAO ĐỘNG & LOGISTICS (khác biệt cấu trúc lớn nhất vs engine ta)

### 4.1 Các con số lao động mỗi ngày (giai đoạn ổn định d13-27)

| Chỉ số | SpaTaro | UMG | Otter Vibe |
|---|---|---|---|
| Hands thuê | 9-12 | 10-12 | **13-15** |
| WATER/ngày | 50-73 | 39-57 | 28-54 |
| FEED/ngày | 3-7 | 7-14 | **17-22** (full-care 22 con) |
| CARE/ngày | 3-7 | 6-14 | **14-19** |
| HARVEST/ngày | 9-32 | 18-38 | 22-39 |
| PLANT/ngày | 5-18 | 3-17 | 2-24 |
| COLLECT_FERT | 4-7 | 10-15 | 12-24 |
| MOVE/ngày | 97-148 | 100-136 | 105-152 |
| **Tổng action/ngày** | 189-259 | 204-268 | 253-344 |

So với engine ta (kain40/v6.6: **52-67 action/ngày, 12-13 units, 71% thời gian đi bộ**) — top-3 chạy **4-5× tổng khối lượng hành động** với chỉ ~1.2× số units. 

### 4.2 Hai khám phá cơ chế then chốt

1. ** KHÔNG CẦN ĐI VỀ SHED CUỐI NGÀY**: `_drop_inventories_to_shed` chạy ở end-of-day — tay thợ chết lúc h23 và TOÀN BỘ inventory tự đổ vào shed. Top players cho thợ thu hoạch khắp farm suốt ngày, không bao giờ đi về. Đây chính là "phím tăng tốc lao động" 2-3× mà R127 (trần 85% fill) của ta bị khóa.
2. ** HIRE 90% diễn ra ở h1-h2** (208-244/272-293 lần) — ngay sau đợt bán sáng (tiền có sẵn) và fib reset đầu ngày. Bán sáng → thuê → dispatch.

### 4.3 Hai phong cách nuôi động vật (đều thắng/thua)

| | SpaTaro "producer-feeding" | Otter "full-care" |
|---|---|---|
| FEED/CARE | 4-7/ngày (chỉ bò ĐANG có sữa hôm đó) | 17-22/ngày (mọi con, mọi ngày) |
| Wheat tiêu | ~5u/ngày | ~20u/ngày |
| Sữa/bò/ngày (đo thực tế) | **~1.3-1.4u** (254u / 9 bò) | ~1.0-1.1u (231u / 11 bò) |
| Chi phí chênh | tiết kiệm ~$10-12k wheat/mùa | đốt thêm nhưng bù bằng EGG+FERT scale |

Kết quả sữa/bò gần như NGANG NHAU → **care-bonus không đáng tiền bằng giá wheat ở M2 ($40+)**; nhưng full-care nuôi được đàn LỚN hơn (22 vs 13 con) để chạy kênh FERT+EGG. Hai chiến lược đều khả thi — điều quyết định là TỔNG ĐÀN + ĐỌC SHOP.

### 4.4 Nhịp bán (tranche discipline — R90 đúng và còn gắt hơn)

- Đơn hàng SELL trung bình **3.5-15.3u** (không bao giờ dội 20+u một lệnh)
- Giờ bán: **h0-2 (sáng, sau shed đêm) + h21-23 (tối)** — UMG 47 bán ở h22, Otter 72 bán ở h0
- Tổng units bán ra: **1,963-2,119u/người/mùa** (~70u/ngày) với shed 100 → shed là bộ đệm NGÀY, không phải kho

---

## PHẦN 5 — THANH LÝ CUỐI GAME (E8 ở quy mô chưa từng thấy)

| | d28 | d29 (ngày cuối) | Tồn cuối |
|---|---|---|---|
| SpaTaro M1 | +$5.6k | +$4.4k (57 wheat + 36 dâu + 55 carrot + ...) | 16 wool + 5 hạt |
| UMG | +$4.6k | **+$11.6k** (94 wheat + 34 dâu + 24 trứng + **125 carrot** + 40 FERT + ...) | **~0** (1 hạt wheat) |
| SpaTaro M2 | +$5.1k | +$4.5k | ~0 (1 FERT + 6 hạt) |
| Otter | +$3.7k | **+$11.6k** | 6 wool + 7 wheat trên ô |

Ngày 29 riêng lẻ đóng góp **$4.4-11.6k** (5-11% tổng tiền). Người thắng M1/M2 đều có ngày cuối $11.6k — thanh lý là "trận trong trận". Họ ngừng trồng từ d27-28, thu+dồn bán hết, kết thúc sạch bóng (R71 của ta: tồn $250-800 — top-3 để lại <$300).

**Cấu trúc ngày 29 của người thắng**: dồn tất cả tồn + thu harvest cuối + bán theo hàng đợi 10 lệnh/giờ tới h22, giá chấp nhận (carrot 125u vẫn bán được $38-44 vì drain PET_CAFE còn hút).

---

## PHẦN 6 — ĐỐI CHIẾU RULES.md ↔ THỰC TẾ TOP-3 (yêu cầu chính của user)

### 6.1 ✅ QUY TẮC ĐƯỢC XÁC NHẬN (giữ nguyên, bổ sung bằng chứng)

| Quy tắc | Bằng chứng từ replay |
|---|---|
| R8 (lịch ongoing 4 events) | Dâu 4 events × 2 ngày, chết tuổi 17 (cả 4 lượt dâu chết d20-23 đúng lịch) |
| R10 (melon window đóng) | Không ai trồng melon sau d15 |
| R24 (shed 100 + end-of-day dump) | **Được khai thác TỐI ĐA** — xem 4.2: đây là phím lao động top-3 |
| R36 (chỉ WHEAT+FERT mua được) | SpaTaro spam 248-260 lệnh BUY_PRODUCT vô hiệu (CARROT/EGG/MELON/MILK/STRAW/TOMATO) — engine drop sạch. **Cả bot top-3 còn mang bug này** |
| R37/R48 (wheat churn/room) | M2: 2 bên tự trồng ~527u + mua 244-446u → wheat khan −355 → $44. Mua feed $40 đổi sữa $170 = 4× margin (R92 đúng ở quy mô top) |
| R49 (wool floor 2-3 cừu) | Mọi người đúng 2-3 cừu, wool $5.3k bằng nhau tuyệt đối. 5-6 cừu tổng 2 bên vẫn sập giá (T=105 quá hẹp) |
| R83 (first-mover premium) | Dâu trồng d5-7 bắt event d10-14 ở $165-188 |
| R90 (tranche sâu/dump chết) | Melon dump d10-12 (kênh không drain) vs milk tranche nhỏ cả mùa (kênh drain sâu) |
| R92 (wheat→milk converter) | 9-11 bò + wheat machine 24-41 ô — đúng cấu trúc, nhưng quy mô 2× |
| R101 (hiến kênh) | M2: 2 bên cùng dội dâu d20-26 → cùng ăn giá $37-56 |
| R53/E8 (thanh lý d29) | $4.4-11.6k ngày cuối (xem Phần 5) |
| R5 (P0/P1) | Cả 2 trận chênh 1.6-6.9% — knife-edge ở top |

### 6.2 ❌ QUY TẮC BỊ MÂU THUẪN / CẦN HIỆU ĐÍNH

| Quy tắc | Thực tế top-3 | Hiệu đính đề xuất |
|---|---|---|
| **R74 "Đất tối ưu = 50 ô (NW+NE)"** | **4/4 lượt chơi đều mua 75 ô.** R74 chỉ đúng trong bối cảnh v5-vs-v4 (đối thủ yếu, quota không binding — đã tự ghi chú sẵn trong R74) | R74 giữ nguyên phạm vi "vs đối thủ yếu"; luật top-3 là **75 ô + fill 98-100%** (kết hợp R100 + kernel lao động mới) |
| **R127 "Trần lao động: fill tối đa 60-66 ô, 85% là giới hạn vật lý"** | **BỊ PHỦ BỎ HOÀN TOÀN**: Otter Vibe fill 75/75 + 22 con vật với 253-344 action/ngày (vs 67 của ta). Chìa khóa = cơ chế shed end-of-day dump (4.2) + 13-15 hands | R127 hiệu đính: trần 67 action/ngày là trần của KERNEL LAO ĐỘNG v6 (đi-về-shed), không phải vật lý game. Vật lý thật: ~350+ action/ngày với 15 units |
| **R75 "Lấp đất bằng wheat = tự sát"** | Top-3 lấp 24-41 ô wheat (32-55% đất!) NHƯNG làm máy FEED cho đàn 11-22 con, không phải để bán rẻ | Phân biệt wheat-FEED (đúng) vs wheat-SELL-flood (sai): R75 đúng cho bán, cần luật mới cho feed-machine 24-41 ô |
| **R114 "wheat-flood nuôi bò đối thủ"** | Chỉ đúng khi ĐỐI THỦ mua wheat. Top-3 TỰ TRỒNG ~527u + chỉ mua phần thiếu (244-446u); không ai phụ thuộc hoàn toàn vào mua feed | Hiệu đính phạm vi: R114 áp dụng khi telemetry (R44) đọc được đối thủ net-buyer wheat |
| **R86 (milk counter-scale theo archetype)** | Mức cao hơn: quyết định đàn theo SHOP DRAW (public info từ d3!) chứ không phải theo đối thủ | Nâng cấp: shop draw là tín hiệu SỚM hơn telemetry đàn (R78 đã nói telemetry trễ) |
| **R100 (SE = option value $4k đổi $8-12k quota)** | Top-3 KHÔNG mua SE dù quota dâu/wheat đầy 75 ô + $30-90k tiền nhàn rỗi cuối game | 100 ô KHÔNG nằm trong optimale top-3; option value của R100 chưa đủ lớn khi kernel lao động đã bão hòa ở 75 |
| R17 (FERT 1/con/ngày miễn phí) | Được coi là KÊNH DOANH THU chính: $9.1-19.7k/mùa, nhiều khi lớn hơn milk | Bổ sung giá trị: FERT = 25-33% doanh thu "đàn" khi卖的 đúng nhịp |
| R58 (kho là độ trễ) | Top-3 bán 70u/ngày — shed-clearing daily là chuẩn mực | Tăng nhịp dọn: tồn shed qua ngày = lãng phí action chở đồ |

### 6.3 ✨ PHÁT HIỆN MỚI KHÔNG CÓ TRONG RULES.md (đề xuất R131-R138)

**R131 [E] — FERT-FUNDED BOOTSTRAP**: Con vật mua d0 trả FERT từ d1 ($95-100/u) = $300-600/ngày tiền mặt khởi động, tài trợ mua NE d3-6. Mở màn không có con vật = chậm 2-3 ngày vốn đất. (UMG: 6 con d0 → NE d3.)

**R132 [E] — ĐỌC SHOP DRAW LÀ DECISION LAYER CẤP CAO NHẤT CỦA ĐÀN**: từ d3 mỗi 3 ngày 1 shop mở; herd composition (ngỗng/bò) phải đổi theo số instance kênh: M1 (4 egg-shop) → 6 ngỗng + 5 bò thắng; profile cứng 4 bò + 0 ngỗng thua. Tín hiệu shop công khai từ d3-d12, TRƯỚC khi telemetry đối thủ có ý nghĩa.

**R133 [E] — SHED END-OF-DAY DUMP = ĐÒN BẨY LAO ĐỘNG 2-3×**: tay thợ không cần quay về shed — chết h23, inventory tự về kho. Toàn bộ hành động giữa ngày dành cho harvest/water/plant xa shed. Đây là cơ chế để fill 75 ô ở 0% empty (phá trần R127).

**R134 [E] — SELL-BEFORE-HIRE (nhịp h0-2)**: 90% HIRE ở h1-2 sau đợt bán sáng (fib reset + tiền có sẵn); mua hạt/thú sau hire. Ngược trình tự này = mất ngày lao động.

**R135 [E] — MELON LÀ BOM VỐN GIỮA GAME, KHÔNG PHẢI KÊNH**: 90-150 quả d10-12, bán hết trong 2-3 ngày ($13-22k), sau đó kênh chết vĩnh viễn (0 shop drain) — không cố quay lại. Kết hợp R114: nửa sau mùa chuyển hoàn toàn sang wheat-feed + carrot.

**R136 [E] — TOMATO LÀ KÊNH THỨ 4 CỦA NGƯỜI THẮNG**: 5-12 ô d10-18 (sau khi dâu đợt 1 xong), $5-6.2k/season, 100-130u. Chỉ 2 người thắng dùng (SpaTaro bỏ qua cả 2 trận). Event mỗi ngày (interval 1) = dòng đều, cân bằng dâu (mỗi 2 ngày).

**R137 [E] — FERTILIZE DÂU 90-190 LẦN/MÙA = +100% YIELD KÊNH #1**: bón phân đúng event-day (fert+water → yield ×2 theo R8) trên 20-34 ô dâu đứng. 186 lần của Otter tiêu FERT nội bộ (tự sản) — vòng lặp dâu↔đàn khép kín. FERT không bón = bỏ 50% doanh thu kênh lớn nhất.

**R138 [E] — LIQUIDATION-DAY LÀ "TRẬN TRONG TRẬN" ($4-11.6k)**: d27 ngừng trồng → d28-29 thu tất cả + bán theo queue 10 lệnh/giờ đến h22, kể cả bán 125 carrot một ngày cuối. Kết thúc sạch <$300 tồn. E8 của ta thu $3-5k thời v4 — top-3 gấp đôi.

### 6.4 Kiểm chứng chéo 4 luật cứng (AA) của user

| Luật cứng AA | Trạng thái sau replay |
|---|---|
| 50 ô ngày 5-7 | ✅ đúng (biến thể d3-6; sớm hơn nếu vốn FERT đủ) |
| 75 ô ngày 10-12 | ✅ đúng (thực tế d8-10 — sớm hơn 1-2 ngày) |
| Không 100 ô | ✅ 4/4 |
| Empty 0-15% | ✅ thực tế 0-7% (d7-26), spike 1 ngày khi mua đất |

→ **4 luật cứng của user là ĐÚNG và được replay xác nhận đầy đủ** — khác biệt duy nhất: cửa sổ mua đất thực tế XIÊN SỚM hơn (d3-8), và "0-15%" thực chất là "0-7% + 1 ngày thông khí khi mua đất".

---

## PHẦN 7 — HÀM Ý CHO v7 (chưa triển khai — chỉ định hướng)

1. **Lao động là đồng xu tăng tốc**: cơ chế R133 + hire 13-15 cuối game = fill 75 ô 100%. Kernel lao động v7 phải tận dụng end-of-day dump (không đi về shed giữa ngày) — đây là điều kiện tiên quyết cho luật empty 0-7%.
2. **Đàn 14-22 con theo shop draw** (R131/R132): FERT $10-20k + EGG $11-14k + MILK $37-43k = "kênh đàn" tổng $60-70k — lớn hơn toàn bộ doanh thu v6.6 hiện tại.
3. **Dâu 20-34 ô + FERTILIZE nội bộ** (R137): kênh #1 $32-66k.
4. **Wheat machine 24-41 ô làm feed** + mua thêm khi $40 (R92 scale 2×) — wheat-FEED ≠ wheat-flood (R75).
5. **Melon bomb d0-5 → thanh lý d10-12** (R135) rồi chuyển hoàn toàn feed/premium.
6. **Thanh lý d27-29 chuẩn $5-11k** (R138) — DP ngưỡng giảm dần + queue 10 lệnh/giờ.
7. **Thang điểm chuẩn mới**: $93-109k/lượt (2× kain40 hiện tại) — tổng 2 bên $193-216k nghĩa là nền kinh tế đủ cho cả hai cùng $100k+ khi KHÔNG crash kênh chung (M2 gần như Pareto-optimal $107k/$109k).

---

## PHẦN 8 — CÂU HỎI MỞ CHO VÒNG PHÂN TÍCH 2

1. Tại sao UMG/Otter để shed gần 0 ở cuối game nhưng SpaTaro M1 còn 16 wool — DP thanh lý của họ có ngưỡng giá thế nào?
2. Producer-feeding (SpaTaro) vs full-care (Otter) — cần A/B để tìm điểm tối ưu theo giá wheat;
3. Chu kỳ wheat 5 ngày: trồng lại bao nhiêu ô/ngày để duy trì 24-41 standing? (trace PLANT wheat theo ngày: 3-17 ô/ngày, gần như liên tục)
4. Ngỗng 6-8 con có phải ceiling không (max_held 4 trứng/ngày/con)?
5. Đòn zero-sum có tồn tại ở top không? (M2 cho thấy 2 bên gần Pareto — có lẽ "đánh tốt hơn" ở top = "tổng lớn hơn", R94 đúng ở tầng tối thượng)

---
*KAIN — TOP3_REPLAY_ANALYSIS.md v1.0 (Task 38, vòng phân tích 1). Nguồn: 107559251.json + 107573831.json. Tool: tool-results/replay_*.py + q1-q7. Số liệu absolute ±20% (requested≠executed), tỷ trọng kênh đáng tin. Chưa triển khai v7/kain41 theo chỉ thị.*
