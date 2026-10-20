"""
Null models for induced structure. One implementation, because there is one correct one.

Two nulls, and the difference between them is the single most consequential thing in this area —
running only the first inverted one published result and erased another:

    difficulty_draws   each item resampled independently at its observed solve rate.
                       Removes dependencies. ALSO removes learner ability, since independent
                       resampling gives every learner the same expected score.

    fixed_margin_draws both margins held: items solved per learner (ability) and learners solving
                       each item (difficulty). Leaves only the association between SPECIFIC items,
                       which is the only thing a prerequisite claim can be about.

Ability alone produces exactly the Guttman-like pattern an inductive method reads as implication —
a strong learner solves the hard item and the easy one, a weak learner neither, so counterexamples
are rare with no dependency present. A relation made entirely of ability passes the difficulty null
untouched. Pre-registered as E7 in
`../../procedures/task-structure/typed-grammar-cycle0/PRE-REGISTRATION.md`: a relation clearing only the
difficulty null is reported as NOT ESTABLISHED, never as weak evidence.
"""

from __future__ import annotations

import random
from typing import Iterator


def difficulty_draws(patterns: list[set[int]], m: int, rng: random.Random,
                     draws: int) -> Iterator[list[set[int]]]:
    """Same per-item solve rates, every dependency removed."""
    n = len(patterns)
    rates = [sum(1 for p in patterns if i in p) / n for i in range(m)] if n else [0.0] * m
    for _ in range(draws):
        yield [{i for i, r in enumerate(rates) if rng.random() < r} for _ in range(n)]


def fixed_margin_draws(patterns: list[set[int]], m: int, rng: random.Random,
                       draws: int) -> Iterator[list[set[int]]]:
    """Successive shuffles holding BOTH margins, as a chain rather than `draws` fresh shuffles.

    Two things make this ~35x faster than the obvious version, which otherwise dominates runtime at
    roughly 50x the cost of the IITA call it is controlling:

    - **Swaps are sampled from the 1-cells.** Picking a random 2x2 and hoping it is a checkerboard
      almost always fails on a sparse or dense matrix; picking two 1s and testing the opposite
      corners accepts far more often.
    - **The chain is reused.** Burn in once, then take each draw after a shorter run of swaps.
      Successive draws are correlated, which is fine for a percentile over draws, and the burn-in
      is what removes dependence on the observed matrix.

    Both margins are preserved exactly — asserted by `test_nulls.py`.
    """
    mat = [[1 if i in p else 0 for i in range(m)] for p in patterns]
    n = len(mat)
    ones = [(r, c) for r in range(n) for c in range(m) if mat[r][c]]
    if n < 2 or m < 2 or len(ones) < 2:
        for _ in range(draws):
            yield patterns
        return

    def swap_round(k: int) -> None:
        for _ in range(k):
            i, j = rng.randrange(len(ones)), rng.randrange(len(ones))
            (r1, c1), (r2, c2) = ones[i], ones[j]
            if r1 == r2 or c1 == c2 or mat[r1][c2] or mat[r2][c1]:
                continue
            mat[r1][c1] = mat[r2][c2] = 0
            mat[r1][c2] = mat[r2][c1] = 1
            ones[i], ones[j] = (r1, c2), (r2, c1)

    swap_round(10 * len(ones))
    for _ in range(draws):
        swap_round(max(1, len(ones) // 2))
        yield [{i for i in range(m) if row[i]} for row in mat]


def control(patterns: list[set[int]], m: int, observed: int, rng: random.Random,
            draws, estimator) -> dict:
    """Score `observed` against a null. `draws` is one of the generators above."""
    sizes = sorted(len(estimator(d, m)[0]) for d in draws(patterns, m, rng, 200))
    p95 = sizes[int(0.95 * len(sizes))]
    return {"observed": observed, "null_mean": sum(sizes) / len(sizes), "null_p95": p95,
            "null_max": sizes[-1], "survives": observed > p95}
