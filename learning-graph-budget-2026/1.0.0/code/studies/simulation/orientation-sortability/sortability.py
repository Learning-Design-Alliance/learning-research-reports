"""
Does the orientation finding (Paper II, F2) say more than "sort the skills by difficulty"?

PRE-REGISTRATION. Written 2026-10-07, before any number in this file was computed, synthetic or
real. Design committed before the floor and the sweep run; nothing on real data is read before that
commit. Author: Claude Opus 5.5 (session 01GTZaPFRRea1VKMWeMZogHX), working overnight from
`scratchpad/analyses/BRIEF.md`; every decision the maintainer would otherwise have made is recorded
here and marked DECISION.

WHY. F2 rests on `studies/simulation/learner-sim/orientation_soft.py` (and its parent
`orientation_difficulty.py`): the signed marginal asymmetry
    s(a, b) = P(fail b | fail a) - P(fail a | fail b),     s > 0  =>  orient a -> b
orients true edges at 0.77-1.00 (all pairs) depending on mechanism (prerequisite hardness) and on
how difficulty relates to depth (ALIGNED / INDEPENDENT / INVERTED). The literature review
(`research/readiness/learning-graph-budget-2026/literature.md`, strand 2 entries 2.1-2.3 and strand-2
analyses items 2-3; synthesis rank 3) says this has the structure of a known result:
  2.1 Verma & Pearl (1990): a chain is not oriented by conditional independence alone, so any
      pairwise orientation rides on distributional assumptions of the generator.
  2.2 Reisach, Seiler & Weichwald (2021): simulated orientation success can track VARSORTABILITY,
      the agreement of the causal order with increasing marginal variance; a trivial sort matches
      the algorithms. Difficulty rising with depth is the education analogue.
  2.3 Reisach et al. (2023): even scale-free, R^2 (the share of a variable explained by all the
      others) tends to rise along the causal order; "R^2-SortnRegress" is a baseline any
      orientation statistic must beat. Their recommendation: report the sortability of the
      generator and claim only what the statistic adds beyond it.
So the question is: in each mechanism x difficulty regime of the existing sweep, what do the two
sorting baselines score, and does the asymmetry statistic beat them?

THREE PARTS.

(a) SORTABILITY BASELINES ON THE EXISTING SWEEP (synthetic; no corpus).
    Grid, seeds, graphs and learners are those of orientation_soft.py EXACTLY: 3 regimes x 5
    hardness levels (1.0 = conjunctive gate ... 0.0 = load only), 15 worlds per cell seeded
    random.Random(3300 + w), 30 nodes, edge prob 0.08, 3,000 learners, slip 0.12, guess 0.15. The
    world and learner generators are imported from that study, not copied, and the asymmetry
    accuracies are REQUIRED to reproduce `orientation-soft-result.json` to 1e-12 (REPRO check);
    if they do not, nothing else in part (a) is read.
    On the same learners and the same edge set the asymmetry statistic scores (true edges for
    which s is defined and non-zero, as od.score does), three orientations are scored per edge:
      ASYM     s(a, b) > 0                                      (the existing statistic)
      DIFFSORT orient from the easier to the harder skill: observed P(correct a) > P(correct b)
      R2SORT   orient from lower to higher R^2, R^2 of each skill's 0/1 state regressed (OLS with
               intercept, linear probability) on all 29 other skills
    Ties in a baseline score 0.5 (DECISION: a coin flip, not an exclusion, so the baseline is never
    flattered by dropping its hard cases). The difficulty-MATCHED subset (|fail a - fail b| <= 0.05,
    od.MATCH_TOL) is scored the same way and reported descriptively (n is 17-21 in ALIGNED cells).
    Also reported per cell, as the generator's own sortability: the share of edges whose LATENT
    difficulty rises along the edge, and Spearman(depth, latent difficulty) over nodes.

    ESTIMAND. Per cell, D = acc(ASYM) - acc(DIFFSORT) (and D_R2 against R2SORT), pooled over the
    cell's 15 worlds. SIGNED: D > 0 means the asymmetry statistic beats the sort.
    INTERVAL. 95% percentile bootstrap resampling WORLDS (the unit the generator assigns a graph,
    a difficulty draw and a learner sample to; edges within a world share all three), 2,000 draws,
    paired (both accuracies on the same resample). DECISION: 15 worlds is what F2 was measured on;
    the brief asks for the same seeds, so the world count is not raised. That makes the intervals
    wide, and the floor below says how wide.

    PRE-REGISTERED CELL READINGS (margin m = 0.02):
      ADDS       D's interval lower bound > 0 and D > m
      NO BETTER  D's interval upper bound <= m        (WORSE if the upper bound < 0)
      UNDECIDED  otherwise
      CEILING    acc(DIFFSORT) >= 0.95: the sort leaves at most 0.05 to beat; read but excluded
                 from the headline
    PRE-REGISTERED HEADLINE (conjunctive/soft mechanism = the existing F2 sweep, 15 cells), against
    DIFFSORT; the same rule against R2SORT is the secondary verdict:
      "F2 REDUCES TO DIFFICULTY SORTABILITY"   every non-CEILING cell reads NO BETTER.
          MEANING, written before the run: the mechanism x regime grid is then a map of how
          sortable each generator is, not of what the asymmetry statistic knows about dependency;
          Paper II must say that the statistic orients no better than sorting skills by observed
          difficulty and must not describe it as reading direction from dependency.
      "F2 ADDS BEYOND DIFFICULTY SORTABILITY"  every non-CEILING cell where ASYM beats chance (its
          own world-bootstrap lower bound > 0.5) reads ADDS.
          MEANING: the statistic carries direction information beyond the marginal difficulty
          order, in the regimes where it orients at all; F2's grid can be presented as the
          prerequisite-graph case of Reisach et al. with the statistic's increment stated.
      "F2 PARTLY REDUCES TO DIFFICULTY SORTABILITY"  otherwise; the cells that are NO BETTER and
          those that ADD are listed by name, and only the ADDS cells may be quoted as orientation
          beyond sortability.
      "UNANSWERABLE"  REPRO fails, or the floor's ADDS power fails at every planted size.

(b) A DISJUNCTIVE (OR, DINO-type) ARM (synthetic; no corpus).
    (b1) Orientation. Same worlds and learner count; one change to the learner generator: a node is
    blocked (with probability `hardness`, else load-penalised as in orientation_soft) only when
    it holds NONE of its prerequisites; holding any one suffices. For single-parent nodes this is
    identical to the conjunctive generator, so the OR arm is ALSO reported on edges into fan-in >= 2
    nodes only, beside the conjunctive arm on the same subset. The same three orientations, D,
    intervals and cell readings; headline rule as in (a), reported as the "OR ARM" verdict.
    Rng: each world's rng is random.Random(3300 + w), so the worlds are the same graphs and
    difficulties; learner draws differ from the conjunctive arm because the generator consumes the
    stream differently (DECISION: unavoidable without a second stream, and the comparison is
    between arms, not between paired learners).
    (b2) The conjunctive-census reading. The programme's conjunction instrument is
    `studies/identifiability/conjunctive/stage1_floor.py`: pairwise drop for A, and
    interaction = (m_both - m_a_only) - (m_b_only - m_neither) against a learner-DERANGED null
    (the unit assigned the (A, B) state is the learner), "fires" iff interaction > null 97.5th
    percentile (ONE-SIDED, signed), and a pairwise reading is null iff |pairwise A| < 0.10. Its
    statistics() and deranged_null() are imported; a disjunctive simulate() is added beside its
    own: the 0.45 penalty applies unless A OR B is held (stage1's conjunctive applies it unless
    both are). Same grid (co-parent prevalence 0.2-0.8 x gate 0, 0.25, 0.5, 1.0), 4,000 learners,
    20 reps (STAGE1.md ran 20), seed 20261007. The null's 2.5th percentile is also kept.
    PRE-REGISTERED READINGS per OR arm (gate < 1):
      MISREAD AS CONJUNCTION    interaction > null 97.5th   (the census calls OR an AND gate)
      NEGATIVE INTERACTION      interaction < null 2.5th    (a disjunction is visible, with the
                                opposite sign; the one-sided census records it as "no conjunction")
      INVISIBLE                 neither
    and, separately, how many OR arms the pairwise reading records as null. Expected sign, stated
    before the run: m_both = m_a_only = m_b_only, so interaction = -(m_b_only - m_neither) < 0, and
    the pairwise A drop is attenuated by the co-parent's PREVALENCE (the reverse corner from AND).
    CENSUS FLOOR: the same wrapper must reproduce stage1's verdict: >= 1 conjunctive arm fires and
    0 additive / none arms fire. If not, the OR reading is not reported as a census reading.

(c) WHERE REAL CORPORA SIT ON THE REGIME AXIS (reads corpora; after the design commit).
    Corpora, all read through shared.paths.data_path / shared.corpus / shared.junyi_graph:
      JUNYI 2015 (junyi2015-authored, $JUNYI_DIR, research use). Authored graph: the exercise
        table's `prerequisites` column via shared.junyi_graph.authored_edges (p -> name means p is
        a prerequisite of name). Difficulty: 1 - proportion correct on each learner's FIRST attempt
        at the exercise (Outcome CORRECT/INCORRECT, rows ordered by Time) in
        junyi_ProblemLog_for_PSLC.txt. DECISION: first attempts only, so practice within the log
        does not make heavily practised exercises look easy. The full log (ds1275) is DataShop
        login-gated and not held; this file is the small release sample, so coverage may be thin
        and the gate below decides.
        Depth: longest path from a root of the authored graph (as in the sim: 0 for a root,
        1 + max parent depth otherwise), on the strongly connected condensation if cycles exist
        (cycle members share a depth; the count is reported).
        SECONDARY, DESCRIPTIVE ONLY: the crowd raters' Difficulty_avg on annotated pairs that are
        authored edges (row (A, B): high = B harder than A; codebook junyi2015-authored). CODER: the
        Junyi 2015 crowd workers (Chang, Hsu & Chen 2015), averaged; no independent reference is
        computed here, so per CLAUDE.md it is a descriptive count and gates nothing.
      ASSISTMENTS 2012-13 (assist2012, $ASSIST_DIR, analysis only). No authored prerequisite graph
        is held for it (studies/outcomes/decision-model/evpi.py falls back to all ordered pairs;
        the corpus adapter carries none). The authored ORDER that is held is CCSS grade through
        studies/measurement/assist2012-direction/out/skill_ccss_map.json (a name match to EDM Cup's
        code table). Depth := CCSS grade; pairs := skills in different grades, lower grade -> higher.
        Exact-name tier (jaccard 1.0) reported as the sensitivity. Difficulty as for Junyi, from
        first attempts per learner per skill (shared.corpus.Assistments2012.events()).
      EEDI. No authored prerequisite graph is held: the NeurIPS 2020 subject tree is a taxonomy
        with no order (shared.corpus.Eedi: "position() is None: the subject tree carries no year or
        key stage"), and the NeurIPS 2022 Task 3 adjacency is not released or held (literature 2.6).
        Reported as NOT HELD; nothing is computed.
    ELIGIBILITY / POSITIVITY (before any estimate): a unit counts if >= 20 learners made a first
    attempt at it. Edge-level readings need >= 30 eligible edges (both ends eligible, depth
    defined); node-level readings need >= 30 eligible nodes spanning >= 2 depths. Below that the
    corpus reads UNANSWERABLE, not null.
    ESTIMANDS (both signed, both also computed in the sim cells so the axes are the same):
      S    edge difficulty-sortability: share of authored edges (pairs for ASSISTments) whose
           dependent is harder than its prerequisite, ties 0.5. This is DIFFSORT's accuracy on the
           real graph, i.e. the corpus's own varsortability analogue.
      rho  Spearman(depth, difficulty) over eligible nodes.
    INTERVALS: S resamples EDGES (Junyi) or SKILLS (ASSISTments: pairs share skills, so the skill
    is the unit; pairs are rebuilt from the resampled skills). rho, as the brief asks, is resampled
    over EDGES for Junyi (rho on the endpoint multiset of the resampled edges, so nodes weigh by
    degree) with the node-resampled interval as a sensitivity; over SKILLS for ASSISTments. 2,000
    draws, percentile.
    PRE-REGISTERED PLACEMENT VERDICTS per corpus (signed):
      "DIFFICULTY RISES WITH DEPTH (ALIGNED SIDE)"   rho lower > 0 AND S lower > 0.5
      "DIFFICULTY FALLS WITH DEPTH (INVERTED SIDE)"  rho upper < 0 AND S upper < 0.5
      "NO DIFFICULTY-DEPTH ORDER RESOLVED"           otherwise, when the floor passes
      "UNDERPOWERED"                                 otherwise, when the floor fails
      "UNANSWERABLE"                                 eligibility fails
    plus a descriptive placement: the sim cell (conjunctive arm) whose observed DIFFSORT accuracy
    is nearest the corpus's S, and that cell's ASYM-vs-DIFFSORT reading, which is what F2 implies
    for the corpus.
    FLOOR FOR (c) (synthetic, shaped like the eligible real set, run after the commit on the real
    eligible structure: its edges/pairs, depths and per-unit learner counts; outcomes are synthetic):
    plant latent difficulty = r * z(depth) + sqrt(1 - r^2) * noise, draw each unit's first-attempt
    successes Binomial(n_unit, logistic(-1.5 * difficulty)), 100 reps per r in {+0.3, 0, -0.3}.
    PASS iff for r = +/-0.3 both rho's and S's intervals exclude the null value WITH THE PLANTED
    SIGN in >= 80% of reps, and for r = 0 a wrong-signed exclusion occurs in <= 10%.
    DECISION: |r| = 0.3 is the planted size because the sim's own regimes differ by far more
    (ALIGNED vs INDEPENDENT latent Spearman ~0.9 vs ~0); a corpus that cannot see 0.3 cannot be
    placed. Floor reps use 400 bootstrap draws (stated reason: 600 floor intervals at 2,000 each
    does not change a pass/fail on an 80% bar and costs minutes per corpus on a shared machine).

FLOOR FOR (a)/(b1), synthetic, on the sweep's own edges. Can the paired world bootstrap see an
increment over DIFFSORT when there is one, and does it say NO BETTER when the statistic IS the
sort?
  PLANT-SORT  a statistic equal to DIFFSORT with random tie-breaks: must read NO BETTER in >= 95%
              of 50 reps in every non-CEILING cell.
  PLANT-ADD   a statistic equal to DIFFSORT where DIFFSORT is right, and right with probability q
              on edges where DIFFSORT is wrong, q set per cell so the expected increment is
              delta in {0.05, 0.10, 0.15}. Sized like the treatment: the observed unmatched-minus-
              matched gap in F2 is 0.07-0.23, so 0.05-0.15 spans the increments at issue.
              ADDS power = share of 50 reps reading ADDS. The minimum detectable increment is the
              smallest delta with power >= 0.80 in every non-CEILING cell.
  If power is below 0.80 at delta = 0.15, UNDECIDED cells are uninformative and the headline may
  only be REDUCES (if every cell is NO BETTER, which noise cannot produce) or UNANSWERABLE.
R2SORT IMPLEMENTATION CHECK: on a linear-Gaussian SEM over the same 30-node graphs (edge weights
+/-U(0.5, 2), unit noise, 3,000 draws), the setting in which Reisach et al. (2023) report high
R^2-sortability, R2SORT must orient >= 0.70 of true edges, and its accuracy must be identical on
standardised data (scale invariance). If it fails, R2SORT columns are labelled "not validated".

CONTROLS. The baselines are the controls: they are the confound (generator sortability) made into
an orientation rule, scored on the same edges, the same learners and the same resamples as the
treatment, so they are exactly the treatment's size. No permutation null is needed for an
orientation accuracy against a known truth (chance is 0.5 by symmetry of the label); the census
part keeps stage1's learner derangement.

WHAT THIS CAN SAY. Whether, inside the existing generator family, the asymmetry statistic orients
better than two trivial sorts; how a disjunctive prerequisite changes orientation and what the
conjunctive census records for it; and on which side of the regime axis each held authored
structure sits. WHAT IT CANNOT SAY. Whether real edges are oriented by the statistic (no real
orientation truth is used here); anything about Eedi; anything about ASSISTments as a GRAPH (only
grade order is held); and anything beyond this generator family (other generators may be more or
less sortable). The Junyi reading is on the small public log sample, not ds1275.

DATA HANDLING. Part (c) reads Junyi 2015 (research use) and ASSISTments 2012-13 (analysis only, no
redistribution) from the session scratchpad. Only aggregates are written: counts, correlations,
intervals. No learner rows, no item text, no skill names.

    python3 sortability.py sim      # floor + parts (a) and (b); synthetic only -> out/sim.json
    python3 sortability.py real     # part (c) with its floor -> out/real.json (Junyi from ds1275;
                                    #   --junyi-log public for the 999-row public sample)

CHANGES
  (no design change was made after the design commit)
  POST-RUN NOTE 2026-10-07 (not a design change; recorded after the sim run, before the real run).
  ASYM and DIFFSORT agreed on every scored edge of all 30 cells (D = 0, interval [0, 0]). That is an
  identity, not a simulation result. With f_x = P(fail x) and j = P(fail a AND fail b) on one
  population,  s(a, b) = j/f_a - j/f_b = j (f_b - f_a) / (f_a f_b),  so whenever j > 0 the sign of s
  is the sign of f_b - f_a: the signed marginal asymmetry IS "orient from the easier to the harder
  skill", and the difficulty-matched subset is the same sort applied to pairs with small gaps.
  Two pre-registered checks did not pass and are reported as such, untuned: the R2SORT
  implementation check (0.665 < 0.70 on the linear-Gaussian SEM, identical when standardised), so
  R2SORT columns are "not validated"; and the census floor (1 of 16 additive/none control arms fired:
  additive, co-parent 0.6, gate 0, interaction +0.0415 against a null 97.5th of +0.0305), so the OR
  census numbers are descriptive, not a census reading.
  CHANGE 2026-10-08 (loader only; made and committed BEFORE this study read any ds1275 row; the only
  ds1275 content inspected beforehand was its header line, its README.txt and its MD5, which matched
  data/data-sources.json: edbbcaf83211085be980ab02ff186127). WHAT: part (c)'s Junyi difficulty is
  read from the DataShop ds1275 student-step export ('All Data' sample, chosen by
  shared.corpus.ds1275_export, $DS1275_DIR) instead of the 999-row public transaction sample, which
  came back UNANSWERABLE (2 exercises reached 20 learners). The public-sample loader is kept and
  selected with `real --junyi-log public`. Column mapping, chosen to reproduce the pre-registered
  rule (first attempt per learner per exercise, CORRECT/INCORRECT only, ordered by time):
      learner  <- Anon Student Id            unit <- KC (Exercise) (the authored graph's names)
      time     <- Step Start Time (ISO text, sorts as time; file order breaks ties)
      outcome  <- First Attempt: correct -> 1, incorrect -> 0; 'hint' (no answer attempted on the
                  step, the student-step analogue of the public loader's skipped HINT rows) skipped
  Only those four columns are read. Rows with an empty KC or start time are skipped and counted.
  WHY: the handover (docs/handover/2026-10-09-restricted-datasets.md, task 1b) names ds1275 as the
  log the Junyi reading waits on. Note, from its README, read before this change: ds1275 is itself
  titled "Partial Samples" (1/120 of users, 2,063 students); it is larger than the public sample
  (642 learners) but is not Junyi's full log. The eligibility gate decides whether it suffices.
  ALSO: the Junyi eligible-branch (its floor and bootstrap) now draws from its own stream,
  np.random.default_rng(20261008 + 1275), so the shared stream that the rater descriptive and the
  ASSISTments reading consume is exactly what it was in the committed run; the ASSISTments rows must
  then reproduce out/real.json bit for bit, which is checked after the run. No design, threshold,
  estimand, interval or verdict string changed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
SIM_DIR = ROOT / "studies/simulation/learner-sim"
CONJ_DIR = ROOT / "studies/identifiability/conjunctive"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "shared"))
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(CONJ_DIR))

import orientation_difficulty as od  # noqa: E402
import orientation_soft as osoft     # noqa: E402
import stage1_floor as s1            # noqa: E402
from shared.stats import bootstrap, paired_bootstrap, spearman  # noqa: E402

REGIMES = osoft.REGIMES
HARDNESS = osoft.HARDNESS
WORLDS = osoft.WORLDS
SEED_BASE = 3300
MARGIN = 0.02
CEILING = 0.95
BOOT = 2000
FLOOR_REPS = 50
PLANT_DELTAS = (0.05, 0.10, 0.15)
CENSUS_SEED = 20261007
CENSUS_REPS = 20
MIN_LEARNERS = 20
MIN_EDGES = 30
MIN_NODES = 30


# --------------------------------------------------------------------------- generators

def learners_or(par, diff, hardness, rng):
    """orientation_soft.learners with one change: a node is short of prerequisites only when it
    holds NONE of them (disjunctive, DINO-type); any one parent suffices."""
    out = []
    order = sorted(range(od.N_NODES))
    bump = osoft.MODEL.gamma / osoft.MODEL.lam
    for _ in range(od.N_LEARNERS):
        th = rng.gauss(0, 1)
        have = {}
        for n in order:
            ps = par[n]
            short = bool(ps) and not any(have[p] for p in ps)
            if short and rng.random() < hardness:
                have[n] = rng.random() < od.GUESS
                continue
            eff = diff[n] + (bump * math.log(1 + len(ps)) if short else 0.0)
            have[n] = (rng.random() > od.SLIP) if th > eff else (rng.random() < od.GUESS)
        out.append(have)
    return out


def depths(par, n_nodes):
    d = {}
    for n in range(n_nodes):
        d[n] = 0 if not par[n] else 1 + max(d[p] for p in par[n])
    return d


# --------------------------------------------------------------------------- scoring

def r2_all(X):
    """R^2 of each column regressed (OLS, intercept) on all other columns."""
    n, k = X.shape
    out = np.full(k, np.nan)
    for j in range(k):
        y = X[:, j]
        sst = float(((y - y.mean()) ** 2).sum())
        if sst <= 0:
            continue
        A = np.column_stack([np.ones(n), np.delete(X, j, axis=1)])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        res = y - A @ beta
        out[j] = 1.0 - float((res ** 2).sum()) / sst
    return out


def sort_score(lo_better_a, va, vb):
    """1 if the sort orients a -> b, 0.5 on a tie or undefined, 0 otherwise.
    lo_better_a: the sort puts a first when va < vb."""
    if np.isnan(va) or np.isnan(vb) or va == vb:
        return 0.5
    return 1.0 if (va < vb) == lo_better_a else 0.0


def score_world(edges, par, diff, rows):
    """Edge-level records for one world: the existing statistic and both baselines."""
    X = np.array([[r[n] for n in range(od.N_NODES)] for r in rows], dtype=float)
    pc = X.mean(0)
    fail = 1 - pc
    r2 = r2_all(X)
    dep = depths(par, od.N_NODES)
    recs = []
    for a, b in sorted(edges):
        s = od.signed_marginal(rows, a, b)
        if s is None or abs(s) < 1e-9:
            continue
        recs.append(dict(
            asym=1.0 if s > 0 else 0.0,
            # easier first: a first when fail[a] < fail[b]
            diffsort=sort_score(True, fail[a], fail[b]),
            r2sort=sort_score(True, r2[a], r2[b]),
            matched=bool(abs(fail[a] - fail[b]) <= od.MATCH_TOL),
            latent_up=1.0 if diff[b] > diff[a] else 0.0,
            fanin=len(par[b]),
        ))
    rho_lat = spearman([dep[n] for n in range(od.N_NODES)], [diff[n] for n in range(od.N_NODES)])
    rho_obs = spearman([dep[n] for n in range(od.N_NODES)], list(fail))
    return recs, rho_lat, rho_obs


def run_cell(mech, regime, hard):
    worlds = []
    for w in range(WORLDS):
        rng = random.Random(SEED_BASE + w)
        edges, par, diff = od.world(rng, regime)
        gen = osoft.learners if mech == "AND" else learners_or
        rows = gen(par, diff, hard, rng)
        recs, rl, ro = score_world(edges, par, diff, rows)
        worlds.append(dict(recs=recs, rho_latent=rl, rho_observed=ro))
    return worlds


def pooled(worlds, key, sel=lambda r: True):
    """Per-world (sum, count) arrays for a field over selected records."""
    s = np.array([sum(r[key] for r in w["recs"] if sel(r)) for w in worlds], float)
    c = np.array([sum(1 for r in w["recs"] if sel(r)) for w in worlds], float)
    return s, c


def ratio(s, c):
    return lambda i: (s[i].sum() / c[i].sum()) if c[i].sum() else float("nan")


def read_cell(D, lo, hi, acc_ds):
    if acc_ds >= CEILING:
        return "CEILING"
    if lo > 0 and D > MARGIN:
        return "ADDS"
    if hi <= MARGIN:
        return "WORSE" if hi < 0 else "NO BETTER"
    return "UNDECIDED"


def summarise(worlds, rng, sel=lambda r: True):
    out = {}
    s_a, c = pooled(worlds, "asym", sel)
    n = int(c.sum())
    out["n_edges"] = n
    if n == 0:
        return out
    idx = len(worlds)
    for k in ("asym", "diffsort", "r2sort", "latent_up"):
        s, _ = pooled(worlds, k, sel)
        p, lo, hi = bootstrap(ratio(s, c), idx, rng, BOOT)
        out[k] = dict(acc=p, lo=lo, hi=hi)
    for base in ("diffsort", "r2sort"):
        s_b, _ = pooled(worlds, base, sel)
        D, lo, hi = paired_bootstrap(ratio(s_b, c), ratio(s_a, c), idx, rng, BOOT)
        out[f"D_{base}"] = dict(D=D, lo=lo, hi=hi,
                                reading=read_cell(D, lo, hi, out[base]["acc"]))
    return out


# --------------------------------------------------------------------------- floor

def world_boot_idx(rng, n_worlds, reps=BOOT):
    return rng.integers(0, n_worlds, (reps, n_worlds))


def plant_floor(worlds, rng):
    """PLANT-SORT and PLANT-ADD on this cell's own edges; vectorised world bootstrap."""
    ds = [np.array([r["diffsort"] for r in w["recs"]]) for w in worlds]
    c = np.array([len(x) for x in ds], float)
    acc_ds = sum(x.sum() for x in ds) / c.sum()
    wrong_share = 1 - acc_ds
    B = world_boot_idx(rng, len(worlds))
    s_ds = np.array([x.sum() for x in ds])

    def reading(stat_sums):
        D = (stat_sums.sum() - s_ds.sum()) / c.sum()
        Db = (stat_sums[B].sum(1) - s_ds[B].sum(1)) / c[B].sum(1)
        lo, hi = np.percentile(Db, [2.5, 97.5])
        return read_cell(D, lo, hi, acc_ds)

    res = {"acc_diffsort": float(acc_ds)}
    # PLANT-SORT: DIFFSORT with ties broken at random
    nb = 0
    for _ in range(FLOOR_REPS):
        sums = np.array([np.where(x == 0.5, rng.random(len(x)) < 0.5, x).sum() for x in ds])
        nb += reading(sums) in ("NO BETTER", "WORSE")
    res["plant_sort_no_better_rate"] = nb / FLOOR_REPS
    for delta in PLANT_DELTAS:
        q = delta / wrong_share if wrong_share > 0 else float("inf")
        if q > 1:
            res[f"plant_add_{delta}"] = None   # the sort leaves less than delta to add
            continue
        hit = 0
        for _ in range(FLOOR_REPS):
            sums = []
            for x in ds:
                base = np.where(x == 0.5, (rng.random(len(x)) < 0.5).astype(float), x)
                fix = (base == 0) & (rng.random(len(x)) < q)
                sums.append((base + fix).sum())
            hit += reading(np.array(sums)) == "ADDS"
        res[f"plant_add_{delta}"] = hit / FLOOR_REPS
    return res


def r2_check(rng_seed=4400):
    """R2SORT on a linear-Gaussian SEM over the sweep's graphs; raw and standardised."""
    ok_raw = ok_std = tot = 0
    for w in range(WORLDS):
        rng = random.Random(SEED_BASE + w)
        edges, par, _ = od.world(rng, "INDEPENDENT")
        g = np.random.default_rng(rng_seed + w)
        W = {e: g.uniform(0.5, 2.0) * g.choice([-1, 1]) for e in edges}
        X = np.zeros((od.N_LEARNERS, od.N_NODES))
        for n in range(od.N_NODES):
            X[:, n] = g.normal(0, 1, od.N_LEARNERS)
            for p in par[n]:
                X[:, n] += W[(p, n)] * X[:, p]
        r_raw = r2_all(X)
        r_std = r2_all((X - X.mean(0)) / X.std(0))
        for a, b in edges:
            ok_raw += sort_score(True, r_raw[a], r_raw[b])
            ok_std += sort_score(True, r_std[a], r_std[b])
            tot += 1
    return dict(acc_raw=ok_raw / tot, acc_standardised=ok_std / tot, n_edges=tot,
                passes=bool(ok_raw / tot >= 0.70 and abs(ok_raw - ok_std) < 1e-9))


# --------------------------------------------------------------------------- census (b2)

def simulate_or(n, p_a, p_b, gate, rng, *, base=0.55, ability=0.22):
    """stage1_floor.simulate's structure, with the penalty applied unless A OR B is held."""
    theta = rng.normal(0, ability, n)
    held_a = rng.random(n) < p_a
    held_b = rng.random(n) < p_b
    p = np.full(n, base) + theta
    p = np.where(held_a | held_b, p, p - (1 - gate) * 0.45)
    ok = (rng.random(n) < np.clip(p, 0.01, 0.99)).astype(float)
    return held_a, held_b, ok


def census_arm(kind, p_b, gate, rng):
    acc, nulls = [], []
    for _ in range(CENSUS_REPS):
        if kind == "disjunctive":
            ha, hb, ok = simulate_or(s1.N_LEARNERS, 0.5, p_b, gate, rng)
        else:
            ha, hb, ok = s1.simulate(s1.N_LEARNERS, 0.5, p_b, gate, kind, rng)
        got = s1.statistics(ha, hb, ok)
        if got:
            acc.append(got)
            nb = s1.deranged_null(ha, hb, ok, rng)
            if nb:
                nulls.append(nb["interaction"])
    g = lambda k: float(np.median([x[k] for x in acc]))  # noqa: E731
    r = dict(kind=kind, co_parent=p_b, gate=gate, reps=len(acc),
             pairwise_a=g("pairwise_a"), pairwise_b=g("pairwise_b"),
             interaction=g("interaction"),
             null_lo=float(np.percentile(nulls, 2.5)), null_hi=float(np.percentile(nulls, 97.5)))
    r["pairwise_reads_null"] = bool(abs(r["pairwise_a"]) < s1.BACKGROUND)
    r["fires"] = bool(r["interaction"] > r["null_hi"])
    r["negative"] = bool(r["interaction"] < r["null_lo"])
    return r


def census():
    rng = np.random.default_rng(CENSUS_SEED)
    rows = []
    for kind in ("conjunctive", "additive", "none", "disjunctive"):
        for p_b in s1.CO_PARENT:
            for gate in s1.GATE:
                if kind == "none" and gate != 0.0:
                    continue
                rows.append(census_arm(kind, p_b, gate, rng))
    conj = [r for r in rows if r["kind"] == "conjunctive" and r["gate"] < 1]
    ctrl = [r for r in rows if r["kind"] in ("additive", "none") and (r["gate"] < 1 or r["kind"] == "none")]
    disj = [r for r in rows if r["kind"] == "disjunctive" and r["gate"] < 1]
    floor = bool(any(r["fires"] for r in conj) and not any(r["fires"] for r in ctrl))
    for r in disj:
        r["reading"] = ("MISREAD AS CONJUNCTION" if r["fires"] else
                        "NEGATIVE INTERACTION" if r["negative"] else "INVISIBLE")
    return dict(seed=CENSUS_SEED, reps=CENSUS_REPS, n_learners=s1.N_LEARNERS,
                floor_passes=floor,
                conj_fired=sum(r["fires"] for r in conj), n_conj=len(conj),
                ctrl_fired=sum(r["fires"] for r in ctrl), n_ctrl=len(ctrl),
                or_misread=sum(r["fires"] for r in disj),
                or_negative=sum(r["negative"] for r in disj),
                or_pairwise_null=sum(r["pairwise_reads_null"] for r in disj),
                n_or=len(disj), rows=rows)


# --------------------------------------------------------------------------- headline

def headline(cells, base, label):
    non_ceiling = {k: v for k, v in cells.items() if v[f"D_{base}"]["reading"] != "CEILING"}
    readings = {k: v[f"D_{base}"]["reading"] for k, v in non_ceiling.items()}
    beats = [k for k, v in non_ceiling.items() if v["asym"]["lo"] > 0.5]
    if non_ceiling and all(r in ("NO BETTER", "WORSE") for r in readings.values()):
        verdict = f"{label} REDUCES TO {'DIFFICULTY' if base == 'diffsort' else 'R2'} SORTABILITY"
    elif beats and all(readings[k] == "ADDS" for k in beats):
        verdict = f"{label} ADDS BEYOND {'DIFFICULTY' if base == 'diffsort' else 'R2'} SORTABILITY"
    else:
        verdict = f"{label} PARTLY REDUCES TO {'DIFFICULTY' if base == 'diffsort' else 'R2'} SORTABILITY"
    return dict(verdict=verdict, readings=readings, asym_beats_chance=beats,
                ceiling=[k for k in cells if k not in non_ceiling])


def main_sim():
    rng = np.random.default_rng(20261007)
    ref = json.loads((SIM_DIR / "orientation-soft-result.json").read_text())
    out = {"grid": dict(regimes=REGIMES, hardness=HARDNESS, worlds=WORLDS, seeds=f"{SEED_BASE}+w",
                        n_nodes=od.N_NODES, n_learners=od.N_LEARNERS, boot=BOOT, margin=MARGIN)}
    cells = {"AND": {}, "OR": {}}
    cells_fan2 = {"AND": {}, "OR": {}}
    floors = {}
    repro = []
    sweep = {}
    for mech in ("AND", "OR"):
        for regime in REGIMES:
            for hard in HARDNESS:
                key = f"{regime}/{hard}"
                worlds = run_cell(mech, regime, hard)
                sm = summarise(worlds, rng)
                sm["matched"] = summarise(worlds, rng, sel=lambda r: r["matched"])
                sm["rho_latent_mean"] = float(np.nanmean([w["rho_latent"] for w in worlds]))
                sm["rho_observed_mean"] = float(np.nanmean([w["rho_observed"] for w in worlds]))
                cells[mech][key] = sm
                cells_fan2[mech][key] = summarise(worlds, rng, sel=lambda r: r["fanin"] >= 2)
                if mech == "AND":
                    d_all = abs(sm["asym"]["acc"] - ref[key]["all"])
                    d_m = (abs(sm["matched"]["asym"]["acc"] - ref[key]["matched"])
                           if sm["matched"]["n_edges"] else 0.0)
                    repro.append(max(d_all, d_m))
                floors[f"{mech}/{key}"] = plant_floor(worlds, rng)
                D = sm["D_diffsort"]
                print(f"{mech} {key:<18} asym {sm['asym']['acc']:.3f} diffsort "
                      f"{sm['diffsort']['acc']:.3f} r2sort {sm['r2sort']['acc']:.3f} "
                      f"D {D['D']:+.3f} [{D['lo']:+.3f},{D['hi']:+.3f}] {D['reading']}", flush=True)
    out["repro_max_abs_diff"] = max(repro)
    out["repro_passes"] = bool(max(repro) < 1e-12)
    out["r2_check"] = r2_check()
    # floor summary over non-ceiling cells of the AND and OR arms
    fs = {}
    for mech in ("AND", "OR"):
        nc = [k for k in cells[mech] if cells[mech][k]["D_diffsort"]["reading"] != "CEILING"]
        f = {k: floors[f"{mech}/{k}"] for k in nc}
        mdi = None
        for delta in PLANT_DELTAS:
            vals = [v[f"plant_add_{delta}"] for v in f.values() if v[f"plant_add_{delta}"] is not None]
            if vals and min(vals) >= 0.80:
                mdi = delta
                break
        fs[mech] = dict(non_ceiling_cells=nc,
                        plant_sort_min_no_better=min(v["plant_sort_no_better_rate"] for v in f.values()),
                        min_power={str(d): min([v[f"plant_add_{d}"] for v in f.values()
                                                if v[f"plant_add_{d}"] is not None] or [float("nan")])
                                   for d in PLANT_DELTAS},
                        min_detectable_increment=mdi)
    out["floor"] = dict(per_cell=floors, summary=fs)
    out["cells"] = cells
    out["cells_fanin2"] = cells_fan2
    for mech, label in (("AND", "F2"), ("OR", "OR ARM")):
        powered = fs[mech]["min_detectable_increment"] is not None
        h_ds = headline(cells[mech], "diffsort", label)
        h_r2 = headline(cells[mech], "r2sort", label)
        if not out["repro_passes"]:
            h_ds["verdict"] = h_r2["verdict"] = "UNANSWERABLE"
        elif not powered:
            # only an all-NO-BETTER reading survives an underpowered comparison
            for h in (h_ds, h_r2):
                if not h["verdict"].startswith(f"{label} REDUCES"):
                    h["verdict"] = "UNANSWERABLE"
        if not out["r2_check"]["passes"]:
            h_r2["verdict"] += " (R2SORT NOT VALIDATED)"
        out[f"headline_{mech}"] = dict(vs_diffsort=h_ds, vs_r2sort=h_r2)
        print(f"\n{mech}: {h_ds['verdict']} | {h_r2['verdict']}")
    out["census"] = census()
    c = out["census"]
    print(f"\ncensus floor {c['floor_passes']}: conj fired {c['conj_fired']}/{c['n_conj']}, "
          f"controls fired {c['ctrl_fired']}/{c['n_ctrl']}; OR misread {c['or_misread']}/{c['n_or']}, "
          f"negative {c['or_negative']}, pairwise null {c['or_pairwise_null']}")
    print(f"repro {out['repro_passes']} ({out['repro_max_abs_diff']:.2e}); r2 check {out['r2_check']}")
    print(f"floor {json.dumps(fs, indent=1)}")
    OUT.mkdir(exist_ok=True)
    (OUT / "sim.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT / 'sim.json'}")


# --------------------------------------------------------------------------- real data (c)

def first_attempt_difficulty(events):
    """events: (learner, unit, time, correct). Difficulty = 1 - share correct on first attempts."""
    first = {}
    for learner, unit, t, ok in events:
        k = (learner, unit)
        if k not in first or t < first[k][0]:
            first[k] = (t, ok)
    n = defaultdict(int)
    s = defaultdict(float)
    for (_, unit), (_, ok) in first.items():
        n[unit] += 1
        s[unit] += ok
    return {u: 1 - s[u] / n[u] for u in n}, dict(n)


def junyi_events(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = {h: i for i, h in enumerate(head)}
        for line in f:
            c = line.rstrip("\n").split("\t")
            if len(c) < len(head) or c[ix["Student Response Type"]] != "ATTEMPT":
                continue
            o = c[ix["Outcome"]]
            if o not in ("CORRECT", "INCORRECT"):
                continue
            yield c[ix["Anon Student Id"]], c[ix["KC (Exercise)"]], int(c[ix["Time"]]), \
                1.0 if o == "CORRECT" else 0.0


def ds1275_events(root, counts):
    """ds1275 student-step export -> (learner, exercise, time, correct); see CHANGES 2026-10-08."""
    from shared.corpus import ds1275_export
    path = ds1275_export(root)
    counts["file"] = path.name
    with open(path, encoding="utf-8", errors="replace") as f:
        head = f.readline().rstrip("\n").split("\t")
        ix = [head.index(h) for h in ("Anon Student Id", "KC (Exercise)", "Step Start Time",
                                      "First Attempt")]
        for line in f:
            c = line.rstrip("\n").split("\t")
            counts["rows"] += 1
            if len(c) <= max(ix):
                counts["short"] += 1
                continue
            learner, kc, t, fa = (c[i].strip() for i in ix)
            if not kc or not t:
                counts["no_kc_or_time"] += 1
                continue
            fa = fa.lower()
            if fa not in ("correct", "incorrect"):
                counts["first_attempt_" + (fa or "empty")] += 1
                continue
            yield learner, kc, t, 1.0 if fa == "correct" else 0.0


def dag_depth(nodes, edges):
    """Longest-path depth on the SCC condensation; returns depth per node and cycle-member count."""
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
    idx, low, on, st, comp = {}, {}, set(), [], {}
    counter = [0]
    sys.setrecursionlimit(10000)

    def strong(v):
        idx[v] = low[v] = counter[0]; counter[0] += 1
        st.append(v); on.add(v)
        for w in adj[v]:
            if w not in idx:
                strong(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            while True:
                w = st.pop(); on.discard(w); comp[w] = v
                if w == v:
                    break
    for v in nodes:
        if v not in idx:
            strong(v)
    cpar = defaultdict(set)
    for a, b in edges:
        if comp[a] != comp[b]:
            cpar[comp[b]].add(comp[a])
    memo = {}

    def dep(c):
        if c in memo:
            return memo[c]
        memo[c] = 0 if not cpar[c] else 1 + max(dep(p) for p in cpar[c])
        return memo[c]
    sizes = defaultdict(int)
    for v in nodes:
        sizes[comp[v]] += 1
    in_cycle = sum(1 for v in nodes if sizes[comp[v]] > 1)
    return {v: dep(comp[v]) for v in nodes}, in_cycle


def edge_S(pairs, diff):
    """Share of (prereq, dependent) pairs whose dependent is harder; ties 0.5."""
    if not pairs:
        return float("nan")
    v = [1.0 if diff[b] > diff[a] else 0.5 if diff[b] == diff[a] else 0.0 for a, b in pairs]
    return float(np.mean(v))


def place(rho_ci, S_ci, floor_ok, eligible):
    if not eligible:
        return "UNANSWERABLE"
    if rho_ci[1] > 0 and S_ci[1] > 0.5:
        return "DIFFICULTY RISES WITH DEPTH (ALIGNED SIDE)"
    if rho_ci[2] < 0 and S_ci[2] < 0.5:
        return "DIFFICULTY FALLS WITH DEPTH (INVERTED SIDE)"
    return "NO DIFFICULTY-DEPTH ORDER RESOLVED" if floor_ok else "UNDERPOWERED"


def corpus_reading(kind, units, depth, diff, n_unit, pairs, rng, boot=BOOT):
    """kind 'graph' (Junyi: resample edges) or 'order' (ASSISTments: resample skills)."""
    units = list(units)
    if kind == "graph":
        E = list(pairs)

        def S_of(i):
            return edge_S([E[k] for k in i], diff)

        def rho_edges(i):
            ends = [x for k in i for x in E[k]]
            return spearman([depth[x] for x in ends], [diff[x] for x in ends])
        S = bootstrap(S_of, len(E), rng, boot)
        rho = bootstrap(rho_edges, len(E), rng, boot)
        rho_nodes = bootstrap(lambda i: spearman([depth[units[k]] for k in i],
                                                 [diff[units[k]] for k in i]), len(units), rng, boot)
        return dict(S=S, rho=rho, rho_node_resampled=rho_nodes)
    # order: pairs = all cross-depth ordered pairs among the resampled skills

    def S_of(i):
        us = [units[k] for k in i]
        dv = np.array([depth[u] for u in us]); fv = np.array([diff[u] for u in us])
        lo, hi = np.meshgrid(np.arange(len(us)), np.arange(len(us)), indexing="ij")
        m = dv[lo] < dv[hi]
        if not m.any():
            return float("nan")
        harder = fv[hi][m] - fv[lo][m]
        return float(np.mean(np.where(harder > 0, 1.0, np.where(harder == 0, 0.5, 0.0))))
    S = bootstrap(S_of, len(units), rng, boot)
    rho = bootstrap(lambda i: spearman([depth[units[k]] for k in i],
                                       [diff[units[k]] for k in i]), len(units), rng, boot)
    return dict(S=S, rho=rho)


def synth_floor(kind, units, depth, n_unit, pairs, rng):
    """Planted latent difficulty-depth relation on the real eligible structure; synthetic outcomes."""
    units = list(units)
    dv = np.array([depth[u] for u in units], float)
    z = (dv - dv.mean()) / (dv.std() or 1)
    res = {}
    for r in (0.3, 0.0, -0.3):
        right = wrong = 0
        for _ in range(100):
            lat = r * z + math.sqrt(1 - r * r) * rng.normal(0, 1, len(units))
            p = 1 / (1 + np.exp(1.5 * lat))
            k = rng.binomial([n_unit[u] for u in units], p)
            diff = {u: 1 - k[j] / n_unit[u] for j, u in enumerate(units)}
            got = corpus_reading(kind, units, depth, diff, n_unit, pairs, rng, boot=400)
            S, rho = got["S"], got["rho"]
            up = S[1] > 0.5 and rho[1] > 0
            down = S[2] < 0.5 and rho[2] < 0
            if r > 0:
                right += up; wrong += down
            elif r < 0:
                right += down; wrong += up
            else:
                wrong += up or down
        res[str(r)] = dict(correct_sign_rate=right / 100, wrong_sign_rate=wrong / 100)
    ok = (res["0.3"]["correct_sign_rate"] >= 0.8 and res["-0.3"]["correct_sign_rate"] >= 0.8
          and res["0.0"]["wrong_sign_rate"] <= 0.10)
    return dict(per_r=res, passes=bool(ok))


def nearest_sim(S_point):
    p = OUT / "sim.json"
    if not p.exists() or S_point != S_point:
        return None
    sim = json.loads(p.read_text())
    best = min(sim["cells"]["AND"].items(), key=lambda kv: abs(kv[1]["diffsort"]["acc"] - S_point))
    k, v = best
    return dict(cell=f"AND/{k}", sim_diffsort=v["diffsort"]["acc"], sim_asym=v["asym"]["acc"],
                reading_vs_diffsort=v["D_diffsort"]["reading"], D=v["D_diffsort"]["D"])


def main_real(junyi_log="ds1275"):
    from shared.paths import data_path
    from shared.junyi_graph import authored_edges, exercises
    rng = np.random.default_rng(20261008)
    jrng = np.random.default_rng(20261008 + 1275)   # Junyi eligible branch only (CHANGES 2026-10-08)
    out = {"min_learners": MIN_LEARNERS, "min_edges": MIN_EDGES, "min_nodes": MIN_NODES, "boot": BOOT}

    # ---- Junyi 2015
    jd = data_path("JUNYI_DIR")
    rows = exercises(jd)
    names = [r["name"] for r in rows]
    edges = authored_edges(jd, rows=rows)
    depth, in_cycle = dag_depth(names, edges)
    if junyi_log == "public":
        log = dict(source="public sample junyi_ProblemLog_for_PSLC.txt")
        diff, n_unit = first_attempt_difficulty(junyi_events(jd / "junyi_ProblemLog_for_PSLC.txt"))
    else:
        cnt = defaultdict(int)
        diff, n_unit = first_attempt_difficulty(ds1275_events(data_path("DS1275_DIR"), cnt))
        log = dict(source="DataShop ds1275 student-step export, 'All Data' sample", **cnt)
    log["n_logged_exercises_in_authored_table"] = sum(1 for u in diff if u in depth)
    log["n_logged_exercises_not_in_authored_table"] = sum(1 for u in diff if u not in depth)
    elig = {u for u in diff if n_unit[u] >= MIN_LEARNERS and u in depth}
    E = [(a, b) for a, b in edges if a in elig and b in elig]
    nodes = sorted(elig)
    j = dict(n_exercises=len(names), n_authored_edges=len(edges), n_cycle_members=in_cycle,
             n_exercises_in_log=len(diff), n_eligible_exercises=len(nodes), n_eligible_edges=len(E),
             n_depths_eligible=len({depth[u] for u in nodes}),
             depth_max=max(depth.values()), log=log)
    eligible = len(E) >= MIN_EDGES and len(nodes) >= MIN_NODES and j["n_depths_eligible"] >= 2
    j["eligible"] = eligible
    if eligible:
        j["floor"] = synth_floor("graph", nodes, depth, n_unit, E, jrng)
        j.update(corpus_reading("graph", nodes, depth, diff, n_unit, E, jrng))
        j["verdict"] = place(j["rho"], j["S"], j["floor"]["passes"], True)
        j["nearest_sim"] = nearest_sim(j["S"][0])
    else:
        j["verdict"] = "UNANSWERABLE"
    # secondary, descriptive: rater difficulty on annotated authored edges
    import csv
    aset = set(edges)
    rd = []
    for fn in ("relationship_annotation_training.csv", "relationship_annotation_testing.csv"):
        with open(jd / fn, encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                A, B = r["Exercise_A"], r["Exercise_B"]
                v = float(r["Difficulty_avg"])
                if (A, B) in aset:       # A prereq of B; high = B harder: dependent harder
                    rd.append(v - 5)
                elif (B, A) in aset:     # B prereq of A; high = B (the prereq) harder
                    rd.append(5 - v)
    rd = np.array(rd)
    if len(rd):
        mean = bootstrap(lambda i: float(rd[i].mean()), len(rd), rng, BOOT)
        share = bootstrap(lambda i: float(np.mean(np.where(rd[i] > 0, 1, np.where(rd[i] == 0, .5, 0)))),
                          len(rd), rng, BOOT)
        j["rater_difficulty_descriptive"] = dict(
            coder="Junyi 2015 crowd workers (Chang, Hsu & Chen 2015), mean of raters; no independent "
                  "reference computed here: descriptive only",
            n_rated_authored_pairs=int(len(rd)),
            mean_dependent_minus_equal=mean, share_dependent_rated_harder=share)
    out["junyi2015"] = j
    print("junyi", json.dumps({k: v for k, v in j.items() if k != "floor"}, default=str))

    # ---- ASSISTments 2012-13: CCSS grade order (no authored graph held)
    from shared.corpus import Assistments2012
    cmap = ROOT / "studies/measurement/assist2012-direction/out/skill_ccss_map.json"
    corp = Assistments2012(data_path("ASSIST_DIR"), ccss_map=cmap)
    exact = {s for s, rec in json.loads(cmap.read_text()).items() if rec.get("jaccard") == 1.0}
    diff, n_unit = first_attempt_difficulty(corp.events())
    a = {}
    for tier, keep in (("all_matched", lambda s: True), ("exact_name", lambda s: s in exact)):
        units = sorted(u for u in diff if n_unit[u] >= MIN_LEARNERS and corp.position(u) is not None
                       and keep(u))
        depth = {u: corp.position(u) for u in units}
        pairs = [(x, y) for x in units for y in units if depth[x] < depth[y]]
        t = dict(n_skills=len(units), n_cross_grade_pairs=len(pairs),
                 n_grades=len(set(depth.values())))
        ok = len(units) >= MIN_NODES and len(pairs) >= MIN_EDGES and t["n_grades"] >= 2
        t["eligible"] = ok
        if ok:
            t["floor"] = synth_floor("order", units, depth, n_unit, pairs, rng)
            t.update(corpus_reading("order", units, depth, diff, n_unit, pairs, rng))
            t["verdict"] = place(t["rho"], t["S"], t["floor"]["passes"], True)
            t["nearest_sim"] = nearest_sim(t["S"][0])
        else:
            t["verdict"] = "UNANSWERABLE"
        a[tier] = t
        print("assist", tier, json.dumps({k: v for k, v in t.items() if k != "floor"}, default=str))
    a["note"] = ("No authored prerequisite graph is held for ASSISTments 2012-13; depth is the CCSS "
                 "grade of the name-matched code (studies/measurement/assist2012-direction).")
    out["assistments2012"] = a
    out["eedi"] = dict(verdict="NOT HELD",
                       note="No authored prerequisite graph is held: the NeurIPS 2020 subject tree is "
                            "an unordered taxonomy and the NeurIPS 2022 Task 3 adjacency is not "
                            "released or held.")
    OUT.mkdir(exist_ok=True)
    (OUT / "real.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {OUT / 'real.json'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("part", choices=("sim", "real"))
    ap.add_argument("--junyi-log", choices=("ds1275", "public"), default="ds1275",
                    help="real: Junyi log to read (CHANGES 2026-10-08); 'public' is the 999-row sample")
    args = ap.parse_args()
    main_sim() if args.part == "sim" else main_real(args.junyi_log)
