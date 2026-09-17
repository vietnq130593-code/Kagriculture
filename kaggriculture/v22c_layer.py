# ================================================================= v22c MILK-BANKER layer (cap-bounded, evidence-boosted)
# H1 variant #3 of the milk-recovery family (Task 90 continuation).
#
# DESIGN HISTORY (all measured, Task 90):
#   v22  (reactive, floor 30):    +$81 vs v20, CI [-32,+222] — noise.
#   v22b (floor 50, early enter): +$217, CI [53,402] — real, but flipped
#        seed 21 (2 shops, flat inv, no recovery) into 2 LOSSES (-24 each):
#        banked ~35 units into REAPER garbage while v46 free-rode +$195.
#   v22c-guard (money-lead guard): blocked banking exactly in the recovery
#        window on seed 3 (lead < 900 at d18 latches guard ON) — kills the
#        upside. Guard REJECTED.
#   v22c (this): bound the RISK instead of the LEAD:
#     * BANK CAP 20 units while speculative (entered on shops>=2, p<100 —
#       no recovery evidence yet). Worst case ~= 20u x $10 = -$200.
#     * CAP 40 once recovery EVIDENCE seen (inv fell >= 8 over 2 days while
#       in bank mode) — go harder when the recovery is real.
#     * Over-cap milk: chassis sells pass through (strip only below cap-8).
#     * Keeps v22b wins: floor $50, chunk cap 8, h0-h5 emission window,
#       stall-exit 4d, REAPER pass-through d27+.
#
# Mechanism (all signals observable in-game; no seed peeking):
#   ENTER bank: >=2 milk shops AND 10 <= day < 27 AND p < 100.
#   IN bank mode: strip chassis SELL MILK (size <= 200) while bank < cap-8;
#   emit once per day in h0-h5 at p >= 50: p>=120 -> 8 | p>=80 -> 6 | p>=50
#   -> 4 units (from d24 double). EXIT: p >= 140 (recovered), stall (p < 50
#   for 4 days AND inv flat/rising), or day >= 27 (REAPER). Fail-open.

_V22C_HOST = agent  # noqa: F821  (flat chain: v20 = v19.4's entry point)

_V22C_START_DAY = 10
_V22C_END_DAY = 27              # REAPER owns d27+ (sell 1000s pass through)
_V22C_ENTER_P = 100             # only start banking below this price
_V22C_EXIT_P = 140              # fully recovered -> resume chassis tape
_V22C_FLOOR_P = 50              # emit only at/above this price
_V22C_STALL_DAYS = 4            # low-price stall -> resume chassis tape
_V22C_ACCEL_DAY = 24            # double emission in the endgame
_V22C_EMIT_HOURS = (0, 1, 2, 3, 4, 5)   # sell-the-bump window (h0 consumption)
_V22C_CAP_SPEC = 20             # speculative bank cap (risk bound ~$200)
_V22C_CAP_EVID = 40             # cap once recovery evidence confirmed
_V22C_CAP_HYST = 8              # over-cap release margin
_V22C_EVIDENCE_FALL = 8         # inv fall over 2 days = recovery evidence

_V22C_STATE = {"mode": "watch", "low_days": 0, "emit_day": -1,
               "inv_hist": {}, "evidence": False}
_V22C_TELEMETRY = {"v22c_banked_units": 0, "v22c_emitted_units": 0,
                   "v22c_stripped_orders": 0, "v22c_pass_turns": 0,
                   "v22c_mode_days": 0, "v22c_errors": 0, "v22c_mode": "watch",
                   "v22c_evidence": 0}

_V22C_MILK_SHOPS = ("PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP")


def _v22c_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v22c_int(x, default=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def _v22c_emit_k(p):
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
    action = _V22C_HOST(observation, configuration)
    try:
        if not _v22c_standard(configuration) or not isinstance(action, dict):
            return action
        step = _v22c_int(observation.get("step"), -1)
        day = step // 24
        if day < _V22C_START_DAY or day >= _V22C_END_DAY:
            _V22C_TELEMETRY["v22c_pass_turns"] += 1
            return action
        hour = step % 24
        if hour >= 21:                # preguard h21/22 + auto-drop h23
            _V22C_TELEMETRY["v22c_pass_turns"] += 1
            return action

        market = observation.get("market") or {}
        inv = _v22c_int((market.get("inventory") or {}).get("MILK"), 10 ** 9)
        p = _v22c_int((market.get("prices") or {}).get("MILK"), 0)
        shops = 0
        try:
            for sh in (observation.get("town") or {}).get("unlocked_shops", []):
                if sh in _V22C_MILK_SHOPS:
                    shops += 1
        except Exception:
            shops = 0
        shed = ((observation.get("private") or {}).get("shed")) or {}
        bank = _v22c_int(shed.get("MILK"), 0)

        # --- daily bookkeeping (last-hour inv per day) ---
        _V22C_STATE["inv_hist"][day] = inv

        mode = _V22C_STATE["mode"]

        if mode == "watch":
            if shops >= 2 and day >= _V22C_START_DAY and p < _V22C_ENTER_P:
                mode = "bank"
                _V22C_STATE["mode"] = "bank"
                _V22C_STATE["low_days"] = 0
        else:
            # bank mode upkeep: recovered / stall / evidence
            if p >= _V22C_EXIT_P:
                mode = "watch"
                _V22C_STATE["mode"] = "watch"
            else:
                fell = (_v22c_int(_V22C_STATE["inv_hist"].get(day - 2), 10 ** 9)
                        - inv)
                if (not _V22C_STATE["evidence"]
                        and fell >= _V22C_EVIDENCE_FALL):
                    _V22C_STATE["evidence"] = True
                    _V22C_TELEMETRY["v22c_evidence"] = 1
                if p < _V22C_FLOOR_P:
                    _V22C_STATE["low_days"] += 1
                    inv_prev2 = _v22c_int(_V22C_STATE["inv_hist"].get(day - 2),
                                          10 ** 9)
                    if (_V22C_STATE["low_days"] >= _V22C_STALL_DAYS
                            and inv >= inv_prev2 - 4):
                        mode = "watch"      # recovery stalled: resume tape
                        _V22C_STATE["mode"] = "watch"
                else:
                    _V22C_STATE["low_days"] = 0

        _V22C_TELEMETRY["v22c_mode"] = mode

        market_orders = action.get("market")
        if not isinstance(market_orders, list) or not market_orders:
            _V22C_TELEMETRY["v22c_pass_turns"] += 1
            return action

        if mode != "bank":
            _V22C_TELEMETRY["v22c_pass_turns"] += 1
            return action

        cap = (_V22C_CAP_EVID if _V22C_STATE["evidence"]
               else _V22C_CAP_SPEC)

        # --- strip chassis SELL MILK only while under the cap ---
        # (normal size; REAPER-size >200 always passes)
        strip_allowed = bank < (cap - _V22C_CAP_HYST)
        out = []
        stripped = False
        for o in market_orders:
            if (strip_allowed and isinstance(o, (list, tuple)) and len(o) >= 3
                    and o[0] == "SELL" and o[1] == "MILK"
                    and isinstance(o[2], (int, float))
                    and 0 < _v22c_int(o[2], 0) <= 200):
                stripped = True
                continue
            out.append(o)

        # --- emit our own sell once per day, in the h0-h5 bump window ---
        emitted = 0
        if (bank > 0 and p >= _V22C_FLOOR_P and hour in _V22C_EMIT_HOURS
                and _V22C_STATE["emit_day"] != day):
            k = _v22c_emit_k(p)
            if day >= _V22C_ACCEL_DAY:
                k *= 2
            k = max(1, min(k, bank, 60))
            out.append(["SELL", "MILK", k])
            emitted = k
            _V22C_STATE["emit_day"] = day

        if stripped or emitted:
            action = dict(action)
            action["market"] = out
            _V22C_TELEMETRY["v22c_stripped_orders"] += int(stripped)
            _V22C_TELEMETRY["v22c_emitted_units"] += emitted
        _V22C_TELEMETRY["v22c_banked_units"] = bank
        if _V22C_STATE.get("mode_day") != day:
            _V22C_STATE["mode_day"] = day
            _V22C_TELEMETRY["v22c_mode_days"] += 1
    except Exception:
        _V22C_TELEMETRY["v22c_errors"] += 1
    return action


agent.telemetry = _V22C_TELEMETRY
