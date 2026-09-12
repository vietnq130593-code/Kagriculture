# PHÂN TÍCH NOTEBOOK "Kaggriculture Master Engine V3" (guruprasaathas111)

> Nguồn: https://www.kaggle.com/code/guruprasaathas111/kaggriculture-master-engine-v3
> Ngày phân tích: 12/09 (Task 56) · Tái dựng thành công toàn bộ main.py 285KB/2.356 dòng từ chuỗi Base85 nén

---

## 1. METADATA NOTEBOOK

| Mục | Giá trị |
|---|---|
| Tác giả | Guru Prasaath S |
| Đăng / cập nhật | 2026-09-12 (v9 cuối cùng, chạy lần cuối 2026-09-09) |
| Lượt xem / vote / copy | 997 / 56 / 55 |
| **Public Score** | **600.0** |
| **Best Score** | **2712.8 V3** |
| License | Apache 2.0 |
| Ngôn ngữ / runtime | Python, 16s |
| Cell | 2 markdown chiến lược + 1 cell tái dựng agent (Base85+zlib) + 1 cell verify |

**Bản chất**: notebook tổng hợp (synthesis) toàn bộ meta public của competition — "Unified Winning System" tự claim 95.1% win rate, +17.5M net margin.

---

## 2. CHUỖI CỐI NGUỒN (attribution từ header code)

Tape gốc = **Thomas Tschinkel — "Kaggriculture: 93.8% Win Rate Public State Router" v3** (scriptVersionId 347936183).
Các lớp phủ (overlay) mua/ghép từ các notebook public khác:

1. **yhay81 / shop-router-0909**: 13 tape 719-turn + bản đồ shop-pair → route
2. **aurax7 / Reactive Router**: sale timing + shed projection
3. **Dmitrii Gluzdov / E184 + E182**: lookahead sale horizon + terminal physical closure planner
4. **prvsiyan / Frontier v34 (V221B, V224C)**: adaptive production — cattle switch, SE sheep paddock, sales-first
5. **Ahmed Berat Ozer / V35 (EXP-154…173)**: game-theoretic engine — R37 giá phi tuyến, fingerprint, R44 mirror probe, V219/V231/V233/V234, R51/R53
6. **leoprovorov / Two Coins Mirror Counter**: cash-response probe (R44)
7. **lucifer19 / Harvest Nocturne**: rivalry features (R37)
8. **tetsutani**: weed_dig, projected shed

→ Đây là "meta tối thượng" của mặt trận public vào giữa tháng 9.

---

## 3. KIẾN TRÚC — "ONION" 20+ LỚP TRÊN NỀN ROUTE-TAPE

```
Chassis (replay tape 719 turn) 
  + hand_align / weed_repair / sell_lead / front_run / budget_guard / room_guard / clamp_sells / dead_stock / terminal_liquidation
+ R42 opening (turn 0: BUY WHEAT 13 + BUY 30 + SELL 30 — tự arbitrage nâng giá rồi bán)
+ terminal rescue (step 718 full dump)
+ shadow terminal planner (E182, simulate từ step 712)
+ room_guard (h23: shed+tồn mang ≤ 99 → thêm SELL)
+ V219 late-investment (d18+: BUY_LAND + TOMATO-10 + hire theo ngày)
+ V224 sales-first ordering (d12+)
+ V231 cattle switch (step 216-227: SHEEP→COW khi milk-shops ≥2 & MILK≥WOOL)
+ R36 multi-turn sale window (d12-28: bán trước 2-3 turn, debt ledger chống bán kép)
+ R37 quote priority + rival fingerprint (≥90% giống nhau → mirror)
+ R44 mirror probe (bán all-SELL probe, đo phản ứng tiền → mở window 4 turn)
+ V233 SE sheep paddock (d12: BUY_LAND SE + 6 SHEEP + 2 hands riêng, điều kiện WOOL≥$220 & ≥2 YARN_STORE)
+ V234 emergency feed rescue (mua WHEAT khi đàn đói, cap 6/ngày)
+ R51 FERT-input workers (mua FERT rẻ ≤$30, bón cây đang cửa sổ tưới)
+ R51 warehouse close + R53 labor assignment (d26-28: 2-3 worker sweep hàng bón phân)
= agent cuối (mọi lớp fail-safe → PASS, không bao giờ raise)
```

**Router 13 route**: tại step 144 (d6) đọc `town.unlocked_shops` → map 16 cặp shop → route 0-12; tại step 648 (d27) chuyển route 2 (terminal). Patch route = đột biến vài trăm turn của tape gốc.

---

## 4. XÁC THỰC THAM SỐ GIÁ (R37) — KHỚP 100% ENGINE

`_R37_MARKET_PARAMS` (base/I0=10000/T/below_func/above_func/target 9 mặt hàng) **trùng tuyệt đối** với `MARKET_PARAMS` của kaggle-environments 1.32.7. Agent tính giá chính xác từng đơn vị → quote priority, front-run, debt ledger đều trên đường giá THẬT.

---

## 5. KẾT QUẢ ĐỐI ĐẤU TRỰC TIẾP (chạy engine thật, kaggle-environments 1.32.7)

### 5.1. kme3 (Master Engine V3) vs v10 của chúng ta — 16/16 trận, 2 ghế × 8 seed (100-107)

| | kme3 | v10 |
|---|---|---|
| TB | **$142.737** | $37.618 |
| Min | $72.819 (s106) | $4.957 |
| Max | $181.646 (s103) | $60.705 |

### 5.2. kme3 vs v6 (seed 100-107): **8/8**, TB **$165.769** (min $147.612, max $182.178)
### 5.3. kme3 vs melon_maxxer s100: $172.495 vs $5.269
### 5.4. kme3 self-play (validation episode kiểu Kaggle): $78.443 / $97.812 — đúng khoảng top leaderboard thực chiến ($90-110k) khi cả hai đều mạnh

**Kết luận sức mạnh**: vượt hẳn top-3 chúng ta từng phân tích (90-110k khi đánh nhau với nhau). Đây là **sparring partner hoàn hảo + mã nguồn đầy đủ**.

---

## 6. LỊCH TRÌNH KINH TẾ CỦA TAPE (route 0) — "NHÀ MÁY 2×"

### 6.1. Đầu tư
- Hạt: 163 WHEAT + 33 STRAWBERRY + 31 CARROT + 12 MELON = **$6.510**
- Đàn: **17 con** = 8 COW ($3.200) + 6 SHEEP ($3.000) + 3 GOOSE ($900) = $7.100 — MUA SỚM: d0 2C+2S, d2-3 +2C, d6-7 +4C, d8-9 +4S, d10-11 +3G → **đủ 17 con từ d11**
- Đất: 2 BUY_LAND (NE $1.000 + SW $2.000) — 3 quadrant
- Mua WHEAT ngoài: 43 (R42) + 155 d0-11 (feed trong lúc máy wheat chưa lên)
- Mua FERTILIZER: 46u rẻ (≤$30) d6-29 để BÓN (không bán)
- HIRE: 260 lệnh cả mùa (~8-11 hands duy trì)

### 6.2. Máy sản xuất (719 turn, farmer + hands)
| Op | kme3 tape | top-3 replay (đo trước) | v10 ta |
|---|---|---|---|
| WATER | **1.102** | ~1.187 | 629 |
| HARVEST | **475** | ~484 | 245 |
| CARE | 417 | — | — |
| FEED | 367 | — | — |
| COLLECT_FERTILIZER | 367 | — | — |
| PLANT | 239 (W163/S33/C31/M12) | — | — |
| FERTILIZE | 61 | 130 | 40 |

WATER ramp: d0 19 → d6-10 30-40/ngày → d11-27 34-62/ngày. **Đúng profile top-3** — xác nhận lần 3 chẩn đoán "nút chặn = KERNEL-OPS".

### 6.3. Nhịp bán (cadence) — "giọt nhỏ đều tay"
- Mỗi ngày bán **lot nhỏ trên MỌI mặt hàng**: WHEAT 1-3, FERT 1-10, MILK 1-6, WOOL 1-4, EGG 1-3, STRAWBERRY 1-9, MELON 6 (chỉ d10), CARROT 2-11 (d27+)
- D29: **dump toàn bộ** (W11/C10/M9/E9/F10/S7/W10/T6/M6)
- Giá đạt được vs v10 (s103): STRAWBERRY $227-248, WOOL $215-238, MILK $133-247 — giữ tồn thị trường 9.600-9.800 (vùng premium) cả mùa

### 6.4. Đường tiền (vs v10, s103)
d10 $19k → d18 $63k → d24 $127k → d28 $160k → final **$181.6k** (tăng ~$10-11k/ngày suốt nửa sau)

---

## 7. CƠ CHẾ THỜI GIAN / THÔNG MINH ĐẶC BIỆT (đáng học nhất)

1. **R42 turn-0 self-arbitrage**: BUY 13 + BUY 30 wheat đẩy giá lên rồi SELL 30 tại giá nâng — kiếm chênh lệch trên chính đơn của mình + để lại 13-26 wheat feed.
2. **sell_lead**: khi `step % 4 != 0` (không có town drain giữa 2 turn) kéo lệnh SELL của turn sau lên NGAY — đi trước 1 bước.
3. **R36 debt ledger**: d12-28 bán TRƯỚC 2-3 turn (4 turn nếu phát hiện mirror clone) số hàng tape định bán, ghi "nợ" để trừ đúng khi đến hạn — không bao giờ bán kép.
4. **R37 quote priority**: khi có nhiều SELL cùng turn, bán TRƯỚC mặt hàng có doanh thu dễ tổn thương nhất trước batch đối thủ (tính bằng đường giá thật + batch ước tính 8-24u từ yield đứng của đối thủ trên public tiles).
5. **R44 mirror probe**: tung all-SELL probe $100+ giữa d14-26, nếu đối thủ "ăn theo" đúng lượng → xác nhận mirror clone → nới window lên 4 turn.
6. **V224 sales-first**: d12+ SELL đứng đầu hàng market orders (đảm bảo fill trước khi hết slot).
7. **Fingerprint đối thủ** (≥90% giống tile) — chống self-play, chỉ dùng public info.
8. **room_guard h23**: shed + hàng mang > 99 → SELL thêm tránh tràn.
9. **V231 cattle switch**: d9-10, nếu ≥2 milk-shop, không YARN_STORE, giá MILK ≥ WOOL → đổi lệnh mua SHEEP thành COW (cap 4).
10. **V233 SE sheep paddock**: d12 nếu WOOL ≥ $220 & ≥2 YARN_STORE → mua đất SE + 6 cừu + 2 worker riêng chuyên trị 6 ô (feed/care/harvest/collect), có V234 cứu đói (mua wheat ≤6/ngày).

## 8. HỌC THUYẾT KINH TẾ (từ cell "Economic Policy")

- Mục tiêu là **B_T(p) − B_T(1−p)** (đối kháng tương đối, không phải tuyệt đối).
- **Định lý order timing**: bán x đơn trước block q của đối thủ (không phản ứng) → swing mục tiêu = **2×** tổng bậc giá δ_r — lợi mình = thiệt đối thủ, hệ số 2.
- **Định lý withholding**: giữ hàng nâng giá cho CẢ HAI — nếu đối thủ là người bán nhiều hơn trong window, withhold là **chuyển tiền cho đối thủ** → chỉ khi mình mới là nguồn cung lớn.
- Ưu tiên từ điển: feed > nước sắp chết > thu hoạch cuối > dỡ cuối; tăng trưởng chỉ dùng lao động dư.
- Công thức hire: `H* = min(ceiling(d), max(floor, ⌈(J + 2R)/7⌉))`, trần 12 (d<20) → 13 (d≥20), chi phí fib C(12)=$376/ngày.
- S_ij assignment: `b_pj + v_j − c·d_1(x_i,x_j)` với bonus ưu tiên (120000, 100000, 1500, 750, 250, 0, −100).
- Town drain: trung tâm 1u/ngày/mặt hàng (trừ FERT) = 30/mùa cố định; shop bốc **có hoàn lại** (with replacement) từ catalogue — melon KHÔNG có shop nào hút (chỉ 1u/ngày) → cầu melon gần như cố định cả mùa.

## 9. SO SÁNH VỚI V10 CỦA TA — 5 GAP CẤU TRÚC

| Gap | kme3 | v10 | Ý nghĩa |
|---|---|---|---|
| KERNEL-OPS | WATER 1.102, HARVEST 475 | 629 / 245 | Nút chặn số 1 — đúng chẩn đoán §11.18 |
| Đàn thú | 17 con đủ từ d11 | AD 45,8 (≈11 con) | Dòng milk/wool/egg gấp 1,5× |
| Máy wheat | 163 ô + 198u mua | 574u bán/net | Nguồn feed cho đàn lớn |
| Nhịp bán | lot nhỏ MỌI ngày MỌI mặt hàng | theo batch/hold | Giữ 9 thị trường đồng thời ở premium |
| Thích ứng shop-draw | 13 route + V231/V233 | hầu như không | Đàn/chiến lược nhánh theo shop |

## 10. KHUYẾN NGHỊ CHO V11 (thứ tự ưu tiên)

1. **Kernel-ops 70→90+** (đã đúng hướng v9/v10, cần tiếp tục — WATER 629→1.100)
2. **Đàn 17 con từ d11** (8C+6S+3G): mua dồn d0-d11 thay vì d11-16
3. **Cadence bán giọt nhỏ mọi mặt hàng** + terminal dump d29 (thay batch HOLD lớn)
4. **Máy wheat 163 ô + mua wheat ngoài d0-11 khi rẻ**
5. **V231/V233-style adaptive**: nhánh đàn theo shop draw (milk-shop vs yarn-store)
6. **R42 turn-0 arbitrage** + **sell_lead step%4** — 2 đòn timing rẻ tiền, dễ cài
7. **R36-style lead-selling với debt ledger** khi đối thủ mạnh
8. **Mua FERT ≤$30 để bón** (không bán) + room_guard h23

## 11. TỆP & CÔNG CỤ

- `kaggriculture/kme3.py` — agent tái dựng (đã đăng ký arena `--a kme3`)
- `battles/kme3/kme3_v10_s103.jsonl.gz`, `kme3_v6_s100.jsonl.gz` — replay để god-analysis
- `/tmp/kme3.ipynb`, `/tmp/kme3_work/main.py` — notebook gốc + bản giải nén
- Kaggle API v1 public pull (không cần auth): `/api/v1/kernels/pull?user_name=...&kernel_slug=...`
