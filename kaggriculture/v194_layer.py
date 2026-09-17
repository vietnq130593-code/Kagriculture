# ================================================================= v19.4 LOCKSTEP layer
# Clone-gated best-response SELL ordering — mechanism ported from seyitkaangunes'
# public notebook "KaggressurE: V44 + Four Market Layers" (Layer 2, Apache-2.0),
# re-implemented over our chain with the V43 chassis's own projection helpers
# and v18's engine-exact price model.
#
# WHY: when two clones meet (the ladder majority is one V43/V44-family tape),
# farming is identical and the market decides the game. The engine resolves
# both lists slot-by-slot, unit-by-unit in lockstep; within a slot nobody is
# "first", but WHICH product occupies which slot is a free lever: if my glutted
# product sits where the clone still sells something else, I take the pre-dump
# prices and its copy lands on the inventory I raised. seyit measured this
# layer alone at 20-0, +1436 vs plain V44 (seeds 46001-46010, both seats).
#
# MECHANISM (identical to seyit L2):
#   Gate: from step 216, when the chassis's own race mode is active (the parent
#   sets its per-player horizon to 4) or, from step 696, occupied-tile
#   similarity >= 0.95 — i.e. an exact clone is assumed.
#   Action: every contiguous run of 2-6 SELL orders is permuted; each distinct
#   permutation is replayed through an exact 2-player lockstep simulation
#   against the clone's assumed list (our own unmodified list and projected
#   shed — an exact copy of us). The permutation maximizing (own revenue -
#   clone revenue) wins; the original order scores exactly 0 against itself,
#   so only a positive edge (> $0.5) ever changes the list. Quantities never
#   change; only order slots move.
#
#   The price model is v18's _price (verified byte-exact against the engine's
#   MARKET_PARAMS shapes); the shed projection is the V43 chassis's own
#   projected_shed(FarmView) used by its reservation system.

import itertools as _v194_it

_V194_HOST = _V193  # noqa: F821  (v19.3's entry point from the embedded namespace)

_V194_ENABLED = True
_V194_FROM_STEP = 216
_V194_SIM_GATE = 0.95
_V194_EDGE = 0.5
_V194_MAX_BLOCK = 6
_V194_TELEMETRY = {"lk_turns": 0, "lk_gain": 0.0, "lk_errors": 0}

# engine-exact price model + chassis helpers through the embedded chain
_V194_NS18 = _V193_NS["_V192_NS"]["_V191_NS"]["_V19_NS"]["_V18_NS"]  # noqa: F821
_V194_V43 = _V194_NS18["_PARENT_NS"]
_v194_price = _V194_NS18["_price"]
_v194_params0 = _V194_NS18["_MARKET_PARAMS"]
_v194_projected_shed = _V194_V43["projected_shed"]
_v194_FarmView = _V194_V43["FarmView"]
_v194_similarity = _V194_V43["_r37_similarity"]
_v194_horizons = _V194_V43["_R37_HORIZONS"]  # the v18 _Horizons wrapper instance


def _v194_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v194_params(obs):
    params = {k: dict(v) for k, v in _v194_params0.items()}
    try:
        for k, patch in (obs["market"].get("params") or {}).items():
            if k in params and isinstance(patch, dict):
                params[k].update(patch)
    except Exception:
        pass
    return params


def _v194_lockstep(orders_me, orders_opp, inv0, stock_me, stock_opp, params):
    """Replay the engine's per-slot / per-unit lockstep for SELL and BUY_PRODUCT
    orders (money-unbounded). Returns (revenue_me, revenue_opp)."""
    inv = dict(inv0)
    stock = [dict(stock_me), dict(stock_opp)]
    rev = [0.0, 0.0]
    queues = [list(orders_me), list(orders_opp)]
    for i in range(max(len(queues[0]), len(queues[1]))):
        rem = [None, None]
        for p in (0, 1):
            if i < len(queues[p]):
                o = queues[p][i]
                if o and len(o) >= 3 and o[0] in ("SELL", "BUY_PRODUCT") and o[1] in params:
                    try:
                        n = int(o[2])
                    except Exception:
                        n = 0
                    if n > 0:
                        rem[p] = [o[0], o[1], n]
        guard = 0
        while True:
            guard += 1
            if guard > 5000:
                break
            quoted = [None, None]
            for p in (0, 1):
                r = rem[p]
                if r is None or r[2] <= 0:
                    continue
                if r[0] == "SELL":
                    quoted[p] = ("SELL", r[1], _v194_price(r[1], inv[r[1]], params))
                elif r[1] in ("WHEAT", "FERTILIZER"):
                    quoted[p] = ("BUY_PRODUCT", r[1], _v194_price(r[1], inv[r[1]] - 1, params))
                else:
                    rem[p] = None
            if quoted[0] is None and quoted[1] is None:
                break
            committed = False
            for p in (0, 1):
                q = quoted[p]
                if q is None:
                    continue
                op, item, price = q
                if op == "SELL":
                    if stock[p].get(item, 0) <= 0:
                        rem[p] = None
                        continue
                    stock[p][item] -= 1
                    rev[p] += price
                    if price > 1:
                        inv[item] += 1
                else:
                    stock[p][item] = stock[p].get(item, 0) + 1
                    rev[p] -= price
                    inv[item] -= 1
                rem[p][2] -= 1
                committed = True
            if not committed:
                break
    return rev[0], rev[1]


def _v194_clone_gate(obs):
    player = int(obs["player"])
    step = int(obs["step"])
    try:
        if dict.get(_v194_horizons, player, 0) >= 4:
            return True
    except Exception:
        pass
    if step >= 696:
        try:
            return _v194_similarity(obs) >= _V194_SIM_GATE
        except Exception:
            return False
    return False


def _v194_reorder(obs, action):
    market = action.get("market") or []
    if len(market) < 2:
        return action
    orders = [list(o) if isinstance(o, (list, tuple)) else o for o in market]
    blocks = []
    i = 0
    while i < len(orders):
        o = orders[i]
        if o and o[0] == "SELL":
            j = i
            while j < len(orders) and orders[j] and orders[j][0] == "SELL":
                j += 1
            if 2 <= j - i <= _V194_MAX_BLOCK:
                blocks.append((i, j))
            i = j
        else:
            i += 1
    if not blocks:
        return action
    stock = _v194_projected_shed(action, _v194_FarmView(obs))
    stock = {k: max(0, int(v)) for k, v in stock.items()}
    params = _v194_params(obs)
    inv0 = {k: int(v) for k, v in obs["market"]["inventory"].items()}
    opp = [list(o) for o in orders]

    def margin(cand):
        a, b = _v194_lockstep(cand, opp, inv0, stock, stock, params)
        return a - b

    base = margin(orders)
    best = base
    best_orders = None
    for (i, j) in blocks:
        blk = orders[i:j]
        n = j - i
        seen = set()
        for perm in _v194_it.permutations(range(n)):
            key = tuple((blk[p][1], int(blk[p][2])) for p in perm)
            if key in seen:
                continue
            seen.add(key)
            cand = orders[:i] + [blk[p] for p in perm] + orders[j:]
            v = margin(cand)
            if v > best + _V194_EDGE:
                best = v
                best_orders = cand
        if best_orders is not None:
            orders = best_orders
            best_orders = None
    if best <= base + _V194_EDGE:
        return action
    _V194_TELEMETRY["lk_turns"] += 1
    _V194_TELEMETRY["lk_gain"] += best - base
    out = dict(action)
    out["market"] = orders
    return out


def agent(observation, configuration=None):
    action = _V194_HOST(observation, configuration)
    try:
        if (_V194_ENABLED and isinstance(action, dict)
                and _v194_standard(configuration)
                and int(observation["step"]) >= _V194_FROM_STEP
                and _v194_clone_gate(observation)):
            action = _v194_reorder(observation, action)
    except Exception:
        _V194_TELEMETRY["lk_errors"] += 1
    _V194_TELEMETRY.update(getattr(_V194_HOST, "telemetry", {}) or {})
    return action


agent.telemetry = _V194_TELEMETRY
