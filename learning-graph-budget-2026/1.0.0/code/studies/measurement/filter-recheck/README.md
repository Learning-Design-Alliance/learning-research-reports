# Filter re-check: do graph-state's and S2's headlines move under moment matching?

S3 (`../grey-box/`, its CHANGE 3) found a problem in the coupled filter's update step,
`gstate.run_gauss`. That step is one Laplace (extended-Kalman) step at the predictive point. With the true
parameters of a synthetic world it preferred a spurious general learning term and fell 46 nats behind
an exact filter. Moment matching (assumed-density filtering) closed most of that gap. Graph-state's C2
family and S2's Part A (its C2, C2g and the g-tracker behind A1) use the Laplace step. Their numbers feed
the engine recommendation: implement A1 first.

This study re-runs both studies with one change. Every call of the coupled filter uses moment matching,
not the Laplace step. Everything else is the original code: subsamples, splits, items, seeds and verdict
functions. This is a re-check, not a rewrite. The original studies' code and `out/` are untouched.

Files:

- `filter_recheck.py`: the pre-registration (its docstring, committed at a29cf54 before any run),
  CHANGE 1, the driver and the comparison.
- `fstep.py`: the update step (Laplace or moment matching), and copies of `gstate.run_gauss` and
  `tstate.run_joint` with the step selectable. With the Laplace step they equal the originals exactly.
- `out/`: aggregates only.
  - `synthetic.json`: the check against an exact filter.
  - `gs-*.json`, `s2-*.json`: the moment-matching runs.
  - `gs-lap-*.json`, `s2-lap-*.json`: the Laplace re-runs (CHANGE 1).
  - `comparison.json`: every headline, with its rule and status.

These are answers about the formulas on open corpora, not about Lazuli's items or learners.

## The short answer

**The engine recommendation stands, with two ranges widened.**

- **Implement A1 first: STANDS.** Under moment matching, A1 reads PRIOR-ONLY CAPTURES MOST on all three
  corpora. Its calibration guard holds, and it does not worsen the next attempt. Every Part A verdict
  string is unchanged.
- **"A1 captures 0.91-1.01 of the coupled state's cold-skill gain": MOVED, to 0.88-1.05.**
  - ASSISTments: 1.05 [1.00, 1.10].
  - XES3G5M: 0.88 [0.86, 0.91]. Only XES3G5M crosses the pre-stated rule.
  - Eedi: 0.92 [0.91, 0.94].
  - Why: the coupled state C2, the denominator, gains more under moment matching (+0.002 nats on
    XES3G5M and Eedi). A1, the numerator, is the engine's own Beta and moves only through g_hat
    (+0.0006 to +0.0009).
- **"One general factor gives 95-99% of the gain": MOVED, to 93-100%.**
  - XES3G5M: 0.947 to 0.930 [0.917, 0.943]. The rank the filter selects rises from 8 to 12 there; the
    two ranks are within 0.0001 nats on validation.
  - Eedi: 0.991 to 0.982 [0.975, 0.991]. The move only just exceeds the interval half-width.
  - ASSISTments holds (0.998).
  - S2's version of the claim, at fixed ranks, holds on all three: 0.96-1.00.
- **The coupled state's predictive intervals are still calibrated.** The engine's are still too wide at
  first encounters. A1's cold-window intervals are still less under-confident than C0's.
- **Every verdict string holds.** In graph-state these are coupling, graph, which skills and the
  next-attempt guard. In S2 they are the six Part A verdicts.
  - The headline gains move by less than their own interval half-widths: C2's cold gain, its
    every-attempt gain, the coupling attribution, the C3 retention and the items saved.
- **What moved is the size of specific (non-general) coupling, and only on XES3G5M.**
  - C2's margin over its deranged control rises from +0.0075 to +0.0089.
  - C3g's margin over C2g rises from +0.0010 to +0.0013.
  - These move with the rank, not against the verdicts: the general level still carries over 90%.
- **The changes come from the step, not from drift.** The Laplace re-runs reproduce the original
  records to within 6% of every threshold.
- **Moment matching is the better filter where it can be checked exactly.** In grey-box's world W3, at
  true parameters, the Laplace step falls 201 and 224 nats behind the exact filter, about 0.0004 nats
  per answer. It under-predicts at every learner volume. Moment matching falls 31 and 26 nats behind.

## Engine bottom line

The product recommendation is unchanged: build A1, the learner-informed cold-start prior with a
per-skill map, first.

Its value is a little lower on XES3G5M and a little higher on ASSISTments than reported:

- 0.88-1.05 of the full coupled state's first-encounter gain;
- +0.041 to +0.065 nats per first attempt over C0;
- 17-59 unneeded items saved per 1,000 attempts at matched 20% risk.

The full coupled state is now credited with slightly more on XES3G5M and Eedi. That is the gap A2-orth
and C2g close. A2-orth's share of C2's every-attempt gain moves from 0.82 to 0.79 (XES3G5M) and from
0.87 to 0.85 (Eedi). A2-orth's own increment over A1 is unchanged (+0.0013 / +0.0019 / +0.0049).

The general-factor claim should read 93-100%, not 95-99%. An engine that adopts the coupled filter
should use moment matching. It costs the same per response and is closer to exact.

## Synthetic check (`out/synthetic.json`)

Grey-box's world W3: 2,000 learners, 30 skills, a general factor, true items and prior, no forgetting.
Both registered seeds.

| check | seed 20261002 | seed 20261003 | rule | passes |
| --- | --- | --- | --- | --- |
| identity: copies with the Laplace step vs gstate.run_gauss (dense, arrow) and tstate.run_joint | 0 / 0 / 9e-16 | 0 / 0 / 7e-16 | < 1e-9 | yes |
| agreement: first-attempt P identical under both steps | 0 | 0 | < 1e-12 | yes |
| agreement: step at v = 0, c = 0, d = 1 (relative) | 6.3e-10 | 6.3e-10 | < 1e-9 | yes |
| agreement: prior variance x 1e-4, c = 0, d = 1, max abs dP | 8e-8 | 8e-8 | < 1e-3 | yes |
| Laplace behind exact, total nats (per answer) | 200.8 (0.00035 [0.00028, 0.00041]) | 223.6 (0.00039 [0.00031, 0.00046]) | | |
| moment matching behind exact, total nats (per answer) | 31.3 (0.00005 [0.00003, 0.00008]) | 26.2 (0.00005 [0.00002, 0.00007]) | <= 0.001 per answer and below Laplace | yes |
| mean residual y - P, learner's attempts 0-50 / 50-150 / 150-300 / 300+: exact | +0.0003 / -0.0002 / +0.0018 / -0.0034 | +0.0007 / -0.0010 / -0.0004 / +0.0009 | | |
| the same, Laplace | +0.0061 / +0.0066 / +0.0085 / +0.0031 | +0.0077 / +0.0070 / +0.0073 / +0.0083 | | |
| the same, moment matching | +0.0005 / -0.0002 / +0.0019 / -0.0033 | +0.0008 / -0.0009 / -0.0003 / +0.0010 | | |

The Laplace step's update ignores the predictive variance. Its forecasts come out too low by 0.6-0.8
percentage points at every learner volume.
Moment matching tracks the exact filter's residual to 0.0002. At true items the two steps' forecasts
differ by 0.008-0.009 in P on average (at most 0.09).

## Reproduction and CHANGE 1

The pre-registered R1 and R2 assumed bitwise reproduction. They failed for a numerical reason.
calibrate.py's empirical-Bayes EM, which sets C0's prior, follows a different floating-point path at a
different BLAS thread count. On identical ASSISTments data its 2PL prior took 34 EM rounds in the
original log, 32 at 2 threads and 36 at 1 thread. C0's log loss moved by 1.7-2.8e-5.

The data are identical: every subset count, and CLIM's log loss bit for bit, on all nine records. CHANGE
1 (committed before any further moment-matching number was read) adds a same-environment reference.
Each pipeline is run end to end again with the original Laplace step. The registered comparison is
still original record against moment matching. Beside it are the drift (Laplace re-run minus original)
and the step's effect (moment matching minus Laplace re-run).

The drift is negligible. The largest is 6% of a headline's threshold (items saved, ASSISTments, +0.2 per
1,000). Every Laplace re-run reproduces its record's verdicts and chosen rank. No cell is "MOVED
(drift)": every MOVED cell moved because of the step.

One moment-matching line was seen before CHANGE 1 was written: S2 Eedi's Part A verdicts and A1's share,
0.925 [0.905, 0.942]. The progress monitor displayed it.

## Original vs re-computed

Materiality rules, stated before any run:

- (a) a number with an original interval moves if it shifts by more than that interval's half-width;
- (b) the general-factor share, which had no original interval, moves if it shifts by more than the
  re-computed interval's half-width;
- (c) a coverage moves if any level shifts by more than 0.02;
- (d) a verdict or label moves if it differs.

A row is MOVED if any corpus moves. Intervals are 95% learner-bootstrap percentile intervals (B = 200).
**Eedi outputs refreshed, 2026-10-09.** The four Eedi files (`out/gs-eedi.json`, `out/gs-lap-eedi.json`,
`out/s2-eedi.json`, `out/s2-lap-eedi.json`) as first committed failed the script's own reproduction checks
(R2 off by 3.35e-6 for the two graph-state files, R1 by 2.62e-5 for S2), and `s2-eedi.json` predated the
`R1_CLIM_logloss_diff` field, so they had been written from an earlier state of the inputs or the
script. Rerun at the release commit from the registry-verified `answers.tsv`
(MD5 63f6af8cf12132f6dff578832dd433e5), all four pass every check exactly; 15 cells move across the
information cut. An independent verification run on another machine got the same files. Of the
tables below, 11 Eedi cells change in their last printed digit and no status or verdict changes. The
article's one number from these files, the Eedi retained share 0.352 [0.333, 0.370], is unchanged.

Gains are in nats per attempt over C0. "Laplace re-run" is CHANGE 1's reference. The full record,
including warm windows and C0's own intervals, is `out/comparison.json`.

### Graph-state (`../graph-state/out/*.json`)

| headline | corpus | original | moment matching | Laplace re-run | status |
| --- | --- | --- | --- | --- | --- |
| GS1 C2 M1 gain over C0 | XES3G5M | +0.0457 [+0.0424, +0.0486] | +0.0481 [+0.0446, +0.0510] | +0.0457 [+0.0424, +0.0486] | HOLDS |
|  | ASSISTments | +0.0473 [+0.0423, +0.0533] | +0.0462 [+0.0414, +0.0522] | +0.0473 [+0.0424, +0.0533] | HOLDS |
|  | Eedi | +0.0672 [+0.0634, +0.0711] | +0.0691 [+0.0652, +0.0731] | +0.0672 [+0.0634, +0.0711] | HOLDS |
| GS2 C2g share of C2's M1 gain | XES3G5M | 0.947 | 0.930 [0.917, 0.943] | 0.947 [0.934, 0.958] | MOVED |
|  | ASSISTments | 0.995 | 0.998 [0.983, 1.014] | 0.995 [0.979, 1.010] | HOLDS |
|  | Eedi | 0.991 | 0.982 [0.975, 0.991] | 0.991 [0.983, 1.001] | MOVED |
| GS2b C2g M1 gain over C0 | XES3G5M | +0.0433 [+0.0398, +0.0460] | +0.0447 [+0.0413, +0.0474] | +0.0433 [+0.0398, +0.0460] | HOLDS |
|  | ASSISTments | +0.0470 [+0.0422, +0.0534] | +0.0461 [+0.0415, +0.0523] | +0.0470 [+0.0423, +0.0534] | HOLDS |
|  | Eedi | +0.0666 [+0.0632, +0.0704] | +0.0679 [+0.0643, +0.0722] | +0.0666 [+0.0632, +0.0704] | HOLDS |
| GS3 C2 over C2-diag, M1 | XES3G5M | +0.0456 [+0.0420, +0.0487] | +0.0478 [+0.0442, +0.0507] | +0.0456 [+0.0420, +0.0487] | HOLDS |
|  | ASSISTments | +0.0322 [+0.0273, +0.0378] | +0.0299 [+0.0249, +0.0352] | +0.0322 [+0.0273, +0.0378] | HOLDS |
|  | Eedi | +0.0656 [+0.0617, +0.0698] | +0.0671 [+0.0632, +0.0712] | +0.0656 [+0.0617, +0.0698] | HOLDS |
| GS4 C2 over C2-shuf, M1 | XES3G5M | +0.0075 [+0.0069, +0.0083] | +0.0089 [+0.0081, +0.0096] | +0.0075 [+0.0069, +0.0083] | MOVED |
|  | ASSISTments | +0.0016 [+0.0004, +0.0026] | +0.0015 [+0.0004, +0.0026] | +0.0016 [+0.0004, +0.0026] | HOLDS |
|  | Eedi | +0.0052 [+0.0044, +0.0059] | +0.0052 [+0.0045, +0.0059] | +0.0052 [+0.0044, +0.0059] | HOLDS |
| GS5 C3 retention | XES3G5M | 0.141 [0.132, 0.151] | 0.143 [0.134, 0.152] | 0.141 [0.132, 0.151] | HOLDS |
|  | Eedi | 0.348 [0.328, 0.365] | 0.352 [0.333, 0.370] | 0.348 [0.328, 0.365] | HOLDS |
| GS5b C3g over C2g, M1 | XES3G5M | +0.0010 [+0.0008, +0.0013] | +0.0013 [+0.0011, +0.0015] | +0.0010 [+0.0008, +0.0013] | MOVED |
|  | Eedi | +0.0020 [+0.0014, +0.0025] | +0.0024 [+0.0019, +0.0029] | +0.0020 [+0.0014, +0.0025] | HOLDS |
| GS6 C2 M2 gain over C0 | XES3G5M | +0.0358 [+0.0332, +0.0377] | +0.0379 [+0.0357, +0.0398] | +0.0358 [+0.0333, +0.0377] | HOLDS |
|  | ASSISTments | +0.0198 [+0.0185, +0.0211] | +0.0200 [+0.0187, +0.0212] | +0.0199 [+0.0185, +0.0211] | HOLDS |
|  | Eedi | +0.0373 [+0.0357, +0.0392] | +0.0389 [+0.0373, +0.0410] | +0.0373 [+0.0357, +0.0392] | HOLDS |
| GS7 C2 intervals, cold | XES3G5M | 0.50 / 0.79 / 0.94 CALIBRATED | 0.50 / 0.78 / 0.94 CALIBRATED | 0.50 / 0.79 / 0.94 CALIBRATED | HOLDS |
|  | ASSISTments | 0.51 / 0.80 / 0.95 CALIBRATED | 0.50 / 0.79 / 0.94 CALIBRATED | 0.51 / 0.80 / 0.95 CALIBRATED | HOLDS |
|  | Eedi | 0.50 / 0.79 / 0.95 CALIBRATED | 0.48 / 0.78 / 0.94 CALIBRATED | 0.50 / 0.79 / 0.95 CALIBRATED | HOLDS |
| GS7 C2 intervals, warm | XES3G5M | 0.49 / 0.78 / 0.94 CALIBRATED | 0.48 / 0.77 / 0.94 CALIBRATED | 0.49 / 0.78 / 0.94 CALIBRATED | HOLDS |
|  | ASSISTments | 0.48 / 0.78 / 0.94 CALIBRATED | 0.48 / 0.78 / 0.94 CALIBRATED | 0.48 / 0.78 / 0.94 CALIBRATED | HOLDS |
|  | Eedi | 0.49 / 0.79 / 0.94 CALIBRATED | 0.48 / 0.78 / 0.94 CALIBRATED | 0.49 / 0.79 / 0.94 CALIBRATED | HOLDS |
| GS8 C2 items saved per 1,000, 20% risk | XES3G5M | +74.3 [+69.3, +78.1] | +75.7 [+70.4, +79.6] | +74.4 [+69.3, +78.0] | HOLDS |
|  | ASSISTments | +25.5 [+22.1, +29.2] | +25.5 [+22.3, +29.2] | +25.7 [+22.2, +29.2] | HOLDS |
|  | Eedi | +53.2 [+50.4, +55.8] | +54.5 [+51.7, +57.6] | +53.2 [+50.4, +55.8] | HOLDS |
| GS9 chosen rank (reported) | XES3G5M | 8 | 12 | 8 | REPORTED |
|  | ASSISTments | 2 | 2 | 2 | REPORTED |
|  | Eedi | 8 | 8 | 8 | REPORTED |

### S2 Part A (`../state-timescales/out/*.json`, key A)

| headline | corpus | original | moment matching | Laplace re-run | status |
| --- | --- | --- | --- | --- | --- |
| A1 A1 share of C2's cold gain | ASSISTments | 1.007 [0.961, 1.054] | 1.050 [1.003, 1.100] | 1.006 [0.961, 1.053] | HOLDS |
|  | XES3G5M | 0.912 [0.885, 0.938] | 0.883 [0.861, 0.907] | 0.912 [0.885, 0.938] | MOVED |
|  | Eedi | 0.942 [0.922, 0.962] | 0.925 [0.905, 0.942] | 0.942 [0.922, 0.962] | HOLDS |
| A2 C2 cold gain over C0 | ASSISTments | +0.0473 [+0.0419, +0.0527] | +0.0462 [+0.0411, +0.0516] | +0.0473 [+0.0419, +0.0527] | HOLDS |
|  | XES3G5M | +0.0443 [+0.0395, +0.0495] | +0.0464 [+0.0416, +0.0517] | +0.0443 [+0.0395, +0.0495] | HOLDS |
|  | Eedi | +0.0682 [+0.0631, +0.0735] | +0.0700 [+0.0646, +0.0757] | +0.0682 [+0.0631, +0.0735] | HOLDS |
| A2b A1 cold gain over C0 | ASSISTments | +0.0476 [+0.0424, +0.0533] | +0.0485 [+0.0432, +0.0543] | +0.0476 [+0.0424, +0.0533] | HOLDS |
|  | XES3G5M | +0.0404 [+0.0360, +0.0457] | +0.0410 [+0.0366, +0.0462] | +0.0404 [+0.0360, +0.0457] | HOLDS |
|  | Eedi | +0.0642 [+0.0590, +0.0691] | +0.0648 [+0.0595, +0.0697] | +0.0642 [+0.0590, +0.0691] | HOLDS |
| A3 C2g share of C2's cold gain | ASSISTments | 0.995 [0.977, 1.008] | 0.998 [0.979, 1.012] | 0.995 [0.977, 1.009] | HOLDS |
|  | XES3G5M | 0.968 [0.949, 0.989] | 0.957 [0.938, 0.976] | 0.968 [0.949, 0.989] | HOLDS |
|  | Eedi | 0.993 [0.981, 1.010] | 0.985 [0.974, 1.001] | 0.993 [0.981, 1.010] | HOLDS |
| A4 A1-global share | ASSISTments | 0.582 [0.519, 0.639] | 0.613 [0.552, 0.668] | 0.582 [0.519, 0.639] | HOLDS |
|  | XES3G5M | 0.838 [0.814, 0.865] | 0.819 [0.797, 0.841] | 0.838 [0.814, 0.865] | HOLDS |
|  | Eedi | 0.862 [0.835, 0.885] | 0.856 [0.831, 0.876] | 0.862 [0.835, 0.885] | HOLDS |
| A5 A2-orth over A1, every attempt | ASSISTments | +0.0012 [+0.0009, +0.0015] | +0.0013 [+0.0010, +0.0015] | +0.0012 [+0.0009, +0.0015] | HOLDS |
|  | XES3G5M | +0.0019 [+0.0017, +0.0022] | +0.0019 [+0.0017, +0.0022] | +0.0019 [+0.0017, +0.0022] | HOLDS |
|  | Eedi | +0.0048 [+0.0041, +0.0055] | +0.0049 [+0.0041, +0.0056] | +0.0048 [+0.0041, +0.0055] | HOLDS |
| A5b A1 share of C2's every-attempt gain | ASSISTments | 0.650 [0.618, 0.683] | 0.660 [0.627, 0.695] | 0.649 [0.617, 0.683] | HOLDS |
|  | XES3G5M | 0.767 [0.745, 0.786] | 0.742 [0.724, 0.760] | 0.767 [0.745, 0.786] | MOVED |
|  | Eedi | 0.739 [0.713, 0.761] | 0.721 [0.696, 0.742] | 0.739 [0.713, 0.761] | HOLDS |
| A5c A2-orth share of C2's every-attempt gain | ASSISTments | 0.712 [0.678, 0.743] | 0.724 [0.690, 0.755] | 0.711 [0.677, 0.742] | HOLDS |
|  | XES3G5M | 0.822 [0.801, 0.842] | 0.794 [0.777, 0.810] | 0.822 [0.801, 0.842] | MOVED |
|  | Eedi | 0.869 [0.852, 0.886] | 0.849 [0.833, 0.863] | 0.869 [0.852, 0.886] | MOVED |
| A6 A1 intervals, cold | ASSISTments | 0.60 / 0.87 / 0.97 UNDER | 0.61 / 0.87 / 0.97 UNDER | 0.60 / 0.87 / 0.97 UNDER | HOLDS |
|  | XES3G5M | 0.56 / 0.84 / 0.96 UNDER | 0.57 / 0.84 / 0.96 UNDER | 0.56 / 0.84 / 0.96 UNDER | HOLDS |
|  | Eedi | 0.57 / 0.85 / 0.96 UNDER | 0.57 / 0.85 / 0.96 UNDER | 0.57 / 0.85 / 0.96 UNDER | HOLDS |
| A6 A2-orth intervals, cold | ASSISTments | 0.60 / 0.87 / 0.97 UNDER | 0.61 / 0.87 / 0.97 UNDER | 0.60 / 0.87 / 0.97 UNDER | HOLDS |
|  | XES3G5M | 0.56 / 0.84 / 0.96 UNDER | 0.57 / 0.84 / 0.96 UNDER | 0.56 / 0.84 / 0.96 UNDER | HOLDS |
|  | Eedi | 0.53 / 0.82 / 0.95 CALIBRATED | 0.53 / 0.82 / 0.95 CALIBRATED | 0.53 / 0.82 / 0.95 CALIBRATED | HOLDS |
| A6 C2g intervals, cold | ASSISTments | 0.51 / 0.80 / 0.95 CALIBRATED | 0.50 / 0.79 / 0.95 CALIBRATED | 0.51 / 0.80 / 0.95 CALIBRATED | HOLDS |
|  | XES3G5M | 0.52 / 0.81 / 0.95 CALIBRATED | 0.50 / 0.80 / 0.95 CALIBRATED | 0.52 / 0.81 / 0.95 CALIBRATED | HOLDS |
|  | Eedi | 0.50 / 0.80 / 0.94 CALIBRATED | 0.49 / 0.78 / 0.94 CALIBRATED | 0.50 / 0.80 / 0.94 CALIBRATED | HOLDS |
| A6 C2 intervals, cold | ASSISTments | 0.51 / 0.80 / 0.95 CALIBRATED | 0.50 / 0.79 / 0.94 CALIBRATED | 0.51 / 0.80 / 0.95 CALIBRATED | HOLDS |
|  | XES3G5M | 0.51 / 0.80 / 0.95 CALIBRATED | 0.50 / 0.79 / 0.94 CALIBRATED | 0.51 / 0.80 / 0.95 CALIBRATED | HOLDS |
|  | Eedi | 0.49 / 0.79 / 0.94 CALIBRATED | 0.48 / 0.77 / 0.93 CALIBRATED | 0.49 / 0.79 / 0.94 CALIBRATED | HOLDS |
| A6 C2 intervals, warm | ASSISTments | 0.48 / 0.78 / 0.94 CALIBRATED | 0.48 / 0.78 / 0.94 CALIBRATED | 0.48 / 0.78 / 0.94 CALIBRATED | HOLDS |
|  | XES3G5M | 0.48 / 0.77 / 0.94 CALIBRATED | 0.48 / 0.77 / 0.93 CALIBRATED | 0.48 / 0.77 / 0.94 CALIBRATED | HOLDS |
|  | Eedi | 0.49 / 0.79 / 0.94 CALIBRATED | 0.49 / 0.78 / 0.94 CALIBRATED | 0.49 / 0.79 / 0.94 CALIBRATED | HOLDS |
| A7 A1 items saved per 1,000, 20% risk | ASSISTments | +17.1 [+14.3, +21.1] | +17.5 [+14.8, +21.5] | +17.2 [+14.2, +21.0] | HOLDS |
|  | XES3G5M | +58.0 [+51.9, +62.5] | +59.3 [+53.4, +63.7] | +58.0 [+52.0, +62.5] | HOLDS |
|  | Eedi | +43.3 [+39.7, +46.8] | +43.1 [+39.5, +47.1] | +43.3 [+39.7, +46.8] | HOLDS |
| A7 A2-orth items saved per 1,000, 20% risk | ASSISTments | +18.6 [+15.9, +22.4] | +19.2 [+16.7, +23.3] | +18.7 [+15.9, +22.5] | HOLDS |
|  | XES3G5M | +62.4 [+56.1, +67.9] | +63.0 [+57.1, +68.4] | +62.4 [+56.1, +68.0] | HOLDS |
|  | Eedi | +48.7 [+45.0, +52.8] | +49.0 [+45.2, +52.9] | +48.7 [+45.0, +52.8] | HOLDS |
| A7 C2 items saved per 1,000, 20% risk | ASSISTments | +25.5 [+21.9, +30.0] | +25.5 [+21.8, +29.8] | +25.7 [+21.8, +30.1] | HOLDS |
|  | XES3G5M | +75.3 [+68.4, +80.0] | +76.0 [+69.3, +81.4] | +75.4 [+68.3, +80.0] | HOLDS |
|  | Eedi | +54.0 [+50.0, +57.8] | +54.6 [+50.8, +59.0] | +54.0 [+50.0, +57.8] | HOLDS |

### Verdict strings

| | XES3G5M | ASSISTments | Eedi | status |
| --- | --- | --- | --- | --- |
| graph-state coupling | COUPLING HELPS COLD NODES | COUPLING HELPS COLD NODES | COUPLING HELPS COLD NODES | HOLDS |
| graph-state graph | EMPIRICAL COVARIANCE ONLY | NOT TESTABLE (no hierarchy) | EMPIRICAL COVARIANCE ONLY | HOLDS |
| graph-state which skills | WHICH SKILLS CO-VARY MATTERS | WHICH SKILLS CO-VARY MATTERS | WHICH SKILLS CO-VARY MATTERS | HOLDS |
| graph-state guard | C2 IMPROVES NEXT-ATTEMPT | C2 IMPROVES NEXT-ATTEMPT | C2 IMPROVES NEXT-ATTEMPT | HOLDS |
| S2 A1 | PRIOR-ONLY CAPTURES MOST | PRIOR-ONLY CAPTURES MOST | PRIOR-ONLY CAPTURES MOST | HOLDS |
| S2 A1-global | PRIOR-ONLY CAPTURES MOST | PRIOR-ONLY CAPTURES MOST | PRIOR-ONLY CAPTURES MOST | HOLDS |
| S2 next-attempt guard | A1 DOES NOT WORSEN | A1 DOES NOT WORSEN | A1 DOES NOT WORSEN | HOLDS |
| S2 A2 | GENERAL STATE ADDS TO WARM PREDICTIONS | GENERAL STATE ADDS TO WARM PREDICTIONS | GENERAL STATE ADDS TO WARM PREDICTIONS | HOLDS |
| S2 double counting | NO DOUBLE COUNTING DETECTED | NAIVE BLEND DOUBLE-COUNTS | NO DOUBLE COUNTING DETECTED | HOLDS |
| S2 learner information | LEARNER-SPECIFIC, NOT VOLUME | LEARNER-SPECIFIC, NOT VOLUME | LEARNER-SPECIFIC, NOT VOLUME | HOLDS |

## Also seen (not registered)

- **Point calibration.** Moment matching removes most of graph-state's XES3G5M point-calibration
  excess, a stated limit there. C2's cold ECE is 0.004 against 0.014 under Laplace (C0 0.005); over all
  attempts it is 0.004 against 0.016. On Eedi cold ECE is 0.007 against 0.010. On ASSISTments it is
  worse, 0.030 against 0.022, still better than C0's 0.050.
- **Rank.** On XES3G5M the moment-matching filter's validation loss is 0.42219 at rank 12 and 0.42225 at
  rank 8. The Laplace filter's was lowest at rank 8. ASSISTments (2) and Eedi (8) keep their ranks.
  S2 fixes its ranks by design (8 / 2 / 8), so its XES3G5M numbers are at rank 8.
- **Validation loss, ASSISTments.** With Stage 1's items, before the per-variant refit, moment matching's
  validation cold loss is 0.0020 higher than Laplace's on ASSISTments. It is 0.0005-0.0007 lower on
  XES3G5M. After the refit, C2's TEST cold gain on ASSISTments is 0.0011 lower than under Laplace.
- C1 (parent read), C0, PFA-lite and CLIM do not use the filter. They match the original records to
  within the C0 drift (C1's cold gain -0.0091 on XES3G5M and +0.0251 on Eedi, as before).

## Limits

- The original synthetic floors were not re-run under moment matching. Their flags (graph-state floor
  passes, S2 Part A floor passes) are carried.
- Moment matching is still a Gaussian approximation applied one response at a time, with the same
  hyperedge spread for multi-skill items. It was checked against an exact filter only on single-skill
  W3 at true parameters.
- Not re-computed: S2 Part B (its own decoupled step with components), state-structure (S1) and S3
  (already moment matching).
- The XES3G5M general-factor share moves partly through a change of selected rank between two nearly
  tied ranks. The fixed-rank S2 reading (0.957) is the cleaner one for that claim.
- No `board/history.json` entry is written here (a re-check; integration records it).
- Open corpora, not Lazuli's.

## Reproduce

    python3 filter_recheck.py synthetic
    python3 filter_recheck.py gs assist | xes | eedi          # 25 / 88 / 67 min, peak 2.4 GB
    python3 filter_recheck.py s2 assist | xes | eedi          # 20 / 14 / 20 min, peak 2.0 GB
    python3 filter_recheck.py gs-lap assist | xes | eedi      # CHANGE 1: the same, original step
    python3 filter_recheck.py s2-lap assist | xes | eedi
    python3 filter_recheck.py compare
