# ================================================================== v19.2 PREGUARD layer
# Hour-21/22 shed-overflow preguard — mechanism ported from seyitkaangunes'
# public notebook "KaggressurE: V44 + Four Market Layers" (Layer 1, Apache-2.0),
# adapted to our V43 chassis (different item mix + destruction evidence).
#
# WHY (Task 87 battle-JSONL forensics, 3 battles x 2 players):
#   The V43 chassis has NO day-end storage guard (V44 added one as EXP-154).
#   At hour 23 the engine deposits every unit's carried items into the shed and
#   DESTROYS the overflow above 100. Measured on our own games:
#     - overflow on 8-10 of days 18-28, 2-28 units/day
#     - ~90-116 units destroyed per player-game, 96% WHEAT + some CARROT
#     - wheat prices $22-42 at those hours -> ~$3,000-7,000/game vaporized
#   (Both players burn it: the whole V43-lineage ladder leaks this money.)
#
# MECHANISM (identical to seyit L1, item list adapted):
#   At hours 21-22 of days >= 1 (before step 696 — endgame belongs to REAPER):
#   project the end-of-day shed+carried total with the V43 chassis's own
#   helpers (_r127_fields applies this step's unit verbs, _r97_market_stock
#   applies the queued market orders). If the projection exceeds 93 (margin -6,
#   seyit's tuning), SELL the excess from shed stock, price-descending, so the
#   carried feed wheat survives the deposit. Selling any shed item makes room;
#   price-desc banks the most value and front-runs the V44-family's hour-23
#   guard dumps (the ladder majority sells its excess at h23, highest price
#   first — our h21/22 quotes are pre-dump).
#
#   Item list: WHEAT (feed-neutral 1:1 — a sold shed unit is replaced by a
#   carried unit that would have been destroyed), EGG/MILK/STRAWBERRY/MELON/
#   WOOL/TOMATO (products; price >= 2 gate). EXCLUDED: CARROT (endgame ramp
#   $35->$280, 8x — never sell early), FERTILIZER (field input the tape needs),
#   animals/seeds. seyit's list skipped WHEAT/EGG because V44's shed mix
#   differs; ours is 69% WHEAT + 16% EGG at h21/22 (measured).
#
#   No consumption runs between the hour-20 market and hour-0 market, so a
#   passive market pays the same price at h21, h22 and h23 — the early sell
#   only wins races, it never loses the window.

_V192_HOST = _V191  # noqa: F821  (v19.1's entry point from the embedded namespace)

_PG_HOURS = (21, 22)
_PG_ITEMS = ("WHEAT", "EGG", "MILK", "STRAWBERRY", "MELON", "WOOL", "TOMATO")
_PG_MIN_DAY = 1
_PG_MAX_STEP = 696
_PG_MARGIN = -6
_PG_TELEMETRY = {"pg_turns": 0, "pg_units": 0, "pg_errors": 0}

# V43 chassis projection helpers, reached through the embedded chain
# v192 -> v191 -> v19 -> v18 -> V43(_PARENT_NS).
_V192_V43 = _V191_NS["_V19_NS"]["_V18_NS"]["_PARENT_NS"]  # noqa: F821
_r127_fields = _V192_V43["_r127_fields"]
_r97_market_stock = _V192_V43["_r97_market_stock"]
_PG_PRODUCTS = _V192_V43["PRODUCTS"]


def _v192_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("startingMoney", 3000),
        ))
    except Exception:
        return False


def _pg_preguard(obs, action):
    step = int(obs["step"])
    if step % 24 not in _PG_HOURS or step // 24 < _PG_MIN_DAY or step >= _PG_MAX_STEP:
        return action
    orders = [list(o) for o in (action.get("market") or [])]
    if len(orders) >= 10:
        return action
    res = _r127_fields(obs, action)
    farm, private = res[0], res[1]
    res2 = _r97_market_stock(private["shed"], orders)
    stock = res2[0]
    carried = sum(max(0, int(n)) for bag in private["inventories"] for n in bag.values())
    needed = sum(max(0, int(v)) for v in stock.values()) + carried - 99 - _PG_MARGIN
    if needed <= 0:
        return action
    prices = obs["market"]["prices"]
    extra = []
    for item in sorted(_PG_PRODUCTS, key=lambda it: -int(prices.get(it, 0) or 0)):
        avail = max(0, int(stock.get(item, 0) or 0))
        qty = min(needed, avail)
        if qty <= 0:
            continue
        if item in _PG_ITEMS and int(prices.get(item, 0) or 0) >= 2:
            extra.append(["SELL", item, qty])
        needed -= qty
        if needed <= 0:
            break
    if not extra or len(orders) + len(extra) > 10:
        return action
    _PG_TELEMETRY["pg_turns"] += 1
    _PG_TELEMETRY["pg_units"] += sum(o[2] for o in extra)
    return dict(action, market=orders + extra)


def agent(observation, configuration=None):
    action = _V192_HOST(observation, configuration)
    try:
        if isinstance(action, dict) and _v192_standard(configuration):
            new = _pg_preguard(observation, action)
            if new is not action:
                action = new
    except Exception:
        _PG_TELEMETRY["pg_errors"] += 1
    _PG_TELEMETRY.update(getattr(_V192_HOST, "telemetry", {}) or {})
    return action


agent.telemetry = _PG_TELEMETRY
