"""
How complete is this graph? Capture-recapture on multiple proposers — and what our correlation costs.

`FLARE-FOCUS.md` showed the flare-or-focus decision turns almost entirely on the omission rate: flare
wins above roughly 40% omitted and loses badly below it. So a triage step that picks between them
needs to ESTIMATE completeness without ground truth, and that is a species-richness problem —
several observers each produce a partial list, and the overlap between them says how much nobody saw.

**Chao2**, the incidence-based estimator, is the standard tool:

    S_est = S_obs + ((k-1)/k) * Q1^2 / (2*Q2)

where Q1 is the number of edges exactly one proposer found and Q2 the number exactly two found. A
large Q1 relative to Q2 means the proposers keep turning up things the others missed, which implies
plenty still unseen.

**Its assumption is independent observers, and ours are anything but.** Measured AI-to-AI agreement
is kappa 0.72-0.84 within a model and 0.44-0.53 across vendors. Correlated proposers miss the *same*
edges, which deflates Q1, which makes the estimator report a graph as more complete than it is — the
error runs in the dangerous direction, because it would route a badly incomplete graph to `focus`
when it needed `flare`.

This measures that bias against known truth instead of assuming it away.

    python3 completeness.py
"""

from __future__ import annotations

import json
import random
import statistics
from collections import Counter
from pathlib import Path

TRUE_EDGES = 60
N_PROPOSERS = (3, 5, 8)
#: Probability a proposer recovers any given true edge, before correlation.
DETECT = 0.55
#: 0.0 = independent proposers; 1.0 = every proposer sees exactly the same edges. Real AI proposers
#: sit high, which is the point of the sweep.
CORRELATION = (0.0, 0.3, 0.6, 0.85)
REPEATS = 300


def propose(k: int, corr: float, rng: random.Random) -> list[set[int]]:
    """k proposers over TRUE_EDGES, sharing `corr` of their detection tendency.

    Correlation is modelled the way it actually arises: each edge has a latent 'obviousness' that all
    proposers partly share, so hard edges are hard for everybody. That is exactly why several runs of
    one model, or several models trained on the same corpora, miss the same things.
    """
    obvious = [rng.random() for _ in range(TRUE_EDGES)]
    out = []
    for _ in range(k):
        own = [rng.random() for _ in range(TRUE_EDGES)]
        blended = [corr * o + (1 - corr) * w for o, w in zip(obvious, own)]
        # threshold so the marginal detection rate stays at DETECT whatever the correlation
        cut = sorted(blended)[int(TRUE_EDGES * (1 - DETECT))]
        out.append({i for i, b in enumerate(blended) if b >= cut})
    return out


def chao2(lists: list[set[int]]) -> float:
    """Estimated true richness from incidence across k lists."""
    k = len(lists)
    counts = Counter(e for s in lists for e in s)
    s_obs = len(counts)
    q1 = sum(1 for v in counts.values() if v == 1)
    q2 = sum(1 for v in counts.values() if v == 2)
    if q2 == 0:
        return s_obs + ((k - 1) / k) * q1 * (q1 - 1) / 2      # bias-corrected form
    return s_obs + ((k - 1) / k) * q1 * q1 / (2 * q2)


def main() -> None:
    rng = random.Random(20260914)
    print("=" * 76)
    print("CAN WE ESTIMATE COMPLETENESS WITHOUT GROUND TRUTH?")
    print("=" * 76)
    print(f"\n   {TRUE_EDGES} true edges, each proposer recovers {DETECT:.0%} of them.")
    print(f"   'observed' is the union of the proposers; 'Chao2' is what the estimator claims.\n")
    print(f"   {'proposers':>10} {'corr':>6} {'observed':>9} {'Chao2':>8} {'true':>6} "
          f"{'est. completeness':>18} {'actual':>8}")
    print("   " + "-" * 72)
    grid = {}
    for k in N_PROPOSERS:
        for corr in CORRELATION:
            obs, est = [], []
            for _ in range(REPEATS):
                lists = propose(k, corr, rng)
                union = set().union(*lists)
                obs.append(len(union))
                est.append(chao2(lists))
            o, e = statistics.mean(obs), statistics.mean(est)
            claimed = o / e if e else 1.0
            actual = o / TRUE_EDGES
            grid[f"{k}-{corr}"] = {"observed": o, "chao2": e,
                                   "claimed_completeness": claimed, "actual": actual}
            print(f"   {k:>10} {corr:>6.2f} {o:>9.1f} {e:>8.1f} {TRUE_EDGES:>6} "
                  f"{claimed:>17.0%} {actual:>8.0%}")

    print(f"\n   The two right-hand columns are the whole result. Where they agree the estimator")
    print(f"   works; where 'est.' exceeds 'actual' it is reporting a graph as more complete than")
    print(f"   it is, and a triage step reading it would choose focus when it needed flare.")
    Path("completeness-result.json").write_text(json.dumps(grid, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
