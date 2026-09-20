#!/usr/bin/env python3
"""Task 110: build v27a = thomast2945 + CRASH-DUMP ACCELERATOR.

Chassis: thomast2945.py byte-exact (the 2944.7-ladder notebook bot).
Patch: outermost wrapper (production-loader safe: `agent` re-defined last).
Logic: track daily price history per seat; when a pure-output product
(MILK/STRAWBERRY/MELON/WOOL/EGG/CARROT/TOMATO) is in a structural crash
(yesterday <= 88% of the 4-day peak AND price not recovering), dump the
whole shed inventory of it immediately (extend the tape's own sell order
if present, else append SELL <qty+50>).

WHEAT and FERTILIZER are EXCLUDED: they are inputs to the chassis' own
machinery (feed / fertilize / support machine round-trips).

Usage: python3 bench/t110_build_v27a.py [out] [mode]
  mode = base (default) -> crash-dump accelerator only
"""
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "thomast2945.py")

TAIL = '''

# ===================== v27 LAYER — CRASH-DUMP ACCELERATOR =====================
# Task 110 (2026-09-19): v27a. Base chassis = the 2945 farm (byte-exact).
# This layer only accelerates the sale of pure-output products during
# structural price crashes so the co-op tape's paced trickle does not donate
# the declining tail of the price curve to the opponent's identical tape.
# It never touches WHEAT / FERTILIZER (internal inputs), never buys, and
# never changes unit actions — market sell orders only.
_v27_parent = agent
globals().pop("agent", None)

_V27_STATE = {}
_V27_DUMPABLE = ("MILK", "STRAWBERRY", "MELON", "WOOL", "EGG", "CARROT", "TOMATO")
_V27_PEAK_LOOKBACK = 4
_V27_CRASH_RATIO = 0.88
_V27_MIN_DAY = 9


def _v27_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _v27_note_day(state, obs):
    day = _v27_int(obs.get("day"))
    seat = _v27_int(obs.get("player"))
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


def _v27_crashing(st, day, prices):
    days = st["days"]
    hist = [days[d] for d in range(day - 1, day - 1 - _V27_PEAK_LOOKBACK, -1) if d in days]
    if len(hist) < 3:
        return set()
    out = set()
    for item in _V27_DUMPABLE:
        p = prices.get(item)
        if p is None:
            continue
        peak = 0.0
        for h in hist:
            v = h.get(item)
            if v is not None and v > peak:
                peak = v
        if peak <= 0:
            continue
        yest = hist[0].get(item, p)
        if yest <= _V27_CRASH_RATIO * peak and p <= yest * 1.02:
            out.add(item)
    return out


def agent(observation, configuration=None):
    action = _v27_parent(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        obs = observation
        day = _v27_int(obs.get("day"))
        if day < _V27_MIN_DAY:
            return action
        st = _v27_note_day(_V27_STATE, obs)
        prices = {}
        try:
            prices = dict(obs["market"]["prices"] or {})
        except Exception:
            return action
        crashing = _v27_crashing(st, day, prices)
        if not crashing:
            return action
        shed = {}
        try:
            shed = dict(obs["private"]["shed"] or {})
        except Exception:
            shed = {}
        if not shed:
            return action
        market = action.get("market")
        if market is None:
            market = []
            action["market"] = market
        elif not isinstance(market, list):
            return action
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
                        o[2] = max(_v27_int(o[2]), have + 50)
                    except Exception:
                        pass
                    extended = True
                    break
            if not extended and len(market) < 10:
                market.append(["SELL", item, have + 50])
    except Exception:
        pass
    return action
# ===================== end v27 layer =====================
'''


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "v27a.py")
    src = open(SRC, "r").read()
    if not src.endswith("\n"):
        src += "\n"
    open(out, "w").write(src + TAIL)
    print("wrote", out, len(src) + len(TAIL), "bytes")

    # loader verification (kaggle server semantics)
    import types
    g = {}
    exec(compile(src + TAIL, out, "exec"), g)
    callables = [(k, v) for k, v in g.items() if callable(v)]
    last = callables[-1]
    print("last callable:", last[0], "argcount:", last[1].__code__.co_argcount)
    import inspect
    sig = inspect.signature(last[1])
    print("signature ok")


if __name__ == "__main__":
    main()
