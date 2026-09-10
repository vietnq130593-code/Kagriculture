#!/usr/bin/env python3
"""COUNTERFACTUAL HARNESS v2 (vòng phản cảnh) — surgical god replay.

KEY LESSON (v1): core.env does `structify(state)` before every interpreter
call and `structify(interpreter(...))` after — the state tree is re-wrapped
at each step, so mutations OUTSIDE the interpreter call never persist.
All surgery must happen INSIDE the wrapped interpreter, on the working
state object the interpreter itself mutates:

  wrapped_interpreter(state, env):
      pre_step(state)    # mutate before orig interpreter runs
      r = orig_interp(state, env)
      post_step(state)    # mutate the same working copy (persists via return)
      return r
"""
import json, copy, sys, gc
from kaggle_environments import make
import kaggle_environments.envs.kaggriculture.kaggriculture as eng

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
CROPS_CF = {
    "TOMATO":     {"first_yield_day": 8,  "interval": 1, "max_yield": 4},
    "STRAWBERRY": {"first_yield_day": 10, "interval": 2, "max_yield": 4},
}


def _shed_total(shed):
    return sum(v for v in shed.values() if isinstance(v, (int, float)))


def _take_wheat(farm, private, market, n, cost_log, from_shed=True):
    if from_shed:
        shed = private["shed"]
        have = shed.get("WHEAT", 0)
        take = min(have, n)
        if take:
            shed["WHEAT"] = have - take
            n -= take
    bought = 0
    while n > 0:
        price = eng.market_price("WHEAT", market["inventory"]["WHEAT"])
        if farm["money"] < price:
            cost_log.append(("STARVE", n))
            break
        farm["money"] -= price
        bought += 1
        n -= 1
        inv = market["inventory"]["WHEAT"]
        market["inventory"]["WHEAT"] = inv - 1 if inv > 10000 else inv + 1
    if bought:
        cost_log.append(("BUY_WHEAT", bought))


class CF:
    def __init__(self, target, label):
        self.target = target
        self.label = label
        self.tiles = []
        self.cost_log = []
        self.injected_sells = []
        self.diag = {}

    def inject_orders(self, action, new_orders):
        mkt = action.get("market") or []
        junk_idx = {i for i, o in enumerate(mkt)
                    if isinstance(o, (list, tuple)) and o and o[0] == "BUY_PRODUCT"
                    and (len(o) < 2 or o[1] not in ("WHEAT", "FERTILIZER"))}
        out = []
        ni = 0
        for i, o in enumerate(mkt):
            if i in junk_idx and ni < len(new_orders):
                out.append(list(new_orders[ni]))
                ni += 1
            else:
                out.append(list(o) if isinstance(o, (list, tuple)) else o)
        while ni < len(new_orders) and len(out) < 10:
            out.append(list(new_orders[ni]))
            ni += 1
        action["market"] = out[:10]
        return ni

    def pre_step(self, t, day, hour, farms, privates, market):
        pass

    def on_action(self, t, day, hour, p, action, farms, privates):
        pass

    def post_step(self, t, day, hour, farms, privates, market):
        pass

    def _harvest_tiles(self, farm, private, pred, max_room=80):
        shed = private["shed"]
        got = {}
        for (x, y) in self.tiles:
            tl = farm["tiles"][y][x]
            if not isinstance(tl, dict):
                continue
            if not pred(tl):
                continue
            yu = tl.get("yield_units", 0) or 0
            room = max_room - _shed_total(shed)
            take = min(yu, max(0, room))
            if take > 0:
                item = tl.get("crop") or tl.get("product") or "EGG"
                if tl.get("animal") == "GOOSE":
                    item = "EGG"
                shed[item] = shed.get(item, 0) + take
                tl["yield_units"] = yu - take
                got[item] = got.get(item, 0) + take
        return got


class GooseCF(CF):
    """N geese ADDED on target's least-used tiles; purchases respect land
    reserves (the 4 hard land laws — a $300 goose before SW = death spiral,
    verified empirically), perfect daily feed+care (market wheat), fert
    collected daily, eggs harvested daily, stock sold every morning."""

    def __init__(self, target, label, n_geese, place_day=1, occ=None):
        super().__init__(target, label)
        self.n = n_geese
        self.place_day = place_day
        self.occ = occ or {}
        self.diag["eggs_harvested"] = 0
        self.diag["fert_collected"] = 0
        self.diag["feed_wheat"] = 0
        self.diag["geese_placed"] = 0
        self.diag["shed_pressure"] = 0
        self.placed_total = 0
        self.last_buy_day = -1

    def _land_reserve(self, farm):
        nq = len(farm.get("unlocked_quadrants") or ["NW"])
        if nq == 1:
            return 1150  # NE fund
        if nq == 2:
            return 2150  # SW fund
        return 400       # operating buffer after all land

    def _place_missing(self, farm, day):
        board = len(farm["tiles"])
        have = len(self.tiles)
        if have >= self.n:
            return
        # cash discipline: 1 goose/day, must clear land reserve + $400 ops
        reserve = self._land_reserve(farm)
        if farm["money"] < 300 + reserve + 400 or day <= self.last_buy_day:
            return
        empties = []
        for y in range(board):
            for x in range(board):
                if farm["tiles"][y][x] is None:
                    o = self.occ.get(f"{x},{y}", 30)
                    empties.append((o, x, y))
        empties.sort()
        for (_, x, y) in empties[:1]:
            farm["tiles"][y][x] = {
                "kind": "COOP", "animal": "GOOSE", "placed_day": day,
                "yield_units": 0, "consecutive_unfed": 0,
                "fed_today": True, "cared_today": True,
                "fertilizer_available": False, "pending_care_bonus": 0,
            }
            self.tiles.append((x, y))
            farm["money"] -= 300
            self.cost_log.append(("GEESE_BUY", 1, 300))
            self.placed_total += 1
            self.last_buy_day = day
        self.diag["geese_placed"] = self.placed_total

    def pre_step(self, t, day, hour, farms, privates, market):
        if hour != 23 or not self.tiles:
            return
        farm, private = farms[self.target], privates[self.target]
        need = 0
        for (x, y) in self.tiles:
            tl = farm["tiles"][y][x]
            if isinstance(tl, dict) and tl.get("animal") == "GOOSE":
                tl["fed_today"] = True
                tl["cared_today"] = True
                need += 1
        if need:
            # FEED FROM HIS SHED FIRST (his own herd does; shed wheat is sunk
            # cost — zero impact on his fragile early-game CASH position).
            # Market fallback only when flush (cash kills seed/land orders).
            pw = eng.market_price("WHEAT", market["inventory"]["WHEAT"])
            shed_have = private["shed"].get("WHEAT", 0) or 0
            if shed_have >= need or farm["money"] >= pw * need + 2500:
                _take_wheat(farm, private, market, need, self.cost_log, from_shed=True)
                self.diag["feed_wheat"] += need

    def post_step(self, t, day, hour, farms, privates, market):
        if day < self.place_day:
            return
        farm, private = farms[self.target], privates[self.target]
        # placement attempts: every hour is fine now (cash-gated, 1/day)
        self._place_missing(farm, day)
        if not self.tiles or hour != 23:
            return
        shed = private["shed"]
        # keep the shed clear for HIS end-of-day dump: collect/harvest only
        # while there is headroom
        room = 80 - _shed_total(shed)
        if room < 0:
            self.diag["shed_pressure"] += 1
        for (x, y) in list(self.tiles):
            tl = farm["tiles"][y][x]
            if not (isinstance(tl, dict) and tl.get("animal") == "GOOSE"):
                continue
            # FERT POLICY: top up his working stock only (his own recorded
            # SELL FERTILIZER + PICKUP orders drain it at his rhythm). NEVER
            # sell fert ourselves — his units need it for event fertilizing.
            if tl.get("fertilizer_available") and shed.get("FERTILIZER", 0) < 12 \
                    and _shed_total(shed) < 80:
                shed["FERTILIZER"] = shed.get("FERTILIZER", 0) + 1
                tl["fertilizer_available"] = False
                self.diag["fert_collected"] += 1
        got = self._harvest_tiles(farm, private, lambda tl: tl.get("animal") == "GOOSE")
        self.diag["eggs_harvested"] += got.get("EGG", 0)

    def on_action(self, t, day, hour, p, action, farms, privates):
        if p != self.target or not self.tiles:
            return
        if day < self.place_day + 4:
            return
        # sell every hour from h0: stock must clear before HIS end-of-day dump
        shed = privates[p]["shed"]
        orders = []
        e = shed.get("EGG", 0)
        if e:
            orders.append(["SELL", "EGG", min(e, 8)])
        if orders:
            n_inj = self.inject_orders(action, orders)
            for o in orders[:n_inj]:
                self.injected_sells.append((t, o[1], o[2]))
        if day == 29 and hour == 22:
            fin = []
            n = shed.get("EGG", 0)
            if n:
                fin.append(["SELL", "EGG", n])
            if fin:
                self.inject_orders(action, fin)
                for o in fin:
                    self.injected_sells.append((t, o[1], o[2]))


class CropCF(CF):
    """Convert target's young WHEAT tiles to crop at plant_day; water daily,
    fert from shed on event days; harvest events to shed; sell when free."""

    def __init__(self, target, label, crop, n_tiles, plant_day):
        super().__init__(target, label)
        self.crop = crop
        self.n = n_tiles
        self.plant_day = plant_day
        self.planted = False
        self.cd = CROPS_CF[crop]
        self.diag = {"harvested": 0, "fert_used": 0}

    def _event_days(self):
        # production credits at END of day (planted + first + i*interval - 1):
        # days_since_first = next_day - planted - first = i*interval at
        # next_day = planted + first + i*interval, i.e. END of day N-1.
        d0 = self.plant_day + self.cd["first_yield_day"] - 1
        return {d0 + i * self.cd["interval"] for i in range(self.cd["max_yield"])}

    def _convert(self, farm):
        board = len(farm["tiles"])
        cands = []
        for y in range(board):
            for x in range(board):
                tl = farm["tiles"][y][x]
                if (isinstance(tl, dict) and tl.get("kind") == "PLANT"
                        and tl.get("crop") == "WHEAT"
                        and (tl.get("yield_units", 0) or 0) <= 2):
                    cands.append((x, y, tl.get("planted_day", 0)))
        cands.sort(key=lambda c: -c[2])  # youngest wheat first (least forgone)
        taken = []
        for (x, y, _) in cands[: self.n]:
            farm["tiles"][y][x] = {
                "kind": "PLANT", "crop": self.crop, "planted_day": self.plant_day,
                "watered_today": False, "consecutive_unwatered": 0,
                "yield_units": 0, "max_lifespan_step": -1, "fertilized_until_day": -1,
            }
            taken.append((x, y))
        self.tiles = taken
        return len(taken)

    def post_step(self, t, day, hour, farms, privates, market):
        if not self.planted:
            if day >= self.plant_day and hour == 23:
                farm = farms[self.target]
                n = self._convert(farm)
                cost = (100 if self.crop == "STRAWBERRY" else 50) * n
                if farm["money"] >= cost:
                    farm["money"] -= cost
                else:  # cannot afford this wave — skip surgery
                    self.planted = True
                    self.tiles = []
                    return
                self.cost_log.append(("SEEDS", n, cost))
                self.planted = True
            return
        if hour != 23:
            return
        farm, private = farms[self.target], privates[self.target]
        got = self._harvest_tiles(farm, private, lambda tl: tl.get("crop") == self.crop, max_room=80)
        self.diag["harvested"] += got.get(self.crop, 0)

    def pre_step(self, t, day, hour, farms, privates, market):
        if hour != 23 or not self.tiles or not self.planted:
            return
        farm, private = farms[self.target], privates[self.target]
        # FEED-BUY PROTECTION: converting wheat tiles removes his feed rotation;
        # a smart player flips to buying feed (top-3 bought 133-449u/mùa).
        animals = sum(1 for row in farm["tiles"] for tl in row
                      if isinstance(tl, dict) and "animal" in tl)
        shed_w = private["shed"].get("WHEAT", 0) or 0
        # top-up ABOVE his morning drain (his recorded SELL WHEAT 20-35u +
        # unit PICKUPs ~15-20u at h0-h6 happen before any harvest flows in)
        target = animals * 2 + 40
        if animals > 0 and shed_w < target and farm["money"] > 400:
            pw = eng.market_price("WHEAT", market["inventory"]["WHEAT"])
            want = min(target - shed_w, int((farm["money"] - 300) // max(1, pw)))
            n = min(12, want)
            if n > 0:
                farm["money"] -= n * pw
                market["inventory"]["WHEAT"] -= n
                private["shed"]["WHEAT"] = shed_w + n
                self.cost_log.append(("BUY_FEED", n, n * pw))
        events = self._event_days()
        # buy fert at market for event days (top-3 bought 17-50u for exactly
        # this purpose) instead of stealing his working stock
        buy_fert = 0
        if day in events:
            need = sum(1 for (x, y) in self.tiles
                       if isinstance(farm["tiles"][y][x], dict)
                       and farm["tiles"][y][x].get("crop") == self.crop)
            price = eng.market_price("FERTILIZER", market["inventory"]["FERTILIZER"])
            afford = int((farm["money"] - 300) // price) if price > 0 else 0
            buy_fert = min(need, afford)
            if buy_fert > 0:
                farm["money"] -= buy_fert * price
                market["inventory"]["FERTILIZER"] -= buy_fert
                self.cost_log.append(("BUY_FERT", buy_fert, buy_fert * price))
                self.diag["fert_used"] += buy_fert
        applied = 0
        for (x, y) in self.tiles:
            tl = farm["tiles"][y][x]
            if not (isinstance(tl, dict) and tl.get("crop") == self.crop):
                continue
            tl["watered_today"] = True
            if day in events and applied < buy_fert:
                tl["fertilized_until_day"] = day
                applied += 1

    def on_action(self, t, day, hour, p, action, farms, privates):
        if p != self.target or not self.planted:
            return
        if day < self.plant_day + self.cd["first_yield_day"]:
            return
        shed = privates[p]["shed"]
        n = shed.get(self.crop, 0)
        if n and hour >= 0:
            k = min(n, 10)
            n_inj = self.inject_orders(action, [["SELL", self.crop, k]])
            if n_inj:
                self.injected_sells.append((t, self.crop, k))
        if day == 29 and hour == 22:
            n = shed.get(self.crop, 0)
            if n:
                self.inject_orders(action, [["SELL", self.crop, n]])
                self.injected_sells.append((t, self.crop, n))


class SubsGeeseCF(CF):
    """SHEEP→GOOSE substitution at the action level (purest causal test of the
    shop-draw read): every BUY_ANIMAL SHEEP n becomes BUY_ANIMAL GOOSE m
    (m = ceil(5n/3), cash-equal-or-cheaper), every BUILD_PASTURE becomes
    BUILD_COOP, every PLACE SHEEP becomes PLACE GOOSE. Same money, same tiles,
    same recorded labor (feed/care/collect/harvest all still hit). Wool
    disappears (his SELL WOOL orders no-op); eggs are sold by injected
    orders. Option place_shed_geese: also place geese sitting in his shed
    (fixes SpaTaro M2's 3 bought-but-never-placed geese) at 1/day h23."""

    def __init__(self, target, label, marks=None, place_shed_geese=False,
                 sheep_commits=None):
        super().__init__(target, label)
        self.marks = {(int(t), str(k)) for t, k in (marks or [])}
        self.place_shed = place_shed_geese
        self.sheep_commits = {int(t): int(n) for t, n in (sheep_commits or {}).items()}
        self.diag = {"geese_bought": 0, "geese_placed_shed": 0, "feed_wheat": 0}
        self._placed_day = -1

    def on_action(self, t, day, hour, p, action, farms, privates):
        if p != self.target:
            return
        mkt = action.get("market") or []
        for o in mkt:
            if (isinstance(o, (list, tuple)) and len(o) >= 3 and o[0] == "BUY_ANIMAL"
                    and o[1] == "SHEEP"):
                # CASH-MATCHED: only substitute what the ORIGINAL actually
                # committed at this step (his later sheep orders failed for
                # cash in the original; letting cheaper geese succeed would
                # drain his seed money — verified empirically).
                committed = self.sheep_commits.get(t, 0)
                if committed <= 0:
                    o[0], o[1], o[2] = "PASS_ORDER", "PASS", 0  # drop
                    continue
                m = max(1, (5 * committed) // 3)  # never costs more than sheep
                o[0], o[1], o[2] = "BUY_ANIMAL", "GOOSE", m
                self.diag["geese_bought"] += m
        for key in ("farmer", "hands"):
            lst = action.get(key) or []
            if not isinstance(lst, list):
                continue
            ukey = "F" if key == "farmer" else None
            for i, u in enumerate(lst):
                if not isinstance(u, (list, tuple)) or not u:
                    continue
                k = ukey if ukey else i
                if u[0] == "BUILD_PASTURE" and (t, str(k)) in self.marks:
                    u[0] = "BUILD_COOP"
                elif (len(u) >= 2 and u[0] == "PLACE" and u[1] == "SHEEP"):
                    u[1] = "GOOSE"
        # sell EGGS only (fert flows through his own pipeline)
        if hour >= 0 and day >= 2:
            shed = privates[p]["shed"]
            orders = []
            e = shed.get("EGG", 0)
            if e:
                orders.append(["SELL", "EGG", min(e, 8)])
            if orders:
                self.inject_orders(action, orders)
                for o in orders:
                    self.injected_sells.append((t, o[1], o[2]))
        if day == 29 and hour == 22:
            shed = privates[p]["shed"]
            fin = []
            n = shed.get("EGG", 0)
            if n:
                fin.append(["SELL", "EGG", n])
            if fin:
                self.inject_orders(action, fin)

    def pre_step(self, t, day, hour, farms, privates, market):
        if hour != 23 or not self.tiles:
            return
        farm, private = farms[self.target], privates[self.target]
        need = 0
        for (x, y) in self.tiles:
            tl = farm["tiles"][y][x]
            if isinstance(tl, dict) and tl.get("animal") == "GOOSE":
                tl["fed_today"] = True
                tl["cared_today"] = True
                need += 1
        if need:
            pw = eng.market_price("WHEAT", market["inventory"]["WHEAT"])
            shed_have = private["shed"].get("WHEAT", 0) or 0
            if shed_have >= need or farm["money"] >= pw * need + 2500:
                _take_wheat(farm, private, market, need, self.cost_log, from_shed=True)
                self.diag["feed_wheat"] = self.diag.get("feed_wheat", 0) + need

    def post_step(self, t, day, hour, farms, privates, market):
        farm, private = farms[self.target], privates[self.target]
        if hour == 23:
            # maintenance of MY shed-placed geese: harvest eggs, top up fert
            shed = private["shed"]
            for (x, y) in list(self.tiles):
                tl = farm["tiles"][y][x]
                if not (isinstance(tl, dict) and tl.get("animal") == "GOOSE"):
                    continue
                yu = tl.get("yield_units", 0) or 0
                if yu > 0 and _shed_total(shed) < 80:
                    shed["EGG"] = shed.get("EGG", 0) + yu
                    tl["yield_units"] = 0
                if tl.get("fertilizer_available") and shed.get("FERTILIZER", 0) < 12 \
                        and _shed_total(shed) < 80:
                    shed["FERTILIZER"] = shed.get("FERTILIZER", 0) + 1
                    tl["fertilizer_available"] = False
        if not self.place_shed or hour != 23 or day <= self._placed_day:
            return
        shed = private["shed"]
        if shed.get("GOOSE", 0) <= 0:
            return
        board = len(farm["tiles"])
        for y in range(board):
            for x in range(board):
                tl = farm["tiles"][y][x]
                if (isinstance(tl, dict) and tl.get("kind") == "COOP"
                        and "animal" not in tl):
                    shed["GOOSE"] -= 1
                    if shed["GOOSE"] <= 0:
                        del shed["GOOSE"]
                    farm["tiles"][y][x] = {
                        "kind": "COOP", "animal": "GOOSE", "placed_day": day,
                        "yield_units": 0, "consecutive_unfed": 0,
                        "fed_today": True, "cared_today": True,
                        "fertilizer_available": False, "pending_care_bonus": 0,
                    }
                    self.diag["geese_placed_shed"] += 1
                    self.tiles.append((x, y))
                    self._placed_day = day
                    return
        # no empty coop — build one on a WEED tile (dig+build, $100 ignored)
        for y in range(board):
            for x in range(board):
                tl = farm["tiles"][y][x]
                if isinstance(tl, dict) and tl.get("kind") == "WEED":
                    shed["GOOSE"] -= 1
                    if shed["GOOSE"] <= 0:
                        del shed["GOOSE"]
                    farm["tiles"][y][x] = {
                        "kind": "COOP", "animal": "GOOSE", "placed_day": day,
                        "yield_units": 0, "consecutive_unfed": 0,
                        "fed_today": True, "cared_today": True,
                        "fertilizer_available": False, "pending_care_bonus": 0,
                    }
                    self.diag["geese_placed_shed"] += 1
                    self.tiles.append((x, y))
                    self._placed_day = day
                    return


def run_cf(path, seed, cf, out_path=None):
    data = json.load(open(path))
    steps = data["steps"]
    names = [a["Name"] for a in data["info"]["Agents"]]
    rewards = data["rewards"]
    target = cf.target

    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.reset(2)
    env.info["seed"] = seed

    ctx = {"t": 0}
    orig_interp = eng.interpreter
    commit_log = []
    orig_commit = eng._commit_unit

    def wrapped_interpreter(state, env_):
        obs0 = state[0].observation
        farms = [obs0.farms[0], obs0.farms[1]]
        privates = [state[0].observation.private, state[1].observation.private]
        market = obs0.market
        t = ctx["t"]
        day, hour = (t - 1) // 24, (t - 1) % 24

        def which_player(farm):
            return 0 if farm is farms[0] else 1

        def commit(op, item, price, farm, private, mkt, shed_capacity=100):
            ok = orig_commit(op, item, price, farm, private, mkt, shed_capacity)
            if ok:
                commit_log.append([t, which_player(farm), op, item, price])
            return ok
        eng._commit_unit = commit
        try:
            cf.pre_step(t, day, hour, farms, privates, market)
            r = orig_interp(state, env_)
            cf.post_step(t, day, hour, farms, privates, market)
        finally:
            eng._commit_unit = orig_commit
        return r
    env.interpreter = wrapped_interpreter

    daily = []
    for t in range(1, 720):
        ctx["t"] = t
        day, hour = (t - 1) // 24, (t - 1) % 24
        # actions (surgery on orders)
        acts = []
        st_farms = env.state[0].observation.farms
        st_priv = [env.state[0].observation.private, env.state[1].observation.private]
        for p in (0, 1):
            a = copy.deepcopy(steps[t][p].get("action") or {})
            cf.on_action(t, day, hour, p, a, st_farms, st_priv)
            acts.append(a)
        env.step(acts)
        if hour == 23:
            obs = env.state[0].observation
            # tile diagnostics for target
            tf = obs.farms[target]
            crops = {}
            animals = {}
            for row in tf["tiles"]:
                for tl in row:
                    if isinstance(tl, dict):
                        if tl.get("kind") == "PLANT":
                            crops[tl.get("crop")] = crops.get(tl.get("crop"), 0) + 1
                        if "animal" in tl:
                            animals[tl["animal"]] = animals.get(tl["animal"], 0) + 1
            daily.append({
                "day": day,
                "money": [obs.farms[0]["money"], obs.farms[1]["money"]],
                "prices": dict(obs.market["prices"]),
                "inv": dict(obs.market["inventory"]),
                "shed": [dict(st_priv[0]["shed"]), dict(st_priv[1]["shed"])],
                "crops": crops, "animals": animals,
                "n_hands": len(env.state[0].observation.farms[target]["hands"]),
            })

    final_money = [env.state[0].observation.farms[0]["money"],
                   env.state[0].observation.farms[1]["money"]]
    env.interpreter = orig_interp
    eng._commit_unit = orig_commit

    ledger = {}
    for (t, p, op, item, price) in commit_log:
        if p != target or op != "SELL":
            continue
        d = ledger.setdefault(item, [0, 0.0])
        d[0] += 1
        d[1] += price
    buys = {}
    for (t, p, op, item, price) in commit_log:
        if p != target or op != "BUY_SEED":
            continue
        k = buys.setdefault(item, [0, 0.0])
        k[0] += 1
        k[1] += price
    out = {
        "file": path.split("/")[-1], "label": cf.label, "names": names,
        "seed": seed, "target": target,
        "original_rewards": rewards, "final_money": final_money,
        "delta": final_money[target] - rewards[target],
        "opp_delta": final_money[1 - target] - rewards[1 - target],
        "ledger_target": ledger, "buys_target": buys,
        "cost_log": cf.cost_log, "injected_sells": cf.injected_sells,
        "diag": cf.diag, "daily": daily,
    }
    if out_path:
        with open(out_path, "w") as f:
            json.dump(out, f)
    print(f"[{cf.label}] {path.split('/')[-1]}: final {final_money} "
          f"(orig {rewards}) delta_target={out['delta']:+,.0f} "
          f"opp={out['opp_delta']:+,.0f} diag={cf.diag}", flush=True)
    return out


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    M1 = ("/home/z/my-project/upload/107559251.json", 1620414037, 0)
    M2 = ("/home/z/my-project/upload/107573831.json", 896878425, 0)
    OUT = "/home/z/my-project/tool-results/cf_"

    def load_occ(p):
        d = json.load(open(p))
        return {f"{x},{y}": d["occ"][y][x]
                for y in range(d["board"]) for x in range(d["board"])}

    occ_m1 = load_occ("/home/z/my-project/tool-results/cf_occ_M1_p0.json")
    occ_m2 = load_occ("/home/z/my-project/tool-results/cf_occ_M2_p0.json")
    exps = []
    sb = json.load(open("/home/z/my-project/tool-results/cf_sheepbuilds.json"))
    marks_m1 = [tuple(x) for x in sb["M1"]]
    marks_m2 = [tuple(x) for x in sb["M2"]]
    from collections import defaultdict

    def sheep_commits(god_path, p=0):
        o = json.load(open(god_path))
        d = defaultdict(int)
        for (t, pp, op, item, price) in o["commit_log"]:
            if pp == p and op == "BUY_ANIMAL" and item == "SHEEP":
                d[t] += 1
        return dict(d)

    sc_m1 = sheep_commits("/home/z/my-project/tool-results/r2_god_M1.json")
    sc_m2 = sheep_commits("/home/z/my-project/tool-results/r2_god_M2.json")
    if which in ("all", "s1"):
        exps.append((lambda: SubsGeeseCF(0, "S1: SpaTaro M1 sheep->geese cash-matched", marks_m1, True, sc_m1), M1, "M1_sheep2geese"))
    if which in ("all", "s2"):
        exps.append((lambda: SubsGeeseCF(0, "S2: SpaTaro M2 sheep->geese cash-matched", marks_m2, True, sc_m2), M2, "M2_sheep2geese"))
    if which in ("all", "cf1"):
        exps.append((lambda: GooseCF(0, "CF1: SpaTaro M1 +6 geese (land-safe)", 6, 1, occ_m1), M1, "M1_goose6"))
    if which in ("all", "cf7"):
        exps.append((lambda: GooseCF(0, "CF7: SpaTaro M1 +10 geese (land-safe)", 10, 1, occ_m1), M1, "M1_goose10"))
    if which in ("all", "cf4"):
        exps.append((lambda: CropCF(0, "CF4: SpaTaro M2 +20 straw d12 (feed-buy)", "STRAWBERRY", 20, 12), M2, "M2_straw20"))
    if which in ("all", "cf5"):
        exps.append((lambda: CropCF(0, "CF5: SpaTaro M2 +10 tomato d17 (feed-buy)", "TOMATO", 10, 17), M2, "M2_tom10"))
    for mk, (path, seed, tgt), name in exps:
        run_cf(path, seed, mk(), OUT + name + ".json")
        gc.collect()
    print("done", flush=True)
