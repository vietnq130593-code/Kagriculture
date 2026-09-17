# Beyond V43: What the Top 0.5% Do on Turn 1

**TL;DR**: Fork this, submit, get a top agent. But if you want to learn *how cluster analysis found a turn-1 optimization that beats V43 81% of the time*, keep reading.

I built a strategy-clustering pipeline that fingerprints the top 50 leaderboard teams, groups them by behavioral similarity, and traces exactly what the top clusters do differently. The answer was surprisingly simple: **most agents waste money on turn 1**.

This notebook explains:
1. How Union-Find clustering reveals the strategy landscape
2. What Cluster C9 (top 0.5%) does differently on turn 1
3. Why this one change improves Ahmed's V43 from 75% → 96% vs V42
4. Full colosseum results: 200-game H2H against 5 agents

The agent is self-contained — no datasets, no internet, no GPU. Run all cells to build `submission.tar.gz`.

---

---

## The Strategy Landscape: 33 Clusters from 263 Teams

Most Kaggle agents in this competition are variations of the same idea. How do you find the ones that aren't?

I built a **strategy fingerprinting system** that:
1. Downloads replay episodes from the top 50 LB teams
2. Extracts the first 144 actions from each game as a "fingerprint"
3. Clusters teams using Union-Find at 90% similarity threshold

The result: **263 teams collapse into 33 distinct strategy clusters**.

| Cluster | Size | Avg Elo | Representative | Similarity to Us |
|---|---|---|---|---|
| C0 | 1 | 3215 | Majkel1337 (#1) | 40% |
| C1 | 1 | 3024 | ymg_aq | 50% |
| C2 | 1 | 3008 | SpaTaro | 42% |
| C4 | 1 | 2991 | Otter Vibe | 54% |
| **C9** | **5** | **2931** | **AI是我的豆包** | **84%** |
| C15 | 212 | 2881 | (v40 megacluster) | 100% |

**81% of the top 50 teams are in Cluster C15** — they all play essentially the same strategy (Ahmed's v40 lineage). The top 8 clusters are all singletons with unique strategies.

But Cluster C9 is interesting: **5 teams, 84% similar to us, but consistently winning**. That 16% difference is where the edge lives.

---

---

## The Discovery: What C9 Does on Turn 1

I ran a **mechanism tracer** on 58 games where C9 beat C15 agents. It traces through each game step-by-step, finds the first point where actions diverge, and classifies what changed.

The #1 mechanism by count: **the opening market sequence**.

### What V40–V43 (Cluster C15) does on turn 1:
```
Step 0 market: [BUY_PRODUCT WHEAT 5, BUY_PRODUCT WHEAT 10, SELL WHEAT 60]
```
This is the "wheat flip" — buy 15 wheat for cheap, immediately sell 60 for profit. It generates ~$900 bridge cash.

### What C9 does on turn 1:
```
Step 0 market: [BUY_PRODUCT WHEAT 5]
Step 1 market: [HIRE, HIRE, HIRE, HIRE, HIRE, BUY_ANIMAL COW 2, BUY_ANIMAL SHEEP 2]
```
No flip. Just buy 5 wheat (minimum for planting), then immediately hire workers and buy animals.

### Why this works:
The wheat flip costs **tempo**. You spend 3 market order slots on a trade that nets ~$900, but you delay hiring workers and buying animals by one full turn. In a 720-step game where compound returns dominate, **starting production 1 turn earlier** is worth more than $900 in bridge cash.

**But there's a catch**: routes that include a BAKERY shop *need* the wheat trade because bread production depends on having wheat inventory. So the fix is conditional:
- **BAKERY routes**: Keep the original wheat flip (11 specific route IDs)
- **All other routes**: Minimal wheat + early hiring

---

---

## The Implementation: pipe-4

pipe-4 = Ahmed's V43 base + C9 conditional opening.

V43 itself is a strong upgrade over V42, adding three new reactive layers:
1. **Shed overflow recovery** — sells cargo at hour 23 that would otherwise be destroyed at dawn when the shed overflows (the "Recovering Lost Harvests" mechanism)
2. **Atomic planting fix** — prevents the engine from canceling ALL planting when seeds are insufficient for all commands
3. **Route proposal planner** — optimized endgame worker routing

These V43 improvements are orthogonal to the C9 opening — they stack cleanly.

### The exact change

Replace the uniform wheat flip:
```python
_R42_OPENING = [['BUY_PRODUCT', 'WHEAT', 5], ['BUY_PRODUCT', 'WHEAT', 10], ['SELL', 'WHEAT', 60]]
for _r42_tape in _ROUTES.values():
    _r42_tape[0] = dict(_r42_tape[0], market=[list(o) for o in _R42_OPENING])
```

With a conditional opening:
```python
_PIPE3_BAKERY_ROUTES = {101, 103, 104, 105, 106, 107, 108, 109, 111, 119, 120}
_PIPE3_MINIMAL = [['BUY_PRODUCT', 'WHEAT', 5]]
_PIPE3_WHEAT = [['BUY_PRODUCT', 'WHEAT', 5], ['BUY_PRODUCT', 'WHEAT', 10], ['SELL', 'WHEAT', 60]]
_PIPE3_STEP2_MIN = [['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['HIRE'], ['BUY_ANIMAL', 'COW', 2], ['BUY_ANIMAL', 'SHEEP', 2]]
for _p3_rid, _p3_tape in _ROUTES.items():
    if _p3_rid in _PIPE3_BAKERY_ROUTES:
        _p3_tape[0] = dict(_p3_tape[0], market=[list(o) for o in _PIPE3_WHEAT])
    else:
        _p3_tape[0] = dict(_p3_tape[0], market=[list(o) for o in _PIPE3_MINIMAL])
        _p3_tape[1] = dict(_p3_tape[1], market=[list(o) for o in _PIPE3_STEP2_MIN])
```

That's it. 11 lines replace 4. The rest of V43's 3,367 lines are untouched.

---

---

## Colosseum Results: 200 Games Each, LB-Identical Rules

Every match below uses `kaggle_environments.make('kaggriculture')` with no debug flags, no config overrides — identical to the leaderboard. 200 games per matchup (100 as player 0, 100 as player 1). Statistical significance tested via binomial test.

### pipe-4 vs the field

| Opponent | W-L-T | Elo Rate | Effect Size | p-value |
|---|---|---|---|---|
| **pipe-3** (our prev. best, V42 base + C9 opening) | 148-25-27 | **80.8%** | h=+0.662 (medium) | 0.000 |
| **V43 raw** (Ahmed's V43, no modification) | 193-7-0 | **96.5%** | h=+1.194 (large) | 0.000 |
| **V42** (Ahmed's V42) | 192-8-0 | **96.0%** | h=+1.168 (large) | 0.000 |
| **V41** (Ahmed's V41) | 193-7-0 | **96.5%** | h=+1.194 (large) | 0.000 |
| **pipe-1** (V40 base + V41 opening) | 172-28-0 | **86.0%** | h=+0.804 (large) | 0.000 |

### How much does V43 itself improve over V42?

| Matchup | W-L-T | Elo Rate | Effect Size |
|---|---|---|---|
| V43 raw vs V42 | 122-20-58 | **75.5%** | h=+0.535 (medium) |

### Reading the numbers

- **Elo Rate** = (wins + 0.5 × ties) / total. This is what the Kaggle Elo system uses. >50% = better.
- **Cohen's h** = effect size. <0.2 = negligible, 0.2–0.5 = small, 0.5–0.8 = medium, >0.8 = large.
- **p-value** = probability this result is due to chance. <0.05 = statistically significant.

### Key takeaways

1. **V43's reactive layers and C9's opening stack cleanly**: pipe-4 beats pipe-3 (same opening, V42 base) at 80.8% — that's the V43 base doing work.
2. **The C9 opening is still dominant on V43**: pipe-4 beats raw V43 at 96.5%. The opening optimization is just as valuable on the new base.
3. **V43 is genuinely better than V42**: Even without our mod, V43 beats V42 at 75.5%. Ahmed's shed overflow recovery is a real improvement.

---

---

## Build the Agent

No datasets, no internet, no GPU. The complete agent is embedded below.

---

## Build the Submission Archive

---

---

## How to Reproduce This

The full pipeline that found this optimization:

```
CLUSTER ENGINE (Union-Find from LB replays)
  Top 50 teams → download episodes → fingerprint first 144 actions → cluster at 90%
  Output: 33 clusters, inter-cluster win/loss edges
       ↓
MECHANISM TRACER (on inter-cluster losses)
  C9 beats C15 in 58 games → checkpoint divergence → action trace
  Output: ranked fix candidates with exact opponent actions
       ↓
COLOSSEUM (200-game LB-identical testing)
  Apply fix → 200 games at --parallel 10 → keep if p < 0.05
  Release gate: >96% elo rate for shipping
       ↓
ITERATE until cluster transition complete
```

The cluster engine, mechanism tracer, and colosseum are available in my other notebooks:
- [Colosseum: Agent Testing Framework](https://www.kaggle.com/code/nathanjacob/colosseum-876-2600-agent-testing-framework)
- [No Cow Left Behind: V40 Autopsy + Fix](https://www.kaggle.com/code/nathanjacob/no-cow-left-behind-v40-autopsy-fix)

### What's left on the table

pipe-4 captures the C9 opening (~10% of the 16% behavioral divergence from C9). The remaining gap:
- **Day 9–11 COW preference**: C9 buys 3x more cows (53 vs 18 across 58 games). This is a deep tape change, not a shallow swap.
- **Top 8 singletons**: The top 8 LB positions are all unique strategies (35–54% similar to the v40 cluster). Convergence won't get there — it requires innovation.

---

---

# Attribution and License

This agent is a derivative work. Credit where credit is due:

### Base agent: Ahmed Berat Özer
- [V43: Recovering Lost Harvests](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v43-recovering-lost-harvests) — the complete chassis, route library, reactive layers, and V43's shed overflow recovery / atomic planting / route proposal planner
- [V42: Production That Fits the Market](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v42-production-that-fits-the-marke)
- [V41: Review Candidate](https://www.kaggle.com/code/ahmedberatozer/kaggriculture-v41-review-candidate)
- Ahmed's agent retains Apache-2.0 notices and full attribution to thomastschinkel, yhay81, destbreso, aurax7, tetsutani, prvsiyan, Dmitrii Gluzdov, and all other contributors listed in V43's source

### Opening optimization: Cluster C9 insight
- The conditional opening was discovered by analyzing replay data from Cluster C9 teams (led by AI是我的豆包), who independently developed the minimal wheat strategy
- [Rayk Kretzschmar — Rank Your Agent](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent): the low-volume opening concept credited by Ahmed in V41

### Pipeline and analysis
- Strategy clustering, mechanism tracing, and colosseum testing by Nathan Jacob
- [Colosseum notebook](https://www.kaggle.com/code/nathanjacob/colosseum-876-2600-agent-testing-framework) for the testing framework

All Apache-2.0 notices from the original V43 source are retained in main.py. This notebook adds no new upstream code beyond the 11-line opening modification.

---

*If this analysis helped you understand the competition better, an upvote means a lot. Happy farming!*