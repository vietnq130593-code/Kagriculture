# 01 — TOÀN CẢNH KAGGLE KAGGRICULTURE META (snapshot 13/9, Task 74)

> Nguồn: Kaggle API `kernels/list?competition=kaggriculture` — 493 notebook public duy nhất;
> 10 trang sort-by-votes + 3 trang sort-by-date-run. 34 notebook đầu tải về + phân tích code-level.

## 1. BẢN ĐỒ VOTES — TOP 40 (định vị các "trường phái")

| # | Notebook | Votes | Bản chất (sau khi mổ) |
|---|---|---|---|
| 1 | bovard/getting-started | 1083 | Agent contract chính thức (không phải agent mạnh) |
| 2 | boatlee/v16-rc5 | 313 | 8C/4S tape (Nikita 55440039) + premium market lead 1-turn |
| 3 | kaitofukami/v27 | 200 | Tape Ezzzzzekki + continuation reset từ step 161 + sparse SELL ordering |
| 4 | raykkretzschmar/findings | 187 | **NHẬT KÝ NGHIÊN CỨU** c14→C95 (đọc bắt buộc) |
| 5 | boatlee/84-84-clone-preemption | 149 | Clone preemption có sổ nợ (84/84 holdout) |
| 6 | tetsutani/adaptive | 142 | BL-Kawashigi-V19Core: 5 tape theo shop + guard dày + counters đóng băng |
| 7 | kaitofukami/v48 | 132 | 40/40 early floor — clone-preempt debt-ledger + fast routes |
| 8 | yhay81/six-day-fieldbook | 131 | Methodology đo 188 external histories (24k game) |
| 9 | romantamrazov/hamburger | 129 | Clone Quad H1: staged herds + front-run khi phát hiện clone |
| 10 | yhay81/shop-router-0909 | 127 | **Tổ tiên chassis của v15 ta** (SHOP_PLANS 13 tape) |
| 11 | tetsutani/shape-the-shop | 126 | Biến thể của tetsutani family |
| 12 | yhay81/three-day-shop-router | 121 | Router chu kỳ 72-turn + budget guard |
| 13 | raykkretzschmar/rank-your-agent | 111 | Tool xếp hạng local (paired-seat protocol) |
| 14 | pilkwang/structured-economic-policy | 106 | Scheduler + scenario-admission + SaleLedger (upstream của kme3!) |
| 15-17 | ahmedberatozer/more-yield (103), prvsiyan/soil (103), tetsutani (126) | ~100+ | Xem ANALYSIS_POLICY_ENGINES / PRVSIYAN_TETSUTANI |
| 18-25 | thomastschinkel routers (99+81), georgymarin visualized (98), indarkarhana (94), prvsiyan/moon (93), flexonafft multi-route (93), boatlee v16-rc2 (81), ahmed v38 (88), salemali7 2900 (77) | ~80-100 | Các family chính |
| 26-40 | kaitofukami v21.1 (102)/v20 (75)/v43 (76), cjlcjlcjl live-meta (75), andrewsokolovsky tie (73), reyhanksatria (78), guruprasaathas v39 (72), lynnsakurai (72), boatlee v29-r1 (69), jek1wantaufik (76)... | ~70-100 | Đầy đủ trong ANALYSIS_* |

**Nhận xét quan trọng**: nhiều notebook votes cao là *research/tool* (raykkretzschmar, yhay81 fieldbook, georgymarin,
cjlcjlcjl) — giá trị votes ≠ sức mạnh agent. Ngược lại guruprasaathas chỉ 72 votes nhưng là **đối thủ thật mạnh nhất
họ KaggressurE** (kme3 → kme3v10 → V39).

## 2. GIAI ĐOẠN TIẾN HÓA META (từ nhật ký raykkretzschmar + live-meta cjlcjlcjl)

```
melon tutorials → cow ranches → staged mixed herds (C0x) → economic schedulers (pilkwang)
  → tape routers (yhay shop-router, 13 tape theo cặp shop ngày 6)
  → stable c14 efficiency schedule (senkin refresh, 8c/6s)
  → c15 clone-aware sale front-run (+1.8k mirror)
  → c18 premium-liquidation schedule (edge = MARKET, không phải farm)
  → c27 terminal-717 correction (step 718 chạy, 719 không)
  → c45 debt-tracked 2-turn pull-forward (horizon 25 BỊ LOẠI 0-6)
  → c68 THUNDER field + ONLINE opponent-horizon inference (fit H1-6, default H4)
  → c70/c71 impact-first SELL ordering (Giovanni tape)
  → c72 one-step intraday banking ≥$2000, 1-move-from-shed (threshold 500/1000 = THẤT BẠI)
  → C90-C92 weed repair (chỉ repair action bị chặn, resync tại PASS)
  → C93 quadrant-4 BROAD NEGATIVE (mọi biến thể SE thua 10-0)
  → C94 feed-first slot-0 + fertilizer preemption cap 10 (88-14, BT 1837)
  → C95 pull 10 wheat + 5 fertilizer (112-8)
KAGGLE LIVE: 7/30 median Elo 670 → 8/6 2973 (4.4× trong 7 ngày!)
  8/7: 8c6s modal 54% → 8/10-11: 9c4s+1w+10h modal 30% (hiện tại)
```

### Sự kiện meta quan trọng
- **Top-30 opening collapsed**: 26/30 teams cùng 1-COW/4-SHEEP/HIRE4 (Kaito v27 audit 8/10). Opening classifier hết giá trị.
- **Top players HARDCODED**: kakuteki/venks 100% trace giống nhau qua các game; riêng Seb (LB#1-era ~3204) adapts 35-66%.
- **Leaderboard 8/12**: #1 カワシギ 3179.7 · #2 researchstudio.site 3174.3 · #3 Kaito Fukami 3133.9.
- **Rating = lottery khi mirror**: cùng byte-code có thể 2182 hoặc 1210 → 1865 tùy pool đối thủ (raykkretzschmar §4.4);
  xác nhận luật L38 (mirror knife-edge) của ta từ phía bên ngoài.
- **Engine 1.32.x có sẵn daily-replay dataset chính thức** (`kaggriculture-episodes-index`, 20GB/ngày, manifest.csv có avg_score)
  → tool kéo meta mới mỗi ngày đã được 3 nhóm (cjlcjlcjl, georgymarin, raykkretzschmar) dùng như workflow chuẩn.

## 3. CÁC FAMILY CHIẾN LƯỢC (7 họ chính, sau dedupe)

| Họ | Đại diện | Kiến trúc | Điểm mạnh | Điểm yếu khi gặp v15 ta |
|---|---|---|---|---|
| **KaggressurE** (guruprasaathas/pilkwang/ahmed/reyhan) | kme3→v10→**V39** | Planner beam-search + joint plans + 12 tape theo shop | Đối thủ mạnh nhất ta từng đo; V39 +3 layer mới | Đã thắng 10/10 nhưng gap chỉ +$3.2k — V39 chưa đo |
| **Kaito** (LB#3) | v18→v48 | Tape top-player + micro-timing layers | Conditional Memory 177/180; chống clone tốt | Clone-preempt tự tắt (ta không phải near-clone tape) |
| **boatlee** | V14→V16-RC5→V29 | Tape Nikita 8C/4S + market lead/hysteresis | Impact-model giá phi tuyến khớp engine; mirror latch | Route cố định — bị steering nếu bị đọc |
| **thomastschinkel router** | v3.1→v5 | 5 tape + decision tree mỗi 144 turn | 93.8% win rate claim; rẻ; chống variance shop-draw | **Router bị steer qua public state** (CARROT ≤54 → tape3 tồi) |
| **yhay81** (tổ tiên ta) | shop-router 0909 | 13 tape chọn theo 2 shop đầu | Chassis tốt (ta kế thừa), budget-guard 72-turn | Đã thua v15 10/10 |
| **tetsutani/BL-Kawashigi** | adaptive 142v | 5 tape theo vị trí YARN + 10 guard | Counters đóng băng R5/MD; FERT-heavy 2932u | Counter tự tắt với herd 8C/6S của ta |
| **indarkarhana E776** | top-10 94v | Kenjo1209 medoid 9C/5S/HIRE290 + guard dày | Contested-value SELL ranking; sequential funding | **Đối thủ mới ngoài registry — phải build proxy** |

## 4. ENGINE FACTS XÁC NHẬT LẠI (từ georgymarin, tính từ 1.32.7)

- **Profit/tile-day**: MELON **$142** ≫ CARROT 28.3 > STRAW 23.8 > WHEAT 22.5 > TOMATO 17.3
- **Giá trị CARE cuối mùa** (đã cared vs fed-only): SHEEP **+$5.575** · COW +$4.635 · GOOSE +$1.675 — CARE đáng 5-15× feed-only
- **Độ sâu crash $1 floor**: WOOL **59u** · STRAW **62u** · MILK **76u** · MELON **158u** · WHEAT/EGG: không chạm
- **100 melon 1 lượt = 87% giá trị** (so với bán rải)
- Wheat cần fertilizer mới đạt cap 6; melon đạt cap 6 chỉ bằng watering (age 6-10, fert melon = lãng phí)
- Shop demand: `%4 turn` (shop) ×2 nếu 1-product, center `%12` ×1/2/4 theo ngày — **giờ 0 = tick demand kép**
- Fertilizer: mỗi thú 1 unit/ngày (boolean — không thu là mất); SELL FERTILIZER được engine chấp nhận

## 5. SỨC MẠNH TƯƠNG ĐỐI (ước lượng từ claims + battery của ta)

```
starter << pure cow << melon IPO << C03/C05 << yhay routers < c11-c14 < hamburger < c27 < c45 < C70/C71 < C72 < C90-92 < C94/C95 (raykk)
     kme3(v37) < kme3v10(v38) < kme3v39(v39 — CHƯA ĐO)
     v15 ta: thắng 10/10 mọi đối thủ local (v13/kme3/kme3v10/aurax), gap +$3.2-4.1k
```

- Kaito v21.1 claim **177/180 vs top-30 replay** (counterfactual, đối thủ đóng băng) — con số cao nhất public.
- thomast v5 claim 93.8% qua 44.096 game replay.
- boatlee V16-RC5 claim 60/60 vs route-core reconstructed.
- ⚠️ Mọi claim đều là **replay counterfactual** (đối thủ không phản ứng) — chỉ dùng để xếp hạng cơ chế, không phải live score.

## 6. NHỮNG GÌ META ĐANG LÀM MÀ TA CHƯA (gap analysis v15)

1. **Không có refresh pipeline replay Kaggle** — 3 nhóm top đều kéo daily episodes dataset; ta chỉ có 3 replay user tải tay.
2. **Không có conditional memory** (đoán bán của đối thủ từ chữ ký farm public) — v15 chỉ front_run theo lịch trình giả định.
3. **Không có impact model giá** — v15 sorts theo giá hiện tại; Kaito/boatlee sort theo *giá sau khi tự đổ* (phi tuyến).
4. **Terminal relay OFF** — mega-SELL 716-718 + dead_stock chưa bật (2 A/B rẻ nhất).
5. **Đối thủ battery lạc hậu** — không có kme3v39, kawashigi, indark_e776; không đo được vs meta hiện tại.

## 7. RỦI RO / CẢNH BÁO CHUNG TỪ META

- **Balance Changes discussion** (34 votes): engine có thể đổi → tape chết hàng loạt. Adaptive layer (như Seb) là bảo hiểm.
- **Cùng upload 2 submission gần giống nhau = chết cả 2** khi meta shift (raykk §7) → giữ 2 slot submission khác họ.
- **Kaggle rating instance là lottery** — đừng đuổi điểm số tuyệt đối, đuổi win-rate vs meta mới nhất.
- **File-runner**: kaggle-environments chọn callable cuối cùng bind trong namespace → main.py phải kết bằng binding mới (R80 của ta đã đúng).
