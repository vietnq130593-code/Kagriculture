# ================================================================= v24 GARBAGE-THROTTLE layer (Task 92, H2 peak-pricing)
# Host: v20 flat chain (byte-exact) — this layer ONLY re-times SELL orders
# of already-produced output. No new inputs, no displacement, no vacating.
#
# MEASUREMENT BASIS (Task 92 probes, 6 seeds fill-exact + hoard forensic):
#   * Intraday timing is DEAD: hour-of-day inventory swing 5-20 units,
#     local dp/dinv ~ $0.02-0.08/u -> cents per unit. Both seats already
#     sell h13-h23.
#   * No hoards exist (shed ~empty; endgame volume = daily flow) -> the
#     naive "+16.8K/game front-run" first-order estimate is illusory.
#   * REAL remaining inefficiency: synchronized garbage windows — both
#     sides dump daily flow into near-floor prices ($1-9) while the drain
#     eventually catches up (STRA crash d21-24 then recovery $38-113 in
#     seeds 3/11/17; MILK $4-15 windows in 8/11/21, recovery to $29-41).
#     Value destroyed per crash seed: $1-11K, half of it capturable.
#   * Walk-down on release is STEEP for STRA (linear 1.6 above-curve:
#     42u dump = $50 -> $1) -> release in chunks, gate deep.
#
# DESIGN (lessons applied from H1/v21/v22/v23):
#   L-day    counters: release/stall counted once per DAY, never per turn.
#   L-evid   garbage-gate is the evidence (p < $10 = true garbage only,
#            NOT speculative banking at $50-100 — that flipped seeds in v22b).
#   L-flap   hysteresis strip<10 / release>=25 (2.5x gap) — re-entry after a
#            profitable cycle is safe (buy-$8-sell-$25), unlike v22c flaps.
#   L-shed   TOTAL hoard cap 24u + interlock (pass-through if sum(shed)>55)
#            — never block the wheat-feed bridge BUY (cows starve -> milk
#            machine dies) nor BUY_ANIMAL.
#   L-walk   release chunk <= 12u/day/item, one release per item per day.
#   L-reaper day >= 27 full pass-through (REAPER owns the endgame).
#   L-guard  hours >= 21 pass through (v19.2 h21/22 preguard = safety valve
#            for OUR hoard too: core will liquidate overflow itself).
#   L-fail   fail-open; 3 errors/day -> layer off for the day; telemetry.
#   L-tel    replay-telemetry test required after build (0 errors + strips>0).

_V24_HOST = agent  # noqa: F821  (flat chain: v20 = v19.4's entry point)

_V24_GATE_P = 15            # strip only true-garbage prices (sweep: 15 > 12; 20 eats recovering milk)
_V24_RELEASE_P = 18         # release back into recovered prices (sweep: 18 > 25)
_V24_HOURS = set(range(0, 21))   # h0-h20 only (h21+ = preguard/auto-drop)
_V24_MAX_ORDER = 200        # REAPER-sized orders (>200) always pass
_V24_HOARD_CAP = 24         # total units held across items (shed safety)
_V24_SHED_INTERLOCK = 55    # if sum(shed) already above this: no new strips
_V24_RELEASE_CHUNK = 12     # max units released per item per day
_V24_START_DAY = 3
_V24_END_DAY = 27           # REAPER owns d27+

_V24_STATE = {"held": {}, "released_day": {}, "err_day": -1, "errors_today": 0}
_V24_TELEMETRY = {"v24_stripped_orders": 0, "v24_held_now": 0,
                  "v24_release_events": 0, "v24_released_units": 0,
                  "v24_interlocks": 0, "v24_pass_turns": 0,
                  "v24_errors": 0, "v24_mode": "watch",
                  "v24_by_item": {}}


def _v24_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v24_int(x, default=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def agent(observation, configuration=None):
    action = _V24_HOST(observation, configuration)
    try:
        if not _v24_standard(configuration) or not isinstance(action, dict):
            return action
        step = _v24_int(observation.get("step"), -1)
        day = step // 24
        if day < _V24_START_DAY or day >= _V24_END_DAY:
            _V24_TELEMETRY["v24_pass_turns"] += 1
            return action
        hour = step % 24
        if hour not in _V24_HOURS:
            _V24_TELEMETRY["v24_pass_turns"] += 1
            return action

        # error budget: 3/day then off for the day (fail-open discipline)
        if _V24_STATE.get("err_day") != day:
            _V24_STATE["err_day"] = day
            _V24_STATE["errors_today"] = 0
        if _V24_STATE["errors_today"] >= 3:
            _V24_TELEMETRY["v24_pass_turns"] += 1
            return action

        market_orders = action.get("market")
        if not isinstance(market_orders, list) or not market_orders:
            _V24_TELEMETRY["v24_pass_turns"] += 1
            return action

        prices = ((observation.get("market") or {}).get("prices")) or {}
        shed = ((observation.get("private") or {}).get("shed")) or {}
        shed_total = 0
        try:
            shed_total = sum(_v24_int(v) for v in shed.values())
        except Exception:
            shed_total = 0

        held = _V24_STATE["held"]
        held_total = sum(held.values())

        # --- 1) strip garbage-price SELL orders (hoard-bound, capped) ---
        strip_ok = (shed_total + held_total) <= _V24_SHED_INTERLOCK
        out = []
        stripped = False
        for o in market_orders:
            if (strip_ok and isinstance(o, (list, tuple)) and len(o) >= 3
                    and o[0] == "SELL" and isinstance(o[2], (int, float))
                    and 0 < _v24_int(o[2], 0) <= _V24_MAX_ORDER):
                item = o[1]
                p = _v24_int(prices.get(item), 10 ** 9)
                if p < _V24_GATE_P:
                    q = _v24_int(o[2], 0)
                    room = _V24_HOARD_CAP - held_total
                    if room > 0:
                        held[item] = held.get(item, 0) + q
                        held_total += q
                        stripped = True
                        _V24_TELEMETRY["v24_stripped_orders"] += 1
                        bi = _V24_TELEMETRY["v24_by_item"].setdefault(
                            item, {"stripped": 0, "released": 0})
                        bi["stripped"] += q
                        if held_total >= _V24_HOARD_CAP:
                            strip_ok = False
                        continue
            out.append(o)

        # --- 2) release held items into recovered prices (chunked, 1/item/day) ---
        released_any = False
        for item in list(held.keys()):
            # clamp phantom units: cannot hold more than physically in shed
            # (core over-asks: order qty can exceed shed count)
            phys = _v24_int(shed.get(item), 0)
            if 0 <= phys < held.get(item, 0):
                held[item] = phys
            if held.get(item, 0) <= 0:
                if held.get(item, 0) <= 0 and item in held and held[item] == 0:
                    del held[item]
                continue
            p = _v24_int(prices.get(item), 0)
            if p < _V24_RELEASE_P:
                continue
            if _V24_STATE["released_day"].get(item) == day:
                continue
            shed_units = _v24_int(shed.get(item), 0)
            if shed_units <= 0:
                continue
            _v24_k = max(4, min(_V24_RELEASE_CHUNK, p // 4))
            k = min(held[item], shed_units, _v24_k)
            if k <= 0:
                continue
            if len(out) >= 10:      # engine drops orders beyond 10/turn
                break
            out.append(["SELL", item, k])
            held[item] = held.get(item, 0) - k
            _V24_STATE["released_day"][item] = day
            released_any = True
            _V24_TELEMETRY["v24_release_events"] += 1
            _V24_TELEMETRY["v24_released_units"] += k
            bi = _V24_TELEMETRY["v24_by_item"].setdefault(
                item, {"stripped": 0, "released": 0})
            bi["released"] += k
            if held.get(item, 0) <= 0:
                del held[item]

        if stripped or released_any:
            action = dict(action)
            action["market"] = out
        _V24_TELEMETRY["v24_held_now"] = sum(held.values())
        _V24_TELEMETRY["v24_mode"] = "hold" if held_total > 0 else "watch"
    except Exception:
        _V24_TELEMETRY["v24_errors"] += 1
        _V24_STATE["errors_today"] = (_V24_STATE.get("errors_today", 0) or 0) + 1
    return action


agent.telemetry = _V24_TELEMETRY
