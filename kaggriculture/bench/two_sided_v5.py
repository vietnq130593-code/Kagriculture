import sys, time, json
sys.path.insert(0, '/home/z/my-project/kaggriculture')
sys.path.insert(0, '/home/z/my-project/kaggriculture/bench')
from kaggle_environments import make

import os as _os
SEEDS = list(range(int(_os.environ.get("SEED_LO", 100)), int(_os.environ.get("SEED_HI", 120))))
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
    rows = []
    t0 = time.time()
    for i, s in enumerate(SEEDS):
        # A at seat 0 then A at seat 1 (two-sided)
        r0, r1 = one_match(a, b, s)
        r2, r3 = one_match(b, a, s)  # swapped: b seat0, a seat1
        ra = (r0 + r3) / 2.0   # a's average across seats
        rb = (r1 + r2) / 2.0
        rows.append({"seed": s, "a_seat0": r0, "b_seat1": r1, "b_seat0": r2, "a_seat1": r3})
        print(f"seed {s}: {a} avg ${ra:,.0f} vs {b} avg ${rb:,.0f}  "
              f"ratio {ra / max(1, rb):.3f}x  (s0 {r0:,.0f}/{r1:,.0f} s1 {r2:,.0f}/{r3:,.0f})",
              flush=True)
    wa = sum(1 for r in rows if r["a_seat0"] > r["b_seat1"]) + \
         sum(1 for r in rows if r["a_seat1"] > r["b_seat0"])
    ties = sum(1 for r in rows if r["a_seat0"] == r["b_seat1"]) + \
           sum(1 for r in rows if r["a_seat1"] == r["b_seat0"])
    n = len(rows) * 2
    ma = sum(r["a_seat0"] + r["a_seat1"] for r in rows) / n
    mb = sum(r["b_seat1"] + r["b_seat0"] for r in rows) / n
    worst = min((r["a_seat0"] / max(1, r["b_seat1"])) for r in rows)
    worst = min(worst, min((r["a_seat1"] / max(1, r["b_seat0"])) for r in rows))
    print(f"\n=== {a} vs {b} two-sided {n} games ===")
    print(f"wins {wa}/{n} (ties {ties}) | {a} avg ${ma:,.0f} vs ${mb:,.0f} | "
          f"ratio {ma / max(1, mb):.3f}x | worst {worst:.3f}x | {time.time() - t0:.0f}s")
    if out_path:
        with open(out_path, "w") as f:
            json.dump({"rows": rows, "summary": {"wins": wa, "n": n, "avg_a": ma,
                                                 "avg_b": mb, "ratio": ma / max(1, mb),
                                                 "worst": worst}}, f, indent=1)
        print(f"saved {out_path}")


if __name__ == "__main__":
    main()
