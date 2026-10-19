"""Longitudinal compounding of the grader's learner-context edge (Paper VI, placeholder 4).

THE QUESTION. Paper VI (`research/article/attainment-bias-in-llm-grading.md` §6.2, release
`ai-grader-reliability-2026`) argues that passing the engine's belief about a learner into the grader
closes the belief -> grade -> belief loop early, and says "confidence compounds", "the direction of the
compounding is not in doubt even where its magnitude is", and that a simulation over a synthetic
cohort is the realistic route to bounding it (placeholder 4). This study is that simulation. No model
is called. The grader is a statistical stand-in whose every parameter is MEASURED, per model, from the
attainment-swap runs of `studies/measurement/grader-attainment-prior/` (four models, 300 JorGPT cases,
control / true label / swapped label on identical work).

If the grader is shown the engine's current belief and its grade then updates that belief:
  (a) does belief diverge further from true ability over a term with the edge than without it?
  (b) does it change misclassification at a mastery threshold (false 'not mastered' for strong
      learners, false 'mastered' for weak) by the end of the term?
  (c) does the loop have a stable fixed point or run away? Analytically where possible: the loop gain
      is label effect x belief sensitivity to one grade;
  (d) the false-label cost: a strong learner who starts with a wrong low belief -- how many items until
      the belief recovers, with and without the edge?

DATA READ. Two inputs, both outside the repo.
  * The per-case dumps of `grader-attainment-prior` (`--mode attainment-swap`, one JSON per model,
    session scratchpad `grader-vi/swap-*.json`): JorGPT teacher marks, held-out learner labels and the
    model's three scores per case. They are derived from JorGPT (CC BY 4.0, `jorgpt-answers` in
    data/data-sources.json) and stay in the scratchpad. Only fitted parameters go to out/params.json.
  * JorGPT itself (`JORGPT_DIR`, file dataset_en.csv), read for the cohort's shape only: the mean and
    between-learner sd of learner-mean teacher marks (sampling variance removed), the within-learner sd
    of a teacher mark, and the number of graded responses per learner (the term length).
  Neither enters the repo. `params` writes out/params.json (aggregates); `floor` and `run` read only
  that file, so the simulation reproduces without the dumps.

THE GRADER STAND-IN (per model m; 0-10 mark scale, as JorGPT):

    g = clip(round( a_m + b_m h + u_i + e  +  EDGE * [ delta_m + gamma_m (l - 5) + eta_m (h - 5) ] ), 0, 10)

  h        the teacher's mark the work deserves (simulated, below);
  a, b     the label-blind calibration: OLS of the control score on the teacher mark, all 300 cases;
  e        per-grade error, N(0, sigma_m): the within-learner residual sd of that fit. Every simulated
           item is a fresh answer, so the case-level error and the call-to-call noise enter the same
           way; the call-to-call part is reported (Gemini's measured per-answer pass sd 0.18 from the
           pooling run; for every model an upper bound, the edge regression's residual sd / sqrt 2);
  u_i      a persistent learner-level grader error, N(0, sigma_u,m): the learner-mean residual variance
           with its sampling part removed (method of moments, floored at 0);
  l        the label shown: the engine's current belief for the skill being graded, x 10, to one
           decimal ("Current attainment for this learner across this course: 6.0/10", the harness's
           sentence);
  delta    the shift when any label is shown, at l = 5;
  gamma    THE LABEL EFFECT: grade points per label point. Fitted with eta and delta by OLS of
           (arm score - control score) on (l - 5) and (h - 5), stacking the true-label and the
           swapped-label arm (600 rows). The swap makes the label vary on identical work, so gamma is
           the causal slope the swapped arm identifies. Checked against the within-case estimate
           sum((true - swapped)(l_t - l_s)) / sum((l_t - l_s)^2), reported;
  eta      whether the label also changes how much the grade follows the work (eta < 0: the label
           pulls the grade toward itself rather than shifting it).
  Measured labels lie in [0, 4) and [6, 10]; the loop mostly shows labels near 5. Linear
  interpolation across the middle is an ASSUMPTION; a quadratic term is reported, not used.
  Every parameter's uncertainty is carried by a learner-cluster bootstrap of the dumps (resampling
  learners within tail, the unit the label was assigned to; B = 200), each draw refitted and
  re-simulated with a fresh cohort.

THE COHORT. N learners, true ability theta_i ~ N(mu_theta, sd_theta) clipped to [0, 10], with
mu_theta, sd_theta from JorGPT (above). True mastery pi_i = theta_i / 10. Each item's deserved mark
h_it = clip(round(theta_i + N(0, sd_item)), 0, 10), sd_item JorGPT's within-learner sd. A term is T
items (JorGPT's median responses per learner), interleaved over K = 4 skills, one item every 2.5 days,
so a skill is revisited every 10 days. One ability per learner (no skill-specific deviation: none is
measured on this corpus). "Strong" = theta >= 6, "weak" = theta < 4 (the attainment draw's tails);
"truly mastered" = pi >= tau = 0.6.

THE ENGINE (two update rules; `docs/specs/SYSTEM-MODEL.md` §5,
`studies/measurement/grader-eval/findings/mastery-and-inference.md`, `studies/measurement/engine-decay/`).
  E0, as shipped: each skill a Beta, starting Beta(0.5, 0.5). An AI-graded response adds
     da = M s, db = M (1 - s), s = g / 10, with mass M (primary M = 1.0, the surveyed p50 of
     AI-graded mass; sensitivity M = 3.0, MAX_EVIDENCE_MASS). Before the write the stored Beta decays
     lazily toward Beta(0.5, 0.5): alpha' = r alpha + (1 - r) 0.5, likewise beta, r = (1 + 0.1 t)^-0.5
     with t in days since that skill's last write. The read is the stored mean (no decay on read).
  E5, the recommended change (engine-decay): a learner-level general state g ~ N(m, v) on the logit
     scale, updated by every graded response (one-step Laplace/EKF update with the score as a soft
     label: p = sigmoid(m / sqrt(1 + pi v / 8)), v' = 1 / (1/v + p(1 - p)), m' = m + v'(s - p)); a skill
     starts at its first evidence at Beta(n0 p0, n0 (1 - p0)), p0 the predictive mean at that moment,
     n0 = 2, and decays toward that prior, same r. m starts at the logit of the cohort's mean no-edge
     grade / 10 (the offline-fitted mu_k), v at 1.
  The label shown is the stored mean of the skill being graded (E5: p0 for a skill not yet touched).
  The learner-level belief read at time t is the mean of the K skills' reads.

ARMS. Each simulated cohort is run twice on COMMON random numbers (same theta, h, e, u): NO EDGE
(grader blind) and EDGE (grader shown the current belief). Every estimand is EDGE minus NO EDGE, or a
ratio of the two, so the grader's label-blind miscalibration (shared by both arms) is not attributed
to the edge.

CONFIGURATIONS. Primary: E0, M = 1, continuous label, the model's measured (a, b, sigma, sigma_u).
Sensitivity, reported, carrying no headline: E0 M = 3; E5 (M = 1, n0 = 2); label granularity BANDS3
(belief < 0.4 / 0.4-0.6 / >= 0.6 shown as the low tail's mean label, 5.0, the high tail's mean label)
and BINARY (belief >= tau shown as the high tail's mean label, else the low tail's) -- the grader's
response to a band's WORDING is unmeasured, so a band is assumed to act as the tail-mean label it
stands for; CALIBRATED grader (a = 0, b = 1, sigma_u = 0: the label effect on a grader with no
label-blind miscalibration, which isolates the loop); and sigma_u = 0.

ESTIMANDS AND PRE-REGISTERED VERDICTS (all signed; intervals are the 2.5-97.5 percentiles over the
B = 200 parameter draws, each with its own cohort of 2,000; point estimates at the full-data
parameters with a cohort of 20,000).
  SPREAD (the compounding headline). A = slope(end-of-term belief on theta | EDGE) /
     slope(... | NO EDGE)   (revision 2: / slope(... | EDGE with gamma = 0); see FLOOR RECORD). A > 1: beliefs of strong and weak learners are pushed further apart than
     the work alone moves them.
       AMPLIFIES   A - 1 >= +0.02 and the interval's lower bound > 0
       DAMPS       A - 1 <= -0.02 and the interval's upper bound < 0
       NEUTRAL     the interval lies inside [-0.02, +0.02]   (revision 1: [-0.05, +0.05]; FLOOR RECORD)
       UNRESOLVED  otherwise
     Across models: the shared verdict, else MIXED-ACROSS-MODELS.
  STABILITY (c), E0 analytic. In steady state the skill's mass is n* = 1 + M / (1 - r); one grade
     moves the belief by w = M / n* per unit of s, so the LOOP GAIN per write is G = w gamma and the
     belief's deviation propagates with eigenvalue lambda_E = r + w gamma (lambda_0 = r without the
     edge). Steady-state spread multiplier from the loop alone: A_loop = (1 - r) / (1 - r - w gamma);
     runaway iff gamma >= gamma* = 1 + (1 - r) / M.
       STABLE      the 97.5th percentile of lambda_E < 1 (a fixed point exists in every draw)
       RUNAWAY     lambda_E >= 1 at the point estimate
       UNRESOLVED  otherwise
     The per-grade part (1 + eta / b) and delta's shift are reported beside A_loop as its decomposition.
  DIVERGENCE (a). dRMSE = RMSE(belief - pi | EDGE) - RMSE(... | NO EDGE) at the end of the term (also
     at items 10, 20, 30, reported).
       HARMS / HELPS / NO-CHANGE / UNRESOLVED: lower bound > +0.01 / upper bound < -0.01 / interval
       inside +-0.01 / otherwise (0.01 belief = 0.1 mark).
     Per tail (strong, weak): d|err| = |mean(belief - pi | EDGE)| - |mean(... | NO EDGE)|:
       AWAY / TOWARD / FLAT / UNRESOLVED on the same +-0.01 rule (AWAY = the edge moves that tail's
       mean belief further from its true mastery).
  MISCLASSIFICATION (b) at tau = 0.6. dFNR = change in P(belief < tau | pi >= tau) (false 'not
     mastered'); dFPR = change in P(belief >= tau | pi < tau) (false 'mastered'); dFPR_weak the same
     inside theta < 4.
       UP / DOWN / FLAT / UNRESOLVED: lower bound > +0.01 / upper bound < -0.01 / inside +-0.01 /
       otherwise (one percentage point).
  RECOVERY (d). 500 learners at theta = 7, each run four ways on common random numbers: {NO EDGE, EDGE}
     x {default start, false start}. False start, E0: every skill at Beta(0.3 n*, 0.7 n*), a belief of
     0.3 held with steady-state confidence; E5: g at m = logit 0.3, v = 0.1. Recovery item = the first
     item after which the false-start belief stays within 0.05 of the same arm's default-start belief.
     R = median recovery item | EDGE / median | NO EDGE (not recovered within the term counts as T + 1;
     the share not recovered is reported). Analytic E0 counterpart: ln(lambda_0) / ln(lambda_E).
       SLOWER / FASTER / SAME / UNRESOLVED: R - 1 >= +0.05 with lower bound > 1 / R - 1 <= -0.05 with
       upper bound < 1 / interval inside [0.95, 1.05] / otherwise.
     Items until the false-start belief first reaches tau are reported beside it.

DETECTION FLOOR (`floor`, must pass before `run`; `run` refuses otherwise). It reads the cohort's shape
from JorGPT and the draw's structure, and no score. The
instrument is the whole pipeline: synthetic dumps -> fit -> learner-cluster bootstrap -> simulate ->
verdict. Synthetic dumps keep the real draw's structure (its 300 cases: tails, learners, teacher marks,
true and swapped labels; no score is read) and replace the three scores with a planted grader:
a = 0.5, b = 0.85, case effect sd 1.4 shared by the three arms of a case, call noise sd 0.6 per score,
learner effect sd 0.33 (the parent study's floor values), rounded and clipped to 0-10. Worlds (40
replicates each, B = 100 draws, cohorts of 1,000, primary configuration):
  AMP-MEASURED  gamma = +0.10 (the measured order)           -> AMPLIFIES
  AMP-LARGE     gamma = +0.30                                -> AMPLIFIES
  DAMP          gamma = -0.10                                -> DAMPS
  NULL-SHIFT    gamma = 0, delta = +0.30 (label-blind shift) -> NEUTRAL
  NULL          gamma = 0, delta = 0, eta = 0                -> NEUTRAL
  RUNAWAY       gamma = +1.50 (> gamma* = 1.29 at M = 1)     -> stability RUNAWAY
Pass: >= 80% of replicates return the planted verdict in every world, and <= 10% of replicates in each
NULL world return AMPLIFIES or DAMPS. GAIN RECOVERY: with the planted parameters exactly (no fitting),
cohort 20,000, the simulated A - 1 must lie within 25% of the analytic A_loop - 1 for gamma = +0.10,
+0.30 and -0.10 (the analytic ignores rounding, clipping and the transient from the prior), and
|A - 1| < 0.01 at gamma = 0. A SHRINK world (gamma = 0, eta = -0.15) is reported without a pass rule:
it must read as a spread change with A_loop = 1, i.e. not a loop. These are smoke checks written and
scored by one session (the same reader wrote the instrument), and are reported as such.

FLOOR RECORD AND REVISIONS (all before any real parameter was fitted; out/params.json did not exist).
  Revision 0 (as pre-registered at a3647f5): FAILED, on three worlds, by declining or misreading, never
  by a false effect. NULL and NULL-SHIFT read UNRESOLVED in 38 and 37 of 40 (false AMPLIFIES/DAMPS 2/40
  and 3/40): at 300 cases and 33 learners the 95% interval of A has a half-width of about 0.03-0.035
  under a null (the gamma, eta and delta uncertainty together), so an equivalence band of +-0.02
  cannot be reached. RUNAWAY read STABLE in 23 of 40: the dumps' scores are clipped to 0-10, so the
  OLS label slope is attenuated (planted 1.50 fitted 1.22 on average; 0.30 -> 0.27, 0.10 -> 0.092),
  and an attenuated slope reads below gamma* = 1.29 -- the dangerous direction for a stability
  verdict. Every other world passed (AMP-MEASURED 34/40, AMP-LARGE 40/40, DAMP 32/40), and the
  gain-recovery check passed. The revision-0 floor.json is not committed; its counts are here.
  Revision 1 (the verdicts now):
    * SPREAD's NEUTRAL band widens from +-0.02 to +-0.05 (MARGIN_NEUTRAL), the instrument's measured
      null resolution. AMPLIFIES and DAMPS are unchanged (|A - 1| >= 0.02 with the interval excluding
      1) and are checked first.
    * STABILITY uses the LATENT label slope: the floor first maps planted gamma to the mean fitted
      gamma on its own calibration worlds (gamma 0, 0.1, 0.3, 0.6, 1.0, 1.5; 20 replicates each; seeds
      distinct from the floor's), and the stability verdict inverts that curve before computing
      lambda_E (point and every draw). The curve is written to out/floor.json and `run` reads it. The
      simulation itself still uses the fitted gamma (the clipping is in the simulated grader too, and
      the attenuation at the measured size is about 8%, which biases A toward 1, i.e. conservative).
  Revision 1 floor: RUNAWAY 40/40, AMP-MEASURED 34/40, AMP-LARGE 40/40, DAMP 32/40, but NULL 23/40 and
    NULL-SHIFT 19/40 NEUTRAL (the rest UNRESOLVED; false AMPLIFIES/DAMPS 2/40 and 3/40): FAILED. The
    total spread ratio carries eta's uncertainty (the label's effect on how much the grade follows
    the work) and delta's, which are per-grade effects, not feedback; a null interval reaches +-0.05
    only about half the time.
  Revision 2 (the verdicts now): the SPREAD verdict is the LOOP's multiplier, the question asked: a
    third arm runs the edge with gamma set to 0 (the same delta and eta, so the label's per-grade
    effects without any feedback through the belief), and A = slope(EDGE) / slope(EDGE, gamma = 0).
    Under gamma = 0, A = 1 exactly on common random numbers. The total change A_total =
    slope(EDGE) / slope(NO EDGE) and the per-grade part A_per_grade = slope(EDGE, gamma = 0) /
    slope(NO EDGE) are reported beside it, A_total with the same strings as `spread_total`, carrying no
    headline. SHRINK (gamma = 0, eta = -0.15) now has a pass rule: the loop verdict NEUTRAL in >= 80%.
    Margins unchanged from revision 1.
  Revision 2a (a bug, not a design change): the first `params` run printed bootstrap intervals for
    sigma_u that equalled sigma. The learner-cluster bootstrap relabelled each resampled learner with
    an f-string evaluated per ROW, so every row became its own learner: in every draw sigma (the
    per-grade error) was ~0 and sigma_u (the persistent learner error) carried the whole residual.
    gamma, delta, eta, a and b (OLS, no cluster term) were unaffected. The floor at revision 2 used
    the same faulty draws, so it was re-run after the fix before the real-parameter simulation; its
    result is the one in out/floor.json. The point fits printed by that first `params` run were
    correct and were seen (gamma 0.093 / 0.100 / 0.140 / 0.199); the run's verdict rules were already
    committed (dc32491).

WHAT THIS CANNOT SAY. It is a simulation: the delay of every outcome is a parameter of the generator
(outcome-timing tag `simulated`). The grader stand-in is linear in the label and was measured on one
corpus (JorGPT short answers) with one label sentence; band wording, other subjects and the product's
own graders are not measured. Whether Lazuli's engine would ever show the label is a design choice the
paper argues against; this bounds what the edge would do if it existed.

    python3 compounding.py params --dumps <scratch>/grader-vi/swap-*.json   # needs JORGPT_DIR
    python3 compounding.py floor --draw <scratch>/grader-vi/draw.json       # out/floor.json
    python3 compounding.py run                                              # out/results.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

from shared.seeds import arm_seed  # noqa: E402

OUT = HERE / "out"
TAU = 0.6
K = 4
DAYS_PER_ITEM = 2.5
DECAY_V = 0.1          # per day, shipped
DECAY_D = 0.5          # exponent, shipped
N0_E5 = 2.0
MARGIN_A = 0.02
MARGIN_NEUTRAL = 0.05  # revision 1: the floor's null resolution
ATTEN_GAMMAS = (0.0, 0.1, 0.3, 0.6, 1.0, 1.5)
ATTEN_REPS = 20
MARGIN_B = 0.01        # belief units (0.1 mark)
MARGIN_P = 0.01        # misclassification, one percentage point
MARGIN_R = 0.05
REC_TOL = 0.05
SHOCK_BELIEF = 0.3
STRONG, WEAK = 6.0, 4.0
B_REAL, N_DRAW, N_POINT = 200, 2000, 20000
N_REC = 500
SEED = 20261005

CONFIGS = {
    "primary":    {"rule": "E0", "M": 1.0, "label": "continuous"},
    "E0_M3":      {"rule": "E0", "M": 3.0, "label": "continuous"},
    "E5":         {"rule": "E5", "M": 1.0, "label": "continuous"},
    "bands3":     {"rule": "E0", "M": 1.0, "label": "bands3"},
    "binary":     {"rule": "E0", "M": 1.0, "label": "binary"},
    "calibrated": {"rule": "E0", "M": 1.0, "label": "continuous", "calibrated": True},
    "no_learner_bias": {"rule": "E0", "M": 1.0, "label": "continuous", "sigma_u0": True},
}


# ------------------------------------------------------------------ fitting the grader stand-in

def _ols(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta, y - X @ beta


def fit_grader(rows: list[dict]) -> dict:
    """Fit (a, b, sigma, sigma_u, delta, gamma, eta) from one model's swap dump rows."""
    ok = [r for r in rows if r.get("control") is not None]
    h = np.array([r["human"] for r in ok], float)
    c = np.array([r["control"] for r in ok], float)
    lid = np.array([r["learnerId"] for r in ok])
    (a, b), res = _ols(np.column_stack([np.ones_like(h), h]), c)
    # variance components of the residual: learner mean vs within
    uniq = np.unique(lid)
    means, ns, wss = [], [], 0.0
    for u in uniq:
        m = lid == u
        means.append(res[m].mean())
        ns.append(m.sum())
        wss += ((res[m] - res[m].mean()) ** 2).sum()
    ns = np.array(ns, float)
    sw2 = wss / max(1.0, len(res) - len(uniq))
    sb2 = float(np.var(means, ddof=1) - np.mean(sw2 / ns)) if len(uniq) > 1 else 0.0
    ys, l5, h5, dw, dl = [], [], [], [], []
    for r in ok:
        for arm, lab in (("trueLabel", "labelTrue"), ("swappedLabel", "labelSwapped")):
            if r.get(arm) is not None:
                ys.append(r[arm] - r["control"])
                l5.append(r[lab] - 5.0)
                h5.append(r["human"] - 5.0)
        if r.get("trueLabel") is not None and r.get("swappedLabel") is not None:
            dw.append(r["trueLabel"] - r["swappedLabel"])
            dl.append(r["labelTrue"] - r["labelSwapped"])
    ys, l5, h5 = (np.array(x, float) for x in (ys, l5, h5))
    (delta, gamma, eta), eres = _ols(np.column_stack([np.ones_like(ys), l5, h5]), ys)
    (_, _, _, quad), _ = _ols(np.column_stack([np.ones_like(ys), l5, h5, l5 ** 2]), ys)
    dw, dl = np.array(dw, float), np.array(dl, float)
    return {"a": float(a), "b": float(b), "sigma": float(math.sqrt(max(sw2, 1e-9))),
            "sigma_u": float(math.sqrt(max(sb2, 0.0))), "delta": float(delta), "gamma": float(gamma),
            "eta": float(eta), "gamma_within": float((dw * dl).sum() / (dl ** 2).sum()),
            "gamma_quadratic_term": float(quad),
            "call_noise_upper": float(eres.std(ddof=3) / math.sqrt(2)),
            "n_control": int(len(ok)), "n_edge_rows": int(len(ys))}


def bootstrap_fits(rows: list[dict], B: int, rng: np.random.Generator) -> list[dict]:
    """Learner-cluster bootstrap within tail; each draw refitted."""
    by = {}
    for r in rows:
        by.setdefault((r["tail"], r["learnerId"]), []).append(r)
    tails = {t: [k for k in by if k[0] == t] for t in ("high", "low")}
    out = []
    for _ in range(B):
        rs = []
        for t, keys in tails.items():
            for j in rng.integers(0, len(keys), len(keys)):
                k = keys[j]
                # relabel the learner so a learner drawn twice is two clusters. The tag is fixed per
                # cluster draw: an f-string on len(rs) inside the generator made every ROW its own
                # learner (found 2026-10-05 in the first params run; see FLOOR RECORD, revision 2a).
                tag = f"{k[1]}#{len(rs)}"
                rs.extend([{**r, "learnerId": tag} for r in by[k]])
        out.append(fit_grader(rs))
    return out


def tail_labels(rows):
    return {t: float(np.mean([r["labelTrue"] for r in rows if r["tail"] == t])) for t in ("high", "low")}


# ------------------------------------------------------------------ the engine and the loop

def _label(bel, mode, lab):
    if mode == "continuous":
        return np.round(10 * bel, 1)
    if mode == "bands3":
        return np.where(bel < 0.4, lab["low"], np.where(bel < 0.6, 5.0, lab["high"]))
    if mode == "binary":
        return np.where(bel >= TAU, lab["high"], lab["low"])
    raise ValueError(mode)


def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def _pred(m, v):
    return _sig(m / np.sqrt(1.0 + math.pi * v / 8.0))


def run_engine(theta, h, e, u, P, cfg, edge: bool, cohort, lab, shock=False):
    """One arm. Returns the learner-level belief after every item (N x T)."""
    N, T = h.shape
    M = cfg["M"]
    gap_skill = DAYS_PER_ITEM * K
    r = (1.0 + DECAY_V * gap_skill) ** (-DECAY_D)
    a, b = (0.0, 1.0) if cfg.get("calibrated") else (P["a"], P["b"])
    rule = cfg["rule"]
    A = np.full((N, K), 0.5)
    Bb = np.full((N, K), 0.5)
    At = np.full((N, K), 0.5)
    Bt = np.full((N, K), 0.5)
    touched = np.zeros((N, K), bool)
    last = np.zeros((N, K))
    if rule == "E0":
        touched[:] = True
        if shock:
            ns = 1.0 + M / (1.0 - r)
            A[:], Bb[:] = SHOCK_BELIEF * ns, (1 - SHOCK_BELIEF) * ns
    else:
        mu = cohort["mu_logit"]
        gm = np.full(N, math.log(SHOCK_BELIEF / (1 - SHOCK_BELIEF)) if shock else mu)
        gv = np.full(N, 0.1 if shock else 1.0)
    traj = np.empty((N, T))
    for t in range(T):
        k = t % K
        now = t * DAYS_PER_ITEM
        if rule == "E5":
            new = ~touched[:, k]
            if new.any():
                p0 = _pred(gm[new], gv[new])
                A[new, k], Bb[new, k] = N0_E5 * p0, N0_E5 * (1 - p0)
                At[new, k], Bt[new, k] = A[new, k], Bb[new, k]
                touched[new, k] = True
                last[new, k] = now
        bel_k = A[:, k] / (A[:, k] + Bb[:, k])
        x = a + b * h[:, t] + u + e[:, t]
        if edge:
            lbl = _label(bel_k, cfg["label"], lab)
            x = x + P["delta"] + P["gamma"] * (lbl - 5.0) + P["eta"] * (h[:, t] - 5.0)
        s = np.clip(np.round(x), 0, 10) / 10.0
        dt = now - last[:, k]
        rr = np.where(dt > 0, (1.0 + DECAY_V * dt) ** (-DECAY_D), 1.0)
        A[:, k] = rr * A[:, k] + (1 - rr) * At[:, k] + M * s
        Bb[:, k] = rr * Bb[:, k] + (1 - rr) * Bt[:, k] + M * (1 - s)
        last[:, k] = now
        if rule == "E5":
            p = _pred(gm, gv)
            gv = 1.0 / (1.0 / gv + p * (1 - p))
            gm = gm + gv * (s - p)
            reads = np.where(touched, A / (A + Bb), _pred(gm, gv)[:, None])
        else:
            reads = A / (A + Bb)
        traj[:, t] = reads.mean(1)
    return traj


def draw_cohort(N, T, cohort, P, cfg, rng, theta=None):
    if theta is None:
        theta = np.clip(rng.normal(cohort["mu_theta"], cohort["sd_theta"], N), 0, 10)
    h = np.clip(np.round(theta[:, None] + rng.normal(0, cohort["sd_item"], (N, T))), 0, 10)
    e = rng.normal(0, P["sigma"], (N, T))
    su = 0.0 if (cfg.get("calibrated") or cfg.get("sigma_u0")) else P["sigma_u"]
    u = rng.normal(0, su, N)
    return theta, h, e, u


def slope(x, y):
    xc = x - x.mean()
    return float((xc * (y - y.mean())).sum() / (xc ** 2).sum())


def cohort_estimands(P, cfg, cohort, lab, N, seed):
    rng = np.random.default_rng(seed)
    T = cohort["T"]
    theta, h, e, u = draw_cohort(N, T, cohort, P, cfg, rng)
    b0 = run_engine(theta, h, e, u, P, cfg, False, cohort, lab)
    b1 = run_engine(theta, h, e, u, P, cfg, True, cohort, lab)
    b2 = run_engine(theta, h, e, u, {**P, "gamma": 0.0}, cfg, True, cohort, lab)   # edge without feedback
    pi = theta / 10.0
    s0, s1, s2 = (slope(theta, x[:, -1]) for x in (b0, b1, b2))
    out = {"A": s1 / s2, "A_total": s1 / s0, "A_per_grade": s2 / s0}
    for t in (10, 20, 30, T):
        r0 = math.sqrt(((b0[:, t - 1] - pi) ** 2).mean())
        r1 = math.sqrt(((b1[:, t - 1] - pi) ** 2).mean())
        out[f"dRMSE_{t}"] = r1 - r0
        if t == T:
            out["RMSE_noedge"], out["RMSE_edge"] = r0, r1
    out["dRMSE"] = out[f"dRMSE_{T}"]
    for name, m in (("strong", theta >= STRONG), ("weak", theta < WEAK)):
        e0 = float((b0[m, -1] - pi[m]).mean())
        e1 = float((b1[m, -1] - pi[m]).mean())
        out[f"err_noedge_{name}"], out[f"err_edge_{name}"] = e0, e1
        out[f"dabs_{name}"] = abs(e1) - abs(e0)
    mast = pi >= TAU
    for nm, bb in (("noedge", b0), ("edge", b1)):
        out[f"FNR_{nm}"] = float((bb[mast, -1] < TAU).mean())
        out[f"FPR_{nm}"] = float((bb[~mast, -1] >= TAU).mean())
        out[f"FPRweak_{nm}"] = float((bb[theta < WEAK, -1] >= TAU).mean())
    for q in ("FNR", "FPR", "FPRweak"):
        out[f"d{q}"] = out[f"{q}_edge"] - out[f"{q}_noedge"]
    return out


def recovery_estimands(P, cfg, cohort, lab, N, seed):
    rng = np.random.default_rng(seed)
    T = cohort["T"]
    theta = np.full(N, 7.0)
    theta, h, e, u = draw_cohort(N, T, cohort, P, cfg, rng, theta=theta)
    out = {}
    for nm, edge in (("noedge", False), ("edge", True)):
        d = run_engine(theta, h, e, u, P, cfg, edge, cohort, lab)
        s = run_engine(theta, h, e, u, P, cfg, edge, cohort, lab, shock=True)
        far = np.abs(s - d) >= REC_TOL
        # recovery item = 1 + last item still far (0 if never far); T + 1 if still far at the end
        idx = np.where(far.any(1), T - np.argmax(far[:, ::-1], axis=1), 0)
        rec = np.where(far[:, -1], T + 1, idx + 1)
        out[f"rec_median_{nm}"] = float(np.median(rec))
        out[f"rec_unrecovered_{nm}"] = float(far[:, -1].mean())
        reach = (s >= TAU)
        out[f"reach_tau_median_{nm}"] = float(np.median(np.where(reach.any(1), np.argmax(reach, 1) + 1, T + 1)))
        out[f"reach_tau_never_{nm}"] = float((~reach.any(1)).mean())
    out["R"] = out["rec_median_edge"] / out["rec_median_noedge"]
    return out


def analytic(P, cfg):
    M = cfg["M"]
    r = (1.0 + DECAY_V * DAYS_PER_ITEM * K) ** (-DECAY_D)
    ns = 1.0 + M / (1.0 - r)
    w = M / ns
    g = P["gamma"]
    lamE = r + w * g
    out = {"r": r, "n_star": ns, "w": w, "loop_gain": w * g, "lambda_0": r, "lambda_E": lamE,
           "gamma_star": 1.0 + (1.0 - r) / M,
           "A_loop": (1 - r) / (1 - r - w * g) if lamE < 1 else float("inf"),
           "per_grade_factor": 1.0 + P["eta"] / (1.0 if cfg.get("calibrated") else P["b"])}
    out["R_analytic"] = math.log(r) / math.log(lamE) if 0 < lamE < 1 else float("inf")
    return out


# ------------------------------------------------------------------ verdicts

def pct(xs):
    xs = np.asarray(xs, float)
    return [float(np.percentile(xs, 2.5)), float(np.percentile(xs, 97.5))]


def v_spread(est, ci):
    d, lo, hi = est - 1, ci[0] - 1, ci[1] - 1
    if d >= MARGIN_A and lo > 0:
        return "AMPLIFIES"
    if d <= -MARGIN_A and hi < 0:
        return "DAMPS"
    if lo >= -MARGIN_NEUTRAL and hi <= MARGIN_NEUTRAL:
        return "NEUTRAL"
    return "UNRESOLVED"


def v_band(ci, m, up, down, flat):
    if ci[0] > m:
        return up
    if ci[1] < -m:
        return down
    if ci[0] >= -m and ci[1] <= m:
        return flat
    return "UNRESOLVED"


def v_stab(point_lam, lams):
    if point_lam >= 1:
        return "RUNAWAY"
    if np.percentile(lams, 97.5) < 1:
        return "STABLE"
    return "UNRESOLVED"


def v_recovery(est, ci):
    if est - 1 >= MARGIN_R and ci[0] > 1:
        return "SLOWER"
    if est - 1 <= -MARGIN_R and ci[1] < 1:
        return "FASTER"
    if ci[0] >= 1 - MARGIN_R and ci[1] <= 1 + MARGIN_R:
        return "SAME"
    return "UNRESOLVED"


def delatent(g, curve):
    """Latent gamma from a fitted one, inverting the floor's attenuation curve (planted -> mean fitted).
    Beyond the curve's last point the last ratio is applied."""
    if curve is None:
        return g
    pl, fh = np.array(curve["planted"]), np.array(curve["fitted_mean"])
    sgn, x = (1.0 if g >= 0 else -1.0), abs(g)
    if x <= fh[-1]:
        return sgn * float(np.interp(x, fh, pl))
    return sgn * x * pl[-1] / fh[-1]


def evaluate(P, draws, cfg, cohort, lab, n_point, n_draw, seed, recovery=True, curve=None):
    """Point estimates at P, intervals over the parameter draws, and the verdicts."""
    pt = cohort_estimands(P, cfg, cohort, lab, n_point, seed)
    ds = [cohort_estimands(Pd, cfg, cohort, lab, n_draw, seed + 1 + i) for i, Pd in enumerate(draws)]
    ci = {k: pct([d[k] for d in ds]) for k in pt}
    an = analytic(P, cfg)
    lat = {**P, "gamma": delatent(P["gamma"], curve)}
    an_lat = analytic(lat, cfg)
    lams = [analytic({**Pd, "gamma": delatent(Pd["gamma"], curve)}, cfg)["lambda_E"] for Pd in draws]
    res = {"point": pt, "ci95": ci, "analytic": an, "analytic_latent_gamma": an_lat,
           "lambda_E_latent_ci95": pct(lams),
           "A_loop_ci95": pct([analytic(Pd, cfg)["A_loop"] for Pd in draws]),
           "verdicts": {
               "spread": v_spread(pt["A"], ci["A"]),
               "spread_total": v_spread(pt["A_total"], ci["A_total"]),
               "stability": v_stab(an_lat["lambda_E"], lams),
               "divergence": v_band(ci["dRMSE"], MARGIN_B, "HARMS", "HELPS", "NO-CHANGE"),
               "strong_tail": v_band(ci["dabs_strong"], MARGIN_B, "AWAY", "TOWARD", "FLAT"),
               "weak_tail": v_band(ci["dabs_weak"], MARGIN_B, "AWAY", "TOWARD", "FLAT"),
               "false_not_mastered": v_band(ci["dFNR"], MARGIN_P, "UP", "DOWN", "FLAT"),
               "false_mastered": v_band(ci["dFPR"], MARGIN_P, "UP", "DOWN", "FLAT"),
               "false_mastered_weak": v_band(ci["dFPRweak"], MARGIN_P, "UP", "DOWN", "FLAT")}}
    if recovery:
        rp = recovery_estimands(P, cfg, cohort, lab, N_REC, seed + 7)
        rd = [recovery_estimands(Pd, cfg, cohort, lab, N_REC // 2, seed + 9001 + i)
              for i, Pd in enumerate(draws)]
        rci = {k: pct([d[k] for d in rd]) for k in rp}
        res["recovery"] = {"point": rp, "ci95": rci}
        res["verdicts"]["recovery"] = v_recovery(rp["R"], rci["R"])
    return res


# ------------------------------------------------------------------ floor

FLOOR_GRADER = {"a": 0.5, "b": 0.85, "case_sd": 1.4, "call_sd": 0.6, "learner_sd": 0.33}
FLOOR_WORLDS = {
    "AMP-MEASURED": ({"gamma": 0.10, "delta": 0.0, "eta": 0.0}, "spread", "AMPLIFIES"),
    "AMP-LARGE":    ({"gamma": 0.30, "delta": 0.0, "eta": 0.0}, "spread", "AMPLIFIES"),
    "DAMP":         ({"gamma": -0.10, "delta": 0.0, "eta": 0.0}, "spread", "DAMPS"),
    "NULL-SHIFT":   ({"gamma": 0.0, "delta": 0.30, "eta": 0.0}, "spread", "NEUTRAL"),
    "NULL":         ({"gamma": 0.0, "delta": 0.0, "eta": 0.0}, "spread", "NEUTRAL"),
    "RUNAWAY":      ({"gamma": 1.50, "delta": 0.0, "eta": 0.0}, "stability", "RUNAWAY"),
    "SHRINK":       ({"gamma": 0.0, "delta": 0.0, "eta": -0.15}, "spread", "NEUTRAL"),
}
FLOOR_REPS, FLOOR_B, FLOOR_N = 40, 100, 1000


def synth_rows(draw_rows, world, rng):
    g = FLOOR_GRADER
    learners = sorted({r["learnerId"] for r in draw_rows})
    ul = dict(zip(learners, rng.normal(0, g["learner_sd"], len(learners))))
    out = []
    for r in draw_rows:
        base = g["a"] + g["b"] * r["human"] + ul[r["learnerId"]] + rng.normal(0, g["case_sd"])

        def score(lbl):
            x = base + rng.normal(0, g["call_sd"])
            if lbl is not None:
                x += world["delta"] + world["gamma"] * (lbl - 5) + world["eta"] * (r["human"] - 5)
            return float(np.clip(np.round(x), 0, 10))
        out.append({**{k: r[k] for k in ("id", "learnerId", "tail", "human", "labelTrue", "labelSwapped")},
                    "control": score(None), "trueLabel": score(r["labelTrue"]),
                    "swappedLabel": score(r["labelSwapped"])})
    return out


def _atten_rep(args):
    gam, rep, draw_rows = args
    rng = np.random.default_rng(arm_seed(SEED, "atten", rep * 1000 + int(round(gam * 100))))
    return gam, fit_grader(synth_rows(draw_rows, {"gamma": gam, "delta": 0.0, "eta": 0.0}, rng))["gamma"]


def _floor_rep(args):
    wname, rep, draw_rows, cohort, lab, curve = args
    world, kind, _ = FLOOR_WORLDS[wname]
    seed = arm_seed(SEED, f"floor-{wname}", rep * 1000)
    rng = np.random.default_rng(seed)
    rows = synth_rows(draw_rows, world, rng)
    P = fit_grader(rows)
    draws = bootstrap_fits(rows, FLOOR_B, rng)
    res = evaluate(P, draws, CONFIGS["primary"], cohort, lab, FLOOR_N * 4, FLOOR_N, seed, recovery=False,
                   curve=curve)
    return wname, {"spread": res["verdicts"]["spread"], "stability": res["verdicts"]["stability"],
                   "spread_total": res["verdicts"]["spread_total"], "A_total": res["point"]["A_total"],
                   "A": res["point"]["A"], "gamma_hat": P["gamma"], "A_loop": res["analytic"]["A_loop"]}


def gain_recovery(cohort, lab):
    out = {}
    g = FLOOR_GRADER
    for gam in (0.10, 0.30, -0.10, 0.0):
        P = {"a": g["a"], "b": g["b"], "sigma": math.hypot(g["case_sd"], g["call_sd"]),
             "sigma_u": g["learner_sd"], "delta": 0.0, "gamma": gam, "eta": 0.0}
        est = cohort_estimands(P, CONFIGS["primary"], cohort, lab, N_POINT, arm_seed(SEED, "gain", int(gam * 100)))
        an = analytic(P, CONFIGS["primary"])
        a_sim, a_an = est["A"] - 1, an["A_loop"] - 1
        ok = abs(a_sim) < 0.01 if gam == 0 else abs(a_sim - a_an) <= 0.25 * abs(a_an)
        out[f"gamma={gam:+.2f}"] = {"A_sim_minus_1": a_sim, "A_loop_analytic_minus_1": a_an, "pass": bool(ok)}
    return out


def floor(draw_path: Path):
    """The floor reads the cohort's SHAPE from JorGPT and the draw's STRUCTURE (no score)."""
    from shared.paths import data_path
    cohort = cohort_shape(data_path("JORGPT_DIR") / "dataset_en.csv")
    draw_rows = json.loads(draw_path.read_text())["rows"]
    lab = tail_labels(draw_rows)
    fits = {g: [] for g in ATTEN_GAMMAS}
    with ProcessPoolExecutor() as ex:
        for g, gh in ex.map(_atten_rep, [(g, i, draw_rows) for g in ATTEN_GAMMAS for i in range(ATTEN_REPS)]):
            fits[g].append(gh)
    curve = {"planted": list(ATTEN_GAMMAS), "fitted_mean": [float(np.mean(fits[g])) for g in ATTEN_GAMMAS],
             "fitted_sd": [float(np.std(fits[g])) for g in ATTEN_GAMMAS], "reps": ATTEN_REPS}
    print("attenuation curve", curve)
    jobs = [(w, i, draw_rows, cohort, lab, curve) for w in FLOOR_WORLDS for i in range(FLOOR_REPS)]
    tally = {w: [] for w in FLOOR_WORLDS}
    with ProcessPoolExecutor() as ex:
        for w, r in ex.map(_floor_rep, jobs, chunksize=2):
            tally[w].append(r)
    worlds, ok = {}, True
    for w, rs in tally.items():
        _, kind, want = FLOOR_WORLDS[w]
        counts = {}
        for r in rs:
            counts[r[kind]] = counts.get(r[kind], 0) + 1
        rate = counts.get(want, 0) / len(rs) if want else None
        wrong = (sum(1 for r in rs if r["spread"] in ("AMPLIFIES", "DAMPS")) / len(rs)
                 if w.startswith("NULL") or w == "SHRINK" else None)
        passed = True if want is None else (rate >= 0.8 and (wrong is None or wrong <= 0.10))
        ok &= passed
        worlds[w] = {"planted": FLOOR_WORLDS[w][0], "reads": kind, "expected": want, "counts": counts,
                     "rate": rate, "null_false_rate": wrong, "pass": passed,
                     "A_mean": float(np.mean([r["A"] for r in rs])),
                     "A_total_mean": float(np.mean([r["A_total"] for r in rs])),
                     "spread_total_counts": {v: sum(1 for r in rs if r["spread_total"] == v) for v in
                                             ("AMPLIFIES", "DAMPS", "NEUTRAL", "UNRESOLVED")},
                     "gamma_hat_mean": float(np.mean([r["gamma_hat"] for r in rs])),
                     "spread_counts": {v: sum(1 for r in rs if r["spread"] == v) for v in
                                       ("AMPLIFIES", "DAMPS", "NEUTRAL", "UNRESOLVED")}}
    gr = gain_recovery(cohort, lab)
    ok &= all(v["pass"] for v in gr.values())
    res = {"pass": bool(ok), "revision": 1, "attenuation_curve": curve, "cohort": cohort, "tail_labels": lab, "worlds": worlds, "gain_recovery": gr, "grader": FLOOR_GRADER,
           "reps": FLOOR_REPS, "B": FLOOR_B, "cohort_n": FLOOR_N,
           "note": "smoke check: instrument, worlds and scoring written by one session"}
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(res, indent=2) + "\n")
    print(json.dumps({w: (v["counts"], v["pass"]) for w, v in worlds.items()}, indent=1))
    print(json.dumps(gr, indent=1))
    print("FLOOR", "PASSES" if ok else "FAILS")


# ------------------------------------------------------------------ params and run

def cohort_shape(jorgpt_csv: Path) -> dict:
    import pandas as pd
    d = pd.read_csv(jorgpt_csv)
    d = d[d.student_answer.fillna("").str.strip() != ""]
    g = d.groupby("student_anom_id").teacher_grade
    m, n = g.mean(), g.size()
    within = d.teacher_grade - g.transform("mean")
    sw = float(math.sqrt((within ** 2).sum() / (len(d) - len(m))))
    sb2 = float(m.var(ddof=1) - np.mean(sw ** 2 / n))
    return {"mu_theta": float(m.mean()), "sd_theta": float(math.sqrt(max(sb2, 0.0))), "sd_item": sw,
            "T": int(np.median(n)), "learners": int(len(m)), "responses": int(len(d))}


def params(dumps: list[Path]):
    from shared.paths import data_path
    cohort = cohort_shape(data_path("JORGPT_DIR") / "dataset_en.csv")
    rng = np.random.default_rng(SEED)
    models = {}
    for p in dumps:
        blob = json.loads(p.read_text())
        rows = blob["rows"]
        fit = fit_grader(rows)
        draws = bootstrap_fits(rows, B_REAL, rng)
        models[blob["model"]] = {"dump": p.name, "run": blob.get("runStamp"), "fit": fit,
                                 "fit_ci95": {k: pct([d[k] for d in draws]) for k in fit if isinstance(fit[k], float)},
                                 "draws": [{k: d[k] for k in ("a", "b", "sigma", "sigma_u", "delta", "gamma", "eta")}
                                           for d in draws],
                                 "tail_labels": tail_labels(rows)}
    first = next(iter(models.values()))
    # E5's offline mu: logit of the cohort's mean label-blind grade, per model (set in run)
    out = {"cohort": cohort, "models": models, "tail_labels": first["tail_labels"],
           "call_noise_measured": {"google:gemini-3.5-flash-lite": 0.18,
                                   "source": "grader-attainment-prior/out/pooling.json run: per-answer sd over nine passes"}}
    OUT.mkdir(exist_ok=True)
    (OUT / "params.json").write_text(json.dumps(out, indent=1) + "\n")
    for m, v in models.items():
        f = v["fit"]
        print(m, {k: round(f[k], 3) for k in f if isinstance(f[k], float)})
    print(cohort)


def _run_model(args):
    mname, mv, cohort, lab, curve = args
    P = mv["fit"]
    res = {}
    for cname, cfg in CONFIGS.items():
        c2 = dict(cohort)
        a, b = (0.0, 1.0) if cfg.get("calibrated") else (P["a"], P["b"])
        mg = np.clip((a + b * cohort["mu_theta"]) / 10.0, 0.02, 0.98)
        c2["mu_logit"] = float(math.log(mg / (1 - mg)))
        res[cname] = evaluate(P, mv["draws"], cfg, c2, lab, N_POINT, N_DRAW,
                              arm_seed(SEED, f"{mname}-{cname}"), curve=curve)
    return mname, res


def run():
    fl = OUT / "floor.json"
    if not fl.exists() or not json.loads(fl.read_text())["pass"]:
        raise SystemExit("out/floor.json is missing or did not pass; the real-parameter run is refused")
    prm = json.loads((OUT / "params.json").read_text())
    cohort, lab = prm["cohort"], prm["tail_labels"]
    curve = json.loads(fl.read_text())["attenuation_curve"]
    jobs = [(m, v, cohort, lab, curve) for m, v in prm["models"].items()]
    per = {}
    with ProcessPoolExecutor() as ex:
        for m, r in ex.map(_run_model, jobs):
            per[m] = r
    prim = [per[m]["primary"]["verdicts"]["spread"] for m in per]
    overall = prim[0] if len(set(prim)) == 1 else "MIXED-ACROSS-MODELS"
    res = {"overall_spread_primary": overall, "per_model": per, "configs": CONFIGS, "cohort": cohort,
           "tail_labels": lab, "B": B_REAL, "n_draw": N_DRAW, "n_point": N_POINT}
    (OUT / "results.json").write_text(json.dumps(res, indent=1) + "\n")
    print("overall spread (primary):", overall)
    for m, r in per.items():
        for c, x in r.items():
            print(f"{m:40s} {c:16s} A={x['point']['A']:.3f} {x['ci95']['A']} {x['verdicts']}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["params", "floor", "run"])
    ap.add_argument("--dumps", type=Path, nargs="*")
    ap.add_argument("--draw", type=Path, help="the attainment draw (grader-vi/draw.json) for the floor")
    a = ap.parse_args()
    if a.cmd == "params":
        params(a.dumps)
    elif a.cmd == "floor":
        floor(a.draw)
    else:
        run()
