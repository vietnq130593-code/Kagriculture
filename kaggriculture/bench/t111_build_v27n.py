#!/usr/bin/env python3
"""Task 111 FINAL: build v27.2 = v27 + race-mode refinements.

Base: v27.py (2945 chassis byte-exact + v27 dual-mode layer).

Modifications (all RACE MODE only — clone mode byte-identical to v27):
1. v27 layer race-mode crash-dump: ratio 0.95 -> 0.92, plus a deep-crash
   filter for late fires (day > 23: only fire when p <= 0.30 x 4-day peak
   — slow bleeds bounce at the endgame; terminal collapses keep falling).
2. New outermost v27.2 layer with four coupled reflexes:
   (a) near-peak sale-advance (dribbles, horizon 14, near 6-day max)
   (b) peak-rollover full-shed dump (break from the 6-day ceiling)
   (c) endgame trough-hold (d22+: p < 0.07 x all-game peak -> hold)
   (d) endgame hold-until-recovery (d27-29: hold below 1.6x day-open,
       dump the whole shed at the recovered price)

Writes kaggriculture/v27n.py.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27n.py")

RACE_PATCH_OLD = """        if is_clone is False:
            # RACE MODE: non-clone opponent (V48-class front-runners). No MILK
            # (their market-making harvests milk dump troughs), earlier window,
            # more sensitive ratio to pre-empt their look-ahead sale races.
            if day < 12:
                return action
            dumpable = ("STRAWBERRY", "WOOL", "MELON", "EGG", "CARROT", "TOMATO")
            ratio = 0.95
        else:
            if day < _V27_MIN_DAY:
                return action
            dumpable = _V27_DUMPABLE
            ratio = _V27_CRASH_RATIO
        prices = {}
        try:
            prices = dict(obs["market"]["prices"] or {})
        except Exception:
            return action
        crashing = _v27_crashing(st, day, prices, dumpable, ratio)
        if not crashing:
            return action"""

RACE_PATCH_NEW = """        if is_clone is False:
            # RACE MODE: non-clone opponent (V48-class front-runners). No MILK
            # (their market-making harvests milk dump troughs), earlier window,
            # more sensitive ratio to pre-empt their look-ahead sale races.
            # Task 111: ratio 0.95 -> 0.92 (alperen1 s100 -430 -> +445/seat).
            if day < 12:
                return action
            dumpable = ("STRAWBERRY", "WOOL", "MELON", "EGG", "CARROT", "TOMATO")
            ratio = 0.92
        else:
            if day < _V27_MIN_DAY:
                return action
            dumpable = _V27_DUMPABLE
            ratio = _V27_CRASH_RATIO
        prices = {}
        try:
            prices = dict(obs["market"]["prices"] or {})
        except Exception:
            return action
        crashing = _v27_crashing(st, day, prices, dumpable, ratio)
        if day > 23 and is_clone is False:
            # Task 111 deep-crash filter: late fires only for terminal
            # collapses (p <= 0.30 x 4-day ceiling); slow bleeds bounce.
            days_ = st["days"]
            for item_ in list(crashing):
                peak4_ = 0.0
                for d4_ in range(day - 1, day - 5, -1):
                    if d4_ in days_:
                        v4_ = days_[d4_].get(item_)
                        if v4_ is not None and v4_ > peak4_:
                            peak4_ = v4_
                p_now_ = prices.get(item_)
                if peak4_ <= 0 or p_now_ is None or p_now_ > 0.30 * peak4_:
                    crashing.discard(item_)
        if not crashing:
            return action"""

LAYER = '''

# ===================== v27.2 LAYER — RACE-PEAK + ENDGAME RECOVERY =====================
# Task 111 (2026-09-19): v27.2 "RACE-PEAK ENDGAME GENERAL" (race mode only).
# Base = v27 dual-mode crash-dump agent (2945 chassis byte-exact below; the
# v27 layer's race-mode dump is retuned: ratio 0.92 + deep-crash filter for
# late fires). This outermost wrapper adds four coupled reflexes:
#
#  (a) NEAR-PEAK SALE-ADVANCE — when the tape plans a SELL of a pure cash
#      product within 14 steps, the units sit in the shed, and the price is
#      at/near its 6-day max (>= 0.95 x), sell them now (mechanism after
#      the public sdy623/jaxa623 "Beyond 48-0" EXP293 sale-advance family;
#      alperen5252525 "First in Line" / tetsutani v65 horizon-14 racers).
#  (b) PEAK-ROLLOVER DUMP — when yesterday's opening was at/near the item's
#      6-day ceiling (>= 0.98 x) and the current price broke >= 3% below it,
#      dump the shed: structural intraday breaks (MELON 271->131, WOOL
#      154->1, STRAWBERRY 207->32) are invisible to the crash-dump until a
#      day late.
#  (c) ENDGAME TROUGH-HOLD — from day 22, an item that was once valuable
#      (all-game peak >= 50) now dead (p < 0.07 x all-game peak) is HELD
#      (its dribble sells zeroed, capacity-guarded) to ride the endgame
#      bounce (measured: WOOL 1 -> 61/88/93).
#  (d) ENDGAME HOLD-UNTIL-RECOVERY — days 27-29: the tape dribbles into the
#      flush-day troughs while the price recovers intraday (d28 STRAWBERRY
#      28 -> 70 -> 37); hold everything below 1.6 x the day-open and dump
#      the whole shed at the recovered price, racing the opponent's
#      flush-race to the top.
#
# Clone mode stays completely silent (measured perturbation loss vs the
# mirror: s102 -2258, s104 -1924 in the unconditional variant).
# Guards from the v25.1 port: never on the dawn turn, never when this step
# buys products, the first-listed sale of the next turn is left alone,
# quantities are caps (the tape's later SELL sells whatever arrives),
# terminal flush orders (cap >= 500) are never touched.
_V27N_PARENT = agent
globals().pop("agent", None)

_V27N_LOOK = 14
_V27N_FROM = 144
_V27N_TO = 710
_V27N_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MILK", "MELON", "CARROT", "TOMATO")
_V27N_PROTECT = True
_V27N_PEAK_RATIO = 0.95
_V27N_PEAK_LOOKBACK = 6
_V27N_ROLL_CEIL = 0.98
_V27N_ROLL_BREAK = 0.97
_V27N_ROLL_MIN = 3
_V27N_RECOVERY = 1.6
_V27N_STATE = {}
_V27N_REPORT = {"adv_turns": 0, "adv_units": 0, "roll_turns": 0,
                "roll_units": 0, "hold_turns": 0, "recovery_turns": 0,
                "adv_errors": 0}


def _v27n_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27n_note_day(state, obs):
    day = _v27n_int(obs.get("day"))
    seat = _v27n_int(obs.get("player"))
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


def _v27n_race_mode(seat, day):
    try:
        st = _V27_STATE.get(seat)
        if not st:
            return False
        if day < 9:
            return False
        return st.get("clone") is False
    except Exception:
        return False


def _v27n_ceiling(st, day, item):
    days = st["days"]
    peak = 0.0
    seen = 0
    for d in range(day - 1, day - 1 - _V27N_PEAK_LOOKBACK, -1):
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


def _v27n_near_peak(st, day, prices, item):
    peak, _, seen = _v27n_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or seen < 2:
        return False
    return p >= _V27N_PEAK_RATIO * peak


def _v27n_rollover(st, day, prices, item):
    peak, yest, seen = _v27n_ceiling(st, day, item)
    p = prices.get(item)
    if p is None or yest is None or seen < 2 or peak <= 0:
        return False
    if yest < _V27N_ROLL_CEIL * peak:
        return False
    return p <= _V27N_ROLL_BREAK * yest


def _v27n_future(seat, t):
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


def _v27n_market_caps(action):
    caps = {}
    for o in action.get("market") or []:
        if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
            try:
                caps[o[1]] = caps.get(o[1], 0) + max(0, int(o[2]))
            except Exception:
                pass
    return caps


def _v27n_add_sell(action, item, qty):
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
                o[2] = max(_v27n_int(o[2]), qty + 50)
            except Exception:
                pass
            return True
    if len(market) >= 10:
        return False
    market.append(["SELL", item, qty + 50])
    return True


def agent(observation, configuration=None):
    action = _V27N_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27n_int(obs.get("step"))
        seat = _v27n_int(obs.get("player"))
        day = _v27n_int(obs.get("day"))
        if step % 24 == 23 or not (_V27N_FROM <= step < 718):
            return action
        if not _v27n_race_mode(seat, day):
            return action  # clone mode: stay silent
        st = _v27n_note_day(_V27N_STATE, obs)
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
        total_shed = sum(_v27n_int(v) for v in stock.values())
        held = False

        # ---- (d) endgame hold-until-recovery (days 27-29, race the flush V) ----
        if day >= 27 and step < 710:
            day_open = st.setdefault("day_open", {})
            if step % 24 == 0:
                for _it in _V27N_ITEMS:
                    if prices.get(_it) is not None:
                        day_open[_it] = float(prices[_it])
                st["dumped_today"] = set()
            dumped_today = st.setdefault("dumped_today", set())
            for item in _V27N_ITEMS:
                p_e = prices.get(item)
                o_open = day_open.get(item, 0.0)
                if p_e is None or o_open <= 0 or item in dumped_today:
                    continue
                if p_e >= _V27N_RECOVERY * o_open:
                    caps_e = _v27n_market_caps(action)
                    avail_e = _v27n_int(stock.get(item)) - caps_e.get(item, 0)
                    if avail_e >= 1 and _v27n_add_sell(action, item, avail_e):
                        dumped_today.add(item)
                        _V27N_REPORT["recovery_turns"] += 1
                elif _v27n_int(stock.get(item)) < 50 and total_shed < 80:
                    for o in market:
                        if (isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
                                and o[1] == item and _v27n_int(o[2]) < 500):
                            o[2] = 0
                            held = True
            if held:
                action["market"] = market
                _V27N_REPORT["hold_turns"] += 1
            if day >= 27:
                return action  # endgame zone: (a)-(c) silent

        # ---- (c) endgame trough-hold (day >= 22: ride the bounce) ----
        allpeak = st.setdefault("allpeak", {})
        for _it in _V27N_ITEMS:
            _pt = prices.get(_it)
            if _pt is not None:
                allpeak[_it] = max(allpeak.get(_it, 0.0), float(_pt))
        if day >= 22:
            for item in _V27N_ITEMS:
                p_t = prices.get(item)
                if p_t is None:
                    continue
                ap = allpeak.get(item, 0.0)
                if ap < 50 or p_t >= 0.07 * ap:
                    continue  # only items that were valuable once, now dead
                if _v27n_int(stock.get(item)) >= 15 or total_shed >= 30:
                    continue
                for o in market:
                    if (isinstance(o, list) and len(o) >= 3 and o[0] == "SELL"
                            and o[1] == item and _v27n_int(o[2]) < 500):
                        o[2] = 0
                        held = True
            if held:
                action["market"] = market
                _V27N_REPORT["hold_turns"] += 1

        # ---- (b) peak-rollover dump (paced) ----
        rolled = False
        for item in _V27N_ITEMS:
            if item in picked:
                continue
            p = prices.get(item)
            if p is None or int(p) < 2:
                continue
            if not _v27n_rollover(st, day, prices, item):
                continue
            caps = _v27n_market_caps(action)
            avail = _v27n_int(stock.get(item)) - caps.get(item, 0)
            if avail < _V27N_ROLL_MIN:
                continue
            if _v27n_add_sell(action, item, min(avail, 6)):
                rolled = True
                _V27N_REPORT["roll_turns"] += 1
                _V27N_REPORT["roll_units"] += min(avail, 6)

        # ---- (a) near-peak sale-advance (dribbles) ----
        plan = []
        first = None
        for off in range(1, _V27N_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27n_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27N_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27N_PROTECT and first is not None and first[0] == "SELL" else None
        plan = [(t, item, q) for t, item, q in plan if item != protected]
        added = 0
        if plan:
            market2 = [list(o) for o in (action.get("market") or [])]
            selling = _v27n_market_caps({"market": market2})
            extra = []
            for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
                if item in picked or int(prices.get(item, 0)) < 2:
                    continue
                if not _v27n_near_peak(st, day, prices, item):
                    continue
                avail = _v27n_int(stock.get(item)) - selling.get(item, 0)
                if avail < 1:
                    continue
                hit = next((o for o in market2 if len(o) >= 3 and o[0] == "SELL" and o[1] == item), None)
                if hit is None and len(market2) + len(extra) >= 10:
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
                _V27N_REPORT["adv_turns"] += 1
                _V27N_REPORT["adv_units"] += added
                action["market"] = extra + market2
        if not (rolled or added or held):
            return action
    except Exception:
        _V27N_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27N_REPORT
# ===================== end v27.2 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    assert RACE_PATCH_OLD in base, "v27 race-mode block not found"
    base = base.replace(RACE_PATCH_OLD, RACE_PATCH_NEW)
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
