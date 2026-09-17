# Kaggriculture V46: First-Turn Microstructure and Sale Timing

V46 keeps the complete production policy of the previous releases (all V43 farming,
service and warehouse layers, the clone-gated sale pre-emption of V44 and the mirror gate)
and changes how the agent trades against the copies and derivatives of its own public
lineage that now fill the ladder:

* **First market turn.** The market settles orders index by index and quotes both players'
  current units at the same inventory. The previous 70-unit wheat round trip lifted the
  quotes of a rival's second wheat purchase, but a rival selling a small lot at index 1
  rides the same lift; against `[BUY 5, SELL 5]` or `[BUY 50, SELL 50]` it lost 32-77
  cash at turn 1, below the plan's 8-cash day-0 slack, and one or two wheat seeds with it.
  V46 buys its five feed units once at index 0 of turn 0 (`[BUY_PRODUCT WHEAT 7, SELL WHEAT 2]`),
  cleans turn 1, and never falls below the slack against any opening observed on the
  ladder; rival round trips lose 10-45.
* **Turn 1 lift.** Every tape of this lineage buys its feed at index 1 of turn 1. V46 buys 30
  wheat at index 0 of turn 1 and sells them back at turn 2, when no tape trades; the rival's
  purchase is quoted 4 higher per unit, again below its slack, and the resale meets the
  lifted quotes.
* **Sale timing.** Tape sales due within three turns are executed as soon as the units are
  in the shed (not at dawn, first-listed sale protected), the market list is ordered sales,
  then product purchases, then fixed-price orders, and the clone-gated pre-emption horizon
  rises to a full day as soon as a rival is seen selling a product we hold five or more
  turns ahead of the common plan.

No rival private information is used. The mechanisms of the third point follow the public
analysis "Beyond 48-0" by sdy623 (jaxa623), re-implemented over this project's chassis;
the turn-0 finding (buy the feed units at index 0 of turn 0) follows the public
"Pipe-8 clean opening" by Nathan Jacob. The exact lockstep simulations, the slack analysis,
the turn-1 lift and the race detector are this project's own work.

This notebook contains the complete agent. It needs no attached datasets, donor
notebook, internet, GPU, training, installation or compressed source blob. Run the five
code cells to produce `submission_competitive_v46.tar.gz`. Optional full-game checks
are off by default; enable `RUN_GAME_CHECKS` to play. The notebook does not submit
anything automatically.
