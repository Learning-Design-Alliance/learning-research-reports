"""
Does the Junyi rater-learner agreement survive conditioning on taxonomy distance?

PRE-REGISTRATION. Written 2026-10-07, before any real number in this study was computed. Committed
before the real-data run (step 2 of the analyses brief).

## Question

Paper II's F4 says crowd-rater prerequisite judgments on Junyi "point the right way but are not
established": `studies/identifiability/junyi/expert_vs_data.py` section 3 found Spearman
+0.29914 [-0.01714, +0.57081] between each rated pair's mean Prerequisite rating and a learner-order
gap, over 47 rated (prereq -> dependent) pairs with >= 15 learners in each order
(`studies/identifiability/junyi/junyi-expert-vs-data.json`; direction corrected 2026-09-24,
`docs/notes/JUNYI-DIRECTION.md`).

The literature review (`research/readiness/learning-graph-budget-2026/literature.md`, strand 1 entry
1.15, strand-1 "Analyses" item 2, synthesis ranked analysis 5) gives a reason to doubt what that
agreement means. In VISL on Eedi (Morales-Alvarez et al. 2021, arXiv:2110.08223, section 4.3, Tables
6-7), teachers' "sensibility" ratings of learned edges track topic proximity: 36% of learned edges lie
inside one level-2 topic against 6% of random edges. If Junyi's raters rate exercises in the same topic
as better prerequisites, and learners' order gaps are also larger for same-topic pairs (shared
content, not dependence), the rater-learner correlation can arise with no pair-specific dependence at
all. The control the review names is pairs matched on taxonomy distance, not uniform random pairs.

## Data (reads licensed corpora)

  junyi2015-authored ($JUNYI_DIR, data/data-sources.json): junyi_Exercise_table.csv (taxonomy: `topic`,
      `area`; knowledge-map coordinates `h_position`, `v_position`), relationship_annotation_*.csv
      read only through shared.junyi_ratings (oriented: prereq = Exercise_B, dependent = Exercise_A),
      and junyi_ProblemLog_for_PSLC.txt.
  datashop ds1275 ($DS1275_DIR, read through shared.corpus.ds1275_export, the 'All Data' sample): the
      learner log the committed 47-pair result came from. Upload-only (DataShop login); if absent the
      learner side is BLOCKED unless the fallback below reproduces.

Fallback, as the brief directs: if ds1275 is not on disk, the Junyi 2015 problem log that is
(`junyi_ProblemLog_for_PSLC.txt`) is read with the same rule and must reproduce the committed result
first: exactly 47 pairs and |rho - 0.29914| < 0.001 under the original script's ranking. If it does not
reproduce, every learner-side estimand below is reported BLOCKED, not estimated on a different sample.
Only aggregates are written; no learner rows, no exercise names (ids of the licensed corpus are not
needed in the output).

DIRECTION: a -> b means a is the prerequisite of b, per Chang et al. 2015's third question for rating
rows, whose (prereq, dependent) is (Exercise_B, Exercise_A) (quoted in shared/junyi_ratings.py), and per
the release's column description of `prerequisites` ("Indicate its prerequisite exercise (parent shown
in its knowledge map)", codebook junyi2015-authored) for authored edges (p, name).

## Taxonomy distance (defined)

The exercise table assigns each exercise one `topic` and one `area` (a two-level hierarchy over
exercises). For an exercise pair (x, y):

    dist = 0   same topic (hence same area)
    dist = 1   same area, different topic
    dist = 2   different area

An exercise with an empty topic or area takes its own singleton value at that level (so it is never
"same" by an empty string). Pairs naming an exercise absent from the table are dropped and counted.
This is an ordinal 3-level covariate; ranks are tie-averaged (shared.stats.rank).
Secondary covariate (sensitivity only, declared now): `mapdist`, the Euclidean distance between the two
exercises' (h_position, v_position) on the authored knowledge map.

## Learner statistic (unchanged from expert_vs_data.py section 3)

For rated pair P -> D: learners with >= 20 attempts overall; residual accuracy on D (accuracy on D
minus the learner's overall accuracy), requiring >= 2 attempts at D; gap = mean residual of learners
who met P before D minus that of learners who met D first (a tie in first position counts as D-first,
as in the original). Kept if >= 15 learners in each order. Coverage n = learners in both orders.

## Estimands

  rho_T     Spearman(rating, gap) over the treatment pairs, tie-averaged ranks (shared.stats.spearman).
            Also reported under the original script's positional ranking, for the reproduction check.
  rho_p     partial Spearman(rating, gap | dist), shared.stats.partial_spearman. Sensitivity: | mapdist.
  C1        WITHIN-TREATMENT STRATIFIED DERANGEMENT. The gaps of the treatment pairs are deranged within
            distance level (no pair keeps its own gap; each gets another treatment pair's gap at the same
            dist). rho_C1 = Spearman(rating, deranged gap), 2,000 derangements. This is the conditional
            permutation null: it keeps every rating, every gap and the whole distance structure, and
            breaks only the pair-specific link. The unit permuted is the rated pair, the unit the rating
            was assigned to. Reported: mean rho_C1, and p = share of derangements with rho_C1 >= rho_T
            (one-sided, the H1 direction). A level holding a single pair cannot be deranged; such pairs
            are dropped from C1 and counted.
  C2        EXTERNAL MATCHED CONTROL, the review's construction. Each treatment pair i keeps its rating
            and is given the gap of a pool pair j: an ordered exercise pair rated in NEITHER order
            (so no real rated pair is kept, and no pair is matched to itself), with >= 15 learners in
            each order, at the same dist as i, with the dependent in the same area as i's dependent
            (family match), and coverage n_j within a factor 1.5 of n_i (widened to 2, then the area
            match dropped, in that order, if no candidate; each relaxation counted). Pool pairs are drawn
            without replacement within a draw, so the control is the same size as the treatment (47
            pairs if reproduced) with the same coverage distribution; shared.controls.check_control_scale
            asserts pair count and median coverage are at least 0.5x the treatment's.
            rho_C2 = Spearman(rating_i, gap_j(i)). Delta = rho_T - rho_C2.
            Interval: 2,000 bootstrap replicates over treatment pairs; each replicate resamples pairs
            and redraws the control assignment, so it carries both pair sampling and matching noise.
            The point estimate of rho_C2 is the mean over 2,000 assignments on the full sample.
  RAW(rating, dist)  Spearman over all 1,954 rated rows (signed), bootstrap over unordered pairs
            (a pair rated in both orders moves together); and over the treatment pairs.
  RAW(gap, dist)     Spearman over the treatment pairs and over the C2 pool (signed).
  AUX (held without learner data): the map-vs-raters contrast of expert_vs_data.py section 2 (authored
            rows vs other rated rows, Cohen's d 0.955) re-scored against a distance-matched control:
            each authored rated row is compared with non-authored rated rows at the same dist
            (d_strat = within-dist standardized mean difference, weighted by authored rows per level,
            pooled SD from all rows). Bootstrap over unordered pairs.

Expected signs, stated now so direction is checked, not just magnitude: the confound requires
RAW(rating, dist) < 0 (raters rate nearer pairs higher) AND RAW(gap, dist) < 0 (nearer pairs show the
larger prerequisite-first advantage). Both negative is the configuration in which distance can
manufacture a positive rho_T; if either is >= 0, distance cannot explain a positive rho_T and is at most
a suppressor.

## Positivity

P1: dist must vary inside the treatment: at least two levels with >= 5 treatment pairs each. If not,
the verdict is "DISTANCE CONSTANT IN TREATMENT: the association cannot be a distance artefact within
these pairs" (and C1, rho_p are not computed). P2: C2 must match >= 90% of treatment pairs at the strict
or first-widened rule; otherwise C2 is reported but carries "C2 UNDER-MATCHED".

## Verdict (pre-registered, signed)

Preconditions in order: learner data reproduces (else "BLOCKED: learner data not reproducible");
rho_T > 0 (else "NO POSITIVE ASSOCIATION TO CONDITION"); P1.

    distance_explains_C = mean rho_C2 >= 0.5 * rho_T   (the matched control reproduces half or more)
    distance_explains_P = rho_p < 0.5 * rho_T          (partialling distance removes half or more)

    SURVIVES TAXONOMY CONTROL      neither explains, rho_p > 0, and Delta's 95% lower bound > 0
    SURVIVES IN POINT, NOT ESTABLISHED   neither explains, Delta's interval includes 0
    EXPLAINED BY TAXONOMY DISTANCE both explain
    MIXED                           exactly one explains (reported with which)

If the detection floor's power check (F2) fails, any verdict other than SURVIVES TAXONOMY CONTROL
carries the suffix "(UNDERPOWERED: floor F2 failed)" and is not a finding about the raters. If the
confound check (F1) fails, the real-data verdict is UNANSWERABLE.

AUX verdict: "MAP-RATER AGREEMENT SURVIVES DISTANCE MATCHING" if d_strat >= 0.5 * d_raw and its 95%
lower bound > 0; "MAP-RATER AGREEMENT EXPLAINED BY DISTANCE" if d_strat < 0.5 * d_raw and its interval
includes 0; otherwise "MAP-RATER AGREEMENT ATTENUATED BY DISTANCE" (with d_strat). Caveat stated now: the
authored map and the topic/area taxonomy come from the same authors, so this is catalogue against
catalogue, and the raters were shown pairs "paired according to student modeling and knowledge tree"
(codebook), so rated rows over-sample authored neighbours.

## Detection floor (synthetic; `--floor`)

Synthetic treatment sets shaped like the real one: 47 pairs; dist levels drawn from the distribution
of dist over all rated rows (real ratings and table, read after the design commit; the learner-selected
47 cannot be shaped without learner data, and that substitution is recorded); rating and gap generated
from a latent pair-specific dependence S and the distance level, with gap noise added; a C2 pool of
470 unrated pairs (10x) generated from the distance term and noise only, with the same coverage
distribution. 500 synthetic datasets per scenario, C2 point from 200 assignments and its interval
from 400 bootstrap replicates (fewer than the real run's 2,000, to fit the shared machine; stated).

  S0 NULL         no S, no distance term in gap.
  S1 SPECIFIC     rating = distance term + S; gap = S + noise, scaled so unconditional rho_T ~ 0.30.
  S2 DISTANCE     rating and gap both follow distance (rating-distance Spearman ~ -0.6), no S, scaled so
                  unconditional rho_T ~ 0.30: the confound alone produces the observed association.

  F1 (confound recognised, must pass): in S2, SURVIVES TAXONOMY CONTROL in <= 10% of datasets, and
     EXPLAINED or MIXED in >= 50%.
  F2 (power): in S1 at rho_T ~ 0.30, SURVIVES TAXONOMY CONTROL in >= 80% of datasets. Also reported:
     the planted rho_T needed for 80% (minimum detectable effect, over a grid 0.30 .. 0.60).
  F3 (size): in S0, SURVIVES in <= 5%.

This floor is scored by the same script that defines it: a smoke check of the instrument's arithmetic
and its power at n = 47, not an independent validation.

## What it can and cannot say

It can say whether the rater-learner rank association is larger than what the distance structure of
the same pairs produces. It cannot say the association is causal (learners chose their order;
expert_vs_data.py's confound paragraph applies unchanged), and conditioning on a 3-level taxonomy
leaves within-topic proximity uncontrolled (mapdist is the only finer proxy and is a sensitivity). The
ratings were coded by Chang et al.'s crowd raters (3-15 per row, 1-9 scale); their split-half agreement
is in expert_vs_data.py section 1. No construct here was coded by a model.

    python3 taxonomy_control.py --floor
    python3 taxonomy_control.py            # real data

## CHANGES

2026-10-07, floor result recorded (no design change): F1 PASS, F3 PASS, F2 FAIL (SURVIVES in 31.4% at a
planted rho_T of 0.30; 80% first reached at 0.50). Per the verdict section, any non-SURVIVES real verdict
would carry "(UNDERPOWERED: floor F2 failed)".
2026-10-07 (after the real run; no estimand, threshold or verdict changed). The first real run wrote
`"rho_positional": NaN` (no pairs to correlate), which is not valid JSON. `write` now emits null for
non-finite numbers. Re-run with the same seed; every other value is unchanged.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from shared.controls import check_control_scale  # noqa: E402
from shared.junyi_graph import authored_edges, exercises  # noqa: E402
from shared.junyi_ratings import load as load_ratings  # noqa: E402
from shared.paths import data_path  # noqa: E402
from shared.stats import partial_spearman, rank, spearman  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
SEED = 20261007
COMMITTED = dict(n=47, rho=0.2991443108233118, ci=[-0.01714269195189639, 0.5708082793709526])
CORRECT = {"CORRECT", "OK"}
KC = "KC (Exercise)"
MIN_ORDER = 15


# ---------------------------------------------------------------- taxonomy ----------------------
def taxonomy(rows):
    tax = {}
    for r in rows:
        n = r["name"]
        topic = (r.get("topic") or "").strip() or f"__t_{n}"
        area = (r.get("area") or "").strip() or f"__a_{n}"
        try:
            pos = (float(r["h_position"]), float(r["v_position"]))
        except (TypeError, ValueError):
            pos = None
        tax[n] = (topic, area, pos)
    return tax


def dist(tax, x, y):
    if x not in tax or y not in tax:
        return None
    tx, ax, _ = tax[x]
    ty, ay, _ = tax[y]
    return 0 if tx == ty else 1 if ax == ay else 2


def mapdist(tax, x, y):
    px, py = tax[x][2], tax[y][2]
    if px is None or py is None:
        return float("nan")
    return math.hypot(px[0] - py[0], px[1] - py[1])


def spearman_positional(x, y):
    """expert_vs_data.py's ranking (ties by position). Used ONLY to check reproduction."""
    x, y = np.asarray(x, float), np.asarray(y, float)

    def rk(a):
        o = np.argsort(a)
        r = np.empty(len(a))
        r[o] = np.arange(len(a))
        return r
    return float(np.corrcoef(rk(x), rk(y))[0, 1])


# ---------------------------------------------------------------- learner gaps ------------------
def learner_cells_ds1275(path):
    """(first position, correct, attempts) per (learner, KC), exactly as expert_vs_data.py builds it."""
    first, acc, seq = {}, defaultdict(lambda: [0, 0]), defaultdict(int)
    with open(path, encoding="utf-8", errors="replace") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            s = r["Anon Student Id"]
            seq[s] += 1
            ok = (r.get("First Attempt") or "").strip().upper() in CORRECT
            for k in (r.get(KC) or "").split("~~"):
                k = k.strip()
                if not k:
                    continue
                first.setdefault((s, k), seq[s])
                acc[(s, k)][0] += ok
                acc[(s, k)][1] += 1
    return first, acc


def learner_cells_pslc(path):
    """The PSLC transaction sample: same rule, transactions sorted by Time, Outcome as correctness."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    rows.sort(key=lambda r: (r["Anon Student Id"], int(r["Time"] or 0)))
    first, acc, seq = {}, defaultdict(lambda: [0, 0]), defaultdict(int)
    for r in rows:
        s = r["Anon Student Id"]
        seq[s] += 1
        ok = (r.get("Outcome") or "").strip().upper() in CORRECT
        k = (r.get(KC) or "").strip()
        if k:
            first.setdefault((s, k), seq[s])
            acc[(s, k)][0] += ok
            acc[(s, k)][1] += 1
    return first, acc, len(rows), len({r["Anon Student Id"] for r in rows})


def all_gaps(first, acc):
    """Order gap for EVERY ordered pair (a, b), accumulated per learner. Returns
    {(a, b): (gap, n_af + n_bf)} for pairs with >= MIN_ORDER learners in each order."""
    overall = defaultdict(lambda: [0, 0])
    for (s, k), (c, n) in acc.items():
        overall[s][0] += c
        overall[s][1] += n
    ability = {s: c / n for s, (c, n) in overall.items() if n >= 20}
    by_s = defaultdict(list)
    for (s, k), f in first.items():
        if s in ability:
            by_s[s].append((k, f))
    sums = defaultdict(lambda: [0.0, 0, 0.0, 0])        # af sum, af n, bf sum, bf n
    for s, cells in by_s.items():
        for b, fb in cells:
            c, n = acc[(s, b)]
            if n < 2:
                continue
            resid = c / n - ability[s]
            for a, fa in cells:
                if a == b:
                    continue
                t = sums[(a, b)]
                if fa < fb:
                    t[0] += resid
                    t[1] += 1
                else:
                    t[2] += resid
                    t[3] += 1
    return {e: (t[0] / t[1] - t[2] / t[3], t[1] + t[3]) for e, t in sums.items()
            if t[1] >= MIN_ORDER and t[3] >= MIN_ORDER}


# ---------------------------------------------------------------- controls ----------------------
def derange_within(levels, rng):
    """A permutation of indices that maps each index to a different index at the same level."""
    levels = np.asarray(levels)
    perm = np.arange(len(levels))
    for lv in np.unique(levels):
        idx = np.flatnonzero(levels == lv)
        if len(idx) < 2:
            continue
        while True:
            p = rng.permutation(idx)
            if np.all(p != idx):
                break
        perm[idx] = p
    return perm


def c1(rating, gap, d, rng, reps=2000):
    d = np.asarray(d)
    keep = np.isin(d, [lv for lv in np.unique(d) if (d == lv).sum() >= 2])
    r, g, dd = np.asarray(rating)[keep], np.asarray(gap)[keep], d[keep]
    rho_t = spearman(r, g)
    null = np.array([spearman(r, g[derange_within(dd, rng)]) for _ in range(reps)])
    return dict(n=int(keep.sum()), dropped=int((~keep).sum()), rho_t=rho_t,
                mean=float(null.mean()), sd=float(null.std()),
                p_one_sided=float((null >= rho_t).mean()))


def match_candidates(treat, pool):
    """For each treatment record, the candidate pool indices under the first rule that yields any.
    Records: dict(d, area, n). Returns (list of index arrays, rule used per pair)."""
    pd = np.array([p["d"] for p in pool])
    pa = np.array([p["area"] for p in pool])
    pn = np.array([p["n"] for p in pool], float)
    cands, rules = [], []
    for t in treat:
        got = None
        for rule, fac, use_area in (("strict", 1.5, True), ("n x2", 2.0, True), ("no area", 2.0, False)):
            m = (pd == t["d"]) & (pn >= t["n"] / fac) & (pn <= t["n"] * fac)
            if use_area:
                m &= pa == t["area"]
            idx = np.flatnonzero(m)
            if len(idx):
                got = (idx, rule)
                break
        cands.append(got[0] if got else np.array([], int))
        rules.append(got[1] if got else "unmatched")
    return cands, rules


def draw_control(cands, order, rng):
    """One assignment without replacement; returns pool index per treatment index (-1 if none)."""
    used, out = set(), np.full(len(cands), -1)
    for i in order:
        c = [j for j in cands[i] if j not in used]
        if not c:
            c = list(cands[i])          # exhausted: allow reuse rather than drop (counted)
        if c:
            j = int(c[rng.integers(len(c))])
            used.add(j)
            out[i] = j
    return out


def c2(rating, gap, cands, pool_gap, rng, n_assign=2000, n_boot=2000):
    rating, gap = np.asarray(rating, float), np.asarray(gap, float)
    pool_gap = np.asarray(pool_gap, float)
    ok = np.array([len(c) > 0 for c in cands])
    n = len(rating)

    def one(idx):
        a = draw_control([cands[i] for i in idx], rng.permutation(len(idx)), rng)
        m = a >= 0
        return spearman(rating[idx][m], pool_gap[a[m]])
    full = np.arange(n)[ok]
    rho_t = spearman(rating[full], gap[full])
    rc = np.array([one(full) for _ in range(n_assign)])
    rho_c = float(np.nanmean(rc))
    deltas = []
    for _ in range(n_boot):
        idx = full[rng.integers(0, len(full), len(full))]
        deltas.append(spearman(rating[idx], gap[idx]) - one(idx))
    deltas = np.array(deltas)
    deltas = deltas[~np.isnan(deltas)]
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return dict(n=int(ok.sum()), unmatched=int((~ok).sum()), rho_t=rho_t, rho_c=rho_c,
                rho_c_sd=float(np.nanstd(rc)), delta=rho_t - rho_c, ci=[float(lo), float(hi)])


def verdict(rho_t, rho_p, rho_c, ci, f1_ok=True, f2_ok=True):
    if not f1_ok:
        return "UNANSWERABLE: floor F1 failed"
    if not rho_t > 0:
        return "NO POSITIVE ASSOCIATION TO CONDITION"
    ec = rho_c >= 0.5 * rho_t
    ep = rho_p < 0.5 * rho_t
    if ec and ep:
        v = "EXPLAINED BY TAXONOMY DISTANCE"
    elif ec or ep:
        v = "MIXED (" + ("matched control reproduces half or more" if ec
                         else "partialling distance removes half or more") + ")"
    elif rho_p > 0 and ci[0] > 0:
        return "SURVIVES TAXONOMY CONTROL"
    else:
        v = "SURVIVES IN POINT, NOT ESTABLISHED"
    return v + ("" if f2_ok else " (UNDERPOWERED: floor F2 failed)")


# ---------------------------------------------------------------- floor -------------------------
def floor(args):
    rng = np.random.default_rng(SEED)
    tax = taxonomy(exercises())
    ann = load_ratings().rows
    ds = [dist(tax, r.prereq, r.dependent) for r in ann]
    ds = np.array([x for x in ds if x is not None])
    p_levels = np.bincount(ds, minlength=3) / len(ds)
    print(f"   floor shape: dist share over {len(ds)} rated rows: "
          + ", ".join(f"{k}:{p:.3f}" for k, p in enumerate(p_levels)))
    N, NPOOL = COMMITTED["n"], 10 * COMMITTED["n"]
    areas = 3                                          # synthetic dependent areas for the family match

    def make(kind, strength):
        d = rng.choice(3, N, p=p_levels)
        dz = (d - d.mean()) / (d.std() or 1)
        S = rng.standard_normal(N)
        cov_t = 15 * 2 + rng.geometric(1 / 40, N)       # coverage ~ 30 + geometric, a stated guess
        area_t = rng.integers(0, areas, N)
        dp = rng.choice(3, NPOOL, p=p_levels)
        dpz = (dp - d.mean()) / (d.std() or 1)
        cov_p = 15 * 2 + rng.geometric(1 / 40, NPOOL)
        area_p = rng.integers(0, areas, NPOOL)
        if kind == "S0":
            rating = -0.6 * dz + 0.8 * rng.standard_normal(N)
            gap = rng.standard_normal(N)
            pool = rng.standard_normal(NPOOL)
        elif kind == "S1":
            rating = -0.6 * dz + 0.8 * S
            gap = strength * S + rng.standard_normal(N)
            pool = rng.standard_normal(NPOOL)
        else:   # S2
            rating = -0.6 * dz + 0.8 * rng.standard_normal(N)
            gap = -strength * dz + rng.standard_normal(N)
            pool = -strength * dpz + rng.standard_normal(NPOOL)
        treat = [dict(d=int(d[i]), area=int(area_t[i]), n=float(cov_t[i])) for i in range(N)]
        pl = [dict(d=int(dp[j]), area=int(area_p[j]), n=float(cov_p[j])) for j in range(NPOOL)]
        return rating, gap, d, treat, pl, pool

    def run(kind, strength, reps):
        calls, rts = defaultdict(int), []
        for _ in range(reps):
            rating, gap, d, treat, pl, pool = make(kind, strength)
            cands, _ = match_candidates(treat, pl)
            r2 = c2(rating, gap, cands, pool, rng, n_assign=args.assign, n_boot=args.boot)
            rp = partial_spearman(rating, gap, d)
            v = verdict(r2["rho_t"], rp, r2["rho_c"], r2["ci"])
            calls[v.split(" (")[0]] += 1
            rts.append(r2["rho_t"])
        return {k: v / reps for k, v in calls.items()}, float(np.mean(rts))

    # calibrate planted strengths so unconditional rho_T ~ target (cheap, no controls)
    def calib(kind, target):
        best = None
        for s in np.linspace(0.05, 3.0, 60):
            vals = []
            for _ in range(300):
                rating, gap, *_ = make(kind, s)
                vals.append(spearman(rating, gap))
            m = float(np.mean(vals))
            if best is None or abs(m - target) < abs(best[1] - target):
                best = (s, m)
        return best

    out = dict(seed=SEED, n_pairs=N, n_pool=NPOOL, dist_share=p_levels.tolist(),
               reps=args.reps, assign=args.assign, boot=args.boot, scenarios={})
    s0, rt0 = run("S0", 0, args.reps)
    out["scenarios"]["S0"] = dict(calls=s0, mean_rho_t=rt0)
    print(f"   S0 null      rho_T {rt0:+.3f}  {s0}")
    s2s, s2m = calib("S2", 0.30)
    s2, rt2 = run("S2", s2s, args.reps)
    out["scenarios"]["S2"] = dict(strength=s2s, calibrated_rho_t=s2m, calls=s2, mean_rho_t=rt2)
    print(f"   S2 distance  rho_T {rt2:+.3f}  {s2}")
    grid = {}
    for target in (0.30, 0.40, 0.50, 0.60):
        s, m = calib("S1", target)
        c, rt = run("S1", s, args.reps)
        grid[f"{target:.2f}"] = dict(strength=s, calibrated_rho_t=m, calls=c, mean_rho_t=rt)
        print(f"   S1 specific  target {target:.2f} rho_T {rt:+.3f}  {c}")
    out["scenarios"]["S1"] = grid
    surv = "SURVIVES TAXONOMY CONTROL"
    f1 = s2.get(surv, 0) <= 0.10 and (s2.get("EXPLAINED BY TAXONOMY DISTANCE", 0)
                                      + s2.get("MIXED", 0)) >= 0.50
    f2 = grid["0.30"]["calls"].get(surv, 0) >= 0.80
    f3 = s0.get(surv, 0) <= 0.05
    mde = next((t for t, g in grid.items() if g["calls"].get(surv, 0) >= 0.80), None)
    out.update(F1_confound_recognised=f1, F2_power_at_0_30=f2, F3_size=f3,
               mde_80=mde, note="scored by the same script that defines it: a smoke check, "
               "not an independent validation; rating-distance strength fixed at -0.6 latent")
    print(f"   F1 {'PASS' if f1 else 'FAIL'}  F2 {'PASS' if f2 else 'FAIL'}  F3 "
          f"{'PASS' if f3 else 'FAIL'}  MDE(80%) {mde}")
    OUT.mkdir(exist_ok=True)
    (OUT / "floor.json").write_text(json.dumps(out, indent=2) + "\n")


# ---------------------------------------------------------------- real --------------------------
def boot_pairs(stat, keys, rng, reps=2000):
    """Bootstrap clustered by unordered pair. `stat` takes an index array of rows."""
    groups = defaultdict(list)
    for i, k in enumerate(keys):
        groups[k].append(i)
    g = list(groups.values())
    vals = []
    for _ in range(reps):
        idx = np.concatenate([g[j] for j in rng.integers(0, len(g), len(g))])
        v = stat(idx)
        if not np.isnan(v):
            vals.append(v)
    return [float(x) for x in np.percentile(vals, [2.5, 97.5])]


def real(args):
    rng = np.random.default_rng(SEED)
    rows = exercises()
    tax = taxonomy(rows)
    area = {n: t[1] for n, t in tax.items()}
    authored = set(authored_edges(rows=rows))
    ann = load_ratings().rows
    res = dict(seed=SEED, committed=COMMITTED)

    # ---- held: ratings vs distance, all rated rows --------------------------------------------
    keep = [i for i, r in enumerate(ann) if dist(tax, r.prereq, r.dependent) is not None]
    rt = np.array([ann[i].prerequisite for i in keep])
    dd = np.array([dist(tax, ann[i].prereq, ann[i].dependent) for i in keep])
    md = np.array([mapdist(tax, ann[i].prereq, ann[i].dependent) for i in keep])
    key = [frozenset(ann[i].pair) for i in keep]
    rho_rd = spearman(rt, dd)
    res["rating_vs_dist_all_rows"] = dict(
        n_rows=len(keep), n_dropped=len(ann) - len(keep), n_unordered=len(set(key)),
        dist_counts={str(k): int((dd == k).sum()) for k in range(3)},
        mean_rating_by_dist={str(k): float(rt[dd == k].mean()) for k in range(3) if (dd == k).any()},
        spearman=rho_rd, ci=boot_pairs(lambda ix: spearman(rt[ix], dd[ix]), key, rng),
        spearman_mapdist=spearman(rt, md),
        ci_mapdist=boot_pairs(lambda ix: spearman(rt[ix], md[ix]), key, rng),
        resamples="unordered rated pairs (a pair rated in both orders moves together), 2000")
    print(f"   rating vs dist (all {len(keep)} rows): Spearman {rho_rd:+.4f} "
          f"{res['rating_vs_dist_all_rows']['ci']}")

    # ---- held: AUX, map-vs-raters d against distance-matched rows -----------------------------
    isa = np.array([ann[i].pair in authored for i in keep])

    def d_raw(ix):
        y, n = rt[ix][isa[ix]], rt[ix][~isa[ix]]
        if len(y) < 2 or len(n) < 2:
            return float("nan")
        sd = np.sqrt(((len(y) - 1) * y.var(ddof=1) + (len(n) - 1) * n.var(ddof=1)) / (len(y) + len(n) - 2))
        return float((y.mean() - n.mean()) / sd)

    def d_strat(ix):
        r, a, d = rt[ix], isa[ix], dd[ix]
        sd = r.std(ddof=1)
        num, w = 0.0, 0
        for lv in range(3):
            m = d == lv
            if (m & a).sum() >= 2 and (m & ~a).sum() >= 2:
                num += (m & a).sum() * (r[m & a].mean() - r[m & ~a].mean())
                w += (m & a).sum()
        return float(num / w / sd) if w else float("nan")
    dr, dsr = d_raw(np.arange(len(keep))), d_strat(np.arange(len(keep)))
    aux = dict(d_raw=dr, ci_raw=boot_pairs(d_raw, key, rng), d_strat=dsr,
               ci_strat=boot_pairs(d_strat, key, rng),
               authored_by_dist={str(k): int((isa & (dd == k)).sum()) for k in range(3)},
               other_by_dist={str(k): int((~isa & (dd == k)).sum()) for k in range(3)},
               note="d_raw here uses rows with a known taxonomy; expert_vs_data.py's 0.955 uses all rows")
    lo = aux["ci_strat"][0]
    aux["verdict"] = ("MAP-RATER AGREEMENT SURVIVES DISTANCE MATCHING" if dsr >= 0.5 * dr and lo > 0
                      else "MAP-RATER AGREEMENT EXPLAINED BY DISTANCE"
                      if dsr < 0.5 * dr and lo <= 0 <= aux["ci_strat"][1]
                      else "MAP-RATER AGREEMENT ATTENUATED BY DISTANCE")
    res["aux_map_vs_raters"] = aux
    print(f"   AUX d raw {dr:.4f} {aux['ci_raw']}, distance-stratified {dsr:.4f} {aux['ci_strat']} "
          f"-> {aux['verdict']}")

    # ---- learner side --------------------------------------------------------------------------
    ds_dir = data_path("DS1275_DIR", must_exist=False)
    src = None
    if ds_dir and Path(ds_dir).exists():
        from shared.corpus import ds1275_export
        first, acc = learner_cells_ds1275(ds1275_export(ds_dir))
        src = "ds1275 'All Data'"
    else:
        pslc = Path(os.environ.get("JUNYI_DIR") or data_path("JUNYI_DIR")) / "junyi_ProblemLog_for_PSLC.txt"
        first, acc, n_rows, n_learners = learner_cells_pslc(pslc)
        src = "junyi_ProblemLog_for_PSLC.txt (ds1275 not on disk)"
        res["fallback_log"] = dict(rows=n_rows, learners=n_learners,
                                   learner_exercise_cells=len(acc))
    gaps = all_gaps(first, acc)
    del first, acc
    tr = [(i, r) for i, r in enumerate(ann) if r.pair in gaps]
    ratings = [r.prerequisite for _, r in tr]
    g = [gaps[r.pair][0] for _, r in tr]
    rep_rho = spearman_positional(ratings, g) if len(tr) >= 3 else float("nan")
    reproduces = len(tr) == COMMITTED["n"] and abs(rep_rho - COMMITTED["rho"]) < 0.001
    res["learner_source"] = src
    res["reproduction"] = dict(n_pairs=len(tr), rho_positional=rep_rho, reproduces=reproduces,
                               rule="exactly 47 pairs and |rho - 0.29914| < 0.001")
    print(f"   learner source: {src}; {len(tr)} rated pairs with >= {MIN_ORDER} per order; "
          f"reproduces committed result: {reproduces}")
    floor_res = json.loads((OUT / "floor.json").read_text()) if (OUT / "floor.json").exists() else {}
    f1, f2 = floor_res.get("F1_confound_recognised"), floor_res.get("F2_power_at_0_30")
    res["floor"] = dict(F1=f1, F2=f2, F3=floor_res.get("F3_size"), mde_80=floor_res.get("mde_80"))
    if not reproduces:
        res["verdict"] = "BLOCKED: learner data not reproducible"
        res["blocked"] = ("ds1275 is a DataShop upload-only export (login); the Junyi 2015 problem log "
                          "on disk does not reproduce the committed 47-pair result, so rho_T, rho_p, "
                          "C1, C2 and RAW(gap, dist) are not estimated")
        write(res)
        return

    # ---- full analysis (runs only when the learner data reproduces) -------------------------
    ratings, g = np.array(ratings), np.array(g)
    dt = np.array([dist(tax, r.prereq, r.dependent) for _, r in tr], float)
    mt = np.array([mapdist(tax, r.prereq, r.dependent) for _, r in tr])
    n_t = np.array([gaps[r.pair][1] for _, r in tr], float)
    rho_t = spearman(ratings, g)
    levels = {str(k): int((dt == k).sum()) for k in range(3)}
    res["treatment"] = dict(n=len(tr), rho_t=rho_t, dist_counts=levels,
                            rating_vs_dist=spearman(ratings, dt), gap_vs_dist=spearman(g, dt),
                            gap_vs_mapdist=spearman(g, mt), median_coverage=float(np.median(n_t)))
    if sum(v >= 5 for v in levels.values()) < 2:
        res["verdict"] = ("DISTANCE CONSTANT IN TREATMENT: the association cannot be a distance "
                          "artefact within these pairs")
        write(res)
        return
    rho_p = partial_spearman(ratings, g, dt)
    res["partial"] = dict(rho_p=rho_p, rho_p_mapdist=partial_spearman(ratings, g, np.nan_to_num(mt)))
    res["C1"] = c1(ratings, g, dt, rng)
    rated_any = {frozenset(r.pair) for r in ann}
    pool_keys = [e for e in gaps if frozenset(e) not in rated_any and dist(tax, *e) is not None]
    pool = [dict(d=dist(tax, *e), area=area[e[1]], n=float(gaps[e][1])) for e in pool_keys]
    pool_gap = [gaps[e][0] for e in pool_keys]
    treat = [dict(d=int(dt[i]), area=area[r.dependent], n=float(n_t[i])) for i, (_, r) in enumerate(tr)]
    cands, rules = match_candidates(treat, pool)
    pg = np.array(pool_gap)
    pd_ = np.array([p["d"] for p in pool])
    res["pool"] = dict(n=len(pool_keys), authored_share=float(np.mean([e in authored for e in pool_keys])),
                       gap_vs_dist=spearman(pg, pd_),
                       mean_gap_by_dist={str(k): float(pg[pd_ == k].mean()) for k in range(3) if (pd_ == k).any()},
                       match_rules={k: rules.count(k) for k in set(rules)})
    r2 = c2(ratings, g, cands, pool_gap, rng)
    res["C2"] = r2
    matched_ok = sum(r in ("strict", "n x2") for r in rules) >= 0.9 * len(rules)
    med_c = float(np.median([pool[j]["n"] for c in cands for j in c[:1]])) if any(len(c) for c in cands) else 0
    scale = check_control_scale({"treatment_pairs": len(tr), "control_pairs": r2["n"]},
                                ["control_pairs"], strict=False)
    scale_n = check_control_scale({"treatment_coverage": float(np.median(n_t)), "control_coverage": med_c},
                                  ["control_coverage"], strict=False)
    res["C2"]["scale"] = dict(pairs=scale["report"], coverage=scale_n["report"], under_matched=not matched_ok)
    v = verdict(rho_t, rho_p, r2["rho_c"], r2["ci"], f1_ok=f1 is not False, f2_ok=bool(f2))
    res["verdict"] = v + ("" if matched_ok else " [C2 UNDER-MATCHED]")
    print(f"   verdict: {res['verdict']}")
    write(res)


def _finite(x):
    """NaN/inf become null so the output is valid JSON (CHANGES 2026-10-07)."""
    if isinstance(x, float) and not math.isfinite(x):
        return None
    if isinstance(x, dict):
        return {k: _finite(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_finite(v) for v in x]
    return x


def write(res):
    OUT.mkdir(exist_ok=True)
    (OUT / "taxonomy-control.json").write_text(json.dumps(_finite(res), indent=2) + "\n")
    print(f"   verdict: {res['verdict']}\n   wrote out/taxonomy-control.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--reps", type=int, default=500)
    ap.add_argument("--assign", type=int, default=200)
    ap.add_argument("--boot", type=int, default=400)
    a = ap.parse_args()
    floor(a) if a.floor else real(a)
