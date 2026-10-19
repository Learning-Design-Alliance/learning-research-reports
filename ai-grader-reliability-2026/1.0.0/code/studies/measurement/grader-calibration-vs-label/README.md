# Does a label-free calibration buy what the attainment label bought? (Paper VI)

**Status: RUN 2026-10-06.** Pre-registered, with the floor run, at 4bce18b, before any real estimand was computed. The design, the estimands, the verdict strings and their
margins are in the docstring of `calibrate.py`, which is the primary record. The floor (`out/floor.json`)
ran and was committed with the pre-registration, before any real estimand was computed; `--run` refuses
unless both are committed unchanged. Results go below the line; the plan above it is not rewritten.

## What is asked

No model calls and no corpus text: a reanalysis of existing per-case grader outputs (session
scratchpad, each verified against `studies/measurement/grader-eval/analyses/per-case-dumps.sha256`
before it is read). The outcome is a grader's mark on fixed work (`not-a-learner-outcome`).

Paper VI says the attainment label's QWK gain on some graders is "consistent with moving marks toward
where the teacher puts them, which QWK rewards. That is the kind of gain a calibration that does not use
the label (one shift and one stretch fitted to everybody) is designed to produce ... we did not test
whether it produces this one." This study tests it.

**Correction recorded before pre-registration.** The brief named GPT-4.1-mini, Qwen and Opus as the
graders the label helped; the coordinator corrected it: the runs whose true label raised QWK with a 95%
interval clear of 0 are **Claude Opus 5.5** (+0.029), **Llama 4 Maverick** (+0.046) and **GPT-5-mini at
minimal reasoning** (+0.039). These three are the summary set for (b) and (c); GPT-4.1-mini, Qwen,
GPT-5-mini (default) and Gemini 3.5 Flash Lite are reported with the same rules.

**Prior knowledge, stated.** An exploratory, non-pre-registered look (leave-one-student-out mean/SD
matching on the control arm) has been seen: calibrated control QWK rose on every model, e.g. Opus
0.682 → 0.814, Llama 0.706 → 0.755. That is question (a) and most of (b). The primary question is (c),
which that look did not touch.

## Design in one table

| piece | choice |
| --- | --- |
| data | swapped-label dumps: Gemini 3.5 Flash Lite, GPT-4.1-mini, GPT-5-mini (default), Qwen3-235B, Claude Opus 5.5, Llama 4 Maverick, GPT-5-mini (minimal, 223 complete) |
| calibration | label-free linear map per grader and arm: shift + stretch to the teacher's mean and SD (primary); least squares (sensitivity) |
| fitting | out of sample: leave-one-student-out (primary), leave-one-question-out (secondary); integer-rounded half-up, clipped to 0–10 before scoring |
| QWK | the paper's implementation (`grader-attainment-prior/analyse.py` = `harness/metrics.ts`) |
| (a) | calibrated control − raw control (ΔQWK, ΔMAE) |
| (b) | calibrated control − raw true label |
| **(c) primary** | calibrated true label − calibrated control (ΔQWK, ΔMAE, Δr): does the label add anything once both are calibrated? |
| interval | learner-cluster bootstrap within tail, 4,000 replicates, **calibration refitted inside every replicate**; one shared learner draw for all models so the summary-set mean has a joint interval |
| margins | ±0.02 QWK, ±0.10 MAE, ±0.02 r; bounded strings only where the floor shows them reachable |
| verdicts | (a) CALIBRATION-GAIN / -LOSS / NO-GAIN-BOUNDED / UNRESOLVED; (b) CALIBRATION-AT-LEAST-MATCHES-LABEL / LABEL-BETTER / UNRESOLVED; (c) LABEL-ADDS / LABEL-HURTS / LABEL-ADDS-NOTHING-BOUNDED / UNRESOLVED; across models, the summary-set mean's verdict plus a unanimity string |
| reported, not verdicts | cross-fit by question; least squares; tail transfer (map from one tail applied to the other); Gemini's map carried to another draw (history, grade-stratified) and to a second run of the same draw |
| floor | synthetic graders shaped from committed aggregates (Opus-, Llama-, GPT-5-mini-minimal-shaped, and a calibrated one) in five worlds: NULL, SHIFT-STRETCH (label gain is purely a shift and stretch), INFO-STRONG (the label makes marks track the teacher), INFO-MEASURED (reported), LABEL-WINS; plus the summary-set mean |

## Floor (run before any real estimand)

PASS on every scored check (200 replicates × 400 bootstrap per world; `out/floor.json`). The bounded
"label adds nothing" string is **unreachable** at n = 300 for every shape and for the summary-set mean
(≤ 36% of null replicates reach it), so (c) is read as an interval: "once both arms are calibrated the
label adds no more than X QWK". A label that makes marks track the teacher (planted +0.06 to +0.07 QWK
after calibration) is caught 189–200/200; false resolved effects in no-information worlds ≤ 7.5%. If the
measured label effect were all information, its calibrated gain would be +0.011 (Opus), +0.021 (Llama),
+0.053 (GPT-5-mini minimal), caught 13%, 32%, 69% of the time: a per-model null on Opus or Llama does
not rule out information of the measured size. A smoke check on synthetic graders written and scored
by this session, not a validation.

## Caveats fixed in advance

- **Same corpus, same questions.** One corpus (JorGPT), 35 questions, 33 learners; the calibration is
  fitted and tested on the same questions (the by-question cross-fit is the only check on that).
- **Tails-only draw.** The attainment draw holds the top and bottom of the learner distribution; a map
  fitted here sees a bimodal teacher distribution and may not carry to a representative class.
- **Calibration moves marks, not ranking.** A linear map leaves r unchanged (up to rounding and
  clipping); it cannot add information, and it does not address the group gaps the paper reports — the
  label's effect on identical work is untouched by rescaling every mark the same way.
- **Formative use.** In a product that writes feedback, the feedback text is written with the grader's
  own mark in mind; a mark rescaled after grading would no longer match the words the student reads.

---

## Results

`out/results.json` (primary), `out/results-all-arms.json` (deviation 1 sensitivity). Learner-cluster
bootstrap within tail, 4,000 replicates, calibration refitted in every replicate; 95% intervals.
Calibration = leave-one-student-out shift + stretch to the teacher's mean and SD, rounded and clipped.

### In one paragraph

A label-free shift and stretch raises QWK on every harsh grader by more than the label did, and on the
summary set (Opus 5.5, Llama 4, GPT-5-mini minimal) the calibrated control beats the raw labelled arm:
mean ΔQWK **+0.038 [+0.013, +0.061]**, `CALIBRATION-AT-LEAST-MATCHES-LABEL`. Once both arms are
calibrated, the label's remaining QWK advantage is **+0.014 [−0.008, +0.035]** on the summary mean
(raw label gain on the same models +0.038 [+0.017, +0.058]): `UNRESOLVED`, read as an interval —
**the label adds no more than +0.035 QWK beyond where marks land**. The point estimate keeps about a
third of the raw gain, and the floor showed this design cannot tell "nothing" from information of the
measured size on Opus or Llama, so "the label's gain is only a calibration effect" is *not*
established; what is established is that a label-free calibration buys at least as much QWK as the
label did. One resolved per-model signal: on Opus 5.5 the calibrated labelled arm has lower MAE than
the calibrated control, −0.073 [−0.152, −0.007] (`LABEL-ADDS` on MAE; QWK +0.010 [−0.008, +0.031]
unresolved).

### Per model (primary: leave-one-student-out, mean/SD map)

| model | n | QWK raw c → cal c | (a) ΔQWK / ΔMAE | (b) cal c − raw t, QWK / MAE | (c) cal t − cal c, QWK | (c) MAE | (c) r |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Claude Opus 5.5** | 300 | 0.682 → 0.814 | +0.132 [+0.091, +0.158] / −0.487 [−0.609, −0.304] GAIN | +0.103 [+0.066, +0.127] / −0.458 AT-LEAST (better) | +0.010 [−0.008, +0.031] UNRESOLVED | −0.073 [−0.152, −0.007] **LABEL-ADDS** | +0.009 [−0.008, +0.031] |
| **Llama 4 Maverick** | 300 | 0.706 → 0.755 | +0.049 [+0.021, +0.078] / −0.153 [−0.271, −0.023] GAIN | +0.003 [−0.049, +0.052] UNRESOLVED / −0.065 [−0.193, +0.094] AT-LEAST | +0.015 [−0.034, +0.059] UNRESOLVED | −0.023 [−0.148, +0.093] | +0.015 [−0.034, +0.059] |
| **GPT-5-mini (minimal)** | 242 | 0.726 → 0.772 | +0.047 [+0.024, +0.071] GAIN / −0.070 [−0.184, +0.075] UNRESOLVED | +0.008 [−0.035, +0.050] UNRESOLVED / −0.037 UNRESOLVED | +0.018 [−0.022, +0.054] UNRESOLVED | +0.021 [−0.145, +0.152] | +0.017 [−0.022, +0.054] |
| GPT-4.1-mini | 300 | 0.712 → 0.808 | +0.097 [+0.068, +0.117] / −0.305 GAIN | +0.093 [+0.059, +0.121] AT-LEAST (better) | +0.002 [−0.019, +0.031] UNRESOLVED | +0.043 [−0.056, +0.132] | +0.003 |
| GPT-5-mini (default) | 298 | 0.749 → 0.800 | +0.052 [+0.035, +0.069] GAIN / −0.072 UNRESOLVED | +0.053 [+0.028, +0.085] AT-LEAST (better) | +0.002 [−0.018, +0.028] UNRESOLVED | +0.044 [−0.114, +0.144] | +0.002 |
| Qwen3-235B | 291 | 0.719 → 0.817 | +0.098 [+0.072, +0.132] / −0.373 GAIN | +0.108 [+0.075, +0.150] AT-LEAST (better) | −0.011 [−0.042, +0.017] UNRESOLVED | +0.072 [−0.035, +0.205] | −0.013 |
| Gemini 3.5 Flash Lite | 300 | 0.809 → 0.817 | +0.008 [−0.011, +0.014] / −0.020 **NO-GAIN-BOUNDED** | +0.005 [−0.019, +0.017] AT-LEAST | +0.006 [−0.009, +0.026] UNRESOLVED | −0.023 [−0.136, +0.056] | +0.005 |

(c) is `UNRESOLVED` on QWK for every model, with the bounded string withheld as pre-registered
(unreachable on the floor). Largest QWK addition admitted (95% upper): Opus +0.031, Llama +0.059,
GPT-5-mini minimal +0.054, GPT-4.1-mini +0.031, GPT-5-mini default +0.028, Qwen +0.017, Gemini +0.026.

### Across models (summary set: Opus 5.5, Llama 4 Maverick, GPT-5-mini minimal)

| | summary-set mean | verdict | unanimity |
| --- | --- | --- | --- |
| (a) ΔQWK / ΔMAE | +0.076 [+0.057, +0.093] / −0.237 [−0.309, −0.136] | (reported) | GAIN on all three (QWK) |
| (b) QWK | **+0.038 [+0.013, +0.061]** | `CALIBRATION-AT-LEAST-MATCHES-LABEL` (calibration better) | MIXED: Opus AT-LEAST, Llama and GPT-5-mini minimal UNRESOLVED |
| (b) MAE | −0.187 [−0.250, −0.091] | `CALIBRATION-AT-LEAST-MATCHES-LABEL` (better) | |
| (c) QWK | **+0.014 [−0.008, +0.035]** | `UNRESOLVED`: adds no more than +0.035 | UNRESOLVED on all three |
| (c) MAE / r | −0.025 [−0.102, +0.034] / +0.014 [−0.008, +0.034] | UNRESOLVED / UNRESOLVED | |
| raw label gain (for scale) | +0.038 [+0.017, +0.058] | | |

Pre-registered reading: none of the three readings fires. Not "the label's gain is what a shift and
stretch buys" (that needed a bounded or within-margin (c)); not "the label carries information beyond
where marks land" (that needed (c) resolved above 0). The honest sentence for the paper: *a label-free
calibration recovers at least the QWK the label bought; whether the label carries anything beyond that
is unresolved at n = 300, bounded at +0.035 QWK on the three graders it helped.*

### Transfer and robustness (reported, not verdicts)

- **T1, cross-fit by question** (leave-one-question-out): every QWK estimand within 0.015 of the
  by-student value (MAE on GPT-5-mini minimal moves most: (c) +0.021 → −0.062, both unresolved); summary (b) +0.035 [+0.009, +0.061], (c) +0.017 [−0.008, +0.036]. Same verdicts.
- **T2, least squares instead of mean/SD**: LS shrinks toward the mean, which QWK penalises, so its
  calibration gain is smaller (summary (a) +0.042 vs +0.076) and **(b) on the summary mean drops to
  +0.004 [−0.035, +0.032], `UNRESOLVED`**. "Calibration at least matches the label" holds for the
  mean/SD map, not for any linear map. (c) under LS +0.018 [−0.012, +0.049]; Opus's MAE `LABEL-ADDS`
  survives under LS (−0.067 [−0.139, −0.013]).
- **T3, tail transfer** (each tail marked with the other tail's map; deliberately hostile — the tails'
  teacher means differ by ~3 points): QWK still at or above raw on harsh graders (Opus 0.776 vs raw
  0.682, cross-fit 0.814; Qwen 0.815; GPT-4.1-mini 0.805; Llama 0.740 vs 0.706) but below the
  all-learner cross-fit, and per-tail errors open up: low tail +0.40 to +0.60 too generous on Opus,
  Qwen, Llama and GPT-5-mini default; Gemini high −0.52 / low +0.43. A map fitted on one kind of class
  and applied to another overshoots in the direction the paper warned.
- **T4, another draw (Gemini only)**: the attainment-draw map applied to the grade-stratified history
  draw (n = 150, 19 answers shared) moved QWK 0.836 → 0.847, MAE 1.22 → 1.19, leaving bias +0.29
  (in-draw cross-fit 0.841, bias +0.05); the reverse moved 0.809 → 0.819. A map fitted on run 1 and
  applied to run 2 of the same draw: QWK 0.813 → 0.813, MAE 1.27 → 1.26. No overshoot for a grader
  that was nearly calibrated already; this check says nothing about the harsh graders, which ran on
  one draw only.
- **Deviation 1** (docstring): the primary filter keeps rows with control and true-label marks
  (GPT-5-mini minimal 242, not the 223 complete in all three arms quoted in the plan). On the paper's
  all-arms basis (`results-all-arms.json`): GPT-5-mini minimal (b) +0.009 [−0.040, +0.045], (c)
  +0.016 [−0.022, +0.056]; summary (b) +0.038 [+0.011, +0.060], (c) +0.014 [−0.008, +0.036]. Every
  verdict unchanged.
- **Direction check**: the calibrated control's mean error is closer to 0 than the raw one's on every
  harsh grader (Opus −1.31 → −0.04, Qwen −0.96 → −0.01, GPT-4.1-mini −0.89 → +0.01, Llama −0.79 →
  +0.06). GPT-5-mini minimal is not off in mean (−0.07 → −0.16); its gain is the stretch.

### What this does not say (caveats above, restated)

Same corpus and questions; tails-only draw; a linear map leaves r unchanged and does nothing about the
label's effect on identical work or the group gaps; and a mark rescaled after grading no longer matches
the feedback text the grader wrote for it.
