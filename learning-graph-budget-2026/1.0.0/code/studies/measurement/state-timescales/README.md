# State timescales: the cheapest engine-ready coupling, and the fast state

S2 of `docs/notes/NEXT-ROUND.md`. Its part of `docs/specs/SYSTEM-MODEL.md`: the fast part of Φ, and
separating w (state noise that persists) from v (answer noise). Two separate questions:

- **Part A.** How much of the coupled state's gain at a never-seen skill (graph-state's C2) can the
  engine's own Beta per skill capture, if a new skill's Beta starts from the learner's general level?
- **Part B.** Once item memory, the serving policy, the previous answer and action, and learner-level
  dynamics are accounted for, is there a fast state that persists from answer to answer within a
  session? Does filtering it out give a better slow state for the next session?

Files:

- `state_timescales.py`: the pre-registration (its docstring, with CHANGES and RESULTS), the runs and
  the verdicts.
- `tstate.py`: the machinery (sessions and steps, the control-stack features, the joint filter with
  extra components, the engine's Beta with a learner-informed prior).
- `out/`: aggregates only. `synthetic.json` (the floor), `assist.json`, `xes.json`, `eedi.json`,
  `stop-go.json`.

Pre-registered at de1ec24, before any real-data statistic, answering `docs/notes/S2-HOSTILE-REVIEW.md`
point by point. CHANGES 1-6 came from debugging on development worlds (other seeds) before the floor
and before any real statistic (d9c7ee6). The floor ran at d9c7ee6 (record 6f10342). CHANGE 7 is
computation only.

These are answers about the formulas on open corpora, not about Lazuli's items or learners. They
describe regularities of these platforms' activity systems under their own curricula, tools and
item-selection policies.

## The short answer

- **Part A: a learner-informed prior on the engine's own Beta captures almost all of the coupled
  state's cold-skill gain.** Starting a new skill's Beta at the learner's general level (A1: two
  numbers per skill fitted offline, one scalar state per learner) captures 0.91-1.01 of C2's gain at
  first encounters, on all three corpora: PRIOR-ONLY CAPTURES MOST. It does not worsen the next
  attempt, and its intervals are less under-confident than the engine's.
- **Re-centring warm skills on the current general level (A2-orth) adds a little more** (+0.001 to
  +0.005 nats per attempt) without double counting. Leaving the skill's own evidence in the general
  level (A2-naive) double-counts on ASSISTments.
- **The gain is the learner's outcomes, not practice volume.** Swapping in another learner's general
  level at the same count (A1-der) or a volume-and-time prior (A1-vol) keeps 0.02-0.41 of it.
- **Part B: the floor failed for existence.** The instrument raised no false fast state in nine
  worlds without one, but it did not detect any of the four planted fast states either. Every Part B
  verdict below therefore carries "(UNCALIBRATED)".
- **On real data a small, session-level fast component survives every control on all three corpora**:
  +0.0006 to +0.0012 nats per within-session answer over the same machinery without persistence,
  also on steps after a change of skill with an item the learner has not seen. Its fitted
  persistence is about 1 per answer and it resets at the session boundary. In practice it is a
  shift in level for each sitting, not a decaying streak: FAST PERSISTENT STATE PRESENT
  (UNCALIBRATED); AR FORM UNIDENTIFIED on ASSISTments and XES3G5M, 2TS on Eedi by +0.00002.
- **Engine value is small.** Filtering it out improves next-session first attempts by +0.0001 to
  +0.0006 nats, under the pre-registered 0.001. ASSISTments passes only through interval coverage.
- **Stop/go for S3: HOLD (UNIDENTIFIED).** No named momentary-state component goes into S3. S3 may
  test a generic session-level component in its own ablation.

## Verdicts

| | ASSISTments (primary for B) | XES3G5M | Eedi |
| --- | --- | --- | --- |
| A1 (per-skill map) | **PRIOR-ONLY CAPTURES MOST** | **PRIOR-ONLY CAPTURES MOST** | **PRIOR-ONLY CAPTURES MOST** |
| A1-global | PRIOR-ONLY CAPTURES MOST | PRIOR-ONLY CAPTURES MOST | PRIOR-ONLY CAPTURES MOST |
| next-attempt guard | A1 DOES NOT WORSEN | A1 DOES NOT WORSEN | A1 DOES NOT WORSEN |
| A2 | GENERAL STATE ADDS TO WARM PREDICTIONS | GENERAL STATE ADDS TO WARM PREDICTIONS | GENERAL STATE ADDS TO WARM PREDICTIONS |
| double counting | NAIVE BLEND DOUBLE-COUNTS | NO DOUBLE COUNTING DETECTED | NO DOUBLE COUNTING DETECTED |
| learner information | LEARNER-SPECIFIC, NOT VOLUME | LEARNER-SPECIFIC, NOT VOLUME | LEARNER-SPECIFIC, NOT VOLUME |
| B existence | FAST PERSISTENT STATE PRESENT (UNCALIBRATED) | FAST PERSISTENT STATE PRESENT (UNCALIBRATED) | FAST PERSISTENT STATE PRESENT (UNCALIBRATED) |
| B demand | NOT TESTABLE (no ratings) | PLAIN SUPPORTED (UNCALIBRATED); kappa-hat 0 | NOT TESTABLE (no ratings) |
| B dynamics | AR FORM UNIDENTIFIED (UNCALIBRATED) | AR FORM UNIDENTIFIED (UNCALIBRATED) | 2TS SUPPORTED (UNCALIBRATED) |
| B engine value | FILTERING IMPROVES NEXT-SESSION STATE (UNCALIBRATED), by coverage only | FILTERING DOES NOT MATERIALLY IMPROVE (UNCALIBRATED) | FILTERING DOES NOT MATERIALLY IMPROVE (UNCALIBRATED) |
| B within session | M NOT MATERIAL (UNCALIBRATED) | M NOT MATERIAL (UNCALIBRATED) | M MATERIAL WITHIN SESSION (UNCALIBRATED) |

Part A's floor passed. Part B's existence, form and engine-value families failed theirs (CHANGE 4
assigns the flag per family).

## Part A: the learner-informed prior

Gain over C0 in nats per attempt (log loss of C0 minus the variant); share = the share of C2's gain.
TEST cold attempts: 23,678 (ASSISTments), 98,466 (XES3G5M), 57,052 (Eedi).

| cold attempts | ASSISTments | XES3G5M | Eedi |
| --- | --- | --- | --- |
| C2 (full coupled state) | +0.0473 [+0.0419, +0.0527] | +0.0443 [+0.0395, +0.0495] | +0.0682 [+0.0631, +0.0735] |
| C2g (one general factor) | +0.0470; share 0.99 [0.98, 1.01] | +0.0429; 0.97 [0.95, 0.99] | +0.0677; 0.99 [0.98, 1.01] |
| **A1** | **+0.0476; share 1.01 [0.96, 1.05]** | **+0.0404; 0.91 [0.89, 0.94]** | **+0.0642; 0.94 [0.92, 0.96]** |
| A1-global | +0.0275; 0.58 [0.52, 0.64] | +0.0371; 0.84 [0.81, 0.86] | +0.0588; 0.86 [0.83, 0.89] |
| A1-der (deranged control) | +0.0193; 0.41 [0.34, 0.48] | +0.0007; 0.02 [0.00, 0.03] | +0.0030; 0.04 [0.02, 0.06] |
| A1-vol (volume and time) | +0.0050; 0.11 [0.08, 0.14] | +0.0007; 0.02 [0.00, 0.03] | +0.0029; 0.04 [0.02, 0.06] |
| A1-leak (planted leak) | +0.0726; 1.54 | +0.0479; 1.08 | +0.0796; 1.17 |
| A1 AUC gain | +0.083 [+0.076, +0.091] | +0.062 [+0.055, +0.068] | +0.096 [+0.088, +0.103] |

| every attempt | ASSISTments | XES3G5M | Eedi |
| --- | --- | --- | --- |
| C2 | +0.0198 [+0.0187, +0.0211] | +0.0356 [+0.0325, +0.0391] | +0.0370 [+0.0349, +0.0391] |
| A1; share | +0.0129; 0.65 [0.62, 0.68] | +0.0273; 0.77 [0.75, 0.79] | +0.0273; 0.74 [0.71, 0.76] |
| **A2-orth; share** | **+0.0141; 0.71 [0.68, 0.74]** | **+0.0293; 0.82 [0.80, 0.84]** | **+0.0321; 0.87 [0.85, 0.89]** |
| A2-orth over A1 | +0.0012 [+0.0009, +0.0015] | +0.0019 [+0.0017, +0.0022] | +0.0048 [+0.0041, +0.0055] |
| A2-naive minus A2-orth (log loss; warm ECE) | +0.0014 [+0.0012, +0.0015]; +0.0038 | -0.0001; -0.0006 | -0.0001; -0.0015 |
| practice saved per 1,000 at 20% risk: A1 / A2-orth / C2 | +17.1 / +18.6 / +25.5 | +58.0 / +62.4 / +75.3 | +43.3 / +48.7 / +54.0 |

- **The prior alone does almost all of the first-encounter work.** On ASSISTments A1 matches C2 at
  first encounters. The per-skill map matters there: the single-pair version (A1-global) keeps only
  0.58, because skills' starting levels and their dependence on the general level differ.
- **Where A1 falls short is warm attempts.** A1 keeps 0.65-0.77 of C2's gain over all attempts. A1's
  prior is frozen at the first touch. C2 keeps reading the learner's other skills. A2-orth recovers
  part of the difference (0.71-0.87).
- **Calibration.** A1's cold-window intervals are still UNDER-CONFIDENT (coverage 0.60 / 0.87 / 0.97
  on ASSISTments against nominal 0.50 / 0.80 / 0.95) but less so than C0's (0.72 / 0.90 / 0.97). C2's
  are calibrated. No A variant is over-confident; warm windows are calibrated for every variant. Cold
  ECE improves by 0.038 (ASSISTments) and 0.021 (Eedi). On XES3G5M it changes by +0.003 [-0.003, +0.006].
  So the gain is not bought with narrower-but-wrong uncertainty (hostile review 2.A4).
- **Leakage and volume (2.A1, 2.A2).** The planted leak scores 0.007-0.025 nats above A1, so a leaky
  implementation would show. The deranged control has the same number of earlier attempts, the same
  volume decile and the same spread of g_hat (SD ratio 0.99-1.02). On XES3G5M and Eedi it keeps 2-4%
  of the gain. On ASSISTments it keeps 41%: there the per-skill map alone, the population's
  starting level per skill, is worth a lot, because the engine's Jeffreys prior is badly placed for
  ASSISTments skills. A1 beats A1-der by +0.028, +0.040 and +0.061 nats on cold attempts.
- n0 = 2-3 pseudo-observations on every corpus.

## Part B: the fast state

TEST attempts within a session (not a session's first): 158,530 / 213,614 / 282,132; restricted
steps (previous step on another skill, the item new to the learner): 44,709 / 88,184 / 109,025.
Every gain is over the same layer with its answer-noise component and no persistence (CHANGE 3).

| AR1 gain within session | ASSISTments | XES3G5M (batch-blind) | Eedi |
| --- | --- | --- | --- |
| over H0 (C2 only) | +0.0046 [+0.0035, +0.0057] | +0.0012 [+0.0009, +0.0016] | +0.0038 [+0.0032, +0.0044] |
| over H1 (+ previous answer) | +0.0016 [+0.0010, +0.0022] | +0.0006 [+0.0004, +0.0008] | +0.0019 [+0.0014, +0.0024] |
| over H2 (+ previous action) | +0.0013 [+0.0008, +0.0018] | (no traces) | (no traces) |
| over H3 (+ memory, selection) | +0.0012 [+0.0007, +0.0017] | +0.0006 [+0.0004, +0.0009] | +0.0019 [+0.0014, +0.0024] |
| **over H4 (+ learner slope)** | **+0.0008 [+0.0004, +0.0013]** | **+0.0006 [+0.0004, +0.0008]** | **+0.0012 [+0.0010, +0.0014]** |
| over H4, restricted steps | +0.0011 [+0.0005, +0.0018] | +0.0011 [+0.0007, +0.0015] | +0.0018 [+0.0014, +0.0021] |
| rho-hat at H4 (bootstrap 2.5-97.5%) | 0.98 [0.95, 1.0] | 0.98 [0.8, 1.0] | 1.0 [0.98, 1.0] |
| tau-hat at H4 (logits) | 0.2 | 0.3 | 0.2 |
| rho-hat at H0 | 0.85 | 0.8 | 0.9 |
| carried across sessions (rho_b) | 0 (reset) | 0 (reset) | 0.75 |

- **The controls take most of it.** The previous answer alone (H1) removes 50-66% of the AR gain
  over C2. By H4, 18%, 49% and 32% of the H0 gain is left. What remains is a level shift per
  sitting. Once the previous answer is controlled, its fitted persistence is 0.95-1.0 per answer.
  It resets at the session boundary on ASSISTments and XES3G5M (carrying it costs 47-49 nats of
  TRAIN log likelihood). Eedi keeps 0.75 of it across sittings.
- **It survives the restriction**, so it is not same-skill memory or a repeat of the same item
  (3.B1, 3.B5). It does not vary by learner tercile (rho 0.9-1.0 in every volume and ability
  tercile; 3.B4).
- **Forms (3.B7).** AR1 and a session random intercept are indistinguishable (AR1 minus SRI +0.00005
  [-0.00007, +0.00013] on ASSISTments, -0.000003 on XES3G5M, 0 on Eedi). Both beat the finite-lag model.
  On Eedi two AR components beat AR1 by +0.000016 [+0.000001, +0.000031]: a slow (rho 1.0) and a fast
  (rho 0.7, tau 0.1) part.
- **Demand (XES3G5M).** kappa-hat = 0: PLAIN SUPPORTED. The session-level shift does not grow with the
  item's rated element interactivity once position x interactivity is in H3. demand_i is externally
  rated task demand, not experienced load, so this says nothing about load.
- **Batches (3.B2).** On XES3G5M an AR that updates within a submission gains +0.0033 on same-submission
  transitions. The batch-blind one gains +0.0005 there and +0.0007 on next-submission transitions.
  Most of the XES3G5M within-sitting dependence is within a submitted set, as residual-structure
  found.
- **Session end (hostile review 4).** The fast component at the end of a session is negative after a
  wrong last answer and positive after a right one (ASSISTments -0.048 / +0.019 logits; XES3G5M
  -0.066 / +0.021; Eedi -0.030 / +0.021). Session boundaries partly follow outcomes.

### The next-session criterion

First attempts of every session after the learner's first: 15,692 / 53,006 / 42,626.

| gain at next-session first attempts | ASSISTments | XES3G5M | Eedi |
| --- | --- | --- | --- |
| (4) FILTERED vs (3) ABSORBED | +0.0039 [+0.0025, +0.0052] | +0.0086 [+0.0075, +0.0096] | +0.0055 [+0.0043, +0.0066] |
| **(4) FILTERED vs (1) BASELINE** | **+0.0006 [+0.0003, +0.0009]** | **+0.0001 [+0.0000, +0.0002]** | **+0.0003 [+0.0002, +0.0005]** |
| (2) RAW last-session residual vs (1) | +0.0000 [-0.0000, +0.0000] | +0.0001 [+0.0000, +0.0001] | +0.0004 [+0.0001, +0.0008] |
| practice saved per 1,000, (4) vs (1), 20% risk | +0.6 [-2.4, +2.6] | +0.1 [-1.5, +1.8] | +0.4 [-1.2, +1.8] |
| session-start 5-attempt window coverage, (1) | 0.45 / 0.74 / 0.92 | 0.50 / 0.77 / 0.94 | 0.48 / 0.77 / 0.93 |
| the same, (4) | 0.48 / 0.76 / 0.93 | 0.52 / 0.79 / 0.95 | 0.49 / 0.79 / 0.94 |

- **The decisive contrast is not diagnostic.** FILTERED beat ABSORBED in every floor world, including
  the worlds with no fast state (+0.003 to +0.026). Carrying a filter's end-of-session estimate of any
  fast component into the next session always costs. So the informative contrast is FILTERED against
  BASELINE. It is positive but under the 0.001 materiality bar on every corpus. On ASSISTments
  session-start intervals move toward nominal by 0.03 at the 50% level (4,001 windows), which meets
  the registered coverage clause. On XES3G5M (620 windows) and Eedi they move by less than 0.02.
- Filtering does not reduce false early advances at matched risk on any corpus.

### The engine reading (C0 + AR1)

The same component on the shipped engine's Beta gains more, because C0 has no general level to
absorb a sitting's shift: +0.0034 [+0.0018, +0.0052] (ASSISTments), +0.0070 (XES3G5M), +0.0102 (Eedi)
within session. Filtering it out of the Beta updates gains +0.0022, +0.0013 and +0.0015 at
next-session first attempts. Practice saved: +1.9 [-1.1, +4.3], +1.6 [-0.9, +4.4], +0.8 [+0.5, +5.8].
This is the value of a per-sitting offset to an engine without a general level. Part A's prior
removes most of the reason for it.

## Design in one page

**Data.** ASSISTments 2012-13 (primary for Part B: reliable start times, hints, response times, the
skill-builder section type), 1 learner in 3 (graph-state's sample). XES3G5M, 1 in 4 (a subset of
graph-state's 1 in 2; RAM). Eedi 2020, 1 in 12 (a subset of graph-state's 1 in 6; RAM). TRAIN/TEST by
e2e.py's learner hash; everything fitted on TRAIN, measured on TEST; 200 learner bootstraps, the same
draws for every variant. Sessions: a gap over 30 minutes; Eedi: a quiz sitting. XES3G5M answers that
share a millisecond timestamp form one submission.

**Part A variants** (all on the engine's Beta and C0's item parameters):

| variant | the new skill's Beta |
| --- | --- |
| C0 | Beta(0.5, 0.5), the engine as shipped (calibrated, E5-decay) |
| A1-global | Beta(n0 p0, n0 (1 - p0)), logit p0 = mu + lambda g_hat, one mu and lambda |
| A1 | the same with mu_k, lambda_k per skill (shrunk to the global pair) |
| A2-orth | the prior part re-centred on the current g_hat at every attempt, the skill's own evidence removed from g_hat |
| A2-naive | the same with the skill's own evidence left in g_hat (counted twice) |
| A1-leak | g_hat from the learner's whole history, the future included (a planted leak) |
| A1-der | g_hat of another learner from the same volume decile, after the same number of attempts (deranged) |
| A1-vol | p0 from practice volume and time on the platform only |
| C2g, C2 | graph-state's coupled Gaussian state (one general factor; full rank) |

g_hat is C2g's general-factor posterior from the learner's strictly earlier responses: one mean and
one precision per learner. It is a forecasting coordinate in p(X), not a learner mechanism.

**Part B, the control stack.** Each layer is an offset on the C2 filter's linear predictor, fitted on
TRAIN, plus an answer-noise component WN (rho = 0; CHANGE 3), which is the reference of every
persistence contrast:

| layer | adds |
| --- | --- |
| H0 | C2 alone (+ WN) |
| H1 | the previous answer in the session, by same skill / same submission |
| H2 | the previous problem's hint, bottom-out hint, extra attempts, response time, rapid response, hint x answer (ASSISTments) |
| H3 | item seen before (count, hours since, last residual on it), same-skill recency and count in session, position and gap in session; ASSISTments: position in assignment, the run of correct answers (the skill builder's stopping state) x MasterySection; XES3G5M: position x demand |
| H4 | a per-learner practice slope (learner-level dynamics) |
| + AR1 | the candidate fast state: delta_{t+1} = rho delta_t + eta, reset at each session start, batch-blind on XES3G5M |

Competing forms on top of H4: a session random intercept (SRI), the residuals of the last three steps
(LAG3), two AR components (2TS), the AR scaled by demand (B2, XES3G5M), carried with decay across
sessions (DECAY). Parameters by the joint filter's own likelihood on a TRAIN fitting sample (CHANGE 1).

**The next-session criterion** (first attempt of each session after the learner's first): (1) H4,
(2) H4 plus the previous session's mean residual, (3) H4 + AR1 with the end-of-session fast state
carried as if it were mastery, (4) H4 + AR1 with it reset (the slow state alone).

## How the hostile review is answered

| section | answer in the design |
| --- | --- |
| 2.A1 leakage | g_hat strictly from earlier responses; TRAIN-only prior and items; A1-leak plants the leak and must score better on the floor (it did, +0.011 to +0.014 nats) |
| 2.A2 practice volume | A1-der keeps count, volume decile and timing and swaps the outcomes (family-matched derangement; SD of g_hat within 10%, asserted); A1-vol is a volume-and-timing prior |
| 2.A3 double counting | A2-cold (= A1), A2-orth (leave-skill-out g), A2-naive; judged on warm intervals and ECE, not log loss alone |
| 2.A4 calibration | a calibration guard (no over-confident intervals; cold ECE not credibly worse by > 0.005) and matched-risk practice saved |
| 2.A5 population vs individual | g is a forecasting coordinate throughout; nothing here says g moves |
| 3.B1 memory | H3's item and skill memory; RESTRICTED steps (previous step on another skill, item new); rho refitted on them |
| 3.B2 batches | XES3G5M batch-blind; same- vs next-submission split; ASSISTments primary |
| 3.B3 selection | calibrated item parameters in every forecast; H3's assignment position and correct-run x MasterySection; ADAPT floor worlds |
| 3.B4 learner heterogeneity | H4's per-learner slope; the HET world; rho per learner tercile |
| 3.B5 learner x item | H3's last-residual-on-this-item; new-item restriction; the LXI world |
| 3.B6 behaviour | H1, then H2, before M; the gain at each layer; the BEH world |
| 3.B7 one shape | SRI, LAG3, 2TS compete; the TWO world; FORM UNIDENTIFIED is a registered outcome |
| 4 tautology | four forecasts from one filter and the same items; the decisive contrast FILTERED vs ABSORBED, and FILTERED vs BASELINE; skill-continuation subset; session-end state by the last answer. The floor showed FILTERED vs ABSORBED is positive in every world, so only FILTERED vs BASELINE carries information |
| 5 w vs v | WN is v made explicit; AR is the candidate w; unobserved A, C, E can look like w |
| 6 floor | eleven Part B worlds (the review's nine, AR-S, BATCH) and world I for Part A |
| 7 engine units | next-answer and next-session log loss, session-start window coverage, practice saved at matched 20% risk; materiality 0.001 nats |
| 8 hierarchy | EXISTENCE / FORM / ENGINE VALUE, each flagged by its own floor family (CHANGE 4) |
| 9 stop/go | `out/stop-go.json` |
| 10 guardrail | a detected M would be "unobserved fast state or process"; teacher, peer, classroom and platform events are unobserved here |

## The variance tree's T4 leaf: the slow / fast split

Shares of the reduction in next-answer Brier score (explained Bernoulli variance) from the item's
success rate (L0) to the full model (L7), forward ladder, TEST answers. Log-loss shares agree to 0.01.

| increment | ASSISTments | XES3G5M | Eedi |
| --- | --- | --- | --- |
| total Brier reduction L0 to L7 | 0.0167 [0.0149, 0.0190] | 0.0193 [0.0172, 0.0217] | 0.0375 [0.0350, 0.0401] |
| L1 general level only | 0.447 | 0.748 | 0.833 |
| L2 + skill-local state | 0.229 | 0.072 | 0.119 |
| L3 + structured factors (C2) | 0.001 | 0.032 | 0.005 |
| **SLOW (L1-L3)** | **0.68 [0.64, 0.71]** | **0.85 [0.83, 0.87]** | **0.96 [0.95, 0.96]** |
| L4 + exposure and item memory | 0.065 | 0.027 | 0.001 |
| L5 + observed process (previous answer and action, selection) | 0.222 | 0.106 | 0.017 |
| L7 + fast state M | 0.021 | 0.010 | 0.011 |
| **FAST (L4, L5, L7)** | **0.31 [0.28, 0.35]** | **0.14 [0.13, 0.16]** | **0.03 [0.02, 0.03]** |
| L6 learner dynamics (per-learner slope, answer noise) | 0.016 [0.011, 0.020] | 0.005 [0.004, 0.008] | 0.014 [0.010, 0.018] |

Leave-one-out from L7 (log loss): dropping the observed-process terms costs the most (+0.0068,
+0.0052, +0.0005), then M (+0.0008, +0.0005, +0.0011). The order of entry favours what enters first.
The forward shares describe predictable variance; they say nothing about leverage.

## The floor (`out/synthetic.json`)

14 worlds of 2,000 learners each (30 skills, 18-30 sessions of 8-16 answers; a general factor
like graph-state's world H).

| world | planted | Part B over H4 | passes |
| --- | --- | --- | --- |
| NULL x2 | nothing fast | NOT DETECTED; UNIDENTIFIED (+0.00002) | yes |
| MEM | item memory | NOT DETECTED | yes |
| ADAPT x2 | adaptive serving, stop at 3 right | NOT DETECTED | yes |
| HET | per-learner gain and forgetting | NOT DETECTED | yes |
| LXI | stable learner x item | NOT DETECTED | yes |
| BEH | hints driven by the previous outcome and hint | UNIDENTIFIED (+0.00019; H0 +0.0136) | yes |
| BATCH | submitted sets with a set-level shift | NOT DETECTED | yes |
| AR-L | AR rho 0.8, tau 0.6 | NOT DETECTED (-0.000004 [-0.00005, +0.00005]; at H0 +0.00009 [-0.00003, +0.00024]); rho-hat 0.5 | **no** |
| AR-S | AR rho 0.8, tau 0.35 | NOT DETECTED; rho-hat 0.5 | **no** |
| ARD | AR x exp(0.5 demand) | UNIDENTIFIED; kappa not recovered | **no** |
| TWO | AR 0.5 + AR 0.97 | NOT DETECTED | **no** (existence) |

Part A passed in every world: A1's share 1.30 and 1.29 in the NULL worlds, A1 over A1-der +0.035 /
+0.031, the planted leak +0.011 / +0.014 over A1; world I gave no learner-specific verdict.

**What the failed floor means.** The instrument is specific: nothing in nine no-M worlds read
PRESENT. But a planted per-answer AR state of 0.35-0.6 logits is worth under 0.0002 nats per answer
to the joint filter. The skill state absorbs its slow part, and the previous-answer control takes
most of the rest, so the instrument cannot see it at 120,000 TEST answers. The real component is a
different shape: persistence near 1, a level for each sitting, and behind the same controls it
gains +0.0006 to +0.0012 nats where AR-L gained nothing (-0.000004). It is still "unobserved fast state or process". A sitting's level can come
from the learner, from the content of the session, from a teacher or classmates, from the device
or the time of day. None of these is observed here (hostile review 10).

## Stop/go for S3 (`out/stop-go.json`)

**HOLD (UNIDENTIFIED).** ASSISTments reads PRESENT and FILTERING IMPROVES, but both carry UNCALIBRATED,
so the registered GO conditions are not met. Recommendation for S3, beyond the registered rule:

- do not add a named momentary state (no AR(1) "M" with kappa x demand);
- carry a generic per-session level shift as a candidate fast component, reset at the session
  boundary (an SRI with tau about 0.2-0.3 logits), and keep it only if S3's own ablation and floor
  justify it;
- record the earlier streak result (residual-structure R2) as mostly local dependence already
  explained by the previous answer and action, plus a small session-level shift.

Part A's line for S3's g layer: the cheapest variant passing on all three corpora is A1-global. A1,
A2-orth and C2g pass too.

## What a product engine should implement first

**A1, the learner-informed cold-start prior with a per-skill map, then A2-orth.** In engine units:

- **Per learner:** one general level with its precision. This is C2g's general-factor posterior, a
  scalar update per response.
- **Per skill, fitted offline:** mu_k and lambda_k for the map, and the factor loading and unique
  variance for the tracker.
- **One global value:** n0, between 2 and 3.

At a skill's first attempt the Beta starts at Beta(n0 p0, n0 (1 - p0)), with logit p0 = mu_k + lambda_k g.
Decay pulls toward that prior.

- It captures 91-101% of the full coupled state's first-encounter gain: +0.040 to +0.064 nats and
  +0.06 to +0.10 AUC per first attempt.
- Over all attempts it is worth +0.013 to +0.027 nats, and it saves 17-58 unneeded items per 1,000
  attempts at matched 20% risk.
- It needs no new uncertainty machinery, and its intervals are better than the shipped engine's.
- A1-global, with a single mu and lambda, is the registered cheapest pass, but it keeps only 58% of
  the gain on ASSISTments. The two numbers per skill are worth their cost.

**Second, A2-orth.** It keeps the Beta's evidence separate from its prior part and re-centres the
prior on the general level with the skill's own evidence removed. That adds +0.001 to +0.005 nats on
every attempt and 1.5-5 more items saved per 1,000. Do not use the naive blend: on ASSISTments it
double-counts.

**Do not add a momentary-state term yet.** On these corpora a fast component is worth 0.0006-0.0012
nats per answer behind the controls, and under 0.001 at the next session. The floor could not
calibrate it.

## Limits

- Open corpora, not Lazuli's; subsamples of 1 in 3 (ASSISTments), 1 in 4 (XES3G5M), 1 in 12 (Eedi).
- Observational logs under each platform's own item-selection policy: D depends on X-hat. No number
  here is an effect of a design.
- **Part B's floor failed for existence, form and engine value.** The instrument does not detect a
  planted per-answer AR state of the sizes tried. Real-data Part B verdicts are uncalibrated, and
  NOT DETECTED would not have been informative.
- The decoupled extended-Kalman step ignores posterior correlation between the skill state and the
  extra components; rho is biased low in planted worlds (0.5 for 0.8).
- The control stack is two-stage (gamma fitted on the base filter's state). M's parameters are fitted
  on a TRAIN fitting sample of 86,000-138,000 attempts.
- XES3G5M's timestamps cannot separate a sitting from a submitted set. Eedi keeps last answers only,
  in last-answer order, with minute timestamps. Only ASSISTments has hint and response-time traces,
  and they are traces O^A, not the activity.
- demand_i (XES3G5M) is externally rated task demand from text without figures. It is not
  experienced cognitive load, which may depend on the learner's state, how the activity is
  organised, the context and the goal's significance.
- g is a forecasting coordinate in p(X). Part A shows that it forecasts new skills. It says nothing
  about whether g moves with experience, and nothing about transfer.
- C2's rank is graph-state's (8, 2, 8), not re-selected on these subsamples.
- The session-start window coverage assumes the session's first five attempts share the first
  attempt's state. It uses single-skill windows only, and XES3G5M has only 620 of them.

## Reproduce

    python3 state_timescales.py synthetic p1 NULL I AR-L AR-S     # parts in parallel; intermediates in <scratch>/s2-tmp
    python3 state_timescales.py synthetic p2 ARD MEM ADAPT
    python3 state_timescales.py synthetic p3 HET LXI BEH BATCH TWO
    python3 state_timescales.py merge
    python3 state_timescales.py assist | xes | eedi                # about 1.1 h, 1.1 h, 0.7 h; peak 2.3 GB
    python3 state_timescales.py stopgo

