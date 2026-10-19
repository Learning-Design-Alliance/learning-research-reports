"""PRE-REGISTERED: does remnant adjustment sharpen or overturn the four-order ASSISTments result, and how
large must a randomized edge-release trial be?

Written 2026-10-07, before any statistic of this design was computed on real data. Literature review
rank 8 (research/readiness/learning-graph-budget-2026/literature.md, strand 4: entry 4.17 Sales,
Prihar, Gagnon-Bartsch & Heffernan 2023 with its companion Gagnon-Bartsch et al. 2023; 4.18 Hedges &
Hedberg 2007; 4.19 Lortie-Forgues & Inglis 2019; strand-4 "Analyses" items 1-2; item 3 is noted, not run).

WHAT IT PROTECTS. Paper II's F4 includes studies/identifiability/core-vs-culture/order_swap.py:
experiment PSABANRN (osf.io/59shv) randomized 1,192 students to four orders of mean, median, range and
mode in one skill builder. Problems to mastery: omnibus permutation p 0.0035 (arm labels permuted over
students); T1-T3 -1.4947 problems, pre-registered 90% bootstrap interval [-2.2425, -0.7654]; verdict
ORDER MATTERS. This study asks whether that verdict survives, and how much it sharpens, when the
estimator uses a prediction built from students who were NOT in the experiment.

DATA (READS A CORPUS). $SCRATCH/osf-59shv/exp.zip, resolved through shared.paths.scratch_root() as
order_swap.py does (data id osf-59shv; ASSISTments Data Terms of Use: research use, no redistribution;
aggregates only). Each of its 88 inner PSA*.zip files holds exp_alogs.csv (one row per student
assignment), exp_plogs.csv (one row per problem attempt), exp_slogs.csv and priors.csv (per-student and
per-class activity on the platform BEFORE that experiment). Structural checks made before writing this
(no outcome read): student_id is shared across the 88 experiments (912 of PSABANRN's 1,193 students
appear in other experiments; 45,274 students appear in the others), so non-participants are
identifiable; PSABANRN's priors.csv carries class_id (69 classes) and teacher_id (40 teachers); no
pretest or posttest rows exist for PSABANRN. license.txt is NOT in this machine's copy (the registry
records it as shipped with the files); the terms applied are those data/data-sources.json records.
The 2012-13 export assist_rich.csv is NOT linked: it is a different school year under a different
anonymization, and nothing in either release maps one id space to the other, so a numeric id match
would be coincidence. It is not read.

ESTIMANDS (unchanged from order_swap.py). Units: students with assigned_condition Treatment 1-4, first
row by start_time. completion: end_time present (N = 1,192). problems to mastery: condition_problem_count
among completers (the original's estimand, a difference among completers; completion is itself an
outcome, so this contrast is not a pure randomized contrast; this study keeps it so that the
comparison with the original is like for like, and says so).

REMNANT MODEL (pre-treatment information only, fitted on non-participants).
  Remnant = every student-experiment pair in the other 87 experiments whose student never appears in
  PSABANRN (any row, including Not Assigned). First row per student per experiment, started only.
  Targets, standardized within each remnant experiment so skill builders of different length pool:
    ptm:  z-score of log1p(condition_problem_count) among completers; experiments with >= 50
          completers and >= 5 distinct counts only (fixed-length problem sets carry no signal).
    comp: completion minus the experiment's completion rate; experiments with >= 50 starters and a
          rate strictly between 0 and 1.
  Features (that experiment's priors.csv row, all recorded before the experiment): the 9 student_prior_*
  fields and the 13 numeric class_prior_* / class size fields; log1p for counts and times; a missing
  indicator per field, missing values set to the remnant mean; squares of the standardized fields.
  Model: ridge regression (closed form; no scikit-learn on this machine, and a deep model is not
  needed for a design-based estimator to stay unbiased). Penalty chosen from {0.1, 1, 10, 100, 1000}
  by 5-fold cross-validation grouped by experiment (shared.stats.grouped_folds) on the remnant only.
  Its grouped-CV R^2 on the remnant is reported. This is the "stated simpler variant" of Sales et al.
  (2023), who used a deep network on full action logs.
  The model is then applied to PSABANRN's own priors.csv, giving each participant x_ptm and x_comp.
  No PSABANRN outcome enters the model.

ESTIMATOR (ReLOOP-style, Wu & Gagnon-Bartsch 2018; Gagnon-Bartsch et al. 2023; Sales et al. 2023).
  For each arm a (n_a units of N, p_a = n_a / N), an OLS of Y on [1, x] within arm a. For a unit in
  arm a its prediction is leave-one-out (closed form via hat values); for a unit outside arm a it is
  the full arm-a fit. Then
      mu_a = mean over all N of yhat_a(i)  +  (1/N) * sum over i in a of (Y_i - yhat_a(i)) / p_a.
  Each unit's own outcome never enters its own prediction, so the estimator is unbiased under
  Bernoulli assignment whether or not the model is right (exactly), and nearly so under complete
  randomization. Pairwise contrasts are mu_a - mu_b; the unadjusted comparator is the arm mean
  (the original estimator).
  Interval: the original's type, a 90% percentile bootstrap resampling students within arm (5,000
  draws), the adjusted and unadjusted estimators computed on the SAME draws so their variance ratio
  is paired. Omnibus test: variance of the four mu_a, permutation p over 10,000 relabellings of arm
  across students (the unit assigned), the whole estimator refitted on each relabelling.

CONTROL (family-matched, deranged, sized like the treatment). The covariate is replaced by a
derangement of itself across the analysed students (no student keeps their own value): same values,
same distribution, so it is exactly the size of the real covariate, and carries no information about
the student. Expected: variance ratio in [0.95, 1.05] and the T1-T3 estimate inside the unadjusted 90%
interval. If not, CONTROL FAILED and the precision verdict is not interpretable.

DETECTION FLOOR (synthetic, run with --floor; shapes from the published arm sizes only).
  Arms of 247, 245, 206, 234 (the original's completer counts); covariate x ~ N(0, 1); latent
  L = r x + sqrt(1 - r^2) e; Y = 3 + Poisson(exp(1.0 + 0.55 L)) (a right-skewed count like problems to
  mastery); Treatment 3 receives +1.0 problem, so the planted T1-T3 is -1.0 exactly. r in {0, 0.35, 0.6}.
  200 simulations per r, 300 bootstrap draws and 500 permutations per simulation (fewer than the real
  run, stated, so the floor finishes on a shared machine). Passes if all hold:
    F1 bias:      |mean adjusted T1-T3 + 1.0| <= 0.05 at every r.
    F2 no harm:   paired variance ratio (adjusted / unadjusted) <= 1.05 at r = 0.
    F3 gain seen: variance ratio <= 0.85 at r = 0.6, and within 0.07 of 1 - R^2 (R^2 of Y on x).
    F4 coverage:  adjusted 90% interval covers -1.0 in 0.84-0.96 of simulations at every r.
    F5 power and sign: at r = 0.35, the adjusted interval lies below 0 in >= 0.80 of simulations and
                  above 0 in none.
    F6 null:      with no planted effect (r = 0.35), adjusted omnibus p < 0.05 in 0.02-0.09 of runs.
  If the floor fails, the remnant verdicts are UNANSWERABLE and the estimates are descriptive.

VERDICTS (thresholds and strings written before the run; signed where a direction exists).
  V1 order verdict, re-estimated: the order_swap.py rule on the adjusted statistics. ORDER MATTERS if
     adjusted omnibus p < 0.05 for completion or problems to mastery; ORDER INTERCHANGEABLE if not and
     every adjusted pairwise 90% interval lies inside the original margins (completion +-0.08,
     problems +-1.0); INCONCLUSIVE otherwise. "VERDICT UNCHANGED" if it equals ORDER MATTERS, else
     "VERDICT CHANGES".
  V2 headline pair, signed: T1-T3 CONFIRMED (Treatment 1 needs fewer problems) if the adjusted 90%
     upper bound < 0; T1-T3 REVERSED if the lower bound > 0; T1-T3 NOT CONFIRMED otherwise.
  V3 precision, on T1-T3 problems to mastery: PRECISION GAIN if the paired bootstrap variance ratio
     <= 0.95; NO MATERIAL GAIN if in (0.95, 1.05]; PRECISION LOSS if > 1.05. The medians over the six
     pairs of each outcome are reported beside it, with the implied effective-sample multiplier 1/ratio.
  Remnant sign check: the within-arm correlation of x_ptm with problems to mastery should be positive
     (students predicted to need more problems need more). If negative: REMNANT SIGN WRONG, reported.

POWER FOR A RANDOMIZED EDGE-RELEASE TRIAL (part 2; formulas fixed here).
  Two arms, equal allocation, two-sided alpha 0.05, power 0.80, normal approximation
  (Z = z_.975 + z_.80); effects d in {0.05, 0.10, 0.30} outcome SD (0.05-0.10 from Lortie-Forgues &
  Inglis 2019's 0.06 SD large-trial mean; 0.30 the single-study size).
  per-learner:  n per arm = 2 Z^2 / d^2 * eta_W, eta_W = 1 without and the realized paired variance
                ratio with the remnant covariate (V3 headline; the completion ratio also reported).
  per-class:    classes per arm J = 2 Z^2 / d^2 * [rho * eta_B + (1 - rho) * eta_W / m] (Hedges & Hedberg
                2007's variance-inflation form without the t-df correction), m in {median participant
                class size in PSABANRN, 20}. rho from (a) this experiment: one-way ANOVA ICC of each
                outcome over class_id (and teacher_id), 90% interval from 2,000 bootstrap draws over
                classes; (b) published planning values, used because the Clements-Sarama ICPSR data are
                not on this machine: Hedges & Hedberg's working paper (IPR WP-06-12, the draft of the
                2007 article) recommends rho 0.15-0.25 for national samples (e.g. grade-1 mathematics,
                unconditional, 0.228) and gives, with a pretest at both levels, eta_B 0.210 and
                eta_W 0.360 (grade-1 reading example). Those are SCHOOL-level values; a class ICC is at
                least as large in principle only if classes nest the same between-school variance, so
                they are planning anchors, not estimates. For our remnant covariate eta_B = 1 (no
                class-level gain assumed; conservative) and eta_W = the realized ratio.
  per-pair encounter (micro-randomized, NeCamp et al. 2019): each eligible encounter re-randomized
                with p = 0.5; with learner effects absorbed, total encounters N_e = 4 Z^2 / d^2 *
                (1 - rho_L) (large-K approximation), learners = N_e / K for K in {5, 20} encounters per
                learner. rho_L = learner ICC of first-attempt correctness across PSABANRN problem
                attempts (exp_plogs.csv), 90% interval over 2,000 learner bootstrap draws. d is then in
                encounter-level SD, which is NOT the learner-level SD; carryover between encounters
                (releasing one edge changes the next encounter) is assumed away and must be designed
                out or modelled. Stated, not solved.
  Comparison: studies/outcomes/lt-trials/out/arm_power.json's 291-385 per arm "for 0.10" is an ABSOLUTE
  accuracy difference of 0.10 at p 0.5-0.8 (0.20-0.25 SD), not 0.10 SD; the conversion is printed.
  This experiment's own MDE (Z * bootstrap SE) for T1-T3 is printed in problems and in SD, with and
  without the covariate.

WHAT IT CAN SAY. Whether a covariate that no participant's outcome touched changes the order verdict or
its precision; the clustering this experiment shows; sample sizes under stated assumptions.
WHAT IT CANNOT SAY. Which order is which (the release does not label Treatment 1-4); anything about a
dependency (the four measures are not prerequisites of one another); a class-randomized power figure
for kindergarten classrooms (no class-level data from those trials here); whether problems to mastery
among completers is a causal contrast (it conditions on an outcome).

PART 3 (noted for a later study, not run). The randomized mastery-requirement experiments are
PSAVTMK (2/4/5 in a row vs control), PSAZGQM (2/3/4 correct vs a fourth arm), PSAXJC2 (2/4 vs 3 in a
row, 46 students) and the choice/no-choice pair PSA59TP and PSAUTWT. Their posttests are on the SAME
skill. No row names a next skill. The only route to a next-skill outcome is that student_id is shared
across experiments: e.g. 206 of PSAVTMK's students appear later in PSAHQV and 195 in PSA2KPV. Whether
any later experiment's skill depends on the gated one has to be read from the experiment tag paths
(skill names are not written here) before such a study is registered.

    OMP_NUM_THREADS=1 python3 remnant.py --floor   # synthetic detection floor -> out/floor.json
    OMP_NUM_THREADS=1 python3 remnant.py           # real run -> out/remnant-result.json, out/power.json

CHANGES
  2026-10-07, after the floor's first run and before any real data were read: the floor passed but
  could not write out/floor.json (numpy booleans are not JSON-serializable). The checks are cast to
  bool and the null rejection count to int; no threshold, draw count or estimator changed. The floor
  was re-run with the same seed and gave the same numbers.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
import zipfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from shared.paths import scratch_root  # noqa: E402
from shared.stats import grouped_folds  # noqa: E402

OUT = HERE / "out"
SEED = 20261007
EXP = "PSABANRN"
ARMS = ["Treatment 1", "Treatment 2", "Treatment 3", "Treatment 4"]
MARGIN = {"completion": 0.08, "problems_to_mastery": 1.0}
Z = 1.959963984540054 + 0.8416212335729143
STUDENT_F = ["student_prior_started_skill_builder_count", "student_prior_completed_skill_builder_count",
             "student_prior_started_problem_set_count", "student_prior_completed_problem_set_count",
             "student_prior_completed_problem_count", "student_prior_median_first_response_time",
             "student_prior_median_time_on_task", "student_prior_average_correctness",
             "student_prior_average_attempt_count"]
CLASS_F = ["class_student_count", "class_prior_skill_builder_count", "class_prior_problem_set_count",
           "class_prior_skill_builder_percent_started", "class_prior_skill_builder_percent_completed",
           "class_prior_problem_set_percent_started", "class_prior_problem_set_percent_completed",
           "class_prior_completed_problem_count", "class_prior_median_time_on_task",
           "class_prior_median_first_response_time", "class_prior_average_correctness",
           "class_prior_average_attempt_count"]
FEATURES = STUDENT_F + CLASS_F
LOG = {f for f in FEATURES if "count" in f or "time" in f}


# ----------------------------------------------------------------------------- estimator

def _arm_fit(y, X):
    """OLS of y on X; returns coefficients and leave-one-out fitted values."""
    XtX_inv = np.linalg.pinv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)
    e = y - X @ beta
    loo = y - e / np.clip(1 - h, 1e-9, None)
    return beta, loo


def reloop_means(arm, y, x, k=4):
    """mu_a for each arm: LOO arm-wise OLS on [1, x], imputation plus inverse-probability residual."""
    N = len(y)
    X = np.column_stack([np.ones(N), x]) if x is not None else np.ones((N, 1))
    mus = np.empty(k)
    for a in range(k):
        m = arm == a
        na = m.sum()
        if na < X.shape[1] + 2:
            mus[a] = np.nan
            continue
        beta, loo = _arm_fit(y[m], X[m])
        pred = X @ beta
        pred[m] = loo
        mus[a] = pred.mean() + (y[m] - loo).sum() / N / (na / N)
    return mus


def arm_means(arm, y, k=4):
    return np.array([y[arm == a].mean() if (arm == a).any() else np.nan for a in range(k)])


def analyse(arm, y, x, rng, boots=5000, perms=10000, pairs_only=None):
    """Unadjusted and adjusted arm means, paired bootstrap pairwise intervals, permutation omnibus."""
    k = 4
    mu_u, mu_a = arm_means(arm, y), reloop_means(arm, y, x)
    idx = [np.nonzero(arm == a)[0] for a in range(k)]
    bu, ba = np.empty((boots, k)), np.empty((boots, k))
    for b in range(boots):
        s = np.concatenate([rng.choice(ix, len(ix)) for ix in idx])
        bu[b], ba[b] = arm_means(arm[s], y[s]), reloop_means(arm[s], y[s], x[s])
    pairs = {}
    for a in range(k):
        for c in range(a + 1, k):
            key = f"T{a + 1}-T{c + 1}"
            if pairs_only and key not in pairs_only:
                continue
            du, da = bu[:, a] - bu[:, c], ba[:, a] - ba[:, c]
            pairs[key] = {
                "unadjusted": {"diff": float(mu_u[a] - mu_u[c]), "lo90": float(np.percentile(du, 5)),
                               "hi90": float(np.percentile(du, 95)), "se": float(du.std(ddof=1))},
                "adjusted": {"diff": float(mu_a[a] - mu_a[c]), "lo90": float(np.percentile(da, 5)),
                             "hi90": float(np.percentile(da, 95)), "se": float(da.std(ddof=1))},
                "variance_ratio": float(da.var(ddof=1) / du.var(ddof=1)),
            }
    res = {"n": [int(len(ix)) for ix in idx], "means_unadjusted": mu_u.tolist(),
           "means_adjusted": mu_a.tolist(), "pairs": pairs}
    if perms:
        su, sa = np.var(mu_u), np.var(mu_a)
        pu, pa = np.empty(perms), np.empty(perms)
        for i in range(perms):
            p = rng.permutation(arm)
            pu[i] = np.var(arm_means(p, y))
            pa[i] = np.var(reloop_means(p, y, x))
        res["omnibus_p_unadjusted"] = float((1 + (pu >= su).sum()) / (1 + perms))
        res["omnibus_p_adjusted"] = float((1 + (pa >= sa).sum()) / (1 + perms))
    return res


def derange(n, rng):
    while True:
        p = rng.permutation(n)
        if not (p == np.arange(n)).any():
            return p


# ----------------------------------------------------------------------------- floor

def floor(rng):
    sizes = [247, 245, 206, 234]
    arm0 = np.repeat(np.arange(4), sizes)
    out = {"design": "arms 247/245/206/234; x~N(0,1); L=r x+sqrt(1-r^2) e; Y=3+Poisson(exp(1+0.55L)); "
                     "T3 +1.0 (T1-T3 = -1.0); 200 sims, 300 boots, 500 perms (null only)",
           "by_r": {}}
    for r in (0.0, 0.35, 0.6):
        est, vr, cov, below, above, r2 = [], [], [], 0, 0, []
        for s in range(200):
            x = rng.standard_normal(len(arm0))
            L = r * x + math.sqrt(1 - r * r) * rng.standard_normal(len(arm0))
            y = 3 + rng.poisson(np.exp(1.0 + 0.55 * L)).astype(float)
            r2.append(np.corrcoef(x, y)[0, 1] ** 2)
            y = y + (arm0 == 2) * 1.0
            res = analyse(arm0, y, x, rng, boots=300, perms=0, pairs_only={"T1-T3"})
            p = res["pairs"]["T1-T3"]
            est.append(p["adjusted"]["diff"])
            vr.append(p["variance_ratio"])
            cov.append(p["adjusted"]["lo90"] <= -1.0 <= p["adjusted"]["hi90"])
            below += p["adjusted"]["hi90"] < 0
            above += p["adjusted"]["lo90"] > 0
        out["by_r"][str(r)] = {"mean_adjusted_T1_T3": float(np.mean(est)), "variance_ratio": float(np.mean(vr)),
                               "one_minus_r2": float(1 - np.mean(r2)), "coverage90": float(np.mean(cov)),
                               "share_below_0": below / 200, "share_above_0": above / 200}
        print(r, out["by_r"][str(r)])
    rej = 0
    for s in range(200):
        x = rng.standard_normal(len(arm0))
        L = 0.35 * x + math.sqrt(1 - 0.35 ** 2) * rng.standard_normal(len(arm0))
        y = 3 + rng.poisson(np.exp(1.0 + 0.55 * L)).astype(float)
        mu = reloop_means(arm0, y, x)
        st = np.var(mu)
        pv = np.array([np.var(reloop_means(rng.permutation(arm0), y, x)) for _ in range(500)])
        rej += int((1 + (pv >= st).sum()) / 501 < 0.05)
    out["null_rejection_rate"] = rej / 200
    b = out["by_r"]
    checks = {
        "F1_bias": all(abs(v["mean_adjusted_T1_T3"] + 1.0) <= 0.05 for v in b.values()),
        "F2_no_harm": b["0.0"]["variance_ratio"] <= 1.05,
        "F3_gain": b["0.6"]["variance_ratio"] <= 0.85 and abs(b["0.6"]["variance_ratio"] - b["0.6"]["one_minus_r2"]) <= 0.07,
        "F4_coverage": all(0.84 <= v["coverage90"] <= 0.96 for v in b.values()),
        "F5_power_sign": b["0.35"]["share_below_0"] >= 0.80 and b["0.35"]["share_above_0"] == 0,
        "F6_null": 0.02 <= out["null_rejection_rate"] <= 0.09,
    }
    out["checks"] = checks = {k: bool(v) for k, v in checks.items()}
    out["floor"] = "PASS" if all(checks.values()) else "FAIL"
    print(checks, out["floor"])
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(out, indent=1) + "\n")


# ----------------------------------------------------------------------------- data

def fnum(v):
    try:
        f = float(v)
        return f if math.isfinite(f) else None
    except (TypeError, ValueError):
        return None


def read_exp(z, name):
    inner = zipfile.ZipFile(io.BytesIO(z.read(name + ".zip")))
    rows = list(csv.DictReader(io.TextIOWrapper(inner.open("exp_alogs.csv"), encoding="utf-8")))
    priors = {r["student_id"]: r for r in csv.DictReader(io.TextIOWrapper(inner.open("priors.csv"), encoding="utf-8"))}
    return inner, rows, priors


def first_rows(rows, keep):
    first = {}
    for r in sorted(rows, key=lambda r: (r["student_id"], r["start_time"] or "~")):
        if keep(r) and r["student_id"] not in first:
            first[r["student_id"]] = r
    return list(first.values())


def raw_features(prior_rows):
    M = np.full((len(prior_rows), len(FEATURES)), np.nan)
    for i, p in enumerate(prior_rows):
        for j, f in enumerate(FEATURES):
            v = fnum((p or {}).get(f))
            if v is not None:
                M[i, j] = math.log1p(max(v, 0.0)) if f in LOG else v
    return M


class Design:
    """Feature standardization fixed on the remnant."""

    def __init__(self, M):
        self.mu = np.nanmean(M, axis=0)
        self.sd = np.nanstd(M, axis=0)
        self.sd[~np.isfinite(self.sd) | (self.sd == 0)] = 1.0

    def __call__(self, M):
        miss = np.isnan(M).astype(float)
        S = np.where(np.isnan(M), 0.0, (M - self.mu) / self.sd)
        return np.column_stack([S, S ** 2, miss])


def ridge(X, y, lam):
    mx, my = X.mean(0), y.mean()
    Xc = X - mx
    beta = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ (y - my))
    return lambda Q: my + (Q - mx) @ beta


def fit_remnant(M, y, groups, rng):
    D = Design(M)
    X = D(M)
    folds = grouped_folds(groups, 5, rng)
    cv = {}
    for lam in (0.1, 1, 10, 100, 1000):
        pred = np.empty(len(y))
        for f in range(5):
            tr = folds != f
            pred[~tr] = ridge(X[tr], y[tr], lam)(X[~tr])
        cv[lam] = float(1 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum())
    best = max(cv, key=cv.get)
    model = ridge(X, y, best)
    return (lambda Mq: model(D(Mq))), best, cv


def build_remnant(z, exclude):
    Mp, yp, gp, Mc, yc, gc = [], [], [], [], [], []
    n_exp_p = n_exp_c = 0
    for name in sorted(n[:-4] for n in z.namelist()):
        if name == EXP:
            continue
        _, rows, priors = read_exp(z, name)
        fr = first_rows(rows, lambda r: bool(r["start_time"]) and r["student_id"] not in exclude)
        if len(fr) >= 50:
            done = np.array([bool((r["end_time"] or "").strip()) for r in fr], float)
            if 0 < done.mean() < 1:
                Mc.append(raw_features([priors.get(r["student_id"]) for r in fr]))
                yc.append(done - done.mean())
                gc += [name] * len(fr)
                n_exp_c += 1
        comp = [r for r in fr if (r["end_time"] or "").strip() and fnum(r["condition_problem_count"]) is not None]
        if len(comp) >= 50:
            v = np.array([fnum(r["condition_problem_count"]) for r in comp])
            if len(set(v.tolist())) >= 5:
                lv = np.log1p(v)
                Mp.append(raw_features([priors.get(r["student_id"]) for r in comp]))
                yp.append((lv - lv.mean()) / lv.std())
                gp += [name] * len(comp)
                n_exp_p += 1
    return ((np.vstack(Mp), np.concatenate(yp), np.array(gp), n_exp_p),
            (np.vstack(Mc), np.concatenate(yc), np.array(gc), n_exp_c))


def icc_oneway(y, g):
    """ANOVA ICC for unbalanced groups (groups of size 1 dropped)."""
    labs, inv, cnt = np.unique(g, return_inverse=True, return_counts=True)
    keep = cnt[inv] >= 2
    y, inv = y[keep], inv[keep]
    labs, inv, cnt = np.unique(inv, return_inverse=True, return_counts=True)
    k, N = len(labs), len(y)
    means = np.bincount(inv, y) / cnt
    ssb = (cnt * (means - y.mean()) ** 2).sum()
    ssw = ((y - means[inv]) ** 2).sum()
    msb, msw = ssb / (k - 1), ssw / (N - k)
    n0 = (N - (cnt ** 2).sum() / N) / (k - 1)
    return float((msb - msw) / (msb + (n0 - 1) * msw)), k, N


def icc_ci(y, g, rng, draws=2000):
    labs = np.unique(g)
    members = {l: np.nonzero(g == l)[0] for l in labs}
    vals = []
    for _ in range(draws):
        pick = rng.choice(labs, len(labs))
        ix = np.concatenate([members[l] for l in pick])
        gg = np.concatenate([np.full(len(members[l]), j) for j, l in enumerate(pick)])
        vals.append(icc_oneway(y[ix], gg)[0])
    return float(np.percentile(vals, 5)), float(np.percentile(vals, 95))


def order_verdict(res):
    matters = res["completion"]["omnibus_p_adjusted"] < 0.05 or res["problems_to_mastery"]["omnibus_p_adjusted"] < 0.05
    inside = all(abs(v["adjusted"]["lo90"]) <= MARGIN[k] and abs(v["adjusted"]["hi90"]) <= MARGIN[k]
                 for k in MARGIN for v in res[k]["pairs"].values())
    return "ORDER MATTERS" if matters else "ORDER INTERCHANGEABLE" if inside else "INCONCLUSIVE"


def main_real(rng):
    z = zipfile.ZipFile(scratch_root() / "osf-59shv/exp.zip")
    inner, rows, priors = read_exp(z, EXP)
    exclude = {r["student_id"] for r in rows}
    units = first_rows(rows, lambda r: r["assigned_condition"] in ARMS)
    arm = np.array([ARMS.index(r["assigned_condition"]) for r in units])
    done = np.array([bool((r["end_time"] or "").strip()) for r in units])
    ptm = np.array([fnum(r["condition_problem_count"]) if d else None for r, d in zip(units, done)], dtype=object)
    Mx = raw_features([priors.get(r["student_id"]) for r in units])

    (Mp, yp, gp, np_exp), (Mc, yc, gc, nc_exp) = build_remnant(z, exclude)
    pred_p, lam_p, cv_p = fit_remnant(Mp, yp, gp, rng)
    pred_c, lam_c, cv_c = fit_remnant(Mc, yc, gc, rng)
    x_p, x_c = pred_p(Mx), pred_c(Mx)
    remnant = {"students_excluded_as_participants": len(exclude),
               "ptm": {"experiments": int(np_exp), "rows": int(len(yp)),
                       "lambda": lam_p, "grouped_cv_r2": cv_p},
               "completion": {"experiments": int(nc_exp), "rows": int(len(yc)), "lambda": lam_c, "grouped_cv_r2": cv_c}}

    res = {"students": int(len(units)), "remnant": remnant}
    sets = {"completion": (np.ones(len(units), bool), done.astype(float), x_c),
            "problems_to_mastery": (np.array([v is not None for v in ptm]), None, x_p)}
    for k, (m, y, x) in sets.items():
        yy = done.astype(float)[m] if k == "completion" else np.array([v for v in ptm[m]], float)
        a, xx = arm[m], x[m]
        # remnant sign check: pooled within-arm correlation
        yc_ = yy - arm_means(a, yy)[a]
        xc_ = xx - np.array([xx[a == j].mean() for j in range(4)])[a]
        r_w = float(np.corrcoef(xc_, yc_)[0, 1])
        out = analyse(a, yy, xx, rng)
        out["within_arm_corr_x_y"] = r_w
        out["sign_check"] = "OK" if r_w > 0 else "REMNANT SIGN WRONG"
        out["pooled_within_arm_sd"] = float(np.sqrt((yc_ ** 2).sum() / (len(yy) - 4)))
        dp = derange(len(yy), rng)
        ctrl = analyse(a, yy, xx[dp], rng, boots=2000, perms=0)
        out["deranged_control"] = {p: {"adjusted_diff": v["adjusted"]["diff"], "variance_ratio": v["variance_ratio"]}
                                   for p, v in ctrl["pairs"].items()}
        out["deranged_control_boots"] = 2000
        res[k] = out
        print(k, "n", out["n"], "p_u", out["omnibus_p_unadjusted"], "p_a", out["omnibus_p_adjusted"], "r_w", round(r_w, 3))
        for p, v in out["pairs"].items():
            print(f"  {p} U {v['unadjusted']['diff']:+.4f} [{v['unadjusted']['lo90']:+.4f},{v['unadjusted']['hi90']:+.4f}]"
                  f" A {v['adjusted']['diff']:+.4f} [{v['adjusted']['lo90']:+.4f},{v['adjusted']['hi90']:+.4f}] VR {v['variance_ratio']:.3f}"
                  f" ctrlVR {out['deranged_control'][p]['variance_ratio']:.3f}")

    h = res["problems_to_mastery"]["pairs"]["T1-T3"]
    ch = res["problems_to_mastery"]["deranged_control"]["T1-T3"]
    control_ok = (0.95 <= ch["variance_ratio"] <= 1.05
                  and h["unadjusted"]["lo90"] <= ch["adjusted_diff"] <= h["unadjusted"]["hi90"])
    vr = h["variance_ratio"]
    floor_path = OUT / "floor.json"
    floor_ok = floor_path.is_file() and json.loads(floor_path.read_text())["floor"] == "PASS"
    v1 = order_verdict(res)
    res["verdicts"] = {
        "floor": "PASS" if floor_ok else "FAIL OR NOT RUN",
        "control": "CONTROL PASSED" if control_ok else "CONTROL FAILED",
        "V1_order": v1,
        "V1_change": "VERDICT UNCHANGED" if v1 == "ORDER MATTERS" else "VERDICT CHANGES",
        "V2_headline": ("T1-T3 CONFIRMED" if h["adjusted"]["hi90"] < 0 else
                        "T1-T3 REVERSED" if h["adjusted"]["lo90"] > 0 else "T1-T3 NOT CONFIRMED"),
        "V3_precision": ("PRECISION GAIN" if vr <= 0.95 else "NO MATERIAL GAIN" if vr <= 1.05 else "PRECISION LOSS"),
    }
    if not floor_ok:
        res["verdicts"] = {k: (v if k == "floor" else "UNANSWERABLE (" + v + ")") for k, v in res["verdicts"].items()}
    for k in ("completion", "problems_to_mastery"):
        ratios = [v["variance_ratio"] for v in res[k]["pairs"].values()]
        res[k]["median_variance_ratio"] = float(np.median(ratios))
        res[k]["median_effective_sample_multiplier"] = float(1 / np.median(ratios))
    res["headline_mde"] = {
        "unadjusted_problems": Z * h["unadjusted"]["se"], "adjusted_problems": Z * h["adjusted"]["se"],
        "unadjusted_sd": Z * h["unadjusted"]["se"] / res["problems_to_mastery"]["pooled_within_arm_sd"],
        "adjusted_sd": Z * h["adjusted"]["se"] / res["problems_to_mastery"]["pooled_within_arm_sd"],
        "T1_T3_in_sd": h["unadjusted"]["diff"] / res["problems_to_mastery"]["pooled_within_arm_sd"]}
    print("verdicts", res["verdicts"])
    OUT.mkdir(exist_ok=True)
    (OUT / "remnant-result.json").write_text(json.dumps(res, indent=1) + "\n")

    # ------------------------------------------------------------- part 2: ICC and power
    cls = np.array([(priors.get(r["student_id"]) or {}).get("class_id", "") for r in units])
    tch = np.array([(priors.get(r["student_id"]) or {}).get("teacher_id", "") for r in units])
    pw = {"alpha": 0.05, "power": 0.80, "Z": Z, "icc": {}}
    for k, (m, _, x) in sets.items():
        yy = done.astype(float)[m] if k == "completion" else np.array([v for v in ptm[m]], float)
        a = arm[m]
        resid = yy - arm_means(a, yy)[a]                      # arm-centred: ICC net of treatment
        for lab, g in (("class", cls[m]), ("teacher", tch[m])):
            ok = g != ""
            rho, kk, nn = icc_oneway(resid[ok], g[ok])
            lo, hi = icc_ci(resid[ok], g[ok], rng)
            pw["icc"][f"{k}_{lab}"] = {"icc": rho, "lo90": lo, "hi90": hi, "groups": kk, "students": nn}
        # residual ICC after the remnant covariate (arm-wise OLS residual)
        rr = np.empty(len(yy))
        for j in range(4):
            mm = a == j
            X = np.column_stack([np.ones(mm.sum()), x[m][mm]])
            rr[mm] = yy[mm] - X @ np.linalg.lstsq(X, yy[mm], rcond=None)[0]
        ok = cls[m] != ""
        pw["icc"][f"{k}_class_after_remnant"] = {"icc": icc_oneway(rr[ok], cls[m][ok])[0]}
    sizes = np.unique(cls[cls != ""], return_counts=True)[1]
    m_med = float(np.median(sizes))
    pw["participant_class_size_median"] = m_med
    pw["participant_classes"] = int(len(sizes))
    # encounter-level learner ICC from problem attempts
    pl = csv.DictReader(io.TextIOWrapper(inner.open("exp_plogs.csv"), encoding="utf-8"))
    armset = {r["student_id"] for r in units}
    sid, cor = [], []
    for r in pl:
        if r["student_id"] in armset and r["problem_condition"] in ARMS and r["correct"] in ("True", "False") and not r["scaffold_id"]:
            sid.append(r["student_id"])
            cor.append(1.0 if r["correct"] == "True" else 0.0)
    sid, cor = np.array(sid), np.array(cor)
    rho_l, kl, nl = icc_oneway(cor, sid)
    lo_l, hi_l = icc_ci(cor, sid, rng, draws=500)
    pw["icc"]["encounter_correct_learner"] = {"icc": rho_l, "lo90": lo_l, "hi90": hi_l, "learners": kl,
                                              "attempts": nl, "draws": 500}
    eta_w = {"none": 1.0, "remnant_ptm": res["problems_to_mastery"]["pairs"]["T1-T3"]["variance_ratio"],
             "remnant_completion": res["completion"]["median_variance_ratio"]}
    rho_cls = pw["icc"]["problems_to_mastery_class"]["icc"]
    table = {}
    for d in (0.05, 0.10, 0.30):
        base = 2 * Z ** 2 / d ** 2
        row = {"per_learner_n_per_arm": {k: math.ceil(base * v) for k, v in eta_w.items()}}
        cl = {}
        for src, rho, eb, ew in (("this_experiment_ptm_rho", rho_cls, 1.0, 1.0),
                                 ("this_experiment_ptm_rho_with_remnant", rho_cls, 1.0, eta_w["remnant_ptm"]),
                                 ("hedges_hedberg_rho_0.15", 0.15, 1.0, 1.0),
                                 ("hedges_hedberg_rho_0.25", 0.25, 1.0, 1.0),
                                 ("hedges_hedberg_rho_0.239_pretest_etaB_0.210_etaW_0.360", 0.239, 0.210, 0.360)):
            rho = max(rho, 0.0)
            cl[src] = {f"m={mm:g}": {"classes_per_arm": math.ceil(base * (rho * eb + (1 - rho) * ew / mm)),
                                     "learners_per_arm": math.ceil(base * (rho * eb + (1 - rho) * ew / mm)) * int(mm)}
                       for mm in (m_med, 20)}
        row["per_class"] = cl
        ne = 4 * Z ** 2 / d ** 2 * (1 - rho_l)
        row["per_encounter"] = {"total_encounters": math.ceil(ne),
                                **{f"learners_K={K}": math.ceil(ne / K) for K in (5, 20)},
                                "with_remnant_total_encounters_if_same_ratio": math.ceil(ne * eta_w["remnant_ptm"])}
        table[str(d)] = row
    pw["sample_sizes"] = table
    arm_power = json.loads((ROOT / "studies/outcomes/lt-trials/out/arm_power.json").read_text())
    pw["lt_trials_comparison"] = {
        "arm_power_n_per_arm_for_abs_0.10": arm_power["n_per_arm_for_0_10"],
        "abs_0.10_in_sd_at_p": {p: 0.10 / math.sqrt((float(p) * (1 - float(p)) + (float(p) - 0.1) * (1.1 - float(p))) / 2)
                                for p in arm_power["n_per_arm_for_0_10"]},
        "note": "arm_power.json's 0.10 is an absolute accuracy difference, i.e. about 0.20-0.25 SD"}
    print(json.dumps(pw, indent=1))
    (OUT / "power.json").write_text(json.dumps(pw, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    args = ap.parse_args()
    rng = np.random.default_rng(SEED)
    floor(rng) if args.floor else main_real(rng)


if __name__ == "__main__":
    main()
