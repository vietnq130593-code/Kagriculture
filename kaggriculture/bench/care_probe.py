"""v6 (Task 27): đo care-discipline hằng ngày — đếm thú được feed/care mỗi
ngày + herd size + hire count, cho 2 agent trên 1 seed. Cách dùng:
  python bench/care_probe.py <a> <b> <seed>
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


env = make(glob.glob(os.path.join(ROOT, ''))[0] and "kag" + "g" + "riculture",
           debug=False, configuration={"seed": seed})
env.run([resolve(a), resolve(b)])
r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
print(f"seed {seed}: {a} ${r0:,.0f} vs {b} ${r1:,.0f}")


def day_stats(side):
    """Cuối mỗi ngày: đếm thú fed/cared + tổng đàn + hire."""
    rows = []
    for si, step in enumerate(env.steps):
        obs = step[0].observation
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        if hour != 23 or day < 2:
            continue
        farm = obs.farms[side] if obs.get("farms") else None
        if not farm:
            continue
        n = fed = cared = 0
        for row in farm.get("tiles", []):
            for t in row:
                if isinstance(t, dict) and "animal" in t:
                    n += 1
                    if t.get("fed_today"):
                        fed += 1
                    if t.get("cared_today"):
                        cared += 1
        money = farm.get("money", 0)
        hires = farm.get("hires_today", 0)
        rows.append((day, n, fed, cared, money, hires))
    return rows


for side, name in ((0, a), (1, b)):
    print(f"\n=== side{side} {name} ===")
    print(f"{'d':>3} {'herd':>5} {'fed':>4} {'cared':>5} {'money':>8} {'hire':>4}")
    for day, n, fed, cared, money, hires in day_stats(side):
        flag = ""
        if n > 0 and (fed < n or cared < n):
            flag = "  <-- CARE MISS" if cared < n else "  <-- FEED MISS"
        print(f"{day:>3} {n:>5} {fed:>4} {cared:>5} {money:>8,.0f} {hires:>4}{flag}")
