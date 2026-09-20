#!/usr/bin/env python3
"""Task 111f: build v27y = v27x + TROUGH-HOLD + loosened peak/rollover.

The 2945 tape donates WOOL at $1 for ~10 days after the mid-game wool
collapse (s101: WOOL 1..5 from d14, bouncing to 61/88/93 at d25-27; the
tape's 6-8 unit dribbles fill those troughs). A trough-hold layer (race
mode only) zeroes the tape's dribble SELLs of a deep-trough item (price
< 0.30 x 6-day ceiling, ceiling >= 10) while the shed stays under 40
units of it and the total shed under 60 (capacity guard), so the stock
rides the bounce and drains at the recovered prices (the tape's late
sells + terminal flush). MILK excluded (consistent with the race-mode
no-MILK rule: s100 milk never recovers). Terminal flush orders (caps
>= 500) are never zeroed.

Also loosened: ROLL_CEIL 0.98 -> 0.93 (the s101 WOOL break was missed by
a hair: yest-open 181 vs 0.98 x 187), PEAK_RATIO 0.95 -> 0.90 (s101 STR
201-209 vs peak 214 was filtered).

Writes kaggriculture/v27y.py (v27.py + patched race dump + appended layer).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27y.py")

V27_LAYER_PATCH_OLD = """        for item in sorted(crashing):
            have = _v27_int(shed.get(item))
            if have <= 0:
                continue
            extended = False
            for o in market:
                if (
                    isinstance(o, list)
                    and len(o) >= 3
                    and o[0] == "SELL"
                    and o[1] == item
                ):
                    try:
                        o[2] = max(_v27_int(o[2]), have + 50)
                    except Exception:
                        pass
                    extended = True
                    break
            if not extended and len(market) < 10:
                market.append(["SELL", item, have + 50])"""

V27_LAYER_PATCH_NEW = """        for item in sorted(crashing):
            have = _v27_int(shed.get(item))
            if have <= 0:
                continue
            extended = False
            for o in market:
                if (
                    isinstance(o, list)
                    and len(o) >= 3
                    and o[0] == "SELL"
                    and o[1] == item
                ):
                    try:
                        o[2] = max(_v27_int(o[2]), have + 50)
                    except Exception:
                        pass
                    extended = True
                    break
            if not extended and len(market) < 10:
                market.append(["SELL", item, have + 50])"""

LAYER = '''

# ===================== v27.6 LAYER — TROUGH-HOLD + RACE-PEAK =====================
# Task 111 (2026-09-19): v27y "TROUGH-HOLDING PRICE GENERAL".
# v27y = v27x (near-peak sale-advance + peak-rollover dump + paced race
# dump) + TROUGH-HOLD: the 2945 tape donates WOOL (and dead products) at
# $1 troughs while the price bounces 60x at the end of the arc; the hold
# rides the bounce instead. Race mode only; MILK excluded; flush orders
# (cap >= 500) untouched; capacity-guarded (shed[item] < 40, total < 60).
# Loosened detectors: ROLL_CEIL 0.93, PEAK_RATIO 0.90.
_V27Y_PARENT = agent
globals().pop("agent", None)

_V27Y_LOOK = 14
_V27Y_FROM = 144
_V27Y_TO = 700          # hold/act window ends before the terminal flush
_V27Y_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MELON", "CARROT", "TOMATO")
_V27Y_PROTECT = True
_V27Y_PEAK_RATIO = 0.90
_V27Y_PEAK_LOOKBACK = 6
_V27Y_ROLL_CEIL = 0.93
_V27Y_ROLL_BREAK = 0.97
_V27Y_ROLL_MIN = 3
_V27Y_CHUNK = 6
_V27Y_TROUGH_RATIO = 0.30
_V27Y_TROUGH_MIN_PEAK = 10
_V27Y_HOLD_ITEM_CAP = 40
_V27Y_HOLD_TOTAL_CAP = 60
_V27Y_STATE = {}
_V27Y_REPORT = {"adv_turns": 0, "adv_units": 0, "roll_turns": 0,
                "roll_units": 0, "hold_turns": 0, "adv_errors": 0}


def _v27y_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27y_note_day(state, obs):
    day = _v27y_int(obs.get("day"))
    seat = _v27y_int(obs.get("player"))
    st = state.setdefault(seat, {"days": {}})
    prices = {}
    try:
        prices = dict(obs["market"]["prices"] or {})
    except Exception:
        prices = {}
    if day not in st["days"] and prices:
        st["days"][day] = prices
    if len(st["days"]) > 40:
        for d in sorted(st["days"])[:-40]:
            del st["days"][d]
    return st


def _v27y_race_mode(seat, day):
    try:
        st = _V27_STATE.get(seat)
        if not st:
            return False
        if day < 9:
            return False
        return st.get("clone") is False
    except Exception:
        return False


def _v27y_ceiling(st, day, item):
    days = st["days"]
    peak = 0.0
    seen = 0
    for d in range(day - 1, day - 1 - _V27Y_PEAK_LOOKBACK, -1):
        if d not in days:
            continue
        v = days[d].get(item)
        if v is not None and v > peak:
            peak = v
        seen += 1
    yest = None
    if day - 1 in days:
        yest = days[day - 1].get(item)
    return peak, yest, seen


def _v27y_near_peak(st, day, prices, item):
    peak, _, seen = _v27y_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or seen < 2:
        return False
    return p >= _V27Y_PEAK_RATIO * peak


def _v27y_rollover(st, day, prices, item):
    peak, yest, seen = _v27y_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or yest is None or seen < 2 or peak <= 0:
        return False
    if yest < _V27Y_ROLL_CEIL * peak:
        return False
    return p <= _V27Y_ROLL_BREAK * yest


def _v27y_trough(st, day, prices, item):
    peak, _, seen = _v27y_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or seen < 2:
        return False
    if peak < _V27Y_TROUGH_MIN_PEAK:
        return False
    return p < _V27Y_TROUGH_RATIO * peak


def _v27y_future(seat, t):
    try:
        chassis = _IMPL.chassis
        native = chassis.players.get(seat) or {}
        route = native.get("route")
        if t >= 648 or route is None or route not in chassis.routes:
            route = 2 if 2 in chassis.routes else next(iter(chassis.routes))
        tape = chassis.routes[route]
        if 0 <= t < len(tape) and isinstance(tape[t], dict):
            return tape[t].get("market") or []
    except Exception:
        pass
    return []


def _v27y_market_caps(action):
    caps = {}
    for o in action.get("market") or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            try:
                caps[o[1]] = caps.get(o[1], 0) + max(0, int(o[2]))
            except Exception:
                pass
    return caps


def _v27y_add_sell(action, item, qty):
    market = action.get("market")
    if market is None:
        market = []
        action["market"] = market
    if not isinstance(market, list):
        return False
    for o in market:
        if (isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
                and o[1] == item):
            try:
                o[2] = max(_v27y_int(o[2]), qty + 50)
            except Exception:
                pass
            return True
    if len(market) >= 10:
        return False
    market.append(["SELL", item, qty + 50])
    return True


def agent(observation, configuration=None):
    action = _V27Y_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27y_int(obs.get("step"))
        seat = _v27y_int(obs.get("player"))
        day = _v27y_int(obs.get("day"))
        if step % 24 == 23 or not (_V27Y_FROM <= step < _V27Y_TO):
            return action
        if not _v27y_race_mode(seat, day):
            return action  # clone mode: stay silent
        st = _v27y_note_day(_V27Y_STATE, obs)
        prices = {}
        try:
            prices = dict(obs["market"]["prices"] or {})
        except Exception:
            return action
        market = [list(o) for o in (action.get("market") or [])]
        if any(len(o) > 1 and o[0] == "BUY_PRODUCT" for o in market):
            return action
        stock = projected_shed(action, FarmView(obs))
        commands = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
        picked = {c[1] for c in commands if len(c) > 1 and c[0] == "PICKUP"}
        total_shed = sum(_v27y_int(v) for v in stock.values())

        # ---- (c) trough-hold: zero the dribble SELLs of deep-trough items ----
        held = False
        for item in _V27Y_ITEMS:
            if not _v27y_trough(st, day, prices, item):
                continue
            if _v27y_int(stock.get(item)) >= _V27Y_HOLD_ITEM_CAP:
                continue
            if total_shed >= _V27Y_HOLD_TOTAL_CAP:
                continue
            for o in market:
                if (isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
                        and o[1] == item and _v27y_int(o[2]) < 500):
                    o[2] = 0  # hold the units for the bounce (keep the slot)
                    held = True
        if held:
            _V27Y_REPORT["hold_turns"] += 1

        # ---- (b) peak-rollover dump (paced) ----
        rolled = False
        for item in _V27Y_ITEMS:
            if item in picked:
                continue
            p = prices.get(item)
            if p is None or int(p) < 2:
                continue
            if _v27y_trough(st, day, prices, item):
                continue  # never dump into a trough
            if not _v27y_rollover(st, day, prices, item):
                continue
            caps = _v27y_market_caps(action)
            avail = _v27y_int(stock.get(item)) - caps.get(item, 0)
            if avail < _V27Y_ROLL_MIN:
                continue
            if _v27y_add_sell(action, item, min(avail, _V27Y_CHUNK)):
                rolled = True
                _V27Y_REPORT["roll_turns"] += 1
                _V27Y_REPORT["roll_units"] += min(avail, _V27Y_CHUNK)

        # ---- (a) near-peak sale-advance (dribbles) ----
        plan = []
        first = None
        for off in range(1, _V27Y_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27y_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27Y_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27Y_PROTECT and first is not None and first[0] == "SELL" else None
        plan = [(t, item, q) for t, item, q in plan if item != protected]
        added = 0
        if plan:
            market = [list(o) for o in (action.get("market") or [])]
            selling = _v27y_market_caps({"market": market})
            extra = []
            for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
                if item in picked or int(prices.get(item, 0)) < 2:
                    continue
                if _v27y_trough(st, day, prices, item):
                    continue  # never front-run into a trough
                if not _v27y_near_peak(st, day, prices, item):
                    continue
                avail = _v27y_int(stock.get(item)) - selling.get(item, 0)
                if avail < 1:
                    continue
                hit = next((o for o in market if len(o) >= 3 and o[0] == "SELL" and o[1] == item), None)
                if hit is None and len(market) + len(extra) >= 10:
                    continue
                n = 0
                for t, it, q in plan:
                    if it != item or avail <= 0:
                        continue
                    take = min(q, avail)
                    n += take
                    avail -= take
                if n < 1:
                    continue
                if hit is not None:
                    hit[2] = int(hit[2]) + n
                else:
                    extra.append(["SELL", item, n])
                selling[item] = selling.get(item, 0) + n
                added += n
            if added:
                _V27Y_REPORT["adv_turns"] += 1
                _V27Y_REPORT["adv_units"] += added
                action["market"] = extra + market
        if not (rolled or added or held):
            return action
    except Exception:
        _V27Y_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27Y_REPORT
# ===================== end v27.6 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    # register the chunk constant (kept for the paced race dump parity with v27x)
    anchor = "_V27_MIN_DAY = 9\n"
    assert anchor in base
    base = base.replace(anchor, anchor + "_V27X_CHUNK = 6  # race-mode paced dump chunk (Task 111)\n", 1)
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
