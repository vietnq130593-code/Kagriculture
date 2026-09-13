#!/usr/bin/env python3
"""FORCE-ROUTE variant generator (Task 69, ARI plan H3 screen).

The lineage chassis picks a production tape at step 144 by mapping the first two
unlocked shops to one of 13 route tapes (0..12; route 2 is the shared endgame).
This tool generates a variant of ANY lineage file with the day-6 route choice
forced to a constant K (endgame switch to route 2 at step 648 is kept).

Usage:
  python3 force_route.py <base.py> <K ...>         # writes bench/variants/<base>_rK.py
  python3 force_route.py <base.py> --probe-seeds 100-115   # print default route per seed
"""
import os
import re
import sys

ROOT = '/home/z/my-project/kaggriculture'
VAR_DIR = os.path.join(ROOT, 'bench', 'variants')
os.makedirs(VAR_DIR, exist_ok=True)

ROUTE_LINE = re.compile(
    r"state\['route'\]=\{[^}]*\}\.get\(tuple\(shops\[:2\]\),0\)"
)


def gen_variant(base_path, k):
    src = open(base_path).read()
    m = ROUTE_LINE.search(src)
    if not m:
        raise SystemExit(f"router route-map line not found in {base_path}")
    out = src[:m.start()] + f"state['route']={k}" + src[m.end():]
    name = f"{os.path.splitext(os.path.basename(base_path))[0]}_r{k}.py"
    path = os.path.join(VAR_DIR, name)
    open(path, 'w').write(out)
    return path


def probe_default_routes(seeds):
    """Run dummy battles and report shops + default route per seed (seat-0 view)."""
    sys.path.insert(0, ROOT)
    from kaggle_environments import make
    mapping = {('BAKERY', 'YARN_STORE'): 3, ('BRUNCH_SPOT', 'YARN_STORE'): 4, ('FARMERS_MARKET', 'YARN_STORE'): 5, ('ICE_CREAM_SHOP', 'YARN_STORE'): 6, ('PET_CAFE', 'YARN_STORE'): 5, ('PIZZA_SHOP', 'YARN_STORE'): 7, ('SMOOTHIE_SHOP', 'YARN_STORE'): 8, ('YARN_STORE', 'BAKERY'): 9, ('YARN_STORE', 'BRUNCH_SPOT'): 9, ('YARN_STORE', 'FARMERS_MARKET'): 1, ('YARN_STORE', 'ICE_CREAM_SHOP'): 9, ('YARN_STORE', 'PET_CAFE'): 10, ('YARN_STORE', 'PIZZA_SHOP'): 6, ('YARN_STORE', 'SMOOTHIE_SHOP'): 11, ('YARN_STORE', 'YARN_STORE'): 12}
    dummy = os.path.join(VAR_DIR, '_dummy_pass.py')
    open(dummy, 'w').write(
        "def agent(observation, configuration=None):\n"
        "    return {'farmer': ['PASS'], 'hands': [], 'market': []}\n")
    for s in seeds:
        env = make('kaggriculture', debug=False, configuration={'seed': s})
        env.run([dummy, dummy])
        obs = env.steps[144][0].observation
        shops = list(obs.town.unlocked_shops) if hasattr(obs.town, 'unlocked_shops') \
            else obs.town['unlocked_shops']
        route = mapping.get(tuple(shops[:2]), 0)
        print(f"seed {s}: shops[:4]={shops[:4]} -> default route {route}")


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    base = args[0] if os.path.isfile(args[0]) else os.path.join(ROOT, args[0])
    if not os.path.isfile(base):
        raise SystemExit(f"base not found: {args[0]}")
    if len(args) > 1 and args[1] == '--probe-seeds':
        lo, hi = args[2].split('-')
        probe_default_routes(range(int(lo), int(hi) + 1))
        return
    for k in args[1:]:
        path = gen_variant(base, int(k))
        print(f"route {k}: {path}")


if __name__ == "__main__":
    main()
