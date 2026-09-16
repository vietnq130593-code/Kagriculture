# Kaggriculture: What the Top Farms Do — a Live Meta Guide

**A beginner-friendly guide to the Kaggriculture engine + a live tracker of what
top-ladder agents are actually doing, re-run daily on the official replay dataset.**

Two things in one notebook:
1. **Teach the mechanics that decide the game** — crop economics, yield curves,
   the price cliff, why everyone meters sales. (No ML background needed.)
2. **Track the meta** — infer the collective strategy (herd, crops, hiring, land,
   sell timing) from the top episodes, and slice the ladder any way you like.

> Data: official daily replays — [kaggriculture-episodes-index](https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-index)
> "ranked by average agent rating, capped at 20 GiB/day."
>
> Jump to the [§9 Summary](#summary) for the key takeaways and the daily workflow.

---

## 1. Setup

Every number in this notebook is computed from an **embedded copy of the
competition engine's market model** — `kaggle-environments` **1.32.x**, the
version the official replays record. Kaggle notebook images sometimes install a
newer build with different market math (the strawberry price cliff is **62
units** in 1.32.x but ~247 in other builds), which would silently corrupt every
teaching figure. Embedding the reference keeps the notebook correct and
reproducible everywhere — no pip installs, no restarts. The check at the bottom
just tells you whether the installed engine agrees.

---

## 2. What each crop pays (at base prices)

Profit per tile-day drives every planting decision. One-shot crops earn once;
ongoing crops earn repeatedly but slow. Here is the honest economics.

---

<details><summary><b>What this means</b></summary>

**Profit per tile-day = (units × base price − seed cost) / tile-days occupied.** This is the
foundation of every planting decision.

- **Melon** looks most profitable on paper ($250 base, highest profit/tile-day), but it is a
  *one-shot* crop and its price cliff is steep (see §4) — planting too many destroys the value.
- **Tomato** has a low base price but yields continuously: steady cash flow. **Strawberry**
  yields continuously at a high price — it is the main crop of the top meta (§6).
- **Wheat** has thin margins but two hidden values: it feeds animals, and its price
  essentially never crashes (3000 units before hitting the floor, §4).
</details>

---

## 3. Yield curves: fertilizer is not optional

For one-shot crops, watering in the bonus window adds yield; fertilizer doubles
that. Here is what that does to wheat vs melon day by day.

---

<details><summary><b>What this means</b></summary>

- **One-shot crops** (wheat / carrot / melon) gain +1 yield per watered day inside the
  bonus window; **fertilizer doubles that to +2/day**.
- **Wheat** cannot reach its 6-unit cap on watering alone — it **needs fertilizer**. So the
  seed's real value exceeds what the profit table shows.
- **Melon** reaches its 6-unit cap on watering alone by day 10; fertilizing melon is wasted
  — save the fertilizer for wheat.
- **Animals each produce 1 fertilizer per day** (a boolean, not a stockpile — uncollected
  dung is gone at day's end). That is the "raise animals, sell the fertilizer" free-money
  loop (§7 shows top games selling thousands of units).
</details>

---

## 4. The price cliff: why everyone meters sales

Premium goods (strawberry / milk / wool) crash from full price to the $1 floor
after ~100 units of oversupply. This is the single most important mechanic for
selling strategy. The shape of each curve comes straight from the engine.

---

<details><summary><b>What this means</b></summary>

**Overselling drives the price from the 10,000 baseline toward the $1 floor.** How fast
depends entirely on the product:

| Product | Units to hit the floor | Crash shape |
|---|---|---|
| Wool / Strawberry / Milk | **~60-80 units** | Most fragile — one big dump zeroes them |
| Melon | ~158 units | Resilient early, but cumulative oversupply still crashes it |
| Tomato / Carrot | ~500-850 units | Gentle |
| Wheat / Egg | ~3000 units | **Essentially never crash** (ballast) |

**The response**: **small, metered batches** (4-8 units per order), selling more while the
price holds. Dumping everything at once means the first units earn a high price and the rest
sit on the $1 floor — you crash your own revenue. That is exactly the top selling rhythm you
will see in §7.
</details>

---

### 4b. Watch a price dump happen (animation)

Selling premium goods into a glut pushes the price down a cliff *while you are
still selling*. This is why metered sales matter — the first units earn far more
than the last ones. The animation below sells strawberries one at a time.

---

<details><summary><b>What this means</b></summary>

The animation sells strawberries *one at a time* into a saturated market. Two things to watch:

1. **The price crashes while you sell** — the first units earn $100+, the last earn $1. The
   revenue curve (right panel) flattens: **the first 50 units earn more than the next 100**.
2. **The takeaway**: never dump everything at once. Sell in batches while the price holds
   high (before opponents flood the market) to lift your **average realized price**. This is
   the core of the whole selling strategy.
</details>

---

## 5. Live meta: pick your slice of the ladder

The daily dataset ships a `manifest.csv` with each episode's **mean Ladder rating**
(`avg_score`). Set `MIN_ELO` / `MAX_ELO` to analyze any band of the ladder.

> **What is this Elo?** It is the agents' **Ladder rating** (the Elo ladder that runs
> daily games), **not** the leaderboard score you submit for. The ladder has many more
> agents than the leaderboard's top ~20 rows — on 8/5 about 1,200+ agents were rated
> 2800+, while the leaderboard shows far fewer. You don't need your exact ladder rating:
> just pick the band you want to study.
>
> - `MIN_ELO = 2900` → pure top tier (small sample, sharpest)
> - `MIN_ELO = 2800` → strong band, good sample (default)
> - `MIN_ELO = 2600, MAX_ELO = 2799` → a mid/your-neighborhood band
> - `MIN_ELO = 2500, MAX_ELO = 2699` → "climbing players" — what separates them from top
> - `MIN_ELO = None, MAX_ELO = None` → the whole day
>
> The median ladder rating is printed after selection, so you can see where your chosen
> slice sits relative to the day.

---

<details><summary><b>How to read any slice of the ladder</b></summary>

The official daily dataset ships a `manifest.csv` recording each episode's **mean Ladder
rating (avg_score)** — not the leaderboard score. Pick episodes by band — no count cap:

```python
MIN_ELO = 2800     # only episodes with avg Elo >= 2800 (lowest score to keep)
MAX_ELO = None     # highest score to keep; None = no upper bound
```

- `MIN_ELO=2800` → a strong band with a large sample; `MIN_ELO=2600, MAX_ELO=2799` → a lower
  band (e.g. your ladder neighborhood); both `None` → the whole day.
- The cell above also prints the **score distribution** of the selected slice (count / min /
  median / mean / max + a histogram) so you know exactly which part of the ladder you are
  looking at.
- The cell above also prints the **score distribution** of the selected slice (count / min /
  median / mean / max + a histogram) so you know exactly which part of the ladder you are
  looking at.
- Data comes from the official daily dataset — **point at a new date and re-run to track the
  meta every day**.
</details>

---

## 6. The collective strategy (what top farms do)

Tally the final farm of every player in the selected band. This is the meta in
one screen.

---

<details><summary><b>What top farms look like</b></summary>

The **modal meta** is printed above the composition table (the `MODAL META` line) —
it is derived from *this* band's real data, so it updates every day you re-run
instead of going stale. The same farm keeps winning for a few *mechanical* reasons:

- **Animals pay more than crops.** Cows/sheep multiply output ~3-4x under daily CARE,
  and each animal drops **1 fertilizer/day** for free — farm animals are also the
  fertilizer business (§7).
- **Strawberry is the late-game earner.** It yields continuously at the highest
  sustainable price; a steady block of 6 keeps income high into day 30.
- **A little wheat for feed.** Cows eat wheat; growing some yourself keeps the herd
  profitable — hence the recurring **6 strawberry + 1 wheat** layout.
- **NE + SW, skip SE.** Land beyond the free NW tile costs 1k then 2k; the 4k SE tile
  almost never pays back in a 30-day game (≈0% of top players buy it).
- **12 hired hands** is the newest upgrade over the older 8-hand version.

> Because the modal farm is derived from data, it tracks the meta day to day — watch
> the `MODAL META` line move, and see §8 for how fast the ladder shifts.
</details>

---

## 7. Sell timing: the strategy behind the farm

Given the price cliff, selling is metered. Here is the actual rhythm of the
selected band — first sale day and average batch per product.

---

<details><summary><b>The selling rhythm</b></summary>

Sell characteristics of top episodes (current Elo band):

| Product | First day | Avg batch | Note |
|---|---|---|---|
| Wheat | day 0-5 | 7-8 | **Sold first** — feeds cows + cash flow |
| Melon | day 3-10 | 6-7 | Early capital; big sale around day 10 |
| Milk | day 8 | 8 | Steady once cows mature |
| Strawberry | day 11 | 8 | Main late-game earner |
| Wool | day 6 | 7 | Steady |
| Fertilizer | day 1 | 4-5 | **Free money**, sold daily |

**The pattern**: every product is sold in **small, steady batches, more while the price
holds**. Nothing is dumped in one go — that is the standard defense against the price cliff.
**The differentiation**: when everyone sells on this rhythm, **whoever acts first gets the
better price** — watch your opponent's maturation timing and sell before their big harvest.
</details>

---

## 8. The meta clock: how fast the bar moves

The official index records the average Elo of participants per day. This is the
most important number a competitor can watch — skip a week and you come back to
a different game.

---

<details><summary><b>Why you must track daily</b></summary>

The official index's `top_avg_score` / `median_avg_score` show the ladder evolving
explosively:

- **07-30 → 08-06**: median **670 → 2973** (4.4x in seven days); top **1152 → 3081**
- Pace: 08-04 → 08-05 +72/+135; 08-05 → 08-06 +59/+134 — the ladder keeps rising fast,
  and the meta keeps shifting (see §5-§7: top players moved to pure-animal farms on 8/6).

**Implication**: "yesterday's top strategy" can be mid-pack today. To stay relevant you need to:
1. **Pull the newest episodes daily** (re-run §5 on a fresh date)
2. **Watch your own rating neighborhood** (adjust `MIN_ELO` / `MAX_ELO`)
3. **Evolve with the meta** instead of clinging to one fixed "optimal farm"
</details>

---


<a id="hardcoded"></a>
## 8b. The meta is a fixed playbook — top players repeat it exactly

Digging into the **official daily dataset** (all episodes Elo 3000+) shows something
striking: **many of the highest-rated players execute the SAME per-step actions every
game**, no matter who they face.

### Verified: top players are hardcoded

For a player who appears in N+ games, I compared their **full per-step action trace**
(farmer move + hand actions + market orders + positions) across games:

| Player | Elo band | Full-trace identical across games |
|---|---|---|
| kakuteki | ~3136 | **3/3 games, 100% identical** |
| venks | ~3117 | **3/3 games, 100% identical** |
| Wufang Hong | ~3146 | **5/6 games, 100% identical** |
| Seb (allegedly) | ~3204 (LB #1) | ✗ 35-66% — *not* fixed (adapts execution) |

**What this means:** the current engine is stable and predictable enough that a
**fixed asset-development plan** (plant the same crops, buy the same animals, sell on
the same rhythm) achieves a very high win rate. The competitive edge is not
"re-planning every turn" — it is **executing a proven high-yield plan more completely,
faster, and with fewer errors** than the next player.

### The one exception: the leaderboard #1

**Seb (allegedly) is NOT a fixed trace.** His buy/sell *decisions* are consistent, but
his **farmer/hand execution adapts** to the observation (35-66% identical across games).
That adaptive layer is likely why he sits above the fixed-plan players — a fixed plan
wins against familiar opponents, but adaptation keeps you winning against **any**
strategy.

### What this means for you

1. **Copy the proven skeleton, not the position.** The exact per-step trace of a top
   player is fragile (any drift cascades). The *plan* — same crops, same animal count,
   same sell rhythm — is the robust part.
2. **The meta is a playbook.** Top farms converge because the engine rewards a stable
   optimum. Track *which* playbook is current via §5-§8, then execute it cleanly.
3. **The frontier is adaptation.** When balance changes arrive (see the discussion
   threads), fixed playbooks will crack and adaptive agents will rise. Keep an eye on
   who stops repeating themselves.


---

## 8.5 Daily Meta Report — 2026-08-11

*Data: 2026-08-11 matches · Elo band 3100–all*

### 1. Today's meta
- **Modal farm**: 9 cow + 4 sheep · 1 wheat · 10 hands · land NE+NW+SW — **30%** of players (296 players, 148 episodes).
- **Ending money**: median 84,151, max 154,941.
- **Slice**: 148 episodes, avg Elo [3100, 3187], median 3137 (avg of the two agents' ladder score per game — a *game-level strength tag*, NOT a per-player ranking or a win predictor).

**Top compositions:**
1. 1 wheat + 9 cow + 4 sheep + 10 hands, land NE+NW+SW — x89
2. 2 wheat + 9 cow + 5 sheep + 9 hands, land NE+NW+SW — x73
3. 9 cow + 1 sheep + 9 hands, land NE+NW+SW — x17
4. 7 wheat + 9 cow + 4 sheep + 10 hands, land NE+NW+SW — x16
5. 2 wheat + 7 cow + 4 sheep + 9 hands, land NE+NW+SW — x10

**Sell rhythm:** (first sell day / avg batch)
- Carrot       day 25 · batch 5.3 · 12 players
- Fertilizer   day  4 · batch 4.9 · 296 players
- Melon        day 10 · batch 7.7 · 296 players
- Milk         day 11 · batch 7.7 · 296 players
- Strawberry   day 15 · batch 15.4 · 296 players
- Wheat        day  8 · batch 11.6 · 296 players
- Wool         day  6 · batch 9.8 · 296 players

**Build order:** (median first-ORDER day)
- first land 6 · first hire 0 · first cow 0 · first sheep 0
- early seeds (days 0-4, avg/player): wheat 11.4, melon 6.3, strawberry 2.8, carrot 0.0
- cash curve (median on-hand cash, not net worth): d5=545, d10=2,172, d15=11,782, d20=36,414

**Winners vs losers:**
- final money: 85,501 (win) vs 81,412 (loss)
- early seeds (avg/player): win wheat 11.6, melon 6.7, strawberry 2.8 · loss wheat 11.2, melon 5.9, strawberry 2.9
- first-sell contrast: Strawberry 14→16 (win→loss)

### 2. Recent trend
Recent days (by match day = EPISODE_DATE):
| match-day | min-elo | score-med | money-med | modal-share | farm |
|---|---|---|---|---|---|
| 2026-08-07 | 3000 | 3029 | 109,071 | 25% | 8 cow + 6 sheep · 9 wheat · 10 hands · land NE+NW+SW |
| 2026-08-08 | 3100 | 3121 | 78,020 | 54% | 8 cow + 6 sheep · 4 wheat · 11 hands · land NE+NW+SW |
| 2026-08-09 | 3100 | 3131 | 77,737 | 26% | 8 cow + 6 sheep · 4 wheat · 11 hands · land NE+NW+SW |
| 2026-08-10 | 3100 | 3128 | 82,237 | 29% | 9 cow + 4 sheep · 1 wheat · 10 hands · land NE+NW+SW |
| 2026-08-11 | 3100 | 3137 | 84,151 | 30% | 9 cow + 4 sheep · 1 wheat · 10 hands · land NE+NW+SW |

*Note: rows use different `MIN_ELO`, so modal-share is NOT directly comparable across rows — higher min_elo = sharper top, lower share.*

*`min-elo` = band floor on the per-game `avg_score` (the ladder rating averaged over the two agents). It tags how strong the game's opponents are; it is NOT a win predictor and NOT a per-player ranking.*

Latest day deltas: consensus 29% → 30%; score-med 3128 → 3137 (+9); money-med 82,237 → 84,151 (+1,914).

### 3. Code area (today)
*Leaderboard snapshot pulled 2026-08-12 21:57 (live; may include later submissions)*
- **Leaderboard #1**: カワシギ @ 3179.7 (submitted 2026-08-11).
- Top 3: カワシギ (3179.7); researchstudio.site (3174.3); Kaito Fukami (3133.9).

**Engine balance watch:**
- [Balance Changes](https://www.kaggle.com/discussions/kaggriculture/733431) (votes 34) — engine may change; today's meta could become stale quickly.

**Recently updated (worth watching):**
- [raykkretzschmar/kaggriculture-rank-your-agent](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent) (votes 61, **new 8/12**) — agent 排名工具
- [boatlee/v16-rc5-high-score-8c-4s-premium-market-lead](https://www.kaggle.com/code/boatlee/v16-rc5-high-score-8c-4s-premium-market-lead) (votes 2, **new 8/12**) — **8c-4s 路线 + premium market lead**（和今天 meta 的 9c4s 呼应）
- [boatlee/v16-rc5-r5a-high-score-8c-4s-recovery](https://www.kaggle.com/code/boatlee/v16-rc5-r5a-high-score-8c-4s-recovery) (votes 0, **new 8/12**) — 同路线的 recovery 变体
- [georgymamarin/kaggriculture-daily-replays-the-live-meta-report](https://www.kaggle.com/code/georgymamarin/kaggriculture-daily-replays-the-live-meta-report) (votes 12, **new 8/11**) — 竞品 meta 报告
- [jeffmarcecadet/reverse-engineering-rank-5-thunder-thunder](https://www.kaggle.com/code/jeffmarcecadet/reverse-engineering-rank-5-thunder-thunder) (votes 8, **new 8/12**) — 逆向 THUNDER THUNDER
- [tetsutani/adaptive-farming-strategy-for-kaggriculture](https://www.kaggle.com/code/tetsutani/adaptive-farming-strategy-for-kaggriculture) (votes 104, **8/12 run**)

**Current hot notebooks (top votes):**
- [bovard/kaggriculture-getting-started](https://www.kaggle.com/code/bovard/kaggriculture-getting-started) (votes 540)
- [kaitofukami/25-27-strict-future-v27-midgame-meta-reset](https://www.kaggle.com/code/kaitofukami/25-27-strict-future-v27-midgame-meta-reset) (votes 150)
- [romantamrazov/kaggriculture-hamburger](https://www.kaggle.com/code/romantamrazov/kaggriculture-hamburger) (votes 126)
- [tetsutani/adaptive-farming-strategy-for-kaggriculture](https://www.kaggle.com/code/tetsutani/adaptive-farming-strategy-for-kaggriculture) (votes 104)
- [kaitofukami/177-180-fresh-top-30-v21-1-conditional-memory](https://www.kaggle.com/code/kaitofukami/177-180-fresh-top-30-v21-1-conditional-memory) (votes 89)

**Recent discussion topics:**
- [Balance Changes](https://www.kaggle.com/discussions/kaggriculture/733431) (votes 34)
- [Comment on the final evaluation for this competition](https://www.kaggle.com/discussions/kaggriculture/731587) (votes 16)
- [Daily Top Episodes Dataset](https://www.kaggle.com/discussions/kaggriculture/731215) (votes 24)
- [How to get started + Competition's Official Discord](https://www.kaggle.com/discussions/kaggriculture/730708) (votes 8)
- [Match outcome contradicts stated win condition (higher coin total reco](https://www.kaggle.com/discussions/kaggriculture/734684) (votes 2)

### 4. Takeaway

**9c4s 新共识稳固，分化后的收敛正在形成**

1. **Modal 连续两天相同**：9c4s-1w-10h，share 29%→**30%**。8c6s（8-8 的 54% 共识）已彻底被替代。meta 分化后正在形成新的收敛。
2. **双极仍在**：9c4s（89）vs 9c5s（73），差距扩大 13→16。另有 9c1s（17）、9c4s-7w（16）—— **sheep 数量成主要分化轴**。
3. **草莓节奏仍在进化**：首卖 d15，batch 15.4（三天前 9.9→14.1→15.4，持续放大）。赢家 d14 先卖 vs 输家 d16（赢家早 2 天，比昨天的 1 天差距更大）。**草莓规模化后，先卖优势在扩大**。
4. **甜瓜回补**：early 甜瓜 4.9→6.3（+29%）。9 牛 + 甜瓜 + 草莓的组合正在成型。
5. **利润再涨 +1,914**（$84,151），连续第三天上涨 —— 新配方组的收益在稳定爬升。
6. **Code 区呼应 meta**：boatlee 发布 **v16-rc5 "8c-4s" 系列**（premium-market-lead / recovery）—— 顶尖玩家已切换到 8-4s 牛羊路线并加 premium 市场领先；georgymamarin 发布了**竞品 live-meta 报告**（我们的差异化被复制了）。

**策略含义**：8-10/8-11 的 **9c4s-1w** 和 **9c5s-2w** 就是当前最强配方。必须用这两条路线刷新 trace（boatlee 的 8c-4s 说明连顶部的 composition 都在快速迭代）。旧 8c6s trace 已完全过时。

---

<a id="summary"></a>
## 9. Summary

### Key takeaways

1. **The meta is converged but still evolving.** Top farms are ~**8 cows + 5-6 sheep +
   6-7 strawberry, NE+SW land**. But the newest top tier has upgraded to **12 hands +
   6 strawberry + 1 wheat-for-feed**, vs the older 8-hand / 7-strawberry version.
   **Tracking the latest episodes matters.**
2. **Selling is metered.** Premium price curves are cliffs, so top players sell in
   **small batches (avg 4-8 units/order)** and **more while the price holds**.
3. **Fertilizer is free money.** The engine accepts `SELL FERTILIZER`, animals produce it
   daily — raising animals and selling the fertilizer is steady cash flow.
4. **Differentiation is in timing.** When everyone plays the same farm, **whoever sells into
   the shared market first gets the better price**. Watch your opponent's maturation rhythm
   and **sell before their big harvest**.

### Analyze any band of the ladder

Set the config at the top of §5 (`avg_score` = Ladder rating, not leaderboard):
```python
MIN_ELO = 2800    # only episodes with avg Elo >= 2800
MAX_ELO = None    # None = no upper bound
```
- `MIN_ELO=2800` → a strong band with a large sample; `MIN_ELO=2600, MAX_ELO=2799` → a lower
  band (e.g. your ladder neighborhood).
- Data comes from the **official daily dataset** — point at a fresh date and re-run to
  **track the meta every day**.

### Daily workflow
1. Point at the newest dataset. 2. Pick your Elo band. 3. Read the collective strategy /
   sell rhythm. 4. Differentiate against it.
