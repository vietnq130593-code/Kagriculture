"""KAIN vs v6 (Task 28): đo đạc SỬ DỤNG ĐẤT hằng ngày — trả lời câu hỏi của
user: "số đất trống thừa và không dùng hết rất nhiều, có nên dùng tối đa 75 đất?"
Đo cho cả 2 player: quadrant mở (từ locked count), ô trống, cây đứng, thú,
structure, tiền → tính wasted-tile-days (ô trống × ngày) + utilization.
Cách dùng: python bench/land_probe.py <a> <b> <seed>
"""
import sys, os, glob
ROOT = glob.glob('/home/z/my-project/kag*')[0]
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'bench'))
from kaggle_environments import make

a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])


def resolve(x):
    if os.path.isfile(x):
        return x
    p = os.path.join(ROOT, x)
    return p if os.path.isfile(p) else x


env = make("kaggriculture", debug=False, configuration={"seed": seed})
env.run([resolve(a), resolve(b)])
r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
print(f"seed {seed}: {a} ${r0:,.0f} vs {b} ${r1:,.0f}")


def snapshot(tiles):
    """(locked, empty, crops{crop:n}, animals, coop, pasture, weeds)"""
    locked = empty = animals = coop = pasture = weeds = 0
    crops = {}
    for row in tiles:
        for t in row:
            if t == "LOCKED":
                locked += 1
            elif t is None:
                empty += 1
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "PLANT":
                    c = t.get("crop")
                    crops[c] = crops.get(c, 0) + 1
                elif k == "COOP":
                    coop += 1
                elif k == "PASTURE":
                    pasture += 1
                elif k == "WEED":
                    weeds += 1
                if "animal" in t:
                    animals += 1
    return locked, empty, crops, animals, coop, pasture, weeds


def land_days(side):
    """Cuối mỗi ngày (h23): snapshot đất."""
    rows = []
    last_day_seen = -1
    for step in env.steps:
        obs = step[0].observation
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        if hour != 23 or day == last_day_seen:
            continue
        last_day_seen = day
        farm = obs.farms[side] if obs.get("farms") else None
        if not farm:
            continue
        locked, empty, crops, animals, coop, pasture, weeds = \
            snapshot(farm.get("tiles", []))
        nq = (100 - locked) // 25
        used = sum(crops.values()) + animals + coop + pasture + weeds
        rows.append({
            "day": day, "nq": nq, "locked": locked, "empty": empty,
            "crops": crops, "animals": animals, "coop": coop,
            "pasture": pasture, "weeds": weeds, "used": used,
            "money": farm.get("money", 0),
        })
    return rows


for side, name in ((0, a), (1, b)):
    rows = land_days(side)
    print(f"\n=== side{side} {name} — LAND USAGE seed {seed} ===")
    print(f"{'d':>3} {'nq':>3} {'empty':>6} {'crops':>6} {'anim':>5} "
          f"{'struct':>7} {'weed':>5} {'used':>5} {'money':>8}  crop-mix")
    for r in rows:
        if r["day"] < 1:
            continue
        mix = ",".join(f"{c[:4]}{n}" for c, n in sorted(
            r["crops"].items(), key=lambda kv: -kv[1]))
        print(f"{r['day']:>3} {r['nq']:>3} {r['empty']:>6} "
              f"{sum(r['crops'].values()):>6} {r['animals']:>5} "
              f"{r['coop'] + r['pasture']:>7} {r['weeds']:>5} {r['used']:>5} "
              f"{r['money']:>8,.0f}  {mix}")
    # Tóm tắt sử dụng đất: chỉ tính từ d5 (sau mở viêm) đến d28
    core = [r for r in rows if 5 <= r["day"] <= 28]
    if core:
        total_tile_days = sum(25 * r["nq"] for r in core)
        used_tile_days = sum(r["used"] for r in core)
        empty_tile_days = sum(r["empty"] for r in core)
        # ô trống TÍCH LUỸ theo nq (đã mở mà không dùng = lãng phí thật)
        nq_days = {}
        for r in core:
            nq_days.setdefault(r["nq"], 0)
            nq_days[r["nq"]] += 1
        print(f"\n[TOTAL {name}] opened-quadrant-days: {nq_days}")
        print(f"[WASTE {name}] empty-tile-days d5-28 = {empty_tile_days} "
              f"(~{empty_tile_days / max(1, len(core)):.0f} ô trống/ngày) · "
              f"utilization = {used_tile_days}/{total_tile_days} = "
              f"{100.0 * used_tile_days / max(1, total_tile_days):.0f}%")
        buys = [r["day"] for r in rows
                if r["day"] > 0 and rows[rows.index(r) - 1]["nq"] < r["nq"]]
        print(f"[BUY_LAND {name}] quadrants opened at days {buys}")
