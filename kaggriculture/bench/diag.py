import sys, time, json
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as eng

LOG = []
CURMAP = {}


_orig_commit = eng._commit_unit
_orig_pm = eng._process_market


def _log_commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    if ok and op == "SELL":
        LOG.append((CURMAP.get(id(farm), -1), item, price))
    return ok


def _log_pm(state, env):
    obs0 = state[0].observation
    if getattr(obs0, "farms", None):
        CURMAP.clear()
        CURMAP.update({id(f): i for i, f in enumerate(obs0.farms)})
    return _orig_pm(state, env)


eng._commit_unit = _log_commit
eng._process_market = _log_pm


def diag_match(a, b, n, label):
    print(f"\n===== {label} ({n} eps) =====")
    for ep in range(n):
        LOG.clear()
        pair = [a, b] if ep % 2 == 0 else [b, a]
        env = make("kaggriculture", debug=False)
        env.run(pair)
        final = env.steps[-1]
        obs = final[0].observation
        farms = obs.farms
        idmap = CURMAP
        sales = {0: {}, 1: {}}
        rev = {0: {}, 1: {}}
        for fid, item, price in LOG:
            p = fid
            sales[p][item] = sales[p].get(item, 0) + 1
            rev[p][item] = rev[p].get(item, 0) + price
        r0, r1 = final[0].reward, final[1].reward
        names = {0: pair[0], 1: pair[1]}
        for p in (0, 1):
            an = {}
            crops = {}
            for row in farms[p]["tiles"]:
                for t in row:
                    if isinstance(t, dict):
                        if "animal" in t:
                            an[t["animal"]] = an.get(t["animal"], 0) + 1
                        elif t.get("kind") == "PLANT":
                            crops[t["crop"]] = crops.get(t["crop"], 0) + 1
                        elif t.get("kind") in ("COOP", "PASTURE"):
                            an["EMPTY_" + t["kind"]] = an.get("EMPTY_" + t["kind"], 0) + 1
            mix = " ".join(f"{it}:{sales[p].get(it,0)}u/${rev[p].get(it,0):,}" for it in
                           ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
                           if sales[p].get(it, 0))
            print(f"  ep{ep} P{p} [{names[p]}] final=${r0 if p==0 else r1:,.0f} | sold {mix}")
            print(f"        end-board: animals={an} standing_crops={crops} quad={len(farms[p]['unlocked_quadrants'])}")
        print(f"  ep{ep} ratio A/B = {r0/max(1,r1):.2f} | R={r0:,.0f} vs {r1:,.0f}")


if __name__ == "__main__":
    t0 = time.time()
    diag_match("bench/v2_a.py", "bench/v2_b.py", 2, "v2 SELF-PLAY")
    diag_match("v2.py", "bench/baseline.py", 1, "v2 vs BASELINE")
    print(f"\n{time.time()-t0:.0f}s")
