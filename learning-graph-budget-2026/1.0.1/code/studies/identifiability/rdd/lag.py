"""
Is a prerequisite a gate or a hook?

`mastery_exit.py` found that being released from a skill builder without mastery costs something
downstream, and that the cost is edge-specific rather than flat. It measured that cost at the
learner's FIRST encounter with each downstream skill -- minutes or hours later. That is the right
measurement for one theory of what a prerequisite is and the wrong one for the other.

    GATE   you cannot do B without A. The penalty is there immediately and does not grow.
    HOOK   B does not STICK without A. Learning is expansion -- new material attaches to what is
           already held -- so a learner with nothing to attach to can still answer B correctly today
           by matching the surface of the problem set, and has nothing holding it later.

The two make opposite predictions about time. A gate's penalty is constant or decays as the learner
picks the prerequisite up elsewhere. A hook's penalty WIDENS: the hooked and the unhooked look alike
on day one and diverge.

So this re-cuts the same 1.28M observations by the lag between release and the downstream attempt.

Three things have to be controlled or the shape is an artefact:

Two arms, because the first one does not fully answer the question:

  DEFICIT PERSISTENCE   does lacking A hurt MORE when B is met later? This is the lag curve below.
                        It tests how long the deficit lasts, not whether B sticks.
  RETENTION OF B        among learners who got B RIGHT at first encounter, does their later
                        performance on B differ by whether they held A? That is the hook claim
                        stated exactly: same initial success, different durability.

  COMPOSITION   which skills a learner meets changes with lag, and skills differ in difficulty. The
                within-pair arm holds (A, B) fixed and compares its own short-lag and long-lag gap,
                so no skill enters one bucket and not another.
  ATTRITION     only learners still active appear at long lag. If released learners drop out faster,
                the survivors are the persistent ones and the gap shrinks -- biasing AGAINST the
                hook. Reported, not assumed away.
  ABILITY       as before: gaps are pooled within ability strata measured before the exit.

    python3 lag.py [--out result.json] [--buckets 5]
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mastery_exit import (MIN_RUN, SEED, STRATA, adjusted_gap, exits, prior_ability,  # noqa: E402
                          read, strata_of)

BOOTSTRAP = 400
#: a (lag bucket, edge) cell needs this many learners each side to contribute to the within-pair arm
MIN_PAIR_CELL = 15


def when(t: str) -> float:
    """Seconds since epoch. Most rows are 'YYYY-MM-DD HH:MM:SS'; some carry fractional seconds."""
    head, _, frac = t.partition(".")
    base = datetime.strptime(head, "%Y-%m-%d %H:%M:%S").timestamp()
    return base + (float(f"0.{frac}") if frac else 0.0)


def later_attempts(seq):
    """Per (learner, skill), every attempt after the first, in time order.

    `read()` keeps only first encounters, which is right for asking what a learner carried INTO a
    skill and wrong for asking whether it stayed. The sequence rows hold the rest.
    """
    by = defaultdict(list)
    for (learner, _), rows in seq.items():
        for t, ok, s in rows:
            by[(learner, s)].append((t, ok))
    for v in by.values():
        v.sort()
    return by


def build():
    print("reading the log")
    seq, first_seen = read()
    ex = list(exits(seq))
    n_mast = sum(1 for _, _, m, _, _ in ex if m)
    print(f"   {len(ex):,} skill-builder runs of {MIN_RUN}+ problems on a single skill")
    print(f"   exited with mastery {n_mast:,}  |  released without it {len(ex) - n_mast:,}")

    rows = []
    for learner, skill, mast, t_exit, _n in ex:
        fs = first_seen.get(learner, {})
        abil, k = prior_ability(fs, t_exit)
        if k < 5:
            continue
        te = when(t_exit)
        for s, (t, ok) in fs.items():
            if s == skill or t <= t_exit:
                continue
            rows.append((learner, skill, s, int(mast), abil, int(ok),
                         (when(t) - te) / 86400.0))
    print(f"   {len(rows):,} (exit, downstream skill) observations with a lag")
    return rows, seq, first_seen, ex


def retention(seq, first_seen, ex):
    """Among learners who got a downstream skill RIGHT first time, how did it hold?

    Conditioning on initial success is what isolates durability from ability: both groups have
    demonstrated they could do it once, and the question is only whether it stayed.
    """
    later = later_attempts(seq)
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
            rows.append((learner, int(mast), abil, float(np.mean(rest)), len(rest)))
    return rows


def boot_gap(mast, y, stratum, rng, n=BOOTSTRAP, cluster=None):
    """Adjusted gap with a bootstrap interval.

    `cluster` resamples LEARNERS rather than observations, which is the only honest unit here: one
    learner contributes hundreds of rows and their exit status is the same in all of them, so an
    observation bootstrap treats correlated rows as independent evidence and returns an interval
    far tighter than the data supports. The retention arm's interval was +-0.002 on 627,000 rows
    before this, which no 20,000-learner sample can justify.
    """
    point = adjusted_gap(mast, y, stratum)
    draws = []
    if cluster is None:
        for _ in range(n):
            b = rng.integers(0, len(y), len(y))
            g = adjusted_gap(mast[b], y[b], stratum[b])
            if not np.isnan(g):
                draws.append(g)
    else:
        uniq, inv = np.unique(cluster, return_inverse=True)
        members = [np.flatnonzero(inv == i) for i in range(len(uniq))]
        for _ in range(n):
            pick = rng.integers(0, len(uniq), len(uniq))
            b = np.concatenate([members[i] for i in pick])
            g = adjusted_gap(mast[b], y[b], stratum[b])
            if not np.isnan(g):
                draws.append(g)
    if not draws:
        return point, float("nan"), float("nan")
    return point, float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main() -> None:
    argv = sys.argv
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else None
    nb = int(argv[argv.index("--buckets") + 1]) if "--buckets" in argv else 5

    rows, seq, first_seen, ex = build()
    mast_runs = sum(1 for _, _, m, _, _ in ex if m)
    learner = np.array([r[0] for r in rows])
    a_skill = np.array([r[1] for r in rows])
    b_skill = np.array([r[2] for r in rows])
    mast = np.array([r[3] for r in rows], np.int8)
    abil = np.array([r[4] for r in rows], float)
    y = np.array([r[5] for r in rows], np.int8)
    lag = np.array([r[6] for r in rows], float)
    stratum = strata_of(abil)

    edges = np.quantile(lag, np.linspace(0, 1, nb + 1))
    bucket = np.clip(np.searchsorted(edges[1:-1], lag), 0, nb - 1)
    rng = np.random.default_rng(SEED)

    print(f"\nPENALTY BY LAG -- gate predicts flat or decaying, hook predicts widening")
    print(f"{'lag (days)':<18}{'n':>10}{'released %':>12}{'gap':>10}{'95% interval':>20}")
    curve = []
    for b in range(nb):
        m = bucket == b
        lo_d, hi_d = lag[m].min(), lag[m].max()
        g, lo, hi = boot_gap(mast[m], y[m], stratum[m], rng)
        rel = float((mast[m] == 0).mean())
        label = f"{lo_d:.1f} - {hi_d:.1f}"
        print(f"{label:<18}{int(m.sum()):>10,}{rel:>11.1%}{g:>10.4f}   [{lo:+.4f},{hi:+.4f}]")
        curve.append(dict(bucket=b, lo_days=float(lo_d), hi_days=float(hi_d),
                          n=int(m.sum()), released_frac=rel, gap=g, ci=[lo, hi]))

    # ATTRITION: the released share per bucket is the composition check. A falling share means the
    # released learners are leaving, and the survivors are the persistent ones.
    rel = np.array([c["released_frac"] for c in curve])
    print(f"\n   released share across buckets: {rel[0]:.1%} -> {rel[-1]:.1%}"
          f"   ({'falling, so long-lag gaps are biased DOWNWARD' if rel[-1] < rel[0] - 0.01 else 'stable'})")

    # WITHIN-PAIR: hold (A, B) fixed and compare its own first and last bucket. Skill composition
    # cannot move the answer here, because every pair contributes to both sides or to neither.
    print(f"\nWITHIN-PAIR -- same (A, B) measured early and late")
    first, last = 0, nb - 1
    key = defaultdict(lambda: {first: [], last: []})
    for i in range(len(y)):
        if bucket[i] in (first, last):
            key[(a_skill[i], b_skill[i])][bucket[i]].append(i)
    deltas, weights = [], []
    for (a, b), cells in key.items():
        vals = {}
        for bk in (first, last):
            idx = np.array(cells[bk], int)
            if len(idx) < 2 * MIN_PAIR_CELL:
                break
            if (mast[idx] == 1).sum() < MIN_PAIR_CELL or (mast[idx] == 0).sum() < MIN_PAIR_CELL:
                break
            g = adjusted_gap(mast[idx], y[idx], stratum[idx])
            if np.isnan(g):
                break
            vals[bk] = (g, len(idx))
        if len(vals) == 2:
            deltas.append(vals[last][0] - vals[first][0])
            weights.append(min(vals[first][1], vals[last][1]))
    deltas, weights = np.array(deltas), np.array(weights, float)
    if len(deltas) >= 10:
        w = weights / weights.sum()
        point = float((w * deltas).sum())
        draws = [float((lambda s: (weights[s] / weights[s].sum() * deltas[s]).sum())(
            rng.integers(0, len(deltas), len(deltas)))) for _ in range(BOOTSTRAP)]
        lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
        print(f"   {len(deltas):,} pairs readable in both buckets")
        print(f"   late gap minus early gap   {point:+.4f}   [{lo:+.4f},{hi:+.4f}]")
        verdict = ("HOOK -- the penalty widens with time" if lo > 0 else
                   "GATE -- the penalty does not widen" if hi < 0 else
                   "UNDECIDED -- the interval spans zero")
        print(f"   {verdict}")
    else:
        point = lo = hi = float("nan")
        verdict = "UNREADABLE -- too few pairs survive in both buckets"
        print(f"   {verdict}")

    # how small a widening could this arm have seen? "Undecided" without a magnitude is not a
    # result, it is a shrug
    half = (hi - lo) / 2
    print(f"   this arm could only have detected a widening of {half:+.4f} or more")

    print(f"\nRETENTION -- among learners who got the downstream skill RIGHT first time,")
    print(f"             did it hold, and does holding A predict that?")
    ret = retention(seq, first_seen, ex)
    if len(ret) > 1000:
        rl = np.array([r[0] for r in ret])
        rm = np.array([r[1] for r in ret], np.int8)
        ra = np.array([r[2] for r in ret], float)
        ry = np.array([r[3] for r in ret], float)
        rn = np.array([r[4] for r in ret], float)
        rs = strata_of(ra)
        g, rlo, rhi = boot_gap(rm, ry, rs, rng, n=200, cluster=rl)
        print(f"   {len(ret):,} first-time successes with a later attempt, "
              f"{len(np.unique(rl)):,} learners")
        print(f"   later attempts per success: mastered {rn[rm == 1].mean():.2f}   "
              f"released {rn[rm == 0].mean():.2f}"
              f"   (more practice would help them, not hurt)")
        print(f"   later accuracy: mastered {ry[rm == 1].mean():.4f}   "
              f"released {ry[rm == 0].mean():.4f}")
        print(f"   ability-stratified gap   {g:+.4f}   [{rlo:+.4f},{rhi:+.4f}]"
              f"   (learner-clustered bootstrap)")
        rverdict = ("HOOK -- same initial success, worse retention without the prerequisite"
                    if rlo > 0 else
                    "NO HOOK -- initial success holds equally with or without the prerequisite"
                    if rhi < 0 else "UNDECIDED -- the retention interval spans zero")
        print(f"   {rverdict}")
    else:
        g = rlo = rhi = float("nan")
        rverdict = "UNREADABLE -- too few first-time successes with a later attempt"
        print(f"   {rverdict}")

    res = dict(runs=len(ex), mastered=int(mast_runs), released=int(len(ex) - mast_runs),
               observations=len(y), buckets=curve,
               within_pair_mde=float(half),
               retention=dict(n=len(ret), gap=g, ci=[rlo, rhi], verdict=rverdict),
               released_share=[float(rel[0]), float(rel[-1])],
               within_pair=dict(n_pairs=int(len(deltas)), delta=point, ci=[lo, hi]),
               verdict=verdict)
    if out:
        out.write_text(json.dumps(res, indent=1))
        print(f"\n   -> {out}")


if __name__ == "__main__":
    main()
