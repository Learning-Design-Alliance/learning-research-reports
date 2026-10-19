# Remnant-adjusted re-estimate of the four-order experiment, and power for edge release

Script: `remnant.py` (its docstring is the pre-registration, committed before any real data were
read). Outputs: `out/floor.json`, `out/remnant-result.json`, `out/power.json`, `out/history-entry.json`.
Literature review rank 8 (strand 4: Sales et al. 2023 with Gagnon-Bartsch et al. 2023; Hedges & Hedberg
2007; Lortie-Forgues & Inglis 2019).

## What was asked

1. Does Paper II's F4 order result (ASSISTments experiment PSABANRN, `studies/identifiability/core-vs-culture/order_swap.py`:
   problems to mastery, omnibus p 0.0035, T1-T3 -1.4947 problems, 90% interval [-2.2425, -0.7654],
   ORDER MATTERS) survive, and how much does it sharpen, when the estimator uses a prediction built only
   from students who were not in the experiment?
2. How many learners, classes or encounters would a randomized edge-release trial need at 0.05, 0.10 and
   0.30 SD, with and without that covariate?
3. Do the randomized mastery-requirement experiments identify the next dependent skill?

## Data

`osf-59shv` (ASSISTments; research use, no redistribution; aggregates only). `student_id` is shared
across the release's 88 experiments, so non-participants are identifiable: the remnant is every
student-experiment pair in the other 87 experiments whose student never appears in PSABANRN (1,193
excluded). Features are the per-student and per-class `priors.csv` fields, all recorded before each
experiment. `license.txt` is not in this machine's copy; the terms in `data/data-sources.json` were
applied. The 2012-13 export `assist_rich.csv` was not linked: it is a different year and anonymization,
and nothing maps one id space to the other.

## Detection floor: PASS

Synthetic data with the original arm sizes (247/245/206/234), a right-skewed count outcome, and a planted
T1-T3 of -1.0 problem (200 simulations per setting, 300 bootstrap draws each). The adjusted estimate was
unbiased (mean -0.995, -0.989, -0.987 at covariate strength r = 0, 0.35, 0.6). A useless covariate cost
nothing (variance ratio 1.005). A useful one gained what theory predicts (0.842 against 1 - R² = 0.836).
The 90% interval covered in 0.855-0.930 of runs. At r = 0.35 the interval lay below zero in 0.99 of
runs and above zero in none. Under no effect, the permutation omnibus rejected at 0.05 in 0.075 of runs.

## Result 1: the verdict is unchanged, and about a fifth more precise

Remnant model (ridge, penalty chosen by 5-fold CV grouped by experiment on the remnant only):

- Problems to mastery: 68 experiments and 50,127 rows; grouped-CV R² 0.030 on the remnant. The
  penalty chosen, 1000, is the edge of the pre-registered grid.
- Completion: 82 experiments and 91,925 rows; R² 0.138.

Applied to PSABANRN, its prediction correlates with the outcome within arm at +0.386 (problems) and
+0.405 (completion). The sign is right.

| Problems to mastery (completers) | unadjusted (arm means) | remnant-adjusted (ReLOOP-style) | variance ratio |
| --- | --- | --- | --- |
| omnibus permutation p (10,000 relabellings of students) | 0.0047 | **0.0013** | |
| T1-T3 | -1.4947 [-2.2417, -0.7558] | **-1.4737 [-2.1558, -0.8093]** | **0.828** |
| T2-T3 | -0.8498 [-1.6148, -0.0879] | -0.9319 [-1.6135, -0.2336] | 0.813 |
| T3-T4 | +1.0732 [+0.3334, +1.8021] | +1.0027 [+0.3178, +1.6719] | 0.826 |
| T1-T2 | -0.6450 [-1.2867, +0.0105] | -0.5418 [-1.1227, +0.0619] | 0.845 |
| T1-T4 | -0.4215 [-1.0531, +0.2034] | -0.4709 [-1.0796, +0.1220] | 0.889 |
| T2-T4 | +0.2235 [-0.4256, +0.8853] | +0.0708 [-0.5420, +0.6682] | 0.860 |

All intervals are 90% percentile bootstrap intervals, resampling students within arm (5,000 draws).
The adjusted and unadjusted estimators are computed on the same draws. n per arm: 247, 245, 206, 234
completers. The unadjusted column re-runs the original estimator. Its omnibus p (0.0047) and interval
differ from the original's (0.0035; [-2.2425, -0.7654]) only through the random draws.

- **Completion:** omnibus p 0.813 unadjusted and 0.849 adjusted. Every adjusted pairwise difference
  lies between -0.0242 and +0.0008. The median variance ratio is 0.843.
- **Verdicts:**
  - V1 order verdict: **ORDER MATTERS, VERDICT UNCHANGED**.
  - V2 headline pair: **T1-T3 CONFIRMED**. Treatment 1 needs fewer problems, and the adjusted
    interval lies entirely below zero.
  - V3 precision: **PRECISION GAIN**. On T1-T3 the variance ratio is 0.828, equivalent to about 21%
    more students. The median over the six pairs is 0.837 for problems and 0.843 for completion.
- **MDE:** this experiment's minimum detectable T1-T3 difference (80% power, two-sided 0.05) falls
  from 1.25 to 1.14 problems, which is 0.278 to 0.253 within-arm SD (SD 4.51 problems). The observed
  T1-T3 is -0.331 SD.
- **Deranged control: CONTROL PASSED.** The same covariate values, deranged across students, gave a
  T1-T3 variance ratio of 0.984 (all twelve pairs 0.984-1.003). Its estimate, -1.5091, lies inside
  the unadjusted interval.

The gain matches Sales et al.'s (2023) average of about 20% across ASSISTments A/B tests, from a much
simpler model (ridge on 21 prior fields, not a deep network on action logs).

## Result 2: clustering and sample size for edge release

ICCs come from this experiment, on outcomes centred by arm. Each 90% interval resamples 2,000
classes, or teachers, with replacement.

| ICC | estimate [90%] | groups / students |
| --- | --- | --- |
| problems to mastery, class | 0.096 [0.057, 0.136] | 65 / 928 |
| problems to mastery, teacher | 0.091 [0.055, 0.125] | 38 / 930 |
| completion, class | 0.097 [0.052, 0.145] | 67 / 1,190 |
| after the remnant covariate, class | problems 0.095, completion 0.045 | |
| first-attempt correctness, learner (encounter level; 500 draws) | 0.149 [0.129, 0.170] | 1,104 learners / 7,683 attempts |

Sample needed (two arms, two-sided alpha 0.05, power 0.80, normal approximation). The median
participant class has 13 students. "Remnant" uses the realized variance ratio, 0.828; class-level
variance is assumed unreduced.

| effect (SD) | per learner, n per arm: none / remnant | per class, classes per arm at m = 13 / 20: this ICC 0.096 | with remnant | H&H rho 0.15 | H&H rho 0.25 | H&H with pretest (rho 0.239, eta_B 0.210, eta_W 0.360) | per encounter: total / learners at K = 5 / K = 20 (remnant total) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.05 | 6,280 / 5,203 | 1,040 / 887 | 965 / 839 | 1,353 / 1,209 | 1,933 / 1,806 | 448 / 402 | 10,690 / 2,138 / 535 (8,856) |
| 0.10 | 1,570 / 1,301 | 260 / 222 | 242 / 210 | 339 / 303 | 484 / 452 | 112 / 101 | 2,673 / 535 / 134 (2,214) |
| 0.30 | 175 / 145 | 29 / 25 | 27 / 24 | 38 / 34 | 54 / 51 | 13 / 12 | 297 / 60 / 15 (246) |

- **Published planning values.** The Clements-Sarama ICPSR data are not on this machine, so the
  classroom case also uses Hedges & Hedberg's working paper (IPR WP-06-12, the draft of the 2007
  article; text read 2026-10-07). It recommends rho 0.15-0.25 for national samples, with 0.228 for
  grade-1 mathematics, unconditional. Its grade-1 reading example with a pretest at both levels gives
  eta_B 0.210 and eta_W 0.360. These are school-level values, used as planning anchors and not as
  estimates for classrooms.
- **Comparison with `lt-trials/out/arm_power.json`.** Its 291-385 per arm "for 0.10" is an absolute
  accuracy difference at p 0.5-0.8, which is 0.20-0.23 SD. At 0.10 SD a per-learner trial needs 1,570
  per arm (1,301 with the remnant covariate), 4.1 to 5.4 times as many.
- **Assignment unit.** Per-pair-encounter randomization needs the fewest learners. It also rests on
  two assumptions the per-learner design does not need: no carryover between encounters, and an
  effect measured in encounter-level SD.
- **Reading at 0.05-0.10 SD.** This is Lortie-Forgues & Inglis's large-trial range. Class
  randomization needs hundreds of classes per arm, and per-learner randomization needs thousands of
  learners. Only an encounter-randomized design with many encounters per learner reaches the hundreds.

## Result 3 (noted, not run)

The mastery-requirement experiments are:

- PSAVTMK (four arms);
- PSAZGQM (four arms);
- PSAXJC2 (46 students);
- PSA59TP and PSAUTWT (choice and no-choice).

Their posttests are on the same skill, and no row names a next skill. Because `student_id` is shared
across experiments, many of these students appear in later experiments. For example, 206 of PSAVTMK's
students appear later in PSAHQV, and 543 of PSA59TP's appear later in PSAHQV. A later study must first
establish from the experiment tag paths whether any later experiment's skill depends on the gated one.

## What it can and cannot say

It says the F4 order effect does not depend on the estimator. A covariate that no participant's outcome
touched leaves the direction and verdict unchanged, and narrows the headline interval by about a tenth.
It cannot say which treatment is which order (the release does not label them). It cannot say anything
about a dependency (the four measures are not prerequisites of each other). Problems to mastery is
compared among completers, so, as in the original, it conditions on an outcome. The power table rests on
a normal approximation (no t correction for few classes) and on the stated assumptions about class-level
variance and carryover.

## Planning values at the effect the atlas tests for (`planning_abs.py`, 2026-10-13)

`power.json` sizes a release trial in standard-deviation units (0.05, 0.10, 0.30 SD). The effect the
positivity atlas tests for is an absolute drop of 0.10 in accuracy, 0.202 to 0.232 SD at accuracies
0.5 to 0.8 (`lt_trials_comparison`). `planning_abs.py` evaluates the same formulas at those two values,
after asserting that it reproduces every stored 0.10 SD value, and writes `out/planning-abs.json`. It
reads no corpus. Per arm: 291 to 385 learners (1,570 at 0.10 SD); 241 to 319 with the remnant
covariate; 49 to 64 classes of 13 and 42 to 55 of 20 at this experiment's ICC; 129 to 170 classes of 13
at the length trial's ICC of 0.395. Encounters, over both arms: 495 to 655, or 99 to 131 learners with 5
each. Paper II's Table 16 prints both columns.
