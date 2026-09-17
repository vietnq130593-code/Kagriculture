# BỘ TÀI LIỆU NGHIÊN CỨU KAGGLE — HƯỚNG ĐỘT PHÁ V15→V16

> **Nguồn**: Kaggle API (token KGAT) — competition `kaggriculture`, trang /code — 493 public notebook,
> 34 notebook giá trị nhất đã tải + phân tích code-level (Task 74, ngày 13/9).
>
> **Bối cảnh champion**: v15 ARI CLASS Mk-II (Task 73) = v14 + R90 shed-animal watchdog.
> Battery 40/40 thắng vs 4 đối thủ local + 10/10 hòa tuyệt đối vs v14.
> 2 trận thua Kaggle = mirror-class (1 bug đã fix + 1 noise wheat feed-vs-sell).

## CẤU TRÚC BỘ TÀI LIỆU

| File | Nội dung | Đối tượng đọc |
|---|---|---|
| `00_README.md` | (file này) Index + cách đọc bộ tài liệu | Tất cả |
| `01_KAGGLE_LANDSCAPE.md` | Toàn cảnh 493 notebook: strategy clusters, meta evolution 7/30→9/13, top-40 votes, leaderboard, engine facts | Hiểu chiến trường |
| `02_TOP_TECHNIQUES.md` | Danh mục ~25 kỹ thuật đắt giá nhất public meta — mức code, nguồn notebook cụ thể, độ tin cậy | Chọn vũ khí |
| `03_BREAKTHROUGH_PLAN.md` | **KẾ HOẠCH THỰC NGHIỆM** — 12 hướng xếp hạng 3 tier, mỗi hướng có protocol/gate/cost/risk | Triển khai v16 |
| `ANALYSIS_KAITO.md` | Deep-dive họ Kaito Fukami (v20/v21.1/v43/v48) — LB #3, win-rate claim cao nhất | Tham khảo sâu |
| `ANALYSIS_BOATLEE_THOMAST.md` | Deep-dive boatlee (V14 preemption/V16-RC2/V29-R1) + thomastschinkel router 93.8% | Tham khảo sâu |
| `ANALYSIS_YHAY_HAMBURGER_MISC.md` | Deep-dive yhay81 shop-router + hamburger + salemali7 — **phát hiện: yhay81 là tổ tiên直 tiếp của chassis v15 ta** | Tham khảo sâu |
| `ANALYSIS_PRVSIYAN_TETSUTANI.md` | Deep-dive prvsiyan (yhay-family lab) + tetsutani BL-Kawashigi + indarkarhana E776 (Kenjo medoid — đối thủ mới ngoài registry) | Tham khảo sâu |
| `ANALYSIS_POLICY_ENGINES.md` | Deep-dive pilkwang/ahmedberatozer V38/andrewsokolovsky tie-break/georgymarin economics + **guruprasaathas V39 (mới hơn kme3v10!)** | Tham khảo sâu |

## THƯ MỤC DỮ LIỆU

- `kaggle_dl/` — 34 notebook gốc (code `.py` extracted + `_md.txt` + raw ipynb + list 493 NB theo votes/ngày)
- `kaggle_dl/unpacked/` — main.py agent đã giải nén từ payload (kaito_extracted/, tetsutani, prvsiyan, indarkarhana, boatlee V14/V29...)
- List đầy đủ 493 notebook: `kaggle_dl/list_votes_p1..10.json` (sort by votes) + `list_recent_p1..3.json` (sort by date run)

## 5 PHÁT HIỆN LỚN NHẤT (TL;DR)

1. **Meta đã collapse quanh 1 opening** (26/30 top teams cùng 1C/4S/HIRE4) — edge thực sự nằm ở
   *continuation timing + market execution*, đúng hướng v14/v15 đang đi. Nhưng top-1 mới (9c4s, strawberry batch 15.4 d15)
   đã dịch chuyển — cần refresh tape định kỳ (nên kéo replay top-20 mỗi tuần).
2. **3 kỹ thuật rẻ nhất đáng bolt-on ngay vào v15** (tier-1 trong 03): town-demand gate cho front-run,
   debt-ledger chống double-sell, mega-SELL endgame qty 10^6 + dead_stock ON. Cả 3 là layer ngoài cùng zero-regression.
3. **Kaito v21.1 (LB#3) có "Conditional Memory"** — 1-NN match 30 prototype chữ ký farm top-30, đoán item đối thủ
   *sắp bán ngay turn này*, chỉ **reorder** SELL trùng lên đầu queue (không tạo SELL mới) → 177/180 vs top-30. Đây là
   upgrade trực tiếp cho tầng front_run của ta.
4. **guruprasaathas vừa release V39** (notebook "V3" 317KB) = kme3v10 + 3 layer mới (R88 horizon-feed, R95 grain-reserve,
   R97 supply-guard) → **phải dựng kme3v39 làm đối thủ battery mới**, kẻo local meta lạc hậu Kaggle.
   Thêm 2 đối thủ ngoài registry: BL-Kawashigi (tetsutani), indark_e776 (Kenjo 9C5S).
5. **"Router steering" = lớp tấn công mới** (từ thomast 93.8% router): decision tree router của đối thủ đọc public state
   (giá CARROT ≤54 → tape3 kém). Ta có thể *đổ CARROT trước step 576* để đẩy router vào nhánh tồi — đòn thao túng state,
   lần đầu có ở mức code, không vi phạm luật đối xứng engine.

## CÁCH DÙNG ĐỂ TRIỂN KHAI V15/V16

Đọc `03_BREAKTHROUGH_PLAN.md` → chọn hướng theo tier → mỗi hướng có "gate" (tiêu chí thắng/bại)
theo protocol battery chuẩn (seeds mới × 2 ghế, đối thủ = v15 incumbent + tối thiểu 1 họ public khác).
Nguyên tắc vàng giữ nguyên từ Task 69: **1 biến thể = đúng 1 delta**, veto nếu thua parent ở bất kỳ seed nào.
