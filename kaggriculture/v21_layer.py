# ================================================================= v21 FLOOR-BANKER layer
# Garbage-price sell-gating for WOOL over the v19.4 chain.
#
# WHY (measured, 8-seed probe 2026-09-17, v20 vs ahmedv46, full 720-turn games):
#   Three sibling experiments defined the design space:
#     v1 bank+liquidate (WOOL/STRA/MELON, floor 100-140): -$1,030/game — the
#        liquidate dump re-crashes the recovery and the free-rider effect
#        (our withholding raises the price v46 keeps selling into) eats the edge.
#     v2 trim-only WOOL floor 120: -$307/game — withheld $50-98 trough sales
#        that REAPER then sold at the same $55-88: a wash plus free-riding.
#     v3 COW->SHEEP swap: -$18K/game — vacating MILK hands v46 a monopoly on
#        a $250+ milk market (town drain continues) — mix-shifts transfer value
#        to the opponent in a shared 2-player market.
#   The surviving edge is the narrow one: WOOL sells priced $1-15 are garbage
#   (near the engine floor; the $1-floor rule means they add no supply, so
#   withholding them costs nothing and slightly speeds the town-drain
#   recovery), while the endgame REAPER liquidation still sells the banked
#   wool at the recovered price ($61-120 measured in the crash seeds).
#   Expected: +$1-2K in wool-crash seeds, ~0 elsewhere.
#
# MECHANISM:
#   While WOOL price < $15 and 216 <= step < 648 and hour < 21 (preguard
#   boundary) and money >= 1500 and shed_total < 85: trim the chassis's
#   SELL WOOL orders down to the cap-overflow release (bank up to 25 wool).
#   Everything else passes through untouched.  No liquidation pass — the
#   bank rides to REAPER.  Fail-open on any exception.

_V21_HOST = _V194  # noqa: F821  (v19.4's entry point from the embedded namespace)

_V21_FROM_STEP = 216
_V21_ENDGAME_STEP = 648          # REAPER (v19 layer A1) owns 648+ untouched
_V21_MONEY_GUARD = 1500
_V21_SHED_GUARD = 85
_V21_ITEM = "WOOL"
_V21_GARBAGE_P = 15              # bank only garbage-priced sells
_V21_CAP = 25                    # max banked units

_V21_TELEMETRY = {"v21_banked_units": 0, "v21_released_units": 0,
                  "v21_trimmed_orders": 0, "v21_pass_turns": 0,
                  "v21_errors": 0}


def _v21_standard(configuration):
    if configuration is None:
        return True
    try:
        return all(configuration.get(k, v) == v for k, v in (
            ("boardSize", 10), ("turnsPerDay", 24), ("shedCapacity", 100),
            ("maxMarketOrdersPerTurn", 10), ("farmHandCostMult", 1),
        )) and not configuration.get("marketParams", None)
    except Exception:
        return False


def _v21_int(x, default=0):
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def agent(observation, configuration=None):
    action = _V21_HOST(observation, configuration)
    try:
        if not _v21_standard(configuration) or not isinstance(action, dict):
            return action
        step = _v21_int(observation.get("step"), -1)
        if step < _V21_FROM_STEP or step >= _V21_ENDGAME_STEP:
            _V21_TELEMETRY["v21_pass_turns"] += 1
            return action
        if (step % 24) >= 21:          # preguard h21/22 + auto-drop h23
            _V21_TELEMETRY["v21_pass_turns"] += 1
            return action

        prices = (observation.get("market") or {}).get("prices") or {}
        p = _v21_int(prices.get(_V21_ITEM), 10 ** 9)
        if p >= _V21_GARBAGE_P:       # price fine: chassis behavior untouched
            _V21_TELEMETRY["v21_pass_turns"] += 1
            return action

        seat = _v21_int(observation.get("player"), 0)
        farms = observation.get("farms") or []
        money = 0.0
        if 0 <= seat < len(farms):
            money = float((farms[seat] or {}).get("money") or 0)
        if money < _V21_MONEY_GUARD:
            _V21_TELEMETRY["v21_pass_turns"] += 1
            return action
        shed = ((observation.get("private") or {}).get("shed")) or {}
        # v5: shed-total guard removed — the chassis's 100-wheat feed buffer
        # masked it every mid-game turn. The bank itself is bounded by _V21_CAP.

        market = action.get("market")
        if not isinstance(market, list) or not market:
            _V21_TELEMETRY["v21_pass_turns"] += 1
            return action

        held = _v21_int(shed.get(_V21_ITEM), 0)
        over = max(0, held - _V21_CAP)   # release overflow above the cap
        remaining = over
        out = []
        trimmed = False
        for o in market:
            if (isinstance(o, (list, tuple)) and len(o) >= 3
                    and o[0] == "SELL" and o[1] == _V21_ITEM
                    and isinstance(o[2], (int, float))):
                orig_n = _v21_int(o[2], 0)
                n = min(orig_n, max(0, remaining))
                banked = orig_n - n
                if banked > 0:
                    _V21_TELEMETRY["v21_banked_units"] += banked
                    trimmed = True        # order changed (or fully removed)
                if n > 0:
                    no = list(o)
                    no[2] = n
                    out.append(no)
                    remaining -= n
                    _V21_TELEMETRY["v21_trimmed_orders"] += 1
                continue
            out.append(o)
        if trimmed:
            action = dict(action)
            action["market"] = out
    except Exception:
        _V21_TELEMETRY["v21_errors"] += 1
    return action


agent.telemetry = _V21_TELEMETRY
