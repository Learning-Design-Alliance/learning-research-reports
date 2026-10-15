"""
The tutor's own stopping rule fills the cell the tutor is built to keep empty.

`studies/identifiability/overlap/positivity.py` shows why every structural null in this programme is uninterpretable: a
mastery-learning tutor almost never lets a learner reach B without A, so the cell that identifies a
gate is empty. On Junyi, 2 of 775 authored edges have enough learners in it to read at all.

ASSISTments skill builders have a second exit. A learner leaves a skill builder when they get three
problems right in a row -- OR when they run out of problems and are released anyway. The second exit
is a learner the system passed forward WITHOUT mastery, and there are tens of thousands of them.
That is the overlap, manufactured by the same mechanism that destroys it everywhere else.

What makes this readable is not the exit by itself -- learners who fail to master a skill are weaker
learners, and they would do worse on everything downstream for that reason alone. It is the
CONTRAST ACROSS DOWNSTREAM SKILLS. Ability is one number per learner; a prerequisite is a claim
about particular pairs. So for each skill A we ask whether the unmastered-exit penalty is
concentrated on some downstream skills and absent on others, against a null that permutes exit
status within ability strata. A penalty that is flat across every downstream skill is ability. A
penalty that is concentrated is the first structural signal in this programme that does not rest on
a model choosing its own shape.

    python3 mastery_exit.py [--out result.json] [--min-cell 30] [--half]

Raw ASSISTments exports stay outside the repo; only the aggregates printed here are committed.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.paths import data_path  # noqa: E402

SEED = 20260920
#: a skill-builder run needs at least this many problems before "did not reach three in a row"
#: means anything -- a learner who answered twice and left has not been released without mastery,
#: they have just left
MIN_RUN = 5
#: per (A, B) cell, on each side of the exit split
MIN_CELL = 30
#: ability strata for the permutation null and the adjusted gap
STRATA = 10
PERMUTATIONS = 500


def read():
    """One pass over the log, yielding both things this study needs.

    `seq`   every (learner, sequence_id) run, for finding the skill-builder exits
    `first` each learner's FIRST attempt per skill, which is the downstream outcome. First attempt
            only: later ones are contaminated by whatever the tutor did in between, and the question
            is what the learner carried out of the skill builder, not what it taught them after.
    """
    seq: dict[tuple[str, str], list[tuple[str, bool, str]]] = defaultdict(list)
    first: dict[str, dict[str, tuple[str, bool]]] = defaultdict(dict)
    with (data_path("ASSIST_DIR") / "assist_rich.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            s, u, t = r["skill_id"], r["user_id"], r["start_time"]
            if not s or s == "NA" or not t:
                continue
            ok = r["correct"] == "1"
            seq[(u, r["sequence_id"])].append((t, ok, s))
            prev = first[u].get(s)
            if prev is None or t < prev[0]:
                first[u][s] = (t, ok)
    return seq, first


def exits(seq):
    """Skill-builder exits, as (learner, skill, mastered, exit_time, n_problems).

    The unit is (learner, sequence_id): 52% of runs of three or more end exactly at their first
    three-in-a-row, which is the mastery rule showing through, and the rest are the release.
    """
    for (learner, _), rows in seq.items():
        if len(rows) < MIN_RUN:
            continue
        rows.sort()
        if len({s for _, _, s in rows}) != 1:
            continue  # a mixed sequence is not a skill builder; the exit would not name a skill
        yield learner, rows[-1][2], all(ok for _, ok, _ in rows[-3:]), rows[-1][0], len(rows)


def prior_ability(first_seen, exit_time):
    """Mean first-attempt correctness on everything met BEFORE the skill builder exited.

    Measured before the exit so it cannot be contaminated by the outcome, and it is the covariate
    the permutation null strata are built from.
    """
    v = [ok for _, (t, ok) in first_seen.items() if t < exit_time]
    return (float(np.mean(v)), len(v)) if v else (float("nan"), 0)


def build():
    print("reading the log")
    seq, first_seen = read()
    ex = list(exits(seq))
    n_mast = sum(1 for _, _, m, _, _ in ex if m)
    print(f"   {len(ex):,} skill-builder runs of {MIN_RUN}+ problems on a single skill")
    print(f"   exited with mastery {n_mast:,}  |  released without it {len(ex) - n_mast:,}")
    print(f"   {len({e[0] for e in ex}):,} learners")

    rows = []
    for learner, skill, mast, t_exit, n in ex:
        fs = first_seen.get(learner, {})
        abil, k = prior_ability(fs, t_exit)
        if k < 5:
            continue  # no ability estimate, no stratum, no comparison
        for s, (t, ok) in fs.items():
            if s == skill or t <= t_exit:
                continue
            rows.append((learner, skill, s, int(mast), abil, int(ok)))
    print(f"   {len(rows):,} (exit, downstream skill) observations")
    return rows


def strata_of(abil: np.ndarray) -> np.ndarray:
    q = np.quantile(abil, np.linspace(0, 1, STRATA + 1)[1:-1])
    return np.searchsorted(q, abil)


def adjusted_gap(mast, y, stratum, w_counts=None):
    """Mastered-minus-released difference, pooled over ability strata (Mantel-Haenszel style).

    Pooling within strata rather than regressing on ability keeps the estimate from leaning on a
    functional form; the strata are the same ones the permutation null shuffles inside.
    """
    num = den = 0.0
    for s in np.unique(stratum):
        m = stratum == s
        a, b = y[m & (mast == 1)], y[m & (mast == 0)]
        if len(a) == 0 or len(b) == 0:
            continue
        w = len(a) * len(b) / (len(a) + len(b))
        num += w * (a.mean() - b.mean())
        den += w
    return num / den if den else float("nan")


def main() -> None:
    out = Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
    min_cell = int(sys.argv[sys.argv.index("--min-cell") + 1]) if "--min-cell" in sys.argv else MIN_CELL

    rows = build()
    learner = np.array([r[0] for r in rows])
    a_skill = np.array([r[1] for r in rows])
    b_skill = np.array([r[2] for r in rows])
    mast = np.array([r[3] for r in rows], np.int8)
    abil = np.array([r[4] for r in rows], float)
    y = np.array([r[5] for r in rows], np.int8)
    stratum = strata_of(abil)

    print(f"\nHEADLINE -- does being released without mastery cost anything downstream at all?")
    raw = y[mast == 1].mean() - y[mast == 0].mean()
    adj = adjusted_gap(mast, y, stratum)
    print(f"   raw gap                       {raw:+.4f}")
    print(f"   ability-stratified gap        {adj:+.4f}")
    print(f"   (a flat gap of this size on every downstream skill is ability, not structure)")

    print(f"\nPER-EDGE -- is the penalty concentrated on particular downstream skills?")
    rng = np.random.default_rng(SEED)
    key = defaultdict(list)
    for i, (a, b) in enumerate(zip(a_skill, b_skill)):
        key[(a, b)].append(i)
    pairs, index, gaps = [], [], []
    for (a, b), raw_idx in key.items():
        idx = np.array(raw_idx)
        if (mast[idx] == 1).sum() < min_cell or (mast[idx] == 0).sum() < min_cell:
            continue
        g = adjusted_gap(mast[idx], y[idx], stratum[idx])
        if not np.isnan(g):
            pairs.append((a, b, len(idx)))
            index.append(idx)
            gaps.append(g)
    gaps = np.array(gaps)
    print(f"   readable edges (>= {min_cell} learners each side)   {len(gaps):,}")
    if not len(gaps):
        print("   nothing readable -- stop here")
        return
    print(f"   edge gap: median {np.median(gaps):+.4f}  mean {gaps.mean():+.4f}"
          f"  sd {gaps.std():.4f}")

    # The null: exit status permuted within ability stratum and within skill A. Any spread that
    # survives is spread the ability covariate does not explain, leaving the dispersion a finite
    # sample produces on its own, which is what we are testing against.
    #
    # The permuted unit is the EXIT, not the row. A learner leaves skill A once and carries that one
    # status into every downstream skill they then meet, so shuffling rows independently hands the
    # same learner both statuses at once, destroys the within-learner correlation, and shrinks the
    # null until anything at all looks significant. Row-level shuffling put this at p = 0.0000.
    # grouped once: the mask-per-(stratum, skill) form rebuilds 2,650 boolean masks over millions
    # of rows on every permutation and dominates the run
    exit_id = {}
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
    p = float((spread >= gaps.std()).mean()) if len(spread) else float("nan")
    print(f"   null spread of edge gaps (exit permuted in stratum x skill A)")
    print(f"      mean {spread.mean():.4f}  sd {spread.std():.4f}   observed {gaps.std():.4f}"
          f"   p = {p:.4f}")
    verdict = ("CONCENTRATED -- the penalty is edge-specific beyond ability" if p < 0.05
               else "FLAT -- the penalty is one number per learner, which is ability, not structure")
    print(f"   {verdict}")

    # Significance says the excess dispersion is not zero; this says how big it is. The null spread
    # is what finite samples produce on their own, so what is left over is the edge-specific
    # component, and its square root is the typical edge's own penalty in percentage points.
    excess = gaps.var() - float((spread ** 2).mean())
    sigma = float(np.sqrt(excess)) if excess > 0 else 0.0
    print(f"   edge-specific component: sd {sigma:.4f}"
          f"   (vs a flat ability gap of {adj:+.4f})")

    # Does it replicate? Split the LEARNERS, recompute every edge gap on each half, correlate. An
    # edge set that does not survive this is a ranking of noise, whatever its p-value.
    uniq = np.unique(learner)
    half = set(rng.choice(uniq, len(uniq) // 2, replace=False).tolist())
    side = np.array([u in half for u in learner])
    ga, gb = [], []
    for idx in index:
        for m, acc in ((side[idx], ga), (~side[idx], gb)):
            sub = idx[m]
            acc.append(adjusted_gap(mast[sub], y[sub], stratum[sub])
                       if (mast[sub] == 1).sum() >= 10 and (mast[sub] == 0).sum() >= 10
                       else np.nan)
    ga, gb = np.array(ga), np.array(gb)
    ok = ~(np.isnan(ga) | np.isnan(gb))
    if ok.sum() > 20:
        r = float(np.corrcoef(ga[ok], gb[ok])[0, 1])
        # Spearman-Brown: the reliability of the full-sample estimate, not of one half
        sb = 2 * r / (1 + r) if r > -1 else float("nan")
        print(f"   split-half over learners: r = {r:.3f} on {int(ok.sum()):,} edges"
              f"   (full-sample reliability {sb:.3f})")
    else:
        r = sb = float("nan")
        print("   split-half: too few edges survive the split to read")

    top = sorted(zip(pairs, gaps), key=lambda z: -z[1])[:10]
    print(f"\n   largest edge penalties")
    for (a, b, n), g in top:
        print(f"      {a:>6} -> {b:<6}  n={n:<6}  gap {g:+.4f}")

    res = dict(runs=len(set(zip(learner, a_skill))), observations=len(y),
               raw_gap=float(raw), adjusted_gap=float(adj),
               readable_edges=len(gaps), edge_gap_median=float(np.median(gaps)),
               edge_gap_sd=float(gaps.std()), null_spread_mean=float(spread.mean()),
               p_concentrated=p, verdict=verdict,
               edge_component_sd=sigma, split_half_r=r, split_half_reliability=sb,
               top=[dict(a=a, b=b, n=n, gap=float(g)) for (a, b, n), g in top])
    if out:
        out.write_text(json.dumps(res, indent=1))
        print(f"\n   -> {out}")


if __name__ == "__main__":
    main()
