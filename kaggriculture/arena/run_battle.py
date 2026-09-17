#!/usr/bin/env python3
"""
ARENA BATTLE RUNNER — kaggriculture v4 vs v5 observation infrastructure.

Runs a full kaggriculture battle on the REAL kaggle-environments engine and
streams every turn as one JSON line on stdout (JSONL). The arena-service (bun +
socket.io) forwards these lines to the Observer UI at /.

Protocol (stdout, one JSON object per line):
  {"t":"hello","runner":1,"a":"v5","b":"v4","seed":101,"episodeSteps":720}
  {"t":"turn","step":0,"day":0,"hour":0,
   "farms":[farm0,farm1],                       # public, pre-action state of the step
   "market":{"inventory":{...},"prices":{...}},
   "town":{"unlocked_shops":[...]},
   "priv":[privA,privB],                        # omniscient observer: both sheds
   "acts":[actA,actB],                          # actions returned this turn
   "diag":[diagA,diagB],                        # agent internal state (mode/posterior/H...)
   "times":[msA,msB]}                           # agent compute time per turn
  {"t":"end","rewards":[r0,r1],"winner":0|1|-1,"wallS":38.2,"turns":718}

Usage:
  python3 run_battle.py --a v4 --b v5 --seed 101
  python3 run_battle.py --a v5 --b v4 --seed 102          # swapped seats
  python3 run_battle.py --a v4 --b v5 --seed 7 --max-steps 48   # 2-day smoke test
"""
import argparse
import importlib.util
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # kaggriculture/
BENCH = os.path.join(ROOT, "bench")

sys.path.insert(0, ROOT)
sys.path.insert(0, BENCH)

# name -> (file, entry function)
# Task 81 (2026-09-16): RESET TOÀN BỘ registry — user xóa sạch dòng dõi cũ (v13→v17, kme3 family,
# aurax, kawashigi, indark, thomast, ahmedv41) để dựng v18 trên nền mới.
# v18 = jaxa623/sdy623 "Beyond 48-0" K0006 (V43 + 4 market micro-edges) — Kaggle pull 2026-09-16,
#        main.py sha256 4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e (byte-exact).
# Sparring: ahmedv43/v44/v45 = Ahmed Berat Özer lineage (nền của v18).
AGENTS = {
    "v18": (os.path.join(ROOT, "v18.py"), "agent"),
    "v19": (os.path.join(ROOT, "v19.py"), "agent"),
    "ahmedv43": (os.path.join(ROOT, "ahmedv43.py"), "agent"),
    "ahmedv44": (os.path.join(ROOT, "ahmedv44.py"), "agent"),
    "ahmedv45": (os.path.join(ROOT, "ahmedv45.py"), "agent"),
    # Task 87: đối thủ meta mới (extracted từ notebook Kaggle 17-09, sha256-verified)
    # seyit4 = seyitkaangunes "V44+4 layers" (live 56280605, ~2801 rank ~188)
    # ahmedv46 = ahmedberatozer "First-Turn Microstructure" (EXP293)
    "seyit4": (os.path.join(ROOT, "seyit4.py"), "agent"),
    "ahmedv46": (os.path.join(ROOT, "ahmedv46.py"), "agent"),
    # v19.1 = v19 + first-turn microstructure (v46-mechanism port)
    "v191": (os.path.join(ROOT, "v191.py"), "agent"),
    # v19.2 = + h21/22 preguard (seyit-L1 adapted); v19.3 = + LOOKAHEAD 3;
    # v19.4 = + clone-gated lockstep SELL reorder (seyit-L2 port)
    "v192": (os.path.join(ROOT, "v192.py"), "agent"),
    "v193": (os.path.join(ROOT, "v193.py"), "agent"),
    "v194": (os.path.join(ROOT, "v194.py"), "agent"),
    # v20 = FLAT single-namespace build of the v19.4 chain (submission format, 410KB)
    "v20": (os.path.join(ROOT, "v20.py"), "agent"),
    # Task 89: v21 = v19.4 chain + v21 trough-banker layer (WOOL/STRAWBERRY/MELON
    # crash-window banking, recovery liquidation). Flat build, 419KB.
    "v21": (os.path.join(ROOT, "v21.py"), "agent"),
    # Task 88: aurax7 "Farmers Is All You Need" (rank 299, 2723.3) — V45 chassis
    # + V44 race escalator + _r60 survival guard + 2842 overlay (frontload +
    # advance_sales LOOK=2 + HORIZON 24). Extracted byte-exact 17-09.
    "aurax7": (os.path.join(ROOT, "aurax7.py"), "agent"),
}


# kaggle_environments wraps every agent call with redirect_stdout(StringIO)
# (core.py L645-648) to capture agent logs — so anything written to sys.stdout
# *from inside an agent wrapper* is swallowed. Hold the REAL stdout from
# import time and write events through it directly.
_REAL_OUT = sys.stdout


def out(obj):
    _REAL_OUT.write(json.dumps(obj, separators=(",", ":"), default=str) + "\n")
    _REAL_OUT.flush()


def load_agent(name, tag):
    if name in AGENTS:
        path, entry = AGENTS[name]
    elif os.path.isfile(name):
        path, entry = name, "agent"
    else:
        raise SystemExit(f"unknown agent: {name}")
    modname = f"arena_{tag}_{os.path.splitext(os.path.basename(path))[0]}"
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[modname] = mod
    spec.loader.exec_module(mod)
    fn = getattr(mod, entry, None)
    if not callable(fn):
        raise SystemExit(f"agent {name} has no callable '{entry}'")
    return mod, fn


def _jsonable(x):
    try:
        json.dumps(x)
        return x
    except Exception:
        return str(x)


def extract_diag(mod, obs):
    """Pull the agent's internal brain state for the observer UI.

    v5 exposes `_arena_diag(obs)` explicitly. Older v4-family modules are mined
    generically from their `_STATE` dict (tm mode/pm + today's plan).
    """
    try:
        fn = getattr(mod, "_arena_diag", None)
        if callable(fn):
            return _jsonable(fn(obs))
        st = getattr(mod, "_STATE", None)
        if not isinstance(st, dict):
            return {}
        tm = st.get("tm") or {}
        d = {"mode": tm.get("mode")}
        if "pm" in tm:
            try:
                d["pm"] = round(float(tm["pm"]), 3)
            except Exception:
                pass
        od = tm.get("opp_day") or {}
        if od:
            d["opp_flows"] = {k: round(float(v), 1) for k, v in od.items()}
        try:
            day = obs.get("day")
        except Exception:
            day = None
        plan = st.get(("plan", day)) if day is not None else None
        if isinstance(plan, dict):
            d["herd"] = {k: plan.get(k) for k in
                         ("goose_target", "cow_target", "sheep_target")}
            d["crop_plan"] = plan.get("crop_tiles")
            d["feed_demand"] = plan.get("feed_demand")
        return d
    except Exception:
        return {}


class TurnBuffer:
    """Collects one turn record from the two agent calls of the same step."""

    def __init__(self, emit):
        self.emit = emit
        self.cur = None

    def start_step(self, step, day, hour, farms, market, town):
        self.flush()
        self.cur = {
            "t": "turn", "step": step, "day": day, "hour": hour,
            "farms": farms, "market": market, "town": town,
            "priv": [None, None], "acts": [None, None],
            "diag": [{}, {}], "times": [0.0, 0.0],
        }

    def record(self, side, obs, action, diag, ms):
        if self.cur is None or self.cur.get("step") != _step_of(obs):
            # first call of a new step
            try:
                day = obs.get("day") or 0
                hour = obs.get("hour") or 0
            except Exception:
                day, hour = 0, 0
            self.start_step(_step_of(obs), day, hour,
                            _farms(obs), _market(obs), _town(obs))
        self.cur["priv"][side] = _private(obs)
        self.cur["acts"][side] = _jsonable(action)
        self.cur["diag"][side] = diag
        self.cur["times"][side] = round(ms, 2)
        if side == 1:
            self.flush()

    def flush(self):
        if self.cur is not None:
            self.emit(self.cur)
            self.cur = None


def _step_of(obs):
    try:
        return (obs.get("day") or 0) * 24 + (obs.get("hour") or 0)
    except Exception:
        return -1


def _farms(obs):
    try:
        return _jsonable(obs.get("farms"))
    except Exception:
        return None


def _market(obs):
    try:
        return _jsonable(obs.get("market"))
    except Exception:
        return None


def _town(obs):
    try:
        return _jsonable(obs.get("town"))
    except Exception:
        return None


def _private(obs):
    try:
        return _jsonable(obs.get("private"))
    except Exception:
        return None


def wrap_agent(mod, fn, side, buf):
    def agent_fn(obs, config=None):
        t0 = time.perf_counter()
        action = fn(obs)
        ms = (time.perf_counter() - t0) * 1000.0
        buf.record(side, obs, action, extract_diag(mod, obs), ms)
        return action
    return agent_fn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="agent name or file path (seat 0)")
    ap.add_argument("--b", required=True, help="agent name or file path (seat 1)")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--max-steps", type=int, default=None,
                    help="override episodeSteps (smoke tests)")
    args = ap.parse_args()

    from kaggle_environments import make

    modA, fnA = load_agent(args.a, "A")
    modB, fnB = load_agent(args.b, "B")

    cfg = {}
    if args.seed is not None:
        cfg["seed"] = args.seed
    if args.max_steps is not None:
        cfg["episodeSteps"] = args.max_steps
    episode_steps = cfg.get("episodeSteps", 720)

    out({"t": "hello", "runner": 1, "a": args.a, "b": args.b,
         "seed": args.seed, "episodeSteps": episode_steps})

    buf = TurnBuffer(out)
    wrapA = wrap_agent(modA, fnA, 0, buf)
    wrapB = wrap_agent(modB, fnB, 1, buf)

    wall0 = time.time()
    env = make("kaggriculture", debug=False, configuration=cfg or None)
    try:
        env.run([wrapA, wrapB])
    finally:
        buf.flush()

    try:
        final = env.steps[-1]
        r0 = final[0].reward
        r1 = final[1].reward
        r0 = float(r0) if r0 is not None else 0.0
        r1 = float(r1) if r1 is not None else 0.0
    except Exception:
        r0 = r1 = 0.0
    winner = 0 if r0 > r1 else (1 if r1 > r0 else -1)

    out({"t": "end", "rewards": [r0, r1], "winner": winner,
         "wallS": round(time.time() - wall0, 1),
         "turns": len(env.steps)})


if __name__ == "__main__":
    main()
