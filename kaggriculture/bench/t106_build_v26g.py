#!/usr/bin/env python3
"""T106 builder: v26g = thomast2945.py + WHEAT SWING TRADER layer.

Pure market-side layer; never touches farmer/hands commands or the tape's own
market orders.  After day 10 (fat cash, maker active) it band-trades the
intraday wheat oscillation the chassis's own support machine creates:
- BUY trigger: observed wheat price <= rolling-min + edge  (dip steps)
- SELL trigger: observed price >= rolling-max - edge       (post-buy spikes)
Orders are inserted at index 0 so they commit at the best quotes of each
step's lockstep window.  Position capped, chunked, cash-guarded, shed-guarded.
Net gap effect = the layer's own trading P&L (opponent pays identical
friction through its identical tape, so frictions cancel in the gap).
"""
import sys

SRC = "/home/z/my-project/kaggriculture/thomast2945.py"
OUT = "/home/z/my-project/kaggriculture/v26g.py"

CFG = dict(
    START_DAY=10, WINDOW=48, BAND=3, BUY_EDGE=1, SELL_EDGE=1,
    MAX_POS=18, CHUNK=12, KEEP=3000,
)

LAYER = '''

# ---------------------------------------------------------------------------
# t106 WHEAT SWING (v26g): band-trade the intraday wheat oscillation that the
# chassis's support machine itself creates (its 48-96-unit buy/sell ping-pong
# swings the shared inventory ~100 units, i.e. ~$3 of price, every few steps).
# Buys commit at the dip quotes, sells at the post-buy spike quotes; both
# orders inserted at index 0 of the market list so they take the front of
# each lockstep window.  Never touches commands or the tape's own orders.
# ---------------------------------------------------------------------------
T106_START_DAY = {START_DAY}
T106_WINDOW = {WINDOW}
T106_BAND = {BAND}
T106_BUY_EDGE = {BUY_EDGE}
T106_SELL_EDGE = {SELL_EDGE}
T106_MAX_POS = {MAX_POS}
T106_CHUNK = {CHUNK}
T106_KEEP = {KEEP}
_T106_REPORT = dict(t106_buys=0, t106_units_bought=0, t106_sells=0,
                    t106_units_sold=0, t106_errors=0)
_T106_ST = {{}}

_T106_PARENT = agent
del agent


def agent(observation, configuration=None):
    player, step = int(observation["player"]), int(observation["step"])
    day = step // 24
    st = _T106_ST.get(player)
    if st is None or step <= st.get("step", -1):
        st = _T106_ST[player] = {{"step": -1, "pos": 0, "hist": []}}
        if step == 0:
            _T106_REPORT.update(t106_buys=0, t106_units_bought=0, t106_sells=0,
                                t106_units_sold=0, t106_errors=0)
    st["step"] = step
    action = _T106_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict) or day < T106_START_DAY:
            return action
        market = [list(o) for o in (action.get("market") or [])]
        farm = observation["farms"][player]
        private = observation["private"]
        prices = observation["market"]["prices"]
        p = int(prices.get("WHEAT", 0) or 0)
        hist = st["hist"]
        hist.append(p)
        if len(hist) > T106_WINDOW:
            del hist[: len(hist) - T106_WINDOW]
        if len(hist) < 12:
            return action
        lo, hi = min(hist), max(hist)
        pos = st["pos"]
        changed = False
        if hi - lo >= T106_BAND:
            money = int(farm["money"])
            shed_total = int(sum(private["shed"].values()))
            if p <= lo + T106_BUY_EDGE and pos < T106_MAX_POS \\
                    and money >= p * T106_CHUNK + T106_KEEP \\
                    and shed_total + T106_CHUNK <= 100 and len(market) < 10:
                k = min(T106_CHUNK, T106_MAX_POS - pos)
                market.insert(0, ["BUY_PRODUCT", "WHEAT", k])
                st["pos"] = pos + k
                _T106_REPORT["t106_buys"] += 1
                _T106_REPORT["t106_units_bought"] += k
                changed = True
            elif p >= hi - T106_SELL_EDGE and pos > 0 and len(market) < 10:
                shed_w = int(private["shed"].get("WHEAT", 0) or 0)
                k = min(T106_CHUNK, pos, shed_w)
                if k > 0:
                    market.insert(0, ["SELL", "WHEAT", k])
                    st["pos"] = pos - k
                    _T106_REPORT["t106_sells"] += 1
                    _T106_REPORT["t106_units_sold"] += k
                    changed = True
        if changed:
            action = dict(action)
            action["market"] = market[:10]
        return action
    except Exception:
        _T106_REPORT["t106_errors"] += 1
        return action


agent.telemetry = _T106_REPORT
agent = globals().pop('agent')
'''.format(**CFG)


def main():
    src = open(SRC).read()
    out = src + LAYER
    open(OUT, "w").write(out)
    import ast
    ast.parse(out)
    ns = {"__name__": "x"}
    exec(compile(out, OUT, "exec"), ns)
    a = ns["agent"]
    assert callable(a) and a.__code__.co_argcount == 2
    print(f"built {OUT}: {len(out)} bytes, agent argcount {a.__code__.co_argcount}")


if __name__ == "__main__":
    main()
