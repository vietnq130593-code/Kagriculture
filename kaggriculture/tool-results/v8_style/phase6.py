#!/usr/bin/env python3
"""PHASE 6 (Task 46) — yêu cầu user:
  B1: so sánh lượng MUA + DUY TRË bò(COW)/cừu(SHEEP)/ngỗng(GOOSE=*"vịt") giữa v8 vs top-3
  B2: điều tra nguyên nhân tiền cuối trận 90k-110k của top-3
     (money-flow từng ngày: thu/chi/theo loại, khi nào ngừng capex, tích lũy bao lâu)

Sources (EXACT, 0-mismatch god replay):
  TOP3: tool-results/r2_god_M1.json, r2_god_M2.json  (kaggle: day=(t-1)//24)
  V8:   new45/*.jsonl + /tmp/god45_v8n_*.json          (arena:  day=t//24)

Convention fed/care flags:
  kaggle snapshot(h) = post-action(h)     -> đo fed tại h22 (thấy feed h0..h22)
  arena record(h)    = pre-action(h)      -> đo fed tại h23 (thấy feed h0..h22)
  end-of-day d state (kaggle) = snapshot h23 / (arena) = record (d+1,h0)
"""
import json
import glob
from collections import defaultdict

SP = ("COW", "SHEEP", "GOOSE")
PROD_OF = {"COW": "MILK", "SHEEP": "WOOL", "GOOSE": "EGG"}
COST = {"COW": 400, "SHEEP": 500, "GOOSE": 300}
VN = {"COW": "bò", "SHEEP": "cừu", "GOOSE": "ngỗng"}


# ------------------------------------------------------------------ TOP3 --
def top3_trace(path, pidx):
    d = json.load(open(path))
    dh = lambda t: ((t - 1) // 24, (t - 1) % 24)  # kaggle
    T = {"name": d["names"][pidx], "src": path.split("/")[-1], "final": d["rewards"][pidx],
         "buys": defaultdict(lambda: defaultdict(int)),   # sp -> day -> n
         "cnt": {}, "fed": {}, "esc": defaultdict(int),
         "money": {}, "rev_day": defaultdict(float),
         "spend_day": defaultdict(lambda: defaultdict(float)),
         "rev_ch": defaultdict(float), "shed_end": {}, "units_end": 0,
         "hire_days": set(), "land_days": []}
    for (t, p, op, item, price) in d["commit_log"]:
        day, h = dh(t)
        if p != pidx:
            continue
        if op == "SELL":
            T["rev_day"][day] += price
            T["rev_ch"][item] += price
        elif op == "BUY_ANIMAL":
            T["buys"][item][day] += 1
            T["spend_day"][day]["ANIMAL"] += price
        elif op == "BUY_SEED":
            T["spend_day"][day]["SEED"] += price
        elif op == "BUY_PRODUCT":
            T["spend_day"][day]["BUY:" + item] += price
    for (t, p, cost, n) in d["hire_log"]:
        if p == pidx:
            T["spend_day"][dh(t)[0]]["HIRE"] += cost
            T["hire_days"].add(dh(t)[0])
    for (t, p, q, cost) in d["land_log"]:
        if p == pidx:
            T["spend_day"][dh(t)[0]]["LAND"] += cost
            T["land_days"].append((dh(t)[0], q, cost))
    # daily species counts + fed (h22) from snapshots
    prev = {s: 0 for s in SP}
    for snap in d["snapshots"]:
        day, h = snap["day"], snap["hour"]
        tl = snap["p%d" % pidx]["tiles"]
        if h == 22:
            T["fed"][day] = dict(tl.get("animal_fed") or {})
        if h == 23 or (day == 29 and h >= 22):
            T["cnt"][day] = dict(tl.get("animals") or {})
            cur = T["cnt"][day]
            for s in SP:
                if cur.get(s, 0) < prev.get(s, 0):
                    T["esc"][s] += prev.get(s, 0) - cur.get(s, 0)
                prev[s] = cur.get(s, 0)
            T["money"][day] = snap["money"][pidx]
        if day == 29 and h == 22:
            T["shed_end"] = dict(snap["p%d" % pidx]["shed"])
            T["units_end"] = 1 + len(snap["p%d" % pidx].get("hands") or [])
    # fill d29 if h23 snapshot absent
    if 29 not in T["money"]:
        last = [s for s in d["snapshots"] if s["day"] == 29][-1]
        T["money"][29] = last["money"][pidx]
        T["cnt"][29] = dict(last["p%d" % pidx]["tiles"].get("animals") or {})
        T["shed_end"] = dict(last["p%d" % pidx]["shed"])
    return T


# -------------------------------------------------------------------- V8 --
def v8_trace(jsonl, god, pidx):
    T = {"name": "v8", "src": jsonl.split("/")[-1], "final": None,
         "buys": defaultdict(lambda: defaultdict(int)),
         "cnt": {}, "fed": {}, "cared": {}, "cb": {}, "esc": defaultdict(int),
         "money": {}, "rev_day": defaultdict(float),
         "spend_day": defaultdict(lambda: defaultdict(float)),
         "rev_ch": defaultdict(float), "shed_end": {}, "units_end": 0,
         "hire_days": set(), "land_days": []}
    g = json.load(open(god))
    T["final"] = g["final_money_sim"][pidx]
    dh = lambda t: (t // 24, t % 24)  # arena
    for (t, p, op, item, price) in g["commit_log"]:
        day, h = dh(t)
        if p != pidx:
            continue
        if op == "SELL":
            T["rev_day"][day] += price
            T["rev_ch"][item] += price
        elif op == "BUY_ANIMAL":
            T["buys"][item][day] += 1
            T["spend_day"][day]["ANIMAL"] += price
        elif op == "BUY_SEED":
            T["spend_day"][day]["SEED"] += price
        elif op == "BUY_PRODUCT":
            T["spend_day"][day]["BUY:" + item] += price
    for (t, p, cost, n) in g["hire_log"]:
        if p == pidx:
            T["spend_day"][dh(t)[0]]["HIRE"] += cost
            T["hire_days"].add(dh(t)[0])
    for (t, p, q, cost) in g["land_log"]:
        if p == pidx:
            T["spend_day"][dh(t)[0]]["LAND"] += cost
            T["land_days"].append((dh(t)[0], q, cost))

    turns = []
    with open(jsonl) as f:
        for line in f:
            rec = json.loads(line)
            if rec.get("t") == "turn":
                turns.append(rec)
            elif rec.get("t") == "end":
                end = rec
    # scan tiles: fed at h23-pre (covers h0..h22), end-of-day at (d+1,h0)-pre
    prev = {s: 0 for s in SP}
    for i, rec in enumerate(turns):
        day, h = rec["day"], rec["hour"]
        farm = rec["farms"][pidx]
        if h == 23 and day <= 28:
            fed = defaultdict(int)
            for row in farm["tiles"]:
                for t_ in row:
                    if isinstance(t_, dict) and t_.get("kind") in ("COOP", "PASTURE") \
                            and t_.get("animal"):
                        if t_.get("fed_today"):
                            fed[t_["animal"]] += 1
            T["fed"][day] = dict(fed)
        if h == 0 and day >= 1:
            cnt = defaultdict(int)
            for row in farm["tiles"]:
                for t_ in row:
                    if isinstance(t_, dict) and t_.get("kind") in ("COOP", "PASTURE") \
                            and t_.get("animal"):
                        cnt[t_["animal"]] += 1
            T["cnt"][day - 1] = dict(cnt)
            for s in SP:
                if cnt.get(s, 0) < prev.get(s, 0):
                    T["esc"][s] += prev.get(s, 0) - cnt.get(s, 0)
                prev[s] = cnt.get(s, 0)
            T["money"][day - 1] = farm["money"]
    # final record = end of d29
    lastf = turns[-1]["farms"][pidx]
    cnt = defaultdict(int)
    fed = defaultdict(int)
    cared = defaultdict(int)
    cbs = []
    for row in lastf["tiles"]:
        for t_ in row:
            if isinstance(t_, dict) and t_.get("kind") in ("COOP", "PASTURE") and t_.get("animal"):
                cnt[t_["animal"]] += 1
                if t_.get("fed_today"):
                    fed[t_["animal"]] += 1
                if t_.get("cared_today"):
                    cared[t_["animal"]] += 1
                cbs.append(t_.get("pending_care_bonus") or 0)
    T["cnt"][29] = dict(cnt)
    T["money"][29] = lastf["money"]
    T["shed_end"] = dict(lastf.get("shed") or {})
    T["units_end"] = 1 + len(lastf.get("hands") or [])
    return T


# --------------------------------------------------------------- helpers --
def species_days(T):
    out = {s: 0 for s in SP}
    for day, cnt in T["cnt"].items():
        for s in SP:
            out[s] += cnt.get(s, 0)
    return out


def fed_coverage(T):
    """avg over days with species>0 of fed/count (measured h22-window)."""
    out = {s: [] for s in SP}
    for day, fed in T["fed"].items():
        cnt = T["cnt"].get(day) or {}
        for s in SP:
            if cnt.get(s, 0) > 0:
                out[s].append(fed.get(s, 0) / cnt[s])
    return {s: (sum(v) / len(v) if v else None) for s, v in out.items()}


def grp_species(traces):
    n = len(traces)
    out = {}
    for s in SP:
        tot_bought = sum(sum(T["buys"][s].values()) for T in traces) / n
        ad = sum(species_days(T)[s] for T in traces) / n
        peak = max((T["cnt"].get(d, {}).get(s, 0) for T in traces for d in T["cnt"]), default=0)
        esc = sum(T["esc"][s] for T in traces) / n
        rev = sum(T["rev_ch"].get(PROD_OF[s], 0) for T in traces) / n
        cov = [fed_coverage(T)[s] for T in traces]
        cov = [c for c in cov if c is not None]
        first = min((min(T["buys"][s]) for T in traces if T["buys"][s]), default=None)
        lastb = max((max(T["buys"][s]) for T in traces if T["buys"][s]), default=None)
        end_cnt = sum(T["cnt"].get(29, {}).get(s, 0) for T in traces) / n
        out[s] = {"bought": tot_bought, "first": first, "last": lastb, "animal_days": ad,
                  "peak": peak, "esc": esc, "rev": rev, "cov": sum(cov) / len(cov) if cov else None,
                  "end": end_cnt,
                  "rev_per_ad": (rev / ad) if ad else 0,
                  "breakeven": (COST[s] / (rev / ad)) if ad and rev else None}
    return out

def money_flow(T):
    days = sorted(T["money"])
    M = {d: T["money"][d] for d in days}
    lastA = max([max(T["buys"][s]) for s in SP if T["buys"][s]] or [0])
    lastL = max([d for (d, q, c) in T["land_days"]] or [0])
    lastH = max(T["hire_days"] or [0])
    rev7 = sum(T["rev_day"][d] for d in range(23, 30)) / 7
    sp7 = defaultdict(float)
    for d in range(23, 30):
        for c, v in T["spend_day"].get(d, {}).items():
            sp7[c] += v / 7
    net_after = M[29] - M.get(lastA, 0)
    tot_rev = sum(T["rev_day"].values())
    tot_spend = sum(sum(c.values()) for c in T["spend_day"].values())
    return {"lastA": lastA, "lastL": lastL, "lastH": lastH,
            "m_at_lastA": M.get(lastA), "net_after_lastA": net_after,
            "rev7": rev7, "sp7": dict(sp7),
            "tot_rev": tot_rev, "tot_spend": tot_spend,
            "rev_last10": sum(T["rev_day"][d] for d in range(20, 30)),
            "net_d15_29": M[29] - M.get(15, M[29]),
            "M": M, "rev_day": dict(T["rev_day"]),
            "spend": {d: dict(v) for d, v in T["spend_day"].items()}}


# --------------------------------------------------------------- report --
if __name__ == "__main__":
    T3 = [top3_trace("/home/z/my-project/tool-results/r2_god_M1.json", p) for p in (0, 1)] + \
         [top3_trace("/home/z/my-project/tool-results/r2_god_M2.json", p) for p in (0, 1)]
    V8 = []
    for p in sorted(glob.glob("/tmp/god46_v8n_*.json")):
        j = p.replace("/tmp/god46_", "/home/z/my-project/tool-results/v8_style/new46/") \
             .replace("god46_", "").replace(".json", ".jsonl")
        seatA = "seatA" in p
        V8.append(v8_trace(j, p, 0 if seatA else 1))

    print("=" * 100)
    print("B1. LOÀI: MUA + DUY TRÌ bò/cừu/ngỗng — TOP3 (4 seat) vs V8 vòng45 (6 game)")
    print("=" * 100)
    for lab, G in (("TOP3", T3), ("V8", V8)):
        print(f"\n### {lab}")
        for T in G:
            sp = species_days(T)
            print("  %-22s %-14s final=$%6.0f | mua %s | AD %s | trốn %s" % (
                T["name"], T["src"][:14], T["final"],
                {VN[s]: sum(T["buys"][s].values()) for s in SP},
                {VN[s]: sp[s] for s in SP},
                {VN[s]: T["esc"][s] for s in SP}))
        S = grp_species(G)
        print("  -- TB nhóm --")
        for s in SP:
            print("  %-5s mua TB %4.1f con (d%s→d%s) | AD %5.0f | peak %2.0f | "
                  "trốn %3.1f | rev $%5.0f | rev/AD $%4.2f | feed-cov %s | end %4.1f | BE %4.1f ngày" % (
                s, S[s]["bought"], S[s]["first"], S[s]["last"], S[s]["animal_days"],
                S[s]["peak"], S[s]["esc"], S[s]["rev"], S[s]["rev_per_ad"],
                ("%.0f%%" % (100 * S[s]["cov"])) if S[s]["cov"] is not None else "-",
                S[s]["end"], S[s]["breakeven"] if S[s]["breakeven"] is not None else -1))

    print("\n--- Đàn theo loài mỗi ngày (TB nhóm: bò/cừu/ngỗng) ---")
    for lab, G in (("TOP3", T3), ("V8", V8)):
        n = len(G)
        print(f"### {lab}")
        for d in range(0, 30, 2):
            row = []
            for s in SP:
                v = sum(T["cnt"].get(d, {}).get(s, 0) for T in G) / n
                row.append("%s:%4.1f" % (VN[s], v))
            print("  d%-2d %s" % (d, "  ".join(row)))

    print("\n--- NGÀY MUA THEO LOÀI (TB nhóm: số con mua mỗi 2 ngày) ---")
    for lab, G in (("TOP3", T3), ("V8", V8)):
        n = len(G)
        print(f"### {lab}")
        for d in range(0, 30, 2):
            row = []
            for s in SP:
                v = sum(T["buys"][s].get(d, 0) + T["buys"][s].get(d + 1, 0) for T in G) / n
                row.append("%s:+%3.1f" % (VN[s], v))
            print("  d%-2d %s" % (d, "  ".join(row)))

    print("\n" + "=" * 100)
    print("B2. DÒNG TIỀN: VÌ SAO TOP3 LUÔN ĐỌNG 90k-110k CUỐI TRẬN")
    print("=" * 100)
    for lab, G in (("TOP3", T3), ("V8", V8)):
        print(f"\n### {lab}")
        for T in G:
            F = money_flow(T)
            print("  %-22s final=$%6.0f | rev $%6.0f − spend $%5.0f | mua thú cuối d%2d (dư $%5.0f) "
                  "| LAND xong d%2d | HIRE cuối d%2d | sau-mua-cuối +$%5.0f (%.0f%% final) "
                  "| rev 10 ngày cuối $%5.0f" % (
                T["name"], T["final"], F["tot_rev"], F["tot_spend"], F["lastA"],
                F["m_at_lastA"] or 0, F["lastL"], F["lastH"], F["net_after_lastA"],
                100 * F["net_after_lastA"] / max(1, T["final"]), F["rev_last10"]))
        # group avg money curve + rev/spend rate
        n = len(G)
        print("  -- TB nhóm --")
        curve = " ".join("d%d:%.0f" % (d, sum(T["money"].get(d, 0) for T in G) / n)
                         for d in range(0, 30, 3))
        print("  money:", curve)
        revr = " ".join("d%d:%.0f" % (d, sum(T["rev_day"][d] for T in G) / n)
                        for d in range(0, 30, 3))
        print("  rev/ngày:", revr)
        sp7 = defaultdict(float)
        for T in G:
            F = money_flow(T)
            for c, v in F["sp7"].items():
                sp7[c] += v / n
        print("  chi 7 ngày cuối (TB/ngày):", {c: round(v) for c, v in sorted(sp7.items())})
        F = money_flow(G[0])
        print("  (thí dụ %s spend theo ngày:)" % G[0]["name"])
        for d in sorted(G[0]["spend_day"]):
            if d % 3 == 0 or d > 26:
                print("    d%-2d %s" % (d, {c: round(v) for c, v in sorted(G[0]["spend_day"][d].items())}))

    print("\n--- CHI THEO LOẠI CỘNG DỒN (TB/trận) ---")
    for lab, G in (("TOP3", T3), ("V8", V8)):
        n = len(G)
        cats = ("ANIMAL", "LAND", "HIRE", "SEED")
        tot = {c: sum(sum(T["spend_day"][d].get(c, 0) for d in T["spend_day"]) for T in G) / n
               for c in cats}
        buyp = defaultdict(float)
        for T in G:
            for d, cats_ in T["spend_day"].items():
                for c, v in cats_.items():
                    if c.startswith("BUY:"):
                        buyp[c] += v / n
        print("%-5s" % lab, {c: round(v) for c, v in tot.items()}, "+ mua SP:",
              {c: round(v) for c, v in sorted(buyp.items())})

    print("\n--- Shed cuối trận (hàng chưa bán, TB nhóm) ---")
    for lab, G in (("TOP3", T3), ("V8", V8)):
        n = len(G)
        keys = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
        vals = {k: sum(T["shed_end"].get(k, 0) for T in G) / n for k in keys}
        print("%-5s" % lab, {k: round(v, 1) for k, v in vals.items() if v},
              "| units cuối:", round(sum(T["units_end"] for T in G) / n, 1))

    import pickle
    pickle.dump({"T3": T3, "V8": V8}, open("/tmp/phase6.pkl", "wb"))
    print("\nwrote /tmp/phase6.pkl")
