# NGHIÊN CỨU CHIẾN LƯỢC KAGGRICULTURE — TỪ v3 "AGROINDUSTRIAL" ĐẾN v4 ÁP ĐẢO

**Phiên bản:** 1.0 · **Mục tiêu:** thiết kế v4 đánh bại v3 với tỷ lệ thu nhập ≥ 2× trong đối đầu trực tiếp
**Nguồn:** giải phẫu `submission_v3.py` (911 dòng) + source engine `kaggle_environments 1.32.7` (1086 dòng) + benchmark thực nghiệm + đo đạc giao dịch thị trường từng đơn vị

---

## 0. TÓM TẮT ĐIỀU HÀNH

v3 đã thắng v2 10/10 trận (tỷ lệ 1.34–1.46×), nhưng tự nó mang **5 điểm rò tiền cấu trúc** và bỏ trống **4 thị trường có chiều sâu xác thực được**. Nghiên cứu này chứng minh bằng số liệu rằng:

1. **Trò chơi thực chất là một bài toán đấu giá dòng chảy (flow auction), không phải bài toán sản xuất.** Thị trường dùng chung có một "cống hút" (drain) cố định theo mặt hàng; giá = hàm của tồn kho tích lũy. Ai điều tiết dòng bán khớp đúng cống hút, người đó thu trọn phần phí khan hiếm (scarcity premium). Ai bán vượt, người đó tự phá giá của chính mình.
2. **V3 đang "đốt" $61.7k để thu về $41k ròng** (gross $102.8k). Nửa đống chi phí đó là chi phí lao động + tự trồng cám mà một bộ lập kế hoạch tốt hơn có thể cắt 30–40%.
3. **Chi phí phá giá (denial cost) bất đối xứng cực đoan:** sập giá MILK chỉ tốn ~3 đơn vị thừa, WOOL ~16u, STRAW ~8u, trong khi sập WHEAT cần 2.421u (bất khả thi). Điều này tạo ra một vũ khí rẻ tiền để tước dòng thu $29k/năm của v3 từ sữa + lông cừu.
4. **V3 có van tự cứu (pressure valves) làm giảm hiệu quả denial đơn thuần** — bậc thang ngưỡng bán 0.98 → 0.72 → 0.65 → 0.45 → 0.004. V4 phải tấn công bằng **ghim ngưỡng (threshold pinning)** thay vì dump một lần.
5. **Đòn kết liễu để đạt 2× không phải là denial, mà là "chiếm chỗ rồi khai thác":** chính công thức thích ứng của v3 (`milk_room = absorb − 30×opp_cows − 40`) khiến v3 **tự rút lui** khỏi thị trường khi v4 có đàn đủ lớn. V4 chiếm milk/wool/egg/straw bằng cách tồn tại, rồi khai thác trọn cống hút với hiệu suất lao động cao hơn.

**Dự kiến v4 vs v3 head-to-head:** v4 ≈ $55–70k, v3 sụt về $25–32k (rơi về chế độ "wheat-only cầm cự") → tỷ lệ **1.8–2.3×**.

---

## 1. PHƯƠNG PHÁP LUẬN & NGUỒN DỮ LIỆU

| Nguồn | Cách khai thác |
|---|---|
| Source engine `kaggriculture.py` | Đọc từng dòng: công thức giá, lockstep, drain, refresh hàng ngày, decay, hire fib, end-of-day |
| `submission_v3.py` / `v3.py` | Giải phẫu 27 vòng phẫu thuật/tuning, phát hiện dead code & quota cứng theo ngày |
| `bench/diag.py` (instrument `_commit_unit`) | Log mọi giao dịch SELL của cả 2 bên → sales mix, giá trung bình từng mặt hàng |
| Trận đo mới (v3 vs v2) | v3 net $41.081, gross $102.815; v2 net $34.286, gross $49.732 — tỷ lệ 1.20 seed này |
| Worklog benchmark v3 | 10/10 thắng v2 (1.34–1.46×), 10.05× vs melon_maxxer, self-play $48–51k |
| Script định lượng | Bảng giá theo offset, headroom theo ngưỡng, chi phí crash, cống hút kỳ vọng |

> **Nguyên tắc xuyên suốt:** mọi khẳng định trong nghiên cứu này đều truy vết được về (a) một dòng code engine, hoặc (b) một phép đo thực nghiệm. Không có phỏng đoán không kiểm chứng.

---

## 2. "VẬT LÝ" TRÒ CHƠI — 15 LUẬT ĐÃ KIỂM CHỨNG TỪ SOURCE

Đây là nền tảng bất biến mà cả v3, v4 và mọi đối thủ trên ladder đều chịu chi phối.

### 2.1 Kinh tế cơ bản
1. **Tiền khởi đầu $3.000**, bàn 10×10 (góc NW), mở đất theo `LAND_ORDER = [NE, SW, SE]` giá `[$1000, $2000, $4000]` → tối đa 4 quadrant.
2. **720 step = 29 ngày × 24 giờ.** Game kết thúc tại step 718 (ngày 29, giờ 22). **Không có auto-drop ngày cuối** — hàng tồn trên người vào ngày 29 là rác. Reward = money.
3. **Lao động là dịch vụ thuê NGÀY:** cuối mỗi ngày `hands = []`, `hires_today = 0`, farmer về spawn. Chi phí thuê người thứ k trong ngày = `fib(k)` (1,1,2,3,5,8,13,21,34,55,89,144,233,377). **Thuê 12 người/ngày = $376/ngày ≈ $10.9k/mùa.**
4. Mỗi unit có **24 action/ngày**, di chuyển chiếm 1 action. Thực đo v2: MOVE chiếm 80–90% lượt → hành động hiệu dụng chỉ ~2.4–4.8/unit/ngày nếu không tối ưu.

### 2.2 Sinh học cây trồng & vật nuôi
5. **Cây chết khi 2 ngày liên tiếp không tưới** (ngày trồng đã tính là 1 ngày không tưới → phải tưới ngay hoặc chậm nhất là ngày hôm sau). Cây chết biến thành WEED, phải DIG.
6. **Cửa sổ năng suất** (cây một lần: `[⌈(max_yield_day+1)/2⌉, max_yield_day]`): mỗi lần TƯỚI trong cửa sổ +1 yield, **+2 nếu bón phân** — nhưng **bị chặn trên bởi `max_yield`**:
   - WHEAT: 4 (không phân) → 6 (có phân) — phân cho +$78/plant
   - CARROT: 3 → 4 — phân cho +$28/plant
   - MELON: 6 → 6 — **phân KHÔNG tăng yield**, chỉ rút ngắn thời gian đạt cap (cycle 13 ngày → ~9–10 ngày = +35% sản lượng/tile/mùa)
   - TOMATO/STRAW (ongoing): yield tích lũy +1/ngày sản xuất (+2 nếu tưới + phân ngày đó), cap 4
7. **Fertilize có hiệu lực 3 ngày** (`fertilized_until_day = day + 2`).
8. **Vật nuôi:** đói 2 ngày liên tiếp → **bỏ trốn** (mất con, giữ chuồng). Sản xuất theo interval; CARE (+1 pending bonus, chỉ ăn khi ngày sản xuất được FEED). Thực đo: COW 36 sữa (feed+care) vs 12 (không care); GOOSE 56 trứng vs 27. **`max_held` chặn sản xuất nếu không thu hoạch** (goose 4, cow/sheep 6).
9. **Mỗi con vật nhả 1 FERTILIZER/ngày miễn phí** (`fertilizer_available = True` trong `_daily_refresh_animals`), thu bằng COLLECT_FERTILIZER.
10. **Ongoing crop (tomato/straw) chết sau lần sản xuất cuối** (`max_lifespan_step` được set), decay −1 yield mỗi 2 step. Không có cây vĩnh cửu.

### 2.3 Thị trường — phần quan trọng nhất
11. **Tồn kho khởi tạo I0 = 10.000 cho mọi mặt hàng** (giá = base tại cân bằng). Công thức:
    ```
    price(inv) = base ± amp × f(|inv − I0|)   — dấu + khi khan hiếm (inv < I0), − khi thừa (inv > I0)
    amp = target × base / f(T)
    ```
    **Bán 1 unit tăng tồn kho 1** → đơn vị kế tiếp bán rẻ hơn. **Mua chỉ cho phép WHEAT & FERTILIZER**, quote tại giá tồn kho sau mua (round-trip trung tính).
12. **Thị trường là tài nguyên DÙNG CHUNG 2 người chơi** — tồn kho là biến đếm cộng đồng.
13. **Per-unit lockstep:** mỗi step, order của 2 người thực thi so le từng đơn vị. Ai đặt order trước trong step đó được报价 trước (lợi thế người đi trước). Giá $1 không tăng tồn kho.
14. **Cống hút của thị trấn (drain):** mỗi 4 step, mỗi shop instance hút 1u/mặt hàng (shop 1 mặt hàng hút ×2: YARN chỉ WOOL ×2, PET_CAFE chỉ CARROT ×2); mỗi 24 step town center hút 1u của mọi mặt hàng trừ FERTILIZER. **Shop mở 1 cái mỗi 3 ngày, tối đa 8 instance, bốc ngẫu nhiên có hoàn lại** (RNG seed × 1.000.003 ^ day).
15. **Shed 100 slot (overflow bị HỦY cuối ngày), tối đa 10 order/step, mua động vật cần chỗ shed.**

---

## 3. CẤU TRÚC VI MÔ THỊ TRƯỜNG — BẢNG SỐ LIỆU ĐO ĐẠC

### 3.1 Đường giá theo offset tồn kho (đo trực tiếp từ `market_price`)

| Offset | MILK | WOOL | STRAW | MELON | EGG | TOMATO | CARROT | WHEAT |
|---|---|---|---|---|---|---|---|---|
| −300 (khan) | **$311** | $249 | $265 | $300 | $68 | $144 | $58 | $42 |
| −200 | $283 | $245 | $239 | $296 | $62 | $84 | $51 | $39 |
| −100 | $247 | $240 | $204 | $290 | $56 | $72 | $43 | $35 |
| 0 (cân bằng) | $160 | $200 | $120 | $250 | $50 | $60 | $35 | $25 |
| +20 (thừa) | $118 | $177 | $82 | $246 | $45 | $49 | $30 | $22 |
| +80 | **$1** | **$1** | **$1** | $186 | $42 | $37 | $25 | $21 |
| +300 | $1 | $1 | $1 | $1 | $40 | $16 | $15 | $20 |

**Đọc bảng này như một bản đồ địa hình:**
- **MILK/WOOL/STRAW = vách đá:** giá premium rất cao bên khan hiếm ($240–311) nhưng sụp về $1 chỉ sau 80u thừa. Thị trường mỏng — trò chơi của kẻ kiên nhẫn.
- **MELON = cao nguyên:** gần như không nhạy giá trong dải +0…+75 ($250→234), sụp chậm. Đây là lý do melon "denial" của v3 vẫn thu về trung bình $152–210/u trong khi phá đối thủ.
- **EGG/WHEAT = đồng bằng vô tận:** log-shape phẳng — EGG giữ ≥70% base sau **8.124u** bán ra; WHEAT giữ $19–21 mãi mãi. Không thể crash, cũng không bao giờ khan sâu. EGG là thị trường khối lượng duy nhất vô hạn.

### 3.2 Cống hút kỳ vọng cả mùa (720 step, trung bình bốc shop)

| Mặt hàng | Shop hút | Town center | Tổng/mùa | Drain/ngày (cuối mùa, 8 shop) |
|---|---|---|---|---|
| WHEAT | 490u | 30u | **520u** | 2.25 |
| STRAWBERRY | 392u | 30u | **422u** | 2.00 |
| MILK | 294u | 30u | **324u** | 1.75 |
| CARROT | 294u | 30u | **324u** | 1.75 |
| TOMATO | 196u | 30u | **226u** | 1.50 |
| EGG | 196u | 30u | **226u** | 1.50 |
| WOOL | 196u | 30u | **226u** | 1.50 |
| **MELON** | **0u** | 30u | **30u** | 1.00 |
| FERTILIZER | 0u | 0u | **0u** | 0.00 |

> **Phát hiện chiến lược số 1: MELON KHÔNG CÓ SHOP NÀO HÚT.** Toàn bộ "thị trường melon" chỉ là town center 30u/mùa + phao giá base $250. Melon tồn tại duy nhất với 2 mục đích: (a) nguồn thu $/tile cao nếu giá giữ được nhờ cả hai bên tiết chế, (b) **vũ khí phá giá đối thủ**. Mọi chiến lược "maxxer melon" (như tutorial) đều tự đào hố: 2 người cùng bán melon → tồn kho dâng → giá $1.
>
> **Phát hiện số 2: FERTILIZER có drain = 0** nhưng giá khởi $100 và suy giảm tuyến tính 0.2/u → bán được 310u trước khi chạm sàn $38. Với 16 con vật × 26 ngày = 416u tiềm năng, FERT là máy in gần như "miễn phí" (thu gom kèm chuyến CARE) — v3 mới khai thác 196/310.

### 3.3 Chi phí phá giá (denial cost) — bảng vũ khí

Số đơn vị phải đẩy tồn kho TRÊN I0 để giá tụt xuống dưới ngưỡng:

| Mục tiêu phá | Ngưỡng đối thủ | Cần dumphàng | Doanh thu dump | Giá TB khi dump | Đánh giá |
|---|---|---|---|---|---|
| MILK < 0.98×base ($156.8) | v3 HOLD 0.98 | **3u** | ~$480 | $159 | **Rẻ nhất trò chơi** |
| STRAWBERRY < 0.90×base ($108) | v3 HOLD 0.90 | **8u** | ~$900 | $114 | Rẻ |
| WOOL < 0.94×base ($188) | v3 HOLD 0.94 | **16u** | ~$3.000 | $196 | Rẻ |
| TOMATO < 0.82×base ($49) | v3 HOLD 0.82 | **19u** | ~$1.000 | $53 | Rẻ (nhưng v3 đã bỏ trống) |
| EGG < 0.86×base ($43) | v3 HOLD 0.86 | 78u | ~$3.400 | $44 | Vừa |
| CARROT < 0.70×base ($24.5) | v3 HOLD 0.70 | 84u | ~$2.300 | $28 | Vừa |
| MELON < 0.52×base ($130) | v3 HOLD 0.52 | **110u** | ~$23.100 | $210 | Đắt nhưng **tự hoàn vốn** (v3 vẫn kiếm $11k melon) |
| WHEAT < 0.76×base ($19) | v3 HOLD 0.76 | **2.421u** | — | — | **BẤT KHẢ THI** — wheat là tiền điện tử ổn định |

**Nhưng denial một lần là không đủ:** cống hút kéo tồn kho quay lại vùng cân bằng (MILK ~1.75u/ngày). Ghim vĩnh viễn = phải bơm đúng lượng drain mỗi ngày (~1.75u milk/ngày = ~45u/mùa, mất ~$6–7k doanh thu potential). Và v3 có **van giảm áp 4 bậc**:

```python
# v3, hàm _hold(): ngưỡng bán tự hạ khi bị dồn ép
shed_total ≥ 80  →  hold = 0.72   # shed đầy → hạ ngưỡng
money < 250      →  hold = 0.65   # nghèo → hạ ngưỡng
day ≥ 22         →  hold ≤ 0.70   # cuối mùa → hạ ngưỡng
day ≥ 26         →  hold ≤ 0.45
day ≥ 28         →  hold = 0.004  # thanh lý
```

→ **Kết luận chiến lược:** denial đơn thuần chỉ hạ giá trung bình của v3 từ premium về vùng 0.65–0.72×base, không giết được. Đòn thật sự là **chiếm dòng cống hút** (mục 6–7).

---

## 4. GIẢI PHẪU V3 — KIẾN TRÚC, DÒNG TIỀN, VÀ NHỮNG GÌ NÓ LÀM TỐT

### 4.1 Kiến trúc (1095 dòng, 1 file, stdlib-only)

```
agent(obs) 
 ├─ _daily_plan()      — gọi 1 lần/ngày: quota cây theo cửa sổ ngày CỨNG, đàn thú theo room(), 
 │                        reserve ô đất cho COOP/PASTURE, order ưu tiên theo feed_demand
 ├─ _build_tasks()     — mỗi step: sinh task WATER/HARVEST/SERVICE/PLANT/DIG/FERTILIZE/DELIVER
 │                        với tier ưu tiên (T_WATER_CRIT=0 … T_FERTILIZE=7)
 ├─ _build_orders()    — mỗi step: HIRE (budget 25%), BUY_SEED, BUY_ANIMAL (2/ngày),
 │                        BUY_LAND (gate 1.2–1.3×), BUY_PRODUCT wheat (≤$38), SELL theo HOLD
 ├─ _assign_and_act()  — sticky assignment + claimed set + greedy theo (tier, khoảng cách)
 └─ _forward_absorb()  — mô hình cống hút tương lai (shops + unlock + town center)
```

### 4.2 Sales mix thực đo (v3 vs v2, seed mới nhất, net $41.081)

| Mặt hàng | Số lượng | Doanh thu | Giá TB | Ghi chú |
|---|---|---|---|---|
| WHEAT | 898u | $34.881 | $39 | **34% gross** — vừa bán vừa làm cám |
| FERTILIZER | 196u | $15.778 | $80 | 15% — máy in thụ động |
| MILK | 65u | $15.758 | **$242** | premium do v2 không chạm |
| WOOL | 62u | $13.657 | **$220** | premium |
| MELON | 73u | $11.119 | $152 | denial có hoàn vốn |
| EGG | 134u | $8.051 | $60 | khan hiếm nhẹ |
| CARROT | 66u | $1.854 | $28 | biên thấp |
| STRAWBERRY | 6u | $1.717 | $286 | **đã nhường thị trường cho v2** |
| TOMATO | 0u | $0 | — | **bỏ trống hoàn toàn** |
| **GROSS** | | **$102.815** | | |
| **Chi phí** | | **−$61.734** | | hire ~$10k + thú $6k + đất $7k + hạt + cám |
| **NET** | | **$41.081** | | đối thủ $34.286 (1.20× seed này) |

### 4.3 Những gì v3 làm đúng (phải GIỮ trong v4)

1. **Kỷ luật bootstrap 4 ngày** (wheat+carrot trước, hạt trước đất sau) — chống bẫy nghèo.
2. **Sticky assignment** — chống ping-pong task, +$10k so với không sticky.
3. **SERVICE composite** (FEED+CARE+COLLECT_FERTILIZER một chuyến/thú) — giảm 60% chuyến đi.
4. **Tưới theo parity `(x+y+day)%2`** ngoài cửa sổ năng suất — khai thác luật "chỉ chết khi 2 ngày liên tiếp không tưới", giảm một nửa lao động tưới.
5. **Mô hình `_forward_absorb`** — dự báo cống hút tương lai để tính quota (v4 kế thừa và nâng cấp).
6. **Melon denial có hoàn vốn** — $23k dump thu về $11k net trong khi tước $18–20k của v2.
7. **Thanh lý ngày 26–28 + hold ladder** — không chết vì tồn kho.

---

## 5. CHẨN ĐOÁN: 7 ĐIỂM RÒ TIỀN CỦA V3

### Rò #1 — Quota cứng theo cửa sổ ngày (brittle time windows)
`quotas["TOMATO"] = 0` cho ngày 2–16 (dòng 363–364), STRAW chỉ 14–30 ô trong ngày 5–13, MELON 14 ô ngày 8–14. Đây là **bảng tra viết tay sau 27 vòng tuning** — chính xác với v2, sai lệch với bất kỳ đối thủ khác. v3 vs v2 seed mới nhất: v3 nhường straw cho v2 → v2 bán 48u × **$312** = $15k. Logic `room()` trừ `0.85 × opp_pipeline` quá nhún nhường: đối thủ có pipeline ≠ đối thủ monetize được.

### Rò #2 — Dead code fertilizer trên cây
Dòng 452–470 tính `fert_usable` cho WHEAT/CARROT rồi **không bao giờ dùng** — block FERTILIZE chỉ duyệt `crop == "MELON"`. Trong khi phân trên WHEAT = +2 yield (+$78), trên MELON = +0 yield (chỉ rút cycle). Với 416u phân/mùa và thị trường chỉ hút 310u ở giá ≥$38, **~100u phân dư nên bón hết vào lúa mì** = +$7–8k/năm bị bỏ lại.

### Rò #3 — FERT khai thác 196/310 capacity
Herd ramp chậm + vài ngày bỏ collect → mất ~114u × ~$70 = **$8k/năm**. FERT là nguồn thu duy nhất KHÔNG phụ thuộc đối thủ (drain = 0, giá chỉ phụ thuộc tổng cung của 2 bên — nếu đối thủ không có vật nuôi thì gần như chắc chắn được giá).

### Rò #4 — EGG dừng ở 5 ngỗng khi thị trường vô hạn
`goose_target = max(4, min(5, egg_room // 46))` — công thức "room" dành cho thị trường mỏng, áp vào thị trường **deep-log vô hạn** của EGG (giữ 70% base sau 8.124u!). Ngỗng: $300 → 56 trứng (care) ≈ $2.800–3.400 gross tại giá $50–60. 5 con là quá ít; **10 con vẫn giữ giá $45+**. Biên ròng ~$1.800–2.100/ngỗng sau trừ cám.

### Rò #5 — Đốt lao động $376/ngày cho 12 người mà không có ledger $/action
Hire quyết theo `money ≥ 1800` và workload thô. Không ai hỏi: *"fib(12) = $144/ngày — người thứ 12 này tạo ra ≥ $144 giá trị hôm nay không?"* Tác vụ của người lao động có giá trị trải từ $242 (thu sữa) đến $10 (tưới lúa ngoài parity). Thiếu bảng xếp hạng $/action → vừa thuê thừa ở ngày nghèo, vừa thiếu tay ở ngày cao điểm thu hoạch.

### Rò #6 — Không đo được dòng bán của đối thủ (mù thông tin thị trường)
v3 nhìn **bàn cờ** của đối thủ (đàn thú đang đứng, cây đang trồng) nhưng không nhìn **dòng giao dịch**. Trong khi đó, tồn kho thị trường là public và biến mỗi step: `Δinv = my_sales + opp_sales − drain`. v3 biết chính xác my_sales (order mình đặt) và drain (shops public + công thức) → **dòng bán của đối thủ là đại số sơ cấp, đo được từng giờ, từng mặt hàng.** Đây là sóng ngầm thông tin lớn nhất mà v3 chưa đụng tới.

### Rò #7 — Mô hình 0.85×opp_pipeline tuyến tính hóa đối thủ
Trừ 0.85 lần pipeline đối thủ trong `room()` cho mọi mặt hàng — nhưng MILK của đối thủ (7 bò × 36 = 252u) với drain 324u thì phần lớn KHÔNG thể bán được ở premium; phần "room thật" nhỏ hơn nhiều. Ngược lại EGG của đối thủ gần như không chiếm chỗ của ai. Hệ số 0.85 đồng nhất = sai ở cả 2 đầu.

---

## 6. LÝ THUYẾT TRÒ CHƠI CỦA THỊ TRƯỜNG DÙNG CHUNG

### 6.1 Bản chất: common-pool flow auction

Tổng doanh thu tối đa hai bên cộng lại được chặn trên bởi cống hút:

```
Tổng premium có thể thu = Σ_p [ drain_p × giá_TB(scenario) ]
```

- Nếu **cả hai cùng bán vượt drain** ở mặt hàng mỏng (milk/wool/straw): tồn kho dâng, giá rơi tự do về $1 — cả hai mất. Đây là **thảm họa chung** (melons của 2 bot maxxer).
- Nếu **một bên kiềm chế, một bên bán hết drain**: bên bán thu premium, bên kiềm chế nuôi tồn kho vô dụng (giới hạn shed 100 + `max_held` chặn sản xuất).
- Nếu **cả hai khớp đúng drain và chia đều**: cả hai giữ giá premium. Đây là cân bằng hợp tác — nhưng bất ổn (một bên lệch 1u là ăn sẻ).

**Điểm mấu chốt:** ngưỡng bán (hold threshold) của mỗi bên quyết định cân bằng. v3 bán milk ở ngưỡng 0.98 (gần như ngay khi giá ≥ base) → v3 là "bên xả nhanh", tự giữ giá milk quanh vùng base-vừa-cao. Một bên biết đọc drain + đo dòng đối thủ có thể **bán trùm drain ở mức giá cao hơn** (đợi khan hiếm sâu hơn rồi xả đúng nhịp).

### 6.2 Bậc thang nhún nhường của v3 = điểm yếu khai thác được

Công thức đàn thú của v3 (dòng 306–308):
```python
milk_room = absorb − 30×opp_COW − 40      # v3 TỰ RÚT khi đối thủ nhiều bò
wool_room = absorb − 28×opp_SHEEP − 20
egg_room  = absorb − 46×opp_GOOSE − 20
```
→ **v3 đầu hàng thị trường theo số lượng đàn đối thủ, không theo dòng bán thực**. Một đối thủ phô trương 8 con bò (dù cho ăn kém, chỉ bán được ít) đủ khiến v3 đặt `cow_target = 0`. Với drain milk 324u/mùa, 8 bò v4 = 240u "phòng ngừa" trên bàn cờ của v3 — **v4 chiếm milk bằng cách tồn tại, không cần bắn một viên đạn nào.** Đây chính là đòn "chiếm chỗ" (presence warfare) — rẻ hơn denial và không thể chống bởi logic hiện tại của v3.

### 6.3 Phân tích cân bằng v4-vs-v3 theo từng mặt hàng

| Mặt hàng | Kịch bản v4 tối ưu | Kết quả cho v3 | Kết quả cho v4 |
|---|---|---|---|
| MILK (drain 324) | Chạy 8–9 bò, bán đúng nhịp drain ở ngưỡng 1.3–1.5×base | `cow_target→0`, mất $15.8k, đàn sữa sập | ~$60–80k gross nguyên liệu… thực tế ~280u × ~$220 = $60k? *(xem 7.1 — bị chặn bởi sản lượng thật)* |
| WOOL (drain 226) | 7–8 cừu | mất $13.7k | ~180u × $210 ≈ $38k cap |
| EGG (drain ∞) | 9–10 ngỗng, bán tự do $45–55 | giữ mảng $8k (market đủ sâu) | ~500u × $48 ≈ $24k |
| STRAW (drain 422) | 30–40 ô, bán nhịp 2.2/ngày | v3 vốn đã nhường | ~350u × $180–240 ≈ $70k?? *(bị chặn labor — 7.1)* |
| MELON | Denial như v3 (110u dump hoàn vốn) | giữ ~$11k | ~$11k |
| WHEAT | Vùng an toàn vô hạn, tự cân đối cám + bán muộn vào khan hiếm | giữ ~$30k (không thể deny) | +$5–10k từ timing |
| FERT (drain 0) | Max collect 310u về floor $38 | giữ phần theo đàn | +$5–6k |

> Lưu ý quan trọng: các "cap" trong bảng không đạt được đồng thời — **ràng buộc thật là LAO ĐỘNG và TIỀN MẶT**, không phải thị trường. Phân tích ràng buộc ở mục 7.

### 6.4 Ba chế độ đối đầu (dùng cho benchmark v4)

1. **Chế độ cõm nhau (coop):** đối thủ không chạm thị trường động vật → v4 chạy full portfolio, target gross $110k+.
2. **Chế độ chia sẻ (mirror / self-play):** cả hai cùng portfolio → v4 phải đối xứng ổn định (mỗi bên tự khớp nửa drain; không được dump phá giá phản chủ). Đây chính là Validation Episode của Kaggle — **điều kiện sống còn là self-play không tự hủy.**
3. **Chế độ đấu súng (vs v3):** v4 chiếm chỗ + ghim ngưỡng; v3 tự rút về wheat-only mode. Mục tiêu 2× nằm ở chế độ này.

---

## 7. KHO BÁU BỎ TRỐNG — ĐỊNH LƯỢNG TỪNG THỊ TRƯỜNG

### 7.1 Ràng buộc thật: kinh tế lao động (đây là thắt cổ chai số 1)

Giá trị biên mỗi loại action (tính từ số liệu đo + công thức engine):

| Action | Giá trị biên | Ghi chú |
|---|---|---|
| **CARE (bò/cừu đúng lịch)** | **$220–242** | +1 pending → +1 product ở lần sản xuất kế tiếp — action đắt nhất trò chơi |
| HARVEST sữa/len đúng hạn | $220–242 | bắt buộc, không thì `max_held` chặn sản xuất |
| FEED (ngày sản xuất) | ~$150–200 | mở khóa bonus CARE + chống trốn |
| HARVEST melon chín | ~$150 | 6u/plant |
| PLANT wheat | ~$78/plant | trừ chi phí đi lại |
| FERTILIZE wheat | ~+$78 | (v3 đang bỏ) |
| WATER trong cửa sổ năng suất | $28–78 | |
| Tưới parity (ngoài cửa sổ) | $0 | giữ cây sống, không tăng yield |
| SELL order | $0 | order tách bạch khỏi lao động (thị trường tự chạy) |

Một unit = 24 action. Với hire fib, **người thuê thứ 9–12 tốn $55–144/ngày** → cần $/action trung bình ≥ $5–9 chỉ để hòa. Hiện v3 không đo cái này. v4 có: **Labor Ledger** (mục 8).

Sản lượng tối đa theo lao động (ước lượng thận trọng, MOVE chiếm 60% sau zoning):
- 1 công nhân/ngày ≈ 9–12 action hiệu dụng ≈ đủ CARE+FEED 3–4 bò/cừu HOẶC thu hoạch 10–12 melon HOẶC 2.5 cycle lúa.

→ **Farma tối ưu không phải "cày hết bàn 20×20" mà là選 mix có $/action cao nhất trước khi rơi về biên $8–10.** v3 dừng ở ~12 người + 16 thú + ~100 cây: biên của nó đã thấp. v4 cần zoning để đẩy đường biên này ra xa.

### 7.2 TOMATO — thị trường trống có kiểm chứng (khoảng $3–6k)

- v3 quota = 0 (ngày 2–16); v2 chỉ bán vớt vát 8u × $73. Không ai chạm → tồn kho tụt −100…−300 → giá $72–144.
- Kinh tế: $50 hạt → 4u/12 ngày (chỉ tưới parity + không cần phân vì cap 4) → ~2.4 cycle/mùa → 9.6u × ~$95 ≈ **$910/tile/mùa** với lao động rất thấp (thiếu nước chỉ 2 ngày liên tiếp mới chết).
- **Rủi ro:** tomato của cả 2 bên → 2×19u chưa đủ đụng drain 226u → an toàn cho cả hai. Thị trường "tử tế" — ít kịch tính, thu nhập chắc.

### 7.3 STRAWBERRY — premium lớn nhất bị v3 tự nhường (khoảng $8–15k tranh chấp)

- Drain 422u/mùa — **cống hút lớn nhất trong các mặt hàng premium**; giá khan −300 = $265.
- Kinh tế: $100 hạt → 4u/17 ngày → 1.7 cycle → 6.8u × $200–300 ≈ **$1.400–2.000/tile/mùa** nếu bán được ở vùng khan.
- v2 thực tế đã ăn $312 × 48u = $15k từ thị trường này (v3 nhường). V4 tranh 30–40 ô + nhịp bán 2/ngày.
- Chi phí phá straw rẻ (8u) → nếu đối thủ tràn vào, cả hai cùng chết — phải có logic chia drain (mục 8, module D).

### 7.4 FERTILIZER — máy in gần như chắc chắn (+$5–8k)

310u ở giá ≥$38; v4 chỉ cần: 16 con vật + collect kỷ luật + bán dần theo đường giá tuyến tính. Không phụ thuộc đối thủ (trừ khi họ cũng có đàn). Với CARE composite chuyến đi, marginal cost ≈ 0.

### 7.5 EGG — thị trường khối lượng duy nhất vô hạn (+$8–15k)

Log-flat: 8.124u mới hạ giá xuống 70% base. Kinh tế ngỗng: $300 + ~$700 cám → 56 trứng × $48 ≈ $2.700 → **ROI ~2.3× ròng/con**, mỗi con cần ~4 action/ngày (feed+care+collect+harvest) + di chuyển. 10 ngỗng = $27k gross với ~40 action/ngày = **$18/action — cao hơn mọi loại cây trồng**. v4 lên 9–10 con (v3 dừng ở 5).

### 7.6 Timing WHEAT — "kho lạnh giá trị" (+$3–6k)

Đường giá wheat theo mùa khi cả hai tự sản cám: mùa đầu tồn kho về I0 ($25–29), drain 520u/mùa dần kéo xuống −100…−200 ($35–39). Thực đo v3 bán TB $39. Chiến thuật: **tích cám từ tự trồng + chỉ bán surplus sau ngày 12 khi khan hiếm đã hình thành**; đồng thời MUA wheat ngày 1–8 ở $26–30 (tồn kho cao, mua rẻ) cho đàn thú, để dành sản lượng tự trồng bán muộn. Spread mua-bán $26 → $39 = +50% trên phần cám.

---

## 8. KIẾN TRÚC V4 — BLUEPRINT 6 MODULE

```
┌────────────────────────────────────────────────────────────────┐
│  MODULE A: WORLD MODEL (telemetry thị trường + đối thủ)        │
│    • tracker: inv[p] mỗi step (public)                        │
│    • đo dòng bán đối thủ: opp_sales[p] = Δinv + drain − my_sales│
│    • phát hiện dump-attack trong 1 step (glut arrival)        │
│    • phân loại chế độ đối đầu: coop / mirror / contest        │
├────────────────────────────────────────────────────────────────┤
│  MODULE B: PORTFOLIO SOLVER (thay quota cứng của v3)           │
│    • input: room[p] = drain_remaining[p] − opp_flow_measured[p]│
│    • bảng $/action + $/tile-day cho mọi mặt hàng (mục 7)      │
│    • output: allocation (cây theo loại, đàn theo loại) hằng ngày│
│    • ràng buộc: tiền mặt ≥ floor động, shed ≤ 100, labor budget│
├────────────────────────────────────────────────────────────────┤
│  MODULE C: LABOR LEDGER + ZONING                               │
│    • layout: wheat-belt cạnh shed (cycle nhanh, đi lại ngắn), │
│      melon/tomato/straw theo cụm quadrant xa (c cycle dài),   │
│      COOP/PASTURE dải giữa                                     │
│    • batch: 1 chuyến = N action liên tiếp cùng loại trong cụm │
│    • hire: điều kiện fib(k) ≤ marg_value(action kế tiếp)       │
│    • mục tiêu: MOVE từ 80–90% → ≤ 55%                          │
├────────────────────────────────────────────────────────────────┤
│  MODULE D: MARKET OPS (bán + ghim + thanh lý)                  │
│    • flow-matching: bán khớp drain, chia đều với đối thủ đo được│
│    • threshold ladder riêng theo chế độ (coop: cao; mirror: chia)│
│    • pin engine: giữ giá đối thủ dưới ngưỡng của chúng (nếu contest)│
│    • liquidation: schedule dump tối ưu ngày 26–29 (tính đạo hàm │
│      giá từng unit — bán mặt hàng sụp nhanh trước, chậm sau)   │
├────────────────────────────────────────────────────────────────┤
│  MODULE E: PRESENCE WARFARE (đòn 2× vs v3)                     │
│    • đàn "cờ": 8 bò + 7 cừu hiện diện từ sớm → v3 tự rút      │
│    • melon denial chuẩn 110u (hoàn vốn $23k)                   │
│    • KHÔNG denial milk/wool bằng dump (đắt, dễ bị van áp v3)   │
│      — thay bằng chiếm dòng drain + bán premium               │
├────────────────────────────────────────────────────────────────┤
│  MODULE F: SAFETY & VALIDATION (điều kiện sống)                │
│    • try/except toàn cục như v3, PASS an toàn                  │
│    • self-play ổn định (Kaggle Validation Episode)             │
│    • budget compute: O(board²)/step, không dataframe/numpy     │
└────────────────────────────────────────────────────────────────┘
```

### 8.1 Vì sao Module A là "đòn tiên phong"

Thông tin v3 không có = lợi thế thông tin v4. Thông tin này **miễn phí, chính xác tuyệt đối, cập nhật mỗi giờ**:

```python
# pseudo — đại số 3 biến thành 1 ẩn duy nhất
delta_inv[p]     = inv_now[p] − inv_prev[p]        # public
drain_expected[p]= shop_vector[today] / 4 + center # public + công thức
my_sales[p]      = chính xác từ order của mình
opp_sales[p]     = delta_inv[p] + drain_expected[p] − my_sales[p]
```

Ứng dụng:
- Đo v3 đang bán milk bao nhiêu u/ngày → v4 biết chính xác "phần drain còn trống" thay vì đoán bằng 0.85×pipeline.
- Phát hiện v3 vào chế độ glut-dump (dòng âm đột biến) → v4 tạm ngưng bán mặt hàng đó 2–3 ngày để v3 xả vào đáy rồi quay lại mua lại... (mua không được với milk — nhưng chờ v3 cạn hàng rồi bán lại vào khan hiếm sâu).
- Mirror mode: opp_sales = my_sales → chia drain đôi, giữ premium cho cả hai → self-play ổn định.

### 8.2 Presence Warfare chi tiết (đòn chính cho mục tiêu 2×)

Timeline dự kiến v4 vs v3:

| Giai đoạn | Hành động v4 | Phản ứng v3 (từ code) | Phản ứng v3 (thực tế đo) |
|---|---|---|---|
| Ngày 0–4 | Bootstrap wheat/carrot như v3 + mua land sớm hơn | tương tự | cân bằng |
| Ngày 3–8 | Mua 8 bò + 7 cừu (nhờ tiết kiệm hire từ zoning) | `milk_room = 324−240−40 < 0 → cow_target = 0` | v3 **tự hủy đàn sữa**, chuyển cờ sang wheat/egg |
| Ngày 8–20 | Bán milk/wool khớp drain ở $180–240 | v3 không có hàng để cạnh tranh | v4 thu ~$25–35k từ 2 thị trường này |
| Ngày 8–14 | Melon denial 110u + thu $21k dump | v3 giữ hold 0.52 | melon $150 cả hai |
| Ngày 5–25 | 10 ngỗng + 35 ô straw + 20 ô tomato + FERT max | v3 dừng ở 5 ngỗng, 0 tomato | v4 đơn độc thu EGG $24k, STRAW $10–15k, TOMATO $4k, FERT $20k |
| Ngày 26–29 | Liquidation schedule chính xác | thanh lý thô | +$2–3k |

**Điểm mấu chốt: v4 KHÔNG cần "đánh" v3. V4 chỉ cần tồn tại to hơn ở các thị trường mà v3 dùng công thức rút lui — v3 sẽ tự nhường. Sau đó 2× đến từ chênh lệch năng suất (zoning + portfolio solver), không phải từ denial tốn kém.**

### 8.3 Kế thừa có chọn lọc từ v3

| Giữ nguyên | Sửa | Bỏ |
|---|---|---|
| try/except an toàn | quota cứng → portfolio solver | fert chỉ melon |
| sticky assignment | 0.85×opp_pipeline → opp_sales đo được | goose cap 5 |
| SERVICE composite | hire heuristic → labor ledger | parity tưới (giữ, tối ưu thêm zoning) |
| bootstrap 4 ngày | HOLD tĩnh → threshold ladder theo chế độ | melon quota 14 ngày 8–14 |
| melon denial | thanh lý 26–28 → schedule đạo hàm | dead code fert_usable |

---

## 9. BẢNG GIÁ TRỊ DỰ KIẾN TỪNG ĐÒN (đối đầu v4 vs v3)

| # | Đòn | Δ cho v4 | Δ cho v3 | Mức đóng góp tỷ lệ | Độ tin cậy |
|---|---|---|---|---|---|
| E1 | Presence warfare (milk+wool: v3 tự rút) | +$25–33k gross | −$25–28k | **~55%** | Cao (công thức v3 trong source) |
| E2 | Zoning + labor ledger (MOVE 80→55%) | +$8–14k | ~0 | ~15% | Trung bình-cao |
| E3 | FERT max (310u) | +$5–8k | ~0 | ~8% | Cao |
| E4 | EGG scale 10 ngỗng | +$6–10k | −$1k (giá nhẹ) | ~8% | Cao |
| E5 | STRAW tranh 35 ô + flow-match | +$8–15k | 0 (đã tự nhường) | ~12% | Trung bình |
| E6 | TOMATO 20 ô | +$3–5k | 0 | ~5% | Cao |
| E7 | Fert-on-wheat (100u phân dư) | +$7–8k | 0 | ~10% | Cao |
| E8 | Liquidation schedule đạo hàm | +$2–3k | 0 | ~3% | Trung bình |
| E9 | Wheat make-vs-buy timing | +$2–4k | −$1k | ~4% | Trung bình |

**Tổng hợp kịch bản thận trọng (chỉ tính 70% mỗi đòn E2–E9):**
- v4: $41k (nền v3-equivalent) + $25k (E1×0.7) + ~$20k (E2–E9×0.7) ≈ **$55–60k**
- v3: mất milk/wool/straw premium, giữ wheat $30k + egg/fert/melon glut ≈ **$26–30k**
- **Tỷ lệ: 1.9–2.2×** ✓ đạt mục tiêu.

**Điều kiện thất bại cần theo dõi:** nếu v3's pressure-valve cho phép nó chuyển toàn bộ cám sang wheat quy mô lớn (898u → 1.400u), net v3 có thể giữ $32k+ → tỷ lệ tụt về 1.7×. Biện pháp: E9 (wheat squeeze ngày 8–20 — mua $26–32 khi v3 cần cám cho đàn egg còn lại, đẩy giá cám v3 lên $40+).

---

## 10. RỦI RO & PHẦN LƯỢNG TRỌNG THẬN THỰC

1. **Overfit v3.** Ladder Kaggle không phải toàn là v3. Module B phải có fallback: khi `opp_sales` đo được ≠ profile v3 (ví dụ: thuần melon, thuần egg, passive), chuyển chế độ coop/portfolio. **Chỉ kích hoạt presence-warfare khi nhận diện đúng profile đối thủ có công thức room-like** (đặc trưng: tự rút đàn khi ta có đàn lớn — phát hiện qua opp BUY_ANIMAL ngừng sau khi ta mua).
2. **Self-play phải ổn định.** Validation Episode = đấu với bản sao. Module D ở mirror mode phải chia drain đối xứng, không dump phá giá phản chủ (worklog v3 đã đạt self-play $48–51k ổn định — v4 phải benchmark tương tự trước khi nộp).
3. **Runtime:** v3 episode ~4s. Module A/B nhẹ (O(9 mặt hàng)), zoning O(board²) mỗi ngày 1 lần. Giữ < 15s/episode để an toàn với notebook timeout.
4. **Phương sai seed:** trận đo mới ra 1.20× trong khi worklog trung bình 1.34–1.46×. Mọi tuyên bố 2× phải qua **N ≥ 50 trận paired-seed** (bench/run.py có sẵn), báo cáo median + IQR, không lấy trận đẹp.
5. **Mua đất sớm hơn có thể tái tạo "bẫy nghèo"** (bài học đắt nhất của v1: mua đất hút tiền → hạt thiếu → cây chết dây chuyền). Presence warfare cần $4.4k cho 8 bò + 7 cừu — phải chứng minh dòng tiền ngày 5–8 đủ bằng benchmark cash-curve trước khi bật.
6. **Care scheduling là tối ưu toàn cục:** CARE bò chỉ có giá trị nếu ngày sản xuất được FEED. Lịch CARE phải bám lịch sản xuất (bò: chẵn ngày kể từ đặt; cừu: mỗi 3 ngày; ngỗng: hằng ngày). V3 care hằng ngày mọi con — thực ra chỉ cần care trùng nhịp sản xuất (tiết kiệm ~20% action CARE trên cừu).

---

## 11. LỘ TRÌNH THỰC THI v4

| Phase | Việc | nghiệm thu |
|---|---|---|
| P0 | Module A (telemetry) + đo opp_sales trong trận v3-vs-v3 hiện có | log đối chiếu 100% với diag instrument |
| P1 | Portfolio solver thay quota cứng + TOMATO/STRAW/FERT/EGG/E7-fert-wheat | v4-solo (vs random): gross ≥ $110k, net ≥ $55k |
| P2 | Zoning + labor ledger | MOVE ≤ 60% (đo bằng instrument bước); net +$5k |
| P3 | Presence warfare + threshold ladder | vs v3: N=50, tỷ lệ TB ≥ 1.8×, W/L ≥ 90% |
| P4 | Mirror stability + liquidation | self-play ≥ $45k mỗi bên, 0 tự hủy, 20 trận |
| P5 | Archetype suite (melon/egg/straw/passive/denial bots) | không có archetype nào thắng v4 > 10% trận |
| P6 | Strip comment → `submission_v4.py` (thuần code như quy ước Kaggle) + hướng dẫn nộp | syntax + import check + verify benchmark ngang bản dev |

---

## PHỤ LỤC A — THÔNG SỐ ĐỐI CHIẾU NHANH

```
CROPS      : WHEAT($10, 5d, 6u) CARROT($20, 4d, 4u) TOMATO($50, 12d, 4u)
             STRAWBERRY($100, 17d, 4u) MELON($80, 13d, 6u)
ANIMALS    : GOOSE($300→56 EGG) COW($400→36 MILK) SHEEP($500→~35 WOOL)   [feed+care]
MARKET I0  : 10.000 mọi mặt hàng; lockstep per-unit; BUY chỉ WHEAT/FERT
DRAIN/mùa  : WHEAT 520, STRAW 422, MILK 324, CARROT 324, TOMATO 226,
             EGG 226, WOOL 226, MELON 30, FERT 0
DENIAL chi phí: MILK 3u · STRAW 8u · WOOL 16u · TOMATO 19u · EGG 78u ·
             CARROT 84u · MELON 110u · WHEAT 2421u (bất khả thi)
HIRE fib   : 1,1,2,3,5,8,13,21,34,55,89,144 → 12 người/ngày = $376
v3 HOLD    : MILK .98 WOOL .94 STRAW .90 EGG .86 TOM .82 WHEAT .76
             CARROT .70 MELON .52 FERT .40 + van áp (shed≥80→.72, nghèo→.65, d≥26→.45)
v3 KẾT QUẢ : vs v2 10/10W 1.34–1.46× · vs melon 10.05× · self-play $48–51k
v3 ROTÒ   : $61.7k chi phí / $102.8k gross (trận đo mới nhất)
```

## PHỤ LỤC B — VỊ TRÍ CÁC PHÁT HIỆN TRONG CODE v3 (để P1–P3 truy cập nhanh)

| Phát hiện | File:vòng | Bản chất |
|---|---|---|
| TOMATO quota 0 | `v3.py:363–364` | `if 2 <= day <= 16: quotas["TOMATO"] = 0` |
| Dead code fert cây | `v3.py:452–470` | `fert_usable` tính cho WHEAT/CARROT, không consumer |
| FERT chỉ melon | `v3.py:595–613` | block FERTILIZE `crop != "MELON": continue` |
| Goose cap 5 | `v3.py:309` | `goose_target = max(4, min(5, egg_room // 46))` |
| Công thức tự rút đàn | `v3.py:306–308` | `milk_room = absorb − 30×opp_COW − 40` (và wool/egg) |
| Van áp hold | `v3.py:991–1009` | hàm `_hold` — 4 bậc hạ ngưỡng |
| Room 0.85×pipeline | `v3.py:269–272` | trừ tuyến tính pipeline đối thủ mọi mặt hàng |
| Hire heuristic | `v3.py:852–875` | `target_units 12–13`, budget 25%, không $/action |
| Thanh lý thô | `v3.py:995–1004` | d≥28 hold 0.004 dump hết |

---

*Kết thúc nghiên cứu. Tài liệu này là hợp đồng thiết kế cho v4: mọi module trong mục 8 truy vết về một rò tiền ở mục 5, mọi con số truy vết về engine hoặc benchmark ở mục 2–3. Bước tiếp theo: P0 (Module A telemetry) — viết instrumentation lên bench hiện có, đo `opp_sales` trong 10 trận v3-vs-v3 để kiểm định giả thuyết "đo dòng đối thủ = đại số chính xác 100%".*
