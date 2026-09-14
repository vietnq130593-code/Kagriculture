import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
wrap = "/tmp/t78_shed_wrap.py"
open(wrap, "w").write(
    "import sys, json, os\n"
    "if '_v16_probe_mod' not in sys.modules:\n"
    "    import importlib.util\n"
    "    _spec = importlib.util.spec_from_file_location('_v16_probe_mod', '/home/z/my-project/kaggressurE/v16.py'.replace('kaggressurE','kaggriculture'))\n"
    "    _m = importlib.util.module_from_spec(_spec)\n"
    "    sys.modules['_v16_probe_mod'] = _m\n"
    "    _spec.loader.exec_module(_m)\n"
    "else:\n"
    "    _m = sys.modules['_v16_probe_mod']\n"
    "_LOG = os.environ.get('SHED_LOG', '/tmp/shed.jsonl')\n"
    "def agent(obs, configuration=None):\n"
    "    try:\n"
    "        step = int(obs.get('step', 0) or 0)\n"
    "        seat = int(obs.get('player', 0) or 0)\n"
    "        shed = (obs.get('private') or {}).get('shed') or {}\n"
    "        px = ((obs.get('market') or {}).get('prices') or {}).get('CARROT')\n"
    "        with open(_LOG, 'a') as f:\n"
    "            f.write(json.dumps({'step': step, 'seat': seat, 'carrot': shed.get('CARROT', 0),\n"
    "                                'milk': shed.get('MILK', 0), 'wool': shed.get('WOOL', 0),\n"
    "                                'px': px}) + '\\n')\n"
    "    except Exception:\n"
    "        pass\n"
    "    return _m.agent(obs, configuration)\n"
)
from kaggle_environments import make
for seed in (351,):
    logf = f"/tmp/t78_shed_{seed}.jsonl"
    if os.path.exists(logf):
        os.remove(logf)
    os.environ["SHED_LOG"] = logf
    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.run([wrap, os.path.join(ROOT, "v15.py")])
    rows = [json.loads(x) for x in open(logf) if x.strip()]
    seat0 = [r for r in rows if r["seat"] == 0]
    print(f"seed {seed}: seat0 shed CARROT + px timeline (nonzero or every 24 steps):")
    prev_c = None
    for r in seat0:
        c = r["carrot"]
        if (c and (prev_c in (None, 0) or c != prev_c)) or r["step"] % 24 == 0:
            print(f"  t{r['step']:3d} carrot={c:5d} px={r['px']}")
        prev_c = c
