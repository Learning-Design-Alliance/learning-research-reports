"""Does the assay's ranking become reliable on the RETENTION estimand rather than first attempt?

`split_half.py` measured the per-edge ranking at Spearman-Brown 0.475-0.643 on first-attempt
correctness, and `coarse.py` showed that changing the OUTPUT UNIT does not rescue it -- grouping KCs
is no better than the edge and the coarsest grain is worse. The remaining lever is the ESTIMAND, and
there is prior evidence it is the stronger one: on ASSISTments skill builders the same concentration test scored 0.523 on
retention against 0.458 on first-attempt correctness.

THE RETENTION ESTIMAND, as `studies/identifiability/rdd/lag.py` defines it: among learners who got B RIGHT FIRST TIME, how
well did it hold on later attempts? Conditioning on initial success is what isolates durability from
ability -- both groups have demonstrated they could do it once, so the comparison starts from equal
demonstrated capability rather than equal estimated ability. And the outcome is a learner's mean over
several later attempts rather than one binary, so it carries less noise.

`studies/identifiability/rdd/lag.py` also established WHY it is the right outcome rather than merely a different one: the
prerequisite deficit on first-attempt correctness DECAYS with time (+0.0440 at a fortnight, +0.0134
by eleven weeks) while the durability deficit does not (+0.0312 at equal initial success). First
attempt measures the gate at the moment the hook effect is smallest.

BOTH ESTIMANDS ARE SCORED ON THE SAME PAIRS, THE SAME SPLITS, THE SAME LEARNERS. Otherwise a
reliability difference could be a difference in which pairs survived the filters rather than in the
outcome, and that is the comparison this study exists to make.

PRE-REGISTERED, written before the run: retention is expected to beat first attempt, by roughly the
0.065 seen on ASSISTments skill builders (0.458 -> 0.523). Whether that is enough to reach the 0.80 gate is the question;
starting from 0.475-0.643, a gain of that size is NOT enough, so the honest prediction is
IMPROVED BUT STILL SHORT.

    python3 retention.py [--splits 8] [--pairs 6000] [--out out/retention.json]

Exports stay in the scratchpad; only the aggregate row per corpus is committed.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))

from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, timelines  # noqa: E402
from split_half import partial, spearman  # noqa: E402

SEED = 20260922
SPLITS, N_PAIRS = 8, 6000
MIN_CELL = 5
#: later attempts required at B before a learner's durability can be read at all
MIN_LATER = 1  # overridable with --min-later; see the sweep in README
MIN_PAIRS = 30
GATE = 0.80


def index(by_learner):
    """first touch, first pass, outcome at touch, and the mean of LATER attempts, per learner/item."""
    ft, fp, oat, later = {}, {}, {}, {}
    for u, rows in by_learner.items():
        a, b, c, seen = {}, {}, {}, defaultdict(list)
        for t, it, ok in rows:
            seen[it].append(ok)
            if it not in a:
                a[it], c[it] = t, ok
            if ok and it not in b:
                b[it] = t
        ft[u], fp[u], oat[u] = a, b, c
        later[u] = {it: (float(np.mean(v[1:])), len(v) - 1) for it, v in seen.items() if len(v) > 1}
    return ft, fp, oat, later


def at_item(ft):
    idx = defaultdict(list)
    for u, d in ft.items():
        for it, t in d.items():
            idx[it].append((u, t))
    return idx


def both_estimands(pair, ft, fp, oat, later, idx):
    """(first-attempt drop, retention drop) for one pair, or None where a cell is short.

    The retention arm conditions on getting B right first time, so the two arms are computed over
    DIFFERENT learners by construction -- but over the same PAIR, which is the unit being ranked.
    """
    a, b = pair
    fa_m, fa_f, re_m, re_f = [], [], [], []
    for u, tb in idx[b]:
        ta = ft[u].get(a)
        if ta is None or ta >= tb:
            continue
        held = (pa := fp[u].get(a)) is not None and pa < tb
        (fa_m if held else fa_f).append(oat[u][b])
        if not oat[u][b]:
            continue                      # retention conditions on first-time SUCCESS
        lat = later[u].get(b)
        if lat is None or lat[1] < MIN_LATER:
            continue
        (re_m if held else re_f).append(lat[0])
    out = []
    for m, f in ((fa_m, fa_f), (re_m, re_f)):
        out.append(float(np.mean(m)) - float(np.mean(f))
                   if len(m) >= MIN_CELL and len(f) >= MIN_CELL else None)
    return tuple(out)


def run(name, rows, splits, n_pairs, rng):
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft, fp, oat, later = index(by_learner)
    items = sorted(at_item(ft))
    allp = [(a, b) for a in items for b in items if a != b]
    pairs = [allp[i] for i in rng.choice(len(allp), min(n_pairs, len(allp)), replace=False)]
    print(f"{name}: {len(learners):,} learners, {len(items)} items, {len(pairs):,} pairs")

    fa_rs, re_rs, ns = [], [], []
    for s in range(splits):
        perm = rng.permutation(len(learners))
        sides = ({learners[i] for i in perm[:len(perm) // 2]},
                 {learners[i] for i in perm[len(perm) // 2:]})
        scored = []
        for side in sides:
            sub = {k: v for k, v in by_learner.items() if k in side}
            f2, p2, o2, l2 = index(sub)
            i2 = at_item(f2)
            scored.append({p: both_estimands(p, f2, p2, o2, l2, i2) for p in pairs})
        # THE SAME PAIR SET FOR BOTH ARMS: a pair counts only if BOTH estimands are readable on
        # BOTH halves, so any reliability difference is the outcome and not the sample
        keys = [p for p in pairs
                if all(scored[h][p][k] is not None for h in (0, 1) for k in (0, 1))]
        if len(keys) < MIN_PAIRS:
            continue
        fa_rs.append(spearman([scored[0][p][0] for p in keys], [scored[1][p][0] for p in keys]))
        re_rs.append(spearman([scored[0][p][1] for p in keys], [scored[1][p][1] for p in keys]))
        ns.append(len(keys))
        print(f"   split {s+1}/{splits}: {len(keys):,} pairs readable on both arms and both halves",
              flush=True)

    if not ns:
        return dict(corpus=name, skipped="no split kept enough pairs on both arms")

    def sb(rs):
        r = float(np.nanmean(rs))
        return r, (2 * r / (1 + r) if r > -1 else float("nan"))

    r_fa, sb_fa = sb(fa_rs)
    r_re, sb_re = sb(re_rs)
    print(f"   first attempt : split-half {r_fa:+.3f} -> Spearman-Brown {sb_fa:+.3f}")
    print(f"   RETENTION     : split-half {r_re:+.3f} -> Spearman-Brown {sb_re:+.3f}  "
          f"(gain {sb_re - sb_fa:+.3f})")
    return dict(corpus=name, splits=len(ns), pairs_median=int(np.median(ns)),
                first_attempt_split_half=r_fa, first_attempt_sb=sb_fa,
                retention_split_half=r_re, retention_sb=sb_re,
                gain=sb_re - sb_fa,
                retention_meets_gate=bool(sb_re >= GATE),
                min_later=MIN_LATER, min_cell=MIN_CELL)


def main() -> None:
    argv = sys.argv
    splits = int(argv[argv.index("--splits") + 1]) if "--splits" in argv else SPLITS
    n_pairs = int(argv[argv.index("--pairs") + 1]) if "--pairs" in argv else N_PAIRS
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "out/retention.json"
    if "--min-later" in argv:
        globals()["MIN_LATER"] = int(argv[argv.index("--min-later") + 1])
    if "--only" in argv:
        globals()["ONLY"] = argv[argv.index("--only") + 1]
    rng = np.random.default_rng(SEED)

    rows = []
    only = globals().get("ONLY")
    for name, loader in (("ednet", lambda: ednet_rows(SCRATCH / "ednet")),
                         ("xes3g5m", lambda: xes3g5m_rows(SCRATCH / "xes3g5m"))):
        if only and name != only:
            continue
        rows.append(run(name, loader(), splits, n_pairs, rng))

    good = [r for r in rows if "skipped" not in r]
    if good:
        best = max(good, key=lambda r: r["retention_sb"])
        print(f"\nA5 on the retention estimand: best Spearman-Brown {best['retention_sb']:+.3f} "
              f"on {best['corpus']}, against the 0.80 gate.")
        for r in good:
            print(f"   {r['corpus']:9s} estimand gain over first attempt on the same pairs: "
                  f"{r['gain']:+.3f}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, splits=splits, pairs=n_pairs, gate=GATE,
                                   min_later=MIN_LATER, rows=rows), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
