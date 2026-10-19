"""
Does pooling repeated grades improve agreement on JorGPT once it is measured in Pearson r? (2026-10-05)

WHY. Two staged statements disagree. The claim `pooling-repeated-llm-grades-does-not-improve-agreement`
(research/wiki/claims/, release ai-grader-reliability-2026 1.0.0) rests on JorGPT: three LITE passes
pooled by median or mean land within 0.005 QWK of a single call, n=150. The later log entry
studies/measurement/grader-eval/findings/log/2026-09-16-pooling-works-and-qwk-hid-it.md, on Menagerie
(whole CS1 programs, 14-level scale, 9 passes), found Pearson r +0.021 in three arms of four while QWK
moved +0.003, and concluded "pooling works and QWK hid it". The JorGPT run never recorded r per
estimator and saved no per-case scores, so whether QWK hid a gain on the claim's OWN corpus is unknown.
This re-runs JorGPT pooling at the Menagerie depth and reads it in r, QWK and MAE.

DATA. JorGPT (data/data-sources.json `jorgpt-answers`, CC BY 4.0), read only through the harness
(`--mode pool --n 150 --seed 7 --repeats 9 --dump ...`, studies/measurement/grader-eval/harness/
stability.ts), whose per-case dump stays in the scratchpad. Gemini 3.5 Flash Lite, thinking off, as
the original; one Gemini 3.7 Flash pass rides along because the mode always makes it.

QUANTITIES. For k in {3, 9}: dX_k = X(mean of the first k passes) - mean over the k single passes of
X(single pass), X in {r, QWK, MAE}; also the median-of-k. Learner-cluster bootstrap, 4,000 resamples
(the draw holds many learners; cases from one learner are not independent).

PRE-REGISTERED (committed before the run):
  r at k=9:   R-GAIN if the 95% interval of dr_9 excludes 0 on the positive side; R-EQUIVALENT if the
              90% interval lies inside +/-0.01 (half the Menagerie gain); R-LOSS if the 95% interval
              is below 0; else R-INCONCLUSIVE.
  QWK at k=9: same strings with margin +/-0.02 (the harness resolution the paper uses).
  Reading:   R-GAIN with QWK-EQUIVALENT -> "QWK hid it" replicates on JorGPT and the staged claim's
             title is wrong as written. R-EQUIVALENT -> the staged claim stands for short answers and
             the Menagerie gain is corpus-specific; the claim needs scoping, not reversal.
FLOOR (--floor): synthetic passes on the real draw (teacher mark + case effect + per-pass noise sd 0.6,
the size the 09-16 entry measured, rounded onto 0..10) must return R-GAIN in >= 80% of 200 replicates;
with per-pass noise 0 (nothing to average) it must return R-EQUIVALENT in >= 80%. Smoke check of the
arithmetic, written and scored by the same session.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from analyse import qwk, cluster_index, round_half_up  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
REPS = 4000
M_R, M_QWK = 0.01, 0.02


def r_(h, m):
    return float(np.corrcoef(h, m)[0, 1])


def stats(h, P, idx, k):
    hh, PP = h[idx], P[idx, :k]
    single = {"r": np.mean([r_(hh, PP[:, j]) for j in range(k)]),
              "qwk": np.mean([qwk(hh, PP[:, j]) for j in range(k)]),
              "mae": np.mean([np.abs(PP[:, j] - hh).mean() for j in range(k)])}
    mean_k, med_k = PP.mean(1), np.median(PP, 1)
    return {"d_r": r_(hh, mean_k) - single["r"], "d_qwk": qwk(hh, mean_k) - single["qwk"],
            "d_mae": float(np.abs(mean_k - hh).mean() - single["mae"]),
            "d_r_median": r_(hh, med_k) - single["r"], "d_qwk_median": qwk(hh, med_k) - single["qwk"],
            "r_single": single["r"], "qwk_single": single["qwk"], "mae_single": single["mae"]}


def boot(h, P, learner, k, rng, reps):
    pt = stats(h, P, np.arange(len(h)), k)
    one = np.zeros(len(h), bool)
    dr = [stats(h, P, cluster_index(learner, one, rng), k) for _ in range(reps)]
    return {key: {"est": float(v), "ci95": [float(np.percentile([d[key] for d in dr], 2.5)),
                                            float(np.percentile([d[key] for d in dr], 97.5))],
                  "ci90": [float(np.percentile([d[key] for d in dr], 5)),
                           float(np.percentile([d[key] for d in dr], 95))]} for key, v in pt.items()}


def verdict(e, margin, prefix):
    if -margin < e["ci90"][0] and e["ci90"][1] < margin:
        return f"{prefix}-EQUIVALENT"
    if e["ci95"][0] > 0:
        return f"{prefix}-GAIN"
    if e["ci95"][1] < 0:
        return f"{prefix}-LOSS"
    return f"{prefix}-INCONCLUSIVE"


def floor(draw_path: Path) -> dict:
    rows = json.loads(draw_path.read_text())["rows"]
    h = np.array([r["human"] for r in rows], float)
    learner = np.array([str(r["learnerId"]) for r in rows])
    rng = np.random.default_rng(3)
    res = {}
    for name, sd, want in (("noisy-passes", 0.6, "R-GAIN"), ("no-pass-noise", 0.0, "R-EQUIVALENT")):
        got = []
        for _ in range(200):
            base = h + 0.38 + rng.normal(0, 1.3, len(h))
            P = np.clip(round_half_up(base[:, None] + rng.normal(0, sd, (len(h), 9))), 0, 10)
            got.append(verdict(boot(h, P, learner, 9, rng, 300)["d_r"], M_R, "R"))
        hit = got.count(want) / len(got)
        res[name] = {"expected": want, "hit_rate": hit, "verdicts": {v: got.count(v) for v in set(got)},
                     "pass": hit >= 0.8}
        print(name, res[name])
    return {"pass": all(v["pass"] for v in res.values()), "worlds": res,
            "note": "smoke check on the stratified pooling draw; synthetic passes written and scored by one session"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--floor", type=Path, help="a dry-run draw dump with human grades and learner ids")
    ap.add_argument("--dump", type=Path)
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    if a.floor:
        res = floor(a.floor)
        (OUT / "pooling-floor.json").write_text(json.dumps(res, indent=2) + "\n")
        sys.exit(0 if res["pass"] else 1)
    if not json.loads((OUT / "pooling-floor.json").read_text())["pass"]:
        sys.exit("pooling floor has not passed")
    blob = json.loads(a.dump.read_text())
    rows = [r for r in blob["rows"] if len(r["lite"]) == blob["repeats"]]
    h = np.array([r["human"] for r in rows], float)
    P = np.array([r["lite"] for r in rows], float)
    learner = np.array([str(r["learnerId"]) for r in rows])
    rng = np.random.default_rng(5)
    out = {"models": blob["models"], "run": blob.get("runStamp"), "repeats": blob["repeats"],
           "n_rows": len(blob["rows"]), "n_complete": len(rows), "learners": len(set(learner)),
           "margins": {"r": M_R, "qwk": M_QWK}}
    for k in (3, 9):
        b = boot(h, P, learner, k, rng, REPS)
        out[f"k{k}"] = {"stats": b, "verdict_r": verdict(b["d_r"], M_R, "R"),
                        "verdict_qwk": verdict(b["d_qwk"], M_QWK, "QWK")}
        f = lambda key: f"{b[key]['est']:+.4f} [{b[key]['ci95'][0]:+.4f}, {b[key]['ci95'][1]:+.4f}]"
        print(f"k={k}: r single {b['r_single']['est']:.3f}  dr {f('d_r')} {out[f'k{k}']['verdict_r']}"
              f"  dQWK {f('d_qwk')} {out[f'k{k}']['verdict_qwk']}  dMAE {f('d_mae')}  dr(median) {f('d_r_median')}")
    (OUT / "pooling.json").write_text(json.dumps(out, indent=2) + "\n")


if __name__ == "__main__":
    main()
