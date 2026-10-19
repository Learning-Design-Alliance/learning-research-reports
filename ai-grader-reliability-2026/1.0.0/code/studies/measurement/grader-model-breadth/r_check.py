"""Pearson r beside QWK for the true-label arm (repo rule: a change that moves kappa while r stays
flat moved where marks land, not what the grader perceives). Added after part 1 showed QWK GAINs on
three runs; reported only. Learner-cluster bootstrap (Q2's resampler), 4,000 resamples.

    python3 r_check.py <dump> ...
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "grader-attainment-prior"))
import analyse as q2  # noqa: E402

HERE = Path(__file__).resolve().parent


def main() -> None:
    rng = np.random.default_rng(5)
    out = {}
    for p in sys.argv[1:]:
        b = json.loads(Path(p).read_text())
        rows = [r for r in b["rows"] if None not in (r["control"], r["trueLabel"], r["swappedLabel"])]
        h = np.array([r["human"] for r in rows], float)
        c = np.array([r["control"] for r in rows], float)
        t = np.array([r["trueLabel"] for r in rows], float)
        L = np.array([str(r["learnerId"]) for r in rows])
        hi = np.array([r["tail"] == "high" for r in rows])
        f = lambda i: np.corrcoef(h[i], t[i])[0, 1] - np.corrcoef(h[i], c[i])[0, 1]  # noqa: E731
        est = f(np.arange(len(h)))
        bs = [f(q2.cluster_index(L, hi, rng)) for _ in range(4000)]
        key = f"{b['model']} [{b.get('reasoning', 'provider default')}] {Path(p).name}"
        out[key] = {"r_control": float(np.corrcoef(h, c)[0, 1]), "r_true": float(np.corrcoef(h, t)[0, 1]),
                    "dr": float(est), "ci95": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}
        print(f"{key:80s} r {out[key]['r_control']:.3f} -> {out[key]['r_true']:.3f}  dr {est:+.3f} [{out[key]['ci95'][0]:+.3f}, {out[key]['ci95'][1]:+.3f}]")
    (HERE / "out/r_check.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
