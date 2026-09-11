#!/usr/bin/env python3
"""GOD REPLAY for arena JSONL battles (Task 45).

Re-runs the real engine on recorded arena actions with the same
instrumentation as r2_godreplay.py, producing an EXACT per-unit market
ledger (commit_log), hire/land logs, and per-turn money validation.

Arena convention: turn t record = pre-action(t) state + acts for engine
step t. 719 turns (step 0..718). Validation: post-step state must equal
turn t+1's farms.
"""
import json
import sys
import copy
import gc

from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as eng

PASS = {"farmer": ["PASS"], "hands": [], "market": []}


def run_god_arena(path, out_path):
    hello = None
    turns = []
    end = None
    with open(path) as f:
        for line in f:
            d = json.loads(line)
            if d.get("t") == "hello":
                hello = d
            elif d.get("t") == "turn":
                turns.append(d)
            elif d.get("t") == "end":
                end = d
    seed = hello["seed"]
    names = [hello.get("a"), hello.get("b")]

    env = make("kaggriculture", debug=False, configuration={"seed": seed})
    env.reset(2)
    env.info["seed"] = seed

    ctx = {"t": 0, "env": env, "farms": None}
    orig_interp = eng.interpreter

    def wrapped_interpreter(state, env_):
        ctx["farms"] = [state[0].observation.farms[0], state[0].observation.farms[1]]
        return orig_interp(state, env_)

    env.interpreter = wrapped_interpreter

    def which_player(farm):
        f = ctx["farms"]
        return 0 if farm is f[0] else 1

    commit_log = []
    orig_commit = eng._commit_unit

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok:
            commit_log.append([ctx["t"], which_player(farm), op, item, price])
        return ok

    eng._commit_unit = commit

    hire_log = []
    orig_hire = eng._do_hire

    def do_hire(farm, private, board_size, mult=1):
        before = len(farm["hands"])
        cost = eng._hire_cost(farm["hires_today"])
        orig_hire(farm, private, board_size, mult)
        if len(farm["hands"]) > before:
            hire_log.append([ctx["t"], which_player(farm), cost, farm["hires_today"]])

    eng._do_hire = do_hire

    land_log = []
    orig_land = eng._do_buy_land

    def do_buy_land(farm, board_size):
        before = len(farm["unlocked_quadrants"])
        orig_land(farm, board_size)
        if len(farm["unlocked_quadrants"]) > before:
            q = farm["unlocked_quadrants"][-1]
            cost = [0, 1000, 2000, 4000][len(farm["unlocked_quadrants"]) - 1]
            land_log.append([ctx["t"], which_player(farm), q, cost])

    eng._do_buy_land = do_buy_land

    n = len(turns)
    mismatches = []
    for t in range(n):
        ctx["t"] = t
        acts = turns[t].get("acts") or [None, None]
        a0 = acts[0] if isinstance(acts[0], dict) else PASS
        a1 = acts[1] if isinstance(acts[1], dict) else PASS
        try:
            env.step([copy.deepcopy(a0), copy.deepcopy(a1)])
        except Exception as e:
            mismatches.append({"t": t, "err": str(e)})
            break
        obs_m = env.state[0].observation
        if t + 1 < n:
            f_r = turns[t + 1]["farms"]
            for p in (0, 1):
                if obs_m.farms[p]["money"] != f_r[p]["money"]:
                    mismatches.append({"t": t, "p": p, "kind": "money",
                                       "sim": obs_m.farms[p]["money"],
                                       "real": f_r[p]["money"]})
        if t % 240 == 0:
            print("  t=%d ok (%d commits)" % (t, len(commit_log)), file=sys.stderr)

    final_money = [env.state[p].observation.farms[p]["money"] for p in (0, 1)]
    out = {
        "file": path.split("/")[-1], "names": names, "seed": seed,
        "rewards": (end or {}).get("rewards"),
        "final_money_sim": final_money,
        "n_turns": n, "n_mismatches": len(mismatches),
        "mismatch_samples": mismatches[:20],
        "commit_log": commit_log, "hire_log": hire_log, "land_log": land_log,
    }
    with open(out_path, "w") as f:
        json.dump(out, f)
    print("%s: %d turns, %d mismatches, final %s (real %s)" % (
        path.split("/")[-1], n, len(mismatches), final_money,
        (end or {}).get("rewards")), file=sys.stderr)
    return out


if __name__ == "__main__":
    import glob
    for path in sorted(glob.glob("/home/z/my-project/tool-results/v8_style/v8p_*.jsonl")):
        tag = path.split("/")[-1].replace(".jsonl", "")
        out_path = f"/tmp/god_{tag}.json"
        run_god_arena(path, out_path)
        gc.collect()
    print("done", file=sys.stderr)
