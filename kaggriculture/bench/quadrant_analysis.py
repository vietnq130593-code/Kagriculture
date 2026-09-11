#!/usr/bin/env python3
"""Kinh tế biên của QUADRANT ĐẤT: quadrant nào trồng gì, giá trị bao nhiêu.

Quadrant: NW(mặc định), NE($1k), SW($2k), SE($4k) — LAND_ORDER [NE,SW,SE].
Quadrant của ô (10x10): x<5,y<5=NW; x>=5,y<5=NE; x<5,y>=5=SW; else SE.
Đo: cây theo quadrant từng ngày + tổng chi hire + doanh thu wheat/straw.
"""
import json, sys, glob, os
from collections import defaultdict

def q_of(x, y):
    if x < 5 and y < 5: return "NW"
    if x >= 5 and y < 5: return "NE"
    if x < 5 and y >= 5: return "SW"
    return "SE"

def main(paths):
    agg = defaultdict(lambda: defaultdict(float))  # qname -> crop -> avg standing
    n_games = 0
    hire_cost_tot = 0
    for path in paths:
        n_games += 1
        with open(path) as f:
            for line in f:
                d = json.loads(line)
                if d.get("t") != "turn":
                    continue
                day = d.get("day", d["step"] // 24)
                if day not in (13, 17, 21) or d.get("hour") not in (0,):
                    continue
                # v5 = pid theo hello
                pass
    # đơn giản: đo lại 1 vòng với pid v5
    for path in paths:
        a = b = None
        with open(path) as f:
            for line in f:
                d = json.loads(line)
                if d.get("t") == "hello":
                    a, b = d.get("a"), d.get("b")
                    v5pid = 0 if a == "v5" else 1
                elif d.get("t") == "turn":
                    day = d.get("day", d["step"] // 24)
                    hour = d.get("hour")
                    if day in (13, 17, 21) and hour == 0:
                        farm = d["farms"][v5pid]
                        for y, row in enumerate(farm["tiles"]):
                            for x, t in enumerate(row):
                                if isinstance(t, dict) and t.get("kind") == "PLANT":
                                    agg[q_of(x, y)][t.get("crop")] += 1
    print(f"=== CÂY ĐỨNG THEO QUADRANT (v5, ngày 13/17/21, {n_games} trận, đơn vị: ô-cây) ===")
    for q in ("NW", "NE", "SW", "SE"):
        tot = sum(agg[q].values())
        detail = dict(sorted(agg[q].items(), key=lambda kv: -kv[1]))
        print(f"{q}: tổng {tot:,.0f} ({tot/n_games:,.1f}/trận/ngày-đo) — {detail}")

if __name__ == "__main__":
    files = sorted(glob.glob("/home/z/my-project/kaggriculture/battles/*.jsonl"))
    main(files[-20:])
