# REVIEW CỦA KAIN — KIỂM ĐỊNH RESEARCH_v4.md TRÊN README CHÍNH THỨC

**Reviewer:** KAIN (kiến trúc sư hệ thống · chuyên gia thuật toán · kinh tế học)
**Đối tượng:** `kaggriculture/RESEARCH_v4.md` v1.0 (480 dòng)
**Chuẩn đối chiếu:** `upload/README.md` (bản mô tả chính thức, 373 dòng) + source engine `kaggle_environments 1.32.7`
**Verdict tổng thể: 85% đúng, 6 lỗi thật, 8 thiếu sót (1 nghiêm trọng), 6 điểm cần hiệu chỉnh số. Luận đề 2× vẫn đứng vững nhưng cơ chế milk phải viết lại.**

Ký hiệu: **L** = lỗi sự thật · **T** = thiếu sót · **C** = cân đối/hiệu chỉnh · **K** = khai thác thêm · **X** = bẫy cần tránh

---

## PHẦN A — NHỮNG GÌ NGHIÊN CỨU ĐÃ ĐÚNG (xác nhận bởi README)

| # | Khẳng định của nghiên cứu | Trích dẫn README | Kết |
|---|---|---|---|
| 1 | I0 = 10.000 mọi mặt hàng, công thức giá 2 phía, floor $1, bán $1 không tăng tồn kho | L190, L196 | ✅ |
| 2 | Per-unit lockstep; buy quote sau-mua / sell quote trước-bán → round-trip trung tính | L194, L202 | ✅ |
| 3 | BUY_PRODUCT chỉ WHEAT + FERTILIZER | L200 | ✅ |
| 4 | Bảng cống hút: shop hút mỗi 4 turn (×2 shop đơn sản phẩm), town center 1u/ngày flat, unlock mỗi 3 ngày cap 8 instance bốc có hoàn lại | L169–173 | ✅ |
| 5 | Hire fib reset HÀNG NGÀY (hands biến mất cuối ngày), 12 hire = $376 | L155–157 | ✅ |
| 6 | Wheat 4→6 / Carrot 3→4 chỉ với phân; Melon 6 dù sao (phân chỉ tăng tốc) | L27–28 | ✅ nguyên văn |
| 7 | Tomato/Straw không vĩnh cửu: 4 lần sản xuất rồi decay thành weed | L29 | ✅ |
| 8 | 2 ngày liên tiếp không tưới → weed; 2 ngày không ăn → trốn | L111 | ✅ |
| 9 | CARE banking: bonus chỉ ăn khi ngày sản xuất được FEED; ngược lại bank reset mà không trả | L75–80 | ✅ |
| 10 | Mỗi con vật 1 FERT/ngày, không tích lũy nếu không thu | L70 | ✅ |
| 11 | Shed 100, overflow discard, stockpile trên người không vượt cap (chỉ trì hoãn) | L147 | ✅ |
| 12 | Bảng đường giá / denial cost khớp bảng tham chiếu P(I0±T), P(I0+2T) của README | L232–242 | ✅ (chênh ≤1u do rounding) |
| 13 | Mù thông tin duy nhất của đối thủ = shed riêng tư; còn lại public | L132, L283 | ✅ |
| 14 | Melon không shop nào hút (chỉ town center 30u/mùa) | suy ra trực tiếp từ bảng shop L175–184 | ✅ |
| 15 | Lockstep xử lý đồng giá mỗi vòng unit cho cả 2 người (không có lợi thế P0 trong vòng) | L94, code engine | ✅ |

Nền móng vi mô thị trường của nghiên cứu (mục 3) là **khỏe mạnh** — các bảng đo khớp chuẩn chính thức đến từng đơn vị làm tròn.

---

## PHẦN B — LỖI THẬT (phải sửa trước khi dựng v4)

### L1 — Luật 5 mâu thuẫn nội tại: cây MỚI TRỒNG phải tưới ngay trong ngày
Nghiên cứu viết: *"phải tưới ngay hoặc chậm nhất là ngày hôm sau"*.
README L113: *"A seed planted and left unwatered that same day reaches 2 at the end-of-day refresh and becomes a weed that night, before it grows. **There is no grace period for fresh plantings.**"*
→ Câu "chậm nhất ngày hôm sau" **sai tuyệt đối** với cây mới: hạt trồng ngày D không tủi ngay ngày D thì chết ngay đêm D (cu = 1 sẵn khi tạo + 1 khi refresh = 2). Quy tắc "tưới mỗi 2 ngày" chỉ áp dụng TỪ ngày hôm sau trở đi, sau khi ngày trồng đã được tưới.
**Tác động v4:** task WATER cho cây vừa PLANT phải là tier 0 (cùng mức cứu đói thú), gộp vào cùng turn với quyết định PLANT. Đây chính là dạng "cây chết dây chuyền" mà v1 đã trả giá.

### L2 — Số học mùa: "720 step = 29 ngày × 24 giờ" sai
720 = 30 ngày (ngày 0–29). Sự thật tinh tế hơn (kết hợp README L35 + engine): ngày 29 bị cắt ở giờ 22, và **end-of-day cuối cùng chạy vào cuối ngày 28** → ngày 29 KHÔNG có refresh (không sản xuất mới, không sinh weed, không auto-drop) — là 23 giờ thu hoạch/bán thuần túy. **Deadline thanh lý cuối cùng = giờ 22 ngày 29**, rộng hơn giả định "thanh lý 26–28" của nghiên cứu và của v3.

### L3 — "Cày hết bàn 20×20" (mục 7.1) sai kích thước
Full board = boardSize 10 → **10×10 = 100 ô**, 4 quadrant 5×5 (README L136). Con số này tham gia mọi tính toán mật độ lao động → phải sửa.

### L4 — Công thức Module A chỉ đúng cho 7/9 mặt hàng
`opp_sales = Δinv + drain − my_sales` đúng cho mọi mặt hàng TRỪ WHEAT và FERTILIZER, vì BUY_PRODUCT của đối thủ cũng trừ tồn kho: với 2 mặt hàng này chỉ đo được **net-flow (sells − buys)**, không tách nổi. May thay, net-flow chính là đại lượng cần cho capacity planning (mua của đối thủ làm khan hiếm → có lợi cho giá của mình). Thêm 2 edge case: bán ở floor $1 không tăng tồn kho (đo underestimate khi dump); tồn kho là số nguyên — công thức vẫn chính xác tuyệt đối phần còn lại.

### L5 — Presence warfare khái quát hóa sai cho SHEEP và GOOSE
Đọc lại code v3 (dòng 309–311):
```python
goose_target = max(4 if day <= 9 else 3, min(5, ...))   # FLOOR 3–4
cow_target   = max(0, min(7, int(milk_room // 30)))     # floor 0 — chỉ COW triệt được
sheep_target = max(5, min(6, int(wool_room // 30)))     # FLOOR 5 tuyệt đối
```
→ **Chỉ bò có thể bị "presence" về 0.** Cừu của v3 không bao giờ dưới 5 con; ngỗng không dưới 3–4. Hệ quả nghiêm trọng cho bảng 6.3 và Module E của nghiên cứu:
- Module E viết "7–8 cừu hiện diện từ sớm" = **tự sát kép**: 7–8 cừu v4 + 5 cừu v3 (floor) ≈ 12 con × ~25–35u ≈ 300–420u wool > drain 226 → giá wool $1 cho cả hai. **Wool là thị trường HỢP TÁC, không phải chiến trường**: tối ưu v4 = 2–3 cừu, chia drain với 5 cừu cố hữu của v3, giá giữ $180–220, cả hai cùng sống.
- Ngỗng: vô nghĩa để deny (egg deep-log), nhưng cũng vô hại — scale thoải mái vì thị trường sâu.
- Số bò để zero `cow_target` của v3: cần `30×bò ≥ absorb(day) − 40`. Ngày 5–6 absorb(MILK) ≈ 290 → **8 bò đủ từ ngày 5** (v3 chỉ bắt đầu mua bò ngày 5–16, đúng khung); cần 9–10 nếu muốn zero từ ngày 0–2 (không cần thiết).

### L6 — "+35% sản lượng melon nhờ phân" quá lạc quan
README L27: không phân đạt cap age 10, có phân age 8 → cycle thực ~10.5 → ~8.5 ngày = **+~24%**, không phải "13 → 9.5 = +35%". CYCLE_LEN = 13 của v3 là hằng số quy hoạch có slack, không phải cycle vật lý.

---

## PHẦN C — THIẾU SÓT (bổ sung vào nghiên cứu)

### T1 — Ý định thiết kế của T (README L220): "Định lý kích thước thị trường"
> *"T is the production capacity of a single 5×5 field over a 24-day window at optimal watering, no fertilizer."*

Thị trường được hiệu chỉnh size cho **1 quadrant / 24 ngày** → tổng công suất tối đa một trận = 2 người × 4 quadrant × (29/24) ≈ **9–10× T**. Đây là lời giải thích thống nhất cho mọi hiện tượng mỏng premium mà nghiên cứu mô tả rải rác — nên phát biểu thành **quy tắc thiết kế cứng cho Portfolio Solver: tổng nguồn cung một bên lên kế hoạch cho một mặt hàng không nên vượt ~T/2 khi có đối thủ cạnh tranh cùng mặt hàng** (400 wheat, 100 straw, 122 milk, 105 wool, 300 melon...). Vượt T/2 là tự vượt khỏi vùng giá "được hiệu chỉnh".

### T2 — Cấu trúc ngày 29 (23 giờ vàng thanh lý)
Từ L2: ngày 29 = 23 giờ, không refresh, không auto-drop → E8 (liquidation schedule) nên được nâng giá trị: DP thanh lý chạy đến **giờ 22 ngày 29**, tận dụng thêm ~1 ngày drain so với kế hoạch 26–28 của v3.

### T3 — `money` và `hires_today` là PUBLIC (farms array)
README L291–301. Có thể theo dõi **chính xác từng đồng tiền mặt và số hire của đối thủ mỗi giờ** → dự báo khả năng mua đất/thú của đối thủ, biết khi nào đối thủ cạn tiền hire (labour lock). Module A nên thêm 2 kênh telemetry này — miễn phí, tường minh.

### T4 — Luật PLANT atomicity chưa nằm trong "15 luật"
README L55–58 + interpreter: nếu tổng PLANT request của một crop trong một turn vượt số hạt → **TẤT CẢ** plant của crop đó trong turn bị drop. v4 phải kiểm tổng request trên toàn bộ unit trước khi phát lệnh (v3 đã có kiểm tra seed qua plant_sticky — nghiên cứu nên nêu luật này tường minh vì nó là dạng bug câm lặng).

### T5 — Hire đầu tiên mỗi ngày spawn trên ô LOCKED (5,4)
README L159: spawn theo NWSE + least-occupied → hire #1 luôn ở (5,4) — ô NE khóa — phải đi bộ về đất mở. Mất 1–2 move/ngày cho hire đầu; zoning và phân công task đầu-ngày của hire #1 nên tính chi phí này.

### T6 — Con vật mới đặt có `consecutive_unfed = 0`
README L115: sống sót ngày đầu không cần feed → tối ưu giờ đặt thú cuối ngày (tiết kiệm 1 lần feed), và lịch feed tính từ ngày hôm sau.

### T7 — weedSpawnChance = 0.005/ô trống/ngày
~0.3–0.5 weed/ngày ở 60–100 ô trống — chi phí DIG nhỏ, đều đặn, nên vào bảng $/action (giá trị DIG = giữ đất trống không bị chiếm).

### T8 — ⚠️ THIẾU SÓT NGHIÊM TRỌNG NHẤT: bẫy "hủy diệt tương hỗ" trong mirror
Nếu v4 kế thừa presence-warfare dạng "9–10 bò để zero đàn đối thủ" thì trong **self-play (Validation Episode của Kaggle!)** hai v4 sẽ cùng thấy 9–10 bò của nhau → cùng zero đàn bò của chính mình → **cả hai mất hoàn toàn dòng milk** — cân bằng tồi tệ nhất có thể. Module A bắt buộc phải có **quy tắc mirror**: khi net-flow của đối thủ tương quan ≈ 1 với của mình qua 2–3 ngày (hoặc cấu trúc đối thủ đối xứng hoàn toàn) → chuyển chế độ chia drain, giữ floor đàn tối thiểu theo drain-share. Đây là điều kiện sống còn để submission không tự đào hố ngay vòng validation.

---

## PHẦN D — CÂN ĐỐI (đúng hướng, hiệu chỉnh con số/cơ chế)

### C1 — Kinh tế milk: thiếu cơ chế "stockpile + drip" — đòn thật là RAMP SỚM
Bảng 6.3 của nghiên cứu gợi ý "$60k?" có dấu hỏi — phân tích đầy đủ:
- Ràng buộc bán premium: *tồn kho tại mọi thời điểm ≤ (drain tích lũy − doanh tích lũy) + deficit khởi điểm* → tổng bán được ở ≥ base ≈ deficit (~40–70) + drain (~324) ≈ **~355u/mùa**, bất kể năng lực sản xuất.
- Sản xuất 10 bò ramp từ ngày 5 ≈ 330u — vừa khít. Bộ đệm kho: shed 100 + on-animal max_held 6×10 = 60 → **max_held chính là kho chứa miễn phí** (bò stall khi đầy — sản xuất tự throttle).
- ⇒ milk monopolist thực dụng ≈ 330u × trung bình $180–220 ≈ **$30–50k** (không $60k, cũng không phải chỉ $15k như v3 đang thu).
- **Tại sao v3 chỉ bán 65u × $242?** Vì ramp trễ (các gate tiền/wheat/struct khiến bò được mua ngày 12–16 → mỗi con chỉ kịp ~9–12 sữa) — production-limited, KHÔNG phải market-limited. ⇒ đòn milk của v4 = **ramp sớm (8–10 bò ngày 5–9) + presence (zero đàn v3) + drip-sell ngưỡng 1.2–1.4× base + stockpile**. Presence và ramp là hai nửa bổ trợ, nghiên cứu mới nêu một nửa.

### C2 — Wool chuyển từ "chiến trường" sang "hợp tác" (hệ quả của L5).
### C3 — E1 giữ quy mô +$25–33k nhưng cơ chế viết lại theo C1.
### C4 — Số liệu minor: WOOL denial 15u (bảng ghi 16); STRAW 7u (vài chỗ ghi 8); wheat 5.0–5.2 cycles/mùa (24–26 ngày usable, không 5.8).
### C5 — Phân rã $61.7k burn hiện là ước lượng; trước khi tin giả định "cắt 30–40%", instrument `_do_hire`/`_parse_order`/`BUY_*` để có itemized ledger (đề nghị thêm vào P0).
### C6 — Dải mục tiêu 2× nêu rõ: **1.8–2.3×**, nhạy nhất với (a) v3 pivot sang wheat-mass + egg (counter: wheat squeeze + chiếm tomato/straw), (b) chất lượng labor ledger (zoning) — đúng như nghiên cứu đã xếp nhưng nên gắn trigger đo được.

---

## PHẦN E — KHAI THÁC THÊM (README hé lộ, nghiên cứu chưa nâng cấp)

**K1 — Ramp speed là biến milk quyết định** (C1) — quan trọng hơn presence một chút, và đo được bằng cash-curve.
**K2 — Telemetry tiền mặt + hire của đối thủ (T3)** — kết hợp fib công bố: biết trước ngày đối thủ không đủ tiền hire >8 người → ngày đó tranh mua drain đi trước.
**K3 — Ngày 29 (T2)** — nâng E8 từ +$2–3k lên +$3–5k.
**K4 — Fert bón/bán theo giá động**: bón wheat khi `price(FERT, inv) < giá trị biên (+2 wheat ≈ $78)` — quy tắc động từng ngày, thay vì quota tĩnh (nâng cấp E7).
**K5 — "Quy tắc T/2" (T1)** thành ràng buộc cứng trong Solver — heuristic thiết kế mạnh nhất toàn tài liệu README.

---

## PHẦN F — BẪY CẦN TRÁNH (tổng hợp)

| # | Bẫy | Nguồn |
|---|---|---|
| X1 | Cừu > 3 khi v3 còn floor 5 | L5 |
| X2 | Bò > 10 (vượt drain + kho → dump $1) | C1 |
| X3 | Presence-war bật trong mirror → hủy diệt tương phụ | T8 |
| X4 | Quota cứng theo ngày (lỗi v3 lặp lại) | nghiên cứu mục 5 |
| X5 | Tối ưu margin thay vì W/L trên ladder | mục 10.1 |
| X6 | PLANT vượt hạt → mất cả turn trồng | T4 |
| X7 | Mua đất trước hạt (bẫy nghèo v1) | worklog |
| X8 | Shed overflow trong đợt thu hoạch dồn | README L147 |
| X9 | Đặt cây cuối ngày không kịp tưới | L1 |

---

## PHẦN G — THUẬT TOÁN TỐT NHẤT CHO v4 (xếp theo leverage)

| Hạng | Thuật toán | Dùng ở đâu | Vì sao | Chi phí |
|---|---|---|---|---|
| 1 | **Rolling-horizon replan (MPC kiểu 1-ngày) + greedy biên với shadow price** | Portfolio Solver (thay quota cứng) | Bài toán 9 biến ràng buộc (labor/cash/board/T/2) — greedy theo $/action đạt ~95% tối ưu LP; dual (giá lao động-giờ) điều khiển hiring + zoning | O(9×ràng buộc)/ngày — vô nghĩa |
| 2 | **Hungarian / auction assignment** (Kuhn–Munkres hoặc Bertsekas auction) | Unit↔Task mỗi giờ (13 unit × ~60–80 task) | v3 dùng greedy (tier, dist) — Hungarian tối tiểu tổng khoảng cách, thu hồi 5–10% MOVE; ma trận nhỏ, thuần Python chạy được | O(n²m) ≈ 10⁴–10⁵ op/step ✓ |
| 3 | **Threshold-ladder inventory policy** ((s,S) biến thể, ngưỡng suy ngược từ đường giá) | Market Ops — bán theo drain, chế độ coop/contest/mirror | Bài toán này là control xác định với mô hình đã biết — policy ngưỡng giải gần tối ưu dạng đóng | O(9)/step |
| 4 | **Flow-telemetry + nearest-centroid archetype classifier** (fictitious-play-lite) | Module A — phân loại coop/mirror/contest + phản ứng | 9 chiều net-flow đo chính xác; phân cụm 3–5 prototype là đủ để đổi chính sách đúng lúc | O(9×k)/ngày |
| 5 | **DP thanh lý cuối mùa** (per product, ngày 26–29 × tồn kho) | E8 | Tách được theo mặt hàng, nhỏ, chính xác — thay dump thô của v3 | O(4×100×9) |
| 6 | **Zone layout + nearest-neighbor batching** (không full TSP) | Zoning + routing | Clustering tĩnh theo mùa + NN trong cụm đủ cắt MOVE; TSP/Christofides là overkill | 0 |
| 7 | **Fib-threshold hiring**: hire người k iff `giá trị hành động biên × số action ≥ fib(k−1)` | Labor ledger | Chính là phân tích biên chuẩn — không cần thuật toán hơn | 0 |

**Tự chối (đừng dùng):** MCTS, deep RL, contextual bandit, evolutionary **ở runtime** — trò chơi deterministic, mô hình thị trường biết chính xác, budget compute/lượt chặt (thuần Python, không search được trong 24 giờ game-giờ). Các phương pháp đó chỉ có giá trị **offline** (parameter sweep, paired-seed benchmark — đã có bench/run.py). Nguyên tắc KAIN: *"Đừng search thứ đã giải được bằng đại số."*

---

## PHẦN H — HÀNH ĐỘNG ƯU TIÊN (patch vào RESEARCH_v4.md + kế hoạch v4)

1. **Sửa 6 lỗi L1–L6** (L1 và L5 là critical cho thiết kế).
2. **Bổ 8 thiếu T1–T8** (T8 = điều kiện sống của Validation Episode; T1 = quy tắc T/2 thành ràng buộc Solver).
3. **Viết lại mục 6.3/8.2 milk theo cơ chế stockpile+drip+ramp sớm** (C1); wool chuyển sang hợp tác (C2).
4. **P0 thêm 2 hạng mục instrumentation**: itemized cost ledger (C5) + 10 trận mirror kiểm định T8.
5. Giữ nguyên mọi bảng vi mô mục 3 (đã kiểm định khớp README) và khung 6 module (đúng hướng, bổ mode-switch state machine coop/mirror/contest).

---
*KAIN — kết thúc review. Tài liệu gốc được giữ nguyên làm "bản đọc"; file này là errata chính thức. Kiến nghị: patch errata vào RESEARCH_v4.md trước khi bắt tay P0.*
