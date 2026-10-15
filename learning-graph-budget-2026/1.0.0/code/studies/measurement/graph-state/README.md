# Graph state: does a coupled state forecast better than a belief per skill?

`docs/specs/ESTIMAND.md` section 8 defines a learner's state as the joint mastery posterior over the
whole skill graph, estimated like weather data assimilation. Lazuli's engine holds an independent Beta
per competency and hands increments to parents. This study replays both on three open corpora. It
asks whether coupling the skills improves what matters:

- the forecast at a skill the learner has never been seen on ("where there is no weather station");
- the forecast long after the last evidence;
- honest uncertainty.

Files:

- `coupling.py`: the pre-registration (its docstring), the runs and the verdicts.
- `gstate.py`: the machinery (the engine replay with parent propagation, the Stage-1 calibration, the
  EM fit of the population covariance, the coupled filter).

Pre-registered at 624feea. The first synthetic floor failed. Two changes came before any real
statistic (0e058ec): graph retention is measured over the no-coupling control, and the
independent-skills world checks for a false coupling verdict. The second floor passed (66a17bd). All
real runs used the code at 66a17bd. CHANGE 3 is computation only: a real run reads the floor record
after it finishes. `out/` holds aggregates only.

These are answers about the formulas on open corpora, not about Lazuli's items or graphs.

## The short answer

- **COUPLING HELPS COLD NODES, in all three corpora.** On a learner's first attempt at a skill, the
  coupled state (C2) beats the engine's calibrated independent state (C0) by 0.046-0.067 nats per
  attempt. AUC rises by 0.07-0.09.
- **The gain is coupling, not machinery.** The same filter without coupling (C2-diag) gains 0.000 on
  XES3G5M and 0.002 on Eedi.
- **The empirical covariance carries it, not the graph: EMPIRICAL COVARIANCE ONLY.** Coupling only
  sibling skills (C3) keeps 14% of the gain on XES3G5M and 35% on Eedi.
- **Almost all of it is one general factor.** A single general level (C2g) gives 95-99% of C2's gain.
  The graph adds 0.001-0.002 nats on top of it (C3g against C2g).
- **Coupling also helps every other attempt** (+0.020 to +0.037 nats) and keeps forecasts useful
  after 30 days. The engine's forecast skill is near zero after a week on two corpora.
- **The coupled state's predictive intervals are calibrated.** The engine's are too wide at first
  encounters.
- **The engine's parent propagation is not a substitute.** Reading the parent's belief at a new child
  helps on Eedi (+0.025) and hurts on XES3G5M (-0.009).

## Variants

| variant | state |
| --- | --- |
| C0 | the calibrated engine (engine-calibration's E5 with the engine's decay): an independent Beta per skill |
| C1 | C0 plus the engine's parent propagation; a skill with no evidence reads its nearest ancestor with evidence |
| C1-engine | C0 plus propagation only (the product today: a new leaf stays at the prior) |
| C2 | a Gaussian state over all skills, covariance = low rank + diagonal fitted on TRAIN, updated per response by a Laplace (extended-Kalman) step |
| C2-diag | C2's mean and variances, no covariance (control: the machinery without coupling) |
| C2-shuf | C2's correlations with skill labels deranged within frequency deciles (control: the same amount of coupling at the wrong skills; 3 derangements) |
| C2g | one general factor only |
| C3 | covariance only within sibling groups (skills sharing a parent in the hierarchy) |
| C3g | a general factor plus the sibling-group factors |
| C3c | covariance only within coarse groups (XES3G5M route depth 2; Eedi level 1) |
| PFA-lite | engine-calibration's logistic reference (it pools a learner's counts across skills) |
| CLIM | the item's TRAIN success rate (the reference for skill scores) |

Every fitted quantity comes from TRAIN learners (80%). Every metric is on TEST learners (20%).
Intervals are 95% percentile intervals over 200 learner bootstraps. Gains are log loss of C0 minus
log loss of the variant, in nats per attempt.

The C2 family has a practice term (log of earlier attempts on the skill) that C0 lacks. It is zero on
every cold attempt. It is one reason the C2 family beats C0 on later attempts, which is why C2-diag
is the coupling control.

## Data

| | XES3G5M (primary) | ASSISTments 2012-13 | Eedi 2020 |
| --- | ---: | ---: | ---: |
| learners | 9,082 (1 in 2) | 9,678 (1 in 3) | 20,009 (1 in 6) |
| skills | 865 KCs | 262 skills | 308 level-3 subjects |
| hierarchy | KC route tree: 420 sibling groups | none | subject tree: 62 sibling groups |
| attempts | 2.76M | 0.86M | 3.32M |
| TEST attempts / learners | 542k / 1,796 | 176k / 1,944 | 662k / 3,967 |
| TEST cold attempts | 200,000 | 23,678 | 116,573 |
| chosen rank r | 8 | 2 | 8 |

A cold attempt is one whose skills the learner has never attempted, and not the learner's first
attempt. Eedi keeps only the latest answer per question, so its "first" is first in last-answer
order.

## Verdicts

| | XES3G5M | ASSISTments | Eedi |
| --- | --- | --- | --- |
| coupling (M1) | **COUPLING HELPS COLD NODES** | **COUPLING HELPS COLD NODES** | **COUPLING HELPS COLD NODES** |
| graph | **EMPIRICAL COVARIANCE ONLY** | NOT TESTABLE (no hierarchy) | **EMPIRICAL COVARIANCE ONLY** |
| C3 retention of the coupling gain | 0.141 [0.132, 0.151] | - | 0.348 [0.328, 0.365] |
| which skills | WHICH SKILLS CO-VARY MATTERS | WHICH SKILLS CO-VARY MATTERS | WHICH SKILLS CO-VARY MATTERS |
| guard (M2) | C2 IMPROVES NEXT-ATTEMPT | C2 IMPROVES NEXT-ATTEMPT | C2 IMPROVES NEXT-ATTEMPT |
| parent read (C1) | DOES NOT HELP COLD NODES | not applicable | HELPS COLD NODES |

The floor passed, so no verdict carries UNCALIBRATED. The general-factor world's C3 retention was
0.33, under 0.5, so the graph verdict needs no "not diagnostic" flag. The retention as first
registered (over C0, not C2-diag) is 0.143 and 0.364: the same verdict.

## M1: forecasts at nodes never seen

Gain over C0 on cold attempts:

| variant | XES3G5M | ASSISTments | Eedi |
| --- | --- | --- | --- |
| C1 (parent read) | -0.0091 [-0.0118, -0.0067] | n/a | +0.0251 [+0.0215, +0.0296] |
| C1-engine | -0.0005 [-0.0008, -0.0002] | n/a | +0.0000 [+0.0000, +0.0000] |
| **C2** | **+0.0457 [+0.0424, +0.0486]** | **+0.0473 [+0.0423, +0.0533]** | **+0.0672 [+0.0634, +0.0711]** |
| C2-diag | +0.0001 [-0.0004, +0.0007] | +0.0151 [+0.0128, +0.0172] | +0.0016 [+0.0008, +0.0024] |
| C2-shuf | +0.0382 [+0.0350, +0.0409] | +0.0457 [+0.0409, +0.0522] | +0.0621 [+0.0587, +0.0659] |
| C2g (general factor) | +0.0433 [+0.0398, +0.0460] | +0.0470 [+0.0422, +0.0534] | +0.0666 [+0.0632, +0.0704] |
| C3 (siblings) | +0.0065 [+0.0059, +0.0072] | n/a | +0.0245 [+0.0224, +0.0263] |
| C3g (general + siblings) | +0.0443 [+0.0410, +0.0471] | n/a | +0.0687 [+0.0650, +0.0727] |
| C3c (coarse groups) | +0.0266 [+0.0243, +0.0286] | n/a | +0.0533 [+0.0501, +0.0566] |
| PFA-lite | +0.0388 [+0.0359, +0.0412] | +0.0388 [+0.0326, +0.0440] | +0.0549 [+0.0517, +0.0586] |
| CLIM | +0.0010 [+0.0003, +0.0017] | +0.0166 [+0.0121, +0.0206] | +0.0052 [+0.0043, +0.0060] |

| | XES3G5M | ASSISTments | Eedi |
| --- | ---: | ---: | ---: |
| C0 cold log loss / AUC | 0.478 / 0.733 | 0.642 / 0.644 | 0.602 / 0.683 |
| C2 cold log loss / AUC | 0.432 / 0.800 | 0.595 / 0.726 | 0.534 / 0.778 |
| C2 AUC gain | +0.067 [+0.063, +0.071] | +0.082 [+0.074, +0.089] | +0.094 [+0.090, +0.100] |
| C2 over C2-diag | +0.0456 [+0.0420, +0.0487] | +0.0322 [+0.0273, +0.0378] | +0.0656 [+0.0617, +0.0698] |
| C2 over C2-shuf | +0.0075 [+0.0069, +0.0083] | +0.0016 [+0.0004, +0.0026] | +0.0052 [+0.0044, +0.0059] |
| C3g over C2g | +0.0010 [+0.0008, +0.0013] | n/a | +0.0020 [+0.0014, +0.0025] |

- **The engine forecasts a new skill no better than the item's average.** C0's cold log loss is
  0.001 worse than climatology's on XES3G5M, 0.017 worse on ASSISTments and 0.005 worse on Eedi. Its belief at a new skill is the
  prior, whatever the learner did elsewhere.
- **Evidence elsewhere carries a lot.** In the fitted covariance the mean correlation between two
  skills' mastery is 0.63 (XES3G5M), 0.52 (ASSISTments) and 0.57 (Eedi). The first factor holds
  56-65% of the correlation matrix.
- **The general level is the coupling.** C2g, one number per learner plus a loading per skill, gets
  95% (XES3G5M), 99% (ASSISTments) and 99% (Eedi) of C2's gain. Deranging the skill labels keeps a
  general level in place and still keeps 84-97% of it (C2-shuf).
- **Which skills co-vary adds a little.** C2 beats its deranged control by 0.002-0.008 nats. C3g beats
  C2g by 0.001-0.002. These are real but small next to the general level.
- **The graph alone carries little.** Siblings share variance, but a learner's first skill in a new
  sibling group gets nothing from C3. Coarse groups (C3c) carry more (58% and 79% of C2's gain) because
  they cover more of what a learner has done.
- **On ASSISTments part of the gain is machinery.** C2-diag gains +0.015 there. Its first-encounter
  forecast (the item integrated over the population prior) is better calibrated than the engine's
  Jeffreys-prior forecast (ECE 0.046 against 0.050, and C2's 0.022). Coupling still adds +0.032.
- **C2 beats PFA-lite at cold nodes** by 0.007-0.012 nats. PFA-lite also pools a learner's history
  across skills, through counts.

## M2: every next attempt

| gain over C0 | XES3G5M | ASSISTments | Eedi |
| --- | --- | --- | --- |
| C1 | -0.0032 [-0.0043, -0.0023] | n/a | +0.0047 [+0.0040, +0.0054] |
| **C2** | **+0.0358 [+0.0332, +0.0377]** | **+0.0198 [+0.0185, +0.0211]** | **+0.0373 [+0.0357, +0.0392]** |
| C2-diag | +0.0023 [+0.0018, +0.0027] | +0.0087 [+0.0072, +0.0098] | +0.0029 [+0.0024, +0.0033] |
| C2g | +0.0337 [+0.0313, +0.0358] | +0.0195 [+0.0180, +0.0209] | +0.0365 [+0.0350, +0.0385] |
| C3 | +0.0074 [+0.0068, +0.0080] | n/a | +0.0167 [+0.0159, +0.0175] |
| C3g | +0.0343 [+0.0318, +0.0363] | n/a | +0.0379 [+0.0363, +0.0397] |
| PFA-lite | +0.0279 [+0.0259, +0.0295] | +0.0192 [+0.0168, +0.0211] | +0.0248 [+0.0231, +0.0269] |

- The guard holds: C2 does not worsen next-attempt prediction. It improves it everywhere.
- C2's AUC gain over C0 is +0.051, +0.025 and +0.041. C2 also beats PFA-lite overall (log loss 0.405
  against 0.413 on XES3G5M, 0.517 against 0.529 on Eedi; level on ASSISTments, 0.541 against 0.542).

## M3: the predictability horizon

Log-loss skill score against climatology, by time since the last evidence on the attempt's skills
(attempts whose skills all have earlier evidence). The horizon is the last bin, from under a day,
whose lower bound stays above 0.

| | < 1 day | 1-7 days | 7-30 days | >= 30 days | horizon |
| --- | ---: | ---: | ---: | ---: | --- |
| XES3G5M C0 | 0.072 | 0.017 | 0.020 | -0.002 | 7-30 days |
| XES3G5M C2 | 0.131 | 0.107 | 0.121 | 0.092 | >= 30 days |
| XES3G5M C2-diag | 0.079 | 0.028 | 0.031 | 0.012 | >= 30 days |
| XES3G5M C3 | 0.088 | 0.040 | 0.043 | 0.022 | >= 30 days |
| ASSISTments C0 | 0.030 | -0.003 | -0.010 | -0.047 | < 1 day |
| ASSISTments C2 | 0.051 | 0.038 | 0.046 | 0.033 | >= 30 days |
| ASSISTments C2-diag | 0.040 | 0.019 | 0.017 | -0.008 | 7-30 days |
| Eedi C0 | 0.118 | 0.071 | 0.081 | 0.036 | >= 30 days |
| Eedi C2 | 0.164 | 0.155 | 0.159 | 0.126 | >= 30 days |
| Eedi C2-diag | 0.124 | 0.079 | 0.082 | 0.041 | >= 30 days |
| Eedi C3 | 0.141 | 0.115 | 0.116 | 0.074 | >= 30 days |

C2's gain over C0 grows with the gap: on XES3G5M +0.025 [+0.023, +0.027] under a day and +0.044
[+0.039, +0.050] after 30 days. On ASSISTments +0.012 and +0.046. On Eedi +0.028 and +0.054.

- **The engine's state goes stale in a week.** On XES3G5M and ASSISTments, C0 keeps a quarter or less
  of its same-day skill after a day, and none after 30 days.
- **The coupled state keeps 65-77% of its same-day skill after 30 days.** Most of what it knows about
  a learner is the general level, and that does not go stale when one skill is left alone.
- The bins mix who comes back, not only time. Every variant is scored on the same attempts.

## M4: calibration

Coverage of central predictive intervals for the count correct in 5 consecutive attempts on one
skill. Cold windows start at the learner's first attempt on the skill; warm windows after 3 attempts.
Nominal 0.50 / 0.80 / 0.95.

| | XES3G5M cold | warm | ASSISTments cold | warm | Eedi cold | warm |
| --- | --- | --- | --- | --- | --- | --- |
| windows | 19,129 | 6,311 | 10,901 | 6,600 | 31,790 | 21,800 |
| C0 | 0.61 / 0.85 / 0.96 UNDER-CONFIDENT | 0.51 / 0.81 / 0.95 calibrated | 0.72 / 0.90 / 0.97 UNDER-CONFIDENT | 0.50 / 0.81 / 0.95 calibrated | 0.60 / 0.85 / 0.96 UNDER-CONFIDENT | 0.51 / 0.81 / 0.95 calibrated |
| C2 | 0.50 / 0.79 / 0.94 **calibrated** | 0.49 / 0.78 / 0.94 calibrated | 0.51 / 0.80 / 0.95 **calibrated** | 0.48 / 0.78 / 0.94 calibrated | 0.50 / 0.79 / 0.95 **calibrated** | 0.49 / 0.79 / 0.95 calibrated |
| C3 | 0.49 / 0.79 / 0.94 calibrated | 0.48 / 0.77 / 0.94 calibrated | n/a | n/a | 0.51 / 0.80 / 0.95 calibrated | 0.48 / 0.79 / 0.94 calibrated |

- At a new skill the engine's Beta(0.5, 0.5) is too wide: it does not know what the learner's other
  skills say. The coupled state's intervals cover at the nominal rate at every level.
- Point calibration (ECE, 10 bins) is mixed. On XES3G5M C2 is worse: 0.014 against 0.005 on cold
  attempts (+0.009 [+0.004, +0.012]) and 0.016 against 0.009 overall. On Eedi it is better on cold
  attempts (0.010 against 0.021) and slightly worse overall (0.010 against 0.008). On ASSISTments it is better on both (0.022 against
  0.050 cold, 0.014 against 0.031 overall). A per-corpus recalibration would remove the XES3G5M
  excess; it was not registered.

## M5: the practice decision

practice_value.py's matched-risk metric on every TEST attempt. Items saved = unneeded practice per
1,000 attempts, C0 minus the variant.

| items saved per 1,000 | XES3G5M | ASSISTments | Eedi |
| --- | --- | --- | --- |
| **C2, risk 20%** | **+74.3 [+69.3, +78.1]** | **+25.5 [+22.1, +29.2]** | **+53.2 [+50.4, +55.8]** |
| C2, risk 10% | +75.5 [+71.0, +79.6] | +24.1 [+19.4, +27.2] | +59.8 [+56.7, +63.8] |
| C2, risk 30% | +64.2 [+60.6, +67.8] | +24.1 [+20.8, +26.9] | +43.9 [+41.9, +45.9] |
| C2-diag, risk 20% | +6.3 [+4.5, +8.5] | +6.0 [+3.4, +9.4] | +3.7 [+2.4, +4.8] |
| C3, risk 20% | +17.1 [+15.0, +19.2] | n/a | +25.0 [+23.4, +26.8] |
| C1, risk 20% | +4.5 [+1.8, +7.2] | n/a | +9.1 [+7.7, +10.7] |
| PFA-lite, risk 20% | +60.7 [+56.4, +64.2] | +31.3 [+26.7, +37.0] | +38.0 [+35.2, +40.9] |

The calibrated engine asks for 347, 364 and 276 unneeded items per 1,000 attempts at this risk. The
coupled state removes 21%, 7% and 19% of them, on top of what calibration already saved.

## The synthetic floor

`out/synthetic.json` (floor 2; floor 1 in `out/synthetic-floor1.json`). 3,000 learners, 60 skills in
15 sibling groups. M1 gains over C0:

| world | planted | C2 | C2-diag | C3 | verdict |
| --- | --- | --- | --- | --- | --- |
| G, 2 seeds | coupling within sibling groups | +0.0074 / +0.0096 | +0.0013 / +0.0031 | +0.0088 / +0.0123 | GRAPH CARRIES THE COUPLING |
| E, 2 seeds | two random factors, off the graph | +0.0039 / +0.0084 | +0.0004 / +0.0040 | +0.0000 / +0.0042 | EMPIRICAL COVARIANCE ONLY |
| I, 2 seeds | independent skills | +0.0027 / +0.0060 | +0.0025 / +0.0062 | | C2 HELPS COLD NODES, NOT BY COUPLING |
| H, 1 seed | a general factor only | +0.0234 | +0.0017 | +0.0088 | EMPIRICAL COVARIANCE ONLY (retention 0.33) |

- The instrument separates the three cases it must: graph coupling, off-graph coupling, and none.
- The first floor failed twice for one reason. The Gaussian filter gains a little at first encounters
  even with no coupling (world I; world E seed 1). Measured over C0, that shared gain counted as
  coupling and as graph retention. Both are now measured over C2-diag (CHANGES 1-2).
- The real corpora look like world H, not G: one strong general level, and C2-shuf close to C2.
- C2's intervals were calibrated in every world.

## What this means for the engine

**What coupling would add.** The engine's forecast at a skill a learner has not yet touched is the
item's average. A coupled state makes it a forecast about this learner: +0.05-0.07 nats and +0.07-0.09
AUC at first encounters, +0.02-0.04 nats on every attempt, and a state that stays informative for
months instead of a week. In the practice decision it saves 25-74 unneeded items per 1,000 attempts
beyond item calibration alone. It also gives intervals that mean what they say at a new skill.

**Most of it is cheap.** One general level per learner carries 95-99% of the gain. The engine could
keep its Beta per competency for what it shows, and add:

- per learner, a general ability with its variance, updated from every response;
- per skill, a loading on that ability and a unique variance, fitted offline;
- per (learner, skill), the evidence precision and information (two numbers where the engine keeps
  alpha and beta);
- the forecast at any skill, seen or not, from the prior conditioned on all of them.

The full rank-8 version costs an 8 x 8 solve per response. The general-factor version costs a scalar
update. Both are an offline fit (minutes on these corpora) plus an online update of the same order as
today's.

**What does not do it.** The authored hierarchy is not the coupling. Sibling groups carry 14-35%, and
the graph adds 0.001-0.002 nats beyond a general level. Parent propagation with a parent read helps on
Eedi (+0.025) and hurts on XES3G5M (-0.009), and propagation as shipped changes nothing for a new leaf.
Do not build the coupled state out of `parent` edges. Fit the covariance from learners.

**What it needs from Lazuli's data.**

- **Learners seen on many skills**, and one learner id across courses. The covariance is estimated
  from learners with evidence on several skills. A skill needs 20 or more such learners to get its own
  loading; the rest take the average.
- **Per-item difficulty and discrimination**, as engine-calibration recommends. The coupled state is
  fitted on a calibrated item scale.
- **A stable skill id space.** Coupling across courses needs the same skill ids, or a mapping.
- **A practice term.** Mastery at first encounter is lower than average mastery. Without the term the
  prior over-predicts first attempts.
- **A refit schedule.** The covariance and item parameters are batch fits on TRAIN learners, refitted
  when the item bank or population changes, never online.

**Before shipping**, rerun this comparison on Lazuli's LRS with `calibrate.py`'s export format plus
skill ids. These results are open corpora, whose curricula differ from Lazuli's.

## Limits

- Open corpora, not Lazuli's items, graphs or learners. XES3G5M is 1 learner in 2, ASSISTments 1 in
  3, Eedi 1 in 6 (memory).
- The covariance is predictive, not causal. Curricula order which skills learners meet, so part of
  the "general level" may be who progresses far.
- The Laplace step linearises one response at a time. The hyperedge rule spreads a multi-skill
  response evenly and cannot tell which skill failed.
- Stage 1 is a static calibration; learning within a skill enters only through the practice term and
  the accumulating evidence.
- C0 is E5 with the engine's decay (within 0.0005 nats of E5 in engine-calibration), not full E5.
- C1's parent read is not in the product. C3 couples parent-child KC pairs only through C3c.
- Eedi's order is last-answer order. ASSISTments has no hierarchy.
- Point calibration of C2 is worse than C0's on XES3G5M (ECE +0.007 to +0.009).

## Files

- `out/xes.json`, `out/assist.json`, `out/eedi.json`: point estimates, verdicts, bootstrap contrasts,
  horizon, coverage and fitted-prior summaries.
- `out/synthetic.json` (floor 2), `out/synthetic-floor1.json` (floor 1).

Commands:

    python3 coupling.py synthetic
    python3 coupling.py xes | eedi | assist
