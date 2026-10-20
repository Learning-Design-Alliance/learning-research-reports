"""PRE-REGISTERED: the minimum grey-box model (S3). Which components of the state X are justified by
held-out forecasting across corpora, and what is the smallest adequate model?

SYSTEM-MODEL.md section 7 fitted as a whole. Brief: docs/notes/NEXT-ROUND.md S3 as adjusted by "Round 2
(launched 2026-10-02)": M4 (S1's factors) is SKIPPED because S1's out/stop-go.json reads NO GO, so the
structured layer is recorded UNIDENTIFIED (g + skill-local state only); M3 is replaced by M3', a
GENERIC per-session level shift with no named momentary term, because S2 Part B's stop/go reads HOLD
(UNIDENTIFIED); M1 is warm-started from S2's A1 learner-informed cold-start prior. The leakage and
double-counting safeguards of docs/notes/S2-HOSTILE-REVIEW.md apply (point by point below). Written
2026-10-02 before any statistic of this design on real data; only S1's and S2's committed READMEs and
out/*.json, and the loaders' code, were read.

Answers are about these platforms' activity systems under their own curricula, tools, rules and
item-selection policies (SYSTEM-MODEL.md section 1). No state is described as located solely in the
learner. The corpora were collected under the platforms' own item-selection policies (D depends on
X-hat), so every forecast conditions on the served item and its timing, and no forecast gain is read
as an effect of D.

DATA (raw data never enters the repo; out/ holds aggregates only). Loaders, row definitions,
competencies and learner subsamples are state-timescales' (S2), imported from
../state-timescales/state_timescales.py unchanged: ASSISTments 2012-13 (1 in 3; competency skill_id;
hint, bottom-out, attempt count, first-response time, assignment and section type per problem log),
XES3G5M through data_path("XES_DIR") (1 in 4; leaf KC; demand = the panel's element-interactivity
rating), Eedi 2020 (1 in 12; level-3 subject; QuizId). TRAIN/TEST by e2e.py's learner hash
(sha256(uid) % 5 == 0 is TEST). Everything is fitted on TRAIN and measured on TEST; 200 learner
bootstraps, the same draws for every model. Grids run on S2's FITTING SAMPLE (the TRAIN validation
quarter, halved until it holds at most 150,000 attempts). SESSIONS: a gap over 30 minutes; Eedi: a quiz
sitting. XES3G5M answers sharing a millisecond timestamp form one submission (session components are
batch-blind there, as in S2). Eedi runs M0-M2 only (last-answer order). Nothing inferred about a learner
is read; there are no learner attributes in these models.

THE STATE AND ITS OBSERVATION (one filter for the Gaussian family; gstate.run_gauss extended)
  theta_lk(t) = mu_k + lambda_k g_l(t) + u_lk(t)          (rank 1: g plus skill-local; no f_j, S1 NO GO)
  S = theta_eff + beta x + m_li + h_learn + h_A + sum_c l_c c      (the linear predictor)
  P(y = 1) = c_i + (d_i - c_i) sigmoid(a_i (S - b_i))    (4PL, probit-integrated over the predictive
                                                          variance of theta_eff)
  theta_eff = the mean of the item's skills (compensatory; competitors below). u_lk is held, as in
  graph-state, as decaying Gaussian pseudo-measurements (the engine's retention curve); beta x is the
  deterministic gain per practice (x = mean log(1 + earlier attempts on the item's skills)).
  READ-DECAY (all Gaussian models): before a prediction the target skill's evidence is decayed by the
  retention since its last evidence and the general factor's posterior is adjusted for that skill's
  changed contribution (the same decayed state the update then uses), so a state frozen for 30 days
  forecasts with its evidence aged. With read-decay off and no extras the filter must equal
  gstate.run_gauss to 1e-9 (asserted).
  Population prior (mu_k, lambda_k, D_k) by graph-state's EM on TRAIN cells (gstate.cells, fit_dense
  r = 1; r = 0 for M0-G); items a, b and beta refitted on the filter's own TRAIN state (two passes, as
  gstate.refit_items, with read-decay). Dynamics parameters by the joint filter's own TRAIN likelihood
  over a grid (replicated learners, one parameter set per replica: S2 CHANGE 1), i.e. coordinate-wise
  maximum likelihood after the EM. Extra components use S2's decoupled extended-Kalman step (tstate.Comps).

MODELS (forward nesting, each adding to the previous; Eedi stops at M2)
  M0     the calibrated independent engine (C0, E5-decay; independent Beta per skill), as shipped.
  M0-G   the Gaussian filter with no general factor (r = 0): the nesting-clean base for g.
  M1     + g, STATIC (g_{t+1} = g_t): the rank-1 filter. Warm-started from S2's A1: the new skill's
         state starts at mu_k + lambda_k g-hat, g-hat from strictly earlier responses; S2's A1 on the
         engine's Beta (Beta(n0 p0, n0 (1 - p0)), logit p0 = mu_k + lambda_k g-hat; mu_k, lambda_k on
         TRAIN first attempts by S2's fit_map, n0 on S2's grid by TRAIN-validation log loss; the
         g-tracker is M1's) is reported beside it as M1-engine, the engine-implementable reading.
         g is a forecasting coordinate in p(X), not a learner mechanism, until shown otherwise.
     competitors to M1 (g dynamics; each against M1 static):
         M1-drift  g a random walk: Var(g) grows by q_g per day between a learner's attempts;
                   q_g in {1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2}.
         M1-learn  g_l(t) = g_l(0) + gamma f(N_lt), entering S as gamma lambda-bar f(N) (lambda-bar =
                   the mean loading of the item's skills; the filter de-trends g's evidence by it). Three
                   forms, the best by TRAIN likelihood: per practice (f = N / 100, N = the learner's
                   earlier attempts), per log practice (f = log(1 + N)), and per practice on
                   high-general-loading items (f = sum over earlier attempts of lambda-bar / (100 times
                   the mean loading)). gamma in {-0.4, -0.2, -0.1, -0.05, 0, 0.05, 0.1, 0.2, 0.4} (log
                   form) and {-0.2, -0.1, -0.05, -0.02, 0, 0.02, 0.05, 0.1, 0.2} (per-100 forms). SIGNED:
                   a positive gamma means g rises with practice. A positive M1-learn result is
                   observational: selection (who stays), platform drift and item mix can each produce it.
  M2     + item memory m_li = alpha exp(-hours since the learner's last exposure to item i / tau_m)
         (0 before the first exposure): a jump on exposure that decays. alpha in {-0.5, -0.25, 0.1,
         0.25, 0.5, 0.75, 1.0, 1.5} (signed: a negative alpha is a re-exposure penalty, which the
         serving policy can produce), tau_m in {1, 6, 24, 72, 240, 720} hours. Exposure only, no
         outcome, so it is known at forecast time. Testable where TEST has >= 2,000 attempts on an
         item the learner has seen.
  M2+WN  + an answer-noise component WN (rho = 0, tau_w in {0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.3,
         1.6, 2.0}): part of H, not a state component (S2 CHANGE 3: any extra component widens the slow
         state's evidence noise; WN is that effect alone). Reported; carried from here on.
  M3'    + a GENERIC per-session level shift delta_s ~ N(0, tau_s^2), constant within a session and
         reset at each session start (S2's SRI; rho = 1, no innovation), tau_s in {0.05, 0.1, 0.15,
         0.2, 0.3, 0.4, 0.5, 0.6, 0.8}. No named momentary term: a sitting's level is "unobserved fast
         state or process" (the learner, the content of the session, a teacher or classmates, the
         device, the time of day), not fatigue, attention or affect.
  M5     + learner-level heterogeneity in Phi (theta_l, hierarchical): a per-learner gain beta_l ~ N(0,
         sigma_b^2) on x and a per-learner forgetting slope f_l ~ N(0, sigma_f^2) on log(1 + days since
         the item's skills' last evidence) (0 at first encounters); static components estimated online;
         sigma_b in {0, 0.05, 0.1, 0.15, 0.2, 0.3} x sigma_f in {0, 0.05, 0.1, 0.2, 0.3}. Reported:
         the spread sigma-hat.
  M6     + observed activity traces O^A (ASSISTments only): on the previous problem in the session, a
         hint used, the bottom-out hint, more than one attempt, log(1 + seconds to first response), a
         rapid response (< 5 s), hint x previous outcome (S2's H2 columns). Coefficients by penalised
         Fisher scoring on the running model's TRAIN state, then a joint-likelihood scale zeta in {0,
         0.5, 0.75, 1, 1.25, 1.5}. Strictly earlier attempts: the current problem's hint request is
         scored as an incorrect first action on ASSISTments (it is the outcome, not a predictor) and its
         response time is concurrent with the answer. Traces are partial observations of the realised
         activity; nothing here identifies the organisation of activity from hints and time.
  M4     SKIPPED (S1 NO GO): the structured layer is UNIDENTIFIED.
  FULL   M6 plus the better (TRAIN likelihood) of M1-drift and M1-learn: every component testable on
         the corpus, each with its forward-fitted parameters.

COMPETING FUNCTIONAL FORMS (each scored on the same held-out criterion; none assumed)
  COMBINATION on multi-skill items, on M1: compensatory mean (M1); conjunctive (the weakest skill
    dominates: theta_eff = sum w_k m_k, w = softmax(-s m) over the item's skills at their predictive
    means, evidence to skill k with precision J w_k: a linearised noisy-AND); disjunctive (w =
    softmax(+s m): a linearised max). s in {1, 3}; each form, compensatory included, gets a
    multi-skill intercept in {-0.4, -0.2, 0, 0.2, 0.4} (fitted on TRAIN), so a level difference is not
    read as a form. Scored on multi-skill TEST attempts (>= 2,000 needed, else NOT TESTABLE) and on all.
  LINK, on M1: the logistic link on the additive linear predictor against a non-linear (power-logistic)
    link, P = c + (d - c) sigmoid(z)^nu, nu in {0.5, 0.7, 1.4, 2.0}, with a global location shift in
    {-0.6, -0.3, 0, 0.3, 0.6} (fitted jointly on TRAIN).
  SESSION-SHIFT FORM, on M3': additive in S (M3'); demand-scaled (the shift times exp(kappa demand_i),
    kappa in {-0.5, -0.25, 0, 0.25, 0.5, 0.75}, XES3G5M only); entering the slip asymptote (the shift
    added to logit d_i, tau grid as M3'). demand_i is externally rated task demand, not experienced
    cognitive load.

HORIZONS AND METRICS (TEST learners; gain = log loss of the reference minus the model, nats per scored
attempt; the same items, served items and timing for every model)
  H1 NEXT ANSWER   every TEST attempt, one step ahead (the filter predicts, then updates).
  H2 NEXT SESSION  the first attempt of every session after the learner's first, from the state at the
                   end of the previous session (session-level terms reset). >= 2,000 needed.
  H3 30 DAYS       a frozen pass: each TEST learner with >= 20 attempts is cut at their median attempt;
                   after the cut nothing updates (skill evidence, g, components); drift and decay still
                   act with elapsed time. Scored: attempts at least 30 days after the cut. The forecast
                   conditions on the schedule (served items, their times, exposure and practice counts:
                   D and timing) but on no outcome or trace after the cut: M6's features after the cut
                   take their TRAIN means; session shifts sit at their prior. >= 2,000 scored attempts
                   from >= 100 learners needed, else NOT TESTABLE.
  At each horizon: log loss, AUC, ECE (10 quantile bins). At H1 also: coverage of central 50/80/95%
  intervals for the count correct in 5 consecutive single-skill attempts (cold and warm windows,
  graph-state's PIT) and unneeded practice per 1,000 at matched 20% premature-advance risk (10%, 30%
  reported).
  LOSES CALIBRATION: at some testable horizon the model's ECE exceeds its reference's with the
  difference's lower bound above 0.005, or its H1 window intervals are OVER-CONFIDENT (a coverage more
  than 0.05 below nominal) where the reference's are not.

THE KEEP RULE (per corpus, then across corpora)
  KEPT (forward) on a corpus: the component's gain over its forward reference has lower bound > 0 at
    EVERY testable horizon and it does not lose calibration. (If only H1 is testable the verdict is
    marked "(ONE HORIZON)".) Forward references: M1 vs M0 AND vs M0-G; M1-drift and M1-learn vs M1;
    M2 vs M1; M3' vs M2+WN; M5 vs M3'; M6 vs M5.
  DETECTED: the forward gain at H1 has lower bound > 0 (reported with the horizon profile: the set of
    horizons with lower bound > 0).
  LOO: dropping the component from FULL costs (lower bound > 0) at H1, after refitting its registered
    substitutes (below) on their grids.
  NOT DISCRIMINABLE: its LOO lower bound <= 0 while dropping it together with a registered substitute
    costs (lower bound > 0).
  ESTIMABLE: its parameter's profile-likelihood set (Delta TRAIN log likelihood >= -1.92 on the grid)
    spans at most three adjacent grid values and excludes the null value (0, or sigma = 0).
  ACROSS CORPORA (testable = the corpora where it can be fitted: g and g dynamics 3; M2 where repeats
    exist; WN, M3', M5 on ASSISTments and XES3G5M; M6 on ASSISTments only):
    JUSTIFIED      KEPT and LOO > 0 on at least 2 of the testable corpora (all of them if 2 are
                   testable).
    UNIDENTIFIED   KEPT on at least 2 but NOT DISCRIMINABLE on those; or testable on one corpus only
                   and KEPT with LOO > 0 there ("UNIDENTIFIED (ONE CORPUS)"); or the structured layer
                   (fixed by S1).
    NOT JUSTIFIED  otherwise; the horizon profile is appended, e.g. "NOT JUSTIFIED (DETECTED AT H1
                   ONLY)".
  SMALLEST ADEQUATE MODEL = {g if JUSTIFIED} + {skill-local state, always: it is the engine} + {every
    JUSTIFIED component}; per corpus, the components KEPT with LOO > 0 there. The g-dynamics verdict:
    G STATIC ADEQUATE (neither competitor kept), G DRIFTS (OBSERVATIONAL), G MOVES WITH PRACTICE
    (OBSERVATIONAL) with gamma-hat > 0, G FALLS WITH PRACTICE (OBSERVATIONAL) with gamma-hat < 0, or G
    DYNAMICS UNIDENTIFIED (both kept and neither beats the other at H3, lower bounds <= 0).
  FORM verdicts: "<form> SUPPORTED" if it beats each alternative (lower bound > 0, on multi-skill
    attempts for combination, on all attempts otherwise, at H1) without losing calibration; "<family>
    UNIDENTIFIED" otherwise; NOT TESTABLE where the data cannot carry it.

THE ABLATION IN FOUR FORMS (THEORETICAL-FOUNDATIONS.md, "Ablation as a theory stress-test")
  1. FORWARD NESTING: the chain above, every horizon.
  2. LEAVE-ONE-COMPONENT-OUT from FULL: drop each of g, g dynamics, M2, WN, M3', M5, M6. Registered
     substitutes are refitted when their partner is dropped: g <-> M3' (a learner's level vs a sitting's
     level), M3' <-> WN (a sitting's shift vs answer noise), g dynamics <-> M5 (practice effects common
     vs per learner), M3' <-> M6 (an unobserved sitting level vs observed traces). Pair blocks: each pair
     dropped together. Importance is never awarded from the order of entry.
  3. BLOCK ABLATION: FAST = {M2, WN, M3', M6}; LEARNER-LEVEL = {g dynamics, M5}; each family removed
     from FULL, every horizon.
  4. MISSPECIFICATION CHALLENGE: a wrong named mechanism, item memory keyed to the wrong item (each item
     mapped to another item of the same first skill by a family-matched derangement, so it fires on
     same-skill exposures of the same size), fitted on the same grid, against FLEX = M1 + WN + M3' + M5
     (the flexible latent terms, refitted without memory): FLEX, FLEX + wrong memory, FLEX + right
     memory. WRONG MECHANISM REJECTED if FLEX + wrong does not beat FLEX (lower bound <= 0) and right
     beats wrong (lower bound > 0); WRONG MECHANISM CREDITED if FLEX + wrong beats FLEX (right minus
     wrong reported beside it); NOT DIAGNOSTIC if right does not beat FLEX. The share of the right
     mechanism's gain that wrong + flexible terms recover, and how tau_s and sigma_b move when memory is
     omitted, are reported (do the flexible terms absorb it?).
  Reported separately: whether a component is detectable, whether its parameters are estimable, and
  whether it is discriminable from its substitutes.

ALSO REPORTED
  WITHIN-LEARNER DRIFT IN g against experience volume (descriptive, TEST): g estimated (MAP, N(0, 1)
    prior, M1's prior and items, skill-local variance integrated) from first attempts on new skills in
    the first and the second half of each learner's attempts (>= 10 first attempts in each half);
    slope of g2 - g1 on log(1 + attempts) and its learner-bootstrap interval. Observational: regression
    to the mean, selection, platform drift and item mix all move it. The floor reports it in a static
    and a learning world.
  THE CLOSED LOOP: ASSISTments' skill builders (MasterySection: fixed stopping at three in a row) are a
    known policy; H1 gains are reported for MasterySection and other problems separately. No randomised
    assignment exists in these three corpora (the PSABANRN arms are in another dataset).
  FITTED MODEL as equations with parameter values; a PRACTICAL-IDENTIFIABILITY TABLE (each grid
    parameter: estimate, bootstrap interval of the grid argmax over 200 learner resamples of the fitting
    sample, profile set, flags NOT PINNED / NULL NOT EXCLUDED / AT GRID EDGE; the same from the floor
    against the planted value; for the EM prior, medians and spreads of mu_k, lambda_k, D_k); the share
    of the H1 Brier reduction from CLIM to FULL taken by each forward step (VARIANCE-TREE T4 style).
  LEVERAGE-MAP STUB: which components have any do() evidence (only D's order and spacing, from the
    order trials); every S3 result is observational.
  HOLES: SIGNIFICANCE S_t (theoretically specified, unobserved, unidentified) and other actors' events
    E_t (teacher, peers, classroom; unobserved in these corpora). Listed so the model's absences are
    explicit.

SYNTHETIC FLOOR (`python3 grey_box.py synthetic`; before any real statistic). Simulated from M5 itself
  with components switched on and off. 2,000 learners (TRAIN/TEST by the same hash on synthetic ids),
  30 skills x 12 items (half MC c ~ U(0.1, 0.3); fill-in c ~ U(0.02, 0.08); slip ~ U(0, 0.04); a ~
  logN(0, 0.25); b = skill offset N(-0.6, 0.6) + N(0, 0.7)); g ~ N(0, 1), lambda_k ~ N(0.85, 0.1^2),
  u_lk(0) ~ N(0, 0.48) (graph-state's world H); 18-30 sessions of 8-16 attempts 20-120 s apart, 2 hours
  to 20 days between sessions, 1-2 skills per session (60% new while any remain), the item drawn
  uniformly from the skill's 12 and the previous item re-served with probability 0.25; practice gain
  per attempt decaying by the engine's curve; a hint flag per attempt (P = 0.10 + 0.30 (1 - previous
  y)) recorded in every world. Components when ON: M5 gain_l ~ N(0.15, 0.12^2) (>= 0) and forgetting
  rate log-uniform over a factor 9 (OFF: 0.15 and the engine's rate); M2 +1.0 exp(-hours / 24) on
  re-exposure; M3' delta_s ~ N(0, 0.5^2); M6 +0.6 logits on the attempt after a hint in the same
  session; drift q_g = 0.003 per day; learn gamma = 0.10 per log practice.
    W1 CORRECT THEORY, NO LATENT RESIDUAL: g, M2, M5, M6 on.
    W2 CORRECT THEORY + A GENUINE UNKNOWN PROCESS: W1 + the session shift.
    W3 MINIMAL: g only (homogeneous gain, no memory, no session, hint without effect).
    W4 DRIFT: W3 + g random walk.          W5 LEARN: W3 + g learning with practice.
    W6 WRONG THEORY + FLEXIBLE LATENT RESIDUAL: W1's data, the misspecification challenge's candidate set.
    W7 OMITTED OBSERVED CONTEXT: W3 + a per-session context flag (P = 0.3, recorded as a trace) that
       shifts its session by -0.6 logits; the flag enters only M6, after M3' in the forward order.
    W8 CORRELATED COMPONENTS (UNIDENTIFIED): each learner works in ONE sitting of 60-150 attempts over the
       skills, lambda_k = 1: a learner's general level and a sitting's level cannot be told apart from
       the observations. Only H1 is testable.
  Two seeds per world (20261002, 20261003); W6 uses W1's seeds.
  PASS RULES (every seed; per component and per family, KEEP = the single-corpus verdict "KEPT and LOO >
  0", DETECT = the H1 lower bound > 0):
    g:        KEPT in W1-W7; in W8 NOT DISCRIMINABLE from M3' (not "KEPT and LOO > 0").
    g drift:  KEPT in W4 only.        g learn: KEPT in W5 only (gamma-hat > 0); the g-dynamics verdict
              reads G STATIC ADEQUATE in W1-W3, W7.
    M2:       KEPT in W1, W2; not KEPT in W3, W4, W5, W7, W8.
    M3':      KEPT in W2; not KEPT in W1, W3, W4, W5; in W7 and W8 not "KEPT and LOO > 0".
    M5:       KEPT in W1, W2; not KEPT in W3, W4, W5, W7, W8.
    M6:       KEPT in W1, W2; DETECTED in W7; not KEPT in W3, W4, W5, W8.
    W6:       right memory beats wrong (lower bound > 0) in both seeds.
    DETECT family: DETECTED wherever planted, not DETECTED wherever absent (same sets).
  A component whose KEEP checks fail carries "(UNCALIBRATED)" on its real KEEP verdicts; a failed
  DETECT check flags its DETECTED readings; a failed W6 flags the misspecification verdicts; W8 flags
  the NOT DISCRIMINABLE logic. EXPLANATORY RECOVERY is reported beside forecast performance: the kept
  set against the planted set, and each planted parameter against its profile set. A model that
  forecasts well while assigning the effect to the wrong component passes as engineering and fails as
  explanation; the floor table says which.
  PARTICLE-FILTER CHECK: on W1 and W2 seed 20261002, 200 TEST learners, a bootstrap particle filter
  under the true generative model and true parameters (2,000 particles); the EKF FULL model's H1 log
  loss minus the particle filter's is reported. A gap above 0.01 nats per answer is stated as a limit
  of the extended-Kalman approximation.
  The machinery is debugged on worlds of these shapes with other seeds (100+) before the floor runs.

STOP RULES
  - The floor runs before any real statistic. If M1 is not KEPT in W3 (the simplest world) the
    machinery is broken: stop, fix, record the fix in CHANGES, rerun the floor.
  - Peak RAM above 5 GB or free disk under 600 MB: stop writing intermediates, record, reduce (a
    smaller learner sample is a CHANGE with its reason) before any affected statistic is read.
  - A corpus run that would exceed about 4 hours drops the H3 pass of the functional-form comparisons
    first (recorded as a CHANGE), never a component of the chain.
  - Thresholds and verdict strings are not changed after real numbers are seen; any post-registration
    change goes into CHANGES with its reason and the point at which it was made.

HOSTILE REVIEW SAFEGUARDS (docs/notes/S2-HOSTILE-REVIEW.md)
  2.A1 leakage: g-hat strictly from earlier responses; prior, items and every parameter from TRAIN;
    the 30-day pass sees no outcome or trace after the cut.  2.A2 volume: M1-learn's feature is
    practice volume, but g_l(0) is estimated within learner, so a between-learner volume difference
    enters g, not gamma; the descriptive drift regression is reported as observational.
  2.A3 double counting: the decoupled step gives the skill evidence precision 1 / (1/J + the
    components' variance), so a response is not counted at full weight twice; LOO and pair blocks show
    substitution; calibration (ECE, window coverage) is part of the keep rule.  2.A4 calibration: the
    LOSES CALIBRATION clause.  2.A5: g is a forecasting coordinate throughout.
  3.B1-B7 (fast state): M3' is generic and reset at the session boundary; item memory (M2) and
    learner heterogeneity (M5) are separate components; O^A enters only from earlier attempts; XES3G5M
    is batch-blind; forms compete (additive / demand / slip).  4 tautology: H2 is scored with session
    terms reset, and the session shift's value at H2 and H3 can come only through a better slow state.
  5 w vs v: WN is v made explicit; M3' is a candidate w; unobserved A, C, E can look like w.
  10 guardrail: a sitting's level is "unobserved fast state or process", not a named learner state.

INTERPRETATION GUARDRAIL (SYSTEM-MODEL.md section 1): regularities of these platforms' activity systems;
  hints and response times are traces O^A, not activity; demand_i is task demand, not experienced load;
  outcomes are not collapsed into one scalar (log loss, AUC, calibration and practice cost per horizon).

LIMITS stated in advance: open corpora, mostly maths, not Lazuli's; observational logs under each
  platform's own item-selection policy; the extended-Kalman step is decoupled and ignores posterior
  correlation between the skill state and the extra components; dynamics parameters are grid maxima on
  a fitting sample; the items are fitted once on M1's state, not per model; the conjunctive and
  disjunctive forms are linearised (soft-min / soft-max weights), not exact noisy-AND / max with
  refitted items; XES3G5M's timestamps cannot separate a sitting from a submitted set; Eedi keeps the
  last answer per question; only ASSISTments has traces and only XES3G5M has demand ratings; the rank-1
  prior leaves the structured layer out by decision (S1).

DIRECTION: symmetric -- no edge between skills is oriented. The general level, its dynamics, item
  memory, the session shift and the learner-level terms are undirected state terms; the signed
  parameters (gamma, alpha) are checked by sign in their own verdicts, so no reversed-arrow control
  applies.

CHANGES (after registration; each before the affected statistic is read)
  Changes 1-4 came from development worlds (seeds 100+, not the floor's), before the floor and before
  any real statistic.
  1. The floor's skill-local practice gain is the model's own form: rate_l log(1 + earlier attempts on
     the skill); with M5 on, rate_l = 0.3 + N(0, 0.15^2) and a per-learner forgetting slope -phi_l
     log(1 + days since the skill's last attempt), phi_l ~ N(0, 0.1^2); with M5 off, 0.3 and 0. Reason:
     the brief asks for a floor simulated from M5 itself, and the registered gain (+0.15 per attempt
     decaying by the engine's curve, S2's world) is not a form the model can represent; in development
     world W8 its unrepresentable part was credited to M1-learn and to the trace term. Misspecification
     is the W6 challenge's job, not every world's.
  2. tau_s's grid gains 1.0 and 1.3. The registered top (0.8) is below the general level's planted SD
     (1.0), so in W8 a sitting's level could not substitute for g by construction and the g <-> M3'
     discriminability test was biased toward g.
  3. The update step is assumed-density filtering (moment matching): the score and observed information
     of the probit-integrated likelihood in the predictive mean, and a pseudo-measurement of precision
     J / (1 - v J), instead of the Laplace step at the point. In a development W3 world with the TRUE
     parameters and no evidence decay, the Laplace step preferred a spurious general learning term
     (+21.5 TRAIN nats at gamma = 0.05 per 100 attempts) and fell 46 nats short of the exact filter;
     moment matching removed the spurious term (-2.1 to -12.6 nats) and came within 2.9 nats of the
     exact filter. With the Laplace step and every option off the filter still equals gstate.run_gauss
     to 1e-9 (asserted). Items are refitted on the moment-matching filter's state.
  4. The particle-filter check is an exact quadrature filter under W3's generative model (g on a
     41-point grid, each skill's u on a 21-point grid given g), against M1 at H1 on W3 seed 20261002. A
     bootstrap particle filter with 2,000 particles degenerates in a 31-dimensional static state, so it
     would not be a reference. W1 and W2 add two per-learner static dimensions and are not checked so.
  5. Leaving g out of FULL keeps M1's prior (mu_k, D_k) and items with the general loading set to 0,
     instead of the r = 0 refit (M0-G's), so the drop removes only g and the refitted substitute (the
     session shift) can take up its variance. In development W8 the r = 0 prior already carried g's
     variance in D_k and its best substitute stood 440 TRAIN nats behind M1; with M1's prior less g it
     stood 69 behind. M0-G stays the forward reference for g.
  6. W8's check is its own family (ND): it tests whether the leave-one-out and pair-block logic can
     return NOT DISCRIMINABLE for substitutable components, a property of that logic, not of g's
     forward gains. A failed ND family flags every LOO and NOT DISCRIMINABLE reading (so every
     JUSTIFIED verdict carries "discriminability uncalibrated"); g's KEEP family is W1-W7 plus g being
     KEPT forward in W8. In development W8 the decoupled extended-Kalman session shift did not
     substitute fully for the coupled general factor (69 nats), so this logic may fail its floor.
  7. Reporting only, after the real runs: verdicts() names the corpora on which a NOT JUSTIFIED
     component was kept, and priors() summarises the cached base fit for the equations. No statistic,
     threshold or verdict changed.

RESULTS (README.md has the tables). Floor (out/synthetic.json, code at 2c56c68): FAILS for KEEP_drift,
  KEEP_learn, DETECT_learn, KEEP_M3', KEEP_M5, KEEP_M6, the g-dynamics verdict and ND; passes for KEEP_g,
  DETECT_g, KEEP_M2, DETECT_M2, DETECT_drift, DETECT_M3', DETECT_M5, DETECT_M6 and MISSPEC. Exact
  filter minus M1 on W3: 0.0017 nats. Real: SMALLEST ADEQUATE MODEL = {skill-local state, g}; g
  JUSTIFIED (discriminability uncalibrated), M1 over M0 +0.020 / +0.035 / +0.038 nats at the next
  answer, +0.034 / +0.035 / +0.057 at the next session, +0.038 / +0.040 / +0.066 at 30 days
  (ASSISTments / XES3G5M / Eedi); g dynamics NOT JUSTIFIED (UNCALIBRATED; G STATIC ADEQUATE,
  G STATIC ADEQUATE, G DYNAMICS UNIDENTIFIED); M2 NOT JUSTIFIED (kept on XES3G5M only); M3', M5, M6
  NOT JUSTIFIED (UNCALIBRATED), each detected at the next answer only; linear link supported on all
  three; combination unidentified; additive session shift over the slip form.

    python3 grey_box.py synthetic | assist | xes | eedi | verdicts
"""



from __future__ import annotations

import gc
import json
import math
import pickle
import resource
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p_ in (ROOT, ROOT / "studies/measurement/engine-calibration", ROOT / "studies/measurement/graph-state",
           ROOT / "studies/measurement/state-timescales", HERE, ROOT / "studies/end-to-end/xes3g5m-build"):
    sys.path.insert(0, str(p_))
import calibrate as C  # noqa: E402
import engine as E  # noqa: E402
import gstate as S  # noqa: E402
import coupling as CP  # noqa: E402
import tstate as T  # noqa: E402
import state_timescales as S2  # noqa: E402
import gbox as G  # noqa: E402
from shared.paths import scratch_root  # noqa: E402

OUT = HERE / "out"
TMP = scratch_root() / "s3-tmp"         # fitted parameters and floor parts; deleted after
SEED = 20261002
FLOOR_SEEDS = (20261002, 20261003)
CH = 40
RISKS = (0.20, 0.10, 0.30)
LEVELS = (0.5, 0.8, 0.95)
QG = (1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2)
G_LOG = (-0.4, -0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2, 0.4)
G_100 = (-0.2, -0.1, -0.05, -0.02, 0.0, 0.02, 0.05, 0.1, 0.2)
ALPHA = (-0.5, -0.25, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5)
TAU_M = (1.0, 6.0, 24.0, 72.0, 240.0, 720.0)
TAU_W = (0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.3, 1.6, 2.0)
TAU_S = (0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.3)      # CHANGE 2: 1.0, 1.3 added
KAPPA = (-0.5, -0.25, 0.0, 0.25, 0.5, 0.75)
SIG_B = (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)
SIG_F = (0.0, 0.05, 0.1, 0.2, 0.3)
ZETA = (0.0, 0.5, 0.75, 1.0, 1.25, 1.5)
S_COMB = (1.0, 3.0)
MS_SHIFT = (-0.4, -0.2, 0.0, 0.2, 0.4)
NU = (0.5, 0.7, 1.4, 2.0)
SHIFT = (-0.6, -0.3, 0.0, 0.3, 0.6)
N0_GRID = (0.5, 1, 2, 3, 5, 8, 13, 20)
MIN_H, MIN_L30, MIN_REPEAT, MIN_MS = 2000, 100, 2000, 2000
ECE_TOL = 0.005
T0 = time.time()


def log(*a):
    gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    print(f"[{time.time() - T0:7.0f}s {gb:4.1f}GB]", *a, flush=True)


def jdump(x):
    return json.dumps(x, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else
                      bool(o) if isinstance(o, np.bool_) else str(o)) + "\n"


# ---------------------------------------------------------------- model specifications

def spec(**kw):
    m = dict(prior="g", qg=0.0, learn=None, mem=None, wmem=None, wn=None, sri=None, kappa=None, slip=None, m5=None,
             m6=None, comb="comp", s=0.0, ms=0.0, nu=1.0, shift=0.0)
    m.update(kw)
    return m


def w_(m, **kw):
    d = dict(m)
    d.update(kw)
    return d


def describe(m):
    """The model's components and parameter values (for the record)."""
    out = {"prior": {"g": "g + skill-local", "g0": "skill-local, M1's prior without g", "0": "skill-local only (no g)"}[m["prior"]]}
    for k in ("qg", "learn", "mem", "wmem", "wn", "sri", "kappa", "slip", "m5", "m6", "ms"):
        if m[k] not in (None, 0.0):
            out[k] = m[k]
    if m["comb"] != "comp":
        out["comb"] = [m["comb"], m["s"]]
    if m["nu"] != 1.0 or m["shift"] != 0.0:
        out["link"] = [m["nu"], m["shift"]]
    return out


class Split:
    """One set of learners: Attempts, Struct, extras and the feature store."""

    def __init__(self, cp, data, mask, lam, wmap, demand=None):
        self.at = S.Attempts(data, mask)
        ext, quiz = S2.extras_for(cp, self.at)
        self.ext = ext
        self.st = T.Struct(self.at, quiz, cp.batch)
        self.fe = G.Feats(self.at, self.st, ext, lam, wmap=wmap)
        self.fe.demand = None if cp.demand is None else cp.demand[self.at.i]


class Ctx:
    def __init__(self, fit, K):
        self.fit, self.K = fit, K
        self.m6_mean = 0.0

    def kwargs(self, models, sp: Split, upd=None):
        """run_grey's keyword arguments for one model or a grid of same-structure models (replicas)."""
        R = len(models)
        m0 = models[0]
        for m in models[1:]:
            for k in ("prior", "comb"):
                assert m[k] == m0[k], k
            for k in ("m5", "sri", "wn", "slip", "kappa"):
                assert (m[k] is None) == (m0[k] is None), k
        fit = self.fit
        if m0["prior"] == "g":
            pr, items = fit["pr1"], fit["it1"]
        elif m0["prior"] == "g0":           # CHANGE 5: M1's prior with the general loading removed
            pr = S.Prior("dense", fit["pr1"].mu, fit["pr1"].D, W=np.zeros_like(fit["pr1"].W))
            items = fit["it1"]
        else:
            pr, items = fit["pr0"], fit["it0"]

        def arr(f):
            v = [f(m) for m in models]
            return float(v[0]) if R == 1 else np.asarray(v, float)
        coefs = []
        for m in models:
            cm = {}
            if m["learn"] is not None:
                cm[("learn", m["learn"][0])] = m["learn"][1]
            if m["mem"] is not None:
                cm[("mem", m["mem"][1])] = m["mem"][0]
            if m["wmem"] is not None:
                cm[("wmem", m["wmem"][1])] = m["wmem"][0]
            if m["m6"] is not None:
                cm[("m6", "lin")] = m["m6"]
            if m["ms"]:
                cm[("ms",)] = m["ms"]
            coefs.append(cm)
        keys = sorted({k for cm in coefs for k in cm}, key=str)
        F = coef = None
        if keys:
            F = np.column_stack([sp.fe.col(k) for k in keys])
            if upd is not None and ("m6", "lin") in keys:
                F = F.copy()
                F[~upd, keys.index(("m6", "lin"))] = self.m6_mean        # no trace after the cut
            coef = np.array([[cm.get(k, 0.0) for k in keys] for cm in coefs])
            if R == 1:
                coef = coef[0]
        comps = []
        if m0["m5"] is not None:
            comps.append({"kind": "static", "sig": arr(lambda m: m["m5"][0]), "loading": sp.fe.x()})
            comps.append({"kind": "static", "sig": arr(lambda m: m["m5"][1]), "loading": sp.fe.forget()})
        if m0["sri"] is not None:
            sc = None if m0["kappa"] is None else (sp.fe.demand, arr(lambda m: m["kappa"]))
            comps.append({"kind": "ar", "rho": 1.0, "tau": arr(lambda m: m["sri"]), "scale": sc, "carry": None})
        if m0["wn"] is not None:
            comps.append({"kind": "ar", "rho": 0.0, "tau": arr(lambda m: m["wn"]), "scale": None, "carry": None})
        return dict(pr=pr, items=items, F=F, coef=coef, spec=comps, q_g=arr(lambda m: m["qg"]), comb=m0["comb"],
                    s_comb=arr(lambda m: m["s"]), nu=arr(lambda m: m["nu"]), shift=arr(lambda m: m["shift"]),
                    slip_tau=None if m0["slip"] is None else arr(lambda m: m["slip"]))

    def grid(self, models, sp: Split):
        """Per-learner TRAIN log likelihood (nl, G) of each model on the fitting sample."""
        out = []
        for s0 in range(0, len(models), CH):
            ch = models[s0:s0 + CH]
            kw = self.kwargs(ch, sp)
            LL = G.run_grey(sp.at, K=self.K, st=sp.st, rep=len(ch), masks=[np.ones(sp.at.n, bool)], **kw)[0]
            out.append(LL)
        return np.concatenate(out, 1)

    def run(self, m, sp: Split, upd=None, record=False):
        kw = self.kwargs([m], sp, upd)
        return G.run_grey(sp.at, K=self.K, st=sp.st, upd=upd, record=record, **kw), kw["items"]


def ident(LL, models, params, nulls, seed):
    """Practical identifiability of each named parameter over a grid: estimate, bootstrap interval of the
    grid argmax (200 learner resamples), profile set (Delta log likelihood >= -1.92) and flags."""
    tot = LL.sum(0)
    best, draws, _ = S2.argmax_boot(LL, seed)
    out = {}
    for name, getter in params.items():
        vals = np.array([float(getter(m)) for m in models])
        uv = np.unique(vals)
        prof = {float(u): float(tot[vals == u].max() - tot[best]) for u in uv}
        pset = [u for u, dv in prof.items() if dv >= -1.92]
        idx = [int(np.nonzero(uv == u)[0][0]) for u in pset]
        bs = vals[draws]
        null = nulls.get(name)
        flags = []
        if max(idx) - min(idx) > 2:
            flags.append("NOT PINNED")
        if null is not None and any(abs(u - null) < 1e-12 for u in pset):
            flags.append("NULL NOT EXCLUDED")
        if vals[best] in (uv[0], uv[-1]) and len(uv) > 1:
            flags.append("AT GRID EDGE")
        out[name] = {"estimate": float(vals[best]), "boot_2.5_50_97.5": [float(x) for x in np.percentile(bs, [2.5, 50, 97.5])],
                     "profile_set": pset, "profile_ll": prof, "flags": flags or ["PINNED"],
                     "estimable": (max(idx) - min(idx) <= 2) and not (null is not None and any(abs(u - null) < 1e-12 for u in pset))}
    out["_ll_best_minus_first"] = float(tot[best] - tot[0])
    return out


# ---------------------------------------------------------------- the base fit (TRAIN)

def refit_grey(at, pr, items, K, group, I, passes=2):
    a, b, c, d, beta = items
    for _ in range(passes):
        o = G.run_grey(at, pr, (a, b, c, d, beta), K)
        a, b, beta, ok = S.fit_items_filter(o["m"], o["v"], at.x, at.i, at.y, np.ones(at.n), c, d, group, I, a, b, beta)
    return a, b, c, d, beta


def base_fit(cp):
    cache = None if cp.synthetic else TMP / f"fit-{cp.name}.pkl"
    data = cp.data
    train = data.rows("train")
    if cache is not None and cache.exists():
        fit = pickle.loads(cache.read_bytes())
        fit["at_tr"] = S.Attempts(data, train)
        log("fitted base read from the scratchpad cache")
        return fit
    K = int(data.df.k.max()) + 1
    asy = C.fit_asymptotes(data, train)
    base = E.engine_params(data.is_mc, data.m).replace(c=asy["c"], d=asy["d"], mode="know", eff="post")
    c0 = C.fit_ab(data.events(train), base, data.group).replace(name="C0")
    at_tr = S.Attempts(data, train)
    a, b, th, beta = S.static_items(at_tr, asy["c"], asy["d"], data.group, data.I, log=lambda *x: None)
    items1 = (a, b, asy["c"], asy["d"], beta)
    cl = S.cells(at_tr, th, a, b, asy["c"], asy["d"], K, beta)
    pr1, _ = S.fit_dense(cl, 1)
    pr0, _ = S.fit_dense(cl, 0)
    del cl
    it1 = refit_grey(at_tr, pr1, items1, K, data.group, data.I)
    it0 = refit_grey(at_tr, pr0, items1, K, data.group, data.I)
    log(f"base fitted: C0; prior r=1 (median lambda {np.median(pr1.W[:, 0]):.2f}) and r=0; practice slope "
        f"{it1[4]:.3f} / {it0[4]:.3f}")
    fit = {"K": K, "c0": c0, "pr1": pr1, "pr0": pr0, "it1": it1, "it0": it0}
    if cache is not None:
        TMP.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(pickle.dumps(fit))
    fit["at_tr"] = at_tr
    return fit


# ---------------------------------------------------------------- evaluation on TEST

class Eval:
    def __init__(self, cp, ctx: Ctx, te: Split, upd, scored, forms=False):
        at = te.at
        self.cp, self.ctx, self.te, self.upd, self.scored = cp, ctx, te, upd, scored
        self.ev = S2.Boot(at.nl, SEED)
        self.win = CP.windows(at)
        self.H = {"ans": np.ones(at.n, bool), "ses": te.st.next_first, "d30": scored}
        self.testable = {"ans": True, "ses": int(self.H["ses"].sum()) >= MIN_H,
                         "d30": int(scored.sum()) >= MIN_H and len(np.unique(at.l[scored])) >= MIN_L30}
        self.extra = {}
        if forms:
            self.extra["ms"] = at.nS > 1
        if "mastery" in te.ext:
            ms_ = np.asarray(te.ext["mastery"]) > 0
            self.extra["mast"], self.extra["nomast"] = ms_, ~ms_
        self.models = {}

    def add(self, name, P, Pf, win_state=None, items=None, beta_rec=None):
        at, ev = self.te.at, self.ev
        y, l, nl = at.y, at.l, at.nl
        ev.add(f"ans|{name}", S2.Mx(P, y, l, nl, self.H["ans"], full=True, risks=RISKS))
        if self.testable["ses"]:
            ev.add(f"ses|{name}", S2.Mx(P, y, l, nl, self.H["ses"], full=True))
        if self.testable["d30"] and Pf is not None:
            ev.add(f"d30|{name}", S2.Mx(Pf, y, l, nl, self.H["d30"], full=True))
        for k, mk in self.extra.items():
            ev.add(f"{k}|{name}", S2.Mx(P, y, l, nl, mk))
        if win_state is not None or beta_rec is not None:
            for wn, idx in self.win.items():
                if not len(idx):
                    continue
                wl = at.l[idx[:, 0]]
                den = np.bincount(wl, None, nl).astype(float)
                if beta_rec is not None:
                    c0 = self.ctx.fit["c0"]
                    u = CP.pit(at, idx, "beta", beta_rec, (c0.a, c0.b, c0.c, c0.d, 0.0))
                else:
                    u = CP.pit(at, idx, "gauss", win_state, items)
                for q in LEVELS:
                    ev.add_sums(f"cov|{wn}|{name}|{q}", np.bincount(wl, (np.abs(u - 0.5) <= q / 2).astype(float), nl), den)

    def model(self, name, m, record=False):
        te = self.te
        o, items = self.ctx.run(m, te, record=record)
        of, _ = self.ctx.run(m, te, upd=self.upd, record=record)
        beta = items[4]
        ws = (o["m"] + o["off"] - beta * te.at.x + o["em"], o["v"])
        self.add(name, o["P"], of["P"], win_state=ws, items=items)
        self.models[name] = describe(m)
        log(f"   TEST {name}: ans {self.ev.pt[f'ans|{name}']['logloss']:.5f}")
        return (o, of) if record else None

    # --- contrasts
    def cov_label(self, name, wn):
        k = f"cov|{wn}|{name}|0.5"
        if k not in self.ev.pt:
            return None, None
        cv = {str(q): self.ev.pt[f"cov|{wn}|{name}|{q}"]["v"] for q in LEVELS}
        dev = [cv[str(q)] - q for q in LEVELS]
        lab = "OVER-CONFIDENT" if min(dev) < -0.05 else "UNDER-CONFIDENT" if max(dev) > 0.05 else "CALIBRATED INTERVALS"
        return cv, lab

    def contrast(self, base, var):
        ev = self.ev
        out = {"base": base, "var": var}
        hs = [h for h in ("ans", "ses", "d30") if self.testable[h]]
        for h in hs:
            out[h] = {"logloss": ev.gain(f"{h}|{base}", f"{h}|{var}"),
                      "auc": ev.gain(f"{h}|{base}", f"{h}|{var}", "auc", -1),
                      "ece_change": ev.gain(f"{h}|{base}", f"{h}|{var}", "ece", -1)}
        out["ans"]["unneeded_per_1000_saved"] = {str(r): ev.gain(f"ans|{base}", f"ans|{var}", f"unneeded_{r}") for r in RISKS}
        for k in self.extra:
            if f"{k}|{base}" in ev.pt and f"{k}|{var}" in ev.pt:
                out[k] = {"logloss": ev.gain(f"{k}|{base}", f"{k}|{var}")}
        lose = any(out[h]["ece_change"]["lo"] > ECE_TOL for h in hs)
        over = {}
        for wn in self.win:
            _, lb = self.cov_label(base, wn)
            _, lv = self.cov_label(var, wn)
            over[wn] = [lb, lv]
            if lv == "OVER-CONFIDENT" and lb != "OVER-CONFIDENT":
                lose = True
        out["intervals"] = over
        out["loses_calibration"] = bool(lose)
        out["horizon_profile"] = [h for h in hs if out[h]["logloss"]["lo"] > 0]
        out["kept"] = bool(all(out[h]["logloss"]["lo"] > 0 for h in hs) and not lose)
        out["detected"] = bool(out["ans"]["logloss"]["lo"] > 0)
        out["one_horizon"] = hs == ["ans"]
        return out

    def drop_cost(self, reduced, full="FULL"):
        """Cost at H1 (and the other horizons) of the reduced model relative to FULL: positive = FULL better."""
        return {h: self.ev.gain(f"{h}|{reduced}", f"{h}|{full}") for h in ("ans", "ses", "d30") if self.testable[h]}


# ---------------------------------------------------------------- the chain on one corpus

def m6_columns(sp: Split, kind):
    cols = T.features(sp.st, sp.at, sp.ext, kind)["H2"] if "hint" in sp.ext else {}
    cols = dict(cols)
    if "ctx" in sp.ext:
        cx = np.asarray(sp.ext["ctx"], float)
        if np.std(cx) > 0:
            cols["ctx"] = cx
    return cols


def run_corpus(cp, synthetic=False, eedi=False):
    data = cp.data
    log(f"{cp.name}: {len(data.df):,} rows, {data.df.attempt.nunique():,} attempts, {len(data.uid):,} learners, "
        f"{data.I:,} items, {int(data.df.k.max()) + 1} skills")
    fit = base_fit(cp)
    K = fit["K"]
    lam = G.lam_of(fit["pr1"])
    rng = np.random.default_rng(SEED + 7)
    first_skill = np.full(data.I, -1)
    dd = data.df.drop_duplicates("i")
    first_skill[dd.i.to_numpy()] = dd.k.to_numpy()
    wmap = G.derange_items(first_skill, rng)
    ctx = Ctx(fit, K)
    te = Split(cp, data, data.rows("test"), lam, wmap)
    at_te = te.at
    # exactness: the grey filter with every option off equals gstate.run_gauss; the Beta copy equals run_beta
    o_ref = G.run_grey(at_te, fit["pr1"], fit["it1"], K, read_decay=False, adf=False)
    err = float(np.abs(o_ref["P"] - S.run_gauss(at_te, fit["pr1"], fit["it1"], K)["P"]).max())
    errb = float(np.abs(G.run_beta_F(at_te, fit["c0"], K)["P"] - S.run_beta(at_te, fit["c0"], K)["P_own"]).max())
    assert err < 1e-9 and errb < 1e-9, (err, errb)
    del o_ref
    uid = np.asarray(data.uid)
    keep = np.array([S2.hsh(u, 4, "gsrank") == 0 for u in uid])
    mm = 1
    while True:
        k2 = keep & np.array([S2.hsh(u, mm, "s2fit") == 0 for u in uid]) if mm > 1 else keep
        if k2[fit["at_tr"].learners][fit["at_tr"].l].sum() <= S2.FIT_CAP:
            break
        mm *= 2
    fs = Split(cp, data, data.rows("train") & k2[data.df.l.to_numpy()], lam, wmap)
    upd, scored = G.cut_mask(at_te)
    forms = not synthetic
    ev = Eval(cp, ctx, te, upd, scored, forms=forms)
    res = {"data": {"rows": int(len(data.df)), "attempts": int(data.df.attempt.nunique()), "learners": int(len(data.uid)),
                    "items": int(data.I), "skills": K, "test_attempts": int(at_te.n), "test_learners": int(at_te.nl),
                    "fitting_sample_attempts": int(fs.at.n), "fitting_sample_learners": int(fs.at.nl),
                    "ses_first_attempts": int(ev.H["ses"].sum()), "d30_scored": int(scored.sum()),
                    "d30_learners": int(len(np.unique(at_te.l[scored]))),
                    "repeat_item_test_attempts": int((te.st.item_count > 0).sum()),
                    "multi_skill_test_attempts": int((at_te.nS > 1).sum())},
           "exactness": {"run_grey_vs_run_gauss": err, "run_beta_F_vs_run_beta": errb}, "testable_horizons": ev.testable,
           "fit": {}, "ident": {}}
    log(f"TEST {at_te.n:,} attempts / {at_te.nl:,} learners; fitting sample {fs.at.n:,}; horizons {ev.testable}; "
        f"exact {err:.1e} {errb:.1e}")
    fitd, idn = res["fit"], res["ident"]
    sd = [SEED + 100]

    def gfit(name, models, params, nulls):
        LL = ctx.grid(models, fs)
        sd[0] += 1
        idn[name] = ident(LL, models, params, nulls, sd[0])
        best = models[int(np.argmax(LL.sum(0)))]
        fitd[name] = describe(best)
        fitd[name + "_train_ll"] = float(LL.sum(0).max())
        log(f"   grid {name}: {len(models)} points; best {describe(best)}")
        return best, float(LL.sum(0).max())

    # ---- M0, M0-G, M1, M1-engine
    c0 = fit["c0"]
    ob = G.run_beta_F(at_te, c0, K)
    obf = G.run_beta_F(at_te, c0, K, upd=upd)
    ev.add("M0", ob["P"], obf["P"], beta_rec=(ob["alpha"], ob["beta"]))
    ev.add("CLIM", S2.clim(data, at_te), S2.clim(data, at_te))
    M0G = spec(prior="0")
    M1 = spec()
    ev.model("M0-G", M0G)
    o1, o1f = ev.model("M1", M1, record=True)
    if not synthetic:
        res["M1_engine"] = m1_engine(cp, fit, ctx, ev, o1, o1f)
    res["g_halves"] = g_drift(at_te, fit)
    # ---- g dynamics (competitors to M1)
    drift_models = [w_(M1, qg=q) for q in QG]
    best_drift, ll_drift = gfit("M1-drift", drift_models, {"qg": lambda m: m["qg"]}, {})
    learn_models = [w_(M1, learn=(f, g_)) for f in ("lin", "load") for g_ in G_100] + [w_(M1, learn=("log", g_)) for g_ in G_LOG]
    best_learn, ll_learn = gfit("M1-learn", learn_models, {"gamma": lambda m: m["learn"][1]}, {"gamma": 0.0})
    fitd["M1-learn_form"] = best_learn["learn"][0]
    lf = best_learn["learn"][0]
    learn_form_models = [m for m in learn_models if m["learn"][0] == lf]
    ev.model("M1-drift", best_drift)
    ev.model("M1-learn", best_learn)
    gdyn = ("drift", best_drift) if ll_drift >= ll_learn else ("learn", best_learn)
    fitd["g_dynamics_in_FULL"] = gdyn[0]
    # ---- M2 item memory
    mem_ok = res["data"]["repeat_item_test_attempts"] >= MIN_REPEAT
    res["testable_components"] = {"M2": mem_ok, "M3'": not eedi, "M5": not eedi, "WN": not eedi,
                                  "M6": bool(m6_columns(te, cp.name))}
    run = M1
    if mem_ok:
        mem_models = [w_(M1, mem=(al, ta)) for al in ALPHA for ta in TAU_M]
        M2, _ = gfit("M2", mem_models, {"alpha": lambda m: m["mem"][0], "tau_m": lambda m: m["mem"][1]}, {})
        ev.model("M2", M2)
        run = M2
    else:
        M2 = None
    if eedi:
        FULL = w_(run, **({"qg": gdyn[1]["qg"]} if gdyn[0] == "drift" else {"learn": gdyn[1]["learn"]}))
        ev.model("FULL", FULL)
        fitd["FULL"] = describe(FULL)
        loo = {"g": spec(prior="0", mem=FULL["mem"]), "gdyn": w_(FULL, qg=0.0, learn=None)}
        if M2 is not None:
            loo["M2"] = w_(FULL, mem=None)
        for c_, m_ in loo.items():
            ev.model(f"LOO-{c_}", m_)
        if forms:
            res["forms"] = run_forms(ctx, ev, fs, gfit, M1, te)
        return finish(res, ev, eedi=True)
    # ---- WN, M3', its forms, M5, M6
    M2WN, _ = gfit("WN", [w_(run, wn=t) for t in TAU_W], {"tau_w": lambda m: m["wn"]}, {})
    ev.model("M2+WN", M2WN)
    M3, _ = gfit("M3'", [w_(M2WN, sri=t) for t in TAU_S], {"tau_s": lambda m: m["sri"]}, {})
    ev.model("M3'", M3)
    if forms:
        res["session_forms"] = {}
        if cp.demand is not None:
            M3d, _ = gfit("M3'-demand", [w_(M3, kappa=k) for k in KAPPA], {"kappa": lambda m: m["kappa"]}, {"kappa": 0.0})
            ev.model("M3'-demand", M3d)
        M3s, _ = gfit("M3'-slip", [w_(M2WN, slip=t) for t in TAU_S], {"tau_d": lambda m: m["slip"]}, {})
        ev.model("M3'-slip", M3s)
    M5, _ = gfit("M5", [w_(M3, m5=(sb, sf)) for sb in SIG_B for sf in SIG_F],
                 {"sigma_b": lambda m: m["m5"][0], "sigma_f": lambda m: m["m5"][1]}, {"sigma_b": 0.0, "sigma_f": 0.0})
    ev.model("M5", M5)
    has6 = res["testable_components"]["M6"]
    if has6:
        M6 = fit_m6(ctx, cp, fit, M5, te, fs, res, gfit)
        ev.model("M6", M6)
    else:
        M6 = M5
    # ---- FULL and the leave-one-out ablations
    FULL = w_(M6, **({"qg": gdyn[1]["qg"]} if gdyn[0] == "drift" else {"learn": gdyn[1]["learn"]}))
    ev.model("FULL", FULL)
    fitd["FULL"] = describe(FULL)

    def refit(base, param):
        if param == "sri":
            return gfit("refit-sri", [w_(base, sri=t) for t in TAU_S], {"tau_s": lambda m: m["sri"]}, {})[0]
        if param == "wn":
            return gfit("refit-wn", [w_(base, wn=t) for t in TAU_W], {"tau_w": lambda m: m["wn"]}, {})[0]
        if param == "m6" and has6:
            return gfit("refit-m6", [w_(base, m6=z) for z in ZETA], {"zeta": lambda m: m["m6"]}, {})[0]
        if param == "m5":
            return gfit("refit-m5", [w_(base, m5=(sb, sf)) for sb in SIG_B for sf in SIG_F],
                        {"sigma_b": lambda m: m["m5"][0], "sigma_f": lambda m: m["m5"][1]}, {})[0]
        if param == "gdyn":
            if gdyn[0] == "drift":
                return gfit("refit-gdyn", [w_(base, qg=q) for q in QG], {"qg": lambda m: m["qg"]}, {})[0]
            return gfit("refit-gdyn", [w_(base, learn=m["learn"]) for m in learn_form_models],
                        {"gamma": lambda m: m["learn"][1]}, {})[0]
        return base
    nog = w_(FULL, prior="g0", qg=0.0, learn=None)
    loo = {"g": refit(nog, "sri"),
           "gdyn": refit(w_(FULL, qg=0.0, learn=None), "m5"),
           "WN": refit(w_(FULL, wn=None), "sri"),
           "M3'": refit(refit(w_(FULL, sri=None), "wn"), "m6"),
           "M5": refit(w_(FULL, m5=None), "gdyn")}
    if M2 is not None:
        loo["M2"] = w_(FULL, mem=None)
    if has6:
        loo["M6"] = refit(w_(FULL, m6=None), "sri")
    for c_, m_ in loo.items():
        ev.model(f"LOO-{c_}", m_)
        fitd[f"LOO-{c_}"] = describe(m_)
    pairs = {"g+M3'": w_(nog, sri=None), "M3'+WN": w_(FULL, sri=None, wn=None),
             "gdyn+M5": w_(FULL, qg=0.0, learn=None, m5=None)}
    if has6:
        pairs["M3'+M6"] = w_(FULL, sri=None, m6=None)
    for c_, m_ in pairs.items():
        ev.model(f"PAIR-{c_}", m_)
    ev.model("BLOCK-FAST", w_(FULL, mem=None, wn=None, sri=None, m6=None))
    ev.model("BLOCK-LEARNER", w_(FULL, qg=0.0, learn=None, m5=None))
    # ---- the misspecification challenge
    if M2 is not None:
        flex = refit(refit(w_(M1, wn=M2WN["wn"]), "sri"), "m5")
        ev.model("FLEX", flex)
        fw, _ = gfit("FLEX+wrong", [w_(flex, wmem=(al, ta)) for al in ALPHA for ta in TAU_M],
                     {"alpha": lambda m: m["wmem"][0], "tau_m": lambda m: m["wmem"][1]}, {})
        fr, _ = gfit("FLEX+right", [w_(flex, mem=(al, ta)) for al in ALPHA for ta in TAU_M],
                     {"alpha": lambda m: m["mem"][0], "tau_m": lambda m: m["mem"][1]}, {})
        ev.model("FLEX+wrong", fw)
        ev.model("FLEX+right", fr)
        fitd["FLEX"] = describe(flex)
    if forms:
        res["forms"] = run_forms(ctx, ev, fs, gfit, M1, te)
    return finish(res, ev, eedi=False, has6=has6, mem=M2 is not None)


def fit_m6(ctx, cp, fit, M5, te, fs, res, gfit):
    """Two-stage: coefficients by penalised Fisher scoring on M5's TRAIN state, then the scale zeta."""
    data = cp.data
    tr = Split(cp, data, data.rows("train"), te.fe.lam, te.fe.wmap)
    cols_tr = m6_columns(tr, cp.name)
    names = list(cols_tr)
    o, items = ctx.run(M5, tr)
    a, b, c, d, beta = items
    it = tr.at.i
    Ftr = np.column_stack([cols_tr[k] for k in names])
    gam = T.fit_offset(Ftr, o["m"] + o["off"] + o["em"], o["v"], a[it], b[it], c[it], d[it], tr.at.y)
    res["fit"]["M6_coefficients"] = dict(zip(names, [float(x) for x in gam]))
    ctx.m6_mean = float((Ftr @ gam).mean())
    for sp in (te, fs):
        cs = m6_columns(sp, cp.name)
        sp.fe.m6_cols = {"lin": np.column_stack([cs.get(k, np.zeros(sp.at.n)) for k in names]) @ gam}
    del tr, Ftr, o
    gc.collect()
    M6, _ = gfit("M6", [w_(M5, m6=z) for z in ZETA], {"zeta": lambda m: m["m6"]}, {"zeta": 0.0})
    return M6


def run_forms(ctx, ev, fs, gfit, M1, te):
    out = {}
    comp, _ = gfit("comb-comp", [w_(M1, ms=x) for x in MS_SHIFT], {"ms": lambda m: m["ms"]}, {})
    ev.model("COMB-comp", comp)
    for kind in ("conj", "disj"):
        best, _ = gfit(f"comb-{kind}", [w_(M1, comb=kind, s=s_, ms=x) for s_ in S_COMB for x in MS_SHIFT],
                       {"s": lambda m: m["s"], "ms": lambda m: m["ms"]}, {})
        ev.model(f"COMB-{kind}", best)
    lk, _ = gfit("link", [w_(M1, nu=n_, shift=s_) for n_ in NU for s_ in SHIFT],
                 {"nu": lambda m: m["nu"], "shift": lambda m: m["shift"]}, {})
    ev.model("LINK-nl", lk)
    return out


def m1_engine(cp, fit, ctx, ev: Eval, o1, o1f):
    """S2's A1 on the engine's Beta with M1's g-tracker: mu_k, lambda_k on TRAIN first attempts, n0 on the
    TRAIN validation quarter."""
    data, K, c0 = cp.data, fit["K"], fit["c0"]
    at_tr = fit["at_tr"]
    otr = G.run_grey(at_tr, fit["pr1"], fit["it1"], K, record=True)
    rows, cols, k, Rr = S2.slot_rows(at_tr)
    cold = Rr == 0
    g_att = otr["g"][rows]
    mk, lk, w = S2.fit_map(g_att[cold], at_tr.i[rows][cold], k[cold], at_tr.y[rows][cold], c0, K, True)

    def p0(at, gvec):
        r_, c_, k_, _ = S2.slot_rows(at)
        P = np.full(at.S.shape, 0.5)
        P[r_, c_] = T.sigmoid(mk[k_] + lk[k_] * gvec[r_])
        return S2.first_touch_P0(at, P)
    P0_tr = p0(at_tr, otr["g"])
    uid = np.asarray(data.uid)
    val = np.array([S2.hsh(u, 4, "gsrank") == 0 for u in uid])
    sel_rows = val[at_tr.learners][at_tr.l]
    at_val = S.Attempts(data, data.rows("train") & val[data.df.l.to_numpy()])
    assert np.array_equal(at_val.gid, at_tr.gid[sel_rows])
    sc = {}
    for x in N0_GRID:
        Pv = np.clip(G.run_beta_F(at_val, c0, K, P0_tr[sel_rows], x)["P"], 1e-9, 1 - 1e-9)
        sc[x] = float(-(at_val.y * np.log(Pv) + (1 - at_val.y) * np.log1p(-Pv)).mean())
    n0 = min(sc, key=sc.get)
    at = ev.te.at
    oa = G.run_beta_F(at, c0, K, p0(at, o1["g"]), n0)
    of = G.run_beta_F(at, c0, K, p0(at, o1f["g"]), n0, upd=ev.upd)
    ev.add("M1-engine", oa["P"], of["P"], beta_rec=(oa["alpha"], oa["beta"]))
    log(f"   TEST M1-engine (A1 on the Beta, n0 = {n0}): ans {ev.ev.pt['ans|M1-engine']['logloss']:.5f}")
    return {"n0": n0, "n0_val_logloss": sc, "map_global": [float(x) for x in w], "lambda_k_median": float(np.median(lk))}


def g_drift(at, fit, B=200):
    g1, g2, n_l, _ = G.g_halves(at, fit["pr1"], fit["it1"])
    if len(g1) < 30:
        return {"learners": int(len(g1))}
    dg = g2 - g1
    x = np.log1p(n_l)
    rng = np.random.default_rng(SEED + 9)

    def slope(i):
        xx, yy = x[i], dg[i]
        return float(np.polyfit(xx, yy, 1)[0]) if np.std(xx) > 0 else float("nan")
    allix = np.arange(len(dg))
    bs = [slope(rng.integers(0, len(dg), len(dg))) for _ in range(B)]
    mb = [float(dg[rng.integers(0, len(dg), len(dg))].mean()) for _ in range(B)]
    return {"learners": int(len(dg)), "mean_delta_g": float(dg.mean()), "mean_delta_g_ci": [float(v) for v in np.percentile(mb, [2.5, 97.5])],
            "slope_on_log_volume": slope(allix), "slope_ci": [float(v) for v in np.nanpercentile(bs, [2.5, 97.5])],
            "corr": float(np.corrcoef(x, dg)[0, 1]), "sd_delta_g": float(dg.std())}


# ---------------------------------------------------------------- verdicts on one corpus

def boot_share(ev, chain, H="ans", k="brier"):
    """Each forward step's share of the reduction from chain[0] to chain[-1], with bootstrap intervals."""
    p, d = ev.ev.pt, ev.ev.dr
    tot_p = p[f"{H}|{chain[0]}"][k] - p[f"{H}|{chain[-1]}"][k]
    tot_d = np.array([a[k] - b[k] for a, b in zip(d[f"{H}|{chain[0]}"], d[f"{H}|{chain[-1]}"])])
    out = {"total": {"est": float(tot_p), "lo": float(np.percentile(tot_d, 2.5)), "hi": float(np.percentile(tot_d, 97.5))}}
    for a_, b_ in zip(chain[:-1], chain[1:]):
        st = (p[f"{H}|{a_}"][k] - p[f"{H}|{b_}"][k]) / tot_p
        dd = np.array([(x[k] - y[k]) / t for x, y, t in zip(d[f"{H}|{a_}"], d[f"{H}|{b_}"], tot_d)])
        out[f"{a_} -> {b_}"] = {"est": float(st), "lo": float(np.percentile(dd, 2.5)), "hi": float(np.percentile(dd, 97.5))}
    return out


def est_of(res, grid, params):
    idn = res["ident"].get(grid, {})
    ok = [idn[p]["estimable"] for p in params if p in idn]
    return {"estimable": bool(ok) and all(ok), "params": {p: idn[p] for p in params if p in idn}}


def finish(res, ev: Eval, eedi=False, has6=False, mem=True):
    pt = ev.ev.pt
    have = lambda nm: f"ans|{nm}" in pt  # noqa: E731
    Cn = {}
    pairs = [("g_vs_M0", "M0", "M1"), ("g_vs_M0-G", "M0-G", "M1"), ("M0-G_vs_M0", "M0", "M0-G"),
             ("drift", "M1", "M1-drift"), ("learn", "M1", "M1-learn"), ("learn_to_drift", "M1-learn", "M1-drift"),
             ("M1-engine_vs_M0", "M0", "M1-engine"), ("M1_vs_M1-engine", "M1-engine", "M1"),
             ("M2", "M1", "M2"), ("WN", "M2" if mem else "M1", "M2+WN"), ("M3'", "M2+WN", "M3'"),
             ("M3'-demand_vs_M3'", "M3'", "M3'-demand"), ("M3'-slip_vs_M3'", "M3'", "M3'-slip"),
             ("M3'-slip_vs_M2+WN", "M2+WN", "M3'-slip"), ("M5", "M3'", "M5"), ("M6", "M5", "M6"),
             ("FULL_vs_M0", "M0", "FULL"),
             ("misspec_wrong", "FLEX", "FLEX+wrong"), ("misspec_right", "FLEX", "FLEX+right"),
             ("misspec_right_over_wrong", "FLEX+wrong", "FLEX+right"),
             ("link_nl", "M1", "LINK-nl"), ("comb_conj_vs_comp", "COMB-comp", "COMB-conj"),
             ("comb_disj_vs_comp", "COMB-comp", "COMB-disj"), ("comb_disj_vs_conj", "COMB-conj", "COMB-disj")]
    for nm, a_, b_ in pairs:
        if have(a_) and have(b_):
            Cn[nm] = ev.contrast(a_, b_)
    res["contrasts"] = Cn
    drops = {}
    for nm in [k.split("|", 1)[1] for k in pt if k.startswith("ans|") and k.split("|", 1)[1].startswith(("LOO-", "PAIR-", "BLOCK-"))]:
        drops[nm] = ev.drop_cost(nm)
    res["drop_costs"] = drops
    res["models"] = ev.models
    res["point"] = {k: v for k, v in pt.items() if not k.startswith("cov|")}
    res["intervals"] = {nm: {wn: ev.cov_label(nm, wn) for wn in ev.win} for nm in
                        sorted({k.split("|")[2] for k in pt if k.startswith("cov|")})}

    def lo(nm):
        return drops.get(nm, {}).get("ans", {"lo": float("nan")})["lo"]
    st = {}

    def status(c, kept, detected, loo_nm, partners, profile, estim):
        loo = bool(lo(loo_nm) > 0) if loo_nm in drops else None
        pair_hit = [p for p in partners if lo(f"PAIR-{p}") > 0]
        nd = bool(loo is False and len(pair_hit) > 0)
        single = ("KEPT AND LOO" if kept and loo else "NOT DISCRIMINABLE" if kept and nd else
                  "KEPT, LOO NOT POSITIVE" if kept else "DETECTED ONLY" if detected else "NOT KEPT")
        if c == "g" and not kept and nd:
            single = "NOT DISCRIMINABLE"
        if c == "g" and nd:
            single = "NOT DISCRIMINABLE"
        st[c] = {"kept": bool(kept), "detected": bool(detected), "loo": loo, "not_discriminable": nd,
                 "pair_blocks_costing": pair_hit, "single": single, "horizon_profile": profile, "estimability": estim}
    g1, g2 = Cn["g_vs_M0"], Cn["g_vs_M0-G"]
    status("g", g1["kept"] and g2["kept"], g1["detected"] and g2["detected"], "LOO-g", ["g+M3'"],
           sorted(set(g1["horizon_profile"]) & set(g2["horizon_profile"])), {"estimable": None, "note": "EM prior"})
    gd = res["fit"]["g_dynamics_in_FULL"]
    for c, key, grid, par in (("drift", "drift", "M1-drift", ["qg"]), ("learn", "learn", "M1-learn", ["gamma"])):
        status(c, Cn[key]["kept"], Cn[key]["detected"], "LOO-gdyn" if gd == c else "_", ["gdyn+M5"] if gd == c else [],
               Cn[key]["horizon_profile"], est_of(res, grid, par))
    gam = res["ident"]["M1-learn"]["gamma"]["estimate"]
    st["learn"]["gamma_hat"] = gam
    kd, kl = st["drift"]["kept"], st["learn"]["kept"]
    if not kd and not kl:
        gv = "G STATIC ADEQUATE"
    elif kd and kl:
        h = "d30" if ev.testable["d30"] else "ans"
        dl = Cn["learn_to_drift"][h]["logloss"]
        gv = ("G DRIFTS (OBSERVATIONAL)" if dl["lo"] > 0 else
              ("G MOVES WITH PRACTICE (OBSERVATIONAL)" if gam > 0 else "G FALLS WITH PRACTICE (OBSERVATIONAL)") if dl["hi"] < 0
              else "G DYNAMICS UNIDENTIFIED")
    elif kd:
        gv = "G DRIFTS (OBSERVATIONAL)"
    else:
        gv = "G MOVES WITH PRACTICE (OBSERVATIONAL)" if gam > 0 else "G FALLS WITH PRACTICE (OBSERVATIONAL)"
    res["g_dynamics_verdict"] = gv
    if "M2" in Cn:
        status("M2", Cn["M2"]["kept"], Cn["M2"]["detected"], "LOO-M2", [], Cn["M2"]["horizon_profile"],
               est_of(res, "M2", ["alpha", "tau_m"]))
        st["M2"]["alpha_hat"] = res["ident"]["M2"]["alpha"]["estimate"]
    if not eedi:
        status("WN", Cn["WN"]["kept"], Cn["WN"]["detected"], "LOO-WN", ["M3'+WN"], Cn["WN"]["horizon_profile"],
               est_of(res, "WN", ["tau_w"]))
        status("M3'", Cn["M3'"]["kept"], Cn["M3'"]["detected"], "LOO-M3'", ["g+M3'", "M3'+WN"] + (["M3'+M6"] if has6 else []),
               Cn["M3'"]["horizon_profile"], est_of(res, "M3'", ["tau_s"]))
        status("M5", Cn["M5"]["kept"], Cn["M5"]["detected"], "LOO-M5", ["gdyn+M5"], Cn["M5"]["horizon_profile"],
               est_of(res, "M5", ["sigma_b", "sigma_f"]))
        if has6:
            status("M6", Cn["M6"]["kept"], Cn["M6"]["detected"], "LOO-M6", ["M3'+M6"], Cn["M6"]["horizon_profile"],
                   est_of(res, "M6", ["zeta"]))
    res["status"] = st
    if "misspec_right" in Cn:
        w, r, rw = Cn["misspec_wrong"]["ans"]["logloss"], Cn["misspec_right"]["ans"]["logloss"], \
            Cn["misspec_right_over_wrong"]["ans"]["logloss"]
        res["misspec_verdict"] = ("NOT DIAGNOSTIC" if r["lo"] <= 0 else "WRONG MECHANISM CREDITED" if w["lo"] > 0 else
                                  "WRONG MECHANISM REJECTED" if rw["lo"] > 0 else "NOT DIAGNOSTIC")
        res["misspec_share_recovered_by_wrong"] = float(w["est"] / r["est"]) if r["est"] > 0 else None
        res["misspec_right_beats_wrong"] = bool(rw["lo"] > 0)
    chain = [m for m in ("CLIM", "M0-G", "M1", "M2", "M2+WN", "M3'", "M5", "M6", "FULL") if have(m)]
    res["forward_shares_brier_ans"] = boot_share(ev, chain)
    res["forward_shares_logloss_ans"] = boot_share(ev, chain, k="logloss")
    if "comb_conj_vs_comp" in Cn:
        res["form_verdicts"] = form_verdicts(Cn, res)
    log(f"== status: { {c: s['single'] for c, s in st.items()} }; g dynamics: {gv}; misspec: {res.get('misspec_verdict')}")
    return res


def form_verdicts(Cn, res):
    out = {}
    if res["data"]["multi_skill_test_attempts"] >= MIN_MS and "ms" in Cn["comb_conj_vs_comp"]:
        g = {("conj", "comp"): Cn["comb_conj_vs_comp"]["ms"]["logloss"], ("disj", "comp"): Cn["comb_disj_vs_comp"]["ms"]["logloss"],
             ("disj", "conj"): Cn["comb_disj_vs_conj"]["ms"]["logloss"]}

        def beats(x, y):
            if (x, y) in g:
                return g[(x, y)]["lo"] > 0
            return g[(y, x)]["hi"] < 0
        win = [f for f in ("comp", "conj", "disj") if all(beats(f, o) for o in ("comp", "conj", "disj") if o != f)]
        out["combination"] = f"{ {'comp': 'COMPENSATORY', 'conj': 'CONJUNCTIVE', 'disj': 'DISJUNCTIVE'}[win[0]]} SUPPORTED" if win \
            else "COMBINATION UNIDENTIFIED"
    else:
        out["combination"] = "NOT TESTABLE"
    lnk = Cn["link_nl"]["ans"]["logloss"]
    out["link"] = ("NON-LINEAR LINK SUPPORTED" if lnk["lo"] > 0 and not Cn["link_nl"]["loses_calibration"] else
                   "LINEAR LINK SUPPORTED" if lnk["hi"] < 0 else "LINK UNIDENTIFIED")
    if "M3'-slip_vs_M3'" in Cn:
        sl = Cn["M3'-slip_vs_M3'"]["ans"]["logloss"]
        dm = Cn.get("M3'-demand_vs_M3'", {}).get("ans", {}).get("logloss")
        if dm is not None:
            out["session_shift_demand"] = ("DEMAND-SCALED SUPPORTED" if dm["lo"] > 0 else "ADDITIVE SUPPORTED OVER DEMAND"
                                           if dm["hi"] < 0 else "DEMAND FORM UNIDENTIFIED")
        else:
            out["session_shift_demand"] = "NOT TESTABLE (no ratings)"
        out["session_shift_slip"] = ("SLIP-ASYMPTOTE SUPPORTED" if sl["lo"] > 0 else "ADDITIVE SUPPORTED OVER SLIP"
                                     if sl["hi"] < 0 else "SLIP FORM UNIDENTIFIED")
    return out


# ---------------------------------------------------------------- synthetic worlds (M5 itself)

WORLDS = {"W1": dict(m2=1, m5=1, m6=1), "W2": dict(m2=1, m5=1, m6=1, m3=1), "W3": dict(), "W4": dict(drift=1),
          "W5": dict(learn=1), "W7": dict(ctx=1), "W8": dict(single=1, lam1=1)}
PLANT = {"W1": {"g", "M2", "M5", "M6"}, "W2": {"g", "M2", "M5", "M6", "M3'"}, "W3": {"g"}, "W4": {"g", "drift"},
         "W5": {"g", "learn"}, "W7": {"g", "M6"}, "W8": {"g"}}
Q_DRIFT, G_LEARN, A_MEM, T_MEM, T_SES, E_HINT, E_CTX = 0.003, 0.10, 1.0, 24.0, 0.5, 0.6, -0.6
R_GAIN, SB_TRUE, SF_TRUE = 0.3, 0.15, 0.1          # CHANGE 1: gain rate log(1 + n), per-learner deviations


def world(kind, seed, L=2000):
    f = WORLDS[kind]
    rng = np.random.default_rng(seed * 10 + list(WORLDS).index(kind))
    K, per = 30, 12
    I = K * per
    skill_of = np.repeat(np.arange(K), per)
    b = rng.normal(-0.6, 0.6, K)[skill_of] + rng.normal(0, 0.7, I)
    a = np.exp(rng.normal(0, 0.25, I))
    is_mc = rng.random(I) < 0.5
    c = np.where(is_mc, rng.uniform(0.1, 0.3, I), rng.uniform(0.02, 0.08, I))
    dd = 1 - rng.uniform(0, 0.04, I)
    lam = np.ones(K) if f.get("lam1") else rng.normal(0.85, 0.1, K)
    items_of = [np.nonzero(skill_of == k)[0] for k in range(K)]
    rows = {k_: [] for k_ in ("u", "i", "k", "y", "t", "o", "hint", "ctx")}
    aid = 0
    for u in range(L):
        g = rng.normal()
        u0 = rng.normal(0, math.sqrt(0.48), K)
        if f.get("m5"):
            rate, phi = R_GAIN + rng.normal(0, SB_TRUE), rng.normal(0, SF_TRUE)
        else:
            rate, phi = R_GAIN, 0.0
        nk = np.zeros(K)
        last = np.full(K, -1.0)
        seen_t = {}
        order = rng.permutation(K)
        nxt, seen = 0, []
        t, tprev, nprac = 0.0, None, 0

        def pick():
            nonlocal nxt
            if nxt < K and (not seen or rng.random() < 0.6):
                k = int(order[nxt])
                nxt += 1
                seen.append(k)
                return k
            return int(rng.choice(seen))
        if f.get("single"):
            natt = int(rng.integers(60, 151))
            runs = []
            while len(runs) < natt:
                runs += [pick()] * int(rng.integers(6, 13))
            sessions = [runs[:natt]]
        else:
            sessions = []
            for _ in range(int(rng.integers(18, 31))):
                sk = [pick() for _ in range(int(rng.integers(1, 3)))]
                natt = int(rng.integers(8, 17))
                sessions.append([sk[0]] * (natt if len(sk) == 1 else natt // 2) + ([sk[1]] * (natt - natt // 2) if len(sk) > 1 else []))
        for runs in sessions:
            t += math.exp(rng.uniform(math.log(2 * 3600), math.log(20 * 86400)))
            dl = rng.normal(0, T_SES) if f.get("m3") else 0.0
            cx = int(rng.random() < 0.3) if f.get("ctx") else 0
            prev_i, y_prev, hint_prev = None, None, 0
            tt = t
            for k in runs:
                if prev_i is not None and skill_of[prev_i] == k and rng.random() < 0.25:
                    i = prev_i
                else:
                    i = int(rng.choice(items_of[k]))
                tt += rng.uniform(20, 120)
                if f.get("drift") and tprev is not None:
                    g += rng.normal(0, math.sqrt(Q_DRIFT * (tt - tprev) / 86400))
                tprev = tt
                fg = -phi * math.log1p((tt - last[k]) / 86400) if last[k] >= 0 else 0.0
                ge = g + (G_LEARN * math.log1p(nprac) if f.get("learn") else 0.0)
                te = lam[k] * ge + u0[k] + rate * math.log1p(nk[k]) + fg + dl + E_CTX * cx + (E_HINT if f.get("m6") and hint_prev else 0.0)
                if f.get("m2") and i in seen_t:
                    te += A_MEM * math.exp(-(tt - seen_t[i]) / 3600 / T_MEM)
                P = c[i] + (dd[i] - c[i]) / (1 + math.exp(-a[i] * (te - b[i])))
                yv = int(rng.random() < P)
                hv = int(rng.random() < 0.10 + 0.30 * (0 if y_prev is None else 1 - y_prev))
                nk[k] += 1
                last[k] = tt
                seen_t[i] = tt
                nprac += 1
                for key, val in zip(rows, (u, i, k, yv, tt, aid, hv, cx)):
                    rows[key].append(val)
                aid += 1
                prev_i, y_prev, hint_prev = i, yv, hv
    ar = {k_: np.asarray(v_) for k_, v_ in rows.items()}
    group = np.where(is_mc, 0, 1)
    data = C.Data(ar["u"], ar["i"], ar["k"], ar["y"].astype(float), ar["t"], ar["o"], is_mc, np.where(is_mc, 4, 0), group,
                  np.array([f"gb{kind}{seed}-{u}" for u in range(L)]))
    ext = {"hint": ar["hint"].astype(float), "ctx": ar["ctx"].astype(float)}
    cp = S2.Corpus(f"world {kind} seed {seed}", data, ext, demand=None, batch=False, rank=1, synthetic=True)
    cp.truth = {"lam": lam, "a": a, "b": b, "c": c, "d": dd, "rate": R_GAIN, "Du": 0.48}
    return cp


def floor_checks(kind, res):
    st = res["status"]
    pl = PLANT[kind]
    ck = {}
    for c in ("g", "drift", "learn", "M2", "M3'", "M5", "M6"):
        s = st.get(c)
        if s is None:
            continue
        both = s["kept"] and bool(s["loo"])
        planted = c in pl
        if c == "g":
            ck["KEEP_g"] = s["kept"] if kind == "W8" else both              # CHANGE 6: W8's check is ND
        elif c in ("drift", "learn"):
            ck[f"KEEP_{c}"] = s["kept"] == planted and (not planted or s["loo"] is not False)
            if c == "learn" and planted:
                ck["KEEP_learn"] = ck["KEEP_learn"] and s.get("gamma_hat", 0) > 0
        elif c == "M3'":
            ck["KEEP_M3'"] = both if kind == "W2" else (not both) if kind in ("W7", "W8") else not s["kept"]
        elif c == "M6":
            ck["KEEP_M6"] = both if kind in ("W1", "W2") else True if kind == "W7" else not s["kept"]
            if kind == "W7":
                ck["DETECT_M6"] = s["detected"]
        else:
            ck[f"KEEP_{c}"] = both if planted else not s["kept"]
        if not (kind == "W7" and c in ("M3'", "M6")):
            ck[f"DETECT_{c}"] = s["detected"] == planted
    if kind in ("W1", "W2", "W3", "W7"):
        ck["KEEP_gdyn_verdict"] = res["g_dynamics_verdict"] == "G STATIC ADEQUATE"
    if kind in ("W1", "W2") and "misspec_right_beats_wrong" in res:
        ck["MISSPEC_right_beats_wrong"] = res["misspec_right_beats_wrong"]
    if kind == "W8":
        ck["ND_g_not_discriminable"] = st["g"]["single"] == "NOT DISCRIMINABLE"
    return ck


def approx_check(cp, res):
    """W3: the exact grid filter under the true model against M1 and FULL at H1 (learner bootstrap)."""
    data = cp.data
    fit = base_fit(cp)
    K = fit["K"]
    at = S.Attempts(data, data.rows("test"))
    Pg = G.grid_filter(at, cp.truth)
    o = G.run_grey(at, fit["pr1"], fit["it1"], K)
    y = at.y

    def ll(P):
        P = np.clip(P, 1e-9, 1 - 1e-9)
        return -(y * np.log(P) + (1 - y) * np.log1p(-P))
    d = ll(o["P"]) - ll(Pg)
    nl = at.nl
    sums, n = np.bincount(at.l, d, nl), np.bincount(at.l, None, nl)
    rng = np.random.default_rng(SEED + 3)
    bs = []
    for _ in range(200):
        w = np.bincount(rng.integers(0, nl, nl), minlength=nl)
        bs.append(float(w @ sums / (w @ n)))
    return {"M1_minus_exact_nats": float(d.mean()), "ci": [float(x) for x in np.percentile(bs, [2.5, 97.5])],
            "exact_logloss": float(ll(Pg).mean()), "M1_logloss": float(ll(o["P"]).mean()), "test_attempts": int(at.n),
            "flag": bool(d.mean() > 0.01)}


FLOOR = [(k, s) for k in WORLDS for s in FLOOR_SEEDS]


def synthetic(which=None, tag="all", L=2000):
    TMP.mkdir(parents=True, exist_ok=True)
    f = TMP / f"floor-{tag}.json"
    out = json.loads(f.read_text()) if f.exists() else {"worlds": []}
    done = {(w["world"], w["seed"]) for w in out["worlds"]}
    for kind, sd in FLOOR:
        if which and kind not in which or (kind, sd) in done:
            continue
        cp = world(kind, sd, L)
        res = run_corpus(cp, synthetic=True)
        ck = floor_checks(kind, res)
        rec = {"world": kind, "seed": sd, "checks": ck, "planted": sorted(PLANT[kind]),
               "explanatory": {"status": {c: s["single"] for c, s in res["status"].items()}, "fit": res["fit"],
                               "g_dynamics_verdict": res["g_dynamics_verdict"]}, "result": res}
        if kind == "W3" and sd == FLOOR_SEEDS[0]:
            rec["approximation_check"] = approx_check(cp, res)
        out["worlds"].append(rec)
        log(f"   {kind} seed {sd}: checks {ck}")
        f.write_text(jdump(out))
        del cp
        gc.collect()


def merge():
    worlds = []
    for p in sorted(TMP.glob("floor-*.json")):
        worlds += json.loads(p.read_text())["worlds"]
    seen, uniq = set(), []
    for w in worlds:
        if (w["world"], w["seed"]) not in seen:
            seen.add((w["world"], w["seed"]))
            uniq.append(w)
    out = {"worlds": sorted(uniq, key=lambda w: (w["world"], w["seed"]))}
    out["complete"] = set(FLOOR) <= seen
    fam = {}
    for w in out["worlds"]:
        for k, v in w["checks"].items():
            fam.setdefault(k, []).append(bool(v))
    out["families"] = {k: all(v) for k, v in fam.items()}
    out["passes"] = bool(out["complete"] and all(out["families"].values()))
    OUT.mkdir(exist_ok=True)
    (OUT / "synthetic.json").write_text(jdump(out))
    log(f"FLOOR {'PASSES' if out['passes'] else 'FAILS'}; complete {out['complete']}; failing families "
        f"{[k for k, v in out['families'].items() if not v]}")


# ---------------------------------------------------------------- real corpora

def real(name):
    floor = OUT / "synthetic.json"
    assert floor.exists() and json.loads(floor.read_text()).get("complete"), "the floor runs before any real statistic"
    cp = {"assist": S2.load_assist, "xes": S2.load_xes, "eedi": S2.load_eedi}[name]()
    res = run_corpus(cp, eedi=(name == "eedi"))
    res["corpus"] = name
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(jdump(res))
    log(f"{name} written")


def priors():
    """Summaries of the fitted EM prior and items per corpus (out/fitted-priors.json), from the scratchpad
    cache of the base fit: the parameters the equations in README.md quote."""
    out = {}
    for n in ("assist", "xes", "eedi"):
        f = TMP / f"fit-{n}.pkl"
        if not f.exists():
            continue
        fit = pickle.loads(f.read_bytes())

        def q(x):
            x = np.asarray(x, float)
            return {"median": float(np.median(x)), "p10": float(np.percentile(x, 10)), "p90": float(np.percentile(x, 90))}
        p1, p0 = fit["pr1"], fit["pr0"]
        lam = p1.W[:, 0]
        a, b, c, d, beta = fit["it1"]
        out[n] = {"skills": int(len(p1.mu)), "M1_prior": {"mu_k": q(p1.mu), "lambda_k": q(lam), "D_k": q(p1.D),
                  "general_share_lambda2_over_lambda2_plus_D": q(lam ** 2 / (lam ** 2 + p1.D))},
                  "M0-G_prior": {"mu_k": q(p0.mu), "D_k": q(p0.D)},
                  "M1_items": {"a": q(a), "b": q(b), "c": q(c), "d": q(d), "beta_practice": float(beta)},
                  "M0-G_beta_practice": float(fit["it0"][4])}
    (OUT / "fitted-priors.json").write_text(jdump(out))
    log(f"priors summarised for {list(out)}")


COMPONENTS = {"g": ("g",), "g dynamics": ("drift", "learn"), "M2 item memory": ("M2",), "M3' session shift": ("M3'",),
              "M5 learner-level dynamics": ("M5",), "M6 observed traces": ("M6",)}


def verdicts():
    """The cross-corpus verdicts (out/verdicts.json), with the floor's per-family flags applied."""
    fl = json.loads((OUT / "synthetic.json").read_text())
    fam = fl["families"]
    corp = {n: json.loads((OUT / f"{n}.json").read_text()) for n in ("assist", "xes", "eedi") if (OUT / f"{n}.json").exists()}

    def flag(keys):
        bad = [k for k in keys if fam.get(k) is False]
        return " (UNCALIBRATED)" if bad else ""
    out = {"floor": {"passes": fl["passes"], "failing_families": [k for k, v in fam.items() if not v]}, "components": {},
           "per_corpus": {}}
    for comp, subs in COMPONENTS.items():
        per = {}
        for n, r in corp.items():
            st = r["status"]
            have = [st[s_] for s_ in subs if s_ in st]
            if not have:
                continue
            if comp == "g dynamics":
                gd = r["fit"]["g_dynamics_in_FULL"]
                s_full = st[gd]
                kept = any(h["kept"] for h in have)
                per[n] = {"kept": kept, "loo": bool(s_full["loo"]), "nd": bool(s_full["not_discriminable"]),
                          "detected": any(h["detected"] for h in have), "verdict": r["g_dynamics_verdict"],
                          "profile": {s_: st[s_]["horizon_profile"] for s_ in subs}}
            else:
                h = have[0]
                per[n] = {"kept": h["kept"], "loo": bool(h["loo"]), "nd": bool(h["not_discriminable"]),
                          "detected": h["detected"], "profile": h["horizon_profile"], "single": h["single"]}
        n_test = len(per)
        n_pass = sum(1 for v in per.values() if v["kept"] and v["loo"])
        n_nd = sum(1 for v in per.values() if v["kept"] and v["nd"])
        need = 2 if n_test >= 2 else 1
        if n_test >= 2:
            v = ("JUSTIFIED" if n_pass >= need else "UNIDENTIFIED" if n_pass + n_nd >= need and n_nd > 0 else "NOT JUSTIFIED")
        elif n_test == 1:
            v = "UNIDENTIFIED (ONE CORPUS)" if n_pass == 1 else "NOT JUSTIFIED"
        else:
            v = "NOT TESTABLE"
        if v == "NOT JUSTIFIED":
            kep = [n for n, x in per.items() if x["kept"] and x["loo"]]
            det = [n for n, x in per.items() if x["detected"] and n not in kep]
            if kep:
                v += f" (KEPT WITH LOO ON {', '.join(kep)} ONLY)"
            if det:
                v += f" (DETECTED AT H1 ONLY ON {', '.join(det)})"
        keys = {"g": ["KEEP_g"], "g dynamics": ["KEEP_drift", "KEEP_learn", "KEEP_gdyn_verdict"], "M2 item memory": ["KEEP_M2"],
                "M3' session shift": ["KEEP_M3'"], "M5 learner-level dynamics": ["KEEP_M5"], "M6 observed traces": ["KEEP_M6"]}[comp]
        dkeys = [k.replace("KEEP_", "DETECT_") for k in keys if not k.endswith("verdict")]
        ndf = " (DISCRIMINABILITY UNCALIBRATED)" if fam.get("ND_g_not_discriminable") is False and \
            v.startswith(("JUSTIFIED", "UNIDENTIFIED")) else ""
        out["components"][comp] = {"verdict": v + flag(keys) + ndf,
                                   "detected_readings_flag": flag(dkeys).strip() or "calibrated",
                                   "testable_corpora": list(per), "per_corpus": per}
    out["components"]["structured layer f_j (M4)"] = {"verdict": "UNIDENTIFIED (S1 NO GO; M4 skipped)"}
    out["components"]["S_t significance"] = {"verdict": "HOLE: theoretically specified, unobserved, unidentified"}
    out["components"]["E_t other actors' events"] = {"verdict": "HOLE: unobserved in these corpora"}
    sam = ["skill-local state u_lk (the engine)"] + [c for c in COMPONENTS if out["components"][c]["verdict"].startswith("JUSTIFIED")]
    out["smallest_adequate_model"] = "SMALLEST ADEQUATE MODEL = {" + ", ".join(sam) + "}"
    for n, r in corp.items():
        st = r["status"]
        out["per_corpus"][n] = {"kept_with_loo": [c for c, s_ in st.items() if s_["kept"] and s_["loo"]],
                                "g_dynamics": r["g_dynamics_verdict"], "misspecification": r.get("misspec_verdict"),
                                "forms": r.get("form_verdicts"), "single": {c: s_["single"] for c, s_ in st.items()}}
    (OUT / "verdicts.json").write_text(jdump(out))
    log(out["smallest_adequate_model"])
    for c, v in out["components"].items():
        log(f"   {c}: {v['verdict']}")


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "synthetic":
        synthetic(sys.argv[3].split(",") if len(sys.argv) > 3 else None, tag=sys.argv[2] if len(sys.argv) > 2 else "all",
                  L=int(sys.argv[4]) if len(sys.argv) > 4 else 2000)
    elif what == "dev":                     # development worlds (seeds 100+), not the floor; nothing is written
        kind, sd, L_ = sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
        assert sd >= 100
        cp_ = world(kind, sd, L_)
        r_ = run_corpus(cp_, synthetic=True)
        log(f"DEV {kind} {sd}: checks {floor_checks(kind, r_)}")
        if kind == "W3":
            log(f"DEV approximation check {approx_check(cp_, r_)}")
    elif what == "merge":
        merge()
    elif what == "verdicts":
        verdicts()
    elif what == "priors":
        priors()
    else:
        real(what)
