"""PRE-REGISTERED: is there dependence between skills beyond one latent trait, at the pair level?

iita_dense.py (IITA-DENSE.md) asked whether corrected-IITA finds structure beyond ability and
difficulty on dense 15-skill sets. On synthetic data its detection floor FAILS: one planted
prerequisite moves the implication count by ~0 against a null band 11-39 wide. An exploratory
pair-level scan against the same fixed-margins null detected 12 of 12 planted pairs but fired on
20 of 20 no-dependency worlds, because a fixed-margins null is exact only when every skill
discriminates equally (Rasch): unequal discrimination reads as structure. This design keeps the
pair-level scan and replaces the null with a fitted item-response model that holds ability,
difficulty AND discrimination, so what is left is local dependence beyond one latent trait.

Reads XES3G5M (attempts.tsv under $XES_DIR) and ASSISTments 2012-13 (assist_slim.csv under
$ASSIST_DIR) through iita_dense.real_sets, i.e. surmise_graphs' loaders, which resolve them with
shared.paths.data_path. Raw exports stay outside the repo; only per-set aggregates (skill ids, fitted
item parameters, counts, rates, z-scores) are written. --synthetic reads no corpus.

Seen while this was written, not chosen from: board/history.json's entry for iita_dense's real run
reports 15 fifteen-skill sets on XES3G5M and 2 on ASSISTments. By the < 5 scored-sets rule, set
before that entry was read, ASSISTments will be UNANSWERABLE here. The entry also gives iita_dense's
own XES3G5M outcome (floor fails; UNANSWERABLE). Nothing below was changed in response, and no
statistic of this design has been computed on either corpus.

PRE-REGISTRATION (written before any real run; the design as first specified is kept below, and every
change the synthetic run forced is listed under CHANGES with its reason, also before any real run)

UNITS        The 15-skill sets of iita_dense.py, built by its real_sets (imported, not copied):
             surmise_graphs' construction, items tagged to one skill only, mastery = at least half
             of a learner's attempts on the skill correct, complete responders only, 200-3000
             learners, at most 20 sets per corpus, and only sets of exactly K = 15 skills are units.
             A set whose observed-data fit does not converge is counted and not scored.
MODEL        Unidimensional 2PL with two common asymptotes (CHANGE 4): P(mastered j | theta) =
             g + (1 - g - l) logistic(a_j theta + c_j), theta ~ N(0, 1); a_j and c_j per skill (so
             difficulty -c_j/a_j and discrimination a_j are free), g and l shared. Fitted by marginal
             maximum likelihood on 31 Gauss-Hermite nodes, the likelihood maximised by L-BFGS-B with
             its analytic gradient (fit_2pl; CHANGE 5), a in [0.2, 6], |c| <= 20, g, l in [0, 0.3].
             First specified as a plain 2PL fitted by Bock-Aitkin EM.
             Recovery is checked on synthetic data (RESULTS). MML, not joint ML, because joint ML is
             inconsistent with a fixed 15 items and needs an ad hoc correction; MML needs none.
NULL         Parametric bootstrap from the fitted model: R = 500 learner samples of the set's size
             (theta ~ N(0, 1), responses from the fitted model), each REFITTED, warm-started at the
             fit. A draw's residual is r*_ij = b*_ij - E_ij(refit), so the fitting's own absorption of
             a deviation is in the null as it is in the observed statistic.
STATISTIC    b_ij = learners who mastered j but not i (IITA's counterexamples to i -> j), for every
             ordered pair. Residual r_ij = b_ij - E_ij, E_ij = n pi_ij, pi_ij = P(not i, j) under the
             fitted model (quadrature), studentised by the same fit's binomial sd: t_ij = r_ij /
             sqrt(n pi_ij (1 - pi_ij)) (CHANGE 7). Standardised against its bootstrap distribution:
             z_ij = (t_ij - mean t*_ij) / sd t*_ij, every bootstrap draw studentised by its own
             refit. A pair is scanned only if its bootstrap mean count is >= 5 (a rarer cell cannot
             show a deficit).
DEFICIT SIGN A prerequisite i -> j predicts b_ij BELOW the model: z_ij < 0. Only the lower tail is
             tested; an excess of counterexamples is never read as structure.
SET TEST     T = min z_ij over scanned ordered pairs. Within-set max-statistic correction
             (Westfall-Young single step): each pair's adjusted p is (1 + #{T* <= z_ij}) / (R + 1),
             T* the minimum over the same pairs in each bootstrap draw. A pair is SIGNIFICANT at
             adjusted p < 0.025 (CHANGE 8; first specified at 0.05).
SECONDARY    Pairs passing BH-FDR 0.05 on one-sided normal p of z_ij (R = 500 cannot resolve the
             p < 0.05/210 a permutation BH would need). Reported, never verdict-bearing.
CONFOUNDS    stated in advance and each given a synthetic world (--synthetic):
             (1) MULTIDIMENSIONALITY. Two latent traits leave local dependence that is no
             prerequisite. First specified check: ASYMMETRY, a prerequisite depresses b_ij but not
             b_ji, a shared second trait both; a significant pair counts only if z_ji > -1.645.
             Replaced by ISOLATION (CHANGES 1-2).
             (2) 2PL MISFIT from guessing or slip: a 3PL world (per-skill guessing 0.1-0.3) and a
             world with 5% misclassification each way (iita_dense's synthetic generator).
             Added: a DOUBLET world (a second trait shared by two skills only), to measure the one
             multidimensional case isolation cannot see.
FLOOR        On each corpus's own scored sets, written out before any observed statistic: into the
             real matrix, iita_dense.plant at 15 random placements per type: PAIR i -> j (learners
             failing i fail j with probability 0.9) and GATE (i AND k) -> j (failing either, 0.9);
             CHAIN a -> b -> c, 10 placements, reported and never verdict-bearing. A planted matrix is
             refitted (warm start) and standardised against the unplanted set's bootstrap; a plant
             is DETECTED when a planted ordered edge meets the verdict-bearing criterion (for GATE,
             either arm; for CHAIN, either link). Scoring against the unplanted set's bootstrap is a
             shortcut; the synthetic run checks it against each plant's own 500-draw calibration.
             The FLOOR PASSES if the median per-set PAIR detection rate is >= 0.8. GATE is reported
             beside it.
FALSE POS.   The same pipeline (own fit, own 500-draw calibration, own score) on data simulated
             FROM THE FITTED MODEL of each scored set, 2 simulations per set (CHANGE 6): no
             dependency by construction. The fraction whose verdict-bearing flag fires (an ISOLATED
             significant pair) is the corpus's calibrated per-set rate. Above 0.10 the corpus is
             UNANSWERABLE. It checks the bootstrap, not the model: misfit the fitted model shares
             with the data it simulates (the guessing world below) is invisible to it.
VERDICTS     per corpus, exactly one of:
               UNANSWERABLE        the floor fails (median per-set PAIR detection < 0.8), or the
                                   fitted-model false-positive rate > 0.10, or fewer than 5 sets
                                   are scored.
               PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT (CHANGE 3; first specified as
                                   PREREQUISITE-LIKE DEPENDENCE BEYOND ONE TRAIT)
                                   the floor passes and the number of scored sets with an ISOLATED
                                   significant pair exceeds chance: one-sided binomial
                                   P(X >= k | n scored, p0) < 0.05, p0 = max(0.05, the corpus's
                                   fitted-model false-positive rate).
               NO DEPENDENCE DETECTED  otherwise.
             Reported beside it and never verdict-bearing: sets with any significant pair, sets with
             a CLUSTERED significant pair (local dependence of the multidimensional kind), sets with
             an asymmetric significant pair, BH pairs, and the significant pairs themselves.
FOR PAPER 1  what each outcome means for the item-tree bullet, fixed now:
               both NO DEPENDENCE DETECTED   the bullet generalises in its strong form: on two dense
                                             corpora, against a demonstrated pair-level floor, a
                                             single latent trait (ability, difficulty and
                                             discrimination) leaves no pairwise dependence of the
                                             size a 0.9-strength prerequisite leaves. Chains and
                                             dependencies inside multidimensional clusters stay
                                             excepted: the floor does not cover them.
               any PAIRWISE LOCAL DEPENDENCE the bullet must be narrowed to sparse MOOCCubeX item
                                             sets and to IITA's count statistic: dense skill data
                                             carry pairwise dependence one trait does not explain.
                                             It may not be called prerequisite structure: this
                                             statistic cannot orient a pair (CHANGE 1) and cannot
                                             tell a prerequisite from a trait shared by exactly two
                                             skills (the doublet world). Paper 1 may say the data
                                             hold candidate pairs for an experiment, not edges.
               any UNANSWERABLE              that corpus neither supports nor challenges the
                                             bullet and Paper 1 may not cite it as corroboration.
               one NO DEPENDENCE, one PAIRWISE  the bullet is corpus-dependent and says so.
             Clustered local dependence, however common, changes none of these: it is the
             multidimensionality every skill set spanning topics has, and says nothing about
             prerequisites.

DIRECTION: (i, j) means i is the prerequisite of j ("j mastered implies i mastered"; b_ij counts
learners who mastered j but not i), per iita.py (DAKS) and surmise_graphs.py. The verdict does not
read orientation: at fitted margins a pair's 2x2 table has one degree of freedom, so a deficit in
b_ij is the same count deficit in b_ji (CHANGE 1). The orientation check is still run with
shared.direction.reversed_arrow on the plants (planted arrows significant as claimed against
significant reversed) and reported. It reads CLAIMED, but only because studentisation gives the
rarer cell the larger z and a plant makes the dependant the harder skill: that is difficulty order,
which a second trait between skills of unequal difficulty reproduces, not evidence of orientation.
Every significant ordered pair is reported; both orientations of one pair often appear.

CONTROL SIZE shared.controls.check_control_scale compares the cells a bootstrap draw differs from
             the observed matrix in against the cells a plant changes; the null must be at least
             half the median plant (it is ~30x).

ORDER        fit + bootstrap calibration (reads no residual of the observed matrix) -> floor ->
             fitted-model false positives (both written to the output file) -> observed statistic ->
             verdict.

CHANGES FORCED BY THE SYNTHETIC RUN (all before any real run)
  1. Asymmetry dropped as the multidimensionality check. First run (2PL, 20 sets a world): PAIR
     plants were significant in 92% of placements and asymmetric in 0-1%; the reverse pair was a
     deficit of the same size (median z -9.5 claimed, -9.4 reversed). Arithmetic says why: with both
     margins fitted, the pair's 2x2 table has one free cell, so any residual in b_ij is the same
     count residual in b_ji. Asymmetry would reject true prerequisites, not second traits. Kept as
     a reported flag.
  2. ISOLATION is the multidimensionality check instead. A significant pair (i, j) is ISOLATED if
     no third skill k has an unordered discordance deficit ((b_ik + b_ki), standardised the same
     way) with both i and j carrying at least 0.4 of the pair's own: z_ik, z_jk <= min(-1.645,
     0.4 z_ij). Otherwise CLUSTERED. A second trait over several skills makes triangles; a PAIR or
     GATE plant does not (a chain does, one reason chains stay outside the floor). First run (plain
     2PL, legs at an absolute z <= -1.645), two-factor world (10 + 5 skills, traits correlated
     0.3-0.8): a significant pair in 20 of 20 sets, CLUSTERED in 19, ISOLATED in 2. Under CHANGE 4's
     model the absolute rule cost floor (2PL world PAIR isolated 0.89 -> 0.76, median per set 0.80):
     refitting a planted matrix leaves small deficits around the plant that complete chance
     triangles, hence the relative leg. Exploratory comparison on 12 fresh sets a world (other
     seeds than RESULTS), R = 200, 10 PAIR plants a set; two-factor sets firing ISOLATED, then mean
     PAIR floor in the 2PL / prerequisite / two-factor / guessing worlds:
       absolute -1.645   0 of 12   0.79 / 0.65 / 0.67 / 0.67
       absolute -2.326   1 of 12   0.81 / 0.71 / 0.69 / 0.68
       relative 0.25     0 of 12   0.80 / 0.70 / 0.77 / 0.69
       relative 0.4      0 of 12   0.83 / 0.77 / 0.78 / 0.70   (kept)
     Tried earlier on the plain 2PL and dropped: legs that are themselves significant (7 of 12
     two-factor sets through) and >= 2 third skills (4 of 12). Limit, measured below: a second
     trait shared by exactly two skills (the doublet world) has no third skill to betray it and
     fires as ISOLATED.
  3. The positive verdict names what the statistic can see: PAIRWISE LOCAL DEPENDENCE BEYOND ONE
     TRAIT, not PREREQUISITE-LIKE, because orientation is not identified (1) and doublets pass (2).
  4. Common asymptotes added to the 2PL. First run, misclassified world (2PL + 5% misclassification
     each way, no dependency): ISOLATED pairs in 4 of 20 sets, binomial p = 0.016, a false
     positive corpus verdict; its fitted-model false-positive check read 0.00 because data
     simulated from a plain 2PL fit carry no misclassification, so the check cannot catch misfit
     it shares with the null. A k/n >= 0.5 mastery rule on a few attempts misclassifies, so real
     data have this. Two shared parameters (g, l) absorb it; per-skill asymptotes (a 4PL) are
     not identified at n = 200. Exploratory rerun, 12 sets a world: misclassified fires 1 of 12.
  5. The fit moved from Bock-Aitkin EM to direct maximisation (L-BFGS-B, analytic gradient). The
     asymptotes made EM crawl (~500 iterations at a 1e-4 parameter tolerance, n = 3000), and at a
     1e-3 tolerance a third run's fitted-model false-positive rate rose above nominal (2PL world
     0.075, prerequisite world 0.13 ISOLATED, 0.24 any): a cold-started EM stops short of the
     optimum on the observed data, while warm-started bootstrap refits start at it, so observed
     residuals carried fitting error the null did not. L-BFGS-B converges to the optimum from
     either start (stopping at ftol 1e-10, projected gradient 1e-5 on the mean log-likelihood; the
     largest change in any expected count against a tighter fit is 0.06, count sd ~24, n = 3000).
     One BLAS thread per worker: with contended threads L-BFGS-B ran ~10x slower.
  6. Fitted-model simulations per set 1 -> 2. First run, 2PL world: 2 of 20 fired (0.10), exactly
     the UNANSWERABLE line on a nominal 5% rate; 40 draws per corpus make that gate less of a coin
     toss (P(> 4 of 40 | 0.05) = 0.05).
  7. Residuals studentised by each dataset's own fit before the bootstrap standardisation. Same
     third run: the raw residual standardised by bootstrap moments (first specified) fired in 7 of 40
     fitted-model simulations in the prerequisite world. The moments come from the fitted
     parameters, not the true ones, and the minimum over 210 pairs finds whichever pair's sd the fit
     understates. A statistic studentised by its own fit is close to pivotal, which is the standard
     cure (the bootstrap of a studentised statistic is second-order accurate). Exploratory check, 60
     fitted-model simulations per world at R = 200: raw 0.067 / 0.067 (2PL-fitted / prerequisite-
     fitted) rejections at 0.05, studentised 0.050 / 0.050.
  8. Pair significance at max-T adjusted p < 0.025, not 0.05. The fitted-model gate reads 40
     simulations against 0.10; at a true per-set rate of 0.07 that gate fails a well-behaved corpus
     about a third of the time. At 0.025 the exploratory studentised rate was 0.017 / 0.033. The
     binomial's chance rate keeps its floor of 0.05, so the stricter pair level makes the corpus
     test more conservative, not less.

SYNTHETIC RESULTS (--synthetic, out/iita-pairscan-synthetic.json; no corpus read). Final design,
six worlds of 20 sets: 15 skills, 200-3000 learners (log-uniform, set 0 at 3000), discrimination
U(0.5, 2.5), difficulty U(-2, 0.5), R = 500, 2 workers. Worlds: 2PL (no dependency); prerequisite
(2PL plus one PAIR and one GATE planted per set, as iita_dense's `dependency`); two-factor (skills
0-9 on one trait, 10-14 on a second, correlation 0.3-0.8, no prerequisite); guessing (3PL, per-skill
guessing 0.1-0.3, no prerequisite); misclassified (2PL + 5% flips each way, no prerequisite);
doublet (skills 13-14 on a second trait, no prerequisite).
  recovery    plain 2PL, n = 200 / 1000 / 3000, 20 fits each: RMSE a 0.60 / 0.21 / 0.10 (bias +0.18
              / +0.07 / +0.02), RMSE difficulty 0.30 / 0.11 / 0.07, g and l <= 0.025. With 5%
              misclassification: a 0.86 / 0.25 / 0.16, difficulty 0.39 / 0.13 / 0.09, g and l 0.036 /
              0.021 / 0.016 (bias <= 0.003). All converged. The n = 200 upward bias in a is MML's
              usual small-sample one and is in the bootstrap too.
  world          fires: isol any clust asym  PAIR floor (sig/isol) GATE CHAIN  fit.FP  binom p  verdict
  2PL                   0/20   0    0    0   1.00 (0.94/0.93)    1.00 1.00   0.050   1        NONE
  prerequisite         19/20  19   10    4   0.90 (0.96/0.89)    0.93 0.90   0.075   8e-21    PAIRWISE
  two-factor            1/20  20   19    0   0.97 (0.98/0.95)    1.00 1.00   0.025   0.64     NONE
  guessing (3PL)        2/20   2    0    0   1.00 (1.00/0.99)    1.00 1.00   0.000   0.26     NONE
  misclassified         0/20   0    0    0   1.00 (0.99/0.99)    1.00 1.00   0.000   1        NONE
  doublet               8/20   8    0    0   1.00 (0.97/0.97)    1.00 0.95   0.000   3e-6     PAIRWISE
              (NONE = NO DEPENDENCE DETECTED, PAIRWISE = PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT;
              fires: sets with a significant pair that is ISOLATED / any / CLUSTERED / asymmetric;
              floor: median per-set detection by the verdict criterion, then all placements'
              significant and ISOLATED rates; fitted FP: 40 fitted-model simulations per world.)
  detection   prerequisite world, the planted truths on the observed matrices: PAIR significant in
              19 of 20 sets, GATE (either arm) 19 of 20; 10 sets also hold a significant pair that
              was not planted (two dependants of one planted prerequisite are dependent on each
              other). Sets under 600 learners detect PAIR plants at 0.87-0.97, larger sets 0.89-1.00.
  confounds   two-factor: some pair is significant in every set and CLUSTERED in 19 of 20; 1 fires
              ISOLATED, so the verdict holds. Guessing and misclassification: 0-2 of 20, verdict
              holds; the guessing world's fitted-model check reads 0.00 while it fires 2 of 20,
              the shared-misfit blind spot stated above. Doublet: fires ISOLATED in 8 of 20 and
              returns the positive verdict, as expected: this is the case the verdict wording
              exists for.
  asymmetry   planted PAIR arrows asymmetric in 2-5% of placements in every world, GATE 13-35%:
              dropped as a check (CHANGE 1), still reported.
  direction   planted arrows significant as claimed / reversed: 814/584, 795/562, 864/659,
              877/513, 858/577, 846/630 (worlds in table order): CLAIMED, for the difficulty-order
              reason under DIRECTION.
  shortcut    15 PAIR plants on 3 sets of the 2PL world scored against their own 500-draw
              calibration as well as the set's: ISOLATED 15 / 15 and significant 15 / 15 both
              ways, critical z -3.60 / -3.61.
  other       fitted-model false positives pooled over worlds 6 of 240 (0.025); in-sample rate of
              ISOLATED firing across bootstrap draws 0.021-0.022; 1 of 120 observed fits failed to
              converge in the third run and none here; 14 discriminations at the bound of 6 across
              the prerequisite world's sets (near-deterministic planted pairs), 0-3 elsewhere;
              control scale 27-36x.
  expected    Real skill sets span topics, so CLUSTERED dependence is expected to be common and is
              not verdict-bearing. The positive verdict needs ISOLATED pairs in more sets than
              chance, and would then say only that some skill pairs share more than ability.

RUNTIME AND BUDGET  Final synthetic run: 59-100 s wall per set on 2 workers, ~2.4 h for 120 sets.
             One 501-fit calibration takes a median 31-61 s (one core), 54-127 s at n = 3000. A real
             set costs three calibrations (observed, two fitted-model simulations) plus 40 plant
             fits: at most ~6.5 min a core at n = 3000. On 4 workers: 20 sets of 3000 ~5 rounds,
             ~33 min, plus loading, inside 45 min per corpus. R = 500 and 15/15/10 placements kept.

    python3 iita_pairscan.py --synthetic --workers 2        # out/iita-pairscan-synthetic.json
    python3 iita_pairscan.py --workers 4                    # out/iita-pairscan.json; both corpora
    python3 iita_pairscan.py --corpus xes3g5m --workers 4   # out/iita-pairscan-xes3g5m.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")      # one BLAS thread a worker: L-BFGS-B slows ~10x when they contend
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
import iita_dense as dense  # noqa: E402  (set construction, plants, binomial tail)
from shared.controls import check_control_scale  # noqa: E402
from shared.direction import reversed_arrow  # noqa: E402

SEED = 20260926
K = dense.K                 # 15 skills per set
R = 500                     # parametric-bootstrap draws per calibration
Q = 31                      # Gauss-Hermite quadrature nodes, theta ~ N(0, 1)
A_MIN, A_MAX = 0.2, 6.0     # discrimination bounds in the M-step
C_MAX = 20.0                # intercept bound
G_MAX = 0.3                 # bound on the common asymptotes g, l
FTOL, GTOL, MAX_ITER = 1e-10, 1e-5, 1000   # L-BFGS-B stopping rule, mean log-likelihood (CHANGE 5)
MIN_EXPECTED = 5.0          # a pair is scanned only if its bootstrap mean counterexample count >= this
ALPHA = 0.025               # max-T adjusted level at which a pair is significant (CHANGE 8)
FDR = 0.05                  # BH level of the secondary pair list
CHANCE_MIN = 0.05           # floor on the per-set chance rate the binomial is scored against
Z_ASYM = 1.645              # the reverse pair counts as a deficit too if z_ji <= -Z_ASYM
ISO_FRAC = 0.4              # a triangle leg must carry this share of the pair's deficit (CHANGE 2)
N_PAIR, N_GATE, N_CHAIN = 15, 15, 10
FLOOR_RATE = 0.8            # median per-set PAIR detection the floor needs
FP_MAX = 0.10               # fitted-model false-positive rate above which a corpus is UNANSWERABLE
FP_REPS = 2                 # fitted-model simulations per set (CHANGE 6)
MIN_SCORED = 5
CRITERION = "isolated"      # the verdict-bearing set-level flag (CHANGES 1-2)

POSITIVE = "PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT"   # CHANGE 3
VERDICTS = ("UNANSWERABLE", POSITIVE, "NO DEPENDENCE DETECTED")

GX, GW = np.polynomial.hermite_e.hermegauss(Q)
GW = GW / GW.sum()
LOGW = np.log(GW)
OFF = ~np.eye(K, dtype=bool)


# ----------------------------------------------------------------------------- the 2PL

def compress(X: np.ndarray):
    """Unique response patterns and their counts; EM cost scales with patterns, not learners."""
    m = X.shape[1]
    codes = (X.astype(np.int64) << np.arange(m)).sum(1)
    u, cnt = np.unique(codes, return_counts=True)
    return ((u[:, None] >> np.arange(m)) & 1).astype(float), cnt.astype(float)


def prob(th, theta) -> np.ndarray:
    """P(mastered | theta) = g + (1 - g - l) * logistic(a theta + c), (len(theta), m)."""
    a, c, g, l = th
    return g + (1 - g - l) / (1 + np.exp(-(np.asarray(theta)[:, None] * a + c)))


def negloglik(x: np.ndarray, U: np.ndarray, cnt: np.ndarray):
    """Mean negative marginal log-likelihood and its gradient; x = (a_1..a_m, c_1..c_m, g, l)."""
    m = U.shape[1]
    a, c, g, l = x[:m], x[m:2 * m], x[2 * m], x[2 * m + 1]
    S = 1 / (1 + np.exp(-(GX[:, None] * a + c)))                       # (Q, m)
    P = np.clip(g + (1 - g - l) * S, 1e-12, 1 - 1e-12)
    ll = U @ np.log(P).T + (1 - U) @ np.log1p(-P).T + LOGW
    top = ll.max(1, keepdims=True)
    post = np.exp(ll - top)
    tot = post.sum(1)
    post *= (cnt / tot)[:, None]
    N, R1 = post.sum(0), (U.T @ post).T                                  # (Q,), (Q, m)
    D = R1 / P - (N[:, None] - R1) / (1 - P)                             # d loglik / d P
    dS = D * (1 - g - l) * S * (1 - S)
    grad = np.concatenate([(dS * GX[:, None]).sum(0), dS.sum(0), [(D * (1 - S)).sum(), -(D * S).sum()]])
    n = cnt.sum()
    return -float((cnt * (top[:, 0] + np.log(tot))).sum()) / n, -grad / n


def fit_2pl(X: np.ndarray, init=None):
    """Unidimensional 2PL with two COMMON asymptotes, by marginal maximum likelihood.

    P(x_j = 1 | theta) = g + (1 - g - l) logistic(a_j theta + c_j), theta ~ N(0, 1) on Q Gauss-Hermite
    nodes. g (a false 'mastered') and l (a false 'not mastered') are shared by every skill, so the
    model has 2K + 2 parameters; they absorb the misclassification a k/n >= 0.5 mastery rule makes
    (CHANGE 4). The marginal likelihood is maximised directly by L-BFGS-B with its analytic gradient
    (the Fisher identity: expected counts from the posterior over nodes, as in Bock-Aitkin EM)
    (CHANGE 5), within a in [A_MIN, A_MAX], |c| <= C_MAX, g and l in [0, G_MAX].
    Returns ((a, c, g, l), iterations, converged).
    """
    U, cnt = compress(X)
    m = X.shape[1]
    if init is None:
        p = np.clip(X.mean(0), 0.01, 0.99)
        x0 = np.concatenate([np.ones(m), 1.3 * np.log(p / (1 - p)), [0.02, 0.02]])
    else:
        x0 = np.concatenate([init[0], init[1], [init[2], init[3]]])
    bounds = [(A_MIN, A_MAX)] * m + [(-C_MAX, C_MAX)] * m + [(0.0, G_MAX)] * 2
    x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
    res = minimize(negloglik, x0, args=(U, cnt), jac=True, method="L-BFGS-B", bounds=bounds,
                   options=dict(maxiter=MAX_ITER, ftol=FTOL, gtol=GTOL))
    x = res.x
    th = (x[:m].copy(), x[m:2 * m].copy(), float(x[2 * m]), float(x[2 * m + 1]))
    return th, int(res.nit), bool(res.success)


def simulate(th, n: int, rng: np.random.Generator) -> np.ndarray:
    return rng.random((n, len(th[0]))) < prob(th, rng.normal(size=n))


def counterexamples(X: np.ndarray) -> np.ndarray:
    """b[i, j] = learners who mastered j but not i: the counterexamples to 'i is a prerequisite of j'."""
    Xi = X.astype(np.int64)
    return ((1 - Xi).T @ Xi).astype(float)


def expected(th, n: int) -> np.ndarray:
    """n * P(not i, j) under the fitted marginal model, by quadrature."""
    P = prob(th, GX)
    return n * (((1 - P) * GW[:, None]).T @ P)


def residuals(X, th):
    """Counterexample residuals studentised by the fit's own binomial sd (CHANGE 7).

    Ordered: (b_ij - E_ij) / sqrt(n pi_ij (1 - pi_ij)), pi_ij = P(not i, j). Unordered: the same for
    the discordance b_ij + b_ji. Each dataset is studentised by its own fit, observed and bootstrap
    alike, so the bootstrap works on a near-pivotal quantity.
    """
    n = len(X)
    E = expected(th, n)
    pi = E / n
    r = counterexamples(X) - E
    pu = pi + pi.T
    with np.errstate(invalid="ignore", divide="ignore"):
        z = r / np.sqrt(np.maximum(n * pi * (1 - pi), 1e-9))
        zu = (r + r.T) / np.sqrt(np.maximum(n * pu * (1 - pu), 1e-9))
    return z, zu


# ----------------------------------------------------------------------------- calibration and scoring

def calibrate(X: np.ndarray, seed, draws: int = R) -> dict:
    """Fit the 2PL to X, then `draws` parametric-bootstrap samples from the fit, each refitted.

    Each draw's residuals are studentised by its own refit (`residuals`); their bootstrap mean and sd
    standardise X's residuals later, so the fitting's own absorption of a deviation is in the null
    too. Returns the fit and the null only: nothing here reads the test statistic of X.
    """
    rng = np.random.default_rng(seed)
    th, iters, ok = fit_2pl(X)
    n = len(X)
    rs, ru = np.empty((draws, K, K)), np.empty((draws, K, K))
    bmean = np.zeros((K, K))
    fails = 0
    for r in range(draws):
        Xs = simulate(th, n, rng)
        th2, _, ok2 = fit_2pl(Xs, init=th)
        fails += not ok2
        bmean += counterexamples(Xs) / draws
        rs[r], ru[r] = residuals(Xs, th2)
    mu, sd = rs.mean(0), rs.std(0, ddof=1)
    mu_u, sd_u = ru.mean(0), ru.std(0, ddof=1)
    scan = OFF & (bmean >= MIN_EXPECTED) & (sd > 0)
    sd, sd_u = np.where(sd > 0, sd, np.inf), np.where(sd_u > 0, sd_u, np.inf)
    cal = dict(th=th, a=th[0], c=th[1], g=th[2], l=th[3], iters=iters, converged=ok, n=n,
               mu=mu, sd=sd, mu_u=mu_u, sd_u=sd_u,
               scan=scan, boot_nonconverged=fails)
    Zs = (rs - mu) / sd
    Us = (ru - mu_u) / sd_u
    cal["tstar"] = np.sort(np.where(scan, Zs, np.inf).reshape(draws, -1).min(1))
    # per-draw set flags under the calibrated threshold: the in-sample rate of each criterion
    flags = [classify(Zs[r], Us[r], cal) for r in range(draws)]
    cal["boot_rates"] = {k: float(np.mean([f[k] for f in flags]))
                         for k in ("any", "asymmetric", "isolated", "clustered")}
    cal["hamming"] = float(np.mean([(simulate(th, n, rng) != X).sum() for _ in range(5)]))
    return cal


def adj_p(z, tstar) -> np.ndarray:
    """Westfall-Young single-step max-statistic adjusted p: (1 + #{T* <= z}) / (R + 1)."""
    return (1 + np.searchsorted(tstar, z, side="right")) / (len(tstar) + 1)


def critical(tstar) -> float:
    """A pair is significant when its z is below this: the largest m with (1 + m) / (R + 1) < ALPHA."""
    return float(tstar[math.ceil(ALPHA * (len(tstar) + 1) - 1) - 1])


def classify(Z: np.ndarray, Uz: np.ndarray, cal: dict) -> dict:
    """Set-level flags from a standardised residual matrix Z (ordered pairs) and Uz (unordered).

    significant  scanned (i, j) with max-T adjusted p < ALPHA: fewer counterexamples to i -> j than
                 the 2PL implies.
    asymmetric   significant, and the reverse (j, i) is NOT a deficit (z_ji > -Z_ASYM).
    isolated     significant, and no third skill k has an unordered discordance deficit with both i
                 and j of at least ISO_FRAC of the pair's own (Uz_ik, Uz_jk <= min(-Z_ASYM,
                 ISO_FRAC * Uz_ij)): a pair, not an edge of a cluster. Relative, because refitting a
                 planted matrix leaves small deficits around the plant that are not a cluster.
    clustered    significant and not isolated.
    """
    p = adj_p(np.where(cal["scan"], Z, np.inf), cal["tstar"])
    sig = cal["scan"] & (p < ALPHA)
    out = dict(any=False, asymmetric=False, isolated=False, clustered=False, pairs=[])
    for i, j in zip(*np.nonzero(sig)):
        asym = bool(Z[j, i] > -Z_ASYM)
        ld = (Uz <= min(-Z_ASYM, ISO_FRAC * Uz[i, j])) & OFF
        iso = not bool(np.any(ld[i] & ld[j]))
        out["any"] = True
        out["asymmetric"] |= asym
        out["isolated"] |= iso
        out["clustered"] |= not iso
        out["pairs"].append((int(i), int(j), float(Z[i, j]), float(Z[j, i]), float(p[i, j]), asym, iso))
    out["pairs"].sort(key=lambda t: t[2])
    return out


def standardise(X: np.ndarray, cal: dict, init=None):
    th, _, ok = fit_2pl(X, init=init)
    z, zu = residuals(X, th)
    return (z - cal["mu"]) / cal["sd"], (zu - cal["mu_u"]) / cal["sd_u"], ok


def score(X: np.ndarray, cal: dict) -> dict:
    """The observed statistic: minimum standardised pair residual, its max-T p, the flags, BH pairs."""
    z, zu = residuals(X, cal["th"])
    Z, Uz = (z - cal["mu"]) / cal["sd"], (zu - cal["mu_u"]) / cal["sd_u"]
    t = float(np.where(cal["scan"], Z, np.inf).min())
    flags = classify(Z, Uz, cal)
    # secondary: BH-FDR over scanned pairs on one-sided normal p of the bootstrap-standardised z
    zi = Z[cal["scan"]]
    pn = 0.5 * np.vectorize(math.erfc)(-zi / math.sqrt(2))
    order = np.argsort(pn)
    k = np.nonzero(pn[order] <= FDR * np.arange(1, len(pn) + 1) / len(pn))[0]
    bh = int(k[-1] + 1) if len(k) else 0
    idx = np.argwhere(cal["scan"])[order[:bh]]
    return dict(t=t, p=float(adj_p(np.array([t]), cal["tstar"])[0]), flags=flags,
                bh_pairs=[(int(i), int(j)) for i, j in idx], scanned=int(cal["scan"].sum()))


def fires(flags: dict) -> bool:
    return flags[CRITERION]


# ----------------------------------------------------------------------------- jobs

def seed_for(*key) -> np.random.SeedSequence:
    return np.random.SeedSequence([SEED, *key])


def calibrate_job(args):
    X, seed, draws = args
    t0 = time.time()
    cal = calibrate(X, seed, draws)
    cal["seconds"] = time.time() - t0
    return cal


def plants_job(args):
    """Every plant into one set's matrix, scored against that set's calibration."""
    X, cal, key = args
    out = []
    for k, (kind, reps) in enumerate((("pair", N_PAIR), ("gate", N_GATE), ("chain", N_CHAIN))):
        for rep in range(reps):
            rng = np.random.default_rng(seed_for(*key, 10 + k, rep))
            Y, edges, aligned = dense.plant(X, kind, rng)
            Z, Uz, ok = standardise(Y, cal, init=cal["th"])
            fl = classify(Z, Uz, cal)
            hit = {(i, j): (asym, iso) for i, j, _, _, _, asym, iso in fl["pairs"]}
            rev = {(j, i) for i, j in hit}
            e = sorted(edges)
            out.append(dict(
                kind=kind, aligned=aligned, flips=int((X != Y).sum()), converged=ok, edges=e,
                sig=any(x in hit for x in e), asymmetric=any(hit.get(x, (0, 0))[0] for x in e),
                isolated=any(hit.get(x, (0, 0))[1] for x in e),
                reversed_sig=any(x in rev for x in e) and not any(x in hit for x in e),
                z=[float(Z[i, j]) for i, j in e], z_rev=[float(Z[j, i]) for i, j in e],
                sig_edges=[x for x in e if x in hit],
                sig_rev_edges=[(j, i) for i, j in e if (j, i) in hit],
                set_fires=fires(fl)))
    return out


def fp_job(args):
    """Simulate from the set's fitted model (no dependency by construction) FP_REPS times and run the
    whole per-set pipeline on each: its own fit, its own R-draw calibration, its own score."""
    cal, seed, draws = args
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(FP_REPS):
        Xs = simulate(cal["th"], cal["n"], rng)
        c2 = calibrate(Xs, rng, draws)
        s = score(Xs, c2)
        out.append({k: s["flags"][k] for k in ("any", "asymmetric", "isolated", "clustered")})
    return out


def own_null_job(args):
    """Validation of the shared calibration: one PAIR plant scored against its OWN R-draw calibration."""
    X, cal, key, draws = args
    rng = np.random.default_rng(seed_for(*key))
    Y, edges, _ = dense.plant(X, "pair", rng)
    Z, Uz, _ = standardise(Y, cal, init=cal["th"])
    shared = classify(Z, Uz, cal)
    own_cal = calibrate(Y, rng, draws)
    Zo, Uo, _ = standardise(Y, own_cal, init=own_cal["th"])
    own = classify(Zo, Uo, own_cal)
    e = sorted(edges)[0]
    pick = {n: {(i, j): (a, iso) for i, j, _, _, _, a, iso in f["pairs"]}
            for n, f in (("s", shared), ("o", own))}
    crit = 0 if CRITERION == "asymmetric" else 1
    return dict(shared_sig=e in pick["s"], own_sig=e in pick["o"],
                shared_hit=bool(pick["s"].get(e, (False, False))[crit]),
                own_hit=bool(pick["o"].get(e, (False, False))[crit]),
                shared_c=critical(cal["tstar"]), own_c=critical(own_cal["tstar"]))


# ----------------------------------------------------------------------------- one corpus

def analyse(name: str, cid: int, sets: list[dict], pool: Pool, log, checkpoint, draws: int = R) -> dict:
    """Phases in the pre-registered order: fit + calibrate -> floor -> fitted-model false positives
    (both written) -> observed statistic -> verdict."""
    t0 = time.time()
    full = [s for s in sets if s["X"].shape[1] == K]
    short = len(sets) - len(full)
    log(f"\n{'=' * 78}\n{name}: {len(sets)} sets built, {len(full)} of {K} skills, {short} short")
    if not full:
        return dict(corpus=name, sets_built=len(sets), short=short, verdict="UNANSWERABLE",
                    reason="no set of K skills")

    # 1. fit and calibrate every set; nothing reads a set's own residuals yet
    cals = pool.map(calibrate_job, [(s["X"], seed_for(cid, i, 1), draws) for i, s in enumerate(full)],
                    chunksize=1)
    rows = []
    for i, (s, cal) in enumerate(zip(full, cals)):
        rows.append(dict(set=i, skills=s["skills"], learners=cal["n"], mastery_rate=float(s["X"].mean()),
                         fit_converged=cal["converged"], fit_iters=cal["iters"],
                         a=[round(float(v), 3) for v in cal["a"]],
                         b=[round(float(-cv / av), 3) for av, cv in zip(cal["a"], cal["c"])],
                         g=round(cal["g"], 4), l=round(cal["l"], 4),
                         a_at_bound=int(np.sum((cal["a"] <= A_MIN) | (cal["a"] >= A_MAX))),
                         boot_nonconverged=cal["boot_nonconverged"], scanned=int(cal["scan"].sum()),
                         critical_z=critical(cal["tstar"]),
                         boot_rates=cal["boot_rates"], calibrate_seconds=round(cal["seconds"], 1)))
    ok = [r["set"] for r in rows if r["fit_converged"]]
    log(f"fit: {len(ok)} of {len(rows)} converged; median critical z "
        f"{np.median([r['critical_z'] for r in rows]):.2f}; scanned pairs median "
        f"{np.median([r['scanned'] for r in rows]):.0f} of {K * (K - 1)}; a at bound "
        f"{sum(r['a_at_bound'] for r in rows)}")

    # 2. detection floor on each scored set's own matrix
    t1 = time.time()
    res = pool.map(plants_job, [(full[i]["X"], cals[i], (cid, i)) for i in ok], chunksize=1)
    floor = {}
    for kind in ("pair", "gate", "chain"):
        per = [[o for o in outs if o["kind"] == kind] for outs in res]
        allk = [o for p in per for o in p]
        floor[kind] = dict(
            median_rate=float(np.median([np.mean([o[CRITERION] for o in p]) for p in per])) if per else 0.0,
            per_set_rates=[float(np.mean([o[CRITERION] for o in p])) for p in per],
            rate_sig=float(np.mean([o["sig"] for o in allk])) if allk else 0.0,
            rate_asymmetric=float(np.mean([o["asymmetric"] for o in allk])) if allk else 0.0,
            rate_isolated=float(np.mean([o["isolated"] for o in allk])) if allk else 0.0,
            rate_reversed_only=float(np.mean([o["reversed_sig"] for o in allk])) if allk else 0.0,
            median_z=float(np.median([min(o["z"]) for o in allk])) if allk else None,
            median_z_rev=float(np.median([min(o["z_rev"]) for o in allk])) if allk else None,
            median_flips=float(np.median([o["flips"] for o in allk])) if allk else 0.0)
    floor_pass = floor["pair"]["median_rate"] >= FLOOR_RATE
    # IITA's convention: (i, j) reads "i is the prerequisite of j". Each planted arrow is scored as a
    # significant deficit claimed (i, j) and reversed (j, i); arrows are keyed by plant.
    planted = [o for outs in res for o in outs if o["kind"] in ("pair", "gate")]
    found = [set(map(tuple, o["sig_edges"])) | set(map(tuple, o["sig_rev_edges"])) for o in planted]
    arrows = {((q, a), (q, b)) for q, o in enumerate(planted) for a, b in o["edges"]}
    direction = reversed_arrow(lambda E: sum((a, b) in found[q] for (q, a), (_, b) in E), arrows)
    scale = check_control_scale({"pair": floor["pair"]["median_flips"],
                                 "gate": floor["gate"]["median_flips"],
                                 "null": float(np.median([cals[i]["hamming"] for i in ok]))}, ["null"])
    log(f"floor ({time.time() - t1:.0f}s):")
    for kind in ("pair", "gate", "chain"):
        f = floor[kind]
        log(f"  {kind:<5} median per-set {CRITERION} {f['median_rate']:.2f}  sig {f['rate_sig']:.2f} "
            f"asym {f['rate_asymmetric']:.2f} isolated {f['rate_isolated']:.2f} reversed-only "
            f"{f['rate_reversed_only']:.2f}  median z {f['median_z']:+.1f} (reverse {f['median_z_rev']:+.1f})")
    log(f"  floor {'PASSES' if floor_pass else 'FAILS'}; direction {direction['verdict']} "
        f"(claimed {direction['claimed']:.0f}, reversed {direction['reversed']:.0f})\n  {scale['report']}")

    # 3. false-positive check on data simulated from each set's fitted 2PL
    t2 = time.time()
    fp = [f for fs in pool.map(fp_job, [(cals[i], seed_for(cid, i, 3), draws) for i in ok], chunksize=1)
          for f in fs]
    fp_rates = {k: float(np.mean([f[k] for f in fp])) if fp else 0.0
                for k in ("any", "asymmetric", "isolated", "clustered")}
    fp_rate = fp_rates[CRITERION]
    log(f"fitted-model false positives ({time.time() - t2:.0f}s): " +
        ", ".join(f"{k} {v:.2f}" for k, v in fp_rates.items()) + f"  (verdict-bearing: {CRITERION})")
    block = dict(floor=floor, floor_pass=floor_pass, direction=direction, control_scale=scale["report"],
                 fitted_model_fp=fp_rates, fitted_model_fp_per_set=fp)
    checkpoint(dict(corpus=name, sets_built=len(sets), short=short, sets=rows, **block, verdict=None,
                    reason="floor and false-positive check written; observed statistic not yet computed"))

    # 4. the observed statistic, read only now
    for r in rows:
        if not r["fit_converged"]:
            continue
        s = score(full[r["set"]]["X"], cals[r["set"]])
        sk = full[r["set"]]["skills"]
        r.update(t_obs=s["t"], p_maxT=s["p"], scanned=s["scanned"],
                 **{f"fires_{k}": s["flags"][k] for k in ("any", "asymmetric", "isolated", "clustered")},
                 pairs=[dict(prereq=sk[i], dependant=sk[j], z=round(z, 2), z_reverse=round(zr, 2),
                             p_adj=round(p, 4), asymmetric=a, isolated=iso)
                        for i, j, z, zr, p, a, iso in s["flags"]["pairs"][:20]],
                 bh_pairs=len(s["bh_pairs"]))
    scored = [r for r in rows if r["fit_converged"]]
    n = len(scored)
    k = sum(r[f"fires_{CRITERION}"] for r in scored)
    p0 = max(CHANCE_MIN, fp_rate)
    p = dense.binom_sf(k, n, p0) if n else 1.0
    k_sym = sum(r["fires_clustered"] for r in scored)
    k_any = sum(r["fires_any"] for r in scored)
    k_asym = sum(r["fires_asymmetric"] for r in scored)
    if not floor_pass:
        verdict, reason = "UNANSWERABLE", "floor fails"
    elif fp_rate > FP_MAX:
        verdict, reason = "UNANSWERABLE", f"fitted-model false-positive rate {fp_rate:.2f} > {FP_MAX}"
    elif n < MIN_SCORED:
        verdict, reason = "UNANSWERABLE", f"fewer than {MIN_SCORED} scored sets"
    elif p < 0.05:
        verdict, reason = POSITIVE, ""
    else:
        verdict, reason = "NO DEPENDENCE DETECTED", ""
    log(f"observed: {k} of {n} sets fire ({CRITERION}); any {k_any}, clustered {k_sym}; binomial p = "
        f"{p:.3g} at p0 = {p0:.3f}")
    log(f"VERDICT {name}: {verdict}{' (' + reason + ')' if reason else ''}")
    return dict(corpus=name, sets_built=len(sets), short=short, sets=rows, scored=n, **block, _cals=cals,
                fires=k, fires_any=k_any, fires_clustered=k_sym, fires_asymmetric=k_asym,
                chance_rate=p0, binomial_p=p,
                verdict=verdict, reason=reason, seconds=time.time() - t0,
                seconds_per_set=(time.time() - t0) / len(full))


# ----------------------------------------------------------------------------- inputs

def synthetic_sets(world: str, n_sets: int, seed: int) -> tuple[list[dict], list]:
    """15 skills, 200-3000 learners (set 0 at 3000). Returns sets and the planted truth per set."""
    rng = np.random.default_rng(seed)
    out, truth = [], []
    for s in range(n_sets):
        n = 3000 if s == 0 else int(round(math.exp(rng.uniform(math.log(200), math.log(3000)))))
        a = rng.uniform(0.5, 2.5, K)
        d = rng.uniform(-2.0, 0.5, K)
        theta = rng.normal(size=(n, 1))
        t = []
        if world in ("two-factor", "doublet"):
            rho = rng.uniform(0.3, 0.8)
            t2 = rho * theta + math.sqrt(1 - rho ** 2) * rng.normal(size=(n, 1))
            th = np.where(np.arange(K) < (10 if world == "two-factor" else K - 2), theta, t2)
            X = rng.random((n, K)) < 1 / (1 + np.exp(-a * (th - d)))
            t = [("rho", round(rho, 2))]
        elif world == "guessing":
            g = rng.uniform(0.1, 0.3, K)
            X = rng.random((n, K)) < g + (1 - g) / (1 + np.exp(-a * (theta - d)))
        else:
            X = rng.random((n, K)) < 1 / (1 + np.exp(-a * (theta - d)))
            if world == "prerequisite":
                X, e1, _ = dense.plant(X, "pair", rng)
                X, e2, _ = dense.plant(X, "gate", rng)
                t = [sorted(e1), sorted(e2)]
            if world == "misclassified":
                X ^= rng.random(X.shape) < 0.05
        out.append(dict(skills=[f"s{j:02d}" for j in range(K)], X=X))
        truth.append(t)
    return out, truth


def recovery(seed: int) -> list[dict]:
    """Parameter recovery of fit_2pl on data simulated from known parameters: plain 2PL (g = l = 0)
    and 2PL with 5% misclassification each way (g = l = 0.05)."""
    rng = np.random.default_rng(seed)
    rows = []
    for g0 in (0.0, 0.05):
        for n in (200, 1000, 3000):
            ea, eb, eg, conv, t = [], [], [], 0, 0.0
            for _ in range(20):
                a, d = rng.uniform(0.5, 2.5, K), rng.uniform(-2.0, 0.5, K)
                X = simulate((a, -a * d, g0, g0), n, rng)
                t0 = time.time()
                (ah, ch, gh, lh), _, ok = fit_2pl(X)
                t += time.time() - t0
                conv += ok
                ea += list(ah - a)
                eb += list(-ch / ah - d)
                eg += [gh - g0, lh - g0]
            rows.append(dict(n=n, g=g0, l=g0, reps=20, rmse_a=float(np.sqrt(np.mean(np.square(ea)))),
                             bias_a=float(np.mean(ea)), rmse_b=float(np.sqrt(np.mean(np.square(eb)))),
                             bias_b=float(np.mean(eb)), rmse_gl=float(np.sqrt(np.mean(np.square(eg)))),
                             bias_gl=float(np.mean(eg)), converged=conv, seconds_per_fit=t / 20))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true", help="run the pipeline on synthetic worlds")
    ap.add_argument("--synthetic-sets", type=int, default=20)
    ap.add_argument("--worlds", default="2pl,prerequisite,two-factor,guessing,misclassified,doublet")
    ap.add_argument("--validate-sets", type=int, default=3, help="synthetic: sets checked for own-null")
    ap.add_argument("--corpus", choices=("both", "xes3g5m", "assist12"), default="both")
    ap.add_argument("--workers", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--draws", type=int, default=R)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    def log(s=""):
        print(s, flush=True)

    results, extra = [], {}
    with Pool(args.workers) as pool:
        if args.synthetic:
            out = args.out or HERE / "out" / "iita-pairscan-synthetic.json"
            rec = recovery(SEED)
            extra["recovery"] = rec
            for r in rec:
                log(f"recovery g=l={r['g']} n={r['n']}: rmse a {r['rmse_a']:.3f} (bias {r['bias_a']:+.3f}), rmse b "
                    f"{r['rmse_b']:.3f} (bias {r['bias_b']:+.3f}), g/l rmse {r['rmse_gl']:.3f} (bias "
                    f"{r['bias_gl']:+.3f}), {r['converged']}/20 converged, "
                    f"{r['seconds_per_fit']:.3f}s a fit")
            worlds = args.worlds.split(",")
            corpora = [(f"synthetic-{w}", w, i) for i, w in enumerate(worlds)]
        else:
            names = ("xes3g5m", "assist12") if args.corpus == "both" else (args.corpus,)
            out = args.out or HERE / "out" / ("iita-pairscan.json" if args.corpus == "both"
                                             else f"iita-pairscan-{args.corpus}.json")
            corpora = [(nm, None, i) for i, nm in enumerate(names)]

        def checkpoint(partial):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(dict(partial=True, corpora=results + [partial]), indent=1,
                                      default=str) + "\n")

        for name, world, cid in corpora:
            if world is None:
                sets, truth = dense.real_sets(name), None
            else:
                sets, truth = synthetic_sets(world, args.synthetic_sets, SEED + 100 + cid)
            res = analyse(name, cid, sets, pool, log, checkpoint, args.draws)
            if truth is not None:
                res["world"] = world
                if world == "prerequisite":
                    res["truth_found"] = truth_found(res, truth)
                    log(f"planted truth: {res['truth_found']}")
                if world == "2pl" and args.validate_sets:
                    res["own_null_validation"] = validate(sets, cid, res["_cals"], pool, args.draws,
                                                          args.validate_sets)
                    log(f"own-null validation: {res['own_null_validation']['summary']}")
            res.pop("_cals", None)
            results.append(res)

    if args.synthetic:
        for r in results:
            for s in r.get("sets", []):
                s.pop("pairs", None)
    table = [dict(corpus=r["corpus"], verdict=r["verdict"], reason=r.get("reason"), scored=r.get("scored"),
                  fires=r.get("fires"), fires_any=r.get("fires_any"),
                  fires_clustered=r.get("fires_clustered"), fires_asymmetric=r.get("fires_asymmetric"),
                  binomial_p=r.get("binomial_p"),
                  fp=r.get("fitted_model_fp"),
                  floor_pair=r.get("floor", {}).get("pair", {}).get("median_rate"),
                  floor_gate=r.get("floor", {}).get("gate", {}).get("median_rate"),
                  floor_chain=r.get("floor", {}).get("chain", {}).get("median_rate"),
                  seconds_per_set=r.get("seconds_per_set")) for r in results]
    log(f"\n{'corpus':<28} {'verdict':<46} {'fire':>4} {'any':>4} {'clus':>4} {'fp':>5} {'pair':>5} "
        f"{'gate':>5} {'chain':>5} {'s/set':>6}")
    for t in table:
        log(f"{t['corpus']:<28} {str(t['verdict']):<46} {t['fires'] or 0:>4} {t['fires_any'] or 0:>4} "
            f"{t['fires_clustered'] or 0:>4} {(t['fp'] or {}).get(CRITERION, 0):>5.2f} "
            f"{t['floor_pair'] or 0:>5.2f} {t['floor_gate'] or 0:>5.2f} {t['floor_chain'] or 0:>5.2f} "
            f"{t['seconds_per_set'] or 0:>6.1f}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(synthetic=args.synthetic, seed=SEED, k=K, draws=args.draws,
                                   criterion=CRITERION, placements=dict(pair=N_PAIR, gate=N_GATE,
                                                                        chain=N_CHAIN),
                                   strength=dense.STRENGTH, workers=args.workers, programme=table,
                                   **extra, corpora=results), indent=1, default=str) + "\n")
    log(f"wrote {out}")


def truth_found(res: dict, truth: list) -> dict:
    """World `prerequisite`: were the latent planted arrows found on the observed matrices, and how?"""
    out = dict(sets=0, pair_sig=0, pair_asym=0, gate_sig=0, gate_asym=0, sets_with_unplanted_sig=0)
    for r, t in zip(res["sets"], truth):
        if "pairs" not in r:
            continue
        out["sets"] += 1
        hit = {(int(p["prereq"][1:]), int(p["dependant"][1:])): p["asymmetric"] for p in r["pairs"]}
        pair, gate = map(lambda e: [tuple(x) for x in e], t)
        out["pair_sig"] += any(e in hit for e in pair)
        out["pair_asym"] += any(hit.get(e, False) for e in pair)
        out["gate_sig"] += any(e in hit for e in gate)
        out["gate_asym"] += any(hit.get(e, False) for e in gate)
        planted = {frozenset(e) for e in pair + gate}
        out["sets_with_unplanted_sig"] += any(frozenset(e) not in planted for e in hit)
    return out


def validate(sets, cid, cals, pool, draws: int, n_sets: int, per_set: int = 5) -> dict:
    """Does scoring a plant against the unplanted set's calibration (the floor's shortcut) decide as
    its own calibration would? PAIR plants on the first `n_sets` sets, each with its own R draws."""
    jobs = [(sets[i]["X"], cals[i], (cid, i, 50, rep), draws) for i in range(min(n_sets, len(sets)))
            for rep in range(per_set)]
    res = pool.map(own_null_job, jobs, chunksize=1)
    agree = float(np.mean([o["shared_hit"] == o["own_hit"] for o in res]))
    summary = (f"{len(res)} PAIR plants: {CRITERION} detection shared {sum(o['shared_hit'] for o in res)}"
               f" / own {sum(o['own_hit'] for o in res)}, agreement {agree:.2f}; significant shared "
               f"{sum(o['shared_sig'] for o in res)} / own {sum(o['own_sig'] for o in res)}; critical z shared "
               f"{np.median([o['shared_c'] for o in res]):.2f} / own {np.median([o['own_c'] for o in res]):.2f}")
    return dict(summary=summary, agreement=agree, plants=res)


if __name__ == "__main__":
    main()
