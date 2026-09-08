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

T_WATER_CRIT = 0
T_SERVICE_URG = 0
T_HARVEST_URG = 2
T_DELIVER = 2
T_BUILD_URG = 2
T_SERVICE = 2
T_WATER_YIELD = 3
T_WATER_MAINT = 3
T_BUILD = 4
T_HARVEST_ANIMAL = 4
T_HARVEST = 5
T_PLANT = 5
T_DIG = 5
T_FERTILIZE = 6

STATE_HERD_CAP = 16
FERT_FLOOR = 37
MELON_TILES = 10
STRAW_TILES = 14
TOMATO_TILES = 8
PREMIUM_ITEMS = ("MILK", "WOOL", "STRAWBERRY", "MELON")

_STATE = {}


def _g(o, k, d=None):
    try:
        if isinstance(o, dict):
            return o.get(k, d)
        return getattr(o, k, d)
    except Exception:
        return d


def _num(v):
    try:
        if isinstance(v, bool):
            return 0
        if isinstance(v, (int, float)):
            return int(v)
    except Exception:
        pass
    return 0


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
                ypc = {"WHEAT": 5.0, "CARROT": 3.0, "TOMATO": 6.0, "STRAWBERRY": 6.0, "MELON": 6.0}
                if crop in ypc:
                    pipe[crop] += ypc[crop]
            elif "animal" in t:
                an = t.get("animal")
                if an in ANIMALS:
                    pipe[ANIMALS[an]["product"]] += 30.0
    if shed:
        for it in PRODUCTS:
            v = shed.get(it, 0)
            if _is_num(v):
                pipe[it] += v
    return pipe


def _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp_farm, money, tm):
    absorb = _forward_absorb(day, 0, shops)

    coops = pastures = animals_now = 0
    cows_now = geese_now = sheep_now = 0
    standing = {c: 0 for c in CROPS}
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                k = t.get("kind")
                if k == "COOP":
                    coops += 1
                elif k == "PASTURE":
                    pastures += 1
                a = t.get("animal")
                if a == "COW":
                    cows_now += 1
                elif a == "GOOSE":
                    geese_now += 1
                elif a == "SHEEP":
                    sheep_now += 1
                if a in ANIMALS:
                    animals_now += 1
                if k == "PLANT":
                    cc = t.get("crop")
                    if cc in standing:
                        standing[cc] += 1
    shed_geese = _num(shed.get("GOOSE")) if shed else 0
    shed_cows = _num(shed.get("COW")) if shed else 0
    shed_sheep = _num(shed.get("SHEEP")) if shed else 0

    opp_cows = opp_geese = opp_sheep = 0
    opp_tiles = _g(opp_farm, "tiles", None) if opp_farm else None
    if opp_tiles:
        for row in opp_tiles:
            for t in row:
                if isinstance(t, dict) and "animal" in t:
                    a = t.get("animal")
                    if a == "COW":
                        opp_cows += 1
                    elif a == "GOOSE":
                        opp_geese += 1
                    elif a == "SHEEP":
                        opp_sheep += 1

    # ---- Module E: presence targets + adaptive herd via measured market offsets (T8-safe)
    milk_off = MARKET_I0 - inv.get("MILK", MARKET_I0)
    wool_off = MARKET_I0 - inv.get("WOOL", MARKET_I0)
    straw_off = MARKET_I0 - inv.get("STRAWBERRY", MARKET_I0)
    tomato_off = MARKET_I0 - inv.get("TOMATO", MARKET_I0)
    egg_off = MARKET_I0 - inv.get("EGG", MARKET_I0)
    opp_milk_flow = 0.0
    opp_wheat_flow = 0.0
    if tm:
        hist = tm.get("net_hist") or []
        if len(hist) >= 2:
            last2 = hist[-2:]
            opp_milk_flow = sum(h.get("MILK", 0.0) for h in last2) / len(last2)
            opp_wheat_flow = sum(h.get("WHEAT", 0.0) for h in last2) / len(last2)
    milk_glut = milk_off < 25 and opp_milk_flow > 1.0
    cow_target = 0
    if 6 <= day <= 18:
        cow_target = 7
        if cows_now + opp_cows >= 11:
            cow_target = min(cow_target, cows_now)
        elif opp_cows >= 8:
            cow_target = 4
        if milk_glut or milk_off < 0:
            cow_target = min(cow_target, cows_now)
        if milk_off > 70 and opp_cows <= 1 and day >= 12:
            cow_target = 8
    goose_target = 0
    if 1 <= day <= 16:
        goose_target = 5
        if egg_off < -40:
            goose_target = 4
        if opp_geese >= 8:
            goose_target = 3
    sheep_target = 0
    if 8 <= day <= 22:
        sheep_target = 2
        if wool_off > 60:
            sheep_target = 3
        if wool_off > 150:
            sheep_target = 4
        if opp_sheep >= 7 or sheep_now + opp_sheep >= 8:
            sheep_target = min(sheep_target, 1)
    total_target = goose_target + cow_target + sheep_target
    if total_target > STATE_HERD_CAP:
        over = total_target - STATE_HERD_CAP
        cut = min(goose_target, over)
        goose_target -= cut
        over -= cut
        cut = min(sheep_target, over)
        sheep_target -= cut
        over -= cut
        cut = min(cow_target, over)
        cow_target -= cut
    herd_owned = animals_now + shed_geese + shed_cows + shed_sheep
    if herd_owned >= STATE_HERD_CAP:
        goose_target = min(goose_target, geese_now + shed_geese)
        cow_target = min(cow_target, cows_now + shed_cows)
        sheep_target = min(sheep_target, sheep_now + shed_sheep)

    # ---- structures: build ahead at most +1 beyond real/pending animals
    coop_need = min(max(0, goose_target + shed_geese - coops), geese_now + shed_geese + 1, 2)
    past_need = min(max(0, cow_target + shed_cows + sheep_target + shed_sheep - pastures),
                    cows_now + shed_cows + sheep_now + shed_sheep + 1, 2)

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

    herd_planned = max(herd_owned, goose_target + cow_target + sheep_target)
    feed_demand = herd_planned * max(0, 29 - day)

    # ---- Module B: portfolio quotas (adaptive to measured scarcity, continuous cycles)
    quotas = {}
    wheat_off = MARKET_I0 - inv.get("WHEAT", MARKET_I0)
    melon_ok = inv.get("MELON", MARKET_I0) < MARKET_I0 + 30
    if (day <= 5 or (10 <= day <= 14 and melon_ok)) and standing.get("MELON", 0) < MELON_TILES:
        quotas["MELON"] = MELON_TILES
    if 3 <= day <= 15:
        if straw_off > 150:
            s_cap = 18
        elif straw_off < -20:
            s_cap = 8
        else:
            s_cap = STRAW_TILES
        quotas["STRAWBERRY"] = s_cap
    if 8 <= day <= 16:
        if tomato_off > 100:
            quotas["TOMATO"] = 11
        else:
            quotas["TOMATO"] = TOMATO_TILES
    elif 17 <= day <= 18:
        quotas["TOMATO"] = 6
    if day <= 26:
        if day == 0:
            quotas["WHEAT"] = 10
        elif day == 1:
            quotas["WHEAT"] = 16
        else:
            if wheat_off < -80:
                wheat_cap = 26
            elif wheat_off < -40:
                wheat_cap = 22
            else:
                wheat_cap = 20
            quotas["WHEAT"] = min(wheat_cap, max(10, int(herd_owned * 1.15) + 8))
    if day <= 6:
        quotas["CARROT"] = 8 if day == 0 else 16
    elif day <= 10:
        quotas["CARROT"] = 6

    crop_tiles = {}
    remaining = len(plantable)
    if day <= 4:
        order = ["WHEAT", "CARROT", "MELON", "STRAWBERRY", "TOMATO"]
    elif wheat_off < -150:
        order = ["WHEAT", "MELON", "STRAWBERRY", "TOMATO", "CARROT"]
    else:
        order = ["MELON", "STRAWBERRY", "TOMATO", "WHEAT", "CARROT"]
    for crop in order:
        want = quotas.get(crop, 0)
        if want <= 0:
            continue
        have = standing.get(crop, 0)
        need = max(0, want - have)
        take = min(remaining, need)
        if take > 0:
            crop_tiles[crop] = take
            remaining -= take
        if remaining <= 0:
            break
    if remaining > 0 and 5 <= day <= 23:
        fill = min(remaining, 12)
        crop_tiles["WHEAT"] = crop_tiles.get("WHEAT", 0) + fill
        remaining -= fill

    return {
        "crop_tiles": crop_tiles,
        "reserved": reserved,
        "goose_target": goose_target,
        "cow_target": cow_target,
        "sheep_target": sheep_target,
        "feed_demand": feed_demand,
        "standing": standing,
        "herd_planned": herd_planned,
        "absorb": absorb,
        "sheep_per_day": 1,
        "milk_contest": opp_milk_flow > 0.5,
        "opp_wheat_buying": opp_wheat_flow <= -2.0,
    }


def _prod_day(cd, planted, day):
    if not cd["ongoing"]:
        return False
    dsf = (day + 1) - planted - cd["first_yield_day"]
    if dsf < 0 or dsf % cd["interval"] != 0:
        return False
    count = dsf // cd["interval"] + 1
    return count <= cd["max_yield"]


def _build_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, n_units):
    tasks = []
    stats = {"water_crit": 0, "total": 0}
    board = len(tiles)
    if not board:
        return tasks, stats

    fert_available = _num(shed.get("FERTILIZER")) if shed else 0
    fert_available += sum(_num(u.get("FERTILIZER")) for u in inventories if isinstance(u, dict))
    wheat_available = _num(shed.get("WHEAT")) if shed else 0
    wheat_available += sum(_num(u.get("WHEAT")) for u in inventories if isinstance(u, dict))

    fert_targets = []
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
                planted = t.get("planted_day", day)
                age = day - planted
                yu = _num(t.get("yield_units"))
                mls = t.get("max_lifespan_step", -1)
                watered = bool(t.get("watered_today", False))
                if not watered and day < 29:
                    cu = _num(t.get("consecutive_unwatered"))
                    ws = (cd["max_yield_day"] + 1) // 2
                    in_win = (not cd["ongoing"]) and (ws <= age <= cd["max_yield_day"])
                    prod = _prod_day(cd, planted, day)
                    fert_alive = t.get("fertilized_until_day", -1) >= day
                    if cu >= 1:
                        tasks.append(_mk(T_WATER_CRIT, x, y, "WATER"))
                        stats["water_crit"] += 1
                    elif in_win:
                        wt = 2 if (crop == "WHEAT" and yu < cd["max_yield"]) else T_WATER_YIELD
                        tasks.append(_mk(wt, x, y, "WATER"))
                    elif prod and fert_alive:
                        tasks.append(_mk(T_WATER_YIELD, x, y, "WATER"))
                    elif crop in ("MELON", "STRAWBERRY", "TOMATO") and (x + y + day) % 2 == 0:
                        tasks.append(_mk(2, x, y, "WATER"))
                    elif (x + y + day) % 2 == 0:
                        tasks.append(_mk(3, x, y, "WATER"))
                if yu > 0 and age >= cd["first_yield_day"]:
                    urgent = mls >= 0 and mls - step <= 4
                    if cd["ongoing"]:
                        ready = yu >= 4 or (mls >= 0 and mls - step <= 6) or day >= 27
                    else:
                        ready = yu >= cd["max_yield"] or age >= cd["max_yield_day"] + 1 or (
                            age >= cd["max_yield_day"] and watered)
                    if ready:
                        ht = 3 if crop == "WHEAT" else (T_HARVEST_URG if urgent else T_HARVEST)
                        tasks.append(_mk(ht, x, y, "HARVEST"))
                # fertilizer targets: ongoing-on-production-day first, then wheat window
                if t.get("fertilized_until_day", -1) < day:
                    if _prod_day(cd, planted, day):
                        fert_targets.append((0, x, y))
                    elif crop == "WHEAT":
                        ws = (cd["max_yield_day"] + 1) // 2
                        if ws <= age <= cd["max_yield_day"] and yu < cd["max_yield"]:
                            fert_targets.append((1, x, y))
            elif "animal" in t:
                ad = ANIMALS.get(t.get("animal"))
                if ad is None:
                    continue
                starve = _num(t.get("consecutive_unfed")) >= 1
                need_feed = (not t.get("fed_today", False)) and wheat_available > 0
                need_care = (not t.get("cared_today", False))
                need_fert = bool(t.get("fertilizer_available", False))
                if need_feed and need_care and need_fert:
                    tasks.append(_mk(T_SERVICE_URG if starve else T_SERVICE, x, y, "SERVICE",
                                     want_wheat=True, feed=True))
                elif day <= 28 and (need_feed or need_care or need_fert):
                    if starve and not need_feed and not need_care and not need_fert:
                        continue
                    tasks.append(_mk(T_SERVICE_URG if starve else T_SERVICE, x, y, "SERVICE",
                                     want_wheat=need_feed, feed=need_feed))
                yu = _num(t.get("yield_units"))
                a_name = t.get("animal")
                shed_total_now = sum(v for v in (shed or {}).values() if _is_num(v))
                if yu >= ad["max_held"] - 1:
                    tasks.append(_mk(T_HARVEST_URG, x, y, "HARVEST"))
                elif day >= 27 and yu > 0:
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, "HARVEST"))
                elif a_name == "GOOSE" and yu >= 3:
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, "HARVEST"))
                elif a_name != "GOOSE" and yu >= 4 and shed_total_now < 80:
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, "HARVEST"))
            elif kind == "WEED":
                if day <= 27:
                    tasks.append(_mk(5, x, y, "DIG"))

    if hour <= 20:
        built = 0
        for (x, y, bop) in plan.get("reserved", []):
            if built >= 3:
                break
            if 0 <= y < board and 0 <= x < board and tiles[y][x] is None:
                animal_waiting = (_num(shed.get("GOOSE")) + _num(shed.get("COW"))
                                  + _num(shed.get("SHEEP"))) > 0
                tasks.append(_mk(T_BUILD_URG if animal_waiting else T_BUILD, x, y, bop))
                built += 1

    if shed and hour <= 21:
        for animal in ("COW", "SHEEP", "GOOSE"):
            n_pending = _num(shed.get(animal))
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
        have = _num(seeds.get(crop)) if seeds else 0
        if remain > 0 and have > 0:
            budget.append((crop, min(remain, have)))
    reserved_xy = {(x, y) for (x, y, _) in plan.get("reserved", [])}
    if budget and hour <= 19 and day <= 25:
        empties = []
        for y in range(board):
            for x in range(board):
                if tiles[y][x] is None and (x, y) not in reserved_xy:
                    empties.append((x, y))
        empties.sort(key=lambda c: abs(c[0] - board // 2) + abs(c[1] - board // 2))
        flat = []
        for crop, n in budget:
            flat.extend([crop] * n)
        turn_budget = n_units * max(1, 23 - hour)
        water_load = stats.get("water_crit", 0)
        safe_plant = int((turn_budget - water_load * 2.0) / 3)
        n_plant = min(len(flat), len(empties), max(0, safe_plant))
        plant_tier = T_PLANT
        if plan.get("feed_demand", 0) > 150:
            plant_tier = 4
        for i in range(n_plant):
            x, y = empties[i]
            tasks.append(_mk(plant_tier, x, y, "PLANT", crop=flat[i]))

    if fert_available > 0 and day < 27:
        fert_targets.sort()
        capf = min(int(fert_available), 7)
        for prio, x, y in fert_targets[:capf]:
            tier = 3 if prio == 0 else 4
            tasks.append(_mk(tier, x, y, "FERTILIZE"))

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
        w = _num(uinv.get("WHEAT"))
        if (ux, uy) == (tx, ty):
            if not an.get("fed_today", False) and w > 0:
                return ["FEED"]
            if not an.get("cared_today", False):
                return ["CARE"]
            if an.get("fertilizer_available", False):
                return ["COLLECT_FERTILIZER"]
            return ["PASS"]
        if not an.get("fed_today", False) and w <= 0 and tk.get("want_wheat") \
                and _num(shed.get("WHEAT")) > 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(4, _num(shed.get("WHEAT")))
                if n > 0:
                    return ["PICKUP", "WHEAT", n]
            else:
                mv = _step_toward(ux, uy, st[0], st[1])
                if mv:
                    return [mv]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ["PASS"]

    if op == "DELIVER":
        item = tk.get("item")
        if _num(uinv.get(item)) > 0:
            if (ux, uy) == (tx, ty):
                return ["PLACE", item]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ["PASS"]
        st = _nearest_shed_tile(ux, uy, board)
        if (ux, uy) == st:
            if shed and _num(shed.get(item)) > 0:
                return ["PICKUP", item, 1]
            return ["PASS"]
        mv = _step_toward(ux, uy, st[0], st[1])
        return [mv] if mv else ["PASS"]

    if op == "FERTILIZE":
        f = _num(uinv.get("FERTILIZER"))
        if f <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(6, _num(shed.get("FERTILIZER")))
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


def _task_still_valid(tk, tiles, board, shed, uinv, day):
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
        return isinstance(t, dict) and _num(t.get("yield_units")) > 0
    if op == "SERVICE":
        if not (isinstance(t, dict) and "animal" in t):
            return False
        if not t.get("fed_today", False):
            if _num(uinv.get("WHEAT")) > 0 or _num(shed.get("WHEAT")) > 0:
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
        return isinstance(t, dict) and t.get("kind") == "PLANT" \
            and t.get("fertilized_until_day", -1) < day
    if op == "DELIVER":
        return _num(uinv.get(tk.get("item"))) > 0 or _num(shed.get(tk.get("item"))) > 0
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
        if not _task_still_valid(tk, tiles, board, shed, uinv_cache[i], day):
            del sticky[i]
            continue
        if feed_pending > 0 and tk["tier"] >= 2 and tk["op"] not in ("SERVICE", "FEED", "DELIVER") \
                and _num(uinv_cache[i].get("WHEAT")) > 0:
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
        if tk["op"] == "DELIVER" and _num(u.get(tk.get("item"))) > 0:
            return 0
        if tk["op"] in ("FEED", "SERVICE") and _num(u.get("WHEAT")) > 0:
            return 0
        d = abs(units[i][1] - tk["x"]) + abs(units[i][2] - tk["y"])
        if (units[i][1] // 5) != (tk["x"] // 5) or (units[i][2] // 5) != (tk["y"] // 5):
            d += 4
        if _num(u.get("WHEAT")) > 0 and tk["tier"] >= 1 and tk["op"] not in ("SERVICE", "FEED"):
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
            if plant_sticky.get(c, 0) + 1 > (_num(seeds.get(c)) if seeds else 0):
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
        sellable = carried - _num(uinv.get("WHEAT"))
        act = ["PASS"]
        tk = sticky.get(idx)

        need_drop = sellable >= 14 or (hour >= 18 and sellable >= 3) \
            or (day >= 29 and sellable >= 1) \
            or (day >= 27 and hour >= 12 and sellable >= 1)
        if need_drop:
            act = _drop_action(ux, uy, board)
        elif tk is not None:
            act = _task_action(tk, ux, uy, uinv, tiles, shed, board)
        if isinstance(act, list) and act and act[0] == "PLANT":
            crop = act[1]
            planted[crop] = planted.get(crop, 0) + 1
        actions.append(act)
    return actions


def _build_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan,
                  stats, tiles, shops, tm):
    orders = []
    money = float(_g(me, "money", 0) or 0)
    hands = _g(me, "hands", None) or []
    unlocked = _g(me, "unlocked_quadrants", None) or ["NW"]
    board = len(tiles) if tiles else 10
    shed_total = sum(v for v in (shed or {}).values() if _is_num(v))
    herd = plan.get("herd_planned", 0)

    # ---- HIRE
    if hour <= 5 and day < 29:
        planted_today = _STATE.get(("planted", day)) or {}
        plant_budget = sum(max(0, n - planted_today.get(c, 0))
                           for c, n in plan.get("crop_tiles", {}).items())
        workload = stats.get("total", 0) + plant_budget
        if day == 0:
            target_units = 7
        elif day <= 2:
            target_units = 8
        elif day <= 5:
            target_units = 10
        else:
            target_units = 12
            if workload > 85:
                target_units += 1
            if workload > 110:
                target_units += 2
            if day >= 22:
                target_units -= 2
        target_units = min(14, target_units)
        want = target_units - (1 + len(hands))
        n_hired = _g(me, "hires_today", 0) or 0
        cost = 0
        k = 0
        hire_floor = 60 if day <= 8 else 150
        hire_budget = min(money - hire_floor, max(88, money * 0.25))
        if hire_budget < 88 and money >= hire_floor + 88:
            hire_budget = 88
        while k < want and k < 4:
            c = _fib(n_hired + k)
            if cost + c > hire_budget:
                break
            cost += c
            orders.append(["HIRE"])
            k += 1

    # ---- BUY_SEED (wheat feed-security first; straw in affordable chunks)
    if hour <= 17 and seeds is not None:
        if day <= 3:
            seed_order = ("WHEAT", "CARROT", "MELON", "STRAWBERRY", "TOMATO")
        else:
            seed_order = ("WHEAT", "MELON", "STRAWBERRY", "TOMATO", "CARROT")
        reserve = 300 if day <= 8 else 500
        spend_cap = max(0.0, money - reserve)
        spent = 0.0
        for crop in seed_order:
            n_tiles = plan.get("crop_tiles", {}).get(crop, 0)
            if not n_tiles:
                continue
            have = _num(seeds.get(crop))
            if have < n_tiles:
                need = n_tiles - have
                unit = CROPS[crop]["seed"]
                chunk = need
                if crop == "STRAWBERRY" and day <= 12:
                    chunk = min(need, 6)
                afford = int((spend_cap - spent) // unit) if unit > 0 else 0
                buy = min(chunk, max(0, afford))
                if buy > 0:
                    orders.append(["BUY_SEED", crop, buy])
                    spent += buy * unit
                    money -= buy * unit
            if len(orders) >= 6:
                break

    # ---- BUY_ANIMAL (presence ramp, cash-first)
    bought = _STATE.setdefault(("bought", day), {"GOOSE": 0, "COW": 0, "SHEEP": 0, "LAND": 0})
    if hour <= 8 and 1 <= day <= 21:
        struct_free = {"COOP": 0, "PASTURE": 0}
        struct_total = {"COOP": 0, "PASTURE": 0}
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    k = t.get("kind")
                    if k in struct_free:
                        struct_total[k] += 1
                        if "animal" not in t:
                            struct_free[k] += 1
        animals_total = sum(1 for row in tiles for t in row
                            if isinstance(t, dict) and "animal" in t)
        shed_animals = _num(shed.get("GOOSE")) + _num(shed.get("COW")) + _num(shed.get("SHEEP"))
        wt = _num(shed.get("WHEAT"))
        wheat_standing = sum(1 for row in tiles for t in row
                             if isinstance(t, dict) and t.get("kind") == "PLANT"
                             and t.get("crop") == "WHEAT")
        wt_supply = wt + 0.8 * wheat_standing
        seq = []
        if day <= 5:
            seq = [("GOOSE", 2)]
        elif day <= 12:
            seq = [("COW", 2), ("GOOSE", 1)]
        elif day <= 18:
            seq = [("COW", 2), ("GOOSE", 1), ("SHEEP", plan.get("sheep_per_day", 1))]
        elif day <= 21:
            seq = [("SHEEP", plan.get("sheep_per_day", 1)), ("GOOSE", 1)]
        windows = {"GOOSE": (1, 16), "COW": (5, 18), "SHEEP": (8, 21)}
        for animal, per_day in seq:
            ad = ANIMALS[animal]
            owned = sum(1 for row in tiles for t in row
                        if isinstance(t, dict) and t.get("animal") == animal)
            owned += _num(shed.get(animal))
            target = plan.get(animal.lower() + "_target", 0)
            w0, w1 = windows[animal]
            if not (w0 <= day <= w1) or owned >= target:
                continue
            n_slots = per_day - bought.get(animal, 0)
            while n_slots > 0 and owned < target:
                if struct_free[ad["structure"]] <= 0 and shed_animals >= 5:
                    break
                cash_gate = ad["cost"] + (900 if animal == "COW" else 600)
                if money < cash_gate:
                    break
                if wheat_standing + shed_animals * 0 + int(money // 45) < (animals_total + shed_animals + 3) and day >= 5:
                    break
                orders.append(["BUY_ANIMAL", animal, 1])
                bought[animal] = bought.get(animal, 0) + 1
                money -= ad["cost"]
                owned += 1
                n_slots -= 1
                if struct_free[ad["structure"]] > 0:
                    struct_free[ad["structure"]] -= 1

    # ---- BUY_LAND
    nq = len(unlocked)
    if nq < 4 and bought.get("LAND", 0) < 1 and hour <= 10:
        owned_empty = sum(1 for row in tiles for t in row if t is None)
        price = LAND_PRICES[nq - 1]
        if nq == 1:
            last_day, gate, buffer = 3, 1.0, 800
        elif nq == 2:
            last_day, gate, buffer = 13, 1.15, 800
        else:
            last_day, gate, buffer = 18, 1.2, 800
        if day <= last_day and (owned_empty <= 10 or day <= 2 or money >= price * gate) \
                and money >= price + buffer:
            orders.append(["BUY_LAND"])
            bought["LAND"] = 1
            money -= price

    # ---- BUY_PRODUCT WHEAT (make-vs-buy + emergency feed protection)
    buying_wheat = False
    animals_now = sum(1 for row in tiles for t in row
                      if isinstance(t, dict) and "animal" in t)
    wheat_standing_s = sum(1 for row in tiles for t in row
                           if isinstance(t, dict) and t.get("kind") == "PLANT"
                           and t.get("crop") == "WHEAT")
    if hour <= 20 and day <= 28:
        shed_wheat = _num(shed.get("WHEAT"))
        feed_gap = animals_now * 1.2 + 2
        feed_stress = (shed_wheat + 0.8 * wheat_standing_s) < animals_now * 1.5
        if day <= 8 and shed_wheat < max(6, feed_gap) and money >= 500:
            pw = _price("WHEAT", inv.get("WHEAT", MARKET_I0) - 1)
            if pw <= 28:
                need = min(10, int(max(6, feed_gap) - shed_wheat))
                afford = int((money - 300) // pw) if pw > 0 else 0
                n = min(need, afford)
                if n >= 1:
                    orders.append(["BUY_PRODUCT", "WHEAT", n])
                    money -= n * pw
                    buying_wheat = True
        elif animals_now >= 4 and (feed_stress or shed_wheat < max(4, animals_now)) and money >= 400:
            pw = _price("WHEAT", inv.get("WHEAT", MARKET_I0) - 1)
            cap = 58 if feed_stress else 45
            if pw <= cap:
                need = min(12, int(animals_now * 1.5) - shed_wheat)
                afford = int((money - 350) // pw) if pw > 0 else 0
                n = max(0, min(need, afford))
                if n >= 1:
                    orders.append(["BUY_PRODUCT", "WHEAT", n])
                    money -= n * pw
                    buying_wheat = True

    # ---- SELL
    glutted = set()
    if tm:
        for p, until in (tm.get("pause") or {}).items():
            if step_now(tm) < until:
                glutted.add(p)

    wheat_reserve = 0
    if day < 27 and shed:
        base_res = animals_now * 2 + 4
        if wheat_standing_s < animals_now:
            base_res = animals_now * 2 + 10
        wheat_reserve = min(base_res, _num(shed.get("WHEAT")))

    def _flow_h(it, off):
        if it in ("MILK", "WOOL"):
            if off >= 140:
                return 1.25
            if off >= 70:
                return 1.05
            if off >= 25:
                return 0.94
            if off >= -10:
                return 0.88
            return 0.80
        if off >= 140:
            return 1.28
        if off >= 70:
            return 1.10
        if off >= 25:
            return 0.98
        if off >= -10:
            return 0.88
        if off >= -40:
            return 0.55
        return 0.28

    def _hold(it):
        b = MARKET_PARAMS[it]["base"]
        off = MARKET_I0 - inv.get(it, MARKET_I0)
        if it in ("MILK", "WOOL", "EGG", "STRAWBERRY", "TOMATO"):
            h = _flow_h(it, off)
            if it == "MILK" and plan.get("milk_contest") and 12 <= day < 26:
                h = min(h, 0.90)
            if it in ("MILK", "WOOL") and off < 0 and day >= 22:
                h = min(h, 0.55)
        elif it == "MELON":
            h = 0.50
        elif it == "WHEAT":
            if day <= 7:
                h = 1.05 if money >= 1200 else 0.88
            elif day <= 11:
                h = 0.94
            elif day < 20:
                h = 1.24
            elif day < 26:
                h = 1.05
            else:
                h = 0.60
        elif it == "CARROT":
            h = 0.78
        else:
            h = 0.37
        prem = it in PREMIUM_ITEMS
        if day >= 29:
            h = 0.02
        elif day >= 28:
            h = min(h, 0.55 if prem else 0.25)
        elif day >= 26:
            h = min(h, 0.75 if prem else 0.45)
        if shed_total >= 85:
            h = min(h, 0.70 if prem else 0.40)
        elif shed_total >= 70:
            h = min(h, 0.90 if prem else 0.72)
        if money < 250:
            h = min(h, 0.70 if prem else 0.55)
        if it in glutted:
            h = min(h, 0.85 if prem else 0.30)
        return h * b

    fert_need = 4
    wheat_window_fert = 0
    for row in tiles:
        for t in row:
            if isinstance(t, dict) and t.get("kind") == "PLANT":
                crop = t.get("crop")
                cd = CROPS.get(crop)
                if cd and t.get("fertilized_until_day", -1) < day:
                    if cd["ongoing"] and _prod_day(cd, t.get("planted_day", day), day):
                        fert_need += 1
                    elif not cd["ongoing"] and crop == "WHEAT" and wheat_window_fert < 12:
                        ws = (cd["max_yield_day"] + 1) // 2
                        age = day - t.get("planted_day", day)
                        if ws <= age <= cd["max_yield_day"]:
                            fert_need += 1
                            wheat_window_fert += 1

    cands = []
    if shed:
        for it in PRODUCTS:
            n = _num(shed.get(it))
            if it == "FERTILIZER":
                if day < 26:
                    sellable = n - fert_need - 2
                else:
                    sellable = n
                sellable = max(0, min(n, sellable))
                if sellable > 0 and day >= 2:
                    k = _sell_count("FERTILIZER", sellable, inv.get("FERTILIZER", MARKET_I0),
                                    FERT_FLOOR if day < 26 else 3)
                    if k > 0:
                        cands.append((k * (FERT_FLOOR + 30), ["SELL", "FERTILIZER", k]))
                continue
            if it == "WHEAT":
                if buying_wheat or day <= 1:
                    continue
                n = max(0, n - wheat_reserve)
            if it in ("GOOSE", "COW", "SHEEP"):
                continue
            if n <= 0:
                continue
            thresh = _hold(it)
            k = _sell_count(it, n, inv.get(it, MARKET_I0), thresh)
            if it in ("MILK", "WOOL", "STRAWBERRY") and day < 27:
                k = min(k, 18)
            if k > 0:
                cands.append((k * (prices.get(it, 0) or 0), ["SELL", it, k]))
    cands.sort(key=lambda c: -c[0])
    sell_orders = []
    for _, o in cands:
        if len(orders) + len(sell_orders) >= MAX_ORDERS:
            break
        sell_orders.append(o)

    # telemetry bookkeeping for submitted orders
    if tm is not None:
        ms = tm.setdefault("my_sells", {})
        mb = tm.setdefault("my_buys", {})
        for o in orders + sell_orders:
            try:
                if o[0] == "SELL":
                    ms[o[1]] = ms.get(o[1], 0) + int(o[2])
                elif o[0] == "BUY_PRODUCT":
                    mb[o[1]] = mb.get(o[1], 0) + int(o[2])
            except Exception:
                pass

    return (orders + sell_orders)[:MAX_ORDERS]


def _tm_step(tm, step, inv):
    try:
        if step % 24 == 0 and step > 0:
            snap = {p: inv.get(p, MARKET_I0) for p in PRODUCTS}
            prev_snap = tm.get("day_snap")
            if prev_snap is not None:
                net = {p: snap[p] - prev_snap.get(p, MARKET_I0) for p in PRODUCTS}
                tm.setdefault("net_hist", []).append(net)
                if len(tm["net_hist"]) > 5:
                    tm["net_hist"] = tm["net_hist"][-5:]
            tm["day_snap"] = snap
        prev = tm.get("prev_inv")
        if prev is not None and tm.get("prev_step") == step - 1:
            drain = _drain_at(step - 1, tm.get("shops") or [])
            ms = tm.get("my_sells") or {}
            mb = tm.get("my_buys") or {}
            opp_day = tm.setdefault("opp_day", {})
            for p in PRODUCTS:
                delta = inv.get(p, MARKET_I0) - prev.get(p, MARKET_I0)
                flow = delta + drain.get(p, 0.0) - ms.get(p, 0) + mb.get(p, 0)
                opp_day[p] = opp_day.get(p, 0.0) + flow
                if p not in ("WHEAT", "FERTILIZER", "EGG") and flow >= 8:
                    tm.setdefault("pause", {})[p] = step + 48
        tm["prev_inv"] = {p: inv.get(p, MARKET_I0) for p in PRODUCTS}
        tm["prev_step"] = step
        tm["my_sells"] = {}
        tm["my_buys"] = {}
    except Exception:
        pass


def step_now(tm):
    try:
        return tm.get("prev_step", 0)
    except Exception:
        return 0


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

    tm = _STATE.get(("tm",))
    if tm is None:
        tm = _STATE[("tm",)] = {}
    _tm_step(tm, step, inv)
    tm["shops"] = list(shops)

    pkey = ("plan", day)
    if pkey not in _STATE:
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
                           hour, plan, stats, tiles, shops, tm)

    actions = _assign_and_act(units, tasks, tiles, shed, inventories, day,
                              hour, board, seeds)

    return {"farmer": actions[0], "hands": actions[1:], "market": orders}


def agent(obs):
    try:
        return _agent(obs)
    except Exception:
        return {"farmer": ["PASS"], "hands": [], "market": []}
