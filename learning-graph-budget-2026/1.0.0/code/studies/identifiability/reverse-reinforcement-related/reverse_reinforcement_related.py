"""
Reverse reinforcement on RELATED pairs (Eedi): when b is closely related to a, does meeting b between two
attempts at a raise a non-master's next answer on a, against a family-matched unrelated skill c?

THIS IS AN OBSERVATIONAL STUDY. Nobody assigned b or c; teachers set quizzes. Every contrast compares
learners who happened to meet b with matched learners who happened to meet c. A positive verdict says the
data behave as a reverse effect would, against the confounds the synthetic floor plants. It is not a causal
estimate.

WHY. `studies/identifiability/reverse-reinforcement/` (the PARENT) found NO REVERSE EFFECT on Eedi:
Delta -0.012 [-0.016, -0.007], S beyond a derangement -0.007 [-0.014, -0.002], margin 0.02. Its pairs were
lag-forgetting-v2's 2,700 count-readable subject pairs, a random sample, mostly unrelated (b shares a's
level-1 strand in 30% of them, a level-2 group in 2.7%). Backward transfer (Cosyn, Uzun, Doble & Matayoshi
2021, J. Math. Psych. 101, 102512; Hohensee, Melville, Collier & Ma 2025, JRME 56(2)) is plausibly confined
to closely related skills. The maintainer asked for the test on related pairs. This is it.

MACHINERY. The parent's code is imported, not changed: `reverse_reinforcement` (rr) supplies the subject
tree, the derangement (`rr.derange`), the strata, positivity mask, estimator (`rr.analyse`, `rr.Est`), the
verdict function, the size checks and the synthetic worlds (`rr.synth_world`), with every constant (strata
edges, MIN_XN = 30, MIN_CELL = 5, MIN_PAIRS = 30, MIN_T = 1,000, MIN_COVER = 0.5, BOOT = 1,000,
BOOT_FLOOR = 200, SEEDS = 40, DELTA_PLANT = 0.15 logit, GAMMA = 0.5, MARGIN = 0.02, PASS_N = 32). The one
piece re-written here is the case builder (`build_cases`), because the parent's is fused to its own pair
set; it is a line-for-line copy of the parent's loop taking (pairs, controls, b') as arguments. A
reproduction check guards the copy: for every parent pair whose control set is unchanged here, the real
set's T-case count must equal the parent's sealed skeleton's T count for that pair (outcome-free; arm only),
or the run stops. (K counts are not compared: the parent's loop admits a learner's intervals only if the
learner answered b or b' at some point, so K depends on b', which differs here. That inherited rule is kept.)

DATA. Eedi NeurIPS 2020 tasks 1-2 (research use, no redistribution), read exactly as the parent reads it
(`lag_forgetting_v2.load("eedi")` from $LDA_SCRATCH_DIR via $EEDI_ANSWERS / $EEDI_ZIP); the subject tree
from data.zip's `subject_metadata.csv` (`rr.subject_tree`). Unit = level-3 subject. The release keeps only
each learner's latest answer per question, at minute resolution (the parent's limitation, unrepairable).
Per-case arrays and the sealed outcomes stay in the scratchpad ($RRR_CACHE, default
<LDA_SCRATCH_DIR>/../reverse-reinforcement-related). Only aggregates are committed; subjects appear as
integer codes (index into the sorted subject list, the parent's coding).
Coherence Map: data/data-sources.json id `coherence-map`; the committed derivative
`studies/producers/pipeline/data/coherence-map.json` (757 standard -> standard `buildsTowards` edges; the
registry marks its edge direction "unverified", so the run asserts it: >= 90% of edges between graded
standards must run from a lower or equal grade to a higher or equal one, K = 0, or the run stops).
Eedi -> Common Core cluster map: `studies/identifiability/core-vs-culture/out/unit-map.json`, model
`openai/gpt-6-sol` (primary map; coded from the subject NAME only).

THE TWO RELATED-PAIR SETS (each analysed separately; fixed here before any case of these sets is built).
"Pair" is ordered: (a, b) with a the earlier skill, as in the parent. COUNT-READABLE is the parent's
population filter (v2's `wald_counts(cases(a, b))` >= 5 in each of four cells; it reads timing and a's
prior-mastery flag, never this study's outcome).
  (1) SAME STRAND, at two levels of Eedi's subject hierarchy:
      L1  TOP LEVEL. a and b share a level-1 strand (Number / Algebra / Geometry and Measure / Data ...).
          Pairs: the parent's 2,700 restricted to same level-1 (799 pairs, counted from the parent's
          committed out/skeleton.json pair codes and the subject tree; structural, no outcome).
          EXTENSION L1x, used only if L1 fails positivity or the floor (below): add count-readable
          same-level-1 ordered pairs not in the parent's set, drawn in a seeded random order
          (np.random.default_rng(20261009) over the sorted candidate list), keeping each that is
          count-readable, until the set holds 2,700 pairs.
      L2  FINER LEVEL. a and b share a level-2 group (62 groups over the 308 subjects). The parent's set
          holds 73 such pairs. Pairs: those 73 (L2r). EXTENSION L2x, used only if L2r fails positivity or
          the floor: every count-readable ordered same-level-2 pair (of 1,682 candidates). L2 is nested in
          L1 (a level-2 group sits in one level-1 strand), so L1 and L2 overlap; they are reported as two
          levels of one question, not two independent tests.
  (2) CM, CURATED BY COMMON CORE PROGRESSIONS. Cluster of a standard = its first three dot fields
      (3.NBT.A.1 -> 3.NBT.A; 1.NBT.B.2.a -> 1.NBT.B). A cluster edge A -> B exists if the Coherence Map
      holds a standard edge s -> t with cluster(s) = A, cluster(t) = B, A != B (direct, one step; no
      transitive closure; HS standards have no K-8 cluster and drop out). Pairs: every count-readable
      ordered Eedi subject pair (a, b) with map(a) -> map(b) a cluster edge, map(a) != map(b), neither
      NONE (1,429 candidates; 84 of them are in the parent's set, too few to restrict to, so the curated
      set is the full readable pool by design). THE CURATION IS MODEL-MAPPED: every subject's cluster
      was coded by gpt-6-sol from the subject's name; against a blind human coder (human:david-porcaro,
      core-vs-culture `human_codes.py`) kappa = 0.606 [0.493, 0.709] over 87 items of four corpora (Eedi
      alone 0.668, n = 24, raw agreement 0.71). The CM set inherits that error: roughly a third of
      subjects may sit in the wrong cluster or wrongly in or out of NONE, which dilutes the set with
      unrelated pairs and biases any real effect toward zero. 829 of the 1,429 candidates also share a's
      level-1 strand, so CM and L1 overlap; again two operationalisations of "related", not independent.

CONTROLS (the parent's rules, with "unrelated" made strict for related sets; fixed here).
  EXCLUSION SET X = the parent's 2,700 pairs, the set's own pairs, and every ordered subject pair whose
  clusters are linked by a CM cluster edge in either direction; X is made symmetric.
  CONTROL SET C(a, b): up to K_CTRL = 5 level-3 subjects c, not a or b, in a different level-1 strand from a,
  (a, c) not in X, |difficulty(c) - difficulty(b)| <= 0.05, the closest to b in difficulty, ties by code
  (difficulty = the subject's mean correctness over every answer). A pair with no such c is dropped.
  DERANGEMENT WITHIN THE RELATED SET: `rr.derange` over the set's own pairs (b-difficulty deciles computed
  over the set), seed 20261008, with the parent's validity rule except that b' must lie outside a's
  LEVEL-1 strand (the parent required only outside a's level-2 group) and (a, b') not in X. [Superseded by
  CHANGE 1 below: b' outside a's level-2 group, as in the parent.] So b' is a
  dependent skill of matched difficulty taken from another related pair, but unrelated to a: S = Delta -
  Delta_der isolates relatedness to a from "met a later topic". Pairs without a valid b' get none.
  SIZE OF THE CONTROLS (asserted per set, outcome-free, at positivity, with the parent's bounds and
  `shared.controls.check_control_scale`): weighted to T's strata, K's mean dose within [0.8, 1.25] x T's and
  K's mean log interval within 0.25 of T's; deranged T mean dose within [0.5, 2] x real; deranged matched-T
  count >= 0.5 x real. A set failing any bound is reported UNANSWERABLE (CONTROL SIZE) and not analysed.

UNIT, ARMS, STRATA, OUTCOME, ESTIMAND: the parent's, unchanged. Case = a non-master interval (two
consecutive a answers by a learner with no correct a answer up to t1); outcome y = correctness of the
answer at t2. T: >= 1 b answer strictly inside, no C answer; K: >= 1 C answer, no b answer. Exact strata
within pair (interval length 5 bands, attempt index 3, dose 3, other activity 2, ability-proxy quintile;
proxy = mean correctness over answers not at a, b, C, on >= 30 answers), plus a linear proxy adjustment
pooled within strata over K. ESTIMAND Delta = ATT of meeting b instead of c, T-weighted. Signed: Delta > 0
means meeting b raises the next a answer.
INTERVAL: 95% percentile, 1,000 draws RESAMPLING LEARNERS (multinomial over every learner with a matched case
in the real or deranged set), the unit whose exposure is selected; real and deranged share each draw, so S
has a joint interval.
POSITIVITY (outcome-free, per set): the parent's rule. Matched stratum >= 1 T and >= 1 K; usable pair >= 5 T
and >= 5 K in matched strata; ANSWERABLE if >= 30 usable pairs, >= 1,000 matched T, coverage >= 0.5, for both
the real and the deranged set; fine strata first, the parent's COARSE fallback second. A set that fails
both, after its registered extension where it has one, is UNANSWERABLE.
MARGIN 0.02 kept: it is a third of v2's +0.064 catch-up, the smallest effect that would matter to Paper II
5.1, and a related-pair effect smaller than that would not change its reading. Changing it after the
parent's result was known would be choosing a margin with the overall answer in view.

VERDICTS per set (the parent's `verdict`, first that applies; signed):
  UNANSWERABLE            positivity fails (after extension), control size fails, or the floor fails
  NO REVERSE EFFECT       Delta CI and S CI both inside (-0.02, +0.02) [tested first, as in the parent]
  PRACTISING B RAISES A   Delta CI > 0 and S CI > 0
  PRACTISING B LOWERS A   Delta CI < 0 and S CI < 0
  NOT B-SPECIFIC          Delta CI excludes 0 and S CI includes 0
  UNRESOLVED              otherwise
SUMMARY LINE (fixed here): "RELATED PAIRS: NO REVERSE EFFECT" if every answerable set reads NO REVERSE
EFFECT and at least one is answerable; "RELATED PAIRS: B RAISES A ON <sets>" if any set reads RAISES;
otherwise the per-set strings are listed. Three sets at 95% each, no family-wise correction: a single
RAISES is to be read with that in mind; the floor bounds a NULL world's directional rate per set.
SECONDARY (descriptive, gates nothing): the first-meeting subset per set; T and K means.

SYNTHETIC FLOOR (per analysed set, on that set's real outcome-free skeleton; `rr.synth_world` unchanged):
NULL, REV (+0.15 logit when b is in the interval), NEG (-0.15), ABILITY-B (meeting b selected on ability,
odds x1.65 per SD, no effect), ABILITY-ALL (the same in the deranged set); 40 seeds x 200 learner draws.
PASS: REV -> RAISES >= 32/40; NEG -> LOWERS >= 32/40; NULL -> NO REVERSE EFFECT >= 32/40 and RAISES or
LOWERS <= 2/40; ABILITY-B and ABILITY-ALL -> RAISES <= 2/40. A set failing its floor is UNANSWERABLE (or, for
L1 and L2r, triggers its extension, which then needs its own positivity and floor). The floor does not plant
selection the proxy cannot see (a teacher setting b to a class about to revisit a; on related pairs this is
MORE plausible than on random ones, since b and a are taught together) or learners sharing a items across
pairs beyond shared ability. A pass is necessary, not sufficient.

WHAT WAS NOT BLIND (stated before any case of these sets was built):
  - The parent's overall result (NO REVERSE EFFECT, Delta -0.012, S -0.007, sign negative) and its secondary
    subsets (first meeting; interval bands) are known to the author of this design.
  - The parent's committed out/ JSON was searched (keys and values) for any same-strand or curated-subset
    estimate. It holds none: the only strand-related values are STRUCTURAL shares in out/skeleton.json
    (b_same_level1_as_a 0.30, b_same_level2_as_a 0.027, bprime_same_level1_as_a), and its estimates are the
    whole set, the first-meeting subset and the five interval bands. floor_parts hold synthetic runs only.
  - L1 restricted is 799 of the parent's 2,700 pairs, so its cases are ~30% of a pool whose aggregate is
    known (Delta -0.012). That constrains, weakly, what L1 can show: a large positive L1 effect would have to
    be offset elsewhere in the parent. It does not reveal L1's value. The parent's per-case sealed files
    were not opened for any subset before this commit.
  - The structural counts above (799, 73, 1,682, 1,429, 84, 829, 62 groups) were computed before this
    design was written, from pair codes, the subject tree, the unit map and the Coherence Map. No case,
    count of cases or outcome of these sets had been computed.
  - The direction the maintainer expects (backward transfer on related pairs) is known.

CODED CONSTRUCTS: one. The CM set's subject -> cluster map is MODEL-CODED (openai/gpt-6-sol, core-vs-culture
invariance.py MAP_PROMPT, name only) and validated against an independent blind human coder (kappa above);
its edges are the Coherence Map's authored edges (Achieve the Core). Every other quantity is a count or mean
of logged answers.

    python3 reverse_reinforcement_related.py skeleton           (loads Eedi; pairs, controls, b', cases; y sealed)
    python3 reverse_reinforcement_related.py positivity         (outcome-free; strata, coverage, size asserts)
    python3 reverse_reinforcement_related.py floor --set S [--worlds W] [--seeds N]
    python3 reverse_reinforcement_related.py assemble --set S
    python3 reverse_reinforcement_related.py real               (opens the sealed y of the analysed sets)

CHANGES
  1. 2026-10-08, after the outcome-free skeleton and positivity of the registered design (commit cd2e62f),
     before any floor or outcome of these sets. Under the registered derangement (b' outside a's LEVEL-1
     strand) every set passed the count rule but FAILED the registered size bound on the deranged control:
     its matched-T count was 0.48 (L1), 0.21 (L2r), 0.24 (L2x) and 0.40 (CM) x the real set's (bound >= 0.5).
     Cause, structural: Eedi quizzes are topic-blocked, so a non-master's interval between two a answers
     holds a same-strand topic far more often than a topic from another strand, and a b' forced outside a's
     strand is rarely met. Under the registered rule every set is UNANSWERABLE (CONTROL SIZE); that result
     stays in out/positivity.json under "registered_strict_derangement" and in the README.
     Change: the derangement reverts to the PARENT'S validity rule: b' outside a's LEVEL-2 group, (a, b')
     not in X (symmetric, so b' is never CM-linked to a nor a parent pair), drawn within the related set's
     b-difficulty deciles. b' may now share a's level-1 strand. Consequence, stated before any outcome:
     for L2 and CM, S still separates the level-2 / Coherence-Map relation from "met a later topic of the
     same difficulty"; for L1 it does NOT isolate the strand relation (b' can be in a's strand), so an
     effect carried by the whole strand would show in Delta (b vs c, c always from another strand) but be
     partly removed from S; an L1 reading of NOT B-SPECIFIC is then the expected shape of a strand-level
     effect, and is reported as such. If a set fails the size bound under this rule too, it is
     UNANSWERABLE (CONTROL SIZE); there is no further change. The L1x / L2x extension rule is unchanged
     (it applies only to positivity or floor failures). Everything else is as registered.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PARENT = REPO / "studies/identifiability/reverse-reinforcement"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "studies/identifiability/lag-forgetting-v2"))
sys.path.insert(0, str(PARENT))

import reverse_reinforcement as rr  # noqa: E402
from shared.controls import check_control_scale  # noqa: E402

OUT = HERE / "out"
UNIT_MAP = REPO / "studies/identifiability/core-vs-culture/out/unit-map.json"
CMAP = REPO / "studies/producers/pipeline/data/coherence-map.json"
MAPPER = "openai/gpt-6-sol"
EXT_SEED = 20261009
L1X_TARGET = 2700
SETS = ["L1", "L1x", "L2r", "L2x", "CM"]
FAMILY = {"L1": ["L1", "L1x"], "L2": ["L2r", "L2x"], "CM": ["CM"]}


def cache_dir():
    d = os.environ.get("RRR_CACHE")
    p = Path(d) if d else Path(os.environ["LDA_SCRATCH_DIR"]).resolve().parent / "reverse-reinforcement-related"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ------------------------------------------------------------------ curation (outcome-free)

def cluster_of(code):
    return ".".join(code.split(".")[:3])


def grade(code):
    g = code.split(".")[0]
    return 0 if g == "K" else (int(g) if g.isdigit() else None)


def cm_cluster_edges():
    d = json.loads(CMAP.read_text())
    codes = d["codes"]
    graded = [(grade(codes[s]), grade(codes[t])) for s, t in d["edges"]
              if grade(codes[s]) is not None and grade(codes[t]) is not None]
    fwd = sum(gs <= gt for gs, gt in graded) / len(graded)
    assert fwd >= 0.9, f"Coherence Map edge direction: only {fwd:.3f} of graded edges run forward in grade"
    E = set()
    for s, t in d["edges"]:
        A, B = cluster_of(codes[s]), cluster_of(codes[t])
        if A != B and grade(codes[s]) is not None and grade(codes[t]) is not None:
            E.add((A, B))
    return E, dict(edges=len(d["edges"]), graded=len(graded), forward_share=fwd, cluster_edges=len(E))


def unit_map():
    return json.loads(UNIT_MAP.read_text())["maps"][MAPPER]["eedi"]


# ------------------------------------------------------------------ cases (copy of the parent's loop)

def build_cases(tl, idx, pairs, ctrl, bprime, lid, tot_c, tot_n, log=""):
    """The parent's case loop (rr.run_skeleton), unchanged, over a given (pairs, ctrl, b')."""
    import bisect  # noqa: F401  (rr.count_in uses it)
    count_in, bin_of = rr.count_in, rr.bin_of
    alltimes = {}

    def times_of(learner):
        v = alltimes.get(learner)
        if v is None:
            v = alltimes[learner] = np.sort(np.concatenate([np.frombuffer(r[0], dtype=np.float64)
                                                            for r in tl[learner].values()]))
        return v

    by_a = defaultdict(list)
    for p, (a, b) in enumerate(pairs):
        if ctrl[p]:
            by_a[a].append(p)
    cols = {s: defaultdict(list) for s in ("R", "D")}
    ys = {"R": [], "D": []}
    t0 = time.time()
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
                            first = rt[0][0] > t1
                        elif nc > 0 and nt == 0:
                            arm, dose = 0, nc
                            first = any(r[0][0] > t1 and r[0][0] < t2 for r in rC)
                        else:
                            continue
                        if lt is None:
                            lt = times_of(learner)
                        tot_in = int(np.searchsorted(lt, t2, "left") - np.searchsorted(lt, t1, "right"))
                        other = tot_in - nt - nc
                        ex = [a, excl] + list(C)
                        ec = sum(sum(d[x][1]) for x in set(ex) if x in d)
                        en = sum(len(d[x][1]) for x in set(ex) if x in d)
                        den = tot_n[L] - en
                        lag = (t2 - t1) / rr.DAY
                        c_ = cols[side]
                        c_["pair"].append(p)
                        c_["learner"].append(L)
                        c_["arm"].append(arm)
                        c_["lenb"].append(bin_of(lag, rr.LEN_EDGES))
                        c_["jb"].append(min(j, 2))
                        c_["dose"].append(dose)
                        c_["doseb"].append(bin_of(dose, rr.DOSE_EDGES))
                        c_["actb"].append(1 if other > rr.ACT_EDGE else 0)
                        c_["x"].append((tot_c[L] - ec) / den if den > 0 else np.nan)
                        c_["xn"].append(den)
                        c_["first"].append(bool(first))
                        c_["hasb"].append(nb > 0)
                        c_["loglen"].append(math.log(lag))
                        ys[side].append(oks[j + 1])
        if na % 50 == 0:
            print(f"    {log} a {na + 1}/{len(by_a)}  R {len(cols['R']['pair']):,d}  D {len(cols['D']['pair']):,d}"
                  f"  ({time.time() - t0:.0f} s)", flush=True)
    return cols, ys


DT = dict(pair=np.int32, learner=np.int32, arm=np.int8, lenb=np.int8, jb=np.int8, dose=np.int16,
          doseb=np.int8, actb=np.int8, x=np.float32, xn=np.int32, first=bool, hasb=bool, loglen=np.float32)


def save_set(name, cols, ys):
    cd = cache_dir() / name
    cd.mkdir(exist_ok=True)
    for side in ("R", "D"):
        np.savez(cd / f"skeleton_{side}.npz", **{k: np.array(v, dtype=DT[k]) for k, v in cols[side].items()})
        np.savez(cd / f"sealed_y_{side}.npz", y=np.array(ys[side], dtype=np.int8))


# ------------------------------------------------------------------ step 1: skeleton

def run_skeleton(only=None):
    import lag_forgetting_v2 as v2
    from lag_forgetting import MIN_CELL as V1_MIN_CELL, cases
    t0 = time.time()
    E, cm_info = cm_cluster_edges()
    um = unit_map()
    tl, idx = v2.load("eedi")
    print(f"  loaded {len(tl):,d} learners, {len(idx)} subjects ({time.time() - t0:.0f} s)", flush=True)
    items = sorted(idx)
    assert items == sorted(um), "unit map subjects differ from the loaded subjects"
    code = {it: k for k, it in enumerate(items)}
    psk = json.loads((PARENT / "out/skeleton.json").read_text())
    parent_pairs = [(items[a], items[b]) for a, b, _c, _x in psk["pairs_coded"]]
    assert len(parent_pairs) == 2700
    l2, l1 = rr.subject_tree()

    def readable(a, b):
        return min(v2.wald_counts(cases(a, b, tl, idx))) >= V1_MIN_CELL

    # the parent's pairs are readable by construction (the parent reproduced v2's set)
    cm_link = {(a, b) for a in items for b in items if a != b and um[a] != "NONE" and um[b] != "NONE"
               and um[a] != um[b] and (um[a], um[b]) in E}
    same1 = [(a, b) for a in items for b in items if a != b and l1[a] == l1[b]]
    same2 = [(a, b) for a, b in same1 if l2[a] == l2[b]]
    pset = set(parent_pairs)
    sets = {"L1": [p for p in parent_pairs if l1[p[0]] == l1[p[1]]],
            "L2r": [p for p in parent_pairs if l2[p[0]] == l2[p[1]]]}
    pool = dict(L1_candidates_all=len(same1), L2_candidates_all=len(same2), CM_candidates_all=len(cm_link),
                L1_restricted=len(sets["L1"]), L2_restricted=len(sets["L2r"]),
                CM_in_parent=len(cm_link & pset), CM_same_level1=sum(l1[a] == l1[b] for a, b in cm_link))
    print("  pools:", pool, flush=True)
    want = only or ["L1", "L2r", "L2x", "CM"]
    if "L2x" in want:
        sets["L2x"] = [p for p in same2 if p in pset or readable(*p)]
        print(f"  L2x readable: {len(sets['L2x'])} of {len(same2)} ({time.time() - t0:.0f} s)", flush=True)
    if "CM" in want:
        sets["CM"] = [p for p in sorted(cm_link) if p in pset or readable(*p)]
        print(f"  CM readable: {len(sets['CM'])} of {len(cm_link)} ({time.time() - t0:.0f} s)", flush=True)
    if "L1x" in want:
        cand = sorted(p for p in same1 if p not in pset)
        order = np.random.default_rng(EXT_SEED).permutation(len(cand))
        ext = list(sets["L1"])
        tried = 0
        for i in order:
            if len(ext) >= L1X_TARGET:
                break
            tried += 1
            if readable(*cand[i]):
                ext.append(cand[i])
        sets["L1x"] = ext
        pool["L1x_tried"] = tried
        print(f"  L1x: {len(ext)} pairs after {tried} tried ({time.time() - t0:.0f} s)", flush=True)

    # learners and difficulty, as the parent
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
    np.savez(cache_dir() / "learners.npz", tot_c=tot_c, tot_n=tot_n)

    meta_path = OUT / "skeleton.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    meta.update(dict(learners=len(tl), coherence_map=cm_info, mapper=MAPPER,
                     unit_map_none=sum(v == "NONE" for v in um.values())))
    meta.setdefault("pools", {}).update(pool)
    meta.setdefault("sets", {})
    cm_sym = cm_link | {(b, a) for a, b in cm_link}
    parent_ctrl = {(items[a], items[b]): tuple(items[c] for c in C) for a, b, C, _x in psk["pairs_coded"]}
    for name in want:
        pairs = sets[name]
        X = set(parent_pairs) | set(pairs) | cm_sym
        X = X | {(b, a) for a, b in X}
        ctrl = []
        for a, b in pairs:
            cand = [c for c in items if c not in (a, b) and l1.get(c) != l1.get(a) and (a, c) not in X
                    and abs(diff[c] - diff[b]) <= rr.DIFF_TOL]
            cand.sort(key=lambda c: (abs(diff[c] - diff[b]), code[c]))
            ctrl.append(tuple(cand[:rr.K_CTRL]))
        # CHANGE 1: the parent's validity rule (b' outside a's level-2 group), not level-1
        bprime = rr.derange(pairs, diff, l2, X, ctrl, np.random.default_rng(rr.DERANGE_SEED))
        for (a, b), x in zip(pairs, bprime):
            assert x is None or (l2[x] != l2[a] and (a, x) not in X)
        cols, ys = build_cases(tl, idx, pairs, ctrl, bprime, lid, tot_c, tot_n, log=name)
        # reproduction check of the copied loop against the parent's sealed skeleton (outcome-free)
        same_ctrl = [p for p, (pr, C) in enumerate(zip(pairs, ctrl)) if pr in parent_ctrl and parent_ctrl[pr] == C]
        repro = None
        if same_ctrl:
            pz = np.load(rr.cache_dir() / "skeleton_R.npz")
            pidx = {pr: k for k, pr in enumerate(parent_pairs)}
            # T-arm counts only: a T case needs a b answer and no C answer, so it does not depend on b';
            # K cases do (the parent's loop skips learners who answered neither b nor b'), and b' differs here.
            mp = np.array(cols["R"]["pair"], np.int64)
            mine = np.bincount(mp[np.array(cols["R"]["arm"]) == 1], minlength=len(pairs))
            theirs = np.bincount(pz["pair"].astype(np.int64)[pz["arm"] == 1], minlength=len(parent_pairs))
            bad = [p for p in same_ctrl if mine[p] != theirs[pidx[pairs[p]]]]
            repro = dict(pairs_checked=len(same_ctrl), mismatched=len(bad))
            assert not bad, f"{name}: copied case loop does not reproduce the parent on {len(bad)} pairs"
        save_set(name, cols, ys)
        meta["sets"][name] = dict(
            n_pairs=len(pairs), pairs_with_controls=sum(1 for c in ctrl if c),
            pairs_with_bprime=sum(1 for x in bprime if x),
            control_set_sizes=np.bincount([len(c) for c in ctrl], minlength=rr.K_CTRL + 1).tolist(),
            control_difficulty_gap_mean=float(np.mean([abs(diff[c] - diff[b]) for (a, b), C in zip(pairs, ctrl)
                                                        for c in C])) if any(ctrl) else None,
            b_same_level1=float(np.mean([l1[a] == l1[b] for a, b in pairs])),
            b_same_level2=float(np.mean([l2[a] == l2[b] for a, b in pairs])),
            b_cm_linked=float(np.mean([(a, b) in cm_link for a, b in pairs])),
            in_parent=sum(p in pset for p in pairs),
            bprime_same_level1=float(np.mean([l1[a] == l1[x] for (a, _b), x in zip(pairs, bprime) if x]))
            if any(bprime) else None,
            parent_reproduction=repro,
            cases_R=len(cols["R"]["pair"]), cases_D=len(cols["D"]["pair"]),
            pairs_coded=[[code[a], code[b], [code[c] for c in C], code[x] if x else None]
                         for (a, b), C, x in zip(pairs, ctrl, bprime)])
        print(f"  {name}: {len(pairs)} pairs, R {len(cols['R']['pair']):,d}, D {len(cols['D']['pair']):,d}, "
              f"repro {repro} ({time.time() - t0:.0f} s)", flush=True)
        OUT.mkdir(exist_ok=True)
        meta_path.write_text(json.dumps(meta) + "\n")


# ------------------------------------------------------------------ loading per set

def load_set(name, info=None):
    z = np.load(cache_dir() / name / "skeleton_R.npz")
    zd = np.load(cache_dir() / name / "skeleton_D.npz")
    out = []
    for side, zz in (("R", z), ("D", zd)):
        keep = zz["xn"] >= rr.MIN_XN
        if info is not None:
            info[side] = dict(cases=int(len(keep)), kept=int(keep.sum()), dropped_proxy_under_min=int((~keep).sum()))
        out.append(({k: zz[k][keep] for k in zz.files}, keep))
    return out


def learners():
    z = np.load(cache_dir() / "learners.npz")
    return z["tot_c"], z["tot_n"]


# ------------------------------------------------------------------ step 2: positivity and size

def positivity_one(name):
    pf = {}
    (R, _), (D, _) = load_set(name, pf)
    tc, tn = learners()
    full = tc[tn > 0] / tn[tn > 0]
    res, chosen = {}, None
    for scheme in ("fine", "coarse"):
        cuts = rr.quantile_cuts(full, 5 if scheme == "fine" else 3)
        stR, stD = rr.strata(R, R["x"], cuts, scheme), rr.strata(D, D["x"], cuts, scheme)
        mR, iR = rr.positivity_mask(R["arm"], stR, R["pair"].astype(np.int64), R["learner"])
        mD, iD = rr.positivity_mask(D["arm"], stD, D["pair"].astype(np.int64), D["learner"])
        ok = rr.answerable(iR) and rr.answerable(iD)
        res[scheme] = dict(real=iR, deranged=iD, answerable_real=rr.answerable(iR),
                           answerable_deranged=rr.answerable(iD))
        if ok:
            res[scheme].update(size_real=rr.size_checks(R, stR, mR), size_deranged=rr.size_checks(D, stD, mD))
            chosen = scheme
            break
    out = dict(scheme=chosen, schemes=res, proxy_filter=pf, answerable=chosen is not None)
    if chosen:
        sz, szd = res[chosen]["size_real"], res[chosen]["size_deranged"]
        ratio = sz["dose"]["K_weighted"] / sz["dose"]["T"]
        dlog = sz["loglen"]["K_weighted"] - sz["loglen"]["T"]
        der_ratio = szd["dose"]["T"] / sz["dose"]["T"]
        t_ratio = res[chosen]["deranged"]["matched_T"] / res[chosen]["real"]["matched_T"]
        reps, err = [], None
        try:
            reps.append(check_control_scale({"treatment_b_dose": sz["dose"]["T"],
                                             "control_c_dose": sz["dose"]["K_weighted"]}, ["control_c_dose"]))
            reps.append(check_control_scale({"treatment_b_dose": sz["dose"]["T"],
                                             "deranged_b_dose": szd["dose"]["T"]}, ["deranged_b_dose"]))
            reps.append(check_control_scale({"treatment_T_cases": res[chosen]["real"]["matched_T"],
                                             "deranged_T_cases": res[chosen]["deranged"]["matched_T"]},
                                            ["deranged_T_cases"]))
            assert 0.8 <= ratio <= 1.25, f"control dose ratio {ratio:.3f} outside [0.8, 1.25]"
            assert abs(dlog) <= 0.25, f"control log-length difference {dlog:+.3f} beyond 0.25"
            assert 0.5 <= der_ratio <= 2.0, f"deranged dose ratio {der_ratio:.3f} outside [0.5, 2]"
            assert t_ratio >= 0.5, "deranged T count below half the real"
        except AssertionError as e:
            err = str(e)
        out["size"] = dict(control_dose_ratio=ratio, control_loglen_diff=dlog, deranged_dose_ratio=der_ratio,
                           deranged_T_ratio=t_ratio, check_control_scale=[str(r) for r in reps],
                           passes=err is None, failure=err)
        if err:
            out["answerable"] = False
    return out


def run_positivity(names):
    path = OUT / "positivity.json"
    allp = json.loads(path.read_text()) if path.exists() else {}
    for name in names:
        allp[name] = positivity_one(name)
        p = allp[name]
        sch = p["scheme"]
        print(f"  {name}: scheme {sch}, answerable {p['answerable']}", flush=True)
        for s, r in p["schemes"].items():
            print(f"     {s}: real {r['real']}\n           der  {r['deranged']}", flush=True)
        if "size" in p:
            print("     size", {k: v for k, v in p["size"].items() if k != "check_control_scale"}, flush=True)
    path.write_text(json.dumps(allp, indent=1, default=str) + "\n")


# ------------------------------------------------------------------ step 3: floor

def run_floor(name, worlds, seeds):
    pos = json.loads((OUT / "positivity.json").read_text())[name]
    assert pos["answerable"], f"{name}: positivity or control size failed; no floor"
    scheme = pos["scheme"]
    (R, _), (D, _) = load_set(name)
    _tc, tn = learners()
    parts = OUT / "floor_parts" / name
    parts.mkdir(parents=True, exist_ok=True)
    q = 5 if scheme == "fine" else 3
    for world in worlds:
        rows, t0 = [], time.time()
        for s in range(seeds):
            rng = np.random.default_rng([20261008, rr.WORLDS.index(world), s])
            ((R2, xR, yR), (D2, xD, yD)), px = rr.synth_world(world, R, D, tn, rng)
            cuts = rr.quantile_cuts(px[tn > 0], q)
            r = rr.analyse(R2, D2, xR, xD, yR, yD, cuts, scheme, len(tn), rr.BOOT_FLOOR, rng)
            r.pop("masks", None)
            rows.append(r)
            print(f"    {name} {world:11s} seed {s:2d}  {r['verdict']:22s}  Delta {r.get('Delta', float('nan')):+.4f}"
                  f"  S {r.get('S', float('nan')):+.4f}  ({time.time() - t0:.0f} s)", flush=True)
        (parts / f"{world}.json").write_text(json.dumps(dict(world=world, seeds=seeds, rows=rows),
                                                        default=float) + "\n")
    assemble(name)


def assemble(name):
    parts = OUT / "floor_parts" / name
    got = {p.stem: json.loads(p.read_text()) for p in parts.glob("*.json")}
    if set(got) != set(rr.WORLDS):
        print(f"  {name}: floor parts present {sorted(got)}; not assembled", flush=True)
        return None
    tally = {}
    for w, g in got.items():
        vs = [r["verdict"] for r in g["rows"]]
        n = len(vs)
        tally[w] = {v: dict(k=vs.count(v), cp95=rr.clopper_pearson(vs.count(v), n)) for v in sorted(set(vs))}
        tally[w]["n"] = n
        for key in ("Delta", "S", "Delta_raw"):
            vals = [r[key] for r in g["rows"] if key in r]
            tally[w][f"{key}_mean"] = float(np.mean(vals)) if vals else None
        cis = [r["Delta_ci"][1] - r["Delta_ci"][0] for r in g["rows"] if "Delta_ci" in r]
        tally[w]["Delta_ci_width_mean"] = float(np.mean(cis)) if cis else None

    def k(w, v):
        return tally[w].get(v, {}).get("k", 0)

    R_, L_, N_ = "PRACTISING B RAISES A", "PRACTISING B LOWERS A", "NO REVERSE EFFECT"
    rules = {"REV -> RAISES >= 32": k("REV", R_) >= rr.PASS_N,
             "NEG -> LOWERS >= 32": k("NEG", L_) >= rr.PASS_N,
             "NULL -> NO REVERSE EFFECT >= 32": k("NULL", N_) >= rr.PASS_N,
             "NULL -> RAISES or LOWERS <= 2": k("NULL", R_) + k("NULL", L_) <= 2,
             "ABILITY-B -> RAISES <= 2": k("ABILITY-B", R_) <= 2,
             "ABILITY-ALL -> RAISES <= 2": k("ABILITY-ALL", R_) <= 2}
    passes = all(rules.values())
    path = OUT / "floor.json"
    allf = json.loads(path.read_text()) if path.exists() else {}
    allf[name] = dict(passes=passes, rules=rules, tally=tally, seeds=len(got["NULL"]["rows"]), boot=rr.BOOT_FLOOR,
                      planted=dict(delta_logit=rr.DELTA_PLANT, gamma=rr.GAMMA, theta_sd=rr.THETA_SD))
    path.write_text(json.dumps(allf, indent=1, default=float) + "\n")
    print(f"  {name}: floor passes {passes}", json.dumps(rules, indent=1))
    for w in rr.WORLDS:
        print(f"    {w:11s} " + ", ".join(f"{v}: {t['k']}" for v, t in tally[w].items() if isinstance(t, dict))
              + f"   mean Delta {tally[w]['Delta_mean']}  mean S {tally[w]['S_mean']}")
    return passes


# ------------------------------------------------------------------ step 4: real

def analysed_set(family, pos, floor):
    """The registered choice: the first member of the family to pass positivity, control size and floor."""
    for name in FAMILY[family]:
        if name in pos and pos[name]["answerable"] and floor.get(name, {}).get("passes"):
            return name
    return None


def run_real():
    pos = json.loads((OUT / "positivity.json").read_text())
    floor = json.loads((OUT / "floor.json").read_text())
    tc, tn = learners()
    full = tc[tn > 0] / tn[tn > 0]
    res = {}
    for family in FAMILY:
        name = analysed_set(family, pos, floor)
        if name is None:
            res[family] = dict(verdict="UNANSWERABLE", tried=[n for n in FAMILY[family] if n in pos])
            print(f"  {family}: UNANSWERABLE", flush=True)
            continue
        scheme = pos[name]["scheme"]
        (R, kR), (D, kD) = load_set(name)
        yR = np.load(cache_dir() / name / "sealed_y_R.npz")["y"][kR]
        yD = np.load(cache_dir() / name / "sealed_y_D.npz")["y"][kD]
        cuts = rr.quantile_cuts(full, 5 if scheme == "fine" else 3)
        r = rr.analyse(R, D, R["x"], D["x"], yR, yD, cuts, scheme, len(tc), rr.BOOT, np.random.default_rng(0))
        r.pop("masks", None)
        fR, fD = R["first"], D["first"]
        Rs, Ds = {k: v[fR] for k, v in R.items()}, {k: v[fD] for k, v in D.items()}
        sec = rr.analyse(Rs, Ds, Rs["x"], Ds["x"], yR[fR], yD[fD], cuts, scheme, len(tc), rr.BOOT,
                         np.random.default_rng(1))
        sec.pop("masks", None)
        res[family] = dict(set=name, scheme=scheme, primary=r, secondary_first_meeting=sec)
        print(f"  {family} ({name}): {r['verdict']}  Delta {r.get('Delta'):+.4f} {r.get('Delta_ci')}  "
              f"Delta_der {r.get('Delta_der'):+.4f} {r.get('Delta_der_ci')}  S {r.get('S'):+.4f} {r.get('S_ci')}",
              flush=True)
        print(f"     first meeting: {sec['verdict']}  Delta {sec.get('Delta')}  S {sec.get('S')}", flush=True)
    verdicts = {f: (v["primary"]["verdict"] if "primary" in v else v["verdict"]) for f, v in res.items()}
    ans = {f: v for f, v in verdicts.items() if v != "UNANSWERABLE"}
    raises = [f for f, v in ans.items() if v == "PRACTISING B RAISES A"]
    if raises:
        summary = "RELATED PAIRS: B RAISES A ON " + ", ".join(raises)
    elif ans and all(v == "NO REVERSE EFFECT" for v in ans.values()):
        summary = "RELATED PAIRS: NO REVERSE EFFECT"
    else:
        summary = "; ".join(f"{f}: {v}" for f, v in verdicts.items())
    out = dict(summary=summary, verdicts=verdicts, boot=rr.BOOT, boot_unit="learner (multinomial resampling)",
               margin=rr.MARGIN, sets=res)
    (OUT / "related.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(summary)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "positivity"
    arg = (lambda f: sys.argv[sys.argv.index(f) + 1] if f in sys.argv else None)
    if mode == "skeleton":
        run_skeleton(arg("--sets").split(",") if arg("--sets") else None)
    elif mode == "positivity":
        run_positivity(arg("--sets").split(",") if arg("--sets") else ["L1", "L2r", "L2x", "CM"])
    elif mode == "floor":
        ws = arg("--worlds").split(",") if arg("--worlds") else rr.WORLDS
        run_floor(arg("--set"), ws, int(arg("--seeds") or rr.SEEDS))
    elif mode == "assemble":
        assemble(arg("--set"))
    elif mode == "real":
        run_real()
    else:
        sys.exit(f"unknown mode {mode}")
