# RULES — SỔ CÁI QUY TẮC KAGGRICULTURE (MÔ HÌNH NHÂN QUẢ CẤU TRÚC CỦA GAME)

**Tác giả:** KAIN · **Phiên bản:** 1.0 (biên soạn đầu Phase 5 thảo luận)
**Mục đích:** Bậc-1 (P(B | thấy A) — dự đoán từ quan sát) và bậc-2 (P(B | làm A) — dự đoán từ can thiệp) đều cần tập quy tắc làm mô hình cấu trúc. Tài liệu này là **bảng tham chiếu duy nhất** gom toàn bộ quy tắc ta đã nắm, mỗi quy tắc đánh số R#, phân loại + gắn tầng Bayes nào tiêu thụ nó.
**Nguồn đối chiếu:** `upload/README.md` (vật lý engine) · `LESSONS_V4.md` §3.3–3.4 (kinh tế + bug-class máu) · `PLAN_V5.md` §12–13 (núm v5.2 + bài học v5.3) · `v5.py` v5.3 (mã hóa thật) · `bench/` + `battles/` (bằng chứng).

**Phân loại mỗi quy tắc:**
- **[P] PHYSICS** — cứng, deterministic, đúng 100% mọi trận (engine white-box)
- **[S] STOCHASTIC** — ngẫu nhiên có phân phối biết trước
- **[E] ECONOMIC** — emergent, học từ thực nghiệm (đo được, có thể đổi theo meta)
- **[I] INFERENCE** — quy tắc về *khả năng/giới hạn suy luận* của chính não

**Tầng tiêu thụ:** L1 archetype · L2 flow (Gamma-Poisson) · L3 giá/race · L4 rollout/DP · LABOR · ECON (nền kinh tế). Bậc nhân quả: Q = quan sát (bậc 1) · C = can thiệp (bậc 2) · Q+C = cả hai.

---

## A. THỜI GIAN & LƯỢT — 5 quy tắc nền

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R1 | 720 turn = 30 ngày × 24 giờ; mỗi turn: 1 action farmer + tối đa 10 market order (vượt = drop âm thầm) | P | mọi tầng | Q+C |
| R2 | Thứ tự xử lý 1 turn: validate → farmer 2 bên đồng thời → market queue xen kẽ từng unit → town drain → refresh (ngày/giá/thu nhập/nông trại) | P | L4 | C |
| R3 | Ngày cuối (d29) chỉ có **23 giờ** — không có refresh cuối ngày: tồn kho bán được tới giờ 22 rồi "đóng sổ"; đồ chưa bán = $0 (không tính vào kết quả) | P | L4 DP | C |
| R4 | 1 action/unit/turn là đơn vị lao động duy nhất — mọi chiến lược quy về $/action | P | ECON | C |
| R5 | Hiệu ứng vị trí P0/P1 ±$3–8k/trận (knife-edge, không đơn điệu: P0 bán trước giá tốt, P1 thấy tồn kho trước khi hành động) | E | benchmark protocol | Q |

## B. CÂY TRỒNG — 8 quy tắc lịch trình (xương sống L3/L4)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R6 | Tưới 1 lần/ngày là đủ (lần 2 no-op); **2 ngày liên tiếp không tưới → cỏ dại**; cây mới trồng có `cu=1` sẵn — KHÔNG ân hạn, phải tưới ngay hôm trồng | P | LABOR | C |
| R7 | One-time (wheat/carrot/melon): từ nửa `max_yield_day` (làm tròn lên) trở đi, mỗi ngày tưới trong bonus window +1 unit; bón phân +2/ngày. Caps: wheat 6 (không bón 4), carrot 4 (3), melon 6 (chạm ở ngày 10, window 6–12) | P | ECON | C |
| R8 | Ongoing (tomato/strawberry): sản xuất theo lịch cố định — tomato d8,9,10,11 (×4 lần, mỗi lần base 1); straw d10,12,14,16; bón phân + tưới ĐÚNG hôm đó → yield ×2. **Chỉ có 4 lần sản xuất** rồi decay thành cỏ dại (bất kể đã thu hay chưa) | P | L3/L4 | C |
| R9 | Decay: sau max lifespan yield giảm 1 mỗi 2 turn về 0 → weed. One-time: 1 ngày sau `max_yield_day`; ongoing: 1 ngày sau lần sản xuất thứ 4 | P | L4 | C |
| R10 | Melon: window 6–12 nhưng chạm cap 6 ở ngày 10 (bón phân: ngày 8) — ngày 11–12 bón/tưới vô nghĩa | P | ECON | C |
| R11 | PLANT vượt số hạt hiện có → **drop TOÀN BỘ** crop đó trong turn (2 unit cùng PLANT 1 hạt → cả hai no-op) — phải kiểm tổng request trước khi phát lệnh | P | LABOR | C |
| R12 | Fertilizer: $100, +2 unit/ngày trong 3 ngày kế (one-time crops) — chỉ có tác dụng ngày cây CŨNG được tưới | P | ECON | C |
| R13 | Bảng $/tile/day (đã hiệu chỉnh tưới tối ưu): egg 1.00 > wheat 0.80 > carrot 0.75 > melon 0.55 > milk 0.50 = tomato 0.33 = wool 0.33 > straw 0.24 — thứ tự "năng suất mặt đất" thô | P | ECON | C |

## C. VẬT NUÔI — 7 quy tắc

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R14 | Cho ăn bằng wheat mỗi ngày; **2 ngày liên tiếp bỏ ăn → thú thoát mất vĩnh viễn**. Thú mới đặt `unfed=0` → sống nổi ngày đầu (khác cây: cây không ân hạn, thú có 1 ngày) | P | LABOR | C |
| R15 | Lịch sản xuất: ngỗng mỗi ngày từ d4 (trả vốn d7); bò 2 ngày/lần từ d8; cừu 3 ngày/lần từ d6. `max_held` (egg 4, milk 6, wool 6) = cap tồn TRÊN tile, không thu là mất chỗ | P | L3/L4 | C |
| R16 | CARE: fed + cared trong ngày → `pending_care_bonus` +1; trả TOÀN BỘ vào lần sản xuất kế (nếu hôm đó được feed); hôm sản xuất mà unfed → vẫn ra base 1 nhưng bonus mất + bank reset. Cap gián tiếp qua max_held | P | ECON | C |
| R17 | Mỗi thú sống nhả 1 fertilizer cuối ngày (dù không feed/care), **không tích lũy** — không COLLECT là mất; nguồn FERT "miễn phí" duy nhất | P | ECON | C |
| R18 | Coop cho ngỗng, pasture cho bò/cừu — mỗi structure 1 thú; BUY_ANIMAL về inventory rồi PLACE lên structure đúng loại; DIG không đào được structure có thú | P | LABOR | C |
| R19 | Chi phí nhập: goose $300/cow $400/sheep $500 + $1 build structure + 1 wheat/ngày/con cho đến cuối mùa (đàn 10 con cuối mùa ăn ~$3–5k lúa) — FEED là khoản đốt tiền #1 của v3/v4 ($37.3k/mùa = 59% burn; $35.2k trong đó là MUA wheat) | E | ECON, P2 | C |

## D. LAO ĐỘNG & HIRE — 4 quy tắc

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R20 | HIRE theo fibonacci: 1,1,2,3,5,8,13,21… (n = số lần đã hire hôm nay, reset mỗi ngày) — thợ chỉ sống 1 ngày, hết ngày đổ đồ vào shed rồi biến mất | P | ECON | C |
| R21 | Thợ spawn cạnh shed theo NWSE, chọn ô ít người nhất (ô LOCKED cũng đứng được — spawn d5,4 chính là ô NE chưa mua); di chuyển 1 ô/turn, nhiều unit cùng ô OK | P | LABOR | C |
| R22 | Ô locked đi QUA được nhưng tile-action no-op (trừ PICKUP/DROP/PLACE-into-shed vẫn dùng ô làm điểm đứng) | P | LABOR | C |
| R23 | Sức chứa lao động ngang nhau 2 bên (cùng move set) → chênh lệch "cơ bắp" chỉ đến từ AI phân bổ, không phải vũ khí tự nhiên | P | ECON | Q |

## E. KHO & ĐẤT — 4 quy tắc

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R24 | Shed 100 item (không tính seed); cuối ngày đổ inventory vào shed, **tràn = mất trắng** (không có overflow area — stockpile trên tay KHÔNG qua mặt được cap) | P | ECON | C |
| R25 | Farmer/hands spawn ở shed đầu mỗi ngày — shed là "trung tâm logistics", 4 ô kề nó (mỗi quadrant 1 ô) là vị trí đắc địa | P | LABOR | C |
| R26 | 10×10 = 4 quadrant 5×5; NW mở sẵn, BUY_LAND $1k/$2k/$4k; mỗi cây/thú 1 ô; không giới hạn loại | P | ECON | C |
| R27 | Cỏ dại spawn 0.005/ô trống/đêm (kỳ vọng ~0.6 ô/đêm trên 25 ô trống) → phải DIG trước khi dùng lại; ô có cỏ dại là "đất bị đóng băng" | S | LABOR | C |

## F. THỊ TRƯỜNG GIÁ — 10 quy tắc (TRÁI TIM của bậc-2)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R28 | Mỗi mặt hàng: `I0 = 10,000` units khởi đầu; giá = `base + sign·amp·f(|inv−I0|)`, floor $1, làm tròn $; f ∈ {linear, sq, sqrt, log, log10, hinge}; `amp = target·base/f(T)`; T = công suất 1 field 5×5 / 24 ngày | P | L3 | Q+C |
| R29 | **Bán → inventory tăng → giá trượt theo above-curve; mua + town drain → giảm → below-curve.** Giá một mặt hàng có VÒNG ĐỜI riêng (state) kéo dài cả mùa, không reset theo ngày | P | L3 | Q+C |
| R30 | Bảng hình dạng (rút gọn): wheat sqrt/log (hoảng khi khan, chịu glut: $45/$20/$19); carrot hinge/sqrt ($70/$10/$1); tomato hinge/sqrt ($84/$24/$9); straw sqrt/linear-1.6 ($204/$1/$1); melon log/sq-3.6 ($300/$1/$1); egg hinge/log ($70/$40/$39); milk sqrt/linear-1.6 ($256/$1/$1); wool log/sq-3.2 ($240/$1/$1); FERT linear/linear ($140/$60/$20) | P | L3 | Q+C |
| R31 | **Premium (base > $100: straw/melon/milk/wool) có above_target > 1** → glut khiêm nhưỡng (+T) cũng đâm thẳng sàn $1 — bán premium phải "bundling + timing", không thể dọn ầm ập | P | L3, Market Ops | C |
| R32 | Hinge (carrot/tomato/egg): giá gần base khi nhu cầu thường, chỉ vọt khi demand chạy QUA T (đầu gối) — các mặt này "tránh bị pump" nhưng dễ sụp nếu bán nhiều | P | L3 | Q+C |
| R33 | Đơn vị xử lý XEN KẼ 2 bên từng unit: 2 lệnh SELL X 10 đồng thời → cùng unit đầu nhận giá như nhau, giá trượt dần về sau — ai đứng TRƯỚC trong queue hưởng giá tốt hơn (P0 lợi thế) | P | Market Ops | C |
| R34 | Buy quoted post-buy, sell quoted pre-sell → mua rồi bán ngay net = $0 (không arbitrage tức thời trong 1 turn) | P | Market Ops | C |
| R35 | Floor $1: unit vẫn BÁN ĐƯỢC nhưng không vào inventory (sàn "thấm", hồi phục khi drain hút tiếp) | P | L3 | C |
| R36 | Chỉ WHEAT + FERTILIZER mua được bằng BUY_PRODUCT; mọi sản phẩm (kể cả FERT thu từ thú) bán được bằng SELL | P | P2 | C |
| R37 | **Wheat churn là VŨ KHÍ zero-sum (khám phá v5.3, đảo ngược giả định "mỏ tiết kiệm")**: mua ồ ạt → pump giá wheat → đánh thuế feedbuy $32–41k của đối thủ net-buyer (v4 mua 1077u/mùa) + tự bán wheat self-grown (500u+) đắt hơn. Ngừng mua = tự giải giáp (A/B cô lập: −0.117x/seed). Town drain hấp thụ ~35u/ngày BẤT CHẤP giá → ai bán vào drain ở giá cao hơn thắng | E | P2 Feed Warfare | C |

## G. TOWN DEMAND — 4 quy tắc (động cơ hút của cả hệ thống)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R38 | Shop unlock mỗi 3 ngày (d3, d6, …), bốc **uniform CÓ hoàn lại** từ 8 loại, cap 8 instances — cùng shop có thể ra nhiều lần, mùa có thể "3 bakery không yarn" | S | L1/L3 | Q |
| R39 | Mỗi instance tiêu 1 unit mỗi mặt hàng nó cần, mỗi 4 turn (= 6 unit/ngày); shop đơn-sản phẩm (YARN, PETCAFE) tiêu ×2. Tổng demand tăng đơn điệu cả mùa | P | L1/L3 | Q |
| R40 | Town center tiêu 1 unit MỌI mặt hàng (trừ FERT) mỗi 24 turn = 1 unit/ngày/mặt hàng, FLAT cả mùa — dòng hút "ân needs" không đổi | P | L1/L3 | Q |
| R41 | Bảng demand: Bakery(egg+wheat) · Pizza(milk+tomato+wheat) · Brunch(egg+wheat+straw) · Yarn(wool×2) · IceCream(straw+milk+wheat) · PetCafe(carrot×2) · Smoothie(straw+milk) · FarmersMarket(wheat+carrot+tomato+straw) — shop mix quyết định mặt hàng nào "sống" mùa này | S | L1/L3 | Q |

## H. BẤT ĐỐI XỨNG THÔNG TIN — 3 quy tắc (định nghĩa "thấy được gì" của bậc-1)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R42 | PUBLIC: tiles 2 bên (loại cây/tuổi/trú/weed + trạng thái structure), money 2 bên, vị trí farmer/hands, `hires_today`, quadrant đã mua, market inventory + giá, shop đã unlock | P | L1 | Q |
| R43 | PRIVATE (không thấy của nhau): **shed, seeds, inventories** — không biết đối thủ đang GIỮ bom tồn kho bao nhiêu, chỉ thấy khi nó BÁN ra | P | L1 | Q |
| R44 | Telemetry vàng: `opp_sales = Δinv + town_drain − my_sales` (chính xác 100%, ledger $0 residual, 5.854/5.854 cell) — đối thủ KHÔNG THỂ giấu dòng bán; đây là "mắt" thật của L1/L2 | E | L1/L2 | Q |

## I. NGUỒN NGẪU NHIÊN CỦA GAME — 2 quy tắc (entropy của Bayes)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R45 | Chỉ 2 nguồn nhiễu thật: shop draw (R38) + weed spawn (R27) — còn lại toàn deterministic → game là "hỗn hợp 90% kết định + 10% bài ngẫu nhiên", lý do analytic control thắng RL/bandit (LT-4) | E | kiến trúc | Q+C |
| R46 | Benchmark 2-agent là chaotic byte-level: cùng code, đổi 1 dòng nhỏ → ±0.1–0.2x/seed; một núm chỉnh toàn cục lật ±6 seed — mọi kết luận bắt buộc two-sided ≥ 20 seed | E | protocol | Q |

## J. KINH TẾ EMERGENT — QUY TẮC "MÁU" (học từ 48+ trận v3/v4, 20 trận v5, 4 bản r1–r4)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R47 | Trần vật lý thị trường dùng chung + lao động ngang (R23): 1.1–1.5× là tối ưu khi đối thủ là bản sao mạnh; 2× chỉ tồn tại khi đối thủ có lỗ hổng cấu trúc. "Áp đảo 100%" phải hiểu theo dominance 6 điều kiện D1–D6 | E | mục tiêu | Q |
| R48 | 218u milk premium BỎ HOANG khi cả 2 rút theo presence (mirror) — tổng milk 2 bên 106u vs drain 324: thị trường không đầy, chỉ là cả hai cùng nhượng. Ai dám ở lại (kho chứa + drip bán) thu phần đó | E | P3/E5 | C |
| R49 | Địa hình thị trường theo mặt hàng: WOOL = hợp tác (floor 2–3 cừu, nếu cả 2 vào cùng lúc thì cùng chết); EGG = thị trường sâu (floor 0, scale tự do); MILK = floor ~3.8 bò/bên theo presence v3 | E | ECON | Q+C |
| R50 | Tín hiệu THỊ TRƯỜNG (giá + shop draw + px_pred) đáng tin hơn tín hiệu HÀNH VI đối thủ: parity-chase đuổi đàn theo đối thủ giúp 1 seed giết 3 seed khác (ruộng đầy + thêm thú = quá tải) | E | L1 coupling | Q+C |
| R51 | v4 white-box có 3 lỗ hổng cấu trúc đang khai thác: (a) quota cố định theo ngày (dâu/dưa compete), (b) room reciprocity nhường khi đối thủ có pipeline (animal floor + thứ tự mua đảo), (c) window mua thú đóng sớm d14–16 (late_ext) | E | knobs v5.2 | C |
| R52 | Mọi coupling sớm não→hành vi đều −0.02–0.04x/seed trên benchmark 20 seed — não phải chạy OBSERVER trước (đo + calibration), coupling chỉ bật khi có chứng cứ gate (l2_mae < 1.5, P > 0.75 hai đêm…) | E | kiến trúc | C |
| R53 | Ngày 29 = 23 giờ vàng không refresh (R3): DP thanh lý tồn theo ngưỡng giảm dần tới giờ 22 = E8 +$3–5k chưa ai thu trọn | E | L4 | C |
| R54 | FEED make-vs-buy đúng nghĩa sinh tồn: tự trồng 1 wheat ~$25–30 đầy đủ chi phí vs mua $36–40 thị trường — nhưng MUA vẫn có thể đúng khi mua chính là vũ khí (R37): hai lựa chọn không loại nhau, chọn theo trạng thái đàn đối thủ | E | P2 | C |

## K. BUG-CLASS ENGINE (chi tiết nhỏ đã trả giá — danh sách "1.000 chi tiết")

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R55 | Cây mới KHÔNG ân hạn tưới (cu=1) — trồng lúc nào cũng phải giữ suất tưới hôm đó cho nó | P | LABOR | C |
| R56 | Urgency quy ra "window hành động": 2h vs 24h trước hạn là khác biệt sống còn (5/8 trận lật nhờ mở window 2h → 24h) | E | LABOR | C |
| R57 | Mọi vòng phản hồi dương (đàn↔chuồng, wheat↔đàn) phải khởi động bằng TARGET, không bằng hiện trạng — nếu không rơi vào bẫy gà–trứng (0 coop → 0 ngỗng → 0 coop…) | E | ECON | C |
| R58 | Kho là tài nguyên ĐỘ TRỄ: tồn kho lúc TẠO task ≠ lúc THỰC HIỆN task — mọi quyết định query trạng thái LIVE tại điểm hành động (bài học "ngỗng chết đói cạnh kho đầy") | E | LABOR | C |
| R59 | Buổi sáng hạt đắt ăn sạch tiền → BUY_ANIMAL fail cả mùa: khi thị trường động vật sâu, BUY_ANIMAL phải đứng TRƯỚC BUY_SEED trong queue | E | Market Ops | C |
| R60 | Survival mode phải có điều kiện thoát — nếu không thành "bẫy nghèo ổn định" $4–8k cả mùa | E | ECON | C |

## L. QUY TẮC SUY LUẬN — giới hạn của chính não (cho thảo luận Phase 5)

| # | Quy tắc | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R61 | Flow-mix của v4 KHÁC NHAU theo seed → naive Bayes 9 kênh dễ đọc nhầm CONTEST/COOP/PASSIVE (r1–r4) → cần warmup (d7 + 50u chứng cứ) + hysteresis 2 đêm + kiến trúc 2 tầng (kernel twin tách khỏi flow posterior) | E | L1 | Q |
| R62 | L2 decay-0.8 TRỄ xu hướng ramp (seed 111: mất straw_compete d12 → −$20k dâu) → quantile thuần chưa đủ, cần trend-blend khi detect ramp | E | L2 | Q |
| R63 | Scale của likelihood không nhân chung được: kernel Gaussian ~0.5 × tích Poisson ~1e-10 → posterior sai 0.99 (bug r1) — các kênh heterogeneous phải TÁCH TẦNG, không nhân thẳng | E | L1 | Q |

---

## M. BẢNG MAP: QUY TẮC → TẦNG BAYES → BẬC NHÂN QUẢ

**Bậc-1 (P(B | thấy A)) — chuỗi: R42/R43/R44 (mắt) → R38–R41 (drain tương lai) → R28–R32 (đường giá) → R61–R63 (giới hạn đọc):**

| Thấy A (quan sát) | Quy tắc dùng | Dự đoán B |
|---|---|---|
| Δinv từng bước + shops list | R44, R39, R40 | flow bán đối thủ hôm qua, 9 kênh — đầu vào L1/L2 |
| Flow 9 kênh tích lũy + money ratio | R61 + PROFILES | archetype posterior (CONTEST/COOP/PASSIVE/DUMP) + twin kernel MIRROR |
| Shop unlock thêm YARN | R41, R30 | wool drain +1 instance ×2 → đường giá wool nâng dự báo |
| Đàn đối thủ + lịch thú | R15, R16 | supply egg/milk/wool của đối thủ 3 ngày tới → room còn lại |
| Tiles có cây tuổi T + cu | R6, R8, R9 | cây sắp chết / sắp thu → cung bùng theo lịch |
| Money 2 bên + run-rate EMA | R5, R47 | tier LEAD/TIGHT/BEHIND (L3-Race) |
| **Không thấy** shed đối thủ | R43 | giới hạn cứng: bom tồn kho chỉ lộ khi bán — L1 luôn có mù ~1 ngày |

**Bậc-2 (P(B | làm A)) — chuỗi: R2 (thứ tự engine) → R28–R37 (impact giá) → R6–R19 (lịch sinh trưởng) → R47–R54 (phản ứng kinh tế):**

| Làm A (can thiệp) | Quy tắc dùng | Hậu quả B dự đoán |
|---|---|---|
| Bán X unit mặt hàng M | R29, R30, R33, R35 | giá trượt theo above-curve của M; premium đâm sàn nếu dồn (R31); vị trí queue đổi giá đơn vị đầu (R33) |
| Mua wheat ồ ạt | **R37** | giá wheat leo below-curve → feedbuy đối thủ chịu thuế + self-sold đắt hơn (đã đo −0.117x khi từ bỏ) |
| Trồng crop ngày D | R7, R8, R10, R13 | dòng thu tại D + k theo lịch — quy về $/action |
| Mua thú + PLACE ngày D | R14, R15, R18, R19 | dòng thu theo interval + nghĩa vụ FEED mỗi ngày đến cuối mùa |
| Hire thêm n người | R20, R4 | fib cost: 1,1,2,3,5,8… — quy về $/action so với giá trị thu hồi |
| Giữ tồn trong shed chờ drain | R24, R39, R40 | bán vào drain ổn định nhưng cap 100 + tràn mất trắng |
| Thanh lý ngày 26–29 | R3, R53 | DP ngưỡng giảm dần đến giờ 22 d29 — tồn = $0 |
| Mọi can thiệp lớn | R46, R47, R50, R52 | benchmark 20 seed trước khi tin; đối thủ CŨNG có não → minimax worst-case (L4) |

**Quy tắc bậc-2 quan trọng nhất KHÔNG nằm trong README: đối thủ phản đòn.** Engine mô tả hậu quả vật lý; v4/v5 thêm hậu quả chiến lược (presence warfare R48/R49, feed war R37). L4 rollout phải mô phỏng CẢ 2 — đây là lý đồ tồn tại minimax P25/P75.

---

## N. LỖ HỎNG CÒN THIẾU (gaps — việc Phase 5 cần lấp)

1. **Own-price impact chưa bọc thành mô hình số bán**: có công thức curve (R28–R30) nhưng chưa có hàm `px_after(sell_n)` xấp xỉ vi phân dùng trực tiếp trong DP thanh lý / solver — hiện gọi `room()` heuristic.
2. **Bom tồn kho đối thủ (R43)**: L1 không thấy shed — chưa có "prior ẩn" cho tồn kho đối thủ (dùng pipeline tiles + flow để ước lượng tích tụ). Nguy cơ bị dump bất ngờ.
3. **Độ trễ phản ứng của đối thủ chưa đo**: khi giá đổi, v4 đổi hành vi sau bao lâu? (latency detector cho L4 minimax — hiện chỉ có detector của mình).
4. **Care bonus (R16) chưa quantify $/action** so với WATER/HARVEST thứ hạng ưu tiên thế nào.
5. **Posterior shop draw tương lai chưa dựng**: R38 là uniform with replacement — có thể tính chính xác P(YARN còn ra trong 5 slot cuối) để blend vào px_pred + late_ext.
6. **Weed quỹ đạo (R27) chưa vào DP**: kỳ vọng mất ~0.6 ô/đêm × $action DIG — chi phí vật lý của "đất trống" chưa nằm trong $/action của solver.

## O. KẾT LUẬN

- **Tổng: 63 quy tắc + 6 lỗ hổng**, phân bổ: 31 PHYSICS (đúng 100%), 2 STOCHASTIC (biết phân phối), 16 ECONOMIC (đo được, có bằng chứng benchmark), 3 INFERENCE (giới hạn não), 11 chi tiết bug-class/protocol.
- Điểm mạnh hiện tại: toàn bộ PHYSICS đã nằm trong v5.3 (mã hóa qua lịch crop/thú, drain, curve giá, fib hire); ECONOMIC máu đã nằm trong knobs v5.2 + bài học v5.3 (feed warfare R37 là quy tắc bậc-2 MỚI NHẤT, chỉ AI benchmark A/B mới phát hiện được — đúng phương pháp user mô tả).
- Điểm yếu: quy tắc nằm rải rác → tài liệu này là hợp nhất đầu tiên; 6 lỗ hổng mục N là "tập quy tắc chưa biết đủ" — thứ tự ưu tiên Phase 5 đề xuất: gap 1 (impact giá) và gap 5 (shop posterior) rẻ nhất/lợi nhất, gap 2 (bom tồn kho) cần thiết cho minimax đúng.

---

## P. BẬC 3 — TẦNG META: NGƯỜI VIẾT v5 MỚI LÀ TẦNG HỌC THỰC SỰ (user chốt, thảo luận Phase 5)

**Nguyên lý:** v5 KHÔNG tự học, không tự rút kinh nghiệm, không tự thêm quy tắc. Mọi tri thức của nó là tri thức chúng ta đã nén vào (hằng số, profile, knob, ngưỡng). Kiến trúc nhân quả 3 tầng:

| Tầng | Ai | Làm gì | Tri thức |
|---|---|---|---|
| **Bậc 1** — P(B \| thấy A) | v5 (in-game) | telemetry + L1 archetype + L2 flow | quy tắc ĐÓNG BĂNG (physics R1–R27 + profile + knob) |
| **Bậc 2** — P(B \| làm A) | v5 (in-game) | L3 giá + L4 rollout minimax | cũng dùng quy tắc đóng băng để mô phỏng can thiệp + phản đòn đối thủ |
| **Bậc 3** — phát hiện quy tắc | **CHÚNG TA** (offline) | quan sát Arena → giả thuyết → thí nghiệm → cập nhật RULES.md → encode vào v5 | quy tắc BIẾN ĐỘNG (kinh tế emergent, meta đối thủ) |

**Vòng đời quy tắc (protocol bắt buộc — mọi R# mới của nhóm [E]):**
1. **Quan sát:** trace trận (Arena UI / JSONL / diag / ledger) phát hiện hiện tượng bất thường
2. **Giả thuyết:** phát biểu quy tắc dạng "đối thủ làm A → hệ quả B → ta nên làm C" (bảng best-response theo lý thuyết trò chơi)
3. **Thí nghiệm cô lập:** A/B 20 seed two-sided — đúng 1 biến đổi, giữ mọi thứ khác nguyên trạng
4. **Phán quyết:** thắng ≥ ngưỡng → cấp R# + encode knob/profile vào v5; thua → ghi BÀI HỌC REVERT kèm số liệu (mẫu: R37 đảo ngược P2, r1–r4 coupling âm)
5. **Tài liệu:** RULES.md là điểm về duy nhất — phiên bản v5 nào dùng bộ quy tắc nào phải ghi rõ

**Hệ quả kiến trúc:**
- "Linh hoạt" của v5 = tri thức đã nén sẵn, KHÔNG phải thích ứng online — độ linh hoạt tối đa của nó bằng độ giàu của bảng best-response ta cung cấp
- M-9 Self-Monitor, `l2_mae`, `calib_mae`, diag feed ledger là **CẢM BIẾN cho tầng 3** — v5 không tự sửa nhưng tự BÁO để ta đọc
- Arena UI = bàn thí nghiệm của tầng 3 (xem từng turn 2 bên — nơi quy tắc mới lộ ra)

**Mục tiêu chính thức mới (user chốt phiên này): v5 đánh bại hoàn toàn v4 VÀ v3, tỷ lệ thắng ≥ 95%.**
- Định lượng từ phân phối hiện tại (67.5% @ 1.058x, σ per-game ~0.12 thang log): cần **mean ratio ≈ 1.16–1.22x vs v4** (hoặc 1.16x + σ giảm còn ~0.09 nhờ bớt knife-edge) ≈ **+$5–8k/mùa**
- vs v3: v5/v3 ≈ 1.058 × 1.117 ≈ 1.18x → ~92% ước tính — sát ngưỡng, Phase 5 bổ thêm để vượt an toàn
- Ngân sách Phase 5 khả thi: P3 Solver (+$5–12k) + E8 DP thanh lý (+$3–5k) + feed-war coupling có điều kiện (+$2–5k) > khoản cần bù
- Bảng best-response cần hoàn thiện trong Phase 5 (dạng "đối thủ làm A → ta làm B"): feed pump theo đàn đối thủ · nhượng/sở hữu room theo tín hiệu giá · mirror split drain · passive nuốt room — mỗi ô của bảng phải có số liệu benchmark đứng sau

---

## Q. BIÊN BẢN PHASE 5 (20 Sep) — QUY TẮC ẨN ENGINE + PHÁN QUYẾT A/B

### Q.1 Kiểm định Arena/engine (audit 3 phía: engine ↔ README ↔ v5)

**Verdict: YELLOW — không sai lệch phá hỏng mô phỏng.** Toàn bộ price curve (9 mặt hàng × 45.000 điểm kiểm số học), lịch crop/thú, shop demand, fib hire, drain timing KHỚP TUYỆT ĐỐI. run_battle.py chỉ truyền seed (+ episodeSteps mặc định) — không override nào. Nhưng audit đào được **các quy tắc ẩn không có trong README**:

| # | Quy tắc ẩn | Loại | Tầng | Bậc |
|---|---|---|---|---|
| R64 | Mùa thực sự có **719 lượt chơi được**: ngày 29 chỉ 23 giờ (0–22), KHÔNG có end-of-day refresh cuối ngày 29 — tưới/FEED/CARE ngày 29 = lãng phí thuần; thợ hire d29 chết mang theo inventory; giờ bán cuối = d29 h22; town center vẫn tick d29 h0, shop d29 h20 | P | L4 | C |
| R65 | **Kho đầy chặn mua**: BUY_PRODUCT/BUY_ANIMAL abort khi shed ≥ 100 (tiền giữ nguyên, lệnh rơi); order bị dừng ở unit fail đầu tiên, không retry | P | Market Ops | C |
| R66 | RNG mỗi ngày DÙNG CHUNG weed + shop draw: `random.Random((seed·1_000_003) ^ day)` — weed outcomes và shop unlock CÓ TƯƠNG QUAN deterministic theo seed | P | L1 | Q |
| R67 | SELL rút từ SHED thôi (không từ tay farmer); FEED/FERTILIZE cần wheat/FERT trong tay UNIT đứng cạnh; HARVEST melon trước ngày 10 = no-op im lặng dù yield đã bank; FERTILIZE mở rộng `max(cur, day+2)` không cộng dồn; PLACE-into-shed giữ phần dư trên tay, DROP vứt toàn bộ tràn; HIRE/BUY_LAND nguyên tử chạy trước vòng per-unit theo thứ tự player 0→1; mua seed/animal không chạm market inventory | P | LABOR/Market | C |
| R68 | v5 hằng nội bộ sai 2 chỗ (đã sửa v5.4): `YIELD_PER_CYCLE WHEAT 5` → thực đo parity-watering **3.0** (428u/~140 cycle từ trace); `CYCLE_LEN MELON 13` → 11 | E | ECON | Q |

### Q.2 Phán quyết A/B 20 seed two-sided (protocol §P — mỗi biến thể đúng 1 delta)

| Biến thể | Nội dung | Ratio | Wins | Worst | Phán quyết |
|---|---|---|---|---|---|
| p4a | Sửa hằng số (wheat 3.0, melon 11) | 1.058x | 27/40 | 0.856 | **GIỮ** — đúng đắn, vô hại (đúng baseline từng số) |
| p4b | +E8-lite drain-aware hold d22–27 + p3_lo (minimax) + px_after/rev_stream/pipe_rest + opp_herd/opp_wnet telemetry | **1.060x** | **27/40** | **0.886** | **GIỮ — bản cuối v5.4** (worst +0.030 = lợi robustness thật) |
| p4c | p4b + pump wheat điều kiện (opp net-buyer ≤−10u/ng & đàn ≥10) | 1.060x | 26/40 | 0.886 | **REVERT** — bắn 3/40 game: +1201/−504/−1076 = net −$379 |
| p4e | p4b + TOMATO mở có gate (≤8 tiles) | 1.027x | 23/40 | 0.766 | **REVERT** — mất −0.033x, worst gãy |
| p4f | p4e + PROFILES học từ số liệu | 1.024x | 23/40 | 0.766 | **REVERT khỏi bản cuối** (≈neutral trên nền tomato; profile giữ làm tư liệu Phase sau) |

**Baseline tham chiếu v5.3: 1.058x · 27/40 · median 1.045 · P25 1.005 · worst 0.856.**
**v5.4 chính thức: 1.060x · 27/40 · median 1.047 · P25 1.010 · worst 0.886.**

### Q.3 Quy tắc mới cấp mã số (từ các kết quả trên)

| # | Quy tắc | Loại | Bằng chứng |
|---|---|---|---|
| R69 | **Wheat-flow của v4 là churn hai chiều** (P25 −9u/ng, P75 +11u/ng, mean 0.7 — profiles_learned.json): "v4 net-buyer 1077u" là hiện tượng THEO SEED (seed 42), không phải thuộc tính cố hữu của archetype → mọi ô best-response "đối thủ làm A → ta làm B" phải gate theo đo lường telemetry sống, cấm theo niềm tin trắng | E | profile_collect 20 trận |
| R70 | **Cơ hội phí wheat-feed áp đảo mọi kênh cây nhỏ**: mở TOMATO 32u (kể cả gate thị trường đúng) mất −0.033x vì 8 tile × 12 ngày = 96 tile-ngày đất+lao động ăn mất chỗ của wheat/dâu trong nền kinh tế feed $37k — chỉ Solver $/action TOÀN CỤC (P3 đầy đủ) đủ thông tin mở kênh đúng lúc | E | A/B p4e |
| R71 | **E8 đã gần cạn** (đo trực tiếp): tồn dư cuối trận v5.2 chỉ $250–800 (10 wheat + sót on-hand) — ước tính "+$3–5k" của LESSONS là thời v4; E8-lite drain-aware thu thêm chủ yếu ROBUSTNESS (worst +0.030) chứ không phải mean | E | parse 6 battles + A/B p4b |
| R72 | **Profile L1 viết tay sai một kênh then chốt**: WHEAT CONTEST tay = 25 vs đo thực 0.7 — mu=25 khi x~±10 cho log-likelihood tệ hơn mọi giả thuyết khác → đây là CỘT GỐC lỗi đọc nhầm archetype r1–r4; profile học đã lưu bench/profiles_learned.json (CONTEST/COOP/PASSIVE/DUMP từ v4/v3/baseline/melon) | E | profile_collect |
| R73 | **Một núm "đúng lý thuyết" vẫn phải thắng bằng số**: pump (R37/R54 hợp lý 100% trên giấy) bắn đúng 3/40 lần và net âm — lý thuyết trò chơi cho HƯỚNG, benchmark cho PHÁN QUYẾT | E | A/B p4c |

### Q.4 Kết luận Phase 5 cho mục tiêu 95%

- v5.4 vs v4: **1.060x / 67.5% / worst 0.886** — tiến bộ thật nhưng NHỎ (+0.002x, +0.030 worst). Khoảng cách tới 95% (cần mean ~1.16–1.22x) **không thể đóng bằng núm** — mọi núm dễ đã cạn (7 núm v5.2 + 3 thử nghiệm Phase 5 này: 2 revert, 1 giữ).
- Giá trị Phase 5 thật sự nằm ở **tri thức**: 5 quy tắc ẩn engine (R64–R68), 5 quy tắc kinh tế mới (R69–R73), profile học được, và xác nhận "kho núm đã cạn".
- **Bước nhảy còn lại = P3 Solver $/action + T/2** (thay bảng quota cứng) — đúng như phán đoán ban đầu của PLAN §7. Mọi thử nghiệm Phase 5 đều hội tụ về kết luận này: cấu trúc danh mục (cây/thú/đất theo $/action thời gian thực) là mỏ cuối.

---
*KAIN — RULES.md v1.2 (bổ sung mục Q: biên bản Phase 5 — audit engine + 5 quy tắc ẩn + 5 phán quyết A/B + 5 quy tắc mới R64–R73). Mọi tầng Bayes của v5 tham chiếu đây; quy tắc mới phát hiện phải qua benchmark 20 seed trước khi cấp mã số.*

## R. BIÊN BẢN TASK 21 (20 Sep) — GT-LAND + LỚP LÝ THUYẾT TRÒ CHƠI 2 CẤP (v5.5)

### R.1 Câu hỏi của user → câu trả lời định lượng (36 trận parse + 7 battery A/B)

**Quan sát user: "lượng đất trống tương đương khu đất cuối cùng thậm chí hơn — mua đất có lãng phí? chưa tìm ra chiến lược tối ưu đất + phân bổ tài nguyên?"** → Đo thực (36 trận v5.4 vs v4, d10–28): v5 trống TB **48/100 ô**, v4 trống 52/100. Phân tích quadrant: NW đầy, NE ($1k) gần đầy (30.9 cây/ô-đo), **SW ($2k) chỉ 15.7/25, SE ($4k) chỉ 18.9/25** — hai đất đắt chạy 60–76% trống. Lao động bão hòa 91% slot (PASS 3%, MOVE 60% do NORTH/SOUTH/EAST/WEST) → đất trống = **tài sản chết**: vốn + lao động + cơ hội phí 3 tầng.

### R.2 Đường cong phân bổ đất (mỗi điểm = 40 game two-sided 20 seed)

| Đất (quadrant) | Vốn đất | Ratio vs v4 | Wins | Worst | Phán quyết |
|---|---|---|---|---|---|
| 25 ô (chỉ NW) | $0 | 1.078x | 28/40 | 0.858 | Thiếu không gian cho chuỗi feed + dâu + thú |
| **50 ô (NW+NE)** | **$1k** | **1.158x** | **34/40** | **0.879** | **ĐỈNH — v5.5 chốt** (paired vs baseline +0.102x, t=4.71, p<0.0002, 17/20 seed) |
| 75 ô (+SW) | $3k | 1.112x | 30/40 | 0.831 | SW lãi mỏng, đuôi xấu |
| 100 ô (+SE) | $7k | 1.060x | 27/40 | 0.886 | Baseline v5.4 — lãng phí kép |

Nông trại 50 ô chạy **đầy ~100%** (empty 1–14): wheat 13–20 + dâu 18 + 11 thú (pasture/coop) + melon window sớm; carrot tự loại khỏi mix (cây biên bị cắt đúng logic Cournot). Vốn tiết kiệm $6k nằm trong tiền cuối (tiền = điểm).

### R.3 Quy tắc mới cấp mã số

| # | Quy tắc | Loại | Bằng chứng |
|---|---|---|---|
| R74 | **Đất tối ưu = 50 ô (NW+NE)**: đường cong U ngược 25/50/75/100 = 1.078/1.158/1.112/1.060x. Mua đất chỉ đúng khi ruộng đang đầy (gate owned_empty ≤ 14 của v5.4 đúng tín hiệu) nhưng lấp đầy ruộng mới phụ thuộc LAO ĐỘNG — không thuê thêm thì mua đất = chôn vốn | E | 4 battery 40 game |
| R75 | **Lấp đất trống bằng wheat = tự sát (−0.174x, 0.886x, 4/40)**: tăng cung wheat vi phạm monopoly-restraint R37 — giá pump rơi → thuế feedbuy của v4 giảm + biên churn của mình ép. Đất trống ở trạng thái cân bằng Cournot KHÔNG phải lãng phí hành vi — nó là hành vi tối ưu với tài nguyên đã phí (bài học 2 tầng: phí nằm ở MUA, không ở KHÔNG TRỒNG) | E | A/B vL1 vs baseline, 20/20 seed âm |
| R76 | **Dung lượng theo trạng thái KHÔNG khả thi**: 5 seed "75 ô tốt hơn" (102/104/106/117/119) không tách được khỏi nhóm "50 ô tốt hơn" bằng tín hiệu quan sát được d12 (milk_shop 1–2 vs 1–2, đàn v4@12 3–9 vs 4–6, giá sữa 213–252 vs 195–243 chồng lấn) → chọn tĩnh theo trung bình; benchmark byte-chaotic nuốt mọi gating mịn | E | parse 10 trận tín hiệu |
| R77 | **GT-Cournot 2 cấp (macro/micro)**: macro mỗi 24 lượt (hour 0–1) đọc L2 Gamma-Poisson E/P75 mỗi kênh → dump_sig (P75 ≥ 8u và ≥ 1.5×E → front-run ×0.96 — bán TRƯỚC cú dội vì lãi 1 ngày trước > nắm chờ khi o > drain) / calm_sig + px_pred rising (→ monopoly restraint ×1.04); micro mỗi lượt áp vào ngưỡng `_hold`. Hiệu ứng trung tính-dương (+0.004x, P25 +0.004) — giá trị chính là KIẾN TRÚC 2 bậc nhân quả đúng yêu cầu (mỗi lượt = vòng nhỏ, mỗi 24 lượt = vòng toàn cục) | E | A/B vG vs vL5 |
| R78 | **Best-response đàn kích hoạt quá muộn**: v4 phóng đàn d16–20 (đến 15 con), v5 mua thú window đóng d16–22 → tín hiệu opp_herd ≥ 13 chỉ đến d18–20 khi cap đã chốt; nới cap +3 (vH) = wash (+0.003x vs v4, −0.005x vs v3, 4 seed kich hoạt: +0.08/+0.06/−0.04/−0.02). Muốn đón đầu đàn muộn phải dựa shop draw d6–12 (đã có knobs_animal) — telemetry đàn là tín hiệu TRỄ | E | A/B vH + trace seed 119 |
| R79 | **95% đạt ở cặp v3 (95.0%), cặp v4 dừng 85% (34/40)**: 6 trận thua chia 2 nhóm — 4 knife-edge (gap ≤ 3.3%) + 2 cấu trúc (seed 107: −$3.8k, seed 119: v4 15 thú ăn $24k sữa + $12k len trên thị trường sâu 100 ô). Nhóm cấu trúc = đúng các seed mà 100 ô của v4 thắng 50 ô — đối xứng với R76: không tín hiệu sớm, không có cửa | E | phân tích 6 trận thua |

### R.4 Bảng kết quả chính thức v5.5 (battery 20 seed two-sided, 40 game mỗi cặp)

| Cặp | v5.4 (baseline) | v5.5 | Δ |
|---|---|---|---|
| **vs v4** | 1.060x · 27/40 (67.5%) · median 1.047 · P25 1.010 · worst 0.886 | **1.162x · 34/40 (85%) · median 1.138 · P25 1.096 · worst 0.879** | +0.102x (t=4.71) · +7 wins · P25 +0.086 |
| **vs v3** | 1.161x · 38/40 (95.0%) · worst 0.889 | **1.311x · 38/40 (95.0%) · P25 1.244 · worst 0.974** | +0.150x · worst +0.085 (mọi trận ≥ 0.974) |

Mục tiêu 95%: **ĐẠT vs v3**; vs v4 đạt 85% (từ 67.5%) — phần còn lại là R79 (knife-edge + seed cấu trúc không tín hiệu). Protocol giữ: mỗi thay đổi 1 delta + 20 seed two-sided + revert cái không dứt khoát (vL1/vL3/vH đều revert có tài liệu; vL2/vL5/vG giữ).

---
*KAIN — RULES.md v1.3 (mục R: biên bản Task 21 — GT-LAND đường cong đất 4 điểm, GT-Cournot 2 cấp, R74–R79, v5.5 chính thức 1.162x/85% vs v4 + 1.311x/95% vs v3). Quy tắc mới vẫn qua protocol §P 5 bước trước khi encode.*

## S. BIÊN BẢN TASK 22 (21 Sep) — KAGGLE SUBMISSION v5.5 + BẪY get_last_callable

### S.1 Phát hiện bẫy (bug-class mới, mức "chết chóc")
Khi dựng bản dán Kaggle (cell 4) từ v5.py: battle kiểm chứng cho v5.py $3,000 (đứng yên)
trong khi bản strip chơi đầy đủ $56–66k. Nguyên nhân: `kaggle_environments.agent.
get_last_callable` chọn **callable CUỐI CÙNG của file/cell** làm agent (không phải
theo tên `agent`). v5.5 Task 21 đã append `_gt_s` (trợ giúp diag) SAU `def agent`
→ mọi lần nạp theo file/cell gọi nhầm `_gt_s(obs)` → exception mỗi lượt → PASS
mãii → $3,000. Arena không lộ vì run_battle.py nạp importlib entry="agent" tường minh.

### S.2 R80 (quy tắc mới — bug-class, mức submission-infra)
| # | Quy tắc | Loại | Nguồn |
|---|---|---|---|
| R80 | **`def agent` PHẢI là callable cuối cùng của file/cell Kaggle**: kaggle_environments `get_last_callable` lấy `[-1]` các giá trị callable trong namespace exec — hàm diag/helper đặt sau `agent` sẽ bị gọi thay `agent` và agent đứng yên $3,000. Mọi hàm trợ giúp diag (_arena_diag, _gt_s) phải đặt TRƯỚC `agent`; kiểm bằng `ast.parse` lấy tên hàm cuối. Cũng đúng cho battery two_sided (nạp file-path) — kết quả $3,000 bất thường = dấu hiệu Called nhầm | K | Task 22 debug + core.py agent.py L66 |

### S.3 Sản phẩm Task 22
- `v5.py`: hoán đổi `_gt_s` lên trước `agent` (behavior-neutral với Arena; sửa bẫy cho mọi lần nạp file-path tương lai)
- `cell4_v5.py` (2.085 dòng, 82.236 bytes, md5 277b2fa5c7b2890134d957d44fb98456): bản cell 4 Kaggle chính thức = v5.5 đầy đủ, bỏ comment/docstring/_arena_diag/_gt_s (dead-code trong Kaggle), chỉ `import math`
- Kiểm chứng 3 lớp: py_compile ✓; AST dump bằng v5.py (bỏ 2 hàm diag + docstring) ✓; 6 battle (seed 100–102 × 2 ghế) cell4_v5 vs v4 ĐỒNG TỪNG ĐÔ LA với v5.py vs v4 — 6/6 v5 thắng ($56.3k–$66.6k vs $49.5k–$60.9k, khớp hướng 1.162x) ✓
- Toàn bộ 24 file agent (v2–v5, bench variants) audit last-callable: chỉ v5.py lỗi (đã sửa) — các số liệu battery cũ hợp lệ

---
*KAIN — RULES.md v1.4 (mục S: biên bản Task 22 — bẫy get_last_callable R80, submission cell4_v5.py, kiểm chứng 3 lớp). Quy tắc mới vẫn qua protocol §P 5 bước trước khi encode.*
