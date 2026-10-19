---
type: log-entry
date: 2026-09-16
title: ASAP 2.0 closes two coverage gaps and finds a differential a calibration cannot fix
---

# 2026-09-16 — ASAP 2.0, and the ELL gap

First corpus added since the coverage grid existed, and the grid picked it: ASAP 2.0 is CC BY 4.0,
downloads unauthenticated, and lands on two axes nothing else touched — **secondary students** (every
other corpus is undergraduate or short-answer) and **page-length prose**, which was the last
unmeasured level of `length`. 24,728 source-based argumentative essays, seven prompts, holistic 1–6.
n=1,400 stratified on the human score.

**No ceiling.** One rater per essay, exactly as predicted when it was first surveyed, so nothing here
is an absolute claim. Two things are readable anyway.

## Which prompt you set moves the grader more than which language it is in

| prompt | QWK |
| --- | --- |
| Does the electoral college work? | 0.626 |
| Exploring Venus | 0.581 |
| Facial action coding system | 0.514 |
| Driverless cars | 0.472 |
| Car-free cities | 0.464 |
| The Face on Mars | 0.401 |
| "A Cowboy Who Rode the Waves" | 0.293 |

One rubric, one rater pool, one population, one subject — and a spread of **0.334**. That is wider
than the whole language contrast (0.021) and comparable to the SAS-Bench subject spread (0.216).
Without a ceiling this cannot be split into "harder task" and "worse grader", and it does not need to
be to matter: **a single per-corpus agreement figure hides a great deal**, and a pilot run on one
assignment predicts the next one poorly. New factor in the ontology (`taskPrompt`).

## The grader is lenient to everybody, and less lenient to English-language learners

The corpus was deliberately sampled across economic and geographic populations and ships
`ell_status`, `economically_disadvantaged`, `student_disability_status` and `race_ethnicity`. **They
are analysis metadata and never enter the prompt** — `--mode attainment` already showed this grader
shifting when told about the learner, so passing an attribute would manufacture the effect.

The quantity is the **residual**, mean(machine − human) within a group. A raw mean comparison measures
the essays; the residual asks whether work a human scored the same is scored the same by the machine
whoever wrote it.

| group | n | mean human | residual |
| --- | --- | --- | --- |
| not ELL | 1,167 | 2.91 | **+0.732** ±0.051 |
| ELL | 208 | 2.51 | **+0.457** ±0.102 |
| not economically disadvantaged | 438 | 2.95 | +0.822 ±0.056 |
| economically disadvantaged | 728 | 2.74 | +0.659 ±0.057 |

Overall the grader marks **+0.695 levels high**. The ELL gap is 0.28 levels with non-overlapping
bootstrap intervals; the economic gap is 0.163 and also clears. **Disability and race/ethnicity
differences do not clear their intervals and are not findings** — the widest race gap is 0.205 with
intervals up to ±0.205, and reporting it as a result would be reading noise.

**Why the direction is the harmful one.** The grader inflates everybody. It inflates ELL writers
*less*. So a deployment using these scores as they come scores ELL students below non-ELL students
whose work a human rated identically — roughly a quarter of a band on a six-band scale.

**And the calibration we rely on cannot fix it.** The affine correction is one shift and one gain
fitted across the whole population; applied here it removes the +0.695 and leaves the 0.28 exactly
where it is. Everything this area has said about calibration — that it transfers across cohorts at no
cost, that it is the cheapest lever available — was measured on leniency that was *uniform*. A
differential is a different defect and needs a different answer: either per-group correction, which
is its own governance question, or a prompt that does not have the differential.

**Scope.** One corpus, one model, one task type; ELL status is self-declared and confounded with
writing features the rubric legitimately marks. This is enough to stop us claiming the grader is
group-neutral, and not enough to quantify the harm in a deployment. It is the first fairness
measurement in this study and it should not be the last.
