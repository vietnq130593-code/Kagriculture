#!/usr/bin/env python3
"""Task 111c: build v27u = v27 + NEAR-PEAK SALE-ADVANCE gated to RACE MODE.

v27t (unconditional near-peak ADV) flipped s100/s101 vs v251 (5/5 seeds win)
but in CLONE mode (vs the 2945 mirror) the early sale perturbs the shared
price path and the mirror's predict machinery harvests the perturbation
better than us (s102 -2258, s104 -1924). v27u therefore reads the v27
clone-detector result (module-global _V27_STATE) and runs the near-peak
sale-advance ONLY when the opponent is NOT a 2945-family clone.

Writes kaggriculture/v27u.py (v27.py + appended layer).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27u.py")

LAYER = '''

# ===================== v27.3 LAYER — RACE-MODE NEAR-PEAK ADVANCE =====================
# Task 111 (2026-09-19): v27u "RACE-PEAK PRICE GENERAL".
# Base = v27 dual-mode crash-dump agent (2945 chassis byte-exact below).
#
# Added reflex #3 — NEAR-PEAK SALE-ADVANCE, RACE MODE ONLY (outermost
# wrapper): when the opponent is NOT a 2945-family clone (the v27
# clone-detector decides by day 8), and the 2945 tape plans a SELL of a
# pure cash product within the next 14 steps, and the units already sit
# in the shed, and the item's price is at/near its own 6-day maximum
# (>= 0.95 x max — a local peak), sell them NOW. This captures the peak
# of peak-then-crash arcs (STRAWBERRY/WOOL) that a racing opponent's
# sale-advance would otherwise harvest first, while never front-running
# steady climbers (MELON) or oscillator troughs (MILK). In clone mode the
# layer stays silent: an early sale against the identical tape perturbs
# the shared price path and the mirror's reactive machinery harvests the
# perturbation better than the seller (measured: s102 -2258, s104 -1924).
# Mechanism after the public sdy623/jaxa623 "Beyond 48-0" EXP293
# sale-advance family (alperen5252525 "First in Line" / tetsutani v65
# horizon-14 racers), adapted with the capture-the-peak filter.
#
# Guards carried over from the v25.1 port: never on the dawn turn, never
# when this step buys products (feed-credit timing), the first-listed sale
# of the next turn is left alone, quantities are caps so the tape's own
# later SELL simply sells whatever was deposited since, sales frontloaded.
_V27U_PARENT = agent
globals().pop("agent", None)

_V27U_LOOK = 14
_V27U_FROM = 144
_V27U_TO = 718
_V27U_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MILK", "MELON", "CARROT", "TOMATO")
_V27U_PROTECT = True
_V27U_PEAK_RATIO = 0.95
_V27U_PEAK_LOOKBACK = 6
_V27U_STATE = {}
_V27U_REPORT = {"adv_turns": 0, "adv_units": 0, "adv_peak_hits": 0, "adv_errors": 0}


def _v27u_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27u_note_day(state, obs):
    day = _v27u_int(obs.get("day"))
    seat = _v27u_int(obs.get("player"))
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


def _v27u_race_mode(seat, day):
    """True only when the v27 clone-detector has decided the opponent is NOT
    a 2945-family clone (race mode). None/True -> stay silent."""
    try:
        st = _V27_STATE.get(seat)
        if not st:
            return False
        clone = st.get("clone")
        if day < 9:
            return False  # detector still undecided
        return clone is False
    except Exception:
        return False


def _v27u_near_peak(st, day, prices, item):
    """True when the item's current price is at/near its own recent maximum:
    the capture-the-peak condition. Blocks front-running while an item is
    below its ceiling (steady climbers, crash tails, oscillator troughs)."""
    days = st["days"]
    p = prices.get(item)
    if p is None or p <= 0:
        return False
    peak = 0.0
    seen = 0
    for d in range(day - 1, day - 1 - _V27U_PEAK_LOOKBACK, -1):
        if d not in days:
            continue
        v = days[d].get(item)
        if v is not None and v > peak:
            peak = v
        seen += 1
    if seen < 2:
        return False
    return p >= _V27U_PEAK_RATIO * peak


def _v27u_future(seat, t):
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
    action = _V27U_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27u_int(obs.get("step"))
        seat = _v27u_int(obs.get("player"))
        day = _v27u_int(obs.get("day"))
        if step % 24 == 23 or not (_V27U_FROM <= step < _V27U_TO):
            return action
        if not _v27u_race_mode(seat, day):
            return action  # clone mode: stay silent (measured perturbation loss)
        st = _v27u_note_day(_V27U_STATE, obs)
        prices = {}
        try:
            prices = dict(obs["market"]["prices"] or {})
        except Exception:
            return action
        plan = []
        first = None
        for off in range(1, _V27U_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27u_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27U_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27U_PROTECT and first is not None and first[0] == "SELL" else None
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
            if not _v27u_near_peak(st, day, prices, item):
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
            _V27U_REPORT["adv_peak_hits"] += 1
        if not added:
            return action
        _V27U_REPORT["adv_turns"] += 1
        _V27U_REPORT["adv_units"] += added
        action["market"] = extra + market
    except Exception:
        _V27U_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27U_REPORT
# ===================== end v27.3 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    marker = "\n\n# ===================== v27.3 LAYER"
    if marker in base:
        base = base[: base.index(marker)] + "\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
