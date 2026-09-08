# Project Worklog

---
Task ID: 1
Agent: main (Z.ai Code)
Task: Phân tích cuộc thi Kaggle Kaggriculture — nghiên cứu luật chơi, kiểm chứng mechanics từ source code, chạy mô phỏng, và xây dựng phân tích chiến lược tối ưu lợi nhuận

Work Log:
- Đọc trang Overview + Rules cuộc thi kaggriculture qua page_reader (web-reader skill)
- Tải notebook "Kaggriculture: Getting Started" qua Kaggle public API, phân tích 12 cell (6 code + 6 markdown), xác định cell nào là harness vs nội dung bài nộp
- Cài kaggle-environments 1.32.7, đọc toàn bộ source `kaggriculture.py` (1086 dòng): xác thực CROPS/ANIMALS/MARKET_PARAMS/SHOPS, logic WATER (bonus window), CARE banking, hire fib cost, market per-unit lockstep, end-of-day auto-drop, game kết thúc ở step 718 (hour 22 ngày 29 — không có auto-drop ngày cuối)
- Xây dựng engine task-scheduler thử nghiệm (engine2.py) với plant-rate control, sell quota/gate, hire-first market ordering
- Chạy ~30 trận mô phỏng 720 lượt: baseline (melon_maxxer $5,957, starter $3,725), wheat_rush, egg_rush, melon slow-sell, COMBO portfolio, mirror matches
- Tính bảng market depth từ hàm market_price thực tế + demand kỳ vọng của town theo shop draws

Stage Summary:
- Kết quả thực nghiệm chính: melon slow-sell (1 quadrant, quota 3/day, gate $120) = $27,3xx–28,2xx ổn định qua nhiều seed, gấp 4.7× tutorial agent; mirror match melon = $13.6k mỗi bên (chia sẻ thị trường premium); quản lý kém giết chiến lược tốt (egg engine của tôi chỉ $2.5-3.7k do pipeline yếu)
- Mechanics quan trọng đã xác thực: cây trồng trong ngày phải tưới ngay trong ngày; CARE +1 ngày cho动物 production; hire chỉ $1–21/ngày (fib); town tiêu thụ ~700 wheat, ~580 strawberry, ~440 carrot+milk, ~300 egg/wool/tomato mỗi mùa; melon chỉ 1/day; fertilizer town không mua
- Sản phẩm phân tích: chiến lược theo giai đoạn, bảng độ sâu thị trường, kiến trúc agent đề xuất, phương pháp kiểm thử — đã trình bày đầy đủ cho user trong phần trả lời
- File thí nghiệm: /home/z/kagri_sim/ (engine2.py, melon_agent.py, sim scripts)

---
Task ID: 1
Agent: main-agent (Z.ai Code)
Task: Viết nội dung Cell 4 cho notebook Kaggle Kaggriculture (agent nâng cấp thay melon_maxxer)

Work Log:
- Đọc source engine kaggle-environments 1.32.7 (kaggriculture.py, 1086 dòng): trích CROPS/ANIMALS/MARKET_PARAMS/SHOPS, công thức giá thị trường, luật tưới/cho ăn/CARE, chi phí fib thợ, giá đất.
- Probe thực nghiệm engine: xác nhận COW 36 sữa (feed+care) vs 12 (không care), GOOSE 56 vs 27 trứng; yield Wheat 4/Carrot 3/Melon 6/Tomato 4/Straw 4 với tưới tối ưu; melon crash giá tại I0+100 → $150.
- Viết agent "Homestead" ~1000 dòng: kế hoạch ngày theo forward-absorption thị trường, phân bổ cây theo score/tile-day + share cap, bán theo mô phỏng giá biên (port công thức engine), sticky assignment chống ping-pong, nhịp trồng theo sức tưới, sàn tiền mặt chống phá sản.
- Vòng lặp test-diagnose-fix 7 lượt: (1) bẫy nghèo do mua đất hút tiền → hạt trước đất sau; (2) BUY_ANIMAL lặp mỗi giờ → ledger theo ngày; (3) ping-pong assignment → sticky; (4) tier-6 PLANT không bao giờ được nhận → T_PLANT=5 + hire 12 unit + workload tính kế hoạch trồng; (5) van cám hút $1k/lượt → đệm 2 ngày; (6) shed tràn 100 vì phân+cám → cap collect; (7) phá sản seed 3 → sàn $250 + nhịp trồng an toàn.
- So sánh cấu trúc: có thú = $24-33k, không thú = $32-44k → chốt thuần cây trồng (targets=0, giữ khung mã thú).
- Kết quả cuối: vs melon_maxxer 8/8 thắng $31-51k (đối thủ $4-5.8k); vs random $33-47k vs $0; vs starter $33k vs $3.5k; self-play hòa 24k/23k; episode ~4s.

Stage Summary:
- Sản phẩm: /home/z/my-project/kaggriculture/cell4_agent.py (1006 dòng, hàm `agent` cuối file, không import ngoài stdlib, an toàn nộp Kaggle).
- Quyết định chính: bỏ vật nuôi v1 (lỗ ròng do cướp lao động), ưu tiên hạt > đất, sticky task assignment là bản vá quyết định (tăng +$10k).
- Còn tiềm năng: bật lại thú với lịch trình lao động tốt hơn, tối ưu luồng bán melon khi đối thủ dump, tomato gần như chưa dùng (market trống).

---
Task ID: 3
Agent: main-agent (Z.ai Code)
Task: Kaggriculture — tối ưu agent khai thác toàn bộ thị trường (EGG/MILK/WOOL/FERTILIZER), xuất code thuần cho cell 4, hướng dẫn nộp bài & tính điểm

Work Log:
- Đọc lại artifact phiên trước: /home/z/my-project/kaggriculture/cell4_agent.py (agent "Homestead", vật nuôi TẮT), /tmp/kagri_*.json (overview/rules/notebook).
- Đọc source engine kaggle-environments 1.32.7 (envs/kaggriculture/kaggriculture.py): công thức giá, cơ chế FEED/CARE/pending_care_bonus, fertilizer_available 1/con/ngày, shop drain mỗi 4 step, tồn kho vật nuôi bị hút -> giá trên base.
- Dựng benchmark: kaggriculture/bench/ (baseline.py = phiên trước, melon.py, run.py, run2.py). Baseline: vs melon 6/6W $36.7k; vs random $35.9k.
- v2: bật vật nuôi 4 ngỗng/3 bò/4 cừu (SHEEP mới hoàn toàn), mua/build/deliver/feed/care/harvest đầy đủ, bán FERTILIZER hằng ngày (ngưỡng $68).
- Benchmark v2 đầu: thua baseline head-to-head (3W/5L). Chẩn đoán: MOVE chiếm 80-90% lượt, FEED/CARE muộn, thú bỏ trốn, cỏ dại 17-29 ô, cây trồng chỉ 28-30/100.
- Refactor lớn: (1) task SERVICE composite = FEED+CARE+COLLECT_FERTILIZER 1 chuyến/thú; (2) tưới duy trì theo parity (x+y+day)%2 thay vì hằng ngày — engine chỉ giết cây khi 2 ngày liên tiếp không tưới; (3) trồng WHEAT đầu danh sách khi có feed_demand + cap 20; (4) shield + release thợ mang lúa mì khỏi task khác khi còn thú đói; (5) need_drop tính trên hàng bán được (trừ lúa mì); (6) hire factor 3.0, budget 16%.
- Sửa bug: unit đứng PASS trên thú không cho ăn được (validity tính wheat obtainable), bỏ detour kho khi kho rỗng, harvest thú yu=0 ngày cuối.
- Kết quả cuối: vs BASELINE 6-7/8 W, $40-41k vs $26.3-26.6k; vs melon 6/6W $42-46k; vs random $45-48k; self-play ổn 34-38k không tự hủy; 0-3 escape (trước: 2-3/episode chết dây chuyền).
- Thử nghiệm mở rộng: 14 thú ($37.5k) và 14 thợ ($37.5k) — đều tệ hơn, giữ 11 thú/12 thợ.
- Xuất file thuần code không chú thích: kaggriculture/submission.py (1016 dòng, AST strip comments+docstring, syntax check OK), đồng bộ cell4_agent.py. Xác minh lại benchmark file cuối.
- Trích xuất hướng dẫn nộp bài/tính điểm từ kagri_overview.json: 3 cách nộp (main.py root + agent function), validation episode tự đấu với bản sao, rating skill theo W/L, 5 submit/ngày, 2 submission mới nhất active, Bradley-Terry finals, timeline 23/9-30/9-15/10/2026.

Stage Summary:
- Sản phẩm: /home/z/my-project/kaggriculture/submission.py (= cell4_agent.py, thuần code 1016 dòng) + v2.py (bản dev có chú thích) + bench/ (harness benchmark).
- Điểm mạnh agent: đa thị trường đầy đủ 9 mặt hàng (5 cây + EGG/MILK/WOOL/FERTILIZER), giá trị/đô la của vật nuôi rất cao vì thị trấn hút tồn kho EGG/MILK/WOOL làm giá trên base (MILK quan sát $271-376).
- Số liệu chuẩn: thắng 100% melon_maxxer & random; thắng ~85% vs bản crop-only mạnh; $40-48k/episode.
- Hạn chế biết trước: chống đối thủ cũng chạy vật nuôi (chưa benchmark bot vật nuôi đối thủ — thị trường EGG/MILK/WOOL sẽ bị chia).

---
Task ID: 4
Agent: main-agent (Z.ai Code)
Task: Kaggriculture — xây agent v3 "AgroIndustrial" đánh bại áp đảo bài nộp cũ (v2 Homestead), mục tiêu thu nhập >= 2x trong đối đầu trực tiếp

Work Log:
- Chẩn đoán v2 bằng benchmark có instrument (patch _commit_unit/_process_market log mọi giao dịch SELL): phát hiện các thị trường bỏ trống khổng lồ — MILK hấp thụ ~327u/mùa nhưng v2 chỉ bán 40-52u (giá $308!), WOOL ~228u vs 28-41u ($245), STRAW ~426u vs 16-47u ($271), FERT vô hạn.
- Viết v3.py từ nền v2 (copy submission.py + 27 vòng phẫu thuật/tuning): quota nông trại mới (wheat feed-driven, straw 30, melon 14 từ ngày 0), đàn thú thích ứng theo thị trường còn trống (cow 7/sheep 6/goose 5, cap 16), ngưỡng bán HOLD theo mặt hàng, melon denial (hold 0.52x base tước $18-20k melon của v2), thanh lý ngày 26-28.
- Sửa 7 bug gốc tìm qua trace từng ngày: (1) hire budget floor quá cao làm 0 thợ khi nghèo -> cây chết dây chuyền; (2) mua hạt all-or-nothing -> straw không bao giờ có hạt (sửa sang mua từng phần); (3) phân bổ ô không trừ cây đang đứng -> quota wheat "ăn" hết ô; (4) double-subtraction standing/fresh_young -> chỉ trồng lại nửa cây thu hoạch; (5) plant tier 3 đánh cắp nước tưới -> cây chết; (6) worker PICKUP 12 wheat hút sạch kho -> tỷ lệ cho thú ăn chỉ 35% (sửa n=5 + mua theo shed gate); (7) vòng lặp mua-bán wheat $42 cháy order slot (giới hạn mua chỉ khi giá <= 38).
- Kết quả benchmark cuối (kaggle-environments 1.32.7): vs v2 10/10 trận thắng, v3 $44-64k vs v2 $29-48k, tỷ lệ trung bình 1.34-1.46x, trận đỉnh 2.0x; vs melon_maxxer 10.05x ($54.7k); vs random $52.8k; vs starter 15.6x ($52.9k); self-play ổn định $48-51k (validation episode của Kaggle).
- Xuất submission_v3.py (911 dòng, AST strip comment, syntax + import check OK), verify hiệu năng ngang v3.py.

Stage Summary:
- Sản phẩm: /home/z/my-project/kaggriculture/submission_v3.py (thuần code, hàm agent() cuối file) + v3.py (bản dev) + bench/diag.py (harness đo sales mix).
- Chiến lược cốt lõi: chiếm các thị trường đói (milk/wool/straw premium $250-300), melon denial phá nguồn thu lớn nhất của v2, đàn thú 10-16 con nuôi bằng wheat tự trồng + mua rẻ ($<=38), kỷ luật tiền mặt 4 ngày bootstrap (wheat+carrot engine) trước khi mở rộng.
- Giới hạn vật lý đã xác nhận: thị trường dùng chung 2 người chơi + năng suất lao động ngang nhau (2.4 bước di chuyển/hành động cho cả hai agent) => thu nhập trung bình 1.3-1.5x là tối ưu khi đối thủ là bản sao cũ mạnh; 2x tuyệt đối chỉ đạt ở trận đỉnh hoặc vs đối thủ yếu.
- v2 vẫn giữ nguyên làm baseline đối chiếu: submission.py (v2) vs submission_v3.py (v3).

---
Task ID: 5
Agent: main-agent (Z.ai Code)
Task: Kaggriculture — viết nghiên cứu phân tích chiến lược (RESEARCH_v4.md) từ bài học submission_v3.py, nền tảng thiết kế v4 đánh bại áp đảo v3 (≥2x)

Work Log:
- Khôi phục context: đọc submission_v3.py/v3.py (1095 dòng), worklog 4 task trước, bench/diag.py
- Kiểm chứng lại source engine (kaggle-environments 1.32.7): market I0=10000 mọi mặt hàng, per-unit lockstep, BUY chỉ WHEAT/FERT (quote giá sau mua), shop drain mỗi 4 step (x2 cho shop 1 mặt hàng), town center 1u/ngày, shop unlock mỗi 3 ngày max 8 (RNG seed^day), hire fib resets HÀNG NGÀY (hands=[] cuối ngày — lao động là dịch vụ thuê ngày), plant chết khi 2 ngày liên tiếp không tưới (ngày trồng tính cu=1), phân +2 yield trong cửa sổ nhưng cap max_yield (melon 0 gain, chỉ rút cycle), CARE pending bonus ăn khi ngày sản xuất được feed, max_held chặn sản xuất, ongoing crop chết sau lần sản xuất cuối, overflow shed bị HỦY, kết thúc step 718 không auto-drop
- Chạy trận diag mới v3 vs v2 (instrument _commit_unit): v3 net $41.081, GROSS $102.815 (WHEAT 898u/$34.9k avg$39, FERT 196u/$15.8k, MILK 65u/$242, WOOL 62u/$220, MELON 73u/$152, EGG 134u/$60, STRAW 6u — nhường v2 bán $312), v2 net $34.286 — phát hiện v3 ĐỐT $61.7k chi phí (hire ~$10k + thú + đất + cám)
- Tính bảng định lượng bằng engine: đường giá theo offset tồn kho 8 mặt hàng; headroom theo ngưỡng; bảng CHI PHÍ PHÁ GIÁ (MILK sập chỉ cần 3u, STRAW 8u, WOOL 16u, WHEAT 2421u bất khả thi); cống hút kỳ vọng (WHEAT 520/mùa, STRAW 422, MILK 324, MELON CHỈ 30 — không shop nào hút melon, FERT drain=0)
- Phát hiện lỗ hổng thông tin lớn nhất: tồn kho thị trường public + drain tính được + my_sales biết chính xác → opp_sales = Δinv + drain − my_sales (đo dòng bán đối thủ từng giờ, chính xác tuyệt đối) — v3 chỉ nhìn bàn cờ đối thủ
- Phát hiện "presence warfare": công thức v3 dòng 306-308 (milk_room = absorb − 30×opp_COW − 40) khiến v3 TỰ RÚT khỏi thị trường khi đối thủ có đàn lớn → v4 chiếm milk/wool bằng tồn tại, không cần denial đắt tiền
- Viết RESEARCH_v4.md (480 dòng, tiếng Việt): 15 luật vật lý kiểm chứng, cấu trúc vi mô thị trường, giải phẫu v3 + 7 điểm rò tiền (quota cứng theo ngày, dead code fert cây dòng 452-470, FERT 196/310, EGG cap 5 ngỗng, hire không ledger $/action, mù thông tin dòng bán, 0.85×opp_pipeline), lý thuyết common-pool flow auction + 3 chế độ đối đầu, 7 thị trường bỏ trống định lượng (TOMATO/STRAW/FERT/EGG/timing WHEAT/fert-on-wheat +$78/plant), blueprint v4 6 module (World Model telemetry, Portfolio Solver, Labor Ledger + Zoning, Market Ops, Presence Warfare, Safety), bảng giá trị 9 đòn (E1 presence +$25-33k là 55%), lộ trình P0-P6, rủi ro overfit/self-play/phương sai seed

Stage Summary:
- Sản phẩm: /home/z/my-project/kaggriculture/RESEARCH_v4.md (nghiên cứu chiến lược 480 dòng, hợp đồng thiết kế v4)
- Kết luận trung tâm: 2x vs v3 đạt được (dự phóng 1.8-2.3x) bằng (1) presence warfare buộc v3 tự rút khỏi milk/wool/straw, (2) khai thác 4 thị trường trống (TOMATO/STRAW/FERT/EGG + fert-on-wheat), (3) zoning + labor ledger cắt MOVE 80-90%→≤55%, (4) telemetry opp_sales — KHÔNG dựa vào denial đắt
- Số liệu nền: v3 gross $102.8k/net $41k (đốt $61.7k); denial cost MILK 3u/STRAW 8u/WOOL 16u/MELON 110u/WHEAT bất khả thi; CARE $220-242 là action đắt nhất; 12 hire = $376/ngày
- Bước tiếp theo: P0 — instrumentation đo opp_sales trong 10 trận v3-vs-v3 kiểm định giả thuyết telemetry
