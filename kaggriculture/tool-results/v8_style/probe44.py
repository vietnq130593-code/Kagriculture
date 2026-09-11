#!/usr/bin/env python3
"""Probe: wrap v8.py bằng file agent riêng để spy orders/tasks."""
import sys

PROBE_DAYS = set(int(x) for x in sys.argv[2].split(',')) if len(sys.argv) > 2 else {17}
A = '/home/z/my-project/kaggriculture/v8.py'
B = '/tmp/v8_base.py'
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 130

wrapper = '''
import sys
sys.path.insert(0, '/home/z/my-project/kaggriculture')
import importlib.util
spec = importlib.util.spec_from_file_location("v8probe", '/home/z/my-project/kaggriculture/v8.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
PROBE_DAYS = ''' + repr(sorted(PROBE_DAYS)) + '''

_o = m._build_orders
_t = m._build_tasks

def spy_orders(me, shed, seeds, inventories, inv, prices, day, hour, plan, stats, tiles, shops):
    o = _o(me, shed, seeds, inventories, inv, prices, day, hour, plan, stats, tiles, shops)
    if day in PROBE_DAYS and hour in (0, 5, 11, 17, 22):
        print(f"d{day}h{hour} ORDERS={o} crop_tiles={plan.get('crop_tiles')} standing={plan.get('standing')}", flush=True)
    return o

def spy_tasks(tiles, shed, seeds, plan, day, hour, step, inventories, n_units):
    t, s = _t(tiles, shed, seeds, plan, day, hour, step, inventories, n_units)
    if day in PROBE_DAYS and hour in (0, 5, 11, 17, 22):
        ops = {}
        for tk in t:
            key = tk["op"] + (":" + str(tk.get("crop", "")) if tk["op"] == "PLANT" else "")
            ops[key] = ops.get(key, 0) + 1
        print(f"d{day}h{hour} TASKS={ops}", flush=True)
    return t, s

m._build_orders = spy_orders
m._build_tasks = spy_tasks

def agent(obs):
    return m.agent(obs)
'''

with open('/tmp/v8_probe_agent.py', 'w') as f:
    f.write(wrapper)

from kaggle_environments import make
env = make("kaggriculture", debug=True, configuration={"seed": SEED})
env.run(['/tmp/v8_probe_agent.py', B])
r0 = env.steps[-1][0].reward
r1 = env.steps[-1][1].reward
print(f"FINAL: NEW ${r0:,.0f} vs BASE ${r1:,.0f}")
