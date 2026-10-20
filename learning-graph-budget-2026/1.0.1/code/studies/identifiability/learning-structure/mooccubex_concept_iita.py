"""
Lift induced structure from items to concepts, through the Q-matrix.

`mooccubex_iita.py` induces dependencies between PROBLEMS. Problems are not capabilities, and the
whole point of a competency graph is the capability level. The bridge is the Q-matrix — in ECD terms
the evidence model, in CbKST terms the skill function — and this is the step that uses it.

The move is CbKST's: stop asking what a learner answered (the performance level) and ask what they
can do (the competence level). A learner's concept state is derived from their item outcomes through
the concept-problem map, and IITA then runs over concepts rather than problems.

Three things make this harder than the item-level run, and each gets a control:

**The mastery rule is a choice, not a fact.** "Has this learner mastered concept X" has to be
derived from the items tagged X, and there is no single right rule. `all` is DINA's conjunctive
assumption, `any` is its disjunctive opposite, `majority` sits between. A relation that appears
under one rule and not the others is an artifact of the rule, so all three are always reported.

**The Q-matrix manufactures dependencies.** If concepts X and Y are both tagged on one problem, a
learner's X-state and Y-state are computed from overlapping evidence and are dependent by
construction — nothing to do with learning. So concept sets are required to have DISJOINT problem
sets, which removes the confound at the source rather than trying to model it.

**Coverage is at the concept level now.** A learner counts only if they attempted at least one item
for every concept in the set, for the same reason the item-level run required complete attempts:
otherwise "not mastered" silently includes "never asked".

    python3 mooccubex_concept_iita.py [--attempts attempts.tsv] [--concept-problem concept-problem.txt]

Inputs default as in mooccubex_iita.py; the result goes to out/iita-concept-result.json.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from iita import corrected_iita

MAX_CONCEPTS = 8
MIN_LEARNERS = 50
N_NULL = 200
SEED = 20260912
RULES = ("all", "any", "majority")


def load(attempts_path: Path, cp_path: Path):
    c2p: dict[str, set[str]] = defaultdict(set)
    p2c: dict[str, set[str]] = defaultdict(set)
    for line in cp_path.read_text(encoding="utf-8").splitlines():
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            c2p[p[0]].add(p[1])
            p2c[p[1]].add(p[0])

    att: dict[str, dict[str, int]] = defaultdict(dict)
    for line in attempts_path.read_text(encoding="utf-8").splitlines():
        p = line.rstrip("\n").split("\t")
        if len(p) < 3:
            continue
        try:
            c = int(p[2])
        except ValueError:
            continue
        att[p[0]][p[1]] = max(att[p[0]].get(p[1], 0), 1 if c == 1 else 0)
    return c2p, p2c, att


def field_of(concept: str) -> str:
    """Concepts are `K_<name>_<field>`; the field is the natural grouping for a coherent set."""
    parts = concept.split("_")
    return parts[-1] if len(parts) >= 3 else "unknown"


def mastered(outcomes: list[int], rule: str) -> bool:
    if not outcomes:
        return False
    if rule == "all":
        return all(outcomes)
    if rule == "any":
        return any(outcomes)
    return sum(outcomes) * 2 > len(outcomes)


def concept_sets(c2p, p2c, att, max_concepts: int, min_learners: int):
    """Candidate sets: concepts of one field, with pairwise DISJOINT problem sets."""
    touched: dict[str, set[str]] = defaultdict(set)
    for u, probs in att.items():
        for pr in probs:
            for c in p2c.get(pr, ()):
                touched[c].add(u)

    by_field: dict[str, list[str]] = defaultdict(list)
    for c, users in touched.items():
        if len(users) >= min_learners:
            by_field[field_of(c)].append(c)

    out = []
    for field, concepts in by_field.items():
        concepts.sort(key=lambda c: (-len(touched[c]), c))  # id breaks ties: hash-seed independent
        chosen: list[str] = []
        used: set[str] = set()
        for c in concepts:
            probs = c2p[c] & set(p2c)
            # Disjointness is the control, not an optimisation: shared items make two concept
            # states dependent by construction.
            if probs and not (probs & used):
                chosen.append(c)
                used |= probs
            if len(chosen) >= max_concepts:
                break
        if len(chosen) < 3:
            continue
        covered = set.intersection(*(touched[c] for c in chosen))
        while len(chosen) > 3 and len(covered) < min_learners:
            chosen.pop()
            covered = set.intersection(*(touched[c] for c in chosen))
        if len(chosen) >= 3 and len(covered) >= min_learners:
            out.append((field, chosen, covered))
    return sorted(out, key=lambda t: (-len(t[2]), t[0]))


def patterns_for(concepts, learners, c2p, att, rule) -> list[set[int]]:
    pats = []
    for u in sorted(learners):
        got = set()
        for i, c in enumerate(concepts):
            outcomes = [att[u][p] for p in c2p[c] if p in att[u]]
            if mastered(outcomes, rule):
                got.add(i)
        pats.append(got)
    return pats


def difficulty_control(patterns, m, observed, rng) -> dict:
    """Same per-concept mastery rates, dependencies removed."""
    rates = [sum(1 for p in patterns if i in p) / len(patterns) for i in range(m)]
    sizes = []
    for _ in range(N_NULL):
        null = [{i for i, r in enumerate(rates) if rng.random() < r} for _ in patterns]
        rel, _, _ = corrected_iita(null, m)
        sizes.append(len(rel))
    sizes.sort()
    return {"observed": observed, "null_mean": sum(sizes) / len(sizes),
            "null_p95": sizes[int(0.95 * len(sizes))],
            "survives": observed > sizes[int(0.95 * len(sizes))]}


def fixed_margins_null(patterns: list[set[int]], m: int, rng: random.Random) -> list[set[int]]:
    """Shuffle the learner x concept matrix holding BOTH margins fixed.

    The control the difficulty null cannot be. That null resamples each concept independently at
    its marginal rate, which destroys any learner-ability factor — so a relation driven entirely by
    "some learners are better than others" sails through it. And ability alone produces exactly the
    Guttman-like pattern IITA reads as implication: a strong learner masters the hard concept and
    the easy one, a weak learner neither, so counterexamples are rare without any dependency.

    Holding row sums (how many concepts each learner mastered — ability) and column sums (how many
    learners mastered each concept — difficulty) fixed leaves only the association between specific
    concepts. Checkerboard swaps: find a 2x2 submatrix [[1,0],[0,1]] and flip it, which changes no
    margin.
    """
    mat = [[1 if i in pat else 0 for i in range(m)] for pat in patterns]
    n = len(mat)
    if n < 2 or m < 2:
        return patterns
    swaps = 20 * n * m
    for _ in range(swaps):
        r1, r2 = rng.randrange(n), rng.randrange(n)
        c1, c2 = rng.randrange(m), rng.randrange(m)
        if r1 == r2 or c1 == c2:
            continue
        if mat[r1][c1] == 1 and mat[r1][c2] == 0 and mat[r2][c1] == 0 and mat[r2][c2] == 1:
            mat[r1][c1], mat[r1][c2] = 0, 1
            mat[r2][c1], mat[r2][c2] = 1, 0
        elif mat[r1][c1] == 0 and mat[r1][c2] == 1 and mat[r2][c1] == 1 and mat[r2][c2] == 0:
            mat[r1][c1], mat[r1][c2] = 1, 0
            mat[r2][c1], mat[r2][c2] = 0, 1
    return [{i for i in range(m) if row[i]} for row in mat]


def ability_control(patterns, m, observed, rng) -> dict:
    sizes = []
    for _ in range(N_NULL):
        rel, _, _ = corrected_iita(fixed_margins_null(patterns, m, rng), m)
        sizes.append(len(rel))
    sizes.sort()
    return {"observed": observed, "null_mean": sum(sizes) / len(sizes),
            "null_p95": sizes[int(0.95 * len(sizes))],
            "survives": observed > sizes[int(0.95 * len(sizes))]}


def analyse(field, concepts, learners, c2p, att) -> dict:
    print("-" * 78)
    print(f"field {field!r}  —  {len(concepts)} concepts, {len(learners):,} learners covering all")
    rng = random.Random(SEED)
    per_rule = {}
    for rule in RULES:
        pats = patterns_for(concepts, learners, c2p, att, rule)
        rates = [sum(1 for p in pats if i in p) / len(pats) for i in range(len(concepts))]
        rel, diff, err = corrected_iita(pats, len(concepts))
        ctrl = difficulty_control(pats, len(concepts), len(rel), rng) if rel else None
        # Only worth running the stronger control on something that cleared the weaker one.
        abil = (ability_control(pats, len(concepts), len(rel), rng)
                if ctrl and ctrl["survives"] else None)
        per_rule[rule] = {
            "implications": sorted([[concepts[a], concepts[b]] for a, b in rel]),
            "n": len(rel), "error_rate": err, "control": ctrl, "ability_control": abil,
            "mastery_rates": {concepts[i]: rates[i] for i in range(len(concepts))},
        }
        if not rel:
            v = "none found"
        elif not ctrl["survives"]:
            v = "no (difficulty)"
        elif abil and abil["survives"]:
            v = "SURVIVES BOTH"
        else:
            v = "no (ability)"
        p95 = ctrl["null_p95"] if ctrl else "-"
        ap95 = abil["null_p95"] if abil else "-"
        print(f"  rule {rule:<9} mastery {sum(rates) / len(rates):>5.1%}  "
              f"{len(rel):>3} impl | diff p95 {str(p95):<4} | ability p95 {str(ap95):<4} "
              f"err={err:.3f}  {v}")

    # The sensitivity test. A relation present under one rule and absent under the others is a
    # property of the rule, and reporting it would be reporting our own modelling choice.
    surviving = [r for r in RULES
                 if per_rule[r].get("ability_control") and per_rule[r]["ability_control"]["survives"]]
    sets = [set(map(tuple, per_rule[r]["implications"])) for r in RULES]
    common = set.intersection(*sets) if all(sets) else set()
    union = set.union(*sets) if any(sets) else set()
    print(f"  -> survives BOTH controls under {len(surviving)}/3 rules"
          + (f" ({', '.join(surviving)})" if surviving else ""))
    print(f"     implications common to all three rules: {len(common)}/{len(union)} of the union")
    return {"field": field, "concepts": concepts, "learners": len(learners),
            "by_rule": per_rule, "rules_surviving": surviving,
            "common_implications": sorted(map(list, common)), "union_size": len(union)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=Path, default=None)
    ap.add_argument("--concept-problem", type=Path, default=None)
    ap.add_argument("--max-concepts", type=int, default=MAX_CONCEPTS)
    ap.add_argument("--min-learners", type=int, default=MIN_LEARNERS)
    ap.add_argument("--top-n", type=int, default=12)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "out" / "iita-concept-result.json")
    args = ap.parse_args()
    from mooccubex_iita import default_inputs
    default_inputs(args)

    print("=" * 78)
    print("CONCEPT-LEVEL IITA — lifting item structure through the Q-matrix")
    print("=" * 78)
    c2p, p2c, att = load(args.attempts, args.concept_problem)
    print(f"learners {len(att):,}   concepts {len(c2p):,}   problems {len(p2c):,}")

    cands = concept_sets(c2p, p2c, att, args.max_concepts, args.min_learners)
    if not cands:
        print("\nNo field yields 3+ concepts with disjoint problem sets and enough covering "
              "learners. Nothing to lift.")
        return
    print(f"\n{len(cands)} field(s) qualify. Analysing the top {min(args.top_n, len(cands))}.")
    print("Concept sets have DISJOINT problem sets — shared items would make two concept states")
    print("dependent by construction, which has nothing to do with learning.\n")

    results = [analyse(f, c, l, c2p, att) for f, c, l in cands[:args.top_n]]

    print("\n" + "=" * 78)
    print("SUMMARY")
    print("=" * 78)
    n = len(results)
    any_rule = sum(1 for r in results if r["rules_surviving"])
    all_rules = sum(1 for r in results if len(r["rules_surviving"]) == 3)

    def binom(k, n, p=0.05):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    print(f"{'field':<26} {'concepts':>8} {'learners':>8} {'rules surviving':>16}")
    for r in results:
        print(f"{r['field'][:26]:<26} {len(r['concepts']):>8} {r['learners']:>8} "
              f"{len(r['rules_surviving'])}/3")
    print(f"\n{any_rule}/{n} concept sets survive the difficulty control under at least one "
          f"mastery rule (binomial p = {binom(any_rule, n):.2e})")
    print(f"{all_rules}/{n} survive under ALL THREE rules — the figure to believe, since the other")
    print("  is partly a choice of rule rather than a property of the data.")

    out = args.out
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"sets": results, "any_rule": any_rule, "all_rules": all_rules,
                               "analysed": n}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
