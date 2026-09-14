#!/usr/bin/env python3
"""t78_probe_h8.py — H8 spend-detector probe.

Wraps v16 with a logger that records opponent money every step, runs it
against v15 / v14 / kme3v39 (1 seed, both arrangements), then reports every
step where the opponent spent >= $100 in one step transition — to verify the
step-217 cattle-switch window from andrewsokolovsky "Breaking the Tie".
"""
import json
import os
import sys
import time

ROOT = "/home/z/my-project/kaggressurE".replace("kaggressurE", "kaggriculture")
sys.path.insert(0, ROOT)

WRAPPER = r'''import sys, json, os
import importlib.util
_spec = importlib.util.spec_from_file_location('_v16_probe_mod', '/home/z/my-project/kaggriculture/v16.py')
_mod = importlib.util.module_from_spec(_spec)
sys.modules['_v16_probe_mod'] = _mod
_spec.loader.exec_module(_mod)
_LOG = os.environ.get('H8_PROBE_LOG', '/tmp/h8_probe.jsonl')
def agent(obs, configuration=None):
    try:
        step = int(obs.get('step', 0) or 0)
        seat = int(obs.get('player', 0) or 0)
        farms = obs.get('farms') or []
        om = float(farms[1 - seat].get('money', 3000) or 0) if len(farms) >= 2 else None
        with open(_LOG, 'a') as f:
            f.write(json.dumps({'step': step, 'seat': seat, 'opp': om}) + '\n')
    except Exception:
        pass
    return _mod.agent(obs, configuration)
'''


def run_pairing(opp_name, seed):
    from kaggle_environments import make
    wrap_path = "/tmp/t78_wrap_v16.py"
    open(wrap_path, "w").write(WRAPGER := WRAPPER)
    opp_path = os.path.join(ROOT, f"{opp_name}.py")
    logs = []
    for arrangement in (0, 1):
        logf = f"/tmp/t78_probe_{opp_name}_{seed}_{arrangement}.jsonl"
        if os.path.exists(logf):
            os.remove(logf)
        os.environ["H8_PROBE_LOG"] = logf
        agents = [wrap_path, opp_path] if arrangement == 0 else [opp_path, wrap_path]
        env = make("kaggriculture", debug=False, configuration={"seed": seed})
        env.run(agents)
        r0 = float(env.steps[-1][0].reward or 0)
        r1 = float(env.steps[-1][1].reward or 0)
        rows = [json.loads(x) for x in open(logf) if x.strip()]
        logs.append((arrangement, rows, (r0, r1)))
    return logs


def analyze(opp_name, logs):
    print(f"\n===== opponent {opp_name} =====")
    for arrangement, rows, rewards in logs:
        prev = None
        big = []
        trace_217 = None
        for r in rows:
            if r["opp"] is None:
                continue
            if prev is not None:
                spend = prev - r["opp"]
                if spend >= 100:
                    big.append((r["step"], spend))
                if r["step"] == 217:
                    trace_217 = spend
            prev = r["opp"]
        print(f" arr{arrangement} rewards={rewards} big_spends(>=100)={big}")
        print(f"   step217 spend={trace_217}")
        spends = [s for _, s in big]
        if spends:
            early = [b for b in big if b[0] <= 217]
            print(f"   #big={len(big)} first={big[0] if big else None} last_big={big[-1] if big else None} pre-217={early}")


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 350
    t0 = time.time()
    for opp in ("v15", "v14", "kme3v39"):
        logs = run_pairing(opp, seed)
        analyze(opp, logs)
    print(f"\ntotal {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
