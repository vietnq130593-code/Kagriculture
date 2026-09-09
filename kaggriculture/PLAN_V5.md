# PLAN_V5 — KẾ HOẠCH TRIỂN KHAI v5 "ORCHESTRATOR" (đánh bại v4 hoàn toàn)

**Tác giả:** KAIN (kỹ sư AI · kiến trúc sư hệ thống · chuyên gia thuật toán)
**Mục tiêu tuyệt đối:** v5 đánh bại v4 một cách hoàn toàn — theo chuẩn dominance 6 điều kiện (mục 1.2), không phải "thua đôi vòng"
**Nền tảng:** LESSONS_V4.md (27 bài học) · RESEARCH_v4.md v2.0 · p0_results.json (ledger $0 residual) · mã nguồn đầy đủ v2/v3/v4 (lợi thế white-box)
**Phiên bản:** 2.1 — đã review + bổ sung theo mandate kép của user: *kiếm tiền xuất sắc* + *hệ phản thân linh hoạt* (tự đánh giá hiện trạng · tự nhận diện kết quả tồi để tránh · tự đổi kế hoạch theo chiến lược đối thủ quan sát được qua Bayes)
**Trạng thái tài liệu:** hợp đồng triển khai **ĐÃ KÍ CHỐT** — 4 quyết định mở mục 10 đã được user chốt (D1–D6 · minimax · thư viện 3 bot đủ · não trước). Hạ tầng mới: **ARENA OBSERVER UI** (mục 11) để xem trận v4↔v5 từng turn 720 lượt trong quá trình phát triển.

---

## 0. TÓM TẮT ĐIỀU HÀNH

v4 hiện là một **orchestrator có nền kinh tế mạnh nhưng não tri giác bán phần**: mắt tinh (telemetry 100% chính xác), tay vững (nền kinh tế v3 + 8 edges), nhưng **vùng não "dự đoán tương lai và đổi chiến thuật" chưa được nối**. Cụ thể: Bayes của v4 chỉ là *bộ phân loại 2 lớp* (twin hay không) — nó **không dự đoán** đối thủ ngày mai bán gì, không dự báo đường giá, không mô phỏng kết quả của quyết định trước khi ra quyết định.

Kế hoạch v5 (phiên bản 2.0, review theo mandate kép của user) xây đúng kiến trúc đó — **1 điều phối trung tâm (orchestrator) điều động nhân công con (executor)** — với **não 6 lớp**: 4 lớp Bayes hướng đối thủ (phân loại → dự báo flow → dự báo giá → mô phỏng kết quả) + **2 lớp phản thân** (L5 tự đánh giá hiện trạng, L6 vệ binh rủi ro với thư viện 10 failure-mode và playbook thoát hiểm), tất cả hội tụ về **bộ meta-controller 6 trạng thái chiến lược** có khả năng đổi kế hoạch giữa trận (dwell 2 đêm chống flip-flop, mọi trạng thái khẩn cấp bắt buộc có lối thoát). Mỗi lớp có công thức tường minh, chi phí đo được, đầu ra bắt buộc được consume bởi quyết định, và cổng nghiệm thu bằng benchmark. Lộ trình P0–P6 (não trước theo mandate), mỗi pha một gate two-sided 24 seed; ước tính giá trị còn lại: **+$15–30k/mùa** so với v4, hướng tới vượt ngưỡng knife-edge ~1.25×.

---

## 1. MỤC TIÊU & TIÊU CHUẨN "ĐÁNH BẠI v4 HOÀN TOÀN"

### 1.1 Định nghĩa mục tiêu

Đối thủ trực tiếp cần đánh bại: `submission_v4.py` (order-invariant, 1.117× vs v3, mirror-safe). Đồng thời giữ mọi chuẩn an toàn đã có (meta coverage, validation self-play).

### 1.2 Chuẩn dominance 6 điều kiện (kế thừa LESSONS_V4 §1.4, nâng ngưỡng + thêm điều kiện phản thân)

| # | Điều kiện | Ngưỡng nghiệm thu | v4 hiện tại |
|---|---|---|---|
| D1 | Tỷ lệ thu nhập hai phía vs v4 (24 seed) | **≥ 1.25×** | — (v4 là đối tượng) |
| D2 | Tỷ lệ thắng hai phía vs v4 | **≥ 90%** | — |
| D3 | Không gãy: trận tệ nhất | **≥ 0.95×** | v4 có 0.80× vs v3 |
| D4 | Mirror / Validation self-play | 10 trận ≥ $30k/bên, không tự hủy T8 | đạt |
| D5 | Phủ meta: melon/random/starter 100%; v2 ≥ 1.34×; crop-baseline ≥ 1.58× | giữ hoặc tốt hơn v4 | đạt |
| D6 | Phản thân: mọi failure mode phát hiện kịp thời, playbook phản hồi kích hoạt, có lối thoát | phát hiện ≤ 24h · hồi phục ≤ 3 ngày | v4: survival không lối thoát (kẹp $4–8k) |

Cột mốc trung gian: P0 ≥ 1.05× · P1 ≥ 1.08× · P2 ≥ 1.10× · P3 ≥ 1.15× · P4 ≥ 1.18× · P5 ≥ 1.20× · P6 ≥ 1.25× (mỗi pha một bậc, không nhảy cóc).

### 1.3 Vì sao 1.25× là "hoàn toàn" chứ không phải 100%/2×

Bài học LE-2 và knife-edge (LESSONS_V4 §1.3): với hai orchestrator cùng mức lao động trên một thị trường dùng chung, biên thắng phụ thuộc phương sai seed ±$3–8k và hiệu ứng thứ tự. Vượt 1.25× trung bình hai phía = toàn bộ phân phối kết quả dịch khỏi vùng hòa/thua — thực chất là "không thua nổi" về xác suất. Đuổi 100% từng trận một trên knife-edge là đuổi con số không tồn tại vật lý.

---

## 2. GÓC NHÌN KIẾN TRÚC — "1 AGENT ĐIỀU PHỐI + NHÂN CÔNG LÀ AGENTS CON"

Nhận định của user là **đúng và là lens thiết kế chính thức của v5**. Đối chiếu với engine:

- **Orchestrator** = hàm `agent(obs)` chạy mỗi giờ: toàn bộ trí tuệ (quan sát, dự đoán, kế hoạch, phân công) tập trung ở đây.
- **Executors** = thợ thuê: engine cho mỗi thợ đúng 1 hành động/giờ (MOVE/hành vi tại ô), **không có trí tuệ, không có bộ nhớ riêng** — mọi "ý định" của thợ là task do orchestrator gán. Năng lực của hệ = số thợ × chất lượng phân công.
- **Đối thủ** = 1 orchestrator khác điều động đội thợ của nó; ta không thấy shed của nó, còn lại public (kể cả tiền mặt và số hire — T3).
- **Môi trường ghép** = thị trường lockstep dùng chung là kênh tương tác gián tiếp duy nhất có ý nghĩa kinh tế ( presence, drain, giá).

Ba hệ quả thiết kế rút ra:

1. **Mọi "AI" phải nằm ở orchestrator.** Không thể "trang bị não cho thợ" — engine không cho phép. Chiến lược sub-agent của user = phân công thông minh: **đấu giá/Hungarian task market** (P4) chính là hiện thực hóa "điều động nhân công con" tối ưu.
2. **Thông tin đối thủ đầy hơn tưởng tượng:** trừ shed riêng tư, mọi thứ public → lớp tri giác (perception) có thể đạt "gần hoàn hảo"; điểm nghẽn thật của v4 nằm ở *suy diễn* (inference) chứ không phải *quan sát*.
3. **Đối đầu tuần tự trên thang Kaggle** (user nhấn mạnh): mỗi trận gặp 1 archetype khác → cần **bộ nhận diện + bảng chiến thuật theo archetype**, không phải một chiến thuật cố định tinh chỉnh cho clone của chính mình. Đây chính là lý do não 6 lớp là trụ cột v5.
4. **Hệ không có ai soi:** orchestrator vừa chơi vừa điều phối — không ai ngoài nó nhìn vào chính nó → muốn "tự đánh giá hiện trạng" phải dựng **gương soi nội tại (L5)**: sổ KPI + chuẩn đối chiếu + điểm sức khỏe; muốn "tránh kết quả tồi" phải dựng **vệ binh nội tại (L6)**: thư viện failure mode với tín hiệu + playbook + lối thoát. Đây là hai lớp mà mandate mới của user yêu cầu và v4 hoàn toàn chưa có.

---

## 3. KIỂM KẾ OODA + PHẢN THÂN CỦA v4 — TRẢ LỜI TRỰC TIẾP CÂU HỎI CỦA USER

*"Agent đã có cơ chế quan sát, xác định trạng thái hiện tại và đối thủ, dùng thuật toán Bayes tính toán trước tương lai kết quả để tùy biến chiến thuật chưa?"*

| Tầng OODA | Trạng thái trong v4 | Bằng chứng mã nguồn | Đánh giá |
|---|---|---|---|
| **Quan sát (Observe)** | telemetry thị trường từng giờ: `opp_sales = Δinv + drain − my_sales`, chuẩn 100% (5.854/5.854 cell); đọc tiền mặt/đàn/đất đối thủ; giá + shop public | `_tm_step`, `_tm_orders` (v4.py L81–116) | ✅ **ĐẠT** — mắt tốt nhất có thể có |
| **Định vị trạng thái (Orient)** | mô hình thế giới đầy đủ mỗi giờ: tile cây/tuổi/urgency, kho, đàn, tiền, drain tương lai xác định | `_forward_absorb` (L306) — chiếu hậu cống hút | ✅ **ĐẠT** (phía vật lý) |
| **Nhận diện đối thủ (Identify)** | Bayes 2-giả-thuyết: MIRROR vs CONTEST; signature đàn + tỷ lệ tiền; geometric forgetting + hysteresis. 4 archetype khai báo thì **2 chết** (COOP/PASSIVE không bao giờ được gán) | `_bayes_step` (L119–164), `_ARCHES` (L73) | ⚠️ **MỚI 2/5 lớp** — chỉ trả lời "twin hay không", không biết đối thủ mạnh/yếu/hợp tác/dump |
| **Dự đoán tương lai (Predict)** | ❌ **KHÔNG CÓ**. Không có mô hình hành vi đối thủ; `opp_daily` ghi đầy đủ nhưng **không dòng code nào đọc ra quyết định** (grep xác nhận: chỉ ghi L88/L93, không consume); không dự báo đường giá; không mô phỏng kết quả quyết định. Dự đoán duy nhất = drain vật lý (phía cầu), thuộc dạng giải tích chứ không phải Bayes | `opp_day`/`opp_daily` dead-read; `_daily_plan` dùng `opp_counts` tĩnh từ bàn cờ | ❌ **THIẾU CẢ TẦNG** — đây là khoảng trống lớn nhất |
| **Thích ứng chiến thuật (Adapt)** | mode đổi **duy nhất mục tiêu đàn** (MIRROR 6/5/3 vs CONTEST công thức). Ngưỡng bán, quota cây, lao động, mua bán — **không đổi theo mode**; telemetry không vào vòng điều khiển | `_daily_plan` L410–426 | ⚠️ **1/5 núm** — đổi não không đổi tay |
| **Tự đánh giá hiện trạng (Self-evaluate)** | ❌ **KHÔNG CÓ**. Không sổ KPI (net/ngày, burn, doanh thu vs kế hoạch), không so dự báo với thực tế, không điểm sức khỏe — agent không biết mình đang chạy tốt hay xấu so với chuẩn cho tới cuối trận | `_STATE` chỉ chứa dữ liệu thô phục vụ phân công task, không vòng phản hồi | ❌ **THIẾU** — "gương soi" chưa tồn tại |
| **Tránh kết quả tồi (Risk guard)** | ⚠️ **1/8 mức**: chỉ sàn tiền mặt + survival hire (từng kẹp nghèo $4–8k cả trận vì không có điều kiện thoát — LESSONS_V4 vòng 2); không thư viện failure mode, không detector, không playbook | hire survival, money floor | ⚠️ **SƠ SÀI** — không có khái niệm worst-case |

**Kết luận thẳng thắn:** v4 có *mắt* và *vùng vận động*, chưa có *vỏ não dự đoán* và cũng chưa có *gương soi + vệ binh nội tại*. "Bayes tính toán trước tương lai kết quả" hiện chưa tồn tại dưới bất kỳ dạng nào — Bayes hiện tại chỉ trả lời "đây có phải ảnh của tôi không" trước khi quyết định mua mấy con bò; và agent cũng không hề biết mình đang thắng hay thua cho tới cuối trận. Thiết kế đầy đủ 6 lớp cho v5 ở mục 4.

---

## 4. THIẾT KẾ NÃO 6 LỚP — 4 LỚP BAYES DỰ ĐOÁN + 2 LỚP PHẢN THÂN

Nguyên tắc chung: **mỗi lớp có công thức tường minh, cập nhật theo đêm (flows là đại lượng theo ngày), chi phí O nhỏ, mọi đầu ra phải được consume bởi quyết định cụ thể** (bài học LA-2/LT-3: tính năng không ra quyết định = xóa). Phân tầng: **L1–L4 hướng ngoại** (nhìn đối thủ và tương lai — mandate "linh hoạt theo chiến lược đối thủ qua Bayes"), **L5–L6 hướng nội** (nhìn chính mình — mandate "tự đánh giá + tránh kết quả tồi"); tất cả hội tụ về **bộ meta-controller (4.8)** — nơi đổi kế hoạch giữa trận.

### 4.1 Lớp L1 — Archetype posterior (nhận diện đối thủ bằng Bayes tuần tự)

- **Không gian giả thuyết** H ∈ {`MIRROR` (twin bit-identical), `STRONG-CONTEST` (dòng v3/v4: đa thị trường, threshold-ladder), `COOP` (chia drain ổn định ~drain/2 mỗi bên), `PASSIVE` (yếu/ít bán: melon, random, starter), `DUMP` (dump giá bất thường)}.
- **Vector đặc trưng mỗi đêm** (từ telemetry đã 100% chính xác): net-flow 9 mặt hàng của đối thủ trong ngày + quỹ đạo tiền + hires_today + cấu trúc đàn (COW/GOOSE/SHEEP) + mức dùng đất.
- **Hàm likelihood:** naive Bayes trên 9 kênh flow — mỗi mặt hàng một phân phối Poisson quanh "hồ sơ flow kỳ vọng" của archetype; hồ sơ này **học offline từ 10 trận/thủ thư viện** (ta có đủ mã nguồn + bot để sinh dữ liệu). Giữ kernel đàn + tiền như bản v4 hiện tại cho giả thuyết MIRROR (đã chứng minh chính xác).
- **Cập nhật:** `P(H|D_t) ∝ P(D_t|H)·P(H|D_{t-1})^λ` với λ = 0.8 (geometric forgetting — đối thủ có thể đổi chiến thuật giữa trận).
- **Chốt mode:** posterior argmax + hysteresis (đổi mode chỉ khi P(mới) > 0.6 hai đêm liên tiếp) — chống flip-flop; **cấm MIRROR trước ngày 8** (giữ nguyên luật v4 đã đúng); với Validation Episode (self-play thật), posterior MIRROR sẽ tự thắng bằng symmetry — an toàn T8 mặc nhiên.
- **Chi phí:** O(9 × |H|) mỗi đêm ≈ 50 phép nhân — không đáng kể.

### 4.2 Lớp L2 — Posterior predictive flow (dự báo dòng bán đối thủ ngày mai)

- Mỗi mặt hàng p: ước lượng tốc độ bán đối thủ λ_p với độ bất định — mô hình **Gamma–Poisson** (lambda conjugate, predictive = Negative Binomial), trọng số suy biến theo λ = 0.8.
- Đầu ra: `E[opp_sales_p(mai)]` + phân vị (P25/P75) — **thay thế công thức room tĩnh `−30×opp_COW`** bằng dự báo flow thật (vá trực tiếp điểm yếu W3: telemetry vào quyết định).
- Công thức room mới: `room_p = deficit_p + drain_cum_p − E[opp_sales_p]` (bán quota) và `herd_target_p = f(room_p)` (quy hoạch đàn) — dùng phân vị thận trọng P75 cho quota, P25 cho kế hoạch đàn.
- Đây là chỗ "Bayes tính toán trước" hoạt động thật: không đoán mò "đối thủ mạnh cỡ nào" mà **đo trực diện dòng chảy và ngoại suy ngày mai kèm khoảng tin cậy**.

### 4.3 Lớp L3 — Dự báo đường giá (lai: giải tích engine + L2)

- Engine cho công thức giá chính xác theo tồn kho: `price(inv)`. Quỹ đạo tồn kho: `inv(t+1) = inv(t) + my_sales + E[opp_sales] − drain(t)`.
- ⇒ **mô phỏng giá từng giờ 24h tới cho 9 mặt hàng** (đóng dạng, O(9×24)); dùng để quyết định *bán ngay hay giữ đến ngưỡng tốt hơn* (1-step lookahead + threshold-ladder có chủ đích) thay vì thang ngưỡng tĩnh.
- Bất định từ L2 lan truyền: quyết định dùng đường giá tại phân vị thận trọng.

### 4.4 Lớp L4 — Mô phỏng kết quả quyết định (rollout có giới hạn)

- Với ≤5 quyết định lớn mỗi ngày (ramp bò? mua đất 4? hire #13? tăng quota X? thanh lý?): rollout **7 ngày** dạng dòng chảy (closed-form: dùng L2+L3, không mô phỏng từng unit) → chênh lệch $ kỳ vọng → chọn.
- Thanh lý cuối mùa 26–29 là trường hợp riêng của L4: **DP per-product** trên lưới (ngày × tồn kho) tới giờ 22 ngày 29 (23 giờ vàng) — thay dump thô.
- Ngân sách compute: 5 rollout × 7 ngày × 9 mặt hàng ≈ 10³ phép — vô nghĩa so với step budget.

### 4.5 Chính sách baseline theo archetype (input cho meta-controller 4.8)

| Posterior chiến thắng | Mục tiêu đàn | Thị trường ops | Đặc biệt |
|---|---|---|---|
| MIRROR | chia drain (6/5/3 — giữ luật v4) | ngưỡng chia premium | không phá giá đôi bên |
| STRONG-CONTEST | presence ramp bò sớm 8–10 + kho chứa + drip milk 1.2–1.4× base; wool 2–3 (hợp tác) | pinning ngưỡng; nuốt TOMATO (v4 quota = 0) | FEED make-vs-buy đánh vào burn $35k của đối thủ |
| COOP | giữ share hiện tại | ngưỡng cao, không undercut | duy trì tín hiệu hợp tác qua flow ổn định |
| PASSIVE | max đàn + max quota mọi thị trường trống | bán trọn room | không tốn denial |
| DUMP | giảm exposure mặt hàng bị dump | nâng ngưỡng, chờ drain hút lại | mua wheat rẻ nếu bị dump |

Ghi chú white-box: **ta có toàn bộ mã nguồn v4** — có thể chạy offline v5-ứng-viên vs v4 trên lưới seed, và mô phỏng chính công thức `milk_room −30×opp_COW` của v4 để biết trước phản ứng của nó: **v4 tự rút bò khi v5 ramp bò** (presence valve kế thừa từ v3) → v5 giữ 8–10 bò + stockpile/drip sẽ thu phần 218u premium mà cặp v3/v4 vẫn bỏ hoang (LE-2: ≈ $54–72k/cặp).

### 4.6 Lớp L5 — Tự đánh giá hiện trạng ("gương soi" nội tại)

- **Sổ KPI mỗi đêm** (tận dụng ledger đã chứng minh $0 residual ở P0): net/ngày · gross/ngày · burn phân loại (feed/hire/đất/hạt/thú) · doanh thu theo mặt hàng vs quota kế hoạch · thị phần từng mặt hàng (my_sales / (my + opp)) · dải giá bán trung bình · cây chết · thú trốn · tồn kho ứ đọng.
- **Chuẩn đối chiếu (expected trajectory):** hồ sơ KPI trung bình ± dải P25–P75 từ 10 trận self-play và 10 trận vs v4 chạy offline — agent biết "ngày 12 lành mạnh net nên ~$1.5–2k" thay vì mù tuyệt đối.
- **Điểm sức khỏe H ∈ [0, 1]** tổng hợp 5 thành phần: tiền (xu hướng cash) · doanh thu (net vs kỳ vọng) · thị phần (so mốc 0.5) · tài sản sống (cây chết/thú trốn) · chất lượng dự báo (sai số L2). H ≥ 0.7 xanh · 0.4–0.7 vàng · < 0.4 đỏ → kích hoạt L6.
- Chi phí: cộng dồn từ dữ liệu đã có — O(20) phép/đêm.

### 4.7 Lớp L6 — Vệ binh rủi ro: thư viện failure mode + playbook + lối thoát

- **10 failure mode (F1–F10)**, mỗi mode một tín hiệu phát hiện sớm đo được từ telemetry/L5:
  - F1 death-spiral tiền (cash < sàn bootstrap ∧ đạo hàm âm 2 ngày) · F2 feed crunch (kho wheat < 2 ngày nhu cầu) · F3 crop death cascade (> 3 cây chết/ngày) · F4 herd collapse (escape dây chuyền) · F5 bị dump giá mặt hàng chủ lực (giá < 0.85× ngưỡng 2 ngày) · F6 mất thị phần trầm trọng (share < 0.25 mặt hàng chủ lực 3 ngày) · F7 overbuild/kẹt đất · F8 nhận diện mirror sai (posterior dao động MIRROR/CONTEST) · F9 dự báo lệch kéo dài (MAE > 40% cửa sổ 5 ngày) · F10 quỹ đạo thua ổn định (net đối thủ − net mình > $3k 3 ngày liên tiếp).
- **Playbook 3 cấp** mỗi mode (nhẹ → nặng → khẩn) + **điều kiện THOÁT bắt buộc** — bài học vòng 2 của v4: survival không lối thoát = bẫy nghèo $4–8k triền miên. Ví dụ F1: cấp 1 cắt 2 hire + trì hoãn mua đất; cấp 2 thanh lý tồn kho non-core; cấp 3 bán nguyên liệu; thoát khi cash ≥ 3× chi/ngày ∧ net/ngày > 0.
- **Nguyên tắc minimax khi mù:** khi posterior L1 entropy cao (chưa nhận diện được đối thủ) hoặc H < 0.4 → mọi quyết định của L4 dùng phân vị bi quan (P25) + ràng buộc an toàn cứng (sàn tiền, đệm kho 2 ngày). "Hạ kết quả tồi xuống thấp nhất" đúng nghĩa phân phối, không phải khẩu hiệu.

### 4.8 Bộ meta-controller — nơi "đổi kế hoạch linh hoạt" thành hiện thực

- **6 trạng thái chiến lược:** S-GROW (mặc định, tối đa hóa lợi nhuận) · S-HOLD (bảo toàn, chờ thông tin khi entropy cao) · S-DEFEND (đối thủ STRONG-CONTEST: contest có kiểm soát) · S-RECOVER (H < 0.4 hoặc F cấp 1–2 kích hoạt) · S-SURVIVE (chỉ F1/F3/F4 cấp 3) · S-LIQUIDATE (ngày ≥ 26, DP thanh lý).
- **Luật chuyển:** đầu vào = (posterior L1, dự báo L2, sức khỏe H, trigger L6, ngày). Chuyển trạng thái yêu cầu đạt ngưỡng (posterior > 0.6 hoặc trigger L6 tương ứng) ∧ **dwell tối thiểu 2 ngày** — chống flip-flop (bài học knife-edge); S-SURVIVE/S-RECOVER mang **điều kiện thoát bắt buộc** — không được phép cư trú vĩnh viễn.
- **Mỗi trạng thái gán trọn bộ 5 núm** (đàn/quota/ngưỡng bán/lao động/thanh lý) = ma trận archetype (bảng 4.5) × trạng thái — phần lớn ô dùng baseline archetype chỉnh hệ số theo trạng thái, không cần 30 bộ tham số riêng.

### 4.9 Tự hiệu chỉnh dự báo (calibration — đóng vòng học)

- Mỗi đêm: so E[opp_sales_p] dự báo đêm trước với thực tế → MAE cuộn 5 ngày theo mặt hàng.
- MAE cao → tự điều chỉnh: (a) tăng forgetting λ 0.8 → 0.6 (tin hôm nay hơn); (b) dịch quyết định sang phân vị bi quan hơn; (c) giảm quota mở tối đa cho mặt hàng đang lỗi. λ bị chặn biên [0.5, 0.9] để không tự bóp méo.
- Vòng học đóng: **dự báo → hành động → đo kết quả → hiệu chỉnh dự báo** — đúng nghĩa "đánh giá kết quả mà thay đổi plan" của user, ở tầng vận hành.

---

## 5. KIẾN TRÚC MODULE v5 & ĐIỂM CẮM VÀO MÃ HIỆN CÓ

Nguyên tắc LA-1: **nền v4 + thay đổi đo lường được** — không rebuild. Bảng map module → điểm cắm:

| Module v5 | Chức năng | Cắm vào đâu trong v4.py | Pha |
|---|---|---|---|
| M-1 Perception + | giữ telemetry; thêm kênh tiền/hire đối thủ | `_tm_step` (đã có), `_agent` L1202 | P0 |
| M-2 Bayesian Core (L1+L2) | archetype posterior + flow predictive | thay `_bayes_step` (L119) — giữ giao diện `tm["mode"]`, thêm `tm["posterior"]`, `tm["flow_pred"]` | P1 |
| M-3 Forecast giá (L3) | đường giá 24h | hàm mới gọi từ `_build_orders` (L972) thay ngưỡng tĩnh | P3 |
| M-4 Rollout/DP (L4) | quyết định lớn + thanh lý 26–29 | gọi từ `_daily_plan` (L367) cho 5 quyết định; DP thay nhịp bán d26–29 trong `_build_orders` | P3/P5 |
| M-5 Portfolio Solver | quota động $/action + T/2 + shadow price lao động | thay khối quota cứng L473–505 | P3 |
| M-6 Labor market | Hungarian/auction assignment | thay `_assign_and_act` (L880) — giữ greedy làm fallback | P4 |
| M-7 FEED make-vs-buy | mô hình biên trồng/mua cám | `_daily_plan` (wheat floor đã có 20–24) + logic mua trong `_build_orders` | P2 |
| M-8 Policy table | 5 hàng archetype → bộ tham số baseline | `_daily_plan` đọc `tm["mode"]` như hiện tại nhưng mở rộng núm (đàn + quota + ngưỡng + lao động) | P1 |
| M-9 Self-Assessment (L5) | sổ KPI + chuẩn đối chiếu + điểm sức khỏe H | hàm mới gọi cuối ngày trong `_agent` (L1173); dữ liệu = ledger runtime (chuyển p0.py vào agent) | P0 |
| M-10 Risk Guard (L6) | 10 failure mode + playbook 3 cấp + lối thoát | gọi ngay sau M-9 mỗi đêm; trigger cấp 1 cắm vào `_daily_plan`/`_build_orders` như ràng buộc cứng | P0 lõi → P1 đầy đủ |
| M-11 Calibration (4.9) | sai số dự báo → tự chỉnh λ/quantile | trong vòng update L2 (M-2) | P1 |
| M-12 Meta-Controller (4.8) | state machine 6 trạng thái + dwell | thay chỗ đọc `tm["mode"]` (L410) bằng `tm["strategy"]`; 5 núm đọc từ trạng thái | P1 |

---

## 6. CHIẾN LƯỢC THANG ĐẤU KAGGLE — ĐỐI ĐẦU TUẦN TỰ ĐA DẠNG

- **Validation (bắt buộc đi trước):** self-play với bản sao chính mình → L1 posterior MIRROR thắng tự nhiên bởi đối xứng flow; floor chia drain giữ ổn định; gate D4.
- **Thư viện đối thủ chuẩn (ladder coverage):** melon_maxxer, random, starter, v2, crop-baseline, v3, v4, + 3 bot tổng hợp mới (dump-bot, hoarder-bot, wheat-masser) — mỗi cặp 4 seed hai phía = 88 trận/lượt Sweep (~6 phút máy).
- **Sinh hồ sơ likelihood L1:** 10 trận mỗi archetype từ thư viện trên → hồ sơ flow kỳ vọng (bước 4.1).
- **Quản lý 2 submission active:** v4-stable giữ làm bản an toàn; v5-dev nộp thử nghiệm hằng ngày từ khi đạt gate P1 (1.08×). Chỉ "thăng chức" v5 lên primary khi đạt trọn D1–D6.
- **5 submit/ngày = 5 phép thử có kiểm soát:** mỗi lần nộp đi kèm một biến thay đổi duy nhất — tránh burn đột biến rating (Bradley-Terry chỉ đo W/L).

---

## 7. LỘ TRÌNH P0–P6 (mỗi pha: nhiệm vụ → gate nghiệm thu)

**P0 — Nền tri giác + gương soi + vệ binh lõi (ước 1–2 ngày)**
- Nối telemetry vào quyết định dạng tối thiểu: `room` dùng `opp_daily` flows thay `opp_counts` tĩnh (bản L2 giản lược: trung bình trượt 3 ngày, chưa Gamma–Poisson).
- Kênh tiền/hire đối thủ vào `tm` (dự báo lock lao động đối thủ).
- **M-9 Self-Assessment runtime:** sổ KPI mỗi đêm + chuẩn đối chiếu offline + điểm sức khỏe H (ledger $0 residual chuyển từ bench vào agent).
- **M-10 Risk Guard lõi:** F1 (death-spiral) + F2 (feed crunch) + F3 (crop cascade) với playbook 3 cấp và điều kiện thoát — chính thức hóa survival mode v4 thành cơ chế có hồi phục.
- Xóa COOP/PASSIVE chết khỏi `_ARCHES` (tạm 2 lớp, mở lại ở P1 với đủ 5).
- Endgame surge (hire +1–2 ngày 26–28 khi giá trị biên thu hoạch > fib) + nhịp bán dần 26–29; straw urgency window đúng.
- **Gate:** two-sided 24 seed vs v4 ≥ 1.05×; vs v3 không hồi phục dưới 1.05×; mirror 10 trận ≥ $30k/bên; **SA chạy thật (KPI khớp ledger, residual $0); không trận nào kẹt trạng thái khẩn cấp quá 3 ngày trên 24 seed.**

**P1 — NÃO 6 LỚP đầy đủ: Bayes L1+L2 + meta-controller + RG đủ 10 mode + calibration (theo mandate "linh hoạt, phân tích, đổi plan")**
- Cài đúng thiết kế 4.1/4.2 (5 archetype + Gamma–Poisson predictive) + bảng 4.5; sinh hồ sơ likelihood offline từ thư viện 10 đối thủ.
- M-12 meta-controller 6 trạng thái với dwell 2 đêm + lối thoát; 5 núm (đàn/quota/ngưỡng/lao động/thanh lý) đọc từ trạng thái.
- M-10 đủ 10 failure mode; M-11 calibration tự hiệu chỉnh λ/quantile.
- **Gate:** nhận diện archetype (offline, đến ngày 10) ≥ 80%; two-sided vs v4 ≥ 1.08×; forecast MAE < 25% sau ngày 5; mọi F phát hiện ≤ 24h trong sweep; coverage ladder không tụt.

**P2 — FEED make-vs-buy (mỏ tiền lớn nhất — +$8–15k, không cần não)**
- Mô hình chi phí đầy đủ tự trồng 1 wheat (~$25–30: đất + hạt + tưới + lao động) vs giá mua động; kho đệm 2 ngày; mục tiêu cắt 30–40% khoản feedbuy $35k.
- **Gate:** feedbuy giảm ≥ 25% (ledger đo); net solo ≥ +$5k; two-sided vs v4 ≥ 1.10×; giữ mọi gate P1.

**P3 — Portfolio Solver + dự báo giá (L3) + rollout (L4)**
- Quota động theo $/action với ràng buộc T/2 + shadow price; mô phỏng giá 24h vào quyết định bán; rollout 5 quyết định/ngày; DP thanh lý.
- **Gate:** two-sided vs v4 ≥ 1.15×; solo gross ≥ $110k (đối chiếu mục tiêu RESEARCH); biên tệ nhất ≥ 0.90×.

**P4 — Labor market: Hungarian/auction assignment + zoning**
- Ma trận 13×~70; O(n²m) ≈ 10⁴–10⁵ op/step; fallback greedy; zoning cụm đất.
- **Gate:** MOVE lãng phí (đo bằng diag) giảm ≥ 10%; two-sided vs v4 ≥ 1.18×.

**P5 — Đánh bóng: FERT động (bón khi giá FERT < $78 biên), TOMATO own (town ~300/mùa + shop), fert-on-wheat**
- **Gate:** two-sided vs v4 ≥ 1.20×; giữ nguyên mọi gate trước + D3 (tệ nhất ≥ 0.95×).

**P6 — Đóng băng & thăng chức**
- AST strip → `submission_v5.py` (pipeline y như quy trình v4); syntax + import check; sweep chuẩn 88 trận cuối; đổi primary submission khi trọn D1–D5.

Thứ tự đã chốt theo mandate của user (phiên bản 2.0): **não trước** — P1 dựng trọn hệ Bayes + meta-controller + phản thân để mọi pha sau hưởng hạ tầng thích ứng; FEED (P2) vẫn là mỏ tiền lớn nhất và không phụ thuộc não. Ghi chú rủi ro đổi thứ tự: nếu P1 trễ lịch, P2 (FEED) có thể kéo lên trước mà không phá phụ thuộc.

---

## 8. PROTOCOL KIỂM ĐỊNH BẮT BUỘC (áp cho mọi pha)

1. Mọi thay đổi một núm → benchmark two-sided 24 seed (100–123) trước/sau; ghi worklog.
2. Chuẩn 4 lượt sweep mỗi pha: vs v4 · vs v3 · mirror 10 · ladder coverage 88 trận.
3. Theo dõi riêng chỉ số "rủi ro gãy": trận tệ nhất, không chỉ trung bình.
4. Quy tắc dừng: 3 vòng liên tiếp không tăng ≥ 2% tỷ lệ hai phía → chốt phiên bản, chuyển pha.
5. Cấm mọi tối ưu chưa đo (LA-5); cấm tính năng không consume (LA-2).
6. Ba chỉ số phản thân mỗi pha (cho mandate "tự đánh giá"): **forecast MAE** (sai số dự báo L2) · **detector latency** (giờ từ sự kiện đến khi L6 phát hiện) · **recovery time** (giờ từ phát hiện đến khi thoát failure mode) — mục tiêu: MAE < 25% sau ngày 5 · latency ≤ 24h · recovery ≤ 3 ngày.
7. Stress-test cố định: 2 seed "nghịch" (bootstrap nghèo — chọn từ tập 24 seed có cash thấp nhất) chạy mỗi pha để xác nhận playbook F1/F2 thoát hiểm thật, không chỉ trên giấy.

---

## 9. RỦI RO & GIẢM NHẸ (tóm tắt, chi tiết ở LESSONS_V4 §5.3)

| Rủi ro chính cho v5 | Giảm nhẹ |
|---|---|
| L1 nhầm archetype giữa trận (đối thủ lai) | hysteresis 2 đêm + chính sách mặc định STRONG-CONTEST an toàn |
| L2 dự báo lệch khi đối thủ đổi chiến thuật | λ = 0.8 forgetting + phân vị thận trọng; fallback room tĩnh |
| Solver động dao động quota (ping-pong cây) | sticky + damping 15% (bài học vòng 1 v1) |
| Hungarian chậm vượt step budget | đo trước, fallback greedy |
| Phá nền kinh tế khi refactor | từng pha một gate; không rebuild toàn cục |
| Overfit clone, yếu trên ladder | thư viện 10 archetype + coverage bắt buộc |
| 5 submit/ngày burn rating | submission đôi, mỗi nộp 1 biến đổi |
| Meta-controller flip-flop giữa 6 trạng thái | dwell 2 đêm + ngưỡng posterior 0.6 + điều kiện thoát một chiều |
| Vòng phản hồi calibration tự bóp méo dự báo | λ chặn biên [0.5, 0.9]; MAE đo cửa sổ cuộn 5 ngày; dịch quantile có giới hạn |
| Phức tạp 12 module — khó debug, chậm phát triển | mỗi module một gate riêng; mọi lớp có fallback tĩnh (não hỏng → nền kinh tế v4 vẫn sống) |

---

## 10. BA QUYẾT ĐỊNH MỞ CHO USER — ĐÃ CHỐT TOÀN BỘ (phiên bản 2.1)

1. ~~Thứ tự ưu tiên~~ — **đã chốt theo mandate user: não trước** (P1 = Bayes 6 lớp + meta-controller; P2 = FEED).
2. ~~Xác nhận chuẩn "hoàn toàn"~~ — **USER CHỐT "D1-D6 ok, đủ"** (phiên 2025-06): D1–D6 với ngưỡng 1.25×/90%/0.95× + phản thân (phát hiện ≤ 24h, hồi phục ≤ 3 ngày) là định nghĩa chính thức của "đánh bại v4 hoàn toàn".
3. ~~Thư viện đối thủ~~ — **USER CHỐT "đủ"**: 3 bot tổng hợp (dump/hoarder/wheat-masser) + thư viện hiện có là đủ khởi động; bổ sung thủ từ meta Kaggle thật sau khi có dữ liệu thang đấu.
4. ~~Khẩu vị rủi ro khi mù~~ — **USER CHỐT "minimax"**: khi entropy posterior cao hoặc H < 4/10 → mặc định phân vị bi quan P25 + ràng buộc an toàn cứng (mục 4.7). Nguyên tắc điều khiển v5: **hạ kết quả tồi xuống thấp nhất trước, tối đa hóa kỳ vọng sau**.

---

## 11. HẠ TẦNG ARENA OBSERVER UI — "QUAN SÁT CẢ 2 BÊN TRIỂN KHAI CHIẾN THUẬT ĐẾN CUỐI" (phiên bản 2.1)

User yêu cầu xem trực tiếp trận v4↔v5 suốt 720 turn (30 ngày × 24 giờ) để rút kinh nghiệm chiến thuật thực chiến. Kiểm chứng: dữ liệu Kaggle (kaggle competitions download) cần xác thực — sandbox không có credential; và gói data chỉ chứa môi trường (đã có sẵn kaggle-environments 1.32.7) chứ **không kèm UI trận đấu** — `env.render(mode="ipython")` chỉ là widget notebook. ⇒ tự xây Arena:

- **run_battle.py** (kaggriculture/arena/): bọc 2 agent bằng recorder, chạy `make("kaggriculture")`, xuất JSONL từng turn ra stdout (obs public + action 2 bên + chẩn đoán nội tâm v5) + kết quả cuối. Nguồn sự thật duy nhất vẫn là engine Kaggle thật.
- **arena-service** (mini-services/, bun + socket.io, port 3005): nhận lệnh bắt đầu trận, spawn python3, chuyển tiếp JSONL → event socket cho UI; cho phép chạy nhiều trận nối tiếp (seed sweep).
- **UI tại / ** (Next.js): 2 bảng farm 10×10 trực tiếp (tile cây/tuổi/thú/weed, vị trí farmer/hands), biểu đồ giá 9 mặt hàng + market inventory, timeline scrub 720 turn, event log 2 bên, bảng chẩn đoán nội tâm v5 (posterior archetype · flow dự báo · sức khỏe H · trạng thái meta-controller · failure mode) — nơi user nhìn thấy "não 6 lớp" làm việc thật.
- **Vai trò trong quy trình:** mọi trận nghiệm thu gate P0–P6 đều chạy qua Arena; user xem v5 thay đổi chiến thuật giữa trận ở đâu và hỏi ngược "tại sao quyết định này" → nguồn câu hỏi điều chỉnh chiến thuật mới đúng tinh thần thực chiến của user.


## 12. BIÊN BẢN TRIỂN KHAI v5.2 "P1-TUNED" (2 TRỌNG TÂM CỦA USER) — 21:00

User chỉ định 2 trọng tâm phát triển v5: **(1) v5 dùng Bayes xác định kết quả của chiến lược hiện tại giữa bản thân và đối thủ; (2) v5 linh hoạt điều chỉnh chiến lược để đấu với v4.** v5.2 là bản P1 đã tinh chỉnh theo đúng 2 trục này, nghiệm thu bằng battery 20 seed.

### 12.1 Trọng tâm 1 — Bayes đánh giá kết quả (L3-Race + L3-Price + Calibration)

- **EMA run-rate (α=0.45)** làm mượt doanh thu 2 bên trước khi ngoại suy E[tiền cuối] — v5.1 bị flip-flop tier ±50%/đêm vì bán theo đợt làm run-rate nhảy vọt.
- **Dwell 2 đêm**: tier LEAD/TIGHT/BEHIND chỉ đổi khi tín hiệu lặp lại 2 đêm liên tiếp (có `tier_cand` hiển thị trong diag để quan sát tín hiệu đang tranh).
- **Calibration M-11 (lite)**: mỗi đêm so E[tiền] dự báo đêm trước với tiền thực → `calib_mae` tích lũy 8 đêm, xuất ra diag — não tự biết mình đo sai bao nhiêu (vòng học đóng đúng thiết kế 4.9).
- **L3-Price** dự báo giá +3 ngày từng mặt hàng (drift = E[opp flow] − town absorb) → đầu vào cho front-run/hold-back VÀ cho các núm cạnh tranh ở 12.2.

### 12.2 Trọng tâm 2 — linh hoạt chống v4 (bảng núm hoàn chỉnh)

| Núm | Kích hoạt | Hành động | Bài học gốc |
|---|---|---|---|
| `straw_compete` | px_pred dâu tăng ≥1.05× + ≥2 shop cầu dâu | tính room KHÔNG trừ opp pipeline | seed 2: nhượng dâu đúng lúc $265 (-$12.9k) |
| `room sub 0.85→0.35` | px_pred tăng ≥1.04× (mọi mặt hàng) | giảm hệ số nhượng trong room() | seed 42: dưa 96 vs 48 quả (-$8.4k) |
| `knobs_animal` + animal floor | px_pred sữa/len tăng HOẶC shop draw (≥2 PIZZA/ICE/SMOOTHIE, ≥1 YARN) | cap opp_sub ở 0.45×absorb + nâng target tối thiểu | seed 555: v4 phóng 15 thú độc chiếm $25k |
| Thứ tự mua có điều kiện | thị trường động vật sâu (milk+yarn shop ≥2) | BUY_ANIMAL lên TRƯỚC BUY_SEED trong list lệnh | seed 555: $274-510 sáng nào cũng bị hạt ăn sạch |
| `late_ext` | giá EGG/MILK/WOOL ≥1.25× base | nới window mua thú +2 ngày | seed 555: cửa sổ bò đóng d16 |
| `fast_wheat` | tier BEHIND | quota wheat +3 (vòng tiền 5 ngày) | thay cho mở đàn mù quáng |
| `herd_expand` (đã sửa) | BEHIND + nợ nước ≤2 + dưới cap + tiền ≥$2.5k | chỉ +1 thú (chọn chân room tốt nhất) | seed 2 bản cũ: +2/+2/+1 giết ruộng |
| Water labor governance | `water_debt` (nợ tưới cuối ngày, L5) | cap đàn −2 khi nợ ≥3; +1 thợ khi nợ ≥1; tưới parity lên tier 2 | seed 2: 13 thú × 3 turn = ruộng chết |

Cùng 5 núm gốc v5-P1 (front_run/hold_back/than lý sớm/threshold ×0.93/×1.02/+1 thợ khi BEHIND).

### 12.3 Sửa lỗi cơ học (bắt từ bài học máu)

1. **Bug elif tưới (chết cây)**: `cu≥1` vào ngày chẵn lẻ (parity-ON) chỉ được tier 3 → bị SERVICE đói → cu=2 → cỏ dại. Fix: cu≥1 luôn tier 0 bất kể parity (v5.2 cuối cùng). Tưới vẫn mỗi 2 ngày/plant (cùng volume v4) nhưng ưu tiên đúng.
2. **Animal reserve**: hạt đắt ăn sạch tiền buổi sáng → BUY_ANIMAL fail cả mùa (seed 42: 1 bò).
3. **Window closing**: plan MELON 14 ngày 14, mua 11 hạt, trồng 0 → leo tier PLANT lên 2 khi window đóng ≤3 ngày.
4. **`water_crit_late` ghi ĐÈ** giờ cuối (hour 23) thay vì max — đo đúng nợ cuối ngày.

### 12.4 Thí nghiệm thất bại (đã revert — mỗi cái một bài học)

- **Daily-crit đảo ngược ưu tiên**: cu≥1 tier 0 mọi cây mọi ngày (bản đầu) — cây sống nhưng cướp capacity → ruộng trống. Sửa về đúng semantics trên.
- **Parity chase** (đuổi đàn theo đối thủ +2/+2): giúp seed 555 nhưng giết seed 3 (0.717×) — v5 ruộng đầy + đuổi 5 thú = quá tải. Kết luận: cấu trúc đúng là tín hiệu THỊ TRƯỜNG (giá/shop), không phải chạy đua hành vi đối thủ.
- **Straw capital balance** (cắt dâu khi đàn thiếu): đúng hướng nhưng cứng — nhường chỗ cho tín hiệu giá.

### 12.5 Kết quả nghiệm thu battery 20 seed (run_battle v5 vs v4)

| Chỉ số | v5.1 (trước) | **v5.2 (sau)** |
|---|---|---|
| Tỷ lệ tổng tiền | 0.948× | **1.063×** |
| Tỷ lệ thắng | 40% (4/10) | **65% (13/20)** |
| Median ratio | — | 1.081 |
| P25 | — | 0.970 |
| Tệ nhất | 0.763× (seed 2) | 0.826× (seed 19) |

Xác nhận qua Arena UI (seed 555: banner "🏆 v5 THẮNG! 1.00×", não hiển thị tier/tier_cand/proj/calib đầy đủ). 7 seed còn thua (42/101/3/19/606/7/808) đều là vấn đề **cân bằng danh mục cấu trúc** — wheat volume + phân bổ cây/thú theo $/action — chính là mục tiêu M-2 Solver (P3) và P2 FEED, không phải núm.

### 12.6 Tiếp theo (đúng lộ trình §7)

P1 gate 1.08× chưa đạt (1.063×) — thiếu đúng phần P1 đầy đủ (L1 5-archetype + Gamma-Poisson L2). Khuyến nghị: hoặc hoàn thiện P1 đúng thiết kế (nhận diện archetype + predictive flow), hoặc kéo P2 (FEED make-vs-buy, +$8-15k không cần não) lên trước vì 7 seed thua đều nhạy chi phí cám + volume wheat.


---
*KAIN — hết kế hoạch phiên bản 2.1 (đã ký chốt 4 quyết định + hạ tầng Arena Observer). File này là hợp đồng triển khai v5; mọi pha P khởi động kèm gate nghiệm thu bằng benchmark, mọi số liệu đối chiếu được với bench/ và worklog.*

## 13. BIÊN BẢN v5.3 (P2 FEED + L1 ARCHETYPE + L2 GAMMA-POISSON) — 8 Sep

**Lệnh user:** "Trước tiên kéo P2 theo khuyến nghị sau đó hoàn thiện L1 archetype + Gamma-Poisson. Sau đó thảo luận chi tiết trước khi nâng cấp Phase 5."

### 13.1 Phát hiện đảo ngược giả định P2 (quan trọng nhất của phiên này)

Khuyến nghị mục 12 ("kéo P2 FEED +$8-15k không cần não vì 7 seed thua nhạy chi phí cám")
đã được kiểm định A/B và **BỊ ĐẢO NGƯỢC**:

- Trace seed 42: từ d26 cả 2 agent rơi vào vòng "mua 110-120u wheat/ngày rồi bán
  150u cùng ngày" — ban đầu đọc là máy nghiền tiền (mua $45 bán $19).
- Bản v5.3-r1 cắt hẳn mua (make-vs-buy thuần: gate $34, dự báo cung 2 ngày, d26+
  ngừng mua) → feedbuy rơi từ ~$31k → ~$2k NHƯNG two-sided 20 seed tụt 1.058→1.016,
  tệ nhất 0.856→0.738. Bản P2-only (cô lập) mất **−0.12x/seed** (104: 1.115→0.922,
  106: 1.295→1.081, 111: 1.325→1.070).
- Cơ chế thật (đã hiểu): "churn" wheat là **VŨ KHÍ zero-sum** — áp lực mua của v5
  nâng mặt giá wheat (deficit sâu hơn), đánh thuế vào feedbuy $32-41k của v4
  (net-buyer 1077u/mùa) và bán self-grown 500u+/mùa đắt hơn. Ngừng mua = tự giải
  giáp + v4 được cám rẻ. Town drain hấp thụ ~35u/ngày BẤT CHẲP giá → ai bán vào
  drain ở giá cao hơn sẽ thắng.
- **P2 đúng nghĩa = FEED WARFARE** (giữ nguyên cơ chế mua v5.2 như một vũ khí),
  không phải feed-thrift. Mục tiêu P2 mới cho Phase 5: đo bằng ledger feedbuy
  "$ paid premium" của ĐỐI THỦ (thuế thu được) thay vì "tiết kiệm feedbuy của mình".

### 13.2 Kiến trúc v5.3 chốt (behavior-frozen + observers)

Nguyên tắc: **mọi coupling hành vi sớm đều −0.02-0.04x** trên benchmark 20 seed
(v4 không phân biệt được các giả thuyết flow — mix wheat của v4 khác nhau theo
seed nên flow-ll đọc nhầm CONTEST/COOP/PASSIVE). Chốt:

- **Hành vi = v5.2 NGUYÊN TRẠNG** (tái hiện 1.058x/27/40 chính xác từng đô la).
- **L1 (5 archetype)**: 2 tầng — pm twin-kernel (v5.2, kiểm chứng) + flow posterior
  4-giả-thuyết (naive Bayes 9 kênh Poisson, softmax τ=5, forgetting 0.8, warmup
  d7+50u, hysteresis 2 đêm nghiêm ngặt). CHỈ MIRROR (kernel) và PASSIVE-cấu-trúc
  (P>0.75 hai đêm + tiền đối thủ <45% mình) được đổi playbook; COOP/DUMP posterior
  tính + hiển thị (diag) nhưng không hành động — chờ validation Phase 5.
- **L2 Gamma-Poisson**: `_l2_night` mỗi sáng — conjugate decay-0.8 (a←0.8a+x,
  b←0.8b+1), predictive NB: E/P25/P75 + **l2_mae calibration** (M-11). Chạy như
  OBSERVER (tm["l2_pred"]) — coupling P75 vào milk_sub đã thử, đo âm, revert.
- **P2 đo lường**: tm["feedbuy"/"feed_units"] + diag "feed" (buy$/units/px_avg)
  — ledger P2 cho Arena UI mỗi trận.
- Bài học coupling đã thử và revert (4 bản r1-r4, mỗi bản benchmark đầy đủ):
  scale-likelihood hỗn hợp kernel×Poisson (posterior MIRROR 0.99 sai khi đấu v4),
  instant-flip hysteresis, E trend-blend 0.55/0.45, P75 subs, mua theo dự báo
  cung — tất cả ghi trong worklog Task 17 kèm số liệu.

### 13.3 Kết quả chốt

20-seed two-sided (100-119, mỗi seed 2 ghế): **1.058x · 27/40 (67.5%) · median
1.045 · P25 1.005 · worst 0.856** — đúng baseline, giờ với não 5 lớp đầy đủ
đo được (L1 posterior + L2 quantiles + MAE 2-3 + feed ledger) trong Arena UI.

### 13.4 Điểm thảo luận Phase 5 (đã định sẵn cho user)

1. P2 Feed Warfare: đo thuế trên v4 (feedbuy premium) thay vì tiết kiệm — cần
   thiết kế thí nghiệm "pump có điều kiện" theo đàn v4 (herd ≥ 12?).
2. L1 activation: học profile offline từ thư viện bot (10 trận/bot như PLAN
   §4.1 gốc) thay vì profile tay — rồi mới bật coupling PASSIVE/COOP/DUMP.
3. L2 coupling: chỉ kích hoạt khi l2_mae < 1.5 (đủ tin cậy) — quy tắc tự tin.
4. M-2 Solver (P3) vẫn là mỏ tiền thật theo đúng plan ($/action + T/2).

## 14. BIÊN BẢN PHASE 5 (20 Sep) — "TRIẾT KHAI THEO 4 HƯỚNG + KIỂM ĐỊNH ARENA"

**Lệnh user:** "Triển khai Phase 5 theo thứ tự bạn đề xuất. sau đó quan sát đối đầu giữa v5 với v4 và v3. Đánh giá kết quả, cập nhật RULES.md nếu có phát hiện mới, nâng cấp v5 nếu có thể. Báo cáo và push. Ngoài ra kiểm tra lại Kaggriculture Arena đã triển khai hoàn toàn chính xác theo upload/README.md chưa."

### 14.1 Kiểm định Arena/engine TRƯỚC khi đụng v5 (đúng mối lo của user)

Audit 3 phía (engine kaggle-environments 1.32.7 ↔ upload/README.md ↔ v5/v4/run_battle.py) bằng subagent + 45.000 phép kiểm số học: **YELLOW — không sai lệch nào phá hỏng mô phỏng** (price curve 9 mặt hàng, lịch crop/thú, shop demand, fib hire, drain timing khớp tuyệt đối; run_battle chỉ truyền seed, không override). Phát hiện 13 hành vi ẩn engine (R64–R67 RULES.md): ngày 29 chỉ 23 giờ không refresh cuối, kho đầy chặn mua, RNG dùng chung weed+shop, SELL rút từ shed thôi, v.v. → đã nhập RULES.md mục Q.

### 14.2 Triển khai Phase 5 theo protocol A/B (mỗi biến thể đúng 1 delta, 20 seed two-sided)

| Bước | Biến thể | Kết quả | Phán quyết |
|---|---|---|---|
| 5.1a | Sửa hằng số sai (wheat yield 5→3.0 đo thực, melon cycle 13→11) | 1.058x = baseline | GIỮ |
| 5.1+5.2 | +E8-lite drain-aware hold d22–27 + p3_lo minimax + px_after/rev_stream/pipe_rest/_shop_slots_left + opp_herd/opp_wnet telemetry | **1.060x, worst 0.856→0.886** | **GIỮ = v5.4** |
| 5.3 | +pump wheat điều kiện (opp net-buyer & đàn ≥10) | 1.060x, 26/40 | REVERT (net −$379/40 game) |
| 5.4 | +TOMATO mở có gate | 1.027x, 23/40, worst 0.766 | REVERT (−0.033x) |
| 5.5 | +PROFILES học offline (profile_collect.py) | ≈neutral | Tư liệu (bench/profiles_learned.json) |

### 14.3 Kết quả chốt v5.4 (battery chính thức, byte-khớp p4b trên 3 seed spot-check)

- **vs v4: 1.060x · 27/40 (67.5%) · median 1.047 · P25 1.010 · worst 0.886** (v5.3: 1.058x/27/40/0.856)
- **vs v3: 1.161x · 38/40 (95.0%) · median 1.162 · P25 1.099 · worst 0.889** ← MỤC TIÊU 95% ĐẠT phía v3
- Ghi nhận: E8 đo thực tế đã gần cạn từ v5.2 (tồn dư cuối $250–800) — ước tính "+$3–5k" của LESSONS là thời v4

### 14.4 Bài học then chốt (đầy đủ ở RULES.md mục Q: R64–R73)

1. **R69**: v4 wheat-flow là churn hai chiều (P25 −9/P75 +11) — "net-buyer" là theo-seed, không phải theo-archetype → best-response phải gate bằng telemetry sống
2. **R70**: cơ hội phí wheat-feed áp đảo mọi kênh cây nhỏ — TOMATO chỉ Solver $/action toàn cục mới mở nổi
3. **R72**: PROFILES viết tay sai kênh WHEAT (25 vs đo 0.7) — cột gốc lỗi L1 r1–r4; profile học đã lưu
4. **R73**: núm "đúng lý thuyết 100%" (pump) vẫn thua bằng số — benchmark là phán quyết cuối

### 14.5 Kết luận & hướng tiếp theo

Kho núm dễ ĐÃ CẠN: 7 núm v5.2 + 3 thử Phase 5 (2 revert, 1 giữ) → mọi con đường nhỏ bị đóng, trừ kết luận hội tụ: **P3 Solver $/action + T/2 là mỏ cuối để đạt 95% vs v4** (cần mean ~1.16–1.22x, tức +$5–8k/mùa). v5.4 hiện giữ: 1.060x vs v4 (67.5%) + 95.0% vs v3 + worst ≥0.886 cả 2 cặp.

## 15. BIÊN BẢN TASK 21 — GT-LAND + LỚP LÝ THUYẾT TRÒ CHƠI 2 CẤP (v5.5, 20 Sep)

**Lệnh user:** dùng token `upload/PAT vietnq.rtf` cho push; quan sát "đất trống nhiều bằng khu cuối" → 2 câu hỏi (mua đất lãng phí? chiến lược tối ưu đất + tài nguyên?); yêu cầu áp dụng Lý thuyết trò chơi ở **bậc nhân quả 2** với kiến trúc **720 lượt = 720 vòng tính nhỏ, mỗi 24 lượt = 1 vòng toàn cục 2 bậc**.

### 15.1 Chẩn đoán đất (trước khi đổi code)
- Parse 36 trận v5.4 vs v4: v5 trống TB 48/100 ô, v4 52/100 — đúng quan sát user
- Quadrant: NW đầy · NE ($1k) 30.9 cây · **SW ($2k) 15.7/25 · SE ($4k) 18.9/25** — 60–76% trống trên đất đắt
- Lao động: 91% slot dùng (PASS 3%) → **đất trống = ràng buộc lao động + quota, không phải quên trồng**
- Mua đất theo gate owned_empty ≤ 14 (ruộng đầy mới mua) — tín hiệu đúng nhưng lấp không kịp

### 15.2 Chuỗi thí nghiệm A/B (protocol Task 20: 1 delta, 20 seed two-sided = 40 game)

| Biến thể | Delta | vs v4 | Phán quyết |
|---|---|---|---|
| vL1 | Lấp đất: quota wheat 34 + cap 15 thợ khi trống ≥ 20 | 0.886x / 4/40 / worst 0.702 | **REVERT — thảm họa −0.174x, 20/20 seed âm** (R75: tăng cung wheat phá pump R37) |
| vL2 | Bỏ quadrant SE ($4k) | 1.112x / 30/40 / worst 0.831 | GIỮ tạm (+0.052x, t=2.33) nhưng đuôi xấu |
| vL3 | vL2 + lấp | 1.091x smoke | Bỏ (thành phần lấp độc hại) |
| vL5 | **Đất tối thiểu 50 ô (bỏ SW+SE, tiết kiệm $6k)** | **1.158x / 34/40 / worst 0.879** | **GIỮ — paired +0.102x, t=4.71, p<0.0002** |
| vL6 | Cận dưới 25 ô | 1.078x / 28/40 | Đỉnh xác nhận ở 50 (đường cong U ngược R74) |
| vG | **vL5 + GT-Cournot 2 cấp** | **1.162x / 34/40 / P25 1.096** | **GIỮ — v5.5 chính thức** (+95.0% vs v3, worst 0.974) |
| vH | vG + best-response đàn (opp_herd≥13 → cap+3) | 1.165x / 34/40 | **REVERT — wash** (+0.003 vs v4, −0.005 vs v3, R78: tín hiệu đàn đến muộn) |

### 15.3 Lớp GT-Cournot 2 cấp (đúng kiến trúc user yêu cầu)
- **Macro (mỗi 24 lượt, hour 0–1)**: đọc L2 Gamma-Poisson E/P25/P75 dòng bán đối thủ mỗi kênh → tín hiệu Cournot: `dump_sig` (P75 ≥ 8u và ≥ 1.5×E — lumpy) / `calm_sig`; ghi `tm["gt"]` cho diag Arena
- **Micro (mỗi lượt)**: điều chế ngưỡng `_hold`: dump_sig → ×0.96 (Stackelberg front-run — bán trước cú dội vì inv +o > drain làm giá mai thấp hơn); calm + px_pred rising → ×1.04 (monopoly restraint)
- Cơ sở: đường cong đất 4 điểm CHÍNH LÀCournot capacity (R74–R75) — lý thuyết trò chơi cho hướng (capacity restraint, monopoly markup, front-run), benchmark cho phán quyết (R73)

### 15.4 Kết quả chính thức v5.5
- vs v4: **1.162x · 34/40 (85%) · median 1.138 · P25 1.096 · worst 0.879** (v5.4: 1.060x/67.5%/0.886)
- vs v3: **1.311x · 38/40 (95.0%) · P25 1.244 · worst 0.974** (v5.4: 1.161x/95.0%/0.889)
- 6 trận thua vs v4: 4 knife-edge (≤3.3%) + 2 cấu trúc (seed 107/119 — v4 15 thú thị trường sâu, không tín hiệu sớm, R79)
- Tài liệu: RULES.md v1.3 mục R (R74–R79); v5.py 2.464 dòng; backup v5.4 /tmp/v54_backup.py
- Chưa giải: 95% vs v4 cần 1.22x — mỏ còn lại đúng như PLAN §7 dự phóng: P3 Solver $/action T/2 toàn cục (thay bảng quota cứng bằng tối ưu hóa $/action theo trạng thái từng ngày)
