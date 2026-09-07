import sys, time
sys.path.insert(0, '/home/z/my-project/kaggriculture')
from kaggle_environments import make

def run_match(a, b, n, label):
    wins_a = wins_b = ties = 0
    ra, rb = [], []
    t0 = time.time()
    for i in range(n):
        pair = [a, b] if i % 2 == 0 else [b, a]
        env = make("kaggriculture", debug=False)
        env.run(pair)
        final = env.steps[-1]
        r0, r1 = final[0].reward, final[1].reward
        if pair[0] == a:
            ra.append(r0); rb.append(r1)
            if r0 > r1: wins_a += 1
            elif r1 > r0: wins_b += 1
            else: ties += 1
        else:
            ra.append(r1); rb.append(r0)
            if r1 > r0: wins_a += 1
            elif r0 > r1: wins_b += 1
            else: ties += 1
    dt = time.time() - t0
    print(f"{label}: A {wins_a}W / B {wins_b}W / {ties}T | A avg ${sum(ra)/len(ra):,.0f} (min ${min(ra):,.0f}, max ${max(ra):,.0f}) | B avg ${sum(rb)/len(rb):,.0f} | {dt:.0f}s")

if __name__ == "__main__":
    run_match("v2.py", "bench/baseline.py", 8, "v2 vs BASELINE")
    run_match("v2.py", "bench/melon.py", 6, "v2 vs melon")
    run_match("v2.py", "random", 4, "v2 vs random")
    run_match("bench/v2_a.py", "bench/v2_b.py", 4, "v2 self-play")
