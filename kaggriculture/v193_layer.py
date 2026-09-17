# ================================================================== v19.3 ADVANCE-WIDEN layer
# Sale-advance window widened from 2 to 3 turns (v46's _ADV_LOOK=3), applied by
# overriding the embedded v18's LOOKAHEAD constant in its namespace (the advance
# function reads it at call time, so the override takes effect from the next
# call onward — i.e. from step 0 of the episode, before any advance can fire).
#
# WHY: ahmedberatozer's V46 ("First-Turn Microstructure and Sale Timing") runs
# a 3-turn advance window over the same V43-family tape and is the only family
# we still split games with after v19.1 (18W/30L, -$45) — their published eval
# attributes the remaining edge to sale timing. v18's author chose 2; v46 chose
# 3; the battery decides which fits OUR chassis (v18 advance + v19 A4 ledger).
#
# The A4 ledger in the embedded v19 is window-agnostic (it accounts whatever
# the advance sells), so widening the window needs no other change.

# one-time namespace override (idempotent, before the host is ever called)
_V193_TELEMETRY = {"adv3_set": 0, "adv3_errors": 0}
try:
    _ns18 = _V192_NS["_V191_NS"]["_V19_NS"]["_V18_NS"]  # noqa: F821
    if _ns18.get("LOOKAHEAD") != 3:
        _ns18["LOOKAHEAD"] = 3
        _V193_TELEMETRY["adv3_set"] = 1
    _V193_HOST = _V192                       # noqa: F821  (v19.2's entry point)
except Exception:
    _V193_TELEMETRY["adv3_errors"] += 1
    _V193_HOST = _V192                       # noqa: F821


def agent(observation, configuration=None):
    return _V193_HOST(observation, configuration)


agent.telemetry = _V193_TELEMETRY
