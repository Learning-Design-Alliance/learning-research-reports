# Graded exemplars: do they calibrate by carrying the correct marks, or by showing the scale? (Paper VI §5.4)

**Status: RUN 2026-10-05.** Pre-registered at 8807506 before any model call; the floors were run and
committed in the same commit. The full record is the docstring of `analyse.py`. Results are below
the line, and the plan above it has not been rewritten.

## What is asked

Paper VI (`research/article/attainment-bias-in-llm-grading.md` §5.4, release
`ai-grader-reliability-2026` 1.0.0, evidence record `lazuli-grader-jorgpt-2026/exemplar-calibration`)
reports, on JorGPT with Gemini 3.5 Flash Lite (Model.LITE, thinking off), n = 150 stratified, seed 7:

| arm | QWK | MAE | bias | drift |
| --- | --- | --- | --- | --- |
| control | 0.840 | 1.24 | +0.38 | — |
| three graded exemplars | 0.840 | 1.22 | +0.06 | −0.32 |
| same three, marks removed | 0.821 | 1.26 | +0.63 | +0.26 |

It reads this as "the gain comes from the marks — from information about where this rubric places a 3
and where it places an 8". The release's literature review
(`research/readiness/ai-grader-reliability-2026/literature.md`: Min et al. 2022; Yoo et al. 2022;
Wei et al. 2023) gives a rival reading. Demonstrations can work by showing the label space and format,
and whether the labels are correct can matter little. Here that would mean the marks calibrate by
showing a 0–10 scale in use, not by pairing each answer with its right mark. The original contrast,
marks against no marks, cannot separate the two readings.

## Design

- **Draw.** `stratifiedSample(all, 600, seed 7)` on JorGPT. The sampler is prefix-stable, so the
  first 150 cases are the original run's 150. The anchors are the original's: the lowest, median and
  highest answers to the same question by teacher grade, in that order, never the answer being graded.
- **Arms** (`--mode exemplar-marks`, `studies/measurement/grader-eval/harness/stability.ts`). Every arm
  grades the same work and shows the same exemplar texts in the same order. Every graded arm ends with
  the same closing instruction. Only the digits change:

  | arm | marks shown | what it isolates |
  | --- | --- | --- |
  | control | none, no exemplars | the shipped configuration |
  | ungraded | exemplars, no marks | the original third arm |
  | correct | the teacher's marks | the original graded arm |
  | shuffled | the same three marks, deranged (cyclic rotation) | scale and level kept, pairing wrong. Mean \|shown − teacher\| is 6.1 points per anchor; mean signed displacement is 0 |
  | shiftUp | teacher + 2, clamped to 0–10 | ranking kept, shown level up by 1.49 on average (top anchors clamp) |
  | shiftDown | teacher − 2, clamped | ranking kept, shown level down by 1.42 on average (bottom anchors clamp) |

  Jobs are interleaved in hash order. A **render check** (`render_check.py`, `out/render-check.json`,
  PASS) shows the new mode sends all 450 prompts of the original run (vendor/934478716,
  `--mode exemplars --n 150`) byte for byte, plus 1,350 new prompts. It also shows that the
  refactored original mode is unchanged call for call.
- **A confound in the original, recorded rather than fixed.** The graded block ends "Grade the
  learner's response on the same scale these examples were graded on."; the ungraded block has no
  such sentence. So "correct vs ungraded" changes two things: the marks and an instruction. The new
  contrasts (correct vs shuffled, shiftUp vs shiftDown) hold the sentence fixed.
- **Models.** Primary: `google:gemini-3.5-flash-lite`. The release names Model.LITE as this model with
  thinking off, and the 934478716 render shows that model id. Replication: `openai:gpt-4.1-mini` on
  the first 150 cases, under the cost stop rule below.
- **Intervals.** Paired cluster bootstrap with 4,000 resamples, clustered by **question** (anchors
  belong to the question) and separately by **learner**. A verdict must hold under both clusterings.
  Case-iid intervals are reported for sensitivity only.

## Pre-registered verdicts (margin m = 0.15 points of bias)

B(arm) = mean(grader − teacher). The bias contrasts are dCorr = B(correct) − B(control),
dUngr = B(ungraded) − B(control), R = B(shuffled) − B(correct) and S = B(shiftUp) − B(shiftDown). The
legs of S are U = B(shiftUp) − B(correct) and D = B(shiftDown) − B(correct).

| question | verdict | rule |
| --- | --- | --- |
| replication | `GRADED-CALIBRATES` / `GRADED-MISCALIBRATES` / `NOT-REPLICATED` | dCorr 95% upper < 0 / lower > 0 / otherwise |
| ungraded | `UNGRADED-WORSE` / `UNGRADED-BETTER` / `UNGRADED-NO-SHIFT` | dUngr 95% lower > 0 / upper < 0 / otherwise |
| **Q1 pairing** | `SCALE IS ENOUGH` | R's 90% interval inside ±0.15 (TOST) |
| | `CORRECT MARKS MATTER` | R's 95% lower bound > 0: wrong pairings give the generosity back |
| | `SHUFFLED MARKS OVERCORRECT` | R's 95% upper bound < 0: wrong pairings make the grader harsher than correct marks do |
| | `PAIRING INCONCLUSIVE` | otherwise |
| **Q2 anchoring** | `ANCHORS TO SHOWN LEVEL` | U's 95% lower > 0 and D's 95% upper < 0: both legs carry the shift's sign |
| | `ANCHORS UP ONLY` / `DOWN ONLY` / `ANCHORS, LEGS UNRESOLVED` | S's 95% lower > 0 with one leg resolved / neither leg resolved |
| | `IGNORES SHOWN LEVEL` | S's 90% interval inside ±0.15 |
| | `ANCHORS AGAINST SHOWN LEVEL` | S's 95% upper < 0 |
| | `ANCHORING INCONCLUSIVE` | otherwise |

Across models the verdict is the shared one, else `DIFFERS-ACROSS-MODELS`. Secondary: dMAE (margin
±0.10) and dQWK (margin ±0.02) for each contrast, each read as `EQUIVALENT` / `BETTER` / `WORSE` /
`INCONCLUSIVE`. Also reported: ρ, the share of the calibration that shuffled marks keep, and κ, the
pass-through of the shown level.

**What each outcome means for Paper VI (fixed now).**

- `CORRECT MARKS MATTER`: §5.4's reading stands.
- `SCALE IS ENOUGH`: §5.4 is wrong as worded. The marks are needed, so "exemplars must carry their
  marks" holds, but "information about where this rubric places a 3" does not.
- `ANCHORS TO SHOWN LEVEL`: the shown marks set the grader's level, so exemplars from a severe or
  lenient marker pass that severity on. "The same correction as the better tier" depends on the
  exemplars being marked on the reference's level.
- `NOT-REPLICATED`: the §5.4 headline does not reproduce.

## Detection floor (run before any call; `out/floor-*.json`)

Synthetic graders run on the real draw, with the real teacher marks, the real question and learner
clusters and the real shown marks. Each has a question effect, a learner effect and a case effect, a
question × arm offset (sd 0.15) on every exemplar arm, and a per-arm call noise of sd 0.6 (planning)
or 0.8 (pessimistic). The docstring says where these values come from: none comes from this study.
Six worlds are planted: SCALE, PAIRING, ANCHOR, PAIR+ANCHOR, OVERCORRECT and NULL. A world passes when
≥ 80% of 200 replicates return the planted verdicts and ≤ 10% return a false finding.

- At n = 600 with the planning noise, **every world passes** (`floor-600.json`). Equivalence
  verdicts come back in 84–92% of replicates, directional verdicts in 100%.
- With the pessimistic noise, n = 600 gives 70–80% on the equivalence verdicts (`floor-600-sd0.8.json`,
  FAIL). n = 900 is needed there (`floor-900-sd0.8.json`).
- At n = 150, the GPT-4.1-mini size, the directional verdicts pass (92–100%) and equivalence returns
  20–26% (`floor-150.json`).

So an `INCONCLUSIVE` on an equivalence question means the run was underpowered. It is never read as
disagreement. The measured within-case sd of each contrast is reported beside the verdicts, so it is
visible which floor applies. These are smoke checks, written and scored by one session, and are
reported as such.

## Budget and stop rule

The estimate uses the dry-run prompts (about 2,100 input tokens) and 600 output tokens per grading,
at the list prices grader-attainment-groups read on 2026-10-05:

| run | calls | estimate |
| --- | --- | --- |
| Gemini, n = 600 | 3,600 | $7.6 |
| GPT-4.1-mini, n = 150 | 900 | $1.6 |

The cap is $10 in total.

- Gemini runs first, with `--max-calls 3700`.
- GPT-4.1-mini runs at n = 150 only if Gemini's measured cost plus GPT's projection (from Gemini's
  measured tokens per call) is at most $10. If not, it runs at n = 100; if that does not fit either, it
  is not run (`python3 analyse.py --stop-rule <gemini dump>`).
- The rule reads token counts, never scores. Neither provider reports cost to the guard, so the calls
  are bounded by `--max-calls`.

## Data

JorGPT (`jorgpt-answers` in `data/data-sources.json`, already registered), read only by the harness.
The per-case dumps stay in the session scratchpad. Only the `out/*.json` aggregates are committed.

## How to run

    cd studies/measurement/grader-eval
    pnpm exec tsx harness/stability.ts --data $JORGPT_DIR/dataset_en.csv --mode exemplar-marks --n 600 --seed 7 \
      --model google:gemini-3.5-flash-lite --concurrency 8 --max-calls 3700 --dump $W/lite.json
    python3 ../grader-exemplar-marks/analyse.py --stop-rule $W/lite.json
    NODE_USE_ENV_PROXY=1 pnpm exec tsx harness/stability.ts --data … --mode exemplar-marks --n 150 --seed 7 \
      --model openai:gpt-4.1-mini --concurrency 8 --max-calls 950 --dump $W/gpt41mini.json
    python3 ../grader-exemplar-marks/analyse.py --dumps $W/lite.json $W/gpt41mini.json

---

## Results

**Runs.** Gemini 3.5 Flash Lite, n = 600:

- 3,600 gradings, 0 failed, all 600 cases complete in every arm.
- 4.67M input and 1.12M output tokens, **$4.19** at list price.

GPT-4.1-mini, n = 150:

- Ran at n = 150 under the stop rule (projection $0.91).
- 900 gradings, 4 failed (3 timeouts, 1 schema miss), 146 cases complete.
- 1.38M input and 0.34M output tokens, **$1.10**.

**Total $5.29.** Neither provider reports cost to the guard, so these figures are the provider token
counts × list price. Aggregates are in `out/results.json`.

Intervals are 95%, paired, and clustered by question (q) and by learner (l); a verdict needs both.
For Gemini, the measured within-case sd of the contrasts is 0.70–0.99, close to the floor's planning
value of about 0.9. So `floor-600.json` (PASS) is the floor that applies.

**Reproduction first.** On the original 150 cases, Gemini today returns:

| arm | bias today (original) | QWK today (original) |
| --- | --- | --- |
| control | +0.32 (+0.38) | 0.841 (0.840) |
| correct marks | 0.00 (+0.06) | 0.846 (0.840) |
| ungraded | +0.67 (+0.63) | 0.814 (0.821) |

The §5.4 table reproduces on its own draw.

### Gemini 3.5 Flash Lite (n = 600, 50 questions, 79 learners)

| arm | bias [q 95%] | MAE | QWK |
| --- | --- | --- | --- |
| control | +0.19 [−0.01, +0.41] | 1.21 | 0.854 |
| ungraded | +0.61 [+0.43, +0.79] | 1.24 | 0.835 |
| correct | −0.15 [−0.34, +0.06] | 1.19 | 0.857 |
| shuffled | +0.06 [−0.11, +0.26] | 1.20 | 0.848 |
| shift +2 | +0.33 [+0.15, +0.52] | 1.23 | 0.844 |
| shift −2 | −0.80 [−1.00, −0.57] | 1.44 | 0.814 |

| contrast | Δbias | q 95% | l 95% | verdict |
| --- | --- | --- | --- | --- |
| dCorr = correct − control | −0.34 | [−0.48, −0.21] | [−0.42, −0.26] | **GRADED-CALIBRATES** |
| dUngr = ungraded − control | +0.42 | [+0.29, +0.55] | [+0.35, +0.48] | **UNGRADED-WORSE** |
| R = shuffled − correct | **+0.22** | [+0.12, +0.31] | [+0.16, +0.27] | **CORRECT MARKS MATTER** |
| S = shift +2 − shift −2 | **+1.13** | [+1.02, +1.23] | [+1.06, +1.19] | **ANCHORS TO SHOWN LEVEL** |
| U = shift +2 − correct | +0.48 | [+0.40, +0.57] | [+0.42, +0.53] | leg up resolved |
| D = shift −2 − correct | −0.65 | [−0.73, −0.57] | [−0.70, −0.59] | leg down resolved |

- **ρ, the share of the downward shift that shuffled marks keep: 0.37** (q [0.02, 0.60], l [0.21, 0.51]).
  The shuffled arm shows the same three numbers, at the same mean level and on the same scale, and it
  still moves the grade about a third as far as the correct marks do. The other two thirds need the
  correct pairing.
- **κ, the pass-through of the shown level: 0.39** (q [0.35, 0.42]). The ±2 arms differ by 2.92
  points of mean shown mark, and the grade follows by 1.13 points, on identical work. Both legs carry
  the sign of their shift.
- **Accuracy (secondary).** Correct vs control and shuffled vs correct are EQUIVALENT on MAE (±0.10)
  and QWK (±0.02): the pairing moves the level and not the ranking. Ungraded vs control is WORSE on
  QWK (−0.018). Shifting down is WORSE on both, MAE +0.24 and QWK −0.043.
- **Calibration and shift are different things.** On the full draw the control is only +0.19
  generous, against +0.32 on the original 150. The correct marks still move the grade by −0.34, so
  here they overshoot to −0.15. |bias| goes from 0.19 to 0.15, which is no real gain, and the shuffled
  arm (+0.06) sits closest to zero of all. The exemplars apply a roughly fixed, mark-dependent shift.
  It lands at zero only where the control's generosity happens to be about that size.

### GPT-4.1-mini (n = 146 of the first 150; a directional check only, see the floor)

| contrast | Δbias | q 95% | l 95% | verdict |
| --- | --- | --- | --- | --- |
| dCorr | −0.06 | [−0.17, +0.03] | [−0.15, +0.03] | **NOT-REPLICATED** |
| dUngr | +0.19 | [+0.07, +0.30] | [+0.09, +0.29] | UNGRADED-WORSE (see note) |
| R | +0.08 | [−0.02, +0.17] | [−0.02, +0.17] | **PAIRING INCONCLUSIVE** (underpowered at n 150: floor 20–26% on equivalence) |
| S | **+0.47** | [+0.38, +0.56] | [+0.37, +0.56] | **ANCHORS TO SHOWN LEVEL** (U +0.23, D −0.23, κ 0.16 [0.13, 0.19]) |

- GPT-4.1-mini is a **harsh** grader here: control bias is −0.77, with MAE 1.58 and QWK 0.738. So the
  pre-registered string `UNGRADED-WORSE` ("more generous than no exemplars") here means the ungraded
  exemplars move it *toward* the teacher, not away.
- On this model the correct marks do not move the bias. They raise QWK by +0.033 (q [+0.005, +0.068],
  BETTER), which Gemini does not show.
- Anchoring replicates in sign on both legs, at less than half Gemini's pass-through.

**Across models:**

| question | verdict |
| --- | --- |
| anchoring | `ANCHORS TO SHOWN LEVEL` on both models |
| ungraded | `UNGRADED-WORSE` (more generous) on both models |
| replication | `DIFFERS-ACROSS-MODELS` (Gemini GRADED-CALIBRATES; GPT-4.1-mini NOT-REPLICATED) |
| pairing | `DIFFERS-ACROSS-MODELS` (Gemini CORRECT MARKS MATTER; GPT-4.1-mini PAIRING INCONCLUSIVE, underpowered) |

### What this means for Paper VI

1. **The §5.4 table stands on its own draw.** It reproduces within 0.06 on every cell. Kappa is
   unchanged on 600 cases too.
2. **The scale-only rival is rejected for the model the paper used.** Shuffled marks show the same
   numbers on the same scale, and they keep only about a third of the shift. So the pairing of answer
   and mark carries most of it, and §5.4's "the gain comes from the marks" survives.
3. **"Information about where this rubric places a 3 and an 8" is too strong as a mechanism.** The
   grader also copies the *level* of whatever marks it is shown. Raising every shown mark by 2 raises
   the grade on identical work by 0.48, and lowering every mark by 2 lowers it by 0.65 and costs 0.24
   MAE. A wrong or differently calibrated set of exemplar marks is therefore passed straight on to the
   grade.
4. **"Calibrate" should read "shift".** The exemplars move Gemini down by about a third of a point
   whatever its starting generosity. On the original 150 cases that lands at 0.00; on the wider draw
   it overshoots to −0.15. On GPT-4.1-mini, already harsh, it does nothing to bias. The claim that
   exemplars "buy the same calibration as a substantially more expensive model" (§5.4, practice
   point 2) holds for one model on one draw. It is not a property of exemplars.
5. **The ungraded arm carries a second difference.** Only the graded block ends "Grade the learner's
   response on the same scale these examples were graded on." So "worse than nothing" (+0.42 here)
   compares marks *plus* an instruction against neither. The wrong-mark arms are what isolate the
   marks.

**Exact replacement text for §5.4's interpretation.** Replace the two paragraphs that begin "**Graded
exemplars calibrate without improving agreement.**" and "**The ungraded arm is what makes this a
dissociation rather than a confound.**", and practice points 2 and 3, with:

> **Graded exemplars shift the grade without improving agreement.** Kappa is unchanged to three
> decimals. The systematic generosity of the cheap tier nearly vanishes on this draw (+0.38 → +0.06).
>
> **The marks do the work, through their pairing with the answers and through their level.** A
> follow-up held the work and the exemplar texts fixed and changed only the marks shown
> (studies/measurement/grader-exemplar-marks, 600 answers, 3,600 gradings, pre-registered). It
> separates two mechanisms:
>
> - *Pairing.* With the same three marks deranged across the three answers, which keeps the scale and
>   its mean level, the grader kept only about a third of the shift (ρ 0.37, question-clustered 95%
>   interval 0.02–0.60). Shuffled marks were 0.22 points more generous than the correct ones
>   [0.12, 0.31]. The correct pairing therefore carries most of the effect, and the scale alone does
>   not.
> - *Level.* With every shown mark moved up or down by two points, ranking kept, the grade on identical
>   work moved 0.39 points for every point of shown level (+0.48 up, −0.65 down; both legs excluding
>   zero). The grader adopts the level the exemplars are marked at, right or wrong.
>
> So the exemplars apply a roughly fixed, mark-dependent shift: −0.34 [−0.48, −0.21] on the wider
> draw, where the control was only +0.19 and the shift overshot to −0.15. That it cancels the
> generosity here is a coincidence of size, not a guarantee. On GPT-4.1-mini, a harsh grader on this
> corpus (−0.77), the same exemplars left bias unchanged (−0.06 [−0.17, +0.03]), though the level
> anchoring replicated (0.16 per point).
>
> **The ungraded arm differs in two ways, not one.** It shows the same three answers without marks,
> and it also drops the closing instruction to grade on the examples' scale. It is worse than nothing
> on bias (+0.63 here; +0.42 [+0.29, +0.55] on the wider draw) and slightly worse on kappa. Extra
> context is not free, but this arm alone cannot say whether the marks or the instruction is the
> active ingredient. The wrong-mark arms can, and they say it is the marks.
>
> 2. **Calibration context about the task moves the grade by the level it is marked at.** Graded
>    exemplars can remove a known generosity, but only if their marks are on the reference's level.
>    The size of the shift must be checked against the grader's own offset on the target corpus, and
>    re-checked when the model changes.
> 3. **Exemplars must carry correct marks, on the right level.** Without marks the intervention is
>    worse than nothing. With wrongly paired marks it does a third of the job. With marks two points
>    off it moves every grade by most of a point.

**Headline change.** §5.4's mechanism and practice points 2 and 3 change. So does the abstract's
"removed almost all of the grader's systematic generosity", which needs scoping to one model and one
draw. The §5.4 numbers do not change. This counts as a verdict correction, so `cooling_off.
last_headline_correction` in `research/readiness/ai-grader-reliability-2026/readiness.yaml` is set to
2026-10-05 in this commit. The article itself is not edited here.

**Coder.** No construct here is coded. Every quantity is a model's numeric grade against the
teacher's numeric mark, read from the dumps.
