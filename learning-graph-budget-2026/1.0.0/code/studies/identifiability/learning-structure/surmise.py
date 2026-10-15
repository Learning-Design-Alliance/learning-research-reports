"""
Validation harness for prerequisite inference: a simulator, a scorer, and the confound test.

**The estimator here is corrected IITA** (`iita.py`, a port of DAKS). It replaced a home-grown
pairwise estimator that looked good on this simulator and found *nothing* in three of four regimes
on DAKS's own model — see `IITA-COMPARISON.md`. The superseded estimator survives only as
`infer_legacy_pairwise`, used by the comparison and marked accordingly; it must not be used on real
data.

What this module contributes that DAKS does not:

1. **The curriculum-order confound test.** If a tutor always teaches A before B, "B without A" is
   rare because nobody was ever OFFERED B first — not because it is impossible. Every counting
   estimator reads that as a prerequisite, IITA included, and nothing in DAKS checks for it. It is
   the missing-is-not-negative rule from the evaluation contract, in a new place.
2. **A harder simulator than BLIM.** Per-KC difficulty, per-learner aptitude, repeated practice, and
   a finite opportunity budget. IITA's precision falls from ~1.00 on BLIM to ~0.52 here, which is
   worth knowing before trusting it on real tutor data where item difficulty certainly varies.
3. **The error-rate diagnostic, surfaced.** IITA estimates one error rate per candidate quasi-order.
   Where it fits well that estimate lands within 0.01-0.03 of the truth; where it fails badly it
   reported 0.295 against a true 0.1. On real data, where there is no ground truth, an implausible
   recovered error rate means the fitted relation does not describe the data.

    python3 experiments/learning-structure/surmise.py selftest
"""

from __future__ import annotations

import argparse
import json
import random
from dataclasses import dataclass
from pathlib import Path

from iita import as_patterns, corrected_iita

#: Too few learners mastering the consequent and any rate is noise. Used only by the legacy
#: estimator; IITA has no equivalent knob, which is part of why it is the better tool.
MIN_SUPPORT = 10


@dataclass
class Mastery:
    """Who mastered what. The only input the inference needs."""
    learners: list[str]
    kcs: list[str]
    mastered: dict[str, set[str]]

    def rate(self, kc: str) -> float:
        return sum(1 for l in self.learners if kc in self.mastered[l]) / len(self.learners)


def infer(m: Mastery) -> tuple[list[dict], float, float]:
    """Prerequisite relation by corrected IITA. Returns (edges, diff value, estimated error rate).

    The error rate is returned rather than hidden because it is the only validity signal available
    on real data: see the module docstring.
    """
    patterns, kcs = as_patterns(m)
    rel, diff, err = corrected_iita(patterns, len(kcs))
    edges = [{"prereq": kcs[i], "of": kcs[j]} for i, j in rel]
    return edges, diff, err


def infer_legacy_pairwise(m: Mastery, min_asymmetry: float = 2.0) -> list[dict]:
    """SUPERSEDED. The original pairwise estimator, kept only so the comparison can be re-run.

    Scores each ordered pair against an independence baseline and keeps the asymmetric ones. It
    finds nothing whenever the true relation is transitively closed, because a closed relation is
    full of mutually-implied pairs whose asymmetry is ~1 by construction. Do not use it on real
    data; `IITA-COMPARISON.md` records the numbers.
    """
    import itertools

    n = len(m.learners)
    out = []
    for a, b in itertools.permutations(m.kcs, 2):
        viol = sum(1 for l in m.learners if b in m.mastered[l] and a not in m.mastered[l])
        support = sum(1 for l in m.learners if b in m.mastered[l])
        exp = n * m.rate(b) * (1 - m.rate(a))
        rev_exp = n * m.rate(a) * (1 - m.rate(b))
        if exp <= 0 or rev_exp <= 0 or support < MIN_SUPPORT:
            continue
        fwd = viol / exp
        rev = sum(1 for l in m.learners if a in m.mastered[l] and b not in m.mastered[l]) / rev_exp
        if fwd > 0 and rev / fwd >= min_asymmetry:
            out.append({"prereq": a, "of": b})
    return out


# ── simulator ───────────────────────────────────────────────────────────────────────────────────
def simulate(
    rng: random.Random,
    n_learners: int = 300,
    n_kcs: int = 10,
    edge_prob: float = 0.25,
    curriculum_order: bool = False,
    slip: float = 0.05,
    guess: float = 0.05,
    scramble: bool = False,
    rounds: int = 6,
    budget_range: tuple[int, int] = (12, 60),
) -> tuple[Mastery, set[tuple[str, str]]]:
    """Learners work through KCs; a KC can only be mastered once its prerequisites are.

    Harder than DAKS's basic local independence model in three ways that matter on real data:
    difficulty varies by KC, practice is repeated, and opportunity is finite.

    `curriculum_order=True` delivers KCs in a fixed order for every learner — the confound.
    `scramble=True` makes that fixed order NOT follow the true dependencies, which is the case where
    ordering and structure actively disagree.
    """
    kcs = [f"kc{i:02d}" for i in range(n_kcs)]
    truth = {
        (kcs[i], kcs[j])
        for i in range(n_kcs) for j in range(i + 1, n_kcs)
        if rng.random() < edge_prob
    }
    prereqs: dict[str, set[str]] = {k: set() for k in kcs}
    for a, b in truth:
        prereqs[b].add(a)

    # Per-KC difficulty. A single per-learner aptitude makes mastery nearly all-or-nothing, every
    # pair look symmetric, and no prerequisite signal exist.
    difficulty = {k: 0.3 * rng.betavariate(2, 2) for k in kcs}

    # A real curriculum need not follow the true dependency structure.
    fixed_order = rng.sample(kcs, len(kcs)) if scramble else list(kcs)

    mastered: dict[str, set[str]] = {}
    for i in range(n_learners):
        learner = f"s{i:04d}"
        got: set[str] = set()
        order = fixed_order if curriculum_order else rng.sample(kcs, len(kcs))
        aptitude = rng.betavariate(5, 3)
        # A finite budget is the MECHANISM of the confound. With unlimited opportunities every
        # learner attempts every KC in every round, a fixed order restricts nobody, and the confound
        # cannot appear at all.
        budget, spent = rng.randint(*budget_range), 0
        for _ in range(rounds):
            for kc in order:
                if spent >= budget:
                    break
                if kc in got:
                    continue
                spent += 1
                ready = prereqs[kc] <= got
                # Not ready: only a guess succeeds. That is what makes a genuine prerequisite's
                # violation rate low rather than exactly zero, as in real data.
                p = (aptitude * (1 - difficulty[kc]) * (1 - slip)) if ready else guess
                if rng.random() < p:
                    got.add(kc)
        mastered[learner] = got
    return Mastery([f"s{i:04d}" for i in range(n_learners)], kcs, mastered), truth


# ── scoring ─────────────────────────────────────────────────────────────────────────────────────
def transitive_closure(edges: set[tuple[str, str]], kcs: list[str]) -> set[tuple[str, str]]:
    closure = set(edges)
    for _ in range(len(kcs)):
        grown = closure | {(a, d) for a, b in closure for c, d in closure if b == c}
        if grown == closure:
            break
        closure = grown
    return closure


def transitive_reduction(edges: set[tuple[str, str]], kcs: list[str]) -> set[tuple[str, str]]:
    closure = transitive_closure(edges, kcs)
    return {
        (a, b) for a, b in edges
        if not any((a, c) in closure and (c, b) in closure for c in kcs if c not in (a, b))
    }


def score(found: list[dict], truth: set[tuple[str, str]], kcs: list[str]) -> dict:
    """Scored against the transitive CLOSURE, which is what these methods estimate.

    IITA returns a quasi-order by construction. If A->B and B->C are true then A->C is a correct
    consequence of the truth, and counting it as a false positive understates the method by design.
    Minimal-DAG recovery after transitive reduction is reported alongside, because that is what a
    curriculum designer would actually draw — and the Dowling data shows experts agree on it far
    less (`CEILING.md`).
    """
    got = {(r["prereq"], r["of"]) for r in found}
    closure = transitive_closure(truth, kcs)
    reduced = transitive_reduction(got, kcs)
    return {
        "true_edges": len(truth), "closure_edges": len(closure), "found": len(got),
        "precision_closure": len(got & closure) / len(got) if got else 0.0,
        "recall_closure": len(got & closure) / len(closure) if closure else 0.0,
        "spurious": len(got - closure),
        "reduced_found": len(reduced),
        "reduced_precision": len(reduced & truth) / len(reduced) if reduced else 0.0,
        "reduced_recall": len(reduced & truth) / len(truth) if truth else 0.0,
    }


def selftest(args) -> int:
    print("Corrected IITA against a KNOWN prerequisite DAG, and what curriculum order does to it.")
    print(f"{args.learners} learners · {args.kcs} KCs · slip {args.slip} · guess {args.guess}")
    print("scored against the transitive closure; minimal-DAG recovery shown alongside\n")
    print(f"  {'delivery order':24} {'closure':>8} {'found':>6} {'prec':>6} {'rec':>5} "
          f"{'spurious':>11}  {'minDAG p/r':>11}  {'err rate':>9}")

    # Averaged over SEEDS, not one run. A single run declared the confound confirmed on a
    # difference of one spurious edge (21 vs 22), which is noise — the arms differ by less than
    # run-to-run variance. A confound worth reporting has to survive repetition.
    import statistics

    arms = (
        ("randomised per learner", False, False),
        ("fixed curriculum order", True, False),
        ("fixed, NOT matching DAG", True, True),
    )
    results: dict[str, dict] = {}
    per_seed: dict[str, list[int]] = {}
    for label, curriculum, scram in arms:
        runs = []
        for r in range(args.repeats):
            m, truth = simulate(random.Random(args.seed + 1000 * r), args.learners, args.kcs,
                                args.edge_prob, curriculum, args.slip, args.guess, scram,
                            budget_range=tuple(args.budget))
            edges, _diff, err = infer(m)
            sc = score(edges, truth, m.kcs)
            sc["error_rate"] = err
            runs.append(sc)
        agg = {k: statistics.mean(r[k] for r in runs) for k in runs[0]}
        agg["spurious_sd"] = statistics.stdev(r["spurious"] for r in runs) if len(runs) > 1 else 0.0
        results[label] = agg
        per_seed[label] = [r["spurious"] for r in runs]
        print(f"  {label:24} {agg['closure_edges']:8.1f} {agg['found']:6.1f} "
              f"{agg['precision_closure']:6.2f} {agg['recall_closure']:5.2f} "
              f"{agg['spurious']:6.1f}±{agg['spurious_sd']:<4.1f}  "
              f"{agg['reduced_precision']:.2f}/{agg['reduced_recall']:.2f}  {agg['error_rate']:9.3f}")

    rnd = results["randomised per learner"]
    print()
    print(f"Under randomised delivery: precision {rnd['precision_closure']:.2f}, recall "
          f"{rnd['recall_closure']:.2f} on the closure, over {args.repeats} seeds.")
    print(f"Minimal-DAG recovery is much weaker ({rnd['reduced_precision']:.2f}/"
          f"{rnd['reduced_recall']:.2f}) — expected, and it mirrors the Dowling finding that")
    print("experts themselves agree on reachability far more than on the immediate-prerequisite DAG.")

    # PAIRED by seed. The arms share a seed, so the same true DAG and the same learner aptitudes
    # are used in each — comparing group means against a standard deviation is both wasteful and
    # wrong, because that SD is inflated BY the effect: at a tight budget the randomised arm sits at
    # 1.2±0.7 spurious while the fixed arm swings 10.1±12.0, which is an intermittent real effect,
    # not noise. A sign test over paired seeds is the right instrument for a skewed difference.
    print()
    print(f"  {'comparison':34} {'median Δ spurious':>18} {'seeds worse':>13}")
    verdicts = []
    for label in ("fixed curriculum order", "fixed, NOT matching DAG"):
        diffs = [f - r for f, r in zip(per_seed[label], per_seed["randomised per learner"])]
        worse = sum(1 for d in diffs if d > 0)
        med = statistics.median(diffs)
        verdicts.append((label, med, worse, len(diffs)))
        print(f"  {label + ' vs randomised':34} {med:+18.1f} {worse:>8}/{len(diffs)}")

    print()
    # Sign test: under the null that delivery order does not matter, the number of seeds where the
    # fixed arm is worse is Binomial(n, 0.5).
    strong = [v for v in verdicts if v[2] >= 0.75 * v[3] and v[1] > 0]
    if strong:
        label, med, worse, n = max(strong, key=lambda v: v[1])
        print(f"CONFOUND CONFIRMED: `{label}` is worse on {worse} of {n} paired seeds, median")
        print(f"{med:+.1f} spurious edges. A KC always taught late looks dependent on everything")
        print("taught earlier, because nobody was ever offered it first — the statistic reads")
        print("impossibility where there was only absence of opportunity.")
        print()
        print("It is INTERMITTENT: on some seeds the fixed order costs nothing, on others it")
        print("dominates the result. That is worse than a steady bias, because a single run cannot")
        print("tell you which case you are in.")
        print()
        print("For real data: a prerequisite graph from a fixed-sequence tutor is substantially a")
        print("picture of the CURRICULUM. Use randomised problem order, or restrict to KC pairs")
        print("whose delivery order actually varies across learners.")
    else:
        print("CONFOUND NOT DEMONSTRATED at this configuration: no fixed-order arm is consistently")
        print("worse across paired seeds. Reported as a null rather than argued away — but note")
        print("the mechanism needs a TIGHT opportunity budget to bite (try --budget 6 14). With a")
        print("generous budget every learner reaches every KC whatever the order, so delivery order")
        print("restricts nobody and there is nothing for the confound to exploit.")

    print()
    print(f"ERROR-RATE DIAGNOSTIC. IITA estimated {rnd['error_rate']:.3f}; the simulated slip is "
          f"{args.slip}.")
    if rnd["error_rate"] > 2 * args.slip:
        print("  The estimate is well above the true slip, and precision on this simulator is")
        print(f"  {rnd['precision_closure']:.2f} — so the diagnostic is WORKING: it flags a poor fit")
        print("  that the edge list alone would not reveal. IITA's model assumes one global error")
        print("  rate, and this simulator gives every KC its own difficulty, which is exactly the")
        print("  assumption violation the inflated estimate is reporting.")
    else:
        print("  The estimate is close to the true slip, consistent with a well-fitting relation.")
    print("  This is the only validity signal available on real data, where there is no ground")
    print("  truth. On DAKS's own model IITA lands within 0.01-0.03 of the truth when it fits well")
    print("  and reported 0.295 against a true 0.1 when it failed badly.")

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=2) + "\n")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("selftest", help="recover a known DAG; demonstrate the curriculum confound")
    t.add_argument("--learners", type=int, default=800)
    t.add_argument("--kcs", type=int, default=10)
    t.add_argument("--edge-prob", type=float, default=0.25)
    t.add_argument("--slip", type=float, default=0.05)
    t.add_argument("--guess", type=float, default=0.05)
    t.add_argument("--seed", type=int, default=20260912)
    t.add_argument("--budget", type=int, nargs=2, default=[12, 60], metavar=("MIN", "MAX"),
                   help="opportunity budget per learner. A TIGHT budget is what makes delivery "
                        "order bite: most learners never reach the late KCs at all.")
    t.add_argument("--repeats", type=int, default=8,
                   help="seeds per arm; one run cannot separate a confound from noise")
    t.add_argument("--json", type=Path)
    t.set_defaults(func=selftest)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
