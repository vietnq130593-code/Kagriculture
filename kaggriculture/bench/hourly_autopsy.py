# Hourly autopsy — grab per-hour: money delta each side, market orders each side,
# market inventory snapshot, prices. Focus on a day range.
# Usage: python3 bench/hourly_autopsy.py 123 1 20 24
import sys, os, json
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
ROOT = '/home/z/my-project/kaggriculture'
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def run(seed, v5_seat, day_lo, day_hi):
    from kaggle_environments import make
    import importlib.util

    def load(path, tag):
        modname = f"hr_{tag}"
        spec = importlib.util.spec_from_file_location(modname, path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules[modname] = mod
        spec.loader.exec_module(mod)
        return mod

    events = []  # (day, hour, side, kind, detail)
    last_money = [None, None]

    def wrap(mod, side):
        def fn(obs):
            act = mod.agent(obs)
            try:
                day = obs.get("day") or 0
                hour = obs.get("hour") or 0
                farms = obs.get("farms") or []
                for s2 in (0, 1):
                    m = float((farms[s2] or {}).get("money") or 0)
                    if last_money[s2] is not None:
                        d = m - last_money[s2]
                        if abs(d) > 50 and day_lo <= day <= day_hi:
                            events.append((day, hour, s2, "delta", round(d)))
                    last_money[s2] = m
                if day_lo <= day <= day_hi and hour == 0:
                    inv = (obs.get("market") or {}).get("inventory") or {}
                    px = (obs.get("market") or {}).get("prices") or {}
                    snapshot = {p: (round(inv.get(p, 0)), px.get(p)) for p in ("WHEAT", "EGG", "MILK", "WOOL", "STRAWBERRY", "MELON", "FERTILIZER")}
                    events.append((day, hour, -1, "inv", snapshot))
                orders = (act or {}).get("market") or []
                for o in orders:
                    if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] in ("SELL", "BUY_PRODUCT", "BUY_ANIMAL"):
                        if day_lo <= day <= day_hi:
                            events.append((day, hour, side, "ord", (o[0], o[1], o[2])))
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
    print(f"seed {seed} v5@seat{v5_seat}: v5 ${r[v5_seat]:,.0f} vs v4 ${r[1-v5_seat]:,.0f}")
    return events


def report(events, v5_seat, day_lo, day_hi):
    evs = sorted([e for e in events if day_lo <= e[0] <= day_hi])
    cur_day = None
    agg = {}
    for (d, h, s, kind, det) in evs:
        if d != cur_day:
            if cur_day is not None:
                _flush(cur_day, agg, v5_seat)
            cur_day = d
            agg = {"delta": {0: 0.0, 1: 0.0}, "ord": {0: [], 1: []}, "inv": None}
        if kind == "delta":
            agg["delta"][s] += det
        elif kind == "ord":
            agg["ord"][s].append((h, det))
        elif kind == "inv":
            agg["inv"] = (h, det)
    if cur_day is not None:
        _flush(cur_day, agg, v5_seat)


def _flush(d, agg, v5s):
    d5, d4 = agg["delta"][v5s], agg["delta"][1 - v5s]
    print(f"\n--- day {d}: v5 {d5:+,.0f}  v4 {d4:+,.0f}  (gap-day {d5 - d4:+,.0f}) ---")
    if agg["inv"]:
        h, inv = agg["inv"]
        s = "  d0h%d inv: " % h
        parts = []
        for p, (i, px) in inv.items():
            parts.append(f"{p[:4]}={i}({px})")
        print(s + " ".join(parts))
    for label, side in (("v5", v5s), ("v4", 1 - v5s)):
        ords = agg["ord"][side]
        if ords:
            o_s = " ".join(f"h{h}:{op[:2]}{it[:4]}x{n}" for h, (op, it, n) in ords[:14])
            print(f"  {label} orders: {o_s}")


if __name__ == "__main__":
    seed, seat = int(sys.argv[1]), int(sys.argv[2])
    day_lo, day_hi = int(sys.argv[3]), int(sys.argv[4])
    evs = run(seed, seat, day_lo, day_hi)
    report(evs, seat, day_lo, day_hi)
