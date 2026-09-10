#!/usr/bin/env python3
"""Full ledger: revenue per channel, costs, prices, shops, labor for both matches.

Convention (verified): steps[t].observation = state AFTER steps[t].action.
Market processing happens BEFORE town consume at each step.
SELL price for unit i of item X at step t uses market_price(X, inv_before + i).
"""
import json
import math

MARKET_I0 = 10000
PRICE_FLOOR = 1
HINGE_GAIN = 8.0

MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}


def _shape(func, x, T=None):
    x = max(0.0, x)
    if func == "linear": return x
    if func == "sq":     return x * x
    if func == "sqrt":   return math.sqrt(x)
    if func == "log":    return math.log(1.0 + x)
    if func == "log10":  return math.log10(1.0 + x)
    if func == "hinge":
        if not T or T <= 0:
            return x
        u = x / T
        return u + HINGE_GAIN * max(0.0, u - 1.0) ** 2
    return x


def market_price(item, inv):
    p = MARKET_PARAMS[item]
    I0 = MARKET_I0
    base = p["base"]
    x = abs(inv - I0)
    if inv < I0:
        amp = p["below_target"] * base / _shape(p["below_func"], p["T"], p["T"])
        val = base + amp * _shape(p["below_func"], x, p["T"])
    else:
        amp = p["above_target"] * base / _shape(p["above_func"], p["T"], p["T"])
        val = base - amp * _shape(p["above_func"], x, p["T"])
    return max(PRICE_FLOOR, round(val))


def fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


SEED_COST = {"WHEAT": 10, "CARROT": 20, "TOMATO": 50, "STRAWBERRY": 100, "MELON": 80}
ANIMAL_COST = {"GOOSE": 300, "COW": 400, "SHEEP": 500}


def analyze(fn):
    with open(fn) as f:
        data = json.load(f)
    names = data["info"]["TeamNames"]
    steps = data["steps"]

    ledger = {0: {"sell_rev": {}, "units_sold": {}, "seed_cost": {}, "seeds_bought": {},
                  "animal_cost": {}, "animals_bought": {}, "wheat_buy_cost": 0.0, "wheat_bought": 0,
                  "fert_buy_cost": 0.0, "fert_bought": 0, "hire_cost": 0.0, "hire_count": 0,
                  "land_cost": 0.0, "invalid_orders": 0},
              1: {}}
    ledger[1] = json.loads(json.dumps(ledger[0]))

    # per-day revenue
    daily_rev = {0: {}, 1: {}}

    prev_inv = None
    prev_money = [None, None]
    prev_hires = [0, 0]

    for t, steprec in enumerate(steps):
        obs = steprec[0]["observation"]
        inv = dict(obs["market"]["inventory"])

        for p in (0, 1):
            act = steprec[p].get("action")
            if not act:
                continue
            mkt = act.get("market", [])
            # count hires to compute costs
            hires_at_step = sum(1 for mo in mkt if mo and mo[0] == "HIRE")
            buy_land = sum(1 for mo in mkt if mo and mo[0] == "BUY_LAND")

            L = ledger[p]
            hcost = 0
            for _ in range(hires_at_step):
                hcost += fib(prev_hires[p] if prev_hires[p] is not None else 0)
                prev_hires[p] = (prev_hires[p] or 0) + 1
            # hires_today resets at end of day — handle via obs
            L["hire_cost"] += hcost
            L["hire_count"] += hires_at_step

            for mo in mkt:
                if not isinstance(mo, list) or not mo:
                    continue
                op = mo[0]
                if op in ("HIRE", "BUY_LAND"):
                    continue
                if len(mo) < 3:
                    continue
                item, qty = mo[1], mo[2]
                if op == "SELL" and item in MARKET_PARAMS:
                    # reconstruct prices from inventory before this step's sells
                    base_inv = prev_inv[item] if prev_inv else MARKET_I0
                    # both players' sells interleave; approximate sequential
                    n_eff = 0
                    for i in range(qty):
                        pr = market_price(item, base_inv + n_eff)
                        L["sell_rev"][item] = L["sell_rev"].get(item, 0.0) + pr
                        n_eff += 1
                    L["units_sold"][item] = L["units_sold"].get(item, 0) + qty
                    daily_rev[p].setdefault(obs["day"], {}).setdefault(item, 0)
                    daily_rev[p][obs["day"]][item] += qty
                    # update local inventory tracking
                elif op == "BUY_SEED" and item in SEED_COST:
                    L["seed_cost"][item] = L["seed_cost"].get(item, 0.0) + SEED_COST[item] * qty
                    L["seeds_bought"][item] = L["seeds_bought"].get(item, 0) + qty
                elif op == "BUY_ANIMAL" and item in ANIMAL_COST:
                    L["animal_cost"][item] = L["animal_cost"].get(item, 0.0) + ANIMAL_COST[item] * qty
                    L["animals_bought"][item] = L["animals_bought"].get(item, 0) + qty
                elif op == "BUY_PRODUCT" and item in ("WHEAT", "FERTILIZER"):
                    base_inv = prev_inv[item] if prev_inv else MARKET_I0
                    for i in range(qty):
                        pr = market_price(item, base_inv - 1 - i)
                        if item == "WHEAT":
                            L["wheat_buy_cost"] += pr
                            L["wheat_bought"] += 1
                        else:
                            L["fert_buy_cost"] += pr
                            L["fert_bought"] += 1
                elif op == "BUY_PRODUCT":
                    L["invalid_orders"] += 1
                elif op == "SELL":
                    L["invalid_orders"] += 1

            if buy_land:
                L["land_cost"] += 1000 * buy_land  # approx (NE=1k, SW=2k...) refined later

        # track hires_today from observation to reset per-day
        for p in (0, 1):
            f = obs["farms"][p]
            if f.get("hires_today", 0) == 0 and t % 24 == 0:
                prev_hires[p] = 0
        prev_inv = inv

    return {"names": names, "rewards": data["rewards"], "ledger": ledger, "daily_rev": daily_rev}


def main():
    out = {}
    for fn in ["/home/z/my-project/upload/107559251.json", "/home/z/my-project/upload/107573831.json"]:
        r = analyze(fn)
        out[fn.split("/")[-1]] = r
    with open("/home/z/my-project/tool-results/replay_ledger.json", "w") as f:
        json.dump(out, f, indent=1)
    print("done")


if __name__ == "__main__":
    main()
