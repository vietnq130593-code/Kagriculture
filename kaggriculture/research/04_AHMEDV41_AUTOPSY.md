# 04_AHMEDV41_AUTOPSY.md — Đối thủ nặng ký mới nhất (Task 79, 2026-09-14)

## 1. Nguồn gốc & xây dựng

- Notebook: `ahmedberatozer/kaggriculture-v41-review-candidate` (pull qua API 2026-09-14, 366KB)
- Tác giả: **Ahmed Berat Özer** — chính là cha đẻ của dòng V39 mà ta đã có trong registry dưới tên `kme3v39` (55% code chung, cùng chuỗi layer R42→R97; các file ghi rõ attribution "Ahmed Berat Ozer")
- Cấu trúc: 13 cells; cell 4 = `%%writefile main.py` toàn bộ agent 331KB/3175 dòng; 25 lần định nghĩa `def agent` chồng lớp — **lớp cuối (L3157) thắng runtime**: `agent = R128(R127(R97(...)))`
- Self-contained: chỉ stdlib (copy/base64/json/zlib/math/itertools); tapes nhúng base64+zlib; KHÔNG đọc file ngoài
- Build: copy nguyên văn → `kaggressurE/ahmedv41.py`, đăng ký 3 tầng registry (run_battle.py / arena-service index.ts / constants.ts) — registry giờ 18 agents
- Verify entry: `agent(obs, None)` → opening `[['BUY_PRODUCT','WHEAT',5],['BUY_PRODUCT','WHEAT',10],['SELL','WHEAT',60]]` ✓

## 2. Self-claims trong notebook (đối chiếu độc lập)

| Cohort | Kết quả V41 | Kết quả V39 |
|---|---|---|
| Direct 128 games vs V39 | 128/0/0 (+$25.0k) | — |
| Direct 128 games vs V40 | 128/0/0 (+$24.6k) | — |
| Working public 3,200 | 98.25% | 94.81% |
| New current elite 352 | 61.9% (+$18.0k) | 56.3% (+$12.3k) |
| Physical checks (vs V39) | feed shortfalls **0** vs 138 · escapes **0** vs 64 · pickup shortfalls **0** vs 49 | |

- Caveat chính họ tự ghi: confidence gate 95% CI [−1.14, +12.22]pp vs elite = **FAILED** (chưa đủ chứng minh vượt elite), và không claim điểm ladder 2800+
- **Đối chiếu local của ta**: kme3v39 vs ahmedv41 seed 362 → $77,843 vs $101,321 (v41 thắng +$23.5k) — khớp chiều claim "thắng V39 128/128"

## 3. Kết quả 10 trận: v16 vs ahmedv41 (seeds 360-364 × 2 ghế, battery t79)

```
wins 0/10 | avg $92,019 vs $121,132 | gap −$29,113 | ratio 0.760x | worst 0.695x
seed 360: −$39,390 | 361: −$7,399 | 362: −$28,099 | 363: −$30,548 | 364: −$40,131
```

**Đối thủ mạnh nhất từng gặp — 0/10, thua ngược hoàn toàn** (trước đó tệ nhất là 8/10 THẮNG). Engine deterministic: cùng seed cho cùng kết quả cả 2 ghế.

## 4. Giải phẫu (replay đầy đủ s361/s364/s365 + smoke s360)

### 4.1 Hai bên chạy GẦN NHƯ CÙNG MỘT tape
- Orders BUY_ANIMAL **giống hệt từng bước**: s1 COW×2+SHEEP×2, s65 COW, s88 COW, s150 COW×2, s169 COW, s176 COW, s196 SHEEP×2, s217 SHEEP, s226 SHEEP, s241 GOOSE×2, s265 GOOSE (tổng 8 COW + 6 SHEEP + 3 GOOSE)
- Plants: MELON 12 / WHEAT 162-163 / STRAW 33 / CARROT 31 (giống nhau)
- Hires ~253-254, quadrants NW+NE+SW, mua WHEAT feed day0-9: đều 102u
- Giá thú: GOOSE $300, COW $400, SHEEP $500

### 4.2 Khác biệt #1 — SALE-CREDIT tại đúng thời điểm mua (cơ chế quyết định)
- v41 tại s65: `$249` trong tay, order = **`SELL FERTILIZER 4` → `BUY_ANIMAL COW`** — engine thực hiện tuần tự trong lượt → doanh thu FERT ($216) cấp vốn cho COW ngay cùng turn → mua được
- v41 tại s196: `SELL MILK 12` → `BUY_ANIMAL SHEEP 2` ($668+$552 ≥ $1,000) → mua được
- v16 cùng thời điểm: $84 (s65), $73 (s196) — **không có SELL dẫn trước** → order BUY_ANIMAL chết im, tape không retry
- Đây chính là lớp `_r128_credit_supply` + "sequential funding ledger" (cùng kỹ thuật E749-E776 của indark)

### 4.3 Khác biệt #2 — đàn vật đầy đủ vs thiếu hụt (hệ quả của 4.2)
| Game | v16 herd cuối | v41 herd cuối |
|---|---|---|
| s364 | 5 COW + 5 SHEEP + 3 GOOSE = **13** | 9 COW + 5 SHEEP + 3 GOOSE = **17** |
| s365 | 5 COW + 4 SHEEP + 3 GOOSE = **12** | 8 COW + 6 SHEEP + 3 GOOSE = **17** |

### 4.4 Khác biệt #3 — bỏ đói vật nuôi (v16 lỗi systemic)
- v16 để 1 con COW (4,4) đói 2 ngày liên tiếp ngay d0-2 → **bỏ trốn** (engine: `consecutive_unfed >= 2` → escape); lặp lại ở cả 3 replay
- Nguyên nhân: d0-1 v16 chỉ có 2-3 worker nhưng phát 1 lệnh FEED/ngày (worker bận route) → tile (4,4) không bao giờ được feed
- v41 feed đủ 100% (đó là cải tiến bán chạy nhất của họ: escapes 0 vs 64)
- Lưu ý engine: vật KHÔNG cần feed vẫn đẻ (+1/lần interval), feed chỉ cần cho (a) tồn tại (b) care bonus (+1 unit khi feed+cared ngày đẻ)

### 4.5 Khác biệt #4 — opening thanh khoản
- v41 step 0: `BUY WHEAT 5+10` rồi `SELL 60` (clamp theo shed ~20) → **đổ sạch starting wheat thành tiền mặt, net +$34**, giữ $3,034 lỏng
- v16 step 0: `BUY 13+30` (executed 14) giữ feed stock → chỉ còn $2,609 + 13 WHEAT
- Chênh lệch $425 này + cascade 4.2 giải thích toàn bộ khoảng cách tiền giai đoạn d4-8 ($275 → $1,475)

### 4.6 Dòng tiền & gap
- Gap ngày cuối (v41−v16): +$16.5k-19.2k (s365), +$40k (s364) — mở rộng đều đặn +$0.5-1.5k/ngày từ d10 (khi đàn bắt đầu cho sản lượng)
- Executed sells (s365): v41 nhiều hơn WOOL 106u vs 66u (~$8k), MILK 132u vs 77u (~$2.7k), FERT 316u vs 239u (~$3k), STRAW 129u vs 104u
- Orders SELL "khổng lồ" (2,000u/lần) của v41 vô hại — engine per-unit lockstep, chỉ clamp theo shed

## 5. Phân rã gốc rễ thất bại của v16 (3 lỗi)

1. **Cash-fragility tại 12 thời điểm mua thú của tape** — không có in-turn sale-credit; nghèo $250-700 ở 3-5 thời điểm là mất vĩnh viễn 1-5 con vật
2. **Feed-coverage d0-2** — 1 COW bỏ trốn mỗi game (route ưu tiên hơn feed)
3. **Opening găm hàng** — giữ 13 WHEAT thay vì tiền lỏng (mất cơ hội hợp tài chính)

## 6. Gợi ý phản công v17 (chưa triển khai trong task này)

- **H13 (sale-credit animal-buys)**: trước khi submit market list, nếu có BUY_ANIMAL/BUY_SEED mà tiền thiếu → **chèn SELL dẫn trước** (bán shed stock theo giá bảo thủ) để cấp vốn trong-lượt — port trực tiếp `_r128_credit_supply` + "sequential funding" của indark E749-E776. Ước tính khôi phục 4-5 con vật/game ≈ +$15-30k
- **H14 (feed-coverage)**: audit mỗi tối — mọi tile có vật phải được feed trong ngày; nếu thiếu worker → hiring ưu tiên / hoãn route
- **H15 (opening liquidation)**: bán sạch starting wheat step 0 (+$34 net + thanh khoản)
- Lưu ý xung đột tiềm năng: H8 front-run (bán sớm) vs H13 (bán để mua) — cần gate "chỉ bán khi thiếu tiền và không phá H1 town-demand"

## 7. Nghịch lý chiến lược

v41 thắng bằng **kỷ luật kinh tế vi mô** (đủ tiền mua đúng hạn + không chết vật) chứ không phải chiến thuật đối kháng — nó gần như không đọc đối thủ. v16 thua vì tape của chính mình bị cash-flow phá vỡ khi đối thủ cạnh tranh cùng tape nhưng quản lý dòng tiền tốt hơn. Bài học: trong meta đồng-tape, **cơ chế thanh khoản > tối ưu bán hàng**.

## 8. Artifacts

- `ahmedv41.py` (331,608 bytes, nguyên văn nguồn + attribution Apache-2.0)
- `bench/t79_v16_vs_ahmedv41.json` (battery 10 games), `bench/t79_battery.log`
- `battles/t79_replay_v16_ahmedv41_s{360,361,364,365}.jsonl`, `battles/t79_replay_kme3v39_ahmedv41_s362.jsonl`
- `bench/t79_{analyze,executed,herd,deaths}.py` (bộ tools autopsy)
- `research/kaggle_dl/raw_ahmedberatozer__kaggress...v41-review-candidate.json` + extracted .ipynb/.py/_md.txt
