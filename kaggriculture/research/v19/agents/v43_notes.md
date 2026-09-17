# Kaggriculture V43: Recovering Lost Harvests

V43 targets a measured warehouse failure: workers can return at dawn with cargo
that exceeds the shared shed capacity. It sells existing inventory only when
otherwise discarded cargo will replace it, leaving the complete next-day stock
vector unchanged. Original field jobs and market-order prefixes are preserved.

This notebook contains the complete agent. It needs no attached datasets,
donor notebook, internet, GPU, training, installation or compressed source blob.
Run the five code cells to produce `submission_competitive_v43.tar.gz`.
Optional full-game checks are off by default; enable `RUN_GAME_CHECKS` to play.
The notebook does not submit anything automatically.

The release specializes copying of ordinary Python containers and avoids constructing movement lists when only their lengths are needed. This
performance change must preserve every action; it introduces no new strategy.


## Start the build


## Write the complete agent


## Verify source and entry point


## Build the submission archive


## Optional: run complete games



## Evaluation

| Cohort | W/L/T | Strict win rate | Mean cash margin |
|---|---:|---:|---:|
| Development V43 | 99/0/13 | 88.39% | +7,169.19 |
| Development V42 | 87/3/22 | 77.68% | +7,011.30 |
| Independent V43 | 412/10/26 | 91.96% | +6,259.49 |
| Independent V42 | 375/14/59 | 83.71% | +6,134.61 |
| Direct V43 vs V42, independent | 39/3/22 | 60.94% | +116.86 |
| Historical top recordings | 114/6/0 | 95.00% | +21,626.16 |
| Historical opponent recordings | 146/4/0 | 97.33% | +19,979.46 |

On the 32 reserved worlds, paired own cash changed by +96.14, relative margin by +124.88, and match points by +4.58 percentage points. Match points count a tie as one half. World-level bootstrap 95% intervals: own cash [54.27, 151.19], margin [72.46, 189.78], points [2.90, 6.47] percentage points.

The reacting panel contains seven configurations, including related replay-router lineages. These are new game worlds, not seven independent elite teams. Historical recordings are auxiliary and cannot react to changed actions. A local cash benefit may move close matches; it is not a major new production economy or a guaranteed ladder rating.

Most additional panel wins occur against V42 itself. Excluding that matchup, the 384-game results are V43 373/7/4 versus V42 370/9/5; the match-point difference is +0.65 percentage points. This is a targeted improvement with a modest gain against the other tested opponents.

All 448 independent candidate/control pairs passed official cash and product accounting. The performance revision matched all 322,112 candidate actions and all final rewards. Warehouse losses were 4,376 units versus 5,713. Feed, pickup and animal regressions were checked separately.

The full 896-game physical ledger was recorded for EXP278. EXP279 inherits that evidence only after reproducing all 322,112 candidate actions, leaving observations unchanged, and matching both final rewards on the same 448 games. Auxiliary recording and historical arena results were measured on the preceding behavior-equivalent sources.

The original EXP277 source failed its frozen Windows timing check at 71.66 ms. EXP278 also failed at 52.16 ms. Both results remain failures. The released EXP279 source passed a separately declared eight-game, normal-GC, separate-process check: Windows maximum 43.81 ms; the same 5,752 actions replayed exactly on Linux, maximum 17.58 ms. Shared-worker and diagnostic timings are not acceptance measurements. These measurements are machine-dependent.


# Attribution and license

This agent retains Apache-2.0 notices in its source. Modified in EXP-167 on
September 10, 2026 by Ahmed Berat Özer's Kaggriculture project.

- [Dmitrii Gluzdov — Two Coins, One Sheep](https://www.kaggle.com/code/dmitriigluzdov/kaggriculture-two-coins-one-sheep-lb-2650): bounded two-turn stock reservations, protection of scheduled pickups, partial future-order deductions and placement after worker repairs. Adapted to our per-player chassis state and preserved terminal planner. Earlier seven-turn physical closure work is also retained through v31.
- [prvsiyan — The Moon Counts Melons](https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-moon-counts-melons): the later cattle substitution controller. Earlier fertilizer/feed and tomato production work remains credited in v31's source.
- [yhay81 — Shop Router 0909](https://www.kaggle.com/code/yhay81/shop-router-0909): thirteen public action schedules and ordered shop-pair routing; earlier ShopForge/Fieldbook lineage.
- [aurax7 — Reactive Router](https://www.kaggle.com/code/aurax7/kaggriculture-reactive-router): sale timing and shed projection lineage.
- thomastschinkel: replay-routing research and earlier foundation of this project; tetsutani: market, room and repair mechanisms credited in the retained source.
- [destbreso — X-ray Your Agent](https://www.kaggle.com/code/destbreso/x-ray-your-agent): diagnostic methodology. Its notebook is not bundled as agent runtime.

Other audited Codes appear in SOURCE_AUDIT.md and the evaluation panel; their
presence there does not imply their code was incorporated. Credits do not
imply author endorsement or a verified private-leader implementation.

## EXP-168 changes (v34)

- [lucifer19 — Harvest Nocturne](https://www.kaggle.com/code/lucifer19/harvest-nocturne-the-market-has-a-rhythm): occupied-tile similarity and exact price-loss ordering ideas/code, adapted and independently tested. Per-seat memory/reset replaces its single shared controller state.
- [flexonafft — Most Powerfull Route](https://www.kaggle.com/code/flexonafft/kaggriculture-most-powerfull-route): requested source snapshot; its full executable bundle is byte-identical to Two Coins above. No new route or original capability is attributed to a renamed copy.
- leoprovorov: public-layout comparison lineage credited by Nocturne.
- [Kaggle official implementation](https://github.com/Kaggle/kaggle-environments/tree/master/kaggle_environments/envs/kaggriculture): Apache-2.0 market-price functions from version1.32.7; verified against local engine.

All earlier in-source notices and the full Apache-2.0 license remain in main.py.
This list implies no author endorsement. Exact incorporated switches appear
in agent/manifest.json; unselected experiments are not claimed as improvements.

## EXP-175–178 changes (v35, September 11, 2026)

- [yhay81 — Shop Router 0911 Simple](https://www.kaggle.com/code/yhay81/shop-router-0911-simple): revised opening market-sequence idea. Our selected opening uses `BUY_PRODUCT WHEAT 13`, `BUY_PRODUCT WHEAT 30`, `SELL WHEAT 30`; it retains the earlier thirteen routes rather than adopting the donor's complete fourteen-route revision.
- [leoprovorov — Two Coins at High Noon: Small Improvement](https://www.kaggle.com/code/leoprovorov/two-coins-at-high-noon-small-improvement): Mirror Counter's public cash-response mechanism. Adapted to the existing occupied-tile similarity guard and per-player state, requiring positive matching cash changes after a probe. Our fourth-turn reservation is an independently tested modification, not a claim about the donor's reported results.
- [prvsiyan — The Soil Remembers Rain](https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-soil-remembers-rain): the already reviewed V234 six-sheep southeast expansion, including financing, confirmed hiring, feed, care and credited production. Adapted to our chassis state, combined telemetry and terminal-planner abstention. This capability is newly integrated here; the September 11 exported donor code itself is unchanged from the earlier reviewed version.
- [lucifer19 — Harvest Nocturne V2](https://www.kaggle.com/code/lucifer19/harvest-nocturne-v2-a-lighter-start): audited startup and runtime packaging reference. Our chassis already shared read-only route data, so no new gameplay gain is attributed to its deep-copy removal.
- [Nagata V6.2](https://www.kaggle.com/code/nagatakengo/kaggriculture): added as a reacting evaluation opponent. Its policy is not bundled in this submission.
- [destbreso — X-Ray Your Agent](https://www.kaggle.com/code/destbreso/x-ray-your-agent) and [Georgy Mamarin — What 2600+ Farms Do Differently](https://www.kaggle.com/code/georgymamarin/kaggriculture-what-2600-farms-do-differently): whole-cohort and economic diagnostic references; no runtime code copied from these notebooks.

Integration, public-response safeguards, experiment design, official-engine accounting checks and release packaging: Ahmed Berat Özer's Kaggriculture project. The complete agent retains its Apache-2.0 license and upstream notices. Exact source hashes and the distinction between incorporated code, evaluated opponents and diagnostics are recorded in `research44/SOURCE_AUDIT.md` and `research47/REPORT.md` in the project workspace.

## EXP179–180 changes (V36, September 11, 2026)

- [Tetsutani — Market Smart Farming](https://www.kaggle.com/code/tetsutani/market-smart-farming-kaggriculture): its updated four-turn configuration motivated this isolated extension of our existing Two Coins stock-reservation layer. V36 applies four turns within V35's physical stock, debt, purchase and terminal guards; farm routes and investment controllers are unchanged.
- [Rayk Kretzschmar — Rank Your Agent](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent) and [Kunal Desale — Kaggriculture2026V1](https://www.kaggle.com/code/kunaldesale2408/kaggriculture-2026-v1): newly evaluated exported opponents. Their separate sale-order scoring ideas were screened and rejected as standalone modifications; those runtime policies and their route libraries are not incorporated into V36.
- The September11 afternoon Flexon export hashes identically to V35; this differs from the older EXP168 snapshot described above. It supplies no new V36 capability.

All earlier Apache-2.0 notices and the complete license remain in main.py. This 130-byte source extension, experiment design, accounting checks and packaging are by Ahmed Berat Özer's Kaggriculture project. Full provenance: research48/SOURCE_AUDIT.md and research49/REPORT.md. Credits imply no author endorsement.

## EXP182–190 changes (V37, September 12, 2026)

V37 retains V36's route library and all earlier source notices. The finite native-crop fertilizer planner, committed-parent priority guard, projected warehouse guard and exact-spawn cooperative tomato labor scheduler were developed and physically audited in this project. Earlier unsuccessful livestock and rival-flow experiments are not included. The latest public Code review is documented in research56/SOURCE_AUDIT.md; those updated analytical/data notebooks supplied no new executable policy to this release.

All earlier Apache-2.0 notices, including thomastschinkel, yhay81 and destbreso, remain intact in main.py along with the full license. Evaluation, guards and packaging are by Ahmed Berat Özer's Kaggriculture project. Credits imply no author endorsement. See research59/REPORT.md for the mixed evidence and release-candidate status.


## EXP193–217 changes (V38, September 12, 2026)

- [Steven Lee Hans — Lord Momo Returns](https://www.kaggle.com/code/stevenleehans/kaggriculture-rank-580-lord-momo-returns): conceptual reference for comparing feed cost with production value and selling surplus fertilizer. Our implementation independently adds care-value accounting, the following-day feeding schedule check, actual carried-food checks, and a reserve for all remaining native and committed crop inputs. No guarantee about future feeding or monotone fertilizer prices is inherited from the donor narrative. Audited exported source SHA-256: `b5c2e156689b41cea5f2e1a0a1cae2e18fd70423931bbac0885bba8b2142c497`.
- The exact-spawn finite-input tour planner, committed-parent fertilizer queue guard, conservative tomato fertilization margin test, next-day service simulation, whole-animal survival audit and integration are by Ahmed Berat Özer's Kaggriculture project. The source preserves the existing route and chassis lineage; tested mechanisms are identified by the frozen manifest.
- [Pilkwang — Structured Economic Policy](https://www.kaggle.com/code/pilkwang/kaggriculture-structured-economic-policy), the Momo source and four other distinct exports were examined in the September 12 public refresh. Six new distinct policies entered the reacting panel; their inclusion as opponents does not mean their runtime was incorporated. Exact V37 duplicates were deduplicated. Complete review: `research84/SOURCE_AUDIT.md` in the project workspace.

All earlier Apache-2.0 notices, including thomastschinkel, yhay81 and destbreso,
remain in `main.py` with the full license. Credits imply no author endorsement.
The final source, complete raw outcomes and frozen-source confirmation are
documented in `research86/REPORT.md` and `research86/results/release_evidence.json`.


## V39 consolidation — September 13, 2026

Production-calendar feeding, bounded physical wheat replenishment, native-pickup
coverage, stock reservation before saturated market turns and current-liability
funding were developed in Ahmed Berat Özer's Kaggriculture project. V39 selects
the unchanged combined EXP231 source after the requested candidate consolidation.
All earlier credits and Apache-2.0 notices remain in main.py, including
thomastschinkel, yhay81 and destbreso. Credits do not imply endorsement.

The latest public inventory audit covered 485 references. Zhihuan Xue's
Kaggriculture Timed Six Cow was reviewed and retained once as an evaluation
opponent. None of its code was copied into this agent. Results and provenance
are recorded in research100, research101 and research102.


## V41 development attribution

The V39 base and all embedded upstream notices are retained. The low-volume
opening was adapted from Rayk Kretzschmar's public [Rank Your Agent notebook](https://www.kaggle.com/code/raykkretzschmar/kaggriculture-rank-your-agent).
Funded atomic planting, first-slot grain funding and final-hour watering
contracts were implemented by Ahmed Berat Ozer. Newly reviewed MetaCounter R1
and Adaptive Land Allocator were evaluated as opponents; their agent source
was not incorporated into this release.


EXP259 owned-input preloading, adjacent pickup/feed ordering, conservative first-sale funding and observation confirmations were implemented by Ahmed Berat Özer. The planned-crop-retirement classifier belongs to validation tooling and is not agent behavior. Master Engine V3 was audited as a V40 runtime copy; its source was not incorporated. All Apache-2.0 license text and upstream notices remain in main.py.


## Production-library lineage retained in V42

## EXP239–241 development — September 13, 2026

- [Yusuke Hayashi (yhay81) — Shop Router 0913](https://www.kaggle.com/code/yhay81/shop-router-0913), version 1 (script version 349474696): the new fixed midgame action plans and ordered shop-pair map. Apache 2.0 was verified in the notebook page's visible License section. Source SHA-256: `77cf67723a753be957cf70fdb8abbce7ef5c020299e8acd16ed8d2dc8b929dfa`.
- Ahmed Berat Özer's project: compatibility repair for late native hiring and already committed crop crews; the fixed choice between the existing V39 policy and the repaired new plans; whole-team cross-fitted selection, integration and official-engine audits.

The common opening, terminal controller and preceding production/market controls retain their existing attribution. The selected source preserves the complete Apache-2.0 text and upstream notices, including thomastschinkel, yhay81 and destbreso. No donor endorsement or live-rating guarantee is implied. This file records research lineage; release qualification is determined separately by the frozen protocol and results.


## EXP242 compatibility correction

Ahmed Berat Özer's project corrected the request window of already committed sheep crews when the selected native plan hires workers at hours 3–6. Initial investment, production routes and the fixed observed shop selector remain unchanged. The correction was motivated by a complete daily animal census, not a loss-only sample. All prior Apache-2.0 notices and source credits are retained.


## EXP260 post-V41 development — September 14, 2026

V42 preserves the V41 opening and service repairs while testing the complete
observed-shop production allocator described above. Integration, the declared
three-arm experiment, official physical audits and packaging are by Ahmed Berat
Özer's project. All existing Apache-2.0 license text and notices are retained.

[Aurax Shop Router Reactive V5](https://www.kaggle.com/code/aurax7/kaggriculture-shop-router-reactive-v5)
motivated the separately tested earlier reservation boundary. Its rescue
wrapper is not incorporated. The results section identifies whether that
boundary was selected along with the production allocator.
[Nathan's No Cow Left Behind](https://www.kaggle.com/code/nathanjacob/no-cow-left-behind-v40-autopsy-fix)
was a diagnostic and evaluation reference; no rescue or rematching code from it
is incorporated. EcoBot V7 and Adaptive Land Allocator R10 are additional
evaluation opponents, not bundled runtime dependencies. Credits imply no
author endorsement.


## EXP261 runtime measurement

The policy source is unchanged. Ahmed Berat Özer’s project added candidate-process isolation to the validation harness, preserving the original shared-process failures. This harness is not bundled as agent runtime.


## V43 — EXP277–279

Exact dawn warehouse replacement contracts and the behavior-preserving copying specialization and exact-distance calculation were developed by Ahmed Berat Özer’s project. No newly reviewed public notebook controller is added in this release. All inherited Apache-2.0 notices, the full license, and credits including thomastschinkel, yhay81 and destbreso remain in main.py. Credits imply no endorsement. The seed repair experiment was inactive in development and is disabled in the selected policy.
