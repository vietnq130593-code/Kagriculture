# ================================================================= v22 MILK-BANKER layer
# Adaptive milk recovery banking over the v19.4 chain (host = flat v20 agent).
#
# WHY (measured, 8-seed probe 2026-09-18, v20 vs ahmedv46, full 720-turn games):
#   MILK is permanently glutted (linear price curve, -2.098$/unit above I0)
#   in 6/8 seeds because both tapes dump their full production daily into a
#   drain (1 milk shop = 7/day) that is smaller than combined supply.
#   BUT in 2-milk-shop seeds (2/8: seed 3 SMOOTHIE@d15+ICE@d18 -> drain 13/day;
#   seed 8 ICE@d9+PIZZA@d18) the endgame inventory falls and price recovers
#   to $131-145 (seed 3) / $34-40 (seed 8) while BOTH tapes keep dumping.
#   Withholding our garbage-price sells (<$30) accelerates the recovery
#   (our ~6 units/day withheld = +6/day extra drain) and the bank is sold
#   back into the recovery in walk-aware small chunks (4-12 units/day,
#   each unit only walks price -2.1) instead of one bulk dump that would
#   re-crash it (the v21-v1/v2 lesson: liquidation dumps self-crash).
#   v46's adaptive V231 cow expansion cannot respond inside the recovery
#   window: newly placed/bought cows need 8 days before first yield.
#
# MECHANISM (all signals observable in-game; no seed peeking):
#   Track market.inventory.MILK at each day's end + milk shop count.
#   ENTER bank mode: >=2 milk shops AND inv fell >=10 over the last 2 days
#   AND milk price < 60 AND 120 <= step < 648.
#   IN bank mode: strip the chassis's SELL MILK orders (normal-sized <=200;
#   REAPER-size passes) and emit our own once-per-day walk-aware sell:
#     p>=120 -> 12u | p>=85 -> 8u | p>=50 -> 6u | p>=30 -> 4u | else hold
#   From step 600 (d25) double k (game ends soon; don't let REAPER eat the
#   bank at mediocre prices). EXIT: p >= 160 (fully recovered) or recovery
#   stalls (p < 30 for 2 days with inv flat/rising) -> pass-through again.
#   step >= 648: REAPER owns (pass-through, bank rides the REAPER dump).
#   Fail-open on any exception.

_V22_HOST = agent  # noqa: F821  (flat chain: v19.4's entry point)

_V22_START_STEP = 120           # d5: inv tracking begins
_V22_ENDGAME_STEP = 648         # REAPER (v19 layer A1) owns 648+ untouched
_V22_ENTER_FALL_2D = 10         # inv must fall >= this over 2 days
_V22_EXIT_RECOVERED_P = 160
_V22_HOLD_P = 30                # below this: garbage sells get banked
_V22_ACCEL_STEP = 600           # d25: double the emit size

_V22_STATE = {"inv_hist": {}, "mode": "watch", "low_days": 0,
              "emit_day": -1, "mode_day": -1}
_V22_TELEMETRY = {"v22_banked_units": 0, "v22_emitted_units": 0,
                  "v22_stripped_orders": 0, "v22_pass_turns": 0,
                  "v22_mode_days": 0, "v22_errors": 0, "v22_mode": "watch"}

_V22_MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


def _v22_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v22_int(x, default=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def _v22_emit_k(p):
    """Walk-aware daily emission: how many bank units to sell at price p."""
    if p >= 120:
        k = 12
    elif p >= 85:
        k = 8
    elif p >= 50:
        k = 6
    elif p >= 30:
        k = 4
    else:
        return 0
    return k


def agent(observation, configuration=None):
    action = _V22_HOST(observation, configuration)
    try:
        if not _v22_standard(configuration) or not isinstance(action, dict):
            return action
        step = _v22_int(observation.get("step"), -1)
        if step < _V22_START_STEP or step >= _V22_ENDGAME_STEP:
            _V22_TELEMETRY["v22_pass_turns"] += 1
            return action
        hour = step % 24
        if hour >= 21:                # preguard h21/22 + auto-drop h23
            _V22_TELEMETRY["v22_pass_turns"] += 1
            return action
        day = step // 24

        market = observation.get("market") or {}
        inv = _v22_int((market.get("inventory") or {}).get("MILK"), 10 ** 9)
        p = _v22_int((market.get("prices") or {}).get("MILK"), 0)
        shops = 0
        try:
            for sh in (observation.get("town") or {}).get("unlocked_shops", []):
                if sh in _V22_MILK_SHOPS:
                    shops += 1
        except Exception:
            shops = 0
        shed = ((observation.get("private") or {}).get("shed")) or {}
        bank = _v22_int(shed.get("MILK"), 0)

        # --- daily bookkeeping (inv at the last hour we see this day) ---
        hist = _V22_STATE["inv_hist"]
        hist[day] = inv

        mode = _V22_STATE["mode"]

        if mode == "watch":
            fell = _v22_int(hist.get(day - 2), 10 ** 9) - inv
            if (shops >= 2 and day >= 12 and p < 60
                    and fell >= _V22_ENTER_FALL_2D):
                mode = "bank"
                _V22_STATE["mode"] = "bank"
                _V22_STATE["mode_day"] = day
                _V22_STATE["low_days"] = 0
        else:
            # bank mode upkeep: stall detection
            if p >= _V22_EXIT_RECOVERED_P:
                mode = "watch"
                _V22_STATE["mode"] = "watch"
            elif p < _V22_HOLD_P:
                _V22_STATE["low_days"] += 1
                inv_prev2 = _v22_int(hist.get(day - 2), 10 ** 9)
                if _V22_STATE["low_days"] >= 3 and inv >= inv_prev2 - 4:
                    mode = "watch"      # recovery stalled: resume tape
                    _V22_STATE["mode"] = "watch"
            else:
                _V22_STATE["low_days"] = 0

        _V22_TELEMETRY["v22_mode"] = mode

        market_orders = action.get("market")
        if not isinstance(market_orders, list) or not market_orders:
            _V22_TELEMETRY["v22_pass_turns"] += 1
            return action

        if mode != "bank":
            _V22_TELEMETRY["v22_pass_turns"] += 1
            return action

        # --- strip chassis SELL MILK (normal size; REAPER >200 passes) ---
        out = []
        stripped = False
        for o in market_orders:
            if (isinstance(o, (list, tuple)) and len(o) >= 3
                    and o[0] == "SELL" and o[1] == "MILK"
                    and isinstance(o[2], (int, float))
                    and 0 < _v22_int(o[2], 0) <= 200):
                stripped = True
                continue
            out.append(o)

        # --- emit our own walk-aware sell once per day ---
        emitted = 0
        if (bank > 0 and p >= _V22_HOLD_P
                and _V22_STATE["emit_day"] != day):
            k = _v22_emit_k(p)
            if step >= _V22_ACCEL_STEP:
                k *= 2
            k = max(1, min(k, bank, 60))
            out.append(["SELL", "MILK", k])
            emitted = k
            _V22_STATE["emit_day"] = day

        if stripped or emitted:
            action = dict(action)
            action["market"] = out
            _V22_TELEMETRY["v22_stripped_orders"] += int(stripped)
            _V22_TELEMETRY["v22_emitted_units"] += emitted
        _V22_TELEMETRY["v22_banked_units"] = bank
        if day != _V22_STATE.get("mode_day"):
            _V22_STATE["mode_day"] = day
            _V22_TELEMETRY["v22_mode_days"] += 1
    except Exception:
        _V22_TELEMETRY["v22_errors"] += 1
    return action


agent.telemetry = _V22_TELEMETRY
