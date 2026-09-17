import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEEDS = "350-354"
PAIRS = [("v16", "thomast"), ("v16", "thomast_t0"), ("v16", "thomast_t3"),
         ("v16h8", "thomast"), ("v16h8", "thomast_t3")]
for a, b in PAIRS:
    p = os.path.join(HERE, f"t78_{a}_vs_{b}.json")
    if os.path.exists(p):
        try:
            old = json.load(open(p))
            if old.get("seeds") == SEEDS and not old.get("fails"):
                continue
        except Exception:
            pass
    subprocess.run([sys.executable, os.path.join(HERE, "battery.py"), a, b,
                    "--seeds", SEEDS, "--out", os.path.basename(p), "--jobs", "2",
                    "--tag", "t78t"], cwd=ROOT)
for a, b in PAIRS:
    p = os.path.join(HERE, f"t78_{a}_vs_{b}.json")
    if os.path.exists(p):
        r = json.load(open(p))
        print(f"{r['a']:6s} vs {r['b']:12s} {r['wins']:2d}/{r['games']:2d} "
              f"gap {r['gap']:+9,.1f} worst {r['worst_ratio']:.4f}", flush=True)
