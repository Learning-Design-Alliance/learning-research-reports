# Which checks move when a checklist meets a planted defect, and where a checklist grader parts from a Likert one

**Status: PRE-REGISTERED 2026-10-28 at e5c2b3a, before any estimate was read. Floor revision 0 passed. RUN 2026-10-28; results below the line.** Design,
verdicts and predictions are fixed in the docstring of `defects.py`, which is the full record. Results
go below the line; the plan above it is not rewritten.

This is a follow-up to `../grader-boolean-rubrics/`, chosen by the maintainer from the analyses ranked
in the release's literature review. It makes no model call. It reads only the published per-case file
of release `checklist-grading-2026`.

## What is asked

The parent study found that a checklist loses 0.17 of its scale to an appended false sentence, against
0.47 for Likert. It also found that the checklist gains more from a key-terms sentence. A post hoc
split put checklists that carry an "avoid …" check at −0.22 and those without at −0.08. That split is
observational, because which questions got such checks was not assigned. This study decomposes each
answer's checklist change into the change on its avoid checks and the change on its presence checks.
It re-scores the same answers without the avoid checks, as a within-answer counterfactual. It also asks
where on the human scale the two formats' signed errors part.

| estimand | verdicts |
| --- | --- |
| E1: presence-check change under a contradiction (120 answers) | PRESENCE-CHECKS-REGISTER-CONTRADICTION / PRESENCE-CHECKS-BLIND (±0.02) / PRESENCE-UNRESOLVED |
| E2: avoid share of the loss, answers with avoid checks | AVOID-CHECKS-CARRY-THE-LOSS / PRESENCE-CHECKS-CARRY-THE-LOSS / SHARED |
| E2: presence-only re-score minus full score | AVOID-CHECKS-ADD-SENSITIVITY / AVOID-CHECKS-ADD-NOTHING (±0.02) / UNRESOLVED |
| E3: presence-check change under key-term stuffing (112 answers) | PRESENCE-CHECKS-REWARD-KEY-TERMS / PRESENCE-CHECKS-UNMOVED / PRESENCE-UNRESOLVED; AVOID-CHECKS-PENALIZE-STUFFING |
| E4: checklist minus Likert signed error, by human band (LOW ≤ 2.5, MID, HIGH ≥ 4.5) | CHECKLIST-HIGHER / CHECKLIST-LOWER / UNRESOLVED |

The floor passed every check, with true-positive rates of 99–100% and false-positive rates of 1–7%.

---

## Results

The study ran from the published per-case file. Every answer in the manipulation-pass sets had complete
per-check answers: 120 contradiction answers over 61 questions and 112 stuffing answers. The changes are
on the 0–1 scale, pooled over the two models, with 95% intervals that resample questions.

### Contradiction: which checks carry the loss

| set | n | total change D | avoid checks A | presence checks P | verdict |
| --- | ---: | --- | --- | --- | --- |
| all answers | 120 | -0.172 [-0.220, -0.123] | -0.109 [-0.152, -0.072] | -0.063 [-0.090, -0.033] | **PRESENCE-CHECKS-REGISTER-CONTRADICTION** |
| answers whose checklist has an avoid check | 77 | -0.224 [-0.288, -0.157] | -0.170 [-0.223, -0.122] | | avoid share S +0.760 [+0.639, +0.915]: **AVOID-CHECKS-CARRY-THE-LOSS** |
| answers with no avoid check | 43 | -0.079 [-0.125, -0.026] | | -0.079 [-0.125, -0.026] | |

**On answers whose checklist has an avoid check, those checks carry 76% of the loss.** Re-scored on
their presence checks alone, the same 77 answers lose -0.095 [-0.146, -0.038] instead of
-0.224 [-0.288, -0.157]. The difference, K = +0.129 [+0.084, +0.177], is a within-answer counterfactual: dropping the avoid checks
removes 58% of the checklist's loss (computed before rounding) (**AVOID-CHECKS-ADD-SENSITIVITY**). Presence checks do register a
contradiction on their own, at -0.063 [-0.090, -0.033] across all answers. That is 0.37 times what the avoid checks
contribute on the answers that have them (-0.170).

**At the level of single checks:**

- **Avoid checks** reverse their majority (YES to NO) in 49.1% of
  216 check-answer-model cases. Their two reps never disagree on the neutral
  form (0.0%).
- **Presence checks** reverse YES to NO in 10.5% of
  874 cases, against a rep-to-rep disagreement of
  4.0% on the neutral form. Their changes lie above the
  noise floor but are small.

**The parent's post hoc split is therefore mechanical, not a property of which questions got avoid
checks.** The avoid checks are where a contradiction is registered.

### Key-term stuffing: which checks carry the gain

| set | n | total change D | avoid checks A | presence checks P | verdicts |
| --- | ---: | --- | --- | --- | --- |
| all answers | 112 | +0.348 [+0.283, +0.411] | +0.003 [-0.010, +0.015] | +0.346 [+0.286, +0.404] | **PRESENCE-CHECKS-REWARD-KEY-TERMS**; avoid checks: NOT-SHOWN |

**The whole gain is presence checks turning from NO to YES:** 45.9%
of 844 presence cases, against a neutral-form rep disagreement of
2.5%. The avoid checks do not move. A sentence that names
the right terms without stating anything correct satisfies "does the answer mention X" checks, and no
check in these checklists asks whether the terms are used correctly.

### Where the formats part, by human score (the 620-answer main draw)

The signed error is the model score minus the human mean over 5, with both on the 0–1 scale.

| human band | n | Likert error | checklist error | checklist − Likert (G) | verdict |
| --- | ---: | --- | --- | --- | --- |
| LOW (h ≤ 2.5) | 65 | -0.144 [-0.216, -0.065] | -0.123 [-0.215, -0.023] | +0.022 [-0.071, +0.120] | UNRESOLVED |
| MID (2.5 < h < 4.5) | 145 | -0.149 [-0.210, -0.091] | -0.327 [-0.386, -0.265] | -0.178 [-0.234, -0.120] | **CHECKLIST-LOWER** |
| HIGH (h ≥ 4.5) | 410 | -0.049 [-0.065, -0.034] | -0.160 [-0.194, -0.127] | -0.111 [-0.143, -0.081] | **CHECKLIST-LOWER** |

**The checklist does not over-credit wrong answers.** Its LOW-band difference is +0.022 [-0.071, +0.120],
unresolved, and the prediction that it would be higher there failed. **It under-credits answers the
humans judged partly or fully correct**, by -0.178 [-0.234, -0.120] in MID and -0.111 [-0.143, -0.081] in HIGH.
Both formats score below the humans in every band. The checklist's shortfall is largest in the middle,
where a partly correct answer misses some enumerated checks and gets no credit for what it does say.

These are differences in level by band, not correlations. They locate the parent's validity loss, and
they do not replace it. A uniform shift would leave Pearson r unchanged. These shifts are not uniform:
the checklist is −0.18 lower in MID, −0.11 in HIGH and level in LOW. That differential compresses the
scale for answers the humans rank above the LOW band, which is where the checklist's correlation with
the humans is lost. This is the pattern Hodges et al. (1999) report for human raters using checklists
on competent performers.

### Predictions

| prediction | outcome |
| --- | --- |
| E1 PRESENCE-CHECKS-REGISTER-CONTRADICTION | yes |
| E2 SHARED or AVOID-CHECKS-CARRY-THE-LOSS | yes (AVOID-CHECKS-CARRY-THE-LOSS) |
| E2 AVOID-CHECKS-ADD-SENSITIVITY | yes |
| E3 PRESENCE-CHECKS-REWARD-KEY-TERMS | yes |
| E4 CHECKLIST-HIGHER in LOW | **no** (unresolved, +0.022) |
| E4 CHECKLIST-LOWER in HIGH | yes |

### What this says

A checklist written from a reference answer registers an error almost only through checks written
to look for it. Without such checks it nearly ignores a contradiction, and with them it carries most
of what it registers. Its presence checks reward naming the right terms. Its validity loss comes from
partial and full credit, not from wrong answers.

For an educator writing a checklist, the practical reading has two parts. The error checks are the
part doing the work, so they need to be there. The checklist's score for a partly correct answer runs
low, so it should not be read on the same scale as a holistic grade.

### Limits

- Avoid-type checks were identified by a word rule (`\bavoid`) over the checklist text, which this
  release does not publish. The rule was fixed in the parent before any grading call.
- The checklists were written by one model, and the defects were generated by one model.
- The bands use the human mean of two raters, whose agreement is 0.62.
