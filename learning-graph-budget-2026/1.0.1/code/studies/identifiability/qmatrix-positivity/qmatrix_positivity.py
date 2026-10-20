"""
Per-edge Q-matrix positivity: is the "dependent skill held without its prerequisite" cell
identifiable BY DESIGN, edge by edge, and are the edges the item design cannot answer the same edges
the learners' order leaves undecided?

PRE-REGISTRATION. Written 2026-10-07, before any number in this file was computed on real data.
Committed before the real run (procedure: scratchpad analyses/BRIEF.md, steps 1-2).

## Question

Paper II's F1 measures the EMPIRICAL decided share: the positivity atlas
(`studies/identifiability/overlap/atlas.py`, `out/atlas.json`; states from `shared/edge_state.py`,
the merge-node gate from `shared/reachability.py`) finds that almost no learners meet a dependent
skill B having failed its candidate prerequisite A, so almost no edge is decided.

Gu & Xu (2024, Statistica Sinica, doi:10.5705/ss.202021.0350; Proposition 1; literature review
`research/readiness/learning-graph-budget-2026/literature.md` entry 1.1, synthesis row 1, strand-1
analysis 1, ranked analysis 2) show the same kind of limit one level up, in the DESIGN: if no item
measures B without A, the latent mass "B mastered, A not" is identified only jointly with "neither"
(their two-attribute toy, items {A} and {A,B}), whatever the learners did, and an edge's presence
becomes a convention. Their condition depends only on the Q-matrix.

So, for every candidate edge A -> B the atlas scores, on the three corpora whose item-to-skill maps
are held (XES3G5M, ASSISTments 2012-13, Eedi NeurIPS 2020): does the Q-matrix contain any item that
measures B without A (and A without B)? Then cross that design state with the atlas's empirical
state for the same edge.

## Data (reads three licensed corpora; aggregates only leave this script)

  XES3G5M   $XES_DIR/attempts.tsv + cid2route.json, read exactly as atlas.xes3g5m_rows reads them.
            Item = question id; its KCs are the `_`-joined concept field, kept where the KC is in
            cid2route (the atlas's 866-leaf filter). Licence: TAL research release; no redistribution.
  ASSIST    $ASSIST_DIR/assist_rich.csv, read exactly as latent-shape/build_matrix._assist_rows reads it
            (rows with an empty or NA skill_id dropped). Item = problem_id; its skills = every
            skill_id that problem carries on any row. ASSISTments terms: analysis only.
  Eedi      $EEDI_ANSWERS (answers.tsv, the slim file data/ingest/eedi/slim.py writes) + $EEDI_ZIP for
            the subject tree, through shared.corpus.Eedi's level-3 leaf map. Item = QuestionId.
            Research use confirmed with Eedi; no redistribution. LIMITATION carried from the atlas:
            Eedi keeps each learner's LATEST answer, so its "order" is last-answer order.
            answers.tsv was still being written by another agent when this study started; the
            reproduction gate below (learner count, atlas counts) is the completeness check, and a
            file that fails it is reported BLOCKED rather than read.
  Nothing is derived to disk. No learner-level row, item text or skill name leaves the script;
  units appear only as counts.

The Q-matrix CODER is the platform, not this study: XES3G5M's KC routes were authored by TAL's
content team; ASSISTments skill tags by the ASSISTments content builders; Eedi's subject tree by
Eedi. None is validated here against an independent coder, and this study does not need it to be:
the question is what THE DESIGN AS TAGGED can identify, which is the same tagging the atlas reads.

## Candidate edge: exactly the atlas's definition

  XES3G5M, Eedi  every ordered pair (A, B), A != B, of units any learner touched (sorted unit names),
                 sampled to 20,000 by atlas.corpus_rng(name) without replacement -- the atlas.audit
                 path, run with its default --max-pairs 20000. Every sampled pair has learners at B.
  ASSISTments    the atlas does not carry an ASSISTments row; F1's ASSISTments figure comes from
                 positivity.py `assist` (out/positivity-assist.json), whose candidate edges are every
                 ordered skill pair sampled to 40,000 by np.random.default_rng(0). That definition is
                 used for ASSISTments. (Decision recorded: the brief names ASSISTments 2012-13; this is
                 the atlas family's only scoring of it.)

## Estimands

Per edge (A -> B), from the Q-matrix Q (items x units, binary):
  iso_BnotA  items with B and not A.   iso_BnotA == 0  ->  U  ("B-without-A unidentified by design")
  iso_AnotB  items with A and not B.   either zero    ->  U_either
  pure_B     items measuring B ALONE (Gu & Xu's I_K row for B).  pure_B == 0 -> U_pure (strict)
  co_AB      items carrying both.
U is the PRIMARY design state: the pairwise reading of Proposition 1 for the two-attribute
sub-model {A, B}. U_pure is the strict reading (an identity row for B over all attributes) and is
secondary; it can only be larger than U.

Per edge, the EMPIRICAL state, recomputed per edge with the atlas's rules (the atlas commits only
aggregates):
  unreadable      MDE undefined (a cell under 5 learners, or the control arm at a ceiling)
  unpowered       readable, MDE > 0.10 (CLAIMED_EFFECT)
  supported       powered and the drop is at or above the MDE
  contradicted    powered null that survives the merge-node gate (shared/reachability.py)
  unfalsifiable   powered null the gate removed (reads UNKNOWN in the atlas)
  decided = supported + contradicted; undecided = everything else (the atlas's `unknown`).

Reported per corpus:
  (1) the census share of ALL ordered pairs in U (exact; no interval: it is the whole population),
      and the share among the atlas's sampled edges (Wilson 95%; and a cluster bootstrap over
      dependants B, 1,000 draws, because edges sharing B share B's items);
  (2) the 2 x 5 cross-tabulation U x empirical state, and the same for U_either and U_pure, and
      for the subset of edges whose skills share at least one item (co_AB >= 1), where the design
      question has bite;
  (3) f = |U and undecided| / |undecided|, with both intervals above -- the HEADLINE;
  (4) d = P(decided | U) - P(decided | not U), SIGNED, with a within-dependant derangement null;
  (5) the overlap of the design-level set U and the learner-level set (undecided), as signed counts:
      |U and undecided|, |U and decided|, |not U and undecided|, |not U and decided|, and Jaccard;
  (6) |U and supported| / |supported|: supported edges whose B-without-A cell the design cannot
      identify. Their drop can be carried by co-tagged items (a learner who lacks A fails an {A,B}
      item whatever their B), so they are flagged as possibly supported by construction;
  (7) the qmatrix.py C1-C4 conditions on each Q (reused from studies/identifiability/identifiability/).

## Controls

  * REPRODUCTION GATE (artefact check, CLAUDE.md "an artefact that parses..."). The per-edge states
    come from a dense re-implementation of atlas.audit / positivity.main (the originals do not fit
    in memory per edge for Eedi and keep no per-edge record). Two checks: (a) on a synthetic corpus
    with ties, multi-KC items and string timestamps, the re-implementation must agree with
    positivity.classify, positivity.mde, edge_state.classify_edge and reachability.reachability on
    EVERY edge (cells, MDE, state, falsifiability) -- part of the floor; (b) on real data, the
    recomputed aggregates (learners, units, edges, readable, detect_20pt, supported, contradicted
    before and after the gate, unknown) are compared with the committed row (atlas.json for XES3G5M
    and Eedi; positivity-assist.json's summary for ASSISTments). A mismatch does not stop the run;
    the cross-tab is then labelled as against a RECOMPUTED atlas and the gap is reported.
  * TIMESTAMP ORDER. The atlas compares timestamps as STRINGS. They are converted to integers only
    where that provably preserves string order (all-digit strings of one length; one fixed datetime
    pattern); otherwise the script stops.
  * DERANGED NULL for d, family-matched by dependant: U labels are deranged (Sattolo cycle) among
    the edges sharing the same B, so B's own item count, reach and difficulty are held fixed and
    no edge keeps its own label. The unit permuted is the edge within B, the unit at which A (and so
    U) varies. Size: the null moves exactly |U| labels, the size of the treatment. 1,000 draws.
    Dependants with a single sampled edge cannot be deranged and are reported.

## Synthetic detection floor (run before real data; failure -> every verdict UNANSWERABLE)

  F1  Gu & Xu's toy: items {A}, {A,B}, {A,B}. A -> B must be U (iso_BnotA = 0, pure_B = 0);
      B -> A must not (one item, {A}, measures A without B).
  F2  A seeded random Q (200 units, 500 items, 1-4 units each) with 40 PLANTED unidentified edges
      (every item carrying b also given a) and 40 PLANTED isolating items ({b} alone added), on
      disjoint units, then a brute-force loop over items for every ordered pair. The matrix counter
      must equal the loop EXACTLY for iso_BnotA, iso_AnotB, pure_B and co_AB on all 39,800 ordered
      pairs; exactly 40 and 40 must have been planted; every planted
      unidentified edge must come back U; every planted isolating edge must come back not-U with
      pure_B >= 1.
  F3  The Q builder fed a row STREAM (items repeated across learners, multi-unit items, rows
      shuffled) must rebuild F2's Q exactly.
  F4  The dense empirical replica against the atlas's own functions on a synthetic corpus (6,000
      learners, 15 units, single- and multi-unit items, two practice regimes, timestamp ties): identical cells, MDE, state and
      falsifiability on every ordered pair, and the corpus must produce at least one supported, one
      would-be contradicted and one falsifiable pair, so that no branch passes vacuously.
  F5  The cross-tab and verdict functions on planted labels with known answers: counts exact, and
      each verdict branch reached by an input built for it.
  F6  TimeKey on mixed-width digit and datetime strings must order rows exactly as Python's str
      comparison (added 2026-10-07, see CHANGES).
  The counter is deterministic, so "exact" is the only pass.

## Pre-registered verdicts (per corpus; thresholds fixed here)

Headline f = share of the atlas's UNDECIDED edges whose B-without-A cell is unidentified by design.
Its interval is the WIDER of Wilson and the dependant-cluster bootstrap (conservative).
  f >= 0.50                      DESIGN-LIMITED: most undecided edges are already unidentified by the
                                 item design; F1's limit is the Q-matrix, not only the learner order.
  upper 95% bound of f < 0.05    LEARNER-ORDER-LIMITED: the design isolates B from A for almost
                                 every undecided edge; F1's limit is who reached B without A, not
                                 which items exist.
  otherwise                      MIXED: both limits bind; report the two shares side by side.
Overlap of the design-level and learner-level limits (signed counts, item 5):
  |U| = 0                                            NO DESIGN LIMIT
  Jaccard(U, undecided) >= 0.50                      SAME EDGES
  >= 0.90 of U undecided, Jaccard < 0.50             DESIGN NESTED IN LEARNER LIMIT (the design's
                                                     edges are a subset of the learners')
  otherwise                                          DIFFERENT EDGES
Direction of d (item 4), checked as a sign, not a magnitude:
  d < 0 with derangement p < 0.05   design-unidentified edges are decided LESS often: the two
                                    limits point the same way.
  d > 0 with derangement p < 0.05   design-unidentified edges are decided MORE often: possible only
                                    through co-tagged items, and read as a co-tagging artefact in
                                    the atlas's decisions, not as evidence about the edges.
  otherwise                         NO DETECTED ASSOCIATION beyond the dependant.
Supported-by-construction flag (item 6): if |U and supported| / |supported| >= 0.05, F1's
supported count CARRIES DESIGN-UNIDENTIFIED EDGES and they must be footnoted or removed.

## What each pattern means for F1 (pre-registered)

  * LEARNER-ORDER-LIMITED on all three: Gu & Xu's condition holds pairwise on these designs, so the
    design does not explain F1's low decided shares. F1's measurement is a distinct, learner-level
    limit; Gu & Xu are credited for the argument (literature row 1), not as the cause of the numbers.
  * DESIGN-LIMITED anywhere: on that corpus F1 must say the item design forbids the answer for most
    undecided edges before any learner order is considered, and the decided share should be
    re-stated over design-identified edges only.
  * MIXED: F1 states both shares beside each other.
  * A positive d or the supported flag: some of F1's SUPPORTED edges on that corpus may be supported
    by co-tagged items rather than by an edge; F1 footnotes the count.

## What this can and cannot say

It can say whether the item design permits the B-without-A cell to be identified, pairwise, for
each scored edge, and whether that design-level limit and the learner-level limit fall on the same
edges. It cannot say a design-identified edge IS identified: Gu & Xu's Theorem 1 needs more than a
pairwise isolating item, the learners must still take those items (which is F1's measurement), and
the Q-matrix is the platform's tagging, not a validated one. It says nothing about direction,
conjunction or lag. The census share is over the population of ordered pairs; the cross-tab is over
the atlas's random sample, and its intervals resample edges (Wilson) or dependants (cluster
bootstrap), not learners: the empirical states are taken as the atlas computed them.

## Machine budget

OMP/OPENBLAS/MKL threads 1. Eedi's dense learner x unit arrays are ~0.3 GB each (119k x 308 int64);
three of them stay under the 3 GB ceiling. Bootstrap and derangement at 1,000 draws each: the
statistics are counts, so 1,000 gives a Monte-Carlo error near 0.007 on a p-value of 0.05, enough
for a threshold at 0.05.

    python3 qmatrix_positivity.py --floor
    python3 qmatrix_positivity.py --corpus xes3g5m|assist|eedi     (each writes out/<corpus>.json)
    python3 qmatrix_positivity.py --summary                       (out/summary.json from the three)

## CHANGES

2026-10-07, after the first synthetic floor run and before any real data was read or the design
committed. The first floor passed every check, but two checks passed VACUOUSLY: with 60 units the
disjoint-unit planting fitted 30 unidentified edges and 0 isolating ones (an `all()` over an empty
list is True), and the F4 corpus produced no falsifiable pair, so the reachability branch was only
tested where it returns False. F2 now uses 200 units and asserts 40 + 40 were planted; F4 asserts
every branch occurs. Its fixture then needed two further changes before any falsifiable pair
appeared (still zero mismatches throughout): a second learner population that takes the items once
in near-fixed order, with the first 15 items each measuring one unit so later units can be merge
nodes, and 6,000 learners rather than 3,000, because at ~375 learners per stratum the merge node's
MDE sits at the 0.10 power line. These change the TEST FIXTURE, not the instrument: the replica
agreed with the atlas's functions on every pair of every version. No threshold or verdict changed.

2026-10-07, at the first real load (XES3G5M), before any number was computed: the order guard
stopped the run -- XES3G5M's millisecond timestamps are not all 13 digits (a 12-digit one appeared).
The atlas compares them as STRINGS, under which a 12-digit time sorts by its characters, not its
value. To reproduce the atlas, TimeKey now keys all-digit times in string (lexicographic) order
rather than refusing; the count of rows at each width is written to the output, and the floor now
checks the key against Python's sort on mixed-width strings (F6). Whether string order is the
RIGHT order for those rows is a question about the atlas, reported, not repaired here.
Same day, at the first ASSISTments load, before any number: start_time carries fractional seconds
of varying width ('...:52.97775'), which the fixed-pattern datetime branch refused. TimeKey was
replaced by an interning ranker -- distinct strings sorted by Python's str sort, each row keyed by
its string's rank -- which reproduces the atlas's string comparison for ANY format, and F6 now
includes mixed fractional widths. XES3G5M is re-run under this key so all three corpora share one
code version.

POST-RUN NOTE, 2026-10-07 (after the real run; no threshold, verdict or code changed): the
within-dependant derangement null came back degenerate (standard deviation ~0) for U on XES3G5M and
Eedi, because every sampled edge into the dependants holding a U edge is undecided, and it is
degenerate by construction for U_pure, which is a property of B alone. The direction verdict is
therefore not informative on these data; README.md reads the sign of d descriptively.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import sys  # noqa: E402
from array import array  # noqa: E402
from collections import defaultdict  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "studies/identifiability/overlap"))
sys.path.insert(0, str(REPO / "studies/identifiability/identifiability"))

import atlas  # noqa: E402
import positivity  # noqa: E402
from shared.edge_state import (CLAIMED_EFFECT, CONTRADICTED, SUPPORTED,  # noqa: E402
                               UNKNOWN, classify_edge)
from shared.paths import data_path  # noqa: E402
from shared import reachability as reach_mod  # noqa: E402

MIN_CELL = positivity.MIN_CELL
INF = np.iinfo(np.int64).max
STATES = ("unreadable", "unpowered", "supported", "contradicted", "unfalsifiable", "no_comparison")
DECIDED = ("supported", "contradicted")
N_BOOT = 1000
N_NULL = 1000
SEED = 20261007

# thresholds, as pre-registered in the docstring
F_DESIGN = 0.50
F_LEARNER_UPPER = 0.05
JACCARD_SAME = 0.50
NESTED_SHARE = 0.90
P_DIR = 0.05
SUPPORTED_FLAG = 0.05


# ----------------------------------------------------------------------------- Q-matrix counters

def q_from_stream(pairs, units):
    """Rebuild Q (items x units, bool) from a stream of (item, unit) incidences. Duplicates are
    absorbed: an item carries a unit if any row says so."""
    uidx = {u: j for j, u in enumerate(units)}
    item_sets = defaultdict(set)
    for it, u in pairs:
        item_sets[it].add(uidx[u])
    items = sorted(item_sets)
    Q = np.zeros((len(items), len(units)), dtype=bool)
    for r, it in enumerate(items):
        Q[r, list(item_sets[it])] = True
    return items, Q


def design_counts(Q):
    """Matrix counters, units x units: co[a,b] = items with a and b; iso[a,b] = items with b and
    not a (the B-without-A count for edge a -> b); pure[b] = items measuring b alone."""
    Qf = Q.astype(np.float64)
    co = np.rint(Qf.T @ Qf).astype(np.int64)
    n = np.diag(co).copy()
    iso = n[None, :] - co              # iso[a, b] = n[b] - co[a, b]
    single = Q.sum(1) == 1
    pure = Q[single].sum(0).astype(np.int64)
    return co, iso, pure, n


def design_counts_bruteforce(Q):
    """The same counters by a loop over items -- the floor's reference."""
    k = Q.shape[1]
    co = np.zeros((k, k), np.int64)
    iso = np.zeros((k, k), np.int64)
    pure = np.zeros(k, np.int64)
    for row in Q:
        s = set(np.flatnonzero(row).tolist())
        if len(s) == 1:
            pure[next(iter(s))] += 1
        for a in range(k):
            for b in range(k):
                if b in s and a in s:
                    co[a, b] += 1
                if b in s and a not in s:
                    iso[a, b] += 1
    return co, iso, pure


def census(iso, pure, co):
    k = iso.shape[0]
    off = ~np.eye(k, dtype=bool)
    n_pairs = int(off.sum())
    u = (iso == 0) & off
    u_either = ((iso == 0) | (iso.T == 0)) & off
    u_pure = np.broadcast_to(pure[None, :] == 0, iso.shape) & off
    cot = (co > 0) & off
    return dict(ordered_pairs=n_pairs,
                U=int(u.sum()), U_share=u.sum() / n_pairs,
                U_either=int(u_either.sum()), U_either_share=u_either.sum() / n_pairs,
                U_pure=int(u_pure.sum()), U_pure_share=u_pure.sum() / n_pairs,
                cotagged=int(cot.sum()), cotagged_share=cot.sum() / n_pairs,
                U_within_cotagged=int((u & cot).sum()),
                U_share_within_cotagged=((u & cot).sum() / cot.sum()) if cot.sum() else None,
                units_without_pure_item=int((pure == 0).sum()), units=k)


# ----------------------------------------------------------------------------- time keys

_DT = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$")


class TimeKey:
    """Integer keys that reproduce EXACTLY the STRING order the atlas compares, for any format.

    Each distinct timestamp string is interned to a provisional id; `ranks()` then sorts the
    distinct strings with Python's own str sort and maps each id to its rank. Order between two
    rows is therefore the atlas's string comparison by construction, whatever the widths (XES3G5M
    mixes 12- and 13-digit times; ASSISTments mixes fractional-second widths: see CHANGES).
    `widths` counts the rows at each string length."""

    def __init__(self):
        self.ids = {}
        self.widths = defaultdict(int)
        self.kind = "string-rank"

    def __call__(self, s: str) -> int:
        self.widths[len(s)] += 1
        i = self.ids.get(s)
        if i is None:
            i = self.ids[s] = len(self.ids)
        return i

    def ranks(self):
        order = sorted(self.ids, key=lambda x: x)
        rank = np.empty(len(order), np.int64)
        for r, x in enumerate(order):
            rank[self.ids[x]] = r
        self.ids = None
        return rank


# ----------------------------------------------------------------------------- dense empirical replica

class Dense:
    """Per (learner, unit): first-touch time, outcome at first touch (False if any row at that
    instant is False, as the atlas's tuple sort gives), first-pass time. Built from integer arrays."""

    def __init__(self, L, U, T, OK, n_learners, units):
        nL, nU = n_learners, len(units)
        self.units = units
        self.nL, self.nU = nL, nU
        lin = L.astype(np.int64) * nU + U.astype(np.int64)
        tf = np.full(nL * nU, INF, np.int64)
        np.minimum.at(tf, lin, T)
        at_first = T == tf[lin]
        y = np.ones(nL * nU, np.int8)
        np.minimum.at(y, lin[at_first], OK[at_first].astype(np.int8))
        p = np.full(nL * nU, INF, np.int64)
        okm = OK.astype(bool)
        np.minimum.at(p, lin[okm], T[okm])
        self.Tf = tf.reshape(nL, nU)
        self.Y = y.reshape(nL, nU)
        self.P = p.reshape(nL, nU)
        self.touched = self.Tf < INF
        self.Y[~self.touched] = 0
        self.at = [np.flatnonzero(self.touched[:, j]) for j in range(nU)]

    def classify(self, a, b):
        Lb = self.at[b]
        tb = self.Tf[Lb, b]
        ta = self.Tf[Lb, a]
        yb = self.Y[Lb, b]
        never = ta >= tb
        mast = (~never) & (self.P[Lb, a] < tb)
        fail = (~never) & (~mast)
        return dict(n_m=int(mast.sum()), n_f=int(fail.sum()), n_n=int(never.sum()),
                    y_m=yb[mast], y_f=yb[fail])

    def falsifiable(self, a, b, min_cell=MIN_CELL, claimed=CLAIMED_EFFECT):
        """reachability.reachability for one pair, on the atlas's timelines (time = first pass if
        passed, else first touch)."""
        both = np.flatnonzero(self.touched[:, a] & self.touched[:, b])
        if not len(both):
            return False, 0
        passed = self.P[both] < INF
        tl = np.where(passed, self.P[both], self.Tf[both])
        after = np.maximum(tl[:, a], tl[:, b])
        stratum = np.where(passed[:, a], 0, 2) + np.where(passed[:, b], 0, 1)
        M = self.touched[both] & (tl > after[:, None])
        M[:, a] = False
        M[:, b] = False
        MP = M & passed
        cells = np.stack([M[stratum == s].sum(0) for s in range(4)])
        passes = np.stack([MP[stratum == s].sum(0) for s in range(4)])
        readable = cells.min(0) >= min_cell
        ok = False
        for c in np.flatnonzero(readable):
            v = cells[:, c]
            p_both = passes[0, c] / v[0] if v[0] else 0.0
            m = reach_mod._mde(int(v[0]), int(v[1:].min()), float(p_both))
            if m is not None and m <= claimed:
                ok = True
                break
        return ok, int(readable.sum())


def edge_states(dense, pairs_idx):
    """Atlas states per edge: (state, mde, observed). The reachability gate runs on would-be
    contradictions only, exactly as atlas.audit and positivity.main do."""
    out = []
    pre_contra = 0
    for a, b in pairs_idx:
        c = dense.classify(a, b)
        n_m, n_f = c["n_m"], c["n_f"]
        v = obs = None
        if n_m:
            p_m = float(np.mean(c["y_m"]))
            v = positivity.mde(n_m, n_f, p_m)
            if n_f:
                obs = p_m - float(np.mean(c["y_f"]))
        st = classify_edge(v, obs)[0]
        if st == CONTRADICTED:
            pre_contra += 1
            ok, _nodes = dense.falsifiable(a, b)
            st2 = classify_edge(v, obs, falsifiable=ok)[0]
            fine = "contradicted" if st2 == CONTRADICTED else "unfalsifiable"
        elif st == SUPPORTED:
            fine = "supported"
        elif v is None:
            fine = "unreadable"
        elif v > CLAIMED_EFFECT:
            fine = "unpowered"
        else:
            fine = "no_comparison"
        out.append((fine, v, obs))
    return out, pre_contra


# ----------------------------------------------------------------------------- cross-tab and verdicts

def wilson(k, n, z=1.959964):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, c - h), min(1.0, c + h))


def crosstab(design, states):
    """design: bool array (True = unidentified by design); states: list of fine states."""
    t = {lab: {s: 0 for s in STATES} for lab in ("unidentified", "identified")}
    for u, s in zip(design, states):
        t["unidentified" if u else "identified"][s] += 1
    return t


def overlap(design, states):
    d = np.asarray(design, bool)
    dec = np.array([s in DECIDED for s in states])
    und = ~dec
    sup = np.array([s == "supported" for s in states])
    n_ud = int((d & und).sum())
    n_dd = int((d & dec).sum())
    n_iu = int((~d & und).sum())
    n_id = int((~d & dec).sum())
    union = int((d | und).sum())
    return dict(U_and_undecided=n_ud, U_and_decided=n_dd, notU_and_undecided=n_iu,
                notU_and_decided=n_id, U=int(d.sum()), undecided=int(und.sum()),
                decided=int(dec.sum()), jaccard=(n_ud / union) if union else None,
                U_share_undecided=(n_ud / d.sum()) if d.sum() else None,
                f=(n_ud / und.sum()) if und.sum() else None,
                f_wilson=wilson(n_ud, int(und.sum())),
                p_decided_given_U=(n_dd / d.sum()) if d.sum() else None,
                p_decided_given_notU=(n_id / (~d).sum()) if (~d).sum() else None,
                d=((n_dd / d.sum()) - (n_id / (~d).sum())) if d.sum() and (~d).sum() else None,
                U_and_supported=int((d & sup).sum()), supported=int(sup.sum()),
                supported_U_share=((d & sup).sum() / sup.sum()) if sup.sum() else None)


def cluster_boot_f(design, states, groups, rng, n=N_BOOT):
    """Percentile 95% interval for f, resampling dependants B with replacement."""
    d = np.asarray(design, bool)
    und = np.array([s not in DECIDED for s in states])
    g = np.asarray(groups)
    ug, inv = np.unique(g, return_inverse=True)
    num = np.bincount(inv, weights=(d & und).astype(float), minlength=len(ug))
    den = np.bincount(inv, weights=und.astype(float), minlength=len(ug))
    vals = []
    for _ in range(n):
        pick = rng.integers(0, len(ug), len(ug))
        dd = den[pick].sum()
        if dd:
            vals.append(num[pick].sum() / dd)
    if not vals:
        return (None, None)
    return (float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5)))


def sattolo(idx, rng):
    """A uniformly random CYCLIC permutation of idx: no element stays in place (a derangement)."""
    p = list(idx)
    for i in range(len(p) - 1, 0, -1):
        j = int(rng.integers(0, i))
        p[i], p[j] = p[j], p[i]
    return p


def derangement_null(design, states, groups, rng, n=N_NULL):
    d = np.asarray(design, bool)
    dec = np.array([s in DECIDED for s in states])

    def stat(lab):
        if lab.sum() == 0 or (~lab).sum() == 0:
            return None
        return dec[lab].mean() - dec[~lab].mean()

    obs = stat(d)
    by = defaultdict(list)
    for i, g in enumerate(groups):
        by[g].append(i)
    singletons = sum(1 for v in by.values() if len(v) == 1)
    movable = [v for v in by.values() if len(v) > 1]
    null = []
    for _ in range(n):
        lab = d.copy()
        for v in movable:
            perm = sattolo(v, rng)
            lab[v] = d[perm]
        s = stat(lab)
        if s is not None:
            null.append(s)
    null = np.array(null)
    if obs is None or not len(null):
        return dict(d=obs, p_two_sided=None, p_one_sided_observed_direction=None,
                    null_mean=None, draws=len(null), singleton_dependants=singletons)
    p2 = (1 + int((np.abs(null) >= abs(obs) - 1e-12).sum())) / (1 + len(null))
    if obs >= 0:
        p1 = (1 + int((null >= obs - 1e-12).sum())) / (1 + len(null))
    else:
        p1 = (1 + int((null <= obs + 1e-12).sum())) / (1 + len(null))
    return dict(d=float(obs), p_two_sided=p2, p_one_sided_observed_direction=p1,
                null_mean=float(null.mean()), null_sd=float(null.std()), draws=len(null),
                singleton_dependants=singletons)


def verdict_f(f, upper):
    if f is None:
        return "UNANSWERABLE: no undecided edges"
    if f >= F_DESIGN:
        return ("DESIGN-LIMITED: most undecided edges are already unidentified by the item design; "
                "F1's limit is the Q-matrix, not only the learner order")
    if upper is not None and upper < F_LEARNER_UPPER:
        return ("LEARNER-ORDER-LIMITED: the design isolates B from A for almost every undecided "
                "edge; F1's limit is who reached B without A, not which items exist")
    return "MIXED: both limits bind; report the two shares side by side"


def verdict_overlap(ov):
    if ov["U"] == 0:
        return "NO DESIGN LIMIT"
    if ov["jaccard"] is not None and ov["jaccard"] >= JACCARD_SAME:
        return "SAME EDGES"
    if ov["U_share_undecided"] is not None and ov["U_share_undecided"] >= NESTED_SHARE:
        return "DESIGN NESTED IN LEARNER LIMIT"
    return "DIFFERENT EDGES"


def verdict_direction(dn):
    d, p = dn.get("d"), dn.get("p_two_sided")
    if d is None or p is None:
        return "NOT TESTABLE (U or not-U empty, or nothing to derange)"
    if d < 0 and p < P_DIR:
        return "SAME DIRECTION: design-unidentified edges are decided less often"
    if d > 0 and p < P_DIR:
        return ("CO-TAGGING ARTEFACT: design-unidentified edges are decided MORE often, possible only "
                "through co-tagged items")
    return "NO DETECTED ASSOCIATION beyond the dependant"


def verdict_supported(ov):
    s = ov["supported_U_share"]
    if s is None:
        return "NO SUPPORTED EDGES"
    if s >= SUPPORTED_FLAG:
        return "SUPPORTED COUNT CARRIES DESIGN-UNIDENTIFIED EDGES"
    return "SUPPORTED COUNT CLEAN OF DESIGN-UNIDENTIFIED EDGES (below 0.05)"


def analyse(design, states, groups, rng):
    ov = overlap(design, states)
    boot = cluster_boot_f(design, states, groups, rng)
    w = ov["f_wilson"]
    lo = min(x for x in (w[0], boot[0]) if x is not None) if (w[0] is not None or boot[0] is not None) else None
    hi = max(x for x in (w[1], boot[1]) if x is not None) if (w[1] is not None or boot[1] is not None) else None
    dn = derangement_null(design, states, groups, rng)
    return dict(crosstab=crosstab(design, states), overlap=ov, f_cluster_boot=boot,
                f_interval_conservative=(lo, hi), derangement=dn,
                verdict_f=verdict_f(ov["f"], hi), verdict_overlap=verdict_overlap(ov),
                verdict_direction=verdict_direction(dn), verdict_supported=verdict_supported(ov))


# ----------------------------------------------------------------------------- corpus loaders

class Rows:
    def __init__(self):
        self.L, self.U, self.T, self.OK = array("i"), array("i"), array("q"), array("b")
        self.learners = {}
        self.unit_names = {}
        self.item_units = defaultdict(set)
        self.tk = TimeKey()

    def unit(self, u):
        j = self.unit_names.get(u)
        if j is None:
            j = self.unit_names[u] = len(self.unit_names)
        return j

    def add(self, learner, unit, ok, t, item):
        li = self.learners.get(learner)
        if li is None:
            li = self.learners[learner] = len(self.learners)
        j = self.unit(unit)
        self.L.append(li)
        self.U.append(j)
        self.T.append(self.tk(t))
        self.OK.append(1 if ok else 0)
        self.item_units[item].add(j)

    def finish(self):
        """Re-index units in SORTED name order (the atlas's `items = sorted(idx)`)."""
        names = sorted(self.unit_names)
        remap = np.empty(len(names), np.int64)
        for new, nm in enumerate(names):
            remap[self.unit_names[nm]] = new
        L = np.frombuffer(self.L, dtype=np.int32).astype(np.int32)
        U = remap[np.frombuffer(self.U, dtype=np.int32)]
        T = self.tk.ranks()[np.frombuffer(self.T, dtype=np.int64)]
        OK = np.frombuffer(self.OK, dtype=np.int8).copy()
        items = sorted(self.item_units)
        Q = np.zeros((len(items), len(names)), bool)
        for r, it in enumerate(items):
            Q[r, [int(remap[j]) for j in self.item_units[it]]] = True
        del self.L, self.U, self.T, self.OK
        return names, L, U, T, OK, len(self.learners), items, Q


def load_xes3g5m():
    root = data_path("XES_DIR")
    attempts, routes = root / "attempts.tsv", root / "cid2route.json"
    known = {int(k) for k in json.loads(routes.read_text(encoding="utf-8"))}
    R = Rows()
    with attempts.open(encoding="utf-8") as fh:
        for line in fh:
            uid, q, c, r, t = line.rstrip("\n").split("\t")
            ok = r == "1"
            for part in c.split("_"):
                if (k := int(part)) in known:
                    R.add(uid, f"k{k}", ok, t, q)
    return R


def load_assist():
    R = Rows()
    with (data_path("ASSIST_DIR") / "assist_rich.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            s = r["skill_id"]
            if not s or s == "NA":
                continue
            R.add(r["user_id"], s, r["correct"] == "1", r["start_time"], r["problem_id"])
    return R


def load_eedi():
    from shared.corpus import Eedi
    answers = data_path("EEDI_ANSWERS")
    zip_path = data_path("EEDI_ZIP")
    # completeness: the file must end in a full row (it was being written when this study began)
    with open(answers, "rb") as fh:
        fh.seek(-4096, 2)
        tail = fh.read().split(b"\n")
    if tail[-1] != b"" or len(tail[-2].split(b"\t")) != 6:
        raise SystemExit("BLOCKED: eedi answers.tsv does not end in a complete row")
    E = Eedi(answers, zip_path)
    R = Rows()
    # the same loop as shared.corpus.Eedi.events(), with the QuestionId kept for the Q-matrix
    with open(answers, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for unit in E.leaves.get(r["QuestionId"], ()):
                R.add(r["UserId"], unit, float(r["IsCorrect"]) >= 0.5, r["DateAnswered"],
                      r["QuestionId"])
    return R


LOADERS = {"xes3g5m": load_xes3g5m, "assist": load_assist, "eedi": load_eedi}


def committed_row(name):
    if name == "assist":
        s = json.loads((REPO / "studies/identifiability/overlap/out/positivity-assist.json")
                       .read_text())["summary"]
        return dict(edges=s["edges"], readable=s["readable"], detect_20pt=s["detect_20pt"],
                    supported=s["edge_state"]["supported"],
                    contradicted=s["edge_state"]["contradicted"],
                    unknown=s["edge_state"]["unknown"], source="overlap/out/positivity-assist.json")
    for r in json.loads((REPO / "studies/identifiability/overlap/out/atlas.json").read_text()):
        if r.get("dataset") == name and "skipped" not in r:
            return dict(learners=r["learners"], items=r["items"], edges=r["edges"],
                        readable=r["readable"], detect_20pt=r["detect_20pt"],
                        supported=r["supported"], contradicted=r["contradicted"],
                        unknown=r["unknown"],
                        contradicted_before_reachability=r["contradicted_before_reachability"],
                        source="overlap/out/atlas.json")
    return None


def sample_pairs(name, units):
    if name == "assist":
        pairs = positivity.candidate_pairs(name, units, "all")
        if len(pairs) > 40000:
            rng = np.random.default_rng(0)
            pairs = [pairs[i] for i in rng.choice(len(pairs), 40000, replace=False)]
        return pairs
    pairs = atlas.candidate_pairs(name, units, "all")
    if len(pairs) > 20000:
        rng = atlas.corpus_rng(name)
        pairs = [pairs[i] for i in rng.choice(len(pairs), 20000, replace=False)]
    return pairs


def run_corpus(name):
    print(f"[{name}] loading", flush=True)
    R = LOADERS[name]()
    time_widths = dict(R.tk.widths)
    time_key = R.tk.kind
    units, L, U, T, OK, nL, items, Q = R.finish()
    del R
    print(f"[{name}] {nL:,} learners, {len(units):,} units, {len(items):,} items, "
          f"{len(T):,} unit-events", flush=True)
    co, iso, pure, nitems = design_counts(Q)
    cen = census(iso, pure, co)
    # qmatrix.py's C1-C4 on the same Q (reused, not re-implemented)
    import qmatrix
    c14 = qmatrix.check(name, {i: {units[j] for j in np.flatnonzero(Q[r])}
                               for r, i in enumerate(items)})
    dense = Dense(L, U, T, OK, nL, units)
    del L, U, T, OK
    pairs = sample_pairs(name, units)
    uix = {u: j for j, u in enumerate(units)}
    pidx = [(uix[a], uix[b]) for a, b in pairs]
    print(f"[{name}] {len(pidx):,} candidate edges; computing states", flush=True)
    st, pre_contra = edge_states(dense, pidx)
    states = [s for s, _v, _o in st]
    mdes = [v for _s, v, _o in st if v is not None]
    recomputed = dict(learners=nL, items=len(units), edges=len(pidx), readable=len(mdes),
                      detect_20pt=int(sum(1 for v in mdes if v <= 0.20)),
                      supported=states.count("supported"),
                      contradicted=states.count("contradicted"),
                      unknown=len(states) - states.count("supported") - states.count("contradicted"),
                      contradicted_before_reachability=pre_contra)
    comm = committed_row(name)
    match = None
    if comm:
        match = {k: (recomputed.get(k), comm[k], recomputed.get(k) == comm[k])
                 for k in comm if k != "source"}
    reproduced = bool(match) and all(v[2] for v in match.values())
    a_ = np.array([a for a, _b in pidx])
    b_ = np.array([b for _a, b in pidx])
    e_iso = iso[a_, b_]
    e_iso_rev = iso[b_, a_]
    e_pure = pure[b_]
    e_co = co[a_, b_]
    U_ = e_iso == 0
    Ue = U_ | (e_iso_rev == 0)
    Up = e_pure == 0
    cot = e_co > 0
    rng = np.random.default_rng(SEED)
    groups = b_.tolist()
    res = dict(
        corpus=name, kc_model=atlas.KC_MODEL.get(name, "ASSISTments 2012-13 skill_id"),
        learners=nL, units=len(units), items=len(items),
        items_per_unit_median=float(np.median(nitems)),
        units_per_item_mean=float(Q.sum(1).mean()),
        multi_unit_items=int((Q.sum(1) > 1).sum()),
        census=cen, qmatrix_conditions=c14,
        timestamps=dict(key=time_key, rows_by_width={str(k): v for k, v in sorted(time_widths.items())}),
        reproduction=dict(recomputed=recomputed, committed=comm, fields=match,
                          reproduced_exactly=reproduced,
                          label=("against the committed atlas" if reproduced
                                 else "against a RECOMPUTED atlas, not the committed one")),
        sample=dict(edges=len(pidx), U=int(U_.sum()), U_wilson=wilson(int(U_.sum()), len(pidx)),
                    U_either=int(Ue.sum()), U_pure=int(Up.sum()), cotagged=int(cot.sum()),
                    states={s: states.count(s) for s in STATES}),
        primary_U=analyse(U_, states, groups, rng),
        secondary_U_either=analyse(Ue, states, groups, rng),
        secondary_U_pure=analyse(Up, states, groups, rng),
    )
    if cot.sum():
        sub = np.flatnonzero(cot)
        res["cotagged_subset_U"] = analyse(U_[sub], [states[i] for i in sub],
                                           [groups[i] for i in sub], rng)
    else:
        res["cotagged_subset_U"] = None
    out = HERE / "out" / f"{name}.json"
    out.write_text(json.dumps(res, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n")
    p = res["primary_U"]
    print(f"[{name}] census U share {cen['U_share']:.6f}; sample U {res['sample']['U']}; "
          f"f {p['overlap']['f']}; {p['verdict_f']}", flush=True)
    print(f"[{name}] reproduction: {res['reproduction']['label']}", flush=True)
    print(f"   -> {out}")
    return res


# ----------------------------------------------------------------------------- floor

def floor():
    rng = np.random.default_rng(SEED)
    checks = {}

    # F1 Gu & Xu's toy
    Q = np.array([[1, 0], [1, 1], [1, 1]], bool)
    co, iso, pure, _n = design_counts(Q)
    checks["F1_toy"] = bool(iso[0, 1] == 0 and pure[1] == 0 and iso[1, 0] == 1 and pure[0] == 1)

    # F2 random Q with planted structure
    K, NI = 200, 500
    Q = np.zeros((NI, K), bool)
    for r in range(NI):
        Q[r, rng.choice(K, int(rng.integers(1, 5)), replace=False)] = True
    planted_u, planted_iso = [], []
    pairs_all = [(a, b) for a in range(K) for b in range(K) if a != b]
    order = rng.permutation(len(pairs_all))
    used = set()
    for i in order:
        a, b = pairs_all[i]
        if len(planted_u) < 40 and a not in used and b not in used:
            Q[Q[:, b], a] = True           # every item carrying b now carries a
            planted_u.append((a, b))
            used.update((a, b))
    for i in order[::-1]:
        a, b = pairs_all[i]
        if len(planted_iso) < 40 and a not in used and b not in used:
            planted_iso.append((a, b))
            used.update((a, b))
    extra = np.zeros((len(planted_iso), K), bool)
    for r, (_a, b) in enumerate(planted_iso):
        extra[r, b] = True
    Q = np.vstack([Q, extra])
    co, iso, pure, _n = design_counts(Q)
    co2, iso2, pure2 = design_counts_bruteforce(Q)
    off = ~np.eye(K, dtype=bool)
    checks["F2_exact_co"] = bool((co[off] == co2[off]).all())
    checks["F2_exact_iso_BnotA"] = bool((iso[off] == iso2[off]).all())
    checks["F2_exact_iso_AnotB"] = bool((iso.T[off] == iso2.T[off]).all())
    checks["F2_exact_pure"] = bool((pure == pure2).all())
    checks["F2_planted_unidentified_recovered"] = all(iso[a, b] == 0 for a, b in planted_u)
    checks["F2_planted_isolating_recovered"] = all(iso[a, b] >= 1 and pure[b] >= 1
                                                   for a, b in planted_iso)
    cen = census(iso, pure, co)
    bf_u = sum(1 for a, b in pairs_all if iso2[a, b] == 0)
    checks["F2_census_exact"] = cen["U"] == bf_u
    checks["F2_planted_40_and_40"] = len(planted_u) == 40 and len(planted_iso) == 40
    f2_counts = dict(ordered_pairs=len(pairs_all), planted_unidentified=len(planted_u),
                     planted_isolating=len(planted_iso), census_U=cen["U"], bruteforce_U=bf_u)

    # F3 Q builder from a shuffled row stream with duplicates
    units = [f"u{j:02d}" for j in range(K)]
    stream = []
    for r in range(Q.shape[0]):
        for _rep in range(int(rng.integers(1, 4))):
            for j in np.flatnonzero(Q[r]):
                stream.append((f"item{r:04d}", units[j]))
    stream = [stream[i] for i in rng.permutation(len(stream))]
    _items, Q3 = q_from_stream(stream, units)
    checks["F3_stream_rebuild"] = bool(Q3.shape == Q.shape and (Q3 == Q).all())

    # F4 dense replica against the atlas's own functions
    checks["F4_replica_equal"], f4 = _floor_replica(rng)

    # F5 cross-tab and verdict branches
    lab = np.array([1, 1, 0, 0, 0, 1, 0, 0], bool)
    sts = ["unreadable", "supported", "supported", "unpowered", "contradicted",
           "unreadable", "unfalsifiable", "unreadable"]
    ov = overlap(lab, sts)
    ok5 = (ov["U_and_undecided"] == 2 and ov["U_and_decided"] == 1 and
           ov["notU_and_undecided"] == 3 and ov["notU_and_decided"] == 2 and
           abs(ov["f"] - 2 / 5) < 1e-12 and ov["U_and_supported"] == 1 and ov["supported"] == 2)
    ok5 = ok5 and verdict_f(0.6, 0.7).startswith("DESIGN-LIMITED")
    ok5 = ok5 and verdict_f(0.01, 0.03).startswith("LEARNER-ORDER-LIMITED")
    ok5 = ok5 and verdict_f(0.10, 0.2).startswith("MIXED")
    ok5 = ok5 and verdict_overlap(dict(U=0, jaccard=None, U_share_undecided=None)) == "NO DESIGN LIMIT"
    ok5 = ok5 and verdict_overlap(dict(U=5, jaccard=0.6, U_share_undecided=1.0)) == "SAME EDGES"
    ok5 = ok5 and verdict_overlap(dict(U=5, jaccard=0.01, U_share_undecided=0.95)).startswith("DESIGN NESTED")
    ok5 = ok5 and verdict_overlap(dict(U=5, jaccard=0.01, U_share_undecided=0.5)) == "DIFFERENT EDGES"
    ok5 = ok5 and verdict_direction(dict(d=-0.2, p_two_sided=0.01)).startswith("SAME DIRECTION")
    ok5 = ok5 and verdict_direction(dict(d=0.2, p_two_sided=0.01)).startswith("CO-TAGGING")
    ok5 = ok5 and verdict_direction(dict(d=0.2, p_two_sided=0.4)).startswith("NO DETECTED")
    # the derangement leaves no label in place
    p = sattolo(list(range(10)), rng)
    ok5 = ok5 and all(p[i] != i for i in range(10)) and sorted(p) == list(range(10))
    checks["F5_crosstab_and_verdicts"] = bool(ok5)

    # F6 string-order keys on mixed widths
    tk = TimeKey()
    strs = ([str(int(x)) for x in rng.integers(10**10, 10**14, 3000)]
            + ["1595229836000", "159522983600", "99", "1", "10", "100",
               "2012-09-04 16:28:52.97775", "2012-09-04 16:28:52.9", "2012-09-04 16:28:52",
               "2012-09-04 16:28:52.977", "2012-09-04 16:28:53"])
    ids = [tk(x) for x in strs]
    rk = tk.ranks()
    keys = [int(rk[i]) for i in ids]
    checks["F6_timekey_string_order"] = (
        [x for _k, x in sorted(zip(keys, strs))] == sorted(strs)
        and all((keys[i] < keys[j]) == (strs[i] < strs[j])
                for i in range(len(strs) - 11, len(strs)) for j in range(len(strs) - 11, len(strs))))

    passed = all(checks.values())
    res = dict(passed=passed, checks=checks, F2=f2_counts, F4=f4,
               verdict=("FLOOR PASSED: the counter is exact and the replica equals the atlas"
                        if passed else "FLOOR FAILED: every real verdict is UNANSWERABLE"))
    (HERE / "out" / "floor.json").write_text(json.dumps(res, indent=1) + "\n")
    for k, v in checks.items():
        print(f"   {k:<40} {'PASS' if v else 'FAIL'}")
    print(f"   -> {res['verdict']}")
    return passed


def _floor_replica(rng):
    """Synthetic corpus: 6,000 learners, 15 units over 30 items (15 single-unit, 15 with 1-3 units), 13-digit string
    times with ties. Two learner populations so every branch occurs: free practice (repeated,
    mostly correct -- supported and unreadable pairs) and a one-shot pass through the items in a
    near-fixed order (balanced pass/fail strata and later merge nodes -- powered nulls that the
    gate can find falsifiable). Units 0-6 load on ability; the rest are coin flips. The dense
    replica must agree with positivity.classify/mde, classify_edge and reachability.reachability on
    every ordered pair."""
    nU, nI, nL = 15, 30, 6000
    units = [f"k{j}" for j in range(nU)]
    # items 0-14 measure unit i alone, in order, so the one-shot pass meets units sequentially and
    # later units can serve as merge nodes; items 15-29 carry 1-3 random units
    item_units = [np.array([i]) if i < nU else rng.choice(nU, int(rng.integers(1, 4)), replace=False)
                  for i in range(nI)]
    R = Rows()
    rows = []

    def p_ok(it, ability):
        js = item_units[it]
        if all(j < 7 for j in js):
            return 1 / (1 + math.exp(-(1.5 * ability)))
        return 0.5

    for li in range(nL):
        ability = rng.normal()
        start = 1_595_000_000_000 + int(rng.integers(0, 10**9))
        if li % 2 == 0:
            seq = [int(rng.integers(0, nI)) if rng.random() < 0.7 else int(min(nI - 1, k))
                   for k in range(int(rng.integers(5, 60)))]
        else:
            seq = list(range(nI))
            for _sw in range(3):
                i = int(rng.integers(0, nI - 1))
                seq[i], seq[i + 1] = seq[i + 1], seq[i]
        for k, it in enumerate(seq):
            t = start + k * 1000 * int(rng.integers(0, 2)) + int(rng.integers(0, 2)) * 1000
            ok = bool(rng.random() < p_ok(it, ability))
            for j in item_units[it]:
                rows.append((f"L{li}", units[j], ok, str(t), False, False))
                R.add(f"L{li}", units[j], ok, str(t), f"i{it}")
    names, L, U, T, OK, n_learners, _items, _Q = R.finish()
    dense = Dense(L, U, T, OK, n_learners, names)
    by_learner = positivity.timelines(rows)
    ft, fp, oat = positivity.states(by_learner)
    idx = positivity.at_item(ft, oat)
    pairs = [(a, b) for a in names for b in names if a != b]
    uix = {u: j for j, u in enumerate(names)}
    tl = {learner: {u: ((fpl[u], True) if u in fpl else (t, False)) for u, t in ft[learner].items()}
          for learner, fpl in fp.items()}
    ref_reach = reach_mod.reachability(tl, pairs, min_cell=MIN_CELL, claimed=CLAIMED_EFFECT)
    mism = 0
    n_states = defaultdict(int)
    n_fals = 0
    for a, b in pairs:
        c = positivity.classify((a, b), ft, fp, oat, idx)
        n_m, n_f, n_n = len(c["mastered"]), len(c["failed"]), len(c["never"])
        v = obs = None
        if n_m:
            p_m = float(np.mean(c["mastered"]))
            v = positivity.mde(n_m, n_f, p_m)
            if n_f:
                obs = p_m - float(np.mean(c["failed"]))
        ref_state = classify_edge(v, obs)[0]
        ref_ok = ref_reach[(a, b)]["status"] == "FALSIFIABLE"
        d = dense.classify(uix[a], uix[b])
        dv = dobs = None
        if d["n_m"]:
            dp = float(np.mean(d["y_m"]))
            dv = positivity.mde(d["n_m"], d["n_f"], dp)
            if d["n_f"]:
                dobs = dp - float(np.mean(d["y_f"]))
        dok, _ = dense.falsifiable(uix[a], uix[b])
        same = ((n_m, n_f, n_n) == (d["n_m"], d["n_f"], d["n_n"]) and v == dv and obs == dobs
                and ref_state == classify_edge(dv, dobs)[0] and ref_ok == dok)
        mism += not same
        n_states[ref_state] += 1
        n_fals += ref_ok
    branches = (n_states[SUPPORTED] > 0 and n_states[CONTRADICTED] > 0 and n_fals > 0)
    return mism == 0 and branches, dict(pairs=len(pairs), mismatches=mism, states=dict(n_states),
                                        falsifiable_pairs=n_fals, all_branches_seen=branches)


# ----------------------------------------------------------------------------- summary

def summary():
    rows = {}
    for name in ("xes3g5m", "assist", "eedi"):
        p = HERE / "out" / f"{name}.json"
        if not p.exists():
            rows[name] = dict(status="BLOCKED or not run")
            continue
        r = json.loads(p.read_text())
        pu = r["primary_U"]
        rows[name] = dict(
            census_U_share=r["census"]["U_share"], census_U_pure_share=r["census"]["U_pure_share"],
            sample_edges=r["sample"]["edges"], sample_U=r["sample"]["U"],
            decided=pu["overlap"]["decided"], undecided=pu["overlap"]["undecided"],
            f=pu["overlap"]["f"], f_interval=pu["f_interval_conservative"],
            d=pu["derangement"]["d"], d_p=pu["derangement"]["p_two_sided"],
            verdict_f=pu["verdict_f"], verdict_overlap=pu["verdict_overlap"],
            verdict_direction=pu["verdict_direction"], verdict_supported=pu["verdict_supported"],
            strict_pure_verdict_f=r["secondary_U_pure"]["verdict_f"],
            reproduction=r["reproduction"]["label"])
    floor_ok = json.loads((HERE / "out/floor.json").read_text())["passed"]
    out = dict(floor_passed=floor_ok, corpora=rows)
    (HERE / "out/summary.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def main():
    argv = sys.argv[1:]
    (HERE / "out").mkdir(exist_ok=True)
    if "--floor" in argv:
        sys.exit(0 if floor() else 1)
    if "--corpus" in argv:
        fl = HERE / "out/floor.json"
        if not fl.exists() or not json.loads(fl.read_text())["passed"]:
            sys.exit("the floor has not passed: real verdicts are UNANSWERABLE; run --floor first")
        run_corpus(argv[argv.index("--corpus") + 1])
        return
    if "--summary" in argv:
        summary()
        return
    print(__doc__)


if __name__ == "__main__":
    main()
