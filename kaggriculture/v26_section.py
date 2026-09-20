# ================================================================== v26 layer
# v26 "HERD-ADAPTIVE ANSWER GENERAL" (Task 100, 19-09) — port nghiên cứu từ
# notebook thomastschinkel "The 2945 Farm v9/4" (public Kaggle, Apache-2.0
# lineage; ladder 2944.7; submission 56269928). 2945-farm đè v25.1 44-4
# (8.3%) qua 2 cơ chế mổ xẻ ở Task 99:
#   (A) HERD-ADAPTIVE (s110): mix động vật đọc shops — khi ICE_CREAM/
#       SMOOTHIE/PIZZA mở (cầu MILK 6/unit/tick mỗi shop) và YARN_STORE
#       không mở, WOOL rơi về $1: băng ghi tĩnh 9bò+5cừu+3ngỗng là dead
#       weight, đúng profile của 2945 = 12 bò. Port: mở rule nosheep/
#       nogeese cho V47 shopherd (SHEEP/GOOSE→COW khi không-yarn + có milk
#       shop; xem _Y_CFG), mở rộng day-window (8,11)→(6,11) vì shop unlock
#       cuối ngày 2/5/8/11 — băng ghi mua ngày 6-11 đã thấy 2-3 shop.
#   (B) SECOND-HALF EXECUTION (s122 + mọi seed): 2945 out-earn mỗi ngày
#       d20-29 nhờ RACE horizon 40 + RACEGATE (không đua vào book đứt giá =
#       price ≤ base) + ORDERPRI2 (sắp SELL theo mức lộ diện trước đợt dump
#       của đối thủ) + CAPHARV (thu trước khi tràn cap chuồng).
# Thiết kế race-conditional (mẫu đã chứng minh ở v25.1 Task 98): khi máy
# race (mirror step-1 / clone-lock / escalation) phát hiện đối thủ cùng
# chassis — toàn bộ lớp v26 TẮT, giữ nguyên hành vi v25.1 (48W-0L vs
# ahmedv48, 10-0 vs alperen1/v65). Chỉ bật khi KHÔNG race — đúng đối thủ
# ngoài dòng như 2945-farm.
_V26_BASE = {'WHEAT': 25, 'CARROT': 35, 'TOMATO': 60, 'STRAWBERRY': 120,
             'MELON': 250, 'EGG': 50, 'MILK': 160, 'WOOL': 200}
_V26_HZ = 40            # 2945 RACE: horizon 40 (40/12 > 44/12 > constant-48)
_V26_HZ_MAX = 48
_V26_HZ_HOLD = 72       # lệnh horizon-trigger sống 3 ngày rồi hết
_V26_RIVAL_MIN = 2      # >=2 unit đối thủ bán mới tính là race signal
_V26_OR2_CAP = 30       # ORDERPRI2 batch cap của 2945
_V26_CH_SHED = 90       # CAPHARV shed-safety (cap engine 100)
_V26_ANIMALS = {'GOOSE': ('EGG', 4, 4, 1), 'COW': ('MILK', 6, 8, 2),
                'SHEEP': ('WOOL', 6, 6, 3)}   # (product, cap, first, interval)
_V26_RACE_ITEMS = ('CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL')
_V26_RACE_SHOPS = {'BAKERY': ('EGG', 'WHEAT'), 'PIZZA_SHOP': ('MILK', 'TOMATO', 'WHEAT'),
                   'BRUNCH_SPOT': ('EGG', 'WHEAT', 'STRAWBERRY'), 'YARN_STORE': ('WOOL',),
                   'ICE_CREAM_SHOP': ('STRAWBERRY', 'MILK', 'WHEAT'), 'PET_CAFE': ('CARROT',),
                   'SMOOTHIE_SHOP': ('STRAWBERRY', 'MILK'),
                   'FARMERS_MARKET': ('WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY')}
_V26_STATE = {}
_V26_REPORT = dict(v26_rival_sales=0, v26_hz_fires=0, v26_hz_turns=0, v26_glut_skips=0,
                   v26_adv_turns=0, v26_or2_turns=0, v26_or2_moves=0, v26_ch_fires=0,
                   v26_ch_units=0, v26_ch_sells=0, v26_errors=0)


def _v26_town_draw(step, shops):
    """Bản sao _race_town (đã chứng minh trong _race_lost): town tiêu thụ
    mỗi 4 step (2 unit nếu shop 1-sản-phẩm, 1 unit/sp else) + town center
    1 unit/sp mỗi 24 step."""
    out = {}
    if step % 4 == 0:
        for shop in shops:
            items = _V26_RACE_SHOPS.get(shop, ())
            for item in items:
                out[item] = out.get(item, 0) + (2 if len(items) == 1 else 1)
    if step % 24 == 0:
        for item in _V26_RACE_ITEMS:
            out[item] = out.get(item, 0) + 1
    return out


def _v26_tile_sig(farm):
    """Chữ ký băng đối thủ (farm ĐỐI THỦ public trong observation): mỗi tile
    plant (crop, yield, planted_day) hoặc animal (loài, yield)."""
    out = {}
    try:
        tiles = farm['tiles']
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if isinstance(t, dict):
                    if t.get('kind') == 'PLANT':
                        out[(x, y)] = ('P', t.get('crop'), int(t.get('yield_units', 0) or 0),
                                       int(t.get('planted_day', -1)))
                    elif t.get('animal'):
                        out[(x, y)] = ('A', t.get('animal'), int(t.get('yield_units', 0) or 0))
    except Exception:
        pass
    return out


def _v26_stock_delta(prev_sig, sig):
    """Đơn vị đối thủ THU về kho trong 1 turn: plant biến mất/replant =
    harvest đủ y; ongoing (tomato/straw) yield giảm = thu từng phần; animal
    yield giảm = thu sản phẩm. (Cơ chế ORDERPRI2 của 2945.)"""
    out = {}
    prod_of = {'GOOSE': 'EGG', 'COW': 'MILK', 'SHEEP': 'WOOL'}
    for pos, p in prev_sig.items():
        now = sig.get(pos)
        if p[0] == 'P':
            crop, y = p[1], p[2]
            if now is None or now[0] != 'P' or now[1] != crop or now[3] != p[3]:
                if y > 0:
                    out[crop] = out.get(crop, 0) + y
            elif now[2] < y:
                out[crop] = out.get(crop, 0) + (y - now[2])
        elif p[0] == 'A':
            prod = prod_of.get(p[1])
            if prod is None:
                continue
            y = p[2]
            if now is None or now[0] != 'A' or now[1] != p[1]:
                if y > 0:
                    out[prod] = out.get(prod, 0) + y
            elif now[2] < y:
                out[prod] = out.get(prod, 0) + (y - now[2])
    return out


def _v26_new_state():
    return {'step': -1, 'prev': None, 'prev_action': None, 'tiles': None,
            'stock': {}, 'hz': {}, 'ch_credit': {}}


def _v26_track(obs, action):
    """Gọi 1 lần/turn ở wrapper ngoài cùng: (1) identity inv'−inv+town−own =
    rival sales; (2) delta chữ ký băng đối thủ → stock ước tính; (3) horizon
    trigger: đối thủ bán item mà ta còn giữ + tape ta định bán trễ hơn → bật
    hz[item]=40 (RACE-lead của 2945, mặc định 40). Ghi snapshot turn này."""
    seat = int(obs['player']); step = int(obs['step'])
    st = _V26_STATE.get(seat)
    if st is None or step <= st['step']:
        st = _V26_STATE[seat] = _v26_new_state()
        if step == 0:
            _V26_REPORT.update(v26_rival_sales=0, v26_hz_fires=0, v26_hz_turns=0,
                               v26_glut_skips=0, v26_adv_turns=0, v26_or2_turns=0,
                               v26_or2_moves=0, v26_ch_fires=0, v26_ch_units=0,
                               v26_ch_sells=0, v26_errors=0)
    if st['step'] == step:
        return st
    rival_farm = obs['farms'][1 - seat]
    sig = _v26_tile_sig(rival_farm)
    if st['prev'] is not None and step == st['prev']['step'] + 1:
        try:
            inv = obs['market']['inventory']
            pinv = st['prev']['inventory']
            town = _v26_town_draw(step - 1, st['prev']['shops'])
            prev_shed = st['prev'].get('shed') or {}
            own_sold = {}
            for o in (st['prev_action'] or {}).get('market', []):
                if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] in _V26_RACE_ITEMS:
                    own_sold[o[1]] = own_sold.get(o[1], 0) + max(0, int(o[2]))
            for it in own_sold:
                own_sold[it] = min(own_sold[it], int(prev_shed.get(it, 0)) + 64)
            # rival sales identity + stock update
            delta = _v26_stock_delta(st['tiles'] or {}, sig)
            for item in _V26_RACE_ITEMS:
                try:
                    rival = int(inv[item]) - int(pinv[item]) + town.get(item, 0) - own_sold.get(item, 0)
                except Exception:
                    rival = 0
                if rival > 0:
                    stock = st['stock'].get(item, 0) + delta.get(item, 0) - rival
                    st['stock'][item] = max(0, stock)
                    if rival >= _V26_RIVAL_MIN:
                        _V26_REPORT['v26_rival_sales'] += 1
                        # horizon trigger (chỉ khi KHÔNG race cùng-chassis)
                        if not _v251_racing(seat) and 144 <= step < 696:
                            held = int(obs['private']['shed'].get(item, 0))
                            if held > 0:
                                def planned(t):
                                    for o in _adv_future(seat, t):
                                        if o and len(o) >= 3 and o[0] == 'SELL' and o[1] == item:
                                            return True
                                    return False
                                soon = any(planned(t) for t in range(step + 1, min(719, step + 6)))
                                later = any(planned(t) for t in range(step + 6, min(719, step + _V26_HZ + 8)))
                                if (not soon) and later:
                                    st['hz'][item] = step + _V26_HZ_HOLD
                                    _V26_REPORT['v26_hz_fires'] += 1
                else:
                    st['stock'][item] = max(0, st['stock'].get(item, 0) + delta.get(item, 0))
        except Exception:
            _V26_REPORT['v26_errors'] += 1
    # hz hết hạn + clear khi ta đã hết stock
    try:
        for item in list(st['hz']):
            if st['hz'][item] < step or int(obs['private']['shed'].get(item, 0)) <= 0:
                del st['hz'][item]
    except Exception:
        pass
    st['step'] = step
    try:
        st['prev'] = dict(step=step, inventory=dict(obs['market']['inventory']),
                          shops=list(obs.get('town', {}).get('unlocked_shops', []) or []),
                          shed=dict(obs['private']['shed']))
    except Exception:
        st['prev'] = dict(step=step, inventory={}, shops=[], shed={})
    st['tiles'] = sig
    st['prev_action'] = action
    return st


# ---- (B1) glut-gate + horizon RACE cho lớp EXP293 front-load ----------------
# Rebind `_adv_apply` lần 2 (v251 đã rebind 1 lần): bản v26 = bản v25.1 TRUNG
# THỰC khi đang race (delegate _V26_PREV_ADV) + khi không race: per-item
# horizon (14 mặc định / 40 khi hz-trigger) + glut-gate (price ≤ base thì
# KHÔNG front-load — RACEGATE của 2945: milk $98-107 vs base 160 = book đứt,
# đua vào = tự đâm giá) + giữ 2 guard demand-preserving của v25.1 (BAKERY
# look-3, WOOL/YARN skip) trong bản mở-rộng.
_V26_PREV_ADV = _adv_apply


def _adv_apply(obs, action):
    try:
        step = int(obs['step']); player = int(obs['player'])
        if step % 24 == 23 or not _ADV_FROM <= step < _ADV_TO:
            return _V26_PREV_ADV(obs, action)
        if step == 144:
            _V251_REPORT.update(v251_bakery_turns=0, v251_wool_skips=0,
                                v251_guard_errors=0, v251_race_turns=0, v251_look3_turns=0)
        if _v251_racing(player):
            return _V26_PREV_ADV(obs, action)
        st = _V26_STATE.get(player) or {}
        hz = st.get('hz') or {}
        if hz:
            _V26_REPORT['v26_hz_turns'] += 1
        shops = list(obs.get('town', {}).get('unlocked_shops', []) or [])
        # guard BAKERY của v25.1 (không race): >=2 BAKERY mở → timing 3-turn
        adv_look = _ADV_LOOK
        if shops.count('BAKERY') >= 2:
            adv_look = 3
            _V251_REPORT['v251_bakery_turns'] += 1
            _V251_REPORT['v251_look3_turns'] += 1
        prices = obs['market']['prices']
        native = _IMPL.chassis.players[player]
        debts = native['sell_state'].setdefault('r36_debts', {})
        plan = []
        first = None
        for off in range(1, _V26_HZ_MAX + 1):
            t = step + off
            if t > 718:
                break
            for o in _adv_future(player, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == 'SELL' and o[1] in _ADV_ITEMS:
                    item = o[1]
                    # RACEGATE: glut (price ≤ base) thì khỏi kéo sớm — để tape
                    # bán đúng lịch, chờ town hút glut.
                    try:
                        if item in _V26_BASE and int(prices.get(item, 0)) <= _V26_BASE[item]:
                            _V26_REPORT['v26_glut_skips'] += 1
                            continue
                    except Exception:
                        pass
                    # demand-preserving guard WOOL (giữ nguyên v25.1)
                    if off >= 5 and item == 'WOOL' and 'YARN_STORE' in shops:
                        _V251_REPORT['v251_wool_skips'] += 1
                        continue
                    look_i = _V26_HZ if item in hz else adv_look
                    if off > look_i:
                        continue
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, item, q))
        protected = first[1] if _ADV_PROTECT and first is not None and first[0] == 'SELL' else None
        plan = [(t, item, q) for t, item, q in plan if item != protected]
        if not plan:
            return action
        market = [list(o) for o in (action.get('market') or [])]
        if any(len(o) > 1 and o[0] == 'BUY_PRODUCT' for o in market):
            return action
        stock = projected_shed(action, FarmView(obs))
        selling = {}
        for o in market:
            if len(o) >= 3 and o[0] == 'SELL':
                try:
                    selling[o[1]] = selling.get(o[1], 0) + max(0, int(o[2]))
                except Exception:
                    return action
        commands = [action.get('farmer') or ['PASS'], *(action.get('hands') or [])]
        picked = {c[1] for c in commands if len(c) > 1 and c[0] == 'PICKUP'}
        added = 0
        extra = []
        booked = []
        for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
            if item in picked or int(prices.get(item, 0)) < 2:
                continue
            avail = int(stock.get(item, 0)) - selling.get(item, 0)
            if avail < 1:
                continue
            hit = next((o for o in market if len(o) >= 3 and o[0] == 'SELL' and o[1] == item), None)
            if hit is None and len(market) + len(extra) >= 10:
                continue
            n = 0
            for t, it, q in plan:
                if it != item or avail <= 0:
                    continue
                take = min(q, avail)
                booked.append((t, item, take))
                n += take
                avail -= take
            if n < 1:
                continue
            if hit is not None:
                hit[2] = int(hit[2]) + n
            else:
                extra.append(['SELL', item, n])
            added += n
        if not added:
            return action
        _V26_REPORT['v26_adv_turns'] += 1
        return dict(action, market=extra + market)
    except Exception:
        _V26_REPORT['v26_errors'] += 1
        return _V26_PREV_ADV(obs, action)


# ---- (B2) ORDERPRI2: sắp SELL theo mức lộ diện trước đợt dump của đối thủ ----
def _v26_exposure(item, qty, stock, inv, params):
    """2945 _or2_exposure: tổng doanh thu MẤT trên qty unit của ta nếu batch
    đối thủ (min(30, stock ước tính)) bán trước ta: Σ price(inv+j) −
    price(inv+batch+j)."""
    try:
        batch = min(_V26_OR2_CAP, max(0, int(stock)))
        if batch <= 0 or qty <= 0:
            return 0
        total = 0
        for j in range(min(int(qty), 24)):
            total += (_r37_market_price(item, inv + j, params)
                      - _r37_market_price(item, inv + batch + j, params))
        return max(0, total)
    except Exception:
        return 0


def _v26_orderpri(obs, action, st):
    step = int(obs['step']); day = step // 24; hour = step % 24
    player = int(obs['player'])
    if step < 144 or step >= 648 or day >= 27 or hour >= 21:
        return action          # FIX-A endgame giữ discipline riêng của nó
    if _v251_racing(player):
        return action          # cùng-chassis: giữ nguyên thứ tự v25.1
    market = action.get('market')
    if not isinstance(market, list) or len(market) < 2:
        return action
    sells = []
    for i, o in enumerate(market):
        try:
            if (isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL'
                    and isinstance(o[2], (int, float)) and int(o[2]) > 0 and o[1] in _V26_BASE):
                sells.append(i)
        except Exception:
            continue
    if len(sells) < 2:
        return action
    bought = set()
    for o in market:
        try:
            if isinstance(o, list) and len(o) >= 3 and o[0] in ('BUY_PRODUCT', 'BUY_SEED', 'BUY_ANIMAL'):
                bought.add(o[1])
        except Exception:
            continue
    movable = [i for i in sells if market[i][1] not in bought]
    if len(movable) < 2:
        return action
    try:
        inv = obs['market']['inventory']
        params = obs['market'].get('params')
        prices = obs['market']['prices']
        stock = st.get('stock') or {}

        def key(i):
            o = market[i]
            e = _v26_exposure(o[1], o[2], stock.get(o[1], 0),
                              int(inv.get(o[1], 0)), params)
            return (-e, -int(prices.get(o[1], 0)) * int(o[2]), i)
        order = sorted(movable, key=key)
        rest = [i for i in range(len(market)) if i not in set(movable)]
        action = dict(action, market=[market[i] for i in order + rest])
        _V26_REPORT['v26_or2_turns'] += 1
        _V26_REPORT['v26_or2_moves'] += 1
    except Exception:
        _V26_REPORT['v26_errors'] += 1
    return action


# ---- (B3) CAPHARV: thu trước khi chuồng tràn cap đêm nay -------------------
def _v26_capharv(obs, action, st):
    step = int(obs['step'])
    if step < 24 or step >= 718:
        return action
    try:
        day = step // 24
        seat = int(obs['player'])
        farm = obs['farms'][seat]
        private = obs['private']
        shed = private['shed']
        invs = private.get('inventories', [])
        tiles = farm['tiles']
        workers = [action.get('farmer') or ['PASS'], *(action.get('hands') or [])]
        positions = [farm['farmer'], *farm['hands']]
        carried = sum(sum((inv or {}).values()) for inv in invs)
        shed_total = sum(int(v or 0) for v in shed.values())
        # tape còn HARVEST hôm nay (dòng farmer/hands)? — nếu có thì tile đó
        # sẽ được thu theo lịch, khỏi cướp trước (gate "no later HARVEST" 2945)
        end_day = min((day + 1) * 24, 719)
        later_harvest = False
        try:
            for t in range(step + 1, end_day):
                fut = _adv_future(seat, t)
                if not fut:
                    continue
                rows = [fut.get('farmer') or ['PASS'], *(fut.get('hands') or [])]
                if any(isinstance(r, list) and r and r[0] == 'HARVEST' for r in rows):
                    later_harvest = True
                    break
        except Exception:
            later_harvest = False
        prices = obs['market']['prices']
        changed = False
        for idx in range(min(len(workers), len(positions))):
            work = workers[idx]
            if not (isinstance(work, list) and work and work[0] in ('CARE', 'COLLECT_FERTILIZER')):
                continue
            try:
                x, y = positions[idx]
                tile = tiles[y][x]
            except Exception:
                continue
            if not (isinstance(tile, dict) and tile.get('animal')):
                continue
            an = tile['animal']
            if an not in _V26_ANIMALS:
                continue
            product, cap, first, interval = _V26_ANIMALS[an]
            placed = int(tile.get('placed_day', 0) or 0)
            since = (day + 1) - placed - first
            if since < 0 or since % interval != 0:
                continue                     # hôm nay không phải ngày sản xuất
            y_now = int(tile.get('yield_units', 0) or 0)
            bonus = int(tile.get('pending_care_bonus', 0) or 0) if tile.get('fed_today') else 0
            overflow = y_now + 1 + bonus - cap
            if overflow <= 0:
                continue
            if shed_total + carried + y_now >= _V26_CH_SHED:
                continue
            if later_harvest:
                continue
            if work[0] == 'CARE':
                if overflow <= 1:
                    continue                 # mất care-bonus không đáng
                credit = overflow - 1
            else:                             # COLLECT_FERTILIZER
                if overflow * int(prices.get(product, 0)) <= 100:
                    continue                 # phân bón đáng hơn (base 100)
                credit = overflow
            workers[idx] = ['HARVEST']
            st['ch_credit'][product] = st['ch_credit'].get(product, 0) + max(0, credit)
            _V26_REPORT['v26_ch_fires'] += 1
            _V26_REPORT['v26_ch_units'] += max(0, credit)
            changed = True
        if changed:
            action = dict(action, farmer=workers[0], hands=workers[1:])
        # bán credit khi sản phẩm đã vào kho (mẫu credit-sale của 2945)
        market = action.get('market')
        if isinstance(market, list):
            market = [list(o) if isinstance(o, list) else o for o in market]
            for prod, credit in list(st.get('ch_credit', {}).items()):
                if credit <= 0:
                    continue
                try:
                    if int(prices.get(prod, 0)) < 2:
                        continue
                    planned = sum(max(0, int(o[2])) for o in market
                                  if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] == prod)
                    avail = int(shed.get(prod, 0)) - planned
                    take = min(credit, avail)
                    if take <= 0:
                        continue
                    hit = next((o for o in market
                                if isinstance(o, list) and len(o) >= 3 and o[0] == 'SELL' and o[1] == prod), None)
                    if hit is not None:
                        hit[2] = int(hit[2]) + take
                    elif len(market) < 10:
                        market.insert(0, ['SELL', prod, take])
                    else:
                        continue
                    st['ch_credit'][prod] = credit - take
                    _V26_REPORT['v26_ch_sells'] += take
                except Exception:
                    continue
            action = dict(action, market=market)
    except Exception:
        _V26_REPORT['v26_errors'] += 1
    return action


# ---- merge telemetry cho runner + wrapper ngoài cùng ------------------------
def _arena_diag(obs):
    """Task 100: merge v25 + v25.1 + v26 telemetry cho runner."""
    try:
        return {'v25': dict(_V25_TELEMETRY), 'v251': dict(_V251_REPORT),
                'v26': dict(_V26_REPORT),
                'held': dict(_V25T_STATE.get('held') or {}),
                'released_day': dict(_V25T_STATE.get('released_day') or {})}
    except Exception:
        return {}


_V26_PARENT = agent
globals().pop('agent', None)


def agent(observation, configuration=None):
    action = _V26_PARENT(observation, configuration)
    try:
        st = _v26_track(observation, action)
        action = _v26_capharv(observation, action, st)
        action = _v26_orderpri(observation, action, st)
    except Exception:
        _V26_REPORT['v26_errors'] += 1
    return action


agent.telemetry = _V26_REPORT
assert callable(globals().get('agent'))
