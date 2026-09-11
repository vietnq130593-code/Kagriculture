import sys
sys.path.insert(0, '/home/z/my-project/kaggressure'.replace('kaggressure', 'kaggriculture'))
sys.path.insert(0, '/home/z/my-project/kaggriculture')
from kaggle_environments import make

def one_match(a, b, seed):
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run([a, b])
    r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
    return r0, r1

seeds = [int(x) for x in sys.argv[1].replace('-', ',').split(',') if x] if '-' in sys.argv[1] else [int(x) for x in sys.argv[1].split(',')] if len(sys.argv) > 1 else list(range(100, 108))
wins = 0
for s in seeds:
    r0, r1 = one_match("v4.py", "v3.py", s)
    w = "V4" if r0 > r1 else "V3"
    if r0 > r1:
        wins += 1
    print(f"seed {s}: v4 ${r0:,.0f} vs v3 ${r1:,.0f}  -> {w} {'+' if w == 'V4' else ''}{(r0 / r1):.2f}x")
print(f"v4 wins {wins}/{len(seeds)}")
