# NGHIÊN CỨU REPLAY TOP-3 KAGGLE — V2.0 (VÒNG 1 + VÒNG 2)

**Ngày:** 10 Sep · **Tác giả:** KAIN
**Nguồn:** `upload/107559251.json` (M1) + `upload/107573831.json` (M2) — 720 step, engine `kaggle_environments 1.32.7`, seed M1=1620414037 / M2=896878425.
**Phạm vi:** Chỉ phân tích học tập — CHƯA triển khai v7/kain41 (theo chỉ thị của user).

---

## PHẦN 0 — PHƯƠNG PHÁP: GOD REPLAY 0-LỖI (nâng cấp lớn nhất của vòng 2)

Vòng 2 xây dựng **"god replay"**: nạp lại engine thật (`kaggle_environments` local) và **bơm đúng 720 action đã ghi** vào interpreter, kèm instrument (monkey-patch `_commit_unit`, `_do_hire`, `_do_buy_land`, `_apply_unit_action`) và snapshot đầy đủ state sau mỗi step.

**Kết quả xác minh:** 719/719 step × 2 trận = **0 mismatch** trên toàn bộ money + market inventory + shops + shed + seeds của CẢ HAI người chơi, final money khớp rewards ĐẾN TỪNG ĐÔ-LA ($93,281/$99,793 và $107,329/$109,084). Mọi con số trong V2.0 là **SỐ THẬT CHÍNH XÁC** — bỏ mức sai số ±20% của vòng 1.

Tool: `tool-results/r2_godreplay.py` (engine harness) → `r2_god_M1/M2.json` (commit/hire/land/unit logs + 719 snapshot) → `r2_analyze.py` → `r2_report.txt`.

**Quy ước giờ đúng (sửa lỗi vòng 1):** action ở row t chạy tại engine-step t−1 → **true day=(t−1)//24, true hour=(t−1)%24**. Nhãn giờ vòng 1 bị +1 (vd "HIRE h1-2" thực chất là **h0**).

**Các số đo được (từ exact data):**
1. HIRE: **74-88% xảy ra ở true h0** (ngay sau end-of-day dump + reset fib) — vòng 1 ghi "h1-2" là nhãn lệch.
2. Giá bán: mỗi lệnh SELL chạy **từng unit một**, giá tại khoảnh khắc đó — tái dựng chính xác giá từng unit đã bán (bao gồm interleaving 2 người chơi trong cùng step).
3. Executed ≠ requested: engine drop âm thầm lệnh không hợp lệ → đo được chính xác "yêu cầu vs thực thi".

**Bảng sửa sai vòng 1 (đối chiếu god replay):**

| Con số vòng 1 (±20%) | Con số thật V2.0 |
|---|---|
| SpaTaro M1 gross CAO HƠN UMG (~$126k vs $121k) | **SAI ngược**: SpaTaro $120,293 < UMG $123,506 |
| UMG bán FERT 406u | **Requested 406u, thực thi 195u** (406 là lệnh yêu cầu) |
| UMG EGG $11.1k/228u | $13,958/**210u** @ $66.5 |
| SpaTaro M2: "3 ngỗng chết sớm" | **1 ngỗng mua d5 KHÔNG BAO GIỜ đặt ra ô** (coop bị đập d4) |
| Sữa/bò SpaTaro 1.3-1.4 vs Otter 1.0-1.1 | **Cả hai đều ~1.2-1.3/bò/ngày** — xem Q2 |
| Giờ bán "h0-2 sáng + h21-23 tối" | **true h0 + h17-h22** |

---

## PHẦN 1 — BỨC TRANH CHIẾN LƯỢC TỔNG QUÁT (giữ nguyên vòng 1, chốt giờ chính xác)

Timeline 30 ngày của vòng 1 được xác nhận toàn bộ. Bổ sung giờ CHÍNH XÁC mua đất (từ land_log):

| Sự kiện | M1 UMG | M1 SpaTaro | M2 Otter | M2 SpaTaro |
|---|---|---|---|---|
| NE ($1k) | t=89 (**d3 h16**) | t=151 (**d6 h6**) | t=121 (**d5 h0**) | t=151 (**d6 h6**) |
| SW ($2k) | t=198 (**d8 h5**) | t=198 (**d8 h5**) | t=247 (**d10 h6**) | t=198 (**d8 h5**) |

- **SpaTaro mua đất theo lịch đồng hồ cố định** (NE t=151, SW t=198 — TRÙNG TUYỆT ĐỐI ở cả 2 trận, khác seed!) → agent của anh ấy chạy schedule determinist, không phải canh vốn.
- M1: **cả 2 mua SW cùng một step t=198** (d8 h5).
- 4 luật cứng của user: NE d3-6 ✓, SW d8-10 ✓, KHÔNG ai mua SE ✓ (đều dừng 75 ô), empty 0-7% ✓ — giữ nguyên phán quyết vòng 1.

---

## PHẦN 2 — SỔ CÁI CHÍNH XÁC (thay toàn bộ bảng ±20% của vòng 1)

### 2.1 Doanh thu theo kênh — EXACT (god replay, từng đô-la)

**M1 (SpaTaro thua −$6,512):**

| Kênh | SpaTaro ($93,281) | UMG ($99,793) |
|---|---|---|
| STRAWBERRY | **$57,723** (296u @ $195.0) | $48,537 (253u @ $191.8) |
| WHEAT | **$24,916** (799u @ $31.2) | $12,913 (441u @ $29.3) |
| MELON | **$15,932** (66u @ $241.4) | $14,099 (89u @ $158.4) |
| FERTILIZER | $7,636 (103u @ $74.1) | $13,968 (195u @ $71.6) |
| WOOL | $6,079 (57u) | $5,030 (50u) |
| MILK | $4,145 (87u @ $47.6) | $6,543 (133u @ $49.2) |
| CARROT | $3,862 (93u) | $5,142 (128u) |
| EGG | **$0** | **$13,958** (210u @ $66.5) |
| TOMATO | **$0** | $3,316 (52u) |
| **TỔNG GROSS** | **$120,293** | **$123,506** |

**M2 (SpaTaro thua −$1,755):**

| Kênh | SpaTaro ($107,329) | Otter ($109,084) |
|---|---|---|
| MILK | $37,623 (221u @ $170.2) | **$39,178** (231u @ $169.6) |
| STRAWBERRY | $32,101 (245u @ $131.0) | $32,700 (224u @ $146.0) |
| WHEAT | $28,140 (705u @ $39.9) | $13,559 (351u @ $38.6) |
| MELON | $17,865 (82u @ $217.9) | $12,846 (90u @ $142.7) |
| FERTILIZER | $9,706 (160u) | $16,453 (280u) |
| CARROT | $7,920 (186u) | $7,241 (133u) |
| WOOL | $5,469 (48u) | $5,381 (56u) |
| EGG | **$0** | **$14,225** (322u @ $44.2) |
| TOMATO | **$0** | $6,234 (100u) |
| **TỔNG GROSS** | **$138,824** | **$147,817** |

### 2.2 Chi phí — EXACT

| Hạng mục | SpaTaro M1 | UMG M1 | SpaTaro M2 | Otter M2 |
|---|---|---|---|---|
| Hạt giống | $7,460 | $7,290 | $7,410 | $6,500 |
| Con vật | $3,100 (4 bò+3 cừu) | $5,700 (6 bò+3 cừu+**6 ngỗng**) | $4,900 (9 bò+2 cừu+1 ngỗng*) | $8,300 (11 bò+3 cừu+**8 ngỗng**) |
| Mua wheat feed | $11,431 (365u) | $4,362 (133u) | $14,896 (389u) | $9,004 (244u) |
| Mua FERT | $1,587 | $990 | $245 | $2,081 |
| HIRE | $3,434 (272 lượt) | $5,371 (293) | $4,044 (278) | **$12,848** (289) |
| Đất | $3,000 | $3,000 | $3,000 | $3,000 |
| **TỔNG chi** | **$27,012** | $26,713 | **$34,495** | **$41,733** |

\* con ngỗng duy nhất không bao giờ được đặt ra ô (xem Phần 9-N6).

**Kiểm tra sổ cái:** 3,000 + gross − chi = final, khớp tuyệt đối cả 4 lượt ($93,281 / $99,793 / $107,329 / $109,084).

### 2.3 Điểm mới quan trọng từ sổ cái exact

- **Gross không quyết định thắng thua**: M1 gross chênh $3.2k, net chênh $6.5k; M2 gross chênh $9k, net chỉ chênh $1.75k. Otter đốt $41.7k chi phí (hire $12.8k + feed $11k) và vẫn thắng — **chi phí chuyển hóa được thành doanh thu cuối ngày**.
- **Otter hire ramp cuối game**: d15-27 thuê 12→15 hands/ngày = $609-1,596/ngày (fib bậc cao) — tổng $12.8k; hàng ngày 12-15 hands thu hoạch carrot/water dâu → trả tiền ngay trong doanh thu d24-29 ($30k+ 5 ngày cuối).

---

## PHẦN 3 — CƠ CHẾ SHOP DRAW & DRAIN MATH (bổ sung vòng 1)

Drain chính xác theo engine: mỗi shop instance hút **1u mỗi sản phẩm của nó × 6 lần/ngày** (mỗi 4 turn; shop 1-sản phẩm ×2), town center −1u/ngày mọi sản phẩm trừ FERT. **FERTILIZER và MELON không có shop nào hút** → chỉ đi xuống (R135 xác nhận tuyệt đối).

| Kênh | M1 (drain/ngày cuối) | M2 (drain/ngày cuối) | Hệ quả giá (exact) |
|---|---|---|---|
| EGG | 4 inst × 6 = **24u** + center | 1 inst = 6u | M1: $50→**$72** cả mùa (khan sâu dần); M2: $50→$42 (đủ 8 ngỗng vẫn chỉ sụt nhẹ) |
| MILK | 2 inst = 12u | 4 inst = **24u** | M1: 41u d8 dồn vào drain 12u → **$36→$11**; M2: 18-35u/ngày vào drain 24u → **$160-199 cả mùa** |
| STRAW | 6 inst = **36u** | 4 inst = 24u | M1: giá giữ $191-195; M2: sóng d21-23 dồn 223u/3 ngày → **$180→$24** |
| WHEAT | 7 inst = 42u | 4 inst = 24u | M1: $38→$21 cuối; M2: giữ $39-44 nhờ tự trồng |
| CARROT | 2-3 inst = 18u | 3 inst = **36u** (+PET_CAFE ×2) | M1: $35→$45; M2: $40→$56 (khan) |
| WOOL | **0** (không YARN_STORE) | 0 | Chỉ center −1u/ngày → bán sớm ~$106, cuối $1-5 |

**Bài học R132 giữ nguyên nhưng giờ có số exact:** cùng 1 con bò, milk ở M2 đáng gấp **3.5×** M1 ($170 vs $49 avg). SpaTaro M2 tăng đàn 4→9 bò theo shop và gần thắng — đúng hướng; M1 giữ 4 bò 0 ngỗng vào kênh chết = thua.

---

## PHẦN 4 — LAO ĐỘNG & LOGISTICS (cập nhật true-hour + hiệu suất lệnh)

### 4.1 Số lệnh thật (raw) vs lệnh hiệu quả (exact từ unit_log)

| | SpaTaro M1 | UMG M1 | SpaTaro M2 | Otter M2 |
|---|---|---|---|---|
| Lệnh raw/mùa (gồm move+pass) | ~5,724 | ~6,248 | ~5,700 | ~6,040 |
| **Lệnh hiệu quả** (thực sự đổi state) | 2,766 | 3,125 | 2,776 | 3,100 |
| Tỷ lệ lệnh đi bộ | 52% | 50% | 51% | 48% |
| WATER (lệnh #1) | 1,387 | 1,060 | 1,320 | 982 |
| HARVEST | 410 | 517 | 446 | 561 |
| FEED/CARE | 135/136 | 248/223 | 224/225 | 446/387 |
| COLLECT_FERT | 173 | 326 | 249 | 420 |
| FERTILIZE | 96 | 142 | 91 | 186 |

- **WATER là việc chiếm nhiều lao động nhất** (35-45% lệnh hiệu quả). Nhưng **số lượng nước không bằng chất lượng thời điểm**: SpaTaro tưới 1,387 lần → wheat 3.41u/ô; UMG 1,060 lần → 4.57u/ô; Otter 982 lần → **5.32u/ô** (tưới đúng cửa sổ tuổi 2-4 của wheat + đúng event-day của dâu).
- **R133 (end-of-day dump) định lượng**: DROP chủ động chỉ 68-133 lần so với 410-615 HARVEST → **~70-85% sản lượng dựa vào auto-dump h23**, units đi khắp farm không cần về kho. Xác nhận vòng 1.
- **Otter bỏ trống h0-h1 mỗi ngày** (0 lệnh unit) nhưng vẫn chạy market h0 (54 lệnh SELL d29) — pattern "sáng chỉ bán, chiều mới làm".

### 4.2 Phản ứng đàn (giữ vòng 1) + số exact về nhịp nuôi

Xem Q2 bên dưới — vòng 1 đoán "2 phong cách cho sữa khác nhau" là **SAI**: cả 4 lượt đều đạt milk/prod-event 2.35-2.55 (care bonus được max gần như mọi event).

---

## PHẦN 5 — THANH LÝ CUỐI GAME = TRẬN CHUNG KẾT (nâng cấp từ vòng 1 + Q1)

### 5.1 Dòng tiền cuối mùa — SPA TARO DẪN TRƯỚC NGÀY CUỐI CẢ 2 TRẬN RỒI THUA

| Cuối ngày | M1: SpaTaro vs UMG | M2: SpaTaro vs Otter |
|---|---|---|
| d27 | $83,911 vs $82,810 (**dẫn +$1,101**) | $97,263 vs $92,619 (**dẫn +$4,644**) |
| d28 | $89,451 vs $88,593 (**dẫn +$858**) | $103,054 vs $99,459 (**dẫn +$3,595**) |
| **d29** | $93,281 vs $99,793 (**thua −$6,512**) | $107,329 vs $109,084 (**thua −$1,755**) |

**Cả 2 trận đều lật kết quả NGAY TRONG NGÀY CUỐI.** Doanh thu theo ngày (exact):

| | d28 | d29 |
|---|---|---|
| SpaTaro M1 | $5,670 | $3,998 |
| UMG M1 | $6,349 | **$11,576** |
| SpaTaro M2 | $6,069 | $4,363 |
| Otter M2 | $7,389 | **$10,001** |

### 5.2 Cơ chế thắng ngày cuối (từ commit log từng unit)

1. **Danh mục đứng cuối mùa**: người thắng đứng ngoài dâu (đã chết tuổi) bằng **carrot (bán d27-29: UMG $4,074; Otter $7,121) + tomato (Otter $1,111) + máy egg/milk chạy đều mỗi ngày**. SpaTaro chỉ còn wheat tồn ($6,855 M2).
2. **Nhịp bán d29**: bán từ h0 (shed qua đêm: Otter 54 lệnh) → thu hoạch+rải suốt ngày → **dump lớn giờ chót: Otter h22 = 91u trong 6 lệnh** (`SELL CARROT 42, WHEAT 25, MILK 6, EGG 10, FERT 6, TOMATO 2` — đúng hàng đợi cuối trận). SpaTaro h22 M2: **market RỖNG** — hết hàng để bán.
3. **Ngưỡng giá thanh lý = KHÔNG NGƯỠNG**: bán xuống tới **$1 (wool)**, $21-34 (wheat), $22-49 (FERT), $26-41 (sữa chết M1). Nguyên tắc: **bán 100% tồn, mọi giá** — nhưng sắp thứ tự kênh lớn trước, giờ chót ép nốt.
4. **Cấu trúc kỹ thuật d29 (phát hiện engine mới — xem R146)**: step 719 không bao giờ chạy → **không có end-of-day dump ngày 29** — tất cả tồn trên tay unit lúc h22 = mất trắng. SpaTaro M2 để lộ 1 ngỗng trên tay; cả 2 bên còn lại gần 0.

### 5.3 Vết nứt của SpaTaro (nguyên nhân thật)

- **M1: 16 wool tồn shed** (~$100) — anh ta chỉ REQUEST 59u bán cả mùa trong khi có 73u (under-request).
- **M2: 25 lệnh BUY_PRODUCT vô hiệu trong 3 ngày cuối (319u rác)** — engine drop im lặng vì chỉ WHEAT/FERT mua được; các lệnh này **chiếm slot hàng đợi 10 lệnh/giờ** đúng lúc cần bán. Cả mùa: ~2,000-2,600u lệnh BUY rác (CARROT/EGG/MELON/MILK/STRAW/TOMATO/WOOL).
- Tồn cuối sạch: 16 wool (M1) / 1 FERT + 1 ngỗng trên tay (M2) — người thắng: ~0.

---

## PHẦN 6 — ĐỐI CHIẾU RULES.md (cập nhật exact + quy tắc mới R139-R146)

### 6.1 Bảng xác nhận (cập nhật bằng chứng vòng 2)

Giữ nguyên 12 quy tắc đã xác nhận ở vòng 1 (R8/R10/R24/R36/R37/R49/R83/R90/R92/R101/R53/E8/R5) — tất cả được tái khẳng định bằng số exact. Lưu ý **R36 còn lớn hơn tưởng tượng**: SpaTaro (top-3) spam ~250-350 lệnh BUY_PRODUCT rác mỗi mùa, trong đó 25 lệnh rơi đúng 3 ngày cuối M2.

### 6.2 Bảng mâu thuẫn vòng 1 — giờ có số exact

| Quy tắc | Phán quyết vòng 2 |
|---|---|
| R74 (50 ô tối ưu) | Giữ phán quyết vòng 1: 75 ô + fill 98-100% là meta top-3 |
| R127 (trần 85% fill) | Định lượng thêm: top-3 chạy 2,700-3,100 lệnh hiệu quả/mùa (~90-105/ngày) vs engine ta 52-67 — chênh 1.5-2×, không phải 4-5× như ước lượng thô vòng 1 (vòng 1 đếm cả move) |
| R75/R114 (wheat) | Exact: SpaTaro bán thô 799/705u wheat; người thắng chuyển hóa 259/446u thành milk+egg+fert. Wheat→sữa ở M2 = **5.2× ROI** ($40 wheat → 1.23 sữa × $170) |
| R100 (SE option) | Giữ: 0/4 mua SE |
| R86/R132 | Củng cố: cùng đàn bò, giá sữa M2 = 3.5× M1 — shop draw là biến số #1 |

### 6.3 Quy tắc mới vòng 2 (R139-R146)

**R139 [E] — NGÀY 29 LÀ TRẬN TRONG TRẬN, ĐÃ ĐO BẰNG CHỨNG**: cả 2 trận top-3 đều lật kết quả trong ngày cuối (+$6.5k và +$5.3k swing). Công thức người thắng: danh mục đứng cuối mùa (carrot+tomato d24-29 + máy egg/milk) + nhịp h0-rải-đến-h22 + bán không ngưỡng. Ngày cuối = 9-11% tổng tiền.

**R140 [E]— ORDER SLOT LÀ TÀI SẢN HIẾM**: 10 lệnh/giờ; lệnh BUY_PRODUCT ngoài WHEAT/FERT = drop im lặng NHƯNG VẪN CHIẾM SLOT. 25 slot rác ngày cuối M2 = CONTRIBUTING trực tiếp vào thất bại. Không bao giờ submit lệnh không thực thi được.

**R141 [E] — WHEAT-FEED MACHINE 5× ROI (exact)**: 1 wheat ($40 M2) → 1 bò ăn 1 wheat/ngày → 1.23 sữa/ngày × $170 = $209/ngày. Ngay cả kênh sữa chết M1 vẫn 1.9× ($31→$59). Máy wheat 17-29 ô + mua thêm 133-389u = lõi kinh tế đàn. (Công thức: thu hoạch + mua − bán = lượng thật ăn: 135/259/224/446u theo thứ tự 4 lượt.)

**R142 [E] — VỰC CẮT TUỔI DÂU d21-23 LÀ CƠ CẤU, KHÔNG PHẢI LỖI**: dâu 4 events (d+10/12/14/16) → chết tuổi ~d21-22 → toàn bộ yield tồn + zombie decay buộc bán trong 2-3 ngày. M2: 2 bên dồn 223u trong d20-22 vào drain 24u/ngày → $180→$24 (self-crash cấu trúc). Phòng thủ duy nhất: bán TRƯỚC vách (d18-20 ở $187-199) hoặc bớt wave-3 replant khi drain mỏng.

**R143 [E] — CARE BONUS RẺ NHƯ MIỄN PHÍ, AI CŨNG MAX**: care+feed cùng ngày → +1 unit ở event kế tiếp. Cả 4 lượt đều đạt 2.35-2.55 milk/event (max lý thuyết 3) và 1.72-1.85 egg/ngỗng/ngày (max 2). Không có "phong cách feed" nào thua vì sữa — cái phân định là QUY MÔ ĐÀN.

**R144 [E] — MELON: AI DUMP SỚM HƠN THẮNG CỬA SỔ** (kênh 0-drain): SpaTaro thắng cả 2 cửa sổ melon (66u@$241 M1, 82u@$218 M2) — đó là lý do anh ta dẫn giữa game; UMG/Otter bán muộn hơn (89u@$158, 90u@$143). Trong kênh không drain, mỗi ngày chậm = −$50-80/quả.

**R145 [E] — NGỖNG LÀ TÀI SẢN ROI CAO NHẤT GAME**: $300/con → 1.72-1.85 egg/ngày ($66.5 M1) + 2.4-2.7 FERT/ngày (unconditional — kể cả ngày không feed, chỉ cần không bỏ đói 2 ngày liên tiếp) = **$82-114 doanh thu/ngỗng-ngày**. Hoà vốn 3-5 ngày. Ceiling 6-8 con không phải giới hạn máy (max_held 4 chỉ đạt 2-6 ô-ngày) — là lựa chọn theo giá egg của shop draw. Mua d0-5, đặt NGAY (SpaTaro M2 mua d5 không đặt = mất $300 + cả kênh $14k).

**R146 [E] — CƠ CHẾ NGÀY 29 (engine)**: step 719 không chạy → (a) **không có shed-dump cuối d29** — tồn trên tay unit h22 = mất trắng; (b) ngày 30 không tồn tại; (c) sản xuất "cho d29" được credit từ cuối d28 (con vật/cây vẫn nhả cho d29, thu được sáng d29); (d) **bán $1 KHÔNG thêm supply** (floor sale không ô nhiễm giá thị trường — engine). E8 của ta phải bán xong trước h22 d29 và không trông chờ dump.

---

## PHẦN 7 — TRẢ LỜI 5 CÂU HỎI MỞ CỦA VÒNG 1 (Q1-Q5)

**Q1 — DP thanh lý của họ có ngưỡng thế nào?**
Không có ngưỡng giá — bán tới $1 (wool), $21 (wheat), $22 (FERT). Ngưỡng thật là **LOGISTIQUE**: có hàng để bán (danh mục d24-29) + đủ slot lệnh (không rác) + bán đến tận h22. UMG/Otter d29 = $10-11.6k; SpaTaro = $4.0-4.4k vì (i) thiếu kênh đứng cuối (egg/tomato/carrot ít), (ii) 9-25 slot bị lệnh BUY rác chiếm, (iii) h22 market rỗng.

**Q2 — Producer-feeding vs full-care, đâu tối ưu?**
Câu hỏi sai bấm. **Milk/cow/ngày ~1.18-1.28 ở CẢ 4 lượt** (2.35-2.55/event) — care bonus ai cũng max gần hết. Khác biệt thật: **quy mô đàn + kênh** (Otter 11 bò vào milk $170 = $39k; SpaTaro M1 4 bò vào milk $49 = $4.1k). Wheat qua bò = 5.2× ở M2 / 1.9× ngay cả M1. Kết luận cho v7: luôn feed+cared các con đang product-cycle (rẻ), quyết định ĐÀN theo shop draw.

**Q3 — Chu kỳ wheat: trồng lại bao nhiêu để giữ standing?**
Chu kỳ ~5 ngày (trồng → tưới tuổi 2-4 (+1/lần, ×2 nếu fert) → thu 3.4-5.3u/ô). Giữ standing 17-29 ô cần **4-8 lần trồng/ngày** (đo được: SpaTaro 8.0-8.2, UMG 5.6, Otter 3.9-11.9). Năng suất/ô phụ thuộc CHẤT LƯỢNG tưới cửa sổ: Otter 5.32u (tưới đủ 3 ngày cửa sổ) vs SpaTaro 3.41u.

**Q4 — 6-8 ngỗng có phải ceiling?**
Không. Máy cho phép nhiều hơn (cap trứng 4/ô hầu như không chạm: chỉ 2-6 ô-ngày ở cap). Giới hạn thật = **giá egg theo shop draw** (M1 4 inst → $66.5-72 lên đều cả mùa; M2 1 inst → $42) + thức ăn + slot COOP. 8 ngỗng của Otter ở $44 egg vẫn lãi (egg $14.2k + share FERT).

**Q5 — Zero-sum ở top tồn tại không?**
**Cục bộ có, toàn cục không.** Kênh: ai dồn thêm 1u vào kênh bão hòa làm giá tụt cho CẢ HAI (straw M2 d20-24; milk M1 d8). Nhưng tổng nền kinh tế M2 = $216.4k > M1 = $193.1k (+12%) vì cả hai cùng bơm vào các kênh có drain lớn (milk 24u/ngày) → **pie lớn hơn cho cả hai**. Ở top, "chơi tốt hơn" = "chọn kênh drain lớn + không tự sát kênh chung", không phải cướp phần của đối thủ.

---

## PHẦN 8 — CÁC PHÁT HIỆN MỚI VÒNG 2 (ngoài Q1-Q5)

**N1 — Nhịp giờ chuẩn (true hours):** h0 = dump shed qua đêm + HIRE (74-88%) + mua hạt; h2-h17 = lao động chính (water/harvest/plant/feed); h17-22 = sóng bán lớn (Otter h22 d29: 91u). Đỉnh MOVE ~h3-5 (đi ra nông trại sau hiring).

**N2 — Cấu trúc dòng tiền theo giai đoạn (money curve):**
- d0-8: bootstrap FERT — UMG/Otter bán $5.1-5.7k FERT d0-9 (vs SpaTaro $3.6k) → dẫn sớm $0.5-3.6k.
- d9-13: SpaTaro bật melon bomb $13-16k → dẫn $10-14k (M1) / $4-9k (M2).
- d14-28: người thắng gỡ chậm bằng annuity (egg $400-1,200/ngày + milk $1-4.6k/ngày + FERT) — cần 10-14 ngày để bắt kịp.
- d29: lật kèo (xem Phần 5).

**N3 — Mua hạt JIT theo lô nhỏ**, không tồn kho lớn (seeds mua 15-66u/lần theo đợt, khớp đợt trồng). Seed tồn cuối: ~0 (mua vừa đủ).

**N4 — Vi cấu trúc lệnh bán**: 60-70% lệnh SELL cỡ 2-6u; tranche lớn (16-49u) chỉ cho wheat (T=400 sâu). Suy giảm giá trong 1 lệnh: $0.30-0.58/unit — tách lệnh không quan trọng bằng CHỌN GIỜ (bán sau đợt drain/shop). Winners dùng đủ 10 slot ở 26-33 bước (đặc biệt d29).

**N5 — Phân phối FERT (exact)**: UMG thu 326 → 142 bón (44%) + 195 bán; Otter 420 → 186 bón (44%) + 280 bán; mua thêm 17-50u khi cần bón dâu đúng event. Tỷ lệ bón/sell ~44/56 ổn định cả 2 người thắng.

**N6 — Autopsy SpaTaro (5 vết nứt, đủ giải thích 2 khoản thua):**
1. M1: không mua ngỗng dù 4 egg-shop (R132 fail) — mất $14k kênh.
2. M2: 1 ngỗng mua d5 không đặt (coop đập d4) — mất $300 + $14k kênh.
3. BUY_PRODUCT rác ~250-350 lệnh/mùa (319u rác d27-29 M2) — chiếm slot thanh lý.
4. Wheat-seller thay vì wheat-converter (bán 705-799u thô; người thắng ăn 446u vào đàn).
5. Không bao giờ trồng tomato ($3.3-6.2k bỏ lại cả 2 trận).
Bù lại: melon timing tốt nhất cả 2 trận + wheat machine lớn → đủ để dẫn đến d28. Thua ở đích, không phải ở giữa chặng.

**N7 — Kỷ luật tưới (chất lượng > số lượng)**: UMG/Otter tưới ÍT hơn SpaTaro nhưng đúng cửa sổ tuổi → wheat 4.6-5.3u/ô vs 3.4. Với cây ongoing (dâu/tomato): nước chỉ tính vào ngày event (fert bonus cần watered) — tưới ngày thường phần lớn là lãng phí.

**N8 — Xác nhận R133 (end-of-day dump)**: DROP chủ động 68-133 lần vs 410-615 HARVEST — đại đa số harvest để trên tay chờ auto-dump h23. Đây là nguồn gốc hiệu suất lao động 2× của top-3 (không về kho giữa ngày).

**N9 — Cả top-3 vẫn để tử vong tồn tại**: 16 wool + 1 ngỗng + ~$300-1k nhỏ lẻ ở 2 người — vì bot của họ cũng có bug (order rác, under-request). Khoảng cách top-3 với phần còn lại = kỷ luật nhỏ nhân với 720 step.

---

## PHẦN 9 — HÀM Ý CHO v7 (cập nhật bằng số exact, CHƯA triển khai theo chỉ thị)

1. **Ngày cuối là một module riêng** (R139): danh mục carrot 10-15 ô + tomato 5-8 ô đứng từ d24; máy egg/milk full; nhịp bán h0→h22; DP = 0 (bán mọi giá, kênh lớn trước); tối ưu slot (R140).
2. **Đàn theo shop draw (R132/R145)**: d0 mua 2-5 con (bootstrap FERT $300-600/ngày); đọc shop d3-d12: ≥3 egg-inst → 6-8 ngỗng; ≥3 milk-inst → 9-11 bò; luôn feed+cared chu kỳ sản xuất (R143). Wheat-feed 5× ROI (R141).
3. **Wheat machine 17-29 ô**: tưới CHÍNH XÁC cửa sổ tuổi 2-4 (5.3u/ô), replant 4-8 ô/ngày, mua thêm khi giá <$45 và đàn cần.
4. **Dâu theo drain-corrected quota** (R142): số ô wave-2/3 ∝ drain của shop draw (36u/ngày → 35-40 ô ok; 24u/ngày → max ~25 ô + bán sớm trước vách d21).
5. **FERT 44/56**: bón event-day của dâu/tomato, bán phần thừa theo tranche 2-6u (N4/N5).
6. **Melon d0-5 → dọn SỚM d10-12** (R144) — không giữ melon quá d15.
7. **Thang điểm chuẩn giữ nguyên vòng 1**: $93-109k/lượt; kernel lao động: 90-105 lệnh hiệu quả/ngày (đếm như top-3, không tính move).

---

## PHẦN 10 — PHÁN QUYẾT: CÓ CẦN VÒNG PHÂN TÍCH 3?

**Kết luận: KHÔNG cần thêm vòng phân tích thụ động (đọc lại replay). Lý do:**

1. **Nguồn đã kiệt**: mọi con số có thể đo từ 2 file replay nay là CHÍNH XÁC (god replay 0-mismatch) — doanh thu từng unit, giá từng lệnh, nước/tưới/fert từng action, vị trí từng unit từng giờ. Một vòng đọc thứ 3 sẽ không tạo thông tin mới đáng kể.
2. **5 câu hỏi mở vòng 1 đã trả lời hết** (Phần 7); các quy tắc mới R139-R146 đã đủ để thiết kế v7 mà không còn chỗ mơ hồ lớn.
3. **Các chi tiết chưa khai thác** (pathing từng bước chân, phân bố khoảng cách shed, weeds RNG) chỉ có ý nghĩa khi THIẾT KẾ kernel v7 cụ thể — lúc đó lấy từ `r2_god_*.json` (đã lưu, tái dùng được).

**NHƯNG nên mở 1 loại vòng mới khi bắt đầu v7 — "VÒNG PHẢN CẢNH (counterfactual)" bằng chính harness god replay:**
- Thay action của 1 người chơi rồi chạy lại engine thật để đo: "SpaTaro + 6 ngỗng ở M1 thắng bao nhiêu?", "bán dâu sớm hơn 2 ngày ở M2 thì giá nào?", "10 ngỗng có sập giá egg?". Đây là thí nghiệm nhân-quả, không phải đọc lại — chỉ làm khi có câu hỏi thiết kế cụ thể của kain41/v7.
- Harness `r2_godreplay.py` đã sẵn sàng làm việc này (bơm action sửa đổi + validate).

**Khuyến nghị cho user: chuyển sang triển khai v7 (kain41) dựa trên V2.0 này; chạy vòng phản cảnh chỉ khi v7 cần quyết định mà số liệu thụ động không trả lời được.**

---
*KAIN — TOP3_REPLAY_ANALYSIS.md v2.0 (Task 39, vòng phân tích 2). Nguồn: god replay 0-mismatch trên 107559251.json + 107573831.json (engine 1.32.7, seed 1620414037/896878425). Tool: tool-results/r2_godreplay.py + r2_analyze.py + r2_god_M1/M2.json + r2_report.txt. Mọi số liệu là EXACT (không còn ±20% của vòng 1). Chưa triển khai v7/kain41 theo chỉ thị.*
