"""PRE-REGISTERED: a latent-level positive control on ECPE. Does a likelihood-based hierarchy test find
the published attribute hierarchy, and do the programme's own instruments find it on the same data?

Literature review for Paper II, rank 11 (research/readiness/learning-graph-budget-2026/literature.md:
synthesis row 6; strand 2 entries 2.7 Leighton, Gierl & Hunka 2004 and 2.9 Templin & Bradshaw 2014,
strand-2 "Analyses" item 4; strand 3 entries 3.14 Templin & Bradshaw 2014, 3.15 Ma & Xu 2021, 3.16 Cui,
Gierl & Chang 2012, 3.17 Thompson & Nash 2022, strand-3 "Analyses" item 6). Protects the F1 and F6
detection floors: Paper II reports that IITA against fixed margins "sees no dependency and could not
have", that a pairwise scan finds dependence beyond one trait, and that an interaction test finds AND
structure that pairwise tests attenuate. None of those instruments has been run on data where a
prerequisite hierarchy among latent skills is independently established. ECPE is such data.

DATA (reads a corpus). ECPE grammar section (Templin & Hoffman 2013, https://doi.org/10.1111/emip.12010),
as shipped in the CDM R package 8.3-14 (Robitzsch, Kiefer, George & Uenlue); data id `ecpe` in
data/data-sources.json, read through shared.paths.data_path("ECPE_DIR"): ecpe_responses.csv (2,922
examinees x 28 dichotomous items E1..E28) and ecpe_qmatrix.csv (28 items x 3 skills). Licence: no data
licence stated; maintainer approved use 2026-10-07 under research use, no redistribution, aggregates
only. Nothing learner-level is written: out/*.json holds fitted model parameters (class proportions,
per-item group success probabilities), test statistics, rates and percentiles. Skills are named by id
(skill1 morphosyntactic, skill2 cohesive, skill3 lexical, as the CDM Rd file names them).

THE HIERARCHY TESTED, stated exactly. Templin & Bradshaw (2014, Psychometrika 79, 317-339,
https://doi.org/10.1007/s11336-013-9362-0) fit the HDCM to these data. Their abstract (read from the
University of Iowa repository record; the Springer full text was not reachable from here) says the
HDCM "is used to test for the presence of a suspected attribute hierarchy in a test of English grammar,
confirming the data is more adequately represented by hierarchical attribute structure when compared
to a crossed, or nonhierarchical structure". The abstract does not name the order. The order is taken
from the secondary literature that reports their result on these data (Frontiers in Psychology 2018,
9:1875, https://doi.org/10.3389/fpsyg.2018.01875, on the M2 statistic under attribute hierarchies):
"There exists a linear hierarchy underlying the three attributes: 'lexical rules' is the prerequisite
attribute of 'cohesive rules,' which in turn is the prerequisite attribute of 'morphosyntactic
rules.'" The internal note studies/identifiability/learning-structure/LIT-DATASETS.md also records it as
a linear hierarchy. So the tested hierarchy H_PUB is the linear chain

    skill3 (lexical)  ->  skill2 (cohesive)  ->  skill1 (morphosyntactic)

whose permissible attribute profiles (skill1, skill2, skill3) are 000, 001, 011, 111; the other four
(100, 010, 110, 101) have zero probability under it. That its order is from a secondary source and not
from T&B's text is a limit of this study, stated in the README.

DIRECTION: (a, b) means a is the prerequisite of b ("b mastered implies a mastered"), per iita.py (DAKS)
and the hierarchy convention above; H_PUB as (prerequisite, dependant) skill pairs is {(skill3, skill2),
(skill2, skill1), (skill3, skill1)}. Every reading below is scored against H_PUB AND its reverse H_REV
(skill1 -> skill2 -> skill3, profiles 000, 100, 110, 111); a reading that does not beat its reverse is
not called agreement.

POSITIVITY. Testing a hierarchy needs an item measuring each skill alone (literature 1.1: Gu & Xu 2024,
Prop. 1; 3.15: Ma & Xu's testability). ECPE's Q-matrix has single-skill items for all three skills
(skill1: E10 E13 E14 E25 E27; skill2: E2 E8 E23 E24; skill3: E4 E5 E6 E9 E15 E18 E19 E22 E26 E28),
asserted at load. The interaction test has its own positivity rule (every parent cell >= 20 learners,
stage3_interaction.MIN_CELL); a triple failing it is UNSCORED, which a strict hierarchy invites: the
cell "cohesive held, lexical not" is forbidden latently and is filled only by misclassification.

PART 1, THE REFERENCE (likelihood-based latent test)
MODEL        Saturated diagnostic classification model: for each item j, one free success probability
             per pattern of the skills it measures (2^K_j groups, K_j <= 2 here), and a free
             distribution over the 8 attribute profiles. With every interaction free this is the
             saturated LCDM (Henson, Templin & Willse 2009), equivalently saturated G-DINA (literature
             2.8); the link function is immaterial when saturated. Monotonicity constraints, which T&B's
             LCDM imposes, are NOT imposed; the number of fitted violations is reported. Fitted by EM in
             numpy (E-step over response patterns, closed-form M-step), stopping when the total
             log-likelihood rises by < 1e-7, at most 20,000 iterations.
HIERARCHICAL The same model with the profile probabilities outside the hierarchy fixed at zero. Item
             groups no permissible profile reaches are unused. With saturated items this attains the
             HDCM's maximised likelihood (T&B's HDCM nests item effects so that effects for absent
             profiles vanish; in a saturated parameterisation that removes nothing the likelihood uses).
STARTS       Real data: 20 random starts per model, and the saturated fit also from each hierarchical
             solution with 0.01 added to each forbidden profile (so ll_sat >= ll_hier up to EM
             tolerance; LR is floored at 0). Bootstrap and floor refits: warm starts (hierarchical
             from the generating fit; saturated from the refitted hierarchical solution + 0.01), plus
             4 random starts per model on each floor replicate's observed data.
TEST         LR = 2 (ll_sat - ll_hier). Parametric bootstrap (Ma & Xu 2021, who show the chi-squared
             reference fails for hierarchy tests): B samples of n = 2,922 from the fitted hierarchical
             model, both models refitted on each, p = (1 + #{LR* >= LR}) / (B + 1). B = 500 on real
             data; B = 49 per floor replicate (CHANGE 1; budget: 4 cores shared with up to eight agents).
             Run for H_PUB, for H_REV, and, reported only, for the other four linear orders of three
             skills.
SECONDARY    Forbidden-profile mass under the saturated fit, with a 95% percentile interval from 200
             nonparametric bootstrap resamples of examinees (the sampled unit). Reported only.

PART 2, THE PROGRAMME'S INSTRUMENTS (imported, not copied)
GRAINS       ITEM grain: the 28 item responses. SKILL grain: skill k "held" = at least half of the
             skill's single-skill items correct (the k/n >= 0.5 mastery rule of iita_dense.py and
             surmise_graphs.py), giving a 2,922 x 3 matrix. Items measuring two skills do not enter
             the skill grain. Item level for item-grain direction: level 3 if the item measures
             skill1, else 2 if skill2, else 1 (skill3 only); under H_PUB a lower-level item is the
             prerequisite side.
I1 IITA      SKILL grain, verdict-bearing (it is the grain iita_dense ran at). Corrected IITA
             (iita.py via iita_dense.iita_count), fixed-margins null by iita_dense.null_counts
             (global curveball, R = 500, margins asserted), band = 2.5th/97.5th percentile,
             degenerate if they coincide (iita_dense's positivity rule), beyond the null if the
             implication count is strictly outside the band (either tail, tail reported).
             Direction d = |relation & H_PUB| - |relation & H_REV|.
               AGREES    beyond the null and d > 0
               REVERSED  beyond the null and d < 0
               MISSES    otherwise (inside the band, degenerate, or d = 0)
             ITEM grain, reported only: the same count against nulls.fixed_margin_draws (checkerboard
             swaps; the curveball packs 16 columns at most), R = 200, and the share of cross-level
             implications running low -> high level against the same null's distribution of it.
I2 PAIRSCAN  ITEM grain only (a 2PL with two common asymptotes has 8 parameters; three skill
             indicators give 7 free cell probabilities, so the skill grain cannot be fitted).
             iita_pairscan's calibrate/score/classify with its module constants K and OFF set to 28
             items (the functions read them as globals); everything else as pre-registered there:
             max-T adjusted p < 0.025, ISOLATED as the verdict-bearing flag. R = 200 on real data
             (iita_pairscan used 500; a 28-item fit takes 7-19 s on this loaded machine, so 500 refits
             would hold a worker ~2 h; at R = 200 a pair is significant at bootstrap rank <= 4).
             For each unordered cross-level item pair with a significant ordered orientation, the
             orientation with the more negative z is its claim; agree if it runs low -> high level.
             Over ISOLATED significant cross-level pairs:
               AGREES    more agree than disagree
               REVERSED  more disagree than agree
               MISSES    none, or a tie
             The same over all significant pairs (CLUSTERED included) is reported, not verdict-bearing.
             iita_pairscan's own corpus verdict needs >= 5 sets and cannot be returned on one set;
             its plant floor (15 PAIR, 15 GATE, 10 CHAIN plants into the real matrix) and its
             fitted-model false-positive check (2 simulations, own calibrations at R = 100) are run on
             the real matrix and reported.
             Expected before any run: a linear hierarchy of three skills is an ordered latent class
             structure, close to one trait, so the 2PL should absorb most of it and the scan should
             MISS. The control still measures it.
I3 INTERACT  SKILL grain. stage3_interaction.score (interaction = (m_both - m_A) - (m_B - m_neither),
             analytic SE, MIN_CELL 20), one-sided p, BH at q = 0.05 over the three triples (each skill
             as dependant of the other two), stage3's three-state verdict per triple (SUPPORTED /
             CONTRADICTED below +0.10 / UNKNOWN). The analytic SE is checked against
             stage3_interaction.empirical_null (learner-deranged, 200 draws) on the real triples and
             the ratio reported. Under H_PUB, skill1 needs skill2 and (through it) skill3: the
             published triple is dependant skill1, parents skill3 and skill2; the reversed triple is
             dependant skill3, parents skill1 and skill2.
               AGREES    published triple SUPPORTED, and its interaction exceeds the reversed
                         triple's (or the reversed triple is unscored)
               REVERSED  reversed triple SUPPORTED and its interaction exceeds the published's (or
                         the published is unscored)
               MISSES    otherwise
NOT RUN      The pairwise drop and the lag profile need an order of attempts in time (a learner's
             state on the prerequisite when first meeting the dependant, and the time between). ECPE
             is one cross-sectional administration with no timestamps: neither can run, and nothing
             here speaks to them. The mastery-release contrast likewise.

PART 3, SYNTHETIC FLOOR (ECPE-shaped: same Q, n = 2,922, item parameters from the real saturated fit)
ITEM PARAMS  The real saturated fit's per-item group probabilities, projected to be monotone (the
             no-skill group set to the item's minimum, the all-skills group to its maximum, partial
             groups clipped between them). The same item parameters in every world, so worlds differ
             only in the profile distribution. (These come from a real-data fit, so the floor runs
             after the design commit and after the fit, but before any test statistic, instrument
             reading or verdict on real data is computed.)
WORLDS       PUB    H_PUB planted: the real hierarchical (H_PUB) fit's class proportions.
             REV    H_REV planted: PUB's proportions moved to the mirror profiles (000->000, 001->100,
                    011->110, 111->111). Same size as PUB, opposite direction: the signed control.
             ONE    no hierarchy, one trait: alpha_k = 1[lambda theta + sqrt(1 - lambda^2) e_k > tau_k],
                    theta, e_k ~ N(0, 1); tau_k matching PUB's attribute margins exactly; lambda set by
                    bisection so the forbidden mass is 0.10, the same violation size as MIX 0.10.
                    Profile probabilities exact by 61-node Gauss-Hermite quadrature. Same margins as
                    PUB, skills correlated through one trait, every profile possible: the confound
                    (ability plus difficulty order without a hierarchy) a programme instrument must not
                    read as a hierarchy.
                    First specified with lambda matching PUB's mean pairwise attribute phi. Changed
                    before the design commit, on the dry run (a synthetic world with invented
                    parameters, no corpus): matching phi 0.66 drove lambda to its 0.999 cap with a
                    forbidden mass of 3e-12. At that correlation a one-trait threshold model IS a linear
                    hierarchy (a Guttman scale), so it could not serve as a no-hierarchy control. The
                    matched-phi lambda and its forbidden mass are still computed on the real fit and
                    reported: if the real attributes' correlation forces the same degeneracy, "linear
                    hierarchy" and "one ordered trait with thresholds" are not separable on ECPE, which
                    the README states.
             MIX f  (1 - w) PUB + w INDEP, INDEP the independent profile distribution with PUB's
                    margins (so margins are exact), w set so the forbidden mass is f. f = 0.10 is the
                    pre-registered violation size for the latent test's power; f = 0.05 reported.
REPLICATES   Latent test: PUB 60 (size of the H_PUB test; power of the H_REV test), MIX 0.10 40,
             ONE 40, MIX 0.05 30; B = 49 each, so a replicate rejects at p = (1 + k)/50 < 0.05, i.e.
             when at most 1 of its 49 bootstrap LRs reaches its own (CHANGE 1). IITA and interaction: 200 per world (PUB, REV, ONE).
             Pairscan: 20 per world (PUB, REV, ONE), each scored against ONE calibration per world at
             R = 100 fitted on that world's first replicate (iita_pairscan's own shortcut, there
             validated against own calibrations); here validated again on 1 replicate per world
             against its own R = 100 calibration, agreement reported. With R = 100 the max-T critical
             value is the 2nd-smallest bootstrap minimum (adjusted p < 0.025 needs rank <= 1).
             Budget, not tuning: a 28-item 2PL fit took 7-19 s on the dry run (load ~20 on 4 cores). Budget, not tuning: a 28-item
             2PL fit takes ~3 s, so own calibrations for 60 replicates would take ~10 core-hours.
FLOOR PASSES latent test: size (PUB, H_PUB rejected at 0.05) <= 0.10, power at MIX 0.10 >= 0.80,
             and direction power (PUB, H_REV rejected at 0.05) >= 0.80.
             each instrument: AGREES in >= 0.80 of PUB replicates, and AGREES in <= 0.10 of ONE and
             <= 0.10 of REV replicates (REVERSED in REV reported).

VERDICTS (exactly these strings)
REFERENCE    UNANSWERABLE           the latent floor fails
             HIERARCHY FOUND        floor passes, H_PUB not rejected (p >= 0.05) and H_REV rejected
                                    (p < 0.05)
             HIERARCHY REJECTED     floor passes and H_PUB rejected (p < 0.05)
             DIRECTION UNRESOLVED   floor passes, neither rejected
INSTRUMENT   UNANSWERABLE           that instrument's floor fails: it cannot see a planted latent
                                    hierarchy of ECPE's shape, or reads one where none is; a
                                    detection-floor statement from simulation
             AGREES                 floor passes and the real reading is AGREES
             REVERSED               floor passes and the real reading is REVERSED
             MISSES                 floor passes and the real reading is MISSES: a detection-floor
                                    statement about that instrument on real data with a known
                                    reference
CONTROL      INFORMATIVE when the reference is HIERARCHY FOUND; otherwise CONTROL UNINFORMATIVE, and
             the instrument readings are reported as descriptions only.

WHAT EACH OUTCOME MEANS FOR PAPER II (fixed now)
  IITA UNANSWERABLE or MISSES, reference FOUND: F6's "IITA against fixed margins could not have seen
      a dependency" is confirmed on real data with an established hierarchy; cite as such.
  IITA AGREES: IITA can see a latent hierarchy at assessment shape; F6's null on platform corpora is a
      property of those corpora, and "could not have" narrows to them.
  PAIRSCAN MISSES/UNANSWERABLE: the scan's positives (8 of 15 sets) are local dependence beyond one
      trait, not hierarchy detection, and its nulls do not exclude a hierarchy; Paper II says so.
  PAIRSCAN AGREES: the scan sees a latent hierarchy here; its direction is still difficulty order
      (iita_pairscan CHANGE 1), so agreement is in the deficit sign, not in orientation.
  INTERACTION AGREES: the interaction test recovers a latent conjunctive hierarchy on assessment data,
      a positive control for F1's AND result. MISSES/UNANSWERABLE: F1's AND result has no latent-level
      positive control here; its validation rests on the planted floor alone.
  REFERENCE not FOUND: the control is uninformative and Paper II may not cite ECPE as a positive
      control; the T&B result is then not reproduced by this implementation, which is reported.

WHAT IT CANNOT SAY. ECPE is a 28-item grammar test, not a platform log: agreement here does not show
the instruments work on fixed-order platform data, only whether they can see a latent hierarchy when
one is there. The skill grain uses only single-skill items (4-10 per skill), so mastery is misclassified
at a rate this design does not estimate. The hierarchy's order comes from a secondary source.

ORDER        fit (real; params written, no LR computed) -> floor (synthetic, written) -> real reference
             test -> real instrument readings -> verdicts.

RESULTS (2026-10-07; out/floor.json, out/result.json; README.md has the full account)
  floor     latent test PASSES: H_PUB rejected in 0 of 60 PUB replicates; power 40/40 at MIX 0.10,
            40/40 at ONE, 30/30 at MIX 0.05; H_REV rejected in 60/60 PUB replicates (B = 49).
            Instruments FAIL (AGREES in PUB / ONE / REV): IITA skill grain 0.02 / 0.01 / 0.00 (200 a
            world; band degenerate in 0.32 of PUB); pairscan item grain 0.25 / 0.10 / 0.00 (20 a world;
            REV reads REVERSED 1.00); interaction skill grain 0.245 / 0.04 / 0.24 (published triple
            unscored in 0.29 of PUB by MIN_CELL). Matched-phi one-trait lambda hits 0.999 with
            forbidden mass 2e-14: on ECPE's correlation a linear hierarchy is a one-trait Guttman scale.
  real      HIERARCHY FOUND, narrowly: H_PUB LR 25.51, p = 0.068 (33 of 500 bootstrap LRs at or
            above; Clopper-Pearson [0.046, 0.091], straddling 0.05); H_REV LR 426.60 and the other
            four orders 94.13-413.48, all p = 0.002 (none of 500 reached them). Saturated forbidden
            mass 0.041 [0.017, 0.091] (200 examinee resamples; boundary estimate, not a test).
            IITA, pairscan, interaction: UNANSWERABLE (floors fail). Descriptive real readings: IITA
            skill grain 3 implications inside [2, 3], relation includes cohesive -> lexical
            (difficulty order, against H_PUB); pairscan one isolated pair E19-E28 (same level);
            interaction published triple -0.016 (SE 0.097) UNKNOWN, reversed -0.107 CONTRADICTED.
  control   INFORMATIVE.

    python3 ecpe_control.py --phase check     # EM recovery on an arbitrary synthetic world, no corpus
    python3 ecpe_control.py --phase fit       # out/fit.json
    python3 ecpe_control.py --phase floor     # out/floor.json
    python3 ecpe_control.py --phase real      # out/result.json

CHANGES (dated; any change after the design commit is listed here, with its reason)
  1. 2026-10-07, after the design commit (c14cb59) and the real-data parameter fit, before any floor
     or real-data statistic was seen. The first floor run (PUB 100, MIX 0.10 50, ONE 50, MIX 0.05 50,
     B = 99) was killed by the session's 2-hour limit on background commands with nothing written,
     because results were written only at the end. On the real-fit worlds the saturated refit takes
     ~600 EM iterations (0.5 s), not the ~85 of the dry-run world, so a bootstrap draw costs ~0.55 s
     and that budget needed ~6 worker-hours. Cut to PUB 60, MIX 0.10 40, ONE 40, MIX 0.05 30 and
     B = 49 (~2.2 worker-hours); each finished job is now checkpointed so a killed run resumes. The
     thresholds are unchanged. At B = 49 the smallest attainable p is 0.02, so a rejection at 0.05 is
     still possible; the size estimate over 60 replicates has a binomial sd of ~0.03 at 0.05.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies/identifiability/learning-structure"))
sys.path.insert(0, str(ROOT / "studies/identifiability/conjunctive"))
import iita_dense as dense  # noqa: E402  (iita_count, null_counts, band, tail_of)
import iita_pairscan as ps  # noqa: E402  (fit_2pl, calibrate, score, classify, standardise, plants_job, fp_job)
import nulls  # noqa: E402  (fixed_margin_draws, item grain)
from iita import iita_from_counts  # noqa: E402
import stage3_interaction as s3  # noqa: E402  (score, bh, norm_sf, empirical_null, MIN_MEANINGFUL)
from shared.paths import data_path  # noqa: E402
from shared.direction import reversed_arrow  # noqa: E402

SEED = 20261007
J, KS, NC = 28, 3, 8                     # items, skills, attribute profiles
OUT = HERE / "out"
WORKERS = 3
EM_TOL, EM_MAXIT, PMIN = 1e-7, 20000, 1e-6
EPS_FORBID = 0.01
NR_REAL, NR_FLOOR = 20, 4
B_REAL, B_FLOOR, B_NONPAR = 500, 49, 200
ALPHA = 0.05
R_IITA, R_IITA_ITEM = 500, 200
R_PS_REAL, R_PS_FLOOR = 200, 100
REPS_LRT = dict(PUB=60, MIX10=40, ONE=40, MIX05=30)
REPS_SKILL, REPS_PS, OWN_CAL_CHECK = 200, 20, 1
FLOOR_SIZE, FLOOR_POWER, FLOOR_DETECT, FLOOR_FP = 0.10, 0.80, 0.80, 0.10

# profiles: class c has skill k mastered iff bit k of c is set (k = 0 skill1, 1 skill2, 2 skill3)
CL = np.array([[(c >> k) & 1 for k in range(KS)] for c in range(NC)])
PUB_ORDER = (2, 1, 0)                    # bottom -> top: skill3 -> skill2 -> skill1
REV_ORDER = (0, 1, 2)
H_PUB = {(2, 1), (1, 0), (2, 0)}         # (prerequisite, dependant), transitively closed
H_REV = {(b, a) for a, b in H_PUB}

# iita_pairscan reads K and OFF as module globals; ECPE's set is the 28 items
ps.K = J
ps.OFF = ~np.eye(J, dtype=bool)

REF_VERDICTS = ("UNANSWERABLE", "HIERARCHY FOUND", "HIERARCHY REJECTED", "DIRECTION UNRESOLVED")
INST_VERDICTS = ("UNANSWERABLE", "AGREES", "REVERSED", "MISSES")


def allowed(order) -> np.ndarray:
    """Profiles permitted by a linear chain order[0] -> order[1] -> order[2] (bottom to top)."""
    ok = np.ones(NC, bool)
    for t in range(1, len(order)):
        ok &= CL[:, order[t]] <= CL[:, order[t - 1]]
    return ok


def chain_edges(order) -> set:
    return {(order[a], order[b]) for a in range(len(order)) for b in range(a + 1, len(order))}


# ----------------------------------------------------------------------------- data

def load_ecpe():
    d = data_path("ECPE_DIR")
    import csv
    with open(d / "ecpe_qmatrix.csv") as f:
        rows = list(csv.DictReader(f))
    Q = np.array([[int(r[f"skill{k + 1}"]) for k in range(KS)] for r in rows])
    items = [r["item"] for r in rows]
    with open(d / "ecpe_responses.csv") as f:
        rd = csv.reader(f)
        head = next(rd)
        assert head[1:] == items, "response columns do not match the Q-matrix items"
        X = np.array([[int(v) for v in r[1:]] for r in rd], dtype=np.int8)
    assert X.shape == (2922, J) and set(np.unique(X)) <= {0, 1}, X.shape
    return X.astype(bool), Q


def design(Q):
    """Item -> group index per profile, single-skill items, item levels; asserts positivity."""
    G = np.zeros((J, NC), int)
    for j in range(J):
        a = np.flatnonzero(Q[j])
        for c in range(NC):
            G[j, c] = sum(int(CL[c, x]) << t for t, x in enumerate(a))
    single = {k: [j for j in range(J) if Q[j].sum() == 1 and Q[j, k]] for k in range(KS)}
    assert all(single[k] for k in range(KS)), "a skill has no single-skill item: hierarchy untestable"
    level = np.where(Q[:, 0] == 1, 3, np.where(Q[:, 1] == 1, 2, 1))
    ngroups = 2 ** Q.sum(1)
    return dict(Q=Q, G=G, single=single, level=level, ngroups=ngroups)


# ----------------------------------------------------------------------------- the DCM by EM

def compress(X):
    u, cnt = np.unique(X.astype(np.int8), axis=0, return_counts=True)
    return u.astype(float), cnt.astype(float)


def item_probs(Pg, G):
    return np.clip(np.take_along_axis(Pg, G, 1), PMIN, 1 - PMIN)       # (J, NC)


def em(U, cnt, G, allow, pi, Pg):
    pi = np.where(allow, pi, 0.0)
    pi = pi / pi.sum()
    Pg = Pg.copy()
    prev = -np.inf
    jj = np.repeat(np.arange(J)[:, None], NC, 1)
    with np.errstate(divide="ignore"):
        for it in range(EM_MAXIT):
            P = item_probs(Pg, G)
            L = U @ np.log(P) + (1 - U) @ np.log1p(-P) + np.log(pi)
            m = L.max(1, keepdims=True)
            post = np.exp(L - m)
            s = post.sum(1)
            ll = float((cnt * (m[:, 0] + np.log(s))).sum())
            if ll - prev < EM_TOL:
                return dict(ll=ll, pi=pi, Pg=Pg, iters=it, converged=True)
            prev = ll
            post *= (cnt / s)[:, None]
            N = post.sum(0)
            pi = N / N.sum()
            R1 = U.T @ post
            num, den = np.zeros((J, 4)), np.zeros((J, 4))
            np.add.at(num, (jj, G), R1)
            np.add.at(den, (jj, G), np.broadcast_to(N, (J, NC)))
            upd = den > 1e-8
            Pg[upd] = num[upd] / den[upd]
    return dict(ll=ll, pi=pi, Pg=Pg, iters=EM_MAXIT, converged=False)


def random_start(rng, D, allow):
    pi = rng.dirichlet(np.ones(NC)) * allow
    Pg = np.full((J, 4), 0.5)
    for j in range(J):
        lo, hi = rng.uniform(0.1, 0.35), rng.uniform(0.65, 0.9)
        k = int(D["Q"][j].sum())
        for g in range(2 ** k):
            Pg[j, g] = np.clip(lo + (hi - lo) * bin(g).count("1") / k + rng.normal(0, 0.05), 0.02, 0.98)
    return pi / pi.sum(), Pg


def with_eps(fit):
    pi = fit["pi"] + EPS_FORBID * (fit["pi"] == 0)
    return pi / pi.sum(), fit["Pg"]


def fit_model(U, cnt, D, allow, rng, n_random, warm=()):
    best = None
    starts = list(warm) + [random_start(rng, D, allow) for _ in range(n_random)]
    for pi0, Pg0 in starts:
        f = em(U, cnt, D["G"], allow, pi0, Pg0)
        if best is None or f["ll"] > best["ll"]:
            best = f
    return best


def simulate(pi, Pg, D, n, rng):
    P = item_probs(Pg, D["G"])                       # (J, NC)
    cls = rng.choice(NC, n, p=pi / pi.sum())
    return rng.random((n, J)) < P[:, cls].T


def lrt(X, D, order, rng, B, n_random, warm_h=None, sat_fit=None):
    """Parametric-bootstrap LRT of the chain `order` against the saturated model."""
    U, cnt = compress(X)
    allow = allowed(order)
    h = fit_model(U, cnt, D, allow, rng, n_random, warm=[warm_h] if warm_h else [])
    if sat_fit is None:
        sat_fit = fit_model(U, cnt, D, np.ones(NC, bool), rng, n_random, warm=[with_eps(h)])
    elif sat_fit["ll"] < h["ll"]:
        sat_fit = fit_model(U, cnt, D, np.ones(NC, bool), rng, 0, warm=[with_eps(h)])
    lr = max(0.0, 2 * (sat_fit["ll"] - h["ll"]))
    boot = np.empty(B)
    for b in range(B):
        Xb = simulate(h["pi"], h["Pg"], D, len(X), rng)
        Ub, cb = compress(Xb)
        hb = fit_model(Ub, cb, D, allow, rng, 0, warm=[(h["pi"], h["Pg"])])
        sb = fit_model(Ub, cb, D, np.ones(NC, bool), rng, 0, warm=[with_eps(hb)])
        boot[b] = max(0.0, 2 * (sb["ll"] - hb["ll"]))
    p = (1 + int((boot >= lr).sum())) / (B + 1)
    return dict(lr=lr, p=p, ll_hier=h["ll"], ll_sat=sat_fit["ll"], boot_q95=float(np.quantile(boot, 0.95)),
                boot_mean=float(boot.mean()), hier=h, sat=sat_fit)


def forbidden_mass(pi, order=PUB_ORDER) -> float:
    return float(pi[~allowed(order)].sum())


def monotone_violations(fit, D) -> int:
    v = 0
    for j in range(J):
        k = int(D["Q"][j].sum())
        for g in range(2 ** k):
            for h in range(2 ** k):
                if g != h and (g & h) == g and fit["Pg"][j, g] > fit["Pg"][j, h] + 1e-9:
                    v += 1
    return v


def monotone_project(Pg, D):
    out = Pg.copy()
    for j in range(J):
        k = int(D["Q"][j].sum())
        vals = Pg[j, :2 ** k]
        lo, hi = vals.min(), vals.max()
        out[j, 0], out[j, 2 ** k - 1] = lo, hi
        for g in range(1, 2 ** k - 1):
            out[j, g] = min(max(Pg[j, g], lo), hi)
    return out


# ----------------------------------------------------------------------------- synthetic worlds

def margins(pi):
    return np.array([pi[CL[:, k] == 1].sum() for k in range(KS)])


def mean_phi(pi):
    m = margins(pi)
    out = []
    for a in range(KS):
        for b in range(a + 1, KS):
            p11 = pi[(CL[:, a] == 1) & (CL[:, b] == 1)].sum()
            out.append((p11 - m[a] * m[b]) / math.sqrt(m[a] * (1 - m[a]) * m[b] * (1 - m[b])))
    return float(np.mean(out))


def one_trait(m, lam):
    x, w = np.polynomial.hermite_e.hermegauss(61)
    w = w / w.sum()
    tau = norm.ppf(1 - m)
    p = 1 - norm.cdf((tau[None, :] - lam * x[:, None]) / math.sqrt(1 - lam ** 2))   # (nodes, KS)
    pi = np.zeros(NC)
    for c in range(NC):
        pi[c] = float((w * np.prod(np.where(CL[c] == 1, p, 1 - p), axis=1)).sum())
    return pi / pi.sum()


def worlds(pi_pub):
    m = margins(pi_pub)
    rev = np.zeros(NC)
    mapping = {0: 0, 4: 1, 6: 3, 7: 7}      # 000->000, 001->100, 011->110, 111->111
    for a, b in mapping.items():
        rev[b] = pi_pub[a]
    target = mean_phi(pi_pub)
    lo, hi = 0.0, 0.999
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if mean_phi(one_trait(m, mid)) < target else (lo, mid)
    lam_phi = (lo + hi) / 2
    lo, hi = 0.0, 0.999
    assert forbidden_mass(one_trait(m, 0.0)) > 0.10, "independent skills hold less than 0.10 forbidden mass"
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if forbidden_mass(one_trait(m, mid)) > 0.10 else (lo, mid)
    lam = (lo + hi) / 2
    one = one_trait(m, lam)
    indep = np.array([np.prod(np.where(CL[c] == 1, m, 1 - m)) for c in range(NC)])
    out = dict(PUB=pi_pub, REV=rev, ONE=one)
    for f, name in ((0.10, "MIX10"), (0.05, "MIX05")):
        w = f / forbidden_mass(indep)
        assert w <= 1, "independent world has too little forbidden mass for this mixture"
        out[name] = (1 - w) * pi_pub + w * indep
    info = dict(lambda_one=lam, mean_phi_pub=target, mean_phi_one=mean_phi(one),
                lambda_matched_phi=lam_phi, forbidden_mass_matched_phi=forbidden_mass(one_trait(m, lam_phi)),
                margins_pub=m.tolist(), margins_one=margins(one).tolist(),
                forbidden_mass={k: forbidden_mass(v) for k, v in out.items()},
                pi={k: v.tolist() for k, v in out.items()})
    return out, info


# ----------------------------------------------------------------------------- the instruments

def skill_grain(X, D):
    return np.stack([X[:, D["single"][k]].mean(1) >= 0.5 for k in range(KS)], 1)


def read_iita(Hs, rng, R=R_IITA):
    obs, rel = dense.iita_count(Hs, relation=True)
    null = dense.null_counts(Hs, R, rng)
    lo, hi = dense.band(null)
    degenerate = lo == hi
    tail = None if degenerate else dense.tail_of(obs, lo, hi)
    rel = {(int(a), int(b)) for a, b in rel}
    d = len(rel & H_PUB) - len(rel & H_REV)
    reading = "AGREES" if tail and d > 0 else "REVERSED" if tail and d < 0 else "MISSES"
    return dict(count=obs, band=[lo, hi], null_median=float(np.median(null)), degenerate=degenerate,
                tail=tail, relation=sorted(rel), d=d, reading=reading)


def read_interaction(Hs):
    rows = []
    for dep in range(KS):
        a, b = [k for k in range(KS) if k != dep]
        sc = s3.score(Hs[:, dep].astype(float), Hs[:, a], Hs[:, b])
        rows.append(dict(dependant=dep, parents=[a, b], **(sc or dict(unscored=True))))
    scored = [r for r in rows if "z" in r]
    if scored:
        p = np.array([float(s3.norm_sf(r["z"])) for r in scored])
        keep = s3.bh(p, s3.FDR_Q)
        for i, r in enumerate(scored):
            r["p_one_sided"] = float(p[i])
            r["ci_hi"] = r["interaction"] + 1.96 * r["se"]
            r["verdict"] = ("SUPPORTED" if keep[i] and r["interaction"] > 0
                            else "CONTRADICTED" if r["ci_hi"] < s3.MIN_MEANINGFUL else "UNKNOWN")
    pub, rev = rows[0], rows[2]          # dependant skill1 (H_PUB top); dependant skill3 (H_REV top)
    def beats(x, y):
        return x.get("verdict") == "SUPPORTED" and ("z" not in y or y["interaction"] < x["interaction"])
    reading = "AGREES" if beats(pub, rev) else "REVERSED" if beats(rev, pub) else "MISSES"
    return dict(triples=rows, reading=reading)


def read_pairscan(Z, Uz, cal, level):
    fl = ps.classify(Z, Uz, cal)
    def tally(only_iso):
        best = {}
        for i, j, zij, zji, p, asym, iso in fl["pairs"]:
            if only_iso and not iso:
                continue
            if level[i] == level[j]:
                continue
            key = (min(i, j), max(i, j))
            if key not in best or zij < best[key][2]:
                best[key] = (i, j, zij)
        agree = sum(1 for i, j, _ in best.values() if level[i] < level[j])
        return agree, len(best) - agree
    ai, di = tally(True)
    aa, da = tally(False)
    reading = "AGREES" if ai > di else "REVERSED" if di > ai else "MISSES"
    return dict(reading=reading, iso_agree=ai, iso_disagree=di, any_agree=aa, any_disagree=da,
                fires_isolated=fl["isolated"], fires_any=fl["any"], n_sig_pairs=len(fl["pairs"]),
                reading_any="AGREES" if aa > da else "REVERSED" if da > aa else "MISSES")


# ----------------------------------------------------------------------------- phases

def phase_check():
    """EM recovery on an arbitrary ECPE-shaped synthetic world (no corpus read)."""
    rng = np.random.default_rng(SEED)
    Q = np.array([[1, 1, 0], [0, 1, 0], [1, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1], [1, 0, 1], [0, 1, 0],
                  [0, 0, 1], [1, 0, 0], [1, 0, 1], [1, 0, 1], [1, 0, 0], [1, 0, 0], [0, 0, 1], [1, 0, 1],
                  [0, 1, 1], [0, 0, 1], [0, 0, 1], [1, 0, 1], [1, 0, 1], [0, 0, 1], [0, 1, 0], [0, 1, 0],
                  [1, 0, 0], [0, 0, 1], [1, 0, 0], [0, 0, 1]])   # the CDM Rd Q-matrix (design, public)
    D = design(Q)
    pi = np.zeros(NC)
    pi[[0, 4, 6, 7]] = [0.3, 0.15, 0.15, 0.4]
    Pg = np.zeros((J, 4))
    for j in range(J):
        k = int(Q[j].sum())
        for g in range(2 ** k):
            Pg[j, g] = 0.25 + 0.6 * bin(g).count("1") / k
    X = simulate(pi, Pg, D, 2922, rng)
    t = time.time()
    r = lrt(X, D, PUB_ORDER, rng, 49, NR_FLOOR)
    rr = lrt(X, D, REV_ORDER, rng, 49, NR_FLOOR)
    out = dict(true_pi=pi.tolist(), hier_pi=r["hier"]["pi"].tolist(), sat_pi=r["sat"]["pi"].tolist(),
               pub_lr=r["lr"], pub_p=r["p"], rev_lr=rr["lr"], rev_p=rr["p"],
               max_abs_item_err=float(np.max(np.abs(item_probs(r["hier"]["Pg"], D["G"])[:, [0, 4, 6, 7]]
                                                    - item_probs(Pg, D["G"])[:, [0, 4, 6, 7]]))),
               seconds=time.time() - t)
    print(json.dumps(out, indent=1))


def lrt_job(args):
    world, rep, pi, Pg, Dq = args
    D = design(np.array(Dq))
    rng = np.random.default_rng([SEED, 1, list(REPS_LRT).index(world), rep])
    X = simulate(np.array(pi), np.array(Pg), D, 2922, rng)
    r = lrt(X, D, PUB_ORDER, rng, B_FLOOR, NR_FLOOR)
    out = dict(world=world, rep=rep, lr=r["lr"], p=r["p"], reject=r["p"] < ALPHA)
    if world == "PUB":
        rr = lrt(X, D, REV_ORDER, rng, B_FLOOR, NR_FLOOR, sat_fit=r["sat"])
        out.update(rev_lr=rr["lr"], rev_p=rr["p"], rev_reject=rr["p"] < ALPHA)
    return out


def skill_job(args):
    world, rep, pi, Pg, Dq = args
    D = design(np.array(Dq))
    rng = np.random.default_rng([SEED, 2, ["PUB", "REV", "ONE"].index(world), rep])
    X = simulate(np.array(pi), np.array(Pg), D, 2922, rng)
    Hs = skill_grain(X, D)
    return dict(world=world, rep=rep, iita=read_iita(Hs, rng), interaction=read_interaction(Hs))


def ps_world_job(args):
    world, pi, Pg, Dq = args
    D = design(np.array(Dq))
    wi = ["PUB", "REV", "ONE"].index(world)
    rng = np.random.default_rng([SEED, 3, wi])
    Xs = [simulate(np.array(pi), np.array(Pg), D, 2922, rng) for _ in range(REPS_PS)]
    cal = ps.calibrate(Xs[0], np.random.SeedSequence([SEED, 4, wi]), R_PS_FLOOR)
    reads = []
    for r, X in enumerate(Xs):
        Z, Uz, ok = ps.standardise(X, cal, init=cal["th"])
        reads.append(dict(rep=r, converged=ok, **read_pairscan(Z, Uz, cal, D["level"])))
    return dict(world=world, calibration=dict(converged=cal["converged"], boot_nonconverged=cal["boot_nonconverged"],
                                              critical=ps.critical(cal["tstar"]), boot_rates=cal["boot_rates"]),
                reads=reads)


def ps_own_job(args):
    world, rep, pi, Pg, Dq = args
    D = design(np.array(Dq))
    wi = ["PUB", "REV", "ONE"].index(world)
    rng = np.random.default_rng([SEED, 3, wi])
    Xs = [simulate(np.array(pi), np.array(Pg), D, 2922, rng) for _ in range(rep + 1)]
    X = Xs[rep]
    cal = ps.calibrate(X, np.random.SeedSequence([SEED, 5, wi, rep]), R_PS_FLOOR)
    z, zu = ps.residuals(X, cal["th"])
    Z, Uz = (z - cal["mu"]) / cal["sd"], (zu - cal["mu_u"]) / cal["sd_u"]
    return dict(world=world, rep=rep, critical=ps.critical(cal["tstar"]), **read_pairscan(Z, Uz, cal, D["level"]))


def job_key(tagged) -> str:
    kind, args = tagged
    return f"{kind}:{args[0]}" if kind == "psw" else f"{kind}:{args[0]}:{args[1]}"


def run_tagged(tagged):
    kind, args = tagged
    fn = dict(psw=ps_world_job, lrt=lrt_job, skill=skill_job, own=ps_own_job)[kind]
    return job_key(tagged), json.loads(json.dumps(fn(args), default=float))


def phase_fit():
    X, Q = load_ecpe()
    D = design(Q)
    rng = np.random.default_rng([SEED, 0])
    U, cnt = compress(X)
    hier = {}
    for order in [(2, 1, 0), (0, 1, 2), (2, 0, 1), (1, 0, 2), (1, 2, 0), (0, 2, 1)]:
        hier[order] = fit_model(U, cnt, D, allowed(order), rng, NR_REAL)
    sat = fit_model(U, cnt, D, np.ones(NC, bool), rng, NR_REAL, warm=[with_eps(h) for h in hier.values()])
    Pw = monotone_project(sat["Pg"], D)
    out = dict(
        n=int(len(X)), items=J, patterns=int(len(U)),
        single_skill_items={f"skill{k + 1}": [f"E{j + 1}" for j in D["single"][k]] for k in range(KS)},
        saturated=dict(pi=sat["pi"].tolist(), Pg=sat["Pg"].tolist(), iters=sat["iters"], converged=sat["converged"],
                       monotone_violations=monotone_violations(sat, D)),
        hierarchical_pub=dict(pi=hier[PUB_ORDER]["pi"].tolist(), Pg=hier[PUB_ORDER]["Pg"].tolist(),
                              iters=hier[PUB_ORDER]["iters"], converged=hier[PUB_ORDER]["converged"]),
        world_item_params=Pw.tolist(), Q=Q.tolist(),
        note="Parameters only. No likelihood-ratio statistic is computed in this phase.")
    OUT.mkdir(exist_ok=True)
    (OUT / "fit.json").write_text(json.dumps(out, indent=1))
    print(f"fit written: n={len(X)}, patterns={len(U)}, sat converged={sat['converged']}")


def phase_floor():
    fit = json.loads((OUT / "fit.json").read_text())
    Q = fit["Q"]
    W, info = worlds(np.array(fit["hierarchical_pub"]["pi"]))
    Pw = fit["world_item_params"]
    t0 = time.time()
    jobs_lrt = [(w, r, W[w].tolist(), Pw, Q) for w, n in REPS_LRT.items() for r in range(n)]
    jobs_skill = [(w, r, W[w].tolist(), Pw, Q) for w in ("PUB", "REV", "ONE") for r in range(REPS_SKILL)]
    jobs_psw = [(w, W[w].tolist(), Pw, Q) for w in ("PUB", "REV", "ONE")]
    jobs_own = [(w, r, W[w].tolist(), Pw, Q) for w in ("PUB", "REV", "ONE") for r in range(OWN_CAL_CHECK)]
    tagged = ([("psw", j) for j in jobs_psw] + [("lrt", j) for j in jobs_lrt]
              + [("skill", j) for j in jobs_skill] + [("own", j) for j in jobs_own])
    ckpt = OUT / ".floor-progress.jsonl"          # synthetic aggregates; deleted when the floor completes
    done = {}
    if ckpt.exists():
        for line in ckpt.read_text().splitlines():
            rec = json.loads(line)
            done[rec["key"]] = rec["result"]
    todo = [(i, t) for i, t in enumerate(tagged) if job_key(t) not in done]
    print(f"floor: {len(done)} jobs checkpointed, {len(todo)} to run", flush=True)
    with Pool(WORKERS) as pool, open(ckpt, "a") as fh:
        for n, (key, res) in enumerate(pool.imap_unordered(run_tagged, [t for _, t in todo]), 1):
            done[key] = res
            fh.write(json.dumps(dict(key=key, result=res), default=float) + "\n")
            fh.flush()
            if n % 25 == 0 or n == len(todo):
                print(f"floor: {n}/{len(todo)} jobs, {time.time() - t0:.0f}s", flush=True)
    res_of = lambda kind: [done[job_key(t)] for t in tagged if t[0] == kind]
    lrt_res, skill_res, psw, own = res_of("lrt"), res_of("skill"), res_of("psw"), res_of("own")
    lat = {}
    for w in REPS_LRT:
        rs = [r for r in lrt_res if r["world"] == w]
        lat[w] = dict(reps=len(rs), reject_rate=float(np.mean([r["reject"] for r in rs])),
                      lr_median=float(np.median([r["lr"] for r in rs])))
        if w == "PUB":
            lat[w]["rev_reject_rate"] = float(np.mean([r["rev_reject"] for r in rs]))
    lat_pass = (lat["PUB"]["reject_rate"] <= FLOOR_SIZE and lat["MIX10"]["reject_rate"] >= FLOOR_POWER
                and lat["PUB"]["rev_reject_rate"] >= FLOOR_POWER)
    inst = {}
    for name in ("iita", "interaction"):
        rates = {}
        for w in ("PUB", "REV", "ONE"):
            rs = [r[name]["reading"] for r in skill_res if r["world"] == w]
            rates[w] = {v: rs.count(v) / len(rs) for v in ("AGREES", "REVERSED", "MISSES")}
        extra = {}
        if name == "iita":
            for w in ("PUB", "REV", "ONE"):
                rs = [r["iita"] for r in skill_res if r["world"] == w]
                extra[w] = dict(degenerate=float(np.mean([r["degenerate"] for r in rs])),
                                beyond=float(np.mean([r["tail"] is not None for r in rs])),
                                d_positive=float(np.mean([r["d"] > 0 for r in rs])))
        else:
            for w in ("PUB", "REV", "ONE"):
                rs = [r["interaction"]["triples"] for r in skill_res if r["world"] == w]
                extra[w] = dict(pub_unscored=float(np.mean(["z" not in t[0] for t in rs])),
                                pub_interaction_median=float(np.median([t[0].get("interaction", np.nan) for t in rs])),
                                rev_interaction_median=float(np.median([t[2].get("interaction", np.nan) for t in rs])))
        inst[name] = dict(rates=rates, detail=extra)
    rates = {}
    for res in psw:
        rs = [r["reading"] for r in res["reads"]]
        ra = [r["reading_any"] for r in res["reads"]]
        rates[res["world"]] = {v: rs.count(v) / len(rs) for v in ("AGREES", "REVERSED", "MISSES")}
        rates[res["world"]]["any_AGREES"] = ra.count("AGREES") / len(ra)
        rates[res["world"]]["fires_isolated"] = float(np.mean([r["fires_isolated"] for r in res["reads"]]))
        rates[res["world"]]["fires_any"] = float(np.mean([r["fires_any"] for r in res["reads"]]))
    shared_vs_own = []
    for o in own:
        sh = next(r for res in psw if res["world"] == o["world"] for r in res["reads"] if r["rep"] == o["rep"])
        shared_vs_own.append(dict(world=o["world"], rep=o["rep"], shared=sh["reading"], own=o["reading"],
                                  shared_any=sh["reading_any"], own_any=o["reading_any"],
                                  own_critical=o["critical"]))
    inst["pairscan"] = dict(rates=rates, calibrations={r["world"]: r["calibration"] for r in psw},
                            shared_vs_own=shared_vs_own)
    for name, v in inst.items():
        r = v["rates"]
        v["floor_passes"] = bool(r["PUB"]["AGREES"] >= FLOOR_DETECT and r["ONE"]["AGREES"] <= FLOOR_FP
                                 and r["REV"]["AGREES"] <= FLOOR_FP)
    out = dict(worlds=info, latent=dict(results=lat, floor_passes=bool(lat_pass)), instruments=inst,
               seconds=time.time() - t0,
               thresholds=dict(size=FLOOR_SIZE, power=FLOOR_POWER, detect=FLOOR_DETECT, fp=FLOOR_FP),
               reps=dict(lrt=REPS_LRT, skill=REPS_SKILL, pairscan=REPS_PS, B=B_FLOOR))
    (OUT / "floor.json").write_text(json.dumps(out, indent=1, default=float))
    ckpt.unlink()
    print(json.dumps(dict(latent=out["latent"], **{k: dict(rates=v["rates"], passes=v["floor_passes"])
                                                    for k, v in inst.items()}), indent=1, default=float))


def nonpar_job(args):
    seed, sat_pi, sat_Pg, Q = args
    X, _ = load_ecpe()
    D = design(np.array(Q))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(X), len(X))
    U, cnt = compress(X[idx])
    f = fit_model(U, cnt, D, np.ones(NC, bool), rng, 2, warm=[(np.array(sat_pi), np.array(sat_Pg))])
    return forbidden_mass(f["pi"])


def real_lrt_job(args):
    order, Q = args
    X, _ = load_ecpe()
    D = design(np.array(Q))
    fit = json.loads((OUT / "fit.json").read_text())
    sat = dict(ll=None, pi=np.array(fit["saturated"]["pi"]), Pg=np.array(fit["saturated"]["Pg"]))
    U, cnt = compress(X)
    rng = np.random.default_rng([SEED, 6, *order])
    satf = fit_model(U, cnt, D, np.ones(NC, bool), rng, 0, warm=[(sat["pi"], sat["Pg"])])
    r = lrt(X, D, tuple(order), rng, B_REAL, NR_REAL, sat_fit=satf)
    return dict(order=list(order), edges=sorted(chain_edges(order)), lr=r["lr"], p=r["p"],
                ll_hier=r["ll_hier"], ll_sat=r["ll_sat"], boot_q95=r["boot_q95"], boot_mean=r["boot_mean"],
                hier_pi=r["hier"]["pi"].tolist())


def real_ps_job(args):
    kind, X, seed = args
    if kind == "cal":
        return ps.calibrate(X, np.random.SeedSequence([SEED, 7]), R_PS_REAL)
    if kind == "fp":
        cal, k = seed
        ps.FP_REPS = 1                     # the two fitted-model simulations run as two parallel jobs
        return ps.fp_job((cal, np.random.SeedSequence([SEED, 8, k]), R_PS_FLOOR))[0]
    raise ValueError(kind)


def phase_real():
    fit = json.loads((OUT / "fit.json").read_text())
    floor = json.loads((OUT / "floor.json").read_text())
    X, Q = load_ecpe()
    D = design(Q)
    t0 = time.time()
    orders = [(2, 1, 0), (0, 1, 2), (2, 0, 1), (1, 0, 2), (1, 2, 0), (0, 2, 1)]
    with Pool(WORKERS) as pool:
        a_cal = pool.apply_async(real_ps_job, (("cal", X, None),))
        lrts = pool.map(real_lrt_job, [(o, Q.tolist()) for o in orders])
        print(f"real LRTs done {time.time() - t0:.0f}s", flush=True)
        seeds = np.random.SeedSequence([SEED, 9]).spawn(B_NONPAR)
        fm = pool.map(nonpar_job, [(s, fit["saturated"]["pi"], fit["saturated"]["Pg"], Q.tolist()) for s in seeds],
                      chunksize=10)
        cal = a_cal.get()
        print(f"pairscan calibration done {time.time() - t0:.0f}s", flush=True)
        a_fp = [pool.apply_async(real_ps_job, (("fp", None, (cal, k)),)) for k in range(2)]
        plants = ps.plants_job((X, cal, (SEED, 10)))
        fp = [a.get() for a in a_fp]
    # reference
    pub = next(r for r in lrts if tuple(r["order"]) == PUB_ORDER)
    rev = next(r for r in lrts if tuple(r["order"]) == REV_ORDER)
    lat_pass = floor["latent"]["floor_passes"]
    if not lat_pass:
        ref = "UNANSWERABLE"
    elif pub["p"] < ALPHA:
        ref = "HIERARCHY REJECTED"
    elif rev["p"] < ALPHA:
        ref = "HIERARCHY FOUND"
    else:
        ref = "DIRECTION UNRESOLVED"
    sat_pi = np.array(fit["saturated"]["pi"])
    # instruments
    rng = np.random.default_rng([SEED, 11])
    Hs = skill_grain(X, D)
    iita_r = read_iita(Hs, rng)
    inter_r = read_interaction(Hs)
    nullchk = []
    for t in inter_r["triples"]:
        if "z" in t:
            a, b = t["parents"]
            en = s3.empirical_null(Hs[:, t["dependant"]].astype(float), Hs[:, a], Hs[:, b], rng, draws=200)
            nullchk.append(dict(dependant=t["dependant"], analytic_se=t["se"],
                                deranged_sd=en["null_sd"] if en else None,
                                ratio=(en["null_sd"] / t["se"]) if en else None))
    z, zu = ps.residuals(X, cal["th"])
    Z, Uz = (z - cal["mu"]) / cal["sd"], (zu - cal["mu_u"]) / cal["sd_u"]
    ps_r = read_pairscan(Z, Uz, cal, D["level"])
    ps_score = ps.score(X, cal)
    # item-grain IITA (reported only)
    Xi = X.astype(np.int64)
    b = ((1 - Xi).T @ Xi).tolist()
    p = Xi.sum(0).tolist()
    rel_item, _, _ = iita_from_counts(b, p, len(X), J)
    lev = D["level"]
    def share_up(rel):
        cross = [(i, j) for i, j in rel if lev[i] != lev[j]]
        return (sum(lev[i] < lev[j] for i, j in cross) / len(cross)) if cross else float("nan"), len(cross)
    obs_share, obs_cross = share_up(rel_item)
    pats = [set(np.flatnonzero(r).tolist()) for r in X]
    null_cnt, null_share = [], []
    for Y in nulls.fixed_margin_draws(pats, J, random.Random(SEED), R_IITA_ITEM):
        M = np.zeros((len(Y), J), np.int64)
        for r_, pat in enumerate(Y):
            M[r_, list(pat)] = 1
        rel_n, _, _ = iita_from_counts(((1 - M).T @ M).tolist(), M.sum(0).tolist(), len(M), J)
        null_cnt.append(len(rel_n))
        null_share.append(share_up(rel_n)[0])
    null_cnt, null_share = np.array(null_cnt), np.array(null_share)
    item_iita = dict(count=len(rel_item), null_band=[float(np.quantile(null_cnt, 0.025)), float(np.quantile(null_cnt, 0.975))],
                     null_median=float(np.median(null_cnt)), share_low_to_high=obs_share, cross_level=obs_cross,
                     null_share_band=[float(np.nanquantile(null_share, 0.025)), float(np.nanquantile(null_share, 0.975))],
                     null_share_median=float(np.nanmedian(null_share)), R=R_IITA_ITEM)
    # direction control on the skill-grain IITA relation (shared.direction)
    rel_set = {tuple(e) for e in iita_r["relation"]}
    iita_dir = reversed_arrow(lambda edges: len(edges & rel_set), H_PUB)

    def inst_verdict(name, reading):
        if not floor["instruments"][name]["floor_passes"]:
            return "UNANSWERABLE"
        return reading
    verdicts = dict(reference=ref,
                    iita=inst_verdict("iita", iita_r["reading"]),
                    pairscan=inst_verdict("pairscan", ps_r["reading"]),
                    interaction=inst_verdict("interaction", inter_r["reading"]),
                    control="INFORMATIVE" if ref == "HIERARCHY FOUND" else "CONTROL UNINFORMATIVE")
    plant_rates = {k: dict(sig=float(np.mean([p_["sig"] for p_ in plants if p_["kind"] == k])),
                           isolated=float(np.mean([p_["isolated"] for p_ in plants if p_["kind"] == k])))
                   for k in ("pair", "gate", "chain")}
    out = dict(
        verdicts=verdicts,
        reference=dict(lrts=lrts, B=B_REAL,
                       saturated_pi=sat_pi.tolist(),
                       forbidden_mass_pub=forbidden_mass(sat_pi),
                       forbidden_mass_ci95=[float(np.quantile(fm, 0.025)), float(np.quantile(fm, 0.975))],
                       forbidden_mass_boot_B=B_NONPAR,
                       monotone_violations=fit["saturated"]["monotone_violations"]),
        skill_grain=dict(held_rate=Hs.mean(0).tolist(),
                         profile_counts={"".join(str(int(v)) for v in key): int(c) for key, c in
                                         zip(*np.unique(Hs.astype(int), axis=0, return_counts=True))}),
        iita=iita_r, iita_direction_control=iita_dir, iita_item_grain=item_iita,
        interaction=inter_r, interaction_null_check=nullchk,
        pairscan=dict(reading=ps_r, t=ps_score["t"], p=ps_score["p"], scanned=ps_score["scanned"],
                      pairs=ps_score["flags"]["pairs"], bh_pairs=ps_score["bh_pairs"],
                      critical=ps.critical(cal["tstar"]), converged=cal["converged"],
                      boot_nonconverged=cal["boot_nonconverged"], boot_rates=cal["boot_rates"],
                      a=cal["a"].tolist(), g=cal["g"], l=cal["l"],
                      plant_floor=plant_rates, fitted_model_fp=fp, R=R_PS_REAL,
                      item_level=[int(v) for v in D["level"]]),
        not_run=dict(drop="needs attempt order in time; ECPE is one cross-sectional administration",
                     lag="needs timestamps between skills; none in ECPE",
                     mastery_release="needs a release decision on a platform; none in ECPE"),
        seconds=time.time() - t0)
    (OUT / "result.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(dict(verdicts=verdicts, pub=dict(lr=pub["lr"], p=pub["p"]), rev=dict(lr=rev["lr"], p=rev["p"])),
                     indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("check", "fit", "floor", "real"), required=True)
    a = ap.parse_args()
    dict(check=phase_check, fit=phase_fit, floor=phase_floor, real=phase_real)[a.phase]()


if __name__ == "__main__":
    main()
