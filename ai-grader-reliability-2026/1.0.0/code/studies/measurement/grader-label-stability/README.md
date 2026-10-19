# Is the attainment-label effect stable across item length and score scale? (Paper VI, placeholder 3)

**Status: RUN 2026-10-05.** Pre-registered at b7a97cc, before any model call. Design, contrasts, tolerance, verdict
strings and the detection floor are in `analyse.py`'s docstring, which is the primary record; the
floor (`out/floor.json`) passed before this commit. Results will be added below a line; nothing
above it will be rewritten.

## What is asked

Paper VI (`research/article/attainment-bias-in-llm-grading.md`, release `ai-grader-reliability-2026`
1.0.0), §5.3, placeholder 3: *"What remains open is whether the gap is stable across items of
different length and scale, which this draw does not vary."* The Q2 study
(`../grader-attainment-prior/`) measured the label's effect on identical work with a swapped-label
arm, on one corpus: JorGPT short answers on 0–10, +0.37 to +0.75 points across four models. This
study carries the same manipulation to items of other lengths and scales and compares the effect on a
common scale.

## Design

| cell | corpus | scale | items | median length | calls |
| --- | --- | --- | --- | --- | --- |
| `jorgpt10` | JorGPT, the Q2 draw | 0–10 | 300 answers, 33 learners | 486 chars | none: the Q2 dumps |
| `jorgpt5` | the same 300 answers, same label positions | 0–5 | 300 | 486 | 600 per model |
| `mohler` | Mohler ASAG, stratified on grade, seed 7 | 0–5 | 300 answers, 62 questions | 81 | 600 |
| `menagerie` | Menagerie CS1 Java programs (original source), 4 rubric dimensions | 0–13 (A++..F) | 60 submissions × 4 | 60,000 (truncated; 55 of 60) | 480 |

- **Manipulation.** Two arms per case, the high label and the low label, in the Q2 sentence ("Current
  attainment for this learner across this course: x/max, from n prior graded responses."). The label
  pairs are the Q2 draw's own 150 (high, low) pairs, rescaled by max/10, in every cell, so the label's
  position on the scale is distributed the same way everywhere (gap 0.372 of the range; 0.361 on
  Menagerie, which uses pairs 0–59). Each arm is the other's control, the same size by construction
  (`shared/controls.py`, recorded in `out/results.json`).
- **Estimand.** S = mark under the high label − mark under the low label, same work, signed. Primary:
  s = S / range. Secondary: S / SD of the cell's human scores. Reported: S / label gap (pass-through).
- **Contrasts.** C1 length within JorGPT (within tail, adjusted for score level); C2 length within
  Mohler; C3 **scale on identical answers** (0–5 vs 0–10); C4 Mohler vs JorGPT, both 0–5 (shorter
  answers, other items); C5 Menagerie vs JorGPT (whole programs, other task).
- **Unit.** Cluster bootstrap: learners within tail (JorGPT), questions (Mohler, no learner id),
  submissions (Menagerie). 4,000 resamples.
- **Models.** `google:gemini-3.5-flash-lite` (thinking off), `openai:gpt-4.1-mini`, and
  `openrouter:qwen/qwen3-235b-a22b-2507` pinned to DeepInfra with fallbacks off
  (`OPENROUTER_PROVIDER=DeepInfra`), each at its defaults, as in Q2. GPT-5-mini is not re-run; its Q2
  dump gives C1 only. Node runs with `NODE_USE_ENV_PROXY=1`.

## Pre-registered verdicts

Tolerance δ = **0.02 of the score range** (0.2 points on 0–10; Q2's effects are 0.037–0.075 of the
range, so δ is a third to a half of the effect). SD reading: 0.07 SD. Each contrast: `EQUIVALENT`
(90% interval inside ±δ), else `LARGER` / `SMALLER` (99% interval excludes 0; Bonferroni over five),
else `UNRESOLVED`.

Per model: `STABLE` (every answerable contrast EQUIVALENT); `GROWS-WITH-LENGTH` /
`SHRINKS-WITH-LENGTH` tagged `[within]` or `[across-corpora: confounded with task]`;
`LENGTH-INCONSISTENT`; `SCALE-DEPENDENT (larger|smaller on 0-5)`; else `UNDERPOWERED`. Labels combine
with " + ". Across models: the shared verdict, else `MIXED-ACROSS-MODELS`. Direction, separately:
`DIRECTION-STABLE` if s > 0 (95%) in every cell on every model, `DIRECTION-REVERSES` if any cell is
negative, else `DIRECTION-UNRESOLVED`.

**What each verdict would mean for the paper (written before the run):**

- `STABLE` over C3 and C5 → placeholder 3 can be closed: the effect, as a share of the scale, does
  not change by more than 0.02 of the range between a 0–5 and a 0–10 scale on identical answers, nor
  between short answers and whole programs.
- `SCALE-DEPENDENT` → the paper's points-on-0–10 figures do not transfer to other scales by
  proportion; §5.3 must say which scale an effect size is on and that it is not scale-free.
- `GROWS-` / `SHRINKS-WITH-LENGTH[across-corpora]` → the effect's size depends on the kind of item;
  the paper may not generalise the 0–10 short-answer magnitude to long work, and the difference
  cannot be attributed to length rather than task.
- `UNDERPOWERED` → placeholder 3 stays open, reported with the intervals.
- `DIRECTION-STABLE` → "the direction generalises while the size is model-specific" extends from
  models to item types. `DIRECTION-REVERSES` anywhere → it does not, and the paper must say where.

## Detection floor (passed before this commit)

Synthetic graders on the real draws (real lengths, clusters, tails, label pairs, human scores;
integer marks, clipped to the scale), 200 replicates × 2,000 resamples per world. Revisions before
any call are recorded in the docstring (rev 0 failed: compression at the ends of the scale read as a
length effect, and the scale world was planted below the tolerance's power). Rev 2:

| world | planted | result |
| --- | --- | --- |
| CONST | s = 0.05 everywhere | no difference called in 93.5% |
| CONST-NOISY | same, noise ×1.5, cluster sd 0.5 | 90.5% |
| GROWS | s ∝ length^0.2 (0.035 Mohler → 0.13 Menagerie) | GROWS-WITH-LENGTH 100%, SHRINKS 0% |
| SHRINKS | s ∝ length^−0.2 | SHRINKS-WITH-LENGTH 95.5%, GROWS 0% |
| SCALE | s = 0.09 on 0–5, 0.05 on 0–10/13 | SCALE-DEPENDENT (larger on 0–5) 93%; false length 4% |

**What the floor says before any real number.** Only C3 (scale, 62%) and C5 (programs vs short
answers, 68%) can reach equivalence under a constant effect; C1 (41%), C4 (46%) and C2 (2%) cannot, so
`STABLE` can only be stated over C3 and C5. The planted length trend is found through C5 every time
and within a corpus only 13.5% of the time: this instrument cannot see a length trend of that size
inside JorGPT or Mohler, so any length verdict will rest on corpora that differ in task as well as
length. This is a smoke check written and scored by one session, and is reported as one.

## Budget

Estimated before any call: per model 1,200 short gradings (~1.9k tokens each) and 480 Menagerie
gradings (~17k tokens in). Gemini ≈ $2.7, GPT-4.1-mini ≈ $5.1, Qwen ≈ $1.7: about **$9.5** against a
$15 cap. The harness guards (spend, calls, failure rate 35%) stay on; Qwen runs last and only if the
spend so far leaves room.

## Data

JorGPT (`jorgpt-answers`), Mohler (`mohler-asag`), Menagerie (`menagerie-grades`; this study adds
the deposit's four "Anonymised Assignments" source archives to its entry, hashes matching the OSF
metadata). All read only by the harness (`--mode label-stability` in
`../grader-eval/harness/stability.ts`); per-case dumps stay in the session scratchpad and only
`out/*.json` aggregates are committed.

---

## Results

**Runs.** `--mode label-stability` on the three new cells × three models. Failed gradings: Gemini
0/600, 0/600, 0/480; GPT-4.1-mini 4/600, 1/600, 1/480; Qwen 5/600, 7/600, 8/480. A case missing an
arm is dropped from both arms. Qwen was pinned to DeepInfra with fallbacks off, and OpenRouter
reported $1.25.

**Deviation from the plan.** Qwen ran alongside the other two models rather than after them, because
the guards on each run kept the total bounded. Its Menagerie cell ran as a separate process.

**Spend.** Google and OpenAI do not report spend to the harness. Estimated from prompt sizes (about
1.1k tokens for a short answer, about 16k for a program): about $1–2.5 for Gemini and $5 for
GPT-4.1-mini, so **about $7–9 in all**, against the $15 cap.

**The 0–10 JorGPT cell** is the Q2 dumps, read unchanged. It was checked case by case against this
mode's dry-run draw: the same 300 ids, tails and label pairs.

Aggregates are in `out/results.json`. Intervals are cluster bootstrap 95% unless marked otherwise.

**Checked before reading the results.**
- In every short-answer cell the marks track the human scores: r = 0.76–0.82 between the mean of the
  two arms and the human score.
- On Menagerie they track less well against the deposit's rater mean: r = 0.58 for Gemini, 0.25 for
  GPT-4.1-mini, 0.33 for Qwen.
- Gemini marks programs high: mean 11.4 of 13, and 17% of items have an arm at the top of the scale.

### s = label effect on identical work as a share of the score range (high label − low label)

| model | JorGPT 0–10 (Q2) | JorGPT 0–5, same answers | Mohler 0–5 (short) | Menagerie 0–13 (programs) |
| --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | 0.037 [0.029, 0.044] | 0.031 [0.023, 0.038] | 0.016 [0.007, 0.027] | 0.015 [0.007, 0.023] |
| GPT-4.1-mini | 0.038 [0.030, 0.046] | 0.039 [0.031, 0.048] | 0.031 [0.020, 0.041] | **0.105** [0.094, 0.116] |
| Qwen3-235B-A22B-2507 | 0.076 [0.069, 0.082] | 0.060 [0.051, 0.068] | 0.069 [0.059, 0.078] | **0.179** [0.160, 0.198] |
| GPT-5-mini (Q2 only) | 0.052 [0.044, 0.061] | — | — | — |

The same effects in points, in the column order of the table above (Menagerie on 0–13, per rubric
dimension):

| model | JorGPT 0–10 | JorGPT 0–5 | Mohler 0–5 | Menagerie 0–13 |
| --- | --- | --- | --- | --- |
| Gemini 3.5 Flash Lite | +0.37 | +0.15 | +0.08 | +0.20 |
| GPT-4.1-mini | +0.38 | +0.20 | +0.16 | **+1.37** |
| Qwen3-235B-A22B-2507 | +0.76 | +0.30 | +0.34 | **+2.32** |

In SD of the human scores, Menagerie reads 0.08 SD (Gemini), 0.56 SD (GPT-4.1-mini) and 0.94 SD
(Qwen), against 0.13–0.27 SD on JorGPT.

**Direction: `DIRECTION-STABLE`.** All 13 cells are positive with intervals clear of zero. A high
label raises the mark on identical work on every model, scale and item type tried.

### Contrasts (signed; δ = 0.02 of the range)

| contrast | Gemini | GPT-4.1-mini | Qwen |
| --- | --- | --- | --- |
| C3 scale, same answers (0–5 − 0–10) | −0.006 [−0.016, +0.004] **EQUIVALENT** | +0.000 [−0.012, +0.012] **EQUIVALENT** | −0.016 [−0.024, −0.009] **SMALLER** |
| C5 programs − short answers | −0.022 [−0.032, −0.011] **SMALLER** | +0.068 [+0.054, +0.081] **LARGER** | +0.103 [+0.083, +0.123] **LARGER** |
| C4 Mohler − JorGPT (both 0–5) | −0.014 [−0.027, −0.001] UNRESOLVED | −0.008 [−0.022, +0.005] EQUIVALENT | +0.009 [−0.004, +0.021] EQUIVALENT |
| C1 length within JorGPT (level-adjusted) | +0.008 [−0.004, +0.019] EQUIVALENT | +0.012 [−0.002, +0.025] UNRESOLVED | +0.016 [+0.004, +0.029] UNRESOLVED |
| C2 length within Mohler | −0.002 [−0.031, +0.026] UNRESOLVED | −0.006 [−0.024, +0.016] UNRESOLVED | +0.002 [−0.021, +0.022] EQUIVALENT |

- **C1 on GPT-5-mini** (Q2 dump): +0.002 [−0.011, +0.019], EQUIVALENT.
- **C1 on the 0–5 JorGPT cell** (replication): +0.003, +0.020 and +0.022. Qwen's is LARGER at 99%.
- **C1 and C2 cannot reach equivalence reliably** (see the floor), so their EQUIVALENT readings are
  reported but not relied on.

### Pre-registered verdict: `MIXED-ACROSS-MODELS`

- **Gemini 3.5 Flash Lite: `SHRINKS-WITH-LENGTH[across-corpora: confounded with task]`.** The scale
  contrast is equivalent. On programs the effect is 0.4× its short-answer size.
- **GPT-4.1-mini: `GROWS-WITH-LENGTH[across-corpora: confounded with task]`.** The scale contrast is
  equivalent. On programs the effect is 2.8× its short-answer size.
- **Qwen3-235B: `GROWS-WITH-LENGTH[across-corpora: confounded with task]` + `SCALE-DEPENDENT (smaller
  on 0-5)`.**
  - On programs the effect is 2.4× its short-answer size.
  - On identical answers, the 0–5 scale carries 0.8× the 0–10 share. The point difference (0.016) is
    inside the tolerance, but its 90% interval reaches −0.023, so it is not equivalent.
  - Qwen's 0–10 cell came from the Q2 run, hours earlier. A change on the host between the two runs
    is not ruled out. Gemini and GPT-4.1-mini had the same two-run setup and their cells match.
- **The SD reading** gives the same verdicts, except that Gemini is `UNDERPOWERED` in SD units.

**Reported, not part of the verdict (added after the run).**
1. Gemini's small effect on programs is not only a ceiling effect. In the third of programs with the
   lowest human scores it is 0.025, still below its 0.037 on JorGPT.
2. On Menagerie the label moves every rubric dimension: GPT-4.1-mini +0.99 to +1.57 points, Qwen
   +1.87 to +2.89, Gemini +0.07 to +0.38.
3. The two models with the largest effect on programs are the two whose marks track the human raters
   least there (r = 0.25 and 0.33). That fits a grader that leans on the label where it reads the work
   least well, but this study did not test it.

## What this means for Paper VI

**Placeholder 3 can be closed, but the answer is not "stable".**
- **The sign generalises** across item types and scales: all 13 cells are positive.
- **Changing only the scale on identical answers barely matters.** The share of the range moves by
  at most 0.016, and is equivalent within ±0.02 on two of the three models.
- **The magnitude depends on the kind of item, and differently for each model.** On whole programs:
  - GPT-4.1-mini: 2.8× its short-answer size;
  - Qwen: 2.4× its short-answer size;
  - for those two models, 1.4–2.3 points on a 14-level scale (0.6–0.9 SD of the human grades);
  - Gemini: 0.4× its short-answer size.
- **Length is not shown to be the cause.** Programs differ from short answers in task and rubric as
  well as length. Within the short-answer corpora no length trend was resolved, and the floor showed
  the instrument could not have resolved one of the planted size.

**No headline number or verdict of Paper VI changes.**
- The 0–10 short-answer gaps stand as measured.
- §5.3 says "the *direction* generalises while the *size* is model-specific". That now extends to
  item type: the size is model-specific *and* item-specific.
- So `research/readiness/ai-grader-reliability-2026/readiness.yaml`
  `cooling_off.last_headline_correction` is not touched.
- A re-cut that made the long-work result a headline (for example "up to 2.3 points on programs")
  would be a headline change, and its commit would need to update that field.

**§6.2's architectural argument gets stronger.** On long work the label can move a mark by more than
half a human SD.

**Replacement text for placeholder 3 (§5.3).** The article itself was not edited.

> **`[PLACEHOLDER 3 — resolved]`** *Re-tested on items of three lengths and three scales, with the
> same label pairs throughout, on three models (Gemini 3.5 Flash Lite, GPT-4.1-mini, open-weights
> Qwen3-235B-A22B): Mohler short answers on 0–5; the same Corpus A answers re-marked out of 5; and
> whole CS1 Java programs from Corpus C on a 14-level rubric, four dimensions each. The direction is
> stable: a high label raised the mark on identical work in every model × corpus cell. The size is
> not. Changing only the scale, on identical answers, left the effect as a share of the range within
> ±0.02 on two models and shrank it from 0.076 to 0.060 on the third. On whole programs the effect was
> 2.8× its short-answer size on GPT-4.1-mini (0.105 of the range, 1.4 points) and 2.4× on Qwen (0.179,
> 2.3 points), 0.6–0.9 SD of the human grades, but 0.4× on Gemini (0.015). Programs differ from short
> answers in task and rubric as well as length, so this does not isolate length, and within the
> short-answer corpora no length trend was resolvable. The gaps above are short-answer, 0–10 figures:
> their sign generalises across item types; their magnitude has to be measured per model and per item
> type, and on long work it can be several times larger.*

**Appendix A, row 3** would read: "**RESOLVED 2026-10-05** — sign stable across item type and scale;
magnitude item- and model-dependent (programs 0.4×–2.8× short answers); length not isolated".
