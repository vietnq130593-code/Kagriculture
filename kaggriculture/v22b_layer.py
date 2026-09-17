# ================================================================= v22b MILK-BANKER layer (tuned)
# H1 variant #2 of the milk-recovery family (Task 90 continuation).
#
# DELTAS vs v22 (all from Task-90 forensics):
#   v22 measured: +$81 mean vs v20, CI [-32,+222] — noise. Forensics showed:
#   (a) emission floor $30 re-sold the bank at mediocre $32-47 (seed 8 wash);
#   (b) enter condition (inv falling >=10/2d) triggered LATE (after the crash);
#   (c) strip -> chassis re-emit churn shifted sells by hours (walk noise).
#   v22b fixes: floor $50, enter on shop count (2 milk shops = drain 13+/day)
#   BEFORE the deep crash, emission window h0-h5 only (sell-the-bump, doc 09
#   sec 4), chunk cap 8 (gentler walk), stall-exit 4 days, accel from d24.
#   Sim ceiling (milk_sim): reactive chunking on 2-shop seeds +$273-2,312.
#
# Mechanism (all signals observable in-game; no seed peeking):
#   ENTER bank: >=2 milk shops AND 8 <= day < 27 AND price < 100.
#   IN bank mode: strip chassis SELL MILK orders (size <= 200) every hour;
#   emit once per day in h0-h5 when price >= 50: p>=120 -> 8 | p>=80 -> 6 |
#   p>=50 -> 4 units (from d24 double). EXIT: price >= 140 (recovered),
#   stall (price < 50 for 4 days AND inv flat/rising), or day >= 27 (REAPER).
#   Fail-open on any exception.

_V22B_HOST = agent  # noqa: F821  (flat chain: v20 = v19.4's entry point)

_V22B_START_DAY = 8
_V22B_END_DAY = 27              # REAPER owns d27+ (sell 1000s pass through)
_V22B_ENTER_P = 100             # enter banking while price below this
_V22B_EXIT_P = 140              # fully recovered -> resume chassis tape
_V22B_FLOOR_P = 50              # emit only at/above this price
_V22B_STALL_DAYS = 4            # low-price stall -> resume chassis tape
_V22B_ACCEL_DAY = 24            # double emission in the endgame
_V22B_EMIT_HOURS = (0, 1, 2, 3, 4, 5)   # sell-the-bump window (h0 consumption)

_V22B_STATE = {"mode": "watch", "low_days": 0, "emit_day": -1,
               "inv_hist": {}, "enter_day": -1}
_V22B_TELEMETRY = {"v22b_banked_units": 0, "v22b_emitted_units": 0,
                   "v22b_stripped_orders": 0, "v22b_pass_turns": 0,
                   "v22b_mode_days": 0, "v22b_errors": 0, "v22b_mode": "watch"}

_V22B_MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


def _v22b_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v22b_int(x, default=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def _v22b_emit_k(p):
    """Walk-aware daily emission at price p (chunk cap 8)."""
    if p >= 120:
        k = 8
    elif p >= 80:
        k = 6
    elif p >= 50:
        k = 4
    else:
        return 0
    return k


def agent(observation, configuration=None):
    action = _V22B_HOST(observation, configuration)
    try:
        if not _v22b_standard(configuration) or not isinstance(action, dict):
            return action
        step = _v22b_int(observation.get("step"), -1)
        day = step // 24
        if day < _V22B_START_DAY or day >= _V22B_END_DAY:
            _V22B_TELEMETRY["v22b_pass_turns"] += 1
            return action
        hour = step % 24
        if hour >= 21:                # preguard h21/22 + auto-drop h23
            _V22B_TELEMETRY["v22b_pass_turns"] += 1
            return action

        market = observation.get("market") or {}
        inv = _v22b_int((market.get("inventory") or {}).get("MILK"), 10 ** 9)
        p = _v22b_int((market.get("prices") or {}).get("MILK"), 0)
        shops = 0
        try:
            for sh in (observation.get("town") or {}).get("unlocked_shops", []):
                if sh in _V22B_MILK_SHOPS:
                    shops += 1
        except Exception:
            shops = 0
        shed = ((observation.get("private") or {}).get("shed")) or {}
        bank = _v22b_int(shed.get("MILK"), 0)

        # --- daily bookkeeping (last-hour inv per day) ---
        _V22B_STATE["inv_hist"][day] = inv

        mode = _V22B_STATE["mode"]

        if mode == "watch":
            if shops >= 2 and day >= 8 and p < _V22B_ENTER_P:
                mode = "bank"
                _V22B_STATE["mode"] = "bank"
                _V22B_STATE["enter_day"] = day
                _V22B_STATE["low_days"] = 0
        else:
            # bank mode upkeep: recovered / stall detection
            if p >= _V22B_EXIT_P:
                mode = "watch"
                _V22B_STATE["mode"] = "watch"
            elif p < _V22B_FLOOR_P:
                _V22B_STATE["low_days"] += 1
                inv_prev2 = _v22b_int(_V22B_STATE["inv_hist"].get(day - 2),
                                      10 ** 9)
                if (_V22B_STATE["low_days"] >= _V22B_STALL_DAYS
                        and inv >= inv_prev2 - 4):
                    mode = "watch"      # recovery stalled: resume tape
                    _V22B_STATE["mode"] = "watch"
            else:
                _V22B_STATE["low_days"] = 0

        _V22B_TELEMETRY["v22b_mode"] = mode

        market_orders = action.get("market")
        if not isinstance(market_orders, list) or not market_orders:
            _V22B_TELEMETRY["v22b_pass_turns"] += 1
            return action

        if mode != "bank":
            _V22B_TELEMETRY["v22b_pass_turns"] += 1
            return action

        # --- strip chassis SELL MILK (normal size; REAPER >200 passes) ---
        out = []
        stripped = False
        for o in market_orders:
            if (isinstance(o, (list, tuple)) and len(o) >= 3
                    and o[0] == "SELL" and o[1] == "MILK"
                    and isinstance(o[2], (int, float))
                    and 0 < _v22b_int(o[2], 0) <= 200):
                stripped = True
                continue
            out.append(o)

        # --- emit our own sell once per day, in the h0-h5 bump window ---
        emitted = 0
        if (bank > 0 and p >= _V22B_FLOOR_P and hour in _V22B_EMIT_HOURS
                and _V22B_STATE["emit_day"] != day):
            k = _v22b_emit_k(p)
            if day >= _V22B_ACCEL_DAY:
                k *= 2
            k = max(1, min(k, bank, 60))
            out.append(["SELL", "MILK", k])
            emitted = k
            _V22B_STATE["emit_day"] = day

        if stripped or emitted:
            action = dict(action)
            action["market"] = out
            _V22B_TELEMETRY["v22b_stripped_orders"] += int(stripped)
            _V22B_TELEMETRY["v22b_emitted_units"] += emitted
        _V22B_TELEMETRY["v22b_banked_units"] = bank
        if _V22B_STATE.get("mode_day") != day:
            _V22B_STATE["mode_day"] = day
            _V22B_TELEMETRY["v22b_mode_days"] += 1
    except Exception:
        _V22B_TELEMETRY["v22b_errors"] += 1
    return action


agent.telemetry = _V22B_TELEMETRY
