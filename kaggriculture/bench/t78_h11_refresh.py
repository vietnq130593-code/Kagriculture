#!/usr/bin/env python3
"""t78_h11_refresh.py — H11 daily-replay refresh pipeline (Task 78).

End-to-end: pull kaggle/kaggressurE-episodes-index -> latest daily dataset ->
manifest.csv -> top-N episodes by avg Elo -> download -> extract per-seat
tape signatures (sell hour histogram, product mix, land count, hires, money) ->
diff vs v16's own tape signatures -> drift report.

Outputs: bench/t78_h11_tapes/*.json, bench/t78_h11_report.json, bench/t78_h11_report.md
Auth: KAGGLE_TOKEN env (KGAT bearer) or fallback from worklog (as before).
"""
import io
import json
import os
import subprocess
import sys
import zipfile
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TAPES_DIR = os.path.join(HERE, "t78_h11_tapes")
API = "https://www.kaggle.com/api/v1"


def api_get(path, out):
    subprocess.run(["curl", "-s", "-m", "300", "-L",
                    f"{API}/{path}", "-o", out], check=True)
    return out


def read_maybe_zip(path):
    raw = open(path, "rb").read()
    if raw[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(raw))
        name = z.namelist()[0]
        return z.read(name).decode("utf-8", "replace")
    return raw.decode("utf-8", "replace")


def latest_daily():
    api_get("datasets/list?search=episodes-index&pageSize=40", "/tmp/h11_search.json")
    refs = json.load(open("/tmp/h11_search.json"))
    refs = refs if isinstance(refs, list) else refs.get("datasets", [])
    ref = next(r["ref"] for r in refs
               if r["ref"].split("/")[0] == "kaggle" and r["ref"].endswith("-episodes-index"))
    api_get(f"datasets/download/{ref}", "/tmp/h11_index.zip")
    txt = read_maybe_zip("/tmp/h11_index.zip")
    lines = txt.strip().split("\n")
    hdr = lines[0].split(",")
    rows = [dict(zip(hdr, l.split(","))) for l in lines[1:]]
    rows.sort(key=lambda r: r["date"])
    return rows


def ep_signature(d):
    steps = d["steps"]
    info = d.get("info", {})
    sig = {
        "episode_id": info.get("EpisodeId"),
        "teams": info.get("TeamNames"),
        "seed": info.get("seed"),
        "rewards": d.get("rewards"),
        "seats": [],
    }
    agg = []
    for p in (0, 1):
        a = {"sells_by_hour": defaultdict(int), "sells_by_product": defaultdict(int),
             "units": 0, "hires": 0, "quads_final": 0, "animals_final": {}, "crops_final": {},
             "money_final": 0, "buys_animal": defaultdict(int)}
        for t, step in enumerate(steps):
            act = (step[p].get("action") or {})
            hour = t % 24
            for o in act.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    a["sells_by_hour"][hour] += 1
                    a["sells_by_product"][o[1]] += max(0, int(o[2] or 0))
                    a["units"] += max(0, int(o[2] or 0))
                elif isinstance(o, list) and o and o[0] == "HIRE":
                    a["hires"] += 1
                elif isinstance(o, list) and len(o) >= 2 and o[0] in ("BUY", "BUY_PRODUCT"):
                    if o[1] in ("GOOSE", "COW", "SHEEP"):
                        a["buys_animal"][o[1]] += 1
        obs = steps[-1][0]["observation"]
        farm = obs["farms"][p]
        a["quads_final"] = len(farm.get("unlocked_quadrants") or [])
        a["money_final"] = round(float(farm.get("money", 0) or 0))
        cc = defaultdict(int)
        for row in farm.get("tiles") or []:
            for tile in row:
                if isinstance(tile, dict):
                    k = tile.get("kind")
                    if k == "PLANT":
                        cc["crop:" + str(tile.get("crop"))] += 1
                    elif k in ("COOP", "PASTURE"):
                        cc["animal:" + str(tile.get("animal"))] += 1
        a["crops_final"] = {k: v for k, v in cc.items() if k.startswith("crop:")}
        a["animals_final"] = {k: v for k, v in cc.items() if k.startswith("animal:")}
        agg.append(a)
    for p in (0, 1):
        sig["seats"].append({
            "money": agg[p]["money_final"], "units": agg[p]["units"], "hires": agg[p]["hires"],
            "quads": agg[p]["quads_final"],
            "sells_by_hour": {str(k): v for k, v in agg[p]["sells_by_hour"].items()},
            "sells_by_product": dict(agg[p]["sells_by_product"]),
            "crops_final": agg[p]["crops_final"], "animals_final": agg[p]["animals_final"],
            "buys_animal": dict(agg[p]["buys_animal"]),
        })
    return sig


def v16_signatures():
    sys.path.insert(0, ROOT)
    import importlib.util
    spec = importlib.util.spec_from_file_location("_v16_h11", os.path.join(ROOT, "v16.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_v16_h11"] = mod
    spec.loader.exec_module(mod)
    routes = mod._ROUTES
    keys = sorted(routes) if isinstance(routes, dict) else range(len(routes))
    sigs = []
    for ri in keys:
        tape = routes[ri]
        hh = defaultdict(int)
        pp = defaultdict(int)
        for t, a in enumerate(tape):
            if not isinstance(a, dict):
                continue
            for o in a.get("market") or []:
                if isinstance(o, list) and len(o) >= 3 and o[0] == "SELL":
                    hh[t % 24] += 1
                    pp[o[1]] += max(0, int(o[2] or 0))
        sigs.append({"route": ri, "sells_by_hour": dict(hh), "sells_by_product": dict(pp)})
    return sigs


def cosine(a, b):
    ka = set(a) | set(b)
    num = sum(a.get(k, 0) * b.get(k, 0) for k in ka)
    na = sum(v * v for v in a.values()) ** 0.5
    nb = sum(v * v for v in b.values()) ** 0.5
    return num / max(1e-9, na * nb)


def main():
    n_top = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    os.makedirs(TAPES_DIR, exist_ok=True)

    print("[1/4] pulling episodes index ...")
    idx = latest_daily()
    latest = idx[-1]
    print(f"  latest daily: {latest['date']} episodes={latest['episode_count']} "
          f"top_elo={float(latest['top_avg_score']):.1f}")
    week = idx[-8:]
    elo_trend = [(r["date"], float(r["top_avg_score"])) for r in week]

    print("[2/4] pulling daily manifest ...")
    daily = latest["daily_dataset_slug"]
    api_get(f"datasets/download/kaggle/{daily}/manifest.csv", "/tmp/h11_daily.zip")
    txt = read_maybe_zip("/tmp/h11_daily.zip")
    lines = txt.strip().split("\n")
    hdr = lines[0].split(",")
    rows = [dict(zip(hdr, l.split(","))) for l in lines[1:]]
    rows.sort(key=lambda r: -float(r["avg_score"]))
    top20 = rows[:20]
    print(f"  manifest rows={len(rows)} top-20 elo "
          f"{float(top20[0]['avg_score']):.1f}..{float(top20[-1]['avg_score']):.1f}")

    print(f"[3/4] downloading top-{n_top} episodes (~34MB each) ...")
    eps = []
    for r in top20[:n_top]:
        eid = r["episode_id"]
        dest = os.path.join(TAPES_DIR, f"{eid}.json")
        if not os.path.exists(dest):
            api_get(f"datasets/download/kaggle/{daily}/{eid}.json", dest)
        print(f"  {eid} elo={float(r['avg_score']):.1f} size={os.path.getsize(dest)}")
        d = json.load(open(dest))
        sig = ep_signature(d)
        sig["elo"] = float(r["avg_score"])
        eps.append(sig)

    print("[4/4] diffing vs v16 tapes ...")
    mine = v16_signatures()
    my_hours = defaultdict(int)
    for s in mine:
        for h, c in s["sells_by_hour"].items():
            my_hours[h] += c
    my_h0 = my_hours.get(0, 0)
    my_total = sum(my_hours.values())

    report = {"latest_daily": latest, "elo_trend_7d": elo_trend,
              "top20": [{"id": r["episode_id"], "elo": float(r["avg_score"])} for r in top20],
              "episodes": [], "v16": {"routes": len(mine), "hour_histogram": dict(my_hours),
                                      "hour0_share": round(my_h0 / max(1, my_total), 4)}}
    for e in eps:
        rec = {"episode_id": e["episode_id"], "teams": e["teams"], "elo": e["elo"],
               "rewards": e["rewards"], "seats": []}
        for p in (0, 1):
            s = e["seats"][p]
            tot = sum(s["sells_by_hour"].values())
            h0 = s["sells_by_hour"].get("0", 0)
            best = max(mine, key=lambda m: cosine(m["sells_by_product"], s["sells_by_product"]))
            rec["seats"].append({
                "money": s["money"], "units": s["units"], "hires": s["hires"], "quads": s["quads"],
                "h0_share": round(h0 / max(1, tot), 4),
                "sells_by_product": s["sells_by_product"],
                "nearest_route": best["route"],
                "route_sim": round(cosine(best["sells_by_product"], s["sells_by_product"]), 4),
            })
        report["episodes"].append(rec)

    out = os.path.join(HERE, "t78_h11_report.json")
    json.dump(report, open(out, "w"), indent=1)
    md = [f"# H11 daily-replay refresh report — {latest['date']}", "",
          f"- latest daily dataset: `{daily}` ({latest['episode_count']} episodes)",
          f"- top Elo trend (7d): " + " → ".join(f"{e:.0f}" for _, e in elo_trend),
          f"- top-20 Elo band: {float(top20[-1]['avg_score']):.0f}..{float(top20[0]['avg_score']):.0f}",
          f"- v16 own tapes: {len(mine)} routes, hour-0 sell share {report['v16']['hour0_share']*100:.1f}%",
          "", "## Top episodes", ""]
    for e in report["episodes"]:
        md.append(f"### episode {e['episode_id']} (elo {e['elo']:.0f}) teams={e['teams']} rewards={e['rewards']}")
        for p, s in enumerate(e["seats"]):
            md.append(f"- seat{p}: ${s['money']:,} units={s['units']} hires={s['hires']} "
                       f"quads={s['quads']} h0={s['h0_share']*100:.0f}% "
                       f"nearest v16 route={s['nearest_route']} sim={s['route_sim']}")
        md.append("")
    open(os.path.join(HERE, "t78_h11_report.md"), "w").write("\n".join(md))
    print(f"report: {out}")
    print("\n".join(md))


if __name__ == "__main__":
    main()
