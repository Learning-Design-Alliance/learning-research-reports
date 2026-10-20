"""
Does orientation survive prerequisites that are soft rather than conjunctive?

`orientation_difficulty.py` put the signed marginal rate at **0.726 on difficulty-matched pairs**,
and that figure is why the programme believes observation can orient an edge it cannot establish.
It was measured under a conjunctive gate with slip and guess: lacking a prerequisite makes the
dependent capability fail except for a GUESS-sized escape.

That gate is exactly what the statistic feeds on. P(fail b | fail a) exceeds P(fail a | fail b)
because failing a *blocks* b. Under the model the programme has since moved to, a missing
prerequisite does not block anything — it raises the load, so the dependent capability is acquired
more slowly and ends weaker. The asymmetry the statistic depends on should weaken with it, and
possibly vanish.

So: the same graphs, the same three difficulty regimes, the same statistic, the same matched
control, across a range of prerequisite hardness.

    HARDNESS 1.0   the conjunctive gate of the original, reproduced
    HARDNESS 0.0   prerequisites affect load only — no gate at all
    in between     the dependent is gated with probability `hardness`, load-penalised otherwise

Pre-registered: if accuracy on difficulty-matched pairs decays towards chance as hardness falls,
then 0.726 is a property of conjunctive worlds and not of observation, and the programme's one
positive observational result is narrower than claimed. If it holds, orientation is robust to the
change of model and 0.726 stands.

    python3 orientation_soft.py
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "shared"))

import learner as LM                         # noqa: E402
import orientation_difficulty as od          # noqa: E402

HARDNESS = (1.0, 0.75, 0.5, 0.25, 0.0)
REGIMES = ("ALIGNED", "INDEPENDENT", "INVERTED")
WORLDS = 15
LESSON = 1.0
MODEL = LM.Model(gamma=1.0, binary=False, gate=False)


def learners(par, diff, hardness, rng):
    """The original generator with exactly one thing varied: what a MISSING prerequisite does.

    At hardness 1 a missing prerequisite blocks, which is `orientation_difficulty.learners`
    verbatim. Below 1 it may instead raise the effective difficulty, because in the shared model
    load enters as `elements ** gamma` inside an exponential in (difficulty - ability):

        exp(λ(d - θ)) × E**γ  =  exp(λ(d + γ·ln E / λ - θ))

    so a load of E elements IS a difficulty increase of γ·ln(E)/λ. The ability rule, the slip and
    the guess are untouched, so nothing but prerequisite hardness moves between arms."""
    out = []
    #: Edges come from combinations(range(N_NODES), 2), so they always run low index -> high and
    #: PLAIN INDEX ORDER IS ALREADY TOPOLOGICAL (sim.py:129 says the same of its own truth). An
    #: earlier version sorted by in-degree, which is not: with edges (0,1),(0,2),(1,2),(2,3) the
    #: in-degrees are 0,1,2,1, so node 3 was processed before its only parent, node 2. `have.get(p)`
    #: then returned None, `all(...)` short-circuited False, and the node was pinned to the guess
    #: branch - the conjunctive gate failing closed, silently. Indexing `have[p]` instead of
    #: `.get` makes any future misordering raise rather than bias the result.
    order = sorted(range(od.N_NODES))
    bump = MODEL.gamma / MODEL.lam
    for _ in range(od.N_LEARNERS):
        th = rng.gauss(0, 1)
        have = {}
        for n in order:
            missing = sum(1 for p in par[n] if not have[p])
            if missing and rng.random() < hardness:
                have[n] = rng.random() < od.GUESS            # blocked, as in the original
                continue
            eff = diff[n] + (bump * math.log(1 + missing) if missing else 0.0)
            have[n] = (rng.random() > od.SLIP) if th > eff else (rng.random() < od.GUESS)
        out.append(have)
    return out


def main() -> None:
    print("=" * 96)
    print(f"ORIENTATION UNDER SOFT PREREQUISITES — {WORLDS} worlds, "
          f"{od.N_LEARNERS} learners, matched tolerance {od.MATCH_TOL}")
    print("=" * 96)
    print("\n   hardness 1.0 is the conjunctive gate the 0.726 was measured under; 0.0 is")
    print("   prerequisites that only add load. Accuracy is on difficulty-MATCHED pairs, with")
    print("   the all-pairs figure alongside since the gap between them is the base-rate effect.\n")
    print(f"   {'regime':<13}{'hardness':>9}{'all pairs':>11}{'matched':>10}{'n matched':>11}")
    out = {}
    for regime in REGIMES:
        for hard in HARDNESS:
            ok_a = tot_a = ok_m = tot_m = 0
            for w in range(WORLDS):
                rng = random.Random(3300 + w)
                edges, par, diff = od.world(rng, regime)
                rows = learners(par, diff, hard, rng)
                a, b = od.score(edges, rows)
                c, d = od.score(edges, rows, matched_only=True)
                ok_a += a; tot_a += b; ok_m += c; tot_m += d
            acc_a = ok_a / tot_a if tot_a else float("nan")
            acc_m = ok_m / tot_m if tot_m else float("nan")
            out[f"{regime}/{hard}"] = {"all": acc_a, "matched": acc_m, "n_matched": tot_m}
            print(f"   {regime:<13}{hard:>9.2f}{acc_a:>11.3f}{acc_m:>10.3f}{tot_m:>11}")
        print()
    Path("orientation-soft-result.json").write_text(json.dumps(out, indent=2))
    print("   Chance is 0.500. A matched column that decays towards it as hardness falls means")
    print("   the 0.726 belongs to conjunctive worlds rather than to observation.")


if __name__ == "__main__":
    main()
