#!/usr/bin/env python3
"""Report v8 vs top-3 style comparison from style_agg.json."""
import json
from collections import defaultdict

D = json.load(open("/home/z/my-project/tool-results/v8_style/style_agg.json"))

TOP3 = ["107559251#0:SpaTaro", "107573831#0:SpaTaro",
        "107559251#1:Unknown Mother-Goose", "107573831#1:Otter Vibe"]
V8 = [k for k in D if k.startswith("v8_seatA") and "#0" in k] + \
     [k for k in D if k.startswith("v8_seatB") and "#1" in k]
V7 = [k for k in D if k.startswith("v8_seatA") and "#1" in k] + \
     [k for k in D if k.startswith("v8_seatB") and "#0" in k]


def grp(keys):
    return [D[k] for k in keys]


def fm(x):
    return f"{x:,.0f}" if isinstance(x, (int, float)) else str(x)


print("=" * 100)
print("1) ĐỘNG VẬT — PHÂN BỔ MUA & VỊ TRÍ Ô NUÔI")
print("=" * 100)
for label, keys in (("TOP-3", TOP3), ("V8", V8), ("V7", V7)):
    print(f"\n--- {label} ---")
    for k in keys:
        R = D[k]
        buys = {d: v for d, v in R["buys"].items()}
        tot = defaultdict(int)
        for d, v in buys.items():
            for a, n in v.items():
                tot[a] += n
        first = {}
        for d in sorted(buys, key=int):
            for a in buys[d]:
                first.setdefault(a, f"d{d}")
        pl = R["placement"]
        geo = []
        for day in ("10", "20", "28"):
            p = pl.get(day)
            if p:
                geo.append(f"d{day}: n={p['n']} d̄shed={p['d_shed_avg']:.1f} bbox={p['bbox']} Q={p['quads']}")
        print(f"  {k.split(':')[0][:26]:<27} herd cuối={R['daily_animals'].get('28')} mua={dict(tot)} first={first}")
        for g in geo:
            print(f"      {g}")

print()
print("=" * 100)
print("2) VỊ TRÍ ĐỘNG VẬT → NHÂN CÔNG")
print("=" * 100)
print(f"{'player':<28} {'acts/ngày':>9} {'MOVE%':>6} {'đi bộ/ngày':>10} "
      f"{'FEED d̄':>8} {'CARE d̄':>8} {'CFERT d̄':>9} {'WATER d̄':>9} {'HARV d̄':>8}")
for label, keys in (("TOP-3", TOP3), ("V8", V8), ("V7", V7)):
    print(f"--- {label} ---")
    for k in keys:
        R = D[k]
        L = R["labor"]
        svc = L["svc_loc"]
        fld = L["field_loc"]

        def d_(m, op):
            v = m.get(op)
            return f"{v[0]:.1f}×{v[1]}" if v else "-"

        print(f"  {k.split(':')[0][:26]:<28} {L['per_day']:>9.1f} {L['move_frac']*100:>5.1f}% "
              f"{L['walk_per_day']:>10.1f} {d_(svc,'FEED'):>8} {d_(svc,'CARE'):>8} "
              f"{d_(svc,'COLLECT_FERTILIZER'):>9} {d_(fld,'WATER'):>9} {d_(fld,'HARVEST'):>8}")

print()
print("=" * 100)
print("3) ĐẤT TRỐNG TOÀN TRẬN")
print("=" * 100)
for label, keys in (("TOP-3", TOP3), ("V8", V8), ("V7", V7)):
    print(f"\n--- {label} ---")
    for k in keys:
        R = D[k]
        E = R["empty"]
        ww = E["worst_window"]
        print(f"  {k.split(':')[0][:26]:<27} emptyTB d9-27={E['empty_avg_d9_27']:.1f} ô "
              f"weedTB={E['weeds_avg_d9_27']:.1f} | cửa sổ tệ: d{ww[0]}-d{ww[1]} "
              f"({ww[2]} ngày, TB {ww[3]:.1f} ô trống) | max 1 ngày: {E['max_empty_day']}")

print()
print("=" * 100)
print("4) CHUỖI EMPTY THEO NGÀY (end-of-day)")
print("=" * 100)
days = [str(d) for d in range(30)]
for label, keys in (("TOP-3", TOP3), ("V8", V8), ("V7", V7)):
    print(f"\n--- {label} ---")
    for k in keys:
        E = D[k]["empty"]
        row = " ".join(f"{E['per_day'].get(d, '-')}" for d in days)
        print(f"  {k.split(':')[0][:26]:<27} {row}")

print()
print("=" * 100)
print("5) TIỀN + ĐÀN + CÂY ĐỨNG (ngày 20 & 28)")
print("=" * 100)
for label, keys in (("TOP-3", TOP3), ("V8", V8), ("V7", V7)):
    print(f"\n--- {label} ---")
    for k in keys:
        R = D[k]
        for day in ("20", "28"):
            an = R["daily_animals"].get(day) or {}
            pl = R["daily_plants"].get(day) or {}
            pl_s = " ".join(f"{c[:4]}×{n}" for c, n in sorted(pl.items(), key=lambda x: -x[1]))
            print(f"  {k.split(':')[0][:26]:<27} d{day}: đàn={an} cây: {pl_s}")
        print(f"      final={fm(R['final_money'])} sells={R['animal_sells']} land d={sorted(set(R['land_days']))}")
