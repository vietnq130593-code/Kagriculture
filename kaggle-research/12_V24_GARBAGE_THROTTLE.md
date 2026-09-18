# 12 — v24 GARBAGE-THROTTLE: H2 peak-pricing trên output hiện có
## 6 seed probe × 9 biến thể knob × 2 battery 48 trận + replay-telemetry

> Task 92 · 2026-09-18 · Bio
> Chuẩn đối: v20 (flat 410KB, submission #56308666) vs ahmedv46, engine
> kaggle-environments 1.32.7, 720 turn. Batteries: seeds 100-123 × 2 ghế
> (bench/battery.py, official runner) + 6 crash-seed sweep (3/5/8/11/17/21).

---

## 0. TÓM TẮT

| Đối chứng | Kết quả | Ý nghĩa |
|---|---|---|
| v24 vs ahmedv46, 48 trận (100-123) | **48W-0L, +$1,699** (worst gap +$438) | GATE PASS — ngang v20 (+$1,647), không seed nào nguy hiểm |
| v24 vs v20 direct, 48 trận | **43W-5L, +$113, t=2.68, CI95 [$30, $196]** | **Challenger đầu tiên có CI>0** trong lịch sử project |
| Sweep 5 biến thể × 12 trận (crash seeds) | +$110…+$169, đều 11/12 wins | Knob không nhạy — thiết kế an toàn trong vùng |
| Replay-telemetry (seed 5 + 11) | 0 errors, 95 strips, held→0 | Layer cơ học sạch, không kẹt kho |

**Phán quyết: H2 peak-pricing KHẢ THI và DƯƠNG — nhưng biên nhỏ (+$113/game,
+0.12%).** Đây không phải cú nhảy $40-80K như H1 mơ tưởng; đó là $100-200/game
thuần học được từ "đừng bán vào cửa sổ rác". Là challenger đầu tiên vượt qua
được 3 cổng cùng lúc (48-0 vs v46 / CI>0 vs v20 / telemetry sạch), v24 là
**ứng viên submission hợp lệ** khi token Kaggle trở lại (token cũ mất theo
sandbox reboot, đã leak + rotate — cần token mới từ user).

```
v24.py = v20 flat chain (byte-exact — "cash engine" không đụng tới)
       + v24_layer GARBAGE-THROTTLE (~190 dòng, thuần re-time SELL):
           • strip SELL khi giá < $15            (cửa sổ rác thật)
           • giữ tối đa 24 đơn vị / interlock 55 (an toàn shed)
           • release ≤12 u/ngày/item khi giá ≥ $18, chunk co giãn theo giá
           • h0-h20 only; d≥27 REAPER owns; fail-open 3 lỗi/ngày
```

## 1. H2 LÀ GÌ — và 3 probe đã đục chết các phiên bản ngây thơ

H2 = peak-pricing: **không thêm input nào** (không tile, không labor, không
feed — những thứ đã đúc kết opportunity-cost = 0 trong doc 11), chỉ đổi
*thời điểm* bán output mà v20 đã sản xuất hằng ngày.

Ba probe (seeds 3/5/8/11/17/21, full 720 turn, forensic từng đơn):

| Probe | Phát hiện | Số |
|---|---|---|
| h2_timing_probe | **Intraday DEAD**: hour-of-day swing chỉ 5-20 u, dp/dinv $0.02-0.08/u | ~cents/game |
| h2_hoard_forensic | **Không có kho để bán đỉnh**: shed gần rỗng, endgame volume = daily flow; ước tính "+16.8K front-run" là ảo | $0 |
| h2_endgame_probe | **Cửa sổ rác THẬT và có tiền**: cả hai ghế xả daily flow vào giá $1-9 khi drain chưa kịp bắt kịp; STRA crash d21-24 rồi hồi $38-113 (seeds 3/11/17), MILK $4-15 (seeds 8/11/21, hồi $29-41). Giá trị bị phá mỗi crash seed $1-11K, ~nửa lấy được | $500-5K/crash seed |

Walk-down STEEP cho STRA (42u xả = $50 → $1) → release phải chia chunk.

## 2. THIẾT KẾ — 8 bài học từ H1/v21/v22/v23 áp trực tiếp

| Bài học (nguồn) | Áp dụng trong v24_layer |
|---|---|
| L-day (v22: counter đếm mỗi turn → flap) | release/stall đếm **mỗi NGÀY**, không phải mỗi turn |
| L-evid (v22b: speculative banking $50-100 lật seed) | gate $15 = **chỉ rác thật**, không đoán đỉnh |
| L-flap (v22c: re-entry chết) | hysteresis strip<15 / release≥18 — vòng buy-$8-sell-$18 an toàn |
| L-shed (v21: đếm tổng shed mù wheat-buffer) | interlock sum(shed)>55 + cap 24 — không bao giờ chặn BUY feed/animal |
| L-walk (engine: walk-down STRA) | release ≤12 u/ngày/item, chunk co theo giá `max(4, min(12, p//4))` |
| L-reaper (v19: endgame owned) | d≥27 full pass-through — REAPER tự liquidation |
| L-guard (v19.2: h21/22 preguard) | h≥21 pass — core tự xả overflow tồn kho của ta |
| L-fail + L-tel (Task 90: NameError fail-open kín 719 turn) | 3 lỗi/ngày → off; **replay-telemetry test bắt buộc** |

Thêm clamp chống "phantom units": core over-ask (đơn > shed thật) → held
clamp về số vật lý mỗi turn — không bao giờ release nhiều hơn có.

## 3. SWEEP 9 BIẾN THỂ (b→i) — kết luận tái tạo lại 2026-09-18

Sweep gốc (mất theo context) kết luận: gate 15 > 12 ("20 eats recovering
milk"), release 18 > 25. Tái tạo bằng 5 battery 12 trận trên 6 crash seeds
(so v20, both seats):

| Biến thể | gate/release | Crash-seed gap (12 games) | Full battery 100-123 |
|---|---|---|---|
| v24c | 10 / 18 | +$117 (11/12) | — |
| v24h | 12 / 25 | +$110 (11/12) | — |
| v24e | 15 / 25 | +$127 (11/12) | — |
| v24f | 20 / 25 | +$169 (11/12) | **+$111 (41/48)** ≈ v24 |
| **v24 final** | **15 / 18 + price-chunk** | **+$139 (11/12)** | **+$113 (43/48)** |

Đọc kết quả: **knob không nhạy trong vùng [10-20]/[18-25]** — mọi cấu hình
an toàn đều bắt được ~$110-170 trên crash seeds. Gate 20 thắng hơn trên
crash seeds nhưng bằng v24 trên full battery (hiệu ứng "ăn milk đang hồi"
bù trừ). Chọn 15/18 + price-scaled chunk: giữa dải, chunk nhỏ khi giá thấp
(chống tự walk-down khi release). **Không rebuild.**

## 4. BATTERY CHÍNH + TELEMETRY

**v24 vs ahmedv46** (bench/t92_v24_vs_v46.json): 48W-0L, avg $96,218 vs
$94,518, **gap +$1,699** (v20 baseline cùng dải: +$1,647). Worst gap +$438
(seed 110) — không seed nào tiến gần ván thua.

**v24 vs v20 direct** (bench/t92_v24_vs_v20.json): 43W-5L, mean **+$113**,
sd $207, **t=2.68 → CI95 [$30, $196] loại trừ 0**. Worst ratio 0.9981
(seed 103, −$218 = −0.19%) — 5 thua đều nhỏ, không có "game flip" kiểu
v22b. Per-seed: giúp 22/24 seed, trong đó mạnh nhất seed 111 (+$871),
105 (+$310), 100 (+$435).

**Replay-telemetry** (research/v24_replay_test.py, seed 5 + 11):
- 0 errors cả 2 seed; 368/412 turn pass-through.
- Seed 5: 39 strips (MILK 97u + WOOL 31u), gap **+$1,794** vs v20 cùng
  seed +$1,556 → v24 **+$238 tốt hơn**.
- Seed 11 (STRA crash): 56 strips (WOOL 58 + MILK 84 + STRA 18u), 1 release
  event (STRA 4u vào giá hồi), gap +$715.
- **held→0 cuối game** — không tồn kho kẹt: mọi đơn vị bị strip đều được
  release lại, hoặc bán bởi chính core tại h21-22 preguard / REAPER d27+.
- Interlock không lần nào bắn.

## 5. ĐẶT TRONG BỐI CẢNH — tại sao +$113 lại là kết quả tốt

| Challenger | Direct vs v20 | Verdict cũ |
|---|---|---|
| v21-v5 (Task 89) | +$11 (noise) | giữ v20 |
| v22b (Task 90) | +$217 CI>0 NHƯNG 2 game-flips | giữ v20 |
| v22d (Task 90) | +$31 (48-0, worst +$603) | giữ v20 |
| v23 (Task 91) | −$20,205 (0-48) | giữ v20 |
| **v24 (Task 92)** | **+$113, t=2.68, CI[$30,$196], worst −0.19%** | **ứng viên submit** |

Ba dấu hiệu phân biệt v24 với v22b: (1) t-stat 2.68 với worst-case chỉ
−0.2% (v22b flip là thua thật); (2) cơ chế zero-input — không có đường nào
để đối thủ "free-ride" như milk-banker; (3) telemetry chứng minh từng đơn
vị được tracking (held→0).

## 6. QUYẾT ĐỊNH & HƯỚNG TIẾP

- **Submission Kaggle: chờ token.** v24 vượt đủ 3 cổng submission-local
  (48-0 gate, CI>0 direct, telemetry sạch) — nhưng token Kaggle đã mất theo
  sandbox reboot 17:56 (token cũ từng leak public + rotate). #56308666
  (v20.1) tiếp tục climb trên server Kaggle — không ảnh hưởng. Khi user cấp
  token mới: submit v24.py (đã có entry-point verify theo pattern Task 88).
- **Kỳ vọng field**: +$113 mean áp lên 100+ episode matchmaking = +$10-20K
  tổng margin tích lũy — di chuyển rank thật nhưng không đổi tier. Meta-level
  (field ≠ mirror) vẫn là câu chuyện lớn.
- **Đóng sổ H2**: biên còn lại của H2 thuần timing đã vắt kiệt (intraday
  dead, hoard = 0, garbage window ≈ nửa lấy được, knob flat trong dải an
  toàn). Không còn $ đáng kể trong "bán khôn hơn" trên output hiện có.
- **Hướng còn mở**: (1) matchmaking data của #56308666 sau 100+ trận — đo
  field thật; (2) meta-level: cấu trúc đối thủ top-tier không phản ứng kiểu
  constant-seller; (3) H3 arbitrage vẫn postponed (BUY_PRODUCT chỉ
  WHEAT/FERTILIZER — cổng engine đóng).

## Phụ lục — Artifact

- `kaggriculture/v24.py` (419KB flat, entry-verified) + `v24_layer.py` (190 dòng)
- `kaggriculture/build_v24.py` — build + tự verify get_last_callable
- `kaggriculture/v24b…v24i.py` — 8 biến thể sweep (b: cap40, c: rel18,
  d: cap40+rel18, e: gate15, f: gate20, g: plain-chunk, h: gate12, i: final-twin)
- `bench/t92_v24_vs_v46.json`, `bench/t92_v24_vs_v20.json` — battery chính
- `bench/t92_sweep_v24{e,h,f,c,final}.json`, `bench/t92_sweep_v24f_full.json` — sweep
- `research/h2_{timing,endgame}_probe{.py,.json}`, `h2_hoard_forensic.py`, `v24_replay_test.py`
