#!/usr/bin/env python3
"""Task 111e: build v27x = v27w + RACE-MODE DUMP PACING.

vs alperen1 s100 the race-mode crash-dump (r95) dumps ~20 STRAWBERRY in one
order at ~55; the fill walks the book down to 16 by end of day. alperen1's
market-maker paces 5-unit dribbles and the intraday demand recovery keeps
its fills at 49-70. Fix: in RACE MODE the crash-dump extension adds at most
CHUNK units per turn per item (paced flush through the recovering intraday
price); CLONE MODE keeps the validated full dump (10-0 record, untouched).
Appends logging of race-mode dump extensions to /tmp for debugging.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27x.py")

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

V27_LAYER_PATCH_NEW = """        _v27x_pace = is_clone is False  # race mode: paced extension
        for item in sorted(crashing):
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
                        if _v27x_pace:
                            o[2] = min(_v27_int(o[2]) + _V27X_CHUNK, have + 50)
                        else:
                            o[2] = max(_v27_int(o[2]), have + 50)
                    except Exception:
                        pass
                    extended = True
                    break
            if not extended and len(market) < 10:
                market.append(["SELL", item, min(have, _V27X_CHUNK) if _v27x_pace else have + 50])
            try:
                if _v27x_pace:
                    with open("/tmp/v27xdump.log", "a") as _f:
                        _f.write(f"DUMP d{day} s{step%24} {item} have={have} paced=True\\n")
            except Exception:
                pass"""

LAYER = '''

# ===================== v27.5 LAYER — RACE-PEAK + ROLLOVER + PACED DUMP =====================
# Task 111 (2026-09-19): v27x "PACED-PEAK PRICE GENERAL" = v27w (near-peak
# sale-advance + peak-rollover dump, race mode only) on top of a v27 layer
# whose RACE-MODE crash-dump extension is PACED (at most _V27X_CHUNK units
# per turn per item): single giant orders walk the intraday book down
# (measured: 20@55 fills into a 55->16 collapse) while the opponent's
# market-makers absorb paced dribbles at recovering prices (49-70).
# Clone mode keeps the validated full dump (10-0 record, untouched).
_V27X_PARENT = agent
globals().pop("agent", None)

_V27X_LOOK = 14
_V27X_FROM = 144
_V27X_TO = 718
_V27X_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MILK", "MELON", "CARROT", "TOMATO")
_V27X_PROTECT = True
_V27X_PEAK_RATIO = 0.95
_V27X_PEAK_LOOKBACK = 6
_V27X_ROLL_CEIL = 0.98
_V27X_ROLL_BREAK = 0.97
_V27X_ROLL_MIN = 3
_V27X_CHUNK = 6
_V27X_STATE = {}
_V27X_REPORT = {"adv_turns": 0, "adv_units": 0, "roll_turns": 0,
                "roll_units": 0, "adv_errors": 0}


def _v27x_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27x_note_day(state, obs):
    day = _v27x_int(obs.get("day"))
    seat = _v27x_int(obs.get("player"))
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


def _v27x_race_mode(seat, day):
    try:
        st = _V27_STATE.get(seat)
        if not st:
            return False
        if day < 9:
            return False
        return st.get("clone") is False
    except Exception:
        return False


def _v27x_ceiling(st, day, item):
    days = st["days"]
    peak = 0.0
    seen = 0
    for d in range(day - 1, day - 1 - _V27X_PEAK_LOOKBACK, -1):
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


def _v27x_near_peak(st, day, prices, item):
    peak, _, seen = _v27x_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or seen < 2:
        return False
    return p >= _V27X_PEAK_RATIO * peak


def _v27x_rollover(st, day, prices, item):
    peak, yest, seen = _v27x_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or yest is None or seen < 2 or peak <= 0:
        return False
    if yest < _V27X_ROLL_CEIL * peak:
        return False
    return p <= _V27X_ROLL_BREAK * yest


def _v27x_future(seat, t):
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


def _v27x_market_caps(action):
    caps = {}
    for o in action.get("market") or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            try:
                caps[o[1]] = caps.get(o[1], 0) + max(0, int(o[2]))
            except Exception:
                pass
    return caps


def _v27x_add_sell(action, item, qty):
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
                o[2] = max(_v27x_int(o[2]), qty + 50)
            except Exception:
                pass
            return True
    if len(market) >= 10:
        return False
    market.append(["SELL", item, qty + 50])
    return True


def agent(observation, configuration=None):
    action = _V27X_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27x_int(obs.get("step"))
        seat = _v27x_int(obs.get("player"))
        day = _v27x_int(obs.get("day"))
        if step % 24 == 23 or not (_V27X_FROM <= step < _V27X_TO):
            return action
        if not _v27x_race_mode(seat, day):
            return action  # clone mode: stay silent
        st = _v27x_note_day(_V27X_STATE, obs)
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

        # ---- (b) peak-rollover full-shed dump (paced like the crash-dump) ----
        rolled = False
        for item in _V27X_ITEMS:
            if item in picked:
                continue
            p = prices.get(item)
            if p is None or int(p) < 2:
                continue
            if not _v27x_rollover(st, day, prices, item):
                continue
            caps = _v27x_market_caps(action)
            avail = _v27x_int(stock.get(item)) - caps.get(item, 0)
            if avail < _V27X_ROLL_MIN:
                continue
            if _v27x_add_sell(action, item, min(avail, _V27X_CHUNK)):
                rolled = True
                _V27X_REPORT["roll_turns"] += 1
                _V27X_REPORT["roll_units"] += min(avail, _V27X_CHUNK)

        # ---- (a) near-peak sale-advance (dribbles) ----
        plan = []
        first = None
        for off in range(1, _V27X_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27x_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27X_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27X_PROTECT and first is not None and first[0] == "SELL" else None
        plan = [(t, item, q) for t, item, q in plan if item != protected]
        added = 0
        if plan:
            market = [list(o) for o in (action.get("market") or [])]
            selling = _v27x_market_caps({"market": market})
            extra = []
            for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
                if item in picked or int(prices.get(item, 0)) < 2:
                    continue
                if not _v27x_near_peak(st, day, prices, item):
                    continue
                avail = _v27x_int(stock.get(item)) - selling.get(item, 0)
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
                _V27X_REPORT["adv_turns"] += 1
                _V27X_REPORT["adv_units"] += added
                action["market"] = extra + market
        if not (rolled or added):
            return action
    except Exception:
        _V27X_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27X_REPORT
# ===================== end v27.5 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    assert V27_LAYER_PATCH_OLD in base, "v27 layer dump block not found"
    base = base.replace(V27_LAYER_PATCH_OLD, V27_LAYER_PATCH_NEW)
    # register the chunk constant before the v27 layer's agent function
    anchor = "_V27_MIN_DAY = 9\n"
    assert anchor in base
    base = base.replace(anchor, anchor + "_V27X_CHUNK = 6  # race-mode paced dump chunk (Task 111)\n", 1)
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
