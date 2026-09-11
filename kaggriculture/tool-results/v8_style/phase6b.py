#!/usr/bin/env python3
"""PHASE 6B (Task 46) — phụ trợ: units/hands theo ngày + doanh thu 5 ngày cuối.
Metric mới (gap B0): LAO ĐỘNG MỖI NGÀY (hands/day) — phát hiện v8 = 0 hands d29."""
import json
import glob
from collections import defaultdict


def kaggle_units(path):
    """snapshot h22 (post-action, thấy đủ) -> hands per day."""
    d = json.load(open(path))
    out = {0: defaultdict(list), 1: defaultdict(list)}
    rev = {0: defaultdict(float), 1: defaultdict(float)}
    for snap in d["snapshots"]:
        day, h = snap["day"], snap["hour"]
        for p in (0, 1):
            if h == 22:
                out[p][day].append(len(snap["p%d" % p].get("hands") or []))
    for (t, p, op, item, price) in d["commit_log"]:
        if op == "SELL":
            day = (t - 1) // 24
            rev[p][day] += price
    return {p: {d_: sum(v) / len(v) for d_, v in out[p].items()} for p in (0, 1)}, rev


def arena_units(path, pidx):
    turns = []
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") == "turn":
                turns.append(d)
    hands = defaultdict(list)
    for t in turns:
        hands[t["day"]].append(len(t["farms"][pidx].get("hands") or []))
    return {d_: sum(v) / len(v) for d_, v in hands.items()}


if __name__ == "__main__":
    print("=== UNITS (1+n hands) THEO NGÀY — TOP3(4 seat) vs V8(6 game) ===")
    T3h = []
    for f in ("M1", "M2"):
        u, rev = kaggle_units("/home/z/my-project/tool-results/r2_god_%s.json" % f)
        T3h.append((u[0], rev[0]))
        T3h.append((u[1], rev[1]))
    n = len(T3h)
    print("TOP3 hands/ngày:", " ".join("d%d:%.1f" % (d, sum(u.get(d, 0) for u, _ in T3h) / n)
                                       for d in range(0, 30, 2)))
    V8h = []
    for p in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/new46/*.jsonl")):
        seatA = "seatA" in p
        V8h.append(arena_units(p, 0 if seatA else 1))
    n8 = len(V8h)
    print("V8   hands/ngày:", " ".join("d%d:%.1f" % (d, sum(u.get(d, 0) for u in V8h) / n8)
                                       for d in range(0, 30, 2)))

    print("\n=== DOANH THU 5 NGÀY CUỐI (TB nhóm) ===")
    g = json.load(open("/tmp/god46_v8n_seatA_s100.json"))
    v8rev = defaultdict(float)
    for f in sorted(glob.glob("/tmp/god46_v8n_*.json")):
        seatA = "seatA" in f
        p = 0 if seatA else 1
        for (t, pl, op, item, price) in json.load(open(f))["commit_log"]:
            if op == "SELL" and pl == p:
                v8rev[t // 24] += price / n8
    print("TOP3 rev:", " ".join("d%d:$%.0f" % (d, sum(r.get(d, 0) for _, r in T3h) / n)
                                for d in range(25, 30)))
    print("V8   rev:", " ".join("d%d:$%.0f" % (d, v8rev.get(d, 0)) for d in range(25, 30)))

    print("\n=== TIỀN CUỐI NGÀY 5 NGÀY CUỐI (TB nhóm) ===")
    t3m = defaultdict(float)
    for f in ("M1", "M2"):
        d = json.load(open("/home/z/my-project/tool-results/r2_god_%s.json" % f))
        for snap in d["snapshots"]:
            if snap["hour"] == 23:
                for p in (0, 1):
                    t3m[snap["day"]] += snap["money"][p] / 4
    if 29 not in t3m:
        t3m[29] = sum(d["rewards"][p] for d in
                      [json.load(open("/home/z/my-project/tool-results/r2_god_%s.json" % f))
                       for f in ("M1", "M2")] for p in (0, 1)) / 4
    print("TOP3:", " ".join("d%d:$%.0f" % (d, t3m[d]) for d in range(25, 30)))
    v8m = defaultdict(float)
    for p_ in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/new46/*.jsonl")):
        seatA = "seatA" in p_
        p = 0 if seatA else 1
        with open(p_) as fh:
            for line in fh:
                d = json.loads(line)
                if d.get("t") == "turn" and d["hour"] == 23:
                    v8m[d["day"]] += d["farms"][p]["money"] / n8
                elif d.get("t") == "end":
                    v8m[29] += d["rewards"][p] / n8
    print("V8  :", " ".join("d%d:$%.0f" % (d, v8m[d]) for d in range(25, 30)))
