#!/usr/bin/env python3
"""T108 builder: v26i = v26c.py + HARVEST LEGION (own-chassis port).

v26c (v25.1 chassis) never hires farm hands and writes action["hands"] = []
-- the hands dimension is completely free.  This layer hires up to 4 hands
(fib cost, ~$1-8) from day 8 and OWNS the whole hands list: each hand runs
a greedy harvester program (walk to the best ripe tile yield>=2, HARVEST,
walk home, DROP only when the shed has room).  Never touches the farmer
command, never touches the chassis's market orders.
"""
import sys

SRC = "/home/z/my-project/kaggriculture/v26c.py"
OUT = "/home/z/my-project/kaggriculture/v26i.py"

CFG = dict(
    HIRE_FROM=8, MAX_EXTRA=4, MONEY_MIN=600, YIELD_MIN=2,
    CARRY_RETURN=4, LATE_DAY=28, LATE_DIST=5,
)

LAYER = '''

# ---------------------------------------------------------------------------
# t108 LEGION (v26i): the v25.1 chassis plans only the main farmer and posts
# hands: [] -- it never hires.  Late-game ripe backlogs of 90-110 units sit
# on plants (and ~32 rot at the end) because one farmer cannot keep up.
# This layer hires up to 4 hands (fib cost) and drives the full hands list
# with a greedy harvester: best ripe tile (yield>=2, score yield*price -
# 2*dist), walk, HARVEST (takes all sitting units), walk home, DROP only
# when the shed has room (the engine deletes undropped remainder).  The
# farmer command and the chassis's market orders are untouched.
# ---------------------------------------------------------------------------
T108_HIRE_FROM = {HIRE_FROM}
T108_MAX_EXTRA = {MAX_EXTRA}
T108_MONEY_MIN = {MONEY_MIN}
T108_YIELD_MIN = {YIELD_MIN}
T108_CARRY_RETURN = {CARRY_RETURN}
T108_LATE_DAY = {LATE_DAY}
T108_LATE_DIST = {LATE_DIST}
T108_SHED_TILES = ((4, 4), (5, 4), (4, 5), (5, 5))
_T108_REPORT = dict(t108_hires=0, t108_harvests=0, t108_drops=0,
                    t108_commands=0, t108_errors=0)
_T108_ST = {{}}


def _t108_dist(a, b):
    return abs(int(a[0]) - int(b[0])) + abs(int(a[1]) - int(b[1]))


def _t108_move(fx, fy, tx, ty):
    dx, dy = int(tx) - int(fx), int(ty) - int(fy)
    if abs(dx) >= abs(dy) and dx != 0:
        return ["EAST"] if dx > 0 else ["WEST"]
    if dy != 0:
        return ["SOUTH"] if dy > 0 else ["NORTH"]
    if dx != 0:
        return ["EAST"] if dx > 0 else ["WEST"]
    return ["PASS"]


def _t108_worker_command(pos, inv, farm, private, prices, day):
    px, py = int(pos[0]), int(pos[1])
    carried = sum(v for v in inv.values() if v and v > 0)
    shed_total = int(sum(private["shed"].values()))
    on_shed = (px, py) in T108_SHED_TILES
    if carried > 0 and (carried >= T108_CARRY_RETURN or on_shed):
        if on_shed:
            if shed_total + carried <= 100:
                return ["DROP"]
            return ["PASS"]
        home = min(T108_SHED_TILES, key=lambda t: _t108_dist((px, py), t))
        return _t108_move(px, py, home[0], home[1])
    best, best_score = None, -1
    grid = farm["tiles"]
    for y, row in enumerate(grid):
        for x, t in enumerate(row):
            if not isinstance(t, dict):
                continue
            yu = int(t.get("yield_units", 0) or 0)
            if yu < T108_YIELD_MIN:
                continue
            if t.get("kind") == "PLANT":
                item = t.get("crop")
            elif "animal" in t:
                item = {{"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}}.get(t["animal"])
            else:
                continue
            if item is None:
                continue
            d = _t108_dist((px, py), (x, y))
            if day >= T108_LATE_DAY and d > T108_LATE_DIST:
                continue
            score = yu * int(prices.get(item, 1) or 1) - 2 * d
            if score > best_score:
                best, best_score = (x, y), score
    if best is None:
        if carried > 0 and not on_shed:
            home = min(T108_SHED_TILES, key=lambda t: _t108_dist((px, py), t))
            if _t108_dist((px, py), home) <= 2:
                return _t108_move(px, py, home[0], home[1])
        return ["PASS"]
    if (px, py) == best:
        return ["HARVEST"]
    return _t108_move(px, py, best[0], best[1])


_T108_PARENT = agent
del agent


def agent(observation, configuration=None):
    player, step = int(observation["player"]), int(observation["step"])
    day = step // 24
    st = _T108_ST.get(player)
    if st is None or step <= st.get("step", -1):
        st = _T108_ST[player] = {{"step": -1, "hired": 0}}
        if step == 0:
            _T108_REPORT.update(t108_hires=0, t108_harvests=0, t108_drops=0,
                                t108_commands=0, t108_errors=0)
    st["step"] = step
    action = _T108_PARENT(observation, configuration)
    try:
        if not isinstance(action, dict):
            return action
        farm = observation["farms"][player]
        private = observation["private"]
        prices = observation["market"]["prices"]
        hands_count = len(farm.get("hands") or [])
        changed = False
        market = None
        if day >= T108_HIRE_FROM and st["hired"] < T108_MAX_EXTRA \\
                and st["hired"] < hands_count + 1 \\
                and int(farm["money"]) > T108_MONEY_MIN:
            m = [list(o) for o in (action.get("market") or [])]
            if len(m) < 10:
                m.append(["HIRE"])
                st["hired"] += 1
                _T108_REPORT["t108_hires"] += 1
                market = m
                changed = True
        hands = [list(c) if isinstance(c, list) else ["PASS"]
                 for c in (action.get("hands") or [])]
        while len(hands) < hands_count:
            hands.append(["PASS"])
        n_cmd = 0
        for idx in range(hands_count):
            if idx >= len(hands):
                break
            if hands[idx] != ["PASS"]:
                continue
            pos = (farm["hands"] or [None] * (idx + 1))[idx]
            if pos is None:
                continue
            invs = private.get("inventories") or []
            inv = invs[idx + 1] if idx + 1 < len(invs) else {{}}
            cmd = _t108_worker_command(pos, inv or {{}}, farm, private, prices, day)
            if cmd != ["PASS"]:
                hands[idx] = cmd
                n_cmd += 1
                if cmd == ["HARVEST"]:
                    _T108_REPORT["t108_harvests"] += 1
                elif cmd == ["DROP"]:
                    _T108_REPORT["t108_drops"] += 1
        _T108_REPORT["t108_commands"] += n_cmd
        if n_cmd or changed:
            action = dict(action)
            action["hands"] = hands
            if market is not None:
                action["market"] = market[:10]
        return action
    except Exception:
        _T108_REPORT["t108_errors"] += 1
        return action


agent.telemetry = _T108_REPORT
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
