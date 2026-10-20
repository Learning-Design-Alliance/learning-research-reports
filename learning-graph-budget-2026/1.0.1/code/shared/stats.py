"""
The statistical primitives, in one place, with their invariants enforced rather than remembered.

Four bugs in this programme were not wrong formulas. They were correct formulas answering a slightly
different question than the one asked, and each was caught by luck -- by a number looking odd -- long
after a check could have caught it. This module exists so they cannot recur:

| what went wrong | where | enforced here by |
| --- | --- | --- |
| `argsort(argsort(x))` ranks ties by array position | `studies/measurement/consistency/agreement.py` | `rank`, the only sanctioned ranking |
| a point estimate landed outside its own bootstrap CI | same | `bootstrap` asserts containment |
| a random split shared groups between train and test | the Dowling typing split, 0.992 -> 0.981 | `grouped_folds` requires groups |
| an orientation sign was read off the test fold | `studies/producers/alcpl-audit/leaderboard.py`, first run | `fit_sign` takes training rows only |
| a published reference figure silently stopped reproducing | `studies/identifiability/junyi/critic_vs_gating.py` | `positive_control` exits on mismatch |

This is `CLAUDE.md`'s "enforce a rule in one place" applied to the research harness. The helpers are
deliberately dull; the point is that the correct behaviour is the *only reachable* behaviour, so no
future analysis has to remember the lesson.

`check_idioms.py` is the other half: it fails on the raw idioms these replace.
"""

from __future__ import annotations

import sys
from collections.abc import Callable, Sequence

import numpy as np

__all__ = ["rank", "spearman", "partial_spearman", "bootstrap", "paired_bootstrap",
           "grouped_folds", "fit_sign", "positive_control", "BootstrapError", "kappa_nominal"]


class BootstrapError(AssertionError):
    """A bootstrap whose interval does not contain its own point estimate."""


def rank(v: Sequence[float] | np.ndarray) -> np.ndarray:
    """Ranks, with ties averaged.

    `np.argsort(np.argsort(x))` is the idiom this replaces. It gives tied values distinct ranks in
    whatever order they happen to sit in the array -- arbitrary ordering presented as data. Invisible
    on continuous measurements, severe on coarse ones: in `agreement.py` the statistic took seven
    distinct values over 240 rows, and positional tie-breaking put a partial correlation at +0.237
    with a bootstrap interval of [-0.070, +0.175], an impossibility and the only reason it was
    noticed.
    """
    v = np.asarray(v, dtype=float)
    if v.ndim != 1:
        raise ValueError(f"rank expects a 1-D sequence, got shape {v.shape}")
    order = np.argsort(v, kind="mergesort")
    r = np.empty(len(v), dtype=float)
    r[order] = np.arange(1, len(v) + 1, dtype=float)
    sv = v[order]
    i = 0
    while i < len(sv):
        j = i
        while j + 1 < len(sv) and sv[j + 1] == sv[i]:
            j += 1
        if j > i:
            r[order[i:j + 1]] = (i + j + 2) / 2.0
        i = j + 1
    return r


def _centred_rank(v) -> np.ndarray:
    r = rank(v)
    return r - r.mean()


def spearman(x, y) -> float:
    """Spearman correlation on tie-averaged ranks. NaN pairs dropped pairwise."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    keep = ~(np.isnan(x) | np.isnan(y))
    x, y = x[keep], y[keep]
    if len(x) < 3:
        return float("nan")
    rx, ry = _centred_rank(x), _centred_rank(y)
    d = np.sqrt((rx ** 2).sum() * (ry ** 2).sum())
    return float((rx * ry).sum() / d) if d else float("nan")


def kappa(a, b) -> float:
    """Cohen's kappa on two binary decision vectors -- chance-corrected agreement.

    Lives here because two studies need it and, per this repo's rule, a rule that lives in one copy
    is a rule the next caller does not have. `studies/measurement/reliability/tail.py` and `studies/measurement/reliability/course_grain.py`
    both had their own identical copy before this.

    WHY IT IS IN THIS PROGRAMME AT ALL. `studies/measurement/reliability/COURSE-GRAIN.md` showed a rank correlation is
    the wrong thing to gate an assay on: a correlation is a variance ratio, so it rewards spread
    ANYWHERE in the range -- including far above the assertion bar, where it changes no decision --
    and an order statistic with wide natural spread cleared A5's 0.80 gate at +0.992 while a drop
    tops out at +0.654. Kappa scores the assert/do-not DECISION, which is what an assay emits, and
    corrects for the agreement a given base rate produces on its own. That correction is the point:
    on XES3G5M more than half of all readable pairs already clear the assertion bar, so raw
    agreement would be high before the instrument did anything.

    Returns NaN when either vector is constant, because chance agreement is then 1 and the
    coefficient is undefined -- not 0, which would read as "no better than chance".
    """
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) < 3:
        return float("nan")
    po = float((a == b).mean())
    pa, pb = float(a.mean()), float(b.mean())
    pe = pa * pb + (1 - pa) * (1 - pb)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def kappa_nominal(a: Sequence, b: Sequence) -> float:
    """Cohen's kappa for two coders assigning one of several unordered labels to the same items.

    `kappa` above is the binary case and coerces to bool, so a three-way code passed to it would
    silently collapse to "empty or not". This is the general form: chance agreement is the sum over
    labels of the product of each coder's marginal share. NaN when chance agreement is 1 (both coders
    used one identical label throughout), for the same reason as `kappa`.
    """
    a, b = list(a), list(b)
    if len(a) != len(b):
        raise ValueError("both coders must code the same items")
    if len(a) < 3:
        return float("nan")
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    labels = set(a) | set(b)
    pe = sum((a.count(k) / n) * (b.count(k) / n) for k in labels)
    return float((po - pe) / (1 - pe)) if pe < 1 else float("nan")


def partial_spearman(x, y, z) -> float:
    """Spearman of x and y with z partialled out, all on tie-averaged ranks."""
    rx, ry, rz = rank(x), rank(y), rank(z)

    def resid(a: np.ndarray) -> np.ndarray:
        design = np.c_[np.ones(len(rz)), rz]
        return a - design @ np.linalg.lstsq(design, a, rcond=None)[0]

    a, b = resid(rx), resid(ry)
    d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float((a * b).sum() / d) if d else float("nan")


def bootstrap(stat: Callable[[np.ndarray], float], n: int, rng: np.random.Generator,
              reps: int = 2000, *, alpha: float = 0.05,
              tolerance: float = 0.02) -> tuple[float, float, float]:
    """Point estimate and percentile interval, with containment enforced.

    `stat` takes an index array and returns a scalar; it is called once on `arange(n)` for the point
    estimate and `reps` times on resamples.

    **A point estimate outside its own interval raises rather than returning.** It means the
    statistic is not the same function of a resample as of the sample -- typically something
    re-derived inside `stat` that should have been fixed outside it. `tolerance` allows the small
    overshoot a genuinely discrete statistic can show at the interval edge.
    """
    point = float(stat(np.arange(n)))
    vals = []
    for _ in range(reps):
        v = stat(rng.integers(0, n, n))
        if not np.isnan(v):
            vals.append(float(v))
    if len(vals) < max(1, reps // 10):
        return point, float("nan"), float("nan")
    lo = float(np.percentile(vals, 100 * alpha / 2))
    hi = float(np.percentile(vals, 100 * (1 - alpha / 2)))
    span = max(hi - lo, 1e-12)
    if point < lo - tolerance * span or point > hi + tolerance * span:
        raise BootstrapError(
            f"point estimate {point:+.4f} lies outside its own {100 * (1 - alpha):.0f}% interval "
            f"[{lo:+.4f}, {hi:+.4f}]. The statistic is not the same function of a resample as of "
            f"the sample -- check for anything re-derived from the data inside `stat` (a ranking, a "
            f"fitted sign, a threshold) that should have been fixed outside it.")
    return point, lo, hi


def paired_bootstrap(a: Callable[[np.ndarray], float], b: Callable[[np.ndarray], float],
                     n: int, rng: np.random.Generator,
                     reps: int = 2000) -> tuple[float, float, float]:
    """Difference b - a, on the SAME resample each draw.

    Comparing two arms measured on one sample with independent intervals throws away the pairing
    that makes it a comparison, and overstates the uncertainty of the difference.
    """
    point = float(b(np.arange(n))) - float(a(np.arange(n)))
    d = []
    for _ in range(reps):
        i = rng.integers(0, n, n)
        va, vb = a(i), b(i)
        if not (np.isnan(va) or np.isnan(vb)):
            d.append(float(vb - va))
    if not d:
        return point, float("nan"), float("nan")
    return point, float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def grouped_folds(groups: Sequence, k: int, rng) -> np.ndarray:
    """Fold assignment that never splits a group across train and test.

    There is deliberately no `random_folds` beside this. Every split in this programme has a grouping
    that matters -- corpus, domain, area, learner -- and a random split silently shares it: the
    typing experiment scored 0.992 on a random split of Dowling and 0.981 once made domain-disjoint,
    with one row's gain flipping sign. Callers with genuinely exchangeable rows pass
    `range(len(rows))`, which makes that claim visible at the call site.
    """
    g = list(groups)
    uniq = sorted(set(g), key=str)
    if len(uniq) < k:
        raise ValueError(f"{len(uniq)} distinct groups cannot fill {k} disjoint folds")
    order = list(uniq)
    rng.shuffle(order)
    fold_of = {name: i % k for i, name in enumerate(order)}
    return np.array([fold_of[x] for x in g])


def fit_sign(score: Sequence[float], label: Sequence[int]) -> float:
    """+1 or -1, chosen so `score` points the same way as `label`. TRAINING rows only.

    An antisymmetric feature is equally informative either way up, so which way up is an empirical
    question -- and answering it from the rows about to be scored is a leak. The first run of
    `leaderboard.py` scored a generality feature at 0.257, i.e. 0.743 inverted; flipping it by hand
    after seeing that would have been exactly this leak.
    """
    s, y = np.asarray(score, float), np.asarray(label, int)
    if len(s) != len(y):
        raise ValueError("score and label must be the same length")
    if len(set(y.tolist())) < 2:
        return 1.0
    return 1.0 if s[y == 1].mean() >= s[y == 0].mean() else -1.0


def positive_control(actual: float, expected: float, tolerance: float, what: str) -> None:
    """Exit unless a known reference figure still reproduces.

    Run before an instrument produces a new number. `critic_vs_gating.py` added this after a
    `rating: None` silently became NaN and moved a reference correlation from +0.371 to +0.169 --
    caught only because the published figure happened to be to hand. A control that warns gets
    ignored; this one stops the run.
    """
    if not np.isfinite(actual) or abs(actual - expected) > tolerance:
        print(f"\nPOSITIVE CONTROL FAILED: {what}\n"
              f"  reproduced {actual:+.4f}, expected {expected:+.4f} +/- {tolerance:.4f}\n"
              f"  the instrument does not reproduce its own reference figure; stopping rather than "
              f"reporting new numbers from it.", file=sys.stderr)
        raise SystemExit(1)
