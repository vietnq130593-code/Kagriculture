# ================================================================== v19.1 OPENING layer
# First-turn microstructure — ported mechanism (not source) from ahmedberatozer's
# public V46 notebook "KaggressurE V46: First-Turn Microstructure and Sale Timing"
# (EXP284/EXP293, Apache-2.0), re-implemented over our v18/v19 chassis.
#
# WHY (Task 87 baseline batteries, 24 seeds x 2 seats, official runner):
#   v19 vs ahmedv46 : 2W/46L, mean -$396  <- the v46 opening+timing beats our family
#   v19 vs seyit4   : 46W/2L, mean +$1225
# The ladder's V43..V46 public lineage all run the same day-0/day-1 tape; whoever
# prices the first two market turns better wins the cash slack that funds the
# MELON opening (seed $80-104, ROI 14-18x per research/06) — a $25-50 early
# swing compounds into a four-figure margin.
#
# MECHANISM (verified empirically on our V43 parent, seed 42, both seats):
#   step 0  v18 emits [BUY 50, SELL 50] (net-0 wheat round trip). It lifts the
#           rival's step-0 second buy but lets a rival small SELL at index 1
#           ride the same lift: measured -32..-77 cash vs [BUY 5, SELL 5] /
#           [BUY 50, SELL 50] rivals (v46's published live-replay analysis).
#           v19.1 instead buys its five feed units once, at index 0 of turn 0
#           ([BUY 7, SELL 2]): cheapest quotes, immune to rival round trips,
#           and the 2-unit SELL rides any rival lift.
#   step 1  the whole V43-lineage tape (ours and the public family) buys its
#           five feed units at index 1 ([SELL 13, BUY 5, ...]). A BUY at
#           index 0 executes first and lifts those quotes ~4/unit — above the
#           tape's day-0 slack. v19.1 strips its own SELL 13/BUY 5 (shed keeps
#           exactly the tape's five units) and, when cash allows, attacks with
#           BUY 30 at index 0.
#   step 2  no tape trades; the attack units are sold back into the lifted
#           quotes — the trip pays for itself (measured vs v18: buy 30 = -$886,
#           sell 30 = +$901; the attacked BUY 5 pays +$25 extra).
#
# Robustness gates (v46's published tuning, adopted verbatim):
#   - attack only when money >= 2860 at step 1 (step-0 went clean);
#   - sell back only what the shed actually holds (cap semantics);
#   - whole layer is a no-op on any non-standard configuration or mismatch;
#   - per-seat state, reset on episode restart (C1 pattern from v19_layer).

_V191_HOST = _V19  # noqa: F821  (v19's entry point, captured before redefinition)

_V191_STEP0 = [["BUY_PRODUCT", "WHEAT", 7], ["SELL", "WHEAT", 2]]
_V191_V18_OPEN = [["BUY_PRODUCT", "WHEAT", 50], ["SELL", "WHEAT", 50]]
_V191_TAPE_OPEN = [["BUY_PRODUCT", "WHEAT", 5], ["BUY_PRODUCT", "WHEAT", 10], ["SELL", "WHEAT", 60]]
_V191_ATTACK = 30
_V191_ATTACK_MIN_CASH = 2860
_V191_TELEMETRY = {"open_turns": 0, "open_attack": 0, "open_errors": 0}
_V191_STATE = {0: {"last": -1, "attack": 0}, 1: {"last": -1, "attack": 0}}


def _v191_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("startingMoney", 3000),
        ))
    except Exception:
        return False


def agent(observation, configuration=None):
    action = _V191_HOST(observation, configuration)
    try:
        step = int(observation["step"])
        player = int(observation["player"])
        st = _V191_STATE.get(player)
        if st is None or step <= st["last"]:
            st = _V191_STATE[player] = {"last": -1, "attack": 0}
        st["last"] = step
        if step == 0:
            _V191_TELEMETRY.update(open_turns=0, open_attack=0, open_errors=0)
        if not (_v191_standard(configuration) and isinstance(action, dict) and step <= 2):
            return action
        market = [list(o) for o in (action.get("market") or [])]
        if step == 0 and (market == _V191_V18_OPEN or market == _V191_TAPE_OPEN):
            action = dict(action, market=[list(o) for o in _V191_STEP0])
            _V191_TELEMETRY["open_turns"] += 1
        elif (step == 1 and len(market) >= 2
              and market[0] == ["SELL", "WHEAT", 13]
              and market[1] == ["BUY_PRODUCT", "WHEAT", 5]):
            market = market[2:]
            _V191_TELEMETRY["open_turns"] += 1
            if (_V191_ATTACK
                    and float(observation["farms"][player]["money"]) >= _V191_ATTACK_MIN_CASH):
                market = [["BUY_PRODUCT", "WHEAT", _V191_ATTACK]] + market
                st["attack"] = _V191_ATTACK
                _V191_TELEMETRY["open_attack"] = _V191_ATTACK
            action = dict(action, market=market)
        elif step == 2 and st["attack"]:
            shed = (observation.get("private") or {}).get("shed") or {}
            back = min(st["attack"], max(0, int(shed.get("WHEAT", 0) or 0)))
            st["attack"] = 0
            if back > 0 and not (market and market[0] == ["SELL", "WHEAT", back]):
                market = [["SELL", "WHEAT", back]] + market[:9]
                action = dict(action, market=market)
                _V191_TELEMETRY["open_turns"] += 1
    except Exception:
        _V191_TELEMETRY["open_errors"] += 1
    _V191_TELEMETRY.update(getattr(_V191_HOST, "telemetry", {}))
    return action


agent.telemetry = _V191_TELEMETRY
