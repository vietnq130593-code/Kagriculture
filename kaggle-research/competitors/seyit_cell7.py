%%writefile build/layer2_lockstep.py

# ---- v44y: clone-mode race horizon override ----
_RACE_HORIZON_CLONE = 9

# ---- v44y: exact lockstep best-response SELL ordering against a detected clone ----
_V44Y_HOST = [v for v in list(globals().values()) if callable(v)][-1]
_V44Y_REORDER_GATE = True
_V44Y_REPORT = dict(v44y_reorder_turns=0, v44y_reorder_gain=0.0, v44y_errors=0)
import itertools as _v44y_it

def _v44y_price(item, inventory, params):
    return _r37_market_price(item, inventory, params)

def _v44y_params(obs):
    params = {k: dict(v) for k, v in _R37_MARKET_PARAMS.items()}
    for k, patch in (obs['market'].get('params') or {}).items():
        if k in params and isinstance(patch, dict): params[k].update(patch)
    return params

def _v44y_lockstep(orders_me, orders_opp, inv0, stock_me, stock_opp, params):
    """Replay the engine's per-slot / per-unit lockstep for SELL and BUY_PRODUCT orders (money-unbounded).
    Returns (revenue_me, revenue_opp)."""
    inv = dict(inv0); stock = [dict(stock_me), dict(stock_opp)]; rev = [0.0, 0.0]
    queues = [list(orders_me), list(orders_opp)]
    for i in range(max(len(queues[0]), len(queues[1]))):
        rem = [None, None]
        for p in (0, 1):
            if i < len(queues[p]):
                o = queues[p][i]
                if o and len(o) >= 3 and o[0] in ('SELL', 'BUY_PRODUCT') and o[1] in params:
                    try: n = int(o[2])
                    except Exception: n = 0
                    if n > 0: rem[p] = [o[0], o[1], n]
        guard = 0
        while True:
            guard += 1
            if guard > 5000: break
            quoted = [None, None]
            for p in (0, 1):
                r = rem[p]
                if r is None or r[2] <= 0: continue
                if r[0] == 'SELL':
                    quoted[p] = ('SELL', r[1], _v44y_price(r[1], inv[r[1]], params))
                elif r[1] in ('WHEAT', 'FERTILIZER'):
                    quoted[p] = ('BUY_PRODUCT', r[1], _v44y_price(r[1], inv[r[1]] - 1, params))
                else:
                    rem[p] = None
            if quoted[0] is None and quoted[1] is None: break
            committed = False
            for p in (0, 1):
                q = quoted[p]
                if q is None: continue
                op, item, price = q
                if op == 'SELL':
                    if stock[p].get(item, 0) <= 0:
                        rem[p] = None; continue
                    stock[p][item] -= 1; rev[p] += price
                    if price > 1: inv[item] += 1
                else:
                    stock[p][item] = stock[p].get(item, 0) + 1; rev[p] -= price; inv[item] -= 1
                rem[p][2] -= 1; committed = True
            if not committed: break
    return rev[0], rev[1]

def _v44y_reorder(obs, action):
    market = action.get('market') or []
    if len(market) < 2: return action
    orders = [list(o) if isinstance(o, (list, tuple)) else o for o in market]
    blocks = []; i = 0
    while i < len(orders):
        o = orders[i]
        if o and o[0] == 'SELL':
            j = i
            while j < len(orders) and orders[j] and orders[j][0] == 'SELL': j += 1
            if 2 <= j - i <= 6: blocks.append((i, j))
            i = j
        else: i += 1
    if not blocks: return action
    view = FarmView(obs)
    stock = projected_shed(action, view)
    stock = {k: max(0, int(v)) for k, v in stock.items()}
    params = _v44y_params(obs)
    inv0 = {k: int(v) for k, v in obs['market']['inventory'].items()}
    opp = [list(o) for o in orders]
    def margin(cand):
        a, b = _v44y_lockstep(cand, opp, inv0, stock, stock, params)
        return a - b
    base = margin(orders); best = base; best_orders = None
    for (i, j) in blocks:
        blk = orders[i:j]; n = j - i
        seen = set()
        for perm in _v44y_it.permutations(range(n)):
            key = tuple((blk[p][1], int(blk[p][2])) for p in perm)
            if key in seen: continue
            seen.add(key)
            cand = orders[:i] + [blk[p] for p in perm] + orders[j:]
            v = margin(cand)
            if v > best + 0.5: best = v; best_orders = cand
        if best_orders is not None:
            orders = best_orders; best_orders = None
    if best <= base + 0.5: return action
    _V44Y_REPORT['v44y_reorder_turns'] += 1; _V44Y_REPORT['v44y_reorder_gain'] += best - base
    out = dict(action); out['market'] = orders
    return out

def _v44y_clone_gate(obs):
    player = int(obs['player']); step = int(obs['step'])
    st = _RACE_STATE.get(player) or {}
    if st.get('horizon', 0) > 0: return True
    if step >= 696 and len(st.get('hist', [])) >= 4 and sum(st['hist']) >= 4:
        return _r37_similarity(obs) >= .95
    return False

def v44y_lockstep_agent(observation, configuration=None):
    action = _V44Y_HOST(observation, configuration)
    try:
        step = int(observation.get('step', 0))
        if step >= 216 and (not _V44Y_REORDER_GATE or _v44y_clone_gate(observation)):
            action = _v44y_reorder(observation, action)
    except Exception:
        _V44Y_REPORT['v44y_errors'] += 1
    return action
v44y_lockstep_agent.telemetry = _V44Y_REPORT
