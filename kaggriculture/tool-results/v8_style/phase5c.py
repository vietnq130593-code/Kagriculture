#!/usr/bin/env python3
"""PHASE 5C — style metrics v8-mới (vòng 45) vs top-3 + exact ledger."""
import json, glob, sys
from collections import defaultdict
sys.path.insert(0, "/home/z/my-project/tool-results/v8_style")
from analyze_style import load_any, unit_positions, man, SPAWN, BOARD

sys.path.insert(0, "/home/z/my-project/kaggriculture")
from v8 import ANIMALS

def block_stats(atiles):
    if not atiles:
        return {"n": 0, "ncomp": 0, "big_share": 0.0, "adj_pct": 0.0, "d_shed": None}
    S = set((x, y) for (x, y, k, a) in atiles)
    seen, comps = set(), []
    for p in sorted(S):
        if p in seen: continue
        stack, comp = [p], set()
        seen.add(p)
        while stack:
            cx, cy = stack.pop(); comp.add((cx, cy))
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                q = (cx+dx, cy+dy)
                if q in S and q not in seen:
                    seen.add(q); stack.append(q)
        comps.append(comp)
    big = max(len(c) for c in comps)
    adj = sum(1 for (x, y) in S if any((x+dx, y+dy) in S for dx, dy in ((1,0),(-1,0),(0,1),(0,-1))))
    ds = [man((x, y), SPAWN) for (x, y, k, a) in atiles]
    return {"n": len(atiles), "ncomp": len(comps), "big_share": big/len(atiles),
            "adj_pct": adj/len(atiles), "d_shed": sum(ds)/len(ds)}

def analyze(path, pidx):
    steps, names = load_any(path)
    daily = {}
    walk = 0.0; prev = None
    ops = defaultdict(int)
    for s in steps:
        farm = s["farms"][pidx]
        pos = unit_positions(farm)
        if prev is not None and len(pos) == len(prev):
            walk += sum(man(a,b) for a,b in zip(pos, prev))
        prev = pos
        act = (s["acts"] or [None,None])[pidx]
        if act:
            for u in ([act.get("farmer")] + list(act.get("hands") or [])):
                if u and u[0] not in ("NORTH","SOUTH","EAST","WEST"):
                    ops[u[0]] += 1
                elif u:
                    ops["MOVE"] += 1
        if s["hour"] == 23 or s["t"] >= len(steps)-1:
            plants = defaultdict(int); animals = []; dead = 0; weeds = 0
            for y in range(BOARD):
                for x in range(BOARD):
                    t = farm["tiles"][y][x]
                    if t == "LOCKED" or t == "SHED": continue
                    if t is None: dead += 1
                    elif t.get("kind") == "WEED": dead += 1; weeds += 1
                    elif t.get("kind") == "PLANT": plants[t.get("crop")] += 1
                    elif t.get("kind") in ("COOP","PASTURE"): animals.append((x,y,t.get("kind"),t.get("animal")))
            daily[s["day"]] = {"dead": dead, "weeds": weeds,
                               "plants": dict(plants), "n_plants": sum(plants.values()),
                               "animals": len(animals), "block": block_stats(animals),
                               "money": farm.get("money")}
    return {"daily": daily, "final": steps[-1]["farms"][pidx].get("money"),
            "walk": walk, "ops": dict(ops), "names": names}

V8, V7 = [], []
for path in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/new45/*.jsonl")):
    seatA = "seatA" in path
    V8.append(analyze(path, 0 if seatA else 1))
    V7.append(analyze(path, 1 if seatA else 0))

def grp(Rs):
    n = len(Rs)
    alld = sorted(set(d for R in Rs for d in R["daily"]))
    dead = {d: sum(R["daily"][d]["dead"] for R in Rs if d in R["daily"])/n for d in alld}
    blk = {d: (sum(R["daily"][d]["block"]["ncomp"] for R in Rs if d in R["daily"])/n,
               sum(R["daily"][d]["block"]["big_share"] for R in Rs if d in R["daily"] and R["daily"][d]["animals"]>0)/n,
               sum(R["daily"][d]["block"]["adj_pct"] for R in Rs if d in R["daily"] and R["daily"][d]["animals"]>0)/n,
               sum(R["daily"][d]["block"]["d_shed"] for R in Rs if d in R["daily"] and R["daily"][d]["block"]["d_shed"] is not None)/n) for d in alld}
    plants = {d: sum(R["daily"][d]["n_plants"] for R in Rs if d in R["daily"])/n for d in alld}
    herd = {d: sum(R["daily"][d]["animals"] for R in Rs if d in R["daily"])/n for d in alld}
    mix = defaultdict(float)
    for R in Rs:
        for d in range(5, 28):
            for c, k in R["daily"].get(d, {"plants": {}})["plants"].items():
                mix[c] += k
    ops = defaultdict(float)
    for R in Rs:
        for op, v in R["ops"].items(): ops[op] += v
    return {"dead": dead, "blk": blk, "plants": plants, "herd": herd,
            "mix": {c: v/n/22 for c, v in mix.items()},
            "ops": {op: v/n for op, v in ops.items()},
            "final": sum(R["final"] for R in Rs)/n}

G8 = grp(V8)
print("=== V8-MỚI (vòng 45) 6 game vs v7 — final TB $%.0f" % G8["final"])
print("Đất chết mỗi ngày:", " ".join("d%d:%.0f" % (d, G8["dead"][d]) for d in range(0, 30, 2)))
print("Đàn mỗi ngày:    ", " ".join("d%d:%.1f" % (d, G8["herd"][d]) for d in range(0, 30, 2)))
print("Cây đứng mỗi ngày:", " ".join("d%d:%.0f" % (d, G8["plants"][d]) for d in range(0, 30, 2)))
v = [G8["blk"][d] for d in range(10, 28)]
print("Block d10-27: ncomp=%.2f big_share=%.2f adj=%.2f d̄shed=%.2f" % (
    sum(x[0] for x in v)/len(v), sum(x[1] for x in v)/len(v),
    sum(x[2] for x in v)/len(v), sum(x[3] for x in v)/len(v)))
print("Cơ cấu cây TB d5-27:", {c: round(x,1) for c, x in sorted(G8["mix"].items())})
print("OPS mùa:", {op: round(v) for op, v in sorted(G8["ops"].items(), key=lambda kv: -kv[1])[:12]})
print("MOVE%%: %.0f%%" % (100*G8["ops"].get("MOVE",0)/sum(G8["ops"].values())))
# dead avg d9-27
print("Đất chết TB d9-27: %.1f ô (top-3: 1.76, v8-cũ: 7.9)" % (sum(G8["dead"][d] for d in range(9,28))/19))
