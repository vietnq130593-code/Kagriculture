import sys, time, json
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
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
        r0 = final[0].reward
        r1 = final[1].reward
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
    avg_a = sum(ra) / len(ra)
    avg_b = sum(rb) / len(rb)
    print(f"{label}: A {wins_a}W / B {wins_b}W / {ties}T | A avg ${avg_a:,.0f} (min ${min(ra):,.0f}) | B avg ${avg_b:,.0f} | {dt:.1f}s for {n} eps")
    return avg_a, avg_b

if __name__ == "__main__":
    base = "baseline.py"
    tests = [
        ("melon.py", 6, "vs melon_maxxer"),
        ("random", 4, "vs random"),
    ]
    for opp, n, label in tests:
        run_match(base, opp, n, label)
    run_match("baseline_a.py", "baseline_b.py", 4, "self-play")
