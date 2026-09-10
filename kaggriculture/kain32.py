# kain32 "LAND-LABOR ENGINE" (Task 32) — 4 LUẬT CỨNG từ quan sát top Kaggle:
#   HARD-1 Mua đất 2 (NE $1k) NGÀY 5-7 (top: d5-7; v6 mua muộn ~d11)
#   HARD-2 Mua đất 3 (SW $2k) NGÀY 10-12 (top: d10-12)
#   HARD-3 KHÔNG BAO GIỜ mua đất 4 (SE $4k) — tối đa 75 ô
#   HARD-4 Đất trống <= 15% ô sở hữu (utilization >= 85%) — wheat là van
#        áp suất lấp mọi ô trống (cỗ máy: $10 hạt -> 4-6u, feed đàn + bán)
# Delta bổ sung từ autopsy battle_1789037559333 (kain31 thua v6 $68.2k-$55.6k):
#   ΔW WOOL-FIX: kain31 chỉ mua được 1 cừu (wt_supply gate chặn khi đàn
#      lớn) -> wool $2.9k vs v6 $18.7k. Fix: buy order COW->SHEEP->GOOSE,
#      gate wt_supply nới 1.3x -> 1.1x, buy 3/ngày d<=12, herd cap 17.
#   ΔF FEED-TỰ-TRỒNG: wheat quota = đàn*1.35+4, lấp tới 85% đất; chỉ mua
#      wheat ngoài thị trường khi CẤP BÁO (shed<6) — v6/kain31 mua $34k
#      wheat/mùa để nuôi thú (giá $44 do khan hiếm 2 bên cùng mua).
#   ΔU UTILIZATION WATCHDOG: plant_target = 85% ô sở hữu; wheat quota
#      nâng lên đè hết phần thiếu (straw 28 / melon 12-14 giữ nguyên).
# Giữ kain31: single-plan h0 (R106), MILK-COMMIT cow floor 6 (R107),
# pháo đài cân bằng (R108), P3 graded-quota (R110), tranche-8, E8-lite,
# care tiers, egg-fortress floor 7.
# ---- kain30 gốc:
# KERNEL MỚI (bước ra idol constants, thay bằng giá-trị-biên):
#   ΔP3 GRADED-QUOTA: mọi quota premium (MELON/CARROT/STRAW) định giá bằng
#      _marg() — giá biên TRUNG BÌNH của các unit sắp bán vào kênh chiếu
#      theo (inv hiện tại + pipeline 2 bên − drain tương lai) thay vì
#      constant 14/30/8 (đây là hạt nhân P3: $/unit biên → quyết định).
#   ΔR NOON-REPLAN: plan key (day, noon) — tính lại toàn cục lúc h12
#      (v6 cache 24h không thích ứng giữa ngày).
# SEAM (khai thác điểm yếu v6 — xem RESEARCH_V7.md):
#   S1 EGG-FORTRESS: v6 hard-cap ngỗng 6 → floor 8/cap 9 khi opp_geese≤7
#      (R102: kênh không-đối-chiếu-được); cắt BÒ TRƯỚC khi vượt herd-cap.
#   S3 STRAW-COMMIT: _marg ≥ 0.98 → không nhượng kênh dâu (R101/R105:
#      cắt quota = hiến phần chia; giá-biên quyết định, không pipeline).
#   S3b LATE-STRAW d14-15: quota 8 (v6 dừng 6) khi giá biên còn ≥ 1.0.
#   S4 LATE-MELON d15-16: quota 6 khi marg ≥ 0.78 (đất trống endgame).
# Giữ nguyên v6.6: melon-14 d0-7 (idol K13), tranche-8 (R90), feed-gate $52
# (R92), E8-lite (drain-aware endgame), hire/land/task tiers, care discipline.

import math

CROPS = {
    "WHEAT":      {"seed": 10,  "first_yield_day": 2,  "max_yield_day": 4,  "interval": 0, "max_yield": 6, "ongoing": False},
    "CARROT":     {"seed": 20,  "first_yield_day": 2,  "max_yield_day": 3,  "interval": 0, "max_yield": 4, "ongoing": False},
    "TOMATO":     {"seed": 50,  "first_yield_day": 8,  "max_yield_day": 8,  "interval": 1, "max_yield": 4, "ongoing": True},
    "STRAWBERRY": {"seed": 100, "first_yield_day": 10, "max_yield_day": 10, "interval": 2, "max_yield": 4, "ongoing": True},
    "MELON":      {"seed": 80,  "first_yield_day": 10, "max_yield_day": 12, "interval": 0, "max_yield": 6, "ongoing": False},
}
ANIMALS = {
    "GOOSE": {"cost": 300, "structure": "COOP",    "first_yield_day": 4, "interval": 1, "max_held": 4, "product": "EGG"},
    "COW":   {"cost": 400, "structure": "PASTURE", "first_yield_day": 8, "interval": 2, "max_held": 6, "product": "MILK"},
    "SHEEP": {"cost": 500, "structure": "PASTURE", "first_yield_day": 6, "interval": 3, "max_held": 6, "product": "WOOL"},
}
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
MARKET_I0 = 10000
MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "I0": MARKET_I0, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "I0": MARKET_I0, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "I0": MARKET_I0, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": MARKET_I0, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": MARKET_I0, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "I0": MARKET_I0, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": MARKET_I0, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": MARKET_I0, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}
SHOPS = {
    "BAKERY":         ["EGG", "WHEAT"],
    "PIZZA_SHOP":     ["MILK", "TOMATO", "WHEAT"],
    "BRUNCH_SPOT":    ["EGG", "WHEAT", "STRAWBERRY"],
    "YARN_STORE":     ["WOOL"],
    "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"],
    "PET_CAFE":       ["CARROT"],
    "SMOOTHIE_SHOP":  ["STRAWBERRY", "MILK"],
    "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"],
}
TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != "FERTILIZER"]

TURN_PER_DAY = 24
EPISODE_STEPS = 720
MAX_ORDERS = 10
SHED_CAP = 100
LAND_PRICES = [1000, 2000, 4000]
MAX_SHOP_INSTANCES = 8

CYCLE_LEN = {"WHEAT": 5, "CARROT": 4, "TOMATO": 12, "STRAWBERRY": 17, "MELON": 13}
YIELD_PER_CYCLE = {"WHEAT": 5, "CARROT": 3, "TOMATO": 4, "STRAWBERRY": 4, "MELON": 6}

T_WATER_CRIT = 0
T_SERVICE_URG = 0
T_HARVEST_URG = 2
T_DELIVER = 2
T_BUILD_URG = 2
T_SERVICE = 2
T_WATER_YIELD = 3
T_BUILD = 4
T_HARVEST_ANIMAL = 2
T_HARVEST = 5
T_PLANT = 5
T_DIG = 5
T_WATER_MAINT = 3
T_FERTILIZE = 7

FERT_SELL = True
FERT_FLOOR = 38
ANIMAL_CAP = 14  # V3: lao động 75-ô tường 101 action — đàn 14 an miếng cuối
TOM_QUOTA = 6
HOLD = {"MILK": 0.98, "WOOL": 0.94, "STRAWBERRY": 0.80, "EGG": 0.86,
        "CARROT": 0.70, "WHEAT": 0.76, "MELON": 0.52, "TOMATO": 0.82, "FERTILIZER": 0.50}

_STATE = {}
_ARCHES = ("CONTEST", "MIRROR", "COOP", "PASSIVE")


def _gauss(x, c, s):
    s = max(1e-6, float(s))
    return math.exp(-0.5 * ((float(x) - float(c)) / s) ** 2)


def _tm_step(tm, step, inv, shops):
    try:
        prev = tm.get("prev_inv")
        if prev is not None and tm.get("prev_step") == step - 1:
            drain = _drain_at(step - 1, tm.get("shops") or [])
            ms = tm.get("my_sells") or {}
            mb = tm.get("my_buys") or {}
            od = tm.setdefault("opp_day", {})
            for p in PRODUCTS:
                delta = inv.get(p, MARKET_I0) - prev.get(p, MARKET_I0)
                od[p] = od.get(p, 0.0) + delta + drain.get(p, 0.0) - ms.get(p, 0.0) + mb.get(p, 0.0)
        if step % 24 == 0 and step > 0:
            tm.setdefault("opp_daily", {})[step // 24 - 1] = dict(tm.get("opp_day") or {})
            tm["opp_day"] = {}
        tm["prev_inv"] = {p: inv.get(p, MARKET_I0) for p in PRODUCTS}
        tm["prev_step"] = step
        tm["my_sells"] = {}
        tm["my_buys"] = {}
    except Exception:
        pass


def _tm_orders(tm, orders):
    try:
        ms = tm.setdefault("my_sells", {})
        mb = tm.setdefault("my_buys", {})
        for o in orders or []:
            if not isinstance(o, (list, tuple)) or len(o) < 3:
                continue
            op, item, n = o[0], o[1], o[2]
            if op == "SELL" and item in PRODUCTS and _is_num(n):
                ms[item] = ms.get(item, 0.0) + int(n)
            elif op == "BUY_PRODUCT" and item in PRODUCTS and _is_num(n):
                mb[item] = mb.get(item, 0.0) + int(n)
    except Exception:
        pass


def _bayes_step(tm, day, opp_farm, my_herd, my_money):
    try:
        tm["mode"] = tm.get("mode", "CONTEST")
        if day < 8:
            tm["mode"] = "CONTEST"
            return
        oc = og = osp = 0
        opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
        if opp_tiles:
            for row in opp_tiles:
                for t in row:
                    if isinstance(t, dict) and "animal" in t:
                        a = t.get("animal")
                        if a == "COW":
                            oc += 1
                        elif a == "GOOSE":
                            og += 1
                        elif a == "SHEEP":
                            osp += 1
        opp_money = float(_g(opp_farm, "money", 0) or 0) if opp_farm else 0.0
        mc, mg, msp = my_herd
        money_ratio = (opp_money / my_money) if my_money > 300.0 else 1.0

        # tight bit-identical twin signature (true self-play only)
        sig = (_gauss(oc - mc, 0.0, 0.8)
               * _gauss(og - mg, 0.0, 1.0)
               * _gauss(osp - msp, 0.0, 0.8)
               * _gauss(money_ratio, 1.0, 0.07)
               * _gauss(len(opp_tiles or []) and 1.0 or 0.0, 1.0, 0.05))
        like_m = max(0.005, min(0.98, sig))
        like_c = max(0.05, 1.0 - 0.75 * like_m)

        pm = tm.get("pm", 0.08)
        pm = (pm ** 0.8) * (like_m / (like_m + like_c))
        pm = min(0.99, max(0.005, pm))
        tm["pm"] = pm

        cur = tm.get("mode", "CONTEST")
        if cur == "MIRROR":
            if pm < 0.35:
                tm["mode"] = "CONTEST"
        else:
            if pm > 0.70:
                tm["mode"] = "MIRROR"
    except Exception:
        pass


def _g(o, k, d=None):
    try:
        if isinstance(o, dict):
            return o.get(k, d)
        return getattr(o, k, d)
    except Exception:
        return d


def _mk(tier, x, y, op, **kw):
    d = {"tier": tier, "x": x, "y": y, "op": op}
    d.update(kw)
    return d


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def _step_toward(fx, fy, tx, ty):
    if fx < tx:
        return "EAST"
    if fx > tx:
        return "WEST"
    if fy < ty:
        return "SOUTH"
    if fy > ty:
        return "NORTH"
    return None


def _shed_tiles(board):
    h = board // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]


def _nearest_shed_tile(x, y, board):
    return min(_shed_tiles(board), key=lambda t: abs(t[0] - x) + abs(t[1] - y))


def _is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _shape(func, x, T=None):
    x = max(0.0, x)
    if func == "linear":
        return x
    if func == "sq":
        return x * x
    if func == "sqrt":
        return math.sqrt(x)
    if func == "log":
        return math.log(1.0 + x)
    if func == "log10":
        return math.log10(1.0 + x)
    if func == "hinge":
        if not T or T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x


def _price(item, inventory):
    p = MARKET_PARAMS[item]
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        pr = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        pr = base - amp * _shape(f, inventory - I0, T)
    return max(1, int(round(pr)))


def _sell_count(item, n_avail, inv, thresh):
    k = 0
    while k < n_avail:
        if _price(item, inv + k) < thresh:
            break
        k += 1
    return k


_ABOVE_CACHE = {}


def _above_headroom(item, frac):
    key = (item, frac)
    if key not in _ABOVE_CACHE:
        thresh = frac * MARKET_PARAMS[item]["base"]
        k = 0
        while k < 20000 and _price(item, MARKET_I0 + k) >= thresh:
            k += 1
        _ABOVE_CACHE[key] = k
    return _ABOVE_CACHE[key]


def _shop_vector(shops):
    v = {it: 0.0 for it in PRODUCTS}
    for s in shops:
        prods = SHOPS.get(s, [])
        m = 2 if len(prods) == 1 else 1
        for it in prods:
            v[it] += m
    return v


def _avg_shop_vector():
    v = {it: 0.0 for it in PRODUCTS}
    ks = list(SHOPS)
    for s in ks:
        sv = _shop_vector([s])
        for it in PRODUCTS:
            v[it] += sv[it] / len(ks)
    return v


AVG_SHOP_VEC = _avg_shop_vector()


def _drain_at(step, shops):
    d = {p: 0.0 for p in PRODUCTS}
    if step % 4 == 0 and shops:
        sv = _shop_vector(shops)
        for p in PRODUCTS:
            d[p] += sv[p]
    if step % 24 == 0:
        for p in TOWN_CENTER_PRODUCTS:
            d[p] += 1.0
    return d


def _forward_absorb(day, hour, shops):
    step = day * TURN_PER_DAY + hour
    cur = _shop_vector(shops)
    n = len(shops)
    unlock_steps = []
    for d in range(day + 1, 30):
        if d % 3 == 0 and n < MAX_SHOP_INSTANCES:
            unlock_steps.append(d * TURN_PER_DAY)
            n += 1
    tot = {it: 0.0 for it in PRODUCTS}
    for t in range(step, EPISODE_STEPS):
        if t % 4 == 0:
            k = 0
            for u in unlock_steps:
                if t >= u:
                    k += 1
            for it in PRODUCTS:
                tot[it] += cur[it] + AVG_SHOP_VEC[it] * k
        if t % 24 == 0:
            for it in TOWN_CENTER_PRODUCTS:
                tot[it] += 1
    return tot


def _pipeline(tiles, shed):
    pipe = {it: 0.0 for it in PRODUCTS}
    if not tiles:
        return pipe
    for row in tiles:
        for t in row:
            if not isinstance(t, dict):
                continue
            if t.get("kind") == "PLANT":
                crop = t.get("crop")
                if crop in YIELD_PER_CYCLE:
                    pipe[crop] += YIELD_PER_CYCLE[crop]
            elif "animal" in t:
                an = t.get("animal")
                if an in ANIMALS:
                    pipe[ANIMALS[an]["product"]] += 28.0
    if shed:
        for it in PRODUCTS:
            v = shed.get(it, 0)
            if _is_num(v):
                pipe[it] += v
    return pipe


def _struct_reserve(need, unit_cost, money):
    if need <= 0:
        return 0
    r = 0
    if money >= unit_cost + 250:
        r = 1
    if need >= 2 and money >= 2 * unit_cost + 500:
        r = 2
    if need >= 3 and money >= 3 * unit_cost + 900:
        r = 3
    return min(need, r)



# ---- v6 ΔF: E8-lite port (v5's drain-aware endgame hold) ----

def _pipe_rest(tiles, day):
    """v6 ΔF (port nguyên văn v5._pipe_rest — RULES R71): nguồn cung CHỜ THU
    còn lại trước hết mùa theo item — gate thanh lý d22-27."""
    out = {it: 0.0 for it in PRODUCTS}
    try:
        if not tiles:
            return out
        for row in tiles:
            for t in row:
                if not isinstance(t, dict):
                    continue
                if t.get("kind") == "PLANT":
                    crop = t.get("crop")
                    cd = CROPS.get(crop)
                    if not cd:
                        continue
                    age = day - t.get("planted_day", day)
                    yu = float(t.get("yield_units", 0) or 0)
                    if cd["ongoing"]:
                        mls = t.get("max_lifespan_step", -1)
                        days_left = max(0, (mls - day * 24) // 24 + 1) if mls >= 0 else 0
                        out[crop] += yu + 1.3 * max(0, days_left)
                    else:
                        out[crop] += yu if age > cd["max_yield_day"] else max(yu, 2.0)
                elif "animal" in t:
                    ad = ANIMALS.get(t.get("animal"))
                    if not ad:
                        continue
                    yu = float(t.get("yield_units", 0) or 0)
                    first = ad["first_yield_day"]
                    itv = max(1, ad["interval"])
                    age = day - t.get("placed_day", day)
                    n_prod = 0
                    a = max(age, first)
                    while a <= 28:
                        if (a - first) % itv == 0:
                            n_prod += 1
                        a += 1
                    out[ad["product"]] += yu + min(2.0 * ad["max_held"], 1.3 * n_prod)
    except Exception:
        pass
    return out


def _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp_farm, money, tm=None):
    absorb = _forward_absorb(day, 0, shops)
    my_pipe = _pipeline(tiles, shed)
    opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
    opp_pipe = _pipeline(opp_tiles, None)

    def room(it):
        deficit = max(0.0, MARKET_I0 - inv.get(it, MARKET_I0))
        r = deficit + absorb.get(it, 0) + _above_headroom(it, 0.78)
        return r - my_pipe.get(it, 0) - 0.85 * opp_pipe.get(it, 0)

    # ΔP3: giá-biên trung bình của `units` unit sắp đổ vào kênh `it`, quy về
    # lần base. proj = tồn kho chiếu theo mid-window (inv + pipeline 2 bên −
    # phần drain tới anchor). Đây là kernel P3: quyết định theo đường cầu
    # (Cournot exact), KHÔNG theo constant/idol.
    def _marg(it, units, anchor_day):
        try:
            cur = float(inv.get(it, MARKET_I0) or MARKET_I0)
            total_abs = float(absorb.get(it, 0.0) or 0.0)
            horizon = max(1, 29 - day)
            days_to = max(1, min(28, anchor_day) - day)
            fut_drain = total_abs * min(1.0, days_to / float(horizon))
            proj = (cur + float(my_pipe.get(it, 0.0) or 0.0)
                    + 0.85 * float(opp_pipe.get(it, 0.0) or 0.0) - fut_drain)
            s = 0.0
            for k in range(1, int(units) + 1):
                s += _price(it, max(0.0, proj + k))
            return (s / max(1, int(units))) / float(MARKET_PARAMS[it]["base"])
        except Exception:
            return 1.0

    coops = pastures = wheat_standing = 0
    animals_now = 0
    standing = {c: 0 for c in CROPS}
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                k = t.get("kind")
                if k == "COOP":
                    coops += 1
                elif k == "PASTURE":
                    pastures += 1
                if "animal" in t:
                    animals_now += 1
                if k == "PLANT":
                    cc = t.get("crop")
                    if cc in standing:
                        standing[cc] += 1
                    if cc == "WHEAT":
                        wheat_standing += 1
    shed_geese = shed.get("GOOSE", 0) if shed and _is_num(shed.get("GOOSE", 0)) else 0
    shed_cows = shed.get("COW", 0) if shed and _is_num(shed.get("COW", 0)) else 0
    shed_sheep = shed.get("SHEEP", 0) if shed and _is_num(shed.get("SHEEP", 0)) else 0

    opp_counts = {"GOOSE": 0, "COW": 0, "SHEEP": 0}
    if opp_tiles:
        for row in opp_tiles:
            for t in row:
                if isinstance(t, dict) and "animal" in t:
                    a = t.get("animal")
                    if a in opp_counts:
                        opp_counts[a] += 1

    mode = (tm or {}).get("mode", "CONTEST")
    milk_room = (absorb.get("MILK", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("MILK", MARKET_I0))
                 - 30.0 * opp_counts["COW"] - 40.0)
    wool_room = (absorb.get("WOOL", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("WOOL", MARKET_I0))
                 - 28.0 * opp_counts["SHEEP"] - 20.0)
    egg_room = (absorb.get("EGG", 0) + 0.5 * max(0.0, MARKET_I0 - inv.get("EGG", MARKET_I0))
                - 46.0 * opp_counts["GOOSE"] - 20.0)
    # KAIN-8: herd = v5's adaptive formula + shop floors, capital-capped
    # early, labor-safe total (13), delivery 2/day to d14 + price windows.
    # (v6 v5: BỎ geese-4-early — va chạm ngỗng-sớm với ngỗng-sớm của v5 trên
    # 129/131/138 (cả hai phóng 7 → kênh trứng sập, v6 −$10.6k). Giữ công thức
    # kain16; floor-7 ΔB chỉ bật SAU tiền dưa — lệch pha với đàn ngỗng v5)
    goose_target = max(3, min(9, int(egg_room // 46)))
    # S1 EGG-FORTRESS (R102): v6 hard-cap 6 — floor 7 (mix cân bằng: ngỗng
    # biên ~$1.07k+fert < bò $3.7k khi sữa chưa bão hòa — autopsy 146)
    if opp_counts["GOOSE"] <= 6 and day >= 4:
        goose_target = max(goose_target, 7)
    cow_target = max(2, min(10, int(milk_room // 30)))
    # ΔB MILK-COMMIT: kênh sữa sâu nhất game — KHÔNG nhượng (first-mover:
    # v6 commit 9 bò trước thì ta mất $16.7k; floor 6 khi giá còn khỏe)
    if 4 <= day <= 19:
        try:
            if float(prices.get("MILK", 0) or 0) >= 0.95 * MARKET_PARAMS["MILK"]["base"]:
                cow_target = max(cow_target, 6)
        except Exception:
            pass
    sheep_target = max(5, min(8, int(wool_room // 30)))
    try:
        if mode != "MIRROR":
            milk_shops = sum(1 for s in (shops or [])
                             if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
            yarn_n = sum(1 for s in (shops or []) if s == "YARN_STORE")
            if milk_shops >= 2 and 4 <= day <= 19:
                _dm = float(prices.get("MILK", 0) or 0) >= 0.95 * MARKET_PARAMS["MILK"]["base"]
                cow_target = max(cow_target,
                                 min(8 if _dm else 6, (3 if _dm else 2) + milk_shops))
            if yarn_n >= 1 and 4 <= day <= 18:
                _dw = float(prices.get("WOOL", 0) or 0) >= 0.95 * MARKET_PARAMS["WOOL"]["base"]
                sheep_target = max(sheep_target,
                                   min(8 if _dw else 7, (5 if _dw else 4) + yarn_n))
    except Exception:
        pass
    if day <= 10:
        cow_target = min(cow_target, 1 + int(money // 900))
        sheep_target = min(sheep_target, 2 + int(money // 1500))
    _herd_cap = 14 if (day >= 11 or money >= 3000) else 12
    tot = cow_target + sheep_target + goose_target
    if tot > _herd_cap:
        # autopsy 146: cắt cừu trước (floor 4), rồi bò (floor 6), ngỗng cuối (floor 7)
        over = tot - _herd_cap
        sheep_target = max(4, sheep_target - over)
        tot = cow_target + sheep_target + goose_target
        if tot > _herd_cap:
            cow_target = max(6, cow_target - (tot - _herd_cap))
            tot = cow_target + sheep_target + goose_target
            if tot > _herd_cap:
                goose_target = max(7, goose_target - (tot - _herd_cap))
    if day < 2:
        goose_target = 0
        cow_target = 0
        sheep_target = 0
    elif day < 5:
        cow_target = 0
        sheep_target = 0
    elif day < 6:
        sheep_target = 0
    owned_total = animals_now + shed_geese + shed_cows + shed_sheep
    if owned_total >= ANIMAL_CAP:
        goose_target = min(goose_target, animals_now + shed_geese)
        cow_target = min(cow_target, sum(1 for row in tiles for t in row
                                         if isinstance(t, dict) and t.get("animal") == "COW") + shed_cows)
        sheep_target = min(sheep_target, sum(1 for row in tiles for t in row
                                             if isinstance(t, dict) and t.get("animal") == "SHEEP") + shed_sheep)

    coop_need = _struct_reserve(goose_target + shed_geese - coops, 300, money)
    past_need = _struct_reserve(cow_target + shed_cows + sheep_target + shed_sheep - pastures, 500, money)
    if day <= 2:
        coop_need = min(coop_need, 2)
        past_need = min(past_need, 2)

    board = len(tiles)
    cx = board // 2
    empties = []
    for y in range(board):
        for x in range(board):
            if tiles[y][x] is None:
                empties.append((x, y))
    empties.sort(key=lambda c: abs(c[0] - cx) + abs(c[1] - cx))
    reserved = []
    ri = 0
    for _ in range(coop_need):
        if ri < len(empties):
            reserved.append((empties[ri][0], empties[ri][1], "BUILD_COOP"))
            ri += 1
    for _ in range(past_need):
        if ri < len(empties):
            reserved.append((empties[ri][0], empties[ri][1], "BUILD_PASTURE"))
            ri += 1
    plantable = empties[ri:]

    feed_demand = (animals_now + shed_geese + shed_cows + shed_sheep
                   + goose_target + cow_target + sheep_target) * max(0, 29 - day)

    quotas = {}
    # KAIN-2 "WAVE COLLIDER": bigger + earlier melon (cycle 11: d2 plants
    # harvest d13 — a full 6 days before v5's Wave-E d19 wave) to bank the
    # premium BEFORE the collision, while the visible pipeline pressures
    # v5's room() into yielding.
    if day <= 1:
        quotas["MELON"] = 14
    elif 2 <= day <= 7:
        quotas["MELON"] = 14
    elif 8 <= day <= 14:
        # ΔP3: thang giá-bên thay binary room-gate — 14/10/7 theo marg
        m_m = _marg("MELON", 60, day + 13)
        if room("MELON") > -50 and m_m >= 0.58:
            quotas["MELON"] = 14
        elif m_m >= 0.55:
            quotas["MELON"] = 10
        else:
            quotas["MELON"] = 7
    elif 15 <= day <= 16:
        # S4 LATE-MELON: trồng d15 chín d28 — dùng đất trống endgame
        if _marg("MELON", 36, day + 13) >= 0.78:
            quotas["MELON"] = 6
    if 2 <= day <= 16:
        quotas["TOMATO"] = 0
    if 5 <= day <= 13:
        s_room = room("STRAWBERRY")
        # (v6 v4: REVERT ΔA straw-ramp — battery v3 33/40 vs kain16 38/40:
        # pipeline dâu 30-từ-d5 là ÁP LỰC làm v5 room() nhượng kênh (R94/R96
        # market-share yield); ramp theo v5 = v5 lấy lại $1.9k. Vốn đàn d5-12
        # giờ đến từ ngỗng-4-sớm ΔB (egg+$fert từ d4) thay vì cắt dâu)
        want_straw = 24
        # HARD-4/75-ô: straw 28 thay 30 — nhường 2 ô cho wheat-machine
        # KAIN-10: v5's minimax + scarcity straw escalation — don't subtract
        # the opponent pipeline when the market is deep enough for both.
        try:
            spx = float(prices.get("STRAWBERRY", 0) or 0)
            sinv = float(inv.get("STRAWBERRY", MARKET_I0) or MARKET_I0)
            straw_shops_n = sum(1 for s in (shops or [])
                                if "STRAWBERRY" in SHOPS.get(s, ()))
        except Exception:
            spx, sinv, straw_shops_n = 0.0, MARKET_I0, 0
        if (spx >= 1.05 * MARKET_PARAMS["STRAWBERRY"]["base"] and straw_shops_n >= 2
                and mode != "MIRROR" and day <= 13):
            s_room = max(s_room, absorb.get("STRAWBERRY", 0.0)
                         - my_pipe.get("STRAWBERRY", 0.0))
        if spx >= 1.25 * MARKET_PARAMS["STRAWBERRY"]["base"] and sinv <= MARKET_I0:
            s_room = max(s_room, want_straw * 4 + 40)
        # S3 STRAW-COMMIT (R101/R105): giá-bên còn khỏe → KHÔNG hiến kênh
        # dù pipeline đối thủ lớn (chỉnh theo đường cầu, không theo pipeline)
        if _marg("STRAWBERRY", 110, min(28, day + 14)) >= 0.98:
            s_room = max(s_room, 120)
        quotas["STRAWBERRY"] = want_straw if s_room > 100 else max(0, min(want_straw, int(s_room // 4)))
    elif 14 <= day <= 15:
        # S3b LATE-STRAW: trồng d14 chín d24-28 (3 event) khi giá biên ≥ 1.0
        if _marg("STRAWBERRY", 40, min(28, day + 12)) >= 1.0:
            quotas["STRAWBERRY"] = 8
        else:
            quotas["STRAWBERRY"] = 6
    if day <= 24:
        if day <= 4:
            quotas["WHEAT"] = 17
        else:
            # dF FEED-TU-TROONG: wheat nha thay mua $44 ngoai thi truong.
            # animals_now*1.5 (thuc an ngay) + targets*0.6 (dp dan tang)
            daily_q = int((animals_now + shed_geese + shed_cows + shed_sheep) * 1.5
                          + (goose_target + cow_target + sheep_target) * 0.6) + 4
            # cap lao động (v6-mix trên 75 ô): wheat 13 đứng — phần thiếu
            # MUA như v6 ($34k/mùa = arbitrage lao động, tay cho kênh $250+)
            quotas["WHEAT"] = min(13, max(10, daily_q))
            # KAIN-8: strawberry ~2x wheat $/action — shift tiles wheat->
            # straw only when straw quota will actually fill them.
            if (standing.get("STRAWBERRY", 0) < 22 and 6 <= day <= 16
                    and quotas.get("STRAWBERRY", 0) >= 22):
                quotas["WHEAT"] = min(quotas["WHEAT"], 16)
    # HARD-4 UTILIZATION WATCHDOG: dat trong <= 15% o so huu - wheat la van
    # ap suc: nang quota wheat len de moi khoang trong sau khi premium quota
    # (straw/melon/carrot) + dan + cong trinh da chiem cho cua chung.
    try:
        owned_tiles = sum(1 for row in tiles for t in row if t != "LOCKED")
        plant_target = int(owned_tiles * 0.85)
        used = (animals_now + shed_geese + shed_cows + shed_sheep
                + sum(standing.get(c, 0) for c in ("WHEAT", "CARROT", "TOMATO",
                                                  "STRAWBERRY", "MELON"))
                + coop_need + past_need)
        if 4 <= day <= 25 and owned_tiles >= 25:
            fill = plant_target - used
            if fill > quotas.get("WHEAT", 0):
                quotas["WHEAT"] = max(quotas.get("WHEAT", 0), min(13, fill))
            _beyond = fill - quotas.get("WHEAT", 0)
            if _beyond > 0 and day >= 5:
                quotas["CARROT"] = max(quotas.get("CARROT", 0), min(10, _beyond))
    except Exception:
        pass
    if day <= 23:
        if day <= 2:
            # restore carrot 12 (v6: carrot-30 banh d4-5 -> $1k cache mua
            # straw + land; kain32 dung 4 -> thieu von cua so d5-8)
            quotas["CARROT"] = 12
        else:
            # ΔP3: thang giá-bên carrot (v6: binary room-gate 8/6/4/0)
            c_m = _marg("CARROT", 24, min(28, day + 5))
            if c_m >= 0.92:
                quotas["CARROT"] = 6
            elif c_m >= 0.80:
                quotas["CARROT"] = 4
            elif c_m >= 0.68:
                quotas["CARROT"] = 2
            else:
                quotas["CARROT"] = 0

    if day <= 1:
        quotas["WHEAT"] = 9
        quotas["CARROT"] = 9
        # MELON 14 MỘT ĐỢT (K13 idol): wave-1 $15k tại d12-15 tài trợ trọn
        # gói SW + straw-28 + herd — dòng tiền lớn 1 cục thắng rải nhỏ
        quotas["MELON"] = 14
        quotas.pop("STRAWBERRY", None)

    # An toan thuc an: khi wheat dung + shed < dan*1.2 -> wheat TRUOC
    # straw (kain32-bug: straw an het o d5-10, wheat chet dan, 28-33 o trong)
    try:
        _shed_w = float((shed or {}).get("WHEAT", 0) or 0)
    except Exception:
        _shed_w = 0.0
    wheat_feed_ok = (standing.get("WHEAT", 0) + _shed_w
                     >= (animals_now + goose_target + cow_target + sheep_target) * 1.2)
    if day <= 2:
        order = ["WHEAT", "MELON", "TOMATO", "CARROT", "STRAWBERRY"]
    elif not wheat_feed_ok:
        order = ["WHEAT", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]
    else:
        order = ["MELON", "STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]
    crop_tiles = {}
    remaining = len(plantable)
    for crop in order:
        want = quotas.get(crop, 0)
        if want <= 0:
            continue
        # nghèo vốn: hạt mua không nổi -> nhường ô cho wheat hôm nay
        # (trace d6-10: straw chiếm 28 ô allocation nhưng 0 hạt -> 12-20 ô
        #  trống chết trong khi wheat $10/hạt vẫn mua được)
        try:
            _sd = (seeds or {}).get(crop, 0) or 0
        except Exception:
            _sd = 0
        if crop != "WHEAT" and _sd <= 0 and money < CROPS[crop]["seed"] + 250:
            continue
        # straw đợi đợt tiền lớn: d5-10 rải nhỏ = chết kênh -> chỉ nhận
        # allocation khi mua được ÍT NHẤT 8 hạt một lần
        if crop == "STRAWBERRY" and _sd <= 0 and money < 8 * CROPS["STRAWBERRY"]["seed"] + 200:
            continue
        have = standing.get(crop, 0)
        need = max(0, want - have)
        take = min(remaining, need)
        if take > 0:
            crop_tiles[crop] = take
            remaining -= take
        if remaining <= 0:
            break
    if remaining > 0 and day <= 22:
        # HARD-4: wheat la van ap suat — lap HET o con lai khi dan an wheat
        # (feed_demand > 200 khi co dan); khong de o trong vuong
        # (fill-all 50-o wheat d11-16 = weeds 32 + $17.7k — lao dong gioi
        # han; giu 8-o buffer nhu kain31)
        if feed_demand > 200:
            extra = min(remaining, 8)
            crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + extra
        else:
            extra = min(remaining, 8)
            crop_tiles["CARROT"] = crop_tiles.get("CARROT", 0) + extra
        remaining -= extra

    if day <= 1 and plantable:
        fast = sum(v for c, v in crop_tiles.items() if c in ("WHEAT", "CARROT"))
        if fast < 0.45 * len(plantable):
            need = int(0.45 * len(plantable)) - fast
            for c in list(crop_tiles):
                if c not in ("WHEAT", "CARROT") and need > 0:
                    cut = min(crop_tiles[c], need)
                    crop_tiles[c] -= cut
                    need -= cut
                    if crop_tiles[c] == 0:
                        del crop_tiles[c]
            if need > 0:
                crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + need

    return {
        "crop_tiles": crop_tiles,
        "reserved": reserved,
        "goose_target": goose_target,
        "cow_target": cow_target,
        "sheep_target": sheep_target,
        "feed_demand": feed_demand,
        "standing": standing,
        "mode": mode,
    }


def _build_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, n_units):
    tasks = []
    stats = {"water_crit": 0, "total": 0}
    board = len(tiles)
    if not board:
        return tasks, stats

    fert_available = (shed.get("FERTILIZER", 0) if shed else 0) + sum(
        (u.get("FERTILIZER", 0) or 0) for u in inventories if isinstance(u, dict))
    wheat_available = (shed.get("WHEAT", 0) if shed else 0) + sum(
        (u.get("WHEAT", 0) or 0) for u in inventories if isinstance(u, dict))
    animals_n = 0
    hungry_n = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and "animal" in t:
                animals_n += 1
                if (t.get("consecutive_unfed", 0) or 0) >= 1 and not t.get("fed_today", False):
                    hungry_n += 1
    feed_crunch = hungry_n > 0 or (animals_n > 0 and wheat_available < animals_n + 3)

    fert_usable = 0
    for row in tiles:
        for t in row:
            if not isinstance(t, dict) or t.get("kind") != "PLANT":
                continue
            crop = t.get("crop")
            if crop not in ("WHEAT", "CARROT"):
                continue
            cd = CROPS[crop]
            age = day - t.get("planted_day", day)
            ws = (cd["max_yield_day"] + 1) // 2
            if ws <= age <= cd["max_yield_day"] and t.get("fertilized_until_day", -1) < day:
                fert_usable += 1
    fert_usable = max(0, fert_usable - fert_available)
    fert_made = 0

    for y in range(board):
        row = tiles[y]
        for x in range(board):
            t = row[x]
            if t is None or t == "LOCKED" or not isinstance(t, dict):
                continue
            kind = t.get("kind")
            if kind == "PLANT":
                crop = t.get("crop")
                cd = CROPS.get(crop)
                if cd is None:
                    continue
                age = day - t.get("planted_day", day)
                yu = t.get("yield_units", 0) or 0
                mls = t.get("max_lifespan_step", -1)
                watered = bool(t.get("watered_today", False))
                if not watered:
                    cu = t.get("consecutive_unwatered", 0) or 0
                    ws = (cd["max_yield_day"] + 1) // 2
                    in_win = (not cd["ongoing"]) and (ws <= age <= cd["max_yield_day"])
                    if in_win:
                        tasks.append(_mk(T_WATER_YIELD, x, y, "WATER"))
                        stats["water_yield"] = stats.get("water_yield", 0) + 1
                    elif cu >= 1:
                        # KAIN-9: missed yesterday -> save the PREMIUM crops
                        # (strawberry/tomato) at tier 0; wheat/carrot wait at
                        # tier 2 behind the dairy — v5 gains more than kain
                        # when unconditional CRIT watering starves FEED labor.
                        if crop in ("STRAWBERRY", "TOMATO"):
                            tasks.append(_mk(T_WATER_CRIT, x, y, "WATER"))
                            stats["water_crit"] += 1
                        else:
                            tasks.append(_mk(T_SERVICE, x, y, "WATER"))
                    else:
                        on_day = (x + y + day) % 2 == 0
                        if on_day:
                            tasks.append(_mk(T_WATER_MAINT, x, y, "WATER"))
                if yu > 0 and age >= cd["first_yield_day"]:
                    urgent = (mls >= 0 and mls - step <= 24) or (crop == "WHEAT" and feed_crunch)
                    if cd["ongoing"]:
                        ready = yu >= 4 or (mls >= 0 and mls - step <= 6) or day >= 27
                        if not ready and yu >= 3 and mls >= 0 and mls - step <= 12:
                            ready = True
                    else:
                        ready = yu >= cd["max_yield"] or age >= cd["max_yield_day"] + 1 or (
                            age >= cd["max_yield_day"] and watered)
                    if ready:
                        tasks.append(_mk(T_HARVEST_URG if urgent else T_HARVEST, x, y, "HARVEST"))
            elif "animal" in t:
                ad = ANIMALS.get(t.get("animal"))
                if ad is None:
                    continue
                starve = (t.get("consecutive_unfed", 0) or 0) >= 1
                need_feed = (not t.get("fed_today", False)) and wheat_available > 0
                need_care = not t.get("cared_today", False)
                need_fert = bool(t.get("fertilizer_available", False))
                if day <= 28 and (need_feed or need_care or need_fert):
                    tasks.append(_mk(T_SERVICE_URG if starve else T_SERVICE, x, y, "SERVICE",
                                     want_wheat=need_feed, feed=need_feed))
                yu = t.get("yield_units", 0) or 0
                if yu >= ad["max_held"] - 1:
                    tasks.append(_mk(T_HARVEST_URG, x, y, "HARVEST"))
                elif yu >= 2 or (yu > 0 and day >= 27):
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, "HARVEST"))
            elif kind == "WEED":
                tasks.append(_mk(T_DIG, x, y, "DIG"))
            elif kind in ("COOP", "PASTURE"):
                pass

    if hour <= 20:
        built = 0
        for (x, y, bop) in plan.get("reserved", []):
            if built >= 2:
                break
            if 0 <= y < board and 0 <= x < board and tiles[y][x] is None:
                animal_waiting = ((shed.get("GOOSE", 0) or 0) + (shed.get("COW", 0) or 0)
                                  + (shed.get("SHEEP", 0) or 0)) > 0
                tasks.append(_mk(T_BUILD_URG if animal_waiting else T_BUILD, x, y, bop))
                built += 1

    if shed:
        for animal in ("GOOSE", "COW", "SHEEP"):
            n_pending = shed.get(animal, 0) or 0
            if n_pending <= 0:
                continue
            struct_kind = ANIMALS[animal]["structure"]
            placed = 0
            limit = min(n_pending, 3)
            for y in range(board):
                for x in range(board):
                    if placed >= limit:
                        break
                    t = tiles[y][x]
                    if isinstance(t, dict) and t.get("kind") == struct_kind and "animal" not in t:
                        tasks.append(_mk(T_DELIVER, x, y, "DELIVER", item=animal))
                        placed += 1
                if placed >= limit:
                    break

    planted = _STATE.get(("planted", day)) or {}
    budget = []
    for crop, cap in plan.get("crop_tiles", {}).items():
        remain = cap - planted.get(crop, 0)
        have = (seeds.get(crop, 0) or 0) if seeds else 0
        if remain > 0 and have > 0:
            budget.append((crop, min(remain, have)))
    reserved_xy = {(x, y) for (x, y, _) in plan.get("reserved", [])}
    if budget and hour <= 19:
        empties = []
        for y in range(board):
            for x in range(board):
                if tiles[y][x] is None and (x, y) not in reserved_xy:
                    empties.append((x, y))
        empties.sort(key=lambda c: abs(c[0] - board // 2) + abs(c[1] - board // 2))
        flat = []
        wfirst = (plan.get("feed_demand", 0) or 0) > 0
        for crop, n in budget:
            if wfirst and crop == "WHEAT":
                flat.extend(["WHEAT"] * n)
        for crop, n in budget:
            if wfirst and crop == "WHEAT":
                continue
            flat.extend([crop] * n)
        turn_budget = n_units * max(1, 23 - hour)
        water_load = stats.get("water_crit", 0) + stats.get("water_yield", 0)
        safe_plant = int((turn_budget - water_load * 2.0) / 4)
        n_plant = min(len(flat), len(empties), max(0, safe_plant))
        # ƯU TIÊN TRỒNG NÂNG ĐỘNG: mẻ hạt lớn (>=10) + giờ sáng (<=14) ->
        # tier 1 (chỉ sau WATER_CRIT). T_PLANT=5 bị đói: d13-15 PASS 48-71
        # hành động NGHỈ trong khi 27 hạt straw nằm kho + 33 ô trống!
        _big_batch = sum(n for _, n in budget) >= 10
        _ptier = 1 if (_big_batch and hour <= 14) else T_PLANT
        for i in range(n_plant):
            x, y = empties[i]
            tasks.append(_mk(_ptier, x, y, "PLANT", crop=flat[i]))

    if fert_available > 0 and day < 25:
        made = 0
        capf = min(int(fert_available), 6)
        for y in range(board):
            for x in range(board):
                if made >= capf:
                    break
                t = tiles[y][x]
                if not isinstance(t, dict) or t.get("kind") != "PLANT":
                    continue
                crop = t.get("crop")
                if crop != "MELON":
                    continue
                cd = CROPS[crop]
                age = day - t.get("planted_day", day)
                ws = (cd["max_yield_day"] + 1) // 2
                if ws <= age <= cd["max_yield_day"] and t.get("fertilized_until_day", -1) < day:
                    tasks.append(_mk(T_FERTILIZE, x, y, "FERTILIZE"))
                    made += 1

    stats["total"] = len(tasks)
    return tasks, stats


def _drop_action(ux, uy, board):
    st = _nearest_shed_tile(ux, uy, board)
    if (ux, uy) == st:
        return ["DROP"]
    mv = _step_toward(ux, uy, st[0], st[1])
    return [mv] if mv else ["PASS"]


def _task_action(tk, ux, uy, uinv, tiles, shed, board):
    op = tk["op"]
    tx, ty = tk["x"], tk["y"]

    if op == "SERVICE":
        t = tiles[ty][tx] if 0 <= tx < board and 0 <= ty < board else None
        an = t if (isinstance(t, dict) and "animal" in t) else None
        if an is None:
            return ["PASS"]
        w = uinv.get("WHEAT", 0) or 0
        unfed = not an.get("fed_today", False)
        shed_w = (shed.get("WHEAT", 0) or 0) if shed else 0
        if unfed and w > 0:
            if (ux, uy) == (tx, ty):
                return ["FEED"]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        if unfed and w <= 0 and shed_w > 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, shed_w)
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
            else:
                mv = _step_toward(ux, uy, st[0], st[1])
                if mv:
                    return [mv]
        if (ux, uy) == (tx, ty):
            if not an.get("cared_today", False):
                return ["CARE"]
            if an.get("fertilizer_available", False):
                return ["COLLECT_FERTILIZER"]
            return ["PASS"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "FEED":
        w = uinv.get("WHEAT", 0) or 0
        if w <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, (shed.get("WHEAT", 0) or 0) if shed else 0)
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
                return ["PASS"]
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ["PASS"]
        if (ux, uy) == (tx, ty):
            return ["FEED"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "DELIVER":
        item = tk.get("item")
        if uinv.get(item, 0):
            if (ux, uy) == (tx, ty):
                return ["PLACE", item]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        st = _nearest_shed_tile(ux, uy, board)
        if (ux, uy) == st:
            if shed and (shed.get(item, 0) or 0) > 0:
                return ["PICKUP", item, 1]
            return ["PASS"]
        mv = _step_toward(ux, uy, st[0], st[1])
        return [mv] if mv else ["PASS"]

    if op == "FERTILIZE":
        f = uinv.get("FERTILIZER", 0) or 0
        if f <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(6, (shed.get("FERTILIZER", 0) or 0) if shed else 0)
                if n > 0:
                    return ["PICKUP", "FERTILIZER", n]
                return ["PASS"]
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ["PASS"]
        if (ux, uy) == (tx, ty):
            return ["FERTILIZE"]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if (ux, uy) == (tx, ty):
        if op == "PLANT":
            return ["PLANT", tk.get("crop")]
        return [op]

    mv = _step_toward(ux, uy, tx, ty)
    return [mv] if mv else ["PASS"]


def _task_still_valid(tk, tiles, board, shed, uinv):
    x, y = tk["x"], tk["y"]
    if not (0 <= x < board and 0 <= y < board):
        return False
    t = tiles[y][x]
    op = tk["op"]
    if op == "PLANT":
        return t is None
    if op == "WATER":
        return isinstance(t, dict) and t.get("kind") == "PLANT" and not t.get("watered_today", False)
    if op == "HARVEST":
        return isinstance(t, dict) and (t.get("yield_units", 0) or 0) > 0
    if op == "SERVICE":
        if not (isinstance(t, dict) and "animal" in t):
            return False
        if not t.get("fed_today", False):
            if (uinv.get("WHEAT", 0) or 0) > 0 or (shed.get("WHEAT", 0) or 0) > 0:
                return True
        return (not t.get("cared_today", False)) or bool(t.get("fertilizer_available", False))
    if op in ("FEED", "CARE"):
        return isinstance(t, dict) and "animal" in t and not t.get(
            "fed_today" if op == "FEED" else "cared_today", False)
    if op == "DIG":
        return isinstance(t, dict) and t.get("kind") == "WEED"
    if op in ("BUILD_COOP", "BUILD_PASTURE"):
        return t is None
    if op == "COLLECT_FERTILIZER":
        return isinstance(t, dict) and "animal" in t and t.get("fertilizer_available", False)
    if op == "FERTILIZE":
        return isinstance(t, dict) and t.get("kind") == "PLANT" and t.get("crop") == "MELON" \
            and t.get("fertilized_until_day", -1) < day
    if op == "DELIVER":
        return (uinv.get(tk.get("item"), 0) or 0) > 0 or (shed.get(tk.get("item"), 0) or 0) > 0
    return True


def _assign_and_act(units, tasks, tiles, shed, inventories, day, hour, board, seeds):
    uinv_cache = {}
    for i in range(len(units)):
        u = inventories[i] if i < len(inventories) and isinstance(inventories[i], dict) else {}
        uinv_cache[i] = u

    sticky = _STATE.setdefault(("sticky", day), {})
    feed_pending = 0
    for tk2 in tasks:
        if tk2["op"] == "SERVICE" and tk2.get("feed"):
            feed_pending += 1
    for i in list(sticky.keys()):
        if i >= len(units):
            del sticky[i]
            continue
        tk = sticky[i]
        if not _task_still_valid(tk, tiles, board, shed, uinv_cache[i]):
            del sticky[i]
            continue
        if feed_pending > 0 and tk["tier"] >= 2 and tk["op"] not in ("SERVICE", "FEED", "DELIVER") \
                and (uinv_cache[i].get("WHEAT", 0) or 0) > 0:
            del sticky[i]
    claimed = set()
    for i, tk in sticky.items():
        claimed.add((tk["op"], tk["x"], tk["y"]))

    free = [i for i in range(len(units)) if i not in sticky]
    plant_sticky = {}
    for i, tk in sticky.items():
        if tk["op"] == "PLANT":
            plant_sticky[tk.get("crop")] = plant_sticky.get(tk.get("crop"), 0) + 1

    def dist(i, tk):
        u = uinv_cache[i]
        if tk["op"] == "DELIVER" and (u.get(tk.get("item"), 0) or 0) > 0:
            return 0
        if tk["op"] in ("FEED", "SERVICE") and (u.get("WHEAT", 0) or 0) > 0:
            return 0
        d = abs(units[i][1] - tk["x"]) + abs(units[i][2] - tk["y"])
        if (u.get("WHEAT", 0) or 0) > 0 and tk["tier"] >= 1 and tk["op"] not in ("SERVICE", "FEED"):
            d += 6
        return d

    def skey(tk):
        return (tk["tier"], min((dist(i, tk) for i in free), default=99))

    for tk in sorted(tasks, key=skey):
        if not free:
            break
        if (tk["op"], tk["x"], tk["y"]) in claimed:
            continue
        if tk["op"] == "PLANT":
            c = tk.get("crop")
            if plant_sticky.get(c, 0) + 1 > (seeds.get(c, 0) if seeds else 0):
                continue
            plant_sticky[c] = plant_sticky.get(c, 0) + 1
        best = min(free, key=lambda i: dist(i, tk))
        sticky[best] = tk
        claimed.add((tk["op"], tk["x"], tk["y"]))
        free.remove(best)

    planted = _STATE.setdefault(("planted", day), {})
    actions = []
    for idx in range(len(units)):
        ux, uy = units[idx][1], units[idx][2]
        uinv = uinv_cache[idx]
        carried = sum(v for v in uinv.values() if _is_num(v))
        sellable = carried - (uinv.get("WHEAT", 0) or 0)
        act = ["PASS"]
        tk = sticky.get(idx)

        need_drop = sellable >= 18 or (hour >= 20 and sellable >= 3) \
            or (day >= 28 and hour >= 14 and sellable >= 1)
        if need_drop:
            act = _drop_action(ux, uy, board)
        elif tk is not None:
            act = _task_action(tk, ux, uy, uinv, tiles, shed, board)
        if isinstance(act, list) and act and act[0] == "PLANT":
            crop = act[1]
            planted[crop] = planted.get(crop, 0) + 1
        actions.append(act)
    return actions


def _wheat_all(shed, inventories):
    w = (shed.get("WHEAT", 0) or 0) if shed else 0
    for u in inventories or []:
        if isinstance(u, dict):
            w += u.get("WHEAT", 0) or 0
    return w


def _build_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan,
                  stats, tiles, shops):
    orders = []
    money = float(_g(me, "money", 0) or 0)
    hands = _g(me, "hands", None) or []
    unlocked = _g(me, "unlocked_quadrants", None) or ["NW"]
    board = len(tiles) if tiles else 10
    shed_total = sum(v for v in (shed or {}).values() if _is_num(v))

    if hour <= 5 and day < 29:
        planted_today = _STATE.get(("planted", day)) or {}
        plant_budget = sum(max(0, n - planted_today.get(c, 0))
                           for c, n in plan.get("crop_tiles", {}).items())
        workload = stats.get("total", 0) + plant_budget
        if day >= 6:
            cap = 13 if ((day >= 9 and money >= 1800) or (day >= 18 and money >= 2500)) else 12
            target_units = min(cap, max(8, 6 + money // 500))
        elif day >= 1:
            target_units = 8
        else:
            target_units = 7
        target_units = max(target_units, min(11, 1 + int(math.ceil(workload * 2.6 / max(5, 23 - hour)))))
        want = target_units - (1 + len(hands))
        n_hired = _g(me, "hires_today", 0) or 0
        cost = 0
        k = 0
        hire_floor = 60 if day <= 5 else 150
        if money > hire_floor + 88:
            hire_budget = min(money - hire_floor, max(88, money * 0.25))
        else:
            hire_budget = max(0, money - 10)
        while k < want and k < 5:
            c = _fib(n_hired + k)
            if cost + c > hire_budget:
                break
            cost += c
            orders.append(["HIRE"])
            k += 1

    bought = _STATE.setdefault(("bought", day), {"GOOSE": 0, "COW": 0, "SHEEP": 0, "LAND": 0})
    pending_animal_cost = 0

    # ==== 4 LUẬT CỨNG (top Kaggle) — LAND-FIRST, chạy TRƯỚC mọi lệnh chi ====
    # HARD-1 NE ($1k) d5-7 (fallback d8-9 chống khoá 25 ô vĩnh viễn)
    # HARD-2 SW ($2k) d10-12 (fallback d13-14)
    # HARD-3 KHÔNG BAO GIỜ mua SE — tối đa 75 ô
    # (Đặt đầu hàng đợi: autopsy seed 100 — SELL wheat d5h01 về tiền SAU khi
    #  geese+straw-seeds đã ăn sạch quỹ; land phải thấy tiền TRƯỚC ai khác)
    nq = len(unlocked)
    if nq < 3 and bought.get("LAND", 0) < 1:
        if nq == 1:
            if (5 <= day <= 7 or 8 <= day <= 9) and money >= 1000 + 100:
                orders.append(["BUY_LAND"])
                bought["LAND"] = 1
                money -= 1000
        elif nq == 2:
            if (10 <= day <= 12 or 13 <= day <= 14) and money >= 2000 + 150:
                orders.append(["BUY_LAND"])
                bought["LAND"] = 1
                money -= 2000

    # Quỹ dự trữ mua đất — mọi lệnh chi khác phải tôn trọng
    land_reserve = 0
    if nq == 1 and 3 <= day <= 9 and bought.get("LAND", 0) < 1:
        land_reserve = 1150
    elif nq == 2 and 8 <= day <= 14 and bought.get("LAND", 0) < 1:
        land_reserve = 2150
    if hour <= 8 and 1 <= day <= 22:
        struct_free = {"COOP": 0, "PASTURE": 0}
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k in struct_free and "animal" not in t:
                        struct_free[k] += 1
        animals_total = sum(1 for row in tiles for t in row
                            if isinstance(t, dict) and "animal" in t)
        wt = _wheat_all(shed, inventories)
        wheat_ripe = sum(1 for row in tiles for t in row
                         if isinstance(t, dict) and t.get("kind") == "PLANT"
                         and t.get("crop") == "WHEAT"
                         and (day - t.get("planted_day", day)) >= 3)
        wt_supply = wt + 0.8 * wheat_ripe
        pxg = float(prices.get("EGG", 0) or 0)
        pxw = float(prices.get("WOOL", 0) or 0)
        pxm = float(prices.get("MILK", 0) or 0)
        milk_shops_n = sum(1 for s in (shops or [])
                           if s in ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"))
        yarn_n = sum(1 for s in (shops or []) if s == "YARN_STORE")
        # dW WOOL-FIX: buy order COW -> SHEEP -> GOOSE (kain31 mua duoc 1 cưu
        # vs v6 7 cưu: geese an slot tien + gate wt_supply 1.3x chan cưu khi
        # dan lon; wool $2.9k vs v6 $18.7k). Gate nới 1.1x, buy 3/ngày d<=12.
        for animal, target, w0, w1 in (("COW", plan.get("cow_target", 0), 4,
                                        16 + (2 if pxm >= 200 else 0) + (2 if milk_shops_n >= 2 else 0)),
                                       ("SHEEP", plan.get("sheep_target", 0), 4,
                                        15 + (2 if pxw >= 250 else 0) + (2 if yarn_n >= 1 else 0)),
                                       ("GOOSE", plan.get("goose_target", 0), 2,
                                        14 + (2 if pxg >= 62 else 0))):
            owned = sum(1 for row in tiles for t in row
                        if isinstance(t, dict) and t.get("animal") == animal)
            owned += (shed.get(animal, 0) or 0) if shed else 0
            ad = ANIMALS[animal]
            # V4: d10-20 giữ quỹ thuê >= $1200 (autopsy: d11-13 chi $9k một
            # cục -> d14-16 money $150-950 -> units 6-7 -> weeds 20-31 ->
            # wheat chết -> đàn đói chết. Đàn phải PHA theo dòng tiền)
            cash_floor = (1200 if 10 <= day <= 20 else 250) + land_reserve
            buy_per_day = 2 if (day <= 14) else 1
            # Ưu TIÊN HẠT DÂU trước ngỗng mới d5-11: straw ROI 15-20x/đô
            # (seed $100 -> $1.5-2k) > goose 7.7x — geese ăn $900 d5 = chết
            # kênh $16k (trace: 3 geese d5 -> straw 1 hạt d6)
            if animal == "GOOSE" and 5 <= day <= 11 and owned < 3:
                _straw_n = sum(1 for row in tiles for t in row
                               if isinstance(t, dict) and t.get("kind") == "PLANT"
                               and t.get("crop") == "STRAWBERRY")
                _straw_n += (seeds or {}).get("STRAWBERRY", 0) or 0
                if _straw_n < 10:
                    continue
            if (owned < target and w0 <= day <= w1
                    and bought.get(animal, 0) < buy_per_day
                    and struct_free[ad["structure"]] > 0
                    and money >= ad["cost"] + cash_floor and shed_total < 92
                    and (wt_supply >= (animals_total + 1) * 1.1 or animals_total == 0)):
                orders.append(["BUY_ANIMAL", animal, 1])
                bought[animal] = bought.get(animal, 0) + 1
                money -= ad["cost"]
        if 4 <= day <= 15:
            try:
                for animal, tgt in (("COW", plan.get("cow_target", 0)),
                                    ("SHEEP", plan.get("sheep_target", 0))):
                    own_n = sum(1 for row in tiles for t in row
                                if isinstance(t, dict) and t.get("animal") == animal)
                    own_n += (shed.get(animal, 0) or 0) if shed else 0
                    pending_animal_cost += max(0, int(tgt) - own_n) * ANIMALS[animal]["cost"]
            except Exception:
                pending_animal_cost = 0
    pending_animal_cost = min(pending_animal_cost, 1400)

    seed_spent = 0
    if hour <= 17 and seeds is not None:
        for crop in ("WHEAT", "CARROT", "STRAWBERRY", "MELON", "TOMATO"):
            n_tiles = plan.get("crop_tiles", {}).get(crop, 0)
            if not n_tiles:
                continue
            if crop == "MELON" and day > 7 and day > 2 and False:
                continue
            if crop == "STRAWBERRY" and day < 5:
                continue
            if crop == "TOMATO" and (day < 2 or day > 16):
                continue
            have = seeds.get(crop, 0) or 0
            if have < n_tiles:
                need = n_tiles - have
                unit = CROPS[crop]["seed"]
                floor = ((30 + land_reserve) if crop == "WHEAT" else
                         (150 + land_reserve) if crop == "STRAWBERRY" else (220 + land_reserve))
                if crop == "STRAWBERRY":
                    # V3: d5-10 giữ vốn; d11-16 mua liên tục theo dòng
                    # melon-tranche (42u trả dần d12-15, không 1 cục d12)
                    floor = 150 if 11 <= day <= 16 else 900
                    try:
                        _spx = float(prices.get("STRAWBERRY", 0) or 0)
                        _sinv = float(inv.get("STRAWBERRY", MARKET_I0) or MARKET_I0)
                        # low floor only when treasury can survive the batch
                        if (_spx >= 1.25 * MARKET_PARAMS["STRAWBERRY"]["base"]
                                and _sinv <= MARKET_I0
                                and (money >= 1500 or day >= 12)):
                            floor = 200
                    except Exception:
                        pass
                if crop == "MELON":
                    floor = 700
                if crop == "MELON" and pending_animal_cost > 0:
                    floor = max(floor, min(pending_animal_cost, 1100))
                max_afford = max(0, int((money - floor) // unit)) if unit > 0 else 0
                buy = min(need, max_afford)
                if buy > 0:
                    orders.append(["BUY_SEED", crop, buy])
                    money -= buy * unit
                    seed_spent += buy * unit
            if len(orders) >= 9:
                break


    animals = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and "animal" in t)
    _wr_mult, _wr_add = (2, 2) if day <= 9 else (3, 6)
    wheat_reserve = (min(animals * _wr_mult + _wr_add, shed.get("WHEAT", 0) or 0)
                     if day < 26 and shed else 0)
    plan_animals = plan.get("goose_target", 0) + plan.get("cow_target", 0) + plan.get("sheep_target", 0)
    if animals > 0 or plan_animals > 0:
        shed_wheat = (shed.get("WHEAT", 0) or 0) if shed else 0
        # đồng bộ mức giữ: mua về đúng reserve, bán mọi phần trên reserve
        # (fix dao động d3: SELL 2 -> BUY 2 lặp cả ngày, mất spread giá)
        wheat_want = wheat_reserve
        # V3 FEED-LAI: v6 mua $34k wheat = ARBITRAGE LAO ĐỘNG (đổi tiền lấy
        # tay cho kênh $250-280) — tự trồng 100% làm đôi lao động nông trại,
        # 14 thú đói chết d18-22 (autopsy seed 100). Trồng 18-20 ô + MUA khi
        # đàn > 8 hoặc cấp báo.
        wheat_standing_n = sum(1 for row in tiles for t in row
                               if isinstance(t, dict) and t.get("kind") == "PLANT"
                               and t.get("crop") == "WHEAT")
        if shed_wheat < wheat_want and money >= 400:
            need = min(10, wheat_want - shed_wheat)
            pw = _price("WHEAT", inv.get("WHEAT", MARKET_I0) - 1)
            afford = int((money * 0.35) // pw) if pw > 0 else 0
            n = min(need, afford)
            acute = shed_wheat < 6
            # KAIN-11: v5 out-dairied us buying $42 wheat (its 15-animal herd
            # converts wheat->milk $265). Allow pricier feed ONLY when the
            # dairy pays for it (milk >= $200) and the herd target is unmet.
            _pxm = float(prices.get("MILK", 0) or 0)
            _pxw2 = float(prices.get("WOOL", 0) or 0)
            _dairy_deep = (_pxm >= 200 or _pxw2 >= 220) and day <= 23
            _tgt_unmet = (animals < (plan.get("cow_target", 0) + plan.get("sheep_target", 0)))
            if n >= 1 and (pw <= 38 or (acute and pw <= 62)
                           or (_dairy_deep and _tgt_unmet and pw <= 52)):
                orders.append(["BUY_PRODUCT", "WHEAT", n])
                money -= n * pw

    absorb_key = ("absorb", day)
    if absorb_key not in _STATE:
        _STATE[absorb_key] = _forward_absorb(day, 0, shops)
    absorb = _STATE[absorb_key]
    glutted = set()
    for it in PRODUCTS:
        if it in ("FERTILIZER", "MELON"):
            continue
        over = inv.get(it, MARKET_I0) - MARKET_I0
        pr_now = prices.get(it, 0) or 0
        if over > absorb.get(it, 0) * 0.8 and pr_now < 0.75 * MARKET_PARAMS[it]["base"]:
            glutted.add(it)

    # KAIN-15: 3 days of feed reserve (the $52 dairy-gated feed buys work;
    # sell the rest — v5 outsold us 880u vs 684u on wheat).

    # v6 ΔF (E8-lite): drain-aware endgame — d22-27 nếu drain còn đủ hút
    # TOÀN BỘ nguồn chờ bán thì KHÔNG hạ ngưỡng (bán dần vào drain giá đẹp)
    absorb_rest = {}
    pipe_rest = {}
    try:
        if 22 <= day <= 27:
            absorb_rest = _forward_absorb(day, 0, shops)
            pipe_rest = _pipe_rest(tiles, day)
    except Exception:
        absorb_rest, pipe_rest = {}, {}

    def _hold(it):
        h = HOLD.get(it, 0.90)
        if it in glutted:
            return min(h, 0.40)
        if 22 <= day <= 27:
            try:
                _np_ = float(shed.get(it, 0) or 0) + float(pipe_rest.get(it, 0.0) or 0.0)
                if _np_ > 0 and absorb_rest.get(it, 0.0) >= _np_ * 1.1:
                    return h
            except Exception:
                pass
        if day >= 28:
            return 0.004
        if day >= 27:
            return min(h, 0.20)
        if day >= 26:
            return min(h, 0.45)
        if day >= 22:
            return min(h, 0.70)
        if it == "MELON" and day >= 24:
            return min(h, 0.30)
        if it == "MELON" and day >= 21:
            return min(h, 0.42)
        if shed_total >= 80:
            return min(h, 0.72)
        if money < 250:
            return min(h, 0.65)
        return h

    cands = []
    if shed:
        for it in PRODUCTS:
            if it == "FERTILIZER" and day < 26:
                nf = shed.get("FERTILIZER", 0) or 0
                if nf > 2 and day >= 1:
                    k = _sell_count("FERTILIZER", nf - 2, inv.get("FERTILIZER", MARKET_I0), FERT_FLOOR)
                    if k > 0:
                        cands.append((k * 60, ["SELL", "FERTILIZER", k]))
                continue
            n = shed.get(it, 0) or 0
            if it == "WHEAT":
                n = max(0, n - wheat_reserve)
            if n <= 0:
                continue
            thresh = _hold(it) * MARKET_PARAMS[it]["base"]
            k = _sell_count(it, n, inv.get(it, MARKET_I0), thresh)
            # KAIN-16: deep-drain channels (MILK/WOOL/EGG) recover price
            # between hours as the town drains inventory — tranche at 8/hour
            # instead of dumping 19 at once down the curve (v5 sells 3-9 per
            # order and banks the recovery premium).
            if k > 8 and it in ("MILK", "WOOL", "EGG") and day < 26:
                k = 8
            if k > 0:
                cands.append((k * (prices.get(it, 0) or 0), ["SELL", it, k]))
    cands.sort(key=lambda c: -c[0])
    for _, o in cands:
        if len(orders) >= MAX_ORDERS:
            break
        orders.append(o)

    return orders[:MAX_ORDERS]


def _agent(obs):
    player = _g(obs, "player", 0)
    farms = _g(obs, "farms", None) or []
    if not farms or player is None or not (0 <= player < len(farms)):
        return {"farmer": ["PASS"], "hands": [], "market": []}
    me = farms[player]
    day = _g(obs, "day", 0) or 0
    hour = _g(obs, "hour", 0) or 0
    step = day * TURN_PER_DAY + hour
    if day == 0 and hour == 0:
        _STATE.clear()

    tiles = _g(me, "tiles", None) or []
    board = len(tiles)
    if board == 0:
        return {"farmer": ["PASS"], "hands": [], "market": []}

    private = _g(obs, "private", None) or {}
    market = _g(obs, "market", None) or {}
    town = _g(obs, "town", None) or {}
    shed = _g(private, "shed", None) or {}
    seeds = _g(private, "seeds", None) or {}
    inventories = _g(private, "inventories", None) or []
    prices = _g(market, "prices", None) or {}
    inv = _g(market, "inventory", None) or {}
    shops = _g(town, "unlocked_shops", None) or []
    opp = farms[1 - player] if len(farms) > 1 else None

    tm = _STATE.setdefault("tm", {})
    _tm_step(tm, step, inv, shops)

    pkey = ("plan", day)
    if pkey not in _STATE:
        mc = sum(1 for row in tiles for t in row
                 if isinstance(t, dict) and t.get("animal") == "COW")
        mg = sum(1 for row in tiles for t in row
                 if isinstance(t, dict) and t.get("animal") == "GOOSE")
        msp = sum(1 for row in tiles for t in row
                  if isinstance(t, dict) and t.get("animal") == "SHEEP")
        _bayes_step(tm, day, opp, (mc, mg, msp), float(_g(me, "money", 0) or 0))
        _STATE[pkey] = _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp,
                                   float(_g(me, "money", 0) or 0), tm)
    plan = _STATE[pkey]

    fpos = _g(me, "farmer", None) or [board // 2 - 1, board // 2 - 1]
    units = [(0, int(fpos[0]), int(fpos[1]))]
    for i, h in enumerate(_g(me, "hands", None) or []):
        units.append((i + 1, int(h[0]), int(h[1])))

    tasks, stats = _build_tasks(tiles, shed, seeds, plan, day, hour, step,
                                inventories, len(units))

    orders = _build_orders(me, shed, seeds, inventories, inv, prices, day,
                           hour, plan, stats, tiles, shops)
    _tm_orders(tm, orders)

    actions = _assign_and_act(units, tasks, tiles, shed, inventories, day,
                              hour, board, seeds)

    return {"farmer": actions[0], "hands": actions[1:], "market": orders}


def agent(obs):
    try:
        return _agent(obs)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
