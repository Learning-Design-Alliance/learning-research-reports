"""PRE-REGISTERED: do the graph-state and state-timescales (S2 Part A) headlines move when the coupled
filter's Laplace update step is replaced by moment matching?

Why. S3 (studies/measurement/grey-box/, its CHANGE 3) found that the update step of gstate.run_gauss --
one Laplace / extended-Kalman step at the predictive point: score and Fisher information of the plain
4PL at m -- with the TRUE parameters of a synthetic world (W3) preferred a spurious general learning term
(+21.5 TRAIN nats) and fell 46 nats behind an exact filter. Assumed-density filtering (moment matching:
score and observed information of the probit-integrated likelihood in the predictive mean, and a
pseudo-measurement of precision J / (1 - v J)) removed the term and came within 2.9 nats. Graph-state's
C2 family and S2's Part A (its C2, C2g and the g-tracker g_hat behind A1) run on the Laplace step, and
their numbers feed the engine recommendation to the product (implement A1 first). This is a re-check,
not a rewrite: the original studies' code and out/ are not edited. Written 2026-10-02, before any run of
this design on real data.

THE ONE CHANGE. Every call of the coupled filter uses fstep.step(adf=True) (grey-box's gbox.run_grey adf
branch at nu = 1, no extra components) instead of the Laplace step. It is installed by replacing
gstate.run_gauss and tstate.run_joint with fstep's copies, whose adf=False path is the original exactly
(checked, below). Everything else is the original code imported unchanged and called in the original
order: loaders, learner subsamples (graph-state: XES3G5M 1 in 2, ASSISTments 1 in 3, Eedi 1 in 6; S2:
1 in 3, 1 in 4, 1 in 12), e2e.py's TRAIN/TEST split, graph-state's rank-selection split, items,
skills, C0 (E5-decay), Stage 1 (static items, cells -- its linearisation at theta_l is a calibration,
not the filter's update, and is not changed), the EM priors, the derangement seeds, S2's fixed ranks
(8 / 2 / 8), the bootstrap seeds and B = 200, the metrics and the verdict functions. What follows
from the filter follows by the same code: graph-state's rank is re-selected by its own rule (the
filter's validation cold-attempt loss); a, b and the practice slope are refitted on the moment-matching
filter's own state (two passes, as registered there; grey-box CHANGE 3 did the same); S2's g_hat, the
A1 maps mu_k, lambda_k and n0 are refitted from the moment-matching g-tracker. Not changed: C0, C1,
PFA-lite, CLIM and the engine's Beta (they do not use the filter). The original synthetic floors are not
re-run; their records (graph-state floor PASSES with world-H retention 0.33; S2 Part A floor PASSES)
are read, as the originals read them, for the verdict flags.

DATA (raw data never enters the repo; out/ holds aggregates only). Through the original loaders and the
repo's data registry (shared.paths.data_path), no downloads: XES3G5M (XES_DIR), Eedi NeurIPS 2020
(EEDI_ANSWERS, EEDI_ZIP), ASSISTments 2012-13 (ASSIST_DIR, streamed from its zip). Synthetic: grey-box's
world W3 (grey_box.world), simulated in memory.

HEADLINES RE-COMPUTED (original value [95% learner-bootstrap percentile interval]; source file).
  Graph-state, studies/measurement/graph-state/out/{xes,assist,eedi}.json (real runs at 66a17bd), in
  the order XES3G5M / ASSISTments / Eedi:
    GS1 C2's cold-attempt (M1) gain over C0, nats per attempt (M1_gain_vs_C0.C2):
        +0.0457 [+0.0424, +0.0486] / +0.0473 [+0.0423, +0.0533] / +0.0672 [+0.0634, +0.0711]
    GS2 the general factor's share of it, C2g's M1 gain / C2's (point only in the original; README
        "95-99%"): 0.947 / 0.995 / 0.991. C2g's M1 gain: +0.0433 [+0.0398, +0.0460] /
        +0.0470 [+0.0422, +0.0534] / +0.0666 [+0.0632, +0.0704]
    GS3 C2 over C2-diag on M1 (the coupling attribution, C2_over_C2diag_M1):
        +0.0456 [+0.0420, +0.0487] / +0.0322 [+0.0273, +0.0378] / +0.0656 [+0.0617, +0.0698]
    GS4 C2 over C2-shuf on M1: +0.0075 [+0.0069, +0.0083] / +0.0016 [+0.0004, +0.0026] /
        +0.0052 [+0.0044, +0.0059]
    GS5 C3 retention (graph_retention): 0.141 [0.132, 0.151] / n.a. / 0.348 [0.328, 0.365];
        C3g over C2g on M1: +0.0010 [+0.0008, +0.0013] / n.a. / +0.0020 [+0.0014, +0.0025]
    GS6 C2's M2 gain over C0 (every attempt): +0.0358 [+0.0332, +0.0377] / +0.0198 [+0.0185, +0.0211] /
        +0.0373 [+0.0357, +0.0392]
    GS7 C2's predictive-interval coverage 50 / 80 / 95% and label (M4_calibration.C2): cold
        0.50 / 0.79 / 0.94, 0.51 / 0.80 / 0.95, 0.50 / 0.79 / 0.95, all CALIBRATED INTERVALS; warm
        0.49 / 0.78 / 0.94, 0.48 / 0.78 / 0.94, 0.49 / 0.79 / 0.94, all CALIBRATED INTERVALS. C3's labels
        (CALIBRATED, cold and warm, XES3G5M and Eedi) are checked the same way.
    GS8 C2's items saved per 1,000 attempts at 20% risk: +74.3 [+69.3, +78.1] / +25.5 [+22.1, +29.2] /
        +53.2 [+50.4, +55.8]
    GS9 verdict strings: coupling COUPLING HELPS COLD NODES (all three); graph EMPIRICAL COVARIANCE ONLY
        / NOT TESTABLE (no hierarchy) / EMPIRICAL COVARIANCE ONLY; which skills WHICH SKILLS CO-VARY
        MATTERS (all three); guard C2 IMPROVES NEXT-ATTEMPT (all three). Chosen rank 8 / 2 / 8 (reported).
  S2 Part A, studies/measurement/state-timescales/out/{assist,xes,eedi}.json key "A", in the order
  ASSISTments / XES3G5M / Eedi:
    A1  A1's share of C2's cold gain (share_of_C2_cold.A1):
        1.007 [0.961, 1.054] / 0.912 [0.885, 0.938] / 0.942 [0.922, 0.962]   (README 1.01 / 0.91 / 0.94)
    A2  C2's cold gain over C0: +0.0473 [+0.0419, +0.0527] / +0.0443 [+0.0395, +0.0495] /
        +0.0682 [+0.0631, +0.0735]; A1's: +0.0476 [+0.0424, +0.0533] / +0.0404 [+0.0360, +0.0457] /
        +0.0642 [+0.0590, +0.0691]
    A3  C2g's share of C2's cold gain: 0.995 [0.977, 1.008] / 0.968 [0.949, 0.989] / 0.993 [0.981, 1.010]
    A4  A1-global's share: 0.582 [0.519, 0.639] / 0.838 [0.814, 0.865] / 0.862 [0.835, 0.885]
    A5  A2-orth over A1, every attempt (A2_orth_over_A1_all): +0.0012 [+0.0009, +0.0015] /
        +0.0019 [+0.0017, +0.0022] / +0.0048 [+0.0041, +0.0055]; shares of C2's every-attempt gain:
        A1 0.650 [0.618, 0.683] / 0.767 [0.745, 0.786] / 0.739 [0.713, 0.761]; A2-orth 0.712 [0.678,
        0.743] / 0.822 [0.801, 0.842] / 0.869 [0.852, 0.886]
    A6  interval labels, cold windows: C0 UNDER-CONFIDENT x3; A1 UNDER-CONFIDENT x3 (coverage
        0.60 / 0.87 / 0.97, 0.56 / 0.84 / 0.96, 0.57 / 0.85 / 0.96); A2-orth UNDER-CONFIDENT /
        UNDER-CONFIDENT / CALIBRATED; C2g and C2 CALIBRATED x3; warm windows CALIBRATED for every variant.
    A7  items saved per 1,000 at 20% risk, A1 / A2-orth / C2: +17.1 / +18.6 / +25.5, +58.0 / +62.4 /
        +75.3, +43.3 / +48.7 / +54.0 (intervals from the source file)
    A8  verdict strings: A1 PRIOR-ONLY CAPTURES MOST x3; A1-global PRIOR-ONLY CAPTURES MOST x3; A1 DOES
        NOT WORSEN NEXT-ATTEMPT x3; GENERAL STATE ADDS TO WARM PREDICTIONS x3; double counting NAIVE BLEND
        DOUBLE-COUNTS / NO DOUBLE COUNTING DETECTED / NO DOUBLE COUNTING DETECTED; LEARNER-SPECIFIC, NOT
        VOLUME x3.
  Not re-computed: S2 Part B (its own decoupled step with components; not in the recommendation's
  A1 line), state-structure (S1; NO GO and UNCALIBRATED, not part of the recommendation), grey-box (S3;
  already moment matching).

MATERIALITY (stated before any run). For each headline and corpus:
  (a) a number with an original 95% interval MOVES if |recomputed - original| exceeds the original
      interval's half-width (hi - lo) / 2;
  (b) a number reported without an interval (GS2's shares) MOVES if |recomputed - original| exceeds the
      recomputed interval's half-width (graph-state's ratio_ci, the same bootstrap);
  (c) a coverage (no interval in either run) MOVES if any level changes by more than 0.02;
  (d) a verdict or label string MOVES if it differs at all.
  A headline row is MOVED if any of its numbers moves on any corpus, HOLDS otherwise. Every change is
  reported signed, recomputed minus original. No direction of change is predicted.

ENGINE BOTTOM LINE (rules stated in advance).
  - "Implement A1 first" stands if A1 reads PRIOR-ONLY CAPTURES MOST on all three corpora, without
    BUT OVER-CONFIDENT, and A1 DOES NOT WORSEN NEXT-ATTEMPT on all three.
  - "A1 captures 0.91-1.01 of the coupled state's cold-skill gain" stands if A1 (row A1) HOLDS on all
    three; otherwise the recomputed range replaces it.
  - "One general factor gives 95-99% of the gain" stands if GS2 HOLDS on all three; otherwise the
    recomputed range replaces it. A3 is S2's version of the same claim and is read beside it.
  - "The coupled state's intervals are calibrated; the engine's are too wide at first encounters"
    stands if GS7 and A6 HOLD.

REPRODUCTION CONTROLS (before any moment-matching number is read).
  R1 Filter-free quantities equal the original record: C0's cold and every-attempt log loss to 1e-9 and
     every subset count exactly (graph-state; S2: A|cold|C0 and A|all|C0 log loss, counts).
  R2 Graph-state: the ORIGINAL gstate.run_gauss (Laplace) is run beside moment matching in each of the
     eight rank-selection calls; its validation cold-attempt log loss equals the original
     fit.rank_cold_logloss to 1e-6 at every rank. This checks Stage 1, cells, EM and the Laplace filter
     path on real data. In the first of those calls fstep.run_gauss(adf=False) equals gstate.run_gauss
     to 1e-9.
  R3 S2's own assertion run_joint == run_gauss (1e-9) runs on TEST with both replaced, so the two
     moment-matching copies agree on real data.
  If R1 or R2 fails, the moment-matching numbers are not read: the difference is diagnosed and recorded
  as a CHANGE first.

SYNTHETIC CHECK (`python3 filter_recheck.py synthetic`; grey-box's W3 world, 2,000 learners, 30 skills,
  a general factor g ~ N(0, 1), loadings N(0.85, 0.1^2), u_k ~ N(0, 0.48), the practice gain
  0.3 log(1 + earlier attempts), true 4PL items; seeds 20261002 and 20261003, grey-box's floor seeds).
  The filters get the TRUE prior (mu = 0, W = loadings, D = 0.48) and items (beta = 0.3), all learners.
  S-ID  identity: fstep.run_gauss(adf=False) equals gstate.run_gauss (a dense rank-1 prior and an arrow
        prior: general factor + six groups) and fstep.run_joint(adf=False, record_g) equals
        tstate.run_joint (P and g_hat) to 1e-9; fstep.run_joint(adf=True) equals
        fstep.run_gauss(adf=True) to 1e-9.
  S-AG  agreement where the two steps must agree: (i) the forecast before any update is the same, so
        every learner's first attempt has identical P under both (1e-12); (ii) at v = 0 with c = 0, d = 1
        (the canonical logistic, where observed and Fisher information coincide) step() returns the same
        g and J under both, relative difference under 1e-9 over a grid of a, a (m - b) and y; (iii) with
        c = 0, d = 1 and the prior variance scaled by 1e-4 the two filters' P differ by under 1e-3 at
        every attempt. Reported beside it: the mean |P difference| at the true items and prior.
  S-EX  exactness: evidence decay off (W3 has no forgetting), against the exact quadrature filter
        (gbox.grid_filter: g on 41 points, each u_k on 21 given g). PASS on both seeds if moment
        matching's log loss is within 0.001 nats per answer of the exact filter's AND its total
        log-likelihood gap to the exact filter is smaller than the Laplace step's. Reported: totals,
        per-answer gaps with learner-bootstrap intervals (200), and the mean residual y - P by the
        learner's total earlier attempts (the spurious learning term's signature) for all three filters.
  If S-ID fails the machinery is wrong: stop and fix. If S-AG or S-EX fails, the real re-computation
  still runs and every bottom-line sentence carries "(MOMENT MATCHING NOT VALIDATED)".

OUTPUT (out/, aggregates only): synthetic.json; gs-{xes,assist,eedi}.json (graph-state's record
  layout plus the reproduction checks and GS2's interval); s2-{assist,xes,eedi}.json (S2's layout,
  Part A only); comparison.json (every headline: original, recomputed, rule, MOVED / HOLDS).

LIMITS stated in advance: the original floors are not re-run under moment matching; moment matching is
  still a Gaussian approximation, one response at a time, with the hyperedge spread unchanged (a
  multi-skill response is spread evenly at J / nS); it is validated against an exact filter only on
  single-skill W3 at true parameters; S2 Part B, S1 and the S3 numbers are not re-computed; open
  corpora, not Lazuli's.

DIRECTION: symmetric -- no edge between skills is oriented. The re-check changes only the filter's
  update step; every reported change is signed (recomputed minus original), and no verdict is built from
  an unsigned comparison.

CHANGES (after registration; each before the affected statistic is read)
  1. R1 and R2 presumed bitwise reproduction (1e-9, 1e-6); it does not hold, for numerical reasons.
     calibrate.py's empirical-Bayes EM (C0's prior, before any filter) follows a different
     floating-point path under a different BLAS thread count: on identical ASSISTments data its 2PL
     prior took 34 EM rounds in the original run's log, 32 rounds at 2 threads and 36 at 1 thread here.
     S2's Eedi run (the first to finish) had every count and CLIM's log loss bit-identical to the
     original record but C0's log loss 2.6e-5 away, so R1 failed. The fix is a same-environment
     reference: each pipeline is also run end to end with the ORIGINAL Laplace step (`gs-lap`, `s2-lap`;
     the original gstate.run_gauss and tstate.run_joint, nothing replaced), on the same machine and
     thread count (1). The registered comparison (original record vs moment matching, rules (a)-(d))
     stays the primary reading. Beside it the comparison table reports the numerical drift (Laplace
     re-run minus original) and the step's effect (moment matching minus Laplace re-run). A cell MOVED
     by the primary rule whose step effect is itself within the same threshold is labelled
     "MOVED (drift)": it moved, but not because of the step. R1 becomes: counts identical and CLIM's
     log loss to 1e-12 (the data are the same); C0's shift is reported. R2 is reported, not gated.
     Disclosure: when this change was written the progress monitor had displayed one moment-matching
     line, S2 Eedi's Part A verdicts and A1's share (0.925 [0.905, 0.942]); no other moment-matching
     statistic had been read.

RESULTS (README.md has the tables; out/comparison.json every cell).
  Synthetic: identity, agreement and exactness PASS on both W3 seeds. Behind the exact filter: Laplace
  200.8 / 223.6 nats (0.00035 / 0.00039 per answer, under-predicting by 0.006-0.008 at every learner
  volume), moment matching 31.3 / 26.2 (0.00005).
  Reproduction: data identical (counts and CLIM bit-identical, all nine records); C0 drift 1.7-2.8e-5
  (CHANGE 1); the Laplace re-runs reproduce every original number within 6% of its threshold and every
  verdict and rank, so no cell is MOVED (drift).
  MOVED (by the step): GS2 general-factor share, XES3G5M 0.947 -> 0.930 [0.917, 0.943] (rank re-selected
  8 -> 12) and Eedi 0.991 -> 0.982 [0.975, 0.991]; GS4 C2 over C2-shuf and GS5b C3g over C2g on XES3G5M
  (+0.0075 -> +0.0089, +0.0010 -> +0.0013); A1's share of C2's cold gain on XES3G5M 0.912 -> 0.883
  [0.861, 0.907] (ASSISTments 1.050, Eedi 0.925 HOLD); A1's and A2-orth's shares of C2's every-attempt
  gain on XES3G5M (0.767 -> 0.742, 0.822 -> 0.794) and A2-orth's on Eedi (0.869 -> 0.849).
  HOLDS: every verdict string (graph-state and S2 Part A), C2's cold and every-attempt gains, the coupling
  attribution, C3 retention, interval calibration (C2 calibrated, C0 and A1 under-confident at cold
  windows), items saved, S2's C2g share (0.96-1.00), A1-global, A2-orth over A1.
  Bottom line: "implement A1 first" STANDS; "A1 captures 0.91-1.01" becomes 0.88-1.05; "one general factor
  gives 95-99%" becomes 93-100%; "the coupled state's intervals are calibrated" STANDS.

    python3 filter_recheck.py synthetic
    python3 filter_recheck.py gs assist | xes | eedi        # graph-state with moment matching
    python3 filter_recheck.py s2 assist | xes | eedi        # S2 Part A with moment matching
    python3 filter_recheck.py gs-lap | s2-lap <corpus>       # CHANGE 1: the same pipelines, original step
    python3 filter_recheck.py compare
"""

from __future__ import annotations

import json
import math
import resource
import sys
import time
from functools import partial
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GSD = ROOT / "studies/measurement/graph-state"
STD = ROOT / "studies/measurement/state-timescales"
GBD = ROOT / "studies/measurement/grey-box"
for p_ in (ROOT, ROOT / "studies/measurement/engine-calibration", GSD, STD, GBD, HERE,
           ROOT / "studies/end-to-end/xes3g5m-build"):
    sys.path.insert(0, str(p_))
import gstate as S  # noqa: E402
import tstate as T  # noqa: E402
import coupling as CP  # noqa: E402
import state_timescales as ST  # noqa: E402
import fstep as F  # noqa: E402

OUT = HERE / "out"
LAPLACE_RUN_GAUSS = S.run_gauss
LAPLACE_RUN_JOINT = T.run_joint
W3_SEEDS = (20261002, 20261003)
MM_TOL = 0.001
T0 = time.time()


def log(*a):
    gb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    print(f"[{time.time() - T0:7.0f}s {gb:4.1f}GB]", *a, flush=True)


def jdump(x):
    return json.dumps(x, indent=1, default=float) + "\n"


def mm_gauss(at, pr, items, K):
    return F.run_gauss(at, pr, items, K, adf=True)


def install_mm(gauss=mm_gauss):
    """THE ONE CHANGE: every coupled-filter call goes through the moment-matching step."""
    S.run_gauss = gauss
    T.run_joint = partial(F.run_joint, adf=True)


def ll_vec(P, y):
    P = np.clip(P, 1e-9, 1 - 1e-9)
    return -(y * np.log(P) + (1 - y) * np.log1p(-P))


def boot_mean(d, grp, nl, seed, B=200):
    sums, n = np.bincount(grp, d, nl), np.bincount(grp, None, nl)
    rng = np.random.default_rng(seed)
    bs = [float(w @ sums / (w @ n)) for w in (np.bincount(rng.integers(0, nl, nl), minlength=nl) for _ in range(B))]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return {"est": float(d.mean()), "lo": float(lo), "hi": float(hi)}


# ---------------------------------------------------------------- synthetic check

def w3(seed):
    import grey_box as GB
    cp = GB.world("W3", seed, 2000)
    tr = cp.truth
    K = len(tr["lam"])
    at = S.Attempts(cp.data, np.ones(len(cp.data.df), bool))
    pr = S.Prior("dense", np.zeros(K), np.full(K, tr["Du"]), W=np.asarray(tr["lam"], float)[:, None], name="truth")
    items = (tr["a"], tr["b"], tr["c"], tr["d"], tr["rate"])
    return cp, at, pr, items, K


def check_identity(at, pr, items, K):
    out = {}
    ref = LAPLACE_RUN_GAUSS(at, pr, items, K)
    out["run_gauss_dense"] = float(np.abs(F.run_gauss(at, pr, items, K, adf=False)["P"] - ref["P"]).max())
    grp = np.arange(K) // 5
    pa = S.Prior("arrow", pr.mu, pr.D * 0.8, lam0=pr.W[:, 0] * 0.9, lam=np.full(K, 0.3), grp=grp, G=int(grp.max()) + 1)
    out["run_gauss_arrow"] = float(np.abs(F.run_gauss(at, pa, items, K, adf=False)["P"]
                                          - LAPLACE_RUN_GAUSS(at, pa, items, K)["P"]).max())
    rj = LAPLACE_RUN_JOINT(at, pr, items, K, record_g=True)
    fj = F.run_joint(at, pr, items, K, record_g=True, adf=False)
    out["run_joint_P"] = float(np.abs(fj["P"] - rj["P"]).max())
    out["run_joint_g"] = float(max(np.abs(fj["g"] - rj["g"]).max(), np.nanmax(np.abs(fj["g_loo"] - rj["g_loo"]))))
    mg = F.run_gauss(at, pr, items, K, adf=True)["P"]
    mj = F.run_joint(at, pr, items, K, adf=True)["P"]
    out["mm_joint_vs_gauss"] = float(np.abs(mg - mj).max())
    out["passes"] = bool(max(out.values()) < 1e-9)
    return out


def check_agreement(at, pr, items, K):
    a, b, c, d, beta = items
    out = {}
    Pl = F.run_gauss(at, pr, items, K, adf=False)["P"]
    Pm = F.run_gauss(at, pr, items, K, adf=True)["P"]
    first = at.step == 0
    out["first_attempt_max_abs_dP"] = float(np.abs(Pl[first] - Pm[first]).max())
    out["true_items_mean_abs_dP"] = float(np.abs(Pl - Pm).mean())
    out["true_items_max_abs_dP"] = float(np.abs(Pl - Pm).max())
    A_, Z_, Y_ = np.meshgrid([0.3, 0.7, 1.0, 1.5, 2.5], np.linspace(-4, 4, 33), [0.0, 1.0], indexing="ij")
    A_, Z_, Y_ = A_.ravel(), Z_.ravel(), Y_.ravel()
    zero, one = np.zeros_like(A_), np.ones_like(A_)
    gl, Jl = F.step(A_, zero, zero, one, Z_ / A_, zero, Y_, False)
    gm, Jm = F.step(A_, zero, zero, one, Z_ / A_, zero, Y_, True)
    out["step_canonical_v0_max_rel"] = float(max(np.abs(gm / gl - 1).max(), np.abs(Jm / Jl - 1).max()))
    it0 = (a, b, np.zeros_like(c), np.ones_like(d), beta)
    p0 = S.Prior("dense", pr.mu, pr.D * 1e-4, W=pr.W * 1e-2)
    Pl0 = F.run_gauss(at, p0, it0, K, adf=False)["P"]
    Pm0 = F.run_gauss(at, p0, it0, K, adf=True)["P"]
    out["canonical_small_var_max_abs_dP"] = float(np.abs(Pl0 - Pm0).max())
    out["passes"] = bool(out["first_attempt_max_abs_dP"] < 1e-12 and out["step_canonical_v0_max_rel"] < 1e-9
                         and out["canonical_small_var_max_abs_dP"] < 1e-3)
    return out


def check_exact(cp, at, pr, items, K, seed):
    import gbox as G
    y = at.y
    Pe = G.grid_filter(at, cp.truth)
    Pl = F.run_gauss(at, pr, items, K, adf=False, decay=False)["P"]
    Pm = F.run_gauss(at, pr, items, K, adf=True, decay=False)["P"]
    le, ll, lm = ll_vec(Pe, y), ll_vec(Pl, y), ll_vec(Pm, y)
    out = {"answers": int(at.n), "learners": int(at.nl),
           "total_nats_behind_exact": {"laplace": float((ll - le).sum()), "moment_matching": float((lm - le).sum())},
           "per_answer_behind_exact": {"laplace": boot_mean(ll - le, at.l, at.nl, seed + 1),
                                       "moment_matching": boot_mean(lm - le, at.l, at.nl, seed + 1)},
           "laplace_minus_mm_per_answer": boot_mean(ll - lm, at.l, at.nl, seed + 1),
           "logloss": {"exact": float(le.mean()), "laplace": float(ll.mean()), "moment_matching": float(lm.mean())}}
    first = np.r_[0, np.nonzero(np.r_[False, at.l[1:] != at.l[:-1]])[0]]
    prior_n = np.arange(at.n) - first[at.l]                  # the learner's earlier attempts (rows sorted by learner, time)
    bins = ((0, 50), (50, 150), (150, 300), (300, 10 ** 9))
    out["mean_residual_by_learner_attempts"] = {
        f"{lo}-{hi if hi < 10 ** 9 else 'inf'}": {nm: float((y - P)[(prior_n >= lo) & (prior_n < hi)].mean())
                                                   for nm, P in (("exact", Pe), ("laplace", Pl), ("moment_matching", Pm))}
        for lo, hi in bins}
    gap_m, gap_l = out["total_nats_behind_exact"]["moment_matching"], out["total_nats_behind_exact"]["laplace"]
    out["passes"] = bool(out["per_answer_behind_exact"]["moment_matching"]["est"] <= MM_TOL and abs(gap_m) < abs(gap_l))
    return out


def synthetic():
    res = {"worlds": []}
    for seed in W3_SEEDS:
        cp, at, pr, items, K = w3(seed)
        log(f"W3 seed {seed}: {at.n:,} answers, {at.nl:,} learners, {K} skills")
        rec = {"seed": seed, "identity": check_identity(at, pr, items, K)}
        log(f"   identity {rec['identity']}")
        rec["agreement"] = check_agreement(at, pr, items, K)
        log(f"   agreement {rec['agreement']}")
        rec["exact"] = check_exact(cp, at, pr, items, K, seed)
        log(f"   exact {json.dumps(rec['exact'])}")
        res["worlds"].append(rec)
        del cp, at
    res["identity_passes"] = all(w["identity"]["passes"] for w in res["worlds"])
    res["agreement_passes"] = all(w["agreement"]["passes"] for w in res["worlds"])
    res["exact_passes"] = all(w["exact"]["passes"] for w in res["worlds"])
    res["validated"] = res["agreement_passes"] and res["exact_passes"]
    OUT.mkdir(exist_ok=True)
    (OUT / "synthetic.json").write_text(jdump(res))
    log(f"SYNTHETIC: identity {res['identity_passes']}, agreement {res['agreement_passes']}, exact {res['exact_passes']}")


# ---------------------------------------------------------------- graph-state with moment matching

class RankHook:
    """S.run_gauss during graph-state's fit: moment matching, and in the first n calls (the rank-selection
    calls, in RANKS order) also the original Laplace filter, for R2."""

    def __init__(self, n):
        self.left, self.lap, self.mm, self.copy_err = n, [], [], None

    def __call__(self, at, pr, items, K):
        o = F.run_gauss(at, pr, items, K, adf=True)
        if self.left > 0:
            self.left -= 1
            ol = LAPLACE_RUN_GAUSS(at, pr, items, K)
            if self.copy_err is None:
                self.copy_err = float(np.abs(F.run_gauss(at, pr, items, K, adf=False)["P"] - ol["P"]).max())
            self.lap.append(CP.cold_ll(ol["P"], at))
            self.mm.append(CP.cold_ll(o["P"], at))
        return o


def orig(study, name):
    return json.loads((ROOT / "studies/measurement" / study / "out" / f"{name}.json").read_text())


def gs(name, mm=True):
    loader = {"xes": CP.load_xes, "eedi": CP.load_eedi, "assist": CP.load_assist}[name]
    data, labels, hier = loader()
    o0 = orig("graph-state", name)
    hook = RankHook(len(CP.RANKS) if mm else 0)
    if mm:
        install_mm(hook)
    log(f"{name}: {len(data.df):,} rows, {data.df.attempt.nunique():,} attempts, {len(data.uid):,} learners")
    c0, items, P, info = CP.fit_all(data, hier)
    hook.left = 0
    if not mm:
        hook.lap = [info["rank_cold_logloss"][r] for r in CP.RANKS]
        hook.copy_err = 0.0
    rep = {"R2_laplace_val_cold_logloss": dict(zip(map(str, CP.RANKS), hook.lap)),
           "R2_original": o0["fit"]["rank_cold_logloss"],
           "R2_max_abs_diff": float(max(abs(hook.lap[j] - o0["fit"]["rank_cold_logloss"][str(r)])
                                        for j, r in enumerate(CP.RANKS))),
           "R2_copy_adf_false_vs_run_gauss": hook.copy_err}
    rep["R2_passes"] = bool(rep["R2_max_abs_diff"] < 1e-6 and hook.copy_err < 1e-9)
    log(f"R2: Laplace validation losses reproduce to {rep['R2_max_abs_diff']:.1e}; copy = run_gauss to {hook.copy_err:.1e}")
    at, pred, extra = CP.predict(data, hier, c0, items, P)
    ev = CP.evaluate(at, pred, extra, c0, items)
    res = CP.verdicts(ev, hier.groups is not None, None)
    res["fit"] = info
    res["data"] = {"rows": int(len(data.df)), "attempts": int(data.df.attempt.nunique()), "learners": int(len(data.uid)),
                   "items": int(data.I), "skills": int(data.df.k.max()) + 1, "test_attempts": int(at.n),
                   "test_learners": int(at.nl)}
    res["C2g_share_of_C2_M1"] = CP.ratio_ci(ev, "C2g", "C2", "C0", "cold_logloss")
    pc, po = res["point"]["C0"], o0["point"]["C0"]
    rep["R1_C0_logloss_diff"] = float(max(abs(pc["cold_logloss"] - po["cold_logloss"]), abs(pc["all_logloss"] - po["all_logloss"])))
    rep["R1_counts_equal"] = res["counts"] == o0["counts"]
    rep["R1_CLIM_logloss_diff"] = float(abs(res["point"]["CLIM"]["all_logloss"] - o0["point"]["CLIM"]["all_logloss"]))
    rep["R1_passes"] = bool(rep["R1_CLIM_logloss_diff"] < 1e-12 and rep["R1_counts_equal"])      # CHANGE 1
    res["reproduction"] = rep
    CP.report(name, res)
    fl = CP.floor_record()                       # graph-state's floor record, read only
    if fl["H_retention"] >= 0.5 and res["graph"] == "GRAPH CARRIES THE COUPLING":
        res["graph"] += " (not diagnostic: a general factor seen through siblings also passes)"
    if not fl["passes"]:
        for k_ in ("coupling", "graph", "which_skills", "guard_M2"):
            res[k_] += " (UNCALIBRATED)"
    res["floor"] = fl
    res["update_step"] = "moment matching (fstep.step adf=True)" if mm else "Laplace (original gstate.run_gauss)"
    log(f"R1 {rep['R1_passes']} (C0 diff {rep['R1_C0_logloss_diff']:.1e}); R2 {rep['R2_passes']}")
    OUT.mkdir(exist_ok=True)
    tag = "gs" if mm else "gs-lap"
    (OUT / f"{tag}-{name}.json").write_text(jdump(res))
    log(f"wrote out/{tag}-{name}.json")


# ---------------------------------------------------------------- S2 Part A with moment matching

def s2(name, mm=True):
    ST.fit_base = ST._fit_base                   # no parameter cache: nothing fitted elsewhere is read
    if mm:
        install_mm()
    cp = {"assist": ST.load_assist, "xes": ST.load_xes, "eedi": ST.load_eedi}[name]()
    o0 = orig("state-timescales", name)
    res = ST.run_corpus(cp, do_a=True, do_b=False)
    fl = ST.floor_record()                       # S2's floor record, read only
    res["floor"] = fl
    ST.mark_uncalibrated(res, fl)
    A, A0 = res["A"]["point"], o0["A"]["point"]
    rep = {"R1_C0_logloss_diff": float(max(abs(A[f"A|{s}|C0"]["logloss"] - A0[f"A|{s}|C0"]["logloss"]) for s in ("cold", "all"))),
           "R1_counts_equal": res["A"]["counts"] == o0["A"]["counts"],
           "R1_CLIM_logloss_diff": float(max(abs(A[f"A|{s}|CLIM"]["logloss"] - A0[f"A|{s}|CLIM"]["logloss"]) for s in ("cold", "all"))),
           "R3_run_joint_vs_run_gauss": res["exactness"]["run_joint_vs_run_gauss"]}
    rep["R1_passes"] = bool(rep["R1_CLIM_logloss_diff"] < 1e-12 and rep["R1_counts_equal"])      # CHANGE 1
    res["reproduction"] = rep
    res["update_step"] = "moment matching (fstep.step adf=True)" if mm else "Laplace (original)"
    log(f"R1 {rep['R1_passes']} (C0 diff {rep['R1_C0_logloss_diff']:.1e}); R3 {rep['R3_run_joint_vs_run_gauss']:.1e}")
    OUT.mkdir(exist_ok=True)
    tag = "s2" if mm else "s2-lap"
    (OUT / f"{tag}-{name}.json").write_text(jdump(res))
    log(f"wrote out/{tag}-{name}.json")


# ---------------------------------------------------------------- the comparison

GS_C = ("xes", "assist", "eedi")
S2_C = ("assist", "xes", "eedi")


def _ratio(g):
    return {"est": g["M1_gain_vs_C0"]["C2g"]["est"] / g["M1_gain_vs_C0"]["C2"]["est"]}


def gs_rows(r, original=False):
    """headline -> (kind, value) for one graph-state record; kind: num (rule a), numb (rule b), cov, str."""
    out = {"GS1 C2 M1 gain over C0": ("num", r["M1_gain_vs_C0"]["C2"]),
           "GS2 C2g share of C2's M1 gain": ("numb", _ratio(r) if original else r["C2g_share_of_C2_M1"]),
           "GS2b C2g M1 gain over C0": ("num", r["M1_gain_vs_C0"]["C2g"]),
           "GS3 C2 over C2-diag, M1": ("num", r["C2_over_C2diag_M1"]),
           "GS4 C2 over C2-shuf, M1": ("num", r["C2_over_C2shuf_M1"])}
    if "graph_retention" in r:
        out["GS5 C3 retention"] = ("num", r["graph_retention"])
        out["GS5b C3g over C2g, M1"] = ("num", r["C3g_over_C2g_M1"])
    out["GS6 C2 M2 gain over C0"] = ("num", r["M2_gain_vs_C0"]["C2"])
    for v in ("C2", "C3"):
        cal = r["M4_calibration"].get(v, {})
        for wn in ("cold", "warm"):
            if f"coverage_{wn}" in cal:
                out[f"GS7 {v} intervals, {wn}"] = ("cov", {"coverage": cal[f"coverage_{wn}"], "label": cal[f"intervals_{wn}"]})
    out["GS8 C2 items saved per 1,000, 20% risk"] = ("num", r["M5_items_saved"]["C2"]["0.2"])
    for k_ in ("coupling", "graph", "which_skills", "guard_M2"):
        out[f"GS9 verdict: {k_}"] = ("str", r[k_])
    out["GS9 chosen rank (reported)"] = ("report", r["fit"]["rank"])
    return out


def s2_rows(A):
    out = {"A1 A1 share of C2's cold gain": ("num", A["share_of_C2_cold"]["A1"]),
           "A2 C2 cold gain over C0": ("num", A["gain_vs_C0_cold"]["C2"]),
           "A2b A1 cold gain over C0": ("num", A["gain_vs_C0_cold"]["A1"]),
           "A3 C2g share of C2's cold gain": ("num", A["share_of_C2_cold"]["C2g"]),
           "A4 A1-global share": ("num", A["share_of_C2_cold"]["A1-global"]),
           "A5 A2-orth over A1, every attempt": ("num", A["A2_orth_over_A1_all"]),
           "A5b A1 share of C2's every-attempt gain": ("num", A["share_of_C2_all"]["A1"]),
           "A5c A2-orth share of C2's every-attempt gain": ("num", A["share_of_C2_all"]["A2-orth"])}
    for v in ("C0", "A1", "A2-orth", "C2g", "C2"):
        for wn in ("cold", "warm"):
            out[f"A6 {v} intervals, {wn}"] = ("cov", A["intervals"][v][wn])
    for v in ("A1", "A2-orth", "C2"):
        out[f"A7 {v} items saved per 1,000, 20% risk"] = ("num", A["items_saved"][v]["0.2"])
    for k_ in ("A1", "A1-global", "A1_guard_M2", "A2", "double_counting", "learner_information"):
        out[f"A8 verdict: {k_}"] = ("str", A[k_])
    return out


def _cell(kind, o, n, lap):
    """Rules (a)-(d) on original vs moment matching; drift and step effect against the Laplace re-run
    (CHANGE 1)."""
    c = {"original": o, "recomputed": n, "laplace_rerun": lap}
    if kind in ("num", "numb"):
        thr = (o["hi"] - o["lo"]) / 2 if kind == "num" else (n["hi"] - n["lo"]) / 2
        c.update(rule="a" if kind == "num" else "b", threshold=float(thr), change=float(n["est"] - o["est"]))
        c["moved"] = bool(abs(c["change"]) > thr)
        if lap is not None:
            c["drift"], c["step"] = float(lap["est"] - o["est"]), float(n["est"] - lap["est"])
            step_moves = abs(c["step"]) > thr
    elif kind == "cov":
        dq = lambda x, y: max(abs(x["coverage"][q] - y["coverage"][q]) for q in x["coverage"])
        c.update(rule="c+d", change=float(dq(n, o)))
        c["moved"] = bool(c["change"] > 0.02 or n["label"] != o["label"])
        if lap is not None:
            c["drift"], c["step"] = float(dq(lap, o)), float(dq(n, lap))
            step_moves = c["step"] > 0.02 or n["label"] != lap["label"]
    elif kind == "report":
        c.update(rule="reported", moved=False)
    else:
        c.update(rule="d", moved=bool(n != o))
        if lap is not None:
            step_moves = n != lap
    c["status"] = "REPORTED" if kind == "report" else "HOLDS"
    if c["moved"]:
        c["status"] = "MOVED (drift)" if lap is not None and not step_moves else "MOVED"
    return c


def compare():
    rows = {}
    for study, cs, tag, fn in (("graph-state", GS_C, "gs", None), ("state-timescales", S2_C, "s2", None)):
        for c in cs:
            f, fl = OUT / f"{tag}-{c}.json", OUT / f"{tag}-lap-{c}.json"
            if not f.exists():
                continue
            o, n = orig(study, c), json.loads(f.read_text())
            lap = json.loads(fl.read_text()) if fl.exists() else None
            if tag == "gs":
                ro, rn, rl = gs_rows(o, True), gs_rows(n), gs_rows(lap) if lap else None
            else:
                ro, rn, rl = s2_rows(o["A"]), s2_rows(n["A"]), s2_rows(lap["A"]) if lap else None
            for k, (kind, vo) in ro.items():
                rows.setdefault(k, {})[c] = _cell(kind, vo, rn[k][1], rl[k][1] if rl else None)
    summary = {}
    for k, cells in rows.items():
        st = [v["status"] for v in cells.values()]
        summary[k] = ("MOVED" if "MOVED" in st else "MOVED (drift)" if "MOVED (drift)" in st else
                      "REPORTED" if "REPORTED" in st else "HOLDS")
    syn = json.loads((OUT / "synthetic.json").read_text()) if (OUT / "synthetic.json").exists() else {}
    repro = {}
    for tag, cs in (("gs", GS_C), ("s2", S2_C)):
        for c in cs:
            for t in (tag, f"{tag}-lap"):
                f = OUT / f"{t}-{c}.json"
                if f.exists():
                    r = json.loads(f.read_text())
                    o = orig("graph-state" if tag == "gs" else "state-timescales", c)
                    rp = dict(r.get("reproduction") or {})
                    if tag == "gs":         # CHANGE 1's R1, recomputed for records written before it
                        clim = abs(r["point"]["CLIM"]["all_logloss"] - o["point"]["CLIM"]["all_logloss"])
                        cnt = r["counts"] == o["counts"]
                    else:
                        clim = max(abs(r["A"]["point"][f"A|{s_}|CLIM"]["logloss"] - o["A"]["point"][f"A|{s_}|CLIM"]["logloss"])
                                   for s_ in ("cold", "all"))
                        cnt = r["A"]["counts"] == o["A"]["counts"]
                    rp.update(R1_CLIM_logloss_diff=float(clim), R1_counts_equal=cnt, R1_passes=bool(clim < 1e-12 and cnt))
                    repro[f"{t}-{c}"] = rp
    out = {"rows": rows, "summary": summary, "synthetic_validated": syn.get("validated"), "reproduction": repro}
    (OUT / "comparison.json").write_text(jdump(out))

    def fmt(v):
        if isinstance(v, dict) and "est" in v:
            return f"{v['est']:+.4f}"
        if isinstance(v, dict) and "label" in v:
            return "/".join(f"{v['coverage'][q]:.2f}" for q in v["coverage"]) + " " + v["label"][:5]
        return str(v)
    for k, cells in rows.items():
        parts = []
        for c, v in cells.items():
            extra = f" lap {fmt(v['laplace_rerun'])}" if v["laplace_rerun"] is not None else ""
            parts.append(f"{c} {fmt(v['original'])} -> {fmt(v['recomputed'])}{extra} [{v['status']}]")
        print(f"{summary[k]:<13} {k}: " + "; ".join(parts))


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "synthetic":
        synthetic()
    elif what == "gs":
        gs(sys.argv[2])
    elif what == "s2":
        s2(sys.argv[2])
    elif what == "gs-lap":
        gs(sys.argv[2], mm=False)
    elif what == "s2-lap":
        s2(sys.argv[2], mm=False)
    elif what == "compare":
        compare()
    else:
        raise SystemExit(__doc__)
