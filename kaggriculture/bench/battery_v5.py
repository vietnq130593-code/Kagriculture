# Battery 20-seed two-sided: A vs B, seeds 100-119, cả 2 ghế.
# In: python3 battery_v5.py <a.py> <b.py> [out.json] [seedspec]
import sys, time, json
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make

ROOT = '/home/z/my-project/kaggriculture'


def resolve(x):
    import os
    if os.path.isfile(x):
        return x
    p = os.path.join(ROOT, x)
    if os.path.isfile(p):
        return p
    return x


def one_match(a, b, seed):
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run([resolve(a), resolve(b)])
    r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
    return float(r0), float(r1)


def main():
    a, b = sys.argv[1], sys.argv[2]
    out_path = sys.argv[3] if len(sys.argv) > 3 else None
    seedspec = sys.argv[4] if len(sys.argv) > 4 else "100-119"
    if "-" in seedspec:
        lo, hi = seedspec.split("-")
        SEEDS = list(range(int(lo), int(hi) + 1))
    else:
        SEEDS = [int(x) for x in seedspec.split(",")]
    rows = []
    t0 = time.time()
    for i, s in enumerate(SEEDS):
        r0, r1 = one_match(a, b, s)
        r2, r3 = one_match(b, a, s)  # swapped
        ra = (r0 + r3) / 2.0
        rb = (r1 + r2) / 2.0
        rows.append({"seed": s, "a_seat0": r0, "b_seat1": r1, "b_seat0": r2, "a_seat1": r3,
                     "ratio": ra / max(1, rb)})
        print(f"seed {s}: {a} ${ra:,.0f} vs {b} ${rb:,.0f}  ratio {ra / max(1, rb):.3f}x  "
              f"(s0 {r0:,.0f}/{r1:,.0f} s1 {r2:,.0f}/{r3:,.0f})", flush=True)
    wa = sum(1 for r in rows if r["a_seat0"] > r["b_seat1"]) + \
         sum(1 for r in rows if r["a_seat1"] > r["b_seat0"])
    n = len(rows) * 2
    ma = sum(r["a_seat0"] + r["a_seat1"] for r in rows) / n
    mb = sum(r["b_seat1"] + r["b_seat0"] for r in rows) / n
    worst = min(min(r["a_seat0"] / max(1, r["b_seat1"]), r["a_seat1"] / max(1, r["b_seat0"]))
                for r in rows)
    ratios = sorted(r["ratio"] for r in rows)
    med = ratios[len(ratios) // 2]
    p25 = ratios[len(ratios) // 4]
    print(f"\n=== {a} vs {b} two-sided {n} games (seeds {SEEDS[0]}-{SEEDS[-1]}) ===")
    print(f"wins {wa}/{n} | avg ${ma:,.0f} vs ${mb:,.0f} | ratio {ma / max(1, mb):.3f}x "
          f"| median {med:.3f} | P25 {p25:.3f} | worst {worst:.3f} | {time.time() - t0:.0f}s")
    if out_path:
        with open(out_path, "w") as f:
            json.dump({"a": a, "b": b, "rows": rows,
                       "summary": {"wins": wa, "n": n, "avg_a": ma, "avg_b": mb,
                                   "ratio": ma / max(1, mb), "median": med,
                                   "p25": p25, "worst": worst}}, f, indent=1)
        print(f"saved {out_path}")


if __name__ == "__main__":
    main()
