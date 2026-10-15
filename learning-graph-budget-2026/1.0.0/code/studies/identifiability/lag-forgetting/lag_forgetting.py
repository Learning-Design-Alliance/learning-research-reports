"""
Is the lag decay of the prerequisite drop forgetting of A, or the edge weakening?

QUESTION. `studies/identifiability/overlap/lag_bands.py` found that the drop (first-attempt B accuracy
of learners who had passed A before B, minus that of learners who had attempted A and never passed it)
shrinks with the lag from first touching A to first touching B: within-pair
D = drop(>= 7 days) - drop(< 1 day) is -0.062 [-0.080, -0.043] on ASSISTments, -0.033 on XES3G5M,
-0.015 on EdNet, -0.048 on Eedi (verdict LAG-DEPENDENT; `out/lag_bands.json` there), and
`studies/identifiability/domain-mechanism/` reads DECAYS in 12 of 13 domains. Paper II's F1 reports
this as "the drop shrinks with the time between the two skills".

The literature gives a second reading (literature review for Paper II, synthesis row 4 and strand-2
analysis 1). Matayoshi, Cosyn, Uzun & Kurd-Misto (2025, JEDM 17(1), entry 2.20) randomised ALEKS
mastery thresholds and found the retention advantage of the higher threshold on the SAME topic shrinks
over weeks to under 0.02: an advantage from having mastered A fades because A itself is forgotten.
Cepeda, Vul, Rohrer, Wixted & Pashler (2008, Psych. Sci. 19(11), entry 2.14) found final-test
performance first rises and then falls as the gap between study and review grows: a lag profile need
not be monotone. So the drop may shrink because learners who passed A long ago no longer hold A when
they meet B (forgetting; the edge is intact), not because B depends less on A (the edge weakens).

THE IDEA. Hold A's CURRENT state at B fixed. A learner's attempt at A shortly before their first
attempt at B is a reading of what they hold in A at B. If the drop shrinks only because past masters
forget A, then among past masters who still get A right just before B the drop does not shrink.

DATA. Reads four licensed corpora through the same adapters lag_bands.py uses (aggregates only are
written; no learner rows, item text or skill names):
  ASSISTments 2012-13 skill builders  build_matrix.LOADERS["assist"] (assist_rich.csv), skill_id as A/B
  XES3G5M                             atlas.xes3g5m_rows (attempts.tsv), KC grain
  EdNet KT1                           atlas.ednet_rows (ednet-kt1.zip prefix of 6,000 learners), first tag
  Eedi NeurIPS 2020                   atlas.eedi_rows (answers.tsv), level-3 subject grain. Eedi keeps
                                      only each learner's LATEST answer to each question, so a "recent
                                      A attempt" is a latest answer to another question of subject A;
                                      a re-answer of the same question is invisible
                                      (`studies/identifiability/overlap/LAG-BANDS.md`).
EDM Cup is left out: lag_bands found no pair readable at short lags there.
Corpora come from $LDA_SCRATCH_DIR through shared.paths.data_path; no file is derived.

DEFINITIONS (one learner-pair case = a learner who first touched A before first touching B)
  tb          time of the learner's first attempt at B; y = its outcome
  lag         tb - (time of first attempt at A), in days -- lag_bands' definition, unchanged
  arm         MASTERED (an A attempt correct before tb) or FAILED (A attempted before tb, never correct)
  recent A    the learner's LAST attempt at A strictly before tb, if tb - t(last A) <= W = 1 day
  R           outcome of that recent A attempt (FAILED cases have R = 0 by construction)
  In the EARLY band (lag < 1 day) every case has a recent A attempt, since the last A attempt cannot
  be further back than the first. In MID and LATE a recent A attempt means A was re-attempted within
  a day of B.

  bands       EARLY [0, 1) d, MID [1, 7) d, LATE [7, inf) d (lag_bands' primary bands)
  shape bands [0, 1 h), [1 h, 1 d), [1, 7) d, [7, 30) d, [30, inf) d (finer at short lags, where a
              Cepeda-type rise would sit)
  pair sample lag_bands' exactly: every ordered pair of items, then 10,000 drawn with atlas.corpus_rng
              (name-keyed), so these are the same pairs lag_bands read
  readable    a cell needs >= MIN_CELL (5) cases in each arm and the MASTERED rate inside (0.01, 0.99)

THREE DROPS PER PAIR AND BAND
  drop_full   p(MASTERED) - p(FAILED), every case                                  (lag_bands' drop)
  drop_sub    p(MASTERED) - p(FAILED), cases with a recent A attempt only          (same selection as
                                                                                      the held drop)
  drop_held   p(MASTERED, R = 1) - p(FAILED), cases with a recent A attempt only   (A's current state
              held: past masters who still answer A correctly, against learners who never passed A and
              answer it wrongly now)
  D_x = drop_x(LATE) - drop_x(EARLY), within pair, over the pairs where drop_sub AND drop_held are
  readable in both EARLY and LATE (the "held pairs"); D_full is also reported on those pairs, so
  D_full - D_sub shows what the selection into having a recent A attempt does by itself.

PRIMARY ESTIMAND as first registered (SECONDARY 3 since 2026-10-07; see CHANGES): on the held pairs,
  D_sub, D_held, Delta = D_held - D_sub, and share explained = (D_sub - D_held) / D_sub, signed
  (1 = holding A's current state removes all the decay; 0 = removes none; < 0 = holding A makes the
  decay larger; > 1 = holding A reverses it). 95% intervals from 2,000 cluster-bootstrap draws
  resampling B items (lag_bands' unit; the B item is what each pair's outcome is measured on), all
  statistics from the same draws.

POSITIVITY (step 1, reported before anything else, per corpus and band): learner-pair cases, cases
with a recent A attempt (by arm), MASTERED cases with R = 1, and pairs readable for each drop.

PRE-REGISTERED VERDICTS (per corpus, in this order)
  UNANSWERABLE        fewer than 30 held pairs (MIN_BOTH, lag_bands' threshold)
  NO-DECAY-TO-SPLIT   D_sub's interval is not entirely below 0: on the cases where A's current state
                      can be read, there is no decay to apportion
  MOSTLY-FORGETTING   share explained >= 0.5 AND Delta's interval entirely above 0 (holding A's current
                      state removes most of the decay); reported with whether D_held's interval still
                      excludes 0 (a residual)
  EDGE-WEAKENS        D_held's interval entirely below 0 (same sign as D, excludes 0) AND share
                      explained < 0.5: the decay survives with A's current state held
  UNRESOLVED          otherwise
  programme           LAG DECAY IS FORGETTING OF A   >= 2 corpora MOSTLY-FORGETTING, none EDGE-WEAKENS
                      THE EDGE WEAKENS WITH LAG       >= 2 corpora EDGE-WEAKENS, none MOSTLY-FORGETTING
                      CORPUS-DEPENDENT                at least one of each
                      UNRESOLVED                      otherwise
  DIRECTION. Every comparison above is signed. D < 0 is decay; "explained" is the part of D_sub that
  D_held no longer has, with sign.

SECONDARY 1, BOTH ARMS' ABSOLUTE ACCURACY (descriptive, plot-free). On the pairs where drop_full is
  readable in EARLY and LATE (lag_bands' pair set), the pair-mean p(MASTERED) and p(FAILED) in each
  band, their changes dM = pM(LATE) - pM(EARLY) and dF = pF(LATE) - pF(EARLY) with B-item bootstrap
  intervals, and the signed shares of D_full = dM - dF: dM / D_full (advantaged arm falls) and
  -dF / D_full (disadvantaged arm rises), which sum to 1. Labels:
  ADVANTAGED-FALLS (dM interval below 0 and its share >= 0.5), DISADVANTAGED-RISES (dF interval above 0
  and its share >= 0.5), NEITHER-DOMINATES otherwise. The same on the held pairs with pM(R = 1).
  Descriptive only: the learners differ across bands.

SECONDARY 2, RISE-THEN-FALL (Cepeda; rule revised 2026-10-07, see CHANGES). drop_full in the five shape bands; for each adjacent pair of bands
  the within-pair contrast (later minus earlier) over pairs readable in both, with a B-item bootstrap
  interval (2,000 draws).
  NON-MONOTONE        some interior band k has contrast(k-1 -> k) interval entirely above 0 AND
                      contrast(k -> k+1) interval entirely below 0 (a rise, then a fall)
  MONOTONE-DECREASING no adjacent contrast has an interval entirely above 0, and at least one has an
                      interval entirely below 0
  OTHER               otherwise (named by which contrasts are signed)
  Adjacent contrasts with fewer than 30 readable pairs are reported and count as unsigned.

CONTROLS AND WHY NO PERMUTATION. The comparison is within pair (each pair is its own control across
bands), as in lag_bands. The relevant control is the selection one: drop_sub is the drop on exactly
the cases drop_held uses, minus only the R = 1 restriction, so Delta isolates the conditioning on A's
current state and not the selection into having a recent A attempt (D_full vs D_sub shows that
separately). No permutation null is used; the bootstrap resamples B items, the unit the outcome is
measured on.

FLOOR (run first, on synthetic learners; no real number is read unless it passes). Learners meet 48
items, a chain of planted gates, in random order, 1-3 attempts each, sessions with breaks of days
(lag_bands' clock). Each learner holds a latent state per item; an attempt is correct with probability
1 - slip (0.10) if held and guess (0.20) if not, plus a logistic ability term; a wrong attempt teaches
the item with probability 0.3. Before a first attempt at an item whose parent was touched, the learner
reviews the parent once with probability 0.5 (so recent-A cases exist at every lag). The child's first
attempt loses `gate` (0.30) if the parent is not CURRENTLY held:
  FORGET   held parent knowledge is lost at rate 1/10 per day; the gate is constant
  EDGE     no forgetting; the gate shrinks as exp(-lag/10 days), lag from first touching the parent
  NULL     no forgetting; constant gate
  HUMP     no forgetting; gate x (lag/2 d) x exp(1 - lag/2 d) (zero at lag 0, peak at 2 days)
Three seeds each, gated pairs only. Pass requires, in 3 of 3 seeds:
  FORGET -> MOSTLY-FORGETTING; EDGE -> EDGE-WEAKENS; NULL -> neither MOSTLY-FORGETTING nor EDGE-WEAKENS;
  HUMP -> shape NON-MONOTONE; FORGET and EDGE -> shape not NON-MONOTONE.
If the primary split fails its part, every real verdict is UNANSWERABLE (positivity and the
descriptive secondaries are still reported); if only the shape part fails, the shape verdicts are
reported as UNANSWERABLE and the rest stands.

WHAT IT CAN AND CANNOT SAY.
- R is ONE reading of A's state. Slips and guesses misclassify; in a forgetting world the LATE masters
  with R = 1 include lucky guessers who forgot A, so D_held keeps some decay that is forgetting. The
  instrument therefore leans toward EDGE-WEAKENS; the floor shows by how much on a 0.20 guess rate.
- The re-attempt of A just before B is itself practice (retrieval), so "A's state at B" is the state
  after that attempt's learning, in every band alike.
- Learners who re-attempt A weeks later and then meet B within a day differ from those who do not
  (review assignments, teachers, motivation). D_full vs D_sub shows how far that selection moves D;
  it does not remove selection on unobservables between bands.
- Arbitrary pairs, not edges: as in lag_bands, D describes how the estimand moves with lag; the split
  says how much of that movement tracks A's current state.
- Pairs share A items and the B-item bootstrap does not absorb A-item dependence, so intervals may
  be narrow (lag_bands' caveat).
- Eedi: latest answers only (above); its recent-A cases are latest answers to other questions of A.

    python3 lag_forgetting.py floor
    python3 lag_forgetting.py real [--corpora assist,xes3g5m,ednet,eedi]

CHANGES

2026-10-07 (after the first floor run, before any real corpus was read). The floor FAILED on both
parts (`out/floor_v1_failed.json`), and both failures have a structural cause, so the design changes
rather than the thresholds or the planted worlds, which are kept exactly.
  1. The single-reading split above (now SECONDARY 3, "single_reading") returned EDGE-WEAKENS in the
     pure-forgetting world in 3 of 3 seeds: D_held kept 81-88% of D_sub (share explained +0.19,
     +0.12, +0.13). Cause, as the caveat above predicted: with a 0.20 guess rate, past masters with
     R = 1 at long lags still include many who forgot A and guessed, so restricting to R = 1 removes
     only part of the forgetting. Restricting harder (two recent correct readings) costs positivity
     and still leaves guess contamination.
     NEW PRIMARY (Wald split). Define the arm WITHOUT the reading: among cases with at least two A
     attempts before tb, the last of them within W of tb, the arm is MASTERED' if an A attempt BEFORE
     that last one was correct, FAILED' otherwise. R, the last attempt's outcome, is then a fresh,
     equally noisy reading of A's state in both arms (FAILED' learners can answer A correctly now).
     Per band, over the held pairs (readable in EARLY and LATE: >= 5 cases per arm, MASTERED' rate
     inside (0.01, 0.99)):
       drop_b = mean over pairs of p(B | MASTERED') - p(B | FAILED')
       gap_b  = mean over pairs of p(R = 1 | MASTERED') - p(R = 1 | FAILED')   (A's own gap at B: the
                quantity Matayoshi et al. randomise, here between past masters and non-masters)
       E_b    = drop_b / gap_b   (the drop in B per unit of current A-accuracy gap: the edge)
     If R = guess + (1 - slip - guess) x K in both arms, misclassification scales gap_b by the same
     constant in every band, so E_b is constant under pure forgetting and E_b falls under a weakening
     edge. D_sub = drop_LATE - drop_EARLY; D_held = drop the LATE band would have with the EARLY A-gap,
     minus drop_EARLY = drop_LATE x gap_EARLY / gap_LATE - drop_EARLY; Delta = D_held - D_sub; share
     explained = (D_sub - D_held) / D_sub, signed, as before. All from the same 2,000 B-item draws.
     Verdicts and the programme rule are unchanged, with one added first: UNRESOLVED-NO-A-GAP if
     gap_EARLY's or gap_LATE's interval is not entirely above 0 (the ratio has no denominator). The
     gap's own change (gap_LATE - gap_EARLY, with interval) is reported: it is the direct reading of
     whether past masters' A advantage fades with lag.
     The arms here are not lag_bands' arms (a learner whose only correct A attempt is the last one
     before B is FAILED'), so D_sub is reported beside lag_bands' D_full and the v1 split; the
     identifying assumption is that past mastery moves B only through A's state at B plus a
     component constant across bands (exclusion), and the floor is what checks it holds well enough.
  2. The shape test returned NON-MONOTONE in 1 of 3 HUMP seeds: adjacent-band contrasts on 47 pairs
     cannot see a rise spread over two bands (0-1 h -> 1-7 d rose +0.025 to +0.044 in sum, no single
     step significant). NEW SHAPE RULE: for each interior band k (1 h-1 d, 1-7 d, 7-30 d), rise =
     contrast(0-1 h -> k), fall = contrast(k -> 30 d+), each with a Bonferroni 98.33% interval (three
     interior bands). NON-MONOTONE if some k has rise entirely above 0 and fall entirely below 0;
     MONOTONE-DECREASING if contrast(0-1 h -> 30 d+) (95%) is entirely below 0 and no rise is entirely
     above 0; OTHER otherwise. Adjacent contrasts are still reported and gate nothing.
  The floor's pass rule is unchanged and applies to the new primary and shape rule. If it fails again,
  the real verdicts are UNANSWERABLE as written above; nothing further is changed tonight.

2026-10-07, second floor run (`out/floor.json`), still before any real corpus was read. FAILS, on
power, not on direction. Split: FORGET -> MOSTLY-FORGETTING 3 of 3 (gap +0.26 -> +0.05; share
explained +1.15, +1.45, +2.57); EDGE -> EDGE-WEAKENS 2 of 3, the third NO-DECAY-TO-SPLIT (D_sub
-0.024 [-0.049, +0.001]: the decay on the Wald subset missed by 0.001); NULL -> NO-DECAY-TO-SPLIT
3 of 3. No world ever returned the other world's verdict. Shape: HUMP -> NON-MONOTONE 2 of 3; FORGET
and EDGE never NON-MONOTONE. As registered, every real primary and shape verdict is therefore
UNANSWERABLE. The computed values are still written (`verdict_as_computed`) beside positivity and
the descriptive arms, labelled as the output of an instrument that failed its floor. Nothing is
changed. A diagnostic run of the identical floor at 9,000 learners (`floor-diagnostic`,
`out/floor_diagnostic_9000.json`) is run before the real data and gates nothing; it says only
whether a larger synthetic sample passes, i.e. whether a re-registration with a power-matched floor
is worth the maintainer's time.

2026-10-07, implementation only, during the real run. Eedi reached 3.9 GB with Python lists, over
the brief's 3 GB budget; the run was stopped and build() now stores times in array('d') and outcomes
in a bytearray. Re-running the floor reproduced `out/floor.json` byte for byte, and XES3G5M's
already-written real row reproduced exactly. A print line read a key the Wald output names
`share_explained_ci` and crashed after Eedi's computation and before its write; the key was fixed,
and each corpus is now written before it is printed. No estimand, threshold or sample changed.

DIRECTION: symmetric -- A and B take their roles from each learner's timeline (A attempted before B);
no edge orientation is read, so no reversed-arrow control applies.
"""

from __future__ import annotations

import bisect
from array import array
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

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OVERLAP = REPO / "studies/identifiability/overlap"
sys.path.insert(0, str(OVERLAP))
sys.path.insert(0, str(REPO / "studies/identifiability/latent-shape"))
sys.path.insert(0, str(REPO))

from positivity import MIN_CELL  # noqa: E402
from lag_bands import to_seconds  # noqa: E402

DAY, HOUR = 86400.0, 3600.0
W = 1.0 * DAY                    # recent-A window
BANDS = [("EARLY", 0.0, 1.0), ("MID", 1.0, 7.0), ("LATE", 7.0, math.inf)]
SHAPE = [("0-1h", 0.0, 1 / 24), ("1h-1d", 1 / 24, 1.0), ("1-7d", 1.0, 7.0), ("7-30d", 7.0, 30.0),
         ("30d+", 30.0, math.inf)]
MAX_PAIRS, MIN_BOTH, BOOT = 10_000, 30, 2000
CORPORA = ["assist", "xes3g5m", "ednet", "eedi"]


def band(lag_days, bands):
    for name, lo, hi in bands:
        if lo <= lag_days < hi:
            return name
    return bands[-1][0]


# ------------------------------------------------------------------ data structure

def build(rows):
    """Per learner, per item: sorted attempt times and outcomes. Also the B index (first touch)."""
    # Compact store (2026-10-07, a memory fix only; Eedi reached 3.9 GB with Python lists): times in
    # array('d'), outcomes in a bytearray. Sorting and every value read are unchanged.
    att = defaultdict(dict)
    for learner, item, ok, t, _h1, _h2 in rows:
        d = att[sys.intern(str(learner))]
        it = sys.intern(str(item))
        rec = d.get(it)
        if rec is None:
            rec = d[it] = (array("d"), bytearray())
        rec[0].append(t)
        rec[1].append(1 if ok else 0)
    idx = defaultdict(list)
    for learner, d in att.items():
        for item, (ts, oks) in list(d.items()):
            if any(ts[i] > ts[i + 1] for i in range(len(ts) - 1)):
                order = sorted(range(len(ts)), key=ts.__getitem__)
                ts = array("d", (ts[i] for i in order))
                oks = bytearray(oks[i] for i in order)
            fpi = oks.find(1)
            d[item] = (ts, oks, None if fpi < 0 else fpi)
            idx[item].append((learner, ts[0], bool(oks[0])))
    return att, idx


def cases(a, b, tl, idx):
    """Every learner-pair case for (A, B): (lag_days, arm_m, recent, R, y, n_before, m_prior).

    m_prior: an A attempt correct BEFORE the last A attempt before tb (the arm of the 2026-10-07
    Wald split, defined without the reading R); n_before: A attempts before tb."""
    out = []
    for learner, tb, y in idx[b]:
        rec = tl[learner].get(a)
        if rec is None:
            continue
        ts, oks, fpi = rec
        if ts[0] >= tb:
            continue
        j = bisect.bisect_left(ts, tb) - 1
        m = fpi is not None and fpi <= j
        recent = (tb - ts[j]) <= W
        r = oks[j]
        if not m:
            assert not r
        m_prior = fpi is not None and fpi < j
        out.append(((tb - ts[0]) / DAY, m, recent, r, y, j + 1, m_prior))
    return out


def _drop(m, f):
    if len(m) < MIN_CELL or len(f) < MIN_CELL:
        return None
    pm = sum(m) / len(m)
    if pm <= 0.01 or pm >= 0.99:
        return None
    return pm, sum(f) / len(f)


def pair_stats(cs):
    """Per band: (pM, pF) for full / sub / held, and per shape band (pM, pF) full; positivity counts."""
    cells = defaultdict(lambda: {"fm": [], "ff": [], "sm": [], "sf": [], "hm": [],
                                 "wm": [], "wf": [], "wrm": [], "wrf": []})
    shape = defaultdict(lambda: {"m": [], "f": []})
    for lag, m, recent, r, y, nb, mp in cs:
        c = cells[band(lag, BANDS)]
        if recent and nb >= 2:
            (c["wm"] if mp else c["wf"]).append(y)
            (c["wrm"] if mp else c["wrf"]).append(r)
        (c["fm"] if m else c["ff"]).append(y)
        if recent:
            (c["sm"] if m else c["sf"]).append(y)
            if m and r:
                c["hm"].append(y)
        s = shape[band(lag, SHAPE)]
        (s["m"] if m else s["f"]).append(y)
    res = {}
    for name, _, _ in BANDS:
        c = cells[name]
        w = _drop(c["wm"], c["wf"])
        if w is not None:
            w = w + (sum(c["wrm"]) / len(c["wrm"]), sum(c["wrf"]) / len(c["wrf"]))
        res[name] = dict(full=_drop(c["fm"], c["ff"]), sub=_drop(c["sm"], c["sf"]),
                         held=_drop(c["hm"], c["sf"]), wald=w,
                         n=dict(cases=len(c["fm"]) + len(c["ff"]), m=len(c["fm"]), f=len(c["ff"]),
                                recent_m=len(c["sm"]), recent_f=len(c["sf"]), held_m=len(c["hm"]),
                                wald_m=len(c["wm"]), wald_f=len(c["wf"])))
    res["shape"] = {name: _drop(shape[name]["m"], shape[name]["f"]) for name, _, _ in SHAPE}
    return res


# ------------------------------------------------------------------ bootstrap

def boot_weights(groups_of_rows, rng):
    """(BOOT x n_rows) weights from resampling clusters with replacement."""
    keys = sorted(set(groups_of_rows))
    pos = {k: i for i, k in enumerate(keys)}
    g = np.array([pos[k] for k in groups_of_rows])
    counts = rng.multinomial(len(keys), [1 / len(keys)] * len(keys), size=BOOT)
    return counts[:, g].astype(float)


def wmean(wts, x):
    s = wts.sum(axis=1)
    return (wts * x).sum(axis=1) / np.where(s > 0, s, np.nan)


def ci(v):
    v = v[np.isfinite(v)]
    lo, hi = np.percentile(v, [2.5, 97.5])
    return [float(lo), float(hi)]


def primary(stats, bs, seed=0):
    rows = [(b, s) for b, s in zip(bs, stats)
            if all(s[k][x] is not None for k in ("EARLY", "LATE") for x in ("sub", "held"))]
    out = dict(held_pairs=len(rows))
    if len(rows) < MIN_BOTH:
        out["verdict"] = "UNANSWERABLE"
        return out

    def D(x):
        return np.array([(s["LATE"][x][0] - s["LATE"][x][1]) - (s["EARLY"][x][0] - s["EARLY"][x][1])
                         if s["LATE"][x] is not None and s["EARLY"][x] is not None else np.nan
                         for _, s in rows])

    dsub, dheld, dfull = D("sub"), D("held"), D("full")
    wts = boot_weights([b for b, _ in rows], np.random.default_rng(seed))
    bsub, bheld = wmean(wts, dsub), wmean(wts, dheld)
    bdelta = bheld - bsub
    bshare = (bsub - bheld) / bsub
    msub, mheld = float(dsub.mean()), float(dheld.mean())
    share = (msub - mheld) / msub if msub != 0 else float("nan")
    full_ok = np.isfinite(dfull)
    out.update(D_sub=msub, D_sub_ci=ci(bsub), D_held=mheld, D_held_ci=ci(bheld),
               delta=mheld - msub, delta_ci=ci(bdelta), share_explained=share, share_ci=ci(bshare),
               D_full_same_pairs=float(dfull[full_ok].mean()) if full_ok.any() else None,
               D_full_pairs=int(full_ok.sum()))
    if full_ok.sum() >= MIN_BOTH:
        wf = boot_weights([b for (b, _), ok in zip(rows, full_ok) if ok], np.random.default_rng(seed + 1))
        out["D_full_same_pairs_ci"] = ci(wmean(wf, dfull[full_ok]))
    for k in ("EARLY", "LATE"):
        for x in ("sub", "held"):
            out[f"mean_{x}_{k}"] = dict(pM=float(np.mean([s[k][x][0] for _, s in rows])),
                                        pF=float(np.mean([s[k][x][1] for _, s in rows])))
    if out["D_sub_ci"][1] >= 0:
        v = "NO-DECAY-TO-SPLIT"
    elif share >= 0.5 and out["delta_ci"][0] > 0:
        v = "MOSTLY-FORGETTING"
    elif out["D_held_ci"][1] < 0 and share < 0.5:
        v = "EDGE-WEAKENS"
    else:
        v = "UNRESOLVED"
    out["verdict"] = v
    out["held_residual_excludes_0"] = bool(out["D_held_ci"][1] < 0 or out["D_held_ci"][0] > 0)
    return out


def primary_wald(stats, bs, seed=0):
    """The 2026-10-07 primary: drop = E x g, with g the arms' gap in A accuracy at B (a fresh reading
    in both arms), so the decay splits into the A-gap shrinking (forgetting) and E changing (edge)."""
    rows = [(b, s) for b, s in zip(bs, stats) if s["EARLY"]["wald"] is not None and s["LATE"]["wald"] is not None]
    out = dict(held_pairs=len(rows))
    if len(rows) < MIN_BOTH:
        out["verdict"] = "UNANSWERABLE"
        return out
    arr = {k: np.array([s[k]["wald"] for _, s in rows]) for k in ("EARLY", "LATE")}   # pM, pF, rM, rF
    wts = boot_weights([b for b, _ in rows], np.random.default_rng(seed))

    def stats_from(mean):
        dE, dL = mean("EARLY", 0) - mean("EARLY", 1), mean("LATE", 0) - mean("LATE", 1)
        gE, gL = mean("EARLY", 2) - mean("EARLY", 3), mean("LATE", 2) - mean("LATE", 3)
        Dsub = dL - dE
        Dheld = dL * gE / gL - dE
        return dict(drop_EARLY=dE, drop_LATE=dL, gap_EARLY=gE, gap_LATE=gL, gap_change=gL - gE,
                    E_EARLY=dE / gE, E_LATE=dL / gL, D_sub=Dsub, D_held=Dheld, delta=Dheld - Dsub,
                    share_explained=(Dsub - Dheld) / Dsub)

    with np.errstate(divide="ignore", invalid="ignore"):
        point = stats_from(lambda k, i: float(arr[k][:, i].mean()))
        draws = stats_from(lambda k, i: wmean(wts, arr[k][:, i]))
    for k, v in point.items():
        out[k] = v
        out[k + "_ci"] = ci(np.asarray(draws[k], dtype=float))
    out["pM_pF_rM_rF"] = {k: [float(x) for x in arr[k].mean(axis=0)] for k in ("EARLY", "LATE")}
    if out["gap_EARLY_ci"][0] <= 0 or out["gap_LATE_ci"][0] <= 0:
        v = "UNRESOLVED-NO-A-GAP"
    elif out["D_sub_ci"][1] >= 0:
        v = "NO-DECAY-TO-SPLIT"
    elif out["share_explained"] >= 0.5 and out["delta_ci"][0] > 0:
        v = "MOSTLY-FORGETTING"
    elif out["D_held_ci"][1] < 0 and out["share_explained"] < 0.5:
        v = "EDGE-WEAKENS"
    else:
        v = "UNRESOLVED"
    out["verdict"] = v
    out["held_residual_excludes_0"] = bool(out["D_held_ci"][1] < 0 or out["D_held_ci"][0] > 0)
    return out


def arms(stats, bs, x, mkey, seed=0):
    """Both arms' absolute B accuracy by band, on pairs readable for drop x in EARLY and LATE."""
    rows = [(b, s) for b, s in zip(bs, stats) if s["EARLY"][x] is not None and s["LATE"][x] is not None]
    out = dict(pairs=len(rows), arm_m=mkey)
    if len(rows) < MIN_BOTH:
        out["label"] = "UNANSWERABLE"
        return out
    pm = {k: np.array([s[k][x][0] for _, s in rows]) for k in ("EARLY", "LATE")}
    pf = {k: np.array([s[k][x][1] for _, s in rows]) for k in ("EARLY", "LATE")}
    dM, dF = pm["LATE"] - pm["EARLY"], pf["LATE"] - pf["EARLY"]
    wts = boot_weights([b for b, _ in rows], np.random.default_rng(seed))
    bM, bF = wmean(wts, dM), wmean(wts, dF)
    D = float(dM.mean() - dF.mean())
    sM = float(dM.mean()) / D if D else float("nan")
    out.update(pM_EARLY=float(pm["EARLY"].mean()), pM_LATE=float(pm["LATE"].mean()),
               pF_EARLY=float(pf["EARLY"].mean()), pF_LATE=float(pf["LATE"].mean()),
               dM=float(dM.mean()), dM_ci=ci(bM), dF=float(dF.mean()), dF_ci=ci(bF), D=D,
               share_advantaged_falls=sM, share_disadvantaged_rises=1 - sM if D else float("nan"))
    if out["dM_ci"][1] < 0 and sM >= 0.5:
        out["label"] = "ADVANTAGED-FALLS"
    elif out["dF_ci"][0] > 0 and (1 - sM) >= 0.5:
        out["label"] = "DISADVANTAGED-RISES"
    else:
        out["label"] = "NEITHER-DOMINATES"
    return out


def _contrast(stats, bs, a, b, seed, q=(2.5, 97.5)):
    rows = [(bb, s) for bb, s in zip(bs, stats) if s["shape"][a] is not None and s["shape"][b] is not None]
    c = dict(frm=a, to=b, pairs=len(rows), sign=0)
    if len(rows) >= MIN_BOTH:
        d = np.array([(s["shape"][b][0] - s["shape"][b][1]) - (s["shape"][a][0] - s["shape"][a][1])
                      for _, s in rows])
        wts = boot_weights([bb for bb, _ in rows], np.random.default_rng(seed))
        v = wmean(wts, d)
        v = v[np.isfinite(v)]
        lo, hi = np.percentile(v, q)
        c.update(mean=float(d.mean()), ci=[float(lo), float(hi)])
        c["sign"] = 1 if lo > 0 else (-1 if hi < 0 else 0)
    return c


SIGN = {1: "+", -1: "-", 0: "0"}


def shape(stats, bs, seed=0):
    """2026-10-07 form: for each interior band k, rise = first band -> k and fall = k -> last band,
    with Bonferroni (3 interior bands) 98.33% intervals; adjacent contrasts reported, gating nothing."""
    names = [n for n, _, _ in SHAPE]
    first, last = names[0], names[-1]
    alpha = 0.05 / (len(names) - 2)
    q = (100 * alpha / 2, 100 * (1 - alpha / 2))
    interior = []
    for k, n in enumerate(names[1:-1], start=1):
        rise = _contrast(stats, bs, first, n, seed + 10 * k, q)
        fall = _contrast(stats, bs, n, last, seed + 10 * k + 1, q)
        interior.append(dict(band=n, rise=rise, fall=fall))
    end = _contrast(stats, bs, first, last, seed + 99)
    adjacent = [_contrast(stats, bs, names[k], names[k + 1], seed + k) for k in range(len(names) - 1)]
    if any(x["rise"]["sign"] == 1 and x["fall"]["sign"] == -1 for x in interior):
        v = "NON-MONOTONE"
    elif end["sign"] == -1 and not any(x["rise"]["sign"] == 1 for x in interior):
        v = "MONOTONE-DECREASING"
    else:
        v = ("OTHER(rises " + ",".join(SIGN[x["rise"]["sign"]] for x in interior)
             + "; first-to-last " + SIGN[end["sign"]] + ")")
    levels = {}
    for n in names:
        ds = [s["shape"][n][0] - s["shape"][n][1] for s in stats if s["shape"][n] is not None]
        levels[n] = dict(readable_pairs=len(ds), mean_drop=float(np.mean(ds)) if ds else None)
    return dict(verdict=v, interior=interior, first_to_last=end, adjacent=adjacent, levels=levels)


def positivity(stats):
    tot = {}
    for name, _, _ in BANDS:
        agg = defaultdict(int)
        for s in stats:
            for k, v in s[name]["n"].items():
                agg[k] += v
        for x in ("full", "sub", "held", "wald"):
            agg[f"readable_{x}"] = sum(1 for s in stats if s[name][x] is not None)
        tot[name] = dict(agg)
    return tot


def analyse(tl, idx, pairs, seed=0):
    stats = [pair_stats(cases(a, b, tl, idx)) for a, b in pairs]
    bs = [b for _, b in pairs]
    return dict(positivity=positivity(stats), primary=primary_wald(stats, bs, seed),
                single_reading=primary(stats, bs, seed),
                arms_full=arms(stats, bs, "full", "MASTERED", seed),
                arms_held=arms(stats, bs, "held", "MASTERED with R=1", seed),
                shape=shape(stats, bs, seed))


# ------------------------------------------------------------------ floor

SLIP, GUESS, LEARN, REVIEW, GATE = 0.10, 0.20, 0.30, 0.5, 0.30


def synth(world, seed, learners=3000, items=48, tau=10.0, peak=2.0):
    rnd = random.Random(seed)
    rows = []
    parent = {f"i{k}": f"i{k-1}" for k in range(1, items)}
    forget = world == "FORGET"

    def logit(p):
        return math.log(p / (1 - p))

    for u in range(learners):
        ability = rnd.gauss(0, 0.5)
        t = rnd.uniform(0, 30) * DAY
        held, last_t, first_t = {}, {}, {}

        def state(it, now):
            if held.get(it) and forget and rnd.random() > math.exp(-(now - last_t[it]) / DAY / tau):
                held[it] = False
            last_t[it] = now
            return held.get(it, False)

        def attempt(it, now, gate_loss=0.0):
            k = state(it, now)
            p = 1 / (1 + math.exp(-(logit(1 - SLIP if k else GUESS) + ability)))
            p = max(0.02, min(0.98, p - gate_loss))
            ok = rnd.random() < p
            if not k and rnd.random() < LEARN:
                held[it] = True
            first_t.setdefault(it, now)
            rows.append((f"u{u}", it, ok, now, False, False))

        def tick():
            nonlocal t
            t += (rnd.expovariate(1 / 0.01) if rnd.random() < 0.8 else rnd.expovariate(1 / 5.0)) * DAY

        order = [f"i{k}" for k in range(items)]
        rnd.shuffle(order)
        for it in order:
            par = parent.get(it)
            if par is not None and par in first_t and rnd.random() < REVIEW:
                tick()
                attempt(par, t)
            for n in range(rnd.randint(1, 3)):
                tick()
                loss = 0.0
                if n == 0 and par is not None and par in first_t and not state(par, t):
                    lag = (t - first_t[par]) / DAY
                    if world == "EDGE":
                        loss = GATE * math.exp(-lag / tau)
                    elif world == "HUMP":
                        loss = GATE * (lag / peak) * math.exp(1 - lag / peak)
                    else:
                        loss = GATE
                attempt(it, t, loss)
    return rows, [(a, b) for b, a in parent.items()]


def run_floor(learners=3000, out_name="floor.json"):
    results, ok = {}, True
    want = {"FORGET": "MOSTLY-FORGETTING", "EDGE": "EDGE-WEAKENS"}
    for world in ("FORGET", "EDGE", "NULL", "HUMP"):
        results[world] = []
        for s in range(3):
            rows, pairs = synth(world, seed=200 + s, learners=learners)
            tl, idx = build(rows)
            r = analyse(tl, idx, pairs, seed=s)
            p, sh = r["primary"], r["shape"]
            results[world].append(dict(primary=p, single_reading=r["single_reading"], shape=sh["verdict"],
                                       shape_detail=sh, arms_full=r["arms_full"]))
            print(f"   {world:6s} seed {s}: {p['verdict']:18s} pairs {p['held_pairs']:3d}  "
                  + (f"gap {p['gap_EARLY']:+.3f}->{p['gap_LATE']:+.3f}  D_sub {p['D_sub']:+.3f} {fmt(p['D_sub_ci'])}  "
                     f"D_held {p['D_held']:+.3f} {fmt(p['D_held_ci'])}  share {p['share_explained']:+.2f}"
                     if "D_sub" in p else "")
                  + f"  | single-reading {r['single_reading']['verdict']}"
                  + f"  | shape {sh['verdict']}  | arms {r['arms_full'].get('label')}", flush=True)
    split_ok = (all(x["primary"]["verdict"] == want["FORGET"] for x in results["FORGET"])
                and all(x["primary"]["verdict"] == want["EDGE"] for x in results["EDGE"])
                and not any(x["primary"]["verdict"] in want.values() for x in results["NULL"]))
    shape_ok = (all(x["shape"] == "NON-MONOTONE" for x in results["HUMP"])
                and not any(x["shape"] == "NON-MONOTONE" for w in ("FORGET", "EDGE") for x in results[w]))
    ok = split_ok and shape_ok
    print(f"   FLOOR split {'PASSES' if split_ok else 'FAILS'}; shape {'PASSES' if shape_ok else 'FAILS'}")
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / out_name).write_text(json.dumps(dict(split_passes=split_ok, shape_passes=shape_ok,
                                                             results=results), indent=1) + "\n")
    return ok


def fmt(c):
    return f"[{c[0]:+.3f}, {c[1]:+.3f}]"


# ------------------------------------------------------------------ real

def loaders():
    import atlas
    from build_matrix import LOADERS
    return {"assist": lambda: LOADERS["assist"](), "xes3g5m": lambda: atlas.xes3g5m_rows(),
            "ednet": lambda: atlas.ednet_rows(), "eedi": lambda: atlas.eedi_rows()}


def run_real(names):
    import atlas
    floor = json.loads((HERE / "out" / "floor.json").read_text())
    L = loaders()
    out_path = HERE / "out" / "lag_forgetting.json"
    res = json.loads(out_path.read_text())["corpora"] if out_path.exists() else {}
    for name in names:
        rows = ((u, i, ok, to_seconds(t), h1, h2) for u, i, ok, t, h1, h2 in L[name]())
        tl, idx = build(rows)
        items = sorted(idx)
        pairs = [(a, b) for a in items for b in items if a != b]
        rng = atlas.corpus_rng(name)
        if len(pairs) > MAX_PAIRS:
            pairs = [pairs[i] for i in rng.choice(len(pairs), MAX_PAIRS, replace=False)]
        r = analyse(tl, idx, pairs)
        if not floor["split_passes"]:
            r["primary"]["verdict_as_computed"] = r["primary"]["verdict"]
            r["primary"]["verdict"] = "UNANSWERABLE"
        if not floor["shape_passes"]:
            r["shape"]["verdict"] = "UNANSWERABLE"
        res[name] = dict(learners=len(tl), items=len(items), pairs=len(pairs), **r)
        del tl, idx
        write(res, floor, out_path)
        p = r["primary"]
        print(f"  {name:8s} learners {res[name]['learners']:,d} items {len(items)}  held pairs {p['held_pairs']}  "
              f"{p['verdict']}", flush=True)
        if "D_sub" in p:
            print(f"           gap {p['gap_EARLY']:+.4f} -> {p['gap_LATE']:+.4f}  D_sub {p['D_sub']:+.4f} {fmt(p['D_sub_ci'])}"
                  f"  D_held {p['D_held']:+.4f} {fmt(p['D_held_ci'])}  share {p['share_explained']:+.3f} "
                  f"{fmt(p['share_explained_ci'])}", flush=True)
        for k, v in r["positivity"].items():
            print(f"           {k:5s} {v}", flush=True)
        q = r["single_reading"]
        print(f"           single-reading (v1, failed floor) {q['verdict']} share {q.get('share_explained')}",
              flush=True)
        print(f"           arms(full) {r['arms_full'].get('label')}  arms(held) {r['arms_held'].get('label')}  "
              f"shape {r['shape']['verdict']}", flush=True)
        write(res, floor, out_path)
    write(res, floor, out_path, final=True)


def write(res, floor, out_path, final=False):
    vs = [v["primary"]["verdict"] for v in res.values()]
    nf, ne = vs.count("MOSTLY-FORGETTING"), vs.count("EDGE-WEAKENS")
    if nf >= 2 and ne == 0:
        overall = "LAG DECAY IS FORGETTING OF A"
    elif ne >= 2 and nf == 0:
        overall = "THE EDGE WEAKENS WITH LAG"
    elif nf and ne:
        overall = "CORPUS-DEPENDENT"
    else:
        overall = "UNRESOLVED"
    if final:
        print(f"\nPROGRAMME VERDICT: {overall}  (" + ", ".join(f"{k}: {v['primary']['verdict']}"
                                                         for k, v in res.items()) + ")")
    out_path.write_text(json.dumps(dict(window_days=W / DAY, bands_days=[b[1:] for b in BANDS],
                                        shape_bands_days=[b[1:] for b in SHAPE], min_cell=MIN_CELL,
                                        max_pairs=MAX_PAIRS, boot=BOOT,
                                        floor=dict(split_passes=floor["split_passes"],
                                                   shape_passes=floor["shape_passes"]),
                                        verdict=overall, corpora=res), indent=1, default=str) + "\n")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    if mode == "floor":
        sys.exit(0 if run_floor() else 1)
    if mode == "floor-diagnostic":
        # gates nothing: the same floor at 3x the learners, to say whether the failure is power
        run_floor(learners=9000, out_name="floor_diagnostic_9000.json")
        sys.exit(0)
    names = (sys.argv[sys.argv.index("--corpora") + 1].split(",") if "--corpora" in sys.argv else CORPORA)
    run_real(names)
