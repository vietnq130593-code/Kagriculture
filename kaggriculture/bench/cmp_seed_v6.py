"""v6 (Task 27): so sánh per-seed v6 vs v5 với baseline kain16 vs v5 — tìm
seed lật (win↔lose) và khoản chênh $ để phán quyết delta nào giúp/hại."""
import json
import sys

ROOT = "/home/z/my-project/kaggriculture/bench/"


def load(p):
    return json.load(open(ROOT + p))


def rows_map(d):
    out = {}
    for r in d["rows"]:
        out[r["seed"]] = r
    return out


def main():
    v6_file, base_file = sys.argv[1], sys.argv[2]
    v6 = rows_map(load(v6_file))
    base = rows_map(load(base_file))

    def game_wins(row, a_key, b_key):
        return 1 if row[a_key] > row[b_key] else 0

    print(f"{'seed':>5} {'v6 s0':>8} {'v5 s1':>8} {'W/L':>4} | {'k16 s0':>8} {'v5 s1':>8} {'W/L':>4} | {'delta$ s0':>9}")
    print(f"{'':>5} {'v5 s0':>8} {'v6 s1':>8} {'W/L':>4} | {'v5 s0':>8} {'k16 s1':>8} {'W/L':>4} | {'delta$ s1':>9}")
    fl = []
    for s in sorted(v6):
        if s not in base:
            continue
        a, b = v6[s], base[s]
        w6 = (a["a_seat0"] > a["b_seat1"]) + (a["a_seat1"] > a["b_seat0"])
        wb = (b["a_seat0"] > b["b_seat1"]) + (b["a_seat1"] > b["b_seat0"])
        d0 = a["a_seat0"] - a["b_seat1"]
        d1 = a["a_seat1"] - a["b_seat0"]
        mark = "  <-- FLIP" if w6 != wb else ""
        print(f"{s:>5} {a['a_seat0']:>8,.0f} {a['b_seat1']:>8,.0f} {w6:>4} | "
              f"{b['a_seat0']:>8,.0f} {b['b_seat1']:>8,.0f} {wb:>4} | {d0:>+9,.0f}")
        print(f"{s:>5} {a['b_seat0']:>8,.0f} {a['a_seat1']:>8,.0f} {w6:>4} | "
              f"{b['b_seat0']:>8,.0f} {b['a_seat1']:>8,.0f} {wb:>4} | {d1:>+9,.0f}{mark}")
        if w6 != wb:
            fl.append((s, wb, w6))
    print(f"\nflips: {len(fl)}  {fl}")
    print(f"v6 sum: {load(v6_file)['summary']}")
    print(f"base:   {load(base_file)['summary']}")


if __name__ == "__main__":
    main()
