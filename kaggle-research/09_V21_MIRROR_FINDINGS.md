# 09 — V21 MIRROR FINDINGS: H1 Milk Printer bị bác bỏ trong thế giới mirror
## 6 thực nghiệm định lượng · Cơ chế thất bại · Đường đi còn lại

> Task 89 · 2026-09-17 · Bio
> Chuẩn đo: v20 (flat build 410KB) vs ahmedv46, official kaggle_environments 1.32.7
> runner, full 720 turn/game, seeds 2-9 (8-seed probe) + battery 48 trận (24 seed × 2
> ghế). Engine facts verify trực tiếp từ source (L544-672 _process_market/_commit_unit,
> L192-206 market_price, L61-74 _shape).

---

## 0. TÓM TẮT ĐO NÉT

| Config | Cơ chế | Mean margin (8 seed) | Kết luận |
|---|---|---|---|
| v20 (baseline) | — | **+$1,566** | tham chiếu |
| v21-v1 bank+liquidate | WOOL/STRA/MELON floor 100-140 + dump khi hồi phục | +$537 | **−$1,030** — liquidate-dump tự re-crash + free-rider |
| v21-v2 trim-only WOOL | floor 120, cap 25, không liquidate | +$1,259 | −$307 — giữ bán $50-98 rồi REAPER bán lại cùng giá |
| v21-v3 COW→SHEEP swap | đổi 6 bò thành 6 cừu (PASTURE chung) | **−$17,995** | **THẢM HỌA** — xem §2 |
| v21-v4 floor-banker $15 | chỉ giữ lệnh bán rác <$15 | +$1,566 | vô hiệu — trim dead orders (engine đã no-op) |
| v21-v5 (final) | v4 + fix 2 bug (shed guard đếm wheat buffer; flag `trimmed` không set khi xóa hết order) | +$1,575 | **+$9** — edge thật nhưng nhỏ (~17 wool/seed) |

**Kết luận chính: H1 "Milk Printer" (+$40-80K kỳ vọng) KHÔNG chuyển được vào
mirror V45.** Mọi macro-lever đều nằm trong khoảng neutral→âm. Chuỗi v19.4
đã tối ưu gần sát biên của những gì market-micro có thể bòn trong mirror này.

## 1. THỰC NGHIỆM 1 — Thị trường MILK của mirror là glut vĩnh viễn

Probe 8 seed (giá MILK tại step 0/96/192/336/480/624/718):

| seed | milk shops | quỹ đạo giá MILK |
|---|---|---|
| 2 | 1 (ICE_CREAM) | 160→177→185→**17→9→1→1** |
| 3 | 2 (ICE+SMOOTHIE) | 160→177→185→**13→28→91→141** (hồi phục!) |
| 4 | 1 | 160→187→214→152→**11→13→1** |
| 5 | 1 (PIZZA) | 160→177→185→**13→5→26→9** |
| 6 | 1 | 160→177→199→114→**11→15→1** |
| 7 | 1 | 160→187→214→152→**24→28→1** |
| 8 | 2 (ICE+PIZZA) | 160→177→185→**76→26→42→13** |
| 9 | 1 | 160→187→214→152→**11→13→1** |

- inv MILK cuối trận ≈ 10.070-10.077 (trên I0 = glut 70-77 units) ở 7/8 seed.
- Nguyên nhân: cả hai tape V45 chạy 6 bò (3 sữa/ngày/bên) + REAPER dump cuối
  game (ngày 27-29) vào drain yếu (1 milk shop 6/8 seed).
- **TFC $250-306 milk tồn tại vì đối thủ TFC không bán sữa** — trong mirror,
  v46 bán sữa mỗi ngày; nhà in sữa của ai cũng bơm vào cùng một cái xả.
- Engine chặn arb mua lại: `BUY_PRODUCT` chỉ hợp lệ cho WHEAT/FERTILIZER
  (L598-601) — không thể mua milk/wool/stra từ market.

## 2. THỰC NGHIỆM 2 — Hiệu ứng "nhường thị trường" (mix-shift = chuyển tiền cho đối thủ)

v21-v3 (COW→SHEEP): margin rơi từ +$1,566 → **−$17,995**. Phân rã:

- Khi ta ngừng sản xuất milk, town drain milk tiếp diễn → giá milk vọt lên
  → v46 (vẫn giữ 6 bò) bán sữa $200-300: v46 được **+$14-20K** (money v46:
  90-92K → 87-120K tùy seed).
- Đồng thời V231 của v46 (đổi SHEEP→COW khi milk≥wool + 2 milk shop) kích
  hoạt — v46 mở rộng đàn bò trên đỉnh giá sữa.
- Phía ta: 12 cừu + 4 wool/ngày đẩy wool supply 6/ngày (2 bên) vs drain
  8-16/ngày → wool mất sâu hơn ở các seed yếu drain.
- **Bài học cấu trúc: thị trường 2 người chơi dùng chung → mỗi item ta rời
  bỏ, đối thủ độc quyền; mỗi item ta dồn vào, ta tự crash.** Mix phải giữ
  nguyên hiện trạng均衡 — mọi cải tiến phải là "thêm tổng giá trị" chứ
  không "dời giá trị".

## 3. THỰC NGHIỆM 3 — Free-rider effect giết sell-discipline (H2)

- v1 (bank+liquidate WOOL/STRA/MELON): giữ hàng qua crash-window → giá hồi
  (town drain) → **đối thủ free-ride**: v46 bán liên tục vào giá cao hơn mà
  ta tạo ra. Dump bank của ta lại tự re-crash thị trường đang hồi phục.
- v2 (trim-only, floor 120): phần lớn wool bị giữ rồi bán ở REAPER cùng mức
  giá với baseline đã bán — net wash + thiệt free-rider (−$307).
- Còn sót lại duy nhất: **lệnh bán rác <$15** (17 wool units/seed trung bình)
  — giữ rồi bán lại ở REAPER $61-120 → +$9/game trung bình (noise).

## 4. CHASSIS v19.4 ĐÃ TỐI ƯU TỚI ĐÂU (đo từ replay seed 5)

- Chassis bán wool chủ yếu ở **h00-h01** — đúng sau consumption bump h0
  (shops step%4==0 + center step%24==0 trùng nhau): tự động "sell-the-bump".
- Các lệnh SELL WOOL $1-$11 giữa ngày (h02-h20) phần lớn là **dead orders**
  (shed không có stock — engine no-op): tape over-ask 8-14u nhưng chỉ bán
  đúng số có. v21-v4 trim dead orders → kết quả y hệt từng đồng.
- REAPER (v19-A1) dump cuối game tận dụng quy tắc **"bán $1 không tăng
  supply"** (L658-660) —_dump glut item ở sàn là free money, không thể cải
  thiện thêm bằng gap-selling (glut item không có gap).
- Wool thực thi 58 units ≈ $19.9K revenue ở seed 5 — engine thị trường wool
  đã được chassis vắt gần kiệt.

## 5. BUG KỸ THUẬT ĐÃ QUẢ (ghi lại cho layer tương lai)

1. **`_V21_STANDARD` vs `_v21_standard`** — NameError nuốt kín trong
   fail-open except 719/719 turn → agent silently = v20. (T ищ traceback
   debug mới lộ.)
2. **Flag `trimmed` chỉ set khi order còn sót units** — order bị xóa hoàn
   toàn (n=0) không kích hoạt rebuild → action gốc trả về nguyên vẹn.
3. **Shed guard `sum(shed) ≥ 85` bị wheat feed-buffer 100 units che mù**
   — guard không bao giờ vượt qua giữa game. Layer banking phải đo áp lực
   theo item, không theo tổng shed.

## 6. ĐƯỜNG ĐI CÒN LẠI (xếp theo prior)

| # | Hướng | Vì sao chưa làm | Prior |
|---|---|---|---|
| 1 | **Goose ladder 5→20** (EGG +$50-100/ngày/con; log-0.2 curve gần như không crash; BAKERY+BRUNCH 8/8 seed) | Cần tape-surgery: BUILD_COOP + PLACE + tending choreography (mini-planner worker-state ~300 dòng) — vượt khả năng layer-wrap | CAO |
| 2 | **PET_CAFE carrot scaling** (giá $63-89 khi PET_CAFE unlock, 2/8 seed) | Tương tự — tape-surgery crop plan | TB |
| 3 | **Deception: pump MILK giá để trigger V231 của v46 đổi cừu thành bò sai lúc** | YARN luôn unlock chặn điều kiện V231 bản V43; cần verify logic v46 riêng | THẤP |
| 4 | Đa dạng hóa đối thủ battery (vs seyit4/aurax7/v43) trước khi tin tưởng bất kỳ lever nào | đã có infra, chỉ cần chạy | CAO (verification) |

**Khuyến nghị deploy: giữ v20.1 (Kaggle #56308666) làm submission chính.**
v21-v5 ≈ v20 trong sai số bootstrap (+$9); không có lý do thay submission
khi chưa có lever thật. Bước đột phá biên độ lớn cần kiến trúc mới (production
planner riêng thay tape), không phải layer thứ 6 trên chuỗi v19.x.
