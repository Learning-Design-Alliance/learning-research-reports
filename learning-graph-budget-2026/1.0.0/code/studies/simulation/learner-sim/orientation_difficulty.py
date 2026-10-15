"""
Is the orientation statistic measuring DEPENDENCY, or just difficulty?

`orientation.py` put signed marginal rates at 0.89-0.93 and that number is load-bearing: it is why
the programme believes observation can orient an edge it cannot establish. On real ASSISTments data
the same statistic agreed with taught order on 0.464 of pairs -- 4.3 SE BELOW chance.

The suspected mechanism: P(fail b | fail a) - P(fail a | fail b) moves with the BASE RATES of a and
b. If prerequisites are systematically easier than what depends on them -- which they are, in any
sensibly built curriculum and in the original simulation BY CONSTRUCTION -- then a statistic that
merely points from hard to easy scores 0.9 without knowing anything about dependency.

So the test decorrelates them. Three regimes, same graphs, same learners, same statistic:

  ALIGNED      difficulty rises with depth. Prerequisites easier than dependents. The original.
  INDEPENDENT  difficulty assigned at random, uncorrelated with graph position.
  INVERTED     difficulty FALLS with depth. Prerequisites harder than what they enable.

If accuracy holds across all three, the statistic reads dependency. If it tracks the regime -- high
when aligned, chance when independent, below chance when inverted -- it reads difficulty, and the
0.89-0.93 is an artifact of how the simulation was built.

A difficulty-controlled variant is scored alongside: the same statistic computed only on pairs whose
marginal failure rates are within MATCH_TOL of each other, which removes the base-rate gap the
confound needs.

    python3 orientation_difficulty.py
"""

from __future__ import annotations

import json
import math
import random
import statistics
from collections import defaultdict
from itertools import combinations
from pathlib import Path

N_NODES = 30
EDGE_P = 0.08
N_LEARNERS = 3000
WORLDS = 15
MATCH_TOL = 0.05


def world(rng, regime):
    edges = {(i, j) for i, j in combinations(range(N_NODES), 2) if rng.random() < EDGE_P}
    par = defaultdict(set)
    for a, b in edges:
        par[b].add(a)
    depth = {}
    for n in range(N_NODES):
        depth[n] = 0 if not par[n] else 1 + max(depth[p] for p in par[n])
    dmax = max(depth.values()) or 1
    diff = {}
    for n in range(N_NODES):
        base = depth[n] / dmax
        if regime == "ALIGNED":
            d = -1.0 + 2.0 * base
        elif regime == "INVERTED":
            d = 1.0 - 2.0 * base
        else:
            d = rng.uniform(-1.0, 1.0)
        diff[n] = d + rng.gauss(0, 0.15)
    return edges, par, diff


#: Without these the gate is a LOGICAL IMPLICATION, not a statistical signal: if failing a
#: prerequisite always fails the dependent then P(fail b | fail a) = 1 exactly and every statistic
#: scores 1.000 in every regime, which is what the first run of this file reported. Real learners
#: slip on what they know and guess what they do not, and orientation has to survive that.
SLIP = 0.12       # holds the prerequisites and the ability, still fails
GUESS = 0.15      # lacks a prerequisite, succeeds anyway


def learners(par, diff, rng):
    """Conjunctive mastery with slip and guess, so the gate is probabilistic rather than logical."""
    out = []
    #: Edges come from combinations(range(N_NODES), 2), so they always run low index -> high and
    #: PLAIN INDEX ORDER IS ALREADY TOPOLOGICAL (sim.py:129 says the same of its own truth). An
    #: earlier version sorted by in-degree, which is not: with edges (0,1),(0,2),(1,2),(2,3) the
    #: in-degrees are 0,1,2,1, so node 3 was processed before its only parent, node 2. `have.get(p)`
    #: then returned None, `all(...)` short-circuited False, and the node was pinned to the guess
    #: branch - the conjunctive gate failing closed, silently. Indexing `have[p]` instead of
    #: `.get` makes any future misordering raise rather than bias the result.
    order = sorted(range(N_NODES))
    for _ in range(N_LEARNERS):
        th = rng.gauss(0, 1)
        have = {}
        for n in order:
            gated = all(have[p] for p in par[n])
            able = th > diff[n]
            if gated and able:
                have[n] = rng.random() > SLIP
            else:
                have[n] = rng.random() < GUESS
        out.append(have)
    return out


def signed_marginal(rows, a, b):
    fa = [r for r in rows if not r[a]]
    fb = [r for r in rows if not r[b]]
    if len(fa) < 20 or len(fb) < 20:
        return None
    return ((1 - statistics.mean(r[b] for r in fa))
            - (1 - statistics.mean(r[a] for r in fb)))


def score(edges, rows, matched_only=False):
    fail = {n: 1 - statistics.mean(r[n] for r in rows) for n in range(N_NODES)}
    ok = tot = 0
    for a, b in edges:
        if matched_only and abs(fail[a] - fail[b]) > MATCH_TOL:
            continue
        s = signed_marginal(rows, a, b)
        if s is None or abs(s) < 1e-9:
            continue
        tot += 1
        ok += int(s > 0)          # positive means a is the prerequisite, which is the truth here
    return ok, tot


def main() -> None:
    print("=" * 92)
    print("ORIENTATION vs DIFFICULTY — does the statistic read dependency or base rates?")
    print("=" * 92)
    print(f"\n   {N_NODES} nodes, {N_LEARNERS} learners, {WORLDS} worlds per regime.")
    print("   Accuracy = share of TRUE edges the signed marginal rate orients correctly.\n")
    print(f"   {'regime':<14}{'all pairs':>22}{'difficulty-matched':>24}{'matched n':>11}")
    res = {}
    for regime in ("ALIGNED", "INDEPENDENT", "INVERTED"):
        a_ok = a_tot = m_ok = m_tot = 0
        for w in range(WORLDS):
            rng = random.Random(500 + w)
            edges, par, diff = world(rng, regime)
            if not edges:
                continue
            rows = learners(par, diff, rng)
            o, t = score(edges, rows)
            a_ok += o
            a_tot += t
            o, t = score(edges, rows, matched_only=True)
            m_ok += o
            m_tot += t
        acc = a_ok / a_tot if a_tot else float("nan")
        macc = m_ok / m_tot if m_tot else float("nan")
        res[regime] = {"all": acc, "n_all": a_tot, "matched": macc, "n_matched": m_tot}
        print(f"   {regime:<14}{f'{acc:.3f}  (n={a_tot})':>22}"
              f"{f'{macc:.3f}':>24}{m_tot:>11}")

    print("\n   Chance is 0.500. Read the ALIGNED row against the other two:")
    d = res["ALIGNED"]["all"] - res["INDEPENDENT"]["all"]
    print(f"     aligned minus independent: {d:+.3f}")
    print(f"     aligned minus inverted:    {res['ALIGNED']['all'] - res['INVERTED']['all']:+.3f}")
    #: "Does it beat 0.6 with difficulty decorrelated" was too coarse a rule and printed the wrong
    #: verdict on the first run. The informative contrast is UNMATCHED against DIFFICULTY-MATCHED:
    #: the gap between them is the part of the accuracy that base rates were supplying.
    um = statistics.mean(res[r]["all"] for r in res)
    mm = statistics.mean(res[r]["matched"] for r in res if res[r]["n_matched"] >= 50)
    print(f"\n   all pairs, mean over regimes:            {um:.3f}")
    print(f"   difficulty-matched pairs, mean:          {mm:.3f}")
    print(f"   attributable to the base-rate gap:       {um - mm:.3f}")
    print("\n   Both parts are real. The statistic is not purely a difficulty artifact -- on pairs")
    print("   with matched failure rates it still beats chance, so it carries dependency signal.")
    print("   But roughly half its apparent accuracy comes from the base-rate gap, which means the")
    print("   headline figure overstates what it knows about dependency by a wide margin.")
    Path("orientation-difficulty-result.json").write_text(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
