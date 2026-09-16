# 01 · V18 BASE ANALYSIS — jaxa623 K0006 (V43 + 4 market micro-edges)

> Task 8-a · Phân tích nghiên cứu (read-only). Ngày: 2026-09-16 (sandbox clock).
> Đối tượng: `/home/z/my-project/kaggriculture/v18.py` — 350.794 bytes, 315 dòng,
> sha256 `4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`.
> Đối chiếu: `/home/z/my-project/kaggle-research/agents/ahmed_v43_main.py` (V43 gốc,
> 3.366 dòng, sha256 `919fc1d61050cd96f799979e49177ae3ac7bce98ec9835724238bea73f4a08ed`).
> Engine đối chiếu: `kaggle_environments==1.32.7` (`envs/kaggriculture/kaggriculture.py`, `_process_market` L544-628).

**Kết luận 1 dòng:** v18 KHÔNG phải một agent mới — nó là **wrapper 315 dòng** bọc
**nguyên văn V43** (nhúng thành 1 dòng byte-string 335.009 ký tự, sha256 khớp tuyệt đối)
rồi thêm đúng 4 can thiệp vào **market list** sau khi V43 đã trả action. Không thay đổi
bất kỳ thứ gì trong farm plan (cây trồng, tưới, thu hoạch, thuê thợ, mua đất).

---

## Mục lục

1. [Cấu trúc tổng thể & entry flow](#1-cấu-trúc-tổng-thể--entry-flow)
2. [Tape/Plan core của V43](#2-tapeplan-core-của-v43)
3. [Triển khai chính xác 4 micro-edges + diff vs V43](#3-triển-khai-chính-xác-4-micro-edges)
4. [Bộ mô phỏng giá `_simulate` — audit độ trung thực vs engine](#4-bộ-mô-phỏng-giá-_simulate--audit-độ-trung-thực-vs-engine)
5. [Tunables (bảng đầy đủ + số dòng)](#5-tunables)
6. [Telemetry](#6-telemetry)
7. [Điểm mở rộng cho v18+ (hook map + top 5)](#7-điểm-mở-rộng-cho-v18)
8. [Phòng thủ trước tình huống lạ](#8-phòng-thủ-trước-tình-huống-lạ)
9. [Probe thực nghiệm (seed 7)](#9-probe-thực-nghiệm-seed-7)
10. [Cảnh báo & rủi ro phát hiện được](#10-cảnh-báo--rủi-ro-phát-hiện-được)

---

## 1. Cấu trúc tổng thể & entry flow

### 1.1 Layout file v18.py (315 dòng)

| Dòng | Nội dung |
|---|---|
| 1-6 | Header attribution (jaxa623/sdy623; nguồn V43, V45; Apache-2.0) |
| 7 | `import math` |
| **9** | `_PARENT_SRC = b'...'` — **toàn bộ V43 nhúng thành MỘT dòng** byte-string 335.009 ký tự (sha256 = ahmed_v43_main.py, đã verify) |
| 10-13 | `exec(compile(...))` vào namespace `_PARENT_NS` → `_PARENT = _PARENT_NS["agent"]` → `del _PARENT_SRC` (giải phóng ~330KB — chính là "trap 2" sys.modules/OOM trong notebook) |
| 14-16 | Hằng số edge: `HORIZON = 24`, `OPEN_UNITS = 50`, `_V43_OPENING` (fingerprint mở màn V43) |
| 19-27 | Class `_Horizons(dict)` + tiêm vào `_PARENT_NS["_R37_HORIZONS"]` — **edge HORIZON-24** |
| 29-182 | **frontload core**: `_MARKET_PARAMS` (46-56), `_shape` (63-74), `_price` (77-85), `_fib` (88-91), `_simulate` (94-143), `frontload()` (146-182) |
| 185-259 | **advance core**: `PREMIUM/PROTECT_FIRST/LOOKAHEAD/MIN_UNITS` (195-198), `advance_sales()` (201-259) |
| 262-315 | **wrapper**: `TELEMETRY` (263), `_future_market()` (266-280), `_standard()` (283-291), `agent()` (294-315) |

**Diff vs V43 gốc:** jaxa623 thêm **314 dòng** (mọi dòng trừ dòng 9 là parent nhúng
nguyên văn). Không xóa/sửa một dòng nào của parent — parent được nhúng byte-exact.
Đây chính là cấu trúc "wrapper-file" mà notebook mô tả (nhưng bản submit là single-file
để tránh trap 1 — kaggle_environments `exec` agent source nên wrapper nạp parent bằng
đường dẫn tương đối sẽ PASS cả trận).

### 1.2 Entry flow `agent()` (v18.py L294-315)

```
agent(observation, configuration)                       # v18.py:294
│
├─ action = _PARENT(observation, configuration)          # L295 — CHẠY TOÀN BỘ V43 TRƯỚC
│    (V43 không bao giờ raise — layer release-guard L1913-1927 bắt tất cả)
│
├─ [try 1] OPEN-50 (L296-303)                            # EDGE 4
│    └─ if action là dict ∧ _standard(cfg) ∧ step==0
│         ∧ action["market"] == _V43_OPENING (so khớp ĐÚNG DANH SÁCH):
│         action["market"] = [["BUY_PRODUCT","WHEAT",50],["SELL","WHEAT",50]]
│       TELEMETRY["open_turns"] += 1 ; lỗi → open_errors, giữ action gốc
│
├─ [try 2] ADVANCE-2 rồi FRONT-LOAD (L304-314)           # EDGE 2 + EDGE 1
│    └─ if action là dict ∧ _standard(cfg):
│         m = list(action["market"])                     # L306-307
│         new = advance_sales(obs, m, _future_market)     # L308 — bán trước 2 turn
│         if len(new) > 1:
│             new = frontload(obs, new, None)             # L310 — xếp lại list
│         if new is not m: action["market"] = new         # L311-312
│       lỗi → wrap_errors, giữ action gốc
│
└─ return action                                          # L315
```

**EDGE 3 (HORIZON-24) không nằm trong `agent()`** — nó được kích hoạt bằng
monkey-patch một lần lúc import (L27): `_PARENT_NS["_R37_HORIZONS"] = _Horizons()`.
Thứ tự các edge trong 1 turn: parent (với horizon 24 đã có hiệu lực bên trong) →
OPEN-50 → ADVANCE-2 → FRONT-LOAD.

### 1.3 Chuỗi layer "củ hành" của V43 (parent, 3.366 dòng)

V43 là ~30 wrapper `agent()` lồng nhau, mỗi layer = một thí nghiệm EXP của Ahmed,
mỗi layer tự bọc try/except và merge telemetry của con. Gọi từ ngoài vào trong:

| # | Layer (dòng def) | Chức năng |
|---|---|---|
| 1 | `agent` L3310 (R148) | **Final**: overflow dawn-cargo rescue (step%24==23) + atomic + config gate + reset telemetry step 0 |
| 2 | `agent` L3174 (R128) | Sale-credit: dùng first SELL để tài trợ mua feed (đây là thứ ADVANCE-2 phải `PROTECT_FIRST`) |
| 3 | `agent` L3025 (R127) | Last-hour grain priority |
| 4 | `agent` L2922 (R124) | Opening seed budget + atomic plant rescue |
| 5 | `agent` L2858 (R97) | Supply guard (grain bảo vệ, prefund, slot) |
| 6 | `agent` L2728 (R95) | Replenishment trim |
| 7 | R88/R86/R85 (L2648-2673) | Feed/fertilizer reserve — animal days GOOSE(4,1) COW(8,2) SHEEP(6,3) |
| 8 | R79/R70/R68/R62 (L2388-2515) | Fertilizer top-up, joint plans, input start |
| 9 | `agent` L2377 (R53) | Labor assignment |
| 10 | `agent` L2334/L2261 (R51) | Warehouse close + input workers (WHEAT/CARROT) |
| 11 | `agent` L2109 (R46) + L2053 (V233) | Sheep commit overlay |
| 12 | `agent` L1913 (release guard) | Bắt mọi exception → PASS — **đảm bảo `_PARENT` không bao giờ raise** |
| 13 | `agent` L1870 (R37) | **Horizon phases** (chỗ `_R37_HORIZONS` sống) + quote-priority reorder sells (step≥288) + R44 probe |
| 14 | `agent` L1706 (R36) | **Sale reservation** (pre-sell trước `horizon` turn trong window 216..696) + `_v224_sales_first` (step≥288) |
| 15 | `agent` L1620 (V231) | Market cap controller (`_V231_CAP=4`) |
| 16 | `agent` L1498 (V31) | `_v224_sales_first` (step≥144): dồn SELL lên trước, lọc order rỗng/qty=0 |
| 17 | `agent` L1468 (V219 timing) | `APPLY_TIMING=False` (tắt) |
| 18 | `agent` L1394 (V219) | Fertilizer builder + hire workers (`_V219_FERTILIZE=True`) |
| 19 | `agent` L1110 (V28) | Room guard giờ 23 (giữ shed ≤ 99) |
| 20 | `agent` L1054 | Terminal planner (64 mô phỏng xác định tại step 712 — "Dmitrii Gluzdov rescue") |
| 21 | `agent` L982 | Terminal rescue step≥718: DROP + SELL toàn bộ projected shed |
| 22 | `agent` L971 | Bọc `_IMPL` = `make_agent(_ROUTES, _router, **_SETTINGS)` |
| 23 | `Chassis.act` L460-504 | **Tape replay**: router → deepcopy tape step → hand_align → weed_repair → sell_lead (chỉ 3 layer bật; budget/room/clamp/dead_stock/terminal_liquidation/front_run = OFF theo `_SETTINGS` L948) |

Ghi chú: `_SETTINGS` (L948) = `{hand_align: T, weed_repair: T, sell_lead: T,
budget_guard: F, room_guard: F, clamp_sells: F, dead_stock: F,
terminal_liquidation: F, front_run: F}` — các layer reactive thô của Chassis đã
tắt, thay bằng các layer "củ hành" tinh vi hơn ở ngoài.

---

## 2. Tape/Plan core của V43

### 2.1 Dữ liệu tape: hardcode hoàn toàn, nén base85+zlib+json

```python
# ahmed_v43_main.py L944-946
_R108_DATA=json.loads(zlib.decompress(base64.b85decode('c-ri}-EL&p(...')))
_ROUTES={int(k):[_R108_DATA['actions'][i] for i in ids] for k,ids in _R108_DATA['routes'].items()}
_R108_SHOP_ROUTES={tuple(r['shops']):r['route'] for r in _R108_DATA['shops']}
```

Số liệu thực đo (giải nén):
- **41 route** (id 0-12 và 100-128, không có 102), **mỗi route đúng 719 step** (0..718).
- **3.982 action dict dùng chung** (dedupe theo index) — nén rất gọn.
- **64 cặp shop** → map route 101-128 (`_R108_SHOP_ROUTES`, EXP240) + 64 cặp cũ
  `_R110_OLD_SHOPS` (L950) → route 0-12 (dòng V39, dùng khi có YARN_STORE).

Tape là **kịch bản đóng hoàn toàn**: farmer/hands/market từng bước đều hardcode —
kể cả `HIRE` đơn lẻ (260 lệnh ở route 0), `BUY_SEED` (189), `SELL` (396),
`BUY_PRODUCT` (65 — chỉ WHEAT/FERTILIZER, đúng ràng buộc engine R36/RULES.md),
`BUY_LAND` (2), `BUY_ANIMAL` (12). Có **45 order rỗng `[]`** rải rác (bắt đầu
step 121) — parent tự lọc từ step 144 nhờ `_v224_sales_first` L1480.

### 2.2 Router — chọn route theo shop (L952-962)

```python
def _router(observation,step,state):
    if step>=144 and not state.get('day6'):          # ngày 6: đọc 2 shop đầu
        shops=tuple((_get(_get(observation,'town',{}),'unlocked_shops',[]) or [])[:2])
        use_new=shops.count('YARN_STORE')<=0
        state['route']=_R108_SHOP_ROUTES.get(shops,100) if use_new else _R110_OLD_SHOPS.get(shops,0)
        state['day6']=True
    if step>=648 and not state.get('day27'):          # ngày 27: ép route 2
        state['route']=2
        state['day27']=True
    return state.get('route',0)
```

### 2.3 Các mốc step quan trọng (tổng hợp cả parent + wrapper)

| Step | Ngày | Diễn biến | Nguồn |
|---|---|---|---|
| 0 | 0 | Tape step 0 bị ghi đè bởi `_R42_OPENING` = `[BUY WHEAT 5, BUY WHEAT 10, SELL WHEAT 60]` (L964-966). v18 thay bằng round-trip 50. | parent L964, v18 L16 |
| 1 | 0 | Tape: mua COW×2, SHEEP×2 + HIRE×5 | tape route 0 |
| 121 | 5 | Order rỗng `[]` đầu tiên xuất hiện trong tape | tape |
| **144** | 6 | **Router đọc 2 shop mở đầu** → chốt route cho cả mùa (64 "worlds" của jaxa623 chính là 64 cặp shop này) | parent L953 |
| 216-287 | 9-11 | Window `_r36_reserve` bật nhưng horizon còn 2 (native) | parent L1663 |
| **288** | 12 | Horizon=4 bật (EXP179) → v18 biến thành 24 | parent L1892 |
| 336-647 | 14-26 | Cửa sổ adaptive horizon-3 (similarity ≥ .90, streak ≥ 6) + R44 probe | parent L1881-1889 |
| **648** | 27 | Router ép route 2 (endgame tape chung) | parent L959 |
| 695 | 28 | Tape bắt đầu SELL qty=1000 (cap = "bán hết") | tape |
| 696 | 29 | Hết window reservation (r36/r37 đều `< 696`) | parent L1663/1892 |
| 712 | 29 | Terminal planner chạy 64 mô phỏng xác định | parent L1005-1006 |
| 718 | 29 | Terminal rescue: DROP + SELL toàn bộ shed; `LAST_ACT_STEP=718` | parent L985-993 |

### 2.4 Chassis.act — pipeline replay 1 turn (L460-504)

```
chassis.act(obs)
├─ _state(player, step)                 # reset nếu step==0 hoặc step lùi (episode replay)
├─ route = router(obs, step, st)        # fallback route cũ nếu route lạ
├─ action = deepcopy(tape[route][step]) # hoặc PASS_ACTION nếu step ngoài tape
├─ raw = deepcopy(action)               # fallback nếu layer ném lỗi
├─ hand_align → weed_repair → apply_suppression → projected_shed
├─ sell_lead (step%4 != 0: bán trước lot của step sau 1 bước, có suppression)
├─ budget/room/clamp/dead_stock/terminal_liquidation  (OFF)
├─ action["market"] = action["market"][:10]            # cắt 10 order
└─ return action / return raw khi exception (layer_fallbacks += 1)
```

`make_agent` (L910-938) bọc thêm 3 cấp fallback: raw tape → PASS (đệm hands) →
`PASS_ACTION`. **Đây là lý do `_PARENT` của v18 không bao giờ raise.**

---

## 3. Triển khai chính xác 4 micro-edges

### 3.1 EDGE 1 — FRONT-LOAD (v18.py L29-182)

**Hàm chính:** `frontload(obs, market, params=None, telemetry=None)` — L146-182.

**Thuật toán (L154-164):** tách list thành 3 nhóm giữ nguyên thứ tự tương đối:
- **A** = SELL **không phải wash** (wash = có `BUY_PRODUCT` cùng item đứng TRƯỚC nó trong list — L158)
- **B** = `BUY_PRODUCT` + các SELL wash
- **C** = còn lại (HIRE, BUY_SEED, BUY_LAND, BUY_ANIMAL)

`new = A + B + C` (L164). Nếu `new == orders` → trả list gốc (L165).

**Cổng an toàn (L166-179) — "per-unit simulation":**

```python
me = int(obs["player"]); farm = obs["farms"][me]; private = obs["private"]   # L167
money = float(farm["money"]); shed_total = sum(int(v) for v in private["shed"].values())
inv = {k: int(v) for k, v in obs["market"]["inventory"].items()}
hires_today = int(farm.get("hires_today", 0)); n_land_extra = max(0, len(farm.get("unlocked_quadrants", ["NW"])) - 1)
for pressure in (0, 1):                                                      # L172 — solo + lockstep
    ok_old, _ = _simulate(orders, ...pressure)
    ok_new, _ = _simulate(new, ...pressure)
    if not ok_old or not ok_new:
        telemetry["frontload_declined"] += 1                                 # L176
        return market
```

`pressure=1` làm mỗi unit buy/sell dịch thêm 1 đơn vị inventory (L122/129:
`inv[item] += 1 + opp_pressure`) — mô phỏng đối thủ chạy lockstep cùng chỉ số.
**Cả hai list phải execute ĐỦ 100% ở cả 2 chế độ** — nếu không, giữ nguyên list gốc.
Không thêm/xóa/resize order — chỉ đổi thứ tự.

**Tại sao có lợi:** engine settle lockstep theo index (xem §4) — SELL đứng trước
được báo giá TRƯỚC cú glut của đối thủ; BUY_PRODUCT đứng sau SELL wash không tự làm
đắt đơn của mình (cùng index được báo cùng inventory).

### 3.2 EDGE 2 — ADVANCE-2 (v18.py L185-259)

**Hàm chính:** `advance_sales(obs, market, future_market, telemetry=None, max_orders=10, items=PREMIUM)` — L201-259.
**Hằng số:** `LOOKAHEAD = 2` (L197), `MIN_UNITS = 1` (L198), `PROTECT_FIRST = True` (L196),
`PREMIUM = ("STRAWBERRY","WOOL","EGG","MILK","MELON","CARROT","TOMATO")` (L195) —
thuần cash product, loại WHEAT (feed) và FERTILIZER (đầu vào).

**Luồng:**
1. Bỏ qua dawn turn `step % 24 == 23` và `step >= 718` (L206) — dawn là chỗ layer
   R148 của parent kiểm hợp đồng shed (xem §3.6).
2. Đọc tape tương lai qua `_future_market(obs, off)` cho off = 1..2 (L209-212) —
   lấy thẳng `impl.chassis.routes[route][step].get("market")` (L278).
3. Gom `want[item]` = tổng qty SELL của item thuộc PREMIUM trong 2 turn tới (L220-223),
   **trừ item của SELL đầu tiên trong danh sách tương lai** (`protected`, L218-219).
4. `avail = shed[item] - đang_bán_turn_này` → `n = min(want, avail)`; `n < MIN_UNITS` bỏ qua (L235-237).
5. **Merge vào SELL cùng item có sẵn** (tăng cap: `hit[2] += n`) hoặc prepend
   `["SELL", item, n]` (L240-244).
6. Vượt `max_orders=10` → cắt phần thừa, đếm `advance_declined_full` (L245-249).

**Cơ sở an toàn:** SELL trong engine là **cap** (bán tối đa n từ shed — engine
L653-660), nên việc bán sớm KHÔNG khiến lệnh tape ở t+1 bán âm — nó chỉ bán phần
còn lại. Notebook: "advance_declined_full counts the times the look-ahead refused
because the earlier sale would not have executed in full" — thực tế counter này
chỉ đếm trường hợp cắt bớt do đầy 10 slot (cùng tinh thần từ chối).

### 3.3 EDGE 3 — HORIZON-24 (v18.py L14, L19-27)

```python
HORIZON = 24                                                                  # L14
class _Horizons(dict):
    """The parent reserves (pre-sell) tape sales up to _R37_HORIZONS[player] turns
    ahead (4 in its 288..696 window). .get() answers HORIZON whenever the parent set 4,
    so its own writes still land and the 2/3-turn phases stay native."""
    def get(self, key, default=None):
        v = dict.get(self, key, default)
        return HORIZON if v is not None and v >= 4 else v                      # L24
_PARENT_NS["_R37_HORIZONS"] = _Horizons()                                     # L27 — SAU khi exec parent
```

**Cơ chế đón lỗng cực kỳ tinh:** trong V43, dict `_R37_HORIZONS` chỉ được đọc
bằng `.get()` tại **đúng một chỗ** — `_r36_reserve` L1666:

```python
end=min(695, step+_R37_HORIZONS.get(int(obs['player']),2), (step//72+1)*72-1)
```

Mọi chỗ khác (L1878/1884/1888/1889/1892) đều là **đọc/ghi trực tiếp `[player]`** —
không đi qua `.get()`. Nên subclass chỉ chặn đúng nút đọc của bộ reservation,
còn toàn bộ phase 2/3 turn (adaptive theo similarity ≥ .90, R44 probe) và write
của parent vẫn nguyên bản. Khi parent set 4 (window `288 <= step < 696`, L1892),
`.get()` trả 24 → cửa sổ pre-sell rộng từ 4 lên 24 turn (vẫn bị kẹp `min(695, ...,
hết block 72 turn)`).

Notebook đã sweep: 8 (2-14), 16 (8-8), **24 (optimum)**, 36 (+19 nhưng 10-4-2),
48 (thua mirror) — 24 là đỉnh thật, không phải "càng to càng tốt".

### 3.4 EDGE 4 — OPEN-50 (v18.py L14-16, L296-303)

```python
OPEN_UNITS = 50                                                               # L15
_V43_OPENING = [["BUY_PRODUCT", "WHEAT", 5], ["BUY_PRODUCT", "WHEAT", 10], ["SELL", "WHEAT", 60]]  # L16
...
if (isinstance(action, dict) and _standard(configuration)
        and int(observation["step"]) == 0
        and action.get("market") == _V43_OPENING):                            # L299 — SO KHỚP CHÍNH XÁC
    action = dict(action)
    action["market"] = [["BUY_PRODUCT", "WHEAT", OPEN_UNITS], ["SELL", "WHEAT", OPEN_UNITS]]      # L300
```

Điều kiện kích hoạt: action market step-0 phải **bằng đúng** opening 3 lệnh của
V43 (`==` trên list — so cả thứ tự lẫn giá trị). Nếu parent thay đổi opening →
edge tự tắt (provably-inert). Sweep của jaxa623: n=50 nằm giữa plateau 25-50,
cách vách đá dưới (~10) một khoảng an toàn; 85+ tự hại.

### 3.5 Tổng kết diff vs V43

| Thành phần | Số dòng | Vị trí |
|---|---|---|
| Header + load parent + del | 13 | L1-13 |
| HORIZON-24 (hằng số + class + tiêm) | 14 | L14-27 |
| FRONT-LOAD core (params giá + sim + hàm) | 154 | L29-182 |
| ADVANCE-2 core | 75 | L185-259 |
| Wrapper (telemetry + future + standard + agent) | 54 | L262-315 |
| **Tổng code jaxa623 thêm** | **~310 dòng** | (không xóa/sửa dòng nào của parent) |

### 3.6 Tương tác giữa các edge và với parent (điểm tinh tế nhất)

1. **OPEN-50 không bị FRONT-LOAD phá:** ở step 0, list `[BUY WHEAT 50, SELL WHEAT 50]`
   — SELL là wash (có BUY cùng item trước nó) → vào nhóm B → `new == orders` →
   frontload trả về nguyên list (L165).
2. **ADVANCE-2 → FRONT-LOAD nối tiếp** (L308-310): sells advance được prepend,
   sau đó frontload đẩy chúng lên đầu nhóm A — đúng ý đồ "bán sớm nhất có thể".
3. **`PROTECT_FIRST` bảo vệ R128 sale-credit:** parent's `_r128_sale_credit`
   (L3057-3065) tính doanh thu của **order đầu tiên** của turn khi là SELL non-wheat
   để tài trợ mua feed. Advance item đó sớm sẽ rút cạn shed ở t+1 → credit giảm →
   feed purchase thất bại. Nên item của SELL đầu trong cửa sổ tương lai được miễn.
4. **Bỏ dawn turn (step%24==23):** R148 `_r148_overflow` (L3206-3241) bán bớt
   cargo sẽ bị vứt lúc nửa đêm và **kiểm hợp đồng** shed đầu giờ sau
   (`_R148_PENDING` + `_r148_same_stock` L3317-3320). Advance ở dawn sẽ làm
   contract check báo lỗi → bị cấm.
5. **Horizon-24 nằm BÊN TRONG parent** nên các cơ chế nợ (`r36_debts` — suppression
   của R36 L1648-1655) vẫn hoạt động: lượng đã pre-sell sẽ bị trừ khỏi SELL của
   ngày đúng hạn, không bán двой.

---

## 4. Bộ mô phỏng giá `_simulate` — audit độ trung thực vs engine

`_simulate` (v18 L94-143) tái hiện settlement per-unit của engine
(`kaggriculture.py::_process_market` L544-628 + `_commit_unit` L652-694):

| Quy tắc | Engine | `_simulate` | Khớp |
|---|---|---|---|
| Lockstep theo index list | `for i in range(max_len)` L563 | mô phỏng solo + `opp_pressure` | ✅ (xấp xỉ đối thủ bằng +1 inventory/unit) |
| HIRE/BUY_LAND atomic, theo thứ tự player, tại vị trí index của chúng | L571-581 | xử lý tại vị trí trong list, cost `_fib(hires_today)` | ✅ |
| SELL: từ shed, `money += price`, inventory +1 **chỉ khi price > 1** | L653-661 | L117-123 | ✅ |
| BUY_PRODUCT: chỉ WHEAT/FERTILIZER, **quote tại inventory-1**, chặn khi shed ≥ 100 | L598-601, L662-672 | L124-129 | ✅ |
| BUY_SEED: trừ tiền theo từng unit, không chạm inventory/shed | L673-678 | L130-134 (gộp lump-sum = tương đương) | ✅ |
| BUY_ANIMAL: per-unit, shed check | L679+ | L135-140 | ✅ |
| Order fail 1 unit → chết cả order, không retry | L622-623 | `return False` ngay | ✅ |
| Cắt 10 order/turn | L560 `q[:max_orders]` | ngầm (gate ở advance max_orders) | ✅ |
| Mô hình giá (9 sản phẩm: base/I0/T/shape/targets, floor 1, hinge gain 8) | `market_price` | `_MARKET_PARAMS` L46-56 copy từ `_R37_MARKET_PARAMS` của parent L1730 | ✅ (parent tự verify sẵn) |

Điểm khác duy nhất: `_ANIMAL_COST` của wrapper có thêm `CHICKEN: 150` (L59) mà
parent không có — vô hại (tape không mua CHICKEN; thừa key chỉ khiến sim từ chối
nhanh hơn nếu gặp item lạ).

---

## 5. Tunables

### 5.1 Wrapper v18.py (4 edges)

| Tên | Giá trị | Dòng | Ý nghĩa |
|---|---|---|---|
| `HORIZON` | **24** | 14 | Edge 3 — sale-reservation horizon (V43 native 4; sweep: 8 thua, 16 hòa, 24 opt, 36/48 thua) |
| `OPEN_UNITS` | **50** | 15 | Edge 4 — size round trip step-0 (plateau 25-50; vách đá <10; 85+ tự hại) |
| `_V43_OPENING` | fingerprint 3 lệnh | 16 | Trigger OPEN-50 (so khớp chính xác) |
| ngưỡng `v >= 4` trong `_Horizons.get` | 4 | 24 | Chỉ override khi parent vào phase 4-turn (288..696) |
| `PREMIUM` | 7 items | 195 | Items được phép advance (loại WHEAT/FERT) |
| `PROTECT_FIRST` | True | 196 | Bảo vệ item SELL đầu của turn tương lai (khỏi phá R128 credit) |
| `LOOKAHEAD` | **2** | 197 | Edge 2 — số turn nhìn trước (1 = chỉ turn kế) |
| `MIN_UNITS` | 1 | 198 | Ngưỡng advance tối thiểu |
| `max_orders` (tham số advance_sales) | 10 | 201 | Giới hạn slot — vượt thì cắt + đếm declined_full |
| `opp_pressure` sweep | (0, 1) | 172 | Hai chế độ mô phỏng solo + lockstep |
| gate `len(market) < 2` | 2 | 148 | Frontload bỏ qua list quá ngắn |
| skip dawn/ends | step%24==23, ≥718 | 206 | Advance bỏ dawn turn + 2 turn cuối |
| `_MARKET_PARAMS` | 9 sản phẩm | 46-56 | Mirror mô hình giá engine |
| `_MARKET_I0/_PRICE_FLOOR/_HINGE_GAIN` | 10000/1/8.0 | 43-45 | Tham số giá |
| `_standard` gate | board 10, tpd 24, shed 100, maxOrd 10, farmHandMult 1, marketParams rỗng | 286-288 | Tắt toàn bộ 4 edge nếu config lạ |

### 5.2 Parent V43 — các núm quan trọng nhất

| Tên | Giá trị | Dòng (ahmed_v43_main.py) | Ý nghĩa |
|---|---|---|---|
| `DEFAULT_SETTINGS` tunables | block_turns 72, shed_capacity 100, max_orders 10, turns_per_day 24, min_sell_price 2 | 274-279 | Nòng cốt Chassis |
| `_SETTINGS` | sell_lead ON, 6 layer reactive OFF | 948 | Cấu hình layer |
| Router mốc | 144 (chọn route theo shop), 648 (ép route 2) | 953/959 | Bắt buộc đúng với `_future_market` của wrapper |
| `_R42_OPENING` | [BUY 5, BUY 10, SELL 60] | 964 | Opening bị OPEN-50 thay |
| `MAX_ORDERS` | 10 | 1216 | |
| `CROP_MIN_PRICE` | 70 | 1222 | Ngưỡng V219 |
| `_V219_FERTILIZE` | True | 1227 | Cờ ablation fertilizer builder |
| `APPLY_TIMING` | False | 1461 | Layer timing tắt |
| `_V231_CAP` | 4 | 1526 | Cap controller mua lớn |
| Window `_r36_reserve` | 216 ≤ step < 696, end clamp theo block 72 | 1645/1663/1666 | Nơi horizon có hiệu lực |
| R37 adaptive | similarity ≥ .90, streak ≥ 6, window 336..648, probe ≥ 100 | 1842-1892 | Phase horizon 3 |
| Phase horizon 4 | 288 ≤ step < 696 | 1892 | Nút bị `_Horizons` đón lỗng |
| `_R37_ADAPTIVE/_R37_QUOTE` | True/True | 1859-1860 | Công tắc layer R37 |
| batch stress quote | min(24, max(8, standing)) | 1801 | Quote priority |
| `_R51_INPUT_MAX_WORKERS` | 2 | 2127 | |
| `_R51_INPUT_CROPS` | WHEAT (2,4,6), CARROT (2,3,4) | 2128 | |
| `_R85_FEED/_R85_FERT` | True/True | 2519-2520 | |
| `_R88_ANIMAL_DAYS` | GOOSE(4,1) COW(8,2) SHEEP(6,3) | 2650 | |
| `_R148_OVERFLOW/_R148_SEEDS` | True/**False** | 3193-3194 | `_R148_SEEDS=False` — slot edge chưa bật |

---

## 6. Telemetry

### 6.1 Wrapper — `TELEMETRY = {}` (v18 L263)

| Key | Tăng khi | Dòng |
|---|---|---|
| `open_turns` | OPEN-50 áp dụng thành công | 301 |
| `open_errors` | exception khối opening | 303 |
| `advance_turns` / `advance_units` | có advance / số unit bán sớm | 253-254 |
| `advance_declined_full` | không đủ slot 10 order → cắt bớt | 249 |
| `advance_errors` | exception trong advance | 258 |
| `frontload_turns` | reorder được duyệt qua 2 mô phỏng | 181 |
| `frontload_declined` | mô phỏng nói list reorder sẽ fail | 176 |
| `wrap_errors` | exception khối wrap chính | 314 |

**Cách đọc:** dict module-level — harness import module rồi đọc thuộc tính
`v18.TELEMETRY` sau khi chạy trận (không ghi file, không in ra). Lưu ý:
**wrapper không reset TELEMETRY ở step 0** (khác parent — mọi layer parent reset
khi `step==0` hoặc `step<=last_step`). Chạy nhiều trận trong 1 process → counter
cộng dồn; harness phải tự snapshot delta từng trận. `advance_declined_full` còn
được notebook nhắc: "counts the times the look-ahead refused because the earlier
sale would not have executed in full."

### 6.2 Parent — chuỗi `agent.telemetry`

Mỗi layer có report dict riêng và merge của con (`_R148_REPORT.update(getattr(_R148_PARENT,'telemetry',{}))` L3326) → `v18._PARENT.telemetry` là **bảng 142 key** đầy đủ (đo thực tế: `sale_reserved_units`, `sale_reservations`, `reordered_market_turns`, `overflow_turns`, `input_confirmed_hires`, `feed_skips`, `cattle_confirmed`...). Đây là nguồn chẩn đoán chính khi debug hành vi parent.

---

## 7. Điểm mở rộng cho v18+

### 7.1 Hook map — chỗ an toàn để thêm code

| Hook | Cách dùng | Rủi ro |
|---|---|---|
| **H1. Try-block của `agent()`** (L304-314) | Thêm overlay thứ 3 sau `advance_sales`/`frontload` — đúng pattern đã chứng minh: gate → thử → sim duyệt → telemetry → fallback | Thấp — mọi exception bị bắt, action gốc được trả về |
| **H2. `_PARENT_NS` injection** (kiểu L27) | Patch global của parent TRƯỚC turn đầu: `_R37_QUOTE` (tắt reorder SELL của parent cho khỏi chồng với frontload), `_R148_SEEDS=True` (slot chưa bật), `_V219_FERTILIZE`, monkeypatch `Chassis._sell_lead` (parent tự làm thế ở L1657-1658) | Trung bình — phải hiểu ngữ cảnh đọc/ghi từng global |
| **H3. API `_future_market`/`chassis.routes`** | Đọc toàn bộ plan tương lai (719 step của route đang chạy) → overlay có thể nhìn xa hơn 2 turn (ví dụ phát hiện overstock sắp tràn shed) | Thấp (chỉ đọc) |
| **H4. Fingerprint mở màn** (kiểu L299) | Pattern "so khớp chính xác output parent → thay bằng bản đã verify" mở rộng cho các mốc khác (step 1, step 648...) | Thấp — mismatch thì tự no-op |
| **H5. `_simulate` làm oracle chung** | Bất kỳ overlay mới nào dựng market list candidate → bắt buộc `_simulate(ok) under pressure (0,1)` như frontload — đây là "máy chứng minh inert" dùng lại được | Thấp |

### 7.2 Cơ chế "provably-inert" đã có trong code

1. OPEN-50: chỉ kích hoạt khi `action["market"] == _V43_OPENING` **chính xác** (L299).
2. FRONT-LOAD: dual-simulation (solo + lockstep) của **cả list cũ lẫn list mới** —
   list cũ fail cũng từ chối (kẹt trong trạng thái đã biết) (L172-177).
3. ADVANCE-2: dựa trên **cap semantics** của SELL — không thể bán âm/oversell;
   merge thay vì thêm order khi có thể.
4. `_standard()`: mọi edge tắt hoàn toàn nếu configuration khác engine chuẩn.
5. Mọi khối bọc try/except với counter lỗi + trả action gốc.
6. `del _PARENT_SRC` (L13) — vệ sinh bộ nhớ (chống trap OOM của notebook).

### 7.3 Top 5 hướng mở rộng (theo thứ tự giá trị/rủi ro)

1. **Tắt `_R37_QUOTE` khi frontload hoạt động** (H2): parent vẫn reorder SELL
   theo quote-priority (L1895-1897) rồi wrapper reorder lại theo A/B/C — hai lần
   sort có thể phá nhau. A/B: đo 64-worlds CI.
2. **Bật `_R148_SEEDS=True`** (H2): slot seed-prefund đã có code sẵn trong parent
   (L3270+) nhưng cờ False — edge "miễn phí" chưa từng được sweep.
3. **ADVANCE-2 thông minh hơn** (H1+H3): lookahead 2 → động (đọc `chassis.routes`
   xa hơn khi giá cao, gần hơn khi giá thấp); thêm gate giá (`view.prices` đã có).
4. **OPEN attack tổng quát hoá có điều kiện**: notebook đã chứng minh lặp attack
   mọi turn THUA (0-16) vì giữa mùa đối thủ dư tiền — nhưng biến thể "chỉ attack
   khi phát hiện đối thủ y như V43-family qua `_r37_similarity`" chưa ai thử.
5. **Telemetry per-game + export**: cho wrapper reset TELEMETRY ở step 0 (một dòng
   `if int(observation["step"])==0: TELEMETRY.clear()`) và ghi JSONL ra bench —
   hạ chi phí đo lường cho mọi thí nghiệm sau.

---

## 8. Phòng thủ trước tình huống lạ

**Wrapper (v18):**
- `_standard(configuration)` (L283-291): `configuration=None` → coi như chuẩn
(harness không truyền config); thiếu key → default; sai 1 giá trị → tắt hết 4 edge.
Đặc biệt từ chối khi `marketParams` khác rỗng — tức mô hình giá engine bị đổi thì
bộ sim của wrapper vô hiệu → an toàn.
- Mọi truy cập obs nằm trong try/except; `frontload` có try/except riêng bên trong
hàm (L166-179); `advance_sales` toàn thân trong try (L204-259); `_future_market`
try/except → None (L268-280).
- OPEN-50 chỉ đụng dict action đã là `dict`; so khớp fingerprint trước khi thay.

**Parent (V43) — nhiều tầng:**
- `make_agent` (L910-938): 3 cấp fallback không bao giờ raise.
- Mỗi layer onion: try/except + trả kết quả parent + counter lỗi riêng.
- `_get`/`_int` (L284-298): đọc field cho cả dict lẫn Kaggle Struct (attribute);
thiếu field → default.
- `_step_of` (L308-312): thiếu `step` → tính từ `day*24+hour`.
- `Chassis.act` raise ValueError khi obs thiếu farms (L461-462) → factory bắt → fallback tape.
- State per-player + reset khi `step==0` hoặc `step <= last_step` (L427-434) —
   sống sót qua episode replay trong cùng process.
- Gate "standard config" lặp lại ở R36 (L1711), R51-warehouse (L2338), R95 (L2733), R148 (L3321).
- Không hề đọc đối thủ ngoài public fields: `_r37_similarity` dùng tiles công khai;
notebook ghi rõ "no private rival inventory" (R44 probe cũng chỉ đo money công khai).

---

## 9. Probe thực nghiệm (seed 7)

Chạy trực tiếp trên engine thật (`kaggle_environments.make("kaggriculture")`,
seed 7, v18 seat 0 vs ahmedv43 seat 1, script /tmp/v18probe/probe.py):

- Trận đủ 720 step, wall time **8.5s**, status DONE/DONE — không error, không slow turn.
- Kết quả: **v18 thắng 102.381 vs 100.779 (+1.602)** — cùng bậc magnitude với
  +1.282 (24 seeds × 2 seat) mà notebook đo.
- `v18.TELEMETRY` = `{"open_turns": 1, "frontload_turns": 22, "advance_turns": 10,
  "advance_units": 22, "advance_declined_full": 5}` — **cả 3 edge động đều hoạt động,
  0 error counter** (không có key open_errors/wrap_errors/advance_errors/frontload_declined).
- Step 0 action của v18 (env.steps[1][0].action): `[["BUY_PRODUCT","WHEAT",50],
  ["SELL","WHEAT",50]]` — OPEN-50 đúng như thiết kế.
- Ví dụ frontload (step ~96): v18 `[SELL FERTILIZER 1, HIRE×4]` vs v43 `[HIRE×4,
  SELL FERTILIZER 1]` — cùng đơn, khác thứ tự.
- Parent telemetry 142 key: `sale_reserved_units=253, sale_reservations=45` (horizon
  24 đang pre-sell mạnh), `reordered_market_turns=105` (v224 sales-first),
  `overflow_turns=2, overflow_units_reclaimed=8`...

---

## 10. Cảnh báo & rủi ro phát hiện được

1. **TELEMETRY không reset theo game** (L263): cộng dồn cross-episode trong 1
   process. Harness đo nhiều trận phải tự snapshot delta (notebook của jaxa623
   load agent fresh mỗi world một phần cũng vì kiểu này).
2. **Order rỗng `[]` trong tape** (45 cái ở route 0, từ step 121): trước step 144
   parent chưa lọc (`_v224_sales_first` chỉ chạy step≥144) → frontload gặp list
   có order rỗng sẽ **im lặng no-op** (check `len(orders) != len(market)` L150 —
   không qua counter). Vô hại nhưng làm số frontload_turns thấp hơn tiềm năng.
3. **`_future_market` tin route hiện tại là route tương lai** (trước 144 route=0;
   sau 144 route shop — đúng; ≥648 ép 2 — sao chép đúng logic `_r128_future`
   L3053-3055 của parent). Nếu sau này đổi router, phải đổi cả 2 chỗ.
4. **Wash-detection của frontload chỉ nhìn BUY_PRODUCT đứng trước trong cùng
   list** (L158) — không nhìn cross-turn. Đúng cho mục đích reorder (an toàn).
5. **Sim BUY_SEED gộp lump-sum** (L130-134) trong khi engine trừ per-unit —
   tương đương về tiền, chỉ khác khi tiền vừa vặn cạn giữa chừng list có many seed
   orders — đều fail → cùng kết luận decline. Không thấy lỗ hổng.
6. **`_ANIMAL_COST` wrapper có CHICKEN, parent không** — vô hại (thừa key).
7. **Kaggle runner exec's agent source** (trap 1 của notebook): v18 an toàn vì
   single-file tự chứa; nhưng mọi biến thể v18+ phải luôn package single-file,
   không dùng wrapper nạp file tương đối.

---

*Tài liệu liên quan: `jaxa623_markdown.md` (notebook gốc), `agents/v43_notes.md`,
`RULES.md` (R20 fib hire, R36 BUY_PRODUCT, R65 kho đầy, R67 shed/atomic).*
