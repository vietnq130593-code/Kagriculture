#!/usr/bin/env python3
"""Phase 5.5 — HỌC PROFILE L1 OFFLINE từ thư viện bot (PLAN §4.1 gốc).

Chạy v5 đấu từng bot (v4 / v3 / melon / baseline) trên N seed, đọc thẳng
tm["opp_daily"] từ module v5 sau khi trận kết thúc (telemetry $0-residual đã
kiểm chứng) → bảng flow trung bình từng mặt hàng theo archetype đối thủ.

Dùng để: (1) đối chiếu PROFILES viết tay trong _bayes_step, (2) cập nhật
profile đúng số liệu nếu lệch — L1 bớt đọc nhầm (bài học r1-r4: flow-mix của
đối thủ là tín hiệu thật nhưng profile sai làm posterior vọt nhầm).

In:  python3 profile_collect.py [n_seeds]
Out: bench/profiles_learned.json + bảng tóm tắt stdout
"""
import importlib.util
import json
import os
import sys

ROOT = "/home/z/my-project/kaggriculture"
BENCH = os.path.join(ROOT, "bench")
sys.path.insert(0, ROOT)
sys.path.insert(0, BENCH)

from kaggle_environments import make  # noqa: E402

BOTS = {
    "v4": (os.path.join(ROOT, "v4.py"), "agent", "CONTEST"),
    "v3": (os.path.join(ROOT, "v3.py"), "agent", "CONTEST-v3"),
    "melon": (os.path.join(BENCH, "melon.py"), "melon_maxxer", "DUMP-melon"),
    "baseline": (os.path.join(BENCH, "baseline.py"), "agent", "PASSIVE-base"),
}


def load(path, tag):
    modname = f"prof_{tag}_{os.path.splitext(os.path.basename(path))[0]}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    seeds = list(range(200, 200 + n_seeds))
    v5_path = os.path.join(ROOT, "v5.py")
    out = {}
    for name, (path, entry, arch) in BOTS.items():
        acc = {}
        per_seed_money = []
        for s in seeds:
            # v5 ngồi ghế 0; bot ghế 1 (đổi ghế không đổi flow-đặc trưng của bot)
            v5mod = load(v5_path, f"{name}_{s}")
            botmod = load(path, f"bot_{name}_{s}")
            fnA = getattr(v5mod, "agent")
            fnB = getattr(botmod, entry)
            env = make("kaggriculture", debug=False, configuration={"seed": s})
            env.run([fnA, fnB])
            r0 = float(env.steps[-1][0].reward or 0)
            r1 = float(env.steps[-1][1].reward or 0)
            per_seed_money.append((r0, r1))
            tm = (getattr(v5mod, "_STATE", {}) or {}).get("tm", {}) or {}
            od = tm.get("opp_daily") or {}
            # trung bình flow theo ngày (chỉ ngày 7-28: sau warmup, trước thanh lý)
            days = [k for k in od if isinstance(k, int) and 7 <= k <= 28]
            for k in days:
                for p, v in (od.get(k) or {}).items():
                    if isinstance(v, (int, float)):
                        acc.setdefault(p, []).append(float(v))
            # dọn module state để seed kế không nhiễm
            try:
                v5mod._STATE.clear()
                sys.modules.pop(getattr(v5mod, "__name__", ""), None)
            except Exception:
                pass
        prof = {}
        for p, xs in acc.items():
            n = len(xs)
            prof[p] = {
                "mean": round(sum(xs) / n, 2),
                "p25": round(sorted(xs)[max(0, n // 4)], 2),
                "p75": round(sorted(xs)[min(n - 1, 3 * n // 4)], 2),
                "n_days": n,
            }
        avg_me = sum(m for m, _ in per_seed_money) / len(per_seed_money)
        avg_op = sum(o for _, o in per_seed_money) / len(per_seed_money)
        out[name] = {"arch": arch, "profile": prof,
                     "avg_money": [round(avg_me), round(avg_op)],
                     "seeds": seeds}
        print(f"\n=== {name} ({arch}) — v5 ${avg_me:,.0f} vs bot ${avg_op:,.0f} ===")
        for p in ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                  "EGG", "MILK", "WOOL", "FERTILIZER"):
            if p in prof:
                q = prof[p]
                print(f"  {p:11s} mean {q['mean']:6.1f}  P25 {q['p25']:6.1f}  P75 {q['p75']:6.1f}")
    with open(os.path.join(BENCH, "profiles_learned.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("\nsaved bench/profiles_learned.json")


if __name__ == "__main__":
    main()
