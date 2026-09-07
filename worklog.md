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
