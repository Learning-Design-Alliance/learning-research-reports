# Does a sentence about the student move the mark just by being there? (Paper VI, neutral control)

**Status: PRE-REGISTERED 2026-10-06 at 3046048, before any model call; floor revision 1 committed
before any call.** The design, thresholds and verdict strings below were fixed at 3046048 (the
readings verdict revised by the floor, recorded below). **RUN 2026-10-06**; results below the line. Results go
below the line; the plan above it is not rewritten. Full record: the docstring of `neutral.py`.


The outcome is a grader's mark on fixed work (`not-a-learner-outcome`).

## What is asked

Paper VI (`research/article/attainment-bias-in-llm-grading.md`, release `ai-grader-reliability-2026`)
gives a short-answer grader the sentence *"Current attainment for this learner across this course:
x/10, from n prior graded responses."* The swapped-label estimand L (high label minus low label on
the same answer) cannot contain a presence effect: both arms carry a same-length sentence. But two
readings compare the labelled arm with a control that has **no added text**:

- the **penalty** (the true low label's drift from control, low tail) and the **reward** (the true
  high label's drift from control, high tail);
- the **toward/away** reading (`../grader-attainment-prior/`, revision 3).

Both mix "a sentence about the student is present" with "what it says". CLAUDE.md: a control has to
be the size of the thing it controls for. On ASAP 2.0 a same-length mid label moved marks by being
present (`../grader-attainment-groups/`); Kapetanovic et al. 2026 found the presence of a prior score
mattered more than its value.

## Design

- **Draw.** Q2's 300-answer attainment draw, unchanged (150 answers from 19 learners with held-out
  mean ≥ 6, 150 from 14 learners with < 4). A dry run with the new arm set reproduces Q2's rows
  exactly.
- **Arms, one run** (`--mode attainment-swap --n 300 --arms control,neutral,true,swapped`): control
  (no added text), **neutral**, true label, swapped label. The swapped arm is kept (about $0.30): it
  leaves the harness's identical-work pairing untouched and re-measures L inside this run, so the run
  can be checked against Q2 (L +0.37) before anything new is read.
- **The neutral sentence** (fixed here):
  > Current context for this learner across this course: this response was submitted as coursework.

  95 characters against the attainment sentence's 94–95 (mean 94.99; ratio 1.000; rule ±10%). Same
  opening, register and line of the prompt; no number; identical for every answer and true of every
  answer. The rule is asserted in the harness before any call and again on the dump. An offline
  render (fetch replaced, nothing sent) showed the four arms' prompts differ only on that line and
  the request bodies are otherwise identical.
- **Harness change** (`grader-eval/harness/stability.ts`): `neutral` is accepted in `--arms`; only
  when it is asked do rows gain `neutral` and `labelTrueChars` and the dump `neutralText`. Without it
  nothing sent or written changes.
- **Model.** `google:gemini-3.5-flash-lite`, configured as in Q2 and the breadth re-run (Google
  direct, current harness, no sampling parameters sent, thinking `minimal`, response schema, prompt
  pin 277cd5085). Command, from `studies/measurement/grader-eval`:
  `NODE_USE_ENV_PROXY=1 node_modules/.bin/tsx harness/stability.ts --data <scratch>/raw/jorgpt/dataset_en.csv
  --mode attainment-swap --n 300 --arms control,neutral,true,swapped --model google:gemini-3.5-flash-lite
  --concurrency 5 --max-calls 1300 --dump <scratch>/neutral/swap-neutral-lite.json`.
- **Unit.** Learner-cluster bootstrap within tail, 4,000 replicates, percentile (Q2's scheme).

## Estimands (signed, per tail, paired on the same answers)

| | definition | reading |
| --- | --- | --- |
| P_k | neutral − control | presence effect |
| VN_k | true − neutral | value effect: **penalty** (low tail), **reward** (high tail), against a size-matched reference |
| VC_k | true − control | the paper's penalty / reward (VC = VN + P) |
| toward/away | Q2's `tail_direction`, imported unchanged | read with the control as reference (drift VC, reference = control's signed error) and with the neutral arm as reference (drift VN, reference = neutral's signed error) |

## Pre-registered verdicts

**Presence** (margin M = 0.10 marks; per-tail tests Bonferroni over the two tails):

| verdict | rule |
| --- | --- |
| `PRESENCE-EFFECT` | some tail's P_k 97.5% interval excludes 0; each tail's sign named (+ / − / 0), opposite signs reported, not netted |
| `NO-PRESENCE-EFFECT-BOUNDED` | no tail resolved, and both tails' P_k 90% intervals inside ±0.10 |
| `UNRESOLVED` | otherwise; read as "no presence effect larger than X" (largest absolute 95% bound) |

Why 0.10: Gemini's per-tail value effects in Q2 were +0.24 and −0.22; a presence effect under 0.10
leaves more than half of each. It is also Q4's MAE margin.

**Readings.** Per tail: the value effect's class against each reference (+ / − if the 95% interval is
above / below 0, else 0) and the toward/away call against each reference.

| verdict | rule |
| --- | --- |
| `READINGS-HOLD` | in both tails, class(VN) = class(VC) and the toward/away call is the same against neutral as against control |
| `READINGS-CHANGE` | otherwise, naming each change (e.g. "high-tail direction: UNRESOLVED vs control → AWAY vs neutral") |

Q2's combined verdict is reported against each reference beside these.

## Detection floor (before any paid call)

Synthetic graders on the real draw: each answer's latent mark is the mean of Gemini's two existing
control marks on it (Q2 and the breadth re-run) plus ±0.25 uniform jitter; each arm adds its planted
effect and call noise, rounded to Gemini's 0.5-point grid and clipped. The noise is calibrated so two
null calls agree as often (76%) and differ by as much (SD 0.35) as Gemini's two control runs on this
draw. Planted effects carry learner (SD 0.10) and answer (presence 0.20, value 0.40) heterogeneity.
Value effects vs neutral: high label +0.22, low label −0.22. 200 replicates per world:

| world | planted presence (high, low) | pass |
| --- | --- | --- |
| NULL | 0, 0 | `PRESENCE-EFFECT` ≤ 10%; `READINGS-HOLD` ≥ 80%; VN signed and resolved in each tail ≥ 80%. Rate of `NO-PRESENCE-EFFECT-BOUNDED` reported; below 80% it is declared unreachable and an unresolved presence is read as an interval |
| PRES+ | +0.20, +0.20 | `PRESENCE-EFFECT` with no tail "−" ≥ 80%; any "−" ≤ 5% |
| PRES− | −0.20, −0.20 | the mirror |
| CHANGE | −0.22, 0 | `READINGS-CHANGE` ≥ 80% (reward vs control planted at 0, vs neutral +0.22) |

Written and scored by one session: a smoke check, reported as one. `--dump` refuses to read a real
dump until `out/floor.json` passes.

## Cost

Cap **$5**. About 1,200 calls at Q2's ~980 in / ~300 out tokens per call and list price ($0.30 /
$2.50 per million): about $1.25. `--max-calls 1300` is the binding guard (Google reports no spend);
the harness's 35% failure guard stays on. Spend = billed tokens × list price, from the dump's run
record, with the request body and served model.

## Data

JorGPT (`jorgpt-answers` in `data/data-sources.json`), read only by the harness. The per-case dump
stays in the session scratchpad and its sha256 is recorded below; only `out/*.json` aggregates are
committed. The outcome is a grader's mark on fixed work (not a learner outcome).

## Floor record: revision 0 failed, revision 1 passed, both before any model call

- **Revision 0 (as pre-registered at 3046048): FAILED** (`out/floor-rev0.json`). Under NULL,
  `READINGS-HOLD` came back in 73% (< 80%). Nearly every flip was the high tail's toward/away call
  (AWAY ↔ UNRESOLVED): Gemini's control error in the high tail is +0.20 [−0.02, +0.44] on this draw,
  on the edge of resolution, so a reference that differs from the control by noise flips the call.
  Its single-normal call noise also fitted Gemini badly (72% identical marks, SD 0.27, against 76%
  and 0.35).
- **Revision 1 (the instrument now; settled on synthetic worlds only):** call noise is a two-component
  mixture fitted to Gemini's identical-mark rate, difference SD and whole-point-jump rate (76% / 0.35 /
  8.3%; fit 74% / 0.37 / 5.3%). The readings verdict gains a third value: a call that changes in a
  tail whose presence effect is resolved (97.5%) is `READINGS-CHANGE`; a call that changes while that
  tail's presence effect is unresolved is **`READINGS-FRAGILE`** (the reading sits on its own
  resolution boundary); otherwise `READINGS-HOLD`. Pass rules: NULL `READINGS-CHANGE` ≤ 10%, CHANGE
  world `READINGS-CHANGE` ≥ 80%.
- **Revision 1: PASS** (`out/floor.json`, 200 replicates per world, 4,000 bootstrap replicates):

| world | presence verdicts | readings verdicts | VN signed, high / low |
| --- | --- | --- | --- |
| NULL | EFFECT 9.0% (false), BOUNDED 23.5%, UNRESOLVED 67.5% | CHANGE 4.0%, FRAGILE 28.5%, HOLD 67.5% | 97% / 94% |
| PRES+ (+0.20) | EFFECT 100%, no wrong sign | CHANGE 98.5% | 94% / 94% |
| PRES− (−0.20) | EFFECT 100%, no wrong sign | CHANGE 92.5% | 95% / 96% |
| CHANGE (−0.22 high only) | EFFECT 99% | CHANGE 97.5% | 98% / 96% |

What the floor says before any real number: a presence effect of 0.20 is found every time with the
right sign; **`NO-PRESENCE-EFFECT-BOUNDED` is unreachable** (23.5% < 80% under NULL), so an
unresolved presence effect is read only as "no presence effect larger than X"; and `READINGS-FRAGILE`
is common under NULL (28.5%), so it says a reading is boundary-sitting, not that presence moved it.

---

## Results

**Run.** One run, 2026-10-06 (`run muwyye9v-58ve`), `google:gemini-3.5-flash-lite`, 300 answers ×
4 arms = 1,200 gradings, **0 failed**, 300/300 complete in all four arms; all 1,200 served by
`gemini-3.5-flash-lite`; 0 reasoning tokens. Request body (from the dump's run record): Gemini API
`generateContent` v1beta, `generationConfig` = `responseMimeType: application/json`, `responseSchema`
sha256 d5483b2b10191927 (the same schema hash as Q2's and the breadth re-run's), `thinkingConfig:
{thinkingLevel: "minimal", includeThoughts: false}`; no temperature, top-p, seed or token limit.
**Spend $1.25** of the $5 cap (1,177,440 input and 359,708 output tokens × $0.30 / $2.50 per million).
The neutral length rule held on the dump (95 against 94.99, ratio 1.000).
**Per-case dump** (scratchpad, not committed): `neutral/swap-neutral-lite.json`,
sha256 `2bf6b5844b38f0cb4f859da13aa43afc0828f7d08583aa8d17f21293e7fb3533`. Aggregates:
`out/results.json`. All intervals are learner-cluster bootstrap 95% (4,000 replicates) unless marked.

**Reproduction first.** This run reproduces Q2's Gemini run: L +0.38 [+0.31, +0.46] against +0.37;
drift from control +0.22 (high tail) and −0.29 (low tail) against +0.24 and −0.22; control signed
error +0.15 / +0.48 against +0.20 / +0.49.

### Presence: `PRESENCE-EFFECT` (high tail +, low tail 0)

| tail | P = neutral − control | 97.5% (verdict) | reading |
| --- | --- | --- | --- |
| high (attainment ≥ 6) | **+0.14** [+0.05, +0.24] | [+0.04, +0.25] | a sentence about "this learner" that says nothing raises strong learners' marks |
| low (< 4) | −0.02 [−0.10, +0.06] | [−0.11, +0.07] | no presence effect resolved; no larger than 0.10 (90% [−0.08, +0.05]), but the bounded verdict was declared unreachable by the floor |
| pooled | +0.06 [+0.01, +0.12] | | reported only |

"No presence effect larger than" over both tails: 0.24.

### Penalty and reward against a size-matched reference

| tail | value effect vs neutral (true − neutral) | vs control (true − control; the paper's) |
| --- | --- | --- |
| high: **reward** | **+0.08 [−0.01, +0.17]** (unresolved) | +0.22 [+0.13, +0.31] |
| low: **penalty** | **−0.27 [−0.35, −0.18]** | −0.29 [−0.39, −0.19] |

### Toward/away (Q2 revision 3's rule, unchanged)

| tail | vs control: drift, reference error → call | vs neutral: drift, reference error → call |
| --- | --- | --- |
| high | +0.22, +0.15 [−0.08, +0.39] → UNRESOLVED | +0.08 (unresolved), +0.29 [+0.07, +0.54] → **FLAT** |
| low | −0.29, +0.48 [+0.19, +0.76] → TOWARD | −0.27, +0.47 [+0.20, +0.72] → TOWARD |
| combined (Q2's verdict) | UNRESOLVED | PRIOR (every moved tail TOWARD; the high tail no longer moves) |

### Readings: `READINGS-CHANGE` (high tail)

Changes, both in the high tail, where the presence effect is resolved:
- high-tail reward: + vs control → 0 vs neutral;
- high-tail direction: UNRESOLVED vs control → FLAT vs neutral.

The low tail holds: the penalty and its TOWARD call are the same against either reference.

### What this says

1. **On Gemini 3.5 Flash Lite, most of the "reward" is presence, not value.** Of the high label's
   +0.22 over a bare prompt, +0.14 is produced by any sentence about the learner in that slot; the
   label's own value adds +0.08, not resolved from zero. The signs check: P_high > 0 and VN_high + P_high
   = VC_high (0.08 + 0.14 = 0.22).
2. **The penalty is value, not presence.** The low label's −0.29 against the bare prompt is −0.27
   against the neutral sentence; in the low tail the sentence's mere presence does nothing resolvable
   (−0.02).
3. **The asymmetry is a presence effect in one tail only.** The neutral sentence raises strong
   learners' work (+0.14) and leaves weak learners' work where it was (−0.02). Why one tail and not the
   other was not asked and is not tested here; the high tail's answers have higher teacher marks, so
   any account in terms of the answers rather than the learners is open.
4. **L is untouched** (+0.38), as designed: both of its arms carry a sentence. The identical-work
   label effect remains the paper's clean estimand; the per-tail penalty/reward and toward/away
   readings against a bare control are not, on this model's high tail.
5. **Scope.** One model (the shipped tier), one neutral sentence, one draw. Whether other models show
   a presence effect, or another neutral wording moves marks differently, is not tested. The floor
   is a smoke check written and scored by this session.
