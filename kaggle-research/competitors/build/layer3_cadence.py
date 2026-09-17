

# ---------------------------------------------------------------- v44y sell-cadence wrapper (v3: hold & release)
_CD_HOST = [v for v in list(globals().values()) if callable(v)][-1]
_V44Y_CFG = {'rule': 'floor', 'items': ['CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'MILK', 'WOOL'], 'window': [96, 717], 'phases': [0, 2, 3], 'min_lot': 1, 'cash_margin': 300, 'money_floor': 1000, 'shed_cap': 100, 'max_hold': 3, 'hard_hold': 3, 'final_step': 717, 'lookahead': 8}
_V44Y_STATE = {}
_V44Y_SHOPS = {"BAKERY": ["EGG", "WHEAT"], "PIZZA_SHOP": ["MILK", "TOMATO", "WHEAT"], "BRUNCH_SPOT": ["EGG", "WHEAT", "STRAWBERRY"], "YARN_STORE": ["WOOL"], "ICE_CREAM_SHOP": ["STRAWBERRY", "MILK", "WHEAT"], "PET_CAFE": ["CARROT"], "SMOOTHIE_SHOP": ["STRAWBERRY", "MILK"], "FARMERS_MARKET": ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY"]}
_V44Y_SEED_PRICE = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
_V44Y_ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}
_V44Y_LAND = (1000, 2000, 4000)
_CD_REPORT = {"deferred_units": 0, "deferred_lots": 0, "released_alone": 0, "released_merged": 0, "released_forced": 0,
                "absorbed_by_host": 0, "blocked_shed": 0, "blocked_cash": 0, "errors": 0}


def _v44y_fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def _v44y_relief_at(tick_step, shops):
    """Units the town removes per product right after the market of `tick_step` (a multiple of 4)."""
    out = {}
    for s in shops:
        prods = _V44Y_SHOPS.get(s, [])
        m = 2 if len(prods) == 1 else 1
        for p in prods:
            out[p] = out.get(p, 0) + m
    if tick_step % 24 == 0:
        for p in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL"):
            out[p] = out.get(p, 0) + 1
    return out


def _v44y_buy_cost(market, prices, hires_today, quadrants):
    cost = 0.0
    hires = 0
    q = quadrants
    for o in market:
        if not o:
            continue
        op = o[0]
        if op == "HIRE":
            cost += _v44y_fib(hires_today + hires)
            hires += 1
        elif op == "BUY_LAND":
            i = q - 1
            if 0 <= i < 3:
                cost += _V44Y_LAND[i]
                q += 1
        elif len(o) >= 3:
            n = max(0, int(o[2]))
            if op == "BUY_SEED":
                cost += _V44Y_SEED_PRICE.get(o[1], 0) * n
            elif op == "BUY_ANIMAL":
                cost += _V44Y_ANIMAL_COST.get(o[1], 0) * n
            elif op == "BUY_PRODUCT":
                cost += prices.get(o[1], 0) * n
    return cost


def _v44y_append_sell(market, item, qty):
    """Append a separate SELL after the host's orders (keeps the host's order indices paired with a clone's)."""
    if len(market) >= 10:
        for o in market:
            if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
                o[2] = int(o[2]) + qty
                return "merged"
        return None
    market.append(["SELL", item, qty])
    return "alone"


def _v44y_merge_sell(market, item, qty):
    for o in market:
        if o and o[0] == "SELL" and len(o) >= 3 and o[1] == item:
            o[2] = int(o[2]) + qty
            return "merged"
    return _v44y_append_sell(market, item, qty)


def _v44y_defer_amount(rule, lot, n):
    if n <= 0:
        return 0
    if rule == "half":
        return min(lot, (n + 1) // 2)
    if rule == "n":
        return min(lot, n)
    if rule == "floor":
        return min(lot, n // 2)
    if rule == "all":
        return lot
    return 0


def _v44y_stock_view(observation, action, shed):
    """(projected shed after this step's unit actions, units the shed may still receive next step)."""
    try:
        view = FarmView(observation)
        proj = projected_shed(action, view)
        carried = sum(max(0, int(n or 0)) for inv in view.invs for n in inv.values())
        produced = 0
        units = [action.get("farmer") or ["PASS"]] + list(action.get("hands") or [])
        for i in range(min(len(units), len(view.positions))):
            a = units[i]
            if not a:
                continue
            tile = _tile_at(view.tiles, view.positions[i])
            if a[0] == "HARVEST" and isinstance(tile, dict):
                produced += max(0, int(tile.get("yield_units", 0) or 0))
            elif a[0] == "COLLECT_FERTILIZER" and isinstance(tile, dict) and tile.get("fertilizer_available"):
                produced += 1
        return {k: max(0, int(v)) for k, v in proj.items()}, carried + produced
    except Exception:
        _CD_REPORT["errors"] += 1
        return dict(shed), 0


def _v44y_sell_cadence_agent(observation, configuration=None):
    action = _CD_HOST(observation, configuration)
    try:
        cfg = _V44Y_CFG
        step = int(observation.get("step", 0) or 0)
        player = int(observation.get("player", 0) or 0)
        st = _V44Y_STATE.get(player)
        if st is None or step <= st["step"]:
            st = _V44Y_STATE[player] = {"step": -1, "held": {}, "since": {}}
        st["step"] = step
        if configuration is not None and not all(configuration.get(k, v) == v for k, v in (("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100), ("maxMarketOrdersPerTurn", 10))):
            return action
        if not isinstance(action, dict):
            return action
        market = [list(o) for o in (action.get("market") or [])]
        farms = observation.get("farms") or []
        me = farms[player] if player < len(farms) else {}
        shed = {k: int(v or 0) for k, v in dict((observation.get("private") or {}).get("shed") or {}).items()}
        prices = dict((observation.get("market") or {}).get("prices") or {})
        shops = list((observation.get("town") or {}).get("unlocked_shops") or [])
        money = float(me.get("money", 0) or 0)
        proj, incoming = _v44y_stock_view(observation, action, shed)
        host_sell = {}
        for o in market:
            if o and o[0] == "SELL" and len(o) >= 3:
                host_sell[o[1]] = host_sell.get(o[1], 0) + max(0, int(o[2]))
        # 1. reconcile the ledger with what the host will leave in the shed after its own orders
        held = st["held"]
        for it in list(held.keys()):
            left = max(0, proj.get(it, 0) - host_sell.get(it, 0))
            if held[it] > left:
                _CD_REPORT["absorbed_by_host"] += held[it] - left
                held[it] = left
            if held[it] <= 0:
                held.pop(it, None)
                st["since"].pop(it, None)
        # stock after the host's orders (bounded by stock) and the room left for next step's drops
        avail = dict(proj)
        revenue = 0.0
        for o in market:
            if o and o[0] == "SELL" and len(o) >= 3:
                x = min(max(0, int(o[2])), avail.get(o[1], 0))
                avail[o[1]] = avail.get(o[1], 0) - x
                revenue += prices.get(o[1], 0) * x
        total_after = sum(avail.values())
        room = cfg["shed_cap"] - total_after - incoming
        # 2. release held lots
        for it in list(held.keys()):
            q = held[it]
            age = step - st["since"].get(it, step)
            forced = room < 0 or step >= cfg["final_step"]
            if host_sell.get(it, 0) <= 0:
                if step % 4 == 1 or age >= cfg["max_hold"] or forced:
                    how = _v44y_append_sell(market, it, q)
                    if how:
                        _CD_REPORT["released_alone" if how == "alone" else "released_merged"] += q
                        held.pop(it, None); st["since"].pop(it, None); room += q
            else:
                if age >= cfg["hard_hold"] or forced:
                    how = _v44y_merge_sell(market, it, q)
                    if how:
                        _CD_REPORT["released_forced"] += q
                        held.pop(it, None); st["since"].pop(it, None); room += q
        # 3. new deferrals from this step's lots
        lo, hi = cfg["window"]
        if lo <= step < hi and step % 24 != 23 and (step % 4) in cfg["phases"] and money >= cfg["money_floor"]:
            next_tick = step if step % 4 == 0 else step + (4 - step % 4)
            relief = _v44y_relief_at(next_tick, shops)
            planned_soon = set()
            la = int(cfg.get("lookahead", 0) or 0)
            if la > 0:
                try:
                    route = _IMPL.chassis.players[player]["route"]
                    tape = _IMPL.chassis.routes[route]
                    for t in range(step + 1, min(step + 1 + la, len(tape))):
                        for o in (tape[t].get("market") or []) if isinstance(tape[t], dict) else []:
                            if o and o[0] == "SELL" and len(o) >= 3 and int(o[2]) > 0:
                                planned_soon.add(o[1])
                except Exception:
                    _CD_REPORT["errors"] += 1
            cost = _v44y_buy_cost(market, prices, int(me.get("hires_today", 0) or 0), len(me.get("unlocked_quadrants") or []))
            slack = money + revenue - cost - cfg["cash_margin"]
            for o in market:
                if not (o and o[0] == "SELL" and len(o) >= 3):
                    continue
                it = o[1]
                q = int(o[2])
                if it not in cfg["items"] or q <= 0 or prices.get(it, 0) < 2 or it in planned_soon:
                    continue
                lot = min(q, proj.get(it, 0))
                if lot < cfg["min_lot"]:
                    continue
                d = min(lot, _v44y_defer_amount(cfg["rule"], lot, relief.get(it, 0)))
                if d <= 0:
                    continue
                if d > room:
                    _CD_REPORT["blocked_shed"] += 1
                    continue
                if prices.get(it, 0) * d > slack:
                    _CD_REPORT["blocked_cash"] += 1
                    continue
                slack -= prices.get(it, 0) * d
                room -= d
                o[2] = q - d
                held[it] = held.get(it, 0) + d
                st["since"].setdefault(it, step)
                _CD_REPORT["deferred_units"] += d
                _CD_REPORT["deferred_lots"] += 1
        action["market"] = market[:10]
        return action
    except Exception:
        _CD_REPORT["errors"] += 1
        return action


_v44y_sell_cadence_agent.telemetry = _CD_REPORT
