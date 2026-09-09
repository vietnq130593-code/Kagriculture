# Probe: log every committed market unit (SELL/BUY) with price for a seed.
# Usage: python3 bench/sell_log.py <a_path> <b_path> <seed> [item_filter]
import sys, os, glob
ROOT = glob.glob('/home/z/my-project/kag*')[0]
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'bench'))
from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as eng

ENVNAME = os.path.basename(os.path.dirname(eng.__file__))
LOG = []
CURMAP = {}
_orig_commit = eng._commit_unit
_orig_pm = eng._process_market


def _log_commit(op, item, price, farm, private, market, shed_capacity=100):
    ok = _orig_commit(op, item, price, farm, private, market, shed_capacity)
    if ok:
        LOG.append((CURMAP.get(id(farm), -1), op + ":" + str(item), price))
    return ok


def _log_pm(state, env):
    obs0 = state[0].observation
    if getattr(obs0, "farms", None):
        CURMAP.clear()
        CURMAP.update({id(f): i for i, f in enumerate(obs0.farms)})
    return _orig_pm(state, env)


eng._commit_unit = _log_commit
eng._process_market = _log_pm


def resolve(x):
    if os.path.isfile(x):
        return x
    p = os.path.join(ROOT, x)
    return p if os.path.isfile(p) else x


a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
filt = sys.argv[4].upper() if len(sys.argv) > 4 else None
env = make(ENVNAME, debug=False, configuration={"seed": seed})
env.run([resolve(a), resolve(b)])
r0, r1 = env.steps[-1][0].reward, env.steps[-1][1].reward
print(f"seed {seed}: seat0 ${r0:,.0f}  seat1 ${r1:,.0f}")
agg = {}
for side, item, price in LOG:
    if filt and item != filt:
        continue
    k = (side, item)
    a_ = agg.setdefault(k, [0, 0.0])
    a_[0] += 1
    if item.startswith("SELL:"):
        a_[1] += price
    else:
        a_[1] -= price
for (side, item), (n, tot) in sorted(agg.items()):
    sign = "+" if tot >= 0 else "-"
    print(f"side{side} {item:22s} n={n:4d} net={sign}${abs(tot):11,.0f} avg=${abs(tot)/max(1,n):7.1f}")
for side in (0, 1):
    net = sum(t for (s, i), (n, t) in agg.items() if s == side)
    print(f"side{side} LEDGER NET: ${net:+,.0f}")
if filt:
    seq = [(s, p) for s, i, p in LOG if i == filt]
    print(f"\nfirst 90 {filt} unit prices in commit order:")
    print(' '.join(f"{'A' if s==0 else 'B'}:{p}" for s, p in seq[:90]))
