"""
Is the RETENTION penalty edge-specific, and is that ranking reliable enough to use?

`mastery_exit.py` asked whether the release penalty is concentrated on particular downstream skills
rather than spread flat, and found it is -- p = 0.0020, with a split-half reliability of 0.458
against a 0.80 bar. That was measured on first-attempt correctness.

`lag.py` then showed first-attempt correctness is the wrong outcome: the prerequisite deficit
DECAYS on it (+0.0440 at a fortnight, +0.0134 by eleven weeks), while the durability deficit does
not (+0.0312 among learners with equal initial success).

So the concentration test is worth re-running on the outcome that does not fade. There are two
reasons to expect it to do better, and they are worth stating before the number appears:

  LESS CONFOUND   conditioning on first-time success means both groups demonstrated they could do
                  it once, so the comparison starts from equal demonstrated capability rather than
                  from equal estimated ability
  LESS NOISE      the outcome is a learner's mean over ~7 later attempts, not a single binary

If the edge ranking is still unreliable on the better estimand, that is a fact about how much
structure is there to find, not about the choice of outcome.

    python3 retention_edges.py [--out result.json] [--min-cell 30]
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lag import later_attempts, when  # noqa: E402
from mastery_exit import (MIN_RUN, PERMUTATIONS, SEED, adjusted_gap, exits,  # noqa: E402
                          prior_ability, read, strata_of)

MIN_CELL = 30
MIN_HALF = 10


def build():
    print("reading the log")
    seq, first_seen = read()
    ex = list(exits(seq))
    later = later_attempts(seq)
    print(f"   {len(ex):,} skill-builder runs of {MIN_RUN}+ problems on a single skill")

    rows = []
    for learner, skill, mast, t_exit, _n in ex:
        fs = first_seen.get(learner, {})
        abil, k = prior_ability(fs, t_exit)
        if k < 5:
            continue
        for s, (t, ok) in fs.items():
            if s == skill or t <= t_exit or not ok:
                continue  # not downstream, or not a first-time success
            rest = [o for tt, o in later.get((learner, s), ()) if tt > t]
            if not rest:
                continue
            rows.append((learner, skill, s, int(mast), abil, float(np.mean(rest))))
    print(f"   {len(rows):,} first-time successes with a later attempt")
    return rows


def main() -> None:
    argv = sys.argv
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    min_cell = int(argv[argv.index("--min-cell") + 1]) if "--min-cell" in argv else MIN_CELL

    rows = build()
    learner = np.array([r[0] for r in rows])
    a_skill = np.array([r[1] for r in rows])
    b_skill = np.array([r[2] for r in rows])
    mast = np.array([r[3] for r in rows], np.int8)
    abil = np.array([r[4] for r in rows], float)
    y = np.array([r[5] for r in rows], float)
    stratum = strata_of(abil)
    rng = np.random.default_rng(SEED)

    adj = adjusted_gap(mast, y, stratum)
    print(f"\n   flat ability-stratified retention gap   {adj:+.4f}")

    key = defaultdict(list)
    for i, (a, b) in enumerate(zip(a_skill, b_skill)):
        key[(a, b)].append(i)
    pairs, index, gaps = [], [], []
    for (a, b), raw in key.items():
        idx = np.array(raw)
        if (mast[idx] == 1).sum() < min_cell or (mast[idx] == 0).sum() < min_cell:
            continue
        g = adjusted_gap(mast[idx], y[idx], stratum[idx])
        if not np.isnan(g):
            pairs.append((a, b, len(idx)))
            index.append(idx)
            gaps.append(g)
    gaps = np.array(gaps)
    print(f"   readable edges (>= {min_cell} each side)   {len(gaps):,}")
    if len(gaps) < 50:
        print("   too few readable edges -- stop here")
        return
    print(f"   edge gap: median {np.median(gaps):+.4f}  sd {gaps.std():.4f}")

    # same null as mastery_exit: exit status permuted within ability stratum and skill A, and the
    # permuted unit is the EXIT, because one learner carries one status into every downstream skill
    exit_id: dict[tuple, int] = {}
    unit = np.empty(len(y), np.int64)
    for i, (u, a) in enumerate(zip(learner, a_skill)):
        unit[i] = exit_id.setdefault((u, a), len(exit_id))
    u_first = np.zeros(len(exit_id), np.int64)
    u_first[unit[::-1]] = np.arange(len(y))[::-1]
    u_mast, u_stratum, u_a = mast[u_first], stratum[u_first], a_skill[u_first]

    blocks = defaultdict(list)
    for i, (st, a) in enumerate(zip(u_stratum, u_a)):
        blocks[(st, a)].append(i)
    blocks = [np.array(v) for v in blocks.values() if len(v) > 1]

    spread = []
    for _ in range(PERMUTATIONS):
        pu = u_mast.copy()
        for blk in blocks:
            pu[blk] = rng.permutation(pu[blk])
        perm = pu[unit]
        g0 = [v for idx in index
              if (perm[idx] == 1).any() and (perm[idx] == 0).any()
              and not np.isnan(v := adjusted_gap(perm[idx], y[idx], stratum[idx]))]
        if g0:
            spread.append(np.std(g0))
    spread = np.array(spread)
    p = float((spread >= gaps.std()).mean())
    excess = gaps.var() - float((spread ** 2).mean())
    sigma = float(np.sqrt(excess)) if excess > 0 else 0.0
    print(f"   null spread  mean {spread.mean():.4f}   observed {gaps.std():.4f}   p = {p:.4f}")
    print(f"   edge-specific component: sd {sigma:.4f}")

    # the criterion that decides whether any of this is usable
    uniq = np.unique(learner)
    half = set(rng.choice(uniq, len(uniq) // 2, replace=False).tolist())
    side = np.array([u in half for u in learner])
    ga, gb = [], []
    for idx in index:
        for m, acc in ((side[idx], ga), (~side[idx], gb)):
            sub = idx[m]
            acc.append(adjusted_gap(mast[sub], y[sub], stratum[sub])
                       if (mast[sub] == 1).sum() >= MIN_HALF and (mast[sub] == 0).sum() >= MIN_HALF
                       else np.nan)
    ga, gb = np.array(ga), np.array(gb)
    ok = ~(np.isnan(ga) | np.isnan(gb))
    r = float(np.corrcoef(ga[ok], gb[ok])[0, 1]) if ok.sum() > 20 else float("nan")
    sb = 2 * r / (1 + r) if r > -1 else float("nan")
    print(f"\n   SPLIT-HALF over learners: r = {r:.3f} on {int(ok.sum()):,} edges")
    print(f"   full-sample reliability {sb:.3f}   (first-attempt version: 0.458; target 0.80;"
          f" a seven-rater human panel: 0.857)")

    res = dict(observations=len(y), flat_gap=float(adj), readable_edges=len(gaps),
               edge_gap_sd=float(gaps.std()), null_spread_mean=float(spread.mean()),
               p_concentrated=p, edge_component_sd=sigma,
               split_half_r=r, split_half_reliability=sb)
    if out:
        out.write_text(json.dumps(res, indent=1))
        print(f"\n   -> {out}")


if __name__ == "__main__":
    main()
