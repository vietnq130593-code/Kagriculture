import sys
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make

env = make("kaggriculture", debug=False)
env.run(["v4.py", "v3.py"])

# walk steps, print daily snapshot of each farm
prev_day = -1
for si, step_states in enumerate(env.steps):
    obs = step_states[0].observation
    day = obs.day
    hour = obs.hour
    if day != prev_day and hour == 0:
        prev_day = day
        for pi, farm in enumerate(obs.farms):
            tiles = farm.tiles
            counts = {}
            money = farm.money
            hands = len(farm.hands)
            for row in tiles:
                for t in row:
                    if t is None or t == "LOCKED":
                        continue
                    if isinstance(t, dict):
                        k = t.get("kind")
                        a = t.get("animal")
                        if a:
                            counts[a] = counts.get(a, 0) + 1
                        elif k == "PLANT":
                            counts[t.get("crop")] = counts.get(t.get("crop"), 0) + 1
                        elif k in ("COOP", "PASTURE"):
                            counts[k] = counts.get(k, 0) + 1
                        elif k == "WEED":
                            counts["WEED"] = counts.get("WEED", 0) + 1
            name = "V4" if pi == 0 else "V3"
            print(f"d{day:02d} {name}: ${money:>8,.0f} h{hands} " + " ".join(f"{k}={v}" for k, v in sorted(counts.items())))
        mkt = obs.market.inventory
        print(f"   mk: MILK{mkt['MILK']-10000:+d} WOOL{mkt['WOOL']-10000:+d} EG{mkt['EGG']-10000:+d} WH{mkt['WHEAT']-10000:+d} ME{mkt['MELON']-10000:+d} ST{mkt['STRAWBERRY']-10000:+d} FE{mkt['FERTILIZER']-10000:+d}")
print("final:", [s.reward for s in env.steps[-1]])
