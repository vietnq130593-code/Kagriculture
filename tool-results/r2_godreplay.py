#!/usr/bin/env python3
"""ROUND 2 — GOD REPLAY: re-run the actual engine on recorded actions with full
instrumentation. Produces EXACT per-unit market ledger, per-action unit diffs,
per-step state snapshots. Validates every step against the recorded replay.

Convention (verified empirically): replay row t (t>=1) = state AFTER applying
steps[t].action via interpreter call t (engine step counter = t-1 during call).
Row 0 = initial state (its action is never applied by this loop).

True day/hour of the action recorded in row t: day=(t-1)//24, hour=(t-1)%24.
Engine steps processed: 0..718 (719 calls). Last end-of-day = step 695 (end of
day 28). Day 29 end-of-day dump NEVER runs (step 719 unprocessed).
"""
import json, copy, sys, gc, traceback
from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as eng

ANIMALS = {"GOOSE", "COW", "SHEEP"}
CROPS = {"WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"}


def tile_summary(tiles, day):
    out = {
        "empty": 0, "locked": 0, "weeds": 0,
        "coop_empty": 0, "pasture_empty": 0,
        "crops": {}, "crop_yield": {}, "crop_fert_active": {},
        "animals": {}, "animal_yield": {}, "animal_at_cap": {},
        "animal_fed": {}, "animal_cared": {}, "animal_fert_avail": {},
    }
    for row in tiles:
        for t in row:
            if t is None:
                out["empty"] += 1
            elif isinstance(t, str):
                out["locked"] += 1
            else:
                k = t.get("kind", "?")
                if k == "WEED":
                    out["weeds"] += 1
                elif k == "PLANT":
                    c = t.get("crop", "?")
                    out["crops"][c] = out["crops"].get(c, 0) + 1
                    out["crop_yield"][c] = out["crop_yield"].get(c, 0) + t.get("yield_units", 0)
                    if t.get("fertilized_until_day", -1) >= day:
                        out["crop_fert_active"][c] = out["crop_fert_active"].get(c, 0) + 1
                elif k in ("COOP", "PASTURE"):
                    if "animal" in t:
                        a = t["animal"]
                        out["animals"][a] = out["animals"].get(a, 0) + 1
                        out["animal_yield"][a] = out["animal_yield"].get(a, 0) + t.get("yield_units", 0)
                        if t.get("yield_units", 0) >= (4 if a == "GOOSE" else 6):
                            out["animal_at_cap"][a] = out["animal_at_cap"].get(a, 0) + 1
                        if t.get("fed_today"):
                            out["animal_fed"][a] = out["animal_fed"].get(a, 0) + 1
                        if t.get("cared_today"):
                            out["animal_cared"][a] = out["animal_cared"].get(a, 0) + 1
                        if t.get("fertilizer_available"):
                            out["animal_fert_avail"][a] = out["animal_fert_avail"].get(a, 0) + 1
                    else:
                        if k == "COOP":
                            out["coop_empty"] += 1
                        else:
                            out["pasture_empty"] += 1
    return out


def run_god(path, seed, out_path):
    data = json.load(open(path))
    steps = data["steps"]
    names = [a["Name"] for a in data["info"]["Agents"]]
    rewards = data["rewards"]

    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.reset(2)
    env.info["seed"] = seed

    ctx = {"t": 0, "env": env, "farms": None, "privates": None}

    # ---- wrap interpreter to capture per-call state refs (identity-stable) ----
    orig_interp = eng.interpreter

    def wrapped_interpreter(state, env_):
        ctx["farms"] = [state[0].observation.farms[0], state[0].observation.farms[1]]
        ctx["privates"] = [state[0].observation.private, state[1].observation.private]
        return orig_interp(state, env_)
    env.interpreter = wrapped_interpreter

    def which_player(farm):
        f = ctx["farms"]
        return 0 if farm is f[0] else 1

    # ---- instrument _commit_unit ----
    commit_log = []
    orig_commit = eng._commit_unit

    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = orig_commit(op, item, price, farm, private, market, shed_capacity)
        if ok:
            commit_log.append([ctx["t"], which_player(farm), op, item, price])
        return ok
    eng._commit_unit = commit

    # ---- instrument _do_hire ----
    hire_log = []
    orig_hire = eng._do_hire

    def do_hire(farm, private, board_size, mult=1):
        before = len(farm["hands"])
        cost = eng._hire_cost(farm["hires_today"])
        orig_hire(farm, private, board_size, mult)
        if len(farm["hands"]) > before:
            hire_log.append([ctx["t"], which_player(farm), cost, farm["hires_today"]])
    eng._do_hire = do_hire

    # ---- instrument _do_buy_land ----
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

    # ---- instrument _apply_unit_action ----
    unit_log = []
    orig_unit = eng._apply_unit_action

    def unit_action(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity=100):
        if not isinstance(action, list) or not action:
            return
        op = action[0]
        p = which_player(farm)
        pos = eng._farmer_position(farm, idx)
        fx, fy = (pos[0], pos[1]) if pos else (-1, -1)
        tile_b = None
        if 0 <= fy < board_size and 0 <= fx < board_size:
            tl = farm["tiles"][fy][fx]
            if isinstance(tl, dict):
                tile_b = {k: tl.get(k) for k in ("kind", "crop", "animal", "yield_units",
                                                  "fed_today", "cared_today", "fertilizer_available",
                                                  "watered_today", "fertilized_until_day", "planted_day")}
        ninv = len(private["inventories"])
        while len(private["inventories"]) <= idx:
            private["inventories"].append({})
        inv_b = dict(private["inventories"][idx])
        seeds_b = dict(private["seeds"])
        shed_b = dict(private["shed"])
        orig_unit(farm, private, idx, action, board_size, day, turns_per_day, shed_capacity)
        inv_a = dict(private["inventories"][idx])
        seeds_a = dict(private["seeds"])
        shed_a = dict(private["shed"])
        tile_a = None
        if 0 <= fy < board_size and 0 <= fx < board_size:
            tl = farm["tiles"][fy][fx]
            if isinstance(tl, dict):
                tile_a = {k: tl.get(k) for k in ("kind", "crop", "animal", "yield_units",
                                                 "fed_today", "cared_today", "fertilizer_available",
                                                 "watered_today", "fertilized_until_day", "planted_day")}
        # diff
        d = {"cmd": op, "p": p, "unit": idx, "pos": [fx, fy]}
        if op == "PLANT":
            crop = action[1] if len(action) > 1 else "?"
            if seeds_b.get(crop, 0) > seeds_a.get(crop, 0):
                d["planted"] = crop
        if op == "HARVEST" and tile_b:
            if tile_a is None or tile_a.get("kind") != tile_b.get("kind"):
                # non-ongoing crop: tile cleared on harvest
                if tile_b.get("kind") == "PLANT" and tile_b.get("yield_units"):
                    d["harvest"] = [tile_b.get("crop"), tile_b.get("yield_units")]
            else:
                got = (tile_b.get("yield_units") or 0) - (tile_a.get("yield_units") or 0)
                if got > 0 and tile_a.get("kind") == "PLANT":
                    d["harvest"] = [tile_a.get("crop"), got]
                elif got > 0 and tile_a.get("animal"):
                    d["harvest"] = [tile_a.get("animal"), got]
        if op == "COLLECT_FERTILIZER" and tile_b and tile_a and tile_b.get("fertilizer_available") and not tile_a.get("fertilizer_available"):
            d["collect_fert"] = 1
        if op == "FEED" and tile_a and tile_a.get("fed_today") and tile_b and not tile_b.get("fed_today"):
            d["fed"] = tile_a.get("animal")
        if op == "CARE" and tile_a and tile_a.get("cared_today") and tile_b and not tile_b.get("cared_today"):
            d["cared"] = tile_a.get("animal")
        if op == "WATER" and tile_a and tile_a.get("watered_today") and tile_b and not tile_b.get("watered_today"):
            d["watered"] = tile_a.get("crop")
        if op == "FERTILIZE" and tile_a and (tile_a.get("fertilized_until_day") or -1) > (tile_b.get("fertilized_until_day") or -1 if tile_b else -1):
            d["fertilized"] = tile_a.get("crop")
        if op == "PLACE":
            item = action[1] if len(action) > 1 else "?"
            if tile_a and tile_a.get("animal"):
                d["placed_animal"] = tile_a.get("animal")
            elif shed_a.get(item, 0) > shed_b.get(item, 0):
                d["placed_shed"] = item
        if op == "PICKUP":
            for it in set(inv_b) | set(inv_a):
                if inv_a.get(it, 0) > inv_b.get(it, 0):
                    d["pickup"] = [it, inv_a[it] - inv_b.get(it, 0)]
        if op == "DROP":
            tot_b = sum(inv_b.values())
            tot_a = sum(inv_a.values())
            if tot_b > tot_a:
                d["drop"] = tot_b - tot_a
        # skip pure moves / passes / no-ops for size
        if any(k for k in d if k not in ("cmd", "p", "unit", "pos")):
            d["t"] = ctx["t"]
            unit_log.append(d)
    eng._apply_unit_action = unit_action

    # ---- run ----
    snapshots = []
    mismatches = []
    for t in range(1, 720):
        ctx["t"] = t
        a0 = steps[t][0].get("action") or {}
        a1 = steps[t][1].get("action") or {}
        try:
            env.step([copy.deepcopy(a0), copy.deepcopy(a1)])
        except Exception as e:
            mismatches.append({"t": t, "err": str(e), "tb": traceback.format_exc()[-400:]})
            break
        obs_m = env.state[0].observation
        obs_r = steps[t][0]["observation"]
        day = (t - 1) // 24
        # validate
        bad = None
        if obs_m.farms[0]["money"] != obs_r["farms"][0]["money"] or obs_m.farms[1]["money"] != obs_r["farms"][1]["money"]:
            bad = "money"
        elif dict(obs_m.market["inventory"]) != dict(obs_r["market"]["inventory"]):
            bad = "inv"
        elif list(obs_m.town["unlocked_shops"]) != list(obs_r["town"]["unlocked_shops"]):
            bad = "shops"
        if bad:
            mismatches.append({"t": t, "kind": bad,
                               "money": [obs_m.farms[0]["money"], obs_m.farms[1]["money"]],
                               "real_money": [obs_r["farms"][0]["money"], obs_r["farms"][1]["money"]]})
            if len(mismatches) > 20:
                break
        for p in (0, 1):
            pm = env.state[p].observation.private
            pr = steps[t][p]["observation"]["private"]
            if dict(pm["shed"]) != pr["shed"]:
                mismatches.append({"t": t, "kind": f"shed_p{p}",
                                   "mine": dict(pm["shed"]), "real": pr["shed"]})
                if len(mismatches) > 20:
                    break
            if dict(pm["seeds"]) != pr["seeds"]:
                mismatches.append({"t": t, "kind": f"seeds_p{p}",
                                   "mine": dict(pm["seeds"]), "real": pr["seeds"]})
                if len(mismatches) > 20:
                    break
        if len(mismatches) > 20:
            break
        # snapshot
        snap = {
            "t": t, "day": day, "hour": (t - 1) % 24,
            "money": [obs_m.farms[0]["money"], obs_m.farms[1]["money"]],
            "inv": dict(obs_m.market["inventory"]),
            "prices": dict(obs_m.market["prices"]),
            "shops": list(obs_m.town["unlocked_shops"]),
        }
        for p in (0, 1):
            f = obs_m.farms[p]
            pr = env.state[p].observation.private
            snap[f"p{p}"] = {
                "shed": dict(pr["shed"]),
                "seeds": dict(pr["seeds"]),
                "inv_carry": [dict(x) for x in pr["inventories"]],
                "farmer": list(f["farmer"]),
                "hands": [list(h) for h in f["hands"]],
                "hires_today": f["hires_today"],
                "tiles": tile_summary(f["tiles"], day),
            }
        snapshots.append(snap)
        if t % 120 == 0:
            print(f"  t={t} ok ({len(commit_log)} commits, {len(unit_log)} unit events)", file=sys.stderr)

    final_money = [env.state[0].observation.farms[0]["money"], env.state[0].observation.farms[1]["money"]]
    out = {
        "file": path.split("/")[-1], "names": names, "rewards": rewards,
        "seed": seed, "final_money_sim": final_money,
        "n_snapshots": len(snapshots), "n_mismatches": len(mismatches),
        "mismatch_samples": mismatches[:20],
        "commit_log": commit_log, "hire_log": hire_log, "land_log": land_log,
        "unit_log": unit_log, "snapshots": snapshots,
    }
    with open(out_path, "w") as f:
        json.dump(out, f)
    print(f"{path}: {len(snapshots)} steps replayed, {len(mismatches)} mismatches, "
          f"final {final_money} (real {rewards})", file=sys.stderr)
    return out


if __name__ == "__main__":
    for path, seed, tag in [
        ("/home/z/my-project/upload/107559251.json", 1620414037, "M1"),
        ("/home/z/my-project/upload/107573831.json", 896878425, "M2"),
    ]:
        print(f"=== GOD REPLAY {tag} ===", file=sys.stderr)
        run_god(path, seed, f"/home/z/my-project/tool-results/r2_god_{tag}.json")
        gc.collect()
    print("done", file=sys.stderr)
