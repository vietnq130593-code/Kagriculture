import sys, traceback
sys.path.insert(0, '/home/z/my-project/kaggriculture')
from kaggle_environments import make
import importlib.util

spec = importlib.util.spec_from_file_location("v4dbg", "/home/z/my-project/kaggriculture/v4.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

env = make("kaggriculture", debug=True)
env.reset()
# run a few steps manually calling the agent like the engine would
state = env.state
for i in range(30):
    for p in (0, 1):
        obs = state[p].observation
        try:
            out = mod._agent(obs)
        except Exception:
            print(f"CRASH at step {i} player {p}:")
            traceback.print_exc()
            sys.exit(1)
    # step the engine with both agents
    env.step([[o.action for o in state]] if False else None) if False else None
    # use env.run for one step equivalent:
    break

# simpler: monkey-run via env.run with a wrapper file
wrapper = '''
import sys
sys.path.insert(0, "/home/z/my-project/kaggriculture")
import importlib.util
spec = importlib.util.spec_from_file_location("v4dbg", "/home/z/my-project/kaggriculture/v4.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def agent(obs):
    import traceback
    try:
        return mod._agent(obs)
    except Exception:
        with open("/tmp/v4_crash.txt", "a") as f:
            f.write(traceback.format_exc() + "\\n")
        return {"farmer": ["PASS"], "hands": [], "market": []}
'''
with open("/tmp/v4_wrap.py", "w") as f:
    f.write(wrapper)

import os
if os.path.exists("/tmp/v4_crash.txt"):
    os.remove("/tmp/v4_crash.txt")
env2 = make("kaggriculture", debug=True)
env2.run(["/tmp/v4_wrap.py", "/tmp/v4_wrap.py"])
print("money:", [s.reward for s in env2.steps[-1]])
if os.path.exists("/tmp/v4_crash.txt"):
    txt = open("/tmp/v4_crash.txt").read()
    print("CRASHES:", txt.count("Traceback"), "first one:")
    print(txt[:3000])
else:
    print("no crashes in self-play")
