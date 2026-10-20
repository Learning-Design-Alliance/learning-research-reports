# Does the attainment label's effect scale with its value, or is it a step? (Paper VI)

**Status: RUN 2026-10-06.** Pre-registered, with the floor run, at 78605d6, before the real slope was computed. The design, the estimands, the verdict strings and their
thresholds are in the docstring of `dose.py`, which is the primary record. The floor (`out/floor.json`)
ran and was committed with the pre-registration, before the real slope was computed. Results go below the
line; the plan above it is not rewritten.

## What is asked

No model calls and no corpus text: a reanalysis of existing per-case grader outputs. The outcome is a grader's mark on fixed work (`not-a-learner-outcome`).

Paper VI's swapped-label arm grades each answer twice, under its own student's attainment label and under
a paired student's label from the opposite tail. L = mark under the high label − mark under the low label
on the same answer is positive on every model (+0.28 to +0.76 of 10). Kapetanovic et al. (2026) found an
LLM judge's response to a prior score "threshold-like". So: **does the per-answer shift d grow with the
gap g between the two labels the answer saw, or is it a step?** And, on ASAP 2.0, where Qwen graded the
same essays under low (1.9/6), mid (3.0/6) and high (4.2/6) labels: what is the dose curve?

No model is called. Per-case dumps only (session scratchpad, verified against
`studies/measurement/grader-eval/analyses/per-case-dumps.sha256`); aggregates in `out/`.

## Design in one table

| piece | choice |
| --- | --- |
| models (primary) | the six default-configuration API models: Gemini 3.5 Flash Lite, GPT-4.1-mini, GPT-5-mini, Qwen3-235B, Claude Opus 5.5, Llama 4 Maverick |
| beside, never pooled | Gemini lite default re-run; Fable 5.1 via the agent route (100 answers) |
| g | high label − low label shown on that answer: 2.0 to 7.7 points, mean 3.72, SD 0.99 (same draw on every model) |
| pairing | by case index, not by student: a student's answers meet different partners, so g varies within a student |
| confound | the own-label half of g is the student's (corr with teacher mark +0.39 in the high tail) |
| estimand b | OLS d ~ tail + g + own label × tail + teacher mark × tail; with own controlled, b is identified from the partner's label only (SD 0.65 high tail, 0.76 low tail) |
| sensitivity | learner fixed effects; per-tail slopes; the raw unadjusted slope (descriptive) |
| interval | learner-cluster bootstrap within tail, 4,000 replicates, percentile |
| relative slope | ρ = b · mean(g) / L: 1 = fully proportional to the gap, 0 = a pure step |
| across models | pooled ρ = mean of the six models' ρ, one learner resample for all, on the 290 answers complete on all six |
| ASAP | paired contrasts mid − low, high − mid, curvature per label point; essay bootstrap, 4,000 |

**Identifying assumption.** Given tail, the student's own label and the answer's teacher mark, the
partner's label is unrelated to how the grader would move this answer. The pairing is deterministic
(corpus order), not randomised; measured corr(partner label, teacher mark) is −0.07 and +0.02. Weaknesses:
b is linear and pooled across tails that identify it on different label ranges; the label sentence also
carries a response count n that moves with the partner and is not in the dump; and the identifying
variation is the partner label, narrower than g's.

## Pre-registered verdicts (thresholds fixed in the docstring)

| level | strings | rule |
| --- | --- | --- |
| per model | `UNANSWERABLE-FLOOR` | the model's floor fails |
| | `GRADED` / `INVERSE` | b's 95% interval > 0 / < 0 |
| | `STEP-BOUNDED` | L > 0 and b inside ±k·b_prop, k ∈ {0.25, 0.5} the smallest the floor's step world reaches at ≥ 80%; never returned if neither does |
| | `UNRESOLVED` | otherwise |
| across models | `GRADED-` / `INVERSE-` / `STEP-BOUNDED-ACROSS-MODELS`, `UNRESOLVED-ACROSS-MODELS`, `UNANSWERABLE-FLOOR-POOLED` | the same rules on pooled ρ |
| ASAP | `MONOTONE-DOSE`, `STEP-LOW-TO-MID`, `STEP-MID-TO-HIGH`, `NON-MONOTONE`, `UNRESOLVED`; shape `LINEAR-IN-VALUE` / `CONCAVE` / `CONVEX` | paired 95% intervals; step margin ±0.05 levels |

The ASAP reading is **not blind**: its four arm means were published in `grader-attainment-groups` before
this was written. What is new is the paired intervals and the shape test.

## Floor record (`out/floor.json`, committed before the real slope was computed)

Synthetic d on each model's real structure (real g, tails, learners, own labels, teacher marks) and real
noise shape (learner effects shuffled within tail, residuals permuted within learner), mean held at the
model's L. 500 replicates per world, 1,000 bootstrap replicates inside each. Pass: GRADED ≥ 80% in PROP
and a signed call ≤ 10% in STEP.

| model | L | b_prop | STEP signed | PROP GRADED | HALF GRADED | NEG INVERSE | STEP-BOUNDED (k = 0.5) | pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | +0.37 | 0.099 | 0.09 | 0.53 | 0.21 | 0.57 | 0.00 | no |
| GPT-4.1-mini | +0.38 | 0.101 | 0.07 | 0.54 | 0.18 | 0.55 | 0.00 | no |
| GPT-5-mini | +0.52 | 0.140 | 0.08 | 0.68 | 0.25 | 0.67 | 0.00 | no |
| Qwen3-235B | +0.76 | 0.203 | 0.08 | **0.97** | 0.50 | 0.98 | 0.17 | **yes** |
| Claude Opus 5.5 | +0.28 | 0.074 | 0.06 | 0.66 | 0.22 | 0.69 | 0.00 | no |
| Llama 4 Maverick | +0.54 | 0.144 | 0.08 | 0.47 | 0.17 | 0.45 | 0.00 | no |
| *Gemini re-run (beside)* | | | 0.08 | 0.49 | | | | no |
| *Fable 5.1 agent, n = 99 (beside)* | | | 0.07 | 0.13 | | | | no |
| **pooled ρ, six models, n = 290** | | | 0.07 | **0.99** | 0.62 | 0.99 | 0.15 | **yes** |

Point estimates are unbiased in every world (mean recovered slope within 0.004 of the planted one,
signs correct in NEG). What this fixes before the real result:

- **Five of six models are `UNANSWERABLE-FLOOR` on their own.** The identifying variation (the partner's
  label, SD about 0.7 within tail, 14–19 learners per tail) is too narrow for a single model to see even a
  fully proportional effect 80% of the time. Only Qwen, the largest L, passes.
- **The across-model reading is answerable for GRADED vs not.** Pooled ρ recovers a fully proportional
  effect 99% of the time, a half-proportional one 62%, and calls a pure step signed 7% of the time.
- **`STEP-BOUNDED` is unreachable at every level.** No model and not the pool bounds the slope inside half
  the proportional slope in 80% of pure-step worlds (best: 17%). The instrument cannot show the effect is
  a step; a null here can only be `UNRESOLVED`.
- **ASAP floor passes**: LINEAR → `MONOTONE-DOSE` 100%, step low→mid 94%, step mid→high 95% (σ
  calibrated to the real sd of low − none, 0.53).

---

## Results

**RUN 2026-10-06** (`out/results.json`; post-hoc additions in `out/posthoc.json`). Answers complete:
300, 298, 297, 295, 300, 300 per model; 290 on all six; ASAP 2,996 essays on all four arms.

### Across models: `GRADED-ACROSS-MODELS`

**Pooled ρ = +0.84 [+0.38, +1.36]** (six models, 290 answers, one learner resample for all). The label's
effect on identical work grows with the gap between the two labels: on average about 84% of the shift at
the mean gap is accounted for by a slope proportional to the gap, and the interval excludes a pure step
(ρ = 0). It does not exclude a fully proportional effect (ρ = 1). `STEP-BOUNDED` was unreachable by the
floor, so this reading could only have been GRADED, INVERSE or UNRESOLVED; it is GRADED.

### Per model

b is in points of d per point of label gap; m was undefined on every model (STEP-BOUNDED unreachable).

| model | L [95%] | b [95%] | ρ [95%] | pre-registered verdict | FE b [95%] | high-tail b (low label varies) | low-tail b (high label varies) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | +0.37 [+0.30, +0.44] | +0.084 [−0.009, +0.194] | +0.84 [−0.10, +1.86] | UNANSWERABLE-FLOOR | +0.082 [−0.016, +0.188] | +0.13 [−0.04, +0.38] | +0.05 [−0.05, +0.15] |
| GPT-4.1-mini | +0.38 [+0.30, +0.45] | +0.114 [+0.025, +0.201] | +1.13 [+0.27, +1.91] | UNANSWERABLE-FLOOR | +0.126 [+0.027, +0.220] | +0.13 [−0.00, +0.26] | +0.10 [−0.02, +0.22] |
| GPT-5-mini | +0.52 [+0.44, +0.61] | +0.161 [+0.048, +0.287] | +1.15 [+0.37, +2.02] | UNANSWERABLE-FLOOR | +0.174 [+0.068, +0.290] | +0.02 [−0.16, +0.25] | +0.27 [+0.15, +0.41] |
| **Qwen3-235B** | +0.76 [+0.69, +0.82] | **+0.148 [+0.049, +0.255]** | +0.73 [+0.25, +1.21] | **GRADED** | +0.159 [+0.049, +0.267] | +0.22 [+0.08, +0.38] | +0.09 [−0.04, +0.24] |
| Claude Opus 5.5 | +0.28 [+0.23, +0.31] | −0.052 [−0.125, +0.018] | −0.70 [−1.64, +0.26] | UNANSWERABLE-FLOOR | −0.044 [−0.120, +0.030] | −0.07 [−0.19, +0.05] | −0.04 [−0.12, +0.05] |
| Llama 4 Maverick | +0.54 [+0.42, +0.64] | +0.297 [+0.125, +0.488] | +2.07 [+0.85, +3.57] | UNANSWERABLE-FLOOR | +0.279 [+0.094, +0.488] | +0.39 [+0.18, +0.64] | +0.23 [−0.01, +0.51] |
| *Gemini re-run (beside)* | +0.36 | +0.066 [−0.036, +0.170] | | UNANSWERABLE-FLOOR | | | |
| *Fable 5.1 agent, n = 99 (beside)* | +0.31 | −0.046 [−0.265, +0.158] | | UNANSWERABLE-FLOOR | | | |

- **Only Qwen's per-model verdict answers the question, and it is `GRADED`**: +0.15 points of shift per
  point of label gap, ρ = +0.73.
- The other five are `UNANSWERABLE-FLOOR` as pre-registered, whatever their intervals say. Descriptively,
  GPT-4.1-mini, GPT-5-mini and Llama have slope intervals above 0, Gemini's touches 0, and **Opus 5.5 is
  the one model whose point slope is negative** (−0.05, interval [−0.12, +0.02]; −0.1248 to four decimals); its d by gap tercile is
  flat (+0.35, +0.22, +0.26). The floor says a single model's interval this wide is not evidence either way.
- Direction is checked, not just magnitude: every slope is signed so that b > 0 means a bigger gap gives
  a bigger shift toward the high-labelled mark, and the floor's NEG world returns INVERSE with the
  correct sign on every model.
- The adjustment matters little: the unadjusted slope of d on g (descriptive, confounded by the student)
  is within 0.05 of b on every model, and learner fixed effects move b by at most 0.02.

**Post-hoc (added after the run, reported only).** Leave-one-model-out pooled ρ stays above 0 whichever
model is dropped: +0.60 [+0.11, +1.13] without Llama (the largest ρ), +1.17 [+0.70, +1.74] without Opus,
+0.78 to +0.86 otherwise. Mean d by gap tercile (g ≈ 2.7 / 3.6 / 4.8):

| model | d, smallest gaps | middle | largest |
| --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | +0.27 | +0.38 | +0.45 |
| GPT-4.1-mini | +0.22 | +0.32 | +0.58 |
| GPT-5-mini | +0.37 | +0.45 | +0.73 |
| Qwen3-235B | +0.59 | +0.73 | +0.94 |
| Claude Opus 5.5 | +0.35 | +0.22 | +0.26 |
| Llama 4 Maverick | +0.22 | +0.53 | +0.83 |

At the smallest gaps observed (about 2.7 points) the shift is still +0.22 to +0.59. The gap never falls
below 2.0 in this design (the tails are at least 2 points apart by construction), so whether the effect
vanishes as the labels converge, or keeps a floor of its own, is outside the data.

### ASAP 2.0, Qwen: `MONOTONE-DOSE / CONCAVE`

| contrast (0–6 scale, paired, 2,996 essays) | estimate [95%] |
| --- | --- |
| arm means none / low 1.9 / mid 3.0 / high 4.2 | 2.98 / 2.51 / 2.81 / 2.96 |
| mid − low | **+0.308 [+0.289, +0.327]** |
| high − mid | **+0.151 [+0.132, +0.169]** |
| high − low | +0.459 [+0.441, +0.477] |
| per label point, low → mid | +0.280 [+0.263, +0.297] |
| per label point, mid → high | +0.125 [+0.110, +0.141] |
| curvature (difference of the two) | −0.155 [−0.182, −0.127] |

Every step up in the label's value raises the mark on the same essay, so the effect is a dose, not a
step. It is concave: per point of label, the mark moves more than twice as much between 1.9 and 3.0 as
between 3.0 and 4.2. (Presence is not re-litigated here; for the record, the mid and low labels sit below
no label and the high label at it: −0.16, −0.47, −0.01.)

### What this answers, and what it does not

- **The reviewer's question has an answer: the label's value matters, not only its presence.** Both
  readings find a graded response: across six models on JorGPT (pooled ρ +0.84, interval excluding a step),
  on Qwen alone on JorGPT, and on ASAP's direct three-point curve. This is a different contrast from
  Kapetanovic et al.'s "threshold-like" finding, which compared a score present against absent; in the
  swapped-label design both arms carry a label, so only the value differs.
- **Not a strict proportionality claim.** ρ's interval runs from 0.38 to 1.36, and ASAP's curve is concave.
  The effect grows with the value and flattens toward the high end on ASAP.
- **Per-model shape is mostly not answerable** with 14–19 learners per tail: five of six models fail the
  floor alone, and Opus 5.5 is the one whose point estimate runs the other way.
- **The pre-registered STEP-BOUNDED outcome was out of reach**, so the study could never have shown that
  the effect is a step; it could show that it is not one, and did.
- **Identifying assumption** (partner label as good as random given tail, own label and teacher mark) is
  untested beyond the near-zero correlations reported; the response count n in the label sentence moves
  with the partner and is confounded with the value.

### Deviations

- The brief said g is "fixed by the student pairing". The harness pairs by case index, so g varies
  within a student; the design uses that (stated in the docstring before the floor).
- The worktree started on a stale `main` (afc51c0) without the grader studies; it was reset to the
  integration branch head (9b05cf6) before any work.
- Post-hoc leave-one-out and terciles were added after the run and are labelled as such.
