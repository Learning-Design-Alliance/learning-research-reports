"""
Lag decay, forgetting of A or the edge weakening: re-registration with a floor matched to each corpus.

WHAT THIS IS. A re-registration of `studies/identifiability/lag-forgetting/` (v1 below; its script is
`lag_forgetting.py`, its record `README.md` and `out/`). v1 asked whether the shrinking of Paper II's
prerequisite drop with the lag between A and B (lag_bands' D < 0, F1) is forgetting of A or the edge
weakening. Its revised primary (the "Wald split", v1 CHANGES 2026-10-07, item 1) never confused the
planted worlds in its synthetic floor, but failed the registered pass rule on power (EDGE detected in 2
of 3 seeds, rule 3 of 3), so every v1 verdict is UNANSWERABLE. A 9,000-learner floor passed, but only
as information. This study keeps v1's estimand and verdict rule unchanged and replaces only the floor.
The new floor is sized to each corpus's real usable pair and learner counts, with enough seeds for the
pass rule to mean something. Then the real data are re-read under the new gate.

READ THIS FIRST: A RE-REGISTRATION AFTER SEEING ESTIMATES. v1's real-data numbers have already been
computed, written to v1's `out/lag_forgetting.json` and README, and read by the author of this file. For the
held pairs, the as-computed values were: Eedi share explained +1.05 [+0.81, +1.43], which would read
MOSTLY-FORGETTING; ASSISTments and EdNet NO-DECAY-TO-SPLIT; XES3G5M 17 held pairs, so UNANSWERABLE. The
re-run below uses the same code, pairs and bootstrap seed, so it reproduces those numbers exactly. It is
not new data.
  What this licenses: a test of whether the instrument has enough power to be read at each corpus's real
  size, with the floor and pass rule fixed here before the floor is run. The estimand, the verdict strings
  and thresholds and the programme rule are v1's. They were registered before any real corpus was read
  (v1 commits 62fb970 and 49206aa) and are not changed. The planted worlds, their effect sizes and
  mechanism are v1's exactly. None was tuned to the real estimates. What changes is how many pairs and
  cases the floor has, and those come from outcome-free counts.
  What this does not license: reading the real verdicts as an independent replication, or as a test
  whose result was unknown when the test was chosen. The decision to re-register was made after the v1
  estimates had been seen. The 9,000-learner diagnostic was run before v1 read any real data; the
  proposal to re-register is in v1's README, which was written after the real run. A verdict that passes
  here says the instrument, at this corpus's size, can tell v1's planted worlds apart. It says nothing
  new about the data. Confirmation needs data not yet read: another corpus, or another sample of EdNet
  learners beyond v1's 6,000-learner prefix.

LITERATURE (Paper II literature review, `research/readiness/learning-graph-budget-2026/literature.md`,
synthesis row 4, strand C): 2.20 Matayoshi, Cosyn, Uzun & Kurd-Misto (2025), JEDM 17(1). In a randomized
ALEKS experiment, the retention advantage of the higher mastery threshold on the same topic shrinks over
weeks: the two readings of a shrinking advantage. 2.14 Cepeda et al. (2008), Psych. Sci. 19(11): a lag
profile need not be monotone. v1's shape test is not re-registered here (see SCOPE).

DATA. Reads three licensed corpora through v1's loaders (`lag_forgetting.loaders()`, i.e. lag_bands'
adapters). Only aggregates are written: no learner rows, item text or skill names. B items appear in
`out/sizing.json` only as integer codes.
  ASSISTments 2012-13 skill builders  build_matrix.LOADERS["assist"] (assist_rich.csv), skill_id grain
  EdNet KT1                           atlas.ednet_rows (ednet-kt1.zip, prefix of 6,000 learners)
  Eedi NeurIPS 2020                   atlas.eedi_rows (answers.tsv), level-3 subject grain, latest answers
XES3G5M is out: v1 found 17 held pairs (< MIN_BOTH = 30), so it is UNANSWERABLE on positivity and is not
re-read. Corpora come from $LDA_SCRATCH_DIR through shared.paths.data_path, via the adapters. No file is
derived.

ESTIMAND (v1's, imported, unchanged: `lag_forgetting.primary_wald`). The cases are learners with >= 2 A
attempts before their first B attempt, the last of them within W = 1 day of B. The arm is MASTERED' if
an A attempt before that last one was correct, FAILED' otherwise. R is the outcome of the last A
attempt, a fresh reading of A in both arms. Per band (EARLY lag < 1 d, LATE >= 7 d), over the held pairs
(>= 5 cases per arm in both bands, MASTERED' B rate inside (0.01, 0.99)), the computation is:
drop = mean p(B | M') - p(B | F'); gap = mean p(R | M') - p(R | F'); E = drop / gap.
D_sub = drop_LATE - drop_EARLY; D_held = drop_LATE x gap_EARLY / gap_LATE - drop_EARLY.
share explained = (D_sub - D_held) / D_sub, signed. The intervals are 95% from 2,000 cluster-bootstrap
draws resampling B items (seed 0, as in v1).
Verdicts, in order (v1's, unchanged): UNANSWERABLE (< 30 held pairs); UNRESOLVED-NO-A-GAP (gap_EARLY or
gap_LATE interval not entirely above 0); NO-DECAY-TO-SPLIT (D_sub interval not entirely below 0);
MOSTLY-FORGETTING (share >= 0.5 and Delta = D_held - D_sub interval entirely above 0); EDGE-WEAKENS
(D_held interval entirely below 0 and share < 0.5); UNRESOLVED otherwise. Programme (v1's): LAG DECAY IS
FORGETTING OF A if >= 2 corpora MOSTLY-FORGETTING and none EDGE-WEAKENS; THE EDGE WEAKENS WITH LAG if
>= 2 EDGE-WEAKENS and none MOSTLY-FORGETTING; CORPUS-DEPENDENT if at least one of each; UNRESOLVED
otherwise. Corpora that are UNANSWERABLE count toward neither. DIRECTION: every comparison is signed,
with D < 0 meaning decay, exactly as v1.
  What the string MOSTLY-FORGETTING names (v1 README, kept): the decay tracks the narrowing of the arms'
  current A gap. It does not say which arm moved. A SECONDARY DESCRIPTIVE is therefore registered here:
  on the held pairs and from the same bootstrap draws, the change from EARLY to LATE in each arm's
  current A accuracy (rM, rF) and B accuracy (pM, pF), with 95% intervals. The forgetting signature is
  rM falling. The catching-up signature is rF rising. These changes are descriptive and gate nothing.

POSITIVITY AND SIZING (step 1; outcome-free; run after this design is committed, before the floor). v1's
10,000 pairs are re-drawn per corpus, identically (every ordered item pair, then atlas.corpus_rng(name)).
For each pair, the number of Wald cases is counted per band and arm: wald_m and wald_f in EARLY and LATE.
The count uses v1's `cases()` and reads only lag, recency, number of A attempts and the prior-mastery
arm, never y or R. A pair is COUNT-READABLE if each of its four cells has >= MIN_CELL (5) cases. The
held pairs are the subset whose outcomes also keep the MASTERED' B rate inside (0.01, 0.99), so the
count-readable set contains v1's 59 / 632 / 2,692 held pairs. Written to out/sizing.json: learners,
items, pairs, count-readable pairs, distinct B items among them, distinct learners in their Wald cells,
cell-size quantiles, and per count-readable pair [B code, mE, fE, mL, fL]. A corpus with < 30
count-readable pairs is UNANSWERABLE on positivity, and no floor is run for it.

THE MATCHED FLOOR. For each corpus, one synthetic copy is built per seed. It has exactly that corpus's
count-readable pairs. Each synthetic pair has exactly its real pair's four cell sizes (mE, fE, mL, fL),
and its real pair's B code, so the B-item bootstrap resamples the real cluster structure (pairs sharing
a B). The pair and learner counts that set the power are therefore the real ones, cell by cell. Each
case's (R, y) is drawn from v1's planted world for one gated (A, B) pair:
  v1's per-learner process for a single parent -> child pair, simulated case by case. The learner has
  ability ~ N(0, 0.5) and a latent state for A. An attempt is correct with probability
  sigmoid(logit(1 - SLIP or GUESS) + ability) (SLIP 0.10, GUESS 0.20), clipped to [0.02, 0.98]. A
  not-held item is learned after an attempt with probability LEARN = 0.3. A's first touch is a block of
  1-3 attempts. Then come the items between A and B in a random 48-item order: gap g with
  P(g) proportional to 48 - g, and g - 1 items in between, each taking 1-3 ticks plus a parent-review
  tick with probability 0.25. With probability REVIEW = 0.5 there is a review of A one tick before B.
  B's first attempt comes one tick later. A tick lasts Exp(mean 0.01 d) with probability 0.8 and
  Exp(mean 5 d) otherwise; this is v1's session clock. Worlds (v1's, exactly; tau = 10 d, GATE = 0.30):
    FORGET  held A is lost at each A or B touch with probability 1 - exp(-dt / tau); constant gate
    EDGE    no forgetting; B's first attempt loses GATE x exp(-lag / tau) if A is not held
    NULL    no forgetting; constant gate (B loses GATE if A is not held)
  (v1's HUMP world served only the shape test, which is out of scope here.) Cases are simulated in large
  batches. Each is classified exactly as v1's `cases()` would classify it, and cases are dealt to the
  pairs' cells without replacement. Every synthetic pair's cells are fresh, independent cases. Cell
  statistics use v1's `_drop`, and the verdict uses v1's `primary_wald`. Nothing is re-implemented.
  Departures from v1's agent simulation, and why they are harmless or conservative: (a) A's own first
  attempt is not gated by A's parent; (b) the 0.25 parent-review rate for in-between items is
  approximate; (c) every pair is a gated pair with identical items, as in v1's floor, while real pairs
  are arbitrary and heterogeneous; (d) cases are independent across pairs, while real pairs share learners
  and A items. (c) and (d) make the synthetic B-item bootstrap better calibrated than the real one, so a
  pass here is a lower bound on what the real instrument needs, not a guarantee. The caveat is stated in
  the README.
  CALIBRATION (run before the floor; gates nothing). v1's agent floor (`lag_forgetting.synth`, 3,000
  learners, seeds 200-202, gated pairs) is re-run for FORGET, EDGE and NULL, and its per-pair Wald cell
  counts are recorded. The case simulator is then run with exactly those counts (10 seeds per world).
  For each world, the means of drop_EARLY, drop_LATE, gap_EARLY and gap_LATE are compared with the agent
  floor's. The generator is called FAITHFUL if every difference is <= 0.02. If not, one dated CHANGES
  entry may correct the generator's fidelity to v1's process, never its effect sizes, before the floor
  is run. A second failure is reported, and the floor then runs on the generator as it stands.

PASS RULE (per corpus; fixed here; 40 seeds per world; S = 40).
  FORGET -> MOSTLY-FORGETTING in >= 0.80 of seeds (>= 32 of 40)
  EDGE   -> EDGE-WEAKENS      in >= 0.80 of seeds (>= 32 of 40)
  wrong-world calls: FORGET -> EDGE-WEAKENS <= 0.05 (<= 2 of 40), and EDGE -> MOSTLY-FORGETTING
         <= 0.05 (<= 2 of 40)
  false calls: NULL -> MOSTLY-FORGETTING or EDGE-WEAKENS <= 0.10 (<= 4 of 40)
  All five must hold. Each rate is reported with its Clopper-Pearson 95% interval (descriptive). The
  shortened rule of v1 (3 of 3) could not separate a 0.67 detector from a 1.0 one. Under this rule,
  a detector whose true rate is 0.65 passes the 32-of-40 bar with probability 0.03 (0.11 at 0.70), and a
  NULL world with the nominal 0.025 false rate exceeds 4 of 40 with probability 0.003.
  CORPUS GATE: a corpus whose matched floor fails is UNANSWERABLE, and its computed verdict is written
  beside it as `verdict_as_computed`, as in v1. Corpora are NOT pooled. No pooled estimand is
  registered, so none may be used to rescue power.

REAL RUN (after the floor). For each corpus that passes, v1's pipeline is re-run on the same pairs:
pair_stats(cases(...)), then primary_wald(stats, B items, seed=0), plus the secondary descriptive above.
The result is checked against v1's `out/lag_forgetting.json`. Every statistic must reproduce to 1e-12,
or the difference is reported and explained. Corpora whose floor fails are also re-run, so that the
reproduction check covers them, and are reported UNANSWERABLE.

SCOPE. Only the primary split is re-registered. v1's single-reading split (failed structurally), its
descriptive arms table (needs no floor) and its rise-then-fall shape test (UNANSWERABLE in v1) are not
re-run. The shape test would need its own matched floor and is left to a separate re-registration.

WHAT IT CAN AND CANNOT SAY (v1's caveats stand). The two arms differ in who re-attempts A within a day of
B. Learners differ across bands. The Wald ratio assumes that past mastery moves B only through A's
current state, plus a component that is constant across bands. The B-item bootstrap does not absorb
shared A items or shared learners. Eedi keeps only each learner's latest answer per question. The planted
effects are v1's size: the floor certifies power to see those effects, not effects of the size the data
show. EdNet's real A gap (about 0.05) is a fifth of the planted one (about 0.25), and the verdict rule's
own intervals, not the floor, are what guard a real reading against that. No coded constructs: every
quantity is a count of logged outcomes.

    python3 lag_forgetting_v2.py sizing      [--corpora assist,ednet,eedi]   (outcome-free counts)
    python3 lag_forgetting_v2.py calibrate                                    (synthetic only)
    python3 lag_forgetting_v2.py floor       [--corpora ...]                  (synthetic, sized)
    python3 lag_forgetting_v2.py real        [--corpora ...]

CHANGES

2026-10-07, after the calibration and before the matched floor or any real outcome was read. Sizing
(outcome-free counts) was running in parallel. The first calibration DEPARTED
(`out/calibration_v1_departs.json`): the case generator's A gaps were 0.015-0.03 below the agent's in
every world, and FORGET's gap_LATE was 0.023 above it. Two causes were found and fixed, and the effect
sizes were not touched:
  1. IMPLEMENTATION BUG. The recency test compared a clock in days with v1's W, which is in seconds
     (86,400). Every case with >= 2 A attempts therefore counted as "recent", including LATE cases with
     no review, whose last A reading came weeks before B. Fixed to W / DAY. The diagnostic was that the
     LATE cells had n_before = 4 for 0.20 of cases, against the agent's 0.34, and the MASTERED' arm's R
     was 0.38, against the agent's 0.28.
  2. FIDELITY. v1's agent gates EVERY item's first attempt on that item's own parent, so A's first
     attempt loses the gate when A's parent is touched before A and not held. The generator now
     simulates A's parent P: touched before A with probability 1/3 given A before B, except for A = i0;
     P gets its own block, the in-between items, and a review of P with probability REVIEW. A's first
     attempt loses the world's gate if P is not held then. This is the only change to the generator's
     mechanism.
  Second calibration (`out/calibration.json`): FORGET and NULL are FAITHFUL (largest differences: FORGET
  gap_EARLY -0.010, NULL gap_EARLY -0.015). EDGE DEPARTS on gap_EARLY only (case simulator 0.216 against the
  agent's 0.238, a difference of -0.022 over a 0.02 tolerance; the other EDGE differences are -0.008,
  +0.003 and +0.000). As registered, the second result is reported, and the floor runs on the
  generator as it stands. The departure goes in the conservative direction: a smaller A gap makes the
  Wald ratio noisier, and the case generator's EDGE decay on the Wald subset is also smaller
  (drop 0.054 -> 0.035, against the agent's 0.062 -> 0.032), so EDGE is harder to detect here than in
  v1's agent world. At v1's floor counts the case generator reads EDGE-WEAKENS in 2 of 10 seeds,
  against the agent's 2 of 3. Tolerance note: the 0.02 tolerance was set without reference to the
  agent's own seed-to-seed noise; the agent's 3-seed mean of gap_EARLY has a standard error of about
  0.006-0.015. Nothing else changed: worlds, pass rule, seeds and estimand are as first registered.

2026-10-07, implementation only, during the Eedi floor. The Eedi floor process reached the session's
2-hour background limit during its NULL world and was stopped. Its FORGET (MOSTLY-FORGETTING 40 of 40)
and EDGE (EDGE-WEAKENS 40 of 40) tallies had been printed, but nothing had been written, because the
floor wrote once per corpus. The floor now writes each world to `out/floor_parts/<corpus>_<world>.json`
as it finishes, takes `--worlds` so that worlds can run as separate processes, and assembles
`out/floor.json` once every world is present. Seeds are keyed by (corpus, world, seed), so the re-run
reproduces the stopped run exactly. The FORGET and EDGE tallies were re-run and compared with the
printed ones. The ASSISTments and EdNet floors were already written and are not re-run (their parts are
not split out). Nothing in the design changed.
"""

from __future__ import annotations

import bisect
import json
import math
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
V1 = REPO / "studies/identifiability/lag-forgetting"
sys.path.insert(0, str(V1))

import lag_forgetting as v1  # noqa: E402  (also puts overlap/ and latent-shape/ on the path)
from lag_forgetting import (BANDS, DAY, GATE, GUESS, LEARN, MAX_PAIRS, MIN_BOTH, MIN_CELL,  # noqa: E402
                            REVIEW, SLIP, W, band, boot_weights, build, cases, ci, pair_stats,
                            primary_wald, wmean)

CORPORA = ["assist", "ednet", "eedi"]
SEEDS = 40
WORLDS = ["FORGET", "EDGE", "NULL"]
TAU, ITEMS = 10.0, 48
P_REV_BETWEEN = 0.25
PASS = dict(detect=0.80, wrong=0.05, null_false=0.10)
OUT = HERE / "out"


# ------------------------------------------------------------------ pairs and sizing (outcome-free)

def corpus_pairs(name, idx):
    import atlas
    items = sorted(idx)
    pairs = [(a, b) for a in items for b in items if a != b]
    rng = atlas.corpus_rng(name)
    if len(pairs) > MAX_PAIRS:
        pairs = [pairs[i] for i in rng.choice(len(pairs), MAX_PAIRS, replace=False)]
    return items, pairs


def wald_counts(cs):
    """[mE, fE, mL, fL] from v1 cases(): reads lag, recent, n_before, m_prior only (never y or R)."""
    c = [0, 0, 0, 0]
    for lag, _m, recent, _r, _y, nb, mp in cs:
        if recent and nb >= 2:
            b = band(lag, BANDS)
            if b == "EARLY":
                c[0 if mp else 1] += 1
            elif b == "LATE":
                c[2 if mp else 3] += 1
    return c


def wald_learners(a, b, tl, idx):
    """Learners in the pair's EARLY/LATE Wald cells (the same filter as cases(); for the learner count)."""
    out = set()
    for learner, tb, _y in idx[b]:
        rec = tl[learner].get(a)
        if rec is None or rec[0][0] >= tb:
            continue
        ts = rec[0]
        j = bisect.bisect_left(ts, tb) - 1
        if (tb - ts[j]) <= W and j + 1 >= 2 and band((tb - ts[0]) / DAY, BANDS) in ("EARLY", "LATE"):
            out.add(learner)
    return out


def load(name):
    from lag_bands import to_seconds
    L = v1.loaders()
    rows = ((u, i, ok, to_seconds(t), h1, h2) for u, i, ok, t, h1, h2 in L[name]())
    return build(rows)


def run_sizing(names):
    path = OUT / "sizing.json"
    res = json.loads(path.read_text())["corpora"] if path.exists() else {}
    for name in names:
        t0 = time.time()
        tl, idx = load(name)
        items, pairs = corpus_pairs(name, idx)
        code = {it: k for k, it in enumerate(items)}
        cells, learners = [], set()
        for a, b in pairs:
            c = wald_counts(cases(a, b, tl, idx))
            if min(c) >= MIN_CELL:
                cells.append([code[b]] + c)
                learners |= wald_learners(a, b, tl, idx)
        arr = np.array(cells, dtype=int).reshape(-1, 5)
        q = {}
        for k, lab in enumerate(["mE", "fE", "mL", "fL"], start=1):
            v = arr[:, k] if len(arr) else np.zeros(1)
            q[lab] = dict(total=int(v.sum()), min=int(v.min()),
                          quantiles_10_25_50_75_90=[float(x) for x in np.percentile(v, [10, 25, 50, 75, 90])])
        res[name] = dict(learners=len(tl), items=len(items), pairs=len(pairs), count_readable_pairs=len(cells),
                         distinct_B=int(len(set(arr[:, 0]))) if len(arr) else 0,
                         distinct_learners_in_cells=len(learners), cell_sizes=q,
                         answerable_on_positivity=len(cells) >= MIN_BOTH, cells=cells)
        del tl, idx
        print(f"  {name:7s} learners {res[name]['learners']:,d}  count-readable pairs {len(cells):,d}  "
              f"distinct B {res[name]['distinct_B']}  learners in cells {len(learners):,d}  "
              f"median cells mE {q['mE']['quantiles_10_25_50_75_90'][2]:.0f} fE {q['fE']['quantiles_10_25_50_75_90'][2]:.0f} "
              f"mL {q['mL']['quantiles_10_25_50_75_90'][2]:.0f} fL {q['fL']['quantiles_10_25_50_75_90'][2]:.0f}  "
              f"({time.time() - t0:.0f} s)", flush=True)
        OUT.mkdir(exist_ok=True)
        path.write_text(json.dumps(dict(note="outcome-free Wald cell counts on v1's 10,000 pairs; "
                                             "cells = [B code, mE, fE, mL, fL] per count-readable pair",
                                        min_cell=MIN_CELL, corpora=res)) + "\n")


# ------------------------------------------------------------------ case-level simulator (v1's world)

def _sig(x):
    return 1.0 / (1.0 + np.exp(-x))


def _logit(p):
    return math.log(p / (1 - p))


def _ticks(rng, k):
    """Sum of k iid v1 clock ticks (days), k an int array: 0.8 Exp(0.01) + 0.2 Exp(5)."""
    k = np.asarray(k)
    k2 = rng.binomial(k, 0.2)
    return rng.gamma(k - k2, 0.01) + rng.gamma(k2, 5.0)


def simulate(world, n, rng):
    """n independent learner-pair cases of v1's process for one gated pair. Returns (cell, R, y), with cell
    0 = EARLY M', 1 = EARLY F', 2 = LATE M', 3 = LATE F', -1 = not a Wald case in EARLY or LATE."""
    forget = world == "FORGET"
    ab = rng.normal(0.0, 0.5, n)
    held = np.zeros(n, bool)
    last = np.zeros(n)
    lp, lg = _logit(1 - SLIP), _logit(GUESS)

    def gate(lag):
        return GATE * np.exp(-lag / TAU) if world == "EDGE" else np.full(n, GATE)

    def between_ticks():
        # items between two touches in a random 48-item order: P(g) proportional to 48 - g, g - 1 items
        # between, each a parent-review tick with probability 0.25 plus 1-3 attempt ticks
        # (sum of `between` iid U{1,2,3} = between + sum of U{0,1,2})
        gs = np.arange(1, ITEMS)
        g = rng.choice(gs, n, p=(ITEMS - gs) / (ITEMS - gs).sum())
        between = g - 1
        u = rng.integers(0, 3, (n, ITEMS - 2))
        u_sum = (u * (np.arange(ITEMS - 2)[None, :] < between[:, None])).sum(axis=1)
        return _ticks(rng, rng.binomial(between, P_REV_BETWEEN) + between + u_sum)

    # CHANGES 2026-10-07 (calibration): A's own parent P in v1's chain. P was touched before A with
    # probability 1/3 given A before B (orderings PAB of PAB, APB, ABP), except when A = i0 (1 of 47 gated
    # pairs). P gets its own 1-3 attempt block, then the in-between items, then a review of P with
    # probability REVIEW, then A's first attempt one tick later. A's FIRST attempt loses the world's gate
    # if P is not held then (v1's agent does this for every item's first attempt). Only P's held state is used.
    hasP = (rng.random(n) < 1 / 3) & (rng.random(n) >= 1 / 47)
    heldP, lastP = np.zeros(n, bool), np.zeros(n)
    tP = np.zeros(n)
    nP = rng.integers(1, 4, n)

    def touchP(mask, now):
        nonlocal heldP
        if forget:
            heldP = heldP & ~(mask & heldP & (rng.random(n) > np.exp(-(now - lastP) / TAU)))
        lastP[mask] = now[mask]
        k = heldP.copy()
        heldP = heldP | (mask & ~k & (rng.random(n) < LEARN))
        return k

    for j in range(3):
        mask = hasP & (j < nP)
        if j > 0:
            tP = np.where(mask, tP + _ticks(rng, mask.astype(int)), tP)
        touchP(mask, tP)
    tP = tP + between_ticks()
    revP = hasP & (rng.random(n) < REVIEW)
    tP = np.where(revP, tP + _ticks(rng, np.ones(n, int)), tP)
    touchP(revP, tP)
    tA0 = tP + _ticks(rng, np.ones(n, int))          # A's first attempt, on P's clock (P first touched at 0)
    if forget:
        heldP = heldP & ~(hasP & heldP & (rng.random(n) > np.exp(-(tA0 - lastP) / TAU)))
    lossA = np.where(hasP & ~heldP, gate(tA0), 0.0)

    def attempt(mask, now, loss=0.0):
        nonlocal held
        if forget:
            lose = held & mask & (rng.random(n) > np.exp(-(now - last) / TAU))
            held = held & ~lose
        last[mask] = now[mask]
        k = held.copy()
        p = np.clip(_sig(np.where(k, lp, lg) + ab) - loss, 0.02, 0.98)
        ok = rng.random(n) < p
        learn = mask & ~k & (rng.random(n) < LEARN)
        held = held | learn
        return ok

    nA = rng.integers(1, 4, n)
    rev = rng.random(n) < REVIEW
    t = np.zeros(n)
    oks = []                       # outcome of each initial A attempt (valid where j < nA)
    for j in range(3):
        mask = j < nA
        if j > 0:
            t = np.where(mask, t + _ticks(rng, mask.astype(int)), t)
        oks.append(attempt(mask, t, lossA if j == 0 else 0.0))
    t_last_init = t.copy()
    t = t + between_ticks()
    t_r = t + _ticks(rng, np.ones(n, int))
    r_ok = attempt(rev, t_r)
    t = np.where(rev, t_r, t)
    tb = t + _ticks(rng, np.ones(n, int))
    # B's first attempt: state of A read at tb (forgetting since A's last touch), then the gate
    if forget:
        lose = held & (rng.random(n) > np.exp(-(tb - last) / TAU))
        held = held & ~lose
    lag = tb  # first A attempt at time 0
    loss = np.where(held, 0.0, gate(lag))
    y = rng.random(n) < np.clip(_sig(lg + ab) - loss, 0.02, 0.98)
    # v1 cases(): n_before = nA + rev; last A attempt = review if rev else the nA-th initial attempt
    nb = nA + rev
    t_lastA = np.where(rev, t_r, t_last_init)
    recent = (tb - t_lastA) <= W / DAY   # v1 W is in seconds; this clock is in days
    ok_init = np.stack(oks, axis=1)                           # (n, 3)
    idx_last = nA - 1
    R_init = ok_init[np.arange(n), idx_last]
    R = np.where(rev, r_ok, R_init)
    upto = np.where(rev, nA, nA - 1)                          # attempts before the last
    mp = (ok_init & (np.arange(3)[None, :] < upto[:, None])).any(axis=1)
    lagd = lag  # already in days
    cell = np.full(n, -1)
    wald = recent & (nb >= 2)
    early, late = lagd < 1.0, lagd >= 7.0
    cell[wald & early & mp] = 0
    cell[wald & early & ~mp] = 1
    cell[wald & late & mp] = 2
    cell[wald & late & ~mp] = 3
    return cell, R.astype(np.int8), y.astype(np.int8)


def synth_stats(world, counts, rng, chunk=400_000):
    """Per pair v1-style stats {'EARLY': {'wald': w}, 'LATE': {'wald': w}}, cells sized by counts (P x 4)."""
    counts = np.asarray(counts, dtype=int)
    need = counts.sum(axis=0)
    pools = [[[], []] for _ in range(4)]
    have = np.zeros(4, int)
    while (have < need).any():
        cell, R, y = simulate(world, chunk, rng)
        for k in range(4):
            if have[k] < need[k]:
                s = cell == k
                take = min(int(s.sum()), int(need[k] - have[k]))
                pools[k][0].append(R[s][:take])
                pools[k][1].append(y[s][:take])
                have[k] += take
    R = [np.concatenate(p[0]) if p[0] else np.zeros(0, np.int8) for p in pools]
    Y = [np.concatenate(p[1]) if p[1] else np.zeros(0, np.int8) for p in pools]
    off = np.vstack([np.zeros((1, 4), int), np.cumsum(counts, axis=0)])
    stats = []
    for i in range(len(counts)):
        s = {}
        for bname, km, kf in (("EARLY", 0, 1), ("LATE", 2, 3)):
            ym, yf = Y[km][off[i, km]:off[i + 1, km]], Y[kf][off[i, kf]:off[i + 1, kf]]
            w = v1._drop(ym.tolist(), yf.tolist())
            if w is not None:
                rm, rf = R[km][off[i, km]:off[i + 1, km]], R[kf][off[i, kf]:off[i + 1, kf]]
                w = w + (float(rm.mean()), float(rf.mean()))
            s[bname] = {"wald": w}
        stats.append(s)
    return stats


# ------------------------------------------------------------------ calibration against v1's agent floor

def run_calibrate():
    KEYS = ("drop_EARLY", "drop_LATE", "gap_EARLY", "gap_LATE")
    out, faithful = {}, True
    for wi, world in enumerate(WORLDS):
        agent, counts_all = [], []
        for s in range(3):
            rows, pairs = v1.synth(world, seed=200 + s)
            tl, idx = build(rows)
            st = [pair_stats(cases(a, b, tl, idx)) for a, b in pairs]
            p = primary_wald(st, [b for _, b in pairs], s)
            agent.append({k: p.get(k) for k in KEYS})
            counts_all.append(([[x["EARLY"]["n"]["wald_m"], x["EARLY"]["n"]["wald_f"],
                                 x["LATE"]["n"]["wald_m"], x["LATE"]["n"]["wald_f"]] for x in st],
                               [b for _, b in pairs]))
        sim = []
        for s in range(10):
            counts, bs = counts_all[s % 3]
            keep = [i for i, c in enumerate(counts) if min(c) > 0]
            rng = np.random.default_rng([9, wi, s])
            st = synth_stats(world, [counts[i] for i in keep], rng)
            p = primary_wald(st, [bs[i] for i in keep], s)
            sim.append({k: p.get(k) for k in KEYS} | dict(verdict=p["verdict"]))
        am = {k: float(np.mean([a[k] for a in agent])) for k in KEYS}
        sm = {k: float(np.mean([x[k] for x in sim if x[k] is not None])) for k in KEYS}
        diff = {k: sm[k] - am[k] for k in KEYS}
        ok = all(abs(v) <= 0.02 for v in diff.values())
        faithful &= ok
        out[world] = dict(agent_mean=am, case_sim_mean=sm, diff=diff, within_0_02=ok,
                          agent_seeds=agent, case_sim_seeds=sim)
        print(f"  {world:6s} agent " + " ".join(f"{k} {am[k]:+.3f}" for k in KEYS) + "\n         sim   "
              + " ".join(f"{k} {sm[k]:+.3f}" for k in KEYS) + f"   {'FAITHFUL' if ok else 'DEPARTS'}", flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "calibration.json").write_text(json.dumps(dict(faithful=faithful, tolerance=0.02, worlds=out),
                                                     indent=1) + "\n")
    print(f"  CALIBRATION {'FAITHFUL' if faithful else 'DEPARTS'}")
    return faithful


# ------------------------------------------------------------------ matched floor

def clopper_pearson(k, n, a=0.05):
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(a / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a / 2, k + 1, n - k))
    return [lo, hi]


def run_floor(names, only_worlds=None):
    sizing = json.loads((OUT / "sizing.json").read_text())["corpora"]
    path = OUT / "floor.json"
    res = json.loads(path.read_text())["corpora"] if path.exists() else {}
    for ci_, name in enumerate(names):
        sz = sizing[name]
        if not sz["answerable_on_positivity"]:
            res[name] = dict(passes=False, reason="fewer than 30 count-readable pairs")
            continue
        cells = np.array(sz["cells"], dtype=int)
        bs, counts = cells[:, 0].tolist(), cells[:, 1:]
        per = {}
        t0 = time.time()
        parts = OUT / "floor_parts"
        parts.mkdir(parents=True, exist_ok=True)
        for wi, world in enumerate(WORLDS):
            part = parts / f"{name}_{world}.json"
            if part.exists():
                per[world] = json.loads(part.read_text())
                continue
            if only_worlds is not None and world not in only_worlds:
                continue
            runs = []
            for s in range(SEEDS):
                rng = np.random.default_rng([CORPORA.index(name), wi, s])
                st = synth_stats(world, counts, rng)
                p = primary_wald(st, bs, s)
                runs.append({k: p.get(k) for k in ("verdict", "held_pairs", "drop_EARLY", "drop_LATE",
                                                    "gap_EARLY", "gap_LATE", "D_sub", "D_sub_ci", "D_held",
                                                    "D_held_ci", "share_explained", "share_explained_ci",
                                                    "delta_ci")})
            vs = [r["verdict"] for r in runs]
            tally = {v: vs.count(v) for v in sorted(set(vs))}
            per[world] = dict(tally=tally, runs=runs)
            part.write_text(json.dumps(per[world], indent=1) + "\n")
            print(f"  {name:7s} {world:6s} {tally}  ({time.time() - t0:.0f} s)", flush=True)
        if any(w not in per for w in WORLDS):
            print(f"  {name:7s} worlds written: {sorted(per)}; run again without --worlds to assemble", flush=True)
            continue
        n = SEEDS
        f, e, nl = per["FORGET"]["tally"], per["EDGE"]["tally"], per["NULL"]["tally"]
        rates = dict(
            forget_detect=f.get("MOSTLY-FORGETTING", 0), edge_detect=e.get("EDGE-WEAKENS", 0),
            forget_wrong=f.get("EDGE-WEAKENS", 0), edge_wrong=e.get("MOSTLY-FORGETTING", 0),
            null_false=nl.get("MOSTLY-FORGETTING", 0) + nl.get("EDGE-WEAKENS", 0))
        checks = dict(forget_detect=rates["forget_detect"] / n >= PASS["detect"],
                      edge_detect=rates["edge_detect"] / n >= PASS["detect"],
                      forget_wrong=rates["forget_wrong"] / n <= PASS["wrong"],
                      edge_wrong=rates["edge_wrong"] / n <= PASS["wrong"],
                      null_false=rates["null_false"] / n <= PASS["null_false"])
        res[name] = dict(seeds=n, pairs=len(bs), counts_of=rates,
                         rates={k: v / n for k, v in rates.items()},
                         clopper_pearson_95={k: clopper_pearson(v, n) for k, v in rates.items()},
                         checks=checks, passes=all(checks.values()), worlds=per)
        print(f"  {name:7s} FLOOR {'PASSES' if res[name]['passes'] else 'FAILS'}  {rates}", flush=True)
        OUT.mkdir(exist_ok=True)
        path.write_text(json.dumps(dict(seeds=SEEDS, worlds=WORLDS, pass_rule=PASS, corpora=res), indent=1) + "\n")


# ------------------------------------------------------------------ real

def arm_changes(stats, bs, seed=0):
    """Secondary descriptive: each arm's change EARLY -> LATE in B (pM, pF) and current A (rM, rF) accuracy,
    on primary_wald's held pairs and from its bootstrap draws (same rows, same groups, same seed)."""
    rows = [(b, s) for b, s in zip(bs, stats) if s["EARLY"]["wald"] is not None and s["LATE"]["wald"] is not None]
    if len(rows) < MIN_BOTH:
        return None
    arr = {k: np.array([s[k]["wald"] for _, s in rows]) for k in ("EARLY", "LATE")}
    wts = boot_weights([b for b, _ in rows], np.random.default_rng(seed))
    out = {}
    for i, lab in enumerate(("pM", "pF", "rM", "rF")):
        d = arr["LATE"][:, i] - arr["EARLY"][:, i]
        out[lab] = dict(EARLY=float(arr["EARLY"][:, i].mean()), LATE=float(arr["LATE"][:, i].mean()),
                        change=float(d.mean()), change_ci=ci(wmean(wts, d)))
    return out


def run_real(names):
    floor = json.loads((OUT / "floor.json").read_text())["corpora"]
    old = json.loads((V1 / "out/lag_forgetting.json").read_text())["corpora"]
    path = OUT / "lag_forgetting_v2.json"
    res = json.loads(path.read_text())["corpora"] if path.exists() else {}
    for name in names:
        t0 = time.time()
        tl, idx = load(name)
        items, pairs = corpus_pairs(name, idx)
        stats = [pair_stats(cases(a, b, tl, idx)) for a, b in pairs]
        bs = [b for _, b in pairs]
        del tl, idx
        p = primary_wald(stats, bs, 0)
        arms = arm_changes(stats, bs, 0)
        o = old[name]["primary"]
        diffs = {}
        for k, v in p.items():
            if isinstance(v, float):
                diffs[k] = abs(v - o[k])
            elif isinstance(v, list) and v and isinstance(v[0], float):
                diffs[k] = max(abs(a - b) for a, b in zip(v, o[k]))
        repro = dict(max_abs_diff=max(diffs.values()) if diffs else None,
                     verdict_v1_as_computed=o.get("verdict_as_computed"), keys_compared=len(diffs))
        passes = bool(floor.get(name, {}).get("passes"))
        p["verdict_as_computed"] = p["verdict"]
        if not passes:
            p["verdict"] = "UNANSWERABLE"
        res[name] = dict(learners=old[name]["learners"], items=len(items), pairs=len(pairs),
                         floor_passes=passes, primary=p, arm_changes=arms, reproduces_v1=repro)
        print(f"  {name:7s} held {p['held_pairs']}  floor {'PASS' if passes else 'FAIL'}  verdict {p['verdict']} "
              f"(as computed {p['verdict_as_computed']})  repro max|diff| {repro['max_abs_diff']}  "
              f"({time.time() - t0:.0f} s)", flush=True)
        write_real(res, path)
    write_real(res, path, final=True)


def write_real(res, path, final=False):
    allc = dict(res)
    allc.setdefault("xes3g5m", dict(primary=dict(verdict="UNANSWERABLE", held_pairs=17,
                                                 reason="positivity: v1 found 17 held pairs (< 30); not re-read")))
    vs = [v["primary"]["verdict"] for v in allc.values()]
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
                                                         for k, v in allc.items()) + ")")
    path.write_text(json.dumps(dict(boot=v1.BOOT, bootstrap_seed=0, verdict=overall, corpora=allc),
                               indent=1, default=str) + "\n")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    names = (sys.argv[sys.argv.index("--corpora") + 1].split(",") if "--corpora" in sys.argv else CORPORA)
    if mode == "sizing":
        run_sizing(names)
    elif mode == "calibrate":
        sys.exit(0 if run_calibrate() else 1)
    elif mode == "floor":
        run_floor(names, sys.argv[sys.argv.index("--worlds") + 1].split(",") if "--worlds" in sys.argv else None)
    elif mode == "real":
        run_real(names)
