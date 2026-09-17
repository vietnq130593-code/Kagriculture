# ============================================================================
#  P0 — KIỂM ĐỊNH 3 GIẢ THUYẾT CỦA RESEARCH_v4.md v2.0 (hạng P0, mục 11)
#
#  (1) TELEMETRY:  opp_net[p] = Δinv[p] + drain_est[p] − my_sells(>$1)[p]
#                  + my_buys[p]   — đối chiếu ground-truth instrument từng step
#                  (kỳ vọng: 7/9 mặt hàng khớp 100%; WHEAT/FERT đúng net-flow;
#                   dump chạm sàn $1 là "tàng hình" — đo đếm riêng)
#  (2) LEDGER:     phân rã toàn bộ dòng tiền theo 6 hạng mục
#                  (labor / seeds / animals / land / feed / fertbuy) + revenue,
#                  khớp sổ: final_money − 3000 == revenue − chi phí (±$0)
#  (3) BẪY T8:     10 trận mirror v3-vs-v3 — công thức presence đối xứng
#                  (milk_room = absorb − 30×opp_COW − 40) có tự triệt đàn nhau
#                  đến mức nào; đo đàn bò theo ngày, milk/wool bán ra, giá,
#                  và "premium bỏ lại trên bàn" so với drain 324u.
#
#  Chạy:  cd /home/z/my-project/kaggriculture && python3 bench/p0.py
#  Kết quả: bench/p0_results.json + tóm tắt stdout
# ============================================================================
import sys
import time
import json
from collections import defaultdict

sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')

from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as eng

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
            "EGG", "MILK", "WOOL", "FERTILIZER"]
BUYABLE = {"WHEAT", "FERTILIZER"}
I0 = 10000

V3A = "bench/v3_a.py"
V3B = "bench/v3_b.py"
V2 = "bench/baseline.py"


# ---------------------------------------------------------------------------
#  INSTRUMENTATION (monkeypatch engine)
# ---------------------------------------------------------------------------
class Inst:
    txns = []        # (step, player, op, item, price) — mọi unit commit
    hires = []       # (step, player, cost)
    lands = []       # (step, player, cost)
    inv_start = {}   # step -> {item: inv}   (lúc vào _process_market)
    inv_end = {}     # step -> {item: inv}   (sau _town_consume)
    drain_gt = {}    # step -> {item: units hút}
    drain_est = {}   # step -> {item: units} tính từ public town (như v4 sẽ làm)
    prices = {}      # step -> {item: price} đầu step
    herds = {}       # step -> [{animal: n}, {animal: n}]
    money = {}       # step -> [m0, m1]
    curmap = {}      # id(farm) -> player
    step = -1

    @classmethod
    def reset(cls):
        cls.txns = []
        cls.hires = []
        cls.lands = []
        cls.inv_start = {}
        cls.inv_end = {}
        cls.drain_gt = {}
        cls.drain_est = {}
        cls.prices = {}
        cls.herds = {}
        cls.money = {}
        cls.curmap = {}
        cls.step = -1


_orig_commit = eng._commit_unit
_orig_pm = eng._process_market
_orig_hire = eng._do_hire
_orig_land = eng._do_buy_land
_orig_town = eng._town_consume


def _pid(farm):
    return Inst.curmap.get(id(farm), -1)


def _w_commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    if ok:
        Inst.txns.append((Inst.step, _pid(farm), op, item, price))
    return ok


def _w_hire(farm, private, board_size, mult=eng.FARM_HAND_COST_MULT):
    before = farm["money"]
    r = _orig_hire(farm, private, board_size, mult)
    if farm["money"] != before:
        Inst.hires.append((Inst.step, _pid(farm), before - farm["money"]))
    return r


def _w_land(farm, board_size):
    before = farm["money"]
    r = _orig_land(farm, board_size)
    if farm["money"] != before:
        Inst.lands.append((Inst.step, _pid(farm), before - farm["money"]))
    return r


def _w_town(env, state, step):
    obs0 = state[0].observation
    market = obs0.market
    before = dict(market["inventory"])
    r = _orig_town(env, state, step)
    after = dict(market["inventory"])
    Inst.drain_gt[step] = {p: before[p] - after[p] for p in PRODUCTS}
    Inst.inv_end[step] = after
    return r


def _w_pm(state, env):
    obs0 = state[0].observation
    if getattr(obs0, "farms", None):
        Inst.curmap.clear()
        Inst.curmap.update({id(f): i for i, f in enumerate(obs0.farms)})
        st = eng.get(obs0, "step", 0)
        Inst.step = st
        market = obs0.market
        Inv = market["inventory"]
        Inst.inv_start[st] = {p: Inv[p] for p in PRODUCTS}
        if "prices" in market:
            Inst.prices[st] = dict(market["prices"])

        # herd + money snapshot (public — như v4 thấy đầu step)
        herds, money = [], []
        for f in obs0.farms:
            cnt = {}
            for row in f["tiles"]:
                for t in row:
                    if isinstance(t, dict) and "animal" in t and t["animal"]:
                        cnt[t["animal"]] = cnt.get(t["animal"], 0) + 1
            herds.append(cnt)
            money.append(f["money"])
        Inst.herds[st] = herds
        Inst.money[st] = money

        # drain_est: mô hình của v4 từ thông tin public
        de = {p: 0 for p in PRODUCTS}
        town = obs0.town if hasattr(obs0, "town") else {}
        shops = town.get("unlocked_shops", []) if isinstance(town, dict) else []
        if st % 4 == 0:
            for sh in shops:
                prods = eng.SHOPS[sh]
                mult = 2 if len(prods) == 1 else 1
                for it in prods:
                    de[it] += mult
        if st % 24 == 0:
            for it in eng.TOWN_CENTER_PRODUCTS:
                de[it] += 1
        Inst.drain_est[st] = de
    return _orig_pm(state, env)


eng._commit_unit = _w_commit
eng._do_hire = _w_hire
eng._do_buy_land = _w_land
eng._town_consume = _w_town
eng._process_market = _w_pm


# ---------------------------------------------------------------------------
#  PHÂN TÍCH MỘT EPISODE
# ---------------------------------------------------------------------------
def _bucket_txns():
    """step -> player -> op -> item -> [count, total$] (SELL tách floor)."""
    b = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))
    for (st, pl, op, item, price) in Inst.txns:
        key = op
        if op == "SELL" and price <= 1:
            key = "SELL_FLOOR"
        b[st][pl][key][item] += 1
    return b


def analyze_episode(rewards, label):
    tx = _bucket_txns()

    # ---------- (1) TELEMETRY ----------
    tel = {
        "cells_checked": 0, "cells_match": 0,
        "by_product": {p: {"checked": 0, "match": 0} for p in PRODUCTS},
        "opp_floor_units": {0: 0, 1: 0},
        "samples": [],
    }
    drain_check = {"steps": 0, "match": 0, "mismatch_steps": []}
    for st in sorted(Inst.inv_start):
        if st not in Inst.inv_end:
            continue
        dinv = {p: Inst.inv_end[st][p] - Inst.inv_start[st][p] for p in PRODUCTS}
        de = Inst.drain_est.get(st, {p: 0 for p in PRODUCTS})
        dgt = Inst.drain_gt.get(st, {p: 0 for p in PRODUCTS})
        # kiểm mô hình drain của v4
        drain_check["steps"] += 1
        if all(de[p] == dgt[p] for p in PRODUCTS):
            drain_check["match"] += 1
        elif len(drain_check["mismatch_steps"]) < 10:
            drain_check["mismatch_steps"].append(
                (st, {p: (de[p], dgt[p]) for p in PRODUCTS if de[p] != dgt[p]}))
        tstep = tx.get(st, {})
        for me in (0, 1):
            opp = 1 - me
            my = tstep.get(me, {})
            op_ = tstep.get(opp, {})
            my_sells = my.get("SELL", {})
            my_buys = my.get("BUY_PRODUCT", {})
            opp_sells = op_.get("SELL", {})
            opp_buys = op_.get("BUY_PRODUCT", {})
            for p in PRODUCTS:
                est = dinv[p] + de[p] - my_sells.get(p, 0) + my_buys.get(p, 0)
                gt = opp_sells.get(p, 0) - opp_buys.get(p, 0)
                if est == 0 and gt == 0:
                    continue
                tel["cells_checked"] += 1
                tel["by_product"][p]["checked"] += 1
                if est == gt:
                    tel["cells_match"] += 1
                    tel["by_product"][p]["match"] += 1
                elif len(tel["samples"]) < 15:
                    tel["samples"].append({
                        "step": st, "me": me, "item": p, "est": est, "gt": gt,
                        "dinv": dinv[p], "drain_est": de[p], "drain_gt": dgt[p],
                        "my_sells": my_sells.get(p, 0), "my_buys": my_buys.get(p, 0),
                        "opp_sells": opp_sells.get(p, 0), "opp_buys": opp_buys.get(p, 0),
                        "opp_floor": op_.get("SELL_FLOOR", {}).get(p, 0),
                    })
            fl = op_.get("SELL_FLOOR", {})
            tel["opp_floor_units"][me] += sum(fl.values())

    # ---------- (2) LEDGER ----------
    ledger = []
    for pl in (0, 1):
        rev = defaultdict(int)
        units = defaultdict(int)
        seeds = defaultdict(int)
        animals = defaultdict(int)
        feedbuy = 0
        fertbuy = 0
        for (st, p, op, item, price) in Inst.txns:
            if p != pl:
                continue
            if op == "SELL":
                rev[item] += price
                units[item] += 1
            elif op == "BUY_SEED":
                seeds[item] += price
            elif op == "BUY_ANIMAL":
                animals[item] += price
            elif op == "BUY_PRODUCT":
                if item == "WHEAT":
                    feedbuy += price
                else:
                    fertbuy += price
        labor = sum(c for (st, p, c) in Inst.hires if p == pl)
        land = sum(c for (st, p, c) in Inst.lands if p == pl)
        revenue = sum(rev.values())
        balance = (rewards[pl] - 3000) - (revenue - labor - sum(seeds.values())
                                          - sum(animals.values()) - land - feedbuy - fertbuy)
        # hire theo ngày
        labor_day = defaultdict(int)
        for (st, p, c) in Inst.hires:
            if p == pl:
                labor_day[st // 24] += c
        # cash curve (mẫu mỗi 24 step)
        cash = {st: Inst.money[st][pl] for st in sorted(Inst.money) if st % 24 == 23}
        ledger.append({
            "player": pl, "final": rewards[pl],
            "revenue": dict(rev), "units": dict(units),
            "gross": revenue,
            "labor": labor, "land": land,
            "seeds": dict(seeds), "animals": dict(animals),
            "feedbuy": feedbuy, "fertbuy": fertbuy,
            "burn": labor + land + sum(seeds.values()) + sum(animals.values()) + feedbuy + fertbuy,
            "balance_residual": balance,
            "labor_by_day": {str(d): v for d, v in sorted(labor_day.items())},
            "cash_curve": {str(d): v for d, v in sorted(cash.items())},
        })

    # ---------- (3) T8 MIRROR ----------
    # đàn theo ngày (snapshot cuối ngày)
    herd_daily = {0: {}, 1: {}}
    for st in sorted(Inst.herds):
        d = st // 24
        for pl in (0, 1):
            herd_daily[pl][d] = Inst.herds[st][pl]
    cows = {pl: [herd_daily[pl].get(d, {}).get("COW", 0) for d in range(30)] for pl in (0, 1)}
    sheep = {pl: [herd_daily[pl].get(d, {}).get("SHEEP", 0) for d in range(30)] for pl in (0, 1)}
    goose = {pl: [herd_daily[pl].get(d, {}).get("GOOSE", 0) for d in range(30)] for pl in (0, 1)}
    cow_buys = {0: [], 1: []}
    for (st, p, op, item, price) in Inst.txns:
        if op == "BUY_ANIMAL" and item == "COW":
            cow_buys[p].append(st // 24)
    milk_px = [Inst.prices[st]["MILK"] for st in sorted(Inst.prices) if st >= 120]
    last_st = max(Inst.inv_end) if Inst.inv_end else 0
    milk_off = Inst.inv_end[last_st]["MILK"] - I0
    t8 = {
        "cows_daily": {str(pl): cows[pl] for pl in (0, 1)},
        "sheep_final": [sheep[pl][-1] for pl in (0, 1)],
        "goose_final": [goose[pl][-1] for pl in (0, 1)],
        "cow_peak": [max(cows[pl]) for pl in (0, 1)],
        "cow_final": [cows[pl][-1] for pl in (0, 1)],
        "cow_buy_days": {str(pl): cow_buys[pl] for pl in (0, 1)},
        "milk_units": [ledger[pl]["units"].get("MILK", 0) for pl in (0, 1)],
        "milk_rev": [ledger[pl]["revenue"].get("MILK", 0) for pl in (0, 1)],
        "milk_avg_px": [
            round(ledger[pl]["revenue"].get("MILK", 0) / max(1, ledger[pl]["units"].get("MILK", 0)), 1)
            for pl in (0, 1)],
        "wool_units": [ledger[pl]["units"].get("WOOL", 0) for pl in (0, 1)],
        "wool_avg_px": [
            round(ledger[pl]["revenue"].get("WOOL", 0) / max(1, ledger[pl]["units"].get("WOOL", 0)), 1)
            for pl in (0, 1)],
        "milk_px_band": [min(milk_px) if milk_px else 0,
                         round(sum(milk_px) / max(1, len(milk_px)), 1),
                         max(milk_px) if milk_px else 0],
        "milk_inv_offset_final": milk_off,
    }
    return {"label": label, "telemetry": tel, "drain_check": drain_check,
            "ledger": ledger, "t8": t8}


def run_episode(a, b, label):
    Inst.reset()
    env = make("kaggriculture", debug=False)
    env.run([a, b])
    final = env.steps[-1]
    rewards = [final[0].reward, final[1].reward]
    return analyze_episode(rewards, label), rewards


# ---------------------------------------------------------------------------
#  MAIN
# ---------------------------------------------------------------------------
def main():
    t0 = time.time()
    results = {"mirror": [], "ledger_v3v2": [], "summary": {}}

    # ---- 10 trận mirror v3-vs-v3 (đổi bên so le) — kiểm T8 + telemetry + ledger
    nets = []
    for i in range(10):
        a, b = (V3A, V3B) if i % 2 == 0 else (V3B, V3A)
        res, rw = run_episode(a, b, f"mirror_{i}")
        res["rewards"] = rw
        results["mirror"].append(res)
        nets.append(rw)
        print(f"  mirror {i}: ${rw[0]:,.0f} vs ${rw[1]:,.0f}  "
              f"({time.time()-t0:.0f}s)")

    # ---- 2 trận v3-vs-v2 — đối chiếu ledger với trận đo $61.7k cũ
    v3v2 = []
    for i in range(2):
        a, b = (V3A, V2) if i % 2 == 0 else (V2, V3A)
        res, rw = run_episode(a, b, f"v3v2_{i}")
        res["rewards"] = rw
        results["ledger_v3v2"].append(res)
        v3v2.append(rw)
        print(f"  v3v2  {i}: ${rw[0]:,.0f} vs ${rw[1]:,.0f}  ({time.time()-t0:.0f}s)")

    # ---- tổng hợp telemetry (gộp 12 trận)
    tel_tot = {"cells_checked": 0, "cells_match": 0}
    by_prod = {p: {"checked": 0, "match": 0} for p in PRODUCTS}
    drain_tot = {"steps": 0, "match": 0}
    floor_units = 0
    balance_max = 0
    for grp in (results["mirror"], results["ledger_v3v2"]):
        for res in grp:
            t = res["telemetry"]
            tel_tot["cells_checked"] += t["cells_checked"]
            tel_tot["cells_match"] += t["cells_match"]
            floor_units += t["opp_floor_units"][0] + t["opp_floor_units"][1]
            for p in PRODUCTS:
                by_prod[p]["checked"] += t["by_product"][p]["checked"]
                by_prod[p]["match"] += t["by_product"][p]["match"]
            drain_tot["steps"] += res["drain_check"]["steps"]
            drain_tot["match"] += res["drain_check"]["match"]
            for led in res["ledger"]:
                balance_max = max(balance_max, abs(led["balance_residual"]))

    # ---- tổng hợp T8 (10 trận mirror)
    m = results["mirror"]
    t8s = {
        "net_per_side": [round(sum(r["rewards"][p] for r in m) / len(m), 1) for p in (0, 1)],
        "cow_peak_avg": [round(sum(r["t8"]["cow_peak"][p] for r in m) / len(m), 2) for p in (0, 1)],
        "cow_final_avg": [round(sum(r["t8"]["cow_final"][p] for r in m) / len(m), 2) for p in (0, 1)],
        "sheep_final_avg": [round(sum(r["t8"]["sheep_final"][p] for r in m) / len(m), 2) for p in (0, 1)],
        "goose_final_avg": [round(sum(r["t8"]["goose_final"][p] for r in m) / len(m), 2) for p in (0, 1)],
        "milk_units_avg": [round(sum(r["t8"]["milk_units"][p] for r in m) / len(m), 1) for p in (0, 1)],
        "milk_avg_px_avg": [round(sum(r["t8"]["milk_avg_px"][p] for r in m) / len(m), 1) for p in (0, 1)],
        "wool_units_avg": [round(sum(r["t8"]["wool_units"][p] for r in m) / len(m), 1) for p in (0, 1)],
        "milk_px_band": [
            min(r["t8"]["milk_px_band"][0] for r in m),
            round(sum(r["t8"]["milk_px_band"][1] for r in m) / len(m), 1),
            max(r["t8"]["milk_px_band"][2] for r in m)],
        "milk_inv_offset_final": [r["t8"]["milk_inv_offset_final"] for r in m],
    }
    t8s["milk_total_sold_avg"] = round(t8s["milk_units_avg"][0] + t8s["milk_units_avg"][1], 1)
    t8s["milk_premium_left_avg_u"] = round(324 - t8s["milk_total_sold_avg"], 1)

    # ledger trung bình v3 trong mirror
    led_avg = {}
    for key in ("gross", "labor", "land", "feedbuy", "fertbuy", "burn", "final"):
        led_avg[key] = round(sum(r["ledger"][0][key] for r in m) / len(m), 1)
    led_avg["seeds"] = round(sum(sum(r["ledger"][0]["seeds"].values()) for r in m) / len(m), 1)
    led_avg["animals"] = round(sum(sum(r["ledger"][0]["animals"].values()) for r in m) / len(m), 1)

    results["summary"] = {
        "telemetry_total": tel_tot,
        "telemetry_by_product": by_prod,
        "drain_model_check": drain_tot,
        "opp_floor_sell_units_total": floor_units,
        "ledger_balance_max_abs_residual": balance_max,
        "t8_summary": t8s,
        "v3_mirror_ledger_avg": led_avg,
        "elapsed_s": round(time.time() - t0, 1),
    }

    with open('/home/z/my-project/kaggriculture/bench/p0_results.json', 'w') as f:
        json.dump(results, f, indent=1, default=str)

    # ---- in tóm tắt
    print("\n" + "=" * 72)
    print("P0 — TỔNG KẾT")
    print("=" * 72)
    print(f"[TELEMETRY] cells checked {tel_tot['cells_checked']:,} | "
          f"match {tel_tot['cells_match']:,} "
          f"({100*tel_tot['cells_match']/max(1,tel_tot['cells_checked']):.2f}%)")
    for p in PRODUCTS:
        d = by_prod[p]
        if d["checked"]:
            print(f"    {p:12s} {d['match']:>7,}/{d['checked']:<7,} "
                  f"{100*d['match']/d['checked']:6.2f}%")
    print(f"[DRAIN MODEL] {drain_tot['match']}/{drain_tot['steps']} steps khớp "
          f"({100*drain_tot['match']/max(1,drain_tot['steps']):.2f}%)")
    print(f"[FLOOR $1] opp sells vô hình: {floor_units} units (12 trận)")
    print(f"[LEDGER] max |balance residual| = ${balance_max}")
    print(f"[T8 MIRROR] net/side: ${t8s['net_per_side'][0]:,.0f} / ${t8s['net_per_side'][1]:,.0f}")
    print(f"    cow peak avg: {t8s['cow_peak_avg']} | cow final avg: {t8s['cow_final_avg']}"
          f" | sheep final: {t8s['sheep_final_avg']} | goose final: {t8s['goose_final_avg']}")
    print(f"    milk units/side: {t8s['milk_units_avg']} @ ${t8s['milk_avg_px_avg']} | "
          f"wool units/side: {t8s['wool_units_avg']}")
    print(f"    milk price band: {t8s['milk_px_band']} | "
          f"milk inv offset cuối: {t8s['milk_inv_offset_final'][:5]}…")
    print(f"    tổng milk 2 bên: {t8s['milk_total_sold_avg']}u / drain 324u → "
          f"premium bỏ lại ≈ {t8s['milk_premium_left_avg_u']}u")
    print(f"[v3 MIRROR LEDGER] gross ${led_avg['gross']:,.0f} | labor ${led_avg['labor']:,.0f} | "
          f"seeds ${led_avg['seeds']:,.0f} | animals ${led_avg['animals']:,.0f} | "
          f"land ${led_avg['land']:,.0f} | feed ${led_avg['feedbuy']:,.0f} | "
          f"fert ${led_avg['fertbuy']:,.0f} | burn ${led_avg['burn']:,.0f}")
    print(f"[TIME] {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
