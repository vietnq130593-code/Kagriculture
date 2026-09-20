#!/usr/bin/env python3
"""T103 builder: v26e = thomast2945.py + WHEAT CORNER layer (pure market-side).

The layer never touches farmer/hands commands; it only adds market orders:
- BUY window (day 0..7, price <= PMAX): buy wheat in chunks while money guard holds.
- SELL window (day 22..27, price >= PMIN): sell the held position, order INSERTED
  at the front of the market list so it commits before the tape's own sells
  drain the shared shed. Position = bought - sold (optimistic accounting,
  sells capped by actual shed contents).
"""
import sys

SRC = "/home/z/my-project/kaggriculture/thomast2945.py"
OUT = "/home/z/my-project/kaggriculture/v26e.py"

CFG = dict(
    N=40, BUY_D0=0, BUY_D1=7, BUY_PMAX=34, KEEP=600,
    SELL_D0=22, SELL_D1=27, SELL_PMIN=34, CHUNK=12,
)

LAYER = '''

# ---------------------------------------------------------------------------
# t103 WHEAT CORNER (v26e): buy the early wheat glut cheap, hold it off the
# market (the shared inventory is what sets the price -- every unit withheld
# lifts the quote for every later sale), then dump the position into the
# late d22-27 high-price window.  Pure market-side layer: farmer/hands
# commands are never touched, tape market orders are never removed -- the
# corner orders are appended (buys) or inserted at index 0 (sells, so they
# win the shared-shed race against the tape's own sell flow in the same
# step).  Money guard KEEP keeps the opening purchases funded.
# ---------------------------------------------------------------------------
T103_CORNER_N = {N}
T103_BUY_D0, T103_BUY_D1 = {BUY_D0}, {BUY_D1}
T103_BUY_PMAX = {BUY_PMAX}
T103_KEEP = {KEEP}
T103_SELL_D0, T103_SELL_D1 = {SELL_D0}, {SELL_D1}
T103_SELL_PMIN = {SELL_PMIN}
T103_CHUNK = {CHUNK}
_T103_REPORT = dict(t103_bought=0, t103_sold=0, t103_buys=0, t103_sells=0,
                    t103_errors=0)
_T103_ST = {{}}

_T103_PARENT = agent
del agent


def agent(observation, configuration=None):
    player, step = int(observation["player"]), int(observation["step"])
    day = step // 24
    st = _T103_ST.get(player)
    if st is None or step <= st.get("step", -1):
        st = _T103_ST[player] = {{"step": -1, "bought": 0, "sold": 0}}
        if step == 0:
            _T103_REPORT.update(t103_bought=0, t103_sold=0, t103_buys=0,
                                t103_sells=0, t103_errors=0)
    st["step"] = step
    action = _T103_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        market = [list(o) for o in (action.get("market") or [])]
        farm = observation["farms"][player]
        private = observation["private"]
        prices = observation["market"]["prices"]
        money = int(farm["money"])
        pos = st["bought"] - st["sold"]
        changed = False
        if T103_BUY_D0 <= day <= T103_BUY_D1 and pos < T103_CORNER_N:
            price = int(prices.get("WHEAT", 0) or 0)
            k = min(T103_CHUNK, T103_CORNER_N - pos)
            if 0 < price <= T103_BUY_PMAX and money >= price * k + T103_KEEP \\
                    and len(market) < 10:
                market.append(["BUY_PRODUCT", "WHEAT", k])
                st["bought"] += k
                _T103_REPORT["t103_buys"] += 1
                changed = True
        elif T103_SELL_D0 <= day <= T103_SELL_D1 and pos > 0:
            price = int(prices.get("WHEAT", 0) or 0)
            shed_w = int(private["shed"].get("WHEAT", 0) or 0)
            k = min(T103_CHUNK, pos, shed_w)
            if k > 0 and (price >= T103_SELL_PMIN or day >= T103_SELL_D1) \\
                    and len(market) < 10:
                market.insert(0, ["SELL", "WHEAT", k])
                st["sold"] += k
                _T103_REPORT["t103_sells"] += 1
                changed = True
        _T103_REPORT["t103_bought"] = st["bought"]
        _T103_REPORT["t103_sold"] = st["sold"]
        if changed:
            action = dict(action)
            action["market"] = market[:10]
        return action
    except Exception:
        _T103_REPORT["t103_errors"] += 1
        return action


agent.telemetry = _T103_REPORT
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
