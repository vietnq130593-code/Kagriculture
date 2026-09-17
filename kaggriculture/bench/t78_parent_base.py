import json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SEEDS = "350-354"
for b in ("kme3", "kme3v10", "aurax"):
    p = os.path.join(HERE, f"t78_v16_vs_{b}.json")
    if os.path.exists(p):
        try:
            old = json.load(open(p))
            if old.get("seeds") == SEEDS and not old.get("fails"):
                continue
        except Exception:
            pass
    subprocess.run([sys.executable, os.path.join(HERE, "battery.py"), "v16", b,
                    "--seeds", SEEDS, "--out", os.path.basename(p), "--jobs", "2",
                    "--tag", "t78p"], cwd=ROOT)
    r = json.load(open(p))
    print(f"{r['a']:6s} vs {r['b']:9s} {r['wins']:2d}/{r['games']:2d} "
          f"gap {r['gap']:+9,.1f} worst {r['worst_ratio']:.4f}", flush=True)
