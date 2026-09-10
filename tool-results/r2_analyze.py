#!/usr/bin/env python3
"""ROUND 2 analysis over the god-replay logs (exact data). Answers Q1-Q5 + N1-N9."""
import json, sys, gc
from collections import Counter, defaultdict

SHED_ACCESS = {(4, 4), (5, 4), (4, 5), (5, 5)}
IT = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def day_of(t):
    return (t - 1) // 24


def hour_of(t):
    return (t - 1) % 24


def load_god(tag):
    return json.load(open(f"/home/z/my-project/tool-results/r2_god_{tag}.json"))


def analyze(tag, G):
    names = G["names"]
    R = []  # report lines
    P = lambda s="": R.append(s)

    P(f"########## {tag}: {names[0]} (p0) vs {names[1]} (p1) | rewards {G['rewards']}")

    # ---------- EXACT LEDGER ----------
    rev = {0: defaultdict(float), 1: defaultdict(float)}
    units = {0: defaultdict(int), 1: defaultdict(int)}
    seed_cost = {0: defaultdict(float), 1: defaultdict(float)}
    anim_cost = {0: defaultdict(float), 1: defaultdict(float)}
    buy_units = {0: defaultdict(int), 1: defaultdict(int)}
    buy_cost = {0: defaultdict(float), 1: defaultdict(float)}
    for t, p, op, item, price in G["commit_log"]:
        if op == "SELL":
            rev[p][item] += price
            units[p][item] += 1
        elif op == "BUY_SEED":
            seed_cost[p][item] += price
        elif op == "BUY_ANIMAL":
            anim_cost[p][item] += price
        elif op == "BUY_PRODUCT":
            buy_units[p][item] += 1
            buy_cost[p][item] += price
    hire_cost = {p: sum(h[2] for h in G["hire_log"] if h[1] == p) for p in (0, 1)}
    land_cost = {p: sum(l[3] for l in G["land_log"] if l[1] == p) for p in (0, 1)}

    P("\n== EXACT LEDGER (god replay, $) ==")
    hdr = f"{'channel':<12}" + "".join(f"{names[i][:11]:>26}" for i in (0, 1))
    P(hdr)
    for it in IT:
        r0, r1 = rev[0].get(it, 0), rev[1].get(it, 0)
        u0, u1 = units[0].get(it, 0), units[1].get(it, 0)
        if r0 or r1:
            P(f"{it:<12}" + f"{r0:>10.0f} ({u0:>4}u @{(r0/u0 if u0 else 0):>6.1f})".rjust(26)
              + f"{r1:>10.0f} ({u1:>4}u @{(r1/u1 if u1 else 0):>6.1f})".rjust(26))
    tot0 = sum(rev[0].values()); tot1 = sum(rev[1].values())
    P(f"{'TOTAL REV':<12}{tot0:>10.0f}{tot1:>26.0f}")
    P(f"{'seed cost':<12}{-sum(seed_cost[0].values()):>10.0f}  {dict(seed_cost[0])}{-sum(seed_cost[1].values()):>16.0f}  {dict(seed_cost[1])}")
    P(f"{'animal cost':<12}{-sum(anim_cost[0].values()):>10.0f}  {dict(anim_cost[0])}{-sum(anim_cost[1].values()):>16.0f}  {dict(anim_cost[1])}")
    P(f"{'buy WHEAT/FERT':<12}" + f"{-buy_cost[0].get('WHEAT',0):>10.0f} ({buy_units[0].get('WHEAT',0)}u) FERT {-buy_cost[0].get('FERTILIZER',0):.0f} ({buy_units[0].get('FERTILIZER',0)}u)"
      + f"{-buy_cost[1].get('WHEAT',0):>16.0f} ({buy_units[1].get('WHEAT',0)}u) FERT {-buy_cost[1].get('FERTILIZER',0):.0f} ({buy_units[1].get('FERTILIZER',0)}u)")
    P(f"{'hire cost':<12}{-hire_cost[0]:>10.0f}  ({len([h for h in G['hire_log'] if h[1]==0])} hires){-hire_cost[1]:>16.0f}  ({len([h for h in G['hire_log'] if h[1]==1])} hires)")
    P(f"{'land cost':<12}{-land_cost[0]:>10.0f}{-land_cost[1]:>26.0f}")

    # daily revenue
    daily_rev = {0: defaultdict(float), 1: defaultdict(float)}
    for t, p, op, item, price in G["commit_log"]:
        if op == "SELL":
            daily_rev[p][day_of(t)] += price

    # ---------- Q1: LIQUIDATION ----------
    P("\n== Q1: LIQUIDATION d27-29 (exact prices) ==")
    for p in (0, 1):
        sells_late = [(t, item, price) for t, pp, op, item, price in G["commit_log"]
                     if pp == p and op == "SELL" and day_of(t) >= 27]
        by_item = defaultdict(list)
        for t, item, price in sells_late:
            by_item[item].append((t, price))
        parts = []
        for it in sorted(by_item, key=lambda x: -sum(pr for _, pr in by_item[x])):
            ps = [pr for _, pr in by_item[it]]
            parts.append(f"{it}: {len(ps)}u ${sum(ps):.0f} (min ${min(ps)}, avg ${sum(ps)/len(ps):.0f})")
        P(f"  {names[p][:20]}: " + "; ".join(parts))
    last_snap = G["snapshots"][-1]
    P(f"  FINAL SHED (t=719, after last action d29h22): p0={last_snap['p0']['shed']} p1={last_snap['p1']['shed']}")
    lost0 = sum(sum(d.values()) for d in last_snap["p0"]["inv_carry"])
    lost1 = sum(sum(d.values()) for d in last_snap["p1"]["inv_carry"])
    P(f"  LOST in inventories at game end (no d29 end-of-day dump): p0={lost0}u p1={lost1}u "
      f"(detail p0={[d for d in last_snap['p0']['inv_carry'] if d]}, p1={[d for d in last_snap['p1']['inv_carry'] if d]})")
    # hourly sells on d29
    for p in (0, 1):
        hh = Counter()
        for t, pp, op, item, price in G["commit_log"]:
            if pp == p and op == "SELL" and day_of(t) == 29:
                hh[hour_of(t)] += 1
        P(f"  {names[p][:20]} d29 sells by hour: {dict(sorted(hh.items()))}")

    # ---------- Q2: FEED/CARE A/B ----------
    P("\n== Q2: FEED/CARE + milk per cow (exact) ==")
    for p in (0, 1):
        fed = defaultdict(int); cared = defaultdict(int)
        milk_harv = defaultdict(int); egg_harv = defaultdict(int); wool_harv = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] != p:
                continue
            d = day_of(u["t"])
            if "fed" in u:
                fed[d] += 1
            if "cared" in u:
                cared[d] += 1
            if "harvest" in u:
                what, n = u["harvest"]
                if what == "COW":
                    milk_harv[d] += n
                elif what == "GOOSE":
                    egg_harv[d] += n
                elif what == "SHEEP":
                    wool_harv[d] += n
        cows = {}
        for s in G["snapshots"]:
            cows[s["day"]] = s[f"p{p}"]["tiles"]["animals"].get("COW", 0)
        cow_days = sum(cows.get(d, 0) for d in range(8, 29))
        milk_total = sum(milk_harv.values())
        P(f"  {names[p][:20]}: FEED/day d8-28 avg {sum(v for k,v in fed.items() if 8<=k<=28)/21:.1f}, CARE/day {sum(v for k,v in cared.items() if 8<=k<=28)/21:.1f}")
        P(f"    milk harvested d8-28: {milk_total}u | cow-days {cow_days} | milk/cow/day {milk_total/max(1,cow_days):.2f}u | per prod-event(every 2d) {milk_total/max(1,cow_days*0.5):.2f}u")
        P(f"    egg harvested: {sum(egg_harv.values())}u, wool: {sum(wool_harv.values())}u")
        # feed style check: fed vs cows per day
        det = ", ".join(f"d{d}:{fed.get(d,0)}f/{cows.get(d,0)}c" for d in range(8, 29) if cows.get(d, 0))
        P(f"    fed/cows by day: {det}")

    # ---------- Q3: WHEAT CYCLE ----------
    P("\n== Q3: WHEAT CYCLE ==")
    for p in (0, 1):
        planted = defaultdict(int); harv = defaultdict(int); harv_units = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] != p:
                continue
            d = day_of(u["t"])
            if u.get("planted") == "WHEAT":
                planted[d] += 1
            if "harvest" in u and u["harvest"][0] == "WHEAT":
                harv[d] += 1
                harv_units[d] += u["harvest"][1]
        standing = {s["day"]: s[f"p{p}"]["tiles"]["crops"].get("WHEAT", 0) for s in G["snapshots"]}
        P(f"  {names[p][:20]}: total wheat planted {sum(planted.values())} tiles, harvested {sum(harv.values())} tiles / {sum(harv_units.values())}u "
          f"({sum(harv_units.values())/max(1,sum(harv.values())):.2f}u/tile)")
        d13_27_stand = [standing.get(d, 0) for d in range(13, 28)]
        P(f"    standing wheat d13-27 avg {sum(d13_27_stand)/15:.1f} | replant/day d8-26 avg {sum(v for k,v in planted.items() if 8<=k<=26)/19:.1f}")
        # per-day detail (plant, harvest, units, standing)
        det = ", ".join(f"d{d}:{planted.get(d,0)}p/{harv.get(d,0)}h/{harv_units.get(d,0)}u/s{standing.get(d,0)}" for d in range(0, 29) if planted.get(d) or harv.get(d))
        P(f"    day detail (plant/harv/units/standing): {det}")

    # ---------- Q4: GOOSE ECONOMICS ----------
    P("\n== Q4: GOOSE ECONOMICS ==")
    for p in (0, 1):
        geese = {s["day"]: s[f"p{p}"]["tiles"]["animals"].get("GOOSE", 0) for s in G["snapshots"]}
        atcap = {s["day"]: s[f"p{p}"]["tiles"]["animal_at_cap"].get("GOOSE", 0) for s in G["snapshots"]}
        eggs = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] == p and "harvest" in u and u["harvest"][0] == "GOOSE":
                eggs[day_of(u["t"])] += u["harvest"][1]
        fert = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] == p and "collect_fert" in u:
                fert[day_of(u["t"])] += 1
        gd = [(d, geese.get(d, 0)) for d in range(5, 29) if geese.get(d, 0)]
        if gd:
            goose_days = sum(g for _, g in gd)
            egg_total = sum(eggs.values())
            fert_total = sum(fert.values())
            P(f"  {names[p][:20]}: geese timeline {gd[:12]}{'...' if len(gd)>12 else ''}")
            P(f"    goose-days {goose_days} | eggs {egg_total} ({egg_total/goose_days:.2f}/goose/day) | fert collected {fert_total} ({fert_total/goose_days:.2f}/goose/day)")
            capd = sum(atcap.get(d, 0) for d, _ in gd)
            P(f"    days-tiles at EGG cap(4): {capd} | egg rev ${rev[p].get('EGG',0):.0f} + fert used/sold")
            # per goose ROI
            e_rev = rev[p].get("EGG", 0)
            P(f"    egg revenue total ${e_rev:.0f} -> per goose-day ${e_rev/goose_days:.2f} | fert: collected {fert_total}, sold {units[p].get('FERTILIZER',0)}, fertilized below")

    # ---------- Q5: ZERO-SUM ----------
    P("\n== Q5: ZERO-SUM (combined supply vs price) ==")
    sold_comb = defaultdict(lambda: defaultdict(int))  # item -> day -> units (both)
    for t, p, op, item, price in G["commit_log"]:
        if op == "SELL" and price > 1:
            sold_comb[item][day_of(t)] += 1
    for it in ("STRAWBERRY", "WHEAT", "MILK", "MELON", "EGG", "CARROT", "TOMATO"):
        days = sorted(set(list(sold_comb[it].keys())))
        if not days:
            continue
        # price at end of each day from snapshots
        px = {}
        for s in G["snapshots"]:
            px.setdefault(s["day"], s["prices"][it])
        seg = ", ".join(f"d{d}:{sold_comb[it].get(d,0)}u@${px.get(d,'?')}" for d in range(0, 30)
                        if sold_comb[it].get(d, 0) or (d % 4 == 0 and px.get(d)))
        P(f"  {it}: combined-sold/day + EOD price: {seg}")

    # ---------- N2: MONEY CURVE ----------
    P("\n== N2: MONEY CURVE (end of day, diff) ==")
    mday = {s["day"]: s["money"] for s in G["snapshots"]}
    for d in range(0, 30):
        if d in mday:
            m = mday[d]
            P(f"  d{d:>2}: {names[0][:12]:<12}{m[0]:>8.0f}  {names[1][:12]:<12}{m[1]:>8.0f}  diff {m[1]-m[0]:>+8.0f}")

    # ---------- N5: FERT FLOW ----------
    P("\n== N5: FERT ALLOCATION ==")
    for p in (0, 1):
        coll = defaultdict(int); fertz = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] != p:
                continue
            if "collect_fert" in u:
                coll[day_of(u["t"])] += 1
            if "fertilized" in u:
                fertz[day_of(u["t"])] += 1
        P(f"  {names[p][:20]}: collected {sum(coll.values())} | fertilized {sum(fertz.values())} | sold {units[p].get('FERTILIZER',0)} | bought {buy_units[p].get('FERTILIZER',0)}")
        P(f"    fertilize by day: {dict(sorted(fertz.items()))}")

    # ---------- N8: WATER ----------
    P("\n== N8: WATER DISCIPLINE ==")
    for p in (0, 1):
        wat = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] == p and "watered" in u:
                wat[day_of(u["t"])] += 1
        standing_all = defaultdict(int)
        for s in G["snapshots"]:
            standing_all[s["day"]] = sum(s[f"p{p}"]["tiles"]["crops"].values())
        det = ", ".join(f"d{d}:{wat.get(d,0)}/{standing_all.get(d,0)}" for d in range(1, 29) if standing_all.get(d))
        P(f"  {names[p][:20]} watered/standing by day: {det}")

    # ---------- unit command volume ----------
    P("\n== LABOR (effective unit events) ==")
    for p in (0, 1):
        c = Counter()
        for u in G["unit_log"]:
            if u["p"] == p:
                c[u["cmd"]] += 1
        P(f"  {names[p][:20]}: {dict(c.most_common())}")

    # ---------- harvest yields by crop ----------
    P("\n== HARVEST FLOWS (units by product, exact) ==")
    for p in (0, 1):
        flows = defaultdict(int); tiles_h = defaultdict(int)
        for u in G["unit_log"]:
            if u["p"] == p and "harvest" in u:
                what, n = u["harvest"]
                flows[what] += n
                tiles_h[what] += 1
        P(f"  {names[p][:20]}: " + ", ".join(f"{k}:{v}u/{tiles_h[k]}tiles" for k, v in sorted(flows.items())))

    return R


def raw_actions_analysis(tag, path, god_hires):
    """Parse raw replay actions: requested orders, command-by-hour histogram."""
    data = json.load(open(path))
    names = [a["Name"] for a in data["info"]["Agents"]]
    R = []
    P = R.append
    P(f"\n########## {tag} RAW ACTIONS: {names}")
    order_req = {0: Counter(), 1: Counter()}     # (op,item) -> units requested
    order_req_cnt = {0: Counter(), 1: Counter()}  # orders count
    hour_hist = {0: defaultdict(Counter), 1: defaultdict(Counter)}  # hour -> cmd -> count
    norders_step = {0: Counter(), 1: Counter()}
    for t in range(1, 720):
        day, hour = (t - 1) // 24, (t - 1) % 24
        for p in (0, 1):
            act = data["steps"][t][p].get("action") or {}
            mkt = act.get("market", []) or []
            norders_step[p][len(mkt)] += 1
            for mo in mkt:
                if isinstance(mo, list) and len(mo) >= 3 and mo[0] in ("SELL", "BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL"):
                    order_req[p][(mo[0], mo[1])] += mo[2] if isinstance(mo[2], int) else 0
                    order_req_cnt[p][(mo[0], mo[1])] += 1
            fa = act.get("farmer", [])
            if isinstance(fa, str):
                fa = [fa]
            hh = hour_hist[p][hour]
            if fa:
                hh[fa[0] if isinstance(fa[0], str) else "?"] += 1
            for ha in act.get("hands", []) or []:
                if isinstance(ha, str):
                    hh[ha] += 1
                elif isinstance(ha, list) and ha:
                    hh[ha[0] if isinstance(ha[0], str) else "?"] += 1
    for p in (0, 1):
        P(f"  {names[p][:20]} requested orders (units): " +
          "; ".join(f"{op[0]} {op[1][:5]}:{v}" for op, v in sorted(order_req[p].items())))
        P(f"    orders-per-step histogram: {dict(sorted(norders_step[p].items()))}")
        # hire hours (true)
        hh = Counter()
        for h in god_hires[p]:
            hh[hour_of(h[0])] += 1
        P(f"    hires by TRUE hour: {dict(sorted(hh.items()))}")
    # hour profile aggregated across players: MOVE vs WORK split
    for p in (0, 1):
        rows = []
        for h in range(24):
            c = hour_hist[p].get(h, {})
            moves = sum(v for k, v in c.items() if k in ("NORTH", "SOUTH", "EAST", "WEST"))
            work = sum(v for k, v in c.items() if k not in ("NORTH", "SOUTH", "EAST", "WEST", "PASS"))
            rows.append(f"h{h:>2}:M{moves:>3}/W{work:>3}")
        P(f"  {names[p][:20]} hourly MOVE/WORK: " + " ".join(rows))
        top_cmds = Counter()
        for h in hour_hist[p]:
            top_cmds.update(hour_hist[p][h])
        P(f"    cmd totals: {dict(top_cmds.most_common(14))}")
    return R


def main():
    out = []
    for tag in ("M1", "M2"):
        G = load_god(tag)
        out += analyze(tag, G)
        gc.collect()
    for tag, path in [("M1", "/home/z/my-project/upload/107559251.json"),
                      ("M2", "/home/z/my-project/upload/107573831.json")]:
        G = load_god(tag)
        god_hires = {0: [h for h in G["hire_log"] if h[1] == 0],
                    1: [h for h in G["hire_log"] if h[1] == 1]}
        del G
        out += raw_actions_analysis(tag, path, god_hires)
        gc.collect()
    with open("/home/z/my-project/tool-results/r2_report.txt", "w") as f:
        f.write("\n".join(out))
    print(f"wrote r2_report.txt ({len(out)} lines)")


if __name__ == "__main__":
    main()
