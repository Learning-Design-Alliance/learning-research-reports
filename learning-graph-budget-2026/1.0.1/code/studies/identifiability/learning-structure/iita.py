"""
Corrected Inductive Item Tree Analysis — a faithful port of DAKS (Uenlue & Sargin, CRAN v2.1-3).

`surmise.py` was written from the KST *idea*: count the forbidden pattern "B mastered without A",
normalise by what independence predicts, keep pairs that are asymmetric enough. IITA is the
established algorithm for the same problem, and it differs in three ways that matter:

1. **It searches over whole quasi-orders, not independent pairs.** `ind_gen` sweeps a threshold over
   the distinct counterexample counts and builds a NESTED CHAIN of candidate relations, enforcing
   transitivity at every step. Output is always a quasi-order — a genuine knowledge-space object.
   `surmise.py` tests each pair alone and can emit a relation that is not transitively closed.

2. **Selection is model-based, not a threshold.** For each candidate it estimates a single error
   rate and predicts how many counterexamples EACH pair should show under that candidate, then picks
   the candidate minimising squared error against the observed counts. `surmise.py` compares each
   pair against an independence baseline, which knows nothing about the rest of the relation.

3. **Its baseline differs per pair by relation status** — implied, unrelated, or reverse-implied —
   whereas an independence baseline treats every pair the same.

Ported here to compare against, not to replace: an unvalidated home-grown estimator standing in for
a published one is exactly the kind of thing this programme is supposed to catch.

    python3 experiments/learning-structure/iita.py compare
"""

from __future__ import annotations

import argparse
import itertools
import random


def counterexamples(patterns: list[set[int]], m: int) -> list[list[int]]:
    """b[i][j] = respondents who solved j but NOT i — the counterexamples to "i precedes j"."""
    b = [[0] * m for _ in range(m)]
    for i in range(m):
        for j in range(m):
            if i != j:
                b[i][j] = sum(1 for p in patterns if i not in p and j in p)
    return b


def ind_gen(b: list[list[int]], m: int) -> list[set[tuple[int, int]]]:
    """Nested chain of candidate quasi-orders, transitivity enforced at each step.

    Faithful to DAKS `ind_gen`: start from the pairs with the fewest counterexamples, then admit
    pairs at successively higher thresholds, discarding any that would break transitivity against
    what is already accepted.
    """
    lo = min(b[i][j] for i in range(m) for j in range(m) if i != j)
    first = {(i, j) for i in range(m) for j in range(m) if i != j and b[i][j] == lo}
    chain = [first]
    accepted = set(first)

    thresholds = sorted({b[i][j] for i in range(m) for j in range(m) if i != j})
    thresholds = [t for t in thresholds if t != 0]

    for t in thresholds:
        new = {(i, j) for i in range(m) for j in range(m)
               if i != j and b[i][j] <= t and (i, j) not in accepted}
        if not new:
            continue
        # Prune until transitively consistent with `accepted ∪ new`.
        while True:
            union = accepted | new
            drop = set()
            for (a, c) in new:
                for h in range(m):
                    if h in (a, c):
                        continue
                    if (c, h) in union and (a, h) not in union:
                        drop.add((a, c))
                        break
                    if (h, a) in union and (h, c) not in union:
                        drop.add((a, c))
                        break
            if not drop:
                break
            new -= drop
        if new:
            accepted = accepted | new
            chain.append(set(accepted))

    # Drop duplicates, preserving order.
    out, seen = [], []
    for a in chain:
        if a and a not in seen:
            seen.append(a)
            out.append(a)
    return out


def corrected_iita(patterns: list[set[int]], m: int) -> tuple[set[tuple[int, int]], float, float]:
    """Returns the selected quasi-order, its diff value, and its estimated error rate."""
    b = counterexamples(patterns, m)
    p = [sum(1 for pat in patterns if i in pat) for i in range(m)]
    return iita_from_counts(b, p, len(patterns), m)


def iita_from_counts(b: list[list[int]], p: list[int], n: int,
                     m: int) -> tuple[set[tuple[int, int]], float, float]:
    """corrected_iita from its sufficient statistics: counterexample counts b, solve counts p, n.

    Everything IITA does after counting reads only these, so a caller holding a 0/1 matrix can count
    with a matrix product and skip the per-pattern loop (iita_dense.py runs this ~10^5 times).
    """
    candidates = ind_gen(b, m)
    if not candidates:
        return set(), float("nan"), float("nan")

    best, best_diff, best_err = set(), float("inf"), float("nan")
    for A in candidates:
        # One error rate for the whole candidate: the average share of counterexamples among
        # respondents who solved the consequent.
        terms = [b[i][j] / p[j] for (i, j) in A if p[j] > 0]
        if not terms:
            continue
        err = sum(terms) / len(terms)

        total = 0.0
        for i, j in itertools.permutations(range(m), 2):
            if (i, j) in A:
                exp = err * p[j]
            elif (j, i) not in A:
                exp = (1 - p[i] / n) * p[j]
            else:
                exp = p[j] - p[i] + p[i] * err
            total += (b[i][j] - exp) ** 2
        diff = total / (m * m - m)
        if diff < best_diff:
            best, best_diff, best_err = A, diff, err
    return best, best_diff, best_err


def simulate_blim(rng: random.Random, items: int, size: int, ce: float, lg: float,
                  delta: float) -> tuple[list[set[int]], set[tuple[int, int]], list[str]]:
    """DAKS's own generative model — a port of its `simu`.

    A random transitive relation, the knowledge states it induces, a state drawn per respondent,
    then responses with a UNIFORM careless-error rate `ce` and lucky-guess rate `lg`.

    This exists to remove a bias in the comparison. `surmise.py`'s simulator was written alongside
    `surmise.py` and gives each KC its own difficulty, which violates IITA's assumption of a single
    global error rate. Testing only there would flatter the home-grown method. This is IITA's home
    ground, and a fair comparison needs both.
    """
    # Random relation, then transitive closure — the true quasi-order.
    rel = {(i, j) for i in range(items) for j in range(items) if i != j and rng.random() < delta}
    for _ in range(items):
        grown = rel | {(a, d) for a, b in rel for c, d in rel if b == c and a != d}
        if grown == rel:
            break
        rel = grown

    # States: sets closed under the relation (if j is in the state and (i,j) in rel, i must be too).
    # Enumerating all of them is exponential, so states are sampled by closing random item subsets —
    # every closure IS a valid state, which is what the sampling needs to be sound.
    def close(seed_items: set[int]) -> frozenset[int]:
        cur = set(seed_items)
        while True:
            add = {i for (i, j) in rel if j in cur and i not in cur}
            if not add:
                return frozenset(cur)
            cur |= add

    patterns = []
    for _ in range(size):
        k = rng.randrange(items + 1)
        state = close(set(rng.sample(range(items), k)))
        resp = set()
        for i in range(items):
            hit = (rng.random() > ce) if i in state else (rng.random() < lg)
            if hit:
                resp.add(i)
        patterns.append(resp)
    return patterns, rel, [f"kc{i:02d}" for i in range(items)]


def as_patterns(mst) -> tuple[list[set[int]], list[str]]:
    """A `surmise.Mastery` as the 0/1 response patterns IITA consumes."""
    idx = {k: i for i, k in enumerate(mst.kcs)}
    return [{idx[k] for k in mst.mastered[l]} for l in mst.learners], mst.kcs


def compare(args) -> int:
    # Imported inside the function: surmise imports THIS module for its estimator, so a top-level
    # import here would be circular.
    from surmise import infer_legacy_pairwise, score, simulate

    print("surmise.py (independence-normalised pairs) vs corrected IITA (DAKS port)")
    print(f"{args.kcs} KCs, slip {args.slip}, guess {args.guess}; both scored against the")
    print("transitive closure, which is what each method estimates.\n")
    print(f"  {'n':>5} {'order':12}  {'method':16} {'found':>6} {'prec':>6} {'recall':>7} {'spurious':>9}")

    for n in args.learners:
        for label, curriculum in (("randomised", False), ("fixed", True)):
            m, truth = simulate(random.Random(args.seed), n, args.kcs,
                                args.edge_prob, curriculum, args.slip, args.guess)
            # The null-calibrated cut must be passed explicitly. Omitting it falls back to the
            # hardcoded VIOLATION_THRESHOLD of 0.25, which surmise.py's own calibration already
            # showed is far too strict — true edges sit near 0.4. A first version of this
            # comparison did exactly that and made surmise.py look like it LOST recall as data
            # grew, which is backwards and was the tell.
            sc_s = score(infer_legacy_pairwise(m, min_asymmetry=args.asymmetry), truth, m.kcs)

            pats, kcs = as_patterns(m)
            rel, diff, err = corrected_iita(pats, len(kcs))
            found = [{"prereq": kcs[i], "of": kcs[j]} for i, j in rel]
            sc_i = score(found, truth, m.kcs)

            print(f"  {n:5} {label:12}  {'surmise.py':16} {sc_s['found']:6} "
                  f"{sc_s['precision_closure']:6.2f} {sc_s['recall_closure']:7.2f} "
                  f"{sc_s['spurious']:9}")
            print(f"  {'':5} {'':12}  {'corrected IITA':16} {sc_i['found']:6} "
                  f"{sc_i['precision_closure']:6.2f} {sc_i['recall_closure']:7.2f} "
                  f"{sc_i['spurious']:9}   (diff {diff:.1f}, error rate {err:.3f})")
        print()
    return 0


def compare_blim(args) -> int:
    """Both methods on DAKS's own generative model — IITA's home ground."""
    from surmise import Mastery, infer_legacy_pairwise, score
    print("Both methods on DAKS's OWN model (basic local independence, uniform error rates).")
    print(f"{args.kcs} items, careless error {args.ce}, lucky guess {args.lg}, density "
          f"{args.delta}.\n")
    print(f"  {'n':>5}  {'method':16} {'true':>5} {'found':>6} {'prec':>6} {'recall':>7} "
          f"{'spurious':>9}")
    for n in args.learners:
        pats, truth, kcs = simulate_blim(random.Random(args.seed), args.kcs, n,
                                         args.ce, args.lg, args.delta)
        mastered = {f"s{i:04d}": {kcs[j] for j in p} for i, p in enumerate(pats)}
        m = Mastery(sorted(mastered), kcs, mastered)  # noqa: F821 — imported above
        truth_named = {(kcs[i], kcs[j]) for i, j in truth}

        sc_s = score(infer_legacy_pairwise(m, min_asymmetry=args.asymmetry), truth_named, kcs)

        rel, diff, err = corrected_iita(pats, len(kcs))
        sc_i = score([{"prereq": kcs[i], "of": kcs[j]} for i, j in rel], truth_named, kcs)

        print(f"  {n:5}  {'surmise.py':16} {len(truth):5} {sc_s['found']:6} "
              f"{sc_s['precision_closure']:6.2f} {sc_s['recall_closure']:7.2f} {sc_s['spurious']:9}")
        print(f"  {'':5}  {'corrected IITA':16} {len(truth):5} {sc_i['found']:6} "
              f"{sc_i['precision_closure']:6.2f} {sc_i['recall_closure']:7.2f} {sc_i['spurious']:9}"
              f"   (error rate {err:.3f})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare", help="head-to-head against surmise.py on simulated data")
    c.add_argument("--learners", type=int, nargs="+", default=[100, 300, 800])
    c.add_argument("--kcs", type=int, default=8)
    c.add_argument("--edge-prob", type=float, default=0.25)
    c.add_argument("--slip", type=float, default=0.05)
    c.add_argument("--guess", type=float, default=0.05)
    c.add_argument("--asymmetry", type=float, default=2.0)
    c.add_argument("--seed", type=int, default=20260912)
    c.set_defaults(func=compare)

    b = sub.add_parser("blim", help="head-to-head on DAKS's own generative model")
    b.add_argument("--learners", type=int, nargs="+", default=[100, 300, 800])
    b.add_argument("--kcs", type=int, default=8)
    b.add_argument("--ce", type=float, default=0.1, help="careless error rate")
    b.add_argument("--lg", type=float, default=0.1, help="lucky guess rate")
    b.add_argument("--delta", type=float, default=0.25)
    b.add_argument("--asymmetry", type=float, default=2.0)
    b.add_argument("--seed", type=int, default=20260912)
    b.set_defaults(func=compare_blim)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
