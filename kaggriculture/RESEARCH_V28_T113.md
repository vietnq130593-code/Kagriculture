# T113 — BÁO CÁO NGHIÊN CỨU v27.2 (4 NHÓM + THỊ TRƯỜNG)

**Nguồn dữ liệu**: mirror battle s200 (tape đầy đủ), vs-2945 s201, engine
source (kaggle_environments/envs/kaggriculture/kaggriculture.py 1086 dòng),
RULES.md, ladder server (81 episodes).

---

## 1. CÂY TRỒNG — LỖ HỔNG LỚN NHẤT: QUADRANT 4 KHÔNG BAO GIỜ MUA

| Phát hiện | Bằng chứng | Lãng phí ước tính |
|---|---|---|
| **Quad 4 ($4,000) không mua** | BUY_LAND d6 ($1k), d11 ($2k) rồi DỪNG; money $15k→$103k suốt 18 ngày sau | 25 tiles × wheat ~$1.8k/ngày × 17 ngày = **+$20-30k/ghế** |
| Đất bão hòa tuyệt đối d12-26 | empty=0, 58 cây + 17 vật = 75/75 tiles full | — |
| **FERTILIZE = 0 cho tới d14** | FERT ops: d0-13 = 0, d14+ mới 8-36; FRT free 17/ngày từ COLLECT_FERTILIZER đầy đủ | wheat bón = 6 units thay 3 (DOUBLE!): 25 cây × +3 × $38 × ~40 cycle-ngày = **+$4-5k/ghế** |
| ~26 cây/ngày unwatered | consecutive_unwatered ≥ 1: 25.74 mean | mất bonus window +1 unit ($38/cây/ngày trong window) |
| ~10.7 cây/ngày ready-unharvested | yield_units ≥ 2 đứng trên cây | tiền đọng, thu dần cuối game (chấp nhận) |
| COOP build d10 → DIG vứt d15 → build d28 trống | BUILD_COOP 2/ghế, cuối game trống | nhỏ + hành vi mù |

Wheat economics: seed $10, window tưới d2-4 (3 nước), yield 3 non-fert /
**6 fert** (cap 6, R7+engine WATER: bonus = 2 if fertilized). Straw: cap 4
units, FERT chỉ giúp đạt cap sớm (không tăng tổng — min(4, ...)).
CARROT chỉ d25+ (kịp thu) — đúng. TOMATO/MELON = 0 (R70: kênh này hại
trong nền feed-wheat).

## 2. ĐỘNG VẬT — GOOSE BỎ QUA (đối thủ 2945 đang dùng!)

| Phát hiện | Bằng chứng | Giá trị |
|---|---|---|
| **GOOSE = 0 con** | BUY_ANIMAL chỉ COW 6 + SHEEP 11/ghế; 2945 nuôi 2.95 GOOSE và THẮNG s201 | EGG interval 1 (sinh mỗi ngày), $50-65, R13 kênh #1 ($1/tile/ngày) — 2 GOOSE ≈ +$1.4k/ghế |
| 17 vật feed+care đầy đủ | FEED/CARE 17/17 ổn định d13+ ✓ | — |
| yield trên vật ~0 cuối ngày | thu đều, max_held 4-6 không đọng | ✓ |
| COLLECT_FERTILIZER 17/ngày đầy | 34 ops/2 ghế mỗi ngày | ✓ (dòng FRT free 17/ngày!) |
| unfeed 2 ngày → vật THOÁT | không quan sát thoát (count ổn định) | ✓ |

## 3. LAO ĐỘNG — DƯ RẢNH KHÁ LỚN

- Hands reset về 0 mỗi cuối ngày (engine `_end_of_day`) → hire lại từ fib(1):
  chi phí 9.4 hires/ngày = **$88/ngày/ghế** — rẻ so với thu nhập $5-8k/ngày
- **PASS 1,422 unit-turns/30 ngày** (~12/ghế/ngày) — dư địa WATER/FERTILIZE
- PASS-gold: patch PASS → op tĩnh tại chỗ (WATER/FERTILIZE) KHÔNG phá
  chassis (không đổi vị trí unit)

## 4. KHO — SẠCH (không ưu tiên)

- shed_late ~6 units, end-shed ~0, capacity 100 không tràn
- Endgame WOOL 10 đọng bán $1 (sàn) — chấp nhận
- Inventories đổ shed cuối ngày; overflow discard — không quan sát tràn

## 5. THỊ TRƯỜNG — QUY LUẬT

**Pricing engine**: price = base + amp·f(|inv−I0|), I0=10,000.
Bán → inv trên I0 → giá rơi theo above_func (log/sqrt/linear/sq).
**SELL lockstep: 1 unit/turn/lệnh** — lệnh SELL 16k units ≠ fill (tape EGG
lệnh 16k, thực fill nhỏ).
**Town hút**: mỗi 4 turns mỗi shop 1-2 units; 24 turns center 1/item —
shops unlocked (mỗi 3 ngày +1, drawn with replacement) quyết định item sống.

**Price curves (mirror, end-of-day):**
- MELON: 256→270 (đỉnh d6-8)→131 (d10)→78 (đáy d12)→hồi 118
- STRAW: 128→214 (đỉnh d16)→sụp 148 (d22)→157
- MILK: 169→191 (d6)→chết 28 (d18)→15 (d20)→11 (d28)
- WOOL: 206→236 (d8)→giữ 235 (d14)→SỤP 24 (d22)→1 (d28)
- WHEAT/CARROT/TOMATO/EGG: tăng đều 28→44, 35→51, 60→91, 50→65
- FERTILIZER: 100→3 (giảm liên tục)

**Insight quan trọng**: inventory cuối giữ ~I0 (WHEAT 9,826) — town nuốt
được sản lượng hiện tại; thêm ~50 wheat/ngày vẫn lời (seed $10, yield 6,
giá trượt $38→$20 vẫn $104/cycle). Bán nhiều hơn → giá chung rơi →
đối thủ (cùng market) thiệt trước → margin race có lợi cho producer.

## TỔNG LÃNG PHÍ/TIỀM NĂNG v28 (per ghế, ước tính thận trọng)

| # | Cải thiện | Giá trị |
|---|---|---|
| 1 | Mua quad 4 sớm + trồng wheat dày | +$15-25k |
| 2 | FERT wheat từ d0 (double 3→6 units) | +$4-5k |
| 3 | PASS → WATER/FERTILIZE tại chỗ | +$1-2k |
| 4 | GOOSE 2 con vào COOP (bỏ DIG mù) | +$1.4k |
| 5 | Tưới đầy window (fix unwatered) | +$1-2k |
| | **TỔNG** | **+$22-35k/ghế (~20-30%)** |

## RỦI RO & NGUYÊN TẮC PATCH

- Chassis v27.2 sell-layers nhạy butterfly (bài học Task 111: 1 fire 3-unit
  → ±$1k/ghế) → mọi patch phải đo full battery
- Patch an toàn: market-order-level (BUY_LAND, BUY_ANIMAL) + REPLACE PASS
  bằng op TẠI CHỖ (không MOVE) — không phá lộ di chuyển của chassis
- Kiểm chứng chassis TỰ trồng trên quad 4 sau khi mua (test nhanh: patch
  BUY_LAND → chạy → đếm cây trên quadrant mới)

## KIẾN TRÚC v28 (kế hoạch)

Layer v28 gắn CUỐI v27.py (giữ nguyên 100% chassis + v27.2 layers):
1. `_v28_quad4`: BUY_LAND khi quads==3 ∧ money≥4600 ∧ 8≤day≤20
2. `_v28_fert_wheat`: đổi PASS → FERTILIZE (unit đứng trên wheat chưa bón,
   FRT trong tay) + PASS cạnh shed → PICKUP FERT
3. `_v28_water_window`: đổi PASS → WATER (đứng trên wheat/straw chưa tưới)
4. `_v28_goose`: BUY_ANIMAL GOOSE ×2 khi COOP trống tồn tại + PLACE khi
   unit đứng trên coop trống (nhận PASS swap) — phase 2 nếu thời gian cho

---

## PHẦN II — KẾT QUẢ THỰC NGHIỆM 8 CẤU HÌNH v28 (s100 vs v27.2, cùng seed)

| Ver | Cấu hình | Kết quả | Kết luận |
|---|---|---|---|
| v28.0 | quad4-buy + PASS swaps | −$4,108 | $4k đất phí, SE trống |
| v28.1 | PASS swaps only | −$108 | noise |
| v28.3 | 1-hand override SE farm | −$22,740 | cướp 1 worker (~$1.2k/ngày) |
| v28.4 | 3-hand SE farm | −$48,554 | cây chết + 3 workers mất |
| v28.5 | 2-hand + FERT doubling | −$54,806 | cướp FRT phá chassis |
| v28.6 | GOOSE full-override | −$20,173 | geese đặt +$4.8k nhưng worker −$20k |
| v28.7 | GOOSE borrow-PASS-only | battery 10 trận: 0W-4L-1T mean −$3,975 | geese chassis tự lo (race mode); mượn PASS vẫn lệch sync |

Battery v28.7 (seeds 100-104 × 2 ghế): s100 −$667, s101 −$6,666, s102
−$6,840, s103 TIE, s104 −$1,700.

## PHẦN III — GIẢI MÃ CẤU TRÚC SÂU (tại sao mọi patch đều âm)

1. **V219 = SE TOMATO FARM SẴN CÓ trong chassis** (L1410-1500): d18
   `_v219_qualifies` (đúng 3 quads {NW,NE,SW} + money ≥$12k + TOMATO price
   + ≥3 shops PIZZA/FARMERS + tiles SE còn LOCKED + native routes sạch) →
   V219 TỰ MUA BUY_LAND + BUY_SEED TOMATO 10 + hire 2-3 crop workers →
   trồng tomato 10 tiles (y=5,6 × x=5-9) → FERT d24/27 → harvest d26-29 →
   SELL. Trận shops xấu (s200) → V219 off → quad 4 phí (đã quan sát).
2. **Race-mode geese**: chassis tự mua/đặt 5 GOOSE trong race mode (tape
   v28h: cả 2 ghế geese giống hệt d6+). EGG channel đã có.
3. **State-sync d4-8 + clone/race detectors** (L5854): các layer lockstep
   so khớp money/hands/land với đối thủ — mọi lệch (mua đất sớm, hire thêm,
   move unit) làm detector đổi mode → cascade tắt layers → sụp điểm.
4. **Hire cạnh tranh fib**: chassis h0 dùng 9-10 HIRE (queue 10 đầy);
   hire của tôi = thứ 10-14 → $55-377/hand/ngày. Chassis plans commands
   cho TẤT CẢ hands (cmds == hands 719/718) — không thể có "hand riêng".
5. **Override = cướp worker**: 1 hand bị override cả ngày ≈ −$20k/game.

## KẾT LUẬN & ĐỀ XUẤT

**v27.2 là local optimum trong không gian can thiệp additive.** 8 cấu hình
đều âm (−$108 tới −$54k). Cải thiện đòi hỏi:
- **Đường A** (an toàn): giữ v27.2 nguyên vẹn — đang 120/120 local +
  Kaggle 56386175 đang chạy
- **Đường B** (đầu tư lớn): re-architect chassis planning 100 tiles từ
  init (đường build_v2X chain), không patch ngoài — 1-2 session
- **Đường C**: exploit race/clone detector chống clones trên Kaggle

Artifacts: v28.py (v28.7 experimental — negative result), bench/t113_*
(audit tools + batteries + probes), RESEARCH_V28_T113.md.
