#!/usr/bin/env python3
"""Task 111b: build v27t = v27 + SALE-ADVANCE with NEAR-PEAK filter.

The unconditional ADV14 port (v27s) flipped seed 100 (+172) but self-damaged
seeds 101/102/104 by front-running items whose price would later RISE
(MELON climbs all game) or oscillate (MILK). The near-peak filter only
front-runs a planned future SELL when the item's current price is at/near
its own 6-day maximum (>= 0.95 x max) — i.e. capture the peak of the
peak-then-crash arcs (STRAWBERRY 207->14, WOOL spikes) and never sell
below the recent ceiling.

Writes kaggriculture/v27t.py (v27.py + appended layer).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27t.py")

LAYER = '''

# ===================== v27.2 LAYER — NEAR-PEAK SALE-ADVANCE =====================
# Task 111 (2026-09-19): v27t "PEAK-CAPTURING PRICE GENERAL".
# Base = v27 dual-mode crash-dump agent (2945 chassis byte-exact below).
#
# Added reflex #3 — NEAR-PEAK SALE-ADVANCE (outermost wrapper): when the
# 2945 tape plans a SELL of a pure cash product within the next 14 steps,
# the units already sit in the shed, AND the item's price is at/near its
# own 6-day maximum (>= 0.95 x max — a local peak), sell them NOW.
# Captures the peak of the peak-then-crash arcs (s100/s101 STRAWBERRY
# 207/214 -> 32/84; WOOL spikes) that the paced tape would otherwise ride
# into the ground, while never front-running steady climbers (MELON) or
# oscillators (MILK) where selling early loses money. Mechanism after the
# public sdy623/jaxa623 "Beyond 48-0" EXP293 sale-advance family
# (alperen5252525 "First in Line" / tetsutani v65 horizon-14 racers).
#
# Guards carried over from the v25.1 port: never on the dawn turn, never
# when this step buys products (feed-credit timing), the first-listed sale
# of the next turn is left alone, quantities are caps so the tape's own
# later SELL simply sells whatever was deposited since, sales frontloaded.
_V27T_PARENT = agent
globals().pop("agent", None)

_V27T_LOOK = 14
_V27T_FROM = 144
_V27T_TO = 718
_V27T_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MILK", "MELON", "CARROT", "TOMATO")
_V27T_PROTECT = True
_V27T_PEAK_RATIO = 0.95
_V27T_PEAK_LOOKBACK = 6
_V27T_STATE = {}
_V27T_REPORT = {"adv_turns": 0, "adv_units": 0, "adv_peak_hits": 0, "adv_errors": 0}


def _v27t_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27t_note_day(state, obs):
    day = _v27t_int(obs.get("day"))
    seat = _v27t_int(obs.get("player"))
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


def _v27t_near_peak(st, day, prices, item):
    """True when the item's current price is at/near its own recent maximum:
    the capture-the-peak condition. Blocks front-running while an item is
    below its ceiling (steady climbers, crash tails, oscillator troughs)."""
    days = st["days"]
    p = prices.get(item)
    if p is None or p <= 0:
        return False
    peak = 0.0
    seen = 0
    for d in range(day - 1, day - 1 - _V27T_PEAK_LOOKBACK, -1):
        if d not in days:
            continue
        v = days[d].get(item)
        if v is not None and v > peak:
            peak = v
        seen += 1
    if seen < 2:
        return False
    return p >= _V27T_PEAK_RATIO * peak


def _v27t_future(seat, t):
    """Future market orders of OUR tape, honouring the 2945 router: the route
    is locked at step 144 by the two-shop combo and hard-switches to route 2
    at step 648 (day 27)."""
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


def agent(observation, configuration=None):
    action = _V27T_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27t_int(obs.get("step"))
        seat = _v27t_int(obs.get("player"))
        day = _v27t_int(obs.get("day"))
        if step % 24 == 23 or not (_V27T_FROM <= step < _V27T_TO):
            return action
        st = _v27t_note_day(_V27T_STATE, obs)
        prices = {}
        try:
            prices = dict(obs["market"]["prices"] or {})
        except Exception:
            return action
        plan = []
        first = None
        for off in range(1, _V27T_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27t_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27T_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27T_PROTECT and first is not None and first[0] == "SELL" else None
        plan = [(t, item, q) for t, item, q in plan if item != protected]
        if not plan:
            return action
        market = [list(o) for o in (action.get("market") or [])]
        if any(len(o) > 1 and o[0] == "BUY_PRODUCT" for o in market):
            return action
        stock = projected_shed(action, FarmView(obs))
        selling = {}
        for o in market:
            if len(o) >= 3 and o[0] == "SELL":
                try:
                    selling[o[1]] = selling.get(o[1], 0) + max(0, int(o[2]))
                except Exception:
                    return action
        commands = [action.get("farmer") or ["PASS"], *(action.get("hands") or [])]
        picked = {c[1] for c in commands if len(c) > 1 and c[0] == "PICKUP"}
        extra = []
        added = 0
        for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
            if item in picked or int(prices.get(item, 0)) < 2:
                continue
            if not _v27t_near_peak(st, day, prices, item):
                continue  # capture-the-peak filter: only race at local peaks
            avail = int(stock.get(item, 0)) - selling.get(item, 0)
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
            added += n
            _V27T_REPORT["adv_peak_hits"] += 1
        if not added:
            return action
        _V27T_REPORT["adv_turns"] += 1
        _V27T_REPORT["adv_units"] += added
        action["market"] = extra + market
    except Exception:
        _V27T_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27T_REPORT
# ===================== end v27.2 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    marker = "\n\n# ===================== v27.2 LAYER"
    if marker in base:
        base = base[: base.index(marker)] + "\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
