"""
How much does the LT - REV effect vary across classes in the length trial, and can 16 classes say?

Paper II 5.3 reports the trajectory-order effect of the length trial (Sarama et al., ICPSR 151741) as
+0.317 logits [+0.067, +0.566] in the authors' mixed model, +0.301 with class fixed effects, within-class
permutation p 0.032, and a class-cluster bootstrap interval [-0.009, +0.508] read as "not shown to hold
when classes are resampled" (length_order.py). The literature sweep (research/readiness/
learning-graph-budget-2026/literature-sweep-2.md, B.16, Weiss et al. 2017) points out that children
were randomised WITHIN class, so the quantity that governs a class-resampling interval is the variance
of the treatment effect ACROSS classes, not the outcome ICC; the paper should estimate it or say that
16 classes cannot. This study does that.

PRE-REGISTRATION. Written 2026-10-08, before any per-class effect, any variance of the effect across
classes, or any random-slope model of this trial was computed by anyone in this programme. What had
already been seen of the outcomes, all published in out/length_order.json and out/icc.json: the arm
posttest SDs (LT 1.239, REV 0.752, BAU 0.724), the authors' model and class-FE contrasts above, the
within-class permutation p, the class bootstrap interval, the median-regression and rank contrasts,
that the 7 top-5% posttests are all LT (dropping them leaves +0.191), and the arm-centred class ICC
0.395 (pretest slope 0.570). The arm-by-class counts (icc-floor.json) are structure, not outcomes; they
set the floor. Nothing else about the outcomes was looked at before this docstring was committed.

DATA. 151741 'C6 Analysis File.xlsx', read through length_order.load (that sheet holds no race,
language-proficiency or assessor column; only Student ID, Class, Condition, PreTheta_1pl and
Theta_post_1pl are kept). LT and REV children only; BAU is not part of the contrast.
Class structure (icc-floor.json): 16 classes; LT/REV per class 4/2, 6/5, 7/4, 4/8, 4/3, 6/8, 6/4, 7/5,
8/4, 2/3, 4/3, 1/1, 2/2, 4/0, 2/3, 4/4. Class 7 has no REV child.

ESTIMAND. tau = the between-class SD of the class-specific LT - REV effect on posttest theta (logits),
pretest-adjusted, the classes being treated as a sample from the classes the trial stands for.

ESTIMATOR (fixed).
  1. Pooled pretest slope beta and the common effect delta from OLS with class fixed effects,
     y ~ arm + PreTheta + class, on every LT/REV child (length_order.py's model; class 7 enters the
     slope only). Residual r = y - beta * PreTheta.
  2. Per class j with at least one LT and one REV child (15 classes): b_j = mean_LT(r) - mean_REV(r).
  3. Sampling variance v_j = s2_LT / n_LT,j + s2_REV / n_REV,j, where s2_A is arm A's within-class
     residual variance POOLED over all classes (sum of squares about each class-arm mean over its
     degrees of freedom). Few children per arm: a class with one child in an arm (class 5, 1/1) still
     gets a v_j because the variance is pooled, never estimated inside the class; arm-specific pooling
     carries the LT arm's larger spread into every LT mean's variance, so a heavy LT tail widens v_j
     instead of masquerading as between-class spread.
  4. Cochran Q = sum w_j (b_j - b_w)^2, w_j = 1/v_j; tau^2 by DerSimonian-Laird method of moments,
     max(0, (Q - (k-1)) / (sum w - sum w^2 / sum w)), k = 15. tau = sqrt.
  Sensitivities, reported, never verdicts: meta-analytic REML tau on the same b_j, v_j; classes with
  >= 2 children per arm only; a child-level random-slope mixed model (posttest ~ arm + pre,
  (1 + arm | class), statsmodels REML; homoscedastic, so not tail-aware); DL tau after dropping the
  top 5% of LT/REV posttests.

INTERVAL. 95% Q-profile interval for tau^2 (Viechtbauer 2007): the tau^2 values at which the
  generalised Q, sum (b_j - mu(tau^2))^2 / (v_j + tau^2), equals the chi2_{k-1} 0.975 and 0.025
  quantiles (bound 0 when Q at 0 is already below). It RESAMPLES NOTHING: it inverts the Q test against
  its chi-square reference, conditional on the observed v_j. Square roots give the tau interval.
  Its calibration on this structure, tails included, is a floor requirement below.

TEST OF tau > 0 (one-sided). Within-class permutation of the LT/REV labels among each class's LT and
  REV children: the unit and the way the design randomised (BAU children are not touched and not
  used). A plain permutation would test "no effect at all", and a real common effect would then read as
  variation; so the null is the sharp null of a COMMON additive effect delta0: impute
  y0 = y - delta0 * arm, permute arm within class, set y* = y0 + delta0 * arm*, recompute the WHOLE
  estimator (slope, pooled arm variances, v_j, Q) and compare Q* with the observed Q. The statistic is
  Q, studentised by the arm-specific pooled variances recomputed in each permutation.
  delta0 is a nuisance: p_plug is the permutation p at delta0 = delta_FE; the test reported for the
  verdict is Berger-Boos, p = min(1, max over a 9-point grid of delta0 spanning the 99.9% interval
  delta_FE +- 3.29 / sqrt(sum w_j) + 0.001). 2,000 permutations per grid point in the run
  (p = (1 + #{Q* >= Q}) / (1 + perms)); 300 in the floor.
  Note: a heavy tail confined to one arm breaks the sharp null at the CHILD level (it is individual
  effect heterogeneity), so whether the test can tell it from class variation is not assumed. It is
  what the TAIL worlds of the floor check.

DETECTION FLOOR (synthetic only, on 151741's real LT/REV class structure above, before the run).
  y = u_class + 0.57 pre + arm (0.30 + t_class) + e, pre ~ N(0,1), u ~ N(0, 0.5^2),
  t ~ N(0, tau^2). The error SDs are the raw arm posttest SDs (0.752 REV; 0.75 or 1.239 LT), which
  exceed the pretest-adjusted within-class SD; the floor's power is therefore conservative.
    N0, N2, N4   normal e, SD 0.75 both arms, tau 0, 0.2, 0.4
    H0           normal e, LT SD 1.239, REV 0.752, tau 0 (heteroscedastic, no tail)
    M0, M2, M4   MIXTURE TAIL: REV e ~ N(0, 0.752^2); LT e ~ N(0, 0.752^2) plus a jump of 3.29 logits
                 for each LT child with probability 0.10 (independently of class), the bulk LT shift
                 lowered by 0.329 so the mean effect stays 0.30. LT SD = sqrt(0.752^2 + 0.09 * 3.29^2)
                 = 1.24: a common effect carried by a tail of about 1 child in 10, as the real top-7.
                 tau 0, 0.2, 0.4.
    T0           LT e ~ t(3) scaled to SD 1.239, REV normal 0.752, tau 0
  500 replicates per world; 300 permutations per grid point; 1,000 class-bootstrap draws per replicate.
  PASS iff
    validity   the verdict test (Berger-Boos) rejects at 0.05 in <= 0.10 of replicates in EVERY tau-0
               world (N0, H0, M0, T0);
    coverage   the 95% Q-profile interval covers the planted tau in >= 0.85 of replicates in N2, N4,
               M2, M4.
  Reported, not required: p_plug's rejection rate, DL mean and bias, coverage in the tau-0 worlds, the
  median Q-profile upper bound under tau 0 (how large a tau 16 classes can rule out), and the POWER of
  the verdict test at tau 0.2 and 0.4.
  Also reported, for reading the class bootstrap (not required): in every world, the share of
  replicates whose 95% class-cluster bootstrap percentile interval for delta_FE (length_order.py's
  construction: classes resampled whole, LT/REV children) has its lower bound <= 0, and the share whose
  within-class permutation test of delta = 0 (two-sided, 300 perms) gives p < 0.05.
  A failed floor means the run's verdict is CANNOT ESTIMATE (floor) and its tau is printed as
  descriptive only.

VERDICTS (strings fixed; p is the Berger-Boos p; all comparisons signed).
  "CANNOT ESTIMATE (floor): FLOOR FAILED"               the floor failed validity or coverage.
  "EFFECT VARIES ACROSS CLASSES"                         p < 0.05.
  "NO VARIATION DETECTED"                                p >= 0.05 and floor power at M4 (tau 0.4,
                                                         tail) >= 0.80.
  "CANNOT ESTIMATE (floor): 16 CLASSES TOO FEW TO SEE tau 0.4"   p >= 0.05 and that power < 0.80.
  Each is printed with tau (DL), its Q-profile 95% interval, Q, k, p and p_plug.
  Direction: tau is non-negative by construction; delta's sign is printed beside it, with the share of
  the 15 classes whose b_j > 0 and, when tau > 0, Phi(delta / tau), the implied share of classes whose
  true effect is positive.

WHAT IT SAYS ABOUT THE CLASS BOOTSTRAP (fixed reading). The real run also recomputes the class
  bootstrap of delta_FE (2,000 draws, this construction) and prints the inverse-variance SE of the
  common effect at tau = 0, at tau = DL and at tau = the Q-profile upper bound,
  SE(tau) = 1 / sqrt(sum 1 / (v_j + tau^2)), beside the bootstrap SD. Reading rule: the bootstrap
  touching zero is read as "the effect depends on the class" only under EFFECT VARIES ACROSS CLASSES.
  Otherwise it is read against the floor's share of tau-0 worlds (M0, the tail world) in which a true
  common effect of 0.30 produces a bootstrap lower bound <= 0: if that share is >= 0.30 the touch is
  "what this design gives a common effect", and the sentence the paper may use is that 16 classes
  cannot distinguish a common effect from one that varies by the stated upper bound.

CODERS. None. Every construct is the deposit's Rasch theta, its class and arm labels, or arithmetic on
them.

    python3 effect_variation.py --floor   # synthetic, structure only -> out/effect-variation-floor.json
    python3 effect_variation.py --run     # reads outcomes; refuses unless the floor file exists
    python3 effect_variation.py --posthoc # added after the run, see stage_posthoc; changes no verdict
    python3 effect_variation.py --floor-posthoc   # added after the run: power at the run's own noise

Data: $LDA_SCRATCH_DIR/lt-trials/ (registry id clements-sarama-lt; or --dir). AERA/ICPSR open data --
statistical analysis only, no re-identification. Raw files stay in the scratchpad; only aggregates are
written, and per-class effects are written only for classes with >= 2 children in each arm.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.stats import chi2, norm

warnings.filterwarnings("ignore")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))
from shared.paths import scratch_root  # noqa: E402

OUT = HERE / "out"
SEED = 20261008 + 7
EFFECT, SLOPE, U_SD = 0.30, 0.57, 0.5
SD_REV, SD_LT = 0.752, 1.239
JUMP_P, JUMP = 0.10, 3.29
WORLDS = {  # name: (tau, shape)
    "N0": (0.0, "normal"), "N2": (0.2, "normal"), "N4": (0.4, "normal"),
    "H0": (0.0, "hetero"),
    "M0": (0.0, "mixture"), "M2": (0.2, "mixture"), "M4": (0.4, "mixture"),
    "T0": (0.0, "t3"),
}
NULL_WORLDS, COVER_WORLDS = ("N0", "H0", "M0", "T0"), ("N2", "N4", "M2", "M4")
FLOOR = {"null_reject_max": 0.10, "coverage_min": 0.85, "power_world": "M4", "power_min": 0.80,
         "bootstrap_touch_share": 0.30}
GRID = np.linspace(-3.29, 3.29, 9)
P151 = ("ICPSR_151741-V1.1", "AERA Open Depository", "C6 Analysis File.xlsx")


# ------------------------------------------------------------------ structure
class Design:
    """LT/REV children of the trial: class index, arm (1 = LT), and the class one-hot matrix."""

    def __init__(self, cls_labels, arm):
        self.labels, self.g = np.unique(cls_labels, return_inverse=True)
        self.arm = np.asarray(arm, float)
        self.K, self.n = len(self.labels), len(self.arm)
        self.M = np.zeros((self.n, self.K))
        self.M[np.arange(self.n), self.g] = 1.0
        self.cnt = self.M.sum(0)
        self.nL = self.arm @ self.M
        self.nR = self.cnt - self.nL
        self.both = (self.nL > 0) & (self.nR > 0)
        self.blocks = [np.nonzero(self.g == j)[0] for j in range(self.K)]

    def demean(self, X):
        return X - ((X @ self.M) / self.cnt) @ self.M.T

    def permute(self, A0, rng, P):
        A = np.tile(A0, (P, 1))
        for idx in self.blocks:
            if len(idx) > 1:
                A[:, idx] = rng.permuted(A[:, idx], axis=1)
        return A


# ------------------------------------------------------------------ estimator (batched over rows)
def fit(D: Design, Y, A, pre):
    """Rows of Y, A are datasets. Returns delta_FE, beta, b (P x k), v (P x k), Q, tau2_DL."""
    Y, A = np.atleast_2d(Y), np.atleast_2d(A)
    Ad, Yd, pd_ = D.demean(A), D.demean(Y), D.demean(pre[None, :])[0]
    Saa, Sap, Spp = (Ad ** 2).sum(1), (Ad * pd_).sum(1), (pd_ ** 2).sum()
    Say, Spy = (Ad * Yd).sum(1), (Yd * pd_).sum(1)
    det = Saa * Spp - Sap ** 2
    delta = (Spp * Say - Sap * Spy) / det
    beta = (Saa * Spy - Sap * Say) / det
    R = Y - beta[:, None] * pre[None, :]
    B = 1.0 - A
    nL, nR = A @ D.M, B @ D.M
    sL, sR = (A * R) @ D.M, (B * R) @ D.M
    qL, qR = (A * R * R) @ D.M, (B * R * R) @ D.M
    with np.errstate(invalid="ignore", divide="ignore"):
        ssL = np.where(nL > 0, qL - sL ** 2 / nL, 0.0)
        ssR = np.where(nR > 0, qR - sR ** 2 / nR, 0.0)
        s2L = ssL.sum(1) / (nL.sum(1) - (nL > 0).sum(1))
        s2R = ssR.sum(1) / (nR.sum(1) - (nR > 0).sum(1))
        m = D.both
        b = sL[:, m] / nL[:, m] - sR[:, m] / nR[:, m]
        v = s2L[:, None] / nL[:, m] + s2R[:, None] / nR[:, m]
    w = 1.0 / v
    bw = (w * b).sum(1) / w.sum(1)
    Q = (w * (b - bw[:, None]) ** 2).sum(1)
    k = b.shape[1]
    c = w.sum(1) - (w ** 2).sum(1) / w.sum(1)
    tau2 = np.maximum(0.0, (Q - (k - 1)) / c)
    return {"delta": delta, "beta": beta, "b": b, "v": v, "Q": Q, "tau2": tau2, "k": k,
            "se0": 1.0 / np.sqrt(w.sum(1)), "s2L": s2L, "s2R": s2R}


def qprofile(b, v, level=0.95):
    """Q-profile interval for tau^2 (Viechtbauer 2007)."""
    k = len(b)

    def gq(t2):
        w = 1.0 / (v + t2)
        mu = (w * b).sum() / w.sum()
        return (w * (b - mu) ** 2).sum()

    lo_crit, hi_crit = chi2.ppf(1 - (1 - level) / 2, k - 1), chi2.ppf((1 - level) / 2, k - 1)
    top = 100.0
    q0 = gq(0.0)
    lo = 0.0 if q0 <= lo_crit else brentq(lambda t: gq(t) - lo_crit, 0.0, top)
    hi = 0.0 if q0 <= hi_crit else (top if gq(top) > hi_crit else brentq(lambda t: gq(t) - hi_crit, 0.0, top))
    return lo, hi


def reml_tau2(b, v):
    def nll(t2):
        w = 1.0 / (v + t2)
        mu = (w * b).sum() / w.sum()
        return 0.5 * (np.log(v + t2).sum() + np.log(w.sum()) + (w * (b - mu) ** 2).sum())
    return float(minimize_scalar(nll, bounds=(0.0, 10.0), method="bounded").x)


def tau_test(D: Design, y, a, pre, rng, perms, grid=GRID):
    """Permutation p for Q under the sharp common-effect null; plug-in and Berger-Boos."""
    obs = fit(D, y, a, pre)
    Qo, d_hat, se = obs["Q"][0], obs["delta"][0], obs["se0"][0]
    ps = []
    for z in grid:
        d0 = d_hat + z * se
        A = D.permute(a, rng, perms)
        Y = (y - d0 * a)[None, :] + d0 * A
        Qs = fit(D, Y, A, pre)["Q"]
        ps.append((1 + (Qs >= Qo - 1e-12).sum()) / (1 + perms))
    p_plug = ps[len(grid) // 2]
    return obs, float(p_plug), float(min(1.0, max(ps) + 0.001)), [float(p) for p in ps]


def class_suffstats(D: Design, y, a, pre):
    """Within-class centred cross products per class (for the class-cluster bootstrap of delta_FE)."""
    out = np.zeros((D.K, 5))
    for j, idx in enumerate(D.blocks):
        aa, pp, yy = a[idx] - a[idx].mean(), pre[idx] - pre[idx].mean(), y[idx] - y[idx].mean()
        out[j] = [(aa * aa).sum(), (aa * pp).sum(), (pp * pp).sum(), (aa * yy).sum(), (pp * yy).sum()]
    return out


def class_bootstrap(D: Design, y, a, pre, rng, draws):
    S = class_suffstats(D, y, a, pre)
    pick = rng.integers(0, D.K, (draws, D.K))
    T = S[pick].sum(1)
    Saa, Sap, Spp, Say, Spy = T.T
    det = Saa * Spp - Sap ** 2
    ok = Saa > 0
    return ((Spp * Say - Sap * Spy) / det)[ok]


def zero_effect_perm_p(D: Design, y, a, pre, rng, perms):
    est = fit(D, y, a, pre)["delta"][0]
    A = D.permute(a, rng, perms)
    null = fit(D, np.tile(y, (perms, 1)), A, pre)["delta"]
    return float((1 + (np.abs(null) >= abs(est)).sum()) / (1 + perms))


# ------------------------------------------------------------------ floor
def simulate(D: Design, tau, shape, rng, sd_rev=SD_REV, sd_lt=SD_LT, jump=JUMP):
    a = D.arm
    pre = rng.normal(size=D.n)
    u = rng.normal(0, U_SD, D.K)[D.g]
    t = rng.normal(0, tau, D.K)[D.g] if tau > 0 else 0.0
    eff = EFFECT + t
    if shape == "normal":
        e = rng.normal(0, sd_rev, D.n)
    elif shape == "hetero":
        e = np.where(a == 1, rng.normal(0, sd_lt, D.n), rng.normal(0, sd_rev, D.n))
    elif shape == "mixture":
        jump = (rng.random(D.n) < JUMP_P) * jump - JUMP_P * jump
        e = rng.normal(0, sd_rev, D.n) + a * jump
    elif shape == "t3":
        tt = rng.standard_t(3, D.n) / np.sqrt(3.0)
        e = np.where(a == 1, sd_lt * tt, rng.normal(0, sd_rev, D.n))
    else:
        raise ValueError(shape)
    return u + SLOPE * pre + a * eff + e, pre


def run_floor(D: Design, rng, reps=500, perms=300, draws=1000, worlds=WORLDS, **sim):
    res = {}
    for name, (tau, shape) in worlds.items():
        rec = {k: [] for k in ("tau", "p_bb", "p_plug", "cover", "hi", "boot_lo_le0", "boot_cover",
                               "perm0_p_lt05", "delta")}
        for _ in range(reps):
            y, pre = simulate(D, tau, shape, rng, **sim)
            obs, p_plug, p_bb, _ = tau_test(D, y, D.arm, pre, rng, perms)
            lo, hi = qprofile(obs["b"][0], obs["v"][0])
            bs = class_bootstrap(D, y, D.arm, pre, rng, draws)
            blo, bhi = np.percentile(bs, [2.5, 97.5])
            rec["tau"].append(float(np.sqrt(obs["tau2"][0])))
            rec["p_bb"].append(p_bb)
            rec["p_plug"].append(p_plug)
            rec["cover"].append(lo <= tau ** 2 <= hi)
            rec["hi"].append(float(np.sqrt(hi)))
            rec["boot_lo_le0"].append(blo <= 0)
            rec["boot_cover"].append(blo <= EFFECT <= bhi)
            rec["perm0_p_lt05"].append(zero_effect_perm_p(D, y, D.arm, pre, rng, perms) < 0.05)
            rec["delta"].append(float(obs["delta"][0]))
        r = {k: np.array(v, float) for k, v in rec.items()}
        res[name] = {
            "planted_tau": tau, "shape": shape, "reps": reps,
            "reject_bb_05": float((r["p_bb"] < 0.05).mean()),
            "reject_plug_05": float((r["p_plug"] < 0.05).mean()),
            "qprofile_coverage": float(r["cover"].mean()),
            "tau_dl_mean": float(r["tau"].mean()), "tau_dl_bias": float(r["tau"].mean() - tau),
            "tau_dl_share_zero": float((r["tau"] == 0).mean()),
            "qprofile_hi_median": float(np.median(r["hi"])),
            "delta_mean": float(r["delta"].mean()),
            "class_bootstrap_lo_le_0_share": float(r["boot_lo_le0"].mean()),
            "class_bootstrap_coverage_of_0.30": float(r["boot_cover"].mean()),
            "within_class_perm_delta0_reject_share": float(r["perm0_p_lt05"].mean()),
        }
        w = res[name]
        print(f"  {name} tau {tau:.1f} {shape:8s} reject BB {w['reject_bb_05']:.3f} plug "
              f"{w['reject_plug_05']:.3f} | cover {w['qprofile_coverage']:.3f} | DL mean "
              f"{w['tau_dl_mean']:.3f} (zero {w['tau_dl_share_zero']:.2f}) | QP hi med "
              f"{w['qprofile_hi_median']:.3f} | boot lo<=0 {w['class_bootstrap_lo_le_0_share']:.3f} "
              f"| perm delta p<.05 {w['within_class_perm_delta0_reject_share']:.3f}", flush=True)
    if worlds is not WORLDS:
        return {"worlds": res}
    fails = [f"{n} null reject {res[n]['reject_bb_05']:.3f}" for n in NULL_WORLDS
             if res[n]["reject_bb_05"] > FLOOR["null_reject_max"]]
    fails += [f"{n} coverage {res[n]['qprofile_coverage']:.3f}" for n in COVER_WORLDS
              if res[n]["qprofile_coverage"] < FLOOR["coverage_min"]]
    return {"worlds": res, "fails": fails, "pass": not fails,
            "power_tau_0.4_tail": res["M4"]["reject_bb_05"], "power_tau_0.2_tail": res["M2"]["reject_bb_05"],
            "power_tau_0.4_normal": res["N4"]["reject_bb_05"], "power_tau_0.2_normal": res["N2"]["reject_bb_05"]}


# ------------------------------------------------------------------ stages
def data_dir(a) -> Path:
    return Path(a.dir) if a.dir else scratch_root() / "lt-trials"


def structure(a) -> Design:
    from icc import structure_151741  # SID / Class / Condition only
    rows = [r for r in structure_151741(data_dir(a)) if str(r["arm"]).strip() in ("LT", "REV")]
    return Design([str(r["cls"]) for r in rows], [str(r["arm"]).strip() == "LT" for r in rows])


def stage_floor(a):
    D = structure(a)
    print(f"LT/REV structure: {D.n} children, {D.K} classes, {int(D.both.sum())} with both arms; "
          f"LT {D.nL.astype(int).tolist()} REV {D.nR.astype(int).tolist()}")
    fl = run_floor(D, np.random.default_rng(SEED), reps=a.reps)
    out = {"date": "2026-10-08", "floor_rule": FLOOR, "effect": EFFECT, "slope": SLOPE, "u_sd": U_SD,
           "sd_rev": SD_REV, "sd_lt": SD_LT, "jump_p": JUMP_P, "jump": JUMP,
           "structure": {"classes": D.labels.tolist(), "n_lt": D.nL.astype(int).tolist(),
                         "n_rev": D.nR.astype(int).tolist(), "classes_with_both_arms": int(D.both.sum())},
           "perms_per_grid_point": 300, "boot_draws": 1000, **fl}
    print(f"\nFLOOR {'PASS' if fl['pass'] else 'FAIL'} {fl['fails']}; power at tau 0.4 (tail) "
          f"{fl['power_tau_0.4_tail']:.3f}")
    OUT.mkdir(exist_ok=True)
    (OUT / "effect-variation-floor.json").write_text(json.dumps(out, indent=1) + "\n")


def load_real(a):
    from length_order import load
    d = load(data_dir(a).joinpath(*P151))
    d = d[["Student ID Number", "Class", "Condition", "PreTheta_1pl", "Theta_post_1pl"]].copy()
    d["Condition"] = d["Condition"].astype(str).str.strip()
    d = d[d.Condition.isin(["LT", "REV"])].dropna(subset=["PreTheta_1pl", "Theta_post_1pl"])
    return d


def summarise(D, y, a, pre, rng, perms):
    obs, p_plug, p_bb, ps = tau_test(D, y, a, pre, rng, perms)
    b, v = obs["b"][0], obs["v"][0]
    lo, hi = qprofile(b, v)
    return obs, {"k": int(obs["k"]), "delta_fe": float(obs["delta"][0]), "beta": float(obs["beta"][0]),
                 "Q": float(obs["Q"][0]), "tau_dl": float(np.sqrt(obs["tau2"][0])),
                 "tau_qprofile_95": [float(np.sqrt(lo)), float(np.sqrt(hi))],
                 "tau_reml": float(np.sqrt(reml_tau2(b, v))),
                 "p_plug": p_plug, "p_berger_boos": p_bb, "p_grid": ps,
                 "s2_lt": float(obs["s2L"][0]), "s2_rev": float(obs["s2R"][0])}


def stage_run(a):
    if not (OUT / "effect-variation-floor.json").exists():
        sys.exit("run --floor first")
    fl = json.loads((OUT / "effect-variation-floor.json").read_text())
    d = load_real(a)
    D = Design(d.Class.astype(str).values, (d.Condition == "LT").values)
    y, pre, arm = d.Theta_post_1pl.values.astype(float), d.PreTheta_1pl.values.astype(float), D.arm
    rng = np.random.default_rng(SEED + 1)
    print(f"{D.n} LT/REV children, {D.K} classes, {int(D.both.sum())} with both arms")
    obs, main_ = summarise(D, y, arm, pre, rng, a.perms)
    b, v = obs["b"][0], obs["v"][0]
    lo, hi = main_["tau_qprofile_95"]
    delta, tau = main_["delta_fe"], main_["tau_dl"]

    def se_at(t):
        return float(1.0 / np.sqrt((1.0 / (v + t ** 2)).sum()))
    bs = class_bootstrap(D, y, arm, pre, rng, 2000)
    boot = {"draws": int(len(bs)), "percentile_95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
            "sd": float(bs.std(ddof=1)), "se_tau0": se_at(0.0), "se_tau_dl": se_at(tau),
            "se_tau_qprofile_hi": se_at(hi)}

    # sensitivities
    sens = {}
    keep2 = (D.nL >= 2) & (D.nR >= 2)
    m2 = keep2[D.both]
    sens["classes_ge2_per_arm"] = {"k": int(m2.sum()), "tau_dl": None, "tau_qprofile_95": None}
    bb, vv = b[m2], v[m2]
    w = 1 / vv
    Qk = float((w * (bb - (w * bb).sum() / w.sum()) ** 2).sum())
    c = w.sum() - (w ** 2).sum() / w.sum()
    l2, h2 = qprofile(bb, vv)
    sens["classes_ge2_per_arm"].update({"Q": Qk, "tau_dl": float(np.sqrt(max(0.0, (Qk - (len(bb) - 1)) / c))),
                                        "tau_qprofile_95": [float(np.sqrt(l2)), float(np.sqrt(h2))]})
    top = np.quantile(y, 0.95)
    keep = y < top
    Dt = Design(D.labels[D.g][keep], arm[keep])
    ot = fit(Dt, y[keep], arm[keep], pre[keep])
    sens["drop_top_5pct"] = {"n_dropped": int((~keep).sum()), "n_dropped_lt": int(arm[~keep].sum()),
                             "delta_fe": float(ot["delta"][0]), "tau_dl": float(np.sqrt(ot["tau2"][0])),
                             "tau_qprofile_95": [float(np.sqrt(x)) for x in qprofile(ot["b"][0], ot["v"][0])]}
    try:
        import statsmodels.formula.api as smf
        dd = d.assign(arm=arm, cls=d.Class.astype(str))
        mm = smf.mixedlm("Theta_post_1pl ~ arm + PreTheta_1pl", dd, groups="cls", re_formula="~arm").fit(reml=True)
        sens["random_slope_mixed_model"] = {"arm": float(mm.params["arm"]),
                                            "slope_sd": float(np.sqrt(max(0.0, mm.cov_re.loc["arm", "arm"]))),
                                            "converged": bool(mm.converged)}
    except Exception as ex:  # reported, not a verdict
        sens["random_slope_mixed_model"] = {"error": str(ex)}

    # verdict
    p = main_["p_berger_boos"]
    power = fl["power_tau_0.4_tail"]
    if not fl["pass"]:
        verdict = "CANNOT ESTIMATE (floor): FLOOR FAILED"
    elif p < 0.05:
        verdict = "EFFECT VARIES ACROSS CLASSES"
    elif power >= FLOOR["power_min"]:
        verdict = "NO VARIATION DETECTED"
    else:
        verdict = "CANNOT ESTIMATE (floor): 16 CLASSES TOO FEW TO SEE tau 0.4"
    touch = fl["worlds"]["M0"]["class_bootstrap_lo_le_0_share"]
    if verdict == "EFFECT VARIES ACROSS CLASSES":
        reading = "class bootstrap touching zero is read as the effect depending on the class"
    elif touch >= FLOOR["bootstrap_touch_share"]:
        reading = (f"WHAT THIS DESIGN GIVES A COMMON EFFECT: in the tail world with tau 0 and a true common "
                   f"0.30, the class bootstrap lower bound is <= 0 in {touch:.2f} of replicates; 16 classes "
                   f"cannot distinguish a common effect from one varying by up to tau {hi:.2f}")
    else:
        reading = (f"bootstrap touch not typical of a common effect here (share {touch:.2f} < 0.30); "
                   f"not attributable to class variation either (verdict {verdict})")
    per_class = [{"class": str(D.labels[j]), "n_lt": int(D.nL[j]), "n_rev": int(D.nR[j]),
                  "b": float(bj), "se": float(np.sqrt(vj))}
                 for j, bj, vj in zip(np.nonzero(D.both)[0], b, v) if D.nL[j] >= 2 and D.nR[j] >= 2]
    out = {"date": "2026-10-08", "n_children_lt_rev": int(D.n), "classes": int(D.K),
           "classes_with_both_arms": int(D.both.sum()), "perms_per_grid_point": a.perms, **main_,
           "direction": {"delta_sign": "+" if delta > 0 else "-", "share_classes_b_positive": float((b > 0).mean()),
                         "phi_delta_over_tau": float(norm.cdf(delta / tau)) if tau > 0 else None},
           "class_bootstrap": boot, "sensitivity": sens,
           "per_class_ge2_each_arm": per_class,
           "floor": {"pass": fl["pass"], "fails": fl["fails"], "power_tau_0.4_tail": power,
                     "power_tau_0.2_tail": fl["power_tau_0.2_tail"],
                     "M0_class_bootstrap_lo_le_0_share": touch},
           "verdict": verdict, "class_bootstrap_reading": reading}
    print(json.dumps({k: out[k] for k in ("k", "delta_fe", "beta", "Q", "tau_dl", "tau_qprofile_95", "tau_reml",
                                          "p_plug", "p_berger_boos", "direction", "class_bootstrap",
                                          "sensitivity")}, indent=1))
    print(f"\nVERDICT: {verdict}\nREADING: {reading}")
    (OUT / "effect-variation.json").write_text(json.dumps(out, indent=1) + "\n")


def stage_posthoc(a):
    """POST HOC (added after --run, changes no verdict): the observed Q (24.1 on 14 df) sits near the
    chi-square 0.05 cut-off while the permutation p is 0.29. Prints the chi-square reference p and the
    plug-in permutation null's quantiles so the gap is visible, and how much of Q each class carries."""
    d = load_real(a)
    D = Design(d.Class.astype(str).values, (d.Condition == "LT").values)
    y, pre, arm = d.Theta_post_1pl.values.astype(float), d.PreTheta_1pl.values.astype(float), D.arm
    obs = fit(D, y, arm, pre)
    rng = np.random.default_rng(SEED + 2)
    d0 = obs["delta"][0]
    A = D.permute(arm, rng, a.perms)
    Qs = fit(D, (y - d0 * arm)[None, :] + d0 * A, A, pre)["Q"]
    b, v = obs["b"][0], obs["v"][0]
    w = 1 / v
    contrib = w * (b - (w * b).sum() / w.sum()) ** 2
    out = {"post_hoc": True, "Q": float(obs["Q"][0]), "df": int(obs["k"] - 1),
           "chi2_reference_p": float(chi2.sf(obs["Q"][0], obs["k"] - 1)),
           "perm_null_Q_quantiles": {q: float(np.quantile(Qs, float(q))) for q in ("0.5", "0.9", "0.95")},
           "perm_null_Q_mean": float(Qs.mean()), "perms": a.perms,
           "largest_class_shares_of_Q": sorted((float(x) for x in contrib / contrib.sum()), reverse=True)[:3]}
    print(json.dumps(out, indent=1))
    (OUT / "effect-variation-posthoc.json").write_text(json.dumps(out, indent=1) + "\n")


def stage_floor_posthoc(a):
    """POST HOC (added after --run, changes no verdict): the registered floor used the RAW arm posttest
    SDs (0.752 / 1.239); the run's pooled within-class residual SDs after the pretest are smaller
    (out/effect-variation.json s2_rev, s2_lt). Re-runs the power worlds at the run's own noise, the mixture
    jump rescaled so LT's extra variance matches (0.09 jump^2 = sd_lt^2 - sd_rev^2), to say what 16 classes
    can see at the noise this trial actually has."""
    r = json.loads((OUT / "effect-variation.json").read_text())
    sd_rev, sd_lt = float(np.sqrt(r["s2_rev"])), float(np.sqrt(r["s2_lt"]))
    jump = float(np.sqrt((sd_lt ** 2 - sd_rev ** 2) / (JUMP_P * (1 - JUMP_P))))
    worlds = {"M0": (0.0, "mixture"), "M2": (0.2, "mixture"), "M4": (0.4, "mixture"), "M6": (0.6, "mixture"),
              "N4": (0.4, "normal")}
    fl = run_floor(structure(a), np.random.default_rng(SEED + 3), reps=a.reps, worlds=worlds,
                   sd_rev=sd_rev, sd_lt=sd_lt, jump=jump)
    (OUT / "effect-variation-floor-posthoc.json").write_text(json.dumps(
        {"post_hoc": True, "why": "registered floor used raw arm SDs; this uses the run's residual SDs",
         "sd_rev": sd_rev, "sd_lt": sd_lt, "jump": jump, "perms_per_grid_point": 300, "boot_draws": 1000,
         **fl}, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--posthoc", action="store_true")
    ap.add_argument("--floor-posthoc", action="store_true")
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--perms", type=int, default=2000)
    ap.add_argument("--dir", help="folder holding the unpacked ICPSR deposits (default $LDA_SCRATCH_DIR/lt-trials)")
    a = ap.parse_args()
    if a.floor:
        stage_floor(a)
    elif a.run:
        stage_run(a)
    elif a.posthoc:
        stage_posthoc(a)
    elif a.floor_posthoc:
        stage_floor_posthoc(a)
    else:
        ap.error("--floor or --run")


if __name__ == "__main__":
    main()
