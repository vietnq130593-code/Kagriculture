# PLAN_V5 — KẾ HOẠCH TRIỂN KHAI v5 "ORCHESTRATOR" (đánh bại v4 hoàn toàn)

**Tác giả:** KAIN (kỹ sư AI · kiến trúc sư hệ thống · chuyên gia thuật toán)
**Mục tiêu tuyệt đối:** v5 đánh bại v4 một cách hoàn toàn — theo chuẩn dominance 5 điều kiện (mục 1.2), không phải "thua đôi vòng"
**Nền tảng:** LESSONS_V4.md (27 bài học) · RESEARCH_v4.md v2.0 · p0_results.json (ledger $0 residual) · mã nguồn đầy đủ v2/v3/v4 (lợi thế white-box)
**Trạng thái tài liệu:** bản thảo thảo luận — chờ user chốt 3 quyết định mở ở mục 10 trước khi khởi động P0

---

## 0. TÓM TẮT ĐIỀU HÀNH

v4 hiện là một **orchestrator có nền kinh tế mạnh nhưng não tri giác bán phần**: mắt tinh (telemetry 100% chính xác), tay vững (nền kinh tế v3 + 8 edges), nhưng **vùng não "dự đoán tương lai và đổi chiến thuật" chưa được nối**. Cụ thể: Bayes của v4 chỉ là *bộ phân loại 2 lớp* (twin hay không) — nó **không dự đoán** đối thủ ngày mai bán gì, không dự báo đường giá, không mô phỏng kết quả của quyết định trước khi ra quyết định.

Kế hoạch v5 xây đúng kiến trúc mà user mô tả — **1 điều phối trung tâm (orchestrator) điều động nhân công con (executor)** — và nâng não lên 4 lớp Bayes (phân loại → dự báo → dự báo giá → mô phỏng kết quả), mỗi lớp có công thức cụ thể, chi phí tính toán đo được, và cổng nghiệm thu bằng benchmark. Kết cấu thay đổi được sắp theo pha P0–P6, mỗi pha có gate two-sided 24 seed; ước lượng giá trị còn lại của toàn bộ kế hoạch: **+$15–30k/mùa** so với v4, hướng tới vượt ngưỡng knife-edge ~1.25×.

---

## 1. MỤC TIÊU & TIÊU CHUẨN "ĐÁNH BẠI v4 HOÀN TOÀN"

### 1.1 Định nghĩa mục tiêu

Đối thủ trực tiếp cần đánh bại: `submission_v4.py` (order-invariant, 1.117× vs v3, mirror-safe). Đồng thời giữ mọi chuẩn an toàn đã có (meta coverage, validation self-play).

### 1.2 Chuẩn dominance 5 điều kiện (kế thừa LESSONS_V4 §1.4, nâng ngưỡng)

| # | Điều kiện | Ngưỡng nghiệm thu | v4 hiện tại |
|---|---|---|---|
| D1 | Tỷ lệ thu nhập hai phía vs v4 (24 seed) | **≥ 1.25×** | — (v4 là đối tượng) |
| D2 | Tỷ lệ thắng hai phía vs v4 | **≥ 90%** | — |
| D3 | Không gãy: trận tệ nhất | **≥ 0.95×** | v4 có 0.80× vs v3 |
| D4 | Mirror / Validation self-play | 10 trận ≥ $30k/bên, không tự hủy T8 | đạt |
| D5 | Phủ meta: melon/random/starter 100%; v2 ≥ 1.34×; crop-baseline ≥ 1.58× | giữ hoặc tốt hơn v4 | đạt |

Cột mốc trung gian: P0 ≥ 1.05× · P2 ≥ 1.10× · P4 ≥ 1.18× · P6 ≥ 1.25× (mỗi pha một bậc, không nhảy cóc).

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
3. **Đối đầu tuần tự trên thang Kaggle** (user nhấn mạnh): mỗi trận gặp 1 archetype khác → cần **bộ nhận diện + bảng chiến thuật theo archetype** (P2), không phải một chiến thuật cố định tinh chỉnh cho clone của chính mình. Đây chính là lý do Bayes 4 lớp là trụ cột v5.

---

## 3. KIỂM KÊ OODA CỦA v4 — TRẢ LỜI TRỰC TIẾP CÂU HỎI CỦA USER

*"Agent đã có cơ chế quan sát, xác định trạng thái hiện tại và đối thủ, dùng thuật toán Bayes tính toán trước tương lai kết quả để tùy biến chiến thuật chưa?"*

| Tầng OODA | Trạng thái trong v4 | Bằng chứng mã nguồn | Đánh giá |
|---|---|---|---|
| **Quan sát (Observe)** | telemetry thị trường từng giờ: `opp_sales = Δinv + drain − my_sales`, chuẩn 100% (5.854/5.854 cell); đọc tiền mặt/đàn/đất đối thủ; giá + shop public | `_tm_step`, `_tm_orders` (v4.py L81–116) | ✅ **ĐẠT** — mắt tốt nhất có thể có |
| **Định vị trạng thái (Orient)** | mô hình thế giới đầy đủ mỗi giờ: tile cây/tuổi/urgency, kho, đàn, tiền, drain tương lai xác định | `_forward_absorb` (L306) — chiếu hậu cống hút | ✅ **ĐẠT** (phía vật lý) |
| **Nhận diện đối thủ (Identify)** | Bayes 2-giả-thuyết: MIRROR vs CONTEST; signature đàn + tỷ lệ tiền; geometric forgetting + hysteresis. 4 archetype khai báo thì **2 chết** (COOP/PASSIVE không bao giờ được gán) | `_bayes_step` (L119–164), `_ARCHES` (L73) | ⚠️ **MỚI 2/5 lớp** — chỉ trả lời "twin hay không", không biết đối thủ mạnh/yếu/hợp tác/dump |
| **Dự đoán tương lai (Predict)** | ❌ **KHÔNG CÓ**. Không có mô hình hành vi đối thủ; `opp_daily` ghi đầy đủ nhưng **không dòng code nào đọc ra quyết định** (grep xác nhận: chỉ ghi L88/L93, không consume); không dự báo đường giá; không mô phỏng kết quả quyết định. Dự đoán duy nhất = drain vật lý (phía cầu), thuộc dạng giải tích chứ không phải Bayes | `opp_day`/`opp_daily` dead-read; `_daily_plan` dùng `opp_counts` tĩnh từ bàn cờ | ❌ **THIẾU CẢ TẦNG** — đây là khoảng trống lớn nhất |
| **Thích ứng chiến thuật (Adapt)** | mode đổi **duy nhất mục tiêu đàn** (MIRROR 6/5/3 vs CONTEST công thức). Ngưỡng bán, quota cây, lao động, mua bán — **không đổi theo mode**; telemetry không vào vòng điều khiển | `_daily_plan` L410–426 | ⚠️ **1/5 núm** — đổi não không đổi tay |

**Kết luận thẳng thắn:** v4 có *mắt* và *vùng vận động*, chưa có *vỏ não dự đoán*. "Bayes tính toán trước tương lai kết quả" hiện chưa tồn tại dưới bất kỳ dạng nào — Bayes hiện tại chỉ trả lời "đây có phải ảnh của tôi không" trước khi quyết định mua mấy con bò. Nguyên vẹn thiết kế 4 lớp cho v5 ở mục 4.

---

## 4. THIẾT KẾ BAYES 4 LỚP — TRỤ CỘT "NÃO DỰ ĐOÁN" CỦA v5

Nguyên tắc chung: **mỗi lớp có công thức tường minh, cập nhật theo đêm (flows là đại lượng theo ngày), chi phí O nhỏ, mọi đầu ra phải được consume bởi quyết định cụ thể** (bài học LA-2/LT-3: tính năng không ra quyết định = xóa).

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

### 4.5 Bảng chiến thuật theo archetype (nơi "tùy biến" thành hiện thực)

| Posterior chiến thắng | Mục tiêu đàn | Thị trường ops | Đặc biệt |
|---|---|---|---|
| MIRROR | chia drain (6/5/3 — giữ luật v4) | ngưỡng chia premium | không phá giá đôi bên |
| STRONG-CONTEST | presence ramp bò sớm 8–10 + kho chứa + drip milk 1.2–1.4× base; wool 2–3 (hợp tác) | pinning ngưỡng; nuốt TOMATO (v4 quota = 0) | FEED make-vs-buy đánh vào burn $35k của đối thủ |
| COOP | giữ share hiện tại | ngưỡng cao, không undercut | duy trì tín hiệu hợp tác qua flow ổn định |
| PASSIVE | max đàn + max quota mọi thị trường trống | bán trọn room | không tốn denial |
| DUMP | giảm exposure mặt hàng bị dump | nâng ngưỡng, chờ drain hút lại | mua wheat rẻ nếu bị dump |

Ghi chú white-box: **ta có toàn bộ mã nguồn v4** — có thể chạy offline v5-ứng-viên vs v4 trên lưới seed, và mô phỏng chính công thức `milk_room −30×opp_COW` của v4 để biết trước phản ứng của nó: **v4 tự rút bò khi v5 ramp bò** (presence valve kế thừa từ v3) → v5 giữ 8–10 bò + stockpile/drip sẽ thu phần 218u premium mà cặp v3/v4 vẫn bỏ hoang (LE-2: ≈ $54–72k/cặp).

---

## 5. KIẾN TRÚC MODULE v5 & ĐIỂM CẮM VÀO MÃ HIỆN CÓ

Nguyên tắc LA-1: **nền v4 + thay đổi đo lường được** — không rebuild. Bảng map module → điểm cắm:

| Module v5 | Chức năng | Cắm vào đâu trong v4.py | Pha |
|---|---|---|---|
| M-1 Perception + | giữ telemetry; thêm kênh tiền/hire đối thủ | `_tm_step` (đã có), `_agent` L1202 | P0 |
| M-2 Bayesian Core (L1+L2) | archetype posterior + flow predictive | thay `_bayes_step` (L119) — giữ giao diện `tm["mode"]`, thêm `tm["posterior"]`, `tm["flow_pred"]` | P2 |
| M-3 Forecast giá (L3) | đường giá 24h | hàm mới gọi từ `_build_orders` (L972) thay ngưỡng tĩnh | P3 |
| M-4 Rollout/DP (L4) | quyết định lớn + thanh lý 26–29 | gọi từ `_daily_plan` (L367) cho 5 quyết định; DP thay nhịp bán d26–29 trong `_build_orders` | P3/P5 |
| M-5 Portfolio Solver | quota động $/action + T/2 + shadow price lao động | thay khối quota cứng L473–505 | P3 |
| M-6 Labor market | Hungarian/auction assignment | thay `_assign_and_act` (L880) — giữ greedy làm fallback | P4 |
| M-7 FEED make-vs-buy | mô hình biên trồng/mua cám | `_daily_plan` (wheat floor đã có 20–24) + logic mua trong `_build_orders` | P1 |
| M-8 Policy table | 5 hàng archetype → bộ tham số | `_daily_plan` đọc `tm["mode"]` như hiện tại nhưng mở rộng núm (đàn + quota + ngưỡng + lao động) | P2 |

---

## 6. CHIẾN LƯỢC THANG ĐẤU KAGGLE — ĐỐI ĐẦU TUẦN TỰ ĐA DẠNG

- **Validation (bắt buộc đi trước):** self-play với bản sao chính mình → L1 posterior MIRROR thắng tự nhiên bởi đối xứng flow; floor chia drain giữ ổn định; gate D4.
- **Thư viện đối thủ chuẩn (ladder coverage):** melon_maxxer, random, starter, v2, crop-baseline, v3, v4, + 3 bot tổng hợp mới (dump-bot, hoarder-bot, wheat-masser) — mỗi cặp 4 seed hai phía = 88 trận/lượt Sweep (~6 phút máy).
- **Sinh hồ sơ likelihood L1:** 10 trận mỗi archetype từ thư viện trên → hồ sơ flow kỳ vọng (bước 4.1).
- **Quản lý 2 submission active:** v4-stable giữ làm bản an toàn; v5-dev nộp thử nghiệm hằng ngày từ khi đạt gate P2 (1.10×). Chỉ "thăng chức" v5 lên primary khi đạt trọn D1–D5.
- **5 submit/ngày = 5 phép thử có kiểm soát:** mỗi lần nộp đi kèm một biến thay đổi duy nhất — tránh burn đột biến rating (Bradley-Terry chỉ đo W/L).

---

## 7. LỘ TRÌNH P0–P6 (mỗi pha: nhiệm vụ → gate nghiệm thu)

**P0 — Nền tri giác + quick wins (ước 1–2 ngày)**
- Nối telemetry vào quyết định dạng tối thiểu: `room` dùng `opp_daily` flows thay `opp_counts` tĩnh (bản L2 giản lược: trung bình trượt 3 ngày, chưa Gamma–Poisson).
- Kênh tiền/hire đối thủ vào `tm` (dự báo lock lao động đối thủ).
- Xóa COOP/PASSIVE chết khỏi `_ARCHES` (tạm 2 lớp, mở lại ở P2 với đủ 5).
- Endgame surge (hire +1–2 ngày 26–28 khi giá trị biên thu hoạch > fib) + nhịp bán dần 26–29; straw urgency window đúng.
- **Gate:** two-sided 24 seed vs v4 ≥ 1.05×; vs v3 không hồi phục dưới 1.05×; mirror 10 trận ≥ $30k/bên.

**P1 — FEED make-vs-buy (mỏ lớn nhất, không cần Bayes)**
- Mô hình chi phí đầy đủ tự trồng 1 wheat (~$25–30: đất + hạt + tưới + lao động) vs giá mua động; kho đệm 2 ngày; mục tiêu cắt 30–40% khoản feedbuy $35k.
- **Gate:** feedbuy giảm ≥ 25% (ledger đo); net solo ≥ +$5k; giữ gate P0.

**P2 — Bayes L1 + L2 đầy đủ + policy table 5 archetype**
- Cài đúng thiết kế 4.1/4.2 + bảng 4.5; sinh hồ sơ offline; 5 núm thích ứng (đàn/quota/ngưỡng/lao động/thanh lý).
- **Gate:** độ chính xác nhận diện archetype (offline, đến ngày 10) ≥ 80%; two-sided vs v4 ≥ 1.10×; coverage ladder không tụt.

**P3 — Portfolio Solver + dự báo giá (L3) + rollout (L4)**
- Quota động theo $/action với ràng buộc T/2 + shadow price; mô phỏng giá 24h vào quyết định bán; rollout 5 quyết định/ngày; DP thanh lý.
- **Gate:** two-sided vs v4 ≥ 1.18×; solo gross ≥ $110k (đối chiếu mục tiêu RESEARCH); biên tệ nhất ≥ 0.90×.

**P4 — Labor market: Hungarian/auction assignment + zoning**
- Ma trận 13×~70; O(n²m) ≈ 10⁴–10⁵ op/step; fallback greedy; zoning cụm đất.
- **Gate:** MOVE lãng phí (đo bằng diag) giảm ≥ 10%; two-sided vs v4 ≥ 1.20×.

**P5 — Đánh bóng: FERT động (bón khi giá FERT < $78 biên), TOMATO own (town ~300/mùa + shop), fert-on-wheat**
- **Gate:** giữ nguyên mọi gate trước + D3 (tệ nhất ≥ 0.95×).

**P6 — Đóng băng & thăng chức**
- AST strip → `submission_v5.py` (pipeline y như quy trình v4); syntax + import check; sweep chuẩn 88 trận cuối; đổi primary submission khi trọn D1–D5.

Thứ tự có thể điều chỉnh: nếu user muốn "não trước tiền sau" — hoán đổi P1 ↔ P2 (cả hai đều đứng sau P0 vì cùng ăn nền telemetry). KAIN khuyến nghị thứ tự trên vì P1 sinh tiền ở MỌI archetype trong khi P2 sinh giá trị chủ yếu ở các trận nhận diện được đối thủ mạnh.

---

## 8. PROTOCOL KIỂM ĐỊNH BẮT BUỘC (áp cho mọi pha)

1. Mọi thay đổi một núm → benchmark two-sided 24 seed (100–123) trước/sau; ghi worklog.
2. Chuẩn 4 lượt sweep mỗi pha: vs v4 · vs v3 · mirror 10 · ladder coverage 88 trận.
3. Theo dõi riêng chỉ số "rủi ro gãy": trận tệ nhất, không chỉ trung bình.
4. Quy tắc dừng: 3 vòng liên tiếp không tăng ≥ 2% tỷ lệ hai phía → chốt phiên bản, chuyển pha.
5. Cấm mọi tối ưu chưa đo (LA-5); cấm tính năng không consume (LA-2).

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

---

## 10. BA QUYẾT ĐỊNH MỞ CHO USER (chốt trước khi khởi động P0)

1. **Thứ tự ưu tiên:** (a) tiền trước — P0→P1→P2 như kế hoạch; hay (b) não trước — hoán đổi P1↔P2 để có hệ Bayes 4 lớp sớm nhất? *(KAIN: a)*
2. **Xác nhận chuẩn "hoàn toàn":** D1–D5 với ngưỡng 1.25×/90%/0.95× — chấp nhận làm định nghĩa chính thức? *(KAIN: có — 100%/2× là đuổi quỷ ma vật lý)*
3. **Thư viện đối thủ:** 3 bot tổng hợp (dump/hoarder/wheat-masser) có cần thêm thủ nào user muốn mô phỏng từ meta Kaggle thật không? *(KAIN: 3 là đủ để khởi động)*

---
*KAIN — hết kế hoạch. File này là hợp đồng triển khai v5; mọi pha P khởi động kèm gate nghiệm thu bằng benchmark, mọi số liệu đối chiếu được với bench/ và worklog.*
