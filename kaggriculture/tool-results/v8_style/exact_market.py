#!/usr/bin/env python3
"""Exact re-simulation of kaggriculture _process_market for revenue attribution.

Replays both players' order queues per turn with the engine's per-unit
lockstep + interleaving, tracking per-order revenue/cost. Verifies against
logged money deltas (must be exact).

Convention (empirically verified on M1):
  kaggle row t: obs(t) is the state PRODUCED by action(t) (action ran at
    engine step t-1 on obs(t-1)). action(0)=PASS.
  arena  turn t: pre-action(t) state + acts for step t -> run on turn t.
"""
import sys
import json

sys.path.insert(0, "/home/z/my-project/kaggriculture")
from v8 import ANIMALS, CROPS, LAND_PRICES, _price, _fib  # noqa

PRICE_FLOOR = 1
NO_CAP = True  # trust SELL orders (shed snapshot is stale: units collect within the same turn)
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
ANIMAL_ITEMS = list(ANIMALS)


def _quote_price(item, inventory):
    return max(PRICE_FLOOR, int(round(_price(item, inventory))))


def _parse_order(order):
    if not isinstance(order, list) or not order:
        return None
    op = order[0]
    if op in ("HIRE", "BUY_LAND"):
        return {"type": op, "done": 0, "d": 0.0}
    if op in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL") and len(order) >= 3:
        try:
            n = int(order[2])
        except (TypeError, ValueError):
            return None
        if n <= 0:
            return None
        return {"type": op, "item": order[1], "remaining": n, "done": 0, "d": 0.0}
    return None


def sim_market(inv, money, sheds, hires, uqs, acts):
    """One engine step of _process_market for both players (money attribution).

    Returns attr[p] = list of dicts {op, item, n_req, n_done, d} (d = money delta).
    mutates copies passed in — caller passes copies.
    """
    queues = []
    for p in (0, 1):
        a = acts[p] if isinstance(acts[p], dict) else {}
        m = a.get("market", []) if isinstance(a, dict) else []
        q = list(m) if isinstance(m, list) else []
        queues.append(q[:10])
    attr = [[], []]
    order_objs = [[_parse_order(q[i]) if i < len(q) else None for i in range(len(q))]
                  for q in queues]
    max_len = max((len(q) for q in queues), default=0)
    for i in range(max_len):
        order_states = [order_objs[p][i] if i < len(order_objs[p]) else None for p in (0, 1)]
        for p in (0, 1):
            ostate = order_states[p]
            if ostate is None:
                continue
            if ostate["type"] == "HIRE":
                cost = _fib(hires[p])
                if money[p] >= cost:
                    money[p] -= cost
                    hires[p] += 1
                    ostate["done"] = 1
                    ostate["d"] = -cost
                order_states[p] = None
            elif ostate["type"] == "BUY_LAND":
                if 0 <= uqs[p] < len(LAND_PRICES):
                    cost = LAND_PRICES[uqs[p]]
                    if money[p] >= cost:
                        money[p] -= cost
                        uqs[p] += 1
                        ostate["done"] = 1
                        ostate["d"] = -cost
                order_states[p] = None
        while True:
            quoted = [None, None]
            for p in (0, 1):
                ostate = order_states[p]
                if ostate is None or ostate["remaining"] <= 0:
                    continue
                op, item = ostate["type"], ostate.get("item")
                if op == "SELL" and item in PRODUCTS:
                    quoted[p] = ("SELL", item, _quote_price(item, inv[item]), ostate)
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    quoted[p] = ("BUY_PRODUCT", item,
                                 _quote_price(item, inv[item] - 1), ostate)
                elif op == "BUY_SEED" and item in CROPS:
                    quoted[p] = ("BUY_SEED", item, CROPS[item]["seed"], ostate)
                elif op == "BUY_ANIMAL" and item in ANIMALS:
                    quoted[p] = ("BUY_ANIMAL", item, ANIMALS[item]["cost"], ostate)
                else:
                    order_states[p] = None
            if all(q is None for q in quoted):
                break
            committed = False
            for p in (0, 1):
                q = quoted[p]
                if q is None:
                    continue
                op, item, price, ostate = q
                if op == "SELL":
                    if sheds[p].get(item, 0) <= 0:
                        if NO_CAP:
                            pass  # trust the order (agent knows its shed)
                        else:
                            order_states[p] = None
                            continue
                    sheds[p][item] -= 1
                    money[p] += price
                    ostate["d"] += price
                    if price > 1:
                        inv[item] += 1
                    ostate["remaining"] -= 1
                    ostate["done"] += 1
                    committed = True
                else:
                    if money[p] < price:
                        order_states[p] = None
                        continue
                    if op != "BUY_SEED" and sum(sheds[p].values()) >= 100:
                        order_states[p] = None
                        continue
                    money[p] -= price
                    ostate["d"] -= price
                    if op == "BUY_PRODUCT":
                        sheds[p][item] = sheds[p].get(item, 0) + 1
                        inv[item] -= 1
                    elif op == "BUY_ANIMAL":
                        sheds[p][item] = sheds[p].get(item, 0) + 1
                    ostate["remaining"] -= 1
                    ostate["done"] += 1
                    committed = True
            if not committed:
                break
        for p in (0, 1):
            for ost in order_objs[p]:
                pass
    # collect attr: all orders that executed OR were requested (mark n_done)
    for p in (0, 1):
        for qi, raw in enumerate(queues[p]):
            ost = order_objs[p][qi]
            if ost is None:
                continue
            attr[p].append({
                "op": ost["type"], "item": ost.get("item"),
                "n_req": (raw[2] if isinstance(raw, list) and len(raw) >= 3 else 1),
                "n_done": ost["done"], "d": ost["d"],
                "h_done": ost.get("h", 0),
            })
    return money, attr


def load_exact(path):
    """-> steps list with: day, hour, farms, market, privs, acts; plus names."""
    if path.endswith(".jsonl") or path.endswith(".jsonl.gz"):
        import gzip
        opener = gzip.open if path.endswith(".gz") else open
        raw = []
        names = None
        with opener(path, "rt") as f:
            for line in f:
                d = json.loads(line)
                if d.get("t") == "hello":
                    names = [d.get("a"), d.get("b")]
                elif d.get("t") == "turn":
                    raw.append(d)
        steps = []
        for i, d in enumerate(raw):
            nxt = raw[i + 1] if i + 1 < len(raw) else None
            farms = nxt["farms"] if nxt else d["farms"]
            steps.append({
                "t": d["step"], "day": d["day"], "hour": d["hour"],
                "farms": d["farms"],          # pre-action
                "farms_post": farms,
                "market": d["market"],
                "privs": d.get("priv") or [None, None],
                "acts": d.get("acts"),
                "fmt": "arena",
            })
        return steps, names
    d = json.load(open(path))
    steps = []
    names = d["info"].get("TeamNames") if isinstance(d.get("info"), dict) else None
    for t, row in enumerate(d["steps"]):
        obs = row[0]["observation"]
        privs = [row[p]["observation"].get("private") or {} for p in (0, 1)]
        steps.append({
            "t": t, "day": obs["day"], "hour": obs["hour"],
            "farms": obs["farms"],           # post-action(t) = pre-action(t+1)
            "market": obs["market"],
            "privs": privs,
            "acts": [row[p].get("action") for p in (0, 1)],
            "fmt": "kaggle",
        })
    return steps, names


def run_game(steps, collect=False):
    """Full-game exact market sim. Returns per-turn attr + money verification."""
    n = len(steps)
    out = []
    shed_track = [{it: 0 for it in PRODUCTS + ANIMAL_ITEMS} for _ in range(2)]
    money_track = [3000.0, 3000.0]
    for si, s in enumerate(steps):
        fmt = s["fmt"]
        if fmt == "arena":
            base = s
        else:
            if si == 0:
                continue
            base = steps[si - 1]
        inv = dict(base["market"]["inventory"])
        money = [base["farms"][p].get("money") for p in (0, 1)]
        sheds = []
        for p in (0, 1):
            sh = {it: 0 for it in PRODUCTS + ANIMAL_ITEMS}
            priv = base["privs"][p] or {}
            for k, v in (priv.get("shed") or {}).items():
                sh[k] = v
            sheds.append(sh)
        hires = [base["farms"][p].get("hires_today") or 0 for p in (0, 1)]
        uqs = [len(base["farms"][p].get("unlocked_quadrants") or ["NW"]) - 1 for p in (0, 1)]
        m_after, attr = sim_market(inv, list(money),
                                   [{k: v for k, v in sh.items()} for sh in sheds],
                                   list(hires), list(uqs), s["acts"])
        # verification against logged money
        if fmt == "arena":
            nxt = steps[si + 1] if si + 1 < n else None
            actual = [nxt["farms"][p].get("money") if nxt else m_after[p] for p in (0, 1)]
        else:
            actual = [s["farms"][p].get("money") for p in (0, 1)]
        err = [m_after[p] - actual[p] for p in (0, 1)]
        rec = {"si": si, "day": s["day"], "hour": s["hour"], "attr": attr, "err": err,
               "money": actual}
        out.append(rec)
    return out


if __name__ == "__main__":
    path = sys.argv[1]
    steps, names = load_exact(path)
    per_turn = run_game(steps)
    bad = 0
    tot = 0
    for pt in per_turn:
        if pt is None:
            continue
        e = pt["err"]
        tot += 1
        if abs(e[0]) > 0.5 or abs(e[1]) > 0.5:
            bad += 1
            if bad <= 5:
                print("ERR t=%d d%d h%d err=%s" % (pt["si"], pt["day"], pt["hour"], e))
    print(f"{path.split('/')[-1]}: {tot} turns, {bad} money mismatches (names={names})")
