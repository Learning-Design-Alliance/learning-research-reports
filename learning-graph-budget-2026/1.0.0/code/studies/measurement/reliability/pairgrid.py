"""The prerequisite drop for every ordered pair at once, by learner group and lag band.

`studies/identifiability/overlap/positivity.classify` reads one pair at a time and loops over the
learners who reached B. That is the reference implementation and stays the reference: this module is
the same arithmetic laid out as matrices so that every ordered pair of a corpus, many learner splits
and several lag bands can be scored in one pass. Three studies use it
(`lag_band_reliability.py`, `kappa_bar.py`, `raise_kappa_finish.py`), which is why it is a module and
not a copy in each.

THE DEFINITIONS ARE positivity.py's, unchanged:

  reached B    a learner's first touch of B; the outcome is the outcome AT that first touch.
  MASTERED     A first passed strictly before B's first touch.
  FAILED       A first touched strictly before B's first touch, and not passed before it.
  NEVER        A not touched before B (excluded from the drop).
  drop(A,B)    mean outcome at B among MASTERED minus among FAILED.
  lag          t(first touch of B) - t(first touch of A), in days (lag_bands.py's definition: the
               same for both cells and not conditioned on A's outcome timing).

`check_against_classify()` asserts the two implementations agree cell for cell on a corpus sample
before anything built on this module is read. A vectorised reimplementation that has not been
checked against the loop it replaces is a new instrument, not a faster old one.

Times are float seconds; "never" is +inf.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "studies/identifiability/overlap"))
sys.path.insert(0, str(ROOT / "studies/identifiability/latent-shape"))
sys.path.insert(0, str(ROOT))

DAY = 86400.0
#: lag_bands.py's bands, in days. LATE pools [7, 30) and [30, inf) as lag_bands.py does.
BANDS = {"EARLY": (0.0, 1.0), "MID": (1.0, 7.0), "LATE": (7.0, math.inf), "ALL": (-math.inf, math.inf)}


def to_seconds(t) -> float:
    from lag_bands import to_seconds as _ts
    return _ts(t)


class Grid:
    """Learner x item matrices of first touch, first pass and outcome at first touch."""

    def __init__(self, rows, timed: bool = True):
        from positivity import states, timelines
        if timed:
            rows = ((u, i, ok, to_seconds(t), h1, h2) for u, i, ok, t, h1, h2 in rows)
        tl = timelines(rows)
        ft, fp, oat = states(tl)
        self.learners = sorted(ft)
        items = sorted({i for d in ft.values() for i in d})
        self.items = items
        col = {it: j for j, it in enumerate(items)}
        n, k = len(self.learners), len(items)
        FT = np.full((n, k), np.inf)
        FP = np.full((n, k), np.inf)
        Y = np.zeros((n, k), np.float32)
        for r, u in enumerate(self.learners):
            for it, t in ft[u].items():
                FT[r, col[it]] = float(t)
                Y[r, col[it]] = 1.0 if oat[u][it] else 0.0
            for it, t in fp[u].items():
                FP[r, col[it]] = float(t)
        self.FT, self.FP, self.Y = FT, FP, Y
        self.start = np.where(np.isfinite(FT), FT, np.inf).min(1)
        self._raw = (ft, fp, oat)

    def subset(self, cols):
        """Keep only these item columns (A and B both restricted to them)."""
        cols = np.asarray(cols)
        self.FT, self.FP, self.Y = self.FT[:, cols], self.FP[:, cols], self.Y[:, cols]
        self.items = [self.items[c] for c in cols]
        return self

    def top_items(self, n):
        """Column indices of the n items the most learners reached (ties by item id)."""
        reach = np.isfinite(self.FT).sum(0)
        return np.array(sorted(range(len(self.items)), key=lambda j: (-reach[j], self.items[j]))[:n])

    @property
    def shape(self):
        return self.FT.shape


def column_cells(FT, FP, Y, b, groups, bands=("ALL",), lag_scale=DAY, thin=None, rng=None,
                 donor=None, start=None, thinned_all=None):
    """Cell counts and successes for every A against one B, per learner group and band.

    groups  (n_learners, G) float32 0/1 membership matrix; a learner may belong to several groups
            (e.g. half 0 of split 1 and half 1 of split 2) -- membership is one column per group.
    thin    optional (K,) per-A keep-probability applied to every (learner, A) encounter in the
            band(s); used for size matching. Requires rng.
    donor   optional (n_learners,) index: the A-side history (first touch / first pass) of learner
            i is taken from learner donor[i], re-anchored to i's own start time. The B side (who
            reached B, when, and with what outcome) is untouched. This is the deranged arm.
    start   (n_learners,) each learner's first timestamp; needed with donor so lags stay on the
            recipient's own clock.
    thinned_all  optional {name: (K,) keep-probability}: for each, the ALL-lag cells thinned at
            random per (learner, A) encounter, returned as band "THIN_<name>". This is the
            size-matched control for a lag band: same expected cell size, no lag information.

    Returns dict band -> dict(nm, sm, nf, sf) each (G, K) float arrays.
    """
    tb_all = FT[:, b]
    L = np.nonzero(np.isfinite(tb_all))[0]
    out = {}
    if len(L) == 0:
        K = FT.shape[1]
        z = np.zeros((groups.shape[1], K))
        return {bd: dict(nm=z, sm=z, nf=z, sf=z) for bd in bands}
    tb = tb_all[L][:, None]
    y = Y[L, b].astype(np.float32)[:, None]
    if donor is None:
        TA, PA = FT[L], FP[L]
    else:
        d = donor[L]
        shift = (start[L] - start[d])[:, None] if start is not None else 0.0
        TA, PA = FT[d] + shift, FP[d] + shift
    before = TA < tb
    mastered = PA < tb
    failed = before & ~mastered
    before[:, b] = False
    mastered[:, b] = False
    failed[:, b] = False
    lag = (tb - TA) / lag_scale
    S = groups[L].T  # (G, n_b)
    for bd in bands:
        lo, hi = BANDS[bd]
        if bd == "ALL":
            inband = before
        else:
            inband = before & (lag >= lo) & (lag < hi)
        if thin is not None:
            inband = inband & (rng.random(inband.shape, dtype=np.float32) < thin[None, :])
        m = (mastered & inband).astype(np.float32)
        f = (failed & inband).astype(np.float32)
        out[bd] = dict(nm=S @ m, sm=S @ (m * y), nf=S @ f, sf=S @ (f * y))
    for name, keep in (thinned_all or {}).items():
        inband = before & (rng.random(before.shape, dtype=np.float32) < keep[None, :])
        m = (mastered & inband).astype(np.float32)
        f = (failed & inband).astype(np.float32)
        out["THIN_" + name] = dict(nm=S @ m, sm=S @ (m * y), nf=S @ f, sf=S @ (f * y))
    return out


def drops(c, min_cell):
    """drop, se and readable mask from one band's cell dict (arrays of any matching shape)."""
    nm, sm, nf, sf = c["nm"], c["sm"], c["nf"], c["sf"]
    ok = (nm >= min_cell) & (nf >= min_cell)
    with np.errstate(invalid="ignore", divide="ignore"):
        pm = np.where(nm > 0, sm / np.maximum(nm, 1), np.nan)
        pf = np.where(nf > 0, sf / np.maximum(nf, 1), np.nan)
        d = pm - pf
        # binomial se; ddof=1 as raise_kappa.drops_se uses (var(ddof=1) = p(1-p) n/(n-1))
        vm = pm * (1 - pm) * nm / np.maximum(nm - 1, 1)
        vf = pf * (1 - pf) * nf / np.maximum(nf - 1, 1)
        se = np.sqrt(vm / np.maximum(nm, 1) + vf / np.maximum(nf, 1))
    se = np.where(se > 0, se, np.nan)
    return np.where(ok, d, np.nan), np.where(ok, se, np.nan), ok


def check_against_classify(grid: Grid, n_pairs=300, seed=0) -> int:
    """Assert the matrix cells equal positivity.classify's cells on a random sample of pairs."""
    from positivity import at_item, classify
    ft, fp, oat = grid._raw
    idx = at_item(ft, oat)
    rng = np.random.default_rng(seed)
    K = len(grid.items)
    groups = np.ones((len(grid.learners), 1), np.float32)
    checked = 0
    for _ in range(n_pairs):
        a, b = rng.choice(K, 2, replace=False)
        cells = column_cells(grid.FT, grid.FP, grid.Y, b, groups)["ALL"]
        ref = classify((grid.items[a], grid.items[b]), ft, fp, oat, idx)
        got = (int(cells["nm"][0, a]), int(cells["sm"][0, a]), int(cells["nf"][0, a]), int(cells["sf"][0, a]))
        want = (len(ref["mastered"]), int(sum(ref["mastered"])), len(ref["failed"]), int(sum(ref["failed"])))
        assert got == want, f"pair {grid.items[a]}->{grid.items[b]}: matrix {got} vs classify {want}"
        checked += 1
    return checked


def derangement(n, rng, blocks=None):
    """A permutation with no fixed points, optionally within blocks (list of index arrays)."""
    perm = np.arange(n)
    for blk in (blocks if blocks is not None else [np.arange(n)]):
        blk = np.asarray(blk)
        if len(blk) < 2:
            continue
        order = rng.permutation(blk)
        perm[order] = np.roll(order, -1)  # a single cycle through the block: no fixed points
    assert not np.any(perm == np.arange(n)) or blocks is not None
    return perm
