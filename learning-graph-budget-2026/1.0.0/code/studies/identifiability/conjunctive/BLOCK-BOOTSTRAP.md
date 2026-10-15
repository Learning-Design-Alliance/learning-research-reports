# Stage 3 counted 11,203 pieces of evidence. It had 122.

`studies/identifiability/sparse-signal/empirical_null.py` fitted an empirical null to stage 3's z-scores and got
**N(+0.038, 2.753)** — a null 2.75× wider than the one the p-values were computed against. Taken at
face value that erases the 2,425 SUPPORTED triples entirely (π₀ = 1.000).

It should not be taken at face value, and the reason is specific. Stage 3's standard error was not
assumed; it was **validated per-triple against an explicit learner derangement at a ratio of 0.997**,
with a deranged mean interaction of −0.00032. The SE is right *for one test*. A correct per-test SE
and a cross-test spread of 2.75 are not a contradiction — they are the two halves of one fact:

> **11,203 triples were built from 30 items.**

Each item sits in roughly 2,240 triples. Two triples sharing an item share learners, share that
item's base rate and share whatever real structure it carries. Widening every SE to cover that pays
for the correlation by destroying the one quantity that was measured correctly. The right correction
resamples the unit the dependence lives in — the same rule this programme already follows for
permutation ("permute the unit the treatment was assigned to"), applied to resampling.

## What is resampled

A triple is a 3-way draw from the item set, so the **multiway cluster bootstrap** weights each triple
by the *product* of its three items' draw counts (the pigeonhole bootstrap). An item drawn twice
doubles the weight of every triple it appears in; an item not drawn at all removes its ~2,240
triples. The learner-level evidence inside a triple is untouched. The **whole pipeline — Benjamini-
Hochberg included — is re-run inside every replicate**, because it is the pipeline's output that is
being given an interval, not its input.

**The scoring reproduces stage 3 exactly** before anything is bootstrapped: 11,203 triples, 2,425
SUPPORTED, 1,212 above the bar, `max |interaction difference| = 0.00e+00` against stage 3's 400
saved rows. If it had not, the run stops rather than correcting a pipeline that is not stage 3's.

## The floor

A bootstrap always returns an interval; that is not evidence it found anything. Two synthetic worlds
were built with the **same triple geometry and the same amount of planted signal**, differing only in
where the signal is attached — scattered across triples, or attached to four items and everything
they touch.

| world | design effect (median of 6 reps) | worst rep |
| --- | ---: | ---: |
| **unclustered** — non-nulls chosen at random across triples | 11.1 | 13.1 |
| **clustered** — non-nulls are every triple touching 4 planted items | **201.2** | 230.9 |

The instrument separates them by 18×. It also supplies the number that stops "design effect > 1"
being mistaken for a finding: **a 3-way product bootstrap over 30 clusters sits at ~11 even with no
correlation at all.** That 13.1 is the bar the real data has to beat.

## Result

| | point | 95% block CI | design effect | effective independent triples |
| --- | ---: | --- | ---: | ---: |
| SUPPORTED share | 0.216 | [0.149, 0.294] | 94.1 | **119** |
| above-bar share (≥ +0.10) | 0.108 | [0.063, 0.171] | 91.6 | **122** |
| above-bar count | 1,212 | [599, 1,746] | — | — |

Leave-one-item-out, all 30 items: the worst single item (`k214`, 1,091 triples) costs **29.9%** of
the above-bar triples. `k18` costs 15.3%, `k10` 13.9%. No item carries half.

**Verdict: `SURVIVES`.**

## What changed and what did not

**The claim is the same. Its precision is not.**

- The design effect is **91.6**, seven times the unclustered reference of 13.1. The dependence is
  real and it is item-driven, exactly as the empirical null's σ₀ = 2.75 implied.
- So stage 3's 11,203 tests are worth about **122 independent ones**, and its 1,212 above-bar triples
  are one observation with an interval of **[599, 1,746]**, not 1,212 observations.
- But the above-bar share's lower bound, **0.063**, still clears the 0.05 that the false-discovery
  allowance itself occupies. Conjunctive structure in XES3G5M is not an artefact of treating
  correlated tests as independent.
- And it is **not concentrated** the way `studies/identifiability/within-task/conjunctive.py` found for A14, where 2 of 38
  tasks held the whole excess. Here the largest single item accounts for under a third.

**This supersedes the naive re-reading `studies/identifiability/sparse-signal/` would suggest.** Restating every count at
σ₀ = 2.75 would have thrown away a correct SE to pay for a dependence that can be resampled directly.

**What it does not rescue.** The 671 triples that survived `ability_control.py` inherit the same
design effect — they are drawn from the same 30 items and have not been separately blocked. And
`studies/identifiability/assay-generality/local_background.py` has since shown the +0.10 bar is itself local, moving 9.7% of
pairs' status when read per-family. Both corrections point the same way: **the binding constraint is
the number of items, not the number of learners.** 30 items is what 11,203 tests are worth 122 of.

```
python3 block_bootstrap.py --items 30 --draws 1000
```

Reads XES3G5M. Raw exports stay in the session scratchpad; only aggregates are committed.
