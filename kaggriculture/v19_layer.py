# ====================================================================== REAPER layer
# v19 Phase-1 market-timing modules layered on the embedded v18 (K0006).
# All names below resolve into this module's globals; `_V18_NS` and `_V18`
# were populated by the exec block above. Original work, 2026-09-16.
#
# Evidence base: research/v19/06_TOP1_7MATCH_DEEP_ANALYSIS.md
# (7 public episodes of #1 Majkel1337, 5W/2L) → 05_V19_DEPLOYMENT_PLAN.md §3.1.
# Step-numbering note: replay entry indexes are +1 vs engine submission steps
# (verified empirically: with episodeSteps=720 the last EXECUTED step is 718);
# the research docs' "s715-719" window therefore maps to engine steps 714-718.
#
#   A1  ENDGAME LIQUIDATION (front-run) — from step 696 (0h d29, matching
#       the intel money-lifecycle "buys → $0 from d28") the market list is
#       liquidation-only: dead-money BUYs are stripped (seeds cannot mature,
#       animals/land cannot pay back inside one day; FERTILIZER buys stay —
#       they still double same-day TOMATO yields) and every product's SELL cap
#       is boosted to shed+phantom so each step's harvest→DROP inflow is sold
#       in the SAME step's market, ahead of the opponent's endgame dumps
#       (lockstep: earlier sellers get pre-dump prices).  Step-numbering note:
#       replay entry indexes are +1 vs engine submission steps (verified
#       empirically: with episodeSteps=720 the last EXECUTED step is 718), so
#       the research docs' "s715-719" window maps to engine steps 714-718.
#
#   A2  TROUGH THROTTLE (Phase-1: DISABLED) — per-item 14-day rolling price
#       peak; while price is below 0.85 × peak, premium sells are capped at 3
#       units/step, releasing on RECOVERY (price ≥ 1.15 × 3-day min) and
#       aborting on STRUCTURAL oversupply (market inventory above its 3-day
#       level).  Kept in code but off by default: in the v18 mirror meta the
#       crash-hold is a net loser (the opponent never stops flowing, so the
#       recovery tops out far below the pre-crash level — T1 battery: 1W/47L,
#       mean −$1,280).  To be re-calibrated in Phase 2 against diverse
#       (holder-style) opponents before enabling.
#
#   A4  STRICT DEBT INVARIANT — every unit the v18 advance layer sells early
#       is recorded in a per-item ledger; tape SELL caps on later steps are
#       reduced by exactly the absorbed amounts, so "advance" moves revenue
#       in time instead of printing extra units into price impact
#       (cap semantics would otherwise oversell).
#
#   C1  REAPER state + v18 TELEMETRY reset whenever a new episode is
#       detected (step counter restarts), fixing cross-episode accumulation.

A1_START = 696        # 0h d29 (intel: "buys → $0 from d28"): liquidation-only
A1_CATCH = 40         # phantom cap on top of shed counts (the interpreter
                      # sells only what exists; units harvested and DROPped
                      # during this step's verb phase are still caught)
A2_ENABLED = False    # Phase-1: off (mirror-meta net loser; see header note)

A2_TROUGH_RATIO = 0.85
A2_CAP = 3            # max units/step sold of a trough item
A2_SHED_ROOM = 85     # no throttling when the shed is this full
PEAK_WINDOW = 336     # 14-day rolling peak
A2_MIN_WINDOW = 72    # 3-day rolling minimum (recovery reference)
A2_INV_WINDOW = 72    # 3-day inventory momentum (structural abort)
A2_RECOVERY = 1.15    # release when price >= 1.15 x 3-day minimum
A2_INV_TOL = 5        # structural abort when inventory rose by more than this

V19_THROTTLE_ITEMS = ("STRAWBERRY", "MILK", "EGG", "CARROT", "TOMATO")

# engine SHOPS table (kaggriculture.py L103-111) — single-product shops
# consume 2 units/cycle (L739-743); shops fire 6×/day, town center 1×/day.
_V19_SHOPS = {
    "BAKERY":         ("EGG", "WHEAT"),
    "PIZZA_SHOP":     ("MILK", "TOMATO", "WHEAT"),
    "BRUNCH_SPOT":    ("EGG", "WHEAT", "STRAWBERRY"),
    "YARN_STORE":     ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY", "MILK", "WHEAT"),
    "PET_CAFE":       ("CARROT",),
    "SMOOTHIE_SHOP":  ("STRAWBERRY", "MILK"),
    "FARMERS_MARKET": ("WHEAT", "CARROT", "TOMATO", "STRAWBERRY"),
}

# soft per-order chunk caps (A6-lite, engine-exact above_func classes)
_V19_CHUNK_CAP = {
    "WOOL": 3, "MELON": 3, "MILK": 5, "STRAWBERRY": 5,
    "CARROT": 8, "TOMATO": 8, "WHEAT": 10, "EGG": 10, "FERTILIZER": 8,
}

V19_TELEMETRY = {}
_V19 = {"last_step": 1 << 30, "samples": {}, "inv": {}, "ledger": {}}


def _v19_reset():
    _V19["samples"] = {}
    _V19["inv"] = {}
    _V19["ledger"] = {}
    try:
        _V18_NS["TELEMETRY"].clear()          # C1: v18 counters are per-episode
    except Exception:
        pass


def _v19_tick(step):
    if step <= _V19["last_step"]:
        _v19_reset()
        V19_TELEMETRY["v19_resets"] = V19_TELEMETRY.get("v19_resets", 0) + 1
    _V19["last_step"] = step


def _v19_track_prices(obs):
    try:
        step = int(obs["step"])
        market = obs["market"]
        prices = market["prices"]
        invs = market["inventory"]
        s = _V19["samples"]
        iv = _V19["inv"]
        for item, p in prices.items():
            s.setdefault(item, []).append((step, float(p)))
        for item, n in invs.items():
            iv.setdefault(item, []).append((step, float(n)))
        lo_p = step - PEAK_WINDOW
        lo_i = step - A2_INV_WINDOW
        for item in list(s):
            q = s[item]
            if q and q[0][0] <= lo_p:
                s[item] = [t for t in q if t[0] > lo_p]
        for item in list(iv):
            q = iv[item]
            if q and q[0][0] <= lo_i:
                iv[item] = [t for t in q if t[0] > lo_i]
    except Exception:
        pass


def _v19_peak(item):
    q = _V19["samples"].get(item) or []
    return max((p for _, p in q), default=0.0)


def _v19_recent_min(item, window):
    q = _V19["samples"].get(item) or []
    if not q:
        return None
    lo = q[-1][0] - window
    vals = [p for st, p in q if st > lo]
    return min(vals) if vals else None


def _v19_inv_then(item, step, back):
    """Market inventory ~`back` steps ago (latest sample at or before
    step-back); None when no history reaches that far."""
    q = _V19["inv"].get(item) or []
    target = step - back
    best = None
    for st, n in q:
        if st <= target:
            best = n
        else:
            break
    return best


def _v19_sell_caps(mk):
    d = {}
    for o in mk or []:
        if isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == "SELL":
            try:
                d[o[1]] = d.get(o[1], 0) + max(0, int(o[2]))
            except Exception:
                pass
    return d


def _v19_sim_ok(obs, orders):
    """Both-pressure solo-sim gate, same contract as the v18 frontload layer."""
    try:
        me = int(obs["player"])
        farm = obs["farms"][me]
        private = obs["private"]
        money = float(farm["money"])
        shed_total = sum(int(v) for v in private["shed"].values())
        inv = {k: int(v) for k, v in obs["market"]["inventory"].items()}
        hires_today = int(farm.get("hires_today", 0))
        n_land_extra = max(0, len(farm.get("unlocked_quadrants", ["NW"])) - 1)
        params = _V18_NS["_MARKET_PARAMS"]
        sim = _V18_NS["_simulate"]
        for pressure in (0, 1):
            ok, _ = sim(orders, money, shed_total, inv, hires_today,
                        n_land_extra, params, pressure)
            if not ok:
                return False
        return True
    except Exception:
        return False


def _v19_a4_absorb(obs, market):
    """A4: reduce tape SELL caps by the units already sold early (ledger)."""
    ledger = _V19["ledger"]
    if not ledger or not isinstance(market, list) or not market:
        return market
    debt_items = set()
    for o in market:
        if (isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == "SELL"
                and ledger.get(o[1], 0) > 0):
            debt_items.add(o[1])
    if not debt_items:
        return market
    new = []
    undone = []
    for o in market:
        if (isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == "SELL"
                and o[1] in debt_items):
            o = list(o)
            try:
                cap = max(0, int(o[2]))
            except Exception:
                cap = 0
            debt = ledger.get(o[1], 0)
            absorb = min(cap, debt)
            if absorb > 0:
                ledger[o[1]] = debt - absorb
                undone.append((o[1], absorb))
                if cap - absorb <= 0:
                    continue               # fully-absorbed order: drop it (a
                                              # zero-cap SELL would fail sims)
                o[2] = cap - absorb
        new.append(o)
    if not undone:
        return market
    if _v19_sim_ok(obs, market) and not _v19_sim_ok(obs, new):
        for item, a in undone:                   # execution would break: revert
            ledger[item] = ledger.get(item, 0) + a
        V19_TELEMETRY["a4_reverted"] = V19_TELEMETRY.get("a4_reverted", 0) + 1
        return market
    V19_TELEMETRY["a4_absorbed"] = V19_TELEMETRY.get("a4_absorbed", 0) + sum(a for _, a in undone)
    return new


def _v19_advance(obs, market):
    """v18 advance_sales wrapped with A4 ledger accounting."""
    before = _v19_sell_caps(market)
    res = _V18_NS["advance_sales"](obs, market, _V18_NS["_future_market"], V19_TELEMETRY)
    try:
        if res is not market and isinstance(res, list):
            after = _v19_sell_caps(res)
            for it, q in after.items():
                d = q - before.get(it, 0)
                if d > 0:
                    _V19["ledger"][it] = _V19["ledger"].get(it, 0) + d
                    V19_TELEMETRY["a4_debt"] = V19_TELEMETRY.get("a4_debt", 0) + d
    except Exception:
        pass
    return res


def _v19_a2_throttle(obs, market):
    """A2: price-gated sell rate for premium items in a payable trough."""
    try:
        step = int(obs["step"])
    except Exception:
        return market
    if step % 24 == 23 or step >= A1_START:
        return market
    if not isinstance(market, list) or not market:
        return market
    try:
        shed_total = sum(int(v) for v in obs["private"]["shed"].values())
        prices = obs["market"]["prices"]
        invs = obs["market"]["inventory"]
    except Exception:
        return market
    if shed_total >= A2_SHED_ROOM:
        return market
    params = _V18_NS["_MARKET_PARAMS"]
    trough = set()
    for item in V19_THROTTLE_ITEMS:
        p = prices.get(item)
        if p is None:
            continue
        base = params[item]["base"]
        peak = _v19_peak(item)
        if not (p < base or (peak > 0 and p < A2_TROUGH_RATIO * peak)):
            continue                                  # not in a trough
        rmin = _v19_recent_min(item, A2_MIN_WINDOW)
        if rmin is not None and p >= A2_RECOVERY * rmin:
            V19_TELEMETRY["a2_released"] = V19_TELEMETRY.get("a2_released", 0) + 1
            continue                                  # recovery: sell the bounce
        inv_then = _v19_inv_then(item, step, A2_INV_WINDOW)
        inv_now = invs.get(item)
        if inv_then is not None and inv_now is not None and inv_now > inv_then + A2_INV_TOL:
            V19_TELEMETRY["a2_structural"] = V19_TELEMETRY.get("a2_structural", 0) + 1
            continue                                  # oversupply: sell through
        trough.add(item)
    if not trough:
        return market
    hits = False
    for o in market:
        if (isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == "SELL"
                and o[1] in trough):
            hits = True
            break
    if not hits:
        return market
    ledger = _V19["ledger"]
    budget = dict.fromkeys(trough, A2_CAP)
    new = []
    trimmed = 0
    for o in market:
        if (isinstance(o, (list, tuple)) and len(o) > 2 and o[0] == "SELL"
                and o[1] in trough):
            o = list(o)
            try:
                cap = max(0, int(o[2]))
            except Exception:
                cap = 0
            b = budget.get(o[1], 0)
            if cap > b:
                cut = cap - b
                trimmed += cut
                debt = ledger.get(o[1], 0)      # keep the A4 ledger honest
                if debt > 0:
                    ledger[o[1]] = max(0, debt - min(cut, debt))
                if b <= 0:
                    continue                   # budget exhausted: drop the
                                                  # order (zero-cap fails sims)
                o[2] = b
                budget[o[1]] = 0
            else:
                budget[o[1]] = b - cap
        new.append(o)
    if not trimmed:
        return market
    if _v19_sim_ok(obs, market) and not _v19_sim_ok(obs, new):
        V19_TELEMETRY["a2_reverted"] = V19_TELEMETRY.get("a2_reverted", 0) + 1
        return market
    V19_TELEMETRY["a2_throttle_turns"] = V19_TELEMETRY.get("a2_throttle_turns", 0) + 1
    V19_TELEMETRY["a2_throttle_units"] = V19_TELEMETRY.get("a2_throttle_units", 0) + trimmed
    return new


def _v19_a1_liquidation(obs, market):
    """A1: liquidation-only market list for d29. Returns a new list or None.

    - strips dead-money BUYs (BUY_SEED / BUY_ANIMAL / BUY_LAND / BUY_PRODUCT
      except FERTILIZER); HIRE stays (hands harvest the final day);
    - boosts every product SELL cap to shed+phantom and appends catch-all
      SELLs for uncovered products, so the current step's harvest→DROP
      inflow is sold this very step (front-running the endgame dumps)."""
    try:
        have = {k: int(v) for k, v in obs["private"]["shed"].items()}
    except Exception:
        return None
    if not isinstance(market, list):
        return None
    have = {it: q for it, q in have.items() if q > 0}
    params = _V18_NS["_MARKET_PARAMS"]
    new = []
    covered = set()
    changed = False
    for o in market:
        if not (isinstance(o, (list, tuple)) and o):
            new.append(o)
            continue
        op = o[0]
        if op in ("BUY_SEED", "BUY_ANIMAL", "BUY_LAND"):
            changed = True
            continue                               # dead money on d29
        if op == "BUY_PRODUCT" and len(o) > 1 and o[1] != "FERTILIZER":
            changed = True
            continue                               # feed has no d29 payoff
        if (op == "SELL" and len(o) > 2 and o[1] in params):
            item = o[1]
            covered.add(item)
            o = list(o)
            try:
                cap = max(0, int(o[2]))
            except Exception:
                cap = 0
            want = have.get(item, 0) + A1_CATCH
            if want > cap:
                o[2] = want
                changed = True
        new.append(o)
    # catch-alls for products with shed stock but no SELL this step
    for item in sorted(have, key=lambda it: -have[it]):
        if len(new) >= 10:
            break
        if item in covered or item not in params:
            continue
        new.append(["SELL", item, have[item] + A1_CATCH])
        changed = True
    if not changed:
        return None
    return new[:10]


def _arena_diag(obs):
    """REAPER telemetry for the arena observer (run_battle.extract_diag)."""
    try:
        return {
            "v19": dict(V19_TELEMETRY),
            "ledger": {k: v for k, v in _V19["ledger"].items() if v},
            "step": int(obs.get("step") or 0),
        }
    except Exception:
        return {}


def agent(observation, configuration=None):
    action = _V18(observation, configuration)
    try:
        if isinstance(action, dict) and _V18_NS["_standard"](configuration):
            step = int(observation["step"])
            _v19_tick(step)                       # C1 new-episode reset
            _v19_track_prices(observation)
            m = action.get("market")
            m = list(m) if isinstance(m, list) else []
            if step >= A1_START:
                new = _v19_a1_liquidation(observation, m)
                if new is not None and new != m:
                    action = dict(action)
                    action["market"] = new
                    V19_TELEMETRY["a1_turns"] = V19_TELEMETRY.get("a1_turns", 0) + 1
            else:
                m2 = _v19_a4_absorb(observation, m)
                adv = _v19_advance(observation, m2)
                if isinstance(adv, list) and len(adv) > 1:
                    adv = _V18_NS["frontload"](observation, adv, None, V19_TELEMETRY)
                if A2_ENABLED:
                    adv = _v19_a2_throttle(observation, adv)
                if adv is not m:
                    action = dict(action)
                    action["market"] = adv
    except Exception:
        V19_TELEMETRY["v19_errors"] = V19_TELEMETRY.get("v19_errors", 0) + 1
    return action
