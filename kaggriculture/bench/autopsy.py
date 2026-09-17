# P1 AUTOPSY — chạy lại các trận thua, trích: (1) gap tiền theo NGÀY (ground truth
# lộ trình thua), (2) đơn SELL/BUY_PRODUCT theo kênh × ngày, (3) cấu trúc
# (cây đứng / đàn / thợ / đất) mỗi ngày, (4) shop mở theo ngày.
# Cách chạy: python3 bench/autopsy.py 104 0   (seed, ghế v5)
import sys, os, json, time
sys.path.insert(0, '/home/z/my-project/kaggressulture')
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
ROOT = '/home/z/my-project/kaggriculture'

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def run(seed, v5_seat):
    from kaggle_environments import make
    import importlib.util

    def load(path, tag):
        modname = f"aut_{tag}_{os.path.splitext(os.path.basename(path))[0]}"
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        spec.loader.exec_module(mod)
        return mod

    log = {"seed": seed, "v5_seat": v5_seat, "days": [], "sales": [{}, {}],
           "buys": [{}, {}], "spend": [[], []], "struct": []}

    def wrap(mod, side):
        def fn(obs):
            act = mod.agent(obs)
            try:
                day = obs.get("day") or 0
                hour = obs.get("hour") or 0
                me = (obs.get("farms") or [])[side]
                if hour == 23 or day >= 29:
                    m = float(me.get("money") or 0)
                    log["days"].append({"day": day, "side": side, "money": m})
                orders = (act or {}).get("market") or []
                for o in orders:
                    if not isinstance(o, (list, tuple)) or len(o) < 3:
                        continue
                    op, item, n = o[0], o[1], o[2]
                    key = f"{day:02d}"
                    if op == "SELL" and item in PRODUCTS:
                        log["sales"][side].setdefault(item, {})
                        log["sales"][side][item][key] = log["sales"][side][item].get(key, 0) + int(n)
                    elif op == "BUY_PRODUCT" and item in PRODUCTS:
                        log["buys"][side].setdefault(item, {})
                        log["buys"][side][item][key] = log["buys"][side][item].get(key, 0) + int(n)
                fa = (act or {}).get("farmer") or []
                ha = (act or {}).get("hands") or []
                for a in [fa] + list(ha):
                    if isinstance(a, (list, tuple)) and a and a[0] in (
                            "BUY_LAND", "BUILD_COOP", "BUILD_PASTURE", "HIRE", "BUY_ANIMAL"):
                        log["spend"][side].append((day, a[0]))
                if hour == 23 or day >= 29:
                    tiles = me.get("tiles") or []
                    st = {"day": day, "side": side}
                    st["animals"] = sum(1 for row in tiles for t in row
                                        if isinstance(t, dict) and "animal" in t)
                    st["standing"] = sum(1 for row in tiles for t in row
                                         if isinstance(t, dict) and t.get("kind") == "PLANT")
                    st["empty"] = sum(1 for row in tiles for t in row if t is None)
                    st["n_tiles"] = len(tiles) * len(tiles[0]) if tiles else 0
                    st["workers"] = 1 + len(me.get("hands") or [])
                    log["struct"].append(st)
            except Exception:
                pass
            return act
        return fn

    mA = load(os.environ.get("V5_PATH") or os.path.join(ROOT, "v5.py"), "a")
    mB = load(os.path.join(ROOT, "v4.py"), "b")
    if v5_seat == 0:
        agents = [wrap(mA, 0), wrap(mB, 1)]
    else:
        agents = [wrap(mB, 0), wrap(mA, 1)]
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run(agents)
    r = [float(env.steps[-1][0].reward or 0), float(env.steps[-1][1].reward or 0)]
    log["rewards"] = r
    return log


def report(log):
    v5s = log["v5_seat"]
    print(f"\n{'=' * 78}")
    print(f"AUTOPSY seed {log['seed']}  v5@seat{v5s}  v5 ${log['rewards'][v5s]:,.0f} vs "
          f"v4 ${log['rewards'][1 - v5s]:,.0f}  gap {log['rewards'][v5s] - log['rewards'][1 - v5s]:+,.0f}")
    print("=" * 78)
    days = {}
    for d in log["days"]:
        days.setdefault(d["day"], {})[d["side"]] = d["money"]
    ks = sorted(days)
    money = {0: [days[k].get(0) for k in ks], 1: [days[k].get(1) for k in ks]}
    gap = []
    for i, k in enumerate(ks):
        m5 = money[v5s][i]
        m4 = money[1 - v5s][i]
        if m5 is not None and m4 is not None:
            gap.append((k, m5 - m4))
    print("day |   v5$    |   v4$    |  gap   | dGap(v5-v4 trong ngày)")
    prev5 = prev4 = None
    for i, k in enumerate(ks):
        m5 = money[v5s][i]
        m4 = money[1 - v5s][i]
        if m5 is None or m4 is None:
            continue
        dg = ""
        if prev5 is not None:
            dg = f"{(m5 - prev5) - (m4 - prev4):+9,.0f}"
        prev5, prev4 = m5, m4
        mark = " <<<" if prev5 is not None and (m5 - m4) < (gap[i - 1][1] if i else 0) - 300 else ""
        print(f" {k:2d} | {m5:8,.0f} | {m4:8,.0f} | {m5 - m4:+7,.0f} |{dg}{mark}")
    print("\n-- units SOLD (v5 / v4) per channel, days where gap mở >= $1,000 --")
    days_widening = set()
    for i in range(1, len(gap)):
        if gap[i][1] < gap[i - 1][1] - 1000:
            for j in range(gap[i - 1][0] + 1, gap[i][0] + 1):
                days_widening.add(j)
    all_items = sorted(set(log["sales"][v5s]) | set(log["sales"][1 - v5s]),
                       key=lambda x: -sum(sum(v.values()) for v in [log["sales"][v5s].get(x, {})]))
    for it in all_items:
        s5 = log["sales"][v5s].get(it, {})
        s4 = log["sales"][1 - v5s].get(it, {})
        u5 = sum(s5.values())
        u4 = sum(s4.values())
        d5 = {int(d) for d in s5}
        d4 = {int(d) for d in s4}
        print(f"  {it:11s} v5 {u5:5.0f}u (d{min(d5) if d5 else '-'}-{max(d5) if d5 else '-'})  "
              f"v4 {u4:5.0f}u (d{min(d4) if d4 else '-'}-{max(d4) if d4 else '-'})")
    print("\n-- structure (cuối mỗi 4 ngày) --")
    seen = {}
    for st in log["struct"]:
        seen.setdefault(st["side"], {})[st["day"]] = st
    for side_label, side in (("v5", v5s), ("v4", 1 - v5s)):
        ss = seen.get(side, {})
        row = " ".join(f"d{d}:a{ss[d]['animals']}/c{ss[d]['standing']}/w{ss[d]['workers']}"
                       for d in sorted(ss) if d % 4 == 3)
        print(f"  {side_label}: {row}")
    for side_label, side in (("v5", v5s), ("v4", 1 - v5s)):
        sp = log["spend"][side]
        if sp:
            from collections import Counter
            c = Counter(op for _, op in sp)
            hires = [d for d, op in sp if op == "HIRE"]
            lands = [d for d, op in sp if op == "BUY_LAND"]
            print(f"  {side_label} spend: {dict(c)} hires d{hires[:8]} lands d{lands[:8]}")


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        seed, seat = arg.split(":")
        t0 = time.time()
        log = run(int(seed), int(seat))
        report(log)
        sys.stderr.write(f"seed {seed} done {time.time() - t0:.0f}s\n")
