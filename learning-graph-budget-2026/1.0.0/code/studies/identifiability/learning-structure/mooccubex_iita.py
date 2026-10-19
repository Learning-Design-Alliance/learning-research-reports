"""
Induce prerequisite structure from real learner responses — the first time this pipeline sees one.

IITA has been validated only against DAKS's own generative model (`iita.py`, `surmise.py`). This
runs it on MOOCCubeX attempt logs, which makes it the first `induced` provenance in the corpus and
the other half of the comparison worth having: expert-asserted structure against
behaviour-implied structure, over the same concepts.

**The trap this is built around.** MOOCCubeX ships attempt LOGS, not test results. A learner who
worked items 1-3 and stopped has no record for items 4-10 — and if "no record" is read as
"incorrect", that learner looks exactly like someone who cannot do 4-10. Every such learner then
contributes a false counterexample-free pattern, and IITA duly infers that 1-3 are prerequisites of
everything. The structure would be entirely an artifact of dropout order.

So: **only learners who attempted every item in the set are used.** That is the one construction
where "not solved" means what IITA assumes it means. It costs most of the sample, which is the
correct price.

    python3 mooccubex_iita.py --top-n 20 [--attempts attempts.tsv] [--concept-problem concept-problem.txt]

Paper 1's figures are `--top-n 20` (out/iita-real-result.json); the default analyses 12 sets. The
inputs default to $MOOCCUBEX_DIR/attempts.tsv (data/ingest/mooccubex/stream_attempts.py) and
$MOOCCUBEX_DIR/concept-problem.txt.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path

from iita import corrected_iita

#: IITA's inductive generation walks nested quasi-orders, so cost climbs steeply in the item count.
#: Also a statistical bound: with more items, the number of learners who attempted ALL of them
#: collapses, and a quasi-order fitted on a handful of complete responders is noise.
MAX_ITEMS = 14
MIN_COMPLETE_LEARNERS = 60


def load_attempts(path: Path) -> dict[str, dict[str, int]]:
    """user -> {problem: best outcome}. A learner who ever got it right counts as solved."""
    out: dict[str, dict[str, int]] = defaultdict(dict)
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 3:
            continue
        user, prob, correct = parts[0], parts[1], parts[2]
        try:
            c = int(correct)
        except ValueError:
            continue
        # Repeated attempts on one problem: take the best. IITA's patterns are "what this person
        # can do", and a later success is evidence they can.
        out[user][prob] = max(out[user].get(prob, 0), 1 if c == 1 else 0)
    return out


def concept_groups(path: Path) -> dict[str, set[str]]:
    g: dict[str, set[str]] = defaultdict(set)
    for line in path.read_text(encoding="utf-8").splitlines():
        p = line.rstrip("\n").split("\t")
        if len(p) >= 2:
            g[p[0]].add(p[1])
    return g


def pick_item_sets(attempts, groups, max_items: int, min_learners: int):
    """Every concept whose problems yield an item set with enough COMPLETE responders, best first.

    Coherent = problems sharing a concept, so an inferred implication has a chance of meaning
    something. Ranked by complete-responder count, because that number — not the attempt count — is
    the effective N of everything downstream.

    Returns all viable sets rather than the best one: a single surviving case is an anecdote, and
    whichever set we happened to run first would decide the finding.
    """
    per_problem: dict[str, set[str]] = defaultdict(set)
    for user, probs in attempts.items():
        for p in probs:
            per_problem[p].add(user)

    out = []
    for concept, probs in groups.items():
        seen = [p for p in probs if p in per_problem]
        if len(seen) < 3:
            continue
        # Ties broken by id: `probs` is a set, so without it the pick depended on PYTHONHASHSEED.
        seen.sort(key=lambda p: (-len(per_problem[p]), p))
        items = seen[:max_items]
        complete = set.intersection(*(per_problem[p] for p in items)) if items else set()
        while len(items) > 3 and len(complete) < min_learners:
            items = items[:-1]
            complete = set.intersection(*(per_problem[p] for p in items))
        if len(items) >= 3 and len(complete) >= min_learners:
            out.append((concept, items, complete))
    return sorted(out, key=lambda t: (-len(t[2]), t[0]))


def coattendance_report(attempts, groups) -> None:
    """The landscape a refusal has to be read against.

    IITA needs many learners answering the SAME items. The binding quantity is therefore not the
    attempt count but co-attendance: how many learners attempted every item of some set. A mean
    attempts-per-problem hides this completely — a few heavily-worked problems and a long tail of
    singletons give the same mean as uniform sparsity and are worlds apart for this purpose.
    """
    per_problem: dict[str, set[str]] = defaultdict(set)
    for user, probs in attempts.items():
        for p in probs:
            per_problem[p].add(user)
    counts = sorted((len(v) for v in per_problem.values()), reverse=True)
    n = len(counts)
    print(f"\n  problems with any attempt: {n:,}")
    if not n:
        return
    print(f"  attempts per problem: median {counts[n // 2]}, "
          f"90th pct {counts[n // 10]}, max {counts[0]}")
    for thresh in (5, 10, 25, 50):
        print(f"    problems attempted by >= {thresh:>3} learners: "
              f"{sum(1 for c in counts if c >= thresh):,}")

    # The best pair is an upper bound on any larger set: adding items can only shrink the
    # intersection, so if no PAIR clears the floor no set of 3+ ever will.
    top = sorted(per_problem.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:60]
    best_pair, best_n = None, 0
    for i in range(len(top)):
        for j in range(i + 1, len(top)):
            shared = len(top[i][1] & top[j][1])
            if shared > best_n:
                best_pair, best_n = (top[i][0], top[j][0]), shared
    print(f"  best co-attended PAIR among the 60 most-attempted problems: {best_n} learners"
          + (f" ({best_pair[0]}, {best_pair[1]})" if best_pair else ""))
    print("    An upper bound on every larger set — intersections only shrink as items are added.")

    linked = {p for probs in groups.values() for p in probs}
    overlap = sum(1 for p, v in per_problem.items() if p in linked and len(v) >= 10)
    print(f"  concept-linked problems with >= 10 learners: {overlap:,}")
    print("    This is the quantity the expert-versus-behaviour comparison actually needs: a")
    print("    problem must be BOTH concept-linked (to reach the annotated prerequisites) AND")
    print("    well-attempted (to support induction). Neither alone is enough.")


N_NULL = 200
SEED = 20260912


def difficulty_null(solve_rates: list[float], n_learners: int, rng: random.Random) -> list[set[int]]:
    """Response patterns with the SAME item difficulties and NO dependency between items.

    The control this result needs, and the reason the more-solved-to-less-solved count is not one.
    A genuine prerequisite also runs from a more-solved item to a less-solved one — if A is required
    for B then more people have A — so 100% is what a real relation and a pure difficulty ordering
    both look like. The count cannot separate them.

    What separates them is whether IITA still finds implications once difficulties are held and
    dependencies removed. Each item is an independent Bernoulli at its observed solve rate, so
    anything the null recovers is an artifact of difficulty alone.
    """
    return [
        {i for i, r in enumerate(solve_rates) if rng.random() < r}
        for _ in range(n_learners)
    ]


def fixed_margins_null(patterns: list[set[int]], m: int, rng: random.Random) -> list[set[int]]:
    """Shuffle the learner x item matrix holding BOTH margins fixed.

    The control the difficulty null cannot be, and the one that matters most on learner data. The
    difficulty null resamples each item independently at its solve rate, which destroys any
    learner-ability factor — so a relation driven entirely by "some learners are better" sails
    through it. Ability alone produces exactly the Guttman-like pattern IITA reads as implication:
    a strong learner solves the hard item and the easy one, a weak learner neither, so
    counterexamples are rare with no dependency present.

    Holding row sums (items solved per learner — ability) and column sums (learners solving each
    item — difficulty) fixed leaves only the association between specific items. Checkerboard
    swaps on a 2x2 [[1,0],[0,1]] submatrix change neither margin.
    """
    mat = [[1 if i in pat else 0 for i in range(m)] for pat in patterns]
    n = len(mat)
    if n < 2 or m < 2:
        return patterns
    for _ in range(20 * n * m):
        r1, r2, c1, c2 = (rng.randrange(n), rng.randrange(n),
                          rng.randrange(m), rng.randrange(m))
        if r1 == r2 or c1 == c2:
            continue
        if mat[r1][c1] and not mat[r1][c2] and not mat[r2][c1] and mat[r2][c2]:
            mat[r1][c1], mat[r1][c2], mat[r2][c1], mat[r2][c2] = 0, 1, 1, 0
        elif not mat[r1][c1] and mat[r1][c2] and mat[r2][c1] and not mat[r2][c2]:
            mat[r1][c1], mat[r1][c2], mat[r2][c1], mat[r2][c2] = 1, 0, 0, 1
    return [{i for i in range(m) if row[i]} for row in mat]


def run_ability_control(patterns: list[set[int]], m: int, observed: int,
                        rng: random.Random) -> dict:
    sizes = []
    for _ in range(N_NULL):
        rel, _, _ = corrected_iita(fixed_margins_null(patterns, m, rng), m)
        sizes.append(len(rel))
    sizes.sort()
    return {"observed": observed, "null_mean": sum(sizes) / len(sizes),
            "null_p95": sizes[int(0.95 * len(sizes))],
            "survives": observed > sizes[int(0.95 * len(sizes))]}


def run_difficulty_control(patterns: list[set[int]], m: int, observed: int,
                           rng: random.Random) -> dict:
    solve = [sum(1 for p in patterns if i in p) / len(patterns) for i in range(m)]
    sizes = []
    for _ in range(N_NULL):
        rel, _, _ = corrected_iita(difficulty_null(solve, len(patterns), rng), m)
        sizes.append(len(rel))
    sizes.sort()
    return {"observed": observed, "null_mean": sum(sizes) / len(sizes),
            "null_p95": sizes[int(0.95 * len(sizes))], "null_max": sizes[-1],
            "survives": observed > sizes[int(0.95 * len(sizes))]}


def analyse_set(concept: str, items: list[str], complete: set[str], attempts) -> dict:
    print("-" * 74)
    print(f"concept {concept!r}")
    print(f"  {len(items)} items, {len(complete):,} complete responders "
          "(attempted EVERY item — see module docstring)")

    idx = {p: i for i, p in enumerate(items)}
    patterns = [{idx[p] for p in items if attempts[u].get(p) == 1} for u in sorted(complete)]
    solve = Counter()
    for pat in patterns:
        for i in pat:
            solve[i] += 1

    rel, diff, err = corrected_iita(patterns, len(items))
    print(f"  IITA: {len(rel)} implications, diff={diff:.4f}, estimated error rate={err:.4f}")

    ctrl = None
    if rel:
        consistent = sum(1 for a, b in rel if solve[a] >= solve[b])
        print(f"  {consistent}/{len(rel)} run more-solved -> less-solved "
              f"({consistent / len(rel):.0%}) — necessary, not sufficient: a genuine prerequisite")
        print("    runs the same way, since if A is required for B then more people have A.")

        rng = random.Random(SEED)
        ctrl = run_difficulty_control(patterns, len(items), len(rel), rng)
        print(f"  difficulty control (same difficulties, no dependencies, n={N_NULL}): "
              f"observed {ctrl['observed']} vs null mean {ctrl['null_mean']:.1f}, "
              f"p95 {ctrl['null_p95']}, max {ctrl['null_max']}")
        if ctrl["survives"]:
            abil = run_ability_control(patterns, len(items), len(rel), rng)
            ctrl["ability"] = abil
            print(f"  ability control (both margins fixed, n={N_NULL}): "
                  f"observed {abil['observed']} vs null mean {abil['null_mean']:.1f}, "
                  f"p95 {abil['null_p95']}  -> "
                  f"{'SURVIVES BOTH' if abil['survives'] else 'DIES: ability + difficulty'}")
            ctrl["survives"] = abil["survives"]
        if ctrl["survives"]:
            print("    -> SURVIVES. Note what that does not establish: the null removes ALL")
            print("       structure, so this says there is more than difficulty, not what it is.")
            # These problems have consecutive ids and belong to one exercise, so a relation that
            # merely tracked the order items are served in would survive the difficulty null too.
            if all("_" in i and i.split("_")[-1].isdigit() for i in items):
                num = {i: int(i.split("_")[-1]) for i in items}
                fwd = sum(1 for a, b in rel if num[items[a]] < num[items[b]])
                rate = fwd / len(rel)
                print(f"    presentation-order check: {fwd}/{len(rel)} follow ascending item id "
                      f"({rate:.0%})" + ("  ~chance, so not presentation sequence"
                                         if 0.35 <= rate <= 0.65
                                         else "  FAR FROM CHANCE — may be sequence, not dependency"))
        else:
            print("    -> does NOT survive: difficulty ordering, no dependency structure.")

    return {
        "concept": concept, "items": items, "complete_responders": len(complete),
        "implications": [[items[a], items[b]] for a, b in sorted(rel)],
        "diff": diff, "error_rate": err, "difficulty_control": ctrl,
        "solve_rates": {items[i]: solve[i] / len(patterns) for i in range(len(items))},
    }


def default_inputs(args) -> None:
    """--attempts and --concept-problem default to the files under $MOOCCUBEX_DIR."""
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from shared.paths import data_path
    args.attempts = args.attempts or data_path("MOOCCUBEX_DIR") / "attempts.tsv"
    args.concept_problem = args.concept_problem or data_path("MOOCCUBEX_DIR") / "concept-problem.txt"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=Path, default=None)
    ap.add_argument("--concept-problem", type=Path, default=None)
    ap.add_argument("--max-items", type=int, default=MAX_ITEMS)
    ap.add_argument("--min-learners", type=int, default=MIN_COMPLETE_LEARNERS)
    ap.add_argument("--top-n", type=int, default=12, help="how many item sets to analyse")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "out" / "iita-real-result.json")
    args = ap.parse_args()
    default_inputs(args)

    print("=" * 74)
    print("IITA ON REAL LEARNER RESPONSES (MOOCCubeX)")
    print("=" * 74)

    attempts = load_attempts(args.attempts)
    groups = concept_groups(args.concept_problem)
    print(f"learners with any attempt: {len(attempts):,}")
    print(f"concepts with linked problems: {len(groups):,}")
    coattendance_report(attempts, groups)

    picked = pick_item_sets(attempts, groups, args.max_items, args.min_learners)
    if not picked:
        print(f"\nNo concept yields 3+ problems with >= {args.min_learners} learners who "
              "attempted all of them. Nothing to infer; the landscape above says what is missing.")
        return

    print(f"\n{len(picked)} concept(s) clear the floor. Analysing the top "
          f"{min(args.top_n, len(picked))}.")
    print("A single surviving case is an anecdote; the rate across sets is the result.\n")
    results = [analyse_set(c, i, cm, attempts) for c, i, cm in picked[:args.top_n]]

    print("\n" + "=" * 74)
    print("SUMMARY ACROSS ITEM SETS")
    print("=" * 74)
    print(f"{'concept':<36} {'items':>5} {'N':>6} {'impl':>5} {'p95':>5} {'verdict':>10}")
    for r in results:
        c = r["difficulty_control"]
        print(f"{r['concept'][:36]:<36} {len(r['items']):>5} {r['complete_responders']:>6} "
              f"{len(r['implications']):>5} {(c['null_p95'] if c else 0):>5} "
              f"{('survives' if c and c['survives'] else 'no'):>10}")
    surv = sum(1 for r in results if r["difficulty_control"] and r["difficulty_control"]["survives"])

    def binom_tail(k: int, n: int, p: float = 0.05) -> float:
        """P(at least k survive by chance). Each control fires at its 95th percentile, so a set
        survives under the null with probability 0.05 — which is what makes a COUNT of surviving
        sets a testable quantity rather than a tally."""
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    both = 0
    for r in results:
        c = r["difficulty_control"]
        if not (c and c["survives"]) or not r["implications"]:
            continue
        items, imp = r["items"], r["implications"]
        if not all("_" in i and i.split("_")[-1].isdigit() for i in items):
            continue
        num = {i: int(i.split("_")[-1]) for i in items}
        rate = sum(1 for a, b in imp if num[a] < num[b]) / len(imp)
        if 0.35 <= rate <= 0.65:
            both += 1

    n = len(results)
    print(f"\n{surv}/{n} item sets carry structure beyond item difficulty "
          f"({n * 0.05:.1f} expected by chance, binomial p = {binom_tail(surv, n):.2e})")
    print(f"{both}/{n} survive BOTH controls, adding the presentation-order check "
          f"(binomial p = {binom_tail(both, n):.2e})")
    print("  The joint figure is conservative: the presentation-order check is a two-sided chance")
    print("  band, so it also rejects a relation running strongly AGAINST item order, which is not")
    print("  a sequence artifact.")
    if surv == 0:
        print("None survive: on this data IITA recovers difficulty ordering and nothing else.")
    elif surv < len(results):
        print("Mixed, which is the honest shape — some item sets carry dependency and some do not,")
        print("and a single-case report would have been decided by whichever ran first.")

    out = args.out
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"sets": results, "surviving": surv, "analysed": len(results)},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
