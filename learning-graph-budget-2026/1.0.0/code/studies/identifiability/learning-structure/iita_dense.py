"""PRE-REGISTERED: does item-tree analysis find structure beyond ability and difficulty on dense data?

Paper 1 (research/article/limits-of-inferring-prerequisite-structure.md) reports that on 20
MOOCCubeX item sets IITA finds no dependency beyond ability and difficulty: 1 of 20 beats a
fixed-margins null (RESULTS-IITA-REAL.md, IDENTIFIABILITY.md). That test is weak in three ways this
one is built to remove: its sets hold 3-6 items, so in 11 of 20 the null is degenerate (5th pct =
median = 95th) and nothing could have scored; its power was measured on 6-item worlds whose WHOLE
structure was planted, never on the real matrices; and it was scored one-tailed, with the tail
itself disputed (RESULTS-IITA-REAL says real dependency yields FEWER implications than ability
alone; a planted gate plausibly yields MORE). Here: 15-skill sets on the two dense corpora, a
two-sided test, and a detection floor measured on each corpus's own sets before its verdict is read.

Reads XES3G5M (attempts.tsv under $XES_DIR) and ASSISTments 2012-13 (assist_slim.csv under
$ASSIST_DIR) through surmise_graphs' loaders, which resolve them with shared.paths.data_path. Raw
exports stay outside the repo; only per-set aggregates (skill ids, counts, null percentiles, rates)
are written. --synthetic reads no corpus.

PRE-REGISTRATION (written and committed before any real run; nothing below was chosen after seeing
a real number)

UNITS        Skill sets built exactly as studies/measurement/graph-typology/surmise_graphs.py builds
             them (imported, not copied): items tagged to one skill only; mastery = at least half of
             a learner's attempts on the skill correct (surmise_graphs.mastery, k/n >= 0.5); greedy
             disjoint sets seeded by the most-covered unused skill, each skill added to keep the most
             learners covering every skill in the set; a learner enters a set only if they attempted
             every skill in it (a complete responder). Minimum 200 complete responders per set
             (surmise_graphs.MIN_LEARNERS); sets above 3000 are cut to a seeded subsample of 3000
             (MAX_LEARNERS). The set cap is raised from 8 to 20 (MAX_SETS); nothing else changes.
             Only sets of exactly K = 15 skills are units. The construction can stop early (5-14
             skills) when coverage falls under 200; such sets are SHORT, counted and never scored.
NULL         Fixed margins: learner x skill matrices with the observed row sums (ability) and column
             sums (difficulty), R = 500 draws per matrix. Sampler: global curveball (Carstens, Berger
             & Strona 2018), 30 rounds per draw from the observed matrix, each round a random perfect
             matching of rows with every pair's differing columns re-dealt uniformly; margins are
             asserted exact on every draw. It targets the same uniform distribution as
             mooccubex_concept_iita.fixed_margins_null (checkerboard swaps, 20*n*m attempts), which
             is ~0.9 s a draw at n = 3000 and cannot supply ~10^5 draws per corpus.
MIXING CHECK run first on every corpus, and a failure stops that corpus with MIXING CHECK FAILED and
             no verdict (a changed sampler is a new pre-registration): (a) on every set, the mean
             Hamming distance from the observed matrix after 30 rounds is >= 0.98 of that after 60;
             (b) on the first set, 40 curveball draws and 40 fixed_margins_null draws give
             implication-count distributions within the two-sample KS critical value at alpha 0.01
             (1.628 * sqrt(2/40) = 0.364). Synthetic: count distributions agree from 5 rounds on and
             Hamming saturates by ~25, so 30 is margin, not tuning.
DEGENERACY   A set is DEGENERATE if its null's 2.5th and 97.5th percentiles (order statistics 12
             and 487 of 500) coincide. Degenerate sets are excluded and counted, never scored. This
             is the positivity check here: a set whose margins fix the count cannot say anything.
STATISTIC    The corrected-IITA implication count (iita.corrected_iita via iita.iita_from_counts, its
             result asserted identical on every run). Two-sided per set at 2.5% per tail: LOWER if
             observed < 2.5th percentile, UPPER if observed > 97.5th, strictly, so ties never score.
             The tail is reported per set.
FLOOR        Run on each corpus's own non-degenerate sets, and written out, before that corpus's
             observed counts are computed. Into each set's real matrix, at random placements (15 per
             set per type): (a) PAIR, a pairwise prerequisite i -> j: learners failing i fail j
             with probability 0.9; (b) GATE, a conjunctive gate: learners failing i or k fail j with
             probability 0.9. A plant is DETECTED if the planted matrix falls outside the null of
             the planted matrix (its own 500 draws) at 2.5% per tail; a plant whose null is
             degenerate is not detected. Null drawing stops early only when the observed is already
             certain to sit inside the band (>= 13 draws at or below it and >= 13 at or above it),
             which is the same decision the full 500 would give. The FLOOR PASSES for a corpus if
             the median per-set detection rate is >= 0.8 for PAIR or for GATE. The tail each plant
             type moves (detections in the lower vs upper tail, and the median planted-minus-null
             shift) is recorded: this settles the tail dispute empirically, per corpus.
CHAIN        Also planted, 10 per set, and reported, never verdict-bearing: a pure 3-skill chain
             a -> b -> c, the three random skills ordered easiest to hardest so the chain runs WITH
             difficulty (b gated on a, then c on b, each at 0.9). Expected before the run: near 0,
             because a difficulty-aligned chain is a Guttman fragment and ability plus difficulty
             already produce one (chain blindness, IDENTIFIABILITY.md).
VERDICTS     per corpus, exactly one of these strings:
               UNANSWERABLE              the floor fails, or more than half the 15-skill sets are
                                         degenerate, or fewer than 5 sets are scored (with fewer,
                                         two hits are needed for p < 0.05 and the count is noise).
               STRUCTURE BEYOND ABILITY  the floor passes and the number of scored sets beyond the
                                         null in either tail exceeds chance: one-sided binomial
                                         P(X >= k | n scored, 0.05) < 0.05.
               NO STRUCTURE DETECTED     the floor passes and that count does not exceed chance.
             Reported beside the verdict: the split by tail, and whether the tail holding most
             beyond-null sets matches the tail the passing plant types move.
PROGRAMME    The two corpus verdicts side by side as a table. No pooling across corpora.
FOR PAPER 1  what each outcome would mean for its item-tree bullet, fixed now:
               both NO STRUCTURE DETECTED       the bullet generalises: no IITA-visible dependency
                                                beyond ability and difficulty on two dense corpora
                                                too, now against a demonstrated floor (chains still
                                                excepted).
               any STRUCTURE BEYOND ABILITY     the bullet must be narrowed to sparse MOOCCubeX item
                                                sets: dense skill data do carry IITA-visible
                                                structure; if its tail is not the plants' tail it is
                                                not the planted kind and is not called prerequisite
                                                structure.
               any UNANSWERABLE                 that corpus neither supports nor challenges the
                                                bullet, and Paper 1 may not cite it as
                                                corroboration.
               one NO STRUCTURE, one STRUCTURE  the bullet is corpus-dependent and says so.

DIRECTION: (a, b) in an IITA relation means a is the prerequisite of b ("b mastered implies a
mastered"), per iita.py (DAKS) and surmise_graphs.py. The verdict statistic, an implication count,
does not read orientation; the tail is its sign and is reported, never folded with abs(). The
orientation convention is checked on the plants with shared.direction.reversed_arrow: planted arrows
found as claimed against found reversed in IITA's relation on the planted matrices.

CONTROL SIZE  shared.controls.check_control_scale compares the cells a null draw changes against the
             cells a plant changes; the null must be at least half the median plant (it is ~20-30x).

ORDER        mixing -> nulls and degeneracy -> floor (written) -> observed counts -> verdict.

BUDGET       Worst case 20 sets x 3000 learners with every PAIR and GATE detected: 31 full nulls of
             500 draws per set plus early-stopped chains, ~23 ms CPU a draw at n = 3000. Measured on
             the synthetic run (RUNTIME below). R = 500 is kept; placements were cut from 20 to 15
             (PAIR, GATE) and 10 (CHAIN) before any real run to hold ~45 min per corpus on 4 workers.

SYNTHETIC RESULTS (--synthetic, out/iita-dense-synthetic.json; no corpus read). Two worlds of 10
sets each, 15 skills, 204-3000 learners, 2PL ability model (difficulty U(-2, 0.5), discrimination
U(1, 2)), 5% misclassification, mastery 58-73%; `dependency` adds one PAIR and one GATE per set.
  instrument  null never degenerate at 15 skills (0 of 20; band widths 11-39 implications); mixing
              passes (Hamming ratio >= 0.995, KS 0.13-0.15 against 0.364); direction CLAIMED (all
              450 planted arrows in IITA's relation as claimed, 21 and 52 reversed); control 20-29x.
  floor       FAILS in both worlds. Median per-set detection: PAIR 0.07 / 0.10, GATE 0.03 / 0.13,
              CHAIN 0.10 / 0.15 (none / dependency). Detections split evenly between tails (PAIR 8
              lower / 8 upper and 10 / 10; GATE 5 / 5 and 11 / 7) and the median planted-minus-null
              shift is -2.0 to +0.5 implications against bands 11-39 wide. IITA does put the planted
              edge in its relation (every PAIR plant; both GATE edges), but the COUNT does not move:
              a single dependency among 15 skills is lost in how far IITA's selected quasi-order
              swings between null draws. Chain detection is no lower than PAIR or GATE, so chain
              blindness cannot be distinguished from the general blindness here.
  verdicts    synthetic-none UNANSWERABLE (floor fails; 1 of 10 beyond, upper, p = 0.40);
              synthetic-dependency UNANSWERABLE (floor fails; 1 of 10 beyond, upper, p = 0.40). The
              NO STRUCTURE DETECTED and STRUCTURE BEYOND ABILITY branches were not reached.
  expected    Unless the real matrices behave very differently from these, the real run returns
              UNANSWERABLE on both corpora, and that is the pre-registered reading of it.
Exploratory probes on one n = 1000 synthetic set, run once and not part of this design: PAIR at
strength 1.0 is detected 0 of 12 by the count; five simultaneous PAIRs 4 of 12. A pair-level scan
(minimum standardised counterexample count against the same null) detects 12 of 12 PAIRs but also
fires on 20 of 20 UNPLANTED 2PL worlds: the fixed-margins null is exact only for Rasch-type data, and
unequal discriminations are "structure beyond ability" to it. A sharper statistic needs a null that
holds discrimination too.

RUNTIME  ~23 ms CPU per null draw at n = 3000 (curveball 8, IITA 15). Synthetic: 29-33 s wall per set
on 4 workers, with most plants stopping early. Worst case (every PAIR and GATE detected, 20 sets of
3000): ~20,500 draws a set, ~120 s wall, ~40 min per corpus plus loading.

    python3 iita_dense.py --synthetic [--synthetic-sets 10]       # out/iita-dense-synthetic.json
    python3 iita_dense.py [--corpus both|xes3g5m|assist12]         # out/iita-dense.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "studies/measurement/graph-typology"))
from iita import corrected_iita, iita_from_counts  # noqa: E402
from mooccubex_concept_iita import fixed_margins_null  # noqa: E402
import surmise_graphs as sg  # noqa: E402
from shared.controls import check_control_scale  # noqa: E402
from shared.direction import reversed_arrow  # noqa: E402

SEED = 20260925
K = 15                  # skills per set
MAX_SETS = 20           # sets per corpus, at most
R = 500                 # fixed-margin null draws per matrix (real and planted)
ROUNDS = 30             # global-curveball rounds per null draw
TAIL = 0.025            # per tail, per set
N_PAIR, N_GATE, N_CHAIN = 15, 15, 10   # plant placements per set
STRENGTH = 0.9          # P(fail the dependant | failed a prerequisite)
FLOOR_RATE = 0.8        # median per-set detection rate a floor plant type must reach
CHANCE = 0.05           # per-set false-positive rate the binomial is scored against
MIN_SCORED = 5          # fewer scored sets than this cannot reach binomial p < 0.05 at 2 hits
MIX_REF_DRAWS = 40      # reference-sampler draws in the mixing check
MIX_HAMMING = 0.98      # d(ROUNDS) / d(2 * ROUNDS) must reach this
KS_C01 = 1.628          # two-sample Kolmogorov-Smirnov critical constant at alpha = 0.01
CHUNK = 50              # null draws generated together

VERDICTS = ("UNANSWERABLE", "STRUCTURE BEYOND ABILITY", "NO STRUCTURE DETECTED")


# ----------------------------------------------------------------------------- the instrument

def iita_count(X: np.ndarray, relation: bool = False):
    """Corrected-IITA implication count on a learners x skills 0/1 matrix (the relation too if asked).

    Counts by matrix product, then iita.iita_from_counts; identical to iita.corrected_iita (checked
    against it on every run by `check_equivalence`).
    """
    Xi = X.astype(np.int64)
    b = ((1 - Xi).T @ Xi).tolist()
    p = Xi.sum(0).tolist()
    rel, _, _ = iita_from_counts(b, p, X.shape[0], X.shape[1])
    return (len(rel), rel) if relation else len(rel)


def batch_counts(Y: np.ndarray) -> list[int]:
    """iita_count over a (draws, n, m) stack; the counterexample matrices in one product."""
    Yf = Y.astype(np.float32)                      # counts <= 3000: exact in float32
    b = np.rint(np.matmul((1 - Yf).transpose(0, 2, 1), Yf)).astype(np.int64)
    p = Y.sum(1)
    n, m = Y.shape[1], Y.shape[2]
    return [len(iita_from_counts(b[k].tolist(), p[k].tolist(), n, m)[0]) for k in range(len(Y))]


def check_equivalence(X: np.ndarray) -> None:
    pats = [set(np.flatnonzero(r).tolist()) for r in X]
    ref, _, _ = corrected_iita(pats, X.shape[1])
    _, rel = iita_count(X, relation=True)
    Yf = batch_counts(X[None])[0]
    if rel != ref or Yf != len(ref):
        raise SystemExit("iita_count disagrees with iita.corrected_iita; nothing downstream is valid")


#: popcount of every 15-bit row
POP = np.array([bin(v).count("1") for v in range(1 << 16)], dtype=np.int16)


def curveball(X: np.ndarray, draws: int, rounds: int, rng: np.random.Generator) -> np.ndarray:
    """`draws` independent fixed-margin matrices, each `rounds` global-curveball rounds from X.

    One round pairs every row with another at random (a perfect matching) and, within each pair,
    re-deals the columns where the two rows differ: the row that held k of them gets a uniformly
    random k of them (selection sampling), the other row the rest. Row and column sums are unchanged.
    Uniform stationary distribution: Carstens, Berger & Strona 2018 (global curveball); the
    checkerboard swap of mooccubex_concept_iita.fixed_margins_null is the special case of one
    re-dealt pair of columns. Rows are packed into 16-bit words, which is what makes 10^5 draws
    affordable.
    """
    n, m = X.shape
    Y = np.tile((X.astype(np.uint16) << np.arange(m, dtype=np.uint16)).sum(1).astype(np.uint16),
                (draws, 1))
    base = np.tile(np.arange(n), (draws, 1))
    h = n // 2
    for _ in range(rounds):
        perm = rng.permuted(base, axis=1)
        a, b = perm[:, :h], perm[:, h:2 * h]
        A, B = np.take_along_axis(Y, a, 1), np.take_along_axis(Y, b, 1)
        pool = A ^ B
        need, left = POP[A & pool], POP[pool]
        newA = A & ~pool
        u = rng.random((m, draws, h), dtype=np.float32)
        for c in range(m):
            pc = (pool >> c) & 1
            take = (pc == 1) & (u[c] * left < need)
            newA |= take.astype(np.uint16) << c
            need = need - take
            left = left - pc
        np.put_along_axis(Y, a, newA, 1)
        np.put_along_axis(Y, b, (B & ~pool) | (pool & ~newA), 1)
    return ((Y[..., None] >> np.arange(m, dtype=np.uint16)) & 1).astype(bool)


def null_counts(X: np.ndarray, draws: int, seed, stop_at: int | None = None) -> np.ndarray:
    """Sorted implication counts of `draws` fixed-margin draws from X.

    With `stop_at` (an observed count) drawing stops once the observed is certain to sit inside the
    band: at least lo_idx + 1 draws <= it and at least R - hi_idx draws >= it, which no further draw
    can undo (see `band`). Same decision as the full R, at a fraction of the cost for a plant the
    null absorbs; the returned null is then partial.
    """
    rng = seed if isinstance(seed, np.random.Generator) else np.random.default_rng(seed)
    lo_idx, hi_idx = int(math.floor(TAIL * draws)), int(math.ceil((1 - TAIL) * draws)) - 1
    out = []
    while len(out) < draws:
        if stop_at is not None and out:
            v = np.array(out)
            if (v <= stop_at).sum() > lo_idx and (v >= stop_at).sum() >= draws - hi_idx:
                break
        Y = curveball(X, min(CHUNK, draws - len(out)), ROUNDS, rng)
        if not (np.array_equal(Y.sum(1), np.broadcast_to(X.sum(0), Y.sum(1).shape))
                and np.array_equal(Y.sum(2), np.broadcast_to(X.sum(1), Y.sum(2).shape))):
            raise SystemExit("curveball changed a margin")
        out += batch_counts(Y)
    return np.sort(np.array(out))


def band(null: np.ndarray) -> tuple[int, int]:
    """(2.5th, 97.5th) percentile of a sorted null by order statistic; equal means DEGENERATE."""
    r = len(null)
    return int(null[int(math.floor(TAIL * r))]), int(null[int(math.ceil((1 - TAIL) * r)) - 1])


def tail_of(obs: int, lo: int, hi: int) -> str | None:
    """Strict inequality, so ties with a percentile never score: conservative on a discrete count."""
    return "lower" if obs < lo else "upper" if obs > hi else None


# ----------------------------------------------------------------------------- plants

def gate(X: np.ndarray, prereqs, j: int, rng: np.random.Generator) -> np.ndarray:
    """Learners who fail any of `prereqs` fail j with probability STRENGTH."""
    Y = X.copy()
    failed = ~np.all(X[:, list(prereqs)], axis=1)
    Y[failed & (rng.random(len(X)) < STRENGTH), j] = False
    return Y


def plant(X: np.ndarray, kind: str, rng: np.random.Generator):
    """Plant one dependency at a random placement. Returns (matrix, planted edges, aligned)."""
    m = X.shape[1]
    s = [int(v) for v in rng.choice(m, 3, replace=False)]
    rate = X.mean(0)
    if kind == "pair":
        i, j = s[:2]
        return gate(X, [i], j, rng), {(i, j)}, bool(rate[i] > rate[j])
    if kind == "gate":
        i, k, j = s
        return gate(X, [i, k], j, rng), {(i, j), (k, j)}, bool(min(rate[i], rate[k]) > rate[j])
    # chain: the three skills ordered easiest -> hardest, so the chain runs WITH difficulty
    a, b, c = sorted(s, key=lambda v: (-rate[v], v))
    Y = gate(X, [a], b, rng)
    return gate(Y, [b], c, rng), {(a, b), (b, c)}, True


def plant_job(args):
    """One plant: planted count against the planted matrix's own null."""
    X, kind, seed = args
    rng = np.random.default_rng(seed)
    Y, edges, aligned = plant(X, kind, rng)
    obs, rel = iita_count(Y, relation=True)
    null = null_counts(Y, R, rng, stop_at=obs)
    full = len(null) == R
    lo, hi = band(null) if full else (None, None)
    t = None if not full or lo == hi else tail_of(obs, lo, hi)
    return dict(kind=kind, observed=obs, lo=lo, median=float(np.median(null)), hi=hi, drawn=len(null),
                degenerate=full and lo == hi, tail=t, detected=t is not None, aligned=aligned,
                flips=int((X != Y).sum()), edges=sorted(edges), relation=sorted(rel),
                edges_in=sum(e in rel for e in edges),
                edges_reversed_in=sum((b, a) in rel for a, b in edges))


def null_job(args):
    X, seed = args
    return null_counts(X, R, seed)


# ----------------------------------------------------------------------------- mixing

def hamming_job(args):
    X, rounds, seed = args
    Y = curveball(X, 20, rounds, np.random.default_rng(seed))
    return float((Y != X[None]).sum(axis=(1, 2)).mean())


def reference_job(args):
    X, seed = args
    pats = [set(np.flatnonzero(r).tolist()) for r in X]
    Z = fixed_margins_null(pats, X.shape[1], random.Random(seed))
    M = np.zeros_like(X)
    for r, pat in enumerate(Z):
        M[r, list(pat)] = True
    return iita_count(M)


def ks(a, b) -> float:
    a, b = np.sort(a), np.sort(b)
    grid = np.union1d(a, b)
    return float(np.max(np.abs(np.searchsorted(a, grid, "right") / len(a)
                               - np.searchsorted(b, grid, "right") / len(b))))


# ----------------------------------------------------------------------------- one corpus

def binom_sf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def seed_for(*key) -> np.random.SeedSequence:
    return np.random.SeedSequence([SEED, *key])


def analyse(name: str, cid: int, sets: list[dict], pool: Pool, log, checkpoint) -> dict:
    """sets: [{skills, X}] in construction order. Phases run in the pre-registered order;
    `checkpoint` writes the floor to the output file before any observed count exists."""
    t0 = time.time()
    full = [s for s in sets if s["X"].shape[1] == K]
    short = len(sets) - len(full)
    log(f"\n{'=' * 78}\n{name}: {len(sets)} sets built, {len(full)} of {K} skills, {short} short "
        f"(excluded, counted)")
    if not full:
        return dict(corpus=name, sets_built=len(sets), short=short, verdict="UNANSWERABLE",
                    reason="no set of K skills")
    check_equivalence(full[0]["X"])

    # 1. mixing: Hamming saturation on every set, reference sampler on the first
    ham = pool.map(hamming_job, [(s["X"], r, seed_for(cid, i, 90, r))
                                 for i, s in enumerate(full) for r in (ROUNDS, 2 * ROUNDS)])
    ratios = [ham[2 * i] / ham[2 * i + 1] for i in range(len(full))]
    X0 = full[0]["X"]
    ref = pool.map(reference_job, [(X0, int(seed_for(cid, 0, 91, d).generate_state(1)[0]))
                                   for d in range(MIX_REF_DRAWS)])
    cb = null_counts(X0, MIX_REF_DRAWS, seed_for(cid, 0, 92))
    D = ks(ref, cb)
    Dcrit = KS_C01 * math.sqrt(2 / MIX_REF_DRAWS)
    mixing = dict(rounds=ROUNDS, hamming_ratio_min=min(ratios), ks_vs_reference=D, ks_crit=Dcrit,
                  reference_mean=float(np.mean(ref)), curveball_mean=float(np.mean(cb)),
                  passed=min(ratios) >= MIX_HAMMING and D <= Dcrit)
    log(f"mixing: Hamming d({ROUNDS})/d({2 * ROUNDS}) min {min(ratios):.3f} (need >= {MIX_HAMMING}); "
        f"KS vs fixed_margins_null {D:.3f} (crit {Dcrit:.3f}); means {np.mean(ref):.1f} vs "
        f"{np.mean(cb):.1f}")
    if not mixing["passed"]:
        log("MIXING CHECK FAILED -- no verdict")
        return dict(corpus=name, mixing=mixing, verdict=None, reason="MIXING CHECK FAILED")

    # 2. null and degeneracy per set; the observed count is not computed yet
    nulls = pool.map(null_job, [(s["X"], seed_for(cid, i, 1)) for i, s in enumerate(full)])
    rows = []
    for i, (s, null) in enumerate(zip(full, nulls)):
        lo, hi = band(null)
        rows.append(dict(set=i, skills=s["skills"], learners=int(s["X"].shape[0]),
                         mastery_rate=float(s["X"].mean()), null_lo=lo,
                         null_median=float(np.median(null)), null_hi=hi, degenerate=lo == hi))
    scored = [r for r in rows if not r["degenerate"]]
    log(f"degenerate: {len(rows) - len(scored)} of {len(rows)}")
    if not scored:
        return dict(corpus=name, sets_built=len(sets), short=short, degenerate=len(rows), scored=0,
                    mixing=mixing, verdict="UNANSWERABLE", reason="every set degenerate")

    # 3. detection floor on the scored sets' own matrices
    t1 = time.time()
    jobs = [(full[r["set"]]["X"], kind, seed_for(cid, r["set"], 2 + k, rep))
            for r in scored for k, (kind, n) in enumerate((("pair", N_PAIR), ("gate", N_GATE),
                                                           ("chain", N_CHAIN))) for rep in range(n)]
    res = pool.map(plant_job, jobs, chunksize=1)
    per = {}
    for (_, kind, _), o in zip(jobs, res):
        per.setdefault(kind, []).append(o)
    floor = {}
    it = iter(res)
    by_set = {r["set"]: {} for r in scored}
    for r in scored:
        for kind, n in (("pair", N_PAIR), ("gate", N_GATE), ("chain", N_CHAIN)):
            by_set[r["set"]][kind] = [next(it) for _ in range(n)]
    for kind in ("pair", "gate", "chain"):
        rates = [np.mean([o["detected"] for o in by_set[s][kind]]) for s in by_set]
        outs = per[kind]
        det = [o for o in outs if o["detected"]]
        al = [o for o in outs if o["aligned"]]
        mis = [o for o in outs if not o["aligned"]]
        lower, upper = sum(o["tail"] == "lower" for o in det), sum(o["tail"] == "upper" for o in det)
        edges = [o["edges_in"] for o in outs]
        floor[kind] = dict(
            median_rate=float(np.median(rates)) if rates else 0.0,
            per_set_rates=[float(v) for v in rates],
            detected_lower=lower, detected_upper=upper,
            tail="lower" if lower > upper else "upper" if upper > lower else "none",
            median_shift=float(np.median([o["observed"] - o["median"] for o in outs])),
            rate_aligned=float(np.mean([o["detected"] for o in al])) if al else None,
            rate_misaligned=float(np.mean([o["detected"] for o in mis])) if mis else None,
            planted_degenerate=sum(o["degenerate"] for o in outs),
            planted_edges_recovered=float(np.mean(edges)) if edges else 0.0,
            planted_edges_reversed=float(np.mean([o["edges_reversed_in"] for o in outs])),
            median_flips=float(np.median([o["flips"] for o in outs])))
    floor_pass = any(floor[k]["median_rate"] >= FLOOR_RATE for k in ("pair", "gate"))
    plant_tails = sorted({floor[k]["tail"] for k in ("pair", "gate")
                          if floor[k]["median_rate"] >= FLOOR_RATE})
    # IITA's (a, b) reads "a is the prerequisite of b"; the plants know which way is true. Edges are
    # keyed by plant so reversing the set reverses every planted arrow inside its own plant.
    planted = [o for k in ("pair", "gate") for o in per[k]]
    rels = [set(map(tuple, o["relation"])) for o in planted]
    arrows = {((q, a), (q, b)) for q, o in enumerate(planted) for a, b in o["edges"]}
    direction = reversed_arrow(lambda E: sum((a, b) in rels[q] for (q, a), (_, b) in E), arrows)
    claimed, reverse = direction["claimed"], direction["reversed"]
    for o in res:
        del o["relation"], o["edges"]
    null_h = float(np.median([ham[2 * i] for i in range(len(full)) if not rows[i]["degenerate"]]))
    scale = check_control_scale({"pair": floor["pair"]["median_flips"],
                                 "gate": floor["gate"]["median_flips"], "null": null_h}, ["null"])
    log(f"floor ({time.time() - t1:.0f}s, {len(jobs)} plants x {R} draws):")
    for kind in ("pair", "gate", "chain"):
        f = floor[kind]
        log(f"  {kind:<5} median per-set detection {f['median_rate']:.2f}  tail: {f['detected_lower']} "
            f"lower / {f['detected_upper']} upper  median shift {f['median_shift']:+.1f}  "
            f"aligned {f['rate_aligned']} misaligned {f['rate_misaligned']}")
    log(f"  floor {'PASSES' if floor_pass else 'FAILS'}; plants move the {'/'.join(plant_tails) or '-'} "
        f"tail; direction check {direction['verdict']} (planted arrow in IITA's relation "
        f"{claimed:.0f}, reversed {reverse:.0f})\n  {scale['report']}")
    floor_block = dict(floor=floor, floor_pass=floor_pass, plant_tails=plant_tails,
                       direction=direction, control_scale=scale["report"])
    checkpoint(dict(corpus=name, sets_built=len(sets), short=short, mixing=mixing,
                    degenerate=len(rows) - len(scored), scored=len(scored),
                    sets=[{k: v for k, v in r.items()} for r in rows], **floor_block,
                    verdict=None, reason="floor written; observed counts not yet computed"))

    # 4. observed counts, read only now
    for r in rows:
        r["observed"] = iita_count(full[r["set"]]["X"])
        r["tail"] = None if r["degenerate"] else tail_of(r["observed"], r["null_lo"], r["null_hi"])
    k_lo = sum(r["tail"] == "lower" for r in scored)
    k_hi = sum(r["tail"] == "upper" for r in scored)
    n = len(scored)
    p = binom_sf(k_lo + k_hi, n, CHANCE) if n else 1.0
    degenerate = len(rows) - n
    if not floor_pass:
        verdict, reason = "UNANSWERABLE", "floor fails"
    elif degenerate * 2 > len(rows):
        verdict, reason = "UNANSWERABLE", "more than half the sets degenerate"
    elif n < MIN_SCORED:
        verdict, reason = "UNANSWERABLE", f"fewer than {MIN_SCORED} scored sets"
    elif p < 0.05:
        verdict, reason = "STRUCTURE BEYOND ABILITY", ""
    else:
        verdict, reason = "NO STRUCTURE DETECTED", ""
    dominant = "lower" if k_lo > k_hi else "upper" if k_hi > k_lo else "none"
    match = None if not plant_tails or dominant == "none" else dominant in plant_tails
    log(f"observed: {k_lo + k_hi} of {n} scored sets beyond the null ({k_lo} lower, {k_hi} upper); "
        f"binomial p = {p:.3g} against {CHANCE}")
    log(f"VERDICT {name}: {verdict}{' (' + reason + ')' if reason else ''}; beyond-null tail "
        f"{dominant}, plants {'/'.join(plant_tails) or '-'}, match {match}")
    return dict(corpus=name, sets_built=len(sets), short=short, sets=rows, degenerate=degenerate,
                scored=n, mixing=mixing, **floor_block, beyond_lower=k_lo, beyond_upper=k_hi,
                binomial_p=p, verdict=verdict, reason=reason, beyond_tail=dominant,
                tail_matches_plants=match, seconds=time.time() - t0,
                seconds_per_set=(time.time() - t0) / len(full))


def programme(results: list[dict]) -> list[dict]:
    return [dict(corpus=r["corpus"], verdict=r["verdict"], scored=r.get("scored"),
                 degenerate=r.get("degenerate"), beyond_lower=r.get("beyond_lower"),
                 beyond_upper=r.get("beyond_upper"), binomial_p=r.get("binomial_p"),
                 floor_pair=r.get("floor", {}).get("pair", {}).get("median_rate"),
                 floor_gate=r.get("floor", {}).get("gate", {}).get("median_rate"),
                 floor_chain=r.get("floor", {}).get("chain", {}).get("median_rate"))
            for r in results]


# ----------------------------------------------------------------------------- inputs

def real_sets(name: str) -> list[dict]:
    """surmise_graphs' construction, unchanged but for the set cap."""
    sg.SETS = MAX_SETS
    loader = {"xes3g5m": sg.xes3g5m, "assist12": sg.assist12}[name]
    state = sg.mastery(loader())
    out = []
    for skills, learners in sg.skill_sets(state, K, random.Random(SEED)):
        X = np.array([[state[c][u] for c in skills] for u in learners], dtype=bool)
        out.append(dict(skills=skills, X=X))
    return out


def synthetic_sets(world: str, n_sets: int, seed: int) -> list[dict]:
    """Shaped like the real sets: 15 skills, 200-3000 learners (set 0 at the 3000 cap, for timing),
    one latent ability, per-skill difficulty and discrimination, 5% misclassification of the
    mastery state. `dependency` plants one pairwise prerequisite and one conjunctive gate per set
    into the latent states before misclassification."""
    rng = np.random.default_rng(seed)
    out = []
    for s in range(n_sets):
        n = 3000 if s == 0 else int(round(math.exp(rng.uniform(math.log(200), math.log(3000)))))
        theta = rng.normal(size=(n, 1))
        d = rng.uniform(-2.0, 0.5, size=K)
        a = rng.uniform(1.0, 2.0, size=K)
        X = rng.random((n, K)) < 1 / (1 + np.exp(-a * (theta - d)))
        if world == "dependency":
            X, _, _ = plant(X, "pair", rng)
            X, _, _ = plant(X, "gate", rng)
        X ^= rng.random(X.shape) < 0.05
        out.append(dict(skills=[f"s{j:02d}" for j in range(K)], X=X))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true", help="run the pipeline on synthetic worlds")
    ap.add_argument("--synthetic-sets", type=int, default=10)
    ap.add_argument("--corpus", choices=("both", "xes3g5m", "assist12"), default="both")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    lines = []

    def log(s=""):
        print(s, flush=True)
        lines.append(s)

    with Pool(args.workers) as pool:
        if args.synthetic:
            out = args.out or HERE / "out" / "iita-dense-synthetic.json"
            corpora = [(f"synthetic-{w}", lambda w=w, i=i: synthetic_sets(w, args.synthetic_sets, SEED + i))
                       for i, w in enumerate(("none", "dependency"))]
        else:
            names = ("xes3g5m", "assist12") if args.corpus == "both" else (args.corpus,)
            out = args.out or HERE / "out" / ("iita-dense.json" if args.corpus == "both"
                                             else f"iita-dense-{args.corpus}.json")
            corpora = [(nm, lambda nm=nm: real_sets(nm)) for nm in names]
        results = []

        def checkpoint(partial):
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(dict(partial=True, corpora=results + [partial]), indent=1,
                                      default=str) + "\n")

        for cid, (name, build) in enumerate(corpora):
            results.append(analyse(name, cid, build(), pool, log, checkpoint))
    table = programme(results)
    log(f"\n{'corpus':<22} {'verdict':<26} {'scored':>6} {'degen':>5} {'lo':>3} {'hi':>3} "
        f"{'p':>8} {'pair':>5} {'gate':>5} {'chain':>5}")
    for t in table:
        log(f"{t['corpus']:<22} {str(t['verdict']):<26} {t['scored'] or 0:>6} {t['degenerate'] or 0:>5} "
            f"{t['beyond_lower'] or 0:>3} {t['beyond_upper'] or 0:>3} {t['binomial_p'] or 1:>8.3g} "
            f"{t['floor_pair'] or 0:>5.2f} {t['floor_gate'] or 0:>5.2f} {t['floor_chain'] or 0:>5.2f}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(synthetic=args.synthetic, seed=SEED, k=K, draws=R, rounds=ROUNDS,
                                   placements=dict(pair=N_PAIR, gate=N_GATE, chain=N_CHAIN),
                                   strength=STRENGTH, workers=args.workers, programme=table,
                                   corpora=results), indent=1, default=str) + "\n")
    log(f"wrote {out}")


if __name__ == "__main__":
    main()
