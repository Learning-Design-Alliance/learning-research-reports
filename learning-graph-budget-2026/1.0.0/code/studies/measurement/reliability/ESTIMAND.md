# Order is not a cheaper estimand. It is exposure.

`estimand_kappa.py`. `studies/outcomes/ope/c3_readiness.py` made A5 the binding constraint on the north star: a
graph-derived policy acts on the assay's output, realised gain tracks decision kappa, and C3's
sample scales as **1/kappa²**. The cheapest conceivable way to raise kappa is not a better
estimator or more learners — it is to **claim something weaker**. A drop says "meeting A first is
worth +0.11 on B". An order statistic says only "A comes before B".

The board appeared to support that: `course_grain.py` reads kappa **+0.859** on order against
`tail.py`'s **+0.438** on the drop. **That comparison was invalid and this study replaces it.** The
two readings differ on three axes at once — corpus (MOOCCubeX vs XES3G5M), grain (course vs
knowledge-component), and estimand (order vs drop). Only the third is the question.

So both estimands are computed here on the **same corpus, same pairs, same learners, same splits**.
Only the estimand changes.

## Matched assert rates, because kappa is not base-rate free

Kappa is chance-corrected but it still depends on how often the rule says yes. The drop asserts
~56% of pairs; an order statistic at its own bar asserts something else. Comparing at their own
bars would confound estimand with threshold, so each estimand's bar is tuned to hit a matched
assert rate, at several rates.

| assert rate | drop κ | order κ | gain | drop deranged | **order deranged** |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 55% | +0.494 | +0.984 | +0.489 | +0.036 | **+0.973** |
| 40% | +0.488 | +0.980 | +0.493 | +0.038 | **+0.972** |
| 25% | +0.456 | +0.974 | +0.518 | +0.060 | **+0.975** |
| 10% | +0.387 | +0.966 | +0.580 | +0.103 | **+0.961** |

## Verdict: `ORDER IS CONFOUNDED`

Order looks spectacular and is worthless. On **deranged** data — every learner's parent state
crossed onto another learner's dependant outcome, so no learner-level dependency survives — order
still scores **+0.97**. Essentially all of its reliability is item-level presentation order. It
agrees with itself about the curriculum, not about prerequisite structure.

The derangement is precise about what it does: it destroys **learner-level dependency** while
leaving **item-level timing** intact, because the donor's touch time still reflects where that item
generally sits in the sequence. An estimand that survives it is measuring the sequence, not the
dependency.

**Confirmed independently at course grain.** `course_order_derangement.py` ran the same control on
MOOCCubeX, where enrolment is learner-chosen rather than curriculum-set, and found the same thing:
real κ +0.857, deranged κ **+0.800**, excess **+0.057**. See `COURSE-GRAIN.md`.

## What it means for the drop

The drop's own deranged floor is not zero either — **+0.036 to +0.103**, rising as the assert rate
falls. Some of the drop's agreement is also exposure: cell composition tracks parent difficulty and
the dependant's outcome tracks dependant difficulty, and both halves see that.

**So the honest figure for the drop is its excess over its own deranged arm, not its raw kappa.**
At the operating point in use that is roughly **+0.48 − 0.10 ≈ +0.38**, which makes C3's 1/kappa²
penalty worse, not better: about **6.3×** rather than 4.7×.

## The recommendation this reverses

An earlier read of this programme's own board suggested switching the assay's output from a drop to
an order claim, priced at 1.4× to 3.85× cheaper. **That was an extrapolation across corpus, grain
and estimand simultaneously, and the measured answer is the opposite.** Switching estimands buys
nothing, because the reliability it appears to buy is the catalogue.
