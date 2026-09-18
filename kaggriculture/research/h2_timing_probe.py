#!/usr/bin/env python3
"""H2 TIMING PROBE — peak-pricing measurement (Task 92).

Runs v20 vs ahmedv46 on several seeds (both seats) via arena/run_battle.py
JSONL telemetry, then measures:

  1. SELL-hour histogram per item per player (when do we sell vs v46?)
  2. BUY/HIRE-hour histogram (cash-starvation risk of delaying revenue)
  3. Intraday inventory path per item (avg inv by hour-of-day) -> trough/peak
  4. First-order counterfactual: revenue if OUR SELL orders were emitted at a
     different hour (walk-down model with measured per-hour inventory),
     feedback ignored (our volume share is a minority of market flow).
  5. Price sensitivity dp/dinv at the operating point per item.

Output: research/h2_timing_probe.json + stdout analysis.
"""
import json
import subprocess
import sys
import os
import math

ROOT = "/home/z/my-project/kaggriculture"
OUT = os.path.join(ROOT, "research", "h2_timing_probe.json")

SEEDS = [5, 8, 11, 17, 21, 3]  # 6 seeds, seat 0 only (analysis; seats ±1100 noise)


# ---- engine price model (copied from /home/z/engine.py, byte-exact) ----
def _shape(func, x, T=None):
    if func == "linear":
        return x / T
    if func == "sq":
        return (x / T) ** 2
    if func == "sqrt":
        return math.sqrt(x / T)
    if func == "log":
        return math.log(1 + x / T)
    if func == "log10":
        return math.log10(1 + x / T)
    if func == "hinge":
        r = x / T
        if r <= 1:
            return r
        return 1 + HINGE_GAIN * (r - 1) ** 2 / r
    raise ValueError(func)


HINGE_GAIN = 8.0
MARKET_I0 = 10000
PRICE_FLOOR = 1

MARKET_PARAMS = {
    "WHEAT":      {"base":  25, "I0": MARKET_I0, "T": 400, "below_func": "sqrt",   "below_target": 0.80, "above_func": "log",    "above_target": 0.20},
    "CARROT":     {"base":  35, "I0": MARKET_I0, "T": 450, "below_func": "hinge",  "below_target": 1.00, "above_func": "sqrt",   "above_target": 0.70},
    "TOMATO":     {"base":  60, "I0": MARKET_I0, "T": 200, "below_func": "hinge",  "below_target": 0.40, "above_func": "sqrt",   "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": MARKET_I0, "T": 100, "below_func": "sqrt",   "below_target": 0.70, "above_func": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": MARKET_I0, "T": 300, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.60},
    "EGG":        {"base":  50, "I0": MARKET_I0, "T": 332, "below_func": "hinge",  "below_target": 0.40, "above_func": "log",    "above_target": 0.20},
    "MILK":       {"base": 160, "I0": MARKET_I0, "T": 122, "below_func": "sqrt",   "below_target": 0.60, "above_func": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": MARKET_I0, "T": 105, "below_func": "log",    "below_target": 0.20, "above_func": "sq",     "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": MARKET_I0, "T": 200, "below_func": "linear", "below_target": 0.40, "above_func": "linear", "above_target": 0.40},
}


def market_price(item, inventory):
    p = MARKET_PARAMS[item]
    base, I0, T = p["base"], p["I0"], p["T"]
    if inventory < I0:
        f = p["below_func"]
        amp = p["below_target"] * base / _shape(f, T, T)
        price = base + amp * _shape(f, I0 - inventory, T)
    else:
        f = p["above_func"]
        amp = p["above_target"] * base / _shape(f, T, T)
        price = base - amp * _shape(f, inventory - I0, T)
    return max(PRICE_FLOOR, int(round(price)))


def price_of_path(item, inv, k):
    """Revenue of selling k units starting at inventory inv (walk-down)."""
    total = 0
    for i in range(k):
        total += market_price(item, inv + i)
    return total


# ---- run one battle and collect turn lines ----
def run(agent, opp, seed):
    cmd = [sys.executable, f"{ROOT}/arena/run_battle.py", "--a", agent,
           "--b", opp, "--seed", str(seed)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600, cwd=ROOT)
    turns, end = [], None
    for line in (p.stdout or "").splitlines():
        try:
            o = json.loads(line)
        except Exception:
            continue
        if o.get("t") == "end":
            end = o
        elif o.get("t") == "turn":
            turns.append(o)
    return turns, end


def analyze(turns, me=0):
    """Turns: list of {"step","hour","day","market","acts":[a0,a1],"farms"}"""
    sells = {0: {}, 1: {}}       # (player, item) -> {hour: units}
    buys = {0: {}, 1: {}}        # (player) -> {hour: ops}
    inv_path = {}                # item -> {hour: [inv,...]} (pre-action inv per hour)
    price_path = {}              # item -> {hour: [price,...]}
    sell_events = []             # (day, hour, item, qty, inv_at, player)
    money = {0: [], 1: []}

    for t in turns:
        step = t.get("step", 0)
        hour = step % 24
        day = step // 24
        mk = t.get("market") or {}
        invd = mk.get("inventory") or {}
        prd = mk.get("prices") or {}
        for item, v in invd.items():
            inv_path.setdefault(item, {}).setdefault(hour, []).append(v)
        for item, v in prd.items():
            price_path.setdefault(item, {}).setdefault(hour, []).append(v)
        for pid in (0, 1):
            acts = (t.get("acts") or [None, None])[pid]
            if not isinstance(acts, dict):
                continue
            for o in (acts.get("market") or []):
                if not (isinstance(o, list) and len(o) >= 3 and isinstance(o[2], (int, float))):
                    continue
                op, item, q = o[0], o[1], int(o[2])
                if op == "SELL" and q > 0:
                    d = sells[pid].setdefault(item, {})
                    d[hour] = d.get(hour, 0) + q
                    if pid == me:
                        sell_events.append(
                            {"day": day, "hour": hour, "item": item, "qty": q,
                             "inv": invd.get(item, MARKET_I0)})
                elif op in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"):
                    d = buys[pid].setdefault(op, {})
                    d[hour] = d.get(hour, 0) + q
                elif op == "HIRE":
                    d = buys[pid].setdefault("HIRE", {})
                    d[hour] = d.get(hour, 0) + 1
            fm = (t.get("farms") or [None, None])[pid]
            if isinstance(fm, dict):
                money[pid].append(fm.get("money", 0))
    return {"sells": sells, "buys": buys, "inv_path": inv_path,
            "price_path": price_path, "sell_events": sell_events,
            "end_money": {pid: (money[pid][-1] if money[pid] else 0) for pid in (0, 1)}}


def counterfactual(turns, me=0, target_hour=23):
    """Revenue delta if OUR sell orders emitted at target_hour instead.

    Model: for a sell of (item, q) at (day, hour, inv_at): baseline revenue =
    walk-down from inv_at (measured pre-action inv at that exact turn). Shifted
    revenue = walk-down from inv_at_hour(target, day) (measured avg inv at the
    same day, target hour; falls back to day's hourly mean). Feedback (our own
    +v46's later sales reacting) ignored — first-order estimate.
    """
    # inv per (item, day, hour) pre-action
    inv_map = {}
    for t in turns:
        day = t.get("step", 0) // 24
        hour = t.get("step", 0) % 24
        for item, v in ((t.get("market") or {}).get("inventory") or {}).items():
            inv_map[(item, day, hour)] = v

    deltas = {}
    details = []
    for t in turns:
        step = t.get("step", 0)
        day, hour = step // 24, step % 24
        acts = (t.get("acts") or [None, None])[me]
        if not isinstance(acts, dict):
            continue
        for o in (acts.get("market") or []):
            if not (isinstance(o, list) and len(o) >= 3
                    and o[0] == "SELL" and isinstance(o[2], (int, float))
                    and int(o[2]) > 0):
                continue
            item, q = o[1], int(o[2])
            if hour == target_hour:
                continue
            base_inv = inv_map.get((item, day, hour), MARKET_I0)
            tgt_inv = inv_map.get((item, day, target_hour))
            if tgt_inv is None:
                # fallback: mean over recorded hours that day
                vals = [v for (it, d, h), v in inv_map.items()
                        if it == item and d == day]
                tgt_inv = sum(vals) / len(vals) if vals else base_inv
            rev_base = price_of_path(item, base_inv, q)
            rev_tgt = price_of_path(item, int(tgt_inv), q)
            dd = rev_tgt - rev_base
            deltas[item] = deltas.get(item, 0) + dd
            if dd != 0:
                details.append({"day": day, "hour": hour, "item": item,
                                "qty": q, "inv_base": base_inv,
                                "inv_tgt": int(tgt_inv), "delta": dd})
    return deltas, details


def main():
    all_data = {"games": []}
    agg_sell = {}
    agg_buy = {}
    agg_cf = {}
    for seed in SEEDS:
        turns, end = run("v20", "ahmedv46", seed)
        if end is None:
            print(f"seed {seed}: NO END LINE", flush=True)
            continue
        a = analyze(turns, me=0)
        cf, det = counterfactual(turns, me=0, target_hour=23)
        game = {"seed": seed, "rewards": end.get("rewards"),
                "sell_hist": a["sells"], "buy_hist": a["buys"],
                "end_money": a["end_money"], "cf_h23": cf}
        all_data["games"].append(game)
        gap = end["rewards"][0] - end["rewards"][1]
        print(f"=== seed {seed}: v20 {end['rewards'][0]:.0f} vs v46 {end['rewards'][1]:.0f} (gap {gap:+.0f})")
        print(f"    my SELL hours: " + " ".join(
            f"{it}: " + ",".join(f"h{h}={u}" for h, u in sorted(hh.items()))
            for it, hh in a["sells"][0].items()))
        print(f"    v46 SELL hours: " + " ".join(
            f"{it}: " + ",".join(f"h{h}={u}" for h, u in sorted(hh.items()))
            for it, hh in a["sells"][1].items()))
        print(f"    my BUY hours: " + " ".join(
            f"{op}: " + ",".join(f"h{h}={n}" for h, n in sorted(hh.items()))
            for op, hh in a["buys"][0].items()))
        print(f"    cf shift->h23: " + " ".join(
            f"{it}:{d:+.0f}" for it, d in sorted(cf.items())))
        # per-item intraday inventory swing (avg over days, last 20 days)
        for item in ("WHEAT", "MILK", "WOOL", "STRAWBERRY", "MELON", "EGG", "CARROT", "TOMATO"):
            hh = a["inv_path"].get(item)
            if not hh:
                continue
            means = {h: sum(v) / len(v) for h, v in hh.items()}
            lo = min(means.values()); hi = max(means.values())
            # dp/dinv at mean level
            mid = sum(means.values()) / len(means.values())
            dp = market_price(item, int(mid) - 1) - market_price(item, int(mid) + 1)
            if seed == SEEDS[0]:
                print(f"    [{item}] inv by hour: " + " ".join(
                    f"h{h}:{means[h]:.0f}" for h in sorted(means)))
            print(f"    [{item}] intraday lo {lo:.0f} @h{min(means, key=means.get)} "
                  f"hi {hi:.0f} @h{max(means, key=means.get)} | dp/2u {dp:+.1f}")
        for it, d in cf.items():
            agg_cf[it] = agg_cf.get(it, 0) + d
        for pid in (0, 1):
            for it, hh in a["sells"][pid].items():
                k = (pid, it)
                for h, u in hh.items():
                    agg_sell[k] = agg_sell.get(k, {}) or {}
                    agg_sell.setdefault(k, {})[h] = agg_sell[k].get(h, 0) + u
        for op, hh in a["buys"][0].items():
            for h, n in hh.items():
                agg_buy.setdefault(op, {})[h] = agg_buy.get(op, {}).get(h, 0) + n

    print("\n=== AGGREGATE (6 seeds) ===")
    print("my sell hours (units): " + " ".join(
        f"{it}: " + ",".join(f"h{h}={u}" for h, u in sorted(hh.items()))
        for (pid, it), hh in sorted(agg_sell.items()) if pid == 0))
    print("v46 sell hours (units): " + " ".join(
        f"{it}: " + ",".join(f"h{h}={u}" for h, u in sorted(hh.items()))
        for (pid, it), hh in sorted(agg_sell.items()) if pid == 1))
    print("my buy hours (ops): " + " ".join(
        f"{op}: " + ",".join(f"h{h}={n}" for h, n in sorted(hh.items()))
        for op, hh in sorted(agg_buy.items())))
    print("cf total shift->h23 per item: " + " ".join(
        f"{it}:{d:+.0f}" for it, d in sorted(agg_cf.items())))
    print(f"cf TOTAL: {sum(agg_cf.values()):+.0f} over {len(SEEDS)} seeds "
          f"(~{sum(agg_cf.values())/len(SEEDS):+.0f}/game)")

    with open(OUT, "w") as f:
        json.dump(all_data, f, indent=1)
    print(f"saved {OUT}")


if __name__ == "__main__":
    main()
