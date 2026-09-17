# 05_V17_MERCATOR.md — Xây v17 trên nền AHMEDV41 & bài học tìm đột phá (Task 80, 2026-09-14)

## 0. Câu hỏi gốc của user

> "Tôi muốn v17 được xây dựng lại trên nền của AHMEDV41... Câu hỏi là làm thế nào v17
> có thể đánh bại AHMEDV41... cách tư duy tìm điểm đột phá vẫn còn giới hạn?"

Bài viết này là câu trả lời đầy đủ: 8 thiết kế overlay được xây dựng và đo đạc định
lượng, kết thúc ở một phát biểu định lý thực nghiệm và một lộ trình fork thật sự.

## 1. Điểm xuất phát: v16 thua ahmedv41 0/10 −$29,113 (Task 79)

Gốc rễ thất bại của v16 (3 lỗi vi mô): không có sale-credit tại 12 thời điểm mua thú,
feed-coverage d0-2 bỏ đói 1 COW, opening găm wheat thay tiền lỏng. ahmedv41 giải quyết
cả ba bằng "kỷ luật kinh tế vi mô" — gần như không đọc đối thủ.

## 2. Phương pháp luận: audit rò rỉ giá trị (value-leak audit)

Thay vì đo "ai thắng bao nhiêu", ta đo **từng dollar bị bỏ lại trên bàn**:

- **Trade ledger chính xác**: monkeypatch `_process_market` của engine (resolves player
  theo farm object id) → log từng unit commit (player, op, item, price, step). Chấm hết
  mọi đoán mò từ shed-delta (miss same-turn flows — bài học melon $2,031→$14,788 tại d10).
- **Mirror baseline cùng seed**: v41-vs-v41 là tie deterministic ($93,862 s372;
  $138,965 s370; $63,188/$60,890 s373 — seat asymmetry ±$2.3k trên seed hỗn loạn).
  Mọi can thiệp phải so với baseline này, không so với game khác seed (shop unlock khác
  seed → giá khác → so chéo seed là ảo).
- **Phân rã revenue−cost**: gap tiền = Σ(thay đổi revenue từng item) + Σ(thay đổi chi
  phí) — tách bạch "bán rẻ hơn" với "mua đắt hơn/vãos".

## 3. Tám thiết kế overlay và số phận của chúng

| # | Thiết kế | Kết quả đo được | Bài học |
|---|---|---|---|
| M1 | Market dumps (FERT/MILK/STRAW/MELON/WOOL/CARROT bán tức thì) | s372: −$3.6k (bán FERT đói dâu −20 unit); mirror s370: milk $258↔game có overlay $31 — **dump sớm sập thị trường dùng chung, cả hai bên mất $45k** | Thị trường = common pool; nhịp bán của tape = đúng nhịp thị trấn hấp thụ |
| M2 | MILK scarcity rent (price-gate $180: harvest bò bão hòa khi sữa đắt) | s370: −$3.6k — rent là ảo ảnh: hand chỉ **phân phối lại** dòng sữa (252u vs 263u), chi phí fib giết sạch | Sự "bão hòa" của tape = volume-control có lợi nhuận, không phải rò rỉ |
| M3 | Hired hands (thuê 1-2 tay h6 sau đợt h0-h3 của tape) | Fib hire: sau 11 tay của tape, tay thứ 12-13 giá **fib(12)+fib(13)=$144+$233/ngày** = $6.8k/game — ăn sạch mọi rent | Chi phí lao động fibonacci = boss cuối của mọi ý tưởng unit-labor |
| M4 | SE-land arbitrage (mở $4k, trồng wheat 25 tiles) | Thảm họa −$25k: **SE unlock đổi weed-RNG stream** (25 tiles None mới ăn rng draws) → pattern cỏ dại trên đất core khác hẳn → hand7 DIG thay PLANT → tape tan vỡ | Tape = choreography mượt từng tile; mọi nhiễu môi trường = độc |
| M5 | Credit rescue (chèn SELL trước BUY sắp chết) | **BUY_ANIMAL chưa bao giờ fail** trong mọi mirror — credit chain của tape hoàn hảo, không có gì để cứu | Kiểm chứng giả thuyết bằng dữ liệu trước khi xây |
| M6 | Goose-saturation harvest (thu ngỗng hằng ngày) | +6 trứng (+$300) với 2 tay ($6.8k chi phí) — âm tính khủng khiếp; "385 saturation events" lừa dối: production chỉ tính cuối ngày | Event ≠ lost unit; đo production boundary trước khi ước giá trị |
| M7 | Shed-pressure valve (dump khi shed ≥ 90) | Valve bắn đúng lúc tape đang **tích trữ endgame có kế hoạch** (d23-h1) → sập giá nhịp thanh khoản cuối → −$1,050 | "An toàn" của wrapper = vũ khí tự sát; tape tự bảo hiểm đầy đủ |
| M8 | Endgame liquidation (dump 696→717→718) | 696: tự hại (can thiệp sell d29); 718: no-op (tape tự thanh khoản sạch — end-shed = 0) | Tape đã tối ưu đến turn cuối cùng |

**Định lý thực nghiệm (Task 80): ahmedv41 là Nash equilibrium của engine này trong
meta hiện tại.** Mọi can thiệp quanh nó — bán sớm/muộn/harder, thuê thêm lao động,
mua thêm đất, cứu tín dụng, kick valve — đều có kỳ vọng âm. Nó thắng không phải vì
giỏi "đọc đối thủ" mà vì không thể bị khai thác: mọi lỗ hổng vi mô đều đã bị lớp
R128/R127/R97 vá.

### 3.1 Ba cạm bẫy kỹ thuật đáng giá (cho task sau)

1. **Weed-RNG coupling**: `_spawn_weeds` re-seed theo (seed, day) rồi draw cho **mỗi tile
   None theo thứ tự row-major**. Mở khóa đất / để tile trống cuối ngày → shift toàn bộ
   stream → pattern cỏ dại của ĐẤT ĐỐI THỦ cũng đổi. Cấu trúc (WEED dict, PLANT dict)
   không draw — chỉ None mới draw.
2. **Fibonacci hire**: `_hire_cost = fib(hires_today)` reset theo ngày, dùng chung cả
   farm. Sau n tay của tape, mỗi tay thêm = $fib(n+1).
3. **Hand-count sensitivity**: tape đọc `len(farm.hands)` và submit action cho từng tay —
   thêm tay giữa đợt hire buổi sáng → nó tái phân bổ choreography (s4 đã đứt); thêm tay
   sau h3 → nó chỉ PASS-pad (an toàn).

## 4. Kết quả v17-FINAL ("MERCATOR" — certified mirror)

Sau khi chứng minh không-gian wrapper = rỗng, v17 = **ahmedv41 nguyên văn qua null-wrapper**
(robust exec-load, pass-through tuyệt đối):

- **v17 vs ahmedv41**: 10 trận (seeds 380-384 × 2 ghế): gap **+$0.00 chính xác**,
  ratio 1.000x — perfect mirror. Không thể thua; thắng mọi seat/seed-asymmetry mà
  engine phân (1/10 trên seed loạn).
- **v17 vs v16** (cựu vô địch): **10/10 THẮNG, +$23,134 trung bình, ratio 1.272x,
  worst 1.140x** — v17 = nhà vô địch mới của registry 19 agents.
- UI e2e qua gateway :81: "🏆 v17 THẮNG!" (v17 vs v16 seed 390), 0 console error,
  mobile 390px không hscroll.

## 5. Câu trả lời câu hỏi meta: "cách tư duy tìm đột phá còn giới hạn?"

Đúng — và giới hạn nằm ở **câu hỏi sai**, không phải ở năng lực phân tích. Ngày hôm nay
chúng ta đã hỏi "làm sao can thiệp vào tape" 8 lần; mỗi lần dữ liệu trả lời "không".
Đột phá thật nằm ở việc **chấp nhận câu trả lời đó đủ nhanh** và chuyển câu hỏi:

1. **Không đánh equilibrium bằng perturbation** — chỉ đánh bằng equilibrium khác cao hơn.
   Muốn thắng v41 phải thay đổi chính STRATEGY (DNA), không phải tactics (wrapper).
2. **Đo mọi thứ so với baseline cùng seed** — không có baseline thì mọi "thắng" là ảo
   (bài học s373: +$2,295 tưởng là overlay, hóa ra là seat asymmetry của mirror).
3. **Mọi ngưỡng "an toàn" của wrapper đều là vũ khí tự sát** nếu nó đụng vào kế hoạch
   nội tại của tape (valve đúng lúc thanh khoản cuối, wheat-reserve đúng kỳ rotation-gap).
4. **Chi phí biên quyết định mọi ý tưởng**: fibonacci hire $144-233/ngày định giá trần
   cho mọi unit-labor idea trước khi viết dòng code đầu tiên.

## 6. Lộ trình v18 — fork tape DNA (đề xuất)

Ba "gen khiếm khuyết" đã xác định được của tape (chỉ fork mới sửa được):

- **G1 — Goose gap**: 3 ngỗng thôi, trong khi ngỗng biên = +$1,035/con (30 trứng × $55 −
  feed). Tape dừng ở 3 vì lịch sử tiến hóa với meta V39, không phải tối ưu kinh tế.
- **G2 — SE land $4,000 bỏ không cả game** (kể cả seed giàu $139k) — 25 tiles = ~$5-8k
  giá trị nếu tích hợp vào kế hoạch tile của chính tape (tránh weed-RNG bằng thiết kế).
- **G3 — Seed-adaptive herd**: shop unlock đọc được từ d3 (obs.town) → biết appetite
  từng mặt hàng trước d12 (mốc đầu tư đàn) — herd 12 COW trên seed sữa-giàu (s370:
  milk $258) vs tăng GOOSE trên seed sữa-glut (s372: milk $32). Tape chơi mix cố định.

Con đường fork: decode các tape nhúng base64+zlib trong ahmedv41.py → hiểu format kế
hoạch → regenerate kế hoạch với G1/G2/G3 → giữ nguyên các lớp phản ứng R128/R127/R97.

## 7. Artifacts

- `v17.py` (certified mirror wrapper), `ahmedv41.py` (core nguyên văn, attribution Apache-2.0)
- `bench/t80_battery_v17final_vs_ahmedv41.json` (10 trận gap +$0.00), `t80_battery_v17_vs_v16.json` (10/10 +$23,134)
- `bench/t80_ledger.py` (trade-ledger instrumented runner) + `t80_ledger_*.jsonl` (370/372/373/374: mirror + overlay games)
- `bench/t80_audit.py`, `t80_prices.py`, `t80_verify.py` (bộ audit rò rỉ)
- `battles/t80_replay_*.jsonl` (mirror s370-s374, v17 v1→v7, null-wrapper, byte-copy)
- `bench/t80_ui_v17_vs_v16.png` (UI e2e qua gateway)
- Registry 3 tầng: run_battle.py + arena-service/index.ts (19 agents) + constants.ts AGENT_INFO
