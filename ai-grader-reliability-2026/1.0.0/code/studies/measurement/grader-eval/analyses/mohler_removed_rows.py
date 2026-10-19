"""Rater-1 vs rater-2 agreement on the Mohler rows the consistency filter removes.

Paper VI ("The human ceiling", the row "Rater 1 vs rater 2 on the rows the consistency filter removed")
and release analysis `mohler-removed-rows`.

WHY THIS EXISTS. The vendored loader (`loadMohler`, vendor/934478716) keeps only rows whose two rater
scores lie in 0-5 and average to the mirror's `score_avg`. 546 of 2,273 rows fail, almost all (526)
because their per-rater scores are on 0-10 while `score_avg` stays on 0-5. The paper quotes QWK 0.418 on
those rows from an ad hoc rescaling that was never committed. The second independent reproduction
(research/readiness/ai-grader-reliability-2026/reproduction-2.md, row 17) matched 0.418 by halving both
rater scores. This script commits that computation and states its one hidden choice: halving makes
half-points, and 0.418 needs them rounded HALF TO EVEN (Python's round()). Rounded half up, as the
vendored TypeScript `quadraticWeightedKappa` does, the same rescaling gives 0.410. Both are reported, with
two other rescalings beside them, so the choice is visible:
  - halve_both, half to even      (the quoted 0.418)
  - halve_both, half up           (the vendored QWK's rounding)
  - halve_above_5, half to even   (r / 2 only where r > 5)
  - raw_0_10                      (no rescaling, QWK on 0-10)
QWK is quadratic-weighted kappa with chance from the observed marginals, the same formula as the
vendored metrics.ts. On the 1,727 kept rows it gives 0.519, the paper's ceiling, which is checked.
The release's "exact agreement 52.4%" is the share of removed rows whose two raw scores are equal.

Reads the analysed Mohler CSV (release dataset `mohler-answers`; `mohler-asag` in data/data-sources.json; rebuilt from the hashed
parquet by mohler_to_csv.py), path as argv[1] or $MOHLER_DIR/mohler_en.csv. No model call. Python
standard library only. Writes analyses/out/mohler-removed-rows.json (aggregates only).

    python3 studies/measurement/grader-eval/analyses/mohler_removed_rows.py [<mohler_en.csv>]
"""
import csv
import json
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def num(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def qwk(a, b, hi, rnd):
    levels = hi + 1
    ix = lambda v: min(levels - 1, max(0, rnd(v)))  # noqa: E731
    obs = [[0] * levels for _ in range(levels)]
    ha, hb = [0] * levels, [0] * levels
    for x, y in zip(a, b):
        i, j = ix(x), ix(y)
        obs[i][j] += 1
        ha[i] += 1
        hb[j] += 1
    n = len(a)
    num_ = den = 0.0
    for i in range(levels):
        for j in range(levels):
            w = (i - j) ** 2 / (levels - 1) ** 2
            num_ += w * obs[i][j]
            den += w * ha[i] * hb[j] / n
    return 1 - num_ / den


half_even = lambda v: int(round(v))          # noqa: E731
half_up = lambda v: math.floor(v + 0.5)      # noqa: E731


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ["MOHLER_DIR"]) / "mohler_en.csv"
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8")))
    kept, removed = [], []
    for r in rows:
        r1, r2, avg = num(r["score_grader_1"]), num(r["score_grader_2"]), num(r["score_avg"])
        if None in (r1, r2, avg) or not r["student_answer"].strip() or not r["question"].strip():
            continue
        # the vendored loader's filter, line for line
        if 0 <= r1 <= 5 and 0 <= r2 <= 5 and abs((r1 + r2) / 2 - avg) <= 1e-9:
            kept.append((r1, r2))
        else:
            removed.append((r1, r2))
    k = qwk([x for x, _ in kept], [y for _, y in kept], 5, half_up)
    assert abs(k - 0.5193) < 5e-5, k  # the paper's ceiling on the kept rows
    h1 = [x / 2 for x, _ in removed]
    h2 = [y / 2 for _, y in removed]
    out = {
        "rows_in_csv": len(rows),
        "rows_kept": len(kept),
        "rows_removed": len(removed),
        "rows_removed_with_a_score_above_5": sum(1 for x, y in removed if x > 5 or y > 5),
        "kept_qwk_0_5": k,
        "removed_qwk": {
            "halve_both_half_to_even": qwk(h1, h2, 5, half_even),
            "halve_both_half_up": qwk(h1, h2, 5, half_up),
            "halve_above_5_half_to_even": qwk([x / 2 if x > 5 else x for x, _ in removed],
                                              [y / 2 if y > 5 else y for _, y in removed], 5, half_even),
            "raw_0_10": qwk([x for x, _ in removed], [y for _, y in removed], 10, half_up),
        },
        "removed_exact_agreement_unrounded": sum(1 for x, y in removed if x == y) / len(removed),
        "quoted": "0.418 is halve_both_half_to_even; exact agreement 52.4% is removed_exact_agreement_unrounded",
    }
    (HERE / "out").mkdir(exist_ok=True)
    (HERE / "out" / "mohler-removed-rows.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
