"""
Can an estimator that uses VARIATION IN THE ORDER learners met two skills, together with a later
outcome, orient a prerequisite edge beyond what difficulty says?

PRE-REGISTRATION. Written 2026-10-08, before any number in this file was computed, synthetic or real.
Author: Claude Opus 5.5 (session 01GTZaPFRRea1VKMWeMZogHX). Every choice the maintainer would
otherwise have made is marked DECISION. Order of work, each step committed before the next:
(1) this design; (2) the simulation, which is the detection floor and the confounding check;
(3) the positivity count on the real corpora, which reads learner, unit and time only, never an
outcome; (4) the real-data reading.

WHY. Paper II (research/article/what-learner-records-can-say-about-a-prerequisite-edge.md, 5.1 and
its Answer to RQ1) shows the atlas's orientation statistic s(a, b) = P(fail b | fail a) -
P(fail a | fail b) is identically "orient from the easier skill to the harder"
(studies/simulation/orientation-sortability/), and narrows its claim: the identity "does not rule out
an estimator that uses variation in the order learners met the skills together with a later outcome,
which needs the identifying cell above." Doroudi, Holstein, Aleven & Brunskill (EDM 2016, "Sequence
matters, but how exactly?", SCOVA; literature-sweep-2.md entry A.4) regress outcomes on how far each
learner's sequence violates a candidate ordering constraint and found, in a fractions tutor whose
sequences varied, a data-preferred order against the difficulty order. This study builds such an
estimator, floors it in sortability.py's worlds, checks whether a non-random order choice fools it,
and reads it on real corpora that have order variation.

THE ESTIMATOR (ORDER-ADJ, primary).
  For an unordered pair {u, v}, a learner is in the u-FIRST arm if their first attempt at u precedes
  their first attempt at v (strictly; equal first times are dropped), else in the v-FIRST arm.
  OUTCOME (stated): Y = Y_u + Y_v, where Y_x is the learner's accuracy on their FIRST K = 3 attempts at
  x (all available if fewer, at least 1), i.e. each skill's outcome is indexed by that skill's OWN
  attempt count, so both arms are compared at equal own-practice. For the skill met second, these
  attempts come after the other skill was met: that is the "later outcome" the order acts on.
  WHY THE SUM (derivation, not a choice): with D_v = E[Y_v | u first] - E[Y_v | v first] (what
  meeting u first does to v) and D_u = E[Y_u | v first] - E[Y_u | u first] (what meeting v first does
  to u), the u-first advantage on Y_u + Y_v is exactly D_v - D_u. If u -> v is a true edge, D_v > 0
  and D_u = 0 in expectation (v is not upstream of u), so the sign of the u-first advantage on the
  sum is the edge's direction. Practice and warm-up effects that act alike on whichever skill comes
  second cancel in the difference.
  ADJUSTMENT. OLS of Y on [1, uFirst, prior, log(1 + n_prior)], pair by pair, learners as rows.
    prior = the learner's mean RESIDUAL first-attempt correctness (correct minus that unit's mean
    first-attempt correctness over all learners) on the units they first met BEFORE the earlier of
    u and v; n_prior is how many such units (>= PRIOR_MIN = 3, else the learner is not in the
    pair). The residual is the difficulty adjustment: prior ability is measured net of how hard the
    units it was measured on are, so a learner whose earlier units were hard is not scored as weak.
    Within a pair the difficulties of u and v are the same in both arms, so they need no term.
  CALL. A(u, v) = the coefficient on uFirst; orient u -> v if A > 0, v -> u if A < 0, a tie (A = 0
  or not estimable) scores 0.5. Compared, on the same pairs, with DIFFSORT: orient from the skill
  with the higher first-attempt accuracy (over all learners) to the lower; ties 0.5.
  VARIANTS (reported, not headline):
    ORDER-RAW   the same contrast with no covariates (difference in mean Y between arms, same rows).
                Its reason: it shows what the adjustment is doing under a confounded order.
    SCOVA-NEXT  (SCOVA-style, pairwise; DECISION: Doroudi et al. regress a posttest on a sequence's
                share of violated constraints; for one candidate constraint "u before v" the
                violation share is the arm indicator, so the pairwise SCOVA is the arm contrast on a
                COMMON later outcome.) Outcome: the learner's mean residual correctness (attempt
                correct minus that unit's mean correctness over all attempts) on the next W = 20
                attempts, at any unit, after the first attempt at whichever of u, v came second
                (>= 5 such attempts, else not in the pair). Same covariates. Stated weakness, before
                the run: the window can hold u and v attempts themselves, and what follows depends
                on the platform's sequence, so it is a noisier and more confoundable outcome than Y.
    SCOVA-POST  (simulation only; no held corpus has a common posttest): the learner's accuracy on
                a final one-item-per-skill assessment over all skills; same covariates.

PART 1. SIMULATION (synthetic; no corpus). The detection floor and the confounding check.
  Worlds: sortability.py's, i.e. orientation_difficulty.world(random.Random(3300 + w), regime),
  w = 0..14, 30 nodes, edge prob 0.08, regimes ALIGNED (latent difficulty rises with depth),
  INDEPENDENT, INVERTED (falls with depth); od.N_LEARNERS = 3,000 learners; SLIP 0.12, GUESS 0.15.
  A DYNAMIC generator (sortability's is static: one mastery vector, no order) -- DECISION, needed
  because the estimator reads order:
    theta ~ N(0, 1). The learner meets the 30 skills one at a time in an order set by the ORDER
    REGIME. On meeting skill n: "short" = (AND) any parent not yet mastered / (OR) n has parents and
    none is mastered / (NULL) never -- prerequisites inert. Short => blocked with probability
    HARDNESS = 1.0 (not acquired at this meeting). Otherwise acquired iff theta + e > diff[n],
    e ~ N(0, 0.5) per learner-skill. K = 3 attempts at n follow, each correct w.p. 1 - SLIP if
    acquired else GUESS. After all 30 are met, one REVIEW pass in index (topological) order gives
    every unacquired skill one more acquisition try under the same rule with the mastery held then
    (no attempts recorded); then the POSTTEST: one item per skill, slip/guess on final mastery.
  ORDER REGIMES (key per learner per node; the node order is argsort of the key):
    RANDOM      key ~ U(0, 1): order assigned at random, independent of everything.
    ABILITY     key = -1.0 * theta * z(diff[n]) + N(0, 1): abler learners take the harder skills
                first, weaker learners the easier ones (z = latent difficulty standardised over the
                world's nodes).
    CURRICULUM  key = n / 30 + N(0, 0.25): a curriculum in the true topological order with
                ability-free deviations (this is mainly a positivity regime: few edges are violated
                often enough).
    SKIP        key = (n / 30) * exp(-0.75 * theta) + N(0, 0.25): the same curriculum, but abler
                learners compress it and so meet later skills out of order more often; violators
                are abler.
  Mechanisms AND, OR, NULL x 3 difficulty regimes x 4 order regimes = 36 cells, 15 worlds each.
  Seeds: learner stream np.random.default_rng([20261008, mech, regime, order, w]).
  Scored edges: a world's TRUE edges (a -> b, a < b) with >= MIN_ARM = 30 learners in each arm after
  the prior filter (coverage reported). Truth for NULL is the inert edge's nominal direction, so
  0.5 is the correct answer there.
  PER CELL, for each estimator E: acc(E) = share of scored edges oriented a -> b (ties 0.5);
  acc(DIFFSORT) on the SAME edges; D = acc(E) - acc(DIFFSORT). 95% percentile intervals resample
  WORLDS (the unit a graph, a difficulty draw and a learner sample are assigned to), 2,000 draws,
  paired. Readings, margin m = 0.02 (sortability.py's):
    vs DIFFSORT: ADDS (D lo > 0 and D > m) / NO BETTER (D hi <= m) / WORSE (D hi < 0) /
                 UNDECIDED / CEILING (acc(DIFFSORT) >= 0.95, read but not used in a verdict)
    vs chance:   ORIENTS (acc lo > 0.5) / REVERSED (acc hi < 0.5) / CHANCE (interval holds 0.5)
  Also per cell: median over scored edges of |SMD| of prior between arms (how ability-tied the
  order is), and the coverage.
  PRE-REGISTERED SIMULATION VERDICTS (ORDER-ADJ):
    FLOOR passes iff (i) under RANDOM order ORDER-ADJ reads ADDS in the INVERTED regime for both AND
    and OR ("it must beat the difficulty sort under random order where difficulty falls with
    depth"), (ii) it reads ORIENTS in every RANDOM cell of AND and OR, and (iii) it reads CHANCE in
    all three NULL/RANDOM cells (it does not orient inert edges). If the floor fails, every real
    reading below is UNANSWERABLE (FLOOR FAILED).
    CONFOUNDING, per non-random order regime R in {ABILITY, CURRICULUM, SKIP}:
      "FOOLED BY ORDER CHOICE"  NULL/R reads ORIENTS or REVERSED in any difficulty regime (an
                                inert edge is oriented anyway), or any AND/OR cell under R reads
                                REVERSED (true edges confidently reversed).
      "NOT FOOLED"              otherwise.
    Reported for ORDER-ADJ (binding) and ORDER-RAW (to show what adjustment buys).
    SIM HEADLINE: "ORIENTS BEYOND DIFFICULTY UNDER RANDOM ORDER" if the floor passes (else "FLOOR
    FAILED"), followed by "; ABILITY-DRIVEN ORDER FOOLS IT" if ABILITY or SKIP reads FOOLED, else
    "; ABILITY-DRIVEN ORDER DOES NOT FOOL IT".

PART 2. POSITIVITY (reads learner, unit and time only; NO outcome is read; committed before part 3).
  Candidate corpora and why, stated now:
    EdNet KT1 (CC BY-NC 4.0; first EDNET_LEARNERS = 20,000 KT1 members of the zip, the regenerable
      prefix of shared.corpus.kt1_members; unit = the question's FIRST tag, the atlas's KC model;
      time = timestamp). Learners choose what to practise, so order varies. No authored order is
      held: its reference is the difficulty sort only. DECISION: 20,000 learners bounds the pair-row
      table (memory) on a shared 15 GB machine.
    Eedi NeurIPS 2020 (research use; unit = level-3 subject). TIME IS THE LATEST ANSWER, NOT THE
      FIRST (shared.corpus.Eedi): first-meeting order, the treatment, is not recorded. Its
      positivity is counted on last-answer order for the record, but Eedi is NOT read in part 3
      whatever the count says. DECISION, stated before the count.
    ASSISTments 2012-13 (analysis only; unit = skill_id; time = start_time). Reference: CCSS grade
      via studies/measurement/assist2012-direction/out/skill_ccss_map.json (all matched skills),
      lower grade -> higher grade, on cross-grade pairs. Order is set largely by teachers, per class:
      the cohort proxy (shared.corpus.Assistments2012 with_cohorts: first assignment_id) is the
      resampling unit for its learner-side interval.
    Junyi 2015 on DataShop ds1275 'All Data' (research use; unit = KC (Exercise); time = Step Start
      Time; attempt = a step with First Attempt correct/incorrect, hint steps skipped, as in
      sortability.py's ds1275 loader). Reference: the authored prerequisite graph
      (shared.junyi_graph.authored_edges; p -> n). Learners choose, with system suggestions.
  ELIGIBLE PAIR: >= MIN_ARM = 30 learners in EACH arm (after PRIOR_MIN). A corpus is READ in part 3
  iff first-meeting order is recorded AND it has >= MIN_PAIRS = 30 eligible pairs (reference pairs,
  for a corpus with a reference). Otherwise its reading is UNANSWERABLE, not null.

PART 3. REAL DATA (after the positivity commit). Real data has no ground-truth edges.
  Per read corpus, over eligible pairs:
    AGREE       share of pairs where ORDER-ADJ orients as DIFFSORT does (ties 0.5).
    ACC_O       (reference corpora) share of eligible reference pairs ORDER-ADJ orients along the
                reference; ACC_D the same for DIFFSORT; D = ACC_O - ACC_D (SIGNED: > 0 means order
                variation agrees with the authored order more often than difficulty does).
                Descriptive: on the DISCORDANT reference pairs (ORDER-ADJ and DIFFSORT disagree),
                the share where ORDER-ADJ follows the reference.
    SIGNAL      T = mean over eligible pairs of z^2, z = A / its OLS standard error.
    BALANCE     median over eligible pairs of |SMD| of prior between arms.
  CONTROL (deranged, family-matched, the treatment's size): within each pair, the arm labels are
  DERANGED across learners inside prior-ability quintile strata (global quintiles of prior): rows
  are shuffled within (pair, quintile) and each takes the label of the next row, cyclically, so
  every learner gets another learner's label, the arm sizes and the ability-arm relation are kept,
  and only the order-outcome link beyond prior ability is broken. Same pairs, same learners, same
  arm sizes: the control is exactly the treatment's size. 20 derangements. SIGNAL is PRESENT iff
  T exceeds every control T. AGREE and ACC_O under the control are reported (expected 0.5).
  For ASSISTments the order is set per class, so a learner-level derangement is too narrow a null
  for SIGNAL there; its SIGNAL line is reported but flagged, and no ASSISTments verdict uses it.
  INTERVALS (two, both 95% percentile; a verdict needs both):
    LEARNER   Poisson(1) bootstrap weights per learner (per COHORT for ASSISTments: the unit the
              order is assigned to), 200 draws; every pair's A and every unit's difficulty are
              recomputed under the weights; eligibility is fixed from the full sample.
    SKILL     units resampled with replacement, pairs rebuilt from the resampled units
              (multiplicity c_u * c_v), per-pair calls fixed, 2,000 draws: what the pair
              population contributes.
  REAL-SHAPED FLOOR (planted, on the real eligible rows: their arms, prior, n_prior and outcome
  spread): derange the arm labels as the control does (so no real order effect remains), then add
  delta to Y in the arm that met the PLANTED prerequisite first; planted direction = the reference
  on reference pairs, a fair coin elsewhere (and everywhere on EdNet). delta in {0, 0.05, 0.10} on
  the 0-2 scale of Y, 20 reps each, SKILL interval (400 draws). PASS iff at delta = 0.10 the planted
  direction is recovered (ACC lower > 0.5) in >= 80% of reps, and, for a reference corpus, the
  planted run reads ORIENTS BEYOND DIFFICULTY in >= 80% of reps; and at delta = 0 the ACC interval
  excludes 0.5 in <= 10% of reps. The minimum detectable delta is the smallest that passes.
  PRE-REGISTERED REAL VERDICTS (signed), in this precedence:
    "UNANSWERABLE"               the sim floor failed, or the corpus is not read (part 2).
    "CONFOUNDED BY ORDER CHOICE" the sim reads ORDER-ADJ FOOLED under ABILITY or SKIP, AND the
                                 corpus's BALANCE (median |SMD| of prior) >= 0.10: the corpus's
                                 order choice is tied to ability at a size the adjustment was shown
                                 not to remove. The computed reading is reported beside it.
    Reference corpora:
      "ORIENTS BEYOND DIFFICULTY"     D lower > 0 in BOTH intervals and D > m.
      "WORSE THAN DIFFICULTY"         D upper < 0 in both.
      "NO BETTER THAN DIFFICULTY"     D upper <= m in both (and not WORSE).
      "UNDECIDED"                     otherwise.
    EdNet (no reference; a departure from difficulty is not evidence of being right):
      "ORDER ORIENTATION FOLLOWS DIFFICULTY"   AGREE lower > 0.5 + m in both intervals.
      "ORDER ORIENTATION AGAINST DIFFICULTY"   AGREE upper < 0.5 in both.
      "ORDER ORIENTATION INDEPENDENT OF DIFFICULTY"  otherwise.
      each followed by "(ORDER SIGNAL PRESENT)" or "(NO ORDER SIGNAL ABOVE CONTROL)".
    A failed real-shaped floor turns NO BETTER / UNDECIDED / INDEPENDENT into "UNDERPOWERED"; an
    ORIENTS BEYOND reading stands with the floor beside it.
  MEANING, written before the run. ORIENTS BEYOND DIFFICULTY on a reference corpus means order
  variation plus a later outcome agrees with that corpus's authored order more often than the
  difficulty sort does, i.e. Paper II's narrowed RQ1 sentence has a positive instance. NO BETTER
  means the order-variation estimator, where it can be computed, does not beat difficulty against
  the authored reference. CONFOUNDED means the corpus's order choice is tied to ability at a level
  the simulation showed the adjusted estimator cannot see through. Either way nothing here gives a
  ground-truth edge direction: the references are authored orders (CCSS grade is an order, not a
  graph; most cross-grade pairs are not prerequisites), and DIFFSORT on them is the comparator.

WHAT THIS CAN SAY: whether an order-variation estimator orients true edges in a generator family
where order is assigned at random or by ability, against the difficulty sort; and on real corpora,
how its calls relate to difficulty and to an authored order. WHAT IT CANNOT SAY: the real direction
of any edge; anything about Eedi's order (last-answer time); anything outside this generator family.

DATA HANDLING. Parts 2-3 read EdNet KT1 (CC BY-NC 4.0, non-commercial, no model training: nothing
here trains a model), Eedi NeurIPS 2020 (research use; positivity only), ASSISTments 2012-13
(analysis only) and DataShop ds1275 / Junyi 2015 (research use) from the session scratchpad through
shared.paths.data_path. Only aggregates are written: counts, shares, intervals. No learner rows, no
item text, no unit names.

    python3 order_variation.py sim          # part 1 -> out/sim.json
    python3 order_variation.py positivity   # part 2 -> out/positivity.json (no outcome read)
    python3 order_variation.py real         # part 3 -> out/real.json

CHANGES
  2026-10-08, after the simulation run (commit 0de51f6) and BEFORE the positivity count or any real
  row was read. No design, threshold, estimand, interval or verdict string changes.
  (1) RESULT AS REGISTERED: "FLOOR FAILED; ABILITY-DRIVEN ORDER FOOLS IT". Floor part (i) failed:
      AND/INVERTED/RANDOM reads WORSE (ORDER-ADJ 0.571 against DIFFSORT 0.945; under random order
      the dynamic AND gate blocks a dependent met before its prerequisites, so the gate itself makes
      dependents look hard and the sort is near ceiling). Part (iii) failed: NULL/ALIGNED/RANDOM
      0.438 [0.388, 0.490] and NULL/INDEPENDENT/RANDOM 0.456 [0.416, 0.493] read REVERSED.
      Per the registered rule every real VERDICT is therefore UNANSWERABLE (FLOOR FAILED).
  (2) ADDED, labelled POST-HOC, gating nothing: `sim-posthoc` -> out/sim-posthoc.json.
      (a) NULL x 3 regimes x RANDOM on 60 further worlds (w = 15..74), to ask whether part (iii)'s
          failure is a bias or a narrow 15-world interval (a quick check, 6 other learner seeds of
          NULL/ALIGNED/RANDOM, gave pooled accuracies 0.500-0.558, mean 0.519).
      (b) AND at HARDNESS 0.5 x 3 regimes x RANDOM, 15 worlds, to ask whether part (i)'s failure is
          the harshness of a hard dynamic gate.
      Neither can turn the registered floor into a pass.
  (3) REAL PART COMPUTED DESCRIPTIVELY: main_real now computes every registered quantity (estimates,
      both intervals, control, real-shaped floor) for each corpus part 2 admits, even though the sim
      floor failed; the verdict field stays "UNANSWERABLE" (reason: simulation floor failed) and the
      registered rule's own reading is stored as `computed_reading_descriptive`, not a verdict.
      Reason: the confounding result and the real-shaped floor say what Paper VII needs to know
      about these corpora; withholding the numbers would not make them findings either way.
  2026-10-08, during the positivity count (after junyi, assist and ednet were counted, before any
  outcome was read). (4) MEMORY-LIGHT COUNT FOR EEDI: build() was killed by the memory limit on Eedi
  (10.8 GB resident). positivity_light() counts the same quantity -- per unordered pair, learners in
  each arm, first-meeting order, ties dropped, the first-met unit at meeting position >= PRIOR_MIN --
  from each learner's per-unit FIRST time only, accumulated into dense unit x unit arrays, without
  holding pair rows or outcomes. It is checked against build() on junyi before Eedi is counted (the
  eligible-pair and reference counts must match exactly). Eedi's exclusion from part 3 is unchanged.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "shared"))
sys.path.insert(0, str(ROOT / "studies/simulation/learner-sim"))

import orientation_difficulty as od  # noqa: E402

SEED = 20261008
WORLDS = 15
SEED_BASE = 3300
REGIMES = ("ALIGNED", "INDEPENDENT", "INVERTED")
MECHS = ("AND", "OR", "NULL")
ORDERS = ("RANDOM", "ABILITY", "CURRICULUM", "SKIP")
HARDNESS = 1.0
SIGMA_E = 0.5
K = 3
W_NEXT = 20
MIN_NEXT = 5
PRIOR_MIN = 3
MIN_ARM = 30
MIN_PAIRS = 30
MARGIN = 0.02
CEILING = 0.95
BOOT_WORLD = 2000
BOOT_LEARNER = 200
BOOT_SKILL = 2000
BOOT_FLOOR = 400
N_DERANGE = 20
FLOOR_REPS = 20
FLOOR_DELTAS = (0.0, 0.05, 0.10)
SMD_CONFOUND = 0.10
EDNET_LEARNERS = 20000
ESTIMATORS = ("ORDER-ADJ", "ORDER-RAW", "SCOVA-NEXT", "SCOVA-POST")


# =========================================================================== the estimator engine
#
# Rows are (learner, pair) records. pid indexes the canonical unordered pair (lo, hi); af = 1 if
# the learner met lo first. Every estimate is a per-pair OLS from grouped sufficient statistics, so
# the same code runs on the simulation, on the real corpora and under bootstrap weights.

def pair_ols(pid, n_pairs, af, y, covs, w=None):
    """Per-pair OLS of y on [1, af, *covs]; returns (coef on af, its OLS SE, n). NaN if singular."""
    X = [np.ones_like(y), af] + list(covs)
    p = len(X)
    if w is None:
        w = np.ones_like(y)
    S = np.empty((n_pairs, p, p))
    for i in range(p):
        for j in range(i, p):
            S[:, i, j] = S[:, j, i] = np.bincount(pid, w * X[i] * X[j], minlength=n_pairs)
    t = np.stack([np.bincount(pid, w * X[i] * y, minlength=n_pairs) for i in range(p)], 1)
    yy = np.bincount(pid, w * y * y, minlength=n_pairs)
    n = np.bincount(pid, w, minlength=n_pairs)
    coef = np.full(n_pairs, np.nan)
    se = np.full(n_pairs, np.nan)
    ok = n > p + 2
    if ok.any():
        Sk = S[ok] + np.eye(p) * 1e-9
        try:
            inv = np.linalg.inv(Sk)
        except np.linalg.LinAlgError:
            inv = np.stack([np.linalg.pinv(m) for m in Sk])
        b = np.einsum("kij,kj->ki", inv, t[ok])
        rss = yy[ok] - np.einsum("ki,ki->k", b, t[ok])
        s2 = np.maximum(rss, 0) / (n[ok] - p)
        coef[ok] = b[:, 1]
        se[ok] = np.sqrt(np.maximum(s2 * inv[:, 1, 1], 0))
    return coef, se, n


def call(coef):
    """+1 orient lo -> hi, -1 hi -> lo, 0 tie / not estimable."""
    c = np.sign(np.nan_to_num(coef, nan=0.0))
    return c


def score_vs(calls, truth):
    """1 if the call matches truth (+1/-1), 0 if opposite, 0.5 on a tie."""
    return np.where(calls == 0, 0.5, (calls == truth).astype(float))


def smd(pid, n_pairs, af, x, w=None):
    """Per-pair standardised mean difference of x between arms (af=1 minus af=0)."""
    if w is None:
        w = np.ones_like(x)
    n1 = np.bincount(pid, w * af, minlength=n_pairs)
    n0 = np.bincount(pid, w * (1 - af), minlength=n_pairs)
    s1 = np.bincount(pid, w * af * x, minlength=n_pairs)
    s0 = np.bincount(pid, w * (1 - af) * x, minlength=n_pairs)
    q = np.bincount(pid, w * x * x, minlength=n_pairs)
    tot = n0 + n1
    with np.errstate(invalid="ignore", divide="ignore"):
        m = (s0 + s1) / tot
        sd = np.sqrt(np.maximum(q / tot - m * m, 0))
        return (s1 / n1 - s0 / n0) / sd


def derange_labels(pid, strata, af, rng):
    """Within each (pair, stratum) group, every row takes the label of the next row in a random
    cyclic order: a derangement of learners within the group. Arm sizes per group are kept."""
    key = pid.astype(np.int64) * 16 + strata.astype(np.int64)
    order = np.lexsort((rng.random(len(af)), key))
    k = key[order]
    lab = af[order]
    start = np.r_[True, k[1:] != k[:-1]]
    gid = np.cumsum(start) - 1
    first = np.flatnonzero(start)
    pos = np.arange(len(k))
    nxt = pos + 1
    end = np.r_[first[1:], len(k)]
    last = end - 1
    nxt[last] = first          # wrap: the last row of each group takes the first row's label
    del gid
    out = np.empty_like(af)
    out[order] = lab[nxt]
    return out


def selftest():
    """Direction check: rows where lo-first raises Y must call lo -> hi; mirrored must call hi -> lo.
    Also checks the derangement moves every row in groups of size >= 2 and keeps arm sizes."""
    rng = np.random.default_rng(1)
    n = 4000
    pid = np.repeat(np.arange(2), n // 2)
    af = (rng.random(n) < 0.5).astype(float)
    prior = rng.normal(0, 1, n)
    eff = np.where(pid == 0, 0.3, -0.3)
    y = 1.0 + eff * af + 0.5 * prior + rng.normal(0, 0.3, n)
    c, se, _ = pair_ols(pid, 2, af, y, [prior, np.zeros(n)])
    assert c[0] > 0.2 and c[1] < -0.2, c
    assert list(call(c)) == [1, -1]
    assert score_vs(call(c), np.array([1, 1]))[0] == 1 and score_vs(call(c), np.array([1, 1]))[1] == 0
    strata = (rng.random(n) * 5).astype(int)
    d = derange_labels(pid, strata, af, rng)
    for p in range(2):
        for s in range(5):
            m = (pid == p) & (strata == s)
            assert d[m].sum() == af[m].sum()
    # the identity of the moved rows: mark rows by index and derange the marks
    idx = np.arange(n, dtype=float)
    di = derange_labels(pid, strata, idx, np.random.default_rng(2))
    assert (di != idx).all()
    return True


# =========================================================================== part 1: simulation

def zscore(v):
    v = np.asarray(v, float)
    s = v.std()
    return (v - v.mean()) / (s if s > 0 else 1.0)


def simulate(par, diff, mech, order, g, n_learners=od.N_LEARNERS):
    """Dynamic learners. Returns pos (N x 30 step at which node met), att (N x 30 x K correctness),
    post (N x 30 final assessment), and theta."""
    N, M = n_learners, od.N_NODES
    P = np.zeros((M, M), bool)            # P[n, p] = p is a parent of n
    for n in range(M):
        for p in par[n]:
            P[n, p] = True
    nparents = P.sum(1)
    d = np.array([diff[n] for n in range(M)])
    th = g.normal(0, 1, N)
    zd = zscore(d)
    idx = np.arange(M) / M
    if order == "RANDOM":
        key = g.random((N, M))
    elif order == "ABILITY":
        key = -1.0 * th[:, None] * zd[None, :] + g.normal(0, 1, (N, M))
    elif order == "CURRICULUM":
        key = idx[None, :] + g.normal(0, 0.25, (N, M))
    elif order == "SKIP":
        key = idx[None, :] * np.exp(-0.75 * th)[:, None] + g.normal(0, 0.25, (N, M))
    else:
        raise ValueError(order)
    seq = np.argsort(key, 1, kind="stable")       # seq[i, t] = node met at step t
    pos = np.empty((N, M), int)
    pos[np.arange(N)[:, None], seq] = np.arange(M)[None, :]
    E = g.normal(0, SIGMA_E, (N, M))
    held = np.zeros((N, M), bool)
    rows = np.arange(N)

    def short_of(nodes, held):
        Pn = P[nodes]                               # N x M parents of each learner's node
        missing = (Pn & ~held).sum(1)
        if mech == "AND":
            return missing > 0
        if mech == "OR":
            return (nparents[nodes] > 0) & (missing == nparents[nodes])
        return np.zeros(len(nodes), bool)

    for t in range(M):
        nodes = seq[:, t]
        short = short_of(nodes, held)
        blocked = short & (g.random(N) < HARDNESS)
        acq = ~blocked & (th + E[rows, nodes] > d[nodes])
        held[rows, nodes] = acq
    # attempts at the meeting use mastery as acquired AT the meeting
    met_mastery = held.copy()
    att = np.where(met_mastery[:, :, None], g.random((N, M, K)) > od.SLIP,
                   g.random((N, M, K)) < od.GUESS).astype(float)
    # review pass in index (topological) order
    for n in range(M):
        nodes = np.full(N, n)
        need = ~held[:, n]
        short = short_of(nodes, held)
        blocked = short & (g.random(N) < HARDNESS)
        acq = need & ~blocked & (th + g.normal(0, SIGMA_E, N) > d[n])
        held[:, n] |= acq
    post = np.where(held, g.random((N, M)) > od.SLIP, g.random((N, M)) < od.GUESS).astype(float)
    return pos, seq, att, post, th


def sim_rows(edges, pos, seq, att, post):
    """Rows for each true edge (a, b), a < b: canonical lo = a, hi = b, af = 1 if a met first."""
    N, M = pos.shape
    first = att[:, :, 0]
    fmean = first.mean(0)
    resid_first = first - fmean[None, :]
    amean = att.mean((0, 2))
    # per-learner residual first-attempt correctness in meeting order, cumulated
    rf_seq = np.take_along_axis(resid_first, seq, 1)              # N x M by step
    cp = np.concatenate([np.zeros((N, 1)), np.cumsum(rf_seq, 1)], 1)
    # attempt sequence residuals, K per step, cumulated
    ra = att - amean[None, :, None]
    ra_seq = np.take_along_axis(ra, seq[:, :, None], 1).reshape(N, M * K)
    ca = np.concatenate([np.zeros((N, 1)), np.cumsum(ra_seq, 1)], 1)
    Y3 = att.mean(2)
    postm = post.mean(1)
    out = defaultdict(list)
    for k, (a, b) in enumerate(sorted(edges)):
        pa, pb = pos[:, a], pos[:, b]
        lo_t = np.minimum(pa, pb)
        hi_t = np.maximum(pa, pb)
        keep = lo_t >= PRIOR_MIN
        r = np.flatnonzero(keep)
        nprior = lo_t[r].astype(float)
        prior = cp[r, lo_t[r]] / nprior
        s = (hi_t[r] + 1) * K                       # attempt index after the second skill's block
        e = np.minimum(s + W_NEXT, M * K)
        cnt = (e - s).astype(float)
        nxt = np.where(cnt >= MIN_NEXT, (ca[r, e] - ca[r, s]) / np.maximum(cnt, 1), np.nan)
        out["pid"].append(np.full(len(r), k))
        out["af"].append((pa[r] < pb[r]).astype(float))
        out["prior"].append(prior)
        out["lnp"].append(np.log1p(nprior))
        out["y"].append(Y3[r, a] + Y3[r, b])
        out["next"].append(nxt)
        out["post"].append(postm[r])
    rows = {k2: np.concatenate(v) for k2, v in out.items()}
    rows["pid"] = rows["pid"].astype(np.int64)
    return rows, fmean


def estimate_all(rows, n_pairs):
    """Per-pair A for each estimator, plus arm sizes and prior SMD."""
    pid, af = rows["pid"], rows["af"]
    covs = [rows["prior"], rows["lnp"]]
    res = {}
    res["ORDER-ADJ"] = pair_ols(pid, n_pairs, af, rows["y"], covs)
    res["ORDER-RAW"] = pair_ols(pid, n_pairs, af, rows["y"], [])
    m = ~np.isnan(rows["next"])
    res["SCOVA-NEXT"] = pair_ols(pid[m], n_pairs, af[m], rows["next"][m], [c[m] for c in covs])
    if "post" in rows:
        res["SCOVA-POST"] = pair_ols(pid, n_pairs, af, rows["post"], covs)
    n1 = np.bincount(pid, af, minlength=n_pairs)
    n0 = np.bincount(pid, 1 - af, minlength=n_pairs)
    nm1 = np.bincount(pid[m], af[m], minlength=n_pairs)
    nm0 = np.bincount(pid[m], 1 - af[m], minlength=n_pairs)
    return res, n1, n0, nm1, nm0, smd(pid, n_pairs, af, rows["prior"])


def run_world(mech, regime, order, w, hardness=None, tag=None):
    global HARDNESS
    rng = random.Random(SEED_BASE + w)
    edges, par, diff = od.world(rng, regime)
    seed = [SEED, MECHS.index(mech), REGIMES.index(regime), ORDERS.index(order), w]
    g = np.random.default_rng(seed if tag is None else seed + [tag])
    keep_h = HARDNESS
    if hardness is not None:
        HARDNESS = hardness
    try:
        pos, seq, att, post, _ = simulate(par, diff, mech, order, g)
    finally:
        HARDNESS = keep_h
    E = sorted(edges)
    rows, fmean = sim_rows(E, pos, seq, att, post)
    res, n1, n0, nm1, nm0, sm = estimate_all(rows, len(E))
    # DIFFSORT: easier (higher first-attempt accuracy) first; truth is a -> b, i.e. +1
    ds = np.array([0.5 if fmean[a] == fmean[b] else float(fmean[a] > fmean[b]) for a, b in E])
    elig = (np.minimum(n1, n0) >= MIN_ARM)
    elig_next = (np.minimum(nm1, nm0) >= MIN_ARM)
    rec = dict(n_edges=len(E), diffsort=ds, elig=elig, elig_next=elig_next,
               smd=np.abs(sm))
    for est, (coef, se, _) in res.items():
        rec[est] = score_vs(call(coef), np.ones(len(E)))
    return rec


def read_vs_sort(D, lo, hi, acc_ds):
    if acc_ds >= CEILING:
        return "CEILING"
    if lo > 0 and D > MARGIN:
        return "ADDS"
    if hi < 0:
        return "WORSE"
    if hi <= MARGIN:
        return "NO BETTER"
    return "UNDECIDED"


def read_vs_chance(lo, hi):
    if lo > 0.5:
        return "ORIENTS"
    if hi < 0.5:
        return "REVERSED"
    return "CHANCE"


def summarise_cell(worlds, rng):
    nw = len(worlds)
    B = rng.integers(0, nw, (BOOT_WORLD, nw))
    out = dict(n_edges_total=int(sum(w["n_edges"] for w in worlds)))
    for est in ESTIMATORS:
        sel = [w["elig_next"] if est == "SCOVA-NEXT" else w["elig"] for w in worlds]
        c = np.array([s.sum() for s in sel], float)
        se_ = np.array([w[est][s].sum() for w, s in zip(worlds, sel)])
        sd_ = np.array([w["diffsort"][s].sum() for w, s in zip(worlds, sel)])
        if c.sum() == 0:
            out[est] = dict(n_scored=0)
            continue
        acc = se_.sum() / c.sum()
        accd = sd_.sum() / c.sum()
        cb = c[B].sum(1)
        okb = cb > 0
        accb = se_[B].sum(1)[okb] / cb[okb]
        accdb = sd_[B].sum(1)[okb] / cb[okb]
        Db = accb - accdb
        alo, ahi = np.percentile(accb, [2.5, 97.5])
        dlo, dhi = np.percentile(accdb, [2.5, 97.5])
        Dlo, Dhi = np.percentile(Db, [2.5, 97.5])
        D = acc - accd
        out[est] = dict(
            n_scored=int(c.sum()), coverage=float(c.sum() / out["n_edges_total"]),
            acc=[float(acc), float(alo), float(ahi)],
            acc_diffsort=[float(accd), float(dlo), float(dhi)],
            D=[float(D), float(Dlo), float(Dhi)],
            vs_sort=read_vs_sort(D, Dlo, Dhi, accd), vs_chance=read_vs_chance(alo, ahi))
    sm = np.concatenate([w["smd"][w["elig"]] for w in worlds])
    sm = sm[~np.isnan(sm)]
    out["median_abs_smd_prior"] = float(np.median(sm)) if len(sm) else None
    return out


def main_sim():
    assert selftest()
    t0 = time.time()
    rng = np.random.default_rng(SEED + 1)
    cells = {}
    for mech in MECHS:
        for regime in REGIMES:
            for order in ORDERS:
                worlds = [run_world(mech, regime, order, w) for w in range(WORLDS)]
                cell = summarise_cell(worlds, rng)
                key = f"{mech}/{regime}/{order}"
                cells[key] = cell
                a = cell["ORDER-ADJ"]
                print(f"{key:<28} n={a.get('n_scored', 0):>4} cov={a.get('coverage', 0):.2f} "
                      f"ADJ {a.get('acc', [np.nan])[0]:.3f} sort {a.get('acc_diffsort', [np.nan])[0]:.3f} "
                      f"D {a.get('D', [np.nan])[0]:+.3f} {a.get('vs_sort')}/{a.get('vs_chance')}  "
                      f"RAW {cell['ORDER-RAW'].get('acc', [np.nan])[0]:.3f} "
                      f"NEXT {cell['SCOVA-NEXT'].get('acc', [np.nan])[0]:.3f} "
                      f"POST {cell['SCOVA-POST'].get('acc', [np.nan])[0]:.3f} "
                      f"smd {cell['median_abs_smd_prior']}  [{time.time() - t0:.0f}s]", flush=True)
    verdict = sim_verdicts(cells)
    OUT.mkdir(exist_ok=True)
    (OUT / "sim.json").write_text(json.dumps(dict(
        design=dict(worlds=WORLDS, learners=od.N_LEARNERS, nodes=od.N_NODES, hardness=HARDNESS,
                    sigma_e=SIGMA_E, K=K, w_next=W_NEXT, prior_min=PRIOR_MIN, min_arm=MIN_ARM,
                    margin=MARGIN, boot_world=BOOT_WORLD, seed=SEED),
        cells=cells, verdicts=verdict), indent=2) + "\n")
    print(json.dumps(verdict, indent=2))


def main_sim_posthoc():
    """POST-HOC diagnostics (CHANGES 2); gate nothing."""
    rng = np.random.default_rng(SEED + 2)
    out = {}
    for regime in REGIMES:
        ws = [run_world("NULL", regime, "RANDOM", w, tag=1) for w in range(15, 75)]
        out[f"NULL/{regime}/RANDOM/60-more-worlds"] = summarise_cell(ws, rng)
    for regime in REGIMES:
        ws = [run_world("AND", regime, "RANDOM", w, hardness=0.5, tag=2) for w in range(WORLDS)]
        out[f"AND-h0.5/{regime}/RANDOM"] = summarise_cell(ws, rng)
    for k, c in out.items():
        a = c["ORDER-ADJ"]
        print(f"{k:<36} ADJ {a['acc']} sort {a['acc_diffsort'][0]:.3f} D {a['D']} "
              f"{a['vs_sort']}/{a['vs_chance']}", flush=True)
    (OUT / "sim-posthoc.json").write_text(json.dumps(dict(
        note="POST-HOC (CHANGES 2026-10-08 (2)); gates nothing; the registered floor stays FAILED",
        cells=out), indent=2) + "\n")


def sim_verdicts(cells):
    v = {}
    for est in ("ORDER-ADJ", "ORDER-RAW", "SCOVA-NEXT", "SCOVA-POST"):
        def c(m, r, o):
            return cells[f"{m}/{r}/{o}"].get(est, {})
        f1 = all(c(m, "INVERTED", "RANDOM").get("vs_sort") == "ADDS" for m in ("AND", "OR"))
        f2 = all(c(m, r, "RANDOM").get("vs_chance") == "ORIENTS" for m in ("AND", "OR") for r in REGIMES)
        f3 = all(c("NULL", r, "RANDOM").get("vs_chance") == "CHANCE" for r in REGIMES)
        conf = {}
        for o in ("ABILITY", "CURRICULUM", "SKIP"):
            null_bad = [r for r in REGIMES if c("NULL", r, o).get("vs_chance") in ("ORIENTS", "REVERSED")]
            rev = [f"{m}/{r}" for m in ("AND", "OR") for r in REGIMES
                   if c(m, r, o).get("vs_chance") == "REVERSED"]
            conf[o] = dict(verdict="FOOLED BY ORDER CHOICE" if (null_bad or rev) else "NOT FOOLED",
                           null_oriented_in=null_bad, true_edges_reversed_in=rev)
        floor = f1 and f2 and f3
        head = "ORIENTS BEYOND DIFFICULTY UNDER RANDOM ORDER" if floor else "FLOOR FAILED"
        fooled = any(conf[o]["verdict"].startswith("FOOLED") for o in ("ABILITY", "SKIP"))
        head += "; ABILITY-DRIVEN ORDER FOOLS IT" if fooled else "; ABILITY-DRIVEN ORDER DOES NOT FOOL IT"
        v[est] = dict(floor=dict(passes=floor, adds_inverted_random=f1,
                                 orients_all_random=f2, null_random_chance=f3),
                      confounding=conf, headline=head)
    return v


# =========================================================================== parts 2-3: real data

def load_events(corpus, counts):
    """(learner, unit, time, correct) per corpus, plus a cluster id per learner and a reference."""
    from shared.paths import data_path
    import shared.corpus as C
    if corpus == "ednet":
        src = C.EdNet(data_path("EDNET_ZIP"), data_path("EDNET_CONTENTS"),
                      learners=EDNET_LEARNERS, tags="first")
        return src.events(), None
    if corpus == "eedi":
        src = C.Eedi(data_path("EEDI_ANSWERS"), data_path("EEDI_ZIP"))
        return src.events(), None
    if corpus == "assist":
        cmap = ROOT / "studies/measurement/assist2012-direction/out/skill_ccss_map.json"
        src = C.Assistments2012(data_path("ASSIST_DIR"), ccss_map=cmap, with_cohorts=True)
        return src.events(), src
    if corpus == "junyi":
        sys.path.insert(0, str(ROOT / "studies/simulation/orientation-sortability"))
        import sortability as so
        return so.ds1275_events(data_path("DS1275_DIR"), counts), None
    raise ValueError(corpus)


def reference(corpus, units, src):
    """{(lo, hi) unit-index pair: +1 if the reference orients lo -> hi, -1 if hi -> lo}."""
    ref = {}
    if corpus == "assist":
        grade = {i: src.position(u) for i, u in enumerate(units)}
        g = {i: x for i, x in grade.items() if x is not None}
        ids = sorted(g)
        for x in ids:
            for y in ids:
                if x < y and g[x] != g[y]:
                    ref[(x, y)] = 1 if g[x] < g[y] else -1
    elif corpus == "junyi":
        from shared.paths import data_path
        from shared.junyi_graph import authored_edges
        ix = {u: i for i, u in enumerate(units)}
        for p, n in authored_edges(data_path("JUNYI_DIR")):
            if p in ix and n in ix and p != n:
                a, b = ix[p], ix[n]
                k = (min(a, b), max(a, b))
                if k in ref and ref[k] != (1 if a < b else -1):
                    ref[k] = 0          # authored both ways: no reference direction
                else:
                    ref[k] = 1 if a < b else -1
        ref = {k: v for k, v in ref.items() if v != 0}
    return ref


def build(corpus, with_outcomes):
    """Per-learner sequences -> pair rows. With with_outcomes=False only (pid, af, learner) are
    built and no correctness value is touched (positivity)."""
    counts = defaultdict(int)
    ev, src = load_events(corpus, counts)
    by = defaultdict(list)
    uix, units = {}, []
    lix, learners = {}, []
    for k, (learner, unit, t, ok) in enumerate(ev):
        if unit not in uix:
            uix[unit] = len(units)
            units.append(unit)
        if learner not in lix:
            lix[learner] = len(learners)
            learners.append(learner)
        by[lix[learner]].append((t, k, uix[unit], ok if with_outcomes else 0.0))
        counts["events"] += 1
    U = len(units)
    L = len(learners)
    # per learner: attempts in time order (file order breaks ties)
    seqs = {}
    first_n = np.zeros(U)
    first_s = np.zeros(U)
    att_n = np.zeros(U)
    att_s = np.zeros(U)
    for li, lst in by.items():
        lst.sort(key=lambda r: (r[0], r[1]))
        t = [r[0] for r in lst]
        u = np.array([r[2] for r in lst], np.int64)
        c = np.array([r[3] for r in lst], float)
        seqs[li] = (t, u, c)
        _, fi = np.unique(u, return_index=True)
        np.add.at(first_n, u[fi], 1)
        np.add.at(first_s, u[fi], c[fi])
        np.add.at(att_n, u, 1)
        np.add.at(att_s, u, c)
    by.clear()
    fmean = np.where(first_n > 0, first_s / np.maximum(first_n, 1), np.nan)
    amean = np.where(att_n > 0, att_s / np.maximum(att_n, 1), np.nan)

    cluster = np.arange(L)
    if corpus == "assist" and src is not None:
        cid = {}
        for li, name in enumerate(learners):
            co = src.cohort(name)
            cluster[li] = cid.setdefault(co if co is not None else ("solo", name), len(cid))

    cols = defaultdict(list)
    fa_rows = []          # (learner, unit, first correct) for bootstrap difficulty
    for li, (t, u, c) in seqs.items():
        uu, fi = np.unique(u, return_index=True)
        order = np.argsort(fi, kind="stable")
        mu = uu[order]                     # units in first-meeting order
        mf = fi[order]                     # index of first attempt in the sequence
        mt = [t[i] for i in mf]
        m = len(mu)
        fa_rows.append((np.full(m, li), mu, c[mf]))
        if m < PRIOR_MIN + 2:
            continue
        rf = c[mf] - fmean[mu]
        cp = np.r_[0.0, np.cumsum(rf)]
        # Y3: mean of the first K attempts at each unit
        y3 = np.zeros(m)
        if with_outcomes:
            pos_in = {x: j for j, x in enumerate(mu)}
            sums = np.zeros(m)
            cnts = np.zeros(m)
            for x, cc in zip(u, c):
                j = pos_in[x]
                if cnts[j] < K:
                    sums[j] += cc
                    cnts[j] += 1
            y3 = sums / np.maximum(cnts, 1)
        ra = c - amean[u]
        ca = np.r_[0.0, np.cumsum(ra)]
        n_att = len(u)
        I, J = np.triu_indices(m, 1)
        keep = I >= PRIOR_MIN
        I, J = I[keep], J[keep]
        tI = np.array(mt, dtype=object)[I]
        tJ = np.array(mt, dtype=object)[J]
        keep = tI != tJ                     # equal first times: no order, dropped
        counts["pair_rows_tied_time"] += int((~keep).sum())
        I, J = I[keep], J[keep]
        if not len(I):
            continue
        a, b = mu[I], mu[J]                 # a met first
        lo = np.minimum(a, b)
        hi = np.maximum(a, b)
        cols["key"].append(lo * U + hi)
        cols["af"].append((a == lo).astype(np.float32))
        cols["learner"].append(np.full(len(I), li, np.int32))
        cols["prior"].append((cp[I] / I).astype(np.float32))
        cols["lnp"].append(np.log1p(I).astype(np.float32))
        if with_outcomes:
            cols["y"].append((y3[I] + y3[J]).astype(np.float32))
            s = mf[J] + 1
            e = np.minimum(s + W_NEXT, n_att)
            cnt = e - s
            cols["next"].append(np.where(cnt >= MIN_NEXT, (ca[e] - ca[s]) / np.maximum(cnt, 1),
                                         np.nan).astype(np.float32))
    seqs.clear()
    rows = {k: np.concatenate(v) for k, v in cols.items()}
    keys, pid = np.unique(rows.pop("key"), return_inverse=True)
    rows["pid"] = pid.astype(np.int64)
    for k in ("af", "prior", "lnp", "y", "next"):
        if k in rows:
            rows[k] = rows[k].astype(float)
    fa = tuple(np.concatenate(x) for x in zip(*fa_rows))
    meta = dict(units=units, n_units=U, n_learners=L, keys=keys, fmean=fmean, cluster=cluster,
                first_attempts=fa, counts=dict(counts), src=src)
    return rows, meta


def positivity_counts(rows, meta, corpus):
    n_pairs = len(meta["keys"])
    pid, af = rows["pid"], rows["af"]
    n1 = np.bincount(pid, af, minlength=n_pairs)
    n0 = np.bincount(pid, 1 - af, minlength=n_pairs)
    mn = np.minimum(n1, n0)
    elig = mn >= MIN_ARM
    U = meta["n_units"]
    out = dict(n_learners=meta["n_learners"], n_units=U, n_pairs_with_rows=int(n_pairs),
               n_pair_rows=int(len(pid)),
               n_eligible_pairs=int(elig.sum()),
               median_minority_arm_all=float(np.median(mn)) if n_pairs else 0.0,
               median_minority_arm_eligible=float(np.median(mn[elig])) if elig.any() else 0.0,
               counts=meta["counts"])
    if corpus in ("assist", "junyi"):
        ref = reference(corpus, meta["units"], meta["src"])
        kk = {int(k): i for i, k in enumerate(meta["keys"])}
        rp = [kk.get(lo * U + hi) for (lo, hi) in ref]
        rp = [i for i in rp if i is not None]
        out["n_reference_pairs"] = len(ref)
        out["n_reference_pairs_with_rows"] = len(rp)
        out["n_eligible_reference_pairs"] = int(sum(elig[i] for i in rp))
        n_el = out["n_eligible_reference_pairs"]
    else:
        n_el = out["n_eligible_pairs"]
    order_ok = corpus != "eedi"
    out["first_meeting_order_recorded"] = order_ok
    out["read_in_part3"] = bool(order_ok and n_el >= MIN_PAIRS)
    out["reason"] = ("last-answer time: first-meeting order not recorded (pre-registered exclusion)"
                     if not order_ok else
                     (f">= {MIN_PAIRS} eligible {'reference ' if corpus in ('assist', 'junyi') else ''}pairs"
                      if out["read_in_part3"] else f"< {MIN_PAIRS} eligible pairs: UNANSWERABLE"))
    return out


def positivity_light(corpus):
    """Same counts as build() + positivity_counts(), from first times only (CHANGES 4)."""
    counts = defaultdict(int)
    ev, src = load_events(corpus, counts)
    first = {}
    uix, units = {}, []
    lix = {}
    for k, (learner, unit, t, _ok) in enumerate(ev):     # outcome not read
        u = uix.setdefault(unit, len(uix))
        if u == len(units):
            units.append(unit)
        li = lix.setdefault(learner, len(lix))
        key = (li, u)
        cur = first.get(key)
        if cur is None or (t, k) < cur:
            first[key] = (t, k)
        counts["events"] += 1
    U = len(units)
    by = defaultdict(list)
    for (li, u), (t, k) in first.items():
        by[li].append((t, k, u))
    first.clear()
    n_lo = np.zeros(U * U)
    n_hi = np.zeros(U * U)
    for li, lst in by.items():
        lst.sort()
        m = len(lst)
        if m < PRIOR_MIN + 2:
            continue
        mu = np.array([r[2] for r in lst], np.int64)
        mt = np.array([r[0] for r in lst], dtype=object)
        I, J = np.triu_indices(m, 1)
        keep = I >= PRIOR_MIN
        I, J = I[keep], J[keep]
        keep = mt[I] != mt[J]
        counts["pair_rows_tied_time"] += int((~keep).sum())
        I, J = I[keep], J[keep]
        a, b = mu[I], mu[J]
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        key = lo * U + hi
        lf = a == lo
        n_lo += np.bincount(key[lf], minlength=U * U)
        n_hi += np.bincount(key[~lf], minlength=U * U)
    has = (n_lo + n_hi) > 0
    mn = np.minimum(n_lo, n_hi)[has]
    elig_keys = set(np.flatnonzero(has & (np.minimum(n_lo, n_hi) >= MIN_ARM)).tolist())
    out = dict(n_learners=len(lix), n_units=U, n_pairs_with_rows=int(has.sum()),
               n_pair_rows=int((n_lo + n_hi).sum()), n_eligible_pairs=len(elig_keys),
               median_minority_arm_all=float(np.median(mn)) if len(mn) else 0.0,
               median_minority_arm_eligible=float(np.median(mn[mn >= MIN_ARM])) if (mn >= MIN_ARM).any() else 0.0,
               counts=dict(counts), method="positivity_light (CHANGES 4)")
    if corpus in ("assist", "junyi"):
        ref = reference(corpus, units, src)
        out["n_reference_pairs"] = len(ref)
        out["n_reference_pairs_with_rows"] = int(sum(has[lo * U + hi] for lo, hi in ref))
        out["n_eligible_reference_pairs"] = int(sum((lo * U + hi) in elig_keys for lo, hi in ref))
        n_el = out["n_eligible_reference_pairs"]
    else:
        n_el = out["n_eligible_pairs"]
    order_ok = corpus != "eedi"
    out["first_meeting_order_recorded"] = order_ok
    out["read_in_part3"] = bool(order_ok and n_el >= MIN_PAIRS)
    out["reason"] = ("last-answer time: first-meeting order not recorded (pre-registered exclusion)"
                     if not order_ok else (">= 30 eligible pairs" if out["read_in_part3"]
                                           else f"< {MIN_PAIRS} eligible pairs: UNANSWERABLE"))
    return out


def main_positivity(corpora, light=False):
    assert selftest()
    path = OUT / "positivity.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for corpus in corpora:
        t0 = time.time()
        if light:
            r = positivity_light(corpus)
            if corpus in res:          # equivalence check against build()
                for k in ("n_pairs_with_rows", "n_pair_rows", "n_eligible_pairs",
                          "n_eligible_reference_pairs"):
                    print("check", k, res[corpus].get(k), r.get(k))
                    assert res[corpus].get(k) == r.get(k), k
                continue
            res[corpus] = r
        else:
            rows, meta = build(corpus, with_outcomes=False)
            res[corpus] = positivity_counts(rows, meta, corpus)
        res[corpus]["seconds"] = round(time.time() - t0)
        print(corpus, json.dumps(res[corpus], default=str), flush=True)
        OUT.mkdir(exist_ok=True)
        path.write_text(json.dumps(res, indent=2, default=str) + "\n")


# --------------------------------------------------------------------------- real reading

def skill_boot(units_lo, units_hi, vals, U, rng, reps):
    """Units resampled with replacement; each pair weighted c_lo * c_hi. vals: (n_stats, n_pairs)."""
    out = []
    for _ in range(reps):
        c = np.bincount(rng.integers(0, U, U), minlength=U).astype(float)
        w = c[units_lo] * c[units_hi]
        if w.sum() == 0:
            continue
        out.append((vals * w).sum(1) / w.sum())
    return np.array(out)


def pct(a):
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


def stats_for(calls, ds_calls, ref_truth):
    """Pair-level score vectors: AGREE with DIFFSORT, ACC_O and ACC_D vs reference (on ref pairs)."""
    agree = np.where((calls == 0) | (ds_calls == 0), 0.5, (calls == ds_calls).astype(float))
    if ref_truth is None:
        return dict(agree=agree)
    return dict(agree=agree, acc_o=score_vs(calls, ref_truth), acc_d=score_vs(ds_calls, ref_truth))


def diffsort_calls(fmean, lo, hi):
    """+1 if lo is easier (higher first-attempt accuracy) -> orient lo -> hi."""
    a, b = fmean[lo], fmean[hi]
    return np.where(a == b, 0, np.where(a > b, 1, -1))


def weighted_fmean(fa, w_learner, U):
    li, u, c = fa
    w = w_learner[li]
    n = np.bincount(u, w, minlength=U)
    s = np.bincount(u, w * c, minlength=U)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 0, s / n, np.nan)


def quintiles(x):
    q = np.quantile(x, [0.2, 0.4, 0.6, 0.8])
    return np.searchsorted(q, x).astype(np.int64)


def real_reading(corpus, rows, meta, sim_conf, rng):
    U = meta["n_units"]
    keys = meta["keys"]
    n_pairs = len(keys)
    lo_all, hi_all = keys // U, keys % U
    pid, af = rows["pid"], rows["af"]
    covs = [rows["prior"], rows["lnp"]]
    n1 = np.bincount(pid, af, minlength=n_pairs)
    n0 = np.bincount(pid, 1 - af, minlength=n_pairs)
    elig = np.minimum(n1, n0) >= MIN_ARM
    has_ref = corpus in ("assist", "junyi")
    truth_all = np.zeros(n_pairs)
    if has_ref:
        ref = reference(corpus, meta["units"], meta["src"])
        kk = {int(k): i for i, k in enumerate(keys)}
        for (lo, hi), d in ref.items():
            i = kk.get(lo * U + hi)
            if i is not None:
                truth_all[i] = d
        sel = elig & (truth_all != 0)
    else:
        sel = elig
    # restrict rows to eligible pairs (all later computations are on them)
    keep = elig[pid]
    newid = -np.ones(n_pairs, np.int64)
    eidx = np.flatnonzero(elig)
    newid[eidx] = np.arange(len(eidx))
    pid_e = newid[pid[keep]]
    R = {k: v[keep] for k, v in rows.items()}
    R["pid"] = pid_e
    learner = R["learner"]
    ne = len(eidx)
    lo, hi = lo_all[eidx], hi_all[eidx]
    truth = truth_all[eidx]
    refsel = sel[eidx]
    out = dict(n_eligible_pairs=int(ne), n_rows=int(len(pid_e)),
               n_eligible_reference_pairs=int(refsel.sum()) if has_ref else None)

    def estimate(y, w=None, af_=None, mask=None):
        a = R["af"] if af_ is None else af_
        if mask is None:
            return pair_ols(pid_e, ne, a, y, [c[keep] for c in covs], w)
        return pair_ols(pid_e[mask], ne, a[mask], y[mask], [c[keep][mask] for c in covs],
                        None if w is None else w[mask])

    coef, se, _ = estimate(R["y"])
    raw, _, _ = pair_ols(pid_e, ne, R["af"], R["y"], [])
    mnext = ~np.isnan(R["next"])
    nxt, _, _ = estimate(np.nan_to_num(R["next"]), mask=mnext)
    ds = diffsort_calls(meta["fmean"], lo, hi)
    z2 = (coef / se) ** 2
    T = float(np.nanmean(z2))
    sm = smd(pid_e, ne, R["af"], R["prior"])
    balance = float(np.nanmedian(np.abs(sm)))
    out["balance_median_abs_smd_prior"] = balance
    out["signal_T_mean_z2"] = T
    out["median_abs_A"] = float(np.nanmedian(np.abs(coef)))

    def summary(c_calls, label):
        st = stats_for(c_calls, ds, truth if has_ref else None)
        r = dict(agree=float(st["agree"].mean()))
        if has_ref:
            r["acc_o"] = float(st["acc_o"][refsel].mean())
            r["acc_d"] = float(st["acc_d"][refsel].mean())
            r["D"] = r["acc_o"] - r["acc_d"]
            disc = refsel & (c_calls != 0) & (ds != 0) & (c_calls != ds)
            r["n_discordant"] = int(disc.sum())
            r["discordant_order_follows_reference"] = (float(st["acc_o"][disc].mean())
                                                        if disc.any() else None)
        return r, st

    main, st_main = summary(call(coef), "ORDER-ADJ")
    # SKILL interval
    vals = [st_main["agree"]]
    names = ["agree"]
    if has_ref:
        s_ = refsel.astype(float)
        vals_ref = np.stack([st_main["acc_o"] * s_, st_main["acc_d"] * s_, s_])
    sb = skill_boot(lo, hi, np.stack(vals), U, rng, BOOT_SKILL)
    main["skill_ci"] = {"agree": pct(sb[:, 0])}
    if has_ref:
        sr = skill_boot(lo, hi, vals_ref, U, rng, BOOT_SKILL)
        sr = sr[sr[:, 2] > 0]
        ao, ad = sr[:, 0] / sr[:, 2], sr[:, 1] / sr[:, 2]
        main["skill_ci"].update(acc_o=pct(ao), acc_d=pct(ad), D=pct(ao - ad))
    # LEARNER (cluster) interval
    cl = meta["cluster"]
    ncl = int(cl.max()) + 1
    lb = []
    for _ in range(BOOT_LEARNER):
        wc = rng.poisson(1.0, ncl).astype(float)
        wl = wc[cl]
        c_b, _, _ = estimate(R["y"], w=wl[learner])
        fm = weighted_fmean(meta["first_attempts"], wl, U)
        ds_b = diffsort_calls(fm, lo, hi)
        cb = call(c_b)
        agree = np.where((cb == 0) | (ds_b == 0), 0.5, (cb == ds_b).astype(float)).mean()
        row = [agree]
        if has_ref:
            ao = score_vs(cb, truth)[refsel].mean()
            ad = score_vs(ds_b, truth)[refsel].mean()
            row += [ao, ad, ao - ad]
        lb.append(row)
    lb = np.array(lb)
    main["learner_ci"] = {"agree": pct(lb[:, 0])}
    if has_ref:
        main["learner_ci"].update(acc_o=pct(lb[:, 1]), acc_d=pct(lb[:, 2]), D=pct(lb[:, 3]))
    main["learner_ci_unit"] = "cohort (class proxy)" if corpus == "assist" else "learner"
    out["ORDER-ADJ"] = main
    out["ORDER-RAW"] = summary(call(raw), "ORDER-RAW")[0]
    out["SCOVA-NEXT"] = summary(call(nxt), "SCOVA-NEXT")[0]
    # CONTROL: deranged within (pair, prior quintile)
    strata = quintiles(R["prior"])
    ctrl = []
    for _ in range(N_DERANGE):
        afd = derange_labels(pid_e, strata, R["af"], rng)
        c_d, se_d, _ = estimate(R["y"], af_=afd)
        r, _ = summary(call(c_d), "CONTROL")
        r["T"] = float(np.nanmean((c_d / se_d) ** 2))
        ctrl.append(r)
    out["control"] = {k: [float(np.mean([c[k] for c in ctrl if c.get(k) is not None])),
                          float(np.min([c[k] for c in ctrl if c.get(k) is not None])),
                          float(np.max([c[k] for c in ctrl if c.get(k) is not None]))]
                      for k in ctrl[0] if isinstance(ctrl[0][k], float)}
    signal = T > max(c["T"] for c in ctrl)
    out["signal_present"] = bool(signal)
    if corpus == "assist":
        out["signal_note"] = ("order is set per class; the learner-level derangement is too narrow "
                              "a null, so this SIGNAL line is descriptive and no verdict uses it")
    # REAL-SHAPED FLOOR
    out["floor"] = real_floor(corpus, R, pid_e, ne, lo, hi, truth, refsel, has_ref, ds, strata,
                              covs, keep, U, rng)
    out["verdict"] = real_verdict(corpus, out, sim_conf, has_ref)
    return out


def real_floor(corpus, R, pid_e, ne, lo, hi, truth, refsel, has_ref, ds, strata, covs, keep, U, rng):
    res = {}
    for delta in FLOOR_DELTAS:
        rec, beyond, excl = 0, 0, 0
        for _ in range(FLOOR_REPS):
            planted = np.where(has_ref & (truth != 0), truth,
                               np.where(rng.random(ne) < 0.5, 1, -1)) if has_ref else \
                np.where(rng.random(ne) < 0.5, 1, -1)
            afd = derange_labels(pid_e, strata, R["af"], rng)
            p_row = planted[pid_e]
            # lo-first arm gains delta if planted lo -> hi; hi-first arm gains delta otherwise
            y = R["y"] + delta * np.where(p_row > 0, afd, 1 - afd)
            c, _, _ = pair_ols(pid_e, ne, afd, y, [x[keep] for x in covs])
            cc = call(c)
            sc = score_vs(cc, planted)
            selm = refsel if has_ref else np.ones(ne, bool)
            s_ = selm.astype(float)
            if has_ref:
                vals = np.stack([sc * s_, score_vs(ds, truth) * s_, s_])
            else:
                vals = np.stack([sc * s_, s_ * 0, s_])
            sb = skill_boot(lo, hi, vals, U, rng, BOOT_FLOOR)
            sb = sb[sb[:, 2] > 0]
            acc_b = sb[:, 0] / sb[:, 2]
            alo, ahi = np.percentile(acc_b, [2.5, 97.5])
            rec += alo > 0.5
            excl += (alo > 0.5) or (ahi < 0.5)
            if has_ref:
                Db = acc_b - sb[:, 1] / sb[:, 2]
                Dlo = np.percentile(Db, 2.5)
                Dp = sc[selm].mean() - score_vs(ds, truth)[selm].mean()
                beyond += (Dlo > 0) and (Dp > MARGIN)
        res[str(delta)] = dict(recovered=rec / FLOOR_REPS, excludes_half=excl / FLOOR_REPS,
                               beyond=(beyond / FLOOR_REPS) if has_ref else None)
    top = res[str(FLOOR_DELTAS[-1])]
    ok = (top["recovered"] >= 0.8 and (not has_ref or top["beyond"] >= 0.8)
          and res["0.0"]["excludes_half"] <= 0.10)
    mdd = None
    for delta in FLOOR_DELTAS[1:]:
        r = res[str(delta)]
        if r["recovered"] >= 0.8 and (not has_ref or r["beyond"] >= 0.8):
            mdd = delta
            break
    res["passes"] = bool(ok)
    res["min_detectable_delta"] = mdd
    return res


def real_verdict(corpus, out, sim_conf, has_ref):
    m = out["ORDER-ADJ"]
    fooled = any(sim_conf[o]["verdict"].startswith("FOOLED") for o in ("ABILITY", "SKIP"))
    if has_ref:
        D = m["D"]
        lci, sci = m["learner_ci"]["D"], m["skill_ci"]["D"]
        if lci[0] > 0 and sci[0] > 0 and D > MARGIN:
            computed = "ORIENTS BEYOND DIFFICULTY"
        elif lci[1] < 0 and sci[1] < 0:
            computed = "WORSE THAN DIFFICULTY"
        elif lci[1] <= MARGIN and sci[1] <= MARGIN:
            computed = "NO BETTER THAN DIFFICULTY"
        else:
            computed = "UNDECIDED"
        if not out["floor"]["passes"] and computed in ("NO BETTER THAN DIFFICULTY", "UNDECIDED"):
            computed = "UNDERPOWERED"
    else:
        lci, sci = m["learner_ci"]["agree"], m["skill_ci"]["agree"]
        if lci[0] > 0.5 + MARGIN and sci[0] > 0.5 + MARGIN:
            computed = "ORDER ORIENTATION FOLLOWS DIFFICULTY"
        elif lci[1] < 0.5 and sci[1] < 0.5:
            computed = "ORDER ORIENTATION AGAINST DIFFICULTY"
        else:
            computed = "ORDER ORIENTATION INDEPENDENT OF DIFFICULTY"
            if not out["floor"]["passes"]:
                computed = "UNDERPOWERED"
        computed += (" (ORDER SIGNAL PRESENT)" if out["signal_present"]
                     else " (NO ORDER SIGNAL ABOVE CONTROL)")
    if fooled and out["balance_median_abs_smd_prior"] >= SMD_CONFOUND:
        return dict(verdict="CONFOUNDED BY ORDER CHOICE", computed_reading=computed)
    return dict(verdict=computed, computed_reading=computed)


def main_real(corpora):
    assert selftest()
    sim = json.loads((OUT / "sim.json").read_text())
    pos = json.loads((OUT / "positivity.json").read_text())
    adj = sim["verdicts"]["ORDER-ADJ"]
    path = OUT / "real.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for corpus in corpora:
        p = pos[corpus]
        if not p["read_in_part3"]:
            res[corpus] = dict(verdict=dict(verdict="UNANSWERABLE", reason=p["reason"]))
        else:
            t0 = time.time()
            rng = np.random.default_rng([SEED, 3, sorted(pos).index(corpus)])
            rows, meta = build(corpus, with_outcomes=True)
            res[corpus] = real_reading(corpus, rows, meta, adj["confounding"], rng)
            res[corpus]["seconds"] = round(time.time() - t0)
            if not adj["floor"]["passes"]:      # CHANGES 2026-10-08 (3)
                v = res[corpus]["verdict"]
                res[corpus]["verdict"] = dict(
                    verdict="UNANSWERABLE", reason="simulation floor failed (registered rule)",
                    computed_reading_descriptive=v["verdict"],
                    computed_reading_before_confounding_rule=v["computed_reading"])
        print(corpus, json.dumps(res[corpus], default=str), flush=True)
        OUT.mkdir(exist_ok=True)
        path.write_text(json.dumps(res, indent=2, default=str) + "\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=("sim", "sim-posthoc", "positivity", "real", "selftest"))
    ap.add_argument("--corpora", default="ednet,eedi,assist,junyi")
    ap.add_argument("--light", action="store_true", help="positivity: memory-light count (CHANGES 4)")
    args = ap.parse_args()
    cs = args.corpora.split(",")
    if args.part == "sim":
        main_sim()
    elif args.part == "sim-posthoc":
        main_sim_posthoc()
    elif args.part == "positivity":
        main_positivity(cs, args.light)
    elif args.part == "real":
        main_real(cs)
    else:
        print("selftest", selftest())
