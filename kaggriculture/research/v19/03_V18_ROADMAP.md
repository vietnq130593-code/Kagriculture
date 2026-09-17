# 03 — V18 ROADMAP: XÂY DỰNG TRÊN NỀN JAXA623 K0006

> Task 81 · 2026-09-16 · Tổng hợp từ `01_V18_BASE_ANALYSIS.md` (phân tích code) + `02_META_RESEARCH_2026-09-16.md` (nghiên cứu meta 12 notebook Kaggle).

## 0. HIỆN TRẠNG (đã hoàn thành trong task này)

| Thành phần | Trạng thái |
|---|---|
| **v18.py** = jaxa623 K0006 byte-exact (sha256 `4757f3f5…`) | ✅ đã đăng ký 3 tầng registry (run_battle.py / arena-service / constants.ts), arena chạy thật |
| Sparring lineage: ahmedv43 / ahmedv44 / ahmedv45 (sha256 verified) | ✅ cùng registry |
| Verify E2E qua UI (gateway :81) | ✅ v18 thắng ahmedv43 $97.622 vs $96.411 (seed 777), 0 console error; thắng ahmedv45 +$1.711 (socket seed 202); thắng ahmedv43 +$566 (runner seed 101) |
| Kiến trúc v18 (subagent 8-a) | ✅ wrapper 315 dòng bọc V43 nguyên văn qua byte-string exec; 4 edges định vị đủ số dòng |
| Meta research (subagent 8-b) | ✅ 12 notebook, top-10 ý tưởng xếp hạng impact × tin cậy |

**Bản chất v18**: V43 (làm nông 100%) + wrapper 4 market micro-edges:
`agent(obs)` → chạy V43 → OPEN-50 (step 0, fingerprint-gated) → ADVANCE-2 (premium items trong shed, tape lookahead 2 turn) → FRONT-LOAD (reorder list, mô phỏng per-unit solo + lockstep, fail → giữ nguyên) → return. HORIZON-24 = monkey-patch `_R37_HORIZONS.get()` lúc import (chỉ đón đúng 1 điểm đọc, không đụng phase khác).

## 1. NGUYÊN TẮC BẤT BIẾN (học từ jaxa623 + trap đã bị)

1. **Không phá farm plan** — mọi cải tiến chỉ đụng market list / timing / opening. Farm plan = tài sản được kiểm chứng 128-0.
2. **Safety-first**: mọi reorder/advance phải qua mô phỏng per-unit (solo + lockstep) — một lệnh fail còn tệ hơn không tối ưu (V43 plan giả định mọi lệnh land).
3. **4-tier acceptance** trước khi promote bất kỳ biến thể nào:
   - T1: 24 dev-seed cố định × 2 ghế (chạy mỗi candidate)
   - T2: stress-clone library (xây counter của chính mình: bigger-open, horizon-copy, open+h24)
   - T3: 64 worlds × 2 ghế + bootstrap 95% CI — "edge có CI chạm 0 = không phải edge"
   - T4: official `kaggle_environments` runner audit — **nhất thiết dùng single-file packaged**, không dùng wrapper (trap #1: wrapper → parent-load fail → đối thủ PASS cả mùa → +$167.366 ảo)
4. **Single-file submission** cho Kaggle; giải phóng `sys.modules` giữa các lần load agent (trap #2: OOM tại game 200/256).
5. **Telemetry per-game reset** — counter hiện cộng dồn cross-episode (phát hiện của 8-a, phải sửa trước khi dùng đo lường).

## 2. GÓI CẢI TIẾN ĐỀ XUẤT — "market-defence" (v18.1)

Cả 3 ý tưởng nằm gọn trong `frontload()` / `advance_sales()` (L94-259), không đụng farm plan, tổng ~50 dòng:

### MD1 — Impact-aware ordering (sửa frontload) · kỳ vọng +$300-800
- **Bằng chứng**: Rayk C71 31-9 vs C70 — KHÔNG đưa SELL WHEAT/FERT lên đầu: bán sớm = tự hạ giá chính thứ đối thủ đang mua (input của họ rẻ hơn), đồng thời mình bán trước cú dump của chính tape mình.
- **Việc cần làm**: tách group A của frontload thành `premium-first` (MELON/STRAWBERRY/MILK/WOOL/EGG/CARROT/TOMATO) và `wheat-fert-cuối`; giữ nguyên mô phỏng an toàn.
- **Lưu ý từ 8-a**: frontload hiện đưa MỌI non-wash SELL lên đầu — gồm cả WHEAT/FERT khi không phải wash trade. Đây là điểm lệch chuẩn so với C71.

### MD2 — Fertilizer-only preempt với debt-tracked cap 10 (mở rộng advance) · kỳ vọng đảo match
- **Bằng chứng**: Rayk C94 held-out **174-6 (96.7%)**, rank-1 BT 1837 trên 18 agent — cơ chế đảo kết quả trận 5.300-5.700 coins.
- **Việc cần làm**: advance_sales đang **loại trừ tường minh FERTILIZER** — thêm branch riêng cho FERT (khác logic premium: preempt theo window bón phân, cap 10 lệnh/turn, trừ đúng lượng đã bán sớm khỏi lệnh tape sau — xem MD3).

### MD3 — Strict debt invariant (bổ sung cho advance) · chống oversell
- **Bằng chứng**: boatlee V16-RC5 60/60, C45/C94 đều giữ sổ nợ: bán sớm X unit → lệnh tape sau giảm đúng X. jaxa623 dùng SELL-as-cap → nếu shed dư có thể bán THÊM tổng lượng (thay vì chỉ dịch thời gian).
- **Việc cần làm**: thêm per-item debt state trong wrapper; advance chỉ được "di chuyển" doanh thu, không "tạo thêm" doanh thu.

### MD4 — Feed-buy index-0 (early game) · kỳ vọng lớn nhất, rủi ro thấp
- **Bằng chứng**: Rayk §15.1 — 4 live-loss TB **−$13.606/game** do bị squeeze wheat khi mua feed; hoist BUY wheat-feed lên slot 0 "fixed every sampled feed-denial route" (**173-7**).
- **Việc cần làm**: khi day ≤ 6 và tape có BUY WHEAT cho feed → đẩy lên index 0 của market list (đi kèm mô phỏng lockstep như frontload).

## 3. HÀNG ĐỢI SAU (v18.2+) — cần đo trước / fork có kiểm soát

| # | Ý tưởng | Bằng chứng | Ghi chú triển khai |
|---|---|---|---|
| 5 | OPEN_UNITS re-sweep + Two-Coins stress clone | pipe-7: Q=5 đạt **50W-0L vs Q=70** (179-1 tournament, ~$250/game) | jaxa623 chọn 50 từ plateau 25-50; pipe-7 cho thấy 5 còn mạnh hơn — cần battery riêng + thêm clone Two-Coins-opening vào bench |
| 6 | Tắt `_R37_QUOTE` khi frontload chạy | 8-a H1: parent sort SELL theo quote-priority, wrapper sort lại — 2 lớp sort có thể phá nhau | kiểm chứng bằng telemetry before/after |
| 7 | Bật `_R148_SEEDS=True` (slot có sẵn trong parent, cờ đang False) | 8-a H2 | đơn giản nhất — nhưng phải đo trên 64 worlds |
| 8 | Town-demand gate cho advance | boatlee 60/60 | cần verify chiều gate trên engine 1.32.7 (kaggle ≠ bản boatlee mô phỏng) |
| 9 | Online opponent-horizon inference (C68) | **342-18** | thay LOOKAHEAD cố định 2 bằng fit H1-6 từ market-inventory delta net town-drain; đắt nhất |
| 10 | C72 one-step premium banking (≥$2.000, ≤1 bước tới shed) | 109-11, +168.5 cash day-15 | **chạm farmer/hands → là field fork**, làm sau khi cạn market-layer |
| 11 | Per-world route-cell audit (YARN/PET_CAFE) | Kaito v43: YARN thu hồi 10/12 loss; PET_CAFE 16/26 | thuần đo lường bằng arena 64 worlds — không fork nếu chưa thấy lỗ hổng |
| 12 | Endgame stranding audit | destbreso: benchmark #1 $442 stranded/13 fallow tiles | đo shed+inventory kẹt tại step 719 của v18; >$500 → sell-off 3-5 turn cuối (market-only) |

## 4. ÂM TÍNH ĐÃ BIẾT — KHÔNG LÀM LẠI (từ 02_META §6)

SE/quadrant-4 (C93 0-40) · season-long funding attack (0-16, chỉ có tác dụng ngày-0) · horizon 36/48 (thua mirror) · pipe-4 C9 conditional opening (+$1/game = noise, jaxa623 đã tự test) · Hamburger front-run 1-turn · V44 clone-gated escalation (fixed-24 đã thắng V45 chứa nó 128-0) · EGG market maker / BAKERY (0 diff) · Kaito shop-pair routing (V43 có sẵn yhay81-0913) · + ~18 âm tính khác trong báo cáo.

## 5. QUY TRÌNH BENCHMARK CHUẨN (dùng lại hạ tầng arena)

1. Battery 24 seeds × 2 ghế vs {ahmedv43, ahmedv45} qua `run_battle.py` (6-8s/trận → ~13 phút/battery).
2. Stress-clone: tự xây counter (bigger-open / horizon-24 copy / open+h24-no-micro).
3. 64 worlds: label seed theo cặp shop đầu (truncate V43 mirror tại step 145), 1 seed chưa-tune/world, 2 ghế, bootstrap paired margins.
4. Official-runner audit với **single-file packaged** (không wrapper — trap #1).
5. Gate promote: CI-95% dương, worst-world dương, 0 lỗi runner, 0 slow-turn.

## 6. BẢN ĐỒ FILE

```
kagriculture/
  v18.py            ← nền (byte-exact K0006, KHÔNG sửa trực tiếp)
  ahmedv43.py       ← sparring (nền so sánh micro-edges)
  ahmedv44.py, ahmedv45.py ← sparring lineage
  RULES.md          ← 130 quy tắc engine (giữ lại — engine 1.32.7 bất biến)
  arena/run_battle.py ← registry + JSONL stream
kaggle-research/
  01_V18_BASE_ANALYSIS.md      ← kiến trúc v18 + tunables + hooks (8-a)
  02_META_RESEARCH_2026-09-16.md ← meta + top-10 ý tưởng (8-b)
  03_V18_ROADMAP.md            ← tài liệu này
  jaxa623_markdown.md          ← nguyên văn mô tả 4 edges của tác giả
  agents/                      ← K0006 + V43/V44/V45 (sha256 verified)
  extracted/                   ← 12 notebook markdown + code
  raw/                         ← JSON gốc từ Kaggle API + danh sách kernels
  screenshots/                 ← bằng chứng UI E2E
```
