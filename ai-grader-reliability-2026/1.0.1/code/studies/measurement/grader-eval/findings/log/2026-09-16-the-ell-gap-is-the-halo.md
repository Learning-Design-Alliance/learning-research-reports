---
type: log-entry
date: 2026-09-16
title: The ELL gap is the halo — measured observationally, demonstrated causally, and halved by a proposed fix
---

# 2026-09-16 — Reliability, validity and fairness turn out to be one problem

Three questions that looked separate, answered with one instrument each, and they converge.

## 1. Fairness, done properly rather than as one statistic

The earlier ELL result was a single number produced by a mode that also did five other things.
`--mode fairness` is now the standard battery — residual by group, residual by ability band,
calibration slope by group, precision by group, and decision parity at a pass mark — computed offline
from any dump carrying subgroup labels, at no cost.

Building it exposed **two bugs in my own first pass**, each of which would have published a false
finding:

- **`NA` was being treated as a group.** The widest gap for both `economic` and `disability` was
  against students whose status is *unrecorded*. Missingness is not an attribute a student has, and
  those students differ systematically. Excluded.
- **No correction for selecting the widest of k groups.** The same winner's-curse discipline applied
  everywhere else in this area was missing here — and this battery runs across five axes at once. The
  threshold now widens by `E[max of k standard normals]`.

Corrected, on ASAP 2.0 (n=1,400, holistic 1–6):

| axis | widest residual gap | verdict |
| --- | --- | --- |
| **ELL** | 0.275 ±0.115 | **finding** |
| **economic** | 0.163 ±0.079 | **finding** |
| disability | 0.131 ±0.127 | marginal |
| **race** | 0.205, bar 0.318 | **not a finding** |
| gender | 0.023 | not a finding |

**Race is not a finding on this corpus with this model**, and that matters: it is the specific claim
the standard critique makes. What *is* there is an ELL gap and an economic one. Every slope is within
0.06, so all of these are pure SHIFTS — removable by a per-group correction, which is a policy
decision, but not by the single shared calibration this area relies on.

**The harm in the currency a student feels.** At a pass mark of 3, among students *the human placed
above it*: 99% of non-ELL students were passed by the machine, and **91% of ELL students**. One in
eleven ELL students who deserved to pass was failed, against one in a hundred of their peers.

## 2. Why — tested causally, not inferred

Observational subgroup analysis cannot say why, because group membership is confounded with everything
about the writing. But two established findings here predict this gap exactly: the grader's criterion
scores correlate at 0.76–0.81 and it cannot attribute an injected defect to the criterion it belongs
to; and learner writing differs from first-language writing most visibly in **surface form**.

If both hold, a learner making the *same argument* must be marked down on CONTENT for their grammar.

`--mode fairness-probe` holds the argument fixed and varies only the surface — article omission,
subject–verb agreement, preposition substitution, plural inflection, the best-documented L1-transfer
features, applied mechanically. No lexis, no argument, no sentence order changes. The essay says
precisely what it said before.

| surface altered | content | organization | language |
| --- | --- | --- | --- |
| none | 5.99 | 4.58 | 5.57 |
| 30% of sites | −0.42 | −0.32 | −0.72 |
| 60% of sites | **−0.62** | −0.52 | −1.31 |

**Content falls 0.62 on a 0–10 scale for an argument that did not change.** The observational ELL gap
is 0.275 of a 1–6 band — about 0.46 on this scale. **The leak is larger than the gap it has to
explain.** Nearly half of the penalty for imperfect surface form is charged to criteria that have
nothing to do with surface form.

So the ELL gap is not a mysterious bias to be litigated. **It is the halo, seen from the fairness
side.** The same single-latent-judgement fact that produces 0.79 between-criterion correlation and
zero criterion localisation also produces a measurable disadvantage for second-language writers.

## 3. Which makes the fix testable — and it works

If the gap is the halo, the `siblings` configuration written earlier today should reduce it. Same
probe, same essays, only the prompt framing changed:

| | content leak | organization leak | language (legitimate) |
| --- | --- | --- | --- |
| production before | −0.62 | −0.52 | −1.31 |
| **production now (`siblings`)** | **−0.30** | −0.45 | −1.34 |

**The construct-irrelevant leak into content halves. The legitimate language signal is untouched** —
the grader still notices the grammar got worse by exactly as much, it just stops charging it to the
argument. That is the shape a real fix has, rather than a general flattening of scores.

## What this settles about the three questions

**Yes, all three are answerable empirically, and they are not independent.**

- **Reliability** — agreement against a human ceiling on the same items, plus test-retest (0.937).
- **Validity** — manipulate the text so the ground truth comes from construction, not from a marker
  (`--mode babel`, `--mode dress-case`). This is the only family that can detect a grader scoring
  fluency, because human markers are never shown the manipulated text.
- **Fairness** — the observational battery for *whether*, and a causal probe for *why*. Neither alone
  is sufficient: the battery cannot identify a mechanism, and the probe cannot tell you the mechanism
  is actually operating on real students.

**The load-bearing insight is that a validity defect became a fairness defect.** A grader that cannot
keep its constructs apart will always disadvantage whoever differs on the construct it is leaking
from. Fairness work that stops at subgroup means would have found the gap and had nothing to do about
it; the fix came from the validity side.

## Limits, stated plainly

One corpus for the observational half and a different one for the causal half, one model throughout.
The surface transforms are a controlled linguistic manipulation, not a simulation of any real writer,
and real learner writing differs in ways these transforms do not capture. The probe shows the
mechanism *can* produce the gap, not that it is the only thing producing it. **The check that matters
now is re-running the battery on a cohort graded under `siblings`** — the prediction is a materially
smaller ELL gap, and it is falsifiable.
