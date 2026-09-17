# 11 — v23 GOOSE ENGINE: kiến trúc production-planner EGG/GOOSE và phán quyết mirror
## 4 vòng forensic · 3 thiết kế (NE-race → SE-clean → land-only) · 3 battery 48 trận

> Task 91 · 2026-09-18/19 · Bio
> Chuẩn đối: v20 (flat 410KB) vs ahmedv46, engine kaggle 1.32.7, 720 turn.
> Batteries: seeds 100-123 × 2 ghế, official runner (bench/battery.py).

---

## 0. TÓM TẮT

| Biến thể | 48 trận vs ahmedv46 | gap | Self-damage* | v46-gain* |
|---|---|---|---|---|
| v20 baseline (seeds 100-123) | **48W-0L** | **+$1,647** | — | — |
| v23l = mua SE land only | 0W-48L | −$3,304 | **−$6,741** | −$1,789 |
| v23 = SE land + goose engine | 0W-48L | **−$20,205** | **−$15,019** | +$6,834 |

\* so với baseline cùng dải seed (self = avg $ của mình; v46-gain = avg $ của đối thủ).

**Phán quyết: EGG/GOOSE không khả thi trong mirror V45.** Engine chạy đúng cơ học
(13 coop, 14 ngỗng, 220 trứng bán/game, 0 lỗi layer) nhưng thua $20K/game vì
5 bức tường kinh tế cấu trúc (mục 3). Ước lượng +$25-35K của doc 10 đã giá
trứng theo điều kiện TFC-monopoly mà không định giá inputs theo opportunity
cost của chính máy v20.

**Quyết định submission: GIỮ v20.1 #56308666.** v23.py và v23l.py giữ lại
trong repo như artifact nghiên cứu (fail-open đã verify: không có exception
nào làm hỏng game).

## 1. KIẾN TRÚC v23 (production-planner, riêng biệt — không phải layer-wrap)

```
v23.py = v20 flat chain (byte-exact, "cash engine")
       + v23_layer (GOOSE ENGINE planner):
           • phase machine: land-snipe → build → ramp → harvest-loop
           • receipt-claimed hands: HIRE tail-append → hand mới xuất hiện
             cuối list là CỦA MÌNH (engine xử lý atomic theo queue index;
             core giữ vị trí fib rẻ 1..n, mình nhận vị trí đắt n+1..)
           • wheat feed contract: bridge BUY_PRODUCT (sau morning sell-ALL
             của core, trước giờ PICKUP của hands) + rescue giữa ngày
           • market tail slots: đơn của mình đứng SAU đơn của core, bị
             truncate trước khi đơn core bị cắt
           • greedy stateless ladder mỗi hand mỗi turn:
             FEED(rescue) > PLACE > PICKUP > CARE > HARVEST(≥2) > BUILD/DIG
             > walk-to-duty; yield cho lệnh DROP/PLACE của core từ h20+
           • fail-open: 3 lỗi/ngày → tắt tới hôm sau; exception → pure core
```

Bài học kiến trúc (chuyển được cho hướng khác): **receipt-claim ownership**
và **stateless ladder** giải quyết được vấn đề "không thể layer-wrap lao động"
— cái chết của họ v21/v22 là market-order-layer, không phải unit-command.
Layer unit-command LÀ khả thi nếu ownership được receipt hóa.

## 2. 4 VÒNG FORENSIC (mỗi vòng: bug thật → fix → đo lại)

| # | Thiết kế | Phát hiện forensic | Số |
|---|---|---|---|
| 1 | v23.0 NE-zone, steal-hands | 7 ngỗng kẹt shed 17 ngày: gate `total<target` đếm ngỗng-shed vs homes → pump tắt vĩnh viễn; trim SELL WHEAT whole-order → free-rider v46 +$8.6K | −$18.6K |
| 2 | v23.2 bootstrap-safe | bootstrap deadlock: k_need=0 vì không ngỗng→không hire→không build→không mua; core mua NE d5-7, dâu tràn zone 14→2 ô trong 16h; hire window h1-3 trôi qua trước lúc unlock | −$10.9K |
| 3 | v23.4/5 pre-positioned builders + hire mọi giờ | builders đứng sẵn TRÊN ô LOCKED (movement cho phép) → BUILD ngay giờ unlock; zone 14 coop xây đủ. NHƯNG: ladder bug `return PASS` khi đứng trên ngỗng duy nhất hết việc → 2 hands PASS 16 giờ, 10 ngỗng kẹt shed; wallet core gầy ($27-760) tới d11 | −$41K single-seed |
| 4 | v23.6/7 SE-clean | section-1 fall-through fix → engine chạy full (placed 6-14, eggs 220). SE quadrant = 25 ô $4,000 KHÔNG AI dùng → zone 14 coop zero chi phí tile + core được tặng 11 ô | −$13K seed 3 |

## 3. NĂM BỨC TƯỜNG KINH TẾ (đo bằng battery + A/B tách biến)

1. **Tường tile**: mọi ô coop có shadow price = giá trị crop biên của core
   (~$60-70/ô/ngày ở NE). Chuyển sang SE tưởng zero-cost nhưng **A/B land-only
   cho thấy bản thân land buy là −$6.7K**: corefarm SE sub-marginal (chưa bao
   giờ tự mua SE) và crop mới làm loãng giá cả hai bên (v46 cũng −$1.8K).
   $4,000 land là sunk cost, không được hoàn.
2. **Tường fib-labor**: hand #11-15 = fib $89-610/ngày/hand. Ngỗng cần 2-3
   hands = $466-1,220/ngày cuối game. Thu nhập trứng 24 × $45-70 = $1.1-1.7K/ngày
   trừ feed + hands → biên $100-500/ngày, KHÔNG đủ trả $7.6K capex trước d29.
3. **Tường feed**: wheat $35-42 (core chính là wheat-hungry, tự bridge-buy
   5-15/ngày). 1 wheat → 2 eggs ≈ $90-100 gROSS; feed+labor ăn sạch biên.
   Bridge mua còn bơm giá wheat cho cả v46.
4. **Tường displacement**: claimed hands xuất hiện trong obs của core → core
   plan việc cho TẤT CẢ hands → override đuôi = việc core định giao bị bỏ
   dở (đo A/B: goose-engine trên nền land −$8.3K thêm, vượt xa chi phí trực
   tiếp $4.2K ngỗng + $2-4K hire).
5. **Tường free-rider (lần 3 gặp)**: mỗi đơn vị output bị redirect (tile,
   labor, wheat) chuyển market share cho v46: v46 +$8.6K khi engine chạy
   (92,853 → 101,476). Giống hệt v21-v3 (vacate milk) và v22b (wool banking).

## 4. SỐ LIỆU CHÍNH (seeds 100-123, 48 trận/battery)

- v20 vs v46: 48W, avg $96,290 vs $94,642, gap +$1,647 (median ratio 1.020)
- v23l vs v46: 0W, avg $89,549 vs $92,853, gap −$3,304 (worst 0.844x)
- v23 vs v46: 0W, avg $81,271 vs $101,476, gap −$20,205 (worst 0.681x)
- Telemetry seed-3 (engine full): builds 13, geese_bought 14, placed 6,
  eggs_sold 220, feeds 83, cares 83, harvests 67, bridge 5u, hires 38,
  errors 0, yields_to_core 1
- WALLET: core giữ $27-760 từ d1-10, $10K+ từ d11 (bán wool/melon) — capex
  ngỗng chỉ có cửa ở d11+ → yield từ d17+ → còn 12 ngày bán

## 5. ARTIFACTS

- `kaggriculture/v23_layer.py` (planner ~480 dòng) + `v23.py` (430KB flat)
  + `v23l.py` (biến thể land-only A/B) + `build_v23.py`
- `kaggriculture/research/v23_resource_probe.py` (profile tài nguyên v20),
  `v23_goose_forensic.py` (trace vòng đời ngỗng + money từng turn)
- `bench/t91_v23_vs_v46.json`, `t91_v23l_vs_v46.json`, `t91_v20base_vs_v46.json`

## 6. HƯỚNG CÒN LẠI (sau khi animal-production đóng)

- **H2 peak-pricing** (sell timing trên chính output của core — không input
  mới, không displacement): bán muộn giờ vàng,測 thử window h0-2 vs h18-23.
- **Meta-level**: mirror ≠ Kaggle field. Top-tier $160-227K sống ở thế giới
  đối thủ không phản ứng kiểu v46. Submission v20.1 đang climb — dữ liệu
  matchmaking mới (sau 100+ trận) sẽ cho biết field thật khác mirror bao nhiêu.
- Lai anom: goose endgame của chính V43 (d28 BUY_ANIMAL GOOSE + terminal
  harvest) đã có sẵn trong core — không cần mở rộng.

## 7. QUYẾT ĐỊNH

- Submission: **GIỮ v20.1 (#56308666)** — đang climb, không reset cho một
  hướng đã đo là âm $20K.
- H1 (milk) + H5 (goose/EGG) + land-expansion: **ĐÓNG CỔNG TRONG MIRROR**.
- Bài học lớn nhất: trong mirror 2 người dùng chung thị trường, "thêm tổng
  giá trị" chỉ đến từ timing/price trên output hiện có (H2) hoặc từ trạng
  thái mà đối thủ không thể copy — KHÔNG bao giờ từ input mới (tile/labor/
  feed), vì input được định giá đúng bằng cơ hội mất của chính mình.
