# Quick instrumented A-vs-B: sales mix + burn ledger (reuses p0.Inst)
# (v3/baseline-era mặc định đã dọn — dùng argv: python3 ledger_v4.py v6.py kain25.py 3)
import sys, json
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make
import bench.p0 as p0

A = sys.argv[1] if len(sys.argv) > 1 else "v4.py"
B = sys.argv[2] if len(sys.argv) > 2 else "v5.py"
N = int(sys.argv[3]) if len(sys.argv) > 3 else 1

for i in range(N):
    p0.Inst.reset()
    env = make("kaggriculture", debug=False)
    env.run([A, B])
    final = env.steps[-1]
    rewards = [final[0].reward, final[1].reward]
    res = p0.analyze_episode(rewards, f"{A}_vs_{B}_{i}")
    print(f"=== {A} vs {B} ep{i}: ${rewards[0]:,.0f} vs ${rewards[1]:,.0f} ===")
    for pl, led in enumerate(res["ledger"]):
        name = A if pl == 0 else B
        print(f"\n--- {name} (P{pl}) net ${rewards[pl]:,.0f} ---")
        rev = led["revenue"]; un = led["units"]
        tot_r = led["gross"]
        burn = {"labor": led["labor"], "land": led["land"],
                "seeds": sum(led["seeds"].values()),
                "animals": sum(led["animals"].values()),
                "feedbuy": led["feedbuy"], "fertbuy": led["fertbuy"]}
        print(f"  GROSS ${tot_r:,.0f}  | BURN ${sum(burn.values()):,.0f}")
        for it in sorted(rev, key=lambda k: -rev[k]):
            if rev[it] > 0:
                print(f"    {it:<12} {un[it]:>5}u  ${rev[it]:>9,.0f}  avg ${rev[it]/max(1,un[it]):>6.0f}")
        for c, v in sorted(burn.items(), key=lambda kv: -kv[1]):
            if v > 0:
                print(f"    cost:{c:<10} ${v:>9,.0f}")
        cc = led["cash_curve"]
        print("    cash:", " ".join(f"d{d}:${v:,.0f}" for d, v in list(cc.items())))
