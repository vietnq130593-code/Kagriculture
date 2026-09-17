# 10 — H1 KẾT LUẬN CUỐI: Milk Printer chết trong mirror, EGG/GOOSE là lever thật
## 10 thực nghiệm họ H1 · 2 bug layer · sim screening · phát hiện cấu trúc EGG

> Task 90 · 2026-09-18 · Bio
> Chuẩn đối: v20 (flat 410KB) vs ahmedv46, engine kaggle 1.32.7, 720 turn,
> battery 24 seed × 2 ghế. Sim: milk_sim.py (calibrated + engine-exact lockstep).

---

## 0. TỔNG KẾT HỌ H1 (10 thực nghiệm, mọi biến thể user yêu cầu)

| # | Biến thể | Cơ chế | Kết quả | Phán |
|---|---|---|---|---|
| 1 | v21-v1 | bank+liquidate WOOL/STRA/MELON | −$1,030 | dump tự re-crash |
| 2 | v21-v2 | trim-only WOOL floor 120 | −$307 | wash + free-rider |
| 3 | v21-v3 | COW→SHEEP swap | **−$17,995** | nhường monopoly milk |
| 4 | v21-v4 | floor-banker <$15 | ±0 | dead orders (engine no-op) |
| 5 | v21-v5 | v4 + 2 bugfix | +$9 | noise |
| 6 | v22 | milk banker reactive, floor 30 | +$81 [CI −32,+222] | noise |
| 7 | v22b | floor 50, enter sớm p<100 | +$217 [+53,+402] **nhưng 46W-2L vs v46** | flip 2 trận thắng thành thua |
| 8 | v22c | cap-bounded 20/40 | seed 21: **−76 THUA** | flap enter/stall-exit |
| 9 | v22d | evidence-only (inv-fell ≥8/2d) + one-shot | +$39 [−77,+157], **48-0 vs v46, worst +$603** | an toàn nhất, edge nhỏ |
| 10 | cow expansion (TFC core) | +6..18 bò (sim) | **−$5,775/6 bò** | chết toán học |

**Phán quyết H1: KẾT THÚC.** Dream +$40-80K không tồn tại trong mirror V45.
Tồn tại tối đa +$40-400/game từ timing (v22d = cách lấy an toàn nhất), không
đáng thay submission vì:
1. Kaggle submission mới = reset rating climb (đang leo từ 600);
2. +$31 mean nằm trong noise matchmaking;
3. Rủi ro flip game (v22b/v22c proof-of-concept thua 2 trận) > lợi ích.

## 1. VÌ SAO MILK CHẾT — 3 bức tường cấu trúc (đo từ engine + 8-seed probe)

1. **Drain yếu vs supply**: town center drain 1 milk/ngày + 6/shop-instance;
   mirror có 1-4 milk instances (7-25/ngày) vs supply 2 bên ~18+/ngày (12 bò
   2 bên + REAPER dump d27+). 6/8 seed: glut vĩnh viễn ($1-13).
2. **BUY_PRODUCT chỉ WHEAT/FERTILIZER** (engine L598-601) — không arb mua
   tận gốc được; chỉ bán được từ shed.
3. **Free-rider + lockstep**: mọi giá ta giữ lên bằng withholding, v46 bán
   thẳng vào (đo thực: seed 21 v46 +$195/game từ banking của ta). Walk
   interleaving 2 ghế làm kết quả lệch ghế tới ±$1,100 (seed 3: ghế A −$423,
   ghế B +$1,107).

TFC $250-306 milk sống ở thế giới đối thủ KHÔNG bán milk. Mirror V45: cả hai
dump daily → cộng giá trị phải đến từ item KHÁC.

## 2. HAI BUG LAYER HỌC ĐƯỢC (chỉ phát hiện bằng telemetry test — không bao giờ
hiện ở kết quả trận vì fail-open)

1. **NameError im lặng**: generate code bằng sed/replace → `_V22D_int` (viết
   hoa) vs `_v22d_int` → NameError 357 turn → fail-open → layer no-op mà game
   vẫn thắng bình thường. **Bài học: mọi layer build xong PHẢI chạy replay-test
   telemetry (0 errors + số action thay đổi > 0 trên seed mục tiêu).**
2. **low_days đếm theo TURN không theo NGÀY**: stall-exit nổ sau 1 ngày vì
   counter tăng 21 lần/ngày. Đã fix: đếm 1 lần/ngày + so inv end-of-day.

## 3. PHÁT HIỆN CẤU TRÚC: EGG/GOOSE = lever TFC-scale thật sự (đề xuất v23)

Phân tích MARKET_PARAMS + SHOPS + ANIMALS từ engine:

```
EGG:  base $50, trên-I0 "log 0.20" (GENTLE: +1200 glut chỉ rơi tới $38!),
      dưới-I0 "hinge 0.40" (RUN AWAY: −332→$70, −426→$88, −500→$121, −600→$190)
MILK: trên-I0 "linear 1.60" → −$2.1/unit (STEEP — crash ngay)
GOOSE: $300, COOP (BUILD_COOP MIỄN PHÍ — farmer action trên tile trống),
      first yield d4, interval 1 (HÀNG NGÀY), max_held 4, feed+care → ~2 egg/ngày
Hiện trạng mirror: EGG inv cuối −426 dưới I0, $88, drain 1+6×BAKERY+6×BRUNCH
      (2/8 shop types) nhưng supply chỉ ~2/ngày → THỊ TRƯỜNG ĐÓI
```

**Kinh tế 20 ngỗng (buy d1-2, yield d6, 24 ngày):** ~2 egg × 24 ngày × $45-88
≈ $43K/doanh thu; chi phí 20×$300 + 480 wheat (marginal ≈ 0 — máy wheat v20
sẵn) + ~50 action/ngày labor (4-5 hands). **Net ước +$25-35K** — 10-50× toàn
bọ họ H1. Curve log khiến glut TỐT cho giá (khác milk linear). Đối thủ copy
cũng không chết curve (đó là điểm khác căn bản vs milk).

Ràng buộc thật: (a) cần ~20 tile COOP (đất NW + mua quadrant, đè lên máy
wheat 153-ref — phải tính lại hỗn hợp); (b) labor planner FEED/CARE/HARVEST
mỗi ngỗng mỗi ngày; (c) ngỗng chết nếu unfed 2 ngày liên tiếp. Đây là kiến
trúc production-planner riêng (v23), KHÔNG thể layer-wrap như v2x.

## 4. ARTIFACTS

- `kaggriculture/v22_layer.py` → `v22d_layer.py` (4 thế hệ layer + build script)
- `kaggriculture/research/milk_sim.py` (sim calibrated), `milk_diff_probe.py`
  (forensic daily diff), `milk_reconstruct*.py` (engine-exact replay walkers)
- Battery JSON: `bench/t90_v22_vs_v46.json` (48-0 +$1,569), `t90_v22_vs_v20.json`
  (+$81), `t90_v22b_vs_v20.json` (+$217 CI>0), `t90_v22b_vs_v46.json` (46-2 ✗),
  `t90_v22d_vs_v20.json` (+$39), `t90_v22d_vs_v46.json` (48-0 +$1,601.5, worst +$603)

## 5. QUYẾT ĐỊNH

- **Submission giữ nguyên v20.1 (#56308666)** — đang climb, không reset cho +$31.
- **v22d** = increment đã verify an toàn (48-0, worst-case +$603 > v20 +$568),
  giữ làm base component khi build v23.
- **H5/EGG goose ladder = đề xuất nghiên cứu tiếp theo** (production planner),
  kèm PET_CAFE carrot (12 carrot/ngày drain ×2 multiplier — shop 1-item duy nhất
  có double drain).
