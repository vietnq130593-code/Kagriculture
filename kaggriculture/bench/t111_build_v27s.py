#!/usr/bin/env python3
"""Task 111: build v27s = v27 + SALE-ADVANCE RACER layer (outermost).

Port of the public sdy623/jaxa623 "Beyond 48-0" EXP293 sale-advance family
(alperen5252525 "First in Line" _ADV_LOOK=14 / tetsutani v65 horizon-14),
adapted from the v25.1 implementation in this repo to the 2945 chassis:

  * future tape lookup honours the 2945 router (route locked at step 144 by
    shop combo, hard switch to route 2 at step 648);
  * projected shed via the chassis' own _projected_shed (FarmView wrapper);
  * dawn-turn guard, BUY_PRODUCT guard, first-sale-of-next-turn protection,
    pure cash products only (never WHEAT/FERTILIZER — chassis inputs);
  * frontload: extra SELLs prepended so they win the shared price race.

Writes kaggriculture/v27s.py (v27.py + appended layer).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "v27.py")
DST = os.path.join(ROOT, "v27s.py")

LAYER = '''

# ===================== v27.1 LAYER — SALE-ADVANCE RACER =====================
# Task 111 (2026-09-19): v27s "FRONT-LINE PRICE GENERAL".
# Base = v27 dual-mode crash-dump agent (2945 chassis byte-exact below).
#
# Added reflex #3 — SALE-ADVANCE RACER (outermost wrapper): when the 2945
# tape plans a SELL of a pure cash product within the next 14 steps and the
# units already sit in the shed, sell them NOW. In a shared market whose
# prices decay with cumulative sales, every step a planned sale waits is a
# donation of the price tail to whoever sells first (mechanism after the
# public sdy623/jaxa623 "Beyond 48-0" EXP293; horizon-14 parity with
# alperen5252525 "First in Line" and tetsutani v65 — the exact racers our
# old line v25/v251/v26 used to win seeds 100/101).
#
# Guards carried over from the v25.1 port: never on the dawn turn (the
# warehouse-closing layer inspects the shed there), never when this step
# buys products (feed-credit timing), the first-listed sale of the next
# turn is left alone, quantities are caps so the tape's own later SELL
# simply sells whatever was deposited since, and the market list keeps
# sales first (frontload) so the early orders win the race slots.
_V27S_PARENT = agent
globals().pop("agent", None)

_V27S_LOOK = 14
_V27S_FROM = 144
_V27S_TO = 718
_V27S_ITEMS = ("STRAWBERRY", "WOOL", "EGG", "MILK", "MELON", "CARROT", "TOMATO")
_V27S_PROTECT = True
_V27S_REPORT = {"adv_turns": 0, "adv_units": 0, "adv_errors": 0}


def _v27s_future(seat, t):
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
    action = _V27S_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        step = _v27_int(obs.get("step"))
        seat = _v27_int(obs.get("player"))
        if step % 24 == 23 or not (_V27S_FROM <= step < _V27S_TO):
            return action
        plan = []
        first = None
        for off in range(1, _V27S_LOOK + 1):
            t = step + off
            if t > 718:
                break
            for o in _v27s_future(seat, t):
                if not o or len(o) < 3:
                    continue
                if first is None:
                    first = o
                if o[0] == "SELL" and o[1] in _V27S_ITEMS:
                    try:
                        q = max(0, int(o[2]))
                    except Exception:
                        q = 0
                    if q > 0:
                        plan.append((t, o[1], q))
        protected = first[1] if _V27S_PROTECT and first is not None and first[0] == "SELL" else None
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
        try:
            prices = obs["market"]["prices"]
        except Exception:
            return action
        extra = []
        added = 0
        for item in sorted({it for _, it, _ in plan}, key=lambda it: -int(prices.get(it, 0))):
            if item in picked or int(prices.get(item, 0)) < 2:
                continue
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
        if not added:
            return action
        _V27S_REPORT["adv_turns"] += 1
        _V27S_REPORT["adv_units"] += added
        action["market"] = extra + market
    except Exception:
        _V27S_REPORT["adv_errors"] += 1
    return action
agent.telemetry = _V27S_REPORT
# ===================== end v27.1 layer =====================
'''


def main():
    with open(SRC, "r", encoding="utf-8") as f:
        base = f.read()
    # strip any previous v27.1 layer (idempotent rebuild)
    marker = "\n\n# ===================== v27.1 LAYER"
    if marker in base:
        base = base[: base.index(marker)] + "\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(base + LAYER)
    print("wrote", DST, os.path.getsize(DST), "bytes")


if __name__ == "__main__":
    main()
