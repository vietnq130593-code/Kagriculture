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
