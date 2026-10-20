"""
How much of the grader's no-label group gap on ASAP 2.0 is the matching artefact? (Paper VI, H15)

RESULT (2026-10-06, run under amendments 1-2 after the floor passed; README "Results" has the tables).
Per axis, identical on Qwen3-235B and GPT-4.1-mini:
  ell         RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.80)
  disability  RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.85)
  economic    RHO-DEPENDENT (PARTLY-ARTEFACT from 0.65; NOT-ARTEFACT from 0.70)
Corrected gap at equal true score, for rho 0.65 / 0.75 / 0.90:
  Qwen   ell -0.124 / -0.173 / -0.222, disability -0.150 / -0.217 / -0.284 (observed -0.242, -0.318)
  GPT    ell -0.109 / -0.149 / -0.189, disability -0.157 / -0.212 / -0.266 (observed -0.205, -0.295)
The artefact is 27-32% of the observed gap at rho 0.75. Break-even rho (the gap fully artefact) is
0.49-0.52 everywhere. The triad bound on rho is 0.30-0.37, biased down by the graders' shared error;
the two LLMs correlate 0.76 with each other and 0.52-0.55 with the human. The other two corrections
agree in sign and attribute slightly more to the artefact. Item 5: within-essay contrasts are
unbiased only if the label's effect does not depend on quality. Qwen's does, with a slope of
(low - none) on H of -0.113 per level, so its favouring D_low (ell +0.075, disability +0.105) carries
+0.02-0.05 of matching artefact. GPT-4.1-mini's slope is -0.024, and its biases are <= 0.011.

AMENDMENT 3 READING (2026-10-06; reliability_known.py, out/reliability-known.json). The data paper puts
the human score's reliability at 0.75 (one rater) to ~0.857 (two reads). There: ell and disability
PARTLY-ARTEFACT at 0.75 and NOT-ARTEFACT at 0.857, economic NOT-ARTEFACT at both; 0.15-0.27 of a level
remains at equal true quality on ell and disability.

WHAT IS ASKED. Paper VI (release ai-grader-reliability-2026) reports, from
studies/measurement/grader-attainment-groups/ (out/results.json, `none_arm_residual_gap`), that at
equal human score the grader marks English learners' and disability-identified students' essays
0.21-0.32 of a level below their peers' with no label at all (machine - human residual, focal minus
reference, post-stratified on the human score, design-weighted):

                 Qwen3-235B   GPT-4.1-mini
    ELL           -0.242        -0.205
    economic      -0.170        -0.135
    disability    -0.318        -0.295
    gender (F)    +0.031        +0.069

and earlier on Gemini (grader-eval findings log 2026-09-16, ELL 0.275, economic 0.163, n = 1,400,
no per-essay dump kept). The scope audit's finding H15 (research/readiness/ai-grader-reliability-
2026/scope-audit.md) points out that "equal human score" is equal OBSERVED score from one rating.
When the groups differ in true mean (ELL 2.53 v 3.00, disability 2.38 v 3.01 on the 1-6 scale) and
the matching score is noisy, focal essays in the same stratum have lower true quality on average
(Kelley 1947: the best estimate of true quality is shrunk toward the group's own mean). Any second
measure that tracks true quality, an unbiased grader included, then shows a negative residual gap
for the lower-mean group. Under classical test theory, a grader M = a + b T + e and a human
H = T + u, with within-group reliability rho_w = 1 - var(u)/var_within(H):

    E[M - H | H, focal] - E[M - H | H, ref]  =  b (1 - rho_w) (mu_focal - mu_ref)      (the ARTEFACT)

which for b = 1 is the (1 - rho) x (group mean difference) of the audit. This study estimates the
artefact for this draw, these graders and this corpus, subtracts it, and states what is left.

THE DATA. ASAP 2.0 (data/data-sources.json `asap2`, CC BY 4.0, $ASAP2_DIR): the corpus file is read
for the group-mean model (H on group fields and prompt). The two graders' per-essay dumps from the
grader-attainment-groups run (run-qwen.json, run-gpt41mini.json; essay ids, human score, group
fields, quota cell, grader scores per arm) stay in the session scratchpad and are pointed at by
--dumps (by path). Only aggregates go to out/. No model call is made by this study.
The analysis reuses grader-attainment-groups/analyse.py's own `Data`, `strat_diff`, strata, design
weights and completeness mask, and asserts it reproduces that study's none-arm gaps to 1e-9 before
anything else is read.

RELIABILITY OF THE HUMAN SCORE (the input everything turns on). Not in the corpus: ASAP 2.0 ships one
`score` per essay and no rater-level field. The data paper (Crossley, Baffour, Burleigh and King,
Assessing Writing 2025) could not be read from this session (sciencedirect, arxiv, researchgate,
zenodo and aclanthology all blocked by the egress proxy). Web-search snippets of that paper and of
the PERSUADE 2.0 paper (Crossley et al., Assessing Writing 2024), NOT VERIFIED AGAINST THE TEXT,
say the essays were double-blind rated by expert raters with 100% adjudication, with pre-adjudication
inter-rater agreement weighted kappa .745 (r = .750) for the PERSUADE-derived essays and weighted
kappa .659 for another part. If the released score is one rater's, its reliability is about the
inter-rater correlation (~0.66-0.75); if it is the adjudicated score of two raters it is higher
(Spearman-Brown of 0.75 over two ratings is 0.86). The repo's own codebook says "single rater per
the 2026-09-16 grader-eval reading; ... not verified against the data paper". So reliability is
BRACKETED, not estimated. [Since verified, amendment 3: the maintainer supplied the paper (Assessing
Writing 65, 100954, doi:10.1016/j.asw.2025.100954, section 3, p. 3): double-blind expert rating
followed by 100 percent adjudication; pre-adjudication weighted kappa .745, r .750 (PERSUADE 2.0
subset, ~13,000 essays) and weighted kappa .659, r .750 (~12,000 new essays). The bracket below is
what was run.]
  PRIOR       rho ~ Uniform(0.65, 0.90), carried through the bootstrap (the headline interval).
  GRID        rho in {0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95}: every number is also reported
              as a function of rho, with the break-even rho at which the corrected gap reaches 0.
  DATA BOUND  the triad estimate rho_H = cov(H,Q) cov(H,G) / (cov(Q,G) var(H)) on the essays both
              graders scored (none arm, design-weighted; also within-group, on residuals from the
              group-mean model). Reported, not used: two LLM graders share error (the same surface-
              feature halo), which inflates cov(Q,G) and biases rho_H DOWN, so it is a rough lower
              bound, not an estimate.
rho is the reliability of one essay's score in the corpus population: var(u) = (1 - rho) var_corpus(H).

THE ARTEFACT MODEL (primary correction, `artefact`). Group-mean model: OLS on the full corpus of H on
indicators for ell (Yes, NA), economic (disadvantaged, NA), disability (identified, NA), gender (F,
NA if any), race (each level but White, NA included) and prompt (seven, one dropped); mu_i its
prediction, s_w^2 its residual variance. Errors have mean zero, so E[T | groups, prompt] = mu_i.
Kelley posterior: T | H, groups ~ N(m_i, v) with rho_w = 1 - (1 - rho) var(H) / s_w^2,
m_i = mu_i + rho_w (H_i - mu_i), v = rho_w (1 - rho) var(H). The UNBIASED GRADER is
M = clip(round(alpha + beta T + eps), 0, 6), eps ~ N(0, sigma^2), so P(M = k | H_i, groups_i) is a
normal-CDF difference and E[M | H_i, groups_i] is exact (no Monte Carlo). (alpha, beta, sigma) are
calibrated, at each rho, so the unbiased grader reproduces the real grader's design-weighted mean,
covariance with H and variance on the analysed essays (its own leniency, scale and noise). The
artefact A(rho) is analyse.py's strat_diff of (E[M | H, groups] - H): the gap an unbiased grader with
this grader's leniency and noise would show on this draw, with its real strata and weights.
CORRECTED GAP C = G_obs - A(rho).
  Check: A(rho) against the analytic beta (1 - rho_w) (mu_f - mu_r) (mu from the group-mean model,
  averaged over the axis population) and against the audit's (1 - rho)(mean difference); and against
  a Monte Carlo of the same model (simulate T, M; compute the gap) to confirm the exact expectation.

TWO OTHER CORRECTIONS (reported beside the primary; a verdict that depends on the approach is said to):
  KELLEY-REGRESSION  WLS of the real M on [1, m_i, m_i^2, focal] over the axis population (design
                     weights): the focal coefficient is the group gap at equal ESTIMATED TRUE score.
  ERRORS-IN-VARIABLES  no conditioning on the human strata at all: gamma = dM - (b / rho_wa) dH, with
                     dM, dH the design-weighted focal - reference mean differences of M and H, b the
                     WLS slope of M on H with a focal indicator, rho_wa = 1 - (1 - rho) var(H) /
                     var_within_axis(H) (pooled within focal and reference, from the corpus). Under
                     M = a + beta T + gamma focal + e, H = T + u, this is consistent for gamma (Fuller
                     1987). The ratio dM / dH is reported beside beta: an unbiased grader has dM/dH =
                     beta.
INTERVAL. Bootstrap over essays (the unit; no student id), resampled within quota cell so the design
weights are fixed, B = 2,000; each resample draws rho from the prior, recalibrates the grader and
recomputes G_obs, A, C and both other corrections. Percentile 95% intervals. The group-mean model's
own uncertainty (n = 24,728) is not bootstrapped and is stated. Grid points use B = 500 at fixed rho.

PRE-REGISTERED VERDICTS (committed before any real residual is read). Per model x axis, on C's 95%
prior interval [lo, hi], signed in the direction of the observed gap (s = sign(G_obs); compare s*C):
  ARTEFACT-EXPLAINS-IT   the interval includes 0 and excludes G_obs
  PARTLY-ARTEFACT        the interval excludes 0 on the side of G_obs and excludes G_obs
  NOT-ARTEFACT           the interval includes G_obs and excludes 0
  UNRESOLVED             the interval includes both 0 and G_obs
  OVERCORRECTED          the interval excludes 0 on the side opposite G_obs (the predicted artefact
                         exceeds the observed gap: at equal true score the grader would favour the group)
  Axes: ell, disability, economic (the paper's three); gender reported. Per axis across the two models:
  the shared verdict if both agree, else "<qwen verdict> / <gpt verdict>". The headline the paper
  needs is the ELL and disability pair. Also reported per grid rho (same rule, fixed rho), and the
  verdict strings of the two other corrections.

THE FLOOR (`--floor`; must pass before `--run` reads any grader score). Forward synthetic worlds on
the real draw's covariates (groups, prompt, quota cell, design weights; NO real human or grader score):
T_i = mu_i + N(0, s_w^2 - var(u)); H = clip(round(T + u), 1, 6); grader M = clip(round(0.10 + 0.90 T
+ N(0, 0.60) - d_ell [ELL] - d_dis [disability-identified]), 0, 6). Generating H forward (not from the
Kelley posterior) tests the correction's normal model against the integer scale, its ends and the
rounding. The planted truth gamma_true per axis is the design-weighted mean over focal essays minus
over reference essays of E[M | T_i, planted terms] - E[M | T_i, none] (exact). The realised reliability
of the synthetic H (design-weighted corr(T, H)^2 in a 200,000-essay population) is the "true rho":
rounding to 1..6 costs reliability (a continuous 0.65 realises ~0.60, 0.90 ~0.83), and a documented
inter-rater figure is a figure for the integer score, so the floor plants the continuous value that
REALISES the target.
  Worlds: rho_true (realised) in {0.65, 0.75, 0.85} x (d_ell, d_dis) in {(0, 0), (0.10, 0.10), (0.25, 0.25)};
  100 replicates each; prior interval with B = 200 per replicate.
  F1 BIAS      with the correction at the true rho, |mean C - gamma_true| <= 0.03 on ell, disability
               and economic in every world.
  F2 COVERAGE  the prior 95% interval covers gamma_true in >= 90% of replicates (ell, disability) in
               every world.
  F3 NULL      in d = 0 worlds, the interval lies wholly below 0 (a false "bias remains") in <= 8% of
               replicates on each of ell, disability, economic.
  F4 POWER     in d = 0.25 worlds, the interval lies wholly below 0 on ell and on disability in >= 80%.
  F5 PREMISE   in d = 0 worlds at rho_true = 0.65, the uncorrected gap's mean is <= -0.05 on ell and
               disability (the artefact exists in the instrument; otherwise the floor tests nothing).
  Size of the control: the d = 0 world IS the control; its artefact is compared with the planted 0.25
  and with the observed gaps (shared/controls.py), so a null that only shows "a tiny artefact is
  harmless" cannot pass F5. Reported, not pass criteria: the uncorrected gap in every world, the
  correction run at a wrong rho (0.75 when rho_true is 0.65 or 0.85), the analytic and Monte Carlo
  checks of A.

LABEL-BY-GROUP CONTRASTS (`--label-check`, item 5). Paper VI's label results compare two grades of the
SAME essay (D_low = group difference in low - none at equal human score), so a noisy reference should
not bias them: the true-quality difference within a stratum enters both arms and cancels, PROVIDED
the label's effect does not itself depend on true quality. Checked numerically: synthetic worlds as
the floor (rho_true 0.65), none = round(alpha + beta T + c + e0), low = round(alpha + beta T + c + L(T)
+ d_low [focal] + e1), case effect c ~ N(0, 0.5), call noise e ~ N(0, 0.3), L(T) = L0 + L1 (T - 3).
  (i)  L1 = 0, L0 = -0.47 (Qwen's low - none), d_low in {0, +0.10}: criterion |mean D_low - d_low_true|
       <= 0.02 on ell and disability (a fifth of the study's 0.10 MDE), d_low_true computed exactly as
       gamma_true above.
  (ii) L1 = the true-score slope implied by the real data: the WLS slope of (low - none) on H over the
       complete essays, divided by rho_w (run after the floor, on the real dumps), at rho in {0.65,
       0.75, 0.90}; the resulting D_low bias is reported beside the measured D_low values. A label
       effect that grows or shrinks with quality is the one route by which the noisy reference
       reaches the within-essay contrasts.
GEMINI (2026-09-16). No per-essay dump survives, so only the analytic artefact beta (1 - rho_w) dmu is
reported, with beta bracketed by the two calibrated graders' betas and dmu from the corpus; it is a
projection, not a correction.

LIMITS STATED IN ADVANCE. Classical test theory: the human's error is independent of group and of true
quality, and grader and human measure the same T. If raters themselves mark ELL essays down (rater
DIF), the human score is biased, not just noisy, and nothing here corrects that. The reliability is
bracketed, not measured; every conclusion is conditional on the prior and is shown across the grid.

AMENDMENT 1 (2026-10-06, after the first world of the revision-0 floor and before any grader score
was read). Revision 0's first world (realised rho 0.65, d = 0) FAILED F2 and F3: the prior interval
covered 0 in 86% (ell), 75% (disability) and 81% (economic) of replicates, and lay wholly below 0 in
14%, 25% and 19%. The correction itself was accurate at the true rho (bias +0.006, +0.006, -0.000);
the failure is the prior's. A world at the prior's low edge is corrected as if rho were ~0.78, and
the interval inherits that. So the prior interval cannot carry a verdict: the reliability is the
quantity the answer turns on, and integrating it out hides that. The second world (d = 0.10) showed
a second fault. The calibration absorbed 15-19% of a planted bias (bias +0.015 / +0.019), because a
group bias correlated with H inflates the pooled cov(M, H) the unbiased grader is matched to.
Changes (revision 1, `--floor-rev1`, `run`):
  1. HEADLINE BY RELIABILITY. The verdict rule above is applied at each fixed rho in the bracket
     BRACKET = {0.65, 0.70, 0.75, 0.80, 0.85, 0.90}, with a fixed-rho bootstrap (B = 500). Per model x
     axis: the common verdict if it is the same at every bracket rho, else "RHO-DEPENDENT (<verdict>
     from <rho>; ...)". The prior interval is reported as `verdict_prior_interval`, not as the verdict.
  2. WITHIN-GROUP CALIBRATION. The unbiased grader is matched to the real grader's mean and to its
     WITHIN-GROUP covariance with H and variance: residuals after WLS on the group-mean design (all
     group fields and prompt).
  3. THE FLOOR'S TRUTH. gamma_true is the planted bias post-stratified on true-score strata
     (rint(T) in the estimator's strata), the estimand's own definition. Revision 0's unconditional
     difference differs from it where a bias planted on ELL and disability reaches economic through
     composition.
  Revision-1 floor: the same worlds, F1 and F5 unchanged; F2, F3 and F4 are judged on the fixed-rho
  interval at the realised true rho. Also reported: C when rho is misspecified by -0.10 and +0.10, and
  the bias of the two other corrections. Revision 0 runs to completion and is kept as
  out/floor-rev0.json.

AMENDMENT 2 (after the revision-1 floor, before any grader score was read). Revision 1 passed F1, F3,
F4 and F5 and failed F2 in one of its 18 axis x world cells: ell at realised rho 0.85, d = 0, covered
in 88 of 100 replicates against >= 90 (the other 17 ell/disability cells 0.92-0.97; economic, not a
criterion axis, 0.88-0.98). Mean coverage over the 18 cells is 0.94. [Corrected after commit 7c2293d,
which said "0.88 economic in the same world" (it was the rho 0.65 world) and "about a 1-in-4 chance".]
Some cell of 18 at <= 0.88 has probability 0.07 if the true coverage is 0.95 and 0.26 if it is 0.94
(binomial), so it is weak evidence of under-coverage, and the cell is re-run once with 300 fresh
replicates (`--floor-recheck`). F2 is taken as
passed if that pooled coverage is >= 0.90 on ell. If it is not, the floor fails and the run does not
happen. This rule is written and committed before the recheck runs.


AMENDMENT 3 (2026-10-06, after the run; a reading, not an analysis). The data paper's figures above
fix rho inside the registered grid. The registered fixed-rho verdict rule is read at rho = 0.75 (lower
bound: one rater, r = .750) and rho = 0.857 (best estimate: Spearman-Brown of .75 over two ratings,
adjudication assumed at least as good as averaging two raters). 0.857 is read by linear interpolation
of the committed 0.85 and 0.90 point estimates and interval endpoints (the verdict equals the
neighbours' when they agree, since the rule is linear inequalities on the interval). Label-by-group
implied biases are evaluated exactly at 0.857 by the analytic formula in contrast_slopes(), and
corrected z = (measured - bias) / se. A sensitivity at the reliability of an integer composite of two
reads (the released score is an integer) is reported, not used as a verdict. Nothing here is re-run;
reliability_known.py does the reading from out/ and writes out/reliability-known.json.

    python3 artefact.py --floor                 # revision 0 floor; writes out/floor-rev0.json
    python3 artefact.py --floor-rev1            # revision 1 floor; writes out/floor-rev1.json
    python3 artefact.py --run [--dumps a b]     # requires a passed out/floor-rev1.json; writes out/results.json
    python3 artefact.py --label-check           # requires --run; writes out/label-check.json
Environment: ASAP2_DIR (or LDA_SCRATCH_DIR). Every mode takes --dumps run-qwen.json run-gpt41mini.json.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / "out"
sys.path.insert(0, str(REPO))

_spec = importlib.util.spec_from_file_location(
    "attainment_groups", REPO / "studies/measurement/grader-attainment-groups/analyse.py")
AG = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(AG)

AXES = AG.AXES                         # ell, economic, disability, gender: (focal, reference)
PAPER_AXES = ("ell", "disability", "economic")
PRIOR = (0.65, 0.90)
RHO_GRID = (0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95)
B_PRIOR, B_GRID = 2000, 500
LOW_RHO = (0.35, 0.40, 0.45, 0.50, 0.55)   # POST HOC point estimates only (see run())
DUMPS = ("run-qwen.json", "run-gpt41mini.json")
K = np.arange(7.0)                     # grader scale 0..6
CUTS = np.arange(6) + 0.5
SEED = 20261006

# floor
F_RHOS = (0.65, 0.75, 0.85)   # REALISED reliability of the integer synthetic H (planted value solved for)
F_DELTAS = (0.0, 0.10, 0.25)
F_REPS, F_BOOT = 100, 200
F_ALPHA, F_BETA, F_SIGMA = 0.10, 0.90, 0.60


# ----------------------------------------------------------------------------- the group-mean model

class CorpusModel:
    """OLS of the human score on group fields and prompt over the full corpus."""

    def __init__(self, H: np.ndarray, groups: dict[str, np.ndarray], prompt: np.ndarray):
        self.levels = {}
        for ax, (f, r) in AXES.items():
            lv = sorted(set(groups[ax]) - {r})          # focal, NA, anything else
            self.levels[ax] = lv
        self.levels["race"] = sorted(set(groups["race"]) - {"White"})
        self.prompts = sorted(set(prompt))[1:]
        X = self.design(groups, prompt)
        self.coef, *_ = np.linalg.lstsq(X, H, rcond=None)
        res = H - X @ self.coef
        self.s_w2 = float(res @ res / (len(H) - X.shape[1]))
        self.var_H = float(np.var(H, ddof=1))
        self.mean_H = float(H.mean())
        # pooled within-axis variance of H (focal and reference), for the EIV correction
        self.var_within_axis = {}
        for ax, (f, r) in AXES.items():
            a, b = H[groups[ax] == f], H[groups[ax] == r]
            self.var_within_axis[ax] = float(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1))
                                             / (len(a) + len(b) - 2))
        self.group_means = {ax: (float(H[groups[ax] == f].mean()), float(H[groups[ax] == r].mean()))
                            for ax, (f, r) in AXES.items()}

    def design(self, groups, prompt) -> np.ndarray:
        n = len(prompt)
        cols = [np.ones(n)]
        for ax in (*AXES, "race"):
            for lv in self.levels[ax]:
                cols.append((groups[ax] == lv).astype(float))
        for p in self.prompts:
            cols.append((prompt == p).astype(float))
        return np.column_stack(cols)

    def mu(self, groups, prompt) -> np.ndarray:
        return self.design(groups, prompt) @ self.coef

    def var_u(self, rho: float) -> float:
        return (1 - rho) * self.var_H

    def rho_w(self, rho: float) -> float:
        rw = 1 - self.var_u(rho) / self.s_w2
        if rw <= 0:
            raise ValueError(f"rho {rho} leaves no within-group true variance")
        return rw

    def kelley(self, H, mu, rho):
        rw = self.rho_w(rho)
        return mu + rw * (H - mu), rw * self.var_u(rho), rw


def load_corpus_model() -> CorpusModel:
    import pandas as pd
    from shared.paths import data_path
    p = data_path("ASAP2_DIR") / "ASAP2_train_sourcetexts.csv"
    df = pd.read_csv(p, usecols=["essay_id", "score", "prompt_name", "ell_status", "economically_disadvantaged",
                                 "student_disability_status", "race_ethnicity", "gender"])
    cols = {"ell": "ell_status", "economic": "economically_disadvantaged",
            "disability": "student_disability_status", "race": "race_ethnicity", "gender": "gender"}
    groups = {k: df[c].fillna("NA").astype(str).to_numpy() for k, c in cols.items()}
    return CorpusModel(df["score"].to_numpy(float), groups, df["prompt_name"].astype(str).to_numpy())


# ----------------------------------------------------------------------------- the unbiased grader

def probs(mean: np.ndarray, sd: np.ndarray | float) -> np.ndarray:
    """P(clip(round(X), 0, 6) = k) for X ~ N(mean, sd^2); n x 7."""
    sd = np.broadcast_to(np.asarray(sd, float), mean.shape)
    c = norm.cdf((CUTS[None, :] - mean[:, None]) / sd[:, None])
    n = len(mean)
    return np.diff(np.hstack([np.zeros((n, 1)), c, np.ones((n, 1))]), axis=1)


def wmom(x, w):
    return float(np.sum(w * x) / np.sum(w))


def _proj(w, Xd):
    if Xd is None:
        return None
    sw = np.sqrt(w)
    return Xd, np.linalg.pinv(Xd * sw[:, None]), sw


def _resid(x, w, pj):
    """Residual of x after WLS on the draw's group/prompt design (None: centring only)."""
    if pj is None:
        return x - wmom(x, w)
    Xd, Pi, sw = pj
    return x - Xd @ (Pi @ (x * sw))


def target_moments(M, H, w, pj=None):
    """Mean of M; cov(M, H) and var(M), within group when a design is given (FLOOR REVISION 1)."""
    rM, rH = _resid(M, w, pj), _resid(H, w, pj)
    return np.array([wmom(M, w), wmom(rM * rH, w), wmom(rM * rM, w)])


def model_moments(theta, m, v, H, w, pj=None):
    a, b, ls = theta
    P = probs(a + b * m, np.sqrt(b * b * v + np.exp(2 * ls)))
    EM, EM2 = P @ K, P @ (K * K)
    rE, rH = _resid(EM, w, pj), _resid(H, w, pj)
    var = wmom(rE * rE, w) + wmom(EM2 - EM * EM, w)
    return np.array([wmom(EM, w), wmom(rE * rH, w), var]), EM


def calibrate(M, H, w, m, v, start=None, Xd=None):
    """(alpha, beta, log sigma) so the unbiased grader reproduces M's mean, cov with H and variance.
    FLOOR REVISION 1: with Xd, the covariance and variance are WITHIN group (residuals on the
    group-mean design), so a real group bias in M, which is correlated with H across groups, is not
    absorbed into the unbiased grader's slope (revision 0 absorbed ~15-19% of a planted bias)."""
    pj = _proj(w, Xd)
    tgt = target_moments(M, H, w, pj)
    if start is None:
        b0 = 1.0
        start = np.array([tgt[0] - b0 * wmom(m, w), b0, np.log(0.6)])
    scale = np.array([0.1, 0.1, 0.1])
    r = least_squares(lambda th: (model_moments(th, m, v, H, w, pj)[0] - tgt) / scale, start, method="lm")
    mm, EM = model_moments(r.x, m, v, H, w, pj)
    return {"alpha": float(r.x[0]), "beta": float(r.x[1]), "sigma": float(np.exp(r.x[2])),
            "fit_err": float(np.max(np.abs(mm - tgt))), "theta": r.x}, EM


# ----------------------------------------------------------------------------- estimators

def masks(groups, ok, ax):
    f, r = AXES[ax]
    return ok & (groups[ax] == f), ok & (groups[ax] == r)


def observed_gap(M, H, strat, groups, ok, wt, ax):
    isf, isr = masks(groups, ok, ax)
    return AG.strat_diff(M - H, strat, isf, isr, wt)


def kelley_reg(M, m, groups, ok, wt, ax):
    isf, isr = masks(groups, ok, ax)
    s = isf | isr
    X = np.column_stack([np.ones(s.sum()), m[s], m[s] ** 2, isf[s].astype(float)])
    sw = np.sqrt(wt[s])
    coef, *_ = np.linalg.lstsq(X * sw[:, None], M[s] * sw, rcond=None)
    return float(coef[3])


def eiv(M, H, groups, ok, wt, ax, cm: CorpusModel, rho):
    isf, isr = masks(groups, ok, ax)
    s = isf | isr
    w = wt[s]
    dM = wmom(M[isf], wt[isf]) - wmom(M[isr], wt[isr])
    dH = wmom(H[isf], wt[isf]) - wmom(H[isr], wt[isr])
    X = np.column_stack([np.ones(s.sum()), H[s], isf[s].astype(float)])
    sw = np.sqrt(w)
    coef, *_ = np.linalg.lstsq(X * sw[:, None], M[s] * sw, rcond=None)
    rho_wa = 1 - cm.var_u(rho) / cm.var_within_axis[ax]
    beta = coef[1] / rho_wa
    return {"gamma": float(dM - beta * dH), "dM": float(dM), "dH": float(dH), "ratio": float(dM / dH),
            "beta_eiv": float(beta), "b_obs": float(coef[1])}


def estimate(M, H, strat, groups, ok, wt, mu, cm: CorpusModel, rho, axes=tuple(AXES), start=None, Xd=None):
    """Everything at one rho on one (possibly resampled) data set."""
    m, v, rw = cm.kelley(H, mu, rho)
    cal, EM = calibrate(M[ok], H[ok], wt[ok], m[ok], v, start, None if Xd is None else Xd[ok])
    EMfull = np.full(len(H), np.nan)
    EMfull[ok] = EM
    out = {"cal": cal, "rho_w": rw, "axes": {}}
    for ax in axes:
        g = observed_gap(M, H, strat, groups, ok, wt, ax)
        isf, isr = masks(groups, ok, ax)
        A = AG.strat_diff(EMfull - H, strat, isf, isr, wt)["diff"]
        e = eiv(M, H, groups, ok, wt, ax, cm, rho)
        out["axes"][ax] = {"G_obs": g["diff"], "coverage": g["coverage"], "A": A, "C": g["diff"] - A,
                           "kelley_reg": kelley_reg(M, m, groups, ok, wt, ax), "eiv": e["gamma"],
                           "eiv_detail": e}
    return out


def cell_index(cells):
    return [np.flatnonzero(cells == c) for c in np.unique(cells)]


def bootstrap(M, H, strat, groups, ok, wt, cells, mu, cm, rho_spec, B, rng, axes=tuple(AXES), Xd=None):
    """rho_spec: a float (fixed) or a (lo, hi) prior."""
    idx_c = cell_index(cells)
    rec = {ax: {k: [] for k in ("G_obs", "A", "C", "kelley_reg", "eiv")} for ax in axes}
    start = None
    for _ in range(B):
        pick = np.concatenate([i[rng.integers(0, len(i), len(i))] for i in idx_c])
        rho = rng.uniform(*rho_spec) if isinstance(rho_spec, tuple) else rho_spec
        gs = {k: v[pick] for k, v in groups.items()}
        e = estimate(M[pick], H[pick], strat[pick], gs, ok[pick], wt[pick], mu[pick], cm, rho, axes, start,
                     None if Xd is None else Xd[pick])
        start = e["cal"]["theta"]
        for ax in axes:
            for k in rec[ax]:
                rec[ax][k].append(e["axes"][ax][k])
    out = {}
    for ax in axes:
        out[ax] = {}
        for k, v in rec[ax].items():
            v = np.asarray(v)
            out[ax][k] = {"lo": float(np.nanpercentile(v, 2.5)), "hi": float(np.nanpercentile(v, 97.5)),
                          "sd": float(np.nanstd(v, ddof=1)), "mean": float(np.nanmean(v))}
    return out


BRACKET = (0.65, 0.70, 0.75, 0.80, 0.85, 0.90)


def bracket_verdict(by: dict) -> str:
    """AMENDMENT 1: the headline is the fixed-rho verdict across the bracket, not the prior interval's."""
    vs = [by[r] for r in BRACKET]
    if len(set(vs)) == 1:
        return vs[0]
    parts, prev = [], None
    for r, v in zip(BRACKET, vs):
        if v != prev:
            parts.append(f"{v} from {r:.2f}")
            prev = v
    return "RHO-DEPENDENT (" + "; ".join(parts) + ")"


def verdict(G_obs: float, lo: float, hi: float) -> str:
    s = 1.0 if G_obs >= 0 else -1.0
    a, b = sorted((s * lo, s * hi))       # interval in the direction of the observed gap
    g = s * G_obs                          # > 0
    has0 = a <= 0 <= b
    hasG = a <= g <= b
    if b < 0:
        return "OVERCORRECTED"
    if has0 and hasG:
        return "UNRESOLVED"
    if has0:
        return "ARTEFACT-EXPLAINS-IT"
    if hasG:
        return "NOT-ARTEFACT"
    return "PARTLY-ARTEFACT"


# ----------------------------------------------------------------------------- the floor

def draw_covariates(path: Path):
    """Covariates only (groups, prompt, quota cell, design weights): no human or grader score is used."""
    dump = json.loads(path.read_text())
    rows = dump["rows"]
    groups = {k: np.array([r["groups"][k] for r in rows]) for k in (*AXES, "race")}
    prompt = np.array([r["prompt"] for r in rows])
    cells = np.array([r["cell"] for r in rows])
    return rows, groups, prompt, cells


def planted_bias(groups, d_ell, d_dis):
    return -d_ell * (groups["ell"] == "Yes") - d_dis * (groups["disability"] == AXES["disability"][0])


def exact_gamma(T, groups, wt, d_ell, d_dis, ax, alpha=F_ALPHA, beta=F_BETA, sigma=F_SIGMA,
                by_true_stratum=False):
    bias = planted_bias(groups, d_ell, d_dis)
    E1 = probs(alpha + beta * T + bias, sigma) @ K
    E0 = probs(alpha + beta * T, sigma) @ K
    d = E1 - E0
    f, r = AXES[ax]
    isf, isr = groups[ax] == f, groups[ax] == r
    if not by_true_stratum:
        return wmom(d[isf], wt[isf]) - wmom(d[isr], wt[isr])
    # FLOOR REVISION 1: the estimand is a gap AT EQUAL TRUE SCORE, so the truth is the planted bias
    # post-stratified on true-score strata (the estimator's strata applied to rint(T)). Revision 0's
    # unconditional difference differs from it when a bias planted on one axis reaches a correlated
    # axis through composition, which differs at equal T from overall.
    st = np.clip(np.rint(T).astype(int), 1, 5) - 1
    return AG.strat_diff(d, st, isf, isr, wt)["diff"]


def synth_world(mu, cm: CorpusModel, rho_true, groups, d_ell, d_dis, rng):
    n = len(mu)
    vu = cm.var_u(rho_true)
    T = mu + rng.normal(0, np.sqrt(cm.s_w2 - vu), n)
    H = np.clip(np.rint(T + rng.normal(0, np.sqrt(vu), n)), 1, 6)
    X = F_ALPHA + F_BETA * T + rng.normal(0, F_SIGMA, n) + planted_bias(groups, d_ell, d_dis)
    M = np.clip(np.rint(X), 0, 6)
    return T, H, M


def realised_rho(mu_pool, wt_pool, cm, rho_true, rng, n=200_000):
    pick = rng.choice(len(mu_pool), n, p=wt_pool / wt_pool.sum())
    mu = mu_pool[pick]
    vu = cm.var_u(rho_true)
    T = mu + rng.normal(0, np.sqrt(cm.s_w2 - vu), n)
    H = np.clip(np.rint(T + rng.normal(0, np.sqrt(vu), n)), 1, 6)
    return float(np.corrcoef(T, H)[0, 1] ** 2)


def planted_for(target, mu, wt, cm, rng, tol=0.002):
    """The continuous reliability whose rounded, clipped H has realised reliability `target`."""
    lo, hi = target, min(0.995, 1 - (1 - target) * 0.3)
    for _ in range(30):
        mid = (lo + hi) / 2
        if realised_rho(mu, wt, cm, mid, np.random.default_rng(7), 100_000) < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2


def run_floor(dump_path: Path) -> dict:
    rng = np.random.default_rng(SEED)
    cm = load_corpus_model()
    _, corpus_g = AG.load_corpus()
    rows, groups, prompt, cells = draw_covariates(dump_path)
    wt = AG.design_weights(rows, AG.cell_share(corpus_g))
    mu = cm.mu(groups, prompt)
    n = len(mu)
    ok = np.ones(n, bool)
    worlds = []
    crit = {"F1": True, "F2": True, "F3": True, "F4": True, "F5": True}
    for target in F_RHOS:
        rt = planted_for(target, mu, wt, cm, rng)
        rr = realised_rho(mu, wt, cm, rt, rng)
        for d in F_DELTAS:
            rec = {ax: {"gamma_true": [], "G_obs": [], "C_true_rho": [], "C_wrong_rho": [], "C_prior": [],
                        "covered": [], "below0": [], "verdict": []} for ax in PAPER_AXES}
            A_check = {ax: [] for ax in PAPER_AXES}
            for _ in range(F_REPS):
                T, H, M = synth_world(mu, cm, rt, groups, d, d, rng)
                strat = np.clip(H.astype(int), 1, 5) - 1
                e_true = estimate(M, H, strat, groups, ok, wt, mu, cm, rr, PAPER_AXES)
                e_wrong = estimate(M, H, strat, groups, ok, wt, mu, cm, 0.75, PAPER_AXES)
                e_prior = estimate(M, H, strat, groups, ok, wt, mu, cm, float(np.mean(PRIOR)), PAPER_AXES)
                bs = bootstrap(M, H, strat, groups, ok, wt, cells, mu, cm, PRIOR, F_BOOT, rng, PAPER_AXES)
                for ax in PAPER_AXES:
                    gt = exact_gamma(T, groups, wt, d, d, ax)
                    lo, hi = bs[ax]["C"]["lo"], bs[ax]["C"]["hi"]
                    r_ = rec[ax]
                    r_["gamma_true"].append(gt)
                    r_["G_obs"].append(e_true["axes"][ax]["G_obs"])
                    r_["C_true_rho"].append(e_true["axes"][ax]["C"])
                    r_["C_wrong_rho"].append(e_wrong["axes"][ax]["C"])
                    r_["C_prior"].append(e_prior["axes"][ax]["C"])
                    r_["covered"].append(lo <= gt <= hi)
                    r_["below0"].append(hi < 0)
                    r_["verdict"].append(verdict(e_true["axes"][ax]["G_obs"], lo, hi))
                    A_check[ax].append(e_true["axes"][ax]["A"])
            summ = {}
            for ax in PAPER_AXES:
                r_ = rec[ax]
                gt = float(np.mean(r_["gamma_true"]))
                s = {"gamma_true": gt, "G_obs_mean": float(np.mean(r_["G_obs"])),
                     "C_true_rho_mean": float(np.mean(r_["C_true_rho"])),
                     "bias_true_rho": float(np.mean(r_["C_true_rho"]) - gt),
                     "C_wrong_rho_0.75_mean": float(np.mean(r_["C_wrong_rho"])),
                     "C_prior_mid_mean": float(np.mean(r_["C_prior"])),
                     "coverage": float(np.mean(r_["covered"])), "below0": float(np.mean(r_["below0"])),
                     "A_mean": float(np.mean(A_check[ax])),
                     "A_analytic": float(F_BETA * (1 - cm.rho_w(rr)) * (cm.group_means[ax][0] - cm.group_means[ax][1])),
                     "artefact_mc": float(np.mean(np.array(r_["G_obs"]) - np.array(r_["gamma_true"]))),
                     "verdicts": {v: r_["verdict"].count(v) / F_REPS for v in sorted(set(r_["verdict"]))}}
                summ[ax] = s
                if abs(s["bias_true_rho"]) > 0.03:
                    crit["F1"] = False
                if ax in ("ell", "disability") and s["coverage"] < 0.90:
                    crit["F2"] = False
                if d == 0 and s["below0"] > 0.08:
                    crit["F3"] = False
                if d == 0.25 and ax in ("ell", "disability") and s["below0"] < 0.80:
                    crit["F4"] = False
                if d == 0 and target == 0.65 and ax in ("ell", "disability") and s["G_obs_mean"] > -0.05:
                    crit["F5"] = False
            worlds.append({"rho_target": target, "rho_planted": rt, "rho_realised": rr, "delta": d, "axes": summ})
            print(json.dumps({"rho": target, "rho_realised": round(rr, 3), "delta": d,
                              **{ax: {k: round(v, 3) for k, v in summ[ax].items() if isinstance(v, float)}
                                 for ax in PAPER_AXES}}), flush=True)
    # size of the control: the d = 0 world's artefact against the planted 0.25 and the observed gaps
    from shared.controls import check_control_scale
    null_art = abs(next(w for w in worlds if w["rho_target"] == 0.65 and w["delta"] == 0)["axes"]["ell"]["G_obs_mean"])
    ctl = check_control_scale({"planted_0.25": 0.25, "observed_ell_qwen": 0.242, "null_artefact_rho0.65": null_art},
                              ["null_artefact_rho0.65"], strict=False)
    return {"pass": all(crit.values()), "criteria": crit, "worlds": worlds,
            "control_scale": {k: v for k, v in ctl.items() if k != "covers"} if isinstance(ctl, dict) else str(ctl),
            "corpus_model": {"s_w2": cm.s_w2, "var_H": cm.var_H, "group_means": cm.group_means},
            "grader": {"alpha": F_ALPHA, "beta": F_BETA, "sigma": F_SIGMA}, "reps": F_REPS, "boot": F_BOOT}


def _floor_world_rev1(args):
    """One floor world under revision 1: within-group calibration, fixed-rho interval at the true rho."""
    target, d, seed, dump_path = args
    rng = np.random.default_rng(seed)
    cm = load_corpus_model()
    _, corpus_g = AG.load_corpus()
    rows, groups, prompt, cells = draw_covariates(Path(dump_path))
    wt = AG.design_weights(rows, AG.cell_share(corpus_g))
    mu = cm.mu(groups, prompt)
    Xd = cm.design(groups, prompt)
    ok = np.ones(len(mu), bool)
    rt = planted_for(target, mu, wt, cm, rng)
    rr = realised_rho(mu, wt, cm, rt, rng)
    keys = ("gamma_true", "G_obs", "C", "C_wrong_lo", "C_wrong_hi", "kelley_reg", "eiv", "covered", "below0",
            "verdict", "A")
    rec = {ax: {k: [] for k in keys} for ax in PAPER_AXES}
    for _ in range(F_REPS):
        T, H, M = synth_world(mu, cm, rt, groups, d, d, rng)
        strat = np.clip(H.astype(int), 1, 5) - 1
        e = estimate(M, H, strat, groups, ok, wt, mu, cm, rr, PAPER_AXES, Xd=Xd)
        e_lo = estimate(M, H, strat, groups, ok, wt, mu, cm, max(rr - 0.10, 0.5), PAPER_AXES, Xd=Xd)
        e_hi = estimate(M, H, strat, groups, ok, wt, mu, cm, min(rr + 0.10, 0.97), PAPER_AXES, Xd=Xd)
        bs = bootstrap(M, H, strat, groups, ok, wt, cells, mu, cm, rr, F_BOOT, rng, PAPER_AXES, Xd=Xd)
        for ax in PAPER_AXES:
            gt = exact_gamma(T, groups, wt, d, d, ax, by_true_stratum=True)
            lo, hi = bs[ax]["C"]["lo"], bs[ax]["C"]["hi"]
            r_ = rec[ax]
            for k, v in (("gamma_true", gt), ("G_obs", e["axes"][ax]["G_obs"]), ("C", e["axes"][ax]["C"]),
                         ("C_wrong_lo", e_lo["axes"][ax]["C"]), ("C_wrong_hi", e_hi["axes"][ax]["C"]),
                         ("kelley_reg", e["axes"][ax]["kelley_reg"]), ("eiv", e["axes"][ax]["eiv"]),
                         ("covered", lo <= gt <= hi), ("below0", hi < 0),
                         ("verdict", verdict(e["axes"][ax]["G_obs"], lo, hi)), ("A", e["axes"][ax]["A"])):
                r_[k].append(v)
    summ = {}
    for ax in PAPER_AXES:
        r_ = rec[ax]
        gt = float(np.mean(r_["gamma_true"]))
        summ[ax] = {"gamma_true": gt, "G_obs_mean": float(np.mean(r_["G_obs"])),
                    "C_mean": float(np.mean(r_["C"])), "bias": float(np.mean(r_["C"]) - gt),
                    "bias_kelley_reg": float(np.mean(r_["kelley_reg"]) - gt),
                    "bias_eiv": float(np.mean(r_["eiv"]) - gt),
                    "C_mean_rho_minus_0.10": float(np.mean(r_["C_wrong_lo"])),
                    "C_mean_rho_plus_0.10": float(np.mean(r_["C_wrong_hi"])),
                    "coverage": float(np.mean(r_["covered"])), "below0": float(np.mean(r_["below0"])),
                    "A_mean": float(np.mean(r_["A"])),
                    "A_analytic": float(F_BETA * (1 - cm.rho_w(rr)) * (cm.group_means[ax][0] - cm.group_means[ax][1])),
                    "artefact_mc": float(np.mean(np.array(r_["G_obs"]) - np.array(r_["gamma_true"]))),
                    "sd_C": float(np.std(r_["C"], ddof=1)),
                    "verdicts": {v: r_["verdict"].count(v) / F_REPS for v in sorted(set(r_["verdict"]))}}
    w = {"rho_target": target, "rho_planted": rt, "rho_realised": rr, "delta": d, "axes": summ}
    print(json.dumps({"rho": target, "delta": d, **{ax: {k: round(v, 3) for k, v in summ[ax].items()
                                                          if isinstance(v, float)} for ax in PAPER_AXES}}), flush=True)
    return w


def run_floor_rev1(dump_path: Path, procs: int = 3) -> dict:
    from multiprocessing import Pool
    jobs = [(t, d, SEED + 100 * i + j, str(dump_path)) for i, t in enumerate(F_RHOS) for j, d in enumerate(F_DELTAS)]
    with Pool(procs) as pool:
        worlds = pool.map(_floor_world_rev1, jobs)
    crit = {"F1": True, "F2": True, "F3": True, "F4": True, "F5": True}
    for w in worlds:
        for ax, s in w["axes"].items():
            if abs(s["bias"]) > 0.03:
                crit["F1"] = False
            if ax in ("ell", "disability") and s["coverage"] < 0.90:
                crit["F2"] = False
            if w["delta"] == 0 and s["below0"] > 0.08:
                crit["F3"] = False
            if w["delta"] == 0.25 and ax in ("ell", "disability") and s["below0"] < 0.80:
                crit["F4"] = False
            if w["delta"] == 0 and w["rho_target"] == 0.65 and ax in ("ell", "disability") and s["G_obs_mean"] > -0.05:
                crit["F5"] = False
    from shared.controls import check_control_scale
    null_art = abs(next(w for w in worlds if w["rho_target"] == 0.65 and w["delta"] == 0)["axes"]["ell"]["G_obs_mean"])
    ctl = check_control_scale({"planted_0.25": 0.25, "observed_ell_qwen": 0.242, "null_artefact_rho0.65": null_art},
                              ["null_artefact_rho0.65"], strict=False)
    return {"revision": 1, "pass": all(crit.values()), "criteria": crit, "worlds": worlds,
            "control_scale": {k: v for k, v in ctl.items() if k != "covers"} if isinstance(ctl, dict) else str(ctl),
            "grader": {"alpha": F_ALPHA, "beta": F_BETA, "sigma": F_SIGMA}, "reps": F_REPS, "boot": F_BOOT,
            "interval": "fixed rho at the realised true rho", "calibration": "within group"}


def run_floor_recheck(dump_path: Path, procs: int = 3) -> dict:
    """AMENDMENT 2: the one failed F2 cell (ell, realised rho 0.85, d = 0) re-run with 300 fresh
    replicates (3 x 100, new seeds). Pass if the pooled coverage on ell is >= 0.90."""
    from multiprocessing import Pool
    jobs = [(0.85, 0.0, SEED + 9000 + k, str(dump_path)) for k in range(3)]
    with Pool(procs) as pool:
        ws = pool.map(_floor_world_rev1, jobs)
    cov = {ax: float(np.mean([w["axes"][ax]["coverage"] for w in ws])) for ax in PAPER_AXES}
    below = {ax: float(np.mean([w["axes"][ax]["below0"] for w in ws])) for ax in PAPER_AXES}
    bias = {ax: float(np.mean([w["axes"][ax]["bias"] for w in ws])) for ax in PAPER_AXES}
    return {"amendment": 2, "world": {"rho_target": 0.85, "delta": 0.0}, "reps": 3 * F_REPS,
            "coverage": cov, "below0": below, "bias": bias, "pass": cov["ell"] >= 0.90, "parts": ws}


# ----------------------------------------------------------------------------- the run

def load_dump(path: Path, corpus_g):
    dump = json.loads(path.read_text())
    if str(dump.get("model", "")).startswith("fake:") or dump.get("dryRun"):
        raise SystemExit(f"{path} is a fake or dry-run dump")
    rows = dump["rows"]
    d = AG.Data.from_rows(rows, AG.cell_share(corpus_g))
    prompt = np.array([r["prompt"] for r in rows])
    cells = np.array([r["cell"] for r in rows])
    ids = np.array([r["id"] for r in rows])
    return dump, d, prompt, cells, ids


def triad(dq, dg, idq, idg, mu_q, mu_g):
    """Triad reliability of H from H, Qwen, GPT on common essays (none arm), raw and within-group."""
    common = sorted(set(idq[np.isfinite(dq.arms["none"])]) & set(idg[np.isfinite(dg.arms["none"])]))
    iq = {k: i for i, k in enumerate(idq)}
    ig = {k: i for i, k in enumerate(idg)}
    a = np.array([iq[k] for k in common])
    b = np.array([ig[k] for k in common])
    H, Q, G, w = dq.h[a], dq.arms["none"][a], dg.arms["none"][b], dq.wt[a]
    mu = mu_q[a]

    def c(x, y):
        return wmom((x - wmom(x, w)) * (y - wmom(y, w)), w)

    raw = c(H, Q) * c(H, G) / (c(Q, G) * c(H, H))
    # within: residualise each on the group-mean model's prediction (WLS on mu)
    def res(x):
        X = np.column_stack([np.ones(len(x)), mu])
        sw = np.sqrt(w)
        coef, *_ = np.linalg.lstsq(X * sw[:, None], x * sw, rcond=None)
        return x - X @ coef
    Hr, Qr, Gr = res(H), res(Q), res(G)
    within = c(Hr, Qr) * c(Hr, Gr) / (c(Qr, Gr) * c(Hr, Hr))
    return {"n_common": len(common), "rho_triad_raw": float(raw), "rho_triad_within": float(within),
            "corr_HQ": float(c(H, Q) / np.sqrt(c(H, H) * c(Q, Q))), "corr_HG": float(c(H, G) / np.sqrt(c(H, H) * c(G, G))),
            "corr_QG": float(c(Q, G) / np.sqrt(c(Q, Q) * c(G, G)))}


def run(paths: list[Path]) -> dict:
    floor, recheck = OUT / "floor-rev1.json", OUT / "floor-recheck.json"
    f1 = json.loads(floor.read_text()) if floor.exists() else {}
    crit = f1.get("criteria", {})
    others_pass = bool(crit) and all(v for k, v in crit.items() if k != "F2")
    f2_ok = crit.get("F2") or (recheck.exists() and json.loads(recheck.read_text())["pass"])
    if not (others_pass and f2_ok):
        raise SystemExit("the revision-1 floor (with the amendment-2 recheck of F2) did not pass: no grader score is read")
    prev = json.loads((REPO / "studies/measurement/grader-attainment-groups/out/results.json").read_text())
    cm = load_corpus_model()
    _, corpus_g = AG.load_corpus()
    rng = np.random.default_rng(SEED)
    per_model, loaded = {}, {}
    for p in paths:
        dump, d, prompt, cells, ids = load_dump(p, corpus_g)
        model = dump["model"]
        M, H, ok = d.arms["none"], d.h, d.complete
        mu = cm.mu(d.groups, prompt)
        Xd = cm.design(d.groups, prompt)
        loaded[model] = (d, ids, mu)
        # reproduce the reported gaps first (what produced the value)
        for ax in AXES:
            g = observed_gap(M, H, d.stratum, d.groups, ok, d.wt, ax)["diff"]
            ref = prev["per_model"][model]["none_arm_residual_gap"][ax]["diff"]
            assert abs(g - ref) < 1e-9, (model, ax, g, ref)
        point = {str(r): estimate(M, H, d.stratum, d.groups, ok, d.wt, mu, cm, r, Xd=Xd) for r in RHO_GRID}
        mid = estimate(M, H, d.stratum, d.groups, ok, d.wt, mu, cm, float(np.mean(PRIOR)), Xd=Xd)
        low = {str(r): estimate(M, H, d.stratum, d.groups, ok, d.wt, mu, cm, r, Xd=Xd) for r in LOW_RHO}
        bs_prior = bootstrap(M, H, d.stratum, d.groups, ok, d.wt, cells, mu, cm, PRIOR, B_PRIOR, rng, Xd=Xd)
        bs_grid = {str(r): bootstrap(M, H, d.stratum, d.groups, ok, d.wt, cells, mu, cm, r, B_GRID, rng, Xd=Xd)
                   for r in RHO_GRID}
        # Monte Carlo check of the exact artefact at rho = 0.75
        cal = point["0.75"]["cal"]
        m, v, rw = cm.kelley(H, mu, 0.75)
        mc = {ax: [] for ax in AXES}
        for _ in range(200):
            T = m + rng.normal(0, np.sqrt(v), len(m))
            Ms = np.clip(np.rint(cal["alpha"] + cal["beta"] * T + rng.normal(0, cal["sigma"], len(m))), 0, 6)
            for ax in AXES:
                mc[ax].append(observed_gap(Ms, H, d.stratum, d.groups, ok, d.wt, ax)["diff"])
        axes = {}
        for ax in AXES:
            G = mid["axes"][ax]["G_obs"]
            pr = bs_prior[ax]
            rec = {
                "G_obs": G, "G_obs_ci": [pr["G_obs"]["lo"], pr["G_obs"]["hi"]],
                "A_prior_mid": mid["axes"][ax]["A"], "A_ci": [pr["A"]["lo"], pr["A"]["hi"]],
                "C_prior_mid": mid["axes"][ax]["C"], "C_ci": [pr["C"]["lo"], pr["C"]["hi"]],
                "share_artefact_mid": mid["axes"][ax]["A"] / G,
                "verdict_prior_interval": verdict(G, pr["C"]["lo"], pr["C"]["hi"]),
                "kelley_reg_mid": mid["axes"][ax]["kelley_reg"], "kelley_reg_ci": [pr["kelley_reg"]["lo"], pr["kelley_reg"]["hi"]],
                "verdict_kelley_reg": verdict(G, pr["kelley_reg"]["lo"], pr["kelley_reg"]["hi"]),
                "eiv_mid": mid["axes"][ax]["eiv"], "eiv_ci": [pr["eiv"]["lo"], pr["eiv"]["hi"]],
                "verdict_eiv": verdict(G, pr["eiv"]["lo"], pr["eiv"]["hi"]),
                "eiv_detail_mid": mid["axes"][ax]["eiv_detail"],
                "A_mc_rho0.75": float(np.mean(mc[ax])), "A_exact_rho0.75": point["0.75"]["axes"][ax]["A"],
                "A_analytic_rho0.75": float(cal["beta"] * (1 - rw) * (cm.group_means[ax][0] - cm.group_means[ax][1])),
                "A_audit_formula_rho0.75": float((1 - 0.75) * (cm.group_means[ax][0] - cm.group_means[ax][1])),
                "by_rho": {r: {"A": point[r]["axes"][ax]["A"], "C": point[r]["axes"][ax]["C"],
                               "C_ci": [bs_grid[r][ax]["C"]["lo"], bs_grid[r][ax]["C"]["hi"]],
                               "verdict": verdict(G, bs_grid[r][ax]["C"]["lo"], bs_grid[r][ax]["C"]["hi"]),
                               "kelley_reg": point[r]["axes"][ax]["kelley_reg"], "eiv": point[r]["axes"][ax]["eiv"]}
                           for r in point},
            }
            # POST HOC (added after the first run, prompted by the triad bound of ~0.3-0.4): point
            # estimates below the grid, so the break-even rho can be located. Not part of any verdict.
            rec["low_rho_points"] = {str(r): {"A": low[str(r)]["axes"][ax]["A"], "C": low[str(r)]["axes"][ax]["C"]}
                                     for r in LOW_RHO}
            # break-even rho: where the point C crosses 0 (linear interpolation on low + grid)
            grid = (*LOW_RHO, *RHO_GRID)
            cs = [low[str(r)]["axes"][ax]["C"] if r in LOW_RHO else point[str(r)]["axes"][ax]["C"] for r in grid]
            be = None
            for (r0, c0), (r1, c1) in zip(zip(grid, cs), zip(grid[1:], cs[1:])):
                if c0 * c1 <= 0 and c0 != c1:
                    be = r0 + (0 - c0) * (r1 - r0) / (c1 - c0)
                    break
            rec["break_even_rho"] = be
            rec["verdict"] = bracket_verdict({r: rec["by_rho"][str(r)]["verdict"] for r in BRACKET})
            for meth in ("kelley_reg", "eiv"):
                rec[f"verdict_{meth}_bracket"] = bracket_verdict(
                    {r: verdict(G, bs_grid[str(r)][ax][meth]["lo"], bs_grid[str(r)][ax][meth]["hi"]) for r in BRACKET})
                for r in RHO_GRID:
                    rec["by_rho"][str(r)][f"{meth}_ci"] = [bs_grid[str(r)][ax][meth]["lo"], bs_grid[str(r)][ax][meth]["hi"]]
            axes[ax] = rec
        per_model[model] = {"n": int(ok.sum()), "calibration_by_rho": {r: {k: point[r]["cal"][k] for k in
                                                                           ("alpha", "beta", "sigma", "fit_err")}
                                                                       for r in point},
                            "rho_w_by_rho": {r: point[r]["rho_w"] for r in point}, "axes": axes}
        print(model, {ax: (round(axes[ax]["G_obs"], 3), round(axes[ax]["C_prior_mid"], 3),
                           [round(x, 3) for x in axes[ax]["C_ci"]], axes[ax]["verdict"]) for ax in AXES}, flush=True)
    models = list(per_model)
    across = {}
    for ax in AXES:
        vs = [per_model[m]["axes"][ax]["verdict"] for m in models]
        across[ax] = vs[0] if len(set(vs)) == 1 else " / ".join(vs)
    tri = None
    if len(loaded) == 2:
        (dq, iq, muq), (dg, ig, mug) = loaded[models[0]], loaded[models[1]]
        tri = triad(dq, dg, iq, ig, muq, mug)
    betas = [per_model[m]["calibration_by_rho"]["0.75"]["beta"] for m in models]
    gem = {}
    for ax, G in (("ell", -0.275), ("economic", -0.163)):
        dmu = cm.group_means[ax][0] - cm.group_means[ax][1]
        gem[ax] = {"G_obs_2026-09-16": G, "dmu_corpus": dmu,
                   "A_analytic": {str(r): [float(b * (1 - cm.rho_w(r)) * dmu) for b in (min(betas), max(betas))]
                                  for r in (0.65, 0.75, 0.90)}}
    return {"per_model": per_model, "across": across, "triad_reliability": tri, "gemini_projection": gem,
            "corpus_model": {"s_w2": cm.s_w2, "var_H": cm.var_H, "group_means": cm.group_means,
                             "var_within_axis": cm.var_within_axis},
            "prior": PRIOR, "B_prior": B_PRIOR, "B_grid": B_GRID}


# ----------------------------------------------------------------------------- label-by-group check

def run_label_check(dump_path: Path) -> dict:
    if not (OUT / "results.json").exists():
        raise SystemExit("run --run first")
    rng = np.random.default_rng(SEED + 5)
    cm = load_corpus_model()
    _, corpus_g = AG.load_corpus()
    dump, d, prompt, cells, ids = load_dump(dump_path, corpus_g)
    mu = cm.mu(d.groups, prompt)
    wt = d.wt
    # the real data's slope of (low - none) on H (complete essays, design-weighted)
    y = d.contrast("D_low")
    ok = d.complete
    X = np.column_stack([np.ones(ok.sum()), d.h[ok]])
    sw = np.sqrt(wt[ok])
    coef, *_ = np.linalg.lstsq(X * sw[:, None], y[ok] * sw, rcond=None)
    slope_obs = float(coef[1])
    L0 = float(wmom(y[ok], wt[ok]))
    reps = 200
    out = {"model": dump["model"], "slope_low_minus_none_on_H": slope_obs, "L0": L0, "scenarios": []}
    alpha, beta, case_sd, call_sd = F_ALPHA, F_BETA, 0.5, 0.3
    allok = np.ones(len(mu), bool)

    def world(rho, L1, d_low):
        vu = cm.var_u(rho)
        res = {ax: {"D_low": [], "true": []} for ax in PAPER_AXES}
        for _ in range(reps):
            n = len(mu)
            T = mu + rng.normal(0, np.sqrt(cm.s_w2 - vu), n)
            H = np.clip(np.rint(T + rng.normal(0, np.sqrt(vu), n)), 1, 6)
            strat = np.clip(H.astype(int), 1, 5) - 1
            c = rng.normal(0, case_sd, n)
            plant = -planted_bias(d.groups, d_low, d_low)       # +d_low on ELL and disability
            base = alpha + beta * T + c
            Lt = L0 + L1 * (T - 3)
            none = np.clip(np.rint(base + rng.normal(0, call_sd, n)), 0, 6)
            low = np.clip(np.rint(base + Lt + plant + rng.normal(0, call_sd, n)), 0, 6)
            # exact expected (low - none) difference due to the plant, at fixed T and c (sd: call noise)
            e1 = probs(base + Lt + plant, call_sd) @ K
            e0 = probs(base + Lt, call_sd) @ K
            dd = e1 - e0
            for ax in PAPER_AXES:
                f, r = AXES[ax]
                isf, isr = d.groups[ax] == f, d.groups[ax] == r
                res[ax]["D_low"].append(AG.strat_diff(low - none, strat, isf, isr, wt)["diff"])
                res[ax]["true"].append(wmom(dd[isf], wt[isf]) - wmom(dd[isr], wt[isr]))
        return {ax: {"D_low_mean": float(np.mean(v["D_low"])), "true": float(np.mean(v["true"])),
                     "bias": float(np.mean(v["D_low"]) - np.mean(v["true"])),
                     "mc_se": float(np.std(v["D_low"], ddof=1) / np.sqrt(reps))} for ax, v in res.items()}

    ok_i = True
    for d_low in (0.0, 0.10):
        w = world(0.65, 0.0, d_low)
        out["scenarios"].append({"kind": "i: constant label effect", "rho": 0.65, "L1": 0.0, "d_low": d_low, "axes": w})
        for ax in ("ell", "disability"):
            if abs(w[ax]["bias"]) > 0.02:
                ok_i = False
    for rho in (0.65, 0.75, 0.90):
        L1 = slope_obs / cm.rho_w(rho)
        w = world(rho, L1, 0.0)
        out["scenarios"].append({"kind": "ii: label effect tracks true quality (measured slope)", "rho": rho,
                                 "L1": L1, "d_low": 0.0, "axes": w})
    out["criterion_i_pass"] = ok_i
    return out


def contrast_slopes(paths: list[Path]) -> dict:
    """POST HOC (added after scenario ii showed a bias): for every within-essay contrast on every dump,
    the design-weighted slope of the per-essay contrast on H and the analytic matching bias it implies
    for the group difference at equal human score, (slope / rho_w)(1 - rho_w)(mu_f - mu_r), set beside
    the measured contrast from grader-attainment-groups. Scenario ii's simulation checks the formula
    (+0.0245 simulated v +0.0226 analytic, ell at rho 0.75)."""
    cm = load_corpus_model()
    _, corpus_g = AG.load_corpus()
    prev = json.loads((REPO / "studies/measurement/grader-attainment-groups/out/results.json").read_text())
    out = {}
    for p in paths:
        dump, d, *_ = load_dump(p, corpus_g)
        model = dump["model"]
        rec = {}
        for name in AG.CONTRASTS:
            y = d.contrast(name)
            if y is None:
                continue
            ok = d.complete & np.isfinite(y)
            X = np.column_stack([np.ones(ok.sum()), d.h[ok]])
            sw = np.sqrt(d.wt[ok])
            coef, *_ = np.linalg.lstsq(X * sw[:, None], y[ok] * sw, rcond=None)
            r_ = {"slope_on_H": float(coef[1]), "by_axis": {}}
            for ax in PAPER_AXES:
                dmu = cm.group_means[ax][0] - cm.group_means[ax][1]
                meas = prev["per_model"][model]["axes"].get(name, {}).get(ax, {})
                r_["by_axis"][ax] = {"measured": meas.get("diff"), "measured_verdict": meas.get("verdict"),
                                     "implied_bias": {str(rho): float(coef[1] / cm.rho_w(rho) * (1 - cm.rho_w(rho)) * dmu)
                                                      for rho in (0.65, 0.75, 0.90)}}
            rec[name] = r_
        out[model] = rec
    return out


# ----------------------------------------------------------------------------- main

def dump_paths(args) -> list[Path]:
    # The dumps are model outputs of grader-attainment-groups (not a corpus), passed by path as that
    # study passes them. Runs on 2026-10-06 used an environment variable for the directory; it was
    # replaced by this argument so data/data_sources.py --check does not see an unregistered variable.
    if not args.dumps:
        raise SystemExit("pass --dumps <run-qwen.json> <run-gpt41mini.json> (the grader-attainment-groups "
                         "per-essay dumps, kept in the session scratchpad)")
    return args.dumps


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true", help="revision 0 (as pre-registered at 34e8110)")
    ap.add_argument("--floor-rev1", action="store_true")
    ap.add_argument("--floor-recheck", action="store_true", help="amendment 2")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--label-check", action="store_true")
    ap.add_argument("--dumps", type=Path, nargs="*")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    paths = dump_paths(a)
    if a.floor:
        res = run_floor(paths[0])
        (OUT / "floor-rev0.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({"pass": res["pass"], "criteria": res["criteria"]}, indent=1))
    elif a.floor_rev1:
        res = run_floor_rev1(paths[0])
        (OUT / "floor-rev1.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({"pass": res["pass"], "criteria": res["criteria"]}, indent=1))
    elif a.floor_recheck:
        res = run_floor_recheck(paths[0])
        (OUT / "floor-recheck.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({k: v for k, v in res.items() if k != "parts"}, indent=1))
    elif a.run:
        res = run(paths)
        (OUT / "results.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps({"across": res["across"], "triad": res["triad_reliability"]}, indent=1))
    elif a.label_check:
        res = run_label_check(paths[0])
        res["post_hoc_contrast_slopes"] = contrast_slopes(paths)
        (OUT / "label-check.json").write_text(json.dumps(res, indent=1, default=float))
        print(json.dumps(res, indent=1))
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
