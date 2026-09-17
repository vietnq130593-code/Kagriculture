"""indark_e776 — Kenjo1209 medoid 9C/5S + E749-E776 guard chain (Kaggle top-10 family).

Loader for the multi-file E776 package (research unpack of 'shape-the-shop' E776).
Entry contract matches local registry: callable 'agent'.

NOTE: kaggle_environments' raw file runner (env.run / get_last_callable) exec's
agent sources WITHOUT defining __file__ — so the tree root must be resolved
with a hardcoded fallback in that context (run_battle's importlib loader does
provide __file__; both paths are handled below).
"""
import os
import sys


def _tree_root():
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:  # kaggle_environments raw exec context
        here = "/home/z/my-project/kaggriculture/"
    return os.path.join(here, "indark_e776_tree")


_TREE = _tree_root()
if _TREE not in sys.path:
    sys.path.insert(0, _TREE)

from e776_pkg.entry import policy as _e776_policy  # noqa: E402


def agent(observation, configuration=None):
    return _e776_policy(observation, configuration)
