"""
Why are candidate edges whose two skills share an item decided far more often by the positivity
atlas -- the shared item itself (mechanical), or learners who really meet B without A more often
on those pairs (substantive)?

PRE-REGISTRATION. Written 2026-10-07, before any number in this file was computed on real data.
Requested by the maintainer (2026-10-07); procedure: scratchpad analyses/BRIEF.md, steps 1-2.

## Question and what is already known

`studies/identifiability/qmatrix-positivity/` reported, as an EXPLORATORY observation that was NOT
pre-registered, that candidate edges A -> B whose skills share at least one item ("co-tagged",
"shared-item edges") are decided (supported or contradicted) by the positivity atlas far more often
than the rest: on the atlas's 20,000-edge sample, 275 of 427 (64%) against 25.4% on Eedi and 11 of
39 (28%) against 4.0% on XES3G5M. Those are the only real numbers this design has seen.

How the atlas turns item responses into per-skill events (`studies/identifiability/overlap/
atlas.py` xes3g5m_rows / eedi_rows; `shared/corpus.Eedi`): a response to an item tagged with skills
{A, B} is one event on A AND one event on B, with the same time and the same outcome. Per edge the
atlas (`positivity.classify`) splits the learners who reached B, at their FIRST B event, into
MASTERED (a correct A event strictly earlier), FAILED (A events strictly earlier, none correct) and
NEVER (no A event strictly earlier: ties go here); the MDE (`positivity.mde`), the state
(`shared/edge_state.classify_edge`) and the merge-node gate (`shared/reachability.py`) follow.

So a shared item can move an edge's state without any property of the learners changing:
  (m1) COVERAGE. A learner who answers a shared item is a co-attempter of A and B, so the pool the
       cells are drawn from grows.
  (m2) ORDER AND TIES. A shared response is a B event during practice on A (or the reverse). It can
       become B's first touch, which moves the cut point tb; when it is also A's first touch the
       learner is a tie and falls into NEVER.
  (m3) OUTCOME. B's outcome at first touch is read on an item that ALSO requires A (an item needing
       all its skills: Pardos, Beck, Ruiz & Heffernan 2008, "the composition effect", literature
       review entry 2.13 and synthesis row 6). A learner who failed A then fails the shared item
       whatever their B, so the drop is there by construction and the edge reads SUPPORTED.
Against these, the substantive reading (2): co-tagged skills are taught and practised together, so
learners genuinely meet B without A more often (or less often), and the decided share reflects real
positivity. Positivity framing: literature review strand 2c; Gu & Xu (2024, Statistica Sinica,
doi:10.5705/ss.202021.0350), entry 1.1, which `qmatrix-positivity` already tested at design level.

## Data (reads two licensed corpora; aggregates only leave this script)

  XES3G5M  $XES_DIR/attempts.tsv + cid2route.json, read exactly as atlas.xes3g5m_rows reads them
           (and as qmatrix_positivity.load_xes3g5m does), keeping the question id per event.
           TAL research release; no redistribution.
  Eedi     $EEDI_ANSWERS (answers.tsv) + $EEDI_ZIP (subject tree), through shared.corpus.Eedi's
           level-3 leaf map, keeping QuestionId per event. Research use confirmed with Eedi; no
           redistribution. LIMITATION carried from the atlas: Eedi keeps each learner's LATEST answer
           per question and DateAnswered is minute-resolution, so "order" is last-answer order and
           many ties are not caused by shared items at all.
  ASSISTments 2012-13 is EXCLUDED: every problem carries exactly one skill (qmatrix-positivity:
           units per item 1.00, the Q-matrix is a partition), so it has no shared-item edge and the
           question does not arise there.
  Nothing is derived to disk. No learner-level row, item text or skill name leaves the script.

The item-to-skill tagging (the "coder" of the shared-item construct) is the platform's own: TAL's
KC routes and Eedi's subject tree. It is not validated here against an independent coder, and it
does not need to be for this question, which is what the atlas does WITH that tagging.

## Populations

  TREATED  every ordered pair (A, B), A != B, of units any learner touched, whose skills share at
           least one item (co[A,B] >= 1): the census, not the atlas's sample (the sample is a
           uniform draw from the same population; the census gives 1,528 edges on XES3G5M and
           1,986 on Eedi instead of 39 and 427). The atlas-sample subset is reported beside it as
           the reproduction of qmatrix-positivity's 28% / 64%.
  BASELINE the atlas's 20,000-edge sample (atlas.corpus_rng, exactly as qmatrix-positivity draws it),
           non-shared edges only. Its per-edge states are recomputed and the aggregates checked
           against the committed atlas row (reproduction gate, below).
  CONTROLS non-shared edges (co = 0) into the SAME dependant B (family = dependant: B's items,
           reach and difficulty are held fixed), from the whole census, not only the sample.

## Handling the shared responses (the stated rules)

  EXCL (primary)  for edge A -> B, every response to an item tagged with both A and B is removed
                  from A's event stream AND from B's. Other units' streams are untouched, so merge
                  nodes in the reachability gate keep their events (a shared item {A, B, C} stays a
                  C event). Under EXCL, B's outcome comes only from items not tagged A and A's
                  history only from items not tagged B.
  TO_A (secondary) the shared response is attributed to A only (removed from B's stream).
  TO_B (secondary) attributed to B only (removed from A's stream). Note, derived before any data:
                  A events strictly before tb can never be shared items (a shared item before tb
                  would itself be a B event, so tb would be no later), so TO_B can change a
                  learner's cell only through ties; it is expected to be nearly a no-op and is the
                  rule's own check.

## Estimand

D(X) = share of a set X of edges that is decided. With T the treated edges:
  g0     D(T, raw) - D(baseline)                       the gap to be explained (the observation)
  gE     D(T, EXCL) - D(baseline)                      exclusion only
  gM     D(T, raw) - D(M controls, raw)                coverage and difficulty matching only
  gEM    D(T, EXCL) - D(EM controls, raw)              PRIMARY: exclusion AND matching, with the
                                                       controls matched on the treated edge's
                                                       post-exclusion coverage and difficulty
  gES    D(T, EXCL) - D(M controls, sized removal)     robustness: data loss equalised by removal
  share explained = 1 - gEM / g0.
gM and gEM are computed on the matched treated subset; g0 and gE on all treated edges.

Matching covariates (per edge, over the learners who touched both A and B under the stage's
handling; computed by matrix products for the control pool and per edge for the treated):
  x1 log(1 + n_both)                 coverage: learners attempting both
  x2 log(attempts per such learner on A and B)
  x3 first-touch correctness on B among them   (difficulty of B)
  x4 first-touch correctness on A among them   (difficulty of A)
Each standardised by its SD over the control pool (all non-shared edges into treated dependants).
Rule: treated edges in a seeded random order; each takes the nearest control into the same B
(Euclidean on the standardised covariates) whose every covariate is within 0.5 SD (caliper);
1:1, WITH replacement (a control may serve several treated edges; the bootstrap resamples
dependants, so repeated controls stay inside their cluster). An edge with n_both < 10 cannot be readable (it cannot hold
5 + 5 learners) and is matched on x1 alone to a control that also has n_both < 10. Unmatched treated
edges are dropped from that stage and counted. Balance is reported as standardised mean differences.

## Controls

  * FAMILY-MATCHED: each control shares its treated edge's dependant B (above).
  * SIZED LIKE THE TREATMENT (CLAUDE.md; shared/controls.py). EXCL removes data, and an edge with
    less data is decided less often whatever the mechanism. So each M control gets a SIZED REMOVAL:
    whole items of B (random, any of B's items) and of A' (random) are removed until the share of
    B's events and of A''s events removed is as close as possible to the share EXCL removed from
    B and A on the treated edge. Removal is by whole items, the unit EXCL removes. The sizes are
    checked with shared.controls.check_control_scale (control median >= 0.5 x treatment median)
    and their ratio distribution is reported. Delta_T = D(T raw) - D(T EXCL) is then read against
    Delta_C = D(M raw) - D(M sized): the exclusion effect beyond data loss is Delta_T - Delta_C.
  * REPRODUCTION GATE (artefact check, "an artefact that parses ..."). The per-edge engine with no
    removal must equal qmatrix_positivity.Dense / edge_states on every edge (the replica that
    qmatrix-positivity's floor proved equal to positivity.classify, mde, classify_edge and
    reachability); EXCL must equal the atlas's own functions run on a row stream rebuilt without the
    shared responses; the pool covariates by matrix product must equal the per-edge ones. On real
    data, the recomputed baseline aggregates must equal the committed atlas row (atlas.json); a
    mismatch is reported and the results are labelled as against a recomputed atlas.
  * No permutation null is used. Inference is a cluster bootstrap over dependants B (1,000 draws):
    B is the unit shared by a treated edge and its controls, and edges into one B share B's items
    and learners. The interval resamples dependants, not learners or items.

## Mechanism descriptives (reported, not verdicts)

Over treated edges, raw vs EXCL: mean n_mastered, n_failed, n_never; the share of B-reachers whose
first B event is a shared item; the share of B-reachers tied (first A event at tb); the share of
co-attempters who co-attempt only through shared items; and the 4 x 4 transition of learners between
cells (mastered, failed, never, absent from B) summed over edges. The substantive diagnostic is the
FAILED-cell share n_f / (n_m + n_f + n_n) for T (EXCL) against the EM controls, signed.

## Synthetic detection floor (run before real data; a failure makes every verdict UNANSWERABLE)

Exactness (deterministic; "exact" is the only pass), on synthetic worlds:
  X1  per-edge engine with no removal == qmatrix_positivity.edge_states on every ordered pair
      (columns, MDE, observed drop, state) of a small world AND of all four discrimination worlds
      (39,600 pairs), and every state branch (supported, contradicted, unfalsifiable, unpowered,
      unreadable) occurs;
  X2  EXCL on 40 shared edges == positivity.classify / mde / classify_edge / reachability run on a row
      stream rebuilt without those responses (cells, MDE, state, falsifiability);
  X3  matrix covariates == per-edge covariates on every pair with n_both >= 1.
Discrimination (the point of the floor), on two kinds of world, two seeds each. 100 skills with
4-12 own items, 100 random skill pairs given one shared item each (200 ordered shared edges; about a
fifth of a skill's items are shared), 20,000 learners, each visiting 37 skills drawn by a
skill-popularity weight (lognormal) in random order. No true prerequisite anywhere: mastery of each
skill is drawn from a general ability (P = logistic(2 theta + skill offset), offsets for P 0.30-0.80),
so failing A predicts failing B through ability alone, as in real corpora; own-item correctness
0.85 if mastered, else 0.25. A visit is a mastery loop: items from the skill's pool (shared items
included) until a correct own item, 3-8 attempts by skill; a failed loop is remediated with up to two
more loops before the learner moves on.
  W-MECH  shared items are CONJUNCTIVE (0.85 only if both skills are mastered, else 0.25). The shared
          item is the only thing that differs between shared and non-shared pairs: it adds
          co-attempters (m1), B events inside A's practice (m2) and a drop by construction (m3).
          Expected: g0 > 0; MECHANICAL.
  W-SUBST shared items measure general ability only (0.25 + 0.6 logistic(2 theta)), not either skill
          in particular. Shared pairs are TAUGHT TOGETHER: when both are selected, the partner is
          visited right after the skill, and a failed loop on the skill is remediated only after
          the partner, so learners who failed A go on to B: a REAL positivity difference, at the
          same coverage. The shared items still add coverage and ties (m1, m2), so W-SUBST holds a
          planted substantive remainder ON TOP of a mechanical part. Expected: g0 > 0; a same-sign
          remainder survives (SUBSTANTIVE or MIXED, depending on how large the mechanical part is).
  Pass: both W-MECH runs return MECHANICAL and both W-SUBST runs return SUBSTANTIVE or MIXED; X1-X3
  exact. W-MECH's raw lean must be LEANS SUPPORTED (the lean instrument's own check: if only that
  part fails, the lean verdict alone is UNANSWERABLE).

## Pre-registered verdicts (per corpus; thresholds fixed here)

Let s = sign(g0); r = s * gEM with its 95% cluster-bootstrap interval [lo, hi]; G = s * g0.
  floor failed                                         UNANSWERABLE: the floor failed
  g0's interval contains 0                             UNANSWERABLE: NO GAP TO EXPLAIN
  fewer than 30 treated edges matched in EM            UNANSWERABLE: TOO FEW MATCHED EDGES
  more than 50% of treated edges unmatched in EM       UNANSWERABLE: NO COMMON SUPPORT
  lo <= 0 <= hi and hi < 0.5 G                         MECHANICAL: the gap vanishes once shared-item
                                                       responses are excluded and coverage and
                                                       difficulty are matched
  lo > 0 and r >= 0.5 G                                SUBSTANTIVE: the gap survives exclusion and
                                                       matching with the same sign
  lo > 0 and r < 0.5 G                                 MIXED: part of the gap is mechanical, a
                                                       same-sign remainder survives
  hi < 0                                               REVERSED: once handled, shared-item edges
                                                       are decided LESS often than matched controls
  lo <= 0 <= hi and hi >= 0.5 G                        UNANSWERABLE: UNDERPOWERED (the remainder can
                                                       be neither excluded nor bounded below half)
Lean among decided edges, signed: L = P(supported | decided, T) - P(supported | decided, control),
raw (T raw vs baseline) and EM (T EXCL vs EM controls), with the same bootstrap:
  lower bound > 0   LEANS SUPPORTED;  upper bound < 0   LEANS CONTRADICTED;  else   NO DETECTED LEAN.
gE, gM, gES, Delta_T - Delta_C, TO_A and TO_B are reported beside the verdict and do not change it;
if gES and gEM fall in different verdict classes, the README says so.

## What each verdict means for Paper II F1 (pre-registered)

  MECHANICAL: co-tagged edges' high decided share is an artefact of how the atlas maps multi-skill
    items to skill events; F1's decided shares should be footnoted that co-tagged edges are decided
    partly by their shared items, and supported co-tagged edges should not be counted as evidence of
    an edge unless they survive EXCL.
  SUBSTANTIVE: co-tagged skills are a curriculum stratum with genuinely different positivity; F1 can
    report it as such (with the sign of the failed-cell difference).
  MIXED: both statements, with the share explained.
  A raw LEANS SUPPORTED that vanishes under EXCL is the composition effect (m3) inflating F1's
    supported count; the count of supported co-tagged edges that do not survive EXCL is reported.

## What this can and cannot say

It can say how much of the co-tagged edges' decided-share gap is reproduced by how shared responses
enter the atlas and by coverage and difficulty, and what remains. It cannot say the remainder is
substantive: matching is on four observed covariates, and anything else that differs between
co-tagged and other pairs (content area, curriculum position) is in the remainder too. Matching on
coverage also absorbs any real "taught together" difference that acts only through coverage; that
is a choice of the brief (coverage counts as mechanical), stated here. The atlas's states are used
as defined; this study does not ask whether they are right. Eedi's order is last-answer order. It
says nothing about direction, conjunction between prerequisites, or lag.

## Machine budget

OMP/OPENBLAS/MKL threads 1. Eedi's dense learner x unit arrays (as in qmatrix-positivity) are about
0.7 GB; the sorted event arrays about 0.3 GB; the pool covariates are accumulated by learner chunks.
1,000 bootstrap draws (statistics are sums per dependant; cheap).

    python3 shared_item_edges.py --floor
    python3 shared_item_edges.py --corpus xes3g5m|eedi       (each writes out/<corpus>.json)
    python3 shared_item_edges.py --summary                   (out/summary.json)

## Coverage-only world (added 2026-10-09 at the maintainer's request; PRE-REGISTERED here, before it ran)

WHY. The real decomposition (out/summary.json, read before this section was written) has one shape on
both corpora: excluding the shared responses leaves most of the gap (gE close to g0), and matching on
coverage and difficulty closes it (gM and gEM near 0). Paper II reads that as "the gap is coverage":
co-tagged skills are attempted by more of the same learners. Neither floor world plants that: W-MECH's
gap comes from the shared item itself (exclusion removes it, gE near 0), and W-SUBST's survives
matching. So the reading was never tested. This section adds the missing world and asks whether
coverage alone produces the real shape, and whether the other two worlds do not.

  W-COVER  as W-SUBST's shared items (they measure general ability only, neither skill), but no
           teaching together: visits are in random order and remediation is immediate, as in W-MECH.
           What differs is COVERAGE only: after the usual draw of skills, each skill whose shared
           partner was not drawn adds that partner with probability COVER_P = 0.8, so learners who
           attempt one skill of a shared pair usually attempt both. Seeds 1 and 2, every other
           setting as the floor's discrimination worlds.

THE COVERAGE SHAPE, written from the real result's shape and fixed here: with G = g0's point,
  C1  g0's interval excludes 0 (lo > 0);
  C2  exclusion leaves most of the gap: gE's point >= 0.5 G and gE's lower bound > 0;
  C3  matching closes it: gM's interval contains 0 and its upper bound < 0.5 G.

PASS RULE (both conditions):
  P1  both W-COVER seeds show C1, C2 and C3, and the primary verdict (gEM) is MECHANICAL on both;
  P2  neither W-MECH seed nor W-SUBST seed shows C2 and C3 together (read from the committed
      out/floor.json, which this section does not rewrite).
Verdicts:
  P1 and P2   COVERAGE FLOOR PASSED: a coverage-only gap is closed by matching and not by exclusion,
              and neither other world has that shape
  otherwise   COVERAGE FLOOR FAILED: attributing the gap to coverage stays a reading of the
              decomposition
Then, per real corpus (descriptive, from out/summary.json, no new real computation):
  floor passed and C1-C3 hold   COVERAGE SHAPE: the corpus's gap has the shape coverage alone produces
                                (the corpus's own registered gEM verdict, MECHANICAL or MIXED, stands
                                beside it unchanged; it was seen before this section was written)
  floor passed, shape absent    NOT THE COVERAGE SHAPE
  floor failed                  UNANSWERABLE: the coverage floor failed
What a pass does not show: that coverage is the only process that could give this shape; only that
coverage alone gives it, and the two other planted mechanisms do not.

    python3 shared_item_edges.py --coverage-floor        (out/coverage-floor.json)

## CHANGES

2026-10-07, before the design commit and before any real data was read: the synthetic fixture was
iterated four times, the instrument and every threshold except the caliper unchanged. (1) The first
worlds were homogeneous (every skill alike), so covariate SDs were tiny and the within-dependant
caliper of 0.25 SD matched 1-2% of treated edges; skills were made heterogeneous (item count,
mastery rate, popularity, loop length) and the world enlarged to 100 skills so each dependant has
enough candidates. The caliper was widened to 0.5 SD and matching made with replacement; at 0.25 SD
without replacement the EM stage still left 62% of W-MECH's edges unmatched (NO COMMON SUPPORT).
(2) With no general ability, no edge anywhere showed a drop, so "decided" could only mean a
gate-surviving powered null and both worlds were near 0% decided; a general ability factor was
added, as real corpora have. (3) The first W-SUBST (interleaved blocks whenever both partners were
selected, uninformative coin-flip shared items) put most visits into blocks and made failed-A
learners uninformative about ability, so it decided nothing; it was replaced by the taught-together
rule above. (4) Shared items were cut from two per pair to one, so about a fifth rather than two
fifths of a skill's items are shared. On the last fixture W-MECH seeds 1-2 read MECHANICAL and
W-SUBST seeds 1-2 MIXED (this is what fixed the W-SUBST pass rule at SUBSTANTIVE or MIXED: the world
carries the shared items' coverage and ties as well as the planted positivity). The full floor is
re-run after this commit and is what gates the real run.
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from array import array  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "studies/identifiability/overlap"))
sys.path.insert(0, str(REPO / "studies/identifiability/qmatrix-positivity"))
sys.path.insert(0, str(REPO / "studies/identifiability/identifiability"))

import positivity  # noqa: E402
import qmatrix_positivity as qp  # noqa: E402
from shared import reachability as reach_mod  # noqa: E402
from shared.controls import check_control_scale  # noqa: E402
from shared.edge_state import (CLAIMED_EFFECT, CONTRADICTED, SUPPORTED,  # noqa: E402
                               classify_edge)
from shared.paths import data_path  # noqa: E402

INF = qp.INF
MIN_CELL = qp.MIN_CELL
DECIDED = ("supported", "contradicted")
SEED = 20261007
N_BOOT = 1000
CALIPER = 0.5
SMALL_N = 10
HALF = 0.5
MIN_MATCHED = 30
MAX_UNMATCHED = 0.50
COVER_P = 0.8


# ----------------------------------------------------------------------------- loading

class ItemRows(qp.Rows):
    """qmatrix_positivity.Rows, also keeping the item of every unit-event."""

    def __init__(self):
        super().__init__()
        self.I = array("i")
        self.item_ids = {}

    def add(self, learner, unit, ok, t, item):
        super().add(learner, unit, ok, t, item)
        k = self.item_ids.get(item)
        if k is None:
            k = self.item_ids[item] = len(self.item_ids)
        self.I.append(k)

    def finish_items(self):
        I = np.frombuffer(self.I, dtype=np.int32).copy()
        ids = self.item_ids
        del self.I
        names, L, U, T, OK, nL, items, Q = self.finish()
        pos = {it: r for r, it in enumerate(items)}
        remap = np.empty(len(ids), np.int32)
        for it, k in ids.items():
            remap[k] = pos[it]
        return names, L, U, T, OK, nL, items, Q, remap[I]


def load_xes3g5m():
    root = data_path("XES_DIR")
    known = {int(k) for k in json.loads((root / "cid2route.json").read_text(encoding="utf-8"))}
    R = ItemRows()
    with (root / "attempts.tsv").open(encoding="utf-8") as fh:
        for line in fh:
            uid, q, c, r, t = line.rstrip("\n").split("\t")
            ok = r == "1"
            for part in c.split("_"):
                if (k := int(part)) in known:
                    R.add(uid, f"k{k}", ok, t, q)
    return R


def load_eedi():
    from shared.corpus import Eedi
    answers = data_path("EEDI_ANSWERS")
    E = Eedi(answers, data_path("EEDI_ZIP"))
    R = ItemRows()
    with open(answers, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            for unit in E.leaves.get(r["QuestionId"], ()):
                R.add(r["UserId"], unit, float(r["IsCorrect"]) >= 0.5, r["DateAnswered"],
                      r["QuestionId"])
    return R


# ----------------------------------------------------------------------------- the engine

class World:
    """Dense atlas replica (qmatrix_positivity.Dense) plus per-unit event lists with items, so a
    unit's column can be rebuilt with any set of items removed."""

    def __init__(self, names, L, U, T, OK, nL, items, Q, I):
        self.units, self.items, self.Q = names, items, Q
        self.nL, self.nU = nL, len(names)
        self.dense = qp.Dense(L, U, T, OK, nL, names)
        order = np.argsort(U, kind="stable")
        Us = U[order]
        self.eL = L[order].astype(np.int64)
        self.eT = T[order]
        self.eOK = OK[order].astype(np.int8)
        self.eI = I[order]
        self.start = np.searchsorted(Us, np.arange(self.nU + 1))
        self.co = qp.design_counts(Q)[0]
        self.unit_items = [np.flatnonzero(Q[:, j]) for j in range(self.nU)]
        # events per (unit, item), for sizing removals
        self.item_events = []
        for j in range(self.nU):
            s, e = self.start[j], self.start[j + 1]
            it, cnt = np.unique(self.eI[s:e], return_counts=True)
            self.item_events.append((it, cnt))

    def shared_items(self, a, b):
        return np.flatnonzero(self.Q[:, a] & self.Q[:, b])

    def col(self, u, drop=None, mark=None):
        """The atlas's per-learner first touch, outcome at first touch and first pass for unit u,
        with responses to the items in `drop` removed. `mark`: flag learners whose first event
        on u is on one of these items."""
        s, e = self.start[u], self.start[u + 1]
        lu, tu, oku, iu = self.eL[s:e], self.eT[s:e], self.eOK[s:e], self.eI[s:e]
        removed = 0
        if drop is not None and len(drop):
            keep = ~np.isin(iu, drop)
            removed = int((~keep).sum())
            lu, tu, oku, iu = lu[keep], tu[keep], oku[keep], iu[keep]
        nL = self.nL
        tf = np.full(nL, INF, np.int64)
        np.minimum.at(tf, lu, tu)
        at_first = tu == tf[lu]
        y = np.ones(nL, np.int8)
        np.minimum.at(y, lu[at_first], oku[at_first])
        p = np.full(nL, INF, np.int64)
        okm = oku.astype(bool)
        np.minimum.at(p, lu[okm], tu[okm])
        touched = tf < INF
        y[~touched] = 0
        cnt = np.bincount(lu, minlength=nL)
        flag = None
        if mark is not None and len(mark):
            flag = np.zeros(nL, bool)
            sel = at_first & np.isin(iu, mark)
            flag[lu[sel]] = True
        return dict(tf=tf, y=y, p=p, touched=touched, cnt=cnt, removed=removed,
                    total=int(e - s), flag=flag)

    def raw_col(self, u):
        d = self.dense
        return dict(tf=d.Tf[:, u], y=d.Y[:, u], p=d.P[:, u], touched=d.touched[:, u])

    def falsifiable(self, a, b, cA, cB):
        """Dense.falsifiable with columns a and b replaced."""
        d = self.dense
        both = np.flatnonzero(cA["touched"] & cB["touched"])
        if not len(both):
            return False, 0
        P = d.P[both]
        Tf = d.Tf[both]
        touched = d.touched[both]
        for j, c in ((a, cA), (b, cB)):
            P[:, j] = c["p"][both]
            Tf[:, j] = c["tf"][both]
            touched[:, j] = c["touched"][both]
        passed = P < INF
        tl = np.where(passed, P, Tf)
        after = np.maximum(tl[:, a], tl[:, b])
        stratum = np.where(passed[:, a], 0, 2) + np.where(passed[:, b], 0, 1)
        M = touched & (tl > after[:, None])
        M[:, a] = False
        M[:, b] = False
        MP = M & passed
        cells = np.stack([M[stratum == s].sum(0) for s in range(4)])
        passes = np.stack([MP[stratum == s].sum(0) for s in range(4)])
        readable = cells.min(0) >= MIN_CELL
        for c in np.flatnonzero(readable):
            v = cells[:, c]
            p_both = passes[0, c] / v[0] if v[0] else 0.0
            m = reach_mod._mde(int(v[0]), int(v[1:].min()), float(p_both))
            if m is not None and m <= CLAIMED_EFFECT:
                return True, int(readable.sum())
        return False, int(readable.sum())

    def state(self, a, b, cA=None, cB=None):
        """Atlas state of a -> b on the given columns (raw columns when None)."""
        cA = cA or self.raw_col(a)
        cB = cB or self.raw_col(b)
        Lb = np.flatnonzero(cB["touched"])
        tb = cB["tf"][Lb]
        ta = cA["tf"][Lb]
        yb = cB["y"][Lb]
        never = ta >= tb
        mast = (~never) & (cA["p"][Lb] < tb)
        fail = (~never) & (~mast)
        n_m, n_f, n_n = int(mast.sum()), int(fail.sum()), int(never.sum())
        v = obs = None
        if n_m:
            p_m = float(np.mean(yb[mast]))
            v = positivity.mde(n_m, n_f, p_m)
            if n_f:
                obs = p_m - float(np.mean(yb[fail]))
        st = classify_edge(v, obs)[0]
        if st == CONTRADICTED:
            ok, _ = self.falsifiable(a, b, cA, cB)
            fine = "contradicted" if classify_edge(v, obs, falsifiable=ok)[0] == CONTRADICTED \
                else "unfalsifiable"
        elif st == SUPPORTED:
            fine = "supported"
        elif v is None:
            fine = "unreadable"
        elif v > CLAIMED_EFFECT:
            fine = "unpowered"
        else:
            fine = "no_comparison"
        tie = int((ta == tb).sum())
        cell = np.full(self.nL, 3, np.int8)
        cell[Lb[mast]] = 0
        cell[Lb[fail]] = 1
        cell[Lb[never]] = 2
        return dict(state=fine, mde=v, obs=obs, n_m=n_m, n_f=n_f, n_n=n_n, ties=tie,
                    reach=len(Lb), cell=cell)

    def covariates(self, cA, cB):
        both = cA["touched"] & cB["touched"]
        n = int(both.sum())
        if n == 0:
            return np.array([0.0, np.nan, np.nan, np.nan]), 0
        apl = (cA["cnt"][both].sum() + cB["cnt"][both].sum()) / n
        return np.array([math.log1p(n), math.log(apl), float(cB["y"][both].mean()),
                         float(cA["y"][both].mean())]), n

    def pool_covariates(self, chunk=10000):
        """x1..x4 for EVERY ordered pair at once: N = t'.t, AC = t'.C, AY = t'.Y, by learner
        chunks. sum over co-attempters of cnt_a = (t_b . C_a) because C_a > 0 iff t_a."""
        nU = self.nU
        cnt = np.zeros((self.nL, nU), np.int32)
        for j in range(nU):
            cnt[:, j] = np.bincount(self.eL[self.start[j]:self.start[j + 1]], minlength=self.nL)
        N = np.zeros((nU, nU))
        AC = np.zeros((nU, nU))
        AY = np.zeros((nU, nU))
        for s in range(0, self.nL, chunk):
            e = min(self.nL, s + chunk)
            t = self.dense.touched[s:e].astype(np.float64)
            N += t.T @ t
            AC += t.T @ cnt[s:e].astype(np.float64)
            AY += t.T @ self.dense.Y[s:e].astype(np.float64)
        del cnt
        with np.errstate(divide="ignore", invalid="ignore"):
            x1 = np.log1p(N)
            x2 = np.log((AC.T + AC) / N)      # [a,b]: (t_b.C_a + t_a.C_b) / N
            x3 = AY / N                        # [a,b]: sum over co-attempters of y_b
            x4 = AY.T / N
        return np.rint(N).astype(np.int64), np.stack([x1, x2, x3, x4], -1)


# ----------------------------------------------------------------------------- removal sizing

def sized_drop(world, u, target_share, rng, exclude=()):
    """Random whole items of u (any of u's items except `exclude`), added in random order; the
    prefix whose removed-event share is closest to target_share."""
    it, cnt = world.item_events[u]
    total = cnt.sum()
    if target_share <= 0 or total == 0:
        return np.array([], np.int64), 0.0
    keep = ~np.isin(it, np.asarray(exclude, dtype=it.dtype)) if len(exclude) else np.ones(len(it), bool)
    it, cnt = it[keep], cnt[keep]
    perm = rng.permutation(len(it))
    cum = np.cumsum(cnt[perm]) / total
    k = int(np.argmin(np.abs(cum - target_share))) + 1
    return it[perm[:k]], float(cum[k - 1])


# ----------------------------------------------------------------------------- matching

def match(treated, tx, tn, pool_by_b, sd, rng):
    """treated: list of (a, b); tx: covariates per treated edge; tn: n_both per treated edge;
    pool_by_b: b -> (a array, X array (k x 4), N array). Returns list of control a or None."""
    order = rng.permutation(len(treated))
    out = [None] * len(treated)
    for i in order:
        a, b = treated[i]
        if b not in pool_by_b:
            continue
        ca, X, Nn = pool_by_b[b]
        u = np.zeros(len(ca), bool)        # with replacement: a control may serve several edges
        if tn[i] < SMALL_N:
            ok = (Nn < SMALL_N) & ~u
            if not ok.any():
                continue
            dist = np.where(ok, np.abs(X[:, 0] - tx[i][0]) / sd[0], np.inf)
        else:
            z = np.abs(X - tx[i]) / sd
            ok = (Nn >= SMALL_N) & ~u & np.all(z <= CALIPER, axis=1)
            if not ok.any():
                continue
            dist = np.where(ok, np.sqrt((z ** 2).sum(1)), np.inf)
        j = int(np.argmin(dist))
        if not np.isfinite(dist[j]):
            continue
        out[i] = int(ca[j])
    return out


def smd(xt, xc, sd):
    """standardised mean differences; rows with any undefined covariate (n_both = 0) skipped."""
    xt, xc = np.asarray(xt, float), np.asarray(xc, float)
    xt = xt[np.all(np.isfinite(xt), 1)]
    xc = xc[np.all(np.isfinite(xc), 1)]
    if not len(xt) or not len(xc):
        return None
    return ((xt.mean(0) - xc.mean(0)) / sd).tolist()


# ----------------------------------------------------------------------------- statistics

def dec(s):
    return s in DECIDED


class Boot:
    """Cluster bootstrap over dependants: every statistic is a ratio of sums per dependant."""

    def __init__(self, clusters, rng, n=N_BOOT):
        self.ids = np.asarray(sorted(set(clusters)))
        self.pos = {c: i for i, c in enumerate(self.ids)}
        self.draws = [np.bincount(rng.integers(0, len(self.ids), len(self.ids)),
                                  minlength=len(self.ids)) for _ in range(n)]

    def sums(self, groups, vals):
        out = np.zeros(len(self.ids))
        np.add.at(out, [self.pos[g] for g in groups], vals)
        return out

    def ratio(self, groups, num, den):
        """point and per-draw values of sum(num)/sum(den)."""
        sn, sd_ = self.sums(groups, num), self.sums(groups, den)
        point = sn.sum() / sd_.sum() if sd_.sum() else None
        reps = np.array([(w @ sn) / (w @ sd_) if (w @ sd_) else np.nan for w in self.draws])
        return point, reps


def diff_stat(boot, g1, v1, g2, v2, den1=None, den2=None):
    """(sum v1/sum den1) - (sum v2/sum den2), point and 95% percentile interval."""
    den1 = np.ones(len(v1)) if den1 is None else den1
    den2 = np.ones(len(v2)) if den2 is None else den2
    p1, r1 = boot.ratio(g1, v1, den1)
    p2, r2 = boot.ratio(g2, v2, den2)
    if p1 is None or p2 is None:
        return dict(point=None, lo=None, hi=None, a=p1, b=p2)
    reps = r1 - r2
    reps = reps[np.isfinite(reps)]
    return dict(point=float(p1 - p2), lo=float(np.percentile(reps, 2.5)),
                hi=float(np.percentile(reps, 97.5)), a=float(p1), b=float(p2), reps=reps)


def strip(d):
    return {k: v for k, v in d.items() if k != "reps"}


def verdict(g0, gEM, n_matched, n_treated):
    if g0["point"] is None or g0["lo"] is None:
        return "UNANSWERABLE: NO GAP TO EXPLAIN"
    if g0["lo"] <= 0 <= g0["hi"]:
        return "UNANSWERABLE: NO GAP TO EXPLAIN"
    if n_matched < MIN_MATCHED:
        return "UNANSWERABLE: TOO FEW MATCHED EDGES"
    if 1 - n_matched / n_treated > MAX_UNMATCHED:
        return "UNANSWERABLE: NO COMMON SUPPORT"
    s = 1.0 if g0["point"] > 0 else -1.0
    G = s * g0["point"]
    r = s * gEM["point"]
    lo, hi = sorted((s * gEM["lo"], s * gEM["hi"]))
    if lo <= 0 <= hi and hi < HALF * G:
        return ("MECHANICAL: the gap vanishes once shared-item responses are excluded and coverage "
                "and difficulty are matched")
    if lo > 0 and r >= HALF * G:
        return "SUBSTANTIVE: the gap survives exclusion and matching with the same sign"
    if lo > 0:
        return "MIXED: part of the gap is mechanical, a same-sign remainder survives"
    if hi < 0:
        return ("REVERSED: once handled, shared-item edges are decided LESS often than matched "
                "controls")
    return ("UNANSWERABLE: UNDERPOWERED (the remainder can be neither excluded nor bounded below "
            "half)")


def lean_verdict(L):
    if L["point"] is None or L["lo"] is None:
        return "NOT TESTABLE"
    if L["lo"] > 0:
        return "LEANS SUPPORTED"
    if L["hi"] < 0:
        return "LEANS CONTRADICTED"
    return "NO DETECTED LEAN"


# ----------------------------------------------------------------------------- the analysis

def analyse(world, baseline_pairs, baseline_states, label, rng, sample_shared=None, log=print):
    """Everything per corpus (or synthetic world). baseline_pairs/states: the atlas sample's
    non-shared edges (index pairs) with their raw states."""
    nU = world.nU
    co = world.co
    off = ~np.eye(nU, dtype=bool)
    shared_mask = (co > 0) & off
    treated = [(int(a), int(b)) for a, b in zip(*np.nonzero(shared_mask))]
    log(f"[{label}] {len(treated):,} treated (co-tagged) edges; pool covariates")
    Npool, Xpool = world.pool_covariates()
    tb_set = sorted({b for _a, b in treated})
    pool_by_b = {}
    pool_rows = []
    for b in tb_set:
        ca = np.flatnonzero((co[:, b] == 0) & (np.arange(nU) != b))
        pool_by_b[b] = (ca, Xpool[ca, b], Npool[ca, b])
        pool_rows.append(Xpool[ca, b][Npool[ca, b] >= SMALL_N])
    P = np.vstack(pool_rows)
    sd = np.nanstd(P, axis=0)
    sd[sd == 0] = 1.0

    rec = []
    trans = np.zeros((4, 4), np.int64)
    t0 = time.time()
    for k, (a, b) in enumerate(treated):
        S = world.shared_items(a, b)
        rA, rB = world.col(a, mark=None), world.col(b, mark=S)
        raw = world.state(a, b, rA, rB)
        xr, nr = world.covariates(rA, rB)
        eA, eB = world.col(a, drop=S), world.col(b, drop=S)
        ex = world.state(a, b, eA, eB)
        xe, ne = world.covariates(eA, eB)
        toA = world.state(a, b, rA, eB)
        toB = world.state(a, b, eA, rB)
        both_raw = rA["touched"] & rB["touched"]
        both_ex = eA["touched"] & eB["touched"]
        trans += np.bincount(raw["cell"].astype(np.int64) * 4 + ex["cell"], minlength=16).reshape(4, 4)
        rec.append(dict(
            a=a, b=b, n_shared_items=len(S), raw=raw["state"], excl=ex["state"],
            to_a=toA["state"], to_b=toB["state"], xr=xr, nr=nr, xe=xe, ne=ne,
            share_A=eA["removed"] / max(1, eA["total"]), share_B=eB["removed"] / max(1, eB["total"]),
            cells_raw=(raw["n_m"], raw["n_f"], raw["n_n"]), cells_ex=(ex["n_m"], ex["n_f"], ex["n_n"]),
            ties_raw=raw["ties"], ties_ex=ex["ties"], reach_raw=raw["reach"], reach_ex=ex["reach"],
            firstB_shared=int(rB["flag"][rB["touched"]].sum()) if rB["flag"] is not None else 0,
            coattempt_only_shared=int((both_raw & ~both_ex).sum()), coattempt_raw=int(both_raw.sum())))
        if (k + 1) % 200 == 0:
            log(f"   treated {k + 1:,}/{len(treated):,}  {time.time() - t0:.0f}s")

    # matching
    tr_idx = list(range(len(rec)))
    m_ctrl = match(treated, [r["xr"] for r in rec], [r["nr"] for r in rec], pool_by_b, sd, rng)
    em_ctrl = match(treated, [r["xe"] for r in rec], [r["ne"] for r in rec], pool_by_b, sd, rng)
    log(f"[{label}] matched M {sum(c is not None for c in m_ctrl):,}, "
        f"EM {sum(c is not None for c in em_ctrl):,}; control states")

    m_rows, em_rows, sizes_t, sizes_c = [], [], {}, {}
    for i in tr_idx:
        a, b = treated[i]
        r = rec[i]
        c = m_ctrl[i]
        if c is not None:
            st_raw = world.state(c, b)
            S = world.shared_items(a, b)
            dB, achB = sized_drop(world, b, r["share_B"], rng)
            dA, achA = sized_drop(world, c, r["share_A"], rng, exclude=world.unit_items[b])
            cA, cB = world.col(c, drop=dA), world.col(b, drop=dB)
            st_s = world.state(c, b, cA, cB)
            xc = Xpool[c, b]
            m_rows.append(dict(i=i, c=c, b=b, raw=st_raw["state"], sized=st_s["state"], xc=xc,
                               achA=achA, achB=achB))
            sizes_t[f"t{i}"] = r["share_A"] + r["share_B"]
            sizes_c[f"c{i}"] = achA + achB
            del S
        c2 = em_ctrl[i]
        if c2 is not None:
            st2 = world.state(c2, b)
            em_rows.append(dict(i=i, c=c2, b=b, raw=st2["state"], xc=Xpool[c2, b],
                                n_f=st2["n_f"], reach=st2["reach"], cells=(st2["n_m"], st2["n_f"], st2["n_n"])))

    boot = Boot(list(range(nU)), rng)
    gT = [treated[i][1] for i in tr_idx]
    v_raw = np.array([dec(r["raw"]) for r in rec], float)
    v_ex = np.array([dec(r["excl"]) for r in rec], float)
    v_toA = np.array([dec(r["to_a"]) for r in rec], float)
    v_toB = np.array([dec(r["to_b"]) for r in rec], float)
    gB = [b for _a, b in baseline_pairs]
    v_base = np.array([dec(s) for s in baseline_states], float)

    g0 = diff_stat(boot, gT, v_raw, gB, v_base)
    gE = diff_stat(boot, gT, v_ex, gB, v_base)
    g_toA = diff_stat(boot, gT, v_toA, gB, v_base)
    g_toB = diff_stat(boot, gT, v_toB, gB, v_base)
    mi = [m["i"] for m in m_rows]
    mg = [m["b"] for m in m_rows]
    gM = diff_stat(boot, mg, v_raw[mi], mg, np.array([dec(m["raw"]) for m in m_rows], float))
    gES = diff_stat(boot, mg, v_ex[mi], mg, np.array([dec(m["sized"]) for m in m_rows], float))
    dT_dC = diff_stat(boot, mg, v_raw[mi] - v_ex[mi], mg,
                      np.array([dec(m["raw"]) - dec(m["sized"]) for m in m_rows], float))
    ei = [m["i"] for m in em_rows]
    eg = [m["b"] for m in em_rows]
    v_em = np.array([dec(m["raw"]) for m in em_rows], float)
    gEM = diff_stat(boot, eg, v_ex[ei], eg, v_em)
    share_expl = None
    if g0["point"] and gEM["point"] is not None:
        n = min(len(g0["reps"]), len(gEM["reps"]))
        with np.errstate(divide="ignore", invalid="ignore"):
            reps = 1 - gEM["reps"][:n] / g0["reps"][:n]
        reps = reps[np.isfinite(reps)]
        share_expl = dict(point=1 - gEM["point"] / g0["point"],
                          lo=float(np.percentile(reps, 2.5)), hi=float(np.percentile(reps, 97.5)))

    # lean among decided
    def sup_dec(states):
        return (np.array([s == "supported" for s in states], float),
                np.array([dec(s) for s in states], float))
    sT, dT = sup_dec([r["raw"] for r in rec])
    sB, dB_ = sup_dec(baseline_states)
    lean_raw = diff_stat(boot, gT, sT, gB, sB, dT, dB_)
    sTe, dTe = sup_dec([rec[i]["excl"] for i in ei])
    sC, dC = sup_dec([m["raw"] for m in em_rows])
    lean_em = diff_stat(boot, eg, sTe, eg, sC, dTe, dC)

    # positivity diagnostic: failed-cell share, T EXCL vs EM controls
    fT = np.array([rec[i]["cells_ex"][1] for i in ei], float)
    rT = np.array([sum(rec[i]["cells_ex"]) for i in ei], float)
    fC = np.array([m["cells"][1] for m in em_rows], float)
    rC = np.array([sum(m["cells"]) for m in em_rows], float)
    failed_share = diff_stat(boot, eg, fT, eg, fC, rT, rC)

    # sizing check (shared/controls.py)
    scale = None
    if sizes_t and sizes_c:
        tmed = float(np.median(list(sizes_t.values())))
        cmed = float(np.median(list(sizes_c.values())))
        try:
            rep = check_control_scale({"treatment_median": 100 * tmed, "control_median": 100 * cmed},
                                      ["control_median"], strict=True)
            scale_ok = True
        except AssertionError as exc:
            rep, scale_ok = str(exc), False
        ratios = [sizes_c[f"c{i}"] / sizes_t[f"t{i}"] for i in mi if sizes_t[f"t{i}"] > 0]
        scale = dict(treatment_median_share_removed=tmed, control_median_share_removed=cmed,
                     ratio_quartiles=np.percentile(ratios, [25, 50, 75]).tolist() if ratios else None,
                     passes_check_control_scale=scale_ok,
                     report=rep if isinstance(rep, str) else rep.get("report", str(rep)))

    n_t = len(rec)
    v = verdict(g0, gEM, len(em_rows), n_t)
    v_es = verdict(g0, gES, len(m_rows), n_t)

    def counts(states):
        out = {}
        for s in states:
            out[s] = out.get(s, 0) + 1
        return out

    def mean_cells(key, idx=None):
        idx = range(n_t) if idx is None else idx
        a = np.array([rec[i][key] for i in idx], float)
        return a.mean(0).tolist() if len(a) else None

    reach_raw = sum(r["reach_raw"] for r in rec)
    surviving = sum(1 for r in rec if r["raw"] == "supported" and r["excl"] == "supported")
    res = dict(
        treated_edges=n_t, baseline_nonshared_edges=len(baseline_pairs),
        states=dict(treated_raw=counts(r["raw"] for r in rec),
                    treated_excl=counts(r["excl"] for r in rec),
                    treated_to_a=counts(r["to_a"] for r in rec),
                    treated_to_b=counts(r["to_b"] for r in rec),
                    baseline=counts(baseline_states),
                    m_controls_raw=counts(m["raw"] for m in m_rows),
                    m_controls_sized=counts(m["sized"] for m in m_rows),
                    em_controls=counts(m["raw"] for m in em_rows)),
        decided_share=dict(treated_raw=float(v_raw.mean()), treated_excl=float(v_ex.mean()),
                           treated_to_a=float(v_toA.mean()), treated_to_b=float(v_toB.mean()),
                           baseline=float(v_base.mean()) if len(v_base) else None),
        gaps=dict(g0=strip(g0), gE=strip(gE), gM=strip(gM), gEM=strip(gEM), gES=strip(gES),
                  g_toA=strip(g_toA), g_toB=strip(g_toB),
                  exclusion_effect_beyond_data_loss=strip(dT_dC), share_explained=share_expl),
        matching=dict(m_matched=len(m_rows), em_matched=len(em_rows),
                      m_unmatched_share=1 - len(m_rows) / n_t if n_t else None,
                      em_unmatched_share=1 - len(em_rows) / n_t if n_t else None,
                      sd=sd.tolist(), caliper_sd=CALIPER,
                      smd_m=smd([rec[m["i"]]["xr"] for m in m_rows], [m["xc"] for m in m_rows], sd),
                      smd_em=smd([rec[m["i"]]["xe"] for m in em_rows], [m["xc"] for m in em_rows], sd),
                      smd_before=smd([r["xr"] for r in rec if r["nr"] >= SMALL_N], P, sd)),
        sized_control=scale,
        lean=dict(raw=strip(lean_raw), raw_verdict=lean_verdict(lean_raw),
                  em=strip(lean_em), em_verdict=lean_verdict(lean_em)),
        positivity_diagnostic=dict(failed_cell_share=strip(failed_share)),
        mechanism=dict(
            mean_cells_raw_m_f_n=mean_cells("cells_raw"), mean_cells_excl_m_f_n=mean_cells("cells_ex"),
            share_B_reachers_first_B_on_shared_item=(sum(r["firstB_shared"] for r in rec) / reach_raw)
            if reach_raw else None,
            share_B_reachers_tied_raw=(sum(r["ties_raw"] for r in rec) / reach_raw) if reach_raw else None,
            share_B_reachers_tied_excl=(sum(r["ties_ex"] for r in rec) / max(1, sum(r["reach_ex"] for r in rec))),
            share_coattempters_only_through_shared=(sum(r["coattempt_only_shared"] for r in rec)
                                                    / max(1, sum(r["coattempt_raw"] for r in rec))),
            median_share_of_B_events_removed=float(np.median([r["share_B"] for r in rec])),
            median_share_of_A_events_removed=float(np.median([r["share_A"] for r in rec])),
            cell_transition_raw_to_excl=dict(order=["mastered", "failed", "never", "absent"],
                                             counts=trans.tolist()),
            supported_raw=sum(1 for r in rec if r["raw"] == "supported"),
            supported_raw_surviving_excl=surviving),
        verdict=v, verdict_using_gES=v_es,
    )
    if sample_shared is not None:
        ss = [i for i, (a, b) in enumerate(treated) if (a, b) in sample_shared]
        res["atlas_sample_subset"] = dict(edges=len(ss),
                                          decided_raw=int(sum(v_raw[i] for i in ss)),
                                          decided_excl=int(sum(v_ex[i] for i in ss)))
    return res


# ----------------------------------------------------------------------------- synthetic worlds

def synth_world(kind, seed, nL=20000, nU=100, own=8, n_pairs=100, n_sh=1, visits=37, max_loop=6,
                remediate=2, p_master=0.55):
    rng = np.random.default_rng(seed)
    allp = [(u, v) for u in range(nU) for v in range(u + 1, nU)]
    pairs = [allp[i] for i in rng.choice(len(allp), n_pairs, replace=False)]
    partner = {u: set() for u in range(nU)}
    for u, v in pairs:
        partner[u].add(v)
        partner[v].add(u)
    items = []                      # (name, units tuple)
    pool = {u: [] for u in range(nU)}
    # heterogeneous skills, as real corpora are: own-item count, mastery rate, popularity and
    # mastery-loop length vary by skill (independently of which pairs share items)
    own_u = rng.integers(own // 2, own + own // 2 + 1, nU)
    p_master_u = rng.uniform(p_master - 0.25, p_master + 0.25, nU)
    pop = rng.lognormal(0.0, 0.7, nU)
    pop = pop / pop.sum()
    logit_u = np.log(p_master_u / (1 - p_master_u))
    loop_u = rng.integers(max_loop - 3, max_loop + 3, nU)
    for u in range(nU):
        for k in range(int(own_u[u])):
            pool[u].append(len(items))
            items.append((f"o{u}_{k}", (u,)))
    for p, (u, v) in enumerate(pairs):
        for k in range(n_sh):
            pool[u].append(len(items))
            pool[v].append(len(items))
            items.append((f"s{p}_{k}", (u, v)))
    pool = {u: np.array(x) for u, x in pool.items()}
    names = [f"k{u:02d}" for u in range(nU)]
    R = ItemRows()
    rows, row_items = [], []
    for li in range(nL):
        theta = rng.normal()
        know = rng.random(nU) < 1 / (1 + np.exp(-(2.0 * theta + logit_u)))
        sel = list(rng.permutation(rng.choice(nU, visits, replace=False, p=pop)))
        if kind == "cover":         # W-COVER: a drawn skill usually brings its shared partner along
            extra = [v for u in sel for v in sorted(partner[u])
                     if v not in sel and rng.random() < COVER_P]
            sel = list(rng.permutation(list(dict.fromkeys(sel + extra))))
        sel_set = set(sel)
        done = set()
        t = 1_595_000_000_000 + int(rng.integers(0, 10 ** 9))
        lname = f"L{li}"

        def respond(it):
            us = items[it][1]
            if len(us) == 1:
                return rng.random() < (0.85 if know[us[0]] else 0.25)
            if kind == "mech":
                return rng.random() < (0.85 if all(know[x] for x in us) else 0.25)
            # W-SUBST: a shared item measures general ability only, like any item would through
            # theta, and neither of its two skills in particular
            return rng.random() < 0.25 + 0.6 / (1 + math.exp(-2.0 * theta))

        def emit(it, ok, t):
            for x in items[it][1]:
                R.add(lname, names[x], ok, str(t), items[it][0])
                rows.append((lname, names[x], ok, str(t), False, False))
                row_items.append(items[it][0])

        # visit order; in W-SUBST a selected shared partner is taught right after its skill
        order = []
        for u in sel:
            if u in done:
                continue
            done.add(u)
            order.append(u)
            if kind == "subst":
                for v in sorted(partner[u]):
                    if v in sel_set and v not in done:
                        done.add(v)
                        order.append(v)
                        break

        def loop(u, t):
            for _ in range(int(loop_u[u])):
                it = int(rng.choice(pool[u]))
                ok = respond(it)
                t += 1000
                emit(it, ok, t)
                if ok and len(items[it][1]) == 1:
                    return True, t
            return False, t

        pending = None
        for k, u in enumerate(order):
            passed, t = loop(u, t)
            if pending is not None:          # deferred remediation of the previous skill
                for _r in range(remediate):
                    ok_r, t = loop(pending, t)
                    if ok_r:
                        break
                pending = None
            if not passed:
                nxt = order[k + 1] if k + 1 < len(order) else None
                if kind == "subst" and nxt in partner[u]:
                    pending = u              # taught together: move on to the partner first
                else:
                    for _r in range(remediate):
                        ok_r, t = loop(u, t)
                        if ok_r:
                            break
    return R, rows, names, row_items


def synth_run(kind, seed, log=print):
    R, rows, names, _ri = synth_world(kind, seed)
    del rows, _ri
    names_, L, U, T, OK, nL, items, Q, I = R.finish_items()
    W = World(names_, L, U, T, OK, nL, items, Q, I)
    off = ~np.eye(W.nU, dtype=bool)
    base_pairs = [(int(a), int(b)) for a, b in zip(*np.nonzero(off & (W.co == 0)))]
    # X1 on this world: the engine on rebuilt columns against qmatrix_positivity's replica, every pair
    all_pairs = [(int(a), int(b)) for a, b in zip(*np.nonzero(off))]
    ref, _ = qp.edge_states(W.dense, all_pairs)
    mism, seen, eng = 0, set(), {}
    for (a, b), (st, v, obs) in zip(all_pairs, ref):
        cA, cB = W.col(a), W.col(b)
        same = all(np.array_equal(cA[k], W.raw_col(a)[k]) and np.array_equal(cB[k], W.raw_col(b)[k])
                   for k in ("tf", "y", "p", "touched"))
        e = W.state(a, b, cA, cB)
        mism += not (same and e["state"] == st and e["mde"] == v and e["obs"] == obs)
        seen.add(st)
        eng[(a, b)] = e["state"]
    base_states = [eng[p] for p in base_pairs]
    rng = np.random.default_rng(SEED + seed)
    res = analyse(W, base_pairs, base_states, f"{kind}/{seed}", rng, log=log)
    res["X1"] = dict(pairs=len(all_pairs), mismatches=mism, states_seen=sorted(seen))
    return res


def exactness(log=print):
    """X1-X3 on a W-MECH world (smaller, so the atlas's own reference code runs in time)."""
    R, rows, names, ev_items = synth_world("mech", 7, nL=8000, nU=20, n_pairs=25, n_sh=2,
                                           visits=10)
    names_, L, U, T, OK, nL, items, Q, I = R.finish_items()
    W = World(names_, L, U, T, OK, nL, items, Q, I)
    pairs = [(a, b) for a in range(W.nU) for b in range(W.nU) if a != b]
    ref, _ = qp.edge_states(W.dense, pairs)
    mism1 = 0
    seen = set()
    for (a, b), (st, v, obs) in zip(pairs, ref):
        cA, cB = W.col(a), W.col(b)
        same_cols = all(np.array_equal(cA[k], W.raw_col(a)[k]) for k in ("tf", "y", "p", "touched"))
        s = W.state(a, b, cA, cB)
        mism1 += not (same_cols and s["state"] == st and s["mde"] == v and s["obs"] == obs)
        seen.add(st)
    x1 = mism1 == 0          # branch coverage is checked over the discrimination worlds too
    # X2: EXCL against the atlas's functions on a rebuilt row stream
    sh = [(a, b) for a, b in pairs if W.co[a, b] > 0][:40]
    mism2 = 0
    states2 = set()
    for a, b in sh:
        A, B = W.units[a], W.units[b]
        S = {W.items[i] for i in W.shared_items(a, b)}
        kept = [r for r, it in zip(rows, ev_items) if not (r[1] in (A, B) and it in S)]
        bl = positivity.timelines(kept)
        ft, fp, oat = positivity.states(bl)
        idx = positivity.at_item(ft, oat)
        c = positivity.classify((A, B), ft, fp, oat, idx)
        n_m, n_f = len(c["mastered"]), len(c["failed"])
        v = obs = None
        if n_m:
            p_m = float(np.mean(c["mastered"]))
            v = positivity.mde(n_m, n_f, p_m)
            if n_f:
                obs = p_m - float(np.mean(c["failed"]))
        st = classify_edge(v, obs)[0]
        tl = {lr: {u: ((fpl[u], True) if u in fpl else (t, False)) for u, t in ft[lr].items()}
              for lr, fpl in fp.items()}
        okr = reach_mod.reachability(tl, [(A, B)], min_cell=MIN_CELL,
                                     claimed=CLAIMED_EFFECT)[(A, B)]["status"] == "FALSIFIABLE"
        Sx = W.shared_items(a, b)
        eA, eB = W.col(a, drop=Sx), W.col(b, drop=Sx)
        s = W.state(a, b, eA, eB)
        okd, _ = W.falsifiable(a, b, eA, eB)
        mism2 += not ((n_m, n_f, len(c["never"])) == (s["n_m"], s["n_f"], s["n_n"]) and
                      v == s["mde"] and obs == s["obs"] and okr == okd)
        states2.add(s["state"])
    x2 = mism2 == 0 and len(sh) == 40
    # X3 pool covariates
    Np, Xp = W.pool_covariates(chunk=1000)
    mism3 = 0
    for a, b in pairs:
        x, n = W.covariates(W.col(a), W.col(b))
        if n >= 1:
            mism3 += not (Np[a, b] == n and np.allclose(Xp[a, b], x, rtol=1e-9, atol=1e-12))
    x3 = mism3 == 0
    out = dict(X1_engine_equals_replica=x1, X1_mismatches=mism1, X1_states_seen=sorted(seen),
               X2_excl_equals_atlas_functions=x2, X2_edges=len(sh), X2_mismatches=mism2,
               X2_states_seen=sorted(states2),
               X3_pool_covariates_exact=x3, X3_mismatches=mism3)
    log(json.dumps(out))
    return x1 and x2 and x3, out


def floor():
    log = print
    checks, detail = {}, {}
    ok_x, detail["exactness"] = exactness(log)
    checks["exactness"] = ok_x
    lean_ok = True
    x1_seen, x1_mism = set(detail["exactness"]["X1_states_seen"]), 0
    for kind, want in (("mech", ("MECHANICAL",)), ("subst", ("SUBSTANTIVE", "MIXED"))):
        for seed in (1, 2):
            res = synth_run(kind, seed, log=log)
            key = f"{kind}_seed{seed}"
            detail[key] = dict(verdict=res["verdict"], verdict_gES=res["verdict_using_gES"],
                               gaps={k: res["gaps"][k] for k in ("g0", "gE", "gM", "gEM", "gES",
                                                                 "share_explained")},
                               decided_share=res["decided_share"], matching=res["matching"],
                               lean=res["lean"], positivity=res["positivity_diagnostic"],
                               sized=res["sized_control"], mechanism=res["mechanism"])
            checks[key] = any(res["verdict"].startswith(w) for w in want)
            x1_seen |= set(res["X1"]["states_seen"])
            x1_mism += res["X1"]["mismatches"]
            detail[key]["X1"] = res["X1"]
            if kind == "mech":
                lean_ok &= res["lean"]["raw_verdict"] == "LEANS SUPPORTED"
            log(f"   {key}: {res['verdict']}  (g0 {res['gaps']['g0']['point']:.3f}, "
                f"gEM {res['gaps']['gEM']['point']})")
    checks["X1_all_worlds_exact_and_every_branch"] = (
        x1_mism == 0 and {"supported", "contradicted", "unfalsifiable", "unpowered", "unreadable"} <= x1_seen)
    passed = all(checks.values())
    out = dict(passed=passed, lean_floor_passed=lean_ok, checks=checks, detail=detail,
               verdict=("FLOOR PASSED" if passed else
                        "FLOOR FAILED: every real verdict is UNANSWERABLE"))
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out/floor.json").write_text(json.dumps(out, indent=1, default=_j) + "\n")
    print(json.dumps(checks), out["verdict"], "lean floor", lean_ok)
    return passed


def _j(o):
    if hasattr(o, "item"):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


# ----------------------------------------------------------------------------- real corpora

def run_corpus(name):
    fl = HERE / "out/floor.json"
    floor_ok = fl.exists() and json.loads(fl.read_text())["passed"]
    print(f"[{name}] loading", flush=True)
    R = {"xes3g5m": load_xes3g5m, "eedi": load_eedi}[name]()
    names, L, U, T, OK, nL, items, Q, I = R.finish_items()
    del R
    W = World(names, L, U, T, OK, nL, items, Q, I)
    del L, U, T, OK, I
    print(f"[{name}] {nL:,} learners, {W.nU} units, {len(items):,} items", flush=True)
    pairs = qp.sample_pairs(name, names)
    uix = {u: j for j, u in enumerate(names)}
    pidx = [(uix[a], uix[b]) for a, b in pairs]
    st, pre = qp.edge_states(W.dense, pidx)
    states = [s for s, _v, _o in st]
    mdes = [v for _s, v, _o in st if v is not None]
    recomputed = dict(learners=nL, items=W.nU, edges=len(pidx), readable=len(mdes),
                      detect_20pt=int(sum(1 for v in mdes if v <= 0.20)),
                      supported=states.count("supported"), contradicted=states.count("contradicted"),
                      unknown=len(states) - states.count("supported") - states.count("contradicted"),
                      contradicted_before_reachability=pre)
    comm = qp.committed_row(name)
    fields = {k: (recomputed.get(k), comm[k], recomputed.get(k) == comm[k]) for k in comm if k != "source"}
    reproduced = all(v[2] for v in fields.values())
    print(f"[{name}] atlas reproduced exactly: {reproduced}", flush=True)
    base = [(p, s) for p, s in zip(pidx, states) if W.co[p[0], p[1]] == 0]
    sample_shared = {p for p in pidx if W.co[p[0], p[1]] > 0}
    rng = np.random.default_rng(SEED)
    res = analyse(W, [p for p, _ in base], [s for _, s in base], name, rng,
                  sample_shared=sample_shared, log=lambda m: print(m, flush=True))
    if not floor_ok:
        res["verdict"] = "UNANSWERABLE: the floor failed (" + res["verdict"] + " as computed)"
    res.update(corpus=name, learners=nL, units=W.nU, items=len(items),
               multi_unit_items=int((Q.sum(1) > 1).sum()), floor_passed=floor_ok,
               reproduction=dict(recomputed=recomputed, committed=comm, fields=fields,
                                 reproduced_exactly=reproduced),
               sample_decided_nonshared=int(sum(dec(s) for _, s in base)))
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / f"{name}.json").write_text(json.dumps(res, indent=1, default=_j) + "\n")
    print(f"[{name}] {res['verdict']}", flush=True)
    return res


def summary():
    out = {}
    for name in ("xes3g5m", "eedi"):
        p = HERE / "out" / f"{name}.json"
        if not p.exists():
            out[name] = "not run"
            continue
        r = json.loads(p.read_text())
        out[name] = dict(verdict=r["verdict"], verdict_using_gES=r["verdict_using_gES"],
                         treated=r["treated_edges"], decided_share=r["decided_share"],
                         gaps={k: r["gaps"][k] for k in ("g0", "gE", "gM", "gEM", "gES",
                                                         "share_explained")},
                         lean=r["lean"], matching={k: r["matching"][k] for k in
                                                   ("m_matched", "em_matched", "em_unmatched_share")},
                         reproduced=r["reproduction"]["reproduced_exactly"])
    out["floor_passed"] = json.loads((HERE / "out/floor.json").read_text())["passed"]
    (HERE / "out/summary.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def coverage_shape(g):
    """C1-C3 of the coverage-only section, on a result's gaps and verdict."""
    G = g["g0"]["point"]
    c1 = g["g0"]["lo"] > 0
    c2 = g["gE"]["point"] >= HALF * G and g["gE"]["lo"] > 0
    c3 = g["gM"]["lo"] <= 0 <= g["gM"]["hi"] and g["gM"]["hi"] < HALF * G
    return dict(C1=bool(c1), C2=bool(c2), C3_gM=bool(c3))


def coverage_floor():
    log = print
    out = dict(cover_p=COVER_P, worlds={}, others={}, real={})
    p1 = True
    for seed in (1, 2):
        res = synth_run("cover", seed, log=log)
        sh = coverage_shape(res["gaps"])
        sh["C3_verdict_mechanical"] = res["verdict"].startswith("MECHANICAL")
        ok = all(sh.values())
        p1 &= ok
        out["worlds"][f"cover_seed{seed}"] = dict(
            shape=sh, passes=ok, verdict=res["verdict"],
            gaps={k: res["gaps"][k] for k in ("g0", "gE", "gM", "gEM", "gES", "share_explained")},
            decided_share=res["decided_share"], matching=res["matching"], X1=res["X1"])
        log(f"   cover_seed{seed}: {sh}  {res['verdict']}")
    fl = json.loads((HERE / "out/floor.json").read_text())
    p2 = True
    for key, d in fl["detail"].items():
        if key == "exactness":
            continue
        sh = coverage_shape(d["gaps"])
        both = sh["C2"] and sh["C3_gM"]
        p2 &= not both
        out["others"][key] = dict(shape=sh, shows_C2_and_C3=both)
    passed = p1 and p2
    out["P1_cover_worlds_show_shape"] = p1
    out["P2_other_worlds_do_not"] = p2
    out["verdict"] = ("COVERAGE FLOOR PASSED: a coverage-only gap is closed by matching and not by "
                      "exclusion, and neither other world has that shape" if passed else
                      "COVERAGE FLOOR FAILED: attributing the gap to coverage stays a reading of the "
                      "decomposition")
    summ = json.loads((HERE / "out/summary.json").read_text())
    for c, r in summ.items():
        if not isinstance(r, dict) or "gaps" not in r:
            continue
        sh = coverage_shape(r["gaps"])
        sh["C3_verdict_mechanical"] = r["verdict"].startswith("MECHANICAL")
        shape = sh["C1"] and sh["C2"] and sh["C3_gM"]
        out["real"][c] = dict(shape=sh, reading=("UNANSWERABLE: the coverage floor failed" if not passed
                              else "COVERAGE SHAPE: the corpus's gap has the shape coverage alone produces"
                              if shape else "NOT THE COVERAGE SHAPE"))
    (HERE / "out/coverage-floor.json").write_text(json.dumps(out, indent=1, default=_j) + "\n")
    print(out["verdict"])
    for c, r in out["real"].items():
        print(f"   {c}: {r['reading']}  {r['shape']}")
    return passed


def main():
    argv = sys.argv[1:]
    if "--coverage-floor" in argv:
        sys.exit(0 if coverage_floor() else 1)
    if "--floor" in argv:
        sys.exit(0 if floor() else 1)
    if "--corpus" in argv:
        run_corpus(argv[argv.index("--corpus") + 1])
        return
    if "--summary" in argv:
        summary()
        return
    print(__doc__)


if __name__ == "__main__":
    main()
