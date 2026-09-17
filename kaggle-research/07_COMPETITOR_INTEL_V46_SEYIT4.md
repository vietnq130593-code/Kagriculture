# 07 — COMPETITOR INTEL: seyitkaangunes (rank ~188) & ahmedberatozer V46
*Task 87 · 2026-09-17 · Bio · nguồn: 2 public notebook Kaggle, pull qua API + SHA256-verify*

## 1. Nguồn & xác thực

| Đối thủ | Notebook | Kết quả extract |
|---|---|---|
| **seyitkaangunes** — "KaggressurE: V44 + Four Market Layers" (2801 rating, rank ~188/9246, snapshot 16-09) | `seyitkaangunes/kaggressulture-2820-score` → `kaggle-research/competitors/nb_seyit/` | Base V44 = **byte-identical** với `ahmedv44.py` local (sha256 `797d9bca…`); 4 layer files extract từ cells 5/7/9/11 |
| **ahmedberatozer** — "KaggressurE V46: First-Turn Microstructure and Sale Timing" | `ahmedberatozer/kaggressulture-v46-first-turn-microstructure-and-s` → `nb_ahmed/` | main.py 333,658 bytes, sha256 `735c3703…` verify OK |

**Tái tạo được agent live của seyit:** nối `ahmedv44.py` + 4 layer theo LAYER_FORMAT
(README cell 13) → sha256 `fa9e47d81de50208…` = **đúng byte submission live 56280605**
(4-layer build). File: `kaggressulture/seyit4.py`. Cả 2 đối thủ giờ là sparring partner
trong arena (`seyit4`, `ahmedv46`).

## 2. seyit4 = V44 + 4 wrapper layer (chỉ chạm market + herd, không đổi farming)

| # | Layer | Cơ chế | Bằng chứng (vs V44, mirror cả 2 ghế) |
|---|---|---|---|
| 1 | **Preguard h21-22** | Dự báo overflow shed cuối ngày bằng chính helper của chassis (`_r127_fields` + `_r97_market_stock`); bán trước 6 units (target 93) theo giá giảm dần, items {MILK, STRAWBERRY, MELON, WOOL, TOMATO}, giá ≥2. Giữa market h20 và h0 không có consumption → bán h21/22 cùng cửa sổ giá nhưng **đua trước** dump h23 của đối thủ V44-family | 38-2, **+562…834** |
| 2 | **Lockstep SELL reorder + horizon 9** | Khi detect clone (race mode): hoán vị từng block SELL liên tiếp 2-6 đơn, replay lockstep 2 người chuẩn engine, chọn hoán vị max (own − clone) revenue; chỉ nhận edge > $0.5. Horizon race 8→9 (bán trước clone 1 lượt) | **20-0, +1436** |
| 3 | Cadence (town ticks) | Giữ floor(n/2) units qua tick %4, bán lại phase 1 sau tick | 64-2, +30…70 (tie-breaker) |
| 4 | **Yarn herd** | YARN_STORE là shop thứ 3 (ngày 8-11): swap COW/GOOSE→SHEEP, rewrite PICKUP/PLACE/BUILD_COOP→PASTURE, gộp len vào SELL có sẵn (không thêm slot) | Yarn seeds: 18-0, **+3770** |

Live: 3-layer 26-3 (2801); 4-layer 22-2, tiền TB **115.9k vs 86.3k**.
Plain V44 plateau 2630-2657 → 4 layer cộng ~+150-170 điểm rating.

**Phương pháp đáng học nhất — "live-opponent tape testbed":** tải replay trận live của
mình, extract toàn bộ action của đối thủ thành "tape", replay y nguyên (đúng seed +
ghế) → test thay đổi trên đối thủ THẬT của ladder. Replay chuẩn xác đến từng đồng
(26-3 khớp 29 trận live). Đây là cách vượt hạn chế "chỉ test được với agent public".

**Âm tính quan trọng (thứ KHÔNG hoạt động):** cap HIRE mỗi ngày (0-6, −9883!), pipe-5
settings lên V44 (2-4), opening C9 cluster (+1 coin), wheat-pump cũ (thắng local 60-70k
rồi sụp live 1622 — "local wins against yesterday's agents mean little").

## 3. ahmed v46 = V45 + First-Turn Microstructure (EXP284→EXP293)

Diff v45→v46 (xác định bằng sequence-diff toàn file):
1. **Opening turn 0:** thay round-trip [BUY 70, SELL 70] (của v45) bằng **[BUY 7, SELL 2]**
   — mua đúng 5 units feed ở **index 0** (quote rẻ nhất, không ai đẩy trước), units dư
   bán 2 ở index 1 (ăn theo lift của đối thủ nếu có). Round-trip lớn **thua 32-77 cash**
   khi gặp [BUY 5, SELL 5]/[BUY 50, SELL 50] — và bị 2 đối thủ live [BUY 78, SELL 78]
   hút mất 1 melon seed.
2. **Turn 1 strip + attack:** cả dòng họ V43..V46 mua 5 feed ở **index 1** turn 1
   ([SELL 13, BUY 5, …]). V46 strip 2 đơn đó của mình + **BUY 30 wheat ở index 0**
   (gate cash ≥ 2860) → đẩy quote feed của đối thủ +$4/unit, vượt day-0 slack 8 cash.
   Turn 2 bán trả 30 units vào quote đã đẩy — **trip tự trả tiền** (đo trên engine:
   buy −$886, sell +$901; nạn nhân BUY 5 trả thêm $25).
3. **Sale advance (EXP293, "Beyond 48-0" của jaxa tái hiện trên chassis ahmed):**
   LOOK=3 turn, projected shed, protect-first, giá ≥2, sort giá giảm; **frontload
   order: sells → product-buys+wash → rest**; từ step 144.
4. **EXP288 mirror gate:** step 1, cash đối thủ == cash mình (±0.5) → đối thủ là bản
   copy (cùng chạy round-trip) → horizon race = 24 (pre-empt cả ngày).
5. **EXP293 race-lost detector v2:** đối thủ bán race-product lượt trước khi ta còn
   giữ + tape không bán trong 5 turn tới nhưng bán trong 24 turn tới → escalate
   horizon 24.

Eval độc lập của họ (1,216 game): +17.8pp match points vs predecessor; **vs jaxa-family
(pub_beyond48): 0-64 → 52-12**. Đây chính là lý do v18/v19 nhà ta thua v46.

## 4. Định vị của chúng ta (battery 24 seeds × 2 ghế, official runner)

| Matchup | Kết quả | Kết luận |
|---|---|---|
| v19 vs seyit4 | **46W/2L, +$1,225** [+1009,+1438] | Ta mạnh hơn head-to-head — rating của họ đến từ việc farm clone-family trên ladder |
| v18 vs seyit4 | 46W/2L, +$1,205 | Như v19 (nền jaxa là lợi thế chính) |
| v19 vs ahmedv46 | **2W/46L, −$396** [−519,−284] | Opening + sale-timing của v46 khắc chế dòng jaxa |
| v18 vs ahmedv46 | 2W/46L, −$506 | Như v19 |

## 5. Phát hiện pháp y quan trọng nhất: V43 chassis ĐANG ĐỐT TIỀN

Phân tích battle JSONL (3 trận, cả 2 ghế): V43 **không có day-end storage guard**
(V44 mới thêm EXP-154). Mỗi h23 engine deposit carried → shed, phần vượt 100 bị
**PHÁ HỦY**:
- Overflow xảy ra 8-10 ngày/trận (d18-28), 2-28 units/ngày
- **~90-116 units/player/game bị destroy, 96% WHEAT** + ít CARROT
- Giá wheat những giờ đó $22-42 → giá trị danh nghĩa $3-7K/game
- Giá trị thực (trừ cơ hội bán d29 ~$21): **~$1.3-1.6K/game** (đã verify bằng smoke
  v192 vs v191: overflow 79→8 units, chênh lệch +$900/seed)
- Cả dòng V43 trên ladder đều chảy máu ở điểm này; V44+ đã vá

Shed composition h21/22 của ta: WHEAT 69%, EGG 16% (khác V44 → item list khi port
Layer 1 phải thêm WHEAT+EGG, loại CARROT — giá tăng 8x cuối trận $35→$280, và
FERTILIZER — input của tape).

## 6. Kế hoạch áp dụng (đang triển khai)

| Bản | Layer mới | Nguồn cơ chế | Trạng thái |
|---|---|---|---|
| v19.1 | Opening [BUY 7, SELL 2] + strip + BUY 30 attack + sellback | v46 EXP284/293 | ✅ build + smoke khớp số v46 từng đồng (2872→174, shed 35, sellback 30) |
| v19.2 | Preguard h21-22 (item list thích ứng V43) | seyit L1 | ✅ build + smoke: overflow 79→8, +$900/seed |
| v19.3 | LOOKAHEAD 2→3 (override namespace v18) | v46 _ADV_LOOK | ✅ build, chờ battery |
| v19.4 | Lockstep SELL reorder vs clone | seyit L2 | ✅ build + smoke, chờ battery |

Gates battery mỗi bản: vs ahmedv46 (mục tiêu đảo chiều), vs nền ngay dưới (không
thoái hóa), vs seyit4 + ahmedv43 (giữ lợi thế clone-family).

## 7. File map

```
kaggle-research/competitors/
  nb_seyit/kaggressulture-2820-score.ipynb        (notebook gốc)
  nb_ahmed/kaggressulture-v46-first-turn-….ipynb  (notebook gốc)
  seyit_markdown.md, seyit_cell{3,5,7,9,11,13}.py (extract)
  seyit_v44_base.py, seyit_4layer_main.py         (base + build 4-layer, sha-verified)
  ahmed_cell*.py, ahmed_v46_main.py               (extract + main.py sha-verified)
  build/layer{1,2,3,4}*.py                        (4 layer file của seyit)
kaggressulture/
  seyit4.py, ahmedv46.py    (sparring agents, đăng ký arena + UI)
  v191/192/193/194.py + *_layer.py + build_v19x.py (các bản v19.x)
  bench/t87_*.json          (battery results)
```
