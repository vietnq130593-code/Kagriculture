
## Evaluation

| Cohort | W/L/T | Strict win rate | Mean cash margin |
|---|---:|---:|---:|
| Development V46 (8 fresh worlds, 19 rivals, both seats) | 269/35/0 | 88.49% | +3,156.47 |
| Development predecessor (EXP288 build) | 217/73/14 | 71.38% | +3,090.83 |
| Independent V46 (32 untouched worlds) | 1080/135/1 | 88.82% | +2,682.61 |
| Independent predecessor | 835/323/58 | 68.67% | +2,365.16 |
| Independent V46, clone family (13 rivals) | 707/124/1 | 84.98% | +869.29 |
| Independent predecessor, clone family | 474/300/58 | 56.97% | +404.00 |
| Independent V46, other rivals (6) | 373/11/0 | 97.14% | +6,611.46 |
| Independent predecessor, other rivals | 361/23/0 | 94.01% | +6,614.34 |

Independent draw (1,216 games per policy): paired match points +17.80 percentage points over the predecessor (world-level bootstrap 95% interval [+10.44, +24.38]); clone family +24.58, other rivals +3.12. Worlds in this cohort are not shop-matched between the two policies (the town draw depends on the game state), so paired cash differences are not reported here; the shop-matched development screens are in the research notes.

| Rival (64 games each) | Predecessor W/L/T | V46 W/L/T | Points |
|---|---:|---:|---:|
| exact_v43 | 62/2/0 | 59/5/0 | -4.7 |
| fastclone24 | 60/4/0 | 53/11/0 | -10.9 |
| guru_dynamic | 60/4/0 | 60/4/0 | +0.0 |
| lynn_v5 | 60/4/0 | 61/3/0 | +1.6 |
| mirror_counter | 60/4/0 | 63/1/0 | +4.7 |
| mirror_v45 | 48/16/0 | 58/6/0 | +15.6 |
| mirror_v46 | 3/3/58 | 58/6/0 | +40.6 |
| pub_aurax_v6 | 48/16/0 | 58/6/0 | +15.6 |
| pub_beyond48 | 0/64/0 | 52/12/0 | +81.2 |
| pub_pipe7_open5 | 3/61/0 | 53/11/0 | +78.1 |
| pub_pipe8 | 3/61/0 | 51/13/0 | +75.0 |
| pub_tetsu_mirror | 2/62/0 | 49/15/0 | +73.4 |
| race8d_v44 | 60/4/0 | 53/10/1 | -10.2 |
| seven_rescue | 60/4/0 | 63/1/0 | +4.7 |
| thomas955 | 63/1/0 | 63/1/0 | +0.0 |
| v43_open78 | 63/1/0 | 59/5/0 | -6.2 |
| v45_open13 | 61/3/0 | 53/11/0 | -12.5 |
| v45_open5 | 61/3/0 | 51/13/0 | -15.6 |
| v49_bandit | 58/6/0 | 63/1/0 | +7.8 |

Mechanism and limits. The turn-0 and turn-1 effects are exact consequences of the per-unit lockstep market and the plan's fixed day-0 cash; they were verified with the official engine on two- and three-turn scripted games against every rival opening observed in 154 live games and in the new public notebooks. The sale-timing changes decide same-turn races against agents executing the same tape; against rivals with a different plan they change little. The predecessor's 70-unit round trip punished the original V43 opening by a melon seed; V46 gives that up for robustness, so against plain V43-family rivals it wins slightly less often in the shop-matched development screens (44-47 of 48 instead of 48).

All 1216 independent candidate/control pairs passed the official cash and product ledger audit; feed shortfalls, pickup shortfalls and animal escapes were 0/0/0 for V46 versus 0/0/0 for the predecessor.

Runtime: eight fresh full games with the candidate in a separate normal-GC process, Windows maximum 85.08 ms per call (step 712, the inherited V43 terminal closure planner with 64 simulations; the live predecessor measures 71.8 ms in the same game; the engine's actTimeout is 1 s; the project's local 50 ms rule was waived for this step); the same 5,752 actions replayed exactly on native Linux, maximum 15.28 ms. Shared-worker timings are not acceptance measurements; all timings are machine-dependent.

Local win rates against a frozen panel are not a ladder rating and not a guarantee; the ladder population changes daily.
