# ARI — KẾ HOẠCH NGHIÊN CỨU v14: VƯỢT QUA v13 VÀ MỌI ĐỐI THỦ

**Tác giả:** Ari (kỹ sư AI · kiến trúc sư hệ thống · chuyên gia thuật toán)
**Ngày:** 13 Sep 2026 (sau Task 68 — dọn dẹp registry)
**Trạng thái:** Đề xuất nghiên cứu — chờ user duyệt trước khi triển khai

---

## PHẦN 0 — BỐI CẢNH SAU DỌN DẸP

### 0.1 Registry hiện tại (3 tầng: runner / arena-service / constants.ts)

| Agent | Nguồn gốc | Trạng thái |
|---|---|---|
| **v13** | KME3-TUNED v4 DUAL-OPPONENT (của ta) | 🏆 Nhà vô địch |
| kme3 | guruprasaathas111, notebook v9 | Đối thủ chuẩn |
| kme3v10 | guruprasaathas111, notebook v10 (13 Sep) | Đối thủ mạnh nhất |
| aurax | aurax7, shop-router-reactive v4 | Đối thủ mới |

- **Đã xóa (Task 68):** `v12.py` (bị v13 thay thế) + `dra.py` (bản sao MD5 `55579a72…` của kme3 — giữ lại là thừa).
- Hạ tầng: arena-service :3005 (double-fork daemon) · dev :3000 · gateway :81. Smoke test PASS sau xóa.

### 0.2 Bảng sức mạnh hiện tại (số liệu battery đã đo)

| Cặp đấu | Kết quả | TB gap | Ghi chú per-seed |
|---|---|---|---|
| v13 vs kme3 (100-107 ×2 ghế) | 16/16 | **+$3.870** | |
| v13 vs kme3 (200-207 ×2 ghế) | 16/16 | +$3.203 | không overfit |
| v13 vs kme3v10 (100-103 ×2 ghế) | 8/8 | **+$2.597** | seed 103 hẹp nhất: +$1.039 |
| v13 vs aurax (100-103 ×2 ghế) | 8/8 | **+$2.608** | seed 100: +$2.192 · 101: +$2.320 · 102: +$4.867 · **103: +$1.052** |
| kme3v10 vs kme3 (100-101 ×2 ghế) | 4/4 v10 thắng | +$1.773 | v10 mạnh hơn v9 thật |
| aurax vs kme3v10 (100-103 ×2 ghế) | 8/8 aurax thắng | +$5/trận | ≈ ngang sức tuyệt đối |

### 0.3 Mục tiêu v14 (định nghĩa "đạt")

1. **Đánh bại v13 head-to-head** — đây là mục tiêu khó nhất (tự vượt chính mình).
2. **Giữ độc tuyệt đối** vs kme3, kme3v10, aurax (16/16 mỗi đối thủ, 2 bộ seed).
3. Không phá vỡ hạ tầng tape (bài học v11.5-11.8: tái cấu trúc ồ ạt = chết).

---

## PHẦN 1 — KHÁC BIỆT kme3 vs kme3v10 (diff thật, +295/−25 dòng)

MD5: kme3 = dra = `55579a72d9dc94902c8b282d862ce466` · kme3v10 = `4593a884e0a8f8d69293dfe56f566fc1` (2.626 dòng vs 2.356).

### 1.1 Năm thay đổi kiến trúc

| # | Module | kme3 (v9) | kme3v10 (v10) | Giá trị |
|---|---|---|---|---|
| 1 | **R51 input-path** | GREEDY từng bước: mỗi vòng chọn ô có `gain×price/(arrival−now+1)` cao nhất, đi tới, bỏ khỏi danh sách | **BEAM SEARCH width 8, depth 8**: khám phá mọi tổ hợp ô, hàm điểm `gross − 1.5×giá_FERT×len(path)` (phạt chi phí phân/bước đường), giữ candidate tốt nhất từ depth ≥2 | Tối ưu toàn cục thay vì cục bộ khi giao phân cho worker mới |
| 2 | **R62 spawn (EXP193)** | Điểm xuất phát của path luôn giả định `(4,4)` | **Mô phỏng deterministic HIRE spawn**: tính vị trí farmer+hands SAU native actions, rồi mô phỏng ô spawn của thợ mới (4 ô access quanh shed, chọn ô ít người), path bắt đầu từ spawn thật tại `step+2` | Path khả thi 100% — không còn sai lệch điểm xuất phát |
| 3 | **R68 joint plans** | Mỗi worker greedy path riêng lẻ, duyệt tuần tự `i=0..N` | **Liệt kê 3 mode (None / WHEAT-first / CARROT-first)** — mode giới hạn target của worker 0 theo 1 loại cây — rồi chọn mode có score `(Σvalue−Σcost, Σvalue, −cost, −số plan, −mode)` cao nhất | Tìm kiếm tổ hợp nhỏ trên bài toán phân công đa-worker |
| 4 | **R70+R79 fertilizer** | Qty cố định 10, chỉ mua khi giá ≤$30, budget `10×(price+5)` | **Qty thích ứng** `max(10, 10 + native_need − stock)` (đủ cho lệnh PICKUP hôm sau + tồn kho, guard shed-cap 100) + **R79 worthwhile check**: mua cả khi giá >$30 nếu `bonus_tomato × giá_net ≥ 2×(10×giá_FERT + fib_labor) + $100` — tính bonus = số (tile, ngày) trong 3 ngày tới có tomato chưa bón trong cửa sổ sinh trưởng | Bón phân theo ROI thay vì ngưỡng giá cứng |
| 5 | **R85+R86 economic overlay (EXP216/217)** | *(không có)* | **(a) Feed-skip**: ngày 10-28, bỏ lệnh FEED cho thú KHÔNG đói (`consecutive_unfed==0`) khi `bonus×(giá_SP+5)×1.25 < giá_wheat` VÀ mô phỏng tape ngày mai (R86) xác nhận tile đó ĐƯỢC cho ăn ngày mai → tiết kiệm wheat. **(b) FERT-sale**: ngày 6-28, khi market chỉ có SELL, bán lượng FERT thừa (tồn − đã bán − reserve tape − nhu cầu worker, sàn 14) | Lớp kinh tế học 第一 lần xuất hiện — ghi nhận conceptual credit "Steven Lee Hans, Lord Momo Returns" |

*(v10 còn thêm telemetry đầy đủ cho R70: confirmed/shortfall/requests/errors — quan sát đươc từng cơ chế.)*

### 1.2 Đánh giá Ari

- V10 = **nâng cấp logistics + kinh tế học**, KHÔNG đổi production (giữ nguyên route-tape) → đúng kiểu "tinh chỉnh trong lớp" (timing + chi phí vận hành), chưa phải "đổi lớp" theo định nghĩa L26.
- Thực đo: +$1.773 vs v9 — hợp lý vì R85 tiết kiệm feed-wheat + bán FERT thừa là tiền thuần, R51/R62/R68 giảm rơi vỡ giao hàng.
- **Hệ quả cho ta:** v13 (xây trên nền v9) đang thi đấu thiếu 5 module này. Đó là lợi thế chưa thu hoạch — xem H1.

---

## PHẦN 2 — CHẨN ĐOẠN: TẠI SAO VƯỢT v13 LÀ KHÓ

### 2.1 Bão hòa timing (L26 — đã chứng minh bằng oracle)

- Đối đầu mirror-tape (cùng production): gap = thuần timing; H=6 thắng H=4, mọi transit Manhattan-optimal → **cân bằng tại +$3.5-3.9k**.
- Oracle re-timing ±6 bước: trần +$10.5k nhưng **ảo** (vi phạm arrival-physics); backward-1-bước +$6.5k là giới hạn vật lý thật nhưng đã bị H=6 + prefire + flip bắt gần hết.
- 14 cửa chết (7 vòng 3 + 7 vòng 4) đã đo và đóng: front-run melon, water-skip, pre-position, relocate, d9-prewater, FERT-strike, sheep-swap sabotage, momentum-hold…

### 2.2 Vẫn còn bao nhiêu "đất trống"?

| Nguồn giá trị chưa khai thác | Ước tính | Bằng chứng |
|---|---|---|
| 5 module v10 (logistics + kinh tế) | +$1.3-1.8k | battery kme3v10 vs kme3 +$1.773 |
| Kernel-ops (WATER 53%, HARVEST 50.6%) | +$1-3k | "khi có ops thì quota supply mới trả tiền" — mỗi op WATER/HARVEST bỏ lỡ = sản lượng mất |
| Động cơ vốn (cadence bán nhỏ giữ giá premium) | +$1-2k | kme3 giữ 9 thị trường ở vùng $215-248 cả mùa bằng cadence lot nhỏ; v11.5-11.8 của ta thất bại vì làm ồ ạt, R85 của v10 làm surgical và THÀNH CÔNG |
| Đổi lớp production (tape mới) | +$3-10k (không chắc) | L26: con đường duy nhất vượt +$3.9k; rủi ro cao (v11-era: phá tape = chết) |
| Pre-emption deterministic (biết tape đối thủ) | +$0.1-0.5k | contested steps: 93 FERT + 44 MILK + 35 WHEAT/trận nhưng A-behind ≈ B-behind → dư địa nhỏ |

### 2.3 Quan sát seed 103 (điểm yếu nhất của v13: +$1.05k vs aurax)

Seed 103 là seed "giàu" (đối thủ $113k, cao nhất 4 seed) — khi thị trường hút mạnh, chênh lệch GIÁ nén lại → timing mất giá → **muốn thắng seed giàu cần SẢN LƯỢNG/tuần hoàn vốn nhiều hơn, không phải timing tốt hơn**. Cần autopsy chính thức (đề xuất trong M2).

---

## PHẦN 3 — SÁU HƯỚNG NGHIÊN CỨU (thứ tự ROI : rủi ro)

### H1 — MERGE: v14-M = kme3v10 + 6 tầng tuning v13 ⭐ (ưu tiên đầu tiên)

**Ý tưởng:** Nền v13 là kme3 v9 + tuning. Đối thủ v10 đã tự nâng cấp +$1.77k trên chính nền đó. Merge = lấy kme3v10.py làm base, re-apply đúng 6 tầng tuning của v13:

1. `_V12_HORIZON=6`, `_V12_R36_LO=144`, `_V12_R36_HI=712` (cửa sổ R37 reorder + horizon 6)
2. V224 sales-first từ step 144
3. V231-flip SHEEP→COW điều kiện `milk_shops>=3 and 'YARN_STORE' not in shops`
4. `_v12aa_prefire` h21+h22 (ngày 12-28, lookahead 1 bước, bán overflow)
5. Melon-seller mọi giờ
6. `_V12_PREDUMP_STEP=-1` (tắt — giữ nguyên cấu hình)

**Xung đột tiềm ẩn phải xử lý khi merge (danh sách kiểm tra):**
- **R85 feed-skip vs V231 CARE banking**: CARE cần fed+cared hằng ngày để tích `pending_care_bonus`; R85 bỏ FEED hôm nay (hôm sau mới feed) → mất 1 ngày bonus. Phải để R85-aware: chỉ skip khi tile KHÔNG nằm trong chuỗi CARE đang tích của V231, hoặc tính lại ngưỡng `bonus×(giá+5)×1.25` có tính mất care-bonus.
- **R62 deterministic spawn vs prefire**: prefire mô phỏng tape bước kế — R62 đổi vị trí thợ mới (spawn thật thay vì (4,4)) → mô phỏng prefire phải dựng vị trí theo R62.
- **_r51_input_control hook**: v10 thay nội dung loop bằng `_r68_joint_plans()` và đổi chữ ký `_r51_input_path(obs,targets,action,index)` — tầng v13 wrap theo tên hàm nên an toàn, nhưng phải kiểm tra `_R51_INPUT_MAX_WORKERS` tương thích horizon 6.
- **Thứ tự onion**: v10 stack: …→R51(v10)→R70→R79→R85→R86; v13 stack: …→R51(v9)→R53→V231→V233→v12aa. Thứ tự đề xuất cho v14-M: base v10 → V231-flip → V224/R37-tuning → prefire/melon → (V233 giữ nếu không xung đột R85).

**Cổng đo G1:** v14-M vs v13 head-to-head 32 trận (seeds 100-115 × 2 ghế) ≥ 24/32 và TB gap ≥ +$1.2k.
**Cổng đo G2:** v14-M vs kme3/kme3v10/aurax — 16/16 mỗi đối thủ, gap ≥ +$4.5k / +$3.5k / +$3.5k.
**Ước tính:** +$1.3-1.8k. Rủi ro: THẤP (tất cả thành phần đã tồn tại và thắng ở đâu đó).

### H2 — CAPITAL ENGINE (mở rộng R85 thành lớp kinh tế tổng quát)

**Ý tưởng:** R85 của v10 chứng minh pattern surgical kinh tế hoạt động (feed-skip + FERT-sale). Mở rộng thành 3 valve có kiểm chứng:

1. **FERT-scaling (R17):** mỗi thú sống nhả 1 FERT miễn phí/ngày, không thu là mất. Kiểm tra coverage thu FERT của đàn hiện tại; bán toàn bộ phần thừa theo R85-reserve. Thêm 1 lần audit telemetry `fert_sale_units` của kme3v10 để định cỡ.
2. **MILK/STRAW price-maker:** giá milk d8-13 $120-186 rồi sụp $2-35 (cung 22/ngày > drain 19/ngày từ d15) — valve bán bò-sản-lượng-theo-cadence: d8-13 bán full, d14+ chỉ bán đúng lượng drain để giữ giá, phần còn lại chuyển sang chăn nuôi giảm (bỏ FEED bò từ d16 — đã có R85 feed-skip, tăng ngưỡng bỏ cho bò đã hết cửa sổ прибыль).
3. **Wheat drain-harvest (R37/R40):** town hút 35 wheat/ngày BẤT CHẤP giá → bán đúng 35/ngày vào drain từ d1 với lot nhỏ (giữ inventory gần I0, giá không rơi), phần dư giữ đến khi giá trên $28. **CẢNH BÁO:** v11.5-11.8 thất bại vì làm ồ ạt phá vốn + churn — lần này chỉ valve sau khi G1 đạt, đo từng valve riêng (A/B 1 valve/battery).

**Cổng đo G3:** mỗi valve riêng lẻ: battery 16 trận vs v13, chỉ giữ valve có TB gap ≥ +$300 và worst-seed không âm.

### H3 — CLASS CHANGE: tape production mới (con đường vượt +$3.9k duy nhất theo L26)

**Ý tưởng:** Sinh tape mới offline (chúng ta có toàn bộ generator + engine trắng) với 3 danh mục ứng viên:

| Ứng viên | Cơ sở định lượng | Rủi ro |
|---|---|---|
| **Egg-heavy** (ngỗng lớn + ít bò) | EGG là mặt glut-kháng nhất: above log 0.20 (bán +332 units chỉ rơi $50→$43); $/tile/day 1.00 (cao nhất bảng R13); ngỗng trả vốn d7 | Feed-cost + kernel-ops thu 10/ngày; egg_rush v5-era thất bại do pipeline yếu — nhưng giờ có choreography standing |
| **Straw-early + milk-late** | "Đồng hồ sinh tử dâu": trồng trước d10 quyết định $10-20k; straw T=100 linear-1.6 (crash nhanh) → phải bán cadence từ sớm; milk chỉ quý d8-13 → giảm đàn bò sau d15, chuyển đất sang dâu vòng 2 | Phá tape gốc = phải sinh lại toàn bộ walk |
| **FERT-industrial** | Đàn lớn → R17 FERT miễn phí 1/con/ngày; FERT linear/linear hai chiều ($140 trên/$60 dưới) — bán FERT thừa cả mùa + bón chính xác ROI (R79) | Cần đàn 15+ con = feed-wheat lớn — phụ thuộc H2-valve feed |

**Quy trình:** tape-gen offline → smoke 1 trận → battery 16 trận vs v13 → chỉ giữ danh mục thắng ≥ 10/16.
**Cổng đo G4:** danh mục mới vs v13 ≥ 10/16 VÀ vs cả 3 đối thủ 8/8.
**Lưu ý:** H3 chỉ triển khai sau khi H1 đạt (nền so sánh phải là v14-M).

### H4 — KERNEL-OPS: tái sinh choreography walk-level

**Số liệu:** kme3 đứng đầu 74/72 ô = 101 op/ngày; WATER chỉ phủ 53%, HARVEST 50.6%. Mỗi lượt MOVE là "bọt xốp" — mục tiêu tối ưu hàm mục tiêu của tape-gen từ "tổng quãng đường" sang "số op hữu ích/ngày (WATER+HARVEST+PLACE+PICKUP)".

- Bước 1: đo histogram op-type theo ngày của v13 (có sẵn telemetry + oracle transactions) → xác định đúng ngày/tàu mất ops.
- Bước 2: re-run generator với objective mới cho các ngày có mật độ op thấp nhất (chỉ tái sinh từng đoạn, không cả tape — giữ phần còn lại nguyên vẹn).
- **Ước tính:** +$1-3k (mỗi WATER thêm trong bonus window = +1 unit/tree).
- Rủi ro: TRUNG BÌNH — chỉ đụng walk, không đụng market/planner.

### H5 — PRE-EMPTION DETERMINISTIC (biết trước tape đối thủ)

**Ý tưởng:** Ta có code kme3/kme3v10/aurax → tape của họ là deterministic (route chọn theo `town.unlocked_shops` — public). v14 có thể mô phỏng exact-future-sells của đối thủ và chủ động xếp lệnh bán của mình TRƯỚC 1 bước tại các bước contested (93 FERT + 44 MILK + 35 WHEAT/trận).

- **Cảnh báo честность:** oracle vòng 4 cho thấy A-behind ≈ B-behind (đối xứng) và vùng cuối ngày giá phẳng — dư địa có thể chỉ +$100-500. Phải đo lại với baseline v14-M.
- Đây là "đòn đúng luật" (không đọc private state của đối thủ — chỉ dùng public obs + code công khai).

### H6 — SURVIVAL + MONITORING (bảo hiểm, chi phí ~0)

1. Port **R60 survival** của aurax (cứu thú đói 2 ngày tại h22, chọn carrier sạch min-loss) — v14 không được thua vì chết thú trong các seed lạ.
2. Port **R36 early-window** của aurax (sale-lead d9 thay vì d12) — chỉ bật sau A/B riêng (V231-flip từng dạy ta: cửa sổ sớm không luôn lời).
3. **Vòng giám sát Kaggle định kỳ**: pull + MD5 check notebook 3 nguồn mỗi tuần; khác MD5 → đăng ký đối thủ mới 3 tầng + battery (quy trình Task 66-67 đã chuẩn hóa, luật L24/L27/L28/L30).

---

## PHẦN 4 — LỘ TRÌNH THỬ NGHIỆM (milestone + cổng dừng)

| Mốc | Nội dung | Cổng dừng | Ngưỡng |
|---|---|---|---|
| **M1** | H1 merge v14-M + battery G1/G2 | G1: vs v13 32 trận | ≥24/32, TB ≥ +$1.2k |
| | | G2: vs 3 đối thủ | 16/16 mỗi bên |
| **M2** | Autopsy seed 103 + v14-M2 (fix chọn lọc) | So sánh gap seed 103 | +$1.05k → ≥ +$2k |
| **M3** | H2 pilot từng valve (FERT-scaling trước) | G3: 16 trận/valve | TB ≥ +$300, worst ≥ 0 |
| **M4** | H3 tape-gen (chỉ nếu M1-M3 cộng dồn < +$2.5k) | G4: vs v13 10/16 | + cả 3 đối thủ 8/8 |
| **M5** | H4 kernel-ops + H5 pre-emption (lót đường v15) | battery mở rộng | tùy M4 |

**Quy tắc vàng (kế thừa L1-L30):** một thay đổi = một battery · không chạy battery ngầm khi UI e2e (L29) · slug Kaggle bằng hex/từ nguồn (L27) · fork phải MD5-check (L24) · mọi valve phải A/B cô lập.

---

## PHẦN 5 — KẾT LUẬN ARI

v13 là nhà vô địch timing trong lớp mirror-tape. Vượt nó KHÔNG thể bằng timing nữa (L26 + 14 cửa chết) — mà bằng **xếp lớp ba thứ tiền mới**:

1. **Tiền vận hành** (H1): thu hoạch 5 module v10 — gần như miễn phí, rủi ro thấp nhất.
2. **Tiền kinh tế** (H2): lớp valve surgical theo mẫu R85 — đã được đối thủ chứng minh đáng tiền.
3. **Tiền sản lượng** (H3/H4): đổi lớp production + dày đặc ops — con đường duy nhất bứt phá +$3.9k, cần sinh tape mới có kiểm soát.

Đề xuất khởi động: **duyệt M1 (H1 merge)** — nếu user gật, tôi tiến hành ngay theo đúng cổng đo G1/G2.

*Ari — kỹ sư AI, kiến trúc sư hệ thống, chuyên gia thuật toán.*
