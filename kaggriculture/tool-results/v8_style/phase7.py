#!/usr/bin/env python3
"""PHASE 7 (Vòng 48) — user: "tôi vẫn chưa rõ quá trình, nguyên nhân dẫn đến
3 top hạng cao nhất có thể đạt được 90-110k. Đánh giá lại quá trình, các bước
tăng trưởng và nguyên nhân"

Xuất bảng TĂNG TRƯỞNG THEO PHA cho từng seat top-3 + TB v8 (6 game):
  Pha 1 (d0-9)   BOOTSTRAP   — dựng máy (đất+thú+hạt), tiền đi ngang/tụt
  Pha 2 (d10-18) MỞ RỘNG     — capex kết thúc từng loại, rev bắt đầu vượt chi
  Pha 3 (d19-25) CỖ MÁY      — net +$3-6k/ngày
  Pha 4 (d26-29) VỀ ĐÍCH     — thanh lý, hire tới phút chót, shed rỗng

Mỗi pha: rev/day, spend/day, net/day, kênh rev chính, tiền cuối pha,
% final tích lũy trong pha, và mốc "capex kết thúc" từng loại.
"""
import json
import glob
import sys
from collections import defaultdict

sys.path.insert(0, "/home/z/my-project/tool-results/v8_style")
from phase6 import top3_trace, v8_trace  # reuse exact loaders

R2 = "/home/z/my-project/tool-results/"
NEW46 = "/home/z/my-project/tool-results/v8_style/new46/"
GOD46 = "/tmp/god46_%s.json"

PHASES = [("P1 d0-9 BOOTSTRAP", 0, 9), ("P2 d10-18 MỞ RỘNG", 10, 18),
          ("P3 d19-25 CỖ MÁY", 19, 25), ("P4 d26-29 VỀ ĐÍCH", 26, 29)]

TOP3 = [(R2 + "r2_god_M1.json", 0, "SpaTaro·M1"), (R2 + "r2_god_M1.json", 1, "UMG·M1"),
        (R2 + "r2_god_M2.json", 0, "SpaTaro·M2"), (R2 + "r2_god_M2.json", 1, "Otter·M2")]


def phase_rows(T):
    """Trả list row từng pha + mốc capex."""
    rows = []
    for name, a, b in PHASES:
        nd = b - a + 1
        rev = sum(T["rev_day"].get(d, 0.0) for d in range(a, b + 1))
        spn = defaultdict(float)
        for d in range(a, b + 1):
            for k, v in (T["spend_day"].get(d) or {}).items():
                spn[k] += v
        spend = sum(spn.values())
        rows.append({
            "name": name, "n": nd, "rev": rev, "rev_d": rev / nd,
            "spend": spend, "spend_d": spend / nd, "net": rev - spend,
            "net_d": (rev - spend) / nd, "end_money": T["money"].get(b, 0.0),
            "rev_ch": {k: v for k, v in defaultdict(float, {
                k: sum(T["rev_ch"].get(k, 0.0) for _ in [0])}).items()},
        })
    # rev theo kênh THEO PHA — cần tính lại từ commit_log? phase6 chỉ có tổng
    # kênh; dùng spend_day chi tiết + rev_day để pha hóa net thôi, kênh theo
    # tỉ lệ toàn mùa của rev_ch.
    tot_ch = sum(T["rev_ch"].values()) or 1.0
    for r in rows:
        r["ch_mix"] = sorted(T["rev_ch"].items(), key=lambda kv: -kv[1])[:3]
        r["ch_share"] = [(k, round(v / tot_ch * 100)) for k, v in r["ch_mix"]]
    return rows


def capex_marks(T):
    """Ngày MUA CUỐI theo loại — mốc 'không còn gì để mua'."""
    last_animal = max([d for sp in ("COW", "SHEEP", "GOOSE")
                       for d in T["buys"].get(sp, {})] or [-1])
    land_days = [d for (d, q, c) in T["land_days"]]
    return {"animal_last": last_animal, "land_last": max(land_days) if land_days else -1,
            "hire_last": max(T["hire_days"]) if T["hire_days"] else -1}


def fmt_money(v):
    return "$%s" % format(int(round(v)), ",")


def print_seat(label, T):
    rows = phase_rows(T)
    mk = capex_marks(T)
    final = T["final"]
    print("\n=== %s — final %s ===" % (label, fmt_money(final)))
    print("  capex-kết: thú cuối d%d · LAND xong d%d · HIRE cuối d%d"
          % (mk["animal_last"], mk["land_last"], mk["hire_last"]))
    print("  %-20s %8s %8s %8s %9s %6s  %s" %
          ("PHA", "rev/ng", "chi/ng", "net/ng", "tiền@cuối", "%final", "kênh chính"))
    cum0 = 3000.0
    for r in rows:
        pct = (r["end_money"] - cum0) / (final - 3000) * 100 if final > 3000 else 0
        cum0 = r["end_money"]
        print("  %-20s %8s %8s %8s %9s %+5.0f%%  %s" %
              (r["name"], fmt_money(r["rev_d"]), fmt_money(r["spend_d"]),
               ("%+s" % fmt_money(r["net_d"]))[0] + fmt_money(abs(r["net_d"])),
               fmt_money(r["end_money"]), pct,
               "/".join("%s%d%%" % (k, s) for k, s in r["ch_share"])))
    # đường tiền chi tiết 5 ngày then chốt
    print("  tiền: d0 $3,000", end="")
    for d in (5, 9, 12, 15, 18, 21, 24, 27, 29):
        if d in T["money"]:
            print(" → d%d %s" % (d, fmt_money(T["money"][d])), end="")
    print()


def main():
    print("########## TOP-3 (4 seat) ##########")
    for path, pidx, label in TOP3:
        T = top3_trace(path, pidx)
        print_seat(label, T)

    print("\n########## V8 (TB 6 game) ##########")
    agg = None
    games = []
    for jl in sorted(glob.glob(NEW46 + "*.jsonl")):
        tag = jl.split("/")[-1].replace(".jsonl", "")
        g = GOD46 % tag
        pidx = 0 if "seatA" in tag else 1
        T = v8_trace(jl, g, pidx)
        games.append(T)
    if games:
        # gộp TB
        agg = {"final": sum(t["final"] for t in games) / len(games),
               "rev_day": defaultdict(float), "spend_day": defaultdict(dict),
               "money": defaultdict(list), "rev_ch": defaultdict(float),
               "buys": defaultdict(lambda: defaultdict(int)),
               "hire_days": set(), "land_days": []}
        mon_days = set()
        for t in games:
            for d, v in t["rev_day"].items():
                agg["rev_day"][d] += v / len(games)
            for d, kvs in t["spend_day"].items():
                for k, v in kvs.items():
                    agg["spend_day"].setdefault(d, defaultdict(float))[k] += v / len(games)
            for d, v in t["money"].items():
                agg["money"][d] = agg["money"].get(d, 0) + v
                mon_days.add(d)
            for k, v in t["rev_ch"].items():
                agg["rev_ch"][k] += v / len(games)
            for sp in ("COW", "SHEEP", "GOOSE"):
                for d, n in t["buys"].get(sp, {}).items():
                    agg["buys"][sp][d] += n / len(games)
            agg["hire_days"] |= t["hire_days"]
            agg["land_days"] += t["land_days"]
        for d in mon_days:
            agg["money"][d] /= len(games)
        agg["money"] = dict(agg["money"])
        agg["spend_day"] = {d: dict(kv) for d, kv in agg["spend_day"].items()}
        agg["buys"] = {sp: dict(agg["buys"][sp]) for sp in agg["buys"]}
        print_seat("V8-TB(6 game)", agg)

    # Bảng phụ: NET/ngày của từng khoảng 5 ngày để thấy BƯỚC TĂNG TRƯỞNG
    print("\n### BƯỚC TĂNG TRƯỞNG — net/ngày (rev−chi) theo cửa sổ 5 ngày ###")
    print("%-6s" % "cửa", end="")
    for _, _, label in TOP3:
        print(" %12s" % label.split("·")[0], end="")
    print(" %12s" % "V8-TB")
    for a in (0, 5, 10, 15, 20, 25):
        b = min(29, a + 4)
        print("d%-4d" % a, end="")
        for path, pidx, label in TOP3:
            T = top3_trace(path, pidx)
            rev = sum(T["rev_day"].get(d, 0) for d in range(a, b + 1))
            sp = sum(sum((T["spend_day"].get(d) or {}).values()) for d in range(a, b + 1))
            print(" %+12s" % ("$%+d" % int((rev - sp) / (b - a + 1))), end="")
        if agg:
            rev = sum(agg["rev_day"].get(d, 0) for d in range(a, b + 1))
            sp = sum(sum((agg["spend_day"].get(d) or {}).values()) for d in range(a, b + 1))
            print(" %+12s" % ("$%+d" % int((rev - sp) / (b - a + 1))))
        else:
            print()


if __name__ == "__main__":
    main()
