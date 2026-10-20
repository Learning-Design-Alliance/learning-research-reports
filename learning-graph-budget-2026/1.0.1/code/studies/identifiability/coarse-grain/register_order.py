"""Does the identifying cell exist at COURSE grain? A positivity census on MOOCCubeX enrolments.

`studies/identifiability/overlap/positivity.py` asks, for a KC pair A -> B, whether the corpus contains learners who reached
B WITHOUT holding A. Where that cell is empty the question is unanswerable, and `studies/identifiability/overlap/ATLAS.md`
records that most corpora fail it because a mastery tutor gates: it will not offer B until A is
passed, so the cell cannot exist.

NOBODY HAS ASKED THIS AT COURSE GRAIN. `studies/identifiability/coarse-grain/evpi_coarse.py` showed the decision to gate a
COURSE is worth resolving where a KC edge is not, because a multi-semester remediation chain has an
absorbing failure state. That makes course-grain prerequisites the ones worth measuring -- and the
first question about any corpus is whether it CAN measure them.

MOOCCubeX is the right shape for it. XuetangX enrolment is free choice: a learner picks courses in
whatever order they like, so nothing structurally removes the cell the way a tutor does. 3,330,294
learners, of whom 646,779 enrolled in at least two of the 887 courses that carry concept membership.

WHAT IS COUNTED, per ordered course pair (A, B):

    both_A_first   enrolled in both, A before B
    both_B_first   enrolled in both, B before A
    B_without_A    enrolled in B and NEVER in A        <- THE IDENTIFYING CELL

A gated curriculum drives `B_without_A` to zero. Free choice does not.

TWO READINGS, AND ONLY THE FIRST IS CLEAN.

  POSITIVITY is a census. It needs no null: either the learners are there or they are not, and the
  count is the answer. This is the reading the study exists for.

  ORDER ASYMMETRY -- the share of co-enrollers taking A first -- is reported as a DIAGNOSTIC ONLY,
  never as evidence of a prerequisite, because it carries a confound this corpus cannot remove:
  COURSE AVAILABILITY. If A was published before B, every learner takes A first whatever the
  relation between them, and the asymmetry measures the platform's release schedule. Enrolment
  timestamps are present, so the first-enrolment date of each course is reported beside the
  asymmetry and any pair whose courses do not overlap in time is flagged. That is mitigation, not a
  fix; the honest use of the asymmetry is to generate candidates, not to score them.

PRE-REGISTERED VERDICTS, written before the run:

  POSITIVITY HOLDS AT COURSE GRAIN   at least 100 course pairs have all three cells above the floor.
                                     Course-grain prerequisite questions are ANSWERABLE on free-choice
                                     enrolment data, which no corpus in `studies/identifiability/overlap/ATLAS.md` manages.
  IDENTIFYING CELL EMPTY             fewer. Even free enrolment does not supply the cell, and the
                                     coarse-grain question needs a different design.

Reads MOOCCubeX enrolment order. PRIVACY: the ingest (`stream_user.py`) discards `name`, `gender`,
`year_of_birth` and `school` at the door -- they are not needed for any question here, and the way to
not misuse an attribute is to not hold it. Only the pseudonymous id, course sequence and enrolment
times are kept, and only aggregates are committed.

    python3 register_order.py [--top 60]

DIRECTION: symmetric -- the positivity census scores every ordered course pair and needs both orders
present; the order asymmetry is |2p - 1| on one orientation per pair, and the opened-first agreement
is unchanged by swapping a pair.

Direction declaration added 2026-09-24 (reversed-arrow rule, shared/experimental-contract.md):
nothing reported depends on edge orientation, so no reversed-arrow control applies.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SEED = 20260922
SCRATCH = Path("/tmp/claude-0/-home-user-learning-engine-ai-frontend/"
               "95e45190-f913-5b1d-89d5-0a9410ca02ad/scratchpad/mooccubex")
#: a cell must hold this many learners to count as occupied
MIN_CELL = 30
#: pairs needed before course-grain positivity is called answerable
READABLE_AT = 100


def load(path, top):
    """learner -> ordered course list, restricted to the `top` most-enrolled courses."""
    pop = Counter()
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                d = json.loads(line)
            except Exception:
                continue
            rows.append((d["c"], d["t"]))
            pop.update(set(d["c"]))
    keep = {c for c, _ in pop.most_common(top)}
    out = []
    first_seen = {}
    for courses, times in rows:
        pairs = [(c, t) for c, t in zip(courses, times) if c in keep]
        for c, t in pairs:
            if c not in first_seen or t < first_seen[c]:
                first_seen[c] = t
        if pairs:
            out.append(pairs)
    return out, keep, pop, first_seen


def census(seqs, keep, first_seen):
    """Per ordered pair: co-enrolment order, and the identifying cell B-without-A."""
    took = defaultdict(set)
    order = defaultdict(lambda: [0, 0])          # (a,b) unordered -> [a_first, b_first]
    for i, pairs in enumerate(seqs):
        pos = {}
        for c, t in pairs:
            if c not in pos or t < pos[c]:
                pos[c] = t
        for c in pos:
            took[c].add(i)
        for x, y in itertools.combinations(sorted(pos), 2):
            if pos[x] == pos[y]:
                continue
            order[(x, y)][0 if pos[x] < pos[y] else 1] += 1

    rows = []
    for a, b in itertools.permutations(sorted(keep), 2):
        key = (a, b) if a < b else (b, a)
        if key not in order:
            continue
        af, bf = order[key] if a < key[1] or a == key[0] else order[key][::-1]
        both = af + bf
        b_without_a = len(took[b] - took[a])
        if both < MIN_CELL:
            continue
        rows.append(dict(a=a, b=b, both=both, a_first=af, b_first=bf,
                         b_without_a=b_without_a,
                         a_first_share=af / max(both, 1),
                         cell_ok=bool(af >= MIN_CELL and bf >= MIN_CELL
                                      and b_without_a >= MIN_CELL),
                         a_opened=first_seen.get(a, ""), b_opened=first_seen.get(b, ""),
                         # the confound: if A opened first, order says nothing about dependence
                         a_opened_first=bool(first_seen.get(a, "") < first_seen.get(b, ""))))
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=60)
    ap.add_argument("--src", default=str(SCRATCH / "user-order.jsonl"))
    ap.add_argument("--out", default="out/register_order.json")
    args = ap.parse_args()

    print("COURSE-GRAIN POSITIVITY -- does the identifying cell exist when enrolment is free?\n")
    seqs, keep, pop, first_seen = load(args.src, args.top)
    print(f"{len(seqs):,} learners with >=2 of the top {len(keep)} courses "
          f"(median {int(np.median([len(s) for s in seqs]))} courses each)")

    rows = census(seqs, keep, first_seen)
    ok = [r for r in rows if r["cell_ok"]]
    print(f"{len(rows):,} ordered course pairs with >= {MIN_CELL} co-enrollers")
    print(f"{len(ok):,} have ALL THREE cells occupied "
          f"(A-first, B-first, and B-without-A) at >= {MIN_CELL}\n")

    if rows:
        bw = np.array([r["b_without_a"] for r in rows])
        print(f"  identifying cell (B without A): median {int(np.median(bw)):,} learners, "
              f"{100*np.mean(bw >= MIN_CELL):.1f}% of pairs above the floor")
        # EVERY UNORDERED PAIR APPEARS TWICE, as (a,b) and (b,a), and their A-first shares are
        # complements. The median of a set containing both p and 1-p is 0.500 BY CONSTRUCTION -- the
        # first version reported exactly that and it said nothing. Report the ABSOLUTE asymmetry on
        # one orientation per pair instead: 0 = free order, 1 = every learner takes the same one first.
        uniq = {tuple(sorted((r["a"], r["b"]))): r for r in ok}
        asym = np.array([abs(2 * r["a_first_share"] - 1) for r in uniq.values()])
        print(f"  order asymmetry, one orientation per pair ({len(uniq):,} pairs): "
              f"median |2p-1| = {np.median(asym):.3f}   (0 = free order, 1 = always same first)")
        print(f"    share of pairs above 0.20 asymmetry: {100*np.mean(asym > 0.20):.1f}%,  "
              f"above 0.50: {100*np.mean(asym > 0.50):.1f}%   [DIAGNOSTIC ONLY]")
        conf = sum(1 for r in ok if r["a_opened_first"] == (r["a_first_share"] > 0.5))
        print(f"  ...and {conf} of {len(ok)} agree with WHICH COURSE OPENED FIRST "
              f"({100*conf/max(len(ok),1):.0f}%), which is the confound this corpus cannot remove")

    verdict = ("POSITIVITY HOLDS AT COURSE GRAIN" if len(ok) >= READABLE_AT
               else "IDENTIFYING CELL EMPTY")
    print(f"\nVERDICT: {verdict}")
    if len(ok) >= READABLE_AT:
        print(f"  {len(ok):,} course pairs can be read against a bar of {READABLE_AT}. No corpus in")
        print("  overlap/ATLAS.md supplies this at KC grain on a gated platform; free enrolment does")
        print("  at COURSE grain, which is where evpi_coarse.py says the decision is worth resolving.")
        print("  WHAT IS STILL MISSING is the OUTCOME. This establishes the cell exists, not that")
        print("  taking A helps with B -- that needs performance on B's problems, which lives in")
        print("  MOOCCubeX's 21 GB user-problem.json and is the next fetch.")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, top=args.top, min_cell=MIN_CELL,
                                   learners=len(seqs), n_pairs=len(rows), n_readable=len(ok),
                                   verdict=verdict, rows=rows[:500]), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
