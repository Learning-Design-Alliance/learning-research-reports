"""
Reverse reinforcement on Eedi: does meeting the dependent b between two attempts at a raise a non-master's
next answer on a, against a family-matched unrelated skill c met in a comparable interval?

THIS IS AN OBSERVATIONAL STUDY. Nobody assigned b or c. Learners met them because a teacher set a quiz.
Every contrast below compares learners who happened to meet b with learners who happened to meet c, after
matching. A positive verdict says the data behave as a reverse effect would, against the confounds the
synthetic floor plants. It is not a causal estimate and does not rule out confounds the floor does not
plant.

WHY. `studies/identifiability/lag-forgetting-v2/` found that on Eedi the lag decay of the prerequisite drop
tracks non-masters of a catching up on a: their current A accuracy rises from EARLY to LATE by +0.064
[+0.056, +0.071], while past masters' does not fall. Paper II 5.1 names two readings: learning a elsewhere,
and selection of who returns. The second literature sweep
(`research/readiness/learning-graph-budget-2026/literature-sweep-2.md`, strand A: A.16 Cosyn, Uzun, Doble &
Matayoshi 2021, J. Math. Psych. 101, 102512, "the learning of related material can act as a type of
retrieval practice"; A.17 Hohensee, Melville, Collier & Ma 2025, JRME 56(2), backward transfer) adds a
third: working on b exercises a, so meeting b itself raises later accuracy on a. This study tests the third
reading on its own. It does not apportion v2's +0.064 among the three.

DATA. Eedi NeurIPS 2020 (tasks 1-2), research use, no redistribution, read through v1/v2's loader
(`atlas.eedi_rows` via `lag_forgetting.loaders()`, `lag_forgetting_v2.load`) from $LDA_SCRATCH_DIR
($EEDI_ANSWERS, $EEDI_ZIP). The subject tree (level-1/2/3) is read from data.zip's
`subject_metadata.csv`. Unit is the level-3 subject leaf; a question tagged with several leaves counts on
each. LIMITATION, unrepairable: the release keeps only each learner's LATEST answer to each question, at
minute resolution, so "attempts at a" are answers to different a-questions, and "between" is in
latest-answer order. Raw rows and every per-case array stay in the session scratchpad
($RR_CACHE, default <LDA_SCRATCH_DIR>/../reverse-reinforcement). Only aggregates are committed. Subjects
appear in out/ as integer codes only.

PAIR SET. The same Eedi pairs as lag-forgetting-v2: v1's 10,000 ordered subject pairs drawn by
`atlas.corpus_rng("eedi")`, kept if COUNT-READABLE (>= 5 Wald cases in each of v2's four cells; v2's
`wald_counts`, which reads no outcome). v2 reports 2,700 such pairs (`out/sizing.json`), a superset of its
2,692 held pairs. The regenerated set must reproduce v2's count and its B codes exactly, or the run stops.
"b is the dependent of a" means (a, b) is in this set: a was met before b by enough learners, and the pair
was readable. It is v2's pair set, not a curated prerequisite graph, and the README says so.

UNIT AND ARMS. A case is one NON-MASTER INTERVAL: a learner, a pair (a, b), and two consecutive answers at
a, at times t1 < t2, with no correct a answer up to and including t1. The OUTCOME y is the correctness of
the answer at t2 (the next attempt at a after the interval). A learner contributes every such interval up
to their first correct a answer.
  TREATMENT T: the learner answered >= 1 b question strictly inside (t1, t2), and no question of the
    control set C(a, b). Strictly inside, so a question tagged both a and b cannot count.
  CONTROL K: the learner answered >= 1 question of C(a, b) strictly inside (t1, t2), and no b question.
  Intervals with both, or neither, are not cases.
  CONTROL SET C(a, b), family-matched and unrelated, fixed before any outcome on a is read: the up to
    K_CTRL = 5 level-3 subjects c with (i) c not a or b, (ii) c in a different level-1 strand from a,
    (iii) (a, c) and (c, a) not in the pair set, chosen as the closest to b in DIFFICULTY (the subject's
    mean correctness over every answer in the corpus), with |difficulty(c) - difficulty(b)| <= 0.05;
    ties by code. A pair with no such c is dropped.
  MATCHING. Exact strata within each pair on: interval length (< 1 h, 1 h-1 d, 1-7 d, 7-30 d, >= 30 d);
    the index of the a attempt opening the interval (0, 1, >= 2); DOSE, the number of target answers in
    the interval (b answers for T, C answers for K: 1-2, 3-5, >= 6); other activity, the learner's answers
    in the interval at anything else (<= 10, > 10); and an ABILITY PROXY quintile. The proxy is the learner's
    mean correctness over all their answers except those at a, b and C(a, b). Quintile cut points come from
    every learner's whole-record mean. A case enters only if its proxy rests on >= MIN_XN = 30 answers,
    so that the proxy can carry the adjustment (outcome-free; the number dropped is reported). Within strata, the ability proxy is also adjusted linearly, with
    one slope beta pooled within strata over the K arm (below). The proxy uses answers before and after
    the interval. If meeting b raised accuracy elsewhere, the adjustment would pull toward zero
    (conservative); this is stated, not corrected.
  SIZE OF THE CONTROL (asserted, outcome-free, before the floor; `shared.controls.check_control_scale`
    and the bounds here). The treatment's size is the dose. Weighted to T's stratum mix, K's mean dose must
    be within 20% of T's (ratio in [0.8, 1.25]), and K's mean log interval length within 0.25 (natural
    log of days) of T's. The check fails the run, not the reading.

ESTIMAND. Delta = the ATT of meeting b instead of c on y, among non-masters of a. Per stratum s (on the
usable pairs and matched strata below), it is (ybar_T,s - ybar_K,s) - beta (xbar_T,s - xbar_K,s),
weighted by T's count n_T,s. beta is the within-stratum slope of y on the proxy x in K, pooled over
strata. Signed: Delta > 0 means meeting b raises the next a answer. The unadjusted stratified difference
(beta = 0) is reported beside it and gates nothing.
INTERVAL. 95% percentile interval from BOOT = 1,000 draws that RESAMPLE LEARNERS (multinomial weights over
every learner with a case in either the real or the deranged set). Treatment is per interval, but a
learner contributes many intervals and many pairs, and the learner is the unit whose exposure is
selected. Real and deranged estimates share each draw, so their difference has a joint interval.
Strata that lose an arm in a draw are dropped from that draw.

POSITIVITY (step 2; outcome-free; on counts only). A stratum is MATCHED if it holds >= 1 T and >= 1 K case.
A pair is USABLE if it has >= MIN_CELL = 5 T and >= 5 K cases in matched strata. COVERAGE is the share of
all T cases that sit in matched strata of usable pairs. The study is ANSWERABLE on positivity if there are
>= 30 usable pairs, >= 1,000 matched T cases, and coverage >= 0.5. If coverage < 0.5 under these strata,
one registered fallback is applied, still before any outcome: COARSE strata (pair, interval length,
dose, ability tercile; the attempt index and other activity are dropped, and the linear proxy adjustment
stays). If that also fails, the verdict is UNANSWERABLE. Which set was used is written to
out/positivity.json.

DERANGEMENT CONTROL (breaks the a-b link, keeps the structure). Each pair (a, b) is given b' = the b of
another pair in the same decile of b-difficulty (over the pair set). This is a seeded derangement of the
b's within deciles (seed 20261008), repaired by swaps, with b' not b, not a, not in C(a, b), not in a's
level-2 group, and (a, b') not in the pair set. Pairs that cannot be repaired get no b'. a, C(a, b), the
intervals, the strata, the proxy rule and the estimator are unchanged, and b' replaces b. This gives
Delta_der. A reverse effect specific to the a-b link predicts Delta > 0 and Delta_der near 0. Selection or
a generic "met a later topic" effect predicts both alike. SPECIFICITY S = Delta - Delta_der, with a joint
interval from the same draws. Size, asserted: the deranged T count >= 0.5 x the real T count, and the
deranged T mean dose within 0.5-2x of the real one (`check_control_scale`).

VERDICTS (fixed here; signed; first that applies; Eedi is the only corpus, there is no programme rule):
  UNANSWERABLE                 positivity fails (above), or the synthetic floor fails (below)
  NO REVERSE EFFECT            Delta CI and S CI both inside (-0.02, +0.02). MARGIN = 0.02 on the
                               probability scale is the smallest effect of interest: a third of v2's
                               +0.064 catch-up. It is tested FIRST, so an effect whose whole interval is
                               smaller than the margin reads NO REVERSE EFFECT even if it excludes 0; its
                               sign and size are printed beside the string. Why first: an observational
                               contrast on ~10^5 learners has an interval narrower than the selection bias
                               a noisy ability proxy leaves (found on a smoke test of the floor code on fake
                               data, before this design was committed or any Eedi outcome read: about
                               +0.009 under ABILITY-B), so "excludes 0" alone would turn residual selection
                               into a finding. The floor's ABILITY-B mean Delta is reported as the
                               instrument's selection-bias scale.
  PRACTISING B RAISES A        Delta CI entirely > 0 and S CI entirely > 0
  PRACTISING B LOWERS A        Delta CI entirely < 0 and S CI entirely < 0
  NOT B-SPECIFIC               Delta CI excludes 0 and S CI includes 0 (meeting b differs from meeting c,
                               but no more than meeting another pair's b does)
  UNRESOLVED                   otherwise
SECONDARY (descriptive, gates nothing): Delta on FIRST-MEETING cases only (the interval holds the learner's
first answer at b, or for K at the c met); per interval-length band; the T and K means.

SYNTHETIC FLOOR (step 3; before any real outcome). Shaped like Eedi by reusing the real OUTCOME-FREE
skeleton: the real cases' pairs, learners, arms, length, attempt index, dose and activity bins, and each
learner's real answer count, for the real set and the deranged set. Per seed, synthetic quantities are
drawn on that skeleton:
  ability theta_l ~ N(0, 0.8) per learner (shared by all of the learner's cases); a synthetic proxy
  x_l = Binomial(n_l, sigmoid(0.3 + theta_l)) / n_l, from the learner's real answer count n_l; ability
  quintile cut points from all learners' synthetic x.
  y ~ Bernoulli(sigmoid(alpha_p + kappa_p theta_l + 0.10 len + 0.10 min(j, 2) + 0.15 act + effect)) with
  alpha_p ~ N(logit 0.40, 0.5) and kappa_p ~ N(1, 0.3) per pair (the slope varies by pair), len the length
  bin index (catching up elsewhere grows with the interval), j the attempt-index bin and act the activity
  bin.
  Worlds:
    NULL         effect 0; arms as observed
    REV          +DELTA_PLANT = +0.15 logit (about +0.035 in probability) on every case whose interval
                 holds a b answer (T in the real set, and any deranged case whose interval holds b)
    NEG          -0.15 logit, the same cases (direction check)
    ABILITY-B    effect 0; the real set's arms are re-drawn by ability: P(T) = sigmoid(logit pi_s +
                 GAMMA z_l), with pi_s the observed T share in the case's stratum without the proxy, z_l =
                 theta_l / 0.8, GAMMA = 0.5 (odds of meeting b x1.65 per SD of ability). The deranged set is
                 left as observed. This is "ability drives both" aimed at b alone, so the derangement
                 cannot rescue it, and only the proxy adjustment can.
    ABILITY-ALL  as ABILITY-B, but the deranged set's arms are re-drawn the same way (ability drives meeting
                 any later topic)
  SEEDS = 40 per world, BOOT_FLOOR = 200 learner-resampling draws per seed (fewer than the real run's 1,000
  for time). The same estimator, strata and positivity masks are used (masks recomputed per seed on the
  synthetic arms and proxy).
  PASS RULE (all must hold; else every real verdict is UNANSWERABLE):
    REV         -> PRACTISING B RAISES A   in >= 32 of 40
    NEG         -> PRACTISING B LOWERS A   in >= 32 of 40
    NULL        -> NO REVERSE EFFECT       in >= 32 of 40, and RAISES or LOWERS in <= 2 of 40
    ABILITY-B   -> PRACTISING B RAISES A   in <= 2 of 40
    ABILITY-ALL -> PRACTISING B RAISES A   in <= 2 of 40
  Each rate is reported with its Clopper-Pearson 95% interval. What the floor does not plant: selection on
  something the proxy does not see (for example teachers who set b to classes about to revisit a), and
  learners sharing a items across pairs beyond the shared ability. A pass is necessary, not sufficient.

CODED CONSTRUCTS: none. Every quantity is a count of logged answers; difficulty and the proxy are means of
logged correctness.

    python3 reverse_reinforcement.py skeleton     (loads Eedi; pairs, controls, derangement, cases; y sealed)
    python3 reverse_reinforcement.py positivity   (outcome-free; strata, coverage, size assertions)
    python3 reverse_reinforcement.py floor [--worlds W1,W2] [--seeds N]
    python3 reverse_reinforcement.py real         (opens the sealed y)

CHANGES
(none yet)
"""

from __future__ import annotations

import bisect
import csv
import io
import json
import math
import os
import sys
import time
import zipfile
from collections import defaultdict
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402
import scipy.sparse as sp  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "studies/identifiability/lag-forgetting-v2"))

from shared.controls import check_control_scale  # noqa: E402

OUT = HERE / "out"
DAY, HOUR = 86400.0, 3600.0
K_CTRL, DIFF_TOL = 5, 0.05
LEN_EDGES = [1 / 24, 1.0, 7.0, 30.0]          # days -> 5 bins
DOSE_EDGES = [2, 5]                           # 1-2, 3-5, >=6 -> 3 bins
ACT_EDGE = 10                                 # <=10, >10 -> 2 bins
MIN_CELL, MIN_PAIRS, MIN_T, MIN_COVER = 5, 30, 1000, 0.5
MIN_XN = 30
MARGIN = 0.02
BOOT, BOOT_FLOOR, SEEDS = 1000, 200, 40
DELTA_PLANT, GAMMA, THETA_SD = 0.15, 0.5, 0.8
WORLDS = ["NULL", "REV", "NEG", "ABILITY-B", "ABILITY-ALL"]
DERANGE_SEED = 20261008
PASS_N = 32


def cache_dir():
    d = os.environ.get("RR_CACHE")
    if d:
        p = Path(d)
    else:
        p = Path(os.environ["LDA_SCRATCH_DIR"]).resolve().parent / "reverse-reinforcement"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ------------------------------------------------------------------ step 1: skeleton (Eedi)

def subject_tree():
    from shared.paths import data_path
    z = zipfile.ZipFile(data_path("EEDI_ZIP"))
    rows = list(csv.DictReader(io.TextIOWrapper(z.open("data/metadata/subject_metadata.csv"),
                                                encoding="utf-8-sig")))
    parent = {r["SubjectId"]: r["ParentId"] for r in rows}
    level = {r["SubjectId"]: int(r["Level"]) for r in rows}
    l2, l1 = {}, {}
    for s, lv in level.items():
        if lv == 3:
            p2 = parent[s]
            l2["s" + s] = p2
            l1["s" + s] = parent.get(p2)
    return l2, l1


def count_in(ts, lo, hi):
    """Answers strictly inside (lo, hi)."""
    return bisect.bisect_left(ts, hi) - bisect.bisect_right(ts, lo)


def bin_of(v, edges):
    return bisect.bisect_left(edges, v) if isinstance(edges[0], int) else bisect.bisect_right(edges, v)


def derange(pairs, diff, l2, pairset, ctrl, rng):
    """b' for each pair: another pair's b in the same b-difficulty decile, under the validity rule."""
    n = len(pairs)
    bd = np.array([diff[b] for _, b in pairs])
    dec = np.minimum((np.argsort(np.argsort(bd)) * 10) // n, 9)
    bprime = [None] * n

    def ok(i, bb):
        a, b = pairs[i]
        return (bb != b and bb != a and bb not in ctrl[i] and l2.get(bb) != l2.get(a)
                and (a, bb) not in pairset)

    for d in range(10):
        members = list(np.flatnonzero(dec == d))
        perm = list(rng.permutation(members))
        assign = {i: pairs[j][1] for i, j in zip(members, perm)}
        for _ in range(50):
            bad = [i for i in members if not ok(i, assign[i])]
            if not bad:
                break
            for i in bad:
                for _t in range(200):
                    k = members[rng.integers(len(members))]
                    if k != i and ok(i, assign[k]) and ok(k, assign[i]):
                        assign[i], assign[k] = assign[k], assign[i]
                        break
        for i in members:
            if ok(i, assign[i]):
                bprime[i] = assign[i]
    return bprime


def run_skeleton():
    import lag_forgetting_v2 as v2
    from lag_forgetting import MIN_CELL as V1_MIN_CELL, cases
    t0 = time.time()
    tl, idx = v2.load("eedi")
    print(f"  loaded {len(tl):,d} learners, {len(idx)} subjects ({time.time() - t0:.0f} s)", flush=True)
    items, pairs_all = v2.corpus_pairs("eedi", idx)
    code = {it: k for k, it in enumerate(items)}
    pairs = [(a, b) for a, b in pairs_all if min(v2.wald_counts(cases(a, b, tl, idx))) >= V1_MIN_CELL]
    sizing = json.loads((v2.OUT / "sizing.json").read_text())["corpora"]["eedi"]
    v2_b = sorted(c[0] for c in sizing["cells"])
    assert len(pairs) == sizing["count_readable_pairs"] == len(v2_b), (len(pairs), sizing["count_readable_pairs"])
    assert sorted(code[b] for _, b in pairs) == v2_b, "pair set does not reproduce v2's B codes"
    print(f"  pair set reproduces v2: {len(pairs):,d} count-readable pairs ({time.time() - t0:.0f} s)", flush=True)
    pairset = set(pairs)

    # learner index, totals, subject difficulty (mean correctness over every answer)
    lid, tot_c, tot_n = {}, [], []
    s_c, s_n = defaultdict(int), defaultdict(int)
    for k, (learner, d) in enumerate(tl.items()):
        lid[learner] = k
        c = n = 0
        for it, (ts, oks, _f) in d.items():
            ci_, ni_ = sum(oks), len(oks)
            c += ci_
            n += ni_
            s_c[it] += ci_
            s_n[it] += ni_
        tot_c.append(c)
        tot_n.append(n)
    tot_c, tot_n = np.array(tot_c, np.int64), np.array(tot_n, np.int64)
    diff = {it: s_c[it] / s_n[it] for it in items}

    l2, l1 = subject_tree()
    ctrl = []
    for a, b in pairs:
        cand = [c for c in items if c not in (a, b) and l1.get(c) != l1.get(a)
                and (a, c) not in pairset and (c, a) not in pairset and abs(diff[c] - diff[b]) <= DIFF_TOL]
        cand.sort(key=lambda c: (abs(diff[c] - diff[b]), code[c]))
        ctrl.append(tuple(cand[:K_CTRL]))
    bprime = derange(pairs, diff, l2, pairset, ctrl, np.random.default_rng(DERANGE_SEED))
    print(f"  controls: {sum(1 for c in ctrl if c)} pairs with >= 1 c; derangement: "
          f"{sum(1 for x in bprime if x)} pairs with b' ({time.time() - t0:.0f} s)", flush=True)

    alltimes = {}

    def times_of(learner):
        v = alltimes.get(learner)
        if v is None:
            v = alltimes[learner] = np.sort(np.concatenate([np.frombuffer(r[0], dtype=np.float64)
                                                            for r in tl[learner].values()]))
        return v

    # cases, grouped by a
    by_a = defaultdict(list)
    for p, (a, b) in enumerate(pairs):
        if ctrl[p]:
            by_a[a].append(p)
    cols = {s: defaultdict(list) for s in ("R", "D")}
    ys = {"R": [], "D": []}
    for na, (a, plist) in enumerate(sorted(by_a.items())):
        for learner, _t0, _ok in idx[a]:
            d = tl[learner]
            ts, oks, fpi = d[a]
            n = len(ts)
            kmax = (n - 1) if fpi is None else min(fpi, n - 1)
            if kmax < 1:
                continue
            ivs = [(j, ts[j], ts[j + 1]) for j in range(kmax) if ts[j + 1] > ts[j]]
            if not ivs:
                continue
            L = lid[learner]
            lt = None
            for p in plist:
                b, C, b2 = pairs[p][1], ctrl[p], bprime[p]
                rb, r2 = d.get(b), (d.get(b2) if b2 else None)
                rC = [d[c] for c in C if c in d]
                if not rC or (rb is None and r2 is None):
                    continue
                for j, t1, t2 in ivs:
                    nc = sum(count_in(r[0], t1, t2) for r in rC)
                    nb = count_in(rb[0], t1, t2) if rb is not None else 0
                    nb2 = count_in(r2[0], t1, t2) if r2 is not None else 0
                    for side, nt, rt, excl in (("R", nb, rb, b), ("D", nb2, r2, b2)):
                        if side == "D" and b2 is None:
                            continue
                        if nt > 0 and nc == 0:
                            arm, dose = 1, nt
                            first = rt[0][0] > t1        # learner's first answer at b inside the interval
                        elif nc > 0 and nt == 0:
                            arm, dose = 0, nc
                            first = any(r[0][0] > t1 and r[0][0] < t2 for r in rC)
                        else:
                            continue
                        if lt is None:
                            lt = times_of(learner)
                        tot_in = int(np.searchsorted(lt, t2, "left") - np.searchsorted(lt, t1, "right"))
                        other = tot_in - nt - nc     # answers in the interval at anything but the targets
                        ex = [a, excl] + list(C)
                        ec = sum(sum(d[x][1]) for x in set(ex) if x in d)
                        en = sum(len(d[x][1]) for x in set(ex) if x in d)
                        den = tot_n[L] - en
                        lag = (t2 - t1) / DAY
                        c_ = cols[side]
                        c_["pair"].append(p)
                        c_["learner"].append(L)
                        c_["arm"].append(arm)
                        c_["lenb"].append(bin_of(lag, LEN_EDGES))
                        c_["jb"].append(min(j, 2))
                        c_["dose"].append(dose)
                        c_["doseb"].append(bin_of(dose, DOSE_EDGES))
                        c_["actb"].append(1 if other > ACT_EDGE else 0)
                        c_["x"].append((tot_c[L] - ec) / den if den > 0 else np.nan)
                        c_["xn"].append(den)
                        c_["first"].append(bool(first))
                        c_["hasb"].append(nb > 0)
                        c_["loglen"].append(math.log(lag))
                        ys[side].append(oks[j + 1])
        if na % 25 == 0:
            print(f"    a {na + 1}/{len(by_a)}  R cases {len(cols['R']['pair']):,d}  D cases "
                  f"{len(cols['D']['pair']):,d}  ({time.time() - t0:.0f} s)", flush=True)
    cd = cache_dir()
    dt = dict(pair=np.int32, learner=np.int32, arm=np.int8, lenb=np.int8, jb=np.int8, dose=np.int16,
              doseb=np.int8, actb=np.int8, x=np.float32, xn=np.int32, first=bool, hasb=bool, loglen=np.float32)
    for side in ("R", "D"):
        np.savez(cd / f"skeleton_{side}.npz", **{k: np.array(v, dtype=dt[k]) for k, v in cols[side].items()})
        np.savez(cd / f"sealed_y_{side}.npz", y=np.array(ys[side], dtype=np.int8))
    np.savez(cd / "learners.npz", tot_c=tot_c, tot_n=tot_n)
    meta = dict(n_pairs=len(pairs), pairs_with_controls=sum(1 for c in ctrl if c),
                pairs_with_bprime=sum(1 for x in bprime if x),
                control_set_sizes=np.bincount([len(c) for c in ctrl], minlength=K_CTRL + 1).tolist(),
                control_difficulty_gap=dict(
                    mean=float(np.mean([abs(diff[c] - diff[b]) for (a, b), C in zip(pairs, ctrl) for c in C])),
                    max=float(max(abs(diff[c] - diff[b]) for (a, b), C in zip(pairs, ctrl) for c in C))),
                bprime_difficulty_gap_mean=float(np.mean([abs(diff[x] - diff[b]) for (a, b), x in
                                                          zip(pairs, bprime) if x])),
                b_same_level1_as_a=float(np.mean([l1.get(a) == l1.get(b) for a, b in pairs])),
                b_same_level2_as_a=float(np.mean([l2.get(a) == l2.get(b) for a, b in pairs])),
                bprime_same_level1_as_a=float(np.mean([l1.get(a) == l1.get(x) for (a, _b), x in
                                                       zip(pairs, bprime) if x])),
                learners=len(tl), cases_R=len(cols["R"]["pair"]), cases_D=len(cols["D"]["pair"]),
                pairs_coded=[[code[a], code[b], [code[c] for c in C], code[x] if x else None]
                             for (a, b), C, x in zip(pairs, ctrl, bprime)])
    OUT.mkdir(exist_ok=True)
    (OUT / "skeleton.json").write_text(json.dumps(meta) + "\n")
    print(f"  skeleton written ({time.time() - t0:.0f} s): R {meta['cases_R']:,d} cases, D {meta['cases_D']:,d}",
          flush=True)


# ------------------------------------------------------------------ strata, positivity, estimator

def load_skeleton(side, info=None):
    z = np.load(cache_dir() / f"skeleton_{side}.npz")
    keep = z["xn"] >= MIN_XN
    if info is not None:
        info[side] = dict(cases=int(len(keep)), kept=int(keep.sum()), dropped_proxy_under_min=int((~keep).sum()))
    return {k: z[k][keep] for k in z.files}, keep


def quantile_cuts(full_proxy, q):
    return np.quantile(full_proxy, np.arange(1, q) / q)


def strata(S, x, cuts, scheme):
    ab = np.searchsorted(cuts, np.nan_to_num(x, nan=0.5), side="right").astype(np.int64)
    p = S["pair"].astype(np.int64)
    if scheme == "fine":
        base = ((((p * 5 + S["lenb"]) * 3 + S["jb"]) * 3 + S["doseb"]) * 2 + S["actb"])
        return base * 5 + ab
    base = (p * 5 + S["lenb"]) * 3 + S["doseb"]
    return base * 3 + ab


def base_stratum(S):
    p = S["pair"].astype(np.int64)
    return ((((p * 5 + S["lenb"]) * 3 + S["jb"]) * 3 + S["doseb"]) * 2 + S["actb"])


def positivity_mask(arm, st, pair, learner):
    """matched strata (>=1 T and >=1 K) in usable pairs (>=MIN_CELL T and K in matched strata)."""
    u, inv = np.unique(st, return_inverse=True)
    nT = np.bincount(inv, weights=arm == 1, minlength=len(u))
    nK = np.bincount(inv, weights=arm == 0, minlength=len(u))
    matched = ((nT > 0) & (nK > 0))[inv]
    pT = np.bincount(pair[matched], weights=(arm[matched] == 1), minlength=pair.max() + 1)
    pK = np.bincount(pair[matched], weights=(arm[matched] == 0), minlength=pair.max() + 1)
    usable = (pT >= MIN_CELL) & (pK >= MIN_CELL)
    mask = matched & usable[pair]
    nt_all = int((arm == 1).sum())
    return mask, dict(T_cases=nt_all, K_cases=int((arm == 0).sum()), matched_T=int((mask & (arm == 1)).sum()),
                      matched_K=int((mask & (arm == 0)).sum()), usable_pairs=int(usable.sum()),
                      pairs_with_cases=int(len(np.unique(pair))),
                      coverage=float((mask & (arm == 1)).sum() / nt_all) if nt_all else 0.0,
                      learners=int(len(np.unique(learner[mask]))))



def answerable(info):
    return info["usable_pairs"] >= MIN_PAIRS and info["matched_T"] >= MIN_T and info["coverage"] >= MIN_COVER


class Est:
    """Stratified, proxy-adjusted ATT with learner-resampling draws. One instance per case set."""

    def __init__(self, arm, st, learner, x, y, mask, n_learners):
        arm, st, learner, x, y = arm[mask], st[mask], learner[mask], x[mask].astype(float), y[mask].astype(float)
        x = np.nan_to_num(x, nan=np.nanmean(x) if len(x) else 0.5)
        us, sinv = np.unique(st, return_inverse=True)
        self.ns = len(us)
        cell = sinv * 2 + arm.astype(np.int64)
        key = cell * n_learners + learner
        uk, kinv = np.unique(key, return_inverse=True)
        rows, colsl = uk // n_learners, uk % n_learners
        shape = (2 * self.ns, n_learners)

        def mat(v):
            return sp.csr_matrix((np.bincount(kinv, weights=v, minlength=len(uk)), (rows, colsl)), shape=shape)

        one = np.ones(len(y))
        self.M = [mat(one), mat(y), mat(x), mat(x * y), mat(x * x)]
        self.point = self._att([m @ np.ones((n_learners, 1)) for m in self.M])

    def _att(self, sums):
        n, sy, sx, sxy, sxx = [s.reshape(self.ns, 2, -1) for s in sums]
        nK, nT = n[:, 0], n[:, 1]
        with np.errstate(invalid="ignore", divide="ignore"):
            num = np.where(nK > 0, sxy[:, 0] - sx[:, 0] * sy[:, 0] / nK, 0).sum(0)
            den = np.where(nK > 0, sxx[:, 0] - sx[:, 0] ** 2 / nK, 0).sum(0)
            beta = num / den
            ok = (nK > 0) & (nT > 0)
            dy = sy[:, 1] / nT - sy[:, 0] / nK
            dx = sx[:, 1] / nT - sx[:, 0] / nK
            w = np.where(ok, nT, 0)
            adj = (w * np.where(ok, dy - beta * dx, 0)).sum(0) / w.sum(0)
            raw = (w * np.where(ok, dy, 0)).sum(0) / w.sum(0)
            mT = (w * np.where(ok, sy[:, 1] / nT, 0)).sum(0) / w.sum(0)
            mK = (w * np.where(ok, sy[:, 0] / nK, 0)).sum(0) / w.sum(0)
        return dict(adj=adj, raw=raw, beta=beta, mT=mT, mK=mK)

    def draws(self, W):
        return self._att([m @ W for m in self.M])


def boot_weights(n_learners, present, B, rng, chunk):
    """Multinomial learner-resampling weights over the learners present, in chunks of columns."""
    idx = np.flatnonzero(present)
    for s in range(0, B, chunk):
        c = min(chunk, B - s)
        counts = rng.multinomial(len(idx), np.full(len(idx), 1 / len(idx)), size=c).T
        W = np.zeros((n_learners, c))
        W[idx] = counts
        yield W


def ci(v):
    v = np.asarray(v)
    v = v[np.isfinite(v)]
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def verdict(d_ci, s_ci):
    if -MARGIN < d_ci[0] and d_ci[1] < MARGIN and -MARGIN < s_ci[0] and s_ci[1] < MARGIN:
        return "NO REVERSE EFFECT"
    if d_ci[0] > 0 and s_ci[0] > 0:
        return "PRACTISING B RAISES A"
    if d_ci[1] < 0 and s_ci[1] < 0:
        return "PRACTISING B LOWERS A"
    if (d_ci[0] > 0 or d_ci[1] < 0) and s_ci[0] <= 0 <= s_ci[1]:
        return "NOT B-SPECIFIC"
    return "UNRESOLVED"


def analyse(R, D, xR, xD, yR, yD, cuts, scheme, n_learners, B, rng, chunk=50, extra=False):
    stR, stD = strata(R, xR, cuts, scheme), strata(D, xD, cuts, scheme)
    mR, iR = positivity_mask(R["arm"], stR, R["pair"].astype(np.int64), R["learner"])
    mD, iD = positivity_mask(D["arm"], stD, D["pair"].astype(np.int64), D["learner"])
    if not answerable(iR) or not answerable(iD):
        return dict(verdict="UNANSWERABLE", positivity_R=iR, positivity_D=iD)
    eR = Est(R["arm"], stR, R["learner"], xR, yR, mR, n_learners)
    eD = Est(D["arm"], stD, D["learner"], xD, yD, mD, n_learners)
    present = np.zeros(n_learners, bool)
    present[R["learner"][mR]] = True
    present[D["learner"][mD]] = True
    dr, dd, rr, mt, mk = [], [], [], [], []
    for W in boot_weights(n_learners, present, B, rng, chunk):
        a, b = eR.draws(W), eD.draws(W)
        dr.append(a["adj"])
        dd.append(b["adj"])
        rr.append(a["raw"])
        mt.append(a["mT"])
        mk.append(a["mK"])
    dr, dd = np.concatenate(dr), np.concatenate(dd)
    d_ci, s_ci = ci(dr), ci(dr - dd)
    res = dict(verdict=verdict(d_ci, s_ci), Delta=float(eR.point["adj"][0]), Delta_ci=d_ci,
               Delta_der=float(eD.point["adj"][0]), Delta_der_ci=ci(dd),
               S=float(eR.point["adj"][0] - eD.point["adj"][0]), S_ci=s_ci,
               Delta_raw=float(eR.point["raw"][0]), Delta_raw_ci=ci(np.concatenate(rr)),
               beta=float(eR.point["beta"][0]), beta_der=float(eD.point["beta"][0]),
               mean_T=float(eR.point["mT"][0]), mean_T_ci=ci(np.concatenate(mt)),
               mean_K_weighted=float(eR.point["mK"][0]), mean_K_ci=ci(np.concatenate(mk)),
               positivity_R=iR, positivity_D=iD)
    if extra:
        res["masks"] = (mR, mD, stR, stD)
    return res


def full_proxy():
    z = np.load(cache_dir() / "learners.npz")
    tc, tn = z["tot_c"], z["tot_n"]
    return tc, tn


# ------------------------------------------------------------------ step 2: positivity and size

def size_checks(S, st, mask):
    """K's dose and log-length weighted to T's stratum mix, against T's."""
    arm = S["arm"][mask]
    s = st[mask]
    u, inv = np.unique(s, return_inverse=True)
    nT = np.bincount(inv, weights=arm == 1, minlength=len(u))
    nK = np.bincount(inv, weights=arm == 0, minlength=len(u))
    out = {}
    for key in ("dose", "loglen"):
        v = S[key][mask].astype(float)
        sT = np.bincount(inv, weights=v * (arm == 1), minlength=len(u))
        sK = np.bincount(inv, weights=v * (arm == 0), minlength=len(u))
        ok = (nT > 0) & (nK > 0)
        tmean = sT[ok].sum() / nT[ok].sum()
        kmean = (nT[ok] * sK[ok] / nK[ok]).sum() / nT[ok].sum()
        out[key] = dict(T=float(tmean), K_weighted=float(kmean), K_unweighted=float(v[arm == 0].mean()))
    return out


def run_positivity():
    proxy_filter = {}
    (R, _), (D, _) = load_skeleton("R", proxy_filter), load_skeleton("D", proxy_filter)
    tc, tn = full_proxy()
    n_learners = len(tc)
    full = tc[tn > 0] / tn[tn > 0]
    res = {}
    chosen = None
    for scheme in ("fine", "coarse"):
        q = 5 if scheme == "fine" else 3
        cuts = quantile_cuts(full, q)
        stR = strata(R, R["x"], cuts, scheme)
        mR, iR = positivity_mask(R["arm"], stR, R["pair"].astype(np.int64), R["learner"])
        stD = strata(D, D["x"], cuts, scheme)
        mD, iD = positivity_mask(D["arm"], stD, D["pair"].astype(np.int64), D["learner"])
        res[scheme] = dict(real=iR, deranged=iD, answerable_real=answerable(iR), answerable_deranged=answerable(iD),
                           size_real=size_checks(R, stR, mR), size_deranged=size_checks(D, stD, mD))
        print(f"  {scheme}: real {iR}\n          deranged {iD}", flush=True)
        if chosen is None and answerable(iR) and answerable(iD):
            chosen = scheme
            break
    out = dict(scheme=chosen, schemes=res, n_learners=n_learners, proxy_filter=proxy_filter, min_xn=MIN_XN,
               verdict_if_unanswerable=None if chosen else "UNANSWERABLE")
    if chosen:
        sz = res[chosen]["size_real"]
        szd = res[chosen]["size_deranged"]
        ratio = sz["dose"]["K_weighted"] / sz["dose"]["T"]
        dlog = sz["loglen"]["K_weighted"] - sz["loglen"]["T"]
        rep_c = check_control_scale({"treatment_b_dose": sz["dose"]["T"], "control_c_dose": sz["dose"]["K_weighted"]},
                                    ["control_c_dose"])
        rep_d = check_control_scale({"treatment_b_dose": sz["dose"]["T"], "deranged_b_dose": szd["dose"]["T"]},
                                    ["deranged_b_dose"])
        rep_n = check_control_scale({"treatment_T_cases": res[chosen]["real"]["matched_T"],
                                     "deranged_T_cases": res[chosen]["deranged"]["matched_T"]}, ["deranged_T_cases"])
        der_ratio = szd["dose"]["T"] / sz["dose"]["T"]
        out["size"] = dict(control_dose_ratio=ratio, control_loglen_diff=dlog, deranged_dose_ratio=der_ratio,
                           deranged_T_ratio=res[chosen]["deranged"]["matched_T"] / res[chosen]["real"]["matched_T"],
                           check_control_scale=[str(r) for r in (rep_c, rep_d, rep_n)])
        print("  size:", json.dumps(out["size"], indent=1), flush=True)
        assert 0.8 <= ratio <= 1.25, f"control dose ratio {ratio:.3f} outside [0.8, 1.25]"
        assert abs(dlog) <= 0.25, f"control log-length difference {dlog:+.3f} beyond 0.25"
        assert 0.5 <= der_ratio <= 2.0, f"deranged dose ratio {der_ratio:.3f} outside [0.5, 2]"
        assert out["size"]["deranged_T_ratio"] >= 0.5, "deranged T count below half the real"
        out["size"]["passes"] = True
    (OUT / "positivity.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(f"  positivity scheme: {chosen}", flush=True)


# ------------------------------------------------------------------ step 3: synthetic floor

def _sig(v):
    return 1 / (1 + np.exp(-v))


def synth_world(world, R, D, tn, rng):
    n_learners = len(tn)
    theta = rng.normal(0, THETA_SD, n_learners)
    px = rng.binomial(np.maximum(tn, 1), _sig(0.3 + theta)) / np.maximum(tn, 1)
    n_pairs = int(max(R["pair"].max(), D["pair"].max())) + 1
    alpha = rng.normal(math.log(0.4 / 0.6), 0.5, n_pairs)
    kappa = rng.normal(1.0, 0.3, n_pairs)
    z = theta / THETA_SD
    out = []
    for side, S in (("R", R), ("D", D)):
        arm = S["arm"].copy()
        if (world == "ABILITY-B" and side == "R") or (world == "ABILITY-ALL"):
            bs = base_stratum(S)
            u, inv = np.unique(bs, return_inverse=True)
            pi = np.bincount(inv, weights=arm == 1, minlength=len(u)) / np.bincount(inv, minlength=len(u))
            pi = np.clip(pi[inv], 0.02, 0.98)
            arm = (rng.random(len(arm)) < _sig(np.log(pi / (1 - pi)) + GAMMA * z[S["learner"]])).astype(np.int8)
        p = S["pair"]
        eta = (alpha[p] + kappa[p] * theta[S["learner"]] + 0.10 * S["lenb"] + 0.10 * S["jb"] + 0.15 * S["actb"])
        hasb = (arm == 1) if side == "R" else S["hasb"]
        if world == "REV":
            eta = eta + DELTA_PLANT * hasb
        elif world == "NEG":
            eta = eta - DELTA_PLANT * hasb
        y = (rng.random(len(eta)) < _sig(eta)).astype(np.int8)
        S2 = dict(S)
        S2["arm"] = arm
        out.append((S2, px[S["learner"]].astype(np.float32), y))
    return out, px


def clopper_pearson(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def run_floor(worlds, seeds):
    pos = json.loads((OUT / "positivity.json").read_text())
    scheme = pos["scheme"]
    assert scheme, "positivity failed; no floor is run"
    (R, _), (D, _) = load_skeleton("R"), load_skeleton("D")
    _tc, tn = full_proxy()
    parts = OUT / "floor_parts"
    parts.mkdir(parents=True, exist_ok=True)
    q = 5 if scheme == "fine" else 3
    for world in worlds:
        rows = []
        t0 = time.time()
        for s in range(seeds):
            rng = np.random.default_rng([20261008, WORLDS.index(world), s])
            ((R2, xR, yR), (D2, xD, yD)), px = synth_world(world, R, D, tn, rng)
            cuts = quantile_cuts(px[tn > 0], q)
            r = analyse(R2, D2, xR, xD, yR, yD, cuts, scheme, len(tn), BOOT_FLOOR, rng)
            r.pop("masks", None)
            rows.append(r)
            print(f"    {world:11s} seed {s:2d}  {r['verdict']:22s}  Delta {r.get('Delta', float('nan')):+.4f} "
                  f"{r.get('Delta_ci')}  S {r.get('S', float('nan')):+.4f} {r.get('S_ci')}  "
                  f"({time.time() - t0:.0f} s)", flush=True)
        (parts / f"{world}.json").write_text(json.dumps(dict(world=world, seeds=seeds, rows=rows), default=float) + "\n")
    assemble_floor()


def assemble_floor():
    parts = OUT / "floor_parts"
    got = {p.stem: json.loads(p.read_text()) for p in parts.glob("*.json")}
    if set(got) != set(WORLDS):
        print(f"  floor parts present: {sorted(got)}; not assembled", flush=True)
        return None
    tally = {}
    for w, g in got.items():
        vs = [r["verdict"] for r in g["rows"]]
        n = len(vs)
        tally[w] = {v: dict(k=vs.count(v), cp95=clopper_pearson(vs.count(v), n)) for v in sorted(set(vs))}
        tally[w]["n"] = n
        tally[w]["Delta_mean"] = float(np.mean([r["Delta"] for r in g["rows"] if "Delta" in r]))
        tally[w]["S_mean"] = float(np.mean([r["S"] for r in g["rows"] if "S" in r]))
        tally[w]["Delta_raw_mean"] = float(np.mean([r["Delta_raw"] for r in g["rows"] if "Delta_raw" in r]))

    def k(w, v):
        return tally[w].get(v, {}).get("k", 0)

    R_, L_, N_ = "PRACTISING B RAISES A", "PRACTISING B LOWERS A", "NO REVERSE EFFECT"
    rules = {"REV -> RAISES >= 32": k("REV", R_) >= PASS_N,
             "NEG -> LOWERS >= 32": k("NEG", L_) >= PASS_N,
             "NULL -> NO REVERSE EFFECT >= 32": k("NULL", N_) >= PASS_N,
             "NULL -> RAISES or LOWERS <= 2": k("NULL", R_) + k("NULL", L_) <= 2,
             "ABILITY-B -> RAISES <= 2": k("ABILITY-B", R_) <= 2,
             "ABILITY-ALL -> RAISES <= 2": k("ABILITY-ALL", R_) <= 2}
    passes = all(rules.values())
    (OUT / "floor.json").write_text(json.dumps(dict(passes=passes, rules=rules, tally=tally,
                                                    planted=dict(delta_logit=DELTA_PLANT, gamma=GAMMA,
                                                                 theta_sd=THETA_SD),
                                                    seeds=SEEDS, boot=BOOT_FLOOR,
                                                    runs={w: g["rows"] for w, g in got.items()}),
                                               indent=1, default=float) + "\n")
    print(json.dumps(dict(passes=passes, rules=rules), indent=1))
    for w in WORLDS:
        print(f"  {w:11s} " + ", ".join(f"{v}: {t['k']}" for v, t in tally[w].items() if isinstance(t, dict))
              + f"   mean Delta {tally[w]['Delta_mean']:+.4f}  mean S {tally[w]['S_mean']:+.4f}")
    return passes


# ------------------------------------------------------------------ step 4: real

def run_real():
    pos = json.loads((OUT / "positivity.json").read_text())
    floor = json.loads((OUT / "floor.json").read_text())
    scheme = pos["scheme"]
    (R, kR), (D, kD) = load_skeleton("R"), load_skeleton("D")
    yR = np.load(cache_dir() / "sealed_y_R.npz")["y"][kR]
    yD = np.load(cache_dir() / "sealed_y_D.npz")["y"][kD]
    tc, tn = full_proxy()
    full = tc[tn > 0] / tn[tn > 0]
    cuts = quantile_cuts(full, 5 if scheme == "fine" else 3)
    rng = np.random.default_rng(0)
    res = analyse(R, D, R["x"], D["x"], yR, yD, cuts, scheme, len(tc), BOOT, rng, extra=True)
    mR, mD, stR, stD = res.pop("masks")
    if not floor["passes"]:
        res["verdict_as_computed"] = res["verdict"]
        res["verdict"] = "UNANSWERABLE"
    # secondary, descriptive: first-meeting subset and per length band (same estimator, own masks, 1,000 draws)
    sec = {}
    subsets = {"first_meeting": (R["first"], D["first"])}
    for b_, lab in enumerate(["<1h", "1h-1d", "1-7d", "7-30d", ">=30d"]):
        subsets[f"length {lab}"] = (R["lenb"] == b_, D["lenb"] == b_)
    for name, (fR, fD) in subsets.items():
        Rs = {k: v[fR] for k, v in R.items()}
        Ds = {k: v[fD] for k, v in D.items()}
        r = analyse(Rs, Ds, Rs["x"], Ds["x"], yR[fR], yD[fD], cuts, scheme, len(tc), BOOT,
                    np.random.default_rng(1))
        r.pop("masks", None)
        sec[name] = r
        print(f"  secondary {name:16s} {r['verdict']:22s} Delta {r.get('Delta', float('nan')):+.4f} "
              f"{r.get('Delta_ci')}  S {r.get('S', float('nan')):+.4f} {r.get('S_ci')}", flush=True)
    out = dict(scheme=scheme, boot=BOOT, boot_unit="learner (multinomial resampling)", margin=MARGIN,
               floor_passes=floor["passes"], primary=res, secondary=sec)
    (OUT / "reverse_reinforcement.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("positivity")}, indent=1, default=float))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "positivity"
    if mode == "skeleton":
        run_skeleton()
    elif mode == "positivity":
        run_positivity()
    elif mode == "floor":
        ws = sys.argv[sys.argv.index("--worlds") + 1].split(",") if "--worlds" in sys.argv else WORLDS
        n = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else SEEDS
        run_floor(ws, n)
    elif mode == "assemble":
        assemble_floor()
    elif mode == "real":
        run_real()
    else:
        sys.exit(f"unknown mode {mode}")
