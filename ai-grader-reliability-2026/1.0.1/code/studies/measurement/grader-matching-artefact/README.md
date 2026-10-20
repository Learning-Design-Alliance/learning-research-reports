# How much of the grader's no-label group gap is the matching artefact? (Paper VI, scope-audit H15)

**Status (latest): RUN 2026-10-06 under amendments 1–2, floor passed; read at the known reliability
under amendment 3 (2026-10-06).** No model calls were made.

**Verdict at the known reliability (amendment 3).** The data paper fixes the reliability of the human
score: one rater 0.75, and about 0.857 for the two-read adjudicated score (Spearman–Brown). Read at
those two values, the pre-registered fixed-ρ verdicts are, across both graders:

| axis | ρ 0.75 (lower bound) | ρ 0.857 (best estimate) |
| --- | --- | --- |
| ELL | PARTLY-ARTEFACT | NOT-ARTEFACT |
| disability | PARTLY-ARTEFACT | NOT-ARTEFACT |
| economic | NOT-ARTEFACT | NOT-ARTEFACT |

- **What survives at equal true score:**

  | axis | ρ 0.75 | ρ 0.857 |
  | --- | --- | --- |
  | ELL | −0.15 to −0.17 | −0.18 to −0.21 |
  | disability | −0.21 to −0.22 | −0.25 to −0.27 |
  | economic | −0.09 to −0.12 | −0.12 to −0.15 |

- **How much is artefact.** 27–32% of the observed gap at ρ 0.75 and 13–16% at ρ 0.857.
- **The gap is not explained away.** It vanishes only at ρ ≈ 0.50 (break-even 0.49–0.52), which the
  raters' own agreement (r = .75) rules out.
- **The open question has moved.** It is no longer the reference's noise. It is whether the human
  raters are themselves group-neutral, which the classical error model cannot test.

The registered result across the bracket is unchanged:
`RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.80 / 0.85 / 0.70)`. Under the original
bracket, before the paper was read, the surviving range was −0.11 to −0.28.

See "Results" at the end. The pre-registration below was committed first, at 34e8110 (status then:
PRE-REGISTERED, NOT RUN).

## What is asked

Paper VI reports that, with no attainment label, the graders mark English learners' and
disability-identified students' essays 0.21–0.32 of a level below their peers' "at equal human
score" on ASAP 2.0 (`../grader-attainment-groups/out/results.json`, `none_arm_residual_gap`):

| axis | Qwen3-235B | GPT-4.1-mini |
| --- | --- | --- |
| ELL | −0.242 | −0.205 |
| disability | −0.318 | −0.295 |
| economic | −0.170 | −0.135 |
| gender (F) | +0.031 | +0.069 |

Gemini showed ELL −0.275 and economic −0.163 on an earlier draw (grader-eval log, 2026-09-16).

The scope audit (finding H15) points out that "equal human score" means equal *observed* score from
one rating. The groups differ in mean: ELL 2.53 against 3.00, disability 2.38 against 3.01. When the
matching score is noisy, focal essays in a stratum have lower true quality on average, because the
best estimate of true quality is shrunk toward the group's own mean (Kelley). An unbiased grader
would then show a negative residual gap too. Under classical test theory the expected gap is
β (1 − ρ_w) (μ_focal − μ_ref), where ρ_w is the within-group reliability of the human score and β is
the grader's slope on true quality. With β = 1 this is the audit's (1 − ρ) × (mean difference).

How much of 0.21–0.32 is that artefact?

## Design (summary; the docstring is the record)

- **The human score's reliability.** The corpus has no rater-level field. At design time the ASAP
  2.0 data paper could not be read from this session (the egress proxy blocks sciencedirect, arxiv,
  researchgate, zenodo and aclanthology), so reliability was **bracketed** from unverified web-search
  snippets. The maintainer has since supplied the paper, and the figures are now verified against
  its text (Crossley, Baffour, Burleigh & King 2025, *Assessing Writing* 65, 100954,
  doi:10.1016/j.asw.2025.100954, §3, p. 3; see amendment 3):
  - essays were scored by expert raters "using a double-blind rating process followed by 100 percent
    adjudication" (two independent ratings per essay, as the pre-adjudication inter-rater figures
    imply; the text does not give the adjudication procedure);
  - the released dataframe holds "the average human assigned score for the essay", which in the
    file is an integer 1–6 (no half points), so it is an adjudicated or rounded composite of the two
    reads, not their raw mean;
  - inter-rater reliability before adjudication was weighted κ = .745, r = .750 on the ~13,000
    PERSUADE 2.0 essays (20 raters) and weighted κ = .659, r = .750 on the ~12,000 new essays
    (14 raters).

  One rater's reliability is then about 0.75, and a score that uses both ratings sits near the
  Spearman–Brown 0.857. The design below is unchanged; it was run with the bracket:
  - **prior:** ρ ~ U(0.65, 0.90), carried through the bootstrap.
  - **grid:** 0.60–0.95, reported for every number, with the break-even ρ.
  - **data bound:** a triad estimate from H and the two graders, reported but not used. Shared
    LLM error biases it down.
- **Primary correction.**
  - Group-mean model: OLS of H on all group fields and prompt over the whole corpus (24,728).
  - Kelley posterior of true quality given H and groups.
  - An **unbiased grader** M = clip(round(α + βT + ε)), calibrated at each ρ to reproduce the real
    grader's mean, covariance with H and variance.
  - The artefact is the exact expected gap this grader shows on the real draw, with the real strata,
    weights and positivity rule from `analyse.py`.
  - Corrected gap C = observed − artefact.
  - Checks: against the analytic β(1 − ρ_w)Δμ, against the audit's (1 − ρ)Δμ, and against a
    Monte Carlo of the same model.
- **Two other corrections, reported beside it:**
  - The gap at equal *estimated true* score: WLS of M on the Kelley mean, its square, and the group
    indicator.
  - An errors-in-variables comparison that does not stratify on H: γ = ΔM − (b/ρ_wa) ΔH, with ΔM/ΔH
    reported beside β.
- **Interval.** A bootstrap over essays within quota cell, B = 2,000. Each resample draws ρ from the
  prior and recalibrates the grader.

## Pre-registered verdicts

These are applied per model and axis to C's 95% prior interval, signed in the direction of the
observed gap.

| verdict | rule |
| --- | --- |
| `ARTEFACT-EXPLAINS-IT` | the interval includes 0 and excludes the observed gap |
| `PARTLY-ARTEFACT` | the interval excludes 0 (on the observed side) and excludes the observed gap |
| `NOT-ARTEFACT` | the interval includes the observed gap and excludes 0 |
| `UNRESOLVED` | the interval includes both |
| `OVERCORRECTED` | the interval lies wholly on the opposite side of 0 |

The scope is as follows:
- Axes: ELL, disability, economic; gender is reported too.
- Across models: the shared verdict, or both verdicts joined by " / ".
- The paper's headline is the ELL and disability pair.
- Grid-ρ verdicts and the two other corrections' verdicts are reported. A verdict that depends on
  the approach is reported as approach-dependent.

## Detection floor (pass before any grader score is read)

The floor uses forward synthetic worlds on the real draw's covariates only: groups, prompt, quota
cell and weights. In each world:
- T = μ + noise and H = clip(round(T + u), 1, 6). This tests the normal model against the integer
  scale.
- The grader is 0.10 + 0.90T + N(0, 0.6), rounded, minus a planted d on ELL and disability.
- Worlds cross realised reliability 0.65, 0.75 and 0.85 with d = 0, 0.10 and 0.25. Each world has
  100 replicates and B = 200.

Pass criteria:
- **F1:** at the true ρ, |mean C − planted| ≤ 0.03 on every axis and world.
- **F2:** the prior interval's coverage is ≥ 90% on ELL and disability.
- **F3:** at d = 0, the interval falls wholly below 0 in ≤ 8% of replicates.
- **F4:** at d = 0.25, it falls below 0 in ≥ 80%.
- **F5:** at d = 0 and ρ 0.65, the uncorrected gap is ≤ −0.05, so the artefact exists in the
  instrument.

## Label-by-group contrasts (item 5)

D_low compares two grades of the same essay, so the true-quality difference within a stratum should
cancel. It does not cancel if the label's effect itself varies with true quality. The check has two
parts:
- **(i)** With a constant label effect and a noisy reference (ρ 0.65), |bias of D_low| ≤ 0.02 for a
  planted 0 and for a planted 0.10.
- **(ii)** With the measured slope of (low − none) on H, converted to a true-score slope, the D_low
  bias is reported at ρ 0.65, 0.75 and 0.90.

## Limits stated in advance

- **The error model is classical.** The human's error is assumed independent of group and of true
  quality. If raters themselves mark ELL essays down, the reference is biased, not just noisy, and
  nothing here corrects that.
- **Reliability is not measured.** It is bracketed, so every conclusion is conditional on the
  bracket.
- **Gemini is projection only.** It has no per-essay dump, so its figures use the analytic formula
  with β bracketed.

## Amendment 1 (after the first floor world, before any grader score was read)

The revision-0 floor failed on its first world, at realised reliability 0.65 with nothing planted.
- **F2 and F3 failed.** The prior interval covered 0 in 75–86% of replicates and lay wholly below 0
  in 14–25%.
- **The correction itself was accurate.** At the true ρ its bias was +0.006 or less.
- **The prior is at fault.** A world at the prior's low edge is corrected as if ρ were about 0.78.
  The reliability is the quantity the answer turns on, so integrating it out hides that.

The second world (d = 0.10) showed a second fault. The calibration absorbed 15–19% of a planted bias,
because a group bias inflates the pooled cov(M, H).

Revision 1 makes three changes:
1. **Headline by reliability.** The verdict rule is applied at each fixed ρ in {0.65, 0.70, …, 0.90}
   (bootstrap B = 500). A verdict that is the same everywhere stands. Otherwise the result is
   `RHO-DEPENDENT (<verdict> from <ρ>; …)`. The prior interval is reported, not used.
2. **Within-group calibration.** The unbiased grader is matched to the real grader's within-group
   covariance with H and its within-group variance.
3. **The floor's truth is post-stratified on true-score strata**, which is the estimand's own
   definition.

F1 and F5 are unchanged. F2–F4 are judged on the fixed-ρ interval at the true ρ. Revision 0 runs to
completion and is kept as `out/floor-rev0.json`.

## Floor revision 1 result, and amendment 2 (before any grader score was read)

Revision 1 (`out/floor-rev1.json`) passes F1, F3, F4 and F5 and misses F2 in one cell of 18.

| realised ρ | d | ELL: bias / coverage / below 0 | disability: bias / coverage / below 0 | uncorrected ELL gap | artefact (exact / analytic) |
| --- | --- | --- | --- | --- | --- |
| 0.65 | 0 | +0.010 / 0.94 / 0.02 | +0.014 / 0.96 / 0.00 | −0.156 | −0.166 / −0.178 |
| 0.65 | 0.10 | +0.007 / 0.95 / 0.69 | +0.000 / 0.97 / 0.73 | −0.254 | |
| 0.65 | 0.25 | +0.010 / 0.94 / 1.00 | +0.002 / 0.96 / 1.00 | −0.398 | |
| 0.75 | 0 | +0.011 / 0.93 / 0.01 | +0.011 / 0.93 / 0.03 | −0.107 | −0.118 / −0.128 |
| 0.75 | 0.10 | +0.007 / 0.95 / 0.76 | +0.008 / 0.97 / 0.73 | −0.208 | |
| 0.75 | 0.25 | +0.002 / 0.97 / 1.00 | +0.007 / 0.94 / 1.00 | −0.357 | |
| 0.85 | 0 | +0.003 / **0.88** / 0.05 | −0.001 / 0.92 / 0.05 | −0.068 | −0.071 / −0.077 |
| 0.85 | 0.10 | +0.005 / 0.95 / 0.82 | +0.005 / 0.95 / 0.71 | −0.162 | |
| 0.85 | 0.25 | +0.004 / 0.94 / 1.00 | +0.011 / 0.95 / 1.00 | −0.308 | |

What the floor shows:
- **The correction recovers the planted bias.** Its bias is within +0.014 everywhere.
- **The artefact is real.** With nothing planted, matching on one noisy integer rating gives an
  unbiased grader a gap of −0.07 (ρ 0.85) to −0.16 (ρ 0.65) on ELL, and −0.09 to −0.22 on
  disability.
- **The analytic β(1 − ρ_w)Δμ slightly overstates the exact artefact**, by 0.01–0.015.
- **The answer depends on ρ.** Getting ρ wrong by 0.10 moves the corrected gap by about 0.07–0.10.
- **Power is limited at 0.10.** A planted 0.10 is detected in 69–82% of replicates; 0.25 in 100%.

**Amendment 2.** The one F2 cell is ELL at realised ρ 0.85 with nothing planted, at 88 of 100
against 90. The mean coverage over all 18 cells is 0.94. That cell is re-run once with 300 fresh
replicates. F2 passes if the pooled ELL coverage is ≥ 0.90; otherwise the floor fails and the run
does not happen. This rule is committed before the recheck runs.

**Recheck (`out/floor-recheck.json`): PASSED.** With 300 fresh replicates, ELL coverage is 0.957,
disability 0.943 and economic 0.923. The intervals lie wholly below 0 in 1.3–3.7% of replicates and
the bias is +0.001 to +0.005. The floor therefore passes under amendment 2.

Revision 0 also ran to completion (`out/floor-rev0.json`). It failed F1–F4 and passed F5, which
confirms the two faults amendment 1 fixed. Its bias at d = 0.25 was +0.03, the calibration's
absorption.


## Amendment 3 (2026-10-06, after the run): reading the registered grid at the now-known reliability

The maintainer supplied the data paper (Crossley, Baffour, Burleigh & King 2025, *Assessing Writing*
65, 100954, §3, p. 3). It fixes the human score's reliability at values inside the pre-registered
grid. **No new analysis is run and nothing in `out/results.json` or `out/label-check.json` is re-run
or altered.** The registered fixed-ρ verdict rule is read at two values, decided here before any
number is written into this README:
- **ρ = 0.75, the lower bound.** One rater's reliability equals the inter-rater correlation for
  parallel raters (r = .750 in both subsets). A released score that uses two reads is no less reliable
  than one of them.
- **ρ = 0.857, the best estimate.** This is Spearman–Brown of 0.75 over two ratings,
  2(.75)/(1 + .75), on the assumption that adjudication is at least as good as averaging two raters.

0.857 is not a grid point. Its values are interpolated linearly between the committed 0.85 and 0.90
outputs: the point estimate and both bootstrap interval endpoints. The verdict there is the registered
rule applied to the interpolated interval. When the two neighbours agree, this equals their verdict,
because a convex combination of two intervals preserves the rule's linear inequalities. When they
disagree, it is reported as lying between them. The label-by-group implied biases are evaluated
exactly at 0.857 with the committed analytic formula, from the committed slope and corpus model.
Corrected z = (measured − implied bias) / se, with se from `grader-attainment-groups`.

One sensitivity is reported beside these, labelled as such and not used as a verdict. The released
score is an integer, so it cannot be the raw mean of two reads. A synthetic check (normal true score,
two integer raters at r = .75) gives the reliability of plausible integer composites. The reading at
that value is interpolated from the grid in the same way.

The registered result string, `RHO-DEPENDENT (...)`, stays the registered result. This amendment
reads it at a known value. The reading is done by `reliability_known.py`, which reads only committed
outputs, the corpus's essay ids and its blank-field pattern (for the subset check), and the
grader-attainment-groups dumps' essay ids.

---

## Results (2026-10-06)

The real grader scores were read only after the floor passed. The none-arm gaps reproduce
`grader-attainment-groups` to 1e-9, and this is asserted in the script. `out/results.json` was
written twice by deterministic seeds. The second run added only the post-hoc low-ρ points, and its
printed verdicts are identical to the first's.

### The corrected gap

Each row gives the observed gap, the artefact an unbiased grader with this grader's leniency, scale
and noise would show on this draw, and the corrected gap at equal true score with its fixed-ρ 95%
bootstrap interval (B = 500).

| model | axis | observed | artefact at ρ 0.65 / 0.75 / 0.90 | corrected at ρ 0.65 | at ρ 0.75 | at ρ 0.90 | break-even ρ | verdict across 0.65–0.90 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Qwen3-235B | ELL | −0.242 | −0.119 / −0.069 / −0.020 | −0.124 [−0.185, −0.061] | −0.173 [−0.242, −0.109] | −0.222 [−0.287, −0.157] | 0.50 | PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.80 |
| Qwen3-235B | disability | −0.318 | −0.168 / −0.101 / −0.034 | −0.150 [−0.218, −0.092] | −0.217 [−0.284, −0.160] | −0.284 [−0.349, −0.219] | 0.52 | PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.85 |
| Qwen3-235B | economic | −0.170 | −0.086 / −0.050 / −0.014 | −0.084 [−0.157, −0.004] | −0.120 [−0.189, −0.046] | −0.156 [−0.230, −0.086] | 0.51 | PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.70 |
| Qwen3-235B | gender (F) | +0.031 | +0.054 / +0.033 / +0.012 | −0.023 [−0.091, +0.047] | −0.002 [−0.071, +0.063] | +0.019 [−0.045, +0.087] | 0.76 | UNRESOLVED |
| GPT-4.1-mini | ELL | −0.205 | −0.096 / −0.056 / −0.016 | −0.109 [−0.158, −0.057] | −0.149 [−0.199, −0.102] | −0.189 [−0.241, −0.141] | 0.50 | PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.80 |
| GPT-4.1-mini | disability | −0.295 | −0.138 / −0.083 / −0.029 | −0.157 [−0.206, −0.095] | −0.212 [−0.269, −0.152] | −0.266 [−0.318, −0.214] | 0.49 | PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.85 |
| GPT-4.1-mini | economic | −0.135 | −0.070 / −0.040 / −0.011 | −0.065 [−0.121, −0.007] | −0.095 [−0.161, −0.043] | −0.124 [−0.189, −0.066] | 0.52 | PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.70 |
| GPT-4.1-mini | gender (F) | +0.069 | +0.046 / +0.028 / +0.011 | +0.023 [−0.031, +0.080] | +0.041 [−0.012, +0.094] | +0.058 [+0.003, +0.110] | 0.56 | UNRESOLVED from 0.65; NOT-ARTEFACT from 0.85 |

**Across models, per axis (the pre-registered headline):**
- ELL: `RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.80)`
- disability: `RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.85)`
- economic: `RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.70)`

Each is the same on both models. Gender: `UNRESOLVED` on Qwen; on GPT-4.1-mini UNRESOLVED from 0.65
and NOT-ARTEFACT from 0.85. The female advantage is small, and at ρ ≈ 0.76 (Qwen) it is entirely
artefact.

**Reported, not the verdict:**
- **Prior interval, ρ ~ U(0.65, 0.90):**
  - Qwen: ELL −0.183 [−0.258, −0.092] NOT-ARTEFACT; disability −0.231 [−0.317, −0.121]
    PARTLY-ARTEFACT; economic −0.127 [−0.214, −0.040] NOT-ARTEFACT.
  - GPT-4.1-mini: ELL −0.157 [−0.221, −0.086], disability −0.223 [−0.297, −0.136], economic −0.100
    [−0.164, −0.031], all NOT-ARTEFACT.
- **Approach dependence.** The two other corrections agree in sign everywhere and in the verdict
  family. They attribute slightly more to the artefact; at ρ 0.75:

  | model | axis | Kelley regression | errors-in-variables |
  | --- | --- | --- | --- |
  | Qwen | ELL | −0.137 | −0.131 |
  | Qwen | disability | −0.194 | −0.193 |
  | Qwen | economic | −0.128 | −0.125 |
  | GPT-4.1-mini | ELL | −0.128 | −0.121 |
  | GPT-4.1-mini | disability | −0.206 | −0.198 |
  | GPT-4.1-mini | economic | −0.101 | −0.101 |

  Their bracket verdicts are PARTLY-ARTEFACT throughout (Qwen ELL and disability), NOT-ARTEFACT
  (economic, both models), or RHO-DEPENDENT with the change at 0.85–0.90 (GPT-4.1-mini ELL and
  disability). None reads ARTEFACT-EXPLAINS-IT anywhere in the bracket.
- **Ratio check (errors-in-variables).** The focal − reference difference in grader marks is 0.70–0.92
  of the difference in human marks, against a disattenuated grader slope β of 0.45–0.56. A grader
  unbiased on true quality would have ΔM/ΔH = β, so the graders separate the groups by more than
  their own slope on quality predicts.

### Why the artefact is smaller than the audit's formula

The audit's (1 − ρ)Δμ assumes the grader moves one level per level of true quality. Calibrated, the
graders move only β = 0.57 (Qwen) and 0.47 (GPT-4.1-mini) of a level per level of true quality at
ρ 0.75, and 0.38–0.69 across the bracket. Their marks correlate only 0.52–0.55 with the human score.
The artefact is β(1 − ρ_w)Δμ, so it is about half the audit's figure. For ELL at ρ 0.75 on Qwen:

| artefact estimate | value |
| --- | --- |
| exact | −0.069 |
| Monte Carlo | −0.072 |
| analytic | −0.081 |
| audit formula | −0.119 |

### Reliability: what the data say, and the caveat

- **The triad bound is low.** On the 2,985 essays both graders scored it is ρ_H = 0.37 raw and
  0.30 within group.
  - The two LLMs correlate **0.76** with each other and only 0.52 and 0.55 with the human.
  - If their agreement beyond the human were all true quality, the human score would be that
    unreliable. Matching would then explain the whole gap and more (post hoc points, point
    estimates only):

    | ρ | 0.35 | 0.45 | 0.50 | 0.55 |
    | --- | --- | --- | --- | --- |
    | Qwen ELL corrected gap | +0.29 | +0.08 | +0.00 | −0.05 |

- **Why it is a lower bound.** Two LLM graders share error, which is the surface-form halo of the
  2026-09-16 probe, and shared error inflates their agreement.
  - The documented agreement between trained human raters (Crossley et al. 2025, p. 3: weighted
    κ .745 and .659, r .750 in both subsets) implies single-rater reliability of about 0.75.
  - Under that, the LLMs' correlation of 0.76 is far above the ~0.38 that independent errors would
    give.
- **The disagreement is the question itself.** Whatever the LLMs share beyond true quality can
  include exactly the group-correlated surface signal whose size is being estimated.
- **What would settle it.** The inter-rater figures from the data paper, or a second independent
  human rating on a subsample. (The data paper has since been read: see amendment 3 and "Reconciling
  with the data's own bound" below.) The gap is grader bias for ρ above about 0.5 and artefact below it.

### Gemini (2026-09-16; projection only, no per-essay dump)

Using β bracketed by the two calibrated graders and Δμ from the corpus:
- **ELL.** The observed 0.275 carries an artefact of 0.09–0.11 at ρ 0.65, 0.07–0.08 at ρ 0.75 and
  0.03 at ρ 0.90. That leaves about 0.16–0.24.
- **Economic.** The observed 0.163 carries 0.07–0.09 / 0.05–0.06 / 0.02, leaving about 0.08–0.14.

The analytic formula overstates the exact artefact by about 0.01 (see the floor).

### Item 5: the label-by-group contrasts (`out/label-check.json`)

- **(i) Constant label effect: PASSED.** A noisy reference (ρ 0.65) does not bias a within-essay
  group contrast when the label's effect does not depend on quality.
  - Bias of D_low: +0.001 (ELL) and +0.003 (disability) with nothing planted; +0.001 and +0.002 with
    a planted +0.10.
- **(ii) The label's effect does depend on quality, on Qwen.** On the real data the slope of
  (low − none) on H is −0.113 per level for Qwen. Per stratum, from 1 to 5–6: −0.24, −0.41, −0.57,
  −0.66, −0.65. Clipping alone produces about −0.005 in the same synthetic world (a scratch check,
  not committed), so this is the label pulling stronger essays further down, not a floor effect.
  Through the noisy reference, that biases D_low TOWARD FAVOURING the lower-mean group:
  - ELL: +0.038 / +0.023 / +0.007 (ρ 0.65 / 0.75 / 0.90, analytic; simulated +0.043 / +0.025 /
    +0.011)
  - disability: +0.050 / +0.030 / +0.009

  GPT-4.1-mini's slope is −0.024, and its implied biases are ≤ 0.011.
- **What this does to the label results (post hoc, `post_hoc_contrast_slopes`; the pre-registered
  verdicts of grader-attainment-groups are not re-cut):**
  - **Qwen D_low ELL** (+0.075, z 3.2) becomes z 1.6 / 2.2 / 2.9 (ρ 0.65 / 0.75 / 0.90), so it is
    not differential at ρ ≤ 0.75.
  - **Qwen D_low disability** (+0.105, z 4.2) becomes z 2.2 / 3.0 / 3.8.
  - **GPT-4.1-mini D_low economic** (+0.062, z 2.69) becomes 2.4 / 2.5 / 2.6.
  - **Qwen D_lowmid** has a slope of +0.082 per level, so its AGAINST readings are biased toward
    AGAINST. ELL goes from −0.079 to z −2.2 / −2.6 / −3.1; disability from −0.063 to −1.1 / −1.7 /
    −2.3; economic from −0.082 to −2.2 / −2.5 / −2.8.
  - **D_spread (high − low)**, the "uniform" headline, carries ≤ 0.02 of artefact and stays
    uniform.
  - **The direction of the placeholder-1 headline holds.** No corrected D_low turns AGAINST.
    But its "favouring, one model" differentials and the "low value costs those groups 0.06–0.08
    more" reading are each partly this artefact, and at ρ ≈ 0.65 most of them fall below the
    Bonferroni bar of 2.576.

So the claim that within-essay contrasts are immune to the noisy reference holds only for a label
effect that does not vary with quality. On GPT-4.1-mini it nearly holds. On Qwen it does not. The
original study's SCORE-CONFOUND control planted a quality-dependent penalty on the *human* score,
which its strata then removed. It could not see this, because there the human score was the truth.

### Amendment 3: the registered verdicts at the known reliability (`out/reliability-known.json`)

The reading was fixed in amendment 3 (commit 454f28a) before any of these numbers was written here.
`reliability_known.py` reads only the committed `out/` files. For the subset check it also reads the
corpus ids and the dumps' ids. Nothing in `out/results.json` or `out/label-check.json` was re-run.

**What the paper establishes** (Crossley et al. 2025, §3, p. 3):
- Every essay was read twice, double-blind, by expert raters, and every essay was adjudicated.
- Before adjudication the raters correlated r = .750 in both subsets. Weighted κ was .745 on the
  PERSUADE 2.0 subset (~13,000 essays) and .659 on the new essays (~12,000).
- The released column is described as "the average human assigned score". In the file it is an
  integer from 1 to 6, so it is a composite of the two reads, not their raw mean.

**The reliability of the released score:**

| reading | ρ | assumption |
| --- | --- | --- |
| lower bound | 0.75 | one rater. For parallel raters the inter-rater r is each rating's reliability. A score that uses two reads is not worse than one, unless adjudication adds error. |
| best estimate | 0.857 | Spearman–Brown 2(.75)/(1 + .75). This assumes adjudication is at least as good as averaging the two reads. |
| sensitivity (not a verdict) | 0.805 | an integer composite. A synthetic world (normal true score, two integer raters tuned to r = .750 on the corpus's spread) gives these reliabilities: raw mean of two 0.857, mean rounded half up 0.805, a third read on disagreement 0.805, mean rounded at random 0.766. An adjudicator who is better than one rater would sit above these. |

**Why κ and r differ, and why r is the one that matters here.**
- Quadratic-weighted κ is 2cov / (var₁ + var₂ + (m₁ − m₂)²). It falls below r when the two reading
  slots differ in mean or in spread.
- On the new essays κ/r = 0.88. With equal spreads that is a mean difference of about 0.53 SD between
  the first and second reads. On PERSUADE it is 0.12 SD.
- A level difference that is the same for every essay does not reorder essays, and adjudication then
  resolves it. The correction also calibrates the grader's mean on the analysed essays. So the
  classical-test-theory quantity is the correlation.
- Leniency that varies from rater to rater across essays already lowers r, so it is counted.

**Which subset the draw comes from.** The corpus does not mark the subset.
- The 4,005 essays with numeric ids are certainly PERSUADE 2.0. They are all of "Car-free cities"
  and "Does the electoral college work?", and every one has blank economic and disability fields.
  This matches the paper's 4,005 PERSUADE essays without those fields.
- The other 20,723 rows mix about 8,866 PERSUADE and about 11,829 new essays, and nothing in the
  file tells them apart.
- Of the 3,000-essay draw, 278 are identifiably PERSUADE and 2,722 cannot be attributed. The 278 have
  no economic or disability fields, so on those two axes the analysed essays are all from the mixed
  part.
- Both subsets report the same r (.750), so ρ is the same whichever subset an essay is from. The
  subsets do not need to be read separately for this correction. A per-subset reading would need
  the essays matched to the public PERSUADE 2.0 release by text. That was not done, because it adds
  a corpus and ρ does not depend on it.

**The corrected gap at the known reliability.** At ρ = 0.75 the values are the committed grid point.
At 0.857 and 0.805 they are linear interpolations of the committed neighbours. The interpolation error
is at most 0.0005 at 0.857, bounded by the grid's own curvature. The interval is the fixed-ρ 95%
bootstrap; "share" is the artefact as a fraction of the observed gap.

| model | axis | observed | ρ 0.75: corrected [95%] / share / verdict | ρ 0.857: corrected [95%] / share / verdict | ρ 0.805 (sensitivity): corrected / verdict |
| --- | --- | --- | --- | --- | --- |
| Qwen3-235B | ELL | −0.242 | −0.173 [−0.242, −0.109] / 29% / PARTLY-ARTEFACT | −0.210 [−0.273, −0.146] / 13% / NOT-ARTEFACT | −0.193 / NOT-ARTEFACT |
| Qwen3-235B | disability | −0.318 | −0.217 [−0.284, −0.160] / 32% / PARTLY-ARTEFACT | −0.268 [−0.334, −0.202] / 16% / NOT-ARTEFACT | −0.245 / PARTLY-ARTEFACT |
| Qwen3-235B | economic | −0.170 | −0.120 [−0.189, −0.046] / 30% / NOT-ARTEFACT | −0.147 [−0.224, −0.072] / 14% / NOT-ARTEFACT | −0.135 / NOT-ARTEFACT |
| Qwen3-235B | gender (F) | +0.031 | −0.002 [−0.071, +0.063] / — / UNRESOLVED | +0.014 [−0.058, +0.080] / — / UNRESOLVED | +0.007 / UNRESOLVED |
| GPT-4.1-mini | ELL | −0.205 | −0.149 [−0.199, −0.102] / 27% / PARTLY-ARTEFACT | −0.179 [−0.230, −0.130] / 13% / NOT-ARTEFACT | −0.166 / NOT-ARTEFACT |
| GPT-4.1-mini | disability | −0.295 | −0.212 [−0.269, −0.152] / 28% / PARTLY-ARTEFACT | −0.253 [−0.308, −0.201] / 14% / NOT-ARTEFACT | −0.234 / PARTLY-ARTEFACT |
| GPT-4.1-mini | economic | −0.135 | −0.095 [−0.161, −0.043] / 30% / NOT-ARTEFACT | −0.117 [−0.176, −0.056] / 13% / NOT-ARTEFACT | −0.107 / NOT-ARTEFACT |
| GPT-4.1-mini | gender (F) | +0.069 | +0.041 [−0.012, +0.094] / 41% / UNRESOLVED | +0.054 [+0.002, +0.102] / 22% / NOT-ARTEFACT | +0.048 / UNRESOLVED |

At 0.857 the two neighbours (0.85 and 0.90) give the same verdict in every cell, so the verdict there
does not depend on the interpolation. At 0.805 the neighbours (0.80 and 0.85) disagree on disability
(both models) and on GPT-4.1-mini gender. The interpolated reading is shown, and it is a
sensitivity only.

**Across models, per axis:**

| axis | ρ 0.75 (lower bound) | ρ 0.857 (best estimate) | ρ 0.805 (sensitivity) |
| --- | --- | --- | --- |
| ELL | PARTLY-ARTEFACT | **NOT-ARTEFACT** | NOT-ARTEFACT |
| disability | PARTLY-ARTEFACT | **NOT-ARTEFACT** | PARTLY-ARTEFACT |
| economic | NOT-ARTEFACT | **NOT-ARTEFACT** | NOT-ARTEFACT |
| gender | UNRESOLVED | UNRESOLVED / NOT-ARTEFACT | UNRESOLVED |

So at the reported human reliability:
- **The gap does not vanish.** At equal true quality, 0.15–0.17 (ELL) and 0.21–0.22 (disability)
  remains at the lower bound. At the best estimate it is 0.18–0.21 and 0.25–0.27.
- **The artefact is small.** It is 27–32% of the observed gap at 0.75 and 13–16% at 0.857.
- **The ELL and disability verdict depends on the adjudication assumption.** At the best estimate it
  is NOT-ARTEFACT: the observed gap is inside the corrected interval. At the lower bound, and for
  disability at the integer-composite value, it is PARTLY-ARTEFACT: real, but smaller than observed.
- **The break-even reliability is far outside the range.** It is 0.49–0.52, against a known lower
  bound of 0.75.

The two other corrections attribute slightly more to the artefact. At 0.857 they read PARTLY-ARTEFACT
on Qwen ELL and disability and on GPT-4.1-mini disability, and NOT-ARTEFACT elsewhere. None reads
ARTEFACT-EXPLAINS-IT. GPT-4.1-mini's small female advantage resolves from zero at the best estimate
(+0.054 [+0.002, +0.102]).

**Gemini (projection only, interpolated between the committed analytic 0.75 and 0.90 values).**
- ELL: the artefact is 0.038–0.046 at 0.857, leaving about 0.23 of the observed 0.275.
- Economic: it is 0.029–0.035, leaving about 0.13 of 0.163.

**Label-by-group contrasts at the known reliability.** The implied bias is evaluated exactly with
the committed analytic formula, which reproduces the committed values to 1e-9. Corrected
z = (measured − bias) / SD, with SD the bootstrap SD that `grader-attainment-groups`' rule divides by.
The label is that rule (Bonferroni z* = 2.576), applied post hoc as in item 5. The registered verdicts
of `grader-attainment-groups` are not re-cut.

| model | contrast | axis | measured (z) | ρ 0.75: bias / z / rule | ρ 0.857: bias / z / rule | ρ 0.805: z |
| --- | --- | --- | --- | --- | --- | --- |
| Qwen | D_low | ELL | +0.075 (3.20) | +0.023 / 2.24 / UNIFORM | +0.011 / **2.73** / FAVOURING | 2.51 |
| Qwen | D_low | disability | +0.105 (4.20) | +0.030 / 3.01 / FAVOURING | +0.015 / **3.62** / FAVOURING | 3.35 |
| Qwen | D_low | economic | +0.024 (0.88) | +0.017 / 0.26 / UNIFORM | +0.008 / 0.58 / UNIFORM | 0.44 |
| Qwen | D_lowmid | ELL | −0.079 (−3.32) | −0.016 / −2.63 / AGAINST | −0.008 / **−2.98** / AGAINST | −2.82 |
| Qwen | D_lowmid | disability | −0.063 (−2.60) | −0.022 / −1.72 / UNIFORM | −0.011 / −2.17 / UNIFORM | −1.97 |
| Qwen | D_lowmid | economic | −0.082 (−2.93) | −0.012 / −2.49 / UNDERPOWERED | −0.006 / **−2.72** / AGAINST | −2.62 |
| GPT-4.1-mini | D_low | ELL | +0.034 (1.77) | +0.005 / 1.52 / UNIFORM | +0.002 / 1.65 / UNIFORM | 1.59 |
| GPT-4.1-mini | D_low | disability | +0.023 (1.16) | +0.006 / 0.84 / UNIFORM | +0.003 / 1.00 / UNIFORM | 0.93 |
| GPT-4.1-mini | D_low | economic | +0.062 (2.69) | +0.004 / 2.53 / UNIFORM | +0.002 / **2.61** / FAVOURING | 2.57 |

Read at the known reliability, the label-by-group results move back toward what was measured:
- **At the best estimate (0.857), all three favouring differentials of the registered headline still
  clear the Bonferroni bar.** These are Qwen ELL and disability and GPT-4.1-mini economic. GPT's
  clears only just, at 2.61. So DIFFERENTIAL-ONE-MODEL reads unchanged.
- **At the lower bound (0.75), only Qwen disability clears.**
- **Against the mid label**, Qwen ELL clears at both values (z −2.6 / −3.0). Economic clears only at
  0.857 (−2.7). Disability clears at neither (−1.7 / −2.2).
- **The artefact in these contrasts is ≤ 0.03 at 0.75 and ≤ 0.014 at 0.857.**

### Reconciling with the data's own bound (0.30–0.37)

The triad estimate is ρ_H = corr(H, Q) corr(H, G) / corr(Q, G) = 0.518 × 0.547 / 0.761 = 0.37
(0.30 within group). It assumes the two graders' errors are independent of each other. The paper
puts ρ_H at 0.75 or more, so the assumption fails, and by a lot:
- **The graders agree far more than independent errors allow.** If ρ_H = 0.857 and their errors were
  independent, the two graders would correlate corr(H, Q) corr(H, G) / ρ_H = 0.33 (0.38 at
  ρ_H = 0.75). They correlate 0.76.
- **Most of each grader's variance is not the raters' true score.** The share that is, ρ_Q =
  corr(H, Q)² / ρ_H, is 0.31 for Qwen and 0.35 for GPT-4.1-mini at 0.857 (0.36 and 0.40 at 0.75).
  The other two-thirds is shared with the other grader beyond the human's true score, or is noise.
- **About 0.4 of their 0.76 correlation is common variance the human score does not contain.**

What this implies:
1. **The triad bound is not a reliability estimate here.** Its low value measures how much the two
   LLMs share, not how noisy the human is. The scenario in which matching explains the whole gap
   (ρ ≈ 0.5) is ruled out by the raters' own agreement, not by this bound.
2. **Two LLM graders agreeing is not evidence that either is right.** Their shared component is
   large, and an ensemble of the two would not average it away.
3. **The shared component is where the group gap can live.** Whatever the two LLMs share beyond the
   raters' true score, such as the surface-form halo seen in the 2026-09-16 probe, is the natural
   carrier of a gap at equal true quality. A gap of 0.15–0.27 that survives the correction is what one
   would expect if part of that shared component is group-correlated. This is consistent with the
   probe; it does not identify the mechanism.
4. **The remaining caveat is the reference, not its noise.** The correction assumes the human error
   is independent of group. If the raters, who all had anti-bias training, were more lenient to focal
   groups at equal quality, an unbiased grader would also show a negative gap. Rater DIF is not
   corrected here and is the open question. If the raters were harsher to focal groups, the grader's
   bias would be larger than reported.

## What this means for Paper VI (amendment 3, at the known reliability)

This supersedes the section after it, which was written for the assumed bracket and has already been
applied (corrections-1 and corrections-2).

**Applied 2026-10-06 in corrections-4** (`research/readiness/ai-grader-reliability-2026/corrections-4.md`),
with one change of wording throughout: the released score is not called "the adjudicated score". The data
paper calls it "the average human assigned score", so the paper and its records say "a two-read, adjudicated
human score" or quote that phrase. Rater neutrality is stated as the open question in the abstract, §2.3,
§5.9, §6.4 and the release.

**The headline changes.**
- **The assumption is replaced.** The paper says "an assumed human reliability of 0.65–0.90" and
  rater agreement "in sources not yet verified". Both go. The reliability is now known from the data
  paper: 0.75 at least, about 0.86 as best estimate.
- **The remaining gap is narrower and higher.** It moves from 0.11–0.28 to **0.15–0.27 of a level at
  equal true quality**: ELL 0.15–0.21, disability 0.21–0.27, economic 0.10–0.15.
- **The remaining share is larger.** It moves from "about 70% at 0.75 and about half at 0.65" to
  **68–73% at 0.75 and 84–87% at 0.86**.
- **The vanishing condition is ruled out.** "It would vanish only near 0.5, which the data do not
  exclude" now reads: the raters' own agreement excludes it.
- **The "one rater" premise was wrong.** ASAP 2.0's score is not one rater's; it is two
  double-blind reads with full adjudication. "Single-rater", "one human rater per essay" and
  "matching on one noisy rating" are all incorrect for ASAP 2.0.
- **The label-by-group z values change**, as in the table above.
- `cooling_off.last_headline_correction` is set to 2026-10-06 in the same commit. It already held
  that date; a comment records this correction.

**The open question moves.** It is no longer the human score's noise. It is whether the human
raters are themselves group-neutral (rater DIF). A double-rated reference already exists, so "to be
confirmed against a double-rated reference" becomes "measured against human raters whose own group
neutrality is not tested here".

### Where the paper and its records state the bracket or the unverified reliability

Line numbers are at commit 7ddaa2a (this branch's base). Another agent is re-cutting the article, so
match the quoted text, not the line number. None of these files is edited here.

| # | file:line | what it says now |
| --- | --- | --- |
| 1 | `research/article/attainment-bias-in-llm-grading.md:62-65` (abstract) | D_lowmid "corrected at reliability 0.65–0.75, only the English-learner difference stays beyond the multiple-testing bar, and only from 0.75" |
| 2 | `research/article/attainment-bias-in-llm-grading.md:66-78` (abstract) | the gap "under an assumed human reliability of 0.65–0.90 (… in sources not yet verified, at about 0.66–0.75), 0.11 to 0.28 … about 70% … about half at 0.65 … about 0.5, a level the data's own bound … does not exclude … to be confirmed against a double-rated reference" |
| 3 | `research/article/attainment-bias-in-llm-grading.md:79` (abstract scope) | "one human rater per essay" |
| 4 | `research/article/attainment-bias-in-llm-grading.md:222-226` (contribution 7) | "(0.11–0.28 … against a projected 0.01–0.07), conditional on the human score's reliability" |
| 5 | `research/article/attainment-bias-in-llm-grading.md:341` (§2.3, fairness background) | the same D_lowmid parenthetical as #1 |
| 6 | `research/article/attainment-bias-in-llm-grading.md:346-355` (§2.3) | "At equal single-rater human score … at human reliability 0.65–0.90 … 0.11–0.22 … 0.15–0.28 … about 70% … near 0.5, which the two graders' agreement … does not rule out" |
| 7 | `research/article/attainment-bias-in-llm-grading.md:562` (§4.4 corpus table) | ASAP 2.0 "Human raters per item … 1" |
| 8 | `research/article/attainment-bias-in-llm-grading.md:1217-1220` (§5.9 table rows) | "equal single-rater human score"; rows at reliability 0.65 / 0.75 / 0.90 |
| 9 | `research/article/attainment-bias-in-llm-grading.md:1237-1255` (§5.9, "Matching on one noisy rating", including the label-by-group correction) | "equal score from one rater … about 0.5 … does not rule that out; a double-rated reference would settle it … At reliability 0.65–0.75 … z 1.6–2.2 … z 2.2–3.0 … z 2.4–2.6 … at reliability 0.65 no favoring difference clears the bar … z 2.2 at 0.65 … z 1.1–2.3" |
| 10 | `research/article/attainment-bias-in-llm-grading.md:1345-1350` (§6.4 practice point 2) | "0.11–0.28 … unless one human rating's reliability is below about 0.6; near 0.5 the gap vanishes … against a double-rated or latent reference, not one rater's score" |
| 11 | `research/article/attainment-bias-in-llm-grading.md:1405-1407` (§7 limitations) | "one human rater per essay (which also defines "equal work", so the grader's unlabeled group gap at equal true quality is conditional on that rating's reliability)" |
| 12 | `research/article/attainment-bias-in-llm-grading.md:1445-1447` (§8 conclusion) | "provided one human rating is more reliable than about 0.6 (below about 0.5 the gap vanishes altogether)" |
| 13 | `research/article/attainment-bias-in-llm-grading.md:1535-1537` (specialist reviews still to come) | "observed at equal single-rater score and corrected … under a reliability bracket; whether a double-rated or latent reference is needed" |
| 14 | `research/article/attainment-bias-in-llm-grading.md:1644` (placeholder table, row 1) | "corrected … 0.11–0.28 … reliability 0.65–0.90" |
| 15 | `research/wiki/research/releases/ai-grader-reliability-2026/1.0.0.yaml:299-302, 315-316` (dataset `asap2`) | "one holistic human score (1-6) each"; "One rater per essay, so no human ceiling" |
| 16 | `…/1.0.0.yaml:950-951, 966-970` (analysis `asap2-matching-artefact`) | title "equal single-rater human score … one noisy rating"; "reliability of the one human score bracketed at 0.65-0.90 … because the corpus has no rater-level field" |
| 17 | `…/1.0.0.yaml:1041-1045` (evidence note) | "0.11-0.28 … for reliability 0.65-0.90; fully explained only near 0.5" |
| 18 | `…/1.0.0.yaml:1211-1223` (interpretation) | D_lowmid "0.65–0.75 … only from 0.75"; "single-rater human score … 0.11-0.28 … 0.65-0.90 … about 0.5, which the data do not rule out … to be confirmed against a double-rated reference" |
| 19 | `…/1.0.0.yaml:1409-1411` (limitation THE DEMOGRAPHIC TEST IS NARROW) | "one human rater per essay, which also defines "equal work"" |
| 20 | `…/1.0.0.yaml:1419-1427` (same limitation) | ""Equal work" is equal score from one human rater … 0.11-0.28 … 0.65-0.90; at about 0.5 it would vanish … 0.01-0.05" |
| 21 | `research/wiki/observations/lazuli-grader-asap2-2026.yaml:46-53` (claim link note) | "equal single-rater score … 0.11-0.28 … 0.65-0.90" |
| 22 | `…/lazuli-grader-asap2-2026.yaml:179` (label-by-group result model) | "(at equal single-rater score; …)" |
| 23 | `…/lazuli-grader-asap2-2026.yaml:190-197` (label-by-group interpretation) | "one noisy rating"; D_lowmid "0.65–0.75 … only from 0.75"; "equal single-rater score … 0.11-0.28 … 0.65-0.90" |
| 24 | `…/lazuli-grader-asap2-2026.yaml:226` (label-by-group observability_notes) | "One human rater per essay." |
| 25 | `…/lazuli-grader-asap2-2026.yaml:243, 247, 250` (no-label-gap outcome) | "equal score from one human rater"; "matched on one noisy human score"; "fixed human reliability 0.65-0.90" |
| 26 | `…/lazuli-grader-asap2-2026.yaml:266-281` (no-label-gap result model) | rows at 0.65 / 0.75 / 0.90; "the triad bound … 0.30-0.37"; RHO-DEPENDENT; "z 1.6 / 2.2 / 2.9 … z 2.2 / 3.0 / 3.8"; "estimate above … at reliability 0.75" |
| 27 | `…/lazuli-grader-asap2-2026.yaml:283-294` (no-label-gap interpretation) | "THE UNVERIFIED REPORTS OF RATER AGREEMENT … about 70% … 0.11-0.28 … 0.65-0.90 … near reliability 0.5, which the data do not exclude … double-rated reference" |
| 28 | `…/lazuli-grader-asap2-2026.yaml:296-301` (moderator) | "reliability of the one human score … reaches zero near 0.5" |
| 29 | `…/lazuli-grader-asap2-2026.yaml:311-314` (observability_notes) | "Reliability is bracketed, not measured: the corpus has no rater-level field." |
| 30 | `research/wiki/claims/showing-a-grader-a-learners-prior-performance-biases-the-grade.md:45` (K1 fairness paragraph) | "one noisy human score"; D_lowmid "0.65–0.75 … only from 0.75"; "equal single-rater human score … one noisy rating, 0.11–0.28 … 0.65–0.90, and it would vanish only near 0.5 … to be confirmed against a double-rated reference … one rater and two models" |
| 31 | `research/readiness/ai-grader-reliability-2026/readiness.yaml:36` (assessment-fairness review request) | "equal single-rater score … 0.11-0.28 … for human reliability 0.65-0.90" |

Not in scope: release `:1153` and `:1355-1361` and the Mohler and JorGPT "single-rater" lines. Those
are about other corpora.

### Replacement wording

**#1 and #5** (abstract and §2.3, the D_lowmid parenthetical). Replace "corrected at reliability
0.65–0.75, only the English-learner difference stays beyond [clears] the multiple-testing bar, and
only from 0.75" with:

> corrected at the human score's reported reliability (0.75–0.86), the English-learner difference
> stays beyond the multiple-testing bar, the economic one only at 0.86, and the disability one at
> neither

**#2** (abstract). Replace from "The grader's own group gap, with no label at all, is larger." to "…to
be confirmed against a double-rated reference." with:

> The grader's own group gap, with no label at all, is larger. At equal human score it marks English
> learners' and disability-identified students' essays 0.21 to 0.32 of a level below their peers'.
> Part of any such gap is an artifact of matching on a noisy score. ASAP 2.0's scores come from two
> double-blind expert reads with full adjudication, and the raters correlated at .75 before
> adjudication. Corrected at the reliability that implies (0.75, or about 0.86 for a two-read score),
> 0.15 to 0.27 of a level remains at equal true quality: 68–73% of the observed gap at 0.75, and
> 84–87% at 0.86. It would vanish only if the score's reliability were about 0.5, which the raters'
> agreement rules out. An earlier probe on another model showed that learner-typical surface errors
> can lower content scores. So the attainment edge is not shown to launder group disadvantage at these
> sizes. Its cost falls on any student given a false low label, and a larger fairness problem is one
> the grader has without being told anything. That problem is measured against human raters whose
> own group neutrality is not tested here.

**#3** (abstract scope). Replace "one human rater per essay" with "one adjudicated human score per
essay".

**#4** (contribution 7). Replace "(0.11–0.28 of a level at equal true quality, against a projected
0.01–0.07), conditional on the human score's reliability" with:

> (0.15–0.27 of a level at equal true quality at the human score's reported reliability, against a
> projected 0.01–0.07)

**#6** (§2.3). Replace from "At equal single-rater human score, the same graders mark …" to "…one
possible route to such a gap." with:

> At equal human score, the same graders mark English learners' and disability-identified students'
> essays 0.21–0.32 of a level below their peers'. Matching on a noisy score produces some gap of this
> sign even for an unbiased grader, because the groups' mean scores differ (2.53 against 3.00 for
> English learners, 2.38 against 3.01 for disability). ASAP 2.0's scores come from two double-blind
> expert reads with full adjudication. Before adjudication the raters correlated at r = .75 in both
> parts of the corpus (weighted κ .745 and .659; Crossley et al. 2025). So the score's reliability is
> at least 0.75, and about 0.86 if adjudication is as good as averaging the two reads. Corrected at
> those values (`studies/measurement/grader-matching-artefact/`), the gap at equal true quality is
> 0.15–0.21 for English learners and 0.21–0.27 for disability-identified students, 68–87% of the
> observed gap. It would be fully explained only at reliability near 0.5, which the raters' agreement
> rules out. An earlier probe showed that surface form can leak into content judgments, one possible
> route to such a gap.

**#7** (§4.4 table). Replace the ASAP 2.0 cell "1" in "Human raters per item" with:

> 2, double-blind, adjudicated (one score released)

**#8** (§5.9 table). In the observed row, replace "equal single-rater human score" with "equal
(adjudicated) human score". Replace the three rows at 0.65 / 0.75 / 0.90 with:

| | Qwen | GPT-4.1-mini |
| --- | --- | --- |
| The same gap at equal true quality, reliability 0.75 (one rater, lower bound): ELL / economic / disability | −0.17 / −0.12 / −0.22 | −0.15 / −0.10 / −0.21 |
| The same gap at equal true quality, reliability 0.86 (two reads, best estimate) | −0.21 / −0.15 / −0.27 | −0.18 / −0.12 / −0.25 |

**#9** (§5.9 paragraph). Replace from "**Matching on one noisy rating.** "Equal human score" here
means equal score from one rater." to "…No corrected difference turns against the focal group." with:

> **Matching on a noisy score.** "Equal human score" means equal released score. That score is
> adjudicated from two double-blind expert reads, which correlated at r = .75 before adjudication
> (Crossley et al. 2025, p. 3), so its reliability is at least 0.75 and about 0.86 if adjudication is
> as good as averaging the two. When two groups differ in mean score and the matching score is noisy,
> focal essays in the same stratum have lower true quality on average, so even an unbiased grader shows
> a negative residual gap. Correcting for that (`studies/measurement/grader-matching-artefact/`,
> pre-registered, detection floor passed, read at the known reliability by amendment 3) leaves the rows
> above at equal true quality: 68–73% of the observed gap at 0.75 and 84–87% at 0.86. The pre-registered
> verdict is PARTLY-ARTEFACT on English learners and disability at 0.75, and NOT-ARTEFACT on all three
> axes at 0.86. The gap would be fully explained only if the score's reliability were about 0.5
> (break-even 0.49–0.52), which the raters' agreement rules out. The two graders' agreement with each
> other implies a reliability of only 0.30–0.37. That is far below the raters' figure, because the two
> LLMs share a large component that is not in the human score (they correlate 0.76 with each other and
> 0.52–0.55 with the human). The gap at equal true quality is what that shared component would produce
> if part of it tracks group. The correction cannot detect raters who are themselves more lenient or
> harsher to a group.
>
> The same check found that the label-by-group contrasts are not wholly immune. On Qwen the low label
> costs stronger essays more (−0.11 per level of human score). Through the noisy matching score, its
> favoring differences and its against-the-group readings against the mid label are each inflated, by
> at most 0.03 at 0.75 and 0.014 at 0.86. At 0.86 every favoring difference still clears the Bonferroni
> bar: Qwen's English-learner difference at z 2.7 (from 3.2), disability 3.6 (from 4.2), and
> GPT-4.1-mini's economic difference 2.6 (from 2.7). At 0.75 only Qwen's disability difference does
> (3.0), with English learners at 2.2 and GPT-4.1-mini's economic at 2.5. Against the mid label, Qwen's
> English-learner difference clears at both values (z 2.6–3.0), its economic one only at 0.86 (2.5–2.7),
> and its disability one at neither (1.7–2.2). GPT-4.1-mini's slope is a fifth as steep, and the
> high-versus-low spread carries at most 0.02 of the artifact. This check was added after the planned
> analysis. It is reported, and the pre-registered verdicts above are not re-cut. No corrected
> difference turns against the focal group.

**#10** (§6.4 practice point 2). Replace from "Corrected for matching on one noisy rating, 0.11–0.28 …"
to "…not one rater's score." with:

> Corrected for matching on a noisy human score, 0.15–0.27 of a level remains at the corpus's reported
> rater reliability. That is more than the attainment label would add. Audit residuals by group as
> well, against a reference whose reliability is measured, and check whether the human raters are
> themselves group-neutral.

**#11** (§7). Replace "one human rater per essay (which also defines "equal work", so the grader's
unlabeled group gap at equal true quality is conditional on that rating's reliability)" with:

> one adjudicated human score per essay (which also defines "equal work"; the grader's unlabeled group
> gap at equal true quality assumes the raters' errors are independent of group, which is not tested)

**#12** (§8). Replace "provided one human rating is more reliable than about 0.6 (below about 0.5 the
gap vanishes altogether)" with:

> at the human score's reported reliability (0.15–0.27 of a level at equal true quality)

**#13** (specialist reviews). Replace "observed at equal single-rater score and corrected for matching
on one noisy rating under a reliability bracket; whether a double-rated or latent reference is needed
before it is called differential functioning" with:

> observed at equal adjudicated score and corrected for matching on a noisy score at the data paper's
> rater reliability; whether rater DIF has to be excluded before it is called differential functioning

**#14** (placeholder row 1). Replace "(corrected 2026-10-06 for matching on one noisy rating: 0.11–0.28
of a level at equal true quality, reliability 0.65–0.90)" with:

> (corrected 2026-10-06 for matching on a noisy score: 0.15–0.27 of a level at equal true quality at
> the reported rater reliability, 0.75–0.86)

**#15** (release dataset `asap2`). In the title, replace "one holistic human score (1-6) each" with
"one adjudicated holistic human score (1-6) each, from two double-blind expert reads". In the note,
replace "One rater per essay, so no human ceiling." with:

> Two double-blind expert reads per essay with 100 percent adjudication; only the adjudicated score is
> released, so no per-item human ceiling can be computed here. The data paper reports pre-adjudication
> agreement of weighted kappa .745 / .659 and r .750 (p. 3).

**#16** (release analysis `asap2-matching-artefact`).
- In the title, replace "at equal single-rater human score" with "at equal human score" and "one noisy
  rating" with "a noisy human score".
- In `detail`, replace "reliability of the one human score bracketed at 0.65-0.90 and reported on a
  grid, because the corpus has no rater-level field" with:

  > reliability of the human score reported on a pre-registered grid (0.60-0.95), read under
  > amendment 3 at the data paper's figures: 0.75 (one rater, r = .750) and 0.857 (Spearman-Brown,
  > two reads); `reliability_known.py` does that reading from the committed outputs

- Update `code.commit` to the commit that adds `reliability_known.py`.

**#17** (release evidence note). Replace with:

> The unlabeled grader gap corrected for matching on a noisy score: 0.15-0.27 of a level remains at
> equal true quality at the reported rater reliability (0.75-0.86); fully explained only near 0.5,
> which the raters' agreement rules out.

**#18** (release interpretation).
- Apply the D_lowmid parenthetical as in #1.
- Replace from "The graders' own unlabeled gap against English learners …" to "…confirmed against a
  double-rated reference." with:

  > The graders' own unlabeled gap against English learners and disability-identified students is
  > 0.21-0.32 of a level at equal human score. Part of that is the artefact of matching on a noisy score,
  > and 0.15-0.27 remains at equal true quality at the rater reliability the data paper reports
  > (0.75-0.86). It would be fully explained only near 0.5, which that agreement rules out. So it is a
  > fairness problem larger than the label's, measured against human raters whose own group neutrality
  > is not tested.

**#19** (release limitation). Replace "one human rater per essay, which also defines "equal work"" with
"one adjudicated human score per essay, which also defines "equal work"".

**#20** (same limitation). Replace from ""Equal work" is equal score from one human rater:" to "…at about
0.5 it would vanish" with:

> "Equal work" is equal adjudicated human score: the graders' unlabeled group gap of 0.21-0.32 at that
> score is partly an artefact of matching on a noisy score, and 0.15-0.27 remains at equal true quality
> at the data paper's rater reliability (0.75 for one rater, about 0.86 for two reads); it would vanish
> only at about 0.5. The correction assumes rater error is independent of group; rater DIF is not
> tested

Then replace "carry 0.01-0.05 of the same artefact" with "carry up to 0.03 (at 0.75) or 0.015 (at 0.86)
of the same artefact".

**#21** (observation claim note). Replace "at equal single-rater score, of which 0.11-0.28 remains at
equal true quality for human reliability 0.65-0.90" with:

> at equal human score, of which 0.15-0.27 remains at equal true quality at the reported rater
> reliability (0.75-0.86)

**#22.** Replace "(at equal single-rater score;" with "(at equal human score;".

**#23.**
- Replace "one noisy rating" with "a noisy human score".
- Apply the D_lowmid parenthetical as in #1.
- Replace "at equal single-rater score, of which 0.11-0.28 remains at equal true quality for human
  reliability 0.65-0.90" as in #21.

**#24.** Replace "One human rater per essay." with "One adjudicated human score per essay (two
double-blind reads)."

**#25.**
- Replace "at equal score from one human rater" with "at equal human score".
- Replace "matched on one noisy human score" with "matched on a noisy human score".
- Replace "at fixed human reliability 0.65-0.90" with "at fixed human reliability on a pre-registered
  grid, read at 0.75 and 0.857 (amendment 3)".

**#26** (result `model`). Replace the 0.65 / 0.75 / 0.90 rows and the verdict sentence with:

> Corrected at reliability 0.75 / 0.857 (the data paper's one-rater figure and its two-read
> Spearman-Brown value; 0.857 interpolated between committed grid points), Qwen: ELL -0.173 / -0.210,
> disability -0.217 / -0.268, economic -0.120 / -0.147; GPT-4.1-mini: ELL -0.149 / -0.179, disability
> -0.212 / -0.253, economic -0.095 / -0.117. Verdict, both models: PARTLY-ARTEFACT on ELL and
> disability and NOT-ARTEFACT on economic at 0.75; NOT-ARTEFACT on all three at 0.857. Break-even
> reliability 0.49-0.52. The triad bound from the two graders' agreement, 0.30-0.37, is far below the
> raters' own figure because the two LLMs share error. At 0.75 / 0.857, Qwen's ELL D_low has z
> 2.2 / 2.7 (was 3.2) and disability z 3.0 / 3.6 (was 4.2).

Keep "The estimate above is Qwen's ELL corrected gap at reliability 0.75 (the lower bound)" and the
estimate and interval as they are.

**#27** (interpretation). Replace with:

> PART OF THE UNLABELED GROUP GAP IS THE MATCHING SCORE'S NOISE; MOST IS NOT. Matched on a noisy score,
> an unbiased grader would also mark lower-mean groups lower. Corrected at the rater reliability the
> data paper reports, 68-73% of the observed gap remains at 0.75 and 84-87% at 0.857: 0.15-0.27 of a
> level, larger than the 0.01-0.07 the label would add by projection. It would vanish only near
> reliability 0.5, which the raters' agreement (r = .75) rules out. What is not tested is whether the
> raters themselves are group-neutral. The label-by-group contrasts are not wholly immune: on Qwen part
> of the favouring difference is the same artefact (at most 0.03 at 0.75); the high-versus-low spread
> carries at most 0.02 of it.

**#28** (moderator). Replace "reliability of the one human score" with "reliability of the human
score". Replace "and reaches zero near 0.5" with:

> and reaches zero near 0.5; the data paper puts it at 0.75 or above

**#29.** Replace "Reliability is bracketed, not measured: the corpus has no rater-level field." with:

> The corpus has no rater-level field; the reliability is taken from the data paper (pre-adjudication
> r = .750, p. 3), at 0.75 and 0.857.

**#30** (K1 claim page).
- Replace "one noisy human score" with "a noisy human score".
- Apply the D_lowmid parenthetical as in #1.
- Replace from "The grader's own gap with no label at all is 0.21–0.32 …" to "…to be confirmed against
  a double-rated reference." with:

  > The grader's own gap with no label at all is 0.21–0.32 of a level against English learners and
  > disability-identified students at equal human score. Corrected for matching on a noisy score, 0.15–0.27
  > remains at equal true quality at the rater reliability the corpus's data paper reports (0.75–0.86),
  > and it would vanish only near 0.5. That is a fairness problem larger than the label's, measured
  > against human raters whose own group neutrality is not tested.

- Replace "one corpus, one rater and two models" with "one corpus, one adjudicated score per essay and
  two models".

**#31** (readiness review request). Replace "at equal single-rater score is larger, 0.11-0.28 at equal
true quality for human reliability 0.65-0.90" with:

> at equal human score is larger, 0.15-0.27 at equal true quality at the data paper's rater
> reliability (0.75-0.86)

Unchanged:
- the observed gaps (0.21–0.32);
- the projected deployment gap (0.01–0.07);
- the DIFFERENTIAL-ONE-MODEL verdict;
- "the attainment edge is not shown to launder group disadvantage".

## What this means for Paper VI (2026-10-06, under the assumed bracket; applied in corrections-1 and -2, superseded above)

1. **Report "0.21–0.32 at equal human score" as an observed, single-rater-matched gap.**
   - **The grader-bias share.** At the documented level of human agreement (ρ 0.65–0.90), the
     share attributable to the grader at equal true quality is:
     - ELL: 0.11–0.22
     - disability: 0.15–0.28
     - economic: 0.07–0.16

     About 30% of the observed gap (27–32%) is matching artefact at ρ 0.75.
   - **The gap does not vanish in the bracket.** It vanishes only if one human rating's
     reliability is about 0.5, and the data's own triad bound (0.30–0.37, biased down) does not
     exclude that.
   - **The comparison with the label still holds.** "Larger than the label would add" holds at
     every ρ above about 0.6: 0.08+ against the projected 0.01–0.07 (at 0.55 Qwen ELL is 0.05,
     below it; corrected 2026-10-06 from "above about 0.55", scope-audit-2 H15c).
2. **"The larger fairness problem is one the grader has without being told anything"** is
   supported for ρ ≥ 0.65 and needs that condition stated. "Traced to surface features" stays
   "shown possible by a probe" (H15).
3. **The label-by-group results are not wholly immune.**
   - On Qwen the label's effect depends on essay quality, so its favouring D_low and AGAINST
     D_lowmid are each inflated by 0.01–0.05 through the same noisy reference.
   - The sign of the headline (nothing falls harder on a focal group) and the uniform high-versus-low
     spread are unaffected.
4. **What would close it.** A second, independent human rating on a few hundred essays, or the
   data paper's inter-rater statistics, would replace the bracket with a number. The psychometrician
   review H15 asks for should see this table.
5. **Headline correction.** The abstract's number changes from an observed gap to an equal-true-score
   range with its reliability condition, so `cooling_off.last_headline_correction` is set in the
   readiness record in the same commit.

### Replacement wording (SUPERSEDED: proposed for the redraft, kept as the record of the proposal)

> **Superseded 2026-10-06.** This was the wording proposed when the study finished. The article
> (`research/article/attainment-bias-in-llm-grading.md`) now carries its own, corrected wording,
> which differs from the proposal below in substance: the share of the gap that remains is "about
> 70% at reliability 0.75 and about half at 0.65", "larger than the label would add" holds only
> for a human rating more reliable than about 0.6 (not 0.5), and the label-by-group differences
> are placed on their models (corrections-1 and corrections-2 in
> `research/readiness/ai-grader-reliability-2026/`). Quote the article, not this section.


**Abstract**, replacing "The grader's own group gap, with no label at all, is larger: … is one the
grader has without being told anything." with:

> The grader's own group gap, with no label at all, is larger. At equal single-rater human score
> it marks English learners' and disability-identified students' essays 0.21 to 0.32 of a level
> below their peers'. Part of any such gap is an artefact of matching on one noisy rating. Corrected
> for it at the human agreement these corpora report (reliability 0.65–0.90), 0.11 to 0.28 of a level
> remains at equal true quality, about 70% of the observed gap. It would vanish only if one
> human rating were no more reliable than about 0.5. An earlier probe on another model showed that
> learner-typical surface errors can lower content scores. So the attainment edge is not shown to
> launder group disadvantage at these sizes. Its cost falls on any student given a false low label,
> and a larger candidate fairness problem is one the grader has without being told anything, to be
> confirmed against a double-rated reference.

**§2.3**, replacing "It sits beside a larger gap that needs no label at all: … a different route to
the same kind of harm." with:

> It sits beside a larger gap that needs no label at all. At equal single-rater human score, the same
> graders mark English learners' and disability-identified students' essays 0.21–0.32 of a level
> below their peers'. Matching on one noisy rating produces some gap of this sign even for an unbiased
> grader, because the groups' mean scores differ (2.53 against 3.00 for English learners, 2.38 against
> 3.01 for disability). Corrected for that at human reliability 0.65–0.90
> (`studies/measurement/grader-matching-artefact/`), the gap at equal true quality is 0.11–0.22 for
> English learners and 0.15–0.28 for disability-identified students, about 70% of the
> observed gap at reliability 0.75. It would be fully explained only at reliability near 0.5, which
> the two graders' agreement with each other does not rule out. An earlier probe showed that surface
> form can leak into content judgments, one possible route to such a gap.

And replacing "The fairness risk of attainment context is real, … not one concentrated on a protected
group." with:

> The fairness risk of attainment context is real. On this evidence it is a cost borne by any learner
> given a false low label, not one concentrated on a protected group. Where the label's effect
> differed by group it favoured the focal group, and on Qwen part of that difference is itself an
> artefact of the noisy matching score, because its low label costs stronger essays more.

**§5.9 table row**, "No-label residual gap …": keep the observed values. Add a row "At equal true
quality (reliability 0.65 / 0.75 / 0.90)" with these values:

| axis | Qwen | GPT-4.1-mini |
| --- | --- | --- |
| ELL | −0.12 / −0.17 / −0.22 | −0.11 / −0.15 / −0.19 |
| economic | −0.08 / −0.12 / −0.16 | −0.07 / −0.10 / −0.12 |
| disability | −0.15 / −0.22 / −0.28 | −0.16 / −0.21 / −0.27 |

**§6.4 practice point 2**, replacing "both graders tested, and a third in an earlier run, mark …
that gap is the larger fairness problem." with:

> both graders tested mark English learners' and disability-identified students' essays below their
> peers' at equal human score without being told anything. Corrected for matching on one noisy
> rating, 0.11–0.28 of a level remains, more than the attainment label would add, unless one human
> rating's reliability is as low as about 0.5. Audit residuals by group as well, and against a
> double-rated or latent reference, not one rater's score.

**Contribution 7**, replacing "is several times larger than anything the label would add" with "is
larger than anything the label would add (0.11–0.28 of a level at equal true quality, against a
projected 0.01–0.07), conditional on the human score's reliability".

**§8**, replacing "while the grader's own group gap, with no label at all, was larger than anything
the label would add" with "while the grader's own group gap, with no label at all, was larger than
anything the label would add, provided one human rating is more reliable than about 0.5".
