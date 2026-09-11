#!/usr/bin/env python3
"""PHASE 5 (Task 45) — Đo theo yêu cầu user:
  A1: đất trống (chết) mỗi ngày
  A2: đàn (số con + vị trí + LIÊN KHỐI: components/share/adjacency) mỗi ngày
  A3: cây đứng (số lượng + loại) mỗi ngày
  A4: thời điểm bán (giờ) + giá bán + tấn công thị trường qua lại
  A5: phân rã nguồn tiền → 90k-110k từ đâu ra

Sources: top-3 (2 replay × 2 seat) + v8/v7 (6 arena jsonl).
"""
import json, glob, sys
from collections import defaultdict

sys.path.insert(0, "/home/z/my-project/kaggriculture")
from v8 import MARKET_PARAMS, MARKET_I0, ANIMALS, CROPS, LAND_PRICES, _price, _fib

sys.path.insert(0, "/home/z/my-project/tool-results/v8_style")
from analyze_style import load_any, unit_positions, man, quadrant_of, SPAWN, BOARD

PROD = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def scan_tiles(farm):
    out = {"empty": [], "weeds": [], "plants": defaultdict(list), "animals": []}
    tiles = farm["tiles"]
    for y in range(BOARD):
        for x in range(BOARD):
            t = tiles[y][x]
            if t == "LOCKED" or t == "SHED":
                continue
            if t is None:
                out["empty"].append((x, y))
            elif t.get("kind") == "WEED":
                out["weeds"].append((x, y))
            elif t.get("kind") == "PLANT":
                out["plants"][t.get("crop")].append((x, y))
            elif t.get("kind") in ("COOP", "PASTURE"):
                out["animals"].append((x, y, t.get("kind"), t.get("animal")))
    return out


def block_stats(atiles):
    """4-connected components + adjacency share of animal tiles."""
    if not atiles:
        return {"n": 0, "ncomp": 0, "big_share": 0.0, "adj_pct": 0.0,
                "d_shed": None, "bbox": 0}
    S = set((x, y) for (x, y, k, a) in atiles)
    seen = set()
    comps = []
    for p in sorted(S):
        if p in seen:
            continue
        stack, comp = [p], set()
        seen.add(p)
        while stack:
            cx, cy = stack.pop()
            comp.add((cx, cy))
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (cx + dx, cy + dy)
                if q in S and q not in seen:
                    seen.add(q)
                    stack.append(q)
        comps.append(comp)
    big = max(len(c) for c in comps)
    adj = sum(1 for (x, y) in S
              if any((x + dx, y + dy) in S for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))))
    ds = [man((x, y), SPAWN) for (x, y, k, a) in atiles]
    xs = [t[0] for t in atiles]; ys = [t[1] for t in atiles]
    return {"n": len(atiles), "ncomp": len(comps), "big_share": big / len(atiles),
            "adj_pct": adj / len(atiles),
            "d_shed": sum(ds) / len(ds),
            "bbox": (max(xs) - min(xs)) + (max(ys) - min(ys))}


def analyze(path, pidx, name):
    steps, names = load_any(path)
    kaggle = path.endswith(".json") and not path.endswith(".jsonl")
    R = {"name": name, "src": path.split("/")[-1], "seat": pidx,
         "daily": {}, "money_final": steps[-1]["farms"][pidx].get("money"),
         "sells": [], "buys": [], "ops_hour": defaultdict(int),
         "rev_channel": defaultdict(float), "cost_channel": defaultdict(float),
         "rev_day": defaultdict(float), "walk_total": 0.0, "arbitrage": []}
    prev_pos = None
    for si, s in enumerate(steps):
        day, hour = s["day"], s["hour"]
        act = (s["acts"] or [None, None])[pidx]
        farm = s["farms"][pidx]
        # base market/farm state that action(t) sees:
        #   kaggle: obs(t) is POST-action(t) -> action(t) ran on obs(t-1)
        #   arena:  turn t is PRE-action(t)  -> action(t) runs on turn t itself
        base_s = steps[si - 1] if (kaggle and si > 0) else s
        mkt = (base_s.get("market") or {})
        inv = (mkt.get("inventory") or {})
        bfarm = base_s["farms"][pidx]
        pos = unit_positions(farm)
        if prev_pos is not None and len(pos) == len(prev_pos):
            R["walk_total"] += sum(man(a, b) for a, b in zip(pos, prev_pos))
        prev_pos = pos
        if act:
            for u in ([act.get("farmer")] + list(act.get("hands") or [])):
                if u and u[0] == "SELL":
                    R["ops_hour"][hour] += 1
            for g in (act.get("market") or []):
                if not g:
                    continue
                op = g[0]
                if op == "SELL":
                    it, n = g[1], g[2]
                    base = inv.get(it, MARKET_I0)
                    rev = 0.0
                    for k in range(n):
                        p = _price(it, base + k)
                        rev += p
                    R["sells"].append({"d": day, "h": hour, "it": it, "n": n, "rev": rev,
                                       "p0": _price(it, base)})
                    R["rev_channel"][it] += rev
                    R["rev_day"][day] += rev
                elif op == "BUY_PRODUCT":
                    if g[1] not in ("WHEAT", "FERTILIZER"):
                        continue  # engine silently drops these
                    it, n = g[1], g[2]
                    base = inv.get(it, MARKET_I0)
                    cost = 0.0
                    for k in range(n):
                        cost += _price(it, base - 1 - k)  # quote at post-buy inv
                    R["buys"].append({"d": day, "h": hour, "it": it, "n": n, "cost": cost})
                    R["cost_channel"]["BUY:" + it] += cost
                elif op == "BUY_ANIMAL":
                    R["cost_channel"]["ANIMALS"] += ANIMALS[g[1]]["cost"] * g[2]
                elif op == "BUY_LAND":
                    uq = len(bfarm.get("unlocked_quadrants") or ["NW"]) - 1
                    R["cost_channel"]["LAND"] += LAND_PRICES[min(uq, len(LAND_PRICES) - 1)]
                elif op == "HIRE":
                    R["cost_channel"]["HIRE"] += _fib(bfarm.get("hires_today") or 0)
                elif op == "BUY_SEED":
                    R["cost_channel"]["SEEDS"] += CROPS[g[1]]["seed"] * g[2]
        if hour == 23 or s["t"] >= len(steps) - 1:
            sc = scan_tiles(farm)
            R["daily"][day] = {
                "dead": len(sc["empty"]) + len(sc["weeds"]),
                "weeds": len(sc["weeds"]),
                "plants": {k: len(v) for k, v in sc["plants"].items()},
                "n_plants": sum(len(v) for v in sc["plants"].values()),
                "animals": len(sc["animals"]),
                "animal_types": dict(sorted(
                    (a or "DEAD", sum(1 for t in sc["animals"] if t[3] == a))
                    for a in set(t[3] for t in sc["animals"]))),
                "block": block_stats(sc["animals"]),
                "money": farm.get("money"),
            }
    return R


def _avg(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else 0.0


def grp(Rs):
    """Group aggregate over player-traces."""
    out = {}
    days = sorted(R["daily"] for R in Rs)[0] if False else None
    alld = sorted(set(d for R in Rs for d in R["daily"]))
    n = len(Rs)
    dead = {d: sum(R["daily"][d]["dead"] for R in Rs if d in R["daily"]) / n for d in alld}
    herd = {d: sum(R["daily"][d]["animals"] for R in Rs if d in R["daily"]) / n for d in alld}
    blk = {d: (
               _avg([R["daily"][d]["block"]["ncomp"] for R in Rs if d in R["daily"]]),
               _avg([R["daily"][d]["block"]["big_share"] for R in Rs if d in R["daily"] and R["daily"][d]["animals"] > 0]),
               _avg([R["daily"][d]["block"]["adj_pct"] for R in Rs if d in R["daily"] and R["daily"][d]["animals"] > 0]),
               _avg([R["daily"][d]["block"]["d_shed"] for R in Rs if d in R["daily"] and R["daily"][d]["block"]["d_shed"] is not None]))
           for d in alld}
    plants = {d: sum(R["daily"][d]["n_plants"] for R in Rs if d in R["daily"]) / n for d in alld}
    pmix = {d: defaultdict(float) for d in alld}
    for R in Rs:
        for d, s in R["daily"].items():
            for c, k in s["plants"].items():
                pmix[d][c] += k
    for d in alld:
        pmix[d] = {c: v / n for c, v in pmix[d].items()}
    rev = defaultdict(float)
    for R in Rs:
        for c, v in R["rev_channel"].items():
            rev[c] += v
    rev = {c: v / n for c, v in rev.items()}
    cost = defaultdict(float)
    for R in Rs:
        for c, v in R["cost_channel"].items():
            cost[c] += v
    cost = {c: v / n for c, v in cost.items()}
    money = {d: sum(R["daily"][d]["money"] for R in Rs if d in R["daily"]) / n
             for d in alld if any(d in R["daily"] for R in Rs)}
    return {"dead": dead, "herd": herd, "blk": blk, "plants": plants, "pmix": pmix,
            "rev": rev, "cost": cost, "money": money, "n": n}


def fmt_series(d, days=None, w=5):
    days = days or sorted(d)
    rows = []
    for i in range(0, len(days), w):
        chunk = days[i:i + w]
        rows.append("d%-2d " % chunk[0] + " ".join("%3d" % d[x] for x in chunk))
    return "\n".join(rows)


if __name__ == "__main__":
    srcs = []
    for p in ("/home/z/my-project/upload/107559251.json",
              "/home/z/my-project/upload/107573831.json"):
        steps, names = load_any(p)
        srcs.append((p, names))
    for p in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/v8p_*.jsonl")):
        steps, names = load_any(p)
        srcs.append((p, names))

    T3, V8, V7 = [], [], []
    for path, names in srcs:
        nm = names if names else ["P0", "P1"]
        for pidx in (0, 1):
            R = analyze(path, pidx, nm[pidx])
            if "1075" in path:
                T3.append(R)
                print("T3  %-28s %-12s final=$%.0f" % (R["src"], R["name"], R["money_final"]))
            else:
                (V8 if pidx == 0 else V7).append(R)

    G = {"TOP3": grp(T3), "V8": grp(V8), "V7": grp(V7)}
    import pickle
    pickle.dump({"G": G, "T3": T3, "V8": V8, "V7": V7}, open("/tmp/phase5.pkl", "wb"))

    print("\n================ A1. ĐẤT CHẾT MỖI NGÀY (empty+weed) ================")
    for k in ("TOP3", "V8", "V7"):
        print(f"--- {k} ---")
        print(fmt_series(G[k]["dead"]))
    print("\n================ A2. ĐÀN MỖI NGÀY (số con) ================")
    for k in ("TOP3", "V8", "V7"):
        print(f"--- {k} ---")
        print(fmt_series(G[k]["herd"]))
    print("\n--- Block coherence d10-27 TB: (ncomp, big_share, adj%, d̄shed) ---")
    for k in ("TOP3", "V8", "V7"):
        v = [G[k]["blk"][d] for d in range(10, 28)]
        print("%-5s ncomp=%.2f  big_share=%.2f  adj%%=%.2f  d̄shed=%.2f" % (
            k, sum(x[0] for x in v) / len(v), sum(x[1] for x in v) / len(v),
            sum(x[2] for x in v) / len(v), sum(x[3] for x in v) / len(v)))
    print("\n================ A3. CÂY ĐỨNG MỖI NGÀY ================")
    for k in ("TOP3", "V8", "V7"):
        print(f"--- {k} tổng ---")
        print(fmt_series(G[k]["plants"]))
    print("\n--- Cơ cấu cây (TB mùa d5-27) ---")
    for k in ("TOP3", "V8", "V7"):
        mix = defaultdict(float)
        for d in range(5, 28):
            for c, v in G[k]["pmix"][d].items():
                mix[c] += v
        print(k, {c: round(v / 22, 1) for c, v in sorted(mix.items())})
    print("\n================ A4. THỜI ĐIỂM BÁN (giờ) ================")
    for k in ("TOP3", "V8"):
        hh = defaultdict(int)
        for R in (T3 if k == "TOP3" else V8):
            for s in R["sells"]:
                hh[s["h"]] += 1
        tot = sum(hh.values())
        print(k, "tổng lệnh SELL:", tot)
        print("  " + " ".join("h%d:%2d%%" % (h, 100 * c / tot) for h, c in sorted(hh.items())))
    print("\n--- Giá bán trung bình theo kênh (p0 tại lệnh) ---")
    print("%-12s %-22s %-22s" % ("kênh", "TOP3 u/avgP/rev$", "V8 u/avgP/rev$"))
    for it in PROD:
        def st(Rs):
            u = sum(s["n"] for R in Rs for s in R["sells"] if s["it"] == it)
            rev = sum(s["rev"] for R in Rs for s in R["sells"] if s["it"] == it)
            p = sum(s["p0"] * s["n"] for R in Rs for s in R["sells"] if s["it"] == it) / max(1, u)
            return u, p, rev / len(Rs)
        print("%-12s %-22s %-22s" % (it,
              "%4d/%3.0f/%6.0f" % st(T3), "%4d/%3.0f/%6.0f" % st(V8)))
    print("\n================ A5. PHÂN RÃ TIỀN ================")
    for k, Rs in (("TOP3", T3), ("V8", V8)):
        n = len(Rs)
        rev = {c: G[k]["rev"][c] for c in G[k]["rev"]}
        cost = G[k]["cost"]
        print(f"--- {k} (TB/trận) final=${sum(R['money_final'] for R in Rs)/n:.0f} "
              f"rev=${sum(sum(R['rev_channel'].values()) for R in Rs)/n:.0f} "
              f"cost=${sum(sum(R['cost_channel'].values()) for R in Rs)/n:.0f}")
        print("  REV :", {c: round(v) for c, v in sorted(rev.items(), key=lambda kv: -kv[1])})
        print("  COST:", {c: round(v) for c, v in sorted(cost.items(), key=lambda kv: -kv[1])})
    print("\n--- Đường tiền theo ngày (TB nhóm) ---")
    for k in ("TOP3", "V8"):
        m = G[k]["money"]
        print("%-5s " % k + " ".join("d%d:%.0f" % (d, m[d]) for d in range(0, 30, 3)))
