"""HOLON-1: is the course-level graph the projection of the concept-level graph?

Proposed by the maintainer 2026-10-07. Pre-registration; this docstring was committed before any
number computed on learner records was read.

QUESTION. A "holonic" graph lets an edge be asserted at course level while the concept edges inside
the two courses stay unknown, and summarizes the lower level upward by a projection rule. The
programme's zoom result (studies/workforce/graphex/zoom.py) says the rule is: store the reachability
closure, render the transitive reduction, and measure how much contraction manufactures. If the
course graph that learners identify EQUALS the projection of the concept graph, claims can sit at
whichever level identifies them. If it does not, the levels carry independent information and a
course edge cannot be read off concept edges (or the reverse).

DATA (reads a corpus: MOOCCubeX, research use, no redistribution; $MOOCCUBEX_DIR via
shared.paths.data_path). Nothing learner-level and no concept text is written to out/.

  concept graph   prerequisites/{cs,psy,math}.json. ground_truth 1 on (c1, c2) = c1 is the
                  prerequisite of c2. CODER: human annotators ("experienced annotators", Yu et al.,
                  CIKM 2021), labelling candidate pairs that a MODEL ranked (text model + graph model;
                  the graph model uses each course's own video order). Labelled pairs are therefore
                  neither a random sample of concept pairs nor independent of within-course order.
                  Unlabelled candidates (ground_truth -1) are not used. Positives only form the graph.
  concept->course relations/concept-course.txt, `K_{name}_{field}` TAB course id. CODER: a MODEL. The
                  concepts were extracted from each course's video captions by an NER model and then
                  refined by an unstated process (MOOCCubeX docs/concept-en.md). No human reference
                  for this membership exists in this repository. A concept from a prerequisite file
                  is joined to the concept-course map by name within its own field only
                  (cs = 计算机科学与技术, psy = 心理学, math = 数学), so a homonym in another field does
                  not join.
  learner order   entities/user.json, streamed (807 MB, never stored) through the existing ingest
                  data/ingest/mooccubex/stream_user.py, which discards name, gender, year_of_birth
                  and school at the door and keeps pseudonymous id, course sequence and enrolment
                  times, restricted to the courses the projection touches. Output:
                  $LDA_SCRATCH_DIR/derived-holon-projection/user-order.jsonl. Generator:
                      python3 holon.py --write-courses        (writes courses.txt there)
                      curl -sSL https://lfs.aminer.cn/misc/moocdata/data/mooccube2/entities/user.json \\
                        | python3 data/ingest/mooccubex/stream_user.py <derived>/courses.txt \\
                          <derived>/user-order.jsonl
  general factor  relations/user-problem.json (22 GB) STREAMED, never stored, through
                  ability_ingest.py in this directory, which writes one line per learner:
                  id, problems answered, problems correct (<derived>/ability.tsv). Generator:
                      curl -sSL https://lfs.aminer.cn/misc/moocdata/data/mooccube2/relations/user-problem.json \\
                        | python3 ability_ingest.py <derived>/ability.tsv
                  Fallback, registered now: if fewer than 20% of the order learners join to a
                  learner with >= 20 answered problems, ability is dropped from the family key and
                  the README says so.

STEP 0, FEASIBILITY (metadata only, run before this design). Labels exist: cs 725 / psy 831 /
math 761 positives. Joined within field to the concept-course map, 483 / 632 / 240 positive pairs
have both concepts placed in at least one course; the literal course quotient touches 166 courses.
user-problem.json is not needed for the course graph itself, only for the general factor.

THE PROJECTIONS (computed from the concept graph alone).

  P_lit   literal quotient, the brief's rule: course X -> Y iff some concept placed in X is a labelled
          prerequisite of some concept placed in Y (X != Y). Concept membership is many-to-many, so
          this is not a contraction of a partition; it is the image of the concept relation.
  P_red   PRIMARY. Transitive reduction of P_lit's closure, by zoom.reduction (mutually reachable
          pairs excluded: inside a strongly connected class "immediate" has no meaning).
  P_clo   comparison: the closure of P_lit, directed pairs only (mutual pairs carry no direction).
  P_net   secondary, registered because the metadata showed P_lit is mostly one cyclic class:
          X -> Y iff the number of concept edges from X into Y exceeds the number from Y into X;
          P_netred is its transitive reduction. These are the "majority flow" reading.

  Metadata seen before this commit, and the reason P_net exists: P_lit is 5,485 course edges; its
  closure is 12,698 ordered pairs of which most are mutual, and P_red is 510 edges, all in cs (psy
  and math reduce to nothing, every course in one class). That is zoom.py's "contraction manufactures
  reachability" at full strength, and it is itself part of the answer: under the literal rule the
  projection is defined for one domain only.

THE IDENTIFIED COURSE GRAPH (learners), CONTROLLING THE CATALOGUE.

  For an ordered pair (a, b), the real share s(a->b) = of learners enrolled in both, the share who
  enrolled in a first (ties dropped), as course_order_derangement.py. The catalogue control is that
  study's donor derangement: a DONOR's enrolment time for a is compared with the learner's OWN time
  for b, d(a->b), which keeps every course's enrolment-time distribution and destroys within-learner
  sequencing. FAMILY-MATCHED: donors are drawn only from the learner's family, a derangement (no
  fixed points) within each family; singletons are dropped from both arms. Family =
      breadth stratum (courses enrolled among the universe: 2, 3, 4-5, 6+)
    x cohort (calendar quarter of the learner's first enrolment, so donor and learner share a start
      date and the start offset does not leak catalogue order into the real-minus-deranged gap)
    x general factor (tertile of share correct over >= 20 answered problems; "unmeasured" otherwise),
  which is the conditioning on a general learner factor the literature asks for (Krause-Levy et al.
  2020, literature.md 3.21; Kaur et al. 2019, 1.18; synthesis item 7). The order statistic has no
  outcome for ability to confound directly; what the factor removes is any catalogue-timing
  difference between learners of different general standing (strong learners joining early, taking
  advanced courses at a different point in the catalogue).

  The deranged arm is averaged over R derangements (counts summed). Excess e(a->b) = s(a->b) -
  d(a->b), antisymmetrized: E(a, b) = (e(a->b) - e(b->a)) / 2, so E(b, a) = -E(a, b) exactly and a
  reversed projection scores exactly -D (asserted in code). A pair is READ when the real cell and
  both deranged cells hold >= MIN_CELL = 30 learners. The unit the treatment is assigned to is the
  learner, so every resample and every split is over learners.

THE AGREEMENT STATISTIC (signed).

  D(P) = mean of E(x, y) over the edges (x, y) of projection P whose pair is read. Positive D means
  learners take the projected prerequisite course first more often than the catalogue alone
  produces. Its controls:
    deranged projection   relabel the projection's courses by a derangement within domain (a
                          course's domain is the field contributing most of its labelled-edge
                          endpoints), 2,000 draws. The relabelled graph is isomorphic to P: the same
                          edge count, degrees and depth. It is sized like the treatment by
                          construction. p = (1 + #{D_null >= D}) / (1 + draws), one-sided, signed.
    learner bootstrap     B = 30 resamples of learners, each with fresh family derangements, for a
                          95% percentile interval on D (30, not 2,000, because each draw re-derives
                          every pair; stated rather than hidden).
    raw order             D computed on 2*s - 1 with no catalogue control, reported to show what the
                          catalogue trap would have said. Never used for a verdict.
  Concordance: among P's read edges with |E| >= TAU = 0.05, the share with E > 0.
  Kappa (secondary): three-class call per read pair, projection {x->y, y->x, none} against
  identified {E >= TAU, E <= -TAU, else none}, Cohen's kappa (shared.stats.kappa_nominal), with the
  same deranged-projection null.
  Catalogue test: split-half reliability of E over read pairs (learners split in halves, 6 splits,
  mean Spearman). If the learner-imposed excess is not reproducible, there is no course graph beyond
  the catalogue to compare the projection with.

VERDICTS (pre-registered, on P_red; the same rule is reported for P_clo, P_net, P_netred):

  UNANSWERABLE        the synthetic floor fails; or fewer than MIN_EDGES = 30 P_red edges are read.
  CATALOGUE ONLY      split-half reliability of E < REL_MIN = 0.20: course order is not
                      distinguishable from the deranged catalogue.
  PROJECTION HOLDS    D > 0, deranged-projection p < 0.05, bootstrap lower bound > 0, AND concordance
                      >= 0.75 over at least 10 edges with |E| >= TAU.
  PROJECTION PARTIAL  (added to the brief's four, because "significant but weak" is neither "holds"
                      nor "independent") D > 0, p < 0.05, lower bound > 0, concordance < 0.75 or
                      fewer than 10 decided edges: the levels share direction, the projection does
                      not reproduce the course graph.
  LEVELS INDEPENDENT  otherwise: course excess is reproducible but the projection does not predict
                      its sign beyond a relabelled graph of the same shape. If D < 0 with p_low < 0.05
                      and the upper bound < 0, the string is "LEVELS INDEPENDENT (REVERSED)": the
                      projection points against learner order. Direction is checked, not |D|.

  CLAUDE.md BINDS THIS VERDICT AS DESCRIPTIVE. The concept-course membership is model-extracted with
  no human reference, so the projection is a model-coded construct and cannot gate anything. The
  verdict is reported with that qualifier and the history entry moves nothing on its strength.

SYNTHETIC DETECTION FLOOR (worlds built from the real projection; learner marginals are synthetic
before the design commit, and the BINDING floor after it reuses the real marginals only: number of
learners, course popularity, breadth distribution, each course's enrolment-date distribution).
  W_proj  course order IS the reduction: a share BETA = 0.3 of learners enrol in their courses in a
          topological order of P_red (depth + noise < 1); catalogue open dates are shuffled across
          courses, so not aligned with the projection. Expect PROJECTION HOLDS.
  W_cat   catalogue only, adversarial: no learner orders anything, but course open dates are
          assigned in P_red's topological order, so raw order agrees with the projection. Expect
          CATALOGUE ONLY (LEVELS INDEPENDENT tolerated); PROJECTION HOLDS or PARTIAL is a FAIL.
  W_ind   independent levels: as W_proj but learners follow the topological order of a relabelled
          (deranged) P_red. Expect LEVELS INDEPENDENT; HOLDS or PARTIAL is a FAIL.
  Three seeds per world. Floor passes iff W_proj is HOLDS in 3/3, W_cat is never HOLDS/PARTIAL and
  W_ind is never HOLDS/PARTIAL. BETA in {0.1, 0.2} is reported as sensitivity, not as a gate. The
  checks are written and scored by the same reader (this script), so the floor is a planted-effect
  floor on a known truth, not an independent validation.

CHANGES 2026-10-07, after the first synthetic floor (out/floor-synthetic-v1.json) and BEFORE any
real-data statistic was computed. The first floor FAILED: W_proj read PROJECTION HOLDS in 1 of 3
seeds, and, worse, W_cat's D was positive and "significant" against the relabelled-projection null
in all three seeds (D +0.030, +0.022, +0.012; p 0.002, 0.002, 0.028). Only the reliability test
(split-half 0.05 to 0.10 < 0.20) kept W_cat from reading as projection holding, which is one
threshold away from the catalogue trap. The cause is the start-date leak foreseen above: a donor
from the same calendar QUARTER starts up to 91 days apart, so the deranged arm is blurred relative
to the real one and catalogue order survives into E with the catalogue's sign. Two changes, made
once, with the thresholds, BETA and the verdict rules untouched:
  (a) cohort is the WEEK of first enrolment, not the quarter;
  (b) E is residualized on the signed catalogue gap (each course's median enrolment date), by an odd
      binned mean over all read pairs (residualize()). This is conservative where the projection
      happens to align with catalogue timing: agreement that coincides with when courses are
      generally taken is not credited. D before (b) is reported beside D as D_derangement_only.
The floor is then re-run once on synthetic marginals and once, binding, on the real marginals. If it
fails again the verdict is UNANSWERABLE; no further change.

WHAT IT CAN AND CANNOT SAY. It can say whether learner-imposed course order, beyond the catalogue
and within a general factor, follows the direction the concept graph projects. It cannot say the
course edge is a dependency: order is a choice, not a performance effect, and a positive D could be
learners following course titles or advice that also shaped the annotators' concept labels. It
cannot validate the concept-course map. A null is a null on order, not on performance.

    python3 holon.py --write-courses
    python3 holon.py --floor [--shape synthetic|real]
    python3 holon.py --real
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies/workforce/graphex"))

from shared.paths import data_path, scratch_root  # noqa: E402
from shared.stats import kappa_nominal, spearman  # noqa: E402
from zoom import reachability, reduction  # noqa: E402

SEED = 20261007
FIELDS = {"cs": "计算机科学与技术", "psy": "心理学", "math": "数学"}
MIN_CELL = 30
MIN_EDGES = 30
TAU = 0.05
REL_MIN = 0.20
CONC_MIN = 0.75
MIN_DECIDED = 10
NULL_DRAWS = 2000
BOOT = 30
R_DERANGE = 3
SPLITS = 6
BETA = 0.3
CAT_BINS = 10
MIN_PROBLEMS = 20
ABILITY_JOIN_MIN = 0.20

OUT = HERE / "out"


def derived_dir() -> Path:
    d = scratch_root() / "derived-holon-projection"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ----------------------------------------------------------------------------------------------
# projection (metadata only)

def concept_courses(mdir: Path) -> dict:
    cc = collections.defaultdict(set)
    for line in open(mdir / "concept-course.txt", encoding="utf-8"):
        k, c = line.rstrip("\n").split("\t")
        name, _, field = k[2:].rpartition("_")
        cc[(name, field)].add(c)
    return cc


def labelled(mdir: Path, dom: str):
    pos = neg = 0
    edges = []
    for line in open(mdir / f"{dom}.json", encoding="utf-8"):
        line = line.strip().rstrip(",")
        if not line.startswith("{"):
            continue
        d = json.loads(line)
        if d["ground_truth"] == 1:
            pos += 1
            edges.append((d["c1"], d["c2"]))
        elif d["ground_truth"] == 0:
            neg += 1
    return edges, pos, neg


def directed(pairs: set) -> set:
    return {(u, v) for (u, v) in pairs if (v, u) not in pairs}


def build_projection(mdir: Path) -> dict:
    cc = concept_courses(mdir)
    w = collections.Counter()
    endpoint_dom = collections.defaultdict(collections.Counter)
    meta = {}
    for dom, f in FIELDS.items():
        edges, pos, neg = labelled(mdir, dom)
        cov = [(a, b) for a, b in edges if (a, f) in cc and (b, f) in cc]
        dw = collections.Counter()
        for a, b in cov:
            for x in cc[(a, f)]:
                for y in cc[(b, f)]:
                    if x != y:
                        dw[(x, y)] += 1
                        endpoint_dom[x][dom] += 1
                        endpoint_dom[y][dom] += 1
        q = set(dw)
        nodes = sorted({c for e in q for c in e})
        clo = reachability(nodes, sorted(q))
        meta[dom] = {"positives": pos, "negatives": neg, "positives_placed": len(cov),
                     "courses": len(nodes), "quotient_edges": len(q),
                     "quotient_mutual_pairs": sum(1 for u, v in q if (v, u) in q) // 2,
                     "closure_pairs": len(clo),
                     "closure_mutual_pairs": sum(1 for u, v in clo if (v, u) in clo) // 2,
                     "reduction_edges": len(reduction(clo))}
        w.update(dw)
    lit = set(w)
    nodes = sorted({c for e in lit for c in e})
    clo = reachability(nodes, sorted(lit))
    red = reduction(clo)
    net = {(x, y) for (x, y), v in w.items() if v > w.get((y, x), 0)}
    nclo = reachability(nodes, sorted(net))
    netred = reduction(nclo)
    dom_of = {c: endpoint_dom[c].most_common(1)[0][0] for c in nodes}
    P = {"P_red": red, "P_clo": directed(clo), "P_net": net, "P_netred": netred}
    meta["pooled"] = {"courses": len(nodes), "P_lit": len(lit), "closure_pairs": len(clo),
                      **{k: len(v) for k, v in P.items()}}
    return {"courses": nodes, "P": P, "dom": dom_of, "meta": meta}


def topo_depth(nodes, edges):
    """Longest-path depth in an acyclic edge set (P_red is acyclic: its edges are non-mutual
    closure pairs, which are strictly ordered)."""
    succ = collections.defaultdict(list)
    indeg = collections.Counter()
    for u, v in edges:
        succ[u].append(v)
        indeg[v] += 1
    depth = {n: 0 for n in nodes}
    frontier = [n for n in nodes if indeg[n] == 0]
    seen = 0
    while frontier:
        nxt = []
        for u in frontier:
            seen += 1
            for v in succ[u]:
                depth[v] = max(depth[v], depth[u] + 1)
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        frontier = nxt
    assert seen == len(nodes), "P_red is not acyclic"
    return depth


# ----------------------------------------------------------------------------------------------
# learner data as a ragged array: per learner, course indices and times (days)

class Ragged:
    def __init__(self, course_lists, time_lists, family, C):
        self.C = C
        lens = np.array([len(c) for c in course_lists], dtype=np.int64)
        self.start = np.concatenate([[0], np.cumsum(lens)[:-1]]).astype(np.int64)
        self.len = lens
        self.course = np.concatenate(course_lists).astype(np.int64) if len(lens) else np.zeros(0, int)
        self.time = np.concatenate(time_lists).astype(np.float64) if len(lens) else np.zeros(0)
        self.family = np.asarray(family)
        self.n = len(lens)
        # each course's catalogue position: median enrolment date over all its learners
        self.cpos = np.array([np.median(self.time[self.course == c]) if np.any(self.course == c)
                              else np.nan for c in range(C)])
        self.cpos = np.where(np.isfinite(self.cpos), self.cpos, np.nanmedian(self.cpos))


def derange_within(groups: np.ndarray, rows: np.ndarray, rng) -> tuple[np.ndarray, np.ndarray]:
    """For the multiset `rows` (indices into learners) grouped by `groups[rows]`, return
    (own, donor) arrays: every row in a group of size >= 2 is paired with a donor from the same
    group under a derangement of positions (no position maps to itself). Singletons dropped."""
    g = groups[rows]
    order = np.argsort(g, kind="stable")
    rs, gs = rows[order], g[order]
    own, don = [], []
    bounds = np.flatnonzero(np.diff(gs)) + 1
    for seg in np.split(np.arange(len(rs)), bounds):
        m = len(seg)
        if m < 2:
            continue
        # a uniformly random cyclic shift of a random permutation is a derangement
        p = rng.permutation(m)
        k = rng.integers(1, m)
        own.append(rs[seg[p]])
        don.append(rs[seg[np.roll(p, k)]])
    if not own:
        return np.zeros(0, int), np.zeros(0, int)
    return np.concatenate(own), np.concatenate(don)


def cross_counts(R: Ragged, own: np.ndarray, donor: np.ndarray, chunk=4_000_000):
    """C x C matrices lt[a, b] = #(t_donor[a] < t_own[b]), gt likewise, over row pairs; a != b.
    With donor == own this is the real within-learner order."""
    C = R.C
    lt = np.zeros(C * C)
    gt = np.zeros(C * C)
    kx = R.len[donor]
    ky = R.len[own]
    combos = kx * ky
    i = 0
    n = len(own)
    while i < n:
        cum = np.cumsum(combos[i:])
        j = i + max(1, int(np.searchsorted(cum, chunk)))
        j = min(j, n)
        sl = slice(i, j)
        cnt = combos[sl]
        tot = int(cnt.sum())
        if tot:
            r = np.repeat(np.arange(j - i), cnt)
            off = np.arange(tot) - np.repeat(np.cumsum(cnt) - cnt, cnt)
            kyr = ky[sl][r]
            ax = R.start[donor[sl]][r] + off // kyr
            by = R.start[own[sl]][r] + off % kyr
            a, b = R.course[ax], R.course[by]
            ta, tb = R.time[ax], R.time[by]
            keep = a != b
            key = a[keep] * C + b[keep]
            lt += np.bincount(key, weights=(ta[keep] < tb[keep]), minlength=C * C)
            gt += np.bincount(key, weights=(ta[keep] > tb[keep]), minlength=C * C)
        i = j
    return lt.reshape(C, C), gt.reshape(C, C)


def residualize(E, ok, cpos, bins=CAT_BINS):
    """CHANGES 2026-10-07 (b): remove what is left of the catalogue after the derangement.

    The signed catalogue gap g(a, b) = cpos[b] - cpos[a] (each course's median enrolment date) is
    binned on |g| into quantile bins over read pairs; within a bin the odd mean m = mean(sign(g) E)
    is subtracted as sign(g) m. Odd by construction, so E stays antisymmetric. Bin means are taken
    over ALL read pairs, of which any one projection's edges are a small share."""
    C = len(cpos)
    iu = np.triu_indices(C, 1)
    g = (cpos[None, :] - cpos[:, None])
    gu, eu, okk = g[iu], E[iu], ok[iu]
    if okk.sum() < 2 * bins:
        return E
    edges = np.quantile(np.abs(gu[okk]), np.linspace(0, 1, bins + 1))
    edges[-1] = np.inf
    b_all = np.clip(np.searchsorted(edges, np.abs(g), side="right") - 1, 0, bins - 1)
    b_u = b_all[iu]
    m = np.zeros(bins)
    for k in range(bins):
        sel = okk & (b_u == k)
        if sel.any():
            m[k] = float(np.mean(np.sign(gu[sel]) * eu[sel]))
    out = E - np.sign(g) * m[b_all]
    np.fill_diagonal(out, 0.0)
    return out


def excess(R: Ragged, rows: np.ndarray, rng, r_derange=R_DERANGE, full=False, resid=True):
    """Antisymmetric excess E (C x C, NaN where unread) and the raw order 2s-1, over `rows`."""
    own0, _ = derange_within(R.family, rows, rng)       # rows in a family of size >= 2
    lt, gt = cross_counts(R, own0, own0)
    n_real = lt + gt
    s = np.where(n_real > 0, lt / np.maximum(n_real, 1), np.nan)
    dl = np.zeros_like(lt)
    dg = np.zeros_like(gt)
    for _ in range(r_derange):
        own, don = derange_within(R.family, rows, rng)
        a, b = cross_counts(R, own, don)
        dl += a
        dg += b
    n_d = dl + dg
    d = np.where(n_d > 0, dl / np.maximum(n_d, 1), np.nan)
    e = s - d
    E = (e - e.T) / 2
    ok = (n_real >= MIN_CELL) & (n_d / r_derange >= MIN_CELL) & (n_d.T / r_derange >= MIN_CELL)
    ok = ok & ok.T
    np.fill_diagonal(ok, False)
    if resid:
        E = residualize(E, ok, R.cpos)
    E_all = E.copy()
    E = np.where(ok, E, np.nan)
    raw = np.where(n_real >= MIN_CELL, 2 * s - 1, np.nan)
    np.fill_diagonal(E, np.nan)
    assert np.allclose(np.nan_to_num(E), -np.nan_to_num(E.T)), "E must be antisymmetric"
    if full:
        return E, raw, int(len(own0)), E_all
    return E, raw, int(len(own0))


# ----------------------------------------------------------------------------------------------
# agreement

def edge_index(P, cidx):
    return np.array([(cidx[x], cidx[y]) for x, y in P if x in cidx and y in cidx], dtype=int).reshape(-1, 2)


def D_of(E, idx):
    if len(idx) == 0:
        return float("nan"), 0
    v = E[idx[:, 0], idx[:, 1]]
    v = v[np.isfinite(v)]
    return (float(v.mean()) if len(v) else float("nan")), int(len(v))


def calls(E, idx, C):
    """Three-class projection and identified calls over every read unordered pair."""
    proj = np.zeros((C, C), dtype=int)
    for a, b in idx:
        proj[a, b] = 1
        proj[b, a] = -1 if proj[b, a] == 0 else 0     # both directions asserted -> none
    iu = np.triu_indices(C, 1)
    read = np.isfinite(E[iu])
    pc = proj[iu][read]
    ic = np.where(E[iu][read] >= TAU, 1, np.where(E[iu][read] <= -TAU, -1, 0))
    return pc, ic


def null_relabel(courses, dom, rng):
    """A derangement of courses within domain: a graph of identical shape, relabelled."""
    perm = {}
    by = collections.defaultdict(list)
    for c in courses:
        by[dom[c]].append(c)
    for _, cs in by.items():
        if len(cs) < 2:
            perm.update({c: c for c in cs})
            continue
        p = rng.permutation(len(cs))
        k = int(rng.integers(1, len(cs)))
        src = [cs[i] for i in p]
        dst = [cs[i] for i in np.roll(p, k)]
        perm.update(dict(zip(src, dst)))
    return perm


def agreement(E, raw, P, courses, cidx, dom, rng, draws=NULL_DRAWS):
    C = len(cidx)
    idx = edge_index(P, cidx)
    D, n_read = D_of(E, idx)
    Draw, _ = D_of(raw, idx)
    rev = idx[:, ::-1] if len(idx) else idx
    Drev, _ = D_of(E, rev)
    if np.isfinite(D):
        assert abs(Drev + D) < 1e-9, "reversed projection must score -D"
    v = E[idx[:, 0], idx[:, 1]] if len(idx) else np.zeros(0)
    v = v[np.isfinite(v)]
    dec = v[np.abs(v) >= TAU]
    conc = float((dec > 0).mean()) if len(dec) else float("nan")
    pc, ic = calls(E, idx, C)
    k = kappa_nominal(pc, ic) if len(pc) >= 3 else float("nan")
    univ = [c for c in courses if c in cidx]
    nulls, knull, rnull = [], [], []
    for _ in range(draws):
        pm = null_relabel(univ, dom, rng)
        Pn = {(pm.get(x, x), pm.get(y, y)) for x, y in P}
        ni = edge_index(Pn, cidx)
        dn, _ = D_of(E, ni)
        nulls.append(dn)
        rn, _ = D_of(raw, ni)
        rnull.append(rn)
        if len(knull) < 300:
            a, b = calls(E, ni, C)
            knull.append(kappa_nominal(a, b) if len(a) >= 3 else float("nan"))
    nulls = np.array([x for x in nulls if np.isfinite(x)])
    rnull = np.array([x for x in rnull if np.isfinite(x)])
    knull = np.array([x for x in knull if np.isfinite(x)])
    p_hi = float((1 + (nulls >= D).sum()) / (1 + len(nulls))) if np.isfinite(D) and len(nulls) else float("nan")
    p_lo = float((1 + (nulls <= D).sum()) / (1 + len(nulls))) if np.isfinite(D) and len(nulls) else float("nan")
    return {"edges": int(len(P)), "edges_in_universe": int(len(idx)), "edges_read": n_read,
            "D": D, "null_mean": float(nulls.mean()) if len(nulls) else None,
            "null_sd": float(nulls.std()) if len(nulls) else None,
            "p_upper": p_hi, "p_lower": p_lo,
            "concordance": conc, "decided_edges": int(len(dec)),
            "kappa3": k, "kappa3_null_mean": float(knull.mean()) if len(knull) else None,
            "kappa3_null_p95": float(np.percentile(knull, 95)) if len(knull) else None,
            "raw_order_D": Draw,
            "raw_order_null_mean": float(rnull.mean()) if len(rnull) else None,
            "raw_order_p_upper": float((1 + (rnull >= Draw).sum()) / (1 + len(rnull)))
            if np.isfinite(Draw) and len(rnull) else None}


def split_half(R: Ragged, rng, splits=SPLITS):
    rs = []
    for _ in range(splits):
        perm = rng.permutation(R.n)
        h = R.n // 2
        Ea, _, _ = excess(R, np.sort(perm[:h]), rng, r_derange=1)
        Eb, _, _ = excess(R, np.sort(perm[h:]), rng, r_derange=1)
        iu = np.triu_indices(R.C, 1)
        x, y = Ea[iu], Eb[iu]
        m = np.isfinite(x) & np.isfinite(y)
        if m.sum() >= 10:
            rs.append(spearman(x[m], y[m]))
    rs = [r for r in rs if np.isfinite(r)]
    return (float(np.mean(rs)) if rs else float("nan")), len(rs)


def bootstrap_D(R: Ragged, Ps, cidx, rng, E0, B=BOOT):
    """Percentile interval on D over the edge set READ in the full sample, held fixed: letting
    each resample re-decide which edges clear MIN_CELL changes the estimand between draws (found in
    the pre-commit smoke run, where intervals excluded their own point estimate)."""
    vals = collections.defaultdict(list)
    fixed = {}
    for name, P in Ps.items():
        idx = edge_index(P, cidx)
        fixed[name] = idx[np.isfinite(E0[idx[:, 0], idx[:, 1]])] if len(idx) else idx
    for _ in range(B):
        rows = rng.integers(0, R.n, R.n)
        _, _, _, E = excess(R, rows, rng, r_derange=1, full=True)
        for name in Ps:
            d, _ = D_of(E, fixed[name])
            if np.isfinite(d):
                vals[name].append(d)
    return {k: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5)), len(v))
            for k, v in vals.items()}


def verdict(a: dict, rel: float, ci) -> str:
    if a["edges_read"] < MIN_EDGES:
        return "UNANSWERABLE"
    if not np.isfinite(rel) or rel < REL_MIN:
        return "CATALOGUE ONLY"
    lo, hi = ci[0], ci[1]
    if a["D"] > 0 and a["p_upper"] < 0.05 and lo > 0:
        if a["decided_edges"] >= MIN_DECIDED and a["concordance"] >= CONC_MIN:
            return "PROJECTION HOLDS"
        return "PROJECTION PARTIAL"
    if a["D"] < 0 and a["p_lower"] < 0.05 and hi < 0:
        return "LEVELS INDEPENDENT (REVERSED)"
    return "LEVELS INDEPENDENT"


def analyse(R: Ragged, proj, cidx, rng, boot=BOOT, draws=NULL_DRAWS, which=("P_red", "P_clo", "P_net", "P_netred")):
    E, raw, n_used = excess(R, np.arange(R.n), rng)
    E_nores, _, _ = excess(R, np.arange(R.n), rng, resid=False)
    rel, nrel = split_half(R, rng)
    Ps = {k: proj["P"][k] for k in which}
    cis = bootstrap_D(R, Ps, cidx, rng, E, B=boot)
    out = {"learners": int(R.n), "learners_in_families": n_used,
           "pairs_read": int(np.isfinite(E[np.triu_indices(R.C, 1)]).sum()),
           "split_half_spearman_E": rel, "split_half_draws": nrel,
           "E_abs_median": float(np.nanmedian(np.abs(E[np.triu_indices(R.C, 1)]))), "proj": {}}
    for k, P in Ps.items():
        a = agreement(E, raw, P, proj["courses"], cidx, proj["dom"], rng, draws=draws)
        ci = cis.get(k, (float("nan"), float("nan"), 0))
        a["boot_ci"] = [ci[0], ci[1]]
        a["boot_draws"] = ci[2]
        a["verdict"] = verdict(a, rel, ci)
        a["D_derangement_only"] = D_of(E_nores, edge_index(P, cidx))[0]
        out["proj"][k] = a
    return out


# ----------------------------------------------------------------------------------------------
# families

def families(breadth, first_t, ability_tertile):
    b = np.digitize(breadth, [3, 4, 6])                     # 2 | 3 | 4-5 | 6+
    q = np.floor(first_t / 7).astype(int)                     # CHANGES (a): week of first enrolment
    return (b * 100000 + q) * 10 + ability_tertile


# ----------------------------------------------------------------------------------------------
# synthetic floor

def synth_marginals(courses, rng, real=None):
    """Learner count, course popularity, breadth distribution, course date distributions."""
    C = len(courses)
    if real is not None:
        return real
    pop = 1.0 / np.arange(1, C + 1) ** 0.9
    rng.shuffle(pop)
    opens = np.sort(rng.uniform(0, 4 * 365, C))
    rng.shuffle(opens)
    kdist = np.array([0.55, 0.2, 0.1, 0.06, 0.04, 0.02, 0.015, 0.01, 0.005])
    return {"N": 250_000, "pop": pop / pop.sum(), "open": opens,
            "k_values": np.arange(2, 2 + len(kdist)), "k_probs": kdist / kdist.sum(),
            "start_span": 5 * 365}


def synth_world(world, proj, cidx, M, rng, beta=BETA):
    courses = list(cidx)
    C = len(courses)
    red = [(cidx[x], cidx[y]) for x, y in proj["P"]["P_red"] if x in cidx and y in cidx]
    nodes = sorted({u for e in red for u in e})
    depth = topo_depth(nodes, red)
    maxd = max(depth.values()) if depth else 1
    score = rng.uniform(0, maxd + 1, C)
    for n, dpt in depth.items():
        score[n] = dpt + rng.uniform(0, 0.99)
    if world == "W_ind":
        pm = null_relabel(courses, proj["dom"], rng)
        score = score[[cidx[pm[c]] for c in courses]]
    opens = np.array(M["open"], float).copy()
    if world == "W_cat":
        opens = np.sort(opens)[np.argsort(np.argsort(score))]   # opens in planted order
    else:
        rng.shuffle(opens)
    N = M["N"]
    ks = rng.choice(M["k_values"], size=N, p=M["k_probs"])
    starts = rng.uniform(0, M["start_span"], N)
    follows = rng.random(N) < (beta if world in ("W_proj", "W_ind") else 0.0)
    cl, tl = [], []
    pop = M["pop"]
    for i in range(N):
        k = min(int(ks[i]), C)
        cs = rng.choice(C, size=k, replace=False, p=pop)
        if follows[i]:
            cs = cs[np.argsort(score[cs])]
            t = starts[i] + np.cumsum(rng.exponential(60, k))
            t = np.maximum(t, opens[cs] + rng.uniform(0, 5, k))
        else:
            t = np.maximum(starts[i], opens[cs]) + rng.exponential(90, k)
        cl.append(cs)
        tl.append(t)
    first = np.array([t.min() for t in tl])
    fam = families(ks, first, np.zeros(N, dtype=int))
    return Ragged(cl, tl, fam, C)


def floor(proj, cidx, M, label, seeds=3, boot=10, draws=500):
    res = {"shape": label, "beta": BETA, "runs": []}
    for w in ("W_proj", "W_cat", "W_ind"):
        for s in range(seeds):
            rng = np.random.default_rng(SEED + 1000 * s + hash(w) % 997)
            R = synth_world(w, proj, cidx, M, rng)
            a = analyse(R, proj, cidx, rng, boot=boot, draws=draws, which=("P_red",))
            pr = a["proj"]["P_red"]
            row = {"world": w, "seed": s, "verdict": pr["verdict"], "D": pr["D"],
                   "ci": pr["boot_ci"], "p": pr["p_upper"], "concordance": pr["concordance"],
                   "edges_read": pr["edges_read"], "rel": a["split_half_spearman_E"],
                   "raw_order_D": pr["raw_order_D"], "raw_order_p": pr["raw_order_p_upper"]}
            print(json.dumps(row), flush=True)
            res["runs"].append(row)
    for b in (0.1, 0.2):
        rng = np.random.default_rng(SEED + int(b * 100))
        R = synth_world("W_proj", proj, cidx, M, rng, beta=b)
        a = analyse(R, proj, cidx, rng, boot=boot, draws=draws, which=("P_red",))
        pr = a["proj"]["P_red"]
        row = {"world": "W_proj", "beta": b, "verdict": pr["verdict"], "D": pr["D"],
               "ci": pr["boot_ci"], "p": pr["p_upper"], "concordance": pr["concordance"],
               "rel": a["split_half_spearman_E"]}
        print(json.dumps(row), flush=True)
        res.setdefault("sensitivity", []).append(row)
    v = collections.defaultdict(list)
    for r in res["runs"]:
        v[r["world"]].append(r["verdict"])
    bad = {"PROJECTION HOLDS", "PROJECTION PARTIAL"}
    res["pass"] = bool(all(x == "PROJECTION HOLDS" for x in v["W_proj"])
                       and not any(x in bad for x in v["W_cat"])
                       and not any(x in bad for x in v["W_ind"]))
    res["verdicts"] = dict(v)
    return res


# ----------------------------------------------------------------------------------------------
# real data

def to_days(s: str) -> float:
    return (datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S") - datetime(2015, 1, 1)).total_seconds() / 86400


def load_real(cidx):
    dd = derived_dir()
    ab = {}
    ab_path = dd / "ability.tsv"
    if ab_path.exists():
        for line in open(ab_path, encoding="utf-8"):
            u, n, k = line.rstrip("\n").split("\t")
            n, k = int(n), int(k)
            if n >= MIN_PROBLEMS:
                ab[u] = k / n
    cl, tl, ids = [], [], []
    for line in open(dd / "user-order.jsonl", encoding="utf-8"):
        d = json.loads(line)
        best = {}
        for c, t in zip(d["c"], d["t"]):
            if c in cidx:
                tt = to_days(t)
                if c not in best or tt < best[c]:
                    best[c] = tt
        if len(best) < 2:
            continue
        ks = list(best)
        cl.append(np.array([cidx[c] for c in ks]))
        tl.append(np.array([best[c] for c in ks]))
        ids.append(d["u"])
    N = len(cl)
    vals = np.array([ab[u] for u in ids if u in ab])
    join = len(vals) / max(N, 1)
    tert = np.zeros(N, dtype=int)
    used_ability = bool(join >= ABILITY_JOIN_MIN and len(vals) >= 30)
    if used_ability:
        cuts = np.percentile(vals, [100 / 3, 200 / 3])
        for i, u in enumerate(ids):
            if u in ab:
                tert[i] = 1 + int(np.digitize(ab[u], cuts))
    breadth = np.array([len(c) for c in cl])
    first = np.array([t.min() for t in tl])
    fam = families(breadth, first, tert)
    R = Ragged(cl, tl, fam, len(cidx))
    info = {"learners": N, "ability_join_share": join, "ability_used": used_ability,
            "ability_learners": int(len(vals))}
    return R, info, breadth, first, tl, cl


def real_marginals(R: Ragged, breadth, tl, cl):
    C = R.C
    pop = np.bincount(R.course, minlength=C).astype(float)
    pop = np.maximum(pop, 0.5) / np.maximum(pop, 0.5).sum()
    first_course = np.full(C, np.nan)
    for t, c in zip(tl, cl):
        for ci, ti in zip(c, t):
            if not first_course[ci] <= ti:
                first_course[ci] = ti
    first_course = np.where(np.isfinite(first_course), first_course, np.nanmedian(first_course))
    kv, kc = np.unique(np.minimum(breadth, 12), return_counts=True)
    firsts = np.array([t.min() for t in tl])
    return {"N": int(R.n), "pop": pop, "open": first_course - firsts.min(),
            "k_values": kv, "k_probs": kc / kc.sum(),
            "start_span": float(np.percentile(firsts, 99) - firsts.min())}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-courses", action="store_true")
    ap.add_argument("--floor", action="store_true")
    ap.add_argument("--shape", default="synthetic", choices=["synthetic", "real"])
    ap.add_argument("--real", action="store_true")
    args = ap.parse_args()
    mdir = data_path("MOOCCUBEX_DIR")
    proj = build_projection(mdir)
    OUT.mkdir(exist_ok=True)
    if args.write_courses:
        (derived_dir() / "courses.txt").write_text("\n".join(proj["courses"]) + "\n")
        (OUT / "projection.json").write_text(json.dumps(proj["meta"], indent=1, ensure_ascii=False))
        print(json.dumps(proj["meta"], indent=1, ensure_ascii=False))
        return 0
    cidx = {c: i for i, c in enumerate(proj["courses"])}
    if args.floor:
        rng = np.random.default_rng(SEED)
        if args.shape == "real":
            R, info, breadth, first, tl, cl = load_real(cidx)
            cidx_used = cidx
            M = real_marginals(R, breadth, tl, cl)
            del R
        else:
            M = synth_marginals(proj["courses"], rng)
            cidx_used = cidx
        t0 = time.time()
        res = floor(proj, cidx_used, M, args.shape)
        res["seconds"] = round(time.time() - t0)
        (OUT / f"floor-{args.shape}.json").write_text(json.dumps(res, indent=1))
        print("FLOOR", "PASS" if res["pass"] else "FAIL", res["verdicts"])
        return 0
    if args.real:
        fl = OUT / "floor-real.json"
        floor_pass = json.loads(fl.read_text())["pass"] if fl.exists() else False
        R, info, *_ = load_real(cidx)
        rng = np.random.default_rng(SEED + 1)
        res = analyse(R, proj, cidx, rng)
        res.update(info)
        res["floor_pass"] = floor_pass
        if not floor_pass:
            for a in res["proj"].values():
                a["verdict_before_floor"] = a["verdict"]
                a["verdict"] = "UNANSWERABLE"
        # control: no conditioning on breadth or the general factor (cohort only)
        R.family = families(np.full(R.n, 2), np.array([R.time[R.start[i]:R.start[i] + R.len[i]].min()
                                                         for i in range(R.n)]), np.zeros(R.n, int))
        E, raw, _ = excess(R, np.arange(R.n), np.random.default_rng(SEED + 2))
        res["cohort_only_D"] = {k: D_of(E, edge_index(proj["P"][k], cidx))[0] for k in proj["P"]}
        res["projection"] = proj["meta"]
        res["descriptive_only"] = ("concept-course membership is model-extracted (NER over captions) "
                                   "with no human reference; per CLAUDE.md the verdict is descriptive")
        (OUT / "holon.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
        print(json.dumps({k: (v["verdict"], v["D"], v["boot_ci"], v["p_upper"]) for k, v in res["proj"].items()}, indent=1))
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "1")
    raise SystemExit(main())
