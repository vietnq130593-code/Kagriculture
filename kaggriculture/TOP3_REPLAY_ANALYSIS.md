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

---

### 11.11 VÒNG 45 — 5 CÂU HỎI MỚI CỦA USER: ĐẤT TRỐNG/NGÀY, ĐÀN+VỊ TRÍ/NGÀY, CÂY/NGÀY, THỜI ĐIỂM BÁN + TẤN CÔNG THỊ TRƯỜNG, 90K-110K TỪ ĐÂU (god-ledger EXACT)

**Phương pháp:** god-replay engine thật (0-mismatch money/inv/shed) cho cả 2 replay top-3 (có sẵn vòng 2) + 6 game v8-5trụ vs v7 (mới — `god_arena.py`, 6/6 game 0-mismatch) → **commit-log từng unit** (mua/bán/giá chính xác từng đô) + phase5.py đo không gian từng ngày (đất chết, đàn, khối liền-kề, cây theo loại). Nguồn truth: 4 player-trace top-3 + 6 v8 + 6 v7.

#### 45.1 Ba phát hiện engine (đọc source vòng này — hiệu chỉnh 3 hiểu lầm cũ)

| Phát hiện | Chi tiết | Hàm ý |
|---|---|---|
| **BUY_PRODUCT chỉ chạy với WHEAT/FERTILIZER** (`_process_market`: mọi item khác = malformed → drop thầm) | SpaTaro phát 1.936 lệnh mua MELON/MILK/STRAW/CARROT/TOMATO/EGG/WOOL → **0 lệnh nào thực thi** — chỉ 449 wheat + 26 fert chạy | "Tấn công thị trường bằng mua" KHÔNG TỒN TẠI trong engine này; top-3 thắng bằng sản xuất + thời điểm bán, không phải pump giá |
| **Cây chết khi `consecutive_unwatered >= 2`** — mọi cây (kể cả ongoing dâu/tomato) PHẢI tưới tối thiểu mỗi 2 ngày để sống | R152 đúng về YIELD (nước ngày thường = 0 yield) nhưng SINH TỒN vẫn cần nước mỗi-2-ngày; top-3 WATER 1.162 lệnh/mùa ≡ 61 cây đứng × mỗi-2-ngày + event | Không tưới = mất cây = mất kênh; nước sinh-tồn là chi phí cố định của khối lượng kênh |
| **HIRE theo fib(hires_today)** — hands BIẾN MẤT cuối ngày, thuê lại mỗi sáng; d0 4-5 hands = $5-12 | v8 HIRE 7.591$/mùa (TB 33 lệnh) vs top-3 6.424$ — cùng cỡ, không phải chênh lệch lớn | Nhân công là chi phí nhỏ; giá trị nằm ở số lệnh hữu ích mỗi unit (R151 đúng) |

#### 45.2 A1 — ĐẤT CHẾT (empty+weed) THEO NGÀY

```
TOP3: d0 2·1·1·7·12 | d5 12·9·0·6·0 | d10 5·1·0·0·1 | d15 2·2·0·0·0 | d20 0·0·1·4·5 | d25 4·8·18·34·55
V8:   d0 0·0·0·0·6 | d5 4·4·3·15·15| d10 29·25·25·29·33 | d15 30·29·25·25·31 | d20 33·34·37·35·35 | d25 36·38·43·50·53
```
- TOP3 giữ **0-5 ô chết suốt d7-d26** (20 ngày), chỉ mở rộng thanh lý d27-29. v8: hố d8-13 (15-33, sau khi mua đất) + mạn tính 25-37 ô d14-28 → **v8 duy trì ~28 ô chết d14-27 trong khi top-3 = 0-5**.

#### 45.3 A2 — ĐÀN + VỊ TRÍ + LIÊN KHỐI (đo mới: components/big_share/adjacency)

| Chỉ số d10-27 | TOP3 (4 trace) | v8 (6 game) | v7 (6 game) |
|---|---|---|---|
| Số con TB/ngày | 13 (d20: 7-13) | **19** (d20: 19) | 19 |
| **Số cụm (4-liên-thông)** | **3.28** | **5.67** | 6.06 |
| **big_share** (cụm lớn/tổng) | **0.79** | 0.62 | 0.56 |
| **adj%** (ô có hàng xóm đàn) | **0.91** | 0.77 | 0.76 |
| d̄shed | 2.42 | 3.19 | 3.20 |

- **Hình học top-3 (d20, ô thật):** SpaTaro M1: 7 con thành dải liền (1,3)(1,4)(2,4)(3,3)(3,4)(4,4)(5,4) — dải dọc ôm sát shed; UMG M1: 14 con khối (2,3)-(4,6)+(4,1)(4,2)(5,1); Otter M2: 22 con trải (0,3)-(8,4) nhưng vẫn adj 87%. **Cây trồng bao quanh khối đàn** (dâu xa hơn: d̄ 5.4-5.8).
- **v8 d20 (s100):** 17 con rải 3 vùng: cụm chính (3,1)-(6,4) 12 con + (1,3)(1,4) + (4,0) + (8,4)(9,0) — **5-6 cụm tách biệt, đúng như user quan sát**. Gốc: reserved sort theo khoảng-cách-shed TỪNG Ô → lấy ô quanh vòng shed (4 phía) thay vì mọc thành khối.

#### 45.4 A3 — CÂY ĐỨNG THEO NGÀY + CƠ CẤU

```
Tổng cây đứng: TOP3 d0 18 → d10 58-62 → d20 57-61 → d27 43·27·6 (thanh lý)
               V8   d0 23 → d10 22-38   → d20 17-21 → d27 11·5·1
Cơ cấu TB d5-27 (ô đứng):  TOP3: dâu 24.8 · wheat 20.2 · carrot 5.3 · melon 4.5 · tomato 2.6
                            V8:   dâu 12.6 · wheat 8.3  · carrot 2.8 · melon 2.7 · tomato 1.4
```
- TOP3 duy trì ~60 cây đứng cả mùa trên 75 ô; v8 chỉ ~26. **Máy wheat v8 chết giữa mùa** (d10: 9 ô → d15: 1 ô → d20: 4 ô) — top-3 giữ 20 ô suốt.

#### 45.5 A4 — THỜI ĐIỂM BÁN + "TẤN CÔNG QUA LẠI"

**Phân bố giờ bán (units, exact):** TOP3: **h0 29%** + rải đều ban ngày (h1-20: 1-3%/giờ) + **h21-23: 26%**. V8: **h0 56%** + h21-23 13%.
- Cả hai cùng dồn sáng (sau auto-drop cuối ngày đầy shed); top-3 THÊM nhịp bán cuối ngày (h21-23 thu/hát trước khi hết ngày) và rải nhỏ ban ngày — v8 dồn 1 cục sáng.
- **"Tấn công qua lại" thật sự của top-3 = KHÔNG có**: các lệnh mua chéo bị engine drop (45.1); nhịp thật là **đan xen bán dần theo drain của town** — mỗi lệnh bán nhỏ (3-9u) để thị trường kịp hút giữa các đợt, giữ giá không tự sập. v8 hiện bán cục lớn nhưng ÍT HƠN về khối lượng nên giá đơn vị còn CAO HƠN (milk $261 vs $130, dâu $245 vs $168) — vấn đề của v8 là KHỐI LƯỢNG không phải giá.

#### 45.6 A5 — 90K-110K TỪ ĐÂU (god-ledger exact, TB/trận)

| | TOP3 (final $102.372) | V8 (final $56.276) | Chênh |
|---|---|---|---|
| **REV $132.610** | dâu **$42.765** (254u@$168) · milk $21.872 (168u@$130) · wheat $19.882 (574u@$35) · melon $15.186 (82u@$186) · fert $11.941 · egg $7.046 · carrot $6.041 (135u@$45) · wool $5.490 · tomato $2.388 | $106.977: milk $32.578 (125u@$261) · wheat $22.921 (500u@$46) · fert $13.614 · dâu $12.965 (**53u**@$245) · egg $9.720 · melon $6.639 (**32u**) · wool $6.414 · tomato $1.874 · carrot $252 (**8u**) | **−$25.633** |
| **COST $33.238** | mua wheat $9.923 · hire $6.424 · seeds $8.464 · animals $5.500 · land $3.000 · mua fert $1.226 | $53.702: **mua wheat $30.902** · hire $7.591 · seeds $6.705 · animals $6.333 · land $3.000 | **+$20.464** |
| Đường tiền | d12 $14.6k → d18 $41.4k → d24 $74.8k → d27 $88.6k | d12 $6.1k → d18 $8.7k → d24 $31.6k → d27 $42.1k | |

**Phân rã khoảng cách $46.096 (đúng cent):**
1. **Kênh DÂU −$29.800** (53u vs 254u) — v8 đứng 12.6 ô vs 24.8 + cây chết giữa mùa
2. **WHEAT NET −$18.000** — v8 mua 610u ($30.9k) bán 500u ($22.9k) = net −$8k; top-3 mua 248 ($9.9k) bán 574 ($19.9k) = **net +$10k** (máy 20 ô tự cấp feed đàn 13 + bán dư)
3. **MELON −$8.547** (32u vs 82u — top-3 trồng lại wave-2 d16-21)
4. **CARROT −$5.789** (8u vs 135u — kênh đứng rẻ $20 hạt)
5. Trừ đi: milk/egg/wool/fert của v8 CAO HƠN top-3 +$16.0k
→ Nguồn 90-110k của top-3 = **dâu $43k + sữa $22k + wheat NET $10k + melon $15k + fert $12k** trên đất 95% sản xuất — không phải kỹ thuật mua bán.

#### 45.7 Quy tắc mới vòng 45

- **R167 [E] — ĐÀN MỘT KHỐI LIỀN KỀ:** reserved phải mọc BFS-liên-thông từ khối sẵn có (mỗi ô mới kề ≥1 ô đàn), không sort từng-ô-theo-khoảng-cách (loại布局 vòng shed 4 phía = 5.67 cụm). Chỉ số đo: ncomp ≤2, big_share ≥0.85, adj ≥90%.
- **R168 [E] — ĐÀN 13 + MÁY 20 = TỰ CẤP:** đàn 19 (v8) với máy chết = mua 610u wheat ($31k) nuôi $48.7k doanh thu thú (net $17.7k); đàn 13 + máy 20 đứng = top-3 net $24.5k + lao động dư cho tưới. Floors target (cừu 2/bò 5/ngỗng 5) phải cho phép cap 13 hạ thật (floor cũ 4+6+7=17 chặn cap 14 — đàn v8 thực tế 19 vì thế).
- **R169 [E] — KHỐI LƯỢNG > GIÁ BÁN:** v8 đạt giá đơn CAO HƠN top-3 mọi kênh (milk $261/$130, dâu $245/$168) nhưng thua $46k vì khối lượng (53u dâu vs 254u). Mọi tối ưu HOLD/giá thêm = sai hướng; phải tăng cây đứng (26→58 ô) + giữ sống (nước mỗi-2-ngày).
- **R170 [E] — MÁY WHEAT CHẾT TỪ LAYER HẠT:** plan h0 thấy standing 19 → need 1 → không mua hạt; giữa ngày wheat chết/harvest → standing rơi → refill không có hạt (R163 tái diễn ở layer seed-buy). Seed-buy wheat phải nhìn standing SỐNG hiện tại (floor 16 − live), không phải crop_tiles h0.
- **R171 [E] — HỐ SAU MUA ĐẤT LÀ HỐ SAU HẠT:** d8-13 v8 chết 15-33 ô ngay sau BUY_LAND vì hạt chưa về + PLANT tier 4 thua dịch chuyển. Top-3 sau BUY_LAND vá ≤5 ngày. Land + seed budget phải đi cùng nhau.

**Phán quyết vòng 46:** 5 đòn sửa v8 (Trụ A: đàn BFS-liền-kề; Trụ B: đàn 13; Trụ C: máy wheat 16-20 đứng cả mùa bằng 3 layer; Trụ D: khối lượng dâu 24 đứng + carrot floor 8 + melon wave-2 nới; Trụ E: feed-buy acute-only). Mục tiêu tổng: final $90-110k, đất chết d7-26 ≤6, cây đứng ≥55, dâu ≥200u bán.

#### 45.8 TRIỂN KHAI & KẾT QUẢ VÒNG 45 (12 biến thể differential trên v8)

**Các đòn đã cài (theo thứ tự đo):** Trụ A (BFS-liền-kề) · Trụ B (đàn 13, floors 2/5/5) · Trụ C (wheat 3-layer: quota max(16,đàn+3) + seed-buy nhìn standing sống + refill floor 20) · Trụ D (carrot floor 8 không marg + melon nới 0.66/0.58 tới d21 + PLANT tier 3 khi >6 ô trống) · Trụ E (feed-buy acute-only, bỏ dairy-deep) · R172 (nước cứu hạt non — cây mới trồng chết ngay EOD nếu không tưới ngày trồng) · R173 (DIG tier 3 khi weed>6) · R175 (không mua/bán wheat d27+ — chặn churn vòng tròn ~318u) · R176 (dâu standing-target tuyệt đối d14-26) · R177 (fert dâu event tier 2).

**Hai vòng loại (đo lùi phải revert):** (1) survival-water tier 2 + DIG tier 2 = NGẬP phase-1 starving service — **$47.971** (−$8.5k); chỉnh tier 3 → bật lại $67k. Bài học lặp v8b: mọi task thêm vào tier ≤2 phải đo lùi. (2) R177 gần trung tính (dâu 104→110u) — giữ vì dương nhẹ.

**Bảng chỉ số cuối (6 game vs v7, god-verify 0-mismatch):**

| Chỉ số | TOP-3 | v8 đầu vòng 45 | **v8 cuối vòng 45** | Δ |
|---|---|---|---|---|
| Final money | $102.372 | $56.276 | **$67.365** | **+$11.089** |
| Đàn: ncomp / big_share / adj% | 3.28/0.79/0.91 | 5.67/0.62/0.77 | **1.00/1.00/1.00** | ✓ **VƯỢT top-3** |
| Đàn d̄shed | 2.42 | 3.19 | **2.04** | ✓ VƯỢT |
| Số con (d20) | 13 | 19 | **14.5** | ✓ parity |
| Dâu đứng (TB mùa) | 24.8 | 12.6 | **18.3** (giữ 24 tới d21) | △ |
| Máy wheat đứng | 20.2 (cả mùa) | 8.3 (chết d15) | **13.1 (sống cả mùa)** | △ |
| Cây đứng d12-20 | 57-61 | 26-33 | **34-53** | △ |
| WATER / HARVEST (mùa) | 1.188/484 | 471/199 | **659/231** | △ |
| Churn wheat d28-29 | 0 | ~318u vòng tròn | **0** | ✓ |
| Đất chết d9-27 (empty+weed) | 1.76 | ~28 | **21.4** | ✗ còn hố |
| MOVE% | 42% | 62% | 62% | ✗ kernel |
| vs v7 (6 game) | — | 6/6 ($56.3k) | 4-5/6 ($67.4k) | s115 sát nút |
| vs v6 (20 ghế A) | — | ~50% | 7/20 | ✗ R162 |

**Phân rã god-ledger cuối (TB/trận):** MILK $29.907 (120u@$249) · WHEAT $22.633 (512u) · STRAW $23.826 (104u@$228) · MELON $9.191 (46u) · EGG $8.755 · FERT $10.890 · WOOL $5.346 vs top-3 STRAW $42.765 (254u) — **còn thiếu $23k nằm ở: dâu khối-lượng (104 vs 254u — harvest/event-fert labor), melon 46 vs 82u, carrot 11 vs 135u, wheat net −$3.4k vs +$10k**.

**Phán quyết vòng 46:** Trụ A/B đạt và vượt (đàn 1 khối liền kề — yêu cầu trực tiếp của user); Trụ C/D cải thiện lớn nhưng chưa tới đích; mọi kênh còn thiếu đều TỤNG MỘT GỐC: **kernel lao động MOVE 62% vs 42%** (R151/R164 — WATER 659 vs 1.188, HARVEST 231 vs 484). Đất chết 21.4 = weeds từ cây chết + hố sau BUY_LAND d8-13. Muốn $90-110k thật sự cần kernel mới (đi bộ ngắn + lệnh hữu ích ≥130/ngày) — đúng bàn giao từ Task 42-44.

---

### 11.12 VÒNG 47 — LOÀI BÒ/CỪU/NGỖNG + TỔNG KẾT HỆ CHỈ SỐ ĐO LƯỜNG + ĐIỀU TRA NGUYÊN NHÂN 90K-110K

**Nguồn (mới, sạch):** `new46/` = 6 game **v8-HIỆN-TẠI** vs v7 (seed 100/115/130 × 2 ghế, R175 hoạt động — khớp đích vòng 45: final TB $67.365, 4/6 thắng) → `god_arena` 6/6 game **0-mismatch** → commit-log exact từng unit. Top-3 = `r2_god_M1/M2` (4 seat: SpaTaro ×2, UMG, Otter Vibe). Tool: `phase6.py` (loài + money-flow) + `phase6b.py` (units/ngày + 5 ngày cuối).

**Lưu ý danh pháp:** engine chỉ có 3 loài — **COW (bò $400→MILK)**, **SHEEP (cừu $500→WOOL)**, **GOOSE (ngỗng $300→EGG)**. "Vịt" của user = **ngỗng GOOSE** (loài chim đẻ trứng duy nhất; không có vịt trong engine).

#### 47.0 B0 — TỔNG KẾT HỆ CHỈ SỐ ĐO LƯỜNG ĐANG CÓ (18 họ)

| # | Họ chỉ số | Đo được | Tool |
|---|---|---|---|
| 1 | **Ledger thị trường exact** | từng lệnh mua/bán + giá từng unit (0-mismatch), rev/cost theo kênh | r2_godreplay · god_arena · phase5b |
| 2 | Thời điểm bán | giờ của lệnh SELL, giá p0, phân bố % giờ | phase5/5b |
| 3 | Phân rã tiền final | 3.000 + Σrev − Σcost (khớp từng đô) | phase5b |
| 4 | Đường tiền cuối ngày + net/ngày | money EOD từng ngày | N2 · phase6 |
| 5 | **Chi theo loại THEO NGÀY** *(mới vòng 47)* | ANIMAL/LAND/HIRE/SEED/BUY:* từng ngày | phase6 |
| 6 | **Ngày kết thúc capex từng loại** *(mới)* | mua thú cuối / LAND xong / HIRE cuối | phase6 |
| 7 | **Tốc độ tích lũy sau capex** *(mới)* | net sau thú-cuối, rev 10 ngày cuối | phase6 |
| 8 | **Loài (bò/cừu/ngỗng)** *(mới — câu hỏi user)* | mua theo loài (timing+số), đàn theo loài/ngày, animal-days, peak, escape, feed-coverage/loài, doanh thu sản phẩm/loài, rev/AD, break-even | phase6 |
| 9 | Hình học đàn | ncomp/big_share/adj%/d̄shed/bbox | phase5 |
| 10 | Đất | chết/ngày (empty+weed), weeds, cây đứng/ngày + cơ cấu, hourly, cửa sổ xấu nhất | phase5 · analyze_style |
| 11 | Lao động | **units/hands THEO NGÀY** *(mới)*, MOVE%, ops mùa, walk, khoảng cách dịch vụ | phase6b · analyze_style |
| 12 | HIRE | giờ thuê (74-88% h0), chi phí fib/ngày | r2 |
| 13 | Thanh lý d27-29 | giá exact, khối lượng | Q1 |
| 14 | Kinh tế loài | milk/cow, goose-days, egg/goose-day | Q2/Q4 |
| 15 | Chu trình wheat | trồng/hái/đứng/replant, mua-bán net | Q3 · phase6 |
| 16 | FERT & nước | phân bón allocation, kỷ luật nước | N5/N8 |
| 17 | **Shed tồn cuối trận** *(mới)* | hàng chết giá trị chưa bán | phase6 |
| 18 | Counterfactual god-phẫu | nhân-quả (goose6, sheep2geese, straw15…) | cf_* |

**Còn thiếu (đề xuất khi cần):** (a) phân bổ lao động theo giờ-từng-unit (ai-làm-gì-ở-đâu mỗi giờ — mổ xẻ MOVE 62% xuống từng hành trình); (b) vòng đời từng ô cây (plant→water→harvest/chết — định vị chính xác 21-23 ô chết); (c) hiệu chỉnh pool đối thủ khi so chéo (giá v8-vs-v7 ≠ top-3-mirror) → **so khối lượng (u), không so $**.

#### 47.1 B1 — MUA + DUY TRÌ BÒ/CỪU/NGỖNG: TOP-3 vs V8

**Từng seat (mua / AD / escape / final):**

| Seat | Bò | Cừu | Ngỗng | AD bò/cừu/ngỗng | Trốn | Final |
|---|---|---|---|---|---|---|
| SpaTaro M1 | 4 | 3 | 0 | 100/78/0 | 2/1/0 | $93.281 |
| UMG M1 | 6 | 3 | 6 | 151/66/128 | 1/3/0 | $99.793 |
| SpaTaro M2 | 9 | 2 | 1 | 205/57/0 | 1/1/0 | $107.329 |
| Otter M2 | 11 | 3 | 8 | 214/83/192 | 0/0/0 | $109.084 |
| **V8 (TB 6 game)** | **6** | **1.7** | **5** | **118/29/112** | **0/0/0** | **$67.365** |

**TB nhóm theo loài:**

| Loài | Nhóm | Mua (d_first→d_last) | AD | Peak | Feed-cov | Escape | Rev (TB/trận) | BE |
|---|---|---|---|---|---|---|---|---|
| Bò | TOP3 | 7.5 (d0→d18) | 168 | 11 | 78% | 1.0 | $21.872 | 3.1 ngày |
| Bò | V8 | 6.0 (d0→d18) | 118 | 6 | **95%** | 0 | $29.883* | 1.6 |
| Cừu | TOP3 | 2.8 (**d0**→d10) | 71 | 3 | 75% | 1.2 | $5.490 | 6.5 |
| Cừu | V8 | 1.7 (**d9**→d15) | 29 | 2 | 92% | 0 | $4.120* | 3.5 |
| Ngỗng | TOP3 | 3.8 (d0→d11) | 80 | 8 | 92% | 0 | $7.046 | 3.4 |
| Ngỗng | V8 | 5.0 (d0→d11) | 112 | 5 | **99%** | 0 | $8.472* | 4.0 |

\* Giá trị $ của v8 bị thổi phồng do pool (v7 không cạnh tranh milk/egg/dâu): MILK $256/u vs $130 của top-3-mirror — **so khối lượng**: milk 116u vs 168u, wool 22u vs 53u, egg 188u vs 133u (kênh duy nhất vượt).

**AD theo pha (đo mới):**

| Pha | TOP3 | V8 | Δ |
|---|---|---|---|
| d0-10 | **77.0** | 40.7 | **−47%** ← hố duy nhất |
| d11-20 | 127.8 | 103.8 | −19% |
| d21-29 | 102.2 | 101.3 | ngang |

**6 khác biệt chính:**
1. **Chi ngày-0:** top-3 bỏ $1.800-2.500 (TB $2.025 = 2.5 bò + 1.8 cừu + 0.5 ngỗng) trước cả hạt; v8 chỉ $1.100 (2 bò + 1 ngỗng, **0 cừu**).
2. **Cừu trễ 9 ngày:** top-3 mua cừu d0 (AD 71); v8 d9 (AD 29) — mỗi cừu d0 cho 8 lượt thu (d6,9,…27), cừu d9 chỉ 6-7 lượt.
3. **Ramp d0-d10 chậm 47%** (AD 77 vs 41): top-3 **drip-mua liên tục** d4-18 (0.5-1 con/2 ngày), v8 mua **burst** d8-18 — bò d0 sản xuất 22 ngày, bò d14 chỉ 8 ngày.
4. **Đỉnh bò 11 vs 6:** Otter 22 thú (11 bò+8 ngỗng+3 cừu) = trần lao động; v8 cap 6 bò (floor 5). Đàn cuối 14.2 vs 13 — **ngang nhau về cuối, khác nhau về SỚM**.
5. **Underfeed có tính toán:** top-3 feed bò/cừu chỉ 75-78%, chấp nhận 1-2 escape/mùa (mất $400-500/con nhưng tiết kiệm wheat); ngỗng 92%. v8 feed 95-99%, 0 escape — **v8 đúng và RẺ HƠN** khi máy wheat sống (wheat tự sản $1.7/u vs thị trường $27-45) — không cần bắt chước underfeed.
6. **Ngỗng là kênh v8 vượt top-3:** 188 egg vs 133; ngỗng feed-cov 99% + 0 escape + BE 4 ngày.

#### 47.2 B2 — ĐIỀU TRA "LUÔN ĐỌNG 90K-110K" (god-ledger exact từng ngày)

**Đồng nhất-money 4 seat top-3 + 6 game v8 (đều 0-mismatch):**

| | Rev mùa | Spend mùa | Final | Thú cuối | LAND xong | HIRE cuối | Net sau thú-cuối | rev 10 ngày cuối |
|---|---|---|---|---|---|---|---|---|
| SpaTaro M1 | $120.293 | $30.012 | $93.281 | **d10** | d8 | d29 | +$79.138 (85%) | $53.500 |
| UMG M1 | $123.506 | $26.713 | $99.793 | d15 | d8 | d29 | +$77.205 (77%) | $62.979 |
| SpaTaro M2 | $138.824 | $34.495 | $107.329 | d12 | d8 | d29 | +$87.379 (81%) | $63.806 |
| Otter M2 | $147.817 | $41.733 | $109.084 | d18 | d10 | d29 | +$64.617 (59%) | $71.572 |
| **V8 TB** | **$94.675** | **$30.310** | **$67.365** | d14-18 | d10 | **d28** | +$52.168 (77%) | $54.895 |

**Chi cả mùa theo loại (TB/trận) — ĐÃ ĐỐI CHỈNH:**

| Loại chi | TOP3 | V8 | Ghi chú |
|---|---|---|---|
| ANIMAL | $5.500 | $4.733 | ngang |
| LAND | $3.000 | $3.000 | cả hai xong d8-10 |
| HIRE | $6.424 (10-11 hands, $143/ngày) | $8.212 (12 hands, $376/ngày) | v8 trả NHIỀU HƠN cho lao động |
| SEED | $7.165 | $6.807 | ngang |
| BUY:WHEAT | $9.923 (~300u) | $7.558 | R175 hoạt động — hố $16k vòng 45 đã bịt |
| BUY:FERT | $1.226 | $0 | v8 tự thu FERT từ đàn |

**Đường tiền (TB nhóm):** TOP3: d12 $14.6k → d15 $24.6k → d18 $42.0k → d21 $60.7k → d24 $75.6k → d27 $89.2k → **$102.4k**. V8: d12 $6.5k → d18 $18.3k → d24 $36.0k → d27 $52.1k → **$67.4k**.

**5 NGUYÊN NHÂN "LUÔN ĐỌNG 90K-110K" (câu trả lời điều tra):**
1. **Trần chi là cấu trúc và NHỎ:** cả mùa chỉ $27-42k (đất $3k xong d8-10 + thú $4.7-5.5k xong d10-18 + hire ~$143-376/ngày + hạt ~$240/ngày + feed ~$330/ngày). Không còn mục tiêu đầu tư nào hấp thụ tiền — sau d10-18 mọi thứ đã dựng xong.
2. **Cỗ máy doanh thu chạy $4-7.5k/ngày ở cuối mùa:** 45-61 cây đứng + 7-13 thú + 9-12 hands. 7 ngày cuối chi chỉ ~$721/ngày → **net +$4.6-6.7k/ngày**.
3. **59-85% số tiền final được tích lũy SAU lệnh mua thú cuối cùng** — tiền đọng không phải do "quên tiêu" mà do engine chuyển lao động thành tiền nhanh hơn mọi khoản đầu tư còn lại có thể hấp thụ.
4. **Dải 90-110k hẹp bất chấp chiến thuật khác nhau** (SpaTaro thuần bò $93-107k, Otter 22 thú $109k) = **cân bằng cung-cầu thị trường dùng chung**: 2 người cùng hút nhu cầu town → rev mỗi người $120-148k rồi bão hòa (zero-sum Q5).
5. **Kết thúc sạch:** shed cuối gần rỗng (top-3 chỉ sót 4 wool ≈ $400) — không có giá trị chết; 720 bước cố định → final = tích phân của net-rate cuối mùa.

**Cơ chế wheat của top-3 (Q3 + đo mới):** bán 574u ($19.9k, chủ yếu h0 ngay sau reset + h21), mua lại ~300u feed ($9.9k, h0-h3) → **net +$10k** — máy wheat 17-25 ô đứng (SpaTaro trồng 169 ô/mùa, replant 8.2 ô/ngày) vừa là nguồn feed vừa là kênh bán. V8 máy 13.1 ô: 149u bán + nuôi nội bộ đàn 14.

**V8 cách dải 90-110k bao xa — phân rã god-ledger (TB/trận):**

| Kênh | TOP3 | V8 | Δ | Khối lượng |
|---|---|---|---|---|
| STRAWBERRY | $42.765 (254u) | $25.477 (110u) | **−$17.288** | 43% |
| WHEAT net | +$9.959 (574u bán) | −$3.666 (149u) | **−$13.6k** | 26% |
| MELON | $15.186 (82u) | $8.948 (44u) | −$6.237 | 54% |
| CARROT | $6.041 (135u) | $359 (10u) | −$5.683 | 7% |
| FERTILIZER | $11.941 (184u) | $10.494 (171u) | −$1.447 | 93% |
| WOOL | $5.490 (53u) | $4.120 (22u) | −$1.370 | 42% |
| MILK | $21.872 (168u) | $29.883 (116u) | +$8.010* | 69% |
| EGG | $7.046 (133u) | $8.472 (188u) | +$1.426 | 141% |
| **TỔNG** | **$132.610** | **$94.675** | **−$37.935** | |

\* Milk/TOMATO/STRAW $ của v8 phồng do pool v7 — khoảng cách THẬT lớn hơn trên các kênh này ở pool top-3.

**PHÁT HIỆN MỚI LỚN NHẤT VÒNG 47 — SỤP D29 (0 hands):** v8 có gate `day < 29` (v8.py:1680) chặn toàn bộ HIRE ngày cuối → **d29 chỉ còn 1 farmer (0 hands)**, thu $2.288 vs top-3 $7.484 (9-12 hands thuê xuyên h0-h4 d29). Bàn 12 hands ngày thường → ước mất **+$3-5k/trận** cho $376 hire. Đường 5 ngày cuối: TOP3 rev d25→29 = $5.0k/$5.6k/$5.4k/$6.4k/**$7.5k** (tăng dần — top-3 cày SÁT ngày cuối); V8 = $5.0k/$7.6k/$5.8k/$13.4k (thanh lý d28)/**$2.3k** (chết d29).

#### 47.3 QUY TẮC MỚI R178-R182

- **R178 [E] — D29 LÀ NGÀY LÀM VIỆC ĐẦY, KHÔNG PHẢI NGÀY NGHỈ:** top-3 thuê 9-12 hands xuyên d29 (h0-h4, $88-143), thu $7.484 ngày cuối — *tăng dần* vào đích. Gate `day < 29` của v8 = −$3-5k/trận. Sửa: bỏ gate, d29 chạy đủ loại (harvest+bán sạch tối), hire tới khi workload cạn.
- **R179 [E] — CỪU PHẢI CÓ TỪ D0:** cừu trễ 9 ngày (AD 29 vs 71) = mất 1-2 lượt thu/con + delay wool channel. Day-0 budget thú phải là $2.000-2.500 (2 bò + 1-2 cừu + 1 ngỗng), không phải $1.100.
- **R180 [E] — RAMP ĐÀN D0-D10 PHẢI = TỐC ĐỘ TOP-3:** AD d0-10: 77 vs 41 = nguyên nhân bò AD 118 vs 168 dù đàn cuối ngang nhau (14.2 vs 13). Mua drip liên tục 0.5-1 con/2 ngày d4-18 thay vì burst d8-18; ưu tiên animal-day SỚM (bò d0 = 22 ngày sản xuất vs bò d14 = 8 ngày).
- **R181 [K] — FEED NỘI BỘ RẺ HƠN UNDERFEED:** top-3 feed 75-78% bò/cừu bằng wheat thị trường ($27-45/u, $9.9k/mùa) + chấp nhận 1-2 escape; v8 feed 99% bằng wheat tự sản ($1.7/u khi máy sống — R168). Giữ nguyên thiết kế v8, KHÔNG sao chép underfeed; điều kiện sống duy nhất = máy wheat đứng cả mùa.
- **R182 [K] — SO CHÉO POOL DÙNG KHỐI LƯỢNG (u), KHÔNG DÙNG $:** MILK $256 (v8-v7) vs $130 (top-3-mirror) — chênh 2× chỉ do đối thủ. Kết luận "thiếu $38k" phải đọc theo u: dâu 43%, wheat 26%, carrot 7%, melon 54%, wool 42%; chỉ EGG vượt (141%).

#### 47.4 PHÁN QUYẾT VÒNG 47

- **Chi đã đối chỉnh xong** ($30.3k vs $33.2k — R175 bịt hố wheat $16k của vòng 45). Toàn bộ khoảng cách $35k còn lại = **doanh thu khối lượng** (dâu/wheat/carrot/melon) + sụp d29.
- **Ba đòn định lượng được, không cần kernel mới:** R178 (d29 hire, +$3-5k) · R179 (cừu d0, +$1-2k) · R180 (ramp d0-10, +$3-6k qua animal-day sớm) ≈ +$7-13k → đưa v8 vào $75-80k. Phần còn lại ($20-30k) vẫn tụ gốc **kernel lao động MOVE 62% vs 42% + 21-23 ô chết** (R151/R164) — cần vòng kernel đúng như bàn giao Task 42-45.
- **Trả lời điều tra 90k-110k:** trần chi cấu trúc nhỏ ($27-42k) + cỗ máy $4-7.5k/ngày cuối mùa + không còn đích đầu tư + cân bằng cung-cầu dùng chung (dải hẹp) + kết thúc sạch (shed rỗng). v8 muốn vào dải: thu khối lượng 4 kênh chính lên 50-100% + cày trọn d29.

---

### 11.13 VÒNG 48 — LƯỢT FIX v8 THỨ 2 (R178/R179/R180) + GIẢI PHÂU QUÁ TRÌNH TĂNG TRƯỞNG 90K-110K THEO PHA

**Nguồn:** `bat48d/` = 10 game v8-final vs v7 (seed 100-109) + `bat48base/` = 10 game v8-cũ cùng seed (đối chứng) → god_arena 0-mismatch toàn bộ. Top-3 = `r2_god_M1/M2` (4 seat). Tool mới: `phase7.py` (bảng tăng trưởng theo pha).

#### 48.0 — QUÁ TRÌNH TĂNG TRƯỞNG 90K-110K CỦA TOP-3 (GIẢI PHÂU 4 PHA — câu trả lời "tại sao luôn đọng 90-110k")

| Pha | rev/ng | chi/ng | net/ng | Tiền cuối pha | %final tích lũy |
|---|---|---|---|---|---|
| **P1 d0-9 BOOTSTRAP** | $1,183-1,288 | $1,199-1,492 | **≈ 0** | **$13-3,884** | −3..+1% |
| **P2 d10-18 MỞ RỘNG** | $4,531-6,141 | $732-1,632 | **+$3,8-4,9k** | $35-45k | +35-47% |
| **P3 d19-25 CỖ MÁY** | $5,112-7,332 | $589-1,587 | **+$4,2-6,3k** | $73-88k | +33-42% |
| **P4 d26-29 VỀ ĐÍCH** | $5,100-7,254 | $340-987 | **+$4,7-6,8k** | $93-109k | +18-28% |

**Cơ chế từng pha:**
1. **P1 — ĐỐT HẾT VỐN ĐẦU:** 4 seat đều rút tiền về ~$0 (SpaTaro d5 còn $13, d9 $302!). Chi = thú $1,8-2,5k (d0) + LAND $3k (xong d8-10) + hạt. Máy chưa chạy → net ≈ 0. *Tiền không đọng vì mọi đô được đổi thành tài sản sinh lời.*
2. **P2 — CÔNG TẮC ĐẦU:** cây đứng 40-60 + đàn 10-13 + hands 10-11 bật đủ hơi → net +$4-5k/ngày. Riêng pha này tích lũy 35-47% final. **Đây là pha v8 yếu nhất (net +$1,5k vs +$4,4k top-3 trung bình) = nơi gap chính sống.**
3. **P3 — CỖ MÁY ĐẦY TỐC:** chi rơi về $590-1,590/ngày (không còn gì để mua) trong khi rev giữ $5-7,3k → net +$4,2-6,3k/ngày, đều như máy bơm.
4. **P4 — KHÔNG PHẠT PHINH:** chi sập còn $340-987/ngày; thuê tay tới giờ chót (HIRE cuối = d29); shed rửa sạch. **"Tiền đọng 90-110k" = tích phân của net-rate cuối mùa, không phải "quên tiêu".**

**Vì sao dải HẸP (90-110k) dù chiến thuật khác nhau:** thị trường dùng chung 2 người → cung-cầu cân bằng tại rev $120-148k/người (zero-sum Q5) + trần chi cấu trúc nhỏ ($27-42k/mùa) + 720 bước cố định.

**V8 sau vòng 48 đã có ĐÚNG hình dạng đường tiền này:** P1 net ≈ 0 (d5 $127, d9 $2,8k — đầu tư hết như top-3), P4 net +$4,6k/ngày ≈ top-3 (+$4,7-6,8k). Còn lệch ở P2 (+$1,5k vs +$4,4k) + P3 (+$3,8k vs +$5,3k) = đúng vị trí gap khối lượng (dâu 67,6u vs 254u — kernel R151).

#### 48.1 — 3 ĐÒN CHÍNH + 2 ĐÒN PHỤ (đã ship trong v8.py)

| Đòn | Sửa trong code | Kết quả đo (bat48d vs baseline) |
|---|---|---|
| **R178 d29 = ngày làm** | bỏ gate `day < 29` hire; d29 drop từ h8; d29 MỞ lại bán wheat (R175 chỉ chặn d27-28) | 12 HIRE + 13 units h22, hire $376; d29-rev $2.287 → **$3.720** |
| **R179 cừu d0** | d0: 2 bò + 1 cừu + 1 ngỗng ($1.600, giữ $1.400 hạt) + melon floor 300 d0 + sheep window w0 2→0 + buy_per_day d0 = 4 | cừu d0 **10/10 game**; Sheep-AD 29 → **57,5** (top-3: 71); WOOL $4,1k → $8-13,7k |
| **R180 ramp = tốc top-3** | cap money (1+money//900) → trajectory (bò 2+day//2, cừu 1+day//4) | AD d0-10 **41 → 62** (top-3: 77) |
| R180b van hạt sóng dâu | thú chờ (cash_floor +700) khi dâu đứng <14 trong d5-14 | chặn thú ăn vốn hạt (s100-r1: dâu d7 = 5 ô) |
| R180c thứ tự mua hạt | d5-13: dâu TRƯỚC carrot trong _seed_order | dâu được nhận tiền trước |
| R184 TẮT carrot floor | floor 8 khi đứng <8 → 0 (marg-ladder giữ) | carrot 0-6u bán được = hạt + 8-10 task nước/ngày lãng phí hoàn toàn, trả phase-2 cho melon |
| R185 melon salvage | harvest age ≥ 11 bất kể yu (cây chết tuổi 13 = 0u) | melon 6u → **19,7u** TB (s104 +$14,4k) |
| R180d milk veto | floor-6 bò chỉ khi inv MILK ≤ I0+5 & opp bò ≤ 6 | chặn đốt vốn vào kênh sữa đã tràn |

#### 48.2 — HAI BÀI HỌC ÂM TÍNH QUAN TRỌNG (R183 — 2 lần thử đều thất bại)

1. **Tier-0 watering cho carrot/melon (thử 1):** carrot ăn cap-8 `water_crit` → SEEDLING rớt tier-3 chết (R172 tái phát, 39 weed) + melon `cu>=1`-gate → tưới CÁCH NHẬT → yu không đủ 6 → chết trắng $6,6k.
2. **Tier-1/tier-2 watering (thử 2):** phase-1 BÃO HÒA — service bỏ đói (MILK −$8k, WOOL −$5k/mùa).
3. **KẾT LUẬN R183:** kernel MOVE 62% không có dư địa ưu tiên hóa — mọi task mới CẮT task cũ. Carrot/melon phải sống bằng tier-3 + salvage. Gap carrot/melon/dâu = việc của VÒNG KERNEL (R151/R164), không phải quota/tier.
4. **PHÁT HIỆN MỚI (R186) — SHOP-DRAW LÀ PATH-DEPENDENT:** `_spawn_weeds` tiêu thụ RNG theo số ô TRỐNG mỗi ngày → farm-state khác nhau = dòng RNG khác = **thứ tự shop unlock khác nhau**. s100: baseline bốc 5 milk-shop (milk $310/u), v8-mới bốc 2 (milk $61/u) — cùng seed! → đo battery PHẢI đa seed + so trung bình, không so 1 game; var giữa seed = shop-luck lớn hơn var chiến thuật.

#### 48.3 — KẾT QUẢ BATTERY (10 seed 100-109, seedB = mirror seedA — mỗi seed 1 game)

| | final TB | thắng | ghi chú |
|---|---|---|---|
| v8-cũ (baseline) vs v7 | $51.258 | 4/10 | s101/102/109 sập $30-36k |
| **v8-mới vs v7** | **$61.454 (+$10.196 / +19,9%)** | **10/10** | s100 là town 2-milk-shop (cả 2 người đói, v8 thắng sát $425) |
| **v8-mới vs v6** | **$65.849** | **8/10** | s105/108 thua sát |

#### 48.4 QUY TẮC MỚI R183-R186

- **R183 [K] — PHA-1 BÃO HÒA:** mọi nâng ưu tiên tưới cây non-melondâu đều giết service hoặc seedling. Chỉ 2 nguồn được tier-0: event-dâu + seedling (status quo từ v8f).
- **R184 [E] — CARROT LÀ KÊNH CHẾT với kernel hiện tại:** floor-8 = lãng phí hạt+nước (0-6u bán). Chỉ mở lại sau vòng kernel.
- **R185 [E] — SALVAGE > CHẾT TRẮNG:** cây sắp hết lifespan → thu bất kể yu (melon age≥11).
- **R186 [K] — SHOP-LUCK PATH-DEPENDENT:** so sánh phiên bản bắt buộc ≥10 seed; 1 game = 1 điểm dữ liệu shop-luck, không phải chân trị.

#### 48.5 PHÁN QUYẾT VÒNG 48

- Ba đòn R178/R179/R180 + 2 đòn phụ đã đưa v8: **$51,3k → $61,5k (+20%), 4/10 → 10/10 vs v7** — vượt mục tiêu ước tính +$7-13k phần dưới. Hình dạng đường tiền giờ KHỚP top-3 (P1 đốt vốn hết / P4 net +$4,6k).
- Còn cách $90-110k: P2 net +$1,5k vs +$4,4k + P3 +$3,8k vs +$5,3k = **gap khối lượng dâu (67,6u vs 254u) + melon (19,7u vs 82u)** — đúng chẩn đoán vòng 47: tụ gốc kernel MOVE 62% + 21-23 ô chết. Vòng tiếp theo nếu user yêu cầu = VÒNG KERNEL (R151/R164), không phải thêm quota.

## 11.14 VÒNG 50 — ĐIỀU TRỊ "THUA ĐẬM v6" (R188-R193)

Task: user báo "v8 đẩy 74k vs v7, v6 có trận 87k, nhưng tỷ số thua v6 vẫn cao,
nhiều trận thua đậm — rà soát nguyên nhân từ code".

### 50.0 — CHẨN ĐOÁN (battery 20 seed 100-119: 15/20, avg $64.842; 4 trận thua đậm)

God-replay 0-mismatch 4 trận thua đậm (s118 $24.071 / s114 $46.971 / s111 / s108)
+ 2 trận thắng đối chứng, phân rã kênh god-ledger + action-level theo giờ:

| GAP (thua − thắng) | Định lượng | Cơ chế |
|---|---|---|
| **#1 MELON wave-1** | −$8,5-16,4k/trận | v6 d0 mua 14 hạt melon + 0 thú → thu $11,8-18,5k ngay d11; v8 chỉ 8 hạt ($1.600 starter thú ăn vốn + luật 45% fast-crop cắt 1 hạt) → $1,6-6,7k |
| #2 MELON chết dây chuyền | −$8-14k ở game xấu | 12 ô đứng d0-9 → chết/d8-10 khi tier tưới melon = 3 thua service/harvest tier 2 (s132/146/123) |
| #3 WOOL mix | −$1,7-6,8k | v6 giữ 6 cừu (WOOL $200/u) vs v8 đứng 4 (floor + thứ tự cắt cap ưu tiên cừu bị cắt trước) |
| #4 DÂU trễ | −$2,4-4,1k | v6 trồng dâu d5 (bán d21 $3-11,9k), v8 d7-10 (bán d22+); shed wheat 39u ngồi im vì HOLD $37,5 |
| #5 WHEAT cutoff | −$3-8k khi spiral | v8 P10 wheat d24 (chín 1 mứ, 7 task/ô $25-35/task) cướp nước của dâu → s118: 22 ô dâu chết trắng d24-27 |

Lưu ý quan trọng (loại nghi phạm): wheat NET v8 −$5,7-6k vs v6 −$1,1-4k **không phải
gap trực tiếp** — v6 mua $35-36,5k chỉ để bán lại $31-35k + feed đàn; chênh lệch
thực = chi feed, không phải lỗ giao dịch. Gap thật nằm ở doanh thu khối lượng.

### 50.1 — 5 ĐÒN FIX (R188-R192) + 1 đòn loại bỏ (R193)

| Rule | Thay đổi | Kết quả đo |
|---|---|---|
| **R188/b MELON-14** | starter 2C+1S+1G → **1C+1S+1G** ($1.200); quota d0 wheat 14→10 + carrot 8→2 + **MELON 14**; TẮT nhánh CUT của luật 45% fast-crop d0-1 | 50a (0 bò) MILK −$22k ở game 5-milk-shop → 50b giữ 1 bò: s118 $24.071 → $71.071 |
| **R189 WHEAT HOLD SỚM** | HOLD wheat 1.50 → 0.90 khi d≤11 (bán vụ d4-6 nuôi vốn hạt dâu d5) | An toàn: đàn v6 d≤10 còn 0-4 con chưa hút feed (R162 chỉ binding d12+) |
| **R190 WHEAT CUTOFF** | seed-buy refill + fill-law wheat: d26 → d21 | Dâu d22-26 được trả lao động tưới/thu (s118-type spiral hết) |
| **R191 CỪU-6** | trajectory cừu 1+day//4 → 1+day//3; thứ tự cắt cap: ngỗng→bò→cừu (cũ cừu trước) | WOOL s100 $7.024 → $11.191 |
| **R192 MELON SURVIVAL** | ô melon cu≥1 trong cửa sổ chín → T_WATER_CRIT tier-0, budget riêng cap 4/h (không đụng cap seedling 6/h) | s132 $39.743 → $67.454; s146 $42.281 → $49.066 |
| ~~R193 thu d10 + cargo-rush~~ | **LOẠI BỎ**: thu age≥10 mất unit cuối ô fertilized + rush giữa ngày tốn lao động — battery 15/20 $64.919 < R192 15/20 $66.478 (s117 −$16.6k) | trở lại age 11 của R185 |

### 50.2 — KẾT QUẢ BATTERY CUỐI (bản R192, 50 game vs v6 + 10 game vs v7)

| Battery | v8 thắng | v8 TB | đối thủ TB | tệ nhất |
|---|---|---|---|---|
| seeds 100-119 vs v6 | 15/20 | $66.478 | $61.178 | $47.395 |
| seeds 120-149 vs v6 | **28/30** | $68.278 | $59.310 | $45.560 |
| **TỔNG 50 seed vs v6** | **43/50 (86%)** | **~$67.180** | ~$60.120 | $45.560 |
| seeds 100-109 vs v7 | 9/10 | $62.458 | $51.139 | $49.590 (s107 thua sát $1.706) |

So vòng 48 (baseline): vs v6 8/10 (không có battery lớn), avg $65.849, tồn tại
trận sập $24-25k. Vòng 50: **tỷ lệ thắng 75% → 86%, avg +$1.3-3.4k, xóa sạch
trận thảm họa** (tệ nhất $45.6k / biên thua tệ nhất −$10.7k so với −$17.4k).

### 50.3 QUY TẮC MỚI R188-R193

- **R188 [K] — D0 LÀ BÀI PHÂN BỔ VỐN, KHÔNG PHẢI BÀI THÚ:** $1 vào melon d0 trả
  ~$6-13 ở d11; $1 vào thú d0 trả sau d8-15 và phụ thuộc shop-luck. Cân bằng
  đúng: 1 bò + 1 cừu + 1 ngỗng ($1.200) + 14 melon ($1.120) + 10 wheat + 2 carrot.
- **R189 [E] — HOLD THƯƠNG MẠI PHẢI THEO PHA ĐỐI THỦ:** ngưỡng bán cao (chống
  thuế R162) chỉ đúng khi đối thủ đang hút hàng; cửa sổ đối thủ chưa vào kênh
  thì bán rẻ nuôi vốn là đúng.
- **R190 [E] — LAO ĐỘNG ENDGAME QUÝ HƠN THÊM 1 MỨ WHEAT:** hạt planted d22+
  = 7 task/ô cho $150-240; harvest dâu d22-26 = 1 task cho $120-180. Cắt ở d21.
- **R191 [K] — SLOT ĐÀN 13-14 PHẢI VỀ KÊNH ĐẮT NHẤT (WOOL $200/u):** thứ tự
  cắt khi vượt cap quyết định $4-7k/trận.
- **R192 [K] — TIER-0 CÓ THỂ MỞ CARVE-OUT AN TOÀN:** phản例 R183 không tuyệt
  đối — budget riêng + điều kiện hẹp (cu≥1, đúng loài, cap/giờ) cho phép nâng
  ưu tiên không giết pha-1. Công thức: task chỉ sinh ra khi THẬT SẰP mất giá trị.
- **R193 [ÂM] — GIÁ SLOT BÁN SÁNG KHÔNG ĐÁNH ĐỔI UNIT CUỐI:** thu sớm để kịp
  d11-h0 ($236+) nhưng mất unit thứ 6 của ô fertilized + tốn lao động rush —
  lỗ ròng. (Ghi chú: giao trễ melon d11-h23/d12 vẫn là gap nhỏ $3-5k/game,
  cần vòng kernel để phục vụ 2 việc cùng lúc.)

### 50.4 PHÁN QUYẾT VÒNG 50

- "Thua đậm v6" = 5 lỗi cấu trúc chồng nhau, không phải 1 bug: vốn d0 lệch
  (melon), tier tưới melon, mix cừu, HOLD wheat sớm, wheat cutoff. Sửa 5/5
  cấu trúc → 86% thắng, tệ nhất +$21k so với trước.
- Còn lại: s123-type (game path-dependent xấu cả 2) và gap melon-giao-trễ
  $3-5k — đều cần vòng kernel (R151/R164) hoặc chấp nhận variance.
- v9/kain41 vẫn搁置 theo chỉ thị; không đụng v7 (KAIN champion) và v6
  (orchestrator — đối thủ chuẩn đo).

## 11.15 VÒNG 52 — ĐỐI CHIẾU STYLE v8-VÒNG-50 vs TOP-3 + PHÂN TÍCH CÔNG-THỦ (FERT = bài học mới)

Task: user yêu cầu (1) đo lại các chỉ số xem v8 đã khớp top-3 chưa, (2) đánh giá chiến
lược công-thủ của top-3 — bài học mới / thiếu sót còn tồn tại với v8, (3) báo cáo.

Phương pháp: battery mới 8 seed TRẰNG (200-207, chưa từng dùng — tránh overfit đường
RNG theo R186), v8 vòng-50 (R188-R192) vs v6, god-replay 8/8 game 0-mismatch 719 turns
→ phase8.py (B1 style + B2 pha + B3 công-thủ) + đếm op đồng-ruộng từ replay gốc.

### 52.0 — KẾT QUẢ BATTERY MỚI (seeds 200-207, v8 vs v6)

7/8 thắng ($61.4k–74.0k), 1 thua sát (s207: 50.037 vs 51.235, −$1.2k).
v8 TB **$64.841** | v6 TB $56.441. Nhất quán battery 50-game vòng 50 (86%).

### 52.1 — B1 KHỚP CHỈ SỐ: ĐÃ KHỚP GÌ, CÒN THIẾU GÌ

**✅ ĐÃ KHỚP / VƯỢT (so 4 seat top-3):**

| Chỉ số | TOP-3 | v8 vòng-50 | Ghi chú |
|---|---|---|---|
| Cấu trúc chi | $33.2k | $31.9k | khớp — vòng 45-50 đã vá xong hố chi |
| LAND 4 ô / $3k | 4 / $3k | 4 / $3k | khớp tuyệt đối |
| P1 d0-9 net/ngày | −$138 | −$117 | **KHỚP** — đốt vốn đúng chuẩn |
| P4 d26-29 net/ngày | +$5.652 | +$6.578 | **VƯỢT** — endgame v8 tốt hơn |
| Shed cuối trận | sạch | sạch (0 leftovers) | v8 sạch hơn (top3 còn 4 WOOL) |
| FEED/CARE/COLLECT_FERT | ~263/243/292 | 254/245/244 | khớp ~100% |
| MELON units | 81.8 | 69.6 | 85% — R188 melon-14 + R192 đã closer |
| TOMATO units | 38 | 28.8 | 76% |
| WOOL $ / EGG units | $5.5k / 133 | $13.0k / 150.6 | **VƯỢT** (R191 cừu-6) |
| Tổng $ động vật | $34.4k | $46.5k | **VƯỢT** — MILK premium 1.47 vs 0.81 |
| Trốn thú / feed-cov | 1-2 con / 75-78% | 0 / 94-99% | **VƯỢT** — thiết kế an toàn đúng |

**❌ CHƯA KHỚP (gap $37.5k/trận = final $102.4k − $64.8k):**

| Chỉ số | TOP-3 | v8 | Gap → tiền |
|---|---|---|---|
| STRAWBERRY units | 254.5 | 62.0 | **−$28k/trận — gap số 1** |
| WHEAT máy resale | 574u (net +$10k) | 120.5u | −$10k net |
| CARROT units | 135 | 2.2 | −$6k (kênh bị R184 bỏ) |
| WATER ops | 1.188 | 610 | 51% — gap nhân lực số 1 |
| HARVEST ops | 484 | 200 | 41% |
| FERTILIZE ops | 130 (92-186) | 40 | **31% — BÀI HỌC MỚI, xem 52.3** |
| MOVE ops (share) | 2.963 (37%) | 4.842 (63%) | 1.900 op đi lại thừa |
| P2 d10-18 net/ngày | +$4.489 | +$1.358 | × 9 ngày = **−$28k — nơi mất tiền chính** |
| P3 d19-25 net/ngày | +$5.391 | +$3.496 | × 7 ngày = −$13k |
| d29-rev | $7.484 | $5.135 | đang khớp dần (v48: $3.720) |
| AD d0-10 | 77 | 41.8 | mua thú sớm ít hơn (melon-14 đổi vốn) |

Phân rã nhất quán: gap $37.5k ≈ P2 (−$28k) + P3 (−$13k) − lợi P4 (+$4k).

### 52.2 — B2 ĐƯỜNG TĂNG TRƯỞNG 4 PHA

| Pha | TOP-3 rev | v8 rev | TOP-3 net/ng | v8 net/ng | phán quyết |
|---|---|---|---|---|---|
| P1 d0-9 | $12.3k | $5.8k | −$138 | −$117 | ✅ khớp (đốt vốn) |
| P2 d10-18 | $50.6k | $28.1k | +$4.489 | +$1.358 | ❌ **gap chính** |
| P3 d19-25 | $44.9k | $31.4k | +$5.391 | +$3.496 | ❌ gap phụ |
| P4 d26-29 | $24.8k | $28.5k | +$5.652 | +$6.578 | ✅ vượt |

→ v8 đã đóng xong 2 đầu (P1 đốt vốn chuẩn, P4 về đích sạch), toàn bộ khoảng cách
còn lại nằm ở **P2 "MỞ RỘNG"** — cỗ máy chưa đạt tốc độ maximal d10-18.

### 52.3 — B3 CÔNG THỦ: KHÔNG CÓ CHIẾN TRANH THỊ TRƯỜNG — CHỈ CÓ CÔNG SẢN XUẤT

**Kết luận công-thủ (đo trên giờ + giá + khối lượng):**

1. **KHÔNG tồn tại tấn công thị trường** ở top-3 (xác nhận lần 3, lần này bằng phân
   tích giờ): mua wheat đều đặn $300-600 MỖI NGÀY d0-28 (nuôi đàn + máy resale, không
   có spike nhắm giờ); bán rải đều h13-h20 + đỉnh h0/h21-23; không có dump nhắm giờ
   đối thủ sắp bán. Engine price = f(inventory chung) cho phép "đánh" nhưng top-3
   KHÔNG dùng — hoặc vì tự hại, hoặc vì zero-sum khiến nó vô nghĩa.
2. **Phòng thủ top-3** = (a) feed-stock wheat liên tục; (b) mua thêm FERTILIZER
   $1.226/trận khi đàn thu không đủ bón; (c) shed sạch cuối. v8 làm (a)+(c) tốt hơn
   (0 trốn thú, feed-cov 99%), chỉ thiếu (b) — và đây là phát hiện lớn nhất vòng này.
3. **v8 bán đúng giờ giá cao**: h0 gánh $55k/94k rev (59%), premium dâu 2.125 × base
   vs top-3 1.4 (thị trường v8-vs-v6 ít bão hòa hơn top3-vs-top3 — khác môi trường,
   không so thẳng).

**BÀI HỌC MỚI — FERT = BỘ NHÂN ĐÔI HIỆU QUẢ WATER (phát hiện quan trọng nhất vòng 52):**

Cơ chế engine (dòng 441 + 798): tưới trong cửa sổ chín trên ô FERTILIZED (kéo dài 3
ngày) → **+2 units thay vì +1**. Hệ quả theo cây (tham số engine):
- **MELON**: 6u cần 6 lần tưới → với FERT chỉ 3 lần. Tiết kiệm 3 WATER + ~6 MOVE
  tương ứng/ô → giải phóng lao động cho dâu.
- **CARROT**: window chỉ 2 ngày (age 2-3) → không FERT tối đa 2u/ô (R184 "kênh chết"
  là KẾT LUẬN ĐÚNG CHO KERNEL KHÔNG FERT), có FERT = 4u/ô → top-3 135u × $45 ≈ $6k.
  **CARROT KHÔNG CHẾT — CHỈ THIẾU FERT. R184 cần ghi đè có điều kiện.**
- **STRAWBERRY** (ongoing, interval 2): FERT giúp chạm cap 4u sau 2 ngày sản xuất thay
  vì 4 → cây chết sớm → **trồng lại chu kỳ 2** → top-3 plant 237-274 lần vs v8 178.
- **Tài nguyên FERT của v8**: thu 244 FERT/game từ đàn (COLLECT_FERT khớp top-3!) nhưng
  FERTILIZE chỉ 40 lần → **BÁN ~200 FERT ở $64** trong khi bón vào melon/carrot/dâu
  trị $180-810/ô. v8 đang bán nguyên liệu chiến lược giá rẻ!

**THIẾU SÓT v8 CÒN TỒN TẠI (xếp theo $):**
1. MOVE 63% vs 37% — kernel lao động (R151/R164 đã biết, giờ quantify chắc: 4.842 op
   đi lại, dư ~1.900 op so top-3 ≈ ~900 WATER bị mất) — gốc của gap dâu 62u vs 254u.
2. **Chiến lược FERT vắng hoàn toàn** (0 mua + bán 82% lượng thu) — lỗ hổng mới tìm
   thấy, có thể fix KHÔNG cần đụng kernel: tái phân bổ FERT đang bán → bón.
3. P2 cỗ máy +$1.4k/ng vs +$4.5k — hệ quả của (1)+(2).
4. HIRE v8 $8.4k vs top-3 $6.4k — 317 vs ~250 lượt: thừa ~$2k lao động低 hiệu quả
   (triệu chứng của MOVE 63%, không phải lỗi độc lập).

### 52.4 ĐỀ XUẤT VÒNG 53 (nếu user duyệt — chưa tự ý triển khai)

| Đòn | Nội dung | Ước tính |
|---|---|---|
| R194 FERT-KEEP | tắt bán FERT khi có ô melon/carrot/dâu trong/chuẩn window; bón trước ngày window | chuyển 200 FERT từ $64/u → $180-810/ô |
| R195 CARROT-FERT | hồi sinh carrot: trồng + bón khi tồn FERT (2 nước = 4u) | +$3-6k/trận |
| R196 MELON-3-NƯỚC | bón melon đầu window → 3 nước chạm 6u, dư lao động cho dâu | giải phóng ~18-24 op/ô |
| R197 DÂU CHU KỲ 2 | bón dâu ngày sản xuất → chết sớm → replant | cần đo thêm |

## 11.16 VÒNG 53 — TRIỂN KHAI R194-R197: 5 BIẾN THỂ, 138 GAME, KẾT LUẬN ÂM (FERT BỊ CHẶN BỞI KERNEL)

Task: user duyệt triển khai R194-R197 ("v8 mới học bề ngoài, chỉ số chưa khớp") + chạy
thực nghiệm ngay. Đã triển khai đủ 4 đòn + 1 đòn gia tăng (R198), 5 biến thể a-e, tổng
138 game battery (8 trắng 200-207 + 20 chính 100-119 A/B sạch + 30 ext 120-149 + ablation).

### 53.0 — CÁC BIẾN THỂ VÀ KẾT QUẢ (v8 seat A vs v6)

| Biến thể | Cấu hình | Battery | Kết quả | Phán quyết |
|---|---|---|---|---|
| 53a | đủ 4 đòn, dâu+melon FERT **tier 1** (sfert 6/h, mfert 4/h) | trắng 200-207 | 2/8, $58.752 | SỤP — service đàn chết |
| 53b | tier về 2, keep theo "need" (~30 FERT/ngày kể cả wheat) | trắng 200-207 | 7/8, $62.630 | −$2.2k vs vòng-50 |
| 53c | keep CỨNG 8 + carrot floor 6 + melon ws-1 tier2 + dâu tier2 cap6 | 100-119 + trắng | 16/20 $68.092 (+$1.6k) / 5/8 trắng $65.868 | tốt NHƯNG variance lớn |
| 53d | 53c bỏ carrot floor (ablation) | 100-119 | 16/20 $66.927 | floor NET DƯƠNG (+$1.2k, thua 13/20 cặp) |
| 53e | 53c + wheat-rescue tier1 cap 4/h (R198) | 100-119 | 6/20 $58.720 | THẢM HỌA — luật R183 lần 3 |
| 53c (ext) | kiểm chứng độc lập | 120-149 | 23/30 $64.881 | REGRESSION vs 28/30 $68.278 |

**TỔNG 58 game so trực tiếp: 53c 44/58 (76%) vs vòng-50 50/58 (86%) — REVERT về
vòng-50 (md5 bc0d5523, s100=$59.798 bit-perfect).**

### 53.1 — BA LUẬT ÂM MỚI (bổ sung R183)

1. **R183-lần-2 (53a)**: FERTILIZE tier-1 cướp giờ CARE/FEED của đàn — care
   9.8 → 7.0/ngày, WOOL −67u (−$13k), MILK −36u; battery 2/8 $58.752.
   Tier-1 LÀ CỦA SERVICE. FERT giữ tier 2.
2. **R198 (53e)**: carve-out wheat-rescue tier-1 cap 4/h = 96 task/ngày tràn
   phase-1 (wheat cu≥1 là trạng KINH NIÊM dưới phase-2 bão hòa, không phải
   sự kiện cấp tính như melon R192) — 6/20 $58.720. Không cứu wheat bằng tier.
3. **R194-upper (53b)**: giữ FERT > 8 = hàng chết — kernel thực thi chỉ
   ~2.7 FERTILIZE/ngày (đo: supply 15-20/ngày, thực thi 59-72/mùa). Need-
   based keep ~30/ngày → −$3.2k tiền mặt d6-14 → cascade hạt/thú (s202 −$23k).

### 53.2 — PHÁT HIỆN BIÊN KERNEL-FERT (quan trọng nhất vòng 53)

Cơ chế FERT đúng như lý thuyết (engine +2u/lần tưới trên ô fertilized; dâu
event nước+fert = +2u chạm vách 4u sau 2 event → 8u/cây; carrot 2 nước = 4u;
melon 3 nước = 6u + thu sớm d8) — các seed thắng cho thấy đủ: s103 +$17.9k,
s105 +$20.9k, s107 +$17.9k, s111 +$12.7k, s119 +$24.3k, dâu bán +10-13u,
carrot +20-40u.

NHƯNG: mỗi lệnh FERT cần 1 unit-hour + pickup trip; ngân sách phase-1/2 chỉ
hấp thụ ~2.7 lệnh/ngày. Mọi biến thể vượt biên này đều triệt hạ 1 trong 3
trụ khác (service đàn / máy wheat / dòng vốn hạt) vì **kernel 62%-MOVE đã
chạy sát 100% công suất** (xác nhận định lượng R151/R164). Cái chết của
máy wheat d16-24 (s112: 18→2 đứng, WEED 24; s149: 14→3, WEED 24) là triệu
chứng cuối: phase-2 không còn 1 slot dự phòng nào.

### 53.3 — PHÁN QUYẾT & ĐƯỜNG TIẾP

- v8 CHÍNH THỨC = VÒNG 50 (R188-R192, 43/50 = 86%, $67.4k) — R194-R198 ghi
  luật âm, KHÔNG deploy. Điểm mạnh 53c (peak $84.6k s107, avg +$1.6k trên
  100-119) không đủ bền qua 58 game.
- Gap còn lại tới top-3 ($67k vs $102k) KHÔNG thể đóng bằng tài nguyên FERT
  hay chiến lược bón — cần tái cấu trúc KERNEL lao động (MOVE 63% → ~37%):
  giảm chiều dài trung bình mỗi op (layout gia-tốc/shed gần), batching
  pickup/deliver, hoặc giảm tổng op qua cycle nhanh hơn. Đây là phạm vi v9
  (user đã quyết không deploy v9 ở giai đoạn này).
- Tools mới: bat53*.py (a-f) + new53/new53b/new53d/new53e/new53f/new53r50
  (jsonl đầy đủ 138 game + A/B sạch round-50) — chuẩn đối chứng vòng sau.
