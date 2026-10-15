"""PRE-REGISTERED: state timescales. (A) How much of the coupled state's cold-skill gain can the engine's
own Beta structure capture with a learner-informed prior? (B) Is there a fast persistent within-session
state once measured local structure is accounted for, and does filtering it out give a better slow
state for the next session?

SYSTEM-MODEL.md: the fast part of Phi, and separating w (state noise that persists) from v (answer
noise). Brief: docs/notes/NEXT-ROUND.md S2 and its common rules; every section of
docs/notes/S2-HOSTILE-REVIEW.md is answered below (HOSTILE REVIEW, point by point). Written
2026-10-01, before any statistic of this design on real data. Only file headers were read first (the
ASSISTments export's column names, including `type`, `assignment_id`, `hint_count`, `attempt_count`,
`ms_first_response`, `first_action`; Eedi answers.tsv's `QuizId` and minute-resolution
`DateAnswered`) plus graph-state's recorded sample sizes and chosen ranks. Part A and Part B are
separate verdict families: either can succeed while the other fails. Open-corpus answers about the
formulas, not about Lazuli's items.

DATA (raw data never enters the repo; out/ holds aggregates only). Loaders and row definitions are
engine-calibration/variants.py's (one row per attempt x competency) and graph-state's competencies:
  ASSISTments 2012-13 (PRIMARY for Part B): variants.load_assist's filters and 1-in-3 learner sample,
    rebuilt here so each attempt keeps its problem-log fields (assist_raw.load: assignment_id,
    hint_count, attempt_count, ms_first_response, first_action); the section `type` (MasterySection =
    skill builder) is read in a second streaming pass of the same zip, joined on problem_log_id.
    competency = skill_id; no hierarchy. Reliable start times (seconds).
  XES3G5M through data_path("XES_DIR"): variants.load_xes, competency = leaf KC. Learners with
    sha256("gs" + uid)[:8] % 4 == 0: a 1-in-4 subset of graph-state's 1-in-2 sample (RAM: this run
    shares the machine and is held under about 4 GB). Timestamps are milliseconds, but 51% of
    consecutive answers share one (submitted as a set; residual-structure batches.py).
  Eedi NeurIPS 2020: variants.load_eedi (1-in-6, competency = level-3 subject), further restricted to
    sha256("gs" + uid)[:8] % 2 == 0 (1 in 12, RAM). QuizId is read in a second pass of answers.tsv with
    the same learner filter and aligned by the loader's file order. LAST-answer order; DateAnswered has
    minute resolution (ties broken by file order).
  Demand (B2, XES3G5M only): difficulty-sources/build/ratings.json, the two-rater panel's
    element-interactivity rating per question (mean of raters, as xes_sources.rated_matrix), z-scored
    over rated items; unrated items get 0 and a flag. demand_i is externally characterised task
    demand, not experienced cognitive load.
  SPLIT: e2e.py's learner hash (sha256(uid)[:8] % 5 == 0 is TEST). Every fitted quantity from TRAIN
    learners, every metric on TEST learners. Where a grid search on full TRAIN is too slow, it uses the
    TRAIN validation quarter sha256("gsrank" + uid)[:8] % 4 == 0 (graph-state's).
  SESSIONS: a gap over 30 minutes starts a new session (ASSISTments, XES3G5M). Eedi: a session is a quiz
    sitting, i.e. a new session when QuizId changes or a gap exceeds 30 minutes. SUBMISSION (XES3G5M
    only): a maximal run of a learner's consecutive attempts with an identical timestamp. ASSISTments
    (0.005% ties) and Eedi (ties are minute rounding, not sets) use one attempt per step.

SHARED MACHINERY (graph-state's gstate.py, unchanged; graph-state's chosen rank r: XES3G5M 8,
ASSISTments 2, Eedi 8, not re-selected)
  C0   the calibrated engine, E5-decay (engine-calibration): an independent Beta per skill.
  C2   graph-state's coupled Gaussian state at rank r, Stage 1 + EM + per-variant item refit, filter
       run_gauss. C2g: the same with r = 1 (one general factor plus skill-local variance D_k).
  The joint filter used below (run_joint) is run_gauss plus optional extra scalar components and an
  offset; with every option off it must equal run_gauss to 1e-9 (asserted). Extra components enter the
  response's linear predictor S = theta_eff + beta x + h + sum_c l_c c and are updated by a DECOUPLED
  extended-Kalman step: at the predictive mean of S the response gives score g and information J; each
  component treats the others' predictive variance as noise (gain l_c V_c / (l_c^2 V_c + 1/J + v + sum
  of the others' l^2 V)); the skills' pseudo-measurements take precision 1 / (1/J + sum_c l_c^2 V_c)
  instead of J. Prediction: the probit-integrated 4PL over the summed predictive variance.

PART A. ENGINE-IMPLEMENTABLE COLD-START COUPLING (an observation / state-estimation question; it does
not identify transfer in Phi). g is a forecasting coordinate in p(X), not a learner mechanism.
  g-TRACKER: C2g's general-factor posterior N(g_hat, V_g) per learner, before each attempt, from that
    learner's strictly earlier responses only (the filter predicts before it updates). Its prior
    (mu_k, lambda_k, D_k) and items are fitted on TRAIN. Engine cost: one scalar mean and precision per
    learner, plus per skill a loading and a unique variance fitted offline.
  A1 (learner-informed cold-start prior). The engine's Beta for (learner, skill k) is created at the
    first attempt on k as Beta(n0 p0, n0 (1 - p0)), logit p0 = mu_k + lambda_k g_hat (g_hat at that
    attempt). The engine's decay pulls toward this prior instead of Beta(0.5, 0.5). Items, asymptotes
    and evidence masses are C0's. Two forms: A1-global (one mu, one lambda) and A1-skill (mu_k,
    lambda_k per skill; penalised: mu_k ~ N(mu, 1), lambda_k ~ N(lambda, 0.5^2); fewer than 20 TRAIN
    first attempts keep the global pair). mu, lambda fitted on TRAIN first attempts (a first attempt's
    prediction depends on p0 only), by Fisher scoring under C0's item model; n0 on a grid {0.5, 1, 2,
    3, 5, 8, 13, 20} by TRAIN-validation log loss of the full replay. A1 at n0 = 1, p0 = 0.5 must equal
    C0 exactly (asserted). A1 below means A1-skill; A1-global is reported beside it.
  A2 (A1 plus a general state blended into warm predictions). The pair's Beta is held as a prior part
    and an evidence part: alpha = n0 p0(t) + alpha_e, beta = n0 (1 - p0(t)) + beta_e, with p0(t) from
    the CURRENT g-tracker at every attempt and alpha_e, beta_e the engine's accumulated masses (decayed
    toward 0 by the engine's curve). Three forms (hostile review 2.A3):
      A2-cold  = A1 (the prior is fixed at first touch: cold-only use of g);
      A2-orth  p0(t) from g_hat with skill k's own evidence removed (leave-skill-out factor posterior:
               the skill's pseudo-measurement subtracted from the factor's precision and information),
               so a response counts once: in alpha_e / beta_e, and in g only through other skills;
      A2-naive p0(t) from the full g_hat, which already contains skill k's responses (counted twice).
    n0 refitted per form on the same grid.
  CONTROLS (hostile review 2.A1, 2.A2)
    A1-leak  g_hat = the learner's FINAL general-factor posterior (all of their responses, including the
             target skill and the future). A deliberate leak: it must score much better on the floor.
    A1-der   g_hat deranged: learners are grouped by decile of total attempts and deranged within decile
             (no fixed point); learner l's attempt with n earlier attempts takes learner pi(l)'s g_hat
             after min(n, n_pi(l)) attempts. Same count, same volume decile, same timing scale, the same
             distribution of g_hat (asserted: SD ratio within [0.9, 1.1]), someone else's outcomes. mu,
             lambda, n0 refitted under the derangement (applied to TRAIN the same way).
    A1-vol   logit p0 = mu_k + gamma_1 log(1 + earlier attempts) + gamma_2 log(1 + days since the
             learner's first attempt): practice volume and timing only, fitted like A1.
  REFERENCES: C0, C2g, C2 (the full coupled state), CLIM (the item's TRAIN success rate).
  METRICS (graph-state's, TEST learners): M1 cold attempts (all skills new, not the learner's first
    attempt): log loss, AUC, ECE; M2 every attempt; M3 horizon bins (< 1 d, 1-7 d, 7-30 d, >= 30 d since
    the last evidence on the skills); M4 coverage of central 50/80/95% intervals for the count correct
    in 5 consecutive single-skill attempts (cold and warm windows; Beta variants by 20 Beta quantile
    points through the item model, as graph-state's C0) and ECE; M5 unneeded practice per 1,000 at
    matched 20% premature-advance risk (10%, 30% reported). B = 200 learner bootstraps, the same draws
    for every variant; 95% percentile intervals.
  HEADLINE: share = (LL_C0 - LL_A) / (LL_C0 - LL_C2) on M1, per draw; share of C2's M2 gain likewise.
  VERDICTS (per corpus)
    A1: PRIOR-ONLY CAPTURES MOST if the share's lower bound >= 0.5; PRIOR-ONLY CAPTURES SOME if it is
        > 0; PRIOR-ONLY CAPTURES NONE otherwise. CALIBRATION GUARD (2.A4): fails if A1's cold-window
        intervals are OVER-CONFIDENT (a coverage more than 0.05 below nominal) or its cold ECE exceeds
        C0's with the difference's lower bound above 0.005. A failing guard appends " BUT OVER-CONFIDENT"
        and the variant does not pass. NEXT-ATTEMPT GUARD: "A1 WORSENS NEXT-ATTEMPT" if its M2 gain over
        C0 has upper bound < 0.
    A2: GENERAL STATE ADDS TO WARM PREDICTIONS if A2-orth beats A1 on M2 (lower bound > 0) and passes the
        guard on warm windows too; ADDS NOTHING BEYOND THE PRIOR if the upper bound < 0.0005; NOT
        RESOLVED otherwise. Reported: A2-orth's share of C2's M1 and M2 gains.
    DOUBLE COUNTING: NAIVE BLEND DOUBLE-COUNTS if A2-naive's warm intervals are OVER-CONFIDENT, or its
        M2 log loss or warm ECE is worse than A2-orth's (lower bound of the difference > 0); NO DOUBLE
        COUNTING DETECTED otherwise.
    LEARNER INFORMATION: LEARNER-SPECIFIC, NOT VOLUME if A1 beats both A1-der and A1-vol on M1 (lower
        bounds > 0); VOLUME CARRIES IT if A1-vol is not beaten (A1 - A1-vol upper bound <= 0); NOT
        RESOLVED otherwise.
    LEAK: A1-leak minus A1 on M1 is reported (the floor requires it to be large).

PART B. MOMENTARY STATE (a dynamics / state-decomposition question).
  BASE: C2 (primary) and C0 (the engine reading). THE CONTROL STACK (hostile review 3.B1-B6), each layer
  an offset h = F gamma in S, fitted on TRAIN by penalised Fisher scoring (gamma ~ N(0, 1)) with the
  base's TRAIN predictive state as the offset (one pass), features strictly from earlier attempts:
    H0  the base alone.
    H1  + PREVIOUS OUTCOME: y of the previous attempt in the session, its interaction with "same skill
        as now", "same skill" itself, and (XES3G5M) with "same submission"; zero at a session's start.
    H2  + PREVIOUS ACTION (ASSISTments only; observed activity traces, not activity): on the previous
        problem in the session, a hint used (hint_count > 0 or first action a hint), the bottom-out
        hint, more than one answer attempt, log(1 + seconds to first response) and a rapid first
        response (< 5 s).
    H3  + MEMORY AND SELECTION: item seen before by the learner, log(1 + times seen), log(1 + hours since
        last seen), the learner's last residual on this item under H0 (a stable learner x item
        proxy); log(1 + earlier same-skill attempts in the session), log(1 + minutes since the last
        same-skill attempt); log(1 + position in session), log(1 + seconds since the previous attempt);
        ASSISTments: log(1 + position within the assignment), the current run of consecutive correct
        answers within the assignment (dummies 1, 2, >= 3), first problem of an assignment, and each of
        these times MasterySection (the skill builder's stopping state: three in a row); XES3G5M:
        session position x demand (difficulty-sources' C1 term, so B2 tests the latent part beyond it).
    H4  + LEARNER DYNAMICS: a per-learner practice slope beta_l ~ N(0, sigma_b^2) on the practice
        feature x (a static component of run_joint; sigma_b on a grid {0, 0.05, 0.1, 0.15, 0.2, 0.3}
        by TRAIN log loss of the residual filter below). Hierarchical gain, so learner-specific learning
        within a session is not read as a momentary state.
  M (the candidate fast state; "unobserved fast state or process", not fatigue, attention or affect):
    AR1   delta_{t+1} = rho delta_t + eta, Var(delta) = tau^2 stationary, entering S as s_i delta with
          s_i = 1 (plain). RESET at each session start (mean 0, variance tau^2): the primary model.
          Steps are attempts (submissions on XES3G5M: there delta is BATCH-BLIND, i.e. every attempt of a
          submission is predicted from delta before the submission, the submission's responses update
          delta together at its end, and rho applies once per submission).
    B2    AR1 with s_i = exp(kappa demand_i) (XES3G5M): the kappa M demand term.
    DECAY AR1 with delta_start = rho_b delta_end between sessions (rho_b on {0, 0.25, 0.5, 0.75, 1}).
    Competing forms (3.B7): SRI (a session random intercept: rho = 1, no innovation), LAG3 (a
          finite-memory lag model: gamma_j (y - P) of the last three steps in the session, P from H4,
          fitted on TRAIN), 2TS (two AR components, rho_1 in {0.3, 0.5, 0.7}, rho_2 in {0.9, 0.95,
          0.98, 1}).
  FITTING: rho, tau, kappa, rho_b and the 2TS pairs by grid search (rho in {0, 0.2, 0.4, 0.5, 0.6, 0.7,
    0.8, 0.85, 0.9, 0.95, 0.98, 1}; tau in {0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0}; kappa in
    {-0.5, -0.25, 0, 0.25, 0.5, 0.75}) maximising TRAIN log likelihood of a RESIDUAL FILTER (the same
    decoupled step for the M components only, over the layer's fixed TRAIN predictive state), then held
    fixed in run_joint on TEST. Items are the base's. rho-hat intervals: 200 learner bootstraps of the
    grid argmax (per-learner log likelihoods per grid point). rho is also fitted on RESTRICTED steps
    only (below) and per TRAIN tercile of learner volume and of final g_hat (descriptive, 3.B4).
  METRICS (TEST; gains are log loss of the reference minus the variant, nats per attempt)
    B-M1 within-session next answer: every attempt that is not a session's first. Reported on all of
         them and on RESTRICTED steps: the previous step (previous submission on XES3G5M) shares no skill
         with the current attempt and the current item is new to the learner (3.B1, 3.B5). XES3G5M also
         by same-submission / next-submission transitions of the per-attempt (not batch-blind) AR1,
         reported only (3.B2).
    B-M2 THE KEY CRITERION, next-session first attempts (the first attempt of every session after the
         learner's first), four forecasts from the same items (hostile review 4):
           (1) BASELINE  H4 without M;
           (2) RAW       (1) plus eta x the mean residual of the learner's previous session under H4
                         (eta fitted on TRAIN);
           (3) ABSORBED  H4 + AR1's slow state with delta_end carried into the new session (mean and
                         variance): the momentary part treated as mastery;
           (4) FILTERED  H4 + AR1's slow state with delta reset (the primary model's own forecast).
         Decisive contrast (4) vs (3); then (4) vs (1). Also on the subset whose item's skill was
         practised in the previous session, and on the first five attempts of the session. Engine units
         (hostile review 7): log loss; coverage of the 5-attempt window at session start; M5 unneeded
         practice at matched 20% risk on next-session first attempts (premature-advance risk held fixed:
         the change in false early advances shows as items saved).
    B-M3 THE SLOW / FAST SPLIT (variance tree T4): TEST next-answer Brier score (explained Bernoulli
         variance; log loss beside it) of a forward ladder, each increment's share of the total
         reduction from L0 to L7: L0 CLIM; L1 general level only (C2g with D_k at its floor 0.01); L2 + skill-local
         (C2g); L3 + structured factors (C2); L4 + exposure and item memory (H3's memory and recency
         features alone); L5 + observed process (H1, H2 and H3's selection features); L6 + learner
         dynamics (H4); L7 + M (AR1). SLOW = L1-L3; FAST = L4, L5, L7; learner dynamics L6 separately.
         Leave-one-out drops of L4-L7 from L7 reported beside the forward shares.
  VERDICT HIERARCHY (per corpus; hostile review 8)
    EXISTENCE (the H4 + AR1 gain over H4 on B-M1, batch-blind on XES3G5M):
      FAST PERSISTENT STATE PRESENT if the lower bound > 0 on all within-session attempts AND on
        RESTRICTED steps (at least 2,000 TEST attempts);
      FAST PERSISTENT STATE NOT DETECTED if the lower bound on all within-session attempts is <= 0;
      FAST PERSISTENT STATE UNIDENTIFIED otherwise (persistence that does not survive the restriction,
        or too few restricted steps).
      The gain of AR1 at H0, H1, H2, H3 is reported to show what each control absorbs.
    FORM (only under PRESENT or UNIDENTIFIED; else NOT APPLICABLE):
      demand: DEMAND-SCALED SUPPORTED if B2 beats AR1 (lower bound > 0) with kappa-hat > 0; PLAIN
        SUPPORTED if B2 - AR1 has upper bound < 0.0002; FORM UNIDENTIFIED otherwise; NOT TESTABLE
        without ratings (ASSISTments, Eedi).
      dynamics: "<F> SUPPORTED" for the form F among AR1, SRI, LAG3, 2TS that beats each other one
        (lower bounds > 0; 2TS must beat AR1, which it nests); AR FORM UNIDENTIFIED otherwise. Read with
        the hierarchy: FAST STATE PRESENT; AR FORM UNIDENTIFIED is a valid outcome.
    ENGINE VALUE (B-M2):
      FILTERING IMPROVES NEXT-SESSION STATE if (4) beats (3) and (4) beats (1) (lower bounds > 0) and
        the gain over (1) is material: >= 0.001 nats per next-session first attempt, or items saved at
        20% risk with lower bound > 0, or session-start window coverage closer to nominal by >= 0.02
        at some level and no level further by > 0.02;
      FILTERING DOES NOT MATERIALLY IMPROVE NEXT-SESSION STATE if (4) - (1) has upper bound < 0.001 and
        the items-saved interval includes 0 or lies below it;
      ENGINE VALUE UNIDENTIFIED otherwise.
      WITHIN-SESSION VALUE: M MATERIAL WITHIN SESSION if the B-M1 gain over H4 has lower bound > 0 and
        point >= 0.001 nats; M NOT MATERIAL WITHIN SESSION otherwise.
    The ENGINE READING repeats EXISTENCE and ENGINE VALUE on C0 (C0 + AR1, the engine's Beta updated as
    shipped = ABSORBED; C0 + AR1 with each evidence mass multiplied by the filtered share 1 / (1 + J
    s^2 V_delta) = FILTERED); reported, not part of stop/go.

SYNTHETIC FLOOR (`python3 state_timescales.py synthetic`; before any real statistic). 2,000 learners,
  30 skills, 12 items per skill (half MC, c ~ U(0.1, 0.3); fill-in c ~ U(0.02, 0.08); slip ~ U(0, 0.04);
  a ~ logN(0, 0.25); b = skill offset N(-0.6, 0.6) + N(0, 0.7)); theta_lk = lambda_k g_l + u_lk
  (lambda ~ N(0.85, 0.1^2), Var u = 0.48: graph-state's world H), except world I; 18-30 sessions per
  learner, 1-2 skills per session (60% new while any remain), 8-16 attempts, 20-120 s apart, sessions 2
  hours to 20 days apart; practice gain +0.15 per attempt decaying by the engine's curve (graph-state's
  worlds); a hint flag and a demand value per item (N(0, 1)) are recorded in every world. Worlds:
    NULL  (2 seeds) no fast state (pure Bernoulli given the slow state);   I independent skills (Part A);
    AR-L  AR(1) rho = 0.8, tau = 0.6;   AR-S  rho = 0.8, tau = 0.35;   ARD  AR(1) x exp(0.5 demand),
          rho = 0.8, tau = 0.5;
    MEM   item memory only: within a session the previous item is re-served with probability 0.4, and a
          seen item carries +1.2 exp(-hours / 6) logits;
    ADAPT (2 seeds) adaptive serving only: after a wrong answer the next item is drawn from the easiest
          third of the skill's items, after a right one from the hardest third; a skill's run ends after
          three correct in a row (at most 16);
    HET   learner dynamics only: per-learner gain per attempt N(0.15, 0.12^2) (>= 0) and per-learner
          forgetting rate (log-uniform over a factor 9);
    LXI   stable learner x item only: e_li ~ N(0, 0.6^2), four items per skill per learner re-served across
          sessions;
    BEH   observed behaviour only: P(hint_t) = 0.08 + 0.35 (1 - y_{t-1}) + 0.30 hint_{t-1}; a hinted
          answer is wrong with probability 0.8 (the ASSISTments scoring rule); no latent state;
    BATCH answers submitted in sets of three (one timestamp) with a set-level shift N(0, 0.6^2) that does
          not carry across sets;
    TWO   two-timescale fast process: AR(1)s with rho 0.5 (tau 0.45) and 0.97 (tau 0.35).
  PASS RULES (every seed):
    Part A, NULL: A1-skill's M1 share of C2's gain >= 0.5 (point) with lower bound > 0; A1 beats A1-der
      (lower bound > 0); A1-leak beats A1 (lower bound > 0); A2-orth not OVER-CONFIDENT.  World I: no
      LEARNER-SPECIFIC verdict.
    Part B: NULL, MEM, ADAPT, HET, LXI, BEH, BATCH: EXISTENCE is not PRESENT and ENGINE VALUE is not
      FILTERING IMPROVES. AR-L and AR-S: PRESENT; rho-hat at H0 within 0.1 of 0.8 and at H4 within 0.15;
      no DEMAND-SCALED verdict; dynamics not SRI / LAG3 / 2TS SUPPORTED. AR-L also: FILTERING IMPROVES
      NEXT-SESSION STATE and M MATERIAL WITHIN SESSION (the engine-unit floor). ARD: PRESENT and
      DEMAND-SCALED SUPPORTED with kappa-hat > 0. TWO: PRESENT and dynamics not AR1 SUPPORTED.
  The H0 + AR1 gain in each no-M world is reported: it shows what the controls are there to remove.
  If a Part fails its floor, that Part's real verdicts carry "(UNCALIBRATED)". The machinery is debugged
  on synthetic worlds of these shapes with other seeds before the floor runs.

STOP / GO FOR S3 (out/stop-go.json; hostile review 9)
  GO (a named fast-state component in S3) if all of: ASSISTments EXISTENCE PRESENT; the floor's no-M
    worlds gave no PRESENT; the direction replicates on XES3G5M or Eedi (H4 + AR1 gain point > 0 and
    rho-hat > 0); ASSISTments ENGINE VALUE FILTERING IMPROVES NEXT-SESSION STATE; and a dynamics form
    SUPPORTED. GO-GENERIC: the same but AR FORM UNIDENTIFIED (S3 carries a generic fast component and
    compares AR1, SRI and LAG3 on its own criterion). NO-GO (LOCAL DEPENDENCE EXPLAINED) if ASSISTments
    reads NOT DETECTED: the earlier streak result is recorded as local dependence already explained by
    measured dynamics, not as a latent state. NO-GO (NOT ENGINE-RELEVANT) if PRESENT but the engine-value
    condition fails. HOLD (UNIDENTIFIED) otherwise. Part A's line in the same file: the cheapest passing
    variant in the order A1-global, A1-skill, A2-orth, C2g, with its numbers, for S3's g layer.

HOSTILE REVIEW, POINT BY POINT (docs/notes/S2-HOSTILE-REVIEW.md)
  2.A1 leakage: g_hat from strictly earlier responses (the filter predicts, then updates); prior and items
    from TRAIN; TEST scored without future responses; A1-leak plants the leak and the floor requires it
    to score better.  2.A2 practice volume: A1-der keeps count, volume decile and timing and swaps the
    outcomes (family-matched derangement, size asserted); A1-vol is a volume-and-timing prior.
  2.A3 double counting: A2-cold / A2-orth (leave-skill-out g) / A2-naive, judged on intervals and ECE,
    not log loss alone.  2.A4 calibration: the guard on interval coverage and ECE; M5 at matched risk.
  2.A5 population vs individual: g is called a forecasting coordinate throughout; A says nothing about
    whether g moves under experience (S3's M1-learn) or about transfer.
  3.B1 same-item / same-skill memory: H3 memory and recency features; RESTRICTED steps (different skill,
    new item); rho refitted on them.  3.B2 batches: XES3G5M is batch-blind, same-submission dependence
    cannot establish PRESENT; same- vs next-submission split reported; ASSISTments is primary.
  3.B3 selection policy: the served item's calibrated parameters are in every forecast; H3 adds the
    assignment position, the within-assignment run of correct answers, its MasterySection interaction;
    the floor's ADAPT worlds serve adaptively with no M.  3.B4 learner heterogeneity: H4's per-learner
    slope; the HET world; rho per learner tercile (descriptive).  3.B5 stable learner x item: H3's item
    residual proxy, new-item restriction, the LXI world.  3.B6 behaviour: H1 then H2 before M; the BEH
    world; the incremental gain after H1-H3 is reported layer by layer.  3.B7 AR(1) is one shape: SRI,
    LAG3 and 2TS compete; the TWO world; FORM UNIDENTIFIED is a registered outcome.
  4 tautology: four forecasts from the same filter and items; the decisive contrast is FILTERED vs
    ABSORBED; skill-continuation subset reported; session-end state reported by how the session ended
    (last answer right or wrong), because session boundaries encode learner choice and the stopping rule.
  5 w vs v: v = answer residual that does not persist given H; w / fast X = residual structure that
    persists and improves later forecasts; unobserved A, C, E can look like w. Nothing here shows any
    residual to be irreducible.
  6 floor: eleven Part B worlds above (the review's nine, plus AR-S and BATCH; world I serves Part A),
    with pass rules that separate "fast persistent structure exists" from "AR(1) recovered".
  7 engine units: next-answer and next-session log loss, interval coverage, items saved at matched risk;
    materiality 0.001 nats.  8 verdict hierarchy: EXISTENCE / FORM / ENGINE VALUE above.
  9 stop/go: above.  10 guardrail: a detected M is "unobserved fast state or process" first. Teacher
    help, peer help, classroom events and platform feedback (E_t, C_t) are unobserved here and can
    produce the same persistence; naming M needs independent measurement.

INTERPRETATION GUARDRAIL (SYSTEM-MODEL.md section 1): regularities of these platforms' activity systems
  under their own curricula, tools, rules and item-selection policies. Hints and response times are
  traces O^A, not activity. demand_i is task demand, not experienced load, which may depend on the
  learner's state, how the activity is organised, the context and the goal's significance. No factor or
  state is described as located solely in the learner; outcomes are not collapsed into one scalar (log
  loss, calibration and practice cost are reported separately).

LIMITS stated in advance: open corpora; observational logs collected under each platform's own
  item-selection policy, so D depends on X-hat and no gain here is an effect of D; the decoupled EKF
  ignores posterior correlation between components; the control stack is two-stage (gamma fitted on
  the base's state, not jointly); M's parameters come from a residual filter over a fixed base state;
  XES3G5M's timestamps cannot separate within-set dependence from a sitting, so it is not an
  equal-quality replication of fine dynamics; Eedi keeps the last answer per question (order is
  last-answer order; no item repeats; minute timestamps); ASSISTments, XES3G5M and Eedi subsamples as
  above; XES3G5M and Eedi have no hint or time-on-task traces; only XES3G5M has demand ratings (from
  text, without figures); the C2 rank is graph-state's, not re-selected on these subsamples.

CHANGES (after registration; each before the affected statistic is read)
  Changes 1-3 came from debugging the machinery on development worlds (seeds 100+, 400 learners;
  not the floor's seeds), before the floor and before any real statistic.
  1. M's parameters (rho, tau, kappa, rho_b, the 2TS pairs) and H4's sigma_b are fitted by the JOINT
     filter's own likelihood (run_joint over replicated learners, one parameter set per replica), not
     by a residual filter over a fixed base state. The base filter absorbs within-session deviations
     into the skill state, so a residual filter on top of it responds to them a second time: in a
     development AR world (rho 0.8, tau 0.6) it chose tau at the grid floor, 249 nats of TRAIN log
     likelihood above the planted value. Grids run on the FITTING SAMPLE: the TRAIN validation
     quarter, halved by sha256("s2fit" + uid) until it holds at most 150,000 attempts. B2 searches its
     registered kappa grid with (rho, tau) in the 3 x 3 grid neighbourhood of AR1's optimum; 2TS's two
     taus run over {0.1, 0.2, 0.3, 0.5, 0.8}. The engine reading keeps the residual filter, which is
     exact there (the shipped Beta update does not depend on the fast state).
  2. Components enter the forecast as a point shift; their variance is not integrated into P. Item
     discriminations are fitted on the base with the fast-state variance already in the residual, so
     integrating tau^2 counted it twice (in the development AR world the planted tau lost to tau =
     0.05 for that reason alone). The variance still sets each update's gains.
  3. Every layer carries an answer-noise component WN (rho = 0, tau_w fitted on the same grid), and WN
     is the reference of every persistence contrast: "H_k" below and in out/ means the layer plus its
     WN; H0-plain is C2 alone. An AR with rho = 0 has no persistence, yet it widens the slow state's
     evidence noise, and that alone improved forecasts in a development world with no fast state
     (+13.6 nats). So EXISTENCE is H4 + WN + AR1 against H4 + WN, the same machinery without
     persistence (as graph-state's C2-diag controls its coupling). In the variance-tree ladder, L6 is
     H4 with its WN. In the language of section 5, WN is v made explicit; AR is the candidate w.
  4. "(UNCALIBRATED)" is applied per verdict family, by the floor checks that family owns: Part A;
     EXISTENCE (no false PRESENT; PRESENT where planted); FORM (rho recovery, demand scaling, dynamics);
     ENGINE VALUE (with WITHIN-SESSION VALUE). Reason: hostile review 6 asks the instrument to
     separate "fast persistent structure exists" from "AR(1) recovered", so a failed rho recovery
     should flag the form and rho-hat, not existence. In a development AR world at floor size (2,000
     learners, rho 0.8, tau 0.6) the joint fit returned rho 0.6, tau 0.4: the skill state absorbs the
     slow part of the planted deviation. The pass rules themselves are unchanged.
  5. H2 adds the interaction previous hint x previous outcome. In the development behaviour world
     (hint chains driven by the previous outcome and the previous hint) the additive H2 left a residual
     that AR1 took up (+0.0009 nats within session, lower bound above 0; UNIDENTIFIED only because it
     failed the restricted steps). The planted process is a function of that pair, so the pair belongs
     in the control.
  6. AR1's grid excludes rho = 0, and WN's tau grid extends to {1.3, 1.6, 2.0}. At floor size the
     development behaviour world read PRESENT (+0.0009 nats) with the "AR1" at rho = 0, tau 1.0 beside a
     WN at the grid's top (1.0): two white-noise components, i.e. more evidence-noise inflation, not
     persistence. An AR at rho = 0 is WN, the reference, so it cannot be the persistent candidate.
  7. Computation only: the ASSISTments run started while the floor's last worlds ran; it reads the
     merged floor record after its own fit and replay, waiting for it, and its verdicts were not read
     until the floor had finished.
  8. Declaration only, added at integration after all results: the DIRECTION line below, which
     board/direction_audit.py requires. It changes no statistic, threshold or verdict.

DIRECTION: symmetric -- no edge between skills is oriented. The general level, the cold-start prior and
  the fast-state components are undirected state terms, so no reversed-arrow control applies.

RESULTS (floor, out/synthetic.json; registered seeds, 2,000 learners per world, code at the floor commit):
  Part A PASSES in every world. NULL worlds: A1's share of C2's cold gain 1.30 [1.19, 1.49] and 1.29
  [1.17, 1.57] (A1 beats C2 at first encounters there), A1 over A1-der +0.035 / +0.031 nats, A1-leak
  over A1 +0.011 / +0.014; world I: A1 over A1-der +0.0001 [-0.0005, +0.0007], no LEARNER-SPECIFIC.
  Part B: NO FALSE PRESENT in any no-M world (NULL x2, MEM, ADAPT x2, HET, LXI, BEH, BATCH); NULL seed 1
  and BEH read UNIDENTIFIED (gains of +0.00002 and +0.00019 nats that fail the restricted steps). But
  NO PLANTED FAST STATE WAS DETECTED: AR-L, AR-S, ARD and TWO all read NOT DETECTED or UNIDENTIFIED
  over H4 (AR-L: -0.000004 [-0.00005, +0.00005]; even at H0 +0.00009 [-0.00003, +0.00024]); rho-hat at H4 was
  0.5, 0.5, 0.4, 0.7 against 0.8 planted; ARD's demand scaling was not recovered. So the EXISTENCE,
  FORM and ENGINE VALUE families FAIL their floor and carry "(UNCALIBRATED)" on real data. What the
  floor does show: a planted fast state of tau 0.35-0.6 logits and rho 0.8 per answer is worth under
  0.0002 nats per answer to this filter once the previous outcome is controlled, so the instrument is
  specific (it does not invent M) but blind to M of that size; and the FILTERED-vs-ABSORBED contrast
  is positive in every world, with or without M (+0.003 to +0.026 nats), so it is not diagnostic on
  its own: carrying a filter's end-of-session estimate of a fast component always costs. FILTERED vs
  BASELINE is the informative half of the engine-value rule.

RESULTS (real runs; README.md has the tables). Part A, all three corpora: PRIOR-ONLY CAPTURES MOST.
  A1's share of C2's cold gain 1.01 [0.96, 1.05] (ASSISTments), 0.91 [0.89, 0.94] (XES3G5M), 0.94
  [0.92, 0.96] (Eedi); A1-global 0.58, 0.84, 0.86; A1 does not worsen the next attempt; GENERAL STATE
  ADDS TO WARM PREDICTIONS (A2-orth over A1 +0.0012, +0.0019, +0.0048); NAIVE BLEND DOUBLE-COUNTS on
  ASSISTments only; LEARNER-SPECIFIC, NOT VOLUME everywhere. Part B (UNCALIBRATED throughout): FAST
  PERSISTENT STATE PRESENT on all three (H4 + AR1 over H4, both with WN: +0.0008 [+0.0004, +0.0013],
  +0.0006 [+0.0004, +0.0008], +0.0012 [+0.0010, +0.0014]; restricted steps +0.0011, +0.0011, +0.0018),
  rho-hat 0.98, 0.98, 1.0: a level shift per sitting, reset at the boundary except on Eedi (rho_b
  0.75). AR FORM UNIDENTIFIED (ASSISTments, XES3G5M), 2TS SUPPORTED (Eedi, +0.000016); PLAIN SUPPORTED
  (XES3G5M, kappa-hat 0). Next-session FILTERED vs BASELINE +0.0006, +0.0001, +0.0003: FILTERING
  IMPROVES on ASSISTments by the coverage clause only; DOES NOT MATERIALLY IMPROVE elsewhere. T4 slow
  share of the Brier reduction 0.68, 0.85, 0.96; fast 0.31, 0.14, 0.03. Stop/go: HOLD (UNIDENTIFIED).

    python3 state_timescales.py synthetic | assist | xes | eedi
"""


from __future__ import annotations

import gc
import hashlib
import json
import math
import resource
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EC = ROOT / "studies/measurement/engine-calibration"
GS = ROOT / "studies/measurement/graph-state"
for p_ in (ROOT, EC, GS, HERE, ROOT / "studies/end-to-end/xes3g5m-build"):
    sys.path.insert(0, str(p_))
import calibrate as C  # noqa: E402
import engine as E  # noqa: E402
import variants as V  # noqa: E402
import e2e  # noqa: E402
import gstate as S  # noqa: E402
import coupling as CP  # noqa: E402
import tstate as T  # noqa: E402
from shared.paths import data_path, scratch_root  # noqa: E402

OUT = HERE / "out"
TMP = scratch_root() / "s2-tmp"      # intermediates (loaded corpus, fitted parameters, floor parts); deleted after
SEED = 20261001
BOOT = 200
RISKS = (0.20, 0.10, 0.30)
RANK = {"xes": 8, "assist": 2, "eedi": 8}
N0_GRID = (0.5, 1, 2, 3, 5, 8, 13, 20)
RHO_GRID = (0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95, 0.98, 1.0)
TAU_GRID = (0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)
WN_EXTRA = (1.3, 1.6, 2.0)          # CHANGE 6
KAPPA_GRID = (-0.5, -0.25, 0.0, 0.25, 0.5, 0.75)
SIGB_GRID = (0.0, 0.05, 0.1, 0.15, 0.2, 0.3)
RHOB_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
RHO1_2TS = (0.3, 0.5, 0.7)
RHO2_2TS = (0.9, 0.95, 0.98, 1.0)
MIN_RESTRICTED = 2000
MATERIAL = 0.001
EQUIV = 0.0002
LEVELS = (0.5, 0.8, 0.95)
WIN = 5
N_MC = 400
T0 = time.time()


def log(*a):
    gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    print(f"[{time.time() - T0:7.0f}s {gb:4.1f}GB]", *a, flush=True)


def hsh(u, mod, salt=""):
    return int(hashlib.sha256((salt + str(u)).encode()).hexdigest()[:8], 16) % mod


# ---------------------------------------------------------------- corpora

class Corpus:
    """A calibrate.Data plus per-attempt extras keyed by the attempt's file order `o` (dict of arrays
    indexed by o), per-item demand, and the run configuration."""

    def __init__(self, name, data, extra_o=None, demand=None, quiz_o=None, batch=False, rank=2,
                 synthetic=False):
        self.name, self.data, self.extra_o, self.demand = name, data, extra_o or {}, demand
        self.quiz_o, self.batch, self.rank, self.synthetic = quiz_o, batch, rank, synthetic


def load_assist() -> Corpus:
    sys.path.insert(0, str(ROOT / "studies/measurement/guessing-gaming"))
    import assist_raw
    import zipfile
    a = assist_raw.load(mod=3, keep=0, salt="ec", dedupe=False, with_skill_rows=True, chunksize=500_000)
    a = a[(a.original == 1) & (a.skill_id.notna()) & (a.ts > 0) & (a.ptype >= 0)]
    a = a[a.ptype != assist_raw.PTYPES.index("open_response")]
    a = a.drop_duplicates(["problem_log_id", "skill_id"]).reset_index(drop=True)
    a["y"] = (a.correct == 1).astype(float)
    a["o"] = a.problem_log_id.rank(method="dense").astype(np.int64)
    li, uids = pd.factorize(a.user_id)
    ii, pids = pd.factorize(a.problem_id)
    kk, _ = pd.factorize(a.skill_id)
    pt = a.drop_duplicates("problem_id").set_index("problem_id").ptype.reindex(pids).to_numpy()
    is_mc = pt == assist_raw.PTYPES.index("choose_1")
    data = C.Data(li, ii, kk, a.y.to_numpy(), a.ts.to_numpy(float), a.o.to_numpy(), is_mc, np.where(is_mc, 4, 0),
                  pt.astype(int), np.asarray(uids))
    no = int(a.o.max()) + 1
    first = a.drop_duplicates("o")
    o = first.o.to_numpy()

    def per_o(vals, fill=0.0):
        out = np.full(no, fill, float)
        out[o] = vals
        return out
    ext = {"hint": per_o(((first.hint_count > 0) | (first.first_action == 1)).to_numpy(float)),
           "bottom": per_o((first.bottom_hint == 1).to_numpy(float)),
           "multi": per_o((first.attempt_count > 1).to_numpy(float)),
           "rt_ms": per_o(first.ms_first_response.to_numpy(float), np.nan),
           "assign": per_o(first.assignment_id.to_numpy(float), -1)}
    plid = first.problem_log_id.to_numpy()
    keep = set(plid.tolist())
    log(f"ASSISTments: {len(a):,} rows; reading section types for {len(keep):,} problem logs")
    del a
    gc.collect()
    z = zipfile.ZipFile(data_path("ASSIST_DIR") / "assist2012.zip")
    typ = {}
    with z.open(assist_raw.MEMBER) as f:
        for ch in pd.read_csv(f, usecols=["problem_log_id", "type"], dtype={"problem_log_id": "float64", "type": "object"},
                              chunksize=1_000_000):
            ch = ch[ch.problem_log_id.isin(keep)]
            typ.update(zip(ch.problem_log_id.astype(np.int64).tolist(), (ch.type == "MasterySection").tolist()))
    ms = np.array([typ.get(int(p), False) for p in plid], float)
    assert len(typ) >= 0.99 * len(keep), (len(typ), len(keep))
    ext["mastery"] = per_o(ms)
    log(f"   MasterySection share of problem logs {ms.mean():.3f} (structural)")
    return Corpus("assist", data, ext, rank=RANK["assist"])


def load_xes() -> Corpus:
    data, _ = V.load_xes()
    keep = np.array([hsh(u, 4, "gs") == 0 for u in data.uid])
    I = data.I
    data = CP.subsample(data, keep)
    d = data_path("XES_DIR")
    q = pd.read_csv(d / "attempts.tsv", sep="\t", header=None, usecols=[1], names=["q"], dtype={"q": "category"})
    qids = list(q.q.cat.categories)
    del q
    assert len(qids) == I, (len(qids), I)
    rat = json.loads((ROOT / "studies/measurement/difficulty-sources/build/ratings.json").read_text())
    raters = list(rat["ratings"])
    vals = np.full(I, np.nan)
    for j, qq in enumerate(qids):
        v = [rat["ratings"][m].get(str(qq), {}).get("interactivity") for m in raters]
        v = [x for x in v if x is not None]
        if v:
            vals[j] = float(np.mean(v))
    rated = ~np.isnan(vals)
    dem = np.zeros(I)
    dem[rated] = (vals[rated] - vals[rated].mean()) / vals[rated].std()
    log(f"XES3G5M: {rated.sum():,} of {I:,} items rated for interactivity")
    return Corpus("xes", data, {}, demand=dem, batch=True, rank=RANK["xes"])


def load_eedi() -> Corpus:
    data, _ = V.load_eedi()
    keep = np.array([hsh(u, 2, "gs") == 0 for u in data.uid])
    data = CP.subsample(data, keep)
    keepu = {}
    parts = []
    for ch in pd.read_csv(data_path("EEDI_ANSWERS"), sep="\t", usecols=["UserId", "QuizId"],
                          dtype={"UserId": np.int64, "QuizId": np.int64}, chunksize=2_000_000):
        for u in ch.UserId.unique():
            if u not in keepu:
                keepu[u] = hsh(u, 6, "ec") == 0
        parts.append(ch[ch.UserId.map(keepu).to_numpy(bool)].QuizId.to_numpy())
    quiz = np.concatenate(parts)
    assert int(data.df.o.max()) < len(quiz)
    return Corpus("eedi", data, {}, quiz_o=quiz, rank=RANK["eedi"])


# ---------------------------------------------------------------- metrics with the learner bootstrap

class Mx:
    """Per-learner sums for one prediction vector on one subset: log loss and Brier always; AUC, ECE and
    matched-risk unneeded practice on request (variants.Metrics)."""

    def __init__(self, P, y, grp, nl, mask, full=False, risks=()):
        P = np.clip(P[mask], 1e-9, 1 - 1e-9)
        yy, g = y[mask], grp[mask]
        self.n = np.bincount(g, None, nl)
        self.ll = np.bincount(g, -(yy * np.log(P) + (1 - yy) * np.log1p(-P)), nl)
        self.br = np.bincount(g, (yy - P) ** 2, nl)
        self.m = V.Metrics(P, yy, g, nl, bins=True) if full or risks else None
        self.full, self.risks = full, risks
        self.N = int(mask.sum())

    def val(self, w):
        den = max(w @ self.n, 1e-12)
        out = {"logloss": float(w @ self.ll / den), "brier": float(w @ self.br / den)}
        if self.m is not None:
            out["ece"] = self.m.ece(w)
            if self.full:
                out["auc"] = self.m.auc(w.astype(float))
            if self.risks:
                wr = w[self.m.grp]
                share = float(wr @ self.m.y / wr.sum())
                for r in self.risks:
                    out[f"unneeded_{r}"] = self.m.unneeded(wr, r) * share * 1000
        return out


class Boot:
    """Point values and B learner-bootstrap draws (the same draws for every metric)."""

    def __init__(self, nl, seed):
        rng = np.random.default_rng(seed)
        self.W = [np.bincount(rng.integers(0, nl, nl), minlength=nl).astype(float) for _ in range(BOOT)]
        self.nl = nl
        self.pt, self.dr = {}, {}

    def add(self, key, mx: Mx):
        self.pt[key] = mx.val(np.ones(self.nl))
        self.dr[key] = [mx.val(w) for w in self.W]

    def add_sums(self, key, num, den):
        """A ratio of per-learner sums (coverage)."""
        self.pt[key] = {"v": float(num.sum() / max(den.sum(), 1e-12))}
        self.dr[key] = [{"v": float(w @ num / max(w @ den, 1e-12))} for w in self.W]

    def gain(self, base, var, k="logloss", sign=+1):
        """sign +1: base - var (lower is better)."""
        est = sign * (self.pt[base][k] - self.pt[var][k])
        d = np.array([sign * (a[k] - b[k]) for a, b in zip(self.dr[base], self.dr[var])])
        lo, hi = np.percentile(d, [2.5, 97.5])
        return {"est": float(est), "lo": float(lo), "hi": float(hi)}

    def share(self, base, num, den, k="logloss"):
        """(base - num) / (base - den)."""
        p = self.pt
        est = (p[base][k] - p[num][k]) / (p[base][k] - p[den][k])
        d = np.array([(a[k] - b[k]) / (a[k] - c[k]) for a, b, c in zip(self.dr[base], self.dr[num], self.dr[den])])
        lo, hi = np.percentile(d, [2.5, 97.5])
        return {"est": float(est), "lo": float(lo), "hi": float(hi)}

    def value(self, key, k):
        d = np.array([x[k] for x in self.dr[key]])
        lo, hi = np.percentile(d, [2.5, 97.5])
        return {"est": float(self.pt[key][k]), "lo": float(lo), "hi": float(hi)}


# ---------------------------------------------------------------- fitting the shared machinery

def fit_base(cp: Corpus):
    """A real corpus's fitted parameters are cached in TMP (computation only)."""
    import pickle
    cache = None if cp.synthetic else TMP / f"fit-{cp.name}.pkl"
    if cache is not None and cache.exists():
        fit = pickle.loads(cache.read_bytes())
        fit["at_tr"] = S.Attempts(cp.data, cp.data.rows("train"))
        log("fitted parameters read from the scratchpad cache")
        return fit
    fit = _fit_base(cp)
    if cache is not None:
        cache.write_bytes(pickle.dumps({k: v for k, v in fit.items() if k != "at_tr"}))
    return fit


def _fit_base(cp: Corpus):
    data = cp.data
    K = int(data.df.k.max()) + 1
    train = data.rows("train")
    asy = C.fit_asymptotes(data, train)
    base = E.engine_params(data.is_mc, data.m).replace(c=asy["c"], d=asy["d"], mode="know", eff="post")
    c0 = C.fit_ab(data.events(train), base, data.group).replace(name="C0")
    log("C0 (E5-decay) fitted")
    at_tr = S.Attempts(data, train)
    a, b, th, beta = S.static_items(at_tr, asy["c"], asy["d"], data.group, data.I, log=log)
    items1 = (a, b, asy["c"], asy["d"], beta)
    cl = S.cells(at_tr, th, a, b, asy["c"], asy["d"], K, beta)
    r = cp.rank
    pr2, _ = S.fit_dense(cl, r, log=log)
    prg = pr2 if r == 1 else S.fit_dense(cl, 1)[0]
    it2 = S.refit_items(at_tr, pr2, items1, K, data.group, data.I)
    itg = it2 if r == 1 else S.refit_items(at_tr, prg, items1, K, data.group, data.I)
    pr0 = S.Prior("dense", prg.mu, np.full(K, S.D_LO), W=prg.W, name="g only")
    log(f"priors and items fitted: rank {r}; practice slope C2 {it2[4]:.3f}, C2g {itg[4]:.3f}")
    del cl
    gc.collect()
    return {"K": K, "c0": c0, "pr2": pr2, "prg": prg, "pr0": pr0, "it2": it2, "itg": itg, "at_tr": at_tr}


def extras_for(cp: Corpus, at: S.Attempts):
    o = at.o
    ext = {k: np.asarray(v)[o] for k, v in cp.extra_o.items()}
    if cp.demand is not None:
        ext["demand"] = cp.demand[at.i]
    quiz = None if cp.quiz_o is None else np.asarray(cp.quiz_o)[o]
    return ext, quiz


def items_row(items, at):
    a, b, c, d, beta = items
    return a[at.i], b[at.i], c[at.i], d[at.i]


# ---------------------------------------------------------------- Part A

def fit_map(gv, it, k, y, prm: E.Params, K, per_skill=True, X=None):
    """logit p0 = mu_k + lambda_k g (or + X gamma for A1-vol) on first-attempt rows under C0's item
    model, by penalised Fisher scoring (mu_k ~ N(mu, 1), lambda_k ~ N(lambda, 0.5^2))."""
    a, b, c, d = prm.a[it], prm.b[it], prm.c[it], prm.d[it]
    Z = np.column_stack([np.ones(len(y)), gv]) if X is None else np.column_stack([np.ones(len(y)), X])
    w = np.zeros(Z.shape[1])
    for _ in range(30):
        L = T.sigmoid(a * (Z @ w - b))
        P = np.clip(c + (d - c) * L, 1e-9, 1 - 1e-9)
        dz = (d - c) * L * (1 - L) * a
        gr = Z.T @ ((y - P) / (P * (1 - P)) * dz) - 1e-4 * w
        H = (Z * (dz * dz / (P * (1 - P)))[:, None]).T @ Z + 1e-4 * np.eye(Z.shape[1])
        st = np.clip(np.linalg.solve(H, gr), -1, 1)
        w += st
        if np.abs(st).max() < 1e-7:
            break
    mu = np.full(K, w[0])
    lam = np.full(K, w[1] if X is None else 0.0)
    if not per_skill or X is not None:
        return mu, lam, w
    n_k = np.bincount(k, None, K)
    ok = n_k >= 20
    mk, lk = mu.copy(), lam.copy()
    for _ in range(30):
        L = T.sigmoid(a * (mk[k] + lk[k] * gv - b))
        P = np.clip(c + (d - c) * L, 1e-9, 1 - 1e-9)
        dz = (d - c) * L * (1 - L) * a
        u = (y - P) / (P * (1 - P)) * dz
        f = dz * dz / (P * (1 - P))
        g1 = np.bincount(k, u, K) - (mk - w[0])
        g2 = np.bincount(k, u * gv, K) - (lk - w[1]) / 0.25
        h11 = np.bincount(k, f, K) + 1
        h22 = np.bincount(k, f * gv * gv, K) + 4
        h12 = np.bincount(k, f * gv, K)
        det = h11 * h22 - h12 * h12
        s1 = np.clip((h22 * g1 - h12 * g2) / det, -1, 1)
        s2 = np.clip((h11 * g2 - h12 * g1) / det, -1, 1)
        mk, lk = mk + s1, lk + s2
        if max(np.abs(s1).max(), np.abs(s2).max()) < 1e-7:
            break
    mk[~ok], lk[~ok] = w[0], w[1]
    return mk, lk, w


def slot_rows(at):
    rows, cols = np.nonzero(at.M)
    return rows, cols, at.S[rows, cols], at.R[rows, cols]


def first_touch_P0(at, p_slot):
    """A1: each pair's p0 fixed at its first attempt, carried to its later attempts."""
    rows, cols, k, R = slot_rows(at)
    K1 = int(at.S.max()) + 1
    key = at.l[rows].astype(np.int64) * K1 + k
    first = R == 0
    fk, fv = key[first], p_slot[rows[first], cols[first]]
    o = np.argsort(fk)
    pos = np.searchsorted(fk[o], key)
    pos = np.clip(pos, 0, len(fk) - 1)
    found = fk[o][pos] == key
    P0 = np.full(at.S.shape, 0.5)
    P0[rows, cols] = np.where(found, fv[o][pos], 0.5)
    return P0


def deranged_g(at, g, nvol_dec, rng):
    """Learner l's attempt at step n takes learner pi(l)'s g after min(n, len - 1) steps; pi deranges
    learners within deciles of total attempts."""
    nl = at.nl
    ln = np.bincount(at.l, None, nl).astype(int)
    start = np.r_[0, np.cumsum(ln)[:-1]]
    q = np.quantile(ln, np.linspace(0, 1, 11)[1:-1])
    dec = np.searchsorted(q, ln, side="right")
    pi = CP.derange_within(dec, rng)
    src = start[pi[at.l]] + np.minimum(at.step, ln[pi[at.l]] - 1)
    return g[src]


def part_a_variants(at, fit, gt, maps, prm):
    """P0 arrays (n, smax) for every Part A variant on an Attempts `at`, given its g-tracker record gt."""
    rows, cols, k, R = slot_rows(at)
    out = {}
    mk, lk = maps["skill"][:2]
    mg, lg = maps["global"][:2]

    def slot(mu, lam, gvals):
        P = np.full(at.S.shape, 0.5)
        P[rows, cols] = T.sigmoid(mu[k] + lam[k] * gvals)
        return P
    g_att = gt["g"][rows]
    out["A1-global"] = first_touch_P0(at, slot(mg, lg, g_att))
    out["A1"] = first_touch_P0(at, slot(mk, lk, g_att))
    out["A2-orth"] = slot(mk, lk, gt["g_loo"][rows, cols])
    out["A2-naive"] = slot(mk, lk, g_att)
    out["A1-leak"] = first_touch_P0(at, slot(*maps["leak"][:2], gt["g_final"][at.l][rows]))
    out["A1-der"] = first_touch_P0(at, slot(*maps["der"][:2], gt["g_der"][rows]))
    Xv = gt["vol"][rows]
    wv = maps["vol"][2]
    P = np.full(at.S.shape, 0.5)
    P[rows, cols] = T.sigmoid(wv[0] + Xv @ wv[1:])
    out["A1-vol"] = first_touch_P0(at, P)
    return out


def vol_feats(at):
    first_t = at.t[np.r_[0, np.nonzero(np.r_[False, at.l[1:] != at.l[:-1]])[0]]]
    return np.column_stack([np.log1p(at.step), np.log1p((at.t - first_t[at.l]) / 86400.0)])


def g_record(at, fit, seed):
    gt = T.run_joint(at, fit["prg"], fit["itg"], fit["K"], record_g=True)
    gt["g_der"] = deranged_g(at, gt["g"], 10, np.random.default_rng(seed))
    gt["vol"] = vol_feats(at)
    return gt


def part_a(cp: Corpus, fit, at_te, ev: Boot, preds):
    data, K, c0 = cp.data, fit["K"], fit["c0"]
    at_tr = fit["at_tr"]
    gtr = g_record(at_tr, fit, SEED + 5)
    rows, cols, k, R = slot_rows(at_tr)
    cold = R == 0
    it_r, y_r = at_tr.i[rows][cold], at_tr.y[rows][cold]
    k_r = k[cold]
    maps = {"skill": fit_map(gtr["g"][rows][cold], it_r, k_r, y_r, c0, K, True),
            "global": fit_map(gtr["g"][rows][cold], it_r, k_r, y_r, c0, K, False),
            "leak": fit_map(gtr["g_final"][at_tr.l][rows][cold], it_r, k_r, y_r, c0, K, True),
            "der": fit_map(gtr["g_der"][rows][cold], it_r, k_r, y_r, c0, K, True),
            "vol": fit_map(None, it_r, k_r, y_r, c0, K, False, X=gtr["vol"][rows][cold])}
    sd_real, sd_der = float(np.std(gtr["g"])), float(np.std(gtr["g_der"]))
    ratio = sd_der / sd_real
    assert 0.9 <= ratio <= 1.1, f"A1-der: SD ratio {ratio:.3f} outside [0.9, 1.1]"
    info = {"map_global": maps["global"][2].tolist(), "map_leak": maps["leak"][2].tolist(),
            "map_der": maps["der"][2].tolist(), "map_vol": maps["vol"][2].tolist(),
            "lambda_k_median": float(np.median(maps["skill"][1])), "g_sd_ratio_der": ratio}
    P0_tr = part_a_variants(at_tr, fit, gtr, maps, c0)
    uid = np.asarray(data.uid)
    val = np.array([hsh(u, 4, "gsrank") == 0 for u in uid])
    sel = val[at_tr.learners]
    sel_rows = sel[at_tr.l]
    at_val = S.Attempts(data, data.rows("train") & val[data.df.l.to_numpy()])
    assert np.array_equal(at_val.gid, at_tr.gid[sel_rows])
    n0 = {}
    for vn, P0 in P0_tr.items():
        sc = {}
        for x in N0_GRID:
            Pv = T.run_beta_A(at_val, c0, K, P0[sel_rows], x)["P"]
            p = np.clip(Pv, 1e-9, 1 - 1e-9)
            sc[x] = float(-(at_val.y * np.log(p) + (1 - at_val.y) * np.log1p(-p)).mean())
        n0[vn] = min(sc, key=sc.get)
        info[f"n0_{vn}"] = {"chosen": n0[vn], "val_logloss": sc}
        log(f"   Part A {vn}: n0 = {n0[vn]}")
    info["_gfinal_tr"] = gtr["g_final"]
    del P0_tr, gtr
    gc.collect()
    gte = g_record(at_te, fit, SEED + 6)
    P0_te = part_a_variants(at_te, fit, gte, maps, c0)
    rec = {}
    o = T.run_beta_A(at_te, c0, K, None, 1.0, record=True)
    ref = S.run_beta(at_te, c0, K)["P_own"]
    err = float(np.abs(o["P"] - ref).max())
    assert err < 1e-9, f"run_beta_A differs from run_beta by {err}"
    preds["C0"], rec["C0"] = o["P"], (o["alpha"], o["beta"])
    for vn, P0 in P0_te.items():
        o = T.run_beta_A(at_te, c0, K, P0, n0[vn], record=True)
        preds[vn], rec[vn] = o["P"], (o["alpha"], o["beta"])
    preds["C2g"] = gte["P"]
    info["exactness_run_beta"] = err
    return rec, info, (gte["m"], gte["v"])


def eval_a(at, preds, rec, items_c2, items_g, ev: Boot, gauss_state, c0):
    nl, y, g = at.nl, at.y, at.l
    subsets = {"all": np.ones(at.n, bool), "cold": at.cold, "warm": at.warm}
    for name, lo, hi in CP.BINS:
        subsets[name] = at.warm & (at.gap_min >= lo * S.DAY) & (at.gap_min < hi * S.DAY)
    names = ["C0", "A1-global", "A1", "A2-orth", "A2-naive", "A1-leak", "A1-der", "A1-vol", "C2g", "C2", "CLIM"]
    for sk, msk in subsets.items():
        for vn in names:
            ev.add(f"A|{sk}|{vn}", Mx(preds[vn], y, g, nl, msk, full=sk in ("all", "cold", "warm"),
                                      risks=RISKS if sk == "all" else ()))
    win = CP.windows(at)
    cov = {}
    for wn, idx in win.items():
        wl = at.l[idx[:, 0]]
        den = np.bincount(wl, None, nl).astype(float)
        for vn in names:
            if vn == "CLIM":
                continue
            if vn in rec:
                u = CP.pit(at, idx, "beta", rec[vn], (c0.a, c0.b, c0.c, c0.d, 0.0))
            else:
                its = items_c2 if vn == "C2" else items_g
                u = CP.pit(at, idx, "gauss", gauss_state[vn], its)
            for q in LEVELS:
                ev.add_sums(f"Acov|{wn}|{vn}|{q}", np.bincount(wl, (np.abs(u - 0.5) <= q / 2).astype(float), nl), den)
        cov[wn] = int(len(idx))
    return {k: int(v.sum()) for k, v in subsets.items()}, cov


def intervals_verdict(ev, wn, vn):
    cv = {str(q): ev.pt[f"Acov|{wn}|{vn}|{q}"]["v"] for q in LEVELS}
    dev = [cv[str(q)] - q for q in LEVELS]
    lab = "OVER-CONFIDENT" if min(dev) < -0.05 else "UNDER-CONFIDENT" if max(dev) > 0.05 else "CALIBRATED INTERVALS"
    return cv, lab


def verdict_a(ev: Boot, counts, floor_ok=True):
    res = {"counts": counts}
    vs = ["A1-global", "A1", "A2-orth", "A2-naive", "A1-leak", "A1-der", "A1-vol", "C2g", "C2", "CLIM"]
    for sk in ("cold", "all", "h0", "h1", "h7", "h30"):
        res[f"gain_vs_C0_{sk}"] = {v: ev.gain(f"A|{sk}|C0", f"A|{sk}|{v}") for v in vs}
    res["auc_gain_vs_C0_cold"] = {v: ev.gain("A|cold|C0", f"A|cold|{v}", "auc", -1) for v in vs}
    res["auc_gain_vs_C0_all"] = {v: ev.gain("A|all|C0", f"A|all|{v}", "auc", -1) for v in vs}
    res["ece_change_vs_C0_cold"] = {v: ev.gain("A|cold|C0", f"A|cold|{v}", "ece", -1) for v in vs}
    res["items_saved"] = {v: {str(r): ev.gain(f"A|all|C0", f"A|all|{v}", f"unneeded_{r}") for r in RISKS} for v in vs}
    res["share_of_C2_cold"] = {v: ev.share("A|cold|C0", f"A|cold|{v}", "A|cold|C2") for v in vs if v != "C2"}
    res["share_of_C2_all"] = {v: ev.share("A|all|C0", f"A|all|{v}", "A|all|C2") for v in vs if v != "C2"}
    res["intervals"] = {}
    for v in ["C0"] + vs[:-1]:
        res["intervals"][v] = {wn: dict(zip(("coverage", "label"), intervals_verdict(ev, wn, v))) for wn in ("cold", "warm")}
    res["point"] = {k: v for k, v in ev.pt.items() if k.startswith("A|")}

    def guard(v, warm=False):
        bad = res["intervals"][v]["cold"]["label"] == "OVER-CONFIDENT" or res["ece_change_vs_C0_cold"][v]["lo"] > 0.005
        if warm:
            bad = bad or res["intervals"][v]["warm"]["label"] == "OVER-CONFIDENT"
        return not bad
    res["calibration_guard"] = {v: guard(v) for v in vs if v != "CLIM"}
    suf = "" if floor_ok else " (UNCALIBRATED)"
    sh = res["share_of_C2_cold"]["A1"]
    a1 = ("PRIOR-ONLY CAPTURES MOST" if sh["lo"] >= 0.5 else "PRIOR-ONLY CAPTURES SOME" if sh["lo"] > 0 else
          "PRIOR-ONLY CAPTURES NONE")
    if not guard("A1") and a1 != "PRIOR-ONLY CAPTURES NONE":
        a1 += " BUT OVER-CONFIDENT"
    res["A1"] = a1 + suf
    shg = res["share_of_C2_cold"]["A1-global"]
    res["A1-global"] = ("PRIOR-ONLY CAPTURES MOST" if shg["lo"] >= 0.5 else "PRIOR-ONLY CAPTURES SOME" if shg["lo"] > 0
                        else "PRIOR-ONLY CAPTURES NONE") + ("" if guard("A1-global") else " BUT OVER-CONFIDENT") + suf
    m2 = res["gain_vs_C0_all"]["A1"]
    res["A1_guard_M2"] = ("A1 WORSENS NEXT-ATTEMPT" if m2["hi"] < 0 else "A1 DOES NOT WORSEN NEXT-ATTEMPT") + suf
    d2 = ev.gain("A|all|A1", "A|all|A2-orth")
    res["A2_orth_over_A1_all"] = d2
    res["A2"] = ("GENERAL STATE ADDS TO WARM PREDICTIONS" if d2["lo"] > 0 and guard("A2-orth", True) else
                 "GENERAL STATE ADDS NOTHING BEYOND THE PRIOR" if d2["hi"] < 0.0005 else "NOT RESOLVED") + suf
    nv = ev.gain("A|all|A2-naive", "A|all|A2-orth")
    ne = ev.gain("A|warm|A2-naive", "A|warm|A2-orth", "ece")
    res["naive_minus_orth"] = {"logloss_all": nv, "ece_warm": ne}
    dc = (res["intervals"]["A2-naive"]["warm"]["label"] == "OVER-CONFIDENT" or nv["lo"] > 0 or ne["lo"] > 0)
    res["double_counting"] = ("NAIVE BLEND DOUBLE-COUNTS" if dc else "NO DOUBLE COUNTING DETECTED") + suf
    der = ev.gain("A|cold|A1-der", "A|cold|A1")
    vol = ev.gain("A|cold|A1-vol", "A|cold|A1")
    res["A1_over_der_cold"], res["A1_over_vol_cold"] = der, vol
    res["learner_information"] = ("LEARNER-SPECIFIC, NOT VOLUME" if der["lo"] > 0 and vol["lo"] > 0 else
                                  "VOLUME CARRIES IT" if vol["hi"] <= 0 else "NOT RESOLVED") + suf
    res["leak_minus_A1_cold"] = ev.gain("A|cold|A1", "A|cold|A1-leak")
    return res


# ---------------------------------------------------------------- Part B: grid fits on TRAIN

def grid_ar(at, st, S0, v0, ir, het=None, masks=None, rhos=RHO_GRID, taus=TAU_GRID, scale=None, carry=None,
            extra=None):
    """Grid of one AR component (optionally a second, `extra`) over a fixed predictive state; with het =
    (sigma_b, x) a static per-learner slope is carried at that sigma. -> list of (nl, G) per mask, grid."""
    R, Tt = np.meshgrid(np.asarray(rhos, float), np.asarray(taus, float), indexing="ij")
    R, Tt = R.ravel(), Tt.ravel()
    G = len(R)
    spec = []
    if het is not None:
        spec.append({"kind": "static", "sig": np.full(G, het[0]), "loading": het[1]})
    spec.append({"kind": "ar", "rho": R, "tau": Tt, "scale": scale, "carry": carry})
    if extra is not None:
        spec.append(extra)
    masks = masks or [np.ones(at.n, bool)]
    return T.resid_filter(at, st, S0, v0, ir, spec, masks), {"rho": R, "tau": Tt}


def argmax_boot(LL, seed, groups=None):
    """Grid argmax of summed per-learner log likelihood, and its 200-draw learner-bootstrap distribution."""
    tot = LL.sum(0)
    best = int(np.argmax(tot))
    rng = np.random.default_rng(seed)
    nl = LL.shape[0]
    draws = []
    for _ in range(BOOT):
        w = np.bincount(rng.integers(0, nl, nl), minlength=nl).astype(float)
        draws.append(int(np.argmax(w @ LL)))
    return best, np.array(draws), tot


def fit_ar_layer(at, st, S0, v0, ir, het, seed, masks=None):
    LLs, grid = grid_ar(at, st, S0, v0, ir, het, masks)
    best, draws, tot = argmax_boot(LLs[0], seed)
    out = {"rho": float(grid["rho"][best]), "tau": float(grid["tau"][best]),
           "rho_boot": [float(x) for x in np.percentile(grid["rho"][draws], [2.5, 50, 97.5])],
           "tau_boot": [float(x) for x in np.percentile(grid["tau"][draws], [2.5, 50, 97.5])],
           "train_ll_gain_over_tau_min": float(tot[best] - tot[grid["tau"] == min(TAU_GRID)].max())}
    prof = {}
    for r_ in RHO_GRID:
        prof[str(r_)] = float(tot[grid["rho"] == r_].max() - tot[best])
    out["rho_profile_ll"] = prof
    out["rho_profile_95"] = [float(r_) for r_ in RHO_GRID if prof[str(r_)] >= -1.92]
    return out, LLs, grid


def lag_feats(at, st, P):
    """(y - P) of the last three steps in the session (a step's mean residual on a batch-blind Struct)."""
    r = at.y - P
    nsub = int(st.sub.max()) + 1
    cnt = np.bincount(st.sub, None, nsub)
    Rs = np.bincount(st.sub, r, nsub) / np.maximum(cnt, 1)
    sess_of = np.zeros(nsub, np.int64)
    sess_of[st.sub] = st.sess
    F = np.zeros((at.n, 3))
    for j in (1, 2, 3):
        src = st.sub - j
        ok = (src >= 0) & (sess_of[np.maximum(src, 0)] == st.sess)
        F[:, j - 1] = np.where(ok, Rs[np.maximum(src, 0)], 0.0)
    return F


def prev_sess_resid(at, st, P):
    """Mean residual of the learner's previous session, at next-session first attempts (0 elsewhere)."""
    r = at.y - P
    ns = int(st.sess.max()) + 1
    m = np.bincount(st.sess, r, ns) / np.maximum(np.bincount(st.sess, None, ns), 1)
    return np.where(st.next_first, m[np.maximum(st.sess - 1, 0)], 0.0)



# ---------------------------------------------------------------- Part B: joint-filter grid (CHANGE 1)

CH = 40
FIT_CAP = 150_000


def het(sig, x):
    return {"kind": "static", "sig": sig, "loading": x}


def wnc(tau):
    """The answer-noise component: an AR with rho = 0 (no persistence; it only widens the evidence noise
    of the slow state's update). The reference for every persistence contrast (CHANGE 3)."""
    return {"kind": "ar", "rho": 0.0, "tau": tau, "scale": None, "carry": None}


def arc(rho, tau, scale=None, carry=None):
    return {"kind": "ar", "rho": rho, "tau": tau, "scale": scale, "carry": carry}


def fit_sample(fit, data):
    """TRAIN validation quarter (sha256("gsrank" + uid) % 4 == 0), halved by sha256("s2fit" + uid) until it
    holds at most FIT_CAP attempts. -> Attempts and the row selector into fit["at_tr"]."""
    at_tr = fit["at_tr"]
    uid = np.asarray(data.uid)
    keep = np.array([hsh(u, 4, "gsrank") == 0 for u in uid])
    m = 1
    while True:
        k2 = keep & np.array([hsh(u, m, "s2fit") == 0 for u in uid]) if m > 1 else keep
        sel = k2[at_tr.learners][at_tr.l]
        if sel.sum() <= FIT_CAP:
            break
        m *= 2
    at_f = S.Attempts(data, data.rows("train") & k2[data.df.l.to_numpy()])
    assert np.array_equal(at_f.gid, at_tr.gid[sel])
    return at_f, sel


class Grid:
    """Grid fits by the joint filter's own likelihood on the fitting sample (replicated learners)."""

    def __init__(self, at, st, fit):
        self.at, self.st, self.fit = at, st, fit

    def run(self, h, build, G, masks=None):
        masks = masks or [np.ones(self.at.n, bool)]
        out = [[] for _ in masks]
        for s0 in range(0, G, CH):
            j = np.arange(s0, min(G, s0 + CH))
            LL = T.run_joint(self.at, self.fit["pr2"], self.fit["it2"], self.fit["K"], st=self.st, h=h, spec=build(j),
                             rep=len(j), masks=masks)
            for k_, x in enumerate(LL):
                out[k_].append(x)
        return [np.concatenate(x, 1) for x in out]

    def wn(self, h, fixed):
        tw = np.asarray(TAU_GRID + WN_EXTRA)
        LL = self.run(h, lambda j: fixed + [wnc(tw[j])], len(tw))[0].sum(0)
        return {"tau_wn": float(tw[int(np.argmax(LL))]), "ll": float(LL.max()),
                "ll_over_none": float(LL.max() - LL[0])}

    def ar(self, h, fixed, seed, masks=None, st=None):
        if st is not None:
            self.st, st0 = st, self.st
        w = self.wn(h, fixed)
        R, Tt = np.meshgrid(np.asarray(RHO_GRID[1:]), np.asarray(TAU_GRID), indexing="ij")     # CHANGE 6: rho > 0
        R, Tt = R.ravel(), Tt.ravel()
        LLs = self.run(h, lambda j: fixed + [arc(R[j], Tt[j]), wnc(w["tau_wn"])], len(R), masks)
        best, draws, tot = argmax_boot(LLs[0], seed)
        out = {"tau_wn": w["tau_wn"], "wn_ll_over_none": w["ll_over_none"],
               "rho": float(R[best]), "tau": float(Tt[best]), "ll_over_wn": float(tot[best] - w["ll"]),
               "rho_boot": [float(x) for x in np.percentile(R[draws], [2.5, 50, 97.5])],
               "tau_boot": [float(x) for x in np.percentile(Tt[draws], [2.5, 50, 97.5])]}
        prof = {str(r_): float(tot[R == r_].max() - tot[best]) for r_ in RHO_GRID[1:]}
        prof["0.0 (WN only)"] = float(w["ll"] - tot[best])
        out["rho_profile_ll"] = prof
        out["rho_profile_95"] = [r_ for r_, v_ in prof.items() if v_ >= -1.92]
        if st is not None:
            self.st = st0
        return out, LLs, {"rho": R, "tau": Tt}

# ---------------------------------------------------------------- Part B: windows at session start

def ns_windows(at, st):
    """The first five attempts of a non-first session, all single-skill on the first attempt's skill."""
    t0 = np.nonzero(st.next_first & (st.sess_len >= WIN))[0]
    idx = t0[:, None] + np.arange(WIN)[None]
    ok = (at.nS[idx] == 1).all(1) & (at.S[idx, 0] == at.S[t0, 0][:, None]).all(1)
    return idx[ok]


def win_cover(at, st, idx, items, state, rng):
    """Randomised PIT of the count correct in each window under a forecast held at the window's start.
    state: dict m, v (skills' part), off0 (offset at t0), hv (other static variance), and the fast state's
    start (mu0, V0) with rho, tau, or None."""
    a, b, c, d, beta = items
    t0 = idx[:, 0]
    it = at.i[idx]
    ai, bi, ci, di = a[it], b[it], c[it], d[it]
    base = state["m"][t0] + state["off0"][t0]
    xo = beta * (at.x[idx] - at.x[t0][:, None])
    sd = np.sqrt(np.maximum(state["v"][t0] + state["hv"][t0], 0))
    k = st.sub[idx] - st.sub[t0][:, None]
    y = at.y[idx].sum(1).astype(int)
    out = np.empty(len(t0))
    for s0 in range(0, len(t0), 1000):
        sl = slice(s0, s0 + 1000)
        n = len(t0[sl])
        th = base[sl][:, None] + sd[sl][:, None] * rng.standard_normal((n, N_MC))
        Sm = th[:, :, None] + xo[sl][:, None, :]
        if state.get("rho") is not None:
            rho, tau = state["rho"], state["tau"]
            kmax = int(k[sl].max()) + 1
            dl = np.empty((n, N_MC, kmax))
            dl[:, :, 0] = state["mu0"][t0][sl][:, None] + np.sqrt(state["V0"][t0][sl])[:, None] * rng.standard_normal((n, N_MC))
            for j in range(1, kmax):
                dl[:, :, j] = rho * dl[:, :, j - 1] + tau * math.sqrt(max(1 - rho * rho, 0)) * rng.standard_normal((n, N_MC))
            Sm = Sm + np.take_along_axis(dl, np.broadcast_to(k[sl][:, None, :], (n, N_MC, WIN)), 2)
        Pm = ci[sl][:, None, :] + (di[sl] - ci[sl])[:, None, :] * T.sigmoid(ai[sl][:, None, :] * (Sm - bi[sl][:, None, :]))
        pmf = CP._poibin(Pm).mean(1)
        cdf = np.cumsum(pmf, 1)
        yy = y[sl]
        lo = np.where(yy > 0, cdf[np.arange(n), np.maximum(yy - 1, 0)], 0.0)
        hi = cdf[np.arange(n), yy]
        out[sl] = lo + rng.random(n) * (hi - lo)
    return out


# ---------------------------------------------------------------- Part B: the whole part

def ar_spec(p, het=None, scale=None, carry=None):
    sp = []
    if het is not None:
        sp.append({"kind": "static", "sig": het[0], "loading": het[1]})
    sp.append({"kind": "ar", "rho": p["rho"], "tau": p["tau"], "scale": scale, "carry": carry})
    return sp


def part_b(cp: Corpus, fit, at_te, st_te, ext_te, h0te, ev: Boot, gfinal_tr, preds, full=True):
    data, K = cp.data, fit["K"]
    at_tr = fit["at_tr"]
    pr2, it2 = fit["pr2"], fit["it2"]
    beta = it2[4]
    ext_tr, quiz_tr = extras_for(cp, at_tr)
    st_tr = T.Struct(at_tr, quiz_tr, cp.batch)
    info = {}
    btr = T.run_joint(at_tr, pr2, it2, K)
    S0_tr = btr["m"] + beta * at_tr.x
    v_tr = btr["v"]
    ir_tr = items_row(it2, at_tr)
    ir_te = items_row(it2, at_te)
    S0_te = h0te["m"] + beta * at_te.x
    cols_tr = T.features(st_tr, at_tr, ext_tr, cp.name)
    cols_te = T.features(st_te, at_te, ext_te, cp.name)
    T.set_item_resid(cols_tr, st_tr, at_tr.y, btr["P"])
    T.set_item_resid(cols_te, st_te, at_te.y, h0te["P"])
    for lay in cols_tr:
        for k_ in list(cols_tr[lay]):
            if k_ not in cols_te[lay]:
                cols_te[lay][k_] = np.zeros(at_te.n)
        for k_ in list(cols_te[lay]):
            if k_ not in cols_tr[lay]:
                del cols_te[lay][k_]
    layers = {"H1": ["H1"], "H2": ["H1", "H2"], "H3": ["H1", "H2", "H3mem", "H3sel"], "mem": ["H3mem"],
              "loomem": ["H1", "H2", "H3sel"]}
    H = {"H0": (np.zeros(at_tr.n), np.zeros(at_te.n))}
    gam = {}
    for nm, lays in layers.items():
        Ftr, names = T.matrix(cols_tr, lays)
        Fte, _ = T.matrix(cols_te, lays)
        g_ = T.fit_offset(Ftr, S0_tr, v_tr, *ir_tr, at_tr.y)
        H[nm] = (Ftr @ g_, Fte @ g_)
        gam[nm] = dict(zip(names, [float(x) for x in g_]))
        del Ftr, Fte
    info["gamma"] = gam
    has_h2 = len(cols_tr["H2"]) > 0
    log(f"   control stack fitted: H1 {len(cols_tr['H1'])}, H2 {len(cols_tr['H2'])}, H3 {len(cols_tr['H3mem']) + len(cols_tr['H3sel'])} columns")
    # the fitting sample and the joint-filter grid (CHANGES 1-3)
    at_f, selr = fit_sample(fit, data)
    st_f = T.Struct(at_f, None if quiz_tr is None else quiz_tr[selr], cp.batch)
    info["fit_sample"] = {"attempts": int(at_f.n), "learners": int(at_f.nl)}
    Hf = {k_: v_[0][selr] for k_, v_ in H.items()}
    xf = at_f.x
    G_ = Grid(at_f, st_f, fit)
    restricted_f = st_f.restricted
    ones_f = np.ones(at_f.n, bool)
    # H4's per-learner slope, with H3's answer-noise component
    wn3 = G_.wn(Hf["H3"], [])
    LLh = G_.run(Hf["H3"], lambda j: [het(np.asarray(SIGB_GRID)[j], xf), wnc(wn3["tau_wn"])], len(SIGB_GRID))[0]
    sb = float(SIGB_GRID[int(np.argmax(LLh.sum(0)))])
    info["sigma_b"] = sb
    info["sigma_b_ll"] = {str(x): float(v) for x, v in zip(SIGB_GRID, LLh.sum(0) - LLh.sum(0).max())}
    log(f"   H4 per-learner slope sigma_b = {sb}")
    arp = {}
    for i_, lay in enumerate(["H0", "H1", "H2", "H3", "H4"]):
        if lay == "H2" and not has_h2:
            arp["H2"] = arp["H1"]
            continue
        hh = Hf["H3" if lay == "H4" else lay]
        fixed = [het(sb, xf)] if lay == "H4" else []
        masks = [ones_f, restricted_f] if lay == "H4" else [ones_f]
        p_, LLs, grid = G_.ar(hh, fixed, SEED + 50 + i_, masks)
        if lay == "H4":
            br, drr, _ = argmax_boot(LLs[1], SEED + 60)
            p_["restricted_fit"] = {"rho": float(grid["rho"][br]), "tau": float(grid["tau"][br]),
                                    "rho_boot": [float(x) for x in np.percentile(grid["rho"][drr], [2.5, 50, 97.5])],
                                    "train_steps": int(restricted_f.sum())}
            vol = np.bincount(at_f.l, None, at_f.nl)
            gf = gfinal_tr[np.searchsorted(at_tr.learners, at_f.learners)]
            terc = {}
            for nmv, val in (("volume", vol), ("g_final", gf)):
                qq = np.quantile(val, [1 / 3, 2 / 3])
                grp = np.searchsorted(qq, val, side="right")
                terc[nmv] = [{"rho": float(grid["rho"][int(np.argmax(LLs[0][grp == j].sum(0)))]),
                              "tau": float(grid["tau"][int(np.argmax(LLs[0][grp == j].sum(0)))]),
                              "learners": int((grp == j).sum())} for j in range(3)]
            p_["terciles"] = terc
        arp[lay] = p_
        log(f"   AR1 on {lay}: noise tau {p_['tau_wn']}; rho {p_['rho']} tau {p_['tau']} (bootstrap rho {p_['rho_boot']}); "
            f"fit-sample log lik over the noise-only model {p_['ll_over_wn']:+.1f}")
    info["ar1"] = arp
    P = dict(preds)
    runs = {}

    def run(nm, h=None, spec=(), st=st_te, **kw):
        o = T.run_joint(at_te, pr2, it2, K, st=st, h=h, spec=spec, **kw)
        P[nm] = o["P"]
        runs[nm] = o
        return o
    xt = at_te.x
    P["H0-plain"] = h0te["P"]
    for lay in ("H0", "H1", "H2", "H3", "H4"):
        if lay == "H2" and not has_h2:
            P["H2"], P["H2+AR1"] = P["H1"], P["H1+AR1"]
            continue
        hte = None if lay == "H0" else H["H3" if lay == "H4" else lay][1]
        fx = [het(sb, xt)] if lay == "H4" else []
        p_ = arp[lay]
        run(lay, hte, fx + [wnc(p_["tau_wn"])])
        run(lay + "+AR1", hte, fx + [arc(p_["rho"], p_["tau"]), wnc(p_["tau_wn"])], record_ns=(lay == "H4"))
    p4 = arp["H4"]
    spec4 = [het(sb, xt), arc(p4["rho"], p4["tau"]), wnc(p4["tau_wn"])]
    run("H4+AR1-carry", H["H3"][1], [het(sb, xt), arc(p4["rho"], p4["tau"], carry=1.0), wnc(p4["tau_wn"])])
    log("   TEST runs: control stack and AR1 done")
    # RAW (2): eta on TRAIN, from H4's TRAIN forecasts
    o4tr = T.run_joint(at_tr, pr2, it2, K, st=st_tr, h=H["H3"][0], spec=[het(sb, at_tr.x), wnc(p4["tau_wn"])])
    Ptr4 = o4tr["P"]
    rb_tr = prev_sess_resid(at_tr, st_tr, Ptr4)
    S4_tr = o4tr["m"] + beta * at_tr.x + H["H3"][0] + o4tr["cm"]
    eta = T.fit_offset(rb_tr[:, None], S4_tr, o4tr["v"], *ir_tr, at_tr.y, mask=st_tr.next_first)
    info["raw_eta"] = float(eta[0])
    o4 = runs["H4"]
    rb_te = prev_sess_resid(at_te, st_te, o4["P"])
    P["RAW"] = T.probit_P(*ir_te, o4["m"] + beta * at_te.x + H["H3"][1] + o4["cm"] + eta[0] * rb_te, o4["v"])
    P["ABS"] = np.where(st_te.next_first, runs["H4+AR1"]["P_abs"], P["H4+AR1"])
    # metrics
    y, g, nl = at_te.y, at_te.l, at_te.nl
    within, restr, nf = st_te.within, st_te.restricted, st_te.next_first
    sub = {"within": within, "restricted": restr, "nextfirst": nf, "ns_cont": st_te.prev_sess_same_skill,
           "ns_new": nf & ~st_te.prev_sess_same_skill,
           "first5": (st_te.pos < WIN) & (st_te.sess != st_te.sess[np.nonzero(at_te.step == 0)[0]][at_te.l]),
           "all": np.ones(at_te.n, bool)}
    counts = {k_: int(v_.sum()) for k_, v_ in sub.items()}

    def addm(nm, keys=("within", "restricted", "all")):
        for k_ in keys:
            ev.add(f"B|{k_}|{nm}", Mx(P[nm], y, g, nl, sub[k_], full=False,
                                      risks=(0.20,) if k_ == "nextfirst" else ()))
    for nm in ("H0", "H0+AR1", "H1", "H1+AR1", "H2", "H2+AR1", "H3", "H3+AR1", "H4", "H4+AR1"):
        addm(nm)
    for nm in ("H4", "H4+AR1", "RAW", "ABS"):
        addm(nm, ("nextfirst", "ns_cont", "ns_new"))
    for nm in ("H4", "H4+AR1", "H4+AR1-carry"):
        addm(nm, ("first5",))
    res = {"counts": counts, "fit": info}
    res["gain_ar1_by_layer"] = {lay: {k_: ev.gain(f"B|{k_}|{lay}", f"B|{k_}|{lay}+AR1") for k_ in ("within", "restricted")}
                                for lay in ("H0", "H1", "H2", "H3", "H4")}
    res["gain_layer_over_H0"] = {lay: ev.gain("B|within|H0", f"B|within|{lay}") for lay in ("H1", "H2", "H3", "H4")}
    gw = res["gain_ar1_by_layer"]["H4"]["within"]
    gr = res["gain_ar1_by_layer"]["H4"]["restricted"]
    if gw["lo"] <= 0:
        exist = "FAST PERSISTENT STATE NOT DETECTED"
    elif counts["restricted"] >= MIN_RESTRICTED and gr["lo"] > 0:
        exist = "FAST PERSISTENT STATE PRESENT"
    else:
        exist = "FAST PERSISTENT STATE UNIDENTIFIED"
    res["existence"] = exist
    res["within_session_value"] = ("M MATERIAL WITHIN SESSION" if gw["lo"] > 0 and gw["est"] >= MATERIAL
                                   else "M NOT MATERIAL WITHIN SESSION")
    # engine value: next-session first attempts
    c43 = ev.gain("B|nextfirst|ABS", "B|nextfirst|H4+AR1")
    c41 = ev.gain("B|nextfirst|H4", "B|nextfirst|H4+AR1")
    c21 = ev.gain("B|nextfirst|H4", "B|nextfirst|RAW")
    sv = ev.gain("B|nextfirst|H4", "B|nextfirst|H4+AR1", "unneeded_0.2")
    res["next_session"] = {"filtered_vs_absorbed": c43, "filtered_vs_baseline": c41, "raw_vs_baseline": c21,
                           "items_saved_filtered_vs_baseline": sv,
                           "cont_filtered_vs_absorbed": ev.gain("B|ns_cont|ABS", "B|ns_cont|H4+AR1"),
                           "cont_filtered_vs_baseline": ev.gain("B|ns_cont|H4", "B|ns_cont|H4+AR1"),
                           "new_filtered_vs_absorbed": ev.gain("B|ns_new|ABS", "B|ns_new|H4+AR1"),
                           "first5_filtered_vs_carry": ev.gain("B|first5|H4+AR1-carry", "B|first5|H4+AR1"),
                           "first5_filtered_vs_baseline": ev.gain("B|first5|H4", "B|first5|H4+AR1"),
                           "ece": {nm: ev.pt[f"B|nextfirst|{nm}"]["ece"] for nm in ("H4", "H4+AR1", "RAW", "ABS")}}
    o = runs["H4+AR1"]
    lastok = nf & np.isfinite(o["dend"])
    yprev = y[np.maximum(np.arange(at_te.n) - 1, 0)]
    res["session_end_state"] = {f"last_answer_{int(v_)}": {"mean_delta_end": float(np.mean(o["dend"][lastok & (yprev == v_)])),
                                                           "n": int((lastok & (yprev == v_)).sum())} for v_ in (0, 1)}
    # coverage of session-start windows
    idx = ns_windows(at_te, st_te)
    rng = np.random.default_rng(SEED + 7)
    o4, o5 = runs["H4"], runs["H4+AR1"]
    h3 = H["H3"][1]
    ar = arp["H4"]
    tw_ = ar["tau_wn"] ** 2
    states = {"H4": {"m": o4["m"], "v": o4["v"], "off0": h3 + o4["cm"], "hv": o4["cv"] - tw_},
              "H4+AR1": {"m": o5["m"], "v": o5["v"], "off0": h3 + o5["cm"], "hv": o5["cv"] - ar["tau"] ** 2 - tw_,
                         "rho": ar["rho"], "tau": ar["tau"], "mu0": np.zeros(at_te.n), "V0": np.full(at_te.n, ar["tau"] ** 2)},
              "ABS": {"m": o5["m"], "v": o5["v"], "off0": h3 + o5["cm"], "hv": o5["cv"] - ar["tau"] ** 2 - tw_,
                      "rho": ar["rho"], "tau": ar["tau"], "mu0": np.nan_to_num(o5["dend"]),
                      "V0": np.nan_to_num(o5["Vend"], nan=ar["tau"] ** 2)}}
    covd = {}
    wl = at_te.l[idx[:, 0]] if len(idx) else np.zeros(0, int)
    den = np.bincount(wl, None, nl).astype(float)
    for nm, stt in states.items():
        if len(idx) == 0:
            continue
        u = win_cover(at_te, st_te, idx, it2, stt, rng)
        for q in LEVELS:
            ev.add_sums(f"Bcov|{nm}|{q}", np.bincount(wl, (np.abs(u - 0.5) <= q / 2).astype(float), nl), den)
        covd[nm] = {str(q): ev.pt[f"Bcov|{nm}|{q}"]["v"] for q in LEVELS}
    res["window_coverage"] = covd
    res["counts"]["windows"] = int(len(idx))
    cov_ok = False
    if covd:
        d4 = [abs(covd["H4+AR1"][str(q)] - q) for q in LEVELS]
        d1 = [abs(covd["H4"][str(q)] - q) for q in LEVELS]
        cov_ok = any(b_ - a_ >= 0.02 for a_, b_ in zip(d4, d1)) and not any(a_ - b_ > 0.02 for a_, b_ in zip(d4, d1))
    material = c41["est"] >= MATERIAL or sv["lo"] > 0 or cov_ok
    if c43["lo"] > 0 and c41["lo"] > 0 and material:
        engv = "FILTERING IMPROVES NEXT-SESSION STATE"
    elif c41["hi"] < MATERIAL and sv["lo"] <= 0:
        engv = "FILTERING DOES NOT MATERIALLY IMPROVE NEXT-SESSION STATE"
    else:
        engv = "ENGINE VALUE UNIDENTIFIED"
    res["engine_value"] = engv
    res["coverage_closer"] = bool(cov_ok)
    # forms, only under PRESENT or UNIDENTIFIED
    res["form_demand"] = res["form_dynamics"] = "NOT APPLICABLE"
    h3f, h3t = Hf["H3"], H["H3"][1]
    tw4 = p4["tau_wn"]
    fx_f = [het(sb, xf)]
    fx_t = [het(sb, xt)]
    if exist != "FAST PERSISTENT STATE NOT DETECTED":
        forms = {}
        ext_f = {k_: v_[selr] for k_, v_ in ext_tr.items()}
        if "demand" in ext_tr:
            ri = RHO_GRID.index(p4["rho"])
            ti = TAU_GRID.index(p4["tau"])
            rs = [RHO_GRID[j] for j in range(max(0, ri - 1), min(len(RHO_GRID), ri + 2))]
            ts = [TAU_GRID[j] for j in range(max(0, ti - 1), min(len(TAU_GRID), ti + 2))]
            Kp, Rp, Tp = (x.ravel() for x in np.meshgrid(np.asarray(KAPPA_GRID), np.asarray(rs), np.asarray(ts), indexing="ij"))
            LL = G_.run(h3f, lambda j: fx_f + [arc(Rp[j], Tp[j], scale=(ext_f["demand"], Kp[j])), wnc(tw4)], len(Kp))[0].sum(0)
            jb = int(np.argmax(LL))
            best = {"kappa": float(Kp[jb]), "rho": float(Rp[jb]), "tau": float(Tp[jb])}
            forms["B2"] = best
            forms["B2_ll_by_kappa"] = {str(k_): float(LL[Kp == k_].max() - LL[jb]) for k_ in KAPPA_GRID}
            run("H4+B2", h3t, fx_t + [arc(best["rho"], best["tau"], scale=(ext_te["demand"], best["kappa"])), wnc(tw4)])
            addm("H4+B2", ("within",))
            d2 = ev.gain("B|within|H4+AR1", "B|within|H4+B2")
            res["B2_over_AR1"] = d2
            res["form_demand"] = ("DEMAND-SCALED SUPPORTED" if d2["lo"] > 0 and best["kappa"] > 0 else
                                  "PLAIN SUPPORTED" if d2["hi"] < EQUIV else "FORM UNIDENTIFIED")
        else:
            res["form_demand"] = "NOT TESTABLE (no demand ratings)"
        tg = np.asarray(TAU_GRID)
        LL = G_.run(h3f, lambda j: fx_f + [arc(1.0, tg[j]), wnc(tw4)], len(tg))[0].sum(0)
        forms["SRI"] = {"rho": 1.0, "tau": float(tg[int(np.argmax(LL))])}
        run("H4+SRI", h3t, fx_t + [arc(1.0, forms["SRI"]["tau"]), wnc(tw4)])
        Ptr4f = Ptr4[selr]
        Flag = lag_feats(at_f, st_f, Ptr4f)
        Sf = (o4tr["m"] + beta * at_tr.x + H["H3"][0] + o4tr["cm"])[selr]
        gl = T.fit_offset(Flag, Sf, o4tr["v"][selr], *items_row(it2, at_f), at_f.y)
        forms["LAG3"] = [float(x) for x in gl]
        hl = lag_feats(at_te, st_te, runs["H4"]["P"]) @ gl
        run("H4+LAG3", h3t + hl, fx_t + [wnc(tw4)])
        t2 = np.asarray((0.1, 0.2, 0.3, 0.5, 0.8))
        R1, R2, T1, T2 = (x.ravel() for x in np.meshgrid(np.asarray(RHO1_2TS), np.asarray(RHO2_2TS), t2, t2, indexing="ij"))
        LL = G_.run(h3f, lambda j: fx_f + [arc(R2[j], T2[j]), arc(R1[j], T1[j]), wnc(tw4)], len(R1))[0].sum(0)
        jb = int(np.argmax(LL))
        forms["2TS"] = {"rho1": float(R1[jb]), "tau1": float(T1[jb]), "rho2": float(R2[jb]), "tau2": float(T2[jb])}
        run("H4+2TS", h3t, fx_t + [arc(R2[jb], T2[jb]), arc(R1[jb], T1[jb]), wnc(tw4)])
        rbg = np.asarray(RHOB_GRID)
        LL = G_.run(h3f, lambda j: fx_f + [arc(p4["rho"], p4["tau"], carry=rbg[j]), wnc(tw4)], len(rbg))[0].sum(0)
        forms["DECAY"] = {"rho_b": float(rbg[int(np.argmax(LL))]), "ll": {str(r_): float(v_ - LL.max()) for r_, v_ in zip(rbg, LL)}}
        info["forms"] = forms
        fn = {"AR1": "H4+AR1", "SRI": "H4+SRI", "LAG3": "H4+LAG3", "2TS": "H4+2TS"}
        for nm in ("H4+SRI", "H4+LAG3", "H4+2TS"):
            addm(nm, ("within",))
        cmp_ = {}
        win_ = None
        for f1, n1 in fn.items():
            others = [f2 for f2 in fn if f2 != f1]
            cmp_[f1] = {f2: ev.gain(f"B|within|{fn[f2]}", f"B|within|{n1}") for f2 in others}
            if f1 == "AR1":
                ok = all(cmp_[f1][f2]["lo"] > 0 for f2 in ("SRI", "LAG3")) and cmp_[f1]["2TS"]["hi"] < EQUIV
            else:
                ok = all(cmp_[f1][f2]["lo"] > 0 for f2 in others)
            if ok:
                win_ = f1
        res["form_comparisons"] = cmp_
        res["form_dynamics"] = f"{win_} SUPPORTED" if win_ else "AR FORM UNIDENTIFIED"
        log(f"   forms: {res['form_demand']} | {res['form_dynamics']}")
    if cp.batch:
        st_nb = T.Struct(at_f, None if quiz_tr is None else quiz_tr[selr], False)
        p_nb, _, _ = G_.ar(h3f, fx_f, SEED + 70, st=st_nb)
        info["ar1_per_attempt"] = p_nb
        st_te_nb = T.Struct(at_te, extras_for(cp, at_te)[1], False)
        run("H4+AR1-nb", h3t, fx_t + [arc(p_nb["rho"], p_nb["tau"]), wnc(p_nb["tau_wn"])], st=st_te_nb)
        ss = within & st_te.same_sub_prev
        for k_, msk in (("same_sub", ss), ("next_sub", within & ~st_te.same_sub_prev)):
            ev.add(f"B|{k_}|H4", Mx(P["H4"], y, g, nl, msk))
            ev.add(f"B|{k_}|H4+AR1-nb", Mx(P["H4+AR1-nb"], y, g, nl, msk))
            ev.add(f"B|{k_}|H4+AR1", Mx(P["H4+AR1"], y, g, nl, msk))
        res["batch"] = {k_: {"per_attempt_ar1": ev.gain(f"B|{k_}|H4", f"B|{k_}|H4+AR1-nb"),
                             "batch_blind_ar1": ev.gain(f"B|{k_}|H4", f"B|{k_}|H4+AR1")} for k_ in ("same_sub", "next_sub")}
        res["counts"]["same_sub"] = int(ss.sum())
    if full:
        res["T4"] = t4_split(cp, fit, at_te, st_te, H, sb, arp, P, runs, ev, run)
        res["engine_reading"] = engine_reading(cp, fit, at_tr, st_tr, at_te, st_te, ev)
    return res, P


def t4_split(cp, fit, at_te, st_te, H, sb, arp, P, runs, ev, run):
    K = fit["K"]
    o = T.run_joint(at_te, fit["pr0"], fit["itg"], K)
    P["L1"] = o["P"]
    P["L2"] = P["C2g"]
    run("L4", H["mem"][1])
    run("L5", H["H3"][1])
    p4 = arp["H4"]
    sp = [het(sb, at_te.x), arc(p4["rho"], p4["tau"]), wnc(p4["tau_wn"])]
    run("LOO-mem", H["loomem"][1], sp)
    run("LOO-proc", H["mem"][1], sp)
    ladder = [("L0", "CLIM"), ("L1", "L1"), ("L2", "L2"), ("L3", "H0-plain"), ("L4", "L4"), ("L5", "L5"), ("L6", "H4"),
              ("L7", "H4+AR1")]
    y, g, nl = at_te.y, at_te.l, at_te.nl
    al = np.ones(at_te.n, bool)
    for nm, src in ladder + [("LOO-mem", "LOO-mem"), ("LOO-proc", "LOO-proc"), ("LOO-het", "H3+AR1")]:
        ev.add(f"T4|{nm}", Mx(P[src], y, g, nl, al))
    out = {}
    for k in ("brier", "logloss"):
        tot = ev.gain("T4|L0", "T4|L7", k)
        inc = {}
        for (a_, _), (b_, _) in zip(ladder[:-1], ladder[1:]):
            inc[b_] = {"gain": ev.gain(f"T4|{a_}", f"T4|{b_}", k)}
        tot_pt = ev.pt["T4|L0"][k] - ev.pt["T4|L7"][k]
        dr_tot = np.array([d0[k] - d7[k] for d0, d7 in zip(ev.dr["T4|L0"], ev.dr["T4|L7"])])
        for (a_, _), (b_, _) in zip(ladder[:-1], ladder[1:]):
            d = np.array([x[k] - z[k] for x, z in zip(ev.dr[f"T4|{a_}"], ev.dr[f"T4|{b_}"])]) / dr_tot
            lo_, hi_ = np.percentile(d, [2.5, 97.5])
            inc[b_]["share"] = {"est": float((ev.pt[f"T4|{a_}"][k] - ev.pt[f"T4|{b_}"][k]) / tot_pt), "lo": float(lo_), "hi": float(hi_)}

        def grp(names):
            d = sum(np.array([x[k] - z[k] for x, z in zip(ev.dr[f"T4|{p_}"], ev.dr[f"T4|{q_}"])])
                    for p_, q_ in names) / dr_tot
            est = sum(ev.pt[f"T4|{p_}"][k] - ev.pt[f"T4|{q_}"][k] for p_, q_ in names) / tot_pt
            lo_, hi_ = np.percentile(d, [2.5, 97.5])
            return {"est": float(est), "lo": float(lo_), "hi": float(hi_)}
        out[k] = {"total_L0_to_L7": tot, "increments": inc,
                  "slow_share": grp([("L0", "L1"), ("L1", "L2"), ("L2", "L3")]),
                  "fast_share": grp([("L3", "L4"), ("L4", "L5"), ("L6", "L7")]),
                  "learner_dynamics_share": grp([("L5", "L6")]),
                  "loo_drop_from_L7": {nm: ev.gain(f"T4|{nm}", "T4|L7", k) for nm in ("LOO-mem", "LOO-proc", "LOO-het")}
                  | {"LOO-M": ev.gain("T4|L6", "T4|L7", k)}}
    return out


def engine_reading(cp, fit, at_tr, st_tr, at_te, st_te, ev):
    K, c0 = fit["K"], fit["c0"]
    o = T.run_beta_M(at_tr, c0, K, st_tr)
    ir = (c0.a[at_tr.i], c0.b[at_tr.i], c0.c[at_tr.i], c0.d[at_tr.i])
    p_, _, _ = fit_ar_layer(at_tr, st_tr, o["S_eq"], o["V_eq"], ir, None, SEED + 80)
    spec = ar_spec(p_)
    y, g, nl = at_te.y, at_te.l, at_te.nl
    base = T.run_beta_M(at_te, c0, K, st_te)["P"]
    ab = T.run_beta_M(at_te, c0, K, st_te, spec)["P"]
    fl = T.run_beta_M(at_te, c0, K, st_te, spec, filtered=True)["P"]
    res = {"ar1": p_}
    for nm, Pv in (("C0", base), ("C0+AR1", ab), ("C0+AR1-filt", fl)):
        for k_, msk in (("within", st_te.within), ("restricted", st_te.restricted), ("nextfirst", st_te.next_first)):
            ev.add(f"E|{k_}|{nm}", Mx(Pv, y, g, nl, msk, risks=(0.20,) if k_ == "nextfirst" else ()))
    gw = ev.gain("E|within|C0", "E|within|C0+AR1")
    gr = ev.gain("E|restricted|C0", "E|restricted|C0+AR1")
    res["gain_within"], res["gain_restricted"] = gw, gr
    res["existence"] = ("FAST PERSISTENT STATE NOT DETECTED" if gw["lo"] <= 0 else
                        "FAST PERSISTENT STATE PRESENT" if gr["lo"] > 0 and int(st_te.restricted.sum()) >= MIN_RESTRICTED
                        else "FAST PERSISTENT STATE UNIDENTIFIED")
    c43 = ev.gain("E|nextfirst|C0+AR1", "E|nextfirst|C0+AR1-filt")
    c41 = ev.gain("E|nextfirst|C0", "E|nextfirst|C0+AR1-filt")
    sv = ev.gain("E|nextfirst|C0", "E|nextfirst|C0+AR1-filt", "unneeded_0.2")
    res["next_session"] = {"filtered_vs_absorbed": c43, "filtered_vs_baseline": c41, "items_saved": sv}
    if c43["lo"] > 0 and c41["lo"] > 0 and (c41["est"] >= MATERIAL or sv["lo"] > 0):
        res["engine_value"] = "FILTERING IMPROVES NEXT-SESSION STATE"
    elif c41["hi"] < MATERIAL and sv["lo"] <= 0:
        res["engine_value"] = "FILTERING DOES NOT MATERIALLY IMPROVE NEXT-SESSION STATE"
    else:
        res["engine_value"] = "ENGINE VALUE UNIDENTIFIED"
    return res


# ---------------------------------------------------------------- one corpus, end to end

def clim(data, at):
    A = data.df.drop_duplicates("attempt").sort_values("attempt")
    tr = ~data.test_l[A.l.to_numpy()]
    lg, _, _ = e2e.difficulty(A.i.to_numpy(), A.y.to_numpy().astype(np.int64), tr)
    out = np.empty(int(A.attempt.max()) + 1)
    out[A.attempt.to_numpy()] = 1 / (1 + np.exp(-lg.astype(float)))
    return out[at.gid]


def run_corpus(cp: Corpus, do_a=True, do_b=True, full=True):
    data = cp.data
    log(f"{cp.name}: {len(data.df):,} rows, {data.df.attempt.nunique():,} attempts, {len(data.uid):,} learners, "
        f"{data.I:,} items, {int(data.df.k.max()) + 1} skills")
    fit = fit_base(cp)
    K = fit["K"]
    at_te = S.Attempts(data, data.rows("test"))
    ext_te, quiz_te = extras_for(cp, at_te)
    st_te = T.Struct(at_te, quiz_te, cp.batch)
    h0te = T.run_joint(at_te, fit["pr2"], fit["it2"], K)
    ref = S.run_gauss(at_te, fit["pr2"], fit["it2"], K)["P"]
    err = float(np.abs(h0te["P"] - ref).max())
    assert err < 1e-9, f"run_joint differs from run_gauss by {err}"
    log(f"TEST: {at_te.n:,} attempts, {at_te.nl:,} learners; run_joint = run_gauss to {err:.1e}")
    ev = Boot(at_te.nl, SEED)
    preds = {"C2": h0te["P"], "CLIM": clim(data, at_te)}
    res = {"data": {"rows": int(len(data.df)), "attempts": int(data.df.attempt.nunique()), "learners": int(len(data.uid)),
                    "items": int(data.I), "skills": K, "test_attempts": int(at_te.n), "test_learners": int(at_te.nl),
                    "sessions_test": int(st_te.sess.max()) + 1, "rank": cp.rank},
           "exactness": {"run_joint_vs_run_gauss": err}}
    if do_a:
        rec, info, gstate_te = part_a(cp, fit, at_te, ev, preds)
        gfin = info.pop("_gfinal_tr")
        counts, cov = eval_a(at_te, preds, rec, fit["it2"], fit["itg"], ev,
                             {"C2": (h0te["m"], h0te["v"]), "C2g": gstate_te}, fit["c0"])
        ra = verdict_a(ev, counts)
        ra["fit"] = info
        ra["windows"] = cov
        res["A"] = ra
        log(f"== Part A: {ra['A1']} | A1-global {ra['A1-global']} | {ra['A2']} | {ra['double_counting']} | "
            f"{ra['learner_information']} | share {ra['share_of_C2_cold']['A1']}")
    else:
        gtr = T.run_joint(fit["at_tr"], fit["prg"], fit["itg"], K, record_g=True)
        gfin = gtr["g_final"]
        preds["C2g"] = T.run_joint(at_te, fit["prg"], fit["itg"], K)["P"]
    if do_b:
        rb, _ = part_b(cp, fit, at_te, st_te, ext_te, h0te, ev, gfin, preds, full=full)
        res["B"] = rb
        log(f"== Part B: {rb['existence']} | {rb['form_demand']} | {rb['form_dynamics']} | {rb['engine_value']} | "
            f"{rb['within_session_value']}; H4+AR1 within {rb['gain_ar1_by_layer']['H4']['within']}")
    return res


# ---------------------------------------------------------------- synthetic worlds

KINDS = ("NULL", "I", "AR-L", "AR-S", "ARD", "MEM", "ADAPT", "HET", "LXI", "BEH", "BATCH", "TWO")
FAST = {"AR-L": [(0.8, 0.6)], "AR-S": [(0.8, 0.35)], "ARD": [(0.8, 0.5)], "TWO": [(0.5, 0.45), (0.97, 0.35)]}


def world(kind, seed, L=2000):
    rng = np.random.default_rng(SEED + 1000 * KINDS.index(kind) + seed)
    K, per = 30, 12
    beta_k = rng.normal(-0.6, 0.6, K)
    I = K * per
    skill_of = np.repeat(np.arange(K), per)
    b = beta_k[skill_of] + rng.normal(0, 0.7, I)
    a = np.exp(rng.normal(0, 0.25, I))
    is_mc = rng.random(I) < 0.5
    c = np.where(is_mc, rng.uniform(0.1, 0.3, I), rng.uniform(0.02, 0.08, I))
    dd = 1 - rng.uniform(0, 0.04, I)
    dem = rng.normal(0, 1, I)
    if kind == "I":
        Sig = 1.2 * np.eye(K)
    else:
        lam = rng.normal(0.85, 0.1, K)
        Sig = np.outer(lam, lam) + 0.48 * np.eye(K)
    ch = np.linalg.cholesky(Sig)
    items_of = [np.nonzero(skill_of == k)[0] for k in range(K)]
    by_b = [it[np.argsort(b[it])] for it in items_of]
    fast = FAST.get(kind, [])
    rows = {k_: [] for k_ in ("u", "i", "k", "y", "t", "o", "hint", "assign", "mastery")}
    aid = asg = 0
    for u in range(L):
        th = ch @ rng.normal(size=K)
        rate, vf = 0.15, E.V0
        if kind == "HET":
            rate = max(0.0, rng.normal(0.15, 0.12))
            vf = E.V0 * math.exp(rng.uniform(-math.log(3), math.log(3)))
        pool = items_of
        eli = {}
        if kind == "LXI":
            pool = [rng.choice(it, 4, replace=False) for it in items_of]
            for it in pool:
                for i in it:
                    eli[int(i)] = rng.normal(0, 0.6)
        gain = np.zeros(K)
        last = np.full(K, -1.0)
        seen_t = {}
        order = rng.permutation(K)
        nxt, seen = 0, []
        t = 0.0
        hint_prev, y_prev = 0, None
        for _ in range(int(rng.integers(18, 31))):
            t += math.exp(rng.uniform(math.log(2 * 3600), math.log(20 * 86400)))
            sk = []
            for _ in range(int(rng.integers(1, 3))):
                if nxt < K and (not seen or rng.random() < 0.6):
                    k = int(order[nxt])
                    nxt += 1
                    seen.append(k)
                else:
                    k = int(rng.choice(seen))
                sk.append(k)
            natt = int(rng.integers(8, 17))
            runs = [sk[0]] * (natt if len(sk) == 1 else natt // 2) + ([sk[1]] * (natt - natt // 2) if len(sk) > 1 else [])
            dl = [rng.normal(0, tau) for _, tau in fast]
            tt = t
            prev_i, y_prev, hint_prev = None, None, 0
            streak, cur_run, run_k = 0, -1, None
            bshift = 0.0
            j = 0
            ri = 0
            while ri < len(runs):
                k = runs[ri]
                if k != run_k:
                    run_k, streak, prev_in_run = k, 0, None
                    asg += 1
                plist = pool[k]
                if kind == "MEM" and prev_i is not None and skill_of[prev_i] == k and rng.random() < 0.4:
                    i = prev_i
                elif kind == "ADAPT" and prev_in_run is not None:
                    srt = by_b[k]
                    third = max(1, len(srt) // 3)
                    i = int(rng.choice(srt[:third] if prev_in_run == 0 else srt[-third:]))
                else:
                    i = int(rng.choice(plist))
                if kind == "BATCH":
                    if j % 3 == 0:
                        tt += rng.uniform(60, 180)
                        bshift = rng.normal(0, 0.6)
                else:
                    tt += rng.uniform(20, 120)
                if last[k] >= 0:
                    gain[k] *= (1 + vf * (tt - last[k]) / 86400) ** (-0.5)
                te = th[k] + gain[k] + eli.get(i, 0.0)
                if kind == "MEM" and i in seen_t:
                    te += 1.2 * math.exp(-(tt - seen_t[i]) / 3600 / 6)
                if kind == "ARD":
                    te += math.exp(0.5 * dem[i]) * dl[0]
                else:
                    te += sum(dl)
                if kind == "BATCH":
                    te += bshift
                P = c[i] + (dd[i] - c[i]) / (1 + math.exp(-a[i] * (te - b[i])))
                yv = int(rng.random() < P)
                if kind == "BEH":
                    ph = 0.08 + 0.35 * (0 if y_prev is None else 1 - y_prev) + 0.30 * hint_prev
                    hv = int(rng.random() < ph)
                    if hv and rng.random() < 0.8:
                        yv = 0
                else:
                    hv = int(rng.random() < 0.1)
                for r_, (rho, tau) in enumerate(fast):
                    dl[r_] = rho * dl[r_] + rng.normal(0, tau * math.sqrt(1 - rho * rho))
                gain[k] += rate
                last[k] = tt
                seen_t[i] = tt
                for key, val in zip(rows, (u, i, k, yv, tt, aid, hv, asg, int(kind == "ADAPT"))):
                    rows[key].append(val)
                aid += 1
                j += 1
                prev_i, y_prev, hint_prev, prev_in_run = i, yv, hv, yv
                streak = streak + 1 if yv else 0
                if kind == "ADAPT" and (streak >= 3 or j >= 16):
                    nxt_run = [x for x in range(ri + 1, len(runs)) if runs[x] != k]
                    if not nxt_run:
                        break
                    ri = nxt_run[0]
                    continue
                ri += 1
    ar = {k_: np.asarray(v_) for k_, v_ in rows.items()}
    group = np.where(is_mc, 0, 1)
    data = C.Data(ar["u"], ar["i"], ar["k"], ar["y"].astype(float), ar["t"], ar["o"], is_mc, np.where(is_mc, 4, 0), group,
                  np.array([f"st{kind}{seed}-{u}" for u in range(L)]))
    ext = {"hint": ar["hint"].astype(float), "assign": ar["assign"].astype(float), "mastery": ar["mastery"].astype(float)}
    return Corpus(f"world {kind} seed {seed}", data, ext, demand=dem, batch=(kind == "BATCH"), rank=2, synthetic=True)


def floor_checks(kind, res, planted):
    ck = {}
    B = res.get("B")
    if kind in ("NULL", "I") and "A" in res:
        A = res["A"]
        if kind == "NULL":
            sh = A["share_of_C2_cold"]["A1"]
            ck["A_share"] = sh["est"] >= 0.5 and sh["lo"] > 0
            ck["A_beats_der"] = A["A1_over_der_cold"]["lo"] > 0
            ck["A_leak_detected"] = A["leak_minus_A1_cold"]["lo"] > 0
            ck["A2_orth_not_overconfident"] = all(A["intervals"]["A2-orth"][w]["label"] != "OVER-CONFIDENT" for w in ("cold", "warm"))
        else:
            ck["A_no_false_learner_specific"] = not A["learner_information"].startswith("LEARNER-SPECIFIC")
    if B is None:
        return ck
    ex, eng = B["existence"], B["engine_value"]
    if kind in ("NULL", "MEM", "ADAPT", "HET", "LXI", "BEH", "BATCH"):
        ck["Bex_no_false_present"] = ex != "FAST PERSISTENT STATE PRESENT"
        ck["Beng_no_false_engine"] = eng != "FILTERING IMPROVES NEXT-SESSION STATE"
    elif kind in ("AR-L", "AR-S"):
        r0, r4 = B["fit"]["ar1"]["H0"]["rho"], B["fit"]["ar1"]["H4"]["rho"]
        ck["Bex_present"] = ex == "FAST PERSISTENT STATE PRESENT"
        ck["Bform_rho_H0"] = abs(r0 - planted) <= 0.1
        ck["Bform_rho_H4"] = abs(r4 - planted) <= 0.15
        ck["Bform_no_demand_scaled"] = not B["form_demand"].startswith("DEMAND-SCALED")
        ck["Bform_dynamics_not_wrong"] = B["form_dynamics"] not in ("SRI SUPPORTED", "LAG3 SUPPORTED", "2TS SUPPORTED")
        if kind == "AR-L":
            ck["Beng_engine"] = eng == "FILTERING IMPROVES NEXT-SESSION STATE"
            ck["Beng_material"] = B["within_session_value"] == "M MATERIAL WITHIN SESSION"
    elif kind == "ARD":
        ck["Bex_present"] = ex == "FAST PERSISTENT STATE PRESENT"
        ck["Bform_demand_scaled"] = B["form_demand"] == "DEMAND-SCALED SUPPORTED" and B["fit"]["forms"]["B2"]["kappa"] > 0
    elif kind == "TWO":
        ck["Bex_present"] = ex == "FAST PERSISTENT STATE PRESENT"
        ck["Bform_not_ar1"] = B["form_dynamics"] != "AR1 SUPPORTED"
    return ck


FLOOR = [("NULL", 0), ("NULL", 1), ("I", 0), ("AR-L", 0), ("AR-S", 0), ("ARD", 0), ("MEM", 0), ("ADAPT", 0), ("ADAPT", 1),
         ("HET", 0), ("LXI", 0), ("BEH", 0), ("BATCH", 0), ("TWO", 0)]


def synthetic(which=None, out_name="synthetic.json", seed_offset=0, L=2000, out_dir=None):
    f = (out_dir or OUT) / out_name
    out = json.loads(f.read_text()) if f.exists() else {"worlds": []}
    done = {(w["world"], w["seed"]) for w in out["worlds"]}
    for kind, sd in FLOOR:
        if which and kind not in which:
            continue
        if (kind, sd) in done:
            continue
        cp = world(kind, sd + seed_offset, L)
        do_a = kind in ("NULL", "I")
        res = run_corpus(cp, do_a=do_a, do_b=kind != "I", full=False)
        planted = FAST.get(kind, [(None, None)])[0][0]
        ck = floor_checks(kind, res, planted)
        rec = {"world": kind, "seed": sd, "checks": ck, "result": res}
        out["worlds"].append(rec)
        log(f"   {kind} seed {sd}: checks {ck}")
        f.parent.mkdir(exist_ok=True)
        f.write_text(json.dumps(out, indent=1, default=float) + "\n")
        del cp
        gc.collect()
    summarise_floor(out)
    f.write_text(json.dumps(out, indent=1, default=float) + "\n")


def summarise_floor(out):
    allck = [v for w in out["worlds"] for v in w["checks"].values()]
    out["complete"] = {(k, s) for k, s in FLOOR} <= {(w["world"], w["seed"]) for w in out["worlds"]}
    for part in ("A", "Bex", "Bform", "Beng"):                         # CHANGE 4: per verdict family
        cks = [v for w in out["worlds"] for k, v in w["checks"].items() if k.split("_")[0] == part]
        out[f"part_{part}_passes"] = bool(all(cks)) if cks else None
    out["passes"] = bool(all(allck))
    log(f"FLOOR {'PASSES' if out['passes'] else 'FAILS'} (A {out['part_A_passes']}, existence {out['part_Bex_passes']}, "
        f"form {out['part_Bform_passes']}, engine value {out['part_Beng_passes']}); complete {out['complete']}")


# ---------------------------------------------------------------- real corpora and stop/go

def floor_record():
    f = OUT / "synthetic.json"
    if not f.exists():
        return {"part_A_passes": False, "part_Bex_passes": False, "part_Bform_passes": False, "part_Beng_passes": False,
                "complete": False}
    s = json.loads(f.read_text())
    return {k: s.get(k) for k in ("part_A_passes", "part_Bex_passes", "part_Bform_passes", "part_Beng_passes", "complete",
                                  "passes")}


def mark_uncalibrated(res, fl):
    if "A" in res and not fl.get("part_A_passes"):
        for k in ("A1", "A1-global", "A1_guard_M2", "A2", "double_counting", "learner_information"):
            if not res["A"][k].endswith("(UNCALIBRATED)"):
                res["A"][k] += " (UNCALIBRATED)"
    fam = {"part_Bex_passes": ("existence",), "part_Bform_passes": ("form_demand", "form_dynamics"),
           "part_Beng_passes": ("engine_value", "within_session_value")}
    if "B" in res:
        for f_, keys in fam.items():
            if not fl.get(f_):
                for k in keys:
                    res["B"][k] += " (UNCALIBRATED)"


def real(name):
    import pickle
    TMP.mkdir(exist_ok=True)
    cache = TMP / f"{name}.pkl"
    if cache is not None and cache.exists():          # the loaded corpus (raw-derived; scratchpad only)
        cp = pickle.loads(cache.read_bytes())
    else:
        cp = {"assist": load_assist, "xes": load_xes, "eedi": load_eedi}[name]()
        if cache is not None and name == "assist":
            cache.write_bytes(pickle.dumps(cp))
    if len(sys.argv) > 2 and sys.argv[2] == "load-only":
        log(f"{name} loaded: {len(cp.data.df):,} rows, {len(cp.data.uid):,} learners")
        return
    smoke = int(sys.argv[2].split("=")[1]) if len(sys.argv) > 2 and sys.argv[2].startswith("smoke=") else 0
    if smoke:          # a crash test of the code path on 1 learner in `smoke`; its numbers are not read or kept
        cp.data = CP.subsample(cp.data, np.array([hsh(u, smoke, "smoke") == 0 for u in cp.data.uid]))
        cp.name += "-smoke"
        res = run_corpus(cp)
        (TMP / f"smoke-{name}.json").write_text(json.dumps(res, default=float))
        print("SMOKE DONE", flush=True)
        return
    res = run_corpus(cp)
    while not floor_record().get("complete"):        # CHANGE 7 (computation only): wait for the merged floor
        log("waiting for the synthetic floor to finish")
        time.sleep(120)
    fl = floor_record()
    res["floor"] = fl
    mark_uncalibrated(res, fl)
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    log(f"wrote out/{name}.json")


def variant_passes(A, v):
    """Part A pass for a variant: share of C2's cold gain lower bound >= 0.5, calibration guard, and not
    worse than C0 at the next attempt."""
    sh = A["share_of_C2_cold"][v]
    return bool(sh["lo"] >= 0.5 and A["calibration_guard"][v] and A["gain_vs_C0_all"][v]["hi"] >= 0)


def stopgo():
    fl = json.loads((OUT / "synthetic.json").read_text())
    R = {n: json.loads((OUT / f"{n}.json").read_text()) for n in ("assist", "xes", "eedi") if (OUT / f"{n}.json").exists()}
    a = R["assist"]["B"]
    no_m_clean = all(v for w in fl["worlds"] for k, v in w["checks"].items() if k == "Bex_no_false_present")
    rep = {}
    for n in ("xes", "eedi"):
        if n in R:
            b = R[n]["B"]
            rep[n] = bool(b["gain_ar1_by_layer"]["H4"]["within"]["est"] > 0 and b["fit"]["ar1"]["H4"]["rho"] > 0)
    ex = a["existence"]
    present = ex == "FAST PERSISTENT STATE PRESENT"
    engine = a["engine_value"] == "FILTERING IMPROVES NEXT-SESSION STATE"
    cond = {"assist_present": present, "floor_no_m_worlds_clean": no_m_clean, "direction_replicates": rep,
            "assist_filtering_improves": engine, "assist_dynamics": a["form_dynamics"]}
    if present and no_m_clean and any(rep.values()) and engine:
        dec = "GO" if a["form_dynamics"].endswith("SUPPORTED") and "UNCALIBRATED" not in a["form_dynamics"] else "GO-GENERIC"
    elif ex.startswith("FAST PERSISTENT STATE NOT DETECTED"):
        dec = "NO-GO (LOCAL DEPENDENCE EXPLAINED)"
    elif present and not engine:
        dec = "NO-GO (NOT ENGINE-RELEVANT)"
    else:
        dec = "HOLD (UNIDENTIFIED)"
    order = ["A1-global", "A1", "A2-orth", "C2g"]
    pa = {v: {n: variant_passes(R[n]["A"], v) for n in R if "A" in R[n]} for v in order}
    first = next((v for v in order if pa[v] and all(pa[v].values())), None)
    nums = {}
    if first:
        for n in R:
            A = R[n]["A"]
            nums[n] = {"share_of_C2_cold": A["share_of_C2_cold"][first], "cold_gain_vs_C0": A["gain_vs_C0_cold"][first],
                       "cold_auc_gain": A["auc_gain_vs_C0_cold"][first], "items_saved_20": A["items_saved"][first]["0.2"],
                       "all_gain_vs_C0": A["gain_vs_C0_all"][first]}
    reason = {"GO": "every registered condition holds",
              "GO-GENERIC": "every condition holds; the dynamics form is not identified",
              "NO-GO (LOCAL DEPENDENCE EXPLAINED)": "ASSISTments reads NOT DETECTED behind the control stack",
              "NO-GO (NOT ENGINE-RELEVANT)": "persistence present; filtering does not improve the next-session state",
              }.get(dec, "")
    if dec.startswith("HOLD"):
        reason = ("the conditions are not met as registered: " +
                  ("ASSISTments existence reads '" + ex + "'" if not present else "") +
                  ("; ASSISTments engine value reads '" + a["engine_value"] + "'" if not engine else ""))
    out = {"momentary_state_component": dec, "reason": reason, "conditions": cond,
           "note": "a detected M is an unobserved fast state or process, not fatigue, attention or affect",
           "g_layer": {"cheapest_passing_variant": first, "passes": pa, "numbers": nums,
                       "note": "g is a forecasting coordinate in p(X), not a learner mechanism"},
           "floor": {k: fl.get(k) for k in ("part_A_passes", "part_Bex_passes", "part_Bform_passes", "part_Beng_passes")}}
    (OUT / "stop-go.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    log(f"stop/go: {dec}; g layer: {first}")


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "synthetic":            # synthetic [part-name world ...]: parts run in parallel, then merge
        if len(sys.argv) > 2:
            synthetic(sys.argv[3:], out_name=f"synthetic-{sys.argv[2]}.json", out_dir=TMP)
        else:
            synthetic()
    elif what == "merge":
        parts = sorted(TMP.glob("synthetic-*.json"))
        out = {"worlds": [w for p_ in parts for w in json.loads(p_.read_text())["worlds"]]}
        key = {(k, s_): i for i, (k, s_) in enumerate(FLOOR)}
        out["worlds"].sort(key=lambda w: key[(w["world"], w["seed"])])
        summarise_floor(out)
        OUT.mkdir(exist_ok=True)
        (OUT / "synthetic.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    elif what == "stopgo":
        stopgo()
    elif what == "dev":         # machinery debugging on other seeds; written to the scratchpad, not out/
        synthetic(sys.argv[3:] or None, out_name="dev.json", seed_offset=100, L=int(sys.argv[2]), out_dir=TMP)
    else:
        real(what)
