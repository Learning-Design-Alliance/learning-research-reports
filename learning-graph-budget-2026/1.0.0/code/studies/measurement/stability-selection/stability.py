"""Stability selection for data-derived prerequisite edges, and the edge estimator's error curve
against learner count. (Paper II, F3; literature review rank 4; strand 3 analyses 1 and 2.)

PRE-REGISTERED 2026-10-07, committed before any number is computed on real data. Written by an agent
(Claude Opus 5.5) overnight while the maintainer is asleep; every design decision is recorded here.

QUESTION. Paper II's F3 says split-half reliability does not certify edges: in the calibrated
simulation of `studies/measurement/reliability/kappa_bar.py` an estimated graph from 32,000 learners
reaches Spearman-Brown +0.899 and decision kappa +0.646 while its precision against the planted graph
is 0.075 (2,507 edges asserted, 194 true; `out/kappa_bar_floor.json`). The literature's answer to "how
repeatable is the edge?" is stability selection (Meinshausen & Buhlmann 2010, entry 3.10; complementary
pairs, Shah & Samworth 2013): per-edge selection probabilities over subsamples, and a finite-sample bound
on the expected number of false selections,

    E[V] <= q^2 / ((2 tau - 1) p),     tau in (1/2, 1],

where q is the number of edges the base procedure selects per subsample, p the number of candidate
edges, and V the number of non-edges whose selection probability is at least tau. The bound assumes the
noise edges' selection indicators are EXCHANGEABLE and the base procedure is no worse than random
guessing. Entry 3.10 predicts that curriculum order makes noise edges systematically non-exchangeable,
so the bound would understate false edges here. This study tests that prediction against a known truth,
reports the same quantities on real data, and replaces the single 93% false-edge figure with a curve of
sensitivity, specificity and precision against learner count (entries 3.8 Isvoranu & Epskamp 2023,
3.11 Scutari & Nagarajan 2013).

THE EDGE ESTIMATOR is the reliability study's, unchanged: `pairgrid.drops` (positivity.py's
definitions; drop(A, B) = success at B's first touch among learners who passed A before it, minus among
those who touched A and had not passed it), cell floor MIN_CELL = 10 (kappa_bar's and
lag_band_reliability's primary floor).
  - For stability selection the base procedure is "the q readable pairs with the largest drop" in each
    half-sample (split_half.py ranks by the drop; MB's bound needs a fixed q).
  - For the error curve the estimator is kappa_bar's ADOPTED RULE (assert when drop - 1.0 se > 0.10 at
    cell floor 10), the rule whose precision is the 0.075, on the full sample of N learners.

STABILITY SELECTION (fixed before the run).
  subsamples  complementary pairs (Shah & Samworth 2013): B = 50 random splits of the LEARNERS into
              halves, both halves used: 100 half-samples. The learner is the unit resampled because the
              learner is the unit the estimator's cells are built from.
  candidates  p = ordered pairs (A != B) readable at the cell floor on the full sample.
  q           q = round(sqrt(EV0 * (2 tau0 - 1) * p)) with EV0 = 1 and tau0 = 0.75, i.e. q is set so the
              MB bound at the primary threshold is E[V] <= 1 (MB's own worked choice of scale). In the
              simulation p is about 3,500, so q is about 42.
  threshold   tau = 0.75 primary; 0.60 and 0.90 reported with their own bounds.
  output      per-edge selection probabilities pi (aggregates only: a histogram, the counts at each tau,
              and, in simulation, pi for true and false edges separately); the MB bound; the number of
              selected edges; the share of selected edges whose reverse is also selected (a prerequisite
              is one-way, an ability or session artefact is two-way).

THE SIMULATION reuses kappa_bar.py's generator (`kappa_bar.World`, theta sd 0.8 and mu 2.0 as tuned to
XES3G5M in `kappa_bar_tune.json`; 60 items in a hidden order, gates a -> b for a < b with probability
DENSITY and size U(0.05, 0.35), prior holding logistic(theta - beta), each learner a random 60% of items,
1-3 attempts each). It is reproduced first: world (0.10, seed 1) at 32,000 learners must assert exactly
kappa_bar's 2,507 edges at precision 0.0750, or nothing here is read. Four worlds, differing in two
switches only (`OrderedWorld`, a subclass that changes nothing else):

  I0  CALIBRATED            kappa_bar's world exactly: random attempt order, no session state. Noise
                            edges are ability-driven (learners who pass A are abler) and owe nothing to
                            any order. This is Paper II's world.
  I   INDEPENDENT           I0 plus a SESSION STATE: a per-learner AR(1) latent on the logit over the
                            learner's attempt sequence (sd 0.6, autocorrelation 0.9 per attempt), the
                            kind of short-run state (engagement, fatigue, a lesson just taught) that
                            makes items done close together succeed or fail together. Attempt order is
                            random per learner, so which pairs sit close together differs by learner:
                            the noise it adds is independent of any curriculum order.
  C   CURRICULUM-ORDERED    I plus a CATALOGUE ORDER: every learner attempts their items in the
                            catalogue order (the hidden order, which a curriculum follows) with jitter
                            N(0, 3 positions). The session state now lands on the SAME pairs for every
                            learner -- catalogue neighbours, forward in the catalogue -- so its noise
                            edges follow curriculum order. This is the catalogue mechanism.
  C0  ORDER ONLY            I0 plus the catalogue order, no session state (reported, to separate the
                            order from the session state).

  The session-state and jitter values are not tuned to anything; they are chosen to be modest (a 0.6
  logit sd is smaller than theta's 0.8) and are recorded here before any run. I, C and C0 are not
  re-tuned to XES3G5M; their first-attempt accuracy and median drop are reported beside the target.

  replicates  R = 20 worlds per world type at density 0.10, R = 10 at 0.05, seeds 1..R (the world's
              graph, betas and learners all change with the seed). The deranged arm (below) is also
              run in simulation, at N = 32,000 and density 0.10 on seeds 1..5 only, for compute: it
              shows whether the real-data check can see each mechanism. Intervals are 2.5th-97.5th percentiles over
              replicate worlds for per-world quantities, and a percentile bootstrap (2,000 draws over
              replicate worlds) for means. The replicate world is the unit resampled.
  densities   0.10 primary (kappa_bar's floor world); 0.05 reported.
  N           500, 1,000, 2,000, 4,000, 8,000, 16,000, 32,000 training learners, nested prefixes of one
              32,000-learner draw per world (kappa_bar's construction).

ESTIMANDS AND VERDICTS (signed; written before the run).

  (2) Honesty of the MB bound, primary at N = 32,000, density 0.10, tau = 0.75. Realised false
      selections V = edges with pi >= tau that are not planted gates in that direction (a selected
      reversal b -> a of a true a -> b is false; reversals are counted separately as well). Per world
      type, over R replicates:
        HONEST     mean V <= mean bound
        VIOLATED   mean V >  mean bound
      with "(decisive)" appended when the bootstrap interval of mean V lies wholly on that side of the
      bound, and "(marginal)" otherwise. Direction is part of the verdict: V - bound is reported signed.
      Paper II's claim that repeatability does not certify edges:
        SUPPORTED: THE BOUND HOLDS WITH ORDER-INDEPENDENT NOISE AND FAILS WHEN NOISE FOLLOWS CURRICULUM ORDER
                   I HONEST and C VIOLATED.
        BOUND FAILS WITHOUT CURRICULUM ORDER
                   I VIOLATED. Repeatability-based error control fails even where noise owes nothing to
                   the curriculum; the catalogue mechanism is then not needed to break it (C reported).
        NOT SUPPORTED: THE BOUND HOLDS UNDER CURRICULUM ORDER
                   I HONEST and C HONEST.
      The same per-world verdict is reported for I0 (the paper's own world) and C0, and at every N and
      at density 0.05 as secondary readings.

  (3) The error curve. For the adopted rule and for the stability-selected set (tau = 0.75), at each N:
      sensitivity = true edges asserted / true edges; specificity = non-edges not asserted / non-edges
      (over all K(K-1) ordered pairs; an unreadable pair is not asserted); precision = true asserted /
      asserted (undefined when nothing is asserted; the number of replicates where it is defined is
      reported). Mean and 2.5-97.5 percentiles over R replicates. Signed reading pre-registered:
        PRECISION RISES WITH LEARNERS   mean precision at 32,000 above that at 500 and the replicate
                                        intervals do not overlap
        PRECISION FALLS WITH LEARNERS   the reverse
        PRECISION FLAT                  otherwise
      and the same for sensitivity and specificity. The density 0.02 and 0.05 curves are reported for the
      adopted rule (cheap), the stability-selected curve at 0.10 and 0.05.

  (1) Real data: XES3G5M (the 200 KCs the most learners reached, all learners; as kappa_bar and
      lag_band_reliability read it) and EdNet KT1 (the atlas reader's 6,000-learner zip prefix, every
      item; as lag_band_reliability reads it). Per corpus: p, q, the MB bound at each tau, the number of
      edges with pi >= tau, the pi histogram, the reverse-selected share. There is no truth, so the
      bound's honesty is checked against a DERANGED NULL of the same size: the same B = 50 complementary
      splits, the same q, the same candidates, but within each half every learner's A-side history is
      taken from another learner of the same half under a derangement (`pairgrid.derangement`, no fixed
      points; kappa_bar's and lag_band_reliability's arm). The derangement destroys every learner-level
      dependency (prerequisite and ability alike) and keeps each item's own timing and difficulty, so
      every deranged selection is a false one. Per corpus:
        BOUND HONEST UNDER THE DERANGED NULL     deranged selections at tau 0.75 <= the bound
        BOUND VIOLATED UNDER THE DERANGED NULL   deranged selections >  the bound
      A real-data selection count far above the deranged count says the selected edges are not
      exposure; it does not say they are prerequisites (the ability artefact survives in the real arm and
      not in the deranged one -- kappa_bar's lesson). Monte Carlo variability: the whole real arm is run
      twice with different split seeds and both counts are reported.
      Positivity: if fewer than 100 pairs are readable at the cell floor, the corpus is UNANSWERABLE.

FLOORS (synthetic; run first; if either fails the corresponding verdict is UNANSWERABLE).
  F1 RECOVERY. A sparse planted graph with independent noise: theta sd 0 (no ability confound), random
     order, no session state, density 0.05, N = 32,000, R = 10. Passes if, at tau = 0.75, mean precision
     of the selected set >= 0.90, mean recall >= 0.25 (q is about 42 against about 88 true edges, so
     recall cannot exceed about 0.5), and mean V <= the bound (the bound is honest where its assumption
     holds). If F1 fails, the instrument cannot recover a planted sparse graph and nothing below is read.
  F2 VIOLATION IS VISIBLE. The F1 world plus 20 DECOY non-edge pairs carrying a shared learner factor
     on both items' logits (local dependence without a gate: both directions are false edges). Run at
     decoy sd 1, 2 and 3 (a pre-registered ladder, not a tuning loop), R = 10 each. Passes if, at some
     sd <= 3, mean V exceeds the bound with its bootstrap interval wholly above it; the smallest such sd
     is reported. If F2 fails, a VIOLATED verdict could not have been seen and (2) is UNANSWERABLE.
  ALSO: the real grids are checked cell-for-cell against positivity.classify on 300 pairs
  (`pairgrid.check_against_classify`) before any real number is read.

WHAT IT CAN AND CANNOT SAY. In simulation it can say whether MB's bound counts the false edges that this
estimator selects, in worlds whose false-edge mechanisms are known. On real data it can give selection
probabilities and the bound, and test the bound against a no-dependency null; it cannot say which real
selected edges are prerequisites, because no corpus has a truth. The session state and catalogue order
are one mechanism by which noise can follow curriculum order, chosen by the agent, not the only one. The
MB bound is the conservative one; Shah & Samworth's tighter bounds under unimodality would be violated
sooner, so a HONEST verdict here is the generous reading.

DATA. Reads two corpora: XES3G5M (licence unstated; research use, non-redistributable) through
shared.paths `XES_DIR`, and EdNet KT1 (CC BY-NC 4.0; counting cells is neither commercial use nor model
training) through shared.paths `EDNET_ZIP` via shared/corpus.EdNet. Only aggregates are written to out/;
no learner-level rows, no item text, no derived files.

SEEN BEFORE THIS DESIGN WAS COMMITTED (stated so the reader can judge): one synthetic smoke run of
world C, density 0.10, seed 1, at N = 2,000 and 32,000, to time the code. At 32,000 it selected 15 edges
at tau 0.75, all true, against a bound of 0.98; deranged arm 0 selected; adopted-rule precision 0.10;
first-attempt accuracy 0.66, median drop 0.17. No parameter was changed after it. Nothing on real data
has been computed.

RESULTS (2026-10-07; design committed at 50bef7e; no design change after it).
  Reproduction PASSES (2,507 edges, precision 0.0750). F1 PASSES (precision 0.971, recall 0.273, V 0.7
  vs bound 0.997). F2 PASSES at decoy sd 1 (V 4.8 [3.1, 6.3] vs 0.997).
  (2) N 32,000, density 0.10, tau 0.75, mean V over 20 worlds vs bound: I0 1.20 [0.70, 1.75] vs 0.997
  VIOLATED (marginal); I 0.90 vs 0.997 HONEST (marginal); C 0.95 vs 0.986 HONEST (marginal); C0 0.70 vs
  0.986 HONEST (marginal). VERDICT: NOT SUPPORTED: THE BOUND HOLDS UNDER CURRICULUM ORDER. Secondary: at
  tau 0.60 C violates decisively (3.45 [2.85, 4.05] vs 2.46) while I does not (1.60 vs 2.49); the ten
  most stable false edges reach pi 0.548 in C against 0.339 in I. The deranged arm selects 0 in every
  world, so it cannot see the ability or session mechanisms.
  (3) Adopted rule, I0, density 0.10: precision 0.085 at 500 -> 0.074 at 32,000 (FLAT), sensitivity
  0.372 -> 0.949 (RISES), specificity 0.784 -> 0.365 (FALLS). Stability-selected set: precision >= 0.94
  from N 8,000, sensitivity 0.150 at 32,000.
  (1) XES3G5M: 10 / 9 edges at tau 0.75 (bound 0.997), deranged 0 -> BOUND HONEST UNDER THE DERANGED
  NULL. EdNet: 0 / 0 (bound 1.000), deranged 0 -> same verdict, but its deranged cells are 0.43x the
  real ones (control too small). See README.md.

IMPLEMENTATION. `cells()` is pairgrid.column_cells's arithmetic for the ALL band without the lag
computation, because the stability selection needs 100 half-samples per world; `check_cells` asserts the
two agree exactly (with and without a donor) on every world type and on both real grids before use.

COMPUTE. OMP/OPENBLAS/MKL threads 1 (must be set before numpy is imported: multi-threaded BLAS on the
shared machine ran a hundred times slower). Peak memory well under 3 GB (the XES3G5M grid is 18k x 865 before
the top-200 subset).

    python3 stability.py floor     # reproduction check, F1, F2
    python3 stability.py sim       # bound honesty in I0, I, C, C0 and the error curves
    python3 stability.py real      # XES3G5M and EdNet, with the deranged null
"""

from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = ROOT / "studies/measurement/reliability"
sys.path.insert(0, str(REL))
sys.path.insert(0, str(ROOT / "studies/identifiability/overlap"))
sys.path.insert(0, str(ROOT))
import kappa_bar as kb  # noqa: E402
import pairgrid as pg  # noqa: E402

OUT = HERE / "out"
SEED = 20261007
MIN_CELL = kb.MIN_CELL  # 10
B_PAIRS = 50
EV0, TAU0 = 1.0, 0.75
TAUS = (0.60, 0.75, 0.90)
NS = (500, 1000, 2000, 4000, 8000, 16000, 32000)
R = 20
R_FLOOR = 10
SESSION_SD, RHO = 0.6, 0.9
JITTER = 3.0
N_DECOYS = 20
DECOY_LADDER = (1.0, 2.0, 3.0)
BOOT = 2000


# ---------------------------------------------------------------- worlds

class OrderedWorld(kb.World):
    """kappa_bar.World with two switches: catalogue order and a session state (and, for floor F2,
    decoy pairs). Everything else -- gates, betas, prior holding, subset, attempts -- is kappa_bar's."""

    def __init__(self, density, seed, theta_sd, mu, order="random", session_sd=0.0, decoy_sd=0.0,
                 n_decoys=0):
        super().__init__(density, seed, theta_sd, mu)
        self.order, self.session_sd, self.decoy_sd = order, session_sd, decoy_sd
        self.decoys = []
        if n_decoys:
            cand = [(a, b) for a in range(self.K) for b in range(a + 1, self.K) if self.G[a, b] == 0]
            pick = self.rng.choice(len(cand), n_decoys, replace=False)
            self.decoys = [cand[i] for i in pick]

    def learners(self, n):
        rng, K = self.rng, self.K
        theta = rng.normal(0, self.theta_sd, n)
        prior = rng.random((n, K)) < kb.sigmoid(theta[:, None] - self.beta[None, :])
        held = prior.copy()
        m = int(round(kb.SUBSET * K))
        sub = np.argsort(rng.random((n, K)), axis=1)[:, :m]
        if self.order == "catalogue":
            key = sub + rng.normal(0, JITTER, (n, m))
            order = np.take_along_axis(sub, np.argsort(key, axis=1), axis=1)
        else:
            order = sub
        reps = rng.integers(1, 4, (n, m))
        D = np.zeros((n, K))
        for a, b in self.decoys:
            z = rng.normal(0, self.decoy_sd, n)
            D[:, a] += z
            D[:, b] += z
        s = rng.normal(0, self.session_sd, n) if self.session_sd else np.zeros(n)
        innov = np.sqrt(1 - RHO ** 2) * self.session_sd
        FT = np.full((n, K), np.inf)
        FP = np.full((n, K), np.inf)
        Y = np.zeros((n, K), np.float32)
        t = np.zeros(n)
        GT = self.G.T
        ar = np.arange(n)
        for j in range(m):
            b = order[:, j]
            for r in range(3):
                act = reps[:, j] > r
                if not act.any():
                    continue
                L = ar[act]
                bb = b[act]
                pen = (GT[bb] * (~held[L])).sum(1)
                logit = self.mu + theta[L] - self.beta[bb] + s[L] + D[L, bb]
                p = np.clip(kb.sigmoid(logit) - pen, 0.02, 0.98)
                y = rng.random(len(L)) < p
                tt = t[L]
                first = ~np.isfinite(FT[L, bb])
                FT[L[first], bb[first]] = tt[first]
                Y[L[first], bb[first]] = y[first]
                newpass = y & ~np.isfinite(FP[L, bb])
                FP[L[newpass], bb[newpass]] = tt[newpass]
                held[L[y], bb[y]] = True
                t[L] += 1
                if self.session_sd:
                    s[L] = RHO * s[L] + innov * rng.normal(0, 1, len(L))
        return FT, FP, Y


WORLDS = {
    "I0": dict(order="random", session_sd=0.0),
    "I": dict(order="random", session_sd=SESSION_SD),
    "C": dict(order="catalogue", session_sd=SESSION_SD),
    "C0": dict(order="catalogue", session_sd=0.0),
}


def make_world(kind, density, seed, theta_sd=None, mu=None, **extra):
    sd, mu0 = kb.tuned()
    sd = sd if theta_sd is None else theta_sd
    mu = mu0 if mu is None else mu
    if kind == "I0" and not extra:
        w = kb.World(density, seed, sd, mu)
        orig = w.learners
        w.learners = lambda n: orig(n)[:3]
        return w
    cfg = dict(WORLDS.get(kind, {}))
    cfg.update(extra)
    return OrderedWorld(density, seed, sd, mu, **cfg)


# ---------------------------------------------------------------- cells

def cells(FT, FP, Y, groups, donor=None, start=None):
    """ALL-lag cells for every ordered pair and group, shape (G, K_A, K_B): pairgrid.column_cells's
    arithmetic (ALL band only), without the lag computation, in float32. `check_cells` asserts the
    two agree exactly before anything built on this is read."""
    n, K = FT.shape
    Gn = groups.shape[1]
    out = {k: np.zeros((Gn, K, K), np.float32) for k in ("nm", "sm", "nf", "sf")}
    for b in range(K):
        L = np.nonzero(np.isfinite(FT[:, b]))[0]
        if len(L) == 0:
            continue
        tb = FT[L, b][:, None]
        if donor is None:
            TA, PA = FT[L], FP[L]
        else:
            d = donor[L]
            shift = (start[L] - start[d])[:, None] if start is not None else 0.0
            TA, PA = FT[d] + shift, FP[d] + shift
        m = PA < tb
        f = (TA < tb) & ~m
        m[:, b] = False
        f[:, b] = False
        S = groups[L].T
        Sy = S * Y[L, b].astype(np.float32)[None, :]
        mf, ff = m.astype(np.float32), f.astype(np.float32)
        out["nm"][:, :, b] = S @ mf
        out["sm"][:, :, b] = Sy @ mf
        out["nf"][:, :, b] = S @ ff
        out["sf"][:, :, b] = Sy @ ff
    return out


def check_cells(FT, FP, Y, rng, start=None, n_groups=3):
    """Assert cells() equals pairgrid.column_cells, with and without a donor."""
    n, K = FT.shape
    G = (rng.random((n, n_groups)) < 0.5).astype(np.float32)
    donor = pg.derangement(n, rng)
    st = start if start is not None else np.zeros(n)
    for dn in (None, donor):
        mine = cells(FT, FP, Y, G, donor=dn, start=st)
        for b in rng.choice(K, min(K, 12), replace=False):
            ref = pg.column_cells(FT, FP, Y, b, G, bands=("ALL",), lag_scale=1.0, donor=dn, start=st)["ALL"]
            for k in ("nm", "sm", "nf", "sf"):
                assert np.array_equal(mine[k][:, :, b], ref[k].astype(np.float32)), (k, b, dn is not None)
    return True


# ---------------------------------------------------------------- stability selection

def q_for(p):
    return max(1, int(round(np.sqrt(EV0 * (2 * TAU0 - 1) * p))))


def mb_bound(q, p, tau):
    return q ** 2 / ((2 * tau - 1) * p)


def candidates(FT, FP, Y):
    c = cells(FT, FP, Y, np.ones((FT.shape[0], 1), np.float32))
    _, _, ok = pg.drops({k: v[0] for k, v in c.items()}, MIN_CELL)
    ok = ok.copy()
    np.fill_diagonal(ok, False)
    return ok


def _top_q(c, g, cand, q):
    d, _, ok = pg.drops({k: v[g] for k, v in c.items()}, MIN_CELL)
    d = np.where(ok & cand, d, np.nan)
    flat = d.ravel()
    good = np.nonzero(np.isfinite(flat))[0]
    sel = np.zeros(flat.shape, bool)
    if len(good):
        k = min(q, len(good))
        top = good[np.argpartition(-flat[good], k - 1)[:k]]
        sel[top] = True
    return sel.reshape(d.shape)


def cpss(FT, FP, Y, rng, cand, q, deranged=False, start=None, B=B_PAIRS):
    """Complementary-pairs stability selection: selection probability of every ordered pair."""
    n, K = FT.shape
    counts = np.zeros((K, K))
    nsel = []
    if not deranged:
        G = np.zeros((n, 2 * B), np.float32)
        for s in range(B):
            perm = rng.permutation(n)
            G[perm[: n // 2], 2 * s] = 1
            G[perm[n // 2:], 2 * s + 1] = 1
        c = cells(FT, FP, Y, G)
        for g in range(2 * B):
            sel = _top_q(c, g, cand, q)
            counts += sel
            nsel.append(int(sel.sum()))
        cell_sizes = np.minimum(c["nm"], c["nf"])[:, cand]
    else:
        sizes = []
        for s in range(B):
            perm = rng.permutation(n)
            h1, h2 = perm[: n // 2], perm[n // 2:]
            donor = pg.derangement(n, rng, blocks=[h1, h2])
            g2 = np.zeros((n, 2), np.float32)
            g2[h1, 0] = 1
            g2[h2, 1] = 1
            c = cells(FT, FP, Y, g2, donor=donor, start=start)
            for g in range(2):
                sel = _top_q(c, g, cand, q)
                counts += sel
                nsel.append(int(sel.sum()))
            sizes.append(np.minimum(c["nm"], c["nf"])[:, cand])
        cell_sizes = np.concatenate(sizes)
    return counts / (2 * B), float(np.mean(nsel)), float(np.median(cell_sizes))


def summarise_pi(pi, cand, q, truth=None):
    p = int(cand.sum())
    out = dict(p=p, q=q, bounds={f"{t:.2f}": mb_bound(q, p, t) for t in TAUS},
               hist=np.histogram(pi[cand], bins=10, range=(0, 1.0000001))[0].tolist())
    for t in TAUS:
        S = (pi >= t) & cand
        key = f"{t:.2f}"
        rev = S & S.T
        row = dict(selected=int(S.sum()), reverse_also_selected=float(rev.sum() / max(S.sum(), 1)))
        if truth is not None:
            tp = int((S & truth).sum())
            row.update(true=tp, false=int(S.sum()) - tp, reversals=int((S & truth.T & ~truth).sum()),
                       precision=tp / S.sum() if S.sum() else None, recall=tp / max(int(truth.sum()), 1))
        out[key] = row
    if truth is not None:
        out["pi_true_mean"] = float(pi[truth & cand].mean()) if (truth & cand).any() else None
        out["pi_false_top"] = float(np.sort(pi[~truth & cand])[-10:].mean())
    return out


# ---------------------------------------------------------------- error curve helpers

def rates(A, truth):
    K = truth.shape[0]
    off = ~np.eye(K, dtype=bool)
    T = truth & off
    tp = int((A & T).sum())
    fp = int((A & ~T & off).sum())
    neg = int((~T & off).sum())
    return dict(asserted=int(A.sum()), sensitivity=tp / max(int(T.sum()), 1), specificity=1 - fp / neg,
                precision=tp / A.sum() if A.sum() else None)


def boot_mean(x, rng, n=BOOT):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) == 0:
        return None
    m = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(n)]
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def pct(x):
    x = np.asarray([v for v in x if v is not None], float)
    if len(x) == 0:
        return None
    return [float(x.mean()), float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5)), int(len(x))]


def run_replicate(kind, density, seed, ns, rng, do_cpss=True, deranged=False, **extra):
    w = make_world(kind, density, seed, **extra)
    FTp, FPp, Yp = w.learners(max(ns))
    check_cells(FTp[:2000], FPp[:2000], Yp[:2000], np.random.default_rng(seed))
    truth = w.G > 0
    pts = []
    for n in ns:
        FT, FP, Y = FTp[:n], FPp[:n], Yp[:n]
        c1 = cells(FT, FP, Y, np.ones((n, 1), np.float32))
        A, d, ok = kb.assert_graph(c1)
        okd = ok.copy()
        np.fill_diagonal(okd, False)
        pt = dict(n=n, adopted=rates(A, truth), readable=float(okd.mean()),
                  accuracy=float(Y[np.isfinite(FT)].mean()), median_drop=float(np.nanmedian(d[okd])))
        if do_cpss:
            cand = okd
            q = q_for(int(cand.sum()))
            pi, qbar, _ = cpss(FT, FP, Y, rng, cand, q)
            ss = summarise_pi(pi, cand, q, truth)
            S = (pi >= TAU0) & cand
            pt.update(cpss=ss, q_mean=qbar, selected_rates=rates(S, truth))
            if deranged and n == max(ns):
                pid, _, _ = cpss(FT, FP, Y, rng, cand, q, deranged=True, start=np.zeros(n))
                pt["deranged"] = summarise_pi(pid, cand, q, truth)
        pts.append(pt)
    return dict(seed=seed, true_edges=int(truth.sum()), points=pts)


def bound_verdict(reps, n, rng, tau=TAU0):
    key = f"{tau:.2f}"
    V, Bd = [], []
    for r in reps:
        pt = next(p for p in r["points"] if p["n"] == n)
        V.append(pt["cpss"][key]["false"])
        Bd.append(pt["cpss"]["bounds"][key])
    mv = boot_mean(V, rng)
    mb = float(np.mean(Bd))
    v = "HONEST" if mv[0] <= mb else "VIOLATED"
    decisive = (mv[2] <= mb) if v == "HONEST" else (mv[1] > mb)
    return dict(verdict=f"{v} ({'decisive' if decisive else 'marginal'})", base=v, mean_V=mv, mean_bound=mb,
                V_minus_bound=mv[0] - mb, share_reps_V_le_bound=float(np.mean(np.array(V) <= np.array(Bd))),
                V_per_rep=V)


# ---------------------------------------------------------------- modes

def reproduce():
    """kappa_bar's floor world (0.10, seed 1) at 32,000 learners must assert 2,507 edges at 0.0750."""
    ref = json.loads((REL / "out/kappa_bar_floor.json").read_text())["points"][-1]
    w = make_world("I0", 0.10, 1)
    FT, FP, Y = w.learners(32000)
    A, _, _ = kb.assert_graph(cells(FT, FP, Y, np.ones((32000, 1), np.float32)))
    tp = int((A & (w.G > 0)).sum())
    got = dict(edges=int(A.sum()), precision=tp / A.sum())
    ok = got["edges"] == ref["edges"] and abs(got["precision"] - ref["precision"]) < 1e-9
    print(f"REPRODUCTION {'PASSES' if ok else 'FAILS'}: {got} vs kappa_bar {ref['edges']}, {ref['precision']:.4f}",
          flush=True)
    return dict(passes=bool(ok), got=got, reference=dict(edges=ref["edges"], precision=ref["precision"]))


def run_floor():
    OUT.mkdir(exist_ok=True)
    rng = np.random.default_rng([SEED, 1])
    rep = reproduce()
    res = dict(reproduction=rep)
    # F1
    t0 = time.time()
    reps = [run_replicate("F", 0.05, s, (32000,), rng, theta_sd=0.0, order="random", session_sd=0.0)
            for s in range(1, R_FLOOR + 1)]
    pts = [r["points"][0] for r in reps]
    prec = [p["cpss"]["0.75"]["precision"] for p in pts]
    rec = [p["cpss"]["0.75"]["recall"] for p in pts]
    bv = bound_verdict(reps, 32000, rng)
    f1 = (np.mean([x for x in prec if x is not None]) >= 0.90 and np.mean(rec) >= 0.25 and bv["base"] == "HONEST")
    res["F1"] = dict(passes=bool(f1), precision=pct(prec), recall=pct(rec), bound=bv,
                     true_edges=pct([r["true_edges"] for r in reps]), q=pts[0]["cpss"]["q"], p=pct([p["cpss"]["p"] for p in pts]),
                     selected=pct([p["cpss"]["0.75"]["selected"] for p in pts]),
                     reverse_also_selected=pct([p["cpss"]["0.75"]["reverse_also_selected"] for p in pts]))
    print(f"F1 {'PASSES' if f1 else 'FAILS'}: precision {pct(prec)}, recall {pct(rec)}, V {bv['mean_V']} vs bound "
          f"{bv['mean_bound']:.3f} ({time.time() - t0:.0f}s)", flush=True)
    # F2 ladder
    res["F2"] = dict(ladder={})
    smallest = None
    for sd in DECOY_LADDER:
        reps = [run_replicate("F", 0.05, s, (32000,), rng, theta_sd=0.0, order="random", session_sd=0.0,
                              decoy_sd=sd, n_decoys=N_DECOYS) for s in range(1, R_FLOOR + 1)]
        bv = bound_verdict(reps, 32000, rng)
        hit = bv["base"] == "VIOLATED" and bv["mean_V"][1] > bv["mean_bound"]
        res["F2"]["ladder"][str(sd)] = dict(detected=bool(hit), bound=bv)
        print(f"F2 decoy sd {sd}: V {bv['mean_V']} vs bound {bv['mean_bound']:.3f} -> "
              f"{'DETECTED' if hit else 'not detected'}", flush=True)
        if hit and smallest is None:
            smallest = sd
    res["F2"].update(passes=smallest is not None, smallest_sd=smallest)
    print(f"F2 {'PASSES' if smallest is not None else 'FAILS'} (smallest sd {smallest})", flush=True)
    res["passes"] = bool(rep["passes"] and f1)
    (OUT / "floor.json").write_text(json.dumps(res, indent=1, default=float) + "\n")


def curve_summary(reps, ns, prefix):
    out = []
    for n in ns:
        pts = [next(p for p in r["points"] if p["n"] == n) for r in reps]
        row = dict(n=n)
        for m in ("sensitivity", "specificity", "precision"):
            row[m] = pct([p[prefix][m] for p in pts])
        row["asserted"] = pct([p[prefix]["asserted"] for p in pts])
        out.append(row)
    lo, hi = out[0], out[-1]
    trend = {}
    for m in ("sensitivity", "specificity", "precision"):
        a, b = lo[m], hi[m]
        if a is None or b is None:
            trend[m] = "UNDEFINED"
        elif b[0] > a[0] and b[1] > a[2]:
            trend[m] = f"{m.upper()} RISES WITH LEARNERS"
        elif b[0] < a[0] and b[2] < a[1]:
            trend[m] = f"{m.upper()} FALLS WITH LEARNERS"
        else:
            trend[m] = f"{m.upper()} FLAT"
    return dict(rows=out, trend=trend)


def run_sim():
    fl = json.loads((OUT / "floor.json").read_text())
    if not fl.get("passes"):
        raise SystemExit("reproduction or F1 failed; nothing is read")
    rng = np.random.default_rng([SEED, 2])
    res = dict(settings=dict(B=B_PAIRS, R=R, ns=NS, taus=TAUS, ev0=EV0, tau0=TAU0, session_sd=SESSION_SD, rho=RHO,
                             jitter=JITTER, min_cell=MIN_CELL), worlds={})
    path = OUT / "sim.json"
    for density in (0.10, 0.05):
        for kind in ("I0", "I", "C", "C0"):
            t0 = time.time()
            nrep = R if density == 0.10 else R // 2
            reps = [run_replicate(kind, density, s, NS, rng, deranged=(density == 0.10 and s <= 5))
                    for s in range(1, nrep + 1)]
            key = f"{kind}/{density}"
            ent = dict(kind=kind, density=density,
                       bound={str(n): bound_verdict(reps, n, rng) for n in NS},
                       bound_tau={f"{t:.2f}": bound_verdict(reps, 32000, rng, t) for t in TAUS},
                       curve_adopted=curve_summary(reps, NS, "adopted"),
                       curve_selected=curve_summary(reps, NS, "selected_rates"),
                       shape={str(n): dict(accuracy=pct([next(p for p in r["points"] if p["n"] == n)["accuracy"] for r in reps]),
                                           median_drop=pct([next(p for p in r["points"] if p["n"] == n)["median_drop"] for r in reps]))
                              for n in (32000,)},
                       at32000=dict(
                           pi_true_mean=pct([r["points"][-1]["cpss"]["pi_true_mean"] for r in reps]),
                           pi_false_top10=pct([r["points"][-1]["cpss"]["pi_false_top"] for r in reps]),
                           reversals=pct([r["points"][-1]["cpss"]["0.75"]["reversals"] for r in reps]),
                           selected=pct([r["points"][-1]["cpss"]["0.75"]["selected"] for r in reps]),
                           reverse_also_selected=pct([r["points"][-1]["cpss"]["0.75"]["reverse_also_selected"] for r in reps]),
                           p=pct([r["points"][-1]["cpss"]["p"] for r in reps]),
                           q=pct([r["points"][-1]["cpss"]["q"] for r in reps])),
                       true_edges=pct([r["true_edges"] for r in reps]))
            if density == 0.10:
                dr = [r["points"][-1]["deranged"] for r in reps if "deranged" in r["points"][-1]]
                ent["deranged_at32000"] = dict(
                    replicates=len(dr),
                    false=pct([d["0.75"]["false"] for d in dr]),
                    selected=pct([d["0.75"]["selected"] for d in dr]),
                    bound=float(np.mean([d["bounds"]["0.75"] for d in dr])),
                    real_arm_V_same_seeds=pct([r["points"][-1]["cpss"]["0.75"]["false"] for r in reps[:len(dr)]]))
            b = ent["bound"]["32000"]
            print(f"{key}: V {b['mean_V']} vs bound {b['mean_bound']:.3f} -> {b['verdict']}; adopted prec @32k "
                  f"{ent['curve_adopted']['rows'][-1]['precision']}; ({time.time() - t0:.0f}s)", flush=True)
            res["worlds"][key] = ent
            path.write_text(json.dumps(res, indent=1, default=float) + "\n")
    # programme verdict, primary density 0.10, N 32,000, tau 0.75
    vI = res["worlds"]["I/0.1"]["bound"]["32000"]["base"]
    vC = res["worlds"]["C/0.1"]["bound"]["32000"]["base"]
    if vI == "VIOLATED":
        verdict = "BOUND FAILS WITHOUT CURRICULUM ORDER"
    elif vC == "VIOLATED":
        verdict = "SUPPORTED: THE BOUND HOLDS WITH ORDER-INDEPENDENT NOISE AND FAILS WHEN NOISE FOLLOWS CURRICULUM ORDER"
    else:
        verdict = "NOT SUPPORTED: THE BOUND HOLDS UNDER CURRICULUM ORDER"
    if not fl["F2"]["passes"] and vC != "VIOLATED" and vI != "VIOLATED":
        verdict = "UNANSWERABLE (F2 failed: a violation could not have been seen)"
    res["verdict"] = verdict
    print("VERDICT:", verdict)
    path.write_text(json.dumps(res, indent=1, default=float) + "\n")


def load_real(name):
    import atlas
    if name == "xes3g5m":
        grid = pg.Grid(atlas.xes3g5m_rows())
        n = pg.check_against_classify(grid, 300)
        grid.subset(grid.top_items(kb.XES_TOP))
    else:
        grid = pg.Grid(atlas.ednet_rows())
        n = pg.check_against_classify(grid, 300)
    grid._raw = None
    check_cells(grid.FT[:3000], grid.FP[:3000], grid.Y[:3000], np.random.default_rng(0), start=grid.start[:3000])
    print(f"{name}: {grid.shape[0]:,} learners, {grid.shape[1]} items; {n} pairs checked against classify", flush=True)
    return grid


def run_real():
    fl = json.loads((OUT / "floor.json").read_text())
    if not fl.get("passes"):
        raise SystemExit("reproduction or F1 failed; nothing is read")
    corp = sys.argv[sys.argv.index("--corpora") + 1].split(",") if "--corpora" in sys.argv else ["xes3g5m", "ednet"]
    path = OUT / "real.json"
    res = json.loads(path.read_text()) if path.exists() else {}
    for name in corp:
        t0 = time.time()
        grid = load_real(name)
        FT, FP, Y = grid.FT, grid.FP, grid.Y
        cand = candidates(FT, FP, Y)
        p = int(cand.sum())
        ent = dict(learners=int(FT.shape[0]), items=int(FT.shape[1]), readable_pairs=p,
                   ordered_pairs=int(FT.shape[1] * (FT.shape[1] - 1)))
        if p < 100:
            ent["verdict"] = "UNANSWERABLE (fewer than 100 readable pairs)"
            res[name] = ent
            continue
        q = q_for(p)
        runs = []
        for k in (0, 1):
            rng = np.random.default_rng([SEED, 3, k])
            pi, qbar, med = cpss(FT, FP, Y, rng, cand, q)
            s = summarise_pi(pi, cand, q)
            s.update(q_mean=qbar, median_min_cell=med)
            runs.append(s)
            print(f"  {name} run {k}: p {p} q {q} selected@0.75 {s['0.75']['selected']} bound {s['bounds']['0.75']:.3f} "
                  f"reverse-also {s['0.75']['reverse_also_selected']:.2f} ({time.time() - t0:.0f}s)", flush=True)
        rng = np.random.default_rng([SEED, 4])
        pid, qd, medd = cpss(FT, FP, Y, rng, cand, q, deranged=True, start=grid.start)
        der = summarise_pi(pid, cand, q)
        der.update(q_mean=qd, median_min_cell=medd)
        from shared.controls import check_control_scale
        scale = check_control_scale({"real": runs[0]["median_min_cell"], "deranged": medd}, ["deranged"], strict=False)
        bound = runs[0]["bounds"]["0.75"]
        dsel = der["0.75"]["selected"]
        ent.update(q=q, real=runs, deranged=der, control_scale=scale,
                   verdict=("BOUND HONEST UNDER THE DERANGED NULL" if dsel <= bound
                            else "BOUND VIOLATED UNDER THE DERANGED NULL"),
                   deranged_minus_bound=dsel - bound)
        print(f"  {name}: deranged selected@0.75 {dsel} vs bound {bound:.3f} -> {ent['verdict']} "
              f"({time.time() - t0:.0f}s)", flush=True)
        res[name] = ent
        path.write_text(json.dumps(res, indent=1, default=float) + "\n")
        del grid, FT, FP, Y


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "floor"
    {"floor": run_floor, "sim": run_sim, "real": run_real}[mode]()
