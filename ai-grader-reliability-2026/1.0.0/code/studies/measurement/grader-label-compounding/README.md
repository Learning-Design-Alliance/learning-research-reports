# Does the grader's learner-context edge compound? (Paper VI, placeholder 4)

**Status: RUN 2026-10-05.** Pre-registered at a3647f5, before the floor ran and before any real parameter was fitted; floor revisions at dc32491 and 0060add, before the real-parameter simulation.
The design, the estimands, the verdict strings and their thresholds are in the docstring of
`compounding.py`, which is the primary record. Results go below the line; the plan above it is not
rewritten.

## What is asked

Paper VI (`research/article/attainment-bias-in-llm-grading.md` §6.2) argues that passing the engine's
belief into the grader closes the belief → grade → belief loop early, so that "confidence compounds",
and leaves placeholder 4 for "a simulation over a synthetic cohort with a known ability distribution".
`studies/measurement/grader-attainment-prior/` has since measured what the label does on identical work,
per model: +0.37 to +0.75 marks from a high label against a low one, toward the teacher for Gemini's
weak tail and away from it for GPT-4.1-mini and Qwen. This study feeds those measured effects into an
engine like Lazuli's and asks what they do over a term:

- (a) does belief diverge further from true ability with the edge than without it?
- (b) does misclassification at a mastery threshold change by the end of the term?
- (c) is there a stable fixed point, or does the loop run away? Analytically: the loop gain is the label
  effect × the belief's sensitivity to one grade.
- (d) a strong learner who starts with a wrong low belief: how many items until it recovers?

No model is called. Every grader parameter is fitted from the parent study's per-case dumps (in the
session scratchpad, not committed); the cohort's shape comes from JorGPT.

## Design in one table

| piece | choice |
| --- | --- |
| grader | g = clip(round(a + b·h + u + e + edge·[δ + γ(ℓ − 5) + η(h − 5)])), all per model, fitted from the swap dumps; γ is the label effect in marks per label point |
| uncertainty | learner-cluster bootstrap within tail of the dumps, B = 200, each draw refitted and re-simulated |
| cohort | θ ~ N(5.05, 1.27) on the mark scale, item sd 2.39, 40 items a term (all JorGPT's shape), 4 skills interleaved, an item every 2.5 days |
| engine | E0 as shipped (Beta(0.5, 0.5), mass M = 1 per AI-graded item, lazy decay toward 0.5 with r = (1 + 0.1t)^−0.5); E5 (general-level prior and decay target) as sensitivity |
| label | the stored belief of the skill being graded, ×10, one decimal; bands and binary as sensitivity |
| comparison | edge vs no edge on common random numbers; every estimand is a difference or ratio of the two |

## Pre-registered verdicts (thresholds fixed in the docstring)

| estimand | strings | rule |
| --- | --- | --- |
| spread A = slope(belief on θ | edge) / slope(… | no edge) | AMPLIFIES / DAMPS / NEUTRAL / UNRESOLVED | A − 1 ≥ +0.02 with lower bound > 0 / ≤ −0.02 with upper < 0 / interval inside ±0.02 |
| stability (E0, analytic λ_E = r + wγ) | STABLE / RUNAWAY / UNRESOLVED | 97.5th percentile of λ_E < 1 / point λ_E ≥ 1 |
| divergence ΔRMSE(belief − π) at term end | HARMS / HELPS / NO-CHANGE | ±0.01 belief |
| per tail Δ\|mean error\| (θ ≥ 6, θ < 4) | AWAY / TOWARD / FLAT | ±0.01 belief |
| ΔFNR, ΔFPR at τ = 0.6 | UP / DOWN / FLAT | ±1 percentage point |
| recovery ratio R (median items, edge / no edge) | SLOWER / FASTER / SAME | ±0.05 |

Headline per model: the primary configuration (E0, M = 1, continuous label, measured grader). Across
models: the shared spread verdict, else `MIXED-ACROSS-MODELS`.

## Detection floor (planned)

The whole pipeline (synthetic dumps on the real draw's structure → fit → bootstrap → simulate →
verdict) on six planted worlds × 40 replicates: γ = +0.10 and +0.30 must read AMPLIFIES, γ = −0.10
DAMPS, γ = 0 with and without a label-blind shift NEUTRAL (≤ 10% AMPLIFIES/DAMPS), γ = 1.5 RUNAWAY; and
the simulated spread multiplier must match the analytic loop gain within 25%. A smoke check, written
and scored by one session.

Development note (before this commit, synthetic parameters only): a trial of the gain-recovery check
gave A − 1 = 0.070 / 0.233 / −0.064 against the analytic 0.084 / 0.302 / −0.072 at γ = +0.10 / +0.30 /
−0.10. The simulation sits below the steady-state formula because a skill gets 10 writes a term from a
Beta(0.5, 0.5) start, so the loop never reaches steady state; the 25% tolerance was not changed.

## Floor record: failed twice, revised twice, passed — all before any real parameter was fitted

`out/params.json` did not exist while this ran; full record in the `compounding.py` docstring.

- **Revision 0 (as pre-registered at a3647f5): FAILED.** Nulls read UNRESOLVED (38/40, 37/40): at 300
  cases and 33 learners the interval of A cannot fit inside ±0.02. RUNAWAY read STABLE 23/40: the dumps'
  scores are clipped to 0–10, so the fitted label slope is attenuated (1.50 → 1.22), below γ* = 1.29.
  No world returned a false effect above 3/40.
- **Revision 1:** NEUTRAL band ±0.05 (the measured null resolution); stability judged on the latent γ,
  inverting an attenuation curve fitted on separate synthetic worlds (planted 0.1 / 0.3 / 0.6 / 1.0 / 1.5
  → fitted 0.091 / 0.270 / 0.538 / 0.867 / 1.210). RUNAWAY then 40/40, but the nulls still reached
  NEUTRAL only 23/40 and 19/40: the edge-vs-no-edge spread ratio carries η's and δ's uncertainty, which
  are per-grade effects, not feedback. FAILED.
- **Revision 2 (the verdict now):** the spread verdict is the loop's own multiplier, A = slope(edge) /
  slope(edge with γ = 0), a third arm with the same δ and η and no feedback through the belief. The total
  change (edge / no edge) and its per-grade part are reported beside it.

| world (40 replicates) | planted | reads | result |
| --- | --- | --- | --- |
| AMP-MEASURED | γ = +0.10 | AMPLIFIES | 40/40 |
| AMP-LARGE | γ = +0.30 | AMPLIFIES | 40/40 |
| DAMP | γ = −0.10 | DAMPS | 40/40 |
| NULL-SHIFT | γ = 0, δ = +0.3 | NEUTRAL | 38/40 (2 AMPLIFIES) |
| NULL | all 0 | NEUTRAL | 40/40 |
| SHRINK | γ = 0, η = −0.15 | NEUTRAL | 37/40 (3 AMPLIFIES) |
| RUNAWAY | γ = 1.5 | stability RUNAWAY | 40/40 |

Gain recovery with the planted parameters (cohort 20,000): simulated A − 1 = 0.070 / 0.233 / −0.064
against the analytic steady state 0.084 / 0.302 / −0.072, and exactly 0 at γ = 0. **FLOOR PASSES**
(`out/floor.json`). A smoke check: instrument, worlds and scoring by one session.

Revision 2a, a bug: the learner-cluster bootstrap relabelled resampled learners per row, so in every
draw the per-grade error was ~0 and the persistent learner error carried the whole residual (γ, δ, η,
a, b unaffected). Found from the first `params` run's printed intervals; fixed, and the floor re-run
before the real simulation (the table above is the re-run; SHRINK moved from 38/40 to 37/40).

---

## Results

Runs: `params` on the four swap dumps (Gemini 3.5 Flash Lite, GPT-4.1-mini, GPT-5-mini,
Qwen3-235B-A22B-2507), then `run` (7 configurations × 4 models; 200 parameter draws each with a cohort of
2,000; point estimates on 20,000). Aggregates: `out/params.json`, `out/results.json`. All intervals are
2.5–97.5 percentiles over the learner-cluster parameter draws.

### The measured grader, per model (`out/params.json`)

| model | a | b | per-grade sd σ | learner sd σ_u | δ (any label, at 5) | **γ** (marks per label point) | η | γ within-case |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 1.28 | 0.82 | 1.58 | 0.10 [0.00, 0.45] | −0.02 [−0.07, +0.02] | **0.093** [0.073, 0.114] | −0.012 | 0.098 |
| GPT-4.1-mini | 1.41 | 0.56 | 1.10 | 0.34 [0.00, 0.48] | −0.15 [−0.20, −0.12] | **0.100** [0.081, 0.118] | −0.022 | 0.105 |
| GPT-5-mini | 1.83 | 0.57 | 1.16 | 0.12 [0.00, 0.34] | −0.29 [−0.36, −0.20] | **0.140** [0.121, 0.157] | −0.029 | 0.141 |
| Qwen3-235B (open weights) | 1.56 | 0.52 | 0.94 | 0.40 [0.12, 0.55] | −0.07 [−0.12, −0.01] | **0.199** [0.185, 0.214] | −0.074 | 0.199 |

Checked rather than trusted: γ × the draw's mean label gap (6.96 − 3.24 = 3.72) gives back the parent
study's L (0.35 / 0.37 / 0.52 / 0.74 against 0.37 / 0.38 / 0.52 / 0.75); the within-case estimate
agrees with the regression to 0.007; the quadratic term is ≤ 0.013 in every model, so the linear
interpolation across the unmeasured middle of the label range is not contradicted. All four graders
compress (b 0.52–0.82). Call-to-call noise: Gemini's measured per-answer pass sd is 0.18; the upper
bounds from the edge regression are 0.41–0.50 for every model, against per-grade sd 0.94–1.58, so the
noise a new item brings is mostly case error, not resampling.

### (c) The loop is a stable amplifier on every model: `AMPLIFIES` (all four), `STABLE` (all four)

Primary configuration: E0 as shipped, mass 1 per AI-graded item, a skill revisited every 10 days
(r = 0.707, steady-state mass n* = 4.41, so one grade moves the skill's belief by w = 0.227 per unit of
score).

| model | latent γ | loop gain G = wγ per write | λ_E (λ_0 = 0.707) [95%] | analytic A_loop | **simulated loop multiplier A** [95%] | verdict | runaway needs γ ≥ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 0.103 | 0.023 | 0.730 [0.725, 0.736] | 1.086 | **1.066** [1.049, 1.083] | AMPLIFIES, STABLE | 1.29 (12.6× measured) |
| GPT-4.1-mini | 0.110 | 0.025 | 0.732 [0.727, 0.737] | 1.093 | **1.075** [1.061, 1.091] | AMPLIFIES, STABLE | 1.29 (11.8×) |
| GPT-5-mini | 0.154 | 0.035 | 0.742 [0.737, 0.746] | 1.136 | **1.111** [1.093, 1.128] | AMPLIFIES, STABLE | 1.29 (8.4×) |
| Qwen3-235B | 0.220 | 0.050 | 0.757 [0.753, 0.761] | 1.205 | **1.167** [1.149, 1.183] | AMPLIFIES, STABLE | 1.29 (5.9×) |

Across models: **`AMPLIFIES`** (shared; not MIXED). The direction the paper asserted holds on every
model, including the ones whose single-item label effect moves weak work toward the teacher: whatever the
grade does relative to the teacher, a higher belief yields a higher grade, which raises the belief. The
loop multiplies the between-learner spread the edge produces by 1.07–1.17 over a 40-item term (the
analytic steady state, 1.09–1.21, is the ceiling a longer term approaches). It has a fixed point: the
eigenvalue rises from 0.707 to 0.73–0.76, far from 1; a runaway needs a label effect of about 1.3 marks
per label point (1.1 at mass 3), 6 to 12 times what any of the four models shows. "Confidence
compounds" is right in sign and bounded in size.

The total edge (edge vs no edge, including the per-grade effects δ and η that do not feed back):
A_total 1.053 [1.025, 1.081] AMPLIFIES (Gemini), 1.032 [0.999, 1.064] UNRESOLVED (GPT-4.1-mini), 1.054
[1.005, 1.091] AMPLIFIES (GPT-5-mini), 1.005 [0.967, 1.044] NEUTRAL (Qwen). Qwen's label also pulls the
grade toward itself (η = −0.074), so it makes each grade follow the work less (per-grade factor 0.86),
which the loop then cancels almost exactly.

### (a) Divergence from true ability: small, and signed by the grader's calibration

| model | RMSE(belief − π), no edge | ΔRMSE at item 40 [95%] | verdict | strong tail (θ ≥ 6): mean error, no edge → edge | verdict | weak tail (θ < 4) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 0.072 | −0.002 [−0.004, +0.000] | NO-CHANGE | −0.046 → −0.040 | FLAT | +0.101 → +0.096 | FLAT |
| GPT-4.1-mini | 0.104 | +0.010 [+0.008, +0.013] | UNRESOLVED | −0.160 → −0.175 | **AWAY** | +0.043 → +0.024 | **TOWARD** |
| GPT-5-mini | 0.085 | +0.010 [+0.006, +0.014] | UNRESOLVED | −0.127 → −0.150 | **AWAY** | +0.077 → +0.046 | **TOWARD** |
| Qwen3-235B | 0.111 | +0.012 [+0.008, +0.015] | UNRESOLVED | −0.170 → −0.187 | **AWAY** | +0.044 → +0.026 | **TOWARD** |

Belief units (0.01 = 0.1 mark). The edge's cost to accuracy over a term is about a tenth of a mark of
RMSE on the three harsh graders (resolved above zero, not resolved beyond the pre-set ±0.01 margin, so
UNRESOLVED), and nothing on Gemini. It grows through the term (GPT-5-mini +0.008 / +0.009 / +0.010 at
items 10 / 20 / 30) and levels off, as a stable loop should. The direction is the parent study's, read
through the engine: the harsh graders already under-believe strong learners (−0.13 to −0.17) and the
loop pushes them further below (AWAY, 0.015–0.023). In the weak tail the engine's own pull toward 0.5
leaves beliefs above the truth, and the low label pulls them back (TOWARD) — so at the level of the
belief, not the grade, even the harsh graders' weak tail moves toward the truth. "A penalty on the
weak" is not what compounds; what compounds is strong learners' under-belief on harsh graders.

### (b) Misclassification at τ = 0.6

| model | false 'not mastered' (π ≥ 0.6), no edge → edge | Δ [95%] | verdict | false 'mastered' (π < 0.6) | Δ | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 29.0% → 25.8% | −3.2 pp [−6.4, −0.2] | UNRESOLVED | 6.4% → 7.1% | +0.7 [−0.1, +2.1] | UNRESOLVED |
| GPT-4.1-mini | 97.4% → 98.5% | +1.1 [+0.2, +2.0] | UNRESOLVED | 0.0% → 0.0% | 0 | FLAT |
| GPT-5-mini | 92.2% → 96.7% | **+4.5 [+2.0, +8.9]** | **UP** | 0.0% → 0.0% | 0 | FLAT |
| Qwen3-235B | 98.7% → 99.2% | +0.5 [+0.0, +2.0] | UNRESOLVED | 0.0% → 0.0% | 0 | FLAT |

No weak learner (θ < 4) is ever called mastered, with or without the edge, on any model or
configuration. The ceiling, stated: the three harsh graders call 92–99% of truly-mastered learners
'not mastered' without any edge, because their label-blind grades for strong work sit 1–1.5 marks low;
that is the grader's calibration, not the loop, and it caps what the edge can add. With the label-blind
miscalibration removed (CALIBRATED), the edge's own effect shows: false 'not mastered' +4.6 pp [+1.9,
+7.6] (GPT-4.1-mini, UP) and +10.2 pp [+4.8, +15.6] (GPT-5-mini, UP), −2.4 and −2.0 pp unresolved on
Gemini and Qwen; false 'mastered' falls by 0.8 and 1.6 pp on the two OpenAI models. Whether a strong
learner gains or loses at the threshold depends on δ (the shift any label causes; −0.15 and −0.29 on
the OpenAI models) against γ, which is per model.

### (d) The false-label cost: recovery is slower with the edge, by 2–3 items of 40

500 learners at θ = 7 starting at a confident false belief of 0.3 (E0: every skill at Beta(0.3 n*,
0.7 n*)); recovery = items until the belief stays within 0.05 of the same arm's correctly-started belief.

| model | median items to recover, no edge → edge | R [95%] | analytic R | verdict | items until belief first reaches 0.6 |
| --- | --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 23 → 25 | 1.087 [1.042, 1.130] | 1.10 | **SLOWER** | 25 → 25 |
| GPT-4.1-mini | 19 → 20 | 1.053 [1.000, 1.105] | 1.11 | UNRESOLVED | never (98–99% never reach it) |
| GPT-5-mini | 21 → 23 | 1.095 [1.048, 1.100] | 1.16 | **SLOWER** | never (89–98%) |
| Qwen3-235B | 19 → 22 | 1.158 [1.105, 1.211] | 1.25 | **SLOWER** | never (99%) |

A wrong low belief costs about half a term to undo without the edge (19–23 items), because the engine
decays it only lazily and adds one item's mass at a time; the edge adds 1–3 items (5–16%). On a
calibrated grader the cost is 23 → 25 / 25 / 25 / 27 items. The harsh graders never take a θ = 7
learner to 0.6 in a term, edge or not.

### Sensitivity

Loop multiplier A (all `AMPLIFIES` and `STABLE` unless stated):

| configuration | Gemini | GPT-4.1-mini | GPT-5-mini | Qwen |
| --- | --- | --- | --- | --- |
| **primary** (E0, M = 1, continuous) | 1.066 | 1.075 | 1.111 | 1.167 |
| E0, M = 3 (the mass cap) | 1.081 | 1.091 | 1.136 | 1.205 |
| E5 (general-level prior, n0 = 2) | 1.054 | 1.062 | 1.091 | 1.133 |
| label in 3 bands | 1.059 | 1.069 | 1.099 | 1.154 |
| binary label (mastered / not) | 1.073 | 1.010 NEUTRAL | 1.024 | 1.009 NEUTRAL |
| calibrated grader | 1.062 | 1.069 | 1.098 | 1.153 |
| no learner-level grader error | 1.067 | 1.075 | 1.111 | 1.165 |

- **Update rule.** More mass per item (M = 3) raises the per-write gain and the multiplier; the
  recommended E5 lowers it (its skill priors carry the general level, so each grade moves a skill's
  belief less), by about a fifth of the excess. Neither changes a verdict. ΔRMSE on M = 3 is +0.015 /
  +0.015 / +0.018 on GPT-4.1-mini, GPT-5-mini and Qwen, passing the margin on GPT-4.1-mini and Qwen
  (HARMS); on E5 +0.011 / +0.011 / +0.014 (Qwen HARMS).
- **Label granularity.** Three bands behave like the continuous label. A binary label kills most of
  the feedback (the label changes only when the belief crosses 0.6) but does more damage: almost every
  learner sits below 0.6, so almost every grade gets the low label's push. On the three harsh graders
  the total spread then shrinks (A_total 0.97 / 0.97 / 0.87; DAMPS on GPT-4.1-mini and Qwen) and
  divergence HARMS (+0.017 / +0.020 / +0.025),
  with strong learners' under-belief growing by 0.027–0.041. Coarser is not safer.
- **E5 and a false start.** Under E5 a wrong general level (ĝ at logit 0.3, v = 0.1) is not undone
  within a term on any model, with or without the edge (58–100% not recovered; verdict SAME by
  construction). The modelled ĝ has no drift and the skill priors are frozen at first touch, so this
  is a property of this E5 stand-in, not a measured property of the recommended engine. It is reported
  because it is the larger effect: a confident wrong prior is costlier under E5 than any label edge.

## What this means for Paper VI

- **Placeholder 4 can be filled.** The architectural argument of §6.2 is now quantified, not only
  asserted. Its direction is confirmed on all four models (the loop amplifies), and its size is
  bounded. The compounding is a stable 7–17% amplification of the label's between-learner effect
  over a 40-item term, with a fixed point. A runaway would need a label effect 6–12 times the measured
  one.
- **Keep "the direction of the compounding is not in doubt"; drop any implication of collapse.** The
  loop's sign does not depend on whether the single-item drift is toward or away from the teacher.
  What it costs in accuracy does: about 0.1 mark of belief RMSE over a term on the three harsh graders,
  none on Gemini. "A student estimated as weak receives marks shifted downward, which is evidence that
  they are weak" is true of the grades. At the level of the engine's belief, the harm that compounds is
  strong learners' under-belief on harsh graders (and, on a calibrated grader, 5–10 pp more false 'not
  mastered' on the two OpenAI models). The weak tail's belief moves toward the truth, because the
  engine's own decay toward 0.5 had overstated it.
- **The false-label cost** is the sharpest practical consequence, as the parent study found for single
  items. A strong learner with a wrong low record needs about 19–23 items to recover without the edge
  and 1–3 more with it.
- **No headline number or verdict of Paper VI changes.** This fills a placeholder that had no number.
  §6.2's last paragraph ("the belief does not need to be in the prompt") is unaffected. The readiness
  record's `cooling_off.last_headline_correction` is therefore not touched by this study.
- **The binary-label sensitivity supports §6.4's "do not pass learner-identifying context".** A coarser
  label is not a safe compromise: it removes most of the feedback but pushes almost every learner down.

### Replacement text for placeholder 4 (§6.2), for the paper's re-cut; the article is not edited here

> **Longitudinal compounding (simulated).** We bounded the compounding with a simulation over a
> synthetic cohort (JorGPT's ability distribution: 40 graded items a term over four skills), driving a
> Lazuli-like Beta-Bernoulli engine (lazy decay toward the prior, as shipped) with a grader whose every
> parameter was measured per model in §5.3's swapped-label runs, on common random numbers with and
> without the edge (`studies/measurement/grader-label-compounding/`; pre-registered, detection floor
> passed). The label effect is 0.09–0.20 marks per label point (Gemini 3.5 Flash Lite 0.093, GPT-4.1-mini
> 0.100, GPT-5-mini 0.140, Qwen3-235B 0.199). One grade moves a skill's belief by 0.23 of its score, so
> the loop gain per write is 0.02–0.05. On every model the loop amplifies: over a term it multiplies the
> spread of beliefs the edge produces by 1.07–1.17 (95% intervals within 1.05–1.18). It never runs away.
> The loop's eigenvalue rises from 0.71 to 0.73–0.76, and instability would need a label effect of about
> 1.3 marks per label point, six to twelve times the largest we measured. The direction of the
> compounding does not depend on whether a single label moves the mark toward or away from the
> teacher's. Its cost does. On the three graders that are harsh on strong work, the edge widens
> strong learners' under-belief by 0.015–0.023 (a fifth of a mark) and raises belief RMSE by about 0.01.
> On Gemini it changes accuracy by nothing measurable. A learner wrongly recorded as weak needs 19–23
> items to recover without the edge and 1–3 more with it. A coarser, binary label removes most of the
> feedback but pushes almost every learner down, so it doubles the accuracy cost. The compounding is
> real, bounded and stable: a reason to leave the edge out, not a collapse. A deployment comparison
> would measure what this simulation bounds; after this result the feature will not exist to compare.

## Limits

- A simulation (outcome-timing tag `simulated`): every delay is a parameter of the generator.
- The grader stand-in is linear in the label. It was measured on one corpus (JorGPT short answers) with
  one label sentence and labels only in the two tails; the middle of the label range is interpolated. A
  band's wording is not measured.
- One ability per learner, four skills, and an item every 2.5 days. The per-write gain scales with w and
  r, so a different spacing or mass changes the size, not the sign (M = 3 shown).
- E5 is a stand-in: no drift on ĝ, μ_k set to the cohort mean, λ_k = 1.
- The floor is a smoke check, written and scored by the same session that wrote the instrument.

