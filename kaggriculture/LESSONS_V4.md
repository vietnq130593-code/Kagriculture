# LESSONS_V4 — ĐÚC KẾT TOÀN BỘ BÀI HỌC TRIỂN KHAI v4 "TWIN PROBE" & ĐỊNH HƯỚNG v5

**Tác giả:** KAIN (kỹ sư AI · kiến trúc sư hệ thống · chuyên gia thuật toán · kinh tế học)
**Đối tượng:** `submission_v4.py` / `v4.py` (1240 dòng bản dev, 1064 dòng bản nộp) — toàn bộ chu kỳ triển khai từ RESEARCH_v4.md v2.0 đến benchmark cuối
**Nguồn dữ liệu:** worklog Task 1–8, `bench/p0_results.json` (10 trận mirror + ledger $0 residual), `RESEARCH_v4.md` v2.0, `RESEARCH_v4_REVIEW.md` (6 lỗi + 8 thiếu), và **đợt kiểm chứng lại mới nhất** (48 trận two-sided seeds 100–123, chạy lại ngày viết tài liệu này)
**Phạm vi:** bài học triển khai · vấn đề gặp phải · đánh giá điểm mạnh/điểm yếu v4 · hướng khắc phục · đề xuất phát triển v5

---

## 0. TÓM TẮT ĐIỀU HÀNH

**Mục tiêu ban đầu của v4:** thắng áp đảo 100% + tỷ lệ ≥ 2× vs `submission_v3.py`.
**Kết quả thực tế đạt được (kiểm chứng lại 48 trận):** v4 thắng 39/48 (81%) hai phía, tỷ lệ trung bình **1.117×** (v4 $51.854 vs v3 $46.397). Phiên worklog ghi 22/24 hạt giống thắng hai phía, 1.114×. Không đạt 100%, không đạt 2× — nhưng v4 **chặn ngược không mất trận nào thảm họa**, an toàn tuyệt đối ở mirror (self-play Validation của Kaggle), và áp đảo mọi đối thủ khác trên trường (melon 9.3–10.8×, v2 1.34–1.36×, crop-baseline 1.58–1.88×).

**Năm bài học lớn nhất của cả chu kỳ:**

1. **"Nền đã chứng minh + edges gia tăng" đánh bại "rebuild từ đầu"** — 3 vòng xây v4 từ đầu đều thất bại (tệ nhất 0/8, $4–8k/trận); vòng 4 lấy nền kinh tế v3 đã tối ưu + cắm 8 edges mới → thắng ngay.
2. **Dead code là kẻ giết thầm lặng** — telemetry + Bayes được viết hoàn chỉnh nhưng *không được nối dây vào vòng quyết định* → agent "mù" mà benchmark vẫn chạy, thua 0/8 không ai báo lỗi.
3. **Stale state là bug class nguy hiểm nhất** — cờ `want_wheat` tính lúc tạo task khiến ngỗng chết đói *ngay cạnh kho đầy lúa mì*. Query trạng thái LIVE tại điểm hành động, không tin cờ cũ.
4. **Hệ thị trường ghép đôi 2 agent: mỗi núm chỉnh toàn cục lật ngẫu nhiên ±6 hạt giống** — đánh giá bắt buộc two-sided multi-seed; một trận một phía không nói lên điều gì.
5. **Trần vật lý là thật:** thị trường dùng chung + lao động ngang nhau → 1.1–1.5× là tối ưu khi đối thủ là bản sao mạnh; 2× chỉ tồn tại khi đối thủ có lỗ hổng cấu trúc (như v2 từng có). "Áp đảo 100%" cần được định nghĩa lại thành: **tỷ lệ trung bình tối đa + không thua thảm + phủ mọi archetype đối thủ**.

**Verdict cho v5:** v4 đã cạn dư địa gia tăng bằng "edges nhỏ". Bước nhảy tiếp theo (1.3–1.6× vs v4) đòi hỏi dựng đúng cái chưa từng dựng: **Portfolio Solver động (thay quota cứng theo ngày) + Labor Ledger thật (Hungarian/zoning) + Bayes đầy đủ posterior 4 archetype**. Chi tiết ở mục 5.

---

## 1. KẾT QUẢ CUỐI CÙNG CỦA v4 — ĐÃ KIỂM CHỨNG LẠI

### 1.1 Đối đầu trực tiếp v4 vs submission_v3.py (48 trận, seeds 100–123)

| Chiều | Thắng | v4 TB | v3 TB | Tỷ lệ | Biên tệ nhất | Biên tốt nhất |
|---|---|---|---|---|---|---|
| v4 đi trước (P0) | **18/24** | $51.837 | $48.064 | 1.078× | 0.80× (seed 113) | 1.45× (seed 122) |
| v4 đi sau (P1) | **21/24** | $51.871 | $44.730 | 1.159× | — | — |
| **Hai phía gộp** | **39/48 = 81%** | **$51.854** | **$46.397** | **1.117×** | | |

Ghi chú quan trọng rút từ chính bảng này:

- **v4 bất biến theo thứ tự đi (±$34 giữa hai chiều), v3 dao động $3.3k** khi đổi vị trí. Sự bất biến này là một ưu điểm thật (thang ngưỡng bán + telemetry thích ứng), dù ban đầu ta tưởng P0 luôn có lợi thế đơn.
- Thua ở P0 tập trung 6 hạt: 100, 102, 104, 108, 112, 113 — tất cả biên hẹp 0.80–0.98×. Không có trận thua "gãy cấu trúc"; toàn knife-edge.
- Đợt kiểm chứng ngẫu nhiên 4 trận (seed mặc định môi trường): 2W/2W — xác nhận knife-edge tồn tại dai dẳng ở biên.
- Phiên worklog ghi 19/24 phía P0, 22/24 hai phía, 2 hòa tuyệt đối (hạt 102, 201, chênh <$200). Chênh lệch 1 trận giữa các lần chạy nằm trong dao động của các trò knife-edge — không có sai lệch hệ thống.

### 1.2 Phủ rộng đối thủ (thang meta thực tế của Kaggle)

| Đối thủ | Kết quả | Ghi chú |
|---|---|---|
| melon_maxxer | **9.3–10.8×** ($52–55k vs $5k) | thị trường premium bị v4 nuốt trọn |
| random / starter | ~$50k vs ~$0–3.5k | |
| v2 "Homestead" (submission.py) | **1.34–1.36×** | đối thủ vật nuôi thế hệ cũ |
| baseline crop-only mạnh | **1.58–1.88×** | đối thủ thuần cây trồng |
| Self-play (Validation Episode) | **$33–55k mỗi bên, ổn định** | MIRROR mode kích hoạt đúng, không tự hủy T8 |

### 1.3 Phân tích khoảng cách mục tiêu — vì sao không 2× và không 100%

1. **Trần vật lý của thị trường dùng chung.** Năng suất lao động hai bên ngang nhau (cùng bộ move/action), cống hút drain cố định theo mặt hàng. Khi hai bên đều mạnh, tổng thu nhập được chia theo vị thế; 1.1–1.5× là vùng tối ưu lý thuyết cho trận "bản sao mạnh vs bản sao mạnh hơn chút". Con số 2× trong RESEARCH_v4.md (dự phóng 1.8–2.3×) giả định đối thủ *không thích ứng* phần lớn các đòn — v3 thực tế tự hạ đàn theo presence (van an toàn công thức milk_room), biến đòn denial thành cuộc đua phần chia chứ không phải tước đoạt.
2. **v3 không còn lỗ hổng cấu trúc lớn.** v2 từng bỏ trống MILK ($242!) — v3 đã chiếm; v4 chỉ còn khai thác *phần v3 chưa làm hết* (TOMATO = 0, STRAW từng hạt, FERT keep-2). Các "thị trường bỏ trống" còn lại đều mỏng hơn dự phóng.
3. **v4 không dựng Portfolio Solver.** Kế hoạch 6 module trong RESEARCH chỉ hiện thực ~2.5 module (World Model telemetry có; Market Ops threshold-ladder có dạng heuristic; Presence/Bayes rút gọn 2-giả-thuyết). Quota cây trồng vẫn là *bảng cứng theo khoảng ngày* — chính lỗi "quota cứng" mà nghiên cứu phê phán ở v3.
4. **Hiệu ứng thứ tự P0/P1 ±$3–8k/trận** tạo knife-edge ở biên: cùng chiến thuật, đổi vị trí đổi kết quả. Không thể 100% trừ khi vượt xa ngưỡng knife-edge (≥1.3× trung bình).

### 1.4 Thành thật về mục tiêu: "thắng áp đảo 100%" cần định nghĩa lại

Đề xuất chuẩn đo lường cho các phiên bản sau (áp dụng luôn cho v5):

- **Dominance = (a) tỷ lệ trung bình hai phía ≥ 1.25×, (b) tỷ lệ thắng ≥ 90%, (c) không trận nào dưới 0.95× (không gãy), (d) mirror an toàn tuyệt đối, (e) phủ 100% melon/random/starter.**
- v4 hiện đạt (c) một phần (có 1 trận 0.80×), (d) (e) đạt; (a) 1.117×, (b) 81%.

---

## 2. BIÊN NIÊN SỬ TRIỂN KHAI v4 — 4 VÒNG LỚN & 2 PHÁT HIỆN THEN CHỐT

### 2.1 Vòng 0 — Xây v4 từ đầu theo thiết kế RESEARCH (thất bại: 1W/3L)

Phiên trước khởi động `v4_prev.py` dựng toàn bộ theo blueprint 6 module. Kết quả: thua v3 1 thắng / 3 thua. Bài học: blueprint lý thuyết đẹp nhưng nền kinh tế vi mô (thứ tự mua hạt/đất, nhịp tưới, độ cao quota an toàn) là **1.000 chi tiết nhỏ đã được v3 xử đúng** — rebuild từ đầu tái phạm lại TẤT CẢ lỗi v1–v3 đã trả giá.

### 2.2 Vòng 1 — Vá dead code → vẫn 0/8

Telemetry `_tm_step`/`_tm_orders` và Bayes `_bayes_step` đã viết hoàn chỉnh từ phiên trước nhưng **không được gọi trong `_agent`** — mode luôn mặc định CONTEST. Nối dây xong: vẫn 0/8. Bài học kép: (a) dead code không tự lên tiếng — cần assertion/đếm log khi tính năng "bật"; (b) sửa đúng 1 lỗi không đủ lật thế trận khi nền yếu.

### 2.3 Vòng 2 — Chống vòng xoáy tử thần → nghèo triền miên $4–8k

Chẩn đoán `ramp_v4.py` phát hiện 3 bệnh: (a) ngỗng chết đói ngày 7–10 khi kho rỗng trên đồng lúa non; (b) không mua ô đất 4; (c) xây 20 chuồng cho 13 con ($2.2k lãng phí). Vá bằng "hire survival mode" (money ≤ 150 → budget = money − 10) + labor_reserve — cứu được khỏi chết, nhưng kẹp agent ở mức nghèo $4–8k hết trận. **Bài học: cơ chế sinh tồn phải có lối thoát** — survival là trạng thái tạm, không phải chính sách vĩnh viễn.

### 2.4 Vòng 3 — Bẫy gà–trứng do chính tay vá overbuild

Vá "chống overbuild" dùng số ngỗng HIỆN TẠI tính coop_want → khi chưa có ngỗng thì coop_want = 0 → không xây chuồng → không bao giờ mua nổi ngỗng. Tương tự spend_cap = money − 900 zero-hóa mọi structure → đàn không ramp. **Bài học: mọi vòng phản hồi dương (đàn → chuồng → đàn) phải khởi động bằng HẠNG MỤC ĐÍCH (target), không bằng hiện trạng.**

### 2.5 Vòng 4 — Bước ngoặt: PIVOT "v3 làm nền + 8 edges"

Từ bỏ tuning v4-from-scratch. Copy v3.py (nền đã chứng minh $50–60k) rồi cắm 8 edges:

1. Bayes 2-giả-thuyết dò mirror (CONTEST/MIRROR, signature chặt σ, geometric forgetting λ = 0.75–0.8, hysteresis 0.70/0.35, cấm MIRROR trước ngày 8)
2. Telemetry dòng chảy đối thủ (`opp_sales = Δinv + drain − my_sales`)
3. Hire survival chống death-spiral (bản tinh chỉnh, có ngưỡng thoát)
4. Live-state SERVICE routing (chống ngỗng chết đói cạnh kho đầy)
5. Crop death-window mở từ 2 giờ → 24 giờ
6. Deficit-aware herd targets (milk/wool/egg room + 0.5×deficit tồn kho)
7. FERT bán sớm keep-2
8. Land-4 ngày 21 + wheat floor 20–24 ô độc lập đàn

### 2.6 Hai phát hiện then chốt lật 5/8 và 9/10 trận thua thành thắng

- **Phát hiện 1 — Cửa sổ chết 2 giờ:** logic cũ chỉ ưu tiên tưới khi `mls − step ≤ 4` (2 giờ trước hạn) → quá hẹp → straw/melon thối trên đồng. Mở rộng ≤24h → **5/8 thua lật thành thắng**.
- **Phát hiện 2 — "Sát thủ ngỗng":** cờ `want_wheat` tính lúc TẠO task SERVICE (kho rỗng giờ đó) → worker đến con vật TAY KHÔNG, đứng PASS cả ngày trong khi lúa mì đổ vào kho SAU đó → ngỗng chết đói ngay lúc kho có đồ ăn. Sửa thành routing theo trạng thái LIVE (đến animal → unfed → không mang lúa → kho có → đi kho PICKUP rồi quay lại FEED) → **9/10 thua lật thành thắng**.

### 2.7 Bảng bug → vá → hệ quả (dạng sổ cái để v5 không tái phạm)

| # | Bug | Triệu chứng | Vá | Hệ quả sau vá |
|---|---|---|---|---|
| B1 | Telemetry/Bayes dead code | thua 0/8, mode im lặng | nối vào `_agent` | nền cho mọi edge sau |
| B2 | Ngỗng chết đói d7–10 | đàn gãy giữa mùa | survival + routing | +đàn sống đến cuối |
| B3 | Không mua land-4 | thiếu đất cuối mùa | land-4 d21 | +đất trồng muộn |
| B4 | Overbuild 20 chuồng/13 con | −$2.2k | struct theo target | tiền về hàng đúng |
| B5 | Survival nghèo vĩnh viễn | $4–8k hết trận | ngưỡng thoát + nền v3 | phục hồi $50k |
| B6 | Chicken-and-egg chuồng | đàn không ramp | target-based want | ramp hoạt động |
| B7 | Death-window 2h | straw/melon thối | ≤24h | 5/8 lật thắng |
| B8 | Stale `want_wheat` | ngỗng chết cạnh kho đầy | live-state routing | 9/10 lật thắng |
| B9 | Wheat quota theo đàn hiện tại | tự giới hạn thức ăn | floor 20–24 ô | nuôi đàn lớn được |

---

## 3. DANH MỤC BÀI HỌC — PHÂN LOẠI THEO GÓC NHÌN

### 3.1 Kiến trúc hệ thống

- **LA-1 · Nền chứng minh + edges gia tăng.** Chi phí cơ hội của rebuild = tái phạm mọi lỗi đã trả giá. Quy tắc: phiên bản mới = bản cũ + tập thay đổi MỖI THAY ĐỔI ĐO LƯỜNG ĐƯỢC. Rebuild từ đầu chỉ hợp lý khi nền có giới hạn cứng về cấu trúc (v4 hiện không có — quota cứng vẫn vá được tại chỗ).
- **LA-2 · Đo độ phủ code quyết định, không chỉ dòng code.** Dead code (B1) tồn tại vì không có kiểm tra "tính năng đang hoạt động". Biện pháp: mọi module quyết định phải để lại vết (log đếm, thay đổi hành vi thấy được trong diag).
- **LA-3 · Hệ ghép đôi: protocol đánh giá là một phần của thiết kế.** Two-sided + ≥24 seed + đặt cố định danh sách seed + ghi lại mọi lần chạy. Một núm toàn cục đổi → coi như lật lại toàn bộ bảng.
- **LA-4 · Trạng thái suy diễn phải tươi.** Nguyên tắc "query at point-of-action": quyết định tại giờ H dùng dữ liệu tại giờ H, không dùng cờ đặt tại giờ H−k.
- **LA-5 · Telemetry-first.** Không tối ưu gì chưa đo. P0 đã chứng minh: đo đúng (ledger residual $0, 5.854/5.854 cell, 8.628/8.628 step drain) thì mọi tranh luận "đốt tiền ở đâu" chấm dứt ngay — FEED $37.3k (59% burn), không phải hire như giả định cũ.

### 3.2 Thuật toán

- **LT-1 · Bayes 2-giả-thuyết hoạt động tốt trong phạm vi hẹp.** Thiết kế đúng đủ 4 thành tố: signature chặt (σ nhỏ → chỉ bắt twin bit-identical), geometric forgetting (quên quá khứ, λ 0.75–0.8), hysteresis hai ngưỡng (0.70 vào / 0.35 ra — chống flip-flop), lockout sớm (cấm MIRROR trước ngày 8 khi tín hiệu chưa đủ). Kết quả: mirror self-play không hủy diệt T8, contest không bị lừa.
- **LT-2 · Nhưng Bayes mới dùng 1/4 công suất.** `_ARCHES` khai báo 4 archetype (CONTEST/MIRROR/COOP/PASSIVE) — chỉ 2 được gán. COOP và PASSIVE là dead code: tốn mã, tạo ảo tưởng "có thích ứng".
- **LT-3 · Telemetry đo nhưng không ra quyết định.** `opp_day` (dòng bán đối thủ theo ngày, chính xác 100%) được ghi đầy đủ nhưng `_daily_plan` vẫn đếm đàn đối thủ từ bàn cờ công khai (`opp_counts`) — kênh thông tin tốt nhất không nối vào vòng điều khiển. Đây là mỏ còn nguyên.
- **LT-4 · "Đừng search thứ đã giải bằng đại số."** Deterministic + mô hình thị trường biết chính xác → analytic control (ngưỡng, greedy biên, ràng buộc) thắng tuyệt đối MCTS/RL/bandit runtime. Các phương pháp đó chỉ có giá trị offline (sweep tham số, paired-seed).
- **LT-5 · Đánh giá dưới nhiễu.** Knife-edge + hiệu ứng thứ tự → trung bình hai phía là thước đo duy nhất công bằng; biên tệ nhất (0.80×) phải được theo dõi riêng như chỉ số "rủi ro gãy".

### 3.3 Kinh tế trò chơi

- **LE-1 · FEED là khoản đốt tiền số 1** ($37.3k/mùa = 59% tổng burn $61.7k; ledger tách khoản cho thấy $35.2k là tiền MUA wheat thị trường để cho ăn) — mọi tối ưu lao động/hire trước đây chỉ quanh $6–10k. Đòn make-vs-buy cám (trồng lúa tự nuôi vs mua) là mỏ lớn nhất chưa khai thác của v5.
- **LE-2 · Trần chia sẻ thị trường là thật và đo được.** Mirror v3-vs-v3: mỗi bên $43.9k/$40.1k; tổng milk hai bên 106u so với drain 324 — **218u premium bỏ hoang ≈ $54–72k/cặp không ai thu**. Không phải vì thị trường đầy — vì cả hai cùng rút theo presence. Ai dám ở lại (với kho chứa + drip) sẽ thu phần đó.
- **LE-3 · Presence warfare đúng lý thuyết, nhưng floor của v3 chặn.** Chỉ bò bị zero được (floor 0); cừu floor 5, ngỗng floor 3–4 → wool là thị trường HỢP TÁC (2–3 cừu), egg là thị trường sâu (scale tự do). v4 đã phản ánh đúng điều này trong targets.
- **LE-4 · Mirror T8 thực nghiệm không tự hủy** — công thức presence của v3 là van an toàn tự hạ đàn (đỉnh 3.8 bò/bên). Bẫy hủy diệt thật chỉ xảy ra nếu hardcode 9–10 bò không detector. Kết luận: mirror-rule vẫn BẮT BUỘC (Kaggle validation là self-play), nhưng dạng "floor chia drain" của v4 là đủ.
- **LE-5 · Hiệu ứng thứ tự P0/P1 là biến chiến lược ±$3–8k** — lớn hơn biên thắng trung bình của v4! Chiều hướng không đơn điệu (P0 bán trước giá tốt hơn; P1 quan sát tồn kho trước khi hành động). v4 bất biến thứ tự là ưu điểm; v3 nhạy thứ tự là điểm yếu của nó.
- **LE-6 · Ngày 29 là 23 giờ vàng không refresh** — v4 chưa có DP thanh lý tận dụng (E8); còn để vali tiền trên sân.

### 3.4 Lập trình / engine — các bug class đặc thù

- Cây mới trồng KHÔNG có ân hạn tưới (trồng xong phải tưới NGAY ngày đó, cu = 1 sẵn).
- Urgency tính bằng "giờ còn lại" phải quy ra window hành động (2h vs 24h là khác biệt sống còn).
- Vòng phản hồi dương (đàn↔chuồng, wheat↔đàn) phải khởi động bằng target, không bằng hiện trạng.
- Kho (shed) là tài nguyên độ trễ: tồn kho tại thời điểm TẠO task ≠ tại thời điểm THỰC HIỆN task.
- PLANT vượt hạt → drop TOÀN BỘ crop đó trong turn (kiểm tổng request trước khi phát lệnh).
- Survival mode phải có điều kiện thoát, nếu không thành bẫy nghèo ổn định.
- Mua đất muộn (d21 cho land-4) đúng; nhưng mua đất trước hạt là bẫy nghèo v1 — thứ tự mua là ràng buộc cứng của bootstrap.

### 3.5 Quy trình & phương pháp luận

- **Trace từng ngày (ramp_v4.py) > tuning mù.** Mỗi vòng chẩn đoán mở ra 3–5 bug thật; mỗi vòng tuning mù lật ±6 seed ngẫu nhiên.
- **Instrument monkeypatch (_commit_unit/_do_hire/...)** cho ledger $0 residual — nền tảng để tranh luận bằng số.
- **Không bao giờ kết luận từ <10 trận một chiều.**
- **Sửa theo chuỗi nhân quả, không theo triệu chứng** (B6 ra đời vì vá B4 theo triệu chứng).
- **Ghi worklog từng vòng** — 50% giá trị của phiên này đến từ việc đọc lại worklog 8 task trước.
- **Đặt mục tiêu đo được và soát lại mục tiêu bằng thực nghiệm** (1.4 ở trên): tránh đuổi chỉ tiêu không tồn tại vật lý (100% + 2× đồng thời trên trận knife-edge).

---

## 4. ĐÁNH GIÁ v4 — ĐIỂM MẠNH / ĐIỂM YẾU

### 4.1 Điểm mạnh (giữ nguyên cho v5)

| # | Điểm mạnh | Bằng chứng |
|---|---|---|
| S1 | Nền kinh tế v3 đã tinh (chọn mặt hàng, nhịp bootstrap, kỷ luật tiền mặt) | $51.854 TB hai phía; không gãy cấu trúc |
| S2 | Mirror-safe bằng Bayes 2-giả-thuyết | self-play $33–55k ổn định, MIRROR kích hoạt đúng |
| S3 | Bất biến thứ tự P0/P1 (±$34) trong khi v3 dao động $3.3k | bảng 1.1 |
| S4 | Live-state SERVICE routing + death-window 24h | 9/10 và 5/8 trận lật thắng |
| S5 | Telemetry chính xác 100% (5.854/5.854) — hạ tầng đã có sẵn | p0_results.json |
| S6 | Wheat floor 20–24 độc lập đàn + land-4 d21 | nuôi đàn lớn không thiếu cám/đất |
| S7 | Thuần stdlib, không import ngoài, 1064 dòng, agent() callable cuối file | an toàn nộp Kaggle |
| S8 | Deficit-aware rooms (thị trường đói + 0.5×deficit) | bám tồn kho thật thay cho absorb tĩnh |

### 4.2 Điểm yếu (cần khắc phục ở v5 — có định lượng)

| # | Điểm yếu | Hệ quả đo được | Gốc rễ |
|---|---|---|---|
| W1 | Biên thắng mỏng: 1.078× phía P0; 6/24 hạt thua; 1 trận 0.80× | chưa vượt ngưỡng knife-edge (~1.3×) | thiếu bước nhấn cấu trúc (W7) |
| W2 | COOP/PASSIVE dead code | 2/4 archetype chỉ khai báo | Bayes rút gọn |
| W3 | Telemetry opp_day KHÔNG nối vào quyết định | kênh thông tin tốt nhất bỏ phí | `_daily_plan` dùng opp_counts tĩnh |
| W4 | Quota cây cứng theo khoảng ngày (melon 14 nếu d8–14; carrot 8/6/4; tomato = 0 vĩnh viễn) | TOMATO bỏ trống 100%; không thích ứng thị trường | Portfolio Solver chưa dựng |
| W5 | MOVE vẫn chiếm tỷ trọng lớn; assignment greedy (tier, dist) | 5–10% MOVE thu hồi được theo phân tích Hungarian | chưa làm |
| W6 | Endgame chưa surge: không thuê người 13+, không DP thanh lý 26–29 | E8 +$3–5k bỏ lại | chưa làm |
| W7 | FERT keep-2 tĩnh, không make-vs-buy theo giá | LE-1: FEED $37.3k burn chưa đụng | chưa làm |
| W8 | STRAW thu hoạch dưới tiềm năng vài hạt | vali nhỏ bỏ lại | urgency/scheduler |
| W9 | 2 hạt hòa tuyệt đối (102/201) | knife-edge chưa phá | W1 |
| W10 | Mã 1240 dòng dev, 8 stateful global — phức tạp gia tăng, khó trải thêm tính năng | vòng lặp debug dài | nợ kỹ thuật của "nền + vá" |

### 4.3 Đối chiếu thiết kế RESEARCH_v4.md vs thực tế v4

| Thành phần thiết kế | Trạng thái | Ghi chú |
|---|---|---|
| Module A — World Model + telemetry | **Có (70%)** | đo chuẩn 100%; thiếu: dùng flows ra quyết định, kênh tiền mặt/hire đối thủ (T3) |
| Module B — Portfolio Solver (flow auction, T/2) | **Không** | thay bằng quota cứng chỉnh tay |
| Module C — Labor Ledger + Zoning | **Không** | giữ greedy v3 + fib budget |
| Module D — Market Ops threshold-ladder | **Có (60%)** | HOLD ngưỡng theo mặt hàng + deficit; thiếu pinning có chủ đích |
| Module E — Presence Warfare | **Có (75%)** | deficit-aware targets; wool hợp tác đúng; milk chưa ramp 8–10 bò sớm |
| Module F — Safety (mirror rule, survival) | **Có (90%)** | Bayes + hysteresis + survival ngưỡng thoát |
| E1 presence milk | **Một phần** | chia premium, chưa chiếm 218u bỏ hoang |
| E7/E9 FERT + fert-on-wheat | **Một phần** | keep-2 tĩnh |
| E8 DP thanh lý 26–29 + ngày 29 | **Không** | |

Tổng: v4 hiện thực khoảng **40–50% bản thiết kế** — và 40–50% đó đã sinh ra toàn bộ biên thắng. Nửa còn lại chính là lộ trình v5.

---

## 5. HƯỚNG KHẮC PHỤC & ĐỀ XUẤT PHÁT TRIỂN v5

### 5.1 Bảy nguyên tắc thiết kế v5 (rút trực tiếp từ bài học)

1. **Nền v4 + thay đổi đo lường được** — mỗi PR-like thay đổi phải kèm benchmark two-sided 24 hạt trước/sau.
2. **Query-at-point-of-action** — cấm mọi cờ stale; quyết định dùng trạng thái tươi.
3. **Đo trước, tối ưu sau** — mở rộng ledger: đếm MOVE lãng phí, FEED mua vs tự trồng, giờ chết của cây.
4. **Không tính năng chết** — archetype nào không ra quyết định thì xóa khỏi khai báo.
5. **Khởi động vòng phản hồi bằng target** (đàn, chuồng, đất, người).
6. **Survival phải có lối thoát** — mọi cơ chế khẩn cấp mang điều kiện hồi phục.
7. **Đánh giá bằng dominance chuẩn 5 điều kiện** (mục 1.4), không đuổi con số không tồn tại vật lý.

### 5.2 Lộ trình P0–P6 cho v5 (xếp theo giá trị/effort)

**P0-v5 · Quick wins (ước 1–2 ngày) — giá trị +$3–8k, rủi ro thấp**
1. **Nối telemetry vào quyết định** (vá W3): `_daily_plan` dùng `opp_day` flows → hiệu chỉnh rooms theo dòng bán THẬT của đối thủ (thay opp_counts tĩnh); kênh tiền mặt + hires_today đối thủ (T3) → dự báo lock lao động đối thủ.
2. **Xóa dead code COOP/PASSIVE** (W2) hoặc kích hoạt COOP thật (khi phát hiện đối thủ chia sẻ drain ổn định qua 3 ngày).
3. **Endgame surge + DP thanh lý ngày 26–29** (W6): thuê thêm 1–2 người cuối mùa khi fib rẻ hơn giá trị thu hoạch; bán tồn theo DP ngưỡng giảm dần đến giờ 22 ngày 29.
4. **Straw urgency + scheduler** (W8) — thu hoạch đúng window, không thối.

**P1-v5 · Portfolio Solver (trái tim của v5) — giá trị kỳ vọng +$5–12k**
- Thay bảng quota cứng bằng greedy biên theo $/action với ràng buộc: labor theo ngày, cash ≥ sàn, đất trống, **quy tắc T/2 cứng** (tổng cung kế hoạch một mặt hàng ≤ T/2 khi có đối thủ cùng mặt hàng), ước lượng giá từ đường giá thị trường + drain kỳ vọng.
- Mở TOMATO (hiện = 0 vĩnh viễn) và điều quota theo room thực thời.
- Shadow price lao động → điều khiển hire/zoning tự động (thay fib budget tay).

**P2-v5 · Labor Ledger thật — giá trị +$3–6k**
- Hungarian/auction assignment (13 unit × ~60–80 task, O(n²m) thuần Python chạy được) thay greedy (tier, dist).
- Zoning: cụm task theo vùng đất, batching nearest-neighbor trong cụm — cắt MOVE 5–15%.

**P3-v5 · Bayes đầy đủ — giá trị bảo vệ +$2–5k và khai thác đối thủ yếu**
- Posterior 4 archetype thật (CONTEST/MIRROR/COOP/PASSIVE) trên 9 chiều `opp_day` + tiền mặt + hires.
- Mỗi archetype gắn chính sách: MIRROR = chia drain; COOP = chia premium + không phá giá; PASSIVE (đối thủ yếu/bỏ thị trường) = nuốt trọn room + tăng đàn; CONTEST = hiện trạng.
- Học prior từ 10 trận offline mỗi archetype (fictitious-play-lite).

**P4-v5 · Make-vs-buy FEED (LE-1) — giá trị +$8–15k (mỏ lớn nhất)**
- Mô hình giá trị biên: mỗi lần FEED tiêu 1 wheat — phần lớn v3 phải MUA wheat thị trường (feedbuy $35.2k/mùa ở ledger). So sánh chi phí đầy đủ tự trồng 1 wheat (đất + hạt + tưới + lao động, ~$25–30) vs giá mua thị trường ($36–40): trồng tới floor 20–24 ô, mua thêm chỉ khi giá thị trường ≤ ngưỡng động; vận hành kho đệm 2 ngày.
- FEED $37.3k burn → mục tiêu cắt 30–40%.

**P5-v5 · Thị trường phụ động (K4/T1) — giá trị +$2–4k**
- FERT bón wheat khi giá FERT < giá trị biên (+2 yield ≈ $78/plant); bán khi cao — quy tắc động.
- TOMATO/STRAW mở theo room; melon cycle chính xác +24% (không +35%).

**P6-v5 · Đóng gói & ladder validation**
- Gate bắt buộc trước khi coi v5 hoàn thành:
  1. Self-play 10 trận: không trận nào dưới $30k, không tự hủy T8.
  2. Two-sided 24 hạt vs v4: dominance đạt (≥1.10× TB hai phía và ≥90% thắng là mục tiêu tối thiểu; ngắm 1.25×).
  3. Two-sided 24 hạt vs v3: giữ ≥ v4 hiện tại.
  4. vs melon/random/starter: giữ 100%.
  5. Biên tệ nhất không dưới 0.95× ở mọi cặp.

### 5.3 Rủi ro v5 & giảm nhẹ

| Rủi ro | Cơ chế | Giảm nhẹ |
|---|---|---|
| R1 Overfit v3/v4 clone | solver tối ưu hóa đúng "đối thủ có mặt" nhưng ladder Kaggle đa dạng | archetype P3 + gate phủ 4 kiểu đối thủ |
| R2 Solver động dao động quota hàng ngày | ping-pong cây trồng (lỗi v1) | sticky + damping (chỉ đổi quota nếu biên >15%) |
| R3 Hungarian chậm/tốn | step budget | ma trận nhỏ 10⁴–10⁵ op — đo trước; fallback greedy |
| R4 Phá nền kinh tế v3 khi refactor lớn | tái phạm vòng 0–3 | từng PR nhỏ + benchmark sau mỗi bước |
| R5 Knife-edge vẫn dao động do seed | v5 vẫn biên mỏng nếu chỉ +$5k | cần vượt mốc tỷ lệ ~1.25× mới "thoát" knife-edge |
| R6 5 submit/ngày — burn thử sai | dual submission: giữ v4 làm submission an toàn, v5 thử nghiệm | luôn có 2 submission active |

---

## 6. KẾT LUẬN & MỞ ĐẠO THẢO LUẬN v5

### 6.1 Ba con đường chiến lược cho v5 (KAIN trình bày để cùng chọn)

- **Con đường A — "Domination nội bộ":** tối ưu tiếp cặp v4-vs-v3/v4 (P0+P1+P4). Đơn giản, đo được, nhưng giá trị trên ladder Kaggle hạn chế vì ladder không đầy clone của ta.
- **Con đường B — "Meta field đa dạng":** dồn sức vào P3 Bayes đầy đủ + bao phủ archetype (nuốt đối thủ yếu, chia với đối thủ mạnh, an toàn mirror). Đây là con đường tối ưu theo EV điểm Bradley-Terry: mỗi trận trên ladder chỉ cần THẮNG, không cần đậm.
- **Con đường C — "Cả hai theo pha":** P0 quick wins + P4 FEED (đòn giá trị lớn nhất, không phụ thuộc đối thủ) trước; sau đó P3 khi đã có hạ tầng telemetry trong vòng quyết định. KAIN khuyến nghị C vì P4 + P1 sinh tiền ở MỌI trận, còn P3 sinh điểm ở các trận gắt.

### 6.2 Khuyến nghị của KAIN (tóm tắt 1 đoạn)

v4 là một thắng lợi về **kiến trúc gia tăng + kỷ luật kiểm định**, không phải về bước nhảy lý thuyết: nó lấy nền v3, cắm 8 edges, đạt 1.117× hai phía với độ an toàn cao (mirror-safe, order-invariant, không gãy). Nửa thiết kế chưa dựng (Portfolio Solver, Labor Ledger, Bayes đầy đủ, make-vs-buy FEED) là nguồn giá trị còn lại ước **+$15–30k/mùa**. v5 nên đi con đường C: trước hết P0 + P4 (tiền ai cũng ăn được), rồi P1 + P3 (điểm trên ladder). Mọi thay đổi theo 7 nguyên tắc mục 5.1, mọi kết luận theo dominance chuẩn 5 điều kiện mục 1.4.

### 6.3 Câu hỏi cần quyết trước khi khởi động v5

1. **Ưu tiên A/B/C nào?** (KAIN khuyến nghị C — nhưng nếu kỳ vọng của bạn là "phải áp đảo v3-clone mọi giá" thì A.)
2. **Ngưỡng dừng:** bao nhiêu vòng lặp benchmark không tiến bộ thì chốt phiên bản? (Đề xuất: 3 vòng liên tiếp không tăng ≥2% tỷ lệ hai phía.)
3. **Chấp nhận rủi ro refactor lớn (W10) không,** hay giữ kiến trúc 1240 dòng và vá tiếp? (Refactor có giải phóng tốc độ phát triển cho P1–P3 nhưng tái tạo rủi ro vòng 0–3.)
4. **Chiến lược submission đôi:** giữ v4 làm submission an toàn + v5 thử nghiệm mỗi ngày từ khi nào? (Đề xuất: ngay từ P1.)
5. **Với 218u milk premium bỏ hoang (LE-2):** v5 có dám "ở lại" milk khi đối thủ rút (kho chứa + drip) — chấp nhận rủi ro đối thủ quay lại dump không?

---
*KAIN — kết thúc đúc kết v4. Tài liệu này là bản đọc chính thức cho mọi quyết định v5; số liệu trong tài liệu đã được kiểm chứng lại 48 trận tại thời điểm viết.*
