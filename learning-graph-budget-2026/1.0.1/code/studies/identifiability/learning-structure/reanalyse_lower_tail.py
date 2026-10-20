"""
Re-analyse the MOOCCubeX runs against the correct tail of the null.

**What was wrong.** Both real-data runs asked whether IITA's relation was LARGER than the
fixed-margins null produces. That is the wrong direction, and simulation says so unambiguously.

Pure ability with ordered difficulties yields a Guttman scale — a near-total order, in which almost
every pair is implied. A real prerequisite does the opposite: a learner who fails a gate then fails
everything downstream regardless of ability, producing patterns that violate orderings a Guttman
scale would never violate. So genuine structure yields FEWER surviving implications than ability
alone, not more.

Measured under ideal conditions (2000 learners, no slip, no guess), observed vs null median:

    two_chains    6  vs 17-18     LOW at every ability level
    fan           3  vs  9-21     LOW at every ability level
    flat         4-19 vs  4-19    sits on its null, as it must

So the test is the LOWER tail, and `flat` — pure ability — is the case that lands on the median.

This script re-scores the real data that way. It does not re-run the induction; it re-reads the
saved relations and re-draws the null.

    python3 reanalyse_lower_tail.py [--attempts attempts.tsv] [--concept-problem concept-problem.txt]

Inputs default as in mooccubex_iita.py; the result goes to out/lower-tail-reanalysis.json.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
import random

from iita import corrected_iita
from mooccubex_iita import concept_groups, default_inputs, load_attempts, pick_item_sets
from nulls import fixed_margin_draws

N_NULL = 200
SEED = 20260912
MAX_ITEMS = 14
MIN_LEARNERS = 60


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--attempts", type=Path, default=None)
    ap.add_argument("--concept-problem", type=Path, default=None)
    ap.add_argument("--top-n", type=int, default=20)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "out" / "lower-tail-reanalysis.json")
    args = ap.parse_args()
    default_inputs(args)
    rng = random.Random(SEED)

    print("=" * 78)
    print("RE-ANALYSIS AGAINST THE LOWER TAIL")
    print("=" * 78)
    print("Genuine dependency yields FEWER implications than ability alone, not more.")
    print("`below p5` is the signal; sitting on the null median is what pure ability looks like.\n")

    attempts = load_attempts(args.attempts)
    groups = concept_groups(args.concept_problem)
    picked = pick_item_sets(attempts, groups, MAX_ITEMS, MIN_LEARNERS)

    print(f"{'concept':<30} {'N':>5} {'obs':>4} {'p5':>4} {'med':>4} {'p95':>4}  verdict")
    rows, below = [], 0
    for concept, items, complete in picked[:args.top_n]:
        idx = {p: i for i, p in enumerate(items)}
        patterns = [{idx[p] for p in items if attempts[u].get(p) == 1} for u in sorted(complete)]
        rel, _, _ = corrected_iita(patterns, len(items))
        sizes = sorted(len(corrected_iita(d, len(items))[0])
                       for d in fixed_margin_draws(patterns, len(items), rng, N_NULL))
        p5, med, p95 = sizes[int(0.05 * N_NULL)], sizes[N_NULL // 2], sizes[int(0.95 * N_NULL)]
        is_below = len(rel) < p5
        below += is_below
        verdict = ("STRUCTURE (below p5)" if is_below
                   else "ability (on the null)" if p5 <= len(rel) <= p95
                   else "above p95 — denser than ability, not a dependency signature")
        print(f"{concept[:30]:<30} {len(complete):>5} {len(rel):>4} {p5:>4} {med:>4} {p95:>4}  "
              f"{verdict}")
        rows.append({"concept": concept, "n": len(complete), "observed": len(rel),
                     "p5": p5, "median": med, "p95": p95, "below_p5": is_below})

    n = len(rows)
    print(f"\n{below}/{n} item sets fall below the null's 5th percentile "
          f"({n * 0.05:.1f} expected by chance)")
    if below == 0:
        print("\nNo set shows the dependency signature. Combined with the earlier result — none")
        print("above the upper tail either — the reading is that these response patterns are")
        print("what learner ability and item difficulty alone produce.")
    out = args.out
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
