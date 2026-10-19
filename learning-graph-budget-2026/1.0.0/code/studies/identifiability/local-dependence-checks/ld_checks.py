"""PRE-REGISTERED: does Paper II's F6 pair-level result depend on its statistic, and is it a unit-level factor?

Paper II's F6 rests on two committed studies in studies/identifiability/learning-structure/:
IITA-PAIRSCAN (iita_pairscan.py, out/iita-pairscan.json): on XES3G5M, 8 of 15 fifteen-skill sets carry
an ISOLATED significant pair (pairwise local dependence beyond one trait: a 2PL with common asymptotes,
refitted parametric bootstrap, a counterexample-deficit statistic, max-T within set), 12 unordered
pairs; ASSISTments 2012 UNANSWERABLE (2 sets, floor fails). PAIRSCAN-CURRICULUM (pairscan_curriculum.py,
out/pairscan-curriculum.json): the 12 pairs are concentrated in taxonomy-adjacent skills (R1 3 of 12
adjacent against 0.024 expected; R3 mean distance rank 0.201 against 0.499). The literature review
(research/readiness/learning-graph-budget-2026/literature.md, rank 6 of "Analyses and controls it
suggests"; strand 1 entry 1.11 and its "Analyses" item 3; strand 6 entries 6.1-6.10 and its items 2 and
4) asks two things of that result, and this study answers both:

(a) STATISTIC. The scan's statistic is not a standard local-dependence (LD) index (6.2). Do Chen and
    Thissen's (1997) G2 and Yen's (1984) Q3, mean-centred as Christensen, Makransky and Horton (2017)
    advise, under the SAME refitted parametric bootstrap, flag the same pairs and fire in the same sets?
(b) UNIT OR PAIR. A bifactor/testlet model (Bradlow, Wainer and Wang 1999; Reise 2012; entry 6.10) with
    a group factor per taxonomy parent absorbs dependence shared by a curriculum unit. If the flagged
    pairs and the adjacency concentration vanish once parent factors are in, the signal is a unit-level
    (shared sub-skill or topic) factor; if they survive, it is pair-specific beyond the unit. Ip (2010,
    entry 6.5) and the Ising-IRT equivalence (6.6) say a factor on exactly two skills and a pair link are
    the same model; the design below therefore never gives a two-skill group its own factor, and says
    which pairs that leaves untestable.

READS A CORPUS. XES3G5M (attempts.tsv and cid2route.json under $XES_DIR) and ASSISTments 2012-13
(assist_slim.csv under $ASSIST_DIR), both through shared.paths.data_path, via iita_dense.real_sets
(surmise_graphs' loaders and mastery table, imported, not copied) and pairscan_curriculum.load_routes
(md5-checked). Reads out/iita-pairscan.json of learning-structure (sha256-checked against the committed
file) for the sets' skill ids and the committed flags. Raw exports stay in the scratchpad; only per-set
aggregates (skill ids, counts, rates, flags, no z matrices, no item text) are written. No derived corpus file is
written. --synthetic reads no learner response (it reads the committed skill-id lists and cid2route.json
to take each real set's label-blind module partition).

SEEN BEFORE THIS WAS WRITTEN (not chosen from): the two committed results above, including per-set
flagged counts (2, 1, 3, 0, 1, 0, 0, 1, 2, 0, 1, 0, 1, 0, 0), the scan's floor (PAIR 1.00) and
fitted-model false positives (0.00), and the curriculum study's R1/R3 numbers. Label-blind taxonomy
structure of the 15 sets (from the committed skill ids and cid2route.json, no response read): route
depths 2-7; the IMMEDIATE parent (route[:-1]) groups are almost all singletons and doublets (largest
group 2-3 skills a set); the depth-3 prefix (topic) groups are 1-4 skills, mostly 1-2; the depth-2
prefix (scheme root + module, e.g. 拓展思维/计算模块) groups are 2-5 skills, sizes per set
[4,3,3,2,1,1,1] [5,4,4,1,1] [5,4,2,2,1,1] [4,3,2,2,2,1,1] [4,3,2,2,1,1,1,1] [3,2,2,2,2,2,1,1]
[4,3,2,2,1,1,1,1] [4,3,2,2,2,1,1] [5,2,2,2,1,1,1,1] [3,3,3,2,2,1,1] [4,3,2,2,1,1,1,1] [5,2,2,1,1,1,1,1,1]
[4,2,2,2,2,1,1,1] [2,2,2,2,1,1,1,1,1,1,1] [4,4,4,1,1,1] (compound skills counted by first component
there; the rule below is stricter). Which committed pairs fall in which group was NOT computed. Code
was smoke-tested on synthetic data only (2-3 sets, 30-100 draws) before this commit.

SETS          The 15 XES3G5M and 2 ASSISTments fifteen-skill sets of iita_pairscan, rebuilt by
              iita_dense.real_sets and checked equal (skill ids and learner counts) to the committed ones.
              (b) runs on XES3G5M only: ASSISTments 2012 has no skill taxonomy in this repository, and
              its 2 sets are below every corpus rule's 5-set minimum.
GRAIN         The unordered skill pair within a set, the grain of the committed 12 pairs.

---------------------------------------------------------------------------------------- (a) LD indexes
MODEL         iita_pairscan's model and fit, imported: P(mastered j | theta) = g + (1-g-l) logistic(a_j theta
              + c_j), theta ~ N(0,1), marginal ML by L-BFGS-B on 31 Gauss-Hermite nodes.
NULL          The SAME bootstrap: calibrate_a replays iita_pairscan.calibrate draw for draw (same seeds
              ps.seed_for(cid, set, 1), R = 500, each draw refitted warm), and computes the indexes on
              every refitted draw beside the scan's residuals. So the scan's own calibration is
              reproduced exactly; that is checked (scanned counts, critical z, fitted a) and reported,
              and the scan's flags are recomputed and compared with the committed ones.
INDEXES       G2 (Chen-Thissen): 2 sum O ln(O/E) over the pair's 2x2 table, E from the fitted model's
              bivariate probabilities (quadrature). X2 = sum (O-E)^2/E, reported only. Signed by
              sign(log OR observed - log OR expected) (observed OR with +0.5 per cell); carried as
              sign x sqrt(index). Q3* : Yen's residual correlation, residual = x - P(theta_EAP), EAP
              under the fitted model, minus the set's mean Q3 over its 105 pairs (Christensen et al.).
              All three are standardised per pair against their own bootstrap moments,
              z = (s - mean*)/sd*, exactly as the scan standardises its residual.
SIGN          Positive LD only (upper tail of z): more concordance than one trait implies, the same
              direction as the scan's counterexample deficit. Negative LD is never read as dependence.
SET TEST      Max-T within set (Westfall-Young single step) over the pairs the scan scans (an unordered
              pair is scanned if either orientation is); significant at adjusted p < 0.025; ISOLATED by
              the scan's rule on the index's own z (no third skill k with z_ik, z_jk >= max(1.645,
              0.4 z_ij)). FLAGGED = significant and isolated. A set FIRES if it has a flagged pair.
FLOOR         iita_pairscan's plants with its seeds (same 15 PAIR and 15 GATE placements a set, strength
              0.9), refitted warm, scored against the unplanted calibration; DETECTED if the planted pair
              is FLAGGED by the index. Floor passes at median per-set PAIR detection >= 0.8.
FALSE POS.    iita_pairscan.fp_job replayed (same seeds): 2 simulations a set from the fitted 2PL, each
              with its own R = 500 calibration; rate of FIRES per index. UNANSWERABLE above 0.10.
CORPUS RULE   Per index, iita_pairscan's: UNANSWERABLE (floor < 0.8, false-positive rate > 0.10, or < 5
              sets); else PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT if one-sided binomial
              P(X >= sets firing | 15, max(0.05, false-positive rate)) < 0.05; else NO DEPENDENCE DETECTED.
REPORTED      Per set and pooled: pairs each index flags; overlap with the committed 12 (count and
              Jaccard, per set and pooled = sum |A & B| / sum |A | B|, with a 95% percentile interval
              resampling the 15 SETS, 2000 draws); per-set verdict agreement with the committed scan
              (share of sets, Cohen's kappa); R1 adjacency of each index's flagged pairs (within-set
              permutation, one-sided upper, 10,000 draws; the curriculum study's unstratified test, not
              its difficulty x co-attempt control). ASSISTments: the same, descriptive (2 sets).
READING (a)   fixed now, from the G2 and Q3 corpus verdicts on XES3G5M (X2 is not verdict-bearing):
                STATISTIC-ROBUST     both PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT: the 8-of-15
                                     result does not rest on the scan's statistic. The pair-level
                                     overlap is reported beside it and says whether the SAME pairs are
                                     found (a low Jaccard with both positive means the set-level claim
                                     is robust and the pair list is not).
                STATISTIC-DEPENDENT  either returns NO DEPENDENCE DETECTED with its floor passing: F6's
                                     set-level claim depends on the statistic and must say so.
                PARTLY ANSWERABLE    otherwise (an index UNANSWERABLE, none negative).

---------------------------------------------------------------------------------------- (b) bifactor
PARENT LEVEL  The depth-2 route prefix, route[:2] = (scheme root, module), e.g. one of the 拓展思维
              modules; the nine roots are parallel schemes, so the same module name under two roots is
              two parents. Chosen over the immediate parent and the depth-3 topic, label-blind, because
              those levels are almost all one- and two-skill groups in these sets (SEEN above), and a
              group factor on two skills is the pair dependence itself (Ip 2010): fitting one would make
              "vanishing" true by construction. A compound skill 'a_b' takes a parent only if every
              component has the same one; otherwise it has no group.
FACTORS       A parent group with >= 3 of the set's skills gets one group factor; groups of 1-2 skills
              get none. Committed pairs are classed WITHIN (both skills in one factor group: the testable
              case), DOUBLET (same parent, a two-skill group: untestable here, reported) and CROSS (no
              shared parent: group factors cannot absorb them by construction; their survival measures
              re-estimation churn and is the control for WITHIN).
MODEL         Constrained bifactor 2PL with the scan's common asymptotes, one loading per group:
              P(x_j | G, S) = g + (1-g-l) logistic(a_j G + lam_s(j) S_s(j) + c_j), G, S_s iid N(0,1),
              lam in [0, 4]. One parameter per unit is what a unit-level factor means; free per-skill
              group loadings are only just identified in a 3-skill binary group and poorly determined at
              200-3000 learners; the group-free world below measures what the constraint costs.
ESTIMATION    LIMITED INFORMATION, said plainly: pairwise (composite) likelihood over the 105 2x2 tables
              (sum over pairs of sum_cells O log pi), with an analytic gradient, L-BFGS-B, iita_pairscan's
              tolerances; 21 x 15 Gauss-Hermite nodes (general x group). Full-information bifactor MML
              with 500 refitted draws a set was too slow for the shared machine. Because estimation
              differs from the committed scan's, the comparison arm is the SAME code with no group
              factors (1D-PL): the effect of the parent factors is BF-PL against 1D-PL on the same sets,
              estimator and statistic, and the committed flags are the population tested.
STATISTIC     The scan's, unchanged: counterexample residuals b_ij - n P(not i, j) under the fitted
              model, studentised by the fit, standardised by a refitted parametric bootstrap from that
              model (R = 500 on the real sets; draws simulate the full model, G and every S_s), max-T
              at 0.025, iita_pairscan.classify for isolation (imported).
FLOOR (b)     Plant pair-specific dependence inside a bifactor world and check it is still seen:
                real sets  8 WITHIN-group and 7 CROSS placements a set (ordered pairs drawn at random;
                           fewer WITHIN if the groups hold fewer), iita_dense's 0.9 PAIR plant, refitted
                           warm, scored against the unplanted BF calibration; DETECTED if the planted
                           ordered pair is significant and isolated (iita_pairscan's criterion).
                synthetic  "group" world: 20 sets shaped like the real ones (15 skills, 200-3000
                           learners, a ~ U(0.5,2.5), difficulty ~ U(-2,0.5)), the real sets' module
                           partitions in turn, lam_s ~ U(0.5,1.5) on every >= 3 group, no pair
                           dependence; the same 8 + 7 plants. R = 200 draws (fewer than 500 to fit
                           the machine; the max-T level 0.025 needs only R >= 40).
              Floor passes if the median per-set detection is >= 0.8 for WITHIN and for CROSS, on the
              real sets AND in the synthetic group world.
FALSE ALARMS  Plant a group factor only and check the BF scan stays quiet: the synthetic group world's
              rate of sets FIRING under BF-PL must be <= 0.10. Reported beside it: the 1D-PL scan's
              firing in the same world (a group factor's signal the one-trait scan reads), and how many
              1D-PL flags there survive BF (the vanishing the design relies on, demonstrated where the
              truth is unit-level). Also on the real sets: 2 simulations a set from each fitted BF, own
              R = 200 calibration; rate of FIRES must be <= 0.10.
              "group-free" world (reported, gates only a PAIR-SPECIFIC verdict): the same, but every
              grouped skill gets its own group loading ~ U(0.3,1.5) (a free bifactor the fitted model only
              approximates). If its BF false-alarm rate exceeds 0.10, pairs surviving BF could be
              misfit of the one-loading constraint, and PAIR-SPECIFIC is downgraded to MIXED.
CONTROL SIZE  The plants change a median number of cells reported beside the null's
              (shared.controls' principle; the bootstrap null perturbs ~30x more cells, as in the scan).
POSITIVITY    (b) can speak only about WITHIN pairs: if no committed pair is WITHIN and kept by 1D-PL,
              the verdict is UNANSWERABLE (no testable pair), not "pair-specific".
ESTIMANDS (b) s_w = share of committed WITHIN pairs FLAGGED under 1D-PL that are still FLAGGED under
              BF-PL (Clopper-Pearson 95% interval over pairs; pairs are nested in sets, so the interval
              is descriptive); s_c, the same for CROSS pairs (the churn control); sets firing under
              BF-PL and the scan's corpus rule on them (chance rate max(0.05, BF fitted-model rate));
              R1 adjacency enrichment of all BF-PL flagged pairs and of all 1D-PL flagged pairs
              (within-set permutation of the flag among scanned pairs, count per set fixed, one-sided
              upper, 10,000 draws). Signed throughout: survival is a kept flag in the scan's deficit
              direction; enrichment is MORE adjacency, never less.
VERDICTS (b)  exactly one of, in this order:
                UNANSWERABLE       a floor fails (WITHIN or CROSS median < 0.8, real or synthetic), the
                                   group-world BF false-alarm rate > 0.10, the real BF fitted-model
                                   rate > 0.10, or no committed WITHIN pair is kept by 1D-PL.
                UNIT-LEVEL FACTOR  s_w <= 0.25 AND BF adjacency enrichment p >= 0.05: the within-module
                                   flags and the concentration vanish with parent factors in.
                PAIR-SPECIFIC      s_w >= 0.50 AND BF adjacency p < 0.05 AND the BF scan's corpus rule
                                   is still PAIRWISE (downgraded to MIXED if the group-free world's
                                   false-alarm rate > 0.10).
                MIXED              otherwise; the numbers are reported.
              CROSS and DOUBLET pairs never enter the verdict: the parent factors cannot absorb the first,
              and the second is the case Ip's theorem makes undecidable from responses.
FOR PAPER II  fixed now, F6 wording:
                (a) STATISTIC-ROBUST     "a pairwise scan, and the standard G2 and Q3 indexes under the same
                                         bootstrap, find ..." ; pair lists are cited only with the overlap.
                (a) STATISTIC-DEPENDENT  F6 names its statistic and reports the indexes that do not fire.
                (b) UNIT-LEVEL FACTOR    the adjacency result is unit-level dependence (a module factor),
                                         Yen's (1984) shared-content LD at skill grain, not pair links.
                (b) PAIR-SPECIFIC        within-module flagged pairs carry dependence a module factor does
                                         not absorb; still not orientable, still not edges, and a factor on
                                         exactly those two skills remains observationally equivalent.
                (b) MIXED / UNANSWERABLE F6 keeps its current wording and states that a unit factor was not
                                         excluded.
WHAT IT CANNOT SAY  Orientation (the 2x2 has one free cell at fitted margins); prerequisite versus a
              two-skill trait (Ip 2010); anything about pairs in two-skill groups; whether a different
              parent level would absorb CROSS pairs. Q3 and G2 are judged by the bootstrap null, not by
              their textbook cut-offs (Christensen et al.: no single cut-off is right).

ORDER         --synthetic (no response read) -> committed -> real: rebuild and check sets -> (a)
              calibrations, floor, fitted-model check written -> (b) calibrations, floor, fitted-model
              check written -> observed statistics -> verdicts.

CHANGES       (dated entries go here if a floor result forces a design change before real data is read)

    python3 ld_checks.py --synthetic --workers 3     # out/ld-checks-synthetic.json, no response read
    python3 ld_checks.py --workers 3                 # out/ld-checks.json; reads $XES_DIR, $ASSIST_DIR
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LS = ROOT / "studies" / "identifiability" / "learning-structure"
sys.path.insert(0, str(LS))
sys.path.insert(0, str(ROOT))
import iita_dense as dense  # noqa: E402  (set construction, plants, binomial tail)
import iita_pairscan as ps  # noqa: E402  (the 2PL, its bootstrap, the scan statistic and its flags)
from pairscan_curriculum import relate  # noqa: E402  (R1 adjacency, R3 distance)
from shared.paths import data_path  # noqa: E402

SEED = 20261007
K = ps.K
OFF = ps.OFF
UPPER = np.triu(np.ones((K, K), bool), 1)
R_REAL = 500                # draws per calibration on the real sets (as iita_pairscan)
R_SYN = 200                 # draws per calibration in the synthetic worlds and the BF fitted-model check
ALPHA = ps.ALPHA            # 0.025 max-T adjusted
Z_LEG = ps.Z_ASYM           # 1.645
ISO_FRAC = ps.ISO_FRAC      # 0.4
FLOOR_RATE = 0.8
FP_MAX = 0.10
FP_REPS = 2
MIN_SCORED = 5
CHANCE_MIN = 0.05
N_PERM = 10_000
MIN_GROUP = 3               # a parent group gets a factor only if it holds >= 3 of the set's skills
LEVEL = 2                   # parent = route[:2] (scheme root + module)
QG, QS = 21, 15             # quadrature nodes, general and group factor (pairwise likelihood)
LAM_MAX = 4.0
POSITIVE = "PAIRWISE LOCAL DEPENDENCE BEYOND ONE TRAIT"
INDEXES = ("pairscan", "g2", "x2", "q3")

PAIRSCAN_OUT = LS / "out" / "iita-pairscan.json"
PAIRSCAN_SHA256 = "8bcaa5cfb168651c53680fbf90c0248930e10876b8833e92ecce0d7153da139c"
ROUTES_MD5 = "f381243566f9da16c29ff237b0233557"

XG, WG = np.polynomial.hermite_e.hermegauss(QG)
WG = WG / WG.sum()
XS, WS = np.polynomial.hermite_e.hermegauss(QS)
WS = WS / WS.sum()


def seed_for(*key) -> np.random.SeedSequence:
    return np.random.SeedSequence([SEED, *key])


# ============================================================================ part (a): LD indexes

def bivariate(th):
    """Model P(x_i = 1, x_j = 1) (off-diagonal) and P(x_i = 1) (diagonal), by iita_pairscan's quadrature."""
    P = ps.prob(th, ps.GX)
    P11 = (P * ps.GW[:, None]).T @ P
    p = P.T @ ps.GW
    np.fill_diagonal(P11, p)
    return P11


def tables(X):
    Xi = X.astype(np.int64)
    n11 = (Xi.T @ Xi).astype(float)
    return n11


def cells(n11, n):
    n1 = np.diag(n11).copy()
    o11 = n11
    o10 = n1[:, None] - n11
    o01 = n1[None, :] - n11
    o00 = n - n1[:, None] - n1[None, :] + n11
    return o11, o10, o01, o00


def eap(X, th):
    """EAP ability per learner under the fitted model (iita_pairscan's 31 nodes)."""
    U, cnt = ps.compress(X)
    P = np.clip(ps.prob(th, ps.GX), 1e-12, 1 - 1e-12)
    ll = U @ np.log(P).T + (1 - U) @ np.log1p(-P).T + ps.LOGW
    ll -= ll.max(1, keepdims=True)
    post = np.exp(ll)
    post /= post.sum(1, keepdims=True)
    return U, cnt, post @ ps.GX


def ld_indexes(X, th):
    """Signed Chen-Thissen G2 and X2 (signed root, + = positive local dependence) and mean-centred Q3.

    G2 = 2 sum O ln(O / E), X2 = sum (O - E)^2 / E over the pair's 2x2 table, E = n x the fitted model's
    bivariate probabilities. Sign = sign(log odds ratio observed - log odds ratio expected), so a pair more
    concordant than the model says is positive. The statistic carried is sign x sqrt(index), near-normal
    under the null. Q3 = correlation over learners of x - P(theta_EAP); Q3* = Q3 minus the mean Q3 of the
    set's 105 pairs (Christensen et al. 2017).
    """
    n = len(X)
    O = cells(tables(X), n)
    P11 = bivariate(th)
    E = cells(n * P11, n)
    with np.errstate(divide="ignore", invalid="ignore"):
        g2 = 2 * sum(np.where(o > 0, o * np.log(o / np.maximum(e, 1e-12)), 0.0) for o, e in zip(O, E))
        x2 = sum((o - e) ** 2 / np.maximum(e, 1e-12) for o, e in zip(O, E))
        lor_o = np.log((O[0] + .5) * (O[3] + .5) / ((O[1] + .5) * (O[2] + .5)))
        lor_e = np.log(E[0] * E[3] / (E[1] * E[2]))
    sgn = np.sign(lor_o - lor_e)
    sg2 = sgn * np.sqrt(np.maximum(g2, 0))
    sx2 = sgn * np.sqrt(np.maximum(x2, 0))
    U, cnt, tq = eap(X, th)
    D = U - ps.prob(th, tq)                                   # pattern residuals
    w = cnt / cnt.sum()
    mu = w @ D
    C = (D - mu).T @ ((D - mu) * w[:, None])
    s = np.sqrt(np.diag(C))
    q3 = C / np.outer(s, s)
    q3c = q3 - q3[UPPER].mean()
    for M in (sg2, sx2, q3c):
        np.fill_diagonal(M, 0.0)
    return dict(g2=sg2, x2=sx2, q3=q3c)


def calibrate_a(X, seed, draws):
    """iita_pairscan.calibrate, draw for draw (same generator sequence, same fits), with the three LD
    indexes computed on every refitted draw beside the scan's residuals. The pairscan part of the
    returned calibration is the committed one exactly when `seed` is the committed seed."""
    rng = np.random.default_rng(seed)
    th, iters, ok = ps.fit_2pl(X)
    n = len(X)
    rs, ru = np.empty((draws, K, K)), np.empty((draws, K, K))
    ix = {k: np.empty((draws, K, K)) for k in ("g2", "x2", "q3")}
    bmean = np.zeros((K, K))
    fails = 0
    for r in range(draws):
        Xs = ps.simulate(th, n, rng)
        th2, _, ok2 = ps.fit_2pl(Xs, init=th)
        fails += not ok2
        bmean += ps.counterexamples(Xs) / draws
        rs[r], ru[r] = ps.residuals(Xs, th2)
        for k, v in ld_indexes(Xs, th2).items():
            ix[k][r] = v
    hamming = float(np.mean([(ps.simulate(th, n, rng) != X).sum() for _ in range(5)]))  # as ps.calibrate
    mu, sd = rs.mean(0), rs.std(0, ddof=1)
    mu_u, sd_u = ru.mean(0), ru.std(0, ddof=1)
    scan = OFF & (bmean >= ps.MIN_EXPECTED) & (sd > 0)
    sd, sd_u = np.where(sd > 0, sd, np.inf), np.where(sd_u > 0, sd_u, np.inf)
    cal = dict(th=th, hamming=hamming, iters=iters, converged=ok, n=n, mu=mu, sd=sd, mu_u=mu_u, sd_u=sd_u, scan=scan,
               boot_nonconverged=fails)
    Zs = (rs - mu) / sd
    cal["tstar"] = np.sort(np.where(scan, Zs, np.inf).reshape(draws, -1).min(1))
    uscan = (scan | scan.T) & UPPER
    cal["uscan"] = uscan
    for k, A in ix.items():
        m, s = A.mean(0), A.std(0, ddof=1)
        s = np.where(s > 0, s, np.inf)
        Z = (A - m) / s
        cal[k] = dict(mu=m, sd=s, tstar=np.sort(np.where(uscan, Z, -np.inf).reshape(draws, -1).max(1)))
    return cal


def classify_index(Z, ical, uscan):
    """Upper-tail max-T flags for a symmetric index z matrix. significant: adjusted p < ALPHA; isolated:
    no third skill k with z_ik and z_jk both >= max(Z_LEG, ISO_FRAC z_ij) (iita_pairscan's rule, signed
    for an index whose positive tail is dependence)."""
    tstar = ical["tstar"]
    R = len(tstar)
    Zm = np.where(uscan, Z, -np.inf)
    p = (1 + (R - np.searchsorted(tstar, Zm, side="left"))) / (R + 1)
    sig = uscan & (p < ALPHA)
    out = dict(any=False, isolated=False, clustered=False, pairs=[])
    for i, j in zip(*np.nonzero(sig)):
        ld = (Z >= max(Z_LEG, ISO_FRAC * Z[i, j])) & OFF
        iso = not bool(np.any(ld[i] & ld[j]))
        out["any"] = True
        out["isolated"] |= iso
        out["clustered"] |= not iso
        out["pairs"].append((int(i), int(j), float(Z[i, j]), float(p[i, j]), iso))
    out["pairs"].sort(key=lambda t: -t[2])
    return out


def standardise_index(ix, cal):
    return {k: (ix[k] - cal[k]["mu"]) / cal[k]["sd"] for k in ("g2", "x2", "q3")}


def score_all(X, cal, th=None):
    """Flags of all four statistics on matrix X against calibration cal. th: the fit to X (refit if None
    and X is not the calibrated matrix)."""
    if th is None:
        th = cal["th"]
    z, zu = ps.residuals(X, th)
    Z, Uz = (z - cal["mu"]) / cal["sd"], (zu - cal["mu_u"]) / cal["sd_u"]
    out = {"pairscan": ps.classify(Z, Uz, cal)}
    zi = standardise_index(ld_indexes(X, th), cal)
    for k in ("g2", "x2", "q3"):
        out[k] = classify_index(zi[k], cal[k], cal["uscan"])
    return out


def flagged_pairs(flags, kind):
    """Unordered pairs carrying an ISOLATED significant flag (the verdict-bearing unit)."""
    if kind == "pairscan":
        return {tuple(sorted((i, j))) for i, j, _, _, _, _, iso in flags["pairs"] if iso}
    return {(i, j) for i, j, _, _, iso in flags["pairs"] if iso}


def sig_pairs(flags, kind):
    if kind == "pairscan":
        return {tuple(sorted((i, j))) for i, j, *_ in flags["pairs"]}
    return {(i, j) for i, j, *_ in flags["pairs"]}


def a_calibrate_job(args):
    X, seed, draws = args
    t0 = time.time()
    cal = calibrate_a(X, seed, draws)
    cal["seconds"] = time.time() - t0
    return cal


def a_plants_job(args):
    """iita_pairscan's floor plants (same seeds, so the same placements), each statistic scored."""
    X, cal, key = args
    out = []
    for k, (kind, reps) in enumerate((("pair", ps.N_PAIR), ("gate", ps.N_GATE))):
        for rep in range(reps):
            rng = np.random.default_rng(ps.seed_for(*key, 10 + k, rep))
            Y, edges, _ = dense.plant(X, kind, rng)
            th, _, ok = ps.fit_2pl(Y, init=cal["th"])
            fl = score_all(Y, cal, th)
            row = dict(kind=kind, converged=ok)
            for ind in INDEXES:
                fp_ = flagged_pairs(fl[ind], ind)
                if ind == "pairscan":   # iita_pairscan's criterion: the planted ORDERED edge isolated
                    hit = {(i, j) for i, j, _, _, _, _, iso in fl[ind]["pairs"] if iso}
                    row[ind] = any(e in hit for e in edges)
                else:
                    row[ind] = any(tuple(sorted(e)) in fp_ for e in edges)
            out.append(row)
    return out


def a_fp_job(args):
    """iita_pairscan.fp_job, mirrored: FP_REPS simulations from the fitted 2PL, each with its own
    calibration, every statistic scored."""
    th, n, seed, draws = args
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(FP_REPS):
        Xs = ps.simulate(th, n, rng)
        c2 = calibrate_a(Xs, rng, draws)
        fl = score_all(Xs, c2)
        out.append({ind: bool(fl[ind]["isolated"]) for ind in INDEXES})
    return out


# ============================================================================ part (b): bifactor PL

def module_groups(skills, routes, level=LEVEL, min_group=MIN_GROUP):
    """Parent key route[:level] per skill; a compound skill 'a_b' takes a key only if all its components
    share it. Groups with >= min_group skills get a factor (index 0..S-1); others get -1."""
    keys = []
    for s in skills:
        ks = {tuple(routes[p][:level]) for p in s.split("_") if p in routes}
        keys.append(ks.pop() if len(ks) == 1 else None)
    cnt = {}
    for k in keys:
        if k is not None:
            cnt[k] = cnt.get(k, 0) + 1
    big = sorted(k for k, c in cnt.items() if c >= min_group)
    gidx = np.array([big.index(k) if k in big else -1 for k in keys])
    sizes = sorted(cnt.values(), reverse=True)
    return gidx, keys, sizes


class BF:
    """Bifactor 2PL with common asymptotes, one loading per group (a constrained bifactor):

        P(x_j = 1 | G, S) = g + (1 - g - l) logistic(a_j G + lam_s(j) S_s(j) + c_j),

    G, S_s iid N(0, 1); lam = 0 for skills with no group. Fitted by PAIRWISE (composite) likelihood over
    the 105 2x2 tables (limited information: the 2x2 tables are all it reads). With no groups it is
    iita_pairscan's model fitted by pairwise likelihood (the 1D-PL reference arm).
    """

    def __init__(self, gidx):
        self.g = np.asarray(gidx)
        self.S = int(self.g.max() + 1) if (self.g >= 0).any() else 0
        if self.S:
            self.ys, self.ws = XS, WS
        else:
            self.ys, self.ws = np.zeros(1), np.ones(1)
        self.same = (self.g[:, None] == self.g[None, :]) & (self.g[:, None] >= 0) & OFF
        self.diff = OFF & ~self.same
        self.W = WG[:, None] * self.ws[None, :]
        self.onehot = np.zeros((K, max(self.S, 1)))
        for j, s in enumerate(self.g):
            if s >= 0:
                self.onehot[j, s] = 1.0

    def unpack(self, x):
        a, c, g, l = x[:K], x[K:2 * K], x[2 * K], x[2 * K + 1]
        lam = x[2 * K + 2:]
        lj = self.onehot[:, :self.S] @ lam if self.S else np.zeros(K)
        return a, c, g, l, lam, lj

    def grid(self, x):
        a, c, g, l, lam, lj = self.unpack(x)
        Sg = 1 / (1 + np.exp(-(a[:, None, None] * XG[None, :, None] + lj[:, None, None] * self.ys[None, None, :]
                               + c[:, None, None])))
        return Sg, g + (1 - g - l) * Sg

    def pair_probs(self, P):
        Pbar = P @ self.ws                                         # (K, QG)
        p = Pbar @ WG
        same = np.einsum("iqv,jqv->ij", P * self.W[None], P) if self.S else 0.0
        diff = (Pbar * WG[None]) @ Pbar.T
        P11 = np.where(self.same, same, diff)
        return P11, p, Pbar

    def nll(self, x, n11, n):
        Sg, P = self.grid(x)
        P11, p, Pbar = self.pair_probs(P)
        o11, o10, o01, o00 = cells(n11, n)
        e11 = np.clip(P11, 1e-12, None)
        e10 = np.clip(p[:, None] - P11, 1e-12, None)
        e01 = np.clip(p[None, :] - P11, 1e-12, None)
        e00 = np.clip(1 - p[:, None] - p[None, :] + P11, 1e-12, None)
        ll = (o11 * np.log(e11) + o10 * np.log(e10) + o01 * np.log(e01) + o00 * np.log(e00))[UPPER].sum()
        A = o11 / e11 - o10 / e10 - o01 / e01 + o00 / e00
        A = np.where(OFF, A, 0.0)
        B = np.where(OFF, o10 / e10 - o00 / e00, 0.0).sum(1)
        S1 = np.einsum("ij,jqv->iqv", A * self.same, P) if self.S else 0.0
        S2 = ((A * self.diff) @ Pbar)[:, :, None]
        G = self.W[None] * (S1 + S2 + B[:, None, None])
        a, c, g, l, lam, lj = self.unpack(x)
        D = G * (1 - g - l) * Sg * (1 - Sg)
        da = (D * XG[None, :, None]).sum((1, 2))
        dc = D.sum((1, 2))
        dg = (G * (1 - Sg)).sum()
        dl = -(G * Sg).sum()
        grad = [da, dc, [dg, dl]]
        if self.S:
            dlj = (D * self.ys[None, None, :]).sum((1, 2))
            grad.append(self.onehot[:, :self.S].T @ dlj)
        npair = UPPER.sum()
        return -ll / (n * npair), -np.concatenate(grad) / (n * npair)

    def fit(self, n11, n, init=None):
        if init is None:
            p = np.clip(np.diag(n11) / n, 0.01, 0.99)
            x0 = np.concatenate([np.ones(K), 1.3 * np.log(p / (1 - p)), [0.02, 0.02], 0.5 * np.ones(self.S)])
        else:
            x0 = np.asarray(init, float).copy()
        bounds = ([(ps.A_MIN, ps.A_MAX)] * K + [(-ps.C_MAX, ps.C_MAX)] * K + [(0.0, ps.G_MAX)] * 2
                  + [(0.0, LAM_MAX)] * self.S)
        x0 = np.clip(x0, [b[0] for b in bounds], [b[1] for b in bounds])
        res = minimize(self.nll, x0, args=(n11, n), jac=True, method="L-BFGS-B", bounds=bounds,
                       options=dict(maxiter=ps.MAX_ITER, ftol=ps.FTOL, gtol=ps.GTOL))
        return res.x, int(res.nit), bool(res.success)

    def simulate(self, x, n, rng):
        a, c, g, l, lam, lj = self.unpack(x)
        G = rng.normal(size=(n, 1))
        if self.S:
            Sv = rng.normal(size=(n, self.S))
            gs = np.where(self.g >= 0, self.g, 0)
            Sj = Sv[:, gs] * (self.g >= 0)
        else:
            Sj = 0.0
        pr = g + (1 - g - l) / (1 + np.exp(-(a * G + lj * Sj + c)))
        return rng.random((n, K)) < pr

    def residuals(self, n11, n, x):
        """iita_pairscan.residuals with this model's expected counterexamples E_ij = n P(not i, j)."""
        _, P = self.grid(x)
        P11, p, _ = self.pair_probs(P)
        pi = np.clip(p[None, :] - P11, 0, 1)
        E = n * pi
        b = np.diag(n11)[None, :] - n11                            # mastered j, not i
        r = b - E
        pu = pi + pi.T
        with np.errstate(invalid="ignore", divide="ignore"):
            z = r / np.sqrt(np.maximum(n * pi * (1 - pi), 1e-9))
            zu = (r + r.T) / np.sqrt(np.maximum(n * pu * (1 - pu), 1e-9))
        return z, zu, b


def calibrate_b(X, model: BF, seed, draws):
    """iita_pairscan.calibrate's design under model `model`: fit, `draws` parametric-bootstrap samples
    from the fit, each refitted (warm start), residuals studentised by each draw's own refit."""
    rng = np.random.default_rng(seed)
    n = len(X)
    n11 = tables(X)
    x, iters, ok = model.fit(n11, n)
    rs, ru = np.empty((draws, K, K)), np.empty((draws, K, K))
    bmean = np.zeros((K, K))
    fails = 0
    for r in range(draws):
        Xs = model.simulate(x, n, rng)
        t = tables(Xs)
        x2, _, ok2 = model.fit(t, n, init=x)
        fails += not ok2
        rs[r], ru[r], b = model.residuals(t, n, x2)
        bmean += b / draws
    mu, sd = rs.mean(0), rs.std(0, ddof=1)
    mu_u, sd_u = ru.mean(0), ru.std(0, ddof=1)
    scan = OFF & (bmean >= ps.MIN_EXPECTED) & (sd > 0)
    sd, sd_u = np.where(sd > 0, sd, np.inf), np.where(sd_u > 0, sd_u, np.inf)
    Zs = (rs - mu) / sd
    tstar = np.sort(np.where(scan, Zs, np.inf).reshape(draws, -1).min(1))
    return dict(x=x, iters=iters, converged=ok, n=n, mu=mu, sd=sd, mu_u=mu_u, sd_u=sd_u, scan=scan,
                tstar=tstar, boot_nonconverged=fails)


def score_b(X, model, cal, refit=False):
    n11, n = tables(X), len(X)
    x = model.fit(n11, n, init=cal["x"])[0] if refit else cal["x"]
    z, zu, _ = model.residuals(n11, n, x)
    Z, Uz = (z - cal["mu"]) / cal["sd"], (zu - cal["mu_u"]) / cal["sd_u"]
    return ps.classify(Z, Uz, cal)


def plant_at(X, i, j, rng):
    """iita_dense's PAIR plant at a chosen placement: learners failing i fail j with probability 0.9."""
    return dense.gate(X, [i], j, rng)


def placements(gidx, rng, n_within, n_cross):
    """Ordered (i, j) plant placements: within a factor group, and across (no shared factor)."""
    within = [(i, j) for i in range(K) for j in range(K) if i != j and gidx[i] >= 0 and gidx[i] == gidx[j]]
    cross = [(i, j) for i in range(K) for j in range(K) if i != j and not (gidx[i] >= 0 and gidx[i] == gidx[j])]
    w = [within[k] for k in rng.choice(len(within), min(n_within, len(within)), replace=False)] if within else []
    c = [cross[k] for k in rng.choice(len(cross), n_cross, replace=False)]
    return [("within", e) for e in w] + [("cross", e) for e in c]


def b_cal_job(args):
    """One set under part (b): the 1D-PL and BF-PL calibrations, then the BF floor plants (scored
    against the unplanted calibrations, iita_pairscan's shortcut). Reads no residual of X itself."""
    X, gidx, key, draws, n_within, n_cross = args
    t0 = time.time()
    m1, mb = BF(np.full(K, -1)), BF(gidx)
    c1 = calibrate_b(X, m1, seed_for(*key, 1), draws)
    cb = calibrate_b(X, mb, seed_for(*key, 2), draws)
    rng = np.random.default_rng(seed_for(*key, 3))
    pl = []
    for where, (i, j) in placements(gidx, rng, n_within, n_cross):
        Y = plant_at(X, i, j, rng)
        hit = {(a, b) for a, b, _, _, _, _, iso in score_b(Y, mb, cb, refit=True)["pairs"] if iso}
        hit1 = {(a, b) for a, b, _, _, _, _, iso in score_b(Y, m1, c1, refit=True)["pairs"] if iso}
        pl.append(dict(where=where, edge=(int(i), int(j)), bf=(i, j) in hit, d1=(i, j) in hit1,
                       flips=int((X != Y).sum())))
    return dict(c1=c1, cb=cb, plants=pl, groups=int(mb.S), seconds=time.time() - t0)


def b_fp_job(args):
    """BF fitted-model check: FP_REPS simulations from the set's fitted BF, each with its own BF
    calibration and score. No pair dependence by construction."""
    x, gidx, n, key, draws = args
    mb = BF(gidx)
    rng = np.random.default_rng(seed_for(*key, 4))
    out = []
    for r in range(FP_REPS):
        Xs = mb.simulate(x, n, rng)
        c = calibrate_b(Xs, mb, seed_for(*key, 5, r), draws)
        out.append(bool(score_b(Xs, mb, c)["isolated"]))
    return out


# ============================================================================ synthetic worlds for (b)

def synthetic_group_world(n_sets, seed, partitions, free=False):
    """Shaped like the real sets: 15 skills, 200-3000 learners (set 0 at 3000), a ~ U(0.5, 2.5),
    difficulty ~ U(-2, 0.5), one general trait, plus a group factor on every parent group of >= 3
    skills, the partition taken from the real sets' label-blind module partitions in turn. Loading
    lam_s ~ U(0.5, 1.5) shared by the group (the fitted model's form), or with free=True one loading
    per skill ~ U(0.3, 1.5) (a free bifactor the fitted model only approximates). No pair dependence."""
    rng = np.random.default_rng(seed)
    out = []
    for s in range(n_sets):
        n = 3000 if s == 0 else int(round(math.exp(rng.uniform(math.log(200), math.log(3000)))))
        gidx = np.array(partitions[s % len(partitions)])
        a = rng.uniform(0.5, 2.5, K)
        d = rng.uniform(-2.0, 0.5, K)
        S = int(gidx.max() + 1)
        lam = rng.uniform(0.5, 1.5, max(S, 1))
        lj = np.where(gidx >= 0, lam[np.maximum(gidx, 0)], 0.0)
        if free:
            lj = np.where(gidx >= 0, rng.uniform(0.3, 1.5, K), 0.0)
        G = rng.normal(size=(n, 1))
        Sv = rng.normal(size=(n, max(S, 1)))
        Sj = Sv[:, np.maximum(gidx, 0)] * (gidx >= 0)
        X = rng.random((n, K)) < 1 / (1 + np.exp(-(a * (G - d) + lj * Sj)))
        out.append(dict(X=X, gidx=gidx, n=n))
    return out


# ============================================================================ summaries

def binom_ci(k, n, level=0.95):
    """Clopper-Pearson interval."""
    from scipy.stats import beta
    if n == 0:
        return [None, None]
    lo = 0.0 if k == 0 else float(beta.ppf((1 - level) / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - (1 - level) / 2, k + 1, n - k))
    return [lo, hi]


def kappa2(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    po = np.mean(a == b)
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return None if pe == 1 else float((po - pe) / (1 - pe))


def jaccard(A, B):
    u = len(A | B)
    return None if u == 0 else len(A & B) / u


def pooled_jaccard(per_set, rng, boots=2000):
    """sum |A & B| / sum |A | B| over sets; percentile interval resampling SETS."""
    inter = np.array([len(a & b) for a, b in per_set], float)
    uni = np.array([len(a | b) for a, b in per_set], float)
    est = float(inter.sum() / uni.sum()) if uni.sum() else None
    bs = []
    for _ in range(boots):
        idx = rng.integers(0, len(per_set), len(per_set))
        if uni[idx].sum():
            bs.append(inter[idx].sum() / uni[idx].sum())
    ci = [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))] if bs else [None, None]
    return est, ci


def adjacency_test(units_by_set, rng, n_perm=N_PERM):
    """Within-set permutation test of R1 enrichment among flagged pairs (one-sided, upper tail):
    units_by_set = [(r1 array over eligible pairs, flagged bool array)]. Count per set held fixed."""
    obs = sum(float(r1[fl].sum()) for r1, fl in units_by_set)
    nflag = sum(int(fl.sum()) for _, fl in units_by_set)
    null = np.zeros(n_perm)
    for r1, fl in units_by_set:
        f = int(fl.sum())
        if f == 0:
            continue
        idx = rng.random((n_perm, len(r1))).argsort(axis=1)[:, :f]
        null += r1[idx].sum(1)
    p = float((1 + np.sum(null >= obs)) / (n_perm + 1))
    return dict(flagged=nflag, adjacent=int(obs), rate=(obs / nflag if nflag else None),
                expected_rate=(float(null.mean()) / nflag if nflag else None), p=p if nflag else None)


def floor_rates(plants, key, where=None):
    per = []
    for pl in plants:
        xs = [p[key] for p in pl if where is None or p["where"] == where]
        if xs:
            per.append(float(np.mean(xs)))
    return dict(median=float(np.median(per)) if per else None, per_set=per,
                pooled=float(np.mean([p[key] for pl in plants for p in pl if where is None or p["where"] == where]))
                if per else None)


def corpus_verdict(n, k, floor_med, fp):
    p0 = max(CHANCE_MIN, fp)
    p = dense.binom_sf(k, n, p0) if n else 1.0
    if floor_med is None or floor_med < FLOOR_RATE:
        return "UNANSWERABLE", "floor fails", p, p0
    if fp > FP_MAX:
        return "UNANSWERABLE", f"fitted-model false-positive rate {fp:.3f} > {FP_MAX}", p, p0
    if n < MIN_SCORED:
        return "UNANSWERABLE", f"fewer than {MIN_SCORED} scored sets", p, p0
    return (POSITIVE if p < 0.05 else "NO DEPENDENCE DETECTED"), "", p, p0


def committed():
    import hashlib
    if hashlib.sha256(PAIRSCAN_OUT.read_bytes()).hexdigest() != PAIRSCAN_SHA256:
        raise SystemExit(f"{PAIRSCAN_OUT} is not the committed iita-pairscan output")
    return json.loads(PAIRSCAN_OUT.read_text())


def committed_flags(row):
    pos = {s: k for k, s in enumerate(row["skills"])}
    iso = {tuple(sorted((pos[p["prereq"]], pos[p["dependant"]]))) for p in row.get("pairs", []) if p["isolated"]}
    return iso


def partitions_from(run, routes):
    rows = next(c for c in run["corpora"] if c["corpus"] == "xes3g5m")["sets"]
    return [module_groups(r["skills"], routes) for r in rows]


def pairs_ids(P, skills):
    return sorted([skills[i], skills[j]] for i, j in P)


# ============================================================================ phases

def run_synthetic(pool, log, n_sets, draws):
    from pairscan_curriculum import load_routes
    run = committed()
    parts = [g.tolist() for g, _, _ in partitions_from(run, load_routes())]
    out = {}
    for w, (free, seed) in {"group": (False, 1), "group-free": (True, 2)}.items():
        sets = synthetic_group_world(n_sets, SEED + seed, parts, free=free)
        t0 = time.time()
        res = pool.map(b_cal_job, [(s["X"], s["gidx"], (900 + seed, i), draws, 8, 7) for i, s in enumerate(sets)],
                       chunksize=1)
        rows = []
        for s, r in zip(sets, res):
            m1, mb = BF(np.full(K, -1)), BF(s["gidx"])
            f1, fb = score_b(s["X"], m1, r["c1"]), score_b(s["X"], mb, r["cb"])
            F1 = {tuple(sorted((i, j))) for i, j, *_, iso in f1["pairs"] if iso}
            Fb = {tuple(sorted((i, j))) for i, j, *_, iso in fb["pairs"] if iso}
            within = {p for p in F1 if s["gidx"][p[0]] >= 0 and s["gidx"][p[0]] == s["gidx"][p[1]]}
            rows.append(dict(n=s["n"], groups=r["groups"], fires_1d=bool(f1["isolated"]), any_1d=bool(f1["any"]),
                             clustered_1d=bool(f1["clustered"]), fires_bf=bool(fb["isolated"]),
                             any_bf=bool(fb["any"]), flagged_1d=len(F1), flagged_1d_within=len(within),
                             survive_bf=len(F1 & Fb), within_survive_bf=len(within & Fb), flagged_bf=len(Fb),
                             conv=(r["c1"]["converged"], r["cb"]["converged"]),
                             boot_nc=(r["c1"]["boot_nonconverged"], r["cb"]["boot_nonconverged"]),
                             seconds=round(r["seconds"], 1)))
        plants = [r["plants"] for r in res]
        summ = dict(
            sets=len(rows),
            bf_false_alarm=float(np.mean([r["fires_bf"] for r in rows])),
            bf_any=float(np.mean([r["any_bf"] for r in rows])),
            d1_fires=float(np.mean([r["fires_1d"] for r in rows])),
            d1_any=float(np.mean([r["any_1d"] for r in rows])),
            d1_clustered=float(np.mean([r["clustered_1d"] for r in rows])),
            d1_flagged=sum(r["flagged_1d"] for r in rows), d1_flagged_within=sum(r["flagged_1d_within"] for r in rows),
            d1_within_survive_bf=sum(r["within_survive_bf"] for r in rows),
            floor_bf_within=floor_rates(plants, "bf", "within"), floor_bf_cross=floor_rates(plants, "bf", "cross"),
            floor_1d_within=floor_rates(plants, "d1", "within"), floor_1d_cross=floor_rates(plants, "d1", "cross"),
            median_flips=float(np.median([p["flips"] for pl in plants for p in pl])),
            seconds=round(time.time() - t0))
        log(f"world {w}: BF false alarm {summ['bf_false_alarm']:.3f} (any {summ['bf_any']:.2f}); 1D-PL fires "
            f"{summ['d1_fires']:.2f} any {summ['d1_any']:.2f} clustered {summ['d1_clustered']:.2f}; 1D flagged "
            f"{summ['d1_flagged']} ({summ['d1_flagged_within']} within), within surviving BF "
            f"{summ['d1_within_survive_bf']}; floor BF within {summ['floor_bf_within']['median']} cross "
            f"{summ['floor_bf_cross']['median']}; 1D within {summ['floor_1d_within']['median']} cross "
            f"{summ['floor_1d_cross']['median']} ({summ['seconds']}s)")
        out[w] = dict(summary=summ, sets=rows)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--synthetic-sets", type=int, default=20)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--draws", type=int, default=R_REAL)
    args = ap.parse_args()

    def log(s=""):
        print(s, flush=True)

    with Pool(args.workers) as pool:
        if args.synthetic:
            res = run_synthetic(pool, log, args.synthetic_sets, R_SYN)
            p = HERE / "out" / "ld-checks-synthetic.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(dict(seed=SEED, draws=R_SYN, level=LEVEL, min_group=MIN_GROUP, worlds=res),
                                    indent=1, default=str) + "\n")
            log(f"wrote {p}")
            return
        run_real(pool, log, args.draws)


def run_real(pool, log, draws):
    from pairscan_curriculum import load_routes
    run = committed()
    routes = load_routes()
    out = HERE / "out" / "ld-checks.json"
    result = dict(seed=SEED, draws=draws, alpha=ALPHA, level=LEVEL, min_group=MIN_GROUP,
                  pairscan_sha256=PAIRSCAN_SHA256, corpora={})

    def checkpoint(note):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(dict(partial=note, **result), indent=1, default=str) + "\n")

    store = {}
    # ---------------------------------------------------------------- phases 1-3: calibrations, floors, FP
    for cid, name in enumerate(("xes3g5m", "assist12")):
        crow = next(c for c in run["corpora"] if c["corpus"] == name)
        sets = [s for s in dense.real_sets(name) if s["X"].shape[1] == K]
        rows = [r for r in crow["sets"] if r["fit_converged"]]
        if [s["skills"] for s in sets] != [r["skills"] for r in rows] or \
                [len(s["X"]) for s in sets] != [r["learners"] for r in rows]:
            raise SystemExit(f"{name}: rebuilt sets differ from the committed pairscan sets")
        t0 = time.time()
        cals = pool.map(a_calibrate_job, [(s["X"], ps.seed_for(cid, i, 1), draws) for i, s in enumerate(sets)],
                        chunksize=1)
        repro = [dict(set=i, scanned=int(c["scan"].sum()), scanned_committed=r["scanned"],
                      critical_z=ps.critical(c["tstar"]), critical_z_committed=r["critical_z"],
                      a_max_diff=float(np.max(np.abs(c["th"][0] - np.array(r["a"])))))
                 for i, (c, r) in enumerate(zip(cals, rows))]
        log(f"{name}: {len(sets)} sets calibrated ({time.time() - t0:.0f}s); scan reproduction "
            f"{sum(x['scanned'] == x['scanned_committed'] for x in repro)} of {len(repro)} scanned counts, "
            f"max |critical z diff| {max(abs(x['critical_z'] - x['critical_z_committed']) for x in repro):.4f}")
        t1 = time.time()
        plants = pool.map(a_plants_job, [(s["X"], c, (cid, i)) for i, (s, c) in enumerate(zip(sets, cals))],
                          chunksize=1)
        floor = {}
        for ind in INDEXES:
            per = {kind: [float(np.mean([o[ind] for o in pl if o["kind"] == kind])) for pl in plants]
                   for kind in ("pair", "gate")}
            floor[ind] = dict(pair_median=float(np.median(per["pair"])), gate_median=float(np.median(per["gate"])),
                              pair_per_set=per["pair"], gate_per_set=per["gate"])
        log(f"  floor ({time.time() - t1:.0f}s): " + ", ".join(
            f"{k} PAIR {v['pair_median']:.2f} GATE {v['gate_median']:.2f}" for k, v in floor.items()) +
            f"  (committed pairscan PAIR {crow['floor']['pair']['median_rate']:.2f})")
        t2 = time.time()
        fps = pool.map(a_fp_job, [(c["th"], c["n"], ps.seed_for(cid, i, 3), draws) for i, c in enumerate(cals)],
                       chunksize=1)
        fp = {ind: float(np.mean([f[ind] for fs in fps for f in fs])) for ind in INDEXES}
        log(f"  fitted-model false positives ({time.time() - t2:.0f}s): " +
            ", ".join(f"{k} {v:.3f}" for k, v in fp.items()) +
            f"  (committed pairscan {crow['fitted_model_fp']['isolated']:.3f})")
        part_a = dict(sets=len(sets), reproduction=repro, floor=floor, fitted_model_fp=fp,
                      fitted_model_fp_per_set=fps,
                      control_scale=dict(null_hamming_median=float(np.median([c["hamming"] for c in cals]))))
        result["corpora"][name] = dict(a=part_a)
        store[name] = dict(sets=sets, rows=rows, cals=cals)
        checkpoint("part (a) floor and false-positive checks written; observed statistics not yet computed")

    # part (b), XES3G5M only (the only corpus here with a taxonomy)
    name = "xes3g5m"
    sets, rows = store[name]["sets"], store[name]["rows"]
    grp = [module_groups(s["skills"], routes) for s in sets]
    t3 = time.time()
    bres = pool.map(b_cal_job, [(s["X"], g[0], (100, i), draws, 8, 7) for i, (s, g) in enumerate(zip(sets, grp))],
                    chunksize=1)
    plants = [r["plants"] for r in bres]
    bfloor = dict(bf_within=floor_rates(plants, "bf", "within"), bf_cross=floor_rates(plants, "bf", "cross"),
                  d1_within=floor_rates(plants, "d1", "within"), d1_cross=floor_rates(plants, "d1", "cross"))
    log(f"part (b) calibrations and floor ({time.time() - t3:.0f}s): BF within {bfloor['bf_within']['median']} "
        f"cross {bfloor['bf_cross']['median']}; 1D-PL within {bfloor['d1_within']['median']} cross "
        f"{bfloor['d1_cross']['median']}")
    t4 = time.time()
    bfp = pool.map(b_fp_job, [(r["cb"]["x"], g[0], r["cb"]["n"], (100, i), R_SYN)
                              for i, (r, g) in enumerate(zip(bres, grp))], chunksize=1)
    bfp_rate = float(np.mean([f for fs in bfp for f in fs]))
    log(f"  BF fitted-model false positives ({time.time() - t4:.0f}s): {bfp_rate:.3f}")
    result["corpora"][name]["b"] = dict(
        groups_per_set=[int(r["groups"]) for r in bres], module_sizes_per_set=[g[2] for g in grp],
        within_pairs_per_set=[int(BF(g[0]).same[UPPER].sum()) for g in grp],
        lam_per_set=[[round(float(v), 3) for v in r["cb"]["x"][2 * K + 2:]] for r in bres],
        conv=[(r["c1"]["converged"], r["cb"]["converged"]) for r in bres],
        boot_nonconverged=[(r["c1"]["boot_nonconverged"], r["cb"]["boot_nonconverged"]) for r in bres],
        floor=bfloor, plants_per_set=plants, fitted_model_fp=bfp_rate, fitted_model_fp_per_set=bfp)
    checkpoint("parts (a) and (b) floor and false-positive checks written; observed statistics not yet computed")

    # ---------------------------------------------------------------- phase 4: observed statistics
    rng = np.random.default_rng(seed_for(7))
    for name in ("xes3g5m", "assist12"):
        sets, rows, cals = store[name]["sets"], store[name]["rows"], store[name]["cals"]
        A = result["corpora"][name]["a"]
        per, refs = [], []
        flagged = {ind: [] for ind in INDEXES}
        for i, (s, r, c) in enumerate(zip(sets, rows, cals)):
            fl = score_all(s["X"], c)
            ref = committed_flags(r)
            refs.append(ref)
            row = dict(set=i, learners=len(s["X"]), committed_fires=bool(r["fires_isolated"]),
                       committed_flagged=pairs_ids(ref, s["skills"]))
            for ind in INDEXES:
                F = flagged_pairs(fl[ind], ind)
                flagged[ind].append(F)
                row[ind] = dict(fires=bool(fl[ind]["isolated"]), any=bool(fl[ind]["any"]),
                                clustered=bool(fl[ind]["clustered"]), flagged=len(F),
                                significant=len(sig_pairs(fl[ind], ind)),
                                overlap=len(F & ref), jaccard=jaccard(F, ref), pairs=pairs_ids(F, s["skills"]))
            per.append(row)
        store[name]["refs"] = refs
        summary = {}
        for ind in INDEXES:
            fires = [row[ind]["fires"] for row in per]
            comm = [row["committed_fires"] for row in per]
            v, why, p, p0 = corpus_verdict(len(per), sum(fires), A["floor"][ind]["pair_median"],
                                           A["fitted_model_fp"][ind])
            pj, ci = pooled_jaccard(list(zip(flagged[ind], refs)), rng)
            adj = None
            if name == "xes3g5m":
                units = []
                for s, c, F in zip(sets, cals, flagged[ind]):
                    el = [tuple(int(v_) for v_ in u) for u in zip(*np.nonzero(c["uscan"]))]
                    r1 = np.array([relate(s["skills"][i], s["skills"][j], routes)[0] for i, j in el], float)
                    units.append((r1, np.array([u in F for u in el])))
                adj = adjacency_test(units, rng)
            summary[ind] = dict(sets_firing=int(sum(fires)), scored=len(per),
                                flagged_pairs=int(sum(len(F) for F in flagged[ind])),
                                overlap_with_committed=int(sum(len(F & R_) for F, R_ in zip(flagged[ind], refs))),
                                committed_pairs=int(sum(len(R_) for R_ in refs)),
                                pooled_jaccard=pj, pooled_jaccard_ci95_sets=ci,
                                set_verdict_agreement=float(np.mean(np.array(fires) == np.array(comm))),
                                set_verdict_kappa=kappa2(fires, comm),
                                verdict=v, reason=why, binomial_p=p, chance_rate=p0, adjacency=adj)
            log(f"{name} {ind}: fires {sum(fires)}/{len(per)}, flagged {summary[ind]['flagged_pairs']}, overlap "
                f"{summary[ind]['overlap_with_committed']}/{summary[ind]['committed_pairs']}, pooled J {pj} {ci}, "
                f"agreement {summary[ind]['set_verdict_agreement']:.2f}; {v} {why} p={p:.3g}"
                + (f"; R1 {adj['adjacent']}/{adj['flagged']} p={adj['p']}" if adj and adj['flagged'] else ""))
        A["per_set"] = per
        A["summary"] = summary
        if name == "xes3g5m":
            vs = [summary[ind]["verdict"] for ind in ("g2", "q3")]
            if all(v == POSITIVE for v in vs):
                reading = "STATISTIC-ROBUST"
            elif any(v == "NO DEPENDENCE DETECTED" for v in vs):
                reading = "STATISTIC-DEPENDENT"
            else:
                reading = "PARTLY ANSWERABLE"
            A["reading"] = reading
            log(f"part (a) reading: {reading}")

    # part (b) observed
    name = "xes3g5m"
    sets, refs = store[name]["sets"], store[name]["refs"]
    B = result["corpora"][name]["b"]
    per = []
    F1s, Fbs = [], []
    for i, (s, r, g) in enumerate(zip(sets, bres, grp)):
        gidx, keys = g[0], g[1]
        m1, mb = BF(np.full(K, -1)), BF(gidx)
        f1, fb = score_b(s["X"], m1, r["c1"]), score_b(s["X"], mb, r["cb"])
        F1 = {tuple(sorted((int(a), int(b)))) for a, b, *_, iso in f1["pairs"] if iso}
        Fb = {tuple(sorted((int(a), int(b)))) for a, b, *_, iso in fb["pairs"] if iso}
        F1s.append(F1)
        Fbs.append(Fb)
        pc = []
        for p in sorted(refs[i]):
            a, b = p
            if gidx[a] >= 0 and gidx[a] == gidx[b]:
                cat = "within"
            elif keys[a] is not None and keys[a] == keys[b]:
                cat = "doublet"
            else:
                cat = "cross"
            pc.append(dict(pair=[s["skills"][a], s["skills"][b]], category=cat, kept_1d=p in F1, kept_bf=p in Fb,
                           adjacent=bool(relate(s["skills"][a], s["skills"][b], routes)[0])))
        per.append(dict(set=i, fires_1d=bool(f1["isolated"]), fires_bf=bool(fb["isolated"]),
                        clustered_bf=bool(fb["clustered"]),
                        flagged_1d=pairs_ids(F1, s["skills"]), flagged_bf=pairs_ids(Fb, s["skills"]),
                        committed=pc, new_under_bf=len(Fb - F1), lost_under_bf=len(F1 - Fb)))
    surv = {}
    for cat in ("within", "doublet", "cross"):
        cs = [c for row in per for c in row["committed"] if c["category"] == cat]
        k1 = sum(c["kept_1d"] for c in cs)
        kb = sum(c["kept_1d"] and c["kept_bf"] for c in cs)
        surv[cat] = dict(committed=len(cs), kept_1d=int(k1), kept_bf_of_kept_1d=int(kb),
                         kept_bf_all=int(sum(c["kept_bf"] for c in cs)),
                         survival=(kb / k1 if k1 else None), survival_ci95=binom_ci(kb, k1))
    adj = {}
    for arm, Fs in (("1d", F1s), ("bf", Fbs)):
        units = []
        for s, F, r in zip(sets, Fs, bres):
            c = r["c1"] if arm == "1d" else r["cb"]
            uscan = (c["scan"] | c["scan"].T) & UPPER
            el = [tuple(int(v_) for v_ in u) for u in zip(*np.nonzero(uscan))]
            r1 = np.array([relate(s["skills"][i], s["skills"][j], routes)[0] for i, j in el], float)
            units.append((r1, np.array([u in F for u in el])))
        adj[arm] = adjacency_test(units, rng)
    n = len(per)
    k1, kb = sum(r["fires_1d"] for r in per), sum(r["fires_bf"] for r in per)
    v1 = corpus_verdict(n, k1, bfloor["d1_cross"]["median"], 0.0)
    vb = corpus_verdict(n, kb, bfloor["bf_within"]["median"], bfp_rate)
    B.update(per_set=per, survival=surv, adjacency=adj, sets_firing_1d=int(k1), sets_firing_bf=int(kb),
             flagged_1d=int(sum(len(F) for F in F1s)), flagged_bf=int(sum(len(F) for F in Fbs)),
             verdict_bf_scan=dict(verdict=vb[0], reason=vb[1], binomial_p=vb[2], chance_rate=vb[3]),
             verdict_1d_scan=dict(verdict=v1[0], reason=v1[1], binomial_p=v1[2], chance_rate=v1[3]))
    log(f"part (b): sets firing 1D-PL {k1}/{n}, BF {kb}/{n}; survival {surv}; adjacency {adj}")
    B["verdict"], B["verdict_reason"] = b_verdict(B)
    log(f"part (b) VERDICT: {B['verdict']} ({B['verdict_reason']})")
    checkpoint(False)
    log(f"wrote {out}")


def b_verdict(B):
    """The pre-registered part (b) verdict (docstring, VERDICTS (b)). Reads the synthetic gates from the
    committed out/ld-checks-synthetic.json."""
    syn = json.loads((HERE / "out" / "ld-checks-synthetic.json").read_text())["worlds"]
    g, gf = syn["group"]["summary"], syn["group-free"]["summary"]
    floors = [B["floor"]["bf_within"]["median"], B["floor"]["bf_cross"]["median"],
              g["floor_bf_within"]["median"], g["floor_bf_cross"]["median"]]
    if any(f is None or f < FLOOR_RATE for f in floors):
        return "UNANSWERABLE", f"BF floor fails (real within/cross, synthetic within/cross: {floors})"
    if g["bf_false_alarm"] > FP_MAX:
        return "UNANSWERABLE", f"BF false alarm in the group-only world {g['bf_false_alarm']:.3f} > {FP_MAX}"
    if B["fitted_model_fp"] > FP_MAX:
        return "UNANSWERABLE", f"BF fitted-model false-positive rate {B['fitted_model_fp']:.3f} > {FP_MAX}"
    w = B["survival"]["within"]
    if not w["kept_1d"]:
        return "UNANSWERABLE", "no committed within-module pair is flagged by the 1D-PL reference arm"
    s, p_bf, p_1d = w["survival"], B["adjacency"]["bf"]["p"], B["adjacency"]["1d"]["p"]
    p_bf = 1.0 if p_bf is None else p_bf
    if s <= 0.25 and p_bf >= 0.05:
        return "UNIT-LEVEL FACTOR", f"within survival {s:.3f}; BF adjacency p {p_bf:.4f} (1D-PL {p_1d})"
    if s >= 0.5 and p_bf < 0.05 and B["verdict_bf_scan"]["verdict"] == POSITIVE:
        if gf["bf_false_alarm"] > FP_MAX:
            return "MIXED", (f"would be PAIR-SPECIFIC, downgraded: group-free world false alarm "
                             f"{gf['bf_false_alarm']:.3f} > {FP_MAX}")
        return "PAIR-SPECIFIC", f"within survival {s:.3f}; BF adjacency p {p_bf:.4f}; BF scan {POSITIVE}"
    return "MIXED", f"within survival {s:.3f}; BF adjacency p {p_bf:.4f}; BF scan {B['verdict_bf_scan']['verdict']}"


if __name__ == "__main__":
    main()
