#!/usr/bin/env python3
"""PHASE 5B (Task 45) — EXACT market ledger analysis from god replays.

Uses r2_god_M1/M2.json (top-3) + /tmp/god_v8p_*.json (v8 vs v7, 0-mismatch).
Answers: A4 (thời điểm bán + tấn công thị trường) + A5 (90k-110k từ đâu).
"""
import json
import glob
from collections import defaultdict

PROD = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def load_god(path, fmt):
    d = json.load(open(path))
    # commit: [t, player, op, item, price]
    def dh(t):
        return ((t - 1) // 24, (t - 1) % 24) if fmt == "kaggle" else (t // 24, t % 24)
    out = {
        "file": path.split("/")[-1], "names": d["names"], "final": d.get("rewards") or d["final_money_sim"],
        "commits": [], "hires": d.get("hire_log", []), "lands": d.get("land_log", []),
        "buys": [], "sells": [], "rev": defaultdict(float), "cost": defaultdict(float),
        "rev_day": defaultdict(float), "sell_hour": defaultdict(int),
        "sell_hour_units": defaultdict(int), "buy_wheat": [], "final_sim": d["final_money_sim"],
    }
    for (t, p, op, item, price) in d["commit_log"]:
        day, hour = dh(t)
        rec = {"t": t, "d": day, "h": hour, "p": p, "op": op, "it": item, "pr": price}
        out["commits"].append(rec)
        if op == "SELL":
            out["sells"].append(rec)
            out["rev"][item] += price
            out["rev_day"][day] += price
            out["sell_hour"][hour] += 1
            out["sell_hour_units"][hour] += 1 if False else 1
        elif op in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL"):
            out["buys"].append(rec)
            out["cost"]["%s:%s" % (op, item)] += price
    for (t, p, cost, n) in out["hires"]:
        out["cost"]["HIRE"] += cost
    for (t, p, q, cost) in out["lands"]:
        out["cost"]["LAND"] += cost
    return out


def agg(gods, pidx, key):
    """Aggregate one player's exact ledger over games."""
    rev = defaultdict(float)
    cost = defaultdict(float)
    sell_hour = defaultdict(int)
    rev_day = defaultdict(float)
    sell_p = defaultdict(lambda: defaultdict(list))  # item -> hour -> [prices]
    buys_w = 0.0
    n = 0
    final = 0.0
    for g in gods:
        n += 1
        final += (g["final"][pidx] or 0)
        for it, v in g["rev"].items() if False else ():
            pass
    # simpler: recompute per player
    for g in gods:
        for c in g["commits"]:
            if c["p"] != pidx:
                continue
            if c["op"] == "SELL":
                rev[c["it"]] += c["pr"]
                sell_hour[c["h"]] += 1
                rev_day[c["d"]] += c["pr"]
                sell_p[c["it"]][c["h"]].append(c["pr"])
            elif c["op"] in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL"):
                cost["%s:%s" % (c["op"].replace("BUY_", ""), c["it"])] += c["pr"]
    for g in gods:
        for (t, p, costv, nn) in g["hires"]:
            if p == pidx:
                cost["HIRE"] += costv
        for (t, p, q, costv) in g["lands"]:
            if p == pidx:
                cost["LAND"] += costv
    ng = len(gods)
    return {"rev": {k: v / ng for k, v in rev.items()},
            "cost": {k: v / ng for k, v in cost.items()},
            "sell_hour": {k: v / ng for k, v in sell_hour.items()},
            "rev_day": {k: v / ng for k, v in rev_day.items()},
            "sell_p": sell_p, "final": final / ng, "n": ng}


if __name__ == "__main__":
    T3 = [load_god("/home/z/my-project/tool-results/r2_god_M1.json", "kaggle"),
          load_god("/home/z/my-project/tool-results/r2_god_M2.json", "kaggle")]
    V8G = []
    V7G = []
    for path in sorted(glob.glob("/tmp/god_v8p_*.json")):
        d = load_god(path, "arena")
        V8G.append(d)
        V7G.append(d)

    print("=== T3 games final:", [g["final"] for g in T3])
    print("=== V8 games final (seatA + seatB reversed):",
          [g["final"] for g in V8G])

    A = {}
    for label, gods, pidx in (("TOP3", T3 + T3, None),):
        pass
    # TOP3: both players in both games are top-3 -> aggregate all 4 seats
    top3_traces = []
    for g in T3:
        for p in (0, 1):
            top3_traces.append((g, p))
    # v8 = seat A in seatA files (p0), seat B in seatB files (p1)
    v8_traces, v7_traces = [], []
    for g in V8G:
        v8_traces.append((g, 0 if "seatA" in g["file"] else 1))
        v7_traces.append((g, 1 if "seatA" in g["file"] else 0))

    def agg2(traces):
        rev = defaultdict(float)
        cost = defaultdict(float)
        sell_hour = defaultdict(int)
        rev_day = defaultdict(float)
        final = 0.0
        sell_px = defaultdict(list)
        for (g, p) in traces:
            final += (g["final"][p] or 0)
            for c in g["commits"]:
                if c["p"] != p:
                    continue
                if c["op"] == "SELL":
                    rev[c["it"]] += c["pr"]
                    sell_hour[c["h"]] += 1
                    rev_day[c["d"]] += c["pr"]
                    sell_px[c["it"]].append(c["pr"])
                elif c["op"] in ("BUY_PRODUCT", "BUY_SEED", "BUY_ANIMAL"):
                    cost["%s:%s" % (c["op"].replace("BUY_", ""), c["it"])] += c["pr"]
            for (t, hp, costv, nn) in g["hires"]:
                if hp == p:
                    cost["HIRE"] += costv
            for (t, lp, q, costv) in g["lands"]:
                if lp == p:
                    cost["LAND"] += costv
        n = len(traces)
        return {"rev": {k: v / n for k, v in rev.items()},
                "cost": {k: v / n for k, v in cost.items()},
                "sell_hour": {k: v / n for k, v in sell_hour.items()},
                "rev_day": {k: v / ng for k, v in rev_day.items()} if False else
                {k: v / n for k, v in rev_day.items()},
                "sell_px": sell_px, "final": final / n, "n": n}

    G = {"TOP3": agg2(top3_traces), "V8": agg2(v8_traces), "V7": agg2(v7_traces)}

    print("\n================ A5. PHÂN RÃ TIỀN (EXACT god-ledger) ================")
    for k in ("TOP3", "V8", "V7"):
        g = G[k]
        tot_rev = sum(g["rev"].values())
        tot_cost = sum(g["cost"].values())
        print(f"--- {k}: final=${g['final']:.0f}  rev=${tot_rev:.0f}  cost=${tot_cost:.0f}  "
              f"(3000+rev-cost=${3000+tot_rev-tot_cost:.0f})")
        print("  REV :", {c: round(v) for c, v in sorted(g["rev"].items(), key=lambda kv: -kv[1])})
        print("  COST:", {c: round(v) for c, v in sorted(g["cost"].items(), key=lambda kv: -kv[1])})

    print("\n================ A4. GIỜ BÁN (lệnh SELL/trận) ================")
    for k in ("TOP3", "V8"):
        g = G[k]
        tot = sum(g["sell_hour"].values())
        print(f"--- {k}: {tot:.0f} lệnh SELL/trận")
        print("  " + " ".join("h%d:%2d%%" % (h, round(100 * c / tot))
                               for h, c in sorted(g["sell_hour"].items())))

    print("\n================ A4b. GIÁ BÁN TB THEO KÊNH (exact) ================")
    print("%-12s %-24s %-24s" % ("kênh", "TOP3 u/avg$/rev$", "V8 u/avg$/rev$"))
    for it in PROD:
        def st(g):
            px = g["sell_px"][it]
            return len(px), (sum(px) / len(px) if px else 0), g["rev"].get(it, 0)
        print("%-12s %-24s %-24s" % (it,
              "%4d/%3.1f/%6.0f" % st(G["TOP3"]),
              "%4d/%3.1f/%6.0f" % st(G["V8"])))

    print("\n================ A5b. DOANH THU THEO NGÀY (TB/trận) ================")
    for k in ("TOP3", "V8", "V7"):
        rd = G[k]["rev_day"]
        print(f"--- {k}")
        print("  " + " ".join("d%d:%.0f" % (d, rd.get(d, 0)) for d in range(0, 30, 2)))

    # pickle for further analysis
    import pickle
    pickle.dump({"G": G, "T3": T3, "V8G": V8G}, open("/tmp/phase5b.pkl", "wb"))
    print("\nwrote /tmp/phase5b.pkl")
