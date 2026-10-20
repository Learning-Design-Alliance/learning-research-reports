"""A5: run the assay twice on split data -- does it say the same thing?

A5 has stood at **0.523** against a 0.80 gate, measured on the retention estimand over ASSISTments skill-builder edges (`studies/identifiability/rdd/retention_edges.py`;
earlier text said Junyi, corrected 2026-09-24).
That figure was obtained where the identifying cell is largely EMPTY: you cannot rank edges reliably
when most of them cannot be read at all, so it has never been clear whether 0.523 is a fact about the
assay or a fact about the corpora it was measured on.

Two corpora now settle that. `studies/identifiability/overlap/atlas.py` shows XES3G5M readable on 24.3% of arbitrary ordered
pairs and EdNet on 81.5% (re-issued) -- the only two on disk where the identifying cell survives, because both are
practice platforms where learners choose rather than tutors that gate. If the ranking is going to be
reliable anywhere, it is here, and if it is not reliable here the 0.80 gate is not a sampling problem.

METHOD, unchanged from `studies/identifiability/junyi/assay_controls.py` so the numbers are comparable: split the learners at
random into halves, score every pair independently on each half, Spearman-correlate the two halves
across pairs, repeat. Spearman-Brown steps the split-half figure back up to the full sample.

THE CEILING THIS SETS. If the assay correlates with itself at r, no predictor can correlate with it
above roughly sqrt(r) for reasons having nothing to do with the predictor. Every elicitation and
critic number in this repo is bounded by it.

TWO CONTROLS, because a reliability figure is easy to inflate.

  READABILITY IS NOT FREE. A pair scoreable on both halves at a larger cell is a different, easier
  population than one scoreable at MIN_CELL. The sweep over `min_cell` reports how much of the
  reliability is bought by discarding pairs rather than by the assay agreeing with itself.

  REACH IS A CONFOUND. Pairs differ enormously in how many learners reach them, and a ranking that is
  really a ranking of REACH would replicate beautifully while saying nothing about edges. The
  reach-partialled figure removes it.

    python3 split_half.py [--splits 40] [--out out/split_half.json]

Raw exports stay in the scratchpad; only the aggregate row per corpus is committed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "studies/identifiability/overlap"))
sys.path.insert(0, str(HERE.parents[2]))

from atlas import ednet_rows, xes3g5m_rows  # noqa: E402
from positivity import SCRATCH, at_item, classify, states, timelines  # noqa: E402
from shared.stats import rank  # noqa: E402

SEED = 20260921
SPLITS = 40
#: cell sizes to sweep. MIN_CELL elsewhere in the repo is 5; larger values buy reliability by
#: discarding pairs, which is why the whole sweep is reported rather than the best row
CELLS = (5, 10, 20)
#: a split that leaves fewer scoreable pairs than this cannot support a correlation
MIN_PAIRS = 30
MAX_PAIRS = 6000
GATE = 0.80


def spearman(x, y) -> float:
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return float("nan")
    rx = rank(x)
    ry = rank(y)
    if rx.std() == 0 or ry.std() == 0:
        return float("nan")
    return float(np.corrcoef(rx, ry)[0, 1])


def partial(x, y, z) -> float:
    """Spearman of x and y with z partialled out, on ranks."""
    x, y, z = (rank(v) for v in (x, y, z))
    if len(x) < 4 or x.std() == 0 or y.std() == 0 or z.std() == 0:
        return float("nan")
    rxy, rxz, ryz = (float(np.corrcoef(a, b)[0, 1]) for a, b in ((x, y), (x, z), (y, z)))
    den = np.sqrt(max(1 - rxz ** 2, 1e-12) * max(1 - ryz ** 2, 1e-12))
    return float((rxy - rxz * ryz) / den)


def drops(pairs, first_touch, first_pass, outcome_at_touch, idx, min_cell):
    """The assay's per-pair statistic, and the pair's reach, for the pairs it can read."""
    out = {}
    for a, b in pairs:
        c = classify((a, b), first_touch, first_pass, outcome_at_touch, idx)
        nm, nf = len(c["mastered"]), len(c["failed"])
        if nm < min_cell or nf < min_cell:
            continue
        out[(a, b)] = (float(np.mean(c["mastered"])) - float(np.mean(c["failed"])),
                       nm + nf + len(c["never"]))
    return out


def run(name, rows, splits, rng) -> list[dict]:
    by_learner = timelines(rows)
    learners = sorted(by_learner)
    ft, fp, oat = states(by_learner)
    idx = at_item(ft, oat)
    items = sorted(idx)
    pairs = [(a, b) for a in items for b in items if a != b]
    if len(pairs) > MAX_PAIRS:
        pairs = [pairs[i] for i in rng.choice(len(pairs), MAX_PAIRS, replace=False)]
    print(f"{name}: {len(learners):,} learners, {len(items)} items, {len(pairs):,} pairs sampled")

    out = []
    for min_cell in CELLS:
        halves, partials, npairs = [], [], []
        for _ in range(splits):
            perm = rng.permutation(len(learners))
            sides = [{learners[i] for i in perm[:len(perm) // 2]},
                     {learners[i] for i in perm[len(perm) // 2:]}]
            scored = []
            for side in sides:
                sub = {k: v for k, v in by_learner.items() if k in side}
                f2, p2, o2 = states(sub)
                i2 = at_item(f2, o2)
                scored.append(drops(pairs, f2, p2, o2, i2, min_cell))
            both = sorted(set(scored[0]) & set(scored[1]))
            if len(both) < MIN_PAIRS:
                continue
            x = [scored[0][k][0] for k in both]
            y = [scored[1][k][0] for k in both]
            reach = [scored[0][k][1] + scored[1][k][1] for k in both]
            halves.append(spearman(x, y))
            partials.append(partial(x, y, reach))
            npairs.append(len(both))

        if not halves:
            out.append(dict(corpus=name, min_cell=min_cell,
                            skipped=f"no split keeps {MIN_PAIRS} pairs readable on both sides"))
            print(f"   min_cell={min_cell}: NOT ESTIMABLE -- no split keeps {MIN_PAIRS} pairs")
            continue
        r = float(np.nanmean(halves))
        rp = float(np.nanmean(partials))
        sb = 2 * r / (1 + r) if r > -1 else float("nan")
        sbp = 2 * rp / (1 + rp) if rp > -1 else float("nan")
        row = dict(corpus=name, min_cell=min_cell, splits=len(halves),
                   pairs_median=int(np.median(npairs)),
                   split_half=r, spearman_brown=sb,
                   split_half_reach_partialled=rp, spearman_brown_reach_partialled=sbp,
                   predictor_ceiling=float(np.sqrt(max(sb, 0))),
                   meets_gate=bool(sb >= GATE))
        out.append(row)
        print(f"   min_cell={min_cell:2d}: {len(halves):2d} splits, {int(np.median(npairs)):5,d} pairs "
              f"| split-half {r:+.3f} -> Spearman-Brown {sb:+.3f} "
              f"({'MEETS' if sb >= GATE else 'below'} the {GATE:.2f} gate) "
              f"| reach-partialled {sbp:+.3f} | predictor ceiling {np.sqrt(max(sb,0)):.3f}")
    return out


def main() -> None:
    argv = sys.argv
    splits = int(argv[argv.index("--splits") + 1]) if "--splits" in argv else SPLITS
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else HERE / "out/split_half.json"
    rng = np.random.default_rng(SEED)

    corpora = []
    if (SCRATCH / "xes3g5m/attempts.tsv").exists():
        corpora.append(("xes3g5m", lambda: xes3g5m_rows(SCRATCH / "xes3g5m")))
    if (SCRATCH / "ednet/contents/questions.csv").exists():
        corpora.append(("ednet", lambda: ednet_rows(SCRATCH / "ednet")))
    if not corpora:
        print("neither positivity-passing corpus is in the scratchpad")
        raise SystemExit(1)

    rows = []
    for name, loader in corpora:
        rows += run(name, loader(), splits, rng)

    best = [r for r in rows if r.get("spearman_brown") is not None and "skipped" not in r]
    if best:
        top = max(best, key=lambda r: r["spearman_brown"])
        print(f"\nA5: best Spearman-Brown {top['spearman_brown']:+.3f} on {top['corpus']} at "
              f"min_cell={top['min_cell']}, against a gate of {GATE:.2f} and the standing 0.523 "
              f"measured where the identifying cell is mostly empty.")
        print(f"   No predictor can correlate with this assay above {top['predictor_ceiling']:.3f}.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(seed=SEED, splits=splits, cells=CELLS, gate=GATE,
                                   min_pairs=MIN_PAIRS, rows=rows), indent=2) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
