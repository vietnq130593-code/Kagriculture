import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import importlib.util
spec = importlib.util.spec_from_file_location("_v16h6_mod", os.path.join(ROOT, "v16h6.py"))
mod = importlib.util.module_from_spec(spec)
sys.modules["_v16h6_mod"] = mod
spec.loader.exec_module(mod)
wrap = "/tmp/t78_h6_wrap.py"
open(wrap, "w").write(
    "import sys\n"
    "if '_v16h6_mod' not in sys.modules:\n"
    "    import importlib.util\n"
    "    _spec = importlib.util.spec_from_file_location('_v16h6_mod', '/home/z/my-project/kaggressurE/v16h6.py'.replace('kaggressurE','kaggriculture'))\n"
    "    _m = importlib.util.module_from_spec(_spec)\n"
    "    sys.modules['_v16h6_mod'] = _m\n"
    "    _spec.loader.exec_module(_m)\n"
    "else:\n"
    "    _m = sys.modules['_v16h6_mod']\n"
    "def agent(obs, configuration=None):\n"
    "    return _m.agent(obs, configuration)\n"
)
from kaggle_environments import make
for seed in (350, 351):
    for opp in ("thomast", "v15"):
        mod._H6_STATE.update(done={0: False, 1: False})
        mod._H6_REPORT.update(dumps=0, units=0, giveups=0)
        env = make("kaggriculture", debug=False, configuration={"seed": seed})
        env.run([wrap, os.path.join(ROOT, f"{opp}.py")])
        r0 = float(env.steps[-1][0].reward or 0)
        r1 = float(env.steps[-1][1].reward or 0)
        px576 = None
        try:
            obs576 = env.steps[576][0]["observation"]
            px576 = float(obs576["market"]["prices"]["CARROT"])
        except Exception:
            pass
        print(f"seed {seed} vs {opp}: rewards=({r0:.0f},{r1:.0f}) px_CARROT@576={px576} "
              f"report={dict(mod._H6_REPORT)}")
