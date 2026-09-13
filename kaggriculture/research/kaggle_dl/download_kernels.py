#!/usr/bin/env python3
"""Download Kaggle kernels for kaggriculture research + extract clean code/markdown."""
import json, os, subprocess, sys, time

TOKEN = os.environ.get("KAGGLE_TOKEN", "")
OUT = os.path.dirname(os.path.abspath(__file__))

# (user, slug) — curated top-value list from the 493-notebook landscape scan
KERNELS = [
    # --- High-win-rate agents (score claims in title) ---
    ("boatlee", "v16-rc5-high-score-8c-4s-premium-market-lead"),      # 313v 8C/4S
    ("kaitofukami", "25-27-strict-future-v27-midgame-meta-reset"),    # 200v 25/27
    ("kaitofukami", "40-40-early-floor-39-46-top-10-v48-fast-routes"),# 132v 40/40
    ("boatlee", "84-84-base-public-holdout-v14-clone-preemption"),    # 149v 84/84
    ("kaitofukami", "177-180-fresh-top-30-v21-1-conditional-memory"), # 102v 177/180
    ("thomastschinkel", "kaggriculture-93-8-win-rate-public-state-router"), # 81v 93.8%
    ("thomastschinkel", "kaggriculture-public-state-router-74-5-win-rate"), # 99v 74.5%
    ("kaitofukami", "159-160-vs-frontier-v20-weed-slip-recovery"),    # 75v 159/160
    ("kaitofukami", "103-128-fresh-public-v43-sparse-shop-hybrid"),   # 76v 103/128
    ("boatlee", "v16-rc2-high-score-near-mirror-market-relay"),       # 81v RC2
    ("boatlee", "v29-r1-adaptive-market-hysteresis"),                 # 69v V29
    # --- Research / meta-analysis notebooks ---
    ("raykkretzschmar", "kaggriculture-findings-from-zero-to-top-meta"), # 187v guide
    ("cjlcjlcjl", "kaggriculture-what-the-top-farms-do-a-live-meta"),  # 75v live meta
    ("georgymamarin", "kaggriculture-visualized-what-every-crop-pays"),# 98v economics
    ("lynnsakurai", "farming-score-v3-replay-revised"),               # 72v score/replay
    # --- Distinct strategy families ---
    ("tetsutani", "adaptive-farming-strategy-for-kaggriculture"),     # 142v adaptive
    ("romantamrazov", "kaggriculture-hamburger"),                     # 129v hamburger
    ("yhay81", "shop-router-0909"),                                   # 127v shop router
    ("yhay81", "three-day-shop-router"),                              # 121v 3-day router
    ("yhay81", "six-day-public-state-fieldbook"),                     # 131v fieldbook
    ("pilkwang", "kaggriculture-structured-economic-policy"),         # 106v policy
    ("ahmedberatozer", "more-yield-smarter-labor"),                   # 103v labor
    ("prvsiyan", "kaggriculture-frontier-the-soil-remembers-rain"),   # 103v soil memory
    ("prvsiyan", "kaggriculture-frontier-the-moon-counts-melons"),    # 93v melons
    ("flexonafft", "kaggriculture-multi-route-farming-agent"),        # 93v multi-route
    ("indarkarhana", "shape-the-shop-work-the-pasture-top-10"),       # 94v top10
    ("salemali7", "kaggriculture-2900"),                              # 77v 2900+
    ("guruprasaathas111", "kaggriculture-master-engine-v3"),          # 72v engine
    ("tetsutani", "shape-the-shop-work-the-pasture-kaggriculture"),   # 126v
    ("ahmedberatozer", "kaggriculture-v38-smarter-feed-stronger-margins"), # 88v v38
    ("andrewsokolovsky", "kaggriculture-breaking-the-tie"),           # 73v tie
    ("jek1wantaufik", "building-a-kaggriculture-ai-agent"),           # 76v build guide
    ("tetsutani", "market-smart-farming-kaggriculture"),             # 77v market-smart
    ("reyhanksatria", "kaggriculture-dynamic-route-agent"),           # 78v dynamic
]

def pull(user, slug):
    out = subprocess.run(
        ["curl", "-s", "-m", "90",
         "-H", f"Authorization: Bearer {TOKEN}",
         f"https://www.kaggle.com/api/v1/kernels/pull?userName={user}&kernelSlug={slug}"],
        capture_output=True, text=True).stdout
    return json.loads(out)

def extract_nb(nb_json):
    """Return (code_text, md_text) from ipynb JSON string."""
    code_lines, md_lines = [], []
    for cell in nb_json.get("cells", []):
        src = "".join(cell.get("source", []))
        if cell.get("cell_type") == "code":
            code_lines.append(src)
        else:
            md_lines.append(src)
    return "\n\n# " + "="*70 + "\n\n".join(code_lines), "\n\n---\n\n".join(md_lines)

ok, fail = 0, 0
for user, slug in KERNELS:
    fn_base = f"{user}__{slug}"
    raw_path = os.path.join(OUT, f"raw_{fn_base}.json")
    if os.path.exists(raw_path) and os.path.getsize(raw_path) > 1000:
        data = json.load(open(raw_path))
    else:
        try:
            data = pull(user, slug)
        except Exception as e:
            print(f"FAIL {user}/{slug}: {e}"); fail += 1; continue
        with open(raw_path, "w") as f:
            json.dump(data, f)
        time.sleep(0.4)
    src = (data.get("blob") or {}).get("sourceNullable")
    if not src:
        print(f"NOBLOB {user}/{slug}"); fail += 1; continue
    # source is the ipynb JSON string
    try:
        nb = json.loads(src)
    except Exception:
        # might be a raw script
        with open(os.path.join(OUT, f"{fn_base}.py"), "w") as f:
            f.write(src)
        ok += 1; print(f"OK(script) {fn_base} ({len(src)} bytes)"); continue
    with open(os.path.join(OUT, f"{fn_base}.ipynb"), "w") as f:
        f.write(src)
    code, md = extract_nb(nb)
    with open(os.path.join(OUT, f"{fn_base}.py"), "w") as f:
        f.write(code)
    with open(os.path.join(OUT, f"{fn_base}_md.txt"), "w") as f:
        f.write(md)
    ok += 1
    print(f"OK {fn_base}: code={len(code)} md={len(md)}")

print(f"\nDONE ok={ok} fail={fail}")
