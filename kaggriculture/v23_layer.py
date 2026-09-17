# ================================================================= v23 GOOSE ENGINE
# EGG/GOOSE production planner — own architecture (Task 91, v23.7 SE-clean).
#
# WHY (measured, doc 10 + v23 forensics, 2026-09-18):
#   The EGG market starves in the mirror (inv -14/day, $50 -> $83 by d29) and
#   neither v20 nor ahmedv46 supplies it.  GOOSE: $300, 1-2 eggs/day from day 4
#   after placement, 1 wheat/day feed; EGG glut curve is log-gentle; BUY_PRODUCT
#   cannot touch EGG (no opponent arb).  The v23.0-v23.6 forensics killed three
#   wrong designs and exposed the real constraints:
#     1. NE-zone coops STEAL tiles from the core's own strawberry/wheat
#        expansion (~$60-70/day/tile) AND vacate market share to v46
#        (measured: v46 +$25-33K when we claimed NE).
#     2. The fib farm-hand curve explodes at the tail (hand #13-15 = $233-610),
#        so goose labor must stay on 2-3 hands max.
#     3. The wallet is lean until ~d11 ($27-$760), then rich ($10K+).
#   THE FIX: the SE quadrant (25 tiles, $4,000) is NEVER used by the core (it
#   buys NE+SW only).  A goose zone there costs ZERO tile opportunity, and the
#   land buy itself GIFTS the core ~11 free tiles it happily farms.  Timing:
#   core unlocks SW ~d10-12 -> we buy SE d11-13 -> builders (pre-positioned on
#   the locked tiles) claim 14 coops within hours -> geese trickle from the
#   rich wallet -> yield from ~d17 -> sell into the starving late egg market.
#
# ARCHITECTURE (planner around the proven v20 core, fail-open):
#   - v20 flat chain = cash engine, untouched.
#   - This planner owns: the SE land buy, a 14-tile COOP zone, receipt-claimed
#     hands (tail HIRE orders -> last-appended hands are ours), a wheat feed
#     budget (morning bridge buy + mid-day rescue), and market tail slots.
#   - Owned hands run a stateless greedy ladder:
#     FEED (rescue first) > PLACE carried geese > PICKUP wheat/goose at shed
#     > CARE > HARVEST (yield>=2) > BUILD/DIG on zone targets > walk to duty.
#   - Safety: inactive d0 and 696+; hours 20+ yield to core DROP/PLACE; 3
#     errors/day latches off; any exception fails open to the pure core.

_V23_HOST = agent  # noqa: F821  (flat chain: v20's entry point)

import os as _v23_os

# ---- tunables -------------------------------------------------------------
_V23_ACTIVE_FROM = 24          # turn 24 = day 1 hour 0
_V23_ACTIVE_TO = 695           # day 28 hour 23 (REAPER/terminal owns 696+)
_V23_MODE = "goose"            # "goose" = full engine; "land" = SE buy only
_V23_GEESE_TARGET = 12
_V23_LAND_MONEY = 4200         # buy SE once NW/NE/SW are unlocked
_V23_LAND_PRE_MONEY = 3600     # pre-position builders when this rich already
_V23_BUY_MONEY = 800           # geese: buy 1-2 when money >= this
_V23_WHEAT_RESERVE = 2         # core bridge-buys its own feed; keep ours lean
_V23_BRIDGE_CAP = 16           # max BUY_PRODUCT WHEAT per day
_V23_HIRE_FIB_CAP = 400        # marginal fib cost ceiling for a goose hand
_V23_EGGS_SELL_TRIGGER = 15    # also sell mid-day above this shed stock

# SE coop zone (x, y): rows y=5 (x6-9), y=6 (x5-9), y=7 (x5-9).  (5,5) is a
# shed-access tile and stays clear.  Sorted nearest-to-shed first.
_V23_ZONE = (
    [(6, 5), (7, 5), (8, 5), (9, 5)]
    + [(5, 6), (6, 6), (7, 6), (8, 6), (9, 6)]
    + [(5, 7), (6, 7), (7, 7), (8, 7), (9, 7)]
)

_V23 = {"day": -1, "errs": 0, "claims": [], "pending_hires": 0,
        "prev_hands": 0, "bridge_today": 0}

_V23_TEL = {
    "v23_active": 0, "v23_hire_orders": 0, "v23_hands_claimed": 0,
    "v23_geese_bought": 0, "v23_placed": 0, "v23_eggs_sell_orders": 0,
    "v23_eggs_sold_units": 0, "v23_feeds": 0, "v23_cares": 0,
    "v23_harvests": 0, "v23_builds": 0, "v23_digs": 0,
    "v23_pump_pickups": 0, "v23_bridge_orders": 0, "v23_bridge_units": 0,
    "v23_yields_to_core": 0, "v23_land_orders": 0, "v23_pass": 0,
    "v23_errors": 0,
}


def _v23_i(x, d=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return d


def _v23_fib(n):
    a, b = 1, 1
    for _ in range(max(0, n)):
        a, b = b, a + b
    return a


def _v23_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v23_tile(farm, x, y):
    try:
        return farm["tiles"][y][x]
    except Exception:
        return "LOCKED"


def _v23_is_goose(t):
    return isinstance(t, dict) and t.get("animal") == "GOOSE"


def _v23_empty_coop(t):
    return isinstance(t, dict) and t.get("kind") == "COOP" and "animal" not in t


def _v23_shed_total(shed):
    try:
        return sum(int(v) for v in shed.values()
                   if isinstance(v, (int, float)))
    except Exception:
        return 100


def _v23_move(pos, tx, ty):
    x, y = int(pos[0]), int(pos[1])
    if x < tx:
        return ["EAST"]
    if x > tx:
        return ["WEST"]
    if y < ty:
        return ["SOUTH"]
    if y > ty:
        return ["NORTH"]
    return ["PASS"]


def _v23_dist(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


def _v23_nearest(pos, points):
    best, bd = None, 10 ** 9
    for (x, y) in points:
        d = _v23_dist(pos[0], pos[1], x, y)
        if d < bd:
            best, bd = (x, y), d
    return best


def _v23_dump(seat, day):
    if not _v23_os.environ.get("V23_TEL_PATH"):
        return
    try:
        import json as _j
        with open(_v23_os.environ["V23_TEL_PATH"], "a") as f:
            f.write(_j.dumps({"seat": seat, "day": day, **_V23_TEL}) + "\n")
    except Exception:
        pass


def _v23_dbg(step, hour, msg):
    if not _v23_os.environ.get("V23_DEBUG"):
        return
    try:
        with open(_v23_os.environ["V23_DEBUG"], "a") as f:
            f.write(f"{step} h{hour:02d} {msg}\n")
    except Exception:
        pass


def agent(observation, configuration=None):
    action = _V23_HOST(observation, configuration)
    try:
        step = _v23_i(observation.get("step"), -1)
        if step >= 715:
            _v23_dump(_v23_i(observation.get("player"), 0), step // 24)
        if not _v23_standard(configuration) or not isinstance(action, dict):
            return action
        if step < _V23_ACTIVE_FROM or step > _V23_ACTIVE_TO:
            _V23_TEL["v23_pass"] += 1
            return action
        action = _v23_plan(observation, action, step)
    except Exception:
        _V23_TEL["v23_errors"] += 1
        _V23["errs"] += 1
    return action


def _v23_plan(obs, core, step):
    day, hour = step // 24, step % 24

    # ---- day rollover -----------------------------------------------------
    if _V23.get("day") != day:
        _V23["day"] = day
        _V23["claims"] = []
        _V23["pending_hires"] = 0
        _V23["prev_hands"] = 0
        _V23["errs"] = 0
        _V23["bridge_today"] = 0
    if _V23["errs"] >= 3:
        return core                      # latched off for the rest of the day

    seat = _v23_i(obs.get("player"), 0)
    farms = obs.get("farms") or []
    if not (0 <= seat < len(farms)):
        return core
    farm = farms[seat] or {}
    private = obs.get("private") or {}
    shed = private.get("shed") or {}
    invs = private.get("inventories") or []
    hands = list(farm.get("hands") or [])
    money = float(farm.get("money") or 0)
    unlocked = farm.get("unlocked_quadrants") or []
    se = "SE" in unlocked

    _V23_TEL["v23_active"] += 1

    # ---- survey -----------------------------------------------------------
    geese, empty_coops, buildable = [], [], []
    for (zx, zy) in _V23_ZONE:
        t = _v23_tile(farm, zx, zy)
        if _v23_is_goose(t):
            geese.append((zx, zy))
        elif _v23_empty_coop(t):
            empty_coops.append((zx, zy))
        elif t is None or (isinstance(t, dict) and t.get("kind") == "WEED"):
            buildable.append((zx, zy))
    try:                                   # stray geese outside the zone
        for y in range(10):
            for x in range(10):
                if (x, y) in _V23_ZONE:
                    continue
                if _v23_is_goose(_v23_tile(farm, x, y)):
                    geese.append((x, y))
    except Exception:
        pass
    geese.sort(key=lambda xy: (-xy[1], xy[0]))     # sweep nearest-shed first

    shed_geese = _v23_i(shed.get("GOOSE"), 0)
    shed_wheat = _v23_i(shed.get("WHEAT"), 0)
    shed_eggs = _v23_i(shed.get("EGG"), 0)
    # capacity = real goose homes now or one BUILD away; target follows it
    capacity = len(empty_coops) + len(buildable)
    placed = len(geese)
    total_geese = placed + shed_geese
    target = min(_V23_GEESE_TARGET, placed + capacity) if (se or placed) else 0
    pumpable = shed_geese > 0 and len(empty_coops) > 0
    build_more = bool(buildable) and (total_geese < target
                                      or shed_geese > len(empty_coops))
    land_ready = len(unlocked) >= 3       # NW/NE/SW: our BUY_LAND opens SE
    pre_position = (not se and land_ready
                    and money >= _V23_LAND_PRE_MONEY)

    # ---- hand ownership: receipt-claimed hires ----------------------------
    n_hands = len(hands)
    pending = _V23["pending_hires"]
    if n_hands > _V23["prev_hands"] and pending > 0:
        grew = n_hands - _V23["prev_hands"]
        take = min(pending, grew)         # my tail hires land last
        for i in range(n_hands - take, n_hands):
            if i not in _V23["claims"]:
                _V23["claims"].append(i)
                _V23_TEL["v23_hands_claimed"] += 1
    _V23["prev_hands"] = n_hands
    _V23["pending_hires"] = 0
    owned = sorted(c for c in _V23["claims"] if c < n_hands)

    # ---- k_needed ----------------------------------------------------------
    k_need = 0
    if placed > 0 or pumpable or build_more:
        k_need = 1 + (placed >= 5) + (placed >= 9)
        if total_geese < target and day <= 24:
            k_need = max(k_need, 2)      # ramp: one sweeps, one buys/places
    if build_more and len(buildable) >= 6:
        k_need = 3                        # build burst: claim the zone same-day
    if pre_position:
        k_need = max(k_need, 2)           # builders wait ON the locked tiles
    if _V23_MODE == "land":
        k_need = 0                        # land-only variant: no goose labor
    k_need = min(k_need, 3)

    # ---- market orders (ours go at the TAIL; core keeps its fib positions) --
    my_orders = []
    if shed_eggs > 0 and (hour <= 2 or shed_eggs > _V23_EGGS_SELL_TRIGGER):
        my_orders.append(["SELL", "EGG", shed_eggs])
        _V23_TEL["v23_eggs_sell_orders"] += 1
        _V23_TEL["v23_eggs_sold_units"] += shed_eggs
    if land_ready and not se and money >= _V23_LAND_MONEY:
        my_orders.insert(0, ["BUY_LAND"])     # unlocks SE, $4000
        _V23_TEL["v23_land_orders"] += 1
    if _V23_MODE == "goose":
        if (se and total_geese < target and capacity > total_geese
                and money >= _V23_BUY_MONEY + 300 and 0 <= hour <= 10
                and _v23_shed_total(shed) <= 95):
            qty = 2 if money >= 1400 else 1
            my_orders.append(["BUY_ANIMAL", "GOOSE", qty])
            _V23_TEL["v23_geese_bought"] += qty
    feed_need = placed
    starving_any = any(
        _v23_tile(farm, g[0], g[1]).get("consecutive_unfed", 0) >= 1
        for g in geese)
    if (_V23_MODE == "goose" and feed_need > 0
            and (hour <= 1 or (starving_any and hour <= 20))
            and _V23["bridge_today"] < _V23_BRIDGE_CAP):
        need = min(feed_need + 4 - shed_wheat, _V23_BRIDGE_CAP)
        if need > 0:
            my_orders.append(["BUY_PRODUCT", "WHEAT", need])
            _V23["bridge_today"] += need
            _V23_TEL["v23_bridge_orders"] += 1
            _V23_TEL["v23_bridge_units"] += need

    # ---- hires: any hour (hires_today reflects the true fib position) -------
    want_hire = k_need - len(owned)
    if want_hire > 0 and 1 <= hour <= 22:
        already = sum(1 for o in my_orders if o[0] == "HIRE")
        base = _v23_i(farm.get("hires_today"), 0)     # core's hires today
        for j in range(min(want_hire, 2)):
            pos_n = base + already + j + 1
            if _v23_fib(pos_n) > _V23_HIRE_FIB_CAP:
                break
            my_orders.append(["HIRE"])
            _V23_TEL["v23_hire_orders"] += 1
        _V23["pending_hires"] = sum(1 for o in my_orders if o[0] == "HIRE")

    core_market = list(core.get("market") or [])
    market = core_market + my_orders
    if len(market) > 10:
        market = market[:10]

    # ---- goose hand commands (greedy stateless ladder) ---------------------
    core_hands = list(core.get("hands") or [])
    hands_out = [list(h) for h in core_hands]
    cmds = _v23_hand_commands(farm, invs, hands, owned, geese, empty_coops,
                              buildable, shed, hour, pumpable, build_more,
                              shed_geese, se, pre_position)
    if _v23_os.environ.get("V23_DEBUG"):
        _v23_dbg(step, hour,
                 f"hands={n_hands} owned={owned} k={k_need} placed={placed} "
                 f"shedG={shed_geese} coops={len(empty_coops)} "
                 f"buildable={len(buildable)} tgt={target} pump={pumpable} "
                 f"bm={build_more} se={se} my_mkt={my_orders} "
                 f"cmds={ {i: c for i, c in list(cmds.items())[:3]} }")
    for idx, cmd in cmds.items():
        # yield to the core's shed-critical commands late in the day
        if hour >= 20 and idx < len(hands_out):
            c = hands_out[idx]
            if isinstance(c, list) and c and c[0] in ("DROP", "PLACE"):
                _V23_TEL["v23_yields_to_core"] += 1
                continue
        while len(hands_out) <= idx:
            hands_out.append(["PASS"])
        hands_out[idx] = cmd

    out = dict(core)
    out["market"] = market
    out["hands"] = hands_out
    return out


def _v23_hand_commands(farm, invs, hands, owned, geese, empty_coops,
                       buildable, shed, hour, pumpable, build_more,
                       shed_geese, se, pre_position):
    """Greedy next-action per owned hand.  Fully stateless."""
    cmds = {}
    if not owned:
        return cmds
    k = len(owned)
    for rank, idx in enumerate(owned):
        if idx >= len(hands):
            continue
        pos = hands[idx]
        if not (isinstance(pos, (list, tuple)) and len(pos) == 2):
            continue
        inv = invs[idx + 1] if idx + 1 < len(invs) else {}
        my_geese = [g for i, g in enumerate(geese) if i % k == rank]
        is_flex = (idx == owned[-1])
        cmd = _v23_one_hand(farm, inv, pos, my_geese, empty_coops,
                            buildable, shed, hour, pumpable, build_more,
                            shed_geese, is_flex, se, pre_position,
                            rank, k)
        if cmd:
            cmds[idx] = cmd
    return cmds


def _v23_one_hand(farm, inv, pos, my_geese, empty_coops, buildable, shed,
                  hour, pumpable, build_more, shed_geese, is_flex, se,
                  pre_position, rank, k):
    x, y = int(pos[0]), int(pos[1])
    inv_wheat = _v23_i(inv.get("WHEAT"), 0) if hasattr(inv, "get") else 0
    inv_goose = _v23_i(inv.get("GOOSE"), 0) if hasattr(inv, "get") else 0
    tile = _v23_tile(farm, x, y)
    shed_wheat = _v23_i(shed.get("WHEAT"), 0)

    def goose_state(g):
        return _v23_tile(farm, g[0], g[1])

    unfed = [g for g in my_geese if not goose_state(g).get("fed_today")]
    starving = [g for g in my_geese
                if (goose_state(g).get("consecutive_unfed", 0) >= 1
                    and not goose_state(g).get("fed_today"))]

    # 1. standing on one of my geese
    if (x, y) in my_geese and _v23_is_goose(tile):
        if (not tile.get("fed_today")) and inv_wheat > 0:
            _V23_TEL["v23_feeds"] += 1
            return ["FEED"]
        if tile.get("fed_today") and not tile.get("cared_today"):
            _V23_TEL["v23_cares"] += 1
            return ["CARE"]
        if tile.get("yield_units", 0) >= 2:
            _V23_TEL["v23_harvests"] += 1
            return ["HARVEST"]
        rest = [g for g in my_geese if g != (x, y)]
        if rest:
            nxt = _v23_nearest(pos, rest)
            return _v23_move(pos, nxt[0], nxt[1])
        # duties done: FALL THROUGH to the pump/build ladder

    # 2. place a carried goose
    if inv_goose > 0 and _v23_empty_coop(tile):
        _V23_TEL["v23_placed"] += 1
        return ["PLACE", "GOOSE"]

    # 3. shed services (spawn tiles are shed-adjacent)
    if (x, y) in ((4, 4), (5, 4), (4, 5), (5, 5)):
        want_wheat = len(unfed) - inv_wheat
        if want_wheat > 0 and shed_wheat > _V23_WHEAT_RESERVE:
            take = min(want_wheat, shed_wheat - _V23_WHEAT_RESERVE)
            if take > 0:
                return ["PICKUP", "WHEAT", take]
        if (inv_goose == 0 and pumpable
                and not (unfed and inv_wheat > 0)):
            _V23_TEL["v23_pump_pickups"] += 1
            return ["PICKUP", "GOOSE", min(2, shed_geese)]

    # 4. build on zone targets
    if (x, y) in buildable and build_more:
        if tile is None:
            _V23_TEL["v23_builds"] += 1
            return ["BUILD_COOP"]
        if isinstance(tile, dict) and tile.get("kind") == "WEED":
            _V23_TEL["v23_digs"] += 1
            return ["DIG"]

    # 5. move toward the next duty
    if inv_goose > 0 and empty_coops:
        nxt = _v23_nearest(pos, empty_coops)
        return _v23_move(pos, nxt[0], nxt[1])
    if starving:
        nxt = _v23_nearest(pos, starving)
        return _v23_move(pos, nxt[0], nxt[1])
    if unfed and inv_wheat > 0:
        nxt = _v23_nearest(pos, unfed)
        return _v23_move(pos, nxt[0], nxt[1])
    if (is_flex and pumpable and inv_goose == 0
            and not (unfed and inv_wheat > 0)):
        return _v23_move(pos, 4, 4)       # only the flex hand pumps
    if unfed:
        nxt = _v23_nearest(pos, unfed)
        if _v23_dist(x, y, nxt[0], nxt[1]) + 1 <= 23 - hour:
            return _v23_move(pos, nxt[0], nxt[1])
    if my_geese:
        uncared = [g for g in my_geese
                   if goose_state(g).get("fed_today")
                   and not goose_state(g).get("cared_today")]
        if uncared:
            nxt = _v23_nearest(pos, uncared)
            return _v23_move(pos, nxt[0], nxt[1])
        ripe = [g for g in my_geese
                if goose_state(g).get("yield_units", 0) >= 2]
        if ripe:
            nxt = _v23_nearest(pos, ripe)
            return _v23_move(pos, nxt[0], nxt[1])
    if build_more and buildable:
        nxt = _v23_nearest(pos, buildable)
        return _v23_move(pos, nxt[0], nxt[1])
    if pre_position:
        # builders wait ON their own locked SE zone tile: the instant our
        # BUY_LAND unlocks SE (mid-day market phase), BUILD fires next hour
        wait = _V23_ZONE[(rank * len(_V23_ZONE)) // k]
        if wait != (x, y):
            return _v23_move(pos, wait[0], wait[1])
        return ["PASS"]
    return ["PASS"]


agent.telemetry = _V23_TEL
