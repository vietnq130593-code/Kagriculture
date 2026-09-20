#!/usr/bin/env python3
"""T107 builder: v26h = thomast2945.py + HARVEST LEGION layer.

Hires up to 3 extra farm hands (hire cost is fib-scaling, ~$1-3 late game),
then drives them by REPLACING the trailing ["PASS"] entries the tape's own
hand_align layer pads in for unknown hands.  Program per worker:
  - carrying stock -> walk to nearest shed tile, DROP only if shed has room
    (the engine DESTROYS un-dropped remainder, so room is checked first);
  - else -> walk to the best ripe tile (yield>=3, score = yield*price - 2*dist)
    and HARVEST it (takes all sitting units; ongoing plants survive).
Never touches the tape's own commands or market orders (HIRE is appended to
the market list only when a slot is free; sells are left to the tape's own
flush machinery).
"""
import sys

SRC = "/home/z/my-project/kaggriculture/thomast2945.py"
OUT = "/home/z/my-project/kaggriculture/v26h.py"

CFG = dict(
    HIRE_FROM=12, MAX_EXTRA=3, MONEY_MIN=400, YIELD_MIN=3,
    CARRY_RETURN=4, LATE_DAY=28, LATE_DIST=5,
)

LAYER = '''

# ---------------------------------------------------------------------------
# t107 HARVEST LEGION (v26h): the tape ends games with ripe yield still
# sitting on plants (39+ units on s100 d29) and mid-game backlogs of 76-112
# units because 12 workers cannot keep up.  This layer hires up to 3 extra
# hands (fib cost ~$1-3 after the tape's own hiring window) and drives them
# through the trailing ["PASS"] slots the tape's hand_align pads for unknown
# hands.  Extra hands harvest the sitting yield, carry it to the shed (DROP
# only when there is room -- the engine deletes undropped remainder), and
# the tape's own sell/flush machinery monetises the stock.  The tape's own
# commands and market orders are never modified.
# ---------------------------------------------------------------------------
T107_HIRE_FROM = {HIRE_FROM}
T107_MAX_EXTRA = {MAX_EXTRA}
T107_MONEY_MIN = {MONEY_MIN}
T107_YIELD_MIN = {YIELD_MIN}
T107_CARRY_RETURN = {CARRY_RETURN}
T107_LATE_DAY = {LATE_DAY}
T107_LATE_DIST = {LATE_DIST}
T107_SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))
_T107_REPORT = dict(t107_hires=0, t107_harvests=0, t107_drops=0,
                    t107_commands=0, t107_errors=0)
_T107_ST = {{}}


def _t107_dist(a, b):
    return abs(int(a[0]) - int(b[0])) + abs(int(a[1]) - int(b[1]))


def _t107_move(fx, fy, tx, ty):
    dx, dy = int(tx) - int(fx), int(ty) - int(fy)
    if abs(dx) >= abs(dy) and dx != 0:
        return ["EAST"] if dx > 0 else ["WEST"]
    if dy != 0:
        return ["SOUTH"] if dy > 0 else ["NORTH"]
    if dx != 0:
        return ["EAST"] if dx > 0 else ["WEST"]
    return ["PASS"]


def _t107_worker_command(pos, inv, farm, private, prices, day):
    px, py = int(pos[0]), int(pos[1])
    carried = sum(v for v in inv.values() if v and v > 0)
    shed_total = int(sum(private["shed"].values()))
    on_shed = (px, py) in T107_SHED_TILES
    if carried > 0 and (carried >= T107_CARRY_RETURN or on_shed):
        if on_shed:
            if shed_total + carried <= 100:
                return ["DROP"]
            return ["PASS"]
        home = min(T107_SHED_TILES, key=lambda t: _t107_dist((px, py), t))
        return _t107_move(px, py, home[0], home[1])
    best, best_score = None, -1
    grid = farm["tiles"]
    for y, row in enumerate(grid):
        for x, t in enumerate(row):
            if not isinstance(t, dict):
                continue
            yu = int(t.get("yield_units", 0) or 0)
            if yu < T107_YIELD_MIN:
                continue
            if t.get("kind") == "PLANT":
                item = t.get("crop")
            elif "animal" in t:
                item = {{"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}}.get(t["animal"])
            else:
                continue
            if item is None:
                continue
            d = _t107_dist((px, py), (x, y))
            if day >= T107_LATE_DAY and d > T107_LATE_DIST:
                continue
            score = yu * int(prices.get(item, 1) or 1) - 2 * d
            if score > best_score:
                best, best_score = (x, y), score
    if best is None:
        if carried > 0 and not on_shed:
            home = min(T107_SHED_TILES, key=lambda t: _t107_dist((px, py), t))
            if _t107_dist((px, py), home) <= 2:
                return _t107_move(px, py, home[0], home[1])
        return ["PASS"]
    if (px, py) == best:
        return ["HARVEST"]
    return _t107_move(px, py, best[0], best[1])


_T107_PARENT = agent
del agent


def agent(observation, configuration=None):
    player, step = int(observation["player"]), int(observation["step"])
    day = step // 24
    st = _T107_ST.get(player)
    if st is None or step <= st.get("step", -1):
        st = _T107_ST[player] = {{"step": -1, "hired": 0}}
        if step == 0:
            _T107_REPORT.update(t107_hires=0, t107_harvests=0, t107_drops=0,
                                t107_commands=0, t107_errors=0)
    st["step"] = step
    action = _T107_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        farm = observation["farms"][player]
        private = observation["private"]
        prices = observation["market"]["prices"]
        hands_count = len(farm.get("hands") or [])
        changed = False
        market = None
        if day >= T107_HIRE_FROM and st["hired"] < T107_MAX_EXTRA \\
                and int(farm["money"]) > T107_MONEY_MIN:
            m = [list(o) for o in (action.get("market") or [])]
            if len(m) < 10:
                m.append(["HIRE"])
                st["hired"] += 1
                _T107_REPORT["t107_hires"] += 1
                market = m
                changed = True
        hands = [list(c) if isinstance(c, list) else ["PASS"]
                 for c in (action.get("hands") or [])]
        n_cmd = 0
        for w in range(st["hired"]):
            idx = hands_count - 1 - w   # last hand index (0-based in hands list)
            if idx < 0 or idx >= len(hands):
                continue
            if hands[idx] != ["PASS"]:
                continue
            pos = (farm["hands"] or [None] * (idx + 1))[idx]
            if pos is None:
                continue
            inv = (private.get("inventories") or [])[idx + 1] \\
                if idx + 1 < len(private.get("inventories") or []) else {{}}
            cmd = _t107_worker_command(pos, inv or {{}}, farm, private, prices, day)
            if cmd != ["PASS"]:
                hands[idx] = cmd
                n_cmd += 1
                if cmd == ["HARVEST"]:
                    _T107_REPORT["t107_harvests"] += 1
                elif cmd == ["DROP"]:
                    _T107_REPORT["t107_drops"] += 1
        _T107_REPORT["t107_commands"] += n_cmd
        if n_cmd or changed:
            action = dict(action)
            action["hands"] = hands
            if market is not None:
                action["market"] = market[:10]
        return action
    except Exception:
        _T107_REPORT["t107_errors"] += 1
        return action


agent.telemetry = _T107_REPORT
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
