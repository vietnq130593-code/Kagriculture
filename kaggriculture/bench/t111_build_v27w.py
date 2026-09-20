#!/usr/bin/env python3
"""Task 111d: build v27w = v27u + PEAK-ROLLOVER full-shed dump.

The dribble-ADV (v27u) flipped s100/s101 vs v251 but the 2945 tape only
dribbles 4-12 STRAWBERRY units per sell, so front-running dribbles gains
little. The big money is in the structural intraday breaks: MELON 271->131
inside d10 (s100/s101), WOOL 154->1 at d14 (s101), STRAWBERRY 207->32
(s100). The existing crash-dump fires only AFTER "yesterday <= 0.92 x
4-day peak" — one day late, selling into the hole (76, or even price 1).

The peak-rollover dump sells the WHOLE projected shed at the FIRST downtick
from near the ceiling: yesterday's opening >= 0.98 x 6-day max AND current
price <= 0.97 x yesterday's open. Monotonic climbers (EGG +1/day, MELON
+2-3/day without breaks) never trip the 3% intraday drop, so the filter
self-selects real breaks. Race mode only — clone mode stays silent
(measured perturbation loss vs the mirror).

Writes kaggriculture/v27w.py (v27.py + appended layer).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27w.py")

LAYER = '''

# ===================== v27.4 LAYER — RACE-PEAK + ROLLOVER DUMP =====================
# Task 111 (2026-09-19): v27w "PEAK-ROLLOVER PRICE GENERAL".
# Base = v27 dual-mode crash-dump agent (2945 chassis byte-exact below).
#
# Added reflex #3 (race mode only, outermost wrapper), two coupled parts:
#
#  (a) NEAR-PEAK SALE-ADVANCE — when the opponent is NOT a 2945-family
#      clone (the v27 clone-detector decides by day 8), the 2945 tape
#      plans a SELL of a pure cash product within 14 steps, the units sit
#      in the shed, and the price is at/near its 6-day max (>= 0.95 x),
#      sell them now (mechanism after the public sdy623/jaxa623 "Beyond
#      48-0" EXP293 sale-advance family; alperen5252525 "First in Line" /
#      tetsutani v65 horizon-14 racers).
#
#  (b) PEAK-ROLLOVER DUMP — the big money: structural intraday breaks
#      (MELON 271->131 inside d10, WOOL 154->1 at d14, STRAWBERRY
#      207->32) are invisible to the crash-dump until a day late. When
#      yesterday's opening was at/near the item's 6-day ceiling (>= 0.98
#      x max) and the current price has dropped >= 3% below that opening,
#      dump the WHOLE projected shed now. Monotonic climbers (EGG/MELON
#      +1-3/day, no intraday breaks) never trip the 3% drop.
#
# Clone mode stays completely silent: an early sale against the identical
# tape perturbs the shared price path and the mirror's reactive machinery
# harvests the perturbation better than the seller (measured s102 -2258,
# s104 -1924 in the unconditional variant).
#
# Guards carried over from the v25.1 port: never on the dawn turn, never
# when this step buys products (feed-credit timing), the first-listed sale
# of the next turn is left alone, quantities are caps so the tape's own
# later SELL simply sells whatever was deposited since, sales frontloaded.
_V27W_PARENT = agent
globals().pop("agent", None)

_V27W_LOOK = 14
_V27W_FROM = 144
_V27W_TO = 718
_V27W_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MILK", "MELON", "CARROT", "TOMATO")
_V27W_PROTECT = True
_V27W_PEAK_RATIO = 0.95
_V27W_PEAK_LOOKBACK = 6
_V27W_ROLL_CEIL = 0.98      # yesterday's open must be >= this x 6-day max
_V27W_ROLL_BREAK = 0.97     # current price must drop below this x yesterday's open
_V27W_ROLL_MIN = 3          # minimum units worth dumping
_V27W_STATE = {}
_V27W_REPORT = {"adv_turns": 0, "adv_units": 0, "roll_turns": 0,
                "roll_units": 0, "adv_errors": 0}


def _v27w_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27w_note_day(state, obs):
    day = _v27w_int(obs.get("day"))
    seat = _v27w_int(obs.get("player"))
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


def _v27w_race_mode(seat, day):
    """True only when the v27 clone-detector has decided the opponent is NOT
    a 2945-family clone (race mode)."""
    try:
        st = _V27_STATE.get(seat)
        if not st:
            return False
        if day < 9:
            return False
        return st.get("clone") is False
    except Exception:
        return False


def _v27w_ceiling(st, day, item):
    """Max of the item's daily OPENING prices over the lookback window
    (yesterday .. lookback days). Returns (peak, yesterday_open)."""
    days = st["days"]
    peak = 0.0
    seen = 0
    for d in range(day - 1, day - 1 - _V27W_PEAK_LOOKBACK, -1):
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


def _v27w_near_peak(st, day, prices, item):
    """Capture-the-peak filter for the dribble advance: current price at/near
    its own recent maximum."""
    peak, _, seen = _v27w_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or seen < 2:
        return False
    return p >= _V27W_PEAK_RATIO * peak


def _v27w_rollover(st, day, prices, item):
    """Peak-rollover break detector: yesterday opened at/near the 6-day
    ceiling and the current price has broken >= 3% below that opening."""
    peak, yest, seen = _v27w_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or yest is None or seen < 2 or peak <= 0:
        return False
    if yest < _V27W_ROLL_CEIL * peak:
        return False
    return p <= _V27W_ROLL_BREAK * yest


def _v27w_future(seat, t):
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


def _v27w_market_caps(action):
    """Current SELL quantity caps per item in the action's market list."""
    caps = {}
    for o in action.get("market") or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            try:
                caps[o[1]] = caps.get(o[1], 0) + max(0, int(o[2]))
            except Exception:
                pass
    return caps


def _v27w_add_sell(action, item, qty):
    """Extend an existing SELL of the item or append a new one (cap +50
    headroom like the crash-dump). Returns True when an order was placed."""
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
                o[2] = max(_v27w_int(o[2]), qty + 50)
            except Exception:
                pass
            return True
    if len(market) >= 10:
        return False
    market.append(["SELL", item, qty + 50])
    return True


def agent(observation, configuration=None):
    action = _V27W_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27w_int(obs.get("step"))
        seat = _v27w_int(obs.get("player"))
        day = _v27w_int(obs.get("day"))
        if step % 24 == 23 or not (_V27W_FROM <= step < _V27W_TO):
            return action
        if not _v27w_race_mode(seat, day):
            return action  # clone mode: stay silent (measured perturbation loss)
        st = _v27w_note_day(_V27W_STATE, obs)
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

        # ---- (b) peak-rollover full-shed dump ----
        rolled = False
        for item in _V27W_ITEMS:
            if item in picked:
                continue
            p = prices.get(item)
            if p is None or int(p) < 2:
                continue
            if not _v27w_rollover(st, day, prices, item):
                continue
            caps = _v27w_market_caps(action)
            avail = _v27w_int(stock.get(item)) - caps.get(item, 0)
            if avail < _V27W_ROLL_MIN:
                continue
            if _v27w_add_sell(action, item, avail):
                rolled = True
                _V27W_REPORT["roll_turns"] += 1
                _V27W_REPORT["roll_units"] += avail

        # ---- (a) near-peak sale-advance (dribbles) ----
        plan = []
        first = None
        for off in range(1, _V27W_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27w_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27W_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27W_PROTECT and first is not None and first[0] == "SELL" else None
        plan = [(t, item, q) for t, item, q in plan if item != protected]
        added = 0
        if plan:
            market = [list(o) for o in (action.get("market") or [])]
            selling = _v27w_market_caps({"market": market})
            extra = []
            for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
                if item in picked or int(prices.get(item, 0)) < 2:
                    continue
                if not _v27w_near_peak(st, day, prices, item):
                    continue
                avail = _v27w_int(stock.get(item)) - selling.get(item, 0)
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
                _V27W_REPORT["adv_turns"] += 1
                _V27W_REPORT["adv_units"] += added
                action["market"] = extra + market
        if rolled or added:
            pass
        else:
            return action
    except Exception:
        _V27W_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27W_REPORT
# ===================== end v27.4 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    marker = "\n\n# ===================== v27.4 LAYER"
    if marker in base:
        base = base[: base.index(marker)] + "\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
