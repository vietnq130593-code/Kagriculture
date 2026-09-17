########## CELL [0] markdown ##########
# Kaggriculture: V44 + Four Market Layers

## TL;DR

- **Live, V44 + layers 1, 2, 4** (submission 56277542): **2801 rating, rank about 188 of 9246 teams** on 16 Sep 2026 (a snapshot; ratings keep moving). It went **26-3** in its first 29 live games, and the three losses were by 1, 348 and 663 coins. Plain V44, submitted by us, plateaued around 2630-2657.
- **Live, all four layers** (submission 56280605): **22-2** in its first 24 live games, with mean final money of **115.9k vs 86.3k**. Its rating is still climbing (2389 after 4 hours), so it has not settled yet.
- **Local, exact engine dynamics, both seats per seed:** the four-layer build beats plain V44 **10-0** on two 5-seed sets (+4329 and +1607 mean margin) and pipe-5 **10-0** (+3737).
- **Live-opponent tapes:** we replayed the opponents' recorded actions from the three-layer build's 29 newest live games (3 open with BUY 70 / SELL 70 wheat on turn 1). An exact replay of the live three-layer file reproduces all 29 results to the coin (26-3). On the same tapes the four-layer build goes **27-2** (+6451 mean margin) and plain V44 goes 24-5 (+5415).
- **Caveat:** locally, the four-layer and three-layer builds are about equal (5-5 at +31, 7-3 at +14). The `USE_CADENCE` flag picks one. Local and tape results are filters, not guarantees of live results.
- **What this is:** the public V44 agent (V43 chassis lineage), unchanged, plus four small wrapper layers appended to the end of the file. Three change when and in what order stock is sold; one changes which animals to buy when a yarn store is open. The notebook builds the four-layer file by default; set `USE_CADENCE = False` for the three-layer file behind the 2801 rating.

## What this is

This notebook is a derivative of the public **V44** agent from this competition (V43 chassis lineage). The V44 file is included unchanged, and four small wrapper layers are added to the end of it. Each layer takes the previous entry point as its host (the last callable in the file), adjusts the host's action and falls back to the host's action if anything goes wrong. Everything that farms and plans comes from V44; the layers only adjust its orders. Three layers change when and in what order stock is sold, and one changes which animals to buy on seeds with a yarn store.

## The four layers at a glance

| # | Layer | What it does | When it acts |
|---|---|---|---|
| 1 | Preguard | Sells at hours 21-22 the stock that V44's own hour-23 storage guard would dump, so it sells one or two steps before a same-code rival | Hours 21-22, when the shed is about to overflow (6-unit margin) |
| 2 | Lockstep | Replays the engine's unit-by-unit market resolution to pick the best SELL order against an assumed exact copy of its own orders, and raises V44's race horizon for clone opponents from 8 to 9 | Only when V44's clone detector fires |
| 3 | Cadence | Holds back a few units just before a town consumption tick and sells them right after it | Steps just before a tick, from day 4 |
| 4 | Yarn herd | Buys sheep instead of cows and geese when YARN_STORE is unlocked | Animal purchases on days 8-11; otherwise it makes exactly V44's moves |

## Results

In all local tests each seed is played twice, once from each seat. "Margin" is our final money minus the opponent's, averaged per game.

**Live leaderboard**

| Build | Submission | Live record | Notes |
|---|---|---|---|
| V44 + layers 1, 2, 4 (three-layer) | 56277542 | 26-3 in first 29 games | 2801 rating, rank about 188 / 9246 (16 Sep 2026 snapshot); losses by 1, 348, 663 coins |
| V44 + layers 1, 2, 3, 4 (four-layer) | 56280605 | 22-2 in first 24 games | Mean final money 115.9k vs 86.3k; 2389 after 4 hours and still climbing |
| Plain V44 (our earlier submission) | - | - | Plateaued around 2630-2657 |

**Local, exact dynamics**

| Matchup | Seeds | W-L | Mean margin |
|---|---|---|---|
| Four-layer vs V44 | 47001-47005 | 10-0 | +4329 |
| Four-layer vs V44 | 46001-46005 | 10-0 | +1607 |
| Four-layer vs pipe-5 | 47001-47005 | 10-0 | +3737 |
| Three-layer vs V44 | 46001-46010 | 20-0 | +1902 |
| Three-layer vs pipe-5 | 5 seeds | 10-0 | +2105 |
| Three-layer vs pipe-4 | 5 seeds | 10-0 | +2060 |
| Three-layer vs Farming Score V5 | 5 seeds | 10-0 | +2646 |
| Four-layer vs three-layer | 5 seeds | 5-5 | +31 |
| Four-layer vs three-layer | 5 seeds | 7-3 | +14 |

Plain V44 also beats pipe-4 and pipe-5 locally, so the margins against them are build-vs-agent margins, not the layers' own gain.

Official `kaggle_environments` runner, four-layer vs V44, seed 46001: **95634 vs 93549** in each seat. The slowest single agent call took 197 ms, and the mean was 1.4 ms.

**Live-opponent tape testbed** (opponents' recorded actions from our live replays, replayed exactly with the same seed and seat)

| Tape set | Plain V44 | Three-layer | Four-layer |
|---|---|---|---|
| 62 tapes, older live games | 61-1 (+9953) | 61-1 (+10827) | 61-1 (+10694) |
| 29 tapes, newest live games (incl. BUY 70 / SELL 70 openers) | 24-5 (+5415) | 26-3 (+6399) | 27-2 (+6451) |

## About the base

- **V44 is a public agent from this competition**, built on the V43 chassis lineage. The planning, farming and trading all come from V44, including the race logic, clone detection and day-end storage guard that our layers hook into.
- **pipe-4 and pipe-5** are related public agents from the same family. We used them as test opponents, along with Farming Score V5.
- **This notebook is a derivative work.** The V44 source is embedded byte-for-byte (sha256 prefix `797d9bca`, original line endings kept), including its Apache-2.0 license text and attribution notices. Our contribution is the four added layers and the testing described below.

## How to use

1. Set `USE_CADENCE` at the top of the **Build the submission** cell (`True` = four-layer, the default; `False` = three-layer).
2. **Save Version -> Save & Run All.** The notebook writes `/kaggle/working/main.py` and `/kaggle/working/submission.tar.gz`.
3. Submit `submission.tar.gz` (or `main.py`) from the notebook's Output, or download it and upload it on the competition's Submit page. The Output also lists the `build/*.py` parts; those are not submissions.
4. The build cell asserts the full sha256 of `main.py`, so a clean run means you have exactly the file we run live. If you edit a layer, the assert fails by design: set `VERIFY_LIVE_SHA = False` (or update `EXPECTED_SHA256`).

The agent is the **last callable** in `main.py`. If you add code, put it at the end and keep your agent function last.

########## CELL [1] markdown ##########
## How we evaluate

Given a seed and both players' actions, a Kaggriculture game always plays out the same way. We build two test tools on that fact, and we lean on mirror games as the main filter.

### 1. Exact-dynamics fast simulator

On every step, the official `kaggle_environments` runner deep-copies the state, validates observations and actions against the schema, and records history. For testing we call the `kaggriculture` interpreter directly and skip that overhead:

- The interpreter is the same, so market, town and end-of-day code, and therefore the game dynamics, are exact.
- It gives **identical final money** to the official runner.
- It is **much faster**, which makes it cheap to test each idea on many seeds.

Every candidate goes through the same protocol:

- Each seed is played twice, once from each seat.
- Results are confirmed on fresh seed ranges that were not used for tuning.
- Opponents are plain V44 (the mirror), near-copies with different settings (pipe-4, pipe-5) and other public agents (Farming Score V5).
- Before shipping, we package `main.py` and load it with Kaggle's file loader, which confirms the last callable is the wrapper. Then we run it in the official runner and record per-call timing.

### 2. Live-opponent tape testbed

Local tests are limited to the public agents you have, and the ladder has opponents you do not have. So we bring their moves home:

1. Download the replays of our own live games.
2. From each replay, extract the opponent's action at every step (its "tape").
3. Wrap the tape in a replay agent that returns the recorded action for the current step, unchanged, with no end-of-game overrides.
4. Play the candidate against the tape with the same seed and seat as the live game.

**Sanity check:** replaying the live three-layer file against the tapes of its own 29 newest games reproduces both players' final money to the coin in all 29 (26-3, the live record). An earlier replay agent that sold the opponent's whole shed at step 718 cost the opponent up to about 3000 coins per game (median 382) and turned all three live losses into tape wins, so exact replay matters.

For each candidate we report the win-loss record, the mean margin, **losses converted** (tapes the baseline lost and the candidate wins) and **wins kept** (tapes the baseline won and the candidate still wins). A change that converts losses but gives up wins is rejected.

**Limitation:** a tape does not react to us. If the candidate moves the market, the opponent still sends its recorded orders, and they now fill at different prices or fail. Tapes are a strong filter against real opponent behavior, but they do not replace live games.

### 3. Why mirror games against V44 are decisive

V44 against itself makes the same decisions in the same situations, and on most seeds the game ends in an **exact tie**. That makes the mirror a zero-noise test:

- Any change shows up at once as a non-zero margin, and the sign means something even when the gain is small. Layer 3 gains only +30 to +70 per game, yet it went 64-2 over 66 mirror games.
- Regressions cannot hide behind variance.
- It is a frequent matchup on the ladder (see the next section).

The risk is overfitting to an exact copy. Every mirror gain is re-checked on fresh seeds, against pipe-4 and pipe-5, and on live tapes.

### 4. Why clone-vs-clone games matter

V43 and then V44 were public, strong, single-file agents, and pipe-4 and pipe-5 come from the same family. When plain V44 plays the exact tapes of our live opponents, its own clone detector fires in 24 of the 29 newest games and 34 of the 62 older ones, so clone-vs-clone games are common on the ladder.

When two clones meet, their farming is nearly identical, so the market decides the game. The engine resolves both players' market orders **slot by slot and unit by unit**. For order slot *i*, both players get a price for their next unit from the same market inventory, both sales go through, and the price moves after every unit. This has three consequences:

- When two clones sell the same product in the same slot on the same turn, they share the price drop evenly.
- A player who sells a contested product one step earlier, or in an earlier slot than the rival, gets the undepressed price and leaves the lower price to the rival.
- Town shops remove units every 4 steps and the town center every 24, so timing relative to those ticks matters.

Layers 1-3 target exactly these same-turn collisions. Layer 4 changes a herd choice that clones do not change. This also helps explain why plain V44 plateaued: against copies of itself, it has no edge.

########## CELL [2] markdown ##########
## V44 base

The base is the public V44 agent from this competition (V43 chassis lineage), used unchanged. Its exact `main.py` (327,314 bytes) is embedded in the next cell as a gzip + base64 blob. The cell decodes it, asserts the full sha256

`797d9bca309d481e18cdbb675ce6d6de9967d266cbafb4c2352c68fb10264e2f`

and writes the bytes to `build/v44_base.py`. The file keeps its own Apache-2.0 license text and attribution notices; our changes are only the layers appended after it.

The cell also switches to `/kaggle/working` (or to the current directory outside Kaggle), so the `%%writefile` cells below write into `build/`.

########## CELL [4] markdown ##########
## Layer 1 - Preguard sells at hours 21-22

**What V44 does.** When hour 23 ends, the engine drops every unit's carried items into the shed and destroys anything above the 100-item cap. V44 guards against this with a day-end storage guard (EXP-154). At hour 23, if shed plus carried items exceed 99, it sells the excess, highest price first. V43/V44-lineage rivals (pipe-4, pipe-5) run the same guard, so they often dump the same lots on the same step.

**What the layer changes.** On hours 21 and 22 of days 1-28, it projects that overflow using V44's own helpers: `_r127_fields` applies this step's unit actions and `_r97_market_stock` applies the orders already queued. Day 29 is left to V44's terminal planner. In the guard's price order, the layer then adds SELLs for MILK, STRAWBERRY, MELON, WOOL and TOMATO, skipping any priced below 2. The hour-23 guard stays in place as a backstop.

**Why it gains.** Within a step, the market runs before town consumption.

| Hour | Consumption after the market | Seller |
|---|---|---|
| 20 | shops | |
| 21, 22 | none | this layer |
| 23 | none, then end-of-day drop | V44 guard |
| 0 | shops + town center | |

No consumption runs between the hour-20 and hour-0 markets, so a passive market pays the same price at hours 21, 22 and 23. The market is lockstep: both players quote each unit at the same inventory, and each sale adds to supply and pushes the price down. Whoever sells first gets the top of the price curve, and a rival's hour-23 dump starts lower.

**Margin 6.** The projection can't see later harvests or deposits, so the layer sells 6 units past it (`_Y_MARGIN=-6`: target 93, not 99). That usually leaves the guard nothing to dump. Six was the best buffer we tried.

**Evidence (layer alone on V44, fresh seeds).** 38-2 against plain V44 (both losses by 6 coins), mean margins +562 to +834. Against pipe-5: +1400 to +2423 mean margin (plain V44 also beats pipe-5 on those seeds, so only part of that is the layer).

**Limitations.** This is a race edge. The gain is small against opponents that don't dump at hour 23, and the buffer can sell a few units early. Products outside the list count toward the overflow but are never pre-sold, so the guard sells them.

This block is appended right after V44's source. It takes the previous last callable as its host and adds nothing but SELL orders to that host's market list.

########## CELL [6] markdown ##########
## Layer 2 - Lockstep SELL ordering and clone horizon 9

**How the engine clears the market.** After unit actions, `_process_market` walks both order lists slot by slot. Inside a slot, SELL and BUY_PRODUCT run in lockstep, one unit at a time: both players are quoted at the same pre-commit inventory, then both commit, and each SELL unit priced above $1 adds one unit of inventory, lowering the next quote. Within a slot nobody is first.

**Why clones collide.** Two V44 copies (or a rival running the same public route tape) emit identical market lists, so they sell the same product in the same slot and split every dump unit by unit. The only lever is slot order: if my glutted product sits where the clone still sells something else, I take the pre-dump prices and its copy lands on the inventory I raised. V44's R37 sort only reorders SELL runs of distinct products.

**What the layer changes.** From step 216, when V44's own race detector flags a clone this turn (farmer and hand positions equal to the rival's on at least 4 of the last 6 turns, plus at least 95% matching occupied tiles; from step 696, the stored history plus a fresh tile check), each contiguous run of 2-6 SELL orders is permuted. Every distinct permutation is replayed through a copy of the engine lockstep against the clone's assumed list (the host's unmodified list and the same projected shed, i.e. an exact copy of us), keeping the order that maximizes own revenue minus clone revenue. The original order scores exactly 0, so only a positive edge changes anything. Quantities never change.

**Horizon 8 -> 9.** In clone mode V44 pre-sells shed stock its tape plans to sell within 8 turns, and it escalates to 24 after it detects a lost race; we keep that. At 9 we sell one turn before a horizon-8 clone.

| Variant vs plain V44 | Result |
|---|---|
| reorder + horizon 9 | 20-0, +1436 (seeds 46001-46010) |
| reorder only | 19-1, +529 |
| horizon 12 only | lost a seed by 2719 |
| horizon 24 | too aggressive |

**Limits.** It assumes an exact clone, so a gated rival with different lists may not yield the edge. The replay ignores cash and shed caps on BUY_PRODUCT. A 6-order block means 720 replays; the full agent peaked at 197 ms.

Appended after Layer 1: `_V44Y_HOST` captures the previous last callable (`agent_v44y_preguard`), the module-level `_RACE_HORIZON_CLONE = 9` overrides V44's 8, and `v44y_lockstep_agent` becomes the new entry point.

########## CELL [8] markdown ##########
## Layer 3 - Cadence (sell timing around town ticks)

**Engine timing.** Each step the market clears first, then the town consumes: when `step % 4 == 0` every unlocked shop removes 1 unit per product (2 for single-product shops), plus 1 of everything every 24 steps. Orders are paired by list index across both players and filled one unit at a time at a shared quote.

**What V44 does.** V44 (V43 chassis) replays a route tape and wins the same-turn sale race by selling planned lots as soon as the stock exists.

**What this layer changes.** At phases `step % 4` in {0, 2, 3} (steps 96-716, not hour 23) it trims `floor(n/2)` units from a host SELL of CARROT, TOMATO, STRAWBERRY, MELON, MILK or WOOL, where `n` is that item's relief at the next tick. Held units are appended as a separate SELL after the host's orders at the first post-tick step (phase 1) where the host is not selling that item; after 3 steps, on shed pressure, or from step 717 they go out regardless. No deferral when the route tape sells that item within 8 steps, when shed room is short (DROP overflow is destroyed), or when this step's purchases plus 300 would not stay funded (money must also be at least 1000).

**Why it gains and naive versions lose.** Against a clone, with price drop `s` per unit sold:

| Change | Margin vs clone |
|---|---|
| Hold `d` units across a tick, sell alone | `+s·d(n-d)`, best near `n/2` |
| Split a lot, no tick between | `-s·d²` |
| Delay a whole lot `q > n` | `s·q(n-q) < 0` |
| Release where the clone sells `q_s` too | extra `-2s·q_s·d` |

`n` is a few units, so the edge is small but nearly always positive.

**Evidence.** Layer 3 alone vs plain V44: 64-2 over 66 mirror games, +30 to +70 per game; splits and whole-lot delays lost.

**Limitations.** A tie-breaker for clone-heavy lobbies, not a money engine. On top of layers 1, 2, 4 it is practically neutral: four-layer vs three-layer 5-5 (+31) and 7-3 (+14); on the older 62 tapes both go 61-1 (+10694 vs +10827), and on the newest 29 it goes 27-2 vs 26-3. Errors or a non-standard config return the host action unchanged.

Below is the exact Layer 3 block, appended after Layer 2. It captures the previous entry as `_CD_HOST`, and its last function, `_v44y_sell_cadence_agent`, becomes the new agent.

########## CELL [10] markdown ##########
## Layer 4 - Yarn herd (shop-aware herd)

**Shop demand model.** A town shop is drawn on days 3, 6, ... 24 (8 draws, with replacement). Every 4 steps each shop instance removes one unit of each product it lists from the shared market; single-product shops (`YARN_STORE`, `PET_CAFE`) remove two. One yarn store drains 12 wool per day, a milk shop only 6 milk. Otherwise only the town center buys wool, 1 per day. Wool rises only slowly on scarcity (log shape: about $240, +20% over its $200 base, after a 105-unit shortage) but collapses on glut (`sq` shape: about 59 surplus units reach the $1 floor). A sheep costs more than a cow (500 vs 400) and yields less often (every 3 days vs 2), so sheep usually lose to cows unless a yarn store absorbs the wool.

**What V44 does.** At step 144 it picks a route from the first two shops: a yarn store there selects the sheep-heavy V39 tape, otherwise an EXP240 tape buys geese (and on some routes a cow) on days 8-11. V44 has the mirror rule (day-9 sheep to cow with 2+ milk shops and no yarn store), but nothing for a yarn store drawn third on day 9.

**What the layer changes** (days 8-11, `YARN_STORE` unlocked):
1. `BUY_ANIMAL COW/GOOSE` (qty 1-2) becomes `SHEEP` if estimated cash after all orders stays at 100 or more.
2. Sheep confirmed in the shed are credited; the tape's `PICKUP`/`PLACE` are rewritten to sheep, `BUILD_COOP` to `BUILD_PASTURE`.
3. Wool harvested at swapped sites is added to the tape's existing `SELL WOOL` orders. No new orders are created, so the order slots stay aligned with a V44 clone's list.

**Evidence.** On yarn-store seeds: 18-0 (+3770 mean) vs V44. When no swap happens, its output was action-identical to its host in our tests. Layer 4 is in both live builds, so the three-layer vs four-layer comparison says nothing about it.

**Limitations.** Fires only when a yarn store is open at the day 8-11 purchases (in practice when it is the third shop; a yarn store among the first two already routes V44 to its sheep-heavy tape). Extra wool also lowers the shared wool price, so with one yarn store margins can be thin, and an opponent selling no wool avoids that cost. After a goose swap, later coops are built as pastures (harmless for V44, which buys all its animals by day 11).

Layer 4 is appended last (after Layer 3, or after Layer 2 in the three-layer build). It takes the previous entry as `_Y_HOST` and passes the host's action through unchanged unless a yarn store is open at the day 8-11 animal purchases. On any exception it returns the host's action.

########## CELL [12] markdown ##########
## Build the submission

Set `USE_CADENCE` at the top of the next cell, then run it. The cell joins the V44 base and the layers in order (layer 1, layer 2, layer 3 only when `USE_CADENCE = True`, layer 4, then any `EXTRA_LAYERS`) into `main.py`, packs `submission.tar.gz` with `main.py` at the archive root, and loads `main.py` the way Kaggle's loader does (exec the file, take the last callable) to print the entry point.

The live file mixes CRLF and LF line endings between blocks, and `%%writefile` does not preserve them, so the cell restores each layer's original newlines before joining. The sha256 assert proves the result is byte-for-byte the live submission.

For your own builds, `EXTRA_LAYERS = ['my_layer']` appends `build/my_layer.py` after layer 4, and `VERIFY_LIVE_SHA = False` lets a build with an edited layer through. The live sha256 is asserted only for the default layers with `VERIFY_LIVE_SHA = True`; in every case the cell prints the sha256 and writes `main.py` and `submission.tar.gz`.

| `USE_CADENCE` | Build | Live submission | sha256 of `main.py` |
|---|---|---|---|
| `True` | V44 + layers 1, 2, 3, 4 | 56280605 | `fa9e47d81de50208...` |
| `False` | V44 + layers 1, 2, 4 | 56277542 | `016b9a32248f3447...` |

########## CELL [14] markdown ##########
## What did not work

- **Daily hire caps.** Capping V44's HIRE orders per day lost clearly. Cap 10 went 0-6 (-9883 mean margin) and cap 11 went 2-4 (-533). The extra hand earns about 500-1000 coins per day, while its Fibonacci hire cost is at most 377, so capping V44's hiring only loses money.
- **pipe-5 settings on V44.** Porting pipe-5's `clamp_sells` / `dead_stock` settings onto V44 went 2-4.
- **Another turn-1 opening on V44.** The turn-1 opening of a top leaderboard cluster (called C9 in a public analysis notebook) changed the result by +1 coin, so no real effect.
- **Our old wheat-pump trick.** It won by +60-70k locally against clones of tt95, an earlier public agent family, then collapsed to a 1622 rating live once the meta moved. Lesson: local wins against yesterday's agents mean little. Always test against the newest public agents and fresh live tapes.

########## CELL [15] markdown ##########
## Next steps

These are the open ideas we see, roughly in order of value:

- **The turn-1 BUY 70 / SELL 70 wheat opener.** Some newer opponents buy and sell 70 wheat on turn 1. Two of the three-layer build's three live losses (by 1 and 663 coins) came against this opener, and the four-layer build still loses the exact tape of the 663-coin game. Understanding where the opener gains, and answering it in the first day's market, is the most obvious next layer.
- **Shop-aware herds beyond the yarn store.** Layer 4 only acts when YARN_STORE is unlocked at the day 8-11 purchase points. Other shop mixes may also call for a different herd.
- **The last-day dumps.** Some same-step endgame sells between clones are still contested. Moving them likely needs changes inside V44's terminal planner, not another market wrapper.
- **Reactive tapes.** A tape opponent that switches to V44 once its recorded actions stop making sense would make the testbed closer to live play.

## Fork it

The layers are built to stack. To add your own:

```python
# Capture the current entry point BEFORE defining any function or class.
_MY_HOST = [v for v in list(globals().values()) if callable(v)][-1]

def my_layer_agent(observation, configuration=None):
    action = _MY_HOST(observation, configuration)
    try:
        return adjust(observation, action)   # your change
    except Exception:
        return action                        # fall back to the host's action
```

Put `adjust` and any other helpers between the capture and the agent, and keep your agent function the last callable in the file.

To build it in this notebook, add a cell above **Build the submission** that starts with `%%writefile build/my_layer.py`, then set `EXTRA_LAYERS = ['my_layer']` in the build cell. Extra layers are appended after layer 4 in list order, and the build skips the live sha256 check for them.

Before you trust a layer, test it in the V44 mirror from both seats, then against pipe-4 and pipe-5, then on fresh live tapes. If you beat this build, publish it and post a link in the comments.

If this notebook helped you, please upvote it.

