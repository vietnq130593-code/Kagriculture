#!/usr/bin/env python3
"""Parse a kaggriculture episode replay into rich per-step execution data.

Alignment (verified empirically): steps[t].action is the action that was applied
to steps[t-1].observation to produce steps[t].observation.  We re-simulate the
engine's _process_market lockstep per step and verify money against the replay.
Outputs: orders.json, timeline.json, daily.json, summary.json, timeline.csv
"""
import json
import sys
import os
import csv
from collections import defaultdict

sys.path.insert(0, "/home/z/.venv/lib/python3.12/site-packages")
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    CROPS, ANIMALS, PRODUCTS, LAND_PRICES, LAND_ORDER, SHOPS,
    market_price, _hire_cost, _parse_order,
)

REPLAY = sys.argv[1]
OUTDIR = sys.argv[2]
os.makedirs(OUTDIR, exist_ok=True)

d = json.load(open(REPLAY))
steps = d["steps"]
n_steps = len(steps)
team_names = d["info"].get("TeamNames", ["p0", "p1"])
seed = d["info"].get("seed")
rewards = d.get("rewards")
cfg = d.get("configuration", {})
MAX_ORDERS = int(cfg.get("maxMarketOrdersPerTurn", 10))
SHED_CAP = int(cfg.get("shedCapacity", 100))

majkel_idx = team_names.index("Majkel1337") if "Majkel1337" in team_names else None


def obs_of(t, p):
    return steps[t][p]["observation"]


def action_of(t, p):
    a = steps[t][p].get("action") or {}
    return a if isinstance(a, dict) else {}


def farm_of(t, p):
    return obs_of(t, p)["farms"][p]


def priv_of(t, p):
    return obs_of(t, p).get("private", {})


def simulate_market(t):
    """Re-simulate _process_market: action[t] applied to state[t-1] -> state[t].
    Unit actions (DROP/PICKUP/PLACE) mutate the shed BEFORE market orders.
    Returns (exec_log, money, mismatch_flag)."""
    prev = t - 1
    market = obs_of(prev, 0)["market"]
    mparams = market.get("params")
    inv = dict(market["inventory"])
    money = [farm_of(prev, p)["money"] for p in (0, 1)]
    shed = [dict(priv_of(prev, p).get("shed", {})) for p in (0, 1)]
    seeds = [dict(priv_of(prev, p).get("seeds", {})) for p in (0, 1)]
    farms = [farm_of(prev, p) for p in (0, 1)]
    hires = [farms[p]["hires_today"] for p in (0, 1)]
    n_unlock = [len(farms[p]["unlocked_quadrants"]) for p in (0, 1)]
    hands = [len(farms[p]["hands"]) for p in (0, 1)]

    # --- pre-market unit-action shed updates ---
    for p in (0, 1):
        f = farms[p]
        board_size = len(f["tiles"])
        half = board_size // 2
        shed_tiles = {(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)}
        priv = priv_of(prev, p)
        invs = list(priv.get("inventories", []))
        act = action_of(t, p)
        unit_acts = [act.get("farmer")] + list(act.get("hands", []))
        positions = [tuple(f["farmer"])] + [tuple(h) for h in f["hands"]]
        for idx, a in enumerate(unit_acts):
            if not isinstance(a, list) or not a or idx >= len(positions):
                continue
            op = a[0]
            if op not in ("DROP", "PICKUP", "PLACE"):
                continue
            if positions[idx] not in shed_tiles:
                continue
            uinv = dict(invs[idx]) if idx < len(invs) else {}
            if op == "DROP":
                for item, n in uinv.items():
                    if n <= 0:
                        continue
                    room = max(0, SHED_CAP - sum(shed[p].values()))
                    take = min(n, room)
                    if take > 0:
                        shed[p][item] = shed[p].get(item, 0) + take
            elif op == "PICKUP":
                if len(a) < 2:
                    continue
                item = a[1]
                n = int(a[2]) if len(a) >= 3 else 1
                n = min(n, shed[p].get(item, 0))
                if n > 0:
                    shed[p][item] -= n
            elif op == "PLACE":
                if len(a) < 2:
                    continue
                item = a[1]
                fx, fy = positions[idx]
                tile = f["tiles"][fy][fx]
                # animal placed onto matching structure: no shed effect
                if item in ANIMALS and isinstance(tile, dict) and tile.get("kind") == ANIMALS[item]["structure"] and "animal" not in tile:
                    continue
                n = int(a[2]) if len(a) >= 3 else 1
                n = min(n, uinv.get(item, 0))
                if n > 0:
                    room = max(0, SHED_CAP - sum(shed[p].values()))
                    n = min(n, room)
                    if n > 0:
                        shed[p][item] = shed[p].get(item, 0) + n

    queues = []
    for p in (0, 1):
        m = action_of(t, p).get("market", [])
        m = m if isinstance(m, list) else []
        queues.append(list(m[:MAX_ORDERS]))

    order_states = [[_parse_order(o) for o in q] for q in queues]
    logs = [[None] * len(q) for q in queues]
    for p in (0, 1):
        for oi, o in enumerate(queues[p]):
            st = order_states[p][oi]
            if st is None:
                logs[p][oi] = dict(player=p, op=(o[0] if isinstance(o, list) and o else "?"),
                                   item=(o[1] if isinstance(o, list) and len(o) > 1 else None),
                                   asked=(int(o[2]) if isinstance(o, list) and len(o) > 2 and str(o[2]).isdigit() else 1),
                                   units=0, cash=0.0, prices=[])
            else:
                logs[p][oi] = dict(player=p, op=st["type"], item=st.get("item"),
                                   asked=st.get("remaining", 1), units=0, cash=0.0, prices=[])

    for oi in range(max(len(q) for q in queues)):
        # atomic pass (HIRE / BUY_LAND)
        for p in (0, 1):
            if oi >= len(order_states[p]) or order_states[p][oi] is None:
                continue
            st = order_states[p][oi]
            lg = logs[p][oi]
            if st["type"] == "HIRE":
                cost = _hire_cost(hires[p])
                lg["unit_price"] = cost
                if money[p] >= cost:
                    money[p] -= cost
                    hires[p] += 1
                    hands[p] += 1
                    lg["units"] = 1
                    lg["cash"] = -cost
                order_states[p][oi] = None
            elif st["type"] == "BUY_LAND":
                k = n_unlock[p] - 1
                if k < len(LAND_PRICES):
                    cost = LAND_PRICES[k]
                    lg["item"] = LAND_ORDER[k]
                    lg["unit_price"] = cost
                    if money[p] >= cost:
                        money[p] -= cost
                        n_unlock[p] += 1
                        lg["units"] = 1
                        lg["cash"] = -cost
                order_states[p][oi] = None

        # per-unit lockstep pass
        while True:
            quoted = [None, None]
            for p in (0, 1):
                if oi >= len(order_states[p]):
                    continue
                st = order_states[p][oi]
                if st is None or st["remaining"] <= 0:
                    continue
                op, item = st["type"], st["item"]
                if op == "SELL" and item in PRODUCTS:
                    quoted[p] = ("SELL", item, market_price(item, inv[item], mparams), st)
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    quoted[p] = ("BUY_PRODUCT", item, market_price(item, inv[item] - 1, mparams), st)
                elif op == "BUY_SEED" and item in CROPS:
                    quoted[p] = ("BUY_SEED", item, CROPS[item]["seed"], st)
                elif op == "BUY_ANIMAL" and item in ANIMALS:
                    quoted[p] = ("BUY_ANIMAL", item, ANIMALS[item]["cost"], st)
                else:
                    order_states[p][oi] = None
            if all(q is None for q in quoted):
                break
            committed_any = False
            for p in (0, 1):
                q = quoted[p]
                if q is None:
                    continue
                op, item, price, st = q
                lg = logs[p][oi]
                ok = False
                if op == "SELL":
                    if shed[p].get(item, 0) > 0:
                        shed[p][item] -= 1
                        money[p] += price
                        if price > 1:
                            inv[item] += 1
                        ok = True
                elif op == "BUY_PRODUCT":
                    if money[p] >= price and sum(shed[p].values()) < SHED_CAP:
                        money[p] -= price
                        shed[p][item] = shed[p].get(item, 0) + 1
                        inv[item] -= 1
                        ok = True
                elif op == "BUY_SEED":
                    if money[p] >= price:
                        money[p] -= price
                        seeds[p][item] = seeds[p].get(item, 0) + 1
                        ok = True
                elif op == "BUY_ANIMAL":
                    if money[p] >= price and sum(shed[p].values()) < SHED_CAP:
                        money[p] -= price
                        shed[p][item] = shed[p].get(item, 0) + 1
                        ok = True
                if ok:
                    st["remaining"] -= 1
                    lg["units"] += 1
                    lg["cash"] += price if op == "SELL" else -price
                    if len(lg["prices"]) < 3 or op == "SELL":
                        lg["prices"].append(round(price, 2))
                    committed_any = True
                else:
                    order_states[p][oi] = None
            if not committed_any:
                break

    mismatch = 0
    for p in (0, 1):
        rec = farm_of(t, p)["money"]
        if abs(rec - money[p]) > 0.01:
            mismatch += 1
    exec_log = [lg for row in logs for lg in row]
    return exec_log, money, mismatch


# ---- main pass ----
timeline = []
orders_all = []
total_mismatch = 0

for t in range(n_steps):
    if t >= 1:
        exec_log, _, mm = simulate_market(t)
        total_mismatch += mm
        for e in exec_log:
            e["step"] = t
            e["day"] = t // 24
            orders_all.append(e)
    obs = obs_of(t, 0)
    day = obs.get("day", t // 24)
    hour = obs.get("hour", t % 24)
    for p in (0, 1):
        f = farm_of(t, p)
        pv = priv_of(t, p)
        plants = defaultdict(int)
        yields = defaultdict(int)
        animals = defaultdict(int)
        weeds = 0
        for row in f["tiles"]:
            for x in row:
                if isinstance(x, dict):
                    if x.get("kind") == "PLANT":
                        plants[x["crop"]] += 1
                        yields[x["crop"]] += x.get("yield_units", 0)
                    elif x.get("kind") == "WEED":
                        weeds += 1
                    elif "animal" in x:
                        animals[x["animal"]] += 1
        act = action_of(t, p)
        verbs = defaultdict(int)
        for a in [act.get("farmer")] + list(act.get("hands", [])):
            if isinstance(a, list) and a:
                verbs[a[0]] += 1
        timeline.append(dict(
            step=t, day=day, hour=hour, player=p, money=f["money"],
            hands=len(f["hands"]), hires_today=f["hires_today"],
            quadrants=len(f["unlocked_quadrants"]),
            plants=dict(plants), yields=dict(yields), animals=dict(animals),
            weeds=weeds, shed=dict(pv.get("shed", {})),
            shed_total=sum(pv.get("shed", {}).values()),
            seeds=dict(pv.get("seeds", {})),
            unit_verbs=dict(verbs),
            n_market_orders=len(act.get("market", []) or []),
        ))

# market snapshots (shared) + shops
market_snap = []
for t in range(n_steps):
    m = obs_of(t, 0)["market"]
    market_snap.append(dict(step=t, prices=dict(m["prices"]),
                            inventory={k: v for k, v in m["inventory"].items()}))
town_snap = [dict(step=t, shops=list(obs_of(t, 0).get("town", {}).get("unlocked_shops", [])))
             for t in range(n_steps)]

# ---- per-day aggregates ----
daily = []
by_day = defaultdict(list)
for row in timeline:
    by_day[(row["day"], row["player"])].append(row)
orders_by_day = defaultdict(list)
for e in orders_all:
    orders_by_day[(e["day"], e["player"])].append(e)

# Money at end of previous day (start of this day). Timeline snapshot at step t
# is POST-action, so rows[0].money (step day*24) already includes the first
# step's orders — using it as money_start silently dropped those transactions
# from profit_day. Start-of-day money = money after the last step of the
# previous day (end-of-day processing never touches money).
money_by_sp = {(row["step"], row["player"]): row["money"] for row in timeline}

for (day, p), rows in sorted(by_day.items()):
    ods = orders_by_day.get((day, p), [])
    buys = defaultdict(lambda: [0, 0.0])
    sells = defaultdict(lambda: [0, 0.0])
    hire_spend = land_spend = 0.0
    for e in ods:
        if e["op"] == "SELL":
            sells[e["item"]][0] += e["units"]
            sells[e["item"]][1] += e["cash"]
        elif e["op"] == "HIRE":
            hire_spend += -e["cash"]
        elif e["op"] == "BUY_LAND":
            land_spend += -e["cash"]
        elif e["op"] in ("BUY_SEED", "BUY_ANIMAL", "BUY_PRODUCT"):
            buys[e["item"]][0] += e["units"]
            buys[e["item"]][1] += -e["cash"]
    verbs = defaultdict(int)
    for r in rows:
        for v, c in r["unit_verbs"].items():
            verbs[v] += c
    money_start = 3000.0 if day == 0 else money_by_sp[(day * 24 - 1, p)]
    daily.append(dict(
        day=day, player=p, money_start=money_start, money_end=rows[-1]["money"],
        profit_day=rows[-1]["money"] - money_start,
        buys={k: dict(units=v[0], cash=round(v[1], 2)) for k, v in buys.items() if v[0] > 0},
        sells={k: dict(units=v[0], cash=round(v[1], 2)) for k, v in sells.items() if v[0] > 0},
        hire_spend=hire_spend, land_spend=land_spend,
        verbs=dict(verbs), plants=dict(rows[-1]["plants"]),
        animals=dict(rows[-1]["animals"]), shed=dict(rows[-1]["shed"]),
        hands_max=max(r["hands"] for r in rows),
        quadrants=rows[-1]["quadrants"], weeds=rows[-1]["weeds"],
    ))

# ---- summary ----
def final_money(p):
    return farm_of(n_steps - 1, p)["money"]

winner_v = "tie" if rewards[0] == rewards[1] else (0 if rewards[0] > rewards[1] else 1)
summary = dict(
    episode_id=d.get("id"), teams=team_names, seed=seed, rewards=rewards,
    statuses=d.get("statuses"), final_money=[final_money(0), final_money(1)],
    winner=winner_v,
    margin=abs(rewards[0] - rewards[1]), majkel_idx=majkel_idx,
    n_steps=n_steps, money_mismatch_player_steps=total_mismatch,
)
for p in (0, 1):
    sel = [e for e in orders_all if e["player"] == p]
    tot = lambda op: sum(-e["cash"] for e in sel if e["op"] == op)
    summary[f"p{p}"] = dict(
        revenue=round(sum(e["cash"] for e in sel if e["op"] == "SELL"), 2),
        sell_units=sum(e["units"] for e in sel if e["op"] == "SELL"),
        hire_spend=tot("HIRE"), land_spend=tot("BUY_LAND"),
        seed_spend=tot("BUY_SEED"), animal_spend=tot("BUY_ANIMAL"),
        product_spend=tot("BUY_PRODUCT"),
        n_orders=len(sel), n_executed=sum(1 for e in sel if e["units"] > 0),
    )

json.dump(orders_all, open(f"{OUTDIR}/orders.json", "w"))
json.dump(timeline, open(f"{OUTDIR}/timeline.json", "w"))
json.dump(daily, open(f"{OUTDIR}/daily.json", "w"))
json.dump(market_snap, open(f"{OUTDIR}/market.json", "w"))
json.dump(town_snap, open(f"{OUTDIR}/town.json", "w"))
json.dump(summary, open(f"{OUTDIR}/summary.json", "w"), indent=1)

with open(f"{OUTDIR}/timeline.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["step", "day", "hour", "player", "money", "hands", "hires_today",
                "quadrants", "plants", "animals", "weeds", "shed_total"])
    for r in timeline:
        w.writerow([r["step"], r["day"], r["hour"], r["player"], r["money"], r["hands"],
                    r["hires_today"], r["quadrants"], json.dumps(r["plants"]),
                    json.dumps(r["animals"]), r["weeds"], r["shed_total"]])

print(json.dumps(summary, indent=1))
