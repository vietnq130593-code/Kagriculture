# Daily herd ramp + cash trace: v4 vs v3
import sys
sys.path.insert(0, '/home/z/my-project/kaggregiculture' if False else '/home/z/my-project/kaggriculture')
from kaggle_environments import make

A = sys.argv[1] if len(sys.argv) > 1 else "/home/z/my-project/kaggriculture/v4.py"
B = sys.argv[2] if len(sys.argv) > 2 else "/home/z/my-project/kaggriculture/v3.py"

env = make("kaggriculture", debug=False)
env.run([A, B])
last = {0: None, 1: None}
for st in env.steps:
    for pl in (0, 1):
        obs = st[pl].observation
        day = obs.get("day", 0)
        hour = obs.get("hour", 0)
        if hour == 23:
            last[pl] = obs
        if day == 29 and hour == 22:
            last[pl] = obs
names = {0: A.split("/")[-1], 1: B.split("/")[-1]}
for pl in (0, 1):
    obs = last[pl]
    print(f"\n=== P{pl} {names[pl]} final: ${st[pl].reward:,.0f}")
    farm = obs["farms"][pl]
    print("money:", farm.get("money"))
# now trace daily from steps
print("\n=== daily trace (day: P0 money/animals  P1 money/animals) ===")
daily = {}
for si, st in enumerate(env.steps):
    for pl in (0, 1):
        obs = st[pl].observation
        day, hour = obs.get("day", 0), obs.get("hour", 0)
        if hour != 12:
            continue
        farm = obs["farms"][pl]
        tiles = farm.get("tiles") or []
        g = c = s = past = coop = 0
        wheat_stand = 0
        for row in tiles:
            for t in row:
                if not isinstance(t, dict):
                    continue
                if "animal" in t:
                    a = t["animal"]
                    if a == "GOOSE": g += 1
                    elif a == "COW": c += 1
                    elif a == "SHEEP": s += 1
                if t.get("kind") == "PASTURE": past += 1
                if t.get("kind") == "COOP": coop += 1
                if t.get("kind") == "PLANT" and t.get("crop") == "WHEAT": wheat_stand += 1
        daily.setdefault(day, {})[pl] = (farm.get("money"), g, c, s, past, coop, wheat_stand,
                                          len(farm.get("unlocked_quadrants") or ["NW"]))
for d in sorted(daily):
    if d % 1 == 0 and d <= 29:
        r0 = daily[d].get(0, ("-","-","-","-","-","-","-","-"))
        r1 = daily[d].get(1, ("-","-","-","-","-","-","-","-"))
        print(f"d{d:>2}: P0 ${r0[0]:>6} g{r0[1]} c{r0[2]} s{r0[3]} past{r0[4]} coop{r0[5]} wh{r0[6]} q{r0[7]}   "
              f"P1 ${r1[0]:>6} g{r1[1]} c{r1[2]} s{r1[3]} past{r1[4]} coop{r1[5]} wh{r1[6]} q{r1[7]}")
