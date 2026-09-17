# 103/128 Fresh Public | v43 Sparse Shop Hybrid

**A coherent 719-step opening, exactly two observable shop branches, and no
opponent-family classifier.**

The title is a local interactive result against eight executable public agents:
**103 wins and 25 losses in 128 fresh games**, using eight unseen seeds and both
seats. It is not a Public-LB score.


---

## 1. The simplification hypothesis

v42 had five continuation experts and a direct-value router. In practice, its
post-freeze router abstained to one fallback in every public-panel game. More
features had created more ways to route into a continuation whose farm state
was not actually compatible.

I therefore looked at a different signal: the public action streams behind two
recent, orderly climbs—**BurntPotato submission 55709825** and
**ActiveMusyoku submission 55691574**. Across 174 public seat-games, the useful
variation was surprisingly low-dimensional:

```text
common route
    ├── first shop is YARN  -> yarn-first continuation
    └── second shop is YARN -> yarn-second continuation
```

This is behavioral evidence, not a claim about who authored or copied source
code. Team and submission names are used only for offline provenance; runtime
never receives them.


---

## 2. Chronological route extraction

The 174 games are ordered by creation time. The oldest 70% select real,
complete medoid trajectories; the newest 30% remain untouched route-source
holdout.

| Public shop cell | Fit | Later holdout | Mean later margin |
|---|---:|---:|---:|
| default | 69/81 | **32/38** | +5,363 |
| first shop YARN | 12/13 | **4/4** | +12,404 |
| second shop YARN | 16/18 | **3/4** | +5,492 |
| first shop BAKERY | 8/9 | **2/7** | -1,943 |

Actor disagreement receives three times the medoid distance of market-order
disagreement. The chosen default and YARN routes share every full action through
step 87 and every farmer/hand action through step 158.


---

## 3. Runtime policy: two branches, no classifier

```python
route = "default"
if first_shop == "YARN_STORE" and step >= 88:
    route = "yarn_first"
elif second_shop == "YARN_STORE" and step >= 153:
    route = "yarn_second"

action = planners[route](observation)
```

There is no nearest-neighbor lookup, learned family label, player identity,
submission ID or hidden future action. Both shop events are public before the
first differing action.

Each of the three child planners still observes every turn. This detail matters:
calling a stateful weed-repair controller for the first time only after a late
route switch can silently lose its transaction state. Every child therefore
stays synchronized, while only one action is emitted.

The feedback surface remains narrow: bounded weed repair and reordering of
existing SELL slots. The policy does not splice an arbitrary farm suffix onto
an incompatible opening.


---

## 4. Same-seed development ablation

| Candidate | Wins | Worst seat | Worst public opponent | Mean margin |
|---|---:|---:|---:|---:|
| v42 direct-value router | 22/32 | 71.9% | 0.0% | +20,219 |
| fixed default only | 20/32 | 62.5% | 50.0% | +19,676 |
| **v43 sparse YARN** | 30/32 | 93.8% | 50.0% | +27,373 |

The fixed default loses 12 games, concentrated in the YARN seed. The sparse
branch recovers ten of them and finishes **30/32**. This is the causal ablation:
same opponent code, seed and seat; only the two shop continuations differ.


---

## 5. Known opening, unseen continuation holdout

The strict replay split groups behavior as:

```text
actor_h96 opening × actor_h200 suffix × actor_h360 suffix
```

A row is evaluated only when its h96 opening exists in train but its composite
h200/h360 continuation does not. This prevents a seed/team split from treating
another copy of the same continuation as independent validation.

| Candidate | Wins | Worst seat | Worst opponent | Mean margin |
|---|---:|---:|---:|---:|
| v42 | 45/116 | 36.2% | 0.0% | +1,058 |
| fixed default | 90/116 | 74.1% | 25.0% | +8,527 |
| **v43 sparse YARN** | 108/116 | 89.7% | 50.0% | +12,617 |

The replay result is **108/116**, but replay opponents cannot react to the
counterfactual agent. It supports route compatibility; it is not a live-LB
estimate.


---

## 6. Final untouched executable panel

After selecting the architecture, I used eight disjoint seeds against eight
executable public agents, always from both seats.

| Candidate | Wins | Worst seat | Worst public opponent | Mean margin |
|---|---:|---:|---:|---:|
| frozen v42 | 84/128 | 64.1% | 12.5% | +20,897 |
| **frozen v43** | 103/128 | 79.7% | 50.0% | +23,441 |

v43 improves win-value from **67.2%** to
**80.5%** and the worst-opponent cell from
**12.5%** to
**50.0%**, with zero agent failures.
Its weakest first-shop cell is PET_CAFE at
**16/26**.
That weakness is reported rather than hidden behind the aggregate.


---

## 7. Why the EGG market maker is not in production

BAKERY-first deteriorated to 2/7 in the chronological source holdout, so I
implemented a separate EGG round-trip expert. It could spend only residual cash
after a fixed floor, animal-feed reserve, near-term route investments and shed
headroom.

I tested maximum batches of 5, 10 and 20. Across the 32-game paired development
panel, every version produced **0 outcome differences** from v43 without the
expert. A plausible mechanism is not enough: the extra state machine did not
earn its complexity, so production disables it.

This is also why there is no BAKERY farm-route branch. The fit-side BAKERY
medoid is action-identical to default; inventing a new suffix would violate the
observed compatibility evidence.


---

## 8. Artifact integrity

- exact `main.py`: **63,309 bytes**
- SHA-256: `69f06a802b62aa08f28705dab5728eb924bb6a7c23ffe0164f65b104cc3dadf3`
- deterministic archive SHA-256: `fb821a9f9867cd413e40323e1e79f1014b74eac7aab3db2bcdbfc6eea5e36a10`
- Python standard-library-only standalone artifact
- 719-step smoke tests: both seats `DONE`
- deployment versus selected candidate: **16 games, 0 outcome mismatches**
- focused planner/router/market tests: **20 passed**
- runtime identity and lineage features: **none**

The builder rejects either route if it differs before its validated branch
boundary. This makes “controller slippage” a build failure rather than a
leaderboard surprise.


---

## 9. Public provenance and attribution

The exact medoid actions come from public competition replays:

- [default source episode 96815867](https://www.kaggle.com/competitions/kaggriculture/episodes/96815867)
- [YARN-first source episode 96905004](https://www.kaggle.com/competitions/kaggriculture/episodes/96905004)
- [YARN-second source episode 96824976](https://www.kaggle.com/competitions/kaggriculture/episodes/96824976)

The observed submission lineages are explicitly credited to **BurntPotato**
and **ActiveMusyoku**. Behavioral equality does not establish source ownership.

This work also builds on public analysis by
[Rayk Kretzschmar](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-findings-from-zero-to-top-meta),
[beicicc](https://www.kaggle.com/code/beicicc/kaggriculture-c20-exact-replication-control),
[prvsiyan](https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-moon-counts-melons),
and the lineage-validation correction in
[Georgy Mamarin's episode audit](https://www.kaggle.com/datasets/georgymamarin/kaggriculture-episodes).


---

## 10. Limits and next experiment

- 103/128 is local executable evidence, not a Public-LB guarantee.
- The eight public agents are important baselines, not the whole ladder.
- First-shop PET_CAFE and some FARMERS_MARKET/PIZZA states still lose.
- A newly copied deterministic v43 does not preserve this best-response edge.
- The next branch must be selected on a new chronological block; adding another
  classifier to explain these 25 losses would repeat v42's mistake.

The intended next experiment is one new PET/demand-compatible continuation
whose opening remains exact through its first observable decision—not a larger
router.
