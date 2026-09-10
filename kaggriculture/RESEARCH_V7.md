# RESEARCH_V7 — GIẢI PHẪU KIẾN TRÚC QUYẾT ĐỊNH CỦA v6.6 & NỀN TẢNG LÝ THUYẾT TRÒ CHƠI CHO v7

**Tác giả:** KAIN · **Task 31** · **Đối tượng:** `v6.py` v6.6 (kain16 chassis + E8-lite — nhà vô địch: 93.75% vs v5, 100% vs v4/v3)
**Mục đích:** trả lời 3 câu hỏi của user — (1) v6 ra quyết định thế nào qua bậc thang nhân quả 1 & 2 mỗi turn và tính toán toàn cục mỗi 24 turn; (2) lý thuyết trò chơi áp dụng vào game này ra sao qua các quy luật đã tìm thấy; (3) khai thác chiến thuật nào hiệu quả để đánh vào điểm yếu đối thủ → xác định hướng v7.

> **[CẬP NHẬT Task 38]** Phần I (mục 1–6) là nghiên cứu nền từ thời kain31. **Phần II (mục 7–11) là kế hoạch triển khai v7 hiện hành** — dựa trên kain40 93/100 (1.271x) + dữ liệu trích xuất từ 2 replay top-3 Kaggle (upload/107559251 + 107573831). Quyết định v7 đọc từ mục 7.

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
- Hệ quả: **khai thác thời điểm (timing) khả thi** — ta dự đoán được khi v6 sắp bán (nhìn giá chạm ngưỡng hold của nó + tồn kho shed của nó đo qua telemetry) → front-run vi mô (bán trước 1 giờ).

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
*KAIN — RESEARCH_V7.md (Task 31, Phần I). Nguồn: v6.py 1.444 dòng (đọc toàn bộ), engine kaggriculture.py (verify care banking/nước/ chu kỳ), RULES.md v2.4 (105 quy tắc), 500 game Task 28 + probe Task 31.*

---
---

# PHẦN II — KẾ HOẠCH TRIỂN KHAI v7 (Task 38)

**Bối cảnh:** kain40 FULL-PRESSURE đạt 93/100 vs v6.6 (1.271x — kỷ lục) nhưng còn 7 thua và đất trống 14-25% chưa đạt chuẩn 0-15% của user. Mục tiêu v7: **100% thắng v6.6 + tiền cuối $90-110k + đất trống ≤15%** (trừ ngày cuối). Dữ liệu mới: user tải 2 replay top-3 Kaggle (đã trích xuất toàn bộ → `bench/top_replay_analysis.json`).

**4 câu hỏi cần trả lời:** ① kain40 còn thiếu sót gì (trọng tâm đất trống — lấp bằng sản phẩm nào, đẩy hướng nào); ② phương án xây v7 kết hợp RULES.md (bài học trọng tâm + hạ tỷ lệ trống xuống dưới 14-25%); ③ tổng hợp các chiến lược tấn công đang có; ④ replay top-1 có giá trị nghiên cứu không.

---

## 7. KAIN40 THIẾU SÓT GÌ — ĐỐI CHIẾU TRỰC TIẾP VỚI ĐỈNH THẬT

### 7.1 Hai trận, ba đối thủ top-3 (dữ liệu đã verify)

| Trận | Episode | Đối thủ | Kết quả | Ghi chú |
|---|---|---|---|---|
| R1 | 107559251 (seed 1620414037) | SpaTaro vs Unknown Mother-Goose | $93.281 vs **$99.793** | Mother-Goose thắng nhờ fertilizer 406u + egg 228u |
| R2 | 107573831 (seed 896878425) | SpaTaro vs Otter Vibe | $107.329 vs **$109.084** | Cả hai vượt $107k — trận "đỉnh đấu đỉnh" |

Mức tiền này **gấp 1.6-1.9× kain40** (avg $58.0k). Quan trọng hơn số tiền là **cách họ giữ đất**: bảng dưới là empty% theo ngày (trích từ snapshot h23 mỗi ngày, script `bench/top_replay_extract.py`):

| Ngày | SpaTaro R2 | Mother-Goose R1 | Otter Vibe R2 | kain40 (profile battery) |
|---|---|---|---|---|
| d0-6 | 4-16% | 0-50% (mua NE d3) | 0-28% (mua NE d5) | 10-58% valley |
| d9 | 1.3% | 0% | 0% | 14-25% |
| d12-24 | **1.3% không đổi** | 0-6.7% | **0.0% liền 18 ngày** | 19-25% |
| d27 | 34.7% (bắt đầu thanh lý) | 10.7% | 0% | 19-25% |
| d29 | 68% (đã bán sạch) | 70.7% | 58.7% | — |

**Kết luận ① — lấp đầy bãi trống bằng gì:** top-3 KHÔNG dùng tomato/melon làm filler chính. Công thức của họ là **STRAWBERRY TÁI TRỒNG LIÊN TỤC + CARROT MUỘN (d24-27)**:
- **Strawberry là xương sống**: SpaTaro giữ 31-41 ô dâu suốt d12-21, bán 313-413u/trận; Otter Vibe 28 ô, bán 224-313u. Họ **tái trồng dâu sau khi cây cũ hết 4 lần sản xuất** (dâu sống tới d15-17 nếu trồng d5-7 → trồng vòng 2 d14-17) — khác hẳn kain40 (quota 30 chốt d5-13 rồi để dâu chết d17-21, đất bỏ trống).
- **Carrot là filler cuối game**: d24-27 cả 3 đều chuyển 15-29 ô sang carrot (chu kỳ 3 ngày, giá cuối $72) — trồng d24 chín d26-27, kịp thu trước giờ chốt.
- **Wheat vừa là thu nhập vừa là feed**: bán 351-904u, nhưng SpaTaro còn **MUA 449u wheat thị trường** để nuôi bò — giải phóng đất cho dâu. Đây là đảo ngược triết lý "tự trồng feed" của v6-lineage (feed_demand = (đàn+target)×(29-d) ô wheat).
- **Tomato chỉ là gia vị**: Otter Vibe giữ 7-12 ô (bán 78-100u), 2 người kia gần như bỏ. Kênh $155 của ta là thật nhưng dải hẹp — giữ quota 8-10 của kain40 là đúng, không tăng.

### 7.2 Bảng đối chiếu 8 chỉ số — kain40 vs top-3

| Chỉ số | kain40 | SpaTaro | Mother-Goose | Otter Vibe | Chênh lệnh |
|---|---|---|---|---|---|
| Tiền cuối | $58.0k avg | $93-107k | $99.8k | $109.1k | **−35 đến −51k** |
| Empty% d9-27 | 14-25% | 1.3% | 0-10.7% | **0.0%** | **thiếu 8-18 ô luôn đứng** |
| Ô dâu giữa game | 26-34 (chết d17-21) | 31-41 (tái trồng) | 26-34 | 18-28 (tái trồng) | vòng 2 dâu = 0 |
| Fertilizer bán | piggyback sau CARE (thu vớt vẩn) | 123-178u | **406u** | 280u | Mother-Goose ≈ 13-14u/ngày — kỷ luật thu mỗi con mỗi ngày |
| Hires/mùa | budget-driven, sụp valley | 272-279 (**9-10/ngày đều 30/30**) | 293 | 289 | bền bỉ kể cả khi tiền $12-1.2k |
| Bò / ngỗng | 4-6 bò, 0 ngỗng | 7→12 bò, 0 ngỗng | 6 bò + 6 ngỗng | **11 bò + 8 ngỗng + 3 cừu** | đàn lớn hơn 60-100% |
| Mua wheat feed | tự trồng là chính | **449u** | 134u | 244u | đất feed → đất dâu |
| Mua đất NE / SW | d6 / d10 (theo luật user) | d6 / d8 | **d3** / d8 | d5 / d10 | khớp luật user d5-7/d10-12 |
| Thanh lý cuối (d27-29) | E8-lite d22-27 | d27-29 bán sạch | d27-29 bán sạch | d27-29 bán sạch | +$10k/trận từ liquidation |

### 7.3 Sáu thiếu sót trọng tâm của kain40 (theo thứ tự tác động tiền)

1. **DÂU KHÔNG TÁI TRỒNG** (thiếu sót lớn nhất): dâu chết d17-21 → 15-25 ô trống suốt 7-10 ngày cuối khi giá dâu $180-204. Top-3 trồng vòng 2 (bằng chứng: SpaTaro R1 mua 55 hạt dâu với max 41 ô đứng → ≥14 ô trồng lại; bán 413u > 320u = trần 1 đời cây). Ước tính: 25 ô × 4 event × 1-2u × $120-150 = **$12-30k/trận** đang nằm trên đất chết.
2. **FERTILIZER BỎ RƠI (leak thứ tự code)**: kain40 CÓ COLLECT_FERTILIZER nhưng chỉ piggyback sau CARE trên cùng 1 visit — thứ tự `if not cared: CARE` khiến flag `fertilizer_available` hôm trước bị bỏ qua tới hôm sau (R17: fert không tích lũy = mất trắng). Mother-Goose thu 406u (≈ $15-20k) — chênh chặt so với 123-178u của SpaTaro, tức kỷ luật thu mỗi con mỗi ngày. Fix: đảo thứ tự trên mỗi visit (collect trước care) + tác vụ riêng cho thú đã care.
3. **ĐẤT TRỐNG MẠN TÍNH d15-28** (triệu chứng AC.1 tầng 3): quota thiết kế ~50-60 ô + $55k nhàn rỗi; top-3 chứng minh 66-70 ô sản xuất + tiền về 0 là cách chạy đúng — đầu tư lại tức thời (họ còn $12-1200 suốt d0-9!).
4. **ĐÀN QUÁ NHỎ**: kain40 4-6 bò; top-3 chạy 6-12 bò + 6-8 ngỗng + 3-9 cừu. Sữa/trứng bán 228-322u/người. Milk-commit floor 6 (kain31) đúng hướng nhưng bị cap 10 kìm — top vượt 11-12 khi có feed-bought.
5. **LAO ĐỘNG KHÔNG BỀN**: 272-293 hires/mùa = 9-10 hands MỖI ngày kể cả ngày nghèo (họ còn $12-1.200 suốt d0-9 mà vẫn thuê đủ). kain40 thuê budget-driven (`hire_budget = min(money − floor, max(88, money×0.25))`) → sụp trong valley. Lưu ý nghịch lý: top-3 chạy ÍT units hơn (10-11 vs 12-13) mà giữ 0% trống — hiệu suất/act cao hơn (đi bộ ngắn hơn, không act thừa). R127 giải bằng bền + hiệu quả, không phải thêm heads.
6. **THANH LÝ CUỐI MÙA KHÔNG TUYỆT ĐỐI**: d29 tồn kho = $0 (R3). Top-3 d27-29 thu HOÀN TOÀN + bán sạch (empty% vọt 58-70% là dấu hiệu đã liquidate đúng). kain40 còn tồn 5-15u trên ô + shed.

**Lưu ý meta:** top-3 đấu với nhau (đối thủ cũng restraint, không dump) nên giá cao hơn môi trường kain40-vs-v6 (v6 dump melon + hút wheat 150-240u/ngày). Các con số $90-110k KHÔNG chuyển nguyên sang trận gặp v6 — nhưng cơ chế lấp đầy (dâu vòng 2, fert, đàn, liquidation) là cấu trúc, chuyển được. Phán xét cuối cùng bằng battery của ta.

---

## 8. PHƯƠNG ÁN XÂY DỰNG v7 — 6 TRỤ CỘT (thứ tự ưu tiên theo tiền)

**Nguyên tắc 2 bước quy kết (giữ nguyên):** Bước 1 = tối ưu nguồn lực/lấp đầy (trụ 1-5) — chỉ khi đã lấp tối ưu mà vẫn thua kinh tế mới quy kết bước 2 (chiến lược tấn công). Không trộn 2 bước trong 1 vòng thử.

### Trụ 1 — STRAW-CONTINUOUS (vòng 2 dâu) — dự kiến +$12-15k
- Khi dâu sống hiện có giảm (cây vòng 1 vào event 3-4) + giá dâu biên ≥ $150 → trồng tiếp hạt dâu ngay trên ô trống (floor vốn R122 chỉ buộc khi chưa đủ 3 quadrant; từ d14 thường đã có NE+SW).
- **Số học cửa sổ (trọng yếu)**: dâu trồng dX → 4 event rơi dX+10, +12, +14, +16. Vòng 2 trồng **d11-13** = đủ cả 4 event trước d29; d14-15 = 3 event (d24-29) — chấp nhận; d16-17 = 2 event (d26/27-29) — chỉ khi giá bên ≥ $150 và không có carrot tốt hơn; ≥ d18 cấm (event đầu đã vượt d28).
- Điều tiết theo room()/anti-yield (R101): nếu đối thủ đứng dâu lớn → cap 22-26 ô, phần còn lại cho carrot.

### Trụ 2 — FERTILIZER DISCIPLINE — dự kiến +$8-15k
- **Fix thứ tự (0 chi phí)**: trên mỗi visit thú, collect fert TRƯỚC khi CARE (code hiện tại return CARE trước khiến flag hôm trước bỏ quên); thêm tác vụ riêng T_COLLECT (tier 2) cho thú đã care hôm đó nhưng còn `fertilizer_available`.
- Mục tiêu thu: mỗi thú sống 1u/ngày — đàn 13-16 con = 13-16u/ngày = đúng nhịp Mother-Goose 406u/mùa.
- Bán theo tranche-8 như kênh khác; giá fert base $100, sập nhanh khi tồn (linear 0.4) — đừng để >30u tồn shed.

### Trụ 3 — LABOR SUSTAIN + HIỆU SUẤT — giải trần R127
- HIRE mỗi sáng lên 9-10 hands (fib tổng $54-87/ngày) — **kể cả ngày nghèo** (top-3 giữ đủ 9-10 khi tiền $12-1.2k), chỉ nhường khi tiền < $90 sau floor seed R121/R122 — vá đúng chỗ sụp valley của hire-budget hiện tại.
- Đồng thời tăng hiệu suất/act (top-3 làm được 0% trống với ÍT units hơn): giảm act thừa (tưới lại no-op, đi vòng), route ngắn (trồng quanh shed trước), đứng ngay tile khi chờ. Thước đo: acts có ích/ngày ≥ 75 (hiện 52-67, 71% là đi bộ).

### Trụ 4 — FEED-BUY ĐẢO NGƯỢC — giải phóng đất feed
- Khi giá wheat mua ≤ $30 và đàn ≥ 8: thay vì trồng `feed_demand` ô wheat → MUA wheat (giống top-3: 244-449u/mùa), rút nhanh quota wheat xuống 8-12 ô, dồn đất cho dâu vòng 2 + carrot.
- Điều kiện vệ sinh R113: KHÔNG áp dụng khi ta là người bán wheat chính (đỡ trợ cấp feed cho bò v6 — trang bị telemetry check opp cow trước khi bật).

### Trụ 5 — ENDGAME LIQUIDATION TUYỆT ĐỐI (d27-29)
- Từ d27 h0: mọi act = thu + bán; bỏ tưới/bón/care; DIG cây chết để nhặt weed? Không — thu những gì còn yield, bán sạch shed + túi trước h22 d29 (R3).
- Tile trống d27-29 KHÔNG tính vào chỉ số 15% (luật user: ngày cuối miễn trừ).

### Trụ 6 — ĐÀN LỚN HƠN (bò 8-11 + ngỗng 6-8) SAU khi trụ 1-4 ổn
- Chỉ mở rộng đàn khi feed-buy đã hoạt động (không mở rộng đàn nếu vẫn tự trồng feed — sẽ tái phạm tầng trống #1).
- Ngỗng từ 0 → 6-8 nếu telemetry cho thấy egg room còn (top-3 bán 228-322 egg!). Đây cũng là đòn egg-fortress S1 đã biết.

### Cổng đo (định nghĩa "đạt" cho từng trụ)
| Trụ | Đo | Đạt |
|---|---|---|
| 1 | ô dâu sống d18-22 | ≥ 22 |
| 2 | fert bán/mùa | ≥ 280u |
| 3 | acts/ngày trung bình d10-25 | ≥ 75 |
| 4 | wheat mua khi đàn ≥8 & giá ≤$30 | ≥ 150u/mùa |
| 5 | tồn cuối (shed+túi+trên ô) d29 h22 | ≤ 5u |
| Tổng | empty% d9-27 (trừ d4, d10-11) | ≤ 7% (top-3: 0-6.7%) |
| Tổng | tiền cuối vs v6.6 battery 100 | $75k+ và 100/100 |

### Rủi ro & cách né (từ RULES)
- **R98/R104 delta-noise**: mỗi trụ triển khai riêng (M1→M3 tách mốc) qua probe 10 seed khó nhất + plan-dump trước khi sửa (không sửa mù).
- **R95/R97 mirror**: trụ 1-5 là thay đổi cấu trúc (không phải tune hằng số) — an toàn với mirror; trụ 6 mở đàn là vùng v6 cũng chơi — cần telemetry gate.
- **R113 feed subsidy**: trụ 4 bắt buộc check opp-cow + own-wheat-role trước khi bật.
- **R127 được giải kiểu top-3** (labor bền đều + hiệu suất/act cao), không phải bằng cách giảm target fill.

---

## 9. TỔNG HỢP CHIẾN LƯỢC TẤN CÔNG HIỆN CÓ (inventory — nguyên trạng Task 35)

| # | Chiến lược | Cơ chế | Bằng chứng | Trạng thái trong kain40 |
|---|---|---|---|---|
| A1 | **Chiếm kênh bằng cam kết sớm** (yield-commitment) | pipeline đứng sớm → room() đối thủ (0.85×) tự nhượng quota | R99, R101, R105; kain16 thắng v5 bằng đòn dâu-30-từ-d5 | ✔ nền tảng (dâu 30 d5-13) |
| A2 | **Egg-fortress** | ngỗng 8-9 vs công thức cap 6 của v6 — nó không counter-scale được | R102, kain30 probe | ✖ kain40 bỏ ngỗng (v7 trụ 6 mở lại) |
| A3 | **First-mover premium** | bán trước ăn đoạn giá cao (bậc thang, không gradient) | R83 (melon d11 vs d12 chênh $100/quả) | ✔ ngầm trong tranche |
| A4 | **Tranche-8 / recovery premium** | chia nhỏ đợt bán cho drain hồi phục giá giữa giờ | R90; K16 | ✔ giữ nguyên |
| A5 | **Milk-commit** | floor 6 bò từ d4 — không nhượng kênh sữa | kain31 lật 28 seed | ✔ (floor 6) nhưng bị cap 10 |
| A6 | **Tomato-channel d17-19** | kênh $155 không ai trồng (AC.1) | kain40 probe | ✔ quota 10/8/6 |
| A7 | **Late-wheat filler d17-22** | wheat cuối $40-49 khi v6 hút 150-240u/ngày | R120, seed 103 | ✔ (fill-law) |
| A8 | **Carrot 2 lưỡi theo lớp seed** | nghèo → carrot-20 bootstrap; giàu → carrot-8 né máy v6 | R126 | ✔ adaptive |
| A9 | **Anti-yield** | không hiến kênh khi giá-bên ≥ 0.98 | R101, v6.2 33/40 | ✔ _marg giữ |
| A10 | **Đòn giá chủ động (dump ép giá)** | phá giá kênh đối thủ đang đứng | kain39 | ✖ ÂM TÍNH — bỏ (R119) |
| A11 | **MIRROR-trap né** | không fork kernel-space của chính mình | R95/R97 (parity 52.5%) | ✔ (kain40 khác cấu trúc v6) |
| A12 | **Endgame E8-lite** | chỉ giữ hàng khi drain còn hút hết pipeline | kain16→v6.6 | ✔ (v7 trụ 5 nâng cấp thành liquidation tuyệt đối) |
| A13 | **Yield-harvest yu≥3** | không để sản phẩm ngồi chết trên ô | R123 | ✔ |
| A14 | **Wheat decay-urgent 36h** | báo trước decay để thu kịp | R124 | ✔ |

**Nhận xét:** toàn bộ A1-A14 là chiến lược **kinh tế-thì-trường** (bán/đứng/điều tiết) — chưa có chiến lược **lao động-tiền tệ** của top-3 (fert-harvest, feed-buy, labor-sustain). v7 bổ sung đúng mảng còn trống.

---

## 10. REPLAY TOP-1 CÓ GIÁ TRỊ NGHIÊN CỨU KHÔNG? — CÂU TRẢ LỜI: CÓ, ĐÃ KIỂM CHỨNG

Download từ trang cạnh trận top-1 cho file JSON chuẩn kaggle_environments (mỗi file ~33MB, 720 step, observation đầy đủ farms 2 bên + market + town + private từng người — chính là format `battles/*.jsonl` của ta nhưng đầy đủ hơn).

**Giá trị đã khai thác được trong 30 phút (kết quả ở mục 7):** timing mua đất theo ngày, empty% theo ngày, cơ cấu cây/vật theo ngày, toàn bộ lệnh thị trường 2 bên (sells/buys/hires theo sản phẩm), đường tiền theo ngày, đàn cuối, cấu trúc ô cuối. Script: `bench/top_replay_extract.py` → `bench/top_replay_analysis.json`.

**Giá trị còn lại chưa khai thác (đề xuất khi cần):**
- Micro-timing bán theo giờ (so với đường cầu exact `_price()` của ta) → học nhịp tranche của top-1.
- Phân bổ care/feed từng con theo ngày → kiểm chứng care-banking ở đỉnh.
- Cây trồng từng ô theo ngày (planted_day) → "opening book" thế cờ đầu game d0-8 của top-3.
- Chuỗi hành động unit theo giờ → bài học đi bộ/route tối ưu.
- **Cách dùng đúng:** đối chiếu cấu trúc (đã xong mục 7) + nâng cấp từng trụ v7 theo số liệu — KHÔNG copy cả nước đi (đó là overfit theo kiểu R98-seed-blind).

**Cảnh báo**: đối thủ trong replay là top-3 lẫn nhau (meta restraint), không phải v6 — mọi kết luận phải kiểm lại trong battery của ta trước khi tin.

---

## 11. LỘ TRÌNH v7 (milestone + tiêu chí dừng)

| Mốc | Nội dung | Tiêu chí | Dừng/kém |
|---|---|---|---|
| M1 | kain41 = kain40 + Trụ 1 (dâu vòng 2) + Trụ 2 (fert) — 2 trụ lớn nhất, thêm vào không đụng quota gốc | probe 10 seed khó ≥ 8/10 → battery 100 ≥ 95/100, empty d9-27 ≤ 12% | autopsy trước khi sửa tiếp (R98) |
| M2 | kain42 = + Trụ 3 (labor 9-10) + Trụ 5 (liquidation) | battery ≥ 98/100, empty ≤ 8%, avg ≥ $70k | dừng tune — quay autopsy |
| M3 | kain43 = + Trụ 4 (feed-buy) + Trụ 6 (đàn lớn, ngỗng 6-8) | **100/100, avg $85k+**, empty ≤ 7% | nếu thua do mirror → khác biệt hóa cấu trúc (R95) |
| M4 | autopsy 7 thua cũ (108 0.772x ưu tiên) trên nền kain43 | mọi seed thua có chẩn đoán plan-dump | — |
| M5 | đối đầu chéo kain43 vs kain40/kain38 (chống mirror-trap nội bộ) | không có regression | — |

**Nguyên tắc thực thi (không thương lượng):** mỗi bản = 1 autopsy trước + probe 10 seed khó + battery 100 hai ghế; không fork kernel khi không có chẩn đoán (R98/R104); push GitHub sau mỗi mốc (bài học Task 37 — rollback ăn mất workspace).

---
*KAIN — RESEARCH_V7.md Phần II (Task 38). Nguồn: RULES.md v2.10 (130 quy tắc, mục AC), battery kain40_vs_v6_100.json (93/100), upload/107559251.json + upload/107573831.json (replay top-3, trích xuất bench/top_replay_extract.py).*
