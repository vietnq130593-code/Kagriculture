# 08 — COMPETITOR INTEL: aurax7 "Shop Router Reactive v7"

> Task 88 · 2026-09-17 · Nguồn: user cung cấp link notebook
> `kaggle.com/code/aurax7/kaggressurE-shop-router-reactive-v7` (slug thật:
> `aurax7/kaggressurE-shop-router-reactive-v7`)

## 1. Nguồn & xác thực

| Mục | Giá trị |
|---|---|
| Notebook | `aurax7/kaggressurE-shop-router-reactive-v7` (title "KaggressurE_shop_router_reactive_v7", last run 17-09 04:33) |
| Team | **"Farmers Is All You Need"** — rank **299/9318**, score **2723.3** (LB 17-09 15:28) |
| Thành viên | aurax7 (Yaxon), coolinlai, davidsarrat, pseree, zongzishuang (5 người) |
| Lịch sử kernel | reactive_router (08-09, 70 votes) → v2 (09-09) → v4 (09-13) → v5 (09-14, 93 votes) → v6 (09-16) → **v7 (17-09)** |
| Extract | `kaggle-research/competitors/nb_aurax7/main.py` — 347,602 chars, **SHA-256 `e221f487…`**, import + `agent` callable verify OK |
| Sparring agent | `kaggressul.../aurax7.py` (byte-exact copy, đăng ký run_battle + arena-service UI — 13 agents) |

## 2. Kiến trúc v7

Header tự khai báo: *"V7: Reactive Market-Master (Horizon 24 + 2-Turn Advance Sales +
Front-Loading + Low-Spread Attack). Architecture: V45 Full Chassis + V44 Same-Turn
Race Escalator + _r60 Survival Guard + 2842 Advance/Frontload Overlay."*

So inventory hàm với `ahmedv45.py` local: **85/85 defs của V45 giữ nguyên, KHÔNG bỏ gì,
thêm 13 defs mới**:

1. **`_r60` survival guard** (8 hàm, ~120 dòng)
2. **Overlay 2842** (5 hàm: `frontload`, `advance_sales`, `_simulate`, `_price`,
   `_future_market`, `_standard`) — comment ghi "Van / Claude, 2026-09-15" (AI-assisted
   wrapper) + header ghi "sdy623 / jaxa623"

### 2.1 `_r60` survival guard (2 cơ chế)

- **Opening liquidity** (day 0, h<18): cap `BUY_SEED WHEAT` để luôn giữ `$4` tiền mặt
  = đúng 3 lượt hire ngày-1 (hire $1 × 3 hands). Không cho cha mẹ đốt hết tiền vào seed.
- **Animal rescue h≥22**: quét tile động vật `fed_today=False && consecutive_unfed≥1`
  (sắp trốn thoát tối nay) → tính loss = giá thú + số lượt sản phẩm còn lại; chọn carrier
  rảnh gần nhất còn WHEAT (ưu tiên PASS/idle, phạt nặng khi mang theo thú) → đè lệnh đi
  FEED. Đây là lớp **bảo vệ tài sản hữu hình** mà ta CHƯA có.

### 2.2 Overlay 2842 (4 cơ chế, chạy SAU cùng)

1. **Step-0 opening wash**: nếu opening của parent == `_V43_OPENING`
   ([BUY 5, BUY 10, SELL 60]) → thay bằng `[BUY_PRODUCT WHEAT 10, SELL WHEAT 10]`
   đặt index-0 — lockstep quoting thấy BUY trước (mục đích tương tự v46 opening của ta
   nhưng flavor wash-roundtrip, nhẹ hơn: BUY 7/SELL 2 + strip + BUY 30 attack của ta).
2. **`advance_sales` (LOOKAHEAD=2)**: pre-sell PREMIUM items 1-2 turn từ tape route
   của parent, chỉ khi hàng đã trong shed; `PROTECT_FIRST` bảo vệ SELL đầu tape
   (credit overlay của parent ăn vào đó); bỏ qua dawn turn (step%24==23) và ≥718.
   → **Ta có LOOK=3 từ v19.3 (v46 port) — tức cơ chế này ta đã mạnh hơn 1 bậc.**
3. **`frontload`**: reorder market list thành A (SELL thật) + B (BUY + wash SELL) + C
   (rest), chỉ áp dụng khi **solo simulation** (engine model riêng `_MARKET_PARAMS`
   + `opp_pressure 0/1`) xác nhận list mới vẫn execute đủ — an toàn hơn permute 2-6
   của seyit-L2 nhưng cùng họ lockstep-reorder. Ta có bản clone-gated + replay
   engine-exact từ v19.4 (chính xác hơn mô hình xấp xỉ của họ).
4. **`_Horizons` hack (HORIZON 24)**: subclass dict đè `.get()` — parent (V45/r37)
   reserve tape sales 4 turn trong cửa sổ 288..696 → wrapper đọc ra **24 turn**.
   Hiệu ứng: parent bán trước xa hơn → gặt giá trước khi đối thủ dìm giá.
   **Ta CHƯA có tương đương** — ứng viên port cho v20.1.

## 3. Định vị so với ta (batteries Task 88, official runner, 48 trận)

| Matchup | W-L | Mean margin/trận | Paired/seed | Worst | CI 95% |
|---|---|---|---|---|---|
| **v20 vs aurax7** | **48-0** | **+$1,711** | +$3,422 | +$679 | [1546, 1876] |
| **v194 vs aurax7** | **48-0** | **+$1,740** | +$3,481 | +$706 | [1570, 1916] |

So sánh biên với các đối thủ meta đã đo (cùng runner 48 trận):

| Đối thủ (rank LB) | v19 cũ | **v20** |
|---|---|---|
| ahmedv46 (~top 30) | −$396 (2W/46L) | **+$1,570 (48-0)** |
| seyit4 (~188, 2801) | +$1,225 | **+$2,176 (48-0)** |
| **aurax7 (299, 2723)** | — | **+$1,711 (48-0)** |
| ahmedv43 (~331) | +$1,298 | **+$2,122 (48-0)** |

**Kết luận định vị:** v20 khắc chế toàn bộ meta đã biết local — kể cả team rank-299
đang nằm an toàn trong vùng bạc. Nếu matchmaking Kaggle phản chiếu kết quả head-to-head
này, rating thật của v20 ≈ vùng 2700+.

## 4. Ứng viên port cho v20.1 (xếp theo kỳ vọng giá trị)

1. **`_r60` animal rescue h22** — bảo vệ $300-500/thú + sản phẩm tương lai; ta chưa có
   gì tương đương; rủi ro thấp (guard hẹp, chỉ đè lệnh khi có thú sắp thoát).
2. **HORIZON 24 (`_Horizons` dict-hack)** — mở rộng reservation window của v19.3
   advance-widen; cần đo vì có thể xung đột với LOOK=3 + preguard của ta.
3. **`frontload` sim-guard flavor** — ta đã có lockstep clone-gated chính xác hơn;
   chỉ đáng xem nếu telemetry cho thấy reorder của ta hay decline.

## 5. Ghi chú cuộc thi (kèm trong Task 88)

- **Bug nghiêm trọng được phát hiện & fix**: submission v20 đầu tiên (56308181, 15:26)
  score **600→281** vì `kaggle_environments.agent.get_last_callable()` (agent.py L64)
  chọn **callable CHÈN CUỐI** trong namespace — re-define `agent` không đổi vị trí key
  trong dict Python, nên helper `_v194_reorder` (def sau cùng trong flat build) đã
  HIJACK lời gọi harness: mọi turn trả về config object → engine coi là PASS →
  720 lượt đứng yên, kết thúc $3000. Local không gặp vì run_battle.py load qua
  `getattr(mod, "agent")`.
- **Fix**: `build_v20.py` thêm block `del agent` + re-def cuối file (thủ thuật của
  dòng jaxa/aurax: `agent = globals().pop('agent')`) → key `agent` được chèn lại ở
  vị trí cuối. Build tự verify `get_last_callable(src) -> agent`.
- Differential battles sau fix: **rewards khớp từng đồng** (seed 5 vs aurax7: +$2,609;
  seed 11 vs ahmedv46: +$711) — fix trong suốt về behavior.
- **Submission v20.1 (56308666, 15:47)**: validation episode 110099769 chạy THẬT
  (rewards [67544, 68171], opening BUY 7/SELL 2, 719/720 turn hành động) —
  điểm hiển thị 600 = rating khởi tạo, sẽ leo dần theo matchmaking episodes.
