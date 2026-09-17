# TOP-1 Match Data — Majkel1337 (2 trận gần nhất, tải 2026-09-16)

Nguồn: Kaggle API, submission 56216119 (đang hoạt động, public score 3179.0).
Team Majkel1337 = teamId 16718819, hạng 1 leaderboard (3191.7).

## Các trận
- **match1/** = episode 109776263 (2026-09-16 19:27): `ymg_aq` (p0) vs `Majkel1337` (p1), seed 223111085.
  Kết quả 86,713 vs 86,262 → **Majkel thua 451**. ymg_aq hiện hạng 4 LB.
- **match2/** = episode 109770002 (2026-09-16 19:03): `Majkel1337` (p0) vs `DSM` (p1), seed 771335573.
  Kết quả 91,845 vs 84,129 → **Majkel thắng 7,716**. DSM hiện hạng 3 LB.

## Định dạng dữ liệu (mỗi thư mục match)
Tất cả được sinh bởi `parse_replay.py` — mô phỏng lại lockstep engine với 0 sai lệch tiền
so với replay gốc (verification money match từng bước từng player).

- `summary.json` — tổng quan: đội, seed, kết quả, dòng tiền tổng hợp mỗi player.
- `orders.json` — list mọi market order từng step: `{step, day, player, op, item, asked, units, cash, prices}`.
  - `op`: SELL | BUY_PRODUCT | BUY_SEED | BUY_ANIMAL | HIRE | BUY_LAND
  - `asked` = số lượng yêu cầu; `units` = số thực tế execute; `cash` = tiền thu (+) / chi (−);
    `prices` = giá từng unit (giữ tối đa 3 phần tử đầu với BUY, đầy đủ với SELL).
- `timeline.json` — snapshot từng step mỗi player: money, hands, hires_today, quadrants,
  plants (số cây theo crop), yields (tổng yield_units trên cây), animals, weeds, shed,
  shed_total, seeds, unit_verbs (đếm PLANT/WATER/HARVEST/DROP/PICKUP/PLACE/moves...).
- `daily.json` — tổng hợp theo ngày mỗi player: money_start/end, profit_day,
  buys/sells theo item (units+cash), hire_spend, land_spend, verbs, plants, animals, shed cuối ngày.
  (`money_start`/`profit_day` = số dư cuối ngày trước / chênh lệch money chuẩn; bản trước tối 16-09
  có bug off-by-one bỏ sót giao dịch step đầu ngày — đã sửa + regenerate, cột Δ trong 04A/04B
  được viết lại theo dữ liệu chuẩn.)
- `market.json` — giá + inventory thị trường từng step (shared).
- `town.json` — shop unlock từng step.
- `timeline.csv` — bản CSV gọn của timeline.

## Engine facts (kaggle_environments 1.32.7 — kaggriculture)
- 720 step = 30 ngày × 24 giờ. Tiền cuối = điểm. Bắt đầu $3,000.
- Đất: NW free; mua theo thứ tự NE $1,000 → SW $2,000 → SE $4,000 (mỗi quadrant 5×5, board 10×10).
- HIRE: farm-hand cost = fib(n) với n = số hire trong ngày (1,1,2,3,5,8,13...), reset đầu ngày.
- CROPS (seed, first_yield_day, max_yield, ongoing): WHEAT(10, d2, 6, no), CARROT(20, d2, 4, no),
  TOMATO(50, d8, 4, regrow 1/ngày), STRAWBERRY(100, d10, 4, regrow 2 ngày), MELON(80, d10-12, 6, no).
- ANIMALS (cost, first_yield_day, interval, product): GOOSE(300, d4, 1 ngày, EGG), COW(400, d8, 2 ngày, MILK), SHEEP(500, d6, 3 ngày, WOOL).
- Giá thị trường: price = f(inventory so với I0=10,000). Bán làm inventory tăng → giá giảm;
  mua WHEAT/FERTILIZER làm inventory giảm → giá tăng. Base: WHEAT 25, CARROT 35, TOMATO 60,
  STRAWBERRY 120, MELON 250, EGG 50, MILK 160, WOOL 200, FERTILIZER 100.
- Town tiêu thụ: mỗi shop mở mua sản phẩm của nó mỗi 4 step (shop 1 sản phẩm ×2);
  town center mỗi 24 step mỗi sản phẩm −1. Shop mới mở mỗi 3 ngày (rng theo seed), tối đa 8.
- Nước tưới: cây không được tưới 2 ngày liên tiếp → thành WEED. Ongoing crop cần tưới để +yield.
- Fertilizer: bón cho cây (fertilized_until_day), yield ×2 những ngày được tưới.
- Shed capacity 100 đơn vị. Farmer/hands là các unit di chuyển trên board, HARVEST rồi DROP vào shed, SELL từ shed.
- maxMarketOrdersPerTurn = 10.

## Shop unlocks thực tế 2 trận
- match1 (seed 223111085): d3 FARMERS_MARKET, d6 PIZZA_SHOP, d9 BAKERY, d12 ICE_CREAM_SHOP,
  d15 PIZZA_SHOP(2), d18 BAKERY(2), d21 PET_CAFE, d24 BRUNCH_SPOT.
- match2 (seed 771335573): d3 FARMERS_MARKET, d6 YARN_STORE, d9 PET_CAFE, d12 BAKERY,
  d15 FARMERS_MARKET(2), d18 FARMERS_MARKET(3), d21 BAKERY(2), d24 ICE_CREAM_SHOP.
