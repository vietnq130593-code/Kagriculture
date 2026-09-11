import math
CROPS = {'WHEAT': {'seed': 10, 'first_yield_day': 2, 'max_yield_day': 4, 'interval': 0, 'max_yield': 6, 'ongoing': False}, 'CARROT': {'seed': 20, 'first_yield_day': 2, 'max_yield_day': 3, 'interval': 0, 'max_yield': 4, 'ongoing': False}, 'TOMATO': {'seed': 50, 'first_yield_day': 8, 'max_yield_day': 8, 'interval': 1, 'max_yield': 4, 'ongoing': True}, 'STRAWBERRY': {'seed': 100, 'first_yield_day': 10, 'max_yield_day': 10, 'interval': 2, 'max_yield': 4, 'ongoing': True}, 'MELON': {'seed': 80, 'first_yield_day': 10, 'max_yield_day': 12, 'interval': 0, 'max_yield': 6, 'ongoing': False}}
ANIMALS = {'GOOSE': {'cost': 300, 'structure': 'COOP', 'first_yield_day': 4, 'interval': 1, 'max_held': 4, 'product': 'EGG'}, 'COW': {'cost': 400, 'structure': 'PASTURE', 'first_yield_day': 8, 'interval': 2, 'max_held': 6, 'product': 'MILK'}, 'SHEEP': {'cost': 500, 'structure': 'PASTURE', 'first_yield_day': 6, 'interval': 3, 'max_held': 6, 'product': 'WOOL'}}
PRODUCTS = ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL', 'FERTILIZER']
MARKET_I0 = 10000
MARKET_PARAMS = {'WHEAT': {'base': 25, 'I0': MARKET_I0, 'T': 400, 'below_func': 'sqrt', 'below_target': 0.8, 'above_func': 'log', 'above_target': 0.2}, 'CARROT': {'base': 35, 'I0': MARKET_I0, 'T': 450, 'below_func': 'hinge', 'below_target': 1.0, 'above_func': 'sqrt', 'above_target': 0.7}, 'TOMATO': {'base': 60, 'I0': MARKET_I0, 'T': 200, 'below_func': 'hinge', 'below_target': 0.4, 'above_func': 'sqrt', 'above_target': 0.6}, 'STRAWBERRY': {'base': 120, 'I0': MARKET_I0, 'T': 100, 'below_func': 'sqrt', 'below_target': 0.7, 'above_func': 'linear', 'above_target': 1.6}, 'MELON': {'base': 250, 'I0': MARKET_I0, 'T': 300, 'below_func': 'log', 'below_target': 0.2, 'above_func': 'sq', 'above_target': 3.6}, 'EGG': {'base': 50, 'I0': MARKET_I0, 'T': 332, 'below_func': 'hinge', 'below_target': 0.4, 'above_func': 'log', 'above_target': 0.2}, 'MILK': {'base': 160, 'I0': MARKET_I0, 'T': 122, 'below_func': 'sqrt', 'below_target': 0.6, 'above_func': 'linear', 'above_target': 1.6}, 'WOOL': {'base': 200, 'I0': MARKET_I0, 'T': 105, 'below_func': 'log', 'below_target': 0.2, 'above_func': 'sq', 'above_target': 3.2}, 'FERTILIZER': {'base': 100, 'I0': MARKET_I0, 'T': 200, 'below_func': 'linear', 'below_target': 0.4, 'above_func': 'linear', 'above_target': 0.4}}
SHOPS = {'BAKERY': ['EGG', 'WHEAT'], 'PIZZA_SHOP': ['MILK', 'TOMATO', 'WHEAT'], 'BRUNCH_SPOT': ['EGG', 'WHEAT', 'STRAWBERRY'], 'YARN_STORE': ['WOOL'], 'ICE_CREAM_SHOP': ['STRAWBERRY', 'MILK', 'WHEAT'], 'PET_CAFE': ['CARROT'], 'SMOOTHIE_SHOP': ['STRAWBERRY', 'MILK'], 'FARMERS_MARKET': ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY']}
TOWN_CENTER_PRODUCTS = [p for p in PRODUCTS if p != 'FERTILIZER']
TURN_PER_DAY = 24
EPISODE_STEPS = 720
MAX_ORDERS = 10
SHED_CAP = 100
LAND_PRICES = [1000, 2000, 4000]
MAX_SHOP_INSTANCES = 8
CYCLE_LEN = {'WHEAT': 5, 'CARROT': 4, 'TOMATO': 12, 'STRAWBERRY': 17, 'MELON': 13}
YIELD_PER_CYCLE = {'WHEAT': 5, 'CARROT': 3, 'TOMATO': 4, 'STRAWBERRY': 4, 'MELON': 6}
T_WATER_CRIT = 0
T_SERVICE_URG = 0
T_HARVEST_URG = 2
T_DELIVER = 2
T_BUILD_URG = 2
T_SERVICE = 2
T_WATER_YIELD = 3
T_BUILD = 4
T_HARVEST_ANIMAL = 4
T_HARVEST = 5
T_PLANT = 5
T_DIG = 5
T_WATER_MAINT = 3
T_FERTILIZE = 7
FERT_SELL = True
FERT_FLOOR = 38
ANIMAL_CAP = 16
TOM_QUOTA = 6
HOLD = {'MILK': 0.98, 'WOOL': 0.94, 'STRAWBERRY': 0.9, 'EGG': 0.86, 'CARROT': 0.7, 'WHEAT': 0.76, 'MELON': 0.52, 'TOMATO': 0.82, 'FERTILIZER': 0.4}
_STATE = {}
def _g(o, k, d=None):
    try:
        if isinstance(o, dict):
            return o.get(k, d)
        return getattr(o, k, d)
    except Exception:
        return d
def _mk(tier, x, y, op, **kw):
    d = {'tier': tier, 'x': x, 'y': y, 'op': op}
    d.update(kw)
    return d
def _fib(n):
    a, b = (1, 1)
    for _ in range(n):
        a, b = (b, a + b)
    return a
def _step_toward(fx, fy, tx, ty):
    if fx < tx:
        return 'EAST'
    if fx > tx:
        return 'WEST'
    if fy < ty:
        return 'SOUTH'
    if fy > ty:
        return 'NORTH'
    return None
def _shed_tiles(board):
    h = board // 2
    return [(h - 1, h - 1), (h, h - 1), (h - 1, h), (h, h)]
def _nearest_shed_tile(x, y, board):
    return min(_shed_tiles(board), key=lambda t: abs(t[0] - x) + abs(t[1] - y))
def _is_num(v):
    return isinstance(v, (int, float)) and (not isinstance(v, bool))
def _shape(func, x, T=None):
    x = max(0.0, x)
    if func == 'linear':
        return x
    if func == 'sq':
        return x * x
    if func == 'sqrt':
        return math.sqrt(x)
    if func == 'log':
        return math.log(1.0 + x)
    if func == 'log10':
        return math.log10(1.0 + x)
    if func == 'hinge':
        if not T or T <= 0:
            return x
        u = x / T
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    return x
def _price(item, inventory):
    p = MARKET_PARAMS[item]
    base, I0, T = (p['base'], p['I0'], p['T'])
    if inventory < I0:
        f = p['below_func']
        amp = p['below_target'] * base / _shape(f, T, T)
        pr = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p['above_func']
        amp = p['above_target'] * base / _shape(f, T, T)
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
        thresh = frac * MARKET_PARAMS[item]['base']
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
            if t.get('kind') == 'PLANT':
                crop = t.get('crop')
                if crop in YIELD_PER_CYCLE:
                    pipe[crop] += YIELD_PER_CYCLE[crop]
            elif 'animal' in t:
                an = t.get('animal')
                if an in ANIMALS:
                    pipe[ANIMALS[an]['product']] += 28.0
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
def _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp_farm, money):
    absorb = _forward_absorb(day, 0, shops)
    my_pipe = _pipeline(tiles, shed)
    opp_tiles = _g(opp_farm, 'tiles', None) if opp_farm else None
    opp_pipe = _pipeline(opp_tiles, None)
    def room(it):
        deficit = max(0.0, MARKET_I0 - inv.get(it, MARKET_I0))
        r = deficit + absorb.get(it, 0) + _above_headroom(it, 0.78)
        return r - my_pipe.get(it, 0) - 0.85 * opp_pipe.get(it, 0)
    coops = pastures = wheat_standing = 0
    animals_now = 0
    standing = {c: 0 for c in CROPS}
    for row in tiles:
        for t in row:
            if isinstance(t, dict):
                k = t.get('kind')
                if k == 'COOP':
                    coops += 1
                elif k == 'PASTURE':
                    pastures += 1
                if 'animal' in t:
                    animals_now += 1
                if k == 'PLANT':
                    cc = t.get('crop')
                    if cc in standing:
                        standing[cc] += 1
                    if cc == 'WHEAT':
                        wheat_standing += 1
    shed_geese = shed.get('GOOSE', 0) if shed and _is_num(shed.get('GOOSE', 0)) else 0
    shed_cows = shed.get('COW', 0) if shed and _is_num(shed.get('COW', 0)) else 0
    shed_sheep = shed.get('SHEEP', 0) if shed and _is_num(shed.get('SHEEP', 0)) else 0
    opp_counts = {'GOOSE': 0, 'COW': 0, 'SHEEP': 0}
    if opp_tiles:
        for row in opp_tiles:
            for t in row:
                if isinstance(t, dict) and 'animal' in t:
                    a = t.get('animal')
                    if a in opp_counts:
                        opp_counts[a] += 1
    milk_room = absorb.get('MILK', 0) - 30.0 * opp_counts['COW'] - 40.0
    wool_room = absorb.get('WOOL', 0) - 28.0 * opp_counts['SHEEP'] - 20.0
    egg_room = absorb.get('EGG', 0) - 46.0 * opp_counts['GOOSE'] - 20.0
    goose_target = max(4 if day <= 9 else 3, min(5, int(egg_room // 46)))
    cow_target = max(0, min(7, int(milk_room // 30)))
    sheep_target = max(5, min(6, int(wool_room // 30)))
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
        cow_target = min(cow_target, sum((1 for row in tiles for t in row if isinstance(t, dict) and t.get('animal') == 'COW')) + shed_cows)
        sheep_target = min(sheep_target, sum((1 for row in tiles for t in row if isinstance(t, dict) and t.get('animal') == 'SHEEP')) + shed_sheep)
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
            reserved.append((empties[ri][0], empties[ri][1], 'BUILD_COOP'))
            ri += 1
    for _ in range(past_need):
        if ri < len(empties):
            reserved.append((empties[ri][0], empties[ri][1], 'BUILD_PASTURE'))
            ri += 1
    plantable = empties[ri:]
    feed_demand = (animals_now + shed_geese + shed_cows + shed_sheep + goose_target + cow_target + sheep_target) * max(0, 29 - day)
    quotas = {}
    if 8 <= day <= 14:
        quotas['MELON'] = 14 if room('MELON') > -50 else 7
        if day <= 1:
            quotas['MELON'] = 8
    if 2 <= day <= 16:
        quotas['TOMATO'] = 0
    if 5 <= day <= 13:
        s_room = room('STRAWBERRY')
        want_straw = 30 if day >= 8 else 14
        quotas['STRAWBERRY'] = want_straw if s_room > 100 else max(0, min(want_straw, int(s_room // 4)))
    elif 14 <= day <= 15:
        quotas['STRAWBERRY'] = 6
    if day <= 24:
        if day <= 4:
            quotas['WHEAT'] = 17
        else:
            daily_q = int((animals_now + shed_geese + shed_cows + shed_sheep + goose_target + cow_target + sheep_target) * 1.25) + 3
            quotas['WHEAT'] = min(19, daily_q)
    if day <= 23:
        if day <= 2:
            quotas['CARROT'] = 12
        elif day <= 10:
            quotas['CARROT'] = 8 if room('CARROT') > 60 else 6
        else:
            quotas['CARROT'] = 4 if room('CARROT') > 60 else 0
    if day <= 1:
        quotas['WHEAT'] = 10
        quotas['CARROT'] = 8
        quotas['MELON'] = 8
        quotas.pop('STRAWBERRY', None)
    if day <= 2:
        order = ['WHEAT', 'MELON', 'TOMATO', 'CARROT', 'STRAWBERRY']
    elif feed_demand > 300:
        order = ['WHEAT', 'STRAWBERRY', 'TOMATO', 'MELON', 'CARROT']
    else:
        order = ['MELON', 'STRAWBERRY', 'TOMATO', 'WHEAT', 'CARROT']
    crop_tiles = {}
    remaining = len(plantable)
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
    if remaining > 0 and day <= 22:
        extra = min(remaining, 8)
        if feed_demand > 200:
            crop_tiles['WHEAT'] = crop_tiles.get('WHEAT', 0) + extra
        else:
            crop_tiles['CARROT'] = crop_tiles.get('CARROT', 0) + extra
        remaining -= extra
    if day <= 1 and plantable:
        fast = sum((v for c, v in crop_tiles.items() if c in ('WHEAT', 'CARROT')))
        if fast < 0.45 * len(plantable):
            need = int(0.45 * len(plantable)) - fast
            for c in list(crop_tiles):
                if c not in ('WHEAT', 'CARROT') and need > 0:
                    cut = min(crop_tiles[c], need)
                    crop_tiles[c] -= cut
                    need -= cut
                    if crop_tiles[c] == 0:
                        del crop_tiles[c]
            if need > 0:
                crop_tiles['WHEAT'] = crop_tiles.get('WHEAT', 0) + need
    return {'crop_tiles': crop_tiles, 'reserved': reserved, 'goose_target': goose_target, 'cow_target': cow_target, 'sheep_target': sheep_target, 'feed_demand': feed_demand, 'standing': standing}
def _build_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, n_units):
    tasks = []
    stats = {'water_crit': 0, 'total': 0}
    board = len(tiles)
    if not board:
        return (tasks, stats)
    fert_available = (shed.get('FERTILIZER', 0) if shed else 0) + sum((u.get('FERTILIZER', 0) or 0 for u in inventories if isinstance(u, dict)))
    wheat_available = (shed.get('WHEAT', 0) if shed else 0) + sum((u.get('WHEAT', 0) or 0 for u in inventories if isinstance(u, dict)))
    fert_usable = 0
    for row in tiles:
        for t in row:
            if not isinstance(t, dict) or t.get('kind') != 'PLANT':
                continue
            crop = t.get('crop')
            if crop not in ('WHEAT', 'CARROT'):
                continue
            cd = CROPS[crop]
            age = day - t.get('planted_day', day)
            ws = (cd['max_yield_day'] + 1) // 2
            if ws <= age <= cd['max_yield_day'] and t.get('fertilized_until_day', -1) < day:
                fert_usable += 1
    fert_usable = max(0, fert_usable - fert_available)
    fert_made = 0
    for y in range(board):
        row = tiles[y]
        for x in range(board):
            t = row[x]
            if t is None or t == 'LOCKED' or (not isinstance(t, dict)):
                continue
            kind = t.get('kind')
            if kind == 'PLANT':
                crop = t.get('crop')
                cd = CROPS.get(crop)
                if cd is None:
                    continue
                age = day - t.get('planted_day', day)
                yu = t.get('yield_units', 0) or 0
                mls = t.get('max_lifespan_step', -1)
                watered = bool(t.get('watered_today', False))
                if not watered:
                    cu = t.get('consecutive_unwatered', 0) or 0
                    ws = (cd['max_yield_day'] + 1) // 2
                    in_win = not cd['ongoing'] and ws <= age <= cd['max_yield_day']
                    if in_win:
                        tasks.append(_mk(T_WATER_YIELD, x, y, 'WATER'))
                        stats['water_yield'] = stats.get('water_yield', 0) + 1
                    else:
                        on_day = (x + y + day) % 2 == 0
                        if on_day:
                            tasks.append(_mk(T_WATER_MAINT, x, y, 'WATER'))
                        elif cu >= 1:
                            tasks.append(_mk(T_WATER_CRIT, x, y, 'WATER'))
                            stats['water_crit'] += 1
                if yu > 0 and age >= cd['first_yield_day']:
                    urgent = mls >= 0 and mls - step <= 4
                    if cd['ongoing']:
                        ready = yu >= 4 or (mls >= 0 and mls - step <= 6) or day >= 27
                    else:
                        ready = yu >= cd['max_yield'] or age >= cd['max_yield_day'] + 1 or (age >= cd['max_yield_day'] and watered)
                    if ready:
                        tasks.append(_mk(T_HARVEST_URG if urgent else T_HARVEST, x, y, 'HARVEST'))
            elif 'animal' in t:
                ad = ANIMALS.get(t.get('animal'))
                if ad is None:
                    continue
                starve = (t.get('consecutive_unfed', 0) or 0) >= 1
                need_feed = not t.get('fed_today', False) and wheat_available > 0
                need_care = not t.get('cared_today', False)
                need_fert = bool(t.get('fertilizer_available', False))
                if day <= 28 and (need_feed or need_care or need_fert):
                    tasks.append(_mk(T_SERVICE_URG if starve else T_SERVICE, x, y, 'SERVICE', want_wheat=need_feed, feed=need_feed))
                yu = t.get('yield_units', 0) or 0
                if yu >= ad['max_held'] - 1:
                    tasks.append(_mk(T_HARVEST_URG, x, y, 'HARVEST'))
                elif yu >= 3 or (yu > 0 and day >= 27):
                    tasks.append(_mk(T_HARVEST_ANIMAL, x, y, 'HARVEST'))
            elif kind == 'WEED':
                tasks.append(_mk(T_DIG, x, y, 'DIG'))
            elif kind in ('COOP', 'PASTURE'):
                pass
    if hour <= 20:
        built = 0
        for x, y, bop in plan.get('reserved', []):
            if built >= 2:
                break
            if 0 <= y < board and 0 <= x < board and (tiles[y][x] is None):
                animal_waiting = (shed.get('GOOSE', 0) or 0) + (shed.get('COW', 0) or 0) + (shed.get('SHEEP', 0) or 0) > 0
                tasks.append(_mk(T_BUILD_URG if animal_waiting else T_BUILD, x, y, bop))
                built += 1
    if shed:
        for animal in ('GOOSE', 'COW', 'SHEEP'):
            n_pending = shed.get(animal, 0) or 0
            if n_pending <= 0:
                continue
            struct_kind = ANIMALS[animal]['structure']
            placed = 0
            limit = min(n_pending, 3)
            for y in range(board):
                for x in range(board):
                    if placed >= limit:
                        break
                    t = tiles[y][x]
                    if isinstance(t, dict) and t.get('kind') == struct_kind and ('animal' not in t):
                        tasks.append(_mk(T_DELIVER, x, y, 'DELIVER', item=animal))
                        placed += 1
                if placed >= limit:
                    break
    planted = _STATE.get(('planted', day)) or {}
    budget = []
    for crop, cap in plan.get('crop_tiles', {}).items():
        remain = cap - planted.get(crop, 0)
        have = seeds.get(crop, 0) or 0 if seeds else 0
        if remain > 0 and have > 0:
            budget.append((crop, min(remain, have)))
    reserved_xy = {(x, y) for x, y, _ in plan.get('reserved', [])}
    if budget and hour <= 19:
        empties = []
        for y in range(board):
            for x in range(board):
                if tiles[y][x] is None and (x, y) not in reserved_xy:
                    empties.append((x, y))
        empties.sort(key=lambda c: abs(c[0] - board // 2) + abs(c[1] - board // 2))
        flat = []
        wfirst = (plan.get('feed_demand', 0) or 0) > 0
        for crop, n in budget:
            if wfirst and crop == 'WHEAT':
                flat.extend(['WHEAT'] * n)
        for crop, n in budget:
            if wfirst and crop == 'WHEAT':
                continue
            flat.extend([crop] * n)
        turn_budget = n_units * max(1, 23 - hour)
        water_load = stats.get('water_crit', 0) + stats.get('water_yield', 0)
        safe_plant = int((turn_budget - water_load * 2.0) / 4)
        n_plant = min(len(flat), len(empties), max(0, safe_plant))
        for i in range(n_plant):
            x, y = empties[i]
            tasks.append(_mk(T_PLANT, x, y, 'PLANT', crop=flat[i]))
    if fert_available > 0 and day < 25:
        made = 0
        capf = min(int(fert_available), 6)
        for y in range(board):
            for x in range(board):
                if made >= capf:
                    break
                t = tiles[y][x]
                if not isinstance(t, dict) or t.get('kind') != 'PLANT':
                    continue
                crop = t.get('crop')
                if crop != 'MELON':
                    continue
                cd = CROPS[crop]
                age = day - t.get('planted_day', day)
                ws = (cd['max_yield_day'] + 1) // 2
                if ws <= age <= cd['max_yield_day'] and t.get('fertilized_until_day', -1) < day:
                    tasks.append(_mk(T_FERTILIZE, x, y, 'FERTILIZE'))
                    made += 1
    stats['total'] = len(tasks)
    return (tasks, stats)
def _drop_action(ux, uy, board):
    st = _nearest_shed_tile(ux, uy, board)
    if (ux, uy) == st:
        return ['DROP']
    mv = _step_toward(ux, uy, st[0], st[1])
    return [mv] if mv else ['PASS']
def _task_action(tk, ux, uy, uinv, tiles, shed, board):
    op = tk['op']
    tx, ty = (tk['x'], tk['y'])
    if op == 'SERVICE':
        t = tiles[ty][tx] if 0 <= tx < board and 0 <= ty < board else None
        an = t if isinstance(t, dict) and 'animal' in t else None
        if an is None:
            return ['PASS']
        w = uinv.get('WHEAT', 0) or 0
        if (ux, uy) == (tx, ty):
            if not an.get('fed_today', False) and w > 0:
                return ['FEED']
            if not an.get('cared_today', False):
                return ['CARE']
            if an.get('fertilizer_available', False):
                return ['COLLECT_FERTILIZER']
            return ['PASS']
        if not an.get('fed_today', False) and w <= 0 and tk.get('want_wheat') and ((shed.get('WHEAT', 0) or 0) > 0):
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, shed.get('WHEAT', 0) or 0 if shed else 0)
                if n > 0:
                    return ['PICKUP', 'WHEAT', n]
            else:
                mv = _step_toward(ux, uy, st[0], st[1])
                if mv:
                    return [mv]
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ['PASS']
    if op == 'FEED':
        w = uinv.get('WHEAT', 0) or 0
        if w <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(5, shed.get('WHEAT', 0) or 0 if shed else 0)
                if n > 0:
                    return ['PICKUP', 'WHEAT', n]
                return ['PASS']
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ['PASS']
        if (ux, uy) == (tx, ty):
            return ['FEED']
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ['PASS']
    if op == 'DELIVER':
        item = tk.get('item')
        if uinv.get(item, 0):
            if (ux, uy) == (tx, ty):
                return ['PLACE', item]
            mv = _step_toward(ux, uy, tx, ty)
            return [mv] if mv else ['PASS']
        st = _nearest_shed_tile(ux, uy, board)
        if (ux, uy) == st:
            if shed and (shed.get(item, 0) or 0) > 0:
                return ['PICKUP', item, 1]
            return ['PASS']
        mv = _step_toward(ux, uy, st[0], st[1])
        return [mv] if mv else ['PASS']
    if op == 'FERTILIZE':
        f = uinv.get('FERTILIZER', 0) or 0
        if f <= 0:
            st = _nearest_shed_tile(ux, uy, board)
            if (ux, uy) == st:
                n = min(6, shed.get('FERTILIZER', 0) or 0 if shed else 0)
                if n > 0:
                    return ['PICKUP', 'FERTILIZER', n]
                return ['PASS']
            mv = _step_toward(ux, uy, st[0], st[1])
            return [mv] if mv else ['PASS']
        if (ux, uy) == (tx, ty):
            return ['FERTILIZE']
        mv = _step_toward(ux, uy, tx, ty)
        return [mv] if mv else ['PASS']
    if (ux, uy) == (tx, ty):
        if op == 'PLANT':
            return ['PLANT', tk.get('crop')]
        return [op]
    mv = _step_toward(ux, uy, tx, ty)
    return [mv] if mv else ['PASS']
def _task_still_valid(tk, tiles, board, shed, uinv):
    x, y = (tk['x'], tk['y'])
    if not (0 <= x < board and 0 <= y < board):
        return False
    t = tiles[y][x]
    op = tk['op']
    if op == 'PLANT':
        return t is None
    if op == 'WATER':
        return isinstance(t, dict) and t.get('kind') == 'PLANT' and (not t.get('watered_today', False))
    if op == 'HARVEST':
        return isinstance(t, dict) and (t.get('yield_units', 0) or 0) > 0
    if op == 'SERVICE':
        if not (isinstance(t, dict) and 'animal' in t):
            return False
        if not t.get('fed_today', False):
            if (uinv.get('WHEAT', 0) or 0) > 0 or (shed.get('WHEAT', 0) or 0) > 0:
                return True
        return not t.get('cared_today', False) or bool(t.get('fertilizer_available', False))
    if op in ('FEED', 'CARE'):
        return isinstance(t, dict) and 'animal' in t and (not t.get('fed_today' if op == 'FEED' else 'cared_today', False))
    if op == 'DIG':
        return isinstance(t, dict) and t.get('kind') == 'WEED'
    if op in ('BUILD_COOP', 'BUILD_PASTURE'):
        return t is None
    if op == 'COLLECT_FERTILIZER':
        return isinstance(t, dict) and 'animal' in t and t.get('fertilizer_available', False)
    if op == 'FERTILIZE':
        return isinstance(t, dict) and t.get('kind') == 'PLANT' and (t.get('crop') == 'MELON') and (t.get('fertilized_until_day', -1) < day)
    if op == 'DELIVER':
        return (uinv.get(tk.get('item'), 0) or 0) > 0 or (shed.get(tk.get('item'), 0) or 0) > 0
    return True
def _assign_and_act(units, tasks, tiles, shed, inventories, day, hour, board, seeds):
    uinv_cache = {}
    for i in range(len(units)):
        u = inventories[i] if i < len(inventories) and isinstance(inventories[i], dict) else {}
        uinv_cache[i] = u
    sticky = _STATE.setdefault(('sticky', day), {})
    feed_pending = 0
    for tk2 in tasks:
        if tk2['op'] == 'SERVICE' and tk2.get('feed'):
            feed_pending += 1
    for i in list(sticky.keys()):
        if i >= len(units):
            del sticky[i]
            continue
        tk = sticky[i]
        if not _task_still_valid(tk, tiles, board, shed, uinv_cache[i]):
            del sticky[i]
            continue
        if feed_pending > 0 and tk['tier'] >= 2 and (tk['op'] not in ('SERVICE', 'FEED', 'DELIVER')) and ((uinv_cache[i].get('WHEAT', 0) or 0) > 0):
            del sticky[i]
    claimed = set()
    for i, tk in sticky.items():
        claimed.add((tk['op'], tk['x'], tk['y']))
    free = [i for i in range(len(units)) if i not in sticky]
    plant_sticky = {}
    for i, tk in sticky.items():
        if tk['op'] == 'PLANT':
            plant_sticky[tk.get('crop')] = plant_sticky.get(tk.get('crop'), 0) + 1
    def dist(i, tk):
        u = uinv_cache[i]
        if tk['op'] == 'DELIVER' and (u.get(tk.get('item'), 0) or 0) > 0:
            return 0
        if tk['op'] in ('FEED', 'SERVICE') and (u.get('WHEAT', 0) or 0) > 0:
            return 0
        d = abs(units[i][1] - tk['x']) + abs(units[i][2] - tk['y'])
        if (u.get('WHEAT', 0) or 0) > 0 and tk['tier'] >= 1 and (tk['op'] not in ('SERVICE', 'FEED')):
            d += 6
        return d
    def skey(tk):
        return (tk['tier'], min((dist(i, tk) for i in free), default=99))
    for tk in sorted(tasks, key=skey):
        if not free:
            break
        if (tk['op'], tk['x'], tk['y']) in claimed:
            continue
        if tk['op'] == 'PLANT':
            c = tk.get('crop')
            if plant_sticky.get(c, 0) + 1 > (seeds.get(c, 0) if seeds else 0):
                continue
            plant_sticky[c] = plant_sticky.get(c, 0) + 1
        best = min(free, key=lambda i: dist(i, tk))
        sticky[best] = tk
        claimed.add((tk['op'], tk['x'], tk['y']))
        free.remove(best)
    planted = _STATE.setdefault(('planted', day), {})
    actions = []
    for idx in range(len(units)):
        ux, uy = (units[idx][1], units[idx][2])
        uinv = uinv_cache[idx]
        carried = sum((v for v in uinv.values() if _is_num(v)))
        sellable = carried - (uinv.get('WHEAT', 0) or 0)
        act = ['PASS']
        tk = sticky.get(idx)
        need_drop = sellable >= 18 or (hour >= 20 and sellable >= 3) or (day >= 28 and hour >= 14 and (sellable >= 1))
        if need_drop:
            act = _drop_action(ux, uy, board)
        elif tk is not None:
            act = _task_action(tk, ux, uy, uinv, tiles, shed, board)
        if isinstance(act, list) and act and (act[0] == 'PLANT'):
            crop = act[1]
            planted[crop] = planted.get(crop, 0) + 1
        actions.append(act)
    return actions
def _wheat_all(shed, inventories):
    w = shed.get('WHEAT', 0) or 0 if shed else 0
    for u in inventories or []:
        if isinstance(u, dict):
            w += u.get('WHEAT', 0) or 0
    return w
def _build_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan, stats, tiles, shops):
    orders = []
    money = float(_g(me, 'money', 0) or 0)
    hands = _g(me, 'hands', None) or []
    unlocked = _g(me, 'unlocked_quadrants', None) or ['NW']
    board = len(tiles) if tiles else 10
    shed_total = sum((v for v in (shed or {}).values() if _is_num(v)))
    if hour <= 5 and day < 29:
        planted_today = _STATE.get(('planted', day)) or {}
        plant_budget = sum((max(0, n - planted_today.get(c, 0)) for c, n in plan.get('crop_tiles', {}).items()))
        workload = stats.get('total', 0) + plant_budget
        if day >= 6:
            target_units = min(13 if day >= 9 and money >= 1800 else 12, max(8, 6 + money // 500))
        elif day >= 1:
            target_units = 8
        else:
            target_units = 7
        target_units = max(target_units, min(11, 1 + int(math.ceil(workload * 2.6 / max(5, 23 - hour)))))
        want = target_units - (1 + len(hands))
        n_hired = _g(me, 'hires_today', 0) or 0
        cost = 0
        k = 0
        hire_floor = 60 if day <= 5 else 150
        hire_budget = min(money - hire_floor, max(88, money * 0.25))
        while k < want and k < 5:
            c = _fib(n_hired + k)
            if cost + c > hire_budget:
                break
            cost += c
            orders.append(['HIRE'])
            k += 1
    seed_spent = 0
    if hour <= 17 and seeds is not None:
        for crop in ('WHEAT', 'CARROT', 'STRAWBERRY', 'MELON', 'TOMATO'):
            n_tiles = plan.get('crop_tiles', {}).get(crop, 0)
            if not n_tiles:
                continue
            if crop == 'MELON' and day < 8 and (day > 2):
                continue
            if crop == 'STRAWBERRY' and day < 5:
                continue
            if crop == 'TOMATO' and (day < 2 or day > 16):
                continue
            have = seeds.get(crop, 0) or 0
            if have < n_tiles:
                need = n_tiles - have
                unit = CROPS[crop]['seed']
                floor = 80 if crop == 'WHEAT' else 150 if crop == 'STRAWBERRY' else 220
                if crop == 'STRAWBERRY':
                    floor = 900
                if crop == 'MELON':
                    floor = 700
                max_afford = max(0, int((money - floor) // unit)) if unit > 0 else 0
                buy = min(need, max_afford)
                if buy > 0:
                    orders.append(['BUY_SEED', crop, buy])
                    money -= buy * unit
                    seed_spent += buy * unit
            if len(orders) >= 9:
                break
    bought = _STATE.setdefault(('bought', day), {'GOOSE': 0, 'COW': 0, 'SHEEP': 0, 'LAND': 0})
    if hour <= 8 and 1 <= day <= 22:
        struct_free = {'COOP': 0, 'PASTURE': 0}
        for row in tiles:
            for t in row:
                if isinstance(t, dict):
                    k = t.get('kind')
                    if k in struct_free and 'animal' not in t:
                        struct_free[k] += 1
        animals_total = sum((1 for row in tiles for t in row if isinstance(t, dict) and 'animal' in t))
        wt = _wheat_all(shed, inventories)
        wheat_standing = sum((1 for row in tiles for t in row if isinstance(t, dict) and t.get('kind') == 'PLANT' and (t.get('crop') == 'WHEAT')))
        wt_supply = wt + 0.8 * wheat_standing
        for animal, target, w0, w1 in (('GOOSE', plan.get('goose_target', 0), 2, 14), ('SHEEP', plan.get('sheep_target', 0), 4, 15), ('COW', plan.get('cow_target', 0), 5, 16)):
            owned = sum((1 for row in tiles for t in row if isinstance(t, dict) and t.get('animal') == animal))
            owned += shed.get(animal, 0) or 0 if shed else 0
            ad = ANIMALS[animal]
            cash_floor = 250
            buy_per_day = 2 if day <= 12 else 1
            if owned < target and w0 <= day <= w1 and (bought.get(animal, 0) < buy_per_day) and (struct_free[ad['structure']] > 0) and (money >= ad['cost'] + cash_floor) and (shed_total < 92) and (wt_supply >= (animals_total + 1) * 1.3 or animals_total == 0):
                orders.append(['BUY_ANIMAL', animal, 1])
                bought[animal] = bought.get(animal, 0) + 1
                money -= ad['cost']
    nq = len(unlocked)
    if nq < 4 and bought.get('LAND', 0) < 1:
        owned_empty = sum((1 for row in tiles for t in row if t is None))
        price = LAND_PRICES[nq - 1]
        if nq == 3:
            last_day = 18
            gate = 1.2
            buffer = int(0.1 * price) + 500
        else:
            last_day = 20
            gate = 1.3
            buffer = int(0.15 * price) + 300
        if day <= last_day and (day <= 1 or owned_empty <= 14 or money >= price * gate) and (money >= price + buffer):
            orders.append(['BUY_LAND'])
            bought['LAND'] = 1
            money -= price
    animals = sum((1 for row in tiles for t in row if isinstance(t, dict) and 'animal' in t))
    plan_animals = plan.get('goose_target', 0) + plan.get('cow_target', 0) + plan.get('sheep_target', 0)
    if animals > 0 or plan_animals > 0:
        shed_wheat = shed.get('WHEAT', 0) or 0 if shed else 0
        wheat_want = int(animals * 1.5) + 4
        if shed_wheat < wheat_want and money >= 400:
            need = min(10, wheat_want - shed_wheat)
            pw = _price('WHEAT', inv.get('WHEAT', MARKET_I0) - 1)
            afford = int(money * 0.35 // pw) if pw > 0 else 0
            n = min(need, afford)
            acute = shed_wheat < 6
            if n >= 1 and (pw <= 38 or (acute and pw <= 62)):
                orders.append(['BUY_PRODUCT', 'WHEAT', n])
                money -= n * pw
    absorb_key = ('absorb', day)
    if absorb_key not in _STATE:
        _STATE[absorb_key] = _forward_absorb(day, 0, shops)
    absorb = _STATE[absorb_key]
    glutted = set()
    for it in PRODUCTS:
        if it in ('FERTILIZER', 'MELON'):
            continue
        over = inv.get(it, MARKET_I0) - MARKET_I0
        pr_now = prices.get(it, 0) or 0
        if over > absorb.get(it, 0) * 0.8 and pr_now < 0.75 * MARKET_PARAMS[it]['base']:
            glutted.add(it)
    wheat_reserve = min(animals * 2 + 6, shed.get('WHEAT', 0) or 0) if day < 26 and shed else 0
    def _hold(it):
        h = HOLD.get(it, 0.9)
        if it in glutted:
            return min(h, 0.4)
        if day >= 28:
            return 0.004
        if day >= 26:
            return min(h, 0.45)
        if day >= 22:
            return min(h, 0.7)
        if it == 'MELON' and day >= 24:
            return min(h, 0.3)
        if it == 'MELON' and day >= 21:
            return min(h, 0.42)
        if shed_total >= 80:
            return min(h, 0.72)
        if money < 250:
            return min(h, 0.65)
        return h
    cands = []
    if shed:
        for it in PRODUCTS:
            if it == 'FERTILIZER' and day < 26:
                nf = shed.get('FERTILIZER', 0) or 0
                if nf > 8 and day >= 2:
                    k = _sell_count('FERTILIZER', nf - 8, inv.get('FERTILIZER', MARKET_I0), FERT_FLOOR)
                    if k > 0:
                        cands.append((k * 60, ['SELL', 'FERTILIZER', k]))
                continue
            n = shed.get(it, 0) or 0
            if it == 'WHEAT':
                n = max(0, n - wheat_reserve)
            if n <= 0:
                continue
            thresh = _hold(it) * MARKET_PARAMS[it]['base']
            k = _sell_count(it, n, inv.get(it, MARKET_I0), thresh)
            if k > 0:
                cands.append((k * (prices.get(it, 0) or 0), ['SELL', it, k]))
    cands.sort(key=lambda c: -c[0])
    for _, o in cands:
        if len(orders) >= MAX_ORDERS:
            break
        orders.append(o)
    return orders[:MAX_ORDERS]
def _agent(obs):
    player = _g(obs, 'player', 0)
    farms = _g(obs, 'farms', None) or []
    if not farms or player is None or (not 0 <= player < len(farms)):
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    me = farms[player]
    day = _g(obs, 'day', 0) or 0
    hour = _g(obs, 'hour', 0) or 0
    step = day * TURN_PER_DAY + hour
    if day == 0 and hour == 0:
        _STATE.clear()
    tiles = _g(me, 'tiles', None) or []
    board = len(tiles)
    if board == 0:
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
    private = _g(obs, 'private', None) or {}
    market = _g(obs, 'market', None) or {}
    town = _g(obs, 'town', None) or {}
    shed = _g(private, 'shed', None) or {}
    seeds = _g(private, 'seeds', None) or {}
    inventories = _g(private, 'inventories', None) or []
    prices = _g(market, 'prices', None) or {}
    inv = _g(market, 'inventory', None) or {}
    shops = _g(town, 'unlocked_shops', None) or []
    opp = farms[1 - player] if len(farms) > 1 else None
    pkey = ('plan', day)
    if pkey not in _STATE:
        _STATE[pkey] = _daily_plan(tiles, shed, seeds, inv, prices, shops, day, opp, float(_g(me, 'money', 0) or 0))
    plan = _STATE[pkey]
    fpos = _g(me, 'farmer', None) or [board // 2 - 1, board // 2 - 1]
    units = [(0, int(fpos[0]), int(fpos[1]))]
    for i, h in enumerate(_g(me, 'hands', None) or []):
        units.append((i + 1, int(h[0]), int(h[1])))
    tasks, stats = _build_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, len(units))
    orders = _build_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan, stats, tiles, shops)
    actions = _assign_and_act(units, tasks, tiles, shed, inventories, day, hour, board, seeds)
    return {'farmer': actions[0], 'hands': actions[1:], 'market': orders}
def agent(obs):
    try:
        return _agent(obs)
    except Exception:
        return {'farmer': ['PASS'], 'hands': [], 'market': []}
