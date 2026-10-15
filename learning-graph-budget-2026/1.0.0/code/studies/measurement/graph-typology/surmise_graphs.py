"""EXPLORATORY: surmise relations induced from learner responses, as a family for signatures.py.

The typology so far compares graphs people authored or annotated. A surmise relation is the one
structure read off learners rather than off experts: IITA over mastery patterns. It is known to be
mostly ability and difficulty on this programme's data (studies/identifiability/learning-structure/RESULTS-IITA-REAL.md), so
each observed graph gets a twin induced from the same learners after checkerboard swaps that hold
both margins fixed. If surmise graphs have a shape of their own, it has to differ from the twin's;
if observed and twin match, the shape is what ability plus difficulty draws.

SKILL SETS  per dataset, up to SETS disjoint sets of K skills, built greedily: seed with the most
            covered unused skill, add the skill that keeps the most learners covering every skill in
            the set, stop at K or when fewer than MIN_LEARNERS remain. Items tagged to more than one
            skill are dropped, so no two skill states share evidence.
MASTERY     majority of a learner's attempts on the skill correct (the middle of the three rules in
            mooccubex_concept_iita.py).
IITA        corrected IITA (studies/identifiability/learning-structure/iita.py); an implication (a, b) reads "b mastered
            implies a mastered", so a is written as the prerequisite.
TWINS       NULL_REPS fixed-margin shuffles per set; replicate 0 enters the typology.
DATASETS    XES3G5M (Chinese primary maths, leaf KCs), ASSISTments 2012-13 (skill builders).

    python3 surmise_graphs.py [--k 15] [--out out/surmise_graphs.json]
"""

from __future__ import annotations

import collections
import csv
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "studies/identifiability/learning-structure"))
from iita import corrected_iita  # noqa: E402
from mooccubex_concept_iita import fixed_margins_null  # noqa: E402

sys.path.insert(0, str(ROOT))
from shared.paths import data_path  # noqa: E402
SEED = 20260924
SETS, MIN_LEARNERS, NULL_REPS, MAX_LEARNERS = 8, 200, 5, 3000


def xes3g5m():
    for line in open(data_path("XES_DIR") / "attempts.tsv"):
        u, q, c, ok, _ = line.rstrip("\n").split("\t")
        yield u, q, c, int(ok)


def assist12():
    with open(data_path("ASSIST_DIR") / "assist_slim.csv") as f:
        for r in csv.DictReader(f):
            if r["skill_id"]:
                yield r["user_id"], r["problem_id"], r["skill_id"], int(float(r["correct"]) >= 1)


def mastery(rows):
    tags = collections.defaultdict(set)
    rows = list(rows)
    for _, q, c, _ in rows:
        tags[q].add(c)
    tally = collections.defaultdict(lambda: [0, 0])      # (user, skill) -> [correct, attempts]
    for u, q, c, ok in rows:
        if len(tags[q]) == 1:
            t = tally[(u, c)]; t[0] += ok; t[1] += 1
    state = collections.defaultdict(dict)
    for (u, c), (k, n) in tally.items():
        state[c][u] = k / n >= 0.5
    return state


def skill_sets(state, k, rng):
    users = {c: set(v) for c, v in state.items() if len(v) >= MIN_LEARNERS}
    used, sets = set(), []
    while len(sets) < SETS:
        pool = [c for c in users if c not in used]
        if not pool:
            break
        seed = max(pool, key=lambda c: (len(users[c]), c))
        chosen, cover = [seed], set(users[seed])
        while len(chosen) < k:
            best = max((c for c in pool if c not in chosen), key=lambda c: (len(cover & users[c]), c), default=None)
            if best is None or len(cover & users[best]) < MIN_LEARNERS:
                break
            chosen.append(best); cover &= users[best]
        used |= set(chosen)
        if len(chosen) >= 5:
            learners = sorted(cover)
            if len(learners) > MAX_LEARNERS:          # IITA cost grows with learners; a seeded subsample
                learners = sorted(rng.sample(learners, MAX_LEARNERS))
            sets.append((chosen, learners))
    return sets


def induce(patterns, skills):
    rel, _, err = corrected_iita(patterns, len(skills))
    return [[skills[a], skills[b]] for a, b in sorted(rel) if a != b], err


def main() -> None:
    k = int(sys.argv[sys.argv.index("--k") + 1]) if "--k" in sys.argv else 15
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else HERE / "out" / "surmise_graphs.json"
    rng = random.Random(SEED)
    res = []
    for name, loader in (("xes3g5m", xes3g5m), ("assist12", assist12)):
        state = mastery(loader())
        for i, (skills, learners) in enumerate(skill_sets(state, k, rng)):
            pats = [{j for j, c in enumerate(skills) if state[c][u]} for u in learners]
            edges, err = induce(pats, skills)
            twins = [induce(fixed_margins_null(pats, len(skills), rng), skills) for _ in range(NULL_REPS)]
            rate = sum(len(p) for p in pats) / (len(pats) * len(skills))
            res.append(dict(graph=f"{name}-set{i}", dataset=name, skills=skills, learners=len(learners),
                            mastery_rate=rate, edges=edges, error_rate=err,
                            null_edges=[t[0] for t in twins], null_error_rates=[t[1] for t in twins]))
            print(f"  {name}-set{i}: {len(skills)} skills, {len(learners)} learners, mastery {rate:.0%}, "
                  f"{len(edges)} implications (twins {[len(t[0]) for t in twins]})", flush=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(exploratory=True, seed=SEED, k=k, rule="majority", graphs=res), indent=1) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
