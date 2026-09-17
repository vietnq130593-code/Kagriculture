# PHÂN TÍCH: boatlee (V14 Clone Preemption → V16-RC2 Market Relay → V29-R1 Adaptive Hysteresis) + thomastschinkel (Public State Router v3.1 74.5% → v5 93.8%)

> Task 74-b · Research only. Nguồn: `research/kaggle_dl/` 5 notebook + md mô tả; toàn bộ cơ chế dưới đây được trích xuất trực tiếp từ code agent (đã giải nén payload b85/zlib/b64).
> Bối cảnh champion ta: **v15** = kme3v10 base + 6 tầng tuning v13 (H=8, V224, V231-flip, prefire h21/22, melon-seller, PREDUMP tắt) + front_run-sync + room_guard + clamp_sells + **R90 shed-animal watchdog**.

---

## 0. TÓM TẮT 1 CÂU

Cả boatlee và thomastschinkel đều chơi **tape cố định 719 turn** (replay reconstruction từ top ladder submissions) + các **lớp mỏng reactive chỉ đụng market order queue**; 3 kỹ thuật đáng giá nhất public meta là: (1) **clone-distance gate** công thức chuẩn hóa khoảng cách 2 farm từ public state (boatlee V14, ngưỡng ≤6, trigger shift-1-turn + repay), (2) **public-state router** chuyển tape theo block 6 ngày bằng decision-tree trên 100 feature công khai (thomast v5, 93.8% trên 44k trận), (3) **adaptive market hysteresis** — EMA áp lực nguồn cung đối thủ từ Δpublic inventory + mirror-latch tắt hẳn layer adaptive khi 2 farm gần trùng nhau (boatlee V29-R1). Cả ba đều xác nhận trực tiếp các định luật ta đã tự rút ra (L38 knife-edge, L33 A/B từng layer, L31 valve surgical).

---

## 1. BẢNG SO SÁNH TỔNG QUAN

| Khía cạnh | boatlee V14 (84/84) | boatlee V16-RC2 (relay) | boatlee V16-RC5 (313 votes) | boatlee V29-R1 | thomast v3.1 (74.5%) | thomast v5 (93.8%) |
|---|---|---|---|---|---|---|
| **Tape gốc** | Kakuteki `55334137`, audit 4 episode 2876/2876 bước trùng | Kakuteki rebalance + legacy (2 tape, chọn theo `townCenterSellInterval`) | Nikita Lugovoy `55440039`, majority-vote 3 trace (field 100% trùng, market 99.91%) → **8 COW / 4 SHEEP** | RngRng `55948382` (3 quadrant) | 1 main + 3 tail (lưu delta prefix) | 5 tape top ladder, opening giống nhau (chỉ lệch qty market bước 1-10) |
| **Kiểu architecture** | Tape + 5 layer reactive | Tape + yarn-switch + wool controller + relay FERTILIZER | Tape + weed repair + front-run premium | Tape + weed repair + adaptive market | Tape + router 3 mốc + 3 repair | Tape + router 5 block (GBDT-style tree) |
| **Chống mirror** | **Clone-distance ≤6** → shift SELL premium sớm 1 turn + repay | 3 checkpoint (216/240/264) cùng pass → lock → bán FERTILIZER sớm 3 turn | Không gate (front-run vô điều kiện theo demand turn) | **Mirror latch**: composition ≤2 + hands + quadrants + |Δmoney| ≤250 → **max_extra=0 (tắt layer)** | Router phản ứng state công khai (không phải mirror-specific) | Router theo block 6 ngày |
| **WEED repair** | Actor-local DIG + replay intended + 8-step catch-up từ tape | Như V14 | Như V14 | Như V14 | `_noop` predicate chính xác engine → DIG khi action chắc chắn bị ignore | **Không có** (ablation: chỉ +1 win) |
| **Endgame** | Terminal liquidation từ step 716 theo `_LIQUIDATION_ORDER` | Trong tape | Trong tape | Reserve→0 + tail tranche từ 684/704 | `dead_stock`: bán phần route sẽ không bao giờ bán; day≥29 bán hết; **SELL qty 1.000.000 ở 716-718** (engine tự kẹp bằng shed) | Trong tape (SELL 1e6) |
| **Số liệu tự báo** | 84/84 vs base+6 public; Ueddy 48-0; CemBas 48-0; **Seb 4-44; wangtf96 4-8** | V27 panel paired 1/11/0 → **12/0/0**; C71 +25 coin; panel khác 0 delta | 60/60 vs core; 30 seed × 2 seat | 106/0/2 (108 game, mean +23.3k); top-20 reps 196/0/20; 8 loss-family 91/0/5 | HOLD 74.5%; vs top-4 route 66.3% | **44,096 game: 93.76%**; stress 256 seed 93.85% |
| **Tốn runtime** | ~0 (stdlib + obs) | ~0 | ~0 | ~0 | ~0 (future_sells precompute) | ~0 |

Điểm chung cốt lõi: **không ai search/planner online** — "offline routes solve the hard logistics that online planners struggle with" (thomast). Toàn bộ sự sống còn của tape = **weed repair + hand align + regime detection**. Camera đo lường: paired-seat (đổi ghế cộng margin), hash-lock artifact, frozen seed.

---

## 2. CLONE PREEMPTION CỦA BOATLEE V14 (84/84) — CƠ CHẾ MÃ NGUỒN ĐẦY ĐỦ

### 2.1. Signature công khai của 1 farm

```python
def _public_signature(farm):
    keys = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON",
            "COW","SHEEP","GOOSE","PASTURE","COOP","WEED")
    counts = {key: 0 for key in keys}
    for row in farm.tiles:                       # quét TOÀN BỘ ô của farm
        for tile in row:
            for field in ("crop", "animal", "kind"):   # 1 tile đếm 1 lần (break)
                if str(tile[field]).upper() in counts: counts[...] += 1; break
    return (len(farm.hands),                      # [0] số lao động
            len(farm.unlocked_quadrants),         # [1] số quadrant mở
            tuple(counts[k] for k in sorted(counts)))  # [2] vector 11 loại ô

def _clone_distance(obs):
    left, right = _public_signature(obs.farms[0]), _public_signature(obs.farms[1])
    return (abs(left[0]-right[0])                 # Δhands   trọng số 1
          + 3*abs(left[1]-right[1])               # Δquadrant trọng số 3
          + sum(abs(a-b) for a,b in zip(left[2], right[2])))  # Σ|Δ11 loại ô| trọng số 1
```

**Ngưỡng**: `_PREEMPT_MAX_CLONE_DISTANCE = 6` — gọi là "near clone" khi distance ≤ 6. (RC2 nới thành 8 nhưng yêu cầu 3 checkpoint liên tiếp cùng pass — xem §4.)

### 2.2. Luồng agent (thứ tự layer cố định — "order-safe")

```python
def agent(obs):
    step = clamp(obs.step, 0, len(_ACTIONS)-1)
    action = _weed_repair_action(obs, _copy_action(_ACTIONS[step]), step)  # 1. tape + weed fix
    action = _repay_shift(obs, action, step)        # 2. trả nợ turn trước
    action = _rank_sell_slots(obs, action, None)    # 3. xếp lại SELL cùng turn theo impact
    action = _preempt_shift(obs, action, step)      # 4. preemption (nếu clone)
    action = _terminal_liquidation(obs, action, step)  # 5. dọn shed từ step 716
    return _align_hands(action, os)
```

### 2.3. Preemption shift (phần quý nhất)

```python
_PREEMPT_ENABLED = True
_PREEMPT_FRACTION = 2.0          # cho phép shift tối đa 2× lượng turn sau (thực tế bị min khác kẹp)
_PREEMPT_MAX_BATCH = 30          # tối đa 30 units / lần shift
_PREEMPT_MIN_FUTURE_QUANTITY = 4 # chỉ shift khi turn sau định bán ≥4
_PREEMPT_START, _PREEMPT_STOP = 120, 680   # chỉ hoạt động giữa mùa
_PREEMPT_MIN_PRICE_RATIO = 0.0  # price gate tắt (giá bao nhiêu cũng bán)
_PREMIUM = ("STRAWBERRY", "MELON", "MILK", "WOOL")

def _preempt_shift(obs, action, step):
    if not (120 <= step < 680): return action
    state = _shift_state(obs, step)
    if state["due"] or _clone_distance(obs) > 6: return action   # ← GATE CLONE
    future = _future_sells(step)          # đọc _ACTIONS[step+1].market SELL của 4 item premium
    if not future: return action
    if len(market) >= 10: return action   # đủ 10 order thì thôi
    remaining = _projected_shed(obs, action)   # shed sau khi trừ DROP/PLACE turn này & SELL đã lên
    for item in _PREMIUM:
        if future[item] < 4: continue
        target = min(remaining[item], future_qty, 30, round(2.0*future_qty))  # ≡ min(shed, plan, 30)
        market.append(["SELL", item, target])
        remaining[item] -= target
    if shifted:
        state["due_step"] = step + 1      # ← NỢ: ghi lại đúng lượng đã shift
        state["due"] = shifted

def _repay_shift(obs, action, step):      # turn sau: khấu trừ đúng lượng đã shift
    if state["due_step"] != step: return action
    for order in action["market"]:
        if order là SELL item đang nợ: order[2] -= due[item]   # xóa order nếu về 0
    state["due_step"], state["due"] = -1, {}
```

**Bất biến 2-turn**: `turn t: SELL s` + `turn t+1: SELL (q−s)` = tổng `q` như kế hoạch — chỉ đổi **thời điểm**, không đổi sản lượng ("order-safe": không vượt lên trước order quý của chính mình ở cùng turn; chỉ đi trước **đợt bán của turn sau** — vốn là lúc đối thủ mirror cũng định bán, nên ta đi trước đợt dump chung 1 turn). Đây chính là "clone preemption" mà raykkretzschmar mô tả +1,865 margin.

`_projected_shed` mô phỏng chính xác DROP/PLACE tại 4 ô shed-access (tâm 2×2 của board) của farmer+hands turn hiện tại (engine xử lý market sau unit action) → không bao giờ bán quá hàng thật có.

### 2.4. Xếp hạng SELL theo price-impact (mượn V23, hard-code đúng engine)

```python
_MARKET_PARAMS = {  # (base, equilibrium, scale, below_shape, below_target, above_shape, above_target)
  "WHEAT":(25,10000,400,"sqrt",0.8,"log",0.2), "CARROT":(35,...,"log",0.2,"sqrt",0.7),
  "TOMATO":(60,...,"linear",0.4,"sqrt",0.6), "STRAWBERRY":(120,...,"sqrt",0.7,"linear",1.6),
  "MELON":(250,...,"log",0.2,"sq",3.6), "EGG":(50,...,"linear",0.4,"log",0.2),
  "MILK":(160,...,"sqrt",0.6,"linear",1.6), "WOOL":(200,...,"log",0.2,"sq",3.2),
  "FERTILIZER":(100,...,"linear",0.4,"linear",0.4)}

def _impact_score(obs, order):   # score = qty × (giá hiện tại − giá sau khi mình đổ qty)
    current_quote = market.prices[item]
    later_quote   = _market_price(item, current_inventory + quantity)   # mô hình phi tuyến
    return quantity * max(0, current_quote - later_quote)

def _order_score(...):           # nhân thêm urgency khi gần chạm trần kho 10000
    excess = max(0, current_inventory + quantity - 10000)
    urgency = min(1, (excess/demand_per_day)/10)
    return impact * (1 + 0.25*urgency)     # demand = shop mở × (24/interval), town center 24
```
→ SELL gây sụt giá lớn nhất / dễ kẹt trần kho được **đưa lên đầu queue** trong cùng 1 turn. Tham số trùng engine thật ta đã đọc ở Task 68 (milk/straw linear-1.6, wool/melon sq-3.2/3.6, egg log-0.2).

### 2.5. Tham số được sweep (5 biến thể, chọn `near_p200_b30`)

`exact_p50_b12` +1548 | `near_p100_b24` +2368 | `near_p200_b30` **+2447 (chọn)** | `near_p50_b12` +1640 | `near_price50` +1842 (mean margin vs dev panel 12 game).

### 2.6. Tính trung thực của boatlee

V14 **thua** Seb 4-44 và wangtf96 4-8 — tức clone-preemption không phải vũ khí toàn năng; nó chỉ tách được nhóm gần-khung (Ueddy/CemBas 48-0).

---

## 3. THOMASTSTSCHINKEL — PUBLIC STATE ROUTER

### 3.1. v3.1 (74.5%) — router 3 mốc + prefix guard + 3 repair

**Router** (chỉ đọc state công khai, KHÔNG seed/KHÔNG biết đối thủ):
```python
DECISIONS = (
    (226, "shop_YARN_STORE", 1,  YARN),         # day 9.4: mở YARN_STORE → đuôi wool
    (360, "px_CARROT",       42, YARN_CARROT),  # day 15: giá CARROT ≥42 (chỉ trong nhánh yarn)
    (433, "inv_MILK",     10067, MILK_GLUT),    # day 18: kho MILK ≥10067 (chỉ nhánh main)
)
```
**Prefix guard** (`_switch_ok`): chỉ được chuyển sang tape mới nếu 2 route **byte-identical mọi turn trước đó** — đảm bảo farm/shed/cash của ta đúng hệ trạng thái mà tape mới được ghi. Thí nghiệm splice không cùng prefix = thảm họa (tape mới tưới/hái ô trống). Tail được lưu dạng `(parent, turn, suffix)` — nén delta.

**3 repair** (mỗi cái phải tự chứng minh +trận trên panel 968 game; tổng +19/−0):
1. **weed_dig**: `_noop(act, tile, inv, ...)` — predicate sao chép đúng `kaggle_environments._apply_unit_action` để biết action nào engine **chắc chắn bỏ qua** (WATER khi đã tưới, HARVEST khi yield=0, PLACE không đủ hàng, MOVE ra ngoài board…). Unit đứng trên WEED + action no-op → thay bằng `DIG`.
2. **clamp_sells**: SELL mà shed (đã cộng DROP/PLACE cùng turn tại 4 ô shed-adjacent) không đủ hàng → **bỏ order**, giải phóng 1/10 slot. Đo được +7/−0 khi có dead_stock cạnh tranh slot.
3. **dead_stock**: tính `future_sells[item][t]` = suffix-sum SELL còn lại của route (precompute) → shed có hàng mà route **không bao giờ bán nữa** → bán ở slot rảnh; day ≥ 29 bán mọi thứ; lọc price > 1; sort theo −price×qty.

**Bị từ chối sau đo** (tổng hợp quan trọng — trùng luật L33 của ta): sells-before-buys **−17 game**, hire-last **−13**, deferring-unaffordable-buys neutral, feed/care/collect trên idle-turn **−4** (tràn shed 100, phần tràn bị vứt).

### 3.2. v5 (93.8%) — 5 tape + 5 decision tree, block 6 ngày, CỨNG SẠCH

```python
def agent(observation):
    t = obs.step
    if t == 0 or mới session: state = [choose(tree[0], features(obs))]      # block 0 luôn tape 0
    if t % 144 == 0:  state[1] = _choose(t // 144, _features(obs))          # day 0/6/12/18/24
    return deep_copy(_TAPES[state[1]][t])
```
**Tree decode từ payload** (đã giải nén, 5 tape × 719 turn, 5 tree):
- **Block 1 (day 6, tree 1 node `[28,...]→[35,...]`)**: `x[28]` = số YARN_STORE mở → **>0 → tape 4** (nhánh sheep-heavy); không thì `x[35]` = demand MILK (ICE_CREAM/PIZZA/SMOOTHIE mở) → **>0 → tape 2, =0 → tape 1**.
- **Block 2 (day 12) & block 3 (day 18)**: lá đơn → luôn về **tape 0** (đường về base sau khi đi nhánh 6 ngày).
- **Block 4 (day 24, tree `[4, thr=54]`)**: `x[4]` = px CARROT **≤ 54 → tape 3** (late-harvest liquidation), >54 → tape 0.
- Feature vector 100 chiều: money 2 bên + Δ, 9 giá, 9 (inventory−10000), 8 shop count, 9 demand-unit, mỗi farm: count crop/animal, **Σ yield_units theo item** (tiền năng sản xuất tương lai!), weeds, empty, quadrants, shed 12, seeds 5, vị trí farmer.

**Vì sao bỏ prefix guard vẫn an toàn**: 5 tape cùng họ (mở màn y hệt: `SELL WHEAT 8 + 5 HIRE + 2 COW + 2 SHEEP` bước 1), chỉ lệch **qty market** bước 3-10 (field action giống nhau tới bước ~150) — sai lệch khi chuyển block nằm trong biên độ mà tape tự hấp thụ. Micro-switch mỗi vài turn gây tile desync → phải block 6 ngày.

**Ablation trên 2.048 game dev**: extra-liquidation cuối = 0; weed-clearance = +1; delivery-deadline override = −4; **purchase-budget liquidation = −440** → "clean replay router beat every hand-crafted repair". (Lưu ý: v5 bỏ luôn clamp_sells/dead_stock — chấp nhận để đổi độ sạch.)

**Endgame**: tape chứa `SELL CARROT 1000000` (716-718) và `SELL MILK/WOOL/EGG 1000000` (718) — qty khổng lồ, engine tự kẹp bằng shed hiện có. Trick "bán tất" 0 dòng code runtime.

---

## 4. MARKET: RELAY (RC2) & ADAPTIVE HYSTERESIS (V29-R1)

### 4.1. V16-RC2 — FERTILIZER market relay 3-turn + 3-checkpoint lock

- **Lock mirror bằng 3 checkpoint**: bước 216/240/264, mỗi lần ghi `distance ≤ 8` (cùng công thức clone distance); chỉ khi **cả 3 cùng pass** mới `locked=True` → hysteresis chống nhiễu đơn điểm (V14 chỉ check tức thời ≤6).
- Khi lock: với step ∈ [278, 662] mà `step+3` có SELL FERTILIZER và `(step+3) % 24 == 17` (đợt bán cuối ngày giờ 17): **bán ngay step hiện tại** `min(target, shed FERTILIZER khả dụng − đã lên lịch)`, ghi `due_step = step+3`, đến hạn `_rc2_repay` khấu đúng lượng. Lead 3 turn (không phải 1).
- Kết quả vs Kaito V27 artifact (12 seed × 2 seat): paired **1/11/0 → 12/0/0**, mean margin +833 → +1.072 (**+239**). Vs Rayk C71: +25. Vs Kaito V25/C68/HealthStone: **0.0** — không đụng được đối thủ khác lớp → xác nhận: layer này chỉ có giá trị trong trận gần-mirror.
- Kèm theo: `_v16_yarn_route` (latch 1 lần tại step ≥161: YARN_STORE mở & không có SMOOTHIE/PIZZA → đổi COW→SHEEP ở BUY step 192 + window hand 193-212) và `_v16_wool_controller` (gate giá theo pha (480→170),(600→120),(672→80),(719→1); pressure khi shed tổng ≥78; batch 16; gap ≥6 bước; terminal ≥713 bán hết).
- Ghi chú engineering: nhánh route-recovery cho animal-placement drift bị **từ chối chủ động** vì regress panel (thua đơn game −8.308) — trùng kinh nghiệm R88 của ta (Task 73).

### 4.2. V29-R1 — adaptive market hysteresis (chi tiết code)

`_FR_ITEMS = ()` — front-run của RC5 **bị tắt hẳn** ở bản này (thay bằng adaptive). Layer `_adaptive_market` từ step 456 (day 19), chỉ 3 item STRAWBERRY/MILK/WOOL:

1. **EMA áp lực nguồn cung ngoài** (đo từ public state, tự bôi mờ):
```python
external = Δmarket.inventory[item] + town_demand(prev_shops, item, step-1) − own_sold_prev
pressure[item] = max(0, 0.72*pressure_old + min(24, max(0, external)))
```
→ ước lượng "đối thủ đang đổ bao nhiêu"; âm thì không thành tín hiệu mua, chỉ cho áp lực cũ phai (0.72 decay/turn).
2. **Reserve theo tiến trình mùa** (chống bán sớm làm thiếu hàng cho schedule sau): <528: 12 → <600: 8 → <648: 6 → <684: 3 → <704: 2 → hết: 0; nếu shed tổng ≥72 (soft) trừ 7; ≥88 (hard) → 0 (bán giải tỎ). Cộng `min(14, 2 × shop_demand_units)` trước 684.
3. **Price gate nhiều tầng**: base `0.66 × base_price`; +`min(0.24, 0.045×shop_demand)`; −0.12 nếu ≥648; −0.18 nếu ≥684; **−0.18 nếu pressure ≥ 2.0** (đối thủ đang dump → ta cũng phải xả trước); −0.08 nếu `capacity_delta ≥ 0` (đối thủ có nhiều COW/SHEEP/STRAWBERRY hơn ta). Bypass khẩn: shed ≥ 88 hoặc step ≥ 704.
4. **Tranche + budget mùa**: mỗi lần bán thêm tối đa tranche 4 (+4 nếu pressure, +4 nếu shed soft, +5 tail); **budget cứng cả mùa 18 unit/item** — mỗi unit bán thêm đều trừ ngân sách.
5. **Mirror latch** (step ≥ 289, chốt 1 lần): composition distance (|ΔCOW|+|ΔSHEEP|+|ΔSTRAWBERRY ô|) ≤ 2 **và** hands bằng **và** quadrants bằng **và** |Δmoney| ≤ 250 → `max_extra_per_item = 0` → **layer adaptive gần như tắt**, giữ đúng lịch bán gốc. *Lý do (nguyên văn): tránh 2 farm giống nhau cùng phản ứng theo cùng tín hiệu công khai bằng cùng cú bán oversized* — đây chính là bản dịch code của luật L38 (knife-edge) và kỹ thuật "clone preemption" ngược chiều: mirror thì KHÔNGtrigger.
6. Sell thêm được **insert vị trí 0** trong market queue (tiền mặt premium trước HIRE/BUY).
7. Anti-peek: `last_inventory/last_sold/last_shops` chỉ lưu **sau** khi action cuối đã biết — ước lượng external flow turn sau không "nhìn trộm" đối thủ.

Kết quả V29-R1: 106/0/2 (108 frozen regression, paired mean +23.315); same-day ladder top-20 reps **196/0/20**; score-stratified 26 teams **310/0/2**; 8 nhóm V28-loss **91/0/5**; 81-trace loss audit 162/0/0. Chỉ band 2500-2599 thua (22/0/2).

### 4.3. V16-RC5 (313 votes — phổ biến nhất) — premium market lead KHÔNG gate

`_FR_ITEMS = ('MELON','MILK','STRAWBERRY','WOOL')`; `_front_run`: nếu turn sau tape định bán item && **turn hiện tại KHÔNG có town demand cho item đó** (`step%4 != 0` với shop, `step%24 != 0` với center — số học chu kỳ mua của town) && shed − (PICKUP đang bay + SELL đã lên) > 0 → bán ngay `min(target, stock−reserve)`, repay turn sau. Không cần clone gate: chỉ cần "turn này town không mua — bán cũng chẳng mất khách — nhưng lên queue trước đợt bán turn sau". 60/60 vs core.

---

## 5. OPENING + FARM + WEED (so sánh)

| | boatlee V14/RC2 | boatlee RC5/V29 | thomast v3.1/v5 | v15 ta |
|---|---|---|---|---|
| Day-0 | Kakuteki (đồn WHEAT, 5 HIRE, 2 COW + 2 SHEEP) | Nikita 8C/4S (5 HIRE, 2 COW + 2 SHEEP, đổi WHEAT buy-sell hằng ngày) | `SELL WHEAT 8 + 5 HIRE + 2 COW + 2 SHEEP` + MELON seed; WHEAT BUY-SELL chống vay (mua 25-30 bán 25-30) | kme3v10 opening (giống họ KaggressurE: đồn WHEAT, 8C/6S/3G) |
| Herd target | Theo tape Kakuteki | **8 COW / 4 SHEEP** (tương thích meta 9C/4S modal live) | Theo tape (top ladder) | 8C/6S/3G (route 0) |
| Hands | Theo tape (~10) | Theo tape | 5 HIRE ngay step 1 rồi bổ sung theo tape | Theo planner (10) |
| WEED | DIG + replay intended + **8-step catch-up từ tape** (rồi pop — chịu desync dài hạn) | như V14 | v3.1: `_noop`-aware DIG; v5: bỏ (chỉ +1 win) | weed_repair layer (tương tự V14) |

**WEED repair của boatlee khác ta ở điểm "catch-up"**: sau khi DIG xong, 8 bước kế họ **replay đúng action của tape ở bước trước đó** cho đúng actor đó (`_trace_actor_action(step-1)`) — tức chấp nhận trễ 1 bước nhưng bám lại tape; quá 8 bước thì bỏ theo đuổi. Điểm yếu rõ: cụm weed dày → tape trôi vĩnh viễn.

---

## 6. CƠ CHẾ MỚI so với v15 của ta (đối chiếu mức code)

| Cơ chế của đối thủ | Ta đã có? | Delta cụ thể so v15 |
|---|---|---|
| Clone-distance gate (signature 11 ô + hands + 3×quadrants, ≤6) | **CHƯA** — front_run ta trigger theo `opponent_plan = _ROUTES[0]` (giả định mirror cùng lineage) | Gate của boatlee **đo từ state công khai**, đúng với MỌI near-clone bất kể lineage; không cần giả định route đối thủ. Ta nên thay/đi kèm trigger này |
| Shift-1-turn + repay (bất biến 2-turn) | CÓ (`sell_lead` + `next_sup["suppress"]`) — cùng ý nghĩa | Giống nhau về mặt thuật toán; khác nguồn trigger (tape-đối thủ vs clone-gate) |
| No-demand-turn front-run (`step%4`, `step%24`) | **CHƯA** tách điều kiện này | RC5 chỉ bán khi turn đó town không mua — tránh tự ăn chân giá mà vẫn thắng queue. Ta không có điều kiện này |
| Price-impact ranking (mô hình giá phi tuyến + urgency trần 10k) | **CHƯA** (ta có sales-first nhưng không xếp theo impact) | Hàm `_impact_score` + `_order_score` port được nguyên văn (param khớp engine) |
| 3-checkpoint mirror lock (hysteresis gate) | CHƯA | V14 check tức thời → RC2 yêu cầu 216/240/264 cùng pass — chống flicker |
| EMA áp lực đối thủ từ Δpublic inventory | **CHƯA hoàn chỉnh** (ta có gap_waterfall offline, không có runtime estimator) | `0.72×old + clip(Δinv + demand − own_sold, 0..24)` — 3 dòng, đo được "đối thủ đang đổ" |
| Mirror latch → tắt layer adaptive | **KHÔNG tắt** — front_run ta vẫn chạy vs mirror | V29 tắt hẳn (max_extra=0) khi near-mirror: xác nhận L38 — vs mirror mọi can thiệp là xúc xắc. Ta đang giữ front_run ON vs v14-self (hòa tuyệt đối từng dollar chứng minh layer inert khi bug không xảy ra, nhưng vs mirror lạ thì nên cân nhắc gate) |
| Season budget per item (18 unit) cho mọi bán thêm | CHƯA | Kẹp đuôi rủi ro của adaptive layer |
| Terminal mega-SELL (qty 1e6, engine tự kẹp) | CÓ terminal_liquidation nhưng đang **OFF** trong `_SETTINGS` | Cách viết 1 dòng của thomast (trong tape) + đo "+0 win" riêng lẻ — rẻ, đáng A/B lại |
| dead_stock (bán phần route không bao giờ bán) | **OFF** (`dead_stock: False`) | thomast đo +19/−0 khi ghép clamp_sells; ta có clamp ON mà bỏ dead_stock — A/B ngay |
| Router block 6 ngày / prefix-guard tail | Không áp dụng (ta là planner 1 route) | Chỉ đáng value nếu xây thư viện multi-route |
| Router input = Σ yield_units công khai của đối thủ | CHƯA | Feature "sản lượng tiềm năng của đối thủ" — rẻ, feed được vào valve của ta |

---

## 7. KHẢ NĂNG KHAI THÁC: v15 vs các agent này

**Đặc điểm chung làm chúng ta có lợi thế cấu trúc**: cả 5 agent đều là **tape + lớp reactive chỉ đụng market queue** — không ai đọc route của ta, không ai phá lịch của ta, không ai trừng phạt sai lệch của ta.

1. **vs boatlee (V14/V16/V29)**: trận đấu thuộc lớp **mirror-knife-edge** (route của họ = top-meta hiện hành cùng họ với kme3v10 của ta). Cơ chế timing 2 bên gần tương đương (H=8 + front_run ta ≈ shift+repay + impact-rank họ). Theo L38 + ceiling ~$5-6.5k đã đo, kỳ vọng: margin nhỏ, tỷ lệ W/L dao động theo seed; **điểm phân định thực** là chất lượng tuyệt đối của route gốc (Kakuteki/Nikita/RngRng là submission top thật, có thể > kme3v10) — chưa đo được, phải chạy proxy. Điểm yếu khai thác được:
   - Clone-gate của họ **tắt** khi ta lệch signature (hands/quadrant/tile-count) > ngưỡng sớm game → toàn bộ preempt/relay của họ im lặng.
   - `_MARKET_PARAMS` hard-code + giả định equilibrium 10000 cố định: khi kho thị trường bị đẩy gần 10k, ranking của họ bóp theo urgency — ta có thể cố ý tạo glut để làm ranking họ tự hại.
   - Weed catch-up chỉ 8 bước — cụm weed xấu làm tape họ trôi.
2. **vs thomast v5 (93.8%)**: 93.8% là **vs trường replay (689 tape băng đông)**, không phải vs đối thủ thích ứng. Với ta, họ = 1 trong 5 route cố định chọn theo public state. **Bề mặt điều khiển rõ ràng nhất public meta**: các ngưỡng router của họ đọc từ market/town mà TA có thể ghi:
   - Trước step 144: giữ YARN_STORE khóa/mở để lái họ vào tape 4 hoặc cấm;
   - Trước step 576 (day 24): **đổ CARROT để px ≤ 54** → ép họ nhảy tape 3 "late-harvest liquidation" (nhánh họ chỉ lấy khi giá cà rốt yếu — nhánh thấp giá trị hơn).
   Đây là đòn "steering đối thủ" đầu tiên tìm thấy ở mức code — ngược với luật L32 (đổi route tự hại) vì ta không đổi route, ta **đổi trạng thái công khai** để đối thủ đổi route.
   - Không clamp_sells ở v5: nếu state drift làm SELL vượt shed của họ → đốt slot (v3.1 đo +7 cho ta-bên-có).
3. **Rủi ro ngược**: v15 không có gate "no-demand turn" cho front_run và không impact-ranking — trong mirror race với boatlee RC5/V29, 2chi tiết đó có thể là vài trăm coin/lần.

**Kết luận khai thác**: chưa khẳng định thắng/thua — phải build proxy + battery. Cơ chế ta vượt trội: R90 watchdog (họ không có — note boatlee từng thử route-recovery cho animal drift và bỏ vì regress), H=8 cadence race, planner đầy đủ thay tape. Cơ chế họ vượt ta: clone-gate từ public state, no-demand-turn, impact-rank, EMA áp lực, steering-resistance bằng mirror-latch.

---

## 8. TRANSFER VALUE — XẾP HẠNG ĂN CẮP ĐƯỢC

**RANK CAO (port ngay, surgical theo L31, mỗi cái 1 A/B battery 8-16 trận):**
1. **Clone-distance gate** — hàm `_public_signature` + `_clone_distance` (~25 dòng) làm trigger cho front_run thay/đi kèm `opponent_plan`; ngưỡng 6, trọng số `1/3/1`. Làm front_run đúng với mọi near-clone lạ (Kaggle!), không phụ thuộc giả định lineage.
2. **dead_stock ON** (đã có sẵn trong chassis, chỉ bật `_SETTINGS`) — thomast đo +19/−0 với clamp_sells đồng hành; kèm **mega-SELL 1e6 endgame** (terminal_liquidation viết 1 dòng) — 2 Layer A/B rẻ nhất danh sách.
3. **No-demand-turn condition** cho mọi sell-lead/front-run: `step%4 != 0 and step%24 != 0` (trừ khi item đang có shop demand) — chỉ bán trước turn không có khách town.
4. **Price-impact ranking** (`_impact_score`/`_order_score` + bảng `_MARKET_PARAMS` — trùng engine) cho thứ tự SELL trong turn; kết hợp sales-first hiện có.

**RANK TRUNG:**
5. **3-checkpoint lock** (216/240/264 cùng pass) thay check tức thời cho mọi gate mirror — chống flicker.
6. **EMA áp lực đối thủ** (0.72 decay; Δinv + town_demand − own_sold) + gate-cut −0.18 khi pressure ≥2 — runtime estimator 3 dòng cho valve kinh tế.
7. **Mirror latch → tắt layer can thiệp** (|Δmoney| ≤ 250 + composition ≤2): vs mirror tuyệt đối thì tắt front_run/adaptive — kiểm chứng thêm L38, tránh xúc xắc vô ích.
8. **Season budget per item** cho mọi lượng bán thêm (18 units) — kẹp rủi ro adaptive.

**RANK THẤP (lưu thôi):**
9. GBDT router 6-ngày + thư viện 5 tape (cần infra luyện lại; ý tưởng prefix-guard tail đáng nhớ nếu xây multi-route).
10. Yarn-route COW→SHEEP swap, wool-controller 4 pha — phụ thuộc unlock shop, giá trị cố định nhỏ.
11. `_noop` predicate (sao chép điều kiện engine bỏ qua action) — hữu ích cho các repair tương lai, ta đã có các predicate tương tự trong shed_watch.

**CẢNH BÁO CỦA HỌ (không nên ăn cắp)**: purchase-budget liquidation (−440 game!), sells-before-buys (−17), hire-last (−13), feed/care trên idle turn (−4, tràn shed) — trùng khớp Law L33 của ta (A/B từng layer, layer của tác giả bị tắt thường tắt có lý).

---

## 9. NEXT ACTIONS (đề xuất)

1. **Task 74-c**: build 5 proxy agent (giải nén main từ notebook — đã có sẵn ở /tmp cho V14, V29) → đăng ký registry bench → battery v15 vs mỗi proxy, 10 seed × 2 seat, seeds mới (400-409) — đo thật thay dự đoán.
2. A/B nhanh trong tuần: dead_stock ON + terminal_liquidation (mega-SELL) + no-demand-turn condition cho front_run (mỗi Layer 1 biến thể, theo L31).
3. Port clone-distance gate vào front_run (thay opponent_plan assumption) → A/B vs toàn registry + 5 proxy.
4. Thí nghiệm steering: force-route CARROT dump trước step 576 vs thomast v5 proxy — đo có ép được tape 3 không (đòn điều khiển đối thủ đầu tiên).
