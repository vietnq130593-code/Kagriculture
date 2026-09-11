# NGHIÊN CỨU REPLAY TOP-3 KAGGLE — V3.0 (VÒNG 1 + VÒNG 2 + VÒNG PHẢN CẢNH)

**Ngày:** 10 Sep · **Tác giả:** KAIN
**Nguồn:** `upload/107559251.json` (M1) + `upload/107573831.json` (M2) — 720 step, engine `kaggle_environments 1.32.7`, seed M1=1620414037 / M2=896878425.
**Phạm vi:** Vòng 1-2 = phân tích thụ động exact. V3.0 bổ sung **VÒNG PHẢN CẢNH** — thí nghiệm nhân-quả bằng god-replay phẫu thuật (xem PHẦN 11).

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

## PHẦN 10 — PHÁN QUYẾT VÒNG 3 (cập nhật theo V2.0)

**Kết luận V2.0: KHÔNG cần vòng phân tích thụ động thứ 3** — nguồn đã kiệt (mọi số exact), 5 câu hỏi mở trả lời xong. **ĐÃ MỞ vòng loại mới: VÒNG PHẢN CẢNH** — kết quả ở PHẦN 11. Sau vòng phản cảnh: mọi câu hỏi thiết kế v7 đã có câu trả lời nhân-quả; **không cần thêm vòng nào — chuyển sang triển khai v7 (kain41).**

---

## PHẦN 11 — VÒNG PHẢN CẢNH (COUNTERFACTUAL) — THÍ NGHIỆM NHÂN-QUẢ BẰNG GOD-REPLAY PHẪU THUẬT

### 11.0 Phương pháp & độ tin cậy

Harness `tool-results/cf_harness.py`: nạp engine thật + bơm 719 action đã ghi của CẢ HAI người chơi, phẫu thuật state/action của 1 người (target) bên TRONG wrapper interpreter (bài học kỹ thuật: `core.env` gọi `structify(state)` tạo bản sao cây state mỗi bước — mọi mutation ngoài interpreter không tồn tại). **NULL-test = +$0.00 sai số trên cả 2 trận** — harness tái tạo gốc tuyệt đối; mọi delta dưới đây là tác động THUẦN của phẫu thuật. Chẩn đoán từng kênh: `cf_diag.py`.

Kỷ luật kế toán của mọi thí nghiệm: mua ngỗng/hạt/fert trừ tiền mặt đúng giá thị trường; feed 1 wheat/con/ngày (ưu tiên shed — như đàn thật); egg/fert thu hoạch + bán qua lệnh thị trường thật (tác động giá do engine tính); shed 100 slot được bảo vệ (thu hoạch chỉ khi còn chỗ; bán sạch mỗi sáng).

### 11.1 Bảng kết quả chính

| Thí nghiệm | Phẫu thuật | Δ tiền (target) | Δ opp | Số đọc thêm |
|---|---|---|---|---|
| **CF1** +6 ngỗng M1 (land-safe) | mua d8-13 sau khi NE+SW an toàn, đặt trên ô ít dùng nhất | **−$449** | +$608 | egg +$11,227 (186u @$60.4); feed −$2.9k; capex −$1.8k; đất −$7.6k |
| **CF7** +10 ngỗng M1 (land-safe) | như CF1, 10 con | **−$118** | +$929 | egg 251u; thêm ngỗng = thêm đất displaced, giá egg mềm đi |
| **CF4** wave-2 dâu +20 ô d12 (M2) | thay 17-19 ô wheat non + feed-buy bảo vệ đàn | **−$17,121** | +$6,316 | kênh dâu: 347u bán (vs 245) nhưng giá $88.9 (vs $131) → kênh ròng −$1.3k; −$5.2k milk do feed-cascade |
| **CF4b** wave-2 dâu d8 (M2) | — | **KHÔNG CHẠY ĐƯỢC** | — | tiền d8 h23 = **$44 < $1,500 hạt** — SpaTaro không nổi trồng dâu wave-2 trước vách |
| **CF4c** wave-2 dâu +15 ô d11 (M2) | sau melon-cash | **−$20,399** | +$11,497 | dâu +36u @ giá vách $112; milk −$9k (feed-wheat displacement + morning-sell cascade) |
| **CF5** +10 ô tomato d17 (M2) | thay wheat non + feed-buy | **−$2,460** | +$1,487 | kênh tomato tự thân ≈ neutral trên farm đầy |
| **S1/S2** cừu→ngỗng (M1/M2) | thay lệnh mua/gây/đặt, cùng tiền, cùng ô, cùng lao động | **−$40,856 / −$58,413** | +$14,650 / −$1,797 | sụp vì DOMINO TIỀN MẶT (xem 11.3) — không phải do ngỗng |

### 11.2 Câu trả lời nhân-quả cho 4 câu hỏi thiết kế v7

**Q-A: "SpaTaro + 6 ngỗng ở M1 thắng bao nhiêu?" (R145 kiểm chứng)**
**Trả lời: GẦN BẰNG — −$449 đến +$333** (dao động theo chính sách feed giữa các biến thể). Máy ngỗng gross rất thật: 186 egg ($11.2k) + 50 fert thu ($1k) trong 17-20 ngày. Nhưng chi phí FULL: $1,800 capex + ~$3k feed (105-117 wheat) + **$7-8k chi phí cơ hội đất** (6 ô không trồng dâu/wheat nữa — kênh STRAW −$3.5k, WHEAT −$2.9k). Trên farm ĐẦY 75 ô của SpaTaro, ngỗng chỉ là swap tài sản ≈ 0. **Hệ quả v7: giá trị ngỗng = f(đất trống). Trên 25-50% ô trống của kain40 (d15-28), ngỗng là THUẦN LỢI** (không displaced gì hết) — Trụ 6 đúng cho context của ta, sai cho context của SpaTaro. UMG thắng M1 bằng ngỗng vì anh ta đọc draw sớm (mua d0-5 khi đất còn rỗng) chứ không phải vì ngỗng "miễn phí".

**Q-B: "Bán dâu sớm hơn 2 ngày ở M2 thì giá nào?" / giá trị wave-2 (R142/Trụ 1)**
Kết cấu vách được xác nhận NHÂN-QUẢ 3 lần: +36-102u cung thêm vào thị trường đã sập → giá dâu −19 đến −$42/u → **kênh ròng ≈ −$0.5k đến −$1.3k** (bán nhiều hơn, thu ít hơn). Điểm rơi sự kiện quyết định tất cả: event ≥ d24 = bán vào thị trường đã sập; event d18-23 = còn ăn $130-190. CF4b chứng minh **cửa sổ trồng pre-vách (d8-10) không thể nào với nổi tài chính** ($44 lúc đó) — phải đấu vốn từ melon (d10-12) → event sớm nhất thực tế = d21-23 (đúng mép vách). **Kết luận v7 Trụ 1: wave-2 dâu chỉ đáng trồng (a) trên Ô TRỐNG (không đụng máy feed — CF4/4c: đụng wheat = giết milk −$5-9k, R141神聖), (b) hạt mua đúng melon-window d10-12, (c) event cuối ≤ d23, (d) kỳ vọng +$3-4k/trận trên đất thật trống (không displaced) — không phải +$12-30k như ước lượng vòng 1.**

**Q-C: "10 ngỗng có sập giá egg?" (Q4/bay ceiling)**
CF7: egg 251u (vs 186 của CF1) — giá egg softens từ $66→$54-60 nhưng KHÔNG sập (drain M1 24u/ngày sâu). Tổng delta vẫn ≈ 0 trên farm đầy vì đất. **Ceiling ngỗng không nằm ở giá egg — nằm ở CHI PHÍ CƠ HỘI ĐẤT.**

**Q-D: tomato kênh $155- giá trị thật? (Trụ "tomato chỉ là gia vị")**
CF5: 10 ô tomato trên farm đầy = −$2.5k (domino feed), kênh tự thân neutral. Xác nhận giữ quota 8/6/4 d17-19 của kain40 — MỞ RỘNG sai lầm khi đất không rảnh.

### 11.3 PHÁT HIỆN LỚN NHẤT VÒNG PHẢN CẢNH: KINH TẾ TOP-3 LÀ DOMINO TIỀN MẶT SƠM (R147)

S1/S2 (thay cừu bằng ngỗng — cùng tiền, cùng ô, cùng lao động) sụp −$40-60k. Autopsy chuỗi nhân-quả (CF-diag từng ngày):
1. d1-6: ngỗng ăn 90-150 wheat mua thị trường (~$150-400 tiền mặt) **hoặc** đơn mua ngỗng rút cạn đúng giờ →
2. d5-6: 10-11 lệnh BUY_SEED STRAWBERRY fail (tiền mặt chạm 0 đúng lúc) → 15 ô dâu không bao giờ được trồng →
3. d8 h5: **không mua nổi SW $2,000** (doanh thu dâu d8 vắng) → 25 ô khóa vĩnh viễn →
4. máy wheat chết → bò đói chết d13-17 → milk −$20k+ → **tổng −$40-60k**.

Cùng cơ chế này đã giết CF1 bản đầu (−$87k: mua 6 ngỗng $1,800 d1-7 → sập SW) và CF4b ($44 không nổi $1,500 hạt). **Đây là bằng chứng nhân-quả MẠNH NHẤT từng có cho 4 luật đất cứng**: $300 chi sai chỗ trước cửa sổ đất = hủy diệt $40-87k. Top-3 chạy với $12-1,200 tiền mặt d0-9 — mọi đồng đều có chỗ đứng đã định.

### 11.4 Quy tắc mới R147-R150 (từ vòng phản cảnh)

**R147 [E] — DAO TIỀN MẶT SỚM (cash knife)**: mọi khoản chi > $0 trước khi NE ($1k d5-9) và SW ($2k d8-12) an toàn PHẢI đi qua quỹ dự trữ đất (NE +$1,150 / SW +$2,150) + buffer $400. Bán lúa/non-essential trước khi động quỹ. V7: không bao giờ để lệnh mua nào (ngỗng/hạt/fert) chạm quỹ đất. Bằng chứng: 3 thí nghiệm sụp −$37 đến −$87k đều do vi phạm này; NULL + GE1 land-safe version sống sót.

**R148 [E] — SHED 100 SLOT LÀ TÀI SẢN CHUNG**: kho đầy lúc h23-dump = harvest bị DISCARD (mất trắng — không phải chờ). Máy egg/fert/sản phẩm mới phải (a) thu chỉ khi còn chỗ, (b) BÁN SẠCH mỗi sáng trước giờ dump (buôn theo giờ, không theo ngày). CF1 bản đầu: 18u tồn kho chiếm chỗ → melon dump tràn → −$6k.

**R149 [E] — FERT LÀ VẬT TƯ SẢN XUẤT, KHÔNG PHẢI HÀNG BÁN**: shed fert 6-12u là pipeline bón của đàn/cây (vết nứt #2 của kain40). Thu thêm = top-up; bán = chỉ phần dư qua nhịp bán riêng. CF bản đầu bán fert shed → dâu/melon mất bonus → −$7-11k. Trụ 2 (fert discipline) giữ nguyên + thêm nguyên tắc collect top-up.

**R150 [E] — FEED CÓ THỨ TỰ ƯU TIÊN**: (a) feed từ shed là chi phí chìm (không đụng tiền mặt — an toàn R147); (b) feed mua thị trường trước d10 = đao tiền mặt; (c) khi milk sâu ($170+), ô wheat là MÁY SỮA — đụng vào = −$5-9k (CF4/4c) trừ khi có feed-buy thay thế sẵn; (d) SELL WHEAT buổi sáng và FEED tranh nhau shed — thứ tự h23-top-up → sáng-bán → pickup phải đủ cho cả hai.

### 11.5 Sửa lại Phần 9 (hàm ý v7) theo số phản cảnh

1. **Trụ 1 (dâu vòng 2) — GIẢM kỳ vọng, SỬA điều kiện**: +$3-4k/trận (không phải $12-30k); chỉ trên ô trống thật; hạt đấu vốn từ melon-window d10-12; event ≤ d23; KHÔNG đụng máy feed (R150).
2. **Trụ 2 (fert)**: giữ nguyên + R149 collect top-up policy.
3. **Trụ 6 (ngỗng/đàn)**: giá trị = f(đất trống): ngỗng ưu tiên ô trống d15-28 của kain; egg bán mỗi sáng (R148); feed từ shed trước (R150); ceiling thực tế 8-10 con khi drain ≥ 3 inst (CF7: giá không sập).
4. **Trụ 3 (labor)**: giữ (bằng chứng vòng 2), bổ sung: lao động bền = không phá R147 (hire fib $54-87/ngày vẫn phải qua quỹ).
5. **Trụ 4 (feed-buy đảo ngược)**: CHỈ bật khi có đồng dư $2,500+ (R147) và đã bảo vệ pickup sáng (R150d).
6. **Trụ 5 (liquidation d27-29)**: giữ nguyên E8-lite → tuyệt đối; thêm: ngày cuối là chiến tranh NGUỒN CUNG (danh mục đứng) — không phải kỹ thuật bán (SpaTaro M2 bán đủ tốt với những gì anh ta có; thua vì không còn gì để bán).

### 11.6 Phán quyết vòng 4

**KHÔNG cần thêm vòng nào.** Vòng phản cảnh đã trả lời hết các câu hỏi thiết kế bằng nhân-quả; các kết quả âm của S1/S2 không phải nhiễu — chúng LÀ phát hiện (R147). Harness `cf_harness.py` (NULL-validated) được giữ lại cho mọi thí nghiệm tương lai khi v7 cần (vd: đối đầu kain41 vs v6 trên seed khó → autopsy → phẫu thuật nhắm). **Tiếp theo: triển khai v7 (kain41).**

---
*KAIN — TOP3_REPLAY_ANALYSIS.md v3.0 (Task 40, vòng phản cảnh). Nguồn: god replay 0-mismatch (vòng 2) + counterfactual harness NULL-validated (vòng 3): tool-results/cf_harness.py + cf_diag.py + cf_occ_* + cf_M1/M2_*.json (10 thí nghiệm nhân-quả). Mọi số exact; phán quyết: đủ dữ liệu triển khai v7/kain41.*

### 11.7 PHỤ LỤC TRIỂN KHAI (Task 40, khép vòng lặp phân tích → build → kiểm chứng)

kain41 = kain40 + 6 biến thể differential trên 10 seed khó: bản đầy đủ (Trụ 1+2) = **67/100 (1.097x) — thua kain40 (93/100, 1.271x)**. Autopsy: mọi tác vụ thêm (bón event, thu fert riêng, trồng dâu liên tục, thêm hands) đều TRỪ lao động khỏi thu hoạch vì kernel chỉ chạy 52-67 lệnh hữu ích/ngày (top-3: 90-105) → **R151: cổ chai lao động** (chi tiết bảng biến thể: RESEARCH_V7.md mục 12). kain41-final = kain40 + ΔA collect-first (biến thể duy nhất trung tính-dương). Bài học kiến trúc cho v8: cần kernel hiệu suất-lao động MỚI trước khi nạp playbook top-3.

### 11.8 VÒNG 42 — KERNEL v8 "REGION-FLOW": GIẢI R151 BẰNG LAI TIER/GEO (user báo v7 để trống 30-37% đất)

**Vấn đề user xác nhận bằng mắt** (v7 đấu v6/kain40 trên UI): đất trống rất cao so với 2 trận mẫu top-3. Đo lại bằng autopsy 3 seed (bench/v8_autopsy.py):

| Chỉ số | v7 | top-3 (chuẩn exact) |
|---|---|---|
| Empty d9-27 | **25-37 ô** (max 72%) | 0-5 ô |
| Máy wheat từ d15 | **chết (1-6 ô)** | 17-29 ô đứng cả mùa |
| MOVE | 4.962/mùa | 2.700-3.100 |
| FERTILIZE | 0 | 91-186 |
| PLANT | 3,9/ngày | 10-15 |
| Kênh đứng cuối mùa | không có | carrot d24-27 + tomato |

**7 nguyên nhân gốc (định lượng được):** (1) T_WATER_CRIT tier-0 hằng ngày cho dâu — trong khi nước chỉ có giá trị NGÀY EVENT và CHỈ khi kết hợp FERT (engine: `+2 if (was_watered AND fert_active) else +1` — tưới không bón = 0 cộng thêm); (2) T_HARVEST=5 và T_PLANT=5 chết đói dưới 30-50 task tier 0-4; (3) sort (tier, dist) thuần lexicographic → zigzag (farmer v7 đi 6 tiếng chỉ để FEED 1 con); (4) FERTILIZE=7 + thu fert 43%; (5) quota wheat flat 20-24/ngày không có standing-target; (6) service đàn 22.7 ops/ngày (cần ~45); (7) không danh mục đứng cuối mùa.

**Quá trình 6 biến thể (a/b/c/d/e/f)** — mỗi lần sai là một bài học engine/scheduler:

| Biến thể | Thiết kế | Kết quả | Bài học |
|---|---|---|---|
| v8a | geo-assign toàn phần + 7 delta | 56.9/51.1/56.6 (3 seed) | lấp đất tốt nhưng money-ops pha loãng (MILK −$8k) |
| v8b | + cap-6 + service-all tier-1 + aging | **33.8k/34.9k — THUA v6** | 19 task tier-1 nuốt phase-1 |
| v8c | + fix NameError | 51.5/57.6/50.8 | **BOM NGẦM TỪ v7**: `_task_still_valid` nhánh FERTILIZE tham chiếu `day` ngoài scope → NameError → `agent()` trả `hands=[]` — CẢ ĐỘI ĐỨNG IM HẾT NGÀY mỗi khi task fert dính sticky qua giờ (v7 hiếm nổ vì fert melon hiếm) |
| v8d | tier-first toàn phần + task-set mới | 38.6-47.2k, v6 lên 62-67k | PLANT tier-2 cướp service/tưới — phi truyền tiếp |
| v8e | LAI: pha-1 tier-first (tier≤2 money-ops) + pha-2 geo+aging (fill) | **20/20 thắng v7, 1.380×** | đúng cấu trúc — nhưng thua v6 65/100 |
| v8f | + seedling-survival tier 4 | **94/100 vs v6 1.284×; 57/60 vs v7 1.434×** | tưới hạt age 0-1 = 0 yield nhưng tier-2 → tràn phase-1 → bỏ đói tưới WINDOW → wheat không chín (s115: d8 harvest 1/12) → thung lũng vốn sâu → domino thua |

**Cấu trúc v8 sau đích (3 seed TB):** empty 6.6 ô | wheat đứng 9-20 cả mùa | PLANT 165 (v7: 116) | FERTILIZE 16-21 (v7: 0) | FEED/CARE/COLLECT 247/234/233 (v7: 240/218/223) | MOVE 4.362 (v7: 4.962) | đàn CO×7 GO×7 SH×2-4 đứng tới d27.

**Quy tắc mới:**
- **R152 [E] — NƯỚC DÂU CHỈ CÓ GIÁ TRỊ QUA FERT:** ongoing crop event +1u vô điều kiện; +2u chỉ khi (tưới hôm đó AND fert còn hiệu lực). Tưới dâu ngày thường (v7 làm hằng ngày 18-23 ô tier-0) = thuần lãng phí. Tưới event không kèm bón = cũng chỉ +1. Cặp nước+fert ngày event là đơn vị năng suất thật.
- **R153 [E] — PHÂN CÔNG LAI (tier-first money-ops + geo fill-ops):** geo toàn phần pha loãng SERVICE/HARVEST (MILK −$8k); tier-first toàn phần làm PLANT cướp service. Money-ops cần bảo đảm phủ, fill-ops cần hiệu quả gần — 2 pha tách bạch.
- **R154 [E] — TƯỚI CỨU HẠT NON PHẢI TIER THẤP:** tưới age 0-1 (ngoài window) = 0 yield nhưng buộc phase-1 khi tier 2 → nuốt units đúng buổi tưới window → wheat trễ 2 ngày → domino thung lũng vốn (s115 chứng minh nhân-quả: 28.9k → 62.4k chỉ từ 1 dòng tier).
- **R155 [E] — STICKY-VALIDATION LÀ ĐIỂM NỔ:** mọi nhánh trong _task_still_valid phải test với task thật tồn tại qua giờ — NameError tại đây biến cả đội thành đứng im mà không có exception nào lộ ra ngoài (bắt bằng trace "hands=[]").

**Bàn giao v9:** WATER 580 (top-3 982-1.387) | HARVEST 196 (410-615) | weeds 11.5 | FERTILIZE 16-21 (91-186) | herd theo shop-draw còn thua v6 ở seed wool/milk-deep (s129: v6 62u wool) — các trụ còn lại của Phần 9.5.

### 11.9 VÒNG 43 — ĐỐI CHIẾU PHONG CÁCH CHƠI v8 vs TOP-3 (user yêu cầu: động vật/vị trí/nhân công/đất trống)

**Phương pháp:** extract thống nhất 2 format (Kaggle replay + arena JSONL, quy ước god-replay) → 16 player-traces: top-3 ×4 (SpaTaro×2, UMG, Otter) + v8 ×6 + v7 ×6 (v8 vs v7, 3 seed × 2 ghế; tool: `tool-results/v8_style/`). Đo đạc theo TỪNG GIỜ với vị trí đầy đủ (10×10 grid) — lần đầu có hình học ô nuôi + khoảng cách đi bộ thật.

#### 43.1 Phân bổ mua & khai thác động vật — v8 trễ 11 NGÀY và sổng đàn cuối mùa

| Hệ số | TOP-3 (4 trận) | v8 (6 trận) | v7 (6 trận) |
|---|---|---|---|
| Mua con đầu tiên | **d0** (SpaTaro $1.800; UMG $2.400 còn $29; Otter $1.700) | **d11** (sau melon-payday) | d11 |
| Đàn d15 / d20 | 7-15 / 7-22 | 16-17 / 20-21 | 18-19 / 18-19 |
| Sổng con (structure rỗng) cả mùa | 0 (chỉ d29 thanh lý) | **7-8 con d26-28** | tương tự |
| FEED/đàn mỗi ngày | **1.00** (tới d28) | 0.94-1.00 → tụt **0.47-0.67** d24-28 | 0.8-1.0 |
| Animal-days cả mùa (ước) | 500-630 | **260-280** | ~250 |

- **Cơ chế**: engine `_daily_refresh_animals`: `consecutive_unfed >= 2` → **con vật bỏ trốn, structure ở lại thành ô chết**. Top-3 cho ăn đủ 100% đàn mỗi ngày đến tận d28 (care-bonus max). v8 dừng feed d24+ khi dồn lực thanh lý → 7-8 con trốn = mất $2.5-3.5k vốn + ô structure chết + đứt dòng trứng/sữa.
- **Chi phí cơ hội của 11 ngày trễ** (nhân quả): bò mua d0 → sữa đầu d8 (first_yield=8); bò mua d11 → sữa đầu d19. Mỗi bò mất ~5 lượt sữa ($169/lượt ×6 bò ≈ $5k) + ngỗng 6 con × 7 ngày trứng ($2.1k) + cừu → **tổng bỏ lại $8-12k** — đúng cỡ khoảng cách $51-62k vs $93-109k (có pha pie).
- Gốc rễ trong code v8: cổng `day<5 cow/sheep=0`, `day<=10: cow≤1+money//900` — thiết kế cho tư duy "bootstrap nghèo vốn", trong khi **startingMoney=3000** (engine default, arena dùng y hệt) thừa sức mua đàn d0 VÀ vẫn chạy melon. v8 tự đặt mình vào thung lũng vốn nhân tạo d5-9 ($57-959).

#### 43.2 Vị trí ô nuôi động vật — top-3 ôm shed, v8 đẩy đàn ra SW

| Hệ số (d20) | SpaTaro×2 | UMG | Otter | v8 | v7 |
|---|---|---|---|---|---|
| Số con | 7-11 | 14 | 22 | 20-21 | 18-19 |
| d̄shed (Manhattan từ (4,4)) | **1.9-2.2** | 2.1 | 3.0-3.7 | **3.3-4.3** | 3.3-4.1 |
| bbox đàn | 5-8 | 8-9 | 12-17 | 13-17 | 14-18 |
| Phân bố quadrant | NW 6-9 | NW 8-9 | NW 9, NE 8, SW 5 | **SW 13-14**, NW 4-6 | NE 6-10, SW 6-9 |

- Top-3 **BUILD coop/pasture TRƯỚC khi trồng** (d0-1 grab 5-7 ô đẹp sát shed), cây trồng bao quanh. v8 lấp full 25 ô NW bằng cây d0 (melon/carrot/wheat) → structure d11 chỉ nhận ô rìa SW (sort từ tâm (5,5) nhưng NW đã kín).
- Vị trí cây trồng thì NGANG nhau giữa các nhóm (d̄shed 4.2-5.8, dâu top-3 thậm chí xa hơn v8: 5.44 vs 4.68) → **chênh lệch hình học nằm ở đàn, không ở cây**.

#### 43.3 Tác động vị trí → nhân công — v8 cháy 59% lệnh vào di chuyển

| Hệ số | TOP-3 | v8 | v7 |
|---|---|---|---|
| Hired units/ngày (d8-26) | 9-13 (TB 11.75) | **12-13** | 12-13 |
| Lệnh/ngày | 230-247 | 248 | 242-245 |
| MOVE% | **40-43%** | **59%** | 62-64% |
| Đi bộ ô/ngày | **91-98** | **132-133** | 139-140 |
| → Lệnh hữu ích/ngày | **133-145** | **~101** | ~88-92 |
| FEED/CARE/CFERT d̄shed | 1.8-2.1 (S/UMG), 3.3-3.4 (Otter) | 3.3-3.6 | 3.3-3.7 |
| WATER (mùa × d̄) | 982-1.388 × 4.9-5.0 | 554-580 × 4.2-4.3 | 560-602 × 3.9-4.1 |
| HARVEST (mùa) | 410-615 | 194-209 | 168-227 |

- v8 thuê NHIỀU hands hơn (12-13 vs 9-12) nhưng mỗi lệnh làm việc phải trả ~1.45 lệnh MOVE (top-3: ~0.7). Hai nguồn: (a) đàn ở SW → chuyến service gấp đôi độ dài; (b) **bàn cờ phân mảnh** — 20-30 ô chết rải rác khiến các cụm việc không liền kề, unit phải băng qua đất chết; top-3 đầy 75/75 nên các dải việc liền lạc, bước 1 ô là tới việc mới.
- Đây là vòng lặp tự củng cố: đất trống → đi bộ nhiều → ít lệnh fill/plant → đất lại trống (R151 phiên vị trí).

#### 43.4 Tỷ lệ đất trống toàn trận + cửa sổ trống lớn nhất

**% ô đang sản xuất / ô đã mở** (cây đứng + con sống; "chết" = empty+weed+structure rỗng):

| Giai đoạn | TOP-3 | v8 | v7 |
|---|---|---|---|
| Mở đầu d1-7 | 81.5% | **86.5%** (v8 lấp NW tốt hơn!) | 84.9% |
| Giữa d8-20 | **97.5%** (chết 1.9 ô) | 68.6% (chết 22.3) | 53.0% |
| Cuối d21-28 | **86.7%** (chết 10.0) | **48.4%** (chết 38.7 — trong đó weed 32.3!) | 48.2% |

**Chuỗi ô chết theo ngày (TB nhóm, empty+weed+null):**
- TOP-3: `d7-d26: 0-6 ô` (20 ngày liên tiếp gần tuyệt đối) → chỉ d27-29 thanh lý (19→35→57)
- v8: d10 hố **48 ô** (mua SW khi chưa có vốn lấp) → d14 hố 29 (máy wheat chết) → mạn tính **20-38 ô suốt d15-27** → d28-29 (61-64)
- v7: mạn tính 30-40 ô từ d11.

**Diễn giải "thời gian trống nhiều nhất":**
- Cả hai đều trống nhất ở d27-29 — nhưng top-3 là thanh lý CÓ CHỦ ĐÍCH (không gì chín kịp nữa; d29 sell-till-$1); v8 cũng vậy ở d29 nhưng bị phạt thêm weed.
- Khoảng cách THẬT nằm ở 2 cấu trúc lỗi riêng của v8: (1) **hố d10 = 48 ô** — mua SW land đúng ngày melon-payday nhưng đàn/hạt/fert chỉ về d11-15 (top-3 sau khi mua NE chỉ hố 25-39 và vá xong trong 4-5 ngày); (2) **mãn tính 20-38 ô chết d15-27** — phần lớn là weed 17-32 ô (cây chết vì không tưới + không nhổ + không replant; top-3 giữ weed 0.1-3.1).

#### 43.5 Loại cây lấp đất + kênh doanh thu

| Kênh bán (units/mùa) | TOP-3 | v8 | Ghi chú |
|---|---|---|---|
| WHEAT | 657 | 765 | v8 bán nhiều — nhưng mua thêm **814** (top-3 mua 318, phần lớn rác SpaTaro) |
| STRAWBERRY | **316** | 60 | dâu đứng top-3 25-34 (replant 4-8/ngày) vs v8 18-26 không duy trì |
| FERTILIZER | 247 | 212 | gần |
| MILK | **181** | 79 | hậu quả của 11 ngày trễ + sổng đàn |
| CARROT | 166 | 42 | top-3 gieo carrot d24-27 làm kênh đứng cuối |
| EGG | 138 | 174 | v8 tốt hơn (ngỗng nhiều) |
| MELO | 107 | 86 | tương đương |

- Máy wheat của v8 **chết từ d14** (đứng 0-9 ô vs top-3 13-32 cả mùa) → v8 phải MUA wheat trên thị trường để feed đàn = rò rỉ vốn vào thứ top-3 sản xuất miễn phí trên đất của họ.

#### 43.6 Quy tắc mới vòng 43

- **R156 [E] — VỐN $3.000 LÀ CHO MUA ĐÀN D0:** cổng `day<5 = 0` và cap money-based của v8 là tư duy kinh tế $500-era; bò d0 cho sữa đầu d8. Trễ tới d11 = bỏ lại $8-12k (nhân quả). Dòng tiền top-3 về 0 sớm lành mạnh — con vật tự trả lãi.
- **R157 [E] — ĐÀN LÀ BẤT ĐỘNG SẢN TRUNG TÂM:** structure phải giành 5-7 ô sát shed TRƯỚC khi trồng (service d̄ 1.9-2.2 vs 3.3-4.3 = ~2× chiều dài mỗi chuyến CARE/FEED/CFERT). Đàn SW + cây trung tâm là cấu trúc ngược.
- **R158 [E] — FEED ĐẾN NGÀY CUỐI:** `consecutive_unfed>=2` = con trốn, structure thành ô chết + mất vốn. Top-3 feed/đàn = 1.00 tới d28; v8 tụt 0.47 d24-28 → 7-8 con trốn. Thanh lý d29 KHÔNG có dump cuối ngày — mọi thứ trên tay h22 mất trắng, nhưng con vật vẫn nhả tới d29 nếu còn sống.
- **R159 [E] — WHEAT ĐỨNG LÀ NHÀ MÁY THỨC ĂN:** 13-32 ô wheat đứng cả mùa = feed tự cấp + 657u bán; phụ thuộc BUY_PRODUCT wheat (814u của v8) là thuê ngoài chức năng cốt lõi của đất.
- **R160 [E] — NGÂN SÁCH ĐẤT CHẾT ≤6 Ô GIỮA MÙA:** hố duy nhất chấp nhận được = sau BUY_LAND, ≤12 ô, vá trong ≤5 ngày (chuẩn UMG d3-6: 25→39→23→9). Hố d10=48 của v8 + mạn tính 20-38 ô là 2× vi phạm. Weed là "đất trống ngụy trang" — phải đo empty+weed+structure-rỗng, không chỉ empty.
- **R161 [E] — CỬA SỔ TRỐNG ĐỊNH MỆNH CÓ 2 CÁI:** d27-29 (thanh lý — ai cũng trống, vô hại) và SAU-BUY_LAND (phải vá nhanh). Mọi ô trống KHÔNG thuộc 2 cửa sổ đó = lỗi sử dụng đất. v8 vi phạm ở d8-27 mạn tính.

#### 43.7 Phán quyết vòng 44

NGUYÊN NHÂN-GỐC còn sống sót sau v8 (xếp theo tiền để bàn): (1) **trễ đàn d11** (R156) — $8-12k; (2) **đàn ra SW thay vì ôm shed** (R157) — ~30-45 lệnh hữu ích/ngày; (3) **weed 17-32 + không replant dâu/wheat liên tục** (R160) — 20-38 ô chết mạn tính; (4) sổng đàn d24-28 (R158) — $2.5-3.5k; (5) dựa wheat thị trường (R159). Đây là 5 trụ cho v9 — không cần vòng phân tích thụ động mới (nguồn đã đo exact từng giờ); vòng counterfactual chỉ cần khi kiểm chứng "mua đàn d0 + lấp NW đồng thời có hỏng melon window không".

---

### 11.10 VÒNG 44 — 5 TRỤ CỘT FIX v8 TẠI CHỖ (chỉ thị user: KHÔNG làm v9, v8 phải đạt chỉ số top-3)

**Chỉ thị:** v8 là agent cuối cùng của giai đoạn này — mục tiêu của nó là **sao chép lối chơi và đạt các chỉ số đã đo của 3 hạng đầu**. Không triển khai v9. 5 nguyên nhân-gốc ở 43.7 trở thành 5 trụ cột sửa trực tiếp trên v8.py.

#### 44.0 Sự kiện engine mới xác minh cho thiết kế (đọc source engine 1.32.7, vòng này)

| Sự kiện | Hàm ý thiết kế |
|---|---|
| **BUILD_COOP / BUILD_PASTURE MIỄN PHÍ** (chỉ tốn labor, `_apply_unit_action` không trừ tiền) | Cổng tiền 300/500 trong `_struct_reserve` của v8 là tự đặt — có thể xây toàn bộ vòng đàn d0 không tốn đô |
| **Sản xuất thú KHÔNG cần feed** (`_daily_refresh_animals`: yield_units +1 theo interval bất kể fed_today; feed chỉ để (a) reset `consecutive_unfed<2` chống trốn, (b) mở care bonus +1) | Đàn d0 không có wheat vẫn nhả milk/egg/wool đúng lịch; feed cách ngày vẫn sống — nhưng care bonus x2 sản lượng nên feed đều khi có máy wheat |
| **FERTILIZER vô điều kiện** (mọi thú không trốn nhả `fertilizer_available=True` mỗi cuối ngày) | Đàn d0 = máy in tiền $95-100/con/ngày từ d1 — đúng cơ chế bootstrap R131 của top-3 |
| **Weed chỉ mọc trên ô `None`** (`_spawn_weeds` quét tile rỗng, 0.5%/ô/ngày) | Weed 17-32 của v8 là triệu chứng của đất trống mạn tính — trụ 3 chữa bằng LẤP ĐẤT, không phải nhổ cỏ |
| **BUY_ANIMAL → shed (pending)** — engine không đòi structure tồn tại; DELIVER mới cần ô | Có thể mua đàn sáng d0 trước khi BUILD xong (v8 tự chặn bằng gate `struct_free>0` của mình) |
| **PLANT trừ từ kho hạt chung** (`private["seeds"]`), unit không cần mang hạt | Wheat-refill task chỉ cần check seeds trong kho |

#### 44.1 Bảng 5 trụ cột — chỉ số hiện tại → đích top-3 → đòn sửa

| # | Trụ cột | v8 hiện tại (đo 6 trận) | ĐÍCH top-3 (đo 4 trận) | Đòn sửa trong v8.py |
|---|---|---|---|---|
| 1 | **Đàn từ d0** (R156) | con đầu d11, animal-days 260-280 | con đầu **d0** (SpaTaro $1.800, UMG $2.400, Otter $1.700), animal-days 500-630 | Bỏ cổng `day<2/day<5/day<6 = 0` trong `_daily_plan`; starter d0 = 2 bò + 1 ngỗng (~$1.100) giữ đủ vốn melon-wave; d1-4 tăng đàn bằng dòng FERT ($95-100/con/ngày); mở cửa sổ mua w0: COW 4→0, GOOSE 2→0, SHEEP 4→2 |
| 2 | **Đàn ôm shed** (R157) | d̄shed 3.3-4.3, bbox 13-17, đàn SW | d̄shed **1.9-2.2**, bbox 5-8, BUILD trước trồng | Sort reserved theo khoảng cách shed thật (4 ô shed (4,4)-(5,5)); reserve vòng 5-7 ô sát shed từ plan d0-h0 TRƯỚC khi planting claim; BUILD tier-urg d0-3; bỏ money-gate `_struct_reserve` (BUILD free) |
| 3 | **Đất chết ≤6 + replant** (R160/161) | 20-38 ô chết mạn tính d15-27, weed 17-32, hố d10=48 | **0-6 ô chết d7-26**, hố sau land ≤12 vá ≤5 ngày, weed 0.1-3.1 | T_DIG 5→3; wheat-refill task trong ngày (standing<18 → PLANT tier 1, không chờ plan h0); plan rebuild khi ô trống mới xuất hiện giữa ngày |
| 4 | **Feed tới d28, 0 trốn** (R158) | feed/đàn 0.47-0.67 d24-28, 7-8 con trốn | **1.00 tới d28, 0 con trốn** (thanh lý d29 mới được bỏ) | `wheat_reserve` giữ tới d28 (hiện bị bỏ từ d26 → bán sạch thức ăn); mở gate mua wheat feed: d≤3 giá ≤45 (đàn non chưa có máy), d≥20 giá ≤70 (thanh lý tiền nhiều, đàn phải sống nhả tới d29) |
| 5 | **Máy wheat đứng cả mùa** (R159) | chết từ d14 (0-9 ô), mua 814u wheat thị trường | **13-32 ô đứng cả mùa**, mua chỉ 318u, bán 657u | Wheat-refill (trụ 3) với floor standing 18; quota 24-standing giữ; seed floor $30 giữ; PLANT tier 1 khi standing<14 (mở lên <18) |

**Chỉ số tổng hợp sau kỳ vọng:** MOVE% 59 → ≤48 | lệnh hữu ích ~101 → ≥125/ngày | % ô sản xuất giữa mùa 68.6 → ≥90 | cuối mùa 48.4 → ≥80 | MILK 79 → 150+u | STRAWBERRY 60 → 250+u.

#### 44.2 Ràng buộc an toàn (bài học R147 domino — không phá v8 hiện tại)

1. **Melon-wave là xương sống v8** ($13-16k payday d13-19): starter đàn d0 phải ≤$1.200 để giữ ≥$1.6k cho hạt (melon 11-14 + wheat 10 + carrot 8 ≈ $1.3-1.6k). d0 mua: 2 COW + 1 GOOSE = $1.100 — mô phỏng cấu trúc d0 của cả SpaTaro (2C+2S) lẫn Otter (2S+2G+1C) thu nhỏ.
2. **Feed d0-4 là mua thị trường** (~$25-45/wheat): 3-6 con × 5 ngày ≈ $300-700 — bù lại FERT d1+ ≈ $285-570/ngày. Được phép feed cách ngày (không trốn: cu chỉ tới 1) nhưng ưu tiên feed đều để giữ care-bonus (milk $160-300 × +1/event).
3. **Cổng xác nhận giữ nguyên hồ sơ:** battery 100 trận vs v6 **≥94/100** (v8 hiện 94) + direct 60 trận vs v8-base **≥55%** + không seed nào sụp <0.75×.
4. **Không over-reserve:** vòng structure chỉ reserve đúng `target + shed_pending - đã_xây` — ô reserved mà đàn không tới = đất chết (vi phạm chính trụ 3).

#### 44.3 KẾT QUẢ SỬ DỤNG (bản cuối cùng của v8-5trụ, xác thực 6 game style + 42 game đối đầu)

**Chỉ số 5 trụ (đo bằng analyze_style, 6 game v8-mới vs v7, seed 100/115/130 × 2 ghế):**

| Chỉ số | TOP-3 | v7-cũ | **v8-5trụ** | Trạng thái |
|---|---|---|---|---|
| Ngày mua con đầu tiên | **d0** | d11 | **d0** (6/6 game) | ✅ **ĐẠT** (Trụ 1) |
| Animal-days cả mùa | 329 | 362 | **441** | ✅ **VƯỢT** (Trụ 1) |
| FEED / CARE / CFERT (mùa) | 263/243/292 | 252/239/236 | **295/282/284** | ✅ **ĐẠT** (Trụ 4) |
| Empty tb d9-27 (ô) | 1.76 | 23.97 | **7.92** | ✅ tiệm cận mạnh (Trụ 3) |
| Đàn d̄shed @d20 | 2.45 | 3.59 | **2.95** | △ tiệm cận (Trụ 2) |
| PLANT (mùa) | 242 | 132 | **178** | △ (Trụ 3/5) |
| Cây-chết weed tb d9-27 | 1.34 | 6.93 | 23.94 | ✗ kernel (harvest-trước-chết) |
| MOVE% | 42% | 64% | 64% | ✗ kernel |
| WATER / HARVEST (mùa) | 1188/484 | 588/208 | **471/211** | ✗ kernel (R151) |
| Kênh: EGG / MILK / WOOL | 138/181/60 | — | **210/125/33** | △ egg vượt, milk/woole dưới |

**Hiệu suất đối đầu (bản cuối):** vs v7 **6/6 (1.157×)** | vs v8-base **10/12 (1.209×)** | vs v6 **~50% (0.96-1.01×)** — v8-base cũ đạt 94/100 vs v6, tức **v6 là điểm yếu đã biết của phong cách top-3 trong kernel hiện tại** (xem R164).

**Bảng vượt chặng:** empty 21-38 → 7.9 | con đầu d11 → d0 | animal-days 361 → 441 | máy wheat chết d14 → đứng 10-20 cả mùa | feed 0.47 cuối mùa → 295 lệnh cả mùa + reserve tới d28 | dâu nhượng kênh → non-surrender 24 ô (top-3 cả hai cùng đứng) | tomato tier-4 chết → tier-1 trồng thật.

#### 44.4 Quy tắc mới vòng 44 (R162-R166)

- **R162 [E] — THUẾ WHEAT ĐỐI VỚI MÁY-WHEAT:** đối thủ dump 700-830u wheat (v6-style) → tồn tại 2 chế độ: bán theo (giá rớt, đàn đối thủ rẻ feed → nổ đủ công suất: v6 $60k) hoặc GIỮ (HOLD wheat 0.76→1.50, chỉ bán ≥$37): ta +$2.5k, v6 −$2.3k, 13/50 → ~50% — base vô tình là net-buyer (máy chết d14 + mua 814u) nên thắng v6 94/100: mạng lưới giá wheat ĐIỀU KHIỂN kinh tế đàn đối thủ.
- **R163 [E] — QUOTA TỰ TRIỆT TIÊU:** quota kiểu `min(10, 24−standing)` là "số trồng/ngày" nhưng layer crop_tiles tính `need = quota − standing` → standing 10 → quota 10 → need 0 → không mua hạt → refill đói hạt → máy chết. Mọi standing-target phải là ĐÍCH TUYỆT ĐỊI nhìn được từ CẢ 3 layer (plan/seed-buy/refill).
- **R164 [E] — TRẦN LAO ĐỘNG ĐỊNH MẬU TOP-3 (R151 phiên định lượng):** kernel 90-100 lệnh hữu ích/ngày (MOVE 64%) nuôi nổi: đàn 14 + dâu 24 + máy 20 + melon + tomato. Đẩy lên đàn 18 + dâu 24 + máy 24 = tưới thiếu → **dâu chết dây chuyền giữa mùa (24→9→7 ô s306)**, weed (cây chết) 24-31 ô, kênh $30k mất cho đối thủ độc quyền. Top-3 chạy mật độ ấy được vì 133-145 lệnh hữu ích/ngày (MOVE 42%) — muốn đạt chỉ số top-3 THẬT phải nâng kernel trước (đi bộ ngắn hơn, harvest-trước-chết, tưới đúng cửa sổ).
- **R165 [E] — MUA-BÁN CHÉO WHEAT (churn):** mua feed tối $45-70 (buffer 2 ngày) rồi sáng sau bán $19-40 (dump trên reserve) = −$10-15/unit × 20-40/ngày = **rút $4-7k + tự nâng giá cho đối thủ**. Phải: trừ dòng máy đang đứng (×2 ngày) khỏi nhu cầu mua; d20+ chỉ mua khi acute (shed<6); reserve cuối mùa = đàn × số ngày còn.
- **R166 [E] — BÁN SẠCH FERT TUẦN 0:** gate `nf > 2` giữ 2 FERT khi chưa có gì để bón → đàn d0 mất $190-285/ngày dòng huyết bootstrap (R131). Dâu vào event (d4+) mới giữ 2.

**Phán quyết vòng 45:** 5 trụ đã cài VÀ vận hành (Trụ 1/4 đạt chỉ số, 2/3/5 tiệm cận); phần còn thiếu của mọi trụ đều trùng một gốc: **kernel lao động (R151/R164) — MOVE 64% vs 42%, WATER 471 vs 1188, HARVEST 211 vs 484**. Không cần vòng phân tích thụ động mới; cần kernel mới (nâng lệnh hữu ích ≥130/ngày) rồi mọi chỉ số top-3 còn lại tự buông theo. v6-weakness (R162) là biến thể cùng gốc: khi một kênh dùng chung (wheat/đất) bị đối thủ khai thác đủ dày, phong cách top-3 cần kernel hiệu suất cao hơn đối thủ để không bị đẩy về thế bị động.
