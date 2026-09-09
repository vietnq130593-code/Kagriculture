# KAIN autopsy — per-day: money delta each side, SELL/BUY orders per channel,
# market inventory+prices at day start, herd counts both sides.
# Usage: python3 bench/kautopsy.py <agentA_path> <agentB_path> <seed> <a_seat> [day_lo day_hi]
import sys, os, json, importlib.util
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
ROOT = '/home/z/my-project/kaggriculture'
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]


def load(path, tag):
    modname = f"ka_{tag}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def run(a_path, b_path, seed, a_seat, day_lo, day_hi):
    from kaggle_environments import make
    events = []
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
                    herds = []
                    for f in farms:
                        tiles = (f or {}).get("tiles") or []
                        hc = {"COW": 0, "GOOSE": 0, "SHEEP": 0}
                        for row in tiles:
                            for t in row:
                                if isinstance(t, dict) and "animal" in t:
                                    a = t.get("animal")
                                    if a in hc:
                                        hc[a] += 1
                        herds.append(hc)
                    snapshot = {p: (round(inv.get(p, 0)), px.get(p)) for p in PRODUCTS}
                    events.append((day, hour, -1, "inv", (snapshot, herds)))
                orders = (act or {}).get("market") or []
                for o in orders:
                    if isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] in ("SELL", "BUY_PRODUCT", "BUY_ANIMAL"):
                        if day_lo <= day <= day_hi:
                            events.append((day, hour, side, "ord", (o[0], o[1], o[2])))
            except Exception:
                pass
            return act
        return fn

    mA, mB = load(a_path, "a"), load(b_path, "b")
    if a_seat == 0:
        agents = [wrap(mA, 0), wrap(mB, 1)]
    else:
        agents = [wrap(mB, 0), wrap(mA, 1)]
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run(agents)
    r = [float(env.steps[-1][0].reward or 0), float(env.steps[-1][1].reward or 0)]
    print(f"seed {seed} A@seat{a_seat}: A ${r[a_seat]:,.0f} vs B ${r[1 - a_seat]:,.0f}")
    return events


def report(events, a_seat, day_lo, day_hi):
    evs = sorted([e for e in events if day_lo <= e[0] <= day_hi])
    cur_day = None
    agg = {}
    for (d, h, s, kind, det) in evs:
        if d != cur_day:
            if cur_day is not None:
                _flush(cur_day, agg, a_seat)
            cur_day = d
            agg = {"delta": {0: 0.0, 1: 0.0}, "ord": {0: [], 1: []}, "inv": None}
        if kind == "delta":
            agg["delta"][s] += det
        elif kind == "ord":
            agg["ord"][s].append((h, det))
        elif kind == "inv":
            agg["inv"] = det
    if cur_day is not None:
        _flush(cur_day, agg, a_seat)


def _flush(d, agg, a_s):
    dA, dB = agg["delta"][a_s], agg["delta"][1 - a_s]
    print(f"d{d:02d}: A {dA:+9,.0f}  B {dB:+9,.0f}  (gap {dA - dB:+,.0f})", end="")
    if agg["inv"]:
        snap, herds = agg["inv"]
        hA, hB = herds[a_s], herds[1 - a_s]
        print(f" | herd A c{hA['COW']}g{hA['GOOSE']}s{hA['SHEEP']} B c{hB['COW']}g{hB['GOOSE']}s{hB['SHEEP']}", end="")
        for p in ("MELON", "MILK", "WOOL", "WHEAT", "STRAWBERRY"):
            i, px = snap[p]
            if i is not None:
                print(f" {p[:4]}:{i}@{px}", end="")
    print()
    for label, side in (("A", a_s), ("B", 1 - a_s)):
        ords = agg["ord"][side]
        if ords:
            o_s = " ".join(f"h{h}:{op[:2]}{it[:4]}x{n}" for h, (op, it, n) in ords[:18])
            print(f"     {label}: {o_s}")


if __name__ == "__main__":
    a_path, b_path = sys.argv[1], sys.argv[2]
    if not os.path.isfile(a_path):
        a_path = os.path.join(ROOT, a_path)
    if not os.path.isfile(b_path):
        b_path = os.path.join(ROOT, b_path)
    seed, a_seat = int(sys.argv[3]), int(sys.argv[4])
    day_lo = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    day_hi = int(sys.argv[6]) if len(sys.argv) > 6 else 29
    evs = run(a_path, b_path, seed, a_seat, day_lo, day_hi)
    report(evs, a_seat, day_lo, day_hi)
