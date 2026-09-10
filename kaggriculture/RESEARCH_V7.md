# RESEARCH_V7 — GIẢI PHẪU KIẾN TRÚC QUYẾT ĐỊNH CỦA v6.6 & NỀN TẢNG LÝ THUYẾT TRÒ CHƠI CHO v7

**Tác giả:** KAIN · **Task 31** · **Đối tượng:** `v6.py` v6.6 (kain16 chassis + E8-lite — nhà vô địch: 93.75% vs v5, 100% vs v4/v3)
**Mục đích:** trả lời 3 câu hỏi của user — (1) v6 ra quyết định thế nào qua bậc thang nhân quả 1 & 2 mỗi turn và tính toán toàn cục mỗi 24 turn; (2) lý thuyết trò chơi áp dụng vào game này ra sao qua các quy luật đã tìm thấy; (3) khai thác chiến thuật nào hiệu quả để đánh vào điểm yếu đối thủ → xác định hướng v7.

---

## 1. KIẾN TRÚC QUYẾT ĐỊNH CỦA v6.6 (code autopsy)

### 1.1 Vòng đời 720 lượt (mỗi turn — `_agent`)

Mỗi turn v6 chạy 5 khối theo thứ tự cố định:

| # | Khối | Việc làm | Tần suất |
|---|---|---|---|
| 1 | `_tm_step` | telemetry: Δinventory mỗi sản phẩm → ước dòng bán/mua của **đối thủ** (trừ đi drain + giao dịch của mình) | mỗi turn |
| 2 | plan cache | `_daily_plan` chỉ tính **một lần lúc hour 0** rồi cache cả ngày — khóa `("plan", day)` | 1 lần/ngày |
| 3 | `_build_tasks` | sinh danh sách tác vụ vật lý (WATER/HARVEST/SERVICE/PLANT/DIG/FERTILIZE/DELIVER/BUILD) kèm tier ưu tiên 0–7 | mỗi turn |
| 4 | `_build_orders` | ≤10 lệnh thị trường: HIRE (fib), BUY_ANIMAL, BUY_SEED, BUY_LAND, BUY_PRODUCT(feed), SELL | mỗi turn |
| 5 | `_assign_and_act` | gán unit→task (tier × khoảng cách, sticky task, feed-preempt), DROP khi túi đầy | mỗi turn |

**Tier ưu tiên vật lý** (bằng chứng R91/R103): T_WATER_CRIT=0 (chỉ cây premium dâu/cà chua) · T_SERVICE_URG=0 (thú đói ≥2 bữa) · T_HARVEST_URG=2 · T_DELIVER=2 · T_BUILD_URG=2 · T_SERVICE=2 · T_WATER_YIELD=3 · T_WATER_MAINT=3 · T_BUILD=4 · T_HARVEST=5 · T_PLANT=5 · T_DIG=5 · T_FERTILIZE=7.

### 1.2 Bậc thang nhân quả 1 — P(B | THẤY A) (dự đoán từ quan sát)

v6 sở hữu **bộ cảm biến white-box rất mạnh** — nó không "học" mà **biết sẵn** cấu trúc:

| Cảm biến | Code | Nó biết gì |
|---|---|---|
| Mô hình giá CHÍNH XÁC | `_price()` | công thức giá engine nguyên văn: `base ± amp·shape(|inv−I0|)` với 9 bộ tham số — v6 không bao giờ bị "ngạc nhiên" về giá |
| Dự báo cầu | `_forward_absorb()` | drain của town: mỗi 4 turn mỗi shop hút vector sản phẩm (shop 1-sản phẩm hút ×2), cuối ngày town center hút 1/sp; unlock shop mới mỗi 3 ngày (dự báo bằng avg shop vector) |
| Đếm cung | `_pipeline()` | cây đứng (bảng YIELD_PER_CYCLE heuristic) + thú (28.0/thú cố định) + tồn shed → tổng nguồn chờ bán của MÌNH và ĐỐI THỦ (tiles công khai!) |
| Telemetry dòng chảy | `_tm_step()` | Δinventory thị trường − drain − giao dịch mình = dòng chảy của đối thủ theo ngày (opp_daily) |
| Nhận dạng archetype | `_bayes_step()` | posterior MIRROR/CONTEST từ chữ ký Gaussian trên (chênh lệch đàn bò-ngỗng-cừu, money ratio) — pm cập nhật dạng `pm^0.8 × like` |

### 1.3 Bậc thang nhân quả 2 — P(B | LÀM A) (dự đoán từ can thiệp)

Đây là chỗ v6 **mô phỏng tác động của chính mình lên thế giới** — toàn bộ nằm trong logic bán + quota:

| Cơ chế | Code | Tư duy nhân quả bậc 2 |
|---|---|---|
| **room()** — trái tim | `def room(it)` | "nếu tôi thêm nguồn `my_pipe` → giá rơi; nếu đối thủ thêm `0.85×opp_pipe` → phần chia của tôi co" — **Cournot accommodation**: v6 chủ động NHƯỢNG kênh khi đối thủ đã đứng pipeline lớn |
| Ngưỡng bán | `_hold(it)` × base + `_sell_count()` | mô phỏng đường cong giá của chính các unit mình sắp đổ: bán đến unit biên có giá ≥ ngưỡng thì dừng (biết dump phá giá mình) |
| Tranche-8 | K16 | "nếu tôi bán 19 sữa một lúc → $265 rơi $210; nếu chia 8/giờ → drain giữa giờ hồi phục giá" — giá trị kỳ vọng của CHỜ (recovery premium, R90) |
| E8-lite endgame | `_pipe_rest` + absorb_rest | d22-27: chỉ giữ hàng khi drain còn đủ hút TOÀN BỘ nguồn chờ (tính cả chu kỳ sống còn của cây/thú) — nếu không thì thanh lý dần vào drain |
| Giá trị tùy chọn đất | BUY_LAND gates | mua quadrant theo cổng vốn (1.3×/1.1× giá) — 25 ô dư = buffer quota (R100) |

**Hệ số 0.85 và hằng số 28.0/thú là heuristic** — v6 không giải đúng Cournot, nó ước lượng. Đây là khe hở cho solver thật (v7).

### 1.4 Tính toán toàn cục mỗi 24 turn — `_daily_plan` (hour 0)

Một lần mỗi ngày v6 tính trọn "kế hoạch nhà nước":

1. **Quota cây** (idol constants): MELON **14** (d0-7 cứng; d8-14 gate `room > −50`); STRAW **30** (d5-13, gate s_room + 2 tầng escalation giá/shop); WHEAT 17 → herd×1.25+3 (cap 24, cắt còn 16 khi dâu đầy); CARROT 12→8/6→4/0 (gate room); TOMATO 0.
2. **Herd targets**: `egg_room // 46` (goose, **cap 6**), `milk_room // 30` (cow cap 10), `wool_room // 28` (sheep cap 8) + shop floors (milk_shops≥2 → +bò; yarn → +cừu) + capital caps d≤10 + **herd cap 15**.
3. **Cơ sở hạ tầng**: reserve coop/pasture theo vốn (`_struct_reserve`).
4. **Đất**: 1 quadrant/ngày theo LAND_ORDER NE($1k)→SW($2k)→SE($4k).
5. **Phân bổ ô**: order `crop_tiles` — WHEAT-first khi feed_demand>300, ngược lại MELON/STRAW-first (R82: order là núm ẩn mạnh nhất).
6. **feed_demand** = (đàn + target) × (29−d).

**Mọi hằng số này là kết quả 500+ game tiến hóa (kain-series)** — chúng là tối ưu LOCAL, không phải tối ưu theo seed/tình huống.

### 1.5 Những gì v6 KHÔNG làm (giới hạn cấu trúc)

1. **Không tính lại giữa ngày** — plan cache 24h: đối thủ dump/greedy giữa ngày không được phản hồi tới tận sáng mai.
2. **Không dự báo hành động tương lai của đối thủ** — telemetry chỉ đo quá khứ; v6 không rollout "đối thủ sẽ bán gì giờ tới" (bậc 2 chỉ 1 chiều: tác động của MÌNH).
3. **Không giải tối ưu** — room()/0.85/28.0 là heuristic; quota là idol.
4. **Không học online** — pm/MIRROR là ngoại lệ (chỉ dùng để tắt straw escalation).

---

## 2. VẬT LÝ ENGINE ĐÃ VERIFY LẦN NÀY (nền cho solver P3)

Đối chiếu trực tiếp `kaggle_environments/envs/kaggriculture/kaggriculture.py`:

| Cơ chế | Sự thật engine | Hàm quả cho solver |
|---|---|---|
| **CARE BANKING** | CARE+FED cộng dồn `pending_care_bonus`; ngày sản xuất: `yield += 1 + bonus` rồi reset bank | **Bò full-care: +3 sữa/2 ngày (vs +1 không care) — 3× năng suất**; ngỗng +2/trày; cừu +4/3 ngày. Đây là "công nghệ" đắt nhất game (R93: race vốn d6-14) |
| Nước non-ongoing | WATER trong cửa sổ `[⌈max_yield_day/2⌉, max_yield_day]`: +1 (+2 nếu fert) lên cap max_yield | Melon: 1 + 5 lần tưới = 6 (cần đúng lịch); wheat 1+3×1=4 (fert mới đủ 6) |
| Sống sót | 2 ngày không tưới → WEED (chết) | phải tưới tối thiểu mỗi 2 ngày — kể cả ngày trồng |
| Ongoing (dâu/cà chua) | +1 mỗi `interval` ngày TỰ ĐỘNG (không cần nước cho base!); cap 4 unit đứng; 4 production-event đời cây | Dâu: 4 event × (+1 base, +2 nếu fert+nước ngày đó) = 4-8 unit/ô/đời |
| Chu kỳ sống | non-ongoing chết `mls=(d+max_yield+1)×24`; dâu sau event 4 → sống tới cuối d+17 | cửa sổ trồng: dâu ≤d15, melon ≤d16 (chín kịp d28), lúa mì ≤d24 |
| Thị trường lockstep | mỗi turn both players' order commit per-unit theo giá hiện hành | bán đến đơn vị biên — đường cầu exact cho mọi kịch bản |
| Drain | shop drain mỗi 4 turn ×6/ngày; town center 1/sp/ngày; shop unlock mỗi 3 ngày (rng seed) | dự báo cầu deterministic theo seed-một-khi-biết-shops |
| Thuê | **hands bị sa thải cuối mỗi ngày** (fib chi phí 1,1,2,3,5/ngày) + vị trí reset về shed | thuê là quyết định NIÊM PHONG hằng ngày, không phải tích lũy |
| Shed | cap 100 TỔNG (vượt = vứt); cuối ngày mọi túi tự đổ về shed | giới hạn tồn kho chờ bán |
| Đất | LAND_ORDER NE→SW→SE, giá 1000/2000/4000, 1 lần/ngày | option value (R100) |

---

## 3. LÝ THUYẾT TRÒ CHƠI ÁP DỤNG — CÁC QUY LUẬT ĐÃ TÌM THẤY DỊNH DẠNG HÓA

### 3.1 Bản chất game: Cournot động 9 kênh trên tồn kho chung

- Giá = hàm **tồn kho thị trường chung** (I0=10.000): cả hai người chơi bán vào CÙNG một bể → mỗi unit bán ra đẩy giá xuống cho cả hai. Đây là **Cournot duopoly với chi phí sunk (hạt/giống/thức ăn) và đường cầu công khai exact**.
- Khác Cournot kinh điển: đường cầu không tĩnh — tồn kho bị **drain deterministic** (town tiêu thụ), làm giá tự hồi phục giữa các đợt bán. Nó là **trò chơi khai thác tài nguyên chung có tái tạo** (common-pool resource game) chạy 720 lượt.
- Tổng phúc lợi dương (town trả cả hai) nhưng **phần chia zero-sum theo thứ tự**: người bán trước ăn đoạn giá cao của đường cong → mọi bài học R83/R90/R99 đều là hệ quả của hình học đường cầu (log/sq → đơn vị đầu đắt gấp 1.5-3× đơn vị cuối).

### 3.2 v6 là một "accommodator" — hệ quả Stackelberg

room() trừ `0.85×opp_pipe` nghĩa là: **khi đối thủ cam kết capacity (đứng cây/thú), v6 tự thu nhỏ quota của mình**. Trong ngôn ngữ game theory, v6 chơi gần với **Stackelberg follower** — nhường phần chia cho leader.

- **Bằng chứng 3 lớp:** R83 (first-mover premium: dưa d11 vs d12 chênh $100/quả); R99 (đòn yield: pipeline dâu-30-từ-d5 làm v5 room() nhượng — kain16 thắng v5 bằng chính đòn này); R105 (vòng phản hồi: pipeline lớn hơn ĐÈ quota nhỏ hơn — already-rich-gets-richer).
- **Vũ khí:** cam kết sớm + công khai (tiles visible) = chiếm kênh. Nhưng lưu ý MIRROR trap (R95): hai accommodator giống hệt nhau → pháo đài đối xứng 52.5% (R97). Chiếm kênh chỉ thắng khi đối thủ KHÔNG phải bản sao mình.

### 3.3 Cấu trúc thông tin: perfect monitoring của hành động, imperfect của tồn kho

- **Công khai:** toàn bộ tiles 2 bên (pipeline đối thủ đo được chính xác), tiền, giá, tồn kho thị trường, shops.
- **Riêng tư:** shed (≤100 unit) + hạt giống. → Đối thủ KHÔNG biết bạn đang ngồi trên bao nhiêu hàng chờ bán — nhưng telemetry (`_tm_step`) suy ra từ Δinventory từng ngày.
- Hệ quả: **khai thác thời điểm (timing) khả thi** — ta dự đoán được khi v6 sắp bán (nhìn giá chạm ngưỡng hold của nó + tồn kho shed của nó đo qua telemetry) → front-run微观 (bán trước 1 giờ).

### 3.4 Đối thủ deterministic → khai thác cấu trúc, không khai thác seed

v6 không có nhiễu nội tại (toàn bộ ngẫu nhiên của game nằm ở shop draws theo seed). Lý thuyết: với đối thủ known fixed strategy, best response tính được bằng mô phỏng trước (per-seed). **Từ chối con đường này** — đó là overfitting, không tổng quát hóa được lên population Kaggle. Khai thác **CẤU TRÚC** (cap cứng, cửa sổ cứng, hệ số heuristic) mới là vũ khí hợp lệ: mọi seam của v6 đều là quy tắc không-best-response ở dạng đóng.

### 3.5 Định luật meta đã chứng minh (giữ nguyên cho v7)

| Định luật | Phát biểu GT | Bằng chứng |
|---|---|---|
| **R94 đàn học đối kháng** | welfare-improving moves của ta có thể nâng thu nhập đối thủ nhiều hơn của ta (hệ số 0.5-1.4×) — chỉ đòn zero-sum thắng | K7: kain +$35k / v5 +$51k |
| **R95/R97 pháo đài mirror** | đối kháng trong cùng kernel-space → đối xứng hóa → parity | K23 15/40; v6.0/v6.1 42/80 |
| **R98/R104 tường delta-noise** | optimum knife-edge: mọi delta quanh nó = nhiễu ± | 8 biến thể/560 game Task 27; 5 hướng/500 game Task 28 |
| **R99/R101 yield & hiến kênh** | nhượng capacity = chuyển phần chia; chỉ cắt khi TÍN HIỆU bão hòa (giá < base) | v6.2 33/40; seed 123 dâu 46u vs 80u |
| **R100 đất = option** | giá trị của buffer quota > chi phí vốn khi kênh chưa bão hòa | land_probe 3 seed |

### 3.6 Ánh xạ GT → hình học cụ thể của game này

1. **Giá trị biên suy giảm mạnh** (log/sq above-func): lợi thế FIRST-MOVER là bậc thang, không phải gradient — bán trước 1 ngày có thể = ăn đoạn 2×.
2. **Drain hồi phục** (6 lần/ngày + town): tồn kho là cái bể rò rỉ đều — "chờ" có giá trị dương khi drain/giờ > tốc mình cần bán (tranche-8 đúng).
3. **9 kênh độc lập + 2 ràng buộc chung** (lao động 24×units, tiền): allocation problem — đây chính là bài toán LP mà solver P3 giải, và là thứ heuristic quota của v6 chỉ ước được.
4. **Cam kết công khai là vũ khí** (pipeline visible) nhưng **bị MIRROR triệt tiêu** (R97) → kernel mới phải khác biệt về cấu trúc quyết định, không chỉ về thông số.

---

## 4. DANH MỤC SEAM V6 (điểm yếu khai thác được, theo code + bằng chứng)

| # | Seam | Cơ chế trong code | Khai thác | Bằng chứng |
|---|---|---|---|---|
| S1 | **Goose hard-cap 6** | `goose_target = max(3, min(6, egg_room // 46))` | EGG-FORTRESS 8-9 ngỗng; v6 không thể counter-scale — công thức của nó còn tự THU NHỎ khi ta đứng nhiều (`−46×opp_geese`) | R102 + probe Task 31: kain30 8 ngỗng vs v6 4 |
| S2 | **Plan cache 24h** | `("plan", day)` tính 1 lần h0 | hành động giữa ngày không được phản hồi tới hôm sau | code + RESEARCH này |
| S3 | **Quota idol seed-mù** | MELON 14 / CARROT binary gate / STRAW gate muộn | graded quota theo giá-bên (_marg) — P3 kernel | kain30 ΔP3 |
| S4 | **Đất trống endgame** | STRAW dừng d13, MELON d14; probe: 53-58 ô trống d20+ | late-straw d14-15, late-melon d15-16 khi giá-bên còn | kain30 S3b/S4 |
| S5 | **Ngưỡng bán tĩnh** | HOLD dict + tranche-8 cố định | bán theo expected recovery (giá trị chờ tính từ drain) — micro-solver | kain30 giữ tranche-8 (v7) |
| S6 | **0.85/28.0 heuristic** | room()/pipeline ước Cournot bằng tay | solver giải đúng đường cầu exact | v7 mục tiêu |
| S7 | **Herd cut order** | v6 cắt NGỖNG trước khi vượt cap 15 | bảo vệ ngỗng, cắt bò trước (fortress giữ nguyên) | kain30 ΔS1 |
| S8 | **Không dự báo đối thủ tương lai** | telemetry chỉ quá khứ | front-run micro-timing (bán trước giờ v6 bán) | v7 (cần telemetry 2 chiều) |

---

## 5. KAIN-30 "SOLVER-1" — KERNEL P3 BẢN 1 (thử nghiệm sống)

Thiết kế (chạy trong battery 100 game seed 100-149, cùng band kain25-29):

- **ΔP3 graded-quota**: `_marg(it, units, anchor)` = giá-biên trung bình của các unit sắp bán (chiếu: inv + pipeline 2 bên − drain tương lai, dùng `_price` exact). MELON 14/10/7 · CARROT 8/6/4/0 · STRAW anti-yield ≥ 0.98 → không hiến kênh (R101/R105).
- **ΔR noon-replan**: plan key `(day, noon)` — tính lại toàn cục lúc h12 (vá S2).
- **S1 egg-fortress**: ngỗng floor 8 / cap 9 khi opp ≤ 7; herd-cap 16, cắt bò trước (vá S1+S7).
- **S4 late windows**: straw d14-15 quota 8; melon d15-16 quota 6 khi giá-bên cho phép (vá S4).
- **Giữ nguyên v6.6**: melon-14 d0-7 (idol K13), tranche-8, feed-gates, E8-lite, hire/land, task tiers, care discipline.

## 5. KAIN-30 → KAIN-31 "SOLVER" — HAI BATTERY 200 GAME: TƯỜNG R104 VỠ

### 5.1 Battery kain30 (100 game, seed 100-149): **29/100 (0.929x, worst 0.613x)**

Autopsy seed 146 (thua cả 2 ghế −16.2/−23.4k) bằng sell_log + care_probe + plan-dump (debug hook ghi plan thật ra file):

| Kênh | kain30 | v6 | Chênh |
|---|---|---|---|
| EGG | 201u = $8.6k | 109u = $4.6k | **+$3.9k (fortress thắng)** |
| FERT | 224u = $13.5k | 181u = $10.6k | +$2.9k |
| WOOL | 55u = $10.1k | 22u = $3.2k | +$7.0k |
| **MILK** | **55u = $17.2k (4 bò)** | **108u = $33.9k (9 bò)** | **−$16.7k** |
| STRAW | 37u = $9.5k | 67u = $17.7k | −$8.2k |
| WHEAT | 630u = $29.1k | 772u = $35.2k | −$6.1k |

**Hai leak cấu trúc (plan-dump xác nhận trực tiếp):**
1. **NOON-REPLAN tự hiến đất**: quota dâu 30 chưa bao giờ bị cắt, nhưng plan h12 trồng wheat 2 lần/ngày (h0 15 + h12 14 tiles) cướp đất dâu → 15 vs 22 tiles đứng.
2. **MILK CONCESSION**: v6 commit 9 bò d8-11 (khi ta băm vốn $2.4k+coops vào ngỗng) → milk_room của ta âm theo công thức accommodate → ta giữ 4 bò. Kênh sữa hút 163 unit mà giá vẫn $312 — **chưa bão hòa**: chia lệch 9/4 là thu nhập bị chuyển giao, không phải khan hiếm.

### 5.2 kain31 = kain30 + 3 fix (ΔA bỏ noon-replan · ΔB milk-commit floor 6 + buy COW trước + mix ngỗng 7/cắt cừu→bò→ngỗng · ΔC FERT hold 0.50)

### 5.3 Battery kain31 (100 game, seed 100-149): **55/100 THẮNG (0.998x, median 1.016)**

- **LẬN ĐỔ 28 seed lên, chỉ 9 xuống** (so kain30). Seed 146 (tệ nhất kain30): lật thành 2/2 thắng $61.4k vs $55.9k. Seed 123 (perfect-storm): 0/2 → 2/2.
- Ghế: 31/50 (s0) + 24/50 (s1). Worst còn lại: 126 s1 (−20.3k), 122 s1, 137, 141, 105 s1 — frontier kế tiếp (care endgame d26-28 + cấu trúc seed).
- **Tường R104 (31-40%) VỠ: 55%** — tường hóa ra là 2 leak tự gây (replan + nhượng sữa), không phải cấu trúc bất khả phá.

## 6. HƯỚNG v7 (khuyến nghị — cập nhật sau battery)

1. **Lý thuyết cam kết (commitment) là trục chính**: đối thủ accommodate (room() trừ pipeline đối thủ) → người COMMIT SỚM kênh sâu giữ phần chia. v7 phải (a) commit milk sớm (floor 6 từ d4), (b) giữ cam kết trọn ngày (không replan xuống), (c) cân bằng pháo đài (ngỗng 7-8 + bò 6 + cừu 4) — all-in một kênh = tự hiến kênh kia.
2. **Kernel P3graded-quota giữ lại**: `_marg` (giá-bên chiếu theo đường cầu exact) cho MELON/CARROT/STRAW anti-yield + FERT hold 0.50 — đóng góp dương chưa isolate (bước kế tiếp: A/B 40 game isolate từng delta).
3. **Micro-sell solver (S5)**: thay tranche-8 bằng so sánh biên giá hôm nay vs E[giá giờ tới] (drain hồi phục − rủi ro đối thủ dump đo bằng telemetry).
4. **Frontier còn lại**: care-collapse d26-28 (9/17 fed — mất nhân suất care banking 3×), 5 seed thua nặng (126/122/137/141/105 s1) — autopsy tiếp.
5. **Tránh**: fork kernel-space (R95), delta quanh optimum KHÔNG có chẩn đoán plan-dump (R98 — autopsy phải chỉ được leak trước khi sửa), per-seed overfit.

---
*KAIN — RESEARCH_V7.md (Task 31). Nguồn: v6.py 1.444 dòng (đọc toàn bộ), engine kaggriculture.py (verify care banking/nước/ chu kỳ), RULES.md v2.4 (105 quy tắc), 500 game Task 28 + probe Task 31.*
